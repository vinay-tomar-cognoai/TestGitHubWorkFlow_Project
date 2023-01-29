# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils import timezone
import logging
import json
import hashlib
import string
import random
import uuid
from datetime import date
from django.test import TestCase
from datetime import datetime, timedelta
from LiveChatApp.utils_validation import LiveChatInputValidation
from EasyChatApp.models import Bot, User, MISDashboard, Profile, Channel, Intent
from LiveChatApp.models import LiveChatCobrowsingData, LiveChatInternalChatGroup, LiveChatInternalChatGroupMembers, LiveChatInternalMISDashboard, LiveChatInternalMessageInfo, LiveChatInternalUserGroup, LiveChatUser, LiveChatCustomer, LiveChatCategory, LiveChatCalender, LiveChatConfig,\
    LiveChatMISDashboard, LiveChatAdminConfig, LiveChatVideoConferencing, LiveChatTransferAudit, CannedResponse,\
    LiveChatAuditTrail, LiveChatSessionManagement, LiveChatBlackListKeyword, LiveChatAgentNotReady, LiveChatTranslationCache, LiveChatFollowupCustomer
from LiveChatApp.utils import check_and_update_user_group, get_blacklisted_keyword_for_current_agent,\
    get_chat_duration_list, get_cobrowsing_data_history_objects, get_cobrowsing_info_based_agent, get_cobrowsing_info_based_guest_agent, get_cobrowsing_request_text, get_milliseconds_to_datetime,\
    get_month_list, check_for_holiday, check_for_non_working_hour, parse_cobrowsing_history_object_list, remove_agent_from_prev_groups,\
    save_audit_trail_data, check_and_add_admin_config, save_session_details, get_livechat_category_object,\
    get_time, get_miniseconds_datetime, get_audit_objects, get_trailing_list, get_livechat_date_format,\
    get_livechat_request_packet_to_channel, add_supervisor, get_chat_status,\
    get_year_list, get_priority_list, update_message_history_till_now, save_transfer_audit,\
    generate_random_password, get_date, set_livechat_session_in_profile, get_number_of_day, check_and_update_based_on_event_type,\
    is_agent_live, get_allowed_livechat_user, get_agent_token,\
    get_admin_from_active_agent, get_admin_config, get_message_history, get_sender_name, get_one_previous_message,\
    get_agents_under_this_user, mask_pii_data, get_masked_data, check_if_livechat_only_admin, check_agent_has_bot_assign_category,\
    get_canned_response_for_current_agent, check_for_system_commands, get_cobrowsing_status, update_followup_lead_message_history,\
    store_keyword_for_livechat_intent, check_if_whatsapp_keyword_present_in_intent, get_phone_number_and_country_code,\
    get_agents_as_per_supervisors
from LiveChatApp.utils_translation import get_translated_message_history, get_translated_text, translat_via_api
from LiveChatApp.utils_calendar import get_prev_month, get_next_month, convert_to_calender

logger = logging.getLogger(__name__)


"""
Test of All functions which are dependent on models
"""


class UtilsSomeFunctionsWithModels(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'LiveChat'})
        LiveChatConfig.objects.create(max_customer_count=110)
        Channel.objects.create(name='Web')
        Channel.objects.create(name='GoogleHome')
        Channel.objects.create(name='Alexa')
        Channel.objects.create(name='WhatsApp')
        Channel.objects.create(name='Android')
        Channel.objects.create(name='Facebook')
        Channel.objects.create(name='Microsoft')
        Channel.objects.create(name='Telegram')
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")

        Profile.objects.create(user_id="919087654321", bot=bot_obj)

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
            role="1", status="1", username="test1234", password="test1234"), last_updated_time=datetime.now())
        livechat_agent.bots.add(bot_obj)
        livechat_agent.save()
        livechat_supervisor = LiveChatUser.objects.create(
            status="2", user=User.objects.create(role="1", status="1", username="testsupervisor", password="test1234"), last_updated_time=datetime.now().replace(hour=1))
        livechat_supervisor.agents.add(livechat_agent)
        livechat_supervisor.bots.add(bot_obj)
        livechat_supervisor.save()
        livechat_admin.agents.add(livechat_supervisor)
        livechat_admin.save()
        group1 = LiveChatInternalChatGroup.objects.create(
            group_name='test_group', group_description='test group', created_by=livechat_admin)
        member1 = LiveChatInternalChatGroupMembers.objects.create(
            user=livechat_agent, group=group1)
        member2 = LiveChatInternalChatGroupMembers.objects.create(
            user=livechat_supervisor, group=group1)
        group1.members.add(member1)
        group1.members.add(member2)
        group2 = LiveChatInternalChatGroup.objects.create(
            group_name='test_group1', group_description='test group', created_by=livechat_admin)
        member1 = LiveChatInternalChatGroupMembers.objects.create(
            user=livechat_agent, group=group2)
        group2.members.add(member1)

    """
    function tested: is_agent_live
    input queries:
        list of livechat agent objects
    expected output:
        returns True for those agents, who are live, False otherwise.
    checks for:
        1. If the difference between current time and last seen of agent is at most 30 seconds, then agent is assumed to be live.
    """

    def test_is_agent_live(self):
        livechat_agents = LiveChatUser.objects.filter(status="3")

        expected_responses = [False, True]
        corrected_queries = []

        for agent in livechat_agents:
            corrected_queries.append(is_agent_live(agent))

        self.assertEqual(expected_responses, corrected_queries)

    """
    function: validate_password
    input params:
        password: 
    expected output:
        returns True if password is valid else False
    """

    def test_validate_password(self):
        logger.info("Testing of test_validate_password is going on.",
                    extra={'AppName': 'LiveChat'})
        print("\n\n\nTesting of test_validate_password is going on.\n")

        validation_obj = LiveChatInputValidation()

        password = "testing sdhj"
        self.assertEqual(validation_obj.validate_password(password), False)
        password = "  345678,kjd**"
        self.assertEqual(validation_obj.validate_password(password), False)
        password = "  345678,kjd**"
        self.assertEqual(validation_obj.validate_password(password), False)
        password = "  345678,kjd**"
        self.assertEqual(validation_obj.validate_password(password), False)
        password = "testing123456"
        self.assertEqual(validation_obj.validate_password(password), True)

    """
    function: test_set_livechat_session_in_profile
    input params:
        livechat_session_id:
        channel_name:
        phone:
    expected output:
        This function is used to add updated livechat session in easychat Profile object
    """

    def test_set_livechat_session_in_profile(self):
        logger.info("Testing of set_livechat_session_in_profile is going on.",
                    extra={'AppName': 'LiveChat'})
        print("\n\n\nTesting of set_livechat_session_in_profile is going on.\n")

        channels = Channel.objects.all()
        livechat_session_id = "yvsd6217bdf0wskjhsdhvsdsdfds"
        bot_obj = Bot.objects.get(pk=1)

        for channel in channels:
            profile_obj = Profile.objects.get(pk=1)
            set_livechat_session_in_profile(
                livechat_session_id, channel.name, profile_obj.user_id, bot_obj, Profile)

            profile_obj = Profile.objects.get(pk=1)

            if channel.name != "WhatsApp":
                self.assertEqual(profile_obj.livechat_connected, False)
                self.assertEqual(profile_obj.livechat_session_id, None)
            else:
                self.assertEqual(profile_obj.livechat_connected, True)
                self.assertEqual(profile_obj.livechat_session_id,
                                 "yvsd6217bdf0wskjhsdhvsdsdfds")
                profile_obj.livechat_connected = False
                profile_obj.livechat_session_id = None
                profile_obj.save()

    """
    function: get_number_of_day
    input params:
        year:
        month:
    expected output:
        1. Provides number of days in a month of a perticular year.
    """

    def test_get_number_of_day(self):
        logger.info("Testing of get_number_of_day is going on.",
                    extra={'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_number_of_day is going on.\n")

        self.assertEqual(get_number_of_day(2020, 1), 31)
        self.assertEqual(get_number_of_day(20200, 2), 28)
        self.assertEqual(get_number_of_day(202000, 2), 29)
        self.assertEqual(get_number_of_day(2020, 2), 29)
        self.assertEqual(get_number_of_day(2021, 11), 30)

    """
    function: check_and_update_based_on_event_type
    input params:
        user:
        calender_obj:
        selected_event:
        start_time:
        end_time:
        description: description of event
        auto_response: auto response will be given to livechat customer on this day.
    expected output:
        1. If user is manager, but the event was created by admin, then this function will create new calender object with modified by manager.
           Current manager will be removed from admin's event object.
        2. If user is admin, then this event will be updated based on event type.
    """

    def test_check_and_update_based_on_event_type(self):
        logger.info("Testing of check_and_update_based_on_event_type is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of check_and_update_based_on_event_type is going on.\n")

        user = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))
        calender_obj = LiveChatCalender.objects.create(
            event_type="2", created_by=user, description="Testing", auto_response="This is testing.", event_date=datetime.now())

        check_and_update_based_on_event_type(
            user, calender_obj, "2", "", "", "TestingAllinCall", "This is testing.")
        calender_obj = LiveChatCalender.objects.get(pk=1)
        self.assertEqual(calender_obj.description, "TestingAllinCall")

        supervisor = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))

        check_and_update_based_on_event_type(
            supervisor, calender_obj, "2", "", "", "Testingsupervisor", "This is testing.")
        calender_obj = LiveChatCalender.objects.get(pk=1)
        self.assertEqual(calender_obj.description, "TestingAllinCall")

        check_and_update_based_on_event_type(
            user, calender_obj, "1", datetime.now().time(), datetime.now().time(), "TestingAdminAllinCall", "This is testing.")

        calender_obj = LiveChatCalender.objects.get(pk=1)
        self.assertEqual(calender_obj.event_type, "1")

    def test_remove_agent_from_prev_groups(self):
        logger.info("Testing of remove_agent_from_prev_groups is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of remove_agent_from_prev_groups is going on.\n")

        admin = LiveChatUser.objects.get(user__username='testadmin')
        supervisor = LiveChatUser.objects.get(user__username='testsupervisor')
        agent = LiveChatUser.objects.get(user__username='test1234')

        remove_agent_from_prev_groups(admin, agent, supervisor, LiveChatInternalChatGroup,
                                      LiveChatInternalChatGroupMembers, LiveChatInternalMessageInfo, LiveChatInternalMISDashboard)

        group_count = LiveChatInternalChatGroupMembers.objects.filter(
            user=agent, is_removed=False).count()

        self.assertEqual(group_count, 1)


