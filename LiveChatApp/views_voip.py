import os
import sys
import json
import uuid
from django import conf
import xlrd
import pytz
import random
import logging
import datetime
import mimetypes
import urllib.parse

# Django REST framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# Django imports
from django.db.models import Q
from django.http import FileResponse
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, HttpResponseRedirect

from EasyChat import settings
from EasyChatApp.utils import *
from LiveChatApp.utils import *
from LiveChatApp.models import *
from LiveChatApp.constants import *
from LiveChatApp.utils_voip import get_call_type
from LiveChatApp.views_calender import *
from LiveChatApp.views_email_profile import *
from EasyChatApp.utils_google_buisness_messages import *
from EasyChatApp.utils_facebook import send_facebook_message, send_facebook_livechat_agent_response
from LiveChatApp.views_analytics import *
from LiveChatApp.views_internal_chat import *
from LiveChatApp.views_agent import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils_validation import LiveChatFileValidation


User = get_user_model()
IST = pytz.timezone("Asia/Kolkata")

# Logger
logger = logging.getLogger(__name__)

ensure_element_tree(xlrd)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


def LiveChatVoiceMeeting(request):  # noqa: N802
    try:
        if request.user.is_authenticated:

            meeting_id = request.GET['meeting_id']
            session_id = request.GET['session_id']

            meeting_obj = LiveChatVoIPData.objects.filter(
                meeting_id=meeting_id)

            if meeting_obj and not meeting_obj[0].is_completed:
                meeting_obj = meeting_obj.first()
                customer_obj = meeting_obj.customer
                bot_obj = customer_obj.bot

                config_obj = LiveChatConfig.objects.get(bot=bot_obj)
                meeting_domain = config_obj.meeting_domain

                if str(customer_obj.session_id) == session_id and not customer_obj.is_session_exp:
                    agent = meeting_obj.agent

                    return render(request, 'LiveChatApp/voice_meeting.html', {
                        "meeting_id": meeting_id,
                        "session_id": session_id,
                        "display_name": agent.get_agent_name(),
                        "meeting_domain": meeting_domain,
                    })

            return render(request, "LiveChatApp/meeting_end.html", {})
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AuditTrail ! %s %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return render(request, 'LiveChatApp/error_500.html')


def LiveChatVoIPMeetingEnded(request):
    try:
        return render(request, "LiveChatApp/meeting_end.html", {})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error VoIPMeetingEnded %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return HttpResponse(status=401)


class ManageVoIPRequestAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal server error!"

        try:

            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            livechat_session_id = data['livechat_session_id']
            request_raised_by = data['request_raised_by']
            request_type = data['request_type']

            customer_obj = LiveChatCustomer.objects.filter(
                session_id=livechat_session_id)

            if customer_obj:
                customer_obj = customer_obj.first()
                agent_obj = customer_obj.agent_id

                call_type = get_call_type(agent_obj, LiveChatConfig)

                if request_type == 'initiated':
                    voip_obj = LiveChatVoIPData.objects.create(
                        call_type=call_type,
                        customer=customer_obj,
                        agent=agent_obj,
                        initiated_by=request_raised_by,
                        call_recording=json.dumps({"items": []}))
                    
                    if customer_obj.is_external:
                        extra_details = {
                            'message': f'{settings.EASYCHAT_HOST_URL}/chat/customer-voice-meeting/?meeting_id={str(voip_obj.meeting_id)}&session_id={livechat_session_id}'
                        }

                        push_livechat_event(SEND_MESSAGE_EVENT, customer_obj, extra_details)

                elif request_type in ['accepted', 'rejected', 'started', 'interrupted']:
                    meeting_id = data['meeting_id']

                    voip_obj = LiveChatVoIPData.objects.filter(
                        meeting_id=meeting_id)

                    if voip_obj:
                        voip_obj = voip_obj.first()

                        if request_type == 'accepted':
                            voip_obj.is_accepted = True
                        elif request_type == 'rejected':
                            voip_obj.is_rejected = True
                        elif request_type == 'started':
                            if voip_obj.call_type == 'video_call':
                                sender_name = str(agent_obj.user.first_name) + " " + str(agent_obj.user.last_name)

                                customer_language = customer_obj.customer_language
                                bot_template_obj = None
                                if customer_language and customer_language.lang != 'en':
                                    bot_template_obj = RequiredBotTemplate.objects.get(bot=customer_obj.bot, language=customer_language)

                                if voip_obj.initiated_by == 'agent':
                                    if bot_template_obj:
                                        text_message = bot_template_obj.livechat_vc_notifications.split('$$$')[3]
                                    else:
                                        text_message = "Please join the following link for video call:"
                                else:
                                    if bot_template_obj:
                                        text_message = bot_template_obj.livechat_vc_notifications.split('$$$')[4]
                                    else:
                                        text_message = "Agent has accepted the request. Please join the following link:"
                                
                                LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                                                    sender="Agent",
                                                                    sender_name=sender_name,
                                                                    text_message=text_message,
                                                                    message_time=timezone.now(),
                                                                    meeting_link=f'{settings.EASYCHAT_HOST_URL}/livechat/meeting/{str(voip_obj.meeting_id)}',
                                                                    is_video_call_message=True,
                                                                    message_for='customer')
                            voip_obj.is_started = True
                            voip_obj.start_datetime = timezone.now()
                        else:
                            voip_obj.is_interrupted = True
                            voip_obj.is_completed = True

                        voip_obj.save()
                    else:
                        response["message"] = 'Meeting does not exist.'
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)

                response['meeting_id'] = str(voip_obj.meeting_id)
                response['status'] = 200
                response['message'] = 'success'

            else:
                response["message"] = 'LiveChat Customer does not exist.'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside ManageVoIPRequestAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ManageVoIPRequest = ManageVoIPRequestAPI.as_view()


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

            validation_obj = EasyChatInputValidation()
            file_validation_obj = LiveChatFileValidation()

            filename = validation_obj.remo_html_from_string(filename)
            filename = validation_obj.sanitize_html(filename)
            
            meeting_id = validation_obj.remo_html_from_string(meeting_id)
            meeting_id = validation_obj.sanitize_html(meeting_id)

            if not os.path.exists('secured_files/LiveChatApp/voice_calls'):
                os.makedirs('secured_files/LiveChatApp/voice_calls/')
            
            allowed_file_list = ['webm', 'bin']
            is_valid = True
            if file_validation_obj.check_malicious_file_from_filename(filename, allowed_file_list):
                is_valid = False
            
            if is_valid and file_validation_obj.check_malicious_file_from_content(base64.b64encode(uploaded_file.read()), allowed_file_list):
                is_valid = False

            if not is_valid:
                response['status'] = 500
                response['message'] = 'Invalid file'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            file_path = "secured_files/LiveChatApp/voice_calls/" + filename

            media_file = open(file_path, "ab+")
            uploaded_file.seek(0)
            media_file.write(uploaded_file.read())
            media_file.close()

            file_path = "/" + file_path

            is_recording_present = False

            if(LiveChatFileAccessManagement.objects.filter(file_path=file_path, is_public=False).count() > 0):
                is_recording_present = True
            else:
                LiveChatFileAccessManagement.objects.create(
                    file_path=file_path, is_public=False)

            meeting_obj = LiveChatVoIPData.objects.get(
                meeting_id=meeting_id)

            client_audio_file = json.loads(
                meeting_obj.call_recording)

            if is_recording_present:
                logger.info("File already present in the list",
                            extra={'AppName': 'LiveChat'})
            else:
                client_audio_file['items'].append({
                    "time_stamp": str(time_stamp), 
                    "path": str(file_path)
                })

                meeting_obj.call_recording = json.dumps(
                    client_audio_file)

                meeting_obj.save()

            response["status"] = 200
            response["name"] = filename
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveClientRecordedDataAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status"] = 500
            response["name"] = "no_name"
            response["src"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveClientRecordedData = SaveClientRecordedDataAPI.as_view()


class SaveVoipMeetingDurationAPI(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            meeting_id = data["meeting_id"]
            meeting_id = remo_html_from_string(meeting_id)

            meeting_obj = LiveChatVoIPData.objects.filter(
                meeting_id=meeting_id, is_completed=False)

            if meeting_obj and meeting_obj.first().agent.user == request.user:
                meeting_obj = meeting_obj.first()
                meeting_obj.end_datetime = timezone.now()
                meeting_obj.is_completed = True
                meeting_obj.save()
                if meeting_obj.call_type == 'pip' or meeting_obj.call_type == 'new_tab':
                    send_event_for_voice_call_history(meeting_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)
                if meeting_obj.call_type == 'video_call':
                    send_event_for_video_call_history(meeting_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveVoipMeetingDurationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveVoipMeetingDuration = SaveVoipMeetingDurationAPI.as_view()


class CheckMeetingStatusAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            meeting_id = data["meeting_id"]
            meeting_id = remo_html_from_string(meeting_id)

            meeting_obj = LiveChatVoIPData.objects.filter(
                meeting_id=meeting_id)

            if meeting_obj:
                meeting_obj = meeting_obj.first()

                response['is_completed'] = meeting_obj.is_completed

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckMeetingStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CheckMeetingStatus = CheckMeetingStatusAPI.as_view()


class CheckChatReportStatusAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            meeting_id = data["meeting_id"]
            meeting_id = remo_html_from_string(meeting_id)

            response['is_chat_reported'] = False

            meeting_obj = LiveChatVoIPData.objects.filter(
                meeting_id=meeting_id).first()

            if meeting_obj:
                reported_customer = LiveChatReportedCustomer.objects.filter(livechat_customer=meeting_obj.customer, is_reported=True).first()

                if reported_customer:
                    response['is_chat_reported'] = reported_customer.is_reported

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckChatReportStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CheckChatReportStatus = CheckChatReportStatusAPI.as_view()
