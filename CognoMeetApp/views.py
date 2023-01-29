from http import server
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render, HttpResponse, redirect
"""For user authentication"""
from django.contrib.auth import authenticate, login, logout
from CognoMeetApp.encrypt import CustomEncrypt
from CognoMeetApp.html_parser import strip_html_tags
from django.utils import timezone
from dateutil.parser import parse
from requests.exceptions import Timeout


from CognoMeetApp.send_email import send_meeting_link_over_mail, send_invite_link_over_mail
from CognoMeetApp.models import *
from EasyChatApp.models import User
from django.conf import settings
from CognoMeetApp.utils_validation import *
from CognoMeetApp.constants import *
from CognoMeetApp.utils import *
from CognoMeetApp.utils_dyte_apis import get_dyte_meeting_total_participants

import os
import sys
import logging
import json
import requests
import threading
import base64
import time
import re
import pytz
import uuid
from datetime import datetime, date


logger = logging.getLogger(__name__)


class CreateAccessTokenAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            admin_agent_username = sanitize_input_string(
                data["admin_agent_username"])
            user_obj = User.objects.filter(
                username=admin_agent_username).first()
            if user_obj:
                cognomeet_agent_obj = CognoMeetAgent.objects.filter(
                    user=user_obj).first()
                if not cognomeet_agent_obj:
                    cognomeet_agent_obj = CognoMeetAgent.objects.create(
                        user=user_obj, role="admin")
                elif cognomeet_agent_obj.role != "admin":
                    response["message"] = "CognoMeet agent for the username exists and the role is not that of an admin"
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

                cognomeet_access_token_obj = CognoMeetAccessToken.objects.filter(
                    agent=cognomeet_agent_obj).first()
                if not cognomeet_access_token_obj:
                    cognomeet_access_token_obj = CognoMeetAccessToken.objects.create(
                        agent=cognomeet_agent_obj)
                    create_cognomeet_config_objects(
                        cognomeet_access_token_obj, CognoMeetConfig, CognoMeetTimers)

                response["status"] = 200
                response["message"] = "success"
                response["access_token_key"] = str(
                    cognomeet_access_token_obj.key)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CreateAccessTokenAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CreateAccessToken = CreateAccessTokenAPI.as_view()


class UpdateAccessTokenConfigAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cognomeet_access_token = sanitize_input_string(
                data["cognomeet_access_token"])

            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                cognomeet_access_token, CognoMeetAccessToken)

            if not cognomeet_access_token_obj:
                return Response(data=get_invalid_access_token_response(custom_encrypt_obj, json))

            if "reset_config" in data and data["reset_config"]:
                cognomeet_access_token_obj.enable_screen_capture = True

                cognomeet_access_token_obj.enable_invite_agent = True

                cognomeet_access_token_obj.show_lobby_page = True

                cognomeet_access_token_obj.enable_time_duration = False

                cognomeet_access_token_obj.max_time_duration = 60

                cognomeet_access_token_obj.no_agent_permit_meeting_toast = True

                cognomeet_access_token_obj.no_agent_permit_meeting_toast_time = 1

                cognomeet_access_token_obj.no_agent_permit_meeting_toast_text = NO_AGENT_PERMIT_MEETING_TOAST_TEXT

                cognomeet_access_token_obj.meeting_background_color = "474747"

                cognomeet_access_token_obj.enable_feedback_in_meeting = True

                cognomeet_access_token_obj.meeting_default_password = ""

                cognomeet_access_token_obj.enable_auto_recording = False

                cognomeet_access_token_obj.enable_screen_sharing = True

                cognomeet_access_token_obj.enable_meeting_chat = True

            else:
                if "enable_screen_capture" in data:
                    cognomeet_access_token_obj.enable_screen_capture = data["enable_screen_capture"]

                if "enable_invite_agent" in data:
                    cognomeet_access_token_obj.enable_invite_agent = data["enable_invite_agent"]

                if "show_lobby_page" in data:
                    cognomeet_access_token_obj.show_lobby_page = data["show_lobby_page"]

                if "enable_time_duration" in data:
                    cognomeet_access_token_obj.enable_time_duration = data["enable_time_duration"]

                if "max_time_duration" in data:
                    if "enable_time_duration" in data and data["enable_time_duration"]:
                        cognomeet_access_token_obj.max_time_duration = int(
                            sanitize_input_string(data["max_time_duration"]))

                if "no_agent_permit_meeting_toast" in data:
                    cognomeet_access_token_obj.no_agent_permit_meeting_toast = data[
                        "no_agent_permit_meeting_toast"]

                if "no_agent_permit_meeting_toast_time" in data:
                    cognomeet_access_token_obj.no_agent_permit_meeting_toast_time = int(
                        sanitize_input_string(data["no_agent_permit_meeting_toast_time"]))

                if "no_agent_permit_meeting_toast_text" in data:
                    cognomeet_access_token_obj.no_agent_permit_meeting_toast_text = sanitize_input_string(
                        data["no_agent_permit_meeting_toast_text"])

                if "meeting_background_color" in data:
                    cognomeet_access_token_obj.meeting_background_color = sanitize_input_string(
                        data["meeting_background_color"])

                if "enable_feedback_in_meeting" in data:
                    cognomeet_access_token_obj.enable_feedback_in_meeting = data[
                        "enable_feedback_in_meeting"]

                if "meeting_default_password" in data:
                    cognomeet_access_token_obj.meeting_default_password = strip_html_tags(
                        data["meeting_default_password"])

                if "enable_auto_recording" in data:
                    cognomeet_access_token_obj.enable_auto_recording = data["enable_auto_recording"]

                if "enable_screen_sharing" in data:
                    cognomeet_access_token_obj.enable_screen_sharing = data["enable_screen_sharing"]

                if "enable_meeting_chat" in data:
                    cognomeet_access_token_obj.enable_meeting_chat = data["enable_meeting_chat"]

            cognomeet_access_token_obj.save()

            response["status"] = 200
            response["message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateAccessTokenConfigAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateAccessTokenConfig = UpdateAccessTokenConfigAPI.as_view()


class GenerateCognoMeetMeetingAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cognomeet_access_token = sanitize_input_string(data["dyte_access_token"])
            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                cognomeet_access_token, CognoMeetAccessToken)

            if not cognomeet_access_token_obj:
                return Response(data=get_invalid_access_token_response(custom_encrypt_obj, json))

            full_name = strip_html_tags(data["full_name"])
            mobile_number = strip_html_tags(data["mobile_number"])
            meeting_description = strip_html_tags(data["meeting_description"])
            meeting_start_date = strip_html_tags(data["meeting_start_date"])
            meeting_start_time = strip_html_tags(data["meeting_start_time"])
            meeting_end_time = strip_html_tags(data["meeting_end_time"])
            meeting_password = strip_html_tags(data["meeting_password"])
            email_id = strip_html_tags(data["email"])

            user_obj = User.objects.get(username=request.user.username)
            cogno_meet_agent_obj = CognoMeetAgent.objects.filter(
                user=user_obj).first()

            cogno_meet_io_obj = CognoMeetIO.objects.create(
                meeting_title=meeting_description,
                customer_name=full_name,
                customer_mobile=mobile_number,
                meeting_start_date=meeting_start_date,
                meeting_start_time=meeting_start_time,
                meeting_end_time=meeting_end_time,
                customer_email=email_id,
                meeting_status="scheduled",
                cogno_meet_access_token=cognomeet_access_token_obj,
                cogno_meet_agent=cogno_meet_agent_obj
            )

            # same as defautl being used
            if meeting_password != "":
                cogno_meet_io_obj.meeting_password = meeting_password
                cogno_meet_io_obj.save()

            server_details = cognomeet_access_token_obj.get_cognomeet_config_object()

            record_on_start = cognomeet_access_token_obj.enable_auto_recording

            # Meetint need to be closed
            HEADERS = {
                'Authorization': server_details.api_key,
                'Content-Type': 'application/json'
            }

            DATA = json.dumps(
                {'title': meeting_description, 'recordOnStart': record_on_start})

            URL = str(server_details.base_url) + \
                f'/organizations/{server_details.organization_id}/meeting'

            try:
                dyte_meeting_detail = requests.post(
                    url=URL, headers=HEADERS, data=DATA, timeout=server_details.api_timeout_time)

                status_code = int(dyte_meeting_detail.status_code)
                response_data = json.loads(dyte_meeting_detail.content)

                # success and status code
                if status_code == 200:
                    #
                    cogno_meet_io_obj.meeting_id = response_data["data"]["meeting"]["id"]
                    cogno_meet_io_obj.meeting_room_name = response_data["data"]["meeting"]["roomName"]
                    cogno_meet_io_obj.save()

                    meeting_url = str(settings.EASYCHAT_HOST_URL) + \
                        "/cogno-meet/meeting/" + \
                        str(cogno_meet_io_obj.session_id)

                    agent_name = cogno_meet_agent_obj.user.username
                    if cogno_meet_agent_obj.user.first_name != "":
                        agent_name = cogno_meet_agent_obj.user.first_name
                        if cogno_meet_agent_obj.user.last_name != "":
                            agent_name += " " + cogno_meet_agent_obj.user.last_name

                    start_time = cogno_meet_io_obj.meeting_start_time
                    start_time = datetime.strptime(start_time, "%H:%M").time()
                    start_time = start_time.strftime("%I:%M %p")
                    end_time = cogno_meet_io_obj.meeting_end_time
                    end_time = datetime.strptime(end_time, "%H:%M").time()
                    end_time = end_time.strftime("%I:%M %p")
                    meeting_date = datetime.strptime(cogno_meet_io_obj.meeting_start_date, '%Y-%m-%d')
                    meeting_date = meeting_date.strftime("%d %B, %Y")
                    join_password = ""
                    if meeting_password != "":
                        join_password = meeting_password
                    else:
                        join_password = 'No password required'

                    client_meeting_url = str(settings.EASYCHAT_HOST_URL) + \
                        "/cogno-meet/meeting/client/" + \
                        str(cogno_meet_io_obj.session_id)
                    
                    thread = threading.Thread(target=send_meeting_link_over_mail, args=(
                        email_id, full_name, client_meeting_url, agent_name, start_time, end_time, meeting_date, join_password), daemon=True)
                    thread.start()

                    response["status"] = 200
                    response["message"] = "success"
                    response["session_id"] = str(cogno_meet_io_obj.session_id)
                    response["video_link"] = meeting_url

            except Timeout as e:
                if cogno_meet_io_obj:
                    cogno_meet_io_obj.delete()
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Timeout GenerateCognoMeetMeetingAPI %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
                response["status"] = 504
                response["message"] = "Timeout"

            except Exception as e:
                if cogno_meet_io_obj:
                    cogno_meet_io_obj.delete()
                response["status"] = 301
                response["message"] = "Error while generating meeting"
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error GenerateCognoMeetMeetingAPI %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GenerateCognoMeetMeetingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GenerateCognoMeetMeeting = GenerateCognoMeetMeetingAPI.as_view()


