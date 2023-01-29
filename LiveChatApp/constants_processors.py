LIVECHAT_PROCESSOR_EXAMPLE_ASSIGN_AGENT = """
import sys
import time
import json
import logging
import requests
import mimetypes
import datetime
import http.client
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count
from EasyChatApp.models import Bot, Profile, User, MISDashboard, EasyChatTranslationCache
from EasyChatApp.utils_bot import get_translated_text
from LiveChatApp.utils import send_event_for_abandoned_chat, update_message_history_till_now, get_livechat_notification, send_event_for_missed_chat, create_customer_details_system_message
from LiveChatApp.utils_agent import push_livechat_event
from LiveChatApp.livechat_channels_webhook import send_channel_based_text_message, send_channel_based_welcome_message
from LiveChatApp.constants import AGENT_ASSIGNED_EVENT, APPLICATION_JSON, REPRESENTATIVE_SYSTEM_MESSAGE

from LiveChatApp.models import LiveChatAdminConfig, LiveChatCustomer, LiveChatConfig, LiveChatUser, LiveChatMISDashboard, LiveChatProcessors, LiveChatFollowupCustomer


from LiveChatApp.utils import logger

log_param = {'AppName': 'EasyChat', 'user_id': 'None',
             'source': 'None', 'channel': 'WhatsApp', 'bot_id': 'None'}

#   GET ROUTE MOBILE API KEY:

# MAIN FUNCTION assign_agent_via_scheduler
def f(livechat_cust_obj):
    try:
        import pytz
        import os
        tz = pytz.timezone(settings.TIME_ZONE)

        logger.info("---------- Agent Assigning Task  ---------",
                    extra={'AppName': 'LiveChat'})

        try:

            livechat_channel_list = ["WhatsApp",
                                     "GoogleBusinessMessages", "Facebook", "Instagram", "Twitter", "GoogleRCS", "Viber", "Telegram"]
            if livechat_cust_obj.channel.name in livechat_channel_list:
                last_updated_time = livechat_cust_obj.joined_date.astimezone(
                    tz)
                current_time = timezone.now().astimezone(tz)
                available_time = (
                    current_time - last_updated_time).total_seconds()

                if available_time >= LiveChatConfig.objects.filter(bot=livechat_cust_obj.bot)[0].queue_timer:

                    livechat_cust_obj.is_session_exp = True
                    livechat_cust_obj.is_denied = True
                    livechat_cust_obj.save()
                    send_event_for_missed_chat(livechat_cust_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)
                    user_obj = Profile.objects.get(
                        user_id=livechat_cust_obj.easychat_user_id, bot=livechat_cust_obj.bot)

                    customer_language = livechat_cust_obj.customer_language
                    repr_system_msg = REPRESENTATIVE_SYSTEM_MESSAGE
                    if customer_language and customer_language.lang != 'en':
                        repr_system_msg = get_translated_text(
                            repr_system_msg, customer_language.lang, EasyChatTranslationCache)

                    send_channel_based_text_message(
                        repr_system_msg, livechat_cust_obj, livechat_cust_obj.easychat_user_id)
                    send_channel_based_welcome_message(
                        user_obj, livechat_cust_obj)

                    user_obj.livechat_connected = False
                    user_obj.save()
                    return
            else:
                last_updated_time = livechat_cust_obj.joined_date.astimezone(
                    tz)
                current_time = timezone.now().astimezone(tz)
                available_time = (
                    current_time - last_updated_time).total_seconds()
                if available_time >= LiveChatConfig.objects.filter(bot=livechat_cust_obj.bot)[0].queue_timer:
                    if not livechat_cust_obj.abruptly_closed:
                        send_event_for_abandoned_chat(
                            livechat_cust_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)
                    livechat_cust_obj.is_session_exp = True
                    livechat_cust_obj.abruptly_closed = True
                    livechat_cust_obj.save()
                    return
            if livechat_cust_obj.agent_id != None or livechat_cust_obj.is_session_exp == True or livechat_cust_obj.is_denied == True:
                return
            agent_list = {}
            logger.info(livechat_cust_obj.category,
                        extra={'AppName': 'LiveChat'})
            logger.info(livechat_cust_obj.bot, extra={
                        'AppName': 'LiveChat'})
            livechat_agents = list(LiveChatUser.objects.filter(status="3", is_online=True, category__in=[livechat_cust_obj.category], bots__in=[
                livechat_cust_obj.bot]).order_by('last_chat_assigned_time').values_list('user__username', flat=True))
            logger.info(livechat_agents, extra={'AppName': 'LiveChat'})
            for agent in livechat_agents:
                agent_list[agent] = 0

            current_agent_list = LiveChatCustomer.objects.filter(is_session_exp=False, request_raised_date=datetime.datetime.now(
            ).date()).filter(~Q(agent_id=None)).values('agent_id__user__username').annotate(total=Count('agent_id')).order_by("total")

            logger.info(current_agent_list, extra={'AppName': 'LiveChat'})
            for agent in current_agent_list:
                if agent["agent_id__user__username"] in livechat_agents:
                    agent_list[agent["agent_id__user__username"]
                               ] = agent["total"]
            if len(livechat_agents) == 0:
                logger.info("No active agents", extra={
                            'AppName': 'LiveChat'})
                check_and_complete_whatsapp_reinitiated_conversation(
                    livechat_cust_obj)
                return

            livechat_config_obj = LiveChatConfig.objects.filter(
                bot=livechat_cust_obj.bot)[0]

            # If it is whatsapp reinitiated conversation then try to assign the same followup lead assigned agent
            if check_and_assign_whatsapp_reinitiated_conversation(livechat_cust_obj, agent_list, livechat_config_obj):
                return

            logger.info(livechat_agents, extra={'AppName': 'LiveChat'})
            for agent in livechat_agents:
                livechat_agent = LiveChatUser.objects.get(
                    user=User.objects.get(username=agent))
                logger.info("Agent process started %s and last assigned customer was at %s", str(
                    livechat_agent.user.username), str(livechat_agent.last_chat_assigned_time), extra={'AppName': 'LiveChat'})
                max_customer_count = livechat_agent.max_customers_allowed

                if max_customer_count == -1:
                    max_customer_count = livechat_config_obj.max_customer_count

                logger.info("Agent max cutomer count %s", str(
                    agent_list[agent]), extra={'AppName': 'LiveChat'})
                if max_customer_count > agent_list[agent]:
                    ongoing_chats = agent_list[agent] + 1
                    livechat_agent.resolved_chats = livechat_agent.resolved_chats + 1
                    livechat_agent.last_chat_assigned_time = timezone.now()
                    livechat_agent.ongoing_chats = ongoing_chats
                    livechat_agent.save()
                    livechat_cust_obj.agent_id = livechat_agent
                    livechat_cust_obj.agents_group.add(livechat_agent)

                    diff = timezone.now() - livechat_cust_obj.joined_date
                    livechat_cust_obj.queue_time = diff.seconds
                    livechat_cust_obj.save()

                    create_customer_details_system_message(
                        livechat_cust_obj, LiveChatMISDashboard)

                    logger.info("Agent assigned cutomer count %s till now", str(
                        agent_list[agent] + 1), extra={'AppName': 'LiveChat'})
                    logger.info("Agent asignment success %s to %s", str(livechat_cust_obj.session_id),
                                str(livechat_agent.user.username), extra={'AppName': 'LiveChat'})

                    if livechat_cust_obj.is_external:
                        push_livechat_event(AGENT_ASSIGNED_EVENT, livechat_cust_obj, {
                                            'agent_name': livechat_cust_obj.agent_id.get_agent_name()})
                        break

                    if livechat_cust_obj.channel.name != "Web":
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

                    break

            check_and_complete_whatsapp_reinitiated_conversation(
                livechat_cust_obj)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("error while assigning customer: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("assign_agent_via_scheduler: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def check_and_assign_whatsapp_reinitiated_conversation(livechat_cust_obj, agent_list, livechat_config_obj):
    try:
        livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.filter(
            livechat_customer=livechat_cust_obj, is_whatsapp_conversation_reinitiated=True, is_completed=False).first()

        if livechat_cust_obj.channel.name == "WhatsApp" and livechat_followup_cust_obj:

            livechat_agent = livechat_followup_cust_obj.agent_id
            if livechat_agent and livechat_agent.status == '3' and livechat_agent.is_online == True:

                current_customer_count = 0
                if livechat_agent.user.username in agent_list:
                    current_customer_count = agent_list[livechat_agent.user.username]

                max_customer_count = livechat_agent.max_customers_allowed
                if max_customer_count == -1:
                    max_customer_count = livechat_config_obj.max_customer_count

                if max_customer_count > current_customer_count:
                    ongoing_chats = current_customer_count + 1
                    livechat_agent.resolved_chats = livechat_agent.resolved_chats + 1
                    livechat_agent.last_chat_assigned_time = timezone.now()
                    livechat_agent.ongoing_chats = ongoing_chats
                    livechat_agent.save()
                    livechat_cust_obj.agent_id = livechat_agent
                    livechat_cust_obj.agents_group.add(livechat_agent)

                    diff = timezone.now() - livechat_cust_obj.joined_date
                    livechat_cust_obj.queue_time = diff.seconds
                    livechat_cust_obj.save()

                    logger.info("Agent assigned cutomer count %s till now", str(
                        current_customer_count + 1), extra={'AppName': 'LiveChat'})
                    logger.info("Agent asignment success %s to %s", str(livechat_cust_obj.session_id),
                                str(livechat_agent.user.username), extra={'AppName': 'LiveChat'})

                    livechat_followup_cust_obj.is_completed = True
                    livechat_followup_cust_obj.save()

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

                    return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_assign_whatsapp_reinitiated_conversation: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return False


def check_and_complete_whatsapp_reinitiated_conversation(livechat_cust_obj):
    try:
        livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.filter(
            livechat_customer=livechat_cust_obj, is_whatsapp_conversation_reinitiated=True, is_completed=False).first()

        if livechat_cust_obj.channel.name == "WhatsApp" and livechat_followup_cust_obj:

            if livechat_cust_obj.agent_id:
                livechat_followup_cust_obj.is_completed = True
            else:
                livechat_followup_cust_obj.is_whatsapp_conversation_reinitiated = False
                livechat_followup_cust_obj.followup_count = livechat_followup_cust_obj.followup_count + 1

            livechat_followup_cust_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_complete_whatsapp_reinitiated_conversation: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
"""

