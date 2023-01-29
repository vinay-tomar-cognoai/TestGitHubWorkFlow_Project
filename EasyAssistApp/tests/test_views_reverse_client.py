#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from django.conf import settings
from rest_framework.test import APIClient
from EasyChatApp.models import User
from EasyAssistApp.models import *
from EasyAssistApp.encrypt import CustomEncrypt
from EasyAssistApp.utils import *
from requests.auth import HTTPBasicAuth
import hashlib
import logging
import time
import json
import random
import execjs
import base64
import os
from datetime import datetime
from Crypto import Random
from Crypto.Cipher import AES
logger = logging.getLogger(__name__)


class ViewsReverseClient(TestCase):

    def setUp(self):
        logger.info('Setting up the test environment for EasyAssistApp: views_reverse_client...', extra={
                    'AppName': 'EasyAssist'})
        user = User.objects.create(username='testeasyassist',
                                   password='testeasyassist')
        support_user = \
            User.objects.create(username='support_testeasyassist',
                                password='testeasyassist')
        supervisor_user = \
            User.objects.create(username='supervisor_testeasyassist',
                                password='testeasyassist')

        cobrowse_agent = CobrowseAgent.objects.create(user=user)
        cobrowse_agent.is_switch_allowed = True
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        cobrowse_agent = CobrowseAgent.objects.create(user=support_user)
        cobrowse_agent.is_switch_allowed = False
        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        cobrowse_agent = \
            CobrowseAgent.objects.create(user=supervisor_user)
        cobrowse_agent.is_switch_allowed = True
        cobrowse_agent.role = 'supervisor'
        cobrowse_agent.save()

    def tearDown(self):
        access_token_objs = CobrowseAccessToken.objects.all()
        for access_token_obj in access_token_objs:
            delete_access_token_specific_static_file(str(access_token_obj.key))

    def test_CheckClientReverseCobrowseStatusAPI(self):
        logger.info('Testing test_CheckClientReverseCobrowseStatusAPI...', extra={
                    'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_io_obj = CobrowseIO.objects.create(
            full_name='Test',
            mobile_number='9191919191',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            is_reverse_cobrowsing=True,
        )

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/check-client-status/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_io_obj.is_archived = True
        cobrowse_io_obj.save()

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/check-client-status/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['is_archived'], True)

    def test_SaveReverseCobrowsingChatAPI(self):
        logger.info('Testing test_SaveReverseCobrowsingChatAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_io_obj = CobrowseIO.objects.create(
            full_name='Test',
            mobile_number='9191919191',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            is_reverse_cobrowsing=True,
        )

        json_string = json.dumps({
            'session_id': str(cobrowse_io_obj.session_id),
            'sender': 'agent',
            'message': 'hello',
            'attachment': 'None',
            'attachment_file_name': 'None',
            'agent_username': 'admin',
            'chat_type': 'chat_message',
            'agent_profile_pic_source': '',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/save-cobrowsing-chat/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            'session_id': str(cobrowse_io_obj.session_id),
            'sender': 'client',
            'message': 'hiii',
            'attachment': 'None',
            'attachment_file_name': 'None',
            'agent_username': 'admin',
            'chat_type': 'chat_message',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/save-cobrowsing-chat/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetReverseCobrowsingChatHistoryAPI(self):
        logger.info('Testing test_GetReverseCobrowsingChatHistoryAPI...', extra={
                    'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_io_obj = CobrowseIO.objects.create(
            full_name='Test',
            mobile_number='9191919191',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            is_reverse_cobrowsing=True,
        )

        json_string = json.dumps({
            'session_id': str(cobrowse_io_obj.session_id),
            'sender': 'agent',
            'message': 'hello',
            'attachment': 'None',
            'attachment_file_name': 'None',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/get-cobrowsing-chat-history/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            'session_id': str(cobrowse_io_obj.session_id),
            'sender': 'client',
            'message': 'hiii',
            'attachment': 'None',
            'attachment_file_name': 'None',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/get-cobrowsing-chat-history/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/get-cobrowsing-chat-history/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_CloseReverseCobrowsingSessionAPI(self):
        logger.info('Testing test_CloseReverseCobrowsingSessionAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_io_obj = CobrowseIO.objects.create(
            full_name='Test',
            mobile_number='9191919191',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            is_reverse_cobrowsing=True,
        )

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'comments': 'Good Reverse Cobrowsing',
                        'rating': 10})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/client-close-session/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_UpdateReverseCobrowseMeetingRequestAPI(self):
        logger.info('Testing test_UpdateReverseCobrowseMeetingRequestAPI...', extra={
                    'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_io_obj = CobrowseIO.objects.create(
            full_name='Test',
            mobile_number='9191919191',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            is_reverse_cobrowsing=True,
        )

        json_string = \
            json.dumps({'id': str(cobrowse_io_obj.session_id),
                        'status': 'true'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/update-agent-meeting-request/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = \
            json.dumps({'id': str(cobrowse_io_obj.session_id),
                        'status': 'false'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/update-agent-meeting-request/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
