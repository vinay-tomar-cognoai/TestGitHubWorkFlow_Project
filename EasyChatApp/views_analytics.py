import copy

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import FileResponse
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.conf import settings

from django.utils.encoding import smart_str
from django.http import HttpResponseNotFound
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_analytics import *
from EasyChatApp.utils_api_analytics import *
from EasyChatApp.utils_bot import get_supported_languages
from EasyChatApp.utils_external_apis import *
from EasyChatApp.utils_userflow import create_user_flow_with_excel, create_bot_with_excel, create_flow_using_excel
from EasyChatApp.static_dummy_data import *
from EasyChatApp.utils_conversion_analytics import *
from EasyChatApp.utils_validation import EasyChatFileValidation, EasyChatInputValidation
from EasyChatApp.utils_execute_query import get_bot_info_object
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses
from EasyChatApp.utils_voicebot import get_call_recording_url

import sys
import os
import json
import datetime
import operator
import xlrd
import math
import ast
import logging
import threading
import urllib
from collections import OrderedDict
from os import path
from orderedset import OrderedSet
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.db.models import Sum
from sklearn.feature_extraction import text as sklearn_text
import time
import urllib.parse

logger = logging.getLogger(__name__)

ensure_element_tree(xlrd)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def MIS_dashboard(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            if not check_access_for_user(request.user, None, "Message History Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")

            validation_obj = EasyChatInputValidation()

            bot_id = None
            if 'bot_id' in request.GET:
                bot_id = request.GET['bot_id']
                bot_id = validation_obj.remo_html_from_string(bot_id)

            channel_name = None
            if 'channel_name' in request.GET:
                channel_name = request.GET['channel_name']
                channel_name = validation_obj.remo_html_from_string(
                    channel_name)

            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            bot_objs = Bot.objects.filter(
                users__in=[user_obj], is_deleted=False)

            if bot_id != None:
                for bot_obj in bot_objs:
                    if bot_obj.pk == int(bot_id):
                        bot_objs = [Bot.objects.get(
                            pk=int(bot_id), is_deleted=False)]
                        if not check_access_for_user(request.user, bot_id, "Message History Related"):
                            return HttpResponseNotFound("You do not have access to this page")

            # modified_mis_objects_list = MISDashboard.objects.filter(
            #     bot__in=bot_objs).filter(~Q(intent_name="INFLOW-INTENT")).order_by('-date')

            modified_mis_objects_list = MISDashboard.objects.filter(
                bot__in=bot_objs)

            if channel_name != None:
                modified_mis_objects_list = modified_mis_objects_list.filter(
                    channel_name=channel_name)

            paginator = Paginator(
                modified_mis_objects_list, MAX_MESSAGE_PER_PAGE)
            page = request.GET.get('page')

            try:
                modified_mis_objects_list = paginator.page(page)
            except PageNotAnInteger:
                modified_mis_objects_list = paginator.page(1)
            except EmptyPage:
                modified_mis_objects_list = paginator.page(paginator.num_pages)

            return render(request, "EasyChatApp/analytics/mis_dashboard.html", {
                "mis_objects_list": modified_mis_objects_list
            })
        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error MIS_dashboard! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
        # return HttpResponseNotFound(INVALID_REQUEST)
        return render(request, 'EasyChatApp/error_500.html')


def Analytics(request):  # noqa: N802
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        return redirect("/chat/revised-analytics")
    else:
        return HttpResponseRedirect("/chat/login")


def RevisedAnalytics(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            dropdown_language = "en"
            if "selected_language" in request.GET:
                dropdown_language = request.GET["selected_language"]
            if not check_access_for_user(request.user, None, "Analytics Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")

            # bot_list = Bot.objects.filter(is_uat=True, users__in=[
            #                              user_obj], is_deleted=False)
            last_month_start_datetime = (
                datetime.datetime.today() - datetime.timedelta(30)).date()
            last3_month_start_datetime = (
                datetime.datetime.today() - datetime.timedelta(3 * 30)).date()

            default_analytics_start_datetime = (
                datetime.datetime.today() - datetime.timedelta(7)).date()

            default_analytics_end_datetime = datetime.datetime.today().date()
            bot_list = user_obj.get_related_bot_objs_for_access_type(
                "Analytics Related")

            if "bot_id" in request.GET:
                selected_bot_id = request.GET.getlist("bot_id")[0]
                if not check_access_for_user(request.user, selected_bot_id, "Analytics Related"):
                    return HttpResponseNotFound("You do not have access to this page")
            else:
                return HttpResponseNotFound("You haven't provided valid bot id.")

            manage_intents_permission = False
            if check_access_for_user(request.user, selected_bot_id, "Intent Related"):
                manage_intents_permission = True

            selected_bot_id = int(selected_bot_id)
            selected_bot_obj = Bot.objects.get(
                pk=selected_bot_id, is_deleted=False)
            intent_categories = Category.objects.filter(bot=selected_bot_obj)

            # getting supported channel list
            bot_channel_objs = BotChannel.objects.filter(bot=selected_bot_obj)

            dict_of_supported_languages_channel_wise, master_language_list = get_dict_of_channel_wise_supported_languages(
                bot_channel_objs)
            string_of_supported_languages_channel_wise = get_supported_languages_stringified_channel_wise(
                dict_of_supported_languages_channel_wise)

            go_live_date = selected_bot_obj.go_live_date

            supported_language = selected_bot_obj.languages_supported.all()

            if selected_bot_obj.static_analytics:

                label_list = []

                for index in range(0, 7):
                    label_list.append(
                        str(default_analytics_start_datetime + datetime.timedelta(index)))

                if dropdown_language == "en":
                    return render(request, 'EasyChatApp/analytics/static_analytics_english.html', {
                        'bot_list': bot_list,
                        "DEFAULT_ANALYTICS_START_DATETIME": default_analytics_start_datetime,
                        "DEFAULT_ANALYTICS_END_DATETIME": default_analytics_end_datetime,
                        "LAST_MONTH_START_DATETIME": last_month_start_datetime,
                        "LAST3_MONTH_START_DATETIME": last3_month_start_datetime,
                        "go_live_date": go_live_date,
                        "selected_bot_id": selected_bot_id,
                        "selected_bot_obj": selected_bot_obj,
                        "label_list": label_list,
                        "intent_categories": intent_categories
                    })

                else:
                    return render(request, 'EasyChatApp/analytics/static_analytics_hindi.html', {
                        'bot_list': bot_list,
                        "DEFAULT_ANALYTICS_START_DATETIME": default_analytics_start_datetime,
                        "DEFAULT_ANALYTICS_END_DATETIME": default_analytics_end_datetime,
                        "LAST_MONTH_START_DATETIME": last_month_start_datetime,
                        "LAST3_MONTH_START_DATETIME": last3_month_start_datetime,
                        "go_live_date": go_live_date,
                        "selected_bot_id": selected_bot_id,
                        "selected_bot_obj": selected_bot_obj,
                        "label_list": label_list,
                        "intent_categories": intent_categories
                    })

            return render(request, 'EasyChatApp/analytics/revised_analytics.html', {
                'bot_list': bot_list,
                "DEFAULT_ANALYTICS_START_DATETIME": default_analytics_start_datetime,
                "DEFAULT_ANALYTICS_END_DATETIME": default_analytics_end_datetime,
                "LAST_MONTH_START_DATETIME": last_month_start_datetime,
                "LAST3_MONTH_START_DATETIME": last3_month_start_datetime,
                "go_live_date": go_live_date,
                "selected_bot_id": selected_bot_id,
                "selected_bot_obj": selected_bot_obj,
                "manage_intents_permission": manage_intents_permission,
                "email_id": request.user.email,
                "intent_categories": intent_categories,
                "bot_channel_objs": bot_channel_objs,
                "string_of_supported_languages_channel_wise": string_of_supported_languages_channel_wise,
                "master_language_list": master_language_list,
                "supported_language": supported_language
            })
        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("RevisedAnalytics %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(selected_bot_id)})
        # return HttpResponseNotFound(INVALID_REQUEST)
        return render(request, 'EasyChatApp/error_500.html')


def ConversionAnalytics(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if not check_access_for_user(request.user, None, "Conversion Analytics Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")

            last_month_start_datetime = (
                datetime.datetime.today() - datetime.timedelta(30)).date()
            last3_month_start_datetime = (
                datetime.datetime.today() - datetime.timedelta(3 * 30)).date()

            default_analytics_start_datetime = (
                datetime.datetime.today() - datetime.timedelta(7)).date()

            default_analytics_end_datetime = datetime.datetime.today().date()

            bot_list = user_obj.get_related_bot_objs_for_access_type(
                "Conversion Analytics Related")

            if "bot_id" in request.GET:
                selected_bot_id = request.GET.getlist("bot_id")[0]
                if not check_access_for_user(request.user, selected_bot_id, "Conversion Analytics Related"):
                    return HttpResponseNotFound("You do not have access to this page")
            else:
                return HttpResponseNotFound("You haven't provided valid bot id.")

            selected_bot_id = int(selected_bot_id)
            selected_bot_obj = Bot.objects.get(
                pk=selected_bot_id, is_deleted=False)

            bot_info_obj = get_bot_info_object(selected_bot_obj)

            if bot_info_obj and bot_info_obj.static_conversion_analytics:
                web_page_source_objs = STATIC_EASYCHAT_CONVERSION_TRAFFIC_ANALYTICS_WEB_SOURCES_DUMMY_DATA
            else:
                web_page_source_objs = list(TrafficSources.objects.filter(bot=selected_bot_obj).values_list(
                    'web_page_source', flat=True).exclude(web_page_source__isnull=True).exclude(web_page_source="").distinct())

            go_live_date = selected_bot_obj.go_live_date

            channel_list = get_channel_list(Channel)

            supported_language = selected_bot_obj.languages_supported.all()

            return render(request, 'EasyChatApp/analytics/conversion_analytics.html', {
                'bot_list': bot_list,
                "DEFAULT_ANALYTICS_START_DATETIME": default_analytics_start_datetime,
                "DEFAULT_ANALYTICS_END_DATETIME": default_analytics_end_datetime,
                "LAST_MONTH_START_DATETIME": last_month_start_datetime,
                "LAST3_MONTH_START_DATETIME": last3_month_start_datetime,
                "go_live_date": go_live_date,
                "selected_bot_id": selected_bot_id,
                "selected_bot_obj": selected_bot_obj,
                "email_id": request.user.email,
                "web_page_source_objs": web_page_source_objs,
                "channel_list": channel_list,
                "supported_language": supported_language
            })
        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ConversionAnalytics %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(selected_bot_id)})
        # return HttpResponseNotFound(INVALID_REQUEST)
        return render(request, 'EasyChatApp/error_500.html')


def MessageHistory(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            sentiment_list = ['Anger', 'Fear', 'Happy', 'Hate',
                              'Love', 'Neutral', 'Sadness', 'Surprise', 'Worry']
            selected_bot_obj = ""
            bot_objs = ""
            message_history_list = ""
            end_date = ""
            start_date = ""
            filter_flag = False
            user_obj = request.user
            manage_intents_permission = False

            config_obj = Config.objects.all().order_by("pk")[0]

            if not check_access_for_user(request.user, None, "Message History Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")

            validation_obj = EasyChatInputValidation()
            bot_objs = user_obj.get_related_bot_objs_for_access_type(
                "Message History Related")
            bot_id = None
            if 'bot_id' in request.GET:
                bot_id = request.GET['bot_id']
                bot_id = validation_obj.remo_html_from_string(bot_id)

                filter_type = None
                start_date = None
                end_date = None
                show_start_date = datetime.datetime.now().strftime('%m/%d/%Y')
                show_start_time = "12 : 00 AM"
                show_end_date = datetime.datetime.now().strftime('%m/%d/%Y')
                show_end_time = "11 : 59 PM"
                if 'filter_type' in request.GET:
                    filter_type = request.GET['filter_type']
                    filter_flag = True
                    if filter_type == "1":
                        start_date = (datetime.datetime.now() -
                                      datetime.timedelta(7)).date()
                        end_date = datetime.datetime.now().date()
                    elif filter_type == "2":
                        start_date = (datetime.datetime.now() -
                                      datetime.timedelta(30)).date()
                        end_date = datetime.datetime.now().date()
                    elif filter_type == "3":
                        start_date = (datetime.datetime.now() -
                                      datetime.timedelta(90)).date()
                        end_date = datetime.datetime.now().date()
                    elif filter_type == "5":
                        start_date = datetime.datetime.strptime(
                            request.GET['start_date'].replace("_", " "), '%m/%d/%Y %I:%M%p')
                        end_date = datetime.datetime.strptime(
                            request.GET['end_date'].replace("_", " "), '%m/%d/%Y %I:%M%p')
                        show_start_date = request.GET['start_date'].split("_")[
                            0].strip()
                        show_end_date = request.GET['end_date'].split("_")[
                            0].strip()
                        start_time = request.GET['start_date'].split("_")[
                            1].strip()
                        show_start_time = start_time[0: 2] + " : " + \
                            start_time[3: 5] + " " + start_time[5:7]
                        end_time = request.GET['end_date'].split("_")[
                            1].strip()
                        show_end_time = end_time[0: 2] + " : " + \
                            end_time[3: 5] + " " + end_time[5:7]

                channel_name = None
                if 'channel_name' in request.GET:
                    filter_flag = True
                    channel_name = request.GET['channel_name']
                    channel_name = validation_obj.remo_html_from_string(
                        channel_name)

                no_of_records_per_page = MAX_MESSAGE_PER_PAGE
                if 'no_of_records_per_page' in request.GET:
                    no_of_records_per_page = request.GET['no_of_records_per_page']
                    no_of_records_per_page = int(no_of_records_per_page)

                low_percent = None
                high_percent = None
                if 'low_percent' in request.GET and 'high_percent' in request.GET:
                    low_percent = request.GET['low_percent']
                    low_percent = int(low_percent)
                    high_percent = request.GET['high_percent']
                    high_percent = int(high_percent)

                selected_channels = []
                if "channels" in request.GET:
                    selected_channels = request.GET["channels"]
                    selected_channels = validation_obj.remo_html_from_string(
                        selected_channels)
                    selected_channels = selected_channels.split()

                intent_pk = None
                if 'intent_pk' in request.GET:
                    intent_pk = request.GET['intent_pk']
                    intent_pk = validation_obj.remo_html_from_string(intent_pk)

                sentiment = None
                if 'sentiment' in request.GET:
                    sentiment = request.GET['sentiment']
                    sentiment = validation_obj.remo_html_from_string(sentiment)

                location_city = None
                if 'location_city' in request.GET:
                    location_city = request.GET['location_city']
                    location_city = validation_obj.remo_html_from_string(
                        location_city)
                    location_city = location_city.split()
                    location_city = [city.replace("_", " ")
                                     for city in location_city]

                location_state = None
                if 'location_state' in request.GET:
                    location_state = request.GET['location_state']
                    location_state = validation_obj.remo_html_from_string(
                        location_state)
                    location_state = location_state.split()
                    location_state = [state.replace(
                        "_", " ") for state in location_state]

                location_pincode = None
                if 'location_pincode' in request.GET:
                    location_pincode = request.GET['location_pincode']
                    location_pincode = validation_obj.remo_html_from_string(
                        location_pincode)
                    location_pincode = location_pincode.split()
                    location_pincode = [
                        pincode for pincode in location_pincode]

                selected_bot_obj = None
                if bot_id != None:
                    selected_bot_obj = Bot.objects.get(
                        pk=int(bot_id), is_deleted=False, is_uat=True)

                    if not check_access_for_user(request.user, bot_id, "Message History Related"):
                        return HttpResponseNotFound("You do not have access to this page")

                message_history_list = []
                if selected_bot_obj != None:
                    message_history_list = MISDashboard.objects.filter(
                        bot__in=[selected_bot_obj])
                else:
                    message_history_list = MISDashboard.objects.filter(
                        bot__in=bot_objs)

                query_type = None
                if "query_type" in request.GET:
                    query_type = request.GET["query_type"]
                    filter_flag = True
                    if query_type == "unanswered":
                        message_history_list = message_history_list.filter(
                            intent_name=None, is_intiuitive_query=False, is_unidentified_query=True).exclude(message_received="")
                        message_history_list = message_history_list.order_by(
                            "-date")

                    elif query_type == "answered":
                        message_history_list = message_history_list.exclude(intent_name=None).exclude(is_intiuitive_query=True).exclude(is_unidentified_query=True).exclude(message_received="").order_by('-date')
                    
                    elif query_type == "intuitive":
                        message_history_list = message_history_list.filter(intent_name=None,
                                                                           is_intiuitive_query=True).order_by('-date')

                    elif query_type == "type_in":
                        message_history_list = message_history_list.filter(is_manually_typed_query=True).order_by(
                            '-date')

                    elif query_type == "flagged":
                        message_history_list = message_history_list.exclude(match_percentage=-1).filter(
                            match_percentage__lte=config_obj.percentage_threshold_for_message_history,
                            flagged_queries_positive_type=None).order_by('-date')

                    elif query_type == "false_positive":
                        message_history_list = message_history_list.filter(flagged_queries_positive_type="1").order_by(
                            '-date')

                    elif query_type == "not_false_positive":
                        message_history_list = message_history_list.filter(flagged_queries_positive_type="2").order_by(
                            '-date')
                        message_history_list = message_history_list.filter(
                            intent_name=None, is_intiuitive_query=True).order_by('-date')

                feedback_type = None
                if "feedback_type" in request.GET:
                    feedback_type = request.GET["feedback_type"]
                    filter_flag = True
                    if feedback_type == "no_feedback":
                        message_history_list = message_history_list.filter(
                            is_helpful_field=0)

                    elif feedback_type == "positive_feedback":
                        message_history_list = message_history_list.filter(
                            is_helpful_field=1)

                    elif feedback_type == "negative_feedback":
                        message_history_list = message_history_list.filter(
                            is_helpful_field=-1)

                if start_date != None:
                    if filter_type == "5":
                        message_history_list = message_history_list.filter(
                            date__gte=start_date)
                    else:
                        message_history_list = message_history_list.filter(
                            creation_date__gte=start_date)

                if end_date != None:
                    if filter_type == "5":
                        message_history_list = message_history_list.filter(
                            date__lte=end_date)
                    else:
                        message_history_list = message_history_list.filter(
                            creation_date__lte=end_date)

                if channel_name != None:
                    message_history_list = message_history_list.filter(
                        channel_name=channel_name)

                if selected_channels != []:
                    message_history_list = message_history_list.filter(
                        channel_name__in=selected_channels)
                    filter_flag = True

                if intent_pk != None:
                    intent_obj = Intent.objects.get(
                        pk=int(intent_pk), is_hidden=False)
                    message_history_list = message_history_list.filter(
                        intent_recognized=intent_obj)

                if sentiment != None:
                    message_history_list = message_history_list.filter(
                        sentiment=sentiment)

                if location_city != None:
                    message_history_list = message_history_list.filter(
                        client_city__in=location_city)
                    filter_flag = True

                if location_state != None:
                    message_history_list = message_history_list.filter(
                        client_state__in=location_state)
                    filter_flag = True

                if location_pincode != None:
                    message_history_list = message_history_list.filter(
                        client_pincode__in=location_pincode)
                    filter_flag = True

                if "timestamp_date" in request.GET:
                    timestamp_date = request.GET["timestamp_date"]
                    timestamp_start_time = ""
                    timestamp_end_time = ""
                    if "timestamp_start_time" in request.GET:
                        timestamp_start_time = request.GET[
                            "timestamp_start_time"]
                    if "timestamp_end_time" in request.GET:
                        timestamp_end_time = request.GET["timestamp_end_time"]
                    if timestamp_start_time != "" and timestamp_end_time != "":
                        start_date_time = timestamp_date + " " + timestamp_start_time
                        start_date_time = datetime.datetime.strptime(
                            start_date_time, "%Y-%m-%d %H:%M")
                        end_date_time = timestamp_date + " " + timestamp_end_time
                        end_date_time = datetime.datetime.strptime(
                            end_date_time, "%Y-%m-%d %H:%M")
                        message_history_list = message_history_list.filter(
                            date__gte=start_date_time, date__lte=end_date_time)

                client_city_list = list(MISDashboard.objects.filter(bot_id=bot_id).order_by().values_list(
                    'client_city', flat=True).exclude(client_city__isnull=True).exclude(client_city="").distinct())
                client_state_list = list(MISDashboard.objects.filter(bot_id=bot_id).order_by().values_list(
                    'client_state', flat=True).exclude(client_state__isnull=True).exclude(client_state="").distinct())
                client_pincode_list = list(MISDashboard.objects.filter(bot_id=bot_id).order_by().values_list(
                    'client_pincode', flat=True).exclude(client_pincode__isnull=True).exclude(
                    client_pincode="").distinct())

                bot_flow_termination_keywords = []
                is_percentage_match_enabled = False
                is_flagged_queries_enabled = False
                enable_flagged_queries_status = False

                bot_metadata = ""

                if selected_bot_obj != None:
                    bot_flow_termination_keywords = (json.loads(
                        selected_bot_obj.flow_termination_keywords))['items']
                    bot_flow_termination_keywords = list(
                        map(lambda x: x.lower(), bot_flow_termination_keywords))
                    bot_info = BotInfo.objects.get(bot=selected_bot_obj)
                    bot_metadata = json.loads(bot_info.console_meta_data)

                    is_percentage_match_enabled = bot_info.is_percentage_match_enabled

                    # percent match filter based on toggle
                    if is_percentage_match_enabled and low_percent != None and high_percent != None:
                        message_history_list = message_history_list.filter(
                            match_percentage__gte=low_percent, match_percentage__lte=high_percent)
                        filter_flag = True

                    is_flagged_queries_enabled = True
                    if is_percentage_match_enabled:
                        for data in bot_metadata["lead_data_cols"]:
                            if (data["name"] == "variation_responsible" or data["name"] == "percentage_match") and data["selected"] == "false":
                                is_flagged_queries_enabled = False

                    enable_flagged_queries_status = bot_info.enable_flagged_queries_status

                total_entries = message_history_list.count()
                average_accuracy_percentage = ""
                if is_percentage_match_enabled:
                    average_accuracy_percentage = message_history_list.exclude(match_percentage=-1).aggregate(
                        average_percentage=Avg('match_percentage'))
                    average_accuracy_percentage = message_history_list.exclude(
                        match_percentage=-1).aggregate(average_percentage=Avg('match_percentage'))

                    if average_accuracy_percentage["average_percentage"] != None:
                        average_accuracy_percentage = round(
                            average_accuracy_percentage["average_percentage"])

                    try:
                        average_accuracy_percentage = int(
                            average_accuracy_percentage)
                    except:
                        average_accuracy_percentage = ""

                template_to_render = 'EasyChatApp/analytics/message_history.html'
                if (selected_bot_obj.static_analytics):
                    message_history_list = STATIC_EASYCHAT_MESSAGE_HISTORY_DUMMY_DATA
                    bot_metadata = STATIC_BOT_META_DATA
                    template_to_render = 'EasyChatApp/analytics/static_message_history.html'

                paginator = Paginator(
                    message_history_list, no_of_records_per_page)
                page = request.GET.get('page')

                try:
                    message_history_list = paginator.page(page)
                except PageNotAnInteger:
                    message_history_list = paginator.page(1)
                except EmptyPage:
                    message_history_list = paginator.page(paginator.num_pages)

                end_date = datetime.datetime.now()
                start_date = end_date - datetime.timedelta(30)

            if check_access_for_user(request.user, bot_id, "Intent Related"):
                manage_intents_permission = True

            # logger.error(selected_channels, extra={'AppName': 'EasyChat', 'user_id': str(
            #     request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            channel_list = get_channel_list(Channel)

            return render(request, template_to_render, {
                "selected_bot_obj": selected_bot_obj,
                "bot_objs": bot_objs,
                "message_history_list": message_history_list,
                "end_date": end_date,
                "start_date": start_date,
                "filter_flag": filter_flag,
                "sentiment_list": sentiment_list,
                "manage_intents_permission": manage_intents_permission,
                "client_city_list": client_city_list,
                "client_state_list": client_state_list,
                "client_pincode_list": client_pincode_list,
                "bot_flow_termination_keywords": bot_flow_termination_keywords,
                "location_city": location_city,
                "location_state": location_state,
                "location_pincode": location_pincode,
                "query_type": query_type,
                "feedback_type": feedback_type,
                "selected_channels": selected_channels,
                "sentiment": sentiment,
                "filter_type": filter_type,
                "show_start_date": show_start_date,
                "show_start_time": show_start_time,
                "show_end_date": show_end_date,
                "show_end_time": show_end_time,
                "channel_list": channel_list,
                "is_percentage_match_enabled": is_percentage_match_enabled,
                "average_accuracy_percentage": average_accuracy_percentage,
                "total_entries": total_entries,
                "bot_metadata": bot_metadata,
                "is_flagged_queries_enabled": is_flagged_queries_enabled,
                "enable_flagged_queries_status": enable_flagged_queries_status,
                "config_obj": config_obj
            })
        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("MessageHistory %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
        # return HttpResponseNotFound(INVALID_REQUEST)
        return render(request, 'EasyChatApp/error_500.html')


"""

SaveBotLeadTableMetadataAPI() : return all active metadata objs for message history w.r.t bot

"""


class SaveBotLeadTableMetadataAPI(APIView):
    permission_classes = [IsAuthenticated]

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            selected_bot_obj = ""
            lead_data_cols = data['lead_data_cols'],
            bot_id = data['bot_pk']
            bot_info_obj = ""
            if bot_id != None:
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_id), is_deleted=False, is_uat=True)
                bot_info_obj = BotInfo.objects.get(bot=selected_bot_obj)

            console_meta_data = {}
            console_meta_data['lead_data_cols'] = lead_data_cols[0]

            bot_info_obj.console_meta_data = json.dumps(console_meta_data)
            bot_info_obj.save()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveAgentLeadTableMetadataAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveBotLeadTableMetadata = SaveBotLeadTableMetadataAPI.as_view()


class UserDetailsAPI(APIView):  # noqa: N802
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {
            "status_code": 500,
            "message_history": []
        }
        try:
            user_obj = request.user
            if not check_access_for_user(request.user, None, "Message History Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            data = DecryptVariable(request.POST['data'])
            data = json.loads(data)
            user_id = data["user_id"]
            bot_pk = data["bot_pk"]
            bot_obj = Bot.objects.get(pk=bot_pk, is_deleted=False)
            if not bot_obj or user_obj not in bot_obj.users.all():
                return HttpResponseNotFound("You do not have access to this page")
            message_history_list = MISDashboard.objects.filter(
                bot=bot_obj, user_id=user_id).order_by('-date')
            message_history = []
            session_id_wise_data = {}
            for message in message_history_list:
                widget_type = ''
                widget_data = []
                widget_language_tuned_text = {}
                is_single_timepicker = False
                is_multi_timepicker = False
                is_single_datepicker = False
                is_multi_datepicker = False
                sent_image = []
                sent_video = []
                pdf_search_results = []
                order_of_response = bot_obj.default_order_of_response[1:-1].replace('"', '').split(',')
                if len(order_of_response) < 2:
                    order_of_response = ['text', 'image', 'table', 'video', 'link_cards', 'intent_level_feedback', 'quick_recommendations', 'drop_down', 'date_picker', 'checkbox', 'radio_button', 'range_slider', 'form', 'time_picker', 'calendar_picker', 'file_attach', 'video_record', 'phone_number']
                sent_table = []
                sent_card = []
                choices_list = ""
                campaign_qr_cta = {}
                attach_file_src = ""
                file_name = ""
                is_campaign = False
                document_name = ""
                channel_name = message.get_channel_name()
                message_sent = message.get_bot_response()
                language_template_obj = RequiredBotTemplate.objects.filter(bot=bot_obj, language=message.selected_language).first()
                if language_template_obj is None:
                    language_template_obj = RequiredBotTemplate.objects.filter(bot=bot_obj, language__lang="en").first()
                bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()
                widget_language_tuned_text["unable_to_load_text"] = language_template_obj.general_text.split("$$$")[17]
                if message.response_json:
                    response_json = json.loads(message.response_json)
                    if 'is_campaign' in response_json['response'] and response_json['response']['is_campaign']:
                        is_campaign = True
                    if is_campaign:
                        if response_json['response']['is_video']:
                            sent_video = response_json['response']['video']
                        elif response_json['response']['is_image']:
                            sent_image = response_json['response']['image']
                        elif response_json['response']['is_document']:
                            sent_card = response_json['response']['document']
                            if response_json.get('response').get('document_name'):
                                document_name = response_json.get('response').get('document_name')
                        if response_json.get('response').get('is_cta'):
                            campaign_qr_cta['cta_text'] = response_json['response']['cta_text']
                        if response_json.get('response').get('is_callus'):
                            campaign_qr_cta['callus_text'] = response_json['response']['callus_text']
                        if response_json.get('response').get('is_qr'):
                            campaign_qr_cta['quick_reply'] = []
                            if response_json.get('response').get('template_qr_1'):
                                campaign_qr_cta['quick_reply'].append(response_json['response']['template_qr_1'])
                            if response_json.get('response').get('template_qr_2'):
                                campaign_qr_cta['quick_reply'].append(response_json['response']['template_qr_2'])
                            if response_json.get('response').get('template_qr_3'):
                                campaign_qr_cta['quick_reply'].append(response_json['response']['template_qr_3'])
                        if response_json.get('response').get('is_header'):
                            message_sent = '<b>' + response_json.get('response').get('header_text') + '</b><br><br>' + message_sent
                        if response_json.get('response').get('is_footer'):
                            message_sent = message_sent + '<br><br><i><p style="color: gray">' + response_json.get('response').get('footer_text') + '</p></i>'
                        campaign_qr_cta['type_of_first_cta_button'] = response_json.get('response').get('type_of_first_cta_button')
                    else:
                        if channel_name in ['Web', 'iOS', 'Android']:
                            if ('is_single_timepicker' in response_json['response']['text_response']['modes'] and response_json['response']['text_response']['modes']['is_single_timepicker'] == 'true'):
                                is_single_timepicker = True
                            if ('is_multi_timepicker' in response_json['response']['text_response']['modes'] and response_json['response']['text_response']['modes']['is_multi_timepicker'] == 'true'):
                                is_multi_timepicker = True
                            if ('is_single_datepicker' in response_json['response']['text_response']['modes'] and response_json['response']['text_response']['modes']['is_single_datepicker'] == 'true'):
                                is_single_datepicker = True
                            if ('is_multi_datepicker' in response_json['response']['text_response']['modes'] and response_json['response']['text_response']['modes']['is_multi_datepicker'] == 'true'):
                                is_multi_datepicker = True
                            widget_language_tuned_text["label_date"] = language_template_obj.widgets_response_text.split("$$$")[1]
                            widget_language_tuned_text["label_time"] = language_template_obj.widgets_response_text.split("$$$")[2]
                            widget_language_tuned_text["label_add"] = language_template_obj.widgets_response_text.split("$$$")[3]
                            widget_language_tuned_text["label_from"] = language_template_obj.widgets_response_text.split("$$$")[4]
                            widget_language_tuned_text["label_to"] = language_template_obj.widgets_response_text.split("$$$")[5]
                            if is_multi_timepicker and is_multi_datepicker:
                                widget_type = 'multi_date_time'
                            elif is_single_timepicker and is_single_datepicker:
                                widget_type = 'single_date_time'
                            elif is_single_timepicker and is_multi_datepicker:
                                widget_type = 'single_time_multi_date'
                            elif is_single_datepicker and is_multi_timepicker:
                                widget_type = 'single_date_multi_time'
                            elif is_single_datepicker:
                                widget_type = 'single_date'
                            elif is_single_timepicker:
                                widget_type = 'single_time'
                            elif is_multi_timepicker:
                                widget_type = 'multi_time'
                            elif is_multi_datepicker:
                                widget_type = 'multi_date'
                            elif ('is_range_slider' in response_json['response']['text_response']['modes'] and response_json['response']['text_response']['modes']['is_range_slider'] == 'true'):
                                widget_type = 'is_range_slider'
                                widget_language_tuned_text["min_text"] = language_template_obj.date_range_picker_text.split("$$$")[7]
                                widget_language_tuned_text["max_text"] = language_template_obj.date_range_picker_text.split("$$$")[8]
                                widget_language_tuned_text["select_value_text"] = language_template_obj.date_range_picker_text.split("$$$")[10]
                                widget_language_tuned_text["selected_value_text"] = language_template_obj.date_range_picker_text.split("$$$")[11]
                                widget_data = response_json['response']['text_response']['modes_param']['range_slider_list'][0]['range_type']
                            elif ('is_create_form_allowed' in response_json['response']['text_response']['modes'] and response_json['response']['text_response']['modes']['is_create_form_allowed'] == 'true'):
                                widget_type = 'is_create_form_allowed'
                                widget_data.append(response_json['response']['text_response']['modes_param']['form_name'])
                                if message.selected_language.lang != "en":
                                    widget_data[0] = get_translated_text(
                                        widget_data[0], message.selected_language.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
                                widget_data.append(response_json['response']['text_response']['modes_param']['form_fields_list'])
                            elif ('is_video_recorder_allowed' in response_json['response']['text_response']['modes'] and response_json['response']['text_response']['modes']['is_video_recorder_allowed'] == 'true'):
                                widget_type = 'is_video_recorder_allowed'
                                widget_language_tuned_text["start_text"] = language_template_obj.start_text
                                widget_language_tuned_text["cancel_text"] = language_template_obj.cancel_text
                            elif ('is_drop_down' in response_json['response']['text_response']['modes'] and response_json['response']['text_response']['modes']['is_drop_down'] == 'true'):
                                widget_type = 'is_drop_down'
                                widget_language_tuned_text["dropdown_text"] = language_template_obj.dropdown_text
                                widget_data = response_json['response']['text_response']['modes_param']['drop_down_choices']
                                if message.selected_language.lang != "en":
                                    translated_drop_down_choices = []
                                    for drop_down in widget_data:
                                        translated_drop_down_choices.append(get_translated_text(
                                            drop_down, message.selected_language.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj))

                                    widget_data = translated_drop_down_choices
                            elif ('is_check_box' in response_json['response']['text_response']['modes'] and response_json['response']['text_response']['modes']['is_check_box'] == 'true'):
                                widget_type = 'is_check_box'
                                widget_data = response_json['response']['text_response']['modes_param']['check_box_choices']
                                if message.selected_language.lang != "en":
                                    translated_check_box_choices = []
                                    for checkbox in widget_data:
                                        translated_check_box_choices.append(get_translated_text(
                                            checkbox, message.selected_language.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj))

                                    widget_data = translated_check_box_choices
                            elif ('is_radio_button' in response_json['response']['text_response']['modes'] and response_json['response']['text_response']['modes']['is_radio_button'] == 'true'):
                                widget_type = 'is_radio_button'
                                widget_data = response_json['response']['text_response']['modes_param']['radio_button_choices']
                                if message.selected_language.lang != "en":
                                    translated_radio_button_choices = []
                                    for radio_button in widget_data:
                                        translated_radio_button_choices.append(get_translated_text(
                                            radio_button, message.selected_language.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj))

                                    widget_data = translated_radio_button_choices
                            elif ('is_phone_widget_enabled' in response_json['response']['text_response']['modes'] and response_json['response']['text_response']['modes']['is_phone_widget_enabled'] == 'true'):
                                widget_type = 'is_phone_widget_enabled'
                                widget_language_tuned_text["enter_phone_text"] = language_template_obj.livechat_form_text.split("$$$")[4]
                                widget_data = response_json['response']['text_response']['modes_param']['country_code']
                        if channel_name not in ['GoogleHome', 'Alexa', 'Voice']:
                            if ('is_attachment_required' in response_json['response']['text_response']['modes'] and response_json['response']['text_response']['modes']['is_attachment_required'] == 'true'):
                                widget_type = 'is_attachment_required'
                                widget_data = response_json['response']['text_response']['modes_param']['choosen_file_type']
                                widget_language_tuned_text["file_attachment_text"] = language_template_obj.file_attachment_text
                                widget_language_tuned_text["file_size_limit_text"] = language_template_obj.file_size_limit_text
                        if channel_name in ['Web', 'iOS', 'Android']:
                            if ('tables' in response_json['response'] and response_json['response']['tables']):
                                sent_table = response_json['response']['tables']
                            
                            sent_image = response_json['response']['images']
                            sent_video = response_json['response']['videos']
                            sent_card = response_json['response']['cards']
                        if 'order_of_response' in response_json['response'] and len(response_json['response']['order_of_response']) > 0:
                            order_of_response = response_json['response']['order_of_response']
                    
                        if widget_type == 'is_create_form_allowed':
                            widget_data[1] = json.loads(widget_data[1])
                            for counter in range(len(widget_data[1])):
                                if message.selected_language.lang != "en":
                                    widget_data[1][counter]['label_name'] = get_translated_text(widget_data[1][counter]['label_name'], message.selected_language.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)

                                if widget_data[1][counter]['input_type'] == "file_attach":
                                    widget_language_tuned_text["file_attachment_text"] = language_template_obj.file_attachment_text
                                    widget_language_tuned_text["file_size_limit_text"] = language_template_obj.file_size_limit_text
                                elif widget_data[1][counter]['input_type'] == "dropdown_list":
                                    widget_language_tuned_text["dropdown_text"] = language_template_obj.dropdown_text
                                    if message.selected_language.lang != "en":
                                        translated_drop_down_choices = "$$$"
                                        for drop_down in widget_data[1][counter]['placeholder_or_options'].split("$$$"):
                                            translated_drop_down_choices += get_translated_text(
                                                drop_down, message.selected_language.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj) + "$$$"
                                        widget_data[1][counter]['placeholder_or_options'] = translated_drop_down_choices.strip("$")
                                elif widget_data[1][counter]['input_type'] == "range":
                                    widget_language_tuned_text["min_text"] = language_template_obj.date_range_picker_text.split("$$$")[7]
                                    widget_language_tuned_text["max_text"] = language_template_obj.date_range_picker_text.split("$$$")[8]
                                    widget_language_tuned_text["select_value_text"] = language_template_obj.date_range_picker_text.split("$$$")[10]
                                    widget_language_tuned_text["selected_value_text"] = language_template_obj.date_range_picker_text.split("$$$")[11]
                                elif widget_data[1][counter]['input_type'] == "checkbox":
                                    if message.selected_language.lang != "en":
                                        translated_choices = "$$$"
                                        for choice in widget_data[1][counter]['placeholder_or_options'].split("$$$"):
                                            translated_choices += get_translated_text(
                                                choice, message.selected_language.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj) + "$$$"
                                        widget_data[1][counter]['placeholder_or_options'] = translated_choices.strip("$")
                                elif widget_data[1][counter]['input_type'] == "radio":
                                    if message.selected_language.lang != "en":
                                        translated_radio_button_choices = "$$$"
                                        for radio_button_choice in widget_data[1][counter]['placeholder_or_options'].split("$$$"):
                                            translated_radio_button_choices += get_translated_text(
                                                radio_button_choice, message.selected_language.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj) + "$$$"
                                        widget_data[1][counter]['placeholder_or_options'] = translated_radio_button_choices.strip("$")
                                elif widget_data[1][counter]['input_type'] == "phone_number":
                                    widget_language_tuned_text["enter_phone_text"] = language_template_obj.livechat_form_text.split("$$$")[4]

                            widget_data[1] = json.dumps(widget_data[1])

                    if message.choices != "[]":
                        choices = ast.literal_eval(message.choices)
                        for choice_iterator in range(0, len(choices)):
                            choices_list += choices[choice_iterator]["display"]
                            if choice_iterator < len(choices) - 1:
                                choices_list += ","
                    if 'pdf_search_results' in response_json['response']:
                        pdf_search_results = response_json['response']['pdf_search_results']
                        widget_language_tuned_text["pdf_view_document_text"] = language_template_obj.pdf_view_document_text
                    if message.attachment:
                        try:
                            attach_file_src = message.attachment
                            file_key = message.attachment.split("/")[-2]
                            file_obj = EasyChatAppFileAccessManagement.objects.get(
                                key=file_key, is_expired=False)
                            file_name = file_obj.file_path.split("/")[-1]
                        except Exception as e:
                            file_name = str(attach_file_src).split("/")[-1]
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("UserDetailsAPI %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                if message.session_id not in session_id_wise_data:
                    session_id_wise_data[message.session_id] = message_history_list.filter(session_id=message.session_id).exclude(message_received="").count()

                message_history_dict = {
                    "pk": message.pk,
                    "message_received": message.get_message_received(),
                    "message_recommendation": message.recommendations,
                    "message_choices": choices_list,
                    "message_sent": message_sent,
                    "date_time": message.get_datetime(),
                    "channel_name": channel_name,
                    "widgets": message.widgets,
                    "form_data_widget": message.form_data_widget,
                    "attached_file_src": attach_file_src,
                    "attached_file_name": file_name,
                    "session_id": message.session_id,
                    "session_id_wise_data": session_id_wise_data,
                    "sent_image": sent_image,
                    "sent_video": sent_video,
                    "sent_card": sent_card,
                    "order_of_response": order_of_response,
                    'sent_table': sent_table,
                    'widget_type': widget_type,
                    'widget_data': widget_data,
                    "widget_language_tuned_text": widget_language_tuned_text,
                    'is_campaign': is_campaign,
                    'campaign_qr_cta': campaign_qr_cta,
                    'document_name': document_name,
                    "source_device": "Mobile" if message.is_mobile else "Desktop",
                    "pdf_search_results": pdf_search_results
                }

                if message.get_channel_name().strip().lower() == "whatsapp":
                    message_history_dict["whatsapp_menu_sections"] = message.get_whatsapp_menu_section_list()

                message_history.append(message_history_dict)

            response["status_code"] = 200
            response["message_history"] = message_history
            response["max_file_size_allowed"] = bot_obj.max_file_size_allowed
            response["user_call_recording"] = get_call_recording_url(
                user_id, bot_obj, Profile, VoiceBotProfileDetail)

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[ENGINE] %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response["status_code"] = 500
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UserDetails = UserDetailsAPI.as_view()


class GetMISUserAPI(APIView):  # noqa: N802
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {
            "status_code": 500,
        }
        try:
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if not check_access_for_user(request.user, None, "Message History Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            bot_objs = user_obj.get_related_bot_objs_for_access_type(
                "Message History Related")
            data = DecryptVariable(request.POST['data'])
            data = json.loads(data)
            user_id = data["user_id"]
            bot_id = data["bot_id"]

            bot_obj = Bot.objects.get(pk=int(bot_id))
            if bot_obj in bot_objs:
                message_history_list = []
                user_ids = []
                if bot_obj.masking_enabled:
                    hashed_user_id = hashlib.md5(user_id.encode()).hexdigest()
                    user_ids += (list(MISDashboard.objects.filter(
                        bot=bot_obj, user_id__icontains=hashed_user_id).values_list('user_id', flat=True).distinct()))
                user_ids += (list(MISDashboard.objects.filter(
                    bot=bot_obj, user_id__icontains=user_id).values_list('user_id', flat=True).distinct()))
                user_ids = list(set(user_ids))
                for user_id in user_ids:
                    mis_obj = MISDashboard.objects.filter(
                        bot=bot_obj, user_id=user_id).first()
                    message_history_list.append([user_id, mis_obj.get_bot_response()])

                if len(message_history_list):
                    response["status_code"] = 200
                    response["results"] = message_history_list
                else:
                    response["status_code"] = 404
                    response["results"] = []
            else:
                response["status_code"] = 404
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[ENGINE] %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
            response["status_code"] = 500
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetMISUser = GetMISUserAPI.as_view()


class FetchMessageHistoryAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:

            # data = request.data
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            # bot_objs = Bot.objects.filter(users__in=[user_obj])
            bot_objs = get_production_bots(user_obj)

            mis_dashboard_objs = MISDashboard.objects.filter(
                bot__in=bot_objs).order_by('-date')

            user_query = []
            bot_response = []
            time_sent = []
            intent_name = []
            user_id = []
            channel_name = []
            intent_pk_list = []

            for mis_dashboard_obj in mis_dashboard_objs:
                user_query.append(mis_dashboard_obj.get_message_received())
                bot_response.append(mis_dashboard_obj.get_bot_response())
                time_sent.append(
                    mis_dashboard_obj.date.strftime("%b %d %Y %H:%M:%S"))
                intent_name.append(mis_dashboard_obj.intent_name)
                intent_pk = -1
                if mis_dashboard_obj.intent_name != None:
                    try:
                        intent_pk = Intent.objects.get(
                            name=mis_dashboard_obj.intent_name, is_deleted=False, is_hidden=False).pk
                    except Exception:  # noqa: F841
                        pass

                user_id.append(mis_dashboard_obj.user_id)
                intent_pk_list.append(intent_pk)
                channel_name.append(mis_dashboard_obj.channel_name)

            response['user_id'] = user_id
            response['user_query'] = user_query
            response['bot_response'] = bot_response
            response['time_sent'] = time_sent
            response["intent_pk"] = intent_pk_list
            response['intent_name'] = intent_name
            response['channel'] = channel_name
            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("FetchMessageHistoryAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetMISDashboardAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500

        try:
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            # bot_objs = Bot.objects.filter(users__in=[user_obj])
            bot_objs = get_production_bots(user_obj)

            mis_objects = MISDashboard.objects.filter(
                ~Q(intent_name="INFLOW-INTENT")).filter(bot__in=bot_objs).order_by("-date")
            date_list = []
            user_id_list = []
            message_received_list = []
            bot_response_list = []
            intent_name_list = []
            channel_name_list = []
            intent_pk_list = []
            api_request_packet_list = []
            api_response_packet_list = []

            for mis_object in mis_objects:
                date_list.append(mis_object.date.strftime("%b %d %Y %H:%M:%S"))
                user_id_list.append(mis_object.user_id)
                message_received_list.append(mis_object.get_message_received())
                bot_response_list.append(mis_object.get_bot_response())
                intent_name_list.append(mis_object.intent_name)

                intent_pk = -1
                if mis_object.intent_name != None:
                    try:
                        intent_pk = Intent.objects.get(
                            name=str(mis_object.intent_name), is_deleted=False, is_hidden=False).pk
                    except Exception:  # noqa: F841
                        pass

                channel_name_list.append(mis_object.channel_name)
                intent_pk_list.append(intent_pk)
                api_request_packet_list.append(mis_object.api_request_packet)
                api_response_packet_list.append(mis_object.api_response_packet)

            response["date_list"] = date_list
            response["user_id_list"] = user_id_list
            response["message_received_list"] = message_received_list
            response["bot_response_list"] = bot_response_list
            response["intent_name_list"] = intent_name_list
            response["intent_pk_list"] = intent_pk_list
            response["channel_name_list"] = channel_name_list
            response["api_request_packet_list"] = api_request_packet_list
            response["api_response_packet_list"] = api_response_packet_list
            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetMISDashboardAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetUserDetailsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            # bot_objs = Bot.objects.filter(users__in=[user_obj])
            bot_objs = get_production_bots(user_obj)

            if not isinstance(data, dict):
                data = json.loads(data)

            user_id = data["user_id"]

            date_list = []
            user_id_list = []
            message_received_list = []
            bot_response_list = []
            intent_name_list = []
            channel_name_list = []

            mis_objects = MISDashboard.objects.filter(
                user_id=str(user_id), bot__in=bot_objs)

            for mis_object in mis_objects:
                date_str = mis_object.date.strftime("%b %d %Y %H:%M:%S")
                user_id = mis_object.user_id
                message_received = mis_object.get_message_received()
                bot_response = mis_object.get_bot_response()
                channel_name = mis_object.channel_name

                sentence = ""
                try:
                    intent_obj = Intent.objects.get(
                        name=str(mis_object.intent_name), is_deleted=False, is_hidden=False)
                    sentence = json.loads(intent_obj.training_data)["0"]
                except Exception:  # noqa: F841
                    sentence = mis_object.intent_name

                date_list.append(date_str)
                user_id_list.append(user_id)
                message_received_list.append(message_received)
                bot_response_list.append(bot_response)
                channel_name_list.append(channel_name)
                intent_name_list.append(sentence)

            response["date_list"] = date_list
            response["user_id_list"] = user_id_list
            response["message_received_list"] = message_received_list
            response["bot_response_list"] = bot_response_list
            response["intent_name_list"] = intent_name_list
            response["channel_name_list"] = channel_name_list
            response["api_request_packet_list"] = []
            response["api_response_packet_list"] = []
            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetUserDetailsAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetMonthlyAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            validation_obj = EasyChatInputValidation()

            bots_pk = json.loads(data['bots_pk'])
            bot_type = data['bot_type']
            bot_type = validation_obj.remo_html_from_string(bot_type)
            bot_objs = []

            if len(bots_pk) == 0:
                if bot_type == "prod":
                    bot_objs = get_production_bots(user_obj)
                else:
                    bot_objs = get_uat_bots(user_obj)
            else:
                if bot_type == "uat":
                    for bot_pk in bots_pk:
                        bot_objs.append(Bot.objects.get(
                            pk=bot_pk, is_deleted=False, is_uat=True))
                else:
                    for bot_pk in bots_pk:
                        bot_obj = Bot.objects.get(
                            pk=bot_pk, is_deleted=False, is_uat=True)
                        bot_slug = bot_obj.slug
                        bot_objs += list(Bot.objects.filter(
                            slug=bot_slug, is_deleted=False, is_active=True))

            number_to_str = ["", 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            months = Config.objects.all()[0].monthly_analytics_parameter
            month_user_dict = {}
            month_message_dict = {}
            month_intent_dict = {}
            month_list = []

            for month_iterator in range(months):
                datetime_obj = (datetime.date.today() -
                                datetime.timedelta((month_iterator)) * 365 / 12)
                year = str(datetime_obj.year)
                month = datetime_obj.month

                month_list.append(month)
                month_user_dict[number_to_str[month]] = get_monthly_count_of_users(
                    User, Bot, MISDashboard, year, month, username, bot_objs)
                month_message_dict[number_to_str[month]] = get_monthly_count_of_message(
                    User, Bot, MISDashboard, year, month, username, bot_objs)
                month_intent_dict[number_to_str[
                    month]] = get_monthly_count_of_messages_categorized_by_intent(
                    User, Bot, MISDashboard, year, month, username, bot_objs)

            month_list.sort()
            response["sorted_month_list"] = []
            for month in month_list:
                response["sorted_month_list"].append(number_to_str[month])

            response["user_frequency"] = month_user_dict
            response["message_frequency"] = month_message_dict
            response["intent_dict"] = month_intent_dict
            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetMonthlyAnalyticsAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetDailyAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500

        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            validation_obj = EasyChatInputValidation()

            bots_pk = json.loads(data['bots_pk'])
            bot_type = data['bot_type']
            bot_type = validation_obj.remo_html_from_string(bot_type)
            bot_objs = []

            if len(bots_pk) == 0:
                if bot_type == "prod":
                    bot_objs = get_production_bots(user_obj)
                else:
                    bot_objs = get_uat_bots(user_obj)
            else:
                if bot_type == "uat":
                    for bot_pk in bots_pk:
                        bot_objs.append(Bot.objects.get(
                            pk=bot_pk, is_deleted=False, is_uat=True))
                else:
                    for bot_pk in bots_pk:
                        bot_obj = Bot.objects.get(
                            pk=bot_pk, is_deleted=False, is_uat=True)
                        bot_slug = bot_obj.slug
                        bot_objs += list(Bot.objects.filter(
                            slug=bot_slug, is_deleted=False, is_active=True))

            no_days = Config.objects.all()[0].daily_analytics_parameter
            datetime_obj_list = []
            day_user_dict = {}
            day_message_dict = {}
            day_intent_dict = {}
            day_unanswered_message_dict = {}
            day_answered_dict = {}
            day_message_by_channel_dict = {}
            # no_grids = 5

            for days_iterator in range(no_days):
                datetime_obj = (datetime.date.today() -
                                datetime.timedelta(days_iterator))
                # year = str(datetime_obj.year)
                # month = str(datetime_obj.month)
                # day = str(datetime_obj.day)

                str_date = datetime_obj.strftime("%d-%m-%Y")

                datetime_obj_list.append(datetime_obj)
                day_user_dict[str(str_date)] = get_daily_count_of_users(
                    User, Bot, MISDashboard, UserSessionHealth, datetime_obj, username, bot_objs)
                day_message_dict[str(str_date)] = get_daily_count_of_messages(
                    MISDashboard, UserSessionHealth, datetime_obj, bot_objs)
                day_intent_dict[str(str_date)] = get_daily_count_of_messages_categorized_by_intent(
                    User, Bot, MISDashboard, datetime_obj, username, bot_objs)
                day_unanswered_message_dict[str(str_date)] = get_count_of_unanswered_messages(
                    User, Bot, MISDashboard, datetime_obj, username, bot_objs)
                day_answered_dict[str(str_date)] = get_count_of_answered_messages(
                    User, Bot, MISDashboard, datetime_obj, username, bot_objs)
                day_message_by_channel_dict[str(str_date)] = get_count_of_message_by_channel(
                    User, Bot, MISDashboard, Channel, datetime_obj, username, bot_objs)

            datetime_obj_list.sort()
            day_list = []
            for datetime_obj in datetime_obj_list:
                str_day = datetime_obj.strftime("%d-%m-%Y")
                day_list.append(str_day)

            bot_names = []
            for bot_obj in bot_objs:
                bot_names.append(bot_obj.name)

            response["sorted_day_list"] = day_list
            response["user_frequency"] = day_user_dict
            response["message_frequency"] = day_message_dict
            response["intent_frequency"] = day_intent_dict
            response["unanswered_message"] = day_unanswered_message_dict
            response["answered"] = day_answered_dict
            response["bot_names"] = bot_names
            response["message_by_channel"] = day_message_by_channel_dict
            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetDailyAnalyticsAPI %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetTopIntentsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        no_days = 15
        no_top_intents = Config.objects.all()[0].top_intents_parameter
        no_grids = 5

        try:
            username = request.user.username
            bot_objs = get_bot_objects_for_given_user(username, User, Bot)

            days_early_date = (datetime.date.today() -
                               datetime.timedelta(no_days))
            today_date = datetime.date.today()
            filtered_objs = MISDashboard.objects.all().filter(
                creation_date__gte=days_early_date).filter(creation_date__lte=today_date, bot__in=bot_objs)
            intent_frequency = {}

            for filtered_obj in filtered_objs:
                intent = filtered_obj.intent_name

                if intent == None or intent == "INFLOW-INTENT":
                    continue

                if intent in intent_frequency.keys():
                    intent_frequency[intent] += 1
                else:
                    intent_frequency[intent] = 1

            intent_frequency = sorted(intent_frequency.items(
            ), key=operator.itemgetter(1), reverse=True)
            no_unique_intents = len(intent_frequency)

            if no_unique_intents <= no_top_intents:
                no_top_intents = no_unique_intents

            intent_list = []
            intent_frequency_list = []
            for top_intent_iterator in range(no_top_intents):
                intent_list.append(
                    str(intent_frequency[top_intent_iterator][0]))
                intent_frequency_list.append(
                    intent_frequency[top_intent_iterator][1])

            response["intent_list"] = intent_list
            response["intent_frequency_list"] = intent_frequency_list
            response["intent_frequency_step_size"] = math.ceil(
                max(intent_frequency_list) / no_grids)
            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetTopIntentsAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


def generate_mail(filename, bot_name, email):
    from EasyChat import settings

    filename = settings.EASYCHAT_HOST_URL + "/" + filename
    pluralize_bot = "ChatBot"
    if bot_name == "All":
        pluralize_bot = "ChatBots"
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
            Dear Team,
        </p>
        <p>
            Following are the bot message history data for {} {}.
        </p>

        <p>Please click on the following to download the report: <a href="{}"style="background-color: darkorchid; border: 2px darkorchid; margin-left: 1em;border-radius: 5px;padding: 5px;color:whitesmoke; font-style: oblique;">Download</a></p>

        <p>Kindly connect with us incase of any issue.</p>
        <p>&nbsp;</p>""".format(bot_name, pluralize_bot, filename)

    config = get_developer_console_settings()

    body += config.custom_report_template_signature

    body += """</div></body>"""

    """With this function we send out our html email"""

    send_email_to_customer_via_awsses(
        email, "Message history exported data for ChatBot @CognoAI", body)


"""
@params FROM: Email id from which mail will be sent
@params TO: List of email ids to whom mail will be sent
@params message_as_string: Message as string
@params PASSWORD: account password
"""


# def send_mail(from_email_id, to_emai_id, message_as_string, from_email_id_password):
#     import smtplib
#     # # The actual sending of the e-mail
#     server = smtplib.SMTP('smtp.gmail.com:587')
#     # Credentials (if needed) for sending the mail
#     password = from_email_id_password
#     # Start tls handshaking
#     server.starttls()
#     # Login to server
#     server.login(from_email_id, password)
#     # Send mail
#     server.sendmail(from_email_id, to_emai_id, message_as_string)
#     # Close session
#     server.quit()


def send_email_to_client(is_keyword, keyword_str, filter_str, start_date, end_date, username, bot_name, email):
    if not os.path.isdir("files"):
        os.mkdir("files")

    if is_keyword == "Yes":
        keyword_list = [keyword.strip().lower()
                        for keyword in keyword_str.split(",")]
        file_path = export_mis_dashboard_with_filter_keywords(
            User, Bot, MISDashboard, keyword_list, username, bot_name)
    elif filter_str == "0":
        file_path = export_mis_dashboard_without_filter(
            User, Bot, MISDashboard, start_date, end_date, username, bot_name)
    else:
        file_path = export_mis_dashboard_with_filter_based_message(
            User, Bot, MISDashboard, start_date, end_date, username, bot_name)

    logger.info("Path for file created: " + str(file_path), extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return generate_mail(file_path, bot_name, email)


class ExportDataAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            bot_pk = requested_data["bot_pk"]
            export_path = None
            export_path_exist = None

            if requested_data["selected_filter_value"] == "1":
                yesterday_date = datetime.datetime.now() - timedelta(1)
                export_path = "/files/message-history/bot-" + \
                    str(bot_pk) + "/MessageHistoryLastOneDay_" + \
                    yesterday_date.strftime("%d-%m-%Y") + ".csv"
                # export_path_exist = path.exists(export_path[1:])
                export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
            elif requested_data["selected_filter_value"] == "2":
                start_date = datetime.datetime.now() - timedelta(7)
                end_date_in_file_name = datetime.datetime.now() - timedelta(1)
                export_path = "/files/message-history/bot-" + \
                    str(bot_pk) + "/MessageHistoryLastSevenDays_from_" + start_date.strftime(
                        "%d-%m-%Y") + "_to_" + end_date_in_file_name.strftime("%d-%m-%Y") + ".csv"
                # export_path_exist = path.exists(export_path[1:])
                export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
            elif requested_data["selected_filter_value"] == "3":
                start_date = datetime.datetime.now() - timedelta(30)
                end_date_in_file_name = datetime.datetime.now() - timedelta(1)
                export_path = "/files/message-history/bot-" + \
                    str(bot_pk) + "/MessageHistoryLastThirtyDays_from_" + start_date.strftime(
                        "%d-%m-%Y") + "_to_" + end_date_in_file_name.strftime("%d-%m-%Y") + ".csv"
                # export_path_exist = path.exists(export_path[1:])
                export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
            elif requested_data["selected_filter_value"] == "4":
                bot_obj = Bot.objects.get(pk=int(bot_pk))
                user_obj = User.objects.get(username=request.user.username)

                date_format = "%Y-%m-%d"
                end_date = datetime.datetime.strptime(
                    requested_data["enddate"], date_format).date()

                if end_date < bot_obj.created_datetime.date():
                    response["status"] = 400
                    response[
                        "message"] = "End date cannot be less than the bot creation date (%s)" % bot_obj.created_datetime.date(
                    ).strftime('%m/%d/%Y')
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                ExportMessageHistoryRequest.objects.create(
                    bot=bot_obj, request_type='message-history', user=user_obj, filter_param=json.dumps(requested_data))
                export_path = "request_saved"

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportDataAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class ExportNPSDataAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            bot_pk = requested_data["bot_pk"]
            export_path = None
            export_path_exist = None

            if requested_data["selected_filter_value"] == "1":
                export_path = "/files/csat-data/bot-" + \
                              str(bot_pk) + "/CSATDataLastOneDay_" + (datetime.datetime.today() - timedelta(1)).strftime("%d-%m-%Y") + ".csv"
                # export_path_exist = path.exists(export_path[1:])
                export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
            elif requested_data["selected_filter_value"] == "2":
                export_path = "/files/csat-data/bot-" + \
                              str(bot_pk) + "/CSATDataLastSevenDays_from_" + (datetime.datetime.today() - timedelta(7)).strftime("%d-%m-%Y") + "_to_" + (datetime.datetime.today() - timedelta(1)).strftime("%d-%m-%Y") + ".csv"
                # export_path_exist = path.exists(export_path[1:])
                export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
            elif requested_data["selected_filter_value"] == "3":
                export_path = "/files/csat-data/bot-" + \
                              str(bot_pk) + "/CSATDataLastThirtyDays_from_" + (datetime.datetime.today() - timedelta(30)).strftime("%d-%m-%Y") + "_to_" + (datetime.datetime.today() - timedelta(1)).strftime("%d-%m-%Y") + ".csv"
                # export_path_exist = path.exists(export_path[1:])
                export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
            elif requested_data["selected_filter_value"] == "4":
                bot_obj = Bot.objects.get(pk=int(bot_pk))
                user_obj = User.objects.get(username=request.user.username)
                ExportMessageHistoryRequest.objects.create(
                    bot=bot_obj, request_type='NPS', user=user_obj, filter_param=json.dumps(requested_data))
                export_path = "request_saved"

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportNPSDataAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ExportNPSData = ExportNPSDataAPI.as_view()


class CreateFAQBotAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        logger.info("CreateFAQBotAPI: Inside Training ChatBot Module", extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        try:
            user_obj = User.objects.get(username=str(request.user.username))

            data = request.data
            uploaded_file = data['my_file']
            bot_id_list = data["bot_id_list"]
            type_of_excel_file = data["type_of_excel_file"]

            bot_objs_list = [Bot.objects.get(pk=int(bot_id), is_deleted=False, is_uat=True) for bot_id in str(
                bot_id_list).split(",") if bot_id != ""]

            file_validation_obj = EasyChatFileValidation()

            if file_validation_obj.check_malicious_file(uploaded_file.name):
                response["status"] = 101
                response["message"] = "Kindly upload file in xls or xlsx format."
                return Response(data=response)

            file_name = get_dot_replaced_file_name(uploaded_file.name)

            path = default_storage.save(
                file_name, ContentFile(uploaded_file.read()))
            ext = path.split(".")[-1]
            is_allowed = True
            if ext.lower() not in ["xls", "xlsx"]:
                response["status"] = 101
                response["message"] = "Kindly upload file in xls or xlsx format."
                is_allowed = False

            if uploaded_file.name.find("EasyChatFlowSheetFormat") != -1 and str(type_of_excel_file) == "1":
                response["status"] = 400
                response["message"] = "Please upload FAQ excel sheet."
                return Response(data=response)

            if uploaded_file.name.find("EasyChatFAQSheetFormat") != -1 and str(type_of_excel_file) == "2":
                response["status"] = 401
                response["message"] = "Please upload UserFlow excel Sheet."
                return Response(data=response)

            if is_allowed:

                file_path = settings.MEDIA_ROOT + path

                response = {}

                excel_processing_obj = ExcelProcessingProgress.objects.create()
                excel_processing_obj.save()

                if str(type_of_excel_file) == "1":
                    t1 = threading.Thread(
                        target=create_bot_with_excel, args=(file_path, bot_objs_list, user_obj, excel_processing_obj))
                    t1.daemon = True
                    t1.start()
                else:
                    t1 = threading.Thread(
                        target=create_flow_using_excel, args=(file_path, bot_objs_list, user_obj, excel_processing_obj))
                    t1.daemon = True
                    t1.start()
                response['status'] = 200
                response['excel_processing_id'] = excel_processing_obj.pk

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateFAQBotAPI %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response = build_error_response(
                "There are some internal issues. Please try again later.")

        return Response(data=response)


class GetExcelProcessingProgressAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            excel_processing_id = str(data["excel_processing_id"]).strip()

            excel_processing_obj = ExcelProcessingProgress.objects.get(
                pk=excel_processing_id)

            if excel_processing_obj.is_processing_completed:
                if excel_processing_obj.status == "200":
                    response["status"] = 200
                else:
                    response["status"] = 102
                    response[
                        "status_message"] = excel_processing_obj.status_message
            else:
                response["status"] = 101

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetExcelProcessingProgressAPI %s at %s", str(e), str(
                exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})
            response["status"] = 500

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetExcelProcessingProgress = GetExcelProcessingProgressAPI.as_view()


class GetFAQExcelResultAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args):
        response = {}
        response["status"] = 500
        try:
            username = request.user.username
            selected_bot_id = ""
            selected_bot_id = request.GET["selected_bot_pk"]
            filename = "files/create_bot_with_excel_" + \
                       str(username) + "_" + \
                str(selected_bot_id) + "_" + ".txt"

            with open(filename, 'r') as file:
                data = file.read().replace('\n', '')

            file_data = data.split("<br>")
            file_data = [data for data in file_data if data]
            file_data_len = len(file_data)
            if file_data_len <= 2:
                response["status"] = 200
                response["status_message"] = ""
            else:
                response["status"] = 305
                response["status_message"] = data
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetFAQExcelResultAPI %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetFAQExcelResult = GetFAQExcelResultAPI.as_view()


# class GetTestAnalysisAPI(APIView):

#     permission_classes = (IsAuthenticated,)

#     authentication_classes = (
#         CsrfExemptSessionAuthentication, BasicAuthentication)

#     def post(self, request, *args, **kwargs):
#         response = {}
#         response['status'] = 500

#         try:
#             data = request.data
#             uploaded_file = data['test_file']
#             path = default_storage.save(
#                 uploaded_file.name, ContentFile(uploaded_file.read()))

#             wb = xlrd.open_workbook(settings.MEDIA_ROOT + path)
#             faqs = wb.sheet_by_index(0)
#             rows_limit = faqs.nrows

#             actual_question_list = []
#             variation_question_list = []
#             actual_answer_list = []
#             variation_answer_list = []
#             actual_intent_list = []
#             variation_intent_list = []
#             score_list = []

#             for rows_limit_iterator in range(1, rows_limit):
#                 query_question = faqs.cell_value(rows_limit_iterator, 0)
#                 query_question = process_string(
#                     query_question, None, None, None, None)

#                 answer = faqs.cell_value(rows_limit_iterator, 2)
#                 answer = answer.strip()

#                 variations_str = faqs.cell_value(rows_limit_iterator, 1)
#                 variations_list = [process_string(
#                     variation, None, None, None, None) for variation in variations_str.split(",") if variation != ""]

#                 query_recognized_intent = query_bot(question=query_question)

#                 if query_recognized_intent == None:
#                     actual_question_list.append(query_question)
#                     variation_question_list.append(query_question)
#                     actual_answer_list.append(answer)
#                     variation_answer_list.append("No response, intent: None")
#                     actual_intent_list.append("None")
#                     variation_intent_list.append("None")
#                     score_list.append(0)
#                 else:
#                     query_recognized_intent_obj = Intent.objects.get(
#                         name=query_recognized_intent, is_hidden=False)
#                     query_recognized_answer = query_recognized_intent_obj.tree.question.question

#                     if answer != query_recognized_answer:
#                         actual_question_list.append(query_question)
#                         variation_question_list.append(query_question)
#                         actual_answer_list.append(answer)
#                         variation_answer_list.append(query_recognized_answer)
#                         actual_intent_list.append("None")
#                         variation_intent_list.append(query_recognized_intent)
#                         score_list.append(query_recognized_intent_obj.get_score(
#                             get_stem_words_of_sentence(query_question)))

#                     for variation in variations_list:
#                         # Insert into database
#                         variation_recognized_intent = query_bot(
#                             question=variation)

#                         if variation_recognized_intent == None:
#                             actual_question_list.append(query_question)
#                             variation_question_list.append(variation)
#                             actual_answer_list.append(answer)
#                             variation_answer_list.append("None")
#                             actual_intent_list.append(query_recognized_intent)
#                             variation_intent_list.append("None")
#                             score_list.append(0)
#                         else:
#                             variation_recognized_intent_obj = Intent.objects.get(
#                                 name=variation_recognized_intent, is_hidden=False)
#                             variation_recognized_answer = variation_recognized_intent_obj.tree.question.question

#                             if answer != variation_recognized_answer:
#                                 actual_question_list.append(query_question)
#                                 variation_question_list.append(variation)
#                                 actual_answer_list.append(
#                                     query_recognized_answer)
#                                 variation_answer_list.append(
#                                     variation_recognized_answer)
#                                 actual_intent_list.append(
#                                     query_recognized_intent)
#                                 variation_intent_list.append(
#                                     variation_recognized_intent)
#                                 score_list.append(variation_recognized_intent_obj.get_score(
#                                     get_stem_words_of_sentence(variation)))

#             response["actual_question_list"] = actual_question_list
#             response["actual_answer_list"] = actual_answer_list
#             response["variation_question_list"] = variation_question_list
#             response["variation_answer_list"] = variation_answer_list
#             response["actual_intent_list"] = actual_intent_list
#             response["variation_intent_list"] = variation_intent_list
#             response["score_list"] = score_list
#             response['status'] = 200

#         except Exception as e:  # noqa: F841
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error("GetTestAnalysisAPI! %s %s",
#                          str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

#         return Response(data=response)


class GetConfigParamsAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500

        try:
            config_obj = Config.objects.all()[0]

            site_title = config_obj.site_title

            is_feedback_required = config_obj.is_feedback_required
            is_bot_switch_allowed = config_obj.allow_bot_switch

            response['site_title'] = site_title
            response['is_feedback_required'] = is_feedback_required
            response['allow_bot_switch'] = is_bot_switch_allowed
            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetConfigParamsAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SetConfigParamsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            is_feedback_required = data["is_feedback_required"]
            allow_bot_switch = data["allow_bot_switch"]

            if str(is_feedback_required) == "False":
                is_feedback_required = False
            else:
                is_feedback_required = True

            if str(allow_bot_switch) == "False":
                allow_bot_switch = False
            else:
                allow_bot_switch = True

            config_obj = Config.objects.all()[0]
            config_obj.is_feedback_required = is_feedback_required
            config_obj.allow_bot_switch = allow_bot_switch
            config_obj.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SetConfigParamsAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetFeedBackStatiticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            validation_obj = EasyChatInputValidation()

            bots_pk = json.loads(data['bots_pk'])
            bot_type = data['bot_type']
            bot_type = validation_obj.remo_html_from_string(bot_type)
            bot_objs = []

            channel_obj = None

            if len(bots_pk) == 0:
                if bot_type == "prod":
                    bot_objs = get_production_bots(user_obj)
                else:
                    bot_objs = get_uat_bots(user_obj)
            else:
                if bot_type == "uat":
                    for bot_pk in bots_pk:
                        bot_objs.append(Bot.objects.get(
                            pk=bot_pk, is_deleted=False, is_uat=True))
                else:
                    for bot_pk in bots_pk:
                        bot_obj = Bot.objects.get(
                            pk=bot_pk, is_deleted=False, is_uat=True)
                        bot_slug = bot_obj.slug
                        bot_objs += list(Bot.objects.filter(
                            slug=bot_slug, is_deleted=False, is_active=True))

            # total_sentences = len(
            #     MISDashboard.objects.filter(bot__in=bot_objs))
            # promoter_feedback = positive_feedback_count(
            #     User, Bot, MISDashboard, username, bot_objs)
            # demoter_feedback = negative_feedback_count(
            #     User, Bot, MISDashboard, username, bot_objs)

            total_feedback = Feedback.objects.count()
            promoter_feedback = promoter_feedback_count(
                bot_objs, channel_obj, Feedback)
            demoter_feedback = demoter_feedback_count(
                bot_objs, channel_obj, Feedback)
            response["promoter_feedback"] = promoter_feedback
            response["demoter_feedback"] = demoter_feedback
            response["total_feedback"] = total_feedback
            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error identify_intent %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            logger.error("Error GetFeedBackStatiticsAPI %s", str(e), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetUserTimeSpentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            response["total_time"] = total_time(TimeSpentByUser)
            response["user_count"] = user_count(TimeSpentByUser)
            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetUserTimeSpentAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            logger.error("Error GetUserTimeSpentAPI %s", str(e), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetMISDashboard = GetMISDashboardAPI.as_view()

GetMonthlyAnalytics = GetMonthlyAnalyticsAPI.as_view()

GetDailyAnalytics = GetDailyAnalyticsAPI.as_view()

GetTopIntents = GetTopIntentsAPI.as_view()

ExportData = ExportDataAPI.as_view()

CreateFAQBot = CreateFAQBotAPI.as_view()

GetConfigParams = GetConfigParamsAPI.as_view()

# GetTestAnalysis = GetTestAnalysisAPI.as_view()

FetchMessageHistory = FetchMessageHistoryAPI.as_view()

GetFeedBackStatitics = GetFeedBackStatiticsAPI.as_view()

SetConfigParams = SetConfigParamsAPI.as_view()

GetUserDetails = GetUserDetailsAPI.as_view()

GetUserTimeSpent = GetUserTimeSpentAPI.as_view()


# Revised Analytics

class GetBasicAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            bot_pk = request.GET["bot_pk"]
            validation_obj = EasyChatInputValidation()
            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            prod_bot_obj = None
            bot_objs = []
            if prod_bot_obj == None:
                bot_objs = [uat_bot_obj]
            else:
                bot_objs = [prod_bot_obj]

            response, status, message = get_basic_analytics_external(bot_objs[0], request.GET)
            response["status"] = status
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetBasicAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetBasicAnalytics = GetBasicAnalyticsAPI.as_view()


class GetFrequentIntentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            # username = request.user.username
            bot_pk = request.GET["bot_pk"]
            page = request.GET["page"]
            dropdown_language = request.GET["dropdown_language"]
            search_term = request.GET.get("search", "")
            if not dropdown_language:
                dropdown_language = "en"

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            prod_bot_obj = None

            bot_objs = []
            if prod_bot_obj == None:
                bot_objs = [uat_bot_obj]
            else:
                bot_objs = [prod_bot_obj]

            response, status, message = get_frequent_intents_external(bot_objs[0], request.GET)

            intent_frequency_list = response['intent_frequency_list']

            translate_api_status = True
            intent_frequency_list, translate_api_status = conversion_intent_analytics_translator(
                list(intent_frequency_list), dropdown_language, translate_api_status, search_term)

            paginator = Paginator(intent_frequency_list, 5)
            no_pages = paginator.num_pages

            is_last_page = False
            if int(page) >= int(no_pages):
                is_last_page = True

            try:
                intent_frequency_list = paginator.page(page)
            except PageNotAnInteger:
                intent_frequency_list = paginator.page(1)
            except EmptyPage:
                intent_frequency_list = paginator.page(paginator.num_pages)

            response["intent_frequency_list"] = list(intent_frequency_list)
            response["is_single_page"] = False
            if paginator.num_pages == 1:
                response["is_single_page"] = True

            response["is_last_page"] = is_last_page
            response["language_script_type"] = "ltr"
            if translate_api_status:
                lang_obj = Language.objects.filter(
                    lang=dropdown_language).first()
                if lang_obj:
                    response["language_script_type"] = lang_obj.language_script_type
                response["status"] = 200
            else:
                response["status"] = 300

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetFrequentIntentAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetFrequentIntent = GetFrequentIntentAPI.as_view()


class GetRecentlyUnansweredMessageAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        from django.core import serializers
        from ast import literal_eval
        try:
            start_time_analytics = time.time()
            bot_pk = request.GET["bot_pk"]
            page = request.GET["page"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            if request.user not in uat_bot_obj.users.all():
                response['message'] = 'You are not authorised to perform this operation.'
                response['status'] = 401
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            prod_bot_obj = None
            bot_objs = []
            if prod_bot_obj == None:
                bot_objs = [uat_bot_obj]
            else:
                bot_objs = [prod_bot_obj]
            
            response, status, message = get_unanswered_queries_external(bot_objs[0], request.GET)

            details_of_unanswered_messages = response['unanswered_questions']

            paginator = Paginator(details_of_unanswered_messages, 5)
            no_pages = paginator.num_pages

            is_last_page = False
            if int(page) >= int(no_pages):
                is_last_page = True

            try:
                details_of_unanswered_messages = paginator.page(page)
            except PageNotAnInteger:
                details_of_unanswered_messages = paginator.page(1)
            except EmptyPage:
                details_of_unanswered_messages = paginator.page(
                    paginator.num_pages)

            response["is_single_page"] = False
            if paginator.num_pages == 1:
                response["is_single_page"] = True

            response["unanswered_message_list"] = list(
                details_of_unanswered_messages)
            response["is_last_page"] = is_last_page
            response["status"] = status

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetRecentlyUnansweredMessageAPI %s in line no %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        end_time = time.time()
        time_taken = str(end_time - start_time_analytics)
        logger.info("Get Recently Unanswered Analytics Time Taken %s", time_taken, extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetRecentlyUnansweredMessage = GetRecentlyUnansweredMessageAPI.as_view()


class GetIntuitiveMessageAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            start_time_analytics = time.time()
            bot_pk = request.GET["bot_pk"]
            
            dropdown_language = "en"
            if "dropdown_language" in request.GET:
                dropdown_language = request.GET["dropdown_language"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            prod_bot_obj = None
            bot_objs = []
            if prod_bot_obj == None:
                bot_objs = [uat_bot_obj]
            else:
                bot_objs = [prod_bot_obj]

            response, status, message = get_intuitive_questions_data_external(bot_objs[0], request.GET, dropdown_language)
            
            details_of_intuitive_questions = response['details_of_intuitive_questions']

            response["intuitive_message_list"] = list(
                details_of_intuitive_questions)

            response["language_script_type"] = "ltr"
            if status == 200:
                lang_obj = Language.objects.filter(
                    lang=dropdown_language).first()
                if lang_obj:
                    response["language_script_type"] = lang_obj.language_script_type
                response["status"] = 200
            else:
                response["status"] = 300
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetIntuitiveMessageAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        
        end_time = time.time()
        time_taken = str(end_time - start_time_analytics)
        logger.info("Get Intuitive Analytics Time Taken %s", time_taken, extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetIntuitiveMessage = GetIntuitiveMessageAPI.as_view()


class GetFrequentWindowLocationAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            # username = request.user.username
            bot_pk = request.GET["bot_pk"]
            channel_name = request.GET["channel"]
            reverse = request.GET["reverse"]
            page = request.GET["page"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))
            channel_name = validation_obj.remo_html_from_string(channel_name)

            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()
            datetime_end = datetime.datetime.today().date()
            try:
                date_format = "%Y-%m-%d"
                start_date = request.GET["start_date"]
                end_date = request.GET["end_date"]
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("start_date and end_date is not in required format. use default datetime: %s at line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                pass

            bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)
            web_pages_name, web_page_visited_count, bot_clicked_count = get_window_location_frequency(
                bot_obj, TrafficSources, datetime_start, datetime_end, channel_name)

            if str(reverse).lower() == "false":
                web_pages_name.reverse()

            paginator = Paginator(web_pages_name, 5)
            no_pages = paginator.num_pages

            paginator_web_page = Paginator(web_page_visited_count, 5)

            paginator_bot_click = Paginator(bot_clicked_count, 5)
            is_last_page = False
            if int(page) >= int(no_pages):
                is_last_page = True

            try:
                web_pages_name = paginator.page(page)
                web_page_visited_count = paginator_web_page.page(page)
                bot_clicked_count = paginator_bot_click.page(page)
            except PageNotAnInteger:
                web_pages_name = paginator.page(1)
                web_page_visited_count = paginator_web_page.page(1)
                bot_clicked_count = paginator_bot_click.page(1)
            except EmptyPage:
                web_pages_name = paginator.page(paginator.num_pages)
                web_page_visited_count = paginator_web_page.page(
                    paginator.num_pages)
                bot_clicked_count = paginator_bot_click.page(
                    paginator.num_pages)

            response["is_single_page"] = False
            if paginator.num_pages == 1:
                response["is_single_page"] = True

            response["is_last_page"] = is_last_page
            response["web_pages_name"] = list(web_pages_name)
            response["web_page_visited_count"] = list(web_page_visited_count)
            response["bot_clicked_count"] = list(bot_clicked_count)
            response["start_date"] = datetime_start.strftime("%d-%b-%y")
            response["end_date"] = datetime_end.strftime("%d-%b-%y")
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetFrequentWindowLocationAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetFrequentWindowLocation = GetFrequentWindowLocationAPI.as_view()


class DownloadTrafficSourcesAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            start_date = data["start_date"]
            end_date = data["end_date"]
            bot_obj = Bot.objects.get(pk=bot_pk)
            traffic_sources_objects = TrafficSources.objects.filter(
                visiting_date__gte=start_date, visiting_date__lte=end_date, bot=bot_obj)

            from xlwt import Workbook
            export_intent_wb = Workbook()
            sheet_name = "Traffic Sources Excel"
            sheet1 = export_intent_wb.add_sheet(sheet_name)
            sheet1.write(0, 0, "URL")
            sheet1.write(0, 1, "Web Page Visit Count")
            sheet1.write(0, 2, "Bot visit count")
            sheet1.write(0, 3, "Date")
            index = 1
            for web_page_frequency in traffic_sources_objects:
                regex_webpage = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                url_check = re.findall(
                    regex_webpage, web_page_frequency.web_page)
                if (len(url_check) >= 1):
                    sheet1.write(index, 0, web_page_frequency.web_page)
                    sheet1.write(index, 1, web_page_frequency.web_page_visited)
                    sheet1.write(
                        index, 2, web_page_frequency.bot_clicked_count)
                    sheet1.write(index, 3, str(
                        web_page_frequency.visiting_date))
                    index += 1
            filename = str(request.user.username) + "-" + \
                str(bot_obj.slug) + "-traffic_sources.xls"
            export_intent_wb.save(settings.MEDIA_ROOT + "private/" + filename)
            path_to_file = '/files/private/' + str(filename)

            response['file_url'] = path_to_file
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error DownloadTrafficSourcesAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DownloadTrafficSources = DownloadTrafficSourcesAPI.as_view()


class GetChannelAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            channel_name = data["channel"]
            filter_name = data["filter"]
            selected_language = data["selected_language"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))
            channel_name = validation_obj.remo_html_from_string(channel_name)

            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()

            datetime_end = datetime.datetime.today().date()
            try:
                date_format = "%Y-%m-%d"
                start_date = data["start_date"]
                end_date = data["end_date"]
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("start_date and end_date is not in required format. use default datetime: %s at line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                pass

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            prod_bot_obj = None

            supported_languages_list = []
            if selected_language.lower() != "all":
                supported_languages_list = selected_language.split(",")
                supported_languages_list = [
                    lang.strip() for lang in supported_languages_list]

            supported_languages = Language.objects.filter(
                lang__in=supported_languages_list)

            bot_objs = []
            if prod_bot_obj == None:
                bot_objs = [uat_bot_obj]
            else:
                bot_objs = [prod_bot_obj]

            category_name = "All"
            category_obj = None
            channel_dict = {}

            if filter_name == "Users":
                previous_user_objects = return_unique_users_objects_based_on_filter(bot_objs, channel_name, selected_language, supported_languages, UniqueUsers)
                filtered_previous_user_objects = previous_user_objects.filter(date__gte=datetime_start, date__lte=datetime_end)

                if channel_name == 'All':
                    for channel_obj in Channel.objects.filter(is_easychat_channel=True):
                        channel_count = filtered_previous_user_objects.filter(channel=channel_obj).aggregate(Sum('count'))['count__sum']
                        channel_dict[channel_obj.name] = 0 if channel_count == None else channel_count
                else:
                    channel_count = filtered_previous_user_objects.filter(channel__name=channel_name).aggregate(Sum('count'))['count__sum']
                    channel_dict[channel_name] = 0 if channel_count == None else channel_count

            else:
                previous_mis_objects = return_mis_daily_objects_based_on_filter(bot_objs, channel_name, category_name, category_obj, selected_language, supported_languages, MessageAnalyticsDaily)
                filtered_previous_mis_objects = previous_mis_objects.filter(date_message_analytics__gte=datetime_start, date_message_analytics__lte=datetime_end)
                if channel_name == 'All':
                    for channel_obj in Channel.objects.filter(is_easychat_channel=True):
                        channel_count = filtered_previous_mis_objects.filter(channel_message=channel_obj).aggregate(Sum('total_messages_count'))['total_messages_count__sum']
                        channel_dict[channel_obj.name] = 0 if channel_count == None else channel_count
                else:
                    channel_count = filtered_previous_mis_objects.filter(channel_message__name=channel_name).aggregate(Sum('total_messages_count'))['total_messages_count__sum']
                    channel_dict[channel_name] = 0 if channel_count == None else channel_count
            
            if datetime_end == datetime.datetime.today().date():
                mis_objects = return_mis_objects_based_on_category_channel_language(
                    datetime_end, datetime_end, bot_objs, channel_name, "All", selected_language, supported_languages, MISDashboard, UserSessionHealth)

                if filter_name == "Users":
                    mis_objects = mis_objects.order_by('user_id').values_list(
                        'user_id', 'channel_name').distinct()
                    channel_name_frequency = list(mis_objects.filter(~Q(channel_name=None)).values(
                        "channel_name").order_by("channel_name").annotate(
                        frequency=Count("user_id", distinct=True)).order_by('-frequency'))
                else:
                    channel_name_frequency = list(mis_objects.filter(~Q(channel_name=None)).values(
                        "channel_name").order_by("channel_name").annotate(frequency=Count("channel_name")).order_by(
                        '-frequency'))

                for channel_detail in channel_name_frequency:
                    channel_dict[channel_detail["channel_name"]] += channel_detail["frequency"]

            response["channel_dict"] = channel_dict
            response["start_date"] = datetime_start.strftime("%d-%b-%y")
            response["end_date"] = datetime_end.strftime("%d-%b-%y")
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetChannelAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetChannelAnalytics = GetChannelAnalyticsAPI.as_view()


class GetCategoryAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            channel_name = data["channel"]
            selected_language = data["selected_language"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))
            channel_name = validation_obj.remo_html_from_string(channel_name)

            supported_languages_list = []
            if selected_language.lower() != "all":
                supported_languages_list = selected_language.split(",")
                supported_languages_list = [
                    lang.strip() for lang in supported_languages_list]

            supported_languages = Language.objects.filter(
                lang__in=supported_languages_list)

            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()

            datetime_end = datetime.datetime.today().date()
            try:
                date_format = "%Y-%m-%d"
                start_date = data["start_date"]
                end_date = data["end_date"]
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("start_date and end_date is not in required format. use default datetime: %s at line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                pass

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            prod_bot_obj = None
            bot_objs = []
            if prod_bot_obj == None:
                bot_objs = [uat_bot_obj]
            else:
                bot_objs = [prod_bot_obj]

            previous_mis_objects = return_mis_daily_objects_based_on_filter(bot_objs, channel_name, "all", None, selected_language, supported_languages, MessageAnalyticsDaily)

            filtered_previous_mis_objects = previous_mis_objects.filter(date_message_analytics__gte=datetime_start, date_message_analytics__lte=datetime_end)

            category_dict = {}
            for category_obj in Category.objects.filter(bot__in=bot_objs):
                category_count = filtered_previous_mis_objects.filter(category=category_obj).aggregate(Sum('total_messages_count'))['total_messages_count__sum']
                if not category_count:
                    category_count = 0
                category_dict[category_obj.name] = category_count
                
            if datetime_end == datetime.datetime.today().date():
                
                if channel_name == 'All':
                    mis_objects = MISDashboard.objects.filter(creation_date=datetime_end, bot__in=bot_objs)
                else:
                    mis_objects = MISDashboard.objects.filter(
                        bot__in=bot_objs, creation_date=datetime_end, channel_name=channel_name)

                mis_objects = return_mis_objects_excluding_blocked_sessions(mis_objects, UserSessionHealth)

                if selected_language.lower() != "all":
                    mis_objects = mis_objects.filter(
                        selected_language__in=supported_languages)

                if datetime_start != None and datetime_end != None:
                    mis_objects = mis_objects.filter(
                        date__date__gte=datetime_start, date__date__lte=datetime_end)

                category_name_frequency = list(
                    mis_objects.filter(~Q(category__name="") & ~Q(category=None) & ~Q(category__name="ABC")).filter(
                        small_talk_intent=False).values(
                        "category__name").order_by("category__name").annotate(frequency=Count("category__name")).order_by(
                        '-frequency'))

                for category_detail in category_name_frequency:
                    category_dict[category_detail["category__name"]] += category_detail["frequency"]

            logger.info(category_dict, extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
            response["category_dict"] = category_dict
            response["start_date"] = datetime_start.strftime("%d-%b-%y")
            response["end_date"] = datetime_end.strftime("%d-%b-%y")
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetChannelAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetCategoryAnalytics = GetCategoryAnalyticsAPI.as_view()


class GetCategoryWiseFrequentIntentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            bot_pk = request.GET["bot_pk"]
            page = request.GET["page"]
            channel_name = request.GET["channel"]
            dropdown_language = request.GET["dropdown_language"]
            global_filter_category_name = request.GET["global_category"]

            selected_language = "All"
            supported_languages_list = []
            search_term = request.GET["search"]
            intent_page = request.GET.get("intent_page", "1")
            if "selected_language" in request.GET:
                selected_language = request.GET["selected_language"]
                if selected_language.lower() != "all":
                    supported_languages_list = selected_language.split(",")
                    supported_languages_list = [
                        lang.strip() for lang in supported_languages_list]

            supported_languages = Language.objects.filter(
                lang__in=supported_languages_list)

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))
            channel_name = validation_obj.remo_html_from_string(channel_name)
            search_term = validation_obj.remo_html_from_string(search_term)

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            prod_bot_obj = None

            bot_objs = []
            start_date = request.GET["start_date"]
            end_date = request.GET["end_date"]
            if prod_bot_obj == None:
                bot_objs = [uat_bot_obj]
            else:
                bot_objs = [prod_bot_obj]
            # logger.info(Category.objects.all())
            intent_num_pages = 1
            category_list = []
            translate_api_status = True
            if global_filter_category_name == "All":
                try:
                    no_pages = Category.objects.filter(bot=bot_objs[0]).count()
                    top_categories = get_max_intent_category_name(
                        bot_objs, MISDashboard, UserSessionHealth, start_date, end_date, channel_name,
                        selected_language, supported_languages
                    )
                    for category in top_categories:
                        category_list.append(category["category__name"])
                    category_names = Category.objects.filter(
                        bot=bot_objs[0]).exclude(name__in=category_list)
                    for category in category_names:
                        category_list.append(category.name)
                    category_name = category_list[int(page) - 1]
                    if search_term:
                        category_name = "All"

                    intent_frequency_list = get_category_wise_intent_frequency(
                        bot_objs, MISDashboard, UserSessionHealth, start_date, end_date, category_name, channel_name,
                        global_filter_category_name, selected_language, supported_languages)
                    intent_frequency_list, translate_api_status = conversion_intent_analytics_translator(
                        list(intent_frequency_list), dropdown_language, translate_api_status, search_term)
                    paginator = Paginator(intent_frequency_list, 5)
                    intent_page = int(intent_page)
                    intent_num_pages = paginator.num_pages
                    try:
                        intent_frequency_list = paginator.page(intent_page)
                    except PageNotAnInteger:
                        intent_frequency_list = paginator.page(1)
                    except EmptyPage:
                        intent_frequency_list = paginator.page(
                            paginator.num_pages)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error while fetching category-wise intent frequency %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                                 'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                    category_name = ""
                    intent_frequency_list = []
            else:
                try:
                    category_name = global_filter_category_name
                    intent_frequency_list = get_category_wise_intent_frequency(
                        bot_objs, MISDashboard, UserSessionHealth, start_date, end_date, category_name, channel_name,
                        global_filter_category_name, selected_language, supported_languages)
                    intent_frequency_list, translate_api_status = conversion_intent_analytics_translator(
                        list(intent_frequency_list), dropdown_language, translate_api_status, search_term)
                    paginator = Paginator(intent_frequency_list, 5)
                    page = int(page)
                    try:
                        intent_frequency_list = paginator.page(page)
                    except PageNotAnInteger:
                        intent_frequency_list = paginator.page(1)
                    except EmptyPage:
                        intent_frequency_list = paginator.page(
                            paginator.num_pages)
                    no_pages = paginator.num_pages
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error while fetching category-wise intent frequency %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                                 'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                    category_name = ""
                    intent_frequency_list = []

            is_last_page = False
            is_intent_last_page = False
            if int(page) >= int(no_pages):
                is_last_page = True
            if int(intent_page) >= int(intent_num_pages):
                is_intent_last_page = True
            response["no_pages"] = no_pages
            response["intent_num_pages"] = intent_num_pages
            response["is_intent_last_page"] = is_intent_last_page
            response["category_name"] = category_name
            response["intent_frequency_list"] = list(intent_frequency_list)
            response["is_last_page"] = is_last_page
            response["language_script_type"] = "ltr"
            if translate_api_status:
                lang_obj = Language.objects.filter(
                    lang=dropdown_language).first()
                if lang_obj:
                    response["language_script_type"] = lang_obj.language_script_type
                response["status"] = 200
            else:
                response["status"] = 300

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetCategoryWiseFrequentIntentAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetCategoryWiseFrequentIntent = GetCategoryWiseFrequentIntentAPI.as_view()


class GetUserAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            start_time_analytics = time.time()
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            channel_name = data["channel"]
            selected_language = data["selected_language"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))
            channel_name = validation_obj.remo_html_from_string(channel_name)
            selected_language = validation_obj.remo_html_from_string(
                selected_language)
            filter_type = "1"  # Default Daily Analytics
            try:
                filter_type = data["filter_type"]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("filter_type is not defined: %s at line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                pass

            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()

            datetime_end = datetime.datetime.today().date()
            try:
                date_format = "%Y-%m-%d"
                start_date = data["start_date"]
                end_date = data["end_date"]
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("startdate and enddate is not in valid format %s at line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                pass

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            supported_languages_list = []
            if selected_language.lower() != "all":
                supported_languages_list = selected_language.split(",")
                supported_languages_list = [
                    lang.strip() for lang in supported_languages_list]

            supported_languages = Language.objects.filter(
                lang__in=supported_languages_list)

            prod_bot_obj = None

            bot_objs = []
            if prod_bot_obj == None:
                bot_objs = [uat_bot_obj]
            else:
                bot_objs = [prod_bot_obj]

            mis_objects = return_mis_objects_based_on_category_channel_language(datetime.datetime.now().date(
            ), datetime.datetime.now().date(), bot_objs, channel_name, "All", selected_language, supported_languages, MISDashboard, UserSessionHealth)

            previous_mis_objects = return_unique_users_objects_based_on_filter(
                bot_objs, channel_name, selected_language, supported_languages, UniqueUsers)

            previous_mis_objects = previous_mis_objects.filter(date__gte=datetime_start, date__lte=datetime_end)
            
            user_analytics_list = []
            today_flag = False
            if filter_type == "1":
                if datetime_end.strftime("%d-%b-%y") == datetime.datetime.today().strftime("%d-%b-%y"):
                    no_days = (datetime_end - datetime_start).days
                    today_flag = True
                else:
                    no_days = (datetime_end - datetime_start).days + 1
                    today_flag = False
                for day in range(no_days):
                    temp_datetime = datetime_start + datetime.timedelta(day)
                    date_filtered_mis_objects = previous_mis_objects.filter(
                        date=temp_datetime)
                    count = date_filtered_mis_objects.aggregate(
                        Sum('count'))['count__sum']

                    count = return_zero_if_number_is_none(count)

                    session_count = date_filtered_mis_objects.aggregate(
                        Sum('session_count'))['session_count__sum']

                    business_initiated_session_count = date_filtered_mis_objects.aggregate(
                        Sum('business_initiated_session_count'))['business_initiated_session_count__sum']

                    session_count = return_zero_if_number_is_none(
                        session_count)

                    business_initiated_session_count = return_zero_if_number_is_none(
                        business_initiated_session_count)

                    user_analytics_list.append({
                        "label": str(temp_datetime.strftime("%d-%b-%y")),
                        "count": count,
                        "session_count": session_count,
                        "business_initiated_sessions": business_initiated_session_count
                    })

                if datetime_end.strftime("%d-%b-%y") == datetime.datetime.today().strftime("%d-%b-%y"):
                    date_filtered_mis_objects = mis_objects
                    total_users = date_filtered_mis_objects.values(
                        "user_id").distinct().count()
                    unique_session_objects = date_filtered_mis_objects.values(
                        "session_id").distinct()
                    total_sessions = unique_session_objects.count()
                    business_initiated_sessions = unique_session_objects.filter(
                        is_business_initiated_session=True).count()

                    user_analytics_list.append({
                        "label": str((datetime_end).strftime("%d-%b-%y")),
                        "count": total_users,
                        "session_count": total_sessions,
                        "business_initiated_sessions": business_initiated_sessions,
                    })

            elif filter_type == "2":
                no_days = (datetime_end - datetime_start).days
                no_weeks = int(no_days / 7.0) + 1
                for week in range(no_weeks):
                    temp_end_datetime = datetime_end - \
                        datetime.timedelta(week * 7)
                    temp_start_datetime = datetime_end - \
                        datetime.timedelta((week + 1) * 7)

                    date_filtered_mis_objects = previous_mis_objects

                    date_filtered_mis_objects = previous_mis_objects.filter(
                        date__gt=temp_start_datetime, date__lte=temp_end_datetime)
                    total_users = date_filtered_mis_objects.aggregate(
                        Sum('count'))['count__sum']

                    if total_users == None:
                        total_users = 0

                    total_sessions = date_filtered_mis_objects.aggregate(
                        Sum('session_count'))['session_count__sum']

                    total_business_initiated_session = date_filtered_mis_objects.aggregate(
                        Sum('business_initiated_session_count'))['business_initiated_session_count__sum']

                    total_sessions = return_zero_if_number_is_none(
                        total_sessions)
                    total_business_initiated_session = return_zero_if_number_is_none(
                        total_business_initiated_session)

                    temp_start_datetime_str = (temp_start_datetime + datetime.timedelta(1)).strftime(
                        "%d/%m")
                    temp_end_datetime_str = (
                        temp_end_datetime).strftime("%d/%m")
                    user_analytics_list.append({
                        "label": temp_start_datetime_str + "-" + temp_end_datetime_str,
                        "count": total_users,
                        "session_count": total_sessions,
                        "business_initiated_sessions": total_business_initiated_session,
                    })

                user_analytics_list = user_analytics_list[::-1]
                if datetime_end.strftime("%d-%b-%y") == datetime.datetime.today().strftime("%d-%b-%y"):
                    date_filtered_mis_objects = mis_objects
                    total_users = date_filtered_mis_objects.values(
                        "user_id").distinct().count()
                    user_analytics_list[-1]["count"] = user_analytics_list[-1]["count"] + total_users

                    unique_sessions_mis = date_filtered_mis_objects.values(
                        "session_id").distinct()

                    total_sessions = unique_sessions_mis.count()
                    business_initiated_sessions = unique_sessions_mis.filter(
                        is_business_initiated_session=True).count()
                    user_analytics_list[-1]["session_count"] = user_analytics_list[-1]["session_count"] + total_sessions
                    user_analytics_list[-1]["business_initiated_sessions"] = user_analytics_list[-1]["business_initiated_sessions"] + business_initiated_sessions
            else:
                month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
                    r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days + 1)).keys())
                date_filtered_mis_objects = previous_mis_objects
                for month in month_list:
                    temp_month = month_to_num_dict[month.split("-")[0]]
                    temp_year = int(month.split("-")[1])

                    date_filtered_mis_objects = previous_mis_objects.filter(date__month=temp_month, date__year=temp_year).aggregate(
                        Sum('count'))['count__sum']

                    if date_filtered_mis_objects == None:
                        date_filtered_mis_objects = 0

                    total_sessions = \
                        previous_mis_objects.filter(date__month=temp_month, date__year=temp_year).aggregate(
                            Sum('session_count'))['session_count__sum']

                    total_business_initiated_session = previous_mis_objects.filter(date__month=temp_month, date__year=temp_year).aggregate(
                        Sum('business_initiated_session_count'))['business_initiated_session_count__sum']

                    total_sessions = return_zero_if_number_is_none(
                        total_sessions)
                    total_business_initiated_session = return_zero_if_number_is_none(
                        total_business_initiated_session)

                    user_analytics_list.append({
                        "label": month,
                        "count": date_filtered_mis_objects,
                        "session_count": total_sessions,
                        "business_initiated_sessions": total_business_initiated_session,
                    })
                if datetime_end.month == datetime.datetime.today().month:
                    date_filtered_mis_objects = mis_objects
                    total_users = date_filtered_mis_objects.values(
                        "user_id").distinct().count()
                    user_analytics_list[-1]["count"] = user_analytics_list[-1]["count"] + total_users

                    unique_sessions_mis = date_filtered_mis_objects.values(
                        "session_id").distinct()

                    total_sessions = unique_sessions_mis.count()
                    business_initiated_sessions = unique_sessions_mis.filter(
                        is_business_initiated_session=True).count()
                    user_analytics_list[-1]["session_count"] = user_analytics_list[-1]["session_count"] + total_sessions
                    user_analytics_list[-1]["business_initiated_sessions"] = user_analytics_list[-1]["business_initiated_sessions"] + business_initiated_sessions

            response["user_analytics_list"] = user_analytics_list
            response["start_date"] = datetime_start.strftime("%d-%b-%y")
            response["end_date"] = datetime_end.strftime("%d-%b-%y")

            if filter_type == "1":
                if today_flag:
                    response["total_days"] = no_days + 1
                else:
                    response["total_days"] = no_days
            elif filter_type == "2":
                response["total_days"] = len(user_analytics_list) * 7
            elif filter_type == "3":
                response["total_days"] = len(user_analytics_list) * 30

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetUserAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        end_time = time.time()
        time_taken = str(end_time - start_time_analytics)
        logger.info("Get User Analytics Time Taken %s", time_taken, extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetUserAnalytics = GetUserAnalyticsAPI.as_view()


class GetMessageAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            start_time_analytics = time.time()
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            channel_name = data["channel"]
            category_name = data["category_name"]
            selected_language = data["selected_language"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))
            channel_name = validation_obj.remo_html_from_string(channel_name)

            filter_type = "1"  # Default Daily Analytics
            try:
                filter_type = data["filter_type"]
            except Exception:
                pass

            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()

            datetime_end = datetime.datetime.today().date()
            try:
                date_format = "%Y-%m-%d"
                start_date = data["start_date"]
                end_date = data["end_date"]
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("startdate and enddate is not in valid format %s at line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                pass

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)
            bot_info_obj = BotInfo.objects.get(bot=uat_bot_obj)
            category_obj = None
            if category_name != "All":
                category_obj = Category.objects.get(
                    bot=uat_bot_obj, name=category_name)

            supported_languages_list = []
            if selected_language.lower() != "all":
                supported_languages_list = selected_language.split(",")
                supported_languages_list = [
                    lang.strip() for lang in supported_languages_list]

            supported_languages = Language.objects.filter(
                lang__in=supported_languages_list)

            prod_bot_obj = None

            bot_objs = []
            if prod_bot_obj == None:
                bot_objs = [uat_bot_obj]
            else:
                bot_objs = [prod_bot_obj]

            mis_objects = return_mis_objects_based_on_category_channel_language(datetime.datetime.now().date(), datetime.datetime.now(
            ).date(), bot_objs, channel_name, category_name, selected_language, supported_languages, MISDashboard, UserSessionHealth)

            previous_mis_objects = return_mis_daily_objects_based_on_filter(
                bot_objs, channel_name, category_name, category_obj, selected_language, supported_languages, MessageAnalyticsDaily)
            
            previous_mis_objects = previous_mis_objects.filter(date_message_analytics__gte=datetime_start, date_message_analytics__lte=datetime_end)

            message_analytics_list = []

            percentage_change = "None"
            today_flag = False
            no_days = 0
            percentage_change_type = ""
            if filter_type == "1":
                total_hours_passed = datetime.datetime.today().hour
                avg_total_messages = mis_objects.filter(
                    creation_date=datetime.datetime.today()).count()

                if total_hours_passed != 0:
                    avg_msgs = math.ceil(
                        (avg_total_messages / float(total_hours_passed)) * 24.0)
                else:
                    avg_msgs = math.ceil((avg_total_messages / float(1)))

                if datetime_end.strftime("%d-%b-%y") == datetime.datetime.today().strftime("%d-%b-%y"):
                    no_days = (datetime_end - datetime_start).days
                    today_flag = True
                else:
                    no_days = (datetime_end - datetime_start).days + 1
                    today_flag = False

                for day in range(no_days):
                    temp_datetime = datetime_start + datetime.timedelta(day)
                    date_filtered_mis_objects = previous_mis_objects.filter(
                        date_message_analytics=temp_datetime)
                    total_messages = date_filtered_mis_objects.aggregate(
                        Sum('total_messages_count'))['total_messages_count__sum']
                    total_intuitive_messages = date_filtered_mis_objects.aggregate(
                        Sum('intuitive_query_count'))['intuitive_query_count__sum']
                    total_answered_messages = date_filtered_mis_objects.aggregate(
                        Sum('answered_query_count'))['answered_query_count__sum']

                    total_unanswered_messages = date_filtered_mis_objects.aggregate(
                        Sum('unanswered_query_count'))['unanswered_query_count__sum']

                    total_messages = return_zero_if_number_is_none(
                        total_messages)
                    total_answered_messages = return_zero_if_number_is_none(
                        total_answered_messages)
                    total_unanswered_messages = return_zero_if_number_is_none(
                        total_unanswered_messages)
                    total_intuitive_messages = return_zero_if_number_is_none(
                        total_intuitive_messages)

                    # false_positive_messages = mis_filtered_objs.filter(
                    #     creation_date=temp_datetime, flagged_queries_positive_type="1").count()

                    message_analytics_list.append({
                        "label": str(temp_datetime.strftime("%d-%b-%y")),
                        "total_messages": total_messages,
                        "total_answered_messages": total_answered_messages,
                        "total_unanswered_messages": total_unanswered_messages,
                        "predicted_messages_no": total_messages,
                        "total_intuitive_messages": total_intuitive_messages
                        # "false_positive_messages": false_positive_messages
                    })

                if datetime_end == datetime.datetime.today().date():
                    date_filtered_mis_objects = mis_objects
                    total_messages = date_filtered_mis_objects.count()

                    total_unanswered_messages = date_filtered_mis_objects.filter(
                        intent_name=None, is_unidentified_query=True, is_intiuitive_query=False).exclude(message_received="").count()
                    total_intuitive_messages = date_filtered_mis_objects.filter(
                        intent_name=None, is_intiuitive_query=True).count()
                    total_answered_messages = total_messages - (total_unanswered_messages + total_intuitive_messages) 
                    # false_positive_messages = date_filtered_mis_objects.filter(
                    #     flagged_queries_positive_type="1").count()

                    message_analytics_list.append({
                        "label": str((datetime_end).strftime("%d-%b-%y")),
                        "total_messages": total_messages,
                        "total_answered_messages": total_answered_messages,
                        "total_unanswered_messages": total_unanswered_messages,
                        "predicted_messages_no": total_messages,
                        "total_intuitive_messages": total_intuitive_messages
                        # "false_positive_messages": false_positive_messages
                    })
                    message_analytics_list[-1]["predicted_messages_no"] = avg_msgs
                    last_daytime = datetime_end - datetime.timedelta(1)
                    today_mis_objects = mis_objects.filter(
                        date__date=datetime_end).count()
                    last_day_mis_objects = mis_objects.filter(
                        date__date=last_daytime).count()
                    if last_day_mis_objects > 0:
                        percentage_change = round(100 * float(
                            today_mis_objects - last_day_mis_objects) / float(last_day_mis_objects), 2)
                    else:
                        percentage_change = "None"
                    percentage_change_type = 'Since Yesterday'

            elif filter_type == "2":
                total_hours_passed = (6 * 24) + datetime.datetime.today().hour

                start_week_date = datetime.datetime.today() - datetime.timedelta(7)

                previous_mis_objects_count = previous_mis_objects.filter(
                    date_message_analytics__gte=start_week_date).aggregate(Sum('total_messages_count'))[
                    'total_messages_count__sum']

                if previous_mis_objects_count == None:
                    previous_mis_objects_count = 0

                avg_msgs = math.ceil(
                    ((previous_mis_objects_count + mis_objects.count()) / total_hours_passed) * 7.0 * 24.0) + 1

                no_days = (datetime_end - datetime_start).days
                no_weeks = int(no_days / 7.0) + 1

                for week in range(no_weeks):
                    temp_end_datetime = datetime_end - \
                        datetime.timedelta(week * 7)
                    temp_start_datetime = datetime_end - \
                        datetime.timedelta((week + 1) * 7)

                    if temp_start_datetime < datetime_start:
                        temp_start_datetime = datetime_start - datetime.timedelta(1)
                        
                    date_filtered_mis_objects = previous_mis_objects

                    date_filtered_mis_objects = previous_mis_objects.filter(
                        date_message_analytics__gt=temp_start_datetime, date_message_analytics__lte=temp_end_datetime)
                    total_messages = date_filtered_mis_objects.aggregate(
                        Sum('total_messages_count'))['total_messages_count__sum']
                    total_answered_messages = date_filtered_mis_objects.aggregate(
                        Sum('answered_query_count'))['answered_query_count__sum']
                    total_unanswered_messages = date_filtered_mis_objects.aggregate(
                        Sum('unanswered_query_count'))['unanswered_query_count__sum']
                    total_intuitive_messages = date_filtered_mis_objects.aggregate(
                        Sum('intuitive_query_count'))['intuitive_query_count__sum']
                    total_messages = return_zero_if_number_is_none(
                        total_messages)
                    total_answered_messages = return_zero_if_number_is_none(
                        total_answered_messages)
                    total_unanswered_messages = return_zero_if_number_is_none(
                        total_unanswered_messages)
                    total_intuitive_messages = return_zero_if_number_is_none(
                        total_intuitive_messages)

                    # false_positive_messages = mis_filtered_objs.filter(
                    #     flagged_queries_positive_type="1", creation_date__gt=temp_start_datetime, creation_date__lte=temp_end_datetime).count()

                    temp_start_datetime_str = (temp_start_datetime + datetime.timedelta(1)).strftime(
                        "%d/%m")
                    temp_end_datetime_str = (
                        temp_end_datetime).strftime("%d/%m")
                    message_analytics_list.append({
                        "label": str(temp_start_datetime_str + "-" + temp_end_datetime_str),
                        "total_messages": total_messages,
                        "total_answered_messages": total_answered_messages,
                        "total_unanswered_messages": total_unanswered_messages,
                        "predicted_messages_no": total_messages,
                        "total_intuitive_messages": total_intuitive_messages
                        # "false_positive_messages": false_positive_messages
                    })

                message_analytics_list = message_analytics_list[::-1]
                if datetime_end == datetime.datetime.today().date():
                    date_filtered_mis_objects = mis_objects
                    total_messages = date_filtered_mis_objects.count()

                    total_unanswered_messages = date_filtered_mis_objects.filter(
                        intent_name=None, is_unidentified_query=True).count()

                    total_answered_messages = total_messages - total_unanswered_messages
                    message_analytics_list[-1]["total_messages"] = message_analytics_list[-1]["total_messages"] + total_messages
                    message_analytics_list[-1]["total_intuitive_messages"] = message_analytics_list[-1]["total_intuitive_messages"] + \
                        total_intuitive_messages
                    message_analytics_list[-1]["total_unanswered_messages"] = message_analytics_list[-1]["total_unanswered_messages"] + \
                        total_unanswered_messages
                    message_analytics_list[-1]["total_answered_messages"] = message_analytics_list[-1]["total_answered_messages"] + \
                        total_answered_messages
                    message_analytics_list[-1]["predicted_messages_no"] = avg_msgs
                    # message_analytics_list[-1]["false_positive_messages"] += date_filtered_mis_objects.filter(
                    #     flagged_queries_positive_type="1").count()
                    this_7days_start = datetime_end - datetime.timedelta(7)
                    previous_mis_objects_count = previous_mis_objects.filter(
                        date_message_analytics__lte=datetime_end,
                        date_message_analytics__gt=this_7days_start).aggregate(Sum('total_messages_count'))[
                        'total_messages_count__sum']

                    if previous_mis_objects_count == None:
                        previous_mis_objects_count = 0

                    today_mis_objects = previous_mis_objects_count + mis_objects.count()
                    last_7days_start = datetime_end - datetime.timedelta(14)
                    last_day_mis_objects = previous_mis_objects.filter(
                        date_message_analytics__lte=this_7days_start,
                        date_message_analytics__gt=last_7days_start).aggregate(Sum('total_messages_count'))[
                        'total_messages_count__sum']

                    if last_day_mis_objects == None:
                        last_day_mis_objects = 0

                    if last_day_mis_objects > 0:
                        percentage_change = round(100 * float(
                            today_mis_objects - last_day_mis_objects) / float(last_day_mis_objects), 2)
                    else:
                        percentage_change = "None"
                    percentage_change_type = 'Since last 7 days'
            else:
                month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
                    r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days + 1)).keys())

                total_hours_passed = datetime.datetime.today().hour + ((datetime.datetime.today().day - 1) * 24.0)

                start_month_date = datetime.datetime.today() - datetime.timedelta(datetime.datetime.today().day - 1)
                avg_msgs = math.ceil(((previous_mis_objects.filter(
                    date_message_analytics__gte=start_month_date).count() + mis_objects.count()) / total_hours_passed) * 24.0 * datetime.datetime.today().day) + 1

                for month in month_list:
                    temp_month = month_to_num_dict[month.split("-")[0]]
                    temp_year = int(month.split("-")[1])
                    date_filtered_mis_objects = previous_mis_objects.filter(
                        date_message_analytics__month=temp_month, date_message_analytics__year=temp_year)

                    total_messages = date_filtered_mis_objects.aggregate(
                        Sum('total_messages_count'))['total_messages_count__sum']

                    total_answered_messages = date_filtered_mis_objects.aggregate(
                        Sum('answered_query_count'))['answered_query_count__sum']
                    total_unanswered_messages = date_filtered_mis_objects.aggregate(
                        Sum('unanswered_query_count'))['unanswered_query_count__sum']
                    total_intuitive_messages = date_filtered_mis_objects.aggregate(
                        Sum('intuitive_query_count'))['intuitive_query_count__sum']
                    # false_positive_messages = mis_filtered_objs.filter(
                    #     flagged_queries_positive_type="1", creation_date__month=temp_month, creation_date__year=temp_year).count()

                    total_messages = return_zero_if_number_is_none(
                        total_messages)
                    total_answered_messages = return_zero_if_number_is_none(
                        total_answered_messages)
                    total_unanswered_messages = return_zero_if_number_is_none(
                        total_unanswered_messages)
                    total_intuitive_messages = return_zero_if_number_is_none(
                        total_intuitive_messages)
                    message_analytics_list.append({
                        "label": month,
                        "total_messages": total_messages,
                        "total_answered_messages": total_answered_messages,
                        "total_unanswered_messages": total_unanswered_messages,
                        "predicted_messages_no": total_messages,
                        "total_intuitive_messages": total_intuitive_messages
                        # "false_positive_messages": false_positive_messages
                    })

                if datetime_end == datetime.datetime.today().date():
                    message_analytics_list[-1]["predicted_messages_no"] = avg_msgs

                    date_filtered_mis_objects = mis_objects
                    total_messages = date_filtered_mis_objects.count()

                    total_unanswered_messages = date_filtered_mis_objects.filter(
                        intent_name=None, is_unidentified_query=True).count()

                    total_answered_messages = total_messages - total_unanswered_messages
                    message_analytics_list[-1]["total_messages"] = message_analytics_list[-1]["total_messages"] + total_messages
                    message_analytics_list[-1]["total_unanswered_messages"] = message_analytics_list[-1]["total_unanswered_messages"] + \
                        total_unanswered_messages
                    message_analytics_list[-1]["total_intuitive_messages"] = message_analytics_list[-1]["total_intuitive_messages"] + \
                        total_intuitive_messages
                    message_analytics_list[-1]["total_answered_messages"] = message_analytics_list[-1]["total_answered_messages"] + \
                        total_answered_messages
                    message_analytics_list[-1]["predicted_messages_no"] = avg_msgs
                    # message_analytics_list[-1]["false_positive_messages"] += date_filtered_mis_objects.filter(
                    #     flagged_queries_positive_type="1").count()

                    this_30days_start = datetime_end - datetime.timedelta(30)

                    previous_mis_objects_count = previous_mis_objects.filter(date_message_analytics__lte=datetime_end, date_message_analytics__gt=this_30days_start).aggregate(
                        Sum('total_messages_count'))['total_messages_count__sum']

                    if previous_mis_objects_count == None:
                        previous_mis_objects_count = 0

                    today_mis_objects = previous_mis_objects_count + mis_objects.count()

                    last_30days_start = datetime_end - datetime.timedelta(60)
                    last_day_mis_objects = previous_mis_objects.filter(date_message_analytics__lte=this_30days_start, date_message_analytics__gt=last_30days_start).aggregate(
                        Sum('total_messages_count'))['total_messages_count__sum']
                    if last_day_mis_objects == None:
                        last_day_mis_objects = 0

                    if last_day_mis_objects > 0:
                        percentage_change = round(100 * float(
                            today_mis_objects - last_day_mis_objects) / float(last_day_mis_objects), 2)
                    else:
                        percentage_change = "None"
                    percentage_change_type = 'Since last 30 days'

            response["message_analytics_list"] = message_analytics_list
            response["percentage_change"] = percentage_change
            response["percentage_change_type"] = percentage_change_type
            response["start_date"] = datetime_start.strftime("%d-%b-%y")
            response["end_date"] = datetime_end.strftime("%d-%b-%y")
            response["show_false_positive_analytics"] = bot_info_obj.enable_flagged_queries_status
            response["total_days"] = get_total_days_based_on_filter_type(filter_type, today_flag, no_days, message_analytics_list)

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetMessageAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': ''})

        end_time = time.time()
        time_taken = str(end_time - start_time_analytics)
        logger.info("Get Message Analytics Time Taken %s", time_taken, extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': ''})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetMessageAnalytics = GetMessageAnalyticsAPI.as_view()


class GetDeviceSpecificAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()
            
            bot_pk = validation_obj.remo_html_from_string(str(data["bot_pk"]))
            channel_name = validation_obj.remo_html_from_string(data["channel"])
            category_name = data["category_name"]
            selected_language = data["selected_language"]

            if channel_name.strip().lower() not in ["web", "all"]:
                response["status"] = 422
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            filter_type = data.get("filter_type", "1")  # Default Daily Analytics

            datetime_start, datetime_end, error_message = get_start_and_end_time(data)
            if error_message:
                return response, 400, error_message

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            category_obj = None
            if category_name != "All":
                category_obj = Category.objects.filter(
                    bot=uat_bot_obj, name=category_name).first()

            supported_languages = get_supported_languages_list(selected_language, Language)

            prod_bot_obj = None

            bot_objs = []
            if prod_bot_obj == None:
                bot_objs = [uat_bot_obj]
            else:
                bot_objs = [prod_bot_obj]

            mis_objects = return_mis_objects_based_on_category_channel_language(datetime.datetime.now().date(), datetime.datetime.now(
            ).date(), bot_objs, channel_name, "All", selected_language, supported_languages, MISDashboard, UserSessionHealth)

            previous_mis_objects = return_mis_daily_objects_based_on_filter(
                bot_objs, channel_name, category_name, category_obj, selected_language, supported_languages, MessageAnalyticsDaily)
            
            previous_unique_mis_objects = return_unique_users_objects_based_on_filter(
                bot_objs, channel_name, selected_language, supported_languages, UniqueUsers)

            device_specific_analytics_list, total_days = get_combined_device_specific_analytics_list(
                datetime_start, datetime_end, mis_objects, previous_mis_objects, previous_unique_mis_objects, filter_type, category_name)
            response["device_specific_analytics_list"] = device_specific_analytics_list
            response["start_date"] = datetime_start.strftime("%d-%b-%y")
            response["end_date"] = datetime_end.strftime("%d-%b-%y")
            response["total_days"] = total_days

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetDeviceSpecificAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': ''})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetDeviceSpecificAnalytics = GetDeviceSpecificAnalyticsAPI.as_view()


class GetCatalogueCombinedAnalyticsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(data["bot_pk"]))
            channel_name = validation_obj.remo_html_from_string(
                data["channel"])

            if channel_name.strip().lower() not in ["whatsapp", "all"]:
                response["status"] = 422
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            # Default Daily Analytics
            filter_type = data.get("filter_type", "1")

            datetime_start, datetime_end, error_message = get_start_and_end_time(
                data)
            if error_message:
                return response, 400, error_message

            bot_obj = Bot.objects.filter(
                pk=int(bot_pk), is_deleted=False, is_uat=True).first()

            if not bot_obj or request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = "You are not authorised to perform this operation."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            catalogue_analytics_list, total_days = get_combined_catalogue_analytics_list(
                datetime_start, datetime_end, bot_obj, filter_type)

            response["catalogue_analytics_list"] = catalogue_analytics_list
            response["start_date"] = datetime_start.strftime("%d-%b-%y")
            response["end_date"] = datetime_end.strftime("%d-%b-%y")
            response["total_days"] = total_days

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetDeviceSpecificAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': ''})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetCatalogueCombinedAnalytics = GetCatalogueCombinedAnalyticsAPI.as_view()


class GetSessionAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            prod_bot_obj = None

            bot_objs = []
            if prod_bot_obj == None:
                bot_objs = [uat_bot_obj]
            else:
                bot_objs = [prod_bot_obj]
            
            response, status, message = get_session_analytics_external(bot_objs[0], data)

            response["status"] = status

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetSessionAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetSessionAnalytics = GetSessionAnalyticsAPI.as_view()


class GetWordCloudDataAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        from itertools import groupby
        from operator import itemgetter
        from ast import literal_eval
        response = {}
        response['status'] = 500

        try:
            # username = request.user.username
            start_time_analytics = time.time()
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            channel_name = data["channel"]
            category_name = data["category_name"]
            selected_language = data["selected_language"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))
            channel_name = validation_obj.remo_html_from_string(channel_name)

            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()

            datetime_end = datetime.datetime.today().date()
            try:
                date_format = "%Y-%m-%d"
                start_date = data["start_date"]
                end_date = data["end_date"]
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("startdate and enddate is not in valid format %s at line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                pass

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            supported_languages_list = []
            if selected_language.lower() != "all":
                supported_languages_list = selected_language.split(",")
                supported_languages_list = [
                    lang.strip() for lang in supported_languages_list]

            supported_languages = Language.objects.filter(
                lang__in=supported_languages_list)

            if category_name != "All":
                category_obj = Category.objects.get(
                    name=category_name, bot=uat_bot_obj)

            word_cloud_array = []
            if channel_name != "All":
                word_cloud_objects = WordCloudAnalyticsDaily.objects.filter(
                    bot=uat_bot_obj, date__gte=datetime_start, date__lte=datetime_end,
                    channel=Channel.objects.get(name=channel_name))
            else:
                word_cloud_objects = WordCloudAnalyticsDaily.objects.filter(
                    bot=uat_bot_obj, date__gte=datetime_start, date__lte=datetime_end)

            if channel_name == "All" and category_name == "All":
                word_cloud_objects = WordCloudAnalyticsDaily.objects.filter(
                    bot=uat_bot_obj, date__gte=datetime_start, date__lte=datetime_end)
            elif channel_name == "All":
                word_cloud_objects = WordCloudAnalyticsDaily.objects.filter(
                    bot=uat_bot_obj, date__gte=datetime_start, date__lte=datetime_end, category=category_obj)
            elif category_name == "All":
                word_cloud_objects = WordCloudAnalyticsDaily.objects.filter(
                    bot=uat_bot_obj, date__gte=datetime_start, date__lte=datetime_end,
                    channel=Channel.objects.get(name=channel_name))
            else:
                word_cloud_objects = WordCloudAnalyticsDaily.objects.filter(
                    bot=uat_bot_obj, date__gte=datetime_start, date__lte=datetime_end, channel=Channel.objects.get(name=channel_name), category=category_obj)

            if selected_language.lower() != "all":
                word_cloud_objects = word_cloud_objects.filter(
                    selected_language__in=supported_languages)

            for item in word_cloud_objects:
                word_cloud_array = word_cloud_array + \
                    literal_eval(item.word_cloud_dictionary)

            get_name = itemgetter('word')
            result_wordcloud = [{'word': name, 'freq': str(sum(int(items['freq']) for items in word_dict))} for
                                name, word_dict in groupby(sorted(word_cloud_array, key=get_name), key=get_name)]

            response["wordcloud_data"] = result_wordcloud
            response["start_date"] = datetime_start.strftime("%d-%b-%y")
            response["end_date"] = datetime_end.strftime("%d-%b-%y")
            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetWordCloudDataAPI %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        end_time = time.time()
        time_taken = str(end_time - start_time_analytics)
        logger.info("Get Word Cloud Analytics Time Taken %s", time_taken, extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetWordCloudData = GetWordCloudDataAPI.as_view()


def GetUserFilterDashboard(request):
    try:
        if request.user.is_authenticated and request.method == "GET":
            bot_id = None
            channel_name = None
            selected_bot_obj = None
            user_history_list = []
            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            if not check_access_for_user(request.user, None, "Message History Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            bot_objs = Bot.objects.filter(
                users__in=[user_obj], is_deleted=False, is_uat=True)
            if 'bot_id' in request.GET:
                bot_id = request.GET['bot_id']

                channel_name = None
                if 'channel_name' in request.GET:
                    channel_name = request.GET['channel_name']

                is_filter_applied = False
                filter_type = "1"
                start_date = None
                end_date = None
                show_start_date = datetime.datetime.now().strftime('%m/%d/%Y')
                show_start_time = "12 : 00 AM"
                show_end_date = datetime.datetime.now().strftime('%m/%d/%Y')
                show_end_time = "11 : 59 PM"
                if 'filter_type' in request.GET:
                    filter_type = request.GET['filter_type']
                    is_filter_applied = True
                    if filter_type == "1":
                        start_date = (datetime.datetime.now() -
                                      datetime.timedelta(7)).date()
                        end_date = datetime.datetime.now().date()
                    elif filter_type == "2":
                        start_date = (datetime.datetime.now() -
                                      datetime.timedelta(30)).date()
                        end_date = datetime.datetime.now().date()
                    elif filter_type == "3":
                        start_date = (datetime.datetime.now() -
                                      datetime.timedelta(90)).date()
                        end_date = datetime.datetime.now().date()
                    elif filter_type == "5":
                        start_date = datetime.datetime.strptime(
                            request.GET['start_date'].replace("_", " "), '%m/%d/%Y %I:%M%p')
                        end_date = datetime.datetime.strptime(
                            request.GET['end_date'].replace("_", " "), '%m/%d/%Y %I:%M%p')
                        show_start_date = request.GET['start_date'].split("_")[
                            0].strip()
                        show_end_date = request.GET['end_date'].split("_")[
                            0].strip()
                        start_time = request.GET['start_date'].split("_")[
                            1].strip()
                        show_start_time = start_time[0: 2] + " : " + \
                            start_time[3: 5] + " " + start_time[5:7]
                        end_time = request.GET['end_date'].split("_")[
                            1].strip()
                        show_end_time = end_time[0: 2] + " : " + \
                            end_time[3: 5] + " " + end_time[5:7]

                selected_channels = []
                if 'channels' in request.GET:
                    selected_channels = request.GET['channels'].split(" ")
                    selected_channels = [channel.replace(
                        "_", " ") for channel in selected_channels]
                    is_filter_applied = True

                username = request.user.username
                user_obj = User.objects.get(username=str(username))

                bot_objs = Bot.objects.filter(
                    users__in=[user_obj], is_deleted=False, is_uat=True)

                selected_bot_obj = None
                if bot_id != None:
                    selected_bot_obj = Bot.objects.get(
                        pk=int(bot_id), is_deleted=False, is_uat=True)

                user_history_list = []
                if selected_bot_obj != None:
                    if not check_access_for_user(request.user, selected_bot_obj.pk, "Message History Related"):
                        return HttpResponseNotFound("You do not have access to this page")
                    user_history_list = Profile.objects.filter(
                        bot__in=[selected_bot_obj]).exclude(user_pipe="").order_by('-last_message_date')
                else:
                    user_history_list = Profile.objects.filter(
                        bot__in=bot_objs).exclude(user_pipe="").order_by('-last_message_date')
                if channel_name != None:
                    user_history_list = user_history_list.filter(
                        channel__name=channel_name)

                if start_date != None:
                    if filter_type == "5":
                        user_history_list = user_history_list.filter(
                            last_message_date__gte=start_date)
                    else:
                        user_history_list = user_history_list.filter(
                            last_message_date__gte=start_date)
                if end_date != None:
                    if filter_type == "5":
                        user_history_list = user_history_list.filter(
                            last_message_date__lte=end_date)
                    else:
                        user_history_list = user_history_list.filter(
                            last_message_date__lte=end_date)
                if selected_channels != []:
                    user_history_list = user_history_list.filter(
                        channel__name__in=selected_channels)

                unique_user_id = list(
                    user_history_list.values_list("user_id", flat=True))
                
                template_to_render = 'EasyChatApp/analytics/user_filter.html'
                if (selected_bot_obj.static_analytics):
                    user_history_list = STATIC_EASYCHAT_USER_FILTERED_MESSAGE_DUMMY_DATA
                    template_to_render = 'EasyChatApp/analytics/static_user_filter.html'

                paginator = Paginator(
                    unique_user_id, MAX_MESSAGE_PER_PAGE)
                page = request.GET.get('page')

                try:
                    unique_user_id = paginator.page(page)
                except PageNotAnInteger:
                    unique_user_id = paginator.page(1)
                except EmptyPage:
                    unique_user_id = paginator.page(paginator.num_pages)

                user_history_list = []
                for user_id in unique_user_id:
                    mis_obj = MISDashboard.objects.filter(
                        bot=selected_bot_obj, user_id=user_id).first()
                    if not mis_obj:
                        continue
                    user_history_list.append([user_id, mis_obj.get_bot_response()])

            manage_intents_permission = False
            if check_access_for_user(request.user, selected_bot_obj.pk, "Intent Related"):
                manage_intents_permission = True

            if start_date == None and end_date == None:
                start_date = (datetime.datetime.now() -
                              datetime.timedelta(7)).date()
                end_date = datetime.datetime.now().date()

            channel_list = get_channel_list(Channel)

            return render(request, template_to_render, {
                "bot_objs": bot_objs,
                "selected_bot_obj": selected_bot_obj,
                "user_history_list": user_history_list,
                "get_bot_related_access_perm": request.user.get_bot_related_access_perm(),
                "manage_intents_permission": manage_intents_permission,
                "is_filter_applied": is_filter_applied,
                "filter_type": filter_type,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "selected_channels": selected_channels,
                "show_start_date": show_start_date,
                "show_end_date": show_end_date,
                "show_start_time": show_start_time,
                "show_end_time": show_end_time,
                "channel_list": channel_list,
                "unique_user_id": unique_user_id,
            })

        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE] %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET['bot_id'])})
        # return HttpResponseNotFound(INVALID_REQUEST)
        return render(request, 'EasyChatApp/error_500.html')


class GetFormAssistAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            dropdown_language = "en"
            search_term = data.get("search", "")
            if "dropdown_language" in data:
                dropdown_language = data["dropdown_language"]
            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))
            search_term = validation_obj.remo_html_from_string(search_term)

            uat_bot_obj = []
            try:
                uat_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True, is_form_assist_enabled=True)
            except Exception:
                response["status"] = 301
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            
            response, status, message = get_form_assist_intent_data_external(uat_bot_obj, data, dropdown_language)

            response["language_script_type"] = "ltr"
            if status == 200:
                lang_obj = Language.objects.filter(
                    lang=dropdown_language).first()
                if lang_obj:
                    response["language_script_type"] = lang_obj.language_script_type
                response["status"] = 200
            else:
                response["status"] = 300
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetFormAssistAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetFormAssistAnalytics = GetFormAssistAnalyticsAPI.as_view()


class ExportFormAssistIntentAPI(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            selected_language = data["selected_language"]
            dropdown_language = data["dropdown_language"]
            supported_languages_list = []
            is_language_filter_applied = False
            if selected_language.lower() != "all":
                is_language_filter_applied = True
                supported_languages_list = selected_language.split(",")
                supported_languages_list = [
                    lang.strip() for lang in supported_languages_list]

            supported_languages = Language.objects.filter(
                lang__in=supported_languages_list)

            start_date = data["start_date"]
            end_date = data["end_date"]
            datetime_start = start_date.split("-")
            start_date = datetime.datetime(int(datetime_start[0]), int(
                datetime_start[1]), int(datetime_start[2]))
            datetime_end = end_date.split("-")
            end_date = datetime.datetime(int(datetime_end[0]), int(
                datetime_end[1]), int(datetime_end[2]))
            email_id = data["email_id"]
            if request.user.email == "" or request.user.email == None:
                request.user.email = email_id
            diff_in_days = (end_date - start_date).days

            if diff_in_days <= 30:
                file_url = export_form_assist_intent(
                    Bot, Intent, FormAssist, FormAssistAnalytics, bot_pk, str(request.user.username),
                    is_language_filter_applied, supported_languages, dropdown_language, email_id, False)
                response["file_url"] = file_url
                if file_url != "":
                    response["status"] = 200
            else:
                thread = threading.Thread(target=export_form_assist_intent, args=(Bot, Intent, FormAssist, FormAssistAnalytics, bot_pk, str(request.user.username), is_language_filter_applied, supported_languages, dropdown_language, email_id, True), daemon=True)
                thread.start()

                response["status"] = 200
                response["email_id"] = email_id

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportFormAssistIntentAPI %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ExportFormAssistIntent = ExportFormAssistIntentAPI.as_view()


class ExportEasyChatNpsExcelAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]

            file_url = export_easy_chat_nps_excel(
                Bot, Feedback, bot_pk, str(request.user.username))

            response['file_url'] = file_url
            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportEasyChatNpsExcelAPI %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ExportEasyChatNpsExcel = ExportEasyChatNpsExcelAPI.as_view()


class FetchIntentsOfBotSelectedAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            bot_pk = None
            bot_pk = request.data['bot_pk']
            logger.info(bot_pk, extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
            bot_obj = Bot.objects.filter(pk=bot_pk)
            intent_objs = Intent.objects.filter(
                bots__in=bot_obj, is_deleted=False).values('pk', 'name')

            response['intents'] = intent_objs
            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("MatchMessageWithIntentAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        return Response(data=response)


FetchIntentsOfBotSelected = FetchIntentsOfBotSelectedAPI.as_view()


class MatchMessageWithIntentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            # logger.info(request.data)
            intent_pk = request.data['intent_pk']
            message_history_ids = request.POST.getlist('message_history_ids[]')

            if not message_history_ids:
                message_history_ids = request.data['message_history_ids']
            # logger.info(message_history_ids)
            intent_obj = Intent.objects.get(pk=int(intent_pk))
            mis_objs = MISDashboard.objects.filter(pk__in=message_history_ids)
            # logger.info(MISDashboard.objects.all().values('pk'))
            # logger.info(mis_objs)
            if not mis_objs:
                logger.error("Matching MISDashboard Object not found.", extra={
                    'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                return Response(data=response)

            training_data = json.loads(intent_obj.training_data)
            logger.info(training_data, extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            key = int(list(training_data.keys())[-1]) + 1
            # logger.info(mis_objs)
            message_not_matched = []
            action_taken = {}
            for mis_obj in mis_objs:
                # logger.info(mis_obj.pk)
                message = mis_obj.get_message_received()
                if message not in training_data.values():
                    training_data[str(key)] = message
                    key += 1
                    mis_obj.set_action_taken_list(intent_obj, 'match')
                else:
                    message_not_matched.append(message)
                    response['status'] = 300

                action_taken[mis_obj.pk] = mis_obj.get_action_taken_list()

            intent_obj.training_data = json.dumps(training_data)
            intent_obj.save()

            if response['status'] != 300:
                response['status'] = 200
            else:
                response['message_not_matched'] = message_not_matched

            response['action_taken'] = action_taken
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("FetchIntentsOfBotSelectedAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response['error_message'] = "FetchIntentsOfBotSelectedAPI" + \
                str(e) + " " + str(exc_tb.tb_lineno)

        logger.error(response, extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return Response(data=response)


MatchMessageWithIntent = MatchMessageWithIntentAPI.as_view()


def GetNPSAnalytics(request, *args, **kwargs):
    try:
        # username = request.user.username
        # print(request.user.is_authenticated)
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/chat/login/')

        if not check_access_for_user(request.user, None, "Analytics Related", "overall"):
            return render(request, 'EasyChatApp/unauthorized.html')

        bot_pk = None

        if "bot_pk" in request.GET:
            selected_bot_id = request.GET.getlist("bot_pk")[0]
            if not check_access_for_user(request.user, selected_bot_id, "Analytics Related"):
                return render(request, 'EasyChatApp/unauthorized.html')
        else:
            return HttpResponseNotFound("You haven't provided valid bot id.")

        bot_pk = request.GET["bot_pk"]
        page_count = request.GET.get("count", MAX_MESSAGE_PER_PAGE)

        if page_count not in ["10", "25", "50", "75", "100"]:
            page_count = "10"

        nps_score = None
        start_date = None
        end_date = None
        filter_type = None
        channels = []
        is_result_filtered = False

        if "page" in request.GET:
            page = request.GET["page"]

        if "filter_type" in request.GET:
            filter_type = request.GET['filter_type']
            is_result_filtered = True
            if filter_type == "1":
                start_date = (datetime.datetime.now() -
                              datetime.timedelta(7)).date()
                end_date = datetime.datetime.now().date()
            elif filter_type == "2":
                start_date = (datetime.datetime.now() -
                              datetime.timedelta(30)).date()
                end_date = datetime.datetime.now().date()
            elif filter_type == "3":
                start_date = (datetime.datetime.now() -
                              datetime.timedelta(90)).date()
                end_date = datetime.datetime.now().date()
            elif filter_type == "5":
                start_date = datetime.datetime.strptime(
                    request.GET['start_date'], '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(
                    request.GET['end_date'], '%Y-%m-%d').date()

        if "nps_score" in request.GET:
            nps_score = request.GET["nps_score"]
            is_result_filtered = True

        if "channels" in request.GET:
            channels = request.GET['channels'].split(" ")
            channels = [channel.replace("_", " ") for channel in channels]
            is_result_filtered = True

        bot_obj = Bot.objects.get(pk=int(bot_pk))

        feedback_objs = []

        if not is_result_filtered:
            feedback_objs = Feedback.objects.filter(
                bot=bot_obj).order_by("-date")
        else:

            feedback_objs = Feedback.objects.filter(
                bot=bot_obj).order_by('-date')

            if nps_score != None:

                if nps_score == "Demoters":
                    feedback_objs_nps = Feedback.objects.filter(
                        bot=bot_obj, rating__lte=2).order_by('-date')
                    feedback_objs = feedback_objs_nps

                if nps_score == "Promoters":
                    feedback_objs_nps_rating_4 = Feedback.objects.filter(
                        bot=bot_obj, rating__gte=3, scale_rating_5=False)

                    feedback_objs_nps_rating_5 = Feedback.objects.filter(
                        bot=bot_obj, rating__gte=4, scale_rating_5=True)

                    feedback_objs_nps = feedback_objs_nps_rating_4 | feedback_objs_nps_rating_5

                    feedback_objs_nps = feedback_objs_nps.order_by('-date')

                    feedback_objs = feedback_objs_nps

                if nps_score == "Passives":
                    feedback_objs_nps = Feedback.objects.filter(
                        bot=bot_obj, rating=3, scale_rating_5=True).order_by('-date')
                    feedback_objs = feedback_objs_nps

            if start_date != None and end_date != None:
                feedback_objs = feedback_objs.filter(
                    date__date__gte=start_date, date__date__lte=end_date)
            if len(channels) >= 1:
                channel_objs = Channel.objects.filter(name__in=channels)
                feedback_objs = feedback_objs.filter(channel__in=channel_objs)

        paginator = Paginator(feedback_objs, page_count)

        last_month_start_datetime = (
            datetime.datetime.today() - datetime.timedelta(30)).date()

        default_analytics_start_datetime = (
            datetime.datetime.today() - datetime.timedelta(7)).date()

        default_analytics_end_datetime = datetime.datetime.today().date()

        try:
            feedback_objs = paginator.page(page)
        except PageNotAnInteger:
            feedback_objs = paginator.page(1)
        except EmptyPage:
            feedback_objs = paginator.page(
                paginator.num_pages)
        if start_date == None and end_date == None:
            start_date = (datetime.datetime.now() -
                          datetime.timedelta(7)).date()
            end_date = datetime.datetime.now().date()
        return render(request, "EasyChatApp/platform/nps_analytics.html", {
            "feedback_objs": feedback_objs,
            "is_result_filtered": is_result_filtered,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "DEFAULT_ANALYTICS_START_DATETIME": default_analytics_start_datetime,
            "DEFAULT_ANALYTICS_END_DATETIME": default_analytics_end_datetime,
            "LAST_MONTH_START_DATETIME": last_month_start_datetime,
            "selected_bot_id": bot_pk,
            "selected_bot_obj": bot_obj,
            "filter_type": filter_type,
            "channels": channels,
            "nps_score": nps_score
        })

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[NLP]: Error GetNPSAnalytics %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        # return HttpResponseNotFound("Internal Server Error")
        return render(request, 'EasyChatApp/error_500.html')


def FlowAnalyticsView(request, *args, **kwargs):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Analytics Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            intent_id = request.GET['intent_pk']
            intent_obj = Intent.objects.get(pk=intent_id)
            bot_id = request.GET['bot_pk']
            dropdown_language = request.GET["dropdown_language"]

            root_tree_obj = Intent.objects.get(pk=intent_id).tree

            last_month_start_datetime = (
                datetime.datetime.today() - datetime.timedelta(30)).date()
            last3_month_start_datetime = (
                datetime.datetime.today() - datetime.timedelta(3 * 30)).date()

            default_analytics_start_datetime = (
                datetime.datetime.today() - datetime.timedelta(7)).date()

            default_analytics_end_datetime = datetime.datetime.today().date()
            selected_bot_obj = Bot.objects.get(pk=bot_id, is_deleted=False)

            bot_channel_objs = BotChannel.objects.filter(bot=selected_bot_obj)

            go_live_date = selected_bot_obj.go_live_date

            start_date = ""
            date_end = ""
            if "start_date" in request.GET and "date_end" in request.GET:
                start_date = request.GET["start_date"]
                date_end = request.GET["date_end"]
                daily_flow_analytics_start_date = request.GET["start_date"]
                daily_flow_analytics_end_date = request.GET["date_end"]
                channel_objs = Channel.objects.filter(is_easychat_channel=True)
                channel_filter = []
                date_filter = ""
                channel_value = ""
                if "channel" in request.GET:
                    channel_value = request.GET["channel"]
                    channel_value = channel_value.split(',')
                    if channel_value == ['']:
                        channel_objs = Channel.objects.filter(
                            is_easychat_channel=True)
                    else:
                        channel_objs = Channel.objects.filter(
                            name__in=channel_value)
                if "channel_filter" in request.GET:
                    channel_filter = request.GET["channel_filter"]
                    channel_filter = channel_filter.split(',')
                if "date_filter" in request.GET:
                    date_filter = request.GET["date_filter"]
                try:
                    start_date = datetime.datetime.strptime(
                        start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
                    daily_flow_analytics_start_date = datetime.datetime.strptime(
                        daily_flow_analytics_start_date, "%Y-%m-%d")
                    daily_flow_analytics_end_date = datetime.datetime.strptime(
                        daily_flow_analytics_end_date, "%Y-%m-%d")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("Need to convert to correct format %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                        'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
                    start_date = datetime.datetime.strptime(
                        start_date, "%d-%b-%y").strftime("%Y-%m-%d")
                    date_end = datetime.datetime.strptime(
                        date_end, "%d-%b-%y").strftime("%Y-%m-%d")
                    daily_flow_analytics_start_date = datetime.datetime.strptime(
                        daily_flow_analytics_start_date, "%d-%b-%y")
                    daily_flow_analytics_end_date = datetime.datetime.strptime(
                        daily_flow_analytics_end_date, "%d-%b-%y")

                flow_analytics_objects = DailyFlowAnalytics.objects.filter(
                    intent_indentifed=intent_obj, created_time__date__gte=daily_flow_analytics_start_date.date(), created_time__date__lte=daily_flow_analytics_end_date.date(), channel__in=channel_objs)

                flow_analytics_objects_that_day = FlowAnalytics.objects.none()
                if date_end == datetime.datetime.now().strftime("%Y-%m-%d"):
                    flow_analytics_objects_that_day = FlowAnalytics.objects.filter(intent_indentifed=intent_obj, created_time__date=daily_flow_analytics_end_date.date(), channel__in=channel_objs)
                
                flow_termination_data_objs = FlowTerminationData.objects.filter(
                    intent=intent_obj, created_datetime__date__gte=daily_flow_analytics_start_date.date(), created_datetime__date__lte=daily_flow_analytics_end_date.date(), channel__in=channel_objs)
            else:
                flow_analytics_objects = DailyFlowAnalytics.objects.filter(
                    intent_indentifed=intent_obj)
                flow_analytics_objects_that_day = FlowAnalytics.objects.filter(
                    intent_indentifed=intent_obj, created_datetime__date=datetime.datetime.now().date())
                flow_termination_data_objs = FlowTerminationData.objects.filter(
                    intent=intent_obj)

            # times the intent was called
            count_intent_was_called = 0
            try:
                count_intent_was_called = flow_analytics_objects.filter(
                    current_tree=intent_obj.tree).aggregate(Sum('count'))['count__sum']
                if count_intent_was_called == None:
                    count_intent_was_called = 0
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Flow Analytics Intent count problem %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})
                pass
            try:
                count_intent_was_called += flow_analytics_objects_that_day.filter(
                    current_tree=intent_obj.tree).count()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Flow Analytics Intent count problem that day %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})
                count_intent_was_called = 0
                pass
            translate_api_status = True
            json_resp, max_level, translate_api_status = get_child_tree_objs_flow_analytics(root_tree_obj.pk, root_tree_obj, [
            ], flow_analytics_objects, flow_analytics_objects_that_day, flow_termination_data_objs, intent_obj, count_intent_was_called, [], [], True, 1, 0, 0, dropdown_language, translate_api_status)

            try:
                first_object_created_date = str(DailyFlowAnalytics.objects.filter(
                    intent_indentifed=intent_obj).first().created_time).split(" ")[0]
                last_object_created_date = str(DailyFlowAnalytics.objects.filter(
                    intent_indentifed=intent_obj).last().created_time).split(" ")[0]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Date Issue %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})
                first_object_created_date = datetime.datetime.now().date()
                last_object_created_date = datetime.datetime.now().date()
                pass

            channel_list = get_channel_list(Channel)
            if translate_api_status:
                status = 200
            else:
                status = 300

            return render(request, 'EasyChatApp/analytics/revised_flow_analytics.html',
                          {"flow_tree_data": json.dumps(json_resp),
                           "intent_id": intent_id,
                           "first_object_created_date": first_object_created_date,
                           "last_object_created_date": last_object_created_date,
                           "start_date": start_date,
                           "end_date": date_end,
                           "bot_id": bot_id,
                           "count_intent_was_called": count_intent_was_called,
                           "DEFAULT_ANALYTICS_START_DATETIME": default_analytics_start_datetime,
                           "DEFAULT_ANALYTICS_END_DATETIME": default_analytics_end_datetime,
                           "LAST_MONTH_START_DATETIME": last_month_start_datetime,
                           "LAST3_MONTH_START_DATETIME": last3_month_start_datetime,
                           "go_live_date": go_live_date,
                           "bot_channel_objs": bot_channel_objs,
                           "date_filter": date_filter,
                           "channel_filter": channel_filter,
                           "max_level": max_level,
                           "channel_list": channel_list,
                           "status": status,
                           "dropdown_language": dropdown_language
                           })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Flow Analytics %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})
        # return HttpResponseNotFound("Internal Server Error")
        return render(request, 'EasyChatApp/error_500.html')


def DownloadUserAnalyticsExcel(request, *args, **kwargs):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Analytics Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")

            intent_id = request.GET["intent_pk"]
            startdate = request.GET["startdate"]
            enddate = request.GET["enddate"]
            channel_list = request.GET["channel"]
            selected_language = "en"
            if "selected_language" in request.GET:
                selected_language = request.GET["selected_language"]
            if "dropdown_language" in request.GET:
                selected_language = request.GET["dropdown_language"]
            channel_list = channel_list.split(',')

            from xlwt import Workbook

            automated_email_wb = Workbook()
            sheet1 = automated_email_wb.add_sheet("Analytics ")
            sheet1.write(0, 0, "Parent")
            sheet1.col(0).width = 256 * 75
            sheet1.write(0, 1, "Child")
            sheet1.col(1).width = 256 * 75
            sheet1.write(0, 2, "Count")
            sheet1.col(2).width = 256 * 75
            sheet1.write(0, 3, "Total Transaction")
            sheet1.col(3).width = 256 * 75
            intent_obj = Intent.objects.get(pk=intent_id)

            if channel_list == ['']:
                channel_objs = Channel.objects.filter(is_easychat_channel=True)
            else:
                channel_objs = Channel.objects.filter(name__in=channel_list)

            if startdate == "" and enddate == "":
                start_date = startdate
                date_end = enddate
                daily_flow_analytics_start_date = startdate
                daily_flow_analytics_end_date = enddate
                try:
                    start_date = datetime.datetime.strptime(
                        start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
                    daily_flow_analytics_start_date = datetime.datetime.strptime(
                        daily_flow_analytics_start_date, "%Y-%m-%d")
                    daily_flow_analytics_end_date = datetime.datetime.strptime(
                        daily_flow_analytics_end_date, "%Y-%m-%d")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("Need to convert to correct format %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                        'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
                    start_date = datetime.datetime.strptime(
                        start_date, "%d-%b-%y").strftime("%Y-%m-%d")
                    date_end = datetime.datetime.strptime(
                        date_end, "%d-%b-%y").strftime("%Y-%m-%d")
                    daily_flow_analytics_start_date = datetime.datetime.strptime(
                        daily_flow_analytics_start_date, "%d-%b-%y")
                    daily_flow_analytics_end_date = datetime.datetime.strptime(
                        daily_flow_analytics_end_date, "%d-%b-%y")

                daily_flow_analytics_start_date = (
                    daily_flow_analytics_start_date + datetime.timedelta(1)).strftime("%Y-%m-%d")
                daily_flow_analytics_end_date = (
                    daily_flow_analytics_end_date + datetime.timedelta(1)).strftime("%Y-%m-%d")
                flow_analytics_objects = DailyFlowAnalytics.objects.filter(
                    intent_indentifed=intent_obj, created_time__date__gte=daily_flow_analytics_start_date, created_time__date__lte=daily_flow_analytics_end_date, channel__in=channel_objs)
                flow_analytics_objects_that_day = FlowAnalytics.objects.filter(
                    intent_indentifed=intent_obj, channel__in=channel_objs, created_time__date=datetime.datetime.now().date())
                startdate = daily_flow_analytics_start_date
                enddate = daily_flow_analytics_end_date
            else:
                flow_analytics_objects = DailyFlowAnalytics.objects.filter(
                    intent_indentifed=intent_obj, created_time__date__gte=startdate, created_time__date__lte=enddate, channel__in=channel_objs)
                flow_analytics_objects_that_day = FlowAnalytics.objects.none()
                if enddate == datetime.datetime.now().strftime("%Y-%m-%d"):
                    flow_analytics_objects_that_day = FlowAnalytics.objects.filter(intent_indentifed=intent_obj, created_time__date=enddate, channel__in=channel_objs)
            root_tree_obj = Intent.objects.get(pk=intent_id).tree
            list_child_parent_pair = get_parent_child_pair(
                root_tree_obj, [], [])
            index = 0
            translate_api_status = True
            for item in list_child_parent_pair:
                count = 0
                total_transaction = 0
                if flow_analytics_objects.filter(previous_tree=item[0], current_tree=item[1]):
                    count = flow_analytics_objects.filter(
                        previous_tree=item[0], current_tree=item[1]).aggregate(Sum('count'))
                    count = count['count__sum']
                    total_transaction = flow_analytics_objects.filter(
                        previous_tree=item[0], current_tree=item[1]).aggregate(Sum('total_sum'))
                    total_transaction = total_transaction['total_sum__sum']

                if flow_analytics_objects_that_day.filter(previous_tree=item[0], current_tree=item[1]):
                    count += flow_analytics_objects_that_day.filter(
                        previous_tree=item[0], current_tree=item[1]).count()
                    total_transaction += flow_analytics_objects_that_day.filter(
                        previous_tree=item[0], current_tree=item[1]).aggregate(Sum('flow_analytics_variable'))[
                        'flow_analytics_variable__sum']

                if count > 0:
                    if selected_language == "en":
                        sheet1.write(index + 1, 0, item[0].name)
                        sheet1.write(index + 1, 1, item[1].name)
                    if selected_language != "en" and translate_api_status:
                        parent_name, translate_api_status = get_multilingual_tree_obj_name(
                            item[0], selected_language, translate_api_status)
                        child_name, translate_api_status = get_multilingual_tree_obj_name(
                            item[1], selected_language, translate_api_status)
                        sheet1.write(index + 1, 0, parent_name)
                        sheet1.write(index + 1, 1, child_name)
                    sheet1.write(index + 1, 2, count)
                    sheet1.write(
                        index + 1, 3, total_transaction)
                    index += 1

            # Adding abort flow sheet to node analytics excel
            abort_flow_sheet = automated_email_wb.add_sheet(
                "Abort or Terminate Flow ")
            add_abort_flow_sheet(intent_id, startdate, enddate, channel_objs,
                                 abort_flow_sheet, FlowTerminationData, Tree, Intent)

            filename = "files/BotUserFlowAnalytics.xls"
            if os.path.isfile(filename) == False:
                open(filename, 'w+')
            automated_email_wb.save(filename)

            response = FileResponse(open(filename, 'rb'))
            response['Content-Type'] = 'application/octet-stream'
            response[
                'Content-Disposition'] = 'attachment;filename="IntentWiseUserFlow.xls"'
            response['Content-Length'] = os.path.getsize(filename)

            return response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Flow Analytics %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})
        # return HttpResponseNotFound("Internal Server Error")
        return render(request, 'EasyChatApp/error_500.html')


def DownloadUserSpecificDropoff(request, *args, **kwargs):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Analytics Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")

            intent_id = request.GET["intent_pk"]
            startdate = request.GET["startdate"]
            enddate = request.GET["enddate"]
            channel_list = request.GET["channel"]
            selected_language = "en"
            if "selected_language" in request.GET:
                selected_language = request.GET["selected_language"]
            if "dropdown_language" in request.GET:
                selected_language = request.GET["dropdown_language"]

            channel_list = channel_list.split(',')

            if channel_list == ['']:
                channel_objs = Channel.objects.filter(is_easychat_channel=True)
            else:
                channel_objs = Channel.objects.filter(name__in=channel_list)

            if startdate == "" and enddate == "":
                start_date = startdate
                end_date = enddate
                try:
                    start_date = datetime.datetime.strptime(
                        start_date, "%Y-%m-%d")
                    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("Need to convert to correct format %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                   'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})
                    start_date = datetime.datetime.strptime(
                        start_date, "%d-%b-%y").strftime("%Y-%m-%d")
                    end_date = datetime.datetime.strptime(
                        end_date, "%d-%b-%y").strftime("%Y-%m-%d")
                startdate = start_date
                enddate = end_date
            try:
                today_date = datetime.datetime.today().date().strftime("%Y-%m-%d")
                if datetime.datetime.strptime(enddate, "%Y-%m-%d").strftime("%Y-%m-%d") == today_date:
                    enddate = datetime.datetime.now() - datetime.timedelta(days=1)
                    enddate = enddate.strftime("%Y-%m-%d")
            except:
                enddate = datetime.datetime.now() - datetime.timedelta(days=1)
                enddate = enddate.strftime("%Y-%m-%d")

            data = {
                'Date & Time': [],
                'User-ID': [],
                'Channel': [],
                'Parent Intent': [],
                'Child Intent': [],
                'Drop-off type': [],
                'Intent Name/Flow Termination Keyword': []
            }
            dropoff_type = ["Terminate", "Timeout", "Miscellaneous"]
            est = pytz.timezone(settings.TIME_ZONE)
            flow_dropoff_objs = UserFlowDropOffAnalytics.objects.filter(
                intent_indentifed__pk=intent_id, created_datetime__date__gte=startdate, created_datetime__date__lte=enddate, channel__in=channel_objs)
            for flow_dropoff_obj in flow_dropoff_objs:
                data['Date & Time'].append(str(flow_dropoff_obj.created_datetime.astimezone(
                    est).strftime("%Y-%m-%d %H:%M:%S")))
                data['User-ID'].append(str(flow_dropoff_obj.user.user_id))
                data['Channel'].append(str(flow_dropoff_obj.channel.name))

                if selected_language == "en":
                    data['Parent Intent'].append(
                        str(flow_dropoff_obj.previous_tree.name))
                    data['Child Intent'].append(
                        str(flow_dropoff_obj.current_tree.name))
                    data['Intent Name/Flow Termination Keyword'].append(
                        str(flow_dropoff_obj.intent_name))
                else:
                    parent_intent_name, _ = get_multilingual_tree_obj_name(
                        flow_dropoff_obj.previous_tree, selected_language, True)
                    data['Parent Intent'].append(str(parent_intent_name))
                    child_intent_name, _ = get_multilingual_tree_obj_name(
                        flow_dropoff_obj.current_tree, selected_language, True)
                    data['Child Intent'].append(str(child_intent_name))
                    intent_name, _ = get_translated_text_with_api_status(str(
                        flow_dropoff_obj.intent_name), selected_language, EasyChatTranslationCache, True)
                    data['Intent Name/Flow Termination Keyword'].append(
                        str(intent_name))

                data['Drop-off type'].append(
                    dropoff_type[int(flow_dropoff_obj.dropoff_type) - 1])

            flow_termination_objs = FlowTerminationData.objects.filter(
                intent__pk=intent_id, created_datetime__date__gte=startdate, created_datetime__date__lte=enddate, channel__in=channel_objs)
            for flow_termination_obj in flow_termination_objs:
                parent_tree_list = flow_termination_obj.tree.tree_set.all()
                if parent_tree_list.count() == 0:
                    parent_tree = flow_termination_obj.tree
                else:
                    parent_tree = parent_tree_list[0]
                data['Date & Time'].append(str(flow_termination_obj.created_datetime.astimezone(
                    est).strftime("%Y-%m-%d %H:%M:%S")))
                if flow_termination_obj.user != None:
                    data['User-ID'].append(str(flow_termination_obj.user.user_id))
                else:
                    data['User-ID'].append("-")
                data['Channel'].append(str(flow_termination_obj.channel.name))

                if selected_language == "en":
                    data['Parent Intent'].append(str(parent_tree.name))
                    data['Child Intent'].append(
                        str(flow_termination_obj.tree.name))
                    data['Intent Name/Flow Termination Keyword'].append(
                        str(flow_termination_obj.termination_message))
                else:
                    parent_tree_name, _ = get_multilingual_tree_obj_name(
                        parent_tree, selected_language, True)
                    data['Parent Intent'].append(str(parent_tree_name))
                    child_intent_name, _ = get_multilingual_tree_obj_name(
                        flow_termination_obj.tree, selected_language, True)
                    data['Child Intent'].append(str(child_intent_name))
                    intent_name, _ = get_translated_text_with_api_status(str(
                        flow_termination_obj.termination_message), selected_language, EasyChatTranslationCache, True)
                    data['Intent Name/Flow Termination Keyword'].append(
                        intent_name)

                data['Drop-off type'].append(dropoff_type[0])

            import pandas as pd

            df = pd.DataFrame(data)
            df.sort_values([df.columns[1], df.columns[0]],
                           axis=0,
                           ascending=[True, True],
                           inplace=True)
            filename = settings.SECURE_MEDIA_ROOT + "EasyChatApp/User_dropoff_analytics_from_" + str(datetime.datetime.strptime(
                startdate, "%Y-%m-%d").strftime("%d-%m-%Y")) + " to " + str((datetime.datetime.strptime(enddate, "%Y-%m-%d")).strftime("%d-%m-%Y")) + ".csv"
            df.to_csv(filename, index=False)

            response = FileResponse(open(filename, 'rb'))
            response['Content-Type'] = 'application/octet-stream'
            response[
                'Content-Disposition'] = 'attachment;filename="User_dropoff_analytics_from_' + str(datetime.datetime.strptime(startdate, "%Y-%m-%d").strftime("%d-%m-%Y")) + ' to ' + str((datetime.datetime.strptime(enddate, "%Y-%m-%d")).strftime("%d-%m-%Y")) + '.csv"'
            response['Content-Length'] = os.path.getsize(filename)
            return response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In DownloadUserSpecificDropoff %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})
        return render(request, 'EasyChatApp/error_500.html')


class FlowAnalyticsStatsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            bot_pk = request.GET["bot_pk"]
            page = request.GET["page"]
            channel_name = request.GET["channel_name"]
            category_name = request.GET["category_name"]
            dropdown_language = request.GET["dropdown_language"]
            selected_language = "All"
            supported_languages_list = []
            search_term = request.GET["search"]
            if "selected_language" in request.GET:
                selected_language = request.GET["selected_language"]
                if selected_language.lower() != "all":
                    supported_languages_list = selected_language.split(",")
                    supported_languages_list = [
                        lang.strip() for lang in supported_languages_list]

            supported_languages = Language.objects.filter(
                lang__in=supported_languages_list)

            bot_objs = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            start_date = request.GET["start_date"]
            end_date = request.GET["end_date"]

            if start_date:
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

            if end_date:
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

            translate_api_call_status = True
            intent_with_children_name_pk_occurences, translate_api_call_status = return_intent_with_children_name_pk_occurences(
                start_date, end_date, category_name, channel_name, bot_objs, selected_language, supported_languages,
                dropdown_language, translate_api_call_status, search_term)
            intent_with_children_name_pk_occurences.sort(
                key=lambda x: x[2], reverse=True)
            paginator = Paginator(intent_with_children_name_pk_occurences, 5)
            no_pages = paginator.num_pages

            is_last_page = False
            if int(page) >= int(no_pages):
                is_last_page = True

            try:
                intent_with_children_name_pk_occurences = paginator.page(page)
            except PageNotAnInteger:
                intent_with_children_name_pk_occurences = paginator.page(1)
            except EmptyPage:
                intent_with_children_name_pk_occurences = paginator.page(
                    paginator.num_pages)

            response["is_single_page"] = False
            if paginator.num_pages == 1:
                response["is_single_page"] = True

            response["intent_with_children_name_pk_occurences"] = list(
                intent_with_children_name_pk_occurences)
            response["is_last_page"] = is_last_page
            response["language_script_type"] = "ltr"
            if translate_api_call_status:
                lang_obj = Language.objects.filter(
                    lang=dropdown_language).first()
                if lang_obj:
                    response["language_script_type"] = lang_obj.language_script_type
                response["status"] = 200
            else:
                response["status"] = 300

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FlowAnalyticsStatsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


FlowAnalyticsStats = FlowAnalyticsStatsAPI.as_view()


class ExportAnalyticsExcelIndividualAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            validation_obj = EasyChatInputValidation()
            data["bot_pk"] = validation_obj.remo_special_characters_from_string(data["bot_pk"])
            start_date = data["start_date"]
            end_date = data["end_date"]
            type_of_analytics = data["type"]
            # channel_value = data["channel_value"]
            data["selected_language"] = validation_obj.remo_special_characters_from_string(data["selected_language"])
            data["dropdown_language"] = validation_obj.remo_special_characters_from_string(data["dropdown_language"])
            # supported_languages = get_supported_languages_list(data["selected_language"], Language)

            # filter_type_particular = data["filter_type_particular"]
            # category_name = data["category_name"]
            datetime_start = start_date.split("-")
            start_date = datetime.datetime(int(datetime_start[0]), int(
                datetime_start[1]), int(datetime_start[2]))
            datetime_end = end_date.split("-")
            end_date = datetime.datetime(int(datetime_end[0]), int(
                datetime_end[1]), int(datetime_end[2]))
            email_id = data['email_id']
            if request.user.email == "" or request.user.email == None:
                request.user.email = email_id
            diff_in_days = (end_date.date() - start_date.date()).days
            is_large_date_range_data = False if diff_in_days <= 30 else True
            AnalyticsExportRequest.objects.create(
                bot_id=data["bot_pk"], user=request.user, email_id=email_id, request_datadump=json.dumps(data), analytics_type=type_of_analytics, start_date=start_date, end_date=end_date, is_large_date_range_data=is_large_date_range_data)
            if diff_in_days <= 30:
                # Commenting this function because now we create AnalyticsExportRequest and process it in easychat_analytics_export cronjob

                # start_thread_of_sending_data_via_mail(
                #     request.user, type_of_analytics, start_date, end_date, channel_value, data["bot_pk"], filter_type_particular, email_id,
                #     category_name, data["selected_language"], supported_languages, data["dropdown_language"], export_request_obj)

                response["status"] = 200
                response["email_id"] = email_id
            else:
                response["status"] = 201
                response["email_id"] = email_id

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportAnalyticsExcelIndividual! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class ExportDataAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            requested_data = DecryptVariable(request.data["json_string"])
            requested_data = json.loads(requested_data)

            bot_pk = requested_data["bot_pk"]
            # start_date = requested_data["startdate"]
            end_date = requested_data["enddate"]
            email_id = requested_data["email_id"]
            export_path = None
            export_path_exist = None

            if requested_data["selected_filter_value"] == "1":
                export_path = "/files/analytics-download-excel/bot-" + \
                              str(bot_pk) + "/AnalyticsExcelOneDay.zip"
                # export_path_exist = path.exists(export_path[1:])
                export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
            elif requested_data["selected_filter_value"] == "2":
                export_path = "/files/analytics-download-excel/bot-" + \
                              str(bot_pk) + "/AnalyticsExcelLastSevenDay.zip"
                # export_path_exist = path.exists(export_path[1:])
                export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
            elif requested_data["selected_filter_value"] == "3":
                export_path = "/files/analytics-download-excel/bot-" + \
                              str(bot_pk) + "/AnalyticsExcelThirtyDay.zip"
                # export_path_exist = path.exists(export_path[1:])
                export_path_exist = path.exists(str(settings.BASE_DIR + export_path))
            elif requested_data["selected_filter_value"] == "4":
                bot_obj = Bot.objects.get(pk=int(bot_pk))
                user_obj = User.objects.get(username=request.user.username)

                date_format = "%Y-%m-%d"
                end_date = datetime.datetime.strptime(
                    requested_data["enddate"], date_format).date()

                if end_date < bot_obj.created_datetime.date():
                    response["status"] = 400
                    response[
                        "message"] = "End date cannot be less than the bot creation date (%s)" % bot_obj.created_datetime.date(
                    ).strftime('%m/%d/%Y')
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                AnalyticsExportRequest.objects.create(
                    bot=bot_obj, user=user_obj, email_id=email_id, analytics_type="combined_global_export",
                    start_date=datetime.datetime.strptime(
                        requested_data["startdate"], date_format),
                    end_date=datetime.datetime.strptime(requested_data["enddate"], date_format))
                export_path = "request_saved"

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportDataAPI! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ExportDataAnalytics = ExportDataAnalyticsAPI.as_view()

MatchMessageWithIntent = MatchMessageWithIntentAPI.as_view()

ExportAnalyticsExcelIndividual = ExportAnalyticsExcelIndividualAPI.as_view()


# Conversion Analytics


class GetConversionFlowAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            username = request.user.username
            bot_pk = request.GET["bot_pk"]
            selected_language = "en"
            if "selected_language" in request.GET:
                selected_language = request.GET["selected_language"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)
            
            response, status, message = get_conversion_flow_analytics_data_external(uat_bot_obj, request.GET, selected_language)

            response["language_script_type"] = "ltr"
            if status == 200:
                lang_obj = Language.objects.filter(
                    lang=selected_language).first()
                if lang_obj:
                    response["language_script_type"] = lang_obj.language_script_type
                response["status"] = 200
            else:
                response['status'] = 300
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetConversionFlowAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetConversionFlowAnalytics = GetConversionFlowAnalyticsAPI.as_view()


class GetConversionDropOffAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            username = request.user.username
            bot_pk = request.GET["bot_pk"]
            selected_language = "en"
            if "selected_language" in request.GET:
                selected_language = request.GET['selected_language']

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            response, status, message = get_conversion_drop_off_data_external(uat_bot_obj, request.GET, selected_language)

            response["language_script_type"] = "ltr"
            if status == 200:
                lang_obj = Language.objects.filter(
                    lang=selected_language).first()
                if lang_obj:
                    response["language_script_type"] = lang_obj.language_script_type
                response["status"] = 200
            else:
                response["status"] = 300

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetConversionDropOffAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetConversionDropOffAnalytics = GetConversionDropOffAnalyticsAPI.as_view()


class GetConversionIntentAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            username = request.user.username
            bot_pk = request.GET["bot_pk"]
            page = request.GET["page"]
            selected_language = "en"
            translate_api_status = True
            if "selected_language" in request.GET:
                selected_language = request.GET["selected_language"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            response, status, message = get_conversion_intent_analytics_external(uat_bot_obj, request.GET, selected_language)
            bot_info_obj = get_bot_info_object(uat_bot_obj)

            if bot_info_obj and bot_info_obj.static_conversion_analytics:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            
            paginator = Paginator(response['intent_completion_data_list'], 20)
            no_pages = paginator.num_pages

            is_last_page = False
            if int(page) >= int(no_pages):
                is_last_page = True

            try:
                intent_completion_data = paginator.page(page)
            except PageNotAnInteger:
                intent_completion_data = paginator.page(1)
            except EmptyPage:
                intent_completion_data = paginator.page(paginator.num_pages)

            intent_completion_data, translate_api_status = conversion_intent_analytics_translator(
                list(intent_completion_data), selected_language, translate_api_status)

            response["intent_completion_data"] = intent_completion_data
            response["total_intent_count"] = response['total_intent_count']
            response["is_last_page"] = is_last_page

            response["language_script_type"] = "ltr"
            if translate_api_status:
                lang_obj = Language.objects.filter(
                    lang=selected_language).first()
                if lang_obj:
                    response["language_script_type"] = lang_obj.language_script_type
                response["status"] = 200
            else:
                response["status"] = 300

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetConversionIntentAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetConversionIntentAnalytics = GetConversionIntentAnalyticsAPI.as_view()


class GetWhatsappBlockAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            username = request.user.username
            bot_pk = request.GET["bot_pk"]
            page = request.GET["page"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False)

            response, status, message = get_whatsapp_block_analytics_external(bot_obj, request.GET)
            bot_info_obj = get_bot_info_object(bot_obj)

            if bot_info_obj and bot_info_obj.static_conversion_analytics:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            
            paginator = Paginator(response['block_session_data'], 20)
            no_pages = paginator.num_pages

            is_last_page = False
            if int(page) >= int(no_pages):
                is_last_page = True

            try:
                block_session_data = paginator.page(page)
            except PageNotAnInteger:
                block_session_data = paginator.page(1)
            except EmptyPage:
                block_session_data = paginator.page(paginator.num_pages)

            response["block_session_data"] = list(block_session_data)
            response["is_last_page"] = is_last_page

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetWhatsappBlockAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetWhatsappBlockAnalytics = GetWhatsappBlockAnalyticsAPI.as_view()


class GetWhatsappCatalogueAnalyticsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            username = request.user.username
            bot_pk = request.GET["bot_pk"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            bot_obj = Bot.objects.filter(
                pk=int(bot_pk), is_deleted=False).first()

            if not bot_obj or request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = "You are not authorised to perform this operation."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            response, status, message = get_whatsapp_catalogue_analytics_external(bot_obj, request.GET)

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetWhatsappCatalogueAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetWhatsappCatalogueAnalytics = GetWhatsappCatalogueAnalyticsAPI.as_view()


class ExportConversionAnalyticsExcelAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            validation_obj = EasyChatInputValidation()
            data["bot_pk"] = validation_obj.remo_special_characters_from_string(data["bot_pk"])
            start_date = data["start_date"]
            end_date = data["end_date"]
            type_of_analytics = data["type"]
            data["selected_language"] = validation_obj.remo_special_characters_from_string(data["selected_language"])
            datetime_start = start_date.split("-")
            start_date = datetime.datetime(int(datetime_start[0]), int(
                datetime_start[1]), int(datetime_start[2]))
            datetime_end = end_date.split("-")
            end_date = datetime.datetime(int(datetime_end[0]), int(
                datetime_end[1]), int(datetime_end[2]))
            email_id = data['email_id']
            if request.user.email == "" or request.user.email == None:
                request.user.email = email_id
            diff_in_days = (end_date.date() - start_date.date()).days
            is_large_date_range_data = False if diff_in_days <= 30 else True
            AnalyticsExportRequest.objects.create(
                bot_id=data["bot_pk"], user=request.user, email_id=email_id, request_datadump=json.dumps(data), analytics_type=type_of_analytics, start_date=start_date, end_date=end_date, is_large_date_range_data=is_large_date_range_data)

            if diff_in_days <= 30:
                response["status"] = 200
                response["email_id"] = email_id
            else:
                # Commenting this function because now we create AnalyticsExportRequest and process it in easychat_analytics_export cronjob
                # start_thread_of_conversion_analytics_data_via_mail(
                #     type_of_analytics, start_date, end_date, channel_list, bot_pk, email_id, selected_language, is_catalogue_purchased, block_type)

                response["status"] = 201
                response["email_id"] = email_id
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportConversionAnalyticsExcel! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        logger.error(response, extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ExportConversionAnalyticsExcel = ExportConversionAnalyticsExcelAPI.as_view()


class GetConversionLivechatAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            username = request.user.username
            bot_pk = request.GET["bot_pk"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            response, status, message = get_livechat_conversion_analytics_external(uat_bot_obj, request.GET)

            response["status"] = status
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetConversionLivechatAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetConversionLivechatAnalytics = GetConversionLivechatAnalyticsAPI.as_view()


class GetConversionBotHitsAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            username = request.user.username
            bot_pk = request.GET["bot_pk"]
            page = request.GET["page"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)
            
            response, status, message = get_bot_hit_list_data_external(uat_bot_obj, request.GET)
            bot_hit_data_list = response['bot_hit_data_list'] 

            paginator = Paginator(bot_hit_data_list, 20)
            no_pages = paginator.num_pages

            try:
                bot_hit_data_list = paginator.page(page)
            except PageNotAnInteger:
                bot_hit_data_list = paginator.page(1)
            except EmptyPage:
                bot_hit_data_list = paginator.page(paginator.num_pages)

            for bot_hit_data in bot_hit_data_list:
                average_time_spent = TimeSpentByUser.objects.filter(
                    bot=uat_bot_obj, web_page=bot_hit_data['web_page'],
                    web_page_source=bot_hit_data['web_page_source']).aggregate(Sum('total_time_spent'))[
                    'total_time_spent__sum']
                if average_time_spent != None:
                    bot_hit_data['average_time_spent'] = average_time_spent
                else:
                    bot_hit_data['average_time_spent'] = 0

            is_last_page = False
            if int(page) >= int(no_pages):
                is_last_page = True

            response["bot_hit_data_count"] = list(bot_hit_data_list)
            response["is_last_page"] = is_last_page
            response["status"] = status
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetConversionBotHitsAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetConversionBotHitsAnalytics = GetConversionBotHitsAnalyticsAPI.as_view()


class GetConversionWelcomeAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            username = request.user.username
            bot_pk = request.GET["bot_pk"]
            page = request.GET["page"]
            selected_language = "en"
            if "selected_language" in request.GET:
                selected_language = request.GET["selected_language"]

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            uat_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

            response, status, message = get_welcome_banner_clicks_data_external(uat_bot_obj, request.GET)

            bot_info_obj = get_bot_info_object(uat_bot_obj)

            welcome_banner_clicked_data_list = response['welcome_banner_clicked_data_list']
            paginator = Paginator(response['welcome_banner_clicked_data_list'], 20)
            no_pages = paginator.num_pages
            is_last_page = False
            if int(page) >= int(no_pages):
                is_last_page = True

            try:
                welcome_banner_clicked_data_count = paginator.page(page)
            except PageNotAnInteger:
                welcome_banner_clicked_data_count = paginator.page(1)
            except EmptyPage:
                welcome_banner_clicked_data_count = paginator.page(
                    paginator.num_pages)

            translate_api_status = True
            if bot_info_obj and bot_info_obj.static_conversion_analytics:
                for data in range(len(welcome_banner_clicked_data_list)):
                    if welcome_banner_clicked_data_list[data]["intent__name"]:
                        welcome_banner_clicked_data_list[data]["multilingual_name"], translate_api_status = get_translated_text_with_api_status(
                            welcome_banner_clicked_data_list[data]["intent__name"], selected_language, EasyChatTranslationCache, translate_api_status)
                response["welcome_banner_clicked_data_count"] = welcome_banner_clicked_data_list
            else:
                response["welcome_banner_clicked_data_count"], translate_api_status = welcome_analytics_translator(
                    list(welcome_banner_clicked_data_count), selected_language, translate_api_status)
            response["is_last_page"] = is_last_page

            response["language_script_type"] = "ltr"
            if translate_api_status:
                lang_obj = Language.objects.filter(
                    lang=selected_language).first()
                if lang_obj:
                    response["language_script_type"] = lang_obj.language_script_type
                response["status"] = 200
            else:
                response["status"] = 300

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetConversionWelcomeAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetConversionWelcomeAnalytics = GetConversionWelcomeAnalyticsAPI.as_view()


class GetConversionNodeAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            intent_pk = data["intent_pk"]
            start_date = data["start_date"]
            end_date = data["end_date"]
            channel_list = data["channel_list"]
            selected_language = "en"
            if "selected_language" in data:
                selected_language = data["selected_language"]

            # check if static analytics is enabled
            bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

            bot_info_obj = get_bot_info_object(bot_obj)
            translated_api_status = True
            if bot_info_obj and bot_info_obj.static_conversion_analytics:
                json_resp, translated_api_status = update_multilingual_name(
                    STATIC_EASYCHAT_CONVERSION_NODE_ANALYTICS_DUMMY_DATA, selected_language, translated_api_status)
                max_level = STATIC_EASYCHAT_CONVERSION_NODE_ANALYTICS_MAX_LEVEL
                response["flow_tree_data"] = json.dumps(json_resp)
                response["max_level"] = max_level
                if translated_api_status:
                    response["status"] = 200
                else:
                    response["status"] = 300

                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            datetime_start = start_date.split("-")
            start_date = datetime.datetime(int(datetime_start[0]), int(
                datetime_start[1]), int(datetime_start[2]))
            datetime_end = end_date.split("-")
            end_date = datetime.datetime(int(datetime_end[0]), int(
                datetime_end[1]), int(datetime_end[2]))

            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))

            intent_obj = Intent.objects.get(pk=int(intent_pk))
            root_tree_obj = intent_obj.tree

            if len(channel_list) == 0:
                channel_objs = Channel.objects.filter(is_easychat_channel=True)
            else:
                channel_objs = Channel.objects.filter(name__in=channel_list)

            flow_analytics_objects = DailyFlowAnalytics.objects.filter(
                intent_indentifed=intent_obj, created_time__date__gte=start_date, created_time__date__lte=end_date,
                channel__in=channel_objs)

            flow_analytics_objects_that_day = FlowAnalytics.objects.none()
            if end_date.date() == datetime.datetime.today().date():
                flow_analytics_objects_that_day = FlowAnalytics.objects.filter(intent_indentifed=intent_obj, created_time__date=end_date, channel__in=channel_objs)
            
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
                logger.error("GetConversionNodeAnalytics Intent count problem %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})
                pass
            try:
                count_intent_was_called += flow_analytics_objects_that_day.filter(
                    current_tree=intent_obj.tree).count()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("GetConversionNodeAnalytics Intent count problem that day %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})
                count_intent_was_called = 0
                pass

            json_resp, max_level, translate_api_status = get_child_tree_objs_flow_analytics(root_tree_obj.pk,
                                                                                            root_tree_obj, [
                                                                                            ], flow_analytics_objects,
                                                                                            flow_analytics_objects_that_day,
                                                                                            flow_termination_data_objs,
                                                                                            intent_obj,
                                                                                            count_intent_was_called, [],
                                                                                            [], True, 1, 0, 0,
                                                                                            selected_language, True)

            response["flow_tree_data"] = json.dumps(json_resp)
            response["max_level"] = max_level

            if translate_api_status:
                response["status"] = 200
            else:
                response["status"] = 300

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetConversionNodeAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetConversionNodeAnalytics = GetConversionNodeAnalyticsAPI.as_view()


class GetUserNudgeAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"

        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(str(bot_id)).strip()

            start_date = data["start_date"]
            start_date = validation_obj.remo_html_from_string(start_date)

            end_date = data["end_date"]
            end_date = validation_obj.remo_html_from_string(end_date)

            page = data["page"]
            page = int(validation_obj.remo_html_from_string(page).strip())

            category_name = data["category_name"]
            category_name = validation_obj.remo_html_from_string(
                category_name).strip()

            channel_name = data["channel_name"]
            channel_name = validation_obj.remo_html_from_string(
                channel_name).strip()

            selected_language = data["selected_language"]

            selected_language = validation_obj.remo_html_from_string(
                selected_language)

            search_term = data.get("search", "")

            search_term = validation_obj.remo_html_from_string(
                search_term)

            if channel_name not in ["Web", "All"]:
                response["status"] = 200
                response["message"] = "Success"
                response["user_nudge_analytics_data"] = []
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            supported_languages_list = []
            if selected_language.lower() != "all":
                supported_languages_list = selected_language.split(",")
                supported_languages_list = [
                    lang.strip() for lang in supported_languages_list]

            supported_languages = Language.objects.filter(
                lang__in=supported_languages_list)

            start_date = datetime.date(int(start_date.split(
                "-")[0]), int(start_date.split("-")[1]), int(start_date.split("-")[2]))
            end_date = datetime.date(int(end_date.split(
                "-")[0]), int(end_date.split("-")[1]), int(end_date.split("-")[2]))

            bot_obj = Bot.objects.get(pk=bot_id)
            channel_objs = Channel.objects.filter(name="Web")

            bubble_click_count_objs = AutoPopUpClickInfo.objects.filter(
                bot=bot_obj, date__gte=start_date, date__lte=end_date)

            if selected_language.lower() != "all":
                bubble_click_count_objs = bubble_click_count_objs.filter(
                    selected_language__in=supported_languages)
            
            if search_term:
                bubble_click_count_objs = bubble_click_count_objs.filter(name__icontains=search_term)

            distinct_bubble_click_objs = bubble_click_count_objs.exclude(
                name="Greeting bubble").values("name").distinct()

            auto_popup_type = bot_obj.auto_popup_type
            is_auto_popup_desktop = bot_obj.is_auto_pop_allowed_desktop
            is_auto_popup_mobile = bot_obj.is_auto_pop_allowed_mobile
            auto_popup_enabled = (is_auto_popup_desktop or is_auto_popup_mobile)
            auto_popup_initial_messages = []
            temp_auto_popup_initial_messages = []

            bot_channel_obj = BotChannel.objects.filter(
                bot=bot_obj, channel=channel_objs[0])[0]
            languages_supported = bot_channel_obj.languages_supported.all().exclude(
                lang="en").values("lang")

            for intent_obj_pk in json.loads(bot_obj.auto_popup_initial_messages):
                intent_obj = Intent.objects.get(pk=int(intent_obj_pk))
                temp_auto_popup_initial_messages.append(intent_obj.name)

            if str(auto_popup_type) == "3":
                auto_popup_initial_messages = temp_auto_popup_initial_messages
                if search_term:
                    auto_popup_initial_messages = list(filter(lambda message: search_term.lower() in message.lower(), auto_popup_initial_messages))
                for language_supported in languages_supported:
                    auto_popup_initial_messages += get_translated_text("$$$".join(auto_popup_initial_messages), language_supported["lang"], EasyChatTranslationCache).split("$$$")

            other_lang_to_english_dict = {}
            initial_messages = temp_auto_popup_initial_messages
            for bubble_click_obj in distinct_bubble_click_objs:
                if bubble_click_obj["name"].strip().replace(" ", "").isalpha():
                    other_lang_to_english_dict[bubble_click_obj["name"].strip(
                    )] = bubble_click_obj["name"].strip()
                    if bubble_click_obj["name"].strip() not in initial_messages:
                        initial_messages.append(
                            bubble_click_obj["name"].strip())

            if len(initial_messages) != 0:
                for language_supported in languages_supported:
                    translated_initial_messages = get_translated_text("$$$".join(
                        initial_messages), language_supported["lang"], EasyChatTranslationCache).split("$$$")

                    for idx, translated_initial_message in enumerate(translated_initial_messages):
                        other_lang_to_english_dict[translated_initial_message.strip(
                        )] = initial_messages[idx]

            if search_term.lower() in "Greeting bubble".lower():
                user_nudge_analytics_data = [{
                    "name": "Greeting bubble",
                    "count": bubble_click_count_objs.filter(name="Greeting bubble").count(),
                    "is_active": str(auto_popup_type) in ["2", "3"]
                }]
            else:
                user_nudge_analytics_data = []

            auto_popup_intent_list = []
            bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()
            if(bot_info_obj.custom_intents_for == AUTO_POPUP):
                custom_intent_objs = CustomIntentBubblesForWebpages.objects.filter(
                    bot=bot_obj, custom_intents_for=AUTO_POPUP)
                for custom_intents in custom_intent_objs:
                    if search_term:
                        custom_intent_bubbles = custom_intents.custom_intent_bubble.filter(name__icontains=search_term)
                    else:
                        custom_intent_bubbles = custom_intents.custom_intent_bubble.all()
                    for intents in custom_intent_bubbles:
                        auto_popup_intent_list.append(intents.name)
            
            if auto_popup_intent_list:
                translated_intent = ''
                for intent in auto_popup_intent_list:
                    translated_intent += '"' + intent + '", '
                    
                translated_intent = "[" + translated_intent[:-2] + "]"
                for language_supported in languages_supported:
                    auto_popup_intent_list += get_translated_text("$$$".join(json.loads(
                        translated_intent)), language_supported["lang"], EasyChatTranslationCache).split("$$$")

            distinct_bubble_click_objs_list = []
            for distinct_bubble_click_obj in distinct_bubble_click_objs:
                distinct_bubble_click_objs_list.append(distinct_bubble_click_obj["name"])
                try:
                    if category_name != "All":
                        Intent.objects.get(bots__in=[bot_obj], name=other_lang_to_english_dict[distinct_bubble_click_obj["name"].strip(
                        )], category__name=category_name.strip(), channels__in=channel_objs)
                    if(bot_info_obj.enable_custom_intent_bubbles == False or distinct_bubble_click_obj["name"] not in auto_popup_intent_list):
                        user_nudge_analytics_data.append({
                            "name": distinct_bubble_click_obj["name"],
                            "count": bubble_click_count_objs.filter(name=distinct_bubble_click_obj["name"]).count(),
                            "is_active": distinct_bubble_click_obj["name"] in auto_popup_initial_messages and auto_popup_type == "3" and auto_popup_enabled
                        })
                except:
                    continue

            for default_intents in auto_popup_initial_messages:
                try:
                    if default_intents != "" and default_intents not in distinct_bubble_click_objs_list:
                        user_nudge_analytics_data.append({
                            "name": default_intents,
                            "count": bubble_click_count_objs.filter(name=default_intents).count(),
                            "is_active": auto_popup_type == "3" and auto_popup_enabled
                        })
                except:
                    continue

            for intents in auto_popup_intent_list:
                try:
                    if intents not in auto_popup_initial_messages:
                        user_nudge_analytics_data.append({
                            "name": intents,
                            "count": bubble_click_count_objs.filter(name=intents).count(),
                            "is_active": bot_info_obj.enable_custom_intent_bubbles and auto_popup_type == "3" and auto_popup_enabled
                        })
                except:
                    continue

            response["is_previous_page"] = False
            response["previous_page_no"] = 0
            if page > 1:
                response["is_previous_page"] = True
                response["previous_page_no"] = page - 1

            response["is_next_page"] = False
            response["next_page_no"] = 0
            if user_nudge_analytics_data[((page + 1) * 5) - 5:]:
                response["is_next_page"] = True
                response["next_page_no"] = page + 1

            user_nudge_analytics_data = user_nudge_analytics_data[(
                page * 5) - 5: page * 5]

            response["user_nudge_analytics_data"] = user_nudge_analytics_data
            response["status"] = 200
            response["message"] = "Success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetUserNudgeAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetUserNudgeAnalytics = GetUserNudgeAnalyticsAPI.as_view()


class ExportUserNudgeAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_obj = request.user

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(str(bot_id)).strip()

            start_date = data["start_date"]
            start_date = validation_obj.remo_html_from_string(start_date)

            end_date = data["end_date"]
            end_date = validation_obj.remo_html_from_string(end_date)

            category_name = data["category_name"]
            category_name = validation_obj.remo_html_from_string(
                category_name).strip()

            channel_name = data["channel_name"]
            channel_name = validation_obj.remo_html_from_string(
                channel_name).strip()

            selected_language = data["selected_language"]
            selected_language = validation_obj.remo_html_from_string(
                selected_language)

            supported_languages_list = []
            if selected_language.lower() != "all":
                supported_languages_list = selected_language.split(",")
                supported_languages_list = [
                    lang.strip() for lang in supported_languages_list]

            supported_languages = Language.objects.filter(
                lang__in=supported_languages_list)

            start_date = datetime.date(int(start_date.split(
                "-")[0]), int(start_date.split("-")[1]), int(start_date.split("-")[2]))
            end_date = datetime.date(int(end_date.split(
                "-")[0]), int(end_date.split("-")[1]), int(end_date.split("-")[2]))

            email_id = data["email_id"]
            if request.user.email == "" or request.user.email == None:
                request.user.email = email_id
            diff_in_days = (end_date - start_date).days
            if diff_in_days <= 30:
                filepath = create_user_nudge_analytics_excel(
                    user_obj, bot_id, channel_name, category_name, start_date, end_date, selected_language,
                    supported_languages, email_id, False)
                response["export_path"] = filepath
                if filepath != "":
                    response["status"] = 200
            else:
                thread = threading.Thread(target=create_user_nudge_analytics_excel, args=(user_obj, bot_id, channel_name, category_name, start_date, end_date, selected_language, supported_languages, email_id, True), daemon=True)
                thread.start()

                response["status"] = 200
                response["email_id"] = email_id

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportUserNudgeAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ExportUserNudgeAnalytics = ExportUserNudgeAnalyticsAPI.as_view()


class MarkFlaggedQueriesAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            bot_id = data["bot_id"]
            message_history_pk_list = data["message_history_pk_list"]
            flagged_queries_type = data["flagged_queries_type"]

            flagged_queries = 0
            not_flagged_queries = 0
            not_percentage_match_queries = 0

            bot_obj = Bot.objects.filter(pk=bot_id, is_deleted=False).first()
            config_obj = Config.objects.all().first()

            percentage_threshold = config_obj.percentage_threshold_for_message_history

            if bot_obj:
                for message_history_pk in message_history_pk_list:
                    mis_obj = MISDashboard.objects.filter(
                        pk=message_history_pk, bot=bot_obj).first()

                    if mis_obj:

                        if mis_obj.match_percentage == -1:
                            not_percentage_match_queries += 1
                        elif mis_obj.match_percentage > percentage_threshold:
                            not_flagged_queries += 1
                        else:
                            mis_obj.flagged_queries_positive_type = flagged_queries_type
                            mis_obj.save()
                            flagged_queries += 1

                if flagged_queries == 0:
                    if len(message_history_pk_list) > 1:
                        toast_message = "Selected queries can't be marked False Positive / Not False Positive, as either their percentage match is higher than set percentage threshold or they don't have a percentage match."
                    else:
                        toast_message = "Selected query can't be marked False Positive / Not False Positive, as either the percentage match is higher than set percentage threshold or it doesn't have a percentage match."

                else:
                    response["status"] = 300
                    if (not_flagged_queries != 0 or not_percentage_match_queries != 0):
                        toast_message = "Some of the selected queries cannot be marked False Positive / Not False Positive as either their percentage match is higher than set percentage threshold or they don't have a percentage match."
                    else:
                        response["status"] = 200
                        toast_message = "Success"

                response["message"] = toast_message

            else:
                response["message"] = "Bot id doesn't exists."

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error MarkFlaggedQueriesAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


MarkFlaggedQueries = MarkFlaggedQueriesAPI.as_view()


class GetHourWiseAnalyticsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            start_time_analytics = time.time()
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]
            channel_name = data["channel"]
            selected_language = data["selected_language"]
            category_name = data["category_name"]
            validation_obj = EasyChatInputValidation()

            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))
            channel_name = validation_obj.remo_html_from_string(channel_name)
            selected_language = validation_obj.remo_html_from_string(
                selected_language)
            bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)
            if not bot_obj or request.user not in bot_obj.users.all():
                response["status"] = 401
                response["status_message"] = "You are not authorised to perform this operation."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)  

            interval_type = "1"  # default 1 hour interval
            time_format = "1"  # default 12 hour format
            try:
                interval_type = data["interval_type"]
                time_format = data["time_format"]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("interval_type is not defined: %s at line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                pass

            datetime_start = datetime.datetime.today().date()
            datetime_end = datetime_start
            try:
                date_format = "%Y-%m-%d"
                start_date = data["start_date"]
                end_date = data["end_date"]
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("startdate and enddate is not in valid format %s at line no %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                pass

            datetime_start, datetime_end, error_message = get_start_and_end_time(
                data)
            if error_message:
                response["status"] = 401
                response["status_message"] = error_message
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
           
            supported_languages_list = []
            if selected_language.lower() != "all":
                supported_languages_list = selected_language.split(",")
                supported_languages_list = [
                    lang.strip() for lang in supported_languages_list]

            supported_languages = Language.objects.filter(
                lang__in=supported_languages_list)

            bot_objs = [bot_obj]
            response, status, message = get_combined_hour_wise_analytics(
                response, bot_objs, datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, interval_type, time_format)

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[NLP]: Error GetHourWiseAnalyticsAPI %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        end_time = time.time()
        time_taken = str(end_time - start_time_analytics)
        logger.info("Get Hour wise Analytics Time Taken %s", time_taken, extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetHourWiseAnalytics = GetHourWiseAnalyticsAPI.as_view()
