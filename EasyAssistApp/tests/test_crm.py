#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from EasyChatApp.models import User
from EasyAssistApp.models import *
from EasyAssistApp.encrypt import CustomEncrypt
from EasyAssistApp.utils import *
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
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


class CRM(TestCase):

    def setUp(self):
        logger.info('Setting up the test environment for EasyAssistApp: CRM...', extra={
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

    def get_auth_token(self):
        username = 'testeasyassist'
        password = 'testeasyassist'

        auth_headers = {'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode((username + ':' + password).encode()).decode()}

        client = Client()
        request = client.post('/easy-assist/crm/auth-token/',
                              json.dumps({}),
                              content_type='application/json',
                              **auth_headers)

        response_data = request.data
        return response_data["Body"]["auth_token"]

    def test_CRMGenerateAuthTokenAPI(self):
        logger.info('Testing test_CRMGenerateAuthTokenAPI...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()
        integration_obj = CRMIntegrationModel.objects.filter(
            auth_token=auth_token).first()

        self.assertNotEqual(integration_obj, None)

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')
        access_token = cobrowse_agent.get_access_token_obj()
        self.assertEqual(integration_obj.access_token, access_token)


class CRMInboundIntegrationAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMInboundIntegrationAPI started",
                    extra={'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/inbound/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "agent_id": "testeasyassist",
        }

        client = Client()
        request = client.post('/easy-assist/crm/inbound/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noAgent(self):
        logger.info('Testing test_noAgent...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "agent_id": "notexists",
            "session_id": "---"
        }

        client = Client()
        request = client.post('/easy-assist/crm/inbound/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 303)

    def test_noCobrowseSession(self):
        logger.info('Testing test_noCobrowseSession...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        cobrowse_io_obj = CobrowseIO.objects.create()

        data = {
            "agent_id": "testeasyassist",
            "session_id": str(cobrowse_io_obj.session_id)
        }

        cobrowse_io_obj.delete()

        client = Client()
        request = client.post('/easy-assist/crm/inbound/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 304)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')
        access_token = cobrowse_agent.get_access_token_obj()

        cobrowse_io_obj = CobrowseIO.objects.create(access_token=access_token)

        data = {
            "agent_id": "testeasyassist",
            "session_id": str(cobrowse_io_obj.session_id)
        }

        client = Client()
        request = client.post('/easy-assist/crm/inbound/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertNotEqual(response_data["Body"]["cobrowsing_url"], None)


class CRMSearchLeadIntegrationAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMSearchLeadIntegrationAPI started",
                    extra={'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/search-lead/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "agent_id": "testeasyassist",
        }

        client = Client()
        request = client.post('/easy-assist/crm/search-lead/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noAgent(self):
        logger.info('Testing test_noAgent...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "agent_id": "notexists",
            "search_value": "9988998899"
        }

        client = Client()
        request = client.post('/easy-assist/crm/search-lead/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 303)

    def test_noCobrowseSession(self):
        logger.info('Testing test_noCobrowseSession...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        search_value = '9191919191'

        data = {
            "agent_id": "testeasyassist",
            "search_value": search_value
        }

        client = Client()
        request = client.post('/easy-assist/crm/search-lead/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 304)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(
            full_name='Test',
            share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj(),
            is_lead=True,
        )

        search_value = '9191919191'
        md5_primary_id = hashlib.md5(search_value.encode()).hexdigest()

        capture_lead_obj = \
            CobrowseCapturedLeadData.objects.create(primary_value=md5_primary_id,
                                                    session_id=cobrowse_io_obj.session_id)

        cobrowse_io_obj.captured_lead.add(capture_lead_obj)

        data = {
            "agent_id": "testeasyassist",
            "search_value": search_value
        }

        client = Client()
        request = client.post('/easy-assist/crm/search-lead/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertNotEqual(response_data["Body"]["cobrowsing_url"], None)


class CRMDropLinkIntegrationAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMDropLinkIntegrationAPI started",
                    extra={'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/droplink/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "agent_id": "testeasyassist",
            "customer_name": "Customer Name",
            "client_page_link": "https://www.hdfccredila.com/apply-for-loan.html",
        }

        client = Client()
        request = client.post('/easy-assist/crm/droplink/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noAgent(self):
        logger.info('Testing test_noAgent...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "agent_id": "notexists",
            "customer_name": "Customer Name",
            "client_page_link": "https://www.hdfccredila.com/apply-for-loan.html",
            "customer_mobile_number": "9988998899",
        }

        client = Client()
        request = client.post('/easy-assist/crm/droplink/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 303)

    def test_generationFailed(self):
        logger.info('Testing test_generationFailed...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "agent_id": "testeasyassist",
            "customer_name": "Customer Name",
            "client_page_link": "com/apply-for-loan.html",
            "customer_mobile_number": "9988998899",
        }

        client = Client()
        request = client.post('/easy-assist/crm/droplink/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 305)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "agent_id": "testeasyassist",
            "customer_name": "Customer Name",
            "client_page_link": "https://www.hdfccredila.com/apply-for-loan.html",
            "customer_mobile_number": "9988998899",
        }

        client = Client()
        request = client.post('/easy-assist/crm/droplink/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertNotEqual(response_data["Body"]["cobrowsing_url"], None)
        self.assertNotEqual(response_data["Body"]["link_for_customer"], None)


class CRMCobrowsingSupportHistoryAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMCobrowsingSupportHistoryAPI started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/support-history/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {}

        client = Client()
        request = client.post('/easy-assist/crm/support-history/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noCobrowseSession(self):
        logger.info('Testing test_noCobrowseSession...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        cobrowse_io_obj = CobrowseIO.objects.create()

        data = {
            "session_id": str(cobrowse_io_obj.session_id),
        }

        cobrowse_io_obj.delete()

        client = Client()
        request = client.post('/easy-assist/crm/support-history/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 304)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(
            access_token=cobrowse_agent.get_access_token_obj()
        )

        data = {
            "session_id": str(cobrowse_io_obj.session_id),
        }

        client = Client()
        request = client.post('/easy-assist/crm/support-history/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertNotEqual(response_data["Body"]["data"], None)


class CRMCobrowsingChatHistoryAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMCobrowsingChatHistoryAPI started",
                    extra={'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/chat-history/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {}

        client = Client()
        request = client.post('/easy-assist/crm/chat-history/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noCobrowseSession(self):
        logger.info('Testing test_noCobrowseSession...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        cobrowse_io_obj = CobrowseIO.objects.create()

        data = {
            "session_id": str(cobrowse_io_obj.session_id),
        }

        cobrowse_io_obj.delete()

        client = Client()
        request = client.post('/easy-assist/crm/chat-history/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 304)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        cobrowse_io_obj = CobrowseIO.objects.create(
            access_token=cobrowse_agent.get_access_token_obj()
        )

        data = {
            "session_id": str(cobrowse_io_obj.session_id),
        }

        client = Client()
        request = client.post('/easy-assist/crm/chat-history/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertNotEqual(response_data["Body"]["data"], None)


class CRMCognoMeetCreateMeetingAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMCognoMeetCreateMeetingAPI started",
                    extra={'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/create-meeting/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "full_name": "Customer Name",
            "mobile_number": "9988998899",
            "meeting_start_date": "2021-09-07",
            "meeting_start_time": "10:34:46",
            "meeting_end_time": "11:34:45",
            "email": "test123@test.com",
            "agent_id": "testeasyassist",
            "meeting_description": "Description",
            "meeting_password": "1234",
            "send_email_to_customer": True,
            # "send_email_to_agent": True,
        }

        client = Client()
        request = client.post('/easy-assist/crm/create-meeting/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noAgent(self):
        logger.info('Testing test_noAgent...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "full_name": "Customer Name",
            "mobile_number": "9988998899",
            "meeting_start_date": "2021-09-07",
            "meeting_start_time": "10:34:46",
            "meeting_end_time": "11:34:45",
            "email": "test123@test.com",
            "agent_id": "notexists",
            "meeting_description": "Description",
            "meeting_password": "1234",
            "send_email_to_customer": True,
            "send_email_to_agent": True,
        }

        client = Client()
        request = client.post('/easy-assist/crm/create-meeting/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 303)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "full_name": "Customer Name",
            "mobile_number": "9988998899",
            "meeting_start_date": "2021-09-07",
            "meeting_start_time": "10:34:46",
            "meeting_end_time": "11:34:45",
            "email": "test123@test.com",
            "agent_id": "testeasyassist",
            "meeting_description": "Description",
            "meeting_password": "1234",
            "send_email_to_customer": False,
            "send_email_to_agent": False,
        }

        client = Client()
        request = client.post('/easy-assist/crm/create-meeting/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertNotEqual(response_data["Body"]["agent_meeting_url"], None)
        self.assertNotEqual(response_data["Body"]["meeting_id"], None)
        self.assertNotEqual(response_data["Body"]["client_meeting_url"], None)


class CRMCognoMeetDeleteMeetingAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMCognoMeetDeleteMeetingAPI started",
                    extra={'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/delete-meeting/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            # "meeting_id": str(meeting_io.meeting_id),
        }

        client = Client()
        request = client.post('/easy-assist/crm/delete-meeting/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noMeeting(self):
        logger.info('Testing test_noCobrowseSession...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        meeting_io = CobrowseVideoConferencing.objects.create()

        data = {
            "meeting_id": str(meeting_io.meeting_id),
        }

        meeting_io.delete()

        client = Client()
        request = client.post('/easy-assist/crm/delete-meeting/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 304)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        meeting_io = CobrowseVideoConferencing.objects.create()

        data = {
            "meeting_id": str(meeting_io.meeting_id),
        }

        client = Client()
        request = client.post('/easy-assist/crm/delete-meeting/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)


class CRMCognoMeetMeetingStatusAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMCognoMeetMeetingStatusAPI started",
                    extra={'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/meeting-status/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            # "meeting_id": str(meeting_io.meeting_id),
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noMeeting(self):
        logger.info('Testing test_noCobrowseSession...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        meeting_io = CobrowseVideoConferencing.objects.create()

        data = {
            "meeting_id": str(meeting_io.meeting_id),
        }

        meeting_io.delete()

        client = Client()
        request = client.post('/easy-assist/crm/meeting-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 304)

    def test_success_meeting_status__NotStarted(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        meeting_io = CobrowseVideoConferencing.objects.create()

        data = {
            "meeting_id": str(meeting_io.meeting_id),
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertEqual(response_data["Body"]["meeting_status"], "NotStarted")

    def test_success_meeting_status__Completed(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        meeting_io = CobrowseVideoConferencing.objects.create()
        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io,
            is_meeting_ended=True,
        )

        data = {
            "meeting_id": str(meeting_io.meeting_id),
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertEqual(response_data["Body"]["meeting_status"], "Completed")

    def test_success_meeting_status__Ongoing(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        meeting_io = CobrowseVideoConferencing.objects.create()
        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io,
            is_meeting_ended=False,
        )

        data = {
            "meeting_id": str(meeting_io.meeting_id),
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertEqual(response_data["Body"]["meeting_status"], "Ongoing")


class CRMCognoMeetMeetingDetailsAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMCognoMeetMeetingDetailsAPI started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/meeting-details/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            # "meeting_id": str(meeting_io.meeting_id),
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting-details/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noMeeting(self):
        logger.info('Testing test_noCobrowseSession...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        meeting_io = CobrowseVideoConferencing.objects.create()

        data = {
            "meeting_id": str(meeting_io.meeting_id),
        }

        meeting_io.delete()

        client = Client()
        request = client.post('/easy-assist/crm/meeting-details/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 304)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        meeting_io = CobrowseVideoConferencing.objects.create()

        data = {
            "meeting_id": str(meeting_io.meeting_id),
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting-details/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)


class CRMAgentAddAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMAgentAddAPI started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/agent/add/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        agent_id = "support_testeasyassist"
        data = {
            "agent_id": agent_id,
            "agent_name": "Test Xyz",
            "agent_email": "test@xyz.kk",
            "agent_mobile": "9988998899",
            "support_level": "L1",
            "agent_type": "agent",
            "supervisor_list": ["testeasyassist", "supervisor_testeasyassist"],
            "language_list": ["Hindi", "Gujarati"],
            # "product_category_list": ["Car Loan", "Home Loan"],
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/add/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_wrongInput(self):
        logger.info('Testing test_wrongInput...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        agent_id = "support_testeasyassist"
        data = {
            "agent_id": agent_id,
            "agent_name": "",
            "agent_email": "test",
            "agent_mobile": "998899889",
            "support_level": "L10",
            "agent_type": "admin_agent",
            "supervisor_list": ["testeasyassist", "supervisor_testeasyassist"],
            "language_list": ["Gujarati", "l"],
            "product_category_list": ["Car Loan", "h"],
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/add/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 306)

        self.assertNotEqual(response_data["Body"]["ValidatorResult"]["agent_id"], "VALID")
        self.assertNotEqual(response_data["Body"]["ValidatorResult"]["agent_name"], "VALID")
        self.assertNotEqual(response_data["Body"]["ValidatorResult"]["agent_email"], "VALID")
        self.assertNotEqual(response_data["Body"]["ValidatorResult"]["agent_mobile"], "VALID")
        self.assertNotEqual(response_data["Body"]["ValidatorResult"]["agent_type"], "VALID")
        self.assertNotEqual(response_data["Body"]["ValidatorResult"]["support_level"], "VALID")
        self.assertNotEqual(response_data["Body"]["ValidatorResult"]["supervisor_list"], "VALID")
        self.assertNotEqual(response_data["Body"]["ValidatorResult"]["language_list"], "VALID")
        self.assertNotEqual(response_data["Body"]["ValidatorResult"]["product_category_list"], "VALID")

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        agent1 = CobrowseAgent.objects.filter(user__username="testeasyassist").first()
        supervisor1 = CobrowseAgent.objects.filter(user__username="supervisor_testeasyassist").first()
        agent1.agents.add(supervisor1)
        agent1.save()

        agent_id = "new_agent_id"
        data = {
            "agent_id": agent_id,
            "agent_name": "Test Xyz",
            "agent_email": "test@xyz.kk",
            "agent_mobile": "9988998899",
            "support_level": "L1",
            "agent_type": "agent",
            "supervisor_list": ["testeasyassist", "supervisor_testeasyassist"],
            "language_list": ["LangOne", "LangTwo"],
            "product_category_list": ["Car Loan", "Home Loan"],
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/add/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

        newAgentObj = CobrowseAgent.objects.get(user__username__iexact=agent_id)
        self.assertEqual(newAgentObj.user.email, "test@xyz.kk")
        self.assertEqual(newAgentObj.mobile_number, "9988998899")
        self.assertEqual(newAgentObj.support_level, "L1")
        self.assertEqual(newAgentObj.role, "agent")

        self.assertIn(newAgentObj, agent1.agents.all())
        self.assertIn(newAgentObj, supervisor1.agents.all())

        lang_obj_1 = LanguageSupport.objects.filter(title__iexact="LangOne").first()
        lang_obj_2 = LanguageSupport.objects.filter(title__iexact="LangTwo").first()

        self.assertNotEqual(lang_obj_1, None)
        self.assertNotEqual(lang_obj_2, None)

        self.assertIn(lang_obj_1, newAgentObj.supported_language.all())
        self.assertIn(lang_obj_2, newAgentObj.supported_language.all())

        self.assertIn(lang_obj_1, agent1.supported_language.all())
        self.assertIn(lang_obj_2, agent1.supported_language.all())

        self.assertIn(lang_obj_1, supervisor1.supported_language.all())
        self.assertIn(lang_obj_2, supervisor1.supported_language.all())

        category_obj_1 = ProductCategory.objects.filter(title__iexact="Car Loan").first()
        category_obj_2 = ProductCategory.objects.filter(title__iexact="Home Loan").first()

        self.assertNotEqual(category_obj_1, None)
        self.assertNotEqual(category_obj_2, None)

        self.assertIn(category_obj_1, newAgentObj.product_category.all())
        self.assertIn(category_obj_2, newAgentObj.product_category.all())

        self.assertIn(category_obj_1, agent1.product_category.all())
        self.assertIn(category_obj_2, agent1.product_category.all())

        self.assertIn(category_obj_1, supervisor1.product_category.all())
        self.assertIn(category_obj_2, supervisor1.product_category.all())


class CRMAgentDelete(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMAgentDelete started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/agent/delete/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            # "agent_id": "support_testeasyassist"
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/delete/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noAgent(self):
        logger.info('Testing test_noAgent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        adminAgent = CobrowseAgent.objects.filter(user__username="testeasyassist").first()
        supervisorAgent = CobrowseAgent.objects.filter(user__username="supervisor_testeasyassist").first()
        newAgentObj = CobrowseAgent.objects.filter(user__username="support_testeasyassist").first()

        adminAgent.agents.add(supervisorAgent)
        adminAgent.save()

        # supervisorAgent.agents.add(newAgentObj)
        # supervisorAgent.save()

        data = {
            "agent_id": newAgentObj.user.username
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/delete/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 303)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        adminAgent = CobrowseAgent.objects.filter(user__username="testeasyassist").first()
        supervisorAgent = CobrowseAgent.objects.filter(user__username="supervisor_testeasyassist").first()
        newAgentObj = CobrowseAgent.objects.filter(user__username="support_testeasyassist").first()

        adminAgent.agents.add(supervisorAgent)
        adminAgent.save()

        supervisorAgent.agents.add(newAgentObj)
        supervisorAgent.save()

        data = {
            "agent_id": newAgentObj.user.username
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/delete/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)


class CRMAgentChangeStatus(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMAgentChangeStatus started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/agent/change-status/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            # "agent_id": "support_testeasyassist",
            # "is_active": False,
            # "is_account_active": False
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/change-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noAgent(self):
        logger.info('Testing test_noAgent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        adminAgent = CobrowseAgent.objects.filter(user__username="testeasyassist").first()
        supervisorAgent = CobrowseAgent.objects.filter(user__username="supervisor_testeasyassist").first()
        newAgentObj = CobrowseAgent.objects.filter(user__username="support_testeasyassist").first()

        adminAgent.agents.add(supervisorAgent)
        adminAgent.save()

        # supervisorAgent.agents.add(newAgentObj)
        # supervisorAgent.save()

        data = {
            "agent_id": newAgentObj.user.username,
            "is_active": False,
            "is_account_active": False
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/change-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 303)

    def test_success_true(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        adminAgent = CobrowseAgent.objects.filter(user__username="testeasyassist").first()
        supervisorAgent = CobrowseAgent.objects.filter(user__username="supervisor_testeasyassist").first()
        newAgentObj = CobrowseAgent.objects.filter(user__username="support_testeasyassist").first()
        newAgentObj.is_account_active = False
        newAgentObj.save()

        adminAgent.agents.add(supervisorAgent)
        adminAgent.save()

        supervisorAgent.agents.add(newAgentObj)
        supervisorAgent.save()

        data = {
            "agent_id": newAgentObj.user.username,
            "is_active": True,
            "is_account_active": True
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/change-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

        newAgentObj = CobrowseAgent.objects.filter(user__username="support_testeasyassist").first()
        self.assertEqual(newAgentObj.is_active, True)
        self.assertEqual(newAgentObj.is_account_active, True)

    def test_success_false(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        adminAgent = CobrowseAgent.objects.filter(user__username="testeasyassist").first()
        supervisorAgent = CobrowseAgent.objects.filter(user__username="supervisor_testeasyassist").first()
        newAgentObj = CobrowseAgent.objects.filter(user__username="support_testeasyassist").first()
        newAgentObj.is_account_active = True
        newAgentObj.save()

        adminAgent.agents.add(supervisorAgent)
        adminAgent.save()

        supervisorAgent.agents.add(newAgentObj)
        supervisorAgent.save()

        data = {
            "agent_id": newAgentObj.user.username,
            "is_active": False,
            "is_account_active": False
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/change-status/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

        newAgentObj = CobrowseAgent.objects.filter(user__username="support_testeasyassist").first()
        self.assertEqual(newAgentObj.is_active, False)
        self.assertEqual(newAgentObj.is_account_active, False)


class CRMAgentChangePassword(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMAgentChangePassword started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/agent/change-password/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "agent_id": "support_testeasyassist",
            "old_password": "Old@123",
            # "new_password": "New@123"
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/change-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noAgent(self):
        logger.info('Testing test_noAgent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        adminAgent = CobrowseAgent.objects.filter(user__username="testeasyassist").first()
        supervisorAgent = CobrowseAgent.objects.filter(user__username="supervisor_testeasyassist").first()
        newAgentObj = CobrowseAgent.objects.filter(user__username="support_testeasyassist").first()

        adminAgent.agents.add(supervisorAgent)
        adminAgent.save()

        # supervisorAgent.agents.add(newAgentObj)
        # supervisorAgent.save()

        data = {
            "agent_id": newAgentObj.user.username,
            "old_password": "Old@123",
            "new_password": "New@123"
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/change-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 303)

    def test_wrongOldPassword(self):
        logger.info('Testing test_wrongOldPassword...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        adminAgent = CobrowseAgent.objects.filter(user__username="testeasyassist").first()
        supervisorAgent = CobrowseAgent.objects.filter(user__username="supervisor_testeasyassist").first()
        newAgentObj = CobrowseAgent.objects.filter(user__username="support_testeasyassist").first()

        adminAgent.agents.add(supervisorAgent)
        adminAgent.save()

        supervisorAgent.agents.add(newAgentObj)
        supervisorAgent.save()

        newAgentObj_userObj = newAgentObj.user
        newAgentObj_userObj.set_password("Old@123")
        newAgentObj_userObj.save()

        data = {
            "agent_id": newAgentObj.user.username,
            "old_password": "Wrong@Old$Password",
            "new_password": "New@123"
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/change-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 306)

    def test_sameAsOldPassword(self):
        logger.info('Testing test_sameAsOldPassword...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        adminAgent = CobrowseAgent.objects.filter(user__username="testeasyassist").first()
        supervisorAgent = CobrowseAgent.objects.filter(user__username="supervisor_testeasyassist").first()
        newAgentObj = CobrowseAgent.objects.filter(user__username="support_testeasyassist").first()

        adminAgent.agents.add(supervisorAgent)
        adminAgent.save()

        supervisorAgent.agents.add(newAgentObj)
        supervisorAgent.save()

        newAgentObj_userObj = newAgentObj.user
        newAgentObj_userObj.set_password("Old@123")
        newAgentObj_userObj.save()

        data = {
            "agent_id": newAgentObj.user.username,
            "old_password": "Old@123",
            "new_password": "New@123"
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/change-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        data = {
            "agent_id": newAgentObj.user.username,
            "old_password": "New@123",
            "new_password": "New@123"
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/change-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 307)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        adminAgent = CobrowseAgent.objects.filter(user__username="testeasyassist").first()
        supervisorAgent = CobrowseAgent.objects.filter(user__username="supervisor_testeasyassist").first()
        newAgentObj = CobrowseAgent.objects.filter(user__username="support_testeasyassist").first()

        adminAgent.agents.add(supervisorAgent)
        adminAgent.save()

        supervisorAgent.agents.add(newAgentObj)
        supervisorAgent.save()

        newAgentObj_userObj = newAgentObj.user
        newAgentObj_userObj.set_password("Old@123")
        newAgentObj_userObj.save()

        data = {
            "agent_id": newAgentObj.user.username,
            "old_password": "Old@123",
            "new_password": "New@123"
        }

        client = Client()
        request = client.post('/easy-assist/crm/agent/change-password/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)


class CRMUpdateMeetingSettings(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMUpdateMeetingSettings started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/meeting/update-settings/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            # "allow_meeting_feedback": False,
            # "meeting_default_password": "5678",
            # "meeting_host_url": "test.allincall.in",
            # "allow_meeting_end_time": True,
            # "meeting_end_time": 70,
            # "meet_background_color": "#121212",
            # "allow_support_documents": False,
            # "share_document_from_livechat": False,
            # "allow_only_support_documents": True,
            # "enable_chat_functionality": False,
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting/update-settings/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "allow_meeting_feedback": False,
            "meeting_default_password": "5678",
            "meeting_host_url": "test.allincall.in",
            "allow_meeting_end_time": True,
            "meeting_end_time": 70,
            "meet_background_color": "#121212",
            "allow_support_documents": False,
            "share_document_from_livechat": False,
            "allow_only_support_documents": True,
            "enable_chat_functionality": False,
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting/update-settings/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        access_token = cobrowse_agent.get_access_token_obj()

        self.assertEqual(access_token.allow_meeting_feedback, False)
        self.assertEqual(access_token.meeting_default_password, "5678")
        self.assertEqual(access_token.meeting_host_url, "test.allincall.in")
        self.assertEqual(access_token.allow_meeting_end_time, True)
        self.assertEqual(access_token.meeting_end_time, "70")
        self.assertEqual(access_token.meet_background_color, "#121212")
        self.assertEqual(access_token.allow_support_documents, False)
        self.assertEqual(access_token.share_document_from_livechat, False)
        self.assertEqual(access_token.allow_only_support_documents, True)
        self.assertEqual(access_token.enable_chat_functionality, False)


class CRMAgentMeetings(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMAgentMeetings started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/meeting/agent-meetings/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        # cobrowse_agent = CobrowseAgent.objects.get(
        #     user__username='testeasyassist')

        data = {
            # "agent_id": cobrowse_agent.user.username,
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting/agent-meetings/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noAgent(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        data = {
            "agent_id": cobrowse_agent.user.username + "..",
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting/agent-meetings/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 303)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        cobrowse_agent = CobrowseAgent.objects.get(
            user__username='testeasyassist')

        data = {
            "agent_id": cobrowse_agent.user.username,
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting/agent-meetings/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertNotEqual(response_data["Body"]["meetings"], None)


class CRMMeetingAnalytics(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMMeetingAnalytics started", extra={
                    'AppName': 'EasyAssist'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/easy-assist/crm/meeting/analytics/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "start_date": "2021-09-07",
            # "end_date": "2021-09-14",
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting/analytics/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_wrongInput(self):
        logger.info('Testing test_wrongInput...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "start_date": "2021-09-07",
            "end_date": "2021-09-14",
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting/analytics/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 306)

        self.assertNotEqual(response_data["Body"]["ValidatorResult"]["start_date"], "VALID")
        self.assertNotEqual(response_data["Body"]["ValidatorResult"]["end_date"], "VALID")

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyAssist'})

        auth_token = self.get_auth_token()

        data = {
            "start_date": "07-09-2021",
            "end_date": "15-09-2021",
        }

        client = Client()
        request = client.post('/easy-assist/crm/meeting/analytics/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertNotEqual(response_data["Body"]["total_meeting_scheduled"], None)
        self.assertNotEqual(response_data["Body"]["total_meeting_completed"], None)
        self.assertNotEqual(response_data["Body"]["total_ongoing_meeting"], None)
        self.assertNotEqual(response_data["Body"]["avg_call_duration"], None)
        self.assertNotEqual(response_data["Body"]["agent_wise_analytics"], None)
