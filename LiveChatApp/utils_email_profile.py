from datetime import datetime, timedelta
import sys
import json
import logging
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from django.http import FileResponse
from LiveChatApp.utils import *
from LiveChatApp.constants_email_html import *
from LiveChatApp.constants_email_profile import *
from LiveChatApp.constants import DEFAULT_AGENT_CONNECTION_RATE, DATE_DD_MMM_YY, DATE_15_08_21_08, INTERACTION_PER_CHAT, EMAIL_EXCEL_PATH
from LiveChatApp.utils_analytics import get_average
from LiveChatApp.models import LiveChatCustomer, LiveChatMISDashboard, LiveChatGuestAgentAudit, LiveChatSessionManagement, LiveChatFileAccessManagement
from EasyChatApp.models import Bot, Channel
from urllib.parse import quote
from os import path
from os.path import basename
import xlwt
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses
logger = logging.getLogger(__name__)


def get_channel_list(Channel):
    try:
        channel_list = []

        channel_objs = Channel.objects.all()
        for channel_obj in channel_objs:
            channel_list.append(
                {"name": channel_obj.name, "icon": channel_obj.icon})

        return channel_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_channel_list! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return []


def get_graph_chart_reports(start_date, end_date, graph_chart_reports, user_obj_list):

    try:
        no_of_days = (end_date - start_date).days + 1
        labels = []
        chats_raised = []
        chats_resolved = []
        abandoned_chats = []
        offline_chats = []
        declined_chats = []

        is_chats_raised = False
        is_chats_resolved = False
        is_abandoned_chats = False
        is_offline_chats = False
        is_declined_chats = False

        if 'chats_raised' in graph_chart_reports:
            is_chats_raised = True

        if 'chats_resolved' in graph_chart_reports:
            is_chats_resolved = True

        if 'abandoned_chats' in graph_chart_reports:
            is_abandoned_chats = True

        if 'offline_chats' in graph_chart_reports:
            is_offline_chats = True

        if 'declined_chats' in graph_chart_reports:
            is_declined_chats = True

        bot_objs = Bot.objects.none()
        for user_obj in user_obj_list:
            bot_objs |= user_obj.bots.all()

        bot_objs = bot_objs.distinct()
        chats_resolved_count = 0
        declined_chats_count = 0
        offline_chats_count = 0
        abandoned_chats_count = 0

        for day in range(no_of_days):
            curr_date = (start_date + timedelta(days=day)).date()
            livechat_cust_objs = LiveChatCustomer.objects.filter(
                request_raised_date=curr_date, agent_id__in=user_obj_list)

            if is_chats_resolved:
                chats_resolved_count = livechat_cust_objs.filter(
                    is_session_exp=True).count()
                chats_resolved.append(chats_resolved_count)

            if is_declined_chats:
                declined_chats_count = LiveChatCustomer.objects.filter(
                    request_raised_date=curr_date, agent_id=None, abruptly_closed=True, bot__in=bot_objs).count()
                declined_chats.append(declined_chats_count)

            if is_abandoned_chats:
                abandoned_chats_count = LiveChatCustomer.objects.filter(
                    request_raised_date=curr_date, is_system_denied=True, bot__in=bot_objs).count()
                abandoned_chats.append(abandoned_chats_count)

            if is_offline_chats:
                offline_chats_count = LiveChatCustomer.objects.filter(bot__in=bot_objs,
                                                                      request_raised_date=curr_date, is_denied=True, is_system_denied=False).count()
                offline_chats.append(offline_chats_count)

            if is_chats_raised:
                chats_raised_count = LiveChatCustomer.objects.filter(
                    request_raised_date=curr_date, bot__in=bot_objs).count()
                chats_raised.append(chats_raised_count)

            labels.append(curr_date.strftime(DATE_DD_MMM_YY))

        return labels, chats_raised, chats_resolved, abandoned_chats, offline_chats, declined_chats

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_graph_chart_reports: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return []


def get_graph_interaction_data(start_date, end_date, user_obj_list):

    try:
        no_of_days = (end_date - start_date).days + 1
        graph_interaction_data = []
        labels = []

        for day in range(no_of_days):

            curr_date = (start_date + timedelta(days=day)).date()

            livechat_cust_objs = LiveChatCustomer.objects.filter(
                request_raised_date=curr_date, agent_id__in=user_obj_list)
            total_interactions = LiveChatMISDashboard.objects.filter(
                livechat_customer__in=livechat_cust_objs).count()

            average_interactions = get_average(
                total_interactions, livechat_cust_objs.count())

            graph_interaction_data.append(average_interactions)

            labels.append(curr_date.strftime(DATE_DD_MMM_YY))

        return graph_interaction_data, labels

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_graph_interaction_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return []


def get_avg_handle_time_data(start_date, end_date, user_obj_list):

    try:
        no_of_days = (end_date - start_date).days + 1
        graph_avg_handle_time_data = []
        labels = []

        for day in range(no_of_days):

            curr_date = (start_date + timedelta(days=day)).date()

            livechat_cust_objs = LiveChatCustomer.objects.filter(
                request_raised_date=curr_date, agent_id__in=user_obj_list)
            total_handle = livechat_cust_objs.aggregate(Sum('chat_duration'))[
                'chat_duration__sum']
            average_handle_time = get_average(
                total_handle, livechat_cust_objs.count())
            average_handle_time = average_handle_time // 60

            graph_avg_handle_time_data.append(average_handle_time)

            labels.append(curr_date.strftime(DATE_DD_MMM_YY))

        return graph_avg_handle_time_data, labels

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_avg_handle_time_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return []