LIVECHAT_PROCESSOR_EXAMPLE_END_CHAT = """from EasyChatApp.models import Data,Profile
import json
import uuid
import sys
import os
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

def f(x):
    json_data = {}
    json_data['status_code'] = '500'
    json_data['status_message'] = 'Error'
    try:
        json_data['status_message'] = 'Success'
        json_data['status_code']='200'
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('LiveChatProcessor: %s at line %s', str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return json_data"""

LIVECHAT_PROCESSOR_EXAMPLE = """from EasyChatApp.models import Data,Profile
import json
import uuid
import sys
import os
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

def f(x):
    json_data = {}
    json_data['status_code'] = '500'
    json_data['status_message'] = 'Error'
    try:
        json_data['status_message'] = 'Success'
        json_data['user_details'] =  [{'key': 'key1','value': 'value1'},{'key': 'key2','value': 'value2'}]
        json_data['status_code']='200'
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('LiveChatProcessor: %s at line %s', str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return json_data"""

LIVECHAT_PROCESSOR_EXAMPLE_PUSH_API = """from EasyChatApp.models import Data,Profile
import json
import uuid
import sys
import os
import requests
import logging
from datetime import datetime
from LiveChatApp.constants import AGENT_ASSIGNED_EVENT, SEND_MESSAGE_EVENT, END_CHAT_EVENT, TRANSFER_CHAT_EVENT

logger = logging.getLogger(__name__)

def send_event (body):
    try:
        url = "https://b431-65-2-65-107.ngrok.io/livechat/external/event-update/"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        req = requests.request("POST", url, headers=headers,
                data=json.dumps(body), timeout=10, verify=True)
                
        content = json.dumps(req.text)
        logger.info("send_event API Response: %s",
                    str(content), extra={'AppName': 'LiveChat'})
                    
        if str(req.status_code) == "200" or str(req.status_code) == "202":
            logger.info("send_event sent succesfully", extra={'AppName': 'LiveChat'})

        else:
            logger.error("Failed to Send send_event.", extra={'AppName': 'LiveChat'})
            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('send_event: %s at line %s', str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    
def f(x):
    json_data = {}
    json_data['status_code'] = '500'
    json_data['status_message'] = 'Error'
    try:
        logger.error('x: %s', str(x), extra={'AppName': 'LiveChat'})
        
        send_event(x)
        
        json_data['status_message'] = 'Success'
        json_data['status_code'] = 200
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('LiveChatProcessor: %s at line %s', str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return json_data"""

