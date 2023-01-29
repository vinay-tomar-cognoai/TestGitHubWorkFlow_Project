import logging
import sys
from datetime import datetime, timedelta
import pytz
from django.conf import settings
from LiveChatApp.constants import *
from LiveChatApp.constants import DATE_DD_MMM_YYYY_TIME_HH_MIN_P
import socket

logger = logging.getLogger(__name__)


def get_chat_history_payload(livechat_user, customer_obj, parent_user, second_user):
    
    data = {}
    from LiveChatApp.models import LiveChatConfig, LiveChatFollowupCustomer
    try:
        config_obj = LiveChatConfig.objects.get(bot=customer_obj.bot)
        is_original_information_in_reports_enabled = config_obj.is_original_information_in_reports_enabled

        data["joined_date"] = (customer_obj.joined_date.astimezone(pytz.timezone(settings.TIME_ZONE))).strftime("%d/%m/%Y")
        if is_original_information_in_reports_enabled and customer_obj.original_username != "" and customer_obj.username != customer_obj.original_username:
            data["customer_name"] = str(customer_obj.username) + "(original - " + str(customer_obj.original_username) + ")"
        else:
            data["customer_name"] = str(customer_obj.username)
            
        if is_original_information_in_reports_enabled and customer_obj.original_phone != "" and customer_obj.phone != customer_obj.original_phone:
            data["phone"] = str(customer_obj.phone) + "(original - " + str(customer_obj.original_phone) + ")"
        else:
            data["phone"] = str(customer_obj.phone)
        
        if is_original_information_in_reports_enabled and customer_obj.original_email != "" and customer_obj.email != customer_obj.original_email:
            data["email"] = str(customer_obj.email) + "(original - " + str(customer_obj.original_email) + ")"
        else:
            data["email"] = str(customer_obj.email)
            
        if customer_obj.rate_value == -1:
            data["rate_value"] = "NA"
        else:
            data["rate_value"] = str(customer_obj.rate_value)
        
        if customer_obj.nps_text_feedback == "":
            data['chat_nps_comment'] = 'NA'
        else:
            data['chat_nps_comment'] = str(customer_obj.nps_text_feedback)
            
        start_time = (customer_obj.joined_date + timedelta(hours=5, minutes=30)).strftime(
            "%d/%m/%Y, %I:%M:%p")
        data["start_time"] = start_time
        
        end_time = (customer_obj.last_appearance_date + timedelta(hours=5, minutes=30)).strftime(
            "%d/%m/%Y, %I:%M:%p")
        if customer_obj.followup_assignment:
            livechat_followup_cust_obj = LiveChatFollowupCustomer.objects.get(
                livechat_customer=customer_obj)
            end_time = (livechat_followup_cust_obj.completed_date + timedelta(hours=5, minutes=30)).strftime(
                "%d/%m/%Y, %I:%M:%p")
        data["end_time"] = end_time
        
        data["chat_duration"] = customer_obj.get_chat_duration()
        
        try:
            data["closing_category"] = customer_obj.category.title
        except Exception:
            data["closing_category"] = 'None'
        
        try:
            data["agent_name"] = customer_obj.get_agent_name()
            data["agent_username"] = customer_obj.get_agent_username()
        except Exception:
            data["agent_name"] = 'None'
            data["agent_username"] = 'None'
            
        channel_name = customer_obj.channel.name
        if customer_obj.followup_assignment:
            channel_name = customer_obj.channel.name + ' (Follow Up)'
        
        data["channel_name"] = str(channel_name)
        data["session_id"] = str(customer_obj.session_id)
        data["wait_time"] = str(customer_obj.get_wait_time())
        data["chat_ended_by"] = str(customer_obj.chat_ended_by)
        data['cobrowsing_nps_rating'], data['cobrowsing_nps_comment'] = customer_obj.get_cobrowsing_nps_data()
        data["first_time_response"] = str(customer_obj.get_agent_first_time_response_time())
        data["date"] = str(customer_obj.request_raised_date)
        data["parent_user"] = str(parent_user)
        data["second_user"] = str(second_user)            
        data["type"] = "ChatHistoryReport"
        
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        data["ip_address"] = str(ip_address)
        
        # data["username"] = str(livechat_user.user.username)
        # data["joined_date"] = customer_obj.joined_date.strftime("%d/%m/%Y")
        # data["customer_name"] = str(customer_obj.username)
        # data["phone"] = str(customer_obj.phone)
        # data["email"] = str(customer_obj.email)
        # data["rate_value"] = customer_obj.rate_value
        # if customer_obj.rate_value == -1:
        #     data["rate_value"] = "NA"
        # data["start_time"] = (customer_obj.joined_date + timedelta(hours=5, minutes=30)).strftime("%d/%m/%Y, %I:%M:%p")
        # data["end_time"] = (customer_obj.last_appearance_date + timedelta(hours=5, minutes=30)).strftime("%d/%m/%Y, %I:%M:%p")
        # data["chat_duration"] = customer_obj.get_chat_duration()
        # data["closing_category"] = "None"
        # if customer_obj.closing_category:
        #     data["closing_category"] = customer_obj.closing_category.title

        # data["agent_name"] = customer_obj.get_agent_name()
        # data["agent_username"] = customer_obj.get_agent_username()
        # data["channel_name"] = customer_obj.channel.name
        # data["session_id"] = str(customer_obj.session_id)
        # data["wait_time"] = str(customer_obj.get_wait_time())
        # data["chat_ended_by"] = str(customer_obj.chat_ended_by)
        # data["parent_user"] = str(parent_user)
        # data["second_user"] = str(second_user)
        
        return data
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_chat_history_payload! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'LiveChat'})
        return data
    

