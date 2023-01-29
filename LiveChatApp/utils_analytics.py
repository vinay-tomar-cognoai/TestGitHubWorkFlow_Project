from datetime import datetime, timedelta
import os
import sys
import json
import logging
import threading
import xlwt
import pytz

from xlwt import Workbook, Formula
from os import path
from zipfile import ZipFile
from os.path import basename
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from django.db.models import Q
from django.db.models import Count
from django.http import FileResponse
from LiveChatApp.utils import create_export_request, export_custom_chat_history, get_livechat_date_format, get_time, get_milliseconds_to_datetime, get_agents_under_this_user, is_agent_live, get_admin_config, get_admin_from_active_agent, export_today_data, get_html_body_for_mailer_report, is_kafka_enabled
from LiveChatApp.constants import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from LiveChatApp.models import LiveChatFileAccessManagement, LiveChatConfig
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses
logger = logging.getLogger(__name__)


"""
function: get_chat_analytics
input params:
    user_obj_list: List of agents
expected output:
    total_entered_chat: Total number of chat request raised
    total_closed_chat: Total number of chats which have been closed by agents.
    denied_chats: Total number of chat which have been denied by system, due to unavailibility of agents.

"""


def get_chat_analytics(user_obj_list, channel_objs, category_objs, Bot, LiveChatCustomer, LiveChatConfig):
    try:

        total_entered_chat = 0
        total_closed_chat = 0
        denied_chats = 0
        chats_in_queue = 0
        abandon_chats = 0
        bot_objs = Bot.objects.none()
        for user_obj in user_obj_list:
            bot_objs |= user_obj.bots.all()
        bot_objs = bot_objs.distinct()

        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date=datetime.now().date(), agent_id__in=user_obj_list)
        total_entered_chat = livechat_cust_objs.count()
        total_closed_chat = livechat_cust_objs.filter(
            is_session_exp=True).count()
        denied_chats += LiveChatCustomer.objects.filter(bot__in=bot_objs,
                                                        request_raised_date=datetime.now().date(), is_denied=True, is_system_denied=False).count()
        chats_in_queue = get_chats_in_queue(
            user_obj_list, channel_objs, category_objs, bot_objs, LiveChatCustomer, LiveChatConfig)
        abandon_chats = LiveChatCustomer.objects.filter(
            request_raised_date=datetime.now().date(), is_system_denied=True, bot__in=bot_objs).count()
        customer_declined_chats = LiveChatCustomer.objects.filter(
            request_raised_date=datetime.now().date(), agent_id=None, abruptly_closed=True, bot__in=bot_objs).count()

        return total_entered_chat + denied_chats + abandon_chats + customer_declined_chats, total_closed_chat, denied_chats, chats_in_queue, abandon_chats, customer_declined_chats
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_chat_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0, 0, 0, 0, 0, 0


def get_chats_in_queue(user_obj_list, channel_objs, category_objs, bot_objs, LiveChatCustomer, LiveChatConfig):
    try:
        if not len(bot_objs):

            for user_obj in user_obj_list:
                bot_objs |= user_obj.bots.all()

            bot_objs = bot_objs.distinct()
        chats_in_queue = 0
        for bot in bot_objs:
            try:
                config_seconds = LiveChatConfig.objects.get(
                    bot=bot).queue_timer
                timedelta_obj = datetime.now() - timedelta(seconds=config_seconds)
                chats_in_queue += LiveChatCustomer.objects.filter(
                    request_raised_date=datetime.now().date(), agent_id=None, is_system_denied=False, abruptly_closed=False, is_denied=False, is_session_exp=False, joined_date__gte=timedelta_obj, bot=bot, category__in=category_objs, channel__in=channel_objs).count()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Inside get_chat_analytics some error in Django get query: %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return chats_in_queue
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_chats in queue: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0


def get_chat_analytics_filter(user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, Bot, LiveChatCustomer, LiveChatConfig):
    try:
        total_entered_chat = 0
        total_closed_chat = 0
        denied_chats = 0
        abandon_chats = 0
        bot_objs = Bot.objects.none()
        for user_obj in user_obj_list:
            bot_objs |= user_obj.bots.all()
        bot_objs = bot_objs.distinct()
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date__range=[datetime_start, datetime_end], agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs)

        total_entered_chat = livechat_cust_objs.count()
        total_closed_chat = livechat_cust_objs.filter(
            is_session_exp=True).count()
        denied_chats += LiveChatCustomer.objects.filter(bot__in=bot_objs,
                                                        request_raised_date__range=[datetime_start, datetime_end], is_denied=True, is_system_denied=False, category__in=category_objs).count()

        abandon_chats = LiveChatCustomer.objects.filter(bot__in=bot_objs,
                                                        request_raised_date__range=[datetime_start, datetime_end], is_system_denied=True, channel__in=channel_objs, category__in=category_objs).count()

        customer_declined_chats = LiveChatCustomer.objects.filter(bot__in=bot_objs,
                                                                  request_raised_date__range=[datetime_start, datetime_end], agent_id=None, abruptly_closed=True, channel__in=channel_objs, category__in=category_objs).count()

        return total_entered_chat + denied_chats + abandon_chats + customer_declined_chats, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_chat_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0, 0, 0, 0, 0, 0


"""
function: get_average
input params:
    Takes two integers x and y
expected output:
    returns the value of (x/y).

This function is used to get Quotient of x and y. Returns 0 if y is 0.
"""


def get_average(numerator_value, denominator_value):
    try:
        return numerator_value // denominator_value
    except Exception:
        return 0


"""
function: get_livechat_avh
input params:
    user_obj_list: List of agents
expected output:
    return the average chat duration(average handle time).
"""


def get_livechat_avh(user_obj_list, LiveChatCustomer):
    try:
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date=datetime.now().date(), agent_id__in=user_obj_list)
        average_handle_time = 0

        total_handle = livechat_cust_objs.aggregate(Sum('chat_duration'))[
            'chat_duration__sum']
        average_handle_time = get_average(
            total_handle, livechat_cust_objs.count())

        time = get_analytics_time_format(average_handle_time)

        return time
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_livechat_avh: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0s"


def get_livechat_avh_filter(user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatCustomer):
    try:
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date__range=[datetime_start, datetime_end], agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs)

        average_handle_time = 0
        total_handle = livechat_cust_objs.aggregate(Sum('chat_duration'))[
            'chat_duration__sum']
        average_handle_time = get_average(
            total_handle, livechat_cust_objs.count())
        hour = average_handle_time // 3600
        rem = average_handle_time % 3600
        minute = rem // 60
        sec = rem % 60
        time = ""
        if hour != 0:
            time = str(hour) + "h "
        if minute != 0:
            time += str(minute) + "m "

        time += str(sec) + "s"
        return time
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_livechat_avh: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0s"


def get_livechat_avq_filter(user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatCustomer):
    try:
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date__range=[datetime_start, datetime_end], agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs)

        average_queue_time = 0
        total_queue = livechat_cust_objs.aggregate(Sum('queue_time'))[
            'queue_time__sum']
        average_queue_time = get_average(
            total_queue, livechat_cust_objs.count())
        hour = average_queue_time // 3600
        rem = average_queue_time % 3600
        minute = rem // 60
        sec = rem % 60
        time = ""
        if hour != 0:
            time = str(hour) + "h "
        if minute != 0:
            time += str(minute) + "m "

        time += str(sec) + "s"
        return time
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_livechat_avq_filter: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0s"


"""
function: get_livechat_avg_queue_time
input params:
    user_obj_list: List of agents
expected output:
    return the average queue time.
"""


def get_livechat_avg_queue_time(user_obj_list, channel_objs, category_objs, LiveChatCustomer):
    try:
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date=datetime.now().date(), agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs)
        yesterdays_livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date=(datetime.now() - timedelta(days=1)).date(), agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs)
        average_queue_time = 0
        total_queue = livechat_cust_objs.aggregate(Sum('queue_time'))[
            'queue_time__sum']
        total_yest_queue = yesterdays_livechat_cust_objs.aggregate(Sum('queue_time'))[
            'queue_time__sum']
        if not total_yest_queue:
            total_yest_queue = 0
        avg_time_for_yesterday = get_average(
            total_yest_queue, yesterdays_livechat_cust_objs.count())

        average_queue_time = get_average(
            total_queue, livechat_cust_objs.count())
        percentage_change = get_percentage_change_data(
            avg_time_for_yesterday, average_queue_time)
        hour = average_queue_time // 3600
        rem = average_queue_time % 3600
        minute = rem // 60
        sec = rem % 60
        time = ""
        if hour != 0:
            time = str(hour) + "h "
        if minute != 0:
            time += str(minute) + "m "

        time += str(sec) + "s"
        return time, percentage_change
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_livechat_avg_queue_time: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0s", 0


def get_livechat_avg_first_time_response(user_obj_list, channel_objs, category_objs, LiveChatCustomer, start_date=None, end_date=None, is_daily_data=True):
    try:

        if is_daily_data:
            livechat_cust_objs = LiveChatCustomer.objects.filter(
                request_raised_date=datetime.now().date(), agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs, agent_first_time_response_time__isnull=False)
        else:
            livechat_cust_objs = LiveChatCustomer.objects.filter(request_raised_date__range=[
                                                                 start_date, end_date], agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs, agent_first_time_response_time__isnull=False)

        avg_first_time_response = 0
        avg_first_time_response = livechat_cust_objs.aggregate(Sum('agent_first_time_response_time'))[
            'agent_first_time_response_time__sum']

        if not livechat_cust_objs:
            avg_first_time_response = 0

        avg_first_time_response = get_average(
            avg_first_time_response, livechat_cust_objs.count())

        hour = avg_first_time_response // 3600
        rem = avg_first_time_response % 3600
        minute = rem // 60
        sec = rem % 60
        time = ""
        if hour != 0:
            time = str(hour) + "h "
        if minute != 0:
            time += str(minute) + "m "

        time += str(sec) + "s"
        return time
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_livechat_avg_first_time_response: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0s"


