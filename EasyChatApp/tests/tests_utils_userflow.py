# -*- coding: utf-8 -*-

from django.test import TestCase

from EasyChatApp.utils_userflow import create_intent_for_user_flow, create_bot_response, create_bot_with_excel, create_user_flow_with_excel, store_this_data_locally, create_bot_with_questions_variations_answers
from EasyChatApp.models import Channel, Bot, User, MISDashboard, Config, BotResponse, Intent, Tree
from EasyChatApp.constants import *
from django.conf import settings

import xlrd
import json
import logging
logger = logging.getLogger(__name__)


"""
Test of all functions which are in utils_alexa.py 
"""


class EasyChatAppUtilsFAQS(TestCase):

    def setUp(self):
        logger.info(
            "Setting up the test environment for EasyChatAppUtilsFAQS...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        Config.objects.create(monthly_analytics_parameter=6, daily_analytics_parameter=7,
                              top_intents_parameter=5, app_url="http://localhost:8000", no_of_bots_allowed=100)
        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)
        user_obj1 = User.objects.create(
            username="test12345", password="test12345", role=BOT_BUILDER_ROLE, status="1", is_online=True)
        user_obj2 = User.objects.create(
            username="test123456", password="test123456", role=BOT_BUILDER_ROLE, status="1", is_online=True)
        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.save()
        bot_obj1 = Bot.objects.create(
            name="test2", slug="test2", bot_display_name="test2", bot_type="Simple")
        bot_obj1.users.add(user_obj1)
        bot_obj1.save()
        bot_obj2 = Bot.objects.create(
            name="test3", slug="test3", bot_display_name="test3", bot_type="Simple")
        bot_obj2.users.add(user_obj2)
        bot_obj2.save()

        Channel.objects.create(name="Web")
        Channel.objects.create(name="Whatsapp")
        Channel.objects.create(name="Alexa")
        BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}')

    """
    Stores the static file to local system using url
    """

    """
    function: test_store_this_data_locally
    input params:
        url: url for that file

    returns url of static file in local system
    """

    def test_store_this_data_locally(self):
        logger.info("Testing store_this_data_locally is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting store_this_data_locally is going on...\n")

        url = "https://image.shutterstock.com/image-photo/spotted-dear-chital-knha-national-260nw-1024196245.jpg"
        
        assert store_this_data_locally(url) == "https://easychat-dev.allincall.in/files/spotted-dear-chital-knha-national-260nw-1024196245.jpg"
        assert store_this_data_locally("") == ""

    """
    function tested: create_intent_for_user_flow
    input params:
        intent_name: name of intent
        bot_objs_list: list of bot objects
        category: category of intent

    returns newly created intent object and added to bots
    """

    def test_create_intent_for_user_flow(self):

        logger.info("Testing write_excel is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting write_excel is going on...\n")

        bot_objs = Bot.objects.all()
        assert create_intent_for_user_flow("Good", bot_objs, 'others').name == "Good"
        assert create_intent_for_user_flow("Bye", bot_objs, None).name == "Bye"

    """
    function: create_bot_response
    input params:
        answer: answer

    returns bot response using answer
    """

    def test_create_bot_response(self):
        logger.info("Testing create_bot_response is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting create_bot_response is going on...\n")

        answer = "Hello, how may I assist you?"

        bot_response_obj = create_bot_response(answer)

        self.assertEqual(json.loads(bot_response_obj.sentence)
                         ["items"][0]["text_response"], answer)

        self.assertEqual(BotResponse.objects.count(), 2)

    """
    function: create_user_flow_with_excel
    input params:
        filepath: path of excel
        bot_objs_list: list of bot objects

    creates 2-level flow with excel
    """

    def test_create_user_flow_with_excel(self):
        logger.info("Testing create_user_flow_with_excel is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting create_user_flow_with_excel is going on...\n")

    """
    function: create_bot_with_excel
    input params:
        filepath: path of excel
        bot_objs_list: list of bot objects

    creates FAQ bot with excel
    """

    # def test_create_bot_with_excel(self):
    #     logger.info("Testing create_bot_with_excel is going on...", extra={
    #                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    #     print("\nTesting create_bot_with_excel is going on...\n")

    #     user_obj = User.objects.all()[0]

    #     bot_objs = Bot.objects.all()

    #     file_path = settings.MEDIA_ROOT + "sjdhv.xlsx"
    #     response = create_bot_with_excel(file_path, bot_objs, user_obj)

    #     self.assertEqual(response["status"], 500)
    #     file_path = settings.MEDIA_ROOT + "/private/EasyChatTest.xls"

    #     response = create_bot_with_excel(file_path, bot_objs, user_obj)
    #     self.assertEqual(response["status"], 200)

    #     bot = bot_objs[0]

    #     intent_objs = Intent.objects.all()

    #     expected_questions_list = []
    #     expected_answers_list = []

    #     for intent in intent_objs:
    #         expected_questions_list.append(intent.name)
    #         expected_answers_list.append(json.loads(intent.tree.response.sentence)[
    #                                      "items"][0]["text_response"])

    #     expected_questions_list.sort()
    #     expected_answers_list.sort()

    #     automated_flow_create_wb = xlrd.open_workbook(
    #         "files/private/EasyChatTest.xls")
    #     excel_flows = automated_flow_create_wb.sheet_by_index(0)
    #     rows_limit = excel_flows.nrows
    #     cols_limit = excel_flows.ncols

    #     row_count = 1
    #     corrected_questions_list = []
    #     corrected_answers_list = []

    #     for row in range(rows_limit - 1):

    #         corrected_questions_list.append(
    #             excel_flows.cell_value(row_count, 0))
    #         corrected_answers_list.append(excel_flows.cell_value(row_count, 2))
    #         row_count += 1

    #     corrected_questions_list.sort()
    #     corrected_answers_list.sort()

    #     self.assertEqual(expected_questions_list, corrected_questions_list)
    #     self.assertEqual(expected_answers_list, corrected_answers_list)

    #     intent_obj = intent_objs.filter(bots=bot, name="Hi")[0]
    #     self.assertEqual(json.loads(intent_obj.tree.response.images)["items"], [
    #                      "https://easychat-dev.allincall.in/files/nature_03j22fB.jpg"])
    #     self.assertEqual(json.loads(
    #         intent_obj.tree.response.videos)["items"], [])
    #     self.assertEqual(json.loads(
    #         intent_obj.tree.response.cards)["items"], [])

    #     intent_obj = intent_objs.filter(bots=bot, name="bye")[0]
    #     self.assertEqual(json.loads(intent_obj.tree.response.videos)["items"], [
    #                      "https://www.youtube.com/embed/8cm1x4bC610"])
    #     self.assertEqual(json.loads(
    #         intent_obj.tree.response.images)["items"], [])
    #     self.assertEqual(json.loads(
    #         intent_obj.tree.response.cards)["items"], [])

    #     intent_obj = intent_objs.filter(bots=bot, name="Are you serious?")[0]
    #     self.assertEqual(json.loads(intent_obj.tree.response.cards)["items"], [
    #                      {'content': 'fhgfgh', 'img_url': 'https://easychat-dev.allincall.in/files/nature_X5BRUAL.jpg', 'link': 'https://easychat-dev.allincall.in/files/car_Nsab3bV.jpeg', 'title': 'ghf'}])
    #     self.assertEqual(json.loads(
    #         intent_obj.tree.response.images)["items"], [])
    #     self.assertEqual(json.loads(
    #         intent_obj.tree.response.videos)["items"], [])

    """
    function: create_bot_with_questions_variations_answers
    input params:
        questions, variations, answers, bot_obj, user_obj

    add intent from extracted faqs
    """

    def test_create_bot_with_questions_variations_answers(self):
        logger.info("Testing create_bot_with_questions_variations_answers is going on...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting create_bot_with_questions_variations_answers is going on...\n")

        questions = ['This is question']
        variations = ['This is variation..']
        answers = ['This is answer']
        user_obj = User.objects.all()[0]
        bot_obj = Bot.objects.all()[0]

        response = create_bot_with_questions_variations_answers(questions, variations, answers, bot_obj, user_obj)

        self.assertEqual(response["status"], 200)

        intent_objs = Intent.objects.filter(name="This is question")
        assert intent_objs.count() >= 0
        intent_obj = intent_objs[0]
        assert json.loads(intent_obj.tree.response.sentence)["items"][0]["text_response"] == "This is answer"

        questions = []
        response = create_bot_with_questions_variations_answers(questions, variations, answers, bot_obj, user_obj)
        self.assertEqual(response["status"], 500)
        self.assertEqual(response["message"], "Enough questions|variations|answers not provided")
