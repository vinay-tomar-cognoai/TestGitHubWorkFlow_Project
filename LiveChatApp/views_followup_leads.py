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
from LiveChatApp.utils_email import get_email_config_obj
from LiveChatApp.utils_translation import get_translated_text
from EasyChatApp.models import MISDashboard
from LiveChatApp.livechat_channels_webhook import send_channel_based_text_message

import datetime

# Logger
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def FollowupLeads(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)
            is_user_agent = user_obj.status == "3"

            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            agent_obj_list = get_agents_under_this_user(user_obj)

            category_list = user_obj.category.all()

            start_date = (datetime.datetime.today() - datetime.timedelta(7)).date()
            end_date = datetime.datetime.today().date()

            followup_lead_sources = []
            if is_user_agent:
                bot_obj = user_obj.bots.filter(is_deleted=False)[0]
                livechat_config = LiveChatConfig.objects.get(bot=bot_obj)
                followup_lead_sources = json.loads(livechat_config.followup_lead_sources)

            else:
                bot_obj_list = user_obj.bots.filter(is_deleted=False)
                for bot in bot_obj_list:
                    livechat_config = LiveChatConfig.objects.get(bot=bot)
                    followup_lead_sources_objs = json.loads(livechat_config.followup_lead_sources)

                    if len(followup_lead_sources) == 3:
                        break
                    elif followup_lead_sources_objs.count == 3:
                        followup_lead_sources = followup_lead_sources_objs
                        break

                    for followup_lead_source in followup_lead_sources_objs:
                        if followup_lead_source not in followup_lead_sources:
                            followup_lead_sources.append(followup_lead_source)

            # get category list for raise ticket form
            raise_ticket_category = {}
            category_objs = user_obj.category.filter(is_deleted=False).values('bot', 'title').exclude(bot__isnull=True)

            for item in category_objs:

                bot = str(item['bot'])
                bot_category = []

                if bot in raise_ticket_category:
                    bot_category = raise_ticket_category[bot]

                bot_category.append(item['title'])
                raise_ticket_category[bot] = bot_category

            return render(request, 'LiveChatApp/followup_leads.html', {
                "user_obj": user_obj, 
                "admin_config": admin_config,
                "agent_list": agent_obj_list,
                "followup_lead_sources": followup_lead_sources,
                "category_list": category_list,
                "start_date": start_date,
                "end_date": end_date,
                "is_user_agent": is_user_agent,
                "raise_ticket_category": raise_ticket_category,
            })
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("FollowupLeads: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class GetLiveChatFollowupLeadsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get_data(self, key):
        try:
            if key in self.data:
                return self.data[key]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLiveChatFollowupLeadsAPI get_data: %s at %s",
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

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            is_user_agent = user_obj.status == "3"

            agent_usernames = self.get_data('agent_usernames')
            if agent_usernames == 'None' or (isinstance(agent_usernames, list) and not agent_usernames):
                if is_user_agent:
                    agent_obj_list = [user_obj]
                else:
                    agent_obj_list = get_agents_under_this_user(user_obj)
            else:
                agent_obj_list = LiveChatUser.objects.filter(user__username__in=agent_usernames)

            lead_source = self.get_data('lead_source')
            if lead_source == 'None' or (isinstance(lead_source, list) and not lead_source):
                lead_source = ['offline_chats', 'missed_chats', 'abandoned_chats']

            lead_category = self.get_data('lead_category')
            if lead_category == 'None' or (isinstance(lead_category, list) and not lead_category):
                category_objs = user_obj.category.all()
            else:
                category_objs = user_obj.category.filter(pk__in=lead_category)

            # By default, chat history of last 7 days is loaded
            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()
            datetime_end = datetime.datetime.today().date()
            try:
                start_date = self.get_data('start_date')
                end_date = self.get_data('end_date')

                if start_date != 'None':
                    datetime_start = datetime.datetime.strptime(
                        start_date.strip(), DEFAULT_DATE_FORMAT).date()
                
                if end_date != 'None':
                    datetime_end = datetime.datetime.strptime(end_date.strip(), DEFAULT_DATE_FORMAT).date()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
 
            bot_objs = user_obj.bots.all()

            livechat_cust_objs = LiveChatFollowupCustomer.objects.filter(
                agent_id__in=agent_obj_list, source__in=lead_source, is_completed=False, 
                livechat_customer__joined_date__date__range=[datetime_start, datetime_end], 
                livechat_customer__bot__in=bot_objs, livechat_customer__category__in=category_objs).order_by('-livechat_customer__joined_date')

            page = data['page']
            total_leads, livechat_cust_objs, start_point, end_point = paginate(
                livechat_cust_objs, FOLLOWUP_LEADS_COUNT, page)

            livechat_followup_leads = parse_and_get_followup_leads(livechat_cust_objs)

            response["status"] = 200
            response["status_message"] = "Success"
            response["followup_leads"] = livechat_followup_leads
            response["pagination_data"] = get_audit_trail_pagination_data(
                livechat_cust_objs)
            response["total_leads"] = total_leads
            response["start_point"] = start_point
            response["end_point"] = end_point
            response["is_user_agent"] = is_user_agent

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetLiveChatFollowupLeads: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatFollowupLeads = GetLiveChatFollowupLeadsAPI.as_view()


class GetLiveChatFollowupLeadMessagesAPI(APIView):

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

            session_id = data["session_id"]

            livechat_cust_obj = LiveChatCustomer.objects.filter(
                session_id=session_id)

            if livechat_cust_obj:
                livechat_cust_obj = livechat_cust_obj[0]

                livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.filter(livechat_customer=livechat_cust_obj).first()

                # Creating chat objects of bot and customer messages.
                update_followup_lead_message_history(
                    livechat_cust_obj, livechat_followup_cust_obj, LiveChatMISDashboard, MISDashboard)

                livechat_config_obj = LiveChatConfig.objects.get(bot=livechat_cust_obj.bot)

                # Get raise ticket form
                raise_ticket_form_obj = LiveChatRaiseTicketForm.objects.filter(
                    bot=livechat_cust_obj.bot)

                raise_ticket_form = json.dumps({})
                if raise_ticket_form_obj:
                    raise_ticket_form = raise_ticket_form_obj[0].form

                # Checking if agent can chat over mail
                is_livechat_email_enabled = False
                admin_config = get_admin_config(livechat_followup_cust_obj.agent_id, LiveChatAdminConfig, LiveChatUser)
                email_config_obj = get_email_config_obj(admin_config, LiveChatEmailConfig)
                if is_user_agent and email_config_obj.is_livechat_enabled_for_email and email_config_obj.is_successful_authentication_complete and email_config_obj.is_followup_leads_over_mail_enabled:
                    is_livechat_email_enabled = True

                # Checking if Reinitiation Conversation button should be enabled
                is_whatsapp_reinitiation_enabled = False
                if livechat_config_obj.is_whatsapp_reinitiation_enabled and livechat_cust_obj.channel.name == "WhatsApp" and (user_obj.status == "1" or user_obj.status == "3"):
                    is_whatsapp_reinitiation_enabled = True

                response["message_history"] = get_message_history(
                    livechat_cust_obj, False, LiveChatMISDashboard, LiveChatTranslationCache)
                response["active_url"] = livechat_cust_obj.active_url
                response["is_agent_raise_ticket_functionality_enabled"] = livechat_config_obj.is_agent_raise_ticket_functionality_enabled
                response["customer_name"] = livechat_cust_obj.username
                response["customer_email"] = livechat_cust_obj.email
                response["customer_phone"] = livechat_cust_obj.phone
                response["raise_ticket_form"] = raise_ticket_form
                response["is_livechat_email_enabled"] = is_livechat_email_enabled
                response["is_whatsapp_reinitiation_enabled"] = is_whatsapp_reinitiation_enabled
                response["is_whatsapp_conversation_reinitiated"] = livechat_followup_cust_obj.is_whatsapp_conversation_reinitiated
                response["status"] = 200
                response["message"] = "success"
            else:
                response['message'] = 'Invalid Session ID'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetLiveChatFollowupLeadMessagesAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatFollowupLeadMessages = GetLiveChatFollowupLeadMessagesAPI.as_view()


class GetLiveChatFollowupLeadAgentsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['status_message'] = INTERNAL_SERVER_ERROR
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            session_ids = data["checked_leads"]

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            is_user_agent = user_obj.status == "3"

            if not is_user_agent:

                livechat_category_objs = LiveChatCustomer.objects.filter(session_id__in=session_ids).values('category').distinct()

                agents_under_this_user = get_agents_under_this_user(user_obj, False)
                agent_list = list(LiveChatUser.objects.filter(user__in=agents_under_this_user, category__in=livechat_category_objs, is_deleted=False).annotate(num_attr=Count('category')).filter(num_attr=livechat_category_objs.count()).values_list("user__username", flat=True))

                response['agent_list'] = agent_list
                response['status'] = 200
                response['status_message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetLiveChatFollowupLeadAgentsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatFollowupLeadAgents = GetLiveChatFollowupLeadAgentsAPI.as_view()


class TransferLiveChatFollowupLeadAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['status_message'] = INTERNAL_SERVER_ERROR
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            session_ids = data["checked_leads"]
            selected_agent = data["selected_agent"]

            validation_obj = LiveChatInputValidation()
            selected_agent = validation_obj.remo_html_from_string(selected_agent)

            try:

                transfer_agent = LiveChatUser.objects.get(
                    user=User.objects.get(username=str(selected_agent)), is_deleted=False)

            except Exception: 

                response['status'] = 400
                response['status_message'] = 'Agent does not exists'

                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            is_user_agent = user_obj.status == "3"

            if not is_user_agent:

                livechat_cust_objs = LiveChatFollowupCustomer.objects.filter(livechat_customer__session_id__in=session_ids)

                for livechat_cust_obj in livechat_cust_objs:
                    livechat_cust_obj.agent_id = transfer_agent
                    livechat_cust_obj.save()

                response['status'] = 200
                response['status_message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error TransferLiveChatFollowupLeadAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


TransferLiveChatFollowupLead = TransferLiveChatFollowupLeadAPI.as_view()


class CompleteLiveChatFollowupLeadAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['status_message'] = INTERNAL_SERVER_ERROR
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            session_ids = data["checked_leads"]

            livechat_cust_objs = LiveChatFollowupCustomer.objects.filter(livechat_customer__session_id__in=session_ids)

            for livechat_cust_obj in livechat_cust_objs:
                livechat_cust_obj.is_completed = True
                livechat_cust_obj.completed_date = timezone.now()
                livechat_cust_obj.save()
                livechat_cust_obj.livechat_customer.chat_ended_by = "Agent"
                livechat_cust_obj.livechat_customer.save()

            response['status'] = 200
            response['status_message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CompleteLiveChatFollowupLeadAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CompleteLiveChatFollowupLead = CompleteLiveChatFollowupLeadAPI.as_view()


class ReinitiateWhatsAppConversationAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['status_message'] = INTERNAL_SERVER_ERROR
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            session_id = data["session_id"]

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            livechat_customer_obj = LiveChatFollowupCustomer.objects.filter(livechat_customer__session_id=session_id).first()

            if livechat_customer_obj:

                if livechat_customer_obj.livechat_customer.channel.name != "WhatsApp":
                    response['status'] = 400
                    response['status_message'] = 'Conversation can be reinitiated only for WhatsApp Leads'

                if livechat_customer_obj.is_whatsapp_conversation_reinitiated:
                    response['status'] = 400
                    response['status_message'] = 'Conversation has been already reinitiated'

                livechat_active_customer = LiveChatCustomer.objects.filter(client_id=livechat_customer_obj.livechat_customer.client_id, is_session_exp=False, is_ameyo_fusion_session=False)
                if livechat_active_customer.exists():
                    response['status'] = 400
                    response['status_message'] = 'Customer is already in an interaction'

                if user_obj.status == '2':
                    response['status'] = 401
                    response['status_message'] = 'Supervisors cannot reinitiate the conversation.'

                if response['status'] == 400 or response['status'] == 401:
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                livechat_customer_obj.is_whatsapp_conversation_reinitiated = True
                livechat_customer_obj.save()

                livechat_config_obj = LiveChatConfig.objects.get(bot=livechat_customer_obj.livechat_customer.bot)
                whatsapp_reinitiating_text = livechat_config_obj.whatsapp_reinitiating_text
                validation_obj = LiveChatInputValidation()
                whatsapp_reinitiating_text = validation_obj.original_from_sanitize_html(whatsapp_reinitiating_text)
                
                customer_language = livechat_customer_obj.livechat_customer.customer_language
                if customer_language and customer_language.lang != 'en':
                    whatsapp_reinitiating_text = get_translated_text(whatsapp_reinitiating_text, customer_language.lang, EasyChatTranslationCache)

                send_channel_based_text_message(whatsapp_reinitiating_text, livechat_customer_obj.livechat_customer, livechat_customer_obj.livechat_customer.easychat_user_id, True)
            else:
                response['status_message'] = "Invalid session ID"

            response['status'] = 200
            response['status_message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ReinitiateWhatsAppConversationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ReinitiateWhatsAppConversation = ReinitiateWhatsAppConversationAPI.as_view()
