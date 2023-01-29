import os
import sys
import json
import uuid
import logging
import requests
import time
import xlwt
from xlwt import Workbook
from requests.api import get
from urllib.parse import quote
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models import Sum, Q, Count

from EasyChatApp.constants_email_html import *
from EasyChatApp.constants_mailer_analytics import *
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses
from EasyChatApp.models import Channel, UserSessionHealth, Language, MISDashboard

from EasyChatApp.utils import get_secure_file_path
from EasyChatApp.utils_analytics import get_bot_accuracy, return_mis_objects_based_on_category_channel_language, return_mis_objects_excluding_blocked_sessions
import csv
from zipfile import ZipFile
from cronjob_scripts.message_history_dump import add_data, add_default_values

logger = logging.getLogger(__name__)

host_url = settings.EASYCHAT_HOST_URL


def get_start_date_based_count_variation(count_var):
    try:
        if count_var == 'Daily':
            return (datetime.now() - timedelta(days=1)).date()

        if count_var == 'WTD':
            return (datetime.today() - timedelta(days=datetime.today().isoweekday() % 7)).date()

        if count_var == 'MTD':
            if datetime.today().date().day == 1:
                previous_month_date = datetime.today().date() - timedelta(days=1)
                return previous_month_date.replace(day=1)
            else:
                return datetime.today().date().replace(day=1)
                
        if count_var == 'YTD':
            return (datetime(datetime.today().year, 1, 1)).date()

        if count_var == 'LMSD':
            return (datetime.now() - timedelta(days=30)).date()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_start_date_based_count_variation: %s at line %s", e, str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_message_analytics_count_variation(parameters, count_variations, bot, MISDashboard):
    count_variations_dict = {}
    try:

        for count_var in count_variations:
            start_date = get_start_date_based_count_variation(count_var)
            end_date = datetime.now().date()

            mis_objs = MISDashboard.objects.filter(
                creation_date__gte=start_date, creation_date__lt=end_date, bot=bot)
            
            mis_objs = return_mis_objects_excluding_blocked_sessions(mis_objs, UserSessionHealth)

            for param in parameters:
                if param not in count_variations_dict:
                    count_variations_dict[param] = {}

                if MESSAGE_ANALYTICS_PARAMETERS[param] == 1:
                    count_variations_dict[param][count_var] = mis_objs.count()
                    continue

                if MESSAGE_ANALYTICS_PARAMETERS[param] == 2:
                    count_variations_dict[param][count_var] = mis_objs.count(
                    ) - get_unidentified_messages(mis_objs)
                    continue

                if MESSAGE_ANALYTICS_PARAMETERS[param] == 3:
                    count_variations_dict[param][count_var] = get_unidentified_messages(
                        mis_objs)
                    continue

                if MESSAGE_ANALYTICS_PARAMETERS[param] == 4:
                    count_variations_dict[param][count_var] = get_positive_messages(
                        mis_objs)
                    continue

                if MESSAGE_ANALYTICS_PARAMETERS[param] == 5:
                    count_variations_dict[param][count_var] = get_negative_messages(
                        mis_objs)
                    continue

                if MESSAGE_ANALYTICS_PARAMETERS[param] == 6:
                    count_variations_dict[param][count_var] = get_mailer_bot_accuracy(
                        mis_objs)
                    continue
                
                if MESSAGE_ANALYTICS_PARAMETERS[param] == 7:
                    count_variations_dict[param][count_var] = get_intuitive_messages(
                        mis_objs)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_message_analytics_count_variation: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return count_variations_dict


def get_message_analytics_based_channels(parameters, channels, start_date, end_date, bot, MISDashboard):
    channel_dict = {}
    try:
        mis_objs = MISDashboard.objects.filter(
            creation_date__gte=start_date, creation_date__lt=end_date, bot=bot)
        
        mis_objs = return_mis_objects_excluding_blocked_sessions(mis_objs, UserSessionHealth)
        
        for channel in channels:
            filtered_mis_objs = mis_objs.filter(channel_name=channel)

            for param in parameters:
                if param not in channel_dict:
                    channel_dict[param] = {}

                if MESSAGE_ANALYTICS_PARAMETERS[param] == 1:
                    channel_dict[param][channel] = filtered_mis_objs.count()
                    continue

                if MESSAGE_ANALYTICS_PARAMETERS[param] == 2:
                    channel_dict[param][channel] = filtered_mis_objs.count(
                    ) - get_unidentified_messages(filtered_mis_objs)
                    continue

                if MESSAGE_ANALYTICS_PARAMETERS[param] == 3:
                    channel_dict[param][channel] = get_unidentified_messages(
                        filtered_mis_objs)
                    continue

                if MESSAGE_ANALYTICS_PARAMETERS[param] == 4:
                    channel_dict[param][channel] = get_positive_messages(
                        filtered_mis_objs)
                    continue

                if MESSAGE_ANALYTICS_PARAMETERS[param] == 5:
                    channel_dict[param][channel] = get_negative_messages(
                        filtered_mis_objs)
                    continue

                if MESSAGE_ANALYTICS_PARAMETERS[param] == 6:
                    channel_dict[param][channel] = get_mailer_bot_accuracy(
                        filtered_mis_objs)
                    continue

                if MESSAGE_ANALYTICS_PARAMETERS[param] == 7:
                    channel_dict[param][channel] = get_intuitive_messages(
                        mis_objs)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_message_analytics_based_channels: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return channel_dict


def get_unidentified_messages(mis_objs):
    try:
        return mis_objs.filter(
            intent_name=None, is_unidentified_query=True, is_intiuitive_query=False).exclude(message_received="").count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_unidentified_messages: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_intuitive_messages(mis_objs):
    try:
        return mis_objs.filter(
            intent_name=None, is_intiuitive_query=True).count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_intuitive_messages: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_positive_messages(mis_objs):
    try:
        return mis_objs.filter(
            is_helpful_field="1").count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_positive_messages: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_negative_messages(mis_objs):
    try:
        return mis_objs.filter(
            is_helpful_field="-1").count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_negative_messages: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_mailer_bot_accuracy(mis_objs):
    try:
        from EasyChatApp.models import BotInfo
        bot_accuracy = 0
        total_queries = mis_objs.count()

        if total_queries > 0:
            exclude_intuitive_query_from_bot_accuracy = BotInfo.objects.filter(
                bot=mis_objs[0].bot).values_list("exclude_intuitive_query_from_bot_accuracy", flat=True)[0]
            total_unanswered_queries = get_unidentified_messages(mis_objs)
            total_intuitive_queries = mis_objs.filter(
                is_intiuitive_query=True).count()

            bot_accuracy = round(
                (100 * (total_queries - total_unanswered_queries)) / total_queries, 2) if exclude_intuitive_query_from_bot_accuracy else round(
                (100 * (total_queries - total_unanswered_queries + total_intuitive_queries)) / total_queries, 2)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_mailer_bot_analytics: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return bot_accuracy


def get_session_analytics_count_variation(parameters, count_variations, bot, TimeSpentByUser, MISDashboard, TrafficSources, UserSessionHealth):
    count_variations_dict = {}
    try:
        from EasyChatApp.utils_analytics import get_average_number_of_message_per_session, get_time_in_standard_format, return_mis_objects_based_on_category_channel_language

        for count_var in count_variations:
            start_date = get_start_date_based_count_variation(count_var)
            end_date = datetime.now().date()

            time_spent_objs = TimeSpentByUser.objects.filter(
                start_datetime__date__gte=start_date, end_datetime__date__lt=end_date, bot=bot)

            traffic_objs = TrafficSources.objects.filter(
                visiting_date__gte=start_date, visiting_date__lt=end_date, bot=bot).exclude(web_page__isnull=True)

            for param in parameters:
                mis_objs = return_mis_objects_based_on_category_channel_language(
                    start_date, end_date, [bot], "All", "All", "All", None, MISDashboard, UserSessionHealth)
                mis_objs = mis_objs.filter(is_session_started=True)
                ave_number_of_messages_per_session, no_of_unique_sessions = get_average_number_of_message_per_session(
                    mis_objs)
                
                if param not in count_variations_dict:
                    count_variations_dict[param] = {}

                if SESSION_ANALYTICS_PARAMETERS[param] == 1:
                    count_variations_dict[param][count_var] = no_of_unique_sessions
                    continue

                if SESSION_ANALYTICS_PARAMETERS[param] == 2:
                    count_variations_dict[param][count_var] = get_time_in_standard_format(get_average_session_duration(
                        time_spent_objs))
                    continue

                if SESSION_ANALYTICS_PARAMETERS[param] == 3:
                    count_variations_dict[param][count_var] = ave_number_of_messages_per_session
                    continue

                if SESSION_ANALYTICS_PARAMETERS[param] == 4:
                    count_variations_dict[param][count_var] = get_time_in_standard_format(get_total_session_duration(
                        time_spent_objs))

                if SESSION_ANALYTICS_PARAMETERS[param] == 5:
                    count_variations_dict[param][count_var] = get_total_bot_clicks(
                        traffic_objs)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_session_analytics_count_variation: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return count_variations_dict


def get_average_session_duration(time_spent_objs):
    try:
        total_sessions = time_spent_objs.count()

        if total_sessions == 0:
            return 0

        total_seconds = time_spent_objs.aggregate(Sum('total_time_spent'))[
            'total_time_spent__sum']

        if total_seconds == None:
            total_seconds = 0

        return int(total_seconds / float(total_sessions))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_average_session_duration: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_total_session_duration(time_spent_objs):
    try:
        total_seconds = time_spent_objs.aggregate(Sum('total_time_spent'))[
            'total_time_spent__sum']

        if total_seconds == None:
            total_seconds = 0

        return total_seconds

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_total_session_duration: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_total_bot_clicks(traffic_objs):
    try:
        bot_clicked_count = traffic_objs.aggregate(Sum('bot_clicked_count'))[
            'bot_clicked_count__sum']

        if bot_clicked_count == None:
            bot_clicked_count = 0

        return bot_clicked_count

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_total_bot_clicks: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_user_analytics_count_variation(parameters, count_variations, bot, MISDashboard, EasyChatUserAuthenticationStatus):
    count_variations_dict = {}
    try:
        for count_var in count_variations:
            start_date = get_start_date_based_count_variation(count_var)
            end_date = datetime.now().date()

            mis_objs = MISDashboard.objects.filter(
                creation_date__gte=start_date, creation_date__lt=end_date, bot=bot)

            user_auth_objs = EasyChatUserAuthenticationStatus.objects.filter(
                auth_date__gte=start_date, auth_date__lt=end_date, bot=bot)

            for param in parameters:
                if param not in count_variations_dict:
                    count_variations_dict[param] = {}

                if USER_ANALYTICS_PARAMETERS[param] == 1:
                    count_variations_dict[param][count_var] = get_total_users(
                        mis_objs)
                    continue

                if USER_ANALYTICS_PARAMETERS[param] == 2:
                    count_variations_dict[param][count_var] = get_form_filled(
                        mis_objs)
                    continue

                if USER_ANALYTICS_PARAMETERS[param] == 3:
                    count_variations_dict[param][count_var] = user_auth_objs.count() - get_authenticated_user_count(
                        user_auth_objs)
                    continue

                if USER_ANALYTICS_PARAMETERS[param] == 4:
                    count_variations_dict[param][count_var] = get_authenticated_user_count(
                        user_auth_objs)
                    continue

                if USER_ANALYTICS_PARAMETERS[param] == 5:
                    count_variations_dict[param][count_var] = get_customer_initiated_session_count(
                        mis_objs)
                    continue

                if USER_ANALYTICS_PARAMETERS[param] == 6:
                    count_variations_dict[param][count_var] = get_business_initiated_session_count(
                        mis_objs)
                    continue

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_user_analytics_count_variation: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return count_variations_dict


