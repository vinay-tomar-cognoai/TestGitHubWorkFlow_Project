# -*- coding: utf-8 -*-
from LiveChatApp.utils import DecryptVariable
from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.easychat_utils_objects import EasyChatChannelParams, EasyChatBotUser
from EasyChatApp.models import BotInfo, User, Agent, Tree, Intent, Processor, Data, Profile, ApiTree, Authentication, UserAuthentication, Bot, Channel, BotChannel, Config, BotResponse, TagMapper, AuditTrail, EasyChatDrive, SandboxUser, IntentTreeHash, EasyChatTranslationCache
from EasyChatApp.utils import get_parent_tree_obj, get_intent_obj_from_tree_obj, is_allowed, is_livechat_access_allowed, is_tms_access_allowed, set_user, get_intent_name, process_api, save_data, check_user_auth, is_flow_ended, is_feedback_required, is_authentication_required, get_identified_intent, \
    is_active_user_authenticated, is_form_assist_activated, spell_checker, get_last_identified_intent_name, build_error_response, load_old_data, check_terminal_tree_logic, get_api_elapsed_time, save_default_parameter_for_flow, return_next_tree_based_on_message, clear_user_data, delete_intent, get_tag_mapper_list_for_given_user, get_authentication_objs, get_uat_bots, get_form_assist_uat_bots, get_lead_generation_uat_bots,\
    get_uat_bots_pk_list, get_google_search_results, load_the_dictionary, get_edit_distance_threshold, process_string, save_audit_trail, get_all_file_type, insert_file_into_intent_from_drive, is_campaign_link_enabled, get_channel_obj, get_hashed_intent_name, return_user_tree_based_on_intent_hash,\
    get_bot_object_and_save_last_query_time, is_lead_generation_enabled, save_user_flow_details, get_previous_bot_id, is_sticky_message_enabled, whatsapp_nps_update, return_autocorrect_response, return_user_tree_based_suggestion, return_next_tree_based_is_go_back_enabled, save_flow_analytics_data_pipe_processor, return_widgets, save_flow_analytics_data_pipe_processor_none
from EasyChatApp.utils_google_home_query import build_google_home_response, build_google_home_welcome_response
from django.test import TestCase
from rest_framework.test import APIClient
from django.test.client import RequestFactory

import execjs
import base64
from Crypto import Random
from Crypto.Cipher import AES

from EasyChatApp.utils import manage_default_livechat_intent, create_default_livechat_trigger_intent, remove_default_livechat_trigger_intent, is_it_livechat_manager,\
    create_default_intents, save_form_assist_analytics, replace_data_values, get_intent_category_name, get_php_processor_response, get_java_processor_response,\
    identify_intent_tree, return_next_tree_based_on_intent_identification, execute_pipeprocessor, return_next_tree, execute_api, get_encrypted_message, check_access_for_user,\
    get_message_list_using_pk, add_changes, apply_filter_api_analytics, get_masked_data, add_confirmation_and_reset_tree, remove_confirmation_and_reset_tree, get_message_list_and_icon_name, build_suggestions_and_word_mapper,\
    check_and_reset_user, check_tms_ticket_status, create_an_issue_tms, check_for_expired_credentials, successfull_file_upload_response, is_similar_words_format_correct, is_similar_words_already_exist, check_for_tms_intent_and_create_categories,\
    create_tms_categories, get_correct_words, update_dropdown_choices_of_tms_intent, check_for_system_commands, check_and_parse_channel_messages, check_channel_status_and_message, check_is_flow_terminated,\
    check_is_flow_termination_break, check_if_abort_flow_initiated, return_tree_if_flow_aborted

from EasyChatApp.utils_build_bot import sync_word_mapper_with_intent

from EasyChatApp.models import WordMapper, MISDashboard, Feedback, TimeSpentByUser,\
    FormAssist, FormAssistAnalytics, Category, AccessManagement, AccessType,\
    APIElapsedTime, ChunksOfSuggestions, Language, FlowAnalytics, WordDictionary, RequiredBotTemplate

from EasyChatApp.utils_bot import check_two_minute_bot_welcome_message, check_and_create_default_language_object, check_and_create_required_bot_language_template_for_selected_language
from EasyChatApp.utils_voicebot import validate_speed_and_pitch_values, process_speech_response, get_selected_tts_provider_name
from EasyTMSApp.models import TicketCategory, Ticket, LeaveCalendar, WorkingCalendar

from LiveChatApp.models import LiveChatUser, LiveChatCustomer
from EasyChatApp.default_intent_constants import *
from EasyChatApp.constants import *

from django.conf import settings
from django.utils import timezone

import requests
import nltk
import sys
import copy
import xlwt
import json
import random
from xlwt import Workbook

from datetime import timedelta
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import logging
logger = logging.getLogger(__name__)


"""
Test of all functions which are in utils_alexa.py 
"""