def get_date_wise_table_records_data(count_variations, table_records, user_obj_list):

    try:
        date_wise_table_records_data = {}
        chats_raised = {}
        chats_resolved = {}
        abandoned_chats = {}
        offline_chats = {}
        declined_chats = {}
        avg_handle_time = {}
        group_chats = {}
        agents_logged_in = {}
        avg_interactions = {}
        avg_wait_time = {}

        is_chats_raised = False
        is_chats_resolved = False
        is_abandoned_chats = False
        is_offline_chats = False
        is_declined_chats = False
        is_avg_handle_time = False
        is_group_chats = False
        is_agents_logged_in = False
        is_avg_interactions = False
        is_avg_wait_time = False

        if 'chats_raised' in table_records:
            is_chats_raised = True

        if 'chats_resolved' in table_records:
            is_chats_resolved = True

        if 'abandoned_chats' in table_records:
            is_abandoned_chats = True

        if 'offline_chats' in table_records:
            is_offline_chats = True

        if 'declined_chats' in table_records:
            is_declined_chats = True

        if 'avg_handle_time' in table_records:
            is_avg_handle_time = True

        if 'group_chats' in table_records:
            is_group_chats = True

        if 'agents_logged_in' in table_records:
            is_agents_logged_in = True

        if 'avg_interactions' in table_records:
            is_avg_interactions = True

        if 'avg_wait_time' in table_records:
            is_avg_wait_time = True

        bot_objs = Bot.objects.none()
        for user_obj in user_obj_list:
            bot_objs |= user_obj.bots.all()

        bot_objs = bot_objs.distinct()
        chats_resolved_count = 0
        declined_chats_count = 0
        offline_chats_count = 0
        abandoned_chats_count = 0

        for count_variation in count_variations:
            if count_variation == '1':
                start_date = (datetime.now() -
                              timedelta(1)).date()
                end_date = (datetime.now() -
                            timedelta(1)).date()

            if count_variation == '2':
                start_date = (datetime.today(
                ) - timedelta(days=datetime.today().isoweekday() % 7)).date()
                end_date = (datetime.now() -
                            timedelta(1)).date()

            if count_variation == '3':
                start_date = datetime.today().date(
                ) - timedelta(days=int(datetime.today().date().strftime("%d")) - 1)
                end_date = (datetime.now() -
                            timedelta(1)).date()

            if count_variation == '4':
                start_date = (datetime(datetime.today().year, 1, 1)).date()
                end_date = (datetime.now() -
                            timedelta(1)).date()

            if count_variation == '5':
                start_date = (datetime.now() -
                              timedelta(30)).date()
                end_date = (datetime.now() -
                            timedelta(1)).date()

            livechat_cust_objs = LiveChatCustomer.objects.filter(
                request_raised_date__gte=start_date, request_raised_date__lte=end_date, agent_id__in=user_obj_list)

            if is_chats_resolved:
                chats_resolved_count = livechat_cust_objs.filter(
                    is_session_exp=True).count()
                chats_resolved[count_variation] = str(chats_resolved_count)

            if is_declined_chats:
                declined_chats_count = LiveChatCustomer.objects.filter(
                    request_raised_date__gte=start_date, request_raised_date__lte=end_date, agent_id=None, abruptly_closed=True, bot__in=bot_objs).count()
                declined_chats[count_variation] = str(declined_chats_count)

            if is_abandoned_chats:
                abandoned_chats_count = LiveChatCustomer.objects.filter(
                    request_raised_date__gte=start_date, request_raised_date__lte=end_date, is_system_denied=True, bot__in=bot_objs).count()
                abandoned_chats[count_variation] = str(abandoned_chats_count)

            if is_offline_chats:
                offline_chats_count = LiveChatCustomer.objects.filter(bot__in=bot_objs,
                                                                      request_raised_date__gte=start_date, request_raised_date__lte=end_date, is_denied=True, is_system_denied=False).count()
                offline_chats[count_variation] = str(offline_chats_count)

            if is_chats_raised:
                chats_raised_count = LiveChatCustomer.objects.filter(
                    request_raised_date__gte=start_date, request_raised_date__lte=end_date, bot__in=bot_objs).count()
                chats_raised[count_variation] = str(chats_raised_count)

            if is_avg_handle_time:
                total_handle = livechat_cust_objs.aggregate(Sum('chat_duration'))[
                    'chat_duration__sum']
                average_handle_time = get_average(
                    total_handle, livechat_cust_objs.count())
                average_handle_time = average_handle_time // 60

                avg_handle_time[count_variation] = str(average_handle_time)

            if is_avg_wait_time:
                total_wait = livechat_cust_objs.aggregate(Sum('queue_time'))[
                    'queue_time__sum']
                average_wait_time = get_average(
                    total_wait, livechat_cust_objs.count())

                avg_wait_time[count_variation] = str(average_wait_time)

            if is_avg_interactions:
                total_interactions = LiveChatMISDashboard.objects.filter(
                    livechat_customer__in=livechat_cust_objs).count()
                average_interactions = get_average(
                    total_interactions, livechat_cust_objs.count())

                avg_interactions[count_variation] = str(average_interactions)

            if is_group_chats:
                group_chats_count = LiveChatGuestAgentAudit.objects.filter(
                    livechat_agent__in=user_obj_list, action_datetime__date__gte=start_date, action_datetime__date__lte=end_date, action="accept").count()
                group_chats[count_variation] = str(group_chats_count)

            if is_agents_logged_in:
                agents_logged_in_count = LiveChatSessionManagement.objects.filter(
                    user__in=user_obj_list, session_starts_at__date__gte=start_date, session_ends_at__date__lte=end_date).values_list('user', flat=True).distinct().count()
                agents_logged_in[count_variation] = str(agents_logged_in_count)

        date_wise_table_records_data["chats_raised"] = chats_raised

        date_wise_table_records_data["chats_resolved"] = chats_resolved

        date_wise_table_records_data["agents_logged_in"] = agents_logged_in

        date_wise_table_records_data["abandoned_chats"] = abandoned_chats

        date_wise_table_records_data["avg_interactions"] = avg_interactions

        date_wise_table_records_data["group_chats"] = group_chats

        date_wise_table_records_data["offline_chats"] = offline_chats

        date_wise_table_records_data["avg_handle_time"] = avg_handle_time

        date_wise_table_records_data["declined_chats"] = declined_chats

        date_wise_table_records_data["avg_wait_time"] = avg_wait_time

        return date_wise_table_records_data

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_date_wise_table_records_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return {}


