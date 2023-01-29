import re
import sys
import base64
import magic
import mimetypes
import json
import logging

logger = logging.getLogger(__name__)


"""
Description: This class contains all the attributes of easychatbot user. It may have some utility methods.
"""


class EasyChatBotUser:

    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id", "")
        self.bot_id = kwargs.get("bot_id", "")
        self.bot_name = kwargs.get("bot_name", "None")
        self.bot_obj = kwargs.get("bot_obj", None)
        self.bot_channel_obj = kwargs.get("bot_channel_obj", None)
        self.category_obj = kwargs.get("category_obj", None)
        self.user = kwargs.get("user", None)
        self.bot_info_obj = kwargs.get("bot_info_obj", None)
        self.language_template_obj = kwargs.get("language_template_obj", None)
        self.intent_obj_category_based = kwargs.get(
            "intent_obj_category_based", None)
        self.message = kwargs.get("message", "None")
        self.src = kwargs.get("src", "en")
        self.selected_language = kwargs.get("selected_language", None)
        self.channel_name = kwargs.get("channel", "Web")
        self.original_message = kwargs.get("original_message", "")
        self.translated_message = kwargs.get("translated_message", None)
        self.is_bot_language_change_confirmed = kwargs.get("is_bot_language_change_confirmed", False)
        self.category_name = kwargs.get("category_name", None)
        self.is_recur_flag = kwargs.get("is_recur_flag", False)
        self.parent_tree = kwargs.get("parent_tree", None)
        self.original_tree = kwargs.get("original_tree", None)
        self.extra = {'AppName': 'EasyChat',
                      'channel': self.channel_name, 'bot_id': self.bot_id}

    def update_easychat_bot_user_details(self, **kwargs):
        self.user_id = kwargs.get("user_id", self.user_id)
        self.bot_id = kwargs.get("bot_id", self.bot_id)
        self.bot_name = kwargs.get("bot_name", self.bot_name)
        self.bot_obj = kwargs.get("bot_obj", self.bot_obj)
        self.bot_channel_obj = kwargs.get("bot_channel_obj", self.bot_channel_obj)
        self.category_obj = kwargs.get("category_obj", self.category_obj)
        self.user = kwargs.get("user", self.user)
        self.bot_info_obj = kwargs.get("bot_info_obj", self.bot_info_obj)
        self.language_template_obj = kwargs.get(
            "language_template_obj", self.language_template_obj)
        self.intent_obj_category_based = kwargs.get(
            "intent_obj_category_based", self.intent_obj_category_based)
        self.message = kwargs.get("message", self.message)
        self.src = kwargs.get("src", self.src)
        self.selected_language = kwargs.get("selected_language", self.selected_language)
        self.channel_name = kwargs.get("channel", self.channel_name)
        self.channel_name = kwargs.get("channel_name", self.channel_name)
        self.is_bot_language_change_confirmed = kwargs.get("is_bot_language_change_confirmed", self.is_bot_language_change_confirmed)
        self.category_name = kwargs.get("category_name", self.category_name)
        self.original_message = kwargs.get(
            "original_message", self.original_message)
        self.translated_message = kwargs.get("translated_message", self.translated_message)
        self.is_recur_flag = kwargs.get("is_recur_flag", self.is_recur_flag)
        self.parent_tree = kwargs.get("parent_tree", self.parent_tree)
        self.original_tree = kwargs.get("original_tree", self.original_tree)