class EasyChatAppUtils(TestCase):

    def setUp(self):
        Config.objects.create(monthly_analytics_parameter=6, daily_analytics_parameter=7,
                              top_intents_parameter=5, app_url="http://localhost:8000", no_of_bots_allowed=100)
        logger.info(
            "Setting up the test environment for EasyChatAppUtils...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    """
    function tested: test_get_encrypted_message
    
    input_params:
        message: text message, it can be by bot or user.
    output_params:
        encrypted_message: encrypted message by RSA ecryption using allincall_public_key key.
    """

    def test_get_encrypted_message(self):
        logger.info("Testing of get_encrypted_message is going on.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of get_encrypted_message is going on.\n")

        self.assertEqual(DecryptVariable(get_encrypted_message(
            "Hi", None, None, None, None, False)), "Hi")

    """
    function tested: get_masked_data
    input params:
        user: active user object
        api_caller: executed code written by developer
        is_cache: True|False (to be saved permanetly in data model or not)
        cache_variable: json data will be saved in this variable
    output:
        returns api_response after execution of code
    """

    # def test_get_masked_data(self):
    #     logger.info("Testing of get_masked_data is going on.", extra={
    #                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    #     print("\n\n\nTesting of get_masked_data is going on.\n")

    #     test_sentence = "This is testing"
    #     expected_response = test_sentence
    #     correct_response = get_masked_data(
    #         test_sentence, None, None, None, None)

    #     self.assertEqual(expected_response, correct_response)

    #     test_sentence = "My username is test123. I have 5 rs."
    #     expected_response = "My username is ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae. I have c81d40dbeed369f1476086cf882dd36bf1c3dc35e07006f0bec588b983055487 rs."
    #     correct_response = get_masked_data(
    #         test_sentence, None, None, None, None)

    #     self.assertEqual(expected_response, correct_response)

    #     test_sentence = "My mobile number is 9012345678. Who are you?"
    #     expected_response = "My mobile number is e917869a180f491f5fe6d443d27d2fd8532623b5638464254b53fe426a4fd4b5. Who are you?"
    #     correct_response = get_masked_data(
    #         test_sentence, None, None, None, None)

    #     self.assertEqual(expected_response, correct_response)
    #     test_sentence = "My name is test4567. My PAN is BDWPJ5333B and account number 1234567543."
    #     expected_response = "My name is af0790ab6dfcbf25af421b9fa785dfee58148f897d920b028fb984b088b895dc. My PAN is 0e443d73cb5a2875f398f2fcdefeb8b8d5e6b877f37f96223a822da886f93895 and account number 25619bdfdd3f2e9b670190fd967b31a30dbe4493df3d0d7336cf57f177b2d2ee."
    #     correct_response = get_masked_data(
    #         test_sentence, None, None, None, None)

    #     self.assertEqual(expected_response, correct_response)
    #     test_sentence = """Thank you 'status': 'vikash' for connecting "vikash" customer care. I have 111321 rs. My PAN number is CEQPK4956K. My mobile number is 9920262298 my username is test12345. I have 2000rs. My dob is 19/10/1998 or 1998/10/19 . my aadhar number is 291313129560"."""
    #     expected_response = """Thank you 'status': 'vikash' for connecting "vikash" customer care. I have 55b1399f83f31dc43399afbc9ceb2417a8d07d39ec8282a36682f63cbfe4fbf9 rs. My PAN number is fc2045ec157769861f8f058880357bcd291f9c75a49d6149675841bc43bd8eb3. My mobile number is 4e6f3061ccfc1bf39e7a30c4e141a9ec11afba4e4266e6cc389e7ccdac270194 my username is 6fec2a9601d5b3581c94f2150fc07fa3d6e45808079428354b868e412b76e6bb. I have 989c32b00f0142150744d7f939bf0fb1b341c6cc076ba48a7ae1bef8ed0c1321. My dob is 1a00644c456957fa8fac6dca77213ad9c26d3c2d1c45d43892e8a29b6e159f24 or 580452003a3fa13c10cffcf8a7bd1299cede798f9932dc51a3f4f37cb885632d . my aadhar number is 0791c1793dd5911580c92d1dfee1a6966f9924f66f1ca7b553a062b21d169b9b"."""
    #     correct_response = get_masked_data(
    #         test_sentence, None, None, None, None)

    #     self.assertEqual(expected_response, correct_response)
    """
    function tested: execute_api
    input params:
        user: active user object
        api_caller: executed code written by developer
        is_cache: True|False (to be saved permanetly in data model or not)
        cache_variable: json data will be saved in this variable
    output:
        returns api_response after execution of code
    """

    def test_execute_api(self):
        logger.info("Testing of execute_api is going on.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of execute_api is going on.\n")

        easychat_user = Profile.objects.create(user_id="test123")
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}', modes_param='{"choosen_file_type": ".png"}', modes='{"is_typable": "true", "is_attachment_required": "true", "is_button": "true", "is_slidable": "false", "is_date": "false", "is_dropdown": "false"}')
        tree_obj = Tree.objects.create(name="Hi", response=bot_response_obj)
        easychat_user.tree = tree_obj
        easychat_user.save()

        api_response = execute_api(
            easychat_user, API_TREE_BASE_PYTHON_CODE_TEST, False, "test123", None, None, None)

        self.assertEqual(api_response["status_code"], "200")
        self.assertEqual(easychat_user.tree, tree_obj)

        api_response = execute_api(
            easychat_user, API_TREE_BASE_PYTHON_CODE_TEST_1, False, "test123", None, None, None)

        self.assertEqual(api_response["status_code"], "500")
        self.assertEqual(easychat_user.tree, None)

    """
    function tested: return_next_tree
    input params:
        user: active user object
        bot_obj: active bot object
        message: processed user message
        channel_of_message: channel from which message is received
    output:
        return (tree, bool, list)
        tree: next_tree identified based on message
        bool: whether re-sentence is required or not
        list: suggestion list of required
    """

    def test_return_next_tree(self):
        logger.info("Testing of return_next_tree is going on.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of return_next_tree is going on.\n")

        processor_obj = Processor.objects.create(name="testing")
        processor_obj.function = POST_PROCESSOR_BASE_PYTHON_CODE
        processor_obj.processor_lang = "1"
        processor_obj.save()

        easychat_user = Profile.objects.create(user_id="test123")
        web_channel = Channel.objects.create(name="Web")
        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)

        easychat_params = EasyChatChannelParams({}, easychat_user.user_id)

        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()
        bot_info_obj.is_advance_tree_level_nlp_enabled = False
        bot_info_obj.save()
        bot_obj.users.add(user_obj)
        bot_obj.save()
        category_obj = Category.objects.create(
            name="testcategory", bot=bot_obj)
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}', modes_param='{"choosen_file_type": ".png"}', modes='{"is_typable": "true", "is_attachment_required": "true", "is_button": "true", "is_slidable": "false", "is_date": "false", "is_dropdown": "false"}')
        tree_obj = Tree.objects.create(name="Hi", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Hi", tree=tree_obj, is_authentication_required=False, is_feedback_required=True, keywords='{"0": "hey", "1": "hello", "2": "hi", "3": "whats"}', training_data='{"0": "Hey", "1": " hello", "2": " hi", "3": " whats up"}', category=category_obj)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()
        easychat_bot_user = EasyChatBotUser(
            user=easychat_user, bot_obj=bot_obj, channel_name="Web", src=None, bot_id=bot_obj.pk, bot_info_obj=bot_info_obj)
        response = return_next_tree(
            "Hi", easychat_user, easychat_bot_user, easychat_params, "", [])
        self.assertEqual(response, (tree_obj, False, [], None, ' hi', '100', {}))

        easychat_user.tree = tree_obj
        easychat_user.save()

        response = return_next_tree(
            "Hi", easychat_user, easychat_bot_user, easychat_params, "", [])

        self.assertEqual(response, (tree_obj, True, [], None, '', '', {}))

        child_bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Thank you for connecting.", "speech_response": "Thank you for connecting.", "text_reprompt_response": "Thank you for connecting.", "speech_reprompt_response": "Thank you for connecting."}]}', modes_param='{"choosen_file_type": ".png"}', modes='{"is_typable": "true", "is_attachment_required": "true", "is_button": "true", "is_slidable": "false", "is_date": "false", "is_dropdown": "false"}')
        child_tree_obj = Tree.objects.create(
            name="Bye", response=child_bot_response_obj)
        tree_obj.children.add(child_tree_obj)
        tree_obj.save()

        response = return_next_tree(
            "Hi", easychat_user, easychat_bot_user, easychat_params, "", [])
        self.assertEqual(response, (child_tree_obj, False, [], None, '', '', {}))

        tree_obj.post_processor = processor_obj
        tree_obj.children.remove(child_tree_obj)
        tree_obj.save()

        response = return_next_tree(
            "Hi", easychat_user, easychat_bot_user, easychat_params, "", [])
        self.assertEqual(response, (None, False, [], None, '', '', {}))

        child_tree_obj = Tree.objects.create(
            name="Bye", response=child_bot_response_obj)
        tree_obj.children.add(child_tree_obj)
        tree_obj.save()

        response = return_next_tree(
            "Hi", easychat_user, easychat_bot_user, easychat_params, "", [])
        self.assertEqual(response, (child_tree_obj, False, [], None, '', '', {}))

        child_tree_obj1 = Tree.objects.create(
            name="testing", response=child_bot_response_obj)
        tree_obj.children.add(child_tree_obj1)
        tree_obj.save()

        response = return_next_tree(
            "Hi", easychat_user, easychat_bot_user, easychat_params, "", [])
        self.assertEqual(response, (None, False, [], None, '', '', {}))

        processor_obj.function = POST_PROCESSOR_BASE_PYTHON_CODE_TEST
        processor_obj.save()

        response = return_next_tree(
            "Hi", easychat_user, easychat_bot_user, easychat_params, "", [])
        self.assertEqual(response, (child_tree_obj1, False, [], None, '', '', {}))

        processor_obj.function = POST_PROCESSOR_BASE_PYTHON_CODE_TEST_206
        processor_obj.save()
        response = return_next_tree(
            "Hi", easychat_user, easychat_bot_user, easychat_params, "", [])
        self.assertEqual(response, (tree_obj, True, [], None, '', '', {"is_repeat_tree": True}))

        processor_obj.function = POST_PROCESSOR_BASE_PYTHON_CODE_TEST_308
        processor_obj.save()
        response = return_next_tree(
            "Hi", easychat_user, easychat_bot_user, easychat_params, "", [])
        self.assertEqual(response, (tree_obj, False, [], None, ' hi', '100', {}))

        processor_obj.function = POST_PROCESSOR_BASE_PYTHON_CODE_TEST_NONE
        processor_obj.save()
        response = return_next_tree(
            "Hi", easychat_user, easychat_bot_user, easychat_params, "", [])
        self.assertEqual(response, (None, False, [], None, '', '', {}))

    """
    function tested: execute_pipeprocessor
    input params:
        user: active user object

    execute given function and save details into data model.
    mostly used for processing user pipe
    """

    # def test_execute_pipeprocessor(self):
    #     logger.info("Testing of conflict_intent_identification is going on.", extra={
    #                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    #     print("\n\n\nTesting of conflict_intent_identification is going on.\n")

    #     easychat_user = Profile.objects.create(user_id="test123")

    #     tree_obj = Tree.objects.create(name="Hi")
    #     bot_obj = Bot.objects.create(name="testing3212")

    #     processor_obj = Processor.objects.create(name="testing")
    #     processor_obj.function = PIPE_PROCESSOR_BASE_PYTHON_CODE
    #     processor_obj.processor_lang = "1"
    #     processor_obj.save()
    #     tree_obj.pipe_processor = processor_obj
    #     tree_obj.save()
    #     easychat_user.tree = tree_obj
    #     easychat_user.save()
    #     response = execute_pipeprocessor(easychat_user, bot_obj, None, None)
    #     self.assertEqual(response, ('testing', False))

    #     processor_obj.function = PIPE_PROCESSOR_BASE_JS_CODE
    #     processor_obj.processor_lang = "4"
    #     processor_obj.save()
    #     response = execute_pipeprocessor(easychat_user, bot_obj, None, None)
    #     self.assertEqual(response, ('testing', False))

    #     processor_obj.function = PIPE_PROCESSOR_BASE_PHP_CODE
    #     processor_obj.processor_lang = "3"
    #     processor_obj.save()
    #     response = execute_pipeprocessor(easychat_user, bot_obj, None, None)
    #     self.assertEqual(response, ('testing', True))

    #     processor_obj.function = PIPE_PROCESSOR_BASE_JAVA_CODE
    #     processor_obj.processor_lang = "2"
    #     processor_obj.save()
    #     response = execute_pipeprocessor(easychat_user, bot_obj, None, None)
    #     self.assertEqual(response, ('testing', True))

    """
    @params: user - current user
             bot_obj - current bot
             message - user message
             channel_of_message - channel from where user message has come
             current_tree

    @output:
             next_tree - next selected tree based on user message after intent identification
             status_re_sentence - True | False
             suggestion list
    """

    def test_return_next_tree_based_on_intent_identification(self):
        logger.info(
            "Testing of return_next_tree_based_on_intent_identification is going on.", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of return_next_tree_based_on_intent_identification is going on.\n")

        easychat_user = Profile.objects.create(user_id="test123")
        web_channel = Channel.objects.create(name="Web")
        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)

        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.save()
        category_obj = Category.objects.create(
            name="testcategory", bot=bot_obj)
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}', modes_param='{"choosen_file_type": ".png"}', modes='{"is_typable": "true", "is_attachment_required": "true", "is_button": "true", "is_slidable": "false", "is_date": "false", "is_dropdown": "false"}')
        tree_obj = Tree.objects.create(name="Hi", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Hi", tree=tree_obj, is_authentication_required=False, is_feedback_required=True, keywords='{"0": "hey", "1": "hello", "2": "hi", "3": "whats"}', training_data='{"0": "Hey", "1": " hello", "2": " hi", "3": " whats up"}', category=category_obj)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()
        intent_obj = Intent.objects.get(pk=intent_obj.pk)
        test_authentication_tree = Tree.objects.create(
            name="TestAuthenticationTree")
        test_authentication_object = Authentication.objects.create(
            name="TestAuthentication", tree=test_authentication_tree, auth_time=300)
        UserAuthentication.objects.create(
            user=Profile.objects.get(user_id="test123"), auth_type=test_authentication_object)
        intent_obj.auth_type = test_authentication_object
        intent_obj.is_authentication_required = True
        intent_obj.save()

        response = return_next_tree_based_on_intent_identification(
            easychat_user, bot_obj, "Hi", "Web", tree_obj, "en", None, "", [], None)

        self.assertEqual(response, (tree_obj, False, [], ' hi', '100'))

        easychat_user = Profile.objects.get(user_id="test123")

        self.assertEqual(easychat_user.previous_tree, None)

        response = return_next_tree_based_on_intent_identification(
            easychat_user, bot_obj, "testing", "Web", None, "en", None, "", [], None)
        self.assertEqual(response, (None, False, [], '', ''))

        response = return_next_tree_based_on_intent_identification(
            easychat_user, bot_obj, "Hi", "Web", tree_obj, "en", category_obj.name, "", [], None)
        self.assertEqual(response, (tree_obj, False, [], ' hi', '100'))

        tree_obj = Tree.objects.create(name="testing", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="testing", tree=tree_obj, is_authentication_required=False, is_feedback_required=True, keywords='{"0": "testing"}', training_data='{"0": "testing"}', category=category_obj,)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()
        intent_obj = Intent.objects.get(pk=intent_obj.pk)

        response = return_next_tree_based_on_intent_identification(
            easychat_user, bot_obj, "testing", "Web", None, "en", category_obj.name, "", [], None)
        self.assertEqual(response, (tree_obj, False, [], 'testing', '100'))

        response = return_next_tree_based_on_intent_identification(
            easychat_user, bot_obj, "Hi", "Web", tree_obj, "en", "Others", "", [], None)
        self.assertEqual(response, (tree_obj, True, [], '', ''))

    """
    function tested: identify_intent_tree
    input params:
        user: active user object
        bot_obj: active bot object
        message: user message
        channel_of_message: channel from which message has been received
    output:
        return (tree, list)
        tree: identified intent tree based on user message
        list: suggestion list of required
    """

    def test_identify_intent_tree(self):
        logger.info("Testing of identify_intent_tree is going on.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of identify_intent_tree is going on.\n")

        easychat_user = Profile.objects.create(user_id="test123")
        web_channel = Channel.objects.create(name="Web")
        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)

        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.save()
        category_obj = Category.objects.create(
            name="testcategory", bot=bot_obj)
        Category.objects.create(
            name="testcategory2", bot=bot_obj)
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}', modes_param='{"choosen_file_type": ".png"}', modes='{"is_typable": "true", "is_attachment_required": "true", "is_button": "true", "is_slidable": "false", "is_date": "false", "is_dropdown": "false"}')
        tree_obj = Tree.objects.create(name="Hi", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Hi", tree=tree_obj, is_authentication_required=False, is_feedback_required=True, keywords='{"0": "hey", "1": "hello", "2": "hi", "3": "whats"}', training_data='{"0": "Hey", "1": " hello", "2": " hi", "3": " whats up"}', category=category_obj)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()

        response = identify_intent_tree(
            easychat_user, bot_obj, "Hi", "Web", None, None, "", [], None)
        self.assertEqual(response, (tree_obj, [], ' hi', '100'))

        easychat_user = Data.objects.get(
            user=easychat_user, variable="is_feedback_required")
        self.assertEqual(json.loads(easychat_user.get_value()), True)

        easychat_user = Data.objects.get(user=Profile.objects.get(
            user_id="test123"), variable="is_authentication_required")
        self.assertEqual(json.loads(easychat_user.get_value()), False)

        ##  is_authentication_required = True

        intent_obj = Intent.objects.get(pk=intent_obj.pk)
        test_authentication_tree = Tree.objects.create(
            name="TestAuthenticationTree")
        test_authentication_object = Authentication.objects.create(
            name="TestAuthentication", tree=test_authentication_tree, auth_time=300)
        UserAuthentication.objects.create(
            user=Profile.objects.get(user_id="test123"), auth_type=test_authentication_object)
        intent_obj.auth_type = test_authentication_object
        intent_obj.is_authentication_required = True
        intent_obj.save()

        response = identify_intent_tree(
            easychat_user, bot_obj, "Hi", "Web", None, None, "", [], None)
        self.assertEqual(response, (None, [], ' hi', '100'))

        bot_obj.is_easychat_ner_required = False
        bot_obj.save()

        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Thank you for reaching out.", "speech_response": "Thank you for reaching out.", "text_reprompt_response": "Thank you for reaching out.", "speech_reprompt_response": "Thank you for reaching out."}]}')
        tree_obj = Tree.objects.create(
            name="hi how are you?", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="hi how are you?", tree=tree_obj, keywords='{"0": "hi", "1": "hello"}', training_data='{"0": " how are you", "1": " hry", "2": " hello, how are you?", "3": " hi hry"}', category=category_obj)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()

        response = identify_intent_tree(
            easychat_user, bot_obj, "hi how are you?", "Web", None, None, "", [], None)
        # self.assertEqual(response, (None, ['Hi how are you?', 'Hi']))
        self.assertEqual(response, (None, [], '', ''))

        response = identify_intent_tree(
            easychat_user, bot_obj, "Testing is going on?", "Web", None, None, "", [], None)
        self.assertEqual(response, (None, [], '', ''))

        tree_obj = Tree.objects.create(
            name="Namaste", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Namaste", tree=tree_obj, keywords='{"0": "Namaste"}', training_data='{"0": "Namaste"}', category=category_obj)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()

        response = identify_intent_tree(
            easychat_user, bot_obj, "Namaste", "Web", None, "testcategory", "", [], None)
        self.assertEqual(response, (tree_obj, [], 'Namaste', '100'))

        response = identify_intent_tree(
            easychat_user, bot_obj, "Namaste", "Web", None, "testcategory2", "", [], None)
        self.assertEqual(response, (None, [], '', ''))

    """
    function tested: get_java_processor_response
    input params:
        code: processor code written in java
        parameter: It is a default variable. In case of post and pipe processor, it holds a value pass by respective processors.
    output:
        response: It is the response packet after execution of processor code in java.

    This function is used to run all the processor code written in java.
    """

    # def test_get_java_processor_response(self):
    #     logger.info("Testing of get_java_processor_response is going on.", extra={
    #                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    #     print("\n\n\nTesting of get_java_processor_response is going on.\n")

    #     code = """
    #         import java.util.*;
    #         import org.json.simple.JSONObject;
    #         public class EasyChatConsole {
    #           public static void main(String[] args){
    #             String input_x = args[0];
    #             JSONObject json_response = new JSONObject();
    #             json_response.put("status_code", "500");
    #             json_response.put("status_message", "Internal server error.");
    #             json_response.put("child_choice", "");
    #             json_response.put("data", new JSONObject());
    #             try{
    #                 /**write your code here*/
    #                 json_response.put("status_code", "200");
    #                 json_response.put("status_message", "SUCCESS");
    #                 json_response.put("value_of_x", input_x);
    #                 System.out.println(json_response);
    #             }catch(Exception e){
    #                 json_response.put("status_code", "500");
    #                 json_response.put("status_message", "ERROR :-  "+e.toString());
    #                 System.out.println(json_response);
    #             }
    #          }
    #         }
    #     """

    #     user_obj = Profile.objects.create(user_id="test123")
    #     response = get_java_processor_response(
    #         code, user_obj, None, None, None, "5")

    #     self.assertEqual(response["status_code"], "200")
    #     self.assertEqual(response["status_message"], 'SUCCESS')
    #     self.assertEqual(response["value_of_x"], '5')

    #     code = """
    #         import java.util.*;
    #         import org.json.simple.JSONObject;
    #         public class EasyChatConsole {
    #           public static void main(String[] args){
    #             String input_x = args[0];
    #             JSONObject json_response = new JSONObject();
    #             json_response.put("status_code", "500");
    #             json_response.put("status_message", "Internal server error.");
    #             json_response.put("child_choice", "");
    #             json_response.put("data", new JSONObject())
    #             try{
    #                 /**write your code here*/
    #                 json_response.put("status_code", "200");
    #                 json_response.put("status_message", "SUCCESS");
    #                 System.out.println(json_response);
    #             }catch(Exception e){
    #                 json_response.put("status_code", "500");
    #                 json_response.put("status_message", "ERROR :-  "+e.toString());
    #                 System.out.println(json_response);
    #             }
    #          }
    #         }
    #     """

    #     response = get_java_processor_response(
    #         code, user_obj, None, None, None, "5")
    #     self.assertEqual(response["status_code"], "500")

    """
    function tested: get_php_processor_response
    input params:
        code: processor code written in php
        parameter: It is a default variable. In case of post and pipe processor, it holds a value pass by respective processors.
    output:
        response: It is the response packet after execution of processor code in php.

    This function is used to run all the processor code written in php.
    """

    # def test_get_php_processor_response(self):
    #     logger.info("Testing of get_php_processor_response is going on.", extra={
    #                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    #     print("\n\n\nTesting of get_php_processor_response is going on.\n")

    #     code = """
    #         <?php
    #         function f($x){
    #             $json_response = array(
    #                 "status_code"=>"500",
    #                 "status_message"=>"Internal server error.",
    #                 "recur_flag"=> true,
    #                 "message"=> ""
    #             );
    #             try{
    #                 // write your code here
    #                 $x = trim(preg_replace('/\s+/', ' ', $x));
    #                 $json_response["value_of_x"] = $x;
    #                 $json_response["status_code"] = "200";
    #                 $json_response["status_message"] = "SUCCESS";
    #                 return $json_response;
    #             }catch(Exception $e){
    #                 $json_response["status_code"] = "500";
    #                 $json_response["status_message"] = "Error :- " + strval($e);
    #                 return $json_response;
    #             }
    #         }
    #         ?>

    #     """

    #     user_obj = Profile.objects.create(user_id="test123")
    #     response = get_php_processor_response(
    #         code, user_obj, None, None, None, "5")

    #     self.assertEqual(response["recur_flag"], True)
    #     self.assertEqual(response["status_code"], "200")
    #     self.assertEqual(response["status_message"], 'SUCCESS')
    #     self.assertEqual(response["value_of_x"], '5')

    #     code = """
    #         <?php
    #         function f($x){
    #             $json_response = array(
    #                 "status_code"=>"500",
    #                 "status_message"=>"Internal server error.",
    #                 "recur_flag"=> true,
    #                 "message"=> ""
    #             );
    #             try{
    #                 // write your code here
    #                 $x = trim(preg_replace('/\s+/', ' ', $x));
    #                 $json_response["value_of_x"] = $x
    #                 $json_response["status_code"] = "200";
    #                 $json_response["status_message"] = "SUCCESS";
    #                 return $json_response;
    #             }catch(Exception $e){
    #                 $json_response["status_code"] = "500";
    #                 $json_response["status_message"] = "Error :- " + strval($e);
    #                 return $json_response;
    #             }
    #         }
    #         ?>

    #     """

    #     response = get_php_processor_response(
    #         code, user_obj, None, None, None, "5")
    #     self.assertEqual(response["status_code"], "500")

    """
    function tested: get_intent_category_name
    input params:
        tree: active user tree
    output
        category_name

    returns category name as "" for inflow tree and 
    name of intent category in case of root tree
    """

    def test_get_intent_category_name(self):
        logger.info("Testing of get_intent_category_name is going on.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of get_intent_category_name is going on.\n")

        web_channel = Channel.objects.create(name="Web")
        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)

        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.save()
        category_obj = Category.objects.create(
            name="testcategory", bot=bot_obj)
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}')
        tree_obj = Tree.objects.create(name="Hi", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Hi", tree=tree_obj, keywords='{"0": "hey", "1": "hello", "2": "hi", "3": "whats"}', training_data='{"0": "Hey", "1": " hello", "2": " hi", "3": " whats up"}', category=category_obj)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()
        user = Profile.objects.create(user_id="123")
        Data.objects.create(user=user, variable="last_identified_intent_name",
                            value=json.dumps("Hi"), is_cache=True)
        self.assertEqual(get_intent_category_name(
            None, None, None, bot_obj.pk, None), "")
        self.assertEqual(get_intent_category_name(
            tree_obj, None, None, bot_obj.pk, user), "testcategory")

    """
    function tested: save_form_assist_analytics
    input params:
        code: It will save the details of the lead who is assisted by form
        parameter: channel_params (is_form_assist), bot_id, user, form_assist_id
    """

    def test_save_form_assist_analytics(self):
        logger.info("Testing of save_form_assist_analytics is going on.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of save_form_assist_analytics is going on.\n")

        channel_params = {"is_form_assist": False}
        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)
        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple", is_form_assist_enabled=True)
        bot_obj.users.add(user_obj)
        bot_obj.save()
        easychat_bot_user = EasyChatBotUser(
            bot_obj=bot_obj, channl_name="Web", src="en", bot_id=bot_obj.pk)
        lang_obj = Language.objects.create(lang="en")
        easychat_bot_user.selected_language = lang_obj
        intent_obj = create_default_livechat_trigger_intent(bot_obj)
        user_obj = Profile.objects.create(user_id="123")

        form_assist_id = FormAssist.objects.create(
            tag_id="test", intent=intent_obj, bot=bot_obj)

        save_form_assist_analytics(
            channel_params, easychat_bot_user, user_obj, form_assist_id.pk)

        data_user_obj = Data.objects.filter(user="123")

        assert len(data_user_obj) == 0

        channel_params = {"is_form_assist": True}

        save_form_assist_analytics(
            channel_params, easychat_bot_user, user_obj, form_assist_id.pk)
        data_user_obj = Data.objects.all()[0]

        form_assist_analytics_obj_pk = FormAssistAnalytics.objects.all()[0].pk

        self.assertEqual(int(json.loads(data_user_obj.get_value())),
                         form_assist_analytics_obj_pk)

    """
    function tested: create_default_intents
    input params:
        code: It will create the defaults intents of the newly created bot
        parameter: bot_id(mandatory)
    """

    def test_create_default_intents(self):
        logger.info("Testing of create_default_intents is going on.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of create_default_intents is going on.\n")

        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)
        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.save()
        create_default_intents(bot_obj.pk)

        intent_objs_list = list(Intent.objects.all().values("name"))

        expected_intent_name_list = []
        for intent in default_intent_contants:
            expected_intent_name_list.append({"name": intent["intent_name"]})

        self.assertEqual(intent_objs_list, expected_intent_name_list)

    """
    function tested: create_default_livechat_trigger_intent
    input params:
        bot_obj: Bot object in which the livechat default intent should be added.
    Output:
        rteurns intent object.
    If there is already defalt livechat intent then it only mark it is_deleted false otherwise creates new one.
    """

    def test_create_default_livechat_trigger_intent(self):
        logger.info(
            "Testing of create_default_livechat_trigger_intent is going on.", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of create_default_livechat_trigger_intent is going on.\n")

        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)
        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.save()

        intent_obj = create_default_livechat_trigger_intent(bot_obj)

        assert intent_obj.name == "Chat with an expert"

        bot_response = json.loads(intent_obj.tree.response.modes)
        assert bot_response["is_livechat"] == "true"

        bot_obj.livechat_default_intent = intent_obj
        bot_obj.save()

        intent_obj = create_default_livechat_trigger_intent(bot_obj)
        assert intent_obj.is_deleted == False

    """
    function tested: is_it_livechat_manager
    input params:
        username: Username of easychat User object.
    Output:
        rteurns True if user is Livechat manager, False otherwise.
    """

    def test_is_it_livechat_manager(self):
        logger.info("Testing of is_it_livechat_manager is going on.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of is_it_livechat_manager is going on.\n")

        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)
        user_obj1 = User.objects.create(
            username="test12345", password="test12345", role=BOT_BUILDER_ROLE, status="1", is_online=True)

        livechat_user1 = LiveChatUser.objects.create(status="1")
        livechat_user1.user = user_obj

        bot_obj = Bot.objects.create(name="Testing", created_by=user_obj)

        livechat_user2 = LiveChatUser.objects.create(status="2")
        livechat_user2.user = user_obj1
        livechat_user2.save()

        assert is_it_livechat_manager("Easychat", bot_obj.pk) == False
        assert is_it_livechat_manager(
            livechat_user1.user.username, bot_obj.pk) == True
        assert is_it_livechat_manager(
            livechat_user2.user.username, bot_obj.pk) == False

    """
    function tested: remove_default_livechat_trigger_intent
    input params:
        bot_obj: Bot object from which the livechat default intent should be removed.
    Output:
        rteurns none
    Mark is_deleted to True of defalt livechat intent
    """

    def test_remove_default_livechat_trigger_intent(self):
        logger.info(
            "Testing of remove_default_livechat_trigger_intent is going on.", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of remove_default_livechat_trigger_intent is going on.\n")

        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)
        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.save()

        intent_obj = create_default_livechat_trigger_intent(bot_obj)
        bot_obj.livechat_default_intent = intent_obj
        bot_obj.save()
        remove_default_livechat_trigger_intent(bot_obj)

        bot_obj = Bot.objects.all()[0]
        intent_obj = bot_obj.livechat_default_intent

        assert intent_obj.is_deleted == True

    """
    function tested: manage_default_livechat_intent
    input params:
        is_livechat_enabled: True/False
        bot_obj: Bot object in which the livechat default intent should be added/removed.
    Output:
        rteurns None just perform the required operation

    If is_livechat_enabled True then it go for create_default_livechat_trigger_intent otherwise remove_default_livechat_trigger_intent
    """

    def test_manage_default_livechat_intent(self):
        logger.info("Testing of manage_default_livechat_intent is going on.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of manage_default_livechat_intent is going on.\n")

        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)
        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.save()

        manage_default_livechat_intent(False, bot_obj)
        bot_obj = Bot.objects.all()[0]
        assert bot_obj.livechat_default_intent == None

        manage_default_livechat_intent(True, bot_obj)

        bot_obj = Bot.objects.all()[0]
        assert bot_obj.livechat_default_intent != None
        intent_obj = bot_obj.livechat_default_intent

        assert intent_obj.is_deleted == False

        manage_default_livechat_intent(False, bot_obj)

        bot_obj = Bot.objects.all()[0]
        assert bot_obj.livechat_default_intent != None
        intent_obj = bot_obj.livechat_default_intent

        assert intent_obj.is_deleted == True


