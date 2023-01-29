import datetime
from EasyAssistApp.constants_mailer_analytics import *

CLIENT_DISCONNECTED_TIME_OUT = 600  # 10 min client disconnected timeout

AGENT_DISCONNECTED_TIME_OUT = 600  # 10 min agent disconnected timeout

ARCHIVE_COBROWSE_IO_TIME = 3600  # 1 hour archive cobrowse io request

COBROWSE_TOAST_TIMEOUT = 3000

NO_DETAILS = "No details"

CUSTOMER_NAME = "Customer Name"

SECURED_FILES_PATH = "secured_files/"

ASIA_KOLKATA = 'Asia/Kolkata'

INVALID_ACCESS_CONSTANT = "Invalid Access"

REDIRECT_LOGIN_PATH = "/chat/login"

INTERNAL_SERVER_ERROR_MSG = "Internal Server Error"

INTERNAL_SERVER_ERROR_MSG_2 = "internal server error"

APPLICATION_JSON_CONTENT_TYPE = "application/json"

NO_MATCHING_SESSION_FOUND_MSG = "No matching session found"

NO_CONTENT_MSG = "No Content"

INVALID_ACCESS_TOKEN_MSG = "Invalid Access Token"

EASYASSISTAPP_SECURED_FILES_PATH = "secured_files/EasyAssistApp/"

EASYASSISTAPP_CHROME_EXTENSION_FILES_PATH = "secured_files/EasyAssistApp/chrome_extension/"

EASYASSISTAPP_DOWNLOAD_FILES_PATH = "easy-assist/download-file/"

EASYASSISTAPP_COGNOVID_FILES_PATH = "secured_files/EasyAssistApp/cognovid"

NOT_PROVIDED = "Not provided"

INVALID_MOBILE_NUMBER = "Invalid Mobile Number"

REQUEST_ATTENDED = "Request Attended"

CUSTOMERS_CONVERTED_BY_AGENT = "Customers Converted By Agent"

CUSTOMERS_CONVERTED_THROUGH_URL = "Customers Converted through URL"

AVERAGE_SESSION_TIME = "Average Session Time"

AVERAGE_WAITING_TIME_FOR_ATTENDED_LEADS = "Average Waiting Time for Attended Leads"

AVERAGE_WAITING_TIME_FOR_UNATTENDED_LEADS = "Average Waiting Time for Unattended Leads"

CRM_DOCUMENTS_PATH = "secured_files/EasyAssistApp/crm-documents/"

DOWNLOAD_FILE_PATH = "easy-assist/download-file/"

TIME_FORMAT = "%d %b %Y %I:%M %p"

ZERO_SEC = "0 sec"

DATE_TIME_FORMAT = "%Y-%m-%d"

DATE_TIME_FORMAT_2 = "%d-%m-%Y %I:%M %p"

DATE_TIME_FORMAT_3 = "%b. %d, %Y"

DATE_TIME_FORMAT_4 = "%I:%M %p"

DATE_TIME_FORMAT_5 = "%d %b, %Y"

DATE_TIME_FORMAT_6 = "%d-%m-%Y"

DATE_TIME_FORMAT_7 = "%d/%m/%Y %H:%M:%S"

CUSTOMER_MOBILE_NUMBER = "Customer Mobile Number"

AGENT_REMARKS = "Agent Remarks"

COBROWSING_REQUEST_DATETIME = "Cobrowsing Request Date & Time"

DELETED_PROFILE = "Deleted Profile"

COBROWSING_ACCESS_TOKEN = "cobrowsing access token"

DATE_WHEN_ANALYTICS_IS_SAVED = "date when analytics is saved"

UNIQUE_ACCESS_TOKEN_KEY = "unique access token key"

ADMIN_RESPONSIBLE_FOR_THE_SAME = "admin responsible for the same"

TOTAL_COBROWSING_SESSION_DURATION = "Total cobrowsing session duration (sec)"

USER_CHOICES = (("agent", "agent"), ("supervisor",
                                     "supervisor"), ("admin", "admin"), ("admin_ally", "admin_ally"))

TRANSFERRED_LEAD_STATUS = (("accepted", "accepted"),
                           ("rejected", "rejected"), ("expired", "expired"))

COBROWSE_REQUEST_TYPE = (("invited", "invited"),
                         ("transferred", "transferred"))

CHAT_TYPE = (
    ("chat_message", "chat_message"),
    ("chat_bubble", "chat_bubble")
)

FORM_INPUT_CHOICES = (
    ("text", "text"),
    ("number", "number"),
    ("checkbox", "checkbox"),
    ("radio", "radio"),
    ("dropdown", "dropdown")
)

