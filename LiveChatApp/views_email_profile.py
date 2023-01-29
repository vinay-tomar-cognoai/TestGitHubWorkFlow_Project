import os
import sys
import json
import uuid
import pytz
import random
import logging
from datetime import datetime
import re

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

from EasyChatApp.models import Channel, Config
from LiveChatApp.models import LiveChatCustomer, LiveChatUser, LiveChatMISDashboard, LiveChatGuestAgentAudit, LiveChatAdminConfig, LiveChatEmailProfile, LiveChatEmailTableParameters, LiveChatEmailGraphParameters, LiveChatEmailAttachmentParameters, LiveChatEmailConfig, LiveChatEmailConfigSetup
from LiveChatApp.constants import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils_email_profile import send_sample_email, get_channel_list
from LiveChatApp.utils_validation import LiveChatInputValidation
from LiveChatApp.utils import check_if_livechat_only_admin, get_admin_config, DecryptVariable
from LiveChatApp.utils_email import get_email_config_obj
from DeveloperConsoleApp.utils import get_developer_console_settings

User = get_user_model()

# Logger
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class SaveEmailProfileAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            if user_obj.status == '1':

                profile_id = data["profile_id"]
                profile_name = data["profile_name"]
                email_freq = data["email_freq"]
                email_addr_list = data["email_addr_list"]
                email_subject = data["email_subject"]
                agent_connection_rate = data["agent_connection_rate"]
                is_table_parameters_enabled = data["is_table_parameters_enabled"]
                count_variations = data["count_variations"]
                channel_list = data["channel_list"]
                table_records_list = data["table_records_list"]
                is_graph_parameters_enabled = data["is_graph_parameters_enabled"]
                is_chat_reports_enabled = data["is_chat_reports_enabled"]
                graph_chat_reports_list = data["graph_chat_reports_list"]
                is_interactions_enabled = data["is_interactions_enabled"]
                is_avg_handle_time_enabled = data["is_avg_handle_time_enabled"]
                is_attachment_parameters_enabled = data["is_attachment_parameters_enabled"]
                attachment_parameters_list = data["attachment_parameters_list"]

                profile_name = validation_obj.remo_html_from_string(profile_name)

                profile_names_list = list(LiveChatEmailProfile.objects.filter(livechat_user=user_obj, is_deleted=False).values_list('profile_name', flat=True))

                if email_subject.strip() == "":
                    email_subject = "Cogno Ai- LiveChat Report Mailer"

                if(profile_id == 'new' and profile_name.lower() in (profile.lower() for profile in profile_names_list)):
                    response["status"] = 400
                    response["message"] = "Profile Name already exists."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)                

                if profile_name.strip() == "":
                    response["status"] = 400
                    response["message"] = "Profile Name cannot be empty"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                profile_name_regex = re.compile(
                    r'[`@#$%^*()_+\-=\[\]{};\':"\\|,.<>~]')
                if re.fullmatch(profile_name_regex, profile_name):
                    response["status"] = 400
                    response["message"] = "Invalid Profile Name"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                if len(profile_name) > LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT:
                    response["status"] = 400
                    response["message"] = "Profile Name max characters allowed - 25"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                if agent_connection_rate != None and agent_connection_rate != "":
                    if int(agent_connection_rate) > 100 or int(agent_connection_rate) < 0:
                        response["status"] = 400
                        response["message"] = "Agent Connection Rate should be between 0-100"
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)

                if len(email_subject) > LIVECHAT_CHARACTER_LIMIT_MEDIUM_TEXT:
                    response["status"] = 400
                    response["message"] = "Email Subject max characters allowed - 100"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                email_profile_obj = None
                try:
                    if(profile_id != 'new'):
                        email_profile_obj = LiveChatEmailProfile.objects.get(
                            pk=int(profile_id), livechat_user=user_obj, is_deleted=False)
                    else:
                        email_profile_obj = LiveChatEmailProfile.objects.create(
                            profile_name=profile_name, livechat_user=user_obj, is_deleted=False)                        
                except Exception:
                    email_profile_obj = LiveChatEmailProfile.objects.create(
                        profile_name=profile_name, livechat_user=user_obj, is_deleted=False)

                table_parameter_obj = None
                try:
                    table_parameter_obj = LiveChatEmailTableParameters.objects.get(
                        profile=email_profile_obj)
                except Exception:
                    table_parameter_obj = LiveChatEmailTableParameters.objects.create(
                        profile=email_profile_obj)

                table_parameter_obj.count_variation = json.dumps(
                    count_variations)
                table_parameter_obj.channel = json.dumps(channel_list)
                table_parameter_obj.table_records = json.dumps(
                    table_records_list)
                table_parameter_obj.save()

                graph_parameter_obj = None
                try:
                    graph_parameter_obj = LiveChatEmailGraphParameters.objects.get(
                        profile=email_profile_obj)
                except Exception:
                    graph_parameter_obj = LiveChatEmailGraphParameters.objects.create(
                        profile=email_profile_obj)

                graph_parameter_obj.is_graph_chart_reports_enabled = is_chat_reports_enabled
                graph_parameter_obj.graph_chart_reports = json.dumps(
                    graph_chat_reports_list)
                graph_parameter_obj.is_graph_interaction_enabled = is_interactions_enabled
                graph_parameter_obj.is_graph_avg_handle_time_enabled = is_avg_handle_time_enabled
                graph_parameter_obj.save()

                attachment_parameter_obj = None
                try:
                    attachment_parameter_obj = LiveChatEmailAttachmentParameters.objects.get(
                        profile=email_profile_obj)
                except Exception:
                    attachment_parameter_obj = LiveChatEmailAttachmentParameters.objects.create(
                        profile=email_profile_obj)

                attachment_parameter_obj.attachment_parameters = json.dumps(
                    attachment_parameters_list)
                attachment_parameter_obj.save()

                email_profile_obj.profile_name = profile_name 
                email_profile_obj.last_updated_datetime = datetime.now()
                email_profile_obj.email_frequency = json.dumps(email_freq)
                email_profile_obj.email_address = json.dumps(email_addr_list)
                email_profile_obj.email_subject = email_subject
                email_profile_obj.agent_connection_rate = agent_connection_rate
                email_profile_obj.is_table_parameters_enabled = is_table_parameters_enabled
                email_profile_obj.table_parameters = table_parameter_obj
                email_profile_obj.is_graph_parameters_enabled = is_graph_parameters_enabled
                email_profile_obj.graph_parameters = graph_parameter_obj
                email_profile_obj.is_attachment_parameters_enabled = is_attachment_parameters_enabled
                email_profile_obj.attachment_parameters = attachment_parameter_obj
                email_profile_obj.save()

                response["message"] = "Profile Saved Successfully (without email address)"                
                if email_addr_list:
                    response["message"] = "Profile Saved Successfully"

                response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveEmailProfileAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveEmailProfile = SaveEmailProfileAPI.as_view()


class EnableDisableEmailNotifAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            is_email_enabled = data["is_email_enabled"]

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)

            admin_config = LiveChatAdminConfig.objects.filter(
                admin=user_obj).first()
            admin_config.is_email_notification_enabled = is_email_enabled
            admin_config.save()

            response["status"] = 200
            response["is_email_enabled"] = admin_config.is_email_notification_enabled
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EnableDisableEmailNotifAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EnableDisableEmailNotif = EnableDisableEmailNotifAPI.as_view()


def EmailSettings(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            bot_obj_list = user_obj.bots.filter(is_deleted=False)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            email_profile_objs = LiveChatEmailProfile.objects.filter(
                livechat_user=user_obj, is_deleted=False).order_by('pk')
            email_profile_pks = list(email_profile_objs.values_list(
                'pk', flat=True).order_by('pk'))
            profile_names_list = list(LiveChatEmailProfile.objects.filter(livechat_user=user_obj, is_deleted=False).values_list('profile_name', flat=True))
            try:
                latest_profile_pk = LiveChatEmailProfile.objects.filter(livechat_user=user_obj, is_deleted=False).latest('last_updated_datetime').pk
            except Exception:
                latest_profile_pk = 'new'
            counter = email_profile_objs.count() + 1

            new_profile_name = "Profile " + str(counter)
            while(new_profile_name.lower() in (profile.lower() for profile in profile_names_list)):
                counter += 1
                new_profile_name = "Profile " + str(counter)

            channel_list = get_channel_list(Channel)

            email_config_id = ""
            email_config_obj = get_email_config_obj(admin_config, LiveChatEmailConfig)
            if email_config_obj.current_email_setup:
                email_config_id = email_config_obj.current_email_setup.email

            if user_obj.status == "1":
                return render(request, 'LiveChatApp/email_settings.html', {
                    'user_obj': user_obj,
                    'admin_config': admin_config,
                    'bot_obj_list': bot_obj_list,
                    'email_profile_objs': email_profile_objs,
                    'new_profile_name': new_profile_name,
                    'email_profile_length': email_profile_objs.count(),
                    'email_profile_pks': email_profile_pks,
                    'latest_profile_pk': latest_profile_pk,
                    'channel_list': channel_list,
                    'email_config_obj': email_config_obj,
                    'email_config_id': email_config_id
                })
            else:
                return HttpResponse("You are not authorised to access this page.")
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EmailSettings: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect("/chat/login/")


class DeleteEmailProfileAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            email_profile_pk = data["email_profile_pk"]
            if user_obj.status == '1':
                email_profile_obj = LiveChatEmailProfile.objects.get(
                    pk=int(email_profile_pk))
                email_profile_obj.is_deleted = True
                email_profile_obj.save()

                response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteEmailProfileAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DeleteEmailProfile = DeleteEmailProfileAPI.as_view()


class SendSampleMailAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            email_profile_id = data['email_profile_pk']

            email_profile_obj = LiveChatEmailProfile.objects.get(pk=int(email_profile_id))
            email_receivers = json.loads(email_profile_obj.email_address)

            if len(email_receivers) == 0:
                response["status"] = 400
                response["message"] = "Please save email address for the profile."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            status_code = send_sample_email(email_profile_obj)
            
            if status_code == 102:
                response["message"] = str(get_developer_console_settings().email_api_failure_message)
                response["status"] = 102
            else:
                response["message"] = "Success"
                response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SendSampleMailAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

SendSampleMail = SendSampleMailAPI.as_view()