def ScheduleMeet(request, session_id):
    try:        
        if not request.user.username:
            return redirect("/cogno-meet/meeting/client/" + str(session_id))
        cogno_meet_io = CognoMeetIO.objects.get(session_id=session_id)
        access_token = cogno_meet_io.cogno_meet_access_token
        server_details = access_token.get_cognomeet_config_object()

        is_waiting = True
        agent_note = None

        meeting_date = cogno_meet_io.meeting_start_date.strftime('%Y-%m-%d')
        meeting_start_time = cogno_meet_io.meeting_start_time.strftime(
            '%H:%M:%S')
        agent_name = 'Agent'
        customer_name = 'Customer'
        is_authicated = False
        org_id = str(server_details.organization_id)
        room_name = str(cogno_meet_io.meeting_room_name)
        screen_sharing = access_token.enable_screen_sharing
        lobby_page_enabled = access_token.show_lobby_page
        is_recording_on = access_token.enable_auto_recording
        is_agent = False
        is_invited_agent = False
        enable_screen_capture = access_token.enable_screen_capture
        enable_invite_agent = access_token.enable_invite_agent
        meeting_background_color = access_token.meeting_background_color
        allow_meeting_end_time = access_token.enable_time_duration
        is_meeting_expired = cogno_meet_io.is_meeting_expired

        config_obj = access_token.get_cognomeet_config_object()
        maximum_participants_limit = config_obj.maximum_participants_limit

        meeting_date_time = meeting_date + " " + meeting_start_time
        customer_name = cogno_meet_io.customer_name
        today = date.today()
        today = today.strftime('%Y-%m-%d')
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        if (meeting_date == today and meeting_start_time <= current_time) or meeting_date < today:
            is_waiting = False

        try:
            primary_agent_obj = cogno_meet_io.cogno_meet_agent
            primary_agent_username = primary_agent_obj.name()
            user_obj = User.objects.filter(username=request.user.username).first()
            request_cognomeet_agent = get_cognomeet_agent_from_request(request, CognoMeetAgent)
            if not request_cognomeet_agent and user_obj:
                request_cognomeet_agent = CognoMeetAgent.objects.create(
                    user=user_obj,
                    role='agent',
                    is_active=True,
                    is_account_active=True,
                    access_token=access_token
                )

            agent_name = request_cognomeet_agent.name()
            agent_full_name = get_agent_name_from_request(request)

            if primary_agent_obj == request_cognomeet_agent:
                is_agent = True
            else:
                is_invited_agent = True
        except Exception:
            is_agent = False

        # if is_agent:
        audit_trail = CognoMeetAuditTrail.objects.filter(
            cogno_meet_io=cogno_meet_io).first()

        if not audit_trail:
            audit_trail = CognoMeetAuditTrail.objects.create(
                cogno_meet_io=cogno_meet_io)

        if not (audit_trail.agent_joined_time or is_waiting):
            audit_trail.agent_joined_time = timezone.now()
            audit_trail.save()

        if audit_trail:
            agent_note = audit_trail.agent_notes

        return render(request, "CognoMeetApp/cogno_meet_agent.html", {
            'cogno_meet_io': cogno_meet_io,
            'meeting_date_time': meeting_date_time,
            'is_waiting': is_waiting,
            'is_agent': is_agent,
            'agent_name': agent_name,
            'customer_name': customer_name,
            'is_authicated': is_authicated,
            'org_id': org_id,
            'room_name': room_name,
            'screen_sharing': screen_sharing,
            'agent_note': agent_note,
            'lobby_page_enabled': lobby_page_enabled,
            'primary_agent_username': primary_agent_username,
            'is_recording_on': is_recording_on,
            'COGNOMEET_TAB_LOGO': DEFAULT_COGNOMEET_TAB_LOGO,
            'COGNOMEET_TITLE_TEXT': DEFAULT_COGNOMEET_TITLE_TEXT,
            'is_invited_agent': is_invited_agent,
            'enable_screen_capture': enable_screen_capture,
            'enable_invite_agent': enable_invite_agent,
            'meeting_background_color': meeting_background_color,
            'maximum_participants_limit': maximum_participants_limit,
            "allow_meeting_end_time": allow_meeting_end_time,
            "is_meeting_expired": is_meeting_expired,
            "agent_full_name": agent_full_name
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ScheduleMeet %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})