CRM_API_TYPES = (
    ("inbound", "inbound"),
    ("lead_search", "lead_search"),
    ("drop_link", "drop_link"),
)

STATIC_FILE_ACTION_CHOICES = (
    ("nochange", "nochange"),
    ("reset", "reset"),
    ("update", "update"),
)

month_to_num_dict = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

COBROWSING_DAYS = [{
    "day": "sunday",
    "index": 0,
}, {
    "day": "monday",
    "index": 1,
}, {
    "day": "tuesday",
    "index": 2,
}, {
    "day": "wednesday",
    "index": 3,
}, {
    "day": "thursday",
    "index": 4,
}, {
    "day": "friday",
    "index": 5,
}, {
    "day": "saturday",
    "index": 6,
}]

COBOWSE_AGENT_WORKING_DAYS = [1, 2, 3, 4, 5]   # 0 => Sunday

FLOATING_BUTTON_POSITION = (("left", "left"), ("right", "right"), ("top", "top"), ("bottom", "bottom"))

HEADING_FONT_STYLE = "font: bold on"

ALIGNMENT_STYLE = "align: vert top"

ACTIVE_STATUS_STYLE = "borders: top_color gray25, bottom_color gray25, right_color gray25, left_color gray25,\
                   left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour light_green"
INACTIVE_STATUS_STYLE = "borders: top_color gray25, bottom_color gray25, right_color gray25, left_color gray25,\
                   left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour rose"

# below constants used in add_live_chat_history_data_into_workbook() for identification whom is sender
AGENT_STYLE = "borders: top_color gray25, bottom_color gray25, right_color gray25, left_color gray25,\
                   left thin, right thin, top thin, bottom thin; align: wrap on, vert top; pattern: pattern solid, fore_colour ivory"
INVITED_AGENT_STYLE = "borders: top_color gray25, bottom_color gray25, right_color gray25, left_color gray25,\
                   left thin, right thin, top thin, bottom thin; align: wrap on,vert top; pattern: pattern solid, fore_colour ice_blue"
CUSTOMER_STYLE = "borders: top_color gray25, bottom_color gray25, right_color gray25, left_color gray25,\
                   left thin, right thin, top thin, bottom thin; align: wrap on, vert top; pattern: pattern solid, fore_colour light_green"

COBROWSING_LOGIN_ACTION = "1"
COBROWSING_LOGOUT_ACTION = "2"
COBROWSING_ADDUSER_ACTION = "3"
COBROWSING_DELETEUSER_ACTION = "4"
COBROWSING_CHANGESETTINGS_ACTION = "5"
COBROWSING_CHANGEAPPCONFIG_ACTION = "6"
COBROWSING_UPDATEUSER_ACTION = "7"
COBROWSING_DOCUMENTUPLOAD_ACTION = "8"
COBROWSING_DOCUMENTDELETE_ACTION = "9"
COBROWSING_ACTIVATEUSER_ACTION = "10"
COBROWSING_DEACTIVATEUSER_ACTION = "11"
COBROWSING_PASSWORD_RESENT_ACTION = "12"
ENABLE_EMAIL_ANALYTICS_ACTION = "13"
DISABLE_EMAIL_ANALYTICS_ACTION = "14"
CREATE_EMAIL_ANALYTICS_PROFILE_ACTION = "15"
UPDATE_EMAIL_ANALYTICS_PROFILE_ACTION = "16"
DELETE_EMAIL_ANALYTICS_PROFILE_ACTION = "17"

COBROWSING_ACTION_LIST = ((COBROWSING_LOGIN_ACTION, "Login"),
                          (COBROWSING_LOGOUT_ACTION, "Logout"),
                          (COBROWSING_ADDUSER_ACTION, "Add-User"),
                          (COBROWSING_DELETEUSER_ACTION, "Delete-User"),
                          (COBROWSING_CHANGESETTINGS_ACTION, "Change-Settings"),
                          (COBROWSING_CHANGEAPPCONFIG_ACTION, "Change-App-Config"),
                          (COBROWSING_UPDATEUSER_ACTION, "Updated-User"),
                          (COBROWSING_DOCUMENTUPLOAD_ACTION, "Upload-Document"),
                          (COBROWSING_DOCUMENTDELETE_ACTION, "Delete-Document"),
                          (COBROWSING_ACTIVATEUSER_ACTION, "Activate-User"),
                          (COBROWSING_DEACTIVATEUSER_ACTION, "Deactivate-User"),
                          (COBROWSING_PASSWORD_RESENT_ACTION, "Password-Resent"),
                          (ENABLE_EMAIL_ANALYTICS_ACTION, "EnableEmailAnalyticsSettings"),
                          (DISABLE_EMAIL_ANALYTICS_ACTION, "DisableEmailAnalyticsSettings"),
                          (CREATE_EMAIL_ANALYTICS_PROFILE_ACTION, "CreateEmailAnalyticsProfile"),
                          (UPDATE_EMAIL_ANALYTICS_PROFILE_ACTION, "UpdateEmailAnalyticsProfile"),
                          (DELETE_EMAIL_ANALYTICS_PROFILE_ACTION, "DeleteEmailAnalyticsProfile"))