def get_channel_wise_table_records_data(start_date, end_date, channel_list, table_records, user_obj_list):

    try:
        channel_wise_table_records_data = {}
        chats_raised = {}
        chats_resolved = {}
        abandoned_chats = {}
        offline_chats = {}
        declined_chats = {}
        avg_handle_time = {}
        group_chats = {}
        agents_logged_in = {}
        avg_interactions = {}
        avg_wait_time = {}

        is_chats_raised = False
        is_chats_resolved = False
        is_abandoned_chats = False
        is_offline_chats = False
        is_declined_chats = False
        is_avg_handle_time = False
        is_group_chats = False
        is_agents_logged_in = False
        is_avg_interactions = False
        is_avg_wait_time = False

        if 'chats_raised' in table_records:
            is_chats_raised = True

        if 'chats_resolved' in table_records:
            is_chats_resolved = True

        if 'abandoned_chats' in table_records:
            is_abandoned_chats = True

        if 'offline_chats' in table_records:
            is_offline_chats = True

        if 'declined_chats' in table_records:
            is_declined_chats = True

        if 'avg_handle_time' in table_records:
            is_avg_handle_time = True

        if 'group_chats' in table_records:
            is_group_chats = True

        if 'agents_logged_in' in table_records:
            is_agents_logged_in = True

        if 'avg_interactions' in table_records:
            is_avg_interactions = True

        if 'avg_wait_time' in table_records:
            is_avg_wait_time = True

        bot_objs = Bot.objects.none()
        for user_obj in user_obj_list:
            bot_objs |= user_obj.bots.all()

        bot_objs = bot_objs.distinct()
        chats_resolved_count = 0
        declined_chats_count = 0
        offline_chats_count = 0
        abandoned_chats_count = 0

        if len(channel_list) == 0:
            channel_objs = Channel.objects.all()
        else:
            channel_objs = Channel.objects.filter(name__in=channel_list)

        for channel in channel_objs:

            livechat_cust_objs = LiveChatCustomer.objects.filter(
                request_raised_date__gte=start_date, request_raised_date__lte=end_date, agent_id__in=user_obj_list, channel=channel)

            if is_chats_resolved:
                chats_resolved_count = livechat_cust_objs.filter(
                    is_session_exp=True).count()
                chats_resolved[channel.name] = str(chats_resolved_count)

            if is_declined_chats:
                declined_chats_count = LiveChatCustomer.objects.filter(
                    request_raised_date__gte=start_date, request_raised_date__lte=end_date, agent_id=None, abruptly_closed=True, bot__in=bot_objs, channel=channel).count()
                declined_chats[channel.name] = str(declined_chats_count)

            if is_abandoned_chats:
                abandoned_chats_count = LiveChatCustomer.objects.filter(
                    request_raised_date__gte=start_date, request_raised_date__lte=end_date, is_system_denied=True, bot__in=bot_objs, channel=channel).count()
                abandoned_chats[channel.name] = str(abandoned_chats_count)

            if is_offline_chats:
                offline_chats_count = LiveChatCustomer.objects.filter(bot__in=bot_objs,
                                                                      request_raised_date__gte=start_date, request_raised_date__lte=end_date, is_denied=True, is_system_denied=False, channel=channel).count()
                offline_chats[channel.name] = str(offline_chats_count)

            if is_chats_raised:
                chats_raised_count = LiveChatCustomer.objects.filter(
                    request_raised_date__gte=start_date, request_raised_date__lte=end_date, bot__in=bot_objs, channel=channel).count()
                chats_raised[channel.name] = str(chats_raised_count)

            if is_avg_handle_time:
                total_handle = livechat_cust_objs.aggregate(Sum('chat_duration'))[
                    'chat_duration__sum']
                average_handle_time = get_average(
                    total_handle, livechat_cust_objs.count())
                average_handle_time = average_handle_time // 60

                avg_handle_time[channel.name] = str(average_handle_time)

            if is_avg_interactions:
                total_interactions = LiveChatMISDashboard.objects.filter(
                    livechat_customer__in=livechat_cust_objs).count()
                average_interactions = get_average(
                    total_interactions, livechat_cust_objs.count())

                avg_interactions[channel.name] = str(average_interactions)

            if is_group_chats:
                group_chats_count = LiveChatGuestAgentAudit.objects.filter(
                    livechat_customer__in=livechat_cust_objs, action="accept").count()
                group_chats[channel.name] = str(group_chats_count)

            if is_agents_logged_in:
                agents_logged_in_count = LiveChatSessionManagement.objects.filter(
                    user__in=user_obj_list, session_starts_at__date__gte=start_date, session_ends_at__date__lte=end_date).values_list('user', flat=True).distinct().count()
                agents_logged_in[channel.name] = str(agents_logged_in_count)

            if is_avg_wait_time:
                total_wait = livechat_cust_objs.aggregate(Sum('queue_time'))[
                    'queue_time__sum']
                average_wait_time = get_average(
                    total_wait, livechat_cust_objs.count())

                avg_wait_time[channel.name] = str(average_wait_time)

        channel_wise_table_records_data["chats_raised"] = chats_raised

        channel_wise_table_records_data["chats_resolved"] = chats_resolved

        channel_wise_table_records_data["agents_logged_in"] = agents_logged_in

        channel_wise_table_records_data["abandoned_chats"] = abandoned_chats

        channel_wise_table_records_data["avg_interactions"] = avg_interactions

        channel_wise_table_records_data["group_chats"] = group_chats

        channel_wise_table_records_data["offline_chats"] = offline_chats

        channel_wise_table_records_data["avg_handle_time"] = avg_handle_time

        channel_wise_table_records_data["declined_chats"] = declined_chats

        channel_wise_table_records_data["avg_wait_time"] = avg_wait_time

        return channel_wise_table_records_data

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_channel_wise_table_records_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return {}


