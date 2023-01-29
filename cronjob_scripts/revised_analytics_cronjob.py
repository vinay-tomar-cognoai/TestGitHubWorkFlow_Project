import os
import sys
import json
import time
import re

from xlsxwriter import Workbook
from EasyChatApp.models import User, Bot, MISDashboard, AnalyticsExportRequest, UserSessionHealth
from EasyChatApp.utils import logger
from zipfile import ZipFile
from datetime import datetime, timedelta
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses

from os import path
from os.path import basename

from EasyChatApp.utils_analytics import return_mis_objects_excluding_blocked_sessions
from EasyChatApp.utils_api_analytics import get_combined_catalogue_analytics_list
from EasyChatApp.utils_execute_query import check_and_send_broken_bot_mail


def send_mail(from_email_id, to_emai_id, message_as_string, from_email_id_password):
    import smtplib
    # The actual sending of the e-mail
    server = smtplib.SMTP('smtp.gmail.com:587')
    # Credentials (if needed) for sending the mail
    password = from_email_id_password
    # Start tls handshaking
    server.starttls()
    # Login to server
    server.login(from_email_id, password)
    # Send mail
    server.sendmail(from_email_id, to_emai_id, message_as_string)
    # Close session
    server.quit()


def message_analytics(last_date, bot_obj):
    try:
        message_analytics_list = []
        from EasyChatApp.models import MessageAnalyticsDaily
        from django.db.models import Sum

        bot_objs = [bot_obj]
        date_filtered_mis_objects = MessageAnalyticsDaily.objects.filter(
            bot__in=bot_objs, date_message_analytics=last_date)

        total_messages = date_filtered_mis_objects.aggregate(
            Sum('total_messages_count'))['total_messages_count__sum']
        if total_messages == None:
            total_messages = 0

        total_answered_messages = date_filtered_mis_objects.aggregate(
            Sum('answered_query_count'))['answered_query_count__sum']
        if total_answered_messages == None:
            total_answered_messages = 0
        total_unanswered_messages = date_filtered_mis_objects.aggregate(
            Sum('unanswered_query_count'))['unanswered_query_count__sum']
        if total_unanswered_messages == None:
            total_unanswered_messages = 0
        total_intuitive_messages = date_filtered_mis_objects.aggregate(
            Sum('intuitive_query_count'))['intuitive_query_count__sum']
        if total_intuitive_messages == None:
            total_intuitive_messages = 0
        message_analytics_list.append({
            "label": str(last_date.strftime("%d-%b-%y")),
            "total_messages": total_messages,
            "total_answered_messages": total_answered_messages,
            "total_unanswered_messages": total_unanswered_messages,
            "total_intuitive_messages": total_intuitive_messages,
            "predicted_messages_no": total_messages
        })
        return message_analytics_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return message_analytics_list


def user_analytics(last_date, bot_obj):
    try:
        from EasyChatApp.models import UniqueUsers
        from django.db.models import Sum, Q
        from pytz import timezone

        datetime_start = last_date
        bot_objs = [bot_obj]
        date_filtered_mis_objects = UniqueUsers.objects.filter(
            bot__in=bot_objs, date=datetime_start)

        user_analytics_list = []
        count = date_filtered_mis_objects.aggregate(Sum('count'))['count__sum']

        if count == None:
            count = 0

        user_analytics_list.append({
            "label": str(last_date.strftime("%d-%b-%y")),
            "count": count,
        })
        return user_analytics_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return user_analytics_list