SESSION_ARCHIVED_CAUSE = (("AGENT_ENDED", "AGENT_ENDED"),
                          ("CLIENT_ENDED", "CLIENT_ENDED"),
                          ("AGENT_INACTIVITY", "AGENT_INACTIVITY"),
                          ("CLIENT_INACTIVITY", "CLIENT_INACTIVITY"),
                          ("UNASSIGNED", "UNASSIGNED"),
                          ("UNATTENDED", "UNATTENDED"),
                          ("FOLLOWUP", "FOLLOWUP"))

COBROWSING_TYPE_LIST = (("modified-inbound", "Modified Inbound"), ("outbound-proxy-cobrowsing", "Outbound Proxy"))

COBROWSING_ACTION_DICT = {}

for action_key, action_value in COBROWSING_ACTION_LIST:
    COBROWSING_ACTION_DICT[action_key] = action_value

COBROWSING_REVERSE_ACTION_DICT = {}

for action_key, action_value in COBROWSING_ACTION_LIST:
    COBROWSING_REVERSE_ACTION_DICT[action_value] = action_key


COBROWSING_AGENT_SUPPORT = (("L1", "L1"), ("L2", "L2"), ("L3", "L3"))

COBROWSING_AGENT_SUPPORT_DICT = {}

for support_key, support_value in COBROWSING_AGENT_SUPPORT:
    COBROWSING_AGENT_SUPPORT_DICT[support_key] = support_value

COBROWSING_HTML_FIELD_TAG = (
    ("input", "input"), ("textarea", "textarea"), ("select", "select"))

COBROWSING_HTML_FIELD_TYPE = (
    ("primary", "primary"), ("secondary", "secondary"))


DEFAULT_APP_COBROWSING_CUSTOMER_SHARE_MESSAGE = "Dear Customer,\n\nPlease click on the link below to virtually connect with our sales representative:\n\n{/customer_link/}\n\nBy clicking on the link above, you are giving consent to connect with our sales representative"

DEFAULT_APP_COBROWSING_EXPERT_SHARE_MESSAGE = "Dear Expert,\n\nPlease click on the link below to virtually connect with our sales representative:\n\n{/expert_link/}"

REPORT_TYPE_CHOICES = (
    ("support-history", "support-history"),
    ("unattended-lead-history", "unattended-lead-history"),
    ("meeting-support-history", "meeting-support-history"),
    ("declined-lead-history", "declined-lead-history"),
    ("followup-lead-history", "followup-lead-history"),
    ("screen-recording-history", "screen-recording-history"),
    ("audit-trail", "audit-trail"),
    ("agent-audit-trail", "agent-audit-trail"),
    ("agent-online-audit-trail", "agent-online-audit-trail"),
    ("inbound-analytics", "inbound-analytics"),
    ("outbound-analytics", "outbound-analytics"),
    ("outbound-proxy-analytics", "outbound-proxy-analytics"),
    ("reverse-analytics", "reverse-analytics"),
    ("general-analytics", "general-analytics"),
    ("manually-converted-leads", "manually-converted-leads"),
    ("inbound-unique-customers", "inbound-unique-customers"),
    ("inbound-repeated-customers", "inbound-repeated-customers"),
    ("outbound-unique-customers", "outbound-unique-customers"),
    ("outbound-repeated-customers", "outbound-repeated-customers"),
    ("reverse-unique-customers", "reverse-unique-customers"),
    ("reverse-repeated-customers", "reverse-repeated-customers"),
    ("outbound-captured-leads", "outbound-captured-leads"),
    ("live-chat-history", "live-chat-history"),
    ("canned-response", "canned-response"),
    ("droplink-urls-generated", "droplink-urls-generated"),
)


MESSAGE_ON_CHOOSE_PRODUCT_CATEGORY_MODAL = "Hi! Our experts would like to help you in buying a new policy. Please select the policy you would like to buy below or click 'Others'"

