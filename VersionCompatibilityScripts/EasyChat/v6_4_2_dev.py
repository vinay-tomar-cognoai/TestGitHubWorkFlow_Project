from EasyChatApp.models import BotInfo, RequiredBotTemplate, EasyChatTranslationCache, ApiTree, Tree, Intent, Bot, MessageAnalyticsDaily, MISDashboard, Category, Channel, BotChannel, UserSessionHealth

from EasyChatApp.constants_tms_proccesors import API_TREE_TMS_ATTACHMENT
from EasyChatApp.constants import DEFAULT_DO_NOT_TRANSLATE_KEYWORDS
from EasyChatApp.utils_analytics import return_mis_objects_excluding_blocked_sessions

from EasyChatApp.utils_bot import get_supported_languages, get_translated_text
from EasyChatApp.utils import logger
from datetime import datetime, timedelta

import json


def update_intent_icon_channels_info():
    try:

        intent_icon_channel_choices_info = {
            "web": ["1", "2", "3", "4", "5", "6", "7"],
            "android": ["1", "2", "3", "4", "5", "6", "7"],
            "ios": ["1", "2", "3", "4", "5", "6", "7"]
        }

        bot_info_objs = BotInfo.objects.filter(enable_intent_icon=True)
        for bot_info_obj in bot_info_objs:
            bot_info_obj.intent_icon_channel_choices_info = json.dumps(intent_icon_channel_choices_info)
            bot_info_obj.save(update_fields=["intent_icon_channel_choices_info"])
    except Exception as e:
        logger.error("Error in update_intent_icon_channels_info: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_external_link_unload_multilingual_error():
    try:
        language_bot_template_objs = RequiredBotTemplate.objects.all()
        external_link_unload_error = "This content is blocked. Please contact the site owner to fix the issue."

        for language_bot_template_obj in language_bot_template_objs:
            language_bot_template_obj.general_text += "$$$" + get_translated_text(external_link_unload_error, language_bot_template_obj.language.lang, EasyChatTranslationCache)
            language_bot_template_obj.save(update_fields=['general_text'])

    except Exception as e:
        logger.error("Error in update_external_link_unload_multilingual_error: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})    


def update_tms_add_attachment_response():
    try:
        add_attachment_response = {"items": [{"text_response": "<p>Kindly attach a screenshot of your issue (if any).</p><p>{/upload_image_note/}</p>", "speech_response": "Kindly attach a screenshot of your issue (if any). {/upload_image_note/}", "hinglish_response": "", "text_reprompt_response": "Kindly attach a screenshot of your issue (if any).<p>{/upload_image_note/}</p>", "speech_reprompt_response": "Kindly attach a screenshot of your issue (if any). {/upload_image_note/}", "tooltip_response": "", "ssml_response": "Kindly attach a screenshot of your issue (if any)."}]}

        add_attachments_api_tree_objs = ApiTree.objects.filter(name__startswith="AddAttachment")

        for add_attachments_api_tree_obj in add_attachments_api_tree_objs:
            add_attachments_api_tree_obj.api_caller = API_TREE_TMS_ATTACHMENT
            add_attachments_api_tree_obj.save(update_fields=['api_caller'])

            tree_objs = Tree.objects.filter(api_tree=add_attachments_api_tree_obj)
            for tree_obj in tree_objs:
                tree_obj.response.sentence = json.dumps(add_attachment_response)
                tree_obj.response.save(update_fields=["sentence"])
    except Exception as e:
        logger.error("Error in update_tms_add_attachment_response: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_do_not_translate_keywords():
    try:
        bot_info_objs = BotInfo.objects.all()
        for bot_info_obj in bot_info_objs:
            do_not_translate_keywords_list = []
            if bot_info_obj.do_not_translate_keywords_list:
                do_not_translate_keywords_list = json.loads(bot_info_obj.do_not_translate_keywords_list)

            bot_info_obj.do_not_translate_keywords_list = json.dumps(list(set(do_not_translate_keywords_list + DEFAULT_DO_NOT_TRANSLATE_KEYWORDS)))
            bot_info_obj.save(update_fields=["do_not_translate_keywords_list"])
    except Exception as e:
        logger.error("Error in update_do_not_translate_keywords: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_tree_level_advanced_nlp_to_false():
    try:
        bot_info_objs = BotInfo.objects.all()
        bot_info_objs.update(is_advance_tree_level_nlp_enabled=False)
    except Exception as e:
        logger.error("Error in update_tree_level_advanced_nlp_to_false: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_whatsapp_csat_bot_response():
    try:
        whatsapp_csat_response = {
            "items": [
                {
                    "text_response": "<p>Please take a second to tell us about your experience with <strong><span translate='no'>{/bot_name/}</span></strong>. Select anyone from the below options</p>",
                    "speech_response": "Please take a second to tell us about your experience with <span translate='no'>{/bot_name/}</span>. Select anyone from the below options",
                    "hinglish_response": "",
                    "text_reprompt_response": "<p>Please take a second to tell us about your experience with <strong><span translate='no'>{/bot_name/}</span></strong>. Select anyone from the below options</p>",
                    "speech_reprompt_response": "Please take a second to tell us about your experience with <span translate='no'>{/bot_name/}</span>. Select anyone from the below options",
                    "tooltip_response": "",
                    "ssml_response": "Please take a second to tell us about your experience with <strong><span translate='no'>{/bot_name/}</span></strong>. Select anyone from the below options"
                }
            ]
        }
        whatsapp_csat_flow_intents = Intent.objects.filter(is_whatsapp_csat=True)
        for whatsapp_csat_flow_intent in whatsapp_csat_flow_intents:
            bot_response_obj = whatsapp_csat_flow_intent.tree.response
            bot_response_obj.sentence = json.dumps(whatsapp_csat_response)
            bot_response_obj.save(update_fields=['sentence'])
        
    except Exception as e:
        logger.error("Error in update_csat_bot_response: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def create_message_analytics_for_none_category():
    try:
        today = datetime.now()
        last_date = today - timedelta(30)
        last_date = last_date.date()
        while(last_date < today.date()):
            for bot in Bot.objects.filter(is_deleted=False):
                supported_languages = get_supported_languages(bot, BotChannel)
                for channel in Channel.objects.filter(is_easychat_channel=True):
                    for category in [None]:
                        for language in supported_languages:
                            date_filtered_mis_objects = MISDashboard.objects.filter(
                                creation_date=last_date, channel_name=channel.name, bot=bot, category=category, selected_language=language)
                            
                            date_filtered_mis_objects = return_mis_objects_excluding_blocked_sessions(date_filtered_mis_objects, UserSessionHealth)
                            
                            # Total Messages
                            total_messages = date_filtered_mis_objects.count()
                            if total_messages == 0:
                                continue
                            total_messages_mobile = date_filtered_mis_objects.filter(is_mobile=True).count()
                            
                            # Unanswered messages
                            total_unanswered_messages = date_filtered_mis_objects.filter(
                                intent_name=None, is_unidentified_query=True)
                            total_unanswered_messages_count = total_unanswered_messages.count()
                            total_unanswered_messages_mobile_count = total_unanswered_messages.filter(is_mobile=True).count()
                            
                            # Answered Messages
                            total_answered_messages = total_messages - total_unanswered_messages_count
                            total_answered_messages_mobile_count = total_messages_mobile - total_unanswered_messages_mobile_count

                            if MessageAnalyticsDaily.objects.filter(date_message_analytics=last_date, channel_message=channel, bot=bot, category=category, selected_language=language):
                                pass
                            else:
                                MessageAnalyticsDaily.objects.create(total_messages_count=total_messages, answered_query_count=total_answered_messages,
                                                                     unanswered_query_count=total_unanswered_messages_count, channel_message=channel, date_message_analytics=last_date,
                                                                      bot=bot, category=category, selected_language=language,
                                                                      total_message_count_mobile=total_messages_mobile,
                                                                      answered_query_count_mobile=total_answered_messages_mobile_count,
                                                                      unanswered_query_count_mobile=total_unanswered_messages_mobile_count)
            last_date = last_date + timedelta(days=1)
    except Exception as e:
        logger.error("Error in create_message_analytics_for_none_category: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running update_intent_icon_channels_info...\n")

update_intent_icon_channels_info()

print("Running update_external_link_unload_multilingual_error...\n")

update_external_link_unload_multilingual_error()

print("Running update_tms_add_attachment_response...\n")

update_tms_add_attachment_response()

print("Running update_do_not_translate_keywords...\n")

update_do_not_translate_keywords()

print("Running update_whatsapp_csat_bot_response...\n")

update_whatsapp_csat_bot_response()

print("Running create_message_analytics_for_none_category...\n")

create_message_analytics_for_none_category()

print("Running update_tree_level_advanced_nlp_to_false...\n")

update_tree_level_advanced_nlp_to_false()
