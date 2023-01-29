from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core import serializers
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.encoding import smart_str


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from EasyAssistApp.models import CobrowseAgent, CobrowseIO
"""For user authentication"""
from django.contrib.auth import authenticate, login, logout

from EasyChatApp.models import User
from EasyAssistApp.models import *
from EasyAssistApp.utils import *
from EasyAssistApp.views_table import *
from EasyAssistApp.send_email import send_password_over_email, send_meeting_link_over_mail, send_invite_link_over_mail
from DeveloperConsoleApp.utils import *
from DeveloperConsoleApp.utils_aws_s3 import *

import os
import sys
import pytz
import time
import json
import base64
import operator
import logging
import hashlib
import requests
from datetime import datetime, timedelta
import random
import urllib.parse
import threading
from django.conf import settings

from operator import itemgetter
from collections import OrderedDict
from datetime import date

logger = logging.getLogger(__name__)


class GenerateVideoConferencingMeetAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            full_name = strip_html_tags(data["full_name"])
            mobile_number = strip_html_tags(data["mobile_number"])
            meeting_description = strip_html_tags(data["meeting_description"])
            meeting_start_date = strip_html_tags(data["meeting_start_date"])
            meeting_start_time = strip_html_tags(data["meeting_start_time"])
            meeting_end_time = strip_html_tags(data["meeting_end_time"])
            meeting_password = strip_html_tags(data["meeting_password"])
            email_id = strip_html_tags(data["email"])

            user_obj = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)

            meeting_io = CobrowseVideoConferencing.objects.create(full_name=full_name,
                                                                  mobile_number=mobile_number,
                                                                  email_id=email_id,
                                                                  agent=cobrowse_agent,
                                                                  meeting_description=str(
                                                                      meeting_description),
                                                                  meeting_start_date=meeting_start_date,
                                                                  meeting_start_time=meeting_start_time,
                                                                  meeting_end_time=meeting_end_time)
            if meeting_password != "":
                meeting_io.meeting_password = meeting_password
                meeting_io.save()

            meeting_url = str(settings.EASYCHAT_HOST_URL) + "/easy-assist/meeting/" + \
                str(meeting_io.meeting_id)

            agent_name = cobrowse_agent.user.username
            if cobrowse_agent.user.first_name != "":
                agent_name = cobrowse_agent.user.first_name
                if cobrowse_agent.user.last_name != "":
                    agent_name += " " + cobrowse_agent.user.last_name

            start_time = meeting_io.meeting_start_time
            start_time = datetime.strptime(start_time, "%H:%M").time()
            start_time = start_time.strftime("%I:%M %p")
            meeting_date = meeting_io.meeting_start_date
            meeting_date = datetime.strptime(meeting_date, '%Y-%m-%d')
            meeting_date = meeting_date.strftime("%d %B, %Y")
            join_password = ""
            if meeting_password != "":
                join_password = meeting_password
            else:
                join_password = 'No Password Required.'

            thread = threading.Thread(target=send_meeting_link_over_mail, args=(
                email_id, full_name, meeting_url, agent_name, start_time, meeting_date, join_password), daemon=True)
            thread.start()
            response["status"] = 200
            response["message"] = "success"
            response["session_id"] = str(meeting_io.meeting_id)
            response["video_link"] = meeting_url
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GenerateVideoConferencingMeetAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GenerateVideoConferencingMeet = GenerateVideoConferencingMeetAPI.as_view()


class SaveVideoConferencingMeetAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            meeting_id = strip_html_tags(data["meeting_id"])
            meeting_io = CobrowseVideoConferencing.objects.filter(
                meeting_id=meeting_id)

            if meeting_io:
                meeting_io = meeting_io[0]
                full_name = strip_html_tags(data["full_name"])
                mobile_number = strip_html_tags(data["mobile_number"])
                meeting_description = strip_html_tags(
                    data["meeting_description"])
                meeting_start_date = strip_html_tags(
                    data["meeting_start_date"])
                meeting_start_time = strip_html_tags(
                    data["meeting_start_time"])
                meeting_end_time = strip_html_tags(data["meeting_end_time"])
                meeting_password = strip_html_tags(data["meeting_password"])
                email_id = strip_html_tags(data["email"])

                user_obj = User.objects.get(username=request.user.username)
                cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)

                meeting_io.full_name = full_name
                meeting_io.mobile_number = mobile_number
                meeting_io.email_id = email_id
                meeting_io.agent = cobrowse_agent
                meeting_io.meeting_description = str(meeting_description)
                meeting_io.meeting_start_date = meeting_start_date
                meeting_io.meeting_start_time = meeting_start_time
                meeting_io.meeting_end_time = meeting_end_time
                meeting_io.is_expired = False
                meeting_io.meeting_password = meeting_password
                meeting_io.save()

                meeting_url = str(settings.EASYCHAT_HOST_URL) + "/easy-assist/meeting/" + \
                    str(meeting_io.meeting_id)

                agent_name = cobrowse_agent.user.username
                start_time = meeting_io.meeting_start_time
                start_time = datetime.strptime(start_time, "%H:%M").time()
                start_time = start_time.strftime("%I:%M %p")
                meeting_date = meeting_io.meeting_start_date
                join_password = ""
                if meeting_password != "":
                    join_password = meeting_password
                else:
                    join_password = 'No Password Required.'
                thread = threading.Thread(target=send_meeting_link_over_mail, args=(
                    email_id, full_name, meeting_url, agent_name, start_time, meeting_date, join_password), daemon=True)
                thread.start()
                response["status"] = 200
                response["message"] = "success"
            else:
                response["status"] = 301
                response["message"] = "No meeting found."
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveVideoConferencingMeetAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveVideoConferencingMeet = SaveVideoConferencingMeetAPI.as_view()