AGENT_CONNECT_MESSAGE = "Hello, thank you for choosing Cogno Cobrowsing Support!  We are glad to welcome you to Cogno Cobrowsing Bank family. My Name  is agent_name. I will  be assisting you."

MASKED_FIELD_WARNING_TEXT = "This field is not visible to agent"

VOIP_CALLING_MESSAGE = "Would you like to connect on a voice call?"

VOIP_WITH_VIDEO_CALLING_MESSAGE = "Would you like to connect on a video call?"

RESEND_PASSWORD_THRESHOLD = 5

NON_WORKING_HOURS_MESSAGE = "Thanks for contacting us. All our agents are currently offline. Please try again during working hours."

AGENT_UNAVAILABLE_MESSAGE = "Thanks for contacting us. All our agents are currently busy. Please try after some time."

CONNECT_MESSAGE = "Please provide your contact details for our experts to assist you"

ASSIST_MESSAGE = """We would like to assist you in filling out your form. By clicking on "Allow" our customer service agent will be able to see your screen and assist you. Please don't worry, your personal data is safe and will not be visible to our agent."""

NO_AGENT_CONNECTS_TOAST_TEXT = "Currently, all our experts are busy. We apologize for the same. We have noted your contact details and will connect with you soon"

NO_AGENT_CONNECTS_TOAST_RESET_MESSAGE = "Sorry our agents are currently busy but we have noted your details and will contact you shortly"

NO_AGENT_CONNECTS_TOAST_TEXT_MEETING = "Thank you for your patience, the meeting host will let you in soon."

DEFAULT_PASSWORD_PREFIX = "CognoAI"

DEFAULT_DROP_LINK_EXPIRY_TIME = 30

AUTO_ASSIGN_UNATTENDED_LEAD_MESSAGE = "We have transferred your request to next available agent. Please wait while the agent is connecting."

AUTO_ASSIGN_LEAD_END_SESSION_MESSAGE = "Currently all agents are busy. We have captured your details and our agent will connect with you."

EASYASSIST_MAX_API_RUNTIME_LIMIT = 5  # in seconds

UNASSIGNED_LEAD_DEFAULT_MESSAGE = "Sorry, all our agents are currently offline. We have noted your details and shall get back to you whenever an agent is available."

STATIC_FILE_TOKEN_WISE_LIST = [
    "css/agent.css",
    "css/cobrowseio.css",
    "css/cobrowse.reverse.css",
    "css/client.reverse.css",
    "css/easyassist_custom_select2.css",
    "css/cognoai_extension.css",
    "css/cogno_meet.css",
    "js/screencapture.js",
    "js/screencapture.min.js",
    "js/app.socket.js",
    "js/app.socket.min.js",
    "js/agent.socket.js",
    "js/screencapture_optimized.js",
    "js/screencapture_optimized.min.js",
    "js/app.socket_optimized.js",
    "js/app.socket_optimized.min.js",
    "js/agent.socket_optimized.js",
    "js/screencapture.reverse.js",
    "js/screencapture.reverse.min.js",
    "js/app.socket.reverse.js",
    "js/app.socket.reverse.min.js",
    "js/client.reverse.socket.js",
    "js/easyassist_custom_select2.js",
    "js/screencapture.reverse.optimized.js",
    "js/screencapture.reverse.optimized.min.js",
    "js/app.socket.reverse.optimized.js",
    "js/app.socket.reverse.optimized.min.js",
    "js/client.reverse.socket.optimized.js",
    "js/video_meeting.js",
    "js/agent_cobrowse_video_meeting.js",
    "js/client_cobrowse_video_meeting.js",
    "js/agent_voip_call.js",
    "js/client_voip_call.js",
    "js/easyassist_tree_mirror.js",
    "js/easyassist_tree_mirror.min.js",
    "js/easyassist_client_iframe.js",
    "js/easyassist_client_iframe.min.js",
    "js/cogno_meet_end.js",
    "js/cognoai_extension.js",
    "js/cognoai_login_extension.js",
    "img/Agent_cursor.svg",
    "img/Client_cursor.svg",
]

