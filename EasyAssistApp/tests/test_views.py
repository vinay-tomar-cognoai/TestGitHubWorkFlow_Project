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

    def test_CobrowseIOInitializeAPI(self):
        logger.info('Testing test_CobrowseIOInitializeAPI...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        access_token = cobrowse_agent.get_access_token_obj()

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        json_string = json.dumps({
            'name': 'Cogno AI',
            'mobile_number': '9512395123',
            'latitude': '19.123437644435743',
            'longitude': '72.89066562607881',
            'selected_language': -1,
            'selected_product_category': -1,
            'active_url': 'https://www.hdfccredila.com/apply-for-loan.html',
            'virtual_agent_code': 'None',
            'customer_id': 'None',
            'browsing_time_before_connect_click': '60',
            'meta_data': {'product_details': {'title': 'Apply for Education Loan | HDFC Credila',
                                              'description': 'Apply online for education loan at HDFC Credila from anywhere and get confirmed education loan before your admission.',
                                              'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                                              }},
            'is_request_from_greeting_bubble': True,
            'is_request_from_inactivity_popup': False,
            'is_request_from_exit_intent': False,
            'is_request_from_button': False,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/initialize/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        # domain is not whitelisted in accesstoken

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        request = client.post('/easy-assist/initialize/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        # normal request with all parameters

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        session_id = response['session_id']
        cobrowseio = \
            CobrowseIO.objects.filter(session_id=session_id).first()
        self.assertNotEqual(cobrowseio, None)

        access_token.allow_connect_with_virtual_agent_code = True
        access_token.save()

        supported_language = \
            LanguageSupport.objects.create(title='Hindi')
        product_category = \
            ProductCategory.objects.create(title='Car Loan')

        cobrowse_agent.supported_language.add(supported_language)
        cobrowse_agent.product_category.add(product_category)
        cobrowse_agent.save()

        json_string = json.dumps({
            'name': 'Cogno AI',
            'mobile_number': '9512395123',
            'latitude': '19.123437644435743',
            'longitude': '72.89066562607881',
            'selected_language': supported_language.pk,
            'selected_product_category': product_category.pk,
            'active_url': 'https://www.hdfccredila.com/apply-for-loan.html',
            'virtual_agent_code': cobrowse_agent.virtual_agent_code,
            'customer_id': 'None',
            'browsing_time_before_connect_click': '60',
            'meta_data': {'product_details': {'title': 'Apply for Education Loan | HDFC Credila',
                                              'description': 'Apply online for education loan at HDFC Credila from anywhere and get confirmed education loan before your admission.',
                                              'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                                              }},
            'is_request_from_greeting_bubble': True,
            'is_request_from_inactivity_popup': False,
            'is_request_from_exit_intent': False,
            'is_request_from_button': False,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/initialize/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        # virtual agent code is passed
        # support language and product category is passed

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        session_id = response['session_id']
        cobrowseio = \
            CobrowseIO.objects.filter(session_id=session_id).first()
        self.assertNotEqual(cobrowseio, None)
        self.assertNotEqual(cobrowseio.agent, None)

        self.assertEqual(cobrowseio.supported_language,
                         supported_language)
        self.assertEqual(cobrowseio.product_category, product_category)

    def test_SaveNonWorkingHourCurstomerDetailAPI(self):
        logger.info('Testing test_SaveNonWorkingHourCurstomerDetailAPI...', extra={
                    'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        access_token = cobrowse_agent.get_access_token_obj()

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        json_string = json.dumps({
            'name': 'Cogno AI',
            'mobile_number': '9512395123',
            'latitude': '19.123437644435743',
            'longitude': '72.89066562607881',
            'active_url': 'https://www.hdfccredila.com/apply-for-loan.html',
            'customer_id': 'None',
            "selected_language": -1,
            "selected_product_category": -1,
            'meta_data': {'product_details': {'title': 'Apply for Education Loan | HDFC Credila',
                                              'description': 'Apply online for education loan at HDFC Credila from anywhere and get confirmed education loan before your admission.',
                                              'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                                              }},
            'is_request_from_greeting_bubble': False,
            'is_request_from_inactivity_popup': False,
            'is_request_from_exit_intent': False,
            'is_request_from_button': False,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/save-non-working-hour-customer-details/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        # domain is not whitelisted in accesstoken

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        request = \
            client.post('/easy-assist/save-non-working-hour-customer-details/', json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        # normal request with all parameters

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertNotEqual(cobrowseio, None)
        self.assertEqual(cobrowseio.access_token, access_token)
        self.assertEqual(cobrowseio.session_archived_cause, 'FOLLOWUP')

    def test_CobrowseIOInitializeUsingDroplinkAPI(self):
        logger.info('Testing test_CobrowseIOInitializeUsingDroplinkAPI...', extra={
                    'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        access_token = cobrowse_agent.get_access_token_obj()

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        json_string = json.dumps({
            'drop_link_key': '12345678-1234-1234-1234-123456789012',
            'latitude': '19.123437644435743',
            'longitude': '72.89066562607881',
            'active_url': 'https://www.hdfccredila.com/apply-for-loan.html',
            'customer_id': 'None',
            'meta_data': {'product_details': {'title': 'Apply for Education Loan | HDFC Credila',
                                              'description': 'Apply online for education loan at HDFC Credila from anywhere and get confirmed education loan before your admission.',
                                              'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                                              }},
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/initialize-using-droplink/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        # domain is not whitelisted in accesstoken

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        request = client.post('/easy-assist/initialize-using-droplink/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        # normal request with wrong drop_link_key

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        cobrowse_drop_link_obj = CobrowseDropLink.objects.create(
            client_page_link='https://www.hdfccredila.com/apply-for-loan.html',
            agent=cobrowse_agent,
            customer_name='Customer Name',
            customer_mobile='9512395123',
            customer_email='testemail@allincall.in',
            generated_link='tinyurl.com/code',
        )

        json_string = json.dumps({
            'drop_link_key': str(cobrowse_drop_link_obj.key),
            'latitude': '19.123437644435743',
            'longitude': '72.89066562607881',
            'active_url': 'https://www.hdfccredila.com/apply-for-loan.html',
            'customer_id': 'None',
            'meta_data': {'product_details': {'title': 'Apply for Education Loan | HDFC Credila',
                                              'description': 'Apply online for education loan at HDFC Credila from anywhere and get confirmed education loan before your admission.',
                                              'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                                              }},
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/initialize-using-droplink/', json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        session_id = response['session_id']
        cobrowseio = \
            CobrowseIO.objects.filter(session_id=session_id).first()
        self.assertNotEqual(cobrowseio, None)
        self.assertEqual(cobrowseio.access_token, access_token)
        self.assertEqual(cobrowseio.is_droplink_lead, True)

        if cobrowseio.access_token.show_verification_code_modal \
                == False:
            self.assertEqual(cobrowseio.allow_agent_cobrowse, 'true')
        else:
            self.assertEqual(cobrowseio.agent_assistant_request_status,
                             True)
            self.assertEqual(cobrowseio.is_agent_request_for_cobrowsing,
                             True)
            self.assertEqual(len(cobrowseio.otp_validation), 4)

    def test_EasyAssistCustomerSetAPI(self):
        logger.info('Testing test_EasyAssistCustomerSetAPI...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        access_token = cobrowse_agent.get_access_token_obj()

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        json_string = json.dumps({
            'easyassist_customer_id': 'None',
            'full_name': 'Customer Name',
            'mobile_number': '9512395123',
            'active_url': 'https://www.hdfccredila.com/apply-for-loan.html',
            'meta_data': {'product_details': {'title': 'Apply for Education Loan | HDFC Credila',
                                              'description': 'Apply online for education loan at HDFC Credila from anywhere and get confirmed education loan before your admission.',
                                              'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                                              }},
            'is_request_from_greeting_bubble': True,
            'is_request_from_inactivity_popup': False,
            'is_request_from_exit_intent': False,
            'is_request_from_button': False,

        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/set-easyassist-customer/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        # domain is not whitelisted in accesstoken

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        request = client.post('/easy-assist/set-easyassist-customer/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        customer_id = response['customer_id']
        easyassist_customer = \
            EasyAssistCustomer.objects.filter(customer_id=customer_id).first()
        self.assertNotEqual(easyassist_customer, None)
        self.assertEqual(easyassist_customer.access_token, access_token)

    def test_HighlightCheckCobrowseIOAPI(self):
        logger.info('Testing test_HighlightCheckCobrowseIOAPI...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.first_name = 'testeasyassist'
        cobrowse_agent.location = 'Allincall, Mumbai'
        cobrowse_agent.save()

        access_token = cobrowse_agent.get_access_token_obj()
        cobrowseio = CobrowseIO.objects.create()
        custom_encrypt_obj = CustomEncrypt()

        http_authorization = 'Bearer ' \
            + custom_encrypt_obj.encrypt(str(cobrowseio.session_id) + ':' + str(int(time.time())))

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        json_string = json.dumps({
            'id': str(cobrowseio.session_id),
            'drop_off_meta_data': {
                'product_details': {
                    'title': 'Apply for Education Loan | HDFC Credila',
                    'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                }
            }
        })
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/highlight/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        self.assertEqual(request.status_code, 401)

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key),
                           HTTP_AUTHORIZATION=http_authorization)

        request = client.post('/easy-assist/highlight/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        cobrowseio.agent = cobrowse_agent
        cobrowseio.access_token = access_token
        cobrowseio.last_update_datetime = datetime.now()
        cobrowseio.save()

        request = client.post('/easy-assist/highlight/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['is_agent_connected'], False)
        self.assertEqual(response['agent_name'], 'testeasyassist')
        self.assertEqual(response['session_ended_by_agent'], False)
        self.assertEqual(response['agent_assistant_request_status'],
                         False)
        self.assertEqual(response['allow_agent_cobrowse'], None)
        self.assertEqual(response['agent_meeting_request_status'],
                         False)
        self.assertEqual(response['allow_agent_meeting'], None)
        self.assertEqual(response['is_lead'], False)
        self.assertEqual(response['is_archived'], False)
        self.assertEqual(response['is_session_closed'], False)

        cobrowseio.is_agent_connected = True
        cobrowseio.last_agent_update_datetime = datetime.now()
        cobrowseio.agent_assistant_request_status = True
        cobrowseio.allow_agent_cobrowse = 'true'
        cobrowseio.agent_meeting_request_status = True
        cobrowseio.allow_agent_meeting = 'true'
        cobrowseio.save()

        request = client.post('/easy-assist/highlight/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['is_agent_connected'], True)
        self.assertEqual(response['agent_name'], 'testeasyassist')
        self.assertEqual(response['session_ended_by_agent'], False)
        self.assertEqual(response['agent_assistant_request_status'],
                         True)
        self.assertEqual(response['allow_agent_cobrowse'], 'true')
        self.assertEqual(response['agent_meeting_request_status'], True)
        self.assertEqual(response['allow_agent_meeting'], 'true')
        self.assertEqual(response['is_lead'], False)
        self.assertEqual(response['is_archived'], False)
        self.assertEqual(response['is_session_closed'], False)

        cobrowseio.last_agent_update_datetime = datetime.now() \
            - timedelta(seconds=AGENT_DISCONNECTED_TIME_OUT + 1)
        cobrowseio.last_update_datetime = datetime.now() \
            - timedelta(seconds=access_token.archive_on_common_inactivity_threshold * 60 + 1)
        cobrowseio.save()

        request = client.post('/easy-assist/highlight/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['is_agent_connected'], False)
        self.assertEqual(response['agent_name'], 'testeasyassist')
        self.assertEqual(response['session_ended_by_agent'], False)
        self.assertEqual(response['agent_assistant_request_status'],
                         True)
        self.assertEqual(response['allow_agent_cobrowse'], 'true')
        self.assertEqual(response['agent_meeting_request_status'], True)
        self.assertEqual(response['allow_agent_meeting'], 'true')
        self.assertEqual(response['is_lead'], False)
        self.assertEqual(response['is_archived'], False)
        self.assertEqual(response['is_session_closed'], True)

        cobrowseio.last_update_datetime = datetime.now() \
            - timedelta(seconds=access_token.auto_archive_cobrowsing_session_timer * 60 + 1)
        cobrowseio.save()

        request = client.post('/easy-assist/highlight/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        cobrowseio = CobrowseIO.objects.all().first()

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['is_agent_connected'], False)
        self.assertEqual(response['agent_name'], 'testeasyassist')
        self.assertEqual(response['session_ended_by_agent'], False)
        self.assertEqual(response['agent_assistant_request_status'],
                         True)
        self.assertEqual(response['allow_agent_cobrowse'], 'true')
        self.assertEqual(response['agent_meeting_request_status'], True)
        self.assertEqual(response['allow_agent_meeting'], 'true')
        self.assertEqual(response['is_lead'], False)
        self.assertEqual(response['is_archived'], True)
        self.assertEqual(response['is_session_closed'], True)
        self.assertEqual(cobrowseio.session_archived_cause, 'UNATTENDED'
                         )

    def test_CobrowseIOCaptureLeadAPI(self):
        logger.info('Testing test_CobrowseIOCaptureLeadAPI...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        product_1 = ProductCategory.objects.create(title='Car Loan One')
        cobrowse_agent.product_category.add(product_1)

        product_2 = ProductCategory.objects.create(title='Car Loan Two')
        cobrowse_agent.product_category.add(product_2)

        cobrowse_agent.save()

        access_token = cobrowse_agent.get_access_token_obj()
        cobrowseio = CobrowseIO.objects.create()
        custom_encrypt_obj = CustomEncrypt()

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        normal_primary_value_list = [{
            'value': '9512395123',
            'label': 'Mobile Number'},
            {'value': 'test@gmail.com',
             'label': 'Email Id'}]
        easyassist_sync_data = [{'value': '9512395123',
                                 'sync_type': 'primary',
                                 'name': 'Mobile Number'},
                                {'value': 'test@gmail.com',
                                 'sync_type': 'primary',
                                 'name': 'Email Id'}]
        json_string = json.dumps({
            'primary_value_list': normal_primary_value_list,
            'session_id': 'None',
            'selected_product_category': product_1.title,
            'meta_data': {'product_details': {'title': 'Apply for Education Loan | HDFC Credila',
                                              'description': 'Apply online for education loan at HDFC Credila from anywhere and get confirmed education loan before your admission.',
                                              'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                                              },
                          'easyassist_sync_data': easyassist_sync_data},
        })
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/easy-assist/capture-lead/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        self.assertEqual(request.status_code, 401)
        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()
        request = client.post('/easy-assist/capture-lead/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['cobrowsing_new_sesion'], True)
        session_id = response['session_id']
        cobrowseio = \
            CobrowseIO.objects.filter(session_id=session_id).first()
        self.assertNotEqual(cobrowseio, None)
        self.assertEqual(cobrowseio.access_token, access_token)
        self.assertEqual(product_1, cobrowseio.product_category)

        primary_value_list = []
        for primary_id_obj in normal_primary_value_list:
            primary_value = primary_id_obj['value']
            primary_value = primary_value.strip().lower()
            primary_value = \
                hashlib.md5(primary_value.encode()).hexdigest()
            primary_value_list.append(primary_value)
        cobrowseio_primary_value_list = []
        for captured_lead in cobrowseio.captured_lead.all():
            cobrowseio_primary_value_list.append(captured_lead.primary_value)
        for primary_value in primary_value_list:
            self.assertIn(primary_value, cobrowseio_primary_value_list)

        normal_primary_value_list = [{'value': '9512395456',
                                     'label': 'Mobile Number'},
                                     {'value': 'test2@gmail.com',
                                      'label': 'Email Id'}]
        easyassist_sync_data = [{'value': '9512395456',
                                 'sync_type': 'primary',
                                 'name': 'Mobile Number'},
                                {'value': 'test2@gmail.com',
                                 'sync_type': 'primary',
                                 'name': 'Email Id'}]
        json_string = json.dumps({
            'primary_value_list': normal_primary_value_list,
            'session_id': str(cobrowseio.session_id),
            'selected_product_category': product_1.title,
            'meta_data': {'product_details': {'title': 'Apply for Education Loan | HDFC Credila',
                                              'description': 'Apply online for education loan at HDFC Credila from anywhere and get confirmed education loan before your admission.',
                                              'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                                              },
                          'easyassist_sync_data': easyassist_sync_data},
        })
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/easy-assist/capture-lead/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')
        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))
        self.assertEqual(response['session_id'],
                         str(cobrowseio.session_id))
        self.assertEqual(response['cobrowsing_new_sesion'], False)
        session_id = response['session_id']
        cobrowseio = \
            CobrowseIO.objects.filter(session_id=session_id).first()
        self.assertNotEqual(cobrowseio, None)
        self.assertEqual(cobrowseio.access_token, access_token)
        self.assertEqual(product_1, cobrowseio.product_category)
        self.assertNotEqual(product_2, cobrowseio.product_category)
        cobrowseio_primary_value_list = []
        for captured_lead in cobrowseio.captured_lead.all():
            cobrowseio_primary_value_list.append(captured_lead.primary_value)
        for primary_value in primary_value_list:
            self.assertNotIn(primary_value,
                             cobrowseio_primary_value_list)

        primary_value_list = []
        for primary_id_obj in normal_primary_value_list:
            primary_value = primary_id_obj['value']
            primary_value = primary_value.strip().lower()
            primary_value = \
                hashlib.md5(primary_value.encode()).hexdigest()
            primary_value_list.append(primary_value)

        for primary_value in primary_value_list:
            self.assertIn(primary_value, cobrowseio_primary_value_list)

        meta_data = cobrowseio.meta_data
        meta_data = json.loads(custom_encrypt_obj.decrypt(meta_data))
        easyassist_sync_data_saved = meta_data['easyassist_sync_data']
        self.assertEqual(easyassist_sync_data_saved,
                         easyassist_sync_data)

    def test_UpdateAgentAssistantRequestAPI(self):
        logger.info('Testing test_UpdateAgentAssistantRequestAPI...',
                    extra={'AppName': 'EasyAssist'})

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

        json_string = json.dumps({'id': str(cobrowseio.session_id),
                                  'otp': '1235', 'status': 'true'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/update-agent-assistant-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        self.assertEqual(request.status_code, 401)

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key),
                           HTTP_AUTHORIZATION=http_authorization)

        request = \
            client.post('/easy-assist/update-agent-assistant-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        cobrowseio.access_token = access_token
        cobrowseio.otp_validation = '1234'
        cobrowseio.agent_assistant_request_status = True
        cobrowseio.save()

        # Invalid OTP status true

        json_string = json.dumps({'id': str(cobrowseio.session_id),
                                  'otp': '1235', 'status': 'true'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/update-agent-assistant-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 101)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.consent_allow_count, 0)
        self.assertEqual(cobrowseio.consent_cancel_count, 0)
        self.assertEqual(cobrowseio.allow_agent_cobrowse, None)
        self.assertEqual(cobrowseio.agent_assistant_request_status,
                         True)

        # Invalid OTP status false

        json_string = json.dumps({'id': str(cobrowseio.session_id),
                                  'otp': '1235', 'status': 'false'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/update-agent-assistant-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['cobrowsing_allowed'], 'false')
        self.assertEqual(response['allow_screen_sharing_cobrowse'],
                         False)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.consent_allow_count, 0)
        self.assertEqual(cobrowseio.consent_cancel_count, 1)
        self.assertEqual(cobrowseio.allow_agent_cobrowse, 'false')
        self.assertEqual(cobrowseio.agent_assistant_request_status,
                         False)

        # Valid OTP status false

        json_string = json.dumps({'id': str(cobrowseio.session_id),
                                  'otp': '1234', 'status': 'false'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/update-agent-assistant-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['cobrowsing_allowed'], 'false')
        self.assertEqual(response['allow_screen_sharing_cobrowse'],
                         False)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.consent_allow_count, 0)
        self.assertEqual(cobrowseio.consent_cancel_count, 2)
        self.assertEqual(cobrowseio.allow_agent_cobrowse, 'false')

        # Valid OTP status true

        json_string = json.dumps({'id': str(cobrowseio.session_id),
                                  'otp': '1234', 'status': 'true'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/update-agent-assistant-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['cobrowsing_allowed'], 'true')
        self.assertEqual(response['allow_screen_sharing_cobrowse'],
                         False)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.consent_allow_count, 1)
        self.assertEqual(cobrowseio.consent_cancel_count, 2)
        self.assertEqual(cobrowseio.allow_agent_cobrowse, 'true')

        access_token.allow_screen_sharing_cobrowse = True
        access_token.save()

        # Valid OTP status true

        json_string = json.dumps({'id': str(cobrowseio.session_id),
                                  'otp': '1234', 'status': 'true'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/update-agent-assistant-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['cobrowsing_allowed'], 'true')
        self.assertEqual(response['allow_screen_sharing_cobrowse'],
                         True)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.consent_allow_count, 2)
        self.assertEqual(cobrowseio.consent_cancel_count, 2)
        self.assertEqual(cobrowseio.allow_agent_cobrowse, 'true')

        access_token.enable_verification_code_popup = False
        access_token.save()
        cobrowseio.otp_validation = None
        cobrowseio.save()

        json_string = json.dumps({'id': str(cobrowseio.session_id),
                                  'otp': 'None', 'status': 'true'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/update-agent-assistant-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['cobrowsing_allowed'], 'true')
        self.assertEqual(response['allow_screen_sharing_cobrowse'],
                         True)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.consent_allow_count, 3)
        self.assertEqual(cobrowseio.consent_cancel_count, 2)
        self.assertEqual(cobrowseio.allow_agent_cobrowse, 'true')

        json_string = json.dumps({'id': str(cobrowseio.session_id),
                                  'otp': 'None', 'status': 'false'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/update-agent-assistant-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['cobrowsing_allowed'], 'false')
        self.assertEqual(response['allow_screen_sharing_cobrowse'],
                         True)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.consent_allow_count, 3)
        self.assertEqual(cobrowseio.consent_cancel_count, 3)
        self.assertEqual(cobrowseio.allow_agent_cobrowse, 'false')

    def test_UpdateAgentMeetingRequestAPI(self):
        logger.info('Testing test_UpdateAgentMeetingRequestAPI...',
                    extra={'AppName': 'EasyAssist'})

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

        json_string = json.dumps({'id': str(cobrowseio.session_id),
                                  'status': 'true'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/update-agent-meeting-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        self.assertEqual(request.status_code, 401)

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key),
                           HTTP_AUTHORIZATION=http_authorization)

        request = \
            client.post('/easy-assist/update-agent-meeting-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        cobrowseio.access_token = access_token
        cobrowseio.agent_meeting_request_status = True
        cobrowseio.save()

        json_string = json.dumps({'id': str(cobrowseio.session_id),
                                  'status': 'false'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/update-agent-meeting-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['meeting_allowed'], 'false')

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.allow_agent_meeting, 'false')
        self.assertEqual(cobrowseio.agent_meeting_request_status, False)

        json_string = json.dumps({'id': str(cobrowseio.session_id),
                                  'status': 'true'})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/update-agent-meeting-request/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['meeting_allowed'], 'true')

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.allow_agent_meeting, 'true')
        self.assertEqual(cobrowseio.agent_meeting_request_status, False)

    def test_SubmitClientFeedbackAPI(self):
        logger.info('Testing test_SubmitClientFeedbackAPI...',
                    extra={'AppName': 'EasyAssist'})

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

        json_string = json.dumps({
            'session_id': str(cobrowseio.session_id),
            'rating': '10', 'feedback': 'Great Session',
            'drop_off_meta_data': {
                'product_details': {
                    'title': 'Apply for Education Loan | HDFC Credila',
                    'url': 'https://www.hdfccredila.com/apply-for-loan.html'
                }
            }
        })
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/submit-client-feedback/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        self.assertEqual(request.status_code, 401)

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key),
                           HTTP_AUTHORIZATION=http_authorization)

        request = client.post('/easy-assist/submit-client-feedback/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        cobrowseio.access_token = access_token
        cobrowseio.save()

        request = client.post('/easy-assist/submit-client-feedback/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowseio = CobrowseIO.objects.all().first()
        self.assertEqual(cobrowseio.agent_rating, 10)
        self.assertEqual(cobrowseio.client_comments, 'Great Session')
        self.assertEqual(cobrowseio.session_archived_cause,
                         'CLIENT_ENDED')

        audit_trail = \
            SystemAuditTrail.objects.filter(category='session_closed',
                                            cobrowse_io=cobrowseio,
                                            cobrowse_access_token=access_token).first()
        self.assertNotEqual(audit_trail, None)

    def test_SaveSystemAuditTrailAPI(self):
        logger.info('Testing test_SaveSystemAuditTrailAPI...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.save()

        access_token = cobrowse_agent.get_access_token_obj()
        cobrowseio = \
            CobrowseIO.objects.create(access_token=access_token)
        custom_encrypt_obj = CustomEncrypt()

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))
        client.login(username='testeasyassist',
                     password='testeasyassist')

        json_string = json.dumps({'category': 'category',
                                  'description': 'description',
                                  'session_id': str(cobrowseio.session_id)})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/save-system-audit/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        audit_trail = \
            SystemAuditTrail.objects.filter(category='category',
                                            description='description', cobrowse_io=cobrowseio,
                                            cobrowse_access_token=access_token,
                                            sender=cobrowse_agent).first()
        self.assertNotEqual(audit_trail, None)

    def test_GetClientCobrowsingChatHistoryAPI(self):
        logger.info('Testing test_GetClientCobrowsingChatHistoryAPI...', extra={
                    'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.save()

        access_token = cobrowse_agent.get_access_token_obj()
        cobrowseio = CobrowseIO.objects.create(full_name='Client Name')
        custom_encrypt_obj = CustomEncrypt()

        http_authorization = 'Bearer ' \
            + custom_encrypt_obj.encrypt(str(cobrowseio.session_id) + ':' + str(int(time.time())))

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        json_string = \
            json.dumps({'session_id': str(cobrowseio.session_id)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/get-cobrowsing-chat-history/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        self.assertEqual(request.status_code, 401)

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key),
                           HTTP_AUTHORIZATION=http_authorization)

        request = \
            client.post('/easy-assist/get-cobrowsing-chat-history/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        cobrowseio.access_token = access_token
        cobrowseio.save()

        CobrowseChatHistory.objects.create(cobrowse_io=cobrowseio,
                                           sender=cobrowse_agent, message='message',
                                           attachment_file_name='attachment_file_name',
                                           attachment='attachment')
        CobrowseChatHistory.objects.create(cobrowse_io=cobrowseio,
                                           sender=None, message='message',
                                           attachment_file_name='attachment_file_name',
                                           attachment='attachment')

        request = \
            client.post('/easy-assist/get-cobrowsing-chat-history/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(len(response['chat_history']), 2)
        self.assertEqual(response['client_name'], cobrowseio.full_name)

    def test_MarkLeadAsConvertedAPI(self):
        logger.info('Testing test_MarkLeadAsConvertedAPI...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.save()

        access_token = cobrowse_agent.get_access_token_obj()
        cobrowseio = CobrowseIO.objects.create(full_name='Client Name')
        custom_encrypt_obj = CustomEncrypt()

        http_authorization = 'Bearer ' \
            + custom_encrypt_obj.encrypt(str(cobrowseio.session_id) + ':' + str(int(time.time())))

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        json_string = \
            json.dumps({'session_id': str(cobrowseio.session_id),
                        'active_url': 'https://www.hdfccredila.com/apply-for-loan.html'
                        })
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/mark-lead-as-converted/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        self.assertEqual(request.status_code, 401)

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key),
                           HTTP_AUTHORIZATION=http_authorization)

        request = client.post('/easy-assist/mark-lead-as-converted/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        request = client.post('/easy-assist/mark-lead-as-converted/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        cobrowseio = CobrowseIO.objects.all().first()

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(cobrowseio.is_helpful, True)

    def test_AvailableAgentListAPI(self):
        logger.info('Testing test_AvailableAgentListAPI...',
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

        supervisor2_user = User.objects.create(username='supervisor2',
                                               password='supervisor2supervisor2')
        supervisor2_agent = \
            CobrowseAgent.objects.create(user=supervisor2_user,
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

        agent6_user = User.objects.create(username='agent6',
                                          password='agent6agent6')
        agent6_agent = CobrowseAgent.objects.create(user=agent6_user,
                                                    role='agent', is_active=True)

        admin_agent.agents.add(supervisor1_agent)
        admin_agent.agents.add(agent1_agent)
        admin_agent.agents.add(agent4_agent)
        admin_agent.save()
        supervisor1_agent.agents.add(agent2_agent)
        supervisor1_agent.agents.add(agent3_agent)
        supervisor1_agent.agents.add(agent5_agent)
        supervisor1_agent.save()
        supervisor2_agent.agents.add(agent6_agent)
        supervisor2_agent.save()

        access_token = admin_agent.get_access_token_obj()
        custom_encrypt_obj = CustomEncrypt()

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        json_string = \
            json.dumps({'access_token': str(access_token.key)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/available-agent-list/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['available_agent_count'], 5)
        self.assertEqual(response['agent_available'], True)

        supervisor1_agent.is_cobrowsing_active = True
        supervisor1_agent.save()
        agent1_agent.is_cobrowsing_active = True
        agent1_agent.save()
        agent2_agent.is_cobrowsing_active = True
        agent2_agent.save()

        request = client.post('/easy-assist/available-agent-list/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['available_agent_count'], 2)
        self.assertEqual(response['agent_available'], True)

        admin_agent.is_active = False
        admin_agent.save()
        agent3_agent.is_active = False
        agent3_agent.save()

        request = client.post('/easy-assist/available-agent-list/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['available_agent_count'], 0)
        self.assertEqual(response['agent_available'], False)

    def test_ClientAuthenticationAPI(self):
        logger.info('Testing test_ClientAuthenticationAPI...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.save()

        access_token = cobrowse_agent.get_access_token_obj()
        custom_encrypt_obj = CustomEncrypt()

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com')

        json_string = json.dumps({'key': str(access_token.key)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/easy-assist/client-authentication/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 500)

        access_token.whitelisted_domain = \
            'www.hdfccredila.com,xyz.com, abc.com   , computer.in'
        access_token.save()

        request = client.post('/easy-assist/client-authentication/',
                              json.dumps({'Request': json_string}),
                              content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_FetchConnectedAgentDetailsAPI(self):
        logger.info('Testing test_FetchConnectedAgentDetailsAPI...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')
        cobrowse_agent.first_name = 'testeasyassist'
        cobrowse_agent.location = 'Allincall, Mumbai'
        cobrowse_agent.agent_profile_pic_source = "web"
        cobrowse_agent.agent_code = "1235"
        cobrowse_agent.save()

        access_token = cobrowse_agent.get_access_token_obj()
        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()
        cobrowseio = CobrowseIO.objects.create()
        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        custom_encrypt_obj = CustomEncrypt()

        http_authorization = 'Bearer ' \
            + custom_encrypt_obj.encrypt(str(cobrowseio.session_id) + ':' + str(int(time.time())))

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        json_string = json.dumps({'id': str(cobrowseio.session_id)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/fetch-connected-agent-details/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = ''
        access_token.save()
        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key),
                           HTTP_AUTHORIZATION=http_authorization)

        request = \
            client.post('/easy-assist/fetch-connected-agent-details/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.display_agent_profile = True
        access_token.show_agent_email = True
        access_token.show_agent_details_modal = True
        access_token.is_agent_details_api_enabled = True
        access_token.save()

        cobrowseio.access_token = access_token
        cobrowseio.agent = cobrowse_agent
        cobrowseio.save()

        json_string = json.dumps({'id': str(cobrowseio.session_id)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/fetch-connected-agent-details/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['agent_name'], 'testeasyassist')
        self.assertEqual(response['agent_email'], 'testeasyassist')
        self.assertEqual(response["display_agent_profile"], True)
        self.assertEqual(response["show_agent_details_modal"], True)
        self.assertEqual(response["show_agent_email"], True)
        self.assertEqual(response["agent_profile_pic_source"], "web")

        access_token.is_agent_details_api_enabled = False
        access_token.save()

        request = \
            client.post('/easy-assist/fetch-connected-agent-details/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response["agent_additional_details_response"], None)

    def test_CustomerRequestCobrowsingMeetingAPI(self):
        logger.info('Testing test_CustomerRequestCobrowsingMeetingAPI...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        access_token = cobrowse_agent.get_access_token_obj()
        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()
        cobrowseio = CobrowseIO.objects.create()

        custom_encrypt_obj = CustomEncrypt()

        http_authorization = 'Bearer ' \
            + custom_encrypt_obj.encrypt(str(cobrowseio.session_id) + ':' + str(int(time.time())))

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        json_string = json.dumps({'id': str(cobrowseio.session_id)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/customer/request-assist-meeting/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = ''
        access_token.save()
        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key),
                           HTTP_AUTHORIZATION=http_authorization)

        request = \
            client.post('/easy-assist/customer/request-assist-meeting/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        cobrowseio.access_token = access_token
        cobrowseio.agent = cobrowse_agent
        cobrowseio.save()

        json_string = json.dumps({'id': str(cobrowseio.session_id)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/customer/request-assist-meeting/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.get_access_token_obj().enable_voip_calling = True
        cobrowse_agent.save()

        json_string = json.dumps({'id': str(cobrowseio.session_id)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/customer/request-assist-meeting/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

        cobrowse_agent.get_access_token_obj().enable_voip_calling = False
        cobrowse_agent.get_access_token_obj().enable_voip_with_video_calling = True
        cobrowse_agent.save()

        json_string = json.dumps({'id': str(cobrowseio.session_id)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/customer/request-assist-meeting/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)

    def test_CheckClientMeetingStatusAPI(self):
        logger.info('Testing test_CheckClientMeetingStatusAPI...',
                    extra={'AppName': 'EasyAssist'})

        cobrowse_agent = \
            CobrowseAgent.objects.get(user__username='testeasyassist')

        access_token = cobrowse_agent.get_access_token_obj()
        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()
        cobrowseio = CobrowseIO.objects.create()

        custom_encrypt_obj = CustomEncrypt()

        http_authorization = 'Bearer ' \
            + custom_encrypt_obj.encrypt(str(cobrowseio.session_id) + ':' + str(int(time.time())))

        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key))

        json_string = json.dumps({'id': str(cobrowseio.session_id)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/client/check-meeting-status/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = ''
        access_token.save()
        client = APIClient(HTTP_ORIGIN='https://www.hdfccredila.com',
                           HTTP_X_ACCESSTOKEN=str(access_token.key),
                           HTTP_AUTHORIZATION=http_authorization)

        request = \
            client.post('/easy-assist/client/check-meeting-status/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        self.assertEqual(request.status_code, 401)

        access_token.whitelisted_domain = 'www.hdfccredila.com'
        access_token.save()

        cobrowseio.access_token = access_token
        cobrowseio.agent = cobrowse_agent
        cobrowseio.save()

        json_string = json.dumps({'id': str(cobrowseio.session_id)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/client/check-meeting-status/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 301)
        self.assertEqual(response['is_agent_answer'], False)
        self.assertEqual(response['is_meeting_allowed'], False)

        cobrowseio.allow_customer_meeting = 'true'
        cobrowseio.save()

        json_string = json.dumps({'id': str(cobrowseio.session_id)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/client/check-meeting-status/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['is_agent_answer'], True)
        self.assertEqual(response['is_meeting_allowed'], True)

        cobrowseio.allow_customer_meeting = 'false'
        cobrowseio.save()

        json_string = json.dumps({'id': str(cobrowseio.session_id)})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = \
            client.post('/easy-assist/client/check-meeting-status/',
                        json.dumps({'Request': json_string}),
                        content_type='application/json')

        response = \
            json.loads(custom_encrypt_obj.decrypt(request.data['Response']))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['is_agent_answer'], True)
        self.assertEqual(response['is_meeting_allowed'], False)