LIVECHAT_PROCESSOR_EXAMPLE_RAISE_TICKET = """import sys
import json
import logging
import requests
import base64
from django.conf import settings
from LiveChatApp.models import LiveChatUser, LiveChatFileAccessManagement
from EasyChatApp.models import User
from EasyTMSApp.models import Agent, TMSAccessToken, CRMIntegrationModel
from LiveChatApp.utils_agent import check_if_uploded_livechat_file_is_valid, save_file_and_get_source_file_path_and_thumbnail_path

logger = logging.getLogger(__name__)


def upload_attachment(filename, base64_content):
    try:
        
        status, status_message = check_if_uploded_livechat_file_is_valid(base64_content, filename)
        
        if status == 500:
            return ""
            
        file_url, thumbnail_url = save_file_and_get_source_file_path_and_thumbnail_path(base64_content, filename, LiveChatFileAccessManagement)
        
        return file_url
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("upload_attachment: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            
        return ""


def f(x):
    try:
        form_filled = x["form_filled"]
        user_obj = x["livechat_agent_obj"]
        customer_obj = x["customer_obj"]

        customer_name = ""
        issue_description = ""
        issue_attachment = ""
        customer_mobile_number = ""
        customer_email_id = ""
        ticket_category = ""

        for form_data in form_filled:

            if form_data and form_data["value"] != "*No Data filled*":
                if form_data["label"] == "Name":
                    customer_name = form_data["value"]

                if form_data["label"] == "Email":
                    customer_email_id  = form_data["value"]

                if form_data["label"] == "Phone No":
                    customer_mobile_number  = form_data["value"]

                if form_data["label"] == "Query":
                    issue_description = form_data["value"]

                if form_data["label"] == "Attachment":
                    issue_attachment = upload_attachment(form_data["filename"], form_data["file_base64_str"])

                if form_data["label"] == "Categories":
                    ticket_category = form_data["value"]

        bot_obj = user_obj.bots.all()
        agent_obj = Agent.objects.filter(role="admin", bots__in=bot_obj)[0]
        access_token = TMSAccessToken.objects.get(agent=agent_obj)
        bot_obj = bot_obj[0]

        crm_integration_model = CRMIntegrationModel.objects.create(access_token=access_token)

        url = settings.EASYCHAT_HOST_URL + "/tms/crm/generate-ticket/"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + crm_integration_model.auth_token,
        }

        body = {
            'customer_name': customer_name,
            'issue_description': issue_description,
            'issue_attachment': issue_attachment,
            'customer_mobile_number': customer_mobile_number,
            'customer_email_id': customer_email_id,
            'ticket_category': ticket_category,
            'bot_id': bot_obj.pk,
            'channel_name': customer_obj.channel.name,
        }
        
        req = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)

        response = json.loads(req.text)

        return response["Body"]["TicketId"]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("raise_ticket_from_data: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "" """

