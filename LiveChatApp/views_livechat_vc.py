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
from DeveloperConsoleApp.utils import get_save_in_s3_bucket_status
from DeveloperConsoleApp.utils_aws_s3 import s3_bucket_upload_file_by_file_path

from EasyChat import settings
from LiveChatApp.models import *
from LiveChatApp.views_agent import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils_validation import LiveChatFileValidation
from LiveChatApp.utils import DecryptVariable


User = get_user_model()
IST = pytz.timezone("Asia/Kolkata")

# Logger
logger = logging.getLogger(__name__)

ensure_element_tree(xlrd)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


def LiveChatVCMeetingEnded(request):
    try:
        meeting_id = request.GET.get('meeting_id')
        selected_language = 'en'
        feedback_text = {}

        if 'language' in request.GET:
            validation_obj = LiveChatInputValidation()
            selected_language = request.GET.get('language')
            selected_language = validation_obj.remo_html_from_string(selected_language)

        is_customer = True
        try:
            User.objects.get(username=request.user.username)
            is_customer = False
        except Exception:
            is_customer = True
        
        meeting_obj = LiveChatVoIPData.objects.get(meeting_id=meeting_id)
        if is_customer:
            try:
                customer_obj = meeting_obj.customer
                bot_obj = customer_obj.bot

                language_obj = Language.objects.filter(lang=selected_language).first()
                language_template_obj = RequiredBotTemplate.objects.filter(
                    bot=bot_obj, language=language_obj).first()

                text = language_template_obj.livechat_feedback_text
                text = text.split('$$$')
                feedback_text['feedback'] = text[0]
                feedback_text['scale_text'] = text[1]
                feedback_text['no_thanks'] = text[2]
                feedback_text['remarks'] = text[4]
                feedback_text['submit'] = text[5]
                feedback_text['video_call_ended'] = text[6]

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error LiveChatVCMeetingEnded %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        is_rating_given = meeting_obj.is_rating_given

        return render(request, "LiveChatApp/livechat_video_meet_end.html", {"is_customer": is_customer, "is_rating_given": is_rating_given, "meeting_id": meeting_id, 'feedback_text': feedback_text})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error LiveChatVCMeetingEnded %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return HttpResponse(status=401)


def LiveChatVCMeeting(request, meeting_id):
    try:
        is_agent = False
        agent_name = 'Agent'
        client_name = 'Client'
        selected_language = 'en'

        if 'language' in request.GET:
            validation_obj = LiveChatInputValidation()
            selected_language = request.GET.get('language')
            selected_language = validation_obj.remo_html_from_string(selected_language)

        livechat_agent = None
        try:
            user_obj = User.objects.get(username=request.user.username)
            livechat_agent = LiveChatUser.objects.get(user=user_obj)
            agent_name = livechat_agent.get_agent_name()
            is_agent = True
        except Exception:
            is_agent = False

        # meeting_io = LiveChatVideoConferencing.objects.filter(
        #     meeting_id=meeting_id)
        meeting_io = LiveChatVoIPData.objects.filter(meeting_id=meeting_id)
        if meeting_io:
            meeting_io = meeting_io[0]
            customer_obj = meeting_io.customer
            client_name = customer_obj.username
            primary_agent = meeting_io.agent

            bot_obj = customer_obj.bot
            config_obj = LiveChatConfig.objects.get(bot=bot_obj)

            meeting_host_url = config_obj.meeting_domain

            # if meeting_io.is_expired:
            #     return HttpResponseRedirect("/livechat/agent-vc-meeting-end/")
            if meeting_io.is_completed:
                return HttpResponseRedirect(f"/livechat/agent-vc-meeting-end/?meeting_id={meeting_io.meeting_id}&language={selected_language}")
            else:
                return render(request, "LiveChatApp/join_meeting.html", {
                    "meeting_io": meeting_io,
                    "meeting_host_url": meeting_host_url,
                    "is_password_required": False,
                    "is_agent": is_agent,
                    "client_name": client_name,
                    "agent_name": agent_name,
                    "unique_id": str(uuid.uuid4()),
                    "is_cobrowsing_active": False,
                    "show_cobrowsing_meeting_lobby": True,
                    "cobrowse_logo": "",
                    "meet_background_color": "",
                    "allow_meeting_feedback": False,
                    "livechat_agent": primary_agent,
                    "enable_meeting_recording": True,
                    "is_invited_agent": livechat_agent != primary_agent,
                    'selected_language': selected_language,
                })
        else:
            return HttpResponse(status=404)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error LiveChatVCMeeting %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)


class GenerateLiveChatVCMeetAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            session_id = validation_obj.remo_html_from_string(data["session_id"])
            meeting_description = "LiveChat Video Call"

            user_obj = User.objects.get(username=request.user.username)
            livechat_agent = LiveChatUser.objects.get(user=user_obj, is_deleted=False)

            livechat_customer_obj = LiveChatCustomer.objects.filter(session_id=session_id)[0]

            if LiveChatVideoConferencing.objects.filter(meeting_id=session_id, is_expired=False):
                meeting_io = LiveChatVideoConferencing.objects.filter(meeting_id=session_id, is_expired=False)[0]
            else:
                meeting_io = LiveChatVideoConferencing.objects.create(meeting_id=session_id,
                                                                      full_name=livechat_customer_obj.get_username(),
                                                                      mobile_number=livechat_customer_obj.phone,
                                                                      agent=livechat_agent,
                                                                      meeting_description=str(
                                                                          meeting_description),
                                                                      meeting_start_date=datetime.datetime.now().date(),
                                                                      meeting_start_time=datetime.datetime.now().time(),
                                                                      meeting_end_time=datetime.datetime.now().time())

            # meeting_url = str(settings.EASYCHAT_HOST_URL) + "/livechat/meeting/" + \
            #     str(meeting_io.meeting_id)

            meeting_url = "http://127.0.0.1:8000/livechat/meeting/" + \
                str(meeting_io.meeting_id)

            response["status"] = 200
            response["message"] = "success"
            response["session_id"] = str(meeting_io.meeting_id)
            response["meeting_url"] = meeting_url
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GenerateLiveChatVCMeetAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GenerateLiveChatVCMeet = GenerateLiveChatVCMeetAPI.as_view()


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

            if not os.path.exists(LIVECHAT_VC_FILES_PATH):
                os.makedirs(LIVECHAT_VC_FILES_PATH)

            file_path = "secured_files/LiveChatApp/video_calls/" + filename

            if get_save_in_s3_bucket_status():
                s3_bucket_upload_file_by_file_path(file_path, filename)

            media_file = open(file_path, "ab+")
            media_file.write(uploaded_file.read())
            media_file.close()

            file_path = "/" + file_path

            try:
                file_access_management_obj = LiveChatFileAccessManagement.objects.get(
                    file_path=file_path, is_public=False)
            except Exception:
                file_access_management_obj = LiveChatFileAccessManagement.objects.create(
                    file_path=file_path, is_public=False)

            meeting_obj = LiveChatVoIPData.objects.get(
                meeting_id=meeting_id)

            if (is_first_packet == 'true' or is_first_packet == True) and (meeting_obj.video_recording == '' or meeting_obj.video_recording == None):
                logger.info(timezone.now(), extra={'AppName': 'LiveChat'})
                meeting_obj.agent_recording_start_time = timezone.now()

            meeting_obj.video_recording = str(file_access_management_obj.pk)
            meeting_obj.save()

            response["status"] = 200
            
            response["name"] = filename
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveScreenRecordedDataAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status"] = 500
            response["name"] = "no_name"
            
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveScreenRecordedData = SaveScreenRecordedDataAPI.as_view()


class SaveCallFeedbackAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            meeting_id = data["meeting_id"]
            meeting_id = validation_obj.remo_html_from_string(meeting_id)

            rating = data['rating']
            rating = validation_obj.remo_html_from_string(rating)

            text_feedback = data['text_feedback']
            text_feedback = validation_obj.remo_html_from_string(text_feedback)

            meeting_obj = LiveChatVoIPData.objects.filter(
                meeting_id=meeting_id)

            if meeting_obj:
                meeting_obj = meeting_obj.first()
                meeting_obj.rating = rating
                meeting_obj.text_feedback = text_feedback
                meeting_obj.is_rating_given = True
                meeting_obj.save()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCallFeedbackAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveCallFeedback = SaveCallFeedbackAPI.as_view()
