from django.db.models import Q
import logging
import sys
import math

from datetime import datetime, timedelta
from django.db.models import Sum
from EasyChatApp.static_dummy_data import *
from django.db.models import Count
from django.db.models.functions import ExtractHour
from django.utils.timezone import get_current_timezone


from EasyChatApp.utils_analytics import *
from EasyChatApp.models import *
from EasyChatApp.utils_execute_query import get_bot_info_object
from LiveChatApp.models import LiveChatCustomer

from operator import itemgetter
from ast import literal_eval
from itertools import groupby
from collections import OrderedDict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from EasyChatApp.utils_bot import get_translated_text

logger = logging.getLogger(__name__)


def get_basic_analytics(response, uat_bot_obj, channel_name, category_name, selected_language, supported_languages):
    try:
        status = 500
        message = "Internal Server Error"
        prod_bot_obj = None
        channel_obj = None
        if Channel.objects.filter(name=channel_name).exists():
            channel_obj = Channel.objects.filter(name=channel_name).first()
        # try:
        #     bot_slug = uat_bot_obj.slug
        #     prod_bot_obj = Bot.objects.filter(
        #         slug=bot_slug, is_deleted=False, is_active=True).order_by("-pk")[0]
        # except Exception:
        #     pass

        bot_objs = []
        if prod_bot_obj == None:
            bot_objs = [uat_bot_obj]
        else:
            bot_objs = [prod_bot_obj]
        total_feedback = 0
        if channel_obj:
            total_feedback = Feedback.objects.filter(
                bot__in=bot_objs, channel=channel_obj).count()
        else:
            total_feedback = Feedback.objects.filter(
                bot__in=bot_objs).count()

        promoter_feedback = promoter_feedback_count(
            bot_objs, channel_obj, Feedback)
        demoter_feedback = demoter_feedback_count(
            bot_objs, channel_obj, Feedback)

        date_today = datetime.date.today()
        # year = date_today.year
        # month = date_today.month
        # day = date_today.day

        mis_objs = return_mis_objects_based_on_category_channel_language(
            date_today, date_today, bot_objs, channel_name, "All", selected_language, supported_languages, MISDashboard, UserSessionHealth)

        number_of_users_today = mis_objs.values(
            "user_id").distinct().count()

        if category_name.lower().strip() != "all" and category_name.strip() != "":
            mis_objs = mis_objs.filter(category__name=category_name)
            
        number_of_answered_queries = mis_objs.filter(
            ~Q(intent_name=None)).count()
        
        number_of_messages_today = mis_objs.count()

        response["promoter_feedback"] = promoter_feedback
        response["demoter_feedback"] = demoter_feedback
        response["total_feedback"] = total_feedback
        response["number_of_answered_queries"] = number_of_answered_queries
        response["number_of_messages_today"] = number_of_messages_today
        response["number_of_users_today"] = number_of_users_today
        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_basic_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return response, status, message


def get_csat_analytics(response, bot_obj, datetime_start, datetime_end, channels, csat_type):
    try:
        status = 500
        message = "Internal Server Error"

        feedback_objs = Feedback.objects.filter(
            bot=bot_obj, date__date__gte=datetime_start, date__date__lte=datetime_end, channel__in=channels)

        if csat_type == "Demoters":
            feedback_objs = feedback_objs.filter(rating__lte=2)
        elif csat_type == "Promoters":
            feedback_objs_4_scale = feedback_objs.filter(
                rating__gte=3, scale_rating_5=False)
            feedback_objs_5_scale = feedback_objs.filter(
                rating__gte=4, scale_rating_5=True)
            feedback_objs = feedback_objs_4_scale | feedback_objs_5_scale
        elif csat_type == "Passives":
            feedback_objs = feedback_objs.filter(rating=3, scale_rating_5=True)

        feedback_objs = feedback_objs.order_by("-date")
        csat_data = []
        for feedback_obj in feedback_objs:
            csat_data.append({
                "timestamp": str(feedback_obj.date),
                "user_id": str(feedback_obj.user_id),
                "comments": feedback_obj.comments,
                "channel": feedback_obj.channel.name,
                "csat_score": feedback_obj.get_csat_score_str()
            })
        response["csat_analytics_data"] = csat_data
        status = 200
        message = "Success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_csat_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
    return response, status, message


def get_combined_hour_wise_analytics(response, bot_objs, datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, interval_type="1", time_format="1"):
    response["status"] = 500
    response["message"] = "Internal Server Error"

    try:
        time_gap = 1  # default value of time interval in hour
        mis_objects = return_mis_objects_based_on_category_channel_language(
            datetime_start, datetime_end, bot_objs, channel_name, "All", selected_language, supported_languages, MISDashboard, UserSessionHealth)

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

        response["hour_wise_analytics_list"] = hour_wise_analytics_list
        response["interval_type"] = interval_type
        response["time_format"] = time_format
        response["status"] = 200
        response["message"] = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_combined_hour_wise_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return response, response["status"], response["message"]


def get_combined_message_analytics(response, bot_objs, datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, filter_type, labels):
    try:
        status = 500
        message = "Internal Server Error"
        category_obj = None
        if category_name != "All":
            category_obj = Category.objects.filter(
                bot=bot_objs[0], name=category_name).first()
        bot_info_obj = BotInfo.objects.filter(bot=bot_objs[0]).first()
        is_flaged_query_required = False
        if bot_info_obj:
            is_flaged_query_required = bot_info_obj.enable_flagged_queries_status

        date_today = datetime.date.today()

        mis_filtered_objs = None
        if is_flaged_query_required:
            mis_object = return_mis_objects_excluding_blocked_sessions(MISDashboard.objects, UserSessionHealth)
            mis_filtered_objs = mis_object.filter(bot__in=bot_objs)
            mis_filtered_objs = get_db_objects_based_on_filter(
                mis_filtered_objs, channel_name, category_name, selected_language, supported_languages)

        previous_mis_objects = return_mis_daily_objects_based_on_filter(
            bot_objs, channel_name, category_name, category_obj, selected_language, supported_languages, MessageAnalyticsDaily)

        mis_objects = return_mis_objects_based_on_category_channel_language(
            date_today, date_today, bot_objs, channel_name, category_name, selected_language, supported_languages, MISDashboard, UserSessionHealth)

        data_dict, total_days = get_combined_message_analytics_list(
            datetime_start, datetime_end, mis_objects, mis_filtered_objs, previous_mis_objects, filter_type, labels, is_flaged_query_required)

        response["start_date"] = datetime_start.strftime("%d-%b-%y")
        response["end_date"] = datetime_end.strftime("%d-%b-%y")
        response["total_no_of_days"] = total_days
        response["message_analytics_data"] = data_dict["message_analytics_list"]

        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_combined_message_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return response, status, message


def get_combined_message_analytics_list(datetime_start, datetime_end, mis_objects, mis_filtered_objs, previous_mis_objects, filter_type, labels, is_flaged_query_required):

    data_dict = {
        "message_analytics_list": [],
        "percentage_change": "",
        "percentage_change_type": ""
    }
    message_analytics_list = []
    total_days = 0
    try:
        if filter_type == "1":
            data_dict, no_of_days, today_flag = get_daily_message_analytics_list(
                datetime_start, datetime_end, previous_mis_objects, mis_objects, mis_filtered_objs, labels, is_flaged_query_required)

        elif filter_type == "2":
            data_dict = get_weekly_message_analytics_list(
                datetime_start, datetime_end, previous_mis_objects, mis_objects, mis_filtered_objs, labels, is_flaged_query_required)
        else:
            data_dict = get_monthly_message_analytics_list(
                datetime_start, datetime_end, previous_mis_objects, mis_objects, mis_filtered_objs, labels, is_flaged_query_required)
        message_analytics_list = data_dict["message_analytics_list"]
        if filter_type == "1":
            if today_flag:
                total_days = no_of_days + 1
            else:
                total_days = no_of_days
        elif filter_type == "2":
            total_days = len(message_analytics_list) * 7
        elif filter_type == "3":
            total_days = len(message_analytics_list) * 30

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_combined_message_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return data_dict, total_days


