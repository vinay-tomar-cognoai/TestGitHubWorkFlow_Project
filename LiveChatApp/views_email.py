import os
import sys
import json
import uuid
import pytz
import random
import logging
from datetime import datetime
import re
import urllib.parse

from django.http import FileResponse
from django.utils.safestring import mark_safe
from django.shortcuts import render, HttpResponse, HttpResponseRedirect

# Django REST framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.contrib.auth import get_user_model

from EasyChatApp.models import Channel
from LiveChatApp.models import *
from LiveChatApp.constants import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils_email import *
from LiveChatApp.utils_validation import LiveChatInputValidation
from LiveChatApp.utils import check_if_livechat_only_admin, get_admin_config, DecryptVariable
from DeveloperConsoleApp.utils import get_developer_console_settings

User = get_user_model()

# Logger
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class LiveChatEmailConfigAuthenticationAPI(APIView):
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

                email_config_id = data["email_config_id"]
                email_config_password = data["email_config_password"]
                email_config_server = validation_obj.remo_html_from_string(data["email_config_server"])
                email_config_security = validation_obj.remo_html_from_string(data["email_config_security"])

                if not validation_obj.validate_email(email_config_id):
                    response["status"] = 400
                    response["message"] = "Please enter valid email."

                if email_config_password.strip() == "":
                    response["status"] = 400
                    response["message"] = "Please enter password."

                if email_config_server.strip() == "":
                    response["status"] = 400
                    response["message"] = "Please enter imap server."

                if email_config_security.strip() == "":
                    response["status"] = 400
                    response["message"] = "Please choose valid security."

                if response["status"] == 400:
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                admin_config = get_admin_config(
                    user_obj, LiveChatAdminConfig, LiveChatUser)

                authentication_status = imap_server_authenticate(admin_config, email_config_id, email_config_password, email_config_server, email_config_security)
                
                if authentication_status == "success":

                    email_config_setup_obj = LiveChatEmailConfigSetup.objects.filter(admin_config=admin_config, email=email_config_id).first()
                    custom_encrypt_obj = CustomEncrypt()
                    email_config_password = custom_encrypt_obj.encrypt(email_config_password)

                    if email_config_setup_obj:

                        email_config_setup_obj.email = email_config_id
                        email_config_setup_obj.password = email_config_password
                        email_config_setup_obj.server = email_config_server
                        email_config_setup_obj.security = email_config_security
                        email_config_setup_obj.save()

                    else:

                        email_config_setup_obj = LiveChatEmailConfigSetup.objects.create(admin_config=admin_config, email=email_config_id, password=email_config_password,
                                                                                         server=email_config_server, security=email_config_security)

                    email_config_obj = get_email_config_obj(admin_config, LiveChatEmailConfig)

                    email_config_obj.is_livechat_enabled_for_email = True
                    email_config_obj.is_successful_authentication_complete = True
                    email_config_obj.current_email_setup = email_config_setup_obj
                    email_config_obj.save()

                response["status"] = 200
                response["message"] = "success"
                response["authentication_status"] = authentication_status

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LiveChatEmailConfigAuthenticationAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LiveChatEmailConfigAuthentication = LiveChatEmailConfigAuthenticationAPI.as_view()