def CognoVidMeeting(request, meeting_id):
    try:
        is_agent = False
        agent_name = 'Agent'
        client_name = 'Client'
        is_cobrowsing_active = False
        show_cobrowsing_meeting_lobby = True
        allow_meeting_end_time = False
        meeting_end_time = None
        is_invited_agent = False
        reverse_cobrowsing_enabled = False
        invited_agent_username = ""

        meeting_io = CobrowseVideoConferencing.objects.filter(
            meeting_id=meeting_id)
        if meeting_io:
            meeting_io = meeting_io.first()
            meeting_primary_agent = meeting_io.agent
            access_token = meeting_primary_agent.get_access_token_obj()
            reverse_cobrowsing_enabled = access_token.allow_agent_to_customer_cobrowsing

        if reverse_cobrowsing_enabled:
            request_cobrowse_agent = None
            agent_identifier = ""
            if 'is_client' in request.GET:
                is_client = request.GET['is_client']
                if is_client == "true":
                    is_agent = False
                    is_invited_agent = False
                elif is_client == "false":
                    if 'id' in request.GET:
                        agent_identifier = request.GET['id']
                        request_cobrowse_agent = CobrowseAgent.objects.filter(
                            virtual_agent_code=agent_identifier).first()
                        if request_cobrowse_agent:
                            is_invited_agent = True
                            is_agent = False
            else:
                request_cobrowse_agent = meeting_primary_agent
                is_agent = True
                is_invited_agent = False

            if request_cobrowse_agent:
                agent_name = request_cobrowse_agent.name

                if request_cobrowse_agent.user.first_name != '':
                    agent_name = request_cobrowse_agent.user.first_name
                    if request_cobrowse_agent.user.last_name != '':
                        agent_name += " " + request_cobrowse_agent.user.last_name

        else:
            try:
                user_obj = User.objects.get(username=request.user.username)
                request_cobrowse_agent = CobrowseAgent.objects.get(
                    user=user_obj)
                agent_name = request_cobrowse_agent.name

                if request_cobrowse_agent.user.first_name != '':
                    agent_name = request_cobrowse_agent.user.first_name
                    if request_cobrowse_agent.user.last_name != '':
                        agent_name += " " + request_cobrowse_agent.user.last_name

                is_agent = True
            except Exception:
                is_agent = False

            try:
                meeting_io = CobrowseVideoConferencing.objects.get(
                    meeting_id=meeting_id)
                if int(request_cobrowse_agent.pk) != int(meeting_io.agent.pk):
                    is_invited_agent = True
                    is_agent = False
                else:
                    is_invited_agent = False

            except Exception:
                is_invited_agent = False

        if "is_meeting_cobrowsing" in request.GET:
            is_cobrowsing_active = True
            meeting_io = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)
            client_name = meeting_io.full_name
            cobrowse_agent = meeting_io.agent
            access_token_obj = cobrowse_agent.get_access_token_obj()
            meeting_host_url = access_token_obj.meeting_host_url
            cobrowse_logo = access_token_obj.source_easyassist_cobrowse_logo
            meet_background_color = access_token_obj.meet_background_color
            show_cobrowsing_meeting_lobby = access_token_obj.show_cobrowsing_meeting_lobby
            allow_meeting_feedback = access_token_obj.allow_meeting_feedback
            allow_meeting_end_time = access_token_obj.allow_meeting_end_time
            allow_video_meeting_only = access_token_obj.allow_video_meeting_only
            enable_meeting_recording = access_token_obj.enable_meeting_recording
            enable_no_agent_connects_toast_meeting = access_token_obj.enable_no_agent_connects_toast_meeting
            no_agent_connects_meeting_toast_text = access_token_obj.no_agent_connects_meeting_toast_text
            no_agent_connects_meeting_toast_threshold = access_token_obj.no_agent_connects_meeting_toast_threshold
            is_reverse_cobrowsing_enabled = access_token_obj.allow_agent_to_customer_cobrowsing

            if allow_meeting_end_time:
                meeting_end_time = access_token_obj.meeting_end_time

            if meeting_io.is_expired:
                return render(request, "EasyAssistApp/meeting_expired.html", {
                    "logo": cobrowse_logo
                })
            else:
                try:
                    audit_trail = CobrowseVideoAuditTrail.objects.get(
                        cobrowse_video=meeting_io)
                except Exception:
                    audit_trail = CobrowseVideoAuditTrail.objects.create(
                        cobrowse_video=meeting_io)
                if is_invited_agent:
                    audit_trail.meeting_agents.add(request_cobrowse_agent)
                    audit_trail.save()
                    invited_agent_username = request_cobrowse_agent.user.username

                try:
                    if is_agent:
                        cobrowse_agent.is_cognomeet_active = True
                        cobrowse_agent.save()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error CognoVidMeeting is_cognomeet_active status changing %s at %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                jaas_authentication = json.loads(
                    access_token_obj.jaas_authentication)

                is_moderator, jwt_token, api_id = True, "None", "None"
                if "api_id" in jaas_authentication and "api_key" in jaas_authentication:
                    api_id = jaas_authentication["api_id"]
                    api_key = jaas_authentication["api_key"]
                    private_key = access_token_obj.jaas_private_key

                    if is_agent:
                        jwt_token = generate_jaas_jwt_token(cobrowse_agent.agent_name(
                        ), meeting_io.agent.user.email, "", api_key, is_moderator, api_id, private_key)
                    else:
                        jwt_token = generate_jaas_jwt_token(
                            client_name, meeting_io.email_id, "", api_key, is_moderator, api_id, private_key)

                return render(request, "EasyAssistApp/join_meeting.html", {
                    "meeting_io": meeting_io,
                    "meeting_host_url": meeting_host_url,
                    "jitsi_api_id": api_id,
                    "jitsi_jwt": jwt_token,
                    "is_password_required": False,
                    "is_agent": is_agent,
                    "client_name": client_name,
                    "agent_name": agent_name,
                    "unique_id": str(uuid.uuid4()),
                    "is_cobrowsing_active": is_cobrowsing_active,
                    "show_cobrowsing_meeting_lobby": show_cobrowsing_meeting_lobby,
                    "cobrowse_logo": cobrowse_logo,
                    "meet_background_color": meet_background_color,
                    "allow_meeting_feedback": allow_meeting_feedback,
                    "allow_meeting_end_time": allow_meeting_end_time,
                    "meeting_end_time": meeting_end_time,
                    "is_invited_agent": is_invited_agent,
                    "allow_video_meeting_only": allow_video_meeting_only,
                    "cobrowse_agent": cobrowse_agent,
                    "access_token_key": str(access_token_obj.key),
                    "DEVELOPMENT": settings.DEVELOPMENT,
                    "enable_meeting_recording": enable_meeting_recording,
                    "enable_no_agent_connects_toast_meeting": enable_no_agent_connects_toast_meeting,
                    "no_agent_connects_meeting_toast_text": no_agent_connects_meeting_toast_text,
                    "no_agent_connects_meeting_toast_threshold": no_agent_connects_meeting_toast_threshold,
                    "is_reverse_cobrowsing_enabled": is_reverse_cobrowsing_enabled,
                    "invited_agent_username": invited_agent_username,
                    "enable_invite_agent_in_meeting": access_token_obj.enable_invite_agent_in_meeting,
                })

        meeting_io = CobrowseVideoConferencing.objects.filter(
            meeting_id=meeting_id)
        if meeting_io:
            meeting_io = meeting_io[0]
            client_name = meeting_io.full_name
            cobrowse_agent = meeting_io.agent
            access_token_obj = cobrowse_agent.get_access_token_obj()
            meeting_host_url = access_token_obj.meeting_host_url
            cobrowse_logo = access_token_obj.source_easyassist_cobrowse_logo
            meet_background_color = access_token_obj.meet_background_color
            allow_meeting_feedback = access_token_obj.allow_meeting_feedback
            status = check_cogno_meet_status(meeting_io)
            logo = access_token_obj.source_easyassist_cobrowse_logo
            allow_meeting_end_time = access_token_obj.allow_meeting_end_time
            allow_video_meeting_only = access_token_obj.allow_video_meeting_only
            enable_meeting_recording = access_token_obj.enable_meeting_recording
            enable_no_agent_connects_toast_meeting = access_token_obj.enable_no_agent_connects_toast_meeting
            no_agent_connects_meeting_toast_text = access_token_obj.no_agent_connects_meeting_toast_text
            no_agent_connects_meeting_toast_threshold = access_token_obj.no_agent_connects_meeting_toast_threshold
            is_reverse_cobrowsing_enabled = access_token_obj.allow_agent_to_customer_cobrowsing

            if allow_meeting_end_time:
                meeting_end_time = access_token_obj.meeting_end_time

            if meeting_io.is_expired:
                return render(request, "EasyAssistApp/meeting_expired.html", {
                    "logo": logo
                })
            elif status == "waiting":
                meeting_date_time = meeting_io.meeting_start_date.strftime(
                    '%Y-%m-%d') + " " + meeting_io.meeting_start_time.strftime('%H:%M:%S')
                return render(request, "EasyAssistApp/join_meeting.html", {
                    "is_waiting": True,
                    'meeting_date_time': meeting_date_time,
                    "is_cobrowsing_active": is_cobrowsing_active,
                    "cobrowse_logo": cobrowse_logo,
                    "cobrowse_agent": cobrowse_agent,
                    "access_token_key": str(access_token_obj.key),
                    "DEVELOPMENT": settings.DEVELOPMENT,
                    "enable_meeting_recording": enable_meeting_recording,
                    "enable_no_agent_connects_toast_meeting": enable_no_agent_connects_toast_meeting,
                    "no_agent_connects_meeting_toast_text": no_agent_connects_meeting_toast_text,
                    "no_agent_connects_meeting_toast_threshold": no_agent_connects_meeting_toast_threshold,
                    "is_reverse_cobrowsing_enabled": is_reverse_cobrowsing_enabled,
                    "invited_agent_username": invited_agent_username,
                    "enable_invite_agent_in_meeting": access_token_obj.enable_invite_agent_in_meeting,
                })

            else:
                is_password_required = False
                if meeting_io.meeting_password != "" and meeting_io.meeting_password != None:
                    is_password_required = True

                try:
                    audit_trail = CobrowseVideoAuditTrail.objects.get(
                        cobrowse_video=meeting_io)
                except Exception:
                    audit_trail = CobrowseVideoAuditTrail.objects.create(
                        cobrowse_video=meeting_io)

                if is_invited_agent:
                    audit_trail.meeting_agents.add(request_cobrowse_agent)
                    audit_trail.save()
                    invited_agent_username = request_cobrowse_agent.user.username

                if is_agent:
                    cobrowse_agent.is_cognomeet_active = True
                    cobrowse_agent.save()
                    if audit_trail.is_meeting_ended == False:
                        audit_trail.agent_joined = timezone.now()
                        audit_trail.save()
                else:
                    is_agent = False

                jaas_authentication = json.loads(
                    access_token_obj.jaas_authentication)

                is_moderator, jwt_token, api_id = True, "None", "None"
                if "api_id" in jaas_authentication and "api_key" in jaas_authentication:
                    api_id = jaas_authentication["api_id"]
                    api_key = jaas_authentication["api_key"]
                    private_key = access_token_obj.jaas_private_key

                    if is_agent:
                        jwt_token = generate_jaas_jwt_token(cobrowse_agent.agent_name(
                        ), meeting_io.agent.user.email, "", api_key, is_moderator, api_id, private_key)
                    else:
                        jwt_token = generate_jaas_jwt_token(
                            client_name, meeting_io.email_id, "", api_key, is_moderator, api_id, private_key)

                return render(request, "EasyAssistApp/join_meeting.html", {
                    "meeting_io": meeting_io,
                    "meeting_host_url": meeting_host_url,
                    "jitsi_api_id": api_id,
                    "jitsi_jwt": jwt_token,
                    "is_password_required": is_password_required,
                    "is_agent": is_agent,
                    "client_name": client_name,
                    "agent_name": agent_name,
                    "unique_id": str(uuid.uuid4()),
                    "is_cobrowsing_active": is_cobrowsing_active,
                    "show_cobrowsing_meeting_lobby": show_cobrowsing_meeting_lobby,
                    "cobrowse_logo": cobrowse_logo,
                    "meet_background_color": meet_background_color,
                    "allow_meeting_feedback": allow_meeting_feedback,
                    "allow_meeting_end_time": allow_meeting_end_time,
                    "allow_video_meeting_only": allow_video_meeting_only,
                    "meeting_end_time": meeting_end_time,
                    "is_invited_agent": is_invited_agent,
                    "cobrowse_agent": cobrowse_agent,
                    "access_token_key": str(access_token_obj.key),
                    "DEVELOPMENT": settings.DEVELOPMENT,
                    "enable_meeting_recording": enable_meeting_recording,
                    "enable_no_agent_connects_toast_meeting": enable_no_agent_connects_toast_meeting,
                    "no_agent_connects_meeting_toast_text": no_agent_connects_meeting_toast_text,
                    "no_agent_connects_meeting_toast_threshold": no_agent_connects_meeting_toast_threshold,
                    "is_reverse_cobrowsing_enabled": is_reverse_cobrowsing_enabled,
                    "invited_agent_username": invited_agent_username,
                    "enable_invite_agent_in_meeting": access_token_obj.enable_invite_agent_in_meeting,
                })

        else:
            return HttpResponse(status=404)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CognoVidMeeting %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)


