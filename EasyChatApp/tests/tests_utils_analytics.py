# -*- coding: utf-8 -*-

from django.test import TestCase

from EasyChatApp.utils_analytics import get_word_mapper_dictionary, run_word_mapper, word_stemmer, remove_whitespace, embed_url, get_category_wise_intent_frequency,\
    build_internal_server_error_response, build_bot_not_found_response, invalid_channel_response, keyword_exist_in_string, process_string_for_intent_identification,\
    get_stem_words_of_sentence, query_bot, get_bot_objects_for_given_user, get_count_of_unanswered_messages, get_count_of_message_by_channel, get_count_of_answered_messages,\
    promoter_feedback_count, demoter_feedback_count, get_daily_count_of_messages, get_daily_count_of_users, get_window_location_frequency, get_recently_unanswered_messages,\
    get_intent_frequency, get_average_session_time, get_average_number_of_message_per_session, total_number_of_answered_queries, user_count, total_time,\
    get_daily_count_of_messages_categorized_by_intent, get_monthly_count_of_message, create_intent,\
    build_autocorrect_response, build_abuse_detected_response, build_suggestion_response, build_flow_break_response, get_parent_child_pair_intent, return_mis_objects_based_on_category_channel_language, get_multilingual_intent_obj_name, get_multilingual_tree_obj_name, update_multilingual_name, conversion_intent_analytics_translator, welcome_analytics_translator

from EasyChatApp.utils_api_analytics import get_combined_device_specific_analytics

from EasyChatApp.models import Category, WordMapper, Bot, User, Config, Tree, Channel, BotResponse, Intent, MISDashboard, Feedback, TimeSpentByUser, Profile,\
    ApiTree, TrafficSources, UnAnsweredQueries, Language, RequiredBotTemplate, LanguageTuningIntentTable, LanguageTuningTreeTable, UserSessionHealth

from django.conf import settings
from EasyChatApp.constants import *

import requests
import nltk
import sys
import copy
import xlwt
import random
from xlwt import Workbook

from datetime import timedelta
from datetime import datetime
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import logging
logger = logging.getLogger(__name__)


"""
Test of all functions which are in utils_alexa.py 
"""


