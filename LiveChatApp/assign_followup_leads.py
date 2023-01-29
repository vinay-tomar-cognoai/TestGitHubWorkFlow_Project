import sys
import time
import json
import logging
import requests
import threading
import mimetypes
import datetime
import http.client
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count
from LiveChatApp.models import LiveChatCustomer, LiveChatConfig, LiveChatUser, LiveChatMISDashboard, LiveChatFollowupCustomer


logger = logging.getLogger(__name__)


def assign_followup_leads_to_agents():
    try:
        logger.info("---------- Assigning Follow Up Leads to Agents  ---------",
                    extra={'AppName': 'LiveChat'})

        bot_objs = LiveChatConfig.objects.filter(is_followup_lead_enabled=True).values('bot')
        livechat_cust_objs = LiveChatCustomer.objects.filter(bot__in=bot_objs, followup_assignment=False, is_session_exp=True, agent_id=None)

        for livechat_cust_obj in livechat_cust_objs:

            bot_obj = livechat_cust_obj.bot
            livechat_config = LiveChatConfig.objects.get(bot=bot_obj)
            followup_lead_sources = json.loads(livechat_config.followup_lead_sources) 

            if not livechat_config.is_followup_lead_enabled or len(followup_lead_sources) == 0:
                continue 

            chat_type = ""

            if livechat_cust_obj.is_system_denied:
                chat_type = 'offline_chats'
            elif livechat_cust_obj.is_denied:
                chat_type = 'missed_chats'
            elif livechat_cust_obj.abruptly_closed:
                chat_type = 'abandoned_chats'

            if chat_type not in followup_lead_sources:
                continue        

            logger.info(livechat_cust_obj.category,
                        extra={'AppName': 'LiveChat'})
            logger.info(livechat_cust_obj.bot, extra={
                        'AppName': 'LiveChat'})

            livechat_agents = LiveChatUser.objects.filter(status="3", category__in=[livechat_cust_obj.category], bots__in=[
                livechat_cust_obj.bot], is_deleted=False).order_by('last_followup_lead_assigned_time')
            logger.info(livechat_agents, extra={'AppName': 'LiveChat'})

            if livechat_agents.count() == 0:
                logger.info("No agents for this follow up lead", extra={
                            'AppName': 'LiveChat'})
                continue

            # Considering the agent according to last assigned time
            livechat_agent = livechat_agents.first()

            LiveChatFollowupCustomer.objects.create(livechat_customer=livechat_cust_obj, agent_id=livechat_agent, source=chat_type, assigned_date=timezone.now())
            livechat_cust_obj.followup_assignment = True
            livechat_cust_obj.save()
            livechat_agent.last_followup_lead_assigned_time = timezone.now()
            livechat_agent.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("assign_followup_leads_to_agents: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