class UtilsSomeFunctionsSectionTwo(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'LiveChat'})
        LiveChatConfig.objects.create(max_customer_count=110)
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        category_obj = LiveChatCategory.objects.create(
            title="others", bot=bot_obj)

        MISDashboard.objects.create(
            user_id="1", bot=bot_obj, message_received="hi", bot_response="how may I assist you?")
        MISDashboard.objects.create(
            user_id="2", bot=bot_obj, message_received="hi", bot_response="how may I assist you?")
        MISDashboard.objects.create(user_id="4", bot=bot_obj, message_received="hi",
                                    bot_response="how may I assist you?", date=datetime.now().replace(hour=23))
        MISDashboard.objects.create(
            user_id="4", bot=bot_obj, message_received="Hi", bot_response="hello")

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
        livechat_supervisor = LiveChatUser.objects.create(
            status="2", user=User.objects.create(role="1", status="1", username="testsupervisor", password="test1234"), last_updated_time=datetime.now().replace(hour=1))
        livechat_supervisor.agents.add(livechat_agent)
        livechat_supervisor.bots.add(bot_obj)
        livechat_supervisor.save()
        livechat_admin.agents.add(livechat_supervisor)
        livechat_admin.save()

        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=10, chat_duration=10, queue_time=5, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj,
                                        is_session_exp=True, joined_date=datetime.now(), wait_time=2, chat_duration=10, queue_time=7, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj,
                                        is_session_exp=True, joined_date=datetime.now(), wait_time=3, chat_duration=10, queue_time=8, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), wait_time=20, chat_duration=100, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), wait_time=10, chat_duration=100, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), wait_time=20, chat_duration=100, bot=bot_obj)
        livechat_customer = LiveChatCustomer.objects.create(username="testcust1", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                                            joined_date=datetime.now() - timedelta(days=8), wait_time=30, chat_duration=100, bot=bot_obj)

        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Customer", sender_name=livechat_customer.username, text_message="cust_message")

        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Agent", sender_name="test_agent", text_message="agent_message")

        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Agent", sender_name="test_agent", text_message="1234567891113")

        livechat_customer = LiveChatCustomer.objects.create(username="testcust2", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                                            joined_date=datetime.now() - timedelta(days=8), wait_time=30, chat_duration=100, bot=bot_obj)

        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Agent", sender_name="test_agent", text_message="abcd")

        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Customer", sender_name=livechat_customer.username, text_message="efgh")

        livechat_customer = LiveChatCustomer.objects.create(username="testcust3", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                                            joined_date=datetime.now() - timedelta(days=8), wait_time=30, chat_duration=100, bot=bot_obj)

        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Agent", sender_name="test_agent", text_message="abcd")

        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Customer", sender_name=livechat_customer.username, text_message="efgh")
        livechat_customer.chat_ended_by = "Customer"
        livechat_customer.save()

        livechat_customer = LiveChatCustomer.objects.create(username="test_masking", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                                            joined_date=datetime.now() - timedelta(days=8), wait_time=30, chat_duration=100, bot=bot_obj)

        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Customer", sender_name=livechat_customer.username, text_message="my pan number is BWNPG1234F")
        livechat_customer.chat_ended_by = "Agent"
        livechat_customer.save()

        LiveChatAdminConfig.objects.create(admin=livechat_admin)

        LiveChatVideoConferencing.objects.create(agent=livechat_agent, meeting_start_date=datetime.now() - timedelta(days=1),
                                                 meeting_start_time=datetime.now() - timedelta(hours=2), meeting_end_time=datetime.now() - timedelta(hours=1))

        livechat_agent = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="test1", password="test1234"))
        livechat_agent.bots.add(bot_obj)
        livechat_agent.save()

        LiveChatVideoConferencing.objects.create(agent=livechat_agent, meeting_start_date=datetime.now().date(),
                                                 meeting_start_time=datetime.now() - timedelta(hours=2), meeting_end_time=datetime.now())

        livechat_agent = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="test2", password="test1234"))
        livechat_agent.bots.add(bot_obj)
        livechat_agent.save()

        LiveChatVideoConferencing.objects.create(agent=livechat_agent, meeting_start_date=datetime.now(),
                                                 meeting_start_time=datetime.now() - timedelta(hours=2), meeting_end_time=datetime.now() - timedelta(hours=1))

    def test_get_agents_under_this_user(self):
        logger.info("Testing of get_agents_under_this_user is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_agents_under_this_user is going on.\n")
        user = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))

        allowed_user = get_agents_under_this_user(user)
        self.assertEqual(len(allowed_user), 1)

        user = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))

        allowed_user = get_agents_under_this_user(user)
        self.assertEqual(len(allowed_user), 3)

        user = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234"))

        allowed_user = get_agents_under_this_user(user)
        self.assertEqual(len(allowed_user), 1)

    """
    function: validate_name
    input params:
        name: name of agent

    returns true if name is valid else false
    """

    def test_validate_name(self):
        logger.info("Testing of validate_name is going on", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of validate_name is going on.\n")

        names = ["test", "test1234", "a", "TEST", "CAPITALLETTERSsmallletters",
                 "firstName LastName", "@#$%", "name_with_special_chars_@#$%^&*()", "very long name more than 30 char should not be allowed "]

        expected_response = [True, False, False,
                             True, True, True, False, False, False]

        actual_response = []

        validation_obj = LiveChatInputValidation()

        for name in names:
            actual_response.append(validation_obj.validate_name(name))

        self.assertEqual(actual_response, expected_response)

    """
    function: validate_email
    input params:
        email: email of agent

    returns true if email is valid else false
    """

    def test_validate_email(self):
        logger.info("Testing of validate_email is going on", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of validate_email is going on.\n")

        emails = ["testingemail@gmail.com", "123.testing.abcd@abcd.in", "abcd", "aaa2aaa1@gmail.com",
                  "gmail@gmail.com", "xxx_xx_x@gmail.com", "abcd@gmail.efgh", "abcd@efgh@gmail.com", "abc@def.123"]

        expected_response = [True, True, False, True, True, True, True, False, False]

        actual_response = []

        validation_obj = LiveChatInputValidation()

        for email in emails:
            actual_response.append(validation_obj.validate_email(email))

        self.assertEqual(actual_response, expected_response)

    """
    function: validate_phone_number
    input params:
        phone: phone number of agent
    returns true if phone number is valid else false
    """

    def test_validate_phone_number(self):
        logger.info("Testing of validate_phone_number is going on", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of validate_phone_number is going on.\n")

        phone_numbers = ["9876543210", "9876543109876543210", "0123456789",
                         "1234567890", "6876543100", "12345", "9876", "0987654321"]

        expected_response = [True, False, False,
                             False, True, False, False, False]

        actual_response = []

        validation_obj = LiveChatInputValidation()

        for phone_number in phone_numbers:
            actual_response.append(
                validation_obj.validate_phone_number(phone_number))

        self.assertEqual(actual_response, expected_response)

    """
    function: get_agent_token
    input params:
        username: username of agent

    This function is used to generate hash of current agent. And this has is used for creating room for current agent.
    """

    def test_get_agent_token(self):
        logger.info("Testing of get_agent_token is going on", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_agent_token is going on.\n")

        usernames = ["abcd", "username", "test", "test2", "tech",
                     "agent", "somebody@allincall.in", "abcd@gmail.com"]
        expected_response = []
        actual_response = []

        for username in usernames:
            expected_response.append(
                hashlib.md5(username.encode()).hexdigest())
            actual_response.append(get_agent_token(username))

        # self.assertEqual(actual_response, expected_response)

    """

    function: test_get_livechat_category_object
    input params:
        category_pk: pk of category object
    output:
        returns category object

    This function returns category object. If category pk is -1, then it creates a category with title "Others" and returns this object.

    """

    def test_get_livechat_category_object(self):

        category_obj = get_livechat_category_object(
            "-1", Bot.objects.get(pk=1), LiveChatCategory)
        self.assertEqual(category_obj.title, "others")
        category_obj = get_livechat_category_object(
            "1", Bot.objects.get(pk=1), LiveChatCategory)
        self.assertEqual(category_obj.title, "others")
        LiveChatCategory.objects.create(
            title="Testing", bot=Bot.objects.get(pk=1))
        category_obj = get_livechat_category_object(
            "2", Bot.objects.get(pk=1), LiveChatCategory)

        self.assertEqual(category_obj.title, "Testing")

    """
    function: get_message_history
    input params:
        livechat_cust_obj: LiveChatCustomer
        
    It returns message history of livechat_cust_obj as a json.
    """

    def test_get_message_history(self):
        logger.info("Testing of get_message_history is going on", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_message_history is going on.\n")

        customer = LiveChatCustomer.objects.filter(username="test")[0]

        message_history = get_message_history(customer, False, LiveChatMISDashboard, LiveChatTranslationCache)

        self.assertEqual(len(message_history), 0)

        customer = LiveChatCustomer.objects.filter(username="testcust1")[0]

        message_history = get_message_history(customer, False, LiveChatMISDashboard, LiveChatTranslationCache)

        self.assertEqual(len(message_history), 3)

        customer = LiveChatCustomer.objects.filter(username="testcust2")[0]

        message_history = get_message_history(customer, False, LiveChatMISDashboard, LiveChatTranslationCache)

        self.assertEqual(len(message_history), 2)

    """

    function: get_sender_name
    input params:
        customer_obj: LiveChatCustomer object
    output:
        returns message sender name

    This function returns name of last message sender.

    """

    def test_get_sender_name(self):
        logger.info("Testing of get_sender_name", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_sender_name is going on.\n")

        customer = LiveChatCustomer.objects.filter(username="testcust1")[0]

        senders_name = get_sender_name(customer, LiveChatMISDashboard)

        self.assertEqual(senders_name, "test_agent")

        customer = LiveChatCustomer.objects.filter(username="testcust2")[0]

        senders_name = get_sender_name(customer, LiveChatMISDashboard)

        self.assertEqual(senders_name, "testcust2")

    def test_get_one_previous_message(self):
        logger.info("Testing of get_agent_token is going on", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_one_previous_message is going on.\n")

        admin = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))

        admin_config_obj = get_admin_config(
            admin, LiveChatAdminConfig, LiveChatUser)

        customer = LiveChatCustomer.objects.filter(username="test")[0]
        one_prev_message = get_one_previous_message(
            customer, admin_config_obj, LiveChatMISDashboard)

        self.assertEqual(one_prev_message["text_message"], "")

        customer = LiveChatCustomer.objects.filter(username="testcust1")[0]
        prev_message = get_one_previous_message(
            customer, admin_config_obj, LiveChatMISDashboard)

        self.assertEqual(prev_message["text_message"], "1234567891113")
        self.assertEqual(prev_message["is_attachment"], "False")
        self.assertEqual(prev_message["sender"], "Agent")

        customer = LiveChatCustomer.objects.filter(username="testcust2")[0]
        prev_message = get_one_previous_message(
            customer, admin_config_obj, LiveChatMISDashboard)

        self.assertEqual(prev_message["text_message"], "efgh")
        self.assertEqual(prev_message["is_attachment"], "False")
        self.assertEqual(prev_message["sender"], "Customer")

        customer = LiveChatCustomer.objects.filter(username="testcust3")[0]
        prev_message = get_one_previous_message(
            customer, admin_config_obj, LiveChatMISDashboard)

        self.assertEqual(
            prev_message["text_message"], "Customer left the chat")

    def test_get_admin_from_active_agent(self):
        logger.info("Testing of get_admin_from_active_agent", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_sender_name is going on.\n")

        user = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))
        admin = get_admin_from_active_agent(user, LiveChatUser)

        self.assertEqual(admin.user.username, "testadmin")

        user = LiveChatUser.objects.get(
            user=User.objects.get(username="test"))

        admin = get_admin_from_active_agent(user, LiveChatUser)

        self.assertEqual(admin.user.username, "testadmin")

        user = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))

        admin = get_admin_from_active_agent(user, LiveChatUser)

        self.assertEqual(admin.user.username, "testadmin")

    """
    function: get_admin_config
    input params:
        livechat_user: LiveChat user

    It returns the LiveChatAdminConfig object for a particular agent.
    """

    def test_get_admin_config(self):
        logger.info("Testing of get_admin_config is going on", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_admin_config  \n")

        admin = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))

        admin_config_obj = get_admin_config(
            admin, LiveChatAdminConfig, LiveChatUser)

        self.assertEqual(admin_config_obj.admin.user.username, "testadmin")

        agent = LiveChatUser.objects.get(
            user=User.objects.get(username="test"))

        admin_config_obj = get_admin_config(
            agent, LiveChatAdminConfig, LiveChatUser)

        self.assertEqual(admin_config_obj.admin.user.username, "testadmin")

        """
    function: mask_pii_data
    input params:
        livechat_cust_obj: LiveChatCustomer
        
    It returns message history of livechat_cust_obj as a json.
    """

    def test_mask_pii_data(self):
        logger.info("Testing of mask_pii_data is going on", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of mask_pii_data is going on.\n")

        customer = LiveChatCustomer.objects.filter(username="test_masking")[0]

        masked_msg = 'my pan number is 935be9e2d64660e2c9827ea601a1d725897ca5cb956becc134cf43393d9cff1d'
        mask_pii_data(customer, LiveChatMISDashboard)

        mis_obj = LiveChatMISDashboard.objects.filter(
            livechat_customer=customer)[0]
        message = mis_obj.text_message

        self.assertEqual(message, masked_msg)


"""
Test of All functions which are independent of models
"""


class UtilsFunctionsSectionThree(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'LiveChat'})
        LiveChatConfig.objects.create(max_customer_count=110)
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        category_obj = LiveChatCategory.objects.create(
            title="others", bot=bot_obj)

        MISDashboard.objects.create(
            user_id="1", bot=bot_obj, message_received="hi", bot_response="how may I assist you?")
        MISDashboard.objects.create(
            user_id="2", bot=bot_obj, message_received="hi", bot_response="how may I assist you?")
        MISDashboard.objects.create(user_id="4", bot=bot_obj, message_received="hi",
                                    bot_response="how may I assist you?", date=datetime.now().replace(hour=23))
        MISDashboard.objects.create(
            user_id="4", bot=bot_obj, message_received="Hi", bot_response="hello")
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
        livechat_supervisor = LiveChatUser.objects.create(
            status="2", user=User.objects.create(role="1", status="1", username="testsupervisor", password="test1234"), last_updated_time=datetime.now().replace(hour=1))
        livechat_supervisor.agents.add(livechat_agent)
        livechat_supervisor.bots.add(bot_obj)
        livechat_supervisor.save()
        livechat_admin.agents.add(livechat_supervisor)
        livechat_admin.save()
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=10, chat_duration=10, queue_time=5, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj,
                                        is_session_exp=True, joined_date=datetime.now(), wait_time=2, chat_duration=10, queue_time=7, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj,
                                        is_session_exp=True, joined_date=datetime.now(), wait_time=3, chat_duration=10, queue_time=8, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), request_raised_date=(datetime.now() - timedelta(days=8)).date(), wait_time=20, chat_duration=100, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), request_raised_date=(datetime.now() - timedelta(days=8)).date(), wait_time=10, chat_duration=100, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), request_raised_date=(datetime.now() - timedelta(days=8)).date(), wait_time=20, chat_duration=100, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), request_raised_date=(datetime.now() - timedelta(days=8)).date(), wait_time=30, chat_duration=100, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test2", agent_id=livechat_agent, category=category_obj, is_session_exp=False,
                                        joined_date=datetime.now(), wait_time=30, chat_duration=10, bot=bot_obj)

    """
    function tested: test_get_chat_status
    input params:
        milliseconds:
    expected output:
        This function is used to get chat status (online/offline).
    """

    def test_get_chat_status(self):
        logger.info("Testing get chat status...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get chat status...\n")

        status = None
        chat_status = get_chat_status(status)
        self.assertEqual(None, chat_status)

        status = "0"
        chat_status = get_chat_status(status)
        self.assertEqual(None, chat_status)

        status = "1"
        chat_status = get_chat_status(status)
        self.assertEqual(False, chat_status)

        status = "2"
        chat_status = get_chat_status(status)
        self.assertEqual(True, chat_status)

    """
    function tested: test_get_chat_duration_start_end
    input params:
        chat_duration:
    expected output:
        This function is used to get chat duration.
    """

    """
    function tested: get_audit_objects
    input params:
        query_user_obj: user objects selected during applying filter
        agent_username: agent username selected during applying filter
        chat_status: Online/Offline(1/2)
        chat_duration:
        datetime_start:
        datetime_end
    expected output:
        This function is used to find LiveChatCustomer objects for a given interval with given chat duration.
    """

    def test_get_audit_objects(self):
        logger.info("Testing of get_audit_objects is going on.",
                    extra={'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_audit_objects is going on.\n")

        from datetime import timedelta
        datetime_end = datetime.now()
        datetime_start = datetime.now() - timedelta(days=1)

        livechat_customer_list = LiveChatCustomer.objects.all()
        livechat_followup_cust_objs = LiveChatFollowupCustomer.objects.all()
        query_user_obj = LiveChatUser.objects.all()[0]
        agent_list = LiveChatUser.objects.all()

        audit_obj_list = get_audit_objects(
            agent_list, "0", datetime_start.date(), datetime_end.date(), livechat_customer_list, 'All', None, 0, None, None, livechat_followup_cust_objs)

        self.assertEqual(len(audit_obj_list), 5)

        audit_obj_list = get_audit_objects(
            agent_list, "0", (datetime_end + timedelta(days=1)).date(), (datetime_end + timedelta(days=2)).date(), livechat_customer_list, 'All', None, 0, None, None, livechat_followup_cust_objs)

        self.assertEqual(len(audit_obj_list), 0)

        audit_obj_list = get_audit_objects(
            [query_user_obj], "1", datetime_start.date(), datetime_end.date(), livechat_customer_list, 'All', None, 2, None, None, livechat_followup_cust_objs)

        self.assertEqual(len(audit_obj_list), 0)

        audit_obj_list = get_audit_objects(
            [query_user_obj], "1", datetime_start.date(), datetime_end.date(), livechat_customer_list, 'All', None, 0, None, None, livechat_followup_cust_objs)

        self.assertEqual(len(audit_obj_list), 0)

        query_user_obj = LiveChatUser.objects.all()[0]
        audit_obj_list = get_audit_objects(
            [query_user_obj], "2", datetime_start.date(), datetime_end.date(), livechat_customer_list, 'All', None, 0, None, None, livechat_followup_cust_objs)

        self.assertEqual(len(audit_obj_list), 0)

    """
    function: get_trailing_list
    input_params:
        current_history_id: the id related to the history on which the user currently is(modal state open). 
        audit_obj_list: audit_obj_list complete 
        AUDIT_TRAIL_ITEM_COUNT: Item count per page,
        audit_obj_list_final: audit_object_list after pagination on current page,
        page: page open in back ground of modal,
        total_pages: total no. of pages.
    Returns the complete list of maximum (AUDIT_TRAIL_ITEM_COUNT*3) objects of audit_objs.
    """

    def test_get_trailing_list(self):
        logger.info("Testing of get_trailing_list is going on.",
                    extra={'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_trailing_list is going on.\n")

        from datetime import timedelta
        datetime_end = datetime.now()
        datetime_start = datetime.now() - timedelta(days=1)

        livechat_customer_list = LiveChatCustomer.objects.all()
        livechat_followup_cust_objs = LiveChatFollowupCustomer.objects.all()
        agent_list = LiveChatUser.objects.all()

        audit_obj_list = get_audit_objects(
            agent_list, "0", datetime_start.date(), datetime_end.date(), livechat_customer_list, 'All', None, 0, None, None, livechat_followup_cust_objs)

        trailing_list = get_trailing_list(
            '', audit_obj_list, 10, audit_obj_list, 1, 1)

        self.assertEqual(len(audit_obj_list), 5)
        self.assertEqual(len(trailing_list), 5)

    """
    function tested: get_miniseconds_datetime
    input params:
        input_date:
    expected output:
        This function is used to find total number of milli seconds for a perticular datetime object
    """

    def test_get_miniseconds_datetime(self):
        logger.info("Testing get miniseconds datetime...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get miniseconds datetime...\n")

        input_date = date(1970, 1, 1)
        total_seconds = get_miniseconds_datetime(input_date)
        self.assertEqual(0, total_seconds)

    """
    function tested: remo_html_from_string
    input queries:
        queries containing some html tags
    expected output:
        queries without html tags
    checks for:
        same expected output and output from function tested
    """

    def test_remo_html_from_string(self):
        input_queries = ['<b>Tell me salary details</b>', '<hr>What is your name',
                         '<h1 >Show me loans', '<a href="www.google.com">']
        expected_responses = ['Tell me salary details',
                              'What is your name', 'Show me loans', '']
        removed_html_queries = []

        validation_obj = LiveChatInputValidation()

        for query in input_queries:
            corrected = validation_obj.remo_html_from_string(query)
            removed_html_queries.append(corrected)
        self.assertEqual(expected_responses, removed_html_queries)

    """
    function tested: remo_special_tag_from_string
    input queries:
        queries containing some special characters (+, |, -, =)
    expected output:
        queries without special characters
    checks for:
        same expected output and output from function tested
    """

    def test_remo_special_tag_from_string(self):
        input_queries = ['Tell me+salary-details', 'What is||your name',
                         'a==b', '4+5=10']
        expected_responses = ['Tell mesalarydetails',
                              'What isyour name', 'ab', '4510']
        removed_html_queries = []

        validation_obj = LiveChatInputValidation()

        for query in input_queries:
            corrected = validation_obj.remo_special_tag_from_string(query)
            removed_html_queries.append(corrected)
        self.assertEqual(expected_responses, removed_html_queries)

    """
    function tested: get_time
    input queries:
        list of datetime objects of different timing in a day
    expected output:
        should return the time in 12 hour system with proper AM and PM tag
    checks for:
        same expected output and output from function tested
    """

    def test_get_time(self):
        today_date = datetime.today()

        input_queries = [today_date.replace(hour=11, minute=59), today_date.replace(
            hour=23, minute=21), today_date.replace(hour=5, minute=17), today_date.replace(hour=16, minute=16)]
        expected_responses = ["11:59 AM", "11:21 PM", "05:17 AM", "04:16 PM"]

        set_time_list = []
        for query in input_queries:
            corrected = get_time(query)
            set_time_list.append(corrected)

        self.assertEqual(expected_responses, set_time_list)

    """
    function tested: get_year_list
    input:

    expected output:
        returns year list in key: value pair (2020-2031)
    checks for:
        same expected output and output from function tested
    """

    def test_get_year_list(self):
        expected_output = [{"key": "2020", "value": "2020"}, {"key": "2021", "value": "2021"}, {"key": "2022", "value": "2022"}, {"key": "2023", "value": "2023"}, {"key": "2024", "value": "2024"}, {"key": "2025", "value": "2025"}, {
            "key": "2026", "value": "2026"}, {"key": "2027", "value": "2027"}, {"key": "2028", "value": "2028"}, {"key": "2029", "value": "2029"}, {"key": "2030", "value": "2030"}, {"key": "2031", "value": "2031"}]

        output = get_year_list()
        self.assertEqual(expected_output, output)

    """
    function tested: get_priority_list
    input:

    expected output:
        returns priority list in key: value pair
    checks for:
        same expected output and output from function tested
    """

    def test_get_priority_list(self):
        expected_output = [{"key": "1", "value": "1"}, {"key": "2", "value": "2"}, {
            "key": "3", "value": "3"}, {"key": "4", "value": "4"}, {"key": "5", "value": "5"}]

        output = get_priority_list()
        self.assertEqual(expected_output, output)

    """
    function: update_message_history_till_now
    input params:
        livechat_cust_obj:
    output:

        This function create LiveChatMISDashboard objects of conversation between chatbot and user

    """

    def test_update_message_history_till_now(self):
        logger.info("Testing of update_message_history_till_now is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of update_message_history_till_now is going on.\n")

        livechat_cust_obj = LiveChatCustomer.objects.filter(username="test")[0]
        livechat_cust_obj.easychat_user_id = "1"
        livechat_cust_obj.save()

        update_message_history_till_now(
            livechat_cust_obj, LiveChatMISDashboard, MISDashboard)

        mis_objs = LiveChatMISDashboard.objects.filter(
            livechat_customer=livechat_cust_obj)

        self.assertEqual(
            mis_objs.count(), 3)

        livechat_cust_obj = LiveChatCustomer.objects.filter(username="test2")[
            0]
        livechat_cust_obj.easychat_user_id = "4"
        livechat_cust_obj.save()

        update_message_history_till_now(
            livechat_cust_obj, LiveChatMISDashboard, MISDashboard)

        mis_objs = LiveChatMISDashboard.objects.filter(
            livechat_customer=livechat_cust_obj)

        self.assertEqual(
            mis_objs.count(), 5)

    """
    function: update_followup_lead_message_history
    input params:
        livechat_cust_obj:
    output:

        This function create LiveChatMISDashboard objects of conversation between chatbot and followup lead

    """

    def test_update_followup_lead_message_history(self):
        logger.info("Testing of update_followup_lead_message_history is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of update_followup_lead_message_history is going on.\n")

        livechat_cust_obj = LiveChatCustomer.objects.filter(username="test")[0]
        livechat_cust_obj.easychat_user_id = "1"
        livechat_cust_obj.save()

        livechat_agent = LiveChatUser.objects.filter(status="3")[0]
        livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.create(
            livechat_customer=livechat_cust_obj, agent_id=livechat_agent, source="missed_chats", assigned_date=datetime.now())

        update_followup_lead_message_history(
            livechat_cust_obj, livechat_followup_cust_obj, LiveChatMISDashboard, MISDashboard)

        mis_objs = LiveChatMISDashboard.objects.filter(
            livechat_customer=livechat_cust_obj)

        self.assertEqual(
            mis_objs.count(), 3)

        livechat_cust_obj = LiveChatCustomer.objects.filter(username="test2")[
            0]
        livechat_cust_obj.easychat_user_id = "4"
        livechat_cust_obj.save()

        livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.create(
            livechat_customer=livechat_cust_obj, agent_id=livechat_agent, source="missed_chats", assigned_date=datetime.now())

        update_followup_lead_message_history(
            livechat_cust_obj, livechat_followup_cust_obj, LiveChatMISDashboard, MISDashboard)

        mis_objs = LiveChatMISDashboard.objects.filter(
            livechat_customer=livechat_cust_obj)

        self.assertEqual(
            mis_objs.count(), 5)

    """
    function: save_transfer_audit
    input params:
        chat_transferred_by: agent who transferred chat
        chat_transferred_to: agent to whom chat is transferred
        livechat_cust_obj: customer
    output:

        This function adds audit obj when chat is transferred

    """

    def test_save_transfer_audit(self):
        logger.info("Testing of save_transfer_audit is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of save_transfer_audit is going on.\n")

        chat_transferred_by = LiveChatUser.objects.get(
            user=User.objects.get(username='test1234'))
        chat_transferred_to = LiveChatUser.objects.get(
            user=User.objects.get(username='test'))
        livechat_cust_obj = LiveChatCustomer.objects.filter(username="test2")[
            0]
        transfer_description = ""

        save_transfer_audit(chat_transferred_by, chat_transferred_to,
                            livechat_cust_obj, transfer_description, LiveChatTransferAudit)

        livechat_transfer_objs = LiveChatTransferAudit.objects.all()

        self.assertEqual(
            livechat_transfer_objs.count(), 1)

    """
    function tested: generate_random_password
    input:

    expected output:
        returns randomly generated password of length 10 containing alphabets and numbers
    checks for:
        generated passwords are always unique
    """

    def test_generate_random_password(self):
        generated_passwords = []
        for _ in range(100):
            length = 10
            letters_and_digits = string.ascii_letters + string.digits
            result_str = ''.join((random.choice(letters_and_digits)
                                  for i in range(length)))

            generated_passwords.append(result_str)

        password = generate_random_password()

        self.assertEqual(len(password), 10)
        for generated_password in generated_passwords:
            self.assertNotEqual(generated_password, password)

    """
    function tested: get_date
    input queries:
        list of datetime objects of different timing in a day
    expected output:
        should return 'Yesterday' for yesterday's date, day name of week for date within
            that week, date for date before the week and time for today
    checks for:
        same expected output and output from function tested
    """

    def test_get_date(self):
        today_date = datetime.today()

        input_queries = [(today_date - timedelta(days=1)), (today_date - timedelta(days=2)), (today_date - timedelta(days=4)),
                         (today_date - timedelta(days=8)), (today_date.replace(hour=16, minute=16))]

        expected_responses = ["Yesterday", (today_date - timedelta(days=2)).strftime('%A'),
                              (today_date - timedelta(days=4)).strftime('%A'), (today_date - timedelta(days=8)).strftime('%d/%m/%Y'), "04:16 PM"]

        set_time_list = []
        for query in input_queries:
            corrected = get_date(query)
            set_time_list.append(corrected)

        self.assertEqual(expected_responses, set_time_list)


"""
Test of All functions which are independent of models
"""


class UtilsFunctionsWithoutModel(TestCase):

    def setUp(self):
        logger.info(
            "Setting up the test environment for UtilsFunctionsWithoutModels...", extra={'AppName': 'LiveChat'})

    """
    function tested: test_get_milliseconds_to_datetime
    input params:
        milliseconds:
    expected output:
        This function is used to convert milliseconds to datetime.
    """

    def test_get_milliseconds_to_datetime(self):
        logger.info("Testing get_milliseconds_to_datetime...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_milliseconds_to_datetime...\n")

        milliseconds = "1593188793000"
        date_obj = get_milliseconds_to_datetime(milliseconds)

        self.assertEqual("26-Jun-2020", date_obj)

    """
    function tested: test_get_livechat_request_packet_to_channel
    input queries:
        user_id:
        type:
        message:
        path:
        channel:
        bot_id:
    expected output:
        return response in json format
    """

    def test_get_livechat_request_packet_to_channel(self):
        logger.info("Testing get_livechat_request_packet_to_channel...", extra={
                    'AppName': 'LiveChat'})
        print("\nTesting get_livechat_request_packet_to_channel...\n")

        response = get_livechat_request_packet_to_channel(
            "test", "test1", "test2", "test3", "test4", "test5", "test6")

        response = json.loads(response)
        self.assertEqual(response["session_id"], "test")
        self.assertEqual(response["type"], "test1")
        self.assertEqual(response["text_message"], "test2")
        self.assertEqual(response["path"], "test3")
        self.assertEqual(response["channel"], "test4")
        self.assertEqual(response["bot_id"], "test5")
        self.assertEqual(response["agent_name"], "test6")

    """
    function tested: get_livechat_date_format
    input queries:
        datetime_obj:
    expected output:
        date_string: datetime as string in the format "DD-MM-YYYY" i.e. "01-May-2020"
    """

    def test_get_livechat_date_format(self):

        test_obj = datetime(2020, 5, 17)
        expected_response = "17-May-2020"
        correct_response = get_livechat_date_format(test_obj)
        self.assertEqual(expected_response, correct_response)

    """
    function tested: get_time
    input queries:
        list of datetime objects of different timing in a day
    expected output:
        should return the time in 12 hour system with proper AM and PM tag
    checks for:
        same expected output and output from function tested
    """

    def test_get_time(self):
        today_date = datetime.today()

        input_queries = [today_date.replace(hour=11, minute=59), today_date.replace(
            hour=23, minute=21), today_date.replace(hour=5, minute=17), today_date.replace(hour=16, minute=16)]
        expected_responses = ["11:59 AM", "11:21 PM", "05:17 AM", "04:16 PM"]

        set_time_list = []
        for query in input_queries:
            corrected = get_time(query)
            set_time_list.append(corrected)

        self.assertEqual(expected_responses, set_time_list)

    """
    function tested: get_masked_data
    input params:
        message: text_message to be masked
    output:
        returns masked confidential data such as pan number, aadhar number e.t.c
    """

    def test_get_masked_data(self):
        logger.info("Testing of get_masked_data is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_masked_data is going on.\n")

        test_sentence = "This is testing"
        expected_response = test_sentence
        correct_response = get_masked_data(test_sentence)

        self.assertEqual(expected_response, correct_response)

        test_sentence = "My username is test123. I have 5 rs."
        expected_response = "My username is ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae. I have c81d40dbeed369f1476086cf882dd36bf1c3dc35e07006f0bec588b983055487 rs."
        correct_response = get_masked_data(
            test_sentence)

        self.assertEqual(expected_response, correct_response)

        test_sentence = "My mobile number is 9012345678. Who are you?"
        expected_response = "My mobile number is e917869a180f491f5fe6d443d27d2fd8532623b5638464254b53fe426a4fd4b5. Who are you?"
        correct_response = get_masked_data(
            test_sentence)

        self.assertEqual(expected_response, correct_response)
        test_sentence = "My customer id is test4567. My PAN is BDWPJ5333B and account number 1234567543."
        expected_response = "My customer id is af0790ab6dfcbf25af421b9fa785dfee58148f897d920b028fb984b088b895dc. My PAN is 0e443d73cb5a2875f398f2fcdefeb8b8d5e6b877f37f96223a822da886f93895 and account number 25619bdfdd3f2e9b670190fd967b31a30dbe4493df3d0d7336cf57f177b2d2ee."

        correct_response = get_masked_data(
            test_sentence)

        self.assertEqual(expected_response, correct_response)
        test_sentence = """Thank you 'status': 'vikash' for connecting "vikash" customer care. My PAN number is CEQPK4956K. My mobile number is 9920262298 my username is test12345. I have 2000rs. My dob is 19/10/1998 or 1998/10/19 . my aadhar number is 291313129560"."""
        expected_response = """Thank you 'status': 'vikash' for connecting "vikash" customer care. My PAN number is fc2045ec157769861f8f058880357bcd291f9c75a49d6149675841bc43bd8eb3. My mobile number is 4e6f3061ccfc1bf39e7a30c4e141a9ec11afba4e4266e6cc389e7ccdac270194 my username is 6fec2a9601d5b3581c94f2150fc07fa3d6e45808079428354b868e412b76e6bb. I have 989c32b00f0142150744d7f939bf0fb1b341c6cc076ba48a7ae1bef8ed0c1321. My dob is 1a00644c456957fa8fac6dca77213ad9c26d3c2d1c45d43892e8a29b6e159f24 or 580452003a3fa13c10cffcf8a7bd1299cede798f9932dc51a3f4f37cb885632d . my aadhar number is 0791c1793dd5911580c92d1dfee1a6966f9924f66f1ca7b553a062b21d169b9b"."""

        correct_response = get_masked_data(
            test_sentence)

        self.assertEqual(expected_response, correct_response)

    """
    function tested: alphanumeric
    input params:
        text: 
    output:
        returns true if text is alphanumeric else false
    """

    def test_alphanumeric(self):
        logger.info("Testing of alphanumeric is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of alphanumeric is going on.\n")

        validation_obj = LiveChatInputValidation()

        test_sentence = "This is testing"
        correct_response = validation_obj.alphanumeric(test_sentence)

        self.assertEqual(True, correct_response)

        test_sentence = "I have 5 $."
        correct_response = validation_obj.alphanumeric(test_sentence)

        self.assertEqual(False, correct_response)

        """
    function tested: validate_keyword
    input params:
        text: 
    output:
        returns true if keyword is valid else false
    """

    def test_validate_keyword(self):
        logger.info("Testing of validate_keyword is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of validate_keyword is going on.\n")

        validation_obj = LiveChatInputValidation()

        test_sentence = "tc"
        correct_response = validation_obj.validate_keyword(test_sentence)

        self.assertEqual(True, correct_response)

        test_sentence = "$"
        correct_response = validation_obj.validate_keyword(test_sentence)

        self.assertEqual(False, correct_response)

    """
    function tested: validate_canned_response
    input params:
        text: 
    output:
        returns true if canned response is valid else false
    """

    def test_validate_canned_response(self):
        logger.info("Testing of validate_canned_response is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of validate_canned_response is going on.\n")

        validation_obj = LiveChatInputValidation()

        test_sentence = "Take Care"
        correct_response = validation_obj.validate_canned_response(
            test_sentence)

        self.assertEqual(True, correct_response)

        test_sentence = "Dollar $"
        correct_response = validation_obj.validate_canned_response(
            test_sentence)

        self.assertEqual(False, correct_response)

    """
    function tested: is_valid_uuid
    input params:
        id: any id
    output:
        returns true if id is a valid uuid else False
    """

    def test_is_valid_uuid(self):
        logger.info("Testing of is_valid_uuid is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of is_valid_uuid is going on.\n")

        validation_obj = LiveChatInputValidation()

        id = "12345"
        res = validation_obj.is_valid_uuid(id)

        self.assertEqual(False, res)

        id = uuid.uuid4()
        res = validation_obj.is_valid_uuid(str(id))

        self.assertEqual(True, res)


"""
Test of All functions which are dependent on models
"""


class UtilsSomeFunctionsSectionFour(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'LiveChat'})
        LiveChatConfig.objects.create(max_customer_count=110)
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        category_obj = LiveChatCategory.objects.create(
            title="others", bot=bot_obj)

        MISDashboard.objects.create(
            user_id="1", bot=bot_obj, message_received="hi", bot_response="how may I assist you?")
        MISDashboard.objects.create(
            user_id="2", bot=bot_obj, message_received="hi", bot_response="how may I assist you?")
        MISDashboard.objects.create(user_id="4", bot=bot_obj, message_received="hi",
                                    bot_response="how may I assist you?", date=datetime.now().replace(hour=23))
        MISDashboard.objects.create(
            user_id="4", bot=bot_obj, message_received="Hi", bot_response="hello")
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
        livechat_supervisor = LiveChatUser.objects.create(
            status="2", user=User.objects.create(role="1", status="1", username="testsupervisor", password="test1234"), last_updated_time=datetime.now().replace(hour=1))
        livechat_supervisor.agents.add(livechat_agent)
        livechat_supervisor.bots.add(bot_obj)
        livechat_supervisor.save()
        livechat_admin.agents.add(livechat_supervisor)
        livechat_admin.save()
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=10, chat_duration=10, queue_time=5, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj,
                                        is_session_exp=True, joined_date=datetime.now(), wait_time=2, chat_duration=10, queue_time=7, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj,
                                        is_session_exp=True, joined_date=datetime.now(), wait_time=3, chat_duration=10, queue_time=8, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), wait_time=20, chat_duration=100, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), wait_time=10, chat_duration=100, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), wait_time=20, chat_duration=100, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), wait_time=30, chat_duration=100, bot=bot_obj)

    """
    function: add_supervisor
    input params:
        user:
        supervisor_pk:
        current_user:
    output:

        This function adds supervisor for a perticular agent. In case, if supervisor pk "-1", then it current user will be the supervisor for agent.

    """

    def test_add_supervisor(self):
        logger.info("Testing of add_supervisor is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of add_supervisor is going on.\n")

        livechat_admin = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))
        livechat_supervisor = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))
        livechat_agent = LiveChatUser.objects.get(
            user=User.objects.get(username="test"))

        add_supervisor(livechat_agent, livechat_supervisor.pk,
                       livechat_admin, LiveChatUser)

        livechat_supervisor = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))

        self.assertEqual(
            livechat_agent in livechat_supervisor.agents.all(), True)

        livechat_supervisor.agents.remove()
        add_supervisor(livechat_agent, "-1", livechat_supervisor, LiveChatUser)

        livechat_supervisor = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))

        self.assertEqual(
            livechat_agent in livechat_supervisor.agents.all(), True)

        add_supervisor(livechat_agent, "-1", livechat_admin, LiveChatUser)

        livechat_supervisor = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))

        self.assertEqual(
            livechat_agent in livechat_supervisor.agents.all(), True)

    """
    function: get_number_of_day
    input params:
        year:
        month:
    expected output:
        1. Provides number of days in a month of a perticular year.
    """

    def test_get_number_of_day(self):
        logger.info("Testing of get_number_of_day is going on.",
                    extra={'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_number_of_day is going on.\n")

        self.assertEqual(get_number_of_day(2020, 1), 31)
        self.assertEqual(get_number_of_day(20200, 2), 28)
        self.assertEqual(get_number_of_day(202000, 2), 29)
        self.assertEqual(get_number_of_day(2020, 2), 29)
        self.assertEqual(get_number_of_day(2021, 11), 30)

    """
    function: get_agents_under_this_user
    input params:
        user_obj:
    output:
        1. This function returns list of livechat agents under this user_obj.
        2. If user_obj is agent then it will be empty.

    """

    def test_get_agents_under_this_user(self):
        logger.info("Testing of get_agents_under_this_user is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_agents_under_this_user is going on.\n")
        user = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))

        allowed_user = get_agents_under_this_user(user)
        self.assertEqual(len(allowed_user), 1)

        user = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))

        allowed_user = get_agents_under_this_user(user)
        self.assertEqual(len(allowed_user), 3)

        user = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234"))

        allowed_user = get_agents_under_this_user(user)
        self.assertEqual(len(allowed_user), 1)

    """
    function tested: get_allowed_livechat_user
    input params:
        livechat_user:
        selected_category:
    expected output:
        1. It is a helper function which two arguments livechat_user and category. It returns the all agents lying under this livechat user.
    """

    def test_get_allowed_livechat_user(self):
        logger.info("Testing of get_allowed_livechat_user is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_allowed_livechat_user is going on.\n")
        bot_obj = Bot.objects.get(name="testbot")
        user = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))

        allowed_user = get_allowed_livechat_user(
            user, "-1", bot_obj, LiveChatUser, LiveChatCategory)
        self.assertEqual(len(allowed_user), 0)

        user = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))

        allowed_user = get_allowed_livechat_user(
            user, "-1", bot_obj, LiveChatUser, LiveChatCategory)
        self.assertEqual(len(allowed_user), 0)

        user = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234"))

        user.is_online = True
        user.save()

        allowed_user = get_allowed_livechat_user(
            user, "-1", bot_obj, LiveChatUser, LiveChatCategory)
        self.assertEqual(len(allowed_user), 1)


