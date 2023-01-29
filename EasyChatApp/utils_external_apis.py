import copy
from django.conf import settings

from datetime import date, datetime, timedelta
import sys
import func_timeout
import pytz
import json
import uuid
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from EasyChatApp.static_dummy_data import *

from EasyChatApp.utils_api_analytics import get_basic_analytics, get_combined_catalogue_analytics_list, get_session_analytics, get_channel_usage_analytics, get_form_assist_intent_data, get_whatsapp_catalogue_conversion_analytics, get_word_cloud_data, get_user_nudge_analytics, get_livechat_conversion_analytics, get_conversion_intent_analytics, get_bot_hit_list_data, get_welcome_banner_clicks_data, get_conversion_drop_off_data, convert_date_into_obj, get_conversion_node_analytics_data, get_combined_user_analytics, get_combined_message_analytics, get_combined_device_specific_analytics, get_csat_analytics, get_combined_hour_wise_analytics, get_whatsapp_block_user_session_analytics
from EasyChatApp.utils_analytics import get_intent_frequency, get_recently_unanswered_messages, get_intuitive_messages, get_category_wise_intent_frequency, get_conversion_flow_counts_data, get_start_and_end_time
from EasyChatApp.models import Category, DailyFlowAnalytics, EasyChatExternalAPIAuditTrail, EasyChatTranslationCache, FlowAnalytics, FlowTerminationData, Intent, Language, EasyChatAuthToken, Bot, MISDashboard, Channel, Tree, UnAnsweredQueries, IntuitiveQuestions, TrafficSources, UserSessionHealth
from EasyChatApp.constants import EXTERNAL_API_FUNCTION_EXEC_TIME_LIMIT, MAX_MESSAGE_PER_PAGE

# Logger
import logging
from EasyChatApp.utils_bot import get_translated_text_with_api_status
from EasyChatApp.utils_custom_encryption import CustomEncrypt
from EasyChatApp.utils_execute_query import get_bot_info_object

from EasyChatApp.utils_validation import EasyChatInputValidation
logger = logging.getLogger(__name__)


def check_easychat_external_data_is_valid(data, external_api_audit_obj):
    bot_obj = None
    response_message = "Auth Token Valid"
    status_code = 200
    try:
        if 'auth_token' not in data:
            return bot_obj, 400, "Invalid Auth Token!"

        auth_token = data['auth_token']
        try:
            # Checks if the auth token is a valid UUID4
            uuid.UUID(auth_token).version == 4
        except ValueError:
            return bot_obj, 400, "Invalid Auth Token!"

        auth_token_obj = EasyChatAuthToken.objects.filter(
            token=auth_token).first()

        if not auth_token_obj:
            return bot_obj, 400, "Invalid Auth Token!"

        external_api_audit_obj.token = auth_token_obj
        external_api_audit_obj.save()

        if auth_token_obj.is_expired:
            return bot_obj, 400, "Auth Token Is Expired!"

        tz = pytz.timezone(settings.TIME_ZONE)
        created_time = auth_token_obj.created_datetime.astimezone(tz)
        current_time = (datetime.now() - timedelta(hours=6)).astimezone(tz)

        if created_time < current_time:
            auth_token_obj.is_expired = True
            auth_token_obj.save()
            return bot_obj, 400, "Auth Token Is Expired!"

        is_rate_limit_excedded = update_easychat_auth_token_rate_limit(
            auth_token_obj)

        if is_rate_limit_excedded:
            return bot_obj, 429, "Rate Limit Reached"

        if 'bot_id' not in data:
            return bot_obj, 400, 'Invalid Bot ID!'

        user = auth_token_obj.user

        validation_obj = EasyChatInputValidation()
        bot_id = validation_obj.remo_html_from_string(data['bot_id'])
        bot_obj = Bot.objects.filter(pk=bot_id, is_deleted=False).first()
        if not bot_obj or user not in bot_obj.users.all():
            return bot_obj, 401, 'You are not authorised to access this bot!'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In update_easychat_auth_token_rate_limit: %s at %s", e, str(
            exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return bot_obj, status_code, response_message


