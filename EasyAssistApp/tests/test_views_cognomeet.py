
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


class ViewsCognoMeet(TestCase):

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

    def test_GenerateVideoConferencingMeetAPI(self):
        logger.info('Testing test_GenerateVideoConferencingMeetAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        json_string = json.dumps({
            "full_name": "test",
            "mobile_number": "9191919191",
            "meeting_description": "None",
            "meeting_start_date": "2021-05-21",
            "meeting_end_time": "16:00",
            "meeting_start_time": "14:22",
            "meeting_password": "1234",
            "email": "test@example.com"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/generate-video-meeting/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_SaveVideoConferencingMeetAPI(self):
        logger.info('Testing test_SaveVideoConferencingMeetAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time())

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
            "full_name": "test",
            "mobile_number": "9292929292",
            "meeting_description": "None",
            "meeting_start_date": "2021-05-21",
            "meeting_end_time": "16:00",
            "meeting_start_time": "14:38",
            "meeting_password": "1234",
            "email": "test@example.com"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/save-video-meeting/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            "meeting_id": str(uuid.uuid4()),
            "full_name": "test",
            "mobile_number": "9292929292",
            "meeting_description": "None",
            "meeting_start_date": "2021-05-21",
            "meeting_end_time": "16:00",
            "meeting_start_time": "14:38",
            "meeting_password": "1234",
            "email": "test@example.com"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/save-video-meeting/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

    def test_GetCognoVidScheduledMeetingsListAPI(self):
        logger.info('Testing test_GetCognoVidScheduledMeetingsListAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time())

        json_string = json.dumps({})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/scheduled-meetings-list/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(len(response['meeting_list']), 1)

        meeting_io.agent = None
        meeting_io.save()

        json_string = json.dumps({})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/scheduled-meetings-list/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(len(response['meeting_list']), 0)

    def test_CognoVidAuthenticatePasswordAPI(self):
        logger.info('Testing test_CognoVidAuthenticatePasswordAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time())

        meeting_io.meeting_password = "1234"
        meeting_io.save()

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
            "password": "1234",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/authenticate-meeting-password/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        meeting_io.meeting_password = "4567"
        meeting_io.save()

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
            "password": "1234",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/authenticate-meeting-password/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        json_string = json.dumps({
            "meeting_id": str(uuid.uuid4()),
            "password": "1234",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/authenticate-meeting-password/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 401)

    def test_CognoVidMeetingDurationAPI(self):
        logger.info('Testing test_CognoVidMeetingDurationAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time())

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/save-meeting-duration/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_CognoVidMeetingNotesAPI(self):
        logger.info('Testing test_CognoVidMeetingNotesAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time())

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
            "notes": "Agent Notes",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/save-meeting-notes/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_CognoVidMeetingChatsAPI(self):
        logger.info('Testing test_CognoVidMeetingChatsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time())

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        chat_history = [
            json.dumps({
                "type": "text",
                "message": "hello",
                "sender": "agent",
                "time": "07:40",
            }),
            json.dumps({
                "type": "text",
                "message": "hello",
                "sender": "client",
                "time": "07:42",
            }),
            json.dumps({
                "type": "attachment",
                "message": "/easy-assist/download-file/",
                "sender": "agent",
                "time": "07:44",
            }),
            json.dumps({
                "type": "attachment",
                "message": "/easy-assist/download-file/",
                "sender": "client",
                "time": "07:46",
            }),
        ]

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
            "chat_history": chat_history,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/save-meeting-chats/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_CognoVidGetClientAgentChatAPI(self):
        logger.info('Testing test_CognoVidGetClientAgentChatAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time())

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        chat_history = [
            json.dumps({
                "type": "text",
                "message": "hello",
                "sender": "agent",
                "time": "07:40",
            }),
            json.dumps({
                "type": "text",
                "message": "hello",
                "sender": "client",
                "time": "07:42",
            }),
            json.dumps({
                "type": "attachment",
                "message": "/easy-assist/download-file/",
                "sender": "agent",
                "time": "07:44",
            }),
            json.dumps({
                "type": "attachment",
                "message": "/easy-assist/download-file/",
                "sender": "client",
                "time": "07:46",
            }),
        ]

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
            "chat_history": chat_history,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/save-meeting-chats/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/get-client-agent-chats/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_SaveClientLocationDetailsAPI(self):
        logger.info('Testing test_SaveClientLocationDetailsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time())

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
            "client_name": "test",
            "longitude": 81.7823744,
            "latitude": 25.4574592,
            "client_address": "Abubakarpur, Nyay Nagar, Dhoomanganj, Prayagraj, Uttar Pradesh 211011, India"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/save-client-location-details/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetListOfMeetSuportAgentsAPI(self):
        logger.info('Testing test_GetListOfMeetSuportAgentsAPI...',
                    extra={'AppName': 'EasyAssist'})

        admin_user = User.objects.create(username='admin',
                                         password='adminadmin')
        admin_agent = CobrowseAgent.objects.create(user=admin_user,
                                                   is_switch_allowed=True, role='admin', is_active=True)

        supervisor1_user = User.objects.create(username='supervisor1',
                                               password='supervisor1supervisor1')
        supervisor1_agent = \
            CobrowseAgent.objects.create(user=supervisor1_user,
                                         is_switch_allowed=True, role='supervisor',
                                         is_active=True)

        agent1_user = User.objects.create(username='agent1',
                                          password='agent1agent1')
        agent1_agent = CobrowseAgent.objects.create(user=agent1_user,
                                                    role='agent', is_active=True)

        agent2_user = User.objects.create(username='agent2',
                                          password='agent2agent2')
        agent2_agent = CobrowseAgent.objects.create(user=agent2_user,
                                                    role='agent', is_active=True)

        agent3_user = User.objects.create(username='agent3',
                                          password='agent3agent3')
        agent3_agent = CobrowseAgent.objects.create(user=agent3_user,
                                                    role='agent', is_active=True)

        agent4_user = User.objects.create(username='agent4',
                                          password='agent4agent4')
        agent4_agent = CobrowseAgent.objects.create(user=agent4_user,
                                                    role='agent')

        agent5_user = User.objects.create(username='agent5',
                                          password='agent5agent5')
        agent5_agent = CobrowseAgent.objects.create(user=agent5_user,
                                                    role='agent')

        admin_agent.agents.add(supervisor1_agent)
        admin_agent.agents.add(agent1_agent)
        admin_agent.agents.add(agent4_agent)
        admin_agent.save()

        supervisor1_agent.agents.add(agent2_agent)
        supervisor1_agent.agents.add(agent3_agent)
        supervisor1_agent.agents.add(agent5_agent)
        supervisor1_agent.save()

        custom_encrypt_obj = CustomEncrypt()

        client = APIClient()
        client.login(username='agent2',
                     password='agent2agent2')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=agent2_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time())

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            'id': str(meeting_io.meeting_id)
        })
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/get-meet-support-agents/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        support_agents = response['support_agents']
        total_support_agents = 0
        for _, agent_list in support_agents.items():
            total_support_agents += len(agent_list)

        self.assertEqual(total_support_agents, 4)

        agent1_agent.is_account_active = False
        agent1_agent.save()
        json_string = json.dumps({
            'id': str(meeting_io.meeting_id)
        })
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/get-meet-support-agents/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        support_agents = response['support_agents']
        total_support_agents = 0
        for _, agent_list in support_agents.items():
            total_support_agents += len(agent_list)

        self.assertEqual(total_support_agents, 3)

        agent3_agent.is_active = False
        agent3_agent.save()
        json_string = json.dumps({
            'id': str(meeting_io.meeting_id)
        })
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/get-meet-support-agents/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        support_agents = response['support_agents']
        total_support_agents = 0
        for _, agent_list in support_agents.items():
            total_support_agents += len(agent_list)

        self.assertEqual(total_support_agents, 2)

    def test_GetListOfMeetingFormsAPI(self):
        logger.info('Testing test_GetListOfMeetingFormsAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_vidoe_form = CobrowseVideoConferencingForm.objects.create(
            form_name="Test Form")
        cobrowse_vidoe_form.agents.add(cobrowse_agent)

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time())

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "id": str(meeting_io.meeting_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/get-meeting-forms/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(len(response["meeting_forms"]), 1)

        cobrowse_vidoe_form.is_deleted = True
        cobrowse_vidoe_form.save()

        json_string = json.dumps({
            "id": str(meeting_io.meeting_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/get-meeting-forms/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(len(response["meeting_forms"]), 0)

    def test_RequestJoinMeetingAPI(self):
        logger.info('Testing test_RequestJoinMeetingAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        support_agent = \
            CobrowseAgent.objects.get(user__username='support_testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time())

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "id": str(meeting_io.meeting_id),
            "support_agents": [str(support_agent.pk)]
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/request-agent-meeting/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_AssignVideoConferencingMeetAPI(self):
        logger.info('Testing test_AssignVideoConferencingMeetAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time(),
            is_cobrowsing_meeting=True)

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
            "agent_id": str(cobrowse_agent.pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/agent/assign-video-meeting/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_InviteVideoMeetingEmailAPI(self):
        logger.info('Testing test_InviteVideoMeetingEmailAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time(),
            is_cobrowsing_meeting=False)

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
            "email_ids": ["test@example.com", "test2@example.com"]
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/invite-video-meeting-email/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_CheckAgentConnectedOrNotAPI(self):
        logger.info('Testing test_CheckAgentConnectedOrNotAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time(),
            is_cobrowsing_meeting=False,
            is_agent_connected=True)

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/check-agent-connected-or-not/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response["is_agent_connected"], True)

        meeting_io.is_agent_connected = False
        meeting_io.save()

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/check-agent-connected-or-not/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response["is_agent_connected"], False)

    def test_UpdateAgentJoinStatusAPI(self):
        logger.info('Testing test_UpdateAgentJoinStatusAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time(),
            is_cobrowsing_meeting=False)

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
            "status": "true",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/update-agent-join-status/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_ClientMeetingFeedbackAPI(self):
        logger.info('Testing test_ClientMeetingFeedbackAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time(),
            is_cobrowsing_meeting=True)

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
            "feedback_rating": "10",
            "feedback_comment": "Good Cogno Meet",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/client-meeting-feedback/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_CheckMeetingEndedOrNotAPI(self):
        logger.info('Testing test_CheckMeetingEndedOrNotAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        access_token_obj = cobrowse_agent.get_access_token_obj()
        access_token_obj.allow_meeting_end_time = True
        access_token_obj.save()

        meeting_end_datetime = datetime.now() + timedelta(hours=2)
        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time(),
            is_cobrowsing_meeting=True)

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/check-meeting-ended-or-not/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        meeting_start_date = datetime.now() - timedelta(minutes=55)
        meeting_io.meeting_start_time = meeting_start_date.time()
        meeting_io.save()

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/check-meeting-ended-or-not/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        meeting_start_date = datetime.now() - timedelta(minutes=60)
        meeting_io.meeting_start_time = meeting_start_date.time()
        meeting_io.save()

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/check-meeting-ended-or-not/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        access_token_obj.allow_meeting_end_time = False
        access_token_obj.save()

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/check-meeting-ended-or-not/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 400)

    def test_SaveVoipMeetingDurationAPI(self):
        logger.info('Testing test_SaveVoipMeetingDurationAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        cobrowse_io_obj = CobrowseIO.objects.create(
            full_name='Test',
            mobile_number='9191919191', share_client_session=False,
            agent=cobrowse_agent,
            access_token=cobrowse_agent.get_access_token_obj())

        meeting_io = CobrowseVideoConferencing.objects.create(
            meeting_id=cobrowse_io_obj.session_id,
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time(),
            is_voip_meeting=True)

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/save-voip-meeting-duration/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_GetMeetingSupportAgentAPI(self):
        logger.info('Testing test_GetMeetingSupportAgentAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time(),
            is_voip_meeting=True)

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/get-meeting-support-agents/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_LoadMapScriptAPI(self):
        logger.info('Testing test_LoadMapScriptAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        map_script = "https://maps.googleapis.com/maps/api/js?key=AIzaSyBAHTtk1lkVvIl1X_i7_1aIK9RCrhqGEpQ&libraries=places"
        json_string = json.dumps({})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/map-script/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['src'], map_script)

    def test_SaveCognoVidMeetingEndTimeAPI(self):
        logger.info('Testing test_SaveCognoVidMeetingEndTimeAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time(),
            is_voip_meeting=True)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
            "is_agent": "True",
            "is_invited_agent": "True",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/save-meeting-end-time/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)

        CobrowseVideoAuditTrail.objects.create(
            cobrowse_video=meeting_io)

        json_string = json.dumps({
            "meeting_id": str(meeting_io.meeting_id),
            "is_agent": "True",
            "is_invited_agent": "True",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/save-meeting-end-time/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_SaveCobrowseCollectedFormDataAPI(self):
        logger.info('Testing test_SaveCobrowseCollectedFormDataAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                     password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        meeting_end_datetime = datetime.now() + timedelta(hours=2)

        meeting_io = CobrowseVideoConferencing.objects.create(
            full_name="Test",
            mobile_number="9191919191",
            email_id="test@example.com",
            agent=cobrowse_agent,
            meeting_description="Meeting Description",
            meeting_start_date=datetime.now().date(),
            meeting_start_time=datetime.now().time(),
            meeting_end_time=meeting_end_datetime.time())

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
            "meeting_id": str(meeting_io.meeting_id),
            "form_id": str(cobrowse_form_obj.pk),
            "category_id": str(cobrowse_form_category_obj.pk),
            "collected_data": [{
                "id": str(cobrowse_form_element_obj.pk),
                "value": "Test Agent"
            }]
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/save-cobrowse-collected-form-data/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