def device_specific_analytics(last_date, bot_obj):
    try:
        device_specific_analytics_list = []
        from EasyChatApp.models import MessageAnalyticsDaily, UniqueUsers
        from django.db.models import Sum

        bot_objs = [bot_obj]
        date_filtered_mis_objects = MessageAnalyticsDaily.objects.filter(
            bot__in=bot_objs, date_message_analytics=last_date)

        date_filtered_mis_objects_users = UniqueUsers.objects.filter(
            bot__in=bot_objs, date=last_date)

        total_messages = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('total_messages_count'))['total_messages_count__sum'])

        total_answered_messages = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('answered_query_count'))['answered_query_count__sum'])

        total_unanswered_messages = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('unanswered_query_count'))['unanswered_query_count__sum'])

        total_messages_mobile = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('total_message_count_mobile'))['total_message_count_mobile__sum'])

        total_answered_messages_mobile = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('answered_query_count_mobile'))['answered_query_count_mobile__sum'])

        total_unanswered_messages_mobile = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('unanswered_query_count_mobile'))['unanswered_query_count_mobile__sum'])

        total_intuitive_messages = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('intuitive_query_count'))['intuitive_query_count__sum'])

        total_intuitive_messages_mobile = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('intuitive_query_count_mobile'))['intuitive_query_count_mobile__sum'])
        total_intuitive_messages_desktop = total_intuitive_messages - total_intuitive_messages_mobile

        total_messages_desktop = total_messages - total_messages_mobile

        total_unanswered_messages_desktop = total_unanswered_messages - \
            total_unanswered_messages_mobile

        total_answered_messages_desktop = total_answered_messages - \
            total_answered_messages_mobile

        total_users_count = return_zero_if_number_is_none(date_filtered_mis_objects_users.aggregate(
            Sum('count'))['count__sum'])
        total_users_mobile = return_zero_if_number_is_none(date_filtered_mis_objects_users.aggregate(
            Sum('users_count_mobile'))['users_count_mobile__sum'])
        total_users_desktop = total_users_count - total_users_mobile

        device_specific_analytics_list.append({
            "label": str(last_date.strftime("%d-%b-%y")),
            "total_messages_mobile": total_messages_mobile,
            "total_answered_messages_mobile": total_answered_messages_mobile,
            "total_unanswered_messages_mobile": total_unanswered_messages_mobile,
            "total_messages_desktop": total_messages_desktop,
            "total_answered_messages_desktop": total_answered_messages_desktop,
            "total_unanswered_messages_desktop": total_unanswered_messages_desktop,
            "total_users_mobile": total_users_mobile,
            "total_users_desktop": total_users_desktop,
            "total_intuitive_messages_mobile": total_intuitive_messages_mobile,
            "total_intuitive_messages_desktop": total_intuitive_messages_desktop,

        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_device_specific_analytics_list: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return device_specific_analytics_list


def frequent_intents(last_date, bot_objs):
    try:
        import math
        from pytz import timezone
        from django.db.models import Sum, Q, Count
        mis_objects = MISDashboard.objects.filter(
            bot__in=[bot_objs], small_talk_intent=False, date__date=last_date)
        mis_objects = return_mis_objects_excluding_blocked_sessions(
            mis_objects, UserSessionHealth)
        intent_frequency = list(mis_objects.filter(~Q(intent_name=None)).values(
            "intent_name").order_by("intent_name").annotate(frequency=Count("intent_name")).order_by('-frequency').exclude(intent_name="INFLOW-INTENT"))
        return intent_frequency
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return intent_frequency


def category_based_intents(last_date, bot_objs):
    try:
        import math
        from pytz import timezone
        from django.db.models import Sum, Q, Count
        mis_objects = MISDashboard.objects.filter(
            bot__in=[bot_objs], small_talk_intent=False, date__date=last_date)
        mis_objects = return_mis_objects_excluding_blocked_sessions(
            mis_objects, UserSessionHealth)
        intent_frequency = list(mis_objects.filter(~Q(intent_name=None)).values(
            "intent_name", "category__name").order_by("intent_name").annotate(frequency=Count("intent_name")).order_by('-frequency').exclude(intent_name="INFLOW-INTENT"))
        return intent_frequency
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return intent_frequency


def unanswered_query_excel(last_date, bot_objs):
    try:
        from EasyChatApp.models import UnAnsweredQueries
        import math
        from pytz import timezone
        from django.db.models import Sum, Q, Count
        unanswered_queries = UnAnsweredQueries.objects.filter(
            bot=bot_objs, date__gte=last_date, date__lte=last_date).exclude(unanswered_message="")
        
        return unanswered_queries.values_list("unanswered_message").annotate(total=Sum("count")).order_by("-total")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return {}


def intuitive_query_excel(last_date, bot_objs):
    try:
        from EasyChatApp.models import IntuitiveQuestions
        import math
        from pytz import timezone
        from django.db.models import Sum, Q, Count
        intuitive_queries = IntuitiveQuestions.objects.filter(
            bot=bot_objs, date__gte=last_date, date__lte=last_date).order_by('-date')
        return intuitive_queries

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return {}


def user_nudge_analytics(last_date, bot_obj):
    try:
        from EasyChatApp.models import AutoPopUpClickInfo

        bubble_click_count_objs = AutoPopUpClickInfo.objects.filter(
            bot=bot_obj, date=last_date)
        distinct_bubble_click_objs = bubble_click_count_objs.exclude(
            name="Greeting bubble").order_by("-pk").values("name").distinct()
        user_nudge_analytics_data = []
        auto_popup_type = bot_obj.auto_popup_type
        auto_popup_initial_messages = []
        if str(auto_popup_type) == "3":
            auto_popup_initial_messages = json.loads(
                bot_obj.auto_popup_initial_messages)

        user_nudge_analytics_data = [{
            "name": "Greeting bubble",
            "count": bubble_click_count_objs.filter(name="Greeting bubble").count(),
            "is_active": str(auto_popup_type) in ["2", "3"]
        }]

        for distinct_bubble_click_obj in distinct_bubble_click_objs:
            user_nudge_analytics_data.append({
                "name": distinct_bubble_click_obj["name"],
                "count": bubble_click_count_objs.filter(name=distinct_bubble_click_obj["name"]).count(),
                "is_active": distinct_bubble_click_obj["name"] in auto_popup_initial_messages
            })

        return user_nudge_analytics_data
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return user_nudge_analytics_data


def merger_excelfiles_within_dir(directory_list, list_of_sheets, d_name):
    from EasyChatApp.utils import logger
    import sys
    import os
    import pandas as pd
    merged_filename = None
    try:
        files = directory_list

        df = pd.DataFrame()

        xl_count = 1
        list_of_dataframes = []

        for sheet in list_of_sheets:
            df = pd.DataFrame()
            for file in files:
                if (file.endswith('.xlsx') or file.endswith('.xls')) and "Merged_" not in file:
                    # for older files it is possible that newly added worksheets might not be there
                    try:
                        df = df.append(pd.read_excel(
                            file, sheet_name=sheet), ignore_index=True)
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.warning("merger_excelfiles_within_dir! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    xl_count += 1
            list_of_dataframes.append(df)

        directory_name = files[0].replace(files[0].split("/")[-1], "")

        merged_filename = directory_name + d_name + ".xlsx"

        writer = pd.ExcelWriter(merged_filename, engine='xlsxwriter')

        for itreator in range(0, len(list_of_sheets)):
            df = list_of_dataframes[itreator]
            df.to_excel(
                writer, sheet_name=list_of_sheets[itreator], index=False)

        writer.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()

        logger.error("merger_excelfiles_within_dir! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return merged_filename


def hour_wise_analytics(last_date, bot_obj):
    try:
        from django.db.models import Count
        from django.db.models.functions import ExtractHour
        time_gap = 1  # default value of time interval in hour
        interval_type = '1'
        category_name = "All"
        mis_objects = MISDashboard.objects.filter(
            creation_date__gte=last_date, creation_date__lte=last_date, bot=bot_obj)
        mis_objects = return_mis_objects_excluding_blocked_sessions(
            mis_objects, UserSessionHealth)

        hour_wise_message_count, hour_wise_users_count = [
            0 for i in range(24)], [0 for i in range(24)]
        hour_wise_analytics_list = []
        hour_wise_analytics_list.append(
            {'total_message_count': hour_wise_message_count, 'total_users_count': hour_wise_users_count})

        total_users_queryset = mis_objects.annotate(hour=ExtractHour(
            'date')).values('hour').annotate(total_users=Count('user_id', distinct=True)).order_by('hour')

        if category_name.lower() != 'all':
            total_messages_queryset = mis_objects.filter(category_name=category_name).annotate(hour=ExtractHour(
                'date')).values('hour').annotate(total_msg=Count('id')).order_by('hour')
        else:
            total_messages_queryset = mis_objects.annotate(hour=ExtractHour(
                'date')).values('hour').annotate(total_msg=Count('id')).order_by('hour')

        for hour_data in total_messages_queryset:
            hour_wise_message_count[hour_data['hour']
                                    ] = hour_data['total_msg']

        for hour_data in total_users_queryset:
            hour_wise_users_count[hour_data['hour']
                                  ] = hour_data['total_users']

        if interval_type == "1":
            hour_wise_analytics_list[0]["total_message_count"] = hour_wise_message_count
            hour_wise_analytics_list[0]["total_users_count"] = hour_wise_users_count
        else:
            if interval_type == "2":
                time_gap = 3
            else:
                time_gap = 6

            hour_wise_message_count_with_gap = []
            hour_wise_users_count_with_gap = []

            for hour_value in range(0, 25 - time_gap, time_gap):
                hour_wise_message_count_with_gap.append(
                    sum(hour_wise_message_count[hour_value:hour_value + time_gap]))
                hour_wise_users_count_with_gap.append(
                    sum(hour_wise_users_count[hour_value:hour_value + time_gap]))

            hour_wise_analytics_list[0]["total_message_count"] = hour_wise_message_count_with_gap
            hour_wise_analytics_list[0]["total_users_count"] = hour_wise_users_count_with_gap

        return hour_wise_analytics_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("hour wise analytics! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return hour_wise_analytics_list
        

def whatsapp_catalogue_analytics(sheet_obj, last_date, bot_obj):
    try:
        sheet_obj.write(0, 0, "Date")
        sheet_obj.write(0, 1, "Purchased Users")
        sheet_obj.write(0, 2, "Cart Users")
        sheet_obj.write(0, 3, "Conversion Ratio")

        catalogue_analytics_list, _ = get_combined_catalogue_analytics_list(
            last_date, last_date, bot_obj, "1")
        sheet_row = 1
        for catalogue_analytics in catalogue_analytics_list:
            catalogue_analytics["total_conversion_ratio"] = str(
                catalogue_analytics["total_conversion_ratio"]) + "%"
            sheet_obj.write(sheet_row, 0, catalogue_analytics["label"])
            sheet_obj.write(
                sheet_row, 1, catalogue_analytics["total_purchased_carts"])
            sheet_obj.write(sheet_row, 2, catalogue_analytics["total_carts"])
            sheet_obj.write(
                sheet_row, 3, catalogue_analytics["total_conversion_ratio"])
            sheet_row += 1

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("whatsapp_catalogue_analytics! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return sheet_obj


def cronjob():
    try:
        import sys
        from pytz import timezone
        ist = timezone('Asia/Kolkata')
        message_history_datadump_log = open(
            "log/message_history_dump.log", "a")

        today = datetime.now()
        domain = settings.EASYCHAT_HOST_URL

        try:
            total_x_days = 31

            if not os.path.exists(settings.MEDIA_ROOT + 'analytics-download-excel'):
                os.makedirs(settings.MEDIA_ROOT + 'analytics-download-excel')

            for bot_obj in Bot.objects.filter(is_deleted=False):

                # Check whether directory for given bot id exists or not: If not create
                # one
                if not os.path.exists(settings.MEDIA_ROOT + 'analytics-download-excel/bot-' + str(bot_obj.pk)):
                    os.makedirs(settings.MEDIA_ROOT +
                                'analytics-download-excel/bot-' + str(bot_obj.pk))

                for last_x_day in range(1, total_x_days + 2):

                    if last_x_day == total_x_days + 1:
                        day_x = today - timedelta(last_x_day)
                        cmd = "rm" + settings.MEDIA_ROOT + "analytics-download-excel/bot-" + \
                            str(bot_obj.pk) + "/analytics_excel_consolidated_" + \
                            str(day_x.date())
                        os.system(cmd)
                        break

                    last_date = today - timedelta(last_x_day)

                    file_already_exists = False
                    if path.exists(settings.MEDIA_ROOT + "analytics-download-excel/bot-" + str(bot_obj.pk) + "/analytics_excel_consolidated_" + str(last_date.date()) + ".xls"):
                        file_already_exists = True

                    if not file_already_exists:
                        test_wb = Workbook(settings.MEDIA_ROOT + "analytics-download-excel/bot-" + str(bot_obj.pk) + "/analytics_excel_consolidated_" +
                                           str(last_date.date()) + '.xls')

                        sheet1 = test_wb.add_worksheet("Message Analytics")
                        global message_analytics
                        message_analytics_list = message_analytics(
                            last_date, bot_obj)
                        sheet1.write(0, 0, "Date")
                        sheet1.write(0, 1, "Total Messages")
                        sheet1.write(0, 2, "Total Answered Messages")
                        sheet1.write(0, 3, "Total Intuitive Messages")
                        sheet1.write(0, 4, "Total UnAnswered Messages")

                        row = 1
                        for message in message_analytics_list:
                            sheet1.write(row, 0, message["label"])
                            sheet1.write(row, 1, message["total_messages"])
                            sheet1.write(row, 2, message[
                                         "total_answered_messages"])
                            sheet1.write(row, 3, message["total_intuitive_messages"])             
                            sheet1.write(row, 4, message[
                                         "total_unanswered_messages"])
                            row += 1

                        sheet2 = test_wb.add_worksheet("User Analytics")
                        global user_analytics
                        user_analytics_list = user_analytics(
                            last_date, bot_obj)
                        sheet2.write(0, 0, "Date")
                        sheet2.write(0, 1, "Count")
                        row = 1
                        for message in user_analytics_list:
                            sheet2.write(row, 0, message["label"])
                            sheet2.write(row, 1, message["count"])
                            row += 1

                        global frequent_intents
                        frequent_intents_list = frequent_intents(
                            last_date, bot_obj)
                        sheet3 = test_wb.add_worksheet(
                            "Frequent Intent Analytics")
                        sheet3.write(0, 0, "Date")
                        sheet3.write(0, 1, "Intent Name")
                        sheet3.write(0, 2, "Frequency")
                        row = 1
                        for message in frequent_intents_list:
                            sheet3.write(row, 0, str(
                                last_date.strftime("%d-%b-%y")))
                            sheet3.write(row, 1, str(message["intent_name"]))
                            sheet3.write(row, 2, message["frequency"])
                            row += 1

                        global category_based_intents
                        category_based_intents_list = category_based_intents(
                            last_date, bot_obj)
                        sheet4 = test_wb.add_worksheet("Category Analytics")
                        sheet4.write(0, 0, "Date")
                        sheet4.write(0, 1, "Intent Name")
                        sheet4.write(0, 2, "Frequency")
                        sheet4.write(0, 3, "Category Name")
                        row = 1
                        for message in category_based_intents_list:
                            sheet4.write(row, 0, str(
                                last_date.strftime("%d-%b-%y")))
                            sheet4.write(row, 1, str(message["intent_name"]))
                            sheet4.write(row, 2, message["frequency"])
                            sheet4.write(row, 3, message["category__name"])
                            row += 1

                        global unanswered_query_excel
                        unanswered_query_excel_list = unanswered_query_excel(
                            last_date, bot_obj)
                        sheet5 = test_wb.add_worksheet("Unanswered Query")
                        sheet5.write(0, 0, "Date")
                        sheet5.write(0, 1, "Unanswered Query")
                        sheet5.write(0, 2, "Frequency")
                        row = 1
                        for key, value in unanswered_query_excel_list:
                            sheet5.write(row, 0, str(
                                last_date.strftime("%d-%b-%y")))
                            sheet5.write(row, 1, key)
                            sheet5.write(row, 2, value)
                            row += 1

                        global intuitive_query_excel
                        intuitive_queries = intuitive_query_excel(
                            last_date, bot_obj)
                        sheet6 = test_wb.add_worksheet("Intuitive Queries")
                        sheet6.write(0, 0, "Date")
                        sheet6.write(0, 1, "User Query")
                        sheet6.write(0, 2, "Frequency")
                        sheet6.write(0, 3, "Intuitive Queries")
                        sheet6.write(0, 4, "Channel Name")
                        row = 1
                        for intuitive_query in intuitive_queries.iterator():
                            string_intents = ""
                            for intent in intuitive_query.suggested_intents.all():
                                string_intents = string_intents + intent.name + ", "
                            string_intents = string_intents.strip()
                            length = len(string_intents) - 1
                            string_intents = string_intents[0:length]
                            sheet6.write(
                                row, 0, intuitive_query.date.strftime(("%d-%m-%Y")))
                            sheet6.write(
                                row, 1, intuitive_query.intuitive_message_query)
                            sheet6.write(row, 2, intuitive_query.count)
                            sheet6.write(row, 3, string_intents)
                            sheet6.write(row, 4, intuitive_query.channel)
                            row += 1

                        global user_nudge_analytics
                        user_nudge_analytics_data = user_nudge_analytics(
                            last_date, bot_obj)
                        sheet7 = test_wb.add_worksheet("User Nudge Analytics")
                        sheet7.write(0, 0, "Greeting/Intent bubble name")
                        sheet7.write(0, 1, "Click Count")
                        sheet7.write(0, 2, "Active/Inactive")

                        row = 1
                        for nudge_data in user_nudge_analytics_data:
                            sheet7.write(row, 0, nudge_data["name"])
                            sheet7.write(row, 1, str(nudge_data["count"]))
                            if nudge_data["is_active"]:
                                sheet7.write(row, 2, "Active")
                            row += 1

                        sheet8 = test_wb.add_worksheet(
                            "Device Specific Analytics")
                        global device_specific_analytics
                        device_specific_analytics_list = device_specific_analytics(
                            last_date, bot_obj)

                        sheet8.write(0, 0, "Date")
                        sheet8.write(0, 1, "Mobile Users")
                        sheet8.write(0, 2, "Desktop Users")
                        sheet8.write(0, 3, "Queries asked(Mobile)")
                        sheet8.write(0, 4, "Queries asked(Desktop)")
                        sheet8.write(0, 5, "Queries answered(Mobile)")
                        sheet8.write(0, 6, "Queries answered(Desktop)")
                        sheet8.write(0, 7, "Queries Intuitive (Mobile)")
                        sheet8.write(0, 8, "Queries Intuitive (Desktop)")
                        sheet8.write(0, 9, "Queries unanswered (Mobile)")
                        sheet8.write(0, 10, "Queries unanswered (Desktop)")

                        row = 1
                        for device_data in device_specific_analytics_list:
                            sheet8.write(row, 0, device_data["label"])
                            sheet8.write(row, 1, str(
                                device_data["total_users_mobile"]))
                            sheet8.write(row, 2, str(
                                device_data["total_users_desktop"]))
                            sheet8.write(row, 3, str(
                                device_data["total_messages_mobile"]))
                            sheet8.write(row, 4, str(
                                device_data["total_messages_desktop"]))
                            sheet8.write(row, 5, str(
                                device_data["total_answered_messages_mobile"]))
                            sheet8.write(row, 6, str(
                                device_data["total_answered_messages_desktop"]))
                            sheet8.write(row, 7, str(
                                device_data["total_intuitive_messages_mobile"]))
                            sheet8.write(row, 8, str(
                                device_data["total_intuitive_messages_desktop"]))
                            sheet8.write(row, 9, str(
                                device_data["total_unanswered_messages_mobile"]))
                            sheet8.write(row, 10, str(
                                device_data["total_unanswered_messages_desktop"]))
                            row += 1

                        sheet9 = test_wb.add_worksheet("Hour wise analytics")
                        global hour_wise_analytics
                        hour_wise_analytics_list = hour_wise_analytics(
                            last_date, bot_obj)
                        sheet9.write(0, 0, "Date")
                        sheet9.write(0, 1, "Time Interval")
                        sheet9.write(0, 2, "No. of users")
                        sheet9.write(0, 3, "No. of messages")
                        row = 1
                        total_number_of_messages = hour_wise_analytics_list[0]["total_message_count"]
                        total_number_of_users = hour_wise_analytics_list[0]["total_users_count"]
                        time_hr = 1
                        for number in range(len(total_number_of_messages)):
                            sheet9.write(
                                row, 0, last_date.strftime("%d-%m-%Y"))
                            sheet9.write(row, 1, str(time_hr - 1) +
                                         "hr" + " - " + str(time_hr) + "hr")
                            sheet9.write(row, 2, total_number_of_users[number])
                            sheet9.write(
                                row, 3, total_number_of_messages[number])
                            row += 1
                            time_hr += 1

                        sheet10 = test_wb.add_worksheet("WhatsApp Catalogue Analytics")
                        sheet10 = whatsapp_catalogue_analytics(sheet10, last_date, bot_obj)

                        test_wb.close()

                # Zip file containing last x days
                try:
                    yesterday = today - timedelta(1)
                    zip_obj = ZipFile(settings.MEDIA_ROOT + "analytics-download-excel/bot-" +
                                      str(bot_obj.pk) + "/AnalyticsExcelOneDay.zip", "w")
                    file_path = "analytics-download-excel/bot-" + \
                        str(bot_obj.pk) + "/analytics_excel_consolidated_" + \
                        str(yesterday.date()) + '.xls'
                    zip_obj.write(settings.MEDIA_ROOT +
                                  file_path, basename(file_path))
                    zip_obj.close()

                    zip_obj = ZipFile(settings.MEDIA_ROOT + "analytics-download-excel/bot-" +
                                      str(bot_obj.pk) + "/AnalyticsExcelLastSevenDay.zip", "w")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Revised Analytics Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass

                last_seven_days = []

                for index in range(1, 8):
                    date = today - timedelta(index)
                    try:
                        file_path = "analytics-download-excel/bot-" + \
                            str(bot_obj.pk) + "/analytics_excel_consolidated_" + \
                            str(date.date()) + '.xls'

                        last_seven_days.append(settings.MEDIA_ROOT + file_path)

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Revised Analytics Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        pass
                list_of_sheets = ["Message Analytics", "User Analytics",
                                  "Frequent Intent Analytics", "Category Analytics", "Unanswered Query", "Intuitive Queries", "User Nudge Analytics", "Device Specific Analytics", "Hour wise analytics", "WhatsApp Catalogue Analytics"]

                merged_file_name = "last_seven_days_from_" + \
                    str((today - timedelta(7)).date()) + \
                    "_to_" + str(today.date())

                merged_file_path = merger_excelfiles_within_dir(
                    last_seven_days, list_of_sheets, merged_file_name)

                zip_obj.write(merged_file_path, basename(merged_file_path))

                zip_obj.close()

                # Zip file containing last 30 days
                zip_obj = ZipFile(settings.MEDIA_ROOT + "analytics-download-excel/bot-" +
                                  str(bot_obj.pk) + "/AnalyticsExcelThirtyDay.zip", "w")
                first_fifteen_days = []
                for index in range(1, 16):
                    date = today - timedelta(index)
                    try:
                        file_path = "analytics-download-excel/bot-" + \
                            str(bot_obj.pk) + "/analytics_excel_consolidated_" + \
                            str(date.date()) + '.xls'

                        first_fifteen_days.append(
                            settings.MEDIA_ROOT + file_path)

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Revised Analytics Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        pass

                merged_file_name = "analytics_excel_from_" + \
                    str((today - timedelta(15)).date()) + \
                    "_to_" + str(today.date())

                merged_file_path = merger_excelfiles_within_dir(
                    first_fifteen_days, list_of_sheets, merged_file_name)

                zip_obj.write(merged_file_path, basename(merged_file_path))

                last_fifteen_days = []
                for index in range(16, 31):
                    date = today - timedelta(index)
                    try:
                        file_path = "analytics-download-excel/bot-" + \
                            str(bot_obj.pk) + "/analytics_excel_consolidated_" + \
                            str(date.date()) + '.xls'

                        last_fifteen_days.append(
                            settings.MEDIA_ROOT + file_path)

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Revised Analytics Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        pass

                merged_file_name = "analytics_excel_from_" + \
                    str((today - timedelta(30)).date()) + \
                    "_to_" + str((today - timedelta(16)).date())

                merged_file_path = merger_excelfiles_within_dir(
                    last_fifteen_days, list_of_sheets, merged_file_name)

                zip_obj.write(merged_file_path, basename(merged_file_path))

                zip_obj.close()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Revised analytics cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            message_history_datadump_log.write(
                str(today) + ": failed: " + str(e))

        message_history_datadump_log.close()

        space_removing_pattern = re.compile(r'\s+')
        for export_date_request in AnalyticsExportRequest.objects.filter(analytics_type="combined_global_export", is_completed=False):
            try:
                bot_obj = export_date_request.bot
                if bot_obj.is_deleted:
                    continue
                start_time = time.time()
                start_date = export_date_request.start_date.astimezone(ist)
                end_date = export_date_request.end_date.astimezone(ist)
                email_str = re.sub(space_removing_pattern, '', export_date_request.email_id)
                bot_pk = bot_obj.pk
                temp_date = start_date
                date_format = "%Y-%m-%d"
                while temp_date <= end_date:

                    file_path = "analytics-download-excel/bot-" + str(bot_pk) + '/analytics_' + str(
                        datetime.strftime(temp_date, date_format)) + "custom_filter.xls"

                    if path.exists(settings.MEDIA_ROOT + file_path):
                        temp_date = temp_date + timedelta(1)
                        continue

                    test_wb = Workbook(settings.MEDIA_ROOT + file_path)

                    sheet1 = test_wb.add_worksheet("Message Analytics")
                    message_analytics_list = message_analytics(
                        temp_date, bot_obj)
                    sheet1.write(0, 0, "Date")
                    sheet1.write(0, 1, "Total Messages")
                    sheet1.write(0, 2, "Total Answered Messages")
                    sheet1.write(0, 3, "Total Intuitive Messages")
                    sheet1.write(0, 4, "Total UnAnswered Messages")

                    row = 1
                    for message in message_analytics_list:
                        sheet1.write(row, 0, message["label"])
                        sheet1.write(row, 1, message["total_messages"])
                        sheet1.write(row, 2, message[
                                     "total_answered_messages"])
                        sheet1.write(row, 3, message[
                                     "total_intuitive_messages"])
                        sheet1.write(row, 4, message[
                                     "total_unanswered_messages"])
                        row += 1

                    sheet2 = test_wb.add_worksheet("User Analytics")
                    user_analytics_list = user_analytics(
                        temp_date, bot_obj)
                    sheet2.write(0, 0, "Date")
                    sheet2.write(0, 1, "Count")
                    row = 1
                    for message in user_analytics_list:
                        sheet2.write(row, 0, message["label"])
                        sheet2.write(row, 1, message["count"])
                        row += 1

                    frequent_intents_list = frequent_intents(
                        temp_date, bot_obj)
                    sheet3 = test_wb.add_worksheet(
                        "Frequent Intent Analytics")
                    sheet3.write(0, 0, "Date")
                    sheet3.write(0, 1, "Intent Name")
                    sheet3.write(0, 2, "Frequency")
                    row = 1
                    for message in frequent_intents_list:
                        sheet3.write(row, 0, str(
                            temp_date.strftime("%d-%b-%y")))
                        sheet3.write(row, 1, str(message["intent_name"]))
                        sheet3.write(row, 2, message["frequency"])
                        row += 1

                    category_based_intents_list = category_based_intents(
                        temp_date, bot_obj)
                    sheet4 = test_wb.add_worksheet("Category Analytics")
                    sheet4.write(0, 0, "Date")
                    sheet4.write(0, 1, "Intent Name")
                    sheet4.write(0, 2, "Frequency")
                    sheet4.write(0, 3, "Category Name")
                    row = 1
                    for message in category_based_intents_list:
                        sheet4.write(row, 0, str(
                            temp_date.strftime("%d-%b-%y")))
                        sheet4.write(row, 1, str(message["intent_name"]))
                        sheet4.write(row, 2, message["frequency"])
                        sheet4.write(row, 3, message["category__name"])
                        row += 1

                    unanswered_query_excel_list = unanswered_query_excel(
                        temp_date, bot_obj)
                    sheet5 = test_wb.add_worksheet("Unanswered Query")
                    sheet5.write(0, 0, "Unanswered Query")
                    sheet5.write(0, 1, "Frequency")
                    row = 1
                    for key, value in unanswered_query_excel_list:
                        sheet5.write(row, 0, key)
                        sheet5.write(row, 1, value)
                        row += 1

                    intuitive_queries = intuitive_query_excel(
                        temp_date, bot_obj)
                    sheet6 = test_wb.add_worksheet("Intuitive Queries")
                    sheet6.write(0, 0, "Date")
                    sheet6.write(0, 1, "User Query")
                    sheet6.write(0, 2, "Frequency")
                    sheet6.write(0, 3, "Intuitive Queries")
                    sheet6.write(0, 4, "Channel Name")
                    row = 1
                    for intuitive_query in intuitive_queries:
                        string_intents = ""
                        for intent in intuitive_query.suggested_intents.all():
                            string_intents = string_intents + intent.name + ", "
                        string_intents = string_intents.strip()
                        length = len(string_intents) - 1
                        string_intents = string_intents[0:length]
                        sheet6.write(
                            row, 0, intuitive_query.date.strftime(("%d-%m-%Y")))
                        sheet6.write(
                            row, 1, intuitive_query.intuitive_message_query)
                        sheet6.write(row, 2, intuitive_query.count)
                        sheet6.write(row, 3, string_intents)
                        sheet6.write(row, 4, intuitive_query.channel)
                        row += 1

                    user_nudge_analytics_data = user_nudge_analytics(
                        temp_date, bot_obj)
                    sheet7 = test_wb.add_worksheet("User Nudge Analytics")
                    sheet7.write(0, 0, "Greeting/Intent bubble name")
                    sheet7.write(0, 1, "Click Count")
                    sheet7.write(0, 2, "Active/Inactive")
                    row = 1
                    for nudge_data in user_nudge_analytics_data:
                        sheet7.write(row, 0, nudge_data["name"])
                        sheet7.write(row, 1, str(nudge_data["count"]))
                        if nudge_data["is_active"]:
                            sheet7.write(row, 2, "Active")
                        row += 1

                    sheet8 = test_wb.add_worksheet("Device Specific Analytics")
                    device_specific_analytics_list = device_specific_analytics(
                        temp_date, bot_obj)

                    sheet8.write(0, 0, "Date")
                    sheet8.write(0, 1, "Mobile Users")
                    sheet8.write(0, 2, "Desktop Users")
                    sheet8.write(0, 3, "Queries asked(Mobile)")
                    sheet8.write(0, 4, "Queries asked(Desktop)")
                    sheet8.write(0, 5, "Queries answered(Mobile)")
                    sheet8.write(0, 6, "Queries answered(Desktop)")
                    sheet8.write(0, 7, "Queries intuitive(Desktop)")
                    sheet8.write(0, 8, "Queries intuitive(Mobile)")
                    sheet8.write(0, 9, "Queries unanswered (Mobile)")
                    sheet8.write(0, 10, "Queries unanswered (Desktop)")

                    row = 1
                    for device_data in device_specific_analytics_list:
                        sheet8.write(row, 0, device_data["label"])
                        sheet8.write(row, 1, str(
                            device_data["total_users_mobile"]))
                        sheet8.write(row, 2, str(
                            device_data["total_users_desktop"]))
                        sheet8.write(row, 3, str(
                            device_data["total_messages_mobile"]))
                        sheet8.write(row, 4, str(
                            device_data["total_messages_desktop"]))
                        sheet8.write(row, 5, str(
                            device_data["total_answered_messages_mobile"]))
                        sheet8.write(row, 6, str(
                            device_data["total_answered_messages_desktop"]))
                        sheet8.write(row, 7, str(
                            device_data["total_unanswered_messages_mobile"]))
                        sheet8.write(row, 8, str(
                            device_data["total_unanswered_messages_desktop"]))
                        row += 1

                    sheet9 = test_wb.add_worksheet("Hour wise analytics")
                    hour_wise_analytics_list = hour_wise_analytics(
                        temp_date, bot_obj)
                    sheet9.write(0, 0, "Date")
                    sheet9.write(0, 1, "Time Interval")
                    sheet9.write(0, 2, "No. of users")
                    sheet9.write(0, 3, "No. of messages")
                    row = 1
                    total_number_of_messages = hour_wise_analytics_list[0]["total_message_count"]
                    total_number_of_users = hour_wise_analytics_list[0]["total_users_count"]
                    time_hr = 1
                    for number in range(len(total_number_of_messages)):
                        sheet9.write(row, 0, temp_date.strftime("%d-%m-%Y"))
                        sheet9.write(row, 1, str(time_hr - 1) +
                                     "hr" + " - " + str(time_hr) + "hr")
                        sheet9.write(row, 2, total_number_of_users[number])
                        sheet9.write(row, 3, total_number_of_messages[number])
                        row += 1
                        time_hr += 1

                    sheet10 = test_wb.add_worksheet("WhatsApp Catalogue Analytics")
                    sheet10 = whatsapp_catalogue_analytics(sheet10, temp_date, bot_obj)

                    test_wb.close()

                    temp_date = temp_date + timedelta(1)

                export_zip_file_path = "analytics-download-excel/bot-" + \
                    str(bot_pk) + "/AnalyticsDownloadCustom_" + \
                    str(export_date_request.pk) + ".zip"

                zip_obj = ZipFile(settings.MEDIA_ROOT +
                                  export_zip_file_path, 'w')

                temp_date = start_date

                list_of_sheets = ["Message Analytics", "User Analytics",
                                  "Frequent Intent Analytics", "Category Analytics", "Unanswered Query", "Intuitive Queries", "User Nudge Analytics", "Device Specific Analytics", "Hour wise analytics", "WhatsApp Catalogue Analytics"]

                while temp_date <= end_date:
                    temp_start_date = temp_date
                    temp_end_date = temp_start_date + timedelta(15)
                    custom_list_fifteen_days = []
                    count_no_of_days = 1
                    while temp_start_date <= temp_end_date and temp_start_date <= end_date:
                        try:
                            file_path = "analytics-download-excel/bot-" + str(bot_pk) + '/analytics_' + str(
                                datetime.strftime(temp_date, date_format)) + "custom_filter.xls"
                            custom_list_fifteen_days.append(
                                settings.MEDIA_ROOT + file_path)

                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Revised Analytics Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                            pass

                        temp_start_date = temp_start_date + timedelta(1)
                        temp_date = temp_date + timedelta(1)
                        count_no_of_days = count_no_of_days + 1

                    merged_file_name = "analytics_excel_from_" + \
                        str((temp_start_date - timedelta(count_no_of_days)
                             ).date()) + "_to_" + str(temp_start_date.date())

                    merged_file_path = merger_excelfiles_within_dir(
                        custom_list_fifteen_days, list_of_sheets, "custom_filter-till" + str(
                            datetime.strftime(temp_end_date, date_format)))

                    zip_obj.write(merged_file_path, basename(merged_file_path))

                zip_obj.close()

                username = export_date_request.user.username

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
                            We have received a request to provide you with the Analytics Data for <b>{}</b> Bot from {} to {}. Please click on the link below to download the file.
                        </p>
                        <a href="{}/{}">click here</a>
                        <p>&nbsp;</p>"""

                config = get_developer_console_settings()

                body += config.custom_report_template_signature

                body += """</div></body>"""

                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                body = body.format(username, bot_obj.name, str(start_date), str(
                    end_date), domain, 'files/' + export_zip_file_path)

                for email_id in email_str.split(","):
                    send_email_to_customer_via_awsses(
                        email_id, "Analytics Data for " + str(bot_obj.name) + " Bot", body)

                export_date_request.is_completed = True
                export_date_request.export_file_path = domain + '/files/' + export_zip_file_path
                export_date_request.time_taken = time.time() - start_time
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()

                logger.error("Analytics Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                message_history_datadump_log.write(
                    str(today) + ": failed: " + str(e))
                export_date_request.is_completed = False
                export_date_request.save()

        message_history_datadump_log.close()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        error_msg = str(e) + str(exc_tb.tb_lineno)
        check_and_send_broken_bot_mail(
            627, "Web", "", error_msg)


def return_zero_if_number_is_none(number):
    if not number:
        return 0

    return number