def get_livechat_avg_queue_time_filter(user_obj_list, datetime_start, datetime_end, category_objs, LiveChatCustomer):
    try:
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date__range=[datetime_start, datetime_end], agent_id__in=user_obj_list, category__in=category_objs)
        average_queue_time = 0
        total_queue = livechat_cust_objs.aggregate(Sum('queue_time'))[
            'queue_time__sum']

        average_queue_time = get_average(
            total_queue, livechat_cust_objs.count())
        hour = average_queue_time // 3600
        rem = average_queue_time % 3600
        minute = rem // 60
        sec = rem % 60
        time = ""
        if hour != 0:
            time = str(hour) + "h "
        if minute != 0:
            time += str(minute) + "m "

        time += str(sec) + "s"
        return time
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_livechat_avg_queue_time_filter: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0s"


"""
function: get_livechat_avg_interaction_per_chat
input params:
    user_obj_list: List of agents
expected output:
    return the average interaction per chat.
"""


def get_livechat_avg_interaction_per_chat(user_obj_list, LiveChatCustomer, LiveChatMISDashboard):
    try:
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date=datetime.now().date(), agent_id__in=user_obj_list)
        average_interactions = 0
        total_interactions = LiveChatMISDashboard.objects.filter(
            livechat_customer__in=livechat_cust_objs).count()

        average_interactions = get_average(
            total_interactions, livechat_cust_objs.count())

        return average_interactions
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_livechat_avg_interaction_per_chat: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0"


def get_livechat_avg_interaction_per_chat_filter(user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatCustomer, LiveChatMISDashboard):
    try:
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date__range=[datetime_start, datetime_end], agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs)
        average_interactions = 0
        total_interactions = LiveChatMISDashboard.objects.filter(
            livechat_customer__in=livechat_cust_objs).count()

        average_interactions = get_average(
            total_interactions, livechat_cust_objs.count())

        return average_interactions
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_livechat_avg_interaction_per_chat: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0"


"""
function: get_agents_availibility_analytics
input params:
    user_obj_list: List of agents
expected output:
    loggen_in_agents: Total number of agents logged in
    ready_agents: Total number of agents ready to chat
    not_ready_agents: Total number of agents not ready to chat

"""


def get_agents_availibility_analytics(user_obj_list, LiveChatAdminConfig, LiveChatUser):
    try:
        loggen_in_agents = 0
        ready_agents = 0
        not_ready_agents = 0
        stop_interaction_agents = 0
        current_capacity = 0

        if len(user_obj_list) == 0:
            return 0, 0, 0, 0, 0

        admin_config = get_admin_config(
            user_obj_list[0], LiveChatAdminConfig, LiveChatUser)
        livechat_config_objs = admin_config.livechat_config.all()

        for user in user_obj_list:
            bot_obj = user.bots.filter(is_deleted=False)

            if bot_obj:
                bot_obj = bot_obj[0]
            else:
                continue

            livechat_config_obj = livechat_config_objs.filter(bot=bot_obj)
            if livechat_config_obj:
                livechat_config_obj = livechat_config_obj[0]
            else:
                continue

            max_customer_count = user.max_customers_allowed
            if max_customer_count == -1:
                max_customer_count = livechat_config_obj.max_customer_count

            if is_agent_live(user) and not user.is_session_exp:
                loggen_in_agents += 1    
                if user.is_online:
                    ready_agents += 1
                    current_capacity += max_customer_count
                elif user.current_status == "0":
                    stop_interaction_agents += 1
                else:
                    not_ready_agents += 1

        return loggen_in_agents, ready_agents, not_ready_agents, stop_interaction_agents, current_capacity
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_agents_availibility_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0, 0, 0, 0, 0


"""
function: get_percentage_change
input params:
    Takes two integers x and y
expected output:
    returns the value of percentage increament or decreament.

This function is used to find out percentage increament or decreament. Returns 0 if y is 0.
"""


def get_percentage_change(current_value, total_value):
    try:
        increase = current_value - total_value
        percentage_increase = (increase / total_value) * 100
        return percentage_increase
    except Exception:
        return 100


"""
function: create_excel_of_chat
input params:
    livechat_customer:
expected output:
    returns filename and filepath of the excel file(chat transcript)

This function creates the excel file of a livechat customer's chat.
"""


def create_excel_of_chat(livechat_customer, is_original_information_in_reports_enabled=True):
    filename = ""
    path_to_file = ""
    index = 0
    try:
        from xlwt import Workbook, Formula
        import datetime
        chat_transcript = Workbook()
        sheet1 = chat_transcript.add_sheet("Chat Transcript")

        sheet1.write(0, 0, "Date")
        sheet1.col(0).width = 256 * 15
        sheet1.write(0, 1, "Time")
        sheet1.col(1).width = 256 * 10
        sheet1.write(0, 2, "User")
        sheet1.col(2).width = 256 * 15
        sheet1.write(0, 3, "Name")
        sheet1.col(3).width = 256 * 12
        sheet1.write(0, 4, "Message")
        sheet1.col(4).width = 256 * 50
        sheet1.write(0, 5, "Attachment")
        sheet1.col(5).width = 256 * 20

        livechat_message_history = livechat_customer.get_messages_list()
        for message in livechat_message_history:
            if message.message_for == "customer" and message.sender == "System" and (message.is_voice_call_message or message.is_cobrowsing_message or message.is_file_not_support_message):
                continue
            if message.sender != "Supervisor":
                sheet1.write(
                    index + 1, 0, get_livechat_date_format(message.message_time))
                sheet1.write(index + 1, 1, get_time(message.message_time))
                sheet1.write(index + 1, 2, message.sender)
                sheet1.write(index + 1, 3, message.sender_name)
                if message.attachment_file_path != "":
                    attachment_file_path = '"' + str(settings.EASYCHAT_HOST_URL) + \
                        str(message.attachment_file_path) + \
                        "/?source=excel" + '"'
                    sheet1.write(
                        index + 1, 5, Formula('HYPERLINK(%s;"Attachment Link")' % attachment_file_path))
                if message.text_message != "":
                    sheet1.write(index + 1, 4, message.text_message)
                index = index + 1

        sheet1.write(1, 7, "Customer Details")
        sheet1.write(3, 7, "Name")
        if is_original_information_in_reports_enabled and livechat_customer.original_username != "" and livechat_customer.username != livechat_customer.original_username:
            sheet1.write(3, 8, str(livechat_customer.username) +
                         "(original - " + str(livechat_customer.original_username) + ")")
        else:
            sheet1.write(3, 8, str(livechat_customer.username))
        sheet1.write(4, 7, "Email ID")
        if is_original_information_in_reports_enabled and livechat_customer.original_email != "" and livechat_customer.email != livechat_customer.original_email:
            sheet1.write(4, 8, str(livechat_customer.email) +
                         "(original - " + str(livechat_customer.original_email) + ")")
        else:
            sheet1.write(4, 8, str(livechat_customer.email))
        sheet1.write(5, 7, "Phone")
        if is_original_information_in_reports_enabled and livechat_customer.original_phone != "" and livechat_customer.phone != livechat_customer.original_phone:
            sheet1.write(5, 8, str(livechat_customer.phone) +
                         "(original - " + str(livechat_customer.original_phone) + ")")
        else:
            sheet1.write(5, 8, str(livechat_customer.phone))

        sheet1.write(6, 7, "Other")
        if livechat_customer.channel.name in ['Web', 'Android', 'iOS', 'WhatsApp', 'GoogleRCS']:
            sheet1.write(6, 8, "-")
        else:
            sheet1.write(6, 8, str(livechat_customer.client_id))

        sheet1.write(7, 7, "Bot Name")
        sheet1.write(7, 8, str(livechat_customer.bot.name))
        sheet1.write(8, 7, "Assigned agent")
        sheet1.write(8, 8, str(livechat_customer.agent_id))
        sheet1.write(9, 7, "Chat initiated on")
        sheet1.write(9, 8, get_livechat_date_format(
            livechat_customer.joined_date))
        sheet1.write(10, 7, "Chat initiated at")
        sheet1.write(10, 8, get_time(livechat_customer.joined_date))
        sheet1.write(11, 7, "Chat initiated from(URL)")
        sheet1.write(11, 8, livechat_customer.active_url)
        sheet1.write(12, 7, "Wait time")
        sheet1.write(12, 8, livechat_customer.get_wait_time())
        sheet1.write(13, 7, "Self Assigned Chat")
        self_assigned_chat = "Yes" if livechat_customer.is_self_assigned_chat == True else "No"
        sheet1.write(13, 8, self_assigned_chat)

        filename = "Chat-Transcript-" + \
            str(livechat_customer.session_id) + ".xls"
        chat_transcript.save(settings.MEDIA_ROOT + filename)
        path_to_file = settings.MEDIA_ROOT + str(filename)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[NLP]: Error create_excel_of_chat %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return filename, path_to_file


"""
function: get_nps_avg
input params:
    user_obj_list: List of agents
expected output:
    nps_avg: The average NPS score given by customers upto that 
             particular point in a day.
"""


def get_nps_avg(user_obj_list, LiveChatCustomer):
    try:
        nps_avg = 0
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date=datetime.now().date(), agent_id__in=user_obj_list)
        promoter_nps_score = livechat_cust_objs.exclude(rate_value=-1).filter(
            rate_value__gte=9).count()
        demoter_nps_score = livechat_cust_objs.exclude(rate_value=-1).filter(
            rate_value__lte=6).count()
        total_feedback = livechat_cust_objs.exclude(rate_value=-1).count()

        if total_feedback != 0:
            nps_avg = ((promoter_nps_score - demoter_nps_score) * 100) / total_feedback

        nps_avg = float("{:.1f}".format(nps_avg))
        return nps_avg
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_nps_avg: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0


def get_nps_avg_filter(user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatCustomer):
    try:
        nps_avg = 0
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date__range=[datetime_start, datetime_end], agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs)

        promoter_nps_score = livechat_cust_objs.exclude(rate_value=-1).filter(
            rate_value__gte=9).count()
        demoter_nps_score = livechat_cust_objs.exclude(rate_value=-1).filter(
            rate_value__lte=6).count()
        total_feedback = livechat_cust_objs.exclude(rate_value=-1).count()

        if total_feedback != 0:
            nps_avg = ((promoter_nps_score - demoter_nps_score) * 100) / total_feedback

        nps_avg = float("{:.1f}".format(nps_avg))
        return nps_avg
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_nps_avg: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0