def ScheduleMeetClient(request, session_id):
    try:        
        permit_status = 'deny'
        if 'permit_status' in request.GET:
            permit_status = request.GET["permit_status"]

        is_external_user = False
        if 'external_user' in request.GET:
            external_user_value = request.GET["external_user"]
            if external_user_value == "true":
                is_external_user = True
        cogno_meet_io = CognoMeetIO.objects.get(session_id=session_id)
        if cogno_meet_io.is_meeting_expired:
            return redirect("/cogno-meet/meeting-end?session_id=" + str(session_id))

        access_token = cogno_meet_io.cogno_meet_access_token
        server_details = access_token.get_cognomeet_config_object()

        is_waiting = True
        # date
        meeting_data = cogno_meet_io.meeting_start_date.strftime('%Y-%m-%d')
        meeting_start_time = cogno_meet_io.meeting_start_time.strftime(
            '%H:%M:%S')
        agent_name = cogno_meet_io.cogno_meet_agent.user.username
        customer_name = 'Customer'
        is_authicated = False
        org_id = str(server_details.organization_id)
        room_name = str(cogno_meet_io.meeting_room_name)
        screen_sharing = access_token.enable_screen_sharing
        lobby_page_enabled = access_token.show_lobby_page
        is_recording_on = access_token.enable_auto_recording
        no_agent_permit_meeting_toast = access_token.no_agent_permit_meeting_toast
        no_agent_permit_meeting_toast_text = access_token.no_agent_permit_meeting_toast_text
        no_agent_permit_meeting_toast_time = access_token.no_agent_permit_meeting_toast_time
        meeting_background_color = access_token.meeting_background_color
        allow_meeting_end_time = access_token.enable_time_duration
        is_meeting_expired = cogno_meet_io.is_meeting_expired
        
        meeting_date_time = meeting_data + " " + meeting_start_time
        customer_name = cogno_meet_io.customer_name
        today = date.today()
        today = today.strftime('%Y-%m-%d')
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        if (meeting_data == today and meeting_start_time <= current_time) or meeting_data < today:
            is_waiting = False

        is_agent = False

        if is_external_user:
            customer_name = ""

        return render(request, "CognoMeetApp/cogno_meet_client.html", {
            'cogno_meet_io': cogno_meet_io,
            'meeting_date_time': meeting_date_time,
            'is_waiting': is_waiting,
            'is_agent': is_agent,
            'agent_name': agent_name,
            'customer_name': customer_name,
            'is_authicated': is_authicated,
            'org_id': org_id,
            'room_name': room_name,
            'screen_sharing': screen_sharing,
            'lobby_page_enabled': lobby_page_enabled,
            'permit_status': permit_status,
            'is_recording_on': is_recording_on,
            'COGNOMEET_TAB_LOGO': DEFAULT_COGNOMEET_TAB_LOGO,
            'COGNOMEET_TITLE_TEXT': DEFAULT_COGNOMEET_TITLE_TEXT,
            'no_agent_permit_meeting_toast': no_agent_permit_meeting_toast,
            'no_agent_permit_meeting_toast_text': no_agent_permit_meeting_toast_text,
            'no_agent_permit_meeting_toast_time': no_agent_permit_meeting_toast_time,
            'meeting_background_color': meeting_background_color,
            "is_external_user": is_external_user,
            'allow_meeting_end_time': allow_meeting_end_time,
            'is_meeting_expired': is_meeting_expired
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ScheduleMeet %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})


class CognoMeetAuthenticatePasswordAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = data["session_id"]
            password = data["password"]

            session_id = remo_html_from_string(session_id)
            password = remo_html_from_string(password)

            meeting_obj = CognoMeetIO.objects.filter(
                session_id=session_id, is_meeting_expired=False)
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
            logger.error("Error CognoMeetAuthenticatePasswordAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoMeetAuthenticatePassword = CognoMeetAuthenticatePasswordAPI.as_view()


class CognoMeetCreateParticipantAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            is_agent = remo_html_from_string(data["is_agent"])
            name = sanitize_input_string(data["name"])
            session_id = remo_html_from_string(data["session_id"])
            is_invited_agent = remo_html_from_string(data["is_invited_agent"])
            client_specific_id = sanitize_input_string(data["client_specific_id"])

            meeting_obj = CognoMeetIO.objects.get(session_id=session_id)
            acceess_token = meeting_obj.cogno_meet_access_token
            server_details = acceess_token.get_cognomeet_config_object()

            HEADERS = {
                'Authorization': server_details.api_key,
                'Content-Type': 'application/json'
            }
            DATA = None
            if (is_agent == 'True' or is_invited_agent == 'True'):

                agent_full_name = get_agent_name_from_request(request)

                DATA = json.dumps({
                    "clientSpecificId": client_specific_id,
                    "userDetails": {
                        "name": f"{agent_full_name}"
                    }
                })
            else:
                DATA = json.dumps({
                    "clientSpecificId": client_specific_id,
                    "userDetails": {
                        "name": f"{name}"
                    }
                })

            URL = str(server_details.base_url) + \
                f'/organizations/{server_details.organization_id}/meetings/{meeting_obj.meeting_id}/participant'

            added_participant_detail = requests.post(
                url=URL, headers=HEADERS, data=DATA, timeout=server_details.api_timeout_time)
            response_data = json.loads(added_participant_detail.content)

            is_success = str(response_data["success"])

            if is_success == 'True':
                #  add all field in create
                auth_token_obj = AuthTokenDetail.objects.create(
                    cogno_meet_io=meeting_obj)
                auth_token_obj.request_payload = DATA
                auth_token_obj.response_payload = response_data
                auth_token_obj.save()
                auth_token = str(
                    response_data["data"]["authResponse"]["authToken"])
                participant_id = str(
                    response_data["data"]["authResponse"]["id"])
                response["status"] = 200
                response["message"] = "success"
                response["participant_authToken"] = auth_token
                response["participant_id"] = participant_id
            else:
                response["status"] = 301
                response["message"] = "doesn't able to add participant"
                logger.error("Error CognoMeetCreateParticipantAPI doesn't able to add participant", extra={
                             'AppName': 'CognoMeet'})

        except Timeout as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Timeout CognoMeetCreateParticipantAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            response["status"] = 504
            response["message"] = "Timeout"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoMeetCreateParticipantAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoMeetCreateParticipant = CognoMeetCreateParticipantAPI.as_view()


class UploadCognoMeetFileAttachmentAPI(APIView):

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
            session_id = sanitize_input_string(data["session_id"])

            meeting_obj = CognoMeetIO.objects.get(session_id=session_id)

            access_token_obj = meeting_obj.cogno_meet_access_token

            file_extention = filename.replace(" ", "").split(".")[-1]
            file_extention = file_extention.lower()

            allowed_files_list = ["png", "jpg",
                                  "jpeg", "jpe", "pdf", "doc", "docx"]

            if file_extention not in allowed_files_list or check_malicious_file_from_filename(filename, allowed_files_list) or check_malicious_file_from_content(base64_data, allowed_files_list):
                response["status"] = 302
            else:
                file_upload_path = str(
                    COGNOMEETAPP_MEETING_FILES_PATH + f'/{session_id}')
                if not os.path.exists(file_upload_path):
                    os.makedirs(file_upload_path)

                file_name_without_extension = str(filename.rsplit('.', 1)[0])
                time_stamp = str(time.time())
                time_stamp = time_stamp.replace('.', '_')

                # For unique file name generation
                file_path = file_upload_path + "/" + file_name_without_extension + \
                    '_' + time_stamp + '.' + file_extention

                fh = open(file_path, "wb")
                fh.write(base64.b64decode(base64_data))
                fh.close()

                file_size = os.path.getsize(file_path) / (1024 * 1024)
                if file_size > 5.0:
                    response["status"] = 300
                    os.remove(file_path)
                    logger.info("UploadCognoMeetFileAttachmentAPI: File Size Exceeded, Max Allowed: 5MB", extra={
                                'AppName': 'CognoMeet'})
                else:
                    file_path = "/" + file_path

                    file_access_management_obj = CognoMeetFileAccessManagement.objects.create(
                        file_path=file_path, is_public=False, cogno_meet_access_token=access_token_obj, original_file_name=filename)

                    src = "/cogno-meet/download-file/" + \
                        str(file_access_management_obj.key)
                    response["status"] = 200
                    response["name"] = filename
                    response["src"] = src

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside UploadCognoMeetFileAttachmentAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            response["status"] = 500
            response["name"] = "no_name"
            response["src"] = "error"

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadCognoMeetFileAttachment = UploadCognoMeetFileAttachmentAPI.as_view()


def FileAccess(request, file_key):
    try:
        if request.user.is_authenticated:
            if check_access_token(request, file_key, CognoMeetAgent, CognoMeetFileAccessManagement):
                return file_download(file_key, CognoMeetFileAccessManagement)
        else:
            if "session_id" in request.GET:
                session_id = request.GET["session_id"]
                cognomeet_io = CognoMeetIO.objects.filter(
                    session_id=session_id).first()
                if not cognomeet_io:
                    return HttpResponse(status=404)
                if cognomeet_io.is_meeting_expired:
                    return HttpResponse(status=404)
                else:
                    return file_download(file_key, CognoMeetFileAccessManagement)

            file_access_management_obj = CognoMeetFileAccessManagement.objects.filter(
                key=file_key).first()

            if file_access_management_obj and not file_access_management_obj.is_obj_time_limit_exceeded():
                return file_download(file_key, CognoMeetFileAccessManagement)

        return HttpResponse(status=404)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error FileAccess %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
    return HttpResponse(status=404)


class CognoMeetMeetingNotesAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            session_id = data["session_id"]
            notes = data["notes"]
            # cehck for strip html and sanatize
            session_id = sanitize_input_string(session_id)
            notes = clean_html(notes)
            notes = remo_html_from_string(notes)
            notes = remo_special_tag_from_string(notes)

            meeting_obj = CognoMeetIO.objects.get(session_id=session_id)
            meeting_audit_trail = CognoMeetAuditTrail.objects.filter(
                cogno_meet_io=meeting_obj)
            if meeting_audit_trail:
                meeting_audit_trail[0].agent_notes = str(notes)
                meeting_audit_trail[0].save()
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoMeetMeetingNotesAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoMeetMeetingNotes = CognoMeetMeetingNotesAPI.as_view()


class SaveCognoMeetAppScreenshotAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            content = data["content"]
            session_id = data["session_id"]
            session_id = remo_html_from_string(session_id)

            meeting_obj = CognoMeetIO.objects.get(
                session_id=session_id)

            access_token_obj = meeting_obj.cogno_meet_access_token
            meeting_audit_trail = CognoMeetAuditTrail.objects.get(
                cogno_meet_io=meeting_obj)

            meeting_screenshot = json.loads(
                meeting_audit_trail.meeting_screenshorts_urls)

            format, imgstr = content.split(';base64,')
            ext = format.split('/')[-1]
            image_name = str(int(uuid.uuid4())) + "." + str(ext)

            file_upload_path = str(
                COGNOMEETAPP_MEETING_FILES_PATH + f'/{session_id}')
            if not os.path.exists(file_upload_path):
                os.makedirs(file_upload_path)

            file_path = file_upload_path + "/" + image_name
            # if get_save_in_s3_bucket_status():
            #     s3_bucket_upload_file_by_file_path(file_path, image_name)

            fh = open(file_path, "wb")
            fh.write(base64.b64decode(imgstr))
            fh.close()

            file_path = "/" + file_path

            file_access_management_obj = CognoMeetFileAccessManagement.objects.create(
                file_path=file_path, is_public=False, cogno_meet_access_token=access_token_obj,
                original_file_name='image.png')

            src = str(file_access_management_obj.key)

            meeting_screenshot["items"].append({
                "screenshot": src,
            })

            meeting_audit_trail.meeting_screenshorts_urls = json.dumps(
                meeting_screenshot)
            meeting_audit_trail.save()

            response["status"] = 200
            response["message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCognoMeetAppScreenshotAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCognoMeetAppScreenshot = SaveCognoMeetAppScreenshotAPI.as_view()


class SaveCognoMeetChatAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = sanitize_input_string(data["session_id"])
            cogno_meet_io = CognoMeetIO.objects.get(session_id=session_id)
            if cogno_meet_io.is_meeting_expired:
                response["status"] = 301
                response["message"] = "meeting expired"
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            sender = sanitize_input_string(data["sender"])
            message = sanitize_input_string(data["message"])
            attachment_file_name = sanitize_input_string(data["attachment_file_name"])
            sender_name = sanitize_input_string(data["sender_name"])
            attachment_link = sanitize_input_string(data["attachment_link"])
            is_file_attachment = sanitize_input_string(data["is_file_attachment"])
            dyte_participant_id = sanitize_input_string(data["dyte_participant_id"])
            cogno_meet_agent = None

            if(is_file_attachment):
                test_file_attached_name = attachment_file_name[:attachment_file_name.find(
                    '.')]
                reg_file = r'^[a-zA-Z0-9_ -]+$'

                if not re.fullmatch(reg_file, test_file_attached_name):
                    response["status"] = 301
                    response[
                        "message"] = "Please do not use special characters other than space( ), hiphen(-) and (_) underscore in file name"
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

            user_obj = User.objects.filter(username=sender_name).first()
            if user_obj:
                cogno_meet_agent = CognoMeetAgent.objects.get(user=user_obj)
                sender_name = ""

            if sender == 'invite_agent':
                sender = 'agent'

            if sender == "client":
                cogno_meet_agent = None
            if not is_file_attachment:
                attachment_file_name = None
                attachment_link = None

            if is_file_attachment:
                message = None

            CognoMeetChatHistory.objects.create(cogno_meet_io=cogno_meet_io,
                                                sender_name=cogno_meet_agent,
                                                sender=sender,
                                                message=message,
                                                attachment_file_name=attachment_file_name,
                                                attachment_file_path=attachment_link,
                                                sender_id=dyte_participant_id,
                                                external_participant_name=sender_name)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCognoMeetChatAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCognoMeetChat = SaveCognoMeetChatAPI.as_view()


class CognoMeetGetChatForSessionAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = sanitize_input_string(data["session_id"])

            meeting_obj = CognoMeetIO.objects.get(
                session_id=session_id)

            chat_history = CognoMeetChatHistory.objects.filter(
                cogno_meet_io=meeting_obj).order_by('datetime')

            client_agent_chats = []

            for message in chat_history:
                if message.sender_name:
                    client_agent_chats.append({
                        "sender": message.sender,
                        "sender_name": message.sender_name.user.username,
                        "message": message.message,
                        "time": message.datetime.strftime("%H:%M"),
                        "attachment_file_name": message.attachment_file_name,
                        "attachment_file_path": message.attachment_file_path,
                        "dyte_participant_id": message.sender_id,
                        "external_participant_name": message.external_participant_name,
                        "full_name": get_agent_name_from_user(message.sender_name.user)
                    })
                else:
                    client_agent_chats.append({
                        "sender": message.sender,
                        "sender_name": message.external_participant_name,
                        "message": message.message,
                        "time": message.datetime.strftime("%H:%M"),
                        "attachment_file_name": message.attachment_file_name,
                        "attachment_file_path": message.attachment_file_path,
                        "dyte_participant_id": message.sender_id,
                        "external_participant_name": message.external_participant_name,
                        "full_name": message.external_participant_name
                    })
            response['status'] = 200
            response["message_history"] = client_agent_chats

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoMeetGetChatForSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            response['status'] = 301
            response["message_history"] = []

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoMeetGetChatForSession = CognoMeetGetChatForSessionAPI.as_view()


def MeetingEnd(request):
    try:
        filled_feedback_page = False
        is_feedback_enabled = False
        is_kicked = False
        is_denied = False

        if 'session_id' in request.GET:
            session_id = request.GET["session_id"]
            session_id = sanitize_input_string(session_id)
        if 'filled_feedback_page' in request.GET:
            filled_feedback_page = request.GET["filled_feedback_page"]
            filled_feedback_page = remo_html_from_string(filled_feedback_page)
        if 'kicked' in request.GET:
            is_kicked = True
        if 'deny' in request.GET:
            is_denied = True

        cogno_meet_io = CognoMeetIO.objects.get(session_id=session_id)
        cogno_meet_accesstoken = cogno_meet_io.cogno_meet_access_token
        is_meeting_expired = cogno_meet_io.is_meeting_expired

        is_feedback_enabled = cogno_meet_accesstoken.enable_feedback_in_meeting

        return render(request, "CognoMeetApp/meet_end.html", {
            'cogno_meet_accesstoken': cogno_meet_accesstoken,
            'filled_feedback_page': filled_feedback_page,
            'is_feedback_enabled': is_feedback_enabled,
            'session_id': session_id,
            'is_kicked': is_kicked,
            'is_denied': is_denied,
            'COGNOMEET_TAB_LOGO': DEFAULT_COGNOMEET_TAB_LOGO,
            'COGNOMEET_TITLE_TEXT': DEFAULT_COGNOMEET_TITLE_TEXT,
            'is_meeting_expired': is_meeting_expired
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error MeetingEnd %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})


class UpdateFeedbackAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            client_comments = strip_html_tags(data["client_comments"])
            client_comments = remo_html_from_string(client_comments)
            agent_rating = strip_html_tags(data["agent_rating"])
            agent_rating = remo_html_from_string(agent_rating)
            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)

            cogno_meet_io = CognoMeetIO.objects.get(session_id=session_id)
            audit_trail = CognoMeetAuditTrail.objects.filter(
                cogno_meet_io=cogno_meet_io).first()

            if cogno_meet_io.is_meeting_expired:
                response["status"] = 301
                response["message"] = "Meeting has been expired."
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            if audit_trail.agent_rating == None:
                agent_rating = int(agent_rating)
                if agent_rating < 0 or agent_rating > 10:
                    response["status"] = 301
                    response["message"] = "Agent ratings cannot be less than 0 or greater than 10."
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                audit_trail.agent_rating = agent_rating
            
            if audit_trail.meeting_feedback_agent:
                response["status"] = 301
                response["message"] = "Feedback is already given."
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)
                
            audit_trail.meeting_feedback_agent = client_comments
            audit_trail.save()

            response["status"] = 200
            response["message"] = "success"

            logger.info("UpdateFeedbackAPI: CognoMeetAuditTrails details saved successfully", extra={
                'AppName': 'CognoMeet'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside UpdateFeedbackAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            response["status"] = 500
            response["message"] = "Error while saving audit trail details"

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateFeedback = UpdateFeedbackAPI.as_view()


class CognoMeetAuditTrailStatsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            cognomeet_access_token = sanitize_input_string(
                data["cogno_meet_access_token"])
            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                cognomeet_access_token, CognoMeetAccessToken)

            if not cognomeet_access_token_obj:
                return Response(data=get_invalid_access_token_response(custom_encrypt_obj, json))

            support_history_filters = None
            agents = None

            user_obj = User.objects.get(username=data["username"])

            if 'agents_list' in data:
                agents = data["agents_list"]

            if 'support_history_filters' in data:
                support_history_filters = data["support_history_filters"]

            cogno_meet_agent = CognoMeetAgent.objects.filter(
                user=user_obj).first()

            cogno_meet_agent_list = []
            for agent in agents:
                user_obj = User.objects.get(username=agent)
                cogno_meet_agent = CognoMeetAgent.objects.filter(
                    user=user_obj).first()
                if cogno_meet_agent:
                    cogno_meet_agent_list.append(cogno_meet_agent)

            cogno_meet_io = CognoMeetIO.objects.filter(
                cogno_meet_agent__in=cogno_meet_agent_list, cogno_meet_access_token=cognomeet_access_token_obj, is_meeting_expired=True)

            invited_agents_objs = CognoMeetInvitedAgentsDetails.objects.select_related(
                'cogno_meet_io').filter(support_agents_joined__in=cogno_meet_agent_list)
            if invited_agents_objs:
                invited_session_ids = []
                for invited_agent_details_obj in invited_agents_objs:
                    invited_session_ids.append(
                        invited_agent_details_obj.cogno_meet_io.session_id)

                cogno_meet_io |= CognoMeetIO.objects.filter(
                    session_id__in=invited_session_ids, cogno_meet_access_token=cognomeet_access_token_obj)

            # --------------- Filtering out ----------------
            if "startdate" in support_history_filters:
                date_format = "%d-%m-%Y"
                start_date = support_history_filters["startdate"]
                start_date = remo_html_from_string(start_date)
                datetime_start = datetime.strptime(
                    start_date, date_format).date()
                cogno_meet_io = cogno_meet_io.filter(
                    meeting_start_date__gte=datetime_start)

            if "enddate" in support_history_filters:
                date_format = "%d-%m-%Y"
                end_date = support_history_filters["enddate"]
                end_date = remo_html_from_string(end_date)
                datetime_end = datetime.strptime(
                    end_date, date_format).date()
                cogno_meet_io = cogno_meet_io.filter(
                    meeting_start_date__lte=datetime_end)

            if "agent" in support_history_filters:
                agent_email = support_history_filters["agent"]
                selected_agents = CognoMeetAgent.objects.filter(
                    user__username__in=agent_email)
                cogno_meet_io = cogno_meet_io.filter(
                    cogno_meet_agent__in=selected_agents)

            if "status" in support_history_filters:
                meeting_status = support_history_filters["status"]
                meeting_status = remo_html_from_string(meeting_status)
                if meeting_status == "Completed":
                    cogno_meet_io = cogno_meet_io.filter(
                        is_expired=True)
                elif meeting_status == "Scheduled":
                    cogno_meet_io = cogno_meet_io.filter(
                        is_expired=False)

            if "meeting_id" in support_history_filters:
                meeting_id = support_history_filters["meeting_id"]
                meeting_id = remo_html_from_string(meeting_id)
                cogno_meet_io = cogno_meet_io.filter(
                    session_id=meeting_id)

            audit_trails = CognoMeetAuditTrail.objects.filter(
                cogno_meet_io__in=cogno_meet_io).order_by('-pk')

            # pagination -
            chat_history = CognoMeetChatHistory.objects.filter(
                cogno_meet_io__in=cogno_meet_io)
            totoal_requested_data = len(audit_trails)
            page_number = int(data["page_number"])
            total_request_io_objs, paginate_request_data, start_point, end_point = paginate(
                audit_trails, 20, page_number)

            meeting_history = parse_request_io_data(
                paginate_request_data, chat_history)

            response['pagination_data'] = get_pagination_data(
                paginate_request_data)
            response["totoal_requested_data"] = totoal_requested_data
            response["start_point"] = start_point
            response["end_point"] = end_point
            response['status'] = 200
            response["meeting_history"] = meeting_history

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoMeetAuditTrailStatsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            response['status'] = 301
            response["meeting_history"] = []

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoMeetAuditTrailStats = CognoMeetAuditTrailStatsAPI.as_view()


class DownloadSessionRecordingAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['message'] = "Some error occurred, please try again"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cognomeet_access_token = sanitize_input_string(
                data["cognomeet_access_token"])
            session_id = sanitize_input_string(data["session_id"])

            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                cognomeet_access_token, CognoMeetAccessToken)

            if not cognomeet_access_token_obj:
                return Response(data=get_invalid_access_token_response(custom_encrypt_obj, json))

            cognomeet_io_obj = CognoMeetIO.objects.filter(
                session_id=session_id).first()

            if cognomeet_io_obj:
                cognomeet_audit_trail = CognoMeetAuditTrail.objects.filter(
                    cogno_meet_io=cognomeet_io_obj).first()
                if not cognomeet_audit_trail:
                    response['message'] = "No recording is available for this session"

                elif not cognomeet_io_obj.is_meeting_recording_fetched:
                    response['message'] = "Recording will be available after 24 hours of session end time"

                elif cognomeet_io_obj.is_meeting_recording_fetched:
                    # for now multiple recordings are not there. Once they are added, logic would have to be changed
                    recording_obj = cognomeet_audit_trail.cogno_meet_recording.all().first()
                    if recording_obj and recording_obj.file_access_management:
                        export_path = "cogno-meet/download-file/" + \
                            str(recording_obj.file_access_management.key)

                        response['export_path'] = export_path
                        response['message'] = "success"
                        response['status'] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DownloadSessionRecordingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DownloadSessionRecording = DownloadSessionRecordingAPI.as_view()


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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


