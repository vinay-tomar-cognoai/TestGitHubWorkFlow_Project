# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.test import TestCase
from django.contrib.auth import get_user_model

from EasyChatApp.models import Bot
from EasySearchApp.models import WebsiteLink, SearchUser, EasySearchConfig
from EasySearchApp.views import StartCrawlingAPI
from django.test import Client
from EasySearchApp.utils_custom_encryption import *

import logging
import json
logger = logging.getLogger(__name__)

"""
Test views of EasySearchApp
"""


class EasySearchViewsAPI(TestCase):

    def setUp(self):
        logger.info(
            "Setting up the test environment for EasySearchApp: EasySearchViewsAPI...", extra={'AppName': 'EasySearch'})
        User = get_user_model()
        User.objects.create_user(
            'temporary', 'temporary@gmail.com', 'temporary')

    """
    function tested: test_crawling
    input queries:
        query containing website link.
    expected output:
        return status code 200 if webpage is crawled successful
    checks for:
        same expected output and output from function tested
    """

    def test_crawling(self):
        logger.info("Testing test_crawling...", extra={'AppName': 'EasySearch'})

        StartCrawlingAPI.as_view()

        bot_obj = Bot.objects.create(
            name="testing", slug="testing", is_deleted=False, is_uat=True, is_form_assist_enabled=True)
        EasySearchConfig.objects.create(bot=bot_obj, feature="1")
        User = get_user_model()
        user = User.objects.get(username='temporary')
        user.set_password('12345')
        user.save()
        c = Client()
        c.login(username='temporary', password='12345')
        username_obj = User.objects.get(username="temporary")
        search_user_obj = SearchUser.objects.create(user=username_obj)
        link = 'https://allincall.in/'
        hyper_text = 'https'
        WebsiteLink.objects.create(
            search_user=search_user_obj, link=link, bot=bot_obj)

        # Correct data
        raw_data = {'url': link, 'hyper_text': hyper_text,
                    'bot_id': bot_obj.pk, 'index_value': '2'}
        json_string = json.dumps(raw_data)
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        response = c.post(
            '/search/start-crawling/', {"json_string": json_string}, follow=True)
        response = json.loads(custom_encrypt_obj.decrypt(response.json()))
        self.assertEqual(response["status"], 200)

        # Incorrect data
        raw_data = {'url': link, 'hyper_text': hyper_text,
                    'bot_id': "200", 'index_value': '2'}
        json_string = json.dumps(raw_data)
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        response = c.post(
            '/search/start-crawling/', {"json_string": json_string}, follow=True)
        response = json.loads(custom_encrypt_obj.decrypt(response.json()))
        self.assertEqual(response["status"], 500)

    """
    function tested: test_enable_google_search
    input queries:
        query containing cx id and bot id.
    expected output:
        return status code 200 if saved successfully
    """

    def test_enable_google_search(self):
        logger.info("Testing test_enable_google_search...", extra={'AppName': 'EasySearch'})

        bot_obj = Bot.objects.create(
            name="testing", slug="testing", is_deleted=False, is_uat=True, is_form_assist_enabled=True)
        EasySearchConfig.objects.create(bot=bot_obj, feature="2")
        User = get_user_model()
        user = User.objects.get(username='temporary')
        user.set_password('12345')
        user.save()
        c = Client()
        c.login(username='temporary', password='12345')
        # username_obj = User.objects.get(username="temporary")

        # Correct data
        raw_data = {
            'bot_id': bot_obj.pk,
            'search_cx': "123"
        }
        json_string = json.dumps(raw_data)
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        response = c.post(
            '/search/enable-g-search/', {"data": json_string}, follow=True)
        response = json.loads(custom_encrypt_obj.decrypt(response.json()))
        self.assertEqual(response["status_code"], 200)

        # Incorrect data
        raw_data = {
            'bot_id': "BOT",
            'search_cx': "123"
        }
        json_string = json.dumps(raw_data)
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        response = c.post(
            '/search/enable-g-search/', {"data": json_string}, follow=True)
        response = json.loads(custom_encrypt_obj.decrypt(response.json()))
        self.assertEqual(response["status_code"], 500)

    """
    function tested: test_enable_elastic_search
    input queries:
        query containing and bot id.
    expected output:
        return status code 200 if saved successfully
    """

    def test_enable_elastic_search(self):
        logger.info("Testing test_enable_elastic_search...", extra={'AppName': 'EasySearch'})

        bot_obj = Bot.objects.create(
            name="testing", slug="testing", is_deleted=False, is_uat=True, is_form_assist_enabled=True)
        EasySearchConfig.objects.create(bot=bot_obj, feature="1")
        User = get_user_model()
        user = User.objects.get(username='temporary')
        user.set_password('12345')
        user.save()
        c = Client()
        c.login(username='temporary', password='12345')
        User.objects.get(username="temporary")

        # Correct data
        raw_data = {
            'bot_id': bot_obj.pk,
        }
        json_string = json.dumps(raw_data)
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        response = c.post(
            '/search/enable-e-search/', {"data": json_string}, follow=True)
        response = json.loads(custom_encrypt_obj.decrypt(response.json()))
        self.assertEqual(response["status_code"], 200)

        # Incorrect data
        raw_data = {
            'bot_id': "BOT",
        }
        json_string = json.dumps(raw_data)
        custom_encrypt_obj = CustomEncrypt()
        json_string = custom_encrypt_obj.encrypt(json_string)
        response = c.post(
            '/search/enable-e-search/', {"data": json_string}, follow=True)
        response = json.loads(custom_encrypt_obj.decrypt(response.json()))
        self.assertEqual(response["status_code"], 500)
