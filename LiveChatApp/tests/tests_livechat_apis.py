# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.db.models import Q
from rest_framework.test import APIClient
from EasyChatApp.models import Bot, User, MISDashboard, Channel, Profile
from LiveChatApp.models import LiveChatInternalUserGroup, LiveChatUser, LiveChatCustomer, CannedResponse, LiveChatConfig, LiveChatCategory,\
    LiveChatBlackListKeyword, LiveChatAuditTrail, LiveChatCalender, LiveChatMISDashboard, LiveChatAdminConfig,\
    LiveChatProcessors, LiveChatDeveloperProcessor, LiveChatDataExportRequest, LiveChatDisposeChatForm, LiveChatWhatsAppServiceProvider, LiveChatRaiseTicketForm, LiveChatFollowupCustomer
from LiveChatApp.utils import check_and_update_user_group, get_time, is_agent_live, get_miniseconds_datetime
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.constants_processors import LIVECHAT_PROCESSOR_EXAMPLE, LIVECHAT_PROCESSOR_EXAMPLE_END_CHAT
import logging
import json
import random
import execjs
import base64
import uuid
from datetime import datetime, timedelta
from Crypto import Random
from Crypto.Cipher import AES
logger = logging.getLogger(__name__)

"""
Test of All functions which are dependent on models
"""