def get_chat_history_nps_payload(livechat_user, customer_obj, parent_user, second_user):
    
    data = {}
    
    try:     
        if customer_obj.rate_value == -1:
            data["rate_value"] = "NA"
        else:
            data["rate_value"] = str(customer_obj.rate_value)
        
        if customer_obj.nps_text_feedback == "":
            data['chat_nps_comment'] = 'NA'
        else:
            data['chat_nps_comment'] = str(customer_obj.nps_text_feedback)
        
        data["date"] = str(customer_obj.request_raised_date)
        data["session_id"] = str(customer_obj.session_id)
        data["parent_user"] = str(parent_user)
        data["second_user"] = str(second_user)            
        data["type"] = "ChatHistoryNPSUpdate"
        
        return data
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_chat_history_payload! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'LiveChat'})
        return data
    

def get_agent_login_logout_payload(livechat_session_management, parent_user, second_user, update):
    
    data = {}
    
    try:     
        data["agent_username"] = str(livechat_session_management.user.user.username)
        data["date"] = str(livechat_session_management.session_starts_at.date().strftime(DATE_DD_MM_YYYY))
        data["duration"] = str(livechat_session_management.get_session_duration())
        data["agent_name"] = str(livechat_session_management.get_name())
        data["login_time"] = str((livechat_session_management.session_starts_at.astimezone(pytz.timezone(settings.TIME_ZONE))).strftime("%H:%M:%S"))
        data["logout_time"] = str((livechat_session_management.session_ends_at.astimezone(pytz.timezone(settings.TIME_ZONE))).strftime("%H:%M:%S"))
        data["total_offline_time"] = str(livechat_session_management.get_total_offline_time())
        data["total_online_time"] = str(livechat_session_management.get_total_online_time())
        data["not_ready_duration"] = str(livechat_session_management.get_session_stop_interaction_duration())
        data["parent_user"] = str(parent_user)
        data["second_user"] = str(second_user)
        
        if not update:
            data["type"] = "AgentLoginLogout"
        else:
            data["type"] = "AgentLoginLogoutUpdate"
        return data
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_agent_login_logout_payload! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'LiveChat'})
        return data