def get_daily_message_analytics_list(datetime_start, datetime_end, previous_mis_objects, mis_objects, mis_filtered_objs, labels, is_flaged_query_required):
    no_of_days = 0
    today_flag = False
    data_dict = {
        "message_analytics_list": [],
        "percentage_change": "None",
        "percentage_change_type": ""
    }
    message_analytics_list = []
    try:
        total_hours_passed = datetime.datetime.today().hour
        avg_total_messages = mis_objects.filter(
            creation_date=datetime.datetime.today()).count()

        if total_hours_passed != 0:
            avg_msgs = math.ceil(
                (avg_total_messages / float(total_hours_passed)) * 24.0)
        else:
            avg_msgs = math.ceil((avg_total_messages / float(1)))

        today_date = datetime.date.today().strftime("%d-%b-%y")
        if datetime_end.strftime("%d-%b-%y") == today_date:
            no_of_days = (datetime_end - datetime_start).days
            today_flag = True
        else:
            no_of_days = (datetime_end - datetime_start).days + 1
            today_flag = False
        percentage_change = ""
        percentage_change_type = ""
        for day in range(no_of_days):
            temp_datetime = datetime_start + datetime.timedelta(day)
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

            total_messages = return_zero_if_number_is_none(
                total_messages)
            total_answered_messages = return_zero_if_number_is_none(
                total_answered_messages)
            total_unanswered_messages = return_zero_if_number_is_none(
                total_unanswered_messages)
            total_intuitive_messages = return_zero_if_number_is_none(
                total_intuitive_messages)

            current_day_data_dict = {
                labels[0]: str(temp_datetime.strftime("%d-%b-%y")),
                "total_messages": total_messages,
                "total_answered_messages": total_answered_messages,
                "total_intuitive_messages": total_intuitive_messages,
                "total_unanswered_messages": total_unanswered_messages,
                "predicted_messages_no": total_messages,
            }
            if is_flaged_query_required:
                false_positive_messages = mis_filtered_objs.filter(
                    creation_date=temp_datetime, flagged_queries_positive_type="1").count()
                current_day_data_dict["false_positive_messages"] = false_positive_messages

            message_analytics_list.append(current_day_data_dict)

        if datetime_end.strftime("%d-%b-%y") == today_date:
            date_filtered_mis_objects = mis_objects
            total_messages = date_filtered_mis_objects.count()

            total_unanswered_messages = date_filtered_mis_objects.filter(
                intent_name=None, is_unidentified_query=True, is_intiuitive_query=False).exclude(message_received="").count()
            total_intuitive_messages = date_filtered_mis_objects.filter(intent_name=None, is_intiuitive_query=True).count()
            total_answered_messages = total_messages - (total_unanswered_messages + total_intuitive_messages)

            current_day_data_dict = {
                labels[0]: str(today_date),
                "total_messages": total_messages,
                "total_answered_messages": total_answered_messages,
                "total_unanswered_messages": total_unanswered_messages,
                "total_intuitive_messages": total_intuitive_messages,
                "predicted_messages_no": total_messages,
            }

            if is_flaged_query_required:
                false_positive_messages = date_filtered_mis_objects.filter(
                    flagged_queries_positive_type="1").count()
                current_day_data_dict["false_positive_messages"] = false_positive_messages

            message_analytics_list.append(current_day_data_dict)

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

        data_dict["message_analytics_list"] = message_analytics_list
        data_dict["percentage_change"] = percentage_change
        data_dict["percentage_change_type"] = percentage_change_type

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_daily_message_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return data_dict, no_of_days, today_flag


def get_weekly_message_analytics_list(datetime_start, datetime_end, previous_mis_objects, mis_objects, mis_filtered_objs, labels, is_flaged_query_required):
    data_dict = {
        "message_analytics_list": [],
        "percentage_change": "",
        "percentage_change_type": ""
    }
    message_analytics_list = []
    try:
        total_hours_passed = datetime.datetime.today(
        ).hour + datetime.datetime.today().weekday() * 24.0

        start_week_date = datetime.datetime.today() - datetime.timedelta(7)

        previous_mis_objects_count = previous_mis_objects.filter(
            date_message_analytics__gte=start_week_date).aggregate(Sum('total_messages_count'))['total_messages_count__sum']

        if previous_mis_objects_count == None:
            previous_mis_objects_count = 0

        avg_msgs = math.ceil(
            ((previous_mis_objects_count + mis_objects.count()) / total_hours_passed) * 7.0 * 24.0) + 1
        today_date = datetime.date.today().strftime("%d-%b-%y")
        no_days = (datetime_end - datetime_start).days
        no_weeks = int(no_days / 7.0) + 1
        percentage_change = ""
        percentage_change_type = ""

        for week in range(no_weeks):
            temp_end_datetime = datetime_end - \
                datetime.timedelta(week * 7)
            temp_start_datetime = datetime_end - \
                datetime.timedelta((week + 1) * 7)

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

            temp_start_datetime_str = (temp_start_datetime + datetime.timedelta(1)).strftime(
                "%d/%m")
            temp_end_datetime_str = (
                temp_end_datetime).strftime("%d/%m")

            current_day_data_dict = {
                labels[0]: str(temp_start_datetime_str + "-" + temp_end_datetime_str),
                "total_messages": total_messages,
                "total_answered_messages": total_answered_messages,
                "total_unanswered_messages": total_unanswered_messages,
                "total_intuitive_messages": total_intuitive_messages,
                "predicted_messages_no": total_messages,
            }
            if is_flaged_query_required:
                false_positive_messages = mis_filtered_objs.filter(
                    flagged_queries_positive_type="1", creation_date__gt=temp_start_datetime, creation_date__lte=temp_end_datetime).count()

                current_day_data_dict["false_positive_messages"] = false_positive_messages

            message_analytics_list.append(current_day_data_dict)

        message_analytics_list = message_analytics_list[::-1]
        if datetime_end.strftime("%d-%b-%y") == today_date:
            date_filtered_mis_objects = mis_objects
            total_messages = date_filtered_mis_objects.count()

            total_unanswered_messages = date_filtered_mis_objects.filter(
                intent_name=None, is_unidentified_query=True, is_intiuitive_query=False).count()
            total_intuitive_messages = date_filtered_mis_objects.filter(intent_name=None, is_intiuitive_query=True).count()
            total_answered_messages = total_messages - (total_unanswered_messages + total_intuitive_messages)

            message_analytics_list[-1]["total_messages"] = message_analytics_list[-1][
                "total_messages"] + total_messages
            message_analytics_list[-1]["total_unanswered_messages"] = message_analytics_list[-1][
                "total_unanswered_messages"] + total_unanswered_messages
            message_analytics_list[-1]["total_intuitive_messages"] = message_analytics_list[-1][
                "total_intuitive_messages"] + total_intuitive_messages
            message_analytics_list[-1]["total_answered_messages"] = message_analytics_list[-1][
                "total_answered_messages"] + total_answered_messages
            message_analytics_list[-1]["predicted_messages_no"] = avg_msgs
            if is_flaged_query_required:
                message_analytics_list[-1]["false_positive_messages"] += date_filtered_mis_objects.filter(
                    flagged_queries_positive_type="1").count()
            this_7days_start = datetime_end - datetime.timedelta(7)
            previous_mis_objects_count = previous_mis_objects.filter(
                date_message_analytics__lte=datetime_end, date_message_analytics__gt=this_7days_start).aggregate(Sum('total_messages_count'))['total_messages_count__sum']

            if previous_mis_objects_count == None:
                previous_mis_objects_count = 0

            today_mis_objects = previous_mis_objects_count + mis_objects.count()
            last_7days_start = datetime_end - datetime.timedelta(14)
            last_day_mis_objects = previous_mis_objects.filter(
                date_message_analytics__lte=this_7days_start, date_message_analytics__gt=last_7days_start).aggregate(Sum('total_messages_count'))['total_messages_count__sum']

            if last_day_mis_objects == None:
                last_day_mis_objects = 0

            if last_day_mis_objects > 0:
                percentage_change = round(100 * float(
                    today_mis_objects - last_day_mis_objects) / float(last_day_mis_objects), 2)
            else:
                percentage_change = "None"
            percentage_change_type = 'Since last 7 days'

        data_dict["message_analytics_list"] = message_analytics_list
        data_dict["percentage_change"] = percentage_change
        data_dict["percentage_change_type"] = percentage_change_type

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_weekly_message_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return data_dict


def get_monthly_message_analytics_list(datetime_start, datetime_end, previous_mis_objects, mis_objects, mis_filtered_objs, labels, is_flaged_query_required):
    data_dict = {
        "message_analytics_list": [],
        "percentage_change": "",
        "percentage_change_type": ""
    }
    message_analytics_list = []
    try:
        month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
            r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days + 1)).keys())

        total_hours_passed = datetime.datetime.today(
        ).hour + (datetime.datetime.today().day - 1) * 24.0

        start_month_date = datetime.datetime.today(
        ) - datetime.timedelta(datetime.datetime.today().day - 1)
        avg_msgs = math.ceil(((previous_mis_objects.filter(
            date_message_analytics__gte=start_month_date).count() + mis_objects.count()) / total_hours_passed) * 24.0 * 30.0) + 1

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

            false_positive_messages = mis_filtered_objs.filter(
                flagged_queries_positive_type="1", creation_date__month=temp_month, creation_date__year=temp_year).count()

            total_messages = return_zero_if_number_is_none(
                total_messages)
            total_answered_messages = return_zero_if_number_is_none(
                total_answered_messages)
            total_unanswered_messages = return_zero_if_number_is_none(
                total_unanswered_messages)
            total_intuitive_messages = return_zero_if_number_is_none(
                total_intuitive_messages)

            message_analytics_list.append({
                labels[0]: month,
                "total_messages": total_messages,
                "total_answered_messages": total_answered_messages,
                "total_unanswered_messages": total_unanswered_messages,
                "total_intuitive_messages": total_intuitive_messages,
                "predicted_messages_no": total_messages,
                "false_positive_messages": false_positive_messages
            })

        if datetime_end.month == datetime.datetime.today().month:
            message_analytics_list[-1]["predicted_messages_no"] = avg_msgs

            date_filtered_mis_objects = mis_objects
            total_messages = date_filtered_mis_objects.count()
            total_unanswered_messages = date_filtered_mis_objects.filter(
                intent_name=None, is_unidentified_query=True, is_intiuitive_query=False).count()
            total_intuitive_messages = date_filtered_mis_objects.filter(intent_name=None, is_intiuitive_query=True).count()
            total_answered_messages = total_messages - (total_unanswered_messages + total_intuitive_messages)

            message_analytics_list[-1]["total_messages"] = message_analytics_list[-1][
                "total_messages"] + total_messages
            message_analytics_list[-1]["total_unanswered_messages"] = message_analytics_list[-1][
                "total_unanswered_messages"] + total_unanswered_messages
            message_analytics_list[-1]["total_intuitive_messages"] = message_analytics_list[-1][
                "total_intuitive_messages"] + total_intuitive_messages
            message_analytics_list[-1]["total_answered_messages"] = message_analytics_list[-1][
                "total_answered_messages"] + total_answered_messages
            message_analytics_list[-1]["predicted_messages_no"] = avg_msgs
            message_analytics_list[-1]["false_positive_messages"] += date_filtered_mis_objects.filter(
                flagged_queries_positive_type="1").count()

            this_30days_start = datetime_end - datetime.timedelta(30)

            previous_mis_objects_count = previous_mis_objects.filter(
                date_message_analytics__lte=datetime_end, date_message_analytics__gt=this_30days_start).aggregate(Sum('total_messages_count'))['total_messages_count__sum']

            if previous_mis_objects_count == None:
                previous_mis_objects_count = 0

            today_mis_objects = previous_mis_objects_count + mis_objects.count()

            last_30days_start = datetime_end - datetime.timedelta(60)
            last_day_mis_objects = previous_mis_objects.filter(
                date_message_analytics__lte=this_30days_start, date_message_analytics__gt=last_30days_start).aggregate(Sum('total_messages_count'))['total_messages_count__sum']

            if last_day_mis_objects == None:
                last_day_mis_objects = 0

            if last_day_mis_objects > 0:
                percentage_change = round(100 * float(
                    today_mis_objects - last_day_mis_objects) / float(last_day_mis_objects), 2)
            else:
                percentage_change = "None"
            percentage_change_type = 'Since last 30 days'

        data_dict["message_analytics_list"] = message_analytics_list
        data_dict["percentage_change"] = percentage_change
        data_dict["percentage_change_type"] = percentage_change_type

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_monthly_message_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return data_dict


