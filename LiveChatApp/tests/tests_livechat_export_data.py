from __future__ import unicode_literals

from django.test import TestCase
from rest_framework.test import APIClient
from EasyChatApp.models import Bot, User, MISDashboard, Channel
from LiveChatApp.models import LiveChatUser, LiveChatCustomer, CannedResponse, LiveChatConfig, LiveChatCategory,\
    LiveChatBlackListKeyword, LiveChatAuditTrail, LiveChatCalender, LiveChatMISDashboard, LiveChatAdminConfig, LiveChatProcessors, LiveChatDeveloperProcessor, LiveChatDataExportRequest
from LiveChatApp.utils import get_time, is_agent_live
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.constants_processors import LIVECHAT_PROCESSOR_EXAMPLE, LIVECHAT_PROCESSOR_EXAMPLE_END_CHAT
import logging
import json
import random
import execjs
import base64
from datetime import datetime, timedelta
from Crypto import Random
from Crypto.Cipher import AES
import os
import shutil
from django.conf import settings
from zipfile import ZipFile
from xlsxwriter import Workbook


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
    function tested: test_ExportDataAPI
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

    def test_ExportDataAPI(self):

        # Admin and supervisor has the ability to download reports
        api_to_call = '/livechat/exportdata/'
        client = APIClient()
        client.login(username="test", password="test")
        if not os.path.exists(settings.MEDIA_ROOT + 'livechat-chat-history/test'):
            os.makedirs(settings.MEDIA_ROOT + 'livechat-chat-history/test')

        # today = datetime.now()
        # yesterday = today - timedelta(1)
        # filename = "livechat-chat-history/test/chat_history_" + \
        #     str(yesterday.date()) + '.xls'
        # test_wb = Workbook(settings.MEDIA_ROOT + filename)
        json_string = json.dumps({'selected_filter_value': "1", "selected_report_type": "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 8):
        #     date = today - timedelta(index)
        #     filename = "livechat-chat-history/test/chat_history_" + \
        #         str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "2", "selected_report_type": "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 31):
        #     date = today - timedelta(index)
        #     filename = "livechat-chat-history/test/chat_history_" + \
        #         str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "3", "selected_report_type": "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        if os.path.exists(settings.MEDIA_ROOT + 'livechat-chat-history/test'):
            shutil.rmtree(settings.MEDIA_ROOT + 'livechat-chat-history/test')
            # os.system(cmd)
        client.logout()

        # If excel and zip is not made, response["export_path_exist"] == False
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({'selected_filter_value': "1", "selected_report_type": "1"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], False)

        json_string = json.dumps({'selected_filter_value': "2"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)

        json_string = json.dumps({'selected_filter_value': "3"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)
        client.logout()

        # Agent is not allowed to download excels.

        client.login(username="test1234", password="test1234")
        json_string = json.dumps({'selected_filter_value': "1", "selected_report_type": "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "2", "selected_report_type": "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "3", "selected_report_type": "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)
        client.logout()

    def test_MissedChatsExportDataAPI(self):

        # Admin and supervisor has the ability to download reports
        api_to_call = "/livechat/missed-chats-exportdata/"
        report_type_name_for_test_user = "livechat-missed-chats-report/test"
        # type_of_filename = "livechat-offline-message-report/test/offline_message_report_"
        client = APIClient()
        client.login(username="test", password="test")
        if not os.path.exists(settings.MEDIA_ROOT + report_type_name_for_test_user):
            os.makedirs(settings.MEDIA_ROOT + report_type_name_for_test_user)

        # today = datetime.now()
        # yesterday = today - timedelta(1)
        # filename = type_of_filename + str(yesterday.date()) + '.xls'
        # test_wb = Workbook(settings.MEDIA_ROOT + filename)
        json_string = json.dumps({'selected_filter_value': "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 8):
        #     date = today - timedelta(index)
        #     filename = type_of_filename + str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "2"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 31):
        #     date = today - timedelta(index)
        #     filename = type_of_filename + str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "3"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        if os.path.exists(settings.MEDIA_ROOT + report_type_name_for_test_user):
            shutil.rmtree(settings.MEDIA_ROOT +
                          report_type_name_for_test_user)
        client.logout()

        # If excel and zip is not made, response["export_path_exist"] == False
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({'selected_filter_value': "1"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], False)

        json_string = json.dumps({'selected_filter_value': "2"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)

        json_string = json.dumps({'selected_filter_value': "3"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)
        client.logout()

        # Agent is not allowed to download excels.

        client.login(username="test1234", password="test1234")
        json_string = json.dumps({'selected_filter_value': "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "2"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "3"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)
        client.logout()

    def test_LoginLogoutReportExportDataAPI(self):

        # Admin and supervisor has the ability to download reports
        api_to_call = "/livechat/login-logout-report-exportdata/"
        report_type_name_for_test_user = "livechat-login-logout-report/test"
        # type_of_filename = "livechat-login-logout-report/test/login_logout_report_"
        client = APIClient()
        client.login(username="test", password="test")
        if not os.path.exists(settings.MEDIA_ROOT + report_type_name_for_test_user):
            os.makedirs(settings.MEDIA_ROOT + report_type_name_for_test_user)

        # today = datetime.now()
        # yesterday = today - timedelta(1)
        # filename = type_of_filename + str(yesterday.date()) + '.xls'
        # test_wb = Workbook(settings.MEDIA_ROOT + filename)
        json_string = json.dumps({'selected_filter_value': "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 8):
        #     date = today - timedelta(index)
        #     filename = type_of_filename + str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "2"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 31):
        #     date = today - timedelta(index)
        #     filename = type_of_filename + str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "3"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        if os.path.exists(settings.MEDIA_ROOT + report_type_name_for_test_user):
            shutil.rmtree(settings.MEDIA_ROOT +
                          report_type_name_for_test_user)
        client.logout()

        # If excel and zip is not made, response["export_path_exist"] == False
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({'selected_filter_value': "1"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], False)

        json_string = json.dumps({'selected_filter_value': "2"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)

        json_string = json.dumps({'selected_filter_value': "3"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)
        client.logout()

        # Agent is not allowed to download excels.

        client.login(username="test1234", password="test1234")
        json_string = json.dumps({'selected_filter_value': "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "2"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "3"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)
        client.logout()

    def test_AgentNotReadyReportExportDataAPI(self):

        # Admin and supervisor has the ability to download reports
        api_to_call = "/livechat/agent-not-ready-report-exportdata/"
        report_type_name_for_test_user = "livechat-agent-not-ready-report/test"
        # type_of_filename = "livechat-agent-not-ready-report/test/agent_not_ready_report_"
        client = APIClient()
        client.login(username="test", password="test")
        if not os.path.exists(settings.MEDIA_ROOT + report_type_name_for_test_user):
            os.makedirs(settings.MEDIA_ROOT + report_type_name_for_test_user)

        # today = datetime.now()
        # yesterday = today - timedelta(1)
        # filename = type_of_filename + str(yesterday.date()) + '.xls'
        # test_wb = Workbook(settings.MEDIA_ROOT + filename)
        json_string = json.dumps({'selected_filter_value': "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 8):
        #     date = today - timedelta(index)
        #     filename = type_of_filename + str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "2"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 31):
        #     date = today - timedelta(index)
        #     filename = type_of_filename + str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "3"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        if os.path.exists(settings.MEDIA_ROOT + report_type_name_for_test_user):
            shutil.rmtree(settings.MEDIA_ROOT +
                          report_type_name_for_test_user)
        client.logout()

        # If excel and zip is not made, response["export_path_exist"] == False
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({'selected_filter_value': "1"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], False)

        json_string = json.dumps({'selected_filter_value': "2"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)

        json_string = json.dumps({'selected_filter_value': "3"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)
        client.logout()

        # Agent is not allowed to download excels.

        client.login(username="test1234", password="test1234")
        json_string = json.dumps({'selected_filter_value': "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "2"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "3"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)
        client.logout()

    def test_AgentPerformanceReportExportDataAPI(self):

        # Admin and supervisor has the ability to download reports
        api_to_call = "/livechat/agent-performance-report-exportdata/"
        report_type_name_for_test_user = "livechat-agent-performance-report/test"
        # type_of_filename = "livechat-agent-performance-report/test/agent_performance_report_"
        client = APIClient()
        client.login(username="test", password="test")
        if not os.path.exists(settings.MEDIA_ROOT + report_type_name_for_test_user):
            os.makedirs(settings.MEDIA_ROOT + report_type_name_for_test_user)

        # today = datetime.now()
        # yesterday = today - timedelta(1)
        # filename = type_of_filename + str(yesterday.date()) + '.xls'
        # test_wb = Workbook(settings.MEDIA_ROOT + filename)
        json_string = json.dumps({'selected_filter_value': "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 8):
        #     date = today - timedelta(index)
        #     filename = type_of_filename + str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "2"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 31):
        #     date = today - timedelta(index)
        #     filename = type_of_filename + str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "3"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        if os.path.exists(settings.MEDIA_ROOT + report_type_name_for_test_user):
            shutil.rmtree(settings.MEDIA_ROOT +
                          report_type_name_for_test_user)
        client.logout()

        # If excel and zip is not made, response["export_path_exist"] == False
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({'selected_filter_value': "1"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], False)

        json_string = json.dumps({'selected_filter_value': "2"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)

        json_string = json.dumps({'selected_filter_value': "3"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)
        client.logout()

        # Agent is not allowed to download excels.

        client.login(username="test1234", password="test1234")
        json_string = json.dumps({'selected_filter_value': "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "2"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "3"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)
        client.logout()

    def test_HourlyInteractionCountExportDataAPI(self):

        # Admin and supervisor has the ability to download reports
        api_to_call = "/livechat/hourly-interaction-count-exportdata/"
        report_type_name_for_test_user = "livechat-hourly-interaction-report/test"
        # type_of_filename = "livechat-hourly-interaction-report/test/hourly_interaction_report_"
        client = APIClient()
        client.login(username="test", password="test")
        if not os.path.exists(settings.MEDIA_ROOT + report_type_name_for_test_user):
            os.makedirs(settings.MEDIA_ROOT + report_type_name_for_test_user)

        # today = datetime.now()
        # yesterday = today - timedelta(1)
        # filename = type_of_filename + str(yesterday.date()) + '.xls'
        # test_wb = Workbook(settings.MEDIA_ROOT + filename)
        json_string = json.dumps({'selected_filter_value': "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 8):
        #     date = today - timedelta(index)
        #     filename = type_of_filename + str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "2"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 31):
        #     date = today - timedelta(index)
        #     filename = type_of_filename + str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "3"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        if os.path.exists(settings.MEDIA_ROOT + report_type_name_for_test_user):
            shutil.rmtree(settings.MEDIA_ROOT +
                          report_type_name_for_test_user)
        client.logout()

        # If excel and zip is not made, response["export_path_exist"] == False
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({'selected_filter_value': "1"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], False)

        json_string = json.dumps({'selected_filter_value': "2"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)

        json_string = json.dumps({'selected_filter_value': "3"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)
        client.logout()

        # Agent is not allowed to download excels.

        client.login(username="test1234", password="test1234")
        json_string = json.dumps({'selected_filter_value': "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "2"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "3"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)
        client.logout()

    def test_DailyInteractionCountExportDataAPI(self):

        # Admin and supervisor has the ability to download reports
        api_to_call = "/livechat/dailey-interaction-count-exportdata/"
        report_type_name_for_test_user = "livechat-daily-interaction-report/test"
        # type_of_filename = "livechat-daily-interaction-report/test/daily_interaction_report_"
        client = APIClient()
        client.login(username="test", password="test")
        if not os.path.exists(settings.MEDIA_ROOT + report_type_name_for_test_user):
            os.makedirs(settings.MEDIA_ROOT + report_type_name_for_test_user)

        # today = datetime.now()
        # yesterday = today - timedelta(1)
        # filename = type_of_filename + str(yesterday.date()) + '.xls'
        # test_wb = Workbook(settings.MEDIA_ROOT + filename)
        json_string = json.dumps({'selected_filter_value': "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 8):
        #     date = today - timedelta(index)
        #     filename = type_of_filename + str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "2"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        # for index in range(1, 31):
        #     date = today - timedelta(index)
        #     filename = type_of_filename + str(date.date()) + '.xls'
        #     test_wb = Workbook(settings.MEDIA_ROOT + filename)

        json_string = json.dumps({'selected_filter_value': "3"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)

        if os.path.exists(settings.MEDIA_ROOT + report_type_name_for_test_user):
            shutil.rmtree(settings.MEDIA_ROOT +
                          report_type_name_for_test_user)
        client.logout()

        # If excel and zip is not made, response["export_path_exist"] == False
        client.login(username="test12345", password="test12345")
        json_string = json.dumps({'selected_filter_value': "1"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], False)

        json_string = json.dumps({'selected_filter_value': "2"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)

        json_string = json.dumps({'selected_filter_value': "3"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 500)
        client.logout()

        # Agent is not allowed to download excels.

        client.login(username="test1234", password="test1234")
        json_string = json.dumps({'selected_filter_value': "1"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "2"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)

        json_string = json.dumps({'selected_filter_value': "3"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(api_to_call, json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["export_path_exist"], None)
        client.logout()