"""
function: get_agents_availibility_analytics_filter
input params:
    user_obj_list: List of agents
expected output:
    loggen_in_agents: Total number of agents logged in
    ready_agents: Total number of agents ready to chat
    not_ready_agents: Total number of agents not ready to chat

"""


def get_agents_availibility_analytics_filter(user_obj_list):
    try:
        loggen_in_agents = 0
        ready_agents = 0
        not_ready_agents = 0

        for user in user_obj_list:
            if is_agent_live(user) and not user.is_session_exp:
                loggen_in_agents += 1
                if user.status == "3":
                    if user.is_online:
                        ready_agents += 1
                    else:
                        not_ready_agents += 1
        logger.info("Inside get_agents_availibility_analytics: %s at %s", str(
            ready_agents), str(not_ready_agents), extra={'AppName': 'LiveChat'})
        return loggen_in_agents, ready_agents, not_ready_agents
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_agents_availibility_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0, 0, 0


def get_livechat_chat_report_history_list(start_date, end_date, channel_objs, category_objs, user_obj_list, is_filter_applied, Bot, LiveChatConfig, LiveChatCustomer):
    try:
        chat_report_history_list = []
        if is_filter_applied:
            date_format = DATE_YYYY_MM_DD
            start_date = datetime.strptime(
                start_date, date_format)
            end_date = datetime.strptime(end_date, date_format)
        else:
            start_date = (datetime.now() - timedelta(days=7))
            end_date = (datetime.now() - timedelta(days=1))

        no_of_days = (end_date - start_date).days + 1
        # +1 because end date is inclusive in range
        bot_objs = Bot.objects.none()
        for user_obj in user_obj_list:
            bot_objs |= user_obj.bots.all()
        bot_objs = bot_objs.distinct()
        total_entered_chat = 0
        total_closed_chat = 0
        denied_chats = 0
        abandon_chats = 0
        customer_declined_chats = 0
        for day in range(no_of_days):
            curr_date = (start_date + timedelta(days=day)).date()

            livechat_cust_objs = LiveChatCustomer.objects.filter(
                request_raised_date=curr_date, agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs)
            curr_total_closed_chat = livechat_cust_objs.filter(
                is_session_exp=True).count()

            curr_denied_chats = LiveChatCustomer.objects.filter(bot__in=bot_objs,
                                                                request_raised_date=curr_date, is_denied=True, is_system_denied=False, channel__in=channel_objs, category__in=category_objs).count()
            curr_abandon_chats = LiveChatCustomer.objects.filter(
                request_raised_date=curr_date, is_system_denied=True, bot__in=bot_objs, channel__in=channel_objs, category__in=category_objs).count()
            curr_customer_declined_chats = LiveChatCustomer.objects.filter(
                request_raised_date=curr_date, agent_id=None, abruptly_closed=True, bot__in=bot_objs, channel__in=channel_objs, category__in=category_objs).count()

            curr_total_entered_chat = livechat_cust_objs.count() + curr_denied_chats + \
                curr_abandon_chats + curr_customer_declined_chats

            chat_report_history_list.append({
                "label": str(curr_date.strftime(DATE_DD_MMM_YY)),
                "total_entered_chat": curr_total_entered_chat,
                "total_closed_chat": curr_total_closed_chat,
                "denied_chats": curr_denied_chats,
                "abandon_chats": curr_abandon_chats,
                "customer_declined_chats": curr_customer_declined_chats,
            })
            total_entered_chat += curr_total_entered_chat
            total_closed_chat += curr_total_closed_chat
            denied_chats += curr_denied_chats
            abandon_chats += curr_abandon_chats
            customer_declined_chats += curr_customer_declined_chats

        return chat_report_history_list, total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_agents_availibility_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return [], 0, 0, 0, 0, 0


def get_avg_nps_list(start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer):
    try:
        avg_nps_list = []
        total_avg_nps = 0
        if is_filter_applied:
            date_format = DATE_YYYY_MM_DD
            start_date = datetime.strptime(
                start_date, date_format)
            end_date = datetime.strptime(end_date, date_format)
            total_avg_nps = get_nps_avg_filter(
                user_obj_list, start_date.date(), end_date.date(), channel_objs, category_objs, LiveChatCustomer)
        else:
            start_date = (datetime.now() - timedelta(days=7))
            end_date = (datetime.now() - timedelta(days=1))

        no_of_days = (end_date - start_date).days + 1

        for day in range(no_of_days):
            curr_date = (start_date + timedelta(days=day)).date()

            avg_nps = 0
            livechat_cust_objs = LiveChatCustomer.objects.filter(
                request_raised_date=curr_date, agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs)
            promoter_nps_score = livechat_cust_objs.exclude(rate_value=-1).filter(
                rate_value__gte=9).count()
            demoter_nps_score = livechat_cust_objs.exclude(rate_value=-1).filter(
                rate_value__lte=6).count()
            total_feedback = livechat_cust_objs.exclude(rate_value=-1).count()

            if total_feedback != 0:
                avg_nps = ((promoter_nps_score - demoter_nps_score) * 100) / total_feedback
            avg_nps = float("{:.1f}".format(avg_nps))

            avg_nps_list.append({
                "label": str(curr_date.strftime(DATE_DD_MMM_YY)),
                "avg_nps": avg_nps,
            })

        return avg_nps_list, total_avg_nps
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_avg_nps_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return [], 0


def get_livechat_avg_handle_time_list(start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer):
    try:
        avg_handle_time_list = []
        total_avg_handle_time = 0
        if is_filter_applied:
            date_format = DATE_YYYY_MM_DD
            start_date = datetime.strptime(
                start_date, date_format)
            end_date = datetime.strptime(end_date, date_format)
            total_avg_handle_time = get_livechat_avh_filter(
                user_obj_list, start_date.date(), end_date.date(), channel_objs, category_objs, LiveChatCustomer)
        else:
            start_date = (datetime.now() - timedelta(days=7))
            end_date = (datetime.now() - timedelta(days=1))

        no_of_days = (end_date - start_date).days + 1

        for day in range(no_of_days):
            curr_date = (start_date + timedelta(days=day)).date()
            total_handle = 0
            average_handle_time = 0
            livechat_cust_objs = LiveChatCustomer.objects.filter(
                request_raised_date=curr_date, agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs)
            total_handle = livechat_cust_objs.aggregate(Sum('chat_duration'))[
                'chat_duration__sum']
            average_handle_time = get_average(
                total_handle, livechat_cust_objs.count())
            average_handle_time = average_handle_time // 60

            avg_handle_time_list.append({
                'label': str(curr_date.strftime(DATE_DD_MMM_YY)),
                'avg_handle_time': average_handle_time,
            })

        return avg_handle_time_list, total_avg_handle_time
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_livechat_avg_handle_time_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return [], 0


def get_livechat_avg_queue_time_list(start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer):
    try:
        avg_queue_time_list = []
        total_avg_queue_time = 0
        if is_filter_applied:
            date_format = DATE_YYYY_MM_DD
            start_date = datetime.strptime(
                start_date, date_format)
            end_date = datetime.strptime(end_date, date_format)
            total_avg_queue_time = get_livechat_avq_filter(
                user_obj_list, start_date.date(), end_date.date(), channel_objs, category_objs, LiveChatCustomer)
        else:
            start_date = (datetime.now() - timedelta(days=7))
            end_date = (datetime.now() - timedelta(days=1))

        no_of_days = (end_date - start_date).days + 1

        for day in range(no_of_days):
            curr_date = (start_date + timedelta(days=day)).date()
            total_queue = 0
            average_queue_time = 0
            livechat_cust_objs = LiveChatCustomer.objects.filter(
                request_raised_date=curr_date, agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs)
            total_queue = livechat_cust_objs.aggregate(Sum('queue_time'))[
                'queue_time__sum']
            average_queue_time = get_average(
                total_queue, livechat_cust_objs.count())

            avg_queue_time_list.append({
                'label': str(curr_date.strftime(DATE_DD_MMM_YY)),
                'average_queue_time': average_queue_time,
            })
        return avg_queue_time_list, total_avg_queue_time
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_livechat_avg_queue_time_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return [], 0


def get_livechat_avg_interaction_per_chat_list(start_date, end_date, channel_objs, user_obj_list, is_filter_applied, category_objs, LiveChatCustomer, LiveChatMISDashboard):
    try:

        avg_interaction_per_chat_list = []
        total_avg_inter_time = 0
        if is_filter_applied:
            date_format = DATE_YYYY_MM_DD
            start_date = datetime.strptime(
                start_date, date_format)
            end_date = datetime.strptime(end_date, date_format)
            total_avg_inter_time = get_livechat_avg_interaction_per_chat_filter(
                user_obj_list, start_date.date(), end_date.date(), channel_objs, category_objs, LiveChatCustomer, LiveChatMISDashboard)
        else:
            start_date = (datetime.now() - timedelta(days=7))
            end_date = (datetime.now() - timedelta(days=1))

        no_of_days = (end_date - start_date).days + 1

        for day in range(no_of_days):

            curr_date = (start_date + timedelta(days=day)).date()
            livechat_cust_objs = LiveChatCustomer.objects.filter(
                request_raised_date=curr_date, agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs)
            average_interactions = 0
            total_interactions = LiveChatMISDashboard.objects.filter(
                livechat_customer__in=livechat_cust_objs).count()
            average_interactions = get_average(
                total_interactions, livechat_cust_objs.count())

            avg_interaction_per_chat_list.append({
                "label": str(curr_date.strftime(DATE_DD_MMM_YY)),
                "average_interactions": average_interactions,
            })

        return avg_interaction_per_chat_list, total_avg_inter_time
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_livechat_avg_interaction_per_chat_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return [], 0


def get_percentage_change_data(yes_data, pres_data):
    try:
        if yes_data == 0:
            return "No Data Available"
        per_change = (pres_data - yes_data) / yes_data

        return round(per_change * 100)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_percentage_change_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0


