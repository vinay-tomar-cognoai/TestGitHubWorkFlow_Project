#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from django.conf import settings
from rest_framework.test import APIClient
from EasyChatApp.models import User
from CampaignApp.models import *
from CampaignApp.encrypt import CustomEncrypt
from CampaignApp.utils import *
from CampaignApp.utils_external_api import *
from requests.auth import HTTPBasicAuth
import hashlib
import logging
import time
import json
import random
import execjs
import base64
import os
from datetime import datetime, timedelta
from Crypto import Random
from Crypto.Cipher import AES
logger = logging.getLogger(__name__)


class ExternalAPIs(TestCase):

    def setUp(self):
        logger.info('Setting up the test environment for CampaignApp: views...', extra={
                    'AppName': 'CampaignApp'})
        user_obj = User.objects.create(username='test_campaignapp',
                                       password='test_campaignapp')

        bot_obj = Bot.objects.create(
            name="Test Bot",
            bot_display_name="Test Bot")

        bot_obj.users.add(user_obj)
        bot_obj.save()

        self.create_draft_campaign()
        self.create_campaign_channel()

    def create_campaign_channel(self):
        channel_obj = CampaignChannel.objects.create(name="Whatsapp Business", value="whatsapp")
        channel_obj = CampaignChannel.objects.create(name="Voice Bot", value="voicebot")
        channel_obj = CampaignChannel.objects.create(name="RCS", value="rcs")

        return channel_obj

    def get_bot_obj(self):
        bot_obj = Bot.objects.get(name="Test Bot")
        return bot_obj

    def get_channel_obj(self):
        channel_obj = CampaignChannel.objects.all().first()
        return channel_obj

    def create_draft_campaign(self):
        bot_obj = self.get_bot_obj()
        total_campaigns = Campaign.objects.all().count()
        campaign_name = "Test Campaign " + str(total_campaigns)

        campaign_obj = Campaign.objects.create(
            name=campaign_name,
            bot=bot_obj,
            status=CAMPAIGN_DRAFT)

        return campaign_obj

    def create_in_progress_campaign(self):
        bot_obj = self.get_bot_obj()
        total_campaigns = Campaign.objects.all().count()
        campaign_name = "Test Campaign " + str(total_campaigns)

        campaign_obj = Campaign.objects.create(
            name=campaign_name,
            bot=bot_obj,
            status=CAMPAIGN_IN_PROGRESS)

        return campaign_obj

    def login_campaign_user(self, client):
        client.login(username='test_campaignapp',
                     password='test_campaignapp')

    def test_add_template_external_api(self):
        logger.info('Testing test_add_template_external_api...',
                    extra={'AppName': 'Campaign'})

        client = APIClient()
        self.login_campaign_user(client)

        bot_obj = self.get_bot_obj()
        
        data = {
            "campaign_name": "whatsapp Campaign",
            "channel_id": "1",
        }

        status, message, template_obj = add_template_external_api(data, bot_obj)
        self.assertEqual(status, 400)
        self.assertEqual(template_obj, None)

        data["template_variables"] = {
            "type": "Text",
            "language": "English (en)",
            "template name": "",
            "category": "TICKET_UPDATE",
            "message body template": ""
        }

        status, message, template_obj = add_template_external_api(data, bot_obj)
        self.assertEqual(status, 400)
        self.assertEqual(template_obj, None)

        data["template_variables"] = {
            "type": "Text",
            "language": "English (en)",
            "template_name": "terminal_update",
            "category": "TICKET_UPDATE",
            "message_body_template": "Your Terminal for Departure is {{1}}, please proceed to gate {{2}}. Please review your boarding pass for Boarding and Departure time. Have a safe flight.",
        }

        status, message, template_obj = add_template_external_api(data, bot_obj)
        self.assertEqual(status, 200)

    def test_add_template_external_api_voicebot(self):
        logger.info('Testing test_add_template_external_api...',
                    extra={'AppName': 'Campaign'})

        client = APIClient()
        self.login_campaign_user(client)

        bot_obj = self.get_bot_obj()
        
        data = {
            "campaign_name": "Voicebot Campaign",
            "channel_id": "2",
            "caller_id": "8047169879",
            "start_date": "",
            "end_date": "",
            "start_time": "11:02 AM",
            "end_time": "11:05 AM",
            "retry_mechanism": "linear",
            "no_of_retries": "2",
            "retry_interval": "",
            "is_busy_enabled": True,
            "is_no_answer_enabled": True,
            "is_failed_enabled": True
        }

        campaign_name = "Voicebot Campaign"
        channel_obj = CampaignChannel.objects.get(value="voicebot")

        status = add_template_external_api_voicebot(data, bot_obj, campaign_name, channel_obj)
        self.assertEqual(status[0], 400)

    def test_add_template_external_api_rcs(self):
        logger.info('Testing test_add_template_external_api_rcs...',
                    extra={'AppName': 'Campaign'})

        client = APIClient()
        self.login_campaign_user(client)

        bot_obj = self.get_bot_obj()
        
        data = {
            "campaign_name": "Whatsapp Campaign",
            "channel_id": "3",
        }

        status, message, template_obj = add_template_external_api_rcs(data, bot_obj)
        self.assertEqual(status, 400)
        self.assertEqual(template_obj, None)

        data["template_variables"] = {
            "template_name": "",
            "message_type": 1,
        }

        status, message, template_obj = add_template_external_api_rcs(data, bot_obj)
        self.assertEqual(status, 400)
        self.assertEqual(template_obj, None)

        data["template_variables"] = {
            "template_name": "Test RCS Template",
            "message_type": 1,
            "text_message": "Test text for RCS template",
            "suggested_reply": []
        }

        status = add_template_external_api_rcs(data, bot_obj)
        self.assertEqual(status[0], 200)