def CognoVidMeetingEnded(request, meeting_id):
    try:
        try:
            user_obj = User.objects.get(username=request.user.username)
            request_cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
            is_agent = True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning("Error CognoVidMeetingEnded find user %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            is_agent = False

        is_cognomeet_active = False
        is_feedback = False
        socket_type = None
        agent_disconnected_meet = False

        message = "You left the meeting."
        if "is_meeting_cobrowsing" in request.GET:
            is_cognomeet_active = True
        
        if "is_feedback" in request.GET:
            if request.GET["is_feedback"] == 'true':
                is_feedback = True
        
        if "agent_disconnected_meet" in request.GET and request.GET["agent_disconnected_meet"] == "true":
            agent_disconnected_meet = True
        
        if 'type' in request.GET:
            socket_type = request.GET["type"]
        if agent_disconnected_meet:
            message = "Agent has left the meeting."
        if socket_type == "1":
            message = "You have been removed from the meeting."
        
        meeting_io = CobrowseVideoConferencing.objects.get(
            meeting_id=meeting_id)

        if meeting_io.meeting_end_time == None:
            meeting_io.meeting_end_time = datetime.now()
            meeting_io.save()

        cobrowse_agent = meeting_io.agent
        access_token_obj = cobrowse_agent.get_access_token_obj()
        cobrowse_logo = access_token_obj.source_easyassist_cobrowse_logo

        try:
            if is_agent:
                request_cobrowse_agent.is_cognomeet_active = False
                request_cobrowse_agent.save()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoVidMeetingEnded is_cognomeet_active status changing %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return render(request, "EasyAssistApp/meeting_end.html", {
            "meeting_id": meeting_id,
            "is_cognomeet_active": is_cognomeet_active,
            "is_feedback": is_feedback,
            "cobrowse_logo": cobrowse_logo,
            "cobrowse_agent": cobrowse_agent,
            "access_token_key": str(access_token_obj.key),
            "message": message,
            "DEVELOPMENT": settings.DEVELOPMENT
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CognoVidMeetingEnded %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)


def CognoVidMeetingScheduled(request):
    try:
        user_obj = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
        current_date = datetime.now().date()
        meeting_objs = CobrowseVideoConferencing.objects.filter(
            agent=cobrowse_agent, meeting_start_date=current_date).order_by('-meeting_start_time')
        return render(request, "EasyAssistApp/scheduled_meetings.html", {
            "meeting_objs": meeting_objs,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CognoVidMeetingEnded %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)


def CobrowseVideoConferencingDataCollect(request, meeting_id, form_id):
    try:
        meeting_io = CobrowseVideoConferencing.objects.get(
            meeting_id=meeting_id, is_expired=False)

        cobrowse_form_obj = CobrowseVideoConferencingForm.objects.filter(
            pk=form_id, is_deleted=False)

        if cobrowse_form_obj:
            cobrowse_form_obj = cobrowse_form_obj[0]
            cobrowse_form_category_objs = CobrowseVideoconferencingFormCategory.objects.filter(
                form=cobrowse_form_obj, is_deleted=False).order_by('pk')

            cobrowse_form_element_objs = CobrowseVideoConferencingFormElement.objects.filter(
                form_category__in=cobrowse_form_category_objs, is_deleted=False).order_by('pk')

            cobrowse_form_elements = []
            for form_element in cobrowse_form_element_objs:
                collected_form_data_obj = CobrowseVideoConferencingFormData.objects.filter(
                    cobrowse_video=meeting_io, form_element=form_element)

                collected_data = []
                if collected_form_data_obj:
                    collected_data = collected_form_data_obj[
                        0].get_collected_values()

                cobrowse_form_elements.append({
                    'pk': form_element.pk,
                    'element_type': form_element.element_type,
                    'element_label': form_element.element_label,
                    'element_choices': form_element.get_element_choices(),
                    'is_mandatory': form_element.is_mandatory,
                    'form_category': form_element.form_category,
                    'collected_data': collected_data,
                })

            return render(request, "EasyAssistApp/cobrowse_data_collect_form.html", {
                "cobrowse_agent": meeting_io.agent,
                "cobrowse_form_obj": cobrowse_form_obj,
                'cobrowse_form_categories': cobrowse_form_category_objs,
                "cobrowse_form_elements": cobrowse_form_elements,
                "meeting_id": meeting_id,
                "is_agent": True,
            })
        else:
            return HttpResponse("Form does not exist")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowseVideoConferencingDataCollect %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)


def ShowCobrowseDataCollectForm(request, meeting_id, form_id):
    try:
        meeting_io = CobrowseVideoConferencing.objects.get(
            meeting_id=meeting_id)

        cobrowse_form_obj = CobrowseVideoConferencingForm.objects.filter(
            pk=form_id, is_deleted=False)

        if cobrowse_form_obj:
            cobrowse_form_obj = cobrowse_form_obj[0]
            cobrowse_form_category_objs = CobrowseVideoconferencingFormCategory.objects.filter(
                form=cobrowse_form_obj, is_deleted=False).order_by('pk')

            cobrowse_form_element_objs = CobrowseVideoConferencingFormElement.objects.filter(
                form_category__in=cobrowse_form_category_objs, is_deleted=False).order_by('pk')

            cobrowse_form_elements = []
            for form_element in cobrowse_form_element_objs:
                collected_form_data_obj = CobrowseVideoConferencingFormData.objects.filter(
                    cobrowse_video=meeting_io, form_element=form_element)

                collected_data = []
                if collected_form_data_obj:
                    collected_data = collected_form_data_obj[
                        0].get_collected_values()

                cobrowse_form_elements.append({
                    'pk': form_element.pk,
                    'element_type': form_element.element_type,
                    'element_label': form_element.element_label,
                    'element_choices': form_element.get_element_choices(),
                    'is_mandatory': form_element.is_mandatory,
                    'form_category': form_element.form_category,
                    'collected_data': collected_data,
                })

            return render(request, "EasyAssistApp/cobrowse_data_collect_form.html", {
                "cobrowse_agent": meeting_io.agent,
                "cobrowse_form_obj": cobrowse_form_obj,
                'cobrowse_form_categories': cobrowse_form_category_objs,
                "cobrowse_form_elements": cobrowse_form_elements,
                "meeting_id": meeting_id,
                "is_readonly": True,
            })
        else:
            return HttpResponse("Form does not exist")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ShowCobrowseDataCollectForm %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)


class SaveCobrowseCollectedFormDataAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            meeting_id = remo_html_from_string(data["meeting_id"])
            form_id = remo_html_from_string(data["form_id"])
            category_id = remo_html_from_string(data["category_id"])
            collected_data = data["collected_data"]

            meeting_io = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id, is_expired=False)

            cobrowse_form_obj = CobrowseVideoConferencingForm.objects.filter(
                pk=form_id, is_deleted=False)

            if cobrowse_form_obj:
                cobrowse_form_obj = cobrowse_form_obj[0]

                meeting_audit_trail = CobrowseVideoAuditTrail.objects.filter(
                    cobrowse_video=meeting_io)

                if meeting_audit_trail:
                    meeting_audit_trail = meeting_audit_trail[0]
                    meeting_audit_trail.cobrowse_forms.add(cobrowse_form_obj)
                    meeting_audit_trail.save()

                for data in collected_data:
                    data_value = remo_html_from_string(data['value'])
                    data_value = remo_special_tag_from_string(data_value)
                    collected_values = [{
                        "value": data_value
                    }]

                    try:
                        cobrowse_form_category_obj = CobrowseVideoconferencingFormCategory.objects.get(
                            pk=category_id, form=cobrowse_form_obj, is_deleted=False)

                        form_element_obj = CobrowseVideoConferencingFormElement.objects.get(
                            pk=data['id'], form_category=cobrowse_form_category_obj, is_deleted=False)

                        try:
                            collected_form_data_obj = CobrowseVideoConferencingFormData.objects.get(
                                cobrowse_video=meeting_io, form_element=form_element_obj)
                            collected_form_data_obj.collected_values = json.dumps(
                                collected_values)
                            collected_form_data_obj.save()
                        except Exception:
                            CobrowseVideoConferencingFormData.objects.create(
                                cobrowse_video=meeting_io,
                                form_element=form_element_obj,
                                collected_values=json.dumps(collected_values))
                    except Exception:
                        logger.warning("Invalid cobrowse form element", extra={
                                       'AppName': 'EasyAssist'})

                response["status"] = 200
            else:
                response["status"] = 300
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowseCollectedFormDataAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowseCollectedFormData = SaveCobrowseCollectedFormDataAPI.as_view()


class GetCognoVidScheduledMeetingsListAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            user_obj = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
            current_date = datetime.now().date()
            meeting_objs = CobrowseVideoConferencing.objects.filter(
                agent=cobrowse_agent, meeting_start_date=current_date).order_by('-meeting_start_time')

            meeting_list = []
            for meeting_obj in meeting_objs:
                meeting_start_date = meeting_obj.meeting_start_date
                meeting_start_time = meeting_obj.meeting_start_time
                meeting_end_time = meeting_obj.meeting_end_time

                if meeting_start_date:
                    meeting_start_date = meeting_start_date.strftime(
                        "%b %d, %Y")

                if meeting_start_time:
                    meeting_start_time = meeting_start_time.strftime(
                        "%-I:%M %p")

                if meeting_end_time:
                    meeting_end_time = meeting_end_time.strftime("%-I:%M %p")

                meeting_list.append({
                    'id': str(meeting_obj.pk),
                    "description": meeting_obj.meeting_description,
                    "start_date": meeting_start_date,
                    "start_time": meeting_start_time,
                    "end_time": meeting_end_time,
                    "is_expired": meeting_obj.is_expired,
                })

            response["status"] = 200
            response["message"] = "success"
            response["meeting_list"] = meeting_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCognoVidScheduledMeetingsList %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCognoVidScheduledMeetingsList = GetCognoVidScheduledMeetingsListAPI.as_view()


class DownloadMeetingRecordingAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            meeting_id = data["meeting_id"]
            audit_trail_obj = CobrowseVideoAuditTrail.objects.filter(
                cobrowse_video__meeting_id=meeting_id).first()

            if audit_trail_obj and audit_trail_obj.merged_filepath:
                response["status"] = 200
                response["message"] = "success"
                response["file_id"] = str(audit_trail_obj.merged_filepath)

            else:
                search_name = meeting_id
                folder_name = ""
                file_name = ""

                if not os.path.exists(EASYASSISTAPP_COGNOVID_FILES_PATH):
                    os.makedirs(EASYASSISTAPP_COGNOVID_FILES_PATH)

                if not os.path.exists('secured_files/EasyAssistApp/cognovid/nfs_recordings'):
                    os.makedirs(
                        'secured_files/EasyAssistApp/cognovid/nfs_recordings')

                with os.scandir(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/cognovid/nfs_recordings/') as entries:
                    for entry in entries:
                        try:
                            files_inside = os.listdir(entry)
                            folder_name = entry.name
                            for file_path_name in files_inside:
                                if search_name in file_path_name:
                                    file_name = file_path_name
                                    break
                            if file_name:
                                break
                        except Exception:
                            pass
                if file_name:
                    file_path = '/secured_files/EasyAssistApp/cognovid/nfs_recordings/' + \
                        folder_name + "/" + file_name

                    if get_save_in_s3_bucket_status():
                        s3_bucket_upload_file_by_file_path(
                            file_path[1:], file_name)

                    file_access_management_obj = CobrowsingFileAccessManagement.objects.filter(
                        file_path=file_path, is_public=False)
                    if not file_access_management_obj:
                        active_agent = get_active_agent_obj(request, CobrowseAgent)
                        file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                            file_path=file_path, is_public=False, access_token=active_agent.get_access_token_obj())
                    response["status"] = 200
                    response["message"] = "success"
                    response["file_id"] = str(
                        file_access_management_obj[0].key)
                else:
                    response["status"] = 301
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCognoVidScheduledMeetingsList %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DownloadMeetingRecording = DownloadMeetingRecordingAPI.as_view()


class CognoVidAuthenticatePasswordAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            meeting_id = data["meeting_id"]
            password = data["password"]

            meeting_id = remo_html_from_string(meeting_id)
            password = remo_html_from_string(password)

            meeting_obj = CobrowseVideoConferencing.objects.filter(
                meeting_id=meeting_id, is_expired=False)
            if meeting_obj:
                if str(meeting_obj[0].meeting_password) == str(password):
                    response["status"] = 200
                    response["message"] = "success"
                else:
                    response["status"] = 301
                    response[
                        "message"] = "Password is incorrect. Please check and try again."
            else:
                response["status"] = 401
                response[
                    "message"] = "The requested meeting is either completed or does not exist."
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoVidAuthenticatePasswordAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoVidAuthenticatePassword = CognoVidAuthenticatePasswordAPI.as_view()


class CognoVidMeetingDurationAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            meeting_id = data["meeting_id"]
            meeting_id = remo_html_from_string(meeting_id)

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)

            cobrowse_agent = meeting_obj.agent
            cobrowse_agent.is_cognomeet_active = False
            cobrowse_agent.save()
            meeting_audit_trail = CobrowseVideoAuditTrail.objects.filter(
                cobrowse_video=meeting_obj)
            if meeting_audit_trail:
                meeting_audit_trail[0].meeting_ended = timezone.now()
                meeting_audit_trail[0].is_meeting_ended = True
                meeting_audit_trail[0].save()
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoVidMeetingDuration %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoVidMeetingDuration = CognoVidMeetingDurationAPI.as_view()


class CognoVidMeetingNotesAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            meeting_id = data["meeting_id"]
            notes = data["notes"]

            meeting_id = remo_html_from_string(meeting_id)
            notes = remo_html_from_string(notes)
            notes = remo_special_tag_from_string(notes)

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)
            meeting_audit_trail = CobrowseVideoAuditTrail.objects.filter(
                cobrowse_video=meeting_obj)
            if meeting_audit_trail:
                meeting_audit_trail[0].agent_notes = str(notes)
                meeting_audit_trail[0].save()
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoVidMeetingNotesAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoVidMeetingNotes = CognoVidMeetingNotesAPI.as_view()


class CognoVidMeetingChatsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            meeting_id = data["meeting_id"]
            message_history = []

            for message_obj in data["chat_history"]:
                message_obj = json.loads(message_obj)
                if message_obj["type"] == 'attachment':
                    message_obj['message'] = remo_special_tag_from_string(
                        message_obj['message'])
                    message_obj["message"] = remo_unwanted_security_characters(message_obj['message'])
                    url = str(settings.EASYCHAT_HOST_URL) + \
                        message_obj["message"]
                    if not is_url_valid(url):
                        response["status"] = 507
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(
                            response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)
                    message_obj["message"] = '<a href=' + \
                        message_obj["message"] + \
                        ' download>File Attachment</a>'
                else:
                    message_obj['message'] = sanitize_input_string(
                        message_obj['message'])

                message_obj = json.dumps(message_obj)
                message_history.append(message_obj)

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)
            meeting_audit_trail = CobrowseVideoAuditTrail.objects.filter(
                cobrowse_video=meeting_obj)
            if meeting_audit_trail:
                meeting_audit_trail[0].message_history = message_history
                meeting_audit_trail[0].save()
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoVidMeetingChatsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoVidMeetingChats = CognoVidMeetingChatsAPI.as_view()


def CognoVidAuditTrail(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        user_obj = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
        access_token_obj = cobrowse_agent.get_access_token_obj()

        agents = []
        supervisor_objs = []
        if cobrowse_agent.role == "agent":
            agents = [cobrowse_agent]
        elif cobrowse_agent.role == "supervisor":
            agents = list(cobrowse_agent.agents.all()) + [cobrowse_agent]
        else:
            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None, is_account_active=None)
            supervisor_objs = cobrowse_agent.agents.filter(role="supervisor")

        cobrowse_video_objs = CobrowseVideoConferencing.objects.filter(
            agent__in=agents)

        # TODO:admint ally case
        # list of agent under current cobrowse_agent
        agents_list = []
        support_history_filters = {}
        for agent in agents:
            agents_list.append(agent.user.username)

        if cobrowse_agent.role in ["agent", "supervisor"] and (access_token_obj.enable_invite_agent_in_meeting or access_token_obj.enable_invite_agent_in_cobrowsing):
            invited_agent_video_audit_objs = CobrowseVideoAuditTrail.objects.filter(
                meeting_agents__in=agents)
            if invited_agent_video_audit_objs:
                invited_session_ids = []
                for invited_agent_video_audit_obj in invited_agent_video_audit_objs:
                    invited_session_ids.append(
                        invited_agent_video_audit_obj.cobrowse_video.meeting_id)
                invited_sessions_cobrowse_objs = CobrowseVideoConferencing.objects.filter(
                    meeting_id__in=invited_session_ids)
                cobrowse_video_objs = cobrowse_video_objs | invited_sessions_cobrowse_objs

        is_cobrowse_video_empty = False
        if cobrowse_video_objs.count() == 0:
            is_cobrowse_video_empty = True

        if "startdate" in request.GET:
            date_format = "%d-%m-%Y"
            start_date = request.GET.getlist("startdate")[0]
            support_history_filters["startdate"] = str(start_date)
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.strptime(
                start_date, date_format).date()

            cobrowse_video_objs = cobrowse_video_objs.filter(
                meeting_start_date__gte=datetime_start)

        if "enddate" in request.GET:
            date_format = "%d-%m-%Y"
            end_date = request.GET.getlist("enddate")[0]
            support_history_filters["enddate"] = str(end_date)
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.strptime(
                end_date, date_format).date()
            cobrowse_video_objs = cobrowse_video_objs.filter(
                meeting_start_date__lte=datetime_end)

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")
            support_history_filters["agent"] = agent_email
            selected_agents = CobrowseAgent.objects.filter(
                user__username__in=agent_email)

            cobrowse_video_objs = cobrowse_video_objs.filter(
                agent__in=selected_agents)

        if "supervisor" in request.GET:
            supervisor_email_id_list = request.GET.getlist("supervisor")
            selected_agents = []
            for agent_email_id in supervisor_email_id_list:
                selected_supervisor = cobrowse_agent.agents.filter(
                    user__username=agent_email_id).first()
                selected_agents += list(selected_supervisor.agents.all())
            support_history_filters["supervisor"] = supervisor_email_id_list
            cobrowse_video_objs = cobrowse_video_objs.filter(
                agent__in=selected_agents)

        if "status" in request.GET:
            meeting_status = request.GET.getlist("status")[0]
            meeting_status = remo_html_from_string(meeting_status)
            support_history_filters["status"] = meeting_status
            if meeting_status == "Completed":
                cobrowse_video_objs = cobrowse_video_objs.filter(
                    is_expired=True)
            elif meeting_status == "Scheduled":
                cobrowse_video_objs = cobrowse_video_objs.filter(
                    is_expired=False)

        if "meeting_id" in request.GET:
            meeting_id = request.GET.getlist("meeting_id")[0]
            meeting_id = remo_html_from_string(meeting_id)
            support_history_filters["meeting_id"] = str(meeting_id)
            cobrowse_video_objs = cobrowse_video_objs.filter(
                meeting_id=meeting_id)

        audit_trail_objs = CobrowseVideoAuditTrail.objects.filter(
            cobrowse_video__in=cobrowse_video_objs).order_by('-pk')

        total_rows_per_pages = 20
        total_audit_trail_objs = len(audit_trail_objs)
        paginator = Paginator(
            audit_trail_objs, total_rows_per_pages)
        page = request.GET.get('page')

        try:
            audit_trail_objs = paginator.page(page)
        except PageNotAnInteger:
            audit_trail_objs = paginator.page(1)
        except EmptyPage:
            audit_trail_objs = paginator.page(paginator.num_pages)

        if page != None:
            start_point = total_rows_per_pages * (int(page) - 1) + 1
            end_point = min(total_rows_per_pages * int(page),
                            total_audit_trail_objs)
            if start_point > end_point:
                start_point = max(end_point - len(audit_trail_objs) + 1, 1)
        else:
            start_point = 1
            end_point = min(total_rows_per_pages, total_audit_trail_objs)
        
        if not access_token_obj.enable_cognomeet:
            return render(request, "EasyAssistApp/meeting_audit_trail.html", {
                "audit_trail_objs": audit_trail_objs,
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "agents": agents,
                "start_point": start_point,
                "end_point": end_point,
                "total_audit_trail_objs": total_audit_trail_objs,
                "is_cobrowse_video_empty": is_cobrowse_video_empty,
                "supervisors": supervisor_objs,
                "invite_agent_in_meeting": access_token_obj.enable_invite_agent_in_meeting
            })
        else:
            return render(request, "EasyAssistApp/meeting_audit_trail_dyte.html", {
                "audit_trail_objs": audit_trail_objs,
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "agents": agents,
                "start_point": start_point,
                "end_point": end_point,
                "total_audit_trail_objs": total_audit_trail_objs,
                "is_cobrowse_video_empty": is_cobrowse_video_empty,
                "supervisors": supervisor_objs,
                "invite_agent_in_meeting": access_token_obj.enable_invite_agent_in_meeting,
                "agents_list": agents_list,
                "support_history_filters": support_history_filters,
                "enable_meeting_recording": access_token_obj.enable_meeting_recording            
            })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CognoVidAuditTrail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)


class CognoVidGetClientAgentChatAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            meeting_id = data["meeting_id"]

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)

            meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
                cobrowse_video=meeting_obj)

            client_agent_chats = []
            message_history = eval(meeting_audit_trail.message_history)
            for message in message_history:
                message = json.loads(message)
                if "sender_name" in message:
                    client_agent_chats.append({
                        "sender": message["sender"],
                        "sender_name": message["sender_name"],
                        "message": get_masked_data_if_hashed(message["message"]),
                        "time": message["time"],
                        "type": message["type"],
                    })
                else:
                    client_agent_chats.append({
                        "sender": message["sender"],
                        "sender_name": message["sender"],
                        "message": get_masked_data_if_hashed(message["message"]),
                        "time": message["time"],
                        "type": message["type"],
                    })
            response['status'] = 200
            response["message_history"] = client_agent_chats

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoVidGetClientAgentChatAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response['status'] = 301
            response["message_history"] = []

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoVidGetClientAgentChat = CognoVidGetClientAgentChatAPI.as_view()


class SaveScreenRecordedDataAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            uploaded_file = data["uploaded_data"]
            filename = data["filename"]
            meeting_id = data["meeting_id"]
            is_first_packet = data["is_first_packet"]
            filename = meeting_id + ".webm"

            if not os.path.exists(EASYASSISTAPP_COGNOVID_FILES_PATH):
                os.makedirs(EASYASSISTAPP_COGNOVID_FILES_PATH)

            file_path = EASYASSISTAPP_COGNOVID_FILES_PATH + "/" + filename

            if get_save_in_s3_bucket_status():
                s3_bucket_upload_file_by_file_path(file_path, filename)

            media_file = open(file_path, "ab+")
            media_file.write(uploaded_file.read())
            media_file.close()

            file_path = "/" + file_path

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)
            access_token_obj = meeting_obj.agent.get_access_token_obj()

            try:
                file_access_management_obj = CobrowsingFileAccessManagement.objects.get(
                    file_path=file_path, is_public=False)
            except Exception:
                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=file_path, is_public=False, access_token=access_token_obj)

            meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
                cobrowse_video=meeting_obj)
            if (is_first_packet == 'true' or is_first_packet == True) and (meeting_audit_trail.meeting_recording == '' or meeting_audit_trail.meeting_recording == None):
                logger.info(timezone.now(), extra={'AppName': 'EasyAssist'})
                meeting_audit_trail.agent_recording_start_time = timezone.now()

            meeting_audit_trail.meeting_recording = str(
                file_access_management_obj.pk)
            meeting_audit_trail.save()

            response["status"] = 200

            response["name"] = filename
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveScreenRecordedDataAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status"] = 500
            response["name"] = "no_name"

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveScreenRecordedData = SaveScreenRecordedDataAPI.as_view()


class SaveAgentRecordedDataAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            uploaded_file = data["uploaded_data"]
            filename = data["filename"]
            meeting_id = data["meeting_id"]
            is_first_packet = data["is_first_packet"]
            filename = meeting_id + ".webm"

            if not os.path.exists(EASYASSISTAPP_COGNOVID_FILES_PATH):
                os.makedirs(EASYASSISTAPP_COGNOVID_FILES_PATH)

            file_path = EASYASSISTAPP_COGNOVID_FILES_PATH + "/" + filename
            if get_save_in_s3_bucket_status():
                s3_bucket_upload_file_by_file_path(file_path, filename)

            media_file = open(file_path, "ab+")
            media_file.write(uploaded_file.read())
            media_file.close()

            file_path = "/" + file_path

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)

            access_token_obj = meeting_obj.agent.get_access_token_obj()

            try:
                file_access_management_obj = CobrowsingFileAccessManagement.objects.get(
                    file_path=file_path, is_public=False)
            except Exception:
                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=file_path, is_public=False, access_token=access_token_obj)

            meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
                cobrowse_video=meeting_obj)
            if (is_first_packet == 'true' or is_first_packet == True) and (meeting_audit_trail.meeting_recording == '' or meeting_audit_trail.meeting_recording == None):
                logger.info(timezone.now(), extra={'AppName': 'EasyAssist'})
                meeting_audit_trail.agent_recording_start_time = timezone.now()

            meeting_audit_trail.meeting_recording = str(
                file_access_management_obj.pk)
            meeting_audit_trail.save()

            response["status"] = 200

            response["name"] = filename
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveAgentRecordedDataAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status"] = 500
            response["name"] = "no_name"

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveAgentRecordedData = SaveAgentRecordedDataAPI.as_view()


class SaveClientRecordedDataAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            uploaded_file = data["uploaded_data"]
            filename = data["filename"]
            meeting_id = data["meeting_id"]
            time_stamp = data["time_stamp"]
            filename = remo_html_from_string(filename)
            meeting_id = remo_html_from_string(meeting_id)

            if not os.path.exists(EASYASSISTAPP_COGNOVID_FILES_PATH):
                os.makedirs(EASYASSISTAPP_COGNOVID_FILES_PATH)

            file_path = EASYASSISTAPP_COGNOVID_FILES_PATH + "/" + filename
            if get_save_in_s3_bucket_status():
                s3_bucket_upload_file_by_file_path(file_path, filename)

            media_file = open(file_path, "ab+")
            media_file.write(uploaded_file.read())
            media_file.close()

            file_path = "/" + file_path

            is_recording_present = False

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)
            access_token_obj = meeting_obj.agent.get_access_token_obj()

            if(CobrowsingFileAccessManagement.objects.filter(file_path=file_path, is_public=False).count() > 0):
                is_recording_present = True
            else:
                CobrowsingFileAccessManagement.objects.create(
                    file_path=file_path, is_public=False, access_token=access_token_obj)

            meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
                cobrowse_video=meeting_obj)

            client_audio_file = json.loads(
                meeting_audit_trail.client_audio_recording)

            if is_recording_present:
                logger.info("File already present in the list",
                            extra={'AppName': 'EasyAssist'})
            else:
                client_audio_file["items"].append(
                    {"time_stamp": str(time_stamp), "path": str(file_path)})
                meeting_audit_trail.client_audio_recording = json.dumps(
                    client_audio_file)
                meeting_audit_trail.save()
            response["status"] = 200
            response["name"] = filename
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveClientRecordedDataAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status"] = 500
            response["name"] = "no_name"
            response["src"] = "error"

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveClientRecordedData = SaveClientRecordedDataAPI.as_view()


class GetVoipMeetingStatusAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            meeting_id = data["meeting_id"]
            meeting_id = remo_html_from_string(meeting_id)

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            is_session_closed = False
            cobrowse_io_objs = CobrowseIO.objects.filter(session_id=meeting_id)
            if cobrowse_io_objs:
                cobrowse_io = cobrowse_io_objs[0]
                is_session_closed = cobrowse_io.is_archived
                if not cobrowse_io.is_archived:
                    if active_agent and active_agent not in cobrowse_io.support_agents.all() and active_agent != cobrowse_io.agent:
                        is_session_closed = True

            response["status"] = 200
            response["is_session_closed"] = is_session_closed
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside GetVoipMeetingStatusAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status"] = 500

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetVoipMeetingStatus = GetVoipMeetingStatusAPI.as_view()


class SaveClientLocationDetailsAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            meeting_id = data["meeting_id"]
            client_name = data["client_name"]
            longitude = data["longitude"]
            latitude = data["latitude"]
            client_address = data["client_address"]

            meeting_id = remo_html_from_string(meeting_id)
            client_name = remo_html_from_string(client_name)
            client_name = remo_special_tag_from_string(client_name)
            longitude = remo_html_from_string(str(longitude))
            latitude = remo_html_from_string(str(latitude))
            client_address = remo_html_from_string(client_address)
            client_address = remo_special_tag_from_string(client_address)

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)

            meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
                cobrowse_video=meeting_obj)

            client_location_details = json.loads(
                meeting_audit_trail.client_location_details)

            client_location_details["items"].append({
                "client_name": client_name,
                "longitude": str(longitude),
                "latitude": str(latitude),
                "address": client_address,
            })
            meeting_audit_trail.client_location_details = json.dumps(
                client_location_details)
            meeting_audit_trail.save()

            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveClientLocationDetailsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status"] = 500

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveClientLocationDetails = SaveClientLocationDetailsAPI.as_view()


class SaveCognoMeetScreenshotAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            content = data["content"]
            meeting_id = data["meeting_id"]
            meeting_id = remo_html_from_string(meeting_id)

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)

            access_token_obj = meeting_obj.agent.get_access_token_obj()
            meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
                cobrowse_video=meeting_obj)

            meeting_screenshot = json.loads(
                meeting_audit_trail.meeting_screenshot)

            format, imgstr = content.split(';base64,')
            ext = format.split('/')[-1]
            image_name = str(int(uuid.uuid4())) + "." + str(ext)

            if not os.path.exists(EASYASSISTAPP_COGNOVID_FILES_PATH):
                os.makedirs(EASYASSISTAPP_COGNOVID_FILES_PATH)

            file_path = EASYASSISTAPP_COGNOVID_FILES_PATH + "/" + image_name
            if get_save_in_s3_bucket_status():
                s3_bucket_upload_file_by_file_path(file_path, image_name)

            fh = open(file_path, "wb")
            fh.write(base64.b64decode(imgstr))
            fh.close()

            file_path = "/" + file_path

            file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                file_path=file_path, is_public=False, access_token=access_token_obj)

            src = str(file_access_management_obj.key)

            meeting_screenshot["items"].append({
                "screenshot": src,
            })

            meeting_audit_trail.meeting_screenshot = json.dumps(
                meeting_screenshot)
            meeting_audit_trail.save()

            response["status"] = 200
            response["message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCognoMeetScreenshotAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCognoMeetScreenshot = SaveCognoMeetScreenshotAPI.as_view()


class UploadCognoVidFileAttachmentAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            filename = strip_html_tags(data["filename"])
            filename = remo_html_from_string(filename)
            base64_data = strip_html_tags(data["base64_file"])
            meeting_id = data["meeting_id"]
            meeting_id = remo_html_from_string(strip_html_tags(meeting_id))

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)

            access_token_obj = meeting_obj.agent.get_access_token_obj()

            file_extention = filename.replace(" ", "").split(".")[-1]
            file_extention = file_extention.lower()

            allowed_files_list = ["png", "jpg",
                                  "jpeg", "jpe", "pdf", "doc", "docx"]

            if file_extention not in allowed_files_list or check_malicious_file_from_filename(filename, allowed_files_list) or check_malicious_file_from_content(base64_data, allowed_files_list):
                response["status"] = 302
            else:
                if not os.path.exists(EASYASSISTAPP_COGNOVID_FILES_PATH):
                    os.makedirs(EASYASSISTAPP_COGNOVID_FILES_PATH)

                file_path = EASYASSISTAPP_COGNOVID_FILES_PATH + "/" + filename

                fh = open(file_path, "wb")
                fh.write(base64.b64decode(base64_data))
                fh.close()

                if get_save_in_s3_bucket_status():
                    key = s3_bucket_upload_file_by_file_path(
                        file_path, filename)
                    s3_file_path = s3_bucket_download_file(
                        key, 'EasyAssistApp/cognovid/', file_extention)
                    file_path = s3_file_path.split("EasyChat/", 1)[1]

                file_path = "/" + file_path

                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=file_path, is_public=False, access_token=access_token_obj)

                src = "/easy-assist/download-file/" + \
                    str(file_access_management_obj.key)
                response["status"] = 200
                response["src"] = src
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside UploadCognoVidFileAttachmentAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status"] = 500
            response["name"] = "no_name"
            response["src"] = "error"

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadCognoVidFileAttachment = UploadCognoVidFileAttachmentAPI.as_view()


class GetListOfMeetSuportAgentsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["id"])
            primary_agent_username = None

            if 'primary_agent_username' in data:
                primary_agent_username = strip_html_tags(data["primary_agent_username"])
                primary_agent_username = remo_html_from_string(primary_agent_username)

            if not primary_agent_username:
                cobrowse_meeting_obj = CobrowseVideoConferencing.objects.get(
                    meeting_id=id)
                active_agent = cobrowse_meeting_obj.agent
            else:
                easy_chat_user = User.objects.get(username=primary_agent_username)
                active_agent = CobrowseAgent.objects.filter(
                    user=easy_chat_user).first()

            agent_admin = get_admin_from_active_agent(
                active_agent, CobrowseAgent)

            agents = get_list_agents_under_admin(agent_admin, is_active=True)

            product_categories = agent_admin.product_category.filter(
                is_deleted=False).order_by('index')
            product_category_wise_agent_list = dict()

            for product_category in product_categories:
                product_category_wise_agent_list[product_category.title] = []

                for agent in agents:
                    if agent.user.username != request.user.username:
                        if agent.product_category.filter(pk=product_category.pk).count():
                            product_category_wise_agent_list[product_category.title].append({
                                "id": agent.user.pk,
                                "username": agent.user.username,
                                "level": agent.support_level
                            })

            for agent in agents:
                if agent.user.username != request.user.username:
                    if agent.product_category.filter(is_deleted=False).count() == 0:
                        if "Others" not in product_category_wise_agent_list:
                            product_category_wise_agent_list["Others"] = []
                        product_category_wise_agent_list["Others"].append({
                            "id": agent.user.pk,
                            "username": agent.user.username,
                            "level": agent.support_level
                        })

            response["status"] = 200
            response["message"] = "success"
            response["support_agents"] = product_category_wise_agent_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetListOfMeetSuportAgentsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)

GetListOfMeetSuportAgents = GetListOfMeetSuportAgentsAPI.as_view()


class GetListOfMeetingFormsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["id"])

            cobrowse_meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=id)

            agent_admin = cobrowse_meeting_obj.agent
            cobrowsing_form_objs = CobrowseVideoConferencingForm.objects.filter(
                is_deleted=False, agents__in=[agent_admin]).distinct()

            cobrowsing_form_obj_list = []
            for cobrowsing_form_obj in cobrowsing_form_objs:
                cobrowsing_form_obj_list.append({
                    'id': cobrowsing_form_obj.pk,
                    'name': cobrowsing_form_obj.form_name,
                })

            response["status"] = 200
            response["message"] = "success"
            response["meeting_forms"] = cobrowsing_form_obj_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetListOfMeetingFormsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetListOfMeetingForms = GetListOfMeetingFormsAPI.as_view()


class GetListOfMeetingSupportDocumentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["id"])
            id = remo_html_from_string(id)
            primary_agent_username = None            

            # in case of Dyte
            if 'primary_agent_username' in data:
                primary_agent_username = strip_html_tags(data["primary_agent_username"])
                primary_agent_username = remo_html_from_string(primary_agent_username)

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            if not primary_agent_username:
                meeting_io = CobrowseVideoConferencing.objects.get(meeting_id=id)
                agent_admin = meeting_io.agent
            else:
                easy_chat_user = User.objects.get(
                    username=primary_agent_username)
                agent_admin = CobrowseAgent.objects.filter(
                    user=easy_chat_user).first()

            agents_for_support_document = get_supervisor_from_active_agent(
                active_agent, CobrowseAgent)
            agents_for_support_document.append(agent_admin)

            support_document_objs = SupportDocument.objects.filter(
                agent__in=agents_for_support_document, is_usable=True, is_deleted=False)

            support_document = []
            for support_document_obj in support_document_objs:
                file_path = support_document_obj.file_access_management_key
                support_document.append({
                    "file_name": support_document_obj.file_name,
                    "file_path": file_path,
                    "file_type": support_document_obj.file_type
                })

            response["status"] = 200
            response["message"] = "success"
            response["support_document"] = support_document
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetListOfMeetingSupportDocumentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetListOfMeetingSupportDocument = GetListOfMeetingSupportDocumentAPI.as_view()


class RequestJoinMeetingAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["id"])
            support_agents = data["support_agents"]

            cobrowse_meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=id)
            meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
                cobrowse_video=cobrowse_meeting_obj)

            active_agent = cobrowse_meeting_obj.agent

            agent_admin = get_admin_from_active_agent(
                active_agent, CobrowseAgent)

            agents = get_list_agents_under_admin(agent_admin, is_active=True)

            is_cobrowsing_meeting = cobrowse_meeting_obj.is_cobrowsing_meeting

            product_name = "Cogno Meet"
            cognomeet_config_obj = get_developer_console_cognomeet_settings()
            if cognomeet_config_obj:
                product_name = cognomeet_config_obj.cognomeet_title_text

            if is_cobrowsing_meeting:
                cobrowse_io = CobrowseIO.objects.get(session_id=id)

                for user_id in support_agents:
                    user_obj = User.objects.get(pk=int(user_id))
                    cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
                    if cobrowse_agent in agents:
                        cobrowse_io.support_agents.add(cobrowse_agent)
                        meeting_audit_trail.meeting_agents_invited.add(
                            cobrowse_agent)
                        notification_message = "Hi, " + cobrowse_agent.user.username + \
                            "! A customer is waiting for you to connect on " + product_name + "."
                        NotificationManagement.objects.create(show_notification=True,
                                                              agent=cobrowse_agent,
                                                              notification_message=notification_message,
                                                              cobrowse_io=cobrowse_io,
                                                              product_name=product_name)
                        send_notification_to_agent(
                            cobrowse_agent, NotificationManagement)

                meeting_audit_trail.save()
                cobrowse_io.save()
            else:
                for user_id in support_agents:
                    user_obj = User.objects.get(pk=int(user_id))
                    cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
                    if cobrowse_agent in agents:
                        cobrowse_meeting_obj.support_meeting_agents.add(
                            cobrowse_agent)
                        meeting_audit_trail.meeting_agents_invited.add(
                            cobrowse_agent)

                cobrowse_meeting_obj.save()
                meeting_audit_trail.save()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RequestJoinMeetingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


RequestJoinMeeting = RequestJoinMeetingAPI.as_view()


class AssignVideoConferencingMeetAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            meeting_id = strip_html_tags(data["meeting_id"])
            agent_id = strip_html_tags(data["agent_id"])

            meeting_io = CobrowseVideoConferencing.objects.filter(
                meeting_id=meeting_id)

            if meeting_io:
                meeting_io = meeting_io[0]
                cobrowse_agent = CobrowseAgent.objects.get(pk=int(agent_id))
                meeting_io.agent = cobrowse_agent
                meeting_io.save()
                product_name = "Cogno Meet"
                cognomeet_config_obj = get_developer_console_cognomeet_settings()
                if cognomeet_config_obj:
                    product_name = cognomeet_config_obj.cognomeet_title_text
                response["status"] = 200
                response["message"] = "success"
                response["product_name"] = product_name
            else:
                response["status"] = 301
                response["message"] = "No meeting found."
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AssignVideoConferencingMeetAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AssignVideoConferencingMeet = AssignVideoConferencingMeetAPI.as_view()


class InviteVideoMeetingEmailAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            email_ids = data["email_ids"]
            meeting_id = strip_html_tags(data["meeting_id"])
            meeting_url = str(settings.EASYCHAT_HOST_URL) + "/easy-assist/meeting/" + \
                str(meeting_id)
            user_obj = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)

            meeting_io = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)
            agent_name = cobrowse_agent.user.username
            start_time = meeting_io.meeting_start_time
            start_time = start_time.strftime("%I:%M %p")
            meeting_date = meeting_io.meeting_start_date
            meeting_date = meeting_date.strftime("%d %B, %Y")
            join_password = ""
            if meeting_io.meeting_password != "" and meeting_io.meeting_password != None:
                join_password = meeting_io.meeting_password
            else:
                join_password = 'No Password Required.'

            for email_id in email_ids:
                email_id = strip_html_tags(email_id)
                thread = threading.Thread(target=send_invite_link_over_mail, args=(
                    email_id, meeting_url, agent_name, str(start_time), str(meeting_date), join_password), daemon=True)
                thread.start()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error InviteVideoMeetingEmailAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


InviteVideoMeetingEmail = InviteVideoMeetingEmailAPI.as_view()


class CheckAgentConnectedOrNotAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            meeting_id = strip_html_tags(data["meeting_id"])
            meeting_io = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)
            is_agent_connected = False
            if meeting_io.is_agent_connected:
                is_agent_connected = True
            response["status"] = 200
            response["message"] = "success"
            response["is_agent_connected"] = is_agent_connected
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckAgentConnectedOrNotAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckAgentConnectedOrNot = CheckAgentConnectedOrNotAPI.as_view()


class UpdateAgentJoinStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            meeting_id = strip_html_tags(data["meeting_id"])
            status_meeting = data["status"]
            meeting_io = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)
            if status_meeting == 'true':
                meeting_io.is_agent_connected = True
            else:
                meeting_io.is_agent_connected = False

            meeting_io.save()

            try:
                agent_obj = meeting_io.agent
                if status_meeting == 'true':
                    agent_obj.is_cognomeet_active = True
                    agent_obj.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error UpdateAgentJoinStatusAPI Agent is_cognomeet_active update %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateAgentJoinStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateAgentJoinStatus = UpdateAgentJoinStatusAPI.as_view()


class ClientMeetingFeedbackAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            meeting_id = strip_html_tags(data["meeting_id"])
            feedback_rating = strip_html_tags(data["feedback_rating"])
            feedback_comment = strip_html_tags(data["feedback_comment"])
            meeting_io = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)
            meeting_io.feedback_rating = int(feedback_rating)
            meeting_io.feedback_comment = feedback_comment
            meeting_io.save()
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ClientMeetingFeedbackAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ClientMeetingFeedback = ClientMeetingFeedbackAPI.as_view()


class CheckMeetingEndedOrNotAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            meeting_id = strip_html_tags(data["meeting_id"])
            meeting_io = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)
            cobrowse_agent = meeting_io.agent
            access_token_obj = cobrowse_agent.get_access_token_obj()
            if access_token_obj.allow_meeting_end_time:
                meeting_end_time = access_token_obj.meeting_end_time
                start_time = meeting_io.meeting_start_time
                current_time = datetime.today()

                start_time_diff = (start_time.hour * 60 * 60) + \
                    (start_time.minute * 60) + start_time.second
                current_time_diff = (current_time.hour * 60 * 60) + \
                    (current_time.minute) * 60 + current_time.second
                time_diff = abs(start_time_diff - current_time_diff)
                time_diff = int(time_diff / 60)
                five_minutes_left = int(meeting_end_time) - 5
                if int(time_diff) == int(five_minutes_left):
                    response["status"] = 301
                    response["message"] = 'This session will end in 5 minutes.'
                elif int(time_diff) >= int(meeting_end_time):
                    meeting_io.is_expired = True
                    meeting_io.is_meeting_ended = True
                    meeting_io.save()
                    response["status"] = 200
                    response["message"] = 'success'
            else:
                response["status"] = 400
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckMeetingEndedOrNotAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckMeetingEndedOrNot = CheckMeetingEndedOrNotAPI.as_view()


class CheckCobrowsingMeetingStatusAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            origin = get_request_origin(request)

            if cobrowse_access_token_obj == None:
                return Response(status=401)
            elif not cobrowse_access_token_obj.is_valid_domain(origin):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                meeting_id = strip_html_tags(data["session_id"])
                meeting_io_objs = CobrowseVideoConferencing.objects.filter(
                    meeting_id=meeting_id)
                if meeting_io_objs:
                    meeting_io = meeting_io_objs[0]

                    is_meeting_expired = meeting_io.is_expired

                    if is_meeting_expired:
                        response["status"] = 200
                        response["message"] = "success"
                    else:
                        meeting_audit_trail_objs = CobrowseVideoAuditTrail.objects.filter(
                            cobrowse_video=meeting_io)
                        if meeting_audit_trail_objs:
                            meeting_audit_trail = meeting_audit_trail_objs[0]
                            if meeting_audit_trail.is_meeting_ended:
                                response["status"] = 200
                                response["message"] = "success"
                            else:
                                response["status"] = 301
                                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckCobrowsingMeetingStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)

CheckCobrowsingMeetingStatus = CheckCobrowsingMeetingStatusAPI.as_view()