def get_chat_data_combined_percentage_change(yes_total_entered_chat, yes_total_closed_chat, yes_denied_chats, yes_abandon_chats, yes_customer_declined_chats, total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats):
    try:
        total_entered_chat_percent_change = get_percentage_change_data(
            yes_total_entered_chat, total_entered_chat)
        total_closed_chat_percent_change = get_percentage_change_data(
            yes_total_closed_chat, total_closed_chat)
        denied_chats_percent_change = get_percentage_change_data(
            yes_denied_chats, denied_chats)
        abandon_chats_percent_change = get_percentage_change_data(
            yes_abandon_chats, abandon_chats)
        customer_declined_chats_percent_change = get_percentage_change_data(
            yes_customer_declined_chats, customer_declined_chats)
        return total_entered_chat_percent_change, total_closed_chat_percent_change, denied_chats_percent_change, abandon_chats_percent_change, customer_declined_chats_percent_change
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_percentage_change_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def get_chat_data_percentage_diff(total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats, user_obj_list, Bot, LiveChatCustomer):
    try:
        yes_total_entered_chat = 0
        yes_total_closed_chat = 0
        yes_denied_chats = 0
        yes_abandon_chats = 0
        bot_objs = Bot.objects.none()
        for user_obj in user_obj_list:
            bot_objs |= user_obj.bots.all()
        bot_objs = bot_objs.distinct()

        curr_date = (datetime.now() - timedelta(days=1)).date()
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date=curr_date, agent_id__in=user_obj_list)
        yes_total_closed_chat = livechat_cust_objs.filter(
            is_session_exp=True).count()

        yes_denied_chats = LiveChatCustomer.objects.filter(bot__in=bot_objs,
                                                           request_raised_date=curr_date, is_denied=True, is_system_denied=False).count()
        yes_abandon_chats = LiveChatCustomer.objects.filter(
            request_raised_date=curr_date, is_system_denied=True, bot__in=bot_objs).count()
        yes_customer_declined_chats = LiveChatCustomer.objects.filter(
            request_raised_date=curr_date, agent_id=None, abruptly_closed=True, bot__in=bot_objs).count()

        yes_total_entered_chat = livechat_cust_objs.count() + yes_denied_chats + \
            yes_abandon_chats + yes_customer_declined_chats

        total_entered_chat_percent_change, total_closed_chat_percent_change, denied_chats_percent_change, abandon_chats_percent_change, customer_declined_chats_percent_change = get_chat_data_combined_percentage_change(
            yes_total_entered_chat, yes_total_closed_chat, yes_denied_chats, yes_abandon_chats, yes_customer_declined_chats,
            total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats
        )

        return total_entered_chat_percent_change, total_closed_chat_percent_change, denied_chats_percent_change, abandon_chats_percent_change, customer_declined_chats_percent_change
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_chat_percentage_diff: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0, 0, 0, 0, 0


def get_customer_report_percentage_change(avg_nps, avg_handle_time, interactions_per_chat, user_obj_list, LiveChatCustomer, LiveChatMISDashboard):

    try:
        yes_avg_nps = 0
        yes_avg_handle_time = 0
        yes_interactions_per_chat = 0

        curr_date = (datetime.now() - timedelta(days=1)).date()

        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date=curr_date, agent_id__in=user_obj_list)

        promoter_nps_score = livechat_cust_objs.exclude(rate_value=-1).filter(
            rate_value__gte=9).count()
        demoter_nps_score = livechat_cust_objs.exclude(rate_value=-1).filter(
            rate_value__lte=6).count()
        total_feedback = livechat_cust_objs.exclude(rate_value=-1).count()
        if total_feedback != 0:
            yes_avg_nps = ((promoter_nps_score - demoter_nps_score) * 100) / total_feedback
        yes_avg_nps = float("{:.1f}".format(yes_avg_nps))

        total_handle = livechat_cust_objs.aggregate(Sum('chat_duration'))[
            'chat_duration__sum']
        yes_avg_handle_time = get_average(
            total_handle, livechat_cust_objs.count())

        total_interactions = LiveChatMISDashboard.objects.filter(
            livechat_customer__in=livechat_cust_objs).count()
        yes_interactions_per_chat = get_average(
            total_interactions, livechat_cust_objs.count())

        avg_nps_percent_change = get_percentage_change_data(
            yes_avg_nps, avg_nps)

        avg_handle_time_percent_change = get_percentage_change_data(
            yes_avg_handle_time, avg_handle_time)

        avg_inter_per_chat_percent_change = get_percentage_change_data(
            yes_interactions_per_chat, interactions_per_chat)

        return avg_nps_percent_change, avg_handle_time_percent_change, avg_inter_per_chat_percent_change

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_customer_report_percentage_change: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0, 0, 0


def get_voice_calls_initiated(user_obj_list, LiveChatVoIPData):

    try:
        today_voip_objs = LiveChatVoIPData.objects.filter(
            request_datetime__date=datetime.now().date(), call_type__in=['pip', 'new_tab'], agent__in=user_obj_list)

        yesterday_voip_objs = LiveChatVoIPData.objects.filter(request_datetime__date=(
            datetime.now() - timedelta(days=1)).date(), call_type__in=['pip', 'new_tab'], agent__in=user_obj_list)

        return today_voip_objs.count(), get_percentage_change_data(yesterday_voip_objs.count(), today_voip_objs.count())

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_voice_calls_initiated: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0, 0


def get_voice_calls_initiated_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatVoIPData):

    try:
        voip_objs = LiveChatVoIPData.objects.filter(request_datetime__date__range=[
                                                    start_date, end_date], call_type__in=['pip', 'new_tab'], agent__in=user_obj_list, customer__channel__in=channel_objs, customer__category__in=category_objs)

        return voip_objs.count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_voice_calls_initiated_filtered: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0"


def get_total_tickets_raised(user_obj_list, LiveChatTicketAudit):

    try:
        today_ticket_objs = LiveChatTicketAudit.objects.filter(
            action_datetime__date=datetime.now().date(), agent__in=user_obj_list)

        yesterday_ticket_objs = LiveChatTicketAudit.objects.filter(action_datetime__date=(
            datetime.now() - timedelta(days=1)).date(), agent__in=user_obj_list)

        return today_ticket_objs.count(), get_percentage_change_data(yesterday_ticket_objs.count(), today_ticket_objs.count())

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_total_tickets_raised: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0, 0


def get_total_tickets_raised_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatTicketAudit):

    try:
        ticket_raised_objs = LiveChatTicketAudit.objects.filter(action_datetime__date__range=[
            start_date, end_date], agent__in=user_obj_list, customer__channel__in=channel_objs, customer__category__in=category_objs)

        return ticket_raised_objs.count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_total_tickets_raised_filtered: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0"


def get_total_followup_leads(user_obj_list, LiveChatFollowupCustomer):
    try:

        followup_leads_count = LiveChatFollowupCustomer.objects.filter(
            agent_id__in=user_obj_list).aggregate(Sum("followup_count"))
        if not followup_leads_count['followup_count__sum']:
            followup_leads_count['followup_count__sum'] = 0
             
        return followup_leads_count['followup_count__sum']

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_total_followup_leads: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0


def get_call_total_duration(voip_objs):
    try:
        total_duration = 0

        for voip_obj in voip_objs:
            total_duration += voip_obj.get_duration()

        return total_duration
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_call_total_duration: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0


def get_average_call_duration(user_obj_list, LiveChatVoIPData):
    try:
        today_voip_objs = LiveChatVoIPData.objects.filter(request_datetime__date=datetime.now(
        ).date(), agent__in=user_obj_list, is_completed=True, is_interrupted=False, call_type__in=['pip', 'new_tab'])

        today_total_duration = get_call_total_duration(today_voip_objs)

        yesterday_voip_objs = LiveChatVoIPData.objects.filter(request_datetime__date=(datetime.now(
        ) - timedelta(days=1)).date(), agent__in=user_obj_list, is_completed=True, is_interrupted=False, call_type__in=['pip', 'new_tab'])

        yesterday_total_duration = get_call_total_duration(yesterday_voip_objs)

        average_duration = "0s"

        if today_voip_objs:
            average_duration = today_total_duration // today_voip_objs.count()
            average_duration = get_analytics_time_format(int(average_duration))

        return average_duration, get_percentage_change_data(yesterday_total_duration, today_total_duration)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_average_call_duration: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0s", 0


def get_average_call_duration_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatVoIPData):
    try:
        voip_objs = LiveChatVoIPData.objects.filter(request_datetime__date__range=[
                                                    start_date, end_date], agent__in=user_obj_list, is_completed=True, is_interrupted=False, customer__channel__in=channel_objs, call_type__in=['pip', 'new_tab'], customer__category__in=category_objs)

        total_duration = get_call_total_duration(voip_objs)

        average_duration = "0s"

        if voip_objs:
            average_duration = total_duration // voip_objs.count()
            average_duration = get_analytics_time_format(int(average_duration))

        return average_duration
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_average_call_duration_filtered: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0s"


def get_average_video_call_duration(user_obj_list, LiveChatVoIPData):
    try:
        today_voip_objs = LiveChatVoIPData.objects.filter(request_datetime__date=datetime.now(
        ).date(), agent__in=user_obj_list, is_completed=True, is_interrupted=False, call_type='video_call')

        today_total_duration = get_call_total_duration(today_voip_objs)

        yesterday_voip_objs = LiveChatVoIPData.objects.filter(request_datetime__date=(datetime.now(
        ) - timedelta(days=1)).date(), agent__in=user_obj_list, is_completed=True, is_interrupted=False, call_type='video_call')

        yesterday_total_duration = get_call_total_duration(yesterday_voip_objs)

        average_duration = "0s"

        if today_voip_objs:
            average_duration = today_total_duration // today_voip_objs.count()
            average_duration = get_analytics_time_format(int(average_duration))

        return average_duration, get_percentage_change_data(yesterday_total_duration, today_total_duration)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_average_video_call_duration: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0s", 0


def get_average_video_call_duration_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatVoIPData):
    try:
        voip_objs = LiveChatVoIPData.objects.filter(request_datetime__date__range=[
                                                    start_date, end_date], agent__in=user_obj_list, is_completed=True, is_interrupted=False, customer__channel__in=channel_objs, call_type='video_call', customer__category__in=category_objs)

        total_duration = get_call_total_duration(voip_objs)

        average_duration = "0s"

        if voip_objs:
            average_duration = total_duration // voip_objs.count()
            average_duration = get_analytics_time_format(int(average_duration))

        return average_duration
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_average_video_call_duration_filtered: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0s"


