# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.test import TestCase

from EasyChatApp.models import Bot, Intent, Tree, FormAssist, Channel
from EasyChatApp.views_formassist import FormAssistResponseAPI, SaveFormAssistTagAPI, DeleteFormAssistTagAPI
from EasyChatApp.utils_userflow import create_bot_response

from django.contrib.auth import get_user_model
from django.test import Client
from EasyChatApp.utils_custom_encryption import *

import base64
import random

import logging
import json
logger = logging.getLogger(__name__)


"""
Test of all functions which are in views_formassist.py 
"""


class FormAssistViewsAPI(TestCase):

    def setUp(self):
        logger.info(
            "Setting up the test environment for EasyChatApp: FormAssistViewsAPI...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        User = get_user_model()
        User.objects.create_user(
            'temporary', 'temporary@gmail.com', 'temporary')

    """
    function tested: test_form_assist_response
    input queries:
        input contains "tag_id" and "bot_id" which will be pass as input prameters
    expected output:
        return response code 200 if it can get intent name from tag_id sucessfully.
    """

    def test_form_assist_response(self):
        logger.info("Testing test_form_assist_response...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        bot_obj = Bot.objects.create(
            name="testing", is_deleted=False, is_uat=True, is_form_assist_enabled=True)

        intent_obj = Intent.objects.create(
            name="test", training_data=json.dumps({"0": "test"}))
        intent_obj.bots.add(bot_obj)

        for channel_obj in Channel.objects.all():
            intent_obj.channels.add(channel_obj)
        intent_obj.save()

        bot_response_obj = create_bot_response("Passed")

        tree_obj = intent_obj.tree
        tree_obj.response = bot_response_obj
        tree_obj.save()

        FormAssist.objects.create(
            tag_id="1", bot=bot_obj, intent=intent_obj)
        response = self.client.post(
            '/form-assist-response/', {'tag_id': '1', 'bot_id': bot_obj.pk}, follow=True)
        response = response.json()
        self.assertEqual(response["status"], 200)

        # Incorrect data
        response = self.client.post(
            '/form-assist-response/', {'tag_id': '1', 'bot_id': "200"}, follow=True)
        response = response.json()
        self.assertEqual(response["status"], 500)

    """
    function tested: test_form_assist_save_tag
    input queries:
        input parameters "form_assist_intent_name", "form_assist_id", "tag_id" and "bot_id"
    expected output:
        return response code 200 if form assist tag is saved sucessfully.
    """

    # def test_form_assist_save_tag(self):
    #     logger.info("Testing test_form_assist_save_tag...")

    #     User = get_user_model()
    #     user = User.objects.get(username='temporary')
    #     user.set_password('12345')
    #     user.save()
    #     c = Client()
    #     c.login(username='temporary', password='12345')

    #     bot_obj = Bot.objects.create(
    #         name="testing", is_deleted=False, is_uat=True, is_form_assist_enabled=True)

    #     intent_obj = Intent.objects.create(
    #         name="test", training_data=json.dumps({"0": "test"}), is_form_assist_enabled=True)
    #     intent_obj.bots.add(bot_obj)
    #     intent_obj.save()
    #     for channel_obj in Channel.objects.all():
    #         intent_obj.channels.add(channel_obj)
    #     intent_obj.save()

    #     bot_response_obj = create_bot_response("Passed")

    #     tree_obj = intent_obj.tree
    #     tree_obj.response = bot_response_obj
    #     tree_obj.save()

    #     FormAssist.objects.create(
    #         tag_id="1", bot=bot_obj, intent=intent_obj)

    #     raw_data = {'form_assist_intent': intent_obj.pk, 'form_assist_id': '1',
    #                 'form_assist_tag_id': '1', 'bot_id': bot_obj.pk}
    #     json_string = json.dumps(raw_data)
    #     custom_encrypt_obj = CustomEncrypt()
    #     data = custom_encrypt_obj.encrypt(json_string)
    #     response = c.post(
    #         '/save-tag/', {"json_string": data}, follow=True)
    #     response = response.json()
    #     self.assertEqual(response["status"], 200)

    #     # Incorrect data
    #     raw_data = {'form_assist_intent': intent_obj.pk, 'form_assist_id': '1',
    #                 'form_assist_tag_id': '1', 'bot_id': "20"}
    #     json_string = json.dumps(raw_data)
    #     custom_encrypt_obj = CustomEncrypt()
    #     data = custom_encrypt_obj.encrypt(json_string)
    #     response = c.post(
    #         '/save-tag/', {"json_string": data}, follow=True)
    #     response = response.json()
    #     self.assertEqual(response["status"], 500)

    """
    function tested: test_form_assist_delete_tag
    input queries:
        input parameters "form_assist_id" "bot_id"
    expected output:
        return response code 200 if form assist tag is deleted sucessfully.
    """

    def test_form_assist_delete_tag(self):
        logger.info("Testing test_form_assist_delete_tag...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        User = get_user_model()
        user = User.objects.get(username='temporary')
        user.set_password('12345')
        user.save()
        c = Client()
        c.login(username='temporary', password='12345')

        bot_obj = Bot.objects.create(
            name="testing", is_deleted=False, is_uat=True, is_form_assist_enabled=True)

        intent_obj = Intent.objects.create(
            name="test", training_data=json.dumps({"0": "test"}))
        intent_obj.bots.add(bot_obj)

        for channel_obj in Channel.objects.all():
            intent_obj.channels.add(channel_obj)
        intent_obj.save()

        bot_response_obj = create_bot_response("Passed")

        tree_obj = intent_obj.tree
        tree_obj.response = bot_response_obj
        tree_obj.save()

        FormAssist.objects.create(
            tag_id="1", bot=bot_obj, intent=intent_obj)

        raw_data = {'form_assist_id': '1', 'bot_id': bot_obj.pk}
        json_string = json.dumps(raw_data)
        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(json_string)
        response = c.post(
            '/delete-tag/', {"json_string": data}, follow=True)
        response = json.loads(custom_encrypt_obj.decrypt(response.json()))
        self.assertEqual(response["status"], 200)

        # Incorrect data
        raw_data = {'form_assist_id': '1', 'bot_id': "30"}
        json_string = json.dumps(raw_data)
        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.encrypt(json_string)
        response = c.post(
            '/delete-tag/', {"json_string": data}, follow=True)
        response = json.loads(custom_encrypt_obj.decrypt(response.json()))
        self.assertEqual(response["status"], 500)
