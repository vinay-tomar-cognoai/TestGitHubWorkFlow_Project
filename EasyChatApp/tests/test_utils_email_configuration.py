# -*- coding: utf-8 -*-

from django.test import TestCase

from EasyChatApp.utils_email_configuration import get_message_analytics_chart_config, get_user_analytics_chart_config, \
    get_category_chart_config, get_channel_chart_config, get_message_analytics_data, get_user_analytics, get_category_analytics, get_channel_analytics
from EasyChatApp.models import EmailConfiguration, MISDashboard, MessageAnalyticsDaily, Channel, UniqueUsers, Category, Bot, User
from django.conf import settings
from django.db.models import Sum, Q, Count
from EasyChatApp.constants import *
import time
import math
from os import path
from urllib.parse import quote
from collections import OrderedDict
from orderedset import OrderedSet
import xlrd
import json
import logging

from datetime import datetime, timedelta
logger = logging.getLogger(__name__)


"""
Test of all functions which are in utils_alexa.py 
"""


class EasyChatAppUtilsEmailConfiguration(TestCase):

    def setUp(self):
        logger.info(
            "Setting up the test environment for EasyChatAppUtilsEmailConfiguration...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)

        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.save()
        cat_obj = Category.objects.create(name="testing")
        cat_obj1 = Category.objects.create(name="testing1")

        web_channel = Channel.objects.create(name="Web")
        web_channel1 = Channel.objects.create(name="Whatsapp")
        # web_channel2 = Channel.objects.create(name="Alexa")

        MISDashboard.objects.create(date=datetime.now(), user_id="test", session_id="test1", bot=bot_obj, message_received="hi",
                                    bot_response="hello, how may I assist you?", intent_name="Hi", channel_name="Web", category_name="testing", window_location="13.233.23.33", category=cat_obj)
        MISDashboard.objects.create(date=datetime.now() - timedelta(days=6), user_id="test1", session_id="test12", bot=bot_obj, message_received="bye",
                                    bot_response="thanks, hoping to serve you again?", intent_name="bye", channel_name="Web", category_name="testing1", window_location="13.233.23.233", category=cat_obj1)
        MISDashboard.objects.create(date=datetime.now() - timedelta(days=5), user_id="test1", session_id="test13", message_received="Is it working?", bot_response="No need to answer",
                                    bot=bot_obj, channel_name="Whatsapp", category_name="testing", window_location="13.233.23.33", category=cat_obj)
        UniqueUsers.objects.create(count=2, date=(datetime.now() - timedelta(days=6)).date(), bot=bot_obj, channel=web_channel)
        UniqueUsers.objects.create(count=5, date=(datetime.now() - timedelta(days=5)).date(), bot=bot_obj, channel=web_channel1)
        MessageAnalyticsDaily.objects.create(date_message_analytics=(datetime.now() - timedelta(days=6)).date(), total_messages_count=1,
                                             answered_query_count=1, unanswered_query_count=0, bot=bot_obj, category=cat_obj1, channel_message=web_channel)
        MessageAnalyticsDaily.objects.create(date_message_analytics=(datetime.now() - timedelta(days=5)).date(), total_messages_count=1,
                                             answered_query_count=0, unanswered_query_count=1, bot=bot_obj, category=cat_obj, channel_message=web_channel1)

    def test_get_message_analytics_chart_config(self):
        logger.info("Testing get_message_analytics_chart_config is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting et_message_analytics_chart_config is going on...\n")

        channels = []
        for channel in Channel.objects.all():
            channels.append(channel.name)

        bot_obj = Bot.objects.get(name="test1")

        chart_config = get_message_analytics_chart_config(
            bot_obj, channels, MessageAnalyticsDaily, MISDashboard, Channel)

        self.assertEqual(chart_config['data']
                         ['datasets'][1]['label'], "Answered")

        self.assertEqual(chart_config['data']
                         ['datasets'][2]['label'], "Unanswered")

    def test_get_user_analytics_chart_config(self):
        logger.info("Testing get_user_analytics_chart_config is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_user_analytics_chart_config is going on...\n")

        channels = []
        for channel in Channel.objects.all():
            channels.append(channel.name)

        bot_obj = Bot.objects.get(name="test1")

        chart_config = get_user_analytics_chart_config(
            bot_obj, channels, MISDashboard, UniqueUsers, Channel)

        self.assertEqual(
            chart_config['data']['datasets'][0]['label'], "Number of total users")

    def test_get_channel_analytics_chart_config(self):
        logger.info("Testing get_channel_analytics_chart_config is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_channels_analytics_chart_config is going on...\n")

        channels = []
        for channel in Channel.objects.all():
            channels.append(channel.name)

        bot_obj = Bot.objects.get(name="test1")

        chart_config, html = get_channel_chart_config(
            bot_obj, channels, MISDashboard)

        self.assertEqual(
            chart_config['data']['datasets'][0]['label'], "Number of total users")

    def test_get_category_analytics_chart_config(self):
        logger.info("Testing get_category_analytics_chart_config is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_category_analytics_chart_config is going on...\n")

        channels = []
        for channel in Channel.objects.all():
            channels.append(channel.name)

        bot_obj = Bot.objects.get(name="test1")

        chart_config, html = get_category_chart_config(
            bot_obj, channels, MISDashboard, Category)

        self.assertEqual(
            chart_config['data']['datasets'][0]['label'], "Number of total users")

    def test_get_message_analytics_data(self):
        logger.info("Testing get_message_analytics_data is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_message_analytics_data is going on...\n")
        channels = []
        for channel in Channel.objects.all():
            channels.append(channel.name)

        bot_obj = Bot.objects.get(name="test1")
        web_channel = Channel.objects.get(name="Web")
        cat_obj = Category.objects.get(name="testing")
        message_list = get_message_analytics_data(
            bot_obj, channels, MessageAnalyticsDaily, MISDashboard, Channel)

        total_count = 0
        for iterator in message_list:
            if iterator['total_messages'] != None:
                total_count += iterator['total_messages']

        self.assertEqual(total_count, 2)
        MessageAnalyticsDaily.objects.create(date_message_analytics=(datetime.now() - timedelta(days=6)).date(), total_messages_count=2,
                                             answered_query_count=1, unanswered_query_count=1, bot=bot_obj, category=cat_obj, channel_message=web_channel)

        message_list = get_message_analytics_data(
            bot_obj, channels, MessageAnalyticsDaily, MISDashboard, Channel)

        total_count = 0
        for iterator in message_list:
            if iterator['total_messages'] != None:
                total_count += iterator['total_messages']

        self.assertEqual(total_count, 4)
        MessageAnalyticsDaily.objects.create(date_message_analytics=(datetime.now() - timedelta(days=31)).date(), total_messages_count=2,
                                             answered_query_count=1, unanswered_query_count=1, bot=bot_obj, category=cat_obj, channel_message=web_channel)

        message_list = get_message_analytics_data(
            bot_obj, channels, MessageAnalyticsDaily, MISDashboard, Channel)

        total_count = 0
        for iterator in message_list:
            if iterator['total_messages'] != None:
                total_count += iterator['total_messages']

        self.assertEqual(total_count, 4)

    def test_get_user_analytics(self):
        logger.info("Testing get_user_analytics is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_user_analytics is going on...\n")
        channels = []
        for channel in Channel.objects.all():
            channels.append(channel.name)

        bot_obj = Bot.objects.get(name="test1")

        user_analytics_list = get_user_analytics(
            bot_obj, channels, MISDashboard, UniqueUsers, Channel)

        total_count = 0
        for iterator in user_analytics_list:
            total_count += iterator['count']

        self.assertEqual(total_count, 7)
        web_channel = Channel.objects.get(name="Web")

        UniqueUsers.objects.create(count=5, date=(datetime.now() - timedelta(days=7)).date(), bot=bot_obj, channel=web_channel)

        user_analytics_list = get_user_analytics(
            bot_obj, channels, MISDashboard, UniqueUsers, Channel)

        total_count = 0
        for iterator in user_analytics_list:
            total_count += iterator['count']

        self.assertEqual(total_count, 12)
        UniqueUsers.objects.create(count=5, date=datetime.now(
        ) - timedelta(days=31), bot=bot_obj, channel=web_channel)

        user_analytics_list = get_user_analytics(
            bot_obj, channels, MISDashboard, UniqueUsers, Channel)

        total_count = 0
        for iterator in user_analytics_list:
            total_count += iterator['count']

        self.assertEqual(total_count, 12)
        # total count should not change because new objectes created are of older than 30 days

    def test_get_channel_analytics(self):
        logger.info("Testing get_user_analytics is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_user_analytics is going on...\n")
        channels = []
        for channel in Channel.objects.all():
            channels.append(channel.name)

        bot_obj = Bot.objects.get(name="test1")

        channel_dict = get_channel_analytics(bot_obj, channels, MISDashboard)

        self.assertEqual(channel_dict['Web'], 1)

        self.assertEqual(channel_dict['Whatsapp'], 1)

    def test_get_category_analytics(self):
        logger.info("Testing get_user_analytics is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_user_analytics is going on...\n")

        channels = []
        for channel in Channel.objects.all():
            channels.append(channel.name)

        bot_obj = Bot.objects.get(name="test1")

        category_dict = get_category_analytics(
            bot_obj, channels, MISDashboard, Category)

        self.assertEqual(category_dict['testing'], 1)

        self.assertEqual(category_dict['testing1'], 1)
