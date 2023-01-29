
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


class ViewsAnalyticsOutbound(TestCase):

    def setUp(self):
        logger.info('Setting up the test environment for EasyAssistApp: views_cognomeet...', extra={
                    'AppName': 'EasyAssist'})
        user = User.objects.create(username='testeasyassist',
                                   password='testeasyassist')
        support_user = \
            User.objects.create(username='support_testeasyassist',
                                password='testeasyassist')
        supervisor_user = \
            User.objects.create(username='supervisor_testeasyassist',
                                password='testeasyassist')

        testeasyassist_agent = CobrowseAgent.objects.create(user=user)
        testeasyassist_agent.is_switch_allowed = True
        testeasyassist_agent.role = 'admin'
        testeasyassist_agent.save()

        support_agent = CobrowseAgent.objects.create(user=support_user)
        support_agent.is_switch_allowed = False
        support_agent.role = 'agent'
        support_agent.save()

        supervisor = \
            CobrowseAgent.objects.create(user=supervisor_user)
        supervisor.is_switch_allowed = True
        supervisor.role = 'supervisor'
        supervisor.save()

        testeasyassist_agent.agents.add(support_agent)
        testeasyassist_agent.agents.add(supervisor)
        testeasyassist_agent.save()

        CobrowseIO.objects.create(
            full_name='First Customer',
            mobile_number='9191919191',
            share_client_session=False,
            agent=testeasyassist_agent,
            access_token=testeasyassist_agent.get_access_token_obj(),
            is_lead=True,
            is_archived=True,
            is_helpful=False,
            title="Apply for Education Loan | HDFC Credila Education Loan")

        CobrowseIO.objects.create(
            full_name='Second Customer',
            mobile_number='9292929292',
            share_client_session=False,
            agent=testeasyassist_agent,
            access_token=testeasyassist_agent.get_access_token_obj(),
            is_lead=True,
            is_archived=True,
            is_helpful=True,
            title="ICICI Bank")

        CobrowseIO.objects.create(
            full_name='Third Customer',
            mobile_number='9191919191',
            share_client_session=False,
            agent=support_agent,
            access_token=support_agent.get_access_token_obj(),
            is_lead=True,
            is_archived=True,
            is_helpful=False,
            cobrowsing_start_datetime=datetime.now(),
            title="Atcoder")

        CobrowseIO.objects.create(
            full_name='Second Customer',
            mobile_number='9292929292',
            share_client_session=False,
            agent=support_agent,
            access_token=support_agent.get_access_token_obj(),
            is_lead=True,
            is_archived=True,
            is_helpful=True,
            title="Codechef")

        CobrowseIO.objects.create(
            full_name='Second Customer',
            mobile_number='9292929292',
            share_client_session=False,
            agent=support_agent,
            access_token=support_agent.get_access_token_obj(),
            is_lead=True,
            is_archived=True,
            is_helpful=True,
            title="Codechef",
            allow_agent_cobrowse="false",
            consent_cancel_count=1)

        CobrowseIO.objects.create(
            full_name='Second Customer',
            mobile_number='9292929292',
            share_client_session=False,
            agent=support_agent,
            access_token=support_agent.get_access_token_obj(),
            is_lead=True,
            is_archived=True,
            is_helpful=True,
            title="Codechef",
            allow_agent_cobrowse="false",
            consent_cancel_count=2)

        CobrowseIO.objects.create(
            full_name='Second Customer',
            mobile_number='9292929292',
            share_client_session=False,
            agent=support_agent,
            access_token=support_agent.get_access_token_obj(),
            is_lead=True,
            is_archived=True,
            is_helpful=True,
            title="Codechef",
            allow_agent_cobrowse="true",
            cobrowsing_start_datetime=datetime.now(),
            consent_cancel_count=1)

        CobrowseIO.objects.create(
            full_name='Second Customer',
            mobile_number='9292929292',
            share_client_session=False,
            agent=support_agent,
            access_token=support_agent.get_access_token_obj(),
            is_lead=True,
            is_archived=True,
            is_helpful=True,
            title="Codechef",
            allow_agent_cobrowse="true",
            cobrowsing_start_datetime=datetime.now(),
            consent_cancel_count=2)

    def tearDown(self):
        access_token_objs = CobrowseAccessToken.objects.all()
        for access_token_obj in access_token_objs:
            delete_access_token_specific_static_file(str(access_token_obj.key))

    def test_GetVisitedPageTitleListOutboundAPI(self):
        logger.info('Testing test_GetVisitedPageTitleListOutboundAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        json_string = json.dumps({})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/get-visited-page-title-list-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(len(response['query_pages']), 4)

    def test_GetQueryPageAnalyticsOutboundAPI(self):
        logger.info('Testing test_GetQueryPageAnalyticsOutboundAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "page": 1,
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/query-page-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = "agent"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "page": 1,
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/query-page-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 401)

        client.logout()
        client.login(username='supervisor_testeasyassist',
                     password='testeasyassist')
        cobrowse_agent.role = "supervisor"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "page": 1,
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/query-page-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetAgentWiseRequestAnalyticsOutboundAPI(self):
        logger.info('Testing test_GetAgentWiseRequestAnalyticsOutboundAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "page": 1,
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/agent-wise-request-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = "agent"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "page": 1,
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/agent-wise-request-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        client.logout()
        client.login(username='supervisor_testeasyassist',
                     password='testeasyassist')
        cobrowse_agent.role = "supervisor"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "page": 1,
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/agent-wise-request-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetAgentNPSAnalyticsOutboundAPI(self):
        logger.info('Testing test_GetAgentNPSAnalyticsOutboundAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "page": 1,
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/agent-wise-nps-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = "agent"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "page": 1,
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/agent-wise-nps-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        client.logout()
        client.login(username='supervisor_testeasyassist',
                     password='testeasyassist')
        cobrowse_agent.role = "supervisor"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "page": 1,
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/agent-wise-nps-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetAgentBasicAnalyticsOutboundAPI(self):
        logger.info('Testing test_GetAgentBasicAnalyticsOutboundAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "page": 1,
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/basic-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = "agent"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "page": 1,
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/basic-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        client.logout()
        client.login(username='supervisor_testeasyassist',
                     password='testeasyassist')
        cobrowse_agent.role = "supervisor"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "page": 1,
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/basic-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetAgentServiceRequestAnalyticsOutboundAPI(self):
        logger.info('Testing test_GetAgentServiceRequestAnalyticsOutboundAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "timeline": "daily",
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/service-request-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            "start_date": "04/05/2021",
            "end_date": "25/05/2021",
            "timeline": "weekly",
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/service-request-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            "start_date": "18/04/2021",
            "end_date": "25/05/2021",
            "timeline": "monthly",
            "title": "codechef"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/service-request-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.role = "agent"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "timeline": "daily",
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/service-request-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "timeline": "weekly",
            "title": "atcoder"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/service-request-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            "start_date": "18/04/2021",
            "end_date": "25/05/2021",
            "timeline": "monthly",
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/service-request-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        client.logout()
        client.login(username='supervisor_testeasyassist',
                     password='testeasyassist')
        cobrowse_agent.role = "supervisor"
        cobrowse_agent.save()

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "timeline": "daily",
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/service-request-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            "start_date": "18/05/2021",
            "end_date": "25/05/2021",
            "timeline": "weekly",
            "title": "all"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/service-request-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            "start_date": "18/04/2021",
            "end_date": "25/05/2021",
            "timeline": "monthly",
            "title": "codechef"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/service-request-analytics-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_ExportCronRequestUniqueCustomersOutboundAPI(self):
        logger.info('Testing test_ExportCronRequestUniqueCustomersOutboundAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        json_string = {
            "start_date": "2022-03-01",
            "end_date": "2022-05-09",
            "email": "testing@asdf.com",
            "title": "all"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/export-cron-request-unique-customers-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = {
            "start_date": "2022-03-01",
            "end_date": "2022-05-09",
            "email": "testing@asdf.com, admin@xyz.com",
            "title": "all"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/export-cron-request-unique-customers-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = {
            "start_date": "2022-03-01",
            "end_date": "2022-05-09",
            "email": "testing@asdf.com, admin@xyz.com, 1234@.com",
            "title": "all"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/export-cron-request-unique-customers-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 300)

        json_string = {
            "end_date": "2022-05-09",
            "email": "testing@asdf.com, admin@xyz.com",
            "title": "all"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/export-cron-request-unique-customers-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        json_string = {
            "start_date": "2022-03-01",
            "email": "testing@asdf.com, admin@xyz.com",
            "title": "all"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/export-cron-request-unique-customers-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        json_string = {
            "start_date": "2022-03-01",
            "end_date": "2022-05-09",
            "title": "all"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/export-cron-request-unique-customers-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_ExportCronRequestRepeatedCustomersOutboundAPI(self):
        logger.info('Testing test_EmailCapturedLeadsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        json_string = {
            "start_date": "2022-03-01",
            "end_date": "2022-05-09",
            "email": "testing@asdf.com, admin@xyz.com",
            "title": "all"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/export-cron-request-repeated-customers-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = {
            "start_date": "2022-03-01",
            "end_date": "2022-05-09",
            "email": "testing@asdf.com, admin@xyz.com, 1234@.com",
            "title": "all"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/export-cron-request-repeated-customers-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 300)

        json_string = {
            "start_date": "2022-03-01",
            "end_date": "2022-05-09",
            "email": "testing@asdf.com, admin@xyz.com"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/export-cron-request-repeated-customers-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = {
            "end_date": "2022-05-09",
            "email": "testing@asdf.com, admin@xyz.com",
            "title": "all"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/export-cron-request-repeated-customers-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        json_string = {
            "start_date": "2022-03-01",
            "email": "testing@asdf.com, admin@xyz.com",
            "title": "all"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/export-cron-request-repeated-customers-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        json_string = {
            "start_date": "2022-03-01",
            "end_date": "2022-05-09",
            "title": "all"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/export-cron-request-repeated-customers-outbound/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

    def test_EmailCapturedLeadsAPI(self):
        logger.info('Testing test_EmailCapturedLeadsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        json_string = {
            "start_date": "01/04/2022",
            "end_date": "08/04/2022",
            "email_id_list": "admin@xyz.com"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/email-captured-leads/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = {
            "start_date": "01/04/2022",
            "end_date": "08/04/2022",
            "email_id_list": "admin@xyz.com, testing@asdf.com"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/email-captured-leads/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = {
            "start_date": "01/04/2022",
            "end_date": "08/03/2022",
            "email_id_list": "admin@xyz.com, testing@asdf.com"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/email-captured-leads/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 300)

        json_string = {
            "start_date": "01/04/2022",
            "end_date": "08/04/2022",
            "email_id_list": "admin@xyz.com, testing@asdf.com, 1234@.com"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/email-captured-leads/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 300)

        json_string = {
            "end_date": "08/04/2022",
            "email_id_list": "admin@xyz.com, testing@asdf.com"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/email-captured-leads/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        json_string = {
            "start_date": "01/04/2022",
            "email_id_list": "admin@xyz.com, testing@asdf.com, 1234@.com"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/email-captured-leads/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        json_string = {
            "start_date": "01/04/2022",
            "end_date": "08/04/2022"
        }

        json_string = json.dumps(json_string)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/email-captured-leads/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)
