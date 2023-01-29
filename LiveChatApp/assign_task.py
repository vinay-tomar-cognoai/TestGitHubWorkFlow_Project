import sys
import time
import json
import logging
import requests
import threading
import mimetypes
import datetime
import http.client
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count
from EasyChatApp.models import Bot, EasyChatTranslationCache, Profile, User, MISDashboard
from EasyChatApp.utils_bot import get_translated_text
from LiveChatApp.utils import send_event_for_abandoned_chat, update_message_history_till_now, get_livechat_notification, send_event_for_missed_chat, create_customer_details_system_message
from LiveChatApp.utils_agent import push_livechat_event
from LiveChatApp.livechat_channels_webhook import send_channel_based_text_message, send_channel_based_welcome_message
from LiveChatApp.constants import AGENT_ASSIGNED_EVENT, APPLICATION_JSON, REPRESENTATIVE_SYSTEM_MESSAGE

from LiveChatApp.models import LiveChatAdminConfig, LiveChatCustomer, LiveChatConfig, LiveChatUser, LiveChatMISDashboard, LiveChatProcessors, LiveChatFollowupCustomer


logger = logging.getLogger(__name__)

log_param = {'AppName': 'EasyChat', 'user_id': 'None',
             'source': 'None', 'channel': 'WhatsApp', 'bot_id': 'None'}

#   GET ROUTE MOBILE API KEY:


def assign_agent_via_scheduler():
    try:
        import pytz
        import os
        tz = pytz.timezone(settings.TIME_ZONE)

        logger.info("---------- Agent Assigning Task  ---------",
                    extra={'AppName': 'LiveChat'})

        livechat_cust_objs = LiveChatCustomer.objects.filter(last_appearance_date__date=datetime.datetime.now(
        ).date(), is_session_exp=False, agent_id=None, abruptly_closed=False, is_denied=False, is_ameyo_fusion_session=False)
        
        for livechat_cust_obj in livechat_cust_objs:

            try:
                bot_obj = livechat_cust_obj.bot

                if bot_obj.use_assign_agent_processor_livechat:
                    code = LiveChatProcessors.objects.filter(bot=bot_obj)[
                        0].assign_agent_processor.function

                    processor_check_dictionary = {}
                    exec(str(code), processor_check_dictionary)
                    processor_check_dictionary['f'](livechat_cust_obj)
                    continue

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
                            repr_system_msg = get_translated_text(repr_system_msg, customer_language.lang, EasyChatTranslationCache)
                        
                        send_channel_based_text_message(repr_system_msg, livechat_cust_obj, livechat_cust_obj.easychat_user_id)
                        send_channel_based_welcome_message(user_obj, livechat_cust_obj)
                            
                        user_obj.livechat_connected = False
                        user_obj.save()
                        continue
                else:
                    last_updated_time = livechat_cust_obj.joined_date.astimezone(
                        tz)
                    current_time = timezone.now().astimezone(tz)
                    available_time = (
                        current_time - last_updated_time).total_seconds()
                    if available_time >= LiveChatConfig.objects.filter(bot=livechat_cust_obj.bot)[0].queue_timer:
                        if not livechat_cust_obj.abruptly_closed:
                            send_event_for_abandoned_chat(livechat_cust_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot)
                        livechat_cust_obj.is_session_exp = True
                        livechat_cust_obj.abruptly_closed = True
                        livechat_cust_obj.save()
                        continue
                if livechat_cust_obj.agent_id != None or livechat_cust_obj.is_session_exp == True or livechat_cust_obj.is_denied == True:
                    continue
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
                    check_and_complete_whatsapp_reinitiated_conversation(livechat_cust_obj)
                    continue

                livechat_config_obj = LiveChatConfig.objects.filter(
                    bot=livechat_cust_obj.bot)[0]

                # If it is whatsapp reinitiated conversation then try to assign the same followup lead assigned agent
                if check_and_assign_whatsapp_reinitiated_conversation(livechat_cust_obj, agent_list, livechat_config_obj):
                    continue

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
                        
                        create_customer_details_system_message(livechat_cust_obj, LiveChatMISDashboard)

                        logger.info("Agent assigned cutomer count %s till now", str(
                            agent_list[agent] + 1), extra={'AppName': 'LiveChat'})
                        logger.info("Agent asignment success %s to %s", str(livechat_cust_obj.session_id),
                                    str(livechat_agent.user.username), extra={'AppName': 'LiveChat'})

                        if livechat_cust_obj.is_external:
                            push_livechat_event(AGENT_ASSIGNED_EVENT, livechat_cust_obj, {'agent_name': livechat_cust_obj.agent_id.get_agent_name()})
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

                            send_channel_based_text_message(livechat_notification, livechat_cust_obj, livechat_cust_obj.easychat_user_id)

                        break

                check_and_complete_whatsapp_reinitiated_conversation(livechat_cust_obj)

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
        livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.filter(livechat_customer=livechat_cust_obj, is_whatsapp_conversation_reinitiated=True, is_completed=False).first()

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

                    send_channel_based_text_message(livechat_notification, livechat_cust_obj, livechat_cust_obj.easychat_user_id)

                    return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_assign_whatsapp_reinitiated_conversation: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})      

    return False


def check_and_complete_whatsapp_reinitiated_conversation(livechat_cust_obj):
    try:
        livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.filter(livechat_customer=livechat_cust_obj, is_whatsapp_conversation_reinitiated=True, is_completed=False).first()

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