LIVECHAT_PROCESSOR_EXAMPLE_SEARCH_TICKET = """import sys
import json
import logging
import requests
import base64
import datetime
from django.conf import settings
from LiveChatApp.models import LiveChatUser
from EasyChatApp.models import User
from EasyTMSApp.models import Agent, TMSAccessToken, CRMIntegrationModel

logger = logging.getLogger(__name__)


def f(x):
    json_data = {}
    json_data['status_code'] = 500
    json_data['status_message'] = 'Error'
    try:
        ticket_id = x["ticket_id"]
        user_obj = x["livechat_agent_obj"]

        bot_obj = user_obj.bots.all()
        agent_obj = Agent.objects.filter(role="admin", bots__in=bot_obj)[0]
        access_token = TMSAccessToken.objects.get(agent=agent_obj)
        bot_obj = bot_obj[0]

        crm_integration_model = CRMIntegrationModel.objects.create(access_token=access_token)

        url = settings.EASYCHAT_HOST_URL + "/tms/crm/ticket-info/"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + crm_integration_model.auth_token,
        }

        body = {
            'ticket_id': ticket_id,     
        }
        
        req = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)

        response = json.loads(req.text)

        json_data['status_code'] = response['Head']['ResponseCode']
        json_data['status_message'] = response['Head']['Description']

        if response['Head']['ResponseCode'] == 200:
            ticket_info = {}
            ticket_info["Ticket Number"] = response['Body']['Data']['ticket_id']
            ticket_info["Ticket initiated on"] = datetime.datetime.strptime(response['Body']['Data']['issue_date_time'], '%d %b %Y %I:%M:%S %p').strftime('%d-%b-%Y')
            ticket_info["Ticket initiated at"] = datetime.datetime.strptime(response['Body']['Data']['issue_date_time'], '%d %b %Y %I:%M:%S %p').strftime('%I:%M %p')
            ticket_info["Category"] = response['Body']['Data']['ticket_category']
            ticket_info["Status"] = response['Body']['Data']['ticket_status']

            json_data['ticket_info'] = ticket_info

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("search ticket processor error: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return json_data """

