from django.conf import settings

from datetime import date, datetime, timedelta
import sys
import func_timeout
import pytz
import json
import uuid
from django.db.models import Q, Count, Sum
from itertools import groupby

from LiveChatApp.utils import get_agents_under_this_user
from LiveChatApp.utils_analytics import get_analytics_channel_objs, get_analytics_category_objs_by_title, get_agents_availibility_analytics,\
    get_chats_in_queue, get_livechat_avg_queue_time, get_livechat_chat_report_history_list, get_total_tickets_raised_filtered, get_voice_calls_initiated_filtered,\
    get_followup_leads_via_email_filtered, get_chat_termination_data_filtered, get_livechat_avg_handle_time_list, get_avg_nps_list, get_livechat_avg_interaction_per_chat_list,\
    get_livechat_avg_queue_time_list, get_nps_avg_filter, get_livechat_avg_interaction_per_chat_filter, get_livechat_avh_filter, get_livechat_avq_filter,\
    get_average_call_duration_filtered, get_average_video_call_duration_filtered, get_average_cobrowsing_duration_filtered, get_total_customers_reported_filtered
from LiveChatApp.constants import EXTERNAL_API_FUNCTION_EXEC_TIME_LIMIT, AUTH_TOKEN_VALIDITY_DURATION, DATE_DD_MMM_YYYY_TIME_HH_MIN_P, DATE_DD_MMM_YYYY
from LiveChatApp.models import LiveChatExternalAPIAuditTrail, LiveChatCustomer, LiveChatUser, LiveChatCategory, LiveChatConfig, LiveChatAdminConfig,\
    LiveChatAuthToken, LiveChatFollowupCustomer, LiveChatReportedCustomer, LiveChatTicketAudit, LiveChatVoIPData, LiveChatMISDashboard, LiveChatCobrowsingData,\
    LiveChatSessionManagement, LiveChatAgentNotReady
from EasyChatApp.models import Channel, Bot

# Logger
import logging

from LiveChatApp.utils_validation import LiveChatInputValidation
logger = logging.getLogger(__name__)