def get_agent_performance_report_payload(livechat_session_management, parent_user, second_user, update):

    data = {}

    try:
        data["agent_username"] = livechat_session_management.get_name().strip()
        data["session_starts_at"] = str((livechat_session_management.session_starts_at.astimezone(
            pytz.timezone(settings.TIME_ZONE))).strftime("%d/%m/%Y, %I:%M:%p"))

        if livechat_session_management.session_completed:
            data["session_ends_at"] = str((livechat_session_management.session_ends_at.astimezone(
                pytz.timezone(settings.TIME_ZONE))).strftime("%d/%m/%Y, %I:%M:%p"))
        else:
            data["session_ends_at"] = '-'

        data["session_duratio"] = livechat_session_management.get_session_duration()
        data["average_handle_time"] = livechat_session_management.get_average_handle_time()
        data["average_first_time_response_time"] = livechat_session_management.get_average_first_time_response_time()
        data["no_response_count"] = livechat_session_management.get_no_response_count()
        data["idle_duration"] = livechat_session_management.get_idle_duration()
        data["not_ready_count"] = livechat_session_management.get_not_ready_count()
        data["not_ready_duration"] = livechat_session_management.get_session_stop_interaction_duration()
        data["interaction_count"] = livechat_session_management.get_interaction_count()
        data["interaction_duration"] = livechat_session_management.get_interaction_duration()
        data["self_assigned_chat"] = livechat_session_management.get_self_assigned_chat()
        data["total_transferred_chat_received"] = livechat_session_management.get_total_transferred_chat_received()
        data["total_transferred_chat_made"] = livechat_session_management.get_total_transferred_chat_made()
        data["total_group_chat_request"] = livechat_session_management.get_total_group_chat_request()
        data["total_group_chat_accept"] = livechat_session_management.get_total_group_chat_accept()
        data["total_group_chat_reject"] = livechat_session_management.get_total_group_chat_reject()
        data["total_group_chat_no_response"] = livechat_session_management.get_total_group_chat_no_response()
        data["total_group_chat_duration"] = livechat_session_management.get_total_group_chat_duration()
        data["average_nps"] = livechat_session_management.get_average_nps()

        data["parent_user"] = str(parent_user)
        data["second_user"] = str(second_user)

        if update:
            data["type"] = "AgentPerfomanceUpdate"
        else:
            data["type"] = "AgentPerfomance"

        return data

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_agent_performance_report_payload! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'LiveChat'})
        return data
    

def get_agent_not_ready_payload(agent_not_ready_obj, parent_user, second_user, update):
    
    data = {}
    
    try:
        data["date"] = str(agent_not_ready_obj.not_ready_starts_at.date().strftime(DATE_DD_MM_YYYY))     
        data["agent_name"] = str(str(agent_not_ready_obj.user.user.first_name) + " " + str(agent_not_ready_obj.user.user.last_name))
        data["agent_username"] = str(agent_not_ready_obj.user.user.username)
        data["reason"] = str(agent_not_ready_obj.get_reason_for_offline())
        data["stop_interaction_duration"] = str(agent_not_ready_obj.get_stop_interaction_duration())
        data["start_time"] = str((agent_not_ready_obj.not_ready_starts_at.astimezone(pytz.timezone(settings.TIME_ZONE))).strftime("%H:%M:%S"))
        data["end_time"] = str((agent_not_ready_obj.not_ready_ends_at.astimezone(pytz.timezone(settings.TIME_ZONE))).strftime("%H:%M:%S"))
        data["total_offline_time"] = str(agent_not_ready_obj.get_offline_duration())
        data["parent_user"] = str(parent_user)
        data["second_user"] = str(second_user)
        
        if not update:
            data["type"] = "AgentNotReady"
        else:
            data["type"] = "AgentNotReadyUpdate"
        
        return data
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_agent_login_logout_payload! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'LiveChat'})
        return data
    

def get_video_call_history_payload(meeting_obj, parent_user, second_user):
    
    data = {}
    tz = pytz.timezone(settings.TIME_ZONE)
    try:
        data["customer_name"] = str(meeting_obj.customer.get_username())
        data["agent_username"] = str(meeting_obj.agent.user.username)
        data["start_datetime"] = str(meeting_obj.start_datetime.astimezone(tz).strftime('%d-%b-%Y, %I:%M %p'))
        data["end_datetime"] = str(meeting_obj.end_datetime.astimezone(tz).strftime('%d-%b-%Y, %I:%M %p'))
        data["total_duration"] = str(meeting_obj.get_call_duration())
        data["meeting_status"] = "Completed"
        data["parent_user"] = str(parent_user)
        data["second_user"] = str(second_user)
        data["type"] = "VideoCallHistory"
        return data
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_video_call_history_payload! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'LiveChat'})
        return data
    
    
