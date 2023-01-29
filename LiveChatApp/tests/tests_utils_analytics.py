# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from LiveChatApp.utils_analytics import get_average, get_percentage_change, get_chat_analytics, get_livechat_avh, get_agents_availibility_analytics, get_livechat_avg_queue_time, get_livechat_avg_queue_time_filter,\
    get_livechat_avg_interaction_per_chat, get_livechat_avg_interaction_per_chat_filter, get_nps_avg, get_nps_avg_filter, get_chat_analytics_filter, get_livechat_avh_filter, get_chats_in_queue, get_livechat_chat_report_history_list,\
    get_avg_nps_list, get_livechat_avg_handle_time_list, get_livechat_avg_interaction_per_chat_list, get_percentage_change_data, get_chat_data_percentage_diff, get_customer_report_percentage_change, get_livechat_avg_queue_time_list,\
    get_livechat_avq_filter, get_total_closed_chats, get_total_closed_chats_filtered, get_followup_leads, get_followup_leads_filtered

from django.test import TestCase
from EasyChatApp.models import Bot, User, MISDashboard, Channel 
from LiveChatApp.models import LiveChatUser, LiveChatCustomer, LiveChatMISDashboard, LiveChatConfig, LiveChatAdminConfig, LiveChatCategory, LiveChatFollowupCustomer
from LiveChatApp.utils_analytics import create_excel_of_chat
from LiveChatApp.utils import get_time, get_agents_under_this_user, ensure_element_tree
import logging
import json
import sys
import xlrd
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
        easychat_user = User.objects.create(
            role="1", status="1", username="test", password="test")
        livechat_agent = LiveChatUser.objects.create(
            status="3", user=easychat_user, last_updated_time=datetime.now().replace(hour=1))
        livechat_admin = LiveChatUser.objects.create(
            status="1", user=User.objects.create(username="admin", password="admin"), last_updated_time=datetime.now().replace(hour=1))
        livechat_agent1 = LiveChatUser.objects.create(
            status="3", user=User.objects.create(username="admin2", password="admin"), last_updated_time=datetime.now().replace(hour=1))
        livechat_agent2 = LiveChatUser.objects.create(
            status="3", user=User.objects.create(username="admin1", password="admin"), is_online=True, last_updated_time=datetime.now().replace(hour=1), is_session_exp=False)
        livechat_admin.agents.add(livechat_agent)
        livechat_admin.agents.add(livechat_agent2)
        livechat_admin.agents.add(livechat_agent1)
        livechat_admin.save()
        channel_obj = Channel.objects.create(name="Web")
        livechat_customer = LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, is_session_exp=True, joined_date=datetime.now(
        ), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj, channel=channel_obj)
        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Customer", sender_name="C", text_message="Hi")
        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Agent", sender_name="C", text_message="Hi1")
        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="System", sender_name="C", text_message="Hi2")
        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Customer", sender_name="C", text_message="Hi3")
        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Customer", sender_name="C", text_message="Hi4")
        LiveChatMISDashboard.objects.create(livechat_customer=livechat_customer, sender="Agent", sender_name="C",
                                            text_message="Hi5", attachment_file_name="testing", attachment_file_path="https://allincall.in/img/test.png")
        LiveChatMISDashboard.objects.create(
            livechat_customer=livechat_customer, sender="Customer", sender_name="C", text_message="Hi6")

    """
    function: create_excel_of_chat
    input params:
        livechat_customer:
    expected output:
        returns filename and filepath of the excel file(chat transcript)

    This function creates the excel file of a livechat customer's chat.
    """

    def test_create_excel_of_chat(self):
        logger.info("Testing create_excel_of_chat...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting create_excel_of_chat...\n")

        filename, path_to_file = create_excel_of_chat(None)
        self.assertEqual(filename, "")
        self.assertEqual(path_to_file, "")

        livechat_customer = LiveChatCustomer.objects.all()[0]
        filename, path_to_file = create_excel_of_chat(livechat_customer)

        ensure_element_tree(xlrd)

        created_chat_sheet = xlrd.open_workbook(path_to_file)
        chat_sheet = created_chat_sheet.sheet_by_index(0)
        rows_limit = chat_sheet.nrows
        cols_limit = chat_sheet.ncols

        self.assertEqual(rows_limit, 14)
        self.assertEqual(cols_limit, 9)
        self.assertEqual("Hi", chat_sheet.cell_value(1, 4))
        self.assertEqual("Hi3", chat_sheet.cell_value(4, 4))
        self.assertEqual("Hi5", chat_sheet.cell_value(6, 4))

        self.assertEqual(filename, "Chat-Transcript-test.xls")

