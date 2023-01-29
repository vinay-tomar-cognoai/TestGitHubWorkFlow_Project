#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from EasyChatApp.models import User
from EasyTMSApp.models import *
from EasyTMSApp.utils import *
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
        logger.info('Setting up the test environment for EasyTMSApp: CRM...', extra={
                    'AppName': 'EasyTMS'})
        user = User.objects.create(username='testeasytms',
                                   password='testeasytms')
        support_user = \
            User.objects.create(username='support_testeasytms',
                                password='testeasytms')
        supervisor_user = \
            User.objects.create(username='supervisor_testeasytms',
                                password='testeasytms')

        tms_agent = Agent.objects.create(user=user)
        tms_agent.role = 'admin'
        tms_agent.save()

        tms_agent = Agent.objects.create(user=support_user)
        tms_agent.role = 'agent'
        tms_agent.save()

        tms_agent = \
            Agent.objects.create(user=supervisor_user)
        tms_agent.role = 'supervisor'
        tms_agent.save()

    def get_auth_token(self):
        username = 'testeasytms'
        password = 'testeasytms'

        auth_headers = {'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode((username + ':' + password).encode()).decode()}

        client = Client()
        request = client.post('/tms/crm/auth-token/',
                              json.dumps({}),
                              content_type='application/json',
                              **auth_headers)

        response_data = request.data
        return response_data["Body"]["auth_token"]

    def test_CRMGenerateAuthTokenAPI(self):
        logger.info('Testing test_CRMGenerateAuthTokenAPI...',
                    extra={'AppName': 'EasyTMS'})

        auth_token = self.get_auth_token()
        integration_obj = CRMIntegrationModel.objects.filter(
            auth_token=auth_token).first()

        self.assertNotEqual(integration_obj, None)

        tms_agent = Agent.objects.get(
            user__username='testeasytms')

        access_token = get_access_token_obj(tms_agent, Agent, TMSAccessToken)

        self.assertEqual(integration_obj.access_token, access_token)


class CRMGenerateTicketAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMGenerateTicketAPI started",
                    extra={'AppName': 'EasyTMS'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyTMS'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/tms/crm/generate-ticket/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyTMS'})

        auth_token = self.get_auth_token()

        data = {
            "customer_name": "customer_name",
            # "issue_description": "issue_description",
            "query_attachment": "query_attachment",
            "customer_mobile_number": "customer_mobile_number",
            "customer_email_id": "customer_email_id",
            "agent_username": "testeasytms",
            "bot_id": 1,
            "channel_name": "Web",
            "ticket_category": "hello",
            "ticket_priority": "urgent"
        }

        client = Client()
        request = client.post('/tms/crm/generate-ticket/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyTMS'})

        auth_token = self.get_auth_token()

        data = {
            "customer_name": "customer_name",
            "issue_description": "issue_description",
            "query_attachment": "query_attachment",
            "customer_mobile_number": "customer_mobile_number",
            "customer_email_id": "customer_email_id",
            "agent_username": "notexists",
            "bot_id": 1,
            "channel_name": "Web",
            "ticket_category": "hello",
            "ticket_priority": "urgent"
        }

        client = Client()
        request = client.post('/tms/crm/generate-ticket/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertNotEqual(response_data["Body"]["TicketId"], None)

        ticket_id = response_data["Body"]["TicketId"]
        ticket_obj = Ticket.objects.filter(ticket_id=ticket_id).first()
        self.assertNotEqual(ticket_obj, None)

        tms_agent = Agent.objects.get(
            user__username='testeasytms')

        access_token = get_access_token_obj(tms_agent, Agent, TMSAccessToken)

        self.assertEqual(ticket_obj.access_token, access_token)


class CRMGetTicketInfoAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMGetTicketInfoAPI started", extra={
                    'AppName': 'EasyTMS'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyTMS'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/tms/crm/ticket-info/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyTMS'})

        auth_token = self.get_auth_token()

        data = {
            # "ticket_id": str(ticket_obj.ticket_id),
        }

        client = Client()
        request = client.post('/tms/crm/ticket-info/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noTicket(self):
        logger.info('Testing test_noTicket...',
                    extra={'AppName': 'EasyTMS'})

        auth_token = self.get_auth_token()

        ticket_obj = Ticket.objects.create()

        data = {
            "ticket_id": str(ticket_obj.ticket_id),
        }

        ticket_obj.delete()

        client = Client()
        request = client.post('/tms/crm/ticket-info/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 304)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyTMS'})

        auth_token = self.get_auth_token()

        tms_agent = Agent.objects.get(
            user__username='testeasytms')
        access_token = get_access_token_obj(tms_agent, Agent, TMSAccessToken)

        ticket_obj = Ticket.objects.create(access_token=access_token)

        data = {
            "ticket_id": str(ticket_obj.ticket_id),
        }

        client = Client()
        request = client.post('/tms/crm/ticket-info/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertNotEqual(response_data["Body"]["Data"], None)


class CRMGetTicketActivityAPI(CRM):

    def test_wrongAuth(self):
        logger.info("Testing of CRMGetTicketActivityAPI started", extra={
                    'AppName': 'EasyTMS'})
        logger.info('Testing test_wrongAuth...',
                    extra={'AppName': 'EasyTMS'})

        auth_token = self.get_auth_token()

        auth_token += "WRONG"

        client = Client()
        request = client.post('/tms/crm/ticket-activity/',
                              json.dumps({}),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.data["Head"]["ResponseCode"], 401)

    def test_noContent(self):
        logger.info('Testing test_noContent...',
                    extra={'AppName': 'EasyTMS'})

        auth_token = self.get_auth_token()

        data = {
            # "ticket_id": str(ticket_obj.ticket_id),
        }

        client = Client()
        request = client.post('/tms/crm/ticket-activity/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 301)

    def test_noTicket(self):
        logger.info('Testing test_noTicket...',
                    extra={'AppName': 'EasyTMS'})

        auth_token = self.get_auth_token()

        ticket_obj = Ticket.objects.create()

        data = {
            "ticket_id": str(ticket_obj.ticket_id),
        }

        ticket_obj.delete()

        client = Client()
        request = client.post('/tms/crm/ticket-activity/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 304)

    def test_success(self):
        logger.info('Testing test_success...', extra={'AppName': 'EasyTMS'})

        auth_token = self.get_auth_token()

        tms_agent = Agent.objects.get(
            user__username='testeasytms')
        access_token = get_access_token_obj(tms_agent, Agent, TMSAccessToken)

        ticket_obj = Ticket.objects.create(access_token=access_token)

        data = {
            "ticket_id": str(ticket_obj.ticket_id),
        }

        client = Client()
        request = client.post('/tms/crm/ticket-activity/',
                              json.dumps(data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION="Bearer " + auth_token)

        self.assertEqual(request.status_code, 200)

        response_data = request.data
        self.assertEqual(response_data["Head"]["ResponseCode"], 200)
        self.assertNotEqual(response_data["Body"]["Data"], None)
