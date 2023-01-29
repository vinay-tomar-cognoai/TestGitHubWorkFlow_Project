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


class ViewsAgent(TestCase):

    def setUp(self):
        logger.info('Setting up the test environment for EasyAssistApp: views_agent...', extra={
                    'AppName': 'EasyAssist'})
        user = User.objects.create(username='testeasyassist',
                                   password='testeasyassist')
        support_user = \
            User.objects.create(username='support_testeasyassist',
                                password='testeasyassist')
        supervisor_user = \
            User.objects.create(username='supervisor_testeasyassist',
                                password='testeasyassist')

        admin_ally_user = \
            User.objects.create(username='admin_ally_testeasyassist',
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

        cobrowse_agent = \
            CobrowseAgent.objects.create(user=admin_ally_user)
        cobrowse_agent.is_switch_allowed = True
        cobrowse_agent.role = 'admin_ally'
        cobrowse_agent.save()

    def tearDown(self):
        access_token_objs = CobrowseAccessToken.objects.all()
        for access_token_obj in access_token_objs:
            delete_access_token_specific_static_file(str(access_token_obj.key))

    def test_SyncCobrowseIOAgentAPI(self):
        logger.info('Testing test_SyncCobrowseIOAgentAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/sync/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_SyncHighlightCobrowseIOAgentAPI(self):
        logger.info('Testing test_SyncHighlightCobrowseIOAgentAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'id': str(cobrowse_io_obj.session_id),
                        'position': {'ClientX': 100, 'ClientY': 100}})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/highlight/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_TakeClientScreenshotAPI(self):
        logger.info('Testing test_TakeClientScreenshotAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'id': str(cobrowse_io_obj.session_id),
                        'screenshot_type': 'image'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/take-client-screenshot/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_CloseCobrowsingSessionAPI(self):
        logger.info('Testing test_CloseCobrowsingSessionAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='support_testeasyassist',
                     password='testeasyassist')
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        support_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist'
                                      )
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        # Test for Invited Agent leave cobrowsing

        cobrowse_io_obj.support_agents.add(support_agent)
        cobrowse_io_obj.save()

        json_string = \
            json.dumps({'id': str(cobrowse_io_obj.session_id),
                        'is_leaving': True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/close-session/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        # Test for Agent ending the session

        client.logout()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9292929292', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        agent_comment = 'Good Feature'
        agent_subcomments = 'Very efficient'
        json_string = \
            json.dumps({'id': str(cobrowse_io_obj.session_id),
                        'comments': agent_comment, 'subcomments': agent_subcomments, 'is_helpful': True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/close-session/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        # Test for Agent updating the session

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9292929292', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())
        agent_comment = 'Good Feature'
        agent_subcomments = 'Very efficient'
        json_string = json.dumps({
            'id': str(cobrowse_io_obj.session_id),
            'comments': agent_comment,
            'subcomments': agent_subcomments,
            'is_helpful': True,
            'is_lead_updated': True,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/close-session/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        # Test for Agent marking the session as test session

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9292929292', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())
        agent_comment = 'Good Feature'
        agent_subcomments = 'Very efficient'
        json_string = json.dumps({
            'id': str(cobrowse_io_obj.session_id),
            'comments': agent_comment,
            'subcomments': agent_subcomments,
            'is_helpful': True,
            'is_lead_updated': True,
            'is_test': True,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/close-session/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        # Test for Agent ending only video meeting session

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9292929292', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        meeting_io_obj = \
            CobrowseVideoConferencing.objects.create(meeting_id=cobrowse_io_obj.session_id,
                                                     agent=cobrowse_agent,
                                                     full_name=cobrowse_io_obj.full_name,
                                                     mobile_number=cobrowse_io_obj.mobile_number)
        CobrowseVideoAuditTrail.objects.create(cobrowse_video=meeting_io_obj)

        json_string = json.dumps({
            'id': str(cobrowse_io_obj.session_id),
            'comments': agent_comment,
            'subcomments': agent_subcomments,
            'is_helpful': True,
            'is_lead_updated': True,
            'is_test': True,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/close-session/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetCobrowsingMetaInformationAPI(self):
        logger.info('Testing test_GetCobrowsingMetaInformationAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'id': str(cobrowse_io_obj.session_id),
                        'page': 1})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/get-meta-information/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_ChangeAgentActiveStatusAPI(self):
        logger.info('Testing test_ChangeAgentActiveStatusAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        # Agent online status is True

        json_string = json.dumps({'active_status': True,
                                  'location': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/change-active-status/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        # Agent online status is False

        json_string = json.dumps({'active_status': False,
                                  'location': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/change-active-status/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        # Agent online status is neither True nor False

        json_string = json.dumps({'active_status': 'some',
                                  'location': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/change-active-status/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_SaveAgentDetailsAPI(self):
        logger.info('Testing test_SaveAgentDetailsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        json_string = json.dumps({
            'old_password': 'testeasyassist',
            'new_password': 'new_password',
            'agent_name': 'Test Agent',
            'agent_mobile_number': '9292929292',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/save-details/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        client.login(username='testeasyassist', password='new_password')
        json_string = json.dumps({
            'old_password': 'abcd',
            'new_password': 'testeasyassist',
            'agent_name': 'Test Agent',
            'agent_mobile_number': '9292929292',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/save-details/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 101)

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'old_password': 'new_password',
            'new_password': 'new_password2',
            'agent_name': 'Test Agent',
            'agent_mobile_number': '9292929292',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/save-details/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_AddNewAgentDetailsAPI(self):
        logger.info('Testing test_AddNewAgentDetailsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        json_string = json.dumps({
            'agent_mobile': '9393939393',
            'agent_email': 'test@example.com',
            'agent_name': 'New Agent',
            'user_type': 'agent',
            'support_level': 'l1',
            'platform_url': 'https://test.example.com',
            'selected_supervisor_pk_list': ['1'],
            'selected_language_pk_list': [],
            'selected_product_category_pk_list': [],
            'assign_followup_lead_to_agent': True
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/add-new-agent/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            'agent_mobile': '9494949494',
            'agent_email': 'test@example.com',
            'agent_name': 'New Agent',
            'user_type': 'agent',
            'support_level': 'l1',
            'platform_url': 'https://test.example.com',
            'selected_supervisor_pk_list': ['1'],
            'selected_language_pk_list': [],
            'selected_product_category_pk_list': [],
            'assign_followup_lead_to_agent': True
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/add-new-agent/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        json_string = json.dumps({
            'agent_mobile': '9393939393',
            'agent_email': 'test2@example.com',
            'agent_name': 'New Agent',
            'user_type': 'agent',
            'support_level': 'l1',
            'platform_url': 'https://test.example.com',
            'selected_supervisor_pk_list': ['1'],
            'selected_language_pk_list': [],
            'selected_product_category_pk_list': [],
            'assign_followup_lead_to_agent': True
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/add-new-agent/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        json_string = json.dumps({
            'agent_mobile': '9494949494',
            'agent_email': 'test2@example.com',
            'agent_name': 'New Agent',
            'user_type': 'supervisor',
            'support_level': 'l1',
            'platform_url': 'https://test.example.com',
            'selected_supervisor_pk_list': ['1'],
            'selected_language_pk_list': [],
            'selected_product_category_pk_list': [],
            'assign_followup_lead_to_agent': True
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/add-new-agent/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_UpdateAgentDetailsAPI(self):
        logger.info('Testing test_UpdateAgentDetailsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        json_string = json.dumps({
            'agent_mobile': '9393939393',
            'agent_email': 'test@example.com',
            'agent_name': 'New Agent',
            'user_type': 'agent',
            'support_level': 'l1',
            'platform_url': 'https://test.example.com',
            'selected_supervisor_pk_list': ['1'],
            'selected_language_pk_list': [],
            'selected_product_category_pk_list': [],
            'assign_followup_lead_to_agent': False
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/add-new-agent/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_DeleteCobrowseAgentAPI(self):
        logger.info('Testing test_DeleteCobrowseAgentAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        new_user = User.objects.create(username='test_deleted_user',
                                       password='deleted_password')
        new_agent = CobrowseAgent.objects.create(user=new_user)
        new_agent.is_switch_allowed = True
        new_agent.role = 'admin'
        new_agent.save()

        json_string = json.dumps({'agent_pk': str(new_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/delete-cobrowse-agent/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({'agent_pk': '100'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/delete-cobrowse-agent/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_DeleteCobrowserLogoAPI(self):
        logger.info('Testing test_DeleteCobrowserLogoAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        json_string = json.dumps({})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/sales-ai/delete-cobrowser-logo/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_SaveAgentCommentsAPI(self):
        logger.info('Testing test_SaveAgentCommentsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_comments': 'Good'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/save-agent-comments/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_SearchCobrowsingLeadAPI(self):
        logger.info('Testing test_SearchCobrowsingLeadAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        search_value = '9191919191'
        md5_primary_id = hashlib.md5(search_value.encode()).hexdigest()

        cobrowse_io_obj = CobrowseIO.objects.create(
            full_name='Test',
            mobile_number='9191919191',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            is_lead=True,
        )

        capture_lead_obj = \
            CobrowseCapturedLeadData.objects.create(primary_value=md5_primary_id,
                                                    session_id=cobrowse_io_obj.session_id)

        cobrowse_io_obj.captured_lead.add(capture_lead_obj)

        json_string = json.dumps({'search_value': search_value})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/search-lead/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({'search_value': '93939393'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/search-lead/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        search_value = '9292929292'
        md5_primary_id = hashlib.md5(search_value.encode()).hexdigest()

        cobrowse_io_obj = CobrowseIO.objects.create(
            full_name='Test',
            mobile_number='9292929292',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            is_lead=True,
            last_update_datetime=timezone.now(),
        )

        capture_lead_obj = \
            CobrowseCapturedLeadData.objects.create(primary_value=md5_primary_id,
                                                    session_id=cobrowse_io_obj.session_id)

        cobrowse_io_obj.captured_lead.add(capture_lead_obj)

        json_string = json.dumps({'search_value': search_value,
                                  'session_id_list': [str(cobrowse_io_obj.session_id)]})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/search-lead/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_AssignCobrowsingLeadAPI(self):
        logger.info('Testing test_AssignCobrowsingLeadAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/assign-lead/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_AssignCobrowsingSessionAPI(self):
        logger.info('Testing test_AssignCobrowsingSessionAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.is_active = True
        cobrowse_agent.save()

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/assign-cobrowsing-session/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.is_active = False
        cobrowse_agent.save()

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/assign-cobrowsing-session/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 400)

    def test_SupervisoAssignCobrowsingLead(self):
        logger.info('Testing test_SupervisoAssignCobrowsingLead...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='supervisor_testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist'
                                      )

        cobrowse_agent.is_active = False
        cobrowse_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/supervisor-assign-lead/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 302)

        cobrowse_agent.is_active = True
        cobrowse_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/supervisor-assign-lead/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        invited_agent.is_active = False
        invited_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(invited_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/supervisor-assign-lead/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 302)

        invited_agent.is_active = True
        invited_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(invited_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/supervisor-assign-lead/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        invited_agent.is_active = True
        invited_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(
            full_name='Test',
            mobile_number='9191919191',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            cobrowsing_start_datetime=timezone.now(),
        )

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(invited_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/supervisor-assign-lead/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 303)

        invited_agent.is_active = True
        invited_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(
            full_name='Test',
            mobile_number='9191919191',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            cobrowsing_start_datetime=timezone.now(),
            is_archived=True,
        )

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(invited_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/supervisor-assign-lead/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 304)

        supervisor = \
            CobrowseAgent.objects.get(user__username='supervisor_testeasyassist'
                                      )
        supervisor.role = 'agent'
        supervisor.save()

        invited_agent.is_active = True
        invited_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(invited_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/supervisor-assign-lead/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 401)

        supervisor.role = 'supervisor'
        supervisor.save()

        cobrowse_agent.is_active = True
        cobrowse_agent.save()

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())
        
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/supervisor-assign-lead/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 501)

    def test_RequestCobrowsingAPI(self):
        logger.info('Testing test_RequestCobrowsingAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/request-assist/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_MarkLeadInactiveAPI(self):
        logger.info('Testing test_MarkLeadInactiveAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        CobrowseIO.objects.create(full_name='Test',
                                  mobile_number='9191919191', share_client_session=False,
                                  access_token=cobrowse_agent.get_access_token_obj())

        json_string = json.dumps({})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/mark-inactive/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_ChangeAgentActivateStatusAPI(self):
        logger.info('Testing test_ChangeAgentActivateStatusAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist'
                                      )

        json_string = \
            json.dumps({'agent_id_list': [str(invited_agent.pk)],
                        'activate': True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/change-agent-activate-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist'
                                      )

        CobrowseIO.objects.create(full_name='Test',
                                  mobile_number='9191919191', share_client_session=False,
                                  agent=invited_agent,
                                  access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'agent_id_list': [str(invited_agent.pk)],
                        'activate': False})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/change-agent-activate-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='supervisor_testeasyassist'
                                      )

        json_string = \
            json.dumps({'agent_id_list': [str(invited_agent.pk)],
                        'activate': True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/change-agent-activate-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='supervisor_testeasyassist'
                                      )

        CobrowseIO.objects.create(full_name='Test',
                                  mobile_number='9191919191', share_client_session=False,
                                  agent=invited_agent,
                                  access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'agent_id_list': [str(invited_agent.pk)],
                        'activate': False})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/change-agent-activate-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='admin_ally_testeasyassist'
                                      )

        json_string = \
            json.dumps({'agent_id_list': [str(invited_agent.pk)],
                        'activate': True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/change-agent-activate-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='admin_ally_testeasyassist'
                                      )

        CobrowseIO.objects.create(full_name='Test',
                                  mobile_number='9191919191', share_client_session=False,
                                  agent=invited_agent,
                                  access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'agent_id_list': [str(invited_agent.pk)],
                        'activate': False})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/change-agent-activate-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        client = APIClient()
        client.login(username='supervisor_testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(
                user__username='supervisor_testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist'
                                      )

        json_string = \
            json.dumps({'agent_id_list': [str(invited_agent.pk)],
                        'activate': True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/change-agent-activate-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        cobrowse_agent = \
            CobrowseAgent.objects.get(
                user__username='supervisor_testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist'
                                      )

        CobrowseIO.objects.create(full_name='Test',
                                  mobile_number='9191919191', share_client_session=False,
                                  agent=invited_agent,
                                  access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'agent_id_list': [str(invited_agent.pk)],
                        'activate': False})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/change-agent-activate-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        client = APIClient()
        client.login(username='admin_ally_testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(
                user__username='admin_ally_testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='supervisor_testeasyassist'
                                      )

        json_string = \
            json.dumps({'agent_id_list': [str(invited_agent.pk)],
                        'activate': False})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/change-agent-activate-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        cobrowse_agent = \
            CobrowseAgent.objects.get(
                user__username='admin_ally_testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='supervisor_testeasyassist'
                                      )

        CobrowseIO.objects.create(full_name='Test',
                                  mobile_number='9191919191', share_client_session=False,
                                  agent=invited_agent,
                                  access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'agent_id_list': [str(invited_agent.pk)],
                        'activate': True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/change-agent-activate-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        cobrowse_agent = \
            CobrowseAgent.objects.get(
                user__username='admin_ally_testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist'
                                      )

        CobrowseIO.objects.create(full_name='Test',
                                  mobile_number='9191919191', share_client_session=False,
                                  agent=invited_agent,
                                  access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'agent_id_list': [str(invited_agent.pk)],
                        'activate': False})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/change-agent-activate-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        client = APIClient()
        client.login(username='support_testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist'
                                      )

        json_string = \
            json.dumps({'agent_id_list': [str(invited_agent.pk)],
                        'activate': True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/change-agent-activate-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist'
                                      )

        CobrowseIO.objects.create(full_name='Test',
                                  mobile_number='9191919191', share_client_session=False,
                                  agent=invited_agent,
                                  access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'agent_id_list': [str(invited_agent.pk)],
                        'activate': False})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/change-agent-activate-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_AgentResetPasswordAPI(self):
        logger.info('Testing test_AgentResetPasswordAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        json_string = json.dumps({
            'username': 'testeasyassist',
            'captcha': '8081.8081',
            'user_captcha': '8082',
            'platform_url': 'http://example.com',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/verify-forgot-password/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 101)

        json_string = json.dumps({
            'username': 'testeasyassist',
            'captcha': generate_md5('8081') + '.8081',
            'user_captcha': '8081',
            'platform_url': 'http://test.example.com',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/verify-forgot-password/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_ShareCobrowsingSessionAPI(self):
        logger.info('Testing test_ShareCobrowsingSessionAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        invited_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist'
                                      )

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())
        json_string = \
            json.dumps({'support_agents': [str(invited_agent.pk)],
                        'id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/share-session/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetListOfSupportAgentsAPI(self):
        logger.info('Testing test_GetListOfSupportAgentsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())
        json_string = \
            json.dumps({'id': str(cobrowse_io_obj.session_id),
                        'selected_lang_pk': '-1',
                        'selected_product_category_pk': '-1'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/get-support-agents/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetSupportMaterialAgentAPI(self):
        logger.info('Testing test_GetSupportMaterialAgentAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())
        json_string = \
            json.dumps({'id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/get-support-material/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetCobrowsingAgentCommentsAPI(self):
        logger.info('Testing test_GetCobrowsingAgentCommentsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())
        json_string = \
            json.dumps({'id': str(cobrowse_io_obj.session_id),
                        'page': 1})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/get-cobrowse-agent-comments/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetSystemAuditTrailBasicActivityAPI(self):
        logger.info('Testing test_GetSystemAuditTrailBasicActivityAPI...', extra={
                    'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())
        json_string = \
            json.dumps({'id': str(cobrowse_io_obj.session_id),
                        'page': 1})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/get-system-audit-trail-basic-activity/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_SwitchAgentModeAPI(self):
        logger.info('Testing test_SwitchAgentModeAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        json_string = json.dumps({'active_status': True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/switch-agent-mode/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        client.logout()

        client.login(username='supervisor_testeasyassist',
                     password='testeasyassist')
        json_string = json.dumps({'active_status': True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/switch-agent-mode/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_SaveCobrowsingChatAPI(self):
        logger.info('Testing test_SaveCobrowsingChatAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())
        json_string = json.dumps({
            'session_id': str(cobrowse_io_obj.session_id),
            'sender': 'agent',
            'message': 'hello',
            'attachment': 'None',
            'attachment_file_name': 'None',
            'chat_type': 'chat_message',
            'agent_profile_pic_source': 'files/AgentProfilePicture/7dbf2045-e13a-4c68-911e-0e98776a3b70 - admin@xyz.com/F4UOh9sMbR_download.png',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/save-cobrowsing-chat/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())
        json_string = json.dumps({
            'session_id': str(cobrowse_io_obj.session_id),
            'sender': 'client',
            'message': 'hii',
            'attachment': 'None',
            'attachment_file_name': 'None',
            'chat_type': 'chat_message',
            'agent_profile_pic_source': '',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/save-cobrowsing-chat/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetCobrowsingChatHistoryAPI(self):
        logger.info('Testing test_GetCobrowsingChatHistoryAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())
        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/get-cobrowsing-chat-history/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_UpdateSupportDocumentDetailAPI(self):
        logger.info('Testing test_UpdateSupportDocumentDetailAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        file_path = '/secured_files/EasyAssistApp/tests/file_name.png'

        support_document_obj = \
            SupportDocument.objects.create(file_name='file_name.png',
                                           file_path=file_path, file_type='png',
                                           file_access_management_key=uuid.uuid4(),
                                           agent=cobrowse_agent)

        json_string = \
            json.dumps({str(support_document_obj.pk): {'is_usable': False,
                                                       'file_name': 'updated_file.png'}})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/sales-ai/update-support-document-detail/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_DeleteSupportDocumentAPI(self):
        logger.info('Testing test_DeleteSupportDocumentAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        file_path = '/secured_files/EasyAssistApp/tests/file_name.png'

        support_document_obj = \
            SupportDocument.objects.create(file_name='file_name.png',
                                           file_path=file_path, file_type='png',
                                           file_access_management_key=uuid.uuid4(),
                                           agent=cobrowse_agent)

        json_string = \
            json.dumps({'support_document_id': str(support_document_obj.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/sales-ai/delete-support-document/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_SetNotificationForAgentAPI(self):
        logger.info('Testing test_SetNotificationForAgentAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/set-notification-for-agent/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.pk),
                        'agent_id_list': [str(cobrowse_agent.pk)]})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/set-notification-for-agent/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_AddNewObfuscatedFieldAPI(self):
        logger.info('Testing test_AddNewObfuscatedFieldAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        json_string = json.dumps({'field_key': 'id',
                                  'field_value': 'id_value',
                                  'masking_type': 'partial'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/add-new-obfuscated-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({'field_key': 'id',
                                  'field_value': 'id_value',
                                  'masking_type': 'partial'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/add-new-obfuscated-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({'field_key': 'id',
                                  'field_value': 'id_value',
                                  'masking_type': 'partial'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/add-new-obfuscated-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_EditObfuscatedFieldAPI(self):
        logger.info('Testing test_EditObfuscatedFieldAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        cobrowse_obfuscated_field = \
            CobrowseObfuscatedField.objects.create(key='id',
                                                   value='id_value', masking_type='partial')

        json_string = json.dumps({
            'field_key': 'id2',
            'field_value': 'id2_value',
            'masking_type': 'partial',
            'field_id': str(cobrowse_obfuscated_field.pk),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/edit-obfuscated-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            'field_key': 'id2',
            'field_value': 'id2_value',
            'masking_type': 'partial',
            'field_id': '100',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/edit-obfuscated-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        cobrowse_obfuscated_field = \
            CobrowseObfuscatedField.objects.create(key='id',
                                                   value='id_value', masking_type='partial')

        json_string = json.dumps({
            'field_key': 'id2',
            'field_value': 'id2_value',
            'masking_type': 'partial',
            'field_id': str(cobrowse_obfuscated_field.pk),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/edit-obfuscated-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_DeleteObfuscatedFieldsAPI(self):
        logger.info('Testing test_DeleteObfuscatedFieldsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        cobrowse_obfuscated_field = \
            CobrowseObfuscatedField.objects.create(key='id',
                                                   value='id_value', masking_type='partial')

        json_string = \
            json.dumps({'obfuscated_field_id_list': [
                       str(cobrowse_obfuscated_field.pk)]})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/delete-obfuscated-fields/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        cobrowse_obfuscated_field = \
            CobrowseObfuscatedField.objects.create(key='id',
                                                   value='id_value', masking_type='partial')

        json_string = \
            json.dumps({'obfuscated_field_id_list': [
                       str(cobrowse_obfuscated_field.pk)]})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/delete-obfuscated-fields/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_AddNewLeadHTMLFieldAPI(self):
        logger.info('Testing test_AddNewLeadHTMLFieldAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        json_string = json.dumps({
            'tag': 'input',
            'tag_label': 'First Name',
            'tag_key': 'id',
            'tag_value': 'fname',
            'tag_type': 'primary',
            'unique_identifier': True,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/add-new-search-tag-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            'tag': 'input',
            'tag_label': 'First Name',
            'tag_key': 'id',
            'tag_value': 'fname',
            'tag_type': 'primary',
            'unique_identifier': False,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/add-new-search-tag-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'tag': 'input',
            'tag_label': 'First Name',
            'tag_key': 'id',
            'tag_value': 'fname',
            'tag_type': 'primary',
            'unique_identifier': True,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/add-new-search-tag-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_EditLeadHTMLFieldAPI(self):
        logger.info('Testing test_EditLeadHTMLFieldAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        cobrowse_lead_html_field = \
            CobrowseLeadHTMLField.objects.create(tag='input',
                                                 tag_label='First Name', tag_key='id', tag_value='fname', tag_type='primary')

        json_string = json.dumps({
            'tag': 'input',
            'tag_label': 'Last Name',
            'tag_key': 'id',
            'tag_value': 'lname',
            'tag_type': 'primary',
            'field_id': str(cobrowse_lead_html_field.pk),
            'unique_identifier': True,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/edit-search-tag-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            'tag': 'input',
            'tag_label': 'Last Name',
            'tag_key': 'id',
            'tag_value': 'lname',
            'tag_type': 'primary',
            'field_id': '100',
            'unique_identifier': False,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/edit-search-tag-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'tag': 'input',
            'tag_label': 'Last Name',
            'tag_key': 'id',
            'tag_value': 'lname',
            'tag_type': 'primary',
            'field_id': '100',
            'unique_identifier': True,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/edit-search-tag-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_DeleteLeadHTMLFieldsAPI(self):
        logger.info('Testing test_DeleteLeadHTMLFieldsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        cobrowse_lead_html_field = \
            CobrowseLeadHTMLField.objects.create(tag='input',
                                                 tag_label='First Name', tag_key='id', tag_value='fname', tag_type='primary')

        json_string = \
            json.dumps({'search_tag_field_id_list': [
                       str(cobrowse_lead_html_field.pk)]})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/delete-search-tag-fields/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        cobrowse_lead_html_field = \
            CobrowseLeadHTMLField.objects.create(tag='input',
                                                 tag_label='First Name', tag_key='id', tag_value='fname', tag_type='primary')

        json_string = \
            json.dumps({'search_tag_field_id_list': [
                       str(cobrowse_lead_html_field.pk)]})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/delete-search-tag-fields/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_AddNewAutoFetchFieldAPI(self):
        logger.info('Testing test_AddNewAutoFetchFieldAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        json_string = json.dumps({
            'fetch_field_key': 'id',
            'fetch_field_value': 'fname',
            'modal_field_key': 'id',
            'modal_field_value': 'modal_id',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/add-new-auto-fetch-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            'fetch_field_key': 'id',
            'fetch_field_value': 'fname',
            'modal_field_key': 'id',
            'modal_field_value': 'modal_id',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/add-new-auto-fetch-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'fetch_field_key': 'id',
            'fetch_field_value': 'fname',
            'modal_field_key': 'id',
            'modal_field_value': 'modal_id',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/add-new-auto-fetch-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_EditAutoFetchFieldAPI(self):
        logger.info('Testing test_EditAutoFetchFieldAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        cobrowse_auto_fetch_field = \
            CobrowseAutoFetchField.objects.create(fetch_field_key='id',
                                                  fetch_field_value='fname', modal_field_key='id',
                                                  modal_field_value='modal_id')

        json_string = json.dumps({
            'fetch_field_key': 'id',
            'fetch_field_value': 'fname',
            'modal_field_key': 'id',
            'modal_field_value': 'modal_id',
            'field_id': str(cobrowse_auto_fetch_field.pk),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/edit-auto-fetch-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            'fetch_field_key': 'id',
            'fetch_field_value': 'fname',
            'modal_field_key': 'id',
            'modal_field_value': 'modal_id',
            'field_id': '100',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/edit-auto-fetch-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'fetch_field_key': 'id',
            'fetch_field_value': 'fname',
            'modal_field_key': 'id',
            'modal_field_value': 'modal_id',
            'field_id': '100',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/edit-auto-fetch-field/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_DeleteAutoFetchFieldsAPI(self):
        logger.info('Testing test_DeleteAutoFetchFieldsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        cobrowse_auto_fetch_field = \
            CobrowseAutoFetchField.objects.create(fetch_field_key='id',
                                                  fetch_field_value='fname', modal_field_key='id',
                                                  modal_field_value='modal_id')

        json_string = \
            json.dumps({'auto_fetch_field_id_list': [
                       str(cobrowse_auto_fetch_field.pk)]})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/delete-auto-fetch-fields/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        cobrowse_auto_fetch_field = \
            CobrowseAutoFetchField.objects.create(fetch_field_key='id',
                                                  fetch_field_value='fname', modal_field_key='id',
                                                  modal_field_value='modal_id')

        json_string = \
            json.dumps({'auto_fetch_field_id_list': [
                       str(cobrowse_auto_fetch_field.pk)]})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/delete-auto-fetch-fields/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_SaveCobrowseAgentAdvancedDetailsAPI(self):
        logger.info('Testing test_SaveCobrowseAgentAdvancedDetailsAPI...', extra={
                    'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        language_obj = LanguageSupport.objects.create(title='Hindi')
        product_category_obj = \
            ProductCategory.objects.create(title='Product 1')

        json_string = \
            json.dumps({'selected_language_pk_list': [str(language_obj.pk)],
                        'selected_product_category_list': [str(product_category_obj.pk)]})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowse-agent-advanced-details/', json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetLeadStatusAPI(self):
        logger.info('Testing test_GetLeadStatusAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/get-lead-status/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetAllActiveLeadStatusAPI(self):
        logger.info('Testing test_GetAllActiveLeadStatusAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        CobrowseIO.objects.create(full_name='Test',
                                  mobile_number='9191919191', share_client_session=False,
                                  agent=cobrowse_agent,
                                  access_token=cobrowse_agent.get_access_token_obj())

        json_string = json.dumps({'page_number': 1})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/get-all-active-lead-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_RequestCobrowsingMeetingAPI(self):
        logger.info('Testing test_RequestCobrowsingMeetingAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/request-assist-meeting/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_CheckMeetingStatusAPI(self):
        logger.info('Testing test_CheckMeetingStatusAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        cobrowse_io_obj.allow_agent_meeting = None
        cobrowse_io_obj.save()

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/check-meeting-status/', json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        cobrowse_io_obj.allow_agent_meeting = 'true'
        cobrowse_io_obj.save()

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/check-meeting-status/', json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_io_obj.allow_agent_meeting = 'false'
        cobrowse_io_obj.save()

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/check-meeting-status/', json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GenerateDropLinkAPI(self):
        logger.info('Testing test_GenerateDropLinkAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        json_string = json.dumps({
            'client_page_link': 'https://abcd.example.com',
            'customer_name': 'Test',
            'customer_mobile_number': '9191919191',
            'customer_email_id': 'test@example.com',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/generate-drop-link/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            'client_page_link': 'abcd',
            'customer_name': 'Test',
            'customer_mobile_number': '9191919191',
            'customer_email_id': 'test@example.com',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/generate-drop-link/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

    def test_AgentOnlineAuditTrailAPI(self):
        logger.info('Testing test_AgentOnlineAuditTrailAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        json_string = json.dumps({'agent_username': 'testeasyassist',
                                  'date': '2021-05-19'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent-online-audit-trail/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_VerifyMaskingPIIDataOTPAPI(self):
        logger.info('Testing test_VerifyMaskingPIIDataOTPAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        pii_data_obj = \
            CobrowsePIIDataOTP.objects.create(agent=cobrowse_agent)

        otp = '123456'

        pii_data_obj.otp = otp
        pii_data_obj.save()

        json_string = json.dumps({'otp': '123457'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/verify-masking-pii-data-otp/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        json_string = json.dumps({'otp': '123456'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/verify-masking-pii-data-otp/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        pii_data_obj.delete()
        json_string = json.dumps({'otp': '123456'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/verify-masking-pii-data-otp/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 401)

    def test_EnableMaskingPIIDataAPI(self):
        logger.info('Testing test_EnableMaskingPIIDataAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        json_string = json.dumps({})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/enable-masking-pii-data/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], '200')

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/enable-masking-pii-data/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], '401')

    def test_AddNewCobrowseFormAPI(self):
        logger.info('Testing test_AddNewCobrowseFormAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        json_string = json.dumps({
            "form_name": "Form",
            "product_categories": "None",
            "form_data": [
                {
                    "category_name": "Category 1",
                    "questions": [
                        {
                            "question_type": "text",
                            "question_label": "Your name",
                            "question_choices": [],
                            "is_mandatory": True
                        },
                        {
                            "question_type": "number",
                            "question_label": "Your Age",
                            "question_choices": [],
                            "is_mandatory": True
                        },
                        {
                            "question_type": "checkbox",
                            "question_label": "Games you like",
                            "question_choices": [
                                "Cricket",
                                "Chess"
                            ],
                            "is_mandatory": False
                        },
                        {
                            "question_type": "dropdown",
                            "question_label": "Country",
                            "question_choices": [
                                "India",
                                "China",
                                "Nepal"
                            ],
                            "is_mandatory": False
                        }
                    ]
                }
            ]
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/create-cobrowse-form/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_SaveCobrowseFormAPI(self):
        logger.info('Testing test_SaveCobrowseFormAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_form_obj = CobrowseVideoConferencingForm.objects.create(
            form_name="Form")

        cobrowse_form_category_obj = CobrowseVideoconferencingFormCategory.objects.create(
            form=cobrowse_form_obj, title="Category 1")

        CobrowseVideoConferencingFormElement.objects.create(
            form_category=cobrowse_form_category_obj,
            element_type="text",
            element_label="Name",
            element_choices=json.dumps([]),
            is_mandatory=True)

        json_string = json.dumps({
            "form_id": str(cobrowse_form_obj.pk),
            "form_name": "New Form",
            "form_data": [
                {
                    "category_id": str(cobrowse_form_category_obj.pk),
                    "category_name": "Section 1",
                    "questions": [
                        {
                            "question_id": "2",
                            "question_type": "text",
                            "question_label": "Your Name",
                            "question_choices": [],
                            "is_mandatory": False
                        }
                    ]
                }
            ]
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/save-cobrowse-form/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_DeleteVideoConferencingFormAPI(self):
        logger.info('Testing test_DeleteVideoConferencingFormAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_form_obj = CobrowseVideoConferencingForm.objects.create(
            form_name="Form")

        cobrowse_form_category_obj = CobrowseVideoconferencingFormCategory.objects.create(
            form=cobrowse_form_obj, title="Category 1")

        CobrowseVideoConferencingFormElement.objects.create(
            form_category=cobrowse_form_category_obj,
            element_type="text",
            element_label="Name",
            element_choices=json.dumps([]),
            is_mandatory=True)

        json_string = json.dumps({
            "form_id": str(cobrowse_form_obj.pk),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/delete-video-conferencing-form/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_form_obj = CobrowseVideoConferencingForm.objects.filter(
            pk=cobrowse_form_obj.pk).first()
        self.assertEqual(cobrowse_form_obj.is_deleted, True)

    def test_DeleteCobrowseFormCategoryAPI(self):
        logger.info('Testing test_DeleteCobrowseFormCategoryAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_form_obj = CobrowseVideoConferencingForm.objects.create(
            form_name="Form")

        cobrowse_form_category_obj = CobrowseVideoconferencingFormCategory.objects.create(
            form=cobrowse_form_obj, title="Category 1")

        CobrowseVideoConferencingFormElement.objects.create(
            form_category=cobrowse_form_category_obj,
            element_type="text",
            element_label="Name",
            element_choices=json.dumps([]),
            is_mandatory=True)

        json_string = json.dumps({
            "category_id": str(cobrowse_form_category_obj.pk),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/delete-cobrowse-form-category/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_form_category_obj = CobrowseVideoconferencingFormCategory.objects.filter(
            pk=cobrowse_form_category_obj.pk).first()

        self.assertEqual(cobrowse_form_category_obj.is_deleted, True)

    def test_DeleteCobrowseFormCategoryQuestionAPI(self):
        logger.info('Testing test_DeleteCobrowseFormCategoryQuestionAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_form_obj = CobrowseVideoConferencingForm.objects.create(
            form_name="Form")

        cobrowse_form_category_obj = CobrowseVideoconferencingFormCategory.objects.create(
            form=cobrowse_form_obj, title="Category 1")

        cobrowse_form_element_obj = CobrowseVideoConferencingFormElement.objects.create(
            form_category=cobrowse_form_category_obj,
            element_type="text",
            element_label="Name",
            element_choices=json.dumps([]),
            is_mandatory=True)

        json_string = json.dumps({
            "question_id": str(cobrowse_form_element_obj.pk),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/delete-cobrowse-form-category-question/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_form_element_obj = CobrowseVideoConferencingFormElement.objects.filter(
            pk=cobrowse_form_element_obj.pk).first()

        self.assertEqual(cobrowse_form_element_obj.is_deleted, True)

    def test_ChangeCobrowseFormAgentAPI(self):
        logger.info('Testing test_ChangeCobrowseFormAgentAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        support_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist')

        cobrowse_form_obj = CobrowseVideoConferencingForm.objects.create(
            form_name="Form")

        cobrowse_form_category_obj = CobrowseVideoconferencingFormCategory.objects.create(
            form=cobrowse_form_obj, title="Category 1")

        CobrowseVideoConferencingFormElement.objects.create(
            form_category=cobrowse_form_category_obj,
            element_type="text",
            element_label="Name",
            element_choices=json.dumps([]),
            is_mandatory=True)

        json_string = json.dumps({
            "form_id": str(cobrowse_form_obj.pk),
            "selected_agents": [str(support_agent.pk)],
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/change-cobrowse-form-agent/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_UploadChatBubbleIconAPI(self):
        logger.info('Testing test_UploadChatBubbleIconAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()
        json_string = {
            "filename": "Chat2.png",
            "base64_file": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII=",
        }
        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/upload-chat-bubble-icon/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = {
            "filename": "Chat2.png",
            "base64_file": "",
        }
        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/upload-chat-bubble-icon/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        json_string = {
            "filename": "",
            "base64_file": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII=",
        }
        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/upload-chat-bubble-icon/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        json_string = {
            "filename": "Chat2.jpeg",
            "base64_file": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII=",
        }
        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/upload-chat-bubble-icon/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 300)

    def test_UploadAgentPictureAPI(self):
        logger.info('Testing test_UploadAgentPictureAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        cobrowse_agent.role = ''
        cobrowse_agent.save()
        json_string = {
            "filename": "Chat2.png",
            "base64_file": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII=",
        }
        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/upload-agent-profile-picture/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()
        json_string = {
            "filename": "Chat2.png",
            "base64_file": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII=",
        }
        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/upload-agent-profile-picture/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = {
            "filename": "",
            "base64_file": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII=",
        }
        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/upload-agent-profile-picture/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        json_string = {
            "filename": "Chat2.png",
            "base64_file": "",
        }
        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/upload-agent-profile-picture/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = {
            "filename": "Chat2.jpegs",
            "base64_file": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII=",
        }
        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/upload-agent-profile-picture/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 300)

    def test_DeleteAgentProfilePictureAPI(self):
        logger.info('Testing test_DeleteAgentProfilePictureAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        json_string = json.dumps({})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        cobrowse_agent.role = ''
        cobrowse_agent.save()

        request = \
            client.post('/easy-assist/sales-ai/delete-agent-profile-picture/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        request = \
            client.post('/easy-assist/sales-ai/delete-agent-profile-picture/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_MaliciousProfilePictureAPI(self):
        logger.info('Testing test_MaliciousProfilePictureAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')
        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()
        json_string = {
            "filename": "Chat2.png",
            "base64_file": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII=",
        }
        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/check-malicious-agent-profile-picture/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = {
            "filename": "Chat2.jpeg",
            "base64_file": "vvvviVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII=",
        }
        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/check-malicious-agent-profile-picture/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_SaveCobrowseGeneralSettingsAPI(self):
        logger.info('Testing test_SaveCobrowseGeneralSettingsAPI...', extra={
                    'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        predefined_remarks_list = [{
            "remark": "Remark 1",
            "subremark": [{
                "remark": "Sub remark 1"
            }]
        }]

        json_string = json.dumps({
            'lead_conversion_checkbox_text': 'text',
            'enable_predefined_remarks': True,
            'enable_predefined_remarks_with_buttons': True,
            'enable_predefined_subremarks': True,
            'predefined_remarks_list': predefined_remarks_list,
            'predefined_remarks_optional': True,
            'predefined_remarks_with_buttons': 'Remarks1,Remark2',
            'enable_agent_connect_message': True,
            'agent_connect_message': 'hello',
            'enable_smart_agent_assignment': True,
            'reconnecting_window_timer_input': "10",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowse-general-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        predefined_remarks_list = [{
            "remark": "Remark 1",
            "subremark": [{
                "remark": "Sub remark 1"
            }]
        }]

        json_string = json.dumps({
            'lead_conversion_checkbox_text': 'text',
            'enable_predefined_remarks': False,
            'enable_predefined_remarks_with_buttons': False,
            'enable_predefined_subremarks': False,
            'predefined_remarks_list': predefined_remarks_list,
            'predefined_remarks_optional': False,
            'predefined_remarks_with_buttons': 'Remarks1,Remark2',
            'enable_agent_connect_message': False,
            'agent_connect_message': 'hello',
            'enable_smart_agent_assignment': False,
            'reconnecting_window_timer_input': "10",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowse-general-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        # Agent is trying to save

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()
        json_string = json.dumps({
            'lead_conversion_checkbox_text': 'text',
            'enable_predefined_remarks': True,
            'enable_predefined_remarks_with_buttons': True,
            'enable_predefined_subremarks': True,
            'predefined_remarks_list': predefined_remarks_list,
            'predefined_remarks_optional': True,
            'predefined_remarks_with_buttons': 'Remarks1,Remark2',
            'enable_agent_connect_message': True,
            'agent_connect_message': 'hello',
            'enable_smart_agent_assignment': True,
            'reconnecting_window_timer_input': "10",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowse-general-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()
        json_string = json.dumps({
            'lead_conversion_checkbox_text': 'text',
            'enable_predefined_remarks': False,
            'enable_predefined_remarks_with_buttons': False,
            'enable_predefined_subremarks': False,
            'predefined_remarks_list': predefined_remarks_list,
            'predefined_remarks_optional': False,
            'predefined_remarks_with_buttons': 'Remarks1,Remark2',
            'enable_agent_connect_message': False,
            'agent_connect_message': 'hello',
            'enable_smart_agent_assignment': False,
            'reconnecting_window_timer_input': "10",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowse-general-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_SaveCobrowseAdminSettingsAPI(self):
        logger.info('Testing test_SaveCobrowseAdminSettingsAPI...', extra={
                    'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        json_string = json.dumps({
            'masking_type': 'partial',
            'allow_screen_sharing_cobrowse': True,
            'allow_agent_to_screen_record_customer_cobrowsing': True,
            'enable_manual_switching': True,
            'enable_low_bandwidth_cobrowsing': True,
            'low_bandwidth_cobrowsing_threshold': 1024,
            'archive_on_common_inactivity_threshold': 30,
            'drop_link_expiry_time': 30,
            'restricted_urls': 'text',
            'urls_consider_lead_converted': '',

        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowse-admin-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            'masking_type': 'partial',
            'allow_screen_sharing_cobrowse': False,
            'allow_agent_to_screen_record_customer_cobrowsing': False,
            'enable_manual_switching': False,
            'enable_low_bandwidth_cobrowsing': False,
            'low_bandwidth_cobrowsing_threshold': 1024,
            'archive_on_common_inactivity_threshold': 30,
            'drop_link_expiry_time': 30,
            'restricted_urls': 'text',
            'urls_consider_lead_converted': '',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowse-admin-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'masking_type': 'partial',
            'allow_screen_sharing_cobrowse': True,
            'allow_agent_to_screen_record_customer_cobrowsing': True,
            'enable_manual_switching': True,
            'enable_low_bandwidth_cobrowsing': True,
            'low_bandwidth_cobrowsing_threshold': 1024,
            'archive_on_common_inactivity_threshold': 30,
            'drop_link_expiry_time': 30,
            'restricted_urls': 'text',
            'urls_consider_lead_converted': '',

        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowse-admin-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()
        json_string = json.dumps({
            'masking_type': 'partial',
            'allow_screen_sharing_cobrowse': False,
            'allow_agent_to_screen_record_customer_cobrowsing': False,
            'enable_manual_switching': False,
            'enable_low_bandwidth_cobrowsing': False,
            'low_bandwidth_cobrowsing_threshold': 1024,
            'archive_on_common_inactivity_threshold': 30,
            'drop_link_expiry_time': 30,
            'restricted_urls': 'text',
            'urls_consider_lead_converted': '',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowse-admin-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_SaveCobrowseAgentSettingsAPI(self):
        logger.info('Testing test_SaveCobrowseAgentSettingsAPI...', extra={
                    'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        json_string = json.dumps({
            'enable_screenshot_agent': True,
            'enable_invite_agent_in_cobrowsing': True,
            'enable_session_transfer_in_cobrowsing': True,
            'transfer_request_archive_time': 120,
            'enable_edit_access': True,
            'allow_video_calling_cobrowsing': True,
            'customer_initiate_video_call': False,
            'customer_initiate_voice_call': False,
            'customer_initiate_video_call_as_pip': False,
            'enable_voip_calling': True,
            'enable_voip_with_video_calling': True,
            'enable_auto_voip_calling_for_first_time': True,
            'enable_auto_voip_with_video_calling_for_first_time': True,
            'voip_calling_text': 'hello',
            'voip_with_video_calling_text': 'text',
            'allow_screen_recording': True,
            'recording_expires_in_days': 15,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowse-agent-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            'enable_screenshot_agent': True,
            'enable_invite_agent_in_cobrowsing': False,
            'enable_session_transfer_in_cobrowsing': False,
            'transfer_request_archive_time': 70,
            'enable_edit_access': True,
            'allow_video_calling_cobrowsing': False,
            'customer_initiate_video_call': True,
            'customer_initiate_voice_call': True,
            'customer_initiate_video_call_as_pip': True,
            'enable_voip_calling': False,
            'enable_voip_with_video_calling': False,
            'enable_auto_voip_calling_for_first_time': False,
            'enable_auto_voip_with_video_calling_for_first_time': False,
            'voip_calling_text': 'hello',
            'voip_with_video_calling_text': 'text',
            'allow_screen_recording': False,
            'recording_expires_in_days': 15,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowse-agent-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'enable_screenshot_agent': True,
            'enable_invite_agent_in_cobrowsing': True,
            'enable_session_transfer_in_cobrowsing': True,
            'transfer_request_archive_time': 120,
            'enable_edit_access': True,
            'allow_video_calling_cobrowsing': True,
            'customer_initiate_video_call': False,
            'customer_initiate_voice_call': False,
            'customer_initiate_video_call_as_pip': False,
            'enable_voip_calling': True,
            'enable_voip_with_video_calling': True,
            'enable_auto_voip_calling_for_first_time': True,
            'enable_auto_voip_with_video_calling_for_first_time': True,
            'voip_calling_text': 'hello',
            'voip_with_video_calling_text': 'text',
            'allow_screen_recording': True,
            'recording_expires_in_days': 15,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowse-agent-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'enable_screenshot_agent': True,
            'enable_invite_agent_in_cobrowsing': True,
            'enable_session_transfer_in_cobrowsing': False,
            'transfer_request_archive_time': 120,
            'enable_edit_access': True,
            'allow_video_calling_cobrowsing': False,
            'customer_initiate_video_call': True,
            'customer_initiate_voice_call': True,
            'customer_initiate_video_call_as_pip': True,
            'enable_voip_calling': False,
            'enable_voip_with_video_calling': False,
            'enable_auto_voip_calling_for_first_time': False,
            'enable_auto_voip_with_video_calling_for_first_time': False,
            'voip_calling_text': 'hello',
            'voip_with_video_calling_text': 'text',
            'allow_screen_recording': False,
            'recording_expires_in_days': 15,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowse-agent-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_SaveCobrowsingMetaCustomerDetailsCobrowsingAPI(self):
        logger.info('Testing test_SaveCobrowsingMetaCustomerDetailsCobrowsingAPI...', extra={
                    'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        json_string = json.dumps({
            'masked_field_warning_text': 'hello',
            'enable_masked_field_warning': True,
            'assistant_message': 'text',
            'show_verification_code_modal': True,
            'enable_verification_code_popup': True
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowsing-meta-details/cobrowsing/customer/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            'masked_field_warning_text': 'hello',
            'enable_masked_field_warning': False,
            'assistant_message': 'text',
            'show_verification_code_modal': False,
            'enable_verification_code_popup': False
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowsing-meta-details/cobrowsing/customer/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'masked_field_warning_text': 'hello',
            'enable_masked_field_warning': True,
            'assistant_message': 'text',
            'show_verification_code_modal': True,
            'enable_verification_code_popup': True
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowsing-meta-details/cobrowsing/customer/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'masked_field_warning_text': 'hello',
            'enable_masked_field_warning': False,
            'assistant_message': 'text',
            'show_verification_code_modal': False,
            'enable_verification_code_popup': False
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowsing-meta-details/cobrowsing/customer/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_SaveCobrowsingMetaCustomerDetailsGeneralAPI(self):
        logger.info('Testing test_SaveCobrowsingMetaCustomerDetailsGeneralAPI...', extra={
                    'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        json_string = json.dumps({
            'easyassit_font_family': 'Silka',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowsing-meta-details/general/customer/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'easyassit_font_family': 'Silka',
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-cobrowsing-meta-details/general/customer/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_SaveVideoAdminSettingsAPI(self):
        logger.info('Testing test_SaveVideoAdminSettingsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')
        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        json_string = json.dumps({
            'proxy_server': '',
            'meeting_url': '',
            'meeting_default_password': 'hello@123',
            'meet_background_color': 'black',
            'allow_meeting_feedback': False,
            'allow_meeting_end_time': False,
            'meeting_end_time': 60,
            'allow_video_meeting_only': False,
            'enable_no_agent_connects_toast_meeting': True,
            'no_agent_connects_meeting_toast_threshold': 1,
            'no_agent_connects_meeting_toast_text': '',
            'allow_generate_meeting': True,
            'enable_cognomeet': True,
            'enable_meeting_recording': True
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/save-video-admin-settings/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'proxy_server': '',
            'meeting_url': '',
            'meeting_default_password': 'hello@123',
            'meet_background_color': 'black',
            'allow_meeting_feedback': False,
            'allow_meeting_end_time': False,
            'meeting_end_time': 60,
            'allow_video_meeting_only': False,
            'enable_no_agent_connects_toast_meeting': True,
            'no_agent_connects_meeting_toast_threshold': 1,
            'no_agent_connects_meeting_toast_text': '',
            'allow_generate_meeting': True,
            'enable_cognomeet': True,
            'enable_meeting_recording': False
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/save-video-admin-settings/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_SaveVideoAgentSettingsAPI(self):
        logger.info('Testing test_SaveVideoAgentSettingsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        json_string = json.dumps({
            'proxy_server': '',
            'meeting_url': '',
            'meeting_default_password': '1234',
            'show_cobrowsing_meeting_lobby': False,
            'meet_background_color': 'black',
            'allow_meeting_feedback': False,
            'allow_meeting_end_time': False,
            'meeting_end_time': 60,
            'allow_capture_screenshots': True,
            'enable_invite_agent_in_meeting': True,
            'allow_video_meeting_only': False,
            'enable_no_agent_connects_toast_meeting': True,
            'no_agent_connects_meeting_toast_threshold': 1,
            'no_agent_connects_meeting_toast_text': '',
            'enable_screen_sharing': True
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-video-agent-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'proxy_server': '',
            'meeting_url': '',
            'meeting_default_password': '1234',
            'show_cobrowsing_meeting_lobby': False,
            'meet_background_color': 'black',
            'allow_meeting_feedback': False,
            'allow_meeting_end_time': False,
            'meeting_end_time': 60,
            'allow_capture_screenshots': True,
            'enable_invite_agent_in_meeting': True,
            'allow_video_meeting_only': False,
            'enable_no_agent_connects_toast_meeting': True,
            'no_agent_connects_meeting_toast_threshold': 1,
            'no_agent_connects_meeting_toast_text': '',
            'enable_screen_sharing': True
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-video-agent-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_SaveGeneralAgentSettingsAPI(self):
        logger.info('Testing test_SaveGeneralAgentSettingsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        json_string = json.dumps({
            'enable_chat_functionality': True,
            'enable_chat_bubble': True,
            'floating_button_position': 'left',
            'share_document_from_livechat': True,
            'allow_support_documents': True,
            'allow_only_support_documents': True,
            'enable_auto_offline_agent': True,
            'display_agent_profile': True,
            'enable_preview_functionality': True,
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-general-agent-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'enable_chat_functionality': True,
            'enable_chat_bubble': True,
            'floating_button_position': 'left',
            'share_document_from_livechat': True,
            'allow_support_documents': True,
            'allow_only_support_documents': True,
            'enable_auto_offline_agent': True,
            'display_agent_profile': True,
            'enable_preview_functionality': True,
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-general-agent-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_SaveGeneralAdminSettingsAPI(self):
        logger.info('Testing test_SaveGeneralAdminSettingsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        json_string = json.dumps({
            'enable_inbound': True,
            'floating_button_bg_color': 'd6d6d6',
            'enable_greeting_bubble': True,
            'greeting_bubble_auto_popup_timer': 3,
            'greeting_bubble_text': 'Test',
            'enable_lead_status': True,
            'maximum_active_leads': True,
            'maximum_active_leads_threshold': 30,
            'enable_request_in_queue': True,
            'enable_auto_assign_unattended_lead': False,
            'auto_assign_unattended_lead_timer': "100",
            'auto_assign_unattended_lead_message': "",
            'enable_auto_assign_to_one_agent': True,
            'auto_assigned_unattended_lead_archive_timer': '10',
            'auto_assign_lead_end_session_message': "Thanks",
            'show_floating_easyassist_button': True,
            'show_easyassist_connect_agent_icon': False,
            'show_only_if_agent_available': False,
            'floating_button_left_right_position': 0,
            'assign_agent_under_same_supervisor': False,
            'auto_assign_unattended_lead_transfer_count': '2',
            'allow_language_support': False,
            'supported_language_list': [],
            'disable_connect_button_if_agent_unavailable': True,
            'enable_non_working_hours_modal_popup': True,
            'message_if_agent_unavailable': '',
            'message_on_non_working_hours': '',
            'enable_followup_leads_tab': True,
            'choose_product_category': False,
            'product_category_list': False,
            'message_on_choose_product_category_modal': '',
            'connect_message': '',
            'no_agent_connects_toast': False,
            'no_agent_connects_toast_threshold': 10,
            'no_agent_connects_toast_text': '',
            'no_agent_connect_timer_reset_message': "Agent are busy",
            'no_agent_connect_timer_reset_count': '2',
            'archive_on_unassigned_time_threshold': '10',
            'archive_message_on_unassigned_time_threshold': '',
            'field_stuck_event_handler': True,
            'field_recursive_stuck_event_check': True,
            'inactivity_auto_popup_number': 5,
            'field_stuck_timer': 30,
            'allow_popup_on_browser_leave': True,
            'enable_recursive_browser_leave_popup': True,
            'exit_intent_popup_count': '2',
            'lead_generation': False,
            'enable_tag_based_assignment_for_outbound': False,
            'show_floating_button_after_lead_search': False,
            'allow_agent_to_customer_cobrowsing': False,
            'allow_agent_to_screen_record_customer_cobrowsing': False,
            'allow_agent_to_audio_record_customer_cobrowsing': False,
            'enable_url_based_inactivity_popup': False,
            'enable_url_based_exit_intent_popup': False,
            'allow_connect_with_virtual_agent_code': False,
            'connect_with_virtual_agent_code_mandatory': True,
            'enable_proxy_cobrowsing': True,
            'proxy_link_expire_time': "90"
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-general-admin-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            'enable_inbound': True,
            'floating_button_bg_color': 'd6d6d6',
            'enable_greeting_bubble': True,
            'greeting_bubble_auto_popup_timer': 3,
            'greeting_bubble_text': 'Test',
            'enable_lead_status': True,
            'maximum_active_leads': True,
            'maximum_active_leads_threshold': 30,
            'enable_request_in_queue': False,
            'enable_auto_assign_unattended_lead': True,
            'auto_assign_unattended_lead_timer': "100",
            'auto_assign_unattended_lead_message': "",
            'enable_auto_assign_to_one_agent': True,
            'auto_assigned_unattended_lead_archive_timer': '10',
            'auto_assign_lead_end_session_message': "Thanks",
            'show_floating_easyassist_button': True,
            'show_easyassist_connect_agent_icon': False,
            'show_only_if_agent_available': False,
            'floating_button_left_right_position': 0,
            'assign_agent_under_same_supervisor': False,
            'auto_assign_unattended_lead_transfer_count': '2',
            'allow_language_support': False,
            'supported_language_list': [],
            'disable_connect_button_if_agent_unavailable': True,
            'enable_non_working_hours_modal_popup': True,
            'message_if_agent_unavailable': '',
            'message_on_non_working_hours': '',
            'enable_followup_leads_tab': True,
            'choose_product_category': False,
            'product_category_list': False,
            'message_on_choose_product_category_modal': '',
            'connect_message': '',
            'no_agent_connects_toast': False,
            'no_agent_connects_toast_threshold': 10,
            'no_agent_connects_toast_text': '',
            'no_agent_connect_timer_reset_message': "Agent are busy",
            'no_agent_connect_timer_reset_count': '2',
            'archive_on_unassigned_time_threshold': '10',
            'archive_message_on_unassigned_time_threshold': '',
            'field_stuck_event_handler': True,
            'field_recursive_stuck_event_check': True,
            'inactivity_auto_popup_number': 5,
            'field_stuck_timer': 30,
            'allow_popup_on_browser_leave': True,
            'enable_recursive_browser_leave_popup': True,
            'exit_intent_popup_count': '2',
            'lead_generation': False,
            'enable_tag_based_assignment_for_outbound': False,
            'show_floating_button_after_lead_search': False,
            'allow_agent_to_customer_cobrowsing': False,
            'allow_agent_to_screen_record_customer_cobrowsing': False,
            'allow_agent_to_audio_record_customer_cobrowsing': False,
            'enable_url_based_inactivity_popup': True,
            'enable_url_based_exit_intent_popup': True,
            'allow_connect_with_virtual_agent_code': False,
            'connect_with_virtual_agent_code_mandatory': True,
            'enable_proxy_cobrowsing': False,
            'proxy_link_expire_time': '90'
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-general-admin-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_SaveGeneralConsoleSettingsAPI(self):
        logger.info('Testing test_SaveGeneralConsoleSettingsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        cobrowse_agent.role = 'admin'
        cobrowse_agent.save()

        json_string = json.dumps({
            "cobrowsing_console_theme_color": {'hex': '#d60000'},
            "go_live_date": '2020-11-21',
            "whitelisted_domain": '',
            "password_prefix": 'password_prefix',
            "deploy_chatbot_flag": False,
            "deploy_chatbot_url": '',
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-general-console-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = 'agent'
        cobrowse_agent.save()

        json_string = json.dumps({
            "cobrowsing_console_theme_color": {'hex': '#d60000'},
            "go_live_date": '2020-11-21',
            "whitelisted_domain": '',
            "password_prefix": 'password_prefix',
            "deploy_chatbot_flag": False,
            "deploy_chatbot_url": '',
        })
        
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/save-general-console-settings/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_ResetChatBubbleIconAPI(self):
        logger.info('Testing test_ResetChatBubbleIconAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        json_string = json.dumps({})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/reset-chat-bubble-icon/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = "admin_ally"
        cobrowse_agent.save()

        json_string = json.dumps({})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/sales-ai/reset-chat-bubble-icon/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_UpdateCustomerMeetingRequestAPI(self):
        logger.info('Testing test_UpdateCustomerMeetingRequestAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='support_testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='support_testeasyassist')

        cobrowse_agent.role = "agent"
        cobrowse_agent.save()

        cobrowseio = CobrowseIO.objects.create()
        json_string = json.dumps(
            {'id': str(cobrowseio.session_id), 'status': 'false'})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/update-customer-meeting-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['meeting_allowed'], 'false')

        json_string = json.dumps(
            {'id': str(cobrowseio.session_id), 'status': 'true'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/update-customer-meeting-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['meeting_allowed'], 'true')

    def test_CustomerInitiateMeetingStatusAPI(self):
        logger.info('Testing test_CustomerInitiateMeetingStatusAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        cobrowseio = CobrowseIO.objects.create()

        cobrowseio.access_token = cobrowse_agent.get_access_token_obj()
        cobrowseio.agent = cobrowse_agent
        cobrowseio.save()

        custom_encrypt_obj = CustomEncrypt()

        json_string = json.dumps({'session_id': str(cobrowseio.session_id)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/check-customer-initiate-meeting-status/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)
        self.assertEqual(response["is_meeting_allowed"], False)

        cobrowseio.allow_customer_meeting = 'true'
        cobrowseio.save()

        request = \
            client.post('/easy-assist/agent/check-customer-initiate-meeting-status/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response["is_meeting_allowed"], True)

        cobrowseio.allow_customer_meeting = 'false'
        cobrowseio.save()

        request = \
            client.post('/easy-assist/agent/check-customer-initiate-meeting-status/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response["is_meeting_allowed"], False)

    def test_TransferCobrowsingSessionAPI(self):
        logger.info('Testing test_TransferCobrowsingSessionAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.is_active = True
        cobrowse_agent.save()

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191',
                                                    access_token=cobrowse_agent.get_access_token_obj(),
                                                    allow_agent_cobrowse="true")

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/transfer-cobrowsing-session/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191',
                                                    access_token=cobrowse_agent.get_access_token_obj(),
                                                    allow_agent_cobrowse="false")

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/transfer-cobrowsing-session/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

    def test_UpdateTransferCobrowsingSessionLogsAPI(self):
        logger.info('Testing test_UpdateTransferCobrowsingSessionLogsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.is_active = True
        cobrowse_agent.save()

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191',
                                                    access_token=cobrowse_agent.get_access_token_obj(),
                                                    allow_agent_cobrowse="true")
        CobrowseIOTransferredAgentsLogs.objects.create(
            cobrowse_io=cobrowse_io_obj, cobrowse_request_type="transferred", transferred_status="")

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/update-transfer-session-log/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191',
                                                    access_token=cobrowse_agent.get_access_token_obj(),
                                                    allow_agent_cobrowse="true")

        CobrowseIOTransferredAgentsLogs.objects.create(
            cobrowse_io=cobrowse_io_obj, cobrowse_request_type="transferred", transferred_status="")

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        "reject_request": True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/update-transfer-session-log/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191',
                                                    access_token=cobrowse_agent.get_access_token_obj(),
                                                    allow_agent_cobrowse="false")

        CobrowseIOTransferredAgentsLogs.objects.create(
            cobrowse_io=cobrowse_io_obj, cobrowse_request_type="transferred", transferred_status="")

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/update-transfer-session-log/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

    def test_GetTransferCobrowsingSessionLogsUpdateAPI(self):
        logger.info('Testing test_GetTransferCobrowsingSessionLogsUpdateAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        user = User.objects.create(username='transferagent',
                                   password='transferagent')
        user.email = "test123@gmail.com"
        user.save()
        transferred_agent = CobrowseAgent.objects.create(user=user)
        transferred_agent.role = 'agent'
        transferred_agent.save()

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.is_active = True
        cobrowse_agent.save()

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191',
                                                    access_token=cobrowse_agent.get_access_token_obj(),
                                                    allow_agent_cobrowse="true")

        CobrowseIOTransferredAgentsLogs.objects.create(
            cobrowse_io=cobrowse_io_obj, cobrowse_request_type="transferred", transferred_agent=transferred_agent, transferred_status="")

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/check-transfer-session-log/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191',
                                                    access_token=cobrowse_agent.get_access_token_obj(),
                                                    allow_agent_cobrowse="false")

        CobrowseIOTransferredAgentsLogs.objects.create(
            cobrowse_io=cobrowse_io_obj, cobrowse_request_type="transferred", transferred_agent=transferred_agent, transferred_status="")

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/check-transfer-session-log/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

    def test_SaveInactivityPopupURLsAPI(self):
        logger.info('Testing test_SaveInactivityPopupURLsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')
        api_end_point = "/easy-assist/sales-ai/save-inactivity-pop-up-urls/"

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        urls_list = ["https://www.google.com", "https://facebook.com"]

        json_string = \
            json.dumps({'urls_list': urls_list})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post(api_end_point, json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        urls_list = ["https://www.google.com", "https://facebook.c"]

        json_string = \
            json.dumps({'urls_list': urls_list})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post(api_end_point, json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 300)

        urls_list = []

        json_string = \
            json.dumps({'urls_list': urls_list})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post(api_end_point, json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        urls_list = ["https://www.google.com", "https://facebook.c"]

        cobrowse_agent.role = "agent"
        cobrowse_agent.save()

        json_string = \
            json.dumps({'urls_list': urls_list})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post(api_end_point, json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 401)

    def test_SaveExitIntentPopupURLsAPI(self):
        logger.info('Testing test_SaveExitIntentPopupURLsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        api_end_point = "/easy-assist/sales-ai/save-exit-intent-pop-up-urls/"

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        urls_list = ["https://www.google.com", "https://facebook.com"]

        json_string = \
            json.dumps({'urls_list': urls_list})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post(api_end_point, json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        urls_list = ["https://www.google.com", "https://facebook.c"]

        json_string = \
            json.dumps({'urls_list': urls_list})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post(api_end_point, json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 300)

        urls_list = []

        json_string = \
            json.dumps({'urls_list': urls_list})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post(api_end_point, json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        urls_list = ["https://www.google.com", "https://facebook.c"]

        cobrowse_agent.role = "agent"
        cobrowse_agent.save()

        json_string = \
            json.dumps({'urls_list': urls_list})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post(api_end_point, json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 401)

    def test_GetAllActiveQueueStatusAPI(self):
        logger.info('Testing test_GetAllActiveQueueStatusAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        CobrowseIO.objects.create(full_name='Test',
                                  mobile_number='9191919191',
                                  share_client_session=False,
                                  is_active=True,
                                  is_archived=False,
                                  agent=None,
                                  is_lead=False,
                                  is_reverse_cobrowsing=False,
                                  access_token=cobrowse_agent.get_access_token_obj())

        json_string = json.dumps({'page_number': 1})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/get-all-active-queue-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_AssignAgentCobrowsingLeadAPI(self):
        logger.info('Testing test_AssignAgentCobrowsingLeadAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='supervisor_testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_agent.is_active = True
        cobrowse_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=None,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/assign-queue-lead/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.is_active = False
        cobrowse_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=None,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/assign-queue-lead/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 302)

        cobrowse_agent.is_active = True
        cobrowse_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    is_archived=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/assign-queue-lead/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 307)

        cobrowse_agent.is_active = True
        cobrowse_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    is_archived=True,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/assign-queue-lead/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 304)

        cobrowse_agent.is_active = True
        cobrowse_agent.save()
        access_token_obj = cobrowse_agent.get_access_token_obj()
        access_token_obj.maximum_active_leads = True
        access_token_obj.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    is_lead=False,
                                                    is_active=True,
                                                    is_reverse_cobrowsing=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    is_lead=False,
                                                    is_active=True,
                                                    is_reverse_cobrowsing=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    is_lead=False,
                                                    is_active=True,
                                                    is_reverse_cobrowsing=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=None,
                                                    is_lead=False,
                                                    is_active=True,
                                                    is_reverse_cobrowsing=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/assign-queue-lead/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 501)

    def test_SelfAssignCobrowsingSessionAPI(self):
        logger.info('Testing test_SelfAssignCobrowsingSessionAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_agent.is_active = True
        cobrowse_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=None,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/self-assign-cobrowsing-session/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.is_active = False
        cobrowse_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=None,
                                                    is_lead=False,
                                                    is_active=True,
                                                    is_reverse_cobrowsing=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/self-assign-cobrowsing-session/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 400)

        cobrowse_agent.is_active = True
        cobrowse_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    is_archived=True,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/self-assign-cobrowsing-session/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 501)

        cobrowse_agent.is_active = True
        cobrowse_agent.save()
        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    is_lead=False,
                                                    is_active=True,
                                                    is_reverse_cobrowsing=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    is_lead=False,
                                                    is_active=True,
                                                    is_reverse_cobrowsing=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=cobrowse_agent,
                                                    is_lead=False,
                                                    is_active=True,
                                                    is_reverse_cobrowsing=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        cobrowse_io_obj = CobrowseIO.objects.create(full_name='Test',
                                                    mobile_number='9191919191', share_client_session=False,
                                                    agent=None,
                                                    is_lead=False,
                                                    is_active=True,
                                                    is_reverse_cobrowsing=False,
                                                    access_token=cobrowse_agent.get_access_token_obj())

        json_string = \
            json.dumps({'session_id': str(cobrowse_io_obj.session_id),
                        'agent_id': str(cobrowse_agent.pk)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/self-assign-cobrowsing-session/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 401)

    def test_GetAllActiveLeadCountAPI(self):
        logger.info('Testing test_GetAllActiveLeadCountAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        CobrowseIO.objects.create(full_name='Test',
                                  mobile_number='9191919191', share_client_session=False,
                                  agent=cobrowse_agent,
                                  access_token=cobrowse_agent.get_access_token_obj())

        json_string = json.dumps({})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/get-all-active-lead-count/', json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response'
                                                               ]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response["total_active_leads"], 1)

    def test_UpdateActiveAgentsDetailsAPI(self):
        logger.info('Testing test_UpdateActiveAgentsDetailsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        json_string = json.dumps({
            "applied_filter": '',
            "agent_pk": ""
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/update-active-agents-details/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data['Response'])
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 200)

    def test_ToggleAgentStatusAPI(self):
        logger.info('Testing test_ToggleAgentStatusAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        new_user = User.objects.create(username='test_user',
                                       password='test@123',
                                       is_online=True)

        new_agent = CobrowseAgent.objects.create(
            user=new_user, is_active=True, is_account_active=True)
        new_agent.role = 'agent'
        new_agent.save()

        json_string = json.dumps({
            "active_status": True,
            "agent_pk": str(new_agent.pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/toggle-agent-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data['Response'])
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 200)

        new_user.is_online = False
        new_user.save()

        json_string = json.dumps({
            "active_status": True,
            "agent_pk": str(new_agent.pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/toggle-agent-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data['Response'])
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 302)

        new_user.is_online = True
        new_user.save()
        new_agent.is_cobrowsing_active = True
        new_agent.save()

        json_string = json.dumps({
            "active_status": True,
            "agent_pk": str(new_agent.pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/toggle-agent-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data['Response'])
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 302)

        new_agent.is_cognomeet_active = True
        new_agent.save()

        json_string = json.dumps({
            "active_status": True,
            "agent_pk": str(new_agent.pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/toggle-agent-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data['Response'])
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 302)

        cobrowse_agent.role = "agent"
        cobrowse_agent.save()

        new_agent.is_cognomeet_active = False
        new_agent.is_cobrowsing_active = False
        new_agent.save()

        json_string = json.dumps({
            "active_status": True,
            "agent_pk": str(new_agent.pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/toggle-agent-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data['Response'])
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 500)

        cobrowse_agent.role = "admin_ally"
        cobrowse_agent.save()

        new_agent.is_cognomeet_active = False
        new_agent.is_cobrowsing_active = False
        new_agent.save()

        json_string = json.dumps({
            "active_status": True,
            "agent_pk": str(new_agent.pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/toggle-agent-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data['Response'])
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 500)

        cobrowse_agent.role = "supervisor"
        cobrowse_agent.save()

        new_agent.is_cognomeet_active = False
        new_agent.is_cobrowsing_active = False
        new_agent.save()

        json_string = json.dumps({
            "active_status": True,
            "agent_pk": str(new_agent.pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/toggle-agent-status/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data['Response'])
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 200)