def send_sample_email(email_profile_obj):

    try:
        status_code = 200
        mail_html = ""

        user_obj = email_profile_obj.livechat_user
        user_obj_list = get_agents_under_this_user(user_obj)

        if email_profile_obj.is_graph_parameters_enabled:
            start_date = (datetime.now() - timedelta(days=7))
            end_date = (datetime.now() - timedelta(days=1))
            if email_profile_obj.graph_parameters.is_graph_chart_reports_enabled:
                graph_chart_reports = email_profile_obj.graph_parameters.graph_chart_reports

                graph_chart_reports_config = get_graph_chart_reports_config(
                    email_profile_obj, start_date, end_date, user_obj_list, graph_chart_reports, True)

                encoded_config = quote(json.dumps(graph_chart_reports_config))
                graph_chart_reports_url = f'https://quickchart.io/chart?c={encoded_config}'

                graph_chart_reports_html = get_html_for_graph_chart_reports(
                    graph_chart_reports_url, "Chat Reports", DATE_15_08_21_08)

                mail_html += graph_chart_reports_html

            if email_profile_obj.graph_parameters.is_graph_interaction_enabled:

                graph_interactions_config = get_graph_interactions_config(
                    email_profile_obj, start_date, end_date, user_obj_list, True)

                encoded_config = quote(json.dumps(graph_interactions_config))
                graph_interactions_url = f'https://quickchart.io/chart?c={encoded_config}'

                graph_interactions_html = get_html_for_graph_interactions(
                    graph_interactions_url, INTERACTION_PER_CHAT, DATE_15_08_21_08)

                mail_html += graph_interactions_html

            if email_profile_obj.graph_parameters.is_graph_avg_handle_time_enabled:

                graph_avg_handle_time_config = get_graph_avg_handle_time_config(
                    email_profile_obj, start_date, end_date, user_obj_list, True)

                encoded_config = quote(json.dumps(
                    graph_avg_handle_time_config))
                graph_avg_handle_time_url = f'https://quickchart.io/chart?c={encoded_config}'

                graph_avg_handle_time_html = get_html_for_graph_avg_handle_time(
                    graph_avg_handle_time_url, "Average Handle Time", DATE_15_08_21_08)

                mail_html += graph_avg_handle_time_html

        if email_profile_obj.is_table_parameters_enabled:
            count_variation = json.loads(
                email_profile_obj.table_parameters.count_variation)
            channel_list = json.loads(
                email_profile_obj.table_parameters.channel)
            table_records = json.loads(
                email_profile_obj.table_parameters.table_records)

            if len(table_records) > 0:
                if len(count_variation) > 0:
                    mail_html += EMAIL_TABLE_HEADING.replace(
                        '{}', 'Record Parameters')
                    mail_html += EMAIL_TABLE_PARAMETERS_START
                    mail_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                        '{}', 'Count')

                    for count in count_variation:
                        if count == '1':
                            count_header = 'Daily'
                        if count == '2':
                            count_header = 'WTD'
                        if count == '3':
                            count_header = 'MTD'
                        if count == '4':
                            count_header = 'YTD'
                        if count == '5':
                            count_header = 'LMSD'
                        mail_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                            '{}', count_header)

                    mail_html += EMAIL_TABLE_PARAMETERS_HEAD_END

                    mail_html += get_table_records_html(
                        table_records, count_variation, TABLE_RECORD_HEADERS, TABLE_COUNT_RECORD_DATA)

                    mail_html += EMAIL_TABLE_PARAMETERS_END

                if len(channel_list) > 0:
                    if len(count_variation) == 0:
                        mail_html += EMAIL_TABLE_HEADING.replace(
                            '{}', 'Record Parameters')
                    mail_html += EMAIL_TABLE_PARAMETERS_START
                    mail_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                        '{}', 'Channel (15/08/21 - 21/08/21)')

                    for channel in channel_list:
                        mail_html += EMAIL_TABLE_PARAMETERS_HEAD.replace(
                            '{}', channel)

                    mail_html += EMAIL_TABLE_PARAMETERS_HEAD_END

                    mail_html += get_table_records_html(
                        table_records, channel_list, TABLE_RECORD_HEADERS, TABLE_CHANNEL_RECORD_DATA)

                    mail_html += EMAIL_TABLE_PARAMETERS_END

        if email_profile_obj.is_attachment_parameters_enabled or email_profile_obj.is_table_parameters_enabled:
            start_date = (datetime.now() - timedelta(days=7))
            end_date = (datetime.now() - timedelta(days=1))
            attachment_params = json.loads(
                email_profile_obj.attachment_parameters.attachment_parameters)

            if len(attachment_params) > 0:
                mail_html += EMAIL_DOWNLOAD_REPORTS_START
                for param in attachment_params:
                    mail_html += EMAIL_REPORT_BUTTON.replace(
                        '()', settings.EASYCHAT_HOST_URL + DOWNLOAD_REPORTS_DATA[param]).replace('{}', DOWNLOAD_REPORTS_MAP[param])

                if email_profile_obj.is_table_parameters_enabled:
                    mailer_summary_path = get_mailer_report_path(start_date, end_date, user_obj, user_obj_list, email_profile_obj, True)
                    mail_html += EMAIL_REPORT_BUTTON.replace(
                        '()', mailer_summary_path).replace('{}', "Mail Summary")

                mail_html += EMAIL_DOWNLOAD_REPORTS_END

            elif email_profile_obj.is_table_parameters_enabled:
                mail_html += EMAIL_DOWNLOAD_REPORTS_START

                mailer_summary_path = get_mailer_report_path(start_date, end_date, user_obj, user_obj_list, email_profile_obj, True)
                mail_html += EMAIL_REPORT_BUTTON.replace(
                    '()', mailer_summary_path).replace('{}', "Mail Summary")

                mail_html += EMAIL_DOWNLOAD_REPORTS_END

        email_subject = email_profile_obj.email_subject
        email_receivers = json.loads(email_profile_obj.email_address)
        for email in email_receivers:
            try:
                email_profile_html = mail_html
                if email_profile_obj.agent_connection_rate != '' and DEFAULT_AGENT_CONNECTION_RATE < int(email_profile_obj.agent_connection_rate) and email.find("getcogno.ai") != -1:
                    email_profile_html = LIVECHAT_AGENT_CONNECTION_RATE.replace(
                        '{}', str(DEFAULT_AGENT_CONNECTION_RATE)) + mail_html

                generate_mail(email_profile_html,
                              email, email_subject, "August 16, 2021")
            except Exception as e:
                status_code = 102
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("send_sample_email > genrate mail: %s %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside send_sample_email: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return status_code


def get_agent_connection_rate(email_profile_obj, start_date, end_date, user_obj_list):
    try:

        bot_objs = Bot.objects.none()
        for user_obj in user_obj_list:
            bot_objs |= user_obj.bots.all()

        bot_objs = bot_objs.distinct()

        livechat_cust_objs = LiveChatCustomer.objects.filter(
            request_raised_date__gte=start_date, request_raised_date__lte=end_date, bot__in=bot_objs)

        if livechat_cust_objs.count() == 0:
            return 0

        assigned_chats = (livechat_cust_objs.exclude(agent_id=None)).count()

        agent_connection_rate = (
            assigned_chats / livechat_cust_objs.count()) * 100

        return int(agent_connection_rate)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside get_agent_connection_rate: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return 0


def get_graph_chart_reports_config(email_profile_obj, start_date, end_date, user_obj_list, graph_chart_reports, is_test_mail):

    chats_raised = []
    chats_resolved = []
    abandoned_chats = []
    offline_chats = []
    declined_chats = []
    label_list = []

    if is_test_mail:
        label_list = ['15-Aug-21', '16-Aug-21', '17-Aug-21',
                      '18-Aug-21', '19-Aug-21', '20-Aug-21', '21-Aug-21']
        chats_raised = ['21', '30', '18', '20', '26', '23', '22']
        chats_resolved = ['21', '26', '11', '19', '20', '18', '20']
        abandoned_chats = ['0', '4', '7', '1', '6', '5', '2']
        offline_chats = ['22', '32', '21', '20', '28', '24', '22']
        declined_chats = ['7', '4', '9', '1', '8', '5', '2']
    else:
        label_list, chats_raised, chats_resolved, abandoned_chats, offline_chats, declined_chats = get_graph_chart_reports(
            start_date, end_date, graph_chart_reports, user_obj_list)

    datasets = []
    if 'chats_raised' in graph_chart_reports:
        datasets.append({
            'label': "Chats Raised",
            'backgroundColor': "#f9f9f9",
            'borderColor': "#4285F4",
            'borderDash': [5, 5],
            'color': "#FF4387",
            'pointRadius': 2,
            'borderWidth': 2,
            'data': chats_raised,
            "datalabels": {
                        "align": 'center',
                        'display': True,
                        'color': "#2d2d2d",
                        }
        })

    if 'chats_resolved' in graph_chart_reports:
        datasets.append({
            'label': "Chats Resolved",
            'backgroundColor': "#f9f9f9",
            'borderColor': "#34A853",
            'borderDash': [5, 5],
            'pointRadius': 2,
            'borderWidth': 2,
            'data': chats_resolved,
            "datalabels": {
                        "align": 'center',
                        'display': True,
                        'color': "#2d2d2d",
                        }

        })

    if 'abandoned_chats' in graph_chart_reports:
        datasets.append({
            'label': "Offline Chats",
            'backgroundColor': "#f9f9f9",
            'borderColor': "#FBC014",
            'borderDash': [5, 5],
            'pointRadius': 2,
            'borderWidth': 2,
            'data': abandoned_chats,
            "datalabels": {
                        "align": 'center',
                        'display': True,
                        'color': "#2d2d2d",
                        }

        })

    if 'offline_chats' in graph_chart_reports:
        datasets.append({
            'label': "Missed Chats",
            'backgroundColor': "#f9f9f9",
            'borderColor': "#EA4335",
            'borderDash': [5, 5],
            'pointRadius': 2,
            'borderWidth': 2,
            'data': offline_chats,
            "datalabels": {
                        "align": 'center',
                        'display': True,
                        'color': "#2d2d2d",
                        }

        })

    if 'declined_chats' in graph_chart_reports:
        datasets.append({
            'label': "Abandoned Chats",
            'backgroundColor': "#f9f9f9",
            'borderColor': "#FF6D01",
            'borderDash': [5, 5],
            'pointRadius': 2,
            'borderWidth': 2,
            'data': declined_chats,
            "datalabels": {
                        "align": 'center',
                        'display': True,
                        'color': "#2d2d2d",
                        }

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
                'text': 'Chat Reports'
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
                    'usePointStyle': True,
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
                        "labelString": 'Chat Reports'
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


def get_html_for_graph_chart_reports(chart_url, chart_heading, date_str):
    try:
        html = EMAIL_TABLE_HEADING.replace('{}', chart_heading)
        html += EMAIL_DATE_ROW.replace('{}', date_str)

        html += "<tr style='background: white;'><div class ='chart-container''> <div class='img-container-line-chart' style='margin: 10px 10px; background: #f9f9f9'>"
        html += "<img src ={} />".format(chart_url)
        html += "</div> </tr>"
        return html

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_html_for_graph_chart_reports: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_graph_interactions_config(email_profile_obj, start_date, end_date, user_obj_list, is_test_mail):

    label_list = []
    graph_interaction_data = []
    if is_test_mail:
        label_list = ['15-Aug-21', '16-Aug-21', '17-Aug-21',
                      '18-Aug-21', '19-Aug-21', '20-Aug-21', '21-Aug-21']
        graph_interaction_data = ['3', '7', '9', '4', '5', '2', '6']
    else:
        graph_interaction_data, label_list = get_graph_interaction_data(
            start_date, end_date, user_obj_list)

    chart_config = {
        'type': 'line',
                'data': {
                    'labels': label_list,
                    'datasets': [{
                        'label': INTERACTION_PER_CHAT,
                        'fill': False,
                        # // lineTension: 0.1,
                        # //backgroundColor: gradient,
                        # // backgroundColor: "#3445C6",
                        'borderWidth': 1,
                        'borderColor': "#3445C6",
                        'fontColor': '#fff',

                        'data': graph_interaction_data,
                        # // spanGaps: false,
                    },
                    ]
                },
        'options': {
                    'title': {
                        'display': False,
                        'text': INTERACTION_PER_CHAT
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
                            'usePointStyle': True,
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
                                'labelString': INTERACTION_PER_CHAT,
                                'beginAtZero': True,
                                # //stepSize: min_step_size,
                            },
                            "scaleLabel": {
                                "display": True,
                                "labelString": INTERACTION_PER_CHAT
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
                                # //stepSize: min_step_size,
                            },
                            "gridLines": {
                                "color": "#f9f9f9"
                            },
                        }]
                    },
                    'responsive': True,
                    'maintainAspectRatio': False,
                }

    }

    return chart_config


