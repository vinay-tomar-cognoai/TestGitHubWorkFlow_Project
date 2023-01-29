import os
import sys
import json
import uuid
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
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from EasyChat import settings
from EasyChatApp.utils import *
from LiveChatApp.utils import *
from LiveChatApp.models import *
from EasyChatApp.models import BotInfo
from LiveChatApp.constants import *
from LiveChatApp.livechat_channels_webhook import send_channel_based_text_message, send_channel_based_welcome_message
from LiveChatApp.utils_agent import push_livechat_event, check_if_uploded_livechat_file_is_valid, save_file_and_get_source_file_path_and_thumbnail_path, send_agent_livechat_response_based_on_channel, assign_selected_agent, auto_assign_agent
from LiveChatApp.views_calender import *
from LiveChatApp.views_analytics import *
from LiveChatApp.views_exposed_apis import *
from LiveChatApp.utils_custom_encryption import *
from EasyChatApp.utils_google_buisness_messages import *
from LiveChatApp.utils_validation import LiveChatFileValidation, LiveChatInputValidation
from EasyChatApp.utils_facebook import send_facebook_message, send_facebook_livechat_agent_response
from EasyChatApp.utils_instagram import send_instagram_message, send_instagram_livechat_agent_response
from EasyChatApp.utils_twitter import send_twitter_message, send_twitter_livechat_agent_response
from LiveChatApp.utils_translation import get_translated_text
from LiveChatApp.utils_email import get_livechat_email_initiated_time, get_livechat_email_initiated_date
from EasyChat.kafka_producer import send_packet_into_kafka_producer

User = get_user_model()
IST = pytz.timezone("Asia/Kolkata")

# Logger
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