def get_user_analytics_based_channels(parameters, channels, start_date, end_date, bot, MISDashboard, EasyChatUserAuthenticationStatus, Channel):
    channel_dict = {}
    try:
        mis_objs = MISDashboard.objects.filter(
            creation_date__gte=start_date, creation_date__lt=end_date, bot=bot)

        user_auth_objs = EasyChatUserAuthenticationStatus.objects.filter(
            auth_date__gte=start_date, auth_date__lt=end_date, bot=bot)

        for channel in channels:
            filtered_mis_objs = mis_objs.filter(channel_name=channel)
            filtered_auth_objs = user_auth_objs.filter(
                channel=Channel.objects.get(name=channel))

            for param in parameters:
                if param not in channel_dict:
                    channel_dict[param] = {}

                if USER_ANALYTICS_PARAMETERS[param] == 1:
                    channel_dict[param][channel] = get_total_users(
                        filtered_mis_objs)
                    continue

                if USER_ANALYTICS_PARAMETERS[param] == 2:
                    channel_dict[param][channel] = get_form_filled(
                        filtered_mis_objs)
                    continue

                if USER_ANALYTICS_PARAMETERS[param] == 3:
                    channel_dict[param][channel] = filtered_auth_objs.count() - get_authenticated_user_count(
                        filtered_auth_objs)
                    continue

                if USER_ANALYTICS_PARAMETERS[param] == 4:
                    channel_dict[param][channel] = get_authenticated_user_count(
                        filtered_auth_objs)
                    continue

                if USER_ANALYTICS_PARAMETERS[param] == 5:
                    channel_dict[param][channel] = get_customer_initiated_session_count(
                        filtered_mis_objs)
                    continue

                if USER_ANALYTICS_PARAMETERS[param] == 6:
                    channel_dict[param][channel] = get_business_initiated_session_count(
                        filtered_mis_objs)
                    continue

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_user_analytics_based_channels: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return channel_dict


def get_total_users(mis_objs):
    try:
        return mis_objs.values('user_id').distinct().count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_total_users: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_form_filled(mis_objs):
    try:
        return mis_objs.count() - mis_objs.filter(form_data_widget="").count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_total_users: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_authenticated_user_count(user_auth_objs):
    try:
        return user_auth_objs.filter(is_authenticated=True).count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_authenticated_user_count: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_customer_initiated_session_count(mis_objs):
    try:
        unique_session_objects = mis_objs.values('session_id').distinct()
        return unique_session_objects.filter(is_business_initiated_session=False).count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_customer_initiated_session_count: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_business_initiated_session_count(mis_objs):
    try:
        unique_session_objects = mis_objs.values('session_id').distinct()
        return unique_session_objects.filter(is_business_initiated_session=True).count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_business_initiated_session_count: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_livechat_analytics_count_variation(parameters, count_variations, bot, Intent, MISDashboard, LiveChatCustomer):
    count_variations_dict = {}
    try:
        mis_objs = MISDashboard.objects.filter(bot=bot)
        livechat_cust_objs = LiveChatCustomer.objects.filter(bot=bot)

        for count_var in count_variations:
            start_date = get_start_date_based_count_variation(count_var)
            end_date = datetime.now().date()

            filtered_mis_objs = mis_objs.filter(
                creation_date__gte=start_date, creation_date__lt=end_date)

            livechat_cust_objs = livechat_cust_objs.filter(
                request_raised_date__gte=start_date, request_raised_date__lt=end_date)

            for param in parameters:
                if param not in count_variations_dict:
                    count_variations_dict[param] = {}

                if LIVECHAT_ANALYTICS_PARAMETERS[param] == 1:
                    count_variations_dict[param][count_var] = get_total_livechat_intent_called(
                        filtered_mis_objs, bot, Intent)
                    continue

                if LIVECHAT_ANALYTICS_PARAMETERS[param] == 2:
                    count_variations_dict[param][count_var] = get_conversion_percent(
                        livechat_cust_objs, filtered_mis_objs, bot, Intent)
                    continue

                if LIVECHAT_ANALYTICS_PARAMETERS[param] == 3:
                    count_variations_dict[param][count_var] = get_total_agent_connected(
                        livechat_cust_objs)
                    continue

                if LIVECHAT_ANALYTICS_PARAMETERS[param] == 4:
                    try:
                        count_variations_dict[param][count_var] = livechat_cust_objs.count(
                        )
                    except:
                        count_variations_dict[param][count_var] = 0

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_livechat_analytics_count_variation: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return count_variations_dict


def get_livechat_analytics_based_channels(parameters, channels, start_date, end_date, bot, Channel, Intent, MISDashboard, LiveChatCustomer):
    channel_dict = {}
    try:
        mis_objs = MISDashboard.objects.filter(
            creation_date__gte=start_date, creation_date__lt=end_date, bot=bot)
        livechat_cust_objs = LiveChatCustomer.objects.filter(
            bot=bot, request_raised_date__gte=start_date, request_raised_date__lt=end_date)

        for channel in channels:
            channel_obj = Channel.objects.filter(name=channel)

            filtered_mis_objs = mis_objs.filter(channel_name=channel)
            livechat_cust_objs = livechat_cust_objs.filter(channel=channel_obj)

            for param in parameters:
                if param not in channel_dict:
                    channel_dict[param] = {}

                if LIVECHAT_ANALYTICS_PARAMETERS[param] == 1:
                    channel_dict[param][channel] = get_total_livechat_intent_called(
                        filtered_mis_objs, bot, Intent)
                    continue

                if LIVECHAT_ANALYTICS_PARAMETERS[param] == 2:
                    channel_dict[param][channel] = get_conversion_percent(
                        livechat_cust_objs, filtered_mis_objs, bot, Intent)
                    continue

                if LIVECHAT_ANALYTICS_PARAMETERS[param] == 3:
                    channel_dict[param][channel] = get_total_agent_connected(
                        livechat_cust_objs)
                    continue

                if LIVECHAT_ANALYTICS_PARAMETERS[param] == 4:
                    channel_dict[param][channel] = livechat_cust_objs.count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_livechat_analytics_based_channels: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return channel_dict


def get_total_livechat_intent_called(mis_objs, bot, Intent):
    try:
        intent_obj = Intent.objects.filter(
            name="Chat with an expert", bots__in=[bot])

        return mis_objs.filter(intent_recognized__in=intent_obj).count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_total_livechat_intent_called: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_total_agent_connected(livechat_cust_objs):
    try:
        return livechat_cust_objs.exclude(agent_id=None).count()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_total_agent_connected: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return 0