def get_combined_user_analytics(response, bot_objs, datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, filter_type, labels):
    try:
        status = 500
        message = "Internal Server Error"

        date_today = datetime.date.today()

        mis_objs = return_mis_objects_based_on_category_channel_language(
            date_today, date_today, bot_objs, channel_name, category_name, selected_language, supported_languages, MISDashboard, UserSessionHealth)
        previous_mis_objects = return_unique_users_objects_based_on_filter(
            bot_objs, channel_name, selected_language, supported_languages, UniqueUsers)
        user_analytics_list, total_days = get_combined_user_analytics_list(
            datetime_start, datetime_end, mis_objs, previous_mis_objects, filter_type, labels)
        response["start_date"] = datetime_start.strftime("%d-%b-%y")
        response["end_date"] = datetime_end.strftime("%d-%b-%y")
        response["total_no_of_days"] = total_days
        response["user_analytics_data"] = user_analytics_list

        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_combined_user_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return response, status, message


def get_daily_user_analytics_list(datetime_start, datetime_end, previous_mis_objects, mis_objs, labels):
    no_of_days = 0
    today_flag = False
    user_analytics_list = []
    try:
        today_date = datetime.date.today().strftime("%d-%b-%y")
        if datetime_end.strftime("%d-%b-%y") == today_date:
            no_of_days = (datetime_end - datetime_start).days
            today_flag = True
        else:
            no_of_days = (datetime_end - datetime_start).days + 1
            today_flag = False

        for day in range(no_of_days):
            temp_datetime = datetime_start + datetime.timedelta(day)
            date_filtered_mis_objects = previous_mis_objects.filter(
                date=temp_datetime)
            count = date_filtered_mis_objects.aggregate(
                Sum('count'))['count__sum']
            count = return_zero_if_number_is_none(count)

            session_count = date_filtered_mis_objects.aggregate(
                Sum('session_count'))['session_count__sum']

            session_count = return_zero_if_number_is_none(
                session_count)

            user_analytics_list.append({
                labels[0]: str(temp_datetime.strftime("%d-%b-%y")),
                labels[1]: count,
                labels[2]: session_count,
            })

        if today_flag:
            user_analytics_data = get_current_day_user_analytics_data(mis_objs)
            user_analytics_list.append({
                labels[0]: str(today_date),
                labels[1]: user_analytics_data["count"],
                labels[2]: user_analytics_data["session_count"]
            })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_daily_user_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return user_analytics_list, no_of_days, today_flag


def get_weekly_user_analytics_list(datetime_start, datetime_end, previous_mis_objects, mis_objs, labels):
    today_flag = False
    user_analytics_list = []
    try:
        today_date = datetime.date.today().strftime("%d-%b-%y")

        if datetime_end.strftime("%d-%b-%y") == today_date:
            today_flag = True

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

            total_sessions = date_filtered_mis_objects.aggregate(
                Sum('session_count'))['session_count__sum']

            if total_users == None:
                total_users = 0

            if total_sessions == None:
                total_sessions = 0

            temp_start_datetime_str = (temp_start_datetime + datetime.timedelta(1)).strftime(
                "%d/%m")
            temp_end_datetime_str = (
                temp_end_datetime).strftime("%d/%m")
            user_analytics_list.append({
                labels[0]: temp_start_datetime_str + "-" + temp_end_datetime_str,
                labels[1]: total_users,
                labels[2]: total_sessions,
            })

        user_analytics_list = user_analytics_list[::-1]

        if today_flag:
            user_analytics_data = get_current_day_user_analytics_data(mis_objs)
            user_analytics_list[-1][labels[1]] += user_analytics_data["count"]
            user_analytics_list[-1][labels[2]
                                    ] += user_analytics_data["session_count"]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_weekly_user_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return user_analytics_list


def get_monthly_user_analytics_list(datetime_start, datetime_end, previous_mis_objects, mis_objs, labels):
    user_analytics_list = []
    try:
        today_date = datetime.date.today()

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

            total_sessions = previous_mis_objects.filter(date__month=temp_month, date__year=temp_year).aggregate(
                Sum('session_count'))['session_count__sum']

            if total_sessions == None:
                total_sessions = 0

            user_analytics_list.append({
                labels[0]: month,
                labels[1]: date_filtered_mis_objects,
                labels[2]: total_sessions,
            })

        if datetime_end.month == today_date.month:
            user_analytics_data = get_current_day_user_analytics_data(mis_objs)
            user_analytics_list[-1][labels[1]] += user_analytics_data["count"]
            user_analytics_list[-1][labels[2]
                                    ] += user_analytics_data["session_count"]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_monthly_user_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return user_analytics_list


def get_current_day_user_analytics_data(date_filtered_mis_objects):
    user_analytics_data = {
        "count": 0,
        "session_count": 0
    }
    try:
        total_users = date_filtered_mis_objects.values(
            "user_id").distinct().count()
        user_analytics_data["count"] = user_analytics_data[
            "count"] + total_users
        total_sessions = date_filtered_mis_objects.values(
            "session_id").distinct().count()
        user_analytics_data["session_count"] = user_analytics_data[
            "session_count"] + total_sessions

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_current_day_user_analytics_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return user_analytics_data


def get_combined_user_analytics_list(datetime_start, datetime_end, mis_objs, previous_mis_objects, filter_type, labels):

    user_analytics_list = []
    total_days = 0
    try:
        if filter_type == "1":
            user_analytics_list, no_of_days, today_flag = get_daily_user_analytics_list(
                datetime_start, datetime_end, previous_mis_objects, mis_objs, labels)
        elif filter_type == "2":
            user_analytics_list = get_weekly_user_analytics_list(
                datetime_start, datetime_end, previous_mis_objects, mis_objs, labels)
        else:
            user_analytics_list = get_monthly_user_analytics_list(
                datetime_start, datetime_end, previous_mis_objects, mis_objs, labels)

        if filter_type == "1":
            if today_flag:
                total_days = no_of_days + 1
            else:
                total_days = no_of_days
        elif filter_type == "2":
            total_days = len(user_analytics_list) * 7
        elif filter_type == "3":
            total_days = len(user_analytics_list) * 30

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_combined_user_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return user_analytics_list, total_days


def get_session_analytics(response, uat_bot_obj, datetime_start, datetime_end, channel_name, selected_language, supported_languages, filter_type):
    try:
        status = 500
        message = "Internal Server Error"
        prod_bot_obj = None
        bot_objs = []
        if prod_bot_obj == None:
            bot_objs = [uat_bot_obj]
        else:
            bot_objs = [prod_bot_obj]
        mis_objs = return_mis_objects_based_on_category_channel_language(
            datetime_start, datetime_end, bot_objs, channel_name, "All", selected_language, supported_languages, MISDashboard, UserSessionHealth)
        mis_objs = mis_objs.filter(is_session_started=True)
        if filter_type == "global" or filter_type == "avg_session_analytics":

            ave_time_spent_time_user = get_average_session_time(
                bot_objs, TimeSpentByUser, datetime_start, datetime_end)
            ave_time_spent_time_user = get_time_in_standard_format(
                ave_time_spent_time_user)

            ave_number_of_messages_per_session, no_of_unique_sessions = get_average_number_of_message_per_session(
                mis_objs)

            no_of_likes = mis_objs.filter(is_helpful_field=1).count()
            no_of_dislikes = mis_objs.filter(is_helpful_field=-1).count()
            no_feedback_asked_or_given = mis_objs.filter(
                is_helpful_field=0).count()
            total_messages = mis_objs.count()

            response[
                "ave_number_of_messages_per_session"] = ave_number_of_messages_per_session
            response["ave_time_spent_time_user"] = ave_time_spent_time_user
            response["no_of_likes"] = no_of_likes
            response["no_of_dislikes"] = no_of_dislikes
            response["no_feedback_asked_or_given"] = no_feedback_asked_or_given
            response["no_of_unique_sessions"] = no_of_unique_sessions
            response["total_messages"] = total_messages
            response["start_date"] = datetime_start.strftime("%d-%b-%y")
            response["end_date"] = datetime_end.strftime("%d-%b-%y")

        if filter_type == "global" or filter_type == "bot_accuracy":
            bot_accuracy = get_bot_accuracy(mis_objs)
            response["bot_accuracy"] = bot_accuracy
        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_session_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return response, status, message