ASSIGN_TAKS_PROCESSOR_CODE = """import sys
import logging
import operator

from EasyChatApp.models import User
from EasyAssistApp.models import *
from EasyAssistApp.utils import *
from EasyAssistApp.utils_client_server_signal import *
from datetime import datetime, timedelta
from DeveloperConsoleApp.utils import get_developer_console_cobrowsing_settings, get_developer_console_cognomeet_settings

def assign_cobrowse_obj_to_agent(cobrowse_access_token_obj):

    def check_agent_available(agent_obj, active_agents):
        for agent in active_agents:
            if agent.user.username == agent_obj.user.username:
                return True
        return False
    
    cobrowse_agent_admin = cobrowse_access_token_obj.agent
    allowed_agent_support_levels = ["L1"]

    cobrowse_io_objs = CobrowseIO.objects.filter(
        access_token=cobrowse_access_token_obj, agent=None, is_lead=False, is_archived=False).order_by('request_datetime')
    for cobrowse_io_obj in cobrowse_io_objs.iterator():

        selected_agent = None
        allow_video_meeting_only = cobrowse_io_obj.access_token.allow_video_meeting_only

        active_agents = get_list_agents_under_admin(
            cobrowse_agent_admin, is_active=True)

        active_agents = filter_free_active_agent(
            active_agents, cobrowse_io_obj, for_meeting=allow_video_meeting_only, support_levels=allowed_agent_support_levels)

        if cobrowse_access_token_obj.enable_smart_agent_assignment == True:
            client_mobile_no = cobrowse_io_obj.mobile_number
            diff_time = datetime.now() - timedelta(minutes=cobrowse_access_token_obj.smart_agent_assignment_reconnecting_window)
            filter_cobrowse_io_objs = CobrowseIO.objects.filter(
                access_token=cobrowse_access_token_obj, is_archived=True, is_lead=False,
                mobile_number=get_hashed_data(client_mobile_no), 
                client_session_end_time__gte=diff_time
            ).order_by('-client_session_end_time')
            
            for filter_cobrowse_io_obj in filter_cobrowse_io_objs.iterator():
                filter_cobrowse_io_obj_agent = filter_cobrowse_io_obj.agent
                agent_obj = CobrowseAgent.objects.get(user=filter_cobrowse_io_obj_agent)
                if check_agent_available(agent_obj, active_agents):
                    selected_agent = agent_obj
                    break
        
        if selected_agent == None:

            if len(active_agents) == 0:
                logger.info("Active Agents are not available",
                            extra={'AppName': 'EasyAssist'})
                continue

            agent_dict = {}
            for agent in active_agents:
                agent_dict[agent.user.username] = []
                agent_dict[agent.user.username].append(0)
                if agent.last_lead_assigned_datetime != None:
                    agent_dict[agent.user.username].append(
                        datetime.timestamp(agent.last_lead_assigned_datetime))
                else:
                    agent_dict[agent.user.username].append(0)

            if not agent_dict:
                logger.info("Active Agents are not available",
                            extra={'AppName': 'EasyAssist'})
                continue

            waiting_cobrowse_io_objs = CobrowseIO.objects.filter(
                agent__in=active_agents, is_archived=False)

            for cobrowse_io in waiting_cobrowse_io_objs.iterator():
                if cobrowse_io.is_active_timer() == False:
                    continue

                if cobrowse_io.agent.user.username in agent_dict:
                    agent_dict[cobrowse_io.agent.user.username][0] += 1

            agent_min_lead_entry = min(agent_dict.items(),
                                        key=lambda item: (item[1][0], item[1][1]))

            agent_username = agent_min_lead_entry[0]
            agent_active_leads_count = agent_min_lead_entry[1][0]

            logger.info("agent_dict : " + str(agent_dict),
                        extra={'AppName': 'EasyAssist'})
            logger.info("Agent with min lead: " + str(agent_username) + ":" +
                        str(agent_active_leads_count), extra={'AppName': 'EasyAssist'})

            if cobrowse_io_obj.access_token.maximum_active_leads and agent_active_leads_count >= cobrowse_io_obj.access_token.maximum_active_leads_threshold:
                logger.info("All active agents have atleast %s active leads",
                            str(cobrowse_io_obj.access_token.maximum_active_leads_threshold), extra={'AppName': 'EasyAssist'})
                continue

            user = User.objects.get(username=agent_username)
            selected_agent = CobrowseAgent.objects.get(user=user)
        if selected_agent.is_active == False:
            continue

        logger.warning("Active agent selected for next cobrowsing session %s : %s",
                        str(cobrowse_io_obj.session_id), selected_agent.user.username, extra={'AppName': 'EasyAssist'})
        selected_agent.last_lead_assigned_datetime = timezone.now()
        selected_agent.save()

        cobrowse_io_obj.agent = selected_agent
        if cobrowse_access_token_obj.enable_auto_assign_unattended_lead:
            update_unattended_lead_transfer_audit_trail(cobrowse_io_obj, 
                                                        selected_agent, UnattendedLeadTransferAuditTrail)
        cobrowse_io_obj.last_agent_assignment_datetime = timezone.now()
        if allow_video_meeting_only:
            product_name = "Cogno Meet"
            cognomeet_config_obj = get_developer_console_cognomeet_settings()
            if cognomeet_config_obj:
                product_name = cognomeet_config_obj.cognomeet_title_text

            notification_message = "Hi, " + selected_agent.user.username + \
                "! A customer has connected with you on " + product_name + "."
        else:
            product_name = "Cogno Cobrowse"
            cobrowse_config_obj = get_developer_console_cobrowsing_settings()
            if cobrowse_config_obj:
                product_name = cobrowse_config_obj.cobrowsing_title_text

            notification_message = "Hi, " + selected_agent.user.username + \
                "! A customer has connected with you on " + product_name + "."

        NotificationManagement.objects.create(agent=selected_agent,
                                                cobrowse_io=cobrowse_io_obj,
                                                notification_message=notification_message,
                                                product_name=product_name)

        if cobrowse_io_obj.access_token.show_verification_code_modal == False:
            cobrowse_io_obj.allow_agent_cobrowse = "true"
        cobrowse_io_obj.save()

        notification_objs = NotificationManagement.objects.filter(
            show_notification=True, agent=selected_agent)

        response = {}
        notification_list = []

        for notification_obj in notification_objs.iterator():
            notification_list.append({
                "notification_message": notification_obj.notification_message,
                "product_name": notification_obj.product_name
            })
            notification_obj.delete()

        response["status"] = 200
        response["message"] = "success"
        response["notification_list"] = notification_list

        send_data_from_server_to_client(
            "notification", response, selected_agent.user)
"""