def update_easychat_auth_token_rate_limit(easychat_auth_token_obj):
    is_rate_limit_excedded = False
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        last_access_time = easychat_auth_token_obj.last_accessed_time.astimezone(
            tz)
        current_time = (datetime.now() - timedelta(minutes=1)).astimezone(tz)
        current_time = current_time.astimezone(tz)

        if last_access_time >= current_time:
            easychat_auth_token_obj.api_used_in_last_minute += 1
        else:
            # reset count and last accessed time
            easychat_auth_token_obj.last_accessed_time = datetime.now()
            easychat_auth_token_obj.api_used_in_last_minute = 1

        easychat_auth_token_obj.save()
        is_rate_limit_excedded = easychat_auth_token_obj.is_rate_limit_exceeded()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In update_easychat_auth_token_rate_limit: %s at %s", e, str(
            exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return is_rate_limit_excedded


def get_external_api_response(code, message, response, external_api_audit_obj):
    try:
        response['status'] = code
        response['message'] = message
        external_api_audit_obj.response_data = json.dumps(response)
        external_api_audit_obj.status_code = code
        external_api_audit_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_external_api_response: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response


def get_supported_languages_by_selected_language(selected_language):
    try:
        supported_languages_list = []
        if selected_language.lower() != "all":
            supported_languages_list = selected_language.split(",")
            supported_languages_list = [
                lang.strip() for lang in supported_languages_list]

        supported_languages = Language.objects.filter(
            lang__in=supported_languages_list)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_supported_languages_by_selected_language: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return supported_languages


def get_basic_analytics_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channel_name = 'All'
        category_name = 'All'
        selected_language = "All"

        if 'channel_name' in data:
            channel_name = data['channel_name']
        if 'category_name' in data:
            category_name = data['category_name']
        if 'selected_language' in data:
            selected_language = data["selected_language"]

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)

        response, status, message = get_basic_analytics(
            response, bot_obj, channel_name, category_name, selected_language, supported_languages)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_basic_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_hour_wise_analytics_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channel_name = 'All'
        category_name = 'All'
        selected_language = "All"
        interval_type = "1"
        time_format = "1"

        if 'channel_name' in data:
            channel_name = data['channel_name']
        if 'selected_language' in data:
            selected_language = data["selected_language"]
        if 'category_name' in data:
            category_name = data["category_name"]
        if 'interval_type' in data:
            interval_type = data["interval_type"]
        if 'time_format' in data:
            time_format = data["time_format"]

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)
        datetime_start, datetime_end, error_message = get_start_and_end_time(
            data)
        if error_message:
            return response, 400, error_message

        response, status, message = get_combined_hour_wise_analytics(
            response, [bot_obj], datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, interval_type, time_format)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_hour_wise_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_message_analytics_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channel_name = 'All'
        category_name = 'All'
        selected_language = "All"
        filter_type = "1"

        if 'channel_name' in data and data['channel_name'].strip() != '':
            channel_name = data['channel_name']
        if 'selected_language' in data and data['selected_language'].strip() != '':
            selected_language = data["selected_language"]
        if 'category_name' in data and data['category_name'].strip() != '':
            category_name = data["category_name"]

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)
        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message
 
        filter_type = get_filter_type_for_user_analytics(data)
        labels = ["date"]

        response, status, message = get_combined_message_analytics(
            response, [bot_obj], datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, filter_type, labels)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_message_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_filter_type_for_user_analytics(data):
    try:
        filter_type = "1"
        filter_map = {
            "daily": "1",
            "weekly": "2",
            "monthly": "3",
        }

        if "filter_type" in data:
            if data["filter_type"].strip() in ["1", "2", "3"]:
                filter_type = data["filter_type"].strip()
            elif data["filter_type"].strip().lower() in filter_map.keys():
                filter_type = filter_map[data["filter_type"].strip().lower()]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error In get_filter_type_for_user_analytics: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return filter_type