def get_html_for_graph_interactions(chart_url, chart_heading, date_str):
    try:
        html = EMAIL_TABLE_HEADING.replace('{}', chart_heading)
        html += EMAIL_DATE_ROW.replace('{}', date_str)

        html += "<tr style='background: white;'><div class ='chart-container''> <div class='img-container-line-chart' style='margin: 10px 10px; background: #f9f9f9'>"
        html += "<img src ={} />".format(chart_url)
        html += "</div> </tr>"
        return html

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_html_for_graph_interactions: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_graph_avg_handle_time_config(email_profile_obj, start_date, end_date, user_obj_list, is_test_mail):

    label_list = []
    graph_avg_handle_time_data = []
    if is_test_mail:
        label_list = ['15-Aug-21', '16-Aug-21', '17-Aug-21',
                      '18-Aug-21', '19-Aug-21', '20-Aug-21', '21-Aug-21']
        graph_avg_handle_time_data = ['13', '17', '19', '14', '15', '12', '16']
    else:
        graph_avg_handle_time_data, label_list = get_avg_handle_time_data(
            start_date, end_date, user_obj_list)

    chart_config = {
        'type': 'line',
                'data': {
                    'labels': label_list,
                    'datasets': [{
                        'label': "Average Handle Time",
                        'fill': False,
                        # // lineTension: 0.1,
                        # //backgroundColor: gradient,
                        # // backgroundColor: "#3445C6",
                        'borderWidth': 1,
                        'borderColor': "#3445C6",
                        'fontColor': '#fff',

                        'data': graph_avg_handle_time_data,
                        # // spanGaps: false,
                    },
                    ]
                },
        'options': {
                    'title': {
                        'display': False,
                        'text': 'Average Handle Time'
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
                            'usePointStyle': True,
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
                                'labelString': "Minutes",
                                'beginAtZero': True,
                                # //stepSize: min_step_size,
                            },
                            "scaleLabel": {
                                "display": True,
                                "labelString": 'Minutes'
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
                                # //stepSize: min_step_size,
                            },
                            "gridLines": {
                                "color": "#f9f9f9"
                            },
                        }]
                    },
                    'responsive': True,
                    'maintainAspectRatio': False,
                }

    }

    return chart_config