def get_conversion_percent(livechat_cust_objs, mis_objs, bot, Intent):
    try:
        total_intent_raised = get_total_livechat_intent_called(
            mis_objs, bot, Intent)

        if total_intent_raised == 0:
            return 0

        total_agent_connected = get_total_agent_connected(livechat_cust_objs)

        return (total_agent_connected // total_intent_raised) * 100

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_total_livechat_intent_called: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_language_analytics(start_date, end_date, bot_obj, channels, selected_language, language_query_analytics):
    try:
        language_data = dict()
        if "all" in selected_language:
            supported_languages = bot_obj.languages_supported.all()
        else:
            supported_languages = Language.objects.filter(name_in_english__in=selected_language)

        mis_objs = return_mis_objects_based_on_category_channel_language(start_date, end_date, [bot_obj], "All", "All", "All", None, MISDashboard, UserSessionHealth)
        mis_objs = mis_objs.filter(is_session_started=True)
        for supported_language_obj in supported_languages:
            language_data[supported_language_obj.name_in_english] = []
            if language_query_analytics and "total_users" in language_query_analytics:
                language_data[supported_language_obj.name_in_english].append(mis_objs.filter(selected_language=supported_language_obj).values("user_id").distinct().count())
            if language_query_analytics and "total_queries_asked" in language_query_analytics:
                language_data[supported_language_obj.name_in_english].append(mis_objs.filter(selected_language=supported_language_obj).count())
            if language_query_analytics and "total_queries_answered" in language_query_analytics:
                language_data[supported_language_obj.name_in_english].append(mis_objs.filter(selected_language=supported_language_obj).filter(~Q(intent_name=None)).count())
            if language_query_analytics and "bot_accuracy" in language_query_analytics:
                bot_accuracy = get_bot_accuracy(mis_objs.filter(selected_language=supported_language_obj))
                if isinstance(bot_accuracy, str):
                    language_data[supported_language_obj.name_in_english].append("-")
                else:
                    language_data[supported_language_obj.name_in_english].append(round(bot_accuracy))

        if channels:
            channel_objs = Channel.objects.filter(name__in=channels)
            for channel_obj in channel_objs:
                for supported_language_obj in supported_languages:
                    language_data[supported_language_obj.name_in_english].append(mis_objs.filter(channel_name=channel_obj.name, selected_language=supported_language_obj).count())
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_total_livechat_intent_called: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return language_data


def get_flow_analytics(parameter, start_date, end_date, bot):
    flow_analytics_list = []
    try:
        from EasyChatApp.models import Tree, Intent, FlowAnalytics, Channel, FlowTerminationData, DailyFlowAnalytics
        from EasyChatApp.utils_analytics import get_conversion_flow_counts_data

        channels = Channel.objects.filter(is_easychat_channel=True)
        end_date = end_date - timedelta(days=1)
        # selected_language is for in which language data will be present
        selected_language = "en"
        flow_analytics_dict, _ = get_conversion_flow_counts_data(
            start_date, end_date, [bot], channels, Intent, Tree, FlowAnalytics, FlowTerminationData, DailyFlowAnalytics, selected_language)

        if 'all_selected' in parameter:
            for flow in flow_analytics_dict:
                if isinstance(flow, list) and len(flow) > 0:
                    flow = flow[0]
                flow_analytics_list.append(
                    [flow['name'], flow['hit_count'], flow['complete_count'], (flow['flow_percent'] / 100)])

        else:
            added_flows = set()
            if 'select_top_five' in parameter:
                for itr in range(0, min(len(flow_analytics_dict), 5)):
                    flow = flow_analytics_dict[itr]
                    if isinstance(flow, list) and len(flow) > 0:
                        flow = flow[0]
                    flow_analytics_list.append(
                        [flow['name'], flow['hit_count'], flow['complete_count'], flow['flow_percent'] / 100])
                    added_flows.add(flow['name'])

            for flow in flow_analytics_dict:
                if flow['name'] in parameter and flow['name'] not in added_flows:
                    if isinstance(flow, list) and len(flow) > 0:
                        flow = flow[0]
                    flow_analytics_list.append(
                        [flow['name'], flow['hit_count'], flow['complete_count'], flow['flow_percent'] / 100])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_flow_analytics: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return flow_analytics_list


def get_intent_analytics(parameter, start_date, end_date, bot):
    intent_analytics_list = []
    total_intent_count = 0
    try:
        from EasyChatApp.models import MISDashboard

        intent_count = list(MISDashboard.objects.filter(creation_date__gte=start_date, creation_date__lt=end_date, bot=bot).values(
            'intent_name').order_by('intent_name').annotate(count=Count('intent_name')).exclude(intent_recognized__isnull=True))

        total_intent_count = MISDashboard.objects.filter(
            creation_date__gte=start_date, creation_date__lt=end_date, bot=bot).exclude(intent_recognized__isnull=True).count()

        intent_analytics_dict = sorted(
            list(intent_count), key=lambda i: i['count'], reverse=True)

        if 'all_selected' in parameter:
            for intent in intent_analytics_dict:
                if total_intent_count == 0:
                    usage = '0%'
                else:
                    usage = str(
                        round((intent['count'] * 100) / total_intent_count)) + '%'
                intent_analytics_list.append(
                    [intent['intent_name'], intent['count'], usage])

        else:
            added_intents = set()
            if 'select_top_five' in parameter:
                for itr in range(0, min(len(intent_analytics_dict), 5)):
                    intent = intent_analytics_dict[itr]
                    if total_intent_count == 0:
                        usage = '0%'
                    else:
                        usage = str(
                            round((intent['count'] * 100) / total_intent_count)) + '%'
                    intent_analytics_list.append(
                        [intent['intent_name'], intent['count'], usage])
                    added_intents.add(intent['intent_name'])

            for intent in intent_analytics_dict:
                if intent['intent_name'] in parameter and intent['intent_name'] not in added_intents:
                    if total_intent_count == 0:
                        usage = '0%'
                    else:
                        usage = str(
                            round((intent['count'] * 100) / total_intent_count)) + '%'
                    intent_analytics_list.append(
                        [intent['intent_name'], intent['count'], usage])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_intent_analytics: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return intent_analytics_list


def get_traffic_analytics(parameter, start_date, end_date, bot):
    traffic_analytics_list = []
    try:
        from EasyChatApp.models import TrafficSources, TimeSpentByUser

        source_list = list(TrafficSources.objects.filter(bot=bot).values_list('web_page_source', flat=True).exclude(
            web_page_source__isnull=True).exclude(web_page_source="").distinct())

        traffic_analytics_dict = list(TrafficSources.objects.filter(visiting_date__gte=start_date, visiting_date__lt=end_date, bot=bot, web_page_source__in=source_list).values('web_page', 'web_page_source').annotate(
            bot_views=Sum('bot_clicked_count'), page_views=Sum('web_page_visited')).exclude(web_page_source__isnull=True).exclude(web_page_source="").order_by("-bot_views", "-page_views"))
        for bot_hit_data in traffic_analytics_dict:
            average_time_spent = TimeSpentByUser.objects.filter(
                bot=bot, web_page=bot_hit_data['web_page'], web_page_source=bot_hit_data['web_page_source']).aggregate(Sum('total_time_spent'))['total_time_spent__sum']
            if average_time_spent != None:
                bot_hit_data['average_time_spent'] = average_time_spent
            else:
                bot_hit_data['average_time_spent'] = 0

        if 'all_selected' in parameter:
            for traffic in traffic_analytics_dict:
                traffic_analytics_list.append([traffic['web_page'], traffic['web_page_source'],
                                              traffic['page_views'], traffic['bot_views'], time.strftime("%H:%M:%S", time.gmtime(int(traffic['average_time_spent'])))])

        else:
            added_web_page = set()

            if 'select_top_five_based_sources' in parameter:
                traffic_analytics_dict = sorted(
                    list(traffic_analytics_dict), key=lambda i: i['page_views'], reverse=True)

                for itr in range(0, min(len(traffic_analytics_dict), 5)):
                    traffic = traffic_analytics_dict[itr]
                    traffic_analytics_list.append([traffic['web_page'], traffic['web_page_source'],
                                                  traffic['page_views'], traffic['bot_views'], time.strftime("%H:%M:%S", time.gmtime(int(traffic['average_time_spent'])))])
                    added_web_page.add(traffic['web_page'])

            if 'select_top_five_based_bot_views' in parameter:
                traffic_analytics_dict = sorted(
                    list(traffic_analytics_dict), key=lambda i: i['bot_views'], reverse=True)

                for itr in range(0, min(len(traffic_analytics_dict), 5)):
                    traffic = traffic_analytics_dict[itr]

                    if traffic['web_page'] not in added_web_page:
                        traffic_analytics_list.append([traffic['web_page'], traffic['web_page_source'],
                                                      traffic['page_views'], traffic['bot_views'], time.strftime("%H:%M:%S", time.gmtime(int(traffic['average_time_spent'])))])
                        added_web_page.add(traffic['web_page'])

            if 'select_top_five_average_time' in parameter:
                traffic_analytics_dict = sorted(
                    list(traffic_analytics_dict), key=lambda i: i['average_time_spent'], reverse=True)

                for itr in range(0, min(len(traffic_analytics_dict), 5)):
                    traffic = traffic_analytics_dict[itr]

                    if traffic['web_page'] not in added_web_page:
                        traffic_analytics_list.append([traffic['web_page'], traffic['web_page_source'],
                                                      traffic['page_views'], traffic['bot_views'], time.strftime("%H:%M:%S", time.gmtime(int(traffic['average_time_spent'])))])
                        added_web_page.add(traffic['web_page'])

            for traffic in traffic_analytics_dict:
                if traffic['web_page'] in parameter and traffic['web_page'] not in added_web_page:
                    traffic_analytics_list.append([traffic['web_page'], traffic['web_page_source'],
                                                  traffic['page_views'], traffic['bot_views'], time.strftime("%H:%M:%S", time.gmtime(int(traffic['average_time_spent'])))])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_traffic_analytics: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return traffic_analytics_list


def get_graph_html(profile_obj, is_test_mail, date_str="(15/08/21 - 21/08/21)"):
    analytics_html = ''
    try:
        from EasyChatApp.models import Channel, MISDashboard, Category, MessageAnalyticsDaily, UniqueUsers

        graph_params = json.loads(
            profile_obj.graph_parameters.graph_parameters)
        message_analytics = json.loads(
            profile_obj.graph_parameters.message_analytics_graph)

        if 'user_analytics' in graph_params:
            ua_chart_config = get_user_analytics_chart_config(
                profile_obj.bot, is_test_mail, UniqueUsers)

            encoded_config = quote(json.dumps(ua_chart_config))
            ua_chart_url = f'https://quickchart.io/chart?c={encoded_config}'
            user_analytics = get_analytics_html_for_line_chart(
                ua_chart_url, "Daily User Analytics", date_str)

            analytics_html += user_analytics

        if len(message_analytics) > 0:
            ma_chart_config = get_message_analytics_chart_config(
                profile_obj.bot, message_analytics, is_test_mail, MessageAnalyticsDaily)

            encoded_config = quote(json.dumps(ma_chart_config))
            ma_chart_url = f'https://quickchart.io/chart?c={encoded_config}'
            message_analytics = get_analytics_html_for_line_chart(
                ma_chart_url, "Message Analytics", date_str)

            analytics_html += message_analytics

        if 'category_wise_usage' in graph_params:
            cat_chart_config, cat_chips_html = get_category_chart_config(
                profile_obj.bot, is_test_mail, MISDashboard, Category)

            encoded_config = quote(json.dumps(cat_chart_config))
            cat_chart_url = f'https://quickchart.io/chart?c={encoded_config}'
            category_analytics = get_analytics_html_for_pie_chart(
                cat_chart_url, cat_chips_html, "Category Usage", date_str)

            analytics_html += category_analytics

        if 'channel_usage' in graph_params:
            channel_chart_config, channel_chips_html = get_channel_chart_config(
                profile_obj.bot, Channel.objects.filter(is_easychat_channel=True), is_test_mail, MISDashboard)

            encoded_config = quote(json.dumps(channel_chart_config))
            channel_chart_url = f'https://quickchart.io/chart?c={encoded_config}'
            channel_analytics = get_analytics_html_for_pie_chart(
                channel_chart_url, channel_chips_html, "Channel Usage", date_str)

            analytics_html += channel_analytics

        if 'word_cloud' in graph_params:
            word_cloud_data = get_word_cloud_data(
                profile_obj.bot, is_test_mail)
            word_cloud = get_word_cloud_image(word_cloud_data, date_str)

            analytics_html += word_cloud
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_graph_html: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return analytics_html


def get_table_html(profile_obj, is_test_mail, start_date, end_date, date_str, export_file_name_time):
    analytics_html = ''
    try:
        from EasyChatApp.models import MISDashboard, TimeSpentByUser, Intent, Channel, EasyChatUserAuthenticationStatus, TrafficSources
        from LiveChatApp.models import LiveChatCustomer

        table_parameters = profile_obj.table_parameters
        count_variation = json.loads(table_parameters.count_variation)
        channels = json.loads(table_parameters.channels)
        message_analytics = json.loads(table_parameters.message_analytics)
        session_analytics = json.loads(table_parameters.session_analytics)
        user_analytics = json.loads(table_parameters.user_analytics)
        livechat_analytics = json.loads(table_parameters.livechat_analytics)
        flow_analytics = json.loads(table_parameters.flow_completion)
        intent_analytics = json.loads(table_parameters.intent_analytics)
        traffic_analytics = json.loads(table_parameters.traffic_analytics)
        language_analytics = json.loads(table_parameters.language_analytics)
        language_query_analytics = json.loads(table_parameters.language_query_analytics)

        test_wb = Workbook(encoding="UTF-8")

        sheet1 = test_wb.add_sheet("Sheet1")
        style = xlwt.XFStyle()

        # font
        font = xlwt.Font()
        font.bold = True
        style.font = font
        # excel
        sheet1.write(0, 0, "Record Parameters", style=style)
        row = 2

        if len(count_variation) > 0:

            is_data_present = False
            if len(message_analytics) > 0 or len(session_analytics) > 0 or len(user_analytics) > 0:
                is_data_present = True
                analytics_html += EMAIL_TABLE_HEADING.replace(
                    '{}', 'Record Parameters')
                analytics_html += EMAIL_TABLE_PARAMETERS_START
                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                    '{}', 'Range<p class="table-parameters-date-text">' + date_str + '</p>')

                # excel
                sheet1.write(row, 0, "Range (" + date_str + ")", style=style)
                col = 1

                for count in count_variation:
                    analytics_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                        '{}', count)
                    # excel
                    sheet1.write(row, col, count, style=style)
                    col = col + 1

                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD_END

            # excel
            row = row + 1
            col = 0

            if len(message_analytics) > 0:
                analytics_html += EMAIL_TABLE_SUB_HEADING.replace(
                    '{}', 'Message Analytics')
                # excel
                sheet1.write(row, col, 'Message Analytics', style=style)
                row = row + 1
                col = 0

                if is_test_mail:
                    data_dict = MESSAGE_ANALYTICS_DATA
                else:
                    data_dict = get_message_analytics_count_variation(
                        message_analytics, count_variation, profile_obj.bot, MISDashboard)
                message_analytics_html, row = get_analytics_table_html(
                    message_analytics, count_variation, MESSAGE_ANALYTICS_MAP, data_dict, [row, col, sheet1, style], False)

                analytics_html += message_analytics_html

                # excel
                row = row + 1
                col = 0

            if len(session_analytics) > 0:
                analytics_html += EMAIL_TABLE_SUB_HEADING.replace(
                    '{}', 'Session Analytics')

                # excel
                sheet1.write(row, col, 'Session Analytics', style=style)
                row = row + 1
                col = 0

                if is_test_mail:
                    data_dict = SESSION_ANALYTICS_DATA
                else:
                    data_dict = get_session_analytics_count_variation(
                        session_analytics, count_variation, profile_obj.bot, TimeSpentByUser, MISDashboard, TrafficSources, UserSessionHealth)
                
                session_analytics_html, row = get_analytics_table_html(
                    session_analytics, count_variation, SESSION_ANALYTICS_MAP, data_dict, [row, col, sheet1, style], False)

                analytics_html += session_analytics_html

                # excel
                row = row + 1
                col = 0

            if len(user_analytics) > 0:
                analytics_html += EMAIL_TABLE_SUB_HEADING.replace(
                    '{}', 'User Analytics')

                # excel
                sheet1.write(row, col, 'User Analytics', style=style)
                row = row + 1
                col = 0

                if is_test_mail:
                    data_dict = USER_ANALYTICS_DATA
                else:
                    data_dict = get_user_analytics_count_variation(
                        user_analytics, count_variation, profile_obj.bot, MISDashboard, EasyChatUserAuthenticationStatus)
                
                user_analytics_html, row = get_analytics_table_html(
                    user_analytics, count_variation, USER_ANALYTICS_MAP, data_dict, [row, col, sheet1, style], False)

                analytics_html += user_analytics_html

                # excel
                row = row + 1
                col = 0

            if is_data_present:
                analytics_html += EMAIL_TABLE_PARAMETERS_END

        if len(channels) > 0:
            is_data_present = False
            if len(message_analytics) > 0 or len(session_analytics) > 0 or len(user_analytics) > 0:
                is_data_present = True
                if len(count_variation) == 0:
                    analytics_html += EMAIL_TABLE_HEADING.replace(
                        '{}', 'Record Parameters')
                analytics_html += EMAIL_TABLE_PARAMETERS_START
                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                    '{}', 'Channel<p class="table-parameters-date-text">' + date_str + '</p>')

                # excel
                sheet1.write(row, 0, "Channel (" + date_str + ")", style=style)
                col = 1

                for channel in channels:
                    analytics_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                        '{}', channel)
                    # excel
                    sheet1.write(row, col, channel, style=style)
                    col = col + 1

                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD_END

            # excel
            row = row + 1
            col = 0

            if len(message_analytics) > 0:
                analytics_html += EMAIL_TABLE_SUB_HEADING.replace(
                    '{}', 'Message Analytics')

                # excel
                sheet1.write(row, col, 'Message Analytics', style=style)
                row = row + 1
                col = 0

                if is_test_mail:
                    data_dict = MESSAGE_ANALYTICS_CHANNEL_DATA
                else:
                    data_dict = get_message_analytics_based_channels(
                        message_analytics, channels, start_date, end_date, profile_obj.bot, MISDashboard)
                
                message_analytics_html, row = get_analytics_table_html(
                    message_analytics, channels, MESSAGE_ANALYTICS_MAP, data_dict, [row, col, sheet1, style], True)

                analytics_html += message_analytics_html
                # excel
                row = row + 1
                col = 0

            if len(user_analytics) > 0:
                analytics_html += EMAIL_TABLE_SUB_HEADING.replace(
                    '{}', 'User Analytics')
                # excel
                sheet1.write(row, col, 'User Analytics', style=style)
                row = row + 1
                col = 0

                if is_test_mail:
                    data_dict = USER_ANALYTICS_CHANNEL_DATA
                else:
                    data_dict = get_user_analytics_based_channels(
                        user_analytics, channels, start_date, end_date, profile_obj.bot, MISDashboard, EasyChatUserAuthenticationStatus, Channel)
                
                user_analytics_html, row = get_analytics_table_html(
                    user_analytics, channels, USER_ANALYTICS_MAP, data_dict, [row, col, sheet1, style], False)

                analytics_html += user_analytics_html

                # excel
                row = row + 1
                col = 0

            if is_data_present:
                analytics_html += EMAIL_TABLE_PARAMETERS_END

        if len(flow_analytics) > 0:
            if is_test_mail:
                data_dict = FLOW_ANALYTICS_DATA
            else:
                data_dict = get_flow_analytics(
                    flow_analytics, start_date, end_date, profile_obj.bot)

            if len(data_dict) > 0:
                analytics_html += EMAIL_TABLE_PARAMETERS_START
                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                    '{}', 'Flow Analytics<p class="table-parameters-date-text">' + date_str + '</p>')
                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD_END

                # excel
                sheet1.write(row, 0, "Flow Analytics (" +
                             date_str + ")", style=style)
                col = 0
                row = row + 1

                row_head = ['Flow Name', 'Hit',
                            'Completion', 'Completion Rate']

                flow_analytics_html, row = get_analytics_table_html_type_2(
                    row_head, data_dict, [row, col, sheet1, style])
                analytics_html += flow_analytics_html
                analytics_html += EMAIL_TABLE_PARAMETERS_END

                # excel
                row = row + 1
                col = 0

        if len(language_analytics) > 0:
            if is_test_mail:
                data_dict = LANGUAGE_ANALYTICS_DATA

                if len(data_dict) > 0:
                    analytics_html += EMAIL_TABLE_PARAMETERS_START
                    analytics_html += EMAIL_TABLE_PARAMETERS_HEAD_END

                    sheet1.write(row, 0, "Language Based Analytics (" + date_str + ")", style=style)
                    col = 0
                    row = row + 1

                    row_head = [str('Language ' + date_str)] + LANGUAGE_ANALYTICS_ROW_HEAD

                    index_names = LANGUAGE_ANALYTICS_INDEX_NAMES

                    language_analytics_html, row = get_language_analytics_table_html(
                        row_head, data_dict, index_names, [row, col, sheet1, style])
                    analytics_html += language_analytics_html
                    analytics_html += EMAIL_TABLE_PARAMETERS_END

                    # excel
                    row = row + 1
                    col = 0

            else:
                data_dict = get_language_analytics(start_date, end_date, profile_obj.bot, channels, language_analytics, language_query_analytics)
            
                if len(data_dict) > 0:
                    analytics_html += EMAIL_TABLE_PARAMETERS_START
                    analytics_html += EMAIL_TABLE_PARAMETERS_HEAD_END

                    sheet1.write(row, 0, "Language Based Analytics (" + date_str + ")", style=style)
                    col = 0
                    row = row + 1
                    
                    if "all" in language_analytics:
                        row_head = [str('Language ' + date_str)] + [supported_language.name_in_english for supported_language in profile_obj.bot.languages_supported.all()]
                    else:
                        row_head = [str('Language ' + date_str)] + language_analytics

                    formatted_language_query = []
                    for language_query_analytic_obj in language_query_analytics:
                        formatted_language_query.append(LANGUAGE_QUERY_ANALYTICS_DATA[language_query_analytic_obj])
                    index_names = formatted_language_query + channels

                    language_analytics_html, row = get_language_analytics_table_html(
                        row_head, data_dict, index_names, [row, col, sheet1, style])
                    analytics_html += language_analytics_html
                    analytics_html += EMAIL_TABLE_PARAMETERS_END

                    # excel
                    row = row + 1
                    col = 0

        if len(intent_analytics) > 0:
            if is_test_mail:
                data_dict = INTENT_ANALYTICS_DATA
            else:
                data_dict = get_intent_analytics(
                    intent_analytics, start_date, end_date, profile_obj.bot)

            if len(data_dict) > 0:
                analytics_html += EMAIL_TABLE_PARAMETERS_START
                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                    '{}', 'Intent Analytics<p class="table-parameters-date-text">' + date_str + '</p>')
                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD_END

                # excel
                sheet1.write(row, 0, "Intent Analytics (" +
                             date_str + ")", style=style)
                col = 0
                row = row + 1

                row_head = ['Intent Name', 'Frequency', 'Usage %']

                intent_analytics_html, row = get_analytics_table_html_type_2(
                    row_head, data_dict, [row, col, sheet1, style])
                analytics_html += intent_analytics_html
                analytics_html += EMAIL_TABLE_PARAMETERS_END

                # excel
                row = row + 1
                col = 0
        if len(traffic_analytics) > 0:
            if is_test_mail:
                data_dict = TRAFFIC_ANALYTICS_DATA
            else:
                data_dict = get_traffic_analytics(
                    traffic_analytics, start_date, end_date, profile_obj.bot)

            if len(data_dict) > 0:
                analytics_html += EMAIL_TABLE_PARAMETERS_START
                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                    '{}', 'Traffic Analytics<p class="table-parameters-date-text">' + date_str + '</p>')
                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD_END

                sheet1.write(row, 0, "Traffic Analytics (" +
                             date_str + ")", style=style)
                col = 0
                row = row + 1

                row_head = ['Page Link', 'Source Medium',
                            'Page Views', 'Bot Views', 'Avg. Time on Bot']

                traffic_analytics_html, row = get_analytics_table_html_type_2(
                    row_head, data_dict, [row, col, sheet1, style])
                analytics_html += traffic_analytics_html
                analytics_html += EMAIL_TABLE_PARAMETERS_END

                # excel
                row = row + 1
                col = 0

        if len(livechat_analytics) > 0 and profile_obj.bot.is_livechat_enabled:
            if len(count_variation) > 0 or len(channels) > 0:
                analytics_html += EMAIL_TABLE_HEADING.replace('{}', 'LiveChat')
                # excel
                col = 0
                sheet1.write(row, col, 'LiveChat', style=style)
                row = row + 1

            if len(count_variation) > 0:
                analytics_html += EMAIL_TABLE_PARAMETERS_START
                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                    '{}', 'Range<p class="table-parameters-date-text">' + date_str + '</p>')

                # excel
                sheet1.write(row, 0, "Range (" + date_str + ")", style=style)
                col = 1

                for count in count_variation:
                    analytics_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                        '{}', count)
                    # excel
                    sheet1.write(row, col, count, style=style)
                    col = col + 1

                # excel
                row = row + 1
                col = 0
                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD_END
                analytics_html += EMAIL_TABLE_SUB_HEADING.replace(
                    '{}', 'LiveChat Analytics')

                # excel
                sheet1.write(row, col, 'LiveChat Analytics', style=style)
                row = row + 1
                col = 0

                if is_test_mail:
                    data_dict = LIVECHAT_ANALYTICS_DATA
                else:
                    data_dict = get_livechat_analytics_count_variation(
                        livechat_analytics, count_variation, profile_obj.bot, Intent, MISDashboard, LiveChatCustomer)
                
                livechat_analytics_html, row = get_analytics_table_html(
                    livechat_analytics, count_variation, LIVECHAT_ANALYTICS_MAP, data_dict, [row, col, sheet1, style], False)

                analytics_html += livechat_analytics_html
                analytics_html += EMAIL_TABLE_PARAMETERS_END

                # excel
                row = row + 1
                col = 0

            if len(channels) > 0:
                analytics_html += EMAIL_TABLE_PARAMETERS_START
                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                    '{}', 'Channel<p class="table-parameters-date-text">' + date_str + '</p>')

                # excel
                sheet1.write(row, 0, "Channel (" + date_str + ")", style=style)
                col = 1

                for channel in channels:
                    analytics_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                        '{}', channel)
                    # excel
                    sheet1.write(row, col, channel, style=style)
                    col = col + 1

                # excel
                row = row + 1
                col = 0

                analytics_html += EMAIL_TABLE_PARAMETERS_HEAD_END
                analytics_html += EMAIL_TABLE_SUB_HEADING.replace(
                    '{}', 'LiveChat Analytics')

                # excel
                sheet1.write(row, col, 'LiveChat Analytics', style=style)
                row = row + 1
                col = 0
                if is_test_mail:
                    data_dict = LIVECHAT_ANALYTICS_CHANNEL_DATA
                else:
                    data_dict = get_livechat_analytics_based_channels(
                        livechat_analytics, channels, start_date, end_date, profile_obj.bot, Channel, Intent, MISDashboard, LiveChatCustomer)
                
                live_analytics_html, row = get_analytics_table_html(
                    livechat_analytics, channels, LIVECHAT_ANALYTICS_MAP, data_dict, [row, col, sheet1, style], False)

                analytics_html += live_analytics_html
                analytics_html += EMAIL_TABLE_PARAMETERS_END
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_table_html: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    if not os.path.exists(settings.SECURE_MEDIA_ROOT + EMAIL_EXCEL_PATH):
        os.mkdir(settings.SECURE_MEDIA_ROOT + EMAIL_EXCEL_PATH)

    file_name = "EasyChatApp/email-excels" + "/MailSummary" + \
        "_" + export_file_name_time + ".xls"

    test_wb.save(settings.SECURE_MEDIA_ROOT + file_name)

    file_url = get_secure_file_path('/secured_files/' + file_name, '', profile_obj.bot, False, True)

    return analytics_html, file_url


