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
from django.contrib.sessions.models import Session

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
"""For user authentication"""
from django.contrib.auth import authenticate, login, logout

from EasyAssistSalesforceApp.models import *
from EasyAssistSalesforceApp.utils import *
from EasyAssistSalesforceApp.html_parser import strip_html_tags
from EasyAssistSalesforceApp.send_email import send_password_over_email, send_meeting_link_over_mail, send_invite_link_over_mail

from urllib.parse import quote_plus, unquote

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
from datetime import datetime
import random
import urllib.parse
import threading
from django.conf import settings

from operator import itemgetter
from collections import OrderedDict

logger = logging.getLogger(__name__)


class GenerateVideoConferencingMeetAPI(APIView):

    # permission_classes = [IsAuthenticated]

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

            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if cobrowse_agent == None:
                return HttpResponse(status=401)

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

            meeting_url = str(settings.EASYCHAT_HOST_URL) + "/easy-assist-salesforce/meeting/" + \
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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GenerateVideoConferencingMeet = GenerateVideoConferencingMeetAPI.as_view()


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

        salesforce_token = None
        try:
            salesforce_token = quote_plus(request.GET["salesforce_token"])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoVidMeetingEnded %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        try:
            cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
            agent_name = cobrowse_agent.name

            if cobrowse_agent.user.first_name != '':
                agent_name = cobrowse_agent.user.first_name
                if cobrowse_agent.user.last_name != '':
                    agent_name += " " + cobrowse_agent.user.last_name

            is_agent = True
        except Exception:
            is_agent = False

        try:
            meeting_io = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)
            if int(cobrowse_agent.pk) != int(meeting_io.agent.pk):
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
            if allow_meeting_end_time:
                meeting_end_time = access_token_obj.meeting_end_time

            if meeting_io.is_expired:
                return render(request, "EasyAssistSalesforceApp/meeting_expired.html", {
                    "logo": cobrowse_logo
                })
            else:
                try:
                    audit_trail = CobrowseVideoAuditTrail.objects.get(
                        cobrowse_video=meeting_io)
                except Exception:
                    audit_trail = CobrowseVideoAuditTrail.objects.create(
                        cobrowse_video=meeting_io)
                return render(request, "EasyAssistSalesforceApp/join_meeting.html", {
                    "salesforce_token": salesforce_token,
                    "meeting_io": meeting_io,
                    "meeting_host_url": meeting_host_url,
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
                    "is_invited_agent": is_invited_agent
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
            if allow_meeting_end_time:
                meeting_end_time = access_token_obj.meeting_end_time

            if meeting_io.is_expired:
                return render(request, "EasyAssistSalesforceApp/meeting_expired.html", {
                    "logo": logo
                })
            elif status == "waiting":
                meeting_date_time = meeting_io.meeting_start_date.strftime(
                    '%Y-%m-%d') + " " + meeting_io.meeting_start_time.strftime('%H:%M:%S')
                return render(request, "EasyAssistSalesforceApp/join_meeting.html", {
                    "salesforce_token": salesforce_token,
                    "is_waiting": True,
                    'meeting_date_time': meeting_date_time,
                    "is_cobrowsing_active": is_cobrowsing_active,
                    "cobrowse_logo": cobrowse_logo,
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

                if is_agent:
                    cobrowse_agent.is_cognomeet_active = True
                    cobrowse_agent.save()
                    if audit_trail.is_meeting_ended == False:
                        audit_trail.agent_joined = timezone.now()
                        audit_trail.save()
                else:
                    is_agent = False
                return render(request, "EasyAssistSalesforceApp/join_meeting.html", {
                    "salesforce_token": salesforce_token,
                    "meeting_io": meeting_io,
                    "meeting_host_url": meeting_host_url,
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
                    "meeting_end_time": meeting_end_time,
                    "is_invited_agent": is_invited_agent
                })
        else:
            return HttpResponse(status=404)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CognoVidMeeting %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse(status=401)


def CognoVidMeetingEnded(request, meeting_id):
    try:
        is_cognomeet_active = False
        is_feedback = False
        if "is_meeting_cobrowsing" in request.GET:
            is_cognomeet_active = True
        if "is_feedback" in request.GET:
            if request.GET["is_feedback"] == 'true':
                is_feedback = True

        salesforce_token = None
        try:
            salesforce_token = quote_plus(request.GET["salesforce_token"])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoVidMeetingEnded %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        meeting_io = CobrowseVideoConferencing.objects.get(
            meeting_id=meeting_id)
        cobrowse_agent = meeting_io.agent
        access_token_obj = cobrowse_agent.get_access_token_obj()
        cobrowse_logo = access_token_obj.source_easyassist_cobrowse_logo
        return render(request, "EasyAssistSalesforceApp/meeting_end.html", {
            "salesforce_token": salesforce_token,
            "meeting_id": meeting_id,
            "is_cognomeet_active": is_cognomeet_active,
            "is_feedback": is_feedback,
            "cobrowse_logo": cobrowse_logo
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CognoVidMeetingEnded %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse(status=401)


def CognoVidAuditTrail(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        agents = []
        if cobrowse_agent.role == "agent":
            agents = [cobrowse_agent]
        elif cobrowse_agent.role == "supervisor":
            agents = cobrowse_agent.agents.all()
        else:
            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None)

        cobrowse_video_objs = CobrowseVideoConferencing.objects.filter(
            agent__in=agents)

        if "startdate" in request.GET:
            date_format = "%Y-%m-%d"
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.strptime(
                start_date, date_format).date()

            cobrowse_video_objs = cobrowse_video_objs.filter(
                meeting_start_date__gte=datetime_start)

        if "enddate" in request.GET:
            date_format = "%Y-%m-%d"
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.strptime(
                end_date, date_format).date()
            cobrowse_video_objs = cobrowse_video_objs.filter(
                meeting_start_date__lte=datetime_end)

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")[0]
            agent_email = remo_html_from_string(agent_email)

            try:
                selected_agent = CobrowseAgent.objects.get(
                    user__username=agent_email)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error CognoVidAuditTrail %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
                selected_agent = []

            cobrowse_video_objs = cobrowse_video_objs.filter(
                agent=selected_agent)

        if "meeting-status" in request.GET:
            meeting_status = request.GET.getlist("meeting-status")[0]
            meeting_status = remo_html_from_string(meeting_status)
            if meeting_status == "completed":
                cobrowse_video_objs = cobrowse_video_objs.filter(
                    is_expired=True)
            elif meeting_status == "notcompleted":
                cobrowse_video_objs = cobrowse_video_objs.filter(
                    is_expired=False)

        audit_trail_objs = CobrowseVideoAuditTrail.objects.filter(
            cobrowse_video__in=cobrowse_video_objs).order_by('-pk')
        return render(request, "EasyAssistSalesforceApp/meeting_audit_trail.html", {
            "salesforce_token": quote_plus(request.GET["salesforce_token"]),
            "audit_trail_objs": audit_trail_objs,
            "cobrowse_agent": cobrowse_agent,
            "agents": agents,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CognoVidAuditTrail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse(status=401)


def CobrowseVideoConferencingDataCollect(request, meeting_id, form_id):
    try:
        meeting_io = CobrowseVideoConferencing.objects.get(
            meeting_id=meeting_id, is_expired=False)
        # cobrowse_agent = meeting_io.agent

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

            return render(request, "EasyAssistSalesforceApp/cobrowse_data_collect_form.html", {
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
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)

        meeting_io = CobrowseVideoConferencing.objects.get(
            meeting_id=meeting_id)
        # cobrowse_agent = meeting_io.agent

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

    # permission_classes = [IsAuthenticated]

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
            # cobrowse_agent = meeting_io.agent

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

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if cobrowse_agent == None:
                return HttpResponse(status=401)

            current_date = datetime.now().date()
            meeting_objs = CobrowseVideoConferencing.objects.filter(
                agent=cobrowse_agent, meeting_start_date=current_date).order_by('-meeting_start_time')

            meeting_list = []
            for meeting_obj in meeting_objs:
                meeting_list.append({
                    'id': str(meeting_obj.pk),
                    "description": meeting_obj.meeting_description,
                    "start_date": meeting_obj.meeting_start_date.strftime("%b %d, %Y"),
                    "start_time": meeting_obj.meeting_start_time.strftime("%-I:%M %p"),
                    "end_time": meeting_obj.meeting_end_time.strftime("%-I:%M %p"),
                    "is_expired": meeting_obj.is_expired,
                })

            response["status"] = 200
            response["message"] = "success"
            response["meeting_list"] = meeting_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCognoVidScheduledMeetingsList %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCognoVidScheduledMeetingsList = GetCognoVidScheduledMeetingsListAPI.as_view()


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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckMeetingEndedOrNot = CheckMeetingEndedOrNotAPI.as_view()


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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckAgentConnectedOrNot = CheckAgentConnectedOrNotAPI.as_view()


class UpdateAgentJoinStatusAPI(APIView):

    # permission_classes = [IsAuthenticated]

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
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateAgentJoinStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateAgentJoinStatus = UpdateAgentJoinStatusAPI.as_view()


class CognoVidMeetingDurationAPI(APIView):

    # permission_classes = [IsAuthenticated]

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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoVidMeetingDuration = CognoVidMeetingDurationAPI.as_view()


class CognoVidMeetingChatsAPI(APIView):

    # permission_classes = [IsAuthenticated]

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
                    message_obj['message'] = remo_html_from_string(
                        message_obj['message'])
                    message_obj["message"] = '<a href=' + \
                        message_obj["message"] + '>File Attachment</a>'
                else:
                    message_obj['message'] = remo_html_from_string(
                        message_obj['message'])
                    message_obj['message'] = remo_special_tag_from_string(
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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoVidMeetingChats = CognoVidMeetingChatsAPI.as_view()


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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoVidAuthenticatePassword = CognoVidAuthenticatePasswordAPI.as_view()


class CognoVidMeetingNotesAPI(APIView):

    # permission_classes = [IsAuthenticated]

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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoVidMeetingNotes = CognoVidMeetingNotesAPI.as_view()


# class SaveScreenRecordedDataAPI(APIView):

# permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         response = {}
#         custom_encrypt_obj = CustomEncrypt()
#         try:
#             data = request.data

#             if not isinstance(data, dict):
#                 data = json.loads(data)

#             uploaded_file = data["uploaded_data"]
#             filename = data["filename"]
#             meeting_id = data["meeting_id"]
#             is_first_packet = data["is_first_packet"]
#             filename = meeting_id + ".webm"

#             if not os.path.exists('secured_files/EasyAssistSalesforceApp/cognovid'):
#                 os.makedirs('secured_files/EasyAssistSalesforceApp/cognovid')

#             file_path = "secured_files/EasyAssistSalesforceApp/cognovid/" + filename

#             media_file = open(file_path, "ab+")
#             media_file.write(uploaded_file.read())
#             media_file.close()

#             file_path = "/" + file_path

#             try:
#                 file_access_management_obj = CobrowsingFileAccessManagement.objects.get(
#                     file_path=file_path, is_public=False)
#             except Exception:
#                 file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
#                     file_path=file_path, is_public=False)

#             meeting_obj = CobrowseVideoConferencing.objects.get(
#                 meeting_id=meeting_id)

#             meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
#                 cobrowse_video=meeting_obj)
#             if (is_first_packet == 'true' or is_first_packet == True) and (meeting_audit_trail.meeting_recording == '' or meeting_audit_trail.meeting_recording == None):
#                 logger.info(timezone.now(), extra={'AppName': 'EasyAssistSalesforce'})
#                 meeting_audit_trail.agent_recording_start_time = timezone.now()

#             meeting_audit_trail.meeting_recording = file_path
#             meeting_audit_trail.save()

#             response["status"] = 200
#             # response["src"] = "/files/" + filename
#             response["name"] = filename
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error("Inside SaveScreenRecordedDataAPI %s at %s", str(
#                 e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
#             response["status"] = 500
#             response["name"] = "no_name"
#             # response["src"] = "error"

#         response = json.dumps(response)
#         encrypted_response = custom_encrypt_obj.encrypt(response)
#         response = {"Response": encrypted_response}
#         return Response(data=response)


# SaveScreenRecordedData = SaveScreenRecordedDataAPI.as_view()


class SaveScreenRecordedDataAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        try:

            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            uploaded_file = data["uploaded_data"]
            filename = data["filename"]
            meeting_id = data["meeting_id"]
            filename = meeting_id + '.webm'

            if not os.path.exists('secured_files/EasyAssistSalesforceApp/cognovid'):
                os.makedirs('secured_files/EasyAssistSalesforceApp/cognovid')

            file_path = "secured_files/EasyAssistSalesforceApp/cognovid/" + filename

            media_file = open(file_path, "ab+")
            media_file.write(uploaded_file.read())
            media_file.close()

            file_path = "/" + file_path

            logger.info("Inside SaveScreenRecordedDataAPI FILE PATH %s",
                        file_path, extra={'AppName': 'EasyAssistSalesforce'})
            try:
                file_access_management_obj = CobrowsingFileAccessManagement.objects.get(
                    file_path=file_path, is_public=False)
            except Exception:
                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=file_path, is_public=False)

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)

            meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
                cobrowse_video=meeting_obj)
            meeting_audit_trail.meeting_recording = str(
                file_access_management_obj.pk)
            meeting_audit_trail.merged_filepath = str(
                file_access_management_obj.pk)
            meeting_audit_trail.is_merging_done = True
            meeting_audit_trail.save()

            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveScreenRecordedDataAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
            response["status"] = 500
            response["name"] = "no_name"

        response = json.dumps(response)
        return Response(data=response)


SaveScreenRecordedData = SaveScreenRecordedDataAPI.as_view()


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

            if not os.path.exists('secured_files/EasyAssistSalesforceApp/cognovid'):
                os.makedirs('secured_files/EasyAssistSalesforceApp/cognovid')

            file_path = "secured_files/EasyAssistSalesforceApp/cognovid/" + filename

            media_file = open(file_path, "ab+")
            media_file.write(uploaded_file.read())
            media_file.close()

            file_path = "/" + file_path

            is_recording_present = False

            if(CobrowsingFileAccessManagement.objects.filter(file_path=file_path, is_public=False).count() > 0):
                is_recording_present = True
            else:
                CobrowsingFileAccessManagement.objects.create(
                    file_path=file_path, is_public=False)

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)

            meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
                cobrowse_video=meeting_obj)

            client_audio_file = json.loads(
                meeting_audit_trail.client_audio_recording)

            if is_recording_present:
                logger.info("File already present in the list",
                            extra={'AppName': 'EasyAssistSalesforce'})
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
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
            response["status"] = 500
            response["name"] = "no_name"
            response["src"] = "error"

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveClientRecordedData = SaveClientRecordedDataAPI.as_view()


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
            session_id = data["session_id"]
            session_id = remo_html_from_string(session_id)

            file_extention = filename.replace(" ", "").split(".")[-1]
            file_extention = file_extention.lower()

            if file_extention not in ["png", "jpg", "jpeg", "pdf", "doc", "docx"] or check_malicious_file_from_filename(filename):
                response["status"] = 302
            else:
                if not os.path.exists('secured_files/EasyAssistSalesforceApp/cognovid'):
                    os.makedirs(
                        'secured_files/EasyAssistSalesforceApp/cognovid')

                file_path = "secured_files/EasyAssistSalesforceApp/cognovid/" + filename

                fh = open(file_path, "wb")
                fh.write(base64.b64decode(base64_data))
                fh.close()

                file_path = "/" + file_path

                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=file_path, is_public=False)

                src = "/easy-assist-salesforce/download-file/" + \
                    str(file_access_management_obj.key)
                response["status"] = 200
                response["src"] = src
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside UploadCognoVidFileAttachmentAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
            response["status"] = 500
            response["name"] = "no_name"
            response["src"] = "error"

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadCognoVidFileAttachment = UploadCognoVidFileAttachmentAPI.as_view()


class GetListOfMeetSuportAgentsAPI(APIView):

    # permission_classes = [IsAuthenticated]

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

            agents = get_list_agents_under_admin(agent_admin, is_active=True)
            # support_agents = []

            product_categories = agent_admin.product_category.all()
            product_category_wise_agent_list = dict()

            for product_category in product_categories:
                product_category_wise_agent_list[product_category.title] = []

                for agent in agents:
                    if agent.user.username != agent_admin.user.username:
                        if agent.product_category.filter(pk=product_category.pk).count():
                            product_category_wise_agent_list[product_category.title].append({
                                "id": agent.user.pk,
                                "username": agent.user.username,
                                "level": agent.support_level
                            })

            for agent in agents:
                if agent.user.username != agent_admin.user.username:
                    if agent.product_category.all().count() == 0:
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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetListOfMeetSuportAgents = GetListOfMeetSuportAgentsAPI.as_view()


class GetListOfMeetingFormsAPI(APIView):

    # permission_classes = [IsAuthenticated]

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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetListOfMeetingForms = GetListOfMeetingFormsAPI.as_view()


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
            agent_admin = cobrowse_meeting_obj.agent

            agents = get_list_agents_under_admin(agent_admin, is_active=True)

            for user_id in support_agents:
                user_obj = User.objects.get(pk=int(user_id))
                cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
                if cobrowse_agent in agents:
                    cobrowse_meeting_obj.support_meeting_agents.add(
                        cobrowse_agent)
                    meeting_audit_trail.meeting_agents.add(cobrowse_agent)
            cobrowse_meeting_obj.save()
            meeting_audit_trail.save()
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RequestJoinMeetingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


RequestJoinMeeting = RequestJoinMeetingAPI.as_view()


class AssignVideoConferencingMeetAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)

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
                response["status"] = 200
                response["message"] = "success"
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

    # permission_classes = [IsAuthenticated]

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
            meeting_url = str(settings.EASYCHAT_HOST_URL) + "/easy-assist-salesforce/meeting/" + \
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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


InviteVideoMeetingEmail = InviteVideoMeetingEmailAPI.as_view()


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

            meeting_id = remo_html_from_string(meeting_id)
            client_name = remo_html_from_string(client_name)
            client_name = remo_special_tag_from_string(client_name)
            longitude = remo_html_from_string(str(longitude))
            latitude = remo_html_from_string(str(latitude))

            meeting_obj = CobrowseVideoConferencing.objects.get(
                meeting_id=meeting_id)

            meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
                cobrowse_video=meeting_obj)

            client_location_details = json.loads(
                meeting_audit_trail.client_location_details)

            client_location_details["items"].append({
                "client_name": client_name,
                "longitude": str(longitude),
                "latitude": str(latitude)
            })
            meeting_audit_trail.client_location_details = json.dumps(
                client_location_details)
            meeting_audit_trail.save()

            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveClientLocationDetailsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
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

            meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
                cobrowse_video=meeting_obj)

            meeting_screenshot = json.loads(
                meeting_audit_trail.meeting_screenshot)

            format, imgstr = content.split(';base64,')
            ext = format.split('/')[-1]
            image_name = str(int(uuid.uuid4())) + "." + str(ext)

            if not os.path.exists('secured_files/EasyAssistSalesforceApp/cognovid'):
                os.makedirs('secured_files/EasyAssistSalesforceApp/cognovid')

            file_path = "secured_files/EasyAssistSalesforceApp/cognovid/" + image_name

            fh = open(file_path, "wb")
            fh.write(base64.b64decode(imgstr))
            fh.close()

            file_path = "/" + file_path

            file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                file_path=file_path, is_public=False)

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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCognoMeetScreenshot = SaveCognoMeetScreenshotAPI.as_view()


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


class CheckCobrowsingMeetingStatusAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            # HTTP_USER_AGENT = None
            # HTTP_X_FORWARDED_FOR = None
            # if settings.ENABLE_IP_TRACKING:
            #     HTTP_X_FORWARDED_FOR = request.META["HTTP_X_FORWARDED_FOR"]
            #     HTTP_USER_AGENT = request.META["HTTP_USER_AGENT"]

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
                meeting_io = CobrowseVideoConferencing.objects.get(
                    meeting_id=meeting_id)

                is_meeting_expired = meeting_io.is_expired

                if is_meeting_expired:
                    response["status"] = 200
                    response["message"] = "success"
                else:
                    meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
                        cobrowse_video=meeting_io)
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