def get_channel_usage_analytics(response, uat_bot_obj, datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, filter_name):
    try:
        status = 500
        message = "Internal Serever Error"
        prod_bot_obj = None

        bot_objs = []
        if prod_bot_obj == None:
            bot_objs = [uat_bot_obj]
        else:
            bot_objs = [prod_bot_obj]

        if filter_name == "Users":
            mis_objects = return_mis_objects_based_on_category_channel_language(
                datetime_start, datetime_end, bot_objs, channel_name, "All", selected_language, supported_languages, MISDashboard, UserSessionHealth)

        else:
            mis_objects = return_mis_objects_based_on_category_channel_language(
                datetime_start, datetime_end, bot_objs, channel_name, category_name, selected_language, supported_languages, MISDashboard, UserSessionHealth)

        if filter_name == "Users":
            mis_objects = mis_objects.order_by('user_id').values_list(
                'user_id', 'channel_name').distinct()
            channel_name_frequency = list(mis_objects.filter(~Q(channel_name=None)).values(
                "channel_name").order_by("channel_name").annotate(frequency=Count("user_id", distinct=True)).order_by('-frequency'))
        else:
            channel_name_frequency = list(mis_objects.filter(~Q(channel_name=None)).values(
                "channel_name").order_by("channel_name").annotate(frequency=Count("channel_name")).order_by('-frequency'))

        channel_dict = {}
        if channel_name == 'All':
            for channel_obj in Channel.objects.filter(is_easychat_channel=True):
                channel_dict[channel_obj.name] = 0
        else:
            channel_dict[channel_name] = 0

        for channel_detail in channel_name_frequency:
            channel_dict[channel_detail["channel_name"]
                         ] = channel_detail["frequency"]

        response["channel_dict"] = channel_dict
        response["start_date"] = datetime_start.strftime("%d-%b-%y")
        response["end_date"] = datetime_end.strftime("%d-%b-%y")
        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_channel_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return response, status, message


def get_form_assist_intent_data(uat_bot_obj, datetime_start, datetime_end, supported_languages, is_language_filter_applied, dropdown_language="en", search_term=""):
    try:
        form_assist_bot = FormAssistAnalytics.objects.none()
        if is_language_filter_applied:
            form_assist_bot = FormAssistAnalytics.objects.filter(
                bot=uat_bot_obj, lead_datetime__date__gte=datetime_start, lead_datetime__date__lte=datetime_end, selected_language__in=supported_languages)
        else:
            form_assist_bot = FormAssistAnalytics.objects.filter(
                bot=uat_bot_obj, lead_datetime__date__gte=datetime_start, lead_datetime__date__lte=datetime_end)

        form_assist_list = list(form_assist_bot)

        no_of_users_assisted = len(form_assist_list)
        no_user_find_helpful = 0
        for form in form_assist_list:
            if form.is_helpful == True:
                no_user_find_helpful += 1
        intent_objs = Intent.objects.filter(
            bots=uat_bot_obj, is_form_assist_enabled=True, is_hidden=False)
        if search_term:
            intent_objs = intent_objs.filter(name__icontains=search_term)

        form_assist_field_data_english = []
        form_assist_field_data_multilingual = []
        translate_api_status = True
        for intent_obj in intent_objs:
            try:
                form_assist_id = FormAssist.objects.filter(
                    intent=intent_obj, bot=uat_bot_obj)[0]

                form_assist_field_obj = form_assist_bot.filter(form_assist_field=form_assist_id)

                length_assist_field = form_assist_field_obj.count()
                if search_term:
                    if search_term.lower() in intent_obj.name.lower():
                        form_assist_field_data_english.append({
                            "intent": intent_obj.name,
                            "user_assisted": length_assist_field
                        })
                else:
                    form_assist_field_data_english.append({
                        "intent": intent_obj.name,
                        "user_assisted": length_assist_field
                    })
                if translate_api_status:
                    intent_name, translate_api_status = get_multilingual_intent_obj_name(
                        intent_obj, dropdown_language, translate_api_status)
                    if search_term:
                        if search_term.lower() in intent_name.lower():
                            form_assist_field_data_multilingual.append({
                                "intent": intent_name,
                                "user_assisted": length_assist_field
                            })
                    else:
                        form_assist_field_data_multilingual.append({
                            "intent": intent_name,
                            "user_assisted": length_assist_field
                        })
            except Exception:
                pass

        if translate_api_status:
            form_assist_field_data = form_assist_field_data_multilingual
        else:
            form_assist_field_data = form_assist_field_data_english

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_form_assist_intent_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return form_assist_field_data, no_of_users_assisted, no_user_find_helpful


def get_word_cloud_data(uat_bot_obj, datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages):
    try:
        result_wordcloud = []
        if category_name != "All":
            category_obj = Category.objects.get(
                name=category_name, bot=uat_bot_obj)

        word_cloud_array = []
        if channel_name != "All":
            word_cloud_objects = WordCloudAnalyticsDaily.objects.filter(
                bot=uat_bot_obj, date__gte=datetime_start, date__lte=datetime_end, channel=Channel.objects.get(name=channel_name))
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
                bot=uat_bot_obj, date__gte=datetime_start, date__lte=datetime_end, channel=Channel.objects.get(name=channel_name))
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
        result_wordcloud = [{'word': name, 'freq': str(sum(int(items['freq']) for items in word_dict))}for name, word_dict in groupby(
            sorted(word_cloud_array, key=get_name), key=get_name)]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_word_cloud_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return result_wordcloud


def get_user_nudge_analytics(bot_obj, start_date, end_date, category_name, selected_language, supported_languages):
    try:
        status = 500
        message = "Internal Server Error"
        user_nudge_analytics_data = []

        start_date, end_date = convert_date_into_obj(start_date, end_date)

        channel_objs = Channel.objects.filter(name="Web")

        bubble_click_count_objs = AutoPopUpClickInfo.objects.filter(
            bot=bot_obj, date__gte=start_date, date__lte=end_date)

        if selected_language.lower() != "all":
            bubble_click_count_objs = bubble_click_count_objs.filter(
                selected_language__in=supported_languages)

        distinct_bubble_click_objs = bubble_click_count_objs.exclude(
            name="Greeting bubble").values("name").distinct()

        auto_popup_type = bot_obj.auto_popup_type
        auto_popup_initial_messages = []
        if str(auto_popup_type) == "3":
            auto_popup_initial_messages = json.loads(
                bot_obj.auto_popup_initial_messages)

        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel_objs[0])[0]
        languages_supported = bot_channel_obj.languages_supported.all().exclude(
            lang="en").values("lang")

        for language_supported in languages_supported:
            auto_popup_initial_messages += get_translated_text("$$$".join(json.loads(
                bot_obj.auto_popup_initial_messages)), language_supported["lang"], EasyChatTranslationCache).split("$$$")

        other_lang_to_english_dict = {}
        initial_messages = json.loads(bot_obj.auto_popup_initial_messages)
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

        user_nudge_analytics_data = [{
            "name": "Greeting bubble",
            "count": bubble_click_count_objs.filter(name="Greeting bubble").count(),
            "is_active": str(auto_popup_type) in ["2", "3"]
        }]

        for distinct_bubble_click_obj in distinct_bubble_click_objs:
            try:
                if category_name != "All":
                    Intent.objects.get(bots__in=[bot_obj], name=other_lang_to_english_dict[distinct_bubble_click_obj["name"].strip(
                    )], category__name=category_name.strip(), channels__in=channel_objs)
                user_nudge_analytics_data.append({
                    "name": distinct_bubble_click_obj["name"],
                    "count": bubble_click_count_objs.filter(name=distinct_bubble_click_obj["name"]).count(),
                    "is_active": distinct_bubble_click_obj["name"] in auto_popup_initial_messages
                })
            except:
                continue
        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_user_nudge_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return user_nudge_analytics_data, status, message