class UtilsSomeFunctionsWithModels2(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'LiveChat'})
        LiveChatConfig.objects.create(max_customer_count=110)
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        LiveChatConfig.objects.create(max_customer_count=110, bot=bot_obj)
        category_obj = LiveChatCategory.objects.create(
            title="others", bot=bot_obj)

        MISDashboard.objects.create(
            user_id="1", bot=bot_obj, message_received="hi", bot_response="how may I assist you?")
        MISDashboard.objects.create(
            user_id="2", bot=bot_obj, message_received="hi", bot_response="how may I assist you?")
        MISDashboard.objects.create(user_id="4", bot=bot_obj, message_received="hi",
                                    bot_response="how may I assist you?", date=datetime.now().replace(hour=23))
        MISDashboard.objects.create(
            user_id="4", bot=bot_obj, message_received="Hi", bot_response="hello")
        easychat_user = User.objects.create(
            role="1", status="1", username="test", password="test")
        easychat_user_2 = User.objects.create(
            role="1", status="1", username="test2", password="test")
        livechat_admin = LiveChatUser.objects.create(
            status="1", user=User.objects.create(role="1", status="1", username="testadmin", password="test1234"), last_updated_time=datetime.now().replace(hour=1))
        livechat_agent = LiveChatUser.objects.create(
            status="3", user=easychat_user, last_updated_time=datetime.now().replace(hour=1))
        livechat_agent_2 = LiveChatUser.objects.create(
            status="3", user=easychat_user_2, last_updated_time=datetime.now().replace(hour=1))
        livechat_agent.category.add(category_obj)
        livechat_agent.bots.add(bot_obj)
        livechat_admin.agents.add(livechat_agent)
        livechat_admin.bots.add(bot_obj)
        livechat_admin.save()
        livechat_agent = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="test1234", password="test1234"))
        livechat_agent.bots.add(bot_obj)
        livechat_agent.save()
        livechat_supervisor = LiveChatUser.objects.create(
            status="2", user=User.objects.create(role="1", status="1", username="testsupervisor", password="test1234"), last_updated_time=datetime.now().replace(hour=1))
        livechat_supervisor.agents.add(livechat_agent)
        livechat_supervisor.bots.add(bot_obj)
        livechat_supervisor.save()
        livechat_admin.agents.add(livechat_supervisor)
        livechat_admin.save()
        customer_obj = LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=False,
                                                       joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj)
        customer_obj.guest_agents.add(livechat_agent_2)
        customer_obj.save()
    """
    function tested: check_if_livechat_only_admin
    input params:
        user_obj: current user
        LiveChatUser: 

    expected output: returns this function checks if current user is livechat only admin or not.
    checks for :
        1.if user is livechat only admin it should return livechat_only_admin__user
        2.if user is not it should return the same livechat user .
    """

    def test_check_if_livechat_only_admin(self):
        livechat_admin = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))
        livechat_admin.is_livechat_only_admin = True
        livechat_admin.livechat_only_admin.add(livechat_admin)
        livechat_admin.save()
        livechat_admin = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))
        user = check_if_livechat_only_admin(livechat_admin, LiveChatUser)
        self.assertEqual(user, LiveChatUser.objects.filter(
            livechat_only_admin__user=livechat_admin.user)[0])

        livechat_admin.is_livechat_only_admin = False
        livechat_admin.save()
        user = check_if_livechat_only_admin(livechat_admin, LiveChatUser)
        self.assertEqual(user, livechat_admin)

    """
    function tested: check_agent_has_bot_assign_category
    input params:
        user_obj: current user
        bot_obj: bot_obj
        livechat_category: livechat_category

    expected output: adds the livechat_category to the livechat_agent's categories if bot_obj is related to livechat_agent.
    checks for :
        1.livechat_category is added or not if it passes above conditions
    """

    def test_check_agent_has_bot_assign_category(self):
        livechat_agent = LiveChatUser.objects.get(status="3", user=User.objects.get(
            username="test1234"))
        count = livechat_agent.category.count()
        bot_obj = Bot.objects.get(name="testbot", slug="testbot")
        category_obj = LiveChatCategory.objects.get(title="others")
        check_agent_has_bot_assign_category(
            livechat_agent, bot_obj, category_obj)
        self.assertEqual(livechat_agent.category.count(), count + 1)

        if category_obj in livechat_agent.category.all():
            new_category = category_obj
        self.assertEqual(new_category, category_obj)

        count = livechat_agent.category.count()
        bot_obj_new = Bot.objects.create(
            name="testbot2", slug="testbot2", bot_display_name="testbot2", bot_type="2")
        category_obj_new = LiveChatCategory.objects.create(
            title="super", bot=bot_obj_new)
        check_agent_has_bot_assign_category(
            livechat_agent, bot_obj_new, category_obj)
        self.assertEqual(livechat_agent.category.count(), count)

        if category_obj_new in livechat_agent.category.all():
            new_category = category_obj_new
        self.assertNotEqual(new_category, category_obj_new)

    """
    function tested: get_canned_response_for_current_agent
    input params:
        user_obj: current user
        CannedResponse

    expected output: returns this function provide all the canned response for user_obj. user_obj can be agent/supervisor/admin or livechatonlyadmin
    checks for: whether the added canned_responses are present in the returned canned_response list.
    """

    def test_get_canned_response_for_current_agent(self):

        livechat_agent = LiveChatUser.objects.get(
            status="3", user=User.objects.get(username="test1234"))
        canned_response = CannedResponse.objects.create(
            title="None", keyword="agent", response="123")
        canned_response.agent_id = livechat_agent
        canned_response.save()
        canned_response_list = get_canned_response_for_current_agent(
            livechat_agent, CannedResponse, LiveChatUser)
        self.assertEqual(canned_response_list.count(), 1)

        canned_response_list_new = CannedResponse.objects.filter(
            agent_id=livechat_agent)
        self.assertEqual(list(canned_response_list),
                         list(canned_response_list_new))

        livechat_supervisor = LiveChatUser.objects.get(
            status="2", user=User.objects.get(username="testsupervisor"))
        canned_response = CannedResponse.objects.create(
            title="None", keyword="sup", response="123")
        canned_response.agent_id = livechat_supervisor
        canned_response.save()
        canned_response = CannedResponse.objects.create(
            title="None", keyword="sup2", response="123")
        canned_response.agent_id = livechat_supervisor
        canned_response.save()
        canned_response_list = get_canned_response_for_current_agent(
            livechat_supervisor, CannedResponse, LiveChatUser)
        self.assertEqual(canned_response_list.count(), 2)

        canned_response_list_new = CannedResponse.objects.filter(
            agent_id=livechat_supervisor)
        self.assertEqual(list(canned_response_list),
                         list(canned_response_list_new))

        livechat_admin = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))
        canned_response = CannedResponse.objects.create(
            title="None", keyword="abc", response="123")
        canned_response.agent_id = livechat_admin
        canned_response.save()
        canned_response_list = get_canned_response_for_current_agent(
            livechat_admin, CannedResponse, LiveChatUser)
        self.assertEqual(canned_response_list.count(), 1)

        canned_response_list_new = CannedResponse.objects.filter(
            agent_id=livechat_admin)
        self.assertEqual(list(canned_response_list),
                         list(canned_response_list_new))

    def test_check_for_system_commands(self):
        print("\n\nTesting check_for_system_commands")
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")

        LiveChatConfig.objects.create(bot=bot_obj)

        code = "import threading\nthreading.Thread()"

        self.assertEqual(check_for_system_commands(
            code, bot_obj.pk, LiveChatConfig, Bot), True)

        code = "import re\ns = r'[a-z]'"

        self.assertEqual(check_for_system_commands(
            code, bot_obj.pk, LiveChatConfig, Bot), False)

    """
    function tested: get_cobrowsing_status
    input params:
        customer_obj: LiveChat customer obj
        LiveChatCobrowsingData
    
    expected output: returns the status and meeting_id of the latest cobrowsing request sent by agent to the
    customer
    """

    def test_get_cobrowsing_status(self):
        print("\n\nTesting get_cobrowsing_status")

        customer_obj = LiveChatCustomer.objects.get(username="test")

        cobrowsing_status, cobrowsing_meeting_id = get_cobrowsing_status(
            customer_obj, LiveChatCobrowsingData)

        self.assertEqual(cobrowsing_status, 'none')
        self.assertEqual(cobrowsing_meeting_id, None)

        agent_obj = LiveChatUser.objects.get(user__username="test")

        cobrowsing_obj = LiveChatCobrowsingData.objects.create(
            customer=customer_obj, agent=agent_obj)

        cobrowsing_status, cobrowsing_meeting_id = get_cobrowsing_status(
            customer_obj, LiveChatCobrowsingData)

        self.assertEqual(cobrowsing_status, 'initiated')
        self.assertEqual(cobrowsing_meeting_id, str(cobrowsing_obj.meeting_id))

        cobrowsing_obj.is_accepted = True
        cobrowsing_obj.save()

        cobrowsing_status, cobrowsing_meeting_id = get_cobrowsing_status(
            customer_obj, LiveChatCobrowsingData)

        self.assertEqual(cobrowsing_status, 'accepted')
        self.assertEqual(cobrowsing_meeting_id, str(cobrowsing_obj.meeting_id))

        cobrowsing_obj.is_started = True
        cobrowsing_obj.save()

        cobrowsing_status, cobrowsing_meeting_id = get_cobrowsing_status(
            customer_obj, LiveChatCobrowsingData)

        self.assertEqual(cobrowsing_status, 'ongoing')
        self.assertEqual(cobrowsing_meeting_id, str(cobrowsing_obj.meeting_id))

        cobrowsing_obj.is_completed = True
        cobrowsing_obj.save()

        cobrowsing_status, cobrowsing_meeting_id = get_cobrowsing_status(
            customer_obj, LiveChatCobrowsingData)

        self.assertEqual(cobrowsing_status, 'completed')
        self.assertEqual(cobrowsing_meeting_id, str(cobrowsing_obj.meeting_id))

    """
    function tested: get_cobrowsing_info_based_agent
    input params:
        user_obj: LiveChat agent obj
        LiveChatCobrowsingData
    
    expected output: returns the cobrowsing_info of the latest cobrowsing request sent by the agent to a
    customer
    """

    def test_get_cobrowsing_info_based_agent(self):
        print("\n\nTesting get_cobrowsing_info_based_agent")

        customer_obj = LiveChatCustomer.objects.get(username="test")
        agent_obj = LiveChatUser.objects.get(user__username="test")

        cobrowsing_info = get_cobrowsing_info_based_agent(
            agent_obj, LiveChatCobrowsingData)

        self.assertEqual(cobrowsing_info['status'], 'none')
        self.assertEqual(cobrowsing_info['meeting_id'], 'none')
        self.assertEqual(cobrowsing_info['session_id'], 'none')

        cobrowsing_obj = LiveChatCobrowsingData.objects.create(
            customer=customer_obj, agent=agent_obj)

        cobrowsing_info = get_cobrowsing_info_based_agent(
            agent_obj, LiveChatCobrowsingData)

        self.assertEqual(cobrowsing_info['status'], 'initiated')
        self.assertEqual(cobrowsing_info['meeting_id'], str(
            cobrowsing_obj.meeting_id))
        self.assertEqual(cobrowsing_info['session_id'], str(
            customer_obj.session_id))

        cobrowsing_obj.is_accepted = True
        cobrowsing_obj.save()

        cobrowsing_info = get_cobrowsing_info_based_agent(
            agent_obj, LiveChatCobrowsingData)

        self.assertEqual(cobrowsing_info['status'], 'accepted')
        self.assertEqual(cobrowsing_info['meeting_id'], str(
            cobrowsing_obj.meeting_id))
        self.assertEqual(cobrowsing_info['session_id'], str(
            customer_obj.session_id))

        cobrowsing_obj.is_started = True
        cobrowsing_obj.save()

        cobrowsing_info = get_cobrowsing_info_based_agent(
            agent_obj, LiveChatCobrowsingData)

        self.assertEqual(cobrowsing_info['status'], 'ongoing')
        self.assertEqual(cobrowsing_info['meeting_id'], str(
            cobrowsing_obj.meeting_id))
        self.assertEqual(cobrowsing_info['session_id'], str(
            customer_obj.session_id))

    """
    function tested: get_cobrowsing_info_based_guest_agent
    input params:
        user_obj: LiveChat agent obj
        LiveChatCobrowsingData
    
    expected output: returns the cobrowsing_info of the latest cobrowsing request where this guest
    agent is invited
    """

    def test_get_cobrowsing_info_based_guest_agent(self):
        print("\n\nTesting get_cobrowsing_info_based_agent")

        customer_obj = LiveChatCustomer.objects.get(username="test")
        agent_obj = LiveChatUser.objects.get(user__username="test2")

        cobrowsing_info = get_cobrowsing_info_based_guest_agent(
            agent_obj, LiveChatCobrowsingData, LiveChatCustomer)

        self.assertEqual(cobrowsing_info, [])

        LiveChatCobrowsingData.objects.create(
            customer=customer_obj, agent=agent_obj, is_accepted=True)

        cobrowsing_info = get_cobrowsing_info_based_guest_agent(
            agent_obj, LiveChatCobrowsingData, LiveChatCustomer)

        self.assertEqual(len(cobrowsing_info), 1)

    """
    function tested: get_cobrowsing_info_based_guest_agent
    input params:
        user_obj: LiveChat agent obj
        LiveChatCobrowsingData
    
    expected output: returns the cobrowsing_info of the latest cobrowsing request where this guest
    agent is invited
    """

    def test_get_cobrowsing_request_text(self):
        print("\n\nTesting get_cobrowsing_info_based_agent")

        bot_obj = Bot.objects.get(name="testbot")
        config_obj = LiveChatConfig.objects.get(bot=bot_obj)

        cobrowsing_request_text = get_cobrowsing_request_text(
            bot_obj, LiveChatConfig)

        self.assertEqual(cobrowsing_request_text,
                         config_obj.cobrowse_request_text)

        config_obj.cobrowse_request_text = 'Hey, Can we connect?'
        config_obj.save()

        cobrowsing_request_text = get_cobrowsing_request_text(
            bot_obj, LiveChatConfig)

        self.assertEqual(cobrowsing_request_text, 'Hey, Can we connect?')

    """
    function tested: get_cobrowsing_data_history_objects
    input params:
        agent_username: username of agent or 'All'
        query_user_obj: LiveChat user obj for which records are fetched or None
        datetime_end
        datetime_start
        agent_obj_list: All agents under the admin or the supervisor
    
    expected output: returns the cobrowsing_object_list which are either ongoing or completed
    """

    def test_get_cobrowsing_data_history_objects(self):
        print("\n\nTesting get_cobrowsing_info_based_agent")

        datetime_start = datetime.now()
        datetime_end = datetime.now()

        agent_obj_list = LiveChatUser.objects.filter(
            status='3', is_deleted=False)

        cobrowsing_object_list = get_cobrowsing_data_history_objects(
            'All', None, datetime_end, datetime_start, agent_obj_list, LiveChatCobrowsingData)

        self.assertEqual(cobrowsing_object_list.count(), 0)

        customer_obj = LiveChatCustomer.objects.get(username='test')

        LiveChatCobrowsingData.objects.create(customer=customer_obj, request_datetime=datetime.now(
        ), agent=agent_obj_list[0], is_accepted=True, is_started=True)

        cobrowsing_object_list = get_cobrowsing_data_history_objects(
            'All', None, datetime_end, datetime_start, agent_obj_list, LiveChatCobrowsingData)

        self.assertEqual(cobrowsing_object_list.count(), 1)

        cobrowsing_object_list = get_cobrowsing_data_history_objects(
            agent_obj_list[0].user.username, agent_obj_list[0], datetime_end, datetime_start, agent_obj_list, LiveChatCobrowsingData)

        self.assertEqual(cobrowsing_object_list.count(), 1)

    """
    function tested: parse_cobrowsing_history_object_list
    input params:
        cobrowsing_data_objs
    
    expected output: returns array of json objects containing details of LiveChatCobrowseData
    """

    def test_parse_cobrowsing_history_object_list(self):
        print("\n\nTesting get_cobrowsing_info_based_agent")

        cobrowsing_objs = LiveChatCobrowsingData.objects.all()

        cobrowsing_data_obj_list = parse_cobrowsing_history_object_list(
            cobrowsing_objs)

        self.assertEqual(cobrowsing_data_obj_list, [])

        customer_obj = LiveChatCustomer.objects.get(username='test')
        agent_obj = LiveChatUser.objects.get(user__username='test')

        LiveChatCobrowsingData.objects.create(
            customer=customer_obj, agent=agent_obj, is_accepted=True, is_completed=True)

        cobrowsing_objs = LiveChatCobrowsingData.objects.all()

        cobrowsing_object_list = parse_cobrowsing_history_object_list(
            cobrowsing_objs)

        self.assertEqual(len(cobrowsing_object_list), 1)


