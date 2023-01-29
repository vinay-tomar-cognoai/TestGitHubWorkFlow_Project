from django.db.models import Q, F, Count, Avg
from django.conf import settings

import requests
import json
import re
import logging
import sys
import emoji
import copy

from EasyChatApp.models import Bot, BotInfo, Profile, Data, Intent, Language, LanguageTunedBotChannel, EasyChatTranslationCache, Channel, BotChannel, LanguageTunedBot, RequiredBotTemplate, WhatsAppMenuSection
from EasyChatApp.utils_bot import get_emojized_message, process_response_based_on_language, get_translated_text, check_and_create_channel_details_language_tuning_objects, check_and_create_language_tuned_bot_objects, check_and_create_bot_language_template_obj
from EasyChatApp.constants import *
from EasyChatApp.telegram.utils_telegram import send_text_message_to_telegram
from EasyChatApp.utils_execute_query import execute_query, set_user, save_data
from EasyChatApp.rcs_business_messaging import messages
from EasyChatApp.utils_facebook import send_facebook_message, send_recommendations_quick_replies, send_recommendations_carousel as send_facebook_recommendations_carousel
from EasyChatApp.utils_instagram import send_instagram_message, send_recommendations_carousel as send_instagram_recommendations_carousel
from EasyChatApp.utils_google_buisness_messages import create_language_choice_list, send_message_with_suggestions as send_gbm_message_with_suggestions, send_text_message as send_gbm_text_message
from EasyChatApp.utils_twitter import process_recommendations_for_quick_reply, send_twitter_message
from EasyChatApp.utils_alexa import build_alexa_speech_response, process_string_for_google_alexa
from EasyChatApp.utils_google import build_google_home_text_speech_response, build_google_home_visual_selection_list_select
from EasyChatApp.utils_microsoft import get_recommendations as get_mst_recommendations
from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.utils_viber import send_text_to_viber, send_recomendations_to_viber
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
log_param = {'AppName': 'EasyChat', 'user_id': 'None',
             'source': 'None', 'channel': 'None', 'bot_id': 'None'}