def get_html_for_graph_avg_handle_time(chart_url, chart_heading, date_str):
    try:
        html = EMAIL_TABLE_HEADING.replace('{}', chart_heading)
        html += EMAIL_DATE_ROW.replace('{}', date_str)

        html += "<tr style='background: white;'><div class ='chart-container''> <div class='img-container-line-chart' style='margin: 10px 10px; background: #f9f9f9'>"
        html += "<img src ={} />".format(chart_url)
        html += "</div> </tr>"
        return html

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_html_for_graph_avg_handle_time: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_table_records_html(parameters1, parameters2, data_map, data_dict):
    table_html = ""
    for param in parameters1:
        table_html += EMAIL_TABLE_PARAMERTERS_TR_START
        table_html += EMAIL_TABLE_PARAMERTERS_VALUES.replace(
            '{}', data_map[param])

        for count in parameters2:
            table_html += EMAIL_TABLE_PARAMERTERS_VALUES.replace(
                '{}', data_dict[param][count])

        table_html += EMAIL_TABLE_PARAMERTERS_TR_END

    return table_html


def generate_mail(mail_html, email, message_subject, display_date):

    import smtplib
    from django.conf import settings
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    body = """
        """ + EMAIL_HEAD + EMAIL_BODY_START + EMAIL_OUTER_TABLE_START + EMAIL_COMPANY_LOGO + EMAIL_ANALYTICS_START.replace('()', display_date) + mail_html + EMAIL_FOOTER + EMAIL_OUTER_TABLE_END + EMAIL_BODY_END + """
    """

    send_email_to_customer_via_awsses(email, message_subject, body)


"""
send_mail : Send mail to the given email id.
"""


def send_mail(FROM, TO, message_as_string, PASSWORD):
    import smtplib
    # # The actual sending of the e-mail
    server = smtplib.SMTP('smtp.gmail.com:587')
    # Credentials (if needed) for sending the mail
    password = PASSWORD
    # Start tls handshaking
    server.starttls()
    # Login to server
    server.login(FROM, password)
    # Send mail
    server.sendmail(FROM, TO, message_as_string)
    # Close session
    server.quit()


def get_performance_report_path(start_date, end_date, user_obj, user_obj_list):

    try:
        message_history_objs = LiveChatSessionManagement.objects.filter(
            user__in=user_obj_list, session_starts_at__date__range=[start_date, end_date]).order_by('-session_starts_at')

        test_wb = Workbook(encoding="UTF-8")

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
        for message in message_history_objs:
            sheet1.write(row, 0, message.get_name())
            sheet1.write(row, 1, str((message.session_starts_at.astimezone(
                pytz.timezone(settings.TIME_ZONE))).strftime("%d/%m/%Y, %I:%M:%p")))
            if message.session_completed:
                sheet1.write(row, 2, str((message.session_ends_at.astimezone(
                    pytz.timezone(settings.TIME_ZONE))).strftime("%d/%m/%Y, %I:%M:%p")))
            else:
                sheet1.write(row, 2, '-')
            sheet1.write(
                row, 3, message.get_session_duration())
            sheet1.write(
                row, 4, message.get_average_handle_time())
            sheet1.write(
                row, 5, message.get_average_first_time_response_time())
            sheet1.write(row, 6, message.get_no_response_count())
            sheet1.write(row, 7, message.get_idle_duration())
            sheet1.write(row, 8, message.get_not_ready_count())
            sheet1.write(
                row, 9, message.get_session_stop_interaction_duration())
            sheet1.write(
                row, 10, message.get_interaction_count())
            sheet1.write(
                row, 11, message.get_interaction_duration())
            sheet1.write(row, 12, message.get_self_assigned_chat())
            sheet1.write(
                row, 13, message.get_total_transferred_chat_received())
            sheet1.write(
                row, 14, message.get_total_transferred_chat_made())
            sheet1.write(row, 15, message.get_total_group_chat_request())
            sheet1.write(row, 16, message.get_total_group_chat_accept())
            sheet1.write(row, 17, message.get_total_group_chat_reject())
            sheet1.write(
                row, 18, message.get_total_group_chat_no_response())
            sheet1.write(row, 19, message.get_total_group_chat_duration())
            sheet1.write(row, 20, message.get_average_nps())
            row += 1

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_performance_report_path: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    if not os.path.exists(settings.SECURE_MEDIA_ROOT + EMAIL_EXCEL_PATH):
        os.mkdir(settings.SECURE_MEDIA_ROOT + EMAIL_EXCEL_PATH)

    file_name = "LiveChatApp/email-excels/PerformanceReport_" + \
        str(user_obj.user.username) + "_" + \
        str(start_date) + "TO" + str(end_date) + ".xls"

    test_wb.save(settings.SECURE_MEDIA_ROOT + file_name)

    file_url = get_livechat_secure_file_path(LiveChatFileAccessManagement, SECURED_FILES_PATH + file_name, False, True, 'MailerReport')

    return file_url