def get_chat_termination_data_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatCustomer, Channel):
    try:
        if not start_date:
            start_date = datetime.today().date()

        if not end_date:
            end_date = datetime.today().date()

        if not channel_objs.count():
            channel_objs = Channel.objects.all()

        chat_termination_data = dict(LiveChatCustomer.objects.filter(
            last_appearance_date__date__range=[start_date, end_date], is_session_exp=True, agent_id__in=user_obj_list, channel__in=channel_objs, 
            category__in=category_objs).values_list('chat_ended_by').annotate(total=Count('chat_ended_by')).order_by('total'))

        return chat_termination_data

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_chat_termination_data_filtered: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return {}


def get_source_of_incoming_request_data_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatCustomer, Channel):
    try:
        if not start_date:
            start_date = datetime.today().date()

        if not end_date:
            end_date = datetime.today().date()

        if not channel_objs.count():
            channel_objs = Channel.objects.all()

        source_data = dict(LiveChatCustomer.objects.filter(
            last_appearance_date__date__range=[start_date, end_date], is_session_exp=True, agent_id__in=user_obj_list, channel__in=channel_objs, 
            category__in=category_objs).values_list('source_of_incoming_request').annotate(total=Count('source_of_incoming_request')))

        total = 0
        desktop = 0
        mobile = 0
        others = 0

        if source_data.get('1') != None:
            desktop = source_data.get('1')
        if source_data.get('2') != None:
            mobile = source_data.get('2')
        if source_data.get('3') != None:
            others = source_data.get('3')

        total = desktop + mobile + others
        
        source_of_incoming_request_data = {
            "Desktop": round((total and desktop / total or 0) * 100),
            "Mobile": round((total and mobile / total or 0) * 100),
            "Others": round((total and others / total or 0) * 100),
        }
        
        return source_of_incoming_request_data

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_source_of_incoming_request_data_filtered: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return {'Desktop': 0, 'Mobile': 0, 'Others': 0}


def get_analytics_time_format(time):
    try:
        hour = (time) // 3600
        rem = (time) % 3600
        minute = rem // 60
        sec = rem % 60
        output_time = ""
        if hour != 0:
            output_time = str(hour) + "h "
        if minute != 0:
            output_time += str(minute) + "m "
        if sec != 0:
            output_time += str(sec) + "s"

        if output_time == "":
            output_time = '0s'

        return output_time

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_analytics_time_format: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0s"


def get_analytics_channel_objs(channel_name, Channel):
    try:
        if channel_name == "All":
            channel_objs = Channel.objects.all()
        else:
            channel_objs = Channel.objects.filter(name=channel_name)

        return channel_objs

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_analytics_channel_objs: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return Channel.objects.all()


def get_analytics_category_objs(category_id, LiveChatCategory):
    try:
        if category_id == "All" or category_id is None:
            category_objs = LiveChatCategory.objects.all()
        else:
            category_objs = LiveChatCategory.objects.filter(pk__in=category_id)

        return category_objs

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_analytics_category_objs: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return LiveChatCategory.objects.all()


def get_analytics_category_objs_by_title(category_data, user_obj, is_single_select, Bot, LiveChatCategory):
    try:
        if category_data == "All":
            bot_objs = user_obj.bots.all().filter(is_deleted=False)
            category_objs = user_obj.category.all().filter(
                bot__in=bot_objs, is_deleted=False)
        else:
            if not isinstance(category_data, dict):
                category_data = json.loads(category_data)

            category_objs = []
            for bot, category in category_data.items():
                bot_objs = Bot.objects.filter(pk=int(bot), is_deleted=False)

                if is_single_select:
                    category_list = [category.strip()]
                else:
                    category_list = [category_name.strip() for category_name in category]

                category_objs.append(list(LiveChatCategory.objects.filter(title__in=category_list, bot__in=bot_objs)))
                
                if is_single_select:
                    break

            category_objs = [category_obj for sub_category_list in category_objs for category_obj in sub_category_list]

        return category_objs

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_analytics_category_objs_by_title: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return None 


def get_chat_history_report(requested_data, user_obj, username, LiveChatCustomer, LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatDataExportRequest, LiveChatFollowupCustomer):

    try:
        export_path = None
        export_path_exist = None
        today = datetime.now()

        if not os.path.exists(settings.MEDIA_ROOT + 'livechat-chat-history/' + username):
            os.makedirs(settings.MEDIA_ROOT + 'livechat-chat-history/' + username)

        if requested_data["selected_filter_value"] == "1":
            zip_obj = ZipFile(settings.SECURE_MEDIA_ROOT + 'LiveChatApp/' + LIVECHAT_CHAT_HISTORY_PATH +
                              username + "/ChatHistoryLastDay.zip", 'w')
            yesterday = today - timedelta(1)
            try:
                file_path = LIVECHAT_CHAT_HISTORY_PATH + \
                    username + CHAT_HISTORY_PATH +\
                    str(yesterday.date()) + '.xls'
                if path.exists(settings.MEDIA_ROOT + file_path):
                    zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Chat History Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'LiveChat'})

            zip_obj.close()
            export_path = CHAT_ANALYTICS_PATH + \
                username + \
                "/ChatHistoryLastDay.zip"
            export_path_exist = path.exists(export_path[1:])

        elif requested_data["selected_filter_value"] == "2":
            zip_obj = ZipFile(settings.SECURE_MEDIA_ROOT + 'LiveChatApp/' + LIVECHAT_CHAT_HISTORY_PATH +
                              username + "/ChatHistoryLastSevenDays.zip", 'w')
            for index in range(1, 8):
                date = today - timedelta(index)
                try:
                    file_path = LIVECHAT_CHAT_HISTORY_PATH + \
                        username + CHAT_HISTORY_PATH + \
                        str(date.date()) + '.xls'
                    if path.exists(settings.MEDIA_ROOT + file_path):
                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Chat History Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                        'AppName': 'LiveChat'})

            zip_obj.close()
            export_path = CHAT_ANALYTICS_PATH + \
                username + \
                "/ChatHistoryLastSevenDays.zip"
            export_path_exist = path.exists(export_path[1:])

        elif requested_data["selected_filter_value"] == "3":
            zip_obj = ZipFile(settings.SECURE_MEDIA_ROOT + 'LiveChatApp/' + LIVECHAT_CHAT_HISTORY_PATH +
                              username + "/ChatHistoryLastThirtyDays.zip", 'w')
            for index in range(1, 31):
                date = today - timedelta(index)
                try:
                    file_path = LIVECHAT_CHAT_HISTORY_PATH + \
                        username + CHAT_HISTORY_PATH + \
                        str(date.date()) + '.xls'
                    if path.exists(settings.MEDIA_ROOT + file_path):
                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Chat History Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                        'AppName': 'LiveChat'})

            zip_obj.close()
            export_path = CHAT_ANALYTICS_PATH + \
                username + \
                "/ChatHistoryLastThirtyDays.zip"
            export_path_exist = path.exists(export_path[1:])

        elif requested_data["selected_filter_value"] == "4":
            
            if is_kafka_enabled():
                start_date = requested_data["startdate"]
                end_date = requested_data["enddate"]

                date_format = DATE_YYYY_MM_DD

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()
                
                if (end_date - start_date).days > DAYS_LIMIT_FOR_KAFKA:
                    create_export_request(user_obj, "2", requested_data, LiveChatDataExportRequest)
                    export_path = "request_saved_custom_range"
                else:    
                    zip_obj = ZipFile(settings.SECURE_MEDIA_ROOT + 'LiveChatApp/' + LIVECHAT_CHAT_HISTORY_PATH +
                                        username + "/ChatHistoryCustom.zip", 'w')

                    temp_date = start_date
                    list_of_date = []
                    while temp_date <= end_date:
                        try:
                            file_path = LIVECHAT_CHAT_HISTORY_PATH + \
                                username + CHAT_HISTORY_PATH + \
                                str(temp_date) + '.xls'
                            if path.exists(settings.MEDIA_ROOT + file_path):
                                zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                            else:
                                list_of_date.append(temp_date)
                                
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Chat History Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'LiveChat'})
                        temp_date = temp_date + timedelta(1)
                    
                    thread = threading.Thread(target=export_custom_chat_history, args=(
                        user_obj, username, list_of_date, requested_data, LiveChatCustomer, LiveChatFollowupCustomer, LiveChatConfig, zip_obj), daemon=True)
                    thread.start()
                        
                    export_path = "request_saved"
            else:
                create_export_request(user_obj, "2", requested_data, LiveChatDataExportRequest)
                export_path = "request_saved_custom_range"    

        elif requested_data["selected_filter_value"] == "5":
        
            if is_kafka_enabled():
                zip_obj = ZipFile(settings.SECURE_MEDIA_ROOT + 'LiveChatApp/' + LIVECHAT_CHAT_HISTORY_PATH +
                                    username + "/ChatHistoryToday.zip", 'w')
                
                try:
                    file_path = LIVECHAT_CHAT_HISTORY_PATH + \
                        username + CHAT_HISTORY_PATH + \
                        str(datetime.now().date()) + '.xls'
                    if path.exists(settings.MEDIA_ROOT + file_path):
                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Chat History Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                        'AppName': 'LiveChat'})

                zip_obj.close()
                export_path = CHAT_ANALYTICS_PATH + \
                    username + \
                    "/ChatHistoryToday.zip"
                export_path_exist = path.exists(export_path[1:])
            else:
                result = export_today_data(user_obj, "2", json.dumps(
                    requested_data), LiveChatCustomer, LiveChatSessionManagement, LiveChatAgentNotReady, LiveChatFollowupCustomer)
                if result == True:
                    export_path = "request_saved_today"
            
        if requested_data["selected_filter_value"] == "1" or requested_data["selected_filter_value"] == "2" or requested_data["selected_filter_value"] == "3" or (requested_data["selected_filter_value"] == "5" and is_kafka_enabled()):
            file_access_management_obj = LiveChatFileAccessManagement.objects.create(
                file_path=export_path, is_public=False)
            file_access_management_obj.file_access_type = "personal_access"
            file_access_management_obj.users.add(user_obj)
            file_access_management_obj.save()

            export_path = '/livechat/download-file/' + \
                str(file_access_management_obj.key) + '/LiveChatHistory.zip'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_chat_history_report: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return export_path, export_path_exist


