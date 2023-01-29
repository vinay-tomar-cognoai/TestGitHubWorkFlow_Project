# -*- coding: utf-8 -*-

from django.test import TestCase

from EasyChatApp.utils_google import build_google_home_table_card_response, html_parser_for_google_response, build_google_home_text_speech_response,\
    build_google_home_suggestion_chips, build_google_home_visual_selection_list_select, easychat_url_validator, build_google_home_basic_card_response,\
    build_google_home_carousel_browse_response

import xlrd
import logging
logger = logging.getLogger(__name__)


"""
Test of all functions which are in utils_alexa.py 
"""


class EasyChatAppUtilsGoogle(TestCase):

    def setUp(self):
        logger.info(
            "Setting up the test environment for EasyChatAppUtilsGoogle...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    """
    function: build_google_home_carousel_browse_response
    input params:
        carousel_tiles: list of carousel card tiles
    builds carousel tiles response for google assistant according to template
    """

    def test_build_google_home_carousel_browse_response(self):
        logger.info(
            "Testing build_google_home_carousel_browse_response is going on...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting build_google_home_carousel_browse_response is going on...\n")

        carousel_tiles = []
        self.assertEqual(
            build_google_home_carousel_browse_response(carousel_tiles), None)

        carousel_tiles = [{"title": "EasyChat", "target_url": "http://google.com", "image_url": "/static/EasyChatApp/img/test.png/", "image_accessibility_text": "Done!!!"},
                          {"title": "EasyChat", "target_url": "http://google.com",
                              "image_url": "/static/EasyChatApp/img/test.png/", "image_accessibility_text": "Done!!!"},
                          {"title": "EasyChat", "target_url": "http://google.com", "image_url": "/static/EasyChatApp/img/test.png/", "image_accessibility_text": "Done!!!"}, ]

        self.assertEqual(len(build_google_home_carousel_browse_response(
            carousel_tiles)["carouselBrowse"]["items"]), 3)

    """
    function: build_google_home_basic_card_response
    input params:
        basic_card: json containing card details
    builds basic card response for google assistant according to template
    """

    def test_build_google_home_basic_card_response(self):
        logger.info(
            "Testing build_google_home_basic_card_response is going on...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting build_google_home_basic_card_response is going on...\n")

        self.assertEqual(build_google_home_basic_card_response(""), None)
        basicCard = {
            "title": "EasyChat",
            "image_url": "/static/EasyChatApp/img/test.png/",
            "image_accessibility_text": "Done!!!",
            "imageDisplayOptions": "CROPPED"
        }

        self.assertEqual(build_google_home_basic_card_response(
            basicCard)["basicCard"]["title"], "EasyChat")

    def test_easychat_url_validator(self):
        logger.info("Testing easychat_url_validator is going on...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting easychat_url_validator is going on...\n")

        test_url = ["google.com", "chat/bots/", "chat/login/",
                    "chat/logout/", "http://abcd.com.com.co"]
        # expected_responses = []
        # corrected_response = []

        for url in test_url:
            print(easychat_url_validator(url))

    """
    function: build_google_home_visual_selection_list_select
    input params:
        selection_list: list of recommedation
    builds recommedation response for google assistant according to template
    """

    def test_build_google_home_visual_selection_list_select(self):
        logger.info(
            "Testing build_google_home_visual_selection_list_select is going on...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting build_google_home_visual_selection_list_select is going on...\n")

        input_queries = [{"key": "hi", "value": "hello, how may I assist you?"}, {
            "key": "bye", "value": "Okay Thanks"}]
        expected_responses = [{"optionInfo": {"key": "hi"}, "title": "hello, how may I assist you?"}, {
            "optionInfo": {"key": "bye"}, "title": "Okay Thanks"}]

        DEFAULT_WEBHOOK_SYSTEM_INTENT = []
        corrected_response = []

        DEFAULT_WEBHOOK_SYSTEM_INTENT = build_google_home_visual_selection_list_select(
            input_queries)

        corrected_response = DEFAULT_WEBHOOK_SYSTEM_INTENT[
            "systemIntent"]["data"]["listSelect"]["items"]

        self.assertEqual(expected_responses, corrected_response)

    """
    function: build_google_home_suggestion_chips
    input params:
        title_list: list of title of suggection

    builds suggestion chips response for google assistant according to template
    """

    def test_build_google_home_suggestion_chips(self):
        logger.info("Testing build_google_home_suggestion_chips is going on...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting build_google_home_suggestion_chips is going on...\n")

        title_list = []

        self.assertEqual(build_google_home_suggestion_chips(title_list), None)

        title_list = ["abcd", "bcde", "cdef", "defg"]

        self.assertEqual(build_google_home_suggestion_chips(title_list), [
                         {"title": "abcd"}, {"title": "bcde"}, {"title": "cdef"}, {"title": "defg"}])

    """
    function: build_google_home_text_speech_response
    input params:
        text: text response
        speech: speech response

    builds simple response for google assistant according to template
    """

    def test_build_google_home_text_speech_response(self):
        logger.info(
            "Testing build_google_home_text_speech_response is going on...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting build_google_home_text_speech_response is going on...\n")

        input_queries = ['<b>Tell me salary details</b>', '<hr>What is your name',
                         '<h1 >Show me loans', '<a href="www.google.com">']
        expected_responses = ['Tell me salary details',
                              'What is your name', 'Show me loans', '']

        corrected_response = []

        for input_message in input_queries:
            corrected_response.append(build_google_home_text_speech_response(
                input_message, input_message)["simpleResponse"]["displayText"])

        self.assertEqual(expected_responses, corrected_response)

    """
    function tested: html_parser_for_google_response
    input params:
        questions: list of questions
        answers: list answers corresponding to qustion list
    saves excel containing qustion & answers pair 
    """

    def test_html_parser_for_google_response(self):

        logger.info("Testing html_parser_for_google_response is going on...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting html_parser_for_google_response is going on...\n")

        input_queries = ['<b>Tell me salary details</b>', '<hr>What is your name',
                         '<h1 >Show me loans', '<a href="www.google.com">']
        expected_responses = ['Tell me salary details',
                              'What is your name', 'Show me loans', '']
        removed_html_queries = []
        for query in input_queries:
            corrected = html_parser_for_google_response(query)
            removed_html_queries.append(corrected)
        self.assertEqual(expected_responses, removed_html_queries)