def get_voice_call_history_payload(meeting_obj, parent_user, second_user):
    
    data = {}
    time_zone = pytz.timezone(settings.TIME_ZONE)
    try:
        data["customer_name"] = str(meeting_obj.customer.get_username())
        data["agent_username"] = str(meeting_obj.agent.user.username)
        data["start_datetime"] = str(meeting_obj.start_datetime.astimezone(time_zone).strftime('%d-%b-%Y, %I:%M %p'))
        data["end_datetime"] = str(meeting_obj.end_datetime.astimezone(time_zone).strftime('%d-%b-%Y, %I:%M %p'))
        data["total_duration"] = str(meeting_obj.get_call_duration())
        data["meeting_status"] = "Completed"
        data["parent_user"] = str(parent_user)
        data["second_user"] = str(second_user)
        data["type"] = "VoiceCallHistory"
        return data
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_voice_call_history_payload! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'LiveChat'})
        return data
    

def get_abandoned_chat_payload(customer_obj, list_of_user):
    
    data = {}
    
    try:
        data["created_on"] = str((customer_obj.joined_date.astimezone(pytz.timezone(settings.TIME_ZONE))).strftime("%d/%m/%Y, %I:%M %p"))
        data["customer_name"] = str(customer_obj.username)
        data["mobile_number"] = str(customer_obj.phone)
        data["email"] = str(customer_obj.email)
        data["message"] = str(customer_obj.message)
        data["channel"] = str(customer_obj.channel.name)
        
        if customer_obj.category.title:
            data["category"] = str(customer_obj.category.title)
        else:
            data["category"] = "None"
        data["wait_time"] = str(customer_obj.get_wait_time())
        data["parent_users"] = list_of_user
        data["type"] = "AgentAbandonedChat"
        
        return data
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_abandoned_chat_payload! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'LiveChat'})
        return data


def get_cobrowsing_history_payload(cobrowse_obj, parent_user, second_user):

    data = {}
    time_zone = pytz.timezone(settings.TIME_ZONE)
    try:
        data["customer_name"] = str(cobrowse_obj.customer.get_username())
        data["agent_username"] = str(cobrowse_obj.agent.user.username)
        data["start_datetime"] = str((cobrowse_obj.start_datetime.astimezone(
            time_zone).strftime(DATE_DD_MMM_YYYY_TIME_HH_MIN_P)))
        data["end_datetime"] = str((cobrowse_obj.end_datetime.astimezone(
            time_zone).strftime(DATE_DD_MMM_YYYY_TIME_HH_MIN_P)))
        data["total_duration"] = str(cobrowse_obj.get_duration())
        data["meeting_status"] = "Completed"

        data["parent_user"] = str(parent_user)
        data["second_user"] = str(second_user)
        data["type"] = "CobrowsingHistory"
        return data

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_cobrowsing_history_payload! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'LiveChat'})
        return data


def get_offline_chat_payload(customer_obj, list_of_user):

    data = {}

    try:
        data["created_on"] = str((customer_obj.joined_date.astimezone(pytz.timezone(settings.TIME_ZONE))).strftime("%d/%m/%Y %I:%M %p"))
        data["customer_name"] = str(customer_obj.username)
        data["mobile_number"] = str(customer_obj.phone)
        data["email"] = str(customer_obj.email)
        data["message"] = str(customer_obj.message)
        data["channel"] = str(customer_obj.channel.name)

        if customer_obj.category.title:
            data["category"] = str(customer_obj.category.title)
        else:
            data["category"] = "None"
        data["parent_users"] = list_of_user
        data["type"] = "AgentOfflineChat"

        return data

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_offline_chat_payload! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'LiveChat'})
        return data


def get_missed_chat_payload(customer_obj, list_of_user):

    data = {}

    try:
        data["created_on"] = str((customer_obj.joined_date.astimezone(pytz.timezone(settings.TIME_ZONE))).strftime("%d/%m/%Y %I:%M %p"))
        data["customer_name"] = str(customer_obj.username)
        data["mobile_number"] = str(customer_obj.phone)
        data["email"] = str(customer_obj.email)
        data["message"] = str(customer_obj.message)
        data["channel"] = str(customer_obj.channel.name)

        if customer_obj.category.title:
            data["category"] = str(customer_obj.category.title)
        else:
            data["category"] = "None"
        data["parent_users"] = list_of_user
        data["type"] = "AgentMissedChat"

        return data

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_missed_chat_payload! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'LiveChat'})
        return data