def get_conversations_report(requested_data, user_obj, username, LiveChatCustomer, LiveChatMISDashboard, LiveChatFollowupCustomer):

    try:
        export_path = None
        export_path_exist = None
        today = datetime.now()
        bot_objs = user_obj.bots.all()
        if requested_data["selected_filter_value"] == "1":

            yesterday_date = (today - timedelta(1)).strftime(DATE_DD_MM_YYYY)
            zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_CONVERSATION_PATH +
                              username + "/LiveChatConversationLastOneDay.zip", "w")

            for bot_obj in bot_objs.iterator():
                bot_name = bot_obj.name.strip().replace(" ", "_")

                try:
                    file_path = LIVECHAT_CONVERSATION_PATH + \
                        username + LIVECHAT_CONVERSATION_FILE_NAME + \
                        str(bot_name) + '_' + yesterday_date + '.xls'
                    
                    if path.exists(settings.MEDIA_ROOT + file_path):
                        zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("LiveChat Conversations Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                        'AppName': 'LiveChat'})

            zip_obj.close()

            export_path = FILES_LIVECHAT_CONVERSATION + \
                username + \
                "/LiveChatConversationLastOneDay.zip"
            export_path_exist = path.exists(export_path[1:])

        elif requested_data["selected_filter_value"] == "2":

            zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_CONVERSATION_PATH +
                              username + "/LiveChatConversationLastSevenDays.zip", 'w')
            
            for index in range(1, 8):
                report_date = (today - timedelta(index)).strftime(DATE_DD_MM_YYYY)

                for bot_obj in bot_objs.iterator():
                    bot_name = bot_obj.name.strip().replace(" ", "_")

                    try:
                        file_path = LIVECHAT_CONVERSATION_PATH + \
                            username + LIVECHAT_CONVERSATION_FILE_NAME + \
                            str(bot_name) + '_' + str(report_date) + '.xls'
                        
                        if path.exists(settings.MEDIA_ROOT + file_path):
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("LiveChat Conversations Datadump! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})

            zip_obj.close()

            export_path = FILES_LIVECHAT_CONVERSATION + \
                username + \
                "/LiveChatConversationLastSevenDays.zip"
            export_path_exist = path.exists(export_path[1:])

        elif requested_data["selected_filter_value"] == "3":

            zip_obj = ZipFile(settings.MEDIA_ROOT + LIVECHAT_CONVERSATION_PATH +
                              username + "/LiveChatConversationLastThirtyDays.zip", 'w')
            for index in range(1, 31):
                report_date = (today - timedelta(index)).strftime(DATE_DD_MM_YYYY)

                for bot_obj in bot_objs.iterator():
                    bot_name = bot_obj.name.strip().replace(" ", "_")

                    try:
                        file_path = LIVECHAT_CONVERSATION_PATH + \
                            username + LIVECHAT_CONVERSATION_FILE_NAME + \
                            str(bot_name) + '_' + report_date + '.xls'
                        
                        if path.exists(settings.MEDIA_ROOT + file_path):
                            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("LiveChat Conversations Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'LiveChat'})

            zip_obj.close()

            export_path = FILES_LIVECHAT_CONVERSATION + \
                username + \
                "/LiveChatConversationLastThirtyDays.zip"
            export_path_exist = path.exists(export_path[1:])

        elif requested_data["selected_filter_value"] == "4" or requested_data["selected_filter_value"] == "5":

            try:
                thread = threading.Thread(target=export_livechat_conversations, args=(
                    user_obj, json.dumps(requested_data), LiveChatCustomer, LiveChatMISDashboard, LiveChatFollowupCustomer), daemon=True)
                thread.start()
                export_path = "conversation_request_saved"

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("LiveChat Conversations Thread! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'LiveChat'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_conversations_report: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return export_path, export_path_exist


def export_livechat_conversations(user, filter_param, LiveChatCustomer, LiveChatMISDashboard, LiveChatFollowupCustomer):
    try:
        domain = settings.EASYCHAT_HOST_URL
        DIR_NAME = "livechat-conversations"
        if not os.path.exists(settings.MEDIA_ROOT + DIR_NAME):
            os.makedirs(settings.MEDIA_ROOT + DIR_NAME)

        filter_param = json.loads(filter_param)
        today = datetime.now()
        email_str = filter_param["email"]
        email_list = [email.strip()
                      for email in email_str.split(",") if email != ""]
        username = user.user.username

        if(filter_param["selected_filter_value"] == "4"):
            date_format = "%Y-%m-%d"
            start_date = datetime.strptime(
                filter_param["startdate"], date_format)
            end_date = datetime.strptime(filter_param["enddate"], date_format)
            export_zip_file_path = "files/livechat-conversations/" + username + "/LiveChatConversationCustom " + \
                start_date.strftime(DATE_DD_MM_YYYY) + " - " + \
                end_date.strftime(DATE_DD_MM_YYYY) + ".zip"

        else:
            start_date = today
            end_date = today
            export_zip_file_path = "files/livechat-conversations/" + username + "/LiveChatConversationToday " + \
                start_date.strftime(DATE_DD_MM_YYYY) + " - " + \
                start_date.strftime("%H:%M:%S") + ".zip"

        agent_list = get_agents_under_this_user(user)
        if not os.path.exists(settings.MEDIA_ROOT + LIVECHAT_CONVERSATION_PATH + str(user.user.username)):
            os.makedirs(settings.MEDIA_ROOT + LIVECHAT_CONVERSATION_PATH +
                        str(user.user.username))

        bot_objs = user.bots.all()
        zip_obj = ZipFile(export_zip_file_path, 'w')

        for bot_obj in bot_objs.iterator():
            bot_name = bot_obj.name.strip().replace(" ", "_")

            for i_counter in range((end_date - start_date).days + 1):

                current_date = start_date + timedelta(days=i_counter)
                report_date = current_date.strftime(DATE_DD_MM_YYYY)

                file_path = LIVECHAT_CONVERSATION_PATH + \
                    username + LIVECHAT_CONVERSATION_FILE_NAME + \
                    str(bot_name) + '_' + report_date + '.xls'
                        
                if path.exists(settings.MEDIA_ROOT + file_path):
                    zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
                else:
                    conversations_wb = Workbook()
                    conversations_wb = add_conversations_sheet(
                        conversations_wb, current_date, bot_obj, agent_list, LiveChatCustomer, LiveChatMISDashboard, LiveChatFollowupCustomer)
                    filename = LIVECHAT_CONVERSATION_PATH + str(user.user.username) + LIVECHAT_CONVERSATION_FILE_NAME + str(bot_name) + "_" + str(report_date) + ".xls"
                    conversations_wb.save(settings.MEDIA_ROOT + filename)
                    zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))

                    if current_date == today:
                        cmd = "rm " + settings.MEDIA_ROOT + LIVECHAT_CONVERSATION_PATH + str(user.user.username) + LIVECHAT_CONVERSATION_FILE_NAME + str(bot_name) + "_" + str(today.date().strftime(DATE_DD_MM_YYYY)) + ".xls"
                        os.system(cmd)

        zip_obj.close()

        body = """
            <head>
              <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
              <title>Cogno AI</title>
              <style type="text/css" media="screen">
              </style>
            </head>
            <body>

            <div style="padding:1em;border:0.1em black solid;" class="container">
                <p>
                    Dear {},
                </p>
                <p>
                    We have received a request to provide you with the LiveChat Conversation History from {} to {}. Please click on the link below to download the file.
                </p>
                <a href="{}/{}">click here</a>
                <p>&nbsp;</p>
                """
        developer_console_config = get_developer_console_settings()

        body += developer_console_config.custom_report_template_signature

        body += """</div></body>"""

        start_date = datetime.strftime(start_date, DATE_DD_MM_YYYY)
        end_date = datetime.strftime(end_date, DATE_DD_MM_YYYY)

        for email_id in email_list:
            body = body.format(username, str(start_date), str(
                end_date), domain, export_zip_file_path)
            message_subject = "LiveChat Conversation History for " + \
                str(username)
            send_email_to_customer_via_awsses(email_id, message_subject, body)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside export_livechat_conversations: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})