def get_livechat_conversion_analytics(response, bot_objs, intent_obj, start_date, end_date, channels, channel_names, livechat_filter):
    try:
        status = 500
        message = "Internal Server Error"

        start_date, end_date = convert_date_into_obj(start_date, end_date)
        intent_raised_previous_day = 0
        request_raised_previous_day = 0
        agent_connect_previous_day = 0

        if livechat_filter == "false":
            total_start_date = datetime.datetime.now().date() - datetime.timedelta(days=7)
            total_end_date = datetime.datetime.now().date()
            previous_date = total_start_date - datetime.timedelta(days=1)
        else:
            total_start_date = start_date
            total_end_date = end_date
        
        bot_info_obj = get_bot_info_object(bot_objs[0])
        
        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            livechat_completion_data_list, intent_raised_total, request_raised_total, agent_connect_total, intent_raised_previous_day, request_raised_previous_day, agent_connect_previous_day = load_livechat_conversion_analytics_static_data()

        else:
            daily_livechat_analytics_objs = DailyLiveChatAnalytics.objects.filter(date__gte=total_start_date, date__lte=total_end_date, bot=bot_objs[0], channel__name__in=channel_names)
            intent_raised_total = 0
            
            request_raised_total = LiveChatCustomer.objects.filter(
                bot__in=bot_objs, request_raised_date__gte=total_start_date, request_raised_date__lte=total_end_date, channel__in=channels).count()
            agent_connect_total = LiveChatCustomer.objects.filter(
                bot__in=bot_objs, request_raised_date__gte=total_start_date, request_raised_date__lte=total_end_date, channel__in=channels).exclude(agent_id=None).count()

            livechat_completion_data_list = []
            for i_counter in range((end_date - start_date).days + 1):
                livechat_completion_data = {}
                current_date = start_date + \
                    datetime.timedelta(days=i_counter)
                livechat_completion_data['date'] = str(current_date.date())

                current_livechat_analytics_count = daily_livechat_analytics_objs.filter(date=current_date, channel__name__in=channel_names).aggregate(Sum("count"))["count__sum"]
                livechat_completion_data['intent_raised_count'] = 0
                if current_livechat_analytics_count:
                    livechat_completion_data['intent_raised_count'] = current_livechat_analytics_count
                    intent_raised_total += current_livechat_analytics_count
                
                livechat_completion_data['request_raised_count'] = LiveChatCustomer.objects.filter(
                    bot__in=bot_objs, request_raised_date=current_date, channel__in=channels).count()
                livechat_completion_data['agent_connect_count'] = LiveChatCustomer.objects.filter(
                    bot__in=bot_objs, request_raised_date=current_date, channel__in=channels).exclude(agent_id=None).count()
                livechat_completion_data_list.append(
                    livechat_completion_data)

            if livechat_filter == "false":
                intent_raised_previous_day = daily_livechat_analytics_objs.filter(date=previous_date, channel__name__in=channel_names).aggregate(Sum("count"))["count__sum"]
                if not intent_raised_previous_day:
                    intent_raised_previous_day = 0
                request_raised_previous_day = LiveChatCustomer.objects.filter(
                    bot__in=bot_objs, request_raised_date=previous_date, channel__in=channels).count()
                agent_connect_previous_day = LiveChatCustomer.objects.filter(
                    bot__in=bot_objs, request_raised_date=previous_date, channel__in=channels).exclude(agent_id=None).count()
        response["livechat_completion_data"] = livechat_completion_data_list
        response["intent_raised_total"] = intent_raised_total
        response["request_raised_total"] = request_raised_total
        response["agent_connect_total"] = agent_connect_total
        response["intent_raised_previous_day"] = intent_raised_previous_day
        response["request_raised_previous_day"] = request_raised_previous_day
        response["agent_connect_previous_day"] = agent_connect_previous_day

        status = 200
        message = "Success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_livechat_conversion_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return response, status, message


