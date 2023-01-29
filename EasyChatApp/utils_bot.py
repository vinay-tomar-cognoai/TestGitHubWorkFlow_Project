import copy
import re
import threading
import emoji
from EasyChatApp import constants
from EasyChatApp.models import LanguageTunedBot, LanguageTuningIntentTable, MISDashboard, ProfanityBotResponse, EmojiBotResponse, User, Bot, UserSessionHealth, BlockConfig, BotInfo, WhatsappCatalogueDetails
from django.utils import timezone
from EasyChatApp.utils_validation import EasyChatInputValidation
from LiveChatApp.models import LiveChatUser
import sys
import json
import logging
import hashlib
import datetime
from bs4 import BeautifulSoup
from EasyChatApp.utils_translation_module import translat_via_api
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from EasyChatApp.constants import BOT_DELETED_ERROR_MESSAGE, CHARACTER_LIMIT_LARGE_TEXT, DEFAULT_PAGINATION_METADATA, MODIFY_INTENT_ACTION


logger = logging.getLogger(__name__)


def wrap_do_not_translate_keywords(text, bot_info_obj):
    try:
        if not bot_info_obj or not bot_info_obj.enable_do_not_translate:
            return text
        
        text = " " + text.strip().lower() + " "
        do_not_translate_words = bot_info_obj.get_do_not_translate_keywords_list()

        for word in do_not_translate_words:
            lower_word = word.strip().lower()
            word = word.strip()
            text = text.replace(" " + lower_word + " ", " <span translate='no'>" + word + "</span> ")
            text = text.replace(">" + lower_word + " ", "><span translate='no'>" + word + "</span> ")
            text = text.replace(" " + lower_word + "<", " <span translate='no'>" + word + "</span><")
            text = text.replace(">" + lower_word + "<", "><span translate='no'>" + word + "</span><")
            text = text.replace("(" + lower_word + ")", "<span translate='no'>(" + word + ")</span>")
            text = text.replace(" " + lower_word + ".", " <span translate='no'>" + word + "</span>.")
            text = text.replace(" " + lower_word + ",", " <span translate='no'>" + word + "</span>,")
            text = text.replace(" " + lower_word + "?", " <span translate='no'>" + word + "</span>?")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("wrap_do_not_translate_keywords %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

    return text.strip()


def unwrap_do_not_translate_keywords(text):
    try:
        span_pattern = "<span[^>]*>|<\/span>"
        tags = re.findall(span_pattern, text)
        for tag in tags:
            text = text.replace(tag, "")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("unwrap_do_not_translate_keywords %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
    
    return text.strip()


"""
Translate text based on selected lanaguage
"""


def get_translated_text(multi_text, selected_language, EasyChatTranslationCache, translate_text=True, bot_info_obj=None):
    try:
        # if target language english, then no need to translate
        if selected_language == "en" or translate_text == False:
            return multi_text

        multi_text, _ = get_translated_text_with_api_status(
            multi_text, selected_language, EasyChatTranslationCache, True, bot_info_obj)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_translated_text %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

    return multi_text


"""
get_translated_text_with_api_status: This function will return translated text as well as google API call status.
"""


def get_translated_text_with_api_status(multi_text, selected_language, EasyChatTranslationCache, translate_api_call_status, bot_info_obj=None):
    try:
        # if target language english, then no need to translate
        if selected_language == "en":
            return multi_text, translate_api_call_status
        final_translated_text = ""

        if isinstance(multi_text, dict):
            for key in multi_text:
                if isinstance(multi_text[key], str):
                    text = multi_text[key]
                    list_of_variables, text = get_list_of_data_variables_and_get_variable_free_text(
                        text)

                    text = wrap_do_not_translate_keywords(text, bot_info_obj)

                    input_text_hash_data = hashlib.md5(
                        text.encode()).hexdigest()
                    if EasyChatTranslationCache.objects.filter(input_text_hash_data=input_text_hash_data, lang=selected_language):

                        final_translated_text = EasyChatTranslationCache.objects.filter(
                            input_text_hash_data=input_text_hash_data, lang=selected_language).first().translated_data

                        final_translated_text = add_data_variables_again_from_list(
                            list_of_variables, final_translated_text)

                        multi_text[key] = final_translated_text
                        continue
                    # We didn't have translated data
                    translated_text, is_translation_api_passed = translat_via_api(
                        text, selected_language)

                    if not is_translation_api_passed:
                        return multi_text, False

                    translated_text = unwrap_do_not_translate_keywords(translated_text)

                    final_translated_text = add_data_variables_again_from_list(
                        list_of_variables, final_translated_text)

                    final_translated_text = translated_text
                    multi_text[key] = final_translated_text
                    # If translation API has some issue then do not cache
                    if translated_text == text:
                        continue

                    output_text_hash_data = hashlib.md5(
                        translated_text.encode()).hexdigest()
                    EasyChatTranslationCache.objects.create(
                        input_text_hash_data=input_text_hash_data, output_text_hash_data=output_text_hash_data, input_text=text, translated_data=translated_text, lang=selected_language)

            return multi_text, translate_api_call_status
 
        for text in multi_text.split("$$$"):
            # Commenting below lines of code as it is manipulating html tags in response
            # validation_obj = EasyChatInputValidation()
            # if(bool(BeautifulSoup(text, "html.parser").find())):
            #     text = validation_obj.clean_html(text)

            # checking if we have translated data
            if final_translated_text != "":
                final_translated_text += "$$$"

            list_of_variables, text = get_list_of_data_variables_and_get_variable_free_text(
                text)

            unwrap_text = text
            text = wrap_do_not_translate_keywords(text, bot_info_obj)

            input_text_hash_data = hashlib.md5(text.encode()).hexdigest()
            hash_condition = True
            if EasyChatTranslationCache.objects.filter(input_text_hash_data=input_text_hash_data, lang=selected_language):
                if EasyChatTranslationCache.objects.filter(input_text_hash_data=input_text_hash_data, lang=selected_language).first().translated_data.strip() == "":
                    hash_condition = False
            else:
                hash_condition = False
            if hash_condition:
                updated_datavariable_text = EasyChatTranslationCache.objects.filter(
                    input_text_hash_data=input_text_hash_data, lang=selected_language).first().translated_data

                updated_datavariable_text = add_data_variables_again_from_list(
                    list_of_variables, updated_datavariable_text)
                final_translated_text += updated_datavariable_text
                continue

            # We didn't have translated data
            translated_text, is_translation_api_passed = translat_via_api(
                text, selected_language)
            if not is_translation_api_passed:
                return multi_text, False

            translated_text = unwrap_do_not_translate_keywords(translated_text)

            translated_text = add_data_variables_again_from_list(
                list_of_variables, translated_text)

            final_translated_text += translated_text
            # If translation API has some issue then do not cache
            if translated_text == text:
                continue

            output_text_hash_data = hashlib.md5(
                translated_text.encode()).hexdigest()
            EasyChatTranslationCache.objects.create(input_text_hash_data=input_text_hash_data, output_text_hash_data=output_text_hash_data,
                                                    input_text=unwrap_text, translated_data=translated_text, lang=selected_language)

        return final_translated_text, translate_api_call_status
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_translated_text %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
        return multi_text, translate_api_call_status


def get_list_of_data_variables_and_get_variable_free_text(sentence):

    list_of_data_variables = []
    data_removed_sentence = sentence

    try:
        regex_pattern = re.compile(r'\{\/(.*?)\/\}', re.X | re.IGNORECASE)

        # list of data variables in order the appear in the sentence
        list_of_data_variables = regex_pattern.findall(sentence)
        # this returns the list of text in string enclosed within thesse "{/"  "/}"
        # for eg - hi {/bot_id/} helo {/name/} -> ['bot_id" , "name"]

        data_removed_sentence = regex_pattern.sub("{//}", sentence)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_list_of_data_variables_and_get_variable_free_text %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

    return list_of_data_variables, data_removed_sentence


def add_data_variables_again_from_list(list_of_variables, sentence):

    final_sentence = sentence
    try:
        for data_variable in list_of_variables:

            final_sentence = final_sentence.replace(
                '{//}', '{/' + data_variable + '/}', 1)
            # replacing data variable one by one in the order they come

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_data_variables_again_from_list %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

    return final_sentence


"""
Translating response based on language selected by user

"""


def process_response_based_on_language(response, selected_language, EasyChatTranslationCache, bot_info_obj=None):
    try:
        # Translating cards related text
        cards = response["response"]["cards"]

        translated_cards = []
        for card in cards:
            card["title"] = get_translated_text(
                card["title"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
            card["content"] = get_translated_text(
                card["content"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
            translated_cards.append(card)

        # Translating choices related text
        choices = response["response"]["choices"]

        translated_choices = []
        for choice in choices:
            choice["value"] = get_translated_text(
                choice["value"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
            choice["display"] = get_translated_text(
                choice["display"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
            translated_choices.append(choice)

        # Translating recommendations related text
        recommendations = response["response"]["recommendations"]
        translated_recommendations = []
        for recommendation in recommendations:
            if type(recommendation) == dict and "name" in recommendation:
                if selected_language == "en":
                    intent_name = recommendation["name"]
                else:
                    lang_tuned_obj = LanguageTuningIntentTable.objects.filter(
                        language__lang=selected_language, intent__pk=recommendation["id"]).first()
                if lang_tuned_obj:
                    intent_name = lang_tuned_obj.multilingual_name
                else:
                    intent_name = get_translated_text(
                        recommendation["name"], selected_language, EasyChatTranslationCache)
                recommendation["name"] = intent_name
                translated_recommendations.append(recommendation)
            else:
                translated_recommendations.append(get_translated_text(recommendation, selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj))

        # Translating speech_response and text_response
        speech_response = get_translated_text(
            response["response"]["speech_response"]["text"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
        text_response = get_translated_text(
            response["response"]["text_response"]["text"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
        temp_text_response = response["response"]["text_response"]["text"]
        if text_response.strip() == BeautifulSoup(temp_text_response).text.strip():
            text_response = temp_text_response
        # Translating tables related text
        tables = []
        if "tables" in response["response"]:
            tables = response["response"]["tables"]

        translated_tables = []

        for row in tables:
            translated_col = []
            for col in row:
                translated_col.append(get_translated_text(
                    col, selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj))

            translated_tables.append(translated_col)

        # Translating datepicker_list related text
        translated_datepicker_list = []
        if "modes_param" in response["response"]["text_response"] and "datepicker_list" in response["response"]["text_response"]["modes_param"]:
            datepicker_list = response["response"][
                "text_response"]["modes_param"]["datepicker_list"]

            for datepicker in datepicker_list:
                datepicker["placeholder"] = get_translated_text(
                    datepicker["placeholder"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
                translated_datepicker_list.append(datepicker)

            response["response"]["text_response"]["modes_param"][
                "datepicker_list"] = translated_datepicker_list

        # Translating timepicker_list related text
        translated_timepicker_list = []
        if "modes_param" in response["response"]["text_response"] and "timepicker_list" in response["response"]["text_response"]["modes_param"]:
            timepicker_list = response["response"][
                "text_response"]["modes_param"]["timepicker_list"]

            for timepicker in timepicker_list:
                timepicker["placeholder"] = get_translated_text(
                    timepicker["placeholder"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
                translated_timepicker_list.append(timepicker)

            response["response"]["text_response"]["modes_param"][
                "timepicker_list"] = translated_timepicker_list

        # Translating radio_button_choices related text
        translated_radio_button_choices = []
        if "modes_param" in response["response"]["text_response"] and "radio_button_choices" in response["response"]["text_response"]["modes_param"]:
            radio_button_choices = response["response"][
                "text_response"]["modes_param"]["radio_button_choices"]

            for radio in radio_button_choices:
                translated_radio_button_choices.append(get_translated_text(
                    radio, selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj))

            response["response"]["text_response"]["modes_param"][
                "radio_button_choices"] = translated_radio_button_choices

        # Translating check_box_choices related text
        translated_check_box_choices = []
        if "modes_param" in response["response"]["text_response"] and "check_box_choices" in response["response"]["text_response"]["modes_param"]:
            check_box_choices = response["response"][
                "text_response"]["modes_param"]["check_box_choices"]

            for checkbox in check_box_choices:
                translated_check_box_choices.append(get_translated_text(
                    checkbox, selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj))

            response["response"]["text_response"]["modes_param"][
                "check_box_choices"] = translated_check_box_choices

        # Translating drop_down_choices related text
        translated_drop_down_choices = []
        if "modes_param" in response["response"]["text_response"] and "drop_down_choices" in response["response"]["text_response"]["modes_param"]:
            drop_down_choices = response["response"][
                "text_response"]["modes_param"]["drop_down_choices"]

            for dropdown in drop_down_choices:
                translated_drop_down_choices.append(get_translated_text(
                    dropdown, selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj))

            response["response"]["text_response"]["modes_param"][
                "drop_down_choices"] = translated_drop_down_choices

        # Translating range_slider_list related text
        translated_range_slider_list = []
        if "modes_param" in response["response"]["text_response"] and "range_slider_list" in response["response"]["text_response"]["modes_param"]:
            range_slider_list = response["response"][
                "text_response"]["modes_param"]["range_slider_list"]

            for range_slider in range_slider_list:
                range_slider["placeholder"] = get_translated_text(
                    range_slider["placeholder"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
                translated_range_slider_list.append(range_slider)

            response["response"]["text_response"]["modes_param"][
                "range_slider_list"] = translated_range_slider_list

        # Translating form related text
        translated_form_fields_list = []
        if "modes_param" in response["response"]["text_response"] and "form_fields_list" in response["response"]["text_response"]["modes_param"]:

            response["response"]["text_response"]["modes_param"]["form_name"] = get_translated_text(
                response["response"]["text_response"]["modes_param"]["form_name"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
            form_fields_list = json.loads(
                response["response"]["text_response"]["modes_param"]["form_fields_list"])

            for form_field in form_fields_list:
                form_field["label_name"] = get_translated_text(
                    form_field["label_name"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
                if form_field["input_type"] != "file_attach":
                    form_field["placeholder_or_options"] = get_translated_text(
                        form_field["placeholder_or_options"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
                translated_form_fields_list.append(form_field)

            response["response"]["text_response"]["modes_param"]["form_fields_list"] = json.dumps(
                translated_form_fields_list)

        # updating response with translated data
        response["response"]["choices"] = translated_choices
        response["response"]["cards"] = translated_cards
        response["response"]["recommendations"] = translated_recommendations
        response["response"]["speech_response"]["text"] = speech_response
        response["response"]["text_response"]["text"] = text_response
        response["response"]["tables"] = translated_tables
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("process_response_based_on_language %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

    return response


def get_fine_tuned_bot_inactivity_and_delay_response(response, bot_obj, selected_language, Language, EasyChatTranslationCache):
    try:
        lang_tuned_bot_obj = LanguageTunedBot.objects.filter(
            bot=bot_obj, language=Language.objects.get(lang=selected_language))
        if lang_tuned_bot_obj.exists():

            lang_tuned_bot_obj = lang_tuned_bot_obj.first()
            bot_inactivity_msg = lang_tuned_bot_obj.bot_inactivity_response
            bot_response_delay_message = lang_tuned_bot_obj.bot_response_delay_message

        else:

            bot_inactivity_msg = get_translated_text(
                response["bot_inactivity_msg"], selected_language, EasyChatTranslationCache)

            bot_response_delay_message = get_translated_text(
                response["bot_response_delay_message"], selected_language, EasyChatTranslationCache)

        return bot_inactivity_msg, bot_response_delay_message
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("process_response_based_on_language %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

        return response["bot_inactivity_msg"], response["bot_response_delay_message"]


def process_welcome_banner_list_based_on_language(intent_name, intent, language_obj, selected_language, EasyChatTranslationCache, LanguageTuningIntentTable):
    try:
        
        if not intent:
            return intent_name

        lang_tuned_obj = LanguageTuningIntentTable.objects.filter(language=language_obj, intent=intent).first()
        
        if lang_tuned_obj:
            intent_name = lang_tuned_obj.multilingual_name
        else:
            intent_name = get_translated_text(intent_name, selected_language, EasyChatTranslationCache)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("process_welcome_banner_list_based_on_language %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
    
    return intent_name


"""
Translating response based on language selected by user

"""


def process_channel_details_based_on_language(response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache, bot_info_obj=None):
    try:
        all_feedbacks = get_translated_text(
            response["all_feedbacks"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)

        bot_inactivity_msg, bot_response_delay_message = get_fine_tuned_bot_inactivity_and_delay_response(
            response, bot_channel_obj.bot, selected_language, Language, EasyChatTranslationCache)

        reprompt_message = get_translated_text(
            response["reprompt_message"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)

        session_end_message = get_translated_text(
            response["session_end_message"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)

        speech_message = get_translated_text(
            response["speech_message"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)

        speech_welcome_message = get_translated_text(
            response["speech_welcome_message"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)

        welcome_message, failure_message, _ = check_and_create_channel_details_language_tuning_objects(
            response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
        # Translating sticky button intent names
        sticky_intents_list = response["sticky_intents_list"]

        translated_sticky_intents_list = []
        for sticky_intent in sticky_intents_list:
            if type(sticky_intent) == dict and "name" in sticky_intent:
                temp_sticky_intent = ""
                if selected_language == "en":
                    temp_sticky_intent = sticky_intent
                else:
                    lang_tuned_obj = LanguageTuningIntentTable.objects.filter(language__lang=selected_language, intent__pk=sticky_intent["id"]).first()
                if lang_tuned_obj:
                    temp_sticky_intent = lang_tuned_obj.multilingual_name
                    sticky_intent["name"] = temp_sticky_intent
                else:
                    sticky_intent["name"] = get_translated_text(
                        sticky_intent["name"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
                translated_sticky_intents_list.append(sticky_intent)
            else:
                translated_sticky_intents_list.append(get_translated_text(sticky_intent, selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj))

        # Translating sticky button intent names as menu view
        sticky_intents_list_menu = response["sticky_intents_list_menu"]

        translated_sticky_intents_list_menu = []

        for sticky_intent in sticky_intents_list_menu:
            sticky_intents_temp = []
            temp_sticky_intent = ""
            if selected_language == "en":
                temp_sticky_intent = sticky_intent
            else:
                lang_tuned_obj = LanguageTuningIntentTable.objects.filter(language__lang=selected_language, intent__pk=sticky_intent[2]).first()
            if lang_tuned_obj:
                temp_sticky_intent = lang_tuned_obj.multilingual_name
                sticky_intents_temp.append(temp_sticky_intent)
            else:
                sticky_intents_temp.append(get_translated_text(
                    sticky_intent[0], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj))
            sticky_intents_temp.append(sticky_intent[1])
            sticky_intents_temp.append(sticky_intent[2])
            translated_sticky_intents_list_menu.append(sticky_intents_temp)

        # Translating initial intent names
        initial_messages_list = response["initial_messages"]["items"]

        translated_initial_messages_list = []

        for initial_message in initial_messages_list:
            if type(initial_message) == dict and "name" in initial_message:
                if "id" in initial_message:
                    if selected_language == "en":
                        intent_name = initial_message["name"]
                    else:
                        lang_tuned_obj = LanguageTuningIntentTable.objects.filter(
                            language__lang=selected_language, intent__pk=initial_message["id"]).first()
                    if lang_tuned_obj:
                        intent_name = lang_tuned_obj.multilingual_name
                    else:
                        intent_name = get_translated_text(
                            initial_message["name"], selected_language, EasyChatTranslationCache)
                    initial_message["name"] = intent_name
                else:
                    initial_message["name"] = get_translated_text(initial_message["name"], selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
                translated_initial_messages_list.append(initial_message)
            else:
                translated_initial_messages_list.append(get_translated_text(initial_message, selected_language, EasyChatTranslationCache, bot_info_obj=bot_info_obj))
        # Updating translated data
        response["all_feedbacks"] = all_feedbacks
        response["bot_inactivity_msg"] = bot_inactivity_msg
        response["bot_response_delay_message"] = bot_response_delay_message
        response["failure_message"] = failure_message
        response["reprompt_message"] = reprompt_message
        response["session_end_message"] = session_end_message
        response["speech_message"] = speech_message
        response["speech_welcome_message"] = speech_welcome_message
        response["welcome_message"] = welcome_message
        response["sticky_intents_list"] = translated_sticky_intents_list
        response["sticky_intents_list_menu"] = translated_sticky_intents_list_menu
        response["initial_messages"][
            "items"] = translated_initial_messages_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("process_channel_details_based_on_language %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})

    return response


"""

Creating language template for English(default) language
"""


def create_language_en_template(bot_obj, lang_obj, RequiredBotTemplate):

    if bot_obj == None:
        return

    template_obj = check_and_create_default_language_object
    return template_obj


"""

This function check for bot language template, if it does not exists then it creates one.

"""


def check_and_create_bot_language_template_obj(bot_obj, supported_lang, RequiredBotTemplate, Language):
    try:
        for lang in supported_lang:
            lang_obj = Language.objects.get(lang=lang)
            language_template = RequiredBotTemplate.objects.filter(
                bot=bot_obj, language=lang_obj)
            if not language_template:
                if lang == "en" and bot_obj:
                    check_and_create_default_language_object(
                        bot_obj, Language, RequiredBotTemplate)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_create_bot_language_template_obj : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def check_and_create_channel_details_language_tuning_objects(response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache):
    try:
        # if language tuned botchannel objects are created for the first time
        # then auto fixing of fileds is not required
        if LanguageTunedBotChannel.objects.filter(bot_channel=bot_channel_obj).exists():
            activity_update = {
                "is_welcome_message_updated": "false",
                "is_failure_message_updated": "false",
                "is_authentication_message_updated": "false",
                "is_auto_pop_up_text_updated": "false",
                "is_web_prompt_message_updated": "false",
                "list_of_updated_ids": "[]",
                "is_block_spam_data_updated": "false",
                "block_spam_field": ""
            }
            activity_update = json.dumps(activity_update)
            bot_channel_obj.activity_update = activity_update
            bot_channel_obj.save()
        welcome_message, failure_message, authentication_message = "", "", ""

        lang_obj = Language.objects.get(lang=selected_language)
        language_tuned_objects = LanguageTunedBotChannel.objects.filter(
            language=lang_obj, bot_channel=bot_channel_obj)

        if "welcome_message" in response:
            welcome_message = response['welcome_message']
        if "failure_message" in response:
            failure_message = response['failure_message']
        if "authentication_message" in response:
            authentication_message = response['authentication_message']
        query_warning_message_text = response.get("query_warning_message_text", "")
        query_block_message_text = response.get("query_block_message_text", "")
        keywords_warning_message_text = response.get("keywords_warning_message_text", "")
        keywords_block_message_text = response.get("keywords_block_message_text", "")

        if language_tuned_objects.exists():
            language_tuned_object = language_tuned_objects[0]
            language_tuned_whatsapp_data = json.loads(language_tuned_object.block_spam_data)
            welcome_message = language_tuned_object.welcome_message
            failure_message = language_tuned_object.failure_message
            authentication_message = language_tuned_object.authentication_message
            if language_tuned_object.block_spam_data != "{}":
                query_warning_message_text = language_tuned_whatsapp_data["query_warning_message_text"]
                query_block_message_text = language_tuned_whatsapp_data["query_block_message_text"]
                keywords_warning_message_text = language_tuned_whatsapp_data["keywords_warning_message_text"]
                keywords_block_message_text = language_tuned_whatsapp_data["keywords_block_message_text"]
            elif bot_channel_obj.channel.name == "WhatsApp":
                query_warning_message_text = get_translated_text(
                    query_warning_message_text, selected_language, EasyChatTranslationCache)
                query_block_message_text = get_translated_text(
                    query_block_message_text, selected_language, EasyChatTranslationCache)
                keywords_warning_message_text = get_translated_text(
                    keywords_warning_message_text, selected_language, EasyChatTranslationCache)
                keywords_block_message_text = get_translated_text(
                    keywords_block_message_text, selected_language, EasyChatTranslationCache)
                language_tuned_block_spam_data = json.dumps({
                    "query_warning_message_text": query_warning_message_text,
                    "query_block_message_text": query_block_message_text,
                    "keywords_warning_message_text": keywords_warning_message_text,
                    "keywords_block_message_text": keywords_block_message_text
                })
                language_tuned_object.block_spam_data = language_tuned_block_spam_data
                language_tuned_object.save(update_fields=["block_spam_data"])
            return welcome_message, failure_message, authentication_message
        else:
            failure_message = get_translated_text(
                failure_message, selected_language, EasyChatTranslationCache)
            welcome_message = get_translated_text(
                welcome_message, selected_language, EasyChatTranslationCache)
            authentication_message = get_translated_text(
                authentication_message, selected_language, EasyChatTranslationCache)
            query_warning_message_text = get_translated_text(
                query_warning_message_text, selected_language, EasyChatTranslationCache)
            query_block_message_text = get_translated_text(
                query_block_message_text, selected_language, EasyChatTranslationCache)
            keywords_warning_message_text = get_translated_text(
                keywords_warning_message_text, selected_language, EasyChatTranslationCache)
            keywords_block_message_text = get_translated_text(
                keywords_block_message_text, selected_language, EasyChatTranslationCache)
            language_tuned_block_spam_data = json.dumps({
                "query_warning_message_text": query_warning_message_text,
                "query_block_message_text": query_block_message_text,
                "keywords_warning_message_text": keywords_warning_message_text,
                "keywords_block_message_text": keywords_block_message_text
            })
            if create_language_tuned_object:
                LanguageTunedBotChannel.objects.create(language=lang_obj, bot_channel=bot_channel_obj, welcome_message=welcome_message,
                                                       failure_message=failure_message, authentication_message=authentication_message,
                                                       block_spam_data=language_tuned_block_spam_data)
                logger.info("language tunder object created for lang " + str(lang_obj) + "for bot channel " + str(bot_channel_obj), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            return welcome_message, failure_message, authentication_message

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_create_bot_language_template_obj : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return welcome_message, failure_message, authentication_message


def auto_fix_language_tuned_objects(bot_channel, channel_activity_update, LanguageTunedBotChannel, EasyChatTranslationCache, block_config=None):
    try:
        if "is_welcome_message_updated" in channel_activity_update and channel_activity_update["is_welcome_message_updated"] == "true":
            lang_objs = LanguageTunedBotChannel.objects.filter(
                bot_channel=bot_channel)
            for lang_tune_obj in lang_objs:
                lang_tune_obj.welcome_message = get_translated_text(
                    bot_channel.welcome_message, lang_tune_obj.language.lang, EasyChatTranslationCache)
                lang_tune_obj.save()
        if "is_failure_message_updated" in channel_activity_update and channel_activity_update["is_failure_message_updated"] == "true":
            lang_objs = LanguageTunedBotChannel.objects.filter(
                bot_channel=bot_channel)
            for lang_tune_obj in lang_objs:
                lang_tune_obj.failure_message = get_translated_text(
                    bot_channel.failure_message, lang_tune_obj.language.lang, EasyChatTranslationCache)
                lang_tune_obj.save()
        if "is_authentication_message_updated" in channel_activity_update and channel_activity_update["is_authentication_message_updated"] == "true":
            lang_objs = LanguageTunedBotChannel.objects.filter(
                bot_channel=bot_channel)
            for lang_tune_obj in lang_objs:
                lang_tune_obj.authentication_message = get_translated_text(
                    bot_channel.authentication_message, lang_tune_obj.language.lang, EasyChatTranslationCache)
                lang_tune_obj.save()
        if "is_auto_pop_up_text_updated" in channel_activity_update and channel_activity_update["is_auto_pop_up_text_updated"] == "true":
            lang_objs = LanguageTunedBot.objects.filter(
                bot=bot_channel.bot)
            for lang_tune_obj in lang_objs:
                lang_tune_obj.auto_pop_up_text = get_translated_text(
                    bot_channel.bot.auto_pop_text, lang_tune_obj.language.lang, EasyChatTranslationCache)
                lang_tune_obj.save()

        if "is_web_prompt_message_updated" in channel_activity_update and channel_activity_update["is_web_prompt_message_updated"] == "true":
            list_of_ids_to_be_updated = json.loads(
                channel_activity_update["list_of_updated_ids"])
            # this will ideally contain only 1 element
            bot_obj = bot_channel.bot
            lang_objs = LanguageTunedBot.objects.filter(
                bot=bot_obj)
            web_landing_data_list = json.loads(bot_obj.web_url_landing_data)
            list_of_text_to_be_updated_from = [
                ""] * len(list_of_ids_to_be_updated)
            for data in web_landing_data_list:
                if data['id'] in list_of_ids_to_be_updated:
                    index = list_of_ids_to_be_updated.index(data['id'])
                    prompt_text = data['prompt_message']
                    list_of_text_to_be_updated_from[index] = prompt_text
            # now we have 2 lists in which one is having id of edited web landing data which needs to be fixed and
            # other list at the same index stores the text in english of that
            # web landing data
            for lang_tuned_obj in lang_objs:
                tuned_web_landing_data_list = json.loads(
                    lang_tuned_obj.web_url_landing_data)
                for tuned_data in tuned_web_landing_data_list:
                    tuned_id = tuned_data['id']

                    if tuned_id in list_of_ids_to_be_updated:
                        index = list_of_ids_to_be_updated.index(tuned_id)
                        tuned_data['prompt_message'] = get_translated_text(
                            list_of_text_to_be_updated_from[index], lang_tuned_obj.language.lang, EasyChatTranslationCache)

                lang_tuned_obj.web_url_landing_data = json.dumps(
                    tuned_web_landing_data_list)
                lang_tuned_obj.save()

        if "is_block_spam_data_updated" in channel_activity_update and channel_activity_update["is_block_spam_data_updated"]:
            lang_objs = LanguageTunedBotChannel.objects.filter(
                bot_channel=bot_channel)
            for lang_tune_obj in lang_objs:
                language_tuned_whatsapp_data = json.loads(lang_tune_obj.block_spam_data)
                if "block_spam_field" in channel_activity_update and "query_warning" in channel_activity_update["block_spam_field"]:
                    language_tuned_whatsapp_data["query_warning_message_text"] = get_translated_text(
                        block_config.user_query_warning_message_text, lang_tune_obj.language.lang, EasyChatTranslationCache)
                if "block_spam_field" in channel_activity_update and "query_block" in channel_activity_update["block_spam_field"]:
                    language_tuned_whatsapp_data["query_block_message_text"] = get_translated_text(
                        block_config.user_query_block_message_text, lang_tune_obj.language.lang, EasyChatTranslationCache)
                if "block_spam_field" in channel_activity_update and "keyword_warning" in channel_activity_update["block_spam_field"]:
                    language_tuned_whatsapp_data["keywords_warning_message_text"] = get_translated_text(
                        block_config.spam_keywords_warning_message_text, lang_tune_obj.language.lang, EasyChatTranslationCache)
                if "block_spam_field" in channel_activity_update and "keyword_block" in channel_activity_update["block_spam_field"]:
                    language_tuned_whatsapp_data["keywords_block_message_text"] = get_translated_text(
                        block_config.spam_keywords_block_message_text, lang_tune_obj.language.lang, EasyChatTranslationCache)
                lang_tune_obj.block_spam_data = json.dumps(language_tuned_whatsapp_data)
                lang_tune_obj.save(update_fields=["block_spam_data"])

        if "catalogue_section_titles_updated" in channel_activity_update and channel_activity_update["catalogue_section_titles_updated"]:
            bot_obj = bot_channel.bot
            lang_objs = LanguageTunedBot.objects.filter(
                bot=bot_obj)
            catalogue_obj = WhatsappCatalogueDetails.objects.filter(
                bot=bot_obj).first()
            if catalogue_obj:
                catalogue_metadata = json.loads(
                    catalogue_obj.catalogue_metadata)
                for lang_tune_obj in lang_objs:
                    tuned_catalogue_metadata = lang_tune_obj.whatsapp_catalogue_data
                    if tuned_catalogue_metadata == "{}":
                        continue
                    tuned_catalogue_metadata = json.loads(
                        tuned_catalogue_metadata)
                    if "sections" in catalogue_metadata and "sections" in tuned_catalogue_metadata:
                        for section in channel_activity_update["catalogue_section_titles_updated"]:
                            if section in catalogue_metadata["sections"] and section in tuned_catalogue_metadata["sections"]:
                                tuned_catalogue_metadata["sections"][section]["section_title"] = get_translated_text(
                                    catalogue_metadata["sections"][section]["section_title"], lang_tune_obj.language.lang, EasyChatTranslationCache)

                    lang_tune_obj.whatsapp_catalogue_data = json.dumps(
                        tuned_catalogue_metadata)
                    lang_tune_obj.save(
                        update_fields=["whatsapp_catalogue_data"])

        if "is_catalogue_header_changed" in channel_activity_update and channel_activity_update["is_catalogue_header_changed"] == "true":
            auto_fix_catalogue_texts_tuning("header_text", bot_channel, EasyChatTranslationCache)

        if "is_catalogue_body_changed" in channel_activity_update and channel_activity_update["is_catalogue_body_changed"] == "true":
            auto_fix_catalogue_texts_tuning("body_text", bot_channel, EasyChatTranslationCache)

        if "is_catalogue_footer_changed" in channel_activity_update and channel_activity_update["is_catalogue_footer_changed"] == "true":
            bot_obj = bot_channel.bot
            lang_objs = LanguageTunedBot.objects.filter(
                bot=bot_obj)
            catalogue_obj = WhatsappCatalogueDetails.objects.filter(
                bot=bot_obj).first()
            if catalogue_obj:
                catalogue_metadata = json.loads(
                    catalogue_obj.catalogue_metadata)
                for lang_tune_obj in lang_objs:
                    tuned_catalogue_metadata = lang_tune_obj.whatsapp_catalogue_data
                    if tuned_catalogue_metadata == "{}":
                        continue
                    tuned_catalogue_metadata = json.loads(
                        tuned_catalogue_metadata)
                    if "footer_text" in catalogue_metadata and "footer_text" in tuned_catalogue_metadata:
                        tuned_catalogue_metadata["footer_text"] = get_translated_text(
                            catalogue_metadata["footer_text"], lang_tune_obj.language.lang, EasyChatTranslationCache)
                    elif "footer_text" in catalogue_metadata and "footer_text" not in tuned_catalogue_metadata:
                        tuned_catalogue_metadata["footer_text"] = get_translated_text(
                            catalogue_metadata["footer_text"], lang_tune_obj.language.lang, EasyChatTranslationCache)
                    elif "footer_text" not in catalogue_metadata and "footer_text" in tuned_catalogue_metadata:
                        tuned_catalogue_metadata["footer_text"] = ""
                    lang_tune_obj.whatsapp_catalogue_data = json.dumps(
                        tuned_catalogue_metadata)
                    lang_tune_obj.save(
                        update_fields=["whatsapp_catalogue_data"])

        if "is_catalogue_merge_cart_text_changed" in channel_activity_update and channel_activity_update["is_catalogue_merge_cart_text_changed"] == "true":
            auto_fix_catalogue_texts_tuning("merge_cart_text", bot_channel, EasyChatTranslationCache)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("auto_tune_language_tuned_objects : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def check_and_update_langauge_tuned_bot_configuration(bot_obj, language_obj, LanguageTunedBot, EasyChatTranslationCache, EmojiBotResponse):
    try:
        lang_tuned_bot_obj = LanguageTunedBot.objects.filter(
            language=language_obj, bot=bot_obj)
        emoji_bot_response_obj = EmojiBotResponse.objects.filter(bot=bot_obj)
        if not emoji_bot_response_obj.exists():
            emoji_bot_response_obj = EmojiBotResponse.objects.create(
                bot=bot_obj)
        else:
            emoji_bot_response_obj = emoji_bot_response_obj.first()

        profanity_bot_response_obj = ProfanityBotResponse.objects.filter(
            bot=bot_obj).first()

        if lang_tuned_bot_obj.exists():

            lang_tuned_bot_obj = lang_tuned_bot_obj.first()
            is_any_field_updated = False

            if lang_tuned_bot_obj.bot_inactivity_response == "":
                lang_tuned_bot_obj.bot_inactivity_response = get_translated_text(
                    bot_obj.bot_inactivity_response, language_obj.lang, EasyChatTranslationCache)
                is_any_field_updated = True

            if lang_tuned_bot_obj.bot_response_delay_message == "":
                lang_tuned_bot_obj.bot_response_delay_message = get_translated_text(
                    bot_obj.bot_response_delay_message, language_obj.lang, EasyChatTranslationCache)
                is_any_field_updated = True

            if lang_tuned_bot_obj.flow_termination_bot_response == "" and bot_obj.flow_termination_bot_response != "":
                lang_tuned_bot_obj.flow_termination_bot_response = get_translated_text(
                    bot_obj.flow_termination_bot_response, language_obj.lang, EasyChatTranslationCache)
                is_any_field_updated = True

            if lang_tuned_bot_obj.flow_termination_confirmation_display_message == "" and bot_obj.flow_termination_confirmation_display_message != "":
                lang_tuned_bot_obj.flow_termination_confirmation_display_message = get_translated_text(
                    bot_obj.flow_termination_confirmation_display_message, language_obj.lang, EasyChatTranslationCache)
                is_any_field_updated = True

            if lang_tuned_bot_obj.emoji_angry_response_text == "" and emoji_bot_response_obj.emoji_angry_response_text != "":
                lang_tuned_bot_obj.emoji_angry_response_text = get_translated_text(
                    emoji_bot_response_obj.emoji_angry_response_text, language_obj.lang, EasyChatTranslationCache)
                is_any_field_updated = True

            if lang_tuned_bot_obj.emoji_happy_response_text == "" and emoji_bot_response_obj.emoji_happy_response_text != "":
                lang_tuned_bot_obj.emoji_happy_response_text = get_translated_text(
                    emoji_bot_response_obj.emoji_happy_response_text, language_obj.lang, EasyChatTranslationCache)
                is_any_field_updated = True

            if lang_tuned_bot_obj.emoji_neutral_response_text == "" and emoji_bot_response_obj.emoji_neutral_response_text != "":
                lang_tuned_bot_obj.emoji_neutral_response_text = get_translated_text(
                    emoji_bot_response_obj.emoji_neutral_response_text, language_obj.lang, EasyChatTranslationCache)
                is_any_field_updated = True

            if lang_tuned_bot_obj.emoji_sad_response_text == "" and emoji_bot_response_obj.emoji_sad_response_text != "":
                lang_tuned_bot_obj.emoji_sad_response_text = get_translated_text(
                    emoji_bot_response_obj.emoji_sad_response_text, language_obj.lang, EasyChatTranslationCache)
                is_any_field_updated = True

            if lang_tuned_bot_obj.profanity_bot_response == "" and profanity_bot_response_obj and profanity_bot_response_obj.profanity_response_text != "":
                lang_tuned_bot_obj.profanity_bot_response = get_translated_text(
                    profanity_bot_response_obj.profanity_response_text, language_obj.lang, EasyChatTranslationCache)
                is_any_field_updated = True

            if is_any_field_updated:
                lang_tuned_bot_obj.save()

            return lang_tuned_bot_obj
        else:
            bot_inactivity_msg = bot_obj.bot_inactivity_response
            bot_response_delay_message = bot_obj.bot_response_delay_message
            flow_termination_bot_response = bot_obj.flow_termination_bot_response
            flow_termination_confirmation_display_message = bot_obj.flow_termination_confirmation_display_message

            emoji_angry_response_text = emoji_bot_response_obj.emoji_angry_response_text
            emoji_happy_response_text = emoji_bot_response_obj.emoji_happy_response_text
            emoji_neutral_response_text = emoji_bot_response_obj.emoji_neutral_response_text
            emoji_sad_response_text = emoji_bot_response_obj.emoji_sad_response_text

            profanity_response_text = ""
            if profanity_bot_response_obj:
                profanity_response_text = profanity_bot_response_obj.profanity_response_text

            bot_inactivity_msg = get_translated_text(
                bot_inactivity_msg, language_obj.lang, EasyChatTranslationCache)
            bot_response_delay_message = get_translated_text(
                bot_response_delay_message, language_obj.lang, EasyChatTranslationCache)
            flow_termination_bot_response = get_translated_text(
                flow_termination_bot_response, language_obj.lang, EasyChatTranslationCache)
            flow_termination_confirmation_display_message = get_translated_text(
                flow_termination_confirmation_display_message, language_obj.lang, EasyChatTranslationCache)

            emoji_angry_response_text = get_translated_text(
                emoji_angry_response_text, language_obj.lang, EasyChatTranslationCache)
            emoji_happy_response_text = get_translated_text(
                emoji_happy_response_text, language_obj.lang, EasyChatTranslationCache)
            emoji_neutral_response_text = get_translated_text(
                emoji_neutral_response_text, language_obj.lang, EasyChatTranslationCache)
            emoji_sad_response_text = get_translated_text(
                emoji_sad_response_text, language_obj.lang, EasyChatTranslationCache)

            profanity_response_text = get_translated_text(
                profanity_response_text, language_obj.lang, EasyChatTranslationCache)

            lang_tuned_bot_obj = LanguageTunedBot.objects.create(bot=bot_obj, language=language_obj, bot_inactivity_response=bot_inactivity_msg, bot_response_delay_message=bot_response_delay_message,
                                                                 flow_termination_bot_response=flow_termination_bot_response, flow_termination_confirmation_display_message=flow_termination_confirmation_display_message,
                                                                 emoji_angry_response_text=emoji_angry_response_text, emoji_happy_response_text=emoji_happy_response_text, emoji_neutral_response_text=emoji_neutral_response_text,
                                                                 emoji_sad_response_text=emoji_sad_response_text, profanity_bot_response=profanity_response_text)

            return lang_tuned_bot_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("auto_tune_language_tuned_objects : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return lang_tuned_bot_obj


def check_and_create_language_tuned_bot_objects(bot_obj, selected_language, form_assist_obj, Language, LanguageTunedBotChannel, EasyChatTranslationCache):
    try:
        lang_obj = Language.objects.get(lang=selected_language)
        lang_tuned_bot_obj = LanguageTunedBot.objects.filter(
            language=lang_obj, bot=bot_obj)
        if lang_tuned_bot_obj.exists():
            lang_tuned_bot_obj = lang_tuned_bot_obj[0]
            if bot_obj.auto_pop_text != "" and lang_tuned_bot_obj.auto_pop_up_text == "":
                auto_pop_up_text = get_translated_text(
                    bot_obj.auto_pop_text, selected_language, EasyChatTranslationCache)
                lang_tuned_bot_obj.auto_pop_up_text = auto_pop_up_text

            if form_assist_obj:
                if form_assist_obj.form_assist_auto_pop_text != "" and lang_tuned_bot_obj.form_assist_popup_text != "":
                    form_assist_popup_text = get_translated_text(
                        form_assist_obj.form_assist_auto_pop_text, selected_language, EasyChatTranslationCache)
                    lang_tuned_bot_obj.form_assist_popup_text = form_assist_popup_text

            tuned_web_landing_data_list = json.loads(
                lang_tuned_bot_obj.web_url_landing_data)
            web_landing_data_list = json.loads(bot_obj.web_url_landing_data)
            updated_tuned_web_landing_list = []
            for web_landing_data in web_landing_data_list:
                web_landing_data_id = web_landing_data['id']
                web_prompt_message = web_landing_data['prompt_message']
                is_present = False
                for tuned_web_landing_data in tuned_web_landing_data_list:
                    if tuned_web_landing_data['id'] == web_landing_data_id:
                        is_present = True
                        tuned_prompt_message = tuned_web_landing_data[
                            'prompt_message']
                        if tuned_prompt_message == "" and web_prompt_message != "":
                            web_landing_prompt_text = get_translated_text(
                                web_prompt_message, selected_language, EasyChatTranslationCache)
                            tuned_web_landing_data[
                                'prompt_message'] = web_landing_prompt_text
                        updated_tuned_web_landing_list.append(
                            tuned_web_landing_data)
                        break

                if not is_present:
                    tuned_single_data = web_landing_data
                    prompt_msg = web_landing_data['prompt_message']
                    if prompt_msg != "":
                        web_landing_prompt_text = get_translated_text(
                            prompt_msg, selected_language, EasyChatTranslationCache)
                        tuned_single_data[
                            'prompt_message'] = web_landing_prompt_text
                    else:
                        tuned_single_data['prompt_message'] = ""
                    updated_tuned_web_landing_list.append(tuned_single_data)

            lang_tuned_bot_obj.web_url_landing_data = json.dumps(
                updated_tuned_web_landing_list)
            lang_tuned_bot_obj.save()
            return lang_tuned_bot_obj
        else:
            auto_pop_up_text = bot_obj.auto_pop_text
            auto_pop_up_text = get_translated_text(
                auto_pop_up_text, selected_language, EasyChatTranslationCache)

            if form_assist_obj:
                form_assist_popup_text = form_assist_obj.form_assist_auto_pop_text
                form_assist_popup_text = get_translated_text(
                    form_assist_popup_text, selected_language, EasyChatTranslationCache)

            web_landing_data_list = json.loads(bot_obj.web_url_landing_data)
            tuned_web_landing_data_list = []
            for web_landing_data in web_landing_data_list:
                tuned_single_data = web_landing_data
                prompt_msg = web_landing_data['prompt_message']

                if prompt_msg != "":
                    web_landing_prompt_text = get_translated_text(
                        prompt_msg, selected_language, EasyChatTranslationCache)
                    tuned_single_data[
                        'prompt_message'] = web_landing_prompt_text
                else:
                    tuned_single_data['prompt_message'] = ""

                tuned_web_landing_data_list.append(tuned_single_data)
            tuned_web_url_landing_data = json.dumps(
                tuned_web_landing_data_list)
            lang_tuned_bot_obj = LanguageTunedBot.objects.create(
                bot=bot_obj, language=lang_obj, auto_pop_up_text=auto_pop_up_text, web_url_landing_data=tuned_web_url_landing_data, form_assist_popup_text=form_assist_popup_text)
            return lang_tuned_bot_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("auto_tune_language_tuned_objects : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return bot_obj


def get_multilingual_auto_popup_response(bot_obj, selected_language, Language, LanguageTunedBot, EasyChatTranslationCache):
    try:
        lang_obj = Language.objects.get(lang=selected_language)
        lang_tuned_bot_obj = LanguageTunedBot.objects.filter(
            language=lang_obj, bot=bot_obj)
        if lang_tuned_bot_obj.exists() and lang_tuned_bot_obj[0].auto_pop_up_text != "":
            return lang_tuned_bot_obj[0].auto_pop_up_text
        else:
            auto_pop_up_text = bot_obj.auto_pop_text
            auto_pop_up_text = get_translated_text(
                auto_pop_up_text, selected_language, EasyChatTranslationCache)
            return auto_pop_up_text
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("et_multilingual_auto_popup_response : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return bot_obj.auto_pop_text


def get_multilingual_form_assist_auto_popup_response(bot_obj, form_assist_obj, selected_language, Language, LanguageTunedBot, EasyChatTranslationCache):
    try:
        lang_obj = Language.objects.get(lang=selected_language)
        lang_tuned_bot_obj = LanguageTunedBot.objects.filter(
            language=lang_obj, bot=bot_obj)
        if lang_tuned_bot_obj.exists() and lang_tuned_bot_obj[0].form_assist_popup_text != "":
            return lang_tuned_bot_obj[0].form_assist_popup_text
        else:
            auto_pop_up_text = form_assist_obj.form_assist_auto_pop_text
            auto_pop_up_text = get_translated_text(
                auto_pop_up_text, selected_language, EasyChatTranslationCache)
            return auto_pop_up_text
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_multilingual_form_assist_auto_popup_response : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return form_assist_obj.form_assist_auto_pop_text


"""

This function check for supported bot languages.

"""


def get_supported_languages(bot_obj, BotChannel):
    supported_language = set()
    try:
        bot_channel_objs = BotChannel.objects.filter(bot=bot_obj)
        for bot_channel in bot_channel_objs:
            for language_obj in bot_channel.languages_supported.all():
                supported_language.add(language_obj)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_supported_languages : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return list(supported_language)


def get_tuned_table(sentence, language_obj, EasyChatTranslationCache, bot_info_obj=None):
    tuned_sentence = sentence
    try:
        tables = json.loads(sentence)['items']
        translated_tables = []

        for row in tables:
            translated_col = []
            for col in row:
                translated_col.append(get_translated_text(
                    col, language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj))

            translated_tables.append(translated_col)

        temp_tuned_table = json.loads(tuned_sentence)
        temp_tuned_table['items'] = translated_tables
        tuned_sentence = json.dumps(temp_tuned_table)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_tuned_tabels : " + str(e) + str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return tuned_sentence


def get_tuned_cards(sentence, language_obj, EasyChatTranslationCache, bot_info_obj=None):
    tuned_sentence = sentence
    try:
        cards = json.loads(sentence)['items']
        translated_cards = []
        for card in cards:
            card["title"] = get_translated_text(
                card["title"], language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
            card["content"] = get_translated_text(
                card["content"], language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
            translated_cards.append(card)
        temp_tuned_cards = json.loads(tuned_sentence)
        temp_tuned_cards['items'] = translated_cards
        tuned_sentence = json.dumps(temp_tuned_cards)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_tuned_cards : " + str(e) + str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return tuned_sentence


"""

This function check for supported bot languages.

"""


def get_tuned_sentence(sentence, language_obj, EasyChatTranslationCache, bot_info_obj=None):
    tuned_sentence = sentence
    try:
        text_response = json.loads(sentence)["items"][0]["text_response"]
        text_response_tuned = get_translated_text(
            text_response, language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)

        if language_obj.lang != "en" and text_response == text_response_tuned:
            return sentence
        speech_response_tuned = json.loads(
            sentence)["items"][0]["speech_response"]
        speech_response_tuned = get_translated_text(
            speech_response_tuned, language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)

        text_reprompt_response_tuned = json.loads(
            sentence)["items"][0]["text_reprompt_response"]
        text_reprompt_response_tuned = get_translated_text(
            text_reprompt_response_tuned, language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)

        speech_reprompt_response_tuned = json.loads(
            sentence)["items"][0]["speech_reprompt_response"]
        speech_reprompt_response_tuned = get_translated_text(
            speech_reprompt_response_tuned, language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)

        # tooltip_text_tuned = json.loads(sentence)["items"][0]["tooltip_text"]
        # tooltip_text_tuned = get_translated_text(tooltip_text_tuned, language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)

        temp_tuned_sentence = json.loads(tuned_sentence)
        temp_tuned_sentence["items"][0]["text_response"] = text_response_tuned

        temp_tuned_sentence["items"][0][
            "speech_response"] = speech_response_tuned

        temp_tuned_sentence["items"][0][
            "text_reprompt_response"] = text_reprompt_response_tuned

        temp_tuned_sentence["items"][0][
            "speech_reprompt_response"] = speech_reprompt_response_tuned

        # temp_tuned_sentence["items"][0]["tooltip_text"] = tooltip_text_tuned

        tuned_sentence = json.dumps(temp_tuned_sentence)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_tuned_sentence : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return tuned_sentence


"""

This function check for supported bot languages.

"""


def check_and_update_tunning_object(intent_obj, language_obj, LanguageTuningIntentTable, LanguageTuningTreeTable, LanguageTuningBotResponseTable, LanguageTuningChoicesTable, EasyChatTranslationCache):

    intent_tuning_obj = None
    try:
        # checking if language tunning for the perticular bot response already
        # exist or not?
        if LanguageTuningBotResponseTable.objects.filter(bot_response=intent_obj.tree.response, language=language_obj):
            return LanguageTuningIntentTable.objects.filter(intent=intent_obj, language=language_obj).first()

        bot_info_obj = BotInfo.objects.filter(bot=intent_obj.bots.all().first()).first()

        sentence = get_tuned_sentence(
            intent_obj.tree.response.sentence, language_obj, EasyChatTranslationCache, bot_info_obj)
        cards = get_tuned_cards(
            intent_obj.tree.response.cards, language_obj, EasyChatTranslationCache, bot_info_obj)
        table = get_tuned_table(
            intent_obj.tree.response.table, language_obj, EasyChatTranslationCache, bot_info_obj)
        # bot_response_tuning_obj.modes = get_tuned_modes(intent_obj.tree.response.modes, language_obj, EasyChatTranslationCache)
        # bot_response_tuning_obj.modes_param = get_tuned_modes_params(intent_obj.tree.response.modes_param, language_obj, EasyChatTranslationCache)
        # bot_response_tuning_obj.auto_response = get_tuned_cards(intent_obj.tree.response.auto_response, language_obj, EasyChatTranslationCache)
        multilingual_tree_name = get_translated_text(
            intent_obj.tree.name, language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj).strip()
        multilingual_intent_name = get_translated_text(
            intent_obj.name, language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj).strip()

        if language_obj.lang != "en":
            if multilingual_intent_name == intent_obj.name or multilingual_intent_name == "":
                return None
            if multilingual_tree_name == intent_obj.tree.name or multilingual_tree_name == "":
                return None

        bot_response_tuning_obj = LanguageTuningBotResponseTable.objects.create(
            bot_response=intent_obj.tree.response, language=language_obj)
        bot_response_tuning_obj.sentence = sentence
        bot_response_tuning_obj.cards = cards
        bot_response_tuning_obj.table = table
        bot_response_tuning_obj.save()

        tree_tuning_obj = LanguageTuningTreeTable.objects.create(
            tree=intent_obj.tree, language=language_obj, response=bot_response_tuning_obj)
        tree_tuning_obj.multilingual_name = multilingual_tree_name
        tree_tuning_obj.save()

        intent_tuning_obj, _ = LanguageTuningIntentTable.objects.get_or_create(
            intent=intent_obj, language=language_obj, defaults={"multilingual_name": multilingual_intent_name, "tree": tree_tuning_obj})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_update_tunning_object : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return intent_tuning_obj


def check_and_update_tunning_tree_object(tree_obj, language_obj, LanguageTuningIntentTable, LanguageTuningTreeTable, LanguageTuningBotResponseTable, LanguageTuningChoicesTable, EasyChatTranslationCache):

    tree_tuning_obj = None
    try:
        # checking if language tunning for the perticular bot response already
        # exist or not?

        if LanguageTuningBotResponseTable.objects.filter(bot_response=tree_obj.response, language=language_obj):
            return LanguageTuningTreeTable.objects.get(tree=tree_obj, language=language_obj)

        from EasyChatApp.utils import get_intent_obj_from_tree_obj

        intent_obj = get_intent_obj_from_tree_obj(tree_obj)
        bot_info_obj = None
        if intent_obj:
            bot_info_obj = BotInfo.objects.filter(bot=intent_obj.bots.all().first()).first()

        sentence = get_tuned_sentence(
            tree_obj.response.sentence, language_obj, EasyChatTranslationCache, bot_info_obj)
        cards = get_tuned_cards(tree_obj.response.cards,
                                language_obj, EasyChatTranslationCache, bot_info_obj)
        table = get_tuned_table(tree_obj.response.table,
                                language_obj, EasyChatTranslationCache, bot_info_obj)
        # bot_response_tuning_obj.modes = get_tuned_modes(intent_obj.tree.response.modes, language_obj, EasyChatTranslationCache)
        # bot_response_tuning_obj.modes_param = get_tuned_modes_params(intent_obj.tree.response.modes_param, language_obj, EasyChatTranslationCache)
        # bot_response_tuning_obj.auto_response = get_tuned_cards(intent_obj.tree.response.auto_response, language_obj, EasyChatTranslationCache)

        bot_response_tuning_obj = LanguageTuningBotResponseTable.objects.create(
            bot_response=tree_obj.response, language=language_obj)

        bot_response_tuning_obj.sentence = sentence
        bot_response_tuning_obj.cards = cards
        bot_response_tuning_obj.table = table
        bot_response_tuning_obj.save()

        tree_tuning_obj = LanguageTuningTreeTable.objects.create(
            tree=tree_obj, language=language_obj, response=bot_response_tuning_obj)
        tree_tuning_obj.multilingual_name = get_translated_text(
            tree_obj.name, language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
        tree_tuning_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_update_tunning_tree_object : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return tree_tuning_obj


def get_translated_bot_web_landing_list(bot_obj, web_landing_list, BotChannel, LanguageTunedBot, EasyChatTranslationCache):
    try:
        web_landing_data_list = json.loads(bot_obj.web_url_landing_data)
        lang_objs = BotChannel.objects.filter(bot=bot_obj, channel__name="Web")[
            0].languages_supported.all()

        for lang_obj in lang_objs:
            if lang_obj.lang == "en":
                continue
            lang_tuned_bot_obj = LanguageTunedBot.objects.filter(
                language=lang_obj, bot=bot_obj)
            translated_web_landing_list = []
            if lang_tuned_bot_obj.exists():
                web_landing_list.append({"selected_language": str(
                    lang_obj.lang), "data": lang_tuned_bot_obj[0].web_url_landing_data})
            else:
                for web_landing_data in web_landing_data_list:
                    tuned_single_data = web_landing_data
                    prompt_msg = web_landing_data['prompt_message']

                    if prompt_msg != "":
                        web_landing_prompt_text = get_translated_text(
                            prompt_msg, lang_obj.lang, EasyChatTranslationCache)
                        tuned_single_data[
                            'prompt_message'] = web_landing_prompt_text
                    else:
                        tuned_single_data['prompt_message'] = ""
                    translated_web_landing_list.append(tuned_single_data)
                web_landing_list.append({"selected_language": str(
                    lang_obj.lang), "data": json.dumps(translated_web_landing_list)})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_translated_bot_web_landing_list : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return web_landing_list


def need_to_show_auto_fix_popup_for_channels(bot_channel, channel_activity_update, selected_language, LanguageTunedBotChannel):
    try:
        # if either of the fields is true then we have to show the auto fix up
        # popup
        if selected_language != "en":
            return False
        if bot_channel.languages_supported.count() < 2:
            return False
        if not LanguageTunedBotChannel.objects.filter(bot_channel=bot_channel).exists():
            return False
        if "is_welcome_message_updated" in channel_activity_update and channel_activity_update["is_welcome_message_updated"] == "true":
            return True
        if "is_failure_message_updated" in channel_activity_update and channel_activity_update["is_failure_message_updated"] == "true":
            return True
        if "is_authentication_message_updated" in channel_activity_update and channel_activity_update["is_authentication_message_updated"] == "true":
            return True
        if "is_auto_pop_up_text_updated" in channel_activity_update and channel_activity_update["is_auto_pop_up_text_updated"] == "true":
            return True
        if "is_web_prompt_message_updated" in channel_activity_update and channel_activity_update["is_web_prompt_message_updated"] == "true":
            return True
        if "is_block_spam_data_updated" in channel_activity_update and channel_activity_update["is_block_spam_data_updated"] == "true":
            return True
        if "catalogue_section_titles_updated" in channel_activity_update and len(channel_activity_update["catalogue_section_titles_updated"]):
            return True
        if "is_catalogue_header_changed" in channel_activity_update and channel_activity_update["is_catalogue_header_changed"] == "true":
            return True
        if "is_catalogue_body_changed" in channel_activity_update and channel_activity_update["is_catalogue_body_changed"] == "true":
            return True
        if "is_catalogue_footer_changed" in channel_activity_update and channel_activity_update["is_catalogue_footer_changed"] == "true":
            return True
        if "is_catalogue_merge_cart_text_changed" in channel_activity_update and channel_activity_update["is_catalogue_merge_cart_text_changed"] == "true":
            return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("need_to_show_auto_fix_popup_for_channels : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return False


def auto_fix_language_tuned_bot_response_objects(bot_response_obj, activity_update, LanguageTuningBotResponseTable, EasyChatTranslationCache, bot_info_obj=None):
    try:
        lang_objs = LanguageTuningBotResponseTable.objects.filter(
            bot_response=bot_response_obj)
        for lang_tune_obj in lang_objs:
            sentence = get_tuned_sentence_based_on_activity_update(
                bot_response_obj.sentence, lang_tune_obj.sentence, lang_tune_obj.language, activity_update, EasyChatTranslationCache, bot_info_obj)
            lang_tune_obj.sentence = sentence
            if "are_cards_updated" in activity_update and activity_update["are_cards_updated"] == "true":
                cards = get_tuned_cards(
                    bot_response_obj.cards, lang_tune_obj.language, EasyChatTranslationCache, bot_info_obj)
                lang_tune_obj.cards = cards
            if "is_table_updated" in activity_update and activity_update["is_table_updated"] == "true":
                table = get_tuned_table(
                    bot_response_obj.table, lang_tune_obj.language, EasyChatTranslationCache, bot_info_obj)
                lang_tune_obj.table = table

            lang_tune_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("auto_fix_language_tuned_bot_response_objects : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def auto_fix_language_tuned_tree_objs(tree_obj, activity_update, LanguageTuningTreeTable, EasyChatTranslationCache):
    try:
        if "is_tree_name_updated" in activity_update and activity_update["is_tree_name_updated"] == "true":
            language_tuned_tree_objs = LanguageTuningTreeTable.objects.filter(tree=tree_obj)
            for lang_tuned_tree_obj in language_tuned_tree_objs:
                lang_tuned_tree_obj.multilingual_name = get_translated_text(tree_obj.name, lang_tuned_tree_obj.language.lang, EasyChatTranslationCache)
                lang_tuned_tree_obj.save(update_fields=["multilingual_name"])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("auto_fix_language_tuned_tree_objs : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def auto_fix_language_tuned_intent_objs(tree_obj, activity_update, Intent, LanguageTuningIntentTable, EasyChatTranslationCache):
    try:
        if "is_intent_name_updated" in activity_update and activity_update["is_intent_name_updated"] == "true":
            intent_obj = Intent.objects.filter(tree=tree_obj, is_deleted=False).first()
            if not intent_obj:
                return

            language_tuned_int_objs = LanguageTuningIntentTable.objects.filter(intent=intent_obj)
            for lang_tuned_int_obj in language_tuned_int_objs:
                lang_tuned_int_obj.multilingual_name = get_translated_text(intent_obj.name, lang_tuned_int_obj.language.lang, EasyChatTranslationCache)
                lang_tuned_int_obj.save(update_fields=["multilingual_name"])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("auto_fix_language_tuned_intent_objs : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_tuned_sentence_based_on_activity_update(sentence, lang_tuned_sentence, language_obj, activity_update, EasyChatTranslationCache, bot_info_obj=None):
    tuned_sentence = sentence
    try:
        text_response = json.loads(
            sentence)["items"][0]["text_response"]
        speech_response_tuned = json.loads(
            sentence)["items"][0]["speech_response"]
        text_reprompt_response_tuned = json.loads(
            sentence)["items"][0]["text_reprompt_response"]

        temp_tuned_sentence = json.loads(lang_tuned_sentence)

        if "is_text_response_updated" in activity_update and activity_update["is_text_response_updated"] == "true":
            text_response_tuned = get_translated_text(
                text_response, language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
            temp_tuned_sentence["items"][0][
                "text_response"] = text_response_tuned

        if "is_speech_response_updated" in activity_update and activity_update["is_speech_response_updated"] == "true":
            speech_response_tuned = get_translated_text(
                speech_response_tuned, language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
            temp_tuned_sentence["items"][0][
                "speech_response"] = speech_response_tuned

        if "is_text_reprompt_response_updated" in activity_update and activity_update["is_text_reprompt_response_updated"] == "true":
            text_reprompt_response_tuned = get_translated_text(
                text_reprompt_response_tuned, language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)
            temp_tuned_sentence["items"][0][
                "text_reprompt_response"] = text_reprompt_response_tuned

        tuned_sentence = json.dumps(temp_tuned_sentence)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_tuned_sentence : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return tuned_sentence


def need_to_show_auto_fix_popup_for_intents(bot_response_obj, activity_update, selected_language, eng_lang_obj, LanguageTuningBotResponseTable):
    try:
        # if either of the fields is true then we have to show the auto fix up
        # popup
        if selected_language != "en":
            return False
        # auto fix popup should not be thier if fine tuned objects are not
        # present other than english
        if not LanguageTuningBotResponseTable.objects.filter(bot_response=bot_response_obj).exclude(language=eng_lang_obj).exists():
            return False

        if "is_text_response_updated" in activity_update and activity_update["is_text_response_updated"] == "true":
            return True
        if "is_speech_response_updated" in activity_update and activity_update["is_speech_response_updated"] == "true":
            return True
        if "is_text_reprompt_response_updated" in activity_update and activity_update["is_text_reprompt_response_updated"] == "true":
            return True
        if "is_table_updated" in activity_update and activity_update["is_table_updated"] == "true":
            return True
        if "are_cards_updated" in activity_update and activity_update["are_cards_updated"] == "true":
            return True
        if "is_tree_name_updated" in activity_update and activity_update["is_tree_name_updated"] == "true":
            return True
        if "is_intent_name_updated" in activity_update and activity_update["is_intent_name_updated"] == "true":
            return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("need_to_show_auto_fix_popup_for_intents : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return False


def auto_fix_bot_configurations_objects(bot_obj, activity_update, LanguageTunedBot, EasyChatTranslationCache):
    try:
        lang_objs = LanguageTunedBot.objects.filter(
            bot=bot_obj)

        profanity_bot_response_obj = ProfanityBotResponse.objects.filter(
            bot=bot_obj).first()
        emoji_bot_response_obj = EmojiBotResponse.objects.filter(
            bot=bot_obj).first()

        for lang_tune_obj in lang_objs:
            lang = lang_tune_obj.language.lang
            if "is_bot_inactivity_response_updated" in activity_update and activity_update["is_bot_inactivity_response_updated"] == "true":
                lang_tune_obj.bot_inactivity_response = get_translated_text(
                    bot_obj.bot_inactivity_response, lang, EasyChatTranslationCache)

            if "is_bot_response_delay_message_updated" in activity_update and activity_update["is_bot_response_delay_message_updated"] == "true":
                lang_tune_obj.bot_response_delay_message = get_translated_text(
                    bot_obj.bot_response_delay_message, lang, EasyChatTranslationCache)

            if "is_flow_termination_bot_response_updated" in activity_update and activity_update["is_flow_termination_bot_response_updated"] == "true":
                lang_tune_obj.flow_termination_bot_response = get_translated_text(
                    bot_obj.flow_termination_bot_response, lang, EasyChatTranslationCache)

            if "is_flow_termination_confirmation_display_message_updated" in activity_update and activity_update["is_flow_termination_confirmation_display_message_updated"] == "true":
                lang_tune_obj.flow_termination_confirmation_display_message = get_translated_text(
                    bot_obj.flow_termination_confirmation_display_message, lang, EasyChatTranslationCache)

            if emoji_bot_response_obj:
                if "is_emoji_happy_response_text_updated" in activity_update and activity_update["is_emoji_happy_response_text_updated"] == "true":
                    lang_tune_obj.emoji_happy_response_text = get_translated_text(
                        emoji_bot_response_obj.emoji_happy_response_text, lang, EasyChatTranslationCache)

                if "is_emoji_angry_response_text_updated" in activity_update and activity_update["is_emoji_angry_response_text_updated"] == "true":
                    lang_tune_obj.emoji_angry_response_text = get_translated_text(
                        emoji_bot_response_obj.emoji_angry_response_text, lang, EasyChatTranslationCache)

                if "is_emoji_neutral_response_text_updated" in activity_update and activity_update["is_emoji_neutral_response_text_updated"] == "true":
                    lang_tune_obj.emoji_neutral_response_text = get_translated_text(
                        emoji_bot_response_obj.emoji_neutral_response_text, lang, EasyChatTranslationCache)

                if "is_emoji_sad_response_text_updated" in activity_update and activity_update["is_emoji_sad_response_text_updated"] == "true":
                    lang_tune_obj.emoji_sad_response_text = get_translated_text(
                        emoji_bot_response_obj.emoji_sad_response_text, lang, EasyChatTranslationCache)

            if profanity_bot_response_obj:
                if "is_profanity_response_text_updated" in activity_update and activity_update["is_profanity_response_text_updated"] == "true":
                    lang_tune_obj.profanity_bot_response = get_translated_text(
                        profanity_bot_response_obj.profanity_response_text, lang, EasyChatTranslationCache)

            lang_tune_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("auto_fix_bot_configurations_objects : " + str(e) + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def need_to_show_auto_fix_popup_for_bot_configuration(bot_obj, activity_update, selected_language, eng_lang_obj, LanguageTunedBot):
    try:
        # if either of the fields is true then we have to show the auto fix up
        # popup
        if selected_language != "en":
            return False
        # auto fix popup should not be thier if fine tuned objects are not
        # present other than english
        if not LanguageTunedBot.objects.filter(bot=bot_obj).exclude(language=eng_lang_obj).exists():
            return False

        if "is_bot_inactivity_response_updated" in activity_update and activity_update["is_bot_inactivity_response_updated"] == "true":
            return True

        if "is_bot_response_delay_message_updated" in activity_update and activity_update["is_bot_response_delay_message_updated"] == "true":
            return True

        if "is_flow_termination_bot_response_updated" in activity_update and activity_update["is_flow_termination_bot_response_updated"] == "true":
            return True

        if "is_flow_termination_confirmation_display_message_updated" in activity_update and activity_update["is_flow_termination_confirmation_display_message_updated"] == "true":
            return True

        if "is_emoji_happy_response_text_updated" in activity_update and activity_update["is_emoji_happy_response_text_updated"] == "true":
            return True

        if "is_emoji_angry_response_text_updated" in activity_update and activity_update["is_emoji_angry_response_text_updated"] == "true":
            return True

        if "is_emoji_neutral_response_text_updated" in activity_update and activity_update["is_emoji_neutral_response_text_updated"] == "true":
            return True

        if "is_emoji_sad_response_text_updated" in activity_update and activity_update["is_emoji_sad_response_text_updated"] == "true":
            return True

        if "is_profanity_response_text_updated" in activity_update and activity_update["is_profanity_response_text_updated"] == "true":
            return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("need_to_show_auto_fix_popup_for_bot_configuration : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return False


def get_language_constant_dict(language_template_obj):
    constant_keywords_dict = {}
    try:

        constant_keywords_dict[
            "bot_name"] = language_template_obj.bot_name
        constant_keywords_dict[
            "placeholder"] = language_template_obj.placeholder
        constant_keywords_dict["widgets_placeholder_text"] = language_template_obj.widgets_placeholder_text
        constant_keywords_dict[
            "close_button_tooltip"] = language_template_obj.close_button_tooltip
        constant_keywords_dict[
            "minimize_button_tooltip"] = language_template_obj.minimize_button_tooltip
        constant_keywords_dict[
            "home_button_tooltip"] = language_template_obj.home_button_tooltip
        constant_keywords_dict[
            "mic_button_tooltip"] = language_template_obj.mic_button_tooltip

        constant_keywords_dict[
            "typing_text"] = language_template_obj.typing_text
        constant_keywords_dict["send_text"] = language_template_obj.send_text
        constant_keywords_dict["cards_text"] = language_template_obj.cards_text
        constant_keywords_dict[
            "go_back_text"] = language_template_obj.go_back_text
        constant_keywords_dict["back_text"] = language_template_obj.back_text
        constant_keywords_dict["menu_text"] = language_template_obj.menu_text
        constant_keywords_dict[
            "search_text"] = language_template_obj.search_text
        constant_keywords_dict[
            "dropdown_text"] = language_template_obj.dropdown_text

        constant_keywords_dict["start_text"] = language_template_obj.start_text
        constant_keywords_dict["stop_text"] = language_template_obj.stop_text
        constant_keywords_dict[
            "submit_text"] = language_template_obj.submit_text
        constant_keywords_dict[
            "uploading_video_text"] = language_template_obj.uploading_video_text
        constant_keywords_dict[
            "cancel_text"] = language_template_obj.cancel_text
        constant_keywords_dict[
            "file_size_limit_text"] = language_template_obj.file_size_limit_text
        constant_keywords_dict[
            "file_attachment_text"] = language_template_obj.file_attachment_text
        constant_keywords_dict[
            "file_upload_success_text"] = language_template_obj.file_upload_success_text

        constant_keywords_dict[
            "feedback_text"] = language_template_obj.feedback_text
        constant_keywords_dict[
            "positive_feedback_options_text"] = language_template_obj.positive_feedback_options_text
        constant_keywords_dict[
            "negative_feedback_options_text"] = language_template_obj.negative_feedback_options_text
        constant_keywords_dict[
            "feedback_error_text"] = language_template_obj.feedback_error_text
        constant_keywords_dict[
            "success_feedback_text"] = language_template_obj.success_feedback_text
        constant_keywords_dict[
            "csat_form_text"] = language_template_obj.csat_form_text
        constant_keywords_dict[
            "csat_form_error_mobile_email_text"] = language_template_obj.csat_form_error_mobile_email_text
        constant_keywords_dict[
            "csat_emoji_text"] = language_template_obj.csat_emoji_text
        constant_keywords_dict[
            "date_range_picker_text"] = language_template_obj.date_range_picker_text
        constant_keywords_dict[
            "form_widget_text"] = language_template_obj.form_widget_text
        constant_keywords_dict[
            "choose_language"] = language_template_obj.choose_language
        constant_keywords_dict[
            "general_text"] = language_template_obj.general_text
        constant_keywords_dict[
            "minimize_text"] = language_template_obj.minimize_text
        constant_keywords_dict[
            "maximize_text"] = language_template_obj.maximize_text
        constant_keywords_dict[
            "mute_text"] = language_template_obj.mute_tooltip_text
        constant_keywords_dict[
            "unmute_text"] = language_template_obj.unmute_tooltip_text
        constant_keywords_dict[
            "no_result_found"] = language_template_obj.no_result_found_text
        constant_keywords_dict[
            "form_widget_error_text"] = language_template_obj.form_widget_error_text
        constant_keywords_dict[
            "widgets_response_text"] = language_template_obj.widgets_response_text
        constant_keywords_dict[
            "greeting_and_welcome_text"] = language_template_obj.greeting_and_welcome_text
        constant_keywords_dict["range_slider_error_messages"] = language_template_obj.range_slider_error_messages
        constant_keywords_dict["end_chat"] = language_template_obj.end_chat
        constant_keywords_dict["auto_language_detection_text"] = language_template_obj.auto_language_detection_text
        constant_keywords_dict["livechat_form_text"] = language_template_obj.livechat_form_text
        constant_keywords_dict["livechat_system_notifications"] = language_template_obj.livechat_system_notifications
        constant_keywords_dict["livechat_voicecall_notifications"] = language_template_obj.livechat_voicecall_notifications
        constant_keywords_dict["livechat_vc_notifications"] = language_template_obj.livechat_vc_notifications
        constant_keywords_dict["livechat_feedback_text"] = language_template_obj.livechat_feedback_text
        constant_keywords_dict["livechat_validation_text"] = language_template_obj.livechat_validation_text
        constant_keywords_dict["attachment_tooltip_text"] = language_template_obj.attachment_tooltip_text
        constant_keywords_dict["powered_by_text"] = language_template_obj.powered_by_text
        constant_keywords_dict["livechat_cb_notifications"] = language_template_obj.livechat_cb_notifications
        constant_keywords_dict["livechat_transcript_text"] = language_template_obj.livechat_transcript_text
        constant_keywords_dict["livechat_system_notifications_ios"] = language_template_obj.livechat_system_notifications_ios

        #  if any other field added in RequiredBotTemplate model please also add the same here
        constant_keywords_dict[
            "auto_language_detection_text"] = language_template_obj.auto_language_detection_text
        constant_keywords_dict[
            "do_not_disturb_text"] = language_template_obj.do_not_disturb_text
        constant_keywords_dict[
            "pdf_view_document_text"] = language_template_obj.pdf_view_document_text
        constant_keywords_dict[
            "frequently_asked_questions_text"] = language_template_obj.frequently_asked_questions_text
        constant_keywords_dict[
            "chat_with_text"] = language_template_obj.chat_with_text
        constant_keywords_dict[
            "query_api_failure_text"] = language_template_obj.query_api_failure_text
        # if any other field added in RequiredBotTemplate model please also add
        # the same here

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_language_constant_dict : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return constant_keywords_dict


def check_and_create_default_language_object(bot_obj, Language, RequiredBotTemplate):
    try:
        eng_lang_obj = Language.objects.filter(lang="en").first()
        eng_template_obj = RequiredBotTemplate.objects.filter(
            bot=bot_obj, language=eng_lang_obj)

        if eng_template_obj.exists():
            return eng_template_obj.first()
        else:
            return RequiredBotTemplate.objects.create(bot=bot_obj, language=eng_lang_obj)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_create_default_language_object : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


def check_and_create_required_bot_language_template_for_selected_language(bot_obj, language_obj, eng_lang_obj, RequiredBotTemplate, EasyChatTranslationCache):
    template_obj = None
    try:
        required_temp_obj = RequiredBotTemplate.objects.filter(
            bot=bot_obj, language=language_obj)

        if required_temp_obj.exists():
            req_temp_obj = required_temp_obj.first()
            ## If bot_name not present in case of bots that was created before this feature
            ## It will try to translate the bot_display_name
            ## Otherwise set bot_name as bot_display_name
            if not req_temp_obj.bot_name:
                temp_bot_name, translate_api_call_status = get_translated_text_with_api_status(
                    eng_lang_obj.bot.bot_display_name, language_obj.lang, EasyChatTranslationCache, translate_api_call_status=True)
                if translate_api_call_status:
                    req_temp_obj.bot_name = temp_bot_name
                else:
                    req_temp_obj.bot_name = req_temp_obj.bot.bot_display_name
                req_temp_obj.save()
            return req_temp_obj

        template_obj = RequiredBotTemplate.objects.create(
            bot=bot_obj, language=language_obj)

        translate_api_call_status = True

        template_obj.placeholder, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.placeholder, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.widgets_placeholder_text, translate_api_call_status = get_translated_text_with_api_status(eng_lang_obj.widgets_placeholder_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.close_button_tooltip, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.close_button_tooltip, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.minimize_button_tooltip, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.minimize_button_tooltip, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.home_button_tooltip, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.home_button_tooltip, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)

        template_obj.mic_button_tooltip, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.mic_button_tooltip, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.typing_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.typing_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.send_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.send_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.cards_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.cards_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.go_back_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.go_back_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.back_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.back_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.chat_with_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.chat_with_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.query_api_failure_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.query_api_failure_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)

        template_obj.menu_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.menu_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.minimize_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.minimize_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.maximize_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.maximize_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.dropdown_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.dropdown_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.search_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.search_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)

        template_obj.start_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.start_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.stop_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.stop_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.submit_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.submit_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.uploading_video_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.uploading_video_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)

        template_obj.cancel_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.cancel_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.file_attachment_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.file_attachment_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.file_size_limit_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.file_size_limit_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.file_upload_success_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.file_upload_success_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.feedback_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.feedback_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)

        template_obj.positive_feedback_options_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.positive_feedback_options_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.negative_feedback_options_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.negative_feedback_options_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)

        template_obj.feedback_error_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.feedback_error_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.success_feedback_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.success_feedback_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.csat_form_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.csat_form_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.csat_form_error_mobile_email_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.csat_form_error_mobile_email_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.csat_emoji_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.csat_emoji_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.date_range_picker_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.date_range_picker_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.general_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.general_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.form_widget_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.form_widget_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.choose_language, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.choose_language, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.range_slider_error_messages, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.range_slider_error_messages, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)

        template_obj.mute_tooltip_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.mute_tooltip_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.unmute_tooltip_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.unmute_tooltip_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)

        template_obj.no_result_found_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.no_result_found_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.form_widget_error_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.form_widget_error_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.widgets_response_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.widgets_response_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.greeting_and_welcome_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.greeting_and_welcome_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.end_chat, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.end_chat, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.auto_language_detection_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.auto_language_detection_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.livechat_form_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.livechat_form_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.livechat_system_notifications, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.livechat_system_notifications, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.livechat_voicecall_notifications, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.livechat_voicecall_notifications, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.livechat_vc_notifications, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.livechat_vc_notifications, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.livechat_feedback_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.livechat_feedback_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.livechat_transcript_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.livechat_transcript_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.livechat_validation_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.livechat_validation_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.attachment_tooltip_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.attachment_tooltip_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.powered_by_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.powered_by_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.livechat_cb_notifications, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.livechat_cb_notifications, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.do_not_disturb_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.do_not_disturb_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.pdf_view_document_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.pdf_view_document_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.frequently_asked_questions_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.frequently_asked_questions_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        
        template_obj.phone_number_too_long_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.phone_number_too_long_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.phone_number_too_short_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.phone_number_too_short_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.invalid_number_text, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.invalid_number_text, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.invalid_country_code, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.invalid_country_code, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.bot_name, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.bot.bot_display_name, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)
        template_obj.livechat_system_notifications_ios, translate_api_call_status = get_translated_text_with_api_status(
            eng_lang_obj.livechat_system_notifications_ios, language_obj.lang, EasyChatTranslationCache, translate_api_call_status)

        # if any filed is RequiredBotTemplate objects add here as well for
        # translation

        if not translate_api_call_status:
            template_obj.delete()
            return None

        template_obj.save()

        return template_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_required_bot_language_template_for_selected_language : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return template_obj


def update_language_template_object(template_obj, constant_keyword_dict, validation_obj):
    try:

        template_obj.placeholder = validation_obj.remo_html_from_string(
            constant_keyword_dict["placeholder"])
        template_obj.widgets_placeholder_text = validation_obj.remo_html_from_string(constant_keyword_dict["widgets_placeholder_text"])
        template_obj.close_button_tooltip = validation_obj.remo_html_from_string(
            constant_keyword_dict["close_button_tooltip"])
        template_obj.minimize_button_tooltip = validation_obj.remo_html_from_string(
            constant_keyword_dict["minimize_button_tooltip"])
        template_obj.home_button_tooltip = validation_obj.remo_html_from_string(
            constant_keyword_dict["home_button_tooltip"])
        template_obj.mic_button_tooltip = validation_obj.remo_html_from_string(
            constant_keyword_dict["mic_button_tooltip"])

        template_obj.typing_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["typing_text"])
        template_obj.send_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["send_text"])
        template_obj.cards_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["cards_text"])
        template_obj.go_back_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["go_back_text"])
        template_obj.back_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["back_text"])
        template_obj.chat_with_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["chat_with_text"])
        template_obj.query_api_failure_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["query_api_failure_text"])

        template_obj.menu_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["menu_text"])
        template_obj.minimize_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["minimize_text"])
        template_obj.maximize_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["maximize_text"])
        template_obj.dropdown_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["dropdown_text"])
        template_obj.search_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["search_text"])

        template_obj.start_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["start_text"])
        template_obj.stop_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["stop_text"])
        template_obj.submit_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["submit_text"])
        template_obj.uploading_video_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["uploading_video_text"])

        template_obj.cancel_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["cancel_text"])
        template_obj.file_attachment_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["file_attachment_text"])
        template_obj.file_size_limit_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["file_size_limit_text"])
        template_obj.file_upload_success_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["file_upload_success_text"])

        template_obj.feedback_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["feedback_text"])
        template_obj.positive_feedback_options_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["positive_feedback_options_text"])
        template_obj.negative_feedback_options_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["negative_feedback_options_text"])
        template_obj.feedback_error_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["feedback_error_text"])
        template_obj.success_feedback_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["success_feedback_text"])
        template_obj.csat_form_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["csat_form_text"])
        template_obj.csat_form_error_mobile_email_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["csat_form_error_mobile_email_text"])
        template_obj.csat_emoji_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["csat_emoji_text"])
        template_obj.date_range_picker_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["date_range_picker_text"])

        template_obj.general_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["general_text"])
        template_obj.form_widget_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["form_widget_text"])
        template_obj.choose_language = validation_obj.remo_html_from_string(
            constant_keyword_dict["choose_language"])

        template_obj.mute_tooltip_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["mute_text"])
        template_obj.unmute_tooltip_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["unmute_text"])

        template_obj.no_result_found_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["no_result_found"])
        template_obj.form_widget_error_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["form_widget_error_text"])
        template_obj.widgets_response_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["widgets_response_text"])
        template_obj.greeting_and_welcome_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["greeting_and_welcome_text"])
        template_obj.end_chat = validation_obj.remo_html_from_string(
            constant_keyword_dict["end_chat"])
        template_obj.auto_language_detection_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["auto_language_detection_text"])
        template_obj.range_slider_error_messages = validation_obj.remo_html_from_string(constant_keyword_dict["range_slider_error_messages"])

        template_obj.livechat_form_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["livechat_form_text"])
        template_obj.livechat_system_notifications = validation_obj.remo_html_from_string(
            constant_keyword_dict["livechat_system_notifications"])
        template_obj.livechat_voicecall_notifications = validation_obj.remo_html_from_string(
            constant_keyword_dict["livechat_voicecall_notifications"])
        template_obj.livechat_vc_notifications = validation_obj.remo_html_from_string(
            constant_keyword_dict["livechat_vc_notifications"])
        template_obj.livechat_feedback_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["livechat_feedback_text"])
        template_obj.livechat_transcript_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["livechat_transcript_text"])
        template_obj.livechat_validation_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["livechat_validation_text"])
        template_obj.attachment_tooltip_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["attachment_tooltip_text"])

        template_obj.auto_language_detection_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["auto_language_detection_text"])
        template_obj.powered_by_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["powered_by_text"])[0:50]

        template_obj.livechat_cb_notifications = validation_obj.remo_html_from_string(
            constant_keyword_dict["livechat_cb_notifications"])

        template_obj.do_not_disturb_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["do_not_disturb_text"])
        template_obj.pdf_view_document_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["pdf_view_document_text"])
        template_obj.frequently_asked_questions_text = validation_obj.remo_html_from_string(
            constant_keyword_dict["frequently_asked_questions_text"])
        template_obj.bot_name = validation_obj.remo_html_from_string(
            constant_keyword_dict["bot_name"]
        )
        template_obj.livechat_system_notifications_ios = validation_obj.remo_html_from_string(
            constant_keyword_dict["livechat_system_notifications_ios"])
        template_obj.save()

        return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_language_template_object : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return False


def remove_supported_langauges_from_bot(bot_obj, language_obj, BotChannel, RequiredBotTemplate):
    try:
        bot_channel_objs = BotChannel.objects.filter(bot=bot_obj)

        for bot_channel in bot_channel_objs:
            if bot_channel.languages_supported.all().filter(lang=language_obj.lang).exists():
                bot_channel.languages_supported.remove(language_obj)
                bot_channel.save()

        if bot_obj.languages_supported.all().filter(lang=language_obj.lang).exists():
            bot_obj.languages_supported.remove(language_obj)
            bot_obj.save()

        required_temp_obj = RequiredBotTemplate.objects.filter(
            bot=bot_obj, language=language_obj)

        if required_temp_obj.exists():
            required_temp_obj.delete()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("remove_supported_langauges_from_bot : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def verify_otp_for_language_configuration(email_id, user, bot_obj, entered_otp, EasyChatOTPDetails):
    try:

        otp_details_obj = EasyChatOTPDetails.objects.filter(
            user=user, bot=bot_obj, email_id=email_id)

        if not otp_details_obj.exists():
            return False

        otp_details_obj = otp_details_obj.first()

        if otp_details_obj.is_expired:
            return False

        if entered_otp != otp_details_obj.otp:
            return False

        otp_details_obj.is_expired = True
        otp_details_obj.save()

        return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("verify_otp_for_language_configuration : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return False


def get_subject_and_content_based_on_action_performed(action_performed, user, bot_obj, otp, language_obj):

    try:
        subject = "Language Configurtion Change Request"
        content = """ <span style="font-size:14px;color: #222 !important;"> Hello, <br><br>Please use the OTP code below to verify <b>""" + str(user.username) + """</b> to Configure <b>""" + language_obj.name_in_english + """</b> Language of the bot <b>""" + str(
            bot_obj.name) + """ - """ + str(bot_obj.pk) + """.</b></span> <div style="display: block; width: max-content; margin-left: 20%;"><p style="word-break: break-word; color: red; padding: 3px 10px; font-weight: bold; font-size: 24px;">""" + str(otp) + """</p></div><p style="font-size:14px;">
                    Thanks,<br>CognoAI Team
                <p>"""

        if action_performed == "add_language":
            subject = "Add Language Request"
            content = """ <span style="font-size:14px;color: #222 !important;"> Hello, <br><br>Please use the OTP code below to verify <b>""" + str(user.username) + """</b> for Adding <b>""" + language_obj.name_in_english + """</b> Language of the bot <b>""" + str(
                bot_obj.name) + """ - """ + str(bot_obj.pk) + """.</b></span> <div style="display: block; width: max-content; margin-left: 20%;"><p style="word-break: break-word; color: red; padding: 3px 10px; font-weight: bold; font-size: 24px;">""" + str(otp) + """</p></div><p style="font-size:14px;">
                    Thanks,<br>CognoAI Team
                <p>"""

        elif action_performed == "edit_language_keywords":
            subject = "Edit Language Request"
            content = """ <span style="font-size:14px;color: #222 !important;"> Hello, <br><br>Please use the OTP code below to verify <b>""" + str(user.username) + """</b> for Editing <b>""" + language_obj.name_in_english + """</b> Language of the bot <b>""" + str(
                bot_obj.name) + """ - """ + str(bot_obj.pk) + """.</b></span> <div style="display: block; width: max-content; margin-left: 20%;"><p style="word-break: break-word; color: red; padding: 3px 10px; font-weight: bold; font-size: 24px;">""" + str(otp) + """</p></div><p style="font-size:14px;">
                    Thanks,<br>CognoAI Team
                <p>"""

        elif action_performed == "delete_language":
            subject = "Delete Language Request"
            content = """ <span style="font-size:14px;color: #222 !important;"> Hello, <br><br>Please use the OTP code below to verify <b>""" + str(user.username) + """</b> for Deleting <b>""" + language_obj.name_in_english + """</b> Language of the bot <b>""" + str(
                bot_obj.name) + """ - """ + str(bot_obj.pk) + """.</b></span> <div style="display: block; width: max-content; margin-left: 20%;"><p style="word-break: break-word; color: red; padding: 3px 10px; font-weight: bold; font-size: 24px;">""" + str(otp) + """</p></div><p style="font-size:14px;">
                    Thanks,<br>CognoAI Team
                <p>"""

        return subject, content

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("def get_subject_and_content_based_on_action_performed : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return "", ""


def get_list_of_phonetic_typing_suported_languages(list_of_langs):
    try:
        supported_language_list = []
        for langugage in list_of_langs:
            supported_language_list.append(langugage[1])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("def get_dict_of_phonetic_typing_suported_languages : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return supported_language_list


def get_language_based_disclaimer_text_dict(bot_channel, phonetic_supported_languages, EasyChatTranslationCache, RequiredBotTemplate):
    disclaimer_text_dict = {}
    try:
        supported_languages = bot_channel.languages_supported.all()
        for language in phonetic_supported_languages:
            lang_code = language[1]
            lang_object = supported_languages.filter(lang=lang_code).first()
            if lang_object:
                template_obj = RequiredBotTemplate.objects.filter(
                    bot=bot_channel.bot, language=lang_object).first()

                disclaimer_text_dict[lang_code] = {
                    "disclaimer_text": get_translated_text(bot_channel.phonetic_typing_disclaimer_text, lang_code, EasyChatTranslationCache),
                    "confirm_text": template_obj.get_confirm_text(),
                    "heading_text": template_obj.get_disclaimer_text(),
                    "cancel_text": template_obj.get_cancel_text(),
                    "language_script_type": lang_object.language_script_type,
                }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("def get_dict_of_phonetic_typing_suported_languages : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return disclaimer_text_dict


def update_emoji_activity_update_dict(angry_emoji_response, happy_emoji_response, neutral_emoji_response, sad_emoji_response, emoji_bot_response_obj, emoji_activity_update):

    if emoji_bot_response_obj.emoji_angry_response_text != angry_emoji_response:
        emoji_activity_update["is_emoji_angry_response_text_updated"] = "true"

    if emoji_bot_response_obj.emoji_happy_response_text != happy_emoji_response:
        emoji_activity_update["is_emoji_happy_response_text_updated"] = "true"

    if emoji_bot_response_obj.emoji_neutral_response_text != neutral_emoji_response:
        emoji_activity_update["is_emoji_neutral_response_text_updated"] = "true"

    if emoji_bot_response_obj.emoji_sad_response_text != sad_emoji_response:
        emoji_activity_update["is_emoji_sad_response_text_updated"] = "true"

    return emoji_activity_update


# save_emoji_data(): saves emoji data saves the responses in the argument to EmojiBotResponse model
def save_emoji_data(EmojiBotResponse, bot_obj, angry_emoji_response, happy_emoji_response, neutral_emoji_response, sad_emoji_response, emoji_livechat_checkbox_value_list):

    emoji_activity_update = {
        "is_emoji_angry_response_text_updated": "false",
        "is_emoji_happy_response_text_updated": "false",
        "is_emoji_neutral_response_text_updated": "false",
        "is_emoji_sad_response_text_updated": "false",
    }

    try:
        emoji_bot_response_obj = EmojiBotResponse.objects.filter(bot=bot_obj)
        if emoji_bot_response_obj.count() == 0:
            emoji_bot_response_obj = EmojiBotResponse.objects.create(
                bot=bot_obj)
        else:
            emoji_bot_response_obj = emoji_bot_response_obj.first()

        emoji_activity_update = update_emoji_activity_update_dict(
            angry_emoji_response, happy_emoji_response, neutral_emoji_response, sad_emoji_response, emoji_bot_response_obj, emoji_activity_update)

        emoji_bot_response_obj.emoji_angry_response_text = angry_emoji_response
        emoji_bot_response_obj.emoji_happy_response_text = happy_emoji_response
        emoji_bot_response_obj.emoji_neutral_response_text = neutral_emoji_response
        emoji_bot_response_obj.emoji_sad_response_text = sad_emoji_response
        emoji_livechat_checkbox = {
            "angry": str(emoji_livechat_checkbox_value_list[0]),
            "happy": str(emoji_livechat_checkbox_value_list[1]),
            "neutral": str(emoji_livechat_checkbox_value_list[2]),
            "sad": str(emoji_livechat_checkbox_value_list[3]),
        }
        emoji_bot_response_obj.add_livechat_intent = json.dumps(
            emoji_livechat_checkbox)
        emoji_bot_response_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("def save_emoji_data : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return emoji_activity_update


def save_profanity_data(bot_obj, profanity_text_response, is_suggest_livechat_for_profanity_words_enabled, add_livechat_as_quick_recommendation, trigger_livechat_intent, ProfanityBotResponse):

    profanity_activity_update = {
        "is_profanity_response_text_updated": "false"
    }
    try:
        profanity_bot_response_obj = ProfanityBotResponse.objects.filter(
            bot=bot_obj)
        if profanity_bot_response_obj.count() == 0:
            profanity_bot_response_obj = ProfanityBotResponse.objects.create(
                bot=bot_obj)
        else:
            profanity_bot_response_obj = profanity_bot_response_obj.first()

        if profanity_bot_response_obj.profanity_response_text != profanity_text_response:
            profanity_activity_update["is_profanity_response_text_updated"] = "true"

        profanity_bot_response_obj.profanity_response_text = profanity_text_response
        profanity_bot_response_obj.is_suggest_livechat_for_profanity_words_enabled = is_suggest_livechat_for_profanity_words_enabled
        profanity_bot_response_obj.add_livechat_as_quick_recommendation = add_livechat_as_quick_recommendation
        profanity_bot_response_obj.trigger_livechat_intent = trigger_livechat_intent
        profanity_bot_response_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("def save_profanity_data : " + str(e) + " at " + str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return profanity_activity_update

"""
function: get_emojized_message
input_params:
    message: message may contain emoji in hexabyte

This function is used to convert all hexabyte emojis to text emoji.
"""


def get_emojized_message(message):
    return emoji.emojize(message, language='alias')


"""
function: check_two_minute_bot_welcome_message
input_params:
    welcome_message: general welcome message for all channels

This function is used to check if welcome message is valid or not.
"""


def check_two_minute_bot_welcome_message(welcome_message):
    status = 200
    message = ""
    try:
        welcome_message = str(BeautifulSoup(
            welcome_message, 'html.parser'))
        welcome_message = welcome_message.strip()

        if BeautifulSoup(welcome_message).text.strip() == "":
            status = 400
            message = "Welcome message is either empty or invalid"

    except Exception as e:
        status = 400
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_two_minute_bot_welcome_message: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return status, message, welcome_message


"""
function: check_two_minute_livechat_manager
input_params:
    username: user creating bot

This function is used to check if the user is livechat admin.
"""


def check_two_minute_livechat_manager(username):
    try:
        user_obj = User.objects.get(username=username)
        livechat_user = LiveChatUser.objects.filter(user=user_obj)
        if livechat_user.count() > 0:
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_two_minute_livechat_manager: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return False


"""
function: convert_to_channel_url_param
input_params:
    name: Channel name

This function is used to covert channel name to channel url param 
"""


def convert_to_channel_url_param(name):
    try:
        kebab_case_name = name[0].lower()

        if name == "GoogleHome":
            return "google-assistant"
        elif name == "GoogleRCS":
            return "google-rcs"
        elif name == "Microsoft":
            return "microsoft-teams"
        elif name == "GoogleBusinessMessages":
            return "google-buisness-messages"
        elif name in ["WhatsApp", "ET-Source", "iOS"]:
            return name.lower()

        for index in range(1, len(name)):
            if name[index].isupper():
                kebab_case_name += "-" + name[index].lower()
            else:
                kebab_case_name += name[index]
        
        return kebab_case_name
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("convert_to_channel_url_param: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: channel_name_formatter
input_params:
    name: Channel name

This function is used to covert channel name to display channel name
"""


def channel_name_formatter(name):
    try:
        if name == "GoogleHome":
            return "Google Home / Assistant"
        elif name == "GoogleBusinessMessages":
            return "Google Business Messages"
        elif name == "GoogleRCS":
            return "Google RCS"
        elif name == "ET-Source":
            return "ET Source"
        elif name == "Microsoft":
            return "Microsoft Teams"

        return name
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("channel_name_formatter: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def update_catalogue_language_tuning(bot_obj, selected_language, Language, LanguageTunedBot, EasyChatTranslationCache, WhatsappCatalogueDetails):
    try:
        language_obj = Language.objects.filter(
            lang=selected_language).first()
        lang_tuned_bot_obj = LanguageTunedBot.objects.filter(
            language=language_obj, bot=bot_obj).first()
        catalogue_object = WhatsappCatalogueDetails.objects.filter(bot=bot_obj).first()
        if not catalogue_object:
            return
        catalogue_metadata = json.loads(catalogue_object.catalogue_metadata)
        if lang_tuned_bot_obj:
            if lang_tuned_bot_obj.whatsapp_catalogue_data == "{}":
                catalogue_metadata["body_text"] = get_translated_text(
                    catalogue_metadata["body_text"], selected_language, EasyChatTranslationCache)
                if "footer_text" in catalogue_metadata:
                    catalogue_metadata["footer_text"] = get_translated_text(
                        catalogue_metadata["footer_text"], selected_language, EasyChatTranslationCache)
                if "header_text" in catalogue_metadata:
                    catalogue_metadata["header_text"] = get_translated_text(
                        catalogue_metadata["header_text"], selected_language, EasyChatTranslationCache)
                if "merge_cart_text" in catalogue_metadata:
                    catalogue_metadata["merge_cart_text"] = get_translated_text(
                        catalogue_metadata["merge_cart_text"], selected_language, EasyChatTranslationCache)
                if "sections" in catalogue_metadata:
                    for section in catalogue_metadata["sections"]:
                        catalogue_metadata["sections"][section]["section_title"] = get_translated_text(
                            catalogue_metadata["sections"][section]["section_title"], selected_language, EasyChatTranslationCache)
                lang_tuned_bot_obj.whatsapp_catalogue_data = json.dumps(catalogue_metadata)
                lang_tuned_bot_obj.save(update_fields=['whatsapp_catalogue_data'])
        else:
            catalogue_metadata["body_text"] = get_translated_text(
                catalogue_metadata["body_text"], selected_language, EasyChatTranslationCache)
            if "footer_text" in catalogue_metadata:
                catalogue_metadata["footer_text"] = get_translated_text(
                    catalogue_metadata["footer_text"], selected_language, EasyChatTranslationCache)
            if "header_text" in catalogue_metadata:
                catalogue_metadata["header_text"] = get_translated_text(
                    catalogue_metadata["header_text"], selected_language, EasyChatTranslationCache)
            if "merge_cart_text" in catalogue_metadata:
                catalogue_metadata["merge_cart_text"] = get_translated_text(
                    catalogue_metadata["merge_cart_text"], selected_language, EasyChatTranslationCache)
            if "sections" in catalogue_metadata:
                for section in catalogue_metadata["sections"]:
                    catalogue_metadata["sections"][section]["section_title"] = get_translated_text(
                        catalogue_metadata["sections"][section]["section_title"], selected_language, EasyChatTranslationCache)
            lang_tuned_bot_obj = LanguageTunedBot.objects.create(
                bot=bot_obj, language=language_obj, whatsapp_catalogue_data=json.dumps(catalogue_metadata))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_catalogue_language_tuning: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def check_and_update_catalogue_fine_tuning(bot_obj, activity_update, catalogue_via, catalogue_metadata, WhatsappCatalogueDetails, EasyChatTranslationCache):
    try:
        catalogue_obj = WhatsappCatalogueDetails.objects.filter(
            bot=bot_obj).first()
        if not catalogue_obj:
            return activity_update
        current_catalogue_metadata = json.loads(
            catalogue_obj.catalogue_metadata)
        lang_tuned_bot_objs = LanguageTunedBot.objects.filter(
            bot=bot_obj)
        if current_catalogue_metadata["merge_cart_enabled"] != catalogue_metadata["merge_cart_enabled"]:
            for lang_tune_obj in lang_tuned_bot_objs:
                tuned_catalogue_metadata = json.loads(
                    lang_tune_obj.whatsapp_catalogue_data)
                tuned_catalogue_metadata["merge_cart_enabled"] = catalogue_metadata["merge_cart_enabled"]
                lang_tune_obj.whatsapp_catalogue_data = json.dumps(
                    tuned_catalogue_metadata)
                lang_tune_obj.save(update_fields=["whatsapp_catalogue_data"])

        if catalogue_obj.catalogue_type != catalogue_via:
            force_autofix_catalogue_fine_tuning(
                catalogue_metadata, lang_tuned_bot_objs, EasyChatTranslationCache)
            return activity_update
        if current_catalogue_metadata["catalogue_type"] != catalogue_metadata["catalogue_type"]:
            force_autofix_catalogue_fine_tuning(
                catalogue_metadata, lang_tuned_bot_objs, EasyChatTranslationCache)
            return activity_update
        if "header_text" in current_catalogue_metadata and "header_text" in catalogue_metadata:
            if current_catalogue_metadata["header_text"] != catalogue_metadata["header_text"]:
                activity_update["is_catalogue_header_changed"] = "true"
        if current_catalogue_metadata["body_text"] != catalogue_metadata["body_text"]:
            activity_update["is_catalogue_body_changed"] = "true"
        if "footer_text" in current_catalogue_metadata and "footer_text" in catalogue_metadata:
            if current_catalogue_metadata["footer_text"] != catalogue_metadata["footer_text"]:
                activity_update["is_catalogue_footer_changed"] = "true"
        elif "footer_text" in current_catalogue_metadata and "footer_text" not in catalogue_metadata:
            activity_update["is_catalogue_footer_changed"] = "true"
        elif "footer_text" not in current_catalogue_metadata and "footer_text" in catalogue_metadata:
            activity_update["is_catalogue_footer_changed"] = "true"
        section_title_checked = False
        if current_catalogue_metadata["merge_cart_text"] != catalogue_metadata["merge_cart_text"]:
            activity_update["is_catalogue_merge_cart_text_changed"] = "true"
        if "sections" in current_catalogue_metadata and "sections" in catalogue_metadata:
            for lang_tuned_obj in lang_tuned_bot_objs:
                if lang_tuned_obj.whatsapp_catalogue_data == "{}":
                    continue
                language_tuned_catalogue_data = json.loads(
                    lang_tuned_obj.whatsapp_catalogue_data)
                section_titles_updated = []
                for section in catalogue_metadata["sections"]:
                    if section not in language_tuned_catalogue_data["sections"]:
                        language_tuned_catalogue_data["sections"][section] = copy.deepcopy(
                            catalogue_metadata["sections"][section])
                        language_tuned_catalogue_data["sections"][section]["section_title"] = get_translated_text(
                            catalogue_metadata["sections"][section]["section_title"], lang_tuned_obj.language.lang, EasyChatTranslationCache)
                        continue
                    else:
                        language_tuned_catalogue_data["sections"][section][
                            "product_ids"] = catalogue_metadata["sections"][section]["product_ids"]
                    if not section_title_checked and catalogue_metadata["sections"][section]["section_title"] != current_catalogue_metadata["sections"][section]["section_title"]:
                        section_titles_updated.append(section)
                sections_to_be_deleted = []
                for section in language_tuned_catalogue_data["sections"]:
                    if section not in catalogue_metadata["section_ordering"]:
                        sections_to_be_deleted.append(section)
                for section_id in sections_to_be_deleted:
                    del language_tuned_catalogue_data["sections"][section_id]
                language_tuned_catalogue_data["section_ordering"] = catalogue_metadata["section_ordering"]
                lang_tuned_obj.whatsapp_catalogue_data = json.dumps(
                    language_tuned_catalogue_data)
                lang_tuned_obj.save(update_fields=["whatsapp_catalogue_data"])
                if not section_title_checked and section_titles_updated:
                    activity_update["catalogue_section_titles_updated"] = section_titles_updated

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_update_catalogue_fine_tuning: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return activity_update


def mark_block_mis_objs_session(session_id):
    try:
        filter_end_date = datetime.datetime.now().date()
        filter_start_date = filter_end_date - datetime.timedelta(1)
        MISDashboard.objects.filter(creation_date__gte=filter_start_date, creation_date__lte=filter_end_date, session_id=session_id).update(is_session_blocked=True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("mark_block_mis_objs_session: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


##  6 return values
##  ok -> If message not triggering block or warning
##  query_warning -> If message is triggering query warning 
##  query_block -> If message is triggering query block 
##  keyword_warning -> If message is triggering keyword warning 
##  keyword_block -> If message is triggering keyword block 
##  ignore -> If message should be ignored


def check_query_for_warning_or_block(bot_id, session_id, query):
    log_param = {'AppName': 'EasyChat', 'user_id': 'None',
                    'source': 'None', 'channel': 'None', 'bot_id': 'None'}
    try:
        to_return = "ok"
        update_fields = []
        bot_obj = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()
        block_config_obj = BlockConfig.objects.filter(bot=bot_obj).first()
        user_session_health_obj = UserSessionHealth.objects.filter(session_id=session_id).last()

        ## If the Block spam user is enabled and block based on user queries is enabled 
        if block_config_obj.is_block_spam_user_enabled and block_config_obj.is_block_based_on_user_queries_enabled:
            user_session_health_obj.message_queries_count += 1
            update_fields.append("message_queries_count")
            if user_session_health_obj.message_queries_count == block_config_obj.user_query_warning_thresold:
                to_return = "query_warning"
            elif block_config_obj.user_query_block_thresold > user_session_health_obj.message_queries_count > block_config_obj.user_query_warning_thresold:
                to_return = "ignore"
            elif user_session_health_obj.message_queries_count == block_config_obj.user_query_block_thresold:
                user_session_health_obj.block_type = "spam_message"
                user_session_health_obj.is_blocked = True
                user_session_health_obj.block_time = timezone.now()
                user_session_health_obj.unblock_time = timezone.now() + timezone.timedelta(
                    hours=block_config_obj.user_query_block_duration)
                update_fields.extend([
                    "block_type", "is_blocked",
                    "block_time", "unblock_time"
                ])
                to_return = "query_block"
                update_mis_objs_thread = threading.Thread(target=mark_block_mis_objs_session, args=(user_session_health_obj.session_id,))
                update_mis_objs_thread.start()

        ## If the Block spam user is enabled and block based on spam keywords is enabled 
        if block_config_obj.is_block_spam_user_enabled and block_config_obj.is_block_based_on_spam_keywords_enabled:
            query_keywords = query.split()
            is_query_keywords_in_spam_keywords = False
            detected_blocked_keywords = ""
            spam_keywords = block_config_obj.spam_keywords.lower().split(",") if block_config_obj.spam_keywords.strip() else []
            for query_keyword in query_keywords:
                if query_keyword.lower() in spam_keywords:
                    is_query_keywords_in_spam_keywords = True
                    if user_session_health_obj.blocked_spam_keywords or detected_blocked_keywords:
                        detected_blocked_keywords += "," + query_keyword
                    else:
                        detected_blocked_keywords += query_keyword
            
            if is_query_keywords_in_spam_keywords:
                user_session_health_obj.spam_keywords_count += 1
                user_session_health_obj.blocked_spam_keywords += detected_blocked_keywords
                update_fields.extend(["spam_keywords_count", "blocked_spam_keywords"])
                if user_session_health_obj.spam_keywords_count == block_config_obj.spam_keywords_warning_thresold:
                    if "block" not in to_return:
                        to_return = "keyword_warning"
                elif block_config_obj.spam_keywords_block_thresold > user_session_health_obj.spam_keywords_count > block_config_obj.spam_keywords_warning_thresold:
                    if "block" not in to_return:
                        to_return = "ignore"
                elif user_session_health_obj.spam_keywords_count == block_config_obj.spam_keywords_block_thresold:
                    user_session_health_obj.block_type = "keyword"
                    user_session_health_obj.is_blocked = True
                    user_session_health_obj.block_time = timezone.now()
                    user_session_health_obj.unblock_time = timezone.now() + timezone.timedelta(
                        hours=block_config_obj.spam_keywords_block_duration)
                    update_fields.extend([
                        "block_type", "is_blocked",
                        "block_time", "unblock_time"
                    ])
                    to_return = "keyword_block"
                    update_mis_objs_thread = threading.Thread(target=mark_block_mis_objs_session, args=(user_session_health_obj.session_id))
                    update_mis_objs_thread.start()
        
        user_session_health_obj.save(update_fields=update_fields)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_query_for_warning_or_block: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
    return to_return


def get_paginator_meta_data(data_objs, no_of_records_per_page, page):

    pagination_metadata = DEFAULT_PAGINATION_METADATA
    try:
        total_data_objs = len(data_objs)

        paginator = Paginator(data_objs, no_of_records_per_page)
        
        try:
            paginated_data_objs = paginator.page(page)
        except PageNotAnInteger:
            paginated_data_objs = paginator.page(1)
        except EmptyPage:
            paginated_data_objs = paginator.page(paginator.num_pages)

        if page != None:
            start_point = no_of_records_per_page * (int(page) - 1) + 1
            end_point = min(no_of_records_per_page *
                            int(page), total_data_objs)
            if start_point > end_point:
                start_point = max(
                    end_point - len(paginated_data_objs) + 1, 1)
        else:
            start_point = 1
            end_point = min(no_of_records_per_page, total_data_objs)

        start_point = min(start_point, end_point)

        pagination_range = paginated_data_objs.paginator.page_range

        has_next = paginated_data_objs.has_next()
        has_previous = paginated_data_objs.has_previous()
        has_other_pages = paginated_data_objs.has_other_pages()
        next_page_number = -1
        previous_page_number = -1

        if has_next:
            next_page_number = paginated_data_objs.next_page_number()
        if has_previous:
            previous_page_number = paginated_data_objs.previous_page_number()

        pagination_metadata = {
            'total_count': total_data_objs,
            'start_point': start_point,
            'end_point': end_point,
            'page_range': [pagination_range.start, pagination_range.stop],
            'has_next': has_next,
            'has_previous': has_previous,
            'next_page_number': next_page_number,
            'previous_page_number': previous_page_number,
            'number': paginated_data_objs.number,
            'num_pages': paginated_data_objs.paginator.num_pages,
            'has_other_pages': has_other_pages,
        }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_paginator_meta_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    
    return pagination_metadata


def recurse_tree_save(Tree, tree_obj, tree_pk, flow):
    try:
        sub_flow = flow[str(tree_pk)]

        tree_obj.children.clear()

        tree_obj.is_last_tree = False
        if not sub_flow.keys():
            tree_obj.is_last_tree = True
        tree_obj.save(update_fields=["is_last_tree"])

        for child_node in sub_flow.keys():
            new_tree_obj = Tree.objects.filter(pk=int(child_node), is_deleted=False).first()
            recurse_tree_save(Tree, new_tree_obj, child_node, sub_flow)
            tree_obj.children.add(new_tree_obj)
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error recurse_tree_save %s %s",
                        str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def force_autofix_catalogue_fine_tuning(catalogue_metadata, lang_tuned_bot_objs, EasyChatTranslationCache):
    try:
        for lang_tune_obj in lang_tuned_bot_objs:
            temp_catalogue_metadata = copy.deepcopy(catalogue_metadata)
            temp_catalogue_metadata["body_text"] = get_translated_text(
                catalogue_metadata["body_text"], lang_tune_obj.language.lang, EasyChatTranslationCache)
            if "footer_text" in catalogue_metadata:
                temp_catalogue_metadata["footer_text"] = get_translated_text(
                    catalogue_metadata["footer_text"], lang_tune_obj.language.lang, EasyChatTranslationCache)
            if "header_text" in catalogue_metadata:
                temp_catalogue_metadata["header_text"] = get_translated_text(
                    catalogue_metadata["header_text"], lang_tune_obj.language.lang, EasyChatTranslationCache)
            if "sections" in catalogue_metadata:
                for section in catalogue_metadata["sections"]:
                    temp_catalogue_metadata["sections"][section]["section_title"] = get_translated_text(
                        catalogue_metadata["sections"][section]["section_title"], lang_tune_obj.language.lang, EasyChatTranslationCache)
            if "merge_cart_text" in catalogue_metadata:
                temp_catalogue_metadata["merge_cart_text"] = get_translated_text(
                    catalogue_metadata["merge_cart_text"], lang_tune_obj.language.lang, EasyChatTranslationCache)

            lang_tune_obj.whatsapp_catalogue_data = json.dumps(
                temp_catalogue_metadata)
            lang_tune_obj.save(update_fields=['whatsapp_catalogue_data'])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("force_autofix_catalogue_fine_tuning: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def auto_fix_catalogue_texts_tuning(text_name, bot_channel, EasyChatTranslationCache):
    try:
        bot_obj = bot_channel.bot
        lang_objs = LanguageTunedBot.objects.filter(
            bot=bot_obj)
        catalogue_obj = WhatsappCatalogueDetails.objects.filter(
            bot=bot_obj).first()
        if catalogue_obj:
            catalogue_metadata = json.loads(
                catalogue_obj.catalogue_metadata)
            for lang_tune_obj in lang_objs:
                tuned_catalogue_metadata = lang_tune_obj.whatsapp_catalogue_data
                if tuned_catalogue_metadata == "{}":
                    continue
                tuned_catalogue_metadata = json.loads(
                    tuned_catalogue_metadata)
                if text_name in catalogue_metadata and text_name in tuned_catalogue_metadata:
                    tuned_catalogue_metadata[text_name] = get_translated_text(
                        catalogue_metadata[text_name], lang_tune_obj.language.lang, EasyChatTranslationCache)

                lang_tune_obj.whatsapp_catalogue_data = json.dumps(
                    tuned_catalogue_metadata)
                lang_tune_obj.save(
                    update_fields=["whatsapp_catalogue_data"])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("auto_fix_catalogue_texts_tuning: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def save_intent_category(data, user_obj, intent_obj, Category, save_audit_trail):
    try:
        category_obj_pk = data["category_obj_pk"]

        change_data = []
        if category_obj_pk != "" or category_obj_pk != None:
            category_obj = Category.objects.filter(
                pk=int(category_obj_pk)).first()
            if intent_obj.category != None and intent_obj.category.name != category_obj.name:
                change_data.append({
                    "heading": "Category changed",
                    "old_data": intent_obj.category.name,
                    "new_data": category_obj.name
                })
            elif intent_obj.category == None:
                change_data.append({
                    "heading": "Category Added",
                    "old_data": "",
                    "new_data": category_obj.name
                })
            intent_obj.category = category_obj
            intent_obj.save(update_fields=["category"])

        if intent_obj and len(change_data):
            audit_trail_data = json.dumps({
                "intent_pk": intent_obj.pk,
                "change_data": change_data
            })
            save_audit_trail(
                user_obj, MODIFY_INTENT_ACTION, audit_trail_data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_intent_category %s %s",
                        str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def update_multilingual_bot_name(bot_obj, RequiredBotTemplate, EasyChatTranslationCache):
    try:
        language_bot_template_objs = RequiredBotTemplate.objects.filter(bot=bot_obj)
        for language_bot_template_obj in language_bot_template_objs:
            language_bot_template_obj.bot_name, _ = get_translated_text_with_api_status(bot_obj.name, language_bot_template_obj.language.lang, EasyChatTranslationCache, True)
            language_bot_template_obj.save(update_fields=['bot_name'])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error update_multilingual_bot_name %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