def add_conversations_sheet(workbook, last_date, bot_obj, agent_list, LiveChatCustomer, LiveChatMISDashboard, LiveChatFollowupCustomer):

    try:
        from LiveChatApp.models import LiveChatConfig
        livechat_followup_cust_objs = LiveChatFollowupCustomer.objects.filter(
            completed_date__date=last_date.date(), agent_id__in=agent_list, is_completed=True).values('livechat_customer')
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            Q(agent_id__in=agent_list, joined_date__date=last_date.date()) | Q(pk__in=livechat_followup_cust_objs)).filter(bot=bot_obj).order_by('joined_date')

        client_ids = []

        for livechat_cust_obj in livechat_cust_objs:
            if livechat_cust_obj.client_id not in client_ids:
                client_ids.append(livechat_cust_obj.client_id)

        sheet = workbook.add_sheet(last_date.strftime(DATE_DD_MM_YYYY))
        style = xlwt.XFStyle()
        alignment_style = xlwt.XFStyle()
        conversation_history_style = xlwt.XFStyle()
        config_obj = LiveChatConfig.objects.get(bot=bot_obj)
        # font
        font = xlwt.Font()
        font.bold = True
        style.font = font
        conversation_history_style.font = font

        alignment = xlwt.Alignment()
        alignment.vert = xlwt.Alignment.VERT_TOP
        alignment_style.alignment = alignment
        conversation_history_style.alignment = alignment

        sheet.write(0, 0, "Sr. No.", style=style)
        sheet.write(0, 1, "Name", style=style)
        sheet.write(0, 2, "Email ID", style=style)
        sheet.write(0, 3, "Phone", style=style)
        sheet.write(0, 4, "Client ID", style=style)
        sheet.write(0, 5, "Bot Name", style=style)
        sheet.write(0, 6, "Assigned Agent", style=style)
        sheet.write(0, 7, "Chat initiated on", style=style)
        sheet.write(0, 8, "Chat initiated at", style=style)
        sheet.write(0, 9, "Chat re-initiated at", style=style)
        sheet.write(0, 10, "Chat initiated from(URL)", style=style)
        sheet.write(0, 11, "Wait Time", style=style)
        sheet.write(0, 12, "")
        sheet.write(0, 13, "Date", style=style)
        sheet.write(0, 14, "Time", style=style)
        sheet.write(0, 15, "User", style=style)
        sheet.write(0, 16, "Name", style=style)
        sheet.write(0, 17, "Message", style=style)
        sheet.write(0, 18, "Attachment", style=style)
        row = 1
        client_count = 1

        for client_id in client_ids:

            customer_objs = LiveChatCustomer.objects.filter(
                client_id=client_id).filter(Q(joined_date__date=last_date.date()) | Q(pk__in=livechat_followup_cust_objs)).exclude(Q(agent_id=None) & Q(followup_assignment=False)).order_by("joined_date")
            customer_name = ""
            customer_email = ""
            customer_phone = ""
            assigned_agent = ""
            if customer_objs.count() > 1:
                chat_reinitiated = ""
            else:
                chat_reinitiated = "_  "
            chat_initiated_url = ""
            wait_time = ""

            for customer_index in range(0, customer_objs.count()):
                original_name = ""
                original_phone = ""
                original_email = ""
                if config_obj.is_original_information_in_reports_enabled:
                    if customer_objs[customer_index].original_username != "" and customer_objs[customer_index].original_username != customer_objs[customer_index].username:
                        original_name = " (original - " + \
                            customer_objs[customer_index].original_username + ")"
                    if customer_objs[customer_index].original_email != "" and customer_objs[customer_index].original_email != customer_objs[customer_index].email:
                        original_email = " (original - " + \
                            customer_objs[customer_index].original_email + ")"
                    if customer_objs[customer_index].original_phone != "" and customer_objs[customer_index].original_phone != customer_objs[customer_index].phone:
                        original_phone = " (original - " + \
                            customer_objs[customer_index].original_phone + ")"

                customer_name += str(
                    customer_objs[customer_index].username) + original_name + ", "
                customer_email += str(
                    customer_objs[customer_index].email) + original_email + ", "
                customer_phone += str(
                    customer_objs[customer_index].phone) + original_phone + ", "
                assigned_agent += str(
                    customer_objs[customer_index].get_agent_username()) + ", "
                chat_initiated_url += str(
                    customer_objs[customer_index].active_url) + ", "
                wait_time += str(customer_objs[customer_index].queue_time) + ", "
                if customer_index != 0:
                    chat_reinitiated += (customer_objs[customer_index].joined_date + timedelta(
                        hours=5, minutes=30)).strftime("%I:%M %p") + ", "

            livechat_messages = LiveChatMISDashboard.objects.filter(
                livechat_customer__in=customer_objs).order_by('message_time')

            sheet.write_merge(row, row + livechat_messages.count(),
                              0, 0, client_count, style=alignment_style)
            sheet.write_merge(row, row + livechat_messages.count(),
                              1, 1, customer_name[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages.count(),
                              2, 2, customer_email[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages.count(),
                              3, 3, customer_phone[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages.count(),
                              4, 4, client_id, style=alignment_style)
            sheet.write_merge(row, row + livechat_messages.count(),
                              5, 5, bot_obj.name, style=alignment_style)
            sheet.write_merge(row, row + livechat_messages.count(),
                              6, 6, assigned_agent[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages.count(), 7,
                              7, last_date.strftime("%d-%b-%Y"), style=alignment_style)
            sheet.write_merge(row, row + livechat_messages.count(), 8, 8, (customer_objs[0].joined_date + timedelta(
                hours=5, minutes=30)).strftime("%I:%M %p"), style=alignment_style)
            sheet.write_merge(row, row + livechat_messages.count(),
                              9, 9, chat_reinitiated[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages.count(),
                              10, 10, chat_initiated_url[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages.count(),
                              11, 11, wait_time[:-2], style=alignment_style)
            sheet.write_merge(row, row + livechat_messages.count(), 12, 12,
                              "Conversation History >>", style=conversation_history_style)

            for livechat_message in livechat_messages:
                if livechat_message.message_for == "customer" and livechat_message.sender == "System" and (livechat_message.is_voice_call_message or livechat_message.is_cobrowsing_message):
                    continue
                sheet.write(
                    row, 13, (livechat_message.message_time).strftime("%d-%b-%Y"))
                sheet.write(row, 14, (livechat_message.message_time +
                                      timedelta(hours=5, minutes=30)).strftime("%I:%M %p"))
                sheet.write(row, 15, str(livechat_message.sender))
                sheet.write(row, 16, str(livechat_message.sender_name))
                if livechat_message.text_message != "":
                    sheet.write(row, 17, str(livechat_message.text_message))
                if livechat_message.attachment_file_path != "":
                    attachment_file_path = '"' + str(settings.EASYCHAT_HOST_URL) + \
                        str(livechat_message.attachment_file_path) + \
                        "/?source=excel" + '"'
                    sheet.write(
                        row, 18, Formula('HYPERLINK(%s;"Attachment Link")' % attachment_file_path))

                row += 1

            client_count += 1
            row += 1

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_conversations_sheet: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return workbook


def get_cobrowsing_total_duration(cobrowsing_objs):
    try:
        total_duration = 0

        for cobrowsing_obj in cobrowsing_objs:
            total_duration += cobrowsing_obj.get_duration_in_seconds()

        return total_duration
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_cobrowsing_total_duration: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0


def get_average_cobrowsing_duration(user_obj_list, LiveChatCobrowsingData):
    try:
        today_cobrowsing_objs = LiveChatCobrowsingData.objects.filter(request_datetime__date=datetime.now(
        ).date(), agent__in=user_obj_list, is_completed=True, is_interrupted=False)

        today_total_duration = get_cobrowsing_total_duration(
            today_cobrowsing_objs)

        yesterday_cobrowsing_objs = LiveChatCobrowsingData.objects.filter(request_datetime__date=(datetime.now(
        ) - timedelta(days=1)).date(), agent__in=user_obj_list, is_completed=True, is_interrupted=False)

        yesterday_total_duration = get_cobrowsing_total_duration(
            yesterday_cobrowsing_objs)

        average_duration = "0s"

        if today_cobrowsing_objs:
            average_duration = today_total_duration // today_cobrowsing_objs.count()
            average_duration = get_analytics_time_format(int(average_duration))

        return average_duration, get_percentage_change_data(yesterday_total_duration, today_total_duration)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_average_cobrowsing_duration: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0s", 0


def get_average_cobrowsing_duration_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatCobrowsingData):
    try:
        cobrowsing_objs = LiveChatCobrowsingData.objects.filter(request_datetime__date__range=[
            start_date, end_date], agent__in=user_obj_list, is_completed=True, is_interrupted=False, customer__channel__in=channel_objs, customer__category__in=category_objs)

        total_duration = get_cobrowsing_total_duration(cobrowsing_objs)

        average_duration = "0s"

        if cobrowsing_objs:
            average_duration = total_duration // cobrowsing_objs.count()
            average_duration = get_analytics_time_format(int(average_duration))

        return average_duration
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_average_cobrowsing_duration_filtered: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return "0s"


def get_customers_reported(user_obj_list, LiveChatReportedCustomer):
    try:

        reported_customers = LiveChatReportedCustomer.objects.filter(created_date__date=datetime.today(
        ).date(), livechat_customer__agent_id__in=user_obj_list, is_reported=True, is_completed=False)
        return reported_customers.count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_total_customers_reported: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0


def get_total_customers_reported(user_obj_list, LiveChatReportedCustomer):

    try:

        today_reported_customers = LiveChatReportedCustomer.objects.filter(created_date__date=datetime.today(
        ).date(), livechat_customer__agent_id__in=user_obj_list, is_reported=True).count()
        yesterday_reported_customers = LiveChatReportedCustomer.objects.filter(created_date__date=(datetime.now(
        ) - timedelta(days=1)).date(), livechat_customer__agent_id__in=user_obj_list, is_reported=True).count()

        return today_reported_customers, get_percentage_change_data(yesterday_reported_customers, today_reported_customers)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_total_customers_reported: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0, 0


def get_total_customers_reported_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, LiveChatReportedCustomer):
    try:

        filtered_reported_customers = LiveChatReportedCustomer.objects.filter(created_date__date__range=[
                                                                              start_date, end_date], livechat_customer__agent_id__in=user_obj_list, is_reported=True, livechat_customer__channel__in=channel_objs, livechat_customer__category__in=category_objs)
        return filtered_reported_customers.count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_total_customers_reported_filtered: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0


def get_followup_leads_via_email(user_obj_list, Channel, LiveChatFollowupCustomer):

    try:
        email_channel_obj = Channel.objects.filter(name="Email").first()

        today_followup_leads_via_email = LiveChatFollowupCustomer.objects.filter(
            completed_date__date=datetime.now().date(), agent_id__in=user_obj_list, livechat_customer__channel=email_channel_obj, is_completed=True)

        yesterday_followup_leads_via_email = LiveChatFollowupCustomer.objects.filter(completed_date__date=(
            datetime.now() - timedelta(days=1)).date(), agent_id__in=user_obj_list, livechat_customer__channel=email_channel_obj, is_completed=True)

        return today_followup_leads_via_email.count(), get_percentage_change_data(yesterday_followup_leads_via_email.count(), today_followup_leads_via_email.count())

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_followup_leads_via_email: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0, 0


def get_followup_leads_via_email_filtered(user_obj_list, start_date, end_date, channel_objs, category_objs, Channel, LiveChatFollowupCustomer):

    try:
        channel_names = list(channel_objs.values_list('name', flat=True))

        email_channel_obj = Channel.objects.filter(name="Email").first()

        followup_leads_via_email = LiveChatFollowupCustomer.objects.filter(completed_date__date__range=[
            start_date, end_date], livechat_customer__channel=email_channel_obj, agent_id__in=user_obj_list, 
            livechat_customer__previous_channel__in=channel_names, livechat_customer__category__in=category_objs, is_completed=True)

        return followup_leads_via_email.count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_followup_leads_via_email_filtered: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0


def get_total_closed_chats(user_obj_list, LiveChatCustomer):
    try:
        total_closed_chats = LiveChatCustomer.objects.filter(
            request_raised_date=datetime.now().date(), agent_id__in=user_obj_list,
            is_session_exp=True).count()

        yes_total_closed_chats = LiveChatCustomer.objects.filter(
            request_raised_date=(datetime.now() - timedelta(days=1)).date(), agent_id__in=user_obj_list,
            is_session_exp=True).count()

        total_closed_chats_percent_change = get_percentage_change_data(
            yes_total_closed_chats, total_closed_chats)

        return total_closed_chats, total_closed_chats_percent_change

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_total_closed_chats: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0, 0


def get_total_closed_chats_filtered(start_date, end_date, channel_objs, user_obj_list, LiveChatCustomer):
    try:

        total_closed_chats = LiveChatCustomer.objects.filter(
            request_raised_date__range=[start_date, end_date], agent_id__in=user_obj_list,
            channel__in=channel_objs, is_session_exp=True).count()

        return total_closed_chats

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_total_closed_chats_filtered: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'}) 

        return 0  


def get_followup_leads(user_obj_list, LiveChatFollowupCustomer):
    try:
        today_followup_leads_count = 0
        today_followup_leads = LiveChatFollowupCustomer.objects.filter(
            assigned_date__date=datetime.now().date(), agent_id__in=user_obj_list).aggregate(Sum("followup_count"))

        if today_followup_leads['followup_count__sum']:
            today_followup_leads_count = today_followup_leads['followup_count__sum']

        yes_followup_leads_count = 0
        yes_followup_leads = LiveChatFollowupCustomer.objects.filter(
            assigned_date__date=(datetime.now() - timedelta(days=1)).date(), agent_id__in=user_obj_list).aggregate(Sum("followup_count"))

        if yes_followup_leads['followup_count__sum']:
            yes_followup_leads_count = yes_followup_leads['followup_count__sum']
             
        followup_leads_percent_change = get_percentage_change_data(
            yes_followup_leads_count, today_followup_leads_count)

        return today_followup_leads_count, followup_leads_percent_change

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_followup_leads: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0, 0      


def get_followup_leads_filtered(start_date, end_date, channel_objs, user_obj_list, LiveChatFollowupCustomer):
    try:
        followup_leads_count = 0
        followup_leads = LiveChatFollowupCustomer.objects.filter(
            assigned_date__date__range=[start_date, end_date], livechat_customer__channel__in=channel_objs,
            agent_id__in=user_obj_list).aggregate(Sum("followup_count"))

        if followup_leads['followup_count__sum']:
            followup_leads_count = followup_leads['followup_count__sum']

        return followup_leads_count

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_followup_leads_filtered: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return 0


def export_custom_performance_report(user_obj, username, list_of_date, requested_data, export_zip_file_path, LiveChatSessionManagement, zip_obj):
    performance_report_datadump_log = open("log/livechat_agent_performance_report_dump.log", "a")
    today = datetime.now()

    try:
        export_zip_file_path = 'files/' + export_zip_file_path
        domain = settings.EASYCHAT_HOST_URL
        email_str = requested_data["email"]
        email_list = [email.strip()
                        for email in email_str.split(",") if email != ""]
        agent_list = get_agents_under_this_user(user_obj)
        
        for temp_date in list_of_date:
            
            session_management_objs = LiveChatSessionManagement.objects.filter(user__in=agent_list, session_starts_at__date=temp_date).order_by('-session_starts_at')            

            test_wb = Workbook()

            sheet1 = test_wb.add_sheet("Sheet1")

            sheet1.write(0, 0, "Agent Name")
            sheet1.write(0, 1, "Login Date-time")
            sheet1.write(0, 2, "Logout Date-time")
            sheet1.write(0, 3, "Login Duration")
            sheet1.write(0, 4, "Average Handle Time")
            sheet1.write(0, 5, "Average FTR")
            sheet1.write(0, 6, "No Response Count")
            sheet1.write(0, 7, "Idle Time")
            sheet1.write(0, 8, "Not Ready Count")
            sheet1.write(0, 9, "Not Ready Duration")
            sheet1.write(0, 10, "Interaction Count")
            sheet1.write(0, 11, "Total Interaction Duration")
            sheet1.write(0, 12, "Self Assigned Chat Count")
            sheet1.write(0, 13, "Transferred Chat Recieved Count")
            sheet1.write(0, 14, "Transferred Chat Made Count")
            sheet1.write(0, 15, "Total Group Chat Requests")
            sheet1.write(0, 16, "Accepted Group Chats")
            sheet1.write(0, 17, "Declined Group Chats")
            sheet1.write(0, 18, "No Accept/Reject Group Chat")
            sheet1.write(0, 19, "Total Group Chat Duration")
            sheet1.write(0, 20, "Average NPS")
            row = 1

            for message in session_management_objs.iterator():
                sheet1.write(row, 0, message.get_name())
                sheet1.write(row, 1, str((message.session_starts_at.astimezone(pytz.timezone(settings.TIME_ZONE))).strftime("%d/%m/%Y, %I:%M:%p")))
                sheet1.write(row, 2, str((message.session_ends_at.astimezone(pytz.timezone(settings.TIME_ZONE))).strftime("%d/%m/%Y, %I:%M:%p")))
                sheet1.write(row, 3, message.get_session_duration())
                sheet1.write(row, 4, message.get_average_handle_time())
                sheet1.write(row, 5, message.get_average_first_time_response_time())
                sheet1.write(row, 6, message.get_no_response_count())
                sheet1.write(row, 7, message.get_idle_duration())
                sheet1.write(row, 8, message.get_not_ready_count())
                sheet1.write(row, 9, message.get_session_stop_interaction_duration())
                sheet1.write(row, 10, message.get_interaction_count())
                sheet1.write(row, 11, message.get_interaction_duration())
                sheet1.write(row, 12, message.get_self_assigned_chat())                
                sheet1.write(row, 13, message.get_total_transferred_chat_received())
                sheet1.write(row, 14, message.get_total_transferred_chat_made())
                sheet1.write(row, 15, message.get_total_group_chat_request())
                sheet1.write(row, 16, message.get_total_group_chat_accept())
                sheet1.write(row, 17, message.get_total_group_chat_reject())
                sheet1.write(row, 18, message.get_total_group_chat_no_response())
                sheet1.write(row, 19, message.get_total_group_chat_duration())
                sheet1.write(row, 20, message.get_average_nps())
                row += 1

            file_path = "livechat-agent-performance-report/" + username + \
                "/agent_performance_report_" + str(temp_date) + ".xls"
            test_wb.save(settings.MEDIA_ROOT + file_path)

            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
        zip_obj.close()

        start_date_obj = requested_data["startdate"]
        end_date_obj = requested_data["enddate"]

        body = get_html_body_for_mailer_report(str(username), start_date_obj, end_date_obj, domain, export_zip_file_path, "Agent Performance")
        email_subject = f"LiveChat Agent Performance Report For {str(username)}"

        for email_id in email_list:
            send_email_to_customer_via_awsses(email_id, email_subject, body)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_custom_performance_report: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        performance_report_datadump_log.write(str(today) + ": failed: " + str(exc))
        
    performance_report_datadump_log.close()


def export_custom_cobrowsing_history_report(user_obj, username, list_of_date, requested_data, export_zip_file_path, LiveChatCobrowsingData, zip_obj):
    cobrowsing_history_report_datadump_log = open("log/livechat_agent_cobrowsing_history_report_dump.log", "a")
    today = datetime.now()

    try:
        domain = settings.EASYCHAT_HOST_URL
        email_str = requested_data["email"]
        email_list = [email.strip()
                      for email in email_str.split(",") if email != ""]
        agent_list = get_agents_under_this_user(user_obj)

        for curr_date in list_of_date:

            cobrowsing_history_objs = LiveChatCobrowsingData.objects.filter(
                request_datetime__date=curr_date, agent__in=agent_list, is_completed=True, is_interrupted=False).order_by("-request_datetime")

            test_wb = Workbook()

            sheet1 = test_wb.add_sheet("Sheet1")

            sheet1.write(0, 0, "Customer Name")
            sheet1.write(0, 1, "Agent Username")
            sheet1.write(0, 2, "Start Date-Time")
            sheet1.write(0, 3, "End Date-Time")
            sheet1.write(0, 4, "Total Duration")
            sheet1.write(0, 5, "Meeting Status")
            row = 1

            for cobrowsing_data in cobrowsing_history_objs.iterator():
                sheet1.write(row, 0, cobrowsing_data.customer.get_username())
                sheet1.write(row, 1, cobrowsing_data.agent.user.username)

                sheet1.write(row, 2, str((cobrowsing_data.start_datetime.astimezone(
                    pytz.timezone(settings.TIME_ZONE))).strftime(DATE_DD_MMM_YYYY_TIME_HH_MIN_P)))
                sheet1.write(row, 3, str((cobrowsing_data.end_datetime.astimezone(
                    pytz.timezone(settings.TIME_ZONE))).strftime(DATE_DD_MMM_YYYY_TIME_HH_MIN_P)))

                sheet1.write(row, 4, cobrowsing_data.get_duration())
                sheet1.write(row, 5, "Completed")
                row += 1

            file_path = 'livechat-cobrowsing-history/' + username + \
                '/cobrowsing_history_' + str(curr_date) + ".xls"
            test_wb.save(settings.MEDIA_ROOT + file_path)

            zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
        zip_obj.close()

        start_date_obj = requested_data["startdate"]
        end_date_obj = requested_data["enddate"]

        body = get_html_body_for_mailer_report(str(username), start_date_obj, end_date_obj, domain, export_zip_file_path, "Cobrowsing History")
        email_subject = f"LiveChat Cobrowsing History Report For {str(username)}"

        for email_id in email_list:
            send_email_to_customer_via_awsses(email_id, email_subject, body)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_custom_cobrowsing_history_report: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        cobrowsing_history_report_datadump_log.write(str(today) + ": failed: " + str(exc))

    cobrowsing_history_report_datadump_log.close()