"""
Test of All functions which are independent of models
"""


class UtilsFunctionsWithoutModels(TestCase):

    def setUp(self):
        logger.info(
            "Setting up the test environment for UtilsFunctionsWithoutModels...", extra={'AppName': 'LiveChat'})

    """
    function: test_get_average
    input params:
        List of touple, in which each touple have two integres(x, y).
    expected output:
        returns the value of (x/y).

    This function is used to get Quotient of x and y. Returns 0 if y is 0.
    """

    def test_get_average(self):

        input_queries = [(4, 2), (4, 3), (5, 0)]
        expected_responses = [2, 1, 0]
        get_average_list = []
        for query in input_queries:
            get_average_list.append(get_average(query[0], query[1]))

        self.assertEqual(expected_responses, get_average_list)
        print("\n**************************************")
        print("Test for get_average PASSED!!!\n")

    """
    function: test_get_percentage_change
    input params:
        List of touple, in which each touple have two integres(x, y).
    expected output:
        returns the value of percentage increament or decreament.

    This function is used to find out percentage increament or decreament. Returns 0 if y is 0.
    """

    def test_get_percentage_change(self):

        input_queries = [(4, 2), (2, 4), (5, 0)]
        expected_responses = [100.0, -50.0, 100]
        get_percentage_change_list = []
        for query in input_queries:
            get_percentage_change_list.append(
                get_percentage_change(query[0], query[1]))

        self.assertEqual(expected_responses, get_percentage_change_list)
        print("\n**************************************")
        print("Test for get_percentage_change PASSED!!!\n")

    def test_get_percentage_change_data(self):
        yes_and_prev_data = [(4, 2), (2, 4), (5, 0), (0, 2)]
        expected_responses = [-50, 100.0, -100, "No Data Available"]
        get_percentage_change_list = []
        for query in yes_and_prev_data:
            get_percentage_change_list.append(
                get_percentage_change_data(query[0], query[1]))

        self.assertEqual(expected_responses, get_percentage_change_list)
        print("\n**************************************")
        print("Test for test_get_percentage_change_data PASSED!!!\n")


"""
Test of All functions which are dependent on models
"""


