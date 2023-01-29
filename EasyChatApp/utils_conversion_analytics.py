from django.conf import settings
from datetime import date, datetime, timedelta
from django.db.models import Q, Count, Sum, CharField, Value
import re
import sys
import json
import copy
import uuid
import logging
import wordninja
import subprocess
import os
import time
import csv
import threading

from EasyChatApp.utils import *
from EasyChatApp.utils_api_analytics import get_whatsapp_catalogue_conversion_analytics
from LiveChatApp.models import *
from EasyChatApp.utils_execute_query import get_bot_info_object
from EasyChatApp.static_dummy_data import *
from EasyChatApp.utils_bot import get_translated_text_with_api_status, check_and_update_tunning_object
from EasyChatApp.models import *

from xlwt import Workbook
from zipfile import ZipFile
from django.utils.timezone import get_current_timezone


def create_flow_conversion_analytics_excel(start_date, end_date, channel_list, bot_pk, email_id, to_be_mailed=True,
                                           selected_language="en", export_request_obj=None):
    try:
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_pk), is_deleted=False, is_uat=True)
        bot_objs = [uat_bot_obj]

        if len(channel_list) == 0:
            channels = Channel.objects.filter(is_easychat_channel=True)
        else:
            channels = Channel.objects.filter(name__in=channel_list)

        bot_info_obj = get_bot_info_object(uat_bot_obj)
        translate_api_status = True
        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            flow_completion_data = copy.deepcopy(STATIC_EASYCHAT_CONVERSION_FLOW_DUMMY_DATA)
            for intent in range(len(flow_completion_data)):
                if translate_api_status:
                    flow_completion_data[intent]["multilingual_name"], translate_api_status = get_translated_text_with_api_status(flow_completion_data[intent]["name"], selected_language, EasyChatTranslationCache, translate_api_status)
        else:
            flow_completion_data, translate_api_status = get_conversion_flow_counts_data(
                start_date, end_date, bot_objs, channels, Intent, Tree, FlowAnalytics, FlowTerminationData,
                DailyFlowAnalytics, selected_language)

        filename = 'flow_conversion_analytics_from_' + \
            start_date.strftime("%d-%m-%Y") + '_to_' + \
            end_date.strftime("%d-%m-%Y") + '.xls'

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Flow Name")
        sheet1.write(0, 1, "Hit")
        sheet1.write(0, 2, "Completion")
        sheet1.write(0, 3, "Flow Aborted/Terminated")
        sheet1.write(0, 4, "Conversion Percentage")

        row = 1

        for flow_data in flow_completion_data:
            if translate_api_status:
                sheet1.write(row, 0, flow_data["multilingual_name"])
            else:
                sheet1.write(row, 0, flow_data["name"])
            sheet1.write(row, 1, flow_data["hit_count"])
            sheet1.write(row, 2, flow_data["complete_count"])
            sheet1.write(row, 3, flow_data["abort_count"])
            sheet1.write(row, 4, str(flow_data["flow_percent"]) + "%")
            row += 1

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)
        file_path = secured_files_path + filename
        test_wb.save(secured_files_path + filename)

        joined_list = []
        channel_names = [channel.name for channel in channels]
        index = 0
        while (start_date + timedelta(days=index)).strftime("%Y-%m-%d") <= end_date.strftime("%Y-%m-%d"):
            if os.path.isfile(settings.SECURE_MEDIA_ROOT + "EasyChatApp/Botwise-flow-dropoff/" + str(uat_bot_obj.name) + "_" + str(uat_bot_obj.pk) + "/User_dropoff_analytics_of_" + str((start_date + timedelta(days=index)).strftime("%Y-%m-%d")) + ".csv"):
                joined_list.append(str(settings.SECURE_MEDIA_ROOT + "EasyChatApp/Botwise-flow-dropoff/" + str(uat_bot_obj.name) + "_" + str(uat_bot_obj.pk) + "/User_dropoff_analytics_of_" + str((start_date + timedelta(days=index)).strftime("%Y-%m-%d")) + ".csv"))
            index += 1

        zip_filename = "Flow Completion Rate From " + str(start_date.strftime("%d-%m-%Y")) + " to " + str(end_date.strftime("%d-%m-%Y")) + ".zip"

        zip = ZipFile(secured_files_path + zip_filename, "w")
        zip.write(file_path, os.path.basename(file_path))
        if len(joined_list) > 0:
            df = pd.concat(map(pd.read_csv, joined_list), ignore_index=True)
            df = df[df["Channel"].isin(channel_names)]
            dropoff_filepath = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + "user_specific_dropoff_from_" + str(start_date.strftime("%d-%m-%Y")) + "_to_" + str((end_date - timedelta(days=1)).strftime("%d-%m-%Y")) + ".csv"
            df.sort_values([df.columns[1], df.columns[0]],
                            axis=0,
                            ascending=[True, True],
                            inplace=True)
            df.to_csv(dropoff_filepath, index=False)
            zip.write(dropoff_filepath, os.path.basename(dropoff_filepath))

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + zip_filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.is_completed = True
            export_request_obj.export_file_path = file_url
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            from EasyChatApp.utils import send_mail_of_analytics
            send_mail_of_analytics(
                'Flow Conversion Analytics', file_url, email_id)
        else:
            return file_url

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_dropoff_conversion_analytics_excel(start_date, end_date, channel_list, bot_pk, email_id, to_be_mailed=True,
                                              selected_language="en", export_request_obj=None):
    try:
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_pk), is_deleted=False, is_uat=True)
        bot_objs = [uat_bot_obj]
        translate_api_status_flag = 1
        if len(channel_list) == 0:
            channel_objs = Channel.objects.filter(is_easychat_channel=True)
        else:
            channel_objs = Channel.objects.filter(name__in=channel_list)

        bot_info_obj = get_bot_info_object(uat_bot_obj)
        translate_api_status = True
        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            result = copy.deepcopy(STATIC_EASYCHAT_CONVERSION_DROPOFF_DUMMY_DATA)
            for static_data in range(len(result)):
                result[static_data][
                    "child_intent_multilingual_name"], translate_api_status = get_translated_text_with_api_status(
                    result[static_data]["child_intent_name"], selected_language, EasyChatTranslationCache,
                    translate_api_status)
                result[static_data][
                    "main_intent_multilingual_name"], translate_api_status = get_translated_text_with_api_status(
                    result[static_data]["main_intent_name"], selected_language, EasyChatTranslationCache,
                    translate_api_status)
        else:
            all_triggered_flows_intent_pk_list = get_all_bot_flows_intent_pk_list(start_date, end_date, bot_objs,
                                                                                  channel_objs, Intent, Tree,
                                                                                  FlowAnalytics, DailyFlowAnalytics)

            result = []

            for intent_pk in all_triggered_flows_intent_pk_list:
                intent_obj = Intent.objects.get(pk=intent_pk)
                root_tree_obj = intent_obj.tree

                flow_analytics_objects = DailyFlowAnalytics.objects.filter(
                    intent_indentifed=intent_obj, created_time__date__gte=start_date, created_time__date__lte=end_date,
                    channel__in=channel_objs)
                flow_analytics_objects_that_day = FlowAnalytics.objects.none()
                if end_date.date() == datetime.datetime.now().date():
                    flow_analytics_objects_that_day = FlowAnalytics.objects.filter(intent_indentifed=intent_obj, created_time__date=end_date.date(), channel__in=channel_objs)
                flow_termination_data_objs = FlowTerminationData.objects.filter(intent=intent_obj,
                                                                                created_datetime__date__gte=start_date,
                                                                                created_datetime__date__lte=end_date,
                                                                                channel__in=channel_objs)

                count_intent_was_called = 0
                try:
                    count_intent_was_called = flow_analytics_objects.filter(
                        current_tree=intent_obj.tree).aggregate(Sum('count'))['count__sum']
                    if count_intent_was_called == None:
                        count_intent_was_called = 0
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("create_dropoff_conversion_analytics_excel Intent count problem %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': "None"})
                    pass
                try:
                    count_intent_was_called += flow_analytics_objects_that_day.filter(
                        current_tree=intent_obj.tree).count()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("create_dropoff_conversion_analytics_excel Intent count problem that day %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': "None"})
                    count_intent_was_called = 0
                    pass

                temp_result, translate_api_status = get_child_tree_objs_flow_dropoff_analytics(root_tree_obj.pk, root_tree_obj, [], flow_analytics_objects, flow_analytics_objects_that_day, flow_termination_data_objs, intent_obj, count_intent_was_called, [], [], True, 1, [], selected_language)
                if not translate_api_status:
                    translate_api_status_flag = 0

                result += temp_result

            result = sorted(result, key=lambda d: d["dropoffs"])
            result.reverse()

        filename = 'dropoff_conversion_analytics_from_' + \
            start_date.strftime("%d-%m-%Y") + '_to_' + \
            end_date.strftime("%d-%m-%Y") + '.xls'
        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Child Intent Name")
        sheet1.write(0, 1, "Dropoffs")
        sheet1.write(0, 2, "Main Intent Name")
        sheet1.write(0, 3, "Dropoff Percentage")

        row = 1
        for flow_data in result:
            if not translate_api_status_flag:
                sheet1.write(row, 0, flow_data["child_intent_name"])
                sheet1.write(row, 1, str(flow_data["dropoffs"]))
                sheet1.write(row, 2, flow_data["main_intent_name"])
            else:
                sheet1.write(row, 0, flow_data["child_intent_multilingual_name"])
                sheet1.write(row, 1, str(flow_data["dropoffs"]))
                sheet1.write(row, 2, flow_data["main_intent_multilingual_name"])
            sheet1.write(row, 3, str(flow_data["dropoff_percentage"]) + "%")
            row += 1

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)
        file_path = secured_files_path + filename
        test_wb.save(secured_files_path + filename)

        joined_list = []
        channel_names = [channel.name for channel in channel_objs]
        index = 0
        while (start_date + timedelta(days=index)).strftime("%Y-%m-%d") <= end_date.strftime("%Y-%m-%d"):
            if os.path.isfile(settings.SECURE_MEDIA_ROOT + "EasyChatApp/Botwise-flow-dropoff/" + str(uat_bot_obj.name) + "_" + str(uat_bot_obj.pk) + "/User_dropoff_analytics_of_" + str((start_date + timedelta(days=index)).strftime("%Y-%m-%d")) + ".csv"):
                joined_list.append(str(settings.SECURE_MEDIA_ROOT + "EasyChatApp/Botwise-flow-dropoff/" + str(uat_bot_obj.name) + "_" + str(uat_bot_obj.pk) + "/User_dropoff_analytics_of_" + str((start_date + timedelta(days=index)).strftime("%Y-%m-%d")) + ".csv"))
            index += 1

        zip_filename = "Customer Dropoff Analytics From " + str(start_date.strftime("%d-%m-%Y")) + " to " + str(end_date.strftime("%d-%m-%Y")) + ".zip"

        zip = ZipFile(secured_files_path + zip_filename, "w")
        zip.write(file_path, os.path.basename(file_path))
        if len(joined_list) > 0:
            df = pd.concat(map(pd.read_csv, joined_list), ignore_index=True)
            df = df[df["Channel"].isin(channel_names)]
            dropoff_filepath = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + "user_specific_dropoff_from_" + str(start_date.strftime("%d-%m-%Y")) + "_to_" + str((end_date - timedelta(days=1)).strftime("%d-%m-%Y")) + ".csv"
            df.sort_values([df.columns[1], df.columns[0]],
                            axis=0,
                            ascending=[True, True],
                            inplace=True)
            df.to_csv(dropoff_filepath, index=False)

            zip.write(dropoff_filepath, os.path.basename(dropoff_filepath))

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + zip_filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.is_completed = True
            export_request_obj.export_file_path = file_url
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            from EasyChatApp.utils import send_mail_of_analytics
            send_mail_of_analytics(
                'Customer Dropoff Analytics', file_url, email_id)
        else:
            return file_url

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_intent_conversion_analytics_excel(start_date, end_date, channel_list, bot_pk, email_id, to_be_mailed=True,
                                             selected_language="en", export_request_obj=None):
    try:
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_pk), is_deleted=False, is_uat=True)
        bot_objs = [uat_bot_obj]

        if len(channel_list) == 0:
            channels = list(Channel.objects.values_list('name', flat=True))
        else:
            channels = channel_list

        bot_info_obj = get_bot_info_object(uat_bot_obj)
        translate_api_status = True
        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            intent_completion_data_list = copy.deepcopy(STATIC_EASYCHAT_CONVERSION_INTENT_DUMMY_DATA)
            total_intent_count = copy.deepcopy(STATIC_EASYCHAT_CONVERSION_INTENT_TOTAL_COUNT)
            for intent in range(len(intent_completion_data_list)):
                if translate_api_status:
                    intent_completion_data_list[intent]["multilingual_name"], translate_api_call_status = get_translated_text_with_api_status(intent_completion_data_list[intent]["intent_name"], selected_language, EasyChatTranslationCache, translate_api_status)

        else:
            intent_count = list(
                MISDashboard.objects.filter(bot__in=bot_objs, channel_name__in=channels, date__date__gte=start_date,
                                            date__date__lte=end_date).values(
                    'intent_name', 'intent_recognized').order_by('intent_name').annotate(
                    count=Count('intent_name')).exclude(
                    intent_recognized__isnull=True))
            total_intent_count = MISDashboard.objects.filter(
                bot__in=bot_objs, channel_name__in=channels, date__date__gte=start_date,
                date__date__lte=end_date).exclude(intent_recognized__isnull=True).count()
            intent_completion_data_list = sorted(
                list(intent_count), key=lambda i: i['count'], reverse=True)

            intent_completion_data_list, translate_api_status = conversion_intent_analytics_translator(
                intent_completion_data_list, selected_language, translate_api_status)

        filename = 'intent_usage_analytics_from_' + \
                   start_date.strftime("%d-%m-%Y") + '_to_' + \
                   end_date.strftime("%d-%m-%Y") + '.xls'

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Intent Name")
        sheet1.write(0, 1, "Frequency")
        sheet1.write(0, 2, "Usage Percentage")

        row = 1

        for intent_data in intent_completion_data_list:
            if translate_api_status:
                sheet1.write(row, 0, intent_data["multilingual_name"])
            else:
                sheet1.write(row, 0, intent_data["intent_name"])
            sheet1.write(row, 1, intent_data["count"])
            if total_intent_count == 0:
                sheet1.write(row, 2, "0%")
            else:
                sheet1.write(row, 2, str(
                    round((intent_data["count"] / total_intent_count) * 100)) + "%")
            row += 1

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        test_wb.save(secured_files_path + filename)

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.is_completed = True
            export_request_obj.export_file_path = file_url
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            from EasyChatApp.utils import send_mail_of_analytics
            send_mail_of_analytics(
                'Intent Usage Analytics', file_url, email_id)
        else:
            return file_url

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_whatsapp_block_analytics_excel(start_date, end_date, block_type, bot_pk, email_id, to_be_mailed=True, export_request_obj=None):
    try:
        blocked_session_objs = []
        bot_obj = Bot.objects.get(
            pk=int(bot_pk), is_deleted=False)
        datetime_fmt = "%d %b %Y %I:%M %p"

        bot_info_obj = get_bot_info_object(bot_obj)
        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            blocked_session_objs = copy.deepcopy(
                STATIC_EASYCHAT_WHATSAPP_BLOCK_ANALYSIS_DUMMY_DATA)
        else:
            if block_type == "All":
                blocked_session_objs = list(UserSessionHealth.objects.filter(bot=bot_obj, is_blocked=True, creation_date__gte=start_date, creation_date__lte=end_date).order_by('-block_time').values(
                    'block_type', 'blocked_spam_keywords', 'block_time', 'unblock_time', whatsapp_number=F('profile__user_id')
                ))
            else:
                blocked_session_objs = list(UserSessionHealth.objects.filter(bot=bot_obj, is_blocked=True, block_type=block_type, creation_date__gte=start_date, creation_date__lte=end_date).order_by('-block_time').values(
                    'block_type', 'blocked_spam_keywords', 'block_time', 'unblock_time', whatsapp_number=F('profile__user_id')
                ))

        filename = 'whatsapp_block_analytics_from_' + \
                   start_date.strftime("%d-%m-%Y") + '_to_' + \
                   end_date.strftime("%d-%m-%Y") + '.xls'

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Whatsapp Number")
        sheet1.write(0, 1, "Blocking type")
        sheet1.write(0, 2, "Blocking Keyword")
        sheet1.write(0, 3, "Block Date time")
        sheet1.write(0, 4, "Unblock date time")

        row = 1

        for session_obj in blocked_session_objs:
            sheet1.write(row, 0, session_obj["whatsapp_number"])
            if session_obj["block_type"] == "keyword":
                sheet1.write(row, 1, "Keyword")
                sheet1.write(row, 2, session_obj["blocked_spam_keywords"])
            else:
                sheet1.write(row, 1, "Spam Message")
                sheet1.write(row, 2, "-")
            sheet1.write(row, 3, session_obj["block_time"].astimezone(get_current_timezone()).strftime(datetime_fmt))
            sheet1.write(row, 4, session_obj["unblock_time"].astimezone(get_current_timezone()).strftime(datetime_fmt))
            
            row += 1

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        test_wb.save(secured_files_path + filename)

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.is_completed = True
            export_request_obj.export_file_path = file_url
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            from EasyChatApp.utils import send_mail_of_analytics
            send_mail_of_analytics(
                'Whatsapp Block Spam Analytics', file_url, email_id)
        else:
            return file_url

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_whatsapp_catalogue_analytics_csv(start_date, end_date, is_catalogue_purchased, bot_pk, email_id, to_be_mailed=True, export_request_obj=None):
    try:
        cart_objs_list = []
        bot_obj = Bot.objects.get(
            pk=int(bot_pk), is_deleted=False)
        datetime_fmt = "%d %b %Y %I:%M %p"
        is_static = False
        bot_info_obj = get_bot_info_object(bot_obj)
        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            cart_objs_list = copy.deepcopy(
                STATIC_EASYCHAT_WHATSAPP_CATALOGUE_CONVERSION_DUMMY_DATA)
            is_static = True
        else:
            cart_objs_list, _ = get_whatsapp_catalogue_conversion_analytics(
                bot_obj, is_catalogue_purchased, start_date, end_date, True)

        filename = 'catalogue_conversion_analytics_from_' + \
                   start_date.strftime("%d-%m-%Y") + '_to_' + \
                   end_date.strftime("%d-%m-%Y") + '.csv'

        secured_files_path = settings.SECURE_MEDIA_ROOT + \
            'EasyChatApp/custom_analytics/' + str(bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        path = '/secured_files/EasyChatApp/custom_analytics/' + \
            str(bot_obj.pk) + '/' + filename

        export_csv_file = open(settings.BASE_DIR + path, 'w+')
        
        writer = csv.writer(export_csv_file)

        file_headings = ["Date and Time", "WhatsApp Number", "Cart", "Purchased", "Price"]

        writer.writerow(file_headings)

        for cart_obj in cart_objs_list:
            row_data = []
            is_purchased = "Yes" if cart_obj["is_purchased"] else "No"

            if is_static:
                cart_obj["cart_update_time"] = datetime.datetime.strptime(
                    cart_obj["cart_update_time"], '%B %d,%Y,%I:%M %p')

            row_data.append(cart_obj["cart_update_time"].strftime(datetime_fmt))
            row_data.append(cart_obj["user__user_id"])
            row_data.append(cart_obj["current_cart_packet"])
            row_data.append(is_purchased)
            row_data.append(cart_obj["cart_total"])

            writer.writerow(row_data)

        export_csv_file.close()

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.is_completed = True
            export_request_obj.export_file_path = file_url
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            from EasyChatApp.utils import send_mail_of_analytics
            send_mail_of_analytics(
                'Whatsapp Catalogue Conversion Analytics', file_url, email_id)
        else:
            return file_url

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error create_whatsapp_catalogue_analytics_csv  %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_livechat_conversion_analytics_excel(start_date, end_date, channel_list, bot_pk, email_id, to_be_mailed=True, export_request_obj=None):
    try:
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_pk), is_deleted=False, is_uat=True)
        bot_objs = [uat_bot_obj]

        if len(channel_list) == 0:
            channels = Channel.objects.filter(is_easychat_channel=True)
            channel_names = list(
                Channel.objects.values_list('name', flat=True))
        else:
            channels = Channel.objects.filter(name__in=channel_list)
            channel_names = channel_list

        bot_info_obj = get_bot_info_object(uat_bot_obj)

        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            livechat_completion_data_list = STATIC_EASYCHAT_CONVERSION_LIVECHAT_DUMMY_DATA
        else:
            livechat_completion_data_list = []
            for i_counter in range((end_date - start_date).days + 1):
                livechat_completion_data = {}
                current_date = start_date + timedelta(days=i_counter)
                livechat_completion_data['date'] = str(current_date.date())
                livechat_completion_data['intent_raised_count'] = 0

                current_livechat_analytics_count = DailyLiveChatAnalytics.objects.filter(date=current_date, bot=uat_bot_obj, channel__name__in=channel_names).aggregate(Sum("count"))["count__sum"]
                if current_livechat_analytics_count:
                    livechat_completion_data['intent_raised_count'] = current_livechat_analytics_count
                
                livechat_completion_data['request_raised_count'] = LiveChatCustomer.objects.filter(
                    bot__in=bot_objs, request_raised_date=current_date, channel__in=channels).count()
                livechat_completion_data['agent_connect_count'] = LiveChatCustomer.objects.filter(
                    bot__in=bot_objs, request_raised_date=current_date, channel__in=channels).exclude(
                    agent_id=None).count()
                livechat_completion_data_list.append(livechat_completion_data)

        filename = 'livechat_analytics_from_' + \
                   start_date.strftime("%d-%m-%Y") + '_to_' + \
                   end_date.strftime("%d-%m-%Y") + '.xls'

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Date")
        sheet1.write(0, 1, "Chat with an expert")
        sheet1.write(0, 2, "Request Raised")
        sheet1.write(0, 3, "Agent Connect Count")
        sheet1.write(0, 4, "Conversion Percentage")

        row = 1
        for livechat_completion_data in livechat_completion_data_list:
            sheet1.write(row, 0, livechat_completion_data['date'])
            sheet1.write(
                row, 1, livechat_completion_data['intent_raised_count'])
            sheet1.write(
                row, 2, livechat_completion_data['request_raised_count'])
            sheet1.write(
                row, 3, livechat_completion_data['agent_connect_count'])
            if (livechat_completion_data['intent_raised_count'] == 0):
                sheet1.write(row, 4, "0%")
            else:
                sheet1.write(row, 4, str(round(
                    (livechat_completion_data['agent_connect_count'] / livechat_completion_data[
                        'intent_raised_count']) * 100)) + "%")
            row += 1

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        test_wb.save(secured_files_path + filename)

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.is_completed = True
            export_request_obj.export_file_path = file_url
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            from EasyChatApp.utils import send_mail_of_analytics
            send_mail_of_analytics(
                'Live Chat Analytics', file_url, email_id)
        else:
            return file_url

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def get_traffic_conversion_analytics_export_file_path(start_date, end_date, source_list, bot_pk, email_id, to_be_mailed=True, export_request_obj=None):
    try:
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_pk), is_deleted=False, is_uat=True)
        bot_objs = [uat_bot_obj]

        bot_info_obj = get_bot_info_object(uat_bot_obj)

        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            bot_hit_data_list = STATIC_EASYCHAT_CONVERSION_TRAFFIC_ANALYTICS_DUMMY_DATA
        else:
            if len(source_list) == 0:
                source_list = list(TrafficSources.objects.filter(bot=uat_bot_obj).values_list(
                    'web_page_source', flat=True).exclude(web_page_source__isnull=True).exclude(
                    web_page_source="").distinct())
            bot_hit_data_list = list(TrafficSources.objects.filter(bot__in=bot_objs, visiting_date__gte=start_date,
                                                                   visiting_date__lte=end_date,
                                                                   web_page_source__in=source_list).values('web_page',
                                                                                                           'web_page_source').annotate(
                bot_views=Sum('bot_clicked_count'), page_views=Sum('web_page_visited')).exclude(
                web_page_source__isnull=True).exclude(web_page_source="").order_by("-bot_views", "-page_views"))
            
            time_spent_objs = TimeSpentByUser.objects.filter(bot__in=bot_objs)
            for bot_hit_data in bot_hit_data_list:
                average_time_spent = time_spent_objs.filter(web_page=bot_hit_data['web_page'], web_page_source=bot_hit_data['web_page_source']).aggregate(Sum('total_time_spent'))['total_time_spent__sum']
                if average_time_spent != None:
                    bot_hit_data['average_time_spent'] = average_time_spent
                else:
                    bot_hit_data['average_time_spent'] = 0

        filename = 'traffic_analytics_from_' + \
                   start_date.strftime("%d-%m-%Y") + '_to_' + \
                   end_date.strftime("%d-%m-%Y") + '.xls'

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Page(Links)")
        sheet1.write(0, 1, "Source/Medium")
        sheet1.write(0, 2, "Page Views")
        sheet1.write(0, 3, "Bot Views")
        sheet1.write(0, 4, "Avg. Time on Bot")

        row = 1
        for bot_hit_data in bot_hit_data_list:
            sheet1.write(row, 0, bot_hit_data["web_page"])
            sheet1.write(row, 1, bot_hit_data["web_page_source"])
            sheet1.write(row, 2, bot_hit_data["page_views"])
            sheet1.write(row, 3, bot_hit_data["bot_views"])
            sheet1.write(row, 4, str(timedelta(
                seconds=bot_hit_data["average_time_spent"])))
            row += 1

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        test_wb.save(secured_files_path + filename)

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.is_completed = True
            export_request_obj.export_file_path = file_url
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            from EasyChatApp.utils import send_mail_of_analytics
            send_mail_of_analytics(
                'Traffic Conversion Analytics', file_url, email_id)

        return file_url

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def get_welcome_conversion_analytics_export_file_path(start_date, end_date, bot_pk, email_id, selected_language, to_be_mailed=True, export_request_obj=None):
    try:
        datetime_start = start_date
        datetime_end = end_date
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_pk), is_deleted=False, is_uat=True)
        bot_objs = [uat_bot_obj]

        bot_info_obj = get_bot_info_object(uat_bot_obj)
        translate_api_status = True
        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            welcome_analytics_list = copy.deepcopy(STATIC_EASYCHAT_CONVERSION_WELCOME_ANALYTICS_EXCEL_DUMMY_DATA)
            total_clicks = copy.deepcopy(STATIC_EASYCHAT_CONVERSION_WELCOME_ANALYTICS_TOTAL_COUNT)
            for data in range(len(welcome_analytics_list)):
                welcome_analytics_list[data]["multilingual_name"], translate_api_status = get_translated_text_with_api_status(welcome_analytics_list[data]["intent__name"], selected_language, EasyChatTranslationCache, translate_api_status)

        else:

            welcome_banner_clicked_data_list = WelcomeBannerClicks.objects.filter(bot__in=bot_objs,
                                                                                  visiting_date__gte=start_date,
                                                                                  visiting_date__lte=end_date).annotate(
                frequency=Count("user_id"))
            total_clicks = welcome_banner_clicked_data_list.aggregate(Sum('frequency'))["frequency__sum"]

            no_days = (datetime_end - datetime_start).days + 1

            welcome_analytics_list = []
            for day in range(no_days):
                temp_datetime = datetime_start + timedelta(day)
                label = temp_datetime.strftime("%d-%m-%Y")
                temp_datetime = temp_datetime.date()
                date_filtered_welcome_banner_clicked_data_list = list(
                    welcome_banner_clicked_data_list.filter(visiting_date=temp_datetime).values(
                        'web_page_visited', 'preview_source', 'frequency', 'pk', 'intent__name', 'intent__pk').annotate(
                        date=Value(str(label), output_field=CharField())))
                welcome_analytics_list += date_filtered_welcome_banner_clicked_data_list

            welcome_analytics_list, translate_api_status = welcome_analytics_translator(welcome_analytics_list, selected_language, translate_api_status)

        filename = 'conversion_analytics_from_' + \
                   start_date.strftime("%d-%m-%Y") + '_to_' + \
                   end_date.strftime("%d-%m-%Y") + '.xls'

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Date")
        sheet1.write(0, 1, "Image Name")
        sheet1.write(0, 2, "Redirection URL")
        sheet1.write(0, 3, "Trigger Intent")
        sheet1.write(0, 4, "User Clicks")
        sheet1.write(0, 5, "User Clicks Percentage")

        row = 1

        for message in welcome_analytics_list:
            sheet1.write(row, 0, message["date"])
            preview_source = message["preview_source"].split("/")
            preview_source = preview_source[len(preview_source) - 1]
            sheet1.write(row, 1, preview_source)
            sheet1.write(row, 2, message["web_page_visited"])
            if message["intent__name"] == None:
                sheet1.write(row, 3, "-")
            else:
                if translate_api_status:
                    sheet1.write(row, 3, message["multilingual_name"])
                else:
                    sheet1.write(row, 3, message["intent__name"])
            sheet1.write(row, 4, message["frequency"])
            percentage_total = round((message["frequency"] / total_clicks) * 100)
            sheet1.write(row, 5, str(percentage_total) + "%")
            row += 1

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        test_wb.save(secured_files_path + filename)
        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.is_completed = True
            export_request_obj.export_file_path = file_url
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            from EasyChatApp.utils import send_mail_of_analytics
            send_mail_of_analytics(
                'Welcome Banner Click Rates', file_url, email_id)
        else:
            return file_url

        return file_url

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def get_conversion_analytics_export_file_path(type_of_analytics, start_date, end_date, channel_list, bot_pk,
                                              selected_language, is_catalogue_purchased, block_type="All"):
    export_file_path = ""
    try:
        to_be_mailed = False
        email_id = ""
        # email id is not required but the parameter is required
        if type_of_analytics == "flow_conversion_analytics":
            export_file_path = create_flow_conversion_analytics_excel(
                start_date, end_date, channel_list, bot_pk, email_id, to_be_mailed, selected_language)
        elif type_of_analytics == "intent_conversion_analytics":
            export_file_path = create_intent_conversion_analytics_excel(
                start_date, end_date, channel_list, bot_pk, email_id, to_be_mailed, selected_language)
        elif type_of_analytics == "livechat_conversion_analytics":
            export_file_path = create_livechat_conversion_analytics_excel(
                start_date, end_date, channel_list, bot_pk, email_id, to_be_mailed)
        elif type_of_analytics == "dropoff_conversion_analytics":
            export_file_path = create_dropoff_conversion_analytics_excel(start_date, end_date, channel_list, bot_pk,
                                                                         email_id, to_be_mailed, selected_language)
        elif type_of_analytics == "whatsapp_block_analytics":
            export_file_path = create_whatsapp_block_analytics_excel(start_date, end_date, block_type, bot_pk,
                                                                      email_id, to_be_mailed)
        elif type_of_analytics == "catalogue_conversion_analytics":
            export_file_path = create_whatsapp_catalogue_analytics_csv(start_date, end_date, is_catalogue_purchased, bot_pk,
                                                                       email_id, to_be_mailed)
        return export_file_path
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_conversion_analytics_export_file_path: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return export_file_path