def get_conversion_intent_analytics(bot_objs, channels, start_date, end_date):
    try:
        start_date, end_date = convert_date_into_obj(start_date, end_date)

        mis_object = return_mis_objects_excluding_blocked_sessions(MISDashboard.objects, UserSessionHealth)

        intent_count = list(mis_object.filter(bot__in=bot_objs, channel_name__in=channels, creation_date__gte=start_date, creation_date__lte=end_date).values(
            'intent_name', 'intent_recognized').order_by('intent_name').annotate(count=Count('intent_name')).exclude(intent_recognized__isnull=True))
        total_intent_count = mis_object.filter(
            bot__in=bot_objs, channel_name__in=channels, creation_date__gte=start_date, creation_date__lte=end_date).exclude(intent_recognized__isnull=True).count()
        intent_completion_data_list = sorted(
            list(intent_count), key=lambda i: i['count'], reverse=True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_conversion_intent_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return total_intent_count, intent_completion_data_list


def get_whatsapp_block_user_session_analytics(bot_obj, block_type, start_date, end_date):
    try:
        blocked_session_objs = []
        start_date, end_date = convert_date_into_obj(start_date, end_date)

        if block_type == "All":
            blocked_session_objs = list(UserSessionHealth.objects.filter(bot=bot_obj, is_blocked=True, creation_date__gte=start_date, creation_date__lte=end_date).order_by('-block_time').values(
                'block_type', 'blocked_spam_keywords', 'block_time', 'unblock_time', whatsapp_number=F('profile__user_id')
            ))
        else:
            blocked_session_objs = list(UserSessionHealth.objects.filter(bot=bot_obj, is_blocked=True, block_type=block_type, creation_date__gte=start_date, creation_date__lte=end_date).order_by('-block_time').values(
                'block_type', 'blocked_spam_keywords', 'block_time', 'unblock_time', whatsapp_number=F('profile__user_id')
            ))

        for session_obj in blocked_session_objs:
            session_obj["block_time"] = str(session_obj["block_time"].astimezone(get_current_timezone()))
            session_obj["unblock_time"] = str(session_obj["unblock_time"].astimezone(get_current_timezone()))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_whatsapp_block_user_session_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
    return blocked_session_objs


def get_whatsapp_catalogue_conversion_analytics(bot_obj, is_catalogue_purchased, start_date, end_date, is_date_obj=False, is_paginator_required=False, page=1):
    try:
        cart_objs_list = []
        is_last_page = False
        if not is_date_obj:
            start_date, end_date = convert_date_into_obj(start_date, end_date)

        cart_objs_list = WhatsappCatalogueCart.objects.filter(
            bot=bot_obj, cart_update_time__date__gte=start_date, cart_update_time__date__lte=end_date)

        if is_catalogue_purchased == "1":
            cart_objs_list = cart_objs_list.filter(is_purchased=True)
        elif is_catalogue_purchased == "0":
            cart_objs_list = cart_objs_list.filter(is_purchased=False)

        cart_objs_list = cart_objs_list.order_by('-cart_update_time')

        if is_paginator_required:

            paginator = Paginator(cart_objs_list, 20)
            try:
                cart_objs_list = paginator.page(page)
            except PageNotAnInteger:
                cart_objs_list = paginator.page(1)
            except EmptyPage:
                cart_objs_list = paginator.page(paginator.num_pages)

            no_pages = paginator.num_pages
            if int(page) >= int(no_pages):
                is_last_page = True

            cart_objs_list = cart_objs_list.object_list

        cart_objs_list = list(cart_objs_list.values(
            'user__user_id', 'current_cart_packet', 'is_purchased', 'cart_update_time', 'cart_total'))

        for cart_obj in cart_objs_list:
            cart_obj["cart_update_time"] = cart_obj["cart_update_time"].astimezone(
                get_current_timezone())
            if not is_date_obj:
                cart_obj["cart_update_time"] = str(
                    cart_obj["cart_update_time"])
            cart_obj["current_cart_packet"] = parse_catalogue_cart_packet(
                cart_obj["current_cart_packet"])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_whatsapp_catalogue_conversion_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return cart_objs_list, is_last_page


def get_bot_hit_list_data(uat_bot_obj, source_list, start_date, end_date):
    try:
        bot_hit_data_list = []

        start_date, end_date = convert_date_into_obj(start_date, end_date)

        bot_hit_data_list = list(TrafficSources.objects.filter(bot=uat_bot_obj, visiting_date__gte=start_date, visiting_date__lte=end_date, web_page_source__in=source_list).values('web_page', 'web_page_source').annotate(
            bot_views=Sum('bot_clicked_count'), page_views=Sum('web_page_visited')).exclude(web_page_source__isnull=True).exclude(web_page_source="").order_by("-bot_views", "-page_views"))

        for bot_hit_data in bot_hit_data_list:
            average_time_spent = TimeSpentByUser.objects.filter(
                bot=uat_bot_obj, web_page=bot_hit_data['web_page'], web_page_source=bot_hit_data['web_page_source']).aggregate(Sum('total_time_spent'))['total_time_spent__sum']
            if average_time_spent:
                bot_hit_data['average_time_spent'] = average_time_spent
            else:
                bot_hit_data['average_time_spent'] = 0

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_bot_hit_list_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return bot_hit_data_list


def get_welcome_banner_clicks_data(bot_objs, start_date, end_date):
    try:
        welcome_banner_clicked_data_list = []
        total_clicks = 0

        start_date, end_date = convert_date_into_obj(start_date, end_date)

        welcome_banner_clicked_data_list = WelcomeBannerClicks.objects.filter(bot__in=bot_objs, visiting_date__gte=start_date, visiting_date__lte=end_date).values(
            'web_page_visited', 'preview_source', 'pk', 'intent__name', 'intent__pk').annotate(frequency=Count("user_id"))
        total_clicks = welcome_banner_clicked_data_list.aggregate(Sum('frequency'))[
            "frequency__sum"]
        welcome_banner_clicked_data_list = list(
            welcome_banner_clicked_data_list)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_welcome_banner_clicks_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return welcome_banner_clicked_data_list, total_clicks


def convert_date_into_obj(start_date, end_date):
    try:
        datetime_start = start_date.split("-")
        start_date = datetime.datetime(int(datetime_start[0]), int(
            datetime_start[1]), int(datetime_start[2]))
        datetime_end = end_date.split("-")
        end_date = datetime.datetime(int(datetime_end[0]), int(
            datetime_end[1]), int(datetime_end[2]))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("convert_date_into_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        start_date = (datetime.datetime.today() - timedelta(7)).date()
        end_date = datetime.datetime.today().date()

    return start_date, end_date


def get_conversion_drop_off_data(bot_objs, channel_objs, start_date, end_date, selected_language="en"):
    try:
        result = []
        status = 500
        message = 'Internal Server Error'
        translate_api_status = True

        start_date, end_date = convert_date_into_obj(start_date, end_date)

        all_triggered_flows_intent_pk_list = get_all_bot_flows_intent_pk_list(
            start_date, end_date, bot_objs, channel_objs, Intent, Tree, FlowAnalytics, DailyFlowAnalytics)

        for intent_pk in all_triggered_flows_intent_pk_list:
            intent_obj = Intent.objects.get(pk=intent_pk)
            root_tree_obj = intent_obj.tree

            flow_analytics_objects = DailyFlowAnalytics.objects.filter(
                intent_indentifed=intent_obj, created_time__date__gte=start_date, created_time__date__lte=end_date, channel__in=channel_objs)
            
            flow_analytics_objects_that_day = FlowAnalytics.objects.none()
            if end_date.date() == datetime.datetime.now().date():
                flow_analytics_objects_that_day = FlowAnalytics.objects.filter(intent_indentifed=intent_obj, created_time__date=end_date.date(), channel__in=channel_objs)
            
            flow_termination_data_objs = FlowTerminationData.objects.filter(
                intent=intent_obj, created_datetime__date__gte=start_date, created_datetime__date__lte=end_date, channel__in=channel_objs)

            count_intent_was_called = 0
            try:
                count_intent_was_called = flow_analytics_objects.filter(
                    current_tree=intent_obj.tree).aggregate(Sum('count'))['count__sum']
                if count_intent_was_called == None:
                    count_intent_was_called = 0
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("GetConversionDropOffAnalyticsAPI Intent count problem %s in line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': "None"})
                pass
            try:
                count_intent_was_called += flow_analytics_objects_that_day.filter(
                    current_tree=intent_obj.tree).count()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("GetConversionDropOffAnalyticsAPI Intent count problem that day %s in line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': "None"})
                count_intent_was_called = 0
                pass
            temp_result, translate_api_status = get_child_tree_objs_flow_dropoff_analytics(root_tree_obj.pk, root_tree_obj, [
            ], flow_analytics_objects, flow_analytics_objects_that_day, flow_termination_data_objs, intent_obj, count_intent_was_called, [], [], True, 1, [], selected_language)
            result += temp_result
        result = sorted(result, key=lambda d: d["dropoffs"])
        result.reverse()
        if translate_api_status:
            status = 200
        else:
            status = 300
        message = 'Success'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_conversion_drop_off_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return result, status, message


def get_conversion_node_analytics_data(intent_obj, start_date, end_date, channel_objs):
    try:
        status = 500
        message = "Internal Server Error"
        json_resp = {}
        max_level = 0
        root_tree_obj = intent_obj.tree
        flow_analytics_objects = DailyFlowAnalytics.objects.filter(
            intent_indentifed=intent_obj, created_time__date__gte=start_date, created_time__date__lte=end_date, channel__in=channel_objs)
        flow_analytics_objects_that_day = FlowAnalytics.objects.filter(
            intent_indentifed=intent_obj, created_time__date__gte=start_date, created_time__date__lte=end_date, channel__in=channel_objs)
        flow_termination_data_objs = FlowTerminationData.objects.filter(intent=intent_obj,
                                                                        created_datetime__date__gte=start_date, created_datetime__date__lte=end_date, channel__in=channel_objs)

        count_intent_was_called = 0
        try:
            count_intent_was_called = flow_analytics_objects.filter(
                current_tree=intent_obj.tree).aggregate(Sum('count'))['count__sum']
            if count_intent_was_called == None:
                count_intent_was_called = 0
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetConversionNodeAnalytics Intent count problem %s in line no %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': "None"})
            pass
        try:
            count_intent_was_called += flow_analytics_objects_that_day.filter(
                current_tree=intent_obj.tree).count()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetConversionNodeAnalytics Intent count problem that day %s in line no %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': "None"})
            count_intent_was_called = 0
            pass

        json_resp, max_level, _ = get_child_tree_objs_flow_analytics(root_tree_obj.pk, root_tree_obj, [
        ], flow_analytics_objects, flow_analytics_objects_that_day, flow_termination_data_objs, intent_obj, count_intent_was_called, [], [], True, 1, 0, 0)

        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_conversion_node_analytics_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return json_resp, max_level, status, message


def load_livechat_conversion_analytics_static_data():
    livechat_completion_data_list = STATIC_EASYCHAT_CONVERSION_LIVECHAT_DUMMY_DATA
    intent_raised_total = STATIC_EASYCHAT_CONVERSION_LIVECHAT_INTENT_RAISED_COUNT
    request_raised_total = STATIC_EASYCHAT_CONVERSION_LIVECHAT_REQUEST_RAISED_COUNT
    agent_connect_total = STATIC_EASYCHAT_CONVERSION_LIVECHAT_AGENT_CONNECT_COUNT
    intent_raised_previous_day = STATIC_EASYCHAT_CONVERSION_LIVECHAT_PREVIOUS_INTENT_RAISED_COUNT
    request_raised_previous_day = STATIC_EASYCHAT_CONVERSION_LIVECHAT_PREVIOUS_REQUEST_RAISED_COUNT
    agent_connect_previous_day = STATIC_EASYCHAT_CONVERSION_LIVECHAT_PREVIOUS_AGENT_CONNECT_COUNT

    return livechat_completion_data_list, intent_raised_total, request_raised_total, agent_connect_total, intent_raised_previous_day, request_raised_previous_day, agent_connect_previous_day


def get_combined_device_specific_analytics(response, bot_objs, datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, filter_type):
    try:
        status = 500
        message = "Internal Server Error"
        category_obj = None
        if category_name != "All":
            category_obj = Category.objects.filter(
                bot=bot_objs[0], name=category_name).first()

        if channel_name.strip().lower() not in ["web", "all"]:
            response["status"] = 400
            return response, 400, "Channel name can be either 'Web' or 'All'"

        date_today = datetime.date.today()
        
        mis_objects = return_mis_objects_based_on_category_channel_language(date_today, date_today, bot_objs, channel_name, "All", selected_language, supported_languages, MISDashboard, UserSessionHealth)

        previous_mis_objects = return_mis_daily_objects_based_on_filter(bot_objs, channel_name, category_name, category_obj, selected_language, supported_languages, MessageAnalyticsDaily)
        
        previous_unique_users_mis_objects = return_unique_users_objects_based_on_filter(
            bot_objs, channel_name, selected_language, supported_languages, UniqueUsers)
        
        device_specific_analytics_list, total_days = get_combined_device_specific_analytics_list(
            datetime_start, datetime_end, mis_objects, previous_mis_objects, previous_unique_users_mis_objects, filter_type, category_name)

        response["start_date"] = datetime_start.strftime("%d-%b-%y")
        response["end_date"] = datetime_end.strftime("%d-%b-%y")
        response["total_no_of_days"] = total_days
        response["device_specific_analytics_list"] = device_specific_analytics_list

        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_combined_user_analytics: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return response, status, message


def get_combined_device_specific_analytics_list(datetime_start, datetime_end, mis_objects, previous_mis_objects, previous_unique_mis_objects, filter_type, category_name):

    device_specific_analytics_list = []
    total_days = 0
    today_flag = False
    no_of_days = 0
    try:
        if filter_type == "1":
            device_specific_analytics_list, no_of_days, today_flag = get_daily_device_specific_analytics_list(
                datetime_start, datetime_end, mis_objects, previous_mis_objects, previous_unique_mis_objects, category_name)

        elif filter_type == "2":
            device_specific_analytics_list = get_weekly_device_specific_analytics_list(
                datetime_start, datetime_end, mis_objects, previous_mis_objects, previous_unique_mis_objects, category_name)
        else:
            device_specific_analytics_list = get_monthly_device_specific_analytics_list(
                datetime_start, datetime_end, mis_objects, previous_mis_objects, previous_unique_mis_objects, category_name)
        
        total_days = get_total_days_based_on_filter_type(filter_type, today_flag, no_of_days, device_specific_analytics_list)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_combined_device_specific_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return device_specific_analytics_list, total_days


def get_daily_device_specific_analytics_list(datetime_start, datetime_end, mis_objects, previous_mis_objects, previous_unique_mis_objects, category_name):
    today_flag = False
    no_of_days = 0
    
    device_specific_analytics_list = []
    try:
        if datetime_end.strftime("%d-%b-%y") == datetime.datetime.today().strftime("%d-%b-%y"):
            no_of_days = (datetime_end - datetime_start).days
            today_flag = True
        else:
            no_of_days = (datetime_end - datetime_start).days + 1
            today_flag = False

        for day in range(no_of_days):
            temp_datetime = datetime_start + datetime.timedelta(day)
            date_filtered_mis_objects = previous_mis_objects.filter(
                date_message_analytics=temp_datetime)

            date_filtered_mis_objects_users = previous_unique_mis_objects.filter(
                date=temp_datetime)
            
            device_specific_message_analytics_dict = get_device_specific_previous_message_analytics_list(date_filtered_mis_objects, str((temp_datetime).strftime("%d-%b-%y")))
            device_specific_analytics_list.append(get_device_specific_previous_users_analytics_list(date_filtered_mis_objects_users, device_specific_message_analytics_dict))
        
        if datetime_end.strftime("%d-%b-%y") == datetime.datetime.today().strftime("%d-%b-%y"):
            date_filtered_mis_objects = mis_objects

            device_specific_analytics_list.append(get_device_specific_analytics_list(date_filtered_mis_objects, datetime_end, category_name))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_daily_device_specific_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return device_specific_analytics_list, no_of_days, today_flag


def get_weekly_device_specific_analytics_list(datetime_start, datetime_end, mis_objects, previous_mis_objects, previous_unique_mis_objects, category_name):

    device_specific_analytics_list = []
    no_of_days = 0
    try:
        no_of_days = (datetime_end - datetime_start).days
        no_weeks = int(no_of_days / 7.0) + 1

        for week in range(no_weeks):
            temp_end_datetime = datetime_end - \
                datetime.timedelta(week * 7)
            temp_start_datetime = datetime_end - \
                datetime.timedelta((week + 1) * 7)

            date_filtered_mis_objects = previous_mis_objects.filter(
                date_message_analytics__gt=temp_start_datetime, date_message_analytics__lte=temp_end_datetime)

            date_filtered_mis_objects_users = previous_unique_mis_objects.filter(
                date__gt=temp_start_datetime, date__lte=temp_end_datetime)

            temp_start_datetime_str = (temp_start_datetime + datetime.timedelta(1)).strftime(
                "%d/%m")
            temp_end_datetime_str = (
                temp_end_datetime).strftime("%d/%m")

            device_specific_message_analytics_dict = get_device_specific_previous_message_analytics_list(date_filtered_mis_objects, str(temp_start_datetime_str + "-" + temp_end_datetime_str))

            device_specific_analytics_list.append(get_device_specific_previous_users_analytics_list(date_filtered_mis_objects_users, device_specific_message_analytics_dict))

        device_specific_analytics_list = device_specific_analytics_list[::-1]
        if datetime_end.strftime("%d-%b-%y") == datetime.datetime.today().strftime("%d-%b-%y"):
            
            date_filtered_mis_objects = mis_objects
            device_specific_analytics_list = add_todays_data_to_device_analytics_week_and_month(date_filtered_mis_objects, datetime_end, device_specific_analytics_list, category_name)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_weekly_device_specific_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return device_specific_analytics_list


def get_monthly_device_specific_analytics_list(datetime_start, datetime_end, mis_objects, previous_mis_objects, previous_unique_mis_objects, category_name):

    device_specific_analytics_list = []
    try:
        month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
            r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days + 1)).keys())

        for month in month_list:
            temp_month = month_to_num_dict[month.split("-")[0]]
            temp_year = int(month.split("-")[1])
            
            date_filtered_mis_objects = previous_mis_objects.filter(
                date_message_analytics__month=temp_month, date_message_analytics__year=temp_year)

            date_filtered_mis_objects_users = previous_unique_mis_objects.filter(date__month=temp_month, date__year=temp_year)
            device_specific_message_analytics_dict = get_device_specific_previous_message_analytics_list(date_filtered_mis_objects, str(month))

            device_specific_analytics_list.append(get_device_specific_previous_users_analytics_list(date_filtered_mis_objects_users, device_specific_message_analytics_dict))

        if datetime_end.month == datetime.datetime.today().month:
            date_filtered_mis_objects = mis_objects
            device_specific_analytics_list = add_todays_data_to_device_analytics_week_and_month(date_filtered_mis_objects, datetime_end, device_specific_analytics_list, category_name)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_monthly_device_specific_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return device_specific_analytics_list


def get_device_specific_analytics_list(date_filtered_mis_objects, datetime_end, category_name):
    device_specific_analytics_dict = {}
    try:
        # total users desktop and mobile
        total_mis_set = date_filtered_mis_objects
        total_mobile_set = total_mis_set.filter(is_mobile=True)
        total_users = total_mis_set.values(
            "user_id").distinct().count()
        total_users_mobile = total_mobile_set.values(
            "user_id").distinct().count()
        total_users_desktop = total_users - total_users_mobile

        if category_name.lower().strip() != "all" and category_name.strip() != "":
            total_mis_set = total_mis_set.filter(category__name=category_name)
            total_mobile_set = total_mobile_set.filter(category__name=category_name)

        # total messages desktop and mobile
        total_messages = total_mis_set.count()
        total_messages_mobile = total_mobile_set.count()
        total_messages_desktop = total_messages - total_messages_mobile
        
        # unanswered messages desktop and mobile
        total_unanswered_messages_set = total_mis_set.filter(
            intent_name=None, is_unidentified_query=True, is_intiuitive_query=False).exclude(message_received="")
        total_unanswered_messages = total_unanswered_messages_set.count()
        total_unanswered_messages_mobile = total_unanswered_messages_set.filter(is_mobile=True).count()
        total_unanswered_messages_desktop = total_unanswered_messages - total_unanswered_messages_mobile
                            
        # intuitive messages desktop and mobile
        total_intuitive_messages_set = total_mis_set.filter(
            intent_name=None, is_intiuitive_query=True)
        total_intuitive_messages = total_intuitive_messages_set.count()
        total_intuitive_messages_mobile = total_intuitive_messages_set.filter(is_mobile=True).count()
        total_intuitive_messages_desktop = total_intuitive_messages - total_intuitive_messages_mobile
        # answered messages desktop and mobile
        total_answered_messages_mobile = total_messages_mobile - total_unanswered_messages_mobile
        total_answered_messages_desktop = total_messages_desktop - total_unanswered_messages_desktop

        device_specific_analytics_dict = {
            "label": str((datetime_end).strftime("%d-%b-%y")),
            "total_messages_mobile": total_messages_mobile,
            "total_answered_messages_mobile": total_answered_messages_mobile,
            "total_unanswered_messages_mobile": total_unanswered_messages_mobile,
            "total_messages_desktop": total_messages_desktop,
            "total_answered_messages_desktop": total_answered_messages_desktop,
            "total_unanswered_messages_desktop": total_unanswered_messages_desktop,
            "total_users_mobile": total_users_mobile,
            "total_users_desktop": total_users_desktop,
            "total_intuitive_messages_mobile": total_intuitive_messages_mobile,
            "total_intuitive_messages_desktop": total_intuitive_messages_desktop
        }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_device_specific_analytics_list: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        
    return device_specific_analytics_dict


def get_device_specific_previous_message_analytics_list(date_filtered_mis_objects, label):
    from django.db.models import Sum
    device_specific_analytics_dict = {}
    try:
        total_messages = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('total_messages_count'))['total_messages_count__sum'])

        total_answered_messages = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('answered_query_count'))['answered_query_count__sum'])

        total_unanswered_messages = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('unanswered_query_count'))['unanswered_query_count__sum'])
        total_intuitive_messages = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('intuitive_query_count'))['intuitive_query_count__sum'])

        total_messages_mobile = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('total_message_count_mobile'))['total_message_count_mobile__sum'])

        total_answered_messages_mobile = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('answered_query_count_mobile'))['answered_query_count_mobile__sum'])

        total_unanswered_messages_mobile = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('unanswered_query_count_mobile'))['unanswered_query_count_mobile__sum'])
        total_intuitive_messages_mobile = return_zero_if_number_is_none(date_filtered_mis_objects.aggregate(
            Sum('intuitive_query_count_mobile'))['intuitive_query_count_mobile__sum'])

        total_messages_desktop = total_messages - total_messages_mobile
        
        total_unanswered_messages_desktop = total_unanswered_messages - total_unanswered_messages_mobile
        total_intuitive_messages_desktop = total_intuitive_messages - total_intuitive_messages_mobile

        total_answered_messages_desktop = total_answered_messages - total_answered_messages_mobile

        device_specific_analytics_dict = {
            "label": label,
            "total_messages_mobile": total_messages_mobile,
            "total_answered_messages_mobile": total_answered_messages_mobile,
            "total_unanswered_messages_mobile": total_unanswered_messages_mobile,
            "total_messages_desktop": total_messages_desktop,
            "total_answered_messages_desktop": total_answered_messages_desktop,
            "total_unanswered_messages_desktop": total_unanswered_messages_desktop,
            "total_intuitive_messages_mobile": total_intuitive_messages_mobile,
            "total_intuitive_messages_desktop": total_intuitive_messages_desktop
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_device_specific_previous_message_analytics_list: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        
    return device_specific_analytics_dict


def get_device_specific_previous_users_analytics_list(date_filtered_mis_objects_users, device_specific_message_analytics_dict={}):
    from django.db.models import Sum
    try:
        total_users_count = return_zero_if_number_is_none(date_filtered_mis_objects_users.aggregate(
            Sum('count'))['count__sum'])
        total_users_mobile = return_zero_if_number_is_none(date_filtered_mis_objects_users.aggregate(
            Sum('users_count_mobile'))['users_count_mobile__sum'])
        total_users_desktop = total_users_count - total_users_mobile
        device_specific_message_analytics_dict["total_users_mobile"] = total_users_mobile
        device_specific_message_analytics_dict["total_users_desktop"] = total_users_desktop

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_device_specific_previous_users_analytics_list: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        
    return device_specific_message_analytics_dict


def add_todays_data_to_device_analytics_week_and_month(date_filtered_mis_objects, datetime_end, device_specific_analytics_list=[], category_name="All"):
    try:
        device_specific_analytics_dict = get_device_specific_analytics_list(date_filtered_mis_objects, datetime_end, category_name)

        device_specific_analytics_list[-1]["total_messages_mobile"] += device_specific_analytics_dict["total_messages_mobile"]
        device_specific_analytics_list[-1]["total_answered_messages_mobile"] += device_specific_analytics_dict["total_answered_messages_mobile"]
        device_specific_analytics_list[-1]["total_unanswered_messages_mobile"] += device_specific_analytics_dict["total_unanswered_messages_mobile"]
        device_specific_analytics_list[-1]["total_messages_desktop"] += device_specific_analytics_dict["total_messages_desktop"]
        device_specific_analytics_list[-1]["total_answered_messages_desktop"] += device_specific_analytics_dict["total_answered_messages_desktop"]
        device_specific_analytics_list[-1]["total_users_mobile"] += device_specific_analytics_dict["total_users_mobile"]
        device_specific_analytics_list[-1]["total_users_desktop"] += device_specific_analytics_dict["total_users_desktop"]
        device_specific_analytics_list[-1]["total_unanswered_messages_desktop"] += device_specific_analytics_dict["total_unanswered_messages_desktop"]
        device_specific_analytics_list[-1]["total_intuitive_messages_mobile"] += device_specific_analytics_dict["total_intuitive_messages_mobile"]
        device_specific_analytics_list[-1]["total_intuitive_messages_desktop"] += device_specific_analytics_dict["total_intuitive_messages_desktop"]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_todays_data_to_device_analytics_week_and_month: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        
    return device_specific_analytics_list


def parse_catalogue_cart_packet(cart_packet):
    try:
        parsed_cart_message = ""
        cart_packet = json.loads(cart_packet)
        catalogue_id = cart_packet["catalog_id"]
        item_names = []
        for item in cart_packet["product_items"]:
            item_obj = WhatsappCatalogueItems.objects.filter(
                catalogue_id=catalogue_id, retailer_id=item["product_retailer_id"]).values("item_name").first()
            if item_obj:
                item_name = item_obj["item_name"]
            else:
                item_name = item["product_retailer_id"]
            item_name = str(item["quantity"]) + " x " + item_name
            item_names.append(item_name)

        parsed_cart_message += ", ".join(item_names)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("parse_catalogue_cart_packet: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return parsed_cart_message


def get_combined_catalogue_analytics_list(datetime_start, datetime_end, bot_obj, filter_type):

    catalogue_combined_analytics_list = []
    total_days = 0
    today_flag = False
    no_of_days = 0
    try:
        if filter_type == "1":
            catalogue_combined_analytics_list, no_of_days, today_flag = get_daily_catalogue_combined_analytics_list(
                datetime_start, datetime_end, bot_obj)

        elif filter_type == "2":
            catalogue_combined_analytics_list = get_weekly_catalogue_combined_analytics_list(
                datetime_start, datetime_end, bot_obj)
        else:
            catalogue_combined_analytics_list = get_monthly_catalogue_combined_analytics_list(
                datetime_start, datetime_end, bot_obj)

        total_days = get_total_days_based_on_filter_type(
            filter_type, today_flag, no_of_days, catalogue_combined_analytics_list)

        if filter_type == "1":
            if today_flag:
                total_days = no_of_days + 1
            else:
                total_days = no_of_days
        elif filter_type == "2":
            total_days = len(catalogue_combined_analytics_list) * 7
        elif filter_type == "3":
            total_days = len(catalogue_combined_analytics_list) * 30

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_combined_catalogue_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return catalogue_combined_analytics_list, total_days


def get_daily_catalogue_combined_analytics_list(datetime_start, datetime_end, bot_obj):
    today_flag = False
    no_of_days = 0

    catalogue_analytics_list = []
    try:
        today_datetime = datetime.datetime.today()
        if datetime_end.strftime("%d-%b-%y") == today_datetime.strftime("%d-%b-%y"):
            no_of_days = (datetime_end - datetime_start).days
            today_flag = True
        else:
            no_of_days = (datetime_end - datetime_start).days + 1
            today_flag = False

        for day in range(no_of_days):
            temp_datetime = datetime_start + datetime.timedelta(day)

            catalogue_cart_objs = WhatsappCatalogueCart.objects.filter(
                bot=bot_obj, cart_update_time__date=temp_datetime)

            catalogue_analytics_dict = get_catalogue_combined_analytics_dict(
                catalogue_cart_objs, str((temp_datetime).strftime("%d-%b-%y")))
            catalogue_analytics_list.append(catalogue_analytics_dict)

        if datetime_end.strftime("%d-%b-%y") == today_datetime.strftime("%d-%b-%y"):
            catalogue_cart_objs = WhatsappCatalogueCart.objects.filter(
                bot=bot_obj, cart_update_time__date=today_datetime)
            catalogue_analytics_dict = get_catalogue_combined_analytics_dict(
                catalogue_cart_objs, today_datetime.strftime("%d-%b-%y"))
            catalogue_analytics_list.append(catalogue_analytics_dict)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_daily_catalogue_combined_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return catalogue_analytics_list, no_of_days, today_flag


def get_weekly_catalogue_combined_analytics_list(datetime_start, datetime_end, bot_obj):

    catalogue_analytics_list = []
    no_of_days = 0
    try:
        today_datetime = datetime.datetime.today()
        no_of_days = (datetime_end - datetime_start).days
        no_weeks = int(no_of_days / 7.0) + 1

        for week in range(no_weeks):
            temp_end_datetime = datetime_end - \
                datetime.timedelta(week * 7)
            temp_start_datetime = datetime_end - \
                datetime.timedelta((week + 1) * 7)

            catalogue_cart_objs = WhatsappCatalogueCart.objects.filter(
                bot=bot_obj, cart_update_time__gt=temp_start_datetime, cart_update_time__lte=temp_end_datetime)

            temp_start_datetime_str = (temp_start_datetime + datetime.timedelta(1)).strftime(
                "%d/%m")
            temp_end_datetime_str = (
                temp_end_datetime).strftime("%d/%m")

            catalogue_analytics_dict = get_catalogue_combined_analytics_dict(
                catalogue_cart_objs, str(temp_start_datetime_str + "-" + temp_end_datetime_str))

            catalogue_analytics_list.append(catalogue_analytics_dict)

        catalogue_analytics_list = catalogue_analytics_list[::-1]
        if datetime_end.strftime("%d-%b-%y") == today_datetime.strftime("%d-%b-%y"):
            catalogue_cart_objs = WhatsappCatalogueCart.objects.filter(
                bot=bot_obj, cart_update_time__date=today_datetime)
            catalogue_analytics_dict = get_catalogue_combined_analytics_dict(
                catalogue_cart_objs, today_datetime.strftime("%d-%b-%y"))
            catalogue_analytics_list[-1]["total_carts"] += catalogue_analytics_dict["total_carts"]
            catalogue_analytics_list[-1]["total_purchased_carts"] += catalogue_analytics_dict["total_purchased_carts"]
            catalogue_analytics_list[-1]["total_conversion_ratio"] = (catalogue_analytics_list[-1]["total_purchased_carts"] / catalogue_analytics_list[-1]
                                                                      ["total_carts"]) * 100 if catalogue_analytics_list[-1]["total_carts"] else 0
            catalogue_analytics_list[-1]["total_conversion_ratio"] = format(catalogue_analytics_list[-1]["total_conversion_ratio"], '.2f')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_weekly_catalogue_combined_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return catalogue_analytics_list


def get_monthly_catalogue_combined_analytics_list(datetime_start, datetime_end, bot_obj):

    catalogue_analytics_list = []
    try:
        month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
            r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days + 1)).keys())

        for month in month_list:
            temp_month = month_to_num_dict[month.split("-")[0]]
            temp_year = int(month.split("-")[1])

            catalogue_cart_obj = WhatsappCatalogueCart.objects.filter(
                bot=bot_obj, cart_update_time__month=temp_month, cart_update_time__year=temp_year)
            
            catalogue_analytics_dict = get_catalogue_combined_analytics_dict(catalogue_cart_obj, str(month))

            catalogue_analytics_list.append(catalogue_analytics_dict)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_monthly_catalogue_combined_analytics_list: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return catalogue_analytics_list


def get_catalogue_combined_analytics_dict(catalogue_cart_objs, label):
    try:

        total_carts = catalogue_cart_objs.count()
        total_purchased_carts = catalogue_cart_objs.filter(
            is_purchased=True).count()
        total_conversion_ratio = (
            total_purchased_carts / total_carts) * 100 if total_carts else 0

        catalogue_analytics_dict = {
            "label": label,
            "total_carts": total_carts,
            "total_purchased_carts": total_purchased_carts,
            "total_conversion_ratio": format(total_conversion_ratio, '.2f')
        }

        return catalogue_analytics_dict
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_catalogue_combined_analytics_dict: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

    return {}
