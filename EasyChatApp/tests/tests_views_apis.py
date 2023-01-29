# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import email

from django.test import TestCase
from django.test import Client
from rest_framework.test import APIClient
from EasyChatApp.constants import *
from EasyChatApp.constants_catalogue import *
from EasyChatApp.models import Bot, Language, User, MISDashboard, Profile, Feedback, Channel, Tree, Intent, Config, BotResponse, BotChannel, EasyChatQueryToken, ApiTree, Processor, EasyChatPIIDataToggle, EasyChatSessionIDGenerator, TrafficSources, FlowAnalytics, TimeSpentByUser, WelcomeBannerClicks, AccessManagement, AccessType, WelcomeBanner, WhatsAppServiceProvider, EasyChatOTPDetails, WhatsappCatalogueDetails
from LiveChatApp.models import LiveChatUser, LiveChatCustomer, CannedResponse, LiveChatConfig
from LiveChatApp.utils import get_time, is_agent_live
from EasyChatApp.utils_custom_encryption import *
from CampaignApp.models import VoiceBotCallerID

import logging
import json
import random
import execjs
import base64
from datetime import datetime, timedelta
from Crypto import Random
from Crypto.Cipher import AES
from requests.auth import HTTPBasicAuth

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
        Channel.objects.create(name="Whatsapp")
        Channel.objects.create(name="Alexa")
        Channel.objects.create(name="Voice")
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        MISDashboard.objects.create(
            user_id="1", bot=bot_obj, message_received="hi", bot_response="how may I assist you?", session_id="123")
        MISDashboard.objects.create(
            user_id="2", bot=bot_obj, message_received="hi", bot_response="how may I assist you?", session_id="123")
        MISDashboard.objects.create(
            user_id="4", bot=bot_obj, message_received="hi", bot_response="how may I assist you?", session_id="123")
        MISDashboard.objects.create(
            user_id="4", bot=bot_obj, message_received="Hi", bot_response="hello", session_id="123")
        easychat_user = User.objects.create(
            role="bot_builder", status="1", username="test", password="test")
        User.objects.create(
            role="customer_care_agent", status="1", username="test1", password="test1")

        Profile.objects.create(user_id="tests1")
        Profile.objects.create(user_id="tests11")
        Profile.objects.create(user_id="tests111")
        web_channel = Channel.objects.create(name="Web")
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}')
        tree_obj = Tree.objects.create(name="Hi", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Hi", tree=tree_obj, keywords='{"0": "hey", "1": "hello", "2": "hi", "3": "whats"}', training_data='{"0": "Hey", "1": " hello", "2": " hi", "3": " whats up"}')
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()
        test_bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hello! How may I assist you?", "speech_response": "Hello! How may I assist you?", "text_reprompt_response": "Hello! How may I assist you?", "speech_reprompt_response": "Hello! How may I assist you?"}]}')
        test_tree_obj = Tree.objects.create(
            name="Hello", response=test_bot_response_obj)
        # test_tree_pk = test_tree_obj.pk
        api_tree_obj = ApiTree.objects.create(name="test_api_tree")
        post_processor_obj = Processor.objects.create(
            name="test_post_processor")
        pipe_processor_obj = Processor.objects.create(
            name="test_pipe_processor")
        test_tree_obj.api_tree = api_tree_obj
        test_tree_obj.post_processor = post_processor_obj
        test_tree_obj.pipe_processor = pipe_processor_obj
        test_tree_obj.save()
        EasyChatPIIDataToggle.objects.create(
            user=easychat_user, bot=bot_obj)
        TrafficSources.objects.create(
            web_page="https://www.bewakoof.com/", web_page_visited=1, bot=bot_obj)
        FlowAnalytics.objects.create(
            user=Profile.objects.all()[0], previous_tree=tree_obj, current_tree=tree_obj, intent_indentifed=intent_obj, user_message="conversion_analytics")
        FlowAnalytics.objects.create(
            user=Profile.objects.all()[0], previous_tree=tree_obj, current_tree=tree_obj, intent_indentifed=intent_obj, user_message="conversion_analytics_child", is_last_tree_child=True)

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
        User.objects.get(username="temporary")
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
            "selected_language": "en",
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

        json_string = json.dumps({
            "selected_bot_pk": "-1",
            "selected_language": "en",
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
            "selected_language": "en",
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post(
            '/chat/bot/get-general-details/', json.dumps({'data': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 500

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
        Profile.objects.create(user_id="123")
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
    #     token_id = EasyChatQueryToken.objects.create().token

    #     mis_objs = MISDashboard.objects.all()

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

    def test_SsoMetaData(self):
        logger.info("Testing SsoMetaData is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting SsoMetaData is going on...\n")

        client = Client()

        json_string = json.dumps({
            "sso_metadata": '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" entityID="https://accounts.google.com/o/saml2?idpid=C01xrn70h" validUntil="2025-02-25T08:29:22.000Z">
  <md:IDPSSODescriptor WantAuthnRequestsSigned="false" protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <md:KeyDescriptor use="signing">
      <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
        <ds:X509Data>
          <ds:X509Certificate>MIIDdDCCAlygAwIBAgIGAXCFw9R4MA0GCSqGSIb3DQEBCwUAMHsxFDASBgNVBAoTC0dvb2dsZSBJ
bmMuMRYwFAYDVQQHEw1Nb3VudGFpbiBWaWV3MQ8wDQYDVQQDEwZHb29nbGUxGDAWBgNVBAsTD0dv
b2dsZSBGb3IgV29yazELMAkGA1UEBhMCVVMxEzARBgNVBAgTCkNhbGlmb3JuaWEwHhcNMjAwMjI3
MDgyOTIyWhcNMjUwMjI1MDgyOTIyWjB7MRQwEgYDVQQKEwtHb29nbGUgSW5jLjEWMBQGA1UEBxMN
TW91bnRhaW4gVmlldzEPMA0GA1UEAxMGR29vZ2xlMRgwFgYDVQQLEw9Hb29nbGUgRm9yIFdvcmsx
CzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpDYWxpZm9ybmlhMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A
MIIBCgKCAQEAoJp/N8CcPqBfCBndC9XWrehyXEGa35RmtEoHNHgZXLJ1Aeq/N+5YNi+fRn172bjg
9GLfqHl7IX94D/kf9KKeIjf/xmGlWvQM59M4hHzf3bDfBPB1LCHbgto+rP3kZJERmH3pKmtJW9E6
e/AqJ6RVsWQAZqV3NXAJL+dtIlVFt68bFAvOgQi5YUh9mYI5hSJCCF7BmTz56Zq3JfPQzSZynPe5
tGbbAaXNIMRPUzhcGYqjsrYGg2C37874A3B7odbYM3DFGHNMS2nGjQCVkyTNvWpfUykHOWAbvlhm
+tY6gnrvrPGJill6zzmNJkaB39KHXqTWCHzEGv3pqeT4OaLJTQIDAQABMA0GCSqGSIb3DQEBCwUA
A4IBAQBEtmc6TuI23MWgStYPabznK+FAeK95h9BKVny3t7xkqoiDyP5flCr5Gly0AogKjsmfp+4N
+Su8w8cMK3LGVeaOkU+tO6K2Mv8TNVwGdLbtSaA4fPXW3CKW6NJ1KglHk9xW0ySO+PF2eY3ghBL1
vxoFNCRmstWEVi2xb7Sb9M5fc6qMIGzmkGQLbv62H+fyM+i1Bb6rVSXQbcxk0rIkkDkOpZhvrkhm
mHhadR1CQ7BKYrd2tkn0XAFSxtOF6PD+uWqSmE9gfGKvU+okzuUdxDbrE6a6t9F7XjMUj9lWZfxu
lDHVhcdIDux5JHXAMi2jJowkdpxFs6xoi7UdSqynO+h2</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </md:KeyDescriptor>
    <md:NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</md:NameIDFormat>
    <md:SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://accounts.google.com/o/saml2/idp?idpid=C01xrn70h"/>
    <md:SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://accounts.google.com/o/saml2/idp?idpid=C01xrn70h"/>
  </md:IDPSSODescriptor>
</md:EntityDescriptor>
'''})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/sso-data-functionality/', json.dumps(
            {'data': json_string}), content_type='application/json')
        response = request.data
        assert "detail" in response

        request = client.post('/chat/sso-data-functionality/',
                              content_type='application/json')
        response = request.data
        assert "detail" in response

        User.objects.create(username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")
        request = client.post('/chat/sso-data-functionality/', json.dumps(
            {'data': json_string}), content_type='application/json')
        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 200
        assert response["status_message"] == "Success"

        request = client.get('/chat/sso-data-functionality/')
        assert request["status"] == "200"

    def test_GetIntentNames(self):
        logger.info("Testing GetIntentNames is going on...", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting GetIntentNames is going on...\n")
        bot_obj = Bot.objects.create(name="test_bot")
        bot_id = bot_obj.pk
        intent_obj = Intent.objects.create(name="test_intent_one",
                                           is_deleted=False, is_form_assist_enabled=False, is_hidden=False)
        intent_obj.bots.add(bot_obj)
        intent_obj.save()
        intent_obj = Intent.objects.create(name="test_intent_two",
                                           is_deleted=False, is_form_assist_enabled=False, is_hidden=False)
        intent_obj.bots.add(bot_obj)
        intent_obj.save()
        client = Client()

        json_string = json.dumps(
            {"bot_id": bot_id, "category_id": "", "intent_type": "", "channel_name": ""})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/chat/get-intents/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 200
        json_string = json.dumps({"bot_id": ""})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/chat/get-intents/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 500

    """
    API Tested: DeleteProcessorContentAPI
    input queries:
        processor: api, post or pipe
        tree_pk: tree primary key
        name: name of processor
    expected output:
        status: 200 // SUCCESS
    checks for:
        This API call is used to delete the processor content in API Tree, Post Processor or Pipe Processor.
    """

    def test_DeleteProcessorContentAPI(self):
        logger.info("Testing DeleteProcessorContentAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting DeleteProcessorContentAPI is going on...\n")
        client = APIClient()

        test_tree = Tree.objects.get(name="Hello")
        test_tree_pk = test_tree.pk
        json_string = json.dumps({
            "processor": "api",
            "tree_pk": test_tree_pk,
            "name": "test_api_tree"
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/delete-processor-content/', json.dumps(
            {'json_string': json_string}), content_type='application/json')
        assert request.status_code == 403

        User.objects.create(username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")
        test_tree = Tree.objects.get(name="Hello")
        test_tree_pk = test_tree.pk
        json_string = json.dumps({
            "processor": "api",
            "tree_pk": test_tree_pk,
            "name": "test_api_tree"
        })
        # username = 'admin'
        # password = 'adminadmin'
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/delete-processor-content/', json.dumps(
            {'json_string': json_string}), content_type='application/json')
        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 200

        json_string = json.dumps({
            "processor": "post",
            "tree_pk": test_tree_pk,
            "name": "test_post_processor"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/delete-processor-content/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 200

        json_string = json.dumps({
            "processor": "pipe",
            "tree_pk": test_tree_pk,
            "name": "test_pipe_processor"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/delete-processor-content/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(custom_encrypt_obj.decrypt(request.data))
        assert request.status_code == 200
        assert response["status"] == 200

    def test_SaveEasyChatAndroidIntentFeedbackAPI(self):

        mis_objs = MISDashboard.objects.all()

        client = APIClient()
        for mis_obj in mis_objs:
            json_string = json.dumps({
                "feedback_id": mis_obj.pk,
                "feedback_type": random.randint(1, 2),
                "feedback_cmt": "It was awesome."
            })

            custom_encrypt_obj = CustomEncrypt()
            json_string = custom_encrypt_obj.encrypt(json_string)

            request = client.post('/chat/save-easychat-android-feedback-msg/', json.dumps(
                {'json_string': json_string}), content_type='application/json')
            response = json.loads(
                custom_encrypt_obj.decrypt(request.data['Response']))
            assert request.status_code == 200
            assert response["status"] == 200

        json_string = ""

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/chat/save-easychat-android-feedback-msg/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        response = json.loads(
            custom_encrypt_obj.decrypt(request.data['Response']))
        assert request.status_code == 200
        assert response["status"] == 500

    def test_CheckDataToggleOtp(self):

        client = APIClient()
        client.login(username="test", password="test")

        data_toggle_obj = EasyChatPIIDataToggle.objects.get(
            user=(User.objects.get(username="test")), bot=(Bot.objects.get(pk=1)))

        otp = '673452'
        data_toggle_obj.otp = otp
        data_toggle_obj.is_expired = False
        data_toggle_obj.save()

        json_string = json.dumps(
            {'bot_id': "1", "entered_otp": otp})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/bot/check-data-toggle-otp/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        assert response["message"] == "Matched"
        assert response["token"] == str(data_toggle_obj.token)

        json_string = json.dumps(
            {'bot_id': "1", "entered_otp": "235436"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/bot/check-data-toggle-otp/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        assert response["message"] == "Not Matched"

        data_toggle_obj.is_expired = True
        data_toggle_obj.save()

        json_string = json.dumps(
            {'bot_id': "1", "entered_otp": otp})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/bot/check-data-toggle-otp/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status_code"] == "200"
        assert response["message"] == "Not Matched"
        client.logout()

        """
        function tested: test DownloadAgentExcelTemplateAPI
        input queries:
        
        expected output:
            status: 200 // SUCCESS
        checks for:
        downloads the create agent via excel template sheet  .
        """

    def test_DownloadWordMapperExcelTemplateAPI(self):

        client = APIClient()
        client.login(username="test", password="test")

        request = client.post('/chat/download-word-mapper-template/', json.dumps(
            {'json_string': ""}), content_type='application/json')

        assert request.status_code == 200

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        assert response["status"] == 200
        assert str(response["export_path"]) == ("/files/templates/easychat-word-mapper" +
                                                "/create_word_mapper_excel_template.xlsx")
        assert str(response["export_path_exist"]) == "True"

        client.logout()

        client.login(username="test1", password="test1")

        request = client.post('/chat/download-word-mapper-template/', json.dumps(
            {'json_string': ""}), content_type='application/json')

        assert request.status_code == 200

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        assert response["status"] == 403
        assert str(response["export_path"]) == "None"
        assert str(response["export_path_exist"]) == "None"

        client.logout()

    """
    API tested: SaveBotClickCountAPI
    input queries:
        bot_id: Bot ID on which click count has to be increased
        bot_web_page: traffic source from where request is coming
    
    expected output:
        status: 200 // SUCCESS
    checks for:
        updates the click count for respective Bot on TrafficSource model
    """

    def test_SaveBotClickCountAPI(self):
        logger.info("Testing SaveBotClickCountAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting SaveBotClickCountAPI is going on...\n")
        client = APIClient()

        json_string = json.dumps(
            {"bot_id": "1", "bot_web_page": "https://www.bewakoof.com/", "web_page_source": "https://www.google.com"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/save-bot-click-count/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        json_string = json.dumps(
            {"bot_web_page": "https://www.bewakoof.com/"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/save-bot-click-count/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

    """
    API tested: GetConversionFlowAnalyticsAPI
    input parameters:
        bot_id: Bot ID
        start_date: Filter parameters start date
        end_date: Filter parameters end date
        channel_list: Filter parameters channel list 
    
    expected output:
        status: 200 // SUCCESS
        response: Flow Conversion Analytics Data
    """

    def test_GetConversionFlowAnalyticsAPI(self):
        logger.info("Testing GetConversionFlowAnalyticsAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting GetConversionFlowAnalyticsAPI is going on...\n")
        client = APIClient()
        client.login(username="test", password="test")

        custom_encrypt_obj = CustomEncrypt()
        request = client.get(
            '/chat/get-conversion-flow-analytics/?bot_pk=1&start_date=2021-04-14&end_date=2021-07-13&channel_list=')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200 or response["status"] == 300
        assert response["flow_completion_data"] != None

        request = client.get(
            '/chat/get-conversion-flow-analytics/?&start_date=2021-04-14&end_date=2021-07-13&channel_list=')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        client.logout()

    """
    API tested: GetConversionIntentAnalyticsAPI
    input parameters:
        bot_id: Bot ID
        start_date: Filter parameters start date
        end_date: Filter parameters end date
        channel_list: Filter parameters channel list 
    
    expected output:
        status: 200 // SUCCESS
        response: Intent Conversion Analytics Data
    """

    def test_GetConversionIntentAnalyticsAPI(self):
        logger.info("Testing GetConversionIntentAnalyticsAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting GetConversionIntentAnalyticsAPI is going on...\n")
        client = APIClient()
        client.login(username="test", password="test")

        custom_encrypt_obj = CustomEncrypt()
        request = client.get(
            '/chat/get-conversion-intent-analytics/?bot_pk=1&start_date=2021-04-14&end_date=2021-07-13&channel_list=&page=1')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200 or response["status"] == 300
        assert response["intent_completion_data"] != None
        assert response["total_intent_count"] == 0

        request = client.get(
            '/chat/get-conversion-intent-analytics/?bot_pk=1&start_date=2021-04-14&end_date=2021-07-13&channel_list=')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        client.logout()

    def test_UpdateNeedToBuildBotAPI(self):
        logger.info("Testing UpdateNeedToBuildBotAPI is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting UpdateNeedToBuildBotAPI is going on...\n")
        client = APIClient()
        client.login(username="test", password="test")

        json_string = json.dumps(
            {"bot_id": "1", })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/update-need-to-build-bot/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        json_string = json.dumps(
            {"bot_id": "500", })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/update-need-to-build-bot/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        client.logout()

    def test_GetConversionBotHitsAnalyticsAPI(self):
        logger.info("Testing GetConversionBotHitsAnalyticsAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting GetConversionBotHitsAnalyticsAPI is going on...\n")

        bot_obj = Bot.objects.all()[0]
        TrafficSources.objects.create(web_page="www.geeks.com", bot_clicked_count=1,
                                      web_page_visited=1, bot=bot_obj, web_page_source="www.google.com")
        TimeSpentByUser.objects.create(user_id="4321", bot=bot_obj, total_time_spent=20,
                                       web_page="www.geeks.com", web_page_source="www.google.com")

        client = APIClient()
        client.login(username="test", password="test")

        custom_encrypt_obj = CustomEncrypt()
        request = client.get(
            '/chat/get-conversion-bot-hits-analytics/?bot_pk=1&start_date=2021-04-14&end_date=2022-07-32&source_list=&page=1')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert response["bot_hit_data_count"][0]['web_page'] == "www.geeks.com"
        assert response["bot_hit_data_count"][0]['average_time_spent'] == 20

        custom_encrypt_obj = CustomEncrypt()
        request = client.get(
            '/chat/get-conversion-bot-hits-analytics/?start_date=2021-04-14&end_date=2022-07-32&source_list=&page=1')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        client.logout()

    def test_GetConversionWelcomeAnalyticsAPI(self):
        logger.info("Testing GetConversionWelcomeAnalyticsAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting GetConversionWelcomeAnalyticsAPI is going on...\n")

        bot_obj = Bot.objects.all()[0]
        user = Profile.objects.all()[0]
        welcomeBannerObj = WelcomeBannerClicks.objects.create(
            web_page_visited="www.geeks.com", bot=bot_obj, preview_source="https://support.content.office.net/en-us/media/91c15bf0-d2be-49b5-afd8-78c7a4ae40e0.png")
        welcomeBannerObj.user_id.add(user)
        client = APIClient()
        client.login(username="test", password="test")

        custom_encrypt_obj = CustomEncrypt()
        request = client.get(
            '/chat/get-conversion-welcome-analytics/?bot_pk=1&start_date=2021-04-14&end_date=2022-07-32&page=1')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200 or response["status"] == 300
        assert response["welcome_banner_clicked_data_count"][0]['web_page_visited'] == "www.geeks.com"
        assert response["welcome_banner_clicked_data_count"][0]['preview_source'] == "https://support.content.office.net/en-us/media/91c15bf0-d2be-49b5-afd8-78c7a4ae40e0.png"

        custom_encrypt_obj = CustomEncrypt()
        request = client.get(
            '/chat/get-conversion-welcome-analytics/?start_date=2021-04-14&end_date=2022-07-32&page=1')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        client.logout()

    """
    API tested: GetConversionNodeAnalyticsAPI
    input parameters:
        bot_id: Bot ID
        intent_pk: Intent PK
        start_date: Filter parameters start date
        end_date: Filter parameters end date
        channel_list: Filter parameters channel list 
    
    expected output:
        status: 200 // SUCCESS
        response: Complete flow data
    """

    def test_GetConversionNodeAnalyticsAPI(self):
        logger.info("Testing GetConversionNodeAnalyticsAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting GetConversionNodeAnalyticsAPI is going on...\n")
        client = APIClient()
        client.login(username="test", password="test")

        intent_obj = Intent.objects.all()[0]
        bot_obj = intent_obj.bots.all()
        start_date = datetime.now() - timedelta(1)
        start_date = datetime.strftime(start_date, '%Y-%m-%d')
        end_date = datetime.now() + timedelta(1)
        end_date = datetime.strftime(end_date, '%Y-%m-%d')
        json_string = json.dumps(
            {"bot_pk": bot_obj[0].pk, "intent_pk": intent_obj.pk, "start_date": start_date, "end_date": end_date, "channel_list": ["Web"]})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-conversion-node-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        flow_data_response = json.loads(response["flow_tree_data"])

        assert response["status"] == 200 or response["status"] == 300
        assert flow_data_response["behavior"] == "Parent Node"
        assert response["max_level"] == 1

        json_string = json.dumps(
            {"bot_pk": bot_obj[0].pk, "intent_pk": intent_obj.pk, "end_date": end_date, "channel_list": ["Web"]})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-conversion-node-analytics/', json.dumps(
            {'json_string': json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)

        assert response["status"] == 500

    def test_SaveBubbleClickInfoAPI(self):

        logger.info("Testing SaveBubbleClickInfoAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting SaveBubbleClickInfoAPI is going on...\n")
        Language.objects.create(lang="en")
        client = APIClient()
        client.login(username="test", password="test")

        intent_obj = Intent.objects.all()[0]
        bot_obj = intent_obj.bots.all()[0]

        json_string = json.dumps(
            {"bot_id": bot_obj.pk, "bubble_name": intent_obj.name, "selected_language": "en"})

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/save-bubble-click-info/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        assert request.data["status"] == 200

        json_string = json.dumps(
            {"bot_id": 0, "bubble_name": intent_obj.name, "selected_language": "en"})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/save-bubble-click-info/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        assert request.data["status"] == 500

    def test_GetUserNudgeAnalyticsAPI(self):

        logger.info("Testing GetUserNudgeAnalyticsAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting GetUserNudgeAnalyticsAPI is going on...\n")

        client = APIClient()
        client.login(username="test", password="test")

        bot_obj = Bot.objects.all()[0]
        try:
            BotChannel.objects.get(
                bot=bot_obj, channel=Channel.objects.get(name="Web"))
        except:
            BotChannel.objects.create(
                bot=bot_obj, channel=Channel.objects.get(name="Web"))
        start_date = datetime.now() - timedelta(7)
        start_date = datetime.strftime(start_date, '%Y-%m-%d')
        end_date = datetime.now()
        end_date = datetime.strftime(end_date, '%Y-%m-%d')

        json_string = json.dumps({"bot_id": bot_obj.pk, "start_date": start_date, "end_date": end_date,
                                  "page": 1, "category_name": "All", "channel_name": "All", "selected_language": "All"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-user-nudge-analytics/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        json_string = json.dumps({"bot_id": bot_obj.pk, "start_date": start_date, "end_date": end_date,
                                  "page": 1, "category_name": "All", "channel_name": "Android", "selected_language": "All"})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-user-nudge-analytics/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert response["user_nudge_analytics_data"] == []

        json_string = json.dumps({"bot_id": bot_obj.pk, "start_date": "None", "end_date": "None",
                                  "page": 1, "category_name": "All", "channel_name": "All", "selected_language": "All"})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-user-nudge-analytics/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

    def test_GetHourWiseAnalyticsAPI(self):

        logger.info("Testing GetHourWiseAnalyticsAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting GetHourWiseAnalyticsAPI is going on...\n")

        client = APIClient()

        user_obj = User.objects.filter(username="testeasychat").first()
        if not user_obj:
            user_obj = User.objects.create(
                username="testeasychat", password="testeasychat")

        client.login(username="testeasychat", password="testeasychat")

        bot_obj = Bot.objects.all()[0]
        bot_obj.users.add(user_obj)
        try:
            BotChannel.objects.get(
                bot=bot_obj, channel=Channel.objects.get(name="Web"))
        except:
            BotChannel.objects.create(
                bot=bot_obj, channel=Channel.objects.get(name="Web"))
        start_date = datetime.now() - timedelta(7)
        start_date = datetime.strftime(start_date, '%Y-%m-%d')
        end_date = datetime.now()
        end_date = datetime.strftime(end_date, '%Y-%m-%d')
        custom_encrypt_obj = CustomEncrypt()

        json_string = json.dumps({"bot_pk": bot_obj.pk, "start_date": start_date, "end_date": end_date,
                                  "category_name": "All", "channel": "All", "selected_language": "All", "interval_type": "1"})

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-hour-wise-analytics/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        json_string = json.dumps({"bot_pk": bot_obj.pk, "start_date": start_date, "end_date": end_date,
                                  "category_name": "All", "channel": "viber", "selected_language": "All", "interval_type": "3", "time_format": "2"})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-hour-wise-analytics/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        # bot_pk is empty
        json_string = json.dumps({"bot_pk": "", "start_date": end_date, "end_date": start_date,
                                  "category_name": "All", "channel": "All", "selected_language": "All", "interval_type": "2", "time_format": "2"})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-hour-wise-analytics/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        # start_date > end_date
        json_string = json.dumps({"bot_pk": bot_obj.pk, "start_date": end_date, "end_date": start_date,
                                  "category_name": "All", "channel": "All", "selected_language": "All", "interval_type": "2", "time_format": "2"})
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/chat/get-hour-wise-analytics/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 401

    def test_ExportUserNudgeAnalyticsAPI(self):

        logger.info("Testing ExportUserNudgeAnalyticsAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting ExportUserNudgeAnalyticsAPI is going on...\n")

        client = APIClient()
        client.login(username="test", password="test")

        bot_obj = Bot.objects.all()[0]
        try:
            BotChannel.objects.get(
                bot=bot_obj, channel=Channel.objects.get(name="Web"))
        except:
            BotChannel.objects.create(
                bot=bot_obj, channel=Channel.objects.get(name="Web"))
        start_date = datetime.now() - timedelta(7)
        start_date = datetime.strftime(start_date, '%Y-%m-%d')
        end_date = datetime.now()
        end_date = datetime.strftime(end_date, '%Y-%m-%d')
        email_id = ""

        json_string = json.dumps({"bot_id": bot_obj.pk, "start_date": start_date, "email_id": email_id,
                                  "end_date": end_date, "category_name": "All", "channel_name": "All", "selected_language": "All"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/export-user-nudge-analytics/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert response["export_path"] != ""

        json_string = json.dumps({"bot_id": bot_obj.pk, "start_date": "None",
                                  "end_date": "None", "category_name": "All", "channel_name": "Android", "selected_language": "All"})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/export-user-nudge-analytics/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

    def test_GetBotManagerAccessDetailsAPI(self):

        logger.info("Testing GetBotManagerAccessDetailsAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting GetBotManagerAccessDetailsAPI is going on...\n")

        client = APIClient()
        client.login(username="test", password="test")

        bot_obj = Bot.objects.all()[0]
        user_obj = User.objects.get(username="test")
        bot_obj.users.add(user_obj)

        try:
            access_management_obj = AccessManagement.objects.get(
                user=user_obj, bot=bot_obj)
        except:
            access_management_obj = AccessManagement.objects.create(
                user=user_obj, bot=bot_obj)

        access_management_obj.access_type.clear()
        try:
            access_type_obj = AccessType.objects.get(name="Full Access")
        except:
            access_type_obj = AccessType.objects.create(
                name="Full Access", value="full_access")
        access_management_obj.access_type.add(access_type_obj)
        access_management_obj.save()

        json_string = json.dumps(
            {"bot_id": bot_obj.pk, "manager_id": user_obj.pk})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-manager-access-details/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert int(response["bot_id"]) == bot_obj.pk

        json_string = json.dumps({"bot_id": bot_obj.pk})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-manager-access-details/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

    def test_SaveWelcomeBannerAPI(self):

        logger.info("Testing SaveWelcomeBannerAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting SaveWelcomeBannerAPI is going on...\n")

        client = APIClient()
        client.login(username="test", password="test")

        bot_obj = Bot.objects.all()[0]
        try:
            channel_obj = Channel.objects.get(name="Web")
        except:
            channel_obj = Channel.objects.create(name="Web")
            channel_obj.save()

        try:
            BotChannel.objects.get(bot=bot_obj, channel=channel_obj)
        except:
            BotChannel.objects.create(bot=bot_obj, channel=channel_obj)

        json_string = json.dumps({"bot_id": bot_obj.pk, "channel_name": "Web", "action_type": "1",
                                  "image_url": "http://127.0.0.1:8000/static/files/dummy.png", "redirection_url": "https://google.com", "intent_pk": ""})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/save-welcome-banner/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert response["welcome_banner_pk"] != ""

        json_string = json.dumps({"bot_id": bot_obj.pk, "channel_name": "xyaz", "action_type": "2",
                                  "image_url": "http://127.0.0.1:8000/static/files/dummy.png", "redirection_url": "https://google.com", "intent_pk": ""})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/save-welcome-banner/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

    def test_EditWelcomeBannerAPI(self):

        logger.info("Testing EditWelcomeBannerAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting EditWelcomeBannerAPI is going on...\n")

        client = APIClient()
        client.login(username="test", password="test")

        wb_obj = WelcomeBanner.objects.create(
            action_type="1", image_url="http://127.0.0.1:8000/static/files/dummy.png", redirection_url="https://google.com")
        wb_obj.save()

        json_string = json.dumps(
            {"wb_id": wb_obj.pk, "redirected_url": "https://yahoo.in", "intent_id": ""})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/edit-welcome-banner/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert response["action_type"] == "1"
        assert response["redirection_url"] == "https://yahoo.in"

        json_string = json.dumps(
            {"wb_id": wb_obj.pk, "redirected_url": "https://yahoo.in"})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/edit-welcome-banner/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

    def test_DeleteWelcomeBannerAPI(self):

        logger.info("Testing DeleteWelcomeBannerAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting DeleteWelcomeBannerAPI is going on...\n")

        client = APIClient()
        client.login(username="test", password="test")

        wb_obj = WelcomeBanner.objects.create(
            action_type="1", image_url="http://127.0.0.1:8000/static/files/dummy.png", redirection_url="https://google.com")
        wb_obj.save()

        json_string = json.dumps({"wb_id": wb_obj.pk})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/delete-welcome-banner/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        json_string = json.dumps({"wb_id": ""})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/delete-welcome-banner/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

    def test_GetIntentInformationAPI(self):

        logger.info("Testing GetIntentInformationAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting GetIntentInformationAPI is going on...\n")

        client = APIClient()
        client.login(username="test", password="test")

        bot_obj = Bot.objects.all()[0]
        intent_obj = Intent.objects.filter(
            bots__in=[bot_obj], is_deleted=False, is_hidden=False)[0]

        json_string = json.dumps(
            {"bot_id": bot_obj.pk, "intent_pk": intent_obj.pk})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-intent-information/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert response["intent_name"] != ""

        json_string = json.dumps({"bot_id": bot_obj.pk, "intent_pk": "None"})
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/chat/get-intent-information/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

    def test_GetWhatsAppWebhookDefaultCodeAPI(self):

        logger.info("Testing GetWhatsAppWebhookDefaultCodeAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting GetWhatsAppWebhookDefaultCodeAPI is going on...\n")

        try:
            wsp_obj = WhatsAppServiceProvider.objects.get(name="3")
        except:
            wsp_obj = WhatsAppServiceProvider.objects.create(
                name="3", default_code_file_path="cronjob_scripts/WhatsAppWebhookSampleScripts/EasyChatApp/easychatapp_rml_webhook.py")
            wsp_obj.save()

        client = APIClient()
        client.login(username="test", password="test")

        json_string = json.dumps({"wsp_code": "3"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-wa-webhook-default-code/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200
        assert["default_code"] != ""
        assert["wsp_name"] != ""

        json_string = json.dumps({"wsp_code": ""})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/get-wa-webhook-default-code/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500
        assert response["wsp_name"] == ""

    def test_MarkFlaggedQueriesAPI(self):

        logger.info("Testing MarkFlaggedQueriesAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting MarkFlaggedQueriesAPI is going on...\n")

        client = APIClient()
        client.login(username="test", password="test")

        mis_obj = MISDashboard.objects.all()[0]
        mis_obj.match_percentage = 22
        mis_obj.save()
        bot_obj = mis_obj.bot

        json_string = json.dumps({"bot_id": bot_obj.pk, "message_history_pk_list": [
                                 mis_obj.pk], "flagged_queries_type": "1"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/mark-flagged-queries/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        json_string = json.dumps({"bot_id": "", "message_history_pk_list": [
                                 mis_obj.pk], "flagged_queries_type": "1"})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/mark-flagged-queries/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

    def test_AddIntentIconAPI(self):

        logger.info("Testing AddIntentIconAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting AddIntentIconAPI is going on...\n")

        client = APIClient()
        client.login(username="test", password="test")

        intent_obj = Intent.objects.filter(is_deleted=False).first()

        json_string = json.dumps(
            {"intent_pk": intent_obj.pk, "icon_src": "https://google.com/abc.png"})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/add-intent-icon/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        json_string = json.dumps(
            {"intent_pk": "", "icon_src": "https://google.com/abc.png"})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/add-intent-icon/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

    def test_RemoveIntentIconAPI(self):

        logger.info("Testing RemoveIntentIconAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting RemoveIntentIconAPI is going on...\n")

        client = APIClient()
        client.login(username="test", password="test")

        intent_obj = Intent.objects.filter(is_deleted=False).first()

        json_string = json.dumps({"intent_pk": intent_obj.pk})
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/add-intent-icon/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        json_string = json.dumps({"intent_pk": ""})
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/add-intent-icon/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

    def test_SaveVoiceChannelDetailsAPI(self):

        logger.info("Testing SaveVoiceChannelDetailsAPI...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting of SaveVoiceChannelDetailsAPI is going on...\n")

        client = APIClient()
        user_obj = User.objects.create(
            username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")
        bot_obj = Bot.objects.all()[0]
        voice_modulation_details = DEFAULT_VOICE_MODULATION
        json_string = json.dumps({
            "bot_id": bot_obj.pk,
            "welcome_message": "This is welcome message",
            "failure_message": "This is failure message",
            "authentication_message": "This is authentication message",
            "selected_tts_provider": "Microsoft",
            "api_key": "64d168e44dc4b5d7bbdb475317398a8fa4022d07d01c3aee",
            "api_token": "fff3bfb413deeba7ebb1553b597c9c94881b040731f4b923",
            "api_subdomain": "1",
            "api_sid": "ameyo1m",
            "tts_language": voice_modulation_details["Microsoft"]["tts_language"],
            "tts_speaking_style": voice_modulation_details["Microsoft"]["tts_speaking_style"],
            "tts_voice": voice_modulation_details["Microsoft"]["tts_voice"],
            "tts_speaking_speed": voice_modulation_details["Microsoft"]["tts_speaking_speed"],
            "tts_pitch": voice_modulation_details["Microsoft"]["tts_pitch"],
            "asr_provider": voice_modulation_details["Microsoft"]["asr_provider"],
            "silence_threshold_count": DEFAULT_SILENCE_THRESHOLD,
            "silence_response": DEFAULT_SILENCE_RESPONSE,
            "silence_termination_response": DEFAULT_SILENCE_TERMINATION_RESPOSNE,
            "loop_threshold_count": DEFAULT_LOOP_THRESHOLD,
            "is_agent_handover": DEFAULT_AGENT_HANDOVER,
            "loop_termination_response": DEFAULT_LOOP_TERMINATION_RESPONSE,
            "loop_handover_response": DEFAULT_LOOP_AGENT_HANDOVER_RESPONSE,
            "languages_supported": "en,hi,",
            "fallback_response": DEFAULT_FALLBACK_RESPONSE
        })
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        request = client.post('/chat/channels/voice/save/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 401

        bot_obj.users.add(user_obj)

        BotChannel.objects.filter(bot=bot_obj, channel=Channel.objects.get(name="Voice")).delete()

        request = client.post('/chat/channels/voice/save/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500

        BotChannel.objects.create(
            bot=bot_obj, channel=Channel.objects.get(name="Voice"))

        request = client.post('/chat/channels/voice/save/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

    def test_AddRepeatVariationsAPI(self):

        logger.info("Testing AddRepeatVariationsAPI...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting of AddRepeatVariationsAPI is going on...\n")

        client = APIClient()
        user_obj = User.objects.create(
            username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")

        bot_obj = Bot.objects.all()[0]
        bot_obj.users.remove(user_obj)
        bot_obj.save()

        json_string = json.dumps({
            "bot_id": str(bot_obj.pk),
            "repeat_variation": "hi hello"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/channels/voice/add-repeat-variation/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 401

        bot_obj.users.add(user_obj)
        bot_obj.save()

        request = client.post('/chat/channels/voice/add-repeat-variation/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        request = client.post('/chat/channels/voice/add-repeat-variation/', json.dumps(
            {"json_string": json.dumps({})}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500
        
    def test_DeleteRepeatVariationsAPI(self):

        logger.info("Testing DeleteRepeatVariationsAPI...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting of DeleteRepeatVariationsAPI is going on...\n")

        client = APIClient()
        user_obj = User.objects.create(
            username="testeasychat", password="testeasychat")
        client.login(username="testeasychat", password="testeasychat")

        bot_obj = Bot.objects.all()[0]
        bot_obj.users.remove(user_obj)
        bot_obj.save()

        json_string = json.dumps({
            "bot_id": str(bot_obj.pk),
            "repeat_variation": "hi hello"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/channels/voice/delete-repeat-variation/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 401

        bot_obj.users.add(user_obj)
        bot_obj.save()

        request = client.post('/chat/channels/voice/delete-repeat-variation/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        request = client.post('/chat/channels/voice/delete-repeat-variation/', json.dumps(
            {"json_string": json.dumps({})}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 500
    
    def test_loginOTPAPI(self):
        logger.info("Testing loginOTPAPI...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting of loginOTPAPI is going on...\n")

        client = APIClient()
        User.objects.create(
            username="testeasychat", password="testeasychat")
        json_string = json.dumps({
            "captcha_image": "http://127.0.0.1:8000/static/EasyChatApp/captcha_images/3223BDEE60A94F8F.jpg",
            "captcha": "n25ync",
            "password": "testeasychat",
            "username": "testeasychat",
            "logout_other": "false"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/otp-authentication/', json.dumps(
            {"Request": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        json_string = json.dumps({
            "captcha_image": "http://127.0.0.1:8000/static/EasyChatApp/captcha_images/3223BDEE60A94F8F.jpg",
            "captcha": "n25ync",
            "password": "testeasychat",
            "username": "xyzworking",
            "logout_other": "false"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/otp-authentication/', json.dumps(
            {"Request": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 303

    def test_ResendLoginOTPAPI(self):
        logger.info("Testing ResendLoginOTPAPI...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting of ResendLoginOTPAPI is going on...\n")

        client = APIClient()
        user_obj = User.objects.create(
            username="testeasychat", password="testeasychat")
        json_string = json.dumps({
            "captcha_image": "http://127.0.0.1:8000/static/EasyChatApp/captcha_images/3223BDEE60A94F8F.jpg",
            "captcha": "n25ync",
            "password": "testeasychat",
            "username": "testeasychat",
            "logout_other": "false"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/otp-authentication/', json.dumps(
            {"Request": json_string}), content_type='application/json')
        
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        otp_access_token = response["otp_access_token"]
        
        otp_details_obj = EasyChatOTPDetails.objects.filter(user=user_obj, token=otp_access_token).first()
        otp_details_obj.otp_sent_on = otp_details_obj.otp_sent_on - timedelta(seconds=120)
        otp_details_obj.save()

        json_string = json.dumps({
            "user_name": "testeasychat",
            "otp_access_token": otp_access_token
        })

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/resend-multifactor-login-otp/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 200

        json_string = json.dumps({
            "user_name": "xyzworking",
            "otp_access_token": otp_access_token
        })

        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/resend-multifactor-login-otp/', json.dumps(
            {"json_string": json_string}), content_type='application/json')

        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert response["status"] == 301

    def test_SaveVoiceBotCallerAPI(self):
        logger.info("Testing SaveVoiceBotCallerAPI...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting of SaveVoiceBotCallerAPI is going on...\n")

        client = APIClient()

        user_obj = User.objects.filter(username="testeasychat").first()
        if not user_obj:
            user_obj = User.objects.create(username="testeasychat", password="testeasychat")

        client.login(username="testeasychat", password="testeasychat")

        bot_obj = Bot.objects.all()[0]
        bot_obj.users.remove(user_obj)
        bot_obj.save()

        json_string = json.dumps({
            "bot_id": str(bot_obj.pk),
            "caller_id": "9999999999",
            "app_id": "9999"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/channels/voice/add-caller/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert str(response["status"]) == "500"

        bot_obj.users.add(user_obj)
        bot_obj.save()

        request = client.post('/chat/channels/voice/add-caller/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert str(response["status"]) == "200"

        request = client.post('/chat/channels/voice/add-caller/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert str(response["status"]) == "501"

    def test_DeleteVoiceBotCallerAPI(self):
        logger.info("Testing DeleteVoiceBotCallerAPI...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting of DeleteVoiceBotCallerAPI is going on...\n")

        client = APIClient()

        user_obj = User.objects.filter(username="testeasychat").first()
        if not user_obj:
            user_obj = User.objects.create(username="testeasychat", password="testeasychat")

        client.login(username="testeasychat", password="testeasychat")

        bot_obj = Bot.objects.all()[0]
        bot_obj.users.remove(user_obj)
        bot_obj.save()

        voice_bot_caller_obj = VoiceBotCallerID.objects.create(bot=bot_obj, caller_id="9898989898", app_id="9898")
        voice_bot_caller_obj.save()

        json_string = json.dumps({
            "bot_id": str(bot_obj.pk),
            "voice_bot_caller_id": str(voice_bot_caller_obj.pk)
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/channels/voice/delete-caller/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert str(response["status"]) == "500"

        bot_obj.users.add(user_obj)
        bot_obj.save()

        request = client.post('/chat/channels/voice/delete-caller/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert str(response["status"]) == "200"

        request = client.post('/chat/channels/voice/delete-caller/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert str(response["status"]) == "500"

    def test_GetCatalogueDetailsAPI(self):
        logger.info("Testing test_GetCatalogueDetailsAPI...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        print("\nTesting of test_GetCatalogueDetailsAPI is going on...\n")

        client = APIClient()

        user_obj = User.objects.filter(username="testeasychat").first()
        if not user_obj:
            user_obj = User.objects.create(username="testeasychat", password="testeasychat")

        client.login(username="testeasychat", password="testeasychat")

        bot_obj = Bot.objects.all()[0]
        bot_obj.users.add(user_obj)

        json_string = json.dumps({
            "bot_id": str(bot_obj.pk),
            "selected_language": "en"
        })

        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)

        request = client.post('/chat/channels/whatsapp/get-catalogue-details/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert str(response["status"]) == "404"

        catalogue_metadata = {"catalogue_type": "multiple_product", "body_text": "Hi! How may i assist you", "footer_text": "asd", "catalogue_id": "asd", "header_text": "asd", "sections": {"x0Zi": {"product_ids": ["akljdn", "sdal/kn", "onemore"], "section_title": "sce1"}}}
        catalogue_object = WhatsappCatalogueDetails.objects.create(
            bot=bot_obj, catalogue_type=MULTIPLE_PRODUCT_CHOICE, catalogue_metadata=json.dumps(catalogue_metadata), is_catalogue_enabled=True)

        request = client.post('/chat/channels/whatsapp/get-catalogue-details/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert str(response["status"]) == "200"
        assert response["catalogue_metadata"] == catalogue_object.catalogue_metadata
        assert response["is_catalogue_enabled"] == catalogue_object.is_catalogue_enabled

        bot_obj.users.remove(user_obj)
        request = client.post('/chat/channels/whatsapp/get-catalogue-details/', json.dumps(
            {"json_string": json_string}), content_type='application/json')
        
        assert request.status_code == 200
        response = custom_encrypt_obj.decrypt(request.data)
        response = json.loads(response)
        assert str(response["status"]) == '401'
