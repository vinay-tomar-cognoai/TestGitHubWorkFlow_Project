from __future__ import unicode_literals

from django.test import TestCase
from rest_framework.test import APIClient
from EasyChatApp.models import User
from EasyAssistApp.utils import delete_access_token_specific_static_file
from EasyAssistApp.models import CobrowseAgent, LiveChatCannedResponse, CobrowseAccessToken
from EasyAssistApp.encrypt import CustomEncrypt
import logging
import json

logger = logging.getLogger(__name__)


class ViewsCannedResponses(TestCase):

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

    def test_EditCannedResponseAPI(self):
        logger.info('Testing test_EditCannedResponseAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                        password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        access_token_obj = cobrowse_agent.get_access_token_obj()

        canned_response_obj = LiveChatCannedResponse.objects.create(keyword="hello",
                                                                    response="How may I help you?",
                                                                    agent=cobrowse_agent,
                                                                    access_token=access_token_obj)

        canned_response_pk = canned_response_obj.pk

        json_string = json.dumps({
            "keyword": "hello",
            "response": "How do I assist you?",
            "canned_response_pk": canned_response_pk})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/edit-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 200)

        canned_response_obj = LiveChatCannedResponse.objects.create(keyword="hello",
                                                                    response="How may I help you?",
                                                                    agent=cobrowse_agent,
                                                                    access_token=access_token_obj)

        canned_response_pk = canned_response_obj.pk

        json_string = json.dumps({
            "keyword": "he llo",
            "response": "How do I assist you?",
            "canned_response_pk": canned_response_pk})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/edit-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 400)

        canned_response_obj = LiveChatCannedResponse.objects.create(keyword="hello",
                                                                    response="How may I help you?",
                                                                    agent=cobrowse_agent,
                                                                    access_token=access_token_obj)

        canned_response_pk = canned_response_obj.pk

        json_string = json.dumps({
            "keyword": "@@@hello",
            "response": "How do I assist you?",
            "canned_response_pk": canned_response_pk})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/edit-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 400)

        cobrowse_agent.role = "agent"
        cobrowse_agent.save()

        canned_response_obj = LiveChatCannedResponse.objects.create(keyword="hello",
                                                                    response="How may I help you?",
                                                                    agent=cobrowse_agent,
                                                                    access_token=access_token_obj)

        canned_response_pk = canned_response_obj.pk

        json_string = json.dumps({
            "keyword": "hsello",
            "response": "How do I assist you?",
            "canned_response_pk": canned_response_pk})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/edit-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 500)

        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        canned_response_obj = LiveChatCannedResponse.objects.create(keyword="hello",
                                                                    response="How may I help you?",
                                                                    agent=cobrowse_agent,
                                                                    access_token=access_token_obj)

        canned_response_pk = canned_response_obj.pk

        json_string = json.dumps({
            "keyword": "hellohellohellohellohellohellohellohellohellohellohellohellohellohellohello",
            "response": "How do I assist you?",
            "canned_response_pk": canned_response_pk})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/edit-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 400)

        canned_response_obj = LiveChatCannedResponse.objects.create(keyword="hello",
                                                                    response="How may I help you?",
                                                                    agent=cobrowse_agent,
                                                                    access_token=access_token_obj)

        canned_response_pk = canned_response_obj.pk

        json_string = json.dumps({
            "keyword": "hello",
            "response": "<>()\"/;:^'",
            "canned_response_pk": canned_response_pk})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/edit-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 302)

    def test_CreateCannedResponseAPI(self):
        logger.info('Testing test_CreateCannedResponseAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                        password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        json_string = json.dumps({
            "keyword": "hello",
            "response": "How do I assist you?",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/create-new-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 200)

        json_string = json.dumps({
            "keyword": "hello llo",
            "response": "How do I assist you?"
        })

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/create-new-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 400)

        json_string = json.dumps({
            "keyword": "@@@hello",
            "response": "How do I assist you?"
        })

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/create-new-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 400)

        cobrowse_agent.role = "agent"
        cobrowse_agent.save()

        json_string = json.dumps({
            "keyword": "hello",
            "response": "How do I assist you?",
        })

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/create-new-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 500)

        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        json_string = json.dumps({
            "keyword": "hellohellohellohellohellohellohellohellohellohellohellohellohellohellohello",
            "response": "How do I assist you?"})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/create-new-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 400)

        access_token_obj = cobrowse_agent.get_access_token_obj()
        LiveChatCannedResponse.objects.create(keyword="hello",
                                                response="How may I help you?",
                                                agent=cobrowse_agent,
                                                access_token=access_token_obj)

        json_string = json.dumps({
            "keyword": "hellohellohellohellohellohellohellohellohellohellohellohellohellohellohello",
            "response": "<>()\"/;:^'"
        })

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/create-new-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 302)\


    def test_CreateAgentWithExcelAPI(self):
        logger.info('Testing test_CreateAgentWithExcelAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                        password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        json_string = json.dumps({
            "src": "/test/canned_response_template.xlsx",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/create-new-canned-response-excel/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 200)

        canned_response_obj = LiveChatCannedResponse.objects.filter(
            keyword="test", is_deleted=False)

        self.assertNotEqual(canned_response_obj, None)

        cobrowse_agent.role = "agent"
        cobrowse_agent.save()

        json_string = json.dumps({
            "src": "/test/canned_response_template.xlsx",
        })

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/create-new-canned-response-excel/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 500)

    def test_UpdateAgentCannedResponseAPI(self):
        logger.info('Testing test_UpdateAgentCannedResponseAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                        password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        access_token_obj = cobrowse_agent.get_access_token_obj()

        LiveChatCannedResponse.objects.create(keyword="test",
                                                response="How may I help you?",
                                                agent=cobrowse_agent,
                                                access_token=access_token_obj)

        json_string = json.dumps({
            "keyword": "test",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/agent/update-agent-used-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 200)

    def test_DeleteCannnedResponseAPI(self):
        logger.info('Testing test_DeleteCannnedResponseAPI...',
                    extra={'AppName': 'EasyAssist'})

        client = APIClient()
        client.login(username='testeasyassist',
                        password='testeasyassist')

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        cobrowse_agent.role = "admin"
        cobrowse_agent.save()

        access_token_obj = cobrowse_agent.get_access_token_obj()

        canned_response_obj = LiveChatCannedResponse.objects.create(keyword="hello",
                                                                    response="How may I help you?",
                                                                    agent=cobrowse_agent,
                                                                    access_token=access_token_obj)

        canned_response_pk = canned_response_obj.pk

        json_string = json.dumps(
            {"canned_response_pk_list": [str(canned_response_pk)]})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/delete-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 200)

        cobrowse_agent.role = "agent"
        cobrowse_agent.save()

        canned_response_obj = LiveChatCannedResponse.objects.create(keyword="hello",
                                                                    response="How may I help you?",
                                                                    agent=cobrowse_agent,
                                                                    access_token=access_token_obj)

        canned_response_pk = canned_response_obj.pk

        json_string = json.dumps(
            {"canned_response_pk_list": [canned_response_pk]})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/delete-canned-response/', json.dumps({'Request': json_string}),
                        content_type='application/json')
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status_code'], 500)