def get_analytical_report_path(start_date, end_date, admin_obj, user_obj_list):

    try:

        test_wb = Workbook(encoding="UTF-8")

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Agent Name")
        sheet1.write(0, 1, "Total Chats Raised")
        sheet1.write(0, 2, "Total Chat Resolved")
        sheet1.write(0, 3, "Total Declined chats")
        sheet1.write(0, 4, "Offline chats")
        sheet1.write(0, 5, "Abandoned Chats")
        sheet1.write(0, 6, "Interactions per chat")
        sheet1.write(0, 7, "Average Handle time")

        row = 1
        for user_obj in user_obj_list:
            livechat_cust_objs = LiveChatCustomer.objects.filter(
                request_raised_date__gte=start_date, request_raised_date__lte=end_date, agent_id=user_obj)

            bot_objs = user_obj.bots.all()

            chats_resolved_count = livechat_cust_objs.filter(
                is_session_exp=True).count()

            declined_chats_count = LiveChatCustomer.objects.filter(
                request_raised_date__gte=start_date, request_raised_date__lte=end_date, agent_id=None, abruptly_closed=True, bot__in=bot_objs).count()

            abandoned_chats_count = LiveChatCustomer.objects.filter(
                request_raised_date__gte=start_date, request_raised_date__lte=end_date, is_system_denied=True, bot__in=bot_objs).count()

            offline_chats_count = LiveChatCustomer.objects.filter(bot__in=bot_objs,
                                                                  request_raised_date__gte=start_date, request_raised_date__lte=end_date, is_denied=True, is_system_denied=False).count()

            chats_raised_count = livechat_cust_objs.count() + offline_chats_count + \
                abandoned_chats_count + declined_chats_count

            total_handle = livechat_cust_objs.aggregate(Sum('chat_duration'))[
                'chat_duration__sum']
            average_handle_time = get_average(
                total_handle, livechat_cust_objs.count())

            total_interactions = LiveChatMISDashboard.objects.filter(
                livechat_customer__in=livechat_cust_objs).count()
            average_interactions = get_average(
                total_interactions, livechat_cust_objs.count())

            sheet1.write(row, 0, user_obj.user.username)
            sheet1.write(row, 1, chats_raised_count)
            sheet1.write(row, 2, chats_resolved_count)
            sheet1.write(row, 3, declined_chats_count)
            sheet1.write(row, 4, offline_chats_count)
            sheet1.write(row, 5, abandoned_chats_count)
            sheet1.write(row, 6, average_interactions)
            sheet1.write(row, 7, average_handle_time // 60)
            row += 1

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_analytical_report_path: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    if not os.path.exists(settings.SECURE_MEDIA_ROOT + EMAIL_EXCEL_PATH):
        os.mkdir(settings.SECURE_MEDIA_ROOT + EMAIL_EXCEL_PATH)

    file_name = "LiveChatApp/email-excels/AnalyticalReport_" + \
        str(admin_obj.user.username) + "_" + \
        str(start_date) + "TO" + str(end_date) + ".xls"

    test_wb.save(settings.SECURE_MEDIA_ROOT + file_name)

    file_url = get_livechat_secure_file_path(LiveChatFileAccessManagement, SECURED_FILES_PATH + file_name, False, True, 'MailerReport')

    return file_url


def get_mailer_report_path(start_date, end_date, admin_obj, user_obj_list, email_profile_obj, is_sample_mail=False):

    try:
        count_variation = json.loads(
            email_profile_obj.table_parameters.count_variation)
        channel_list = json.loads(
            email_profile_obj.table_parameters.channel)
        table_records = json.loads(
            email_profile_obj.table_parameters.table_records)

        if len(table_records) > 0:

            test_wb = Workbook(encoding="UTF-8")

            sheet1 = test_wb.add_sheet("Sheet1")
            style = xlwt.XFStyle()

            # font
            font = xlwt.Font()
            font.bold = True
            style.font = font

            sheet1.write(0, 0, "Record Parameters", style=style)
            row = 2
            if len(count_variation) > 0:
                sheet1.write(row, 0, "Count", style=style)
                col = 1
                for count in count_variation:
                    if count == '1':
                        count_header = 'Daily'
                    if count == '2':
                        count_header = 'WTD'
                    if count == '3':
                        count_header = 'MTD'
                    if count == '4':
                        count_header = 'YTD'
                    if count == '5':
                        count_header = 'LMSD'
                    sheet1.write(row, col, count_header, style=style)
                    col = col + 1

                if is_sample_mail:
                    date_wise_table_records_data = TABLE_COUNT_RECORD_DATA
                else:
                    date_wise_table_records_data = get_date_wise_table_records_data(
                        count_variation, table_records, user_obj_list)

                row = row + 1
                for table_record in table_records:
                    sheet1.write(row, 0, TABLE_RECORD_HEADERS[table_record])

                    col = 1
                    for count in count_variation:
                        sheet1.write(row, col, date_wise_table_records_data[table_record][count])
                        col = col + 1

                    row = row + 1

                row = row + 1

            if len(channel_list) > 0:
                sheet1.write(row, 0, "Channel", style=style)
                col = 1
                for channel in channel_list:
                    sheet1.write(row, col, channel, style=style)
                    col = col + 1

                if is_sample_mail:
                    channel_wise_table_records_data = TABLE_CHANNEL_RECORD_DATA
                else:
                    channel_wise_table_records_data = get_channel_wise_table_records_data(
                        start_date, end_date, channel_list, table_records, user_obj_list)

                row = row + 1
                for table_record in table_records:
                    sheet1.write(row, 0, TABLE_RECORD_HEADERS[table_record])

                    col = 1
                    for channel in channel_list:
                        sheet1.write(row, col, channel_wise_table_records_data[table_record][channel])
                        col = col + 1

                    row = row + 1          

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_mailer_report_path: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    if not os.path.exists(settings.SECURE_MEDIA_ROOT + EMAIL_EXCEL_PATH):
        os.mkdir(settings.SECURE_MEDIA_ROOT + EMAIL_EXCEL_PATH)

    file_name = "LiveChatApp/email-excels/MailSummary_" + \
        str(admin_obj.user.username) + "_" + \
        str(start_date) + "TO" + str(end_date) + ".xls"

    test_wb.save(settings.SECURE_MEDIA_ROOT + file_name)

    file_url = get_livechat_secure_file_path(LiveChatFileAccessManagement, SECURED_FILES_PATH + file_name, False, True, 'MailerReport')

    return file_url


def get_customer_report_path(start_date, end_date, admin_obj, user_obj_list):
    try:
        import pytz
        tz = pytz.timezone(settings.TIME_ZONE)

        test_wb = Workbook(encoding="UTF-8")

        sheet1 = test_wb.add_sheet("Sheet1")

        style = xlwt.XFStyle()
        # font
        font = xlwt.Font()
        font.bold = True
        style.font = font

        # For handling single cell Multi-line
        algn1 = xlwt.Alignment()
        algn1.wrap = 1
        style1 = xlwt.XFStyle()
        style1.alignment = algn1

        sheet1.write(0, 0, "S. No.", style=style)
        sheet1.write(0, 1, "Session ID", style=style)
        sheet1.write(0, 2, "Email ID", style=style)
        sheet1.write(0, 3, "Client/User ID", style=style)
        sheet1.write(0, 4, "Phone No.", style=style)
        sheet1.write(0, 5, "Name", style=style)
        sheet1.write(0, 6, "Chat initiated on", style=style)
        sheet1.write(0, 7, "Categories assigned", style=style)
        sheet1.write(0, 8, "Chat re-initiated on", style=style)
        sheet1.write(0, 9, "Agent Name", style=style)
        sheet1.write(0, 10, "Wait Time (s)", style=style)
        sheet1.write(0, 11, "Last Response Time", style=style)
        sheet1.write(0, 12, "Interaction End Time", style=style)
        sheet1.write(0, 13, "Interaction Duration", style=style)
        sheet1.write(0, 14, "Agent resolved", style=style)
        sheet1.write(0, 15, "Resolution Category", style=style)
        sheet1.write(0, 16, "Chat NPS Score", style=style)
        sheet1.write(0, 17, "Chat NPS Score Feedback Time", style=style)
        sheet1.write(0, 18, "Chat NPS Feedback Comment", style=style)
        sheet1.write(0, 19, "User Response Count", style=style)
        sheet1.write(0, 20, "Average Response Time", style=style)
        sheet1.write(0, 21, "Cobrowsing NPS", style=style)
        sheet1.write(0, 22, "Cobrowsing NPS Comment", style=style)

        customer_chat_initiated_objs = LiveChatCustomer.objects.filter(request_raised_date__gte=start_date, request_raised_date__lte=end_date, agent_id__in=user_obj_list, is_session_exp=True).values('session_id', 'client_id', 'joined_date').order_by('joined_date')

        customer_chat_initiated_dict = {}
        for customer_chat_initiated_obj in customer_chat_initiated_objs:
            if customer_chat_initiated_obj["client_id"] not in customer_chat_initiated_dict.keys():
                customer_chat_initiated_dict[customer_chat_initiated_obj["client_id"]] = {"chat_initiated": customer_chat_initiated_obj["joined_date"]}
            customer_joined_date_info = customer_chat_initiated_dict[customer_chat_initiated_obj["client_id"]]
            customer_joined_date_info[str(customer_chat_initiated_obj["session_id"])] = customer_chat_initiated_obj["joined_date"]

        customer_objs = LiveChatCustomer.objects.filter(request_raised_date__gte=start_date, request_raised_date__lte=end_date, agent_id__in=user_obj_list, is_session_exp=True).order_by('joined_date')

        row = 1
        for customer_obj in customer_objs:

            sheet1.write(row, 0, row)
            sheet1.write(row, 1, str(customer_obj.session_id))
            sheet1.write(row, 2, customer_obj.email)
            sheet1.write(row, 3, customer_obj.client_id)
            sheet1.write(row, 4, customer_obj.phone)
            sheet1.write(row, 5, customer_obj.username)
            sheet1.write(row, 6, customer_chat_initiated_dict[customer_obj.client_id]["chat_initiated"].astimezone(tz).strftime("%d/%m/%Y %H:%M"))

            category_title = "-"
            if customer_obj.category:
                category_title = customer_obj.category.title
            sheet1.write(row, 7, category_title)

            chat_re_initiated_on = customer_chat_initiated_dict[customer_obj.client_id][str(customer_obj.session_id)].astimezone(tz).strftime("%d/%m/%Y %H:%M")
            if customer_obj.joined_date == customer_chat_initiated_dict[customer_obj.client_id]["chat_initiated"]:
                chat_re_initiated_on = "-"
            sheet1.write(row, 8, chat_re_initiated_on)

            agents_involved = ""
            livechat_agent_objs = customer_obj.agents_group.all()
            for livechat_agent_obj in livechat_agent_objs:
                agents_involved = agents_involved + livechat_agent_obj.get_agent_name() + ", "
            sheet1.write(row, 9, agents_involved[:-2])

            sheet1.write(row, 10, customer_obj.queue_time)

            last_response_time = customer_obj.last_appearance_date.astimezone(tz).strftime("%d/%m/%Y %H:%M")
            last_customer_message = LiveChatMISDashboard.objects.filter(livechat_customer=customer_obj, sender="Customer").order_by('-message_time')
            if last_customer_message.exists():
                last_response_time = last_customer_message[0].message_time.astimezone(tz).strftime("%d/%m/%Y %H:%M")
            sheet1.write(row, 11, last_response_time)

            sheet1.write(row, 12, customer_obj.last_appearance_date.astimezone(tz).strftime("%d/%m/%Y %H:%M"))
            sheet1.write(row, 13, customer_obj.get_chat_duration())
            sheet1.write(row, 14, customer_obj.agent_id.get_agent_name())
            sheet1.write(row, 15, customer_obj.get_closing_category_title())

            nps_score = customer_obj.rate_value
            nps_feedback_date = customer_obj.nps_feedback_date.astimezone(tz).strftime("%d/%m/%Y %H:%M")
            if nps_score == -1:
                nps_score = "-"
                nps_feedback_date = "-"
            sheet1.write(row, 16, nps_score)
            sheet1.write(row, 17, nps_feedback_date)

            nps_comment = customer_obj.nps_text_feedback
            if nps_comment.strip() == "":
                nps_comment = "-"
            sheet1.write(row, 18, nps_comment)

            user_response_count = LiveChatMISDashboard.objects.filter(livechat_customer=customer_obj, sender="Customer").count()
            sheet1.write(row, 19, user_response_count)

            avg_response_time = 0
            if user_response_count:
                avg_response_time = int(customer_obj.chat_duration / user_response_count)
            sheet1.write(row, 20, avg_response_time)

            cobrowsing_nps_rating, cobrowsing_nps_comment = customer_obj.get_cobrowsing_nps_data()
            sheet1.write(row, 21, cobrowsing_nps_rating, style1)
            sheet1.write(row, 22, cobrowsing_nps_comment, style1)

            row += 1

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_customer_report_path: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    if not os.path.exists(settings.SECURE_MEDIA_ROOT + EMAIL_EXCEL_PATH):
        os.mkdir(settings.SECURE_MEDIA_ROOT + EMAIL_EXCEL_PATH)

    file_name = "LiveChatApp/email-excels/CustomerReport_" + \
        str(admin_obj.user.username) + "_" + \
        str(start_date) + "TO" + str(end_date) + ".xls"

    test_wb.save(settings.SECURE_MEDIA_ROOT + file_name)

    file_url = get_livechat_secure_file_path(LiveChatFileAccessManagement, SECURED_FILES_PATH + file_name, False, True, 'MailerReport')

    return file_url    