def get_attachment_html(profile_obj, start_date, end_date, channels, is_test_mail, export_file_path):
    analytics_html = ''
    try:
        attachment_params = []
        if profile_obj.is_attachment_enabled:
            attachment_params = json.loads(
                profile_obj.attachment_parameters.attachments)
        if len(attachment_params) > 0:
            analytics_html += EMAIL_DOWNLOAD_REPORTS_START

            if is_test_mail:
                for param in attachment_params:
                    analytics_html += EMAIL_REPORT_BUTTON.replace(
                        '()', settings.EASYCHAT_HOST_URL + DOWNLOAD_REPORTS_DATA[param]).replace('{}', DOWNLOAD_REPORTS_MAP[param])

            else:
                for param in attachment_params:
                    if param == 'bot_queries':
                        file_url = export_bot_user_msg_history(
                            start_date, end_date, channels, profile_obj.bot)
                        analytics_html += EMAIL_REPORT_BUTTON.replace(
                            '()', file_url).replace('{}', DOWNLOAD_REPORTS_MAP[param])
                    elif param == 'unanswered':
                        file_url = export_unanswered_data(
                            start_date, end_date, profile_obj.bot)
                        analytics_html += EMAIL_REPORT_BUTTON.replace(
                            '()', file_url).replace('{}', DOWNLOAD_REPORTS_MAP[param])
                    elif param == 'intuitive':
                        file_url = export_intuitive_data(
                            start_date, end_date, profile_obj.bot)
                        analytics_html += EMAIL_REPORT_BUTTON.replace(
                            '()', file_url).replace('{}', DOWNLOAD_REPORTS_MAP[param])
                    elif param == 'dropoff':
                        file_url = export_user_specific_dropoff_data(
                            start_date, end_date, profile_obj.bot)

                        if file_url != "":
                            analytics_html += EMAIL_REPORT_BUTTON.replace(
                                '()', file_url).replace('{}', DOWNLOAD_REPORTS_MAP[param])
                    elif param == 'language_analytics':
                        file_url = export_language_based_analytics(start_date, end_date, profile_obj.bot)

                        if file_url != "":
                            analytics_html += EMAIL_REPORT_BUTTON.replace(
                                '()', file_url).replace('{}', DOWNLOAD_REPORTS_MAP[param])
                    elif param == 'csat_data':
                        file_url = export_csat_data(start_date, end_date, profile_obj.bot)

                        if file_url != "":
                            analytics_html += EMAIL_REPORT_BUTTON.replace(
                                '()', file_url).replace('{}', DOWNLOAD_REPORTS_MAP[param])

            if export_file_path != "":
                mailer_summary_path = export_file_path
                analytics_html += EMAIL_REPORT_BUTTON.replace(
                    '()', mailer_summary_path).replace('{}', 'Mail Summary')

            analytics_html += EMAIL_DOWNLOAD_REPORTS_END

        elif export_file_path != "":
            analytics_html += EMAIL_DOWNLOAD_REPORTS_START

            mailer_summary_path = export_file_path
            analytics_html += EMAIL_REPORT_BUTTON.replace(
                '()', mailer_summary_path).replace('{}', "Mail Summary")

            analytics_html += EMAIL_DOWNLOAD_REPORTS_END

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_attachment_html: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return analytics_html