def get_external_api_audit_obj(request, access_type):
    try:
        external_api_audit_obj = LiveChatExternalAPIAuditTrail.objects.create(
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
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return None


def get_external_api_response(code, message, response, external_api_audit_obj):
    try:
        response['status'] = code
        response['message'] = message
        external_api_audit_obj.response_data = json.dumps(response)
        external_api_audit_obj.status_code = code
        external_api_audit_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_external_api_response: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response


def update_livechat_auth_token_rate_limit(livechat_auth_token_obj):
    is_rate_limit_exceeded = False
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        last_access_time = livechat_auth_token_obj.last_accessed_time.astimezone(
            tz)
        current_time = (datetime.now() - timedelta(minutes=1)).astimezone(tz)
        current_time = current_time.astimezone(tz)

        if last_access_time >= current_time:
            livechat_auth_token_obj.api_used_in_last_minute += 1
        else:
            # reset count and last accessed time
            livechat_auth_token_obj.last_accessed_time = datetime.now()
            livechat_auth_token_obj.api_used_in_last_minute = 1

        livechat_auth_token_obj.save()
        is_rate_limit_exceeded = livechat_auth_token_obj.is_rate_limit_exceeded()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_livechat_auth_token_rate_limit: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return is_rate_limit_exceeded


def check_livechat_external_data_is_valid(data, external_api_audit_obj):
    livechat_user = None
    response_message = "Auth Token Valid"
    status_code = 200
    try:
        if 'auth_token' not in data:
            return livechat_user, 400, "Invalid Auth Token!"

        auth_token = data['auth_token']
        try:
            # Checks if the auth token is a valid UUID4
            uuid.UUID(auth_token).version == 4
        except ValueError:
            return livechat_user, 400, "Invalid Auth Token!"

        auth_token_obj = LiveChatAuthToken.objects.filter(
            token=auth_token).first()

        if not auth_token_obj:
            return livechat_user, 400, "Invalid Auth Token!"

        external_api_audit_obj.token = auth_token_obj
        external_api_audit_obj.save()

        if auth_token_obj.is_expired:
            return livechat_user, 400, "Auth Token Is Expired!"

        tz = pytz.timezone(settings.TIME_ZONE)
        created_time = auth_token_obj.created_datetime.astimezone(tz)
        current_time = (datetime.now() - timedelta(hours=AUTH_TOKEN_VALIDITY_DURATION)).astimezone(tz)

        if created_time < current_time:
            auth_token_obj.is_expired = True
            auth_token_obj.save()
            return livechat_user, 400, "Auth Token Is Expired!"

        is_rate_limit_exceeded = update_livechat_auth_token_rate_limit(
            auth_token_obj)

        if is_rate_limit_exceeded:
            return livechat_user, 429, "Rate Limit Reached"

        livechat_user = auth_token_obj.user

        if not livechat_user or livechat_user.status == '3':
            return livechat_user, 401, "Unauthorized access!"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_livechat_external_data_is_valid: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return livechat_user, status_code, response_message


def get_analytics_data_external(response, analytics_types_map, analytics_type, livechat_user, filter_params):
    try:
        validation_obj = LiveChatInputValidation()
        filter_params = json.dumps(filter_params)
        filter_params = validation_obj.remo_html_from_string(filter_params)
        filter_params = json.loads(filter_params)
        data, status, message = func_timeout.func_timeout(EXTERNAL_API_FUNCTION_EXEC_TIME_LIMIT, analytics_types_map[analytics_type], args=(
            livechat_user, filter_params))
        response['data'] = data
    except func_timeout.FunctionTimedOut:
        status = 408
        message = 'Request Timed Out. Please try requesting the data of smaller date interval.'
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_analytics_data_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    response['status'] = status
    response['message'] = message
    return response


def get_channel_and_category_objs(livechat_user, filter_params, is_single_select=False):
    try:
        channel_name = 'All'
        category_data = 'All'

        if 'channel_name' in filter_params:
            channel_name = filter_params['channel_name']
        if 'category_data' in filter_params:
            category_data = filter_params['category_data']

        if channel_name.strip() == "":
            channel_name = "All"
        if not isinstance(category_data, dict) and category_data.strip() == "":
            category_data = "All"

        channel_objs = get_analytics_channel_objs(channel_name.strip(), Channel)
        category_objs = get_analytics_category_objs_by_title(category_data, livechat_user, is_single_select, Bot, LiveChatCategory)

        if not channel_objs:
            channel_objs = get_analytics_channel_objs('All', Channel)

        if not category_objs:
            category_objs = get_analytics_category_objs_by_title('All', livechat_user, is_single_select, Bot, LiveChatCategory)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_channel_and_category_objs: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return channel_objs, category_objs


def get_start_and_end_time(data):
    try:
        date_format = "%Y-%m-%d"
        start_date = data["start_date"]
        end_date = data["end_date"]

        datetime_start = datetime.strptime(start_date, date_format).date()
        datetime_end = datetime.strptime(end_date, date_format).date() 

        if datetime_start > datetime_end:
            return datetime_start, datetime_end, "Start date can not be greater than End date!"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_start_and_end_time: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        datetime_start = (datetime.today() - timedelta(7)).date()
        datetime_end = datetime.today().date()

    return datetime_start, datetime_end, None


def get_agent_objs_external(livechat_user, filter_params, is_multiselect=False):
    try:
        agent_filter = "All"

        if 'agent_username_list' in filter_params and is_multiselect:
            agent_filter = filter_params['agent_username_list']
            if not isinstance(agent_filter, list) and agent_filter.strip() != "":
                agent_filter = json.loads(agent_filter)

        elif 'agent_username' in filter_params:
            agent_filter = filter_params['agent_username']
            if agent_filter.strip() != "" and agent_filter.strip() != "All":
                agent_filter = [agent_filter]

        if (isinstance(agent_filter, str) and agent_filter.strip() == "") or (isinstance(agent_filter, list) and len(agent_filter) == 0):
            agent_filter = "All"

        if isinstance(agent_filter, str) and agent_filter == "All":
            return get_agents_under_this_user(livechat_user)

        agent_objs = LiveChatUser.objects.filter(user__username__in=agent_filter)

        return agent_objs

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_agent_objs: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return get_agents_under_this_user(livechat_user)


def get_bot_objs_external(livechat_user, filter_params):
    try:
        bot_list = livechat_user.bots.all()
        bot_id = 0

        if 'bot_id' in filter_params:
            bot_id = filter_params['bot_id']

        if isinstance(bot_id, str) and bot_id == "All":
            return bot_list

        if bot_id and bot_id != '0':
            bot_list = [Bot.objects.get(pk=int(bot_id))]

        return bot_list

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_bot_objs_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return livechat_user.bots.all()


def get_live_analytics_external(livechat_user, filter_params):
    try:
        response = {}
        status = 500
        message = 'Internal Server Error'

        user_obj_list = get_agents_under_this_user(livechat_user)

        channel_objs, category_objs = get_channel_and_category_objs(livechat_user, filter_params)

        category_wise_agent_list = []
        for user in user_obj_list:
            if user.status == "1":
                continue
            for category in user.category.all():
                if category in category_objs:
                    category_wise_agent_list.append(user)
                    break

        # Getting Agent Report
        agents_logged_in, ready_agents, not_ready_agents, stop_interaction_agents, current_capacity = get_agents_availibility_analytics(
            category_wise_agent_list, LiveChatAdminConfig, LiveChatUser)

        response["agent_report"] = {
            "agents_logged_in": agents_logged_in,
            "stop_interaction_instances": stop_interaction_agents,
            "active_agents": ready_agents,
            "inactive_agents": not_ready_agents
        }

        # Getting System Report
        chats_in_queue = get_chats_in_queue(
            user_obj_list, channel_objs, category_objs, Bot.objects.none(), LiveChatCustomer, LiveChatConfig)
        average_queue_time, avg_queue_time_percentage_change = get_livechat_avg_queue_time(
            user_obj_list, channel_objs, category_objs, LiveChatCustomer)

        response["system_report"] = {
            "requests_in_queue": chats_in_queue,
            "current_total_capacity": current_capacity,
            "customer_wait_time": average_queue_time
        }

        # Getting Real Time Chat Report
        ongoing_chats = LiveChatCustomer.objects.filter(~Q(agent_id=None)).filter(
            last_appearance_date__date=datetime.today().date(), is_session_exp=False, agent_id__in=user_obj_list, channel__in=channel_objs, category__in=category_objs).count()
        followup_leads = LiveChatFollowupCustomer.objects.filter(
            agent_id__in=user_obj_list, livechat_customer__channel__in=channel_objs, livechat_customer__category__in=category_objs).aggregate(Sum("followup_count"))
        customers_reported = LiveChatReportedCustomer.objects.filter(
            created_date__date=datetime.today().date(), livechat_customer__agent_id__in=user_obj_list, is_reported=True, is_completed=False,
            livechat_customer__channel__in=channel_objs, livechat_customer__category__in=category_objs).count()

        response["real_time_chat_report"] = {
            "ongoing_chats": ongoing_chats,
            "total_followup_leads": 0 if not followup_leads['followup_count__sum'] else followup_leads['followup_count__sum'],
            "customers_reported": customers_reported
        }

        # Getting Chat Termination
        chat_termination_data = dict(LiveChatCustomer.objects.filter(
            last_appearance_date__date=datetime.today().date(), is_session_exp=True, agent_id__in=user_obj_list, channel__in=channel_objs, 
            category__in=category_objs).values_list('chat_ended_by').annotate(total=Count('chat_ended_by')).order_by('total'))

        response["chat_termination"] = chat_termination_data

        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_live_analytics_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message


def get_chat_reports_external(livechat_user, filter_params):
    try:
        response = {}
        status = 500
        message = 'Internal Server Error'

        datetime_start, datetime_end, error_message = get_start_and_end_time(filter_params)
        if error_message:
            return response, 400, error_message

        user_obj_list = get_agents_under_this_user(livechat_user)

        channel_objs, category_objs = get_channel_and_category_objs(livechat_user, filter_params)

        # Getting Chat Data
        chat_report_graph_data, total_chats_raised, total_chats_resolved, missed_chats, offline_chats, abandoned_chats = get_livechat_chat_report_history_list(
            str(datetime_start), str(datetime_end), channel_objs, category_objs, user_obj_list, True, Bot, LiveChatConfig, LiveChatCustomer)

        for chat_report_data in chat_report_graph_data:
            chat_report_data["total_chats_raised"] = chat_report_data.pop("total_entered_chat", 0)
            chat_report_data["total_chats_resolved"] = chat_report_data.pop("total_closed_chat", 0)
            chat_report_data["missed_chats"] = chat_report_data.pop("denied_chats", 0)
            chat_report_data["offline_chats"] = chat_report_data.pop("abandon_chats", 0)
            chat_report_data["abandoned_chats"] = chat_report_data.pop("customer_declined_chats", 0)

        response = {
            "chat_report_graph": chat_report_graph_data,
            "total_chats_raised": total_chats_raised,
            "total_chats_resolved": total_chats_resolved,
            "abandoned_chats": abandoned_chats,
            "missed_chats": missed_chats,
            "offline_chats": offline_chats
        }

        # Getting Total Tickets Raised
        total_tickets_raised = get_total_tickets_raised_filtered(user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatTicketAudit)

        response["total_tickets_raised"] = total_tickets_raised

        # Getting Voice Calls Initiated
        voice_calls_initiated = get_voice_calls_initiated_filtered(user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatVoIPData)

        response["voice_calls_initiated"] = voice_calls_initiated

        # Getting Email Followup Leads
        followup_leads_via_email = get_followup_leads_via_email_filtered(user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, Channel, LiveChatFollowupCustomer)

        response["followup_leads_via_email"] = followup_leads_via_email

        # Getting Chat Termination Data
        chat_termination_data = get_chat_termination_data_filtered(user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatCustomer, Channel)

        response["chat_termination"] = chat_termination_data

        status = 200
        message = "Success"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_chat_reports_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message


def get_average_nps_external(livechat_user, filter_params):
    try:
        response = {}
        status = 500
        message = 'Internal Server Error'

        datetime_start, datetime_end, error_message = get_start_and_end_time(filter_params)
        if error_message:
            return response, 400, error_message

        user_obj_list = get_agents_under_this_user(livechat_user)

        channel_objs, category_objs = get_channel_and_category_objs(livechat_user, filter_params)

        average_nps_list, average_nps = get_avg_nps_list(
            str(datetime_start), str(datetime_end), channel_objs, user_obj_list, True, category_objs, LiveChatCustomer)

        response["average_nps_graph"] = average_nps_list

        status = 200
        message = 'Success'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_average_nps_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message


def get_average_messages_per_chat_external(livechat_user, filter_params):
    try:
        response = {}
        status = 500
        message = 'Internal Server Error'

        datetime_start, datetime_end, error_message = get_start_and_end_time(filter_params)
        if error_message:
            return response, 400, error_message

        user_obj_list = get_agents_under_this_user(livechat_user)

        channel_objs, category_objs = get_channel_and_category_objs(livechat_user, filter_params)

        average_messages_list, average_messages = get_livechat_avg_interaction_per_chat_list(
            str(datetime_start), str(datetime_end), channel_objs, user_obj_list, True, category_objs, LiveChatCustomer, LiveChatMISDashboard)

        response["average_messages_per_chat_graph"] = average_messages_list

        status = 200
        message = 'Success'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_average_messages_per_chat_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message


def get_average_handling_time(livechat_user, filter_params):
    try:
        response = {}
        status = 500
        message = 'Internal Server Error'

        datetime_start, datetime_end, error_message = get_start_and_end_time(filter_params)
        if error_message:
            return response, 400, error_message

        user_obj_list = get_agents_under_this_user(livechat_user)

        channel_objs, category_objs = get_channel_and_category_objs(livechat_user, filter_params)

        average_handle_time_list, average_handle_time = get_livechat_avg_handle_time_list(
            str(datetime_start), str(datetime_end), channel_objs, user_obj_list, True, category_objs, LiveChatCustomer)

        response["average_handle_time_graph"] = average_handle_time_list

        status = 200
        message = 'Success'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_average_handling_time: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message


def get_average_customer_wait_time_external(livechat_user, filter_params):
    try:
        response = {}
        status = 500
        message = 'Internal Server Error'

        datetime_start, datetime_end, error_message = get_start_and_end_time(filter_params)
        if error_message:
            return response, 400, error_message

        user_obj_list = get_agents_under_this_user(livechat_user)

        channel_objs, category_objs = get_channel_and_category_objs(livechat_user, filter_params)

        average_customer_wait_time_list, average_customer_wait_time = get_livechat_avg_queue_time_list(
            str(datetime_start), str(datetime_end), channel_objs, user_obj_list, True, category_objs, LiveChatCustomer)

        response["average_customer_wait_time_graph"] = average_customer_wait_time_list

        status = 200
        message = 'Success'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_average_customer_wait_time_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message


def get_customer_reports_external(livechat_user, filter_params):
    try:
        response = {}
        status = 500
        message = 'Internal Server Error'

        datetime_start, datetime_end, error_message = get_start_and_end_time(filter_params)
        if error_message:
            return response, 400, error_message

        user_obj_list = get_agents_under_this_user(livechat_user)

        channel_objs, category_objs = get_channel_and_category_objs(livechat_user, filter_params)

        average_nps = get_nps_avg_filter(
            user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatCustomer)

        average_messages_per_chat = get_livechat_avg_interaction_per_chat_filter(
            user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatCustomer, LiveChatMISDashboard)

        average_handling_time = get_livechat_avh_filter(
            user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatCustomer)

        average_customer_wait_time = get_livechat_avq_filter(
            user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatCustomer)
            
        average_call_duration = get_average_call_duration_filtered(user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatVoIPData)

        average_video_call_duration = get_average_video_call_duration_filtered(user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatVoIPData)

        average_cobrowsing_session_duration = get_average_cobrowsing_duration_filtered(user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatCobrowsingData)

        total_customers_reported = get_total_customers_reported_filtered(user_obj_list, datetime_start, datetime_end, channel_objs, category_objs, LiveChatReportedCustomer)

        response = {
            "average_nps": average_nps,
            "average_messages_per_chat": average_messages_per_chat,
            "average_handling_time": average_handling_time,
            "average_customer_wait_time": average_customer_wait_time,
            "average_call_duration": average_call_duration,
            "average_video_call_duration": average_video_call_duration,
            "average_cobrowsing_session_duration": average_cobrowsing_session_duration,
            "total_customers_reported": total_customers_reported
        }

        status = 200
        message = 'Success'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_customer_reports_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message


def get_performance_report_external(livechat_user, filter_params):
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        response = {}
        status = 500
        message = 'Internal Server Error'

        datetime_start, datetime_end, error_message = get_start_and_end_time(filter_params)
        if error_message:
            return response, 400, error_message      

        agent_list = get_agent_objs_external(livechat_user, filter_params, True)
        if not agent_list:
            agent_list = get_agents_under_this_user(livechat_user) 

        session_objects = LiveChatSessionManagement.objects.filter(user__in=agent_list, session_starts_at__date__range=[
            datetime_start, datetime_end]).order_by('-session_starts_at')

        performance_report = []
        for session in session_objects:
            session_report = {
                'agent_name': session.get_name(),
                'login_datetime': session.session_starts_at.astimezone(tz).strftime(DATE_DD_MMM_YYYY_TIME_HH_MIN_P),
                'logout_datetime': '-' if not session.session_completed else session.session_ends_at.astimezone(tz).strftime(DATE_DD_MMM_YYYY_TIME_HH_MIN_P),
                'login_duration': session.get_session_duration(),
                'average_handling_time': session.get_average_handle_time(),
                'idle_time': session.get_idle_duration(),
                'not_ready_count': session.get_not_ready_count(),
                'not_ready_duration': session.get_total_offline_time(),
                'interaction_count': session.get_interaction_count(),
                'interaction_duration': session.get_interaction_duration(),
                'self_assigned_chat_count': session.get_self_assigned_chat(),
                'transfer_chat_received_count': session.get_total_transferred_chat_received(),
                'transfer_chat_made_count': session.get_total_transferred_chat_made(),
                'total_group_chat_requests': session.get_total_group_chat_request(),
                'accepted_group_chats': session.get_total_group_chat_accept(),
                'declined_group_chats': session.get_total_group_chat_reject(),
                'no_accept/reject_group_chat': session.get_total_group_chat_no_response(),
                'total_group_chat_duration': session.get_total_group_chat_duration()
            }

            performance_report.append(session_report)

        response["performance_report"] = performance_report

        status = 200
        message = 'Success'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_performance_report_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message


def get_daily_interaction_external(livechat_user, filter_params):
    try:
        response = {}
        status = 500
        message = 'Internal Server Error'

        datetime_start, datetime_end, error_message = get_start_and_end_time(filter_params)
        if error_message:
            return response, 400, error_message    

        agent_list = get_agents_under_this_user(livechat_user)

        bot_list = get_bot_objs_external(livechat_user, filter_params)

        interaction_objects = []
        interaction_object_list = LiveChatCustomer.objects.filter(
            agent_id__in=agent_list, request_raised_date__range=[datetime_start, datetime_end]).order_by('-joined_date')

        for bot_obj in bot_list:
            interaction_list = list(interaction_object_list.filter(bot=bot_obj).values(
                "joined_date").order_by("joined_date").annotate(frequency=Count("joined_date")))
            for obj in interaction_list:
                interaction_objects.append(
                    {"date": obj["joined_date"].date(), "bot_name": bot_obj.name, "interaction_count": obj["frequency"]})

        freq_array = [(key, len(list(group)))
                      for key, group in groupby(interaction_objects)]

        interaction_objects = []
        for freq_obj in freq_array:
            freq_obj[0]["interaction_count"] = freq_obj[1]
            interaction_objects.append(freq_obj[0])

        interaction_objects = sorted(
            interaction_objects, key=lambda val: val['date'])[::-1]

        for interaction_object in interaction_objects:
            interaction_object['date'] = interaction_object['date'].strftime(DATE_DD_MMM_YYYY)

        response["daily_interaction"] = interaction_objects

        status = 200
        message = 'Success' 

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_daily_interaction_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message


def get_hourly_interaction_external(livechat_user, filter_params):
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        response = {}
        status = 500
        message = 'Internal Server Error'

        try:
            date_format = "%Y-%m-%d"
            start_date = filter_params["start_date"]
            end_date = filter_params["end_date"]

            datetime_start = datetime.strptime(start_date, date_format)
            datetime_end = datetime.strptime(end_date, date_format) 

            if datetime_start > datetime_end:
                return response, 400, "Start date can not be greater than End date!"

        except Exception:

            datetime_start = (datetime.today() - timedelta(7))
            datetime_end = datetime.today()

        agent_list = get_agents_under_this_user(livechat_user)

        bot_list = get_bot_objs_external(livechat_user, filter_params)

        interaction_objects = []
        interaction_object_list = LiveChatCustomer.objects.filter(agent_id__in=agent_list, request_raised_date__range=[
            datetime_start.date(), datetime_end.date()]).order_by('-joined_date')

        for bot_obj in bot_list:
            current_datetime = datetime_start
            current_datetime_end = datetime_end

            go_live_date = bot_obj.go_live_date.astimezone(tz)
            current_datetime = current_datetime.astimezone(tz)
            current_datetime_end = current_datetime_end.astimezone(tz)
            current_datetime = max(current_datetime, go_live_date)

            while current_datetime <= current_datetime_end:
                start_time_obj = current_datetime.time().replace(hour=0, minute=0, second=0)
                for itr in range(1, 25):
                    if current_datetime.date() == datetime.now().date() and start_time_obj > datetime.now().time():
                        break

                    end_time_obj = current_datetime.time().replace(hour=itr %
                                                                   24, minute=0, second=0)
                    interaction_count = interaction_object_list.filter(bot=bot_obj, request_raised_date=current_datetime.date(
                    ), joined_date__time__range=[start_time_obj, end_time_obj]).count()
                    interaction_objects.append({"date": current_datetime, "start_time": start_time_obj,
                                                "end_time": end_time_obj, "bot_name": bot_obj.name, "interaction_count": interaction_count})
                    start_time_obj = current_datetime.time().replace(hour=itr %
                                                                     24, minute=0, second=1)

                current_datetime = current_datetime + timedelta(days=1)

        interaction_objects = sorted(
            interaction_objects, key=lambda val: (val['date'], val['start_time']))[::-1]

        for interaction_object in interaction_objects:
            interaction_object['date'] = interaction_object['date'].strftime(DATE_DD_MMM_YYYY)
            interaction_object['start_time'] = interaction_object['start_time'].strftime('%I:%M %p')
            interaction_object['end_time'] = interaction_object['end_time'].strftime('%I:%M %p')

        response["hourly_interaction"] = interaction_objects

        status = 200
        message = 'Success' 

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_hourly_interaction_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message


def get_login_logout_report_external(livechat_user, filter_params):
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        response = {}
        status = 500
        message = 'Internal Server Error'

        datetime_start, datetime_end, error_message = get_start_and_end_time(filter_params)
        if error_message:
            return response, 400, error_message      

        agent_list = get_agent_objs_external(livechat_user, filter_params)
        if not agent_list:
            agent_list = get_agents_under_this_user(livechat_user)  

        session_objects = LiveChatSessionManagement.objects.filter(user__in=agent_list, session_starts_at__date__range=[
                                                                   datetime_start, datetime_end]).order_by('-session_starts_at')

        login_logout_report = []
        for session in session_objects:
            session_report = {
                'agent_username': session.user.user.username,
                'date': session.session_starts_at.astimezone(tz).strftime(DATE_DD_MMM_YYYY),
                'duration': session.get_session_duration(),
                'agent_name': session.get_name(),
                'login_time': session.session_starts_at.astimezone(tz).strftime('%I:%M %p'),
                'logout_time': session.session_ends_at.astimezone(tz).strftime('%I:%M %p'),
                'online_time': session.get_total_online_time(),
                'offline_time': session.get_total_offline_time()
            }

            login_logout_report.append(session_report)

        response["login_logout_report"] = login_logout_report

        status = 200
        message = 'Success'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_login_logout_report_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message


def get_agent_not_ready_report_external(livechat_user, filter_params):
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        response = {}
        status = 500
        message = 'Internal Server Error'

        datetime_start, datetime_end, error_message = get_start_and_end_time(filter_params)
        if error_message:
            return response, 400, error_message      

        agent_list = get_agent_objs_external(livechat_user, filter_params)
        if not agent_list:
            agent_list = get_agents_under_this_user(livechat_user)  

        not_ready_objects = LiveChatAgentNotReady.objects.filter(user__in=agent_list, not_ready_starts_at__date__range=[
            datetime_start, datetime_end]).order_by('-not_ready_starts_at')

        agent_not_ready_report = []
        for not_ready_object in not_ready_objects:
            not_ready_report = {
                'date': not_ready_object.not_ready_starts_at.astimezone(tz).strftime(DATE_DD_MMM_YYYY),
                'agent_name': not_ready_object.user.get_agent_name(),
                'agent_username': not_ready_object.user.user.username,
                'reason': not_ready_object.get_reason_for_offline(),
                'stop_interaction_duration': not_ready_object.get_stop_interaction_duration(),
                'total_offline_time': not_ready_object.get_offline_duration(),
                'start_time': not_ready_object.not_ready_starts_at.astimezone(tz).strftime('%I:%M %p'),
                'end_time': not_ready_object.not_ready_ends_at.astimezone(tz).strftime('%I:%M %p') 
            }

            agent_not_ready_report.append(not_ready_report)

        response["agent_not_ready_report"] = agent_not_ready_report

        status = 200
        message = 'Success'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_agent_not_ready_report_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message 


def get_missed_chats_external(livechat_user, filter_params):
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        response = {}
        status = 500
        message = 'Internal Server Error'

        datetime_start, datetime_end, error_message = get_start_and_end_time(filter_params)
        if error_message:
            return response, 400, error_message

        channel_objs, category_objs = get_channel_and_category_objs(livechat_user, filter_params, True)

        customer_objs = LiveChatCustomer.objects.filter(bot__in=livechat_user.bots.all(
        ), is_denied=True, is_system_denied=False, request_raised_date__range=[datetime_start, datetime_end], channel__in=channel_objs, category__in=category_objs).order_by('-joined_date')

        missed_chats_report_list = []
        for customer_obj in customer_objs:
            missed_chats_report = {
                'customer_name': customer_obj.name(),
                'email': customer_obj.email,
                'phone_number': customer_obj.phone,
                'message': customer_obj.message,
                'channel': customer_obj.channel.name,
                'category': customer_obj.category.title,
                'created': customer_obj.joined_date.astimezone(tz).strftime(DATE_DD_MMM_YYYY_TIME_HH_MIN_P)
            }

            missed_chats_report_list.append(missed_chats_report)

        response["missed_chats_report"] = missed_chats_report_list

        status = 200
        message = 'Success'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_missed_chats_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message          


def get_offline_chats_external(livechat_user, filter_params):
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        response = {}
        status = 500
        message = 'Internal Server Error'

        datetime_start, datetime_end, error_message = get_start_and_end_time(filter_params)
        if error_message:
            return response, 400, error_message

        channel_objs, category_objs = get_channel_and_category_objs(livechat_user, filter_params, True)

        customer_objs = LiveChatCustomer.objects.filter(bot__in=livechat_user.bots.all(
        ), is_system_denied=True, request_raised_date__range=[datetime_start, datetime_end], channel__in=channel_objs, category__in=category_objs).order_by('-joined_date')
        
        offline_chats_report_list = []
        for customer_obj in customer_objs:
            offline_chats_report = {
                'customer_name': customer_obj.name(),
                'email': customer_obj.email,
                'phone_number': customer_obj.phone,
                'message': customer_obj.message,
                'channel': customer_obj.channel.name,
                'category': customer_obj.category.title,
                'created': customer_obj.joined_date.astimezone(tz).strftime(DATE_DD_MMM_YYYY_TIME_HH_MIN_P)
            }

            offline_chats_report_list.append(offline_chats_report)

        response["offline_chats_report"] = offline_chats_report_list

        status = 200
        message = 'Success'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_offline_chats_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message  


def get_abandoned_chats_external(livechat_user, filter_params):
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        response = {}
        status = 500
        message = 'Internal Server Error'

        datetime_start, datetime_end, error_message = get_start_and_end_time(filter_params)
        if error_message:
            return response, 400, error_message

        channel_objs, category_objs = get_channel_and_category_objs(livechat_user, filter_params, True)

        customer_objs = LiveChatCustomer.objects.filter(bot__in=livechat_user.bots.all(
        ), agent_id=None, abruptly_closed=True, request_raised_date__range=[datetime_start, datetime_end], channel__in=channel_objs, category__in=category_objs).order_by('-joined_date')
        
        abandoned_chats_report_list = []
        for customer_obj in customer_objs:
            abandoned_chats_report = {
                'customer_name': customer_obj.name(),
                'email': customer_obj.email,
                'phone_number': customer_obj.phone,
                'message': customer_obj.message,
                'channel': customer_obj.channel.name,
                'category': customer_obj.category.title,
                'created': customer_obj.joined_date.astimezone(tz).strftime(DATE_DD_MMM_YYYY_TIME_HH_MIN_P),
                'wait_time': customer_obj.get_wait_time(),
            }

            abandoned_chats_report_list.append(abandoned_chats_report)

        response["abandoned_chats_report"] = abandoned_chats_report_list

        status = 200
        message = 'Success'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_abandoned_chats_external: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

    return response, status, message                