class UtilsSomeFunctionsSectionTwo(TestCase):

    def setUp(self):
        logger.info(
            "Setting up test environment for small functions of utils.py having models", extra={'AppName': 'LiveChat'})

        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        easychat_user = User.objects.create(
            role="1", status="1", username="test", password="test")
        livechat_agent = LiveChatUser.objects.create(
            status="3", user=easychat_user, last_updated_time=datetime.now().replace(hour=1))
        livechat_admin = LiveChatUser.objects.create(
            status="1", user=User.objects.create(username="admin", password="admin"), last_updated_time=datetime.now().replace(hour=1))
        livechat_agent1 = LiveChatUser.objects.create(
            status="3", user=User.objects.create(username="admin2", password="admin"), last_updated_time=datetime.now().replace(hour=1))
        livechat_agent2 = LiveChatUser.objects.create(
            status="3", user=User.objects.create(username="admin1", password="admin"), is_online=True, last_updated_time=datetime.now().replace(hour=1), is_session_exp=False)
        livechat_admin.agents.add(livechat_agent)
        livechat_admin.agents.add(livechat_agent2)
        livechat_admin.agents.add(livechat_agent1)
        livechat_admin.save()
        channel_obj = Channel.objects.create(name="Web")
        category_obj = LiveChatCategory.objects.create(title="others", bot=bot_obj)
        customer1 = LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, is_session_exp=True, joined_date=datetime.now(
        ), wait_time=1, chat_duration=10, queue_time=10, bot=bot_obj, rate_value=6, channel=channel_obj, category=category_obj)
        customer2 = LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, is_session_exp=True, joined_date=datetime.now(
        ), wait_time=10, chat_duration=10, queue_time=5, bot=bot_obj, channel=channel_obj, category=category_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=2, chat_duration=10, queue_time=7, bot=bot_obj, channel=channel_obj, category=category_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, is_session_exp=True,
                                        joined_date=datetime.now(), wait_time=3, chat_duration=10, queue_time=8, bot=bot_obj, channel=channel_obj, category=category_obj)
        customer5 = LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, is_session_exp=True, joined_date=datetime.now() - timedelta(days=8), request_raised_date=(datetime.now() - timedelta(days=8)).date(), wait_time=20, chat_duration=100, bot=bot_obj, channel=channel_obj, category=category_obj)
        customer6 = LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, is_session_exp=True, joined_date=datetime.now() - timedelta(days=8), request_raised_date=(datetime.now() - timedelta(days=8)).date(), wait_time=10, chat_duration=100, bot=bot_obj, channel=channel_obj, category=category_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, is_session_exp=True, joined_date=datetime.now() - timedelta(days=8), request_raised_date=(datetime.now() - timedelta(days=8)).date(), wait_time=20, chat_duration=100, bot=bot_obj, channel=channel_obj, category=category_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, is_session_exp=True, joined_date=datetime.now() - timedelta(days=8), request_raised_date=(datetime.now() - timedelta(days=8)).date(), wait_time=30, chat_duration=100, bot=bot_obj, channel=channel_obj, category=category_obj)
        LiveChatCustomer.objects.create(username="test", agent_id=livechat_agent, is_session_exp=True, joined_date=datetime.now() - timedelta(days=7), request_raised_date=(datetime.now() - timedelta(days=7)).date(), wait_time=10, chat_duration=100, bot=bot_obj, channel=channel_obj, category=category_obj)

        LiveChatMISDashboard.objects.create(livechat_customer=customer1)

        LiveChatFollowupCustomer.objects.create(livechat_customer=customer1, agent_id=livechat_agent, assigned_date=datetime.now())
        LiveChatFollowupCustomer.objects.create(livechat_customer=customer2, agent_id=livechat_agent, assigned_date=datetime.now())
        LiveChatFollowupCustomer.objects.create(livechat_customer=customer5, agent_id=livechat_agent, assigned_date=datetime.now() - timedelta(days=7))
        LiveChatFollowupCustomer.objects.create(livechat_customer=customer6, agent_id=livechat_agent, assigned_date=datetime.now() - timedelta(days=7))

    """
    function: get_agents_availibility_analytics
    input params:
        user_obj_list: List of agents
    expected output:
       loggen_in_agents: Total number of agents logged in
       ready_agents: Total number of agents ready to chat
       not_ready_agents: Total number of agents not ready to chat
    """

    def test_get_agents_availibility_analytics(self):
        logger.info("Testing get_agents_availibility_analytics...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_agents_availibility_analytics...\n")

        user_obj = LiveChatUser.objects.get(
            user=User.objects.get(username="admin"))
        user_obj_list = get_agents_under_this_user(user_obj)
        loggen_in_agents, ready_agents, not_ready_agents, stop_interaction_agents, current_capacity = get_agents_availibility_analytics(
            user_obj_list, LiveChatAdminConfig, LiveChatUser)
        self.assertEqual(loggen_in_agents, 0)
        self.assertEqual(ready_agents, 0)
        self.assertEqual(not_ready_agents, 0)

        user_obj_list = []
        loggen_in_agents, ready_agents, not_ready_agents, stop_interaction_agents, current_capacity = get_agents_availibility_analytics(
            user_obj_list, LiveChatAdminConfig, LiveChatUser)

        self.assertEqual(loggen_in_agents, 0)
        self.assertEqual(ready_agents, 0)
        self.assertEqual(not_ready_agents, 0)

        user_obj_list = None
        loggen_in_agents, ready_agents, not_ready_agents, stop_interaction_agents, current_capacity = get_agents_availibility_analytics(
            user_obj_list, LiveChatAdminConfig, LiveChatUser)

        self.assertEqual(loggen_in_agents, 0)
        self.assertEqual(ready_agents, 0)
        self.assertEqual(not_ready_agents, 0)

    """
    function: get_livechat_avh
    input params:
        user_obj_list: List of agents
    expected output:
        return the average chat duration(average handle time).
    """

    def test_get_livechat_avh(self):
        logger.info("Testing get_livechat_avh...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_livechat_avh...\n")
        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        avh = get_livechat_avh(user_obj_list, LiveChatCustomer)
        self.assertEqual(avh, "10s")

        user_obj_list = []
        avh = get_livechat_avh(user_obj_list, LiveChatCustomer)
        self.assertEqual(avh, "0s")

    def test_get_livechat_avh_filter(self):
        logger.info("Testing get_livechat_avh_filter...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_livechat_avh_filter...\n")
        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        start_date = datetime.now() - timedelta(days=8)
        today = datetime.now()
        channel_objs = Channel.objects.all()
        category_objs = LiveChatCategory.objects.all()
        avh = get_livechat_avh_filter(
            user_obj_list, start_date, today, channel_objs, category_objs, LiveChatCustomer)
        self.assertEqual(avh, "1m 0s")

        user_obj_list = []
        avh = get_livechat_avh_filter(
            user_obj_list, start_date, today, channel_objs, category_objs, LiveChatCustomer)
        self.assertEqual(avh, "0s")

    """
    function: get_livechat_avg_queue_time
    input params:
        user_obj_list: List of agents
    expected output:
        return the average queue time.
    """

    def test_get_livechat_avg_queue_time(self):
        logger.info("Testing get_livechat_avg_queue_time...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_livechat_avg_queue_time...\n")
        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        channel_objs = Channel.objects.all()
        category_objs = LiveChatCategory.objects.all()
        avg, _ = get_livechat_avg_queue_time(user_obj_list, channel_objs, category_objs, LiveChatCustomer)
        self.assertEqual(avg, "7s")

        user_obj_list = []
        avg = get_livechat_avh(user_obj_list, LiveChatCustomer)
        self.assertEqual(avg, "0s")

    def test_get_livechat_avg_queue_time_filter(self):
        logger.info("Testing get_livechat_avg_queue_time_filter...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_livechat_avg_queue_time_filter...\n")
        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        category_objs = LiveChatCategory.objects.all()
        start_date = datetime.now() - timedelta(days=8)
        today = datetime.now()
        channel_objs = Channel.objects.all()
        avh = get_livechat_avg_queue_time_filter(
            user_obj_list, start_date, today, category_objs, LiveChatCustomer)
        self.assertEqual(avh, "3s")

        user_obj_list = []
        avh = get_livechat_avh_filter(
            user_obj_list, start_date, today, channel_objs, category_objs, LiveChatCustomer)
        self.assertEqual(avh, "0s")

    def test_get_livechat_avq_filter(self):
        logger.info("Testing get_livechat_avq_filter...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_livechat_avq_filter...\n")
        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        start_date = datetime.now() - timedelta(days=8)
        today = datetime.now()
        channel_objs = Channel.objects.all()
        category_objs = LiveChatCategory.objects.all()
        avq = get_livechat_avq_filter(
            user_obj_list, start_date, today, channel_objs, category_objs, LiveChatCustomer)
        self.assertEqual(avq, "3s")

        user_obj_list = []
        avq = get_livechat_avq_filter(
            user_obj_list, start_date, today, channel_objs, category_objs, LiveChatCustomer)
        self.assertEqual(avq, "0s")

    """
    function: get_chat_analytics
    input params:
        user_obj_list: List of agents
    expected output:
        total_entered_chat: Total number of chat request raised
        total_closed_chat: Total number of chats which have been closed by agents.
        denied_chats: Total number of chat which have been denied by system, due to unavailibility of agents.
    """

    def test_get_chat_analytics(self):
        logger.info("Testing get_chat_analytics...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_chat_analytics...\n")

        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        channel_objs = Channel.objects.all()
        category_objs = LiveChatCategory.objects.all()
        # user_obj = LiveChatUser.objects.get(
        #     user=User.objects.get(username="admin"))
        total_entered_chat, total_closed_chat, denied_chats, chats_in_queue, abandon_chats, customer_declined_chats = get_chat_analytics(
            user_obj_list, channel_objs, category_objs, Bot, LiveChatCustomer, LiveChatConfig)

        self.assertEqual(total_entered_chat, 4)
        self.assertEqual(total_closed_chat, 4)
        self.assertEqual(denied_chats, 0)

        user_obj_list = []
        total_entered_chat, total_closed_chat, denied_chats, chats_in_queue, abandon_chats, customer_declined_chats = get_chat_analytics(
            user_obj_list, channel_objs, category_objs, Bot, LiveChatCustomer, LiveChatConfig)

        self.assertEqual(total_entered_chat, 0)
        self.assertEqual(total_closed_chat, 0)
        self.assertEqual(denied_chats, 0)

    def test_get_chat_analytics_filter(self):
        logger.info("Testing get_chat_analytics_filter...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_chat_analytics_filter...\n")

        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        channel_objs = Channel.objects.all()
        category_objs = LiveChatCategory.objects.all()
        # user_obj = LiveChatUser.objects.get(
        #     user=User.objects.get(username="admin"))
        start_date = datetime.now() - timedelta(days=8)
        today = datetime.now()
        total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats = get_chat_analytics_filter(
            user_obj_list, start_date, today, channel_objs, category_objs, Bot, LiveChatCustomer, LiveChatConfig)

        self.assertEqual(total_entered_chat, 9)
        self.assertEqual(total_closed_chat, 9)
        self.assertEqual(denied_chats, 0)
        self.assertEqual(abandon_chats, 0)
        self.assertEqual(customer_declined_chats, 0)

        user_obj_list = []
        total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats = get_chat_analytics_filter(
            user_obj_list, start_date, today, channel_objs, category_objs, Bot, LiveChatCustomer, LiveChatConfig)

        self.assertEqual(total_entered_chat, 0)
        self.assertEqual(total_closed_chat, 0)
        self.assertEqual(denied_chats, 0)
        self.assertEqual(abandon_chats, 0)
        self.assertEqual(customer_declined_chats, 0)

    """
    function tested: get_nps_avg
    input params:
        user_obj_list: List of agents
    expected output:
        nps_avg: The average NPS score given by customers upto that 
                 particular point in a day.
    checks for: 1.if only one user gave nps and it is 6, it should return -100
                2.if user_obj_list is empty it should return 0
    """

    def test_get_nps_avg(self):
        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))

        nps_avg = get_nps_avg(user_obj_list, LiveChatCustomer)
        self.assertEqual(nps_avg, -100)

        user_obj_list = []
        nps_avg = get_nps_avg(user_obj_list, LiveChatCustomer)
        self.assertEqual(nps_avg, 0)

    def test_get_nps_avg_filter(self):
        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        start_date = datetime.now() - timedelta(days=8)
        today = datetime.now()
        channel_objs = Channel.objects.all()
        category_objs = LiveChatCategory.objects.all()

        nps_avg = get_nps_avg_filter(
            user_obj_list, start_date, today, channel_objs, category_objs, LiveChatCustomer)
        self.assertEqual(nps_avg, -100)

        user_obj_list = []
        nps_avg = get_nps_avg_filter(
            user_obj_list, start_date, today, channel_objs, category_objs, LiveChatCustomer)
        self.assertEqual(nps_avg, 0)

    """
    function tested: get_livechat_avg_interaction_per_chat
    input params:
        user_obj_list: List of agents
    expected output:
        return the average interaction per chat.
    checks for: 1.if no of customers are greater than 1 and if current agent interacts with only one customer,it should return 0
                2.if user_obj_list is empty it should return 0
    """

    def test_get_livechat_avg_interaction_per_chat(self):
        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))

        avg_interaction = get_livechat_avg_interaction_per_chat(
            user_obj_list, LiveChatCustomer, LiveChatMISDashboard)
        self.assertEqual(avg_interaction, 0)

        user_obj_list = []
        avg_interaction = get_livechat_avg_interaction_per_chat(
            user_obj_list, LiveChatCustomer, LiveChatMISDashboard)
        self.assertEqual(avg_interaction, 0)

    def test_get_livechat_avg_interaction_per_chat_filter(self):
        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        start_date = datetime.now() - timedelta(days=8)
        today = datetime.now()
        channel_objs = Channel.objects.all()
        category_objs = LiveChatCategory.objects.all()

        avg_interaction = get_livechat_avg_interaction_per_chat_filter(
            user_obj_list, start_date, today, channel_objs, category_objs, LiveChatCustomer, LiveChatMISDashboard)
        self.assertEqual(avg_interaction, 0)

        user_obj_list = []
        avg_interaction = get_livechat_avg_interaction_per_chat_filter(
            user_obj_list, start_date, today, channel_objs, category_objs, LiveChatCustomer, LiveChatMISDashboard)
        self.assertEqual(avg_interaction, 0)

    def test_get_chats_in_queue(self):
        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        channel_objs = Channel.objects.all()
        category_objs = LiveChatCategory.objects.all()
        bot_objs = Bot.objects.none()
        chats_in_queue = get_chats_in_queue(
            user_obj_list, channel_objs, category_objs, bot_objs, LiveChatCustomer, LiveChatConfig)
        self.assertEqual(chats_in_queue, 0)
        bot_objs = Bot.objects.all()
        LiveChatConfig.objects.create(bot=bot_objs[0], queue_timer=90)
        LiveChatCustomer.objects.create(joined_date=datetime.now() - timedelta(seconds=20), agent_id=None,
                                        is_system_denied=False, abruptly_closed=False, is_denied=False, is_session_exp=False, bot=bot_objs[0], channel=channel_objs[0], category=category_objs[0])
        chats_in_queue = get_chats_in_queue(
            user_obj_list, channel_objs, category_objs, bot_objs, LiveChatCustomer, LiveChatConfig)

        self.assertEqual(chats_in_queue, 1)
        print("test_get_chats_in_queue passed")

    def test_get_livechat_chat_report_history_list(self):
        start_date = ""
        end_date = ""
        is_filter_applied = False
        user_obj_list = []
        channel_objs = Channel.objects.all()
        category_objs = LiveChatCategory.objects.all()

        chat_his_list, total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats = get_livechat_chat_report_history_list(
            start_date, end_date, channel_objs, category_objs, user_obj_list, is_filter_applied, Bot, LiveChatConfig, LiveChatCustomer)
        self.assertEqual(len(chat_his_list), 7)

        start_date = str((datetime.now() - timedelta(days=3)).date())
        end_date = str((datetime.now() - timedelta(days=1)).date())
        is_filter_applied = True
        user_obj_list = []

        chat_his_list, total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats = get_livechat_chat_report_history_list(
            start_date, end_date, channel_objs, category_objs, user_obj_list, is_filter_applied, Bot, LiveChatConfig, LiveChatCustomer)
        self.assertEqual(len(chat_his_list), 3)

    def test_get_avg_nps_list(self):
        start_date = ""
        end_date = ""
        is_filter_applied = False
        user_obj_list = []
        channel_objs = Channel.objects.all()
        category_objs = LiveChatCategory.objects.all()

        chat_his_list, _ = get_avg_nps_list(
            start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer)
        self.assertEqual(len(chat_his_list), 7)

        start_date = str((datetime.now() - timedelta(days=3)).date())
        end_date = str((datetime.now() - timedelta(days=1)).date())
        is_filter_applied = True
        user_obj_list = []

        chat_his_list, _ = get_avg_nps_list(
            start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer)
        self.assertEqual(len(chat_his_list), 3)

    def test_get_livechat_avg_interaction_per_chat_list(self):
        start_date = ""
        end_date = ""
        is_filter_applied = False
        user_obj_list = []
        channel_objs = Channel.objects.all()
        category_objs = LiveChatCategory.objects.all()

        chat_his_list, _ = get_livechat_avg_interaction_per_chat_list(
            start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer, LiveChatMISDashboard)
        self.assertEqual(len(chat_his_list), 7)

        start_date = str((datetime.now() - timedelta(days=3)).date())
        end_date = str((datetime.now() - timedelta(days=1)).date())
        is_filter_applied = True
        user_obj_list = []

        chat_his_list, _ = get_livechat_avg_interaction_per_chat_list(
            start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer, LiveChatMISDashboard)
        self.assertEqual(len(chat_his_list), 3)

    def test_get_livechat_avg_handle_time_list(self):
        start_date = ""
        end_date = ""
        is_filter_applied = False
        user_obj_list = []
        channel_objs = Channel.objects.all()
        category_objs = LiveChatCategory.objects.all()

        chat_his_list, _ = get_livechat_avg_handle_time_list(
            start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer)
        self.assertEqual(len(chat_his_list), 7)

        start_date = str((datetime.now() - timedelta(days=3)).date())
        end_date = str((datetime.now() - timedelta(days=1)).date())
        is_filter_applied = True
        user_obj_list = []

        chat_his_list, _ = get_livechat_avg_handle_time_list(
            start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer)
        self.assertEqual(len(chat_his_list), 3)

    def test_get_livechat_avg_queue_time_list(self):
        start_date = ""
        end_date = ""
        is_filter_applied = False
        user_obj_list = []
        channel_objs = Channel.objects.all()
        category_objs = LiveChatCategory.objects.all()

        chat_his_list, _ = get_livechat_avg_queue_time_list(
            start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer)
        self.assertEqual(len(chat_his_list), 7)

        start_date = str((datetime.now() - timedelta(days=3)).date())
        end_date = str((datetime.now() - timedelta(days=1)).date())
        is_filter_applied = True
        user_obj_list = []

        chat_his_list, _ = get_livechat_avg_handle_time_list(
            start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer)
        self.assertEqual(len(chat_his_list), 3)

    def test_get_chat_data_percentage_diff(self):
        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        user_obj = user_obj_list[0]
        user_obj.bots.add(Bot.objects.all()[0])
        user_obj.save()
        total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats = 0, 0, 0, 0, 0
        total_entered_chat_percent_change, total_closed_chat_percent_change, denied_chats_percent_change, abandon_chats_percent_change, customer_declined_chats_percent_change = get_chat_data_percentage_diff(
            total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats, user_obj_list, Bot, LiveChatCustomer)
        self.assertEqual(total_entered_chat_percent_change,
                         "No Data Available")
        self.assertEqual(total_closed_chat_percent_change, "No Data Available")
        self.assertEqual(denied_chats_percent_change, "No Data Available")
        self.assertEqual(abandon_chats_percent_change, "No Data Available")
        self.assertEqual(
            customer_declined_chats_percent_change, "No Data Available")

        LiveChatCustomer.objects.create(is_session_exp=True, agent_id=user_obj, joined_date=datetime.now() - timedelta(days=1), request_raised_date=(datetime.now() - timedelta(days=1)).date(), bot=Bot.objects.all()[0])
        LiveChatCustomer.objects.create(is_session_exp=False, agent_id=user_obj, joined_date=datetime.now() - timedelta(days=1), request_raised_date=(datetime.now() - timedelta(days=1)).date(), bot=Bot.objects.all()[0])
        LiveChatCustomer.objects.create(is_denied=True, is_system_denied=False, joined_date=datetime.now() - timedelta(days=1), request_raised_date=(datetime.now() - timedelta(days=1)).date(), bot=Bot.objects.all()[0])
        LiveChatCustomer.objects.create(joined_date=datetime.now() - timedelta(days=1), request_raised_date=(datetime.now() - timedelta(days=1)).date(), agent_id=None, abruptly_closed=True, bot=Bot.objects.all()[0])
        LiveChatCustomer.objects.create(is_system_denied=False, joined_date=datetime.now() - timedelta(days=1), request_raised_date=(datetime.now() - timedelta(days=1)).date(), bot=Bot.objects.all()[0])

        total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats = 0, 0, 0, 0, 0
        total_entered_chat_percent_change, total_closed_chat_percent_change, denied_chats_percent_change, abandon_chats_percent_change, customer_declined_chats_percent_change = get_chat_data_percentage_diff(
            total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats, user_obj_list, Bot, LiveChatCustomer)

        self.assertEqual(total_entered_chat_percent_change, -100)
        self.assertEqual(total_closed_chat_percent_change, -100)
        self.assertEqual(denied_chats_percent_change, -100)
        self.assertEqual(abandon_chats_percent_change, "No Data Available")
        self.assertEqual(customer_declined_chats_percent_change, -100)

        total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats = 2, 1, 3, 0, 4
        total_entered_chat_percent_change, total_closed_chat_percent_change, denied_chats_percent_change, abandon_chats_percent_change, customer_declined_chats_percent_change = get_chat_data_percentage_diff(
            total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats, user_obj_list, Bot, LiveChatCustomer)

        self.assertEqual(total_entered_chat_percent_change, -50)
        self.assertEqual(total_closed_chat_percent_change, 0)
        self.assertEqual(denied_chats_percent_change, 200)
        self.assertEqual(abandon_chats_percent_change, "No Data Available")
        self.assertEqual(customer_declined_chats_percent_change, 300)

    def test_get_customer_report_percentage_change(self):
        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        user_obj = user_obj_list[0]
        user_obj.bots.add(Bot.objects.all()[0])
        user_obj.save()

        cust_obj1 = LiveChatCustomer.objects.create(
            rate_value=9, chat_duration=10, agent_id=user_obj, joined_date=datetime.now() - timedelta(days=1), request_raised_date=(datetime.now() - timedelta(days=1)).date(), bot=Bot.objects.all()[0])
        cust_obj2 = LiveChatCustomer.objects.create(
            rate_value=10, chat_duration=20, agent_id=user_obj, joined_date=datetime.now() - timedelta(days=1), request_raised_date=(datetime.now() - timedelta(days=1)).date(), bot=Bot.objects.all()[0])

        LiveChatMISDashboard.objects.create(livechat_customer=cust_obj1)
        LiveChatMISDashboard.objects.create(livechat_customer=cust_obj1)
        LiveChatMISDashboard.objects.create(livechat_customer=cust_obj1)
        LiveChatMISDashboard.objects.create(livechat_customer=cust_obj1)
        LiveChatMISDashboard.objects.create(livechat_customer=cust_obj2)
        LiveChatMISDashboard.objects.create(livechat_customer=cust_obj2)
        avg_nps, avg_handle_time, interactions_per_chat = 0, 0, 0
        avg_nps_percent_change, avg_handle_time_percent_change, avg_inter_per_chat_percent_change = get_customer_report_percentage_change(
            avg_nps, avg_handle_time, interactions_per_chat, user_obj_list, LiveChatCustomer, LiveChatMISDashboard)

        self.assertEqual(avg_nps_percent_change, -100)
        self.assertEqual(avg_handle_time_percent_change, -100)
        self.assertEqual(avg_inter_per_chat_percent_change, -100)

        avg_nps, avg_handle_time, interactions_per_chat = 50, 10, 6
        avg_nps_percent_change, avg_handle_time_percent_change, avg_inter_per_chat_percent_change = get_customer_report_percentage_change(
            avg_nps, avg_handle_time, interactions_per_chat, user_obj_list, LiveChatCustomer, LiveChatMISDashboard)

        self.assertEqual(avg_nps_percent_change, -50)
        self.assertEqual(avg_handle_time_percent_change, -33)
        self.assertEqual(avg_inter_per_chat_percent_change, 100)

    def test_get_total_closed_chats(self):
        logger.info("Testing get_total_closed_chats...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_total_closed_chats...\n")

        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))

        total_closed_chats, percentage_change = get_total_closed_chats(user_obj_list, LiveChatCustomer)

        self.assertEqual(total_closed_chats, 4)
        self.assertEqual(percentage_change, 'No Data Available')

        LiveChatCustomer.objects.create(is_session_exp=True, agent_id=user_obj_list[0], joined_date=datetime.now() - timedelta(days=1), request_raised_date=(datetime.now() - timedelta(days=1)).date(), bot=Bot.objects.all()[0])

        total_closed_chats, percentage_change = get_total_closed_chats(user_obj_list, LiveChatCustomer)

        self.assertEqual(total_closed_chats, 4)
        self.assertEqual(percentage_change, 300)

        user_obj_list = []
        total_closed_chats, percentage_change = get_total_closed_chats(user_obj_list, LiveChatCustomer)

        self.assertEqual(total_closed_chats, 0)

    def test_get_total_closed_chats_filtered(self):
        logger.info("Testing get_total_closed_chats_filtered...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_total_closed_chats_filtered...\n")

        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        channel_objs = Channel.objects.all()

        start_date = datetime.now() - timedelta(days=8)
        today = datetime.now()

        total_closed_chats = get_total_closed_chats_filtered(start_date, today, channel_objs, user_obj_list, LiveChatCustomer)

        self.assertEqual(total_closed_chats, 9)

        user_obj_list = []
        total_closed_chats = get_total_closed_chats_filtered(start_date, today, channel_objs, user_obj_list, LiveChatCustomer)

        self.assertEqual(total_closed_chats, 0)

    def test_get_followup_leads(self):
        logger.info("Testing get_followup_leads...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_followup_leads...\n")  
        
        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))

        total_followup_leads, percentage_change = get_followup_leads(user_obj_list, LiveChatFollowupCustomer)

        self.assertEqual(total_followup_leads, 2)
        self.assertEqual(percentage_change, 'No Data Available')

        customer = LiveChatCustomer.objects.all()[0]
        LiveChatFollowupCustomer.objects.create(livechat_customer=customer, agent_id=user_obj_list[0], assigned_date=datetime.now() - timedelta(days=1))

        total_followup_leads, percentage_change = get_followup_leads(user_obj_list, LiveChatFollowupCustomer)

        self.assertEqual(total_followup_leads, 2)
        self.assertEqual(percentage_change, 100)

        user_obj_list = []
        total_followup_leads, percentage_change = get_followup_leads(user_obj_list, LiveChatFollowupCustomer)      

        self.assertEqual(total_followup_leads, 0)

    def test_get_followup_leads_filtered(self):
        logger.info("Testing get_followup_leads_filtered...",
                    extra={'AppName': 'LiveChat'})
        print("\nTesting get_followup_leads_filtered...\n")  

        user_obj_list = LiveChatUser.objects.filter(
            user=User.objects.get(username="test"))
        channel_objs = Channel.objects.all()

        start_date = datetime.now() - timedelta(days=8)
        today = datetime.now()

        total_followup_leads = get_followup_leads_filtered(start_date, today, channel_objs, user_obj_list, LiveChatFollowupCustomer)

        self.assertEqual(total_followup_leads, 4)

        user_obj_list = []
        total_followup_leads = get_followup_leads_filtered(start_date, today, channel_objs, user_obj_list, LiveChatFollowupCustomer)

        self.assertEqual(total_followup_leads, 0)