def get_user_analytics_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channel_name = 'All'
        category_name = 'All'
        selected_language = "All"
        filter_type = "1"

        if 'channel_name' in data and data['channel_name'].strip() != '':
            channel_name = data['channel_name']
        if 'selected_language' in data and data['selected_language'].strip() != '':
            selected_language = data["selected_language"]
        if 'category_name' in data and data['category_name'].strip() != '':
            category_name = data["category_name"]

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)
        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message
        
        filter_type = get_filter_type_for_user_analytics(data)
        labels = ["date", "user_count", "session_count"]
        response, status, message = get_combined_user_analytics(
            response, [bot_obj], datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, filter_type, labels)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_user_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_csat_analytics_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channels = []
        csat_type = "All"

        if 'channel_list' not in data or data['channel_list'] == 'All' or data['channel_list'].split(',') == ['']:
            channels = Channel.objects.filter(is_easychat_channel=True)
        else:
            channel_list = data['channel_list'].split(',')
            channel_list = list(map(str.strip, channel_list))
            channels = Channel.objects.filter(name__in=channel_list)

        if 'csat_type' in data and data["csat_type"].strip().lower() in ["promoters", "passives", "demoters"]:
            csat_type = data["csat_type"].strip().capitalize()
        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        response, status, message = get_csat_analytics(
            response, bot_obj, datetime_start, datetime_end, channels, csat_type)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_csat_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_session_analytics_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channel_name = 'All'
        selected_language = 'All'
        filter_type = 'global'

        if 'channel_name' in data:
            channel_name = data['channel_name']
        if 'filter_type' in data:
            filter_type = data['filter_type']
        if 'selected_language' in data:
            selected_language = data["selected_language"]

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)
        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        response, status, message = get_session_analytics(
            response, bot_obj, datetime_start, datetime_end, channel_name, selected_language, supported_languages, filter_type)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_session_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_channel_analytics_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channel_name = 'All'
        selected_language = 'All'
        category_name = 'All'
        filter_name = 'Messages'

        if 'channel_name' in data:
            channel_name = data['channel_name']
        if 'filter_name' in data:
            filter_name = data['filter_name']
        if 'category_name' in data:
            category_name = data['category_name']
        if 'selected_language' in data:
            selected_language = data["selected_language"]

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)
        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        response, status, message = get_channel_usage_analytics(
            response, bot_obj, datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, filter_name)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_channel_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_frequent_intents_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channel_name = 'All'
        selected_language = 'All'
        category_name = 'All'
        reverse = 'true'

        if 'channel_name' in data:
            channel_name = data['channel_name']
        if 'category_name' in data:
            category_name = data['category_name']
        if 'reverse' in data:
            reverse = data['reverse']
        if 'selected_language' in data:
            selected_language = data["selected_language"]

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)
        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        response['intent_frequency_list'] = get_intent_frequency(
                [bot_obj], MISDashboard, UserSessionHealth, datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages)
        response['start_date'] = str(datetime_start)
        response['end_date'] = str(datetime_end)

        if str(reverse).lower() == "false":
            response['intent_frequency_list'] = sorted(response['intent_frequency_list'], key=lambda d: d['frequency'], reverse=False)
            # response['intent_frequency_list'].reverse()
       
        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_frequent_intents_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_unanswered_queries_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channel_name = 'All'
        selected_language = 'All'
        search_term = data.get("search", "")

        if 'channel_name' in data:
            channel_name = data['channel_name']
        if 'selected_language' in data:
            selected_language = data["selected_language"]

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)
        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        unanswered_questions = get_recently_unanswered_messages(
            [bot_obj], MISDashboard, UserSessionHealth, UnAnsweredQueries, Channel, datetime_start, datetime_end, channel_name, selected_language, supported_languages, search_term)
        response['unanswered_questions'] = list(unanswered_questions)
        response['start_date'] = str(datetime_start)
        response['end_date'] = str(datetime_end)

        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_unanswered_queries_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_form_assist_intent_data_external(bot_obj, data, dropdown_language="en"):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        selected_language = 'All'
        is_language_filter_applied = False
        search_term = data.get("search", "")

        if 'selected_language' in data:
            selected_language = data["selected_language"]
            if selected_language.lower() != "all":
                is_language_filter_applied = True

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)
        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        form_assist_field_data, no_of_users_assisted, no_user_find_helpful = get_form_assist_intent_data(
            bot_obj, datetime_start, datetime_end, supported_languages, is_language_filter_applied, dropdown_language, search_term)

        paginator = Paginator(form_assist_field_data, 5)
        page = data["form_assist_intent_page"]
        try:
            form_assist_field_data = paginator.page(page)
        except PageNotAnInteger:
            form_assist_field_data = paginator.page(1)
        except EmptyPage:
            form_assist_field_data = paginator.page(paginator.num_pages)

        no_pages = paginator.num_pages
        is_last_page = False
        if int(page) >= int(no_pages):
            is_last_page = True

        intent_data = []
        for intent in form_assist_field_data:
            intent_data.append(intent)
        intent_data = sorted(intent_data, key=lambda k: k['user_assisted'])
        intent_data.reverse()
        form_assist_helpful_percentage = 0
        if no_of_users_assisted > 0:
            form_assist_helpful_percentage = (
                no_user_find_helpful / no_of_users_assisted) * 100
            form_assist_helpful_percentage = round(
                form_assist_helpful_percentage, 2)

        response["is_single_page"] = False
        if paginator.num_pages == 1:
            response["is_single_page"] = True

        response["no-of-users-assisted"] = no_of_users_assisted
        response["no-user-find-helpful"] = no_user_find_helpful
        response["intent_data"] = intent_data
        response["form_assist_helpful_percentage"] = form_assist_helpful_percentage
        response['start_date'] = str(datetime_start)
        response['end_date'] = str(datetime_end)
        response["is_last_page"] = is_last_page

        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_form_assist_intent_data_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_intuitive_questions_data_external(bot_obj, data, dropdown_language="en"):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channel_name = 'All'
        selected_language = 'All'
        search_term = data.get("search", "")
        
        pagination_data = {"is_last_page": True}
        page = data.get("page", 1)
        if not page:
            page = 1

        if 'channel_name' in data:
            channel_name = data['channel_name']
        if 'selected_language' in data:
            selected_language = data["selected_language"]

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)
        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        details_of_intuitive_questions, list_of_intents_per_query, translate_api_status, pagination_data = get_intuitive_messages(
            [bot_obj], MISDashboard, IntuitiveQuestions, Channel, datetime_start, datetime_end, channel_name, selected_language, supported_languages, page, dropdown_language=dropdown_language, search_term=search_term)
        response['details_of_intuitive_questions'] = details_of_intuitive_questions
        response['list_of_intents_per_query'] = list_of_intents_per_query

        response["is_single_page"] = False
        if int(page) == 1 and pagination_data["is_last_page"]:
            response["is_single_page"] = True

        response["is_last_page"] = pagination_data["is_last_page"]

        response['start_date'] = str(datetime_start)
        response['end_date'] = str(datetime_end)
        if translate_api_status:
            status = 200
        else:
            status = 300
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_intuitive_questions_data_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_most_frequent_questions_category_wise_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channel_name = 'All'
        selected_language = 'All'
        category_names = 'All'

        if 'channel_name' in data:
            channel_name = data['channel_name']
        if 'selected_language' in data:
            selected_language = data["selected_language"]
        if 'category_names' in data:
            category_names = data['category_names'].split(',')
            category_names = list(map(str.strip, category_names))
        else:
            category_names = list(
                Category.objects.filter(bot=bot_obj).values_list('name', flat=True))

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)
        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message
        response['category_wise_intent_frequency'] = {}
        for category_name in category_names:
            intent_frequency_list = get_category_wise_intent_frequency(
                [bot_obj], MISDashboard, UserSessionHealth, datetime_start, datetime_end, category_name, channel_name, category_name, selected_language, supported_languages)
            response['category_wise_intent_frequency'][category_name] = list(
                intent_frequency_list)
        response['start_date'] = str(datetime_start)
        response['end_date'] = str(datetime_end)

        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_most_frequent_questions_category_wise_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_word_cloud_data_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channel_name = 'All'
        selected_language = 'All'
        category_name = 'All'

        if 'channel_name' in data:
            channel_name = data['channel_name']
        if 'selected_language' in data:
            selected_language = data["selected_language"]
        if 'category_name' in data:
            category_name = data['category_name']

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)
        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        result_wordcloud = get_word_cloud_data(
            bot_obj, datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages)
        response['wordcloud_data'] = result_wordcloud
        response['start_date'] = str(datetime_start)
        response['end_date'] = str(datetime_end)

        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_word_cloud_data_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_user_nudge_analytics_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        selected_language = 'All'
        category_name = 'All'

        if 'selected_language' in data:
            selected_language = data["selected_language"]
        if 'category_name' in data:
            category_name = data['category_name']

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)
        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        user_nudge_analytics_data, status, message = get_user_nudge_analytics(
            bot_obj, str(datetime_start), str(datetime_end), category_name, selected_language, supported_languages)
        response['user_nudge_analytics_data'] = user_nudge_analytics_data
        response['start_date'] = str(datetime_start)
        response['end_date'] = str(datetime_end)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_user_nudge_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_livechat_conversion_analytics_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channel_names = "All"
        livechat_filter = "false"

        if 'channel_list' not in data or data['channel_list'] == 'All' or data['channel_list'].split(',') == ['']:
            channels = Channel.objects.filter(is_easychat_channel=True)
            channel_names = list(
                Channel.objects.values_list('name', flat=True))
        else:
            channel_list = data['channel_list'].split(',')
            channel_list = list(map(str.strip, channel_list))
            channels = Channel.objects.filter(name__in=channel_list)
            channel_names = channel_list

        if 'livechat_filter' in data:
            livechat_filter = data["livechat_filter"]

        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        intent_obj = bot_obj.livechat_default_intent
        response, status, message = get_livechat_conversion_analytics(
            response, [bot_obj], intent_obj, str(datetime_start), str(datetime_end), channels, channel_names, livechat_filter)
        response['start_date'] = str(datetime_start)
        response['end_date'] = str(datetime_end)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_livechat_conversion_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_conversion_intent_analytics_external(bot_obj, data, selected_language="en"):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"

        if 'channel_list' not in data or data['channel_list'] == 'All' or data['channel_list'].split(',') == ['']:
            channels = list(Channel.objects.values_list('name', flat=True))
        else:
            channels = data['channel_list'].split(',')
            channels = list(map(str.strip, channels))

        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        bot_info_obj = get_bot_info_object(bot_obj)
        translate_api_status = True
        
        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            intent_completion_data_list = copy.deepcopy(
                STATIC_EASYCHAT_CONVERSION_INTENT_DUMMY_DATA)
            total_intent_count = copy.deepcopy(
                STATIC_EASYCHAT_CONVERSION_INTENT_TOTAL_COUNT)

            for intent in range(len(intent_completion_data_list)):
                if translate_api_status:
                    intent_completion_data_list[intent]["multilingual_name"], translate_api_status = get_translated_text_with_api_status(
                        intent_completion_data_list[intent]["intent_name"], selected_language, EasyChatTranslationCache, translate_api_status)

            response["language_script_type"] = "ltr"
            if translate_api_status:
                lang_obj = Language.objects.filter(
                    lang=selected_language).first()
                if lang_obj:
                    response["language_script_type"] = lang_obj.language_script_type
                response["status"] = 200
            else:
                response["status"] = 300

            response["intent_completion_data"] = intent_completion_data_list
            response["total_intent_count"] = total_intent_count
            response["is_last_page"] = True
            return response, response["status"], message

        else:
            total_intent_count, intent_completion_data_list = get_conversion_intent_analytics(
                [bot_obj], channels, str(datetime_start), str(datetime_end))

        response['total_intent_count'] = total_intent_count
        response['intent_completion_data_list'] = intent_completion_data_list
        response['start_date'] = str(datetime_start)
        response['end_date'] = str(datetime_end)
        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_conversion_intent_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_whatsapp_block_analytics_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"

        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        block_type = data.get("block_type", "All")

        bot_info_obj = get_bot_info_object(bot_obj)

        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            blocked_sessions = copy.deepcopy(
                STATIC_EASYCHAT_WHATSAPP_BLOCK_ANALYSIS_DUMMY_DATA)
            response["is_last_page"] = True
        else:
            blocked_sessions = get_whatsapp_block_user_session_analytics(
                bot_obj, block_type, str(datetime_start), str(datetime_end))

        response['message'] = "Success"
        response['status'] = 200
        response['block_session_data'] = blocked_sessions
        response['start_date'] = str(datetime_start)
        response['end_date'] = str(datetime_end)
        status = 200
        message = "Success"
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_whatsapp_block_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    
    return response, status, message