class SomeFunctionsWithModels(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'LiveChat'})
        channel = Channel.objects.create(name="Web")
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        category_obj = LiveChatCategory.objects.create(
            title="others", bot=bot_obj)
        category_obj2 = LiveChatCategory.objects.create(
            title="credit", bot=bot_obj)
        livechat_config = LiveChatConfig.objects.create(
            max_customer_count=110, bot=bot_obj)
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
        livechat_agent.category.add(category_obj2)
        livechat_agent.bots.add(bot_obj)

        livechat_agent2 = LiveChatUser.objects.create(status="2", user=User.objects.create(
            role="1", status="1", username="test12345", password="test12345", first_name="allincall"), is_online=True)
        livechat_agent.agents.add(livechat_agent2)
        livechat_agent.save()
        livechat_admin_config = LiveChatAdminConfig.objects.create(
            admin=livechat_agent)
        livechat_admin_config.livechat_config.add(livechat_config)
        livechat_admin_config.save()
        livechat_agent1 = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="test1234", password="test1234", first_name="allincall"))
        livechat_agent2.agents.add(livechat_agent1)
        livechat_agent2.bots.add(bot_obj)
        livechat_agent2.save()
        livechat_agent1.category.add(category_obj)
        livechat_agent1.bots.add(bot_obj)
        livechat_agent1.save()
        livechat_agent3 = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="test123", password="test123", first_name="allincall"), is_online=True)
        livechat_agent3.bots.add(bot_obj)
        livechat_agent.agents.add(livechat_agent3)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=10, chat_duration=10, queue_time=5, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=2, chat_duration=10, queue_time=7, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=3, chat_duration=10, queue_time=8, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True, joined_date=datetime.now(
        ) - timedelta(days=8), wait_time=20, chat_duration=100, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True, joined_date=datetime.now(
        ) - timedelta(days=8), wait_time=10, chat_duration=100, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True, joined_date=datetime.now(
        ) - timedelta(days=8), wait_time=20, chat_duration=100, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True, joined_date=datetime.now(
        ) - timedelta(days=8), wait_time=30, chat_duration=100, bot=bot_obj, channel=channel)

        LiveChatMISDashboard.objects.create(livechat_customer=LiveChatCustomer.objects.all()[
                                            0], sender="Customer", sender_name="Customer", text_message="Hi")
        LiveChatMISDashboard.objects.create(livechat_customer=LiveChatCustomer.objects.all()[
                                            0], sender="Agent", sender_name="Agent", text_message="hello")
        CannedResponse.objects.create(
            status="public", agent_id=livechat_agent, keyword="Hi", response="hello, how may I assist you?")
        CannedResponse.objects.create(status="public", agent_id=livechat_agent,
                                      keyword="Bye", response="Thanks, Hoping to see you in future.")
        CannedResponse.objects.create(status="public", agent_id=livechat_agent,
                                      keyword="hii", response="Thanks, Hoping to see you in future.")
        CannedResponse.objects.create(status="public", agent_id=livechat_agent,
                                      keyword="Byee", response="Thanks, Hoping to see you in future.")
        CannedResponse.objects.create(status="private", agent_id=livechat_agent1,
                                      keyword="testing", response="Thanks, Hoping to see you in future.")

    """
    function tested: test_TransferChatAPI
    input queries:
        selected_category: Seleected category of livechat customer.
        selected_agent: if it is -1, then random assignment will happen, else selected agent.
        bot_pk: bot id
        session_id: Livechat customer session id
    expected output:
        status: 200 // SUCCESS
    checks for:
        Create new livechat only admin, if user of same username does not exists.
    """

    def test_TransferChatAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        livechat_agent_to_mark_online = LiveChatUser.objects.filter(status="3")[
            0]
        livechat_agent_to_mark_online.is_online = True
        livechat_agent_to_mark_online.save()
        category_obj = LiveChatCategory.objects.all()[0]
        bot_obj = Bot.objects.all()[0]
        livechat_customer = LiveChatCustomer.objects.all()[0]
        livechat_agent = livechat_customer.agent_id
        livechat_agent.status = "3"
        livechat_agent.save()
        # selected_agent = -1
        cust_last_app_time = get_miniseconds_datetime(datetime.now())
        json_string = json.dumps({
            'selected_category': category_obj.pk,
            'selected_agent': '-1',
            'session_id': str(livechat_customer.session_id),
            'bot_pk': bot_obj.pk,
            'cust_last_app_time': cust_last_app_time,
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/transfer-chat/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        # selected_agent = -1 but max customer count exceeded
        livechat_config_obj = LiveChatConfig.objects.get(bot=bot_obj)
        livechat_config_obj.max_customer_count = 1
        livechat_config_obj.save()

        livechat_customer = LiveChatCustomer.objects.all()[1]
        cust_last_app_time = get_miniseconds_datetime(datetime.now())

        json_string = json.dumps({
            'selected_category': category_obj.pk,
            'selected_agent': '-1',
            'session_id': str(livechat_customer.session_id),
            'bot_pk': bot_obj.pk,
            'cust_last_app_time': cust_last_app_time,
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/transfer-chat/', json.dumps(
            {'json_string': json_string}), content_type='application/json')
        print(livechat_customer.agent_id)

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        # selected_agent = known agent
        livechat_config_obj = LiveChatConfig.objects.get(bot=bot_obj)
        livechat_config_obj.max_customer_count = 110
        livechat_config_obj.save()

        livechat_customer = LiveChatCustomer.objects.all()[2]
        selected_agent = LiveChatUser.objects.filter(
            ~Q(pk=livechat_customer.agent_id.pk))[0]
        cust_last_app_time = get_miniseconds_datetime(datetime.now())

        json_string = json.dumps({
            'selected_category': category_obj.pk,
            'selected_agent': selected_agent.pk,
            'session_id': str(livechat_customer.session_id),
            'bot_pk': bot_obj.pk,
            'cust_last_app_time': cust_last_app_time,
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/transfer-chat/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        # selected_agent = known but max customer count exceeded
        livechat_config_obj = LiveChatConfig.objects.get(bot=bot_obj)
        livechat_config_obj.max_customer_count = 1
        livechat_config_obj.save()

        livechat_customer = LiveChatCustomer.objects.all()[3]
        selected_agent = LiveChatUser.objects.filter(
            ~Q(pk=livechat_customer.agent_id.pk))[0]
        cust_last_app_time = get_miniseconds_datetime(datetime.now())

        json_string = json.dumps({
            'selected_category': category_obj.pk,
            'selected_agent': selected_agent.pk,
            'session_id': str(livechat_customer.session_id),
            'bot_pk': bot_obj.pk,
            'cust_last_app_time': cust_last_app_time,
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/transfer-chat/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        client.logout()

    """
    function tested: test_CreateNewLiveChatOnlyAdminAPI
    input queries:
        name: Full name of livechat only admin
        phone_number: phone number of livechat only user
        bot_pk: bot id
        email: Email ID of livechat only user
    expected output:
        status: 200 // SUCCESS
    checks for:
        Create new livechat only admin, if user of same username does not exists.
    """

    def test_CreateNewLiveChatOnlyAdminAPI(self):

        client = APIClient()

        client.login(username="test1234", password="test1234")
        json_string = json.dumps(
            {"name": "vikash patel", "phone_number": "9087654321", "email": "test@getcogno.ai", "bot_pk": "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/livechat/create-livechat-only-admin/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")

        client.logout()

        client.login(username="test", password="test")
        json_string = json.dumps(
            {"name": "vikash patel", "phone_number": "9087654321", "email": "test@getcogno.ai", "bot_pk": "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-livechat-only-admin/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        json_string = json.dumps(
            {"name": "vikash patel", "phone_number": "9087654321", "email": "test@getcogno.ai", "bot_pk": "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-livechat-only-admin/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "300")

    """
    function tested: test_LiveChatMarkChatAbandonedAPI
    input queries:
        livechat_session_id: livechat session id
    expected output:
        status: 200 // SUCCESS
    checks for:
        Return the livechat chat history to customer side.
    """

    def test_LiveChatMarkChatAbandonedAPI(self):

        client = APIClient()
        json_string = json.dumps(
            {"session_id": "-1", "is_abandoned": "", "is_abruptly_closed": ""})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/mark-chat-abandoned/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"

        LiveChat_obj = LiveChatCustomer.objects.all()[0]
        json_string = json.dumps({"session_id": str(
            LiveChat_obj.session_id), "is_abandoned": "", "is_abruptly_closed": ""})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/mark-chat-abandoned/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        LiveChat_obj = LiveChatCustomer.objects.create(username="test", joined_date=datetime.now(
        ) - timedelta(days=8), bot=Bot.objects.all()[0], channel=Channel.objects.get(name="Web"))
        json_string = json.dumps({"session_id": str(
            LiveChat_obj.session_id), "is_abandoned": True, "is_abruptly_closed": True})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/mark-chat-abandoned/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

    """
    function tested: test_GetMessageHistoryAPI
    input queries:
        livechat_session_id: livechat session id
    expected output:
        status: 200 // SUCCESS
    checks for:
        Return the livechat chat history to customer side.
    """

    def test_GetMessageHistoryAPI(self):

        client = APIClient()
        json_string = json.dumps({"livechat_session_id": "-1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-previous-messages/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        LiveChat_obj = LiveChatCustomer.objects.all()[0]
        json_string = json.dumps(
            {"livechat_session_id": str(LiveChat_obj.session_id)})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-previous-messages/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["message_history"][0]["message"], 'Hi')
        self.assertEqual(response["message_history"][1]["message"], 'hello')

    """
    function tested: test_UpdateMessageHistoryAPI
    input queries:
        session_id: livechat session id
    expected output:
        status: 200 // SUCCESS
    checks for:
        Return customer details as well as livechat chat history on agent side
    """

    def test_UpdateMessageHistoryAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        json_string = json.dumps(
            {"session_id": "-1", "refresh_customer_details": False})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/update-message-history/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        LiveChat_obj = LiveChatCustomer.objects.all()[0]
        Profile.objects.create(user_id=LiveChat_obj.easychat_user_id)
        json_string = json.dumps({"session_id": str(
            LiveChat_obj.session_id), "refresh_customer_details": False})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/update-message-history/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["message_history"][0]["message"], 'Hi')
        self.assertEqual(response["message_history"][1]["message"], 'hello')

        bot_obj = Bot.objects.all()[0]

        bot_obj.use_show_customer_detail_livechat_processor = True
        bot_obj.save()

        request = client.post('/livechat/update-message-history/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)

        request = client.post('/livechat/update-message-history/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)

        LiveChatDeveloperProcessor.objects.create(name="customer_details_1")
        LiveChatProcessors.objects.create(show_customer_details_processor=LiveChatDeveloperProcessor.objects.get(
            name="customer_details_1"), bot=bot_obj)

        request = client.post('/livechat/update-message-history/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)
        self.assertEqual(response["custom_data"], [
                         {"key": "Error", "value": "Error in fetching the data"}])

        LiveChatDeveloperProcessor.objects.create(
            name="customer_details_2", function=LIVECHAT_PROCESSOR_EXAMPLE)

        livechat_processor = LiveChatProcessors.objects.all()[0]
        livechat_processor.show_customer_details_processor = LiveChatDeveloperProcessor.objects.get(
            name="customer_details_2")
        livechat_processor.save()

        request = client.post('/livechat/update-message-history/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["custom_data"], [
                         {'key': 'key1', 'value': 'value1'}, {'key': 'key2', 'value': 'value2'}])

    """
    function tested: test_SwitchAgentStatusAPI
    input queries:
        status: Online/Offline
        selected_status: if offline then (Lunch/Coffeee/Adhoc..etc)
    expected output:
        status: 200 // SUCCESS
    checks for:
        Set the livechat agent mode online/offline
    """

    def test_SwitchAgentStatusAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        livechat_user = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234"))
        json_string = json.dumps(
            {'pk': livechat_user.pk, 'status': True, "selected_status": "6"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/switch-agent-status/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"

        json_string = json.dumps({'pk': livechat_user.pk, 'status': True,
                                  "selected_status": "6", "status_changed_by_admin_supervisor": "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/switch-agent-status/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"

        client.logout()

        json_string = json.dumps({'pk': livechat_user.pk, 'status': True,
                                  "selected_status": "6", "status_changed_by_admin_supervisor": "1"})

        client.login(username="test1234", password="test1234")
        request = client.post('/livechat/switch-agent-status/', json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        livechat_agent = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234"))
        self.assertEqual(livechat_agent.current_status, "6")
        self.assertEqual(livechat_agent.is_online, True)

        json_string = json.dumps(
            {'pk': livechat_agent.pk, 'status': False, "selected_status": "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/switch-agent-status/', json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        livechat_agent = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234"))
        self.assertEqual(livechat_agent.current_status, "1")
        self.assertEqual(livechat_agent.is_online, False)

        json_string = json.dumps(
            {'pk': 1, 'status': False, "selected_status": "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/switch-agent-status/', json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"
        livechat_agent = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234"))
        self.assertEqual(livechat_agent.current_status, "1")
        self.assertEqual(livechat_agent.is_online, False)

    """
    function tested: test_EditAgentInfoAPI
    input queries:
        first_name:
        last_name:
        phone_number:
        username:
        password:
        email:
        status:
        supervisor_pk:
    expected output:
        status: 200 // SUCCESS
    checks for:
        If the username exists then it returns status_code 300.
    """

    def test_EditAgentInfoAPI(self):

        client = APIClient()
        # API request from an agent to edit agent info, which is not
        # allowed. It should return status code 500.
        client.login(username="test1234", password="test1234")
        json_string = json.dumps({'first_name': "easychat", 'last_name': 'user', 'phone_number': '1234567890',
                                  'username': 'test123445', 'password': 'test142345', 'email': 'abc@mail.com', 'current_pk': "1", 'status': '1', "category_pk_list": ["1"], "bot_pk_list": ["1"], "supervisor_pk": "-1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-agent-info/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"
        client.logout()

        # API request from Supervisor to edit agent info, which is allowed. It
        # should return status code 200.

        livechat_agent = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234"))
        client.login(username="test", password="test")
        json_string = json.dumps({'name': "easychat", 'phone_number': '1234567890',
                                  'username': 'test1234', 'password': 'test12345', 'email': 'abc@mail.com', 'current_pk': str(livechat_agent.pk), 'status': '3', "category_pk_list": ["1"], "bot_pk_list": ["1"], "supervisor_pk": "1", "max_customers_allowed": 1})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-agent-info/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        # API request from Supervisor to edit agent info, which is allowed. It
        # should return status code 200.
        client.logout()
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({'name': "easychat changed", 'phone_number': '1234567890',
                                  'username': 'test1234', 'password': 'test12345', 'email': 'abc@mail.com', 'current_pk': str(livechat_agent.pk), 'status': '3', "category_pk_list": ["1"], "bot_pk_list": ["1"], "supervisor_pk": "2", "max_customers_allowed": 1})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-agent-info/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

    """
    # function tested: DeleteBlackListedKeywordAPI
    input queries:
        blacklisted_keyword_pk_list: pk list of keyword, which needs to be deleted.
    expected output:
        status: 200 // SUCCESS
    """

    def test_DeleteBlackListedKeywordAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        LiveChatBlackListKeyword.objects.create(
            word="Testing", agent_id=LiveChatUser.objects.get(user=User.objects.get(username="test")))
        json_string = json.dumps({
            'blacklisted_keyword_pk_list': [1],
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/delete-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        json_string = json.dumps({
            'blacklisted_keyword_pk_list': [11],
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/delete-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")

        client.logout()
        client.login(username="test12345", password="test12345")

        LiveChatBlackListKeyword.objects.create(word="Testing12345", agent_id=LiveChatUser.objects.get(
            user=User.objects.get(username="test12345")))
        json_string = json.dumps({
            'blacklisted_keyword_pk_list': [2],
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/delete-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        client.logout()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({
            'blacklisted_keyword_pk_list': 1,
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/delete-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")

    """
    # function tested: EditBlacklistedKeywordAPI
    input queries:
        word: Edited keyword.
        pk: pk of old keyword object
    expected output:
        status: 200 // SUCCESS

        Checks if new keyword exist in blacklist, it will return status code 300. Otherwise it will edit the old keyword object.
    """

    def test_EditBlacklistedKeywordAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        LiveChatBlackListKeyword.objects.create(
            word="Testing", agent_id=LiveChatUser.objects.get(user=User.objects.get(username="test")))
        json_string = json.dumps({
            'word': "LiveChat",
            'pk': 1,
            'blacklist_for': "agent",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        json_string = json.dumps({
            'word': 'Livechat',
            'pk': 1,
            'blacklist_for': "agent",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "300")

        client.logout()
        client.login(username="test12345", password="test12345")

        json_string = json.dumps({
            'word': "LiveChatTesting",
            'pk': 1,
            'blacklist_for': "agent",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")

        LiveChatBlackListKeyword.objects.create(word="Testing12345", agent_id=LiveChatUser.objects.get(
            user=User.objects.get(username="test12345")))
        json_string = json.dumps({
            'word': 'Livechattesting',
            'pk': 2,
            'blacklist_for': "agent",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "300")

        client.logout()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({
            'word': "Testing",
            'pk': 1,
            'blacklist_for': "agent",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")

    """
    # function tested: AddBlacklistedKeywordAPI
    input queries:
        word: keyword which needs to be blacklisted.
    expected output:
        status: 200 // SUCCESS

        Adds new keyword in blacklist.
    """

    def test_AddBlacklistedKeywordAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        json_string = json.dumps({
            'added_words': ["LiveChat"],
            'blacklist_for': "agent",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        json_string = json.dumps({
            'added_words': ['Livechat', 'Easychat'],
            'blacklist_for': "agent",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert response["all_words_added"] == False

        client.logout()
        client.login(username="test12345", password="test12345")

        json_string = json.dumps({
            'added_words': ["LiveChatTesting"],
            'blacklist_for': "agent",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        json_string = json.dumps({
            'added_words': ['Livechattesting'],
            'blacklist_for': "agent",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert response["all_words_added"] == False

        client.logout()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({
            'added_words': ["Testing"],
            'blacklist_for': "agent",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        json_string = json.dumps({
            'added_words': ['Livechattesting'],
            'blacklist_for': "agent",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-blacklisted-keyword/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

    """
    # function tested: GetAgentDetailsAPI
    input queries:
        user_id: livechat customer user ID provided by LiveChat platform
    expected output:
        status: 200 // SUCCESS

        Return the agent details such as name, email, phone, joined date etc.
    """

    def test_GetCustomerDetailsAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        json_string = json.dumps({
            'session_id': "-1",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-customer-details/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == 500

        livechat_customer = LiveChatCustomer.objects.all()[0]
        json_string = json.dumps({
            'session_id': str(livechat_customer.session_id)
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-customer-details/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == 200
        assert response["bot_id"] == 1

    """
    # function tested: GetLiveChatAgentsAPI
    input queries:
        selected_category: Category of livechat agent/-1
    expected output:
        status: 200 // SUCCESS

        Return the list of all agents having the provided category. If selected_category is -1, then it returns all agent list.
    """

    def test_GetLiveChatAgentsAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        user_obj = LiveChatUser.objects.get(
            user=User.objects.get(username="test"))
        category_obj = LiveChatCategory.objects.all()[0]
        bot_obj = Bot.objects.get(name="testbot")
        bot_id = bot_obj.pk

        json_string = json.dumps({
            'selected_category': "-1",
            'bot_id': bot_id
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-agents/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["current_agent_pk"] == user_obj.pk
        assert response["status_code"] == "200"
        assert len(response["agent_list"]) == 1

        category_obj = LiveChatCategory.objects.create(
            title="Loan", bot=bot_obj)

        json_string = json.dumps({
            'selected_category': category_obj.pk,
            'bot_id': bot_id
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-agents/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200

        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        assert len(response["agent_list"]) == 0

        client.logout()
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({
            'selected_category': "-1",
            'bot_id': bot_id
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-agents/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        assert len(response["agent_list"]) == 1

        client.logout()
        client.login(username="test1234", password="test1234")
        json_string = json.dumps({
            'selected_category': "-1",
            'bot_id': bot_id
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-agents/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        self.assertEqual(len(response["agent_list"]), 0)

    """
    # function tested: test_GetLiveChatCategoryListAPI
    input queries:
        title:

    expected output:
        status: 200 // SUCCESS
        retruns the list of category.
    """

    def test_GetLiveChatCategoryListAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        json_string = json.dumps({
            "bot_id": Bot.objects.get(name="testbot").pk
        })

        request = client.post('/livechat/get-livechat-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"

        livechat_config = LiveChatConfig.objects.all()[0]
        livechat_config.category_enabled = True
        livechat_config.save()

        request = client.post('/livechat/get-livechat-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        self.assertEqual(response["category_list"], [
                         {"pk": "1", "title": "others"}, {'pk': '2', 'title': 'credit'}])

    """
    # function tested: test_GetBotUnderUserAPI
    input queries:
        selected_pk:

    expected output:
        status: 200 // SUCCESS
        retruns the list of bots.
    """

    def test_GetBotUnderUserAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        json_string = json.dumps({
            'selected_pk': '1'
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-bots-under-user/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        self.assertEqual(response["bot_objs"], [
                         {"bot_pk": 1, "bot_name": "testbot"}])

    """
    function tested: test_CreateNewAgentAPI
    input queries:
        first_name:
        last_name:
        phone_number:
        username:
        password:
        email:
        status:
    expected output:
        status: 200 // SUCCESS
    checks for:
        If the username exists then it returns status_code 300. This function completed, if it is raised from Supervisor side.
    """

    def test_CreateNewAgentAPI(self):

        client = APIClient()
        # API request from an agent to create a new agent, which is not
        # allowed. It should return status code 500.
        client.login(username="test1234", password="test1234")
        json_string = json.dumps({'name': "easychat", 'phone_number': '1234567890',
                                  'email': 'abc@mail.com', 'status': '1', "category_pk_list": ["1"], "bot_pk_list": ["1"], "max_customers_allowed": 1})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-new-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"
        client.logout()

        # API request from Supervisor to create a new Supervisor, which is allowed. It
        # should return status code 200.
        client.login(username="test", password="test")
        json_string = json.dumps({'name': "easychat", 'phone_number': '9988331133',
                                  'email': 'def@mail.com', 'status': '2', "category_pk_list": ["1"], "bot_pk_list": ["1"], "max_customers_allowed": 1})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-new-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        # API request from Supervisor to create a new agent, which is allowed. It
        # should return status code 200.
        client.login(username="test", password="test")
        json_string = json.dumps({'name': "easychat", 'phone_number': '9977665544',
                                  'email': 'ghi@mail.com', 'status': '3', "category_pk_list": ["1"], "bot_pk_list": ["1"], "max_customers_allowed": 3})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-new-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        # API request from Supervisor to create a new admin, which is not allowed. It
        # should return status code 300.
        client.login(username="test", password="test")
        json_string = json.dumps({'name': "easychat", 'phone_number': '8877665599',
                                  'email': 'jkl@mail.com', 'status': '1', "category_pk_list": ["1"], "bot_pk_list": ["1"], "max_customers_allowed": 8})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-new-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"

        # API request from Supervisor to create a new agent, which is allowed. It
        # should return status code 200.
        client.logout()
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({'name': "easychat", 'phone_number': '9876543211',
                                  'email': 'mno@mail.com', 'status': '3', "category_pk_list": ["1"], "bot_pk_list": ["1"], "max_customers_allowed": -1})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-new-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        # API request from Supervisor to create a new admin, which is not allowed. It
        # should return status code 300.
        client.logout()
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({'name': "easychat", 'phone_number': '9900887711',
                                  'email': 'pqr@mail.com', 'status': '1', "category_pk_list": ["1"], "bot_pk_list": ["1"], "max_customers_allowed": 2})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-new-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"

    """
    function tested: test_DeleteAgentAPI
    input queries:
        agent_id: pk of the agent, which needs to be deleted
    expected output:
        status: 200 // SUCCESS
    checks for:
        set is_deleted = True to corresponding agent. This function completed, if it is raised from Supervisor side.
    """

    def test_DeleteAgentAPI(self):

        client = APIClient()
        # API request from an agent to delete agent, which is not allowed. It
        # should return status code 500.
        client.login(username="test1234", password="test1234")
        json_string = json.dumps({'selected_users': ['1']})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/delete-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"
        client.logout()

        # API request from an agent to delete agent, which is allowed. It
        # should return status code 200.
        client.login(username="test", password="test")
        json_string = json.dumps({'selected_users': ['2']})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/delete-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

    """
    function tested: test_CreateCustomerRoomAPI
    input queries:
        user_id:
        user_id:
        session_id:
        bot_id:
        username:
        phone:
        email:
    expected output:
        status: 200 // SUCCESS
    checks for:
        If livechat customer already exists then it updates the session_id for that livechat customer otherwise creates new one.
    """

    def test_CreateCustomerRoomAPI(self):

        client = APIClient()
        json_string = json.dumps({'message': 'hi', 'session_id': '1231122',
                                  'bot_id': 1, 'username': "vikash", 'phone': '+919988112233', 'email': 'hasdf@ad.com', "livechat_category": "1", "active_url": "easychat-dev.in/chat", "easychat_user_id": '123411', "customer_details": []})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-customer/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        customer_obj = LiveChatCustomer.objects.all()[8]
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        assert customer_obj.bot.pk == 1

    """
    function tested: test_SaveAgentGeneralSettingsAPI
    input queries:
        notification: True/False (LiveChat notification if new customer assigned to agent or chat transfer)
    expected output:
        status: 200 // SUCCESS
    """

    def test_SaveAgentGeneralSettingsAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        json_string = json.dumps(
            {'notification': True, 'preferred_languages': []})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-agent-general-settings/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"

        client.logout()

        client.login(username="test1234", password="test1234")
        request = client.post('/livechat/save-agent-general-settings/', json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

    """
    function tested: test_UpdateLastSeenAPI
    input queries:
        ....
    expected output:
        ....
    checks for:
        updated the last seen of livechat agent
    """

    def test_UpdateLastSeenAPI(self):

        client = APIClient()
        # livechat_agent = LiveChatUser.objects.get(pk=1)
        client.login(username="test", password="test")

        request = client.post('/livechat/update-last-seen/',
                              json.dumps({}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

    """
    function tested: test_SaveLiveChatFeedbackAPI
    input queries:
        user_id: room id of livechat customer
        rate_value: rating given by livechat customer
    expected output:
        status: 200 // SUCCESS
    checks for:
        updates the rate value and chat duration of livechat customer with agent. Also crosscheck the updated rated value.
    """

    def test_SaveLiveChatFeedbackAPI(self):

        client = APIClient()
        livechat_customer = LiveChatCustomer.objects.all()

        for customer in livechat_customer:
            val = random.randint(1, 10)
            json_string = json.dumps({
                'session_id': str(customer.session_id),
                'rate_value': val,
                'bot_id': "1",
                'nps_text_feedback': 'Great'
            })
            custom_encrypt_obj = CustomEncrypt()
            json_string = custom_encrypt_obj.encrypt(json_string)

            request = client.post('/livechat/save-livechat-feedback/', json.dumps(
                {'json_string': json_string}), content_type='application/json')
            customer_obj = LiveChatCustomer.objects.get(
                session_id=customer.session_id)

            assert request.status_code == 200
            response = custom_encrypt_obj.decrypt(request.data)
            response = json.loads(response)
            assert response["status_code"] == "200"
            assert customer_obj.rate_value == val
            assert customer_obj.nps_text_feedback == "Great"

    """
    function tested: test_DeleteCannedResponseAPI
    input queries:
        canned_response_pk_list: list of pk of all canned responses which needs to be deleted
    expected output:
        status: 200 // SUCCESS
    checks for:
        set is_deleted: True for all of given list of pks
    """

    def test_DeleteCannedResponseAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        # canned_responses = CannedResponse.objects.all()
        canned_response_pk_list = ["1", "2"]

        json_string = json.dumps({
            'canned_response_pk_list': canned_response_pk_list
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/livechat/delete-canned-response/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

    """
    function tested: test_EditCannedResponseAPI
    input queries:
        title:
        keyword:
        response:
        status:
        canned_response_pk:
    expected output:
        status: 200 // SUCCESS
    checks for:
        updates the rate value and chat duration of livechat customer with agent. Also crosscheck the updated rated value.
    """

    def test_EditCannedResponseAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        canned_response = CannedResponse.objects.get(pk=3)

        json_string = json.dumps({
            'title': 'hello',
            'keyword': 'hii',
            'response': 'hello',
            'status': "public",
            'canned_response_pk': 3
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-canned-response/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        canned_response = CannedResponse.objects.get(pk=3)

        assert canned_response.response == 'hello'

        canned_response = CannedResponse.objects.get(pk=4)

        json_string = json.dumps({
            'title': 'hello',
            'keyword': 'hii',
            'response': 'hello',
            'status': "public",
            'canned_response_pk': 4
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-canned-response/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"

    """
    function tested: test_GetCannedResponseAPI
    input queries:
        request from autherised agent.
    expected output:
        status: 200 // SUCCESS
        List of all canned responses allowed to the agent.
    checks for:
        returns all public canned response and private canned response created by that perticular Agent.
    """

    def test_GetCannedResponseAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        request = client.post('/livechat/get-canned-response/',
                              json.dumps({}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        assert len(response["canned_response"]) == 4

    """
    function tested: test_CreateNewCannedResponseAPI
    input queries:
        title:
        keyword:
        response:
        status:
        request from autherised agent/Supervisor.
    expected output:
        status: 200 // SUCCESS
        New entry of canned response in database.
    checks for:
        Create a new canned response with status public for Supervisor and private for agent.
    """

    def test_CreateNewCannedResponseAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        json_string = json.dumps({
            'title': 'hello',
            'keyword': 'hii',
            'response': 'hello',
            'status': "public"
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-new-canned-response/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"

        json_string = json.dumps({
            'title': 'hello',
            'keyword': 'hichaki',
            'response': 'hello',
            'status': "public"
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-new-canned-response/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        public_canned_response = CannedResponse.objects.filter(
            status="public", agent_id=LiveChatUser.objects.get(pk=1))

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        assert len(public_canned_response) == 5

        client.logout()

        client.login(username="test1234", password="test1234")

        json_string = json.dumps({
            'title': 'hello',
            'keyword': 'hii1',
            'response': 'he1llo',
            'status': "private",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-new-canned-response/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        private_canned_response = CannedResponse.objects.filter(
            status="private")

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        assert len(private_canned_response) == 2

        json_string = json.dumps({
            'title': 'hello',
            'keyword': 'hii123',
            'response': 'he1llo>)<(;',
            'status': "private",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-new-canned-response/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        canned_response = CannedResponse.objects.filter(
            keyword="hii123")

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "302"
        assert len(canned_response) == 0

    """
    function tested: test_ManageAgentsContinuousAPI
    input queries:
        ....
    expected output:
        status: 200 // SUCCESS

    """

    def test_ManageAgentsContinuousAPI(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({
            'user_type': 'agents',
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post("/livechat/manage-agents-continuous/", json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

    """
    function tested: test_GetLiveChatSupervisorCategoryAPI
    input queries:
        ....
    expected output:
        status: 200 // SUCCESS

    """

    def test_GetLiveChatSupervisorCategoryAPI(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")

        supervisor_obj = LiveChatUser.objects.get(user__username='test')
        agent_obj = LiveChatUser.objects.get(user__username='test123')

        json_string = json.dumps({
            'user_pk': supervisor_obj.pk,
            'agent_pk': agent_obj.pk,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post("/livechat/get-supervisor-category/", json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        self.assertEqual(response["category_list"], [
                         {"pk": 1, "title": "others"}, {'pk': 2, 'title': 'credit'}])


class UtilsSomeFunctionsWithModels(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'LiveChat'})
        Channel.objects.create(name="Web")
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        LiveChatProcessors.objects.create(bot=bot_obj, end_chat_processor=LiveChatDeveloperProcessor.objects.create(
            function=LIVECHAT_PROCESSOR_EXAMPLE_END_CHAT), show_customer_details_processor=LiveChatDeveloperProcessor.objects.create(function=LIVECHAT_PROCESSOR_EXAMPLE))
        User.objects.create(
            role="1", status="1", username="test", password="test")
        user_obj = LiveChatUser.objects.create(status="1", user=User.objects.create(
            role="1", status="1", username="test12345", password="test12345"))
        new_user = LiveChatUser.objects.create(status="1", user=User.objects.create(
            role="1", status="1", username="test1234567", password="test1234567"))
        user_obj.bots.add(bot_obj)
        new_user.is_livechat_only_admin = True
        new_user.phone_number = "1111111111"
        new_user.save()
        user_obj.livechat_only_admin.add(new_user)
        user_obj.save()
        LiveChatUser.objects.create(status="1", user=User.objects.create(
            role="1", status="1", username="test1234", password="test1234"))

    def test_SaveLiveChatProcessorContentAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        json_string = json.dumps(
            {'bot_pk': "1", "code": "def f(x):\n    return x", "name": "test", "type_of_processor": "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-livechat-processor/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == 200

        json_string = json.dumps(
            {'bot_pk': "1", "code": "def f(x):\n    return x", "name": "test", "type_of_processor": "2"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-livechat-processor/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == 200
        client.logout()

    def test_LiveChatProcessorRun(self):
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        Profile.objects.create(user_id='123456', bot=bot_obj)

        LiveChatConfig.objects.create(bot=bot_obj)

        client = APIClient()
        client.login(username="test", password="test")
        json_string = json.dumps(
            {"parameter": "123456", "code": "def f(x):\n    json_data={'key':x}\n    return json_data", "bot_pk": bot_obj.pk})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/livechat/livechat-processor-run/', json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        self.assertEqual(json.loads(response["message"]), {"key": "123456"})

    def test_LiveChatAnalyticsExportDataAPI(self):

        user_obj = LiveChatUser.objects.create(status="1", user=User.objects.create(
            role="1", status="1", username="test123456", password="test123456"), is_online=True)
        client = APIClient()
        client.login(username="test123456", password="test123456")

        json_string = json.dumps({
            "selected_filter_value": "4",
            "startdate": "2021-03-03",
            "enddate": "2021-04-03",
            "email": "dfd@gg.in",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/analytics-exportdata/', json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        export_path = "request_saved"
        export_obj = LiveChatDataExportRequest.objects.filter(
            user=user_obj, report_type="7")
        assert export_obj.count() == 1
        assert response["export_path"] == export_path

    def test_DownloadLiveChatOnlyAdminExcelTemplateAPI(self):

        user_obj = LiveChatUser.objects.get(
            user=User.objects.get(username="test12345"))
        user_obj.is_livechat_only_admin = False
        user_obj.save()
        client = APIClient()
        client.login(username="test12345", password="test12345")
        request = client.post(
            '/livechat/download-create-livechat-only-admin-template/', content_type='application/json')
        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        export_path = "/files/templates/livechat-only-admin-excel-template" + \
            "/Template_createLiveChatOnlyAdmin.xlsx"
        export_path_exist = True
        assert response["export_path"] == export_path
        assert response["export_path_exist"] == export_path_exist

        user_obj = LiveChatUser.objects.get(
            user=User.objects.get(username="test12345"))
        user_obj.is_livechat_only_admin = True
        user_obj.save()
        client = APIClient()
        client.login(username="test12345", password="test12345")
        request = client.post(
            '/livechat/download-create-livechat-only-admin-template/', content_type='application/json')
        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        export_path_exist = None
        assert response["status"] == 500
        response["export_path_exist"] == export_path_exist

    def test_DeleteLiveChatOnlyAdminAPI(self):

        user_obj = LiveChatUser.objects.get(
            user=User.objects.get(username="test12345"))
        new_user = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234567"))
        client = APIClient()
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({
            "current_livechat_only_admin_pk": str(new_user.pk),
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/delete-livechat-only-admin/', json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        new_user = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234567"))
        assert response["status_code"] == "200"
        assert new_user.is_deleted == True

        test_user = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234"))
        user_obj = LiveChatUser.objects.get(
            user=User.objects.get(username="test12345"))
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({
            "current_livechat_only_admin_pk": str(test_user.pk),
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/delete-livechat-only-admin/', json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"

        user_obj = LiveChatUser.objects.get(
            user=User.objects.get(username="test12345"))
        user_obj.is_livechat_only_admin = True
        user_obj.save()
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({
            "current_livechat_only_admin_pk": "1",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/delete-livechat-only-admin/', json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"

    def test_EditLiveChatOnlyAdminInfoAPI(self):

        user_obj = LiveChatUser.objects.get(
            user=User.objects.get(username="test12345"))
        new_user = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234567"))
        bot_obj = Bot.objects.get(name="testbot")
        client = APIClient()
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({
            "name": "new ok",
            "phone_number": "9999999999",
            "email": "abc@r.in",
            "bot_pk": str(bot_obj.pk),
            "current_livechat_only_admin_pk": str(new_user.pk)
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-livechat-only-admin/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        assert new_user.user.first_name == "new"
        assert new_user.user.last_name == "ok"
        assert new_user.user.email == "abc@r.in"

        json_string = json.dumps({
            "name": "new ok",
            "phone_number": "9999999999",
            "email": "abc@r.in",
            "bot_pk": str(bot_obj.pk),
            "current_livechat_only_admin_pk": "1"
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-livechat-only-admin/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"

        user_obj = LiveChatUser.objects.get(
            user=User.objects.get(username="test12345"))
        user_obj.is_livechat_only_admin = True
        user_obj.save()
        json_string = json.dumps({
            "name": "new ok",
            "phone_number": "9999999999",
            "email": "abc@r.in",
            "bot_pk": str(bot_obj.pk),
            "current_livechat_only_admin_pk": "1"
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-livechat-only-admin/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"


class SomeFunctionsWithModelsThirdItreation(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'LiveChat'})
        channel = Channel.objects.create(name="Web")
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        category_obj = LiveChatCategory.objects.create(
            title="others", bot=bot_obj)
        livechat_config = LiveChatConfig.objects.create(
            max_customer_count=110, bot=bot_obj)
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
        livechat_admin_config = LiveChatAdminConfig.objects.create(
            admin=livechat_agent)
        livechat_admin_config.livechat_config.add(livechat_config)
        livechat_admin_config.save()
        livechat_agent1 = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="test1234", password="test1234", first_name="allincall"), is_online=True)
        livechat_agent2.agents.add(livechat_agent1)
        livechat_agent2.bots.add(bot_obj)
        livechat_agent2.save()
        livechat_agent1.category.add(category_obj)
        livechat_agent1.bots.add(bot_obj)
        livechat_agent1.save()
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=10, chat_duration=10, queue_time=5, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=2, chat_duration=10, queue_time=7, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=3, chat_duration=10, queue_time=8, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True, joined_date=datetime.now(
        ) - timedelta(days=8), wait_time=20, chat_duration=100, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True, joined_date=datetime.now(
        ) - timedelta(days=8), wait_time=10, chat_duration=100, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True, joined_date=datetime.now(
        ) - timedelta(days=8), wait_time=20, chat_duration=100, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True, joined_date=datetime.now(
        ) - timedelta(days=8), wait_time=30, chat_duration=100, bot=bot_obj, channel=channel)
        CannedResponse.objects.create(
            status="public", agent_id=livechat_agent, keyword="Hi", response="hello, how may I assist you?")
        CannedResponse.objects.create(status="public", agent_id=livechat_agent,
                                      keyword="Bye", response="Thanks, Hoping to see you in future.")
        CannedResponse.objects.create(status="public", agent_id=livechat_agent,
                                      keyword="hii", response="Thanks, Hoping to see you in future.")
        CannedResponse.objects.create(status="public", agent_id=livechat_agent,
                                      keyword="Byee", response="Thanks, Hoping to see you in future.")
        CannedResponse.objects.create(status="private", agent_id=livechat_agent1,
                                      keyword="testing", response="Thanks, Hoping to see you in future.")

    """
    # function tested: test_DeleteLiveChatCategoryAPI
    input queries:
        category_pk_list: list of category pk

    expected output:
        status: 200 // SUCCESS
        delete livechat category from database.
    """

    def test_DeleteLiveChatCategoryAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        # json_string = json.dumps({
        #     'title': 'Loan',
        #     'priority': '2'
        # })
        bot_obj = Bot.objects.get(name="testbot")

        json_string = json.dumps({
            'title': 'Loan',
            'priority': '2',
            'bot_id': bot_obj.pk,
            'is_public': True
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-new-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        json_string = json.dumps({
            'category_pk_list': ["1"]
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/delete-livechat-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        assert len(LiveChatCategory.objects.filter(is_deleted=False)) == 1

        json_string = json.dumps({
            'category_pk_list': ["1,10,100"]
        })

        request = client.post('/livechat/delete-livechat-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"

        client.logout()

        json_string = json.dumps({
            'category_pk_list': ["1"]
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        client.login(username="test1234", password="test1234")

        request = client.post('/livechat/delete-livechat-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"

    """
    function tested: test_EditLiveChatCategoryAPI
    input queries:
        title:

    expected output:
        status: 200 // SUCCESS
        Edit existing entry of livechat category in database.
    """

    def test_EditLiveChatCategoryAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        bot_obj = Bot.objects.get(name="testbot")

        json_string = json.dumps({
            'title': 'Loan',
            'priority': '3',
            'bot_id': bot_obj.pk,
            'is_public': True
        })

        # json_string = json.dumps({
        #     'title': 'Loan',
        #     'priority': '3'
        # })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-new-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        category_obj = LiveChatCategory.objects.all()[0]

        json_string = json.dumps({
            'title': 'Loan',
            'priority': '4',
            'category_pk': str(category_obj.pk),
            'bot_id': bot_obj.pk,
            'is_public': True
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-livechat-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"

        category_obj = LiveChatCategory.objects.all()[0]

        json_string = json.dumps({
            'title': 'Testing',
            'priority': '5',
            'category_pk': str(category_obj.pk),
            'bot_id': bot_obj.pk,
            'is_public': True
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/edit-livechat-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        client.logout()

        category_obj = LiveChatCategory.objects.all()[0]

        json_string = json.dumps({
            'title': 'TestingAgain',
            'priority': '1',
            'category_pk': str(category_obj.pk),
            'is_public': True
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        client.login(username="test1234", password="test1234")

        request = client.post('/livechat/edit-livechat-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"

    """
    function tested: test_CreateNewCategoryAPI
    input queries:
        title:

    expected output:
        status: 200 // SUCCESS
        New entry of livechat category in database.
    checks for:
        Create a new category based on the conversation type.
    """

    def test_CreateNewCategoryAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        bot_obj = Bot.objects.get(name="testbot")

        json_string = json.dumps({
            'title': 'Loan',
            'priority': '2',
            'bot_id': bot_obj.pk,
            'is_public': True
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/create-new-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        request = client.post('/livechat/create-new-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"

        client.logout()

        client.login(username="test1234", password="test1234")

        request = client.post('/livechat/create-new-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"

        json_string = json.dumps({
            'title': 'Loan',
            'priority': '2',
            'bot_id': bot_obj.pk
        })

        request = client.post('/livechat/edit-livechat-category/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"

    """
    # function tested: test_GetBotUnderUserAPI
    input queries:
        selected_pk:

    expected output:
        status: 200 // SUCCESS
        retruns the list of bots.
    """

    def test_GetBotUnderUserAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        json_string = json.dumps({
            'selected_pk': '1'
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-bots-under-user/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        self.assertEqual(response["bot_objs"], [
                         {"bot_pk": 1, "bot_name": "testbot"}])

        json_string = json.dumps({
            'selected_pk': '5'
        })

        request = client.post('/livechat/get-bots-under-user/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"

        client.logout()

    """
    function tested: test_SaveGeneralSettingsAPI
    input queries:
        max_customer_count: It is the count of customers which can have by an agent.
    expected output:
        status: 200 // SUCCESS
    checks for:
        Set the max_customer_count by Supervisor
    """

    # def test_SaveGeneralSettingsAPI(self):

    #     client = APIClient()
    #     client.login(username="test", password="test")
    #     bot_obj = Bot.objects.get(name="testbot")
    #     bot_pk = bot_obj.pk
    #     json_string = json.dumps({'max_customer_count': 11, "category_enabled": True, "auto_bot_response": "Testing", "meeting_url": "meet.allincall.in", "agent_unavialable_response":
    #                               "Our chat representatives are unavailable right now. Please try again in some time.", "is_video_meeting_enabled": True, "select_bot_obj_pk": bot_pk, "queue_timer": 30, "theme_color": "111,111,111", "show_version_footer": True, "masking_enabled": True})
    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post('/livechat/save-general-settings/', json.dumps(
    #         {'json_string': json_string}), content_type='application/json')

    #     assert request.status_code == 200
    #     response = custom_encrypt_obj.decrypt(request.data)
    #     response = json.loads(response)
    #     assert response["status_code"] == "200"

    #     client.logout()

    #     client.login(username="test1234", password="test1234")
    #     request = client.post('/livechat/save-general-settings/', json.dumps(
    #         {'json_string': json_string}), content_type='application/json')
    #     assert request.status_code == 200
    #     response = custom_encrypt_obj.decrypt(request.data)
    #     response = json.loads(response)
    #     assert response["status_code"] == "500"

    """
    function tested: test_AssignAgentAPI
    input queries:
        session_id of livechat customer
    expected output:
        returns the status of customer, weather he is assigned or not?
    checks for:
        status of livechat customer, which may be one of the following:
        1. assigned_agent: None
        2. assigned_agent: session_end
        3. assigned_agent: not_available
        4. assigned_agent: scheduler_queue
        5. assigned_agent: abruptly_end 
        6. assigned_agent: scheduler_queue
    """

    def test_AssignAgentAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        # to check when no such session exists
        json_string = json.dumps(
            {"session_id": "1234"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/assign-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")
        self.assertEqual(response["assigned_agent"], "None")
        self.assertEqual(response["assigned_agent_username"], "None")

        # to check when no agent assigned
        customer = LiveChatCustomer.objects.create(username="test", is_session_exp=True,
                                                   joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10)

        json_string = json.dumps(
            {"session_id": str(customer.session_id)})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/assign-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")
        self.assertEqual(response["assigned_agent"], "scheduler_queue")
        self.assertEqual(response["assigned_agent_username"], "None")

        # to check when agent is assigned and customer abruptly closed
        livechat_agent = LiveChatUser.objects.get(pk=1)
        customer = LiveChatCustomer.objects.create(username="test", is_session_exp=True, agent_id=livechat_agent,
                                                   joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, abruptly_closed=True)

        json_string = json.dumps(
            {"session_id": str(customer.session_id)})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/assign-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")
        self.assertEqual(response["assigned_agent"], "abruptly_end")
        self.assertEqual(response["assigned_agent_username"], "None")

        # to check when chat is not abruptly closed
        livechat_agent = LiveChatUser.objects.get(pk=1)
        customer = LiveChatCustomer.objects.create(username="test", is_session_exp=True, agent_id=livechat_agent,
                                                   joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, abruptly_closed=False)

        json_string = json.dumps(
            {"session_id": str(customer.session_id)})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/assign-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")
        self.assertEqual(response["assigned_agent"], "session_end")
        self.assertEqual(response["assigned_agent_username"], "None")

        # to check when session is not expired
        livechat_agent = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="testusercheck", password="test1234", first_name="testuser"), is_online=True)
        customer = LiveChatCustomer.objects.create(
            username="test", is_session_exp=False, agent_id=livechat_agent)

        json_string = json.dumps(
            {"session_id": str(customer.session_id)})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/assign-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")
        self.assertEqual(response["assigned_agent"], "not_available")
        self.assertEqual(response["assigned_agent_username"], "None")

        json_string1 = json.dumps(
            {"session_id_check": str(customer.session_id)})

        request = client.post('/livechat/assign-agent/', json.dumps(
            {'json_string': json_string1}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "500")

        client.logout()

    """
    function tested: test_SwitchAgentManagerAPI
    input queries:
        status of livechat user
    expected output:
        status: 200 (Success)
        message: Successfully switched to Agent/Manager mode!"
    """

    def test_SwitchAgentManagerAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        json_string = json.dumps(
            {"status": True})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/switch-agent-manager/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")
        self.assertEqual(response["message"],
                         "Successfully switched to Agent mode!")

        json_string = json.dumps(
            {"status": False})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/switch-agent-manager/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")
        self.assertEqual(response["message"],
                         "Successfully switched to Manager mode!")

        client.logout()

        client.login(username="test1234", password="test1234")

        request = client.post('/livechat/switch-agent-manager/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"
        self.assertEqual(response["message"], "Unauthorised access")


class SomeFunctionsWithModelsSecondItreation(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'LiveChat'})
        channel = Channel.objects.create(name="Web")
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        category_obj = LiveChatCategory.objects.create(
            title="others", bot=bot_obj)
        category_obj = LiveChatCategory.objects.create(
            title="test", bot=bot_obj)
        livechat_config = LiveChatConfig.objects.create(
            max_customer_count=110, bot=bot_obj)
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
        livechat_admin_config = LiveChatAdminConfig.objects.create(
            admin=livechat_agent)
        livechat_admin_config.livechat_config.add(livechat_config)
        livechat_admin_config.save()
        livechat_agent1 = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="test1234", password="test1234", first_name="allincall"), is_online=True)
        livechat_agent4 = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="testagent", password="testagent", first_name="allincall"), is_online=True)
        livechat_agent2.agents.add(livechat_agent1)
        livechat_agent2.agents.add(livechat_agent4)
        livechat_agent2.bots.add(bot_obj)
        livechat_agent2.save()
        livechat_agent2.category.add(category_obj)
        livechat_agent2.save()
        livechat_agent1.category.add(category_obj)
        livechat_agent1.bots.add(bot_obj)
        livechat_agent1.save()
        livechat_agent4.category.add(category_obj)
        livechat_agent4.bots.add(bot_obj)
        livechat_agent4.save()

        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=10, chat_duration=10, queue_time=5, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=2, chat_duration=10, queue_time=7, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=3, chat_duration=10, queue_time=8, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True, joined_date=datetime.now(
        ) - timedelta(days=8), wait_time=20, chat_duration=100, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True, joined_date=datetime.now(
        ) - timedelta(days=8), wait_time=10, chat_duration=100, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True, joined_date=datetime.now(
        ) - timedelta(days=8), wait_time=20, chat_duration=100, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True, joined_date=datetime.now(
        ) - timedelta(days=8), wait_time=30, chat_duration=100, bot=bot_obj, channel=channel)
        LiveChatCustomer.objects.create(username="agent_not_assigned_customer", category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj, channel=channel)

        LiveChatCustomer.objects.create(username="agent_assigned", agent_id=livechat_agent1, phone="9876543210", category=category_obj, is_session_exp=False,
                                        joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj, channel=channel, unread_message_count=2)
        LiveChatCustomer.objects.create(username="agent_assigned_2", agent_id=livechat_agent1, phone="9999988888", category=category_obj, is_session_exp=False,
                                        joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj, channel=channel, unread_message_count=2)
        LiveChatCustomer.objects.create(username="form_filled", category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj, channel=channel, form_filled=json.dumps([
                                            {
                                                "type": "1",
                                                "label": "Name",
                                                "value": "Shubham",
                                                "optional": False
                                            }
                                        ]))

        CannedResponse.objects.create(
            status="public", agent_id=livechat_agent, keyword="Hi", response="hello, how may I assist you?")
        CannedResponse.objects.create(status="public", agent_id=livechat_agent,
                                      keyword="Bye", response="Thanks, Hoping to see you in future.")
        CannedResponse.objects.create(status="public", agent_id=livechat_agent,
                                      keyword="hii", response="Thanks, Hoping to see you in future.")
        CannedResponse.objects.create(status="public", agent_id=livechat_agent,
                                      keyword="Byee", response="Thanks, Hoping to see you in future.")
        CannedResponse.objects.create(status="private", agent_id=livechat_agent1,
                                      keyword="testing", response="Thanks, Hoping to see you in future.")
        LiveChatDisposeChatForm.objects.create(
            bot=bot_obj, form=json.dumps({}))

        followup_cust_obj1 = LiveChatCustomer.objects.create(username="followup_cust1", client_id="8899114433", category=category_obj,
                                                             is_session_exp=True, joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj, channel=channel)
        followup_cust_obj2 = LiveChatCustomer.objects.create(username="followup_cust2", client_id="8899114422", category=category_obj,
                                                             is_session_exp=True, joined_date=datetime.now(), wait_time=10, chat_duration=10, queue_time=5, bot=bot_obj, channel=channel)

        LiveChatFollowupCustomer.objects.create(
            livechat_customer=followup_cust_obj1, agent_id=livechat_agent1, source="missed_chats", assigned_date=datetime.now())
        LiveChatFollowupCustomer.objects.create(
            livechat_customer=followup_cust_obj2, agent_id=livechat_agent4, source="offline_chats", assigned_date=datetime.now())

    def test_UpdateCustomerListAPI(self):

        client = APIClient()
        # logging in with agent account and now updated customer list should be
        # empty.
        client.login(username="testagent", password="testagent")

        json_string = json.dumps({
            "assigned_customer_count": 0
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/update-customer-list/',
                              json.dumps({'json_string': json_string}),
                              content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "300"
        client.logout()

        client.login(username="test", password="test")

        customer_obj = LiveChatCustomer.objects.all()[0]
        self.assertEqual(customer_obj.agent_id.user.username, "test")
        json_string = json.dumps({
            "assigned_customer_count": 0
        })

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/update-customer-list/',
                              json.dumps({'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "300")

        # Customer list of an agent .with assigned customer
        client.logout()
        client.login(username="test1234", password="test1234")
        json_string = json.dumps({
            "assigned_customer_count": 1
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/livechat/update-customer-list/',
                              json.dumps({'json_string': json_string}), content_type='application/json')

        self.assertEqual(request.status_code, 200)
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")
        self.assertEqual(response["new_assigned_customer_count"], 1)

        json_string = json.dumps({
            "assigned_customer_count": 2
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/livechat/update-customer-list/',
                              json.dumps({'json_string': json_string}), content_type='application/json')
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], "200")
        self.assertEqual(response["new_assigned_customer_count"], 0)

    """
    function tested: test_AgentIframeAPI
    input queries:
        session_id
    expected output:
        status: 200 // SUCCESS
    checks for:
       updates the agent-customer chat info  .
    """

    # def test_AgentIframeAPI(self):

    #     client = APIClient()
    #     client.login(username="test1234", password="test1234")
    #     customer_obj = LiveChatCustomer.objects.get(username="agent_assigned")
    #     json_string = json.dumps({
    #         'session_id': str(customer_obj.session_id),
    #     })

    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post('/livechat/agent-bot/', json.dumps(
    #         {'json_string': json_string}), content_type='application/json')

    #     assert request.status_code == 200
    #     response = custom_encrypt_obj.decrypt(request.data)
    #     response = json.loads(response)
    #     assert response["status_code"] == "200"
    #     # checking the customer details are correct or not
    #     assert response["username_display"] == "agent_assigned"
    #     assert response["livechat_cust_phone"] == "9876543210"

    #     customer_obj = LiveChatCustomer.objects.get(phone="9999988888")
    #     json_string = json.dumps({
    #         'session_id': str(customer_obj.session_id),
    #     })

    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post('/livechat/agent-bot/', json.dumps(
    #         {'json_string': json_string}), content_type='application/json')

    #     assert request.status_code == 200
    #     response = custom_encrypt_obj.decrypt(request.data)
    #     response = json.loads(response)
    #     assert response["status_code"] == "200"
    #     # checking the customer details are correct or not
    #     assert response["username_display"] == "agent_assigned_2"
    #     assert response["livechat_cust_phone"] == "9999988888"

    #     json_string = json.dumps({
    #         'session_id': "-1",
    #     })

    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post('/livechat/agent-bot/', json.dumps(
    #         {'json_string': json_string}), content_type='application/json')

    #     assert request.status_code == 200
    #     response = custom_encrypt_obj.decrypt(request.data)
    #     response = json.loads(response)
    #     assert response["status_code"] == "500"

    """
    function tested: test DownloadAgentExcelTemplateAPI
    input queries:
        
    expected output:
        status: 200 // SUCCESS
    checks for:
       downloads the create agent via excel template sheet  .
    """

    def test_DownloadAgentExcelTemplateAPI(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")
        request = client.post('/livechat/download-create-agent-template/', json.dumps(
            {'json_string': ""}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert str(response["export_path"]) == "None"
        assert str(response["export_path_exist"]) == "None"

        client.logout()
        client.login(username="test", password="test")

        request = client.post('/livechat/download-create-agent-template/', json.dumps(
            {'json_string': ""}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert str(response["export_path"]) == "/files/templates/livechat-agent-create-excel-template" + \
            "/Template_createAgent.xlsx"
        assert str(response["export_path_exist"]) == "True"

        client.login(username="test12345", password="test12345")
        request = client.post('/livechat/download-create-agent-template/', json.dumps(
            {'json_string': ""}), content_type='application/json')
        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert str(response["export_path"]) == "/files/templates/livechat-agent-create-excel-template" + \
            "/Template_createAgent_bySupervisor.xlsx"
        assert str(response["export_path_exist"]) == "True"

    """
    function tested: test LiveChatAnalyticsContinousAPI
    input queries:
        
    expected output:
        status: 200 // SUCCESS
    checks for:
         .
    """

    def test_LiveChatAnalyticsContinousAPI(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({"channel": "All", "category": "All"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/analytics-continous/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500
        client.logout()
        client.login(username="test", password="test")

        request = client.post('/livechat/analytics-continous/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        client.login(username="test12345", password="test12345")

        request = client.post('/livechat/analytics-continous/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

    """
    function tested: test_DeleteAgentAPI
    input queries:
        agent_id: pk of the agent, which needs to be deleted
    expected output:
        status: 200 // SUCCESS
    checks for:
        set is_deleted = True to corresponding agent. This function completed, if it is raised from Supervisor side.
    """

    def test_DeleteAgentAPI(self):

        client = APIClient()
        # API request from an agent to delete agent, which is not allowed. It
        # should return status code 500.
        client.login(username="test1234", password="test1234")
        agent_id = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234")).pk

        selected_users = [agent_id]
        json_string = json.dumps({
            'selected_users': selected_users,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/delete-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"
        client.logout()

        # API request from an admin to delete agent, which is allowed. It
        # should return status code 200.
        client.login(username="test", password="test")
        agent_id = LiveChatUser.objects.get(
            user=User.objects.get(username="test")).pk

        selected_users = [agent_id]
        json_string = json.dumps({
            'selected_users': selected_users,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/delete-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        client.logout()

        # API request from an supervisor to delete agent, which is allowed. It
        # should return status code 200.
        client.login(username="test12345", password="test12345")
        agent_id = LiveChatUser.objects.get(
            user=User.objects.get(username="test12345")).pk

        selected_users = [agent_id]
        json_string = json.dumps({
            'selected_users': selected_users,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/delete-agent/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

    """
    function tested: test_SaveCustomerChatAPI
    input queries:
        user_id:
        message:
        sender: customer
    expected output:
        status: 200 // SUCCESS
    checks for:
        append chat in message_history column of LiveChatCustomer model. It store the as list og dictionaries {user_id:, message:, sender:}.
    """

    def test_SaveCustomerChatAPI(self):

        client = APIClient()
        customer_obj = LiveChatCustomer.objects.all()[4]
        json_string = json.dumps({
            'session_id': str(customer_obj.session_id),
            'message': "This is testing and testing",
            'sender': 'Customer',
            'attached_file_src': "",
            'thumbnail_file_path': "",
            'preview_file_src': "",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-customer-chat/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        json_string = json.dumps({
            'session_id': str(customer_obj.session_id),
            'message': "This is testing and testing",
            'sender': 'Customer',
            'attached_file_src': "/files/test/test.png",
            'thumbnail_file_path': "/files/test/test_thumbnail.png",
            'preview_file_src': "/files/test/test.png",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-customer-chat/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        json_string = json.dumps({
            'session_id': "-1",
            'message': "This is testing and testing",
            'sender': 'Customer',
            'attached_file_src': "",
            'thumbnail_file_path': "",
            'preview_file_src': "",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-customer-chat/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"

    """
    function tested: test_SaveAgentChatAPI
    input queries:
        user_id:
        message:
        sender: Agent
    expected output:
        status: 200 // SUCCESS
    checks for:
        append chat in message_history column of LiveChatCustomer model. It store the as list og dictionaries {user_id:, message:, sender:}.
    """

    def test_SaveAgentChatAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        customer_obj = LiveChatCustomer.objects.all()[4]

        json_string = json.dumps({
            'message': "This is testing",
            'sender': 'Agent',
            'attached_file_src': "",
            "session_id": str(customer_obj.session_id).replace("'", '"'),
            "thumbnail_url": ""
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-agent-chat/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        json_string = json.dumps({
            'message': "This is testing",
            'sender': 'Agent',
            'attached_file_src': "",
            "session_id": "-1",
            "thumbnail_url": ""
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-agent-chat/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"

        customer_obj = LiveChatCustomer.objects.get(
            username="agent_not_assigned_customer")

        json_string = json.dumps({
            'message': "This is testing",
            'sender': 'Agent',
            'attached_file_src': "",
            "session_id": str(customer_obj.session_id).replace("'", '"'),
            "thumbnail_url": ""
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-agent-chat/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"

    """
    function tested: test_EndChatSessionAPI
    input queries:
        user_id:
    expected output:
        status: 200 // SUCCESS
    checks for:
        marks livechat customer session end and set to offline.
    """

    def test_EndChatSessionAPI(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")
        customer_obj = LiveChatCustomer.objects.all()[0]
        bot_id = Bot.objects.get(name="testbot").pk
        json_string = json.dumps({
            "session_id": str(customer_obj.session_id).replace("'", '"'),
            "bot_id": str(bot_id)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/end-chat-session/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

        customer_obj = LiveChatCustomer.objects.all()[0]
        bot_id = Bot.objects.get(name="testbot").pk
        json_string = json.dumps({
            "session_id": "-1",
            "bot_id": str(bot_id)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/end-chat-session/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"

        json_string = json.dumps({
            "session_id": str(customer_obj.session_id).replace("'", '"'),
            "bot_id": "-1"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/end-chat-session/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "500"

        category_pk = LiveChatCategory.objects.get(title="test").pk

        json_string = json.dumps({
            "session_id": str(customer_obj.session_id).replace("'", '"'),
            "bot_id": str(bot_id),
            "closing_category_pk": str(category_pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/end-chat-session/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        # in case of either category not enabled or does not exist endchatsessionapi returns status code 200
        json_string = json.dumps({
            "session_id": str(customer_obj.session_id).replace("'", '"'),
            "bot_id": str(bot_id),
            "closing_category_pk": "-1"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/end-chat-session/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"

    def test_GetLiveChatChatReportsAnalytics(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-chart-report-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        client.logout()
        client.login(username="test", password="test")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-chart-report-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        client.login(username="test12345", password="test12345")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-chart-report-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

    def test_GetAverageNPSAnalytics(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-avg-nps-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        client.logout()
        client.login(username="test", password="test")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-avg-nps-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        client.login(username="test12345", password="test12345")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-avg-nps-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

    def test_GetAverageHandleTimeAnalytics(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-avg-handle-time-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        client.logout()
        client.login(username="test", password="test")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-avg-handle-time-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        client.login(username="test12345", password="test12345")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-avg-handle-time-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

    def test_GetAverageQueueTimeAnalytics(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-avg-queue-time-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        client.logout()
        client.login(username="test", password="test")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-avg-queue-time-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        client.login(username="test12345", password="test12345")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-avg-queue-time-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

    def test_GetInteractionsPerChatAnalytics(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-interactions-per-chat-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        client.logout()
        client.login(username="test", password="test")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-interactions-per-chat-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        client.login(username="test12345", password="test12345")
        json_string = json.dumps({
            "start_date": "",
            "end_date": "",
            "is_filter_present": False,
            "channel": "All",
            "category_pk_list": "All",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-interactions-per-chat-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

    def test_SaveDisposeChatForm(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")

        bot_obj = Bot.objects.all()[0]

        json_string = json.dumps({
            "bot_pk": bot_obj.pk,
            "is_form_enabled": False,
            "form": {},
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-dispose-chat-form/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], "200")

        form_obj = LiveChatDisposeChatForm.objects.get(bot=bot_obj)

        self.assertEqual(form_obj.is_form_enabled, False)

        json_string = json.dumps({
            "bot_pk": bot_obj.pk,
            "is_form_enabled": True,
            "form": {
                "field_12345": {
                    "label_name": "Name",
                    "dependent": False,
                    "placeholder": "Enter your name",
                    "optional": False,
                    "type": "1"
                },
            },
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-dispose-chat-form/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        form_obj = LiveChatDisposeChatForm.objects.get(bot=bot_obj)

        self.assertEqual(response["status"], "200")

        self.assertEqual(form_obj.is_form_enabled, True)

        form = json.loads(form_obj.form)

        self.assertEqual(form, {
            "field_12345": {
                "label_name": "Name",
                "dependent": False,
                "placeholder": "Enter your name",
                "optional": False,
                "type": "1"
            }
        })

    def test_GetDisposeChatFormData(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")

        customer_obj = LiveChatCustomer.objects.get(username="form_filled")

        json_string = json.dumps({
            "id": str(customer_obj.session_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-dispose-chat-form-data/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], "200")

        self.assertEqual(response['form_filled'], [
            {
                "type": "1",
                "label": "Name",
                "value": "Shubham",
                "optional": False
            }
        ])

        json_string = json.dumps({
            "id": "12345",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-dispose-chat-form-data/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], "200")
        self.assertEqual(response['form_filled'], [])

    def test_GetLiveChatQueueRequests(self):

        bot_obj = Bot.objects.filter(
            name="testbot", slug="testbot", bot_display_name="testbot")[0]
        category_obj = LiveChatCategory.objects.filter(
            title="test", bot=bot_obj)[0]
        channel = Channel.objects.all()[0]

        customer_obj = LiveChatCustomer.objects.create(
            username="testcustomer1", agent_id=None, category=category_obj, is_session_exp=False, joined_date=datetime.now(), bot=bot_obj, channel=channel)

        client = APIClient()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({
            "page": 1,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-queue-requests/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)
        self.assertEqual(response["total_requests"], 1)
        queue_requests = response["queue_requests"]
        self.assertEqual(queue_requests[0]["pk"], str(customer_obj.session_id))

        customer_obj.delete()

        json_string = json.dumps({
            "page": 1,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-queue-requests/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)
        self.assertEqual(response["total_requests"], 0)

        json_string = json.dumps({
            "page_no": 3,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-queue-requests/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

    def test_LiveChatSelfAssignRequest(self):

        bot_obj = Bot.objects.all()[0]
        category_obj = LiveChatCategory.objects.all()[0]
        channel = Channel.objects.all()[0]

        customer_obj = LiveChatCustomer.objects.create(
            username="testcustomer2", agent_id=None, category=category_obj, is_session_exp=False, joined_date=datetime.now(), bot=bot_obj, channel=channel)

        client = APIClient()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({
            "session_id": str(customer_obj.session_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/livechat-self-assign-request/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)
        self.assertEqual(response["chat_assigned"], True)
        self.assertEqual(response["customer_name"], "testcustomer2")

        customer_obj = LiveChatCustomer.objects.all()[0]

        json_string = json.dumps({
            "session_id": str(customer_obj.session_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/livechat-self-assign-request/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)
        self.assertEqual(response["chat_assigned"], False)

        json_string = json.dumps({
            "session": str(customer_obj.session_id),
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/livechat-self-assign-request/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

    def test_CheckChatRequestsQueue(self):

        bot_obj = Bot.objects.filter(
            name="testbot", slug="testbot", bot_display_name="testbot")[0]
        category_obj = LiveChatCategory.objects.filter(
            title="test", bot=bot_obj)[0]
        channel = Channel.objects.all()[0]

        customer_obj = LiveChatCustomer.objects.create(
            username="testcustomer1", agent_id=None, category=category_obj, is_session_exp=False, joined_date=datetime.now(), bot=bot_obj, channel=channel)

        client = APIClient()
        client.login(username="test1234", password="test1234")

        request = client.post('/livechat/check-chat-requests-queue/')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)
        self.assertEqual(response["chats_available"], True)

        customer_obj.delete()

        request = client.post('/livechat/check-chat-requests-queue/')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)
        self.assertEqual(response["chats_available"], False)

    def test_GetLiveChatWebhookDefaultCodeAPI(self):

        logger.info("Testing GetLiveChatWebhookDefaultCodeAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting GetLiveChatWebhookDefaultCodeAPI is going on...\n")

        try:
            wsp_obj = LiveChatWhatsAppServiceProvider.objects.get(name="3")
        except:
            wsp_obj = LiveChatWhatsAppServiceProvider.objects.create(
                name="3", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/LiveChatApp/livechatapp_rml_webhook.py")
            wsp_obj.save()

        client = APIClient()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({"wsp_code": "3"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-webhook-default-code/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert["default_code"] != ""
        assert["wsp_name"] != ""

        json_string = json.dumps({"wsp_code": ""})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-webhook-default-code/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500
        assert response["wsp_name"] == ""

    def test_SaveLiveChatWebhookContentAPI(self):

        logger.info("Testing SaveLiveChatWebhookContentAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting SaveLiveChatWebhookContentAPI is going on...\n")

        try:
            LiveChatWhatsAppServiceProvider.objects.get(name="3")
        except:
            LiveChatWhatsAppServiceProvider.objects.create(
                name="3", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/LiveChatApp/livechatapp_rml_webhook.py")

        try:
            Channel.objects.get(name="WhatsApp")
        except:
            Channel.objects.create(name="WhatsApp")

        bot_obj = Bot.objects.all()[0]

        client = APIClient()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps(
            {"code": "Hello World!", "bot_id": bot_obj.pk, "wsp_code": "3"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-livechat-webhook-content/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        json_string = json.dumps(
            {"code": "Hello World!", "bot_id": "", "wsp_code": "3"})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-livechat-webhook-content/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

    def test_GetTranslatedMessageHistoryAPI(self):

        bot_obj = Bot.objects.filter(
            name="testbot", slug="testbot", bot_display_name="testbot")[0]
        category_obj = LiveChatCategory.objects.filter(
            title="test", bot=bot_obj)[0]
        channel = Channel.objects.all()[0]

        livechat_customer = LiveChatCustomer.objects.create(
            username="langcustomer1", agent_id=None, category=category_obj, is_session_exp=False, joined_date=datetime.now(), bot=bot_obj, channel=channel)

        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Customer", sender_name=livechat_customer.username, text_message="test message")

        client = APIClient()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps(
            {"session_id": str(livechat_customer.session_id), "selected_language": "ta"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-translated-message-history/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)
        self.assertEqual(response["message_history"]
                         [0]["message"], "சோதனை செய்தி")

        json_string = json.dumps(
            {"session_id": str(livechat_customer.session_id)})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-translated-message-history/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

    def test_GetTranslatedMessageAPI(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps(
            {"text_message": "ग्राहक", "selected_language": "ta"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-translated-message/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)
        self.assertEqual(response["translated_message"], "வாடிக்கையாளர்")

        json_string = json.dumps({"text_message": "ग्राहक"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-translated-message/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

    def test_AddUsertoUserGroupAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        json_string = json.dumps({"is_user_group": False, "selected_users": [
                                 'test1234'], "chat_belong_to": "test12345"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-user-to-user-group/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)

        client.logout()

        client.login(username="test1234", password="test1234")

        json_string = json.dumps({"is_user_group": False, "selected_users": [
                                 'test'], "chat_belong_to": "test12345"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-user-to-user-group/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)
        self.assertEqual(response["message"],
                         'You are not authorized to add members.')

        client.logout()

        client.login(username="test12345", password="test12345")

        user1 = LiveChatUser.objects.get(user__username='test12345')
        user2 = LiveChatUser.objects.get(user__username='test')
        user3 = LiveChatUser.objects.get(user__username='test1234')

        user_group_obj = check_and_update_user_group(
            user1, user2, LiveChatInternalUserGroup)
        user_group_obj.members.add(user3)
        user_group_obj.is_converted_into_group = True
        user_group_obj.save()

        json_string = json.dumps({"is_user_group": True, "selected_users": [
                                 'test123'], "group_id": str(user_group_obj.group_id)})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/add-user-to-user-group/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)
        self.assertEqual(response['group_id'], str(user_group_obj.group_id))

        client.logout()

    def test_SaveRaiseTicketFormAPI(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")

        bot_obj = Bot.objects.filter(
            name="testbot", slug="testbot", bot_display_name="testbot")[0]
        LiveChatRaiseTicketForm.objects.create(bot=bot_obj)
        json_string = json.dumps({"bot_pk": bot_obj.pk, "is_form_enabled": True, "form": {'field_order': ['field_C7hXo', 'field_q2ckT', 'field_2P8vh', 'field_mLPAs', 'field_JbxVy', 'field_NMo1l'], 'field_C7hXo': {'label_name': 'Name', 'type': '1', 'optional': False, 'placeholder': 'Enter full name', 'dependent': False}, 'field_q2ckT': {'label_name': 'Email', 'type': '1', 'optional': False, 'placeholder': 'Enter email id', 'dependent': False}, 'field_2P8vh': {
                                 'label_name': 'Phone No', 'type': '1', 'optional': False, 'placeholder': 'Enter phone no', 'dependent': False}, 'field_mLPAs': {'label_name': 'Categories', 'type': '6', 'optional': False, 'dependent': False, 'values': ['others']}, 'field_JbxVy': {'label_name': 'Query', 'type': '5', 'optional': False, 'placeholder': 'Enter query', 'dependent': False}, 'field_NMo1l': {'label_name': 'Attachment', 'type': '7', 'optional': True, 'dependent': False}}})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-raise-ticket-form/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], "200")

        json_string = json.dumps({"is_form_enabled": True, "form": {'field_order': ['field_C7hXo', 'field_q2ckT', 'field_2P8vh', 'field_mLPAs', 'field_JbxVy', 'field_NMo1l'], 'field_C7hXo': {'label_name': 'Name', 'type': '1', 'optional': False, 'placeholder': 'Enter full name', 'dependent': False}, 'field_q2ckT': {'label_name': 'Email', 'type': '1', 'optional': False, 'placeholder': 'Enter email id', 'dependent': False}, 'field_2P8vh': {
                                 'label_name': 'Phone No', 'type': '1', 'optional': False, 'placeholder': 'Enter phone no', 'dependent': False}, 'field_mLPAs': {'label_name': 'Categories', 'type': '6', 'optional': False, 'dependent': False, 'values': ['others']}, 'field_JbxVy': {'label_name': 'Query', 'type': '5', 'optional': False, 'placeholder': 'Enter query', 'dependent': False}, 'field_NMo1l': {'label_name': 'Attachment', 'type': '7', 'optional': True, 'dependent': False}}})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/save-raise-ticket-form/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], "500")

        client.logout()

    def test_GetLiveChatFollowupLeads(self):

        client = APIClient()
        client.login(username="test", password="test")

        json_string = json.dumps({"page": 1})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-followup-leads/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)
        self.assertEqual(response["total_leads"], 2)

        json_string = json.dumps({})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-followup-leads/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

    def test_GetLiveChatFollowupLeadMessagesAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        livechat_cust_obj = LiveChatCustomer.objects.get(
            username="followup_cust1")
        session_id = str(livechat_cust_obj.session_id)

        json_string = json.dumps({"session_id": session_id})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-followup-lead-messages/',
                              json.dumps({"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)

        json_string = json.dumps({"session_id": session_id + "cxd"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-followup-lead-messages/',
                              json.dumps({"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

    def test_GetLiveChatFollowupLeadAgentsAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        checked_leads = []

        livechat_cust_obj1 = LiveChatCustomer.objects.get(
            username="followup_cust1")
        livechat_cust_obj2 = LiveChatCustomer.objects.get(
            username="followup_cust2")
        checked_leads.append(str(livechat_cust_obj1.session_id))
        checked_leads.append(str(livechat_cust_obj2.session_id))

        json_string = json.dumps({"checked_leads": checked_leads})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-followup-lead-agents/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)

        json_string = json.dumps({})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-followup-lead-agents/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

        client = APIClient()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({"checked_leads": checked_leads})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-livechat-followup-lead-agents/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

    def test_TransferLiveChatFollowupLeadAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        checked_leads = []

        livechat_cust_obj = LiveChatCustomer.objects.get(
            username="followup_cust1")
        checked_leads.append(str(livechat_cust_obj.session_id))

        json_string = json.dumps(
            {"checked_leads": checked_leads, "selected_agent": "testagent"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/transfer-livechat-followup-lead/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)

        livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.get(
            livechat_customer=livechat_cust_obj)
        self.assertEqual(
            livechat_followup_cust_obj.agent_id.user.username, "testagent")

        json_string = json.dumps({"checked_leads": checked_leads})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/transfer-livechat-followup-lead/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

        client = APIClient()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps(
            {"checked_leads": checked_leads, "selected_agent": "testagent"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/transfer-livechat-followup-lead/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

    def test_CompleteLiveChatFollowupLeadAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        checked_leads = []

        livechat_cust_obj = LiveChatCustomer.objects.get(
            username="followup_cust1")
        checked_leads.append(str(livechat_cust_obj.session_id))

        json_string = json.dumps({"checked_leads": checked_leads})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/complete-livechat-followup-lead/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)
        livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.get(
            livechat_customer=livechat_cust_obj)
        self.assertEqual(livechat_followup_cust_obj.is_completed, True)

        json_string = json.dumps({})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/complete-livechat-followup-lead/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

    def test_ReinitiateWhatsAppConversationAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        livechat_cust_obj = LiveChatCustomer.objects.get(
            username="followup_cust1")
        livechat_cust_obj.is_session_exp = True
        whatsapp_channel = Channel.objects.create(name="WhatsApp")
        livechat_cust_obj.channel = whatsapp_channel
        livechat_cust_obj.save()

        json_string = json.dumps(
            {"session_id": str(livechat_cust_obj.session_id)})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/reinitiate-whatsapp-conversation/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 200)
        livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.get(
            livechat_customer=livechat_cust_obj)
        self.assertEqual(
            livechat_followup_cust_obj.is_whatsapp_conversation_reinitiated, True)

        request = client.post('/livechat/reinitiate-whatsapp-conversation/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 400)
        self.assertEqual(response["status_message"],
                         "Conversation has been already reinitiated")

        web_channel = Channel.objects.get(name="Web")
        livechat_cust_obj.channel = web_channel
        livechat_cust_obj.save()
        livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.get(
            livechat_customer=livechat_cust_obj)
        livechat_followup_cust_obj.is_whatsapp_conversation_reinitiated = False
        livechat_followup_cust_obj.save()

        request = client.post('/livechat/reinitiate-whatsapp-conversation/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 400)
        self.assertEqual(
            response["status_message"], "Conversation can be reinitiated only for WhatsApp Leads")

        json_string = json.dumps({})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/complete-livechat-followup-lead/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

    def test_GetCategoriesFromSupervisorsAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        supervisor = LiveChatUser.objects.get(
            status="2", user__username="test12345")
        supervisors_list = [supervisor.pk]

        json_string = json.dumps({"supervisors_list": supervisors_list})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-categories-from-supervisors/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        category_data = response["category_data"]
        self.assertEqual(response["status"], 200)
        self.assertEqual(len(category_data), 1)
        self.assertEqual(category_data[0]['name'], 'test - testbot')

        json_string = json.dumps({"supervisors_list": ['101']})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-categories-from-supervisors/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        category_data = response["category_data"]
        self.assertEqual(response["status"], 200)
        self.assertEqual(len(category_data), 0)

        json_string = json.dumps({})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-categories-from-supervisors/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

        client = APIClient()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({"supervisors_list": supervisors_list})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-categories-from-supervisors/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

    def test_GetAgentsFromSupervisorsAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        supervisor = LiveChatUser.objects.get(
            status="2", user__username="test12345")
        supervisors_list = [supervisor.pk]

        json_string = json.dumps({"supervisors_list": supervisors_list})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-agents-from-supervisors/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        agents_data = response["agents_data"]
        self.assertEqual(response["status"], 200)
        self.assertEqual(len(agents_data), 2)
        self.assertEqual(agents_data[0]['username'], 'test1234')
        self.assertEqual(agents_data[1]['username'], 'testagent')

        json_string = json.dumps({"supervisors_list": ['101']})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-agents-from-supervisors/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        agents_data = response["agents_data"]
        self.assertEqual(response["status"], 200)
        self.assertEqual(len(agents_data), 0)

        json_string = json.dumps({})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-agents-from-supervisors/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

        client = APIClient()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({"supervisors_list": supervisors_list})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-agents-from-supervisors/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

    def test_GetSupervisorsFromCategoriesAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        category = LiveChatCategory.objects.get(title="test")
        category_list = [category.pk]

        json_string = json.dumps({"category_list": category_list})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-supervisors-from-categories/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        supervisor_data = response['supervisor_data']
        self.assertEqual(response["status"], 200)
        self.assertEqual(supervisor_data[0]['username'], 'test')
        self.assertEqual(supervisor_data[1]['username'], 'test12345')

        json_string = json.dumps({"category_list": ['101']})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-supervisors-from-categories/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        supervisor_data = response['supervisor_data']
        self.assertEqual(response["status"], 200)
        self.assertEqual(len(supervisor_data), 1)

        json_string = json.dumps({})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-supervisors-from-categories/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

        client = APIClient()
        client.login(username="test1234", password="test1234")

        json_string = json.dumps({"category_list": category_list})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/get-supervisors-from-categories/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

    def test_CheckNewChatForAgentAPI(self):

        client = APIClient()
        client.login(username="test1234", password="test1234")

        user_obj = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234"), is_deleted=False)

        id1 = uuid.uuid4()
        id2 = uuid.uuid4()
        id3 = uuid.uuid4()
        id4 = uuid.uuid4()
        id5 = uuid.uuid4()

        LiveChatCustomer.objects.create(
            session_id=id1, agent_id=user_obj, is_session_exp=False)
        LiveChatCustomer.objects.create(
            session_id=id2, agent_id=user_obj, is_session_exp=False)

        current_assigned_customer_count = LiveChatCustomer.objects.filter(
            is_session_exp=False, agent_id=user_obj).count()

        json_string = json.dumps({
            'current_assigned_customer_count': current_assigned_customer_count,
        })

        LiveChatCustomer.objects.create(
            session_id=id3, agent_id=user_obj, is_session_exp=False)
        LiveChatCustomer.objects.create(
            session_id=id4, agent_id=user_obj, is_session_exp=False)
        LiveChatCustomer.objects.create(
            session_id=id5, agent_id=user_obj, is_session_exp=False)

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/check-newchat-for-agent/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["new_assigned_customer_count"], 3)

        client.logout()

        # API Failure

        client = APIClient()
        client.login(username="test", password="test")

        user_obj = LiveChatUser.objects.get(
            user=User.objects.get(username="test"), is_deleted=False)

        id1 = uuid.uuid4()
        id2 = uuid.uuid4()
        id3 = uuid.uuid4()
        id4 = uuid.uuid4()
        id5 = uuid.uuid4()

        LiveChatCustomer.objects.create(
            session_id=id1, agent_id=user_obj, is_session_exp=False)
        LiveChatCustomer.objects.create(
            session_id=id2, agent_id=user_obj, is_session_exp=False)

        current_assigned_customer_count = LiveChatCustomer.objects.filter(
            is_session_exp=False, agent_id=user_obj).count()

        json_string = json.dumps({
            'current_assigned_customer_count': current_assigned_customer_count
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        LiveChatCustomer.objects.create(
            session_id=id3, agent_id=user_obj, is_session_exp=False)
        LiveChatCustomer.objects.create(
            session_id=id4, agent_id=user_obj, is_session_exp=False)
        LiveChatCustomer.objects.create(
            session_id=id5, agent_id=user_obj, is_session_exp=False)

        request = client.post('/livechat/check-newchat-for-agent/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        self.assertEqual(response["status"], 500)

        client.logout()

    def test_EnableLiveChatTranscriptAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        livechat_agent_to_mark_online = LiveChatUser.objects.filter(status="3")[
            0]
        livechat_agent_to_mark_online.is_online = True
        livechat_agent_to_mark_online.save()
        livechat_customer = LiveChatCustomer.objects.all()[0]
        livechat_customer.email = "test@gmail.com"
        livechat_customer.save()

        json_string = json.dumps({
            'is_agent_request': True,
            'session_id': str(livechat_customer.session_id),
            'system_message': 'test',
            'send_system_mail_message': True,
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/enable-livechat-transcript/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        json_string = json.dumps({
            'is_agent_request': True,
            'session_id': str(uuid.uuid4()),
            'system_message': 'test',
            'send_system_mail_message': True,
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/enable-livechat-transcript/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], '500')
        self.assertEqual(
            response["status_message"], "This customer livechat session id does not exist.")

        json_string = json.dumps({
            'is_agent_request': True,
            'system_message': 'test',
            'send_system_mail_message': True,
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/enable-livechat-transcript/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], 500)
        
        client.logout()

        client = APIClient()
        json_string = json.dumps({
            'is_agent_request': True,
            'session_id': str(livechat_customer.session_id),
            'system_message': 'test',
            'send_system_mail_message': True,
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/enable-livechat-transcript/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 403)
        self.assertEqual(response['status_message'],
                         'User is not authenticated')

    def test_LiveChatTranscriptAPI(self):

        client = APIClient()
        client.login(username="test", password="test")
        livechat_agent_to_mark_online = LiveChatUser.objects.filter(status="3")[
            0]
        livechat_agent_to_mark_online.is_online = True
        livechat_agent_to_mark_online.save()
        livechat_customer = LiveChatCustomer.objects.all()[0]
        livechat_customer.email = "test@gmail.com"
        livechat_customer.save()

        json_string = json.dumps({
            'is_agent_request': True,
            'is_feedback_transcript_request': True,
            'session_id': str(livechat_customer.session_id),
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/livechat-transcript/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        json_string = json.dumps({
            'is_agent_request': True,
            'is_feedback_transcript_request': True,
            'session_id': str(uuid.uuid4()),
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/livechat-transcript/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], '500')
        self.assertEqual(
            response["status_message"], "This customer livechat session id does not exist.")

        json_string = json.dumps({
            'is_agent_request': False,
            'is_feedback_transcript_request': True,
            'session_id': str(livechat_customer.session_id),
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/livechat-transcript/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)
        
        json_string = json.dumps({
            'is_agent_request': False,
            'is_feedback_transcript_request': True,
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/livechat-transcript/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status_code"], 500)

        client.logout()

        client = APIClient()
        json_string = json.dumps({
            'is_agent_request': True,
            'is_feedback_transcript_request': True,
            'session_id': str(livechat_customer.session_id),
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/livechat/livechat-transcript/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 403)
        self.assertEqual(response['status_message'],
                         'User is not authenticated')