def initialize_intent_name_lists(list_of_objs, channel_obj):
    try:
        name_list = []
        for intent_obj_pk in list_of_objs:
            intent_objs = Intent.objects.filter(
                pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
            if intent_objs:
                intent_obj = intent_objs[0]
                small_talk = intent_obj.is_small_talk
                if small_talk == False:
                    name_list.append({
                        "is_selected": True,
                        "intent_name": intent_obj.name,
                        "intent_pk": intent_obj.pk
                    })
        return name_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("initialize_lists %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})
        return []


def append_all_intent_objects_list(list_to_be_checked, updated_list, selected_bot_obj, channel_obj):
    try:
        all_intent_objs = Intent.objects.filter(
            bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)
        for intent_obj in all_intent_objs:
            if str(intent_obj.pk) not in list_to_be_checked:
                small_talk = intent_obj.is_small_talk
                if small_talk == False:
                    updated_list.append({
                        "is_selected": False,
                        "intent_name": intent_obj.name,
                        "intent_pk": intent_obj.pk
                    })

        return updated_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("append_all_intent_objects_list %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})
        return updated_list


def get_languange_tuned_object(selected_language, selected_bot_obj, channel):
    try:
        bot_channel_obj = BotChannel.objects.filter(
            bot=selected_bot_obj, channel=channel).first()
        language_tuned_object = bot_channel_obj
        if selected_language != "en":
            response = {}
            response["welcome_message"] = bot_channel_obj.welcome_message
            response["failure_message"] = bot_channel_obj.failure_message
            response["authentication_message"] = bot_channel_obj.authentication_message
            create_language_tuned_object = True
            check_and_create_channel_details_language_tuning_objects(
                response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
            lang_obj = Language.objects.filter(lang=selected_language).first()
            language_tuned_object = LanguageTunedBotChannel.objects.filter(
                language=lang_obj, bot_channel=bot_channel_obj)[0]

        return language_tuned_object

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("assign_values_if_lang_not_en %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
        pass


def language_specific_action(data, channel, bot, welcome_message, failure_message, authentication_message):
    try:
        is_language_auto_detection_enabled = data.get(
            "is_language_auto_detection_enabled", False)
        is_enable_choose_language_flow_enabled_for_welcome_response = data.get(
            "is_enable_choose_language_flow_enabled_for_welcome_response", False)
        selected_supported_languages = data["selected_supported_languages"]
        check_and_create_bot_language_template_obj(
            bot, selected_supported_languages, RequiredBotTemplate, Language)
        channel.languages_supported.clear()
        for selected_lang in selected_supported_languages:
            lang_obj = Language.objects.filter(lang=selected_lang).first()
            channel.languages_supported.add(lang_obj)
        activity_update = json.loads(channel.activity_update)
        is_welcome_message_updated = "false"
        if channel.welcome_message != welcome_message:
            is_welcome_message_updated = "true"
        channel.welcome_message = welcome_message
        is_failure_message_updated = "false"
        if channel.failure_message != failure_message:
            is_failure_message_updated = "true"
        channel.failure_message = failure_message
        is_authentication_message_updated = "false"
        if channel.authentication_message != authentication_message:
            is_authentication_message_updated = "true"
        channel.authentication_message = authentication_message
        activity_update[
            "is_welcome_message_updated"] = is_welcome_message_updated
        activity_update[
            "is_failure_message_updated"] = is_failure_message_updated
        activity_update[
            "is_authentication_message_updated"] = is_authentication_message_updated
        channel.activity_update = json.dumps(activity_update)
        channel.is_language_auto_detection_enabled = is_language_auto_detection_enabled
        channel.is_enable_choose_language_flow_enabled_for_welcome_response = is_enable_choose_language_flow_enabled_for_welcome_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("language_specific_action: %s at %s", str(e),
                     str(exc_tb.tb_lineno), extra=log_param)


def get_language_change_response(bot_id, sender, bot, channel_name, REVERSE_CHANNEL_MESSAGE_DICT):
    try:
        bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
        channel = Channel.objects.filter(name=channel_name)[0]
        profile_obj = Profile.objects.filter(
            user_id=str(sender), bot=bot).first()
        selected_language = profile_obj.selected_language.lang if profile_obj.selected_language else "en"
        language_script_type = profile_obj.selected_language.language_script_type if profile_obj.selected_language else "ltr"

        hand_emoji_direction = ":point_right:"
        if language_script_type == "rtl":
            hand_emoji_direction = ":point_left:"

        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()

        language_key_list = []
        if languages_supported.count() > 1:
            please_choose_str = "Please choose your language"
            please_choose_translated = get_translated_text(please_choose_str, selected_language, EasyChatTranslationCache)
            recommendation_str = please_choose_translated + "\n\n"
            for language in languages_supported:
                language_key_list.extend([f"*_{str(language.lang)}_* " + hand_emoji_direction + ""])
                REVERSE_CHANNEL_MESSAGE_DICT[str(
                    language.lang).lower().strip()] = str(language.lang)
                single_language_text = "Please type {} {/language_name/}"
                tarnslated_text = get_translated_text(
                    single_language_text, selected_language, EasyChatTranslationCache)
                tarnslated_text = tarnslated_text.replace("{/language_name/}", str(language.display))
                tarnslated_text += "\n\n"
                recommendation_str += tarnslated_text
            
            tarnslated_text = recommendation_str
            tarnslated_text = tarnslated_text.format(*language_key_list)

        return tarnslated_text, REVERSE_CHANNEL_MESSAGE_DICT
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_language_change_response: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return "", REVERSE_CHANNEL_MESSAGE_DICT


def is_change_language_triggered(sender, bot_obj):
    try:
        user = Profile.objects.filter(user_id=sender, bot=bot_obj).first()

        data_obj = Data.objects.filter(
            user=user, variable="CHANGE_LANGUAGE_TRIGGERED")

        if not data_obj.exists():
            return False

        data_obj = data_obj.first()

        if data_obj.get_value() == 'true':
            data_obj.value = False
            data_obj.save()
            return True

        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_change_language_triggered: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return False


def get_languages(bot_id, channel_name):
    try:
        bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
        logger.info("bot id in  get_language_change response " +
                    str(bot_id), extra=log_param)
        channel = Channel.objects.filter(name=channel_name).first()
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel).first()
        languages_supported = bot_channel_obj.languages_supported.all()

        languages_list = []
        if languages_supported.count() > 1:
            languages = list(languages_supported.values('lang', 'display'))

            for language in languages:
                languages_list.append({
                    "value": language["lang"],
                    "display": language["display"]
                })

        return languages_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_languages: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return []


def send_language_change_response(user_id, bot_id, chat_id, bot_obj, channel):
    profile_obj = Profile.objects.filter(
        user_id=str(user_id), bot=bot_obj).first()

    REVERSE_CHANNEL_MESSAGE_DICT = {}
    data_obj = Data.objects.filter(
        user=profile_obj, variable="REVERSE_TELEGRAM_MESSAGE_DICT").first()
    if data_obj:
        REVERSE_CHANNEL_MESSAGE_DICT = json.loads(str(data_obj.get_value()))
    is_language_change_required = False

    language_str, REVERSE_CHANNEL_MESSAGE_DICT = get_language_change_response(
        bot_id, user_id, bot_obj, channel, REVERSE_CHANNEL_MESSAGE_DICT)

    if language_str != "":
        language_str = get_emojized_message(language_str)
        if channel == "Telegram":
            for char in "[]()~`>#+-=|{}.!":
                language_str = language_str.replace(char, "\\" + char)
            send_status = send_text_message_to_telegram(
                bot_id, language_str, chat_id)
        logger.info("Is change language response sent: %s",
                    str(send_status), extra=log_param)

        set_user(user_id, channel.lower(), "src", channel, bot_id)
        save_data(profile_obj, json_data={"CHANGE_LANGUAGE_TRIGGERED": True},
                  src="None", channel=channel, bot_id=bot_id, is_cache=True)

        logger.info(f"REVERSE_{channel.upper()}_MESSAGE_DICT: %s", str(
            REVERSE_CHANNEL_MESSAGE_DICT), extra=log_param)
        save_data(profile_obj, json_data={f"REVERSE_{channel.upper()}_MESSAGE_DICT": REVERSE_CHANNEL_MESSAGE_DICT},
                  src="None", channel=channel, bot_id=bot_id, is_cache=True)

        response["status_code"] = 200
        response["status_message"] = "Request processed successfully."
        is_language_change_required = True
    return response, is_language_change_required


def change_language_response_required(sender, bot_id, bot, channel_name):
    try:
        bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
        channel = Channel.objects.filter(name=channel_name)[0]
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()

        profile_obj = Profile.objects.filter(
            user_id=str(sender), bot=bot).first()

        if languages_supported.count() == 1:
            profile_obj.selected_language = languages_supported[0]
            profile_obj.save()

        if profile_obj.selected_language:
            return False

        if not bot_channel_obj.is_enable_choose_language_flow_enabled_for_welcome_response:
            default_lang = languages_supported.filter(lang="en").first()
            profile_obj.selected_language = default_lang
            profile_obj.save()
            return False

        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("change_language_response_required: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return False


def get_language_selected_by_user(user_id, bot_id, bot_obj, message, channel):
    try:
        profile_obj = Profile.objects.filter(
            user_id=str(user_id), bot=bot_obj).first()
        selected_language = profile_obj.selected_language

        if not selected_language:
            selected_language = "en"
        else:
            selected_language = selected_language.lang
            languages_supported = Bot.objects.filter(
                pk=int(bot_id)).first().languages_supported
            languages_supported = languages_supported.filter(
                lang=selected_language)

            if not languages_supported:
                selected_language = "en"
    except Exception:
        selected_language = 'en'
        user = set_user(user_id, message, "None", channel, bot_id)
        languages_supported = Language.objects.filter(lang="en").first()
        if user.selected_language == None:
            user.selected_language = languages_supported
            user.save()

    return selected_language


def send_after_language_changed_response(user_id, bot_id, chat_id, channel, bot_obj, message, service_account_location, page_access_token, bot_representative, twitter_channel_detail_obj, sender):
    response = {}
    try:
        profile_obj = Profile.objects.filter(
            user_id=str(user_id), bot=bot_obj).first()
        channel_obj = Channel.objects.filter(name=channel).first()
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel_obj).first()
        languages_supported = bot_channel_obj.languages_supported.all()
        lang_codes = list(languages_supported.values('lang'))
        is_supported = False

        for code in lang_codes:
            if code["lang"].lower().strip() == message.lower().strip():
                is_supported = True
                break

        lang_obj = Language.objects.filter(lang=message).first()
        data_obj = Data.objects.filter(
            user=profile_obj, variable="CHANGE_LANGUAGE_TRIGGERED").first()

        if not lang_obj or not is_supported:
            if data_obj:
                data_obj.value = False
                data_obj.save()
            return None

        profile_obj.selected_language = lang_obj
        profile_obj.save()

        text_message = "You have selected " + \
            str(lang_obj.display if lang_obj else "English") + \
            ", If you want to change your language again please type"

        text_message = get_translated_text(
            text_message, lang_obj.lang if lang_obj else "en", EasyChatTranslationCache)
        text_message = text_message + ' "Change Language"'
        if channel == "Telegram":
            for char in "[]()~`>#+-=|{}.!":
                text_message = text_message.replace(char, "\\" + char)
            send_text_message_to_telegram(
                bot_id, text_message, chat_id)
        elif channel == "GoogleRCS":
            text_message = messages.TextMessage(text_message)
            cluster = messages.MessageCluster().append_message(text_message)
            cluster.send_to_msisdn(sender, service_account_location)
        elif channel == "Facebook":
            send_facebook_message(sender, text_message, page_access_token)
        elif channel == "Instagram":
            send_instagram_message(sender, text_message, page_access_token)
        elif channel == "GoogleBusinessMessages":
            send_gbm_text_message(text_message, user_id,
                                  bot_representative, service_account_location)
        elif channel == "Twitter":
            send_twitter_message(
                twitter_channel_detail_obj, sender, text_message)
        elif channel == "Alexa":
            return build_alexa_speech_response(text_message)
        elif channel == "GoogleHome":
            speech_response = process_string_for_google_alexa(text_message)
            webhook_response = copy.deepcopy(DEFAULT_WEBHOOK_RESPONSE)
            webhook_response_text_speech_response = build_google_home_text_speech_response(
                text_message, speech_response)
            webhook_response["payload"]["google"]["richResponse"]["items"] = [
                webhook_response_text_speech_response]
            return webhook_response
        elif channel == "Microsoft":
            response["data"] = {
                "text_response_list": [text_message],
                "videos": [],
                "image_urls": [],
                "recom_list": [],
                "cards_list": [],
                "choices_list": [],
            }
        elif channel == "Viber":
            send_text_to_viber(sender, user_id, bot_obj, text_message)
        response["status_code"] = 200
        response["status_message"] = "Request processed successfully."

    except Exception as e:
        logger.error("is_change_language_triggered: %s at %s",
                     str(e), extra=log_param)

    return response


def process_language_change_or_get_response(user_id, bot_id, chat_id, bot_name, channel, channel_params, message, bot_obj, service_account_location=None, page_access_token=None, bot_representative=None, twitter_channel_detail_obj=None, sender=None):
    #   CHECK IF CHANGE LANGUAGE WAS TRIGGERED
    try:
        bot_response = None
        user_obj = Profile.objects.filter(user_id=user_id, bot=bot_obj).first()
        if is_change_language_triggered(user_id, bot_obj) and user_obj and not user_obj.livechat_connected:
            response = send_after_language_changed_response(user_id, bot_id, chat_id, channel, bot_obj, message,
                                                            service_account_location, page_access_token, bot_representative, twitter_channel_detail_obj, sender)
            if response is not None:
                return True, response

        #   CHECK IF CHANGE LANGUAGE IS CALLED
        lang_message = re.sub(' +', ' ', message)
        language_change_query_list = [
            "change language", "change the language", "language change", "switch language"]
        language_change_query_list += list(EasyChatTranslationCache.objects.filter(
            input_text__iexact="change language").values_list('translated_data', flat=True).distinct())
        if isinstance(lang_message, str) and lang_message.lower().strip() in language_change_query_list and user_obj and not user_obj.livechat_connected:
            if channel == "GoogleRCS":
                response, is_different_language_selected = send_rcs_language_choices(
                    bot_id, user_id, service_account_location, sender)
            elif channel == "Facebook":
                response, is_different_language_selected = send_facebook_language_choices(
                    bot_id, user_id, page_access_token, sender)
            elif channel == "Instagram":
                response, is_different_language_selected = send_instagram_language_choices(
                    bot_id, user_id, page_access_token, sender)
            elif channel == "GoogleBusinessMessages":
                response, is_different_language_selected = send_gbm_language_choices(
                    bot_id, user_id, service_account_location, bot_representative)
            elif channel == "Twitter":
                response, is_different_language_selected = send_twitter_language_choices(
                    bot_id, user_id, twitter_channel_detail_obj, sender)
            elif channel == "Alexa":
                response, is_different_language_selected = send_alexa_language_choices(bot_id, user_id)
            elif channel == "GoogleHome":
                response, is_different_language_selected = send_google_home_language_choices(bot_id, user_id)
            elif channel == "Microsoft":
                response, is_different_language_selected = send_mst_language_choices(bot_id, user_id, sender)
            elif channel == "Telegram":
                response, is_different_language_selected = send_language_change_response(
                    user_id, bot_id, chat_id, bot_obj, channel)
            elif channel == "Viber":
                response, is_different_language_selected = send_viber_language_choices(bot_id, user_id, sender)
            if is_different_language_selected:
                return True, response

        #   GET LANGUAGE SELECTED BY USER
        selected_language = get_language_selected_by_user(
            user_id, bot_id, bot_obj, message, channel)

        bot_response = execute_query(
            user_id, bot_id, bot_name, message, selected_language, channel, channel_params, message)

        if "is_bot_switched" in bot_response:
            profile_obj = Profile.objects.filter(
                user_id=user_id, bot=bot_obj).first()
            profile_obj.selected_language = Language.objects.filter(
                lang="en").first()
            profile_obj.save()

        if "language_src" in bot_response["response"]:
            selected_language = bot_response["response"]["language_src"]
        else:
            bot_response["response"]["language_src"] = selected_language

        is_response_to_be_language_processed = True

        if "is_response_to_be_language_processed" in bot_response["response"]:
            is_response_to_be_language_processed = bot_response[
                "response"]["is_response_to_be_language_processed"]

        if selected_language != "en" and is_response_to_be_language_processed:
            bot_response = process_response_based_on_language(
                bot_response, selected_language, EasyChatTranslationCache)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("process_language_change_or_get_response: %s at %s", str(e), str(exc_tb.tb_lineno), extra=log_param)

    return False, bot_response


def get_message_from_reverse_channel_mapping(user_message, user, channel):
    message = None
    try:
        logger.info(" === Reverse Message mapping === ", extra=log_param)
        data_obj = Data.objects.filter(
            user=user, variable=f"REVERSE_{channel.upper()}_MESSAGE_DICT")[0]
        data_dict = json.loads(str(data_obj.get_value()))
        if str(user_message) in data_dict:
            message = data_dict[str(user_message)]
        logger.info(str(message), extra=log_param)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f"get_message_from_reverse_{channel}_mapping: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
    return message


def send_rcs_language_choices(bot_id, user_id, service_account_location, sender):
    try:
        bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
        profile_obj = Profile.objects.filter(
            user_id=user_id, bot=bot_obj).first()
        selected_language = profile_obj.selected_language.lang if profile_obj.selected_language else "en"
        channel = Channel.objects.filter(name="GoogleRCS")[0]
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()

        response = {}
        response["status_code"] = 500
        response["status_message"] = "Some error happened"
        is_different_language_selected = False
        text_message = 'choose language'
        translated_text = get_translated_text(
            text_message, selected_language, EasyChatTranslationCache)

        if languages_supported.count() > 1:
            languages = list(languages_supported.values('lang', 'display'))

            text_msg = messages.TextMessage(translated_text)
            cluster = messages.MessageCluster().append_message(text_msg)
            for index in range(len(languages)):
                language = languages[index]['display']

                cluster.append_suggestion_chip(
                    messages.SuggestedReply(language, languages[index]["lang"]))

            set_user(user_id, "googlercs", "src", "GoogleRCS", bot_id)
            save_data(profile_obj, json_data={"CHANGE_LANGUAGE_TRIGGERED": True},
                      src="None", channel="GoogleRCS", bot_id=bot_id, is_cache=True)

            cluster.send_to_msisdn(sender, service_account_location)

            response["status_code"] = 200
            response["status_message"] = "Request processed successfully."
            is_different_language_selected = True

        return response, is_different_language_selected
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_rcs_language_choices: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return response, is_different_language_selected


def send_facebook_language_choices(bot_id, user_id, page_access_token, sender):
    try:
        bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
        profile_obj = Profile.objects.filter(
            user_id=str(user_id), bot=bot_obj).first()
        selected_language = profile_obj.selected_language.lang if profile_obj.selected_language else "en"
        channel = Channel.objects.filter(name="Facebook")[0]
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()

        response = {}
        response["status_code"] = 500
        response["status_message"] = "Some error happened"
        is_different_language_selected = False
        if languages_supported.count() > 1:
            languages = list(languages_supported.values('lang', 'display'))
            text_msg = "choose language"
            translated_text = get_translated_text(
                text_msg, selected_language, EasyChatTranslationCache)
            list_choice = []
            for index in range(len(languages)):
                language = languages[index]['display']
                list_choice.append(
                    {"display": language, "value": languages[index]["lang"]})

            if len(list_choice) <= 13:
                send_recommendations_quick_replies(
                    sender, page_access_token, recommendations=list_choice, text_response=translated_text)
            else:
                send_facebook_message(sender, translated_text, page_access_token)
                send_facebook_recommendations_carousel(
                    sender, page_access_token, recommendations=list_choice)

            set_user(user_id, "facebook", "src", "Facebook", bot_id)
            save_data(profile_obj, json_data={
                      "CHANGE_LANGUAGE_TRIGGERED": True}, src="None", channel="Facebook", bot_id=bot_id, is_cache=True)

            response["status_code"] = 200
            response["status_message"] = "Request processed successfully."
            is_different_language_selected = True
            
        return response, is_different_language_selected
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_facebook_language_choices: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return response, is_different_language_selected


def send_instagram_language_choices(bot_id, user_id, page_access_token, sender):
    try:
        bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
        profile_obj = Profile.objects.filter(
            user_id=str(user_id), bot=bot_obj).first()
        selected_language = profile_obj.selected_language.lang if profile_obj.selected_language else "en"
        channel = Channel.objects.filter(name="Instagram")[0]
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()

        response = {}
        response["status_code"] = 500
        response["status_message"] = "Some error happened"
        is_different_language_selected = False
        if languages_supported.count() > 1:
            languages = list(languages_supported.values('lang', 'display'))
            text_msg = "choose language"
            translated_text = get_translated_text(
                text_msg, selected_language, EasyChatTranslationCache)
            list_choice = []
            for index in range(len(languages)):
                language = languages[index]['display']
                list_choice.append(
                    {"display": language, "value": languages[index]["lang"]})

            send_instagram_message(sender, translated_text, page_access_token)
            send_instagram_recommendations_carousel(
                sender, page_access_token, recommendations=list_choice)

            set_user(user_id, "instagram", "src", "Instagram", bot_id)
            save_data(profile_obj, json_data={"CHANGE_LANGUAGE_TRIGGERED": True},
                      src="None", channel="Instagram", bot_id=bot_id, is_cache=True)

            response["status_code"] = 200
            response["status_message"] = "Request processed successfully."
            is_different_language_selected = True
        return response, is_different_language_selected
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_instagram_language_choices: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return response, is_different_language_selected


def send_gbm_language_choices(bot_id, sender, service_account_location, bot_representative):
    try:
        bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
        profile_obj = Profile.objects.filter(
            user_id=sender, bot=bot_obj).first()
        selected_language = profile_obj.selected_language.lang if profile_obj.selected_language else "en"
        channel = Channel.objects.filter(name="GoogleBusinessMessages")[0]
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()

        response = {}
        response["status_code"] = 500
        response["status_message"] = "Some error happened"
        is_different_language_selected = False
        if languages_supported.count() > 1:
            languages = list(languages_supported.values('lang', 'display'))

            text_msg = 'choose language'
            translated_text = get_translated_text(
                text_msg, selected_language, EasyChatTranslationCache)
            language_choices = create_language_choice_list(languages)

            set_user(sender, "googlebusinessmessages",
                     "src", "GoogleBusinessMessages", bot_id)
            save_data(profile_obj, json_data={"CHANGE_LANGUAGE_TRIGGERED": True},
                      src="None", channel="GoogleBusinessMessages", bot_id=bot_id, is_cache=True)

            send_gbm_message_with_suggestions(
                translated_text, language_choices, sender, bot_representative, service_account_location)

            response["status_code"] = 200
            response["status_message"] = "Request processed successfully."
            is_different_language_selected = True
        return response, is_different_language_selected
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_gbm_language_choices: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return response, is_different_language_selected


def send_twitter_language_choices(bot_id, user_id, twitter_channel_detail_obj, sender):
    try:
        bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
        profile_obj = Profile.objects.filter(
            user_id=str(user_id), bot=bot_obj).first()
        selected_language = profile_obj.selected_language.lang if profile_obj.selected_language else "en"
        channel = Channel.objects.filter(name="Twitter")[0]
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()

        response = {}
        response["status_code"] = 500
        response["status_message"] = "Some error happened"
        is_different_language_selected = False
        if languages_supported.count() > 1:
            languages = list(languages_supported.values('lang', 'display'))
            text_msg = "choose language"
            translated_text = get_translated_text(
                text_msg, selected_language, EasyChatTranslationCache)
            list_choice = []
            for index in range(len(languages)):
                language = languages[index]['display']
                list_choice.append(
                    {"display": language, "value": languages[index]["lang"]})

            language_choices = process_recommendations_for_quick_reply(
                list_choice)

            send_twitter_message(twitter_channel_detail_obj,
                                 sender, translated_text, language_choices)

            set_user(user_id, "twitter", "src", "Twitter", bot_id)
            save_data(profile_obj, json_data={
                      "CHANGE_LANGUAGE_TRIGGERED": True}, src="None", channel="Twitter", bot_id=bot_id, is_cache=True)

            response["status_code"] = 200
            response["status_message"] = "Request processed successfully."
            is_different_language_selected = True
        return response, is_different_language_selected
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_twitter_language_choices: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return response, is_different_language_selected


def build_alexa_language_change_response(user_id, bot_id):
    translated_text = None
    try:
        set_user(user_id, "alexa", "src", "Alexa", bot_id)

        bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
        channel = Channel.objects.filter(name="Alexa")[0]
        profile_obj = Profile.objects.filter(
            user_id=str(user_id), bot=bot_obj).first()
        selected_language = profile_obj.selected_language.lang if profile_obj.selected_language else "en"
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()

        if languages_supported.count() > 1:
            languages = list(languages_supported.values('lang', 'display'))
            text_msg = " Choose language . "
            recommendation_str = ""
            REVERSE_ALEXA_MESSAGE_DICT = {}
            for index in range(len(languages)):
                language = languages[index]['display']
                REVERSE_ALEXA_MESSAGE_DICT[str(
                    index + 1)] = languages[index]['lang']
                recommendation_str += " Please say {} for " + \
                    str(language) + " ."

            translated_text = get_translated_text(
                text_msg + recommendation_str, selected_language, EasyChatTranslationCache)

            translated_text = translated_text.format(
                *list(map(str, range(1, len(languages) + 1))))
            save_data(profile_obj, json_data={
                      "CHANGE_LANGUAGE_TRIGGERED": True}, src="None", channel="Alexa", bot_id=bot_id, is_cache=True)
            save_data(profile_obj, json_data={
                      "REVERSE_ALEXA_MESSAGE_DICT": REVERSE_ALEXA_MESSAGE_DICT}, src="None", channel="Alexa", bot_id=bot_id, is_cache=True)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("build_alexa_language_change_response: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return translated_text


def send_alexa_language_choices(bot_id, user_id):
    try:
        response = {}
        response["status_code"] = 500
        response["status_message"] = "Some error happened"
        is_different_language_selected = False
        translated_text = build_alexa_language_change_response(user_id, bot_id)

        if translated_text:
            response = build_alexa_speech_response(translated_text)
            is_different_language_selected = True
        return response, is_different_language_selected
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_alexa_language_choices: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return response, is_different_language_selected


def build_google_home_language_choices(bot_id, user_id):
    try:
        speech_response, selection_list = None, None
        set_user(user_id, "googlehome", "src", "GoogleHome", bot_id)
        bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
        profile_obj = Profile.objects.filter(
            user_id=str(user_id), bot=bot_obj).first()
        selected_language = profile_obj.selected_language.lang if profile_obj.selected_language else "en"
        channel = Channel.objects.filter(name="GoogleHome")[0]
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()

        if languages_supported.count() > 1:
            languages = list(languages_supported.values('lang', 'display'))
            recommendation_str = ""
            REVERSE_GOOGLEHOME_MESSAGE_DICT = {}
            for index in range(len(languages)):
                language = languages[index]['display']
                REVERSE_GOOGLEHOME_MESSAGE_DICT[str(
                    index + 1)] = languages[index]['lang']
                recommendation_str += " Please say {} for " \
                    + str(language) + " ."

            translated_text = get_translated_text(
                recommendation_str, selected_language, EasyChatTranslationCache)
            translated_text = translated_text.format(
                *list(map(str, range(1, len(languages) + 1))))

            selection_list = []
            for language in languages:
                selection_list.append({
                    "key": language["lang"],
                    "value": language["display"]
                })

            speech_response = process_string_for_google_alexa(translated_text)

            save_data(profile_obj, json_data={"REVERSE_GOOGLEHOME_MESSAGE_DICT": REVERSE_GOOGLEHOME_MESSAGE_DICT},
                      src="None", channel="GoogleHome", bot_id=bot_id, is_cache=True)
            save_data(profile_obj, json_data={"CHANGE_LANGUAGE_TRIGGERED": True},
                      src="None", channel="GoogleHome", bot_id=bot_id, is_cache=True)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("build_google_home_language_choices: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return speech_response, selection_list


def send_google_home_language_choices(bot_id, user_id):
    try:
        webhook_response = copy.deepcopy(DEFAULT_WEBHOOK_RESPONSE)

        speech_response, selection_list = build_google_home_language_choices(
            bot_id, user_id)
        is_different_language_selected = False

        if speech_response and selection_list:
            webhook_response_text_speech_response = build_google_home_text_speech_response(
                speech_response, speech_response)
            webhook_response["payload"]["google"]["richResponse"]["items"] = [
                webhook_response_text_speech_response]

            visual_selection_list_select = build_google_home_visual_selection_list_select(
                selection_list)
            if visual_selection_list_select != None:
                webhook_response["payload"]["google"][
                    "systemIntent"] = visual_selection_list_select["systemIntent"]
            is_different_language_selected = True

        return webhook_response, is_different_language_selected
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_google_home_language_choices: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return webhook_response, is_different_language_selected


def send_mst_language_choices(bot_id, user_id, sender):
    try:
        bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
        profile_obj = Profile.objects.filter(
            user_id=str(user_id), bot=bot_obj).first()
        selected_language = profile_obj.selected_language.lang if profile_obj.selected_language else "en"
        channel = Channel.objects.filter(name="Microsoft")[0]
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()

        response = {}
        response["status"] = 200
        response["data"] = {
            "text_response_list": [],
            "videos": [],
            "image_urls": [],
            "recom_list": [],
            "cards_list": [],
            "choices_list": [],
        }
        is_different_language_selected = False

        if languages_supported.count() > 1:
            text_msg = "choose one"
            translated_message = get_translated_text(
                text_msg, selected_language, EasyChatTranslationCache)
            list_choice = []
            for language in languages_supported:
                list_choice.append(
                    {"display": language.display, "value": language.lang})

            language_choices = get_mst_recommendations(list_choice, sender)

            response["data"]["text_response_list"] = [translated_message]
            response["data"]["recom_list"] = language_choices

            set_user(user_id, "microsoft", "src", "Microsoft", bot_id)
            save_data(profile_obj, json_data={"CHANGE_LANGUAGE_TRIGGERED": True},
                      src="None", channel="Microsoft", bot_id=bot_id, is_cache=True)
            is_different_language_selected = True
        return response, is_different_language_selected
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_mst_language_choices: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return response, is_different_language_selected


def send_viber_language_choices(bot_id, user_id, sender):
    try:
        bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
        profile_obj = Profile.objects.filter(
            user_id=str(user_id), bot=bot_obj).first()
        selected_language = profile_obj.selected_language.lang if profile_obj.selected_language else "en"
        channel = Channel.objects.filter(name="Viber")[0]
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()

        response = {}
        response["status_code"] = 500
        response["status_message"] = "Some error happened"
        is_different_language_selected = False
        if languages_supported.count() > 1:
            languages = list(languages_supported.values('lang', 'display'))
            text_msg = "Choose Your Language"
            translated_text = get_translated_text(
                text_msg, selected_language, EasyChatTranslationCache)
            list_choice = []
            for index in range(len(languages)):
                language = languages[index]['display']
                list_choice.append(
                    {"display": language, "value": languages[index]["lang"]})
            send_text_to_viber(sender, user_id, bot_obj, translated_text)
            send_recomendations_to_viber(sender, user_id, list_choice)

            set_user(user_id, "viber", "src", "Viber", bot_id)
            save_data(profile_obj, json_data={"CHANGE_LANGUAGE_TRIGGERED": True},
                      src="None", channel="Viber", bot_id=bot_id, is_cache=True)

            response["status_code"] = 200
            response["status_message"] = "Request processed successfully."
            is_different_language_selected = True

        return response, is_different_language_selected
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_viber_language_choices: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return response, is_different_language_selected


def url_to_list(url):
    current_list = []
    if url != "":
        current_list = [url]
    return current_list


def check_and_update_whatsapp_menu_objs(tree_obj):
    try:
        whatsapp_menu_section_objs = WhatsAppMenuSection.objects.filter(tree=tree_obj).order_by("-pk")
        if tree_obj.is_child_tree_visible and whatsapp_menu_section_objs.count() and tree_obj.children.filter(is_deleted=False).count() > 1:
            selected_child_trees = []
            selected_main_intents = []

            for whatsapp_menu_section_obj in whatsapp_menu_section_objs:
                if whatsapp_menu_section_obj.child_trees:
                    selected_child_trees += json.loads(whatsapp_menu_section_obj.child_trees)
                if whatsapp_menu_section_obj.main_intents:
                    selected_main_intents += json.loads(whatsapp_menu_section_obj.main_intents)

            unselected_child_trees = tree_obj.children.filter(is_deleted=False).filter(~Q(pk__in=selected_child_trees)).values_list("pk", flat=True)

            if unselected_child_trees:
                available_tree_space = 10 - len(selected_main_intents) - len(selected_child_trees)
                new_section_child_tree_list = []
                for unselected_child_tree in unselected_child_trees:
                    if available_tree_space - 1 > 0:
                        new_section_child_tree_list.append(str(unselected_child_tree))
                        available_tree_space -= 1
                    else:
                        for whatsapp_menu_section_obj in whatsapp_menu_section_objs:
                            if whatsapp_menu_section_obj.main_intents and len(json.loads(whatsapp_menu_section_obj.main_intents)):
                                whatsapp_menu_section_obj.main_intents = json.dumps(json.loads(whatsapp_menu_section_obj.main_intents)[:-1])
                                whatsapp_menu_section_obj.child_trees = json.dumps(json.loads(whatsapp_menu_section_obj.child_trees) + [str(unselected_child_tree)])
                                whatsapp_menu_section_obj.save(update_fields=["child_trees", "main_intents"])
                                break

                if new_section_child_tree_list:
                    WhatsAppMenuSection.objects.create(tree=tree_obj, child_trees=json.dumps(new_section_child_tree_list))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_update_whatsapp_menu_objs: %s at %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
        

def text_link_format(text_response):
    try:
        if "</a>" in text_response:
            soup = BeautifulSoup(text_response)
            for a_tag in soup.findAll('a'):
                a_tag.replaceWith(a_tag['href'].replace(" ", "-"))
            text_response = str(soup).replace(
                "<html><body><p>", "").replace("</p></body></html>", "")
        
        return text_response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error text_link_format %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def check_if_whatsapp_credentials_are_valid(validation_obj, username, password, host_url):
    is_whatsapp_credential_valid = True
    status_message = "Whatsapp Credentials are valid"
    try:
        if username == "":
            status_message = "Username can not be Empty"
            is_whatsapp_credential_valid = False

        if password == "":
            status_message = "Password can not be Empty"
            is_whatsapp_credential_valid = False

        if len(username) > 100:
            status_message = "Username Can not be more than 100 Characters."
            is_whatsapp_credential_valid = False

        if len(password) > 256:
            status_message = "Password Can not be more than 256 Characters."
            is_whatsapp_credential_valid = False
        
        if not validation_obj.is_valid_url(host_url):
            status_message = "Whatsapp Vendor host url must be a vald url."
            is_whatsapp_credential_valid = False
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_if_whatsapp_credentials_are_valid %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return is_whatsapp_credential_valid, status_message
