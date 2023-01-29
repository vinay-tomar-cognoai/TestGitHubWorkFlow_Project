# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from rest_framework.test import APIClient
from EasyChatApp.models import AccessType, Bot, EventProgress, User, MISDashboard, Profile, Feedback, Channel, Tree, Intent, Config, BotResponse,\
    BotChannel, EasyChatQueryToken, ChunksOfSuggestions, EasyChatSessionIDGenerator, SandboxUser, Language, RequiredBotTemplate, EasyChatTheme
from EasyChatApp.utils_custom_encryption import CustomEncrypt
from EasyChatApp.utils_bot import create_language_en_template, check_and_create_default_language_object
from LiveChatApp.models import LiveChatUser, LiveChatCustomer, CannedResponse, LiveChatConfig
from LiveChatApp.utils import get_time, is_agent_live
from requests.auth import HTTPBasicAuth
from EasyChatApp.constants import DEFAULT_THEME_IMAGE_DICT
# from EasyChatApp.utils_custom_encryption import *
import logging
import json
import re
import sys
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
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        Config.objects.create()
        LiveChatConfig.objects.create(max_customer_count=110)
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        MISDashboard.objects.create(
            user_id="1", bot=bot_obj, message_received="hi", bot_response="how may I assist you?", session_id="123")
        MISDashboard.objects.create(
            user_id="2", bot=bot_obj, message_received="hello", bot_response="how may I assist you?", session_id="123")
        MISDashboard.objects.create(
            user_id="4", bot=bot_obj, message_received="hi", bot_response="how may I assist you?", session_id="123")
        MISDashboard.objects.create(
            user_id="4", bot=bot_obj, message_received="Hi", bot_response="hello", session_id="123")
        User.objects.create(
            role="1", status="1", username="test", password="test")
        Profile.objects.create(user_id="tests1")
        Profile.objects.create(user_id="tests11")
        Profile.objects.create(user_id="tests111")
        web_channel = Channel.objects.create(name="Web")
        Channel.objects.create(name="Whatsapp")
        Channel.objects.create(name="Alexa")
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}')
        tree_obj = Tree.objects.create(name="Hi", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Hi", tree=tree_obj, keywords='{"0": "hey", "1": "hello", "2": "hi", "3": "whats"}', training_data='{"0": "Hey", "1": " hello", "2": " hi", "3": " whats up"}')
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()
        MISDashboard.objects.create(user_id="tests1", bot=bot_obj, message_received="hi",
                                    intent_recognized=intent_obj, intent_name="Hi", bot_response="how may I assist you?", session_id="123")

    """
    function tested: SaveWatsAppEmailConfigAPI
    input queries:
       
    expected output:
        return status code 200 if Success
    checks for:
        update log file every second
    """

    def test_SaveWatsAppEmailConfigAPI(self):
        logger.info("Testing test_SaveWatsAppEmailConfigAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting SaveWatsAppEmailConfigAPI is going on...\n")
        client = APIClient()
        User.objects.create(username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")
        bot_obj = Bot.objects.all()[0]
        bot_channel_obj = BotChannel.objects.create(
            bot=bot_obj, channel=Channel.objects.get(name="Whatsapp"))
        json_string = json.dumps({
            "bot_channel_pk": "-1",
            "mail_sender_time_interval": "1",
            "mail_sent_to_list": []
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/save-whatsapp-email-config/', json.dumps({'data': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 500)

        json_string = json.dumps({
            "bot_channel_pk": bot_channel_obj.pk,
            "mail_sender_time_interval": "1",
            "mail_sent_to_list": ['testing@allincall.in']
        })
        request = client.post(
            '/chat/save-whatsapp-email-config/', json.dumps({'data': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)

        bot_channel_obj = BotChannel.objects.all()[0]

        self.assertEqual(bot_channel_obj.mail_sender_time_interval, 1)
        self.assertEqual(json.loads(bot_channel_obj.mail_sent_to_list)[
                         "items"], ['testing@allincall.in'])

    """
    function tested: SaveAPIFailEmailConfigAPI
    input queries:
       
    expected output:
        return status code 200 if Success
    checks for:
        update log file every second
    """

    def test_SaveAPIFailEmailConfigAPI(self):
        logger.info("Testing test_SaveAPIFailEmailConfigAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting SaveAPIFailEmailConfigAPI is going on...\n")
        client = APIClient()
        user_obj = User.objects.create(username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")
        bot_obj = Bot.objects.all()[0]
        bot_obj.users.add(user_obj)
        bot_obj.save()
        json_string = json.dumps({
            "bot_id": "-1",
            "mail_sender_time_interval": "1",
            "mail_sent_to_list": [],
            "from_processor": "false"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/save-api-fail-email-config/', json.dumps({'data': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 500)

        json_string = json.dumps({
            "bot_id": bot_obj.pk,
            "mail_sender_time_interval": "1",
            "mail_sent_to_list": ['testing@allincall.in'],
            "from_processor": "false"
        })
        request = client.post(
            '/chat/save-api-fail-email-config/', json.dumps({'data': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)

        bot_obj = Bot.objects.all()[0]

        self.assertEqual(bot_obj.mail_sender_time_interval, 1)
        self.assertEqual(json.loads(bot_obj.mail_sent_to_list)
                         ["items"], ['testing@allincall.in'])

    """
    function tested: UpdateLogFileAPI
    input queries:
       
    expected output:
        return status code 200 if Success
    checks for:
        update log file every second
    """

    def test_UpdateLogFileAPI(self):
        logger.info("Testing test_UpdateLogFileAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting UpdateLogFileAPI is going on...\n")
        client = APIClient()
        User.objects.create(username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")
        # bot_obj = Bot.objects.all()[0]
        json_string = json.dumps({

        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/update-log-file/', json.dumps({'data': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 500)

        request = client.post(
            '/chat/update-log-file/', json.dumps({'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)

    """
    function tested: test_EnableSmallTalk
    input queries:
       bot id
    expected output:
        return status code 200 if Success
    checks for:
        enable all small talk
    """

    def test_EnableSmallTalk(self):
        logger.info("Testing test_EnableSmallTalk...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        User.objects.create(username="temporary", password="temporary")
        user = User.objects.get(username='temporary')
        user.set_password('12345')
        user.save()
        c = Client()
        c.login(username='temporary', password='12345')
        # user_obj = User.objects.get(username="temporary")
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")

        raw_data = {
            "bot_id": bot_obj.pk
        }
        json_string = json.dumps(raw_data)
        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(json_string)
        response = c.post(
            '/chat/enable-small-talk/', {"data": data}, follow=True)
        response = json.loads(custom_encrypt_obj.decrypt(
            response.json()))
        self.assertEqual(response["status"], 200)

        # Incorrect data
        raw_data = {
            "bot_id": "12"
        }
        json_string = json.dumps(raw_data)
        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(json_string)
        response = c.post(
            '/chat/enable-small-talk/', {"data": data}, follow=True)
        print(response)
        response = json.loads(custom_encrypt_obj.decrypt(
            response.json()))
        self.assertEqual(response["status"], 500)

    """
    function tested: test_DisableSmallTalk
    input queries:
       bot id
    expected output:
        return status code 200 if Success
    checks for:
        disable all small talk
    """

    def test_DisableSmallTalk(self):
        logger.info("Testing test_DisableSmallTalk...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        User.objects.create(username="temporary", password="temporary")
        user = User.objects.get(username='temporary')
        user.set_password('12345')
        user.save()
        c = Client()
        c.login(username='temporary', password='12345')
        # user_obj = User.objects.get(username="temporary")
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")

        raw_data = {
            "bot_id": bot_obj.pk
        }
        json_string = json.dumps(raw_data)
        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(json_string)
        response = c.post(
            '/chat/disable-small-talk/', {"data": data}, follow=True)
        response = json.loads(custom_encrypt_obj.decrypt(
            response.json()))
        self.assertEqual(response["status"], 200)

        # Incorrect data
        raw_data = {
            "bot_id": "12"
        }
        json_string = json.dumps(raw_data)
        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(json_string)
        response = c.post(
            '/chat/disable-small-talk/', {"data": data}, follow=True)
        response = json.loads(custom_encrypt_obj.decrypt(
            response.json()))
        self.assertEqual(response["status"], 500)

    """
    API Tested: GetGeneralDetailsAPI
    input queries:
        selected_bot_pk:
    expected output:
        status: 200 // SUCCESS
    Return:
        return basic details of a bot. Ex. return the flow_termination_keywords and flow_termination_bot_response
    """

    def test_GetGeneralDetailsAPI(self):
        logger.info("Testing GetGeneralDetailsAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting GetGeneralDetailsAPI is going on...\n")
        client = APIClient()
        User.objects.create(username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")
        bot_obj = Bot.objects.all()[0]
        json_string = json.dumps({
            "selected_bot_pk": bot_obj.pk,
            "selected_language": "en"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/bot/get-general-details/', json.dumps({'data': json_string}), content_type='application/json')
        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)
        self.assertEqual(
            response["flow_termination_keywords"], ['stop', 'exit'])
        self.assertEqual(response["flow_termination_bot_response"],
                         'Hi, this is your virtual assistant. Please type "Hi" to start chatting with me.')

        bot_obj.flow_termination_bot_response = "Thank you"
        bot_obj.flow_termination_keywords = json.dumps(
            {"items": ["testing", "testing1", "testing11"]})
        bot_obj.stop_keywords = ['an', 'the']
        bot_obj.save()

        request = client.post(
            '/chat/bot/get-general-details/', json.dumps({'data': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["flow_termination_keywords"], [
                         "testing", "testing1", "testing11"])
        self.assertEqual(
            response["flow_termination_bot_response"], "Thank you")

        self.assertEqual(
            response["stop_words"], "['an', 'the']")

        json_string = json.dumps({
            "selected_bot_pk": "-1",
            "selected_language": "hi"
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/bot/get-general-details/', json.dumps({'data': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 500

        json_string = json.dumps({
            "selected_bot": "1",
            "selected_language": "en"
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/bot/get-general-details/', json.dumps({'data': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 500

    """
    API Tested: GetTrainingDataAPI
    input queries:
        bot_id:
        bot_name: "uat" or other name
    expected output:
        status: 200 // SUCCESS
    Return:
        return basic details of a bot. Ex. return the suggestion list and max_suggestion limit, word_mapper_list etc
    """

    # def test_GetTrainingDataAPI(self):
    #     logger.info("Testing GetTrainingDataAPI is going on...", extra={
    #                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    #     print("\nTesting GetTrainingDataAPI is going on...\n")
    #     client = APIClient()

    #     bot_obj = Bot.objects.all()[0]
    #     bot_obj.max_suggestions = 5
    #     bot_obj.save()
    #     json_string = json.dumps({
    #         "bot_id": bot_obj.pk,
    #         "bot_name": "uat",
    #         "web_page": "www.google.com"
    #     })

    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post(
    #         '/chat/get-data/', json.dumps({'json_string': json_string}), content_type='application/json')

    #     response = json.loads(custom_encrypt_obj.decrypt(request.data))
    #     assert request.status_code == 200
    #     assert response["status"] == 200
    #     assert response["max_suggestions"] == 5
    #     assert response["word_mapper_list"] == []

    #     key_list = []

    #     for item in response["sentence_list"]:
    #         try:
    #             key_list.append(item["key"].decode('utf-8').lower())
    #         except Exception:
    #             key_list.append(item["key"].lower())
    #         try:
    #             assert item["value"].decode('utf-8') == "Hi"
    #         except Exception:
    #             assert item["value"] == "Hi"

    #     training_data = json.loads(Intent.objects.all()[0].training_data)
    #     training_data = list(training_data.values())

    #     training_data_list = []
    #     for item in training_data:
    #         training_data_list.append(item.lower())
    #     training_data_list.append("hi")
    #     training_data_list.sort()
    #     key_list.sort()

    #     self.assertEqual(key_list, training_data_list)

    #     json_string = json.dumps({
    #         "bot_id": 11,
    #         "bot_name": "uat"
    #     })

    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post(
    #         '/chat/get-data/', json.dumps({'json_string': json_string}), content_type='application/json')

    #     response = json.loads(custom_encrypt_obj.decrypt(request.data))
    #     assert request.status_code == 200
    #     assert response["status"] == 500

    """
    API Tested: ClearUserDataAPI
    input queries:
        user_id: user id of easychat customer
    expected output:
        status: 200 // SUCCESS
    Return:
        Clears data of easychat customer from data model.
    """

    def test_ClearUserDataAPI(self):
        logger.info("Testing ClearUserDataAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting ClearUserDataAPI is going on...\n")
        token_id = EasyChatQueryToken.objects.create().token
        client = APIClient()

        # bot_obj = Bot.objects.all()[0]
        # user_obj = Profile.objects.create(user_id="123")
        channel_params = json.dumps({
            "session_id": "123",
            "window_location": 'localhost',
            "is_form_assist": False,
            "attached_file_src": "",
            "file_extension": "",
            "is_save_attachment_required": False
        })
        json_string = json.dumps({
            "query_token_id": str(token_id),
            "message": "Hi",
            "user_id": "123",
            "channel": "Web",
            "channel_params": channel_params,
            "bot_id": 1,
            "bot_name": "uat",
            "bot_display_name": "testbot"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post(
            '/chat/query/', json.dumps({'json_string': json_string}), content_type='application/json')

        json_string = json.dumps({
            "user_id": "123",
            "bot_id": 1,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/clear-user-data/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 200

        json_string = json.dumps({
            "user_id": "1234",
            "bot_id": 1,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/clear-user-data/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 200

    """
    API Tested: GetChannelDetailsAPI
    input queries:
        bot_id: pk of current bot
        bot_name: "uat" or may be othername
        user_id:
        session_id:
        channel_name: name of channel by which bot is getting the equest.
    expected output:
        status: 200 // SUCCESS
    Return:
        return the basic details of bot...like welcome message, banners etc.
    """

    def test_GetChannelDetailsAPI(self):
        logger.info("Testing GetChannelDetailsAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting GetChannelDetailsAPI is going on...\n")

        bot_obj = Bot.objects.all()[0]
        bot_obj.initial_intent = Intent.objects.all()[0]
        BotChannel.objects.create(
            bot=bot_obj, channel=Channel.objects.get(name="Web"))

        client = APIClient()
        json_string = json.dumps({
            "bot_id": bot_obj.pk,
            "bot_name": "uat",
            "user_id": "123",
            "session_id": "123",
            "channel_name": "Web",
            "selected_language": "en",
            "bot_web_page": "www.geeks.com",
            "web_page_source": "https://www.google.com",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-channel-details/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 200
        assert response["initial_intent"] != ""

        json_string = json.dumps({
            "bot_id": 11,
            "bot_name": "uat",
            "user_id": "123",
            "session_id": "123",
            "channel_name": "Web",
            "selected_language": "en",
            "bot_web_page": "www.geeks.com",
            "web_page_source": "https://www.google.com",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-channel-details/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 500

    """
    API Tested: GetBotMessageImageAPI
    input queries:
        bot_id: pk of current bot
    expected output:
        status: 200 // SUCCESS
    Return:
        return the bot theme color, path of bot message image, bot display name and bot terms and conditions.
    """

    def test_GetBotMessageImageAPI(self):
        logger.info("Testing GetBotMessageImageAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting GetBotMessageImageAPI is going on...\n")

        bot_obj = Bot.objects.all()[0]
        bot_obj.message_image = "/static/EasyChatApp/img/test.png"
        bot_obj.save()

        client = APIClient()
        json_string = json.dumps({
            "bot_id": bot_obj.pk,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-bot-message-image/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 200
        assert response[
            "bot_message_image_url"] == "/static/EasyChatApp/img/test.png"

        json_string = json.dumps({
            "bot_id": 11,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-bot-message-image/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 500

    """
    API Tested: QueryAPI
    input queries:
        feedback_id: user id of customer
        feedback_type: session id assigned to the customer for his session
        feedback_cnt: bot pk of customer
    expected output:
        status: 200 // SUCCESS
    checks for:
        This API call is used to record the user feedback for specific intent during chat.
    """

    # def test_QueryAPI(self):
    #     logger.info("Testing QueryAPI is going on...", extra={
    #                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    #     print("\nTesting QueryAPI is going on...\n")
    #     mis_objs = MISDashboard.objects.all()
    #     token_id = EasyChatQueryToken.objects.create().token
    #     channel_params = json.dumps({
    #         "session_id": "123",
    #         "window_location": 'localhost',
    #         "is_form_assist": False,
    #         "attached_file_src": "",
    #         "file_extension": "",
    #         "is_save_attachment_required": False,
    #         "is_sticky_message": False,
    #         "is_video_recorder_allowed": False,
    #         "is_campaign_link": False
    #     })

    #     client = APIClient()
    #     json_string = json.dumps({
    #         "query_token_id": str(token_id),
    #         "message": "Byi",
    #         "user_id": "123",
    #         "channel": "Web",
    #         "channel_params": channel_params,
    #         "bot_id": 1,
    #         "bot_name": "uat",
    #         "bot_display_name": "testbot"
    #     })

    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)

    #     request = client.post(
    #         '/chat/query/', json.dumps({'json_string': json_string}), content_type='application/json')

    #     response = json.loads(custom_encrypt_obj.decrypt(request.data))
    #     assert request.status_code == 200
    #     assert response["status_code"] == "200"
    #     assert response["status_message"] == "SUCCESS"

    #     json_string = json.dumps({
    #         "query_token_id": str(token_id),
    #         "message": "Hi",
    #         "user_id": "123",
    #         "channel": "Web",
    #         "channel_params": channel_params,
    #         "bot_id": 1,
    #         "bot_name": "uat",
    #         "bot_display_name": "testbot"
    #     })

    #     custom_encrypt_obj = CustomEncrypt()
    #     json_string = custom_encrypt_obj.encrypt(json_string)
    #     request = client.post(
    #         '/chat/query/', json.dumps({'json_string': json_string}), content_type='application/json')

    #     response = json.loads(custom_encrypt_obj.decrypt(request.data))
    #     assert request.status_code == 200
    #     assert response["status_message"] == "SUCCESS"

    #     assert response["response"]["speech_response"][
    #         "text"] == "Hi! How may I assist you?"
    #     assert response["response"]["cards"] == []
    #     assert response["response"]["images"] == []
    #     assert response["response"]["videos"] == []
    #     assert response["response"]["choices"] == []
    #     assert response["response"]["recommendations"] == []
    #     assert response["response"]["google_search_results"] == []

    #     bot_response_obj = BotResponse.objects.all()[0]
    #     bot_response_obj.images = "{\"items\":['https://easychat-dev.allincall.in/files/nature_03j22fB.jpg']}"
    #     bot_response_obj.videos = "{\"items\":['https://easychat-dev.allincall.in/files/nature_03j22fB.jpg']}"
    #     bot_response_obj.table = "{\"items\":['https://easychat-dev.allincall.in/files/nature_03j22fB.jpg']}"
    #     bot_response_obj.cards = "{\"items\":['https://easychat-dev.allincall.in/files/nature_03j22fB.jpg']}"

    #     bot_response_obj.save()
    #     request = client.post('/chat/query/', json.dumps({'json_string': json_string}), content_type='application/json')

    #     print(response)

    """
    API Tested: SaveFeedbackAPI
    input queries:
        user_id: user id of customer
        session_id: session id assigned to the customer for his session
        bot_id: bot pk of customer
        comments: optional --> It may be empty
        rating: rating given by livechat customer
    expected output:
        status: 200 // SUCCESS
    checks for:
        updates the rate value of easychat customer. Also crosscheck the updated rated value.
    """

    def test_SaveFeedbackAPI(self):
        logger.info("Testing SaveFeedbackAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting SaveFeedbackAPI is going on...\n")

        client = APIClient()
        livechat_customer = Profile.objects.all()

        for customer in livechat_customer:
            val = random.randint(1, 10)
            json_string = json.dumps({
                'user_id': customer.user_id,
                'session_id': customer.user_id,
                'bot_id': 1,
                'comments': "feedback submitted",
                'rating': val,
                'feedback_country_code': "",
                'feedback_phone_number': "",
                'feedback_email_id': "",
                'checkbox_csat_clicked_list': "",
                'channel_name': "Web"
            })
            custom_encrypt_obj = CustomEncrypt()
            json_string = custom_encrypt_obj.encrypt(json_string)

            request = client.post('/chat/save-feedback/', json.dumps(
                {'json_string': json_string}), content_type='application/json')

            response = json.loads(custom_encrypt_obj.decrypt(request.data))
            assert request.status_code == 200
            assert response["status"] == 200

            feedback_obj = Feedback.objects.get(
                user_id=customer.user_id)

            assert feedback_obj.rating == val

            # json_string = json.dumps("")
            # custom_encrypt_obj = CustomEncrypt()
            # json_string = custom_encrypt_obj.encrypt(json_string)
            # request = client.post('/chat/save-feedback/', json.dumps(
            #     {'json_string': json_string}), content_type='application/json')

            # assert request.status_code == 200
            # assert response["status"] == 500

    """
    API Tested: SaveEasyChatIntentFeedbackAPI
    input queries:
        feedback_id: user id of customer
        feedback_type: session id assigned to the customer for his session
        feedback_cnt: bot pk of customer
    expected output:
        status: 200 // SUCCESS
    checks for:
        This API call is used to record the user feedback for specific intent during chat.
    """

    def test_SaveEasyChatIntentFeedbackAPI(self):
        logger.info("Testing SaveEasyChatIntentFeedbackAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting SaveEasyChatIntentFeedbackAPI is going on...\n")

        mis_objs = MISDashboard.objects.all()

        client = APIClient()
        for mis_obj in mis_objs:
            json_string = json.dumps({
                "session_id": mis_obj.session_id,
                "user_id": mis_obj.user_id,
                "feedback_id": mis_obj.pk,
                "feedback_type": random.randint(1, 2),
                "feedback_cmt": "It was awesome."
            })

            custom_encrypt_obj = CustomEncrypt()
            json_string = custom_encrypt_obj.encrypt(json_string)

            request = client.post('/chat/save-easychat-feedback-msg/', json.dumps(
                {'json_string': json_string}), content_type='application/json')

            response = json.loads(custom_encrypt_obj.decrypt(request.data))
            assert request.status_code == 200
            assert response["status"] == 200

        json_string = ""

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/chat/save-easychat-feedback-msg/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 500

    """
    API Tested: SaveImageLocallyAPI
    input queries:
        feedback_id: user id of customer
        feedback_type: session id assigned to the customer for his session
        feedback_cnt: bot pk of customer
    expected output:
        status: 200 // SUCCESS
    checks for:
        This API call is used to record the user feedback for specific intent during chat.
    """

    def test_SaveImageLocallyAPI(self):
        logger.info("Testing SaveImageLocallyAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting SaveImageLocallyAPI is going on...\n")

        client = APIClient()
        json_string = json.dumps({
            "image_url": "https://image.shutterstock.com/image-photo/spotted-dear-chital-knha-national-260nw-1024196245.jpg",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/save-image-locally/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 200

        json_string = json.dumps({
            "image_url": "",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/save-image-locally/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 500

    """
    API Tested: AddMessagewithIntentAPI
    input queries:
        intent_pk: Intent to which the message needs to be added
        message_history_ids: List of IDs of the messages
        feedback_cnt: bot pk of customer
    expected output:
        status: 200 // SUCCESS
    checks for:
        This API call is used to record the user feedback for specific intent during chat.
    """

    def test_AddMessageWithIntentAPI(self):
        logger.info("Testing AddMessageWithIntentAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting AddMessageWithIntentAPI is going on...\n")

        User.objects.create(username="temporary", password="temporary")
        user = User.objects.get(username='temporary')
        user.set_password('12345')
        user.save()

        client = Client()
        client.login(username='temporary', password='12345')

        payload = {
            'intent_pk': 1,
            'message_history_ids': [1, 2]
        }

        request = client.post('/chat/match-message-with-intent/',
                              json.dumps(payload), content_type="application/json")
        logger.info(request.data, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response = request.data
        assert request.status_code == 200
        assert response["status"] == 200

        payload = {
            'intent_pk': 1,
            'message_history_ids': [1, 2]
        }

        request = client.post('/chat/match-message-with-intent/',
                              json.dumps(payload), content_type="application/json")
        response = request.data
        assert request.status_code == 200
        assert response["status"] == 300

        payload = {
            'intent_pk': 1000,
            'message_history_ids': [1, 2]
        }

        request = client.post('/chat/match-message-with-intent/',
                              json.dumps(payload), content_type="application/json")
        response = request.data
        assert request.status_code == 200
        assert response["status"] == 500

        payload = {
            'intent_pk': 1,
            'message_history_ids': [1000, 2]
        }

        request = client.post('/chat/match-message-with-intent/',
                              json.dumps(payload), content_type="application/json")
        response = request.data
        assert request.status_code == 200
        assert response["status"] == 300

        payload = {
            'intent_pk': 1,
            'message_history_ids': [1000, 2000]
        }

        request = client.post('/chat/match-message-with-intent/',
                              json.dumps(payload), content_type="application/json")
        response = request.data
        assert request.status_code == 200
        assert response["status"] == 500

    """
    API Tested: AddMessagewithIntentAPI
    input queries:
        bot_pk: ID of Bot from Intents are to be fetched
    expected output:
        status: 200 // SUCCESS
    checks for:
        This API call is used to record the user feedback for specific intent during chat.
    """

    def test_FetchIntentsOfBotSelectedAPI(self):
        logger.info("Testing FetchIntentsOfBotSelectedAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting FetchIntentsOfBotSelectedAPI is going on...\n")

        User.objects.create(username="temporary", password="temporary")
        user = User.objects.get(username='temporary')
        user.set_password('12345')
        user.save()

        c = Client()
        c.login(username='temporary', password='12345')

        c = APIClient()
        c.login(username='temporary', password='12345')

        payload = {
            'bot_pk': 1,
        }

        request = c.post('/chat/fetch-intents-of-bot-selected/',
                         json.dumps(payload), content_type="application/json")
        response = request.data
        assert request.status_code == 200
        assert response["status"] == 200

        payload = {
            'intent_pk': 300,
        }

        request = c.post('/chat/fetch-intents-of-bot-selected/', json.dumps(payload),
                         content_type="application/json", auth=HTTPBasicAuth(username='temporary', password='12345'))
        response = request.data
        assert request.status_code == 200
        assert response["status"] == 500

    def test_CropAndSaveImageAPI(self):
        logger.info("Testing CropAndSaveImageAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting CropAndSaveImageAPI is going on...\n")

        User.objects.create(username="temporaryIU", password="temporaryIU")
        client = APIClient()
        client.login(username='temporaryIU', password='temporaryIU')

        json_string = json.dumps({
            "x": 0,
            "y": 0,
            "width": 10,
            "height": 10,
            "image_path": "files/test/spotted-dear-chital-knha-national-260nw-1024196245.jpg",
            "target_path": "files/test/spotted-dear-chital-knha-national-260nw-1024196245.jpg",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/image-crop/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 200

        json_string = json.dumps({
            "x": 0,
            "y": 0,
            "width": 10,
            "height": 10,
            "image_path": ""
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/image-crop/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 500

    """
    API Tested: CropAndSaveImageAPI
    input queries:
        x  : upper x coordinate
        y  : upper y coordinate
        width
        height
        image_path : where file is stored
    expected output :
        status: 200 // SUCCESS
    Return:
        success message 
        or
        failure message 
    """

    # def test_FlowAnalyticsStatsAPI(self):
    #     logger.info("Testing FlowAnalytics is going on...", extra={
    #                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    #     print("\nTesting test_FlowAnalyticsStatsAPI is going on...\n")
    #     client = APIClient()
    #     bot_obj = Bot.objects.create()
    #     bot_id = bot_obj.pk
    #     page = 0
    #     custom_encrypt_obj = CustomEncrypt()
    #     User.objects.create(username="test_user", password="test_password")
    #     client.login(username="test_user", password="test_password")
    #     request = client.get(
    #         '/chat/get-flow-analytics-intent/?bot_pk=' + str(bot_id) + "&page=" + str(page))
    #     response = json.loads(custom_encrypt_obj.decrypt(request.data))
    #     assert request.status_code == 200
    #     assert response["status"] == 200

    """
    function tested: SaveStopwordsAPI
    input queries:
       bot_id,
       bot_stop_keywords : stop words modified by user
    expected output:
        return status code 200 if Success
    Return:
        success message 
        or
        failure message
    """

    def test_SaveStopWordsAPI(self):
        logger.info("Testing test_SaveStopWordsAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting SaveStopWordsAPI is going on...\n")
        client = APIClient()
        user_obj = User.objects.create(username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")
        bot_obj = Bot.objects.all()[0]
        bot_obj.users.add(user_obj)
        bot_obj.save()
        json_string = json.dumps({
            "bot_id": 11,
            "bot_stop_keywords": ['an']
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/save-stop-words/', json.dumps({'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 500)

        json_string = json.dumps({
            "bot_id": bot_obj.pk,
            "bot_stop_keywords": ["an", "the"]
        })
        request = client.post(
            '/chat/save-stop-words/', json.dumps({'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)

        bot_obj = Bot.objects.all()[0]
        stop_keywords = json.loads(bot_obj.stop_keywords)

        self.assertEqual(stop_keywords, ['an', 'the'])

    """
    function tested: test_SaveFormDataAPI
    input queries:
       user_id,
       form_name: name of the form to be saved,
       form_values: form fields values
    expected output:
        return status code 200 if Success
    """

    def test_SaveFormDataAPI(self):
        logger.info("Testing test_SaveFormDataAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting SaveFormDataAPI is going on...\n")
        bot_obj = Bot.objects.create(
            name="testbot123", slug="testbot", bot_display_name="testbot", bot_type="2")
        
        profile_obj = Profile.objects.get(user_id='tests1')
        profile_obj.bot = bot_obj
        profile_obj.save()

        bot_id = bot_obj.pk
        client = APIClient()
        json_string = json.dumps({
            "user_id": "tests1",
            "form_name": "Sample Form",
            "form_data": {'name': 'shubham', 'gender': 'male'},
            "bot_id": bot_id
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/save-form-data/', json.dumps({'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)

    def test_GetTrainingDataSuggestionsAPI(self):
        logger.info("Testing test_GetTrainingDataSuggestionsAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting GetTrainingDataSuggestionsAPI is going on...\n")
        bot_obj = Bot.objects.create(
            name="testbot123", slug="testbot", bot_display_name="testbot", bot_type="2")
        bot_id = bot_obj.pk
        bot_obj.word_mapper_list = json.dumps(
            [{"keyword": "laugh out loud", "similar_words": ["lol"]}])
        bot_obj.save()
        chunk_of_suggestion = ChunksOfSuggestions.objects.create(bot=bot_obj)
        chunk_of_suggestion.suggestion_list = json.dumps([{"key": "Contact Customer Care", "value": "Contact Customer Care", "count": 0}, {"key": "please help me connect to your customer service", "value": "Contact Customer Care", "count": 0}, {"key": " i want to talk to customer care", "value": "Contact Customer Care", "count": 0}, {"key": " help me get in touch with customer service team", "value": "Contact Customer Care", "count": 0}, {"key": " i want my issues to be resolved by customer care", "value": "Contact Customer Care", "count": 0}, {
                                                         "key": " contact customer care", "value": "Contact Customer Care", "count": 0}, {"key": "Are you serious?", "value": "Are you serious?", "count": 0}, {"key": "seriously", "value": "Are you serious?", "count": 0}, {"key": "kidding or what", "value": "Are you serious?", "count": 0}, {"key": "are you kidding me", "value": "Are you serious?", "count": 0}, {"key": "are you serious", "value": "Are you serious?", "count": 0}, {"key": "are you serious?", "value": "Are you serious?", "count": 0}])
        chunk_of_suggestion.save()
        json_string = json.dumps({
            "bot_id": bot_id,
            "count_of_chunk": 0
        })

        client = APIClient()
        User.objects.create(username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/get-data-suggestions/', json.dumps({'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)

        client = APIClient()

    def test_ExtendSandboxUser(self):

        logger.info("Testing test_ExtendSandboxUser...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting ExtendSandboxUser is going on...\n")
        c = Client()
        User.objects.create(username="testeasychat",
                            password="testeasychat",
                            is_staff=True,
                            is_bot_invocation_enabled=True,
                            status="1", is_chatbot_creation_allowed="1")

        sandbox_user_obj = SandboxUser.objects.create(
            username="testuser", password="Test@1234")
        user_id = sandbox_user_obj.pk
        c.login(username="testeasychat", password="testeasychat")

        json_string = json.dumps({
            "user_pk": user_id,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = c.post(
            '/supervisor/extend-sandbox-user/', {'data': json_string}, format='json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.json()["response"]))

        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)

        json_string = json.dumps({
            "user_pk": "-1",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = c.post(
            '/supervisor/extend-sandbox-user/', {'data': json_string}, format='json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.json()["response"]))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 500)

    def test_GetLanguageTemplateAPI(self):
        logger.info("Testing GetLanguageTemplateAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting GetLanguageTemplateAPI is going on...\n")
        bot_obj = Bot.objects.create(
            name="testbot123", slug="testbot", bot_display_name="testbot", bot_type="2")
        bot_id = bot_obj.pk
        client = APIClient()
        json_string = json.dumps({
            "bot_id": bot_id,
            "selected_language": "en"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/get-language-template/', json.dumps({'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 500)

        client = APIClient()
        json_string = json.dumps({
            "bot_id": "-1",
            "selected_language": "en"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/get-language-template/', json.dumps({'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 500)

        bot_obj = Bot.objects.create(
            name="testbot123", slug="testbot", bot_display_name="testbot", bot_type="2")
        lang = Language.objects.create(lang="en")
        bot_obj.languages_supported.add(lang)
        bot_obj.save()

        # create_language_en_template(bot_obj, lang, RequiredBotTemplate)
        # RequiredBotTemplate.objects.create(bot=bot_obj, Language=lang)
        check_and_create_default_language_object(bot_obj, Language, RequiredBotTemplate)
        bot_id = bot_obj.pk
        BotChannel.objects.create(
            bot=bot_obj, channel=Channel.objects.filter(name="Web")[0])
        client = APIClient()
        json_string = json.dumps({
            "bot_id": bot_id,
            "selected_language": "en"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/get-language-template/', json.dumps({'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["close_button_tooltip"], "Close")

    def test_IgnoreBotConfigurationChangesInNonPrimaryLanguageAPI(self):
        logger.info("Testing IgnoreBotConfigurationChangesInNonPrimaryLanguageAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting IgnoreBotConfigurationChangesInNonPrimaryLanguageAPI is going on...\n")

        bot_obj = Bot.objects.create(
            name="testbot123", slug="testbot", bot_display_name="testbot", bot_type="2")
        bot_id = bot_obj.pk
        client = APIClient()
        User.objects.create(username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")
        # client.login(username="testeasychat", password="testeasychat")
        json_string = json.dumps({
            "bot_id": bot_id,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/ignore-bot-configuration-changes-in-non-primary-languages/', json.dumps({'json_string': json_string}), content_type='application/json')
        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)

        client = APIClient()
        client.login(username="testeasychat", password="testeasychat")
        json_string = json.dumps({
            "bot_id": "-1",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/ignore-bot-configuration-changes-in-non-primary-languages/', json.dumps({'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 500)

    def test_AutoFixBotConfigurationChangesInNonPrimaryLanguageAPI(self):
        logger.info("Testing AutoFixBotConfigurationChangesInNonPrimaryLanguageAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting AutoFixBotConfigurationChangesInNonPrimaryLanguageAPI is going on...\n")

        bot_obj = Bot.objects.create(
            name="testbot123", slug="testbot", bot_display_name="testbot", bot_type="2")
        bot_id = bot_obj.pk
        client = APIClient()
        User.objects.create(username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")
        # client.login(username="testeasychat", password="testeasychat")
        json_string = json.dumps({
            "bot_id": bot_id,
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/auto-fix-bot-configuration-changes-in-non-primary-languages/', json.dumps({'json_string': json_string}), content_type='application/json')
        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)

        client = APIClient()
        client.login(username="testeasychat", password="testeasychat")
        json_string = json.dumps({
            "bot_id": "-1",
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/auto-fix-bot-configuration-changes-in-non-primary-languages/', json.dumps({'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 500)

    def test_DecryptDataModelValues(self):
        logger.info("Testing DecryptDataModelValuesAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting DecryptDataModelValuesAPI is going on...\n")

        client = APIClient()
        User.objects.create(username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")

        json_string = json.dumps({
            "data_model_values": ["0IUpF52A4lL5PBOg.GXvmUCmDQnTLZ7lZC/x9KoeZUWuBiyYKa/Mt6i/KWUo=.BM8Ls0ZKCPb3cS7o8iKjNw==", "bDkNxzKwBWawtHX9.u/Wg/TEkW1Mqd8OQGcfhjuaCBlK4FtAPE/ESAh+6584=.XFnshuCJa38T/jMDsdItpg=="],
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/decrypt-data-model-values/', json.dumps({'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["decrypted_values"][0], '"direct/(Google)"')
        self.assertEqual(response["decrypted_values"]
                         [1], '"chat with an expert"')

    def test_TrackEventProgressAPI(self):
        logger.info("Testing TrackEventProgressAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting TrackEventProgressAPI is going on...\n")

        client = APIClient()
        user_obj = User.objects.create(
            username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")

        bot_obj = Bot.objects.get(name='testbot')

        json_string = json.dumps({
            'bot_id': bot_obj.pk,
            'event_type': 'import_bot'
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/bot/track-event-progress/', json.dumps({'data': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 300)

        event_obj = EventProgress.objects.create(
            bot=bot_obj,
            user=user_obj,
            event_type='import_bot',
            event_info=json.dumps({'file_uploaded': 'sample.json'})
        )

        request = client.post(
            '/chat/bot/track-event-progress/', json.dumps({'data': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["event_progress"], 0)
        self.assertEqual(response["is_completed"], False)
        self.assertEqual(response["is_failed"], False)

        event_obj.event_progress = 25
        event_obj.save()

        request = client.post(
            '/chat/bot/track-event-progress/', json.dumps({'data': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["event_progress"], 25)
        self.assertEqual(response["is_completed"], False)
        self.assertEqual(response["is_failed"], False)

        client.logout()

    def test_CreateBotWithNameImageAPI(self):
        logger.info("Testing CreateBotWithNameImageAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting CreateBotWithNameImageAPI is going on...\n")

        EasyChatTheme.objects.create(
            name="theme_2", main_page="EasyChatApp/theme2_bot.html", chat_page="EasyChatApp/theme2.html", theme_image_paths=json.dumps(DEFAULT_THEME_IMAGE_DICT["theme_2"]))
        client = APIClient()
        AccessType.objects.create(name="Full Access", value="full_access")
        Language.objects.create(lang="en")
        config_obj = Config.objects.filter().first()
        config_obj.no_of_bots_allowed = 2
        config_obj.save()
        User.objects.create(
            username="twominutebotuser", password="twominutebotuser")
        client.login(username="twominutebotuser", password="twominutebotuser")

        json_string = json.dumps({
            'bot_id': '',
            'bot_name': 'Test Bot',
            'bot_image': '/static/EasyChatApp/images/bot_image_default_2.svg'
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/two-minute-bot/create/', json.dumps({'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))

        self.assertEqual(response["status"], 200)

        client.logout()

    def test_TwoMinuteBotConfigAPI(self):
        logger.info("Testing TwoMinuteBotConfigAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        
        print("\nTesting TwoMinuteBotConfigAPI...\n")

        client = APIClient()
        user_obj = User.objects.create(
            username="twominutebotuser", password="twominutebotuser")
        client.login(username="twominutebotuser", password="twominutebotuser")

        bot_obj = Bot.objects.filter(pk=1).first()
        bot_obj.users.add(user_obj)
        channels = Channel.objects.all()

        for channel in channels:
            BotChannel.objects.create(
                bot=bot_obj, channel=channel)

        json_string = json.dumps({
            "bot_id": bot_obj.pk,
            "welcome_message": "This is welcome message.",
            "selected_languages": [],
            "is_nps_required": False,
            "is_enable_live_chat": False,
            "is_enable_co_browse": False,
            "is_enable_ticket_management": False,
            "is_enable_pdf_searcher": False,
            "is_enable_easy_search": False,
            "is_enable_lead_generation": False
        })

        custom_encrypt_object = CustomEncrypt()
        json_string = custom_encrypt_object.encrypt(json_string)

        request = client.post(
            "/chat/two-minute-bot/update-config/", json.dumps({"data": json_string}), content_type="application/json")

        response = json.loads(custom_encrypt_object.decrypt(request.data))

        self.assertEqual(response["status"], 200)

    def test_BotsListsAPI(self):
        logger.info("Testing BotsListsAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting BotsListsAPI is going on...\n")

        client = APIClient()
        user_obj = User.objects.create(
            username="testeasychat", password="testeasychat")
        custom_encrypt_obj = CustomEncrypt()
        
        request = client.post('/chat/bots-details/')
        
        assert request.status_code == 403

        client.login(username="testeasychat", password="testeasychat")

        request = client.post('/chat/bots-details/')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        user_obj.role = "bot_builder"
        user_obj.save()

        request = client.post('/chat/bots-details/')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["data"]["no_of_bots"], 0)
        self.assertEqual(response["data"]["bot_obj_list"], [])

        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        bot_obj.users.add(user_obj)

        request = client.post('/chat/bots-details/')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["data"]["no_of_bots"], 1)