# EasyAssistApp standard error codes

'''
    601 : web socket connect error
    606 : recording data save failed
    611 : jitsi initialization error
    612 : jitsi camera error
    613 : jitsi mic error

    631 : reverse initialize api fail - internal server error
    632 : reverse initialize api fail - connection failed
    633 : droplink initialize api fail - internal server error
    634 : droplink initialize api fail - connection failed
    635 : normal initialize api fail - internal server error
    636 : normal initialize api fail - connection 
    637 : non working hour api fail - internal server error
    638 : non working hour api fail - connection failed
'''


CHROME_EXTENSION_MANIFEST_DATA = {
    "manifest_version": 2,
    "name": "CognoAI",
    "short_name": "cognoai",
    "description": "CognoAI Cobrowsing Extension",
    "version": "1.0",

    "permissions": [
        "storage",
        "http://*/",
        "https://*/",
        "tabs"
    ],

    "content_security_policy": "script-src 'self' http://*; object-src 'self'",


    "content_scripts": [{
        "matches": ["<all_urls>"],
        "js": ["cognoai_crm_extension.js"]
    }],
}

CRM_DOCUMENTS = {
    "auth-token": {
        "url_suffix": "auth-token",
        "original_file_name": "Auth_Token_Generation_API.docx",
        "display_file_name": "Auth Token Generation API.docx",
    },
    "inbound-api": {
        "url_suffix": "inbound",
        "original_file_name": "Inbound_API.docx",
        "display_file_name": "Inbound API.docx",
    },
    "search-lead": {
        "url_suffix": "search-lead",
        "original_file_name": "Search_Lead_API.docx",
        "display_file_name": "Search Lead API.docx",
    },
    "droplink": {
        "url_suffix": "droplink",
        "original_file_name": "DropLink_API.docx",
        "display_file_name": "DropLink API.docx",
    },
    "support-history": {
        "url_suffix": "support-history",
        "original_file_name": "Get_Support_History_API.docx",
        "display_file_name": "Get Support History API.docx",
    },
    "chat-history": {
        "url_suffix": "chat-history",
        "original_file_name": "Get_Chat_History_API.docx",
        "display_file_name": "Get Chat History API.docx",
    },
    "generate-auth-token": {
        "url_suffix": "generate-auth-token",
        "original_file_name": "User_Auth_Token_Generation_API.docx",
        "display_file_name": "User Auth Token Generation API.docx",
    },
    "create-meeting": {
        "url_suffix": "create-meeting",
        "original_file_name": "Create_Meeting_API.docx",
        "display_file_name": "Create Meeting API.docx",
    },
    "delete-meeting": {
        "url_suffix": "delete-meeting",
        "original_file_name": "Delete_Meeting_API.docx",
        "display_file_name": "Delete Meeting API.docx",
    },
    "meeting-status": {
        "url_suffix": "meeting-status",
        "original_file_name": "Get_Meeting_Status_API.docx",
        "display_file_name": "Get Meeting Status API.docx",
    },
    "meeting-details": {
        "url_suffix": "meeting-details",
        "original_file_name": "Get_Meeting_Details_API.docx",
        "display_file_name": "Get Meeting Details API.docx",
    },
    "create-user": {
        "url_suffix": "create-user",
        "original_file_name": "Create_User_API.docx",
        "display_file_name": "Create User API.docx",
    },
    "update-user": {
        "url_suffix": "update-user",
        "original_file_name": "Update_User_API.docx",
        "display_file_name": "Update User API.docx",
    },
    "change-user-status": {
        "url_suffix": "change-user-status",
        "original_file_name": "Change_User_Status_API.docx",
        "display_file_name": "Change User Status API.docx",
    },
    "get-user-status": {
        "url_suffix": "get-user-status",
        "original_file_name": "Get_User_Status_API.docx",
        "display_file_name": "Get User Status API.docx",
    },
    "get-all-users-status": {
        "url_suffix": "get-all-users-status",
        "original_file_name": "Get_All_Users_Status_API.docx",
        "display_file_name": "Get All Users Status API.docx",
    },
    "get-list-of-users": {
        "url_suffix": "get-list-of-users",
        "original_file_name": "Get_List_Of_Users_API.docx",
        "display_file_name": "Get List Of Users API.docx",
    },
    "change-user-password": {
        "url_suffix": "change-user-password",
        "original_file_name": "Change_User_Password_API.docx",
        "display_file_name": "Change User Password API.docx",
    },
}