def start_thread_of_conversion_analytics_data_via_mail(type_of_analytics, start_date, end_date, channel_list, bot_pk,
                                                       email_id, selected_language, is_catalogue_purchased, block_type="All"):
    try:
        if type_of_analytics == "flow_conversion_analytics":
            thread = threading.Thread(target=create_flow_conversion_analytics_excel, args=(
                start_date, end_date, channel_list, bot_pk, email_id, True, selected_language,), daemon=True)
            thread.start()
        elif type_of_analytics == "intent_conversion_analytics":
            thread = threading.Thread(target=create_intent_conversion_analytics_excel, args=(
                start_date, end_date, channel_list, bot_pk, email_id, True, selected_language,), daemon=True)
            thread.start()
        elif type_of_analytics == "livechat_conversion_analytics":
            thread = threading.Thread(target=create_livechat_conversion_analytics_excel, args=(
                start_date, end_date, channel_list, bot_pk, email_id,), daemon=True)
            thread.start()
        elif type_of_analytics == "dropoff_conversion_analytics":
            thread = threading.Thread(target=create_dropoff_conversion_analytics_excel, args=(
                start_date, end_date, channel_list, bot_pk, email_id, True, selected_language,), daemon=True)
            thread.start()
        elif type_of_analytics == "whatsapp_block_analytics":
            thread = threading.Thread(target=create_whatsapp_block_analytics_excel, args=(
                start_date, end_date, block_type, bot_pk, email_id, True,), daemon=True)
            thread.start()
        elif type_of_analytics == "catalogue_conversion_analytics":
            thread = threading.Thread(target=create_whatsapp_catalogue_analytics_csv, args=(
                start_date, end_date, is_catalogue_purchased, bot_pk, email_id, True,), daemon=True)
            thread.start()
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()

        logger.error("start_thread_of_conversion_analytics_data_via_mail: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
