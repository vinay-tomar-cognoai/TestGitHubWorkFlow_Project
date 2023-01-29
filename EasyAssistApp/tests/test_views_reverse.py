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
from datetime import datetime, timedelta
from Crypto import Random
from Crypto.Cipher import AES
logger = logging.getLogger(__name__)


class Views(TestCase):

    def setUp(self):
        logger.info('Setting up the test environment for EasyAssistApp: views...', extra={
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

    def test_CobrowseIOReverseInitializeAPI(self):
        logger.info('Testing test_CobrowseIOReverseInitializeAPI...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        access_token = cobrowse_agent.get_access_token_obj()
        custom_encrypt_obj = CustomEncrypt()

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        json_string = json.dumps({
            'name': 'Cogno AI',
            'mobile_number': '9512395123',
            'virtual_agent_code': '12121212121221',
            'active_url': 'https://www.hdfccredila.com/apply-for-loan.html',
            'meta_data': {'product_details': {'title': 'Apply for Education Loan | HDFC Credila',
                                              'description': 'Apply online for education loan at HDFC Credila from anywhere and get confirmed education loan before your admission.',
                                              'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                                              }},
            'client_email': 'abcxyzdummy@abcxyzmail.com'
        })

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/reverse/initialize/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        # domain is not whitelisted in accesstoken

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        request = client.post('/easy-assist/reverse/initialize/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 101)

        json_string = json.dumps({
            'name': 'Cogno AI',
            'mobile_number': '9512395123',
            'virtual_agent_code': cobrowse_agent.virtual_agent_code,
            'active_url': 'https://www.hdfccredila.com/apply-for-loan.html',
            'meta_data': {'product_details': {'title': 'Apply for Education Loan | HDFC Credila',
                                              'description': 'Apply online for education loan at HDFC Credila from anywhere and get confirmed education loan before your admission.',
                                              'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                                              }},
            'client_email': 'abcxyzdummy@abcxyzmail.com'
        })

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/reverse/initialize/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        session_id = response['session_id']
        cobrowseio = \
            CobrowseIO.objects.filter(session_id=session_id).first()
        self.assertNotEqual(cobrowseio, None)
        self.assertEqual(cobrowseio.agent, cobrowse_agent)
        self.assertEqual(cobrowseio.is_reverse_cobrowsing, True)

    def test_CheckAgentReverseCobrowseStatusAPI(self):
        logger.info('Testing test_CheckAgentReverseCobrowseStatusAPI...', extra={
                    'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.save()

        access_token = cobrowse_agent.get_access_token_obj()
        cobrowseio = CobrowseIO.objects.create()
        custom_encrypt_obj = CustomEncrypt()

        http_authorization = 'Bearer ' \
            + custom_encrypt_obj.encrypt(str(cobrowseio.session_id) + ':' + str(int(time.time())))

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        json_string = \
            json.dumps({'session_id': str(cobrowseio.session_id)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/reverse/check-agent-status/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        self.assertEqual(request.status_code, 401)

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key),
                           HTTP_AUTHORIZATION=http_authorization)

        request = client.post('/easy-assist/reverse/check-agent-status/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        cobrowseio.agent = cobrowse_agent
        cobrowseio.access_token = access_token
        cobrowseio.last_update_datetime = datetime.now()
        cobrowseio.is_active = True
        cobrowseio.save()

        request = client.post('/easy-assist/reverse/check-agent-status/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['is_archived'], False)
        self.assertEqual(response['is_customer_connected'], True)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertNotEqual(cobrowseio, None)
        self.assertNotEqual(cobrowseio.last_agent_update_datetime, None)
        self.assertEqual(cobrowseio.is_agent_connected, True)

        cobrowseio.last_update_datetime = datetime.now() \
            - timedelta(seconds=access_token.archive_on_common_inactivity_threshold * 60 + 1)
        cobrowseio.save()

        request = client.post('/easy-assist/reverse/check-agent-status/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['is_archived'], False)
        self.assertEqual(response['is_customer_connected'], False)

        cobrowseio.last_update_datetime = datetime.now() \
            - timedelta(seconds=access_token.auto_archive_cobrowsing_session_timer * 60 + 1)
        cobrowseio.save()

        request = client.post('/easy-assist/reverse/check-agent-status/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['is_archived'], True)
        self.assertEqual(response['is_customer_connected'], False)

    def test_CloseReverseAgentCobrowsingSessionAPI(self):
        logger.info('Testing test_CloseReverseAgentCobrowsingSessionAPI...', extra={
                    'AppName': 'EasyAssist'})

        client = APIClient()
        custom_encrypt_obj = CustomEncrypt()

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowseio = CobrowseIO.objects.create(agent=cobrowse_agent,
                                               cobrowsing_start_datetime=timezone.now(),
                                               meeting_start_datetime=None)

        json_string = \
            json.dumps({'session_id': str(cobrowseio.session_id),
                        'feedback': 'feedback', 'subcomments': 'subcomments'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/agent-close-session/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.is_helpful, False)
        self.assertEqual(cobrowseio.is_archived, True)
        self.assertNotEqual(cobrowseio.last_agent_update_datetime, None)
        self.assertEqual(cobrowseio.session_archived_cause,
                         'AGENT_ENDED')

        cobrowse_agent_comment = \
            CobrowseAgentComment.objects.filter(cobrowse_io=cobrowseio,
                                                agent=cobrowse_agent, agent_comments='feedback',
                                                comment_desc='').first()
        self.assertNotEqual(cobrowse_agent_comment, None)

        CobrowseIO.objects.all().delete()
        cobrowseio = CobrowseIO.objects.create(agent=cobrowse_agent,
                                               cobrowsing_start_datetime=None,
                                               meeting_start_datetime=timezone.now())

        json_string = \
            json.dumps({'session_id': str(cobrowseio.session_id),
                        'feedback': 'feedback', 'is_helpful': True, 'subcomments': 'subcomments'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/agent-close-session/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.is_helpful, True)
        self.assertEqual(cobrowseio.is_archived, True)
        self.assertNotEqual(cobrowseio.last_agent_update_datetime, None)
        self.assertEqual(cobrowseio.session_archived_cause,
                         'AGENT_ENDED')

        cobrowse_agent_comment = \
            CobrowseAgentComment.objects.filter(cobrowse_io=cobrowseio,
                                                agent=cobrowse_agent, agent_comments='feedback',
                                                comment_desc='').first()
        self.assertNotEqual(cobrowse_agent_comment, None)

        CobrowseIO.objects.all().delete()
        cobrowseio = CobrowseIO.objects.create(agent=cobrowse_agent,
                                               cobrowsing_start_datetime=None,
                                               meeting_start_datetime=None)

        json_string = json.dumps({
            'session_id': str(cobrowseio.session_id),
            'feedback': 'feedback',
            'subcomments': 'subcomments',
            'is_helpful': True,
            'comment_desc': 'comment_desc',
        })
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/agent-close-session/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.is_helpful, True)
        self.assertEqual(cobrowseio.is_archived, True)
        self.assertNotEqual(cobrowseio.last_agent_update_datetime, None)
        self.assertEqual(cobrowseio.session_archived_cause,
                         'UNATTENDED')

        cobrowse_agent_comment = \
            CobrowseAgentComment.objects.filter(cobrowse_io=cobrowseio,
                                                agent=cobrowse_agent, agent_comments='feedback',
                                                comment_desc='comment_desc').first()
        self.assertNotEqual(cobrowse_agent_comment, None)

    def test_RequestVoipMeetingAPI(self):
        logger.info('Testing test_RequestVoipMeetingAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowseio = CobrowseIO.objects.create(full_name='Test',
                                               mobile_number='9191919191', agent=cobrowse_agent,
                                               access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowseio.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/request-assist-meeting/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowseio = CobrowseIO.objects.all().first()
        meeting_io = CobrowseVideoConferencing.objects.all().first()

        self.assertNotEqual(cobrowseio, None)
        self.assertNotEqual(meeting_io, None)
        self.assertEqual(cobrowseio.agent_meeting_request_status, True)
        self.assertEqual(cobrowseio.allow_agent_meeting, None)
        self.assertNotEqual(meeting_io.agent, None)

    def test_CheckReverseCobrowsingMeetingStatusAPI(self):
        logger.info('Testing test_CheckReverseCobrowsingMeetingStatusAPI...', extra={
                    'AppName': 'EasyAssist'})

        client = APIClient()

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.is_cognomeet_active = False
        cobrowse_agent.save()

        cobrowseio = CobrowseIO.objects.create()

        cobrowseio.allow_agent_meeting = None
        cobrowseio.agent = cobrowse_agent
        cobrowseio.save()

        json_string = \
            json.dumps({'session_id': str(cobrowseio.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/check-meeting-status/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)
        self.assertEqual(response['is_meeting_allowed'], False)
        self.assertEqual(response['is_client_answer'], False)
        self.assertEqual(response['is_cognomeet_active'], False)

        cobrowseio.allow_agent_meeting = 'true'
        cobrowseio.save()

        cobrowse_agent.is_cognomeet_active = True
        cobrowse_agent.save()

        json_string = \
            json.dumps({'session_id': str(cobrowseio.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/check-meeting-status/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['is_meeting_allowed'], True)
        self.assertEqual(response['is_client_answer'], True)
        self.assertEqual(response['is_cognomeet_active'], True)

        cobrowseio.allow_agent_meeting = 'false'
        cobrowseio.save()

        json_string = \
            json.dumps({'session_id': str(cobrowseio.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/check-meeting-status/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['is_meeting_allowed'], False)
        self.assertEqual(response['is_client_answer'], True)
        self.assertEqual(response['is_cognomeet_active'], True)

    def test_SaveClientLocationAPI(self):
        logger.info('Testing test_SaveClientLocationAPI...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.save()

        cobrowseio = CobrowseIO.objects.create()

        client = APIClient()

        json_string = \
            json.dumps({'session_id': str(cobrowseio.session_id),
                        'latitude': '19.123437644435743',
                        'longitude': '72.89066562607881'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/reverse/save-client-location/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.latitude, '19.123437644435743')
        self.assertEqual(cobrowseio.longitude, '72.89066562607881')
