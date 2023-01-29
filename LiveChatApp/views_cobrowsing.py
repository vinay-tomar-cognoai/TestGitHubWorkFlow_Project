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
import requests
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


class ManageCobrowsingRequestAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal server error!"

        try:

            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            livechat_session_id = data['livechat_session_id']
            request_type = data['request_type']

            customer_obj = LiveChatCustomer.objects.filter(
                session_id=livechat_session_id)

            if customer_obj:
                customer_obj = customer_obj.first()
                agent_obj = customer_obj.agent_id

                if request_type == 'initiated':
                    cobrowsing_obj = LiveChatCobrowsingData.objects.create(
                        customer=customer_obj,
                        agent=agent_obj)
                    
                    # if customer_obj.is_external:
                    #     extra_details = {
                    #         'message': f'{settings.EASYCHAT_HOST_URL}/customer-voice-meeting/?meeting_id={str(voip_obj.meeting_id)}&session_id={livechat_session_id}'
                    #     }

                    #     push_livechat_event(SEND_MESSAGE_EVENT, customer_obj, extra_details)

                elif request_type in ['accepted', 'rejected', 'started', 'completed', 'interrupted', 'guest_agent_joined']:
                    meeting_id = data['meeting_id']

                    cobrowsing_obj = LiveChatCobrowsingData.objects.filter(
                        meeting_id=meeting_id)

                    if cobrowsing_obj:
                        cobrowsing_obj = cobrowsing_obj.first()

                        if request_type == 'accepted':
                            if 'cobrowse_session_id' in data:
                                cobrowsing_obj.cobrowse_session_id = data['cobrowse_session_id']
                            cobrowsing_obj.is_accepted = True
                        elif request_type == 'rejected':
                            cobrowsing_obj.is_rejected = True
                        elif request_type == 'started':
                            cobrowsing_obj.is_started = True
                            cobrowsing_obj.start_datetime = timezone.now()
                        elif request_type == 'completed':
                            cobrowsing_obj.is_completed = True
                            cobrowsing_obj.end_datetime = timezone.now()
                        elif request_type == 'guest_agent_joined':
                            guest_agent_username = data['guest_agent_username']
                            livechat_user = LiveChatUser.objects.filter(user__username=guest_agent_username)

                            if livechat_user:
                                livechat_user = livechat_user.first()
                                cobrowsing_obj.guest_agents.add(livechat_user)
                        else:
                            cobrowsing_obj.is_interrupted = True
                            cobrowsing_obj.is_completed = True

                        cobrowsing_obj.save()
                        if cobrowsing_obj.is_completed and not cobrowsing_obj.is_interrupted:
                            send_event_for_cobrowsing_history(cobrowsing_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)
                    else:
                        response["message"] = 'Meeting does not exist.'
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)

                response['meeting_id'] = str(cobrowsing_obj.meeting_id)
                response['status'] = 200
                response['message'] = 'success'

            else:
                response["message"] = 'LiveChat Customer does not exist.'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside ManageCobrowsingRequestAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ManageCobrowsingRequest = ManageCobrowsingRequestAPI.as_view()


def LiveChatCobrowsingEnd(request):  # noqa: N802
    try:
        if request.user.is_authenticated:
            return render(request, "LiveChatApp/cobrowsing_end.html", {})
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AuditTrail ! %s %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return render(request, 'LiveChatApp/error_500.html')