EASYASSIST_EVENT_TYPE = (("1", "Working"), ("2", "Holiday"))

SYSTEM_COMMANDS_LIST = ["os.system", "subprocess", "import threading", "threading.Thread", "ssh"]

ALLOWED_IMAGE_FILE_EXTENTIONS = ["png", "jpg", "jpeg", "jpe", "bmp", "gif", "tiff", "exif", "jfif"]

AGENT_DETAILS_PROCESSOR_CODE = """from EasyAssistApp.utils import *
import sys
import logging
import requests
import json

def foo(agent_unique_identifier):
    json_response = {
        "status_code": 500,
        "response_body": "",
        "error_message": ""
    }
    try:
        # write your code here
        # api_response = {"name": "Agent One", "Agent ID": "EX123"}
        # json_response["status_code"] = 200
        # json_response["response_body"] = json.dumps(api_response)
        return json_response
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_agent_details_api %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        json_response["error_message"] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return json_response
"""

GOOGLE_GEOCODER_KEY = "AIzaSyBAHTtk1lkVvIl1X_i7_1aIK9RCrhqGEpQ"

FILE_ACCESS_MANAGEMENT_EXPIRE_TIME_LIMIT = 24  # In Hours

QUEUE_LEADS_COUNT = 20

ACTIVE_LEADS_COUNT = 20

# these are unique cronjob IDs which are used to make a log of the cronjob when they get executed

EXPORT_SUPPORT_HISTORY_CRONJOB_CONSTANT = "EASYASSIST_CRJ_1"

EXPORT_ANALYTICS_CRONJOB_CONSTANT = "EASYASSIST_CRJ_2"

SCREEN_RECORDING_DELETE_CRONJOB_CONSTANT = "EASYASSIST_CRJ_3"

MAILER_ANALYTICS_CRONJOB_CONSTANT = "EASYASSIST_CRJ_4"

TRANSFER_LOG_EXPIRY_CRONJOB_CONSTANT = "EASYASSIST_CRJ_5"

MASK_CUSTOMER_DETAILS_CRONJOB_CONSTANT = "EASYASSIST_CRJ_6"

EXPORT_CANNED_RESPONSE_CRONJOB_CONSTANT = "EASYASSIST_CRJ_7"

EASYASSIST_SCHEDULAR_ID_CONSTANT = "EASYASSIST_SCHED_1"

CRONJOB_TRACKER_EXPIRY_TIME_LIMIT = 15  # In mins

NO_DATA_AVAILABLE_IMAGE_PATH = "files/EasyAssistApp/img/no_data_available.png"

EXPORTS_UPPER_CAP_LIMIT = 1000

CHARACTERS_NOT_ALLOWED_IN_CANNED_RESPONSE = "<>()\"/;:^'"

CHARACTER_LIMIT_CANNED_RESPONSE = 500

CHARACTER_LIMIT_CANNED_KEYWORD = 25

CANNED_RESPONSE_ITEM_COUNT = 20

COGNOAI_LOGO_PATH = "/files/EasyAssistApp/img/getcogno_ai.png"

