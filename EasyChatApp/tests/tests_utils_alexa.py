# -*- coding: utf-8 -*-

from django.test import TestCase
from EasyChatApp.utils_alexa import build_alexa_speech_response, build_alexa_account_linking_response
import logging
logger = logging.getLogger(__name__)


"""
Test of all functions which are in utils_alexa.py 
"""


class EasyChatAppUtilsAlexa(TestCase):

    def setUp(self):
        logger.info(
            "Setting up the test environment for EasyChatApp: Alexa...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    """
    function tested: test_build_alexa_speech_response
    input queries:
        welcome_message: bot welcome message
        is_end_session: True/False
    expected output:
        return response
    """

    def test_build_alexa_speech_response(self):
        logger.info("Testing build_alexa_speech_response...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting build_alexa_speech_response...\n")

        welcome_message = ["hi, how may I assist you?",
                           "hey, how are you doing?", "Hey, This is easychat plateform."]
        is_session_end = [True, False, True]
        count = 0

        for item in welcome_message:
            response = build_alexa_speech_response(item, is_session_end[count])
            self.assertEqual(response["version"], "1.0")
            self.assertEqual(
                (response["response"]["outputSpeech"]["text"]), item)
            self.assertEqual(
                response["response"]["shouldEndSession"], is_session_end[count])

            count += 1

    """
    function tested: test_build_alexa_account_linking_response
    input queries:
        speech_output:
    expected output:
        return response
    """

    def test_build_alexa_account_linking_response(self):
        logger.info("Testing build_alexa_account_linking_response...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting build_alexa_account_linking_response...\n")

        response = build_alexa_account_linking_response("test")

        self.assertEqual(response["version"], "1.0")