class UtilsSmallMethodsNoModels(TestCase):

    def setUp(self):
        Config.objects.create()
        logger.info(
            "Setting up test environment for small functions of utils.py that don't have models", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        pass

    def test_remo_html_from_string(self):
        print("\n\nTesting remo_html_from_string function")
        input_strings = ["<html>htmlcontent</html>",
                         """<div class="stylish" style="display: none;">htmlindiv</div>""", ""]
        expected_strings = ["htmlcontent", "htmlindiv", ""]
        output_strings = []
        for test_string in input_strings:
            validation_obj = EasyChatInputValidation()

            output = validation_obj.remo_html_from_string(test_string)
            output_strings.append(output)

        self.assertEqual(output_strings, expected_strings)

    def test_remo_special_tag_from_string(self):
        print("\n\nTesting remo_special_tag_from_string")
        input_strings = ["html+content", """|html|=|-|in+div""", ""]
        expected_strings = ["html+content", "html-in+div", ""]
        output_strings = []

        validation_obj = EasyChatInputValidation()

        for test_string in input_strings:
            output = validation_obj.remo_special_tag_from_string(test_string)
            output_strings.append(output)

        self.assertEqual(output_strings, expected_strings)

    def test_remove_hexabyte_character(self):
        print("\n\nTesting remove_hexabyte_character")
        input_strings = ["àa testé stringüß",
                         "Ã string çöntäining nön äsçii çhäräçters", "normal text"]
        expected_strings = [
            " a test  string  ", "  string   nt ining n n  s ii  h r  ters", "normal text"]
        output_strings = []

        validation_obj = EasyChatInputValidation()

        for test_string in input_strings:
            output = validation_obj.remove_hexabyte_character(test_string)
            output_strings.append(output)

        self.assertEqual(output_strings, expected_strings)

    def test_is_similar_words_format_correct(self):
        print("\n\nTesting is_similar_words_format_correct")

        input = []
        output = is_similar_words_format_correct(input)
        self.assertEqual(output, False)

        input = ['cc', 'card']
        output = is_similar_words_format_correct(input)
        self.assertEqual(output, True)

        input = ['cc', 'credit card']
        output = is_similar_words_format_correct(input)
        self.assertEqual(output, False)

    def test_get_correct_words(self):
        print("\n\nTesting get_correct_words")

        input = ['blance']
        output = get_correct_words(input, "", "", "", None)
        self.assertEqual(output, {'balance', 'b', 'lance'})

        input = ['what', 'fullkyc']
        output = get_correct_words(input, "", "", "", None)
        self.assertEqual(output, {'what', 'fully', 'full', 'kyc'})


class UtilsSmallMethodsWithModels(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        self.factory = RequestFactory()
        self.user = User.objects.create(
            role="1", status="1", username="test1", password="pswdtest1")
        LiveChatUser.objects.create(user=self.user)
        Agent.objects.create(user=self.user)
        test_tree = Tree.objects.create(name="TestIntentsTree")
        Intent.objects.create(name="TestIntent", tree=test_tree)
        Intent.objects.create(name="message1")
        Intent.objects.create(name="message2")
        Intent.objects.create(name="message3")

        # Pre-Processor setup
        pre_processor = Processor.objects.create(
            function="""def f():\n    json_data = {}\n    json_data["status_code"]=200\n    json_data["status_message"] = {/x/}\n    json_data["data"] = { "computed_value" : 2*{/x/} }\n    return json_data""")
        profile_user = Profile.objects.create(user_id="456245645")
        Data.objects.create(user=profile_user, variable="x",
                            value=5, is_cache=True)
        Tree.objects.create(name="TestTreeWithPreProc",
                            pre_processor=pre_processor)

        # API Tree setup
        api_caller = """def f():\n    response = {}\n    response["status_code"]=200\n    response["status_message"] = {/y/}\n    response["data"] = { "computed_value" : {/y/}*{/y/} }\n    return response"""
        profile_user = Profile.objects.create(user_id="542654465")
        Data.objects.create(user=profile_user, variable="y",
                            value=15, is_cache=True)
        api_tree = ApiTree.objects.create(
            name="TestTreeWithAPICaller", api_caller=api_caller)
        Tree.objects.create(name="TestTreeWithAPICaller", api_tree=api_tree)

        # Setting up Authetication object for checking user authetication
        Authentication.objects.create(name="Applicant")

        # Flow setup for is_flow ended
        user_tree1 = Tree.objects.create(name="UserTreeWithoutChildren")
        Profile.objects.create(user_id="2545682", tree=user_tree1)
        child_tree = Tree.objects.create(name="RandomChildTree")
        user_tree2 = Tree.objects.create(
            name="UserTreeWithAChild").children.add(child_tree)
        Profile.objects.create(user_id="2545582", tree=user_tree2)

        # Build Bot Response setup
        test_bot = Bot.objects.create(name="UnitTestBot", is_uat=False)
        test_channel = Channel.objects.create(name="GoogleHome")
        BotChannel.objects.create(bot=test_bot, channel=test_channel, welcome_message="Hi this is a welcome message!",
                                  initial_messages='{"items":["2", "3", "4"]}')

        # User Profile and Data model for is_feedback_required
        user_profile = Profile.objects.create(user_id="654622594")
        Data.objects.create(user=user_profile,
                            variable="is_feedback_required", value="true")
        user_profile2 = Profile.objects.create(user_id="465625264")
        Data.objects.create(user=user_profile2,
                            variable="is_feedback_required", value="false")

    def test_apply_filter_api_analytics(self):
        print("\n\nTesting apply_filter_api_analytics function")

        import datetime
        try:
            user_profile = Profile.objects.all()[0]
        except Exception:
            user_profile = Profile.objects.create(user_id="2545582")
        try:
            test_bot = Bot.objects.all()[0]
        except Exception:
            test_bot = Bot.objects.create(
                name="TestBot", is_active=True, is_deleted=False)

        APIElapsedTime.objects.create(
            user=user_profile, bot=test_bot, api_name="Test")
        APIElapsedTime.objects.create(
            user=user_profile, bot=test_bot, api_name="Test1")
        APIElapsedTime.objects.create(
            user=user_profile, bot=test_bot, api_name="Test2", api_status="Failed")
        APIElapsedTime.objects.create(
            user=user_profile, bot=test_bot, api_name="Test3")
        APIElapsedTime.objects.create(
            user=user_profile, bot=test_bot, api_name="Test4")
        datetime_start = datetime.datetime.now() - datetime.timedelta(days=3)
        datetime_end = datetime.datetime.now()

        correct_list = apply_filter_api_analytics(
            None, None, None, datetime_start, datetime_end, "", APIElapsedTime)
        self.assertEqual(0, len(correct_list))

        correct_list = apply_filter_api_analytics(
            test_bot, None, None, datetime_start, datetime_end, "", APIElapsedTime)
        self.assertEqual(5, len(correct_list))

        correct_list = apply_filter_api_analytics(
            test_bot, None, "Passed", datetime_start, datetime_end, "", APIElapsedTime)
        self.assertEqual(4, len(correct_list))

        correct_list = apply_filter_api_analytics(
            test_bot, None, "Failed", datetime_start, datetime_end, "", APIElapsedTime)
        self.assertEqual(1, len(correct_list))

        correct_list = apply_filter_api_analytics(
            test_bot, None, "Failed", datetime_start, datetime_start, "", APIElapsedTime)
        self.assertEqual(0, len(correct_list))

        correct_list = apply_filter_api_analytics(
            test_bot, "Test2", None, datetime_start, datetime_end, "", APIElapsedTime)
        self.assertEqual(1, len(correct_list))

        correct_list = apply_filter_api_analytics(
            test_bot, "Test2", "Passed", datetime_start, datetime_end, "", APIElapsedTime)
        self.assertEqual(0, len(correct_list))

        correct_list = apply_filter_api_analytics(
            test_bot, "Test2", "Failed", datetime_start, datetime_end, "", APIElapsedTime)
        self.assertEqual(1, len(correct_list))

    def test_add_changes(self):
        print("\n\nTesting add_changes function")

        change_data = []
        expected_list = []
        correct_list = add_changes(change_data, "a", "a", "testing")
        self.assertEqual(expected_list, correct_list)
        change_data = []
        expected_list = [{"heading": "testing",
                          "old_data": "a", "new_data": "b"}]
        correct_list = add_changes(change_data, "a", "b", "testing")
        self.assertEqual(expected_list, correct_list)

    def test_get_message_list_using_pk(self):
        print("\n\nTesting get_message_list_using_pk function")

        intent_pk_list = []
        expected_list = []

        correct_list = get_message_list_using_pk(intent_pk_list)

        self.assertEqual(expected_list, correct_list)

        intent_pk_list = ["1234", "12345"]
        expected_list = []

        correct_list = get_message_list_using_pk(intent_pk_list)

        self.assertEqual(expected_list, correct_list)

        intent_pk_list = ["1", "2", "3"]
        expected_list = ["TestIntent", "message1", "message2"]

        correct_list = get_message_list_using_pk(intent_pk_list)

        self.assertEqual(expected_list, correct_list)

    def test_get_message_list_and_icon_name(self):
        print("\n\nTesting get_message_list_and_icon_name function")

        sticky_menu_list = []
        expected_list = []

        correct_list = get_message_list_and_icon_name(sticky_menu_list, Intent)

        self.assertEqual(expected_list, correct_list)

        sticky_menu_list = [["1234", "fa-address"], ["12345", "fa-address"]]
        expected_list = []

        correct_list = get_message_list_and_icon_name(sticky_menu_list, Intent)

        self.assertEqual(expected_list, correct_list)

        sticky_menu_list = [["1", "fa-address-book"],
                            ["2", "fa-id-card"], ["3", "fa-keyboard-o"]]
        expected_list = [["TestIntent", "fa-address-book", 1],
                         ["message1", "fa-id-card", 2], ["message2", "fa-keyboard-o", 3]]

        correct_list = get_message_list_and_icon_name(sticky_menu_list, Intent)

        self.assertEqual(expected_list, correct_list)

    def test_is_allowed(self):

        print("\n\nTesting is_allowed function")
        request = self.factory.post(
            '/chat/login/', {"username": "test1", "password": "pswdtest1"})
        request.user = self.user
        allowed_list = ["1", "2", "3"]
        bool_response = is_allowed(request, allowed_list)
        self.assertEqual(bool_response, True)

    def test_is_livechat_access_allowed(self):

        print("\n\nTesting is_livechat_access_allowed function")
        request = self.factory.post(
            '/chat/login/', {"username": "test1", "password": "pswdtest1"})
        request.user = self.user

        bool_response = is_livechat_access_allowed(request, BotInfo)
        self.assertEqual(bool_response, False)

    def test_is_tms_access_allowed(self):

        print("\n\nTesting is_tms_access_allowed")
        request = self.factory.post(
            '/chat/login/', {"username": "test1", "password": "pswdtest1"})
        request.user = self.user
        bot_obj = Bot.objects.all()[0]
        tms_user_obj = Agent.objects.get(user=self.user)
        tms_user_obj.bots.add(bot_obj)
        tms_user_obj.save()
        bool_response = is_tms_access_allowed(request, Agent)
        self.assertEqual(bool_response, True)

    def test_set_user(self):

        print("\n\nTesting set_user")
        input_user_id = ['']
        unexpected_responses = ['']
        executed_set_user = []
        for query in input_user_id:
            corrected = set_user(query, 'testing_message', None, None, None)
            executed_set_user.append(corrected)

        self.assertNotEqual(unexpected_responses, executed_set_user)

    def test_get_intent_name(self):

        print("\n\nTesting get_intent_name")
        tree = Tree.objects.get(name="TestIntentsTree")
        intent_name = "TestIntent"
        intent_obj = Intent.objects.get(name="TestIntent")
        bot_obj = Bot.objects.get(name="UnitTestBot")
        intent_obj.bots.add(bot_obj)
        intent_obj.save()
        identified_intent = get_intent_name(tree, None, None, bot_obj.pk, None)
        self.assertEqual(intent_name, identified_intent)

    def test_replace_data_values(self):

        print("\n\nTesting replace_data_values function")
        user = Profile.objects.get(user_id="542654465")
        sentence = Tree.objects.get(
            name="TestTreeWithAPICaller").api_tree.api_caller
        replaced_sentence = replace_data_values(
            user, sentence, None, None, None)
        expected_replaced_sentence = """def f():\n    response = {}\n    response["status_code"]=200\n    response["status_message"] = 15\n    response["data"] = { "computed_value" : 15*15 }\n    return response"""
        self.assertEqual(replaced_sentence, expected_replaced_sentence)

    def test_save_data(self):

        print("\n\nTesting save_data")
        user = Profile.objects.create(user_id="455628855")
        json_data = {}
        json_data["create_this"] = "default value"
        print("\n\nTesting if save_data creates a new data object")
        save_data(user, json_data, None, None, None, False)
        saved_value = json.loads(Data.objects.get(
            user=user, variable="create_this").value)
        self.assertEqual("default value", saved_value)
        print("\n\nData object created: ", Data.objects.get(
            user=user, variable="create_this").value)
        print("\n\nTesting if save_data updates an existing data object")
        json_data["create_this"] = "updated value"
        save_data(user, json_data, None, None, None, False)
        updated_value = json.loads(Data.objects.get(
            user=user, variable="create_this").value)
        self.assertEqual("updated value", updated_value)
        print("\n\nData object created: ", Data.objects.get(
            user=user, variable="create_this").value)

    def test_check_user_auth(self):

        print("\n\nTesting check_user_auth function")
        user = Profile.objects.create(user_id="4461005865")
        bot_obj = Bot.objects.create(name="TestBot")
        Channel.objects.create(name="Web")
        response = {}
        response["AUTHENTICATION"] = {
            "status": True,
            "type": "Applicant",
            "user_params": {
                "ApplicantID": "1234567890"
            }
        }
        response_json_data = response
        print("\n\nTesting when UserAuthentication object does not exist for the user")
        check_user_auth(user, response_json_data, None, "Web", bot_obj.pk)
        saved_data = json.loads(Data.objects.get(
            user=user, variable="ApplicantID").get_value())
        self.assertEqual("1234567890", saved_data)
        print("\n\nUserAuthentication created: ", UserAuthentication.objects.get(
            user=user), " ", UserAuthentication.objects.get(user=user).start_time)
        print("\n\nTesting when UserAuthentication object does not exist for the user")
        check_user_auth(user, response_json_data, None, "Web", bot_obj.pk)
        saved_data = json.loads(Data.objects.get(
            user=user, variable="ApplicantID").get_value())
        self.assertEqual("1234567890", saved_data)
        print("\n\nUserAuthentication updated: ", UserAuthentication.objects.get(
            user=user), " ", UserAuthentication.objects.get(user=user).start_time)

    def test_process_api(self):

        print("\n\nTesting process_api")
        tree1 = None
        tree2 = Tree.objects.get(name="TestIntentsTree")
        tree3 = Tree.objects.get(name="TestTreeWithAPICaller")

        user = User.objects.get(username="test1")
        api_tree_responses = []
        for tree in [tree1, tree2]:
            response = process_api(user, tree, None, None, None)
            api_tree_responses.append(response)
        user_profile = Profile.objects.get(user_id="542654465")
        process_api(user_profile, tree3, None, None, None)
        saved_data = int(Data.objects.get(
            user=user_profile, variable="computed_value").value)
        api_tree_responses.append(saved_data)
        self.assertEqual([{}, {}, 225], api_tree_responses)

    def test_is_flow_ended(self):

        print("\n\nTesting is_flow_ended function")
        print("\n\nTesting for tree without children")
        user = Profile.objects.get(user_id="2545682")
        tree_without_children = user.tree
        bool_response = is_flow_ended(
            user, tree_without_children, None, None, None)
        self.assertEqual(bool_response, True)
        print("\n\nTesting for tree with children")
        user = Profile.objects.get(user_id="2545582")
        tree_with_children = user.tree
        bool_response = is_flow_ended(
            user, tree_with_children, None, None, None)
        self.assertEqual(bool_response, False)

    def test_build_android_response(self):

        print("\n\nTesting build_android_response function")
        print("\n\nTest will be written after execute_query")

    def test_build_google_home_welcome_response(self):

        print("\n\nTesting build_google_home_welcome_response function")
        webhook_response = {
            "fulfillmentText": "Hi this is a welcome message!",
            "fulfillmentMessages": [],
            "source": "www.google.com",
            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse":
                    {
                        "items":
                        [
                            {
                                "simpleResponse": {
                                    "textToSpeech": "Hi this is a welcome message!Please say 1 for message1 . Please say 2 for message2 . Please say 3 for message3 .",
                                                    "displayText": "Hi this is a welcome message!"
                                }
                            },
                        ],
                    },
                    "systemIntent":
                    {
                        "intent": "actions.intent.OPTION",
                        "data":
                        {
                            "@type": "type.googleapis.com/google.actions.v2.OptionValueSpec",
                            "listSelect":
                            {
                                "items":
                                [{
                                    "optionInfo": {
                                        "key": "message1"
                                    },
                                    "title": "message1"
                                },
                                    {
                                    "optionInfo": {
                                        "key": "message2"
                                    },
                                    "title": "message2"
                                },
                                    {
                                    "optionInfo": {
                                        "key": "message3"
                                    },
                                    "title": "message3"
                                }]
                            }
                        }
                    }
                },
                "facebook": {
                    "text": "Hello, Facebook!"
                },
                "slack": {
                    "text": "Hello, Slack."
                }
            }
        }

        bot_obj = Bot.objects.get(name="UnitTestBot")

        webhook_response_dict = build_google_home_welcome_response(
            bot_obj.pk, bot_obj.name)
        self.maxDiff = None
        self.assertEqual(webhook_response, webhook_response_dict)

    # def test_build_google_home_response(self):

    #     print("\n\nTesting build_google_home_response function")

    #     user = User.objects.create(username="TestUser", password="645461210")
    #     Profile.objects.create(
    #         user_id="ABwppHEHTvXeRvhFfkV6j9I9F5O7sED0LhrXpwBtuvrVlON5H-vI6FRVVfELXQPYgGD5Whi2uvZh74R6R2l3vuDdKQ")
    #     bot_obj = Bot.objects.create(
    #         name="TestBot", is_active=True, is_deleted=False)
    #     bot_obj.users.add(user)
    #     bot_id = bot_obj.pk
    #     bot_name = bot_obj.slug
    #     bot_obj.intent_score_threshold = 0.1
    #     bot_obj.save()
    #     try:
    #         Config.objects.all().delete()
    #     except Exception:
    #         pass

    #     Config.objects.create()

    #     channel = Channel.objects.get(name="GoogleHome")
    #     intent_obj = Intent.objects.create(
    #         name="TestIntent", training_data=json.dumps({"1": "Am I signed in?"}))
    #     intent_obj.channels.add(channel)
    #     intent_obj.bots.add(bot_obj)
    #     intent_obj.is_authentication_required = True
    #     sentence = {"items": [{"text_response": "Looks like you need to are signed in", "speech_response": "Looks like you need to are signed in", "hinglish_response": "",
    #                            "text_reprompt_response": "Looks like you need to are signed in", "speech_reprompt_response": "Looks like you need to are signed in", "tooltip_response": ""}]}
    #     bot_response = BotResponse.objects.create(
    #         sentence=json.dumps(sentence))
    #     intent_obj.tree = Tree.objects.create(
    #         name="TestTreeForHandlingResponse", response=bot_response)
    #     test_authentication_tree = Tree.objects.create(
    #         name="TestAuthenticationTree")
    #     try:
    #         Authentication.objects.all().delete()
    #     except Exception:
    #         pass

    #     test_authentication_object = Authentication.objects.create(
    #         name="TestAuthentication", tree=test_authentication_tree, auth_time=300)

    #     intent_obj.auth_type = test_authentication_object
    #     intent_obj.save()

    #     request_welcome = {
    #         "queryResult": {
    #             "queryText": "GOOGLE_ASSISTANT_WELCOME",
    #             "fulfillmentMessages": [
    #                 {
    #                     "text": {
    #                         "text": [
    #                             ""
    #                         ]
    #                     }
    #                 }
    #             ],
    #             "allRequiredParamsPresent": "true",
    #             "parameters": {

    #             },
    #             "languageCode": "en",
    #             "intentDetectionConfidence": 1.0,
    #             "intent": {
    #                 "isFallback": "true",
    #                 "displayName": "Default Fallback Intent"
    #             },
    #             "action": "input.unknown"
    #         },
    #         "originalDetectIntentRequest": {
    #             "source": "google",
    #             "version": "2",
    #             "payload": {
    #                 "conversation": {
    #                     "conversationId": "ABwppHEHTvXeRvhFfkV6j9I9F5O7sED0LhrXpwBtuvrVlON5H-vI6FRVVfELXQPYgGD5Whi2uvZh74R6R2l3vuDdKQ",
    #                     "type": "ACTIVE",
    #                     "conversationToken": "[]"
    #                 },
    #                 "availableSurfaces": [
    #                     {
    #                         "capabilities": [
    #                             {
    #                                 "name": "actions.capability.AUDIO_OUTPUT"
    #                             },
    #                             {
    #                                 "name": "actions.capability.SCREEN_OUTPUT"
    #                             },
    #                             {
    #                                 "name": "actions.capability.WEB_BROWSER"
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 "user": {
    #                     "locale": "en-US",
    #                     "userVerificationStatus": "VERIFIED",
    #                     "accessToken": "kGwJeLw0vDxascyXA4ZH7XFGgOyiif"
    #                 },
    #                 "surface": {
    #                     "capabilities": [
    #                         {
    #                             "name": "actions.capability.ACCOUNT_LINKING"
    #                         },
    #                         {
    #                             "name": "actions.capability.SCREEN_OUTPUT"
    #                         },
    #                         {
    #                             "name": "actions.capability.WEB_BROWSER"
    #                         },
    #                         {
    #                             "name": "actions.capability.AUDIO_OUTPUT"
    #                         },
    #                         {
    #                             "name": "actions.capability.MEDIA_RESPONSE_AUDIO"
    #                         }
    #                     ]
    #                 },
    #                 "inputs": [
    #                     {
    #                         "rawInputs": [
    #                             {
    #                                 "query": ""
    #                             }
    #                         ],
    #                         "intent": "actions.intent.OPTION",
    #                         "arguments": [
    #                             {
    #                                 "name": "OPTION",
    #                                 "textValue": ""
    #                             },
    #                             {
    #                                 "rawText": "",
    #                                 "name": "text",
    #                                 "textValue": ""
    #                             }
    #                         ]
    #                     }
    #                 ]
    #             }
    #         },
    #         "session": "projects/dqcuiw/agent/environments/__aog-4/users/-/sessions/",
    #         "responseId": "d70f95d7-1083-477e-bbe2-601e18fe0adf-426bc00a"
    #     }

    #     print("\n\nTesting a scenario where user is welcomed")

    #     self.assertEqual(build_google_home_welcome_response(
    #         bot_id, bot_name), build_google_home_response(request_welcome, bot_id, bot_name))

    #     try:
    #         AccessToken.objects.all().delete()
    #     except Exception:
    #         pass

    #     request_ask_signin = {
    #         "queryResult": {
    #             "fulfillmentMessages": [
    #                 {
    #                     "text": {
    #                         "text": [
    #                             ""
    #                         ]
    #                     }
    #                 }
    #             ],
    #             "allRequiredParamsPresent": "true",
    #             "parameters": {

    #             },
    #             "languageCode": "en",
    #             "intentDetectionConfidence": 1.0,
    #             "intent": {
    #                 "isFallback": "true",
    #                 "displayName": "Default Fallback Intent"
    #             },
    #             "action": "input.unknown"
    #         },
    #         "originalDetectIntentRequest": {
    #             "source": "google",
    #             "version": "2",
    #             "payload": {
    #                 "conversation": {
    #                     "conversationId": "ABwppHEHTvXeRvhFfkV6j9I9F5O7sED0LhrXpwBtuvrVlON5H-vI6FRVVfELXQPYgGD5Whi2uvZh74R6R2l3vuDdKQ",
    #                     "type": "ACTIVE",
    #                     "conversationToken": "[]"
    #                 },
    #                 "availableSurfaces": [
    #                     {
    #                         "capabilities": [
    #                             {
    #                                 "name": "actions.capability.AUDIO_OUTPUT"
    #                             },
    #                             {
    #                                 "name": "actions.capability.SCREEN_OUTPUT"
    #                             },
    #                             {
    #                                 "name": "actions.capability.WEB_BROWSER"
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 "user": {
    #                     "locale": "en-US",
    #                     "userVerificationStatus": "VERIFIED",
    #                     "accessToken": "kGwJeLw0vDxascyXA4ZH7XFGgOyiif"
    #                 },
    #                 "surface": {
    #                     "capabilities": [
    #                         {
    #                             "name": "actions.capability.ACCOUNT_LINKING"
    #                         },
    #                         {
    #                             "name": "actions.capability.SCREEN_OUTPUT"
    #                         },
    #                         {
    #                             "name": "actions.capability.WEB_BROWSER"
    #                         },
    #                         {
    #                             "name": "actions.capability.AUDIO_OUTPUT"
    #                         },
    #                         {
    #                             "name": "actions.capability.MEDIA_RESPONSE_AUDIO"
    #                         }
    #                     ]
    #                 },
    #                 "inputs": [
    #                     {
    #                         "rawInputs": [
    #                             {
    #                                 "query": "Am I signed in?"
    #                             }
    #                         ],
    #                         "intent": "actions.intent.OPTION",
    #                         "arguments": [
    #                             {
    #                                 "name": "OPTION",
    #                                 "textValue": ""
    #                             },
    #                             {
    #                                 "rawText": "",
    #                                 "name": "text",
    #                                 "textValue": ""
    #                             }
    #                         ]
    #                     }
    #                 ]
    #             }
    #         },
    #         "session": "projects/agent/environments/__aog-4/users/-/sessions/ABwppHEHTvXeRvhFfkV6j9I9F5O7sED0LhrXpwBtuvrVlON5H-vI6FRVVfELXQPYgGD5Whi2uvZh74R6R2l3vuDdKQ",
    #         "responseId": "d70f95d7-1083-477e-bbe2-601e18fe0adf-426bc00a"
    #     }

    #     print("\n\nTesting a scenario where user is asked to login")

    #     SIGNIN_EXPECTED_RESPONSE = {'fulfillmentText': '', 'fulfillmentMessages': [], 'source': 'www.google.com', 'payload': {'google': {'expectUserResponse': True, 'richResponse': {'items': [{'simpleResponse': {
    #         'textToSpeech': 'To use this service, please link your account', 'displayText': 'To use this service, please link your account'}}]}, 'systemIntent': {'intent': 'actions.intent.SIGN_IN', 'data': {'@type': 'type.googleapis.com/google.actions.v2.SignInValueSpec'}}}}}
    #     self.assertEqual(SIGNIN_EXPECTED_RESPONSE, build_google_home_response(
    #         request_ask_signin, bot_id, bot_name))
    #     print("\n\nTesting a scenario where authentication is not mandatory or user is authenticated")

    #     intent_obj.is_authentication_required = True
    #     intent_obj.save()

    #     request_text_speech_response = {
    #         "queryResult": {
    #             "fulfillmentMessages": [
    #                 {
    #                     "text": {
    #                         "text": [
    #                             ""
    #                         ]
    #                     }
    #                 }
    #             ],
    #             "allRequiredParamsPresent": "true",
    #             "parameters": {

    #             },
    #             "languageCode": "en",
    #             "intentDetectionConfidence": 1.0,
    #             "intent": {
    #                 "isFallback": "true",
    #                 "displayName": "Default Fallback Intent"
    #             },
    #             "action": "input.unknown"
    #         },
    #         "originalDetectIntentRequest": {
    #             "source": "google",
    #             "version": "2",
    #             "payload": {
    #                 "conversation": {
    #                     "conversationId": "ABwppHEHTvXeRvhFfkV6j9I9F5O7sED0LhrXpwBtuvrVlON5H-vI6FRVVfELXQPYgGD5Whi2uvZh74R6R2l3vuDdKQ",
    #                     "type": "ACTIVE",
    #                     "conversationToken": "[]"
    #                 },
    #                 "availableSurfaces": [
    #                     {
    #                         "capabilities": [
    #                             {
    #                                 "name": "actions.capability.AUDIO_OUTPUT"
    #                             },
    #                             {
    #                                 "name": "actions.capability.SCREEN_OUTPUT"
    #                             },
    #                             {
    #                                 "name": "actions.capability.WEB_BROWSER"
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 "user": {
    #                     "locale": "en-US",
    #                     "userVerificationStatus": "VERIFIED",
    #                     "accessToken": "kGwJeLw0vDxascyXA4ZH7XFGgOyiif"
    #                 },
    #                 "surface": {
    #                     "capabilities": [
    #                         {
    #                             "name": "actions.capability.ACCOUNT_LINKING"
    #                         },
    #                         {
    #                             "name": "actions.capability.SCREEN_OUTPUT"
    #                         },
    #                         {
    #                             "name": "actions.capability.WEB_BROWSER"
    #                         },
    #                         {
    #                             "name": "actions.capability.AUDIO_OUTPUT"
    #                         },
    #                         {
    #                             "name": "actions.capability.MEDIA_RESPONSE_AUDIO"
    #                         }
    #                     ]
    #                 },
    #                 "inputs": [
    #                     {
    #                         "rawInputs": [
    #                             {
    #                                 "query": "Am I signed in?"
    #                             }
    #                         ],
    #                         "intent": "actions.intent.OPTION",
    #                         "arguments": [
    #                             {
    #                                 "name": "OPTION",
    #                                 "textValue": ""
    #                             },
    #                             {
    #                                 "rawText": "",
    #                                 "name": "text",
    #                                 "textValue": ""
    #                             }
    #                         ]
    #                     }
    #                 ]
    #             }
    #         },
    #         "session": "projects/agent/environments/__aog-4/users/-/sessions/91d8fdae-6192-4636-913b-7f5340ba530f",
    #         "responseId": "d70f95d7-1083-477e-bbe2-601e18fe0adf-426bc00a"
    #     }

    #     user_id = "91d8fdae-6192-4636-913b-7f5340ba530f"
    #     user_profile = Profile.objects.create(user_id=user_id)
    #     user_authentication_object = UserAuthentication.objects.create(
    #         user=user_profile, auth_type=test_authentication_object)
    #     user_authentication_object.user_params = json.dumps(
    #         {"AccessToken": "szdsbjbsbssdfkj"})
    #     user_authentication_object.save()
    #     Data.objects.all().delete()
    #     Data.objects.create(
    #         user=user_profile, variable="is_user_authenticated", value=json.dumps("true"))
    #     EXPECTED_TEXT_SPEECH_RESPONSE = {'fulfillmentText': 'Looks like you need to are signed in', 'fulfillmentMessages': [], 'source': 'www.google.com', 'payload': {'google': {'expectUserResponse': True, 'richResponse': {
    #         'items': [{'simpleResponse': {'textToSpeech': 'Looks like you need to are signed in', 'displayText': 'Looks like you need to are signed in'}}]}}, 'facebook': {'text': 'Hello, Facebook!'}, 'slack': {'text': 'Hello, Slack.'}}}
    #     self.assertEqual(EXPECTED_TEXT_SPEECH_RESPONSE, build_google_home_response(
    #         request_text_speech_response, bot_id, bot_name))

    #     print("\n\nTesting a scenario where bot response has a table, image and a video ")

    #     tree_obj = Tree.objects.get(name="TestTreeForHandlingResponse")
    #     tree_obj.response.table = json.dumps({"items": [[1, 2, 3], [2, 3, 4]]})
    #     tree_obj.response.images = json.dumps(
    #         {"items": ["https://allincall.in/static/img/logo_icon.png"]})
    #     tree_obj.response.videos = json.dumps(
    #         {"items": ["https://youtu.be/sz0GF8sg1Ww"]})
    #     tree_obj.response.save()
    #     tree_obj.save()

    #     EXPECTED_TABLE_RESPONSE = {'fulfillmentText': 'Looks like you need to are signed in', 'fulfillmentMessages': [], 'source': 'www.google.com', 'payload': {'google': {'expectUserResponse': True, 'richResponse': {'items': [{'simpleResponse': {'textToSpeech': 'Looks like you need to are signed in', 'displayText': 'Looks like you need to are signed in'}}, {'tableCard': {'rows': [{'cells': [{'text': 2}, {'text': 3}, {
    #         'text': 4}], 'dividerAfter': True}], 'columnProperties': [{'header': 1}, {'header': 2}, {'header': 3}]}}, {'basicCard': {'title': '', 'image': {'url': 'https://allincall.in/static/img/logo_icon.png', 'accessibilityText': ''}, 'imageDisplayOptions': 'CROPPED', 'buttons': [{'title': 'Click here', 'openUrlAction': {'url': 'https://youtu.be/sz0GF8sg1Ww'}}]}}]}}, 'facebook': {'text': 'Hello, Facebook!'}, 'slack': {'text': 'Hello, Slack.'}}}

    #     self.assertEqual(EXPECTED_TABLE_RESPONSE, build_google_home_response(
    #         request_text_speech_response, bot_id, bot_name))

    #     print("\n\nTesting a scenario where the user needs to provide location details to continue")
    #     request_ask_location_response = {
    #         "queryResult": {
    #             "fulfillmentMessages": [
    #                 {
    #                     "text": {
    #                         "text": [
    #                             ""
    #                         ]
    #                     }
    #                 }
    #             ],
    #             "allRequiredParamsPresent": "true",
    #             "parameters": {

    #             },
    #             "languageCode": "en",
    #             "intentDetectionConfidence": 1.0,
    #             "intent": {
    #                 "isFallback": "true",
    #                 "displayName": "Default Fallback Intent"
    #             },
    #             "action": "input.unknown"
    #         },
    #         "originalDetectIntentRequest": {
    #             "source": "google",
    #             "version": "2",
    #             "payload": {
    #                 "conversation": {
    #                     "conversationId": "ABwppHEHTvXeRvhFfkV6j9I9F5O7sED0LhrXpwBtuvrVlON5H-vI6FRVVfELXQPYgGD5Whi2uvZh74R6R2l3vuDdKQ",
    #                     "type": "ACTIVE",
    #                     "conversationToken": "[]"
    #                 },
    #                 "availableSurfaces": [
    #                     {
    #                         "capabilities": [
    #                             {
    #                                 "name": "actions.capability.AUDIO_OUTPUT"
    #                             },
    #                             {
    #                                 "name": "actions.capability.SCREEN_OUTPUT"
    #                             },
    #                             {
    #                                 "name": "actions.capability.WEB_BROWSER"
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 "user": {
    #                     "locale": "en-US",
    #                     "userVerificationStatus": "VERIFIED",
    #                     "accessToken": "kGwJeLw0vDxascyXA4ZH7XFGgOyiif"
    #                 },
    #                 "surface": {
    #                     "capabilities": [
    #                         {
    #                             "name": "actions.capability.ACCOUNT_LINKING"
    #                         },
    #                         {
    #                             "name": "actions.capability.SCREEN_OUTPUT"
    #                         },
    #                         {
    #                             "name": "actions.capability.WEB_BROWSER"
    #                         },
    #                         {
    #                             "name": "actions.capability.AUDIO_OUTPUT"
    #                         },
    #                         {
    #                             "name": "actions.capability.MEDIA_RESPONSE_AUDIO"
    #                         }
    #                     ]
    #                 },
    #                 "inputs": [
    #                     {
    #                         "rawInputs": [
    #                             {
    #                                 "query": "Am I signed in?"
    #                             }
    #                         ],
    #                         "intent": "actions.intent.OPTION",
    #                         "arguments": [
    #                             {
    #                                 "name": "OPTION",
    #                                 "textValue": ""
    #                             },
    #                             {
    #                                 "rawText": "",
    #                                 "name": "text",
    #                                 "textValue": ""
    #                             }
    #                         ]
    #                     }
    #                 ]
    #             }
    #         },
    #         "session": "projects/agent/environments/__aog-4/users/-/sessions/91d8fdae-6192-4636-913b-7f5340ba530f",
    #         "responseId": "d70f95d7-1083-477e-bbe2-601e18fe0adf-426bc00a"
    #     }
    #     tree_obj = Tree.objects.get(name="TestTreeForHandlingResponse")
    #     modes = json.loads(tree_obj.response.modes)
    #     modes["is_location_required"] = "true"
    #     tree_obj.response.modes = json.dumps(modes)
    #     tree_obj.response.save()
    #     tree_obj.save()
    #     EXPECTED_ASK_LOCATION_RESPONSE = {'fulfillmentText': '', 'fulfillmentMessages': [], 'source': 'www.google.com', 'payload': {'google': {'expectUserResponse': True, 'systemIntent': {
    #         'intent': 'actions.intent.PERMISSION', 'data': {'@type': 'type.googleapis.com/google.actions.v2.PermissionValueSpec', 'optContext': 'Raj', 'permissions': ['DEVICE_PRECISE_LOCATION']}}}}}
    #     self.assertEqual(EXPECTED_ASK_LOCATION_RESPONSE, build_google_home_response(
    #         request_text_speech_response, bot_id, bot_name))

    def test_identify_bot(self):

        print("\n\nTesting identify_bot function")
        print("\n\nNot being called anywhere in the codebase")

    def test_is_feedback_required(self):

        print("\n\nTesting is_feedback_required function")
        user1 = Profile.objects.get(user_id="654622594")
        print("\n\nTesting without a Config object")
        self.assertEqual(False, is_feedback_required(user1, None, None, None))
        Config.objects.create(is_feedback_required="True")
        print("\n\nTesting with a Config object Data object with is_feedback_required set to 'true'")
        self.assertEqual(True, is_feedback_required(
            user1, None, None, None, True))
        user2 = Profile.objects.get(user_id="465625264")
        print("\n\nTesting with Data object with is_feedback_required set to 'false'")
        self.assertEqual(False, is_feedback_required(user2, None, None, None))
        print("\n\nTesting without a proper user passed in arguments")
        self.assertEqual(False, is_feedback_required(
            "user3", None, None, None))

    def test_is_authentication_required(self):

        print("\n\nTesting is_authentication_required function")
        print("\n\nTesting with improper user argument to Data objects")
        self.assertEqual(False, is_authentication_required(
            "user", None, None, None))
        print("\n\nCreating user Profile")
        user = Profile.objects.create(user_id="464542535645")
        Data.objects.create(
            user=user, variable="is_authentication_required", value="false")
        print("\n\nTesting with is_authentication_required for user set to 'false'")
        self.assertEqual(False, is_authentication_required(
            user, None, None, None))
        Data.objects.create(
            user=user, variable="is_authentication_required", value="true")
        print("\n\nTesting with is_authentication_required set to 'true'")
        self.assertEqual(True, is_authentication_required(
            user, None, None, None))

    def test_is_active_user_authenticated(self):

        print("\n\nTesting is_active_user_authenticated function")
        print("\n\nTesting with improper user argument to Data objects")
        self.assertEqual(False, is_active_user_authenticated(
            "user", None, None, None))
        print("\n\nCreating user Profile")
        user = Profile.objects.create(user_id="465949694")
        Data.objects.create(
            user=user, variable="is_active_user_authenticated", value="false")
        print(
            "\n\nTesting with Data object with is_active_user_authenticated set to 'false'")
        self.assertEqual(False, is_active_user_authenticated(
            user, None, None, None))
        Data.objects.create(
            user=user, variable="is_active_user_authenticated", value="true")
        print(
            "\n\nTesting with Data object with is_active_user_authenticated set to 'true'")
        self.assertEqual(False, is_active_user_authenticated(
            user, None, None, None))

    def test_is_form_assist_activated(self):

        print("\n\nTesting is_form_assist function")
        print("\n\nTesting without a Data object with is_form_assist variable")
        user = Profile.objects.create(user_id="387178878")
        self.assertEqual(False, is_form_assist_activated(
            user, None, None, None))
        print("\n\nTesting with a Data object with is_form_assist variable set to 'false'")
        Data.objects.create(
            user=user, variable="is_form_assist", value="false")
        self.assertEqual(False, is_form_assist_activated(
            user, None, None, None))
        print("\n\nTesting with a Data object with is_form_assist variable set to 'true'")
        Data.objects.create(user=user, variable="is_form_assist", value="true")
        self.assertEqual(True, is_form_assist_activated(
            user, None, None, None))

    def test_spell_checker(self):

        print("\n\nTesting spell_checker function")
        message = "I want to become a billnaire"
        expected_corrected_output = "I want to become a billionaire "
        spell_corrected_output = spell_checker(message, None, None, None, None, None)
        self.assertEqual(expected_corrected_output, spell_corrected_output)

    def test_get_last_identified_intent_name(self):

        print("\n\nTesting get_last_identified_intent_name function")
        user = Profile.objects.create(user_id="646152164")
        print(
            "\n\nTesting without any Data object with last_identified_intent_name variable")
        self.assertEqual('None', get_last_identified_intent_name(
            user, None, None, None))
        Data.objects.create(
            user=user, variable="last_identified_intent_name", value=json.dumps("TestIntent"))
        print("\n\nTesting with a Data object with last_identified_intent_name variable")
        self.assertEqual("TestIntent", get_last_identified_intent_name(
            user, None, None, None))

    def test_get_easy_search_results(self):

        print("\n\nTesting get_easy_search_results function")
        print("\n\nNot called anywhere")

    def test_build_web_response(self):

        print("\n\nTesting build_web_response function")
        print("\n\nNeeds to be completed")

    def test_build_bot_switch_response(self):

        print("\n\nTesting build_bot_switch_response function")
        print("\n\nNot called anywhere")

    def test_build_prevent_bot_switch_response(self):

        print("\n\nTesting build_prevent_bot_switch_response function")
        print("\n\nNot called anywhere")

    def test_build_error_response(self):

        print("\n\nTesting build_error_response function")
        e = "Test Error Message"
        expected_response = {
            "status_code": "500",
            "status_message": "Test Error Message",
            "user_id": "",
            "bot_id": "",
            "response": {
                "cards": [

                ],
                "images": [

                ],
                "videos": [

                ],
                "choices": [

                ],
                "recommendations": [

                ],
                "google_search_results": [

                ],
                "speech_response": {
                    "text": ""
                },
                "ssml_response": {
                    "text": ""
                },
                "text_response": {
                    "text": "Test Error Message",
                    "modes": {
                        "is_typable": "true",
                        "is_button": "true",
                        "is_slidable": "false",
                        "is_date": "false",
                        "is_dropdown": "false"
                    },
                    "modes_param": {
                        "is_slidable": {
                            "max": "",
                            "min": "",
                            "step": ""
                        }
                    }
                },
                "is_flow_ended": False,
                "is_authentication_required": False,
                "is_bot_switch": False,
                "is_user_authenticated": False
            }
        }
        received_response = build_error_response(str(e))

        self.assertEqual(expected_response, received_response)

    def test_dump_old_data(self):

        print("\n\nTesting dump_old_data function")
        print("\n\nNot called anywhere")

    def test_load_old_data(self):

        print("\n\nTesting load_old_data function")
        user = Profile.objects.create(user_id="4684610250254")
        user.previous_data = json.dumps(
            {"variable1": "One", "variable2": "Two"})
        load_old_data(user, None, None, None)
        variable1_value = Data.objects.get(
            user=user, variable="variable1").get_value()
        self.assertEqual(variable1_value, "One")
        variable2_value = Data.objects.get(
            user=user, variable="variable2").get_value()
        self.assertEqual(variable2_value, "Two")
        current_previous_data = user.previous_data
        self.assertEqual(current_previous_data, "{}")

    def test_check_terminal_tree_logic(self):
        print("\n\nTesting check_terminal_tree_logic function")
        tree = Tree.objects.create(name="TestTreeForTerminalLogic")
        previous_tree = Tree.objects.create(
            name="TestPreviousTreeForTerminalLogic")
        previous_data = json.dumps({"variable1": "One", "variable2": "Two"})
        user = Profile.objects.create(
            user_id="46762853184", tree=tree, previous_tree=previous_tree, previous_data=previous_data)
        Data.objects.create(
            user=user, variable="non_cached", value="YesNotCached")
        Data.objects.create(
            user=user, variable="yes_cached", value="YesISCached")
        check_terminal_tree_logic(user, None, None, None)
        self.assertEqual(user.tree, previous_tree)
        self.assertEqual(user.previous_tree, None)
        self.assertEqual(user.previous_data, '{}')

    def test_check_bot_switch_logic(self):

        print("\n\nTesting check_bot_switch_logic function")
        print("\n\nNot called anywhere")

    def test_execute_pipeprocessor(self):
        print("\n\nTesting execute_pipeprocessor function")
        print("\n\nTo be written after get_java_response")

    def test_get_max_limit_of_customers(self):
        print("\n\nTesting get_max_limit_of_customers function")
        print("\n\nThe dependency - LiveChatConfig model does not exist hence no test being written")

    def test_get_api_elapsed_time(self):
        print("\n\nTesting get_api_elapsed_time function")
        json_api_resp_list = ["", [], False]
        for json_api_resp in json_api_resp_list:
            self.assertEqual({}, get_api_elapsed_time(
                json_api_resp, None, None, None, None))
        json_api_resp = {}
        self.assertEqual({}, get_api_elapsed_time(
            json_api_resp, None, None, None, None))
        json_api_resp["elapsed_time"] = "This is truly assertible"
        self.assertEqual("This is truly assertible",
                         get_api_elapsed_time(json_api_resp, None, None, None, None))

    def test_small_talk_or_not(self):

        print("\n\nTesting small_talk_or_not function")
        print("\n\nNot called anywhere")

    def test_save_default_parameter_for_flow(self):

        # This function is supposed to be called from execute_query but it never really was called
        # Hence it had a small bug but was never discovered. The function requires three arguments but till now it was being passed only two
        # execute_query function is thus being modified to incorporate this
        # third argument

        print("\n\nTesting save_default_parameter_for_flow function")
        modes, modes_param = {}, {}
        modes["is_attachment_required"] = "true"
        modes_param["choosen_file_type"] = "mp3"

        response = BotResponse.objects.create(
            modes=json.dumps(modes), modes_param=json.dumps(modes_param))
        tree = Tree.objects.create(response=response)
        intent = Intent.objects.create(
            name="TestIntentForDefaultParameters", tree=tree)
        intent.is_feedback_required = True
        intent.is_authentication_required = True
        test_authentication_tree = Tree.objects.create(
            name="TestAuthenticationTree")
        test_authentication_object = Authentication.objects.create(
            name="TestAuthentication", tree=test_authentication_tree, auth_time=300)
        user = Profile.objects.create(user_id="987403165")
        user_authentication_object = UserAuthentication.objects.create(
            user=user, auth_type=test_authentication_object)
        intent.auth_type = test_authentication_object

        # Testing for a Channel that is not explicitly handled
        test_channel = Channel.objects.create(name="TestChannel")
        save_default_parameter_for_flow(intent, user, test_channel, None, None)
        is_feedback_required = Data.objects.get(
            user=user, variable="is_feedback_required").value
        is_attachment_required = Data.objects.get(
            user=user, variable="is_attachment_required").value
        choosen_file_type = json.loads(Data.objects.get(
            user=user, variable="choosen_file_type").value)
        is_authentication_required = Data.objects.get(
            user=user, variable="is_authentication_required").value
        is_user_authenticated = Data.objects.get(
            user=user, variable="is_user_authenticated").value
        last_identified_intent_name = json.loads(Data.objects.get(
            user=user, variable="last_identified_intent_name").value)
        self.assertEqual(is_feedback_required, "true")
        self.assertEqual(is_attachment_required, "true")
        self.assertEqual(choosen_file_type, "mp3")
        self.assertEqual(is_authentication_required, "true")
        self.assertEqual(is_user_authenticated, "false")
        self.assertEqual(last_identified_intent_name,
                         "TestIntentForDefaultParameters")

        # Clearing all enteries in Data model
        Data.objects.filter(user=user).delete()

        # Testing for a Channel in Web, WhatsApp or Android as they have
        # similar authetication rules
        web_channel = Channel.objects.create(name="Web")
        save_default_parameter_for_flow(intent, user, web_channel, None, None)
        is_feedback_required = Data.objects.get(
            user=user, variable="is_feedback_required").value
        is_attachment_required = Data.objects.get(
            user=user, variable="is_attachment_required").value
        choosen_file_type = json.loads(Data.objects.get(
            user=user, variable="choosen_file_type").value)
        is_authentication_required = Data.objects.get(
            user=user, variable="is_authentication_required").value
        is_user_authenticated = Data.objects.get(
            user=user, variable="is_user_authenticated").value
        last_identified_intent_name = json.loads(Data.objects.get(
            user=user, variable="last_identified_intent_name").value)
        self.assertEqual(is_feedback_required, "true")
        self.assertEqual(is_attachment_required, "true")
        self.assertEqual(choosen_file_type, "mp3")
        self.assertEqual(is_authentication_required, "true")
        self.assertEqual(is_user_authenticated, "true")
        self.assertEqual(last_identified_intent_name,
                         "TestIntentForDefaultParameters")

        # Clearing all enteries in Data model
        Data.objects.filter(user=user).delete()

        # Testing for a Channel in GoogleHome or Alexa as they have similar
        # authentication rule
        user_authentication_object.user_params = json.dumps(
            {"AccessToken": "dsdjsadgasdkashkdsclkbjd"})
        user_authentication_object.save()
        alexa_channel = Channel.objects.create(name="Alexa")
        save_default_parameter_for_flow(
            intent, user, alexa_channel, None, None)
        is_feedback_required = Data.objects.get(
            user=user, variable="is_feedback_required").value
        is_attachment_required = Data.objects.get(
            user=user, variable="is_attachment_required").value
        choosen_file_type = json.loads(Data.objects.get(
            user=user, variable="choosen_file_type").value)
        is_authentication_required = Data.objects.get(
            user=user, variable="is_authentication_required").value
        is_user_authenticated = Data.objects.get(
            user=user, variable="is_user_authenticated").value
        last_identified_intent_name = json.loads(Data.objects.get(
            user=user, variable="last_identified_intent_name").value)
        self.assertEqual(is_feedback_required, "true")
        self.assertEqual(is_attachment_required, "true")
        self.assertEqual(choosen_file_type, "mp3")
        self.assertEqual(is_authentication_required, "true")
        self.assertEqual(is_user_authenticated, "true")
        self.assertEqual(last_identified_intent_name,
                         "TestIntentForDefaultParameters")

    def test_conflict_intent_identification(self):

        print("\n\nTesting conflict_intent_identification function")
        print("\n\nWill be done after identify_intent_tree")

    def test_identify_intent_tree(self):

        print("\n\nTesting identify_intent_tree function")
        print("\n\nWill be done after its dependencies are done")

    def test_return_next_tree_based_on_message(self):
        Config.objects.create()
        print("\n\nTesting return_next_tree_based_on_message function")
        bot_obj = Bot.objects.create(name='test_bot')
        bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()
        easychat_bot_user = EasyChatBotUser(
            bot_obj=bot_obj, channl_name="WhatsApp", src="en", bot_id=bot_obj.pk, bot_info_obj=bot_info_obj)
        Config.objects.create()
        current_tree = Tree.objects.create(name="TestTreeWithMultipleChildren")
        child_1 = Tree.objects.create(
            name="test_child1", accept_keywords="test1_A, test1_B, test1 C")
        child_2 = Tree.objects.create(
            name="test_child2", accept_keywords="test2_A, test2_B, test2 D")
        current_tree.children.add(child_1, child_2)

        keyword_list1 = ["test1_A", "test1_B", "test1 C", "C"]
        keyword_list2 = ["test2_A", "test2_B", "test2 D", "D"]

        for keyword in keyword_list1[:-1]:
            self.assertEqual(
                child_1, return_next_tree_based_on_message(easychat_bot_user, keyword, current_tree))
            print("\n\nPassed with keyword: " + str(keyword))

        for keyword in keyword_list2[:-1]:
            self.assertEqual(
                child_2, return_next_tree_based_on_message(easychat_bot_user, keyword, current_tree))
            print("\n\nPassed with keyword: " + str(keyword))

    def test_return_next_tree_based_on_intent_identification(self):

        print("\n\nTesting return_next_tree_based_on_intent_identification function")
        print("\n\nWill be done after identify_intent_tree")

    def test_clear_user_data(self):
        import os
        import uuid

        print("\n\nTesting clear_user_data function")
        user_id = str(uuid.uuid4())
        user = Profile.objects.create(user_id=user_id)
        Data.objects.create(
            user=user, variable="test_variable", value="to_be_deleted")
        auth_type_obj = Authentication.objects.create(
            name="TestAuthenticationObj")
        UserAuthentication.objects.create(user=user, auth_type=auth_type_obj)
        user.tree = Tree.objects.create(name="TestTree666")
        user.user_pipe = "TestPipeTextThisShouldNotMakeSense"
        user.save()

        # Current Working directory
        cwd = os.getcwd()
        print(str(cwd))
        user_folder_path = "/files/language_support/" + str(user_id)
        os.makedirs(cwd + user_folder_path)
        test_folder_path = "/files/language_support/" + \
            str(user_id) + "/test_folder"
        file = open(cwd + user_folder_path + "/test_file.txt", "w+")
        file.close()
        os.makedirs(cwd + test_folder_path)
        file = open(cwd + test_folder_path + "/test_file.txt", "w+")
        file.close()
        clear_user_data(user_id, None, 'Web')
        self.assertEqual(False, os.path.exists(cwd + user_folder_path))
        self.assertEqual(
            [], list(UserAuthentication.objects.filter(user=user)))
        self.assertEqual([], list(Data.objects.filter(user=user)))
        user = Profile.objects.get(user_id=user_id)
        self.assertEqual(None, user.tree)
        self.assertEqual("", user.user_pipe)

    def test_delete_intent(self):

        print("\n\nTesting delete_intent function")

        user = User.objects.create(username="89849549", password="sdhadsdsd")
        bot_obj = Bot.objects.create(name="TestBot")
        bot_obj.users.add(user)
        bot_obj.save()
        intent_obj = Intent.objects.create(name="TestIntent")
        intent_obj.bots.add(bot_obj)
        intent_obj.save()
        intent_pk = intent_obj.pk
        self.assertEqual(False, delete_intent(45, user))
        self.assertEqual(False, delete_intent(45, "user"))
        self.assertEqual(True, delete_intent(intent_pk, user))

    def test_get_identified_intent(self):
        Config.objects.create(monthly_analytics_parameter=6, daily_analytics_parameter=7,
                              top_intents_parameter=5, app_url="http://localhost:8000", no_of_bots_allowed=100)
        print("\n\nTesting get_identified_intent function")
        user_obj = User.objects.create(
            username="TestUserForTestBot", password="76540654")
        bot_obj = Bot.objects.create(
            name="TestBotForTestUserForTestBot", intent_score_threshold=0.5)
        channel_obj = Channel.objects.create(name="Web")
        intent_obj = Intent.objects.create(name="TestIntent1", training_data=json.dumps(
            {"1": "Hi", "2": "hello", "3": "hiya"}), restricted_keywords="stop, reset, bye")
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(channel_obj)
        intent_obj.save()
        bot_obj.users.add(user_obj)
        bot_obj.save()
        message = "Hi there Mr Bot, what is your name"
        is_intent_recognized, intent_list = get_identified_intent(
            message, user_obj, [bot_obj, ], [channel_obj, ])
        self.assertEqual(True, is_intent_recognized)
        self.assertEqual(intent_obj, intent_list)
        intent_obj_2 = Intent.objects.create(name="TestIntent2", training_data=json.dumps(
            {"1": "What is your name", "2": "your name please", "3": "can you tell your name"}), restricted_keywords="stop, reset, bye")
        intent_obj_2.bots.add(bot_obj)
        intent_obj_2.channels.add(channel_obj)
        intent_obj_2.save()
        is_intent_recognized, intent_list = get_identified_intent(
            message, user_obj, [bot_obj, ], [channel_obj, ])
        self.assertEqual(True, is_intent_recognized)
        self.assertEqual(intent_obj_2, intent_list)
        message = "DummyMessageToNotMatch"
        is_intent_recognized, intent_list = get_identified_intent(
            message, user_obj, [bot_obj, ], [channel_obj, ])
        self.assertEqual(False, is_intent_recognized)
        self.assertEqual(False, is_intent_recognized)
        self.assertEqual([], intent_list)

    def test_get_tag_mapper_list_for_given_user(self):

        print("\n\nTesting get_tag_mapper_list_for_given_user function")
        user = User.objects.create(
            role="1", status="1", username="TestRequestUser", password="pswdtest1")
        api_tree = ApiTree.objects.create(name="TestAPITree")
        api_tree.users.add(user)
        api_tree.save()
        tag_map_1 = TagMapper.objects.create(
            display_variable="ETA", alias_variable="Estimated Time of Arrival", api_tree=api_tree)
        tag_map_2 = TagMapper.objects.create(
            display_variable="WHO", alias_variable="World Health Organization", api_tree=api_tree)
        request = self.factory.post("/chat/test_endpoint")
        request.user = user
        tagmapper_objs = get_tag_mapper_list_for_given_user(request)
        self.assertEqual(set([tag_map_1, tag_map_2]), set(tagmapper_objs))

    def test_get_authentication_objs(self):

        print("\n\nTesting get_authentication_objs function")
        bot_obj = Bot.objects.create(name="TestBotForAuth")
        auth_obj_1 = Authentication.objects.create(
            name="TestAuthenticationObj", bot=bot_obj)
        auth_obj_2 = Authentication.objects.create(
            name="TestAuthenticationObj2", bot=bot_obj) 
        auth_obj_list = get_authentication_objs([bot_obj])
        expected_auth_obj_list = list((auth_obj_2, auth_obj_1))
        self.assertEqual(len(expected_auth_obj_list), len(auth_obj_list))

    def test_get_uat_bots(self):

        print("\n\nTesting get_uat_bots function")
        user1 = User.objects.create(username="TestUser1", password="8740461")
        user2 = User.objects.create(username="TestUser2", password="8740461")
        bot1 = Bot.objects.create(name="TestBot1", is_uat=True)
        bot1.users.add(user1)
        bot1.save()
        bot2 = Bot.objects.create(name="TestBot2", is_uat=True)
        bot2.users.add(user2)
        bot2.save()
        self.assertEqual(set([bot1]), set(get_uat_bots(user1)))
        self.assertEqual(set([bot1, bot2]), set(get_uat_bots('all')))

    def test_get_form_assist_uat_bots(self):

        print("\n\nTesting get_form_assist_uat_bots function")
        user1 = User.objects.create(username="TestUser1", password="8740461")
        user2 = User.objects.create(username="TestUser2", password="8740461")
        bot1 = Bot.objects.create(
            name="TestBot1", is_uat=True, is_form_assist_enabled=True)
        bot1.users.add(user1)
        bot1.save()
        bot2 = Bot.objects.create(
            name="TestBot2", is_uat=True, is_form_assist_enabled=True)
        bot2.users.add(user2)
        bot2.save()
        self.assertEqual(set([bot1]), set(get_form_assist_uat_bots(user1)))
        self.assertEqual(set([bot1, bot2]), set(
            get_form_assist_uat_bots('all')))

    def test_get_lead_generation_uat_bots(self):

        print("\n\nTesting get_lead_generation_uat_bots function")
        user1 = User.objects.create(username="TestUser1", password="8740461")
        user2 = User.objects.create(username="TestUser2", password="8740461")
        bot1 = Bot.objects.create(
            name="TestBot1", is_uat=True, is_lead_generation_enabled=True)
        bot1.users.add(user1)
        bot1.save()
        bot2 = Bot.objects.create(
            name="TestBot2", is_uat=True, is_lead_generation_enabled=True)
        bot2.users.add(user2)
        bot2.save()
        self.assertEqual(set([bot1]), set(get_lead_generation_uat_bots(user1)))
        self.assertEqual(set([bot1, bot2]), set(
            get_lead_generation_uat_bots('all')))

    def test_get_production_bot_from_id(self):

        print("\n\nTesting get_production_bot_from_id function")
        print("\n\nNot called anywhere")

    def test_get_production_bots(self):

        print("\n\nTesting get_production_bots function")
        print("\n\nNot called anywhere in files still actively used")

    def test_get_uat_bots_pk_list(self):

        print("\n\nTesting get_uat_bots_pk_list function")
        user1 = User.objects.create(username="TestUser1", password="8740461")
        user2 = User.objects.create(username="TestUser2", password="8740461")

        pk_list = []

        bot1 = Bot.objects.create(name="TestBot1", is_uat=True)
        bot1.users.add(user1)
        bot1.save()
        pk_list.append(bot1.pk)
        bot2 = Bot.objects.create(name="TestBot2", is_uat=True)
        bot2.users.add(user1)
        bot2.save()
        pk_list.append(bot2.pk)
        bot3 = Bot.objects.create(name="TestBot3", is_uat=True)
        bot3.users.add(user2)
        bot3.save()
        self.assertEqual(set(pk_list), set(get_uat_bots_pk_list(user1)))

    # def test_get_google_search_results(self):

    #     print("\n\nTesting get_google_search_results function")
    #     results_list = get_google_search_results(
    #         "What is Wikipedia", "009085939227162172546:d5vguy3w0ey", None, None, None, None)
    #     self.assertNotEqual(results_list[0]["link"], None)
    #     self.assertNotEqual(results_list[0]["title"], None)
    #     self.assertNotEqual(results_list[0]["content"], None)

    def test_get_edit_distance_threshold(self):

        print("\n\nTesting get_edit_distance_threshold function")
        self.assertEqual(1, get_edit_distance_threshold(
            None, None, None, None))

    def test_load_the_dictionary(self):

        print("\n\nTesting load_the_dictionary function")
        dictionary, words_in_dict = load_the_dictionary(None, None, None, None)
        self.assertNotEqual(type(dictionary), None)
        self.assertEqual(type(dictionary), type([1, 2]))
        self.assertNotEqual(type(words_in_dict), None)
        self.assertEqual(type(words_in_dict), type(set()))

    def test_process_string(self):

        print("\n\nTesting process_string function")
        configobject = Config.objects.create()
        configobject.autocorrect_replace_space = "_"
        configobject.autcorrect_do_nothing = "-:@"
        configobject.save()
        message_list = ["I am a Teapot : Fat and stout",
                        "I am an Ant@a_Anthill", "I am - the GOAT"]
        expected_processed_string_list = [
            "I am Teapot : Fat and stout", "I am Ant@a Anthill", "I am - GOAT"]
        processed_string_list = []
        for message in message_list:
            processed_string_list.append(
                process_string(message, None, None, None, None))
        self.assertEqual(set(expected_processed_string_list),
                         set(processed_string_list))

    def test_save_audit_trail(self):

        print("\n\nTesting save_audit_trail function")
        user = User.objects.create(username="TestUser1", password="8740461")
        action = "User Logged In"
        data = "Data1"
        save_audit_trail(user, action, data)
        audit_obj = AuditTrail.objects.get(user=user, action=action, data=data)
        self.assertEqual(audit_obj.action, action)
        self.assertEqual(audit_obj.data, data)

    def test_get_all_file_type(self):

        print("\n\nTesting get_all_file_type function")
        all_type_list = [
            {
                "is_selected": False,
                "file_type": 'image(ex. .jpeg, .png, .jpg)'
            },
            {
                "is_selected": False,
                "file_type": 'word processor(i.e. .doc,.pdf)'
            },
            {
                "is_selected": False,
                "file_type": 'compressed file(ex. .zip)'
            }, {
                "is_selected": False,
                "file_type": 'video file(ex. .mp4)'
            }]

        for item in get_all_file_type():
            if item in all_type_list:
                self.assertEqual(True, True)
            else:
                self.assertEqual(True, False)

    def test_convert_relative_path_to_absolute(self):

        print("\n\nTesting convert_relative_path_to_absolute function")
        print("\n\nTest need not be written as the function is now out of use")

    def test_insert_file_into_intent_from_drive(self):

        from EasyChatApp.constants import MEDIA_IMAGE, MEDIA_VIDEO, MEDIA_PDF

        print("\n\nTesting insert_file_into_intent_from_drive function")
        user = User.objects.create(
            username="TestUserECD", password="7464510165")

        bot_response_obj = BotResponse.objects.create()
        bot_response_obj.sentence = json.dumps(
            {"items": [{"text_response": "Hi this is TestBotResponse"}]})
        bot_response_obj.images = json.dumps({"items": []})
        bot_response_obj.videos = json.dumps({"items": []})
        bot_response_obj.cards = json.dumps({"items": []})
        pk = bot_response_obj.pk
        bot_response_obj.save()

        card_hardcoded = {
            "title": "ECD-PDF" + " attachment",
            "content": "",
            "link": "https://allincall.in/files/TestPDFFile.pdf",
            "img_url": ""
        }
        ecd1 = EasyChatDrive.objects.create(
            user=user, media_name="ECDImages", media_type=MEDIA_IMAGE, media_url="https://allincall.in/static/img/logo_icon.png")
        ecd2 = EasyChatDrive.objects.create(
            user=user, media_name="ECDVideos", media_type=MEDIA_VIDEO, media_url="https://youtu.be/sz0GF8sg1Ww")
        ecd3 = EasyChatDrive.objects.create(
            user=user, media_name="ECD-PDF", media_type=MEDIA_PDF, media_url="https://allincall.in/files/TestPDFFile.pdf")
        ecd4 = EasyChatDrive.objects.create(user=user, media_name="ECDImages", media_type=MEDIA_IMAGE,
                                            media_url="https://allincall.in/static/img/sales_ai_thumbsup.png")
        insert_file_into_intent_from_drive(
            bot_response_obj, [ecd1, ecd2, ecd3, ecd4])
        bot_response_obj_modified = BotResponse.objects.get(pk=pk)
        self.assertEqual(json.loads(bot_response_obj_modified.images), {"items": [
                         "https://allincall.in/static/img/logo_icon.png", "https://allincall.in/static/img/sales_ai_thumbsup.png"]})
        self.assertEqual(json.loads(bot_response_obj_modified.videos), {
                         "items": ["https://youtu.be/sz0GF8sg1Ww"]})
        self.assertEqual(json.loads(bot_response_obj_modified.cards), {
                         "items": [card_hardcoded]})

    def test_check_access_for_user(self):
        accesstype1 = AccessType.objects.create(name="Full Access")
        accesstype2 = AccessType.objects.create(name="Intent Related")
        accesstype3 = AccessType.objects.create(name="Bot Setting Related")

        user1 = User.objects.create(username="TestUser1", password="8740461")
        user2 = User.objects.create(username="TestUser2", password="8740461")

        bot1 = Bot.objects.create(name="TestBot1", is_uat=True)
        access_mng_obj = AccessManagement.objects.create(
            user=user1, bot=bot1)
        for access_type_obj in [accesstype1]:
            access_mng_obj.access_type.add(access_type_obj)
        bot1.users.add(user1)

        access_mng_obj = AccessManagement.objects.create(
            user=user2, bot=bot1)
        for access_type_obj in [accesstype3]:
            access_mng_obj.access_type.add(access_type_obj)
        bot1.users.add(user2)
        bot1.save()

        bot2 = Bot.objects.create(name="TestBot2", is_uat=True)
        access_mng_obj = AccessManagement.objects.create(
            user=user2, bot=bot2)
        for access_type_obj in [accesstype2]:
            access_mng_obj.access_type.add(access_type_obj)
        bot2.users.add(user2)
        bot2.save()

        self.assertEqual(check_access_for_user(
            user1, bot1.pk, "Full Access", type_of_query="bot_specific"), True)
        self.assertEqual(check_access_for_user(
            user1, bot1.pk, "Intent Related", type_of_query="bot_specific"), True)
        self.assertEqual(check_access_for_user(
            user1, bot1.pk, "Bot Setting Related", type_of_query="bot_specific"), True)
        self.assertEqual(check_access_for_user(
            user2, bot1.pk, "Bot Setting Related", type_of_query="bot_specific"), True)
        self.assertEqual(check_access_for_user(
            user2, bot1.pk, "Intent Related", type_of_query="bot_specific"), False)
        self.assertEqual(check_access_for_user(
            user2, bot1.pk, "Full Access", type_of_query="bot_specific"), False)

        self.assertEqual(check_access_for_user(
            user1, bot2.pk, "Intent Related", type_of_query="bot_specific"), False)
        self.assertEqual(check_access_for_user(
            user1, bot2.pk, "Full Access", type_of_query="bot_specific"), False)
        self.assertEqual(check_access_for_user(
            user1, bot2.pk, "Intent Related", type_of_query="bot_specific"), False)
        self.assertEqual(check_access_for_user(
            user2, bot2.pk, "Intent Related", type_of_query="bot_specific"), True)
        self.assertEqual(check_access_for_user(
            user2, bot2.pk, "Bot Setting Related", type_of_query="bot_specific"), False)
        self.assertEqual(check_access_for_user(
            user2, bot2.pk, "Full Access", type_of_query="bot_specific"), False)

        self.assertEqual(check_access_for_user(
            user2, None, "Full Access", type_of_query="overall",), False)
        self.assertEqual(check_access_for_user(
            user2, None, "Intent Related", type_of_query="overall"), True)
        self.assertEqual(check_access_for_user(
            user2, None, "Bot Setting Related", type_of_query="overall"), True)

        self.assertEqual(check_access_for_user(
            user1, None, "Full Access", type_of_query="overall"), True)
        self.assertEqual(check_access_for_user(
            user1, None, "Intent Related", type_of_query="overall"), True)
        self.assertEqual(check_access_for_user(
            user1, None, "Bot Setting Related", type_of_query="overall"), True)

    """
    function tested: add_confirmation_and_reset_tree
    input params:
        tree_obj: A tree object for which confirmation and reset tree should be created
        intent_pk: ID of intent
    output:
        Confirmation and reset tree should be successfully created
    """

    def test_add_confirmation_and_reset_tree(self):
        logger.info("Testing of add_confirmation_and_reset_tree is going on.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of add_confirmation_and_reset_tree is going on.\n")

        web_channel = Channel.objects.create(name="Web")
        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)
        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.save()
        category_obj = Category.objects.create(
            name="testcategory", bot=bot_obj)
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}')
        tree_obj = Tree.objects.create(name="Hi", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Hi", tree=tree_obj, keywords='{"0": "hey", "1": "hello", "2": "hi", "3": "whats"}', training_data='{"0": "Hey", "1": " hello", "2": " hi", "3": " whats up"}', category=category_obj)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()

        add_confirmation_and_reset_tree(tree_obj, intent_obj.id)
        confirmation_reset_tree_pk = tree_obj.confirmation_reset_tree_pk
        if confirmation_reset_tree_pk is None:
            self.assertEqual(True, False)

        confirm_reset_parent_obj = Tree.objects.get(
            id=confirmation_reset_tree_pk)
        reset_tree_obj = Tree.objects.get(name="Reset")
        self.assertEqual(confirm_reset_parent_obj.children.all().count(), 2)
        self.assertEqual(tree_obj.children.all().count(), 1)
        self.assertEqual(reset_tree_obj.children.all().count(), 1)
        self.assertEqual(reset_tree_obj.children.filter(name="Hi").count(), 1)

    """
    function tested: remove_confirmation_and_reset_tree
    input params:
        tree_obj: A tree object for which confirmation and reset tree should be created
    output:
        Confirmation and reset tree should be successfully removed from the parent tree object
    """

    def test_remove_confirmation_and_reset_tree(self):
        logger.info("Testing of remove_confirmation_and_reset_tree is going on.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of remove_confirmation_and_reset_tree is going on.\n")

        web_channel = Channel.objects.create(name="Web")
        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)
        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.save()
        category_obj = Category.objects.create(
            name="testcategory", bot=bot_obj)
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}')
        tree_obj = Tree.objects.create(name="Hi", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Hi", tree=tree_obj, keywords='{"0": "hey", "1": "hello", "2": "hi", "3": "whats"}', training_data='{"0": "Hey", "1": " hello", "2": " hi", "3": " whats up"}', category=category_obj)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()
        add_confirmation_and_reset_tree(tree_obj, intent_obj.id)
        remove_confirmation_and_reset_tree(tree_obj)
        self.assertEqual(tree_obj.children.all().count(), 0)
        self.assertEqual(tree_obj.confirmation_reset_tree_pk, None)
        self.assertEqual(tree_obj.is_confirmation_and_reset_enabled, False)

    def test_remo_unwanted_characters_from_message(self):
        logger.info("Testing of remove_confirmation_and_reset_tree is going on.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of remove_confirmation_and_reset_tree is going on.\n")

        validation_obj = EasyChatInputValidation()

        bot_obj = Bot.objects.create(name="testbot123")
        bot_id = bot_obj.pk
        raw_message = "hello.:+"
        formatted_message = validation_obj.remo_unwanted_characters_from_message(
            raw_message, bot_id)
        self.assertEqual(formatted_message, "hello.:")

    def test_build_suggestions_and_word_mapper(self):
        logger.info("Testing of test_build_suggestions_and_word_mapper is going on.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\n\n\nTesting of test_build_suggestions_and_word_mapper is going on.\n")
        bot_obj = Bot.objects.create(
            name="testbot123", slug="testbot", bot_display_name="testbot", bot_type="2")
        bot_id = bot_obj.pk
        word_mapper_obj = WordMapper.objects.create(
            keyword="laugh out loud", similar_words="lol,")
        word_mapper_obj.bots.add(bot_obj)
        channel_obj = Channel.objects.create(name='Web')
        tree_obj = Tree.objects.create(name="Hi")
        intent_obj = Intent.objects.create(name="test_intent", tree=tree_obj, is_part_of_suggestion_list=True, is_deleted=False,
                                           is_form_assist_enabled=False, is_hidden=False)

        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(channel_obj)
        intent_obj.training_data = json.dumps({"0": "please help me connect to your customer service", "1": " i want to talk to customer care",
                                               "2": " help me get in touch with customer service team", "3": " i want my issues to be resolved by customer care", "4": " Contact Customer Care"})
        intent_obj.save()
        word_mapper_obj.save()
        build_suggestions_and_word_mapper(
            bot_id, Bot, WordMapper, Channel, Intent, ChunksOfSuggestions)
        self.assertEqual(Bot.objects.filter(name="testbot123")[0].suggestion_list, json.dumps([{"key": "test_intent", "value": "test_intent", "count": 0, "pk": intent_obj.pk}, {"key": "please help me connect to your customer service", "value": "test_intent", "count": 0, "pk": intent_obj.pk}, {"key": " i want to talk to customer care", "value": "test_intent", "count": 0, "pk": intent_obj.pk}, {
                         "key": " help me get in touch with customer service team", "value": "test_intent", "count": 0, "pk": intent_obj.pk}, {"key": " i want my issues to be resolved by customer care", "value": "test_intent", "count": 0, "pk": intent_obj.pk}, {"key": " contact customer care", "value": "test_intent", "count": 0, "pk": intent_obj.pk}]))
        self.assertEqual(Bot.objects.filter(name="testbot123")[0].word_mapper_list, json.dumps(
            [{"keyword": "laugh out loud", "similar_words": ["lol"]}]))

    def test_check_and_reset_user(self):
        import os
        import uuid
        from django.utils import timezone

        print("\n\nTesting check_and_reset_user function")
        bot_obj = Bot.objects.create(
            name="testbot123", slug="testbot", bot_display_name="testbot")
        user_id = str(uuid.uuid4())
        user = Profile.objects.create(user_id=user_id, bot=bot_obj)
        Data.objects.create(
            user=user, bot=bot_obj, variable="test_variable", value="to_be_deleted")

        user.tree = Tree.objects.create(name="TestTree666")
        user.user_pipe = "TestPipeTextThisShouldNotMakeSense"
        user.previous_message_date = timezone.now() - timedelta(minutes=30)
        user.save()

        # Current Working directory
        cwd = os.getcwd()
        print(str(cwd))
        user_folder_path = "/files/language_support/" + str(user_id)
        os.makedirs(cwd + user_folder_path)
        test_folder_path = "/files/language_support/" + \
            str(user_id) + "/test_folder"
        file = open(cwd + user_folder_path + "/test_file.txt", "w+")
        file.close()
        os.makedirs(cwd + test_folder_path)
        file = open(cwd + test_folder_path + "/test_file.txt", "w+")
        file.close()

        check_and_reset_user(user, bot_obj, 'Web')
        self.assertEqual(False, os.path.exists(cwd + user_folder_path))
        self.assertEqual(
            [], list(UserAuthentication.objects.filter(user=user)))
        self.assertEqual([], list(Data.objects.filter(user=user)))
        user = Profile.objects.get(user_id=user_id)
        self.assertEqual(None, user.tree)
        self.assertEqual("", user.user_pipe)

    def test_is_campaign_link_enabled(self):
        print("\n\nTesting is_campaign_link_enabled function")
        channel_params = {"is_campaign_link": True}
        logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                        'source': 'None', 'channel': 'None', 'bot_id': 'None'}
        output = is_campaign_link_enabled(
            channel_params, '1', logger_extra, Intent)

        self.assertEqual(output, 'TestIntent')

        channel_params = {"is_campaign_link": False}
        output = is_campaign_link_enabled(
            channel_params, '1', logger_extra, Intent)
        self.assertEqual(output, '1')

    def test_get_channel_obj(self):
        print("\n\nTesting get_channel_obj function")
        logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                        'source': 'None', 'channel': 'None', 'bot_id': 'None'}
        output = get_channel_obj('GoogleHome', Channel, logger_extra)
        channel_obj = Channel.objects.get(name="GoogleHome")

        self.assertEqual(output, channel_obj)

        output = get_channel_obj('LinkedIntest', Channel, logger_extra)

        self.assertEqual(output, None)

    def test_get_bot_object_and_save_last_query_time(self):
        print("\n\nTesting get_bot_object_and_save_last_query_time function")
        bot1 = Bot.objects.create(name="uat", is_uat=True)
        logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                        'source': 'None', 'channel': 'None', 'bot_id': 'None'}
        output = get_bot_object_and_save_last_query_time("test_user_id",
                                                         2, "uat", Bot, logger_extra)

        self.assertEqual(output, bot1)

        output = get_bot_object_and_save_last_query_time("test_user_id",
                                                         100, "TestBotFalse", Bot, logger_extra)

        self.assertEqual(output, None)

    # def test_get_message_and_src_after_translation(self):
    #     print("\n\nTesting get_message_and_src_after_translation function")
    #     logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
    #                     'source': 'None', 'channel': 'None', 'bot_id': 'None'}
    #     bot1 = Bot.objects.all()[0]
    #     output = get_message_and_src_after_translation(
    #         bot1, 'test', logger_extra)

    #     self.assertEqual(output, ('test', 'en'))

    def test_is_lead_generation_enabled(self):
        print("\n\nTesting is_lead_generation_enabled function")
        logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                        'source': 'None', 'channel': 'None', 'bot_id': 'None'}
        bot1 = Bot.objects.all()[0]
        user = User.objects.all()[0]
        app_config = Config.objects.create()
        output = is_lead_generation_enabled(bot1.is_form_assist_enabled, app_config,
                                            'testing_message', user.id, None, 'GoogleHome', bot1.id, bot1, logger_extra)

        self.assertEqual(output, (True, False, 'testing message'))

        bot2 = Bot.objects.create(name='bot2', is_form_assist_enabled=True)
        output = is_lead_generation_enabled(bot2.is_form_assist_enabled, app_config,
                                            'testing_message', user.id, None, 'GoogleHome', bot2.id, bot2, logger_extra)

        self.assertEqual(output, (False, True, 'testing_message'))

    def test_save_user_flow_details(self):
        print("\n\nTesting save_user_flow_details function")
        logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                        'source': 'None', 'channel': 'None', 'bot_id': 'None'}
        user = User.objects.all()[0]
        user_profile = Profile.objects.create(user_id=user.id)
        last_message_date = user_profile.last_message_date
        channel_obj = Channel.objects.all()[0]
        output = save_user_flow_details(
            user_profile, channel_obj, logger_extra)

        self.assertEqual(output.channel, channel_obj)
        self.assertEqual(output.previous_message_date, last_message_date)

    def test_get_previous_bot_id(self):
        print("\n\nTesting get_previous_bot_id function")
        logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                        'source': 'None', 'channel': 'None', 'bot_id': 'None'}
        user = User.objects.all()[0]
        user_profile = Profile.objects.create(user_id=user.id)
        bot = Bot.objects.all()[0]
        Data.objects.create(user=user_profile, bot=bot)

        output = get_previous_bot_id(
            user_profile, bot.id, "WhatsApp", logger_extra, Data)

        self.assertEqual(output.tree, None)

    def test_is_sticky_message_enabled(self):
        print("\n\nTesting is_sticky_message_enabled function")
        logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                        'source': 'None', 'channel': 'None', 'bot_id': 'None'}
        channel_params = {"is_sticky_message": True}
        user = User.objects.all()[0]
        user_profile = Profile.objects.create(user_id=user.id)
        output = is_sticky_message_enabled(
            user_profile, channel_params, logger_extra)

        self.assertEqual(output[0].tree, None)

    def test_return_next_tree_based_is_go_back_enabled(self):
        print("\n\nTesting return_next_tree_based_is_go_back_enabled function")

        bot_obj = Bot.objects.create(name='test_bot')
        easychat_bot_user = EasyChatBotUser(
            bot_obj=bot_obj, channl_name="WhatsApp", src="en", bot_id=bot_obj.pk)
        channel_params = {"is_go_back_enabled": True, "channel_name": "WhatsApp"}

        channel_obj = Channel.objects.filter(name="WhatsApp").first()
        if not channel_obj:
            channel_obj = Channel.objects.create(name="WhatsApp")

        message = "Go Back"
        user1 = User.objects.create(username="testuser4", password="testuser4")
        user_profile1 = Profile.objects.create(user_id=user1.id)
        tree = Tree.objects.get(pk=1)
        user_profile1.tree = tree
        tree.is_go_back_enabled = True
        tree.save()
        easychat_params = EasyChatChannelParams(
            channel_params, user_profile1.user_id)
        easychat_params.channel_obj = channel_obj
        Data.objects.create(user=user_profile1,
                            variable="last_tree_pk", value="2")
        output = return_next_tree_based_is_go_back_enabled(
            easychat_params, message, message, user_profile1, easychat_bot_user, "", [])

        self.assertNotEqual(output[1], None)
        self.assertNotEqual(user_profile1.tree, None)

    def test_save_flow_analytics_data_pipe_processor(self):
        print("\n\nTesting save_flow_analytics_data_pipe_processor function")
        logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                        'source': 'None', 'channel': 'None', 'bot_id': 'None'}
        user1 = User.objects.create(username="testuser1", password="testuser1")
        user_profile1 = Profile.objects.create(user_id=user1.id)
        tree = Tree.objects.create(name='test_intent')
        bot_obj = Bot.objects.create(name='test_bot')

        message = "test_message"
        channel_obj = Channel.objects.all()[0]
        test_intent_obj = Intent.objects.create(name='test_intent1')

        tree1 = Tree.objects.create(name='test_intent1')
        tree1.children.add(tree)
        tree1.save()

        user2 = User.objects.create(username="testuser2", password="testuser2")
        user_profile2 = Profile.objects.create(user_id=user2.id)
        FlowAnalytics.objects.create(
            user=user_profile2, intent_indentifed=test_intent_obj, previous_tree=tree)

        easychat_params = EasyChatChannelParams({}, user_profile2.user_id)

        save_flow_analytics_data_pipe_processor(
            message, tree, bot_obj, user_profile2, None, channel_obj, bot_obj.id, FlowAnalytics, Data, Tree, logger_extra, easychat_params)

        flow_analytics_obj1 = FlowAnalytics.objects.filter(
            user=user_profile2).last()
        data_obj1 = Data.objects.filter(user=user_profile2).last()
        data_obj_value1 = data_obj1.get_value()
        self.assertEqual(flow_analytics_obj1.previous_tree, tree1)
        self.assertEqual(int(data_obj_value1), tree.pk)

        Data.objects.create(user=user_profile1,
                            variable="last_level_tree_pk", value=2)
        intent_obj = Intent.objects.create(name='test_intent')
        intent_obj.tree = tree
        intent_obj.bots.add(bot_obj)
        intent_obj.save()

        easychat_params = EasyChatChannelParams({}, user_profile1.user_id)

        save_flow_analytics_data_pipe_processor(
            message, tree, bot_obj, user_profile1, None, channel_obj, bot_obj.id, FlowAnalytics, Data, Tree, logger_extra, easychat_params)

        flow_analytics_obj2 = FlowAnalytics.objects.filter(
            user=user_profile1).last()
        data_obj2 = Data.objects.filter(user=user_profile1).last()
        data_obj_value2 = data_obj2.get_value()
        self.assertEqual(flow_analytics_obj2.intent_indentifed, intent_obj)
        self.assertEqual(flow_analytics_obj2.user_message, message)
        self.assertEqual(int(data_obj_value2), tree.pk)

    def test_return_widgets(self):
        print("\n\nTesting return_widgets function")
        logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                        'source': 'None', 'channel': 'None', 'bot_id': 'None'}
        modes = {"is_radio_button": "true"}
        modes_param = {"radio_button_choices": "test_radio_button"}
        test_bot = Bot.objects.all()[0]
        message = 'test_intent_tree1'
        easychat_bot_user = EasyChatBotUser(
            bot_obj=test_bot, bot_id=test_bot.id, message=message)
        widget = return_widgets(
            modes, modes_param, easychat_bot_user, logger_extra)
        self.assertEqual(widget, modes_param["radio_button_choices"])

        modes = {"is_drop_down": "true"}
        modes_param = {"drop_down_choices": "test_drop_down"}
        widget = return_widgets(
            modes, modes_param, easychat_bot_user, logger_extra)
        self.assertEqual(widget, modes_param["drop_down_choices"])

        modes = {"is_check_box": "true"}
        modes_param = {"check_box_choices": "test_check_box"}
        widget = return_widgets(
            modes, modes_param, easychat_bot_user, logger_extra)
        self.assertEqual(widget, modes_param["check_box_choices"])

    def test_whatsapp_nps_update(self):
        from django.utils import timezone
        print("\n\nTesting whatsapp_nps_update function")
        logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                        'source': 'None', 'channel': 'None', 'bot_id': 'None'}
        user = User.objects.create(
            username="test_user_wapp", password="test_user_wapp")
        user_profile = Profile.objects.create(user_id=user.id)
        channel = Channel.objects.create(name="WhatsApp")
        user_profile.is_nps_message_send = True
        user_profile.channel = channel
        user_profile.save()
        message = "5"
        bot_obj = Bot.objects.create(name="test_bot_wapp")
        output = whatsapp_nps_update(
            user_profile, message, bot_obj, logger_extra, Feedback)

        feedback_obj = Feedback.objects.filter(
            user_id=user_profile.user_id).last()
        self.assertEqual(output[2], True)
        self.assertEqual(feedback_obj.rating, int(message))
        self.assertEqual(user_profile.is_comment_needed, True)
        self.assertEqual(output[3], False)

        message = "test_comment"
        user_profile.previous_message_date = timezone.now()
        user_profile.save()
        output = whatsapp_nps_update(
            user_profile, message, bot_obj, logger_extra, Feedback)

        feedback_obj = Feedback.objects.filter(
            user_id=user_profile.user_id, bot=bot_obj)[0]

        self.assertEqual(feedback_obj.comments, message)
        self.assertEqual(user_profile.is_nps_message_send, False)
        self.assertEqual(user_profile.is_comment_needed, False)

    def test_return_autocorrect_response(self):
        print("\n\nTesting return_autocorrect_response function")
        logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                        'source': 'None', 'channel': 'None', 'bot_id': 'None'}
        app_config = Config.objects.create(is_auto_correct_required=True)
        user_profile1 = Profile.objects.all()[0]
        user_message = "Chat with an expert"
        bot_obj = Bot.objects.all()[0]
        output = return_autocorrect_response(
            app_config, user_profile1, user_message, logger_extra, bot_obj.id, None, None)

        self.assertEqual(output, "chat with an expert")

    def test_return_user_tree_based_suggestion(self):
        print("\n\nTesting return_user_tree_based_suggestion function")

        user1 = User.objects.all()[0]
        user_profile1 = Profile.objects.create(user_id=user1.id)
        test_bot = Bot.objects.all()[0]
        message = 'test_intent_tree1'

        tree = Tree.objects.create(name='test_tree1')
        easychat_bot_user = EasyChatBotUser(
            bot_obj=test_bot, bot_id=test_bot.id, message=message)
        easychat_params = EasyChatChannelParams({}, user_profile1.user_id)
        easychat_params.entered_suggestion = True
        easychat_params.is_sticky_message_called_in_flow = False
        easychat_params.is_manually_typed_query = True

        output = return_user_tree_based_suggestion(
            easychat_params, easychat_bot_user, user_profile1, tree, message)

        self.assertEqual(output[1], message)

    def test_return_user_tree_based_on_intent_hash(self):
        print("\n\nTesting return_user_tree_based_on_intent_hash function")

        user1 = User.objects.all()[0]
        user_profile1 = Profile.objects.create(user_id=user1.id)
        test_bot = Bot.objects.all()[0]
        message = 'test_intent_tree1'
        import hashlib
        intent_hash = hashlib.md5("test_intent_tree1".encode()).hexdigest()

        try:
            channel_obj = Channel.objects.get(name="Web")
        except:
            channel_obj = Channel.objects.create(name="Web")
            channel_obj.save()

        intent_obj = Intent.objects.create(
            name='test_intent_tree1', intent_hash=intent_hash)
        intent_obj.bots.add(test_bot)
        intent_obj.channels.add(channel_obj)
        intent_obj.save()
        tree = Tree.objects.create(name='test_tree1')

        easychat_bot_user = EasyChatBotUser(bot_obj=test_bot)
        easychat_bot_user.channel_name = "Web"
        channel_params = {"entered_suggestion": False}
        easychat_params = EasyChatChannelParams(
            channel_params, user1.id)
        output = return_user_tree_based_on_intent_hash(
            user_profile1, tree, message, easychat_bot_user, easychat_params)

        self.assertEqual(output[1], message)

    def test_get_hashed_intent_name(self):
        import hashlib
        test_bot = Bot.objects.all()[0]
        output = get_hashed_intent_name("test intent name", test_bot)
        expected_output = hashlib.md5("intent name test".encode()).hexdigest()
        self.assertEqual(output, expected_output)

    def test_save_flow_analytics_data_pipe_processor_none(self):
        print("\n\nTesting save_flow_analytics_data_pipe_processor_none function")
        logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                        'source': 'None', 'channel': 'None', 'bot_id': 'None'}
        user1 = User.objects.create(
            username="test_user10", password="test_user10")
        user_profile1 = Profile.objects.create(user_id=user1.id)
        tree = Tree.objects.create(name='test_intent_none')
        bot_obj = Bot.objects.create(name='test_bot_none')
        message = "test_message_check"
        channel_obj = Channel.objects.all()[0]

        easychat_params = EasyChatChannelParams({}, user_profile1.user_id)

        tree1 = Tree.objects.create(name='test_intent1_none')
        tree1.children.add(tree)
        tree1.save()

        Data.objects.create(user=user_profile1,
                            variable="last_level_tree_pk", value="2")
        intent_obj = Intent.objects.create(name='test_intent_none')
        intent_obj.tree = tree
        intent_obj.bots.add(bot_obj)
        intent_obj.save()

        save_flow_analytics_data_pipe_processor_none(
            user_profile1, message, tree, bot_obj, None, channel_obj, Intent, Data, FlowAnalytics, logger_extra, easychat_params)

        flow_analytics_obj1 = FlowAnalytics.objects.filter(
            user=user_profile1).last()
        data_obj1 = Data.objects.filter(user=user_profile1).last()
        data_obj_value1 = data_obj1.get_value()
        self.assertEqual(flow_analytics_obj1.current_tree, tree)
        self.assertNotEqual(data_obj_value1, None)

    def test_check_for_expired_credentials(self):
        print("\n\nTesting check_for_expired_credentials function")
        user_obj = User.objects.create(username="testuser",
                                       password="Test@1234",
                                       is_staff=False,
                                       status="1", is_chatbot_creation_allowed="1",
                                       role="bot_builder", is_sandbox_user=True)

        sandbox_user_obj = SandboxUser.objects.create(
            username="testuser", password="Test@1234")

        self.assertEqual(check_for_expired_credentials(
            user_obj, SandboxUser), False)

        sandbox_user_obj.will_expire_on = timezone.now() - timedelta(days=1)
        sandbox_user_obj.save()

        self.assertEqual(check_for_expired_credentials(
            user_obj, SandboxUser), True)

        user_obj = User.objects.create(username="testusertwo",
                                       password="Test@1234",
                                       is_staff=False,
                                       status="1", is_chatbot_creation_allowed="1",
                                       role="bot_builder", is_sandbox_user=True)

        sandbox_user_obj = SandboxUser.objects.create(
            username="testusertwo", password="Test@1234", is_expired=True)

        self.assertEqual(check_for_expired_credentials(
            user_obj, SandboxUser), True)

        user_obj = User.objects.create(username="testuserthree",
                                       password="Test@1234",
                                       is_staff=False,
                                       status="1", is_chatbot_creation_allowed="1",
                                       role="bot_builder", is_sandbox_user=True)

        sandbox_user_obj = SandboxUser.objects.create(
            username="testuserthree", password="Test@1234", will_expire_on=timezone.now() + timedelta(hours=2))

        self.assertEqual(check_for_expired_credentials(
            user_obj, SandboxUser), False)

        sandbox_user_obj.will_expire_on = timezone.now() - timedelta(hours=1)
        sandbox_user_obj.save()

        self.assertEqual(check_for_expired_credentials(
            user_obj, SandboxUser), True)

    # def test_successfull_file_upload_response(self):
    #     print("\n\nTesting successfull_file_upload_response function")

    #     self.assertEqual(successfull_file_upload_response(
    #         None), "Your file has been successfully uploaded.")

    #     bot_obj = Bot.objects.get(pk=1)
    #     channel = Channel.objects.create(name="test")
    #     bot_channel = BotChannel.objects.create(bot=bot_obj, channel=channel)
    #     lang_obj = Language.objects.create(lang="hi")
    #     bot_channel.languages_supported.add(lang_obj)
    #     bot_channel.save()

    #     eng_lang_obj = check_and_create_default_language_object(bot_obj, Language, RequiredBotTemplate)

    #     check_and_create_required_bot_language_template_for_selected_language(bot_obj, lang_obj, eng_lang_obj, RequiredBotTemplate, EasyChatTranslationCache)

    #     language_template_obj = RequiredBotTemplate.objects.get(
    #         bot=bot_obj, language=lang_obj)

    #     self.assertEqual(successfull_file_upload_response(
    #         language_template_obj), "आपकी फ़ाइल सफलतापूर्वक अपलोड कर दी गई है।")

    def test_is_similar_words_already_exist(self):
        print("\n\nTesting is_similar_words_already_exist")

        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")

        word_mapper_obj = WordMapper.objects.create(
            keyword="account", similar_words="acc, ac, a/c")
        word_mapper_obj.bots.add(bot_obj)
        word_mapper_obj.save()

        values_list = ["ac"]
        output = is_similar_words_already_exist(
            values_list, bot_obj, WordMapper)
        self.assertEqual(output, True)

        values_list = ["lol"]
        output = is_similar_words_already_exist(
            values_list, bot_obj, WordMapper)
        self.assertEqual(output, False)

    def test_check_for_tms_intent_and_create_categories(self):
        print("\n\nTesting check_for_tms_intent_and_create_categories")

        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        intent_obj = Intent.objects.create(
            name="test1", is_easy_tms_allowed=False)
        intent_obj.bots.add(bot_obj)
        intent_obj.save()
        output = check_for_tms_intent_and_create_categories(
            intent_obj.pk, ["testcat"], TicketCategory)

        self.assertEqual(output['message'], "not a tms intent")

        intent_obj = Intent.objects.create(
            name="test2", is_easy_tms_allowed=True)
        intent_obj.bots.add(bot_obj)
        intent_obj.save()
        output = check_for_tms_intent_and_create_categories(
            intent_obj.pk, ["testcat"], TicketCategory)

        self.assertEqual(output['message'], "Categories Created")

    def test_create_tms_categories(self):
        print("\n\nTesting create_tms_categories")
        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        before_count = TicketCategory.objects.all().count()

        create_tms_categories(["testcat1", "testcat2"],
                              bot_obj, TicketCategory)
        curr_count = TicketCategory.objects.all().count()
        self.assertEqual(before_count + 2, curr_count)

        TicketCategory.objects.create(bot=bot_obj, ticket_category="test")
        before_count = TicketCategory.objects.all().count()

        create_tms_categories(
            ["testcat3", "testcat4", "testcat5"], bot_obj, TicketCategory)
        curr_count = TicketCategory.objects.all().count()
        self.assertEqual(before_count + 3, curr_count)

    def test_update_dropdown_choices_of_tms_intent(self):
        print("\n\nTesting create_tms_categories")
        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        intent_obj = Intent.objects.create(
            name="test1", is_easy_tms_allowed=True)
        intent_obj.bots.add(bot_obj)
        intent_obj.save()
        response = update_dropdown_choices_of_tms_intent(
            bot_obj, TicketCategory)
        self.assertEqual(response['status'], 200)

        bot_obj = None

        response = update_dropdown_choices_of_tms_intent(
            bot_obj, TicketCategory)

        self.assertEqual(response['status'], 200)

    def test_is_valid_password(self):
        print("\n\nTesting is_valid_password")
        passwords = ["abcde", "Abcdef@123", "abcdeF@hijk",
                     "bcdefghi@jklmnopqr@12", "Ab@1c"]
        expected_output = [False, True, False, False, False]

        validation_obj = EasyChatInputValidation()

        for i in range(0, len(passwords)):
            self.assertEqual(validation_obj.is_valid_password(
                passwords[i]), expected_output[i])

    def test_is_valid_email(self):
        print("\n\nTesting is_valid_email")
        valid_username = ["email@example.com", "firstname.lastname@example.com", "email@subdomain.example.com",
                          "email@example-one.com", "1234567890@example.com", "_______@example.com"]

        validation_obj = EasyChatInputValidation()

        for username in valid_username:
            self.assertEqual(validation_obj.is_valid_email(
                username), True)

        invalid_username = ["#@%^%#$@#$@#.com", "@example.com",
                            "email@example@example.com", "abcdefghijklmnopqrst", "abcdefghi@abc", "abcd efgh"]

        for username in invalid_username:
            self.assertEqual(validation_obj.is_valid_email(
                username), False)

    def test_check_for_system_commands(self):
        print("\n\nTesting check_for_system_commands")
        Config.objects.create()

        code = "import threading\nthreading.Thread()"

        self.assertEqual(check_for_system_commands(code, Config), True)

        code = "import re\ns = r'[a-z]'"

        self.assertEqual(check_for_system_commands(code, Config), False)

    def test_sync_word_mapper_with_intent(self):
        print("\n\nTesting sync_word_mapper_with_intent")

        web_channel = Channel.objects.create(name="Web")
        user_obj = User.objects.create(
            username="test1234", password="test1234", role=BOT_BUILDER_ROLE, status="1", is_online=True)

        bot_obj = Bot.objects.create(
            name="test1", slug="test1", bot_display_name="test1", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.save()
        category_obj = Category.objects.create(
            name="testcategory", bot=bot_obj)
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}', modes_param='{"choosen_file_type": ".png"}', modes='{"is_typable": "true", "is_attachment_required": "true", "is_button": "true", "is_slidable": "false", "is_date": "false", "is_dropdown": "false"}')
        tree_obj = Tree.objects.create(name="Hi", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Hi", tree=tree_obj, is_authentication_required=False, is_feedback_required=True, keywords='{"0": "hey", "1": "hlo", "2": "hi", "3": "whats"}', training_data='{"0": "Hey", "1": "hlo", "2": "hi", "3": "whats up"}', category=category_obj)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()

        word_mapper_obj = WordMapper.objects.create(
            keyword="hello", similar_words="hlo,")

        word_mapper_obj.bots.add(bot_obj)

        sync_word_mapper_with_intent(bot_obj, True)

        intent_obj = Intent.objects.get(pk=intent_obj.pk)

        expected_response = {"0": "Hey", "1": "hlo",
                             "2": "hi", "3": "whats up", "4": "hello"}

        self.assertEqual(expected_response, json.loads(
            intent_obj.training_data))

    def test_check_and_parse_channel_messages(self):
        print("\n\nTesting check_and_parse_channel_messages")
        welcome_message = "Hi, I am Iris, a Virtual Assistant."
        failure_message = "I'm not sure if I can help you with your query."
        authentication_message = "Please complete authentication to use this service.         "
        welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
            welcome_message, failure_message, authentication_message)

        self.assertEqual(
            welcome_message, "Hi, I am Iris, a Virtual Assistant.")
        self.assertEqual(
            failure_message, "I'm not sure if I can help you with your query.")

    def test_check_channel_status_and_message(self):
        print("\n\nTesting check_channel_status_and_message")
        welcome_message = "Hi, I am Iris, a Virtual Assistant."
        failure_message = "<p>I'm not sure if I can help you with your query.</p>"
        authentication_message = "Please complete authentication to use this service.         "
        status, message = check_channel_status_and_message(
            welcome_message, failure_message, authentication_message)

        self.assertEqual(status, 500)

        authentication_message = ""
        status, message = check_channel_status_and_message(
            welcome_message, failure_message, authentication_message)

        self.assertEqual(status, 400)
        self.assertEqual(
            message, "Authentication message is either empty or invalid")

    def test_check_is_flow_termination_break(self):
        print("\n\nTesting check_is_flow_termination_break")
        web_channel = Channel.objects.create(name="Web")
        user_obj = User.objects.create(
            username="abortuser", password="abortuser", role=BOT_BUILDER_ROLE, status="1", is_online=True)

        bot_obj = Bot.objects.create(
            name="abortbot", slug="abortbot", bot_display_name="abortbot", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.flow_termination_keywords = '{"items": ["stop"]}'
        bot_obj.save()
        category_obj = Category.objects.create(
            name="testcategory", bot=bot_obj)
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}', modes_param='{"choosen_file_type": ".png"}', modes='{"is_typable": "true", "is_attachment_required": "true", "is_button": "true", "is_slidable": "false", "is_date": "false", "is_dropdown": "false"}')
        tree_obj = Tree.objects.create(
            name="Parent", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Parent", tree=tree_obj, is_authentication_required=False, is_feedback_required=True, keywords='{"0": "hey", "1": "hlo", "2": "hi", "3": "whats"}', training_data='{"0": "Hey", "1": "hlo", "2": "hi", "3": "whats up"}', category=category_obj)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()
        tree_child_obj = Tree.objects.create(
            name="children", response=bot_response_obj)
        tree_obj.children.add(tree_child_obj)

        easychat_user = Profile.objects.create(user_id="test123")
        easychat_user.tree = tree_obj
        easychat_user.save()

        easychat_bot_user = EasyChatBotUser(
            bot_obj=bot_obj, channl_name=web_channel.name, src="en", bot_id=bot_obj.pk)
        channel_params = {"entered_suggestion": False}
        easychat_params = EasyChatChannelParams(
            channel_params, easychat_user.user_id)

        is_flow_termination_break, display_messsage = check_is_flow_termination_break(
            "stop", easychat_user, easychat_params, easychat_bot_user, [None, None, None, None])
        self.assertEqual(is_flow_termination_break, True)

        is_flow_termination_break, display_messsage = check_is_flow_termination_break(
            "random word", easychat_user, easychat_params, easychat_bot_user, [None, None, None, None])

        self.assertEqual(is_flow_termination_break, False)

    def test_check_is_flow_terminated(self):
        print("\n\nTesting check_is_flow_terminated")
        web_channel = Channel.objects.create(name="Web")
        user_obj = User.objects.create(
            username="abortuser", password="abortuser", role=BOT_BUILDER_ROLE, status="1", is_online=True)

        bot_obj = Bot.objects.create(
            name="abortbot", slug="abortbot", bot_display_name="abortbot", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.flow_termination_keywords = '{"items": ["stop"]}'
        bot_obj.save()
        category_obj = Category.objects.create(
            name="testcategory", bot=bot_obj)
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}', modes_param='{"choosen_file_type": ".png"}', modes='{"is_typable": "true", "is_attachment_required": "true", "is_button": "true", "is_slidable": "false", "is_date": "false", "is_dropdown": "false"}')
        tree_obj = Tree.objects.create(name="Hi", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Hi", tree=tree_obj, is_authentication_required=False, is_feedback_required=True, keywords='{"0": "hey", "1": "hlo", "2": "hi", "3": "whats"}', training_data='{"0": "Hey", "1": "hlo", "2": "hi", "3": "whats up"}', category=category_obj)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()
        tree_child_obj = Tree.objects.create(
            name="children", response=bot_response_obj)
        tree_obj.children.add(tree_child_obj)

        easychat_user = Profile.objects.create(user_id="test123")
        easychat_user.tree = tree_obj
        easychat_user.save()

        save_data(easychat_user, {
                  "easychat_flow_termination_initiated": "true"}, None, web_channel, bot_obj.pk, is_cache=True)
        save_data(easychat_user, {
                  "easychat_flow_termination_previous_tree": easychat_user.tree.pk}, None, web_channel, bot_obj.pk, is_cache=True)
        save_data(easychat_user, {
                  "easychat_flow_termination_message": "stop"}, None, web_channel, bot_obj.pk, is_cache=True)
        save_data(easychat_user, {
                  "last_identified_intent_name": "hi"}, None, web_channel, bot_obj.pk, is_cache=True)

        easychat_bot_user = EasyChatBotUser(
            bot_obj=bot_obj, channl_name=web_channel.name, src="en", bot_id=bot_obj.pk)
        channel_params = {"entered_suggestion": False}
        easychat_params = EasyChatChannelParams(
            channel_params, easychat_user.user_id)

        is_flow_terminated, easychat_flow_termination_initiated = check_is_flow_terminated(
            "yes", easychat_user, easychat_params, easychat_bot_user, [None, None, None, None], "Flow Terminated")

        self.assertEqual(is_flow_terminated, False)

        is_flow_terminated, easychat_flow_termination_initiated = check_is_flow_terminated(
            "no", easychat_user, easychat_params, easychat_bot_user, [None, None, None, None], "Flow Terminated")

        self.assertEqual(is_flow_terminated, False)

    def test_check_if_abort_flow_initiated(self):
        print("\n\nTesting check_if_abort_flow_initiated")
        web_channel = Channel.objects.create(name="Web")
        user_obj = User.objects.create(
            username="abortuser", password="abortuser", role=BOT_BUILDER_ROLE, status="1", is_online=True)

        bot_obj = Bot.objects.create(
            name="abortbot", slug="abortbot", bot_display_name="abortbot", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.flow_termination_keywords = '{"items": ["stop"]}'
        bot_obj.save()
        category_obj = Category.objects.create(
            name="testcategory", bot=bot_obj)
        Category.objects.create(
            name="testCategory2", bot=bot_obj)
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}', modes_param='{"choosen_file_type": ".png"}', modes='{"is_typable": "true", "is_attachment_required": "true", "is_button": "true", "is_slidable": "false", "is_date": "false", "is_dropdown": "false"}')
        tree_obj = Tree.objects.create(
            name="Parent", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Parent", tree=tree_obj, is_authentication_required=False, is_feedback_required=True, keywords='{"0": "hey", "1": "hlo", "2": "hi", "3": "whats"}', training_data='{"0": "Hey", "1": "hlo", "2": "hi", "3": "whats up"}', category=category_obj)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()
        tree_child_obj = Tree.objects.create(
            name="children", response=bot_response_obj)
        tree_obj.children.add(tree_child_obj)

        easychat_user = Profile.objects.create(user_id="test123")
        easychat_user.tree = tree_child_obj
        easychat_user.save()
        easychat_bot_user = EasyChatBotUser(
            bot_obj=bot_obj, channl_name=web_channel.name, src="en", bot_id=bot_obj.pk)
        channel_params = {"entered_suggestion": False}
        easychat_params = EasyChatChannelParams(
            channel_params, easychat_user.user_id)

        is_abort_flow_initiated, display_messsage = check_if_abort_flow_initiated(
            easychat_bot_user, easychat_params, "hi", easychat_user, "Are you sure you want to abort it?", tree_obj, [None, None, None, None])

        self.assertEqual(is_abort_flow_initiated, True)

        is_abort_flow_initiated, display_messsage = check_if_abort_flow_initiated(
            easychat_bot_user, easychat_params, "not hash word", easychat_user, "Are you sure you want to abort it?", tree_obj, [None, None, None, None])

        self.assertEqual(is_abort_flow_initiated, False)

        easychat_bot_user.category_name = "testCategory2"
        is_abort_flow_initiated, display_messsage = check_if_abort_flow_initiated(
            easychat_bot_user, easychat_params, "hi", easychat_user, "Are you sure you want to abort it?", tree_obj, [None, None, None, None])

        self.assertEqual(is_abort_flow_initiated, False)

    def test_return_tree_if_flow_aborted(self):
        print("\n\nTesting return_tree_if_flow_aborted")
        web_channel = Channel.objects.create(name="Web")
        user_obj = User.objects.create(
            username="abortuser", password="abortuser", role=BOT_BUILDER_ROLE, status="1", is_online=True)

        bot_obj = Bot.objects.create(
            name="abortbot", slug="abortbot", bot_display_name="abortbot", bot_type="Simple")
        bot_obj.users.add(user_obj)
        bot_obj.flow_termination_keywords = '{"items": ["stop"]}'
        bot_obj.save()
        category_obj = Category.objects.create(
            name="testcategory", bot=bot_obj)
        bot_response_obj = BotResponse.objects.create(
            sentence='{"items": [{"text_response": "Hi! How may I assist you?", "speech_response": "Hi! How may I assist you?", "text_reprompt_response": "Hi! How may I assist you?", "speech_reprompt_response": "Hi! How may I assist you?"}]}', modes_param='{"choosen_file_type": ".png"}', modes='{"is_typable": "true", "is_attachment_required": "true", "is_button": "true", "is_slidable": "false", "is_date": "false", "is_dropdown": "false"}')
        tree_obj = Tree.objects.create(
            name="Parent", response=bot_response_obj)
        intent_obj = Intent.objects.create(
            name="Parent", tree=tree_obj, is_authentication_required=False, is_feedback_required=True, keywords='{"0": "hey", "1": "hlo", "2": "hi", "3": "whats"}', training_data='{"0": "Hey", "1": "hlo", "2": "hi", "3": "whats up"}', category=category_obj)
        intent_obj.bots.add(bot_obj)
        intent_obj.channels.add(web_channel)
        intent_obj.save()
        tree_child_obj = Tree.objects.create(
            name="children", response=bot_response_obj)
        tree_obj.children.add(tree_child_obj)

        easychat_user = Profile.objects.create(user_id="test123")
        easychat_user.tree = tree_child_obj
        easychat_user.save()

        save_data(easychat_user, {
            "easychat_abort_flow_initiated": "true"}, None, web_channel, bot_obj.pk, is_cache=True)
        save_data(easychat_user, {
            "easychat_abort_flow_previous_tree": easychat_user.tree.pk}, None, web_channel, bot_obj.pk, is_cache=True)

        save_data(easychat_user, {
            "easychat_abort_flow_called_intent": intent_obj.pk}, None, web_channel, bot_obj.pk, is_cache=True)

        save_data(easychat_user, {
            "easychat_abort_flow_message": "yes"}, None, web_channel, bot_obj.pk, is_cache=True)

        easychat_bot_user = EasyChatBotUser(
            bot_obj=bot_obj, channl_name=web_channel.name, src="en", bot_id=bot_obj.pk)
        channel_params = {"entered_suggestion": False}
        easychat_params = EasyChatChannelParams(
            channel_params, easychat_user.user_id)
        logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                        'source': 'None', 'channel': 'None', 'bot_id': 'None'}
        channel_obj = get_channel_obj(
            str(web_channel.name), Channel, logger_extra)
        easychat_params.channel_obj = channel_obj
        easychat_params.channel_name = channel_obj.name

        user, tree, easychat_abort_flow_initiated = return_tree_if_flow_aborted(
            "yes", easychat_user, easychat_bot_user, easychat_params)
        self.assertEqual(tree, tree_obj)

        save_data(user, {
            "easychat_abort_flow_initiated": "false"}, None, web_channel, bot_obj.pk, is_cache=True)

        user, tree, easychat_abort_flow_initiated = return_tree_if_flow_aborted(
            "yes", easychat_user, easychat_bot_user, easychat_params)

        self.assertEqual(tree, None)

    def test_process_speech_response(self):
        print("\n\nTesting process_speech_response")

        speech_response = """<speak><voice name="en-IN-NeerjaNeural">This is test</voice></speak>"""
        speech_response = process_speech_response(speech_response)
        self.assertEqual(speech_response, "This is test")

        speech_response = """Normal Text"""
        speech_response = process_speech_response(speech_response)
        self.assertEqual(speech_response, "Normal Text")

    def test_validate_speed_and_pitch_values(self):
        print("\n\nTesting validate_speed_and_pitch_values")

        provider = "Microsoft"
        speaking_speed = 1
        pitch = 1
        response = validate_speed_and_pitch_values(
            provider, speaking_speed, pitch)
        self.assertEqual(response, None)

        speaking_speed = -10
        response = validate_speed_and_pitch_values(
            provider, speaking_speed, pitch)
        self.assertEqual(
            response, "Please enter a valid Speaking Speed Value!")

        speaking_speed = 1
        pitch = 100
        response = validate_speed_and_pitch_values(
            provider, speaking_speed, pitch)
        self.assertEqual(response, "Please enter a valid Pitch Value!")

    def test_get_selected_tts_provider_name(self):
        print("\n\nTesting test_get_selected_tts_provider_name")

        bot_obj = Bot.objects.get(name="UnitTestBot")
        channel = Channel.objects.create(name="Voice")
        BotChannel.objects.create(bot=bot_obj, channel=channel)
        selected_tts_provider = get_selected_tts_provider_name(
            bot_obj, BotChannel)

        self.assertEqual(selected_tts_provider, "Microsoft")

    def test_check_two_minute_bot_welcome_message(self):
        print("\n\nTesting check_two_minute_bot_welcome_message")

        invalid_status, invalid_message, _ = check_two_minute_bot_welcome_message("")

        self.assertEqual(invalid_status, 400)
        self.assertEqual(invalid_message, "Welcome message is either empty or invalid")

        valid_status, valid_message, _ = check_two_minute_bot_welcome_message("<p>Hi, I am Iris, a Virtual Assistant.</p>")

        self.assertEqual(valid_status, 200)
        self.assertEqual(valid_message, "")
    
    def test_get_intent_obj_from_tree_obj(self):

        print("\n\nTesting get_intent_obj_from_tree_obj")
        tree_obj = Tree.objects.filter(is_deleted=True).first()
        response = get_intent_obj_from_tree_obj(tree_obj)
        self.assertEqual(response, None)
        
        tree_obj = Intent.objects.filter(is_deleted=False).first().tree
        response = get_intent_obj_from_tree_obj(tree_obj)
        self.assertNotEqual(response, None)

    def test_get_parent_tree_obj(self):

        print("\n\nTesting get_parent_tree_obj")
        tree_obj = Tree.objects.filter(is_deleted=True).first()
        response = get_parent_tree_obj(tree_obj)
        self.assertEqual(response, None)

        from django.db.models import Count
        
        tree_obj = Tree.objects.annotate(num_childrens=Count('children')).filter(is_deleted=False, num_childrens__gt=0).first().children.all().first()
        response = get_parent_tree_obj(tree_obj)
        self.assertNotEqual(response, None)
