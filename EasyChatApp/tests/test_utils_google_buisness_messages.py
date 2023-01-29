# -*- coding: utf-8 -*-

from django.test import TestCase
from EasyChatApp.models import GMBDetails, Profile, Bot, Channel, User
from LiveChatApp.models import LiveChatConfig, LiveChatCustomer, LiveChatUser, LiveChatCategory, LiveChatCalender
from EasyChatApp.utils_google_buisness_messages import is_image, save_and_get_gmb_image_src, send_gbm_livechat_agent_response
import json
import sys
import xlrd
from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)


"""
Test of all functions which are in utils_googlebuisnessmessages.py 
"""


class EasyChatAppUtilsGoogleBusinessMessages(TestCase):

    def setUp(self):
        logger.info(
            "Setting up the test environment for EasyChatApp: GoogleMyBuisness..", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        LiveChatConfig.objects.create(max_customer_count=110)

        Channel.objects.create(name='Web')
        Channel.objects.create(name='GoogleHome')
        Channel.objects.create(name='Alexa')
        Channel.objects.create(name='WhatsApp')
        Channel.objects.create(name='Android')
        Channel.objects.create(name='Facebook')
        Channel.objects.create(name='Microsoft')
        Channel.objects.create(name='Telegram')
        Channel.objects.create(name='GoogleBusinessMessages')
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        category_obj = LiveChatCategory.objects.create(
            title="others", bot=bot_obj)

        easychat_user = User.objects.create(
            role="1", status="1", username="test", password="test")
        livechat_admin = LiveChatUser.objects.create(
            status="1", user=User.objects.create(role="1", status="1", username="testadmin", password="test1234"), last_updated_time=datetime.now().replace(hour=1))
        livechat_agent = LiveChatUser.objects.create(
            status="3", user=easychat_user, last_updated_time=datetime.now().replace(hour=1))
        livechat_agent.category.add(category_obj)
        livechat_agent.bots.add(bot_obj)
        livechat_admin.agents.add(livechat_agent)
        livechat_admin.bots.add(bot_obj)
        livechat_admin.save()
        livechat_agent = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="test1234", password="test1234"))
        livechat_agent.bots.add(bot_obj)
        livechat_agent.save()
        livechat_customer = LiveChatCustomer.objects.create(username="9087654321", agent_id=livechat_agent, is_session_exp=True, joined_date=datetime.now(
        ), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj)
        Profile.objects.create(
            user_id="9087654321", livechat_session_id=livechat_customer.session_id)

        livechat_customer = LiveChatCustomer.objects.create(username="9729631330", is_session_exp=True, joined_date=datetime.now(
        ), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj)

    """
    function save_and_get_gmb_image_src
    input params:
    img_url : image url 

    this function is used to save the image sent by gbm customer in our filesystem and return the path of the image
    Note: currently in the image url their is no way to know the Image format so we are saving the images in jpeg format

    """

    # def test_save_and_get_gmb_image_src(self):

    #     img_url = "https://storage.googleapis.com/sample-avatars-for-bm/bot-avatar.jpg"

    #     file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

    #     expected_file_path = "/files/GoogleBusinessMessages-attachment/"

    #     self.assertEqual(save_and_get_gmb_image_src(img_url),expected_file_path)
    #     # self.assertEqual(
    #     #     (response["response"]["outputSpeech"]["text"]), item)
    #     # self.assertEqual(
    #     #     response["response"]["shouldEndSession"], is_session_end[count])

    """
    function is_image
    input params:
    file_name

    this function is used to check wheter the given file is a image or not
    """

    def test_is_image(self):

        # logger.info("Testingis_image...", extra={'AppName': 'LiveChat'})
        # print("\nTesting is_image...\n")

        file_name = "document.png"

        self.assertEqual(is_image(file_name), True)

        file_name = "document.pdf"

        self.assertEqual(is_image(file_name), False)

        file_name = "document.jpeg"

        self.assertEqual(is_image(file_name), True)

        file_name = "document.txt"

        self.assertEqual(is_image(file_name), False)

    """
    function send_gbm_livechat_agent_response
    input params:
    customer_obj: LiveChatCustomer object

    this function is used to send Agent respone to to GBM customer

    """

    def test_send_gbm_livechat_agent_response(self):
        # logger.info("Testing send_livechat_agent_response...",
        #             extra={'AppName': 'LiveChat'})
        
        print("\nTesting send_gbm_livechat_agent_response...\n")

        livechat_customer = LiveChatCustomer.objects.get(username="9729631330")
        session_id = livechat_customer.session_id
        attached_file_src = ""

        data = {
            "channel_file_url": ""
        }

        sender_name = "Agent test"
        recevied_resp = send_gbm_livechat_agent_response(
            livechat_customer, session_id, "hi", attached_file_src, data, sender_name, Profile, Bot, GMBDetails)["status"]

        self.assertEqual(recevied_resp, 500)

        livechat_customer = LiveChatCustomer.objects.get(username="9087654321")
        session_id = livechat_customer.session_id
        attached_file_src = ""

        data = {
            "channel_file_url": ""
        }

        sender_name = "Agent test"
        recevied_resp = send_gbm_livechat_agent_response(
            livechat_customer, session_id, "hello", attached_file_src, data, sender_name, Profile, Bot, GMBDetails)["status"]

        self.assertEqual(recevied_resp, 200)