CANNED_RESPONSE_EXPORT_TEMPLATE_PATH = "/files/templates/easyassist-template/canned_response_template.xlsx"

AUTH_TOKEN_GENERATION_API_DOCUMENTATION = "https://documenter.getpostman.com/view/17429957/U16huSZo#0b65b44b-a322-4d18-9971-c6d3b5b415ef"

COBROWSE_API_DOCUMENTS_DOCUMENTATION = {
    "inbound_api_doc": "https://documenter.getpostman.com/view/17429957/U16huSZo#d8e59a01-029d-422d-a4e0-fad013b74ed8",
    "search_lead_api_doc": "https://documenter.getpostman.com/view/17429957/U16huSZo#05dbc7fc-adb6-4be8-bd14-dd65ae987db9",
    "droplink_api_doc": "https://documenter.getpostman.com/view/17429957/U16huSZo#0b31ab97-368c-457f-8fb0-11a4546a2706",
    "support_history_api_doc": "https://documenter.getpostman.com/view/17429957/U16huSZo#0c35e1df-8eba-4435-93fe-b326747e08b2",
    "chat_history_api_doc": "https://documenter.getpostman.com/view/17429957/U16huSZo#f2bd1b95-6332-44cf-8465-c27d45c034ec",
}

COGNO_MEET_API_DOCUMENTS_DOCUMENTATION = {
    "create_meeting_api_doc": "https://documenter.getpostman.com/view/17429957/U16huSZs#745d4255-28db-4798-af18-b67dd676879e",
    "delete_meeting_api_doc": "https://documenter.getpostman.com/view/17429957/U16huSZs#243d532e-4ab9-478f-8449-176aa1e7b633",
    "meeting_status_api_doc": "https://documenter.getpostman.com/view/17429957/U16huSZs#b4440373-9a76-49b0-bb8f-3fe0c6e8da5f",
    "meeting_details_api_doc": "https://documenter.getpostman.com/view/17429957/U16huSZs#18bdd885-2060-4964-ac10-8ce1090fc27f",
}

AGENT_MANAGEMENT_API_DOCUMENTS_DOCUMENTATION = {
    "auth_token_api_doc": "https://documenter.getpostman.com/view/17492232/UzR1KNHG#107da9b2-07f2-4799-a5fc-e69d43d305e0",
    "create_user_api_doc": "https://documenter.getpostman.com/view/17492232/UzR1KNHG#6b833d37-5755-439a-8682-bc85a78adb30",
    "update_user_api_doc": "https://documenter.getpostman.com/view/17492232/UzR1KNHG#0488871d-c810-4562-85be-61821a403d8f",
    "change_user_status_api_doc": "https://documenter.getpostman.com/view/17492232/UzR1KNHG#73fe91f0-0d9e-4f74-b1a6-3739594f6f6e",
    "user_status_api_doc": "https://documenter.getpostman.com/view/17492232/UzR1KNHG#de405620-d947-4170-b0dd-53832bd113c5",
    "get_all_users_status_api_doc": "https://documenter.getpostman.com/view/17492232/UzR1KNHG#cff85469-66cd-458d-a67f-279ca7a1eb9e",
    "get_list_of_users_api_doc": "https://documenter.getpostman.com/view/17492232/UzR1KNHG#1f3533bd-4e89-43fa-aa3a-5b4605d712cb",
    "change_password_api_doc": "https://documenter.getpostman.com/view/17492232/UzR1KNHG#3d7f3ac1-8ef6-49a9-a46c-243467b070d4",
}

AGENT_CREATION_LIMIT_EXHAUST_ERROR = "You have already created the maximum number of agents allowed for your account. Please contact admin to upgrade the limit."

SUPERVISOR_CREATION_LIMIT_EXHAUST_ERROR = "You have already created the maximum number of supervisors allowed for your account. Please contact admin to upgrade the limit."

NO_DATA_FOUND = "No data found for the selected period"

NO_DATA = "No data"

NO_DATA_PDF_PATH = '/files/EasyAssistApp/no_data_found.pdf'

CRONJOB_TRACKER_EXPIRY_TIME = 43200  # In seconds

HOURLY_CRONJOB_TRACKER_EXPIRY_TIME = 5400  # In seconds

ANALYTICS_MAIL_BUTTON_CSS = """
    height: 41px;
    width: 259px;
    border-radius: 30px;
    background: #3905D6;
    border-radius: 30px;
    color: white;
    text-decoration: none;
    font-style: normal;
    font-weight: bold;
    font-size: 14px;
    line-height: 17px;
    letter-spacing: 0.025em;
    color: #ffffff;
    padding: 10px;
"""