def AgentProfile(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            livechat_categories = LiveChatCategory.objects.all()
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            is_user_agent = user_obj.status == "3"
            if is_user_agent:
                return render(request, 'LiveChatApp/agent_profile.html', {"user_obj": user_obj, "livechat_categories": livechat_categories, "admin_config": admin_config})
            else:
                return HttpResponse("You are not authorised to access this page.")
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AgentSettings: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def AgentSettings(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            livechat_categories = LiveChatCategory.objects.all()
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            is_user_agent = user_obj.status == "3"
            master_languages = Language.objects.all()
            if is_user_agent:
                bot_obj = user_obj.bots.all()[0]
                config_obj = LiveChatConfig.objects.get(bot=bot_obj)

                if not user_obj.preferred_languages.exists():
                    for language in bot_obj.languages_supported.all():
                        user_obj.preferred_languages.add(language)
                        user_obj.save()

                return render(request, 'LiveChatApp/agent_settings.html', {"user_obj": user_obj, "livechat_categories": livechat_categories, "admin_config": admin_config, "master_languages": master_languages, "config_obj": config_obj})
            else:
                return HttpResponse("You are not authorised to access this page.")
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AgentSettings: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class AgentIframeAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR

        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            session_id = data["session_id"]
            session_id = validation_obj.remo_html_from_string(session_id)
            try:
                livechat_cust_obj = LiveChatCustomer.objects.get(
                    session_id=session_id)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("AgentIframe: %s at %s", e, str(
                    exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            livechat_cust_obj.unread_message_count = 0
            livechat_cust_obj.save()

            if livechat_cust_obj.username == "not_available":
                username_display = session_id[:7]
            else:
                username_display = livechat_cust_obj.username

            livechat_cust_closing_category = livechat_cust_obj.closing_category
            closing_category = {}
            try:
                closing_category = {'id': livechat_cust_closing_category.pk,
                                    'name': livechat_cust_closing_category.title}
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Closing category not assigned during create customer: %s at %s", e, str(
                    exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            customer_obj = {
                'username': username_display,
                'bot_pk': livechat_cust_obj.bot.pk,
                'channel': livechat_cust_obj.channel.name,
                'easychat_user_id': str(livechat_cust_obj.easychat_user_id),
                'closing_category': closing_category,
                'is_external': livechat_cust_obj.is_external,
            }

            config_obj = LiveChatConfig.objects.get(bot=livechat_cust_obj.bot)
            category_enabled = config_obj.category_enabled

            all_categories_of_that_bot = list(LiveChatCategory.objects.filter(
                bot=livechat_cust_obj.bot, is_deleted=False).values('pk', 'title'))

            form_obj = LiveChatDisposeChatForm.objects.filter(
                bot=livechat_cust_obj.bot)

            is_form_enabled = False
            form = json.dumps({})
            if form_obj:
                is_form_enabled = form_obj[0].is_form_enabled
                form = form_obj[0].form

            # Get raise ticket form
            raise_ticket_form_obj = LiveChatRaiseTicketForm.objects.filter(
                bot=livechat_cust_obj.bot)

            raise_ticket_form = json.dumps({})
            if raise_ticket_form_obj:
                raise_ticket_form = raise_ticket_form_obj[0].form

            response = {
                'all_categories_of_that_bot': all_categories_of_that_bot,
                'category_enabled': category_enabled,
                'customer_obj': customer_obj,
                'is_form_enabled': is_form_enabled,
                'form': form,
                'raise_ticket_form': raise_ticket_form,
            }
            response["status_code"] = "200"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AgentIframe: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AgentIframe = AgentIframeAPI.as_view()


class EndChatSessionAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            session_id = data["session_id"]
            bot_id = data["bot_id"]
            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)

            if customer_obj.is_session_exp:
                response["status_code"] = "300"
                response["status_message"] = "Session Already Expired"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            diff = timezone.now() - customer_obj.joined_date

            customer_obj.is_session_exp = True
            customer_obj.chat_duration = diff.total_seconds() - customer_obj.queue_time
            customer_obj.last_appearance_date = timezone.now()

            if customer_obj.guest_agents.exists():
                guest_agent_objs = customer_obj.guest_agents.all()
                for guest_agent_obj in guest_agent_objs:
                    guest_session_status = json.loads(
                        customer_obj.guest_session_status)
                    if guest_session_status[guest_agent_obj.user.username] == "accept":
                        group_duration_start_time = LiveChatGuestAgentAudit.objects.filter(
                            livechat_customer=customer_obj, action="accept").order_by('-action_datetime')[0]
                        group_chat_duration = timezone.now() - group_duration_start_time.action_datetime
                        customer_obj.group_chat_duration += group_chat_duration.seconds
                        ongoing_chats = guest_agent_obj.ongoing_chats
                        ongoing_chats = max(ongoing_chats - 1, 0)
                        guest_agent_obj.ongoing_chats = ongoing_chats
                        guest_agent_obj.save()

            try:
                closing_category_pk = data["closing_category_pk"]
                if int(closing_category_pk) != -1:
                    customer_obj.closing_category = LiveChatCategory.objects.get(
                        pk=int(closing_category_pk))
            except Exception as e:
                closing_category_pk = -1
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Either category not enabled does not exist or coming from archived chats: %s at %s",
                             e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            if customer_obj.chat_ended_by != "Customer" and customer_obj.chat_ended_by != "System":
                customer_obj.chat_ended_by = "Agent"

            if 'is_email_chat_disposal' in data:
                customer_obj.chat_ended_by = "System"

            if 'is_auto_disposed' in data:
                customer_obj.is_auto_disposed = data['is_auto_disposed']

            if not customer_obj.is_external and customer_obj.channel.name != "Web":
                if Profile.objects.filter(livechat_session_id=session_id, livechat_connected=True).count():
                    user_obj = Profile.objects.get(
                        livechat_session_id=session_id)
                    
                    if user_obj.livechat_connected:
                        customer_language = customer_obj.customer_language
                        agent_left_text = AGENT_LEFT_THE_CHAT_TEXT
                        if customer_language and customer_language.lang != 'en':
                            agent_left_text = get_translated_text(agent_left_text, customer_language.lang, EasyChatTranslationCache)
                        
                        send_channel_based_text_message(
                            agent_left_text, customer_obj, user_obj.user_id)

                        bot_info_obj = BotInfo.objects.filter(bot=customer_obj.bot).first()
                        if bot_info_obj and bot_info_obj.show_welcome_msg_on_end_chat:
                            send_channel_based_welcome_message(user_obj, customer_obj)

                        user_obj.livechat_connected = False
                        user_obj.save()

            if customer_obj.is_external:
                push_livechat_event(END_CHAT_EVENT, customer_obj)

            if 'form_filled' in data:
                form_filled = data['form_filled']

                form_filled = clean_dynamic_form_data(form_filled)
                config_obj = LiveChatConfig.objects.get(bot=customer_obj.bot)
                category_enabled = config_obj.category_enabled

                if category_enabled and int(closing_category_pk) != -1 and form_filled != []:
                    closing_category = LiveChatCategory.objects.get(
                        pk=int(closing_category_pk)).title

                    form_filled.insert(0, {
                        'type': '6',
                        'label': 'Please Select Chat Category',
                        'value': closing_category
                    })

                customer_obj.form_filled = json.dumps(form_filled)

            customer_obj.save()

            if customer_obj.bot.use_end_chat_processor_livechat:
                processor_check_dictionary = {'open': open_file}
                code = LiveChatProcessors.objects.filter(bot=customer_obj.bot)[
                    0].end_chat_processor.function
                exec(str(code), processor_check_dictionary)
                parameter = customer_obj.client_id
                json_data = processor_check_dictionary['f'](parameter)

                if isinstance(json_data, (dict)):
                    response["processor_data"] = json.dumps(json_data)
                else:
                    response["processor_data"] = json_data

                if 'is_auto_disposed' in data:
                    if not isinstance(json_data, (dict)):
                        json_data = json.loads(json_data)

                    if 'form_filled' in json_data:
                        customer_obj.form_filled = json.dumps(
                            json_data['form_filled'])

                    customer_obj.save()
                try:
                    logger.info(response["processor_data"], extra={
                                'AppName': 'LiveChat'})
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("End Chat Processor: %s at %s",
                                 e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            # LiveChat VC session end
            if LiveChatVideoConferencing.objects.filter(meeting_id=session_id, is_expired=False):
                meeting_io = LiveChatVideoConferencing.objects.filter(
                    meeting_id=session_id, is_expired=False)[0]
                meeting_io.is_expired = True
                meeting_io.save()

            # Decreasing ongoing chats

            current_agent = customer_obj.agent_id
            ongoing_chats = current_agent.ongoing_chats
            ongoing_chats = max(ongoing_chats - 1, 0)
            current_agent.ongoing_chats = ongoing_chats
            current_agent.save()

            livechat_config_obj = LiveChatConfig.objects.get(
                bot=(Bot.objects.get(pk=int(bot_id))))
            masking_enabled = livechat_config_obj.masking_enabled

            if masking_enabled:
                mask_pii_data(customer_obj, LiveChatMISDashboard)

            response["status_code"] = "200"
            description = "Resolved chat for bot id " + \
                " (" + str(bot_id) + " and by agent with id " + \
                str(customer_obj.agent_id.user.pk) + ")"
            add_audit_trail(
                "LIVECHATAPP",
                customer_obj.agent_id.user,
                "End-Livechat-Session",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )
            send_event_for_report_creation(customer_obj, LiveChatUser, LiveChatAdminConfig, LiveChatConfig, Bot)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EndChatSessionAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EndChatSession = EndChatSessionAPI.as_view()


class AssignAgentAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            logger.info("inside assign agent", extra={'AppName': 'LiveChat'})
            session_id = data["session_id"]
            session_id = validation_obj.remo_html_from_string(session_id)
            try:
                livechat_cust_obj = LiveChatCustomer.objects.get(
                    session_id=session_id)
            except Exception:
                logger.warning(NO_SESSION_EXIST_TEXT,
                               extra={'AppName': 'LiveChat'})
                response["status_code"] = "200"
                response["status_message"] = "Success"
                response["assigned_agent"] = "None"
                response["assigned_agent_username"] = "None"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if livechat_cust_obj.agent_id == None:
                if livechat_cust_obj.is_ameyo_fusion_session and livechat_cust_obj.is_session_exp:
                    response["status_code"] = "200"
                    response["assigned_agent"] = "not_available"
                    response["livechat_notification"] = "Our chat representatives are unavailable right now. Please try again in some time."
                    response["assigned_agent_username"] = "None"
                else:
                    response["status_code"] = "200"
                    response["assigned_agent"] = "scheduler_queue"
                    response["assigned_agent_username"] = "None"
                    response["agent_websocket_token"] = "None"
            else:
                response["agent_websocket_token"] = get_agent_token(
                    livechat_cust_obj.agent_id.user.username)
                if livechat_cust_obj.is_session_exp and livechat_cust_obj.abruptly_closed:
                    response["status_code"] = "200"
                    response["assigned_agent"] = "abruptly_end"
                    response["assigned_agent_username"] = "None"
                elif livechat_cust_obj.is_session_exp == True:
                    response["status_code"] = "200"
                    response["assigned_agent"] = "session_end"
                    response["assigned_agent_username"] = "None"
                elif livechat_cust_obj.agent_id.is_session_exp == False and (livechat_cust_obj.is_ameyo_fusion_session or is_agent_live(livechat_cust_obj.agent_id)):
                    response["status_code"] = "200"

                    if str(livechat_cust_obj.agent_id.user.first_name) == "":
                        response["assigned_agent"] = str(
                            livechat_cust_obj.agent_id.user.username)
                    else:
                        response["assigned_agent"] = str(
                            livechat_cust_obj.agent_id.user.first_name) + " " + str(livechat_cust_obj.agent_id.user.last_name)

                    response["assigned_agent"] = wrap_do_not_translate_keywords(response["assigned_agent"])
                    response['joined_chat_text'] = f"{response['assigned_agent']} has joined the chat. Please ask your queries now."
                    response['warning_text_for_ios'] = "Please don't minimize the browser during interaction, to avoid disconnecting with the agent"
                    if livechat_cust_obj.customer_language and livechat_cust_obj.customer_language.lang != 'en':
                        response['joined_chat_text'] = get_translated_text(response['joined_chat_text'], livechat_cust_obj.customer_language.lang, EasyChatTranslationCache, False, True)
                        response['warning_text_for_ios'] = get_translated_text(response['warning_text_for_ios'], livechat_cust_obj.customer_language.lang, EasyChatTranslationCache)

                    response["assigned_agent_username"] = str(
                        livechat_cust_obj.agent_id.user.username)
                else:
                    response["status_code"] = "200"
                    response["assigned_agent"] = "not_available"
                    response["livechat_notification"] = "Agent has gone Offline"
                    response["assigned_agent_username"] = "None"

                    if livechat_cust_obj.customer_language and livechat_cust_obj.customer_language.lang != 'en':
                        response["livechat_notification"] = get_translated_text(response["livechat_notification"], livechat_cust_obj.customer_language.lang, EasyChatTranslationCache)

            response["status_message"] = "SUCCESS"

            # No need to log every request for assign agent
            """
            description = "Agent assigned for chat with bot_id " + \
                " (" + str(livechat_cust_obj.bot.pk) + " and assigned to agent with id " + \
                str(livechat_cust_obj.agent_id.user.pk) + ")"
            add_audit_trail(
                "LIVECHATAPP",
                livechat_cust_obj.agent_id.user,
                "Assign-Agent",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )
            """
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AssignAgentAPI: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AssignAgent = AssignAgentAPI.as_view()


class TransferChatAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            current_livechat_agent = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            selected_category = data["selected_category"]
            selected_agent = data["selected_agent"]
            session_id = data["session_id"]
            bot_pk = data["bot_pk"]
            cust_last_app_time = data["cust_last_app_time"]

            bot_obj = Bot.objects.get(pk=int(bot_pk))
            livechat_cust_obj = LiveChatCustomer.objects.get(
                session_id=session_id)
            livechat_config_obj = LiveChatConfig.objects.get(bot=bot_obj)
            if selected_agent != "-1":
                transferred_livechat_agent = LiveChatUser.objects.get(
                    pk=int(selected_agent), is_deleted=False)
                max_customer_count = transferred_livechat_agent.max_customers_allowed
                if max_customer_count == -1:
                    max_customer_count = livechat_config_obj.max_customer_count
            else:
                max_customer_count = livechat_config_obj.max_customer_count
            category_obj = get_livechat_category_object(
                selected_category, bot_obj, LiveChatCategory)
            livechat_cust_obj.closing_category = category_obj
            livechat_cust_obj.save()

            response["new_agent_websocket_token"] = "None"

            transfer_session_data = {"current_livechat_agent": current_livechat_agent, "livechat_cust_obj": livechat_cust_obj,
                                     "max_customer_count": max_customer_count, "cust_last_app_time": cust_last_app_time}

            if selected_agent == "-1" and current_livechat_agent.status == "3":

                response = auto_assign_agent(
                    transfer_session_data, category_obj, data, request)

            elif current_livechat_agent.status == "3":

                response = assign_selected_agent(
                    transfer_session_data, selected_agent, data, request)

            if livechat_cust_obj.is_external and response['status_code'] == '200':
                extra_details = {
                    'previous_agent_name': response['previous_assigned_agent'],
                    'assigned_agent_name': response['assigned_agent']
                }

                push_livechat_event(TRANSFER_CHAT_EVENT,
                                    livechat_cust_obj, extra_details)

            if response["assigned_agent_username"] != "None":
                response["new_agent_websocket_token"] = get_agent_token(
                    response["assigned_agent_username"])
                
                message_to_customer = f'{response["previous_assigned_agent"]} has transferred the chat to {response["assigned_agent"]}'

                if livechat_cust_obj.customer_language:
                    message_to_customer = get_translated_text(message_to_customer, livechat_cust_obj.customer_language.lang, EasyChatTranslationCache)

                response['message_to_customer'] = message_to_customer
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside TransferChatAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


TransferChat = TransferChatAPI.as_view()


class InviteGuestAgentAPI(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            current_livechat_agent = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            guest_agents = data["guest_agents"]
            session_id = data["session_id"]
            bot_pk = data["bot_pk"]

            bot_obj = Bot.objects.get(pk=int(bot_pk))
            livechat_cust_obj = LiveChatCustomer.objects.get(
                session_id=session_id)
            livechat_config_obj = LiveChatConfig.objects.get(bot=bot_obj)
            current_guest_agents = livechat_cust_obj.guest_agents.all()
            response["new_agent_websocket_token"] = "None"

            invited_agents_data = []
            for guest_agent in guest_agents:
                guest_livechat_agent = LiveChatUser.objects.get(
                    pk=int(guest_agent.strip()), is_deleted=False)

                if guest_livechat_agent not in current_guest_agents:

                    max_customer_count = guest_livechat_agent.max_customers_allowed
                    if max_customer_count == -1:
                        max_customer_count = livechat_config_obj.max_customer_count

                    if current_livechat_agent.status == "3":
                        LiveChatGuestAgentAudit.objects.create(
                            livechat_customer=livechat_cust_obj,
                            livechat_agent=current_livechat_agent,
                            action="request")
                        livechat_agent = LiveChatUser.objects.get(
                            pk=int(guest_agent), is_deleted=False)
                        current_assigned_customer_count = LiveChatCustomer.objects.filter(
                            is_session_exp=False, request_raised_date=datetime.datetime.now().date(), agent_id=livechat_agent).count()

                        agent_name = str(
                            livechat_agent.user.first_name) + " " + str(livechat_agent.user.last_name)
                        agent_username = str(
                            livechat_agent.user.username)
                        if max_customer_count > current_assigned_customer_count and livechat_agent.is_online:

                            livechat_cust_obj.guest_agents.add(livechat_agent)
                            guest_session_status = json.loads(
                                livechat_cust_obj.guest_session_status)
                            guest_session_status[livechat_agent.user.username] = "onhold"
                            livechat_cust_obj.guest_session_status = json.dumps(
                                guest_session_status)
                            livechat_cust_obj.save()
                            invited_agents_data.append(
                                [{"status": "available", "name": agent_name, "username": agent_username}])

                            description = "Invite Guest with id " + \
                                " (" + str(guest_livechat_agent.pk) + \
                                " by agent with id " + \
                                str(current_livechat_agent.pk) + ")"
                            add_audit_trail(
                                "LIVECHATAPP",
                                current_livechat_agent.user,
                                "Invite-Guest",
                                description,
                                json.dumps(data),
                                request.META.get("PATH_INFO"),
                                request.META.get('HTTP_X_FORWARDED_FOR')
                            )
                        else:
                            logger.info(
                                "Into InviteGuestAgentAPI.....max_customer_count exceeded", extra={'AppName': 'LiveChat'})
                            invited_agents_data.append(
                                [{"status": "unavailable", "name": agent_name, "username": agent_username}])

                        response["session_id"] = str(
                            livechat_cust_obj.session_id)
                        response["guest_agents_data"] = invited_agents_data
                        response["guest_agent_timer"] = livechat_config_obj.guest_agent_timer

                response["status_code"] = "200"
                response["status_message"] = "Success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside InviteGuestAgentAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


InviteGuestAgent = InviteGuestAgentAPI.as_view()


class GuestAgentAcceptAPI(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            livechat_agent = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            bot_pk = data["bot_pk"]
            session_id = data["session_id"]

            bot_obj = Bot.objects.get(pk=int(bot_pk))
            livechat_cust_obj = LiveChatCustomer.objects.get(
                session_id=session_id)
            livechat_config_obj = LiveChatConfig.objects.get(bot=bot_obj)

            max_customer_count = livechat_agent.max_customers_allowed
            if max_customer_count == -1:
                max_customer_count = livechat_config_obj.max_customer_count

            if livechat_agent.status == "3":
                LiveChatGuestAgentAudit.objects.create(
                    livechat_customer=livechat_cust_obj,
                    livechat_agent=livechat_agent,
                    action="accept")
                current_assigned_customer_count = LiveChatCustomer.objects.filter(
                    is_session_exp=False, request_raised_date=datetime.datetime.now().date(), agent_id=livechat_agent).count()
                if max_customer_count > current_assigned_customer_count:
                    livechat_agent.ongoing_chats = current_assigned_customer_count + 1
                    livechat_agent.save()

                    guest_session_status = json.loads(
                        livechat_cust_obj.guest_session_status)
                    guest_session_status[livechat_agent.user.username] = "accept"
                    livechat_cust_obj.guest_session_status = json.dumps(
                        guest_session_status)
                    livechat_cust_obj.save()
                    response["status_code"] = "200"
                    response["assigned_agent"] = str(
                        livechat_agent.user.first_name) + " " + str(livechat_agent.user.last_name)
                    response["assigned_agent_username"] = str(
                        livechat_agent.user.username)

                    message_to_customer = f"{response['assigned_agent']} has joined the chat"

                    if livechat_cust_obj.customer_language:
                        message_to_customer = get_translated_text(message_to_customer, livechat_cust_obj.customer_language.lang, EasyChatTranslationCache)

                    response['message_to_customer'] = message_to_customer

                    if livechat_cust_obj.is_external:
                        extra_details = {
                            'added_agent_name': response["assigned_agent"]
                        }

                        push_livechat_event(
                            ADD_AGENT_EVENT, livechat_cust_obj, extra_details)

                else:
                    logger.info(
                        "Into GuestAgentAccept.....max_customer_count exceeded", extra={'AppName': 'LiveChat'})
                    response["status_code"] = "300"
                    response["assigned_agent"] = "agent_not_available"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside GuestAgentAcceptAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GuestAgentAccept = GuestAgentAcceptAPI.as_view()


class GuestAgentRejectAPI(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            livechat_agent = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            session_id = data["session_id"]

            livechat_cust_obj = LiveChatCustomer.objects.get(
                session_id=session_id)

            if livechat_agent.status == "3":
                LiveChatGuestAgentAudit.objects.create(
                    livechat_customer=livechat_cust_obj,
                    livechat_agent=livechat_agent,
                    action="reject")

                guest_session_status = json.loads(
                    livechat_cust_obj.guest_session_status)
                guest_session_status[livechat_agent.user.username] = "reject"
                livechat_cust_obj.guest_session_status = json.dumps(
                    guest_session_status)
                livechat_cust_obj.guest_agents.remove(livechat_agent)
                livechat_cust_obj.save()
                response["status_code"] = "200"
                response["status_message"] = "success"
                response["agent_name"] = str(
                    livechat_agent.user.first_name) + " " + str(livechat_agent.user.last_name)
                response["assigned_agent_username"] = str(
                    livechat_agent.user.username)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside GuestAgentRejectAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GuestAgentReject = GuestAgentRejectAPI.as_view()


class GuestAgentExitAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            livechat_agent = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            session_id = data["session_id"]

            livechat_cust_obj = LiveChatCustomer.objects.get(
                session_id=session_id)

            if livechat_agent.status == "3":
                LiveChatGuestAgentAudit.objects.create(
                    livechat_customer=livechat_cust_obj,
                    livechat_agent=livechat_agent,
                    action="exit")
                ongoing_chats = livechat_agent.ongoing_chats
                ongoing_chats = max(ongoing_chats - 1, 0)
                livechat_agent.ongoing_chats = ongoing_chats
                livechat_agent.save()

                group_duration_start_time = LiveChatGuestAgentAudit.objects.filter(
                    livechat_customer=livechat_cust_obj, livechat_agent=livechat_agent, action="accept").order_by('-action_datetime')[0]
                group_chat_duration = timezone.now() - group_duration_start_time.action_datetime
                livechat_cust_obj.group_chat_duration += group_chat_duration.seconds

                guest_session_status = json.loads(
                    livechat_cust_obj.guest_session_status)
                guest_session_status[livechat_agent.user.username] = "exit"
                livechat_cust_obj.guest_session_status = json.dumps(
                    guest_session_status)
                livechat_cust_obj.guest_agents.remove(livechat_agent)
                livechat_cust_obj.save()

                response["status_code"] = "200"
                response["status_message"] = "success"
                response["agent_name"] = str(
                    livechat_agent.user.first_name) + " " + str(livechat_agent.user.last_name)

                message_to_customer = f"{response['agent_name']} has left the chat"

                if livechat_cust_obj.customer_language:
                    message_to_customer = get_translated_text(message_to_customer, livechat_cust_obj.customer_language.lang, EasyChatTranslationCache)

                response['message_to_customer'] = message_to_customer

                if livechat_cust_obj.is_external:
                    extra_details = {
                        'exit_agent_name': response["agent_name"]
                    }

                    push_livechat_event(
                        EXIT_AGENT_EVENT, livechat_cust_obj, extra_details)

                description = "Exited guest session chat for bot id " + \
                    " (" + str(livechat_cust_obj.bot.pk) + \
                    " and by agent with id " + str(livechat_agent.pk) + ")"
                add_audit_trail(
                    "LIVECHATAPP",
                    livechat_agent.user,
                    "Exit-Guest-Session",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside GuestAgentExitAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GuestAgentExit = GuestAgentExitAPI.as_view()


class GuestAgentNoResponseAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            livechat_agent = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            session_id = data["session_id"]

            livechat_cust_obj = LiveChatCustomer.objects.get(
                session_id=session_id)

            if livechat_agent.status == "3":
                LiveChatGuestAgentAudit.objects.create(
                    livechat_customer=livechat_cust_obj,
                    livechat_agent=livechat_agent,
                    action="no_response")

                guest_session_status = json.loads(
                    livechat_cust_obj.guest_session_status)
                guest_session_status[livechat_agent.user.username] = "no_response"
                livechat_cust_obj.guest_session_status = json.dumps(
                    guest_session_status)
                livechat_cust_obj.guest_agents.remove(livechat_agent)
                livechat_cust_obj.save()
                response["status_code"] = "200"
                response["status_message"] = "success"
                response["agent_name"] = str(
                    livechat_agent.user.first_name) + " " + str(livechat_agent.user.last_name)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside GuestAgentNoResponseAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GuestAgentNoResponse = GuestAgentNoResponseAPI.as_view()


class UpdateGuestAgentStatusAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            livechat_agent = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            session_id = data["session_id"]

            livechat_cust_obj = LiveChatCustomer.objects.get(
                session_id=session_id)

            if livechat_agent.status == "3":
                agent_names = {}
                guest_session_status = livechat_cust_obj.guest_session_status
                for agent in json.loads(guest_session_status):
                    user_obj = User.objects.get(username=str(agent))
                    agent_names[agent] = str(
                        user_obj.first_name) + ' ' + str(user_obj.last_name)

                response["status_code"] = "200"
                response["status_message"] = "success"
                response["guest_session_status"] = guest_session_status
                response["agent_names"] = json.dumps(agent_names)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside UpdateGuestAgentStatusAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateGuestAgentStatus = UpdateGuestAgentStatusAPI.as_view()


class GetLiveChatAgentsAPI(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            selected_category = data["selected_category"]
            bot_id = data["bot_id"]
            bot_obj = Bot.objects.get(pk=bot_id)
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            response["current_agent_pk"] = user_obj.pk
            response["agent_list"] = []

            agent_list = get_allowed_livechat_user(
                user_obj, selected_category, bot_obj, LiveChatUser, LiveChatCategory)

            for agent_obj in agent_list:
                response["agent_list"].append({"pk": agent_obj.pk, "name": agent_obj.user.first_name + " " +
                                               agent_obj.user.last_name, "username": agent_obj.user.username})

            response["status_code"] = "200"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside GetLiveChatAgentsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatAgents = GetLiveChatAgentsAPI.as_view()


class GetAgentsGroupChatAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            selected_category = data["selected_category"]
            bot_id = data["bot_id"]
            bot_obj = Bot.objects.get(pk=bot_id)
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            livechat_config_obj = LiveChatConfig.objects.get(bot=bot_obj)

            response["current_agent_pk"] = user_obj.pk
            response["agent_list"] = []

            if int(selected_category) == -1:
                agent_list = LiveChatUser.objects.filter(
                    is_deleted=False, status="3", bots__in=[bot_obj], is_online=True)
            else:
                agent_list = LiveChatUser.objects.filter(is_deleted=False, status="3", bots__in=[
                                                         bot_obj], category=LiveChatCategory.objects.get(pk=int(selected_category)), is_online=True)

            for agent_obj in agent_list:
                max_customer_count = agent_obj.max_customers_allowed

                if max_customer_count == -1:
                    max_customer_count = livechat_config_obj.max_customer_count
                current_assigned_customer_count = LiveChatCustomer.objects.filter(
                    is_session_exp=False, request_raised_date=datetime.datetime.now().date(), agent_id=agent_obj).count()

                if max_customer_count > current_assigned_customer_count:
                    agent_session_ids = list(LiveChatCustomer.objects.filter(
                        guest_agents=agent_obj, is_session_exp=False, bot__in=[bot_obj]).values_list('session_id', flat=True))
                    agent_session_ids = [str(agent_session_id)
                                         for agent_session_id in agent_session_ids]
                    response["agent_list"].append({"pk": agent_obj.pk, "name": agent_obj.user.first_name + " " +
                                                   agent_obj.user.last_name, "username": agent_obj.user.username, "session_ids": agent_session_ids})

            response["status_code"] = "200"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside GetAgentsGroupChatAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetAgentsGroupChat = GetAgentsGroupChatAPI.as_view()


class GetCustomerDetailsAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = 500
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            session_id = data["session_id"]
            session_id = validation_obj.remo_html_from_string(session_id)

            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)

            response["category"] = customer_obj.category.title
            response["session_id"] = session_id
            response["customer_status"] = customer_obj.is_online
            response["assigned_agent"] = customer_obj.agent_id.user.first_name + " " + \
                customer_obj.agent_id.user.last_name + \
                "(" + customer_obj.agent_id.user.username + ")"
            response["previous_assigned_agent"] = customer_obj.get_previous_agents()
            response["name"] = customer_obj.username
            response["is_session_exp"] = customer_obj.is_session_exp
            response["joined_time"] = get_time(customer_obj.joined_date)
            response["joined_date"] = get_livechat_date_format(
                customer_obj.joined_date)
            response["chat_duration"] = customer_obj.get_chat_duration()
            response["bot_name"] = customer_obj.get_bot_name()
            response["rate_value"] = customer_obj.rate_value
            response["email"] = customer_obj.email
            response["phone"] = customer_obj.phone
            response["wait_time"] = customer_obj.get_wait_time()
            response["bot_id"] = customer_obj.bot.pk
            response[
                "show_details_from_processor"] = customer_obj.bot.use_show_customer_detail_livechat_processor

            timer_inital = timezone.now() - customer_obj.joined_date
            response["timer_inital"] = int(timer_inital.total_seconds())

            if(customer_obj.bot.use_show_customer_detail_livechat_processor):
                processor_check_dictionary = {'open': open_file}
                if LiveChatProcessors.objects.filter(bot=customer_obj.bot):
                    code = LiveChatProcessors.objects.filter(bot=customer_obj.bot)[
                        0].show_customer_details_processor.function
                    exec(str(code), processor_check_dictionary)
                    parameter = customer_obj.client_id
                    json_data = processor_check_dictionary['f'](parameter)
                    response["processor_data"] = [
                        {"key": "Error", "value": "Error in fetching the data"}]
                    if isinstance(json_data, (dict)):
                        if json_data["status_code"] == "200":
                            user_details = json_data["user_details"]
                            response["processor_data"] = user_details
                    else:
                        json_data = json.loads(json_data)
                        if json_data["status_code"] == "200":
                            user_details = json_data["user_details"]
                            response["processor_data"] = user_details
                else:
                    response["processor_data"] = [
                        {"key": "Error", "value": "Error in fetching the data"}]
            response["status_code"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside GetCustomerDetailsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = 500
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetCustomerDetails = GetCustomerDetailsAPI.as_view()


class SaveAgentGeneralSettingsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            notification = data["notification"]
            preferred_languages = data["preferred_languages"]

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            if user_obj.status == "3":
                user_obj.notification = notification

                if len(preferred_languages) > 0:
                    user_obj.preferred_languages.clear()
                    for preferred_language in preferred_languages:
                        lang_obj = Language.objects.get(lang=preferred_language)
                        user_obj.preferred_languages.add(lang_obj)

                user_obj.save()
                response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveAgentGeneralSettingsAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveAgentGeneralSettings = SaveAgentGeneralSettingsAPI.as_view()


class UpdateMessageHistoryAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            session_id = data["session_id"]
            refresh_customer_details = data["refresh_customer_details"]

            try:
                livechat_cust_obj = LiveChatCustomer.objects.get(
                    session_id=session_id)
                livechat_cust_obj.unread_message_count = 0
                livechat_cust_obj.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("UpdateMessageHistoryAPI: %s at %s", str(e), str(
                    exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                response["status"] = 500
                response["message"] = NO_SESSION_EXIST_TEXT
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if not refresh_customer_details:
                cust_last_app_time = round(
                    livechat_cust_obj.last_appearance_date.timestamp() * 1000)

                cust_last_updated_time = livechat_cust_obj.last_appearance_date.time().strftime("%H:%M")

                # Creating chat objects of bot and customer messages.
                update_message_history_till_now(
                    livechat_cust_obj, LiveChatMISDashboard, MISDashboard)

                response["message_history"] = get_message_history(
                    livechat_cust_obj, False, LiveChatMISDashboard, LiveChatTranslationCache)
                response["cust_last_app_time"] = cust_last_app_time
                response["cust_last_updated_time"] = cust_last_updated_time

            response["category"] = livechat_cust_obj.category.title
            response["session_id"] = session_id
            response["customer_status"] = livechat_cust_obj.is_online
            response["assigned_agent"] = livechat_cust_obj.agent_id.user.first_name + " " + \
                livechat_cust_obj.agent_id.user.last_name + \
                "(" + livechat_cust_obj.agent_id.user.username + ")"
            response[
                "previous_assigned_agent"] = livechat_cust_obj.get_previous_agents()
            response["name"] = livechat_cust_obj.username
            response["is_session_exp"] = livechat_cust_obj.is_session_exp
            response["joined_time"] = get_time(livechat_cust_obj.joined_date)
            response["joined_date"] = get_livechat_date_format(
                livechat_cust_obj.joined_date)
            response["chat_duration"] = livechat_cust_obj.get_chat_duration()
            response["bot_name"] = livechat_cust_obj.get_bot_name()
            response["rate_value"] = livechat_cust_obj.rate_value
            response["email"] = livechat_cust_obj.email
            response["phone"] = livechat_cust_obj.phone
            response["wait_time"] = livechat_cust_obj.get_wait_time()
            response["bot_id"] = livechat_cust_obj.bot.pk
            response[
                "show_details_from_processor"] = livechat_cust_obj.bot.use_show_customer_detail_livechat_processor

            timer_inital = timezone.now() - livechat_cust_obj.joined_date
            response["initial_time"] = int(timer_inital.total_seconds())
            response["active_url"] = livechat_cust_obj.active_url
            response["client_id"] = livechat_cust_obj.client_id
            response["phone_country_code"] = livechat_cust_obj.phone_country_code
            response["email_initiated_at"] = get_livechat_email_initiated_time(livechat_cust_obj, LiveChatMISEmailData)
            response["email_initiated_on"] = get_livechat_email_initiated_date(livechat_cust_obj, LiveChatMISEmailData)

            if(livechat_cust_obj.bot.use_show_customer_detail_livechat_processor):
                processor_check_dictionary = {'open': open_file}
                code = LiveChatProcessors.objects.filter(bot=livechat_cust_obj.bot)[
                    0].show_customer_details_processor.function

                user = Profile.objects.filter(
                    user_id=livechat_cust_obj.easychat_user_id)[0]
                processed_code = replace_data_values(user, code, '', '', '')

                exec(str(processed_code), processor_check_dictionary)
                parameter = livechat_cust_obj.client_id
                json_data = processor_check_dictionary['f'](parameter)
                response["custom_data"] = [
                    {"key": "Error", "value": "Error in fetching the data"}]
                if isinstance(json_data, (dict)):
                    if json_data["status_code"] == "200":
                        user_details = json_data["user_details"]
                        response["custom_data"] = user_details
                else:
                    json_data = json.loads(json_data)
                    if json_data["status_code"] == "200":
                        user_details = json_data["user_details"]
                        response["custom_data"] = user_details
            else:
                response['custom_data'] = json.loads(
                    livechat_cust_obj.customer_details)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateMessageHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateMessageHistory = UpdateMessageHistoryAPI.as_view()


class LiveChatUploadAttachmentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}

        try:
            data = request.data
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            uploaded_file_encrypted_data = data["uploaded_file"]
            uploaded_file_encrypted_data = DecryptVariable(
                uploaded_file_encrypted_data)
            uploaded_file_encrypted_data = json.loads(
                uploaded_file_encrypted_data)
            file_name = uploaded_file_encrypted_data[0]["filename"]
            file_name = validation_obj.remo_html_from_string(file_name)
            file_name = file_name.replace(" ", "")
            base64_content = uploaded_file_encrypted_data[0]["base64_file"]

            session_id = uploaded_file_encrypted_data[0]["session_id"]
            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)
            agent_obj = customer_obj.agent_id
            
            admin_config = get_admin_config(
                agent_obj, LiveChatAdminConfig, LiveChatUser)

            is_special_charater_allow_in_file_name = admin_config.is_special_character_allowed_in_file_name
            
            if is_special_charater_allow_in_file_name:
                file_name = validation_obj.replace_special_character_in_file_name(file_name)
            elif(validation_obj.is_special_character_present_in_file_name(file_name)):
                response['status'] = 300
                response['status_message'] = 'Special characters are not allowed in file name'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            status, status_message = check_if_uploded_livechat_file_is_valid(
                base64_content, file_name)

            if status == 500:
                response['status'] = status
                response['status_message'] = status_message
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            file_url, thumbnail_url = save_file_and_get_source_file_path_and_thumbnail_path(
                base64_content, file_name, LiveChatFileAccessManagement)

            response["status"] = 200
            response["src"] = file_url
            response["name"] = file_name
            response["thumbnail_url"] = thumbnail_url

            if customer_obj.channel.name != "Web":

                channel_name = customer_obj.channel.name.lower()

                folder_name = channel_name + "-attachment/"

                if not os.path.exists('files/' + folder_name):
                    os.makedirs('files/' + folder_name)

                path = os.path.join(settings.MEDIA_ROOT,
                                    folder_name)

                file_name = file_name.replace(" ", "_")
                fh = open(path + file_name, "wb")
                fh.write(base64.b64decode(base64_content))
                fh.close()

                path = "/files/" + folder_name + file_name
                response["channel_file_url"] = path

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside LiveChatUploadAttachmentAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status"] = 500
            response["name"] = "no_name"
            response["src"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LiveChatUploadAttachment = LiveChatUploadAttachmentAPI.as_view()


class GetMessageHistoryAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)
            session_id = data["livechat_session_id"]
            try:
                livechat_cust_obj = LiveChatCustomer.objects.filter(
                    session_id=session_id).first()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Livechat customer does not exists: %s at %s", e, str(
                    exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

                response["status"] = 500
                response["message"] = NO_SESSION_EXIST_TEXT
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            cust_last_app_time = round(
                livechat_cust_obj.last_appearance_date.timestamp() * 1000)
            response["status"] = 200
            response["message"] = "success"
            response["message_history"] = get_message_history(
                livechat_cust_obj, True, LiveChatMISDashboard, LiveChatTranslationCache)
            response["livechat_customer_name"] = livechat_cust_obj.username
            if livechat_cust_obj.agent_id:
                response["agent_websocket_token"] = get_agent_token(livechat_cust_obj.agent_id.user.username)
                response["agent_name"] = livechat_cust_obj.agent_id.get_agent_name()
                response['assigned_agent_username'] = livechat_cust_obj.agent_id.user.username

            response["cust_last_app_time"] = cust_last_app_time

            config_obj = LiveChatConfig.objects.filter(bot=livechat_cust_obj.bot).first()

            response['queue_time'] = config_obj.queue_timer - (timezone.now() - livechat_cust_obj.joined_date).seconds

            if response['queue_time'] <= 0 and not livechat_cust_obj.agent_id and not livechat_cust_obj.is_session_exp and not livechat_cust_obj.chat_ended_by:
                response['is_queue_time_exceed'] = True
            elif not livechat_cust_obj.agent_id and not livechat_cust_obj.is_session_exp and not livechat_cust_obj.chat_ended_by:
                response['is_queue_time_exceed'] = False

            # cobrowsing info
            response['cobrowsing_status'], response['cobrowsing_meeting_id'] = get_cobrowsing_status(livechat_cust_obj, LiveChatCobrowsingData)
            response['customer_details'] = {
                'username': livechat_cust_obj.username,
                'phone': livechat_cust_obj.phone,
                'email': livechat_cust_obj.email,
            }

            # voip info
            meeting_id = ""
            livechat_voip_start_time = ""
            livechat_voip_object = LiveChatVoIPData.objects.filter(customer=livechat_cust_obj, is_started=True, is_completed=False).order_by('-pk')

            if livechat_voip_object.exists():
                meeting_id = livechat_voip_object[0].meeting_id
                livechat_voip_start_time = int(livechat_voip_object[0].start_datetime.timestamp() * 1000)

            response["meeting_id"] = str(meeting_id)
            response["livechat_voip_start_time"] = livechat_voip_start_time
            response["is_transcript_request"] = livechat_cust_obj.is_transcript_request_enabled

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetMessageHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetMessageHistory = GetMessageHistoryAPI.as_view()


class LiveChatMarkChatAbandonedAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            session_id = data["session_id"]
            is_abandoned = data["is_abandoned"]
            is_abruptly_closed = data["is_abruptly_closed"]
            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)
            queue_time = (timezone.now() - customer_obj.joined_date).seconds
            customer_obj.is_online = False
            if customer_obj.agent_id == None:
                customer_obj.is_session_exp = True
                customer_obj.is_denied = False
                customer_obj.abruptly_closed = is_abruptly_closed
                customer_obj.queue_time = queue_time
                if is_abandoned == True or is_abandoned == "true" or is_abandoned == "True":
                    customer_obj.is_denied = True
                    send_event_for_missed_chat(customer_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)
                customer_obj.last_appearance_date = datetime.datetime.now()
                if customer_obj.abruptly_closed:
                    send_event_for_abandoned_chat(customer_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)
            if customer_obj.guest_agents.exists():
                customer_obj.guest_agents.clear()
            if customer_obj.chat_ended_by == "":
                customer_obj.chat_ended_by = "System"
            customer_obj.save()

            response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LiveChatMarkChatAbandonedAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LiveChatMarkChatAbandoned = LiveChatMarkChatAbandonedAPI.as_view()


class SaveAgentChatAPI(APIView):

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
            attached_file_src = data["attached_file_src"]

            is_message_length_validation_required = True
            if attached_file_src.strip() and message.strip() == "":
                is_message_length_validation_required = False
            
            customer_obj = LiveChatCustomer.objects.filter(session_id=session_id).first()

            if is_message_length_validation_required and not check_if_sentence_valid(message, customer_obj.channel.name):
                response["status_code"] = "300"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
                
            sender = data["sender"]
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

            to_translate_message = False
            if "to_translate_message" in data:
                to_translate_message = data["to_translate_message"]

            is_whatsapp_reinitiating_request = False
            if "is_whatsapp_reinitiating_request" in data:
                is_whatsapp_reinitiating_request = data["is_whatsapp_reinitiating_request"]
            
            session_id = validation_obj.remo_html_from_string(session_id)
            agent_obj = customer_obj.agent_id

            if customer_obj.agent_first_time_response_time == None and sender == 'Agent':
                connected_time = customer_obj.joined_date
                time_now = timezone.now()
                time_diff = (time_now - connected_time).total_seconds()
                time_diff = time_diff - customer_obj.queue_time

                customer_obj.agent_first_time_response_time = time_diff
                customer_obj.save(
                    update_fields=['agent_first_time_response_time'])

            if (message != None and message != "") or attached_file_src != "":
                admin_config = get_admin_config(
                    agent_obj, LiveChatAdminConfig, LiveChatUser)
                is_special_charater_allow = admin_config.is_special_character_allowed_in_chat
                message = validation_obj.remo_html_from_string(message)
                if (not validation_obj.is_valid_url(message) and not is_special_charater_allow):
                    message = validation_obj.remove_special_charater_from_string(message)
                    if message == "" and attached_file_src == "":
                        response["status_code"] = "300"
            else:
                response["status_code"] = "300"
            
            if response["status_code"] == "300":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if is_whatsapp_reinitiating_request:
                followup_customer_obj = LiveChatFollowupCustomer.objects.filter(livechat_customer=customer_obj).first()
                agent_obj = followup_customer_obj.agent_id

            channel_message = message
            attached_file_src = validation_obj.remo_html_from_string(
                attached_file_src)

            if sender_name == "":
                sender_name = str(agent_obj.user.first_name) + \
                    " " + str(agent_obj.user.last_name)
            if sender == "System":
                sender_name = "system"

            attachment_file_name = ""
            if attached_file_src != "":
                attachment_file_name = attached_file_src.split("/")[-1]
            logger.info("inside SaveAgentChatAPI:",
                        extra={'AppName': 'LiveChat'})

            # This translated text is stored for customer end.
            translated_text = ""
            customer_language = "en"

            if customer_obj.customer_language:
                customer_language = customer_obj.customer_language.lang

            if to_translate_message:
                if not validation_obj.is_valid_url(message):
                    translated_text = get_translated_text(message, customer_language, LiveChatTranslationCache)
                else:
                    translated_text = message
              
            is_voice_call_message = False
            if 'voice_call_notification' in data:
                is_voice_call_message = data['voice_call_notification']
                sender_username = request.user.username

            is_video_call_message = False
            if 'video_call_notification' in data:
                is_video_call_message = data['video_call_notification']
                sender_username = request.user.username

            is_cobrowsing_message = False
            if 'cobrowsing_notification' in data:
                is_cobrowsing_message = data['cobrowsing_notification']
                sender_username = request.user.username

            is_customer_warning_message = False
            if 'is_customer_warning_message' in data:
                is_customer_warning_message = data['is_customer_warning_message']

            is_customer_report_message_notification = False
            if 'is_customer_report_message_notification' in data:
                is_customer_report_message_notification = data['is_customer_report_message_notification']

            message_for = 'primary_agent'
            if 'for_guest_agent' in data:
                message_for = 'guest_agent'

            livechat_mis_obj = LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                                                   sender=sender,
                                                                   text_message=message,
                                                                   sender_name=sender_name,
                                                                   message_time=timezone.now(),
                                                                   attachment_file_name=attachment_file_name,
                                                                   attachment_file_path=attached_file_src,
                                                                   thumbnail_file_path=thumbnail_file_src,
                                                                   is_guest_agent_message=is_guest_agent_message,
                                                                   sender_username=sender_username,
                                                                   translated_text=translated_text,
                                                                   is_voice_call_message=is_voice_call_message,
                                                                   is_video_call_message=is_video_call_message,
                                                                   is_cobrowsing_message=is_cobrowsing_message,
                                                                   message_for=message_for,
                                                                   is_customer_warning_message=is_customer_warning_message,
                                                                   is_customer_report_message_notification=is_customer_report_message_notification)

            customer_obj.unread_message_count = 0

            # check if chat is auto resolved by System
            user_obj = None
            bot_info_obj = None
            is_inactivity_msg = False

            if 'inactivity_chat' in data and data['inactivity_chat']:
                is_inactivity_msg = True
                user_obj = Profile.objects.filter(livechat_session_id=session_id).first()
                bot_info_obj = BotInfo.objects.filter(bot=customer_obj.bot).first()

            if sender == "System" and message.lower() == "due to inactivity chat has ended" and customer_obj.chat_ended_by != "Customer" and customer_obj.chat_ended_by != "Agent":
                customer_obj.chat_ended_by = "System"
            customer_obj.save()

            if not customer_obj.is_external and customer_obj.channel.name != "Web" and (sender != "System" or message.lower() != CUSTOMER_LEFT_THE_CHAT):
                if sender != "System" or (message.lower() != "customer details updated" and "video call" not in message.lower() and "voice call" not in message.lower() and message.lower() != CHAT_RESOLVED_BY_AGENT and message.lower() != WARNING_MESSAGE_NOTIF and message.lower() != REPORT_MESSAGE_NOTIF and message.lower() != WHATSAPP_REINITIATING_MESSAGE):
                    send_agent_livechat_response_based_on_channel(
                        customer_obj, session_id, channel_message, attached_file_src, data, sender_name, translated_text)
                
                if is_inactivity_msg and user_obj and bot_info_obj and bot_info_obj.show_welcome_msg_on_end_chat:
                    send_channel_based_welcome_message(user_obj, customer_obj)
                    user_obj.livechat_connected = False
                    user_obj.save(update_fields=['livechat_connected'])

            elif is_inactivity_msg and user_obj and user_obj.livechat_connected:
                user_obj.livechat_connected = False
                user_obj.save(update_fields=['livechat_connected'])

            if customer_obj.is_external:
                if attached_file_src != '' and settings.EASYCHAT_DOMAIN not in attached_file_src:
                    attached_file_src = f'{settings.EASYCHAT_HOST_URL}{attached_file_src}'

                extra_details = {
                    'message': message,
                    'attached_file_src': attached_file_src,
                    'sender': sender,
                }

                push_livechat_event(SEND_MESSAGE_EVENT,
                                    customer_obj, extra_details)

            response["status_code"] = "200"
            response["message_id"] = str(livechat_mis_obj.message_id)
            response["translated_text"] = translated_text

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveAgentChatAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveAgentChat = SaveAgentChatAPI.as_view()


class CreateCustomerRoomAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            logger.info("inside room creation", extra={'AppName': 'LiveChat'})
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)
            bot_id = data["bot_id"]
            username = data["username"]
            phone = data["phone"]
            email = data["email"]
            livechat_category = data["livechat_category"]
            message = data["message"]
            easychat_user_id = data["easychat_user_id"]
            channel = "Web"
            active_url = data["active_url"]
            customer_details = data['customer_details']
            bot_obj = Bot.objects.get(pk=int(bot_id))
            client_id = phone
            is_valid_number = False

            if bot_obj.show_livechat_form_or_no:
                phone_number, country_code, is_valid_number = get_phone_number_and_country_code(phone, channel)

            validation_obj = LiveChatInputValidation()

            language_obj = None
            customer_language = ""
            if "customer_language" in data:
                customer_language = data["customer_language"]
                lang_obj = Language.objects.filter(lang=customer_language)
                if lang_obj.exists():
                    language_obj = lang_obj[0]

            username = username.strip()
            if bot_obj.show_livechat_form_or_no and customer_language == 'en' and not validation_obj.validate_name(username) or not len(username):
                response["status_code"] = "400"
                response["status_message"] = "Please enter a valid name"

            if bot_obj.show_livechat_form_or_no and not validation_obj.validate_email(email):
                response["status_code"] = "400"
                response["status_message"] = "Please enter a valid email."

            if bot_obj.show_livechat_form_or_no and (not validation_obj.validate_phone_number_with_country_code(phone) or not is_valid_number):
                response["status_code"] = "400"
                response["status_message"] = "Please enter a valid phone number."
            
            if response["status_code"] == "400":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(
                    json.dumps(response))
                return Response(data=response)

            if "client_id" in data:
                client_id = data["client_id"]

            if "channel" in data:
                channel = data["channel"]

            is_first_query = False
            if "is_first_query" in data:
                is_first_query = data["is_first_query"]

            session_id = str(uuid.uuid4())

            if not bot_obj.show_livechat_form_or_no:
                username = session_id[:7]
                client_id = username
                email = "Not provided"
                phone_number = None
                country_code = None

            set_livechat_session_in_profile(
                session_id, channel, phone, bot_obj, Profile)
            category_obj = get_livechat_category_object(
                livechat_category, bot_obj, LiveChatCategory)

            ip_address = get_ip_address(request)

            source_of_incoming_request = ''
            source = customer_details[0].get('value')
            if source == "Desktop":
                source_of_incoming_request = '1'
            elif source == "Mobile":    
                source_of_incoming_request = '2'
            else:
                source_of_incoming_request = '3'

            channel_obj = Channel.objects.filter(name=channel).first()
            if is_first_query:
                save_livechat_analytics_details(bot_obj, channel_obj)

            livechat_cust_obj = LiveChatCustomer.objects.create(session_id=session_id,
                                                                username=username.strip(),
                                                                phone=phone_number,
                                                                phone_country_code=country_code,
                                                                email=email,
                                                                is_online=True,
                                                                easychat_user_id=easychat_user_id,
                                                                message=message,
                                                                channel=channel_obj,
                                                                category=category_obj,
                                                                active_url=active_url,
                                                                bot=bot_obj,
                                                                client_id=client_id,
                                                                customer_details=json.dumps(customer_details),
                                                                source_of_incoming_request=source_of_incoming_request,
                                                                customer_language=language_obj,
                                                                ip_address=ip_address)
            livechat_cust_obj.closing_category = livechat_cust_obj.category
            livechat_cust_obj.save()
            try:
                agent_unavialable_response = LiveChatConfig.objects.get(
                    bot=bot_obj).agent_unavialable_response
            except Exception:
                agent_unavialable_response = "Our chat representatives are unavailable right now. Please try again in some time."

            try:
                boolian_var, response = check_for_holiday(
                    bot_obj, LiveChatCalender, LiveChatUser)
                if boolian_var:
                    livechat_cust_obj.is_denied = True
                    livechat_cust_obj.is_session_exp = True
                    livechat_cust_obj.system_denied_response = response[
                        "message"]
                    livechat_cust_obj.is_system_denied = True
                    livechat_cust_obj.last_appearance_date = timezone.now()
                    livechat_cust_obj.save()
                    send_event_for_offline_chat(livechat_cust_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)

                    if livechat_cust_obj.customer_language:
                        lang_obj = livechat_cust_obj.customer_language
                        response["message"] = get_translated_text(response["message"], lang_obj.lang, EasyChatTranslationCache)

                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(
                        json.dumps(response))
                    return Response(data=response)

                boolian_var, response = check_for_non_working_hour(
                    bot_obj, LiveChatCalender, LiveChatConfig, LiveChatUser)

                if boolian_var:
                    livechat_cust_obj.is_denied = True
                    livechat_cust_obj.is_session_exp = True
                    livechat_cust_obj.system_denied_response = response[
                        "message"]
                    livechat_cust_obj.is_system_denied = True
                    livechat_cust_obj.last_appearance_date = timezone.now()
                    livechat_cust_obj.save()
                    send_event_for_offline_chat(livechat_cust_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)

                    if livechat_cust_obj.customer_language:
                        lang_obj = livechat_cust_obj.customer_language
                        response["message"] = get_translated_text(response["message"], lang_obj.lang, EasyChatTranslationCache)

                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(
                        json.dumps(response))
                    return Response(data=response)

                if check_is_customer_blocked(livechat_cust_obj, LiveChatReportedCustomer):
                    response["status_code"] = "300"
                    response["message"] = "Our chat representatives are unavailable right now. Please try again in some time."
                    response["assigned_agent"] = "customer_blocked"
                    response["assigned_agent_username"] = "None"

                    livechat_cust_obj.is_denied = True
                    livechat_cust_obj.is_session_exp = True
                    livechat_cust_obj.system_denied_response = response["message"]
                    livechat_cust_obj.is_system_denied = True
                    livechat_cust_obj.last_appearance_date = timezone.now()
                    livechat_cust_obj.save()
                    send_event_for_offline_chat(livechat_cust_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)

                    if livechat_cust_obj.customer_language:
                        lang_obj = livechat_cust_obj.customer_language
                        response["message"] = get_translated_text(response["message"], lang_obj.lang, EasyChatTranslationCache)

                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(
                        json.dumps(response))
                    return Response(data=response)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("CreateCustomerRoomAPI Holiday check: %s at %s", e, str(
                    exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
                response["status_code"] = "300"
                response["assigned_agent"] = "no_agent_online"
                response["assigned_agent_username"] = "None"
                response["status_message"] = e
                livechat_cust_obj.is_denied = True
                livechat_cust_obj.is_session_exp = True
                livechat_cust_obj.system_denied_response = "Our chat representatives are unavailable right now. Please try again in some time."
                livechat_cust_obj.last_appearance_date = timezone.now()
                livechat_cust_obj.save()

            response["livechat_notification"] = agent_unavialable_response

            if livechat_cust_obj.customer_language:
                lang_obj = livechat_cust_obj.customer_language
                response["livechat_notification"] = get_translated_text(response["livechat_notification"], lang_obj.lang, EasyChatTranslationCache)
        
            response["status_code"] = "200"
            response["session_id"] = session_id

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateCustomerRoom: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CreateCustomerRoom = CreateCustomerRoomAPI.as_view()


class SaveCustomerChatAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)
    
            validation_obj = LiveChatInputValidation()

            session_id = data["session_id"]
            message = data["message"]
            sender = data["sender"]
            attached_file_src = data["attached_file_src"]
            thumbnail_file_path = data["thumbnail_file_path"]
            preview_attachment_file_path = ""
            if "preview_file_src" in data:
                preview_attachment_file_path = data["preview_file_src"]

            session_id = validation_obj.remo_html_from_string(session_id)
            sender = validation_obj.remo_html_from_string(sender)
            attached_file_src = validation_obj.remo_html_from_string(
                attached_file_src)

            customer_obj = LiveChatCustomer.objects.filter(session_id=session_id).first()
            agent_obj = customer_obj.agent_id

            if (message != None and message != "") or attached_file_src != "":
                admin_config = get_admin_config(
                    agent_obj, LiveChatAdminConfig, LiveChatUser)
                is_special_charater_allow = admin_config.is_special_character_allowed_in_chat
                message = validation_obj.remo_html_from_string(message)
                if (not validation_obj.is_valid_url(message) and not is_special_charater_allow):
                    message = validation_obj.remove_special_charater_from_string(message)
                    if message == "" and attached_file_src == "":
                        response["status_code"] = "300"
            else:
                response["status_code"] = "300"
            
            if response["status_code"] == "300":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            attachment_file_name = ""
            if attached_file_src != "":
                attachment_file_name = attached_file_src.split("/")[-1]
            logger.info("inside SaveCustomerChatAPI:",
                        extra={'AppName': 'LiveChat'})

            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)

            # Creating chat objects of bot and customer messages if customer starts messaging before
            # agent opens the chat.
            update_message_history_till_now(
                customer_obj, LiveChatMISDashboard, MISDashboard)

            sender_name = customer_obj.get_username() if sender == "Customer" else "System"

            is_voice_call_message = False
            message_for = 'customer'
            if 'voice_call_notification' in data:
                is_voice_call_message = data['voice_call_notification']

            is_video_call_message = False
            if 'video_call_notification' in data:
                is_video_call_message = data['video_call_notification']

            is_cobrowsing_message = False
            if 'cobrowsing_notification' in data:
                is_cobrowsing_message = data['cobrowsing_notification']
                
            is_transcript_message = False
            if 'transcript_notification' in data:
                is_transcript_message = data['transcript_notification']
                
            is_file_not_support_message = False
            if 'file_not_support_notification' in data:
                is_file_not_support_message = data['file_not_support_notification']

            livechat_mis_obj = LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                                                   sender=sender,
                                                                   text_message=message,
                                                                   sender_name=sender_name,
                                                                   message_time=timezone.now(),
                                                                   attachment_file_name=attachment_file_name,
                                                                   attachment_file_path=attached_file_src,
                                                                   thumbnail_file_path=thumbnail_file_path,
                                                                   preview_attachment_file_path=preview_attachment_file_path,
                                                                   is_voice_call_message=is_voice_call_message,
                                                                   is_video_call_message=is_video_call_message,
                                                                   is_cobrowsing_message=is_cobrowsing_message,
                                                                   is_transcript_message=is_transcript_message,
                                                                   is_file_not_support_message=is_file_not_support_message,
                                                                   message_for=message_for)
            customer_obj.last_appearance_date = timezone.now()
            customer_obj.unread_message_count += 1
            customer_obj.save()

            if "chat_ended_by" in data and data["chat_ended_by"] != "":
                customer_obj.chat_ended_by = data["chat_ended_by"]
                customer_obj.save()

            response["status_code"] = "200"
            response["message_id"] = str(livechat_mis_obj.message_id)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveCustomerChatAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveCustomerChat = SaveCustomerChatAPI.as_view()


class SaveSupervisorChatAPI(APIView):

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

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            session_id = data["session_id"]
            message = data["message"]
            sender = data["sender"]
            attached_file_src = data["attached_file_src"]
            thumbnail_file_src = data["thumbnail_url"]
            reply_message_id = data["reply_message_id"]
            sender_username = data["sender_username"]
            is_uploaded_file = False

            if 'is_uploaded_file' in data:
                is_uploaded_file = data["is_uploaded_file"]

            sender_name = str(user_obj.user.first_name) + \
                " " + str(user_obj.user.last_name)
            if sender_name.strip() == "":
                sender_name = str(user_obj.user.username)

            session_id = validation_obj.remo_html_from_string(session_id)
            message = validation_obj.remo_html_from_string(message)

            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)
            agent_obj = customer_obj.agent_id

            admin_config = get_admin_config(agent_obj, LiveChatAdminConfig, LiveChatUser)

            if (message and message != ""):
                if (not validation_obj.is_valid_url(message) and not admin_config.is_special_character_allowed_in_chat):
                    message = validation_obj.remove_special_charater_from_string(
                        message)

            attached_file_src = validation_obj.remo_html_from_string(
                attached_file_src)
            
            if message == "" and attached_file_src == "":
                response["status_code"] = "300"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            attachment_file_name = ""
            if attached_file_src != "":
                attachment_file_name = attached_file_src.split("/")[-1]
                if admin_config.is_special_character_allowed_in_file_name:
                    attachment_file_name = validation_obj.replace_special_character_in_file_name(attachment_file_name)
                elif(not is_uploaded_file and validation_obj.is_special_character_present_in_file_name(attachment_file_name)):
                    response['status'] = 300
                    response['status_message'] = 'Special characters are not allowed in file name'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            logger.info("inside SaveSupervisorChatAPI:",
                        extra={'AppName': 'LiveChat'})
            livechat_mis_obj = LiveChatMISDashboard.objects.create(livechat_customer=customer_obj,
                                                                   sender=sender,
                                                                   text_message=message,
                                                                   sender_name=sender_name,
                                                                   message_time=timezone.now(),
                                                                   attachment_file_name=attachment_file_name,
                                                                   attachment_file_path=attached_file_src,
                                                                   thumbnail_file_path=thumbnail_file_src,
                                                                   reply_message_id=reply_message_id,
                                                                   sender_username=sender_username)

            response["status_code"] = "200"
            response["message_id"] = str(livechat_mis_obj.message_id)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveSupervisorChatAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveSupervisorChat = SaveSupervisorChatAPI.as_view()


class GetLiveChatMessageDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            message_id = data["message_id"]
            message_obj = LiveChatMISDashboard.objects.get(
                message_id=message_id)

            response["text_message"] = message_obj.text_message
            response["attachment_file_name"] = message_obj.attachment_file_name
            response["attachment_file_path"] = message_obj.attachment_file_path
            response["thumbnail_file_path"] = message_obj.thumbnail_file_path
            response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatMessageDetailsAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatMessageDetails = GetLiveChatMessageDetailsAPI.as_view()


class CheckReplyMessageSenderAPI(APIView):

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
            sender_username = data["sender_username"]
            sender_username = validation_obj.remo_html_from_string(
                sender_username)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            supervisor_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(sender_username)), is_deleted=False)

            if user_obj in supervisor_obj.agents.all():
                response["redirect"] = True
                response["supervisor_webtoken"] = get_agent_token_based_on_username(
                    sender_username)
                response["supervisor_username"] = sender_username
                response["supervisor_name"] = supervisor_obj.user.first_name + \
                    ' ' + supervisor_obj.user.last_name
            else:
                response["redirect"] = False

            response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CheckReplyMessageSenderAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CheckReplyMessageSender = CheckReplyMessageSenderAPI.as_view()


class UpdateUnreadMessageCountAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            session_ids = data['session_ids']
            counts = data['counts']

            customer_objs = LiveChatCustomer.objects.filter(
                session_id__in=session_ids)

            itr = 0
            for customer_obj in customer_objs:
                customer_obj.unread_message_count = int(counts[itr])
                customer_obj.save()

                itr += 1

            response["status"] = 200
            response["status_message"] = "Success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateUnreadMessageCountAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateUnreadMessageCount = UpdateUnreadMessageCountAPI.as_view()


def RequestsInQueue(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            is_user_agent = user_obj.status == "3"
            if is_user_agent:
                admin_config = get_admin_config(
                    user_obj, LiveChatAdminConfig, LiveChatUser)
                return render(request, 'LiveChatApp/requests_in_queue.html', {"user_obj": user_obj, "admin_config": admin_config})
            else:
                return HttpResponse("You are not authorised to access this page.")
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("RequestsInQueue: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class GetLiveChatQueueRequestsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            is_user_agent = user_obj.status == "3"

            if is_user_agent:
                user_category = user_obj.category.all()
                bot_objs = user_obj.bots.all()

                livechat_cust_objs = LiveChatCustomer.objects.filter(
                    agent_id=None, is_session_exp=False, category__in=user_category, bot__in=bot_objs, is_ameyo_fusion_session=False).order_by('joined_date')

                page = data['page']
                total_requests, livechat_cust_objs, start_point, end_point = paginate(
                    livechat_cust_objs, QUEUE_REQUESTS_COUNT, page)

                livechat_requests = parse_livechat_cust_objs(
                    livechat_cust_objs, LiveChatConfig)

                response["status"] = 200
                response["status_message"] = "Success"
                response["queue_requests"] = livechat_requests
                response["pagination_data"] = get_audit_trail_pagination_data(
                    livechat_cust_objs)
                response["total_requests"] = total_requests
                response["start_point"] = start_point
                response["end_point"] = end_point
                response["is_agent_online"] = user_obj.is_online

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetLiveChatQueueRequests: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatQueueRequests = GetLiveChatQueueRequestsAPI.as_view()


class LiveChatSelfAssignRequestAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            livechat_agent = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            session_id = data['session_id']

            is_user_agent = livechat_agent.status == "3"

            if is_user_agent:

                livechat_cust_obj = LiveChatCustomer.objects.get(
                    session_id=session_id)

                if livechat_cust_obj.agent_id == livechat_agent and livechat_cust_obj.is_session_exp == False:

                    response["chat_assigned"] = True
                    response["customer_name"] = livechat_cust_obj.username                   

                elif livechat_cust_obj.agent_id == None and livechat_cust_obj.is_session_exp == False:

                    livechat_cust_obj.agent_id = livechat_agent
                    livechat_cust_obj.agents_group.add(livechat_agent)
                    diff = timezone.now() - livechat_cust_obj.joined_date
                    livechat_cust_obj.queue_time = diff.seconds
                    livechat_cust_obj.is_self_assigned_chat = True
                    livechat_cust_obj.save()

                    create_customer_details_system_message(livechat_cust_obj, LiveChatMISDashboard)

                    livechat_agent.resolved_chats = livechat_agent.resolved_chats + 1
                    livechat_agent.last_chat_assigned_time = timezone.now()
                    livechat_agent.ongoing_chats = livechat_agent.ongoing_chats + 1
                    livechat_agent.save()

                    response["chat_assigned"] = True
                    response["customer_name"] = livechat_cust_obj.username

                    if livechat_cust_obj.is_external:
                        push_livechat_event(AGENT_ASSIGNED_EVENT, livechat_cust_obj, {'agent_name': livechat_cust_obj.agent_id.get_agent_name()})

                    if not livechat_cust_obj.is_external and livechat_cust_obj.channel.name != "Web":

                        # Send chat assigned notification to customer on different channels

                        if str(livechat_agent.user.first_name).strip() == "":
                            agent_fullname = str(
                                livechat_agent.user.username).strip()
                        else:
                            agent_fullname = str(livechat_agent.user.first_name).strip(
                            ) + " " + str(livechat_agent.user.last_name).strip()

                        customer_language = livechat_cust_obj.customer_language
                        
                        livechat_notification = get_livechat_notification(
                            livechat_cust_obj.channel.name, agent_fullname, customer_language, False, EasyChatTranslationCache)

                        send_channel_based_text_message(
                            livechat_notification, livechat_cust_obj, livechat_cust_obj.easychat_user_id)

                    # Check if whatsapp reinitiated conversation
                    livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.filter(livechat_customer=livechat_cust_obj, is_whatsapp_conversation_reinitiated=True, is_completed=False).first()

                    if livechat_cust_obj.channel.name == "WhatsApp" and livechat_followup_cust_obj:
                        livechat_followup_cust_obj.is_completed = True
                        livechat_followup_cust_obj.save()

                else:
                    response["chat_assigned"] = False

                response["status"] = 200
                response["status_message"] = "Success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error LiveChatSelfAssignRequest: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LiveChatSelfAssignRequest = LiveChatSelfAssignRequestAPI.as_view()


class CheckChatRequestsQueueAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            is_user_agent = user_obj.status == "3"

            if is_user_agent:
                user_category = user_obj.category.all()

                livechat_cust_objs_count = LiveChatCustomer.objects.filter(
                    agent_id=None, is_session_exp=False, category__in=user_category, is_ameyo_fusion_session=False).count()

                response["chats_available"] = False
                if livechat_cust_objs_count > 0:
                    response["chats_available"] = True

                response["status"] = 200
                response["status_message"] = "Success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckChatRequestsQueue: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CheckChatRequestsQueue = CheckChatRequestsQueueAPI.as_view()


class SendLiveChatEventAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            event = data['event']
            session_id = data['session_id']

            customer_obj = LiveChatCustomer.objects.get(session_id=session_id)

            if event == 'inactivity':
                push_livechat_event(INACTIVITY_EVENT, customer_obj)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SendLiveChatEventAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SendLiveChatEvent = SendLiveChatEventAPI.as_view()


class UpdateCustomerDetailsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            session_id = data['session_id']
            updated_name = data['updated_name']
            updated_phone = data['updated_phone']
            updated_email = data['updated_email']
            channel = data['channel']

            phone_number = updated_phone
            country_code = ''
            is_valid_number = True
            if channel != 'WhatsApp' and channel != 'GoogleRCS':
                phone_number, country_code, is_valid_number = get_phone_number_and_country_code(updated_phone, channel, True)

            validation_obj = LiveChatInputValidation()
            livechat_cust_obj = LiveChatCustomer.objects.get(session_id=session_id)

            if not validation_obj.validate_name(updated_name):
                response["status"] = "400"
                response["status_message"] = "Please enter a valid name"

            if not validation_obj.validate_email(updated_email):
                response["status"] = "400"
                response["status_message"] = "Please enter a valid email."

            if channel != 'WhatsApp' and channel != 'GoogleRCS' and (not validation_obj.validate_phone_number_with_country_code(updated_phone) or not is_valid_number):
                response["status"] = "400"
                response["status_message"] = "Please enter a valid phone number."

            if (channel == 'WhatsApp' or channel == 'GoogleRCS') and updated_phone != livechat_cust_obj.phone:
                response["status"] = "400"
                response["status_message"] = "For this channel, mobile number can not be changed."
            
            if response["status"] == "400":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(
                    json.dumps(response))
                return Response(data=response)

            if((livechat_cust_obj.original_username == "" and livechat_cust_obj.original_email == "" and livechat_cust_obj.original_phone == "") or (livechat_cust_obj.original_username == None and livechat_cust_obj.original_email == None and livechat_cust_obj.original_phone == None)):
                livechat_cust_obj.original_username = livechat_cust_obj.username
                livechat_cust_obj.original_email = livechat_cust_obj.email
                livechat_cust_obj.original_phone = livechat_cust_obj.phone
            
            if channel in ['Web', 'Android', 'iOS']:
                livechat_cust_obj.client_id = updated_phone
                
            livechat_cust_obj.username = updated_name
            livechat_cust_obj.phone = phone_number
            livechat_cust_obj.email = updated_email
            if channel != 'WhatsApp' and channel != 'GoogleRCS':
                livechat_cust_obj.phone_country_code = country_code
            livechat_cust_obj.save()
            if livechat_cust_obj.username != livechat_cust_obj.original_username:
                text_message = "Customer Name: " + str(livechat_cust_obj.username) + " (Original: " + str(livechat_cust_obj.original_username) + ") | Agent Name: " + str(livechat_cust_obj.agent_id.user.first_name) + " " + str(
                    livechat_cust_obj.agent_id.user.last_name) + "(" + str(livechat_cust_obj.agent_id.user.username) + ")"
            else:
                text_message = "Customer Name: " + str(livechat_cust_obj.username) + " | Agent Name: " + str(livechat_cust_obj.agent_id.user.first_name) + " " + str(
                    livechat_cust_obj.agent_id.user.last_name) + "(" + str(livechat_cust_obj.agent_id.user.username) + ")"
            LiveChatMISDashboard.objects.create(livechat_customer=livechat_cust_obj,
                                                sender="System",
                                                text_message=text_message,
                                                sender_name="system",
                                                message_time=timezone.now(),
                                                attachment_file_name="",
                                                attachment_file_path="")
            response["original_name"] = livechat_cust_obj.original_username
            response["phone_country_code"] = livechat_cust_obj.phone_country_code
            response["status"] = 200
            response["status_message"] = "Success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateCustomerDetails: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateCustomerDetails = UpdateCustomerDetailsAPI.as_view()


class CheckNewChatForAgentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            is_user_agent = user_obj.status == "3"

            if is_user_agent:
                customer_objs = LiveChatCustomer.objects.filter(
                    is_session_exp=False, agent_id=user_obj)
                total_assigned_customer = customer_objs.count()

                if 'current_assigned_customer_count' in data:
                    if data["current_assigned_customer_count"] == -1:
                        assigned_customer_count = total_assigned_customer
                    else:
                        assigned_customer_count = data["current_assigned_customer_count"]    
                else:
                    assigned_customer_count = 0

                response["new_assigned_customer_count"] = max(
                    0, total_assigned_customer - int(assigned_customer_count))  
                response["total_assigned_customer"] = total_assigned_customer  
                response["agent_name"] = user_obj.get_agent_name()
                response["status"] = 200
                response["status_message"] = "Success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckNewChatForAgent: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CheckNewChatForAgent = CheckNewChatForAgentAPI.as_view()


@csrf_exempt
def service_worker_livechat(request):
    try:
        filename = '/LiveChatApp/src/js/agent/service-worker-livechat.js'
        jsfile = open(settings.BASE_DIR + filename, 'rb')
        response = HttpResponse(content=jsfile)
        response['Content-Type'] = 'text/javascript'
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error service_worker %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChatApp'})

        return Response(status=401)


class GetWhatsAppWebhookStatusAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = INTERNAL_SERVER_ERROR
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            need_to_set = False
            session_id = data['session_id']
            user_obj = LiveChatCustomer.objects.filter(session_id=str(session_id)).first()
            livechat_webhook_obj = LiveChatBotChannelWebhook.objects.filter(bot=user_obj.bot).first()
            if livechat_webhook_obj:
                code = livechat_webhook_obj.function
                if not code:
                    need_to_set = True
            else:
                need_to_set = True

            response["status"] = 200
            if need_to_set:
                response["status_message"] = "Webhook are not set"
            else:
                response["status_message"] = "Webhook are set"

            response["need_to_set"] = need_to_set
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetWhatsAppWebhookStatus: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)
    

GetWhatsAppWebhookStatus = GetWhatsAppWebhookStatusAPI.as_view()