def get_whatsapp_catalogue_analytics_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"

        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        is_catalogue_purchased = data.get("is_catalogue_purchased", "all")

        bot_info_obj = get_bot_info_object(bot_obj)
        is_paginator_required = True if "page" in data else False
        is_last_page = True

        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            catalogue_cart_data = copy.deepcopy(
                STATIC_EASYCHAT_WHATSAPP_CATALOGUE_CONVERSION_DUMMY_DATA)
            is_paginator_required = True
        else:
            page = data["page"] if is_paginator_required else 1
            catalogue_cart_data, is_last_page = get_whatsapp_catalogue_conversion_analytics(
                bot_obj, is_catalogue_purchased, str(datetime_start), str(datetime_end), False, is_paginator_required, page)

        response["message"] = "Success"
        response["status"] = 200
        response["catalogue_cart_data"] = catalogue_cart_data
        if is_paginator_required:
            response["is_last_page"] = is_last_page
        response["start_date"] = str(datetime_start)
        response["end_date"] = str(datetime_end)
        status = 200
        message = "Success"
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_whatsapp_block_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    
    return response, status, message


def get_combined_catalogue_analytics_list_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"

        datetime_start, datetime_end, error_message = get_start_and_end_time(
            data)
        if error_message:
            return response, 400, error_message

        filter_type = data.get("filter_type", "1")

        catalogue_analytics_list, total_days = get_combined_catalogue_analytics_list(
            datetime_start, datetime_end, bot_obj, filter_type)

        response["message"] = "Success"
        response["status"] = 200
        response["catalogue_analytics_list"] = catalogue_analytics_list
        response["start_date"] = datetime_start.strftime("%d-%b-%y")
        response["end_date"] = datetime_end.strftime("%d-%b-%y")
        response["total_days"] = total_days
        status = 200
        message = "Success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_combined_catalogue_analytics_list_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_bot_hit_list_data_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"

        if 'source_list' not in data or data['source_list'].split(',') == ['']:
            source_list = list(TrafficSources.objects.filter(bot=bot_obj).values_list(
                'web_page_source', flat=True).exclude(web_page_source__isnull=True).exclude(web_page_source="").distinct())
        else:
            source_list = data['source_list'].split(',')
            source_list = list(map(str.strip, source_list))

        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message
        
        bot_info_obj = get_bot_info_object(bot_obj)
        
        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            bot_hit_data_list = STATIC_EASYCHAT_CONVERSION_TRAFFIC_ANALYTICS_DUMMY_DATA
        
        else:
            bot_hit_data_list = get_bot_hit_list_data(
                bot_obj, source_list, str(datetime_start), str(datetime_end))

        response['bot_hit_data_list'] = bot_hit_data_list
        response['start_date'] = str(datetime_start)
        response['end_date'] = str(datetime_end)
        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_bot_hit_list_data_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_welcome_banner_clicks_data_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"

        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message
        
        bot_info_obj = get_bot_info_object(bot_obj)
        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            welcome_banner_clicked_data_list = copy.deepcopy(
                STATIC_EASYCHAT_CONVERSION_WELCOME_ANALYTICS_DUMMY_DATA)
            total_clicks = copy.deepcopy(
                STATIC_EASYCHAT_CONVERSION_WELCOME_ANALYTICS_TOTAL_COUNT)
        else:
            welcome_banner_clicked_data_list, total_clicks = get_welcome_banner_clicks_data(
                [bot_obj], str(datetime_start), str(datetime_end))

        response['welcome_banner_clicked_data_list'] = welcome_banner_clicked_data_list
        response['total_clicks'] = total_clicks
        response['start_date'] = str(datetime_start)
        response['end_date'] = str(datetime_end)
        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_welcome_banner_clicks_data_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_conversion_drop_off_data_external(bot_obj, data, selected_language="en"):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"

        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        if 'channel_list' not in data or data['channel_list'] == 'All' or data['channel_list'].split(',') == ['']:
            channel_objs = Channel.objects.filter(is_easychat_channel=True)
        else:
            channel_list = data['channel_list'].split(',')
            channel_list = list(map(str.strip, channel_list))
            channel_objs = Channel.objects.filter(name__in=channel_list)
        
        bot_info_obj = get_bot_info_object(bot_obj)

        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            result = copy.deepcopy(
                STATIC_EASYCHAT_CONVERSION_DROPOFF_DUMMY_DATA)
            translate_api_status = True
            for static_data in range(len(result)):
                result[static_data][
                    "child_intent_multilingual_name"], translate_api_status = get_translated_text_with_api_status(
                    result[static_data]["child_intent_name"], selected_language, EasyChatTranslationCache,
                    translate_api_status)
                result[static_data][
                    "main_intent_multilingual_name"], translate_api_status = get_translated_text_with_api_status(
                    result[static_data]["main_intent_name"], selected_language, EasyChatTranslationCache,
                    translate_api_status)

            response["language_script_type"] = "ltr"
            if translate_api_status:
                lang_obj = Language.objects.filter(
                    lang=selected_language).first()
                if lang_obj:
                    response["language_script_type"] = lang_obj.language_script_type
                status = 200
            else:
                status = 300

            response["flow_dropoff_analytics_data"] = result
        else:
            result, status, message = get_conversion_drop_off_data(
                [bot_obj], channel_objs, str(datetime_start), str(datetime_end), selected_language)

        response['flow_dropoff_analytics_data'] = result
        response['start_date'] = str(datetime_start)
        response['end_date'] = str(datetime_end)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_conversion_drop_off_data_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_conversion_flow_analytics_data_external(bot_obj, data, selected_language="en"):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"

        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        start_date, end_date = convert_date_into_obj(
            str(datetime_start), str(datetime_end))

        if 'channel_list' not in data or data['channel_list'] == 'All' or data['channel_list'].split(',') == ['']:
            channel_objs = Channel.objects.filter(is_easychat_channel=True)
        else:
            channel_list = data['channel_list'].split(',')
            channel_list = list(map(str.strip, channel_list))
            channel_objs = Channel.objects.filter(name__in=channel_list)
        
        bot_info_obj = get_bot_info_object(bot_obj)
        translate_api_status = True
        if bot_info_obj and bot_info_obj.static_conversion_analytics:
            flow_completion_data = copy.deepcopy(
                STATIC_EASYCHAT_CONVERSION_FLOW_DUMMY_DATA)
            for intent in range(len(flow_completion_data)):
                if translate_api_status:
                    flow_completion_data[intent]["multilingual_name"], translate_api_status = get_translated_text_with_api_status(
                        flow_completion_data[intent]["name"], selected_language, EasyChatTranslationCache, translate_api_status)
        else:
            flow_completion_data, translate_api_status = get_conversion_flow_counts_data(
                start_date, end_date, [bot_obj], channel_objs, Intent, Tree, FlowAnalytics, FlowTerminationData, DailyFlowAnalytics, selected_language)
        response['flow_completion_data'] = list(flow_completion_data)
        response['start_date'] = str(start_date.date())
        response['end_date'] = str(end_date.date())
        if translate_api_status:
            status = 200
        else:
            status = 300
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_conversion_flow_analytics_data_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_conversion_node_analytics_data_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"

        if 'intent_pk' not in data:
            status = 400
            message = "Intent PK is required!"
            return response, status, message

        intent_pk = data['intent_pk']
        intent_obj = Intent.objects.filter(pk=intent_pk, bots=bot_obj).first()

        if not intent_obj:
            status = 400
            message = "Data for given Intent PK does not exist!"
            return response, status, message

        if 'channel_list' not in data or data['channel_list'] == 'All' or data['channel_list'].split(',') == ['']:
            channel_objs = Channel.objects.filter(is_easychat_channel=True)
        else:
            channel_list = data['channel_list'].split(',')
            channel_list = list(map(str.strip, channel_list))
            channel_objs = Channel.objects.filter(name__in=channel_list)

        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message

        start_date, end_date = convert_date_into_obj(
            str(datetime_start), str(datetime_end))

        json_resp, max_level, status, message = get_conversion_node_analytics_data(
            intent_obj, start_date, end_date, channel_objs)

        response['flow_tree_data'] = json.dumps(json_resp)
        response["max_level"] = max_level
        response['start_date'] = str(start_date.date())
        response['end_date'] = str(end_date.date())

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_conversion_node_analytics_data_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_device_specific_analytics_external(bot_obj, data):
    try:
        response = {}
        status = 500
        message = "Internal Server Error"
        channel_name = 'All'
        category_name = 'All'
        selected_language = "All"
        filter_type = "1"

        if 'channel_name' in data and data['selected_language'].strip() != '':
            channel_name = data['channel_name']
        if 'selected_language' in data and data['selected_language'].strip() != '':
            selected_language = data["selected_language"]
        if 'category_name' in data and data['selected_language'].strip() != '':
            category_name = data["category_name"]

        supported_languages = get_supported_languages_by_selected_language(
            selected_language)
        datetime_start, datetime_end, error_message = get_start_and_end_time(data)
        if error_message:
            return response, 400, error_message
 
        filter_type = get_filter_type_for_user_analytics(data)

        response, status, message = get_combined_device_specific_analytics(
            response, [bot_obj], datetime_start, datetime_end, channel_name, category_name, selected_language, supported_languages, filter_type)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_device_specific_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response, status, message


def get_analytics_data_external(response, analytics_types_map, analytics_type, bot_obj, filter_params):
    try:
        validation_obj = EasyChatInputValidation()
        filter_params = json.dumps(filter_params)
        filter_params = validation_obj.remo_html_from_string(filter_params)
        filter_params = json.loads(filter_params)
        data, status, message = func_timeout.func_timeout(EXTERNAL_API_FUNCTION_EXEC_TIME_LIMIT, analytics_types_map[analytics_type], args=(
            bot_obj, filter_params))
        response['data'] = data
    except func_timeout.FunctionTimedOut:
        status = 408
        message = 'Request Timed Out. Please try requesting the data of smaller date interval.'
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_analytics_data_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    response['status'] = status
    response['message'] = message
    return response


def get_external_api_audit_obj(request, access_type):
    try:
        external_api_audit_obj = EasyChatExternalAPIAuditTrail.objects.create(
            access_type=access_type)
        try:
            request_data = json.dumps(request.data)
            metadata = json.dumps(request.META)
        except:
            request_data = request.data
            metadata = request.META
        external_api_audit_obj.request_data = request_data
        external_api_audit_obj.metadata = metadata
        external_api_audit_obj.save()

        return external_api_audit_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_external_api_audit_obj: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
