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


class Views(TestCase):

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

    def test_GetActiveCampaignsAPI(self):
        logger.info('Testing test_GetActiveCampaignsAPI...',
                    extra={'AppName': 'Campaign'})

        client = APIClient()
        self.login_campaign_user(client)

        bot_obj = self.get_bot_obj()
        total_campaigns = Campaign.objects.filter(bot=bot_obj, channel__name__in=[
                                                  'Voice Bot', 'Whatsapp Business', 'RCS'], channel__is_deleted=False).count()

        json_string = json.dumps({
            "page": 1,
            "bot_pk": int(bot_obj.pk),
            "channels": ['Voice Bot', 'Whatsapp Business', 'RCS'],
            "searched_campaign": '',
            'filter_date_type': '4',
            'tab': 'all_campaigns'
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/get-active-campaign/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(len(response['active_campaigns']), total_campaigns)

        json_string = json.dumps({
            "page": 1,
            "bot_pk": 1234,
            "channels": ['Voice Bot', 'Whatsapp Business', 'RCS'],
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/get-active-campaign/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    # def test_DeleteCampaignsAPI(self):
    #     logger.info('Testing test_DeleteCampaignsAPI...',
    #                 extra={'AppName': 'Campaign'})

    #     client = APIClient()
    #     self.login_campaign_user(client)

    #     campaign_obj = self.create_draft_campaign()

    #     json_string = json.dumps({
    #         "campaign_ids": [str(campaign_obj.pk)]
    #     })

    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post('/campaign/delete-campaigns/',
    #                           json.dumps({'Request': json_string}),
    #                           content_type='application/json')

    #     response = \
    #         json.loads(custom_encrypt_obj.decrypt(request.data['Response'
    #                                                            ]))
    #     self.assertEqual(request.status_code, 200)
    #     self.assertEqual(response['status'], 200)

    #     deleted_campaign_obj = Campaign.objects.get(pk=campaign_obj.pk)
    #     self.assertEqual(deleted_campaign_obj.is_deleted, True)

    #     campaign_obj = self.create_in_progress_campaign()

    #     json_string = json.dumps({
    #         "campaign_ids": [str(campaign_obj.pk)]
    #     })

    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post('/campaign/delete-campaigns/',
    #                           json.dumps({'Request': json_string}),
    #                           content_type='application/json')

    #     response = \
    #         json.loads(custom_encrypt_obj.decrypt(request.data['Response'
    #                                                            ]))
    #     self.assertEqual(request.status_code, 200)
    #     self.assertEqual(response['status'], 401)

    #     updated_campaign_obj = Campaign.objects.get(pk=campaign_obj.pk)
    #     self.assertEqual(updated_campaign_obj.is_deleted, False)

    def test_CreateNewCampaignAPI(self):
        logger.info('Testing test_CreateNewCampaignAPI...',
                    extra={'AppName': 'Campaign'})

        client = APIClient()
        self.login_campaign_user(client)

        bot_obj = self.get_bot_obj()
        channel_obj = self.get_channel_obj()

        json_string = json.dumps({
            "bot_id": int(bot_obj.pk),
            "channel_id": int(channel_obj.pk),
            "campaign_name": "Campaign Test Random"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/create/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        campaign_obj = Campaign.objects.filter(
            name="Campaign Test Random").first()
        self.assertNotEqual(campaign_obj, None)

        json_string = json.dumps({
            "bot_id": int(bot_obj.pk),
            "channel_id": int(channel_obj.pk),
            "campaign_name": "Campaign Test Random"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/create/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        json_string = json.dumps({
            "bot_id": int(bot_obj.pk),
            "channel_id": int(channel_obj.pk),
            "campaign_name": "Campaign Test Random 2",
            "campaign_id": int(campaign_obj.pk),
            'filter_date_type': '4',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/create/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        campaign_obj = Campaign.objects.filter(
            name="Campaign Test Random 2").first()
        self.assertNotEqual(campaign_obj, None)

        json_string = json.dumps({
            "bot_id": int(bot_obj.pk),
            "channel_id": int(channel_obj.pk),
            "campaign_name": "Campaign Test Random 2",
            "campaign_id": int(campaign_obj.pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/create/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        campaign_obj = self.create_draft_campaign()
        json_string = json.dumps({
            "bot_id": int(bot_obj.pk),
            "channel_id": int(channel_obj.pk),
            "campaign_name": "Campaign Test Random 2",
            "campaign_id": int(campaign_obj.pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/create/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        campaign_obj = self.create_in_progress_campaign()
        json_string = json.dumps({
            "bot_id": int(bot_obj.pk),
            "channel_id": int(channel_obj.pk),
            "campaign_name": "Campaign Test Random 3",
            "campaign_id": int(campaign_obj.pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/create/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 401)

    def test_GetSelectedBotWSPCodeAPI(self):
        logger.info('Testing test_GetSelectedBotWSPCodeAPI...',
                    extra={'AppName': 'Campaign'})

        client = APIClient()
        self.login_campaign_user(client)
        bot_obj = self.get_bot_obj()

        user_obj = User.objects.get(username="test_campaignapp")
        bot_obj.users.add(user_obj)
        bot_obj.save()

        try:
            CampaignWhatsAppServiceProvider.objects.get(name="3")
        except:
            CampaignWhatsAppServiceProvider.objects.create(
                name="3", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/CampaignApp/campaignapp_rml_webhook.py")

        json_string = json.dumps({
            "bot_pk": bot_obj.pk,
            "wsp_code": "3",
            "is_reset": False
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/get-selected-bot-wsp-code/', json.dumps(
            {'Request': json_string}), content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            "bot_pk": "",
            "wsp_code": "3",
            "is_reset": False
        })
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/get-selected-bot-wsp-code/', json.dumps(
            {'Request': json_string}), content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_SaveExportVoiceCampaignHistoryRequestAPI(self):
        logger.info("Testing SaveExportVoiceCampaignHistoryRequestAPI...", extra={'AppName': 'Campaign', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting of SaveExportVoiceCampaignHistoryRequestAPI is going on...\n")

        client = APIClient()

        user_obj = User.objects.filter(username="testeasychat").first()
        if not user_obj:
            user_obj = User.objects.create(username="testeasychat", password="testeasychat")
        
        client.login(username="testeasychat", password="testeasychat")

        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")

        json_string = json.dumps({
            "bot_pk": str(bot_obj.pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/save-export-voice-campaign-history-request/', json.dumps(
            {"Request": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data['Response'])
        response = json.loads(response)
        assert response["status"] == "500"

        bot_obj.users.add(user_obj)
        bot_obj.save()
        json_string = json.dumps({
            "bot_pk": str(bot_obj.pk)
        })

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/save-export-voice-campaign-history-request/', json.dumps(
            {"Request": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data['Response'])
        response = json.loads(response)
        assert response["status"] == "200"

    def test_GetWhatsappAudienceCampaignDetailsPageAPI(self):
        logger.info("Testing GetWhatsappAudienceCampaignDetailsPageAPI...", extra={'AppName': 'Campaign', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        client = APIClient()
        self.login_campaign_user(client)

        bot_obj = self.get_bot_obj()
        campaign_obj = self.create_draft_campaign()
        campaign_template_lang_obj = CampaignTemplateLanguage.objects.create(title='test_language')
        channel_obj = CampaignChannel.objects.create(name="Whatsapp Business", value="whatsapp")
        template_obj = CampaignTemplate.objects.create(template_name='test template', bot=bot_obj)
        quick_reply_obj = QuickReply.objects.create(name='test_qr', bot=bot_obj)
        campaign_obj.campaign_template = template_obj
        campaign_obj.campaign_template.language = campaign_template_lang_obj
        campaign_obj.status = CAMPAIGN_COMPLETED
        campaign_obj.channel = channel_obj
        campaign_obj.save()
        audience_obj = CampaignAudience.objects.create(audience_id="test audience", campaign=campaign_obj)
        audience_log_obj = CampaignAudienceLog.objects.create(campaign=campaign_obj, audience=audience_obj, is_failed=False, recepient_id='test_recepient_id1')
        audience_log_obj.quick_replies.add(quick_reply_obj)
        quick_reply_obj.audience_log.add(audience_log_obj)
        audience_log_obj = CampaignAudienceLog.objects.create(campaign=campaign_obj, audience=audience_obj, is_failed=False, recepient_id='test_recepient_id2')
        audience_log_obj.quick_replies.add(quick_reply_obj)
        quick_reply_obj.audience_log.add(audience_log_obj)
        audience_log_obj = CampaignAudienceLog.objects.create(campaign=campaign_obj, audience=audience_obj, is_failed=False, recepient_id='test_recepient_id3')
        audience_log_obj.quick_replies.add(quick_reply_obj)
        quick_reply_obj.audience_log.add(audience_log_obj)

        data = json.dumps({
            "bot_pk": str(bot_obj.pk),
            "campaign_ids": [str(campaign_obj.pk)],
            "filter_date_type": "4",
            "start_date": "",
            "end_date": "",
            "status_filter": ['Success', 'Failed'],
            'quick_reply': [],
            'templates': [],
            'number_of_records': 3,
            'page': 1,
            'searched_value': "",
            'searched_type': "",
            'is_template_select': False,
            'is_first_render': False
        })

        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(data)

        request = client.post('/campaign/get-whatsapp-audience-campaign-details/',
                              json.dumps({'Request': data}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(response['status'], "200")

        data = json.dumps({
            "bot_pk": "",
            "campaign_ids": [str(campaign_obj.pk)],
            "filter_date_type": "4",
            "start_date": "",
            "end_date": "",
            "status_filter": ['Success', 'Failed'],
            'quick_reply': [],
            'templates': [],
            'number_of_records': 3,
            'page': 1,
            'searched_value': "",
            'searched_type': "",
            'is_template_select': False,
            'is_first_render': False
        })

        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(data)

        request = client.post('/campaign/get-whatsapp-audience-campaign-details/',
                              json.dumps({'Request': data}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(response['status'], "500")
        
        custom_start_date = ""
        custom_end_date = ""
        data = json.dumps({
            "bot_pk": str(bot_obj.pk),
            "campaign_ids": [str(campaign_obj.pk)],
            "filter_date_type": "5",
            "start_date": custom_start_date,
            "end_date": custom_end_date,
            "status_filter": ['Success', 'Failed'],
            'quick_reply': [],
            'templates': [],
            'number_of_records': 3,
            'page': 1,
            'searched_value': "",
            'searched_type': "",
            'is_template_select': False,
            'is_first_render': False
        })

        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(data)

        request = client.post('/campaign/get-whatsapp-audience-campaign-details/',
                              json.dumps({'Request': data}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        
        self.assertEqual(response['status'], "200")
        # self.assertEqual(response["date_range_list"], None)
        # self.assertEqual(response["date_range_list"], None)

        custom_start_date = "2022-07-28"
        custom_end_date = "2022-08-29"
        data = json.dumps({
            "bot_pk": str(bot_obj.pk),
            "campaign_ids": [str(campaign_obj.pk)],
            "filter_date_type": "5",
            "start_date": custom_start_date,
            "end_date": custom_end_date,
            "status_filter": ['Success', 'Failed'],
            'quick_reply': [],
            'templates': [],
            'number_of_records': 3,
            'page': 1,
            'searched_value': "",
            'searched_type': "",
            'is_template_select': False,
            'is_first_render': False
        })

        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(data)

        request = client.post('/campaign/get-whatsapp-audience-campaign-details/',
                              json.dumps({'Request': data}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(response['status'], "200")
        
        data = json.dumps({
            "bot_pk": str(bot_obj.pk),
            "campaign_ids": [str(campaign_obj.pk)],
            "filter_date_type": "4",
            "start_date": '',
            "end_date": '',
            "status_filter": [],
            'quick_reply': [],
            'templates': ['test template'],
            'number_of_records': 3,
            'page': 1,
            'searched_value': "",
            'searched_type': "",
            'is_template_select': True,
            'is_first_render': False
        })
        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(data)

        request = client.post('/campaign/get-whatsapp-audience-campaign-details/',
                              json.dumps({'Request': data}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(response['status'], "200")
        self.assertGreaterEqual(response['pagination_metadata']['total_count'], 1)

        data = json.dumps({
            "bot_pk": str(bot_obj.pk),
            "campaign_ids": [],
            "filter_date_type": "4",
            "start_date": '',
            "end_date": '',
            "status_filter": [],
            'quick_reply': [],
            'templates': ['test template'],
            'number_of_records': 3,
            'page': 1,
            'searched_value': "",
            'searched_type': "",
            'is_template_select': False,
            'is_first_render': False
        })
        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(data)

        request = client.post('/campaign/get-whatsapp-audience-campaign-details/',
                              json.dumps({'Request': data}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(response['status'], "200")
        self.assertEqual(response['pagination_metadata']['total_count'], 0)

        data = json.dumps({
            "bot_pk": str(bot_obj.pk),
            "campaign_ids": [str(campaign_obj.pk)],
            "filter_date_type": "4",
            "start_date": '',
            "end_date": '',
            "status_filter": ['Failed'],
            'quick_reply': [],
            'templates': [],
            'number_of_records': 3,
            'page': 1,
            'searched_value': "",
            'searched_type': "",
            'is_template_select': False,
            'is_first_render': False
        })
        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(data)

        request = client.post('/campaign/get-whatsapp-audience-campaign-details/',
                              json.dumps({'Request': data}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(response['status'], "200")
        self.assertEqual(response['pagination_metadata']['total_count'], 0)

        data = json.dumps({
            "bot_pk": str(bot_obj.pk),
            "campaign_ids": [str(campaign_obj.pk)],
            "filter_date_type": "4",
            "start_date": '',
            "end_date": '',
            "status_filter": [],
            'quick_reply': ['not_saved_qr'],
            'templates': ['test template'],
            'number_of_records': 3,
            'page': 1,
            'searched_value': "",
            'searched_type': "",
            'is_template_select': False,
            'is_first_render': False
        })
        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(data)

        request = client.post('/campaign/get-whatsapp-audience-campaign-details/',
                              json.dumps({'Request': data}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        
        self.assertEqual(response['status'], "200")
        self.assertEqual(response['pagination_metadata']['total_count'], 0)

        data = json.dumps({
            "bot_pk": str(bot_obj.pk),
            "campaign_ids": [str(campaign_obj.pk)],
            "filter_date_type": "4",
            "start_date": '',
            "end_date": '',
            "status_filter": [],
            'quick_reply': ['test_qr'],
            'templates': ['test template'],
            'number_of_records': 3,
            'page': 1,
            'searched_value': "",
            'searched_type': "",
            'is_template_select': True,
            'is_first_render': False
        })
        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(data)

        request = client.post('/campaign/get-whatsapp-audience-campaign-details/',
                              json.dumps({'Request': data}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(response['status'], "200")
        self.assertGreaterEqual(response['pagination_metadata']['total_count'], 1)
        self.assertEqual(response['quick_reply_data'][0], 'test_qr')

        data = json.dumps({
            "bot_pk": str(bot_obj.pk),
            "campaign_ids": [str(campaign_obj.pk)],
            "filter_date_type": "4",
            "start_date": "",
            "end_date": "",
            "status_filter": ['Success', 'Failed'],
            'quick_reply': ['test_qr'],
            'templates': [],
            'number_of_records': 3,
            'page': 1,
            'searched_value': "",
            'searched_type': "",
            'is_template_select': False,
            'is_first_render': False
        })

        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(data)

        request = client.post('/campaign/get-whatsapp-audience-campaign-details/',
                              json.dumps({'Request': data}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(response['status'], "200")
        self.assertGreaterEqual(response['pagination_metadata']['total_count'], 1)
        self.assertEqual(response['selected_template_names'][0], 'test template')

    def test_SaveExportWhatsappCampaignHistoryRequestAPI(self):
        logger.info("Testing SaveExportWhatsappCampaignHistoryRequestAPI...", extra={'AppName': 'Campaign', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        client = APIClient()

        self.login_campaign_user(client)

        bot_obj = self.get_bot_obj()
        campaign_obj = self.create_draft_campaign()
        json_string = json.dumps({
            "bot_pk": str(''),
            "campaign_ids": [str(campaign_obj.pk)],
            "filter_date_type": "4",
            "start_date": "",
            "end_date": "",
            "status_filter": ['Success', 'Failed'],
            'quick_reply': [],
            'templates': [],
            'number_of_records': 3,
            'page': 1,
            'searched_value': "",
            'searched_type': "",
            'is_template_select': False,
            'is_first_render': False
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/save-export-whatsapp-campaign-history-request/', json.dumps(
            {"Request": json_string}), content_type='application/json')
        response = custom_encrypt_obj.decrypt(request.data['Response'])
        response = json.loads(response)
        self.assertEqual(response['status'], "500")

        json_string = json.dumps({
            "bot_pk": str(bot_obj.pk),
            "campaign_ids": [str(campaign_obj.pk)],
            "filter_date_type": "4",
            "start_date": "",
            "end_date": "",
            "status_filter": ['Success', 'Failed'],
            'quick_reply': [],
            'templates': [],
            'number_of_records': 3,
            'page': 1,
            'searched_value': "",
            'searched_type': "",
            'is_template_select': False,
            'is_first_render': False
        })

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/campaign/save-export-whatsapp-campaign-history-request/', json.dumps(
            {"Request": json_string}), content_type='application/json')
        response = custom_encrypt_obj.decrypt(request.data['Response'])
        response = json.loads(response)
        self.assertEqual(response['status'], "200")