def CobrowsingHistory(request):  # noqa: N802
    try:
        if request.user.is_authenticated:
            validation_obj = LiveChatInputValidation()

            channel_obj_list = Channel.objects.all()

            agent_username = request.GET.get('agent_username')
            agent_username = validation_obj.remo_html_from_string(
                agent_username)
            agent_username = validation_obj.remo_special_tag_from_string(
                agent_username)

            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            agent_obj_list = get_agents_under_this_user(user_obj)

            category_list = user_obj.category.all()
            agent_list = []
            for agent in agent_obj_list:
                agent_list.append(agent.user.username)

            template_to_render = 'LiveChatApp/cobrowsing_history.html'

            messages_list = []
            voip_object_list = []
            if user_obj.static_analytics:
                template_to_render = 'LiveChatApp/static_audit_trail.html'
                voip_object_list = STATIC_LIVECHAT_AGENT_MESSAGE_HISTORY
                messages_list = STATIC_LIVECHAT_MESSAGES_LIST

            page = request.GET.get('page')
            total_audits, voip_object_list, start_point, end_point = paginate(
                voip_object_list, VOIP_HISTORY_ITEM_COUNT, page)

            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)

            return render(request, template_to_render, {
                "voip_object_list": voip_object_list,
                "total_audits": total_audits,
                "user_obj": user_obj,
                "agent_list": agent_list,
                "DEFAULT_LIVECHAT_FILTER_START_DATETIME": datetime.datetime.today().date(),
                "DEFAULT_LIVECHAT_FILTER_END_DATETIME": datetime.datetime.today().date(),
                "start_date": datetime.datetime.today().date(),
                "end_date": datetime.datetime.today().date(),
                "start_point": start_point,
                "end_point": end_point,
                "admin_config": admin_config,
                "messages_list": messages_list,
                "channel_obj_list": channel_obj_list,
                "category_list": category_list,
                "is_report_generation_via_kafka_enabled": is_kafka_enabled(),
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("CobrowsingHistory ! %s %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return render(request, 'LiveChatApp/error_500.html')


class GetLiveChatCobrowsingHistoryAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get_data(self, key):
        try:
            if key in self.data:
                return self.data[key]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatVOIPHistoryAPI get_data: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 'None'

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            self.data = data

            validation_obj = LiveChatInputValidation()

            agent_username = self.get_data('agent_username')
            agent_username = validation_obj.remo_html_from_string(
                agent_username)
            agent_username = validation_obj.remo_special_tag_from_string(
                agent_username)

            try:
                query_user_obj = LiveChatUser.objects.get(
                    user=User.objects.get(username=str(agent_username)))
            except Exception:
                query_user_obj = None

            # By default, voip history of last 1 days is loaded
            datetime_start = (datetime.datetime.today()).date()
            datetime_end = (datetime.datetime.today() +
                            datetime.timedelta(1)).date()
            # datetime end is not inclusive so adding 1 day
            try:
                start_date = self.get_data('start_date')
                end_date = self.get_data('end_date')
                datetime_start = datetime.datetime.strptime(
                    start_date.strip(), DEFAULT_DATE_FORMAT).date()
                datetime_end = (datetime.datetime.strptime(
                    end_date.strip(), DEFAULT_DATE_FORMAT) + datetime.timedelta(1)).date()  # noqa: F841
                # datetime end is not inclusive in range so adding 1 day
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            agent_obj_list = get_agents_under_this_user(user_obj)

            voip_object_list = get_cobrowsing_data_history_objects(
                agent_username, query_user_obj, datetime_end, datetime_start, agent_obj_list, LiveChatCobrowsingData)

            page = self.get_data('page')

            total_audits, voip_object_list, start_point, end_point = paginate(
                voip_object_list, VOIP_HISTORY_ITEM_COUNT, page)

            response['cobrowsing_object_list'] = parse_cobrowsing_history_object_list(
                voip_object_list)

            response['pagination_data'] = get_audit_trail_pagination_data(
                voip_object_list)
            response['total_audits'] = total_audits
            response['start_point'] = start_point
            response['end_point'] = end_point

            response["status"] = 200
            response["status_message"] = "Success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatCobrowsingHistoryAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatCobrowsingHistory = GetLiveChatCobrowsingHistoryAPI.as_view()


class SaveCobrowsingNpsAPI(APIView):

    def post(self, request, *args, **kwargs):

        response = {}
        response["status"] = "500"
        response["message"] = "Internal server error"

        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            validation_obj = LiveChatInputValidation()

            meeting_id = validation_obj.remo_html_from_string(data['session_id'])
            rating = validation_obj.remo_html_from_string(data['rating'])
            feedback = validation_obj.remo_html_from_string(data['feedback'])

            cobrowsing_obj = LiveChatCobrowsingData.objects.filter(
                cobrowse_session_id=meeting_id).first()
            
            if cobrowsing_obj:
                cobrowsing_obj.rating = rating
                cobrowsing_obj.text_feedback = feedback
                cobrowsing_obj.save(update_fields=['rating', 'text_feedback'])

                if not cobrowsing_obj.is_completed:
                    cobrowsing_obj.is_completed = True
                    cobrowsing_obj.end_datetime = timezone.now()
                    cobrowsing_obj.save(update_fields=['is_completed', 'end_datetime'])

            response['status'] = 200
            response['message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveCobrowsingNpsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

SaveCobrowsingNps = SaveCobrowsingNpsAPI.as_view()


class EndCobrowsingSessionAPI(APIView):

    def post(self, request, *args, **kwargs):

        response = {}
        response["status"] = "500"
        response["message"] = "Internal server error"

        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            validation_obj = LiveChatInputValidation()

            cobrowse_session_id = validation_obj.remo_html_from_string(data['cobrowse_session_id'])

            cobrowsing_obj = LiveChatCobrowsingData.objects.filter(
                cobrowse_session_id=cobrowse_session_id).first()
            
            if cobrowsing_obj and not cobrowsing_obj.is_completed:
                cobrowsing_obj.is_completed = True
                cobrowsing_obj.end_datetime = timezone.now()
                cobrowsing_obj.save(update_fields=['is_completed', 'end_datetime'])

            response['status'] = 200
            response['message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside EndCobrowsingSessionAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

EndCobrowsingSession = EndCobrowsingSessionAPI.as_view()