LIVECHAT_PROCESSOR_EXAMPLE_PREVIOUS_TICKETS = """import sys
import json
import logging
import requests
import datetime
import pytz
from django.conf import settings
from EasyTMSApp.models import Ticket

logger = logging.getLogger(__name__)


def f(x):
    json_data = {}
    json_data['status_code'] = 500
    json_data['status_message'] = 'Error'
    try:
        customer_phone = x["customer_phone"]
        est = pytz.timezone(settings.TIME_ZONE)

        ticket_objs = Ticket.objects.filter(customer_mobile_number=customer_phone)
        ticket_info_list = []

        for ticket_obj in ticket_objs:
            ticket_info = {}
            ticket_info["Ticket Number"] = str(ticket_obj.ticket_id)
            ticket_info["Ticket initiated on"] = ticket_obj.issue_date_time.astimezone(est).strftime('%d-%b-%Y')
            ticket_info["Ticket initiated at"] = ticket_obj.issue_date_time.astimezone(est).strftime('%I:%M %p')

            if ticket_obj.ticket_category:
                ticket_info["Category"] = ticket_obj.ticket_category.ticket_category
            else:
                ticket_info["Category"] = ""

            if ticket_obj.ticket_status:
                ticket_info["Status"] = ticket_obj.ticket_status.name
            else:
                ticket_info["Status"] = ""

            ticket_info_list.append(ticket_info)

        json_data['status_code'] = 200
        json_data['status_message'] = 'Success'
        json_data['ticket_info_list'] = ticket_info_list

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("search ticket processor error: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return json_data """