class HandleEmailConfigStatusAPI(APIView):
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

                is_livechat_enabled_for_email = data["is_livechat_enabled_for_email"]
                is_successful_authentication_complete = data["is_successful_authentication_complete"]

                admin_config = get_admin_config(
                    user_obj, LiveChatAdminConfig, LiveChatUser)

                email_config_obj = get_email_config_obj(admin_config, LiveChatEmailConfig)

                email_config_obj.is_livechat_enabled_for_email = is_livechat_enabled_for_email
                email_config_obj.is_successful_authentication_complete = is_successful_authentication_complete
                email_config_obj.save()

                response["status"] = 200
                response["message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("HandleEmailConfigStatusAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


HandleEmailConfigStatus = HandleEmailConfigStatusAPI.as_view()


class SaveLiveChatEmailConfigurationAPI(APIView):
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

                is_auto_disposal_enabled = data["is_auto_disposal_enabled"]
                is_session_inactivity_enabled = data["is_session_inactivity_enabled"]
                chat_disposal_duration = data["chat_disposal_duration"]
                is_followup_leads_over_mail_enabled = data["is_followup_leads_over_mail_enabled"]

                if is_session_inactivity_enabled and not chat_disposal_duration.isnumeric() or int(chat_disposal_duration) < 1 or int(chat_disposal_duration) > 50:
                    response["status"] = 400
                    response["message"] = 'Please enter integer value between 1 to 50 in "Time After Which Chat Should Dispose field"'

                if response["status"] == 400:
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                admin_config = get_admin_config(
                    user_obj, LiveChatAdminConfig, LiveChatUser)

                email_config_obj = get_email_config_obj(admin_config, LiveChatEmailConfig)

                email_config_obj.is_auto_disposal_enabled = is_auto_disposal_enabled
                email_config_obj.is_session_inactivity_enabled = is_session_inactivity_enabled
                email_config_obj.chat_disposal_duration = int(chat_disposal_duration)
                email_config_obj.is_followup_leads_over_mail_enabled = is_followup_leads_over_mail_enabled
                email_config_obj.save()

                response["status"] = 200
                response["message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveLiveChatEmailConfigurationAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveLiveChatEmailConfiguration = SaveLiveChatEmailConfigurationAPI.as_view()


class SaveAgentEmailChatAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()
            
            session_id = data["session_id"]
            message = data["message"]
            sender = data["sender"]
            attached_file_src = data["attached_file_src"]
            thumbnail_file_src = data["thumbnail_url"]

            is_guest_agent_message = False
            if "is_guest_agent_message" in data:
                is_guest_agent_message = data["is_guest_agent_message"]

            sender_name = ""
            if "sender_name" in data:
                sender_name = data["sender_name"]

            sender_username = ""
            if "sender_username" in data:
                sender_username = data["sender_username"]

            if (message != None and message != "") or attached_file_src != "":
                message = validation_obj.remo_html_from_string(message)
            else:
                response["status_code"] = "300"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            session_id = validation_obj.remo_html_from_string(session_id)
            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)
            agent_obj = customer_obj.agent_id
            admin = get_admin_from_active_agent(agent_obj, LiveChatUser)

            if 'http' not in message and 'https' not in message:
                message = validation_obj.remo_unwanted_characters_from_agent_message(
                    message, LiveChatAdminConfig, admin)

            message = message.replace("*", "")
            attached_file_src = validation_obj.remo_html_from_string(
                attached_file_src)

            if sender_name == "":
                sender_name = str(agent_obj.user.first_name) + \
                    " " + str(agent_obj.user.last_name)

            attachment_file_name = ""
            if attached_file_src != "":
                attachment_file_name = attached_file_src.split("/")[-1]
            logger.info("inside SaveAgentChatAPI:",
                        extra={'AppName': 'LiveChat'})

            livechat_mis_obj = LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                                                   sender=sender,
                                                                   text_message=message,
                                                                   sender_name=sender_name,
                                                                   message_time=timezone.now(),
                                                                   attachment_file_name=attachment_file_name,
                                                                   attachment_file_path=attached_file_src,
                                                                   thumbnail_file_path=thumbnail_file_src,
                                                                   is_guest_agent_message=is_guest_agent_message,
                                                                   sender_username=sender_username)

            customer_obj.unread_message_count = 0
            customer_obj.save()

            response["status_code"] = "200"
            response["message_id"] = str(livechat_mis_obj.message_id)
            response["translated_text"] = message

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveAgentEmailChatAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveAgentEmailChat = SaveAgentEmailChatAPI.as_view()


class TransferFollowupLeadToEmailConversationAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['status_message'] = INTERNAL_SERVER_ERROR
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            session_id = data["session_id"]

            livechat_customer_obj = LiveChatFollowupCustomer.objects.filter(livechat_customer__session_id=session_id).first()

            if livechat_customer_obj:
                if not livechat_customer_obj.livechat_customer.email or livechat_customer_obj.livechat_customer.email.lower() == 'none':
                    response['status'] = 400
                    response['status_message'] = 'Cannot transfer lead as email id is not present.'     
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                livechat_customer_obj.is_completed = True
                livechat_customer_obj.completed_date = timezone.now()
                livechat_customer_obj.save()

                livechat_customer_obj.livechat_customer.agent_id = livechat_customer_obj.agent_id
                livechat_customer_obj.livechat_customer.is_session_exp = False
                livechat_customer_obj.livechat_customer.previous_channel = livechat_customer_obj.livechat_customer.channel.name
                livechat_customer_obj.livechat_customer.channel = Channel.objects.filter(name="Email").first()
                livechat_customer_obj.livechat_customer.client_id = livechat_customer_obj.livechat_customer.email
                livechat_customer_obj.livechat_customer.chat_ended_by = ""
                livechat_customer_obj.livechat_customer.save()

            else:
                response['status_message'] = "Invalid session ID"

            response['status'] = 200
            response['status_message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error TransferFollowupLeadToEmailConversationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


TransferFollowupLeadToEmailConversation = TransferFollowupLeadToEmailConversationAPI.as_view()


class SendLiveChatEmailToCustomerAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()
            
            session_id = data["session_id"]
            message_id = data["message_id"]
            channel_file_url = data["channel_file_url"]

            session_id = validation_obj.remo_html_from_string(session_id)
            message_id = validation_obj.remo_html_from_string(message_id)
            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)
            livechat_mis_obj = LiveChatMISDashboard.objects.get(message_id=message_id)

            agent_obj = customer_obj.agent_id
            admin_config = get_admin_config(agent_obj, LiveChatAdminConfig, LiveChatUser)
            email_config_obj = get_email_config_obj(admin_config, LiveChatEmailConfig)

            if not email_config_obj.is_livechat_enabled_for_email or not email_config_obj.is_successful_authentication_complete:
                response["status"] = 403
                response["status_message"] = "Email authentication is not complete. Please contact administrator."

            if not customer_obj.email:
                response["status"] = 403
                response["status_message"] = "Cannot send the message as customer email is not set." 

            if response["status"] == 403:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            send_email_message_to_customer(livechat_mis_obj.text_message, channel_file_url, customer_obj, livechat_mis_obj, email_config_obj, LiveChatMISDashboard, LiveChatMISEmailData, LiveChatEmailConfigSetup)

            response["status"] = 200
            response["status_message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SendLiveChatEmailToCustomerAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SendLiveChatEmailToCustomer = SendLiveChatEmailToCustomerAPI.as_view()