class EasyChatAppUtilsAnalytics(TestCase):

    def setUp(self):
        logger.info(
            "Setting up the test environment for EasyChatAppUtilsAnalytics...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
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

        wordmapper_obj = WordMapper.objects.create(
            keyword="good night", similar_words="gn, good n8, gn8, gud n8")
        wordmapper_obj.bots.add(bot_obj)
        wordmapper_obj.save()
        wordmapper_obj1 = WordMapper.objects.create(
            keyword="mutual fund", similar_words="mf")
        wordmapper_obj1.bots.add(bot_obj1)
        wordmapper_obj1.save()
        wordmapper_obj2 = WordMapper.objects.create(
            keyword="how are you", similar_words="hrw")
        wordmapper_obj2.bots.add(bot_obj2)
        wordmapper_obj2.save()

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

        bot_response_obj1 = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Bye, have a nice time!", "speech_response": "Bye, have a nice time!", "text_reprompt_response": "Bye, have a nice time!", "speech_reprompt_response": "Bye, have a nice time!", "ssml_response": "Bye, have a nice time!"}]}')
        tree_obj1 = Tree.objects.create(name="bye", response=bot_response_obj1)
        intent_obj1 = Intent.objects.create(
            name="bye", tree=tree_obj1, keywords='{"0": "bye", "1": "you,soon,see,bye", "2": "leave,you,take,shall", "3": "good,bye", "4": "adios"}', training_data='{"0": "bye", "1": " bye see you soon", "2": " I shall take you leave now", "3": " good bye", "4": " adios"}')
        intent_obj1.bots.add(bot_obj)
        intent_obj1.channels.add(web_channel)
        intent_obj1.save()

        bot_response_obj2 = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Glad I made you laugh! How may I assist you now?", "speech_response": "Glad I made you laugh! How may I assist you now?", "text_reprompt_response": "Glad I made you laugh! How may I assist you now?", "speech_reprompt_response": "Glad I made you laugh! How may I assist you now?", "ssml_response": "Glad I made you laugh! How may I assist you now?"}]}')
        tree_obj2 = Tree.objects.create(name="lol", response=bot_response_obj2)
        intent_obj2 = Intent.objects.create(
            name="lol", tree=tree_obj2, keywords='{"0": "hilarious", "1": "funny", "2": "hilarious", "3": "funny", "4": "laugh,made", "5": "lamao", "6": "good,humour", "7": "lmao", "8": "lol"}', training_data='{"0": "hilarious", "1": " funny", "2": " this is hilarious", "3": " this is funny", "4": " this made me laugh", "5": " Lamao", "6": " Good Humour", "7": " LMAO", "8": "lol"}')
        intent_obj2.bots.add(bot_obj)
        intent_obj2.channels.add(web_channel)
        intent_obj2.save()

        MISDashboard.objects.create(date=datetime.now(), user_id="test", session_id="test1", bot=bot_obj, message_received="hi",
                                    bot_response="hello, how may I assist you?", intent_name="Hi", channel_name="Web", category_name="testing", window_location="13.233.23.33")
        MISDashboard.objects.create(date=datetime.now(), user_id="test1", session_id="test12", bot=bot_obj, message_received="bye",
                                    bot_response="thanks, hoping to serve you again?", intent_name="bye", channel_name="Web", category_name="testing1", window_location="13.233.23.233")
        MISDashboard.objects.create(date=datetime.now(), user_id="test1", session_id="test13", message_received="Is it working?", bot_response="No need to answer",
                                    bot=bot_obj1, channel_name="Whatsapp", category_name="testing", window_location="13.233.23.33")
        MISDashboard.objects.create(date=datetime.now(
        ), user_id="test3", message_received="It is not working.", bot_response="okay", session_id="test14", bot=bot_obj2, channel_name="Web", category_name="testing", window_location="13.233.23.33")

        Feedback.objects.create(
            user_id="1234", session_id="12345", bot=bot_obj, rating=4)
        Feedback.objects.create(
            user_id="12341", session_id="123451", bot=bot_obj, rating=4)
        Feedback.objects.create(
            user_id="12342", session_id="123452", bot=bot_obj1, rating=3)
        Feedback.objects.create(
            user_id="12343", session_id="123453", bot=bot_obj, rating=1)
        Feedback.objects.create(
            user_id="12344", session_id="123454", bot=bot_obj2, rating=4)
        Feedback.objects.create(
            user_id="12345", session_id="1234544", bot=bot_obj, rating=3)
        Feedback.objects.create(
            user_id="12345", session_id="12345444", bot=bot_obj2, rating=4)
        TrafficSources.objects.create(
            web_page="www.google.com", web_page_visited=10, bot_clicked_count=10, bot=bot_obj)
        
        lang_obj = Language.objects.create(lang="en")
        lang_obj1 = Language.objects.create(lang="hi")
        lang_obj2 = Language.objects.create(lang="ar")

        lang_tunning_tree_obj = LanguageTuningTreeTable.objects.create(language=lang_obj, tree=tree_obj, multilingual_name="Hi")
        LanguageTuningIntentTable.objects.create(language=lang_obj, intent=intent_obj, tree=lang_tunning_tree_obj, multilingual_name="Hi")
        lang_tunning_tree_obj1 = LanguageTuningTreeTable.objects.create(language=lang_obj1, tree=tree_obj1, multilingual_name="विदा")
        LanguageTuningIntentTable.objects.create(language=lang_obj1, intent=intent_obj1, tree=lang_tunning_tree_obj1, multilingual_name="विदा")
        lang_tunning_tree_obj2 = LanguageTuningTreeTable.objects.create(language=lang_obj2, tree=tree_obj2, multilingual_name="الضحك بصوت مرتفع")
        LanguageTuningIntentTable.objects.create(language=lang_obj2, intent=intent_obj2, tree=lang_tunning_tree_obj2, multilingual_name="الضحك بصوت مرتفع")

        RequiredBotTemplate.objects.create(
            bot=bot_obj,
            language=lang_obj,
            placeholder="Type here...",
            close_button_tooltip="Close",
            minimize_button_tooltip="Minimize",
            home_button_tooltip="Home",
            mic_button_tooltip="mic",
            typing_text="Typing",
            send_text="Send",
            cards_text="Know more",
            go_back_text="Go Back",
            menu_text="Menu",
            minimize_text="Click here to minimize",
            maximize_text="Click here to maximize",
            dropdown_text="Choose from the following ",
            search_text="Search",
            start_text="Start",
            stop_text="Stop",
            submit_text="Submit",
            uploading_video_text="Uploading your video. Please wait.",
            cancel_text="Cancel",
            file_attachment_text="Drag and drop your files here<br>Or Click in this area.",
            file_size_limit_text="File size must be less than",
            file_upload_success_text="Your file has been successfully uploaded.",
            feedback_text="Please provide your feedback",
            positive_feedback_options_text="Easy Communication$$$Fully Satisfied$$$Quick Response$$$Query Resolved Quickly$$$Good Experience",
            negative_feedback_options_text="Inappropriate Answer$$$Response is slow$$$Need more information$$$I couldn’t find what I was looking for$$$Content is too complicated",
            feedback_error_text="Please select from the below options.",
            success_feedback_text="Thank you for your feedback",
            csat_form_text="Was I Helpful?$$$Your feedback matters!$$$We value your feedback$$$Please complete this form to improve the experience.$$$Type here if selected others$$$Please provide your details so that we can contact you:$$$Enter Phone Number$$$Enter Email id$$$Tell us about your experience",
            csat_form_error_mobile_email_text="Please fill all the fields.$$$Please enter a valid phone number.$$$Please fill a valid email id.",
            csat_emoji_text="Angry$$$Sad$$$Neutral$$$Happy$$$Very Happy",
            date_range_picker_text="From Date$$$To Date$$$From Time$$$To Time$$$Select Range$$$Date$$$Time$$$Min$$$Max$$$Range",
            general_text="Did you mean one of the following?$$$There are some internal issue, please try again later. Sorry for your inconvenience.$$$Looks like I don't have answer for selected bot query.$$$Looks like I don't have support for this channel.$$$Session is running in another tab. Please end running sessions and try again.$$$I can tell you are upset. If my answers were not helpful, you can reach out to our customer care team.$$$Sorry to hear that, we would appreciate if you could give your comments on what went wrong. Please type 'Skip' in case you don't wish to give a comment.$$$Glad that you liked our service. Hope to see you again.$$$Thanks, we would try to improve.$$$Looks like I don't have an answer to that. Here's what I found on the web.$$$Sure, How may I assist you now?$$$Looks like, I can not answer your query for now. Please try again after some time.",
        )

    """
    function tested: build_flow_break_response
    input params:
        user: active user object
        bot_obj: active bot object
        message: flow break response
    output:
        return rich json response
    """

    def test_build_flow_break_response(self):
        logger.info("Testing build_flow_break_response...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting build_flow_break_response...\n")

        user_obj = Profile.objects.create(user_id="abcd")
        bot_obj = Bot.objects.all()[0]
        response = build_flow_break_response(
            user_obj, bot_obj, "Sorry!!!", None, None)

        self.assertEqual(response["response"][
                         "text_response"]["text"], "Sorry!!!")

        response = build_flow_break_response(
            None, bot_obj, "Sorry!!!", None, None)
        self.assertEqual(response["status_code"], 500)

        response = build_flow_break_response(
            user_obj, None, "Sorry!!!", None, None)
        self.assertEqual(response["status_code"], 500)

        response = build_flow_break_response(
            None, None, "Sorry!!!", None, None)
        self.assertEqual(response["status_code"], 500)

    """
    function tested: build_suggestion_response
    input params:
        user: active user object
        bot_obj: active bot object
        suggestion_list: suggested intent name list
    output:
        return rich json response
    """

    def test_build_suggestion_response(self):
        logger.info("Testing build_suggestion_response...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting build_suggestion_response...\n")

        user = Profile.objects.create(user_id="test123456")
        bot_obj = Bot.objects.all()[0]
        language_template_obj = RequiredBotTemplate.objects.all()[0]
        suggestion_list = ["Hi", "Bye"]

        assert build_suggestion_response(user, bot_obj, suggestion_list, None, None, language_template_obj)[
            "status_code"] == "200"

    """
    function tested: build_abuse_detected_response
    input params:
        user: active user object
        bot_obj: active bot object
        message: user message
    output:
        return rich bot json response
    """

    def test_build_abuse_detected_response(self):
        logger.info("Testing build_abuse_detected_response...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting build_abuse_detected_response...\n")

        user = Profile.objects.create(user_id="test123456")
        bot_obj = Bot.objects.all()[0]
        language_template_obj = RequiredBotTemplate.objects.all()[0]
        user_message = "Hi, testing is go."

        assert build_abuse_detected_response(user, bot_obj, user_message, None, None, language_template_obj)[
            "status_code"] == "200"

    """
    function tested: build_autocorrect_response
    input params:
        user: active user object
        bot_obj: active bot object
        user_message: user actual message
        corrected_message: corrected user message
    output:
        return rich bot json response
    """

    def test_build_autocorrect_response(self):
        logger.info("Testing build_autocorrect_response...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting build_autocorrect_response...\n")

        user = Profile.objects.create(user_id="test123456")
        bot_obj = Bot.objects.all()[0]
        language_template_obj = RequiredBotTemplate.objects.all()[0]
        user_message = "Hi, testing is go."
        corrected_message = "Hi, teting is going on."

        assert build_autocorrect_response(
            user, bot_obj, user_message, corrected_message, None, None, language_template_obj)["status_code"] == 500

    """
    function tested: build_internal_server_error_response

    builds rich json response in case of internal server error
    """

    def test_build_internal_server_error_response(self):
        logger.info("Testing build_internal_server_error_response...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting build_internal_server_error_response...\n")

        language_template_obj = RequiredBotTemplate.objects.all()[0]

        assert build_internal_server_error_response(None, None, None, None, language_template_obj)[
            "status_code"] == "200"

        assert build_internal_server_error_response(None, None, None, None, None)[
            "status_code"] == 500

    """
    function tested: create_intent
    input params:
        intent_name: name of intent
        variation_list: training sentences
        answer: text response of bot
        bot_obj: bot object for intent to be created
        Intent: Intent model
        Channel: Channel model
        BotResponse: BotResponse model
        is_part_of_suggestion_list: Boolean whether it will be part of suggestion list or not
    output:
        creates intent with given data
    """

    def test_create_intent(self):
        logger.info("Testing create_intent...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting create_intent...\n")

        bot = Bot.objects.all()[0]

        create_intent("testing", ["testing", "testing is going on.", "testing is in progress."],
                      "okay, waiting for response.", bot, Intent, Channel, BotResponse, True)

        self.assertEqual(Intent.objects.count(), 4)
        try:
            create_intent("testing", ["testing", "testing is going on.", "testing is in progress."],
                          "okay, waiting for response.", bot, Intent, Channel, BotResponse, True)
            print("Testing for duplicate intent Failed!")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            print("Testing for duplicate intent passed!")

    """
    function tested: get_monthly_count_of_message
    input params:
        User: user model
        Bot: Bot model
        MISDashboard: Misboard model
        username: username of active user
        bot_objs: list of bot objects
        year: year for which you want data
        month: month for which you want data
    output:
        returns number of total messages for that month
    """

    def test_get_monthly_count_of_message(self):
        logger.info("Testing get_monthly_count_of_message...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_monthly_count_of_message...\n")

        datetime_obj = datetime.now()
        year = datetime_obj.year
        month = datetime_obj.month

        bot_objs = Bot.objects.all()

        assert get_monthly_count_of_message(
            User, Bot, MISDashboard, year, month, "test1234", bot_objs) == 4

    """
    function tested: get_daily_count_of_messages_categorized_by_intent
    input params:
        User: user model
        Bot: Bot model
        MISDashboard: Misboard model
        username: username of active user
        bot_objs: list of bot objects
        year: year for which you want data
        month: month for which you want data
        day: day for which you want data
    output:
        returns list of number of total messages categorized_by_intent of that given day
    """

    def test_get_daily_count_of_messages_categorized_by_intent(self):
        logger.info(
            "Testing get_daily_count_of_messages_categorized_by_intent...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_daily_count_of_messages_categorized_by_intent...\n")

        datetime_obj = datetime.now()

        bot_objs = Bot.objects.all()

        self.assertEqual(get_daily_count_of_messages_categorized_by_intent(User, Bot, MISDashboard, datetime_obj, "test1234", bot_objs), [
                         {"intent_name": None, "frequency": 2}, {"intent_name": "Hi", "frequency": 1}, {"intent_name": "bye", "frequency": 1}])

    """
    function tested: total_time
    input params:
        TimeSpentByUser: TimeSpentByUser model
    output params:
        total time: total time spent by alll user

    returns total time spent by all user. Ex. If user1 spent 3,4 second and user2 spent 1,2 second on the bot, then it will return 10seconds in total
    """

    def test_total_time(self):
        logger.info("Testing total_time...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting total_time...\n")

        bot_objs = Bot.objects.all()
        total_time_spent = 0

        start_datetime = datetime.now() - timedelta(hours=1)
        end_datetime = datetime.now()
        for bot in bot_objs:
            TimeSpentByUser.objects.create(
                user_id="abcd", end_datetime=end_datetime, start_datetime=start_datetime)
            total_time_spent += 3600

        start_datetime = start_datetime - timedelta(hours=1)
        for bot in bot_objs:
            TimeSpentByUser.objects.create(
                user_id="based", end_datetime=end_datetime, start_datetime=start_datetime)
            total_time_spent += 7200

        self.assertEqual(total_time(TimeSpentByUser), total_time_spent)

    """
    function tested: user_count
    input params:
        TimeSpentByUser: TimeSpentByUser model
    output params:
        user_count: number of all users

    returns total number of users, who have open the chat window. There may be duplicate users.
    """

    def test_user_count(self):
        logger.info("Testing user_count...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting user_count...\n")

        bot_objs = Bot.objects.all()

        for bot in bot_objs:
            TimeSpentByUser.objects.create(user_id="abcd")
        for bot in bot_objs:
            TimeSpentByUser.objects.create(user_id="based")

        self.assertEqual(user_count(TimeSpentByUser), 6)

    """
    function tested: total_number_of_answered_queries
    input params:
        bot_objs: Bot object model
    output params:
        user_count: total number of answered queries

    returns total number of users in specified bot

    """

    def test_total_number_of_answered_queries(self):
        logger.info("Testing total_number_of_answered_queries...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting total_number_of_answered_queries...\n")

        bot_objs = Bot.objects.all()
        self.assertEqual(total_number_of_answered_queries(
            bot_objs, MISDashboard), 2)

    """
    function tested: get_average_number_of_message_per_session
    input params:
        bot_objs: Bot object model
    output params:
        average_number_of_message: Average number of messages per session

    returns total number of users in specified bot

    """

    def test_get_average_number_of_message_per_session(self):
        logger.info("Testing get_average_number_of_message_per_session...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_average_number_of_message_per_session...\n")

        bot_objs = Bot.objects.all()

        start_date = datetime.now() - timedelta(days=3)
        end_date = datetime.now() - timedelta(days=2)
        mis_objs = return_mis_objects_based_on_category_channel_language(
            start_date, end_date, bot_objs, "All", "All", "All", [], MISDashboard, UserSessionHealth)
        mis_objs = mis_objs.filter(is_session_started=True)

        expected_ans, _ = get_average_number_of_message_per_session(
            mis_objs)
        self.assertEqual(expected_ans, 0)

        MISDashboard.objects.create(date=datetime.now(
        ), user_id="test3", message_received="It is not worki.", bot=bot_objs[0], bot_response="okay", session_id="test14", channel_name="Web", category_name="testing", window_location="13.233.23.33")
        MISDashboard.objects.create(date=datetime.now(
        ), user_id="test3", message_received="It is not worki.", bot=bot_objs[0], bot_response="okay", session_id="test14", channel_name="Web", category_name="testing", window_location="13.233.23.33")
        MISDashboard.objects.create(date=datetime.now(
        ), user_id="test3", message_received="It is not worki.", bot=bot_objs[0], bot_response="okay", session_id="test14", channel_name="Web", category_name="testing", window_location="13.233.23.33")
        MISDashboard.objects.create(date=datetime.now(
        ), user_id="test3", message_received="It is not worki.", bot=bot_objs[0], bot_response="okay", session_id="test14", channel_name="Web", category_name="testing", window_location="13.233.23.33")

        end_date = datetime.now()
        mis_objs = return_mis_objects_based_on_category_channel_language(
            start_date, end_date, bot_objs, "All", "All", "All", [], MISDashboard, UserSessionHealth)
        mis_objs = mis_objs.filter(is_session_started=True)
        expected_ans, _ = get_average_number_of_message_per_session(
            mis_objs)
        self.assertEqual(expected_ans, 2)

    """
    function tested: get_average_session_time
    input params:
        TimeSpentByUser: 
        bot_objs: list of bot objects
    output:
        returns average time spent by users on bots
    """

    def test_get_average_session_time(self):
        logger.info("Testing get_average_session_time...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_average_session_time...\n")
        start_date = datetime.now() - timedelta(hours=1)
        end_date = datetime.now()
        bot_objs = Bot.objects.all()
        self.assertEqual(get_average_session_time(
            bot_objs, TimeSpentByUser, start_date, end_date), 0)

        expected_time_spent = 3600

        for bot in bot_objs:
            time_spent_obj = TimeSpentByUser.objects.create(
                start_datetime=start_date, end_datetime=end_date, bot=bot)
            time_spent_obj.total_time_spent = time_spent_obj.time_diff()
            time_spent_obj.save()

        self.assertEqual(expected_time_spent,
                         get_average_session_time(bot_objs, TimeSpentByUser, start_date, end_date))

    """
    function tested: get_intent_frequency
    input params:
        MISDashboard: Misboard model
        bot_objs: list of bot objects
    output:
        returns list of intents with their frequency
    """

    # def test_get_intent_frequency(self):
    #     logger.info("Testing get_intent_frequency...", extra={
    #                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    #     print("\nTesting get_intent_frequency...\n")

    #     bot_objs = Bot.objects.all()
    #     expected_list = [{"intent_name": "Hi", "frequency": 1}, {
    #         "intent_name": "bye", "frequency": 1}]
    #     expected_list = sorted(expected_list, key=lambda i: i['intent_name'])
    #     correct_list = get_intent_frequency(bot_objs, MISDashboard)
    #     correct_list = sorted(correct_list, key=lambda i: i['intent_name'])
    #     self.assertEqual(expected_list, correct_list)

    """
    function tested: get_recently_unanswered_messages
    input params:
        MISDashboard: Misboard model
        bot_objs: list of bot objects
    output:
        returns unanswered messages
    """

    # def test_get_recently_unanswered_messages(self):
    #     logger.info("Testing get_recently_unanswered_messages...", extra={
    #                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    #     print("\nTesting get_recently_unanswered_messages...\n")

    #     bot_objs = Bot.objects.all()
    #     expected_list = {"It is not working.": 1, "Is it working?": 1}

    #     correct_list = get_recently_unanswered_messages(
    #         bot_objs, MISDashboard, UnAnsweredQueries, Channel)
    #     correct_list_dict = {}
    #     for items in correct_list:
    #         correct_list_dict[items.unanswered_message] = items.count
    #     self.assertEqual(expected_list, correct_list_dict)

    """
    function tested: get_window_location_frequency
    input params:
        MISDashboard: Misboard model
        bot_objs: list of bot objects
        datetime_start: start date
        datetime_end: end date
    output:
        returns frequency of every hosts from where the bot gets request

    Ex. [{"localhost": 5}, {"13.233.0.125": 3}]
    """

    def test_get_window_location_frequency(self):
        logger.info("Testing get_window_location_frequency...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_window_location_frequency...\n")

        bot_objs = Bot.objects.get(pk=1)
        start_date = datetime.now()
        end_date = datetime.now()

        web_pages_name, web_page_visited_count, bot_clicked_count = get_window_location_frequency(
            bot_objs, TrafficSources, start_date, end_date)

        self.assertEqual(web_pages_name, ['www.google.com'])

    """
    function: get_category_wise_intent_frequency
    input params:
        bot_objs: 
        MISDashboard: Misboard model
        username: username of active user
    output:
        returns get_category_wise_intent_frequency

    Ex. [{'intent_name': 'Hi', 'frequency': 1}, {'intent_name': None, 'frequency': 0}]
    """

    # def test_get_category_wise_intent_frequency(self):
    #     logger.info("Testing get_category_wise_intent_frequency...", extra={
    #                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    #     print("\nTesting get_category_wise_intent_frequency...\n")

    #     bot_objs = Bot.objects.all()
    #     self.assertEqual(get_category_wise_intent_frequency(bot_objs, MISDashboard, "testing"), [
    #                      {'intent_name': 'Hi', 'frequency': 1}, {'intent_name': None, 'frequency': 0}])
    #     self.assertEqual(get_category_wise_intent_frequency(
    #         bot_objs, MISDashboard, "testing1"), [{'intent_name': 'bye', 'frequency': 1}])
    #     self.assertEqual(get_category_wise_intent_frequency(
    #         bot_objs, MISDashboard, "testing3"), [])

    """
    function tested: get_daily_count_of_users
    input params:
        User: user model
        Bot: Bot model
        MISDashboard: Misboard model
        username: username of active user
        bot_objs: list of bot objects
        year: year for which you want data
        month: month for which you want data
        day: day for which you want data
    output:
        returns number of total users for that given date
    """

    def test_get_daily_count_of_users(self):
        logger.info("Testing get_daily_count_of_messages...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_daily_count_of_messages...\n")

        datetime_obj = datetime.now()

        bot_objs = Bot.objects.all()

        assert get_daily_count_of_users(
            MISDashboard, UserSessionHealth, datetime_obj, bot_objs) == 3

    """
    function tested: get_daily_count_of_messages
    input params:
        User: user model
        Bot: Bot model
        MISDashboard: Misboard model
        username: username of active user
        bot_objs: list of bot objects
        year: year for which you want data
        month: month for which you want data
        day: day for which you want data
    output:
        returns number of total messages for that given date
    """

    def test_get_daily_count_of_messages(self):
        logger.info("Testing get_daily_count_of_messages...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_daily_count_of_messages...\n")

        datetime_obj = datetime.now()

        bot_objs = Bot.objects.all()

        assert get_daily_count_of_messages(
            MISDashboard, UserSessionHealth, datetime_obj, bot_objs) == 4

    """
    function tested: demoter_feedback_count
    input params:
        bot_objs: list of bot objects
    output:
        returns number of demoter responses for that bot
    """

    def test_demoter_feedback_count(self):
        logger.info("Testing demoter_feedback_count...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting demoter_feedback_count...\n")

        bot_objs = Bot.objects.all()
        channel_obj = None
        assert demoter_feedback_count(bot_objs, channel_obj, Feedback) == 1

    """
    function tested: promoter_feedback_count
    input params:
        bot_objs: list of bot objects
    output:
        returns number of promoter responses for that bot
    """

    def test_promoter_feedback_count(self):
        logger.info("Testing promoter_feedback_count...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting promoter_feedback_count...\n")

        bot_objs = Bot.objects.all()
        channel_obj = None
        assert promoter_feedback_count(bot_objs, channel_obj, Feedback) == 6

    """
    function tested: get_count_of_message_by_channel
    input params:
        User: user model
        Bot: Bot model
        MISDashboard: Misboard model
        Channel: Channel model
        username: username of active user
        bot_objs: list of bot objects
        year: year for which you want data
        month: month for which you want data
        day: day for which you want data
    output:
        returns json containg details of number of total message per channel
    """

    def test_get_count_of_message_by_channel(self):
        logger.info("Testing get_count_of_message_by_channel...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_count_of_message_by_channel...\n")

        bot_objs = Bot.objects.all()

        datetime_obj = datetime.now()

        expected_dict = {"Web": 3, "Whatsapp": 1, "Alexa": 0}
        correct_dict = get_count_of_message_by_channel(
            User, Bot, MISDashboard, Channel, datetime_obj, "test1234", bot_objs)

        self.assertEqual(expected_dict, correct_dict)

    """
    function tested: get_count_of_answered_messages
    input params:
        User: user model
        Bot: Bot model
        MISDashboard: Misboard model
        username: username of active user
        bot_objs: list of bot objects
        year: year for which you want data
        month: month for which you want data
        day: day for which you want data
    output:
        returns number of answered message on that given day
    """

    def test_get_count_of_answered_messages(self):
        logger.info("Testing get_count_of_answered_messages...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_count_of_answered_messages...\n")

        bot_objs = Bot.objects.all()

        datetime_obj = datetime.now()

        assert get_count_of_answered_messages(
            User, Bot, MISDashboard, datetime_obj, "test1234", bot_objs) == 2

    """
    function tested: get_count_of_unanswered_messages
    input params:
        User: user model
        Bot: Bot model
        MISDashboard: Misboard model
        username: username of active user
        bot_objs: list of bot objects
        year: year for which you want data
        month: month for which you want data
        day: day for which you want data
    output:
        returns number of unanswered message on that given day
    """

    def test_get_count_of_unanswered_messages(self):
        logger.info("Testing get_count_of_unanswered_messages...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_count_of_unanswered_messages...\n")

        bot_objs = Bot.objects.all()

        datetime_obj = datetime.now()

        assert get_count_of_unanswered_messages(
            User, Bot, MISDashboard, datetime_obj, "test1234", bot_objs) == 2

    """
    function tested: get_bot_objects_for_given_user
    input params:
        User: user model
        Bot: Bot model
        username: username of active user
    output:
        returns list of bot objects for given user
    """

    def test_get_bot_objects_for_given_user(self):
        logger.info("Testing get_bot_objects_for_given_user...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_bot_objects_for_given_user...\n")

        user_obj2 = User.objects.get(username="test123456")
        bot_obj3 = Bot.objects.create(
            name="test4", slug="test4", bot_display_name="test4", bot_type="Simple")
        bot_obj3.users.add(user_obj2)
        bot_obj3.save()
        expected_list = [["test1"], ["test2"], ["test3", "test4"]]
        correct_list = []
        user_objs = User.objects.all()

        for user in user_objs:
            bot_objs = get_bot_objects_for_given_user(user.username, User, Bot)
            bot_list = []
            for bot in bot_objs:
                bot_list.append(bot.name)

            correct_list.append(bot_list)

        self.assertEqual(expected_list, correct_list)

    """
    function tested: get_stem_words_of_sentence
    input params:
        sentence: input user query or message
    output:
        return list of stemmed keywords using NLP
    """

    def test_get_stem_words_of_sentence(self):
        logger.info("Testing get_stem_words_of_sentence...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_stem_words_of_sentence...\n")

        test_data = ["what is the better to say hi?", "I am going home",
                     "I rocks", "EasyChat testing is going on.**"]
        expected_list = [['what', 'better', 'say', 'hi'], [
            'going', 'home'], ['rock'], ['easychat', 'testing', 'going']]
        # if config_obj.is_easychat_ner_required:
        #     expected_list = [['what', 'better', 'say', 'hi'], [
        #         'going', 'home'], ['rocks'], ['easychat', 'testing', 'going']]

        correct_list = []
        for item in test_data:
            correct_list.append(get_stem_words_of_sentence(
                item, None, None, None, None))

        self.assertEqual(expected_list, correct_list)

        expected_list = [['better', 'say', 'hi'], [
            'am', 'home'], ['rock'], ['easychat', 'testing', 'on']]

        # if config_obj.is_easychat_ner_required:
        #     expected_list = [['better', 'say', 'hi'], [
        #         'am', 'home'], ['rocks'], ['easychat', 'testing', 'on']]
        #  for some ner optimisations this test case is updated
        bot_obj = Bot.objects.create(
            name="test4", slug="test4", bot_display_name="test4", bot_type="Simple")

        stop_words = '["is", "what", "going", "the", "to", "i"]'
        bot_obj.stop_keywords = stop_words

        bot_obj.save()

        correct_list = []
        for item in test_data:
            correct_list.append(get_stem_words_of_sentence(
                item, None, None, None, bot_obj))

        self.assertEqual(expected_list, correct_list)

    """
    function tested: process_string_for_intent_identification
    input params:
        sentence: string which contains all types of special character
    output:
        output string which contains only a-z, A-Z, 0-9 
    """

    def test_process_string_for_intent_identification(self):
        logger.info("Testing process_string_for_intent_identification...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting process_string_for_intent_identification...\n")

        test_data = ["Testing**  is @going on.", "hello@",
                     "what is @mutual fund ?", "*what is CASA ?", "!EasyChat is!! going on@*."]
        expected_list = ["testing is going on", "hello",
                         "what is mutual fund", "what is casa", "easychat is going on"]

        correct_list = []

        for item in test_data:
            correct_list.append(process_string_for_intent_identification(
                item, None, None, None, None))

        # print(expected_list)
        # print(correct_list)
        self.assertEqual(expected_list, correct_list)

    """
    function: keyword_exist_in_string
    input params:
        keyword_list: list of keywords
        query_string: string which to be checked for keywords
    output:
        returns True/False based on whether keyword is found in query string or not
    """

    def test_keyword_exist_in_string(self):
        logger.info("Testing keyword_exist_in_string...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting keyword_exist_in_string...\n")

        test_data = ["Testing  is going on.", "hello",
                     "what is mutual fund ?", "what is CASA ?", "EasyChat is going on."]
        keyword = ["testing", "hello", "mutual", "CASA", "LiveChat"]
        expected_list = [True, True, True, True, False]

        correct_list = []

        for item in test_data:
            correct_list.append(keyword_exist_in_string(keyword, item))

        # print(expected_list)
        # print(correct_list)
        self.assertEqual(expected_list, correct_list)

    """
    function tested: invalid_channel_response

    builds rich json response in case of invalid channel query
    """

    def test_invalid_channel_response(self):
        logger.info("Testing invalid_channel_response...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting invalid_channel_response...\n")

        response = invalid_channel_response(None, None, None, None)

        self.assertEqual(response["status_code"], "200")

    """
    function tested: build_bot_not_found_response

    builds rich json response in case of bot not found
    """

    def test_build_bot_not_found_response(self):
        logger.info("Testing build_bot_not_found_response...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting build_bot_not_found_response...\n")

        response = build_bot_not_found_response(None, None, None, None)

        self.assertEqual(response["status_code"], "200")

    """
    function tested: get_word_mapper_dictionary
    input params:
        WordMapper: model
        bot_obj: active bot object
    output:
        return dictionary which contains wordmappers
    """

    def test_get_word_mapper_dictionary(self):
        logger.info("Testing get_word_mapper_dictionary...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_word_mapper_dictionary...\n")

        bot_objs = Bot.objects.all()

        expected_dict_list = [{"gn": "good night", "good n8": "good night", "gn8": "good night",
                               "gud n8": "good night"}, {"mf": "mutual fund"}, {"hrw": "how are you"}]

        response_dict_list = []
        for bot_obj in bot_objs:
            response_dict_list.append(
                get_word_mapper_dictionary(WordMapper, bot_obj, None, None, None))

        self.assertEqual(expected_dict_list, response_dict_list)

    """
    function tested: run_word_mapper
    input params:
        WordMapper: model
        sentence: input user message
        bot_obj: active bot object
    output:
        return string after word mapping

    This function helps in mapping synonym words for example
    what is mf ? -> what is mutual fund ?
    """

    def test_run_word_mapper(self):
        logger.info("Testing run_word_mapper...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting run_word_mapper...\n")

        test_data = ["what is mf ?", "hrw ?", "gn"]
        expected_sentence_list = [["what is mf ?", "hrw ?", "good night"], [
            "what is mutual fund ?", "hrw ?", "gn"], ["what is mf ?", "how are you ?", "gn"]]
        correct_sentence_list = []

        bot_objs = Bot.objects.all()
        for bot_obj in bot_objs:
            tested_output_list = []
            for data in test_data:
                tested_output_list.append(
                    run_word_mapper(WordMapper, data, bot_obj, None, None, None))

            correct_sentence_list.append(tested_output_list)
        self.assertEqual(expected_sentence_list, correct_sentence_list)

    """
    function tested: word_stemmer
    input params:
        word: input token
    output:
        return stemmed token

    eg. sleeping -> sleep
    """

    def test_word_stemmer(self):
        logger.info("Testing word_stemmer...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting word_stemmer...\n")

        settings.EASYCHAT_LEMMATIZER_REQUIRED = False
        # config_obj = Config.objects.all().first()
        test_data = ["sleeping", "going", "rocks", "better", "corpora"]
        expected_list = ["sleep", "go", "rock", "better", "corpora"]
        # for ner realted optimsations updating this test case
        # if config_obj.is_easychat_ner_required:
        #     expected_list = ["sleeping", "going", "rocks", "better", "corpora"]
        correct_list = []
        
        for item in test_data:
            correct_list.append(word_stemmer(item))

        self.assertEqual(expected_list, correct_list)

        expected_list = ["sleeping", "going", "rock", "better", "corpus"]

        # if config_obj.is_easychat_ner_required:
        #     expected_list = ["sleeping", "going", "rocks", "better", "corpora"]

        settings.EASYCHAT_LEMMATIZER_REQUIRED = True
        correct_list = []
        for item in test_data:
            correct_list.append(word_stemmer(item))

        self.assertEqual(expected_list, correct_list)

    """
    function tested: remove_whitespace
    input params:
        sentence: string
    output:
        return string after removing extra whitespace

    """

    def test_remove_whitespace(self):
        logger.info("Testing remove_whitespace...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting remove_whitespace...\n")

        test_data = ["  Testing  is going on      .", "    hello",
                     "This is EasyChat    Plateform.   ", "EasyChat", "EasyChat testing is going on"]
        expected_list = ["Testing is going on .", "hello",
                         "This is EasyChat Plateform.", "EasyChat", "EasyChat testing is going on"]

        correct_list = []

        for item in test_data:
            correct_list.append(remove_whitespace(item))

        # print(expected_list)
        # print(correct_list)
        self.assertEqual(expected_list, correct_list)

    """
    function tested: embed_url
    input params:
        url: url, which needs to be embeded
    output:
        return embeded_url
    """

    def test_embed_url(self):
        logger.info("Testing embed_url...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting embed_url...\n")

        test_data = ["google.com", "https://www.youtube.com/watch?v=hR8FEdC6aAs", "https://www.primevideo.com/detail/0NLS2PB87FWDT7STVNQKBEPTHD/ref=atv_hm_hom_c_bV3MWc_hAFov2_1_1",
                     "https://www.youtube.com/watch?v=eRATk6iNmW4&list=RDeRATk6iNmW4&start_radio=1"]
        expected_list = ["google.com", "https://www.youtube.com/embed/hR8FEdC6aAs", "https://www.primevideo.com/detail/0NLS2PB87FWDT7STVNQKBEPTHD/ref=atv_hm_hom_c_bV3MWc_hAFov2_1_1",
                         "https://www.youtube.com/embed/eRATk6iNmW4&list=RDeRATk6iNmW4&start_radio=1"]

        correct_list = []

        for item in test_data:
            correct_list.append(embed_url(item))

        # print(expected_list)
        # print(correct_list)
        self.assertEqual(expected_list, correct_list)

    def test_get_parent_child_pair_intent(self):
        logger.info("Testing Get Parent Child Intent...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting Get Parent Child Intent...\n")
        intent_obj = Intent.objects.create(name="TestIntent")

        tree_obj = Tree.objects.create(name="Child Tree")

        api_obj = ApiTree.objects.create()

        api_obj.apis_used = "test_url_example"

        api_obj.save()

        tree_obj.api_tree = api_obj

        tree_obj.save()

        intent_tree = Tree.objects.create(name="Intent Tree")

        intent_tree.children.add(tree_obj)

        intent_tree.save()

        intent_obj.tree = intent_tree

        intent_obj.save()

        correct_list = []
        get_parent_child_pair_intent(intent_obj.tree, correct_list)
        expected_list = [(tree_obj, 'api')]
        self.assertEqual(expected_list, correct_list)
    
    """
    function: get_multilingual_intent_obj_name
    input params:
        intent_obj: Object of an intent
        selected_language: Language to be covert
        translate_api_status: Status of google API , default is True
    output:
        returns Translated text and Status of google API (True/False)
    """

    def test_get_multilingual_intent_obj_name(self):
        logger.info("Testing get_multilingual_intent_obj_name..", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_multilingual_intent_obj_name...\n")

        test_intent_name = ["Hi", "bye", "lol"]
        selected_language = ["en", "hi", "ar"]
        expected_intent_name = [("Hi", True), ("विदा", True), ("الضحك بصوت مرتفع", True)]

        correct_list = []

        for idx, intent_name in enumerate(test_intent_name):
            intent_obj = Intent.objects.filter(name=intent_name).first()
            correct_list.append(get_multilingual_intent_obj_name(intent_obj, selected_language[idx], True))
        self.assertEqual(expected_intent_name, correct_list)

    """
    function: get_multilingual_tree_obj_name
    input params:
        tree_obj: Object of an tree
        selected_language: Language to be covert
        translate_api_status: Status of google API , default is True
    output:
        returns Translated text and Status of google API (True/False)
    """

    def test_get_multilingual_tree_obj_name(self):
        logger.info("Testing get_multilingual_tree_obj_name..", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_multilingual_tree_obj_name...\n")

        test_tree_name = ["Hi", "bye", "lol"]
        selected_language = ["en", "hi", "ar"]
        expected_tree_name = [("Hi", True), ("विदा", True), ("الضحك بصوت مرتفع", True)]

        correct_list = []

        for idx, intent_name in enumerate(test_tree_name):
            tree_obj = Tree.objects.filter(name=intent_name).first()
            correct_list.append(get_multilingual_tree_obj_name(tree_obj, selected_language[idx], True))
        self.assertEqual(expected_tree_name, correct_list)

    """
    function: update_multilingual_name
    input params:
        dict_obj: List of dictionaries contain details of each intent
        selected_language: Language to be covert
        translate_api_status: Status of google API , default is True
    output:
        returns added multilingual_name in each dictionary and Status of google API (True/False)
    """

    def test_update_multilingual_name(self):
        logger.info("Testing update_multilingual_name..", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting update_multilingual_name...\n")

        test_dict_list = {'name': 'cars', 'children': [{'name': 'honda', 'children': [{'name': 'amaze', 'children': []}, {'name': 'city', 'children': []}]}, {'name': 'hyundai', 'children': [{'name': 'i20', 'children': [{'name': 'elantra', 'children': []}, {'name': 'sports', 'children': []}]}]}]}
        selected_language = "hi"
        expected_dict = {'name': 'cars', 'children': [{'name': 'honda', 'children': [{'name': 'amaze', 'children': [], 'multilingual_name': 'विस्मित करना'}, {'name': 'city', 'children': [], 'multilingual_name': 'शहर'}], 'multilingual_name': 'होंडा'}, {'name': 'hyundai', 'children': [{'name': 'i20', 'children': [{'name': 'elantra', 'children': [], 'multilingual_name': 'Elantra'}, {'name': 'sports', 'children': [], 'multilingual_name': 'खेल'}], 'multilingual_name': 'मैं -20'}], 'multilingual_name': 'हुंडई'}], 'multilingual_name': 'कारों'}
        correct_list, translate_api_status = update_multilingual_name(test_dict_list, selected_language, True)
        # If google translate API is failed we cannot check the results
        if translate_api_status:
            self.assertEqual(expected_dict, correct_list)

    """
    function: conversion_intent_analytics_translator
    input params:
        intent_completion_data: List of dictionaries contain details of each intent
        selected_language: Language to be covert
        translate_api_status: Status of google API , default is True
    output:
        returns added multilingual_name in each dictionary and Status of google API (True/False)
    """

    # def test_conversion_intent_analytics_translator(self):
    #     logger.info("Testing conversion_intent_analytics_translator.", extra={
    #         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    #     print("\nTesting conversion_intent_analytics_translator...\n")

    #     test_intent_list = [{'intent_name': 'lol', 'intent_recognized': 9, 'count': 2}, {'intent_name': 'bye', 'intent_recognized': 2, 'count': 1}]
    #     selected_language = "hi"
    #     expected_list = ([{'intent_name': 'lol', 'intent_recognized': 9, 'count': 2, 'multilingual_name': 'ज़ोर-ज़ोर से हंसना'}, {'intent_name': 'bye', 'intent_recognized': 2, 'count': 1, 'multilingual_name': 'विदा'}], True)
    #     correct_list = conversion_intent_analytics_translator(test_intent_list, selected_language, True)
    #     self.assertEqual(expected_list, correct_list)
    
    """
    function: welcome_analytics_translator
    input params:
        welcome_banner_clicked_data_count: List of dictionaries contain details of each banner clicked with intent
        selected_language: Language to be covert
        translate_api_status: Status of google API , default is True
    output:
        returns added multilingual_name in each dictionary and Status of google API (True/False)
    """

    def test_welcome_analytics_translator(self):
        logger.info("Testing welcome_analytics_translator.", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting welcome_analytics_translator...\n")

        test_banner_data = [{'web_page_visited': '-', 'preview_source': 'http://127.0.0.1:8000/files/cb1ae90e-289e-4b05-91ef-b05beea245f9_compressed.png', 'pk': 12, 'intent__name': 'Helpful', 'intent__pk': 12, 'frequency': 2}, {'web_page_visited': '-', 'preview_source': 'http://127.0.0.1:8000/files/ff0b62bf-231c-42ba-bd11-e1b3fa4b7f24_compressed.png', 'pk': 4, 'intent__name': 'bye', 'intent__pk': 2, 'frequency': 1}]
        select_language = "hi"
        expected_list = ([{'web_page_visited': '-', 'preview_source': 'http://127.0.0.1:8000/files/cb1ae90e-289e-4b05-91ef-b05beea245f9_compressed.png', 'pk': 12, 'intent__name': 'Helpful', 'intent__pk': 12, 'frequency': 2}, {'web_page_visited': '-', 'preview_source': 'http://127.0.0.1:8000/files/ff0b62bf-231c-42ba-bd11-e1b3fa4b7f24_compressed.png', 'pk': 4, 'intent__name': 'bye', 'intent__pk': 2, 'frequency': 1, 'multilingual_name': 'विदा'}], True)
        correct_list = welcome_analytics_translator(test_banner_data, select_language, True)
        self.assertEqual(expected_list, correct_list)

    """
    function: get_combined_device_specific_analytics
    input params:
        response: it is the response param
        bot_obj: the bot object associated
        datetime_start: filter's start time
        datetime_end: filter's end time
        channel_name: channel name given by filter
        category_name: category name given by filter
        selected_language: Language to be filtered
        supported_languages: all supported languages by bot
        filter_type: filter type 1(daily), 2(weekly), 3(monthly)
    output:
        returns added the count of users and messages related to device desktop or mobile
    """

    def test_get_combined_device_specific_analytics(self):
        logger.info("Testing get_combined_device_specific_analytics.", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting get_combined_device_specific_analytics...\n")
        response = {}
        bot_obj = Bot.objects.all()[0]
        bot_objs = [bot_obj]
        datetime_start = (datetime.today() - timedelta(7)).date()
        datetime_end = datetime.today().date()
        channel_name = "All"
        category_name = "All"
        selected_language = "All"
        supported_languages = Language.objects.all()
        filter_type = "1"

        response, status, message = get_combined_device_specific_analytics(response, bot_objs, datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, filter_type)
        
        self.assertEqual(2, response["device_specific_analytics_list"][-1]["total_messages_desktop"])
        self.assertEqual(2, response["device_specific_analytics_list"][-1]["total_answered_messages_desktop"])
        self.assertEqual(2, response["device_specific_analytics_list"][-1]["total_users_desktop"])
        self.assertEqual(200, status)

        response = {}
        channel_name = "Alexa"
        category_name = "testing1"
        category_obj = Category.objects.create(name=category_name, bot=bot_obj)

        MISDashboard.objects.create(date=datetime.now(
        ), user_id="test1", message_received="It is not working.", bot_response="okay", session_id="test1", bot=bot_obj, channel_name="Alexa", category_name="testing1", window_location="13.233.23.33", category=category_obj)

        response, status, message = get_combined_device_specific_analytics(response, bot_objs, datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, filter_type)
        self.assertEqual(400, status)

        response = {}
        channel_name = "Web"

        MISDashboard.objects.create(
            date=datetime.now(), user_id="test4", message_received="It is not working.", bot_response="okay", session_id="test4", bot=bot_obj, channel_name="Web", category_name="testing1", window_location="13.233.23.33", category=category_obj)

        response, status, message = get_combined_device_specific_analytics(response, bot_objs, datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, filter_type)
        logger.info("Testing get_combined_device_specific_analytics respones 1. %s %s %s", channel_name, category_name, str(response), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        self.assertEqual(200, status)
        self.assertEqual(3, response["device_specific_analytics_list"][-1]["total_users_desktop"])
        self.assertEqual(1, response["device_specific_analytics_list"][-1]["total_answered_messages_desktop"])
        self.assertEqual(1, response["device_specific_analytics_list"][-1]["total_messages_desktop"])