class EasyChatChannelParams:

    def __init__(self, channel_params, user_id):
        self.session_id = user_id
        self.window_location = ""

        self.is_go_back_enabled = False
        self.is_first_query = False
        self.is_save_attachment_required = False
        self.is_video_recorder_allowed = False
        self.entered_suggestion = False
        self.is_form_assist = False
        self.is_sticky_message = False
        self.is_campaign_link = False
        self.is_manually_typed_query = True
        self.is_sticky_message_called_in_flow = False
        self.is_attachment_succesfull = False
        self.is_intent_tree = False

        self.form_data_widget = ""
        self.attached_file_src = ""
        self.attached_file_path = ""
        self.attachment = None
        self.is_attachment_already_saved_on_server = False
        self.is_attachment_available = False
        self.file_key = ""
        self.file_extention = ""
        self.widget_user_selected_list = "[]"
        self.web_page_source = ""
        self.is_widget_data = False

        self.client_city = ""
        self.client_state = ""
        self.client_pincode = ""

        self.channel_obj = None
        self.channel_name = ""

        self.training_question = ""
        self.match_percentage = ""
        self.is_session_started = True
        self.is_intiuitive_query = False
        self.response_repeat_needed = False

        self.is_business_initiated_session = False
        self.is_mobile = False

        self.is_initial_intent = False
        self.is_new_user = False

        self.load_channel_params(channel_params)

    def load_channel_params(self, channel_params):

        try:
            if "session_id" in channel_params:
                self.session_id = channel_params["session_id"]
                
            if "window_location" in channel_params:
                self.window_location = channel_params["window_location"]

            if "form_data_misdashboard" in channel_params:
                self.form_data_widget = channel_params['form_data_misdashboard']

            if "is_go_back_enabled" in channel_params and channel_params["is_go_back_enabled"] == True:
                self.is_go_back_enabled = True

            if self.channel_obj:
                self.channel_name = self.channel_obj.name

            if "entered_suggestion" in channel_params and channel_params["entered_suggestion"] == True:
                self.entered_suggestion = True

            if "is_video_recorder_allowed" in channel_params and channel_params["is_video_recorder_allowed"] == True:
                self.is_video_recorder_allowed = True

            if "is_save_attachment_required" in channel_params and channel_params["is_save_attachment_required"] == True:
                self.is_save_attachment_required = True

            if "is_first_query" in channel_params:
                self.is_first_query = channel_params["is_first_query"]

            if "attached_file_src" in channel_params:
                self.attached_file_src = channel_params["attached_file_src"]

            if "file_extension" in channel_params:
                self.file_extention = channel_params["file_extension"]

            if "is_form_assist" in channel_params and channel_params["is_form_assist"] == True:
                self.is_form_assist = True

            if "is_sticky_message" in channel_params and channel_params["is_sticky_message"] == True:
                self.is_sticky_message = True

            if "is_campaign_link" in channel_params and channel_params["is_campaign_link"] == True:
                self.is_campaign_link = True

            if "client_city" in channel_params:
                self.client_city = channel_params["client_city"]

            if "client_state" in channel_params:
                self.client_state = channel_params["client_state"]

            if "client_pincode" in channel_params:
                self.client_pincode = channel_params["client_pincode"]

            if "web_page_source" in channel_params:
                self.web_page_source = channel_params["web_page_source"]

            if "widget_user_selected_list" in channel_params:
                self.widget_user_selected_list = channel_params["widget_user_selected_list"]

            if "is_manually_typed_query" in channel_params:
                # if str(channel_params["is_manually_typed_query"]).strip().lower() == "false":
                self.is_manually_typed_query = channel_params["is_manually_typed_query"]

            if "attached_file_path" in channel_params:
                self.attached_file_path = channel_params["attached_file_path"]
            
            if "is_session_started" in channel_params:
                self.is_session_started = channel_params["is_session_started"]

            if "response_repeat_needed" in channel_params:
                self.response_repeat_needed = channel_params["response_repeat_needed"]

            if "is_business_initiated_session" in channel_params:
                self.is_business_initiated_session = channel_params["is_business_initiated_session"]

            if "is_widget_data" in channel_params:
                self.is_widget_data = channel_params["is_widget_data"]

            self.is_mobile = channel_params.get("is_mobile", False)

            self.is_initial_intent = channel_params.get("is_initial_intent", False)

            self.is_new_user = channel_params.get("is_new_user", False)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error load_channel_params! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


class EasyChatBotResponse:

    def __init__(self, **kwargs):
        self.message_received = kwargs.get("message", "")
        self.bot_response = kwargs.get("bot_response", "")
        self.attachment = kwargs.get("attachment", None)
        self.intent_name = kwargs.get("intent_name", None)
        self.small_talk_intent = kwargs.get("small_talk_intent", False)
        self.intent_recognized = kwargs.get("intent_recognized", None)
        self.category_name = kwargs.get("category_name", "Others")
        self.recommendations = kwargs.get("recommendations", "[]")
        self.choices = kwargs.get("choices", "[]")
        self.response_json = kwargs.get("response_json", "")
        self.widgets = kwargs.get("widgets", "")
        self.form_data_widget = kwargs.get("form_data_widget", "")

        default_api_request_response_parameters = [json.dumps(
            {}), json.dumps({}), json.dumps({}), json.dumps({})]

        self.api_request_response_parameters = kwargs.get(
            "api_request_response_parameters", default_api_request_response_parameters)
