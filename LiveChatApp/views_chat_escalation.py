import os
import sys
import json
import uuid
from django import conf
import pytz
import logging
import urllib.parse

# Django REST framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.shortcuts import render, HttpResponse, HttpResponseRedirect

from EasyChat import settings
from LiveChatApp.utils import *
from LiveChatApp.models import *
from LiveChatApp.constants import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils_translation import get_translated_text
from LiveChatApp.livechat_channels_webhook import send_channel_based_text_message, send_channel_based_welcome_message

import datetime

# Logger
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def ChatEscalation(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            is_user_agent = user_obj.status == "3"

            if is_user_agent:
                return HttpResponse(AUTHORIZATION_DENIED)

            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            return render(request, 'LiveChatApp/chat_escalation.html', {
                "user_obj": user_obj, 
                "admin_config": admin_config,
                "character_limit_large_text": LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT,
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ChatEscalation: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class SaveChatEscalationDataAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            if user_obj.status == "1":

                validation_obj = LiveChatInputValidation()

                is_chat_escalation_matrix_enabled = data["is_chat_escalation_matrix_enabled"]
                is_agent_allowed_to_force_report = data["is_agent_allowed_to_force_report"]
                warning_text_for_customer = validation_obj.remo_html_from_string(data["warning_text_for_customer"])
                end_chat_text_for_reported_customer = validation_obj.remo_html_from_string(data["end_chat_text_for_reported_customer"])

                if len(warning_text_for_customer) == 0:
                    response["status"] = 400
                    response["message"] = "Warning Text For The Customer cannot be empty."

                if len(warning_text_for_customer) > LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT:
                    response["status"] = 400
                    response["message"] = "Warning Text For The Customer is too long."

                if not validation_obj.alphanumeric(warning_text_for_customer):
                    response["status"] = 400
                    response["message"] = "Kindly enter alphanumeric text only in Warning Text For The Customer"

                if len(end_chat_text_for_reported_customer) == 0:
                    response["status"] = 400
                    response["message"] = "End Chat Text For The Customer cannot be empty."

                if len(end_chat_text_for_reported_customer) > LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT:
                    response["status"] = 400
                    response["message"] = "End Chat Text For The Customer is too long."

                if not validation_obj.alphanumeric(end_chat_text_for_reported_customer):
                    response["status"] = 400
                    response["message"] = "Kindly enter alphanumeric text only in End Chat Text For The Customer"

                if response["status"] == 400:
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                admin_config = get_admin_config(
                    user_obj, LiveChatAdminConfig, LiveChatUser)

                admin_config.is_chat_escalation_matrix_enabled = is_chat_escalation_matrix_enabled
                admin_config.is_agent_allowed_to_force_report = is_agent_allowed_to_force_report
                admin_config.warning_text_for_customer = warning_text_for_customer
                admin_config.end_chat_text_for_reported_customer = end_chat_text_for_reported_customer
                admin_config.save()

                response["status"] = 200
                response["message"] = "Success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveChatEscalationDataAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveChatEscalationData = SaveChatEscalationDataAPI.as_view()


class ChatEscalationWarnUserAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            session_id = data["session_id"]
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            if user_obj.status == "3" and admin_config.is_chat_escalation_matrix_enabled:

                livechat_cust_obj = LiveChatCustomer.objects.filter(session_id=session_id)

                if livechat_cust_obj.exists():

                    livechat_cust_obj = livechat_cust_obj[0]
                    livechat_reported_cust_obj = LiveChatReportedCustomer.objects.filter(livechat_customer=livechat_cust_obj)

                    if not livechat_reported_cust_obj.exists():
                        LiveChatReportedCustomer.objects.create(livechat_customer=livechat_cust_obj)

                        message_to_customer = str(admin_config.warning_text_for_customer)

                        if livechat_cust_obj.customer_language:
                            message_to_customer = get_translated_text(message_to_customer, livechat_cust_obj.customer_language.lang, EasyChatTranslationCache)

                        response["status"] = 200
                        response["message"] = "success"
                        response["warning_message"] = str(admin_config.warning_text_for_customer)
                        response["message_to_customer"] = message_to_customer
                    else:
                        response['message'] = 'Customer is already warned'

                else:
                    response['message'] = 'Invalid Session ID'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ChatEscalationWarnUserAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ChatEscalationWarnUser = ChatEscalationWarnUserAPI.as_view()


class ChatEscalationReportUserAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            session_id = data["session_id"]
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            is_customer_reported = False

            if user_obj.status == "3" and admin_config.is_chat_escalation_matrix_enabled:

                livechat_cust_obj = LiveChatCustomer.objects.filter(session_id=session_id)

                if livechat_cust_obj.exists():

                    livechat_cust_obj = livechat_cust_obj[0]
                    livechat_reported_cust_obj = LiveChatReportedCustomer.objects.filter(livechat_customer=livechat_cust_obj)

                    if livechat_reported_cust_obj.exists():

                        livechat_reported_cust_obj = livechat_reported_cust_obj[0]

                        if livechat_reported_cust_obj.is_reported == False and livechat_reported_cust_obj.is_completed == False:

                            livechat_reported_cust_obj.is_reported = True
                            livechat_reported_cust_obj.reported_date = timezone.now()
                            livechat_reported_cust_obj.save()
                            is_customer_reported = True

                        else:

                            response['message'] = 'Customer is already reported'

                    else:

                        if admin_config.is_agent_allowed_to_force_report:

                            LiveChatReportedCustomer.objects.create(livechat_customer=livechat_cust_obj, is_reported=True)
                            is_customer_reported = True

                        else:
                            response["status"] = 400
                            response['message'] = 'You are not authorised to report this user'

                    if is_customer_reported:

                        livechat_cust_obj.is_online = False
                        if livechat_cust_obj.guest_agents.exists():
                            livechat_cust_obj.guest_agents.clear()
                        livechat_cust_obj.save()

                        message_to_customer = str(admin_config.end_chat_text_for_reported_customer)

                        if livechat_cust_obj.customer_language:
                            message_to_customer = get_translated_text(message_to_customer, livechat_cust_obj.customer_language.lang, EasyChatTranslationCache)

                        if not livechat_cust_obj.is_external and livechat_cust_obj.channel.name != "Web":
                            if Profile.objects.filter(livechat_session_id=session_id, livechat_connected=True).count():
                                user_obj = Profile.objects.get(
                                    livechat_session_id=session_id)

                                send_channel_based_text_message(
                                    message_to_customer, livechat_cust_obj, user_obj.user_id)
                                
                                bot_info_obj = BotInfo.objects.filter(bot=livechat_cust_obj.bot).first()
                                if bot_info_obj and bot_info_obj.show_welcome_msg_on_end_chat:
                                    send_channel_based_welcome_message(user_obj, livechat_cust_obj)
                                    
                                user_obj.livechat_connected = False
                                user_obj.save()
                                
                        response["status"] = 200
                        response["message"] = "success"
                        response["report_message"] = str(admin_config.end_chat_text_for_reported_customer)
                        response["message_to_customer"] = message_to_customer
                else:
                    response['message'] = 'Invalid Session ID'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ChatEscalationReportUserAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ChatEscalationReportUser = ChatEscalationReportUserAPI.as_view()


def ReportedUsers(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            is_user_agent = user_obj.status == "3"

            if is_user_agent or not user_obj.is_chat_escalation_enabled: 
                return HttpResponse(AUTHORIZATION_DENIED)

            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            return render(request, 'LiveChatApp/reported_users.html', {
                "user_obj": user_obj, 
                "admin_config": admin_config
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ReportedUsers: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class GetLiveChatReportedUsersAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            is_user_agent = user_obj.status == "3"

            if not is_user_agent and user_obj.is_chat_escalation_enabled:

                bot_objs = user_obj.bots.all()
                agent_obj_list = get_agents_under_this_user(user_obj)

                livechat_cust_objs = LiveChatReportedCustomer.objects.filter(
                    livechat_customer__agent_id__in=agent_obj_list, livechat_customer__bot__in=bot_objs, is_reported=True, is_blocked=False, is_completed=False).order_by('-livechat_customer__joined_date')

                page = data['page']
                total_users, livechat_cust_objs, start_point, end_point = paginate(
                    livechat_cust_objs, REPORTED_USERS_COUNT, page)

                reported_users = parse_and_get_reported_blocked_users(livechat_cust_objs)

                response["status"] = 200
                response["message"] = "success"
                response["reported_users"] = reported_users
                response["pagination_data"] = get_audit_trail_pagination_data(
                    livechat_cust_objs)
                response["total_users"] = total_users
                response["start_point"] = start_point
                response["end_point"] = end_point

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatReportedUsersAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatReportedUsers = GetLiveChatReportedUsersAPI.as_view()


class ChatEscalationBlockUserAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['status_message'] = INTERNAL_SERVER_ERROR
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            is_user_agent = user_obj.status == "3"

            if not is_user_agent and user_obj.is_chat_escalation_enabled:

                session_ids = data["selected_users"]
                block_duration = data["block_duration"]

                livechat_cust_objs = LiveChatReportedCustomer.objects.filter(livechat_customer__session_id__in=session_ids)

                for livechat_cust_obj in livechat_cust_objs:
                    livechat_cust_obj.is_blocked = True
                    livechat_cust_obj.blocked_date = timezone.now()
                    livechat_cust_obj.block_duration = block_duration
                    livechat_cust_obj.save()

                response['status'] = 200
                response['message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ChatEscalationBlockUserAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ChatEscalationBlockUser = ChatEscalationBlockUserAPI.as_view()


class ChatEscalationMarkCompleteAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['status_message'] = INTERNAL_SERVER_ERROR
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            is_user_agent = user_obj.status == "3"

            if not is_user_agent and user_obj.is_chat_escalation_enabled:

                session_ids = data["selected_users"]

                livechat_cust_objs = LiveChatReportedCustomer.objects.filter(livechat_customer__session_id__in=session_ids)

                for livechat_cust_obj in livechat_cust_objs:
                    livechat_cust_obj.is_completed = True
                    livechat_cust_obj.save()

                response['status'] = 200
                response['message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ChatEscalationMarkCompleteAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ChatEscalationMarkComplete = ChatEscalationMarkCompleteAPI.as_view()


def BlockedUsers(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            is_user_agent = user_obj.status == "3"

            if is_user_agent or not user_obj.is_chat_escalation_enabled: 
                return HttpResponse(AUTHORIZATION_DENIED)

            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            return render(request, 'LiveChatApp/blocked_users.html', {
                "user_obj": user_obj, 
                "admin_config": admin_config
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("BlockedUsers: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class GetLiveChatBlockedUsersAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            is_user_agent = user_obj.status == "3"

            if not is_user_agent and user_obj.is_chat_escalation_enabled:

                bot_objs = user_obj.bots.all()
                agent_obj_list = get_agents_under_this_user(user_obj)

                livechat_cust_objs = LiveChatReportedCustomer.objects.filter(
                    livechat_customer__agent_id__in=agent_obj_list, livechat_customer__bot__in=bot_objs, is_blocked=True, is_completed=False).order_by('-livechat_customer__joined_date')

                page = data['page']
                total_users, livechat_cust_objs, start_point, end_point = paginate(
                    livechat_cust_objs, BLOCKED_USERS_COUNT, page)

                blocked_users = parse_and_get_reported_blocked_users(livechat_cust_objs)

                response["status"] = 200
                response["message"] = "success"
                response["blocked_users"] = blocked_users
                response["pagination_data"] = get_audit_trail_pagination_data(
                    livechat_cust_objs)
                response["total_users"] = total_users
                response["start_point"] = start_point
                response["end_point"] = end_point

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatBlockedUsersAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatBlockedUsers = GetLiveChatBlockedUsersAPI.as_view()


class ChatEscalationIgnoreNotificationAPI(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            session_id = data["session_id"]
            notification_type = data["notification_type"]
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            if user_obj.status == "3" and admin_config.is_chat_escalation_matrix_enabled:

                livechat_cust_obj = LiveChatCustomer.objects.filter(session_id=session_id)

                if livechat_cust_obj.exists():

                    livechat_cust_obj = livechat_cust_obj[0]

                    if notification_type == "warn":
                        livechat_cust_obj.chat_escalation_warn_ignored_time = timezone.now()
                        livechat_cust_obj.save()

                        response["status"] = 200
                        response["message"] = "success"
                        response["chat_escalation_status"] = "safe"

                    elif notification_type == "report":
                        livechat_reported_cust_obj = LiveChatReportedCustomer.objects.get(livechat_customer=livechat_cust_obj)
                        livechat_reported_cust_obj.chat_escalation_report_ignored_time = timezone.now()
                        livechat_reported_cust_obj.save()   

                        response["status"] = 200
                        response["message"] = "success"
                        response["chat_escalation_status"] = "warned"

                else:
                    response['message'] = 'Invalid Session ID'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(".ChatEscalationIgnoreNotificationAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ChatEscalationIgnoreNotification = ChatEscalationIgnoreNotificationAPI.as_view()
