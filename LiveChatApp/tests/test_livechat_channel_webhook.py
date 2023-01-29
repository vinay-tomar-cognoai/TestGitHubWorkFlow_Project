# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from EasyChatApp.models import Profile, Bot, Channel, User
from LiveChatApp.models import LiveChatConfig, LiveChatCustomer, LiveChatUser, LiveChatCategory, LiveChatCalender
from LiveChatApp.livechat_channels_webhook import check_for_livechat, get_livechat_userid, get_livechat_response, create_and_enable_livechat, check_agent_assigned, create_image_thumbnail
import logging
import json
import sys
import xlrd
import uuid
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)


"""
Test of All functions which are dependent on models
"""


class UtilsSomeFunctionsWithModels(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'LiveChat'})

        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")

        LiveChatConfig.objects.create(max_customer_count=110)
        Profile.objects.create(user_id="919087654321", bot=bot_obj)
        Channel.objects.create(name='Web')
        Channel.objects.create(name='GoogleHome')
        Channel.objects.create(name='Alexa')
        Channel.objects.create(name='WhatsApp')
        Channel.objects.create(name='Android')
        Channel.objects.create(name='Facebook')
        Channel.objects.create(name='Microsoft')
        Channel.objects.create(name='Telegram')
        Channel.objects.create(name='GoogleBusinessMessages')
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

        customer_obj = LiveChatCustomer.objects.create(username="9087654321", agent_id=livechat_agent, is_session_exp=True, joined_date=datetime.now(
        ), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj, easychat_user_id="9087654321")

        Profile.objects.create(
            user_id="9087654321", bot=bot_obj, livechat_session_id=customer_obj.session_id)

        customer_obj = LiveChatCustomer.objects.create(username="9991653558", agent_id=livechat_agent, is_session_exp=False, joined_date=datetime.now(
        ), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj, easychat_user_id="9991653558")

        Profile.objects.create(
            user_id="9991653558", bot=bot_obj, livechat_session_id=customer_obj.session_id)

        customer_obj = LiveChatCustomer.objects.create(username="9729631330", is_session_exp=True, joined_date=datetime.now(
        ), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj, easychat_user_id="9729631330")

        Profile.objects.create(
            user_id="9729631330", bot=bot_obj, livechat_session_id=customer_obj.session_id)

    """
    function: create_and_enable_livechat
    input params:
        mobile_number: mobile number for easychat user used as user_id,
        category: 
        channel: WhatsApp as of now,
        bot_obj:
        message:
    output:
        This function is used to check for holiday ro non-working hour. If no holiday or wokring hour then it creates livechat customer.
    """

    def test_create_and_enable_livechat(self):
        # Need to add more test-cases
        logger.info("Testing create_and_enable_livechat...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting create_and_enable_livechat...\n")

        response = create_and_enable_livechat("9190876543", -1, "", None, "")
        self.assertEqual(
            response, "Our chat representatives are busy right now. Please try again in some time.")

        bot_obj = Bot.objects.all()[0]

        response = create_and_enable_livechat(
            "919087654321", -1, "WhatsApp", bot_obj, "hi")
        self.assertEqual(response, "")

        response = create_and_enable_livechat(
            "919087654321", -1, "GoogleBusinessMessages", bot_obj, "hi")
        self.assertEqual(response, "")

        response = create_and_enable_livechat(
            "919087654321", -1, "WhatsApp", bot_obj, "hi")
        self.assertEqual(response, "")

    """
    function: get_livechat_response
    input params:
        mobile_number: mobile number for easychat user used as user_id,
        message: message sent by easychat user,
        channel: WhatsApp as of now,
        bot_id: bot pk,
        channel_params:
    output:

        This function is used to get livechat response and send the message to livechat agent.
    """

    def test_get_livechat_response(self):
        logger.info("Testing get_livechat_response...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_livechat_response...\n")

        response = get_livechat_response("9190876543", "hi", "", -1, "")
        self.assertEqual(response["status_code"], 500)

        response = get_livechat_response("9190876543", "hi", "", 1, "")
        self.assertEqual(response["status_code"], 500)

        response = get_livechat_response("9190876543", "hi", "WhatsApp", 1, "")
        self.assertEqual(response["status_code"], 500)

        response = get_livechat_response(
            "9190876543", "hi", "GoogleBusinessMessages", 1, "")
        self.assertEqual(response["status_code"], 500)

        response = get_livechat_response(
            "9190876543", "hi", "WhatsApp", 1, "{\"attached_file_path\": \"https://test.allincall.in/test.png\"}")
        self.assertEqual(response["status_code"], 500)

        profile_obj = Profile.objects.all()[0]
        profile_obj.livechat_connected = True
        livechat_customer = LiveChatCustomer.objects.all()[0]
        profile_obj.livechat_session_id = livechat_customer.session_id
        profile_obj.save()

        response = get_livechat_response("919087654321", "hi", "WhatsApp", -1,
                                         "{\"attached_file_path\": \"https://test.allincall.in/test.png\"}")

        # self.assertEqual(response["status_code"], 200)

        response = get_livechat_response(
            "919087654321", "hi", "GoogleBusinessMessages", -1, "")

        # self.assertEqual(response["status_code"], 200)

    """
    function: get_livechat_userid
    input params:
        mobile_number: mobile number for easychat user used as user_id
    output:

        This function is used to get livechat session id used for livechat session.
    """

    def test_get_livechat_userid(self):
        logger.info("Testing get_livechat_userid...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_livechat_userid...\n")

        profile_obj = Profile.objects.all()[0]
        self.assertEqual(get_livechat_userid(
            "919087654321", "WhatsApp", profile_obj.bot.pk), profile_obj.livechat_session_id)

        profile_obj.livechat_connected = True
        profile_obj.livechat_session_id = "sj97sd67uhsdbg7tsdcytsyfh"
        profile_obj.save()

        self.assertEqual(get_livechat_userid(
            "919087654321", "WhatsApp", profile_obj.bot.pk), "sj97sd67uhsdbg7tsdcytsyfh")

        self.assertEqual(get_livechat_userid(
            "919084321", "WhatsApp", profile_obj.bot.pk), "")

    """
    function: check_for_livechat
    input params:
        mobile_number: mobile number for easychat user used as user_id
    output:

        This function is used to check if user has intiated livechat or not.

    """

    # def test_check_for_livechat(self):
    #     logger.info("Testing check_for_livechat...",
    #                 extra={'AppName': 'LiveChat'})
    #     print("\nTesting check_for_livechat...\n")

    #     profile_obj = Profile.objects.all()[0]

    #     self.assertEqual(check_for_livechat(
    #         "919087654321", "WhatsApp", profile_obj.bot.pk), profile_obj.livechat_connected)

    #     profile_obj.livechat_connected = True
    #     customer_obj = LiveChatCustomer.objects.get(username="9087654321")
    #     customer_obj.last_appearance_date = datetime.now()
    #     profile_obj.livechat_session_id = customer_obj.session_id
    #     profile_obj.save()
    #     customer_obj.save()

    #     self.assertEqual(check_for_livechat(
    #         "919087654321", "WhatsApp", profile_obj.bot.pk), True)

    #     customer_obj.last_appearance_date = datetime.now() - timedelta(minutes=10)
    #     customer_obj.save()
    #     self.assertEqual(check_for_livechat(
    #         "919087654321", "WhatsApp", profile_obj.bot.pk), False)

    """
    function: check_agent_assigned
    input params:
        livechat_cust_obj: LivechatCustomer object 
    output:

        This function is used to check wheter agent is assigned or not. if agent not assigned for longer than queue time it disconnects the livechat  
    """

    def test_check_agent_assigned(self):
        logger.info("Testing check_agent_assignedt...",
                    extra={'AppName': 'LiveChat'})
        print("Testing check_agent_assigned...\n")

        customer_obj = LiveChatCustomer.objects.get(username="9729631330")

        self.assertEqual(check_agent_assigned(customer_obj), False)

        customer_obj = LiveChatCustomer.objects.get(username="9087654321")
        print("is sesion exp", customer_obj.is_session_exp,
              customer_obj.username, customer_obj.easychat_user_id)
        self.assertEqual(check_agent_assigned(customer_obj), False)

        customer_obj = LiveChatCustomer.objects.get(username="9991653558")
        print("is sesion exp", customer_obj.is_session_exp,
              customer_obj.username, customer_obj.easychat_user_id)

        self.assertEqual(check_agent_assigned(customer_obj), True)
    """
    function: create_image_thumbnail
    input params:
        filepath: filepath of the image whose thumbnail is to be created
        filename: name of the file
    output:

        This function is used to genrate a thumbnail image  of image 
    """
    # def test_create_image_thumbnail(self):
    #     logger.info("Testing create_image_thumbnail...", extra={'AppName': 'LiveChat'})
    #     print("\nTesting create_image_thumbnail...\n")

    #     # filepath = "/files/GoogleBusinessMessages-attachment/test.jpeg"
    #     # filename = "test.jpeg"
    #     # expected_thumbnail_path = "" # because there is no image file at /files/GoogleBusinessMessages-attachment/test.jpeg

    #     # self.assertEqual(create_image_thumbnail(filepath, filename), expected_thumbnail_path)

    #     filepath = ""
    #     filename = ""
    #     expected_thumbnail_path=""

    #     self.assertEqual(create_image_thumbnail(filepath, filename), expected_thumbnail_path)