"""
send_test_mail_based_on_config : It will send the test email.
"""


def send_test_mail_based_on_config(profile_obj):
    try:
        status_code = 200
        analytics_html = ""

        if profile_obj.is_graph_enabled:
            analytics_html += get_graph_html(profile_obj, True)

        export_file_path = ""
        if profile_obj.is_table_enabled:
            dummy_name = "test_mail_summary_" + datetime.now().strftime("%d-%m-%y_%H:%M:%S")
            table_analytics_html, export_file_path = get_table_html(
                profile_obj, True, '', '', "(15/08/21 - 21/08/21)", dummy_name)
            analytics_html += table_analytics_html

        if profile_obj.is_attachment_enabled or profile_obj.is_table_enabled:
            analytics_html += get_attachment_html(
                profile_obj, '', '', '', True, export_file_path)

        if analytics_html != '':
            email_subject = profile_obj.email_subject
            email_receivers = json.loads(profile_obj.email_address)
            for email in email_receivers:
                try:
                    generate_mail(profile_obj.bot.name, analytics_html,
                                  email, email_subject)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("send_test_mail_based_on_config > genrate mail: %s %s", str(e), str(exc_tb.tb_lineno), extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    status_code = 102
                    pass

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_test_mail_based_on_config: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return status_code


def get_analytics_table_html(parameters1, parameters2, data_map, data_dict, excel, is_bot_accuracy_included=False):
    analytics_html = ""
    try:
        row = excel[0]
        col = excel[1]
        sheet1 = excel[2]
        style = excel[3]
        for param in parameters1:
            col = 0
            if param == 'bot_accuracy' and not is_bot_accuracy_included:
                continue

            analytics_html += EMAIL_TABLE_PARAMERTERS_TR_START 
            analytics_html += EMAIL_TABLE_PARAMERTERS_VALUES.replace(
                '{}', data_map[param])

            # excel
            sheet1.write(row, col, data_map[param], style=style)
            for count in parameters2:
                # excel
                col = col + 1
                if count in data_dict[param]:
                    sheet1.write(row, col, str(
                        data_dict[param][count]), style=style)
                    analytics_html += EMAIL_TABLE_PARAMERTERS_VALUES.replace(
                        '{}', str(data_dict[param][count]))
                else:
                    sheet1.write(row, col, "0", style=style)
                    analytics_html += EMAIL_TABLE_PARAMERTERS_VALUES.replace(
                        '{}', "0")
            # excel
            row = row + 1
            analytics_html += EMAIL_TABLE_PARAMERTERS_TR_END

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_analytics_table_html: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return analytics_html, row


def get_analytics_table_html_type_2(parameter, data_arr, excel):
    analytics_html = ''
    row = excel[0]
    col = excel[1]
    sheet1 = excel[2]
    style = excel[3]
    try:
        analytics_html = EMAIL_TABLE_PARAMERTERS_TR_START
        for param in parameter:
            analytics_html += EMAIL_TABLE_PARAMERTERS_VALUES_BOLD.replace(
                '{}', param)
            # excel
            sheet1.write(row, col, param, style=style)
            col = col + 1

        row = row + 1
        col = 0
        analytics_html += EMAIL_TABLE_PARAMERTERS_TR_END

        for data in data_arr:
            analytics_html += EMAIL_TABLE_PARAMERTERS_TR_START
            for value in data:
                if LOCALHOST in str(value):
                    value = str(value).replace(
                        LOCALHOST, settings.EASYCHAT_HOST_URL)
                analytics_html += EMAIL_TABLE_PARAMERTERS_VALUES.replace(
                    '{}', str(value))
                # excel
                sheet1.write(row, col, str(value), style=style)
                col = col + 1

            col = 0
            row = row + 1
            analytics_html += EMAIL_TABLE_PARAMERTERS_TR_END

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_analytics_table_html_type_2: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return analytics_html, row


def get_language_analytics_table_html(parameter, data_arr, index_names, excel):
    analytics_html = ''
    row = excel[0]
    col = excel[1]
    sheet1 = excel[2]
    style = excel[3]
    try:
        analytics_html = EMAIL_TABLE_PARAMERTERS_TR_START
        for param in parameter:
            analytics_html += EMAIL_TABLE_PARAMERTERS_VALUES_BOLD.replace(
                '{}', param)
            # excel
            sheet1.write(row, col, param, style=style)
            col = col + 1

        row = row + 1
        col = 0
        analytics_html += EMAIL_TABLE_PARAMERTERS_TR_END

        for index_name_id in range(len(index_names)):
            analytics_html += EMAIL_TABLE_PARAMERTERS_TR_START
            analytics_html += EMAIL_TABLE_PARAMERTERS_VALUES.replace('{}', index_names[index_name_id])
            sheet1.write(row, col, index_names[index_name_id], style=style)
            col = col + 1
            for language_data_id in range(1, len(parameter)):
                analytics_html += EMAIL_TABLE_PARAMERTERS_VALUES.replace('{}', str(data_arr[parameter[language_data_id]][index_name_id]))
                sheet1.write(row, col, str(data_arr[parameter[language_data_id]][index_name_id]), style=style)
                col += 1
            col = 0
            row = row + 1
            analytics_html += EMAIL_TABLE_PARAMERTERS_TR_END

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_language_analytics_table_html: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return analytics_html, row


def get_channel_analytics(bot_obj, channels, MISDashboard):
    channel_dict = {}
    try:

        datetime_start = (
            datetime.now() - timedelta(DEFAULT_TIME_INTERVAL_GRAPH)).date()
        datetime_end = (datetime.now() - timedelta(1)).date()

        mis_objects = MISDashboard.objects.filter(
            bot__in=[bot_obj])

        if datetime_start != None and datetime_end != None:
            mis_objects = mis_objects.filter(
                date__date__gte=datetime_start, date__date__lte=datetime_end)

        channel_name_frequency = list(mis_objects.filter(~Q(channel_name=None)).values(
            "channel_name").order_by("channel_name").annotate(frequency=Count("channel_name")).order_by('-frequency'))

        for channel in channels:
            channel_dict[channel.name] = 0

        for channel_detail in channel_name_frequency:
            channel_dict[channel_detail["channel_name"]
                         ] = channel_detail["frequency"]
        return channel_dict
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[NLP]: Error GetChannelAnalyticsAPI %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': "", 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

    return channel_dict


def get_channel_chart_config(bot_obj, channels, is_test_mail, MISDashboard):
    channel_list = []
    message_count_list = []

    color_list = ["#2697FF", "#6BE119", "#2F4684", "#FFCF26",
                  "#FFA113", "#FF4387", "#FFA113", "#FF4387", "#FFA113", "#FF4387"]
    background_color_list = ["rgba(38, 151, 255, 0.08)", "rgba(107, 225, 25, 0.08)", "rgba(47, 70, 132, 0.08);", "rgba(255, 207, 38, 0.08)", "rgba(255, 161, 19, 0.08)",
                             "rgba(255, 67, 135, 0.08)", "rgba(255, 161, 19, 0.08)", "rgba(255, 67, 135, 0.08)", "rgba(255, 161, 19, 0.08)", "rgba(255, 67, 135, 0.08)"]

    if is_test_mail:
        channel_dict = {
            'Web': 102,
            'WhatsApp': 87,
            'GoogleBusinessMessages': 64,
            'Android': 43
        }
    else:
        channel_dict = get_channel_analytics(bot_obj, channels, MISDashboard)

    html = ""
    iterator = 0
    for data in channel_dict:
        channel_list.append(data)
        message_count_list.append(channel_dict[data])
        html += '<div class="chip" style="align-items:center;color:' + color_list[iterator] + ';background-color:' + background_color_list[iterator] + ';border: 1px solid ' + color_list[iterator] + \
            ';"><span class="dot" style="background-color:' + \
                color_list[iterator] + ';"></span> <span class="chip-label" style="margin:auto;"> ' + data + \
            ': <span style="font-weight:bold;">' + \
                str(channel_dict[data]) + '</span></span></div>'
        iterator += 1

    chart_config = {
        'type': 'doughnut',
        'data': {
            'labels': channel_list,
            'datasets': [{
                'label': "Number of total users",
                'fill': True,
                'fontColor': '#fff',
                'backgroundColor': color_list,
                'borderColor': color_list,
                'data': message_count_list,
                'color': '#fff',
                'fontFamily': 'Silka, Helvetica, sans-serif',
                # // spanGaps: false,
            },
            ]
        },
        'options': {
            'title': {
                'display': False,
                'text': 'Channel Usage'
            },
            "plugins": {
                "datalabels": {
                    'display': False,
                    "color": "#fff",
                }
            },
            'legend': {
                'display': False,
                'position': 'right',
                'align': 'start',
            }
        }
    }

    return chart_config, html


def get_user_analytics_chart_config(bot_obj, is_test_mail, UniqueUsers):

    label_list = []
    no_users_list = []
    if is_test_mail:
        label_list = ['15-Aug-21', '16-Aug-21', '17-Aug-21',
                      '18-Aug-21', '19-Aug-21', '20-Aug-21', '21-Aug-21']
        no_users_list = ['3', '7', '9', '4', '5', '2', '6']
    else:
        label_list, no_users_list = get_user_analytics(
            bot_obj, UniqueUsers)

    chart_config = {
        'type': 'line',
                'data': {
                    'labels': label_list,
                    'datasets': [{
                        'label': "Number of total users",
                        'fill': True,
                        'borderColor': "#3445C6",
                        'fontColor': '#fff',

                        'data': no_users_list,
                    },
                    ]
                },
        'options': {
                    'title': {
                        'display': False,
                        'text': 'Daily User Analytics'
                    },
                    "plugins": {
                        "datalabels": {
                            "align": 'end',
                            'display': True,
                            "color": "#2d2d2d",
                        }
                    },
                    'legend': {
                        'display': True,
                        'position': 'bottom',
                        'align': 'center',
                        "fullWidth": False,
                        'labels': {
                            'fontFamily': "'Silka', 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
                            'fontColor': "#3445C6"
                        }
                    },
                    "layout": {
                        "padding": {
                            "left": 0,
                            "right": 0,
                            "top": 20,
                            "bottom": 0
                        }
                    },
                    'scales': {
                        'yAxes': [{
                            'ticks': {
                                'padding': 20,
                                'display': True,
                                'labelString': "No of users",
                                'beginAtZero': True,
                            },
                            "scaleLabel": {
                                "display": True,
                                "labelString": 'No of Users'
                            },
                            "gridLines": {
                                "color": "#f9f9f9"
                            },
                        }],
                        'xAxes': [{
                            'ticks': {
                                'padding': 20,
                                'display': True,
                                'beginAtZero': True,
                            },
                            "gridLines": {
                                "color": "#f9f9f9"
                            },
                        }]
                    },
                }
    }

    return chart_config


def get_user_analytics(bot_obj, UniqueUsers):

    labels = []
    user_count_list = []
    try:
        datetime_start = (
            datetime.now() - timedelta(DEFAULT_TIME_INTERVAL_GRAPH)).date()
        datetime_end = (datetime.now() - timedelta(1)).date()

        user_objs = UniqueUsers.objects.filter(
            bot__in=[bot_obj])

        no_days = (datetime_end - datetime_start).days + 1

        for day in range(no_days):
            temp_datetime = datetime_start + timedelta(day)

            date_filtered_user_objs = user_objs.filter(
                date=temp_datetime)

            count = date_filtered_user_objs.aggregate(
                Sum('count'))['count__sum']

            if count == None:
                count = 0

            labels.append(str(temp_datetime.strftime("%d-%b-%y")))
            user_count_list.append(count)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_user_analytics: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return labels, user_count_list


def get_message_analytics_chart_config(bot_obj, params, is_test_mail, MessageAnalyticsDaily):

    total_messages_list = []
    total_answered_messages_list = []
    total_unanswered_messages_list = []
    total_intuitive_messages_list = []
    label_list = []
    predicted_messages_no_list = []

    if is_test_mail:
        label_list = ['15-Aug-21', '16-Aug-21', '17-Aug-21',
                      '18-Aug-21', '19-Aug-21', '20-Aug-21', '21-Aug-21']
        total_messages_list = ['21', '30', '18', '20', '26', '23', '22']
        total_answered_messages_list = [
            '21', '26', '11', '19', '20', '18', '20']
        total_unanswered_messages_list = ['0', '4', '7', '1', '6', '5', '2']
        total_intuitive_messages_list = ['1', '8', '11', '5', '10', '7', '4']
        predicted_messages_no_list = ['22', '32', '21', '20', '28', '24', '22']
    else:
        message_analytics_list = get_message_analytics_data(
            bot_obj, MessageAnalyticsDaily)

        for data in message_analytics_list:
            label_list.append(data['label'])
            total_messages_list.append(data['total_messages'])
            total_answered_messages_list.append(
                data['total_answered_messages'])
            total_unanswered_messages_list.append(
                data['total_unanswered_messages'])
            total_intuitive_messages_list.append(data['total_intuitive_messages'])
            predicted_messages_no_list.append(data['predicted_messages_no'])

    datasets = []
    if 'total' in params:
        datasets.append({
            'label': "Total",
            'backgroundColor': "#f9f9f9",
            'borderColor': "#4285F4",
            'borderDash': [5, 5],
            'color': "#FF4387",
            'pointRadius': 2,
            'data': total_messages_list,
            "datalabels": {
                        "align": 'end',
                        'display': True,
                        'color': "#2d2d2d",
                        }
        })

    if 'answered' in params:
        datasets.append({
            'label': "Answered",
            'backgroundColor': "#f9f9f9",
            'borderColor': "#EA4335",
            'borderDash': [5, 5],
            'pointRadius': 2,
            'data': total_answered_messages_list,
            "datalabels": {
                        "align": 'start',
                        'display': True,
                        'color': "#2d2d2d",
                        }

        })

    if 'unanswered' in params:
        datasets.append({
            'label': "Unanswered",
            'backgroundColor': "#f9f9f9",
            'borderColor': "#34A853",
            'borderDash': [5, 5],
            'pointRadius': 2,
            'data': total_unanswered_messages_list,
            "datalabels": {
                        "align": 'center',
                        'display': True,
                        'color': "#2d2d2d",
                        }

        })
    
    if 'intuitive' in params:
        datasets.append({
            'label': "Intuitive",
            'backgroundColor': "#f9f9f9",
            'borderColor': "#ffff00",
            'borderDash': [5, 5],
            'pointRadius': 2,
            'data': total_intuitive_messages_list,
            "datalabels": {
                        "align": 'center',
                        'display': True,
                        'color': "#ffff00",
                        }

        })
    
    if 'projected' in params:
        datasets.append({
            'label': "Projected",
            'fill': "+1",
                    'backgroundColor': "#f9f9f9",
                    'borderColor': "#90A6E2",
                    'borderDash': [5, 5],
                    'pointRadius': 2,
                    'data': predicted_messages_no_list,

        })

    chart_config = {
        'type': 'line',
        'data': {
            'labels': label_list,
            'fontColor': '#2E31A5',
            'datasets': datasets,
        },
        'options': {
            'title': {
                'display': False,
                'text': 'Number Of Messages'
            },
            "plugins": {
                "datalabels": {
                    "align": 'end',
                    'display': False,
                    "color": "rgba(53, 70, 198, 0.56)",
                }
            },
            'legend': {
                'display': True,
                'position': 'bottom',
                'align': 'center',
                "fullWidth": False,
                'labels': {
                    'fontFamily': "'Silka', 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
                    'fontColor': "#3445C6"
                },
            },
            "layout": {
                "padding": {
                    "left": 0,
                    "right": 0,
                    "top": 20,
                    "bottom": 0
                }
            },
            'scales': {
                'yAxes': [{
                    'ticks': {
                        'padding': 20,
                        'display': True,
                        # 'labelString': "No of users",
                        'beginAtZero': True,
                        # //stepSize: min_step_size,
                    },
                    "gridLines": {
                        "color": "#f9f9f9"
                    },
                    "scaleLabel": {
                        "display": True,
                        "labelString": 'No of Messages'
                    },
                }],
                'xAxes': [{
                    'ticks': {
                        'padding': 20,
                        'display': True,
                        'beginAtZero': True,
                        # //stepSize: min_step_size,
                    },
                    "gridLines": {
                        "color": "#f9f9f9"
                    },
                }]
            },

        }

    }
    return chart_config


def get_message_analytics_data(bot_obj, MessageAnalyticsDaily):
    message_analytics_list = []
    try:
        datetime_start = (
            datetime.now() - timedelta(DEFAULT_TIME_INTERVAL_GRAPH)).date()
        datetime_end = (datetime.now() - timedelta(1)).date()

        previous_mis_objects = MessageAnalyticsDaily.objects.filter(
            bot__in=[bot_obj])

        no_days = (datetime_end - datetime_start).days + 1

        for day in range(no_days):
            temp_datetime = datetime_start + timedelta(day)

            date_filtered_mis_objects = previous_mis_objects.filter(
                date_message_analytics=temp_datetime)

            total_messages = date_filtered_mis_objects.aggregate(
                Sum('total_messages_count'))['total_messages_count__sum']

            total_answered_messages = date_filtered_mis_objects.aggregate(
                Sum('answered_query_count'))['answered_query_count__sum']

            total_unanswered_messages = date_filtered_mis_objects.aggregate(
                Sum('unanswered_query_count'))['unanswered_query_count__sum']

            total_intuitive_messages = date_filtered_mis_objects.aggregate(
                Sum('intuitive_query_count'))['intuitive_query_count__sum']

            message_analytics_list.append({
                "label": str(temp_datetime.strftime("%d-%b-%y")),
                "total_messages": total_messages,
                "total_answered_messages": total_answered_messages,
                "total_unanswered_messages": total_unanswered_messages,
                "predicted_messages_no": total_messages,
                "total_intuitive_messages": total_intuitive_messages
            })

        return message_analytics_list
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_message_analytics_data: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return message_analytics_list


def get_analytics_html_for_line_chart(chart_url, chart_heading, date_str):
    try:
        html = EMAIL_TABLE_HEADING.replace('{}', chart_heading)
        html += EMAIL_DATE_ROW.replace('{}', date_str)

        html += "<tr style='background: white;'><div class ='chart-container'> <div class='img-container-line-chart' style='margin: 10px 10px; background: #f9f9f9'>"
        html += "<img src ={} />".format(chart_url)
        html += "</div> </tr>"
        return html

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_analytics_html_for_cat: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_analytics_html_for_pie_chart(chart_url, chips_html, chart_heading, date_str):
    try:
        html = EMAIL_TABLE_HEADING.replace('{}', chart_heading)
        html += EMAIL_DATE_ROW.replace('{}', date_str)

        html += "<tr style='background: white;'><div class ='chart-container' style='padding-top: 20px;padding-bottom: 20px;'> <div class='img-container'>"
        html += "<img src ={} />".format(chart_url)
        html += """</div><div class="chips-wrapper">"""
        html += chips_html
        html += """</div> </div> </tr>"""
        return html

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_analytics_html_for_cat: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_word_cloud_data(bot, is_test_mail):
    word_cloud_text = ''
    try:
        from EasyChatApp.models import WordCloudAnalyticsDaily
        from ast import literal_eval

        if is_test_mail:
            return WORD_CLOUD_DATA
        else:
            datetime_start = (
                datetime.now() - timedelta(DEFAULT_TIME_INTERVAL_GRAPH)).date()
            datetime_end = (datetime.now() - timedelta(1)).date()

            word_cloud_objects = WordCloudAnalyticsDaily.objects.filter(
                bot=bot, date__gte=datetime_start, date__lte=datetime_end).iterator()

            for item in word_cloud_objects:
                word_cloud = literal_eval(item.word_cloud_dictionary)

                for word in word_cloud:
                    word_cloud_text += word['word'] + ' '

            return word_cloud_text

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_word_cloud_data: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return word_cloud_text


def get_word_cloud_image(data, date_str):
    try:
        html = EMAIL_TABLE_HEADING.replace('{}', 'Word Cloud')
        html += EMAIL_DATE_ROW.replace('{}', date_str)

        html += "<tr style='background: white;'><div class ='chart-container' style='padding-top: 20px;padding-bottom: 20px;'>"

        if data == '':
            html += "<p style='text-align: center; font-size: 22px; margin: 60px; display: block; width: inherit;'>Insufficient Data</p>"
        else:
            resp = requests.post('https://quickchart.io/wordcloud', json={
                'format': 'png',
                'width': 1000,
                'height': 1000,
                'fontScale': 15,
                'scale': 'linear',
                'text': data,
            })

            absolute_folder_path = settings.MEDIA_ROOT + 'word_cloud_images/'
            if not os.path.exists(absolute_folder_path):
                os.mkdir(absolute_folder_path)

            random_hash = str(uuid.uuid4())
            filepath = absolute_folder_path + 'word_cloud_' + random_hash + '.png'
            fh = open(filepath, "wb")
            fh.write(resp.content)
            fh.close()

            word_cloud_url = settings.EASYCHAT_HOST_URL + \
                '/files/word_cloud_images/' + 'word_cloud_' + random_hash + '.png'
            html += "<div class='img-container-word-cloud'>"
            html += "<img src ={} />".format(word_cloud_url)
            html += "</div>"

        html += "</div> </tr>"
        return html

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_analytics_html_for_cat: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_category_chart_config(bot_obj, is_test_mail, MISDashboard, Category):

    color_list = ["#2697FF", "#6BE119", "#2F4684", "#FFCF26",
                  "#FFA113", "#FF4387", "#FFA113", "#FF4387", "#FFA113", "#FF4387"]
    background_color_list = ["rgba(38, 151, 255, 0.08)", "rgba(107, 225, 25, 0.08)", "rgba(47, 70, 132, 0.08);", "rgba(255, 207, 38, 0.08)", "rgba(255, 161, 19, 0.08)",
                             "rgba(255, 67, 135, 0.08)", "rgba(255, 161, 19, 0.08)", "rgba(255, 67, 135, 0.08)", "rgba(255, 161, 19, 0.08)", "rgba(255, 67, 135, 0.08)"]

    if is_test_mail:
        category_dict = {
            'Loan': 25,
            'Credit': 17,
            'Debit': 13,
            'Others': 7,
        }
    else:
        category_dict = get_category_analytics(
            bot_obj, MISDashboard, Category)

    category_list = []
    message_count_list = []
    html = ""
    iterator = 0
    for data in category_dict:
        category_list.append(data)
        html += '<div class="chip" style="align-items:center;color:' + color_list[iterator] + ';background-color:' + background_color_list[iterator] + ';border: 1px solid ' + color_list[iterator] + \
            ';"><span class="dot" style="background-color:' + \
                color_list[iterator] + ';"></span> <span class="chip-label" style="margin:auto;"> ' + data + \
            ': <span style="font-weight:bold;">' + \
                str(category_dict[data]) + '</span></span></div>'
        message_count_list.append(category_dict[data])
        iterator += 1

    chart_config = {
        'type': 'doughnut',
        'data': {
            'labels': category_list,
            'datasets': [{
                'label': "Number of total users",
                'fill': True,
                'backgroundColor': color_list,
                'borderColor': color_list,
                'fontColor': '#fff',
                'data': message_count_list,
                # // spanGaps: false,
            },
            ]
        },
        'options': {
            'title': {
                'display': False,
                'text': 'Category Usage'
            },
            "plugins": {
                "datalabels": {
                    'display': False,
                    "color": "#fff",
                }
            },
            'legend': {
                'display': False,
                'position': 'right',
                'align': 'start',
                'labels': {
                    'boxWidth': 30,
                    'usePointStyle': True,
                    'padding': 50,
                    'fontColor': "#2d2d2d"
                }
            }
        }
    }

    return chart_config, html


def get_category_analytics(bot_obj, MISDashboard, Category):
    category_dict = {}
    try:
        datetime_start = (
            datetime.now() - timedelta(DEFAULT_TIME_INTERVAL_GRAPH)).date()
        datetime_end = (datetime.now() - timedelta(1)).date()

        mis_objects = MISDashboard.objects.filter(
            creation_date__gte=datetime_start, creation_date__lte=datetime_end, bot__in=[bot_obj])

        category_name_frequency = list(mis_objects.filter(~Q(category__name="") & ~Q(category=None) & ~Q(category__name="ABC")).filter(small_talk_intent=False).values(
            "category__name").order_by("category__name").annotate(frequency=Count("category__name")).order_by('-frequency'))

        for category_obj in Category.objects.filter(bot=bot_obj).iterator():
            category_dict[category_obj.name] = 0

        for category_detail in category_name_frequency:
            category_dict[category_detail["category__name"]
                          ] = category_detail["frequency"]

        sorted_category_dict = sorted(
            category_dict.items(), key=lambda x: x[1], reverse=True)
        final_dict = {}
        for iterator in range(0, min(5, len(sorted_category_dict))):
            final_dict[sorted_category_dict[iterator]
                       [0]] = sorted_category_dict[iterator][1]

        if "Others" not in final_dict and "Others" in category_dict:
            final_dict["Others"] = category_dict["Others"]

        return final_dict
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[NLP]: Error GetChannelAnalyticsAPI %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': "", 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

    return category_dict


"""
export_bot_user_msg_history : Generate the excel for bot user msgs and return the HTML with the excel link
"""


def export_bot_user_msg_history(start_date, end_date, channels, bot):
    import json
    from django.db.models import Q
    from EasyChatApp.models import Intent, MISDashboard
    from EasyChatApp.utils import get_secure_file_path
    from django.conf import settings
    from xlwt import Workbook
    import datetime
    global host_url

    automated_email_wb = Workbook(encoding="UTF-8")
    for channel in channels:
        channel_name = channel.name
        if len(channel.name) <= 16:
            channel_name = channel_name[:16]
        else:
            channel_name = channel_name[:13] + "..."

        sheet1 = automated_email_wb.add_sheet("User Messages-" + channel_name)
        sheet1.write(0, 0, "Date and Time")
        sheet1.col(0).width = 256 * 15
        sheet1.write(0, 1, "User Id")
        sheet1.col(1).width = 256 * 20
        sheet1.write(0, 2, "Question")
        sheet1.col(2).width = 256 * 100
        sheet1.write(0, 3, "Answer")
        sheet1.col(3).width = 256 * 100
        sheet1.write(0, 4, "Intent Identified")
        sheet1.col(4).width = 256 * 50

        mis_objs = MISDashboard.objects.filter(
            creation_date__gte=start_date, creation_date__lt=end_date, bot=bot, channel_name=channel).iterator()
        index = 0

        for mis_obj in mis_objs:
            try:
                intent_name = str(mis_obj.intent_name)
                date_db = str(mis_obj.date).split(".")[0]
                date_formatted = datetime.datetime.strptime(
                    date_db, "%Y-%m-%d  %H:%M:%S")
                date_humanized = datetime.datetime.strftime(
                    date_formatted, "%d-%B-%Y %H:%M %p")
                message_received = mis_obj.get_message_received()
                bot_response = mis_obj.get_bot_response()
                if message_received == None:
                    message_received = "None"
                if bot_response == None:
                    bot_response = "None"
                if len(message_received) > 30000 or len(bot_response) > 30000:
                    continue
                sheet1.write(index + 1, 0, str(date_humanized))
                sheet1.write(index + 1, 1, str(mis_obj.user_id))
                sheet1.write(index + 1, 2, message_received)
                sheet1.write(index + 1, 3, bot_response)
                sheet1.write(index + 1, 4, intent_name)
                index += 1
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("For Loop Handler %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyChatApp/email-excels/'):
        os.mkdir(settings.SECURE_MEDIA_ROOT + 'EasyChatApp/email-excels/')

    filename = "EasyChatApp/email-excels/BotUserMessageHistory_" + str(bot.pk) + "-{}.xls".format(
        str(end_date))

    automated_email_wb.save(settings.SECURE_MEDIA_ROOT + filename)

    file_url = get_secure_file_path('/secured_files/' + filename, '', bot, False, True)

    return file_url


"""
export_unanswered_data : Generate the excel for unanswered queries and return the HTML with the excel link
"""


def export_unanswered_data(start_date, end_date, bot):
    import json
    from django.db.models import Q
    from EasyChatApp.models import Intent, MISDashboard
    from EasyChatApp.utils import get_secure_file_path
    from django.conf import settings
    from xlwt import Workbook
    import datetime
    global host_url

    automated_email_wb = Workbook(encoding="UTF-8")
    sheet1 = automated_email_wb.add_sheet("User Messages")
    sheet1.write(0, 0, "Date and Time")
    sheet1.col(0).width = 256 * 15
    sheet1.write(0, 1, "User Id")
    sheet1.col(1).width = 256 * 20
    sheet1.write(0, 2, "Question")
    sheet1.col(2).width = 256 * 100
    sheet1.write(0, 3, "Answer")
    sheet1.col(3).width = 256 * 100
    sheet1.write(0, 4, "Intent Identified")
    sheet1.col(4).width = 256 * 50

    mis_objs = MISDashboard.objects.filter(
        creation_date__gte=start_date, creation_date__lt=end_date, intent_name=None, bot=bot, is_unidentified_query=True, is_intiuitive_query=False).iterator()
    index = 0

    for mis_obj in mis_objs:
        try:
            intent_name = str(mis_obj.intent_name)
            date_db = str(mis_obj.date).split(".")[0]
            date_formatted = datetime.datetime.strptime(
                date_db, "%Y-%m-%d  %H:%M:%S")
            date_humanized = datetime.datetime.strftime(
                date_formatted, "%d-%B-%Y %H:%M %p")
            message_received = mis_obj.get_message_received()
            bot_response = mis_obj.get_bot_response()
            if message_received == None:
                message_received = "None"
            if bot_response == None:
                bot_response = "None"
            if len(message_received) > 30000 or len(bot_response) > 30000:
                continue
            sheet1.write(index + 1, 0, str(date_humanized))
            sheet1.write(index + 1, 1, str(mis_obj.user_id))
            sheet1.write(index + 1, 2, message_received)
            sheet1.write(index + 1, 3, bot_response)
            sheet1.write(index + 1, 4, intent_name)
            index += 1
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(str(e) + " at line no" + str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyChatApp/email-excels/'):
        os.mkdir(settings.SECURE_MEDIA_ROOT + 'EasyChatApp/email-excels/')

    filename = "EasyChatApp/email-excels/BotUnansweredQueries_" + str(bot.pk) + "-{}.xls".format(
        str(end_date))
    automated_email_wb.save(settings.SECURE_MEDIA_ROOT + filename)

    file_url = get_secure_file_path('/secured_files/' + filename, '', bot, False, True)

    return file_url


"""
Intutive_unanswered_data : Generate the excel for Intutive queries and return the HTML with the excel link
"""


def export_intuitive_data(start_date, end_date, bot):
    import json
    from django.db.models import Q
    from EasyChatApp.models import Intent, MISDashboard
    from EasyChatApp.utils import get_secure_file_path
    from django.conf import settings
    from xlwt import Workbook
    import datetime
    global host_url

    automated_email_wb = Workbook(encoding="UTF-8")
    sheet1 = automated_email_wb.add_sheet("User Messages")
    sheet1.write(0, 0, "Date and Time")
    sheet1.col(0).width = 256 * 15
    sheet1.write(0, 1, "User Id")
    sheet1.col(1).width = 256 * 20
    sheet1.write(0, 2, "Question")
    sheet1.col(2).width = 256 * 100
    sheet1.write(0, 3, "Answer")
    sheet1.col(3).width = 256 * 100
    sheet1.write(0, 4, "Intent Identified")
    sheet1.col(4).width = 256 * 50

    mis_objs = MISDashboard.objects.filter(
        creation_date__gte=start_date, creation_date__lt=end_date, intent_name=None, bot=bot, is_intiuitive_query=True).iterator()
    index = 0

    for mis_obj in mis_objs:
        try:
            intent_name = str(mis_obj.intent_name)
            date_db = str(mis_obj.date).split(".")[0]
            date_formatted = datetime.datetime.strptime(
                date_db, "%Y-%m-%d  %H:%M:%S")
            date_humanized = datetime.datetime.strftime(
                date_formatted, "%d-%B-%Y %H:%M %p")
            message_received = mis_obj.get_message_received()
            bot_response = mis_obj.get_bot_response()
            if message_received == None:
                message_received = "None"
            if bot_response == None:
                bot_response = "None"
            if len(message_received) > 30000 or len(bot_response) > 30000:
                continue
            sheet1.write(index + 1, 0, str(date_humanized))
            sheet1.write(index + 1, 1, str(mis_obj.user_id))
            sheet1.write(index + 1, 2, message_received)
            sheet1.write(index + 1, 3, bot_response)
            sheet1.write(index + 1, 4, intent_name)
            index += 1
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(str(e) + " at line no" + str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyChatApp/email-excels/'):
        os.mkdir(settings.SECURE_MEDIA_ROOT + 'EasyChatApp/email-excels/')

    filename = "EasyChatApp/email-excels/BotIntuitiveQueries_" + str(bot.pk) + "-{}.xls".format(
        str(end_date))
    automated_email_wb.save(settings.SECURE_MEDIA_ROOT + filename)

    file_url = get_secure_file_path('/secured_files/' + filename, '', bot, False, True)

    return file_url


"""
export_user_specific_dropoff_data : Generate the CSV for User specific dropoff and return the HTML with the CSV link
"""


def export_user_specific_dropoff_data(start_date, end_date, bot):
    import json
    from django.db.models import Q
    from EasyChatApp.models import Intent, MISDashboard
    from EasyChatApp.utils import get_secure_file_path
    from django.conf import settings
    from xlwt import Workbook
    import datetime
    import pandas as pd
    global host_url

    try:
        joined_list = []
        file_url = ""
        index = 0
        while (start_date + datetime.timedelta(days=index)).strftime("%Y-%m-%d") <= end_date.strftime("%Y-%m-%d"):
            if os.path.isfile(settings.SECURE_MEDIA_ROOT + "EasyChatApp/Botwise-flow-dropoff/" + str(bot.name) + "_" + str(bot.pk) + "/User_dropoff_analytics_of_" + str((start_date + datetime.timedelta(days=index)).strftime("%Y-%m-%d")) + ".csv"):
                joined_list.append(str(settings.SECURE_MEDIA_ROOT + "EasyChatApp/Botwise-flow-dropoff/" + str(bot.name) + "_" + str(
                    bot.pk) + "/User_dropoff_analytics_of_" + str((start_date + datetime.timedelta(days=index)).strftime("%Y-%m-%d")) + ".csv"))
            index += 1

        if len(joined_list) > 0:
            df = pd.concat(map(pd.read_csv, joined_list), ignore_index=True)

            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyChatApp/email-excels/'):
                os.mkdir(settings.SECURE_MEDIA_ROOT +
                         'EasyChatApp/email-excels/')

            filename = "EasyChatApp/email-excels/user_specific_dropoff_from_" + str(start_date.strftime("%d-%m-%Y")) + "_to_" + str((end_date - timedelta(days=1)).strftime("%d-%m-%Y")) + ".csv"
            
            df.sort_values([df.columns[1], df.columns[0]],
                            axis=0,
                            ascending=[True, True],
                            inplace=True)
            df.to_csv(settings.SECURE_MEDIA_ROOT + filename, index=False)

            file_url = get_secure_file_path(
                '/secured_files/' + filename, '', bot, False, True)
        return file_url
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("User Specific Dropoff analytics, export_user_specific_dropoff_data()! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return ""


"""
export_language_based_analytics : Generate the ZIP containing CSV for Language Based Analytics and return the HTML with the ZIP link
"""


def export_language_based_analytics(start_date, end_date, bot):
    file_url = ""

    try:
        message_history_objs = MISDashboard.objects.filter(creation_date__range=[start_date, end_date], bot=bot)
        message_history_objs = return_mis_objects_excluding_blocked_sessions(message_history_objs, UserSessionHealth)
        if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyChatApp/email-excels/'):
            os.mkdir(settings.SECURE_MEDIA_ROOT + 'EasyChatApp/email-excels/')
        language_files_path = []
        zip_file_path = "EasyChatApp/email-excels/language_based_analytics_data_" + str(start_date.strftime("%d-%m-%Y")) + "_to_" + str((end_date).strftime("%d-%m-%Y")) + ".zip"
        zip_file_obj = ZipFile(settings.SECURE_MEDIA_ROOT + zip_file_path, 'w')
        for bot_language_obj in bot.languages_supported.all():
            file_name = settings.SECURE_MEDIA_ROOT + "EasyChatApp/email-excels/language_based_analytics_data_" + str(bot_language_obj.name_in_english) + "_" + str(start_date.strftime("%d-%m-%Y")) + "_to_" + str((end_date).strftime("%d-%m-%Y")) + ".csv"
            specific_language_file = open(file_name, "w")
            writer = csv.writer(specific_language_file)
            add_default_values(writer)
            add_data(writer, message_history_objs.filter(selected_language=bot_language_obj).iterator(), bot.name)
            language_files_path.append(file_name)
            specific_language_file.close()
            zip_file_obj.write(file_name, os.path.basename(file_name))
        zip_file_obj.close()
        for language_file_path in language_files_path:
            if os.path.isfile(language_file_path):
                os.remove(language_file_path)

        file_url = get_secure_file_path('/secured_files/' + zip_file_path, '', bot, False, True)
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Language based analytics, export_language_based_analytics()! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        
    return file_url


"""
export_csat_data : Generate the ZIP containing CSV for Language Based Analytics and return the HTML with the ZIP link
"""


def export_csat_data(start_date, end_date, bot):
    file_url = ""

    try:
        date_diff = end_date - start_date
        temp_file_path = ""
        if date_diff.days == 1:
            temp_file_path = "csat-data/bot-" + str(bot.pk) + "/CSATDataLastOneDay_" + start_date.strftime("%d-%m-%Y") + ".csv"
        elif date_diff.days == 7:
            temp_file_path = "csat-data/bot-" + str(bot.pk) + "/CSATDataLastSevenDays_from_" + start_date.strftime("%d-%m-%Y") + "_to_" + (end_date - timedelta(1)).strftime("%d-%m-%Y") + ".csv"
        elif date_diff.days == 15:
            temp_file_path = "csat-data/bot-" + str(bot.pk) + "/CSATDataLastFifteenDays_from_" + start_date.strftime("%d-%m-%Y") + "_to_" + (end_date - timedelta(1)).strftime("%d-%m-%Y") + ".csv"
        elif date_diff.days == 30:
            temp_file_path = "csat-data/bot-" + str(bot.pk) + "/CSATDataLastThirtyDays_from_" + start_date.strftime("%d-%m-%Y") + "_to_" + (end_date - timedelta(1)).strftime("%d-%m-%Y") + ".csv"
        elif date_diff.days == 60:
            temp_file_path = "csat-data/bot-" + str(bot.pk) + "/CSATDataLastSixtyDays_from_" + start_date.strftime("%d-%m-%Y") + "_to_" + (end_date - timedelta(1)).strftime("%d-%m-%Y") + ".csv"
        elif date_diff.days == 90:
            temp_file_path = "csat-data/bot-" + str(bot.pk) + "/CSATDataLastNintyDays_from_" + start_date.strftime("%d-%m-%Y") + "_to_" + (end_date - timedelta(1)).strftime("%d-%m-%Y") + ".csv"
        
        if temp_file_path == "":
            return file_url
        elif os.path.isfile(settings.MEDIA_ROOT + temp_file_path):
            file_url = get_secure_file_path("/files/" + temp_file_path, '', bot, False, True)
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("CSAT Data, export_csat_data()! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        
    return file_url


"""
generate_mail : It will create the HTML and send the mail to the given email ids
"""


def generate_mail(bot_name, anaytics_html, email, message_subject, display_date="August 21, 2021"):

    config_obj = get_developer_console_settings()

    EMAIL_COMPANY_LOGO = get_email_company_logo()

    EMAIL_FOOTER = get_email_footer()

    EMAIL_HEAD = get_email_company_head()

    body = """
        """ + EMAIL_HEAD + EMAIL_BODY_START + EMAIL_OUTER_TABLE_START + EMAIL_COMPANY_LOGO + EMAIL_ANALYTICS_START.replace('{}', bot_name).replace('()', display_date) + anaytics_html + EMAIL_FOOTER.format(config_obj.legal_name) + EMAIL_OUTER_TABLE_END + EMAIL_BODY_END + """
    """

    send_email_to_customer_via_awsses(email, message_subject, body)


"""
send_mail : Send mail to the given email id.
"""


# def send_mail(FROM, TO, message_as_string, PASSWORD):
#     import smtplib
#     # # The actual sending of the e-mail
#     server = smtplib.SMTP('smtp.gmail.com:587')
#     # Credentials (if needed) for sending the mail
#     password = PASSWORD
#     # Start tls handshaking
#     server.starttls()
#     # Login to server
#     server.login(FROM, password)
#     # Send mail
#     server.sendmail(FROM, TO, message_as_string)
#     # Close session
#     server.quit()