LoadMapScript = LoadMapScriptAPI.as_view()


class SaveClientLocationDetailsAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = data["session_id"]
            client_name = data["client_name"]
            longitude = data["longitude"]
            latitude = data["latitude"]
            client_address = data["client_address"]

            session_id = remo_html_from_string(session_id)
            client_name = remo_html_from_string(client_name)
            client_name = remo_special_tag_from_string(client_name)
            longitude = remo_html_from_string(str(longitude))
            latitude = remo_html_from_string(str(latitude))
            client_address = remo_html_from_string(client_address)
            client_address = remo_special_tag_from_string(client_address)

            meeting_obj = CognoMeetIO.objects.get(
                session_id=session_id)

            meeting_audit_trail = CognoMeetAuditTrail.objects.get(
                cogno_meet_io=meeting_obj)

            client_location_details = json.loads(
                meeting_audit_trail.customer_location_details)

            client_location_details["items"].append({
                "client_name": client_name,
                "longitude": str(longitude),
                "latitude": str(latitude),
                "address": client_address,
            })
            meeting_audit_trail.customer_location_details = json.dumps(
                client_location_details)
            meeting_audit_trail.save()

            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveClientLocationDetailsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            response["status"] = 500

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveClientLocationDetails = SaveClientLocationDetailsAPI.as_view()


class EndCognoMeetMeetingAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = data["session_id"]
            session_id = remo_html_from_string(session_id)

            meeting_obj = CognoMeetIO.objects.get(
                session_id=session_id)            

            meeting_audit_trail = CognoMeetAuditTrail.objects.get(
                cogno_meet_io=meeting_obj)

            meeting_obj.is_meeting_expired = True
            meeting_obj.save()
            access_token = meeting_obj.cogno_meet_access_token
            server_details = access_token.get_cognomeet_config_object()

            # closing the meeting
            HEADERS = {
                'Authorization': server_details.api_key,
                'Content-Type': 'application/json'
            }

            DATA = json.dumps({'status': 'CLOSED'})

            URL = str(server_details.base_url) + \
                f'/organizations/{server_details.organization_id}/meetings/{meeting_obj.meeting_id}'

            try:                
                dyte_meeting_detail = requests.put(
                    url=URL, headers=HEADERS, data=DATA, timeout=server_details.api_timeout_time)

                status_code = int(dyte_meeting_detail.status_code)
                response_data = json.loads(dyte_meeting_detail.content)

                # success and status code
                if status_code == 200:

                    # Updateing meeting stats
                    HEADERS = {
                        'Authorization': server_details.api_key,
                        'Content-Type': 'application/json'
                    }

                    DATA = json.dumps({})

                    URL = str(server_details.base_url) + \
                        f'/organizations/{server_details.organization_id}/meetings/{meeting_obj.meeting_id}/analytics'

                    dyte_meeting_detail = requests.get(
                        url=URL, headers=HEADERS, data=DATA, timeout=server_details.api_timeout_time)

                    status_code = int(dyte_meeting_detail.status_code)
                    response_data = json.loads(dyte_meeting_detail.content)

                    if status_code == 200:
                        meeting_analytics = response_data["analytics"]
                        if len(meeting_analytics):
                            min_time = None
                            max_time = None
                            for data in meeting_analytics:
                                for participat_specific_data in data["events"]:
                                    if min_time == None or max_time == None:
                                        min_time = parse(
                                            participat_specific_data["time"])
                                        max_time = parse(
                                            participat_specific_data["time"])
                                    else:
                                        parsed_time = parse(
                                            participat_specific_data["time"])
                                        if(parsed_time < min_time):
                                            min_time = parsed_time
                                        if(parsed_time > max_time):
                                            max_time = parsed_time

                            time_diff = max_time - min_time
                            actul_start_end_time_obj = MeetingActualStartEndTime.objects.create(
                                start_time=min_time, end_time=max_time, cogno_meet_io=meeting_obj)
                            actul_start_end_time_obj.save()
                            meeting_audit_trail.total_call_duration = (
                                time_diff.seconds + time_diff.microseconds / 1000000)
                            meeting_audit_trail.save()

                            response["status"] = 200
                            response["message"] = "success"
                else:
                    response["status"] = 301
                    response["message"] = "Error while closing meeting"

            except Timeout as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Timeout EndCognoMeetMeetingAPI %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
                response["status"] = 504
                response["message"] = "Timeout"
            except Exception as e:
                response_data = json.loads(dyte_meeting_detail.content)
                response["status"] = 301
                response["message"] = "Error while closing meeting"
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error(f'Error while closing Dyte meeting: {response_data}', '%s at %s', str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside EndCognoMeetMeetingAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            response["status"] = 500

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


EndCognoMeetMeeting = EndCognoMeetMeetingAPI.as_view()


class ExportMeetingSupportHistoryAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response["export_path"] = "None"
        response["export_path_exist"] = False
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            requested_data = json.loads(data)
            agents_list = None
            is_custom_date_range_requirement = False

            cognomeet_access_token = sanitize_input_string(
                requested_data["cognomeet_access_token"])
            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                cognomeet_access_token, CognoMeetAccessToken)

            if not cognomeet_access_token_obj:
                return Response(data=get_invalid_access_token_response(custom_encrypt_obj, json))

            cogno_meet_agent = get_cognomeet_agent_from_request(request, CognoMeetAgent)

            if cogno_meet_agent.role == "agent":
                response["export_path"] = "None"
                response["status"] = 401
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            if 'agents_list' in requested_data:
                agents_list = requested_data["agents_list"]
            
            cogno_meet_agent_list = CognoMeetAgent.objects.filter(
                user__username__in=agents_list)
            
            if requested_data["selected_filter_value"] == "1":
                requested_data_date_range = get_requested_data_for_daily()
                
            elif requested_data["selected_filter_value"] == "2":
                requested_data_date_range = get_requested_data_for_week()
                
            elif requested_data["selected_filter_value"] == "3":
                requested_data_date_range = get_requested_data_for_month()
                
            elif requested_data["selected_filter_value"] == "4":
                is_custom_date_range_requirement = True
                requested_data_date_range = {
                    "startdate": requested_data["startdate"],
                    "enddate": requested_data["enddate"]
                }
            
            export_path = None
            start_date = requested_data_date_range["startdate"]
            end_date = requested_data_date_range["enddate"]

            date_format = DATE_TIME_FORMAT

            start_date = datetime.strptime(start_date, date_format).date()
            end_date = datetime.strptime(end_date, date_format).date()

            cognomeet_io_objs = CognoMeetIO.objects.filter(
                cogno_meet_agent__in=cogno_meet_agent_list, meeting_start_date__gte=start_date, meeting_start_date__lte=end_date, is_meeting_expired=True)              
            
            audit_trail_objs = CognoMeetAuditTrail.objects.filter(
                cogno_meet_io__in=cognomeet_io_objs)
            
            if audit_trail_objs.count() > REPORT_GENERATION_CAP:
                create_export_data_request_obj(cogno_meet_agent, "meeting-support-history", json.dumps(requested_data), CognoMeetExportDataRequest)
                response["status"] = 301
                if is_custom_date_range_requirement:
                    response["message"] = "The requested report would be sent to the entered email IDs within the next 1 hour."
                else:
                    response["message"] = "Your requested report would be sent to you over your email ID in the next 1 hour."
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)        
            else:
                export_path = get_custom_meeting_support_history(
                    cognomeet_access_token_obj, requested_data_date_range, cogno_meet_agent, CognoMeetIO, CognoMeetAuditTrail, CognoMeetFileAccessManagement, cogno_meet_agent_list, audit_trail_objs)

            if export_path and os.path.exists(export_path):

                response["export_path_exist"] = True
                file_path = "/" + export_path

                file_access_management_key = create_file_access_management_obj(
                    CognoMeetFileAccessManagement, cognomeet_access_token_obj, file_path)
                response["export_path"] = 'cogno-meet/download-file/' + \
                    file_access_management_key
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportMeetingSupportHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportMeetingSupportHistory = ExportMeetingSupportHistoryAPI.as_view()


class CognoMeetMeetingViewDataAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)            

            # user_name = remo_html_from_string(data["username"])
            cognomeet_access_token = remo_html_from_string(
                data["cogno_meet_access_token"])
            # user_obj = User.objects.filter(username=user_name).first()
            cogno_meet_agent_list = data["agents_list"]

            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                cognomeet_access_token, CognoMeetAccessToken)
            if not cognomeet_access_token_obj:
                return Response(data=get_invalid_access_token_response(custom_encrypt_obj, json))
            
            cognomeet_agents_objs = CognoMeetAgent.objects.filter(
                user__username__in=cogno_meet_agent_list)

            cogno_meet_io = CognoMeetIO.objects.filter(cogno_meet_access_token=cognomeet_access_token_obj,
                                                       cogno_meet_agent__in=cognomeet_agents_objs, is_meeting_expired=False).order_by('-meeting_start_date')
            cogno_meet_io_support = CognoMeetIO.objects.filter(cogno_meet_access_token=cognomeet_access_token_obj,
                                                               support_meeting_agents__in=cognomeet_agents_objs, is_meeting_expired=False).order_by('-meeting_start_date')
            cogno_meet_objs = cogno_meet_io | cogno_meet_io_support

            if 'today_data' in data:
                current_date = datetime.now().date()
                cogno_meet_objs = cogno_meet_objs.filter(meeting_start_date=current_date).order_by(
                    '-meeting_start_time')
                response["status"] = 200
                response["message"] = "success"
                response["meeting_list"] = get_todays_meeting_data(
                    cogno_meet_objs)

            else:
                # pagination -

                totoal_requested_data = len(cogno_meet_objs)
                page_number = int(data["page_number"])
                total_request_io_objs, paginate_request_data, start_point, end_point = paginate(
                    cogno_meet_objs, 20, page_number)

                meeting_data = parse_meeting_data(
                    paginate_request_data)

                response['pagination_data'] = get_pagination_data(
                    paginate_request_data)
                response["totoal_requested_data"] = totoal_requested_data
                response["start_point"] = start_point
                response["end_point"] = end_point
                response['status'] = 200
                response['meeting_agent_data'] = meeting_data

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoMeetMeetingViewDataAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            response['status'] = 301
            response["meeting_history"] = []

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoMeetMeetingViewData = CognoMeetMeetingViewDataAPI.as_view()


class UpdateCognoMeetAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            meeting_id = sanitize_input_string(data["meeting_id"])
            meeting_io = CognoMeetIO.objects.filter(
                session_id=meeting_id)

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

                # user_obj = User.objects.get(username=request.user.username)
                # cogno_meet_agent = CognoMeetAgent.objects.get(user=user_obj)

                meeting_io.customer_name = full_name
                meeting_io.customer_mobile = mobile_number
                meeting_io.customer_email = email_id
                # meeting_io.agent = cobrowse_agent
                meeting_io.meeting_title = str(meeting_description)
                meeting_io.meeting_start_date = meeting_start_date.replace(
                    '/', '-')
                meeting_io.meeting_start_time = meeting_start_time
                meeting_io.meeting_end_time = meeting_end_time
                meeting_io.is_meeting_expired = False
                meeting_io.meeting_password = meeting_password
                meeting_io.save()

                meeting_agent_obj = meeting_io.cogno_meet_agent
                agent_name = meeting_agent_obj.user.username
                if meeting_agent_obj.user.first_name != "":
                    agent_name = meeting_agent_obj.user.first_name
                    if meeting_agent_obj.user.last_name != "":
                        agent_name += " " + meeting_agent_obj.user.last_name
                            
                start_time = meeting_io.meeting_start_time
                start_time = datetime.strptime(start_time, "%H:%M").time()
                start_time = start_time.strftime("%I:%M %p")
                end_time = meeting_io.meeting_end_time
                end_time = datetime.strptime(end_time, "%H:%M").time()
                end_time = end_time.strftime("%I:%M %p")
                meeting_date = datetime.strptime(meeting_io.meeting_start_date, '%Y-%m-%d')
                meeting_date = meeting_date.strftime("%d %B, %Y")
                join_password = ""
                if meeting_password != "":
                    join_password = meeting_password
                else:
                    join_password = 'No password required'

                client_meeting_url = str(settings.EASYCHAT_HOST_URL) + \
                        "/cogno-meet/meeting/client/" + \
                        str(meeting_io.session_id)

                thread = threading.Thread(target=send_meeting_link_over_mail, args=(
                    email_id, full_name, client_meeting_url, agent_name, start_time, end_time, meeting_date, join_password), daemon=True)
                thread.start()
                response["status"] = 200
                response["message"] = "success"
            else:
                response["status"] = 301
                response["message"] = "No meeting found."
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateCognoMeetAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateCognoMeet = UpdateCognoMeetAPI.as_view()


class AssignCognoMeetAgentAPI(APIView):

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
            agent_name = strip_html_tags(data["agent_name"])
            access_token_obj = strip_html_tags(data["access_token"])

            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                access_token_obj, CognoMeetAccessToken)
            if not cognomeet_access_token_obj:
                return Response(data=get_invalid_access_token_response(custom_encrypt_obj, json))

            meeting_io = CognoMeetIO.objects.filter(
                session_id=meeting_id)

            if meeting_io:
                meeting_io = meeting_io[0]
                user_obj = User.objects.get(username=agent_name)
                cogno_meet_agent = CognoMeetAgent.objects.filter(
                    user=user_obj).first()
                if not cogno_meet_agent:
                    cogno_meet_agent = CognoMeetAgent.objects.create(
                        user=user_obj,
                        role='agent',
                        is_active=True,
                        is_account_active=True,
                        access_token=cognomeet_access_token_obj
                    )

                meeting_io.cogno_meet_agent = cogno_meet_agent
                meeting_io.save()

                response["status"] = 200
                response["message"] = "success"
                response["product_name"] = 'CognoMeetApp'
            else:
                response["status"] = 301
                response["message"] = "No meeting found."
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AssignCognoMeetAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AssignCognoMeetAgent = AssignCognoMeetAgentAPI.as_view()