def AgentCobrowseVideoMeeting(request, session_id):
    try:
        agent_name = 'Agent'
        meeting_io = CobrowseVideoConferencing.objects.get(
            meeting_id=session_id)
        cobrowse_agent = meeting_io.agent

        agent_name = cobrowse_agent.name
        if cobrowse_agent.user.first_name != '':
            agent_name = cobrowse_agent.user.first_name
            if cobrowse_agent.user.last_name != '':
                agent_name += " " + cobrowse_agent.user.last_name

        access_token_obj = cobrowse_agent.get_access_token_obj()
        meeting_host_url = access_token_obj.meeting_host_url
        cobrowse_logo = access_token_obj.source_easyassist_cobrowse_logo
        meet_background_color = access_token_obj.meet_background_color
        enable_reverse_cobrowsing = access_token_obj.allow_agent_to_customer_cobrowsing

        invited_agent_name = ""
        invited_agent_username = ""
        admin_agent_username = cobrowse_agent.user.username
        is_invited_agent = False
        invited_agent = None
        agent_identifier = ""
        if 'id' in request.GET:
            agent_identifier = request.GET['id']
            invited_agent = CobrowseAgent.objects.filter(
                virtual_agent_code=agent_identifier).first()
        else:
            user_obj = User.objects.filter(username=request.user.username)
            if user_obj:
                user_obj = user_obj.first()
                temp_invited_agent = CobrowseAgent.objects.filter(
                    user=user_obj)
                if temp_invited_agent:
                    temp_invited_agent = temp_invited_agent.first()
                    cobrowse_io_obj = CobrowseIO.objects.filter(
                        session_id=session_id).first()
                    if cobrowse_io_obj and temp_invited_agent in cobrowse_io_obj.support_agents.all():
                        invited_agent = temp_invited_agent

        if invited_agent:
            invited_agent_name = invited_agent.user.first_name
            invited_agent_username = invited_agent.user.username
            is_invited_agent = True
            if invited_agent_name is None or invited_agent_name.strip() == "":
                invited_agent_name = invited_agent.user.username

        try:
            video_obj = CobrowseVideoAuditTrail.objects.get(
                cobrowse_video=meeting_io)

        except Exception:
            video_obj = CobrowseVideoAuditTrail.objects.create(
                cobrowse_video=meeting_io)

        if invited_agent:
            video_obj.meeting_agents.add(invited_agent)
            video_obj.save()

        if meeting_io.is_expired == True:
            return render(request, "EasyAssistApp/voip_meeting_ended.html", {
                "logo": cobrowse_logo,
                "cobrowse_agent": cobrowse_agent,
                "access_token_key": str(access_token_obj.key),
                "is_agent": True,
            })

        return render(request, "EasyAssistApp/agent_cobrowse_join_meeting.html", {
            "meeting_io": meeting_io,
            "meeting_host_url": meeting_host_url,
            "agent_name": agent_name,
            "unique_id": str(uuid.uuid4()),
            "cobrowse_logo": cobrowse_logo,
            "meet_background_color": meet_background_color,
            "cobrowse_agent": cobrowse_agent,
            "access_token_key": str(access_token_obj.key),
            "enable_voip_calling": access_token_obj.enable_voip_calling,
            "enable_reverse_cobrowsing": enable_reverse_cobrowsing,
            "invited_agent_name": invited_agent_name,
            "admin_agent_username": admin_agent_username,
            "invited_agent_username": invited_agent_username,
            "agent_identifier": agent_identifier,
            "is_invited_agent": is_invited_agent,
            "DEVELOPMENT": settings.DEVELOPMENT,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error AgentCobrowseVideoMeeting %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)


def ClientCobrowseVideoMeeting(request, session_id):
    try:
        client_name = 'Client'

        meeting_io = CobrowseVideoConferencing.objects.get(
            meeting_id=session_id)
        client_name = meeting_io.full_name
        cobrowse_agent = meeting_io.agent
        access_token_obj = cobrowse_agent.get_access_token_obj()
        meeting_host_url = access_token_obj.meeting_host_url
        cobrowse_logo = access_token_obj.source_easyassist_cobrowse_logo
        meet_background_color = access_token_obj.meet_background_color
        enable_reverse_cobrowsing = access_token_obj.allow_agent_to_customer_cobrowsing
        
        if meeting_io.is_expired == True:
            return render(request, "EasyAssistApp/voip_meeting_ended.html", {
                "logo": cobrowse_logo,
                "cobrowse_agent": cobrowse_agent,
                "access_token_key": str(access_token_obj.key),
                "is_agent": False,
            })

        return render(request, "EasyAssistApp/client_cobrowse_join_meeting.html", {
            "meeting_io": meeting_io,
            "meeting_host_url": meeting_host_url,
            "client_name": client_name,
            "unique_id": str(uuid.uuid4()),
            "cobrowse_logo": cobrowse_logo,
            "meet_background_color": meet_background_color,
            "enable_s3_bucket": access_token_obj.agent.user.enable_s3_bucket,
            "access_token_key": str(access_token_obj.key),
            "enable_voip_calling": access_token_obj.enable_voip_calling,
            "enable_reverse_cobrowsing": enable_reverse_cobrowsing,
            "DEVELOPMENT": settings.DEVELOPMENT,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ClientCobrowseVideoMeeting %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)


class SaveVoipMeetingDurationAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            meeting_id = data["meeting_id"]
            meeting_id = remo_html_from_string(meeting_id)

            cobrowse_io = CobrowseIO.objects.get(session_id=meeting_id)
            cobrowse_io.allow_agent_meeting = 'None'
            cobrowse_io.allow_customer_meeting = 'None'
            cobrowse_io.save()

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)

            cobrowse_agent = meeting_obj.agent
            cobrowse_agent.is_cognomeet_active = False
            cobrowse_agent.save()
            meeting_audit_trail = CobrowseVideoAuditTrail.objects.filter(
                cobrowse_video=meeting_obj)
            if meeting_audit_trail:
                meeting_audit_trail[0].meeting_ended = timezone.now()
                meeting_audit_trail[0].agent_end_time = timezone.now()
                meeting_audit_trail[0].is_meeting_ended = True
                meeting_audit_trail[0].save()
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveVoipMeetingDurationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveVoipMeetingDuration = SaveVoipMeetingDurationAPI.as_view()


class LoadMapScriptAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyBAHTtk1lkVvIl1X_i7_1aIK9RCrhqGEpQ&libraries=places"
            response['src'] = src
            response['status'] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error LoadMapScriptAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


LoadMapScript = LoadMapScriptAPI.as_view()


class GetMeetingSupportAgentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            meeting_id = data["meeting_id"]

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)

            cobrowse_agent = meeting_obj.agent
            active_admin_user = get_admin_from_active_agent(
                cobrowse_agent, CobrowseAgent)

            agents = get_list_agents_under_admin(
                active_admin_user, is_active=True)

            support_agents = []
            for agent in agents:
                if agent.pk != cobrowse_agent.pk:
                    support_agents.append({
                        "id": agent.user.pk,
                        "username": agent.user.username,
                        "level": agent.support_level
                    })

            response["status"] = 200
            response["support_agents"] = support_agents
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetMeetingSupportAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetMeetingSupportAgent = GetMeetingSupportAgentAPI.as_view()


class SaveCognoVidMeetingEndTimeAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            meeting_id = data["meeting_id"]
            meeting_id = remo_html_from_string(meeting_id)
            is_agent = data["is_agent"]
            is_agent = remo_html_from_string(is_agent)
            is_invited_agent = data["is_invited_agent"]
            is_invited_agent = remo_html_from_string(is_invited_agent)

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            try:
                time_threshold = datetime.now() - timedelta(minutes=1)
                agent_work_audit_trail_obj = CobrowseAgentWorkAuditTrail.objects.filter(
                    agent=active_agent,
                    session_end_datetime__gte=time_threshold).order_by(
                        '-session_start_datetime').first()

                if agent_work_audit_trail_obj != None:
                    agent_work_audit_trail_obj.session_end_datetime = timezone.now()
                    agent_work_audit_trail_obj.save()
                else:
                    agent_work_audit_trail_obj = CobrowseAgentWorkAuditTrail.objects.create(
                        agent=active_agent,
                        session_start_datetime=timezone.now(),
                        session_end_datetime=timezone.now())
                    agent_work_audit_trail_obj.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error SaveCognoVidMeetingEndTimeAPI %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)

            meeting_audit_trail = CobrowseVideoAuditTrail.objects.filter(
                cobrowse_video=meeting_obj)

            if meeting_audit_trail:
                meeting_audit_trail = meeting_audit_trail[0]
                if is_agent == "True":
                    meeting_audit_trail.agent_end_time = timezone.now()
                    active_agent.is_cognomeet_active = True
                    active_agent.last_active_in_meet_datetime = timezone.now()
                elif is_invited_agent == "True":
                    active_agent.is_cognomeet_active = True
                    active_agent.last_active_in_meet_datetime = timezone.now()

                active_agent.save()
                meeting_audit_trail.save()
                response["status"] = 200
            else:
                response["status"] = 301

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCognoVidMeetingEndTimeAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCognoVidMeetingEndTime = SaveCognoVidMeetingEndTimeAPI.as_view()


def VoIPMeetingEnded(request, meeting_user, meeting_id):
    try:
        try:
            user_obj = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.filter(
                user=user_obj).first()
            if cobrowse_agent and meeting_user == "agent":
                is_agent = True
            else:
                is_agent = False
        except Exception:
            is_agent = False

        cobrowse_video_obj = CobrowseVideoConferencing.objects.get(
            meeting_id=meeting_id)
        cobrowse_agent = cobrowse_video_obj.agent
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/voip_meeting_ended.html", {
            "logo": access_token_obj.source_easyassist_cobrowse_logo,
            "cobrowse_agent": cobrowse_agent,
            "access_token_key": str(access_token_obj.key),
            "is_agent": is_agent,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error VoIPMeetingEnded %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


class SaveJitsiRecordingAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = request.data
            # meeting_id = data["sessionId"]
            # app_id = data["appId"]
            # participants = data["data"]["participants"]
            # duration = data["data"]["durationSec"]
            # start_timestamp = data["data"]["startTimestamp"]
            # end_timestamp = data["data"]["endTimestamp"]
            recording_link = data["data"]["preAuthenticatedLink"]
            logger.error("SaveJitsiRecordingAPI %s", recording_link,
                         extra={'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveJitsiRecordingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


SaveJitsiRecording = SaveJitsiRecordingAPI.as_view()


class GetListOfAgentUnderSupervisorAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)            

            user_obj = User.objects.get(username=request.user.username)
            cobrowsing_agent_obj = CobrowseAgent.objects.filter(
                user=user_obj).first()

            agents_under_supervisor_list = []            
            for agents in cobrowsing_agent_obj.agents.all():
                if agents.is_account_active:                    
                    agents_under_supervisor_list.append(agents.user.username)           

            response["status"] = 200
            response["support_agents"] = agents_under_supervisor_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetListOfAgentUnderSupervisorAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetListOfAgentUnderSupervisor = GetListOfAgentUnderSupervisorAPI.as_view()