class UtilsLiveChatFunctions(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'LiveChat'})
        LiveChatConfig.objects.create(max_customer_count=110)
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        category_obj = LiveChatCategory.objects.create(
            title="others", bot=bot_obj)
        easychat_user = User.objects.create(
            role="1", status="1", username="test", password="test")
        user_admin = User.objects.create(
            role="1", status="1", username="testadmin", password="test1234")
        livechat_admin = LiveChatUser.objects.create(
            status="1", user=user_admin, last_updated_time=datetime.now().replace(hour=1))
        livechat_supervisor = LiveChatUser.objects.create(
            status="2", user=User.objects.create(role="1", status="1", username="testsupervisor", password="test1234"), last_updated_time=datetime.now().replace(hour=1))
        livechat_agent = LiveChatUser.objects.create(
            status="3", user=easychat_user, last_updated_time=datetime.now().replace(hour=1))
        bot_obj.created_by = user_admin
        bot_obj.save()
        livechat_agent.category.add(category_obj)
        livechat_agent.bots.add(bot_obj)
        livechat_admin.agents.add(livechat_supervisor)
        livechat_admin.bots.add(bot_obj)
        livechat_admin.save()
        livechat_supervisor.agents.add(livechat_agent)
        livechat_agent = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="test1234", password="test1234"))
        livechat_agent.bots.add(bot_obj)
        livechat_agent.save()
        livechat_supervisor.agents.add(livechat_agent)
        livechat_supervisor.bots.add(bot_obj)
        livechat_supervisor.save()
        livechat_admin.agents.add(livechat_supervisor)
        livechat_admin.save()
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=10, chat_duration=10, queue_time=5, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj,
                                        is_session_exp=True, joined_date=datetime.now(), wait_time=2, chat_duration=10, queue_time=7, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj,
                                        is_session_exp=True, joined_date=datetime.now(), wait_time=3, chat_duration=10, queue_time=8, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), wait_time=20, chat_duration=100, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), wait_time=10, chat_duration=100, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), wait_time=20, chat_duration=100, bot=bot_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, category=category_obj, is_session_exp=True,
                                        joined_date=datetime.now() - timedelta(days=8), wait_time=30, chat_duration=100, bot=bot_obj)
        livechat_agent = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="test12345", password="test12345"))
        livechat_agent.category.add(category_obj)
        livechat_agent.bots.add(bot_obj)
        livechat_admin.agents.add(livechat_agent)
        livechat_agent.save()
        livechat_admin.save()
        LiveChatBlackListKeyword.objects.create(
            word="SHIT", agent_id=livechat_admin)
        LiveChatBlackListKeyword.objects.create(
            word="SAALE", agent_id=livechat_supervisor)

        livechat_intent = Intent.objects.create(
            name="Chat with an expert", is_authentication_required=False, is_feedback_required=True, keywords='{"0": "agent,chat", "1": "expert,chat"}', training_data='{"0": "chat with an agent", "1": " Chat with an expert"}')
        bot_obj.livechat_default_intent = livechat_intent
        bot_obj.save()
        livechat_intent.bots.add(bot_obj)
        livechat_intent.save()

        LiveChatCalender.objects.create()

    """
    function tested: test_get_blacklisted_keyword_for_current_agent
    input queries:
        livechat_agent
        LiveChatBlackListKeyword model 
    expected output:
        if agent is mapped under supervisor : blacklisted keyywords of supervisor + admin of supervisor
        if supervisor: blacklisted keyywords of supervisor + admin of supervisor
    """

    def test_get_blacklisted_keyword_for_current_agent(self):
        logger.info("Testing of get blacklisted keywords.", extra={
            'AppName': 'LiveChat'})
        print("\n\n\nTesting of get blacklisted keywords.\n")

        # livechat_admin = LiveChatUser.objects.get(
        #     user=User.objects.get(username="testadmin"))
        livechat_supervisor = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))
        livechat_agent = LiveChatUser.objects.get(
            user=User.objects.get(username="test"))
        blacklisted_agent_under_supervisor = []
        blacklisted_admin_agent_query_set = get_blacklisted_keyword_for_current_agent(
            livechat_agent, LiveChatBlackListKeyword, LiveChatUser)
        for items in blacklisted_admin_agent_query_set:
            blacklisted_agent_under_supervisor.append(items.word)
        self.assertEqual(['SAALE', 'SHIT'], blacklisted_agent_under_supervisor)

        blacklisted_supervisor_under_admin = []
        blacklisted_supervisor_under_admin_query_set = get_blacklisted_keyword_for_current_agent(
            livechat_supervisor, LiveChatBlackListKeyword, LiveChatUser)
        for items in blacklisted_supervisor_under_admin_query_set:
            blacklisted_supervisor_under_admin.append(items.word)
        self.assertEqual(['SAALE', 'SHIT'], blacklisted_supervisor_under_admin)

        livechat_agent_under_admin_direct = LiveChatUser.objects.get(
            user=User.objects.get(username="test12345"))
        blacklisted_admin_agent = []
        blacklisted_admin_agent_query_set = get_blacklisted_keyword_for_current_agent(
            livechat_agent_under_admin_direct, LiveChatBlackListKeyword, LiveChatUser)
        for items in blacklisted_admin_agent_query_set:
            blacklisted_admin_agent.append(items.word)
        self.assertEqual(['SHIT'], blacklisted_admin_agent)

    """
    function tested: test_get_chat_duration_list
    input queries:
        -
    expected output:
        array of dictionary for duration list
    """

    def test_get_chat_duration_list(self):
        logger.info("Testing of get chat duration list", extra={
            'AppName': 'LiveChat'})
        print("\n\n\n\nTesting of get chat duration list")
        self.assertEqual([{"key": "10000000", "value": "No Restriction"}, {"key": "15", "value": "Less than 15 Minutes"}, {"key": "30", "value": "Between 15 and 30 minutes"}, {
            "key": "60", "value": "Between 30 and 60 minutes"}, {"key": "61", "value": "More than 60 minutes"}], get_chat_duration_list())

    """
    function tested: test_get_livechat_date_format
    input queries:
        -
    expected output:
        converts date object to DD-MM-YYYY format
    """

    def test_get_livechat_date_format(self):
        logger.info("Testing of get livechat date format", extra={
            'AppName': 'LiveChat'})
        print("\n\n\n\nTesting of get livechat date format")
        test_obj = datetime(2020, 5, 17)
        expected_response = "17-May-2020"
        correct_response = get_livechat_date_format(test_obj)
        self.assertEqual(expected_response, correct_response)

    """
    function tested: test_get_milliseconds_to_datetime
    input queries:
        -
    expected output:
        converts miliseconds to datetime
    """

    def test_get_milliseconds_to_datetime(self):
        logger.info("Testing get_milliseconds_to_datetime...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_milliseconds_to_datetime...\n")

        milliseconds = "1593188793000"
        date_obj = get_milliseconds_to_datetime(milliseconds)

        self.assertEqual("26-Jun-2020", date_obj)

    """
    function tested: test_get_month_list
    input queries:
        -
    expected output:
        returns array of key value of months and numeric value of months
    """

    def test_get_month_list(self):
        logger.info("Testing get month list", extra={'AppName': 'LiveChat'})
        print("\n Testing get month list")
        self.assertEqual([{"key": "1", "value": "Jan"}, {"key": "2", "value": "Feb"}, {"key": "3", "value": "Mar"}, {"key": "4", "value": "Apr"}, {"key": "5", "value": "May"}, {"key": "6", "value": "Jun"}, {
                         "key": "7", "value": "Jul"}, {"key": "8", "value": "Aug"}, {"key": "9", "value": "Sep"}, {"key": "10", "value": "Oct"}, {"key": "11", "value": "Nov"}, {"key": "12", "value": "Dec"}], get_month_list())

    """
    function tested: test_check_for_holiday
    input queries:
        bot object
    expected output:
        returns if agent has holdiday that day
    """

    def test_check_for_holiday(self):
        logger.info("Testing of check_for_holiday is going on.",
                    extra={'AppName': 'LiveChat'})
        print("\n\n\nTesting of check_for_holiday is going on.\n")

        user = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))
        LiveChatCalender.objects.create(
            event_type="2", created_by=user, description="Testing", auto_response="This is testing.", event_date=timezone.now())
        bot_obj = Bot.objects.get(name="testbot")
        check, response = check_for_holiday(
            bot_obj, LiveChatCalender, LiveChatUser)
        self.assertEqual(check, True)
        self.assertEqual("holiday", response["assigned_agent"])

        check, response = check_for_holiday(
            None, LiveChatCalender, LiveChatUser)

        self.assertEqual(check, False)
        self.assertEqual({}, {})

    """
    function tested: test_get_livechat_request_packet_to_channel
    input queries:
        -
    expected output:
        livechat_request_packet_to_channel
    """

    def test_get_livechat_request_packet_to_channel(self):
        logger.info("Testing of get_livechat_request_packet_to_channel is going on.",
                    extra={'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_livechat_request_packet_to_channel is going on.\n")
        response = {
            "session_id": "123456",
            "type": "testing",
            "text_message": "testing",
            "path": "/livechat/audit_trail",
            "channel": "web",
            "bot_id": "1",
            "agent_name": "testing"
        }
        self.assertEqual(json.dumps(response), get_livechat_request_packet_to_channel(
            "123456", "testing", "testing", "/livechat/audit_trail", "web", "1", "testing"))

    """
    function tested: test_check_for_non_working_hour
    input queries:
        bot object
    expected output:
        checks if it's a non working hour for agent
    """

    def test_check_for_non_working_hour(self):
        logger.info("Testing of check_for_non_working_hour is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of check_for_non_working_hour is going on.\n")

        user = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))

        start_date = datetime.now() - timedelta(minutes=1)
        end_date = datetime.now() + timedelta(minutes=1)
        LiveChatCalender.objects.create(event_type="1", event_date=datetime.now(
        ), start_time=start_date.time(), end_time=end_date.time(), created_by=user)

        bot_obj = Bot.objects.all()[0]
        check, response = check_for_non_working_hour(
            bot_obj, LiveChatCalender, LiveChatConfig, LiveChatUser)
        self.assertEqual(check, False)

        LiveChatCalender.objects.all().delete()
        bot_obj = Bot.objects.all()[0]
        check, response = check_for_non_working_hour(
            bot_obj, LiveChatCalender, LiveChatConfig, LiveChatUser)
        self.assertEqual(check, True)

        check, response = check_for_non_working_hour(
            None, LiveChatCalender, LiveChatConfig, LiveChatUser)

        self.assertEqual(check, False)
        self.assertEqual({}, {})

    """
    function tested: test_save_audit_trail
    input queries:
        status
        livechat_user
    expected output:
        saves user action in audit trail
    """

    def test_save_audit_trail(self):
        logger.info("Testing of test_save_audit_trail is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of test_save_audit_trail is going on.\n")
        user = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))
        save_audit_trail_data('1', user, LiveChatAuditTrail)
        self.assertEqual(
            str(LiveChatAuditTrail.objects.filter(user=user)[0].action), "1")

    """
    function tested: test_add_supervisor
    input queries:
        livechat_agent
        supervisor pk
        admin
    expected output:
        adds supervisor to the agent
    """

    def test_add_supervisor(self):
        logger.info("Testing of add_supervisor is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of add_supervisor is going on.\n")

        livechat_admin = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))
        livechat_supervisor = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))
        livechat_agent = LiveChatUser.objects.get(
            user=User.objects.get(username="test"))

        add_supervisor(livechat_agent, livechat_supervisor.pk,
                       livechat_admin, LiveChatUser)

        livechat_supervisor = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))

        self.assertEqual(
            livechat_agent in livechat_supervisor.agents.all(), True)

        livechat_supervisor.agents.remove()
        add_supervisor(livechat_agent, "-1", livechat_supervisor, LiveChatUser)

        livechat_supervisor = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))

        self.assertEqual(
            livechat_agent in livechat_supervisor.agents.all(), True)

        add_supervisor(livechat_agent, "-1", livechat_admin, LiveChatUser)

        livechat_supervisor = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))

        self.assertEqual(
            livechat_agent in livechat_supervisor.agents.all(), True)

    """
    function tested: test_check_and_add_admin_config
    input queries:
        livechat_admin
    expected output:
        if admin config does not exist for Admin, this function creates on
    """

    def test_check_and_add_admin_config(self):
        logger.info("Testing of test_check_and_add_admin_config is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of test_check_and_add_admin_config is going on.\n")
        livechat_admin = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))
        check_and_add_admin_config(livechat_admin, LiveChatAdminConfig)
        self.assertEqual(LiveChatAdminConfig.objects.get(
            admin=livechat_admin).admin, livechat_admin)

    """
    function tested: test_save_session_details
    input queries:
        livechat_admin
        status
    expected output:
        Session details are saved into session management objects and Livechatagentnotready is updated.
    """

    def test_save_session_details(self):
        logger.info("Testing of test_save_session_details is going on.", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of test_save_session_details is going on.\n")
        livechat_admin = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))
        livechat_admin.is_online = True
        livechat_admin.save()
        LiveChatSessionManagement.objects.create(
            user=livechat_admin, session_completed=False)
        save_session_details(livechat_admin, "6",
                             LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatUser, LiveChatAdminConfig, LiveChatConfig, Bot)
        livechat_agent_not_ready = LiveChatAgentNotReady.objects.filter(
            user=livechat_admin)[0]
        livechat_session_management_obj = LiveChatSessionManagement.objects.filter(
            agent_not_ready__in=[livechat_agent_not_ready])
        livechat_agent_not_ready_bool = False
        if livechat_session_management_obj:
            livechat_agent_not_ready_bool = True
        self.assertEqual(True, livechat_agent_not_ready_bool)
        livechat_admin.is_online = False
        livechat_admin.save()
        sessions_obj = LiveChatSessionManagement.objects.filter(
            user=livechat_admin, session_completed=False)[0]
        agent_not_ready_obj = sessions_obj.agent_not_ready.all().order_by(
            '-not_ready_starts_at')[0]
        self.assertEqual(
            agent_not_ready_obj.not_ready_ends_at.date(), timezone.now().date())

    """
    function: get_translated_message_history
    input params:
        livechat_cust_obj: LiveChatCustomer
        selected_language: Language
        
    It returns message history of livechat_cust_obj with translated text as a json.
    """

    def test_get_translated_message_history(self):
        logger.info("Testing of get_translated_message_history is going on", extra={
                    'AppName': 'LiveChat'})
        print("\n\n\nTesting of get_translated_message_history is going on.\n")

        livechat_agent = LiveChatUser.objects.get(
            user=User.objects.get(username="test1234"))

        bot_obj = Bot.objects.filter(name="testbot")[0]

        livechat_customer = LiveChatCustomer.objects.create(username="langcust", agent_id=livechat_agent, is_session_exp=True, joined_date=datetime.now(
        ) - timedelta(days=8), wait_time=30, chat_duration=100, bot=bot_obj)

        LiveChatMISDashboard.objects.create(livechat_customer=livechat_customer, sender="Customer",
                                            sender_name=livechat_customer.username, text_message="test message")

        message_history = get_translated_message_history(
            livechat_customer, "hi", LiveChatMISDashboard, LiveChatTranslationCache)

        self.assertEqual(message_history[0]["message"], "परीक्षण संदेश")
        self.assertEqual(message_history[0]["sender_name"], "langcust")

    """
    function: get_translated_text
    input params:
        text to be translated
        selected_language: Language
        
    Returns translated text from LiveChatTranslationCache if present else from translate API.
    """

    # def test_get_translated_text(self):
    #     logger.info("Testing of get_translated_text is going on", extra={
    #                 'AppName': 'LiveChat'})
    #     print("\n\n\nTesting of get_translated_text is going on.\n")

    #     self.assertEqual(get_translated_text(
    #         "hello", "hi", LiveChatTranslationCache), "नमस्ते")

    """
    function: translat_via_api
    input params:
        text to be translated
        selected_language: Language
        
    Returns translated text from translate API.
    """

    # def test_translat_via_api(self):
    #     print("\n\nTesting translat_via_api function")

    #     self.assertEqual((translat_via_api("ग्राहक", "en")[0]).lower(), "customer")

    """
    function: check_and_update_user_group
    input params:
        user1: LiveChat user whose chat is converted to user group
        user2: LiveChat user who is converting the chat to user group
        
    Returns user group object.
    """

    def test_check_and_update_user_group(self):
        print("\n\nTesting check_and_update_user_group function")

        user1 = LiveChatUser.objects.get(user__username='testadmin')
        user2 = LiveChatUser.objects.get(user__username='testsupervisor')

        user_group_obj = check_and_update_user_group(
            user1, user2, LiveChatInternalUserGroup)

        self.assertEqual(list(user_group_obj.members.all()), [user1, user2])
        self.assertEqual(user_group_obj.is_converted_into_group, False)

    """
    function: store_keyword_for_livechat_intent
    input params:
        bot_pk: Bot pk for which livechat default intent keyword is added 
        whatsapp_reinitiating_keyword: keyword to be added in livechat intent
        previous_reinitiating_keyword: previously stored intent
        
    Returns user group object.
    """

    def test_store_keyword_for_livechat_intent(self):
        print("\n\nTesting store_keyword_for_livechat_intent function")

        bot = Bot.objects.filter(name="testbot").first()
        store_keyword_for_livechat_intent(bot.pk, 'Chat again', '', Bot)

        training_data = json.loads(bot.livechat_default_intent.training_data)
        self.assertEqual(training_data["2"], 'Chat again')   

    """
    function: check_if_whatsapp_keyword_present_in_intent
    input params:
        bot_pk: Bot pk for which intents are checked 
        is_whatsapp_reinitiation_enabled: designates whether whatsapp reinitiation feature is enabled
        whatsapp_reinitiating_keyword: keyword that has to be checked if it is present in any intent
        
    Returns user group object.
    """

    def test_check_if_whatsapp_keyword_present_in_intent(self):
        print("\n\nTesting check_if_whatsapp_keyword_present_in_intent function")

        bot = Bot.objects.filter(name="testbot").first()
        LiveChatConfig.objects.create(bot=bot, whatsapp_reinitiating_keyword="chat expert")

        res = check_if_whatsapp_keyword_present_in_intent(bot.pk, True, 'chat with an agent', Bot, Intent, LiveChatConfig)
        self.assertEqual(res, True)   
        
        res = check_if_whatsapp_keyword_present_in_intent(bot.pk, True, 'chat with an agent again', Bot, Intent, LiveChatConfig)
        self.assertEqual(res, False)   

        res = check_if_whatsapp_keyword_present_in_intent(bot.pk, False, 'chat with an agent', Bot, Intent, LiveChatConfig)
        self.assertEqual(res, False)   

    """
    function: get_phone_number_and_country_code
    input params:
        phone: Phone number of the customer
        channel: Channel from which customer has raised the request
        to_check_edited_number: boolean field which has to be passed true while editing customer details
        
    Returns phone number, country code and is_valid_number boolean.
    """

    def test_get_phone_number_and_country_code(self):
        print("\n\nTesting check_if_whatsapp_keyword_present_in_intent function")

        phone, country_code, is_valid_number = get_phone_number_and_country_code("+918877112233", "Web", False)
        self.assertEqual(phone, "8877112233")
        self.assertEqual(country_code, "91")
        self.assertEqual(is_valid_number, True)

        phone, country_code, is_valid_number = get_phone_number_and_country_code("91887711", "Whatsapp", False)
        self.assertEqual(phone, 'None')
        self.assertEqual(is_valid_number, True)

        phone, country_code, is_valid_number = get_phone_number_and_country_code("+918877112233", "Twitter", False)
        self.assertEqual(phone, 'None')
        self.assertEqual(country_code, "")
        self.assertEqual(is_valid_number, True)

        phone, country_code, is_valid_number = get_phone_number_and_country_code("+448877112255", "Telegram", True)
        self.assertEqual(phone, "8877112255")
        self.assertEqual(country_code, "44")
        self.assertEqual(is_valid_number, False)

    """
    function: get_prev_month
    input params:
        month: month for which prev month is required
        year: year of the month for which prev month is required
        
    Returns month, year 
    """

    def test_get_prev_month(self):
        print("\n\nTesting get_prev_month function")

        month, year = get_prev_month("4", "2022")
        self.assertEquals(month, '3')
        self.assertEquals(year, '2022')

        month, year = get_prev_month("1", "2022")
        self.assertEquals(month, '12')
        self.assertEquals(year, '2021')

    """
    function: get_next_month
    input params:
        month: month for which next month is required
        year: year of the month for which next month is required
        
    Returns month, year 
    """

    def test_get_next_month(self):
        print("\n\nTesting get_prev_month function")

        month, year = get_next_month("4", "2022")
        self.assertEquals(month, '5')
        self.assertEquals(year, '2022')

        month, year = get_next_month("12", "2022")
        self.assertEquals(month, '1')
        self.assertEquals(year, '2023')

    """
    function: convert_to_calendar
    input params:
       calendar_objs: calendar_objs which is needed to be converted to calendar template/frame
        
    Returns list : list of lists denoting calendar template/frame
    """

    def test_convert_to_calendar(self):
        logger.info("Testing of test_convert_to_calendar is going on", extra={
            'AppName': 'LiveChat'})
        print("\n\nTesting convert_to_calendar function")

        selected_month = '5'
        selected_year = '2022'
        no_days = get_number_of_day(selected_year, selected_month)  

        for day in range(1, no_days + 1):
            today_date = datetime(
                int(selected_year), int(selected_month), int(day))
            LiveChatCalender.objects.create(event_type="2", event_date=today_date, description="test-desc", auto_response="test-auto")

        calendar_objs = LiveChatCalender.objects.filter(event_date__year=int(
            selected_year), event_date__month=int(selected_month)).order_by('event_date')

        calendar_list = []
        calendar_list = convert_to_calender(calendar_objs)

        self.assertEquals(len(calendar_list), 5) 

        selected_month = '7'
        selected_year = '2022'
        no_days = get_number_of_day(selected_year, selected_month)  

        for day in range(1, no_days + 1):
            today_date = datetime(
                int(selected_year), int(selected_month), int(day))
            LiveChatCalender.objects.create(event_type="2", event_date=today_date, description="test-desc", auto_response="test-auto")

        calendar_objs = LiveChatCalender.objects.filter(event_date__year=int(
            selected_year), event_date__month=int(selected_month)).order_by('event_date')

        calendar_list = []
        calendar_list = convert_to_calender(calendar_objs)

        self.assertEquals(len(calendar_list), 6)

    """
    function: get_agents_as_per_supervisors
    input params:
        supervisors_list: List of supervisors whose agents has to be returned
        user_obj_list: Initial list of agents
        
    Returns list of agent objects under the input supervisors.
    """

    def test_get_agents_as_per_supervisors(self):
        print("\n\nTesting get_agents_as_per_supervisors function")

        supervisor = LiveChatUser.objects.get(
            user=User.objects.get(username="testsupervisor"))
        supervisor_list = [supervisor.pk]

        agent_list = get_agents_as_per_supervisors(supervisor_list, [], LiveChatUser)
        self.assertEqual(len(agent_list), 2)

        admin = LiveChatUser.objects.get(
            user=User.objects.get(username="testadmin"))

        supervisor_list = [admin.pk]
        agent_list = get_agents_as_per_supervisors(supervisor_list, [], LiveChatUser)
        self.assertEqual(len(agent_list), 1)

        agent = LiveChatUser.objects.create(status="3", user=User.objects.create(
            role="1", status="1", username="dummyagent", password="dummyagent"))

        supervisor_list = [agent.pk]
        agent_list = get_agents_as_per_supervisors(supervisor_list, [], LiveChatUser)
        self.assertEqual(len(agent_list), 0)