class InviteCognoMeetOverEmailAPI(APIView):

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
            session_id = strip_html_tags(data["session_id"])
            meeting_url = str(settings.EASYCHAT_HOST_URL) + "/cogno-meet/meeting/client/" + \
                str(session_id) + "?external_user=true"
            user_obj = User.objects.get(username=request.user.username)
            cogno_meet_agent = CognoMeetAgent.objects.get(user=user_obj)

            meeting_io = CognoMeetIO.objects.get(
                session_id=session_id)
            agent_name = cogno_meet_agent.user.username
            start_time = meeting_io.meeting_start_time
            start_time = start_time.strftime("%I:%M %p")
            meeting_date = meeting_io.meeting_start_date
            meeting_date = meeting_date.strftime("%d %B, %Y")
            join_password = ""
            if meeting_io.meeting_password != "" and meeting_io.meeting_password != None:
                join_password = meeting_io.meeting_password
            else:
                join_password = 'No password required'

            for email_id in email_ids:
                email_id = sanitize_input_string(email_id)
                email_id = email_id.strip()
                if email_id != "" and (not is_email_valid(email_id)):
                    response["status"] = 500
                    response["message"] = "invalid emailId"
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(
                        response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

                thread = threading.Thread(target=send_invite_link_over_mail, args=(
                    email_id, meeting_url, agent_name, str(start_time), str(meeting_date), join_password), daemon=True)
                thread.start()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error InviteCognoMeetOverEmailAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


InviteCognoMeetOverEmail = InviteCognoMeetOverEmailAPI.as_view()


class SetInvitedAgentForMeetingAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            session_id = sanitize_input_string(data["session_id"])
            invited_agent_name = sanitize_input_string(
                data["invited_agent_name"])

            meeting_io = CognoMeetIO.objects.filter(
                session_id=session_id).first()

            user_obj = User.objects.get(username=invited_agent_name)
            cogno_meet_agent = CognoMeetAgent.objects.filter(
                user=user_obj).first()
            if not cogno_meet_agent:
                cogno_meet_agent = CognoMeetAgent.objects.create(
                    user=user_obj,
                    role='agent',
                    is_active=True,
                    is_account_active=True,
                    access_token=meeting_io.cogno_meet_access_token
                )

            invite_agent_details_obj = CognoMeetInvitedAgentsDetails.objects.filter(
                cogno_meet_io=meeting_io).first()
            if not invite_agent_details_obj:
                invite_agent_details_obj = CognoMeetInvitedAgentsDetails.objects.create(
                    cogno_meet_io=meeting_io)

            invite_agent_details_obj.support_agents_invited.add(
                cogno_meet_agent)
            meeting_io.support_meeting_agents.add(cogno_meet_agent)
            invite_agent_details_obj.save()
            meeting_io.save()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SetInvitedAgentForMeetingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SetInvitedAgentForMeeting = SetInvitedAgentForMeetingAPI.as_view()


class CognoMeetSupportAgentJoinedAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            session_id = sanitize_input_string(data["session_id"])
            # agent_name = strip_html_tags(data["agent_name"])

            meeting_io = CognoMeetIO.objects.filter(
                session_id=session_id).first()
            invite_agent_details_obj = CognoMeetInvitedAgentsDetails.objects.filter(
                cogno_meet_io=meeting_io).first()
            cogno_meet_agent = CognoMeetAgent.objects.get(
                user__username=request.user.username)
            invite_agent_details_obj.support_agents_joined.add(
                cogno_meet_agent)
            invite_agent_details_obj.save()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CognoMeetSupportAgentJoinedAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CognoMeetSupportAgentJoined = CognoMeetSupportAgentJoinedAPI.as_view()


class UpdateAgentSessionStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = sanitize_input_string(data["session_id"])

            cognomeet_io_obj = CognoMeetIO.objects.filter(
                session_id=session_id).first()

            if cognomeet_io_obj:
                cognomeet_io_obj.agent_update_datetime = timezone.now()
                cognomeet_io_obj.save()

                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateAgentSessionStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateAgentSessionStatus = UpdateAgentSessionStatusAPI.as_view()


class UpdateCustomerSessionStatusAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = sanitize_input_string(data["session_id"])

            cognomeet_io_obj = CognoMeetIO.objects.filter(
                session_id=session_id).first()

            if cognomeet_io_obj:
                cognomeet_io_obj.customer_update_datetime = timezone.now()
                cognomeet_io_obj.save()

                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateCustomerSessionStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateCustomerSessionStatus = UpdateCustomerSessionStatusAPI.as_view()


class CheckMeetingEndedOrNotAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = sanitize_input_string(data["session_id"])
            meeting_io = CognoMeetIO.objects.get(
                session_id=session_id)
            access_token_obj = meeting_io.cogno_meet_access_token
            if access_token_obj.enable_time_duration:
                meeting_end_time = access_token_obj.max_time_duration
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
                    meeting_io.is_meeting_expired = True
                    meeting_io.save()
                    response["status"] = 200
                    response["message"] = 'success'
            else:
                response["status"] = 400
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckMeetingEndedOrNotAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckMeetingEndedOrNot = CheckMeetingEndedOrNotAPI.as_view()


class CreateOrUpdateCognoMeetAgentAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            access_token = strip_html_tags(data["cogno_meet_access_token"])
            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                access_token, CognoMeetAccessToken)
            if not cognomeet_access_token_obj:
                return Response(data=get_invalid_access_token_response(custom_encrypt_obj, json))

            agent_role = sanitize_input_string(data["agent_role"])
            agent = get_cognomeet_agent_from_request(request, CognoMeetAgent)
            if not agent:
                agent = CognoMeetAgent.objects.create(
                    user=request.user,
                    role=agent_role,
                    is_active=True,
                    is_account_active=True,
                    access_token=cognomeet_access_token_obj
                )
            # admin is not being converted to agent
            elif agent.role != 'admin' and (agent_role != agent.role):
                agent.role = agent_role
                agent.save()

            response["status"] = 200
            response["message"] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CreateOrUpdateCognoMeetAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CreateOrUpdateCognoMeetAgent = CreateOrUpdateCognoMeetAgentAPI.as_view()


class CheckParticipantLimitAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            session_id = strip_html_tags(data["session_id"])
            
            meeting_io_obj = CognoMeetIO.objects.filter(
                session_id=session_id).first()
            
            if meeting_io_obj:

                """
                The below code is written to handle the condition of not checking the participant
                count when no one has joined the meeting. The reason for this is that Dyte returns 
                and status of 404 and a message of "No active session found for meeting id"
                """
                if not meeting_io_obj.agent_update_datetime and \
                        not meeting_io_obj.customer_update_datetime:
                    response["status"] = 200
                    response["message"] = "success"
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                
                total_participants_count = get_dyte_meeting_total_participants(meeting_io_obj)

                if total_participants_count == None:
                    response["status"] = 301
                    response["message"] = "An error occurred while getting total participant count"
                    logger.error("Error CheckParticipantLimitAPI: an error occurred while getting max participant count", 
                                    extra={'AppName': 'CognoMeet'})
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

                cognomeet_access_token_obj = meeting_io_obj.cogno_meet_access_token
                config_obj = cognomeet_access_token_obj.get_cognomeet_config_object()
                
                if total_participants_count >= config_obj.maximum_participants_limit:
                    response["status"] = 302
                    response["message"] = "Sorry, you are not allowed to join the call as maximum participant limit has been reached."
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckParticipantLimitAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckParticipantLimit = CheckParticipantLimitAPI.as_view()
