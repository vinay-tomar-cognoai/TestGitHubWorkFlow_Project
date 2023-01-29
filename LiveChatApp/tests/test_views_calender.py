# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from rest_framework.test import APIClient
from EasyChatApp.models import Bot, User, MISDashboard
from LiveChatApp.models import LiveChatUser, LiveChatCustomer, CannedResponse, LiveChatConfig, LiveChatCategory, LiveChatBlackListKeyword
from LiveChatApp.utils import get_time, is_agent_live
from LiveChatApp.utils_custom_encryption import *
import logging
import json
import random
import execjs
import base64
from datetime import datetime
from Crypto import Random
from Crypto.Cipher import AES
logger = logging.getLogger(__name__)

"""
Test of All functions which are dependent on models
"""


class UtilsSomeFunctionsWithModels(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'LiveChat'})

        LiveChatConfig.objects.create(max_customer_count=110)
        category_obj = LiveChatCategory.objects.create(title="Others")
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        MISDashboard.objects.create(
            user_id="1", bot=bot_obj, message_received="hi", bot_response="how may I assist you?")
        MISDashboard.objects.create(
            user_id="2", bot=bot_obj, message_received="hi", bot_response="how may I assist you?")
        MISDashboard.objects.create(
            user_id="4", bot=bot_obj, message_received="hi", bot_response="how may I assist you?")
        MISDashboard.objects.create(
            user_id="4", bot=bot_obj, message_received="Hi", bot_response="hello")
        easychat_user = User.objects.create(
            role="1", status="1", username="test", password="test")
        livechat_agent = LiveChatUser.objects.create(
            status="1", user=easychat_user, is_online=True, is_allow_toggle=True)
        livechat_agent.category.add(category_obj)
        livechat_agent.bots.add(bot_obj)

        livechat_agent2 = LiveChatUser.objects.create(status="2", user=User.objects.create(
            role="1", status="1", username="test12345", password="test12345", first_name="allincall"), is_online=True)
        livechat_agent.agents.add(livechat_agent2)
        livechat_agent.save()
        livechat_agent1 = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="test1234", password="test1234", first_name="allincall"), is_online=True)
        livechat_agent2.agents.add(livechat_agent1)
        livechat_agent2.bots.add(bot_obj)
        livechat_agent2.save()
        livechat_agent1.category.add(category_obj)
        livechat_agent1.bots.add(bot_obj)
        livechat_agent1.save()

    """
    function tested: CreateWorkingHoursAPI
    input queries:
        month:
        year:
        start_time:
        end_time:
        mode:
        days_list:
    expected output:
        status: 200 // SUCCESS
        status: 300 // Already exist
        status: 500 // Error
    """

    def test_CreateWorkingHoursAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        json_string = json.dumps({
            'month': 1,
            'year': 2020,
            'start_time': '11:30 AM',
            'end_time': '04:00 PM',
            'mode': '1',
            'days_list': ['Sunday']
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-working-hours/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        json_string = json.dumps({
            'month': 1,
            'year': 2020,
            'start_time': '11:30 AM',
            'end_time': '04:00 PM',
            'mode': '1',
            'days_list': ['Sunday']
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-working-hours/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        json_string = json.dumps({
            'month': 1,
            'year': 2021,
            'start_time': '11:30 AM',
            'end_time': '04:00 PM',
            'mode': '2',
            'days_list': ['Sunday']
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-working-hours/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        json_string = json.dumps({
            'month': 1,
            'year': 2021,
            'start_time': '11:30 AM',
            'end_time': '04:00 PM',
            'mode': '3',
            'days_list': ['Sunday']
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-working-hours/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        client.logout()
        client.login(username="test12345", password="test12345")

        json_string = json.dumps({
            'month': 1,
            'year': 2021,
            'start_time': '11:30 AM',
            'end_time': '04:00 PM',
            'mode': '2',
            'days_list': ['Sunday']
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-working-hours/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")

        json_string = json.dumps({
            'month': 1,
            'year': 2021,
            'start_time': '11:30 AM',
            'end_time': '04:00 PM',
            'mode': '3',
            'days_list': ['Sunday']
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-working-hours/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")

        client.logout()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({
            'month': 1,
            'year': 2021,
            'start_time': '11:30 AM',
            'end_time': '04:00 PM',
            'mode': '2',
            'days_list': ['Sunday']
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-working-hours/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")

        json_string = json.dumps({
            'month': 1,
            'year': 2021,
            'start_time': '11:30 AM',
            'end_time': '04:00 PM',
            'mode': '3',
            'days_list': ['Sunday']
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-working-hours/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")

    """
    function tested: EditCalenderEventAPI
    input queries:
        pk: pk of calender event.
        selected_event:
        start_time:
        end_time:
        description:
        auto_response:
    expected output:
        status: 200 // SUCCESS
        status: 500 // Error
    """

    def test_EditCalenderEventAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        # admin can create and edit the calender
        json_string = json.dumps({
            'holiday_date_array': ['2022-12-12'],
            'description': 'Testing',
            'auto_response': 'This is testing.'
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-holiday-calender/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        json_string = json.dumps({
            'pk': 1,
            'selected_event': "2",
            'start_time': '',
            'end_time': '',
            'description': 'AllinCall',
            'auto_response': 'AllinCall testing'
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-calender-event/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        client.logout()
        # supervisor cannot edit calender
        client.login(username="test12345", password="test12345")

        json_string = json.dumps({
            'pk': 1,
            'selected_event': "2",
            'start_time': '',
            'end_time': '',
            'description': 'AllinCallSupervisor',
            'auto_response': 'AllinCall testing'
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-calender-event/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")

        client.logout()
        # agent cannot edit calender
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({
            'holiday_date_array': ['2022-12-12'],
            'description': 'Testing',
            'auto_response': 'This is testing.'
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-holiday-calender/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")

    """
    function tested: DeleteCalenderEventAPI
    input queries:
        pk: pk of calender event.
    expected output:
        status: 200 // SUCCESS
        status: 500 // Error
    """
    # This API is not in use as of now as delete calendar event is not allowed/permissible now
    # def test_DeleteCalenderEventAPI(self):

    #     client = APIClient()
    #     # Admin creates a holiday calender and then deletes
    #     # status 200
    #     client.login(username="test", password="test")

    #     json_string = json.dumps({
    #         'holiday_date': '1212-12-12',
    #         'description': 'Testing',
    #         'auto_response': 'This is testing.'
    #     })
    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post('/livechat/add-holiday-calender/', json.dumps(
    #         {'json_string': json_string}), content_type='application/json')

    #     self.assertEqual(request.status_code, 200)
    #     response = custom_encrypt_obj.decrypt(request.data)
    #     response = json.loads(response)
    #     self.assertEqual(response["status_code"], "200")

    #     json_string = json.dumps({
    #         'pk': 1,
    #     })
    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post('/livechat/delete-calender-event/', json.dumps(
    #         {'json_string': json_string}), content_type='application/json')

    #     self.assertEqual(request.status_code, 200)
    #     response = custom_encrypt_obj.decrypt(request.data)
    #     response = json.loads(response)
    #     self.assertEqual(response["status_code"], "200")

    #     # Admin creates a holiday calender and then supervisor tries to delete it, error 500
    #     json_string = json.dumps({
    #         'holiday_date': '1212-12-12',
    #         'description': 'Testing',
    #         'auto_response': 'This is testing.'
    #     })
    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post('/livechat/add-holiday-calender/', json.dumps(
    #         {'json_string': json_string}), content_type='application/json')

    #     self.assertEqual(request.status_code, 200)
    #     response = custom_encrypt_obj.decrypt(request.data)
    #     response = json.loads(response)
    #     self.assertEqual(response["status_code"], "200")
    #     client.logout()

    #     client.login(username="test12345", password="test12345")
    #     json_string = json.dumps({
    #         'pk': 2,
    #     })
    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post('/livechat/delete-calender-event/', json.dumps(
    #         {'json_string': json_string}), content_type='application/json')

    #     self.assertEqual(request.status_code, 200)
    #     response = custom_encrypt_obj.decrypt(request.data)
    #     response = json.loads(response)
    #     self.assertEqual(response["status_code"], "500")

    #     client.logout()
    #     client.login(username="test1234", password="test1234")

    #     json_string = json.dumps({
    #         'holiday_date': '1212-12-12',
    #         'description': 'Testing',
    #         'auto_response': 'This is testing.'
    #     })
    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post('/livechat/add-holiday-calender/', json.dumps(
    #         {'json_string': json_string}), content_type='application/json')

    #     self.assertEqual(request.status_code, 200)
    #     response = custom_encrypt_obj.decrypt(request.data)
    #     response = json.loads(response)
    #     self.assertEqual(response["status_code"], "500")

    """
    function tested: AddHolidayCalenderAPI
    input queries:
        holiday_date: 
        description: 
        auto_response: 
    expected output:
        status: 200 // SUCCESS
        status: 300 // Duplicate exists
        status: 500 // Error
    """

    def test_AddHolidayCalenderAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        # date format is incorrect will give error
        json_string = json.dumps({
            'holiday_date_array': ['12-12-1212'],
            'description': 'Testing',
            'auto_response': 'This is testing.'
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-holiday-calender/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")

        # date format is correct will give 200 response
        json_string = json.dumps({
            'holiday_date_array': ['2022-12-12'],
            'description': 'Testing',
            'auto_response': 'This is testing.'
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-holiday-calender/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        # more tahn 1 dates will give 200 response
        json_string = json.dumps({
            'holiday_date_array': ['2022-12-12', '2022-11-11'],
            'description': 'Testing',
            'auto_response': 'This is testing.'
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-holiday-calender/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        client.logout()

        # Livechat user with status 2 is not allowed to add holiday
        client.login(username="test12345", password="test12345")

        json_string = json.dumps({
            'holiday_date_array': ['2022-11-11'],
            'description': 'Testing',
            'auto_response': 'This is testing.'
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-holiday-calender/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")

        client.logout()
        # Livechat user with status 3 is not allowed to add holiday
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({
            'holiday_date_array': ['1212-12-12'],
            'description': 'Testing',
            'auto_response': 'This is testing.'
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-holiday-calender/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")
