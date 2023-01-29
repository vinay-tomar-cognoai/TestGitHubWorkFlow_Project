from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.models import *
from EasyChatApp.utils import *
from zipfile import ZipFile

import sys
import json
import xlrd
import logging
import os
import subprocess
from EasyChat.settings import BASE_DIR
from EasyChatApp.models import Intent
logger = logging.getLogger(__name__)

ensure_element_tree(xlrd)


def reverse_map_recommendations(bot_response_pk_dict, intent_pk_dict):
    try:
        for items in bot_response_pk_dict.keys():
            bot_response_obj = BotResponse.objects.get(
                pk=int(bot_response_pk_dict[items]))
            old_recommendations = json.loads(
                bot_response_obj.recommendations)["items"]
            new_recommendations = []
            for pk in old_recommendations:
                new_recommendations.append(intent_pk_dict[pk])

            bot_response_obj.recommendations = json.dumps(
                {"items": new_recommendations})
            bot_response_obj.save()
    except Exception:
        pass


def get_temp_file_path(path):
    try:
        from urllib.parse import urlparse
        file_path = urlparse(str(path))

        if file_path.hostname != settings.EASYCHAT_DOMAIN:
            file_path = file_path.path
            file_name = file_path.split("/")[-1].split(".")

            if len(file_name) > 1:
                return path
            else:
                return "None"

        return (file_path.path)[1:]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_temp_file_path: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return "None"


def get_local_file_path(path):
    try:
        if os.path.exists(path):
            return '/' + path

        filedir, filename = os.path.split(path)
        if filename == "":
            return None
        file_to_store = requests.get(path)
        open(settings.MEDIA_ROOT + filename, 'wb').write(file_to_store.content)
        return "/files/" + filename
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_local_file_path: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return "None"


"""
function: import_auth_user_object
input params:
    easychat_object: object containing user data

returns user object depend on user data [used while importing bot]
"""


def import_auth_user_object(easychat_object):
    try:
        logger.info("Into Import Authorization User Object", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        username = easychat_object["fields"]["username"]
        first_name = easychat_object["fields"]["first_name"]
        last_name = easychat_object["fields"]["last_name"]
        is_active = easychat_object["fields"]["is_active"]
        is_superuser = easychat_object["fields"]["is_superuser"]
        is_staff = easychat_object["fields"]["is_staff"]
        # last_login = easychat_object["fields"]["last_login"]
        password = easychat_object["fields"]["password"]
        email = easychat_object["fields"]["email"]
        # date_joined = easychat_object["fields"]["date_joined"]

        user_objs = User.objects.filter(username=username)
        if len(user_objs) == 0:
            user_obj = User.objects.create(username=username,
                                           first_name=first_name,
                                           last_name=last_name,
                                           is_active=is_active,
                                           is_superuser=is_superuser,
                                           is_staff=is_staff,
                                           password=password,
                                           email=email)
            if user_obj.is_staff:
                user_obj.is_bot_invocation_enabled = True
            logger.info("Exit from Import Authorization User Object", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return user_obj
        else:
            logger.info("Exit from Import Authorization User Object", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return user_objs[0]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_auth_user_object: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_channel_object
input params:
    easychat_object: object containing channel data

returns channel object depend on channel data [used while importing bot]
"""


def import_easychat_channel_object(easychat_object):
    try:
        from EasyChatApp.models import Channel
        channel_name = easychat_object["fields"]["name"]
        channel_objs = Channel.objects.filter(name=str(channel_name))

        if len(channel_objs) != 0:
            return channel_objs[0]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_channel_object: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return None


"""
function: import_easychat_category_object
input params:
    easychat_object: object containing channel data

returns channel object depend on channel data [used while importing bot]
"""


def import_easychat_category_object(easychat_object, active_bot_obj):
    try:
        from EasyChatApp.models import Category
        category_name = easychat_object["fields"]["name"]
        category_objs = Category.objects.filter(
            name=category_name, bot=active_bot_obj)
        if category_objs.count() == 0:
            category_obj = Category.objects.create(
                name=str(category_name), bot=active_bot_obj)
            return category_obj
        else:
            return category_objs[0]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_category_object: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_bot_object
input params:
    easychat_object: object containing bot data
    active_user_obj: active user object
    easychat_bot_objs_dict: list of bot objects

returns bot object depend on bot data [used while importing bot]
"""


def import_easychat_bot_object(easychat_object, active_user_obj, easychat_bot_objs_dict):
    try:
        from EasyChatApp.models import Bot
        is_deleted = easychat_object["fields"]["is_deleted"]
        name = easychat_object["fields"]["name"]
        child_bots = easychat_object["fields"]["child_bots"]
        stop_keywords = easychat_object["fields"]["stop_keywords"]
        is_active = easychat_object["fields"]["is_active"]
        slug = easychat_object["fields"]["slug"]
        bot_image = easychat_object["fields"]["bot_image"]
        is_uat = easychat_object["fields"]["is_uat"]
        bot_theme_color = easychat_object["fields"]["bot_theme_color"]
        trigger_keywords = easychat_object["fields"]["trigger_keywords"]
        message_image = easychat_object["fields"]["message_image"]
        bot_type = easychat_object["fields"]["bot_type"]
        bot_display_name = easychat_object["fields"]["bot_display_name"]
        is_text_to_speech_required = easychat_object[
            "fields"]["is_text_to_speech_required"]
        terms_and_condition = easychat_object["fields"]["terms_and_condition"]
        start_conversation = easychat_object["fields"]["start_conversation"]

        bot_objs = Bot.objects.filter(
            slug=slug, is_uat=True, users__in=[active_user_obj])

        if len(bot_objs) == 0:

            bot_obj = Bot.objects.create(is_deleted=is_deleted,
                                         name=name,
                                         stop_keywords=stop_keywords,
                                         is_active=is_active,
                                         slug=slug,
                                         bot_image=bot_image,
                                         is_uat=is_uat,
                                         bot_theme_color=bot_theme_color,
                                         trigger_keywords=trigger_keywords,
                                         message_image=message_image,
                                         bot_type=bot_type,
                                         bot_display_name=bot_display_name,
                                         is_text_to_speech_required=is_text_to_speech_required,
                                         terms_and_condition=terms_and_condition,
                                         start_conversation=start_conversation)

            for bot_pk in child_bots:
                bot_obj.child_bots.add(easychat_bot_objs_dict[str(bot_pk)])

            bot_obj.users.add(active_user_obj)
            bot_obj.save()
            return bot_obj
        else:
            bot_obj = bot_objs[0]
            bot_obj.is_deleted = is_deleted
            bot_obj.name = name
            bot_obj.stop_keywords = stop_keywords
            bot_obj.is_active = is_active
            bot_obj.slug = slug
            bot_obj.bot_image = bot_image
            bot_obj.is_uat = is_uat
            bot_obj.bot_theme_color = bot_theme_color
            bot_obj.trigger_keywords = trigger_keywords
            bot_obj.message_image = message_image
            bot_obj.bot_display_name = bot_display_name
            bot_obj.is_text_to_speech_required = is_text_to_speech_required
            bot_obj.terms_and_condition = terms_and_condition
            bot_obj.start_conversation = start_conversation
            bot_obj.child_bots.clear()
            bot_obj.users.clear()

            for bot_pk in child_bots:
                bot_obj.child_bots.add(easychat_bot_objs_dict[str(bot_pk)])

            bot_obj.users.add(active_user_obj)
            bot_obj.save()
            return bot_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_bot_object: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_word_mapper_obj
input params:
    easychat_object: object containing word mapper data
    active_user_obj: active user object

returns word mapper object depend on word mapper data [used while importing bot]
"""


def import_easychat_word_mapper_obj(easychat_object, active_bot_obj):
    try:
        from EasyChatApp.models import WordMapper
        keyword = easychat_object["fields"]["keyword"]
        similar_words = easychat_object["fields"]["similar_words"]
        # bots = easychat_object["fields"]["bots"]

        word_mapper_obj = WordMapper.objects.create(keyword=keyword,
                                                    similar_words=similar_words)

        word_mapper_obj.bots.add(active_bot_obj)
        word_mapper_obj.save()
        return word_mapper_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_word_mapper_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


def map_intent_list(intent_from_list, reverse_map_intent_key):
    list_intent_target = []

    for intent in intent_from_list:
        if intent in reverse_map_intent_key.keys():
            list_intent_target.append(reverse_map_intent_key[intent])

    return list_intent_target


def map_intent_dictionary(intent_dictionary_list, reverse_map_intent_key):
    list_intent_target_dictionary = []

    for intent in intent_dictionary_list:
        if list(intent.keys())[0] in reverse_map_intent_key.keys():
            temp_dict = {}
            key = reverse_map_intent_key[list(intent.keys())[0]]
            temp_dict[key] = list(intent.values())[0]
            list_intent_target_dictionary.append(temp_dict)

    return list_intent_target_dictionary


def replace_intents_sticky_intent_menu(sticky_menu_list, reverse_map_intent_key):

    for item in sticky_menu_list:
        if item[0] in reverse_map_intent_key.keys():
            item[0] = reverse_map_intent_key[item[0]]

    return sticky_menu_list


"""
function: import_easychat_bot_channel_obj
input params:
    easychat_object: object containing bot channel data
    active_user_obj: active user object
    easychat_channel_objs_dict: list of channel objects 
    reverse_map_intent_key: for reverse mapping

returns bot channel object depend on bot channel data [used while importing bot]
"""


def import_easychat_bot_channel_obj(easychat_object, easychat_channel_objs_dict, active_bot_obj, reverse_map_intent_key):
    try:

        welcome_message = easychat_object["fields"]["welcome_message"]
        failure_message = easychat_object["fields"]["failure_message"]
        authentication_message = easychat_object[
            "fields"]["authentication_message"]
        channel_params = easychat_object["fields"]["channel_params"]
        reprompt_message = easychat_object["fields"]["reprompt_message"]

        initial_messages = json.loads(
            easychat_object["fields"]["initial_messages"])
        initial_messages["items"] = map_intent_list(
            initial_messages["items"], reverse_map_intent_key)
        if "new_tag_list" in initial_messages:
            initial_messages["new_tag_list"] = map_intent_dictionary(
                initial_messages["new_tag_list"], reverse_map_intent_key)
        initial_messages = json.dumps(initial_messages)

        sticky_intent = json.loads(easychat_object["fields"]["sticky_intent"])
        sticky_intent["items"] = map_intent_list(
            sticky_intent["items"], reverse_map_intent_key)
        sticky_intent = json.dumps(sticky_intent)

        sticky_intent_menu = json.loads(
            easychat_object["fields"]["sticky_intent_menu"])
        sticky_intent_menu['items'] = replace_intents_sticky_intent_menu(
            sticky_intent_menu["items"], reverse_map_intent_key)
        sticky_intent_menu = json.dumps(sticky_intent_menu)

        failure_recommendations = json.loads(
            easychat_object["fields"]["failure_recommendations"])
        failure_recommendations["items"] = map_intent_list(
            failure_recommendations["items"], reverse_map_intent_key)
        failure_recommendations = json.dumps(failure_recommendations)

        session_end_message = easychat_object["fields"]["session_end_message"]
        channel_pk = easychat_object["fields"]["channel"]
        speech_message = easychat_object["fields"]["speech_message"]
        image_url = json.loads(easychat_object["fields"]["image_url"])["items"]
        image_url_list = []
        for url in image_url:
            path = get_temp_file_path(url)
            if path != "None":
                image_url_list.append(
                    settings.EASYCHAT_HOST_URL + get_local_file_path(path))
            else:
                image_url_list.append(url)

        image_url = json.dumps({"items": image_url_list})
        redirection_url = easychat_object["fields"]["redirection_url"]

        bot_obj = active_bot_obj
        channel_obj = easychat_channel_objs_dict[str(channel_pk)]

        bot_channel_objs = BotChannel.objects.filter(bot=bot_obj,
                                                     channel=channel_obj)

        if channel_obj == None:
            return None

        if len(bot_channel_objs) == 0:
            bot_channel_obj = BotChannel.objects.create(welcome_message=welcome_message,
                                                        bot=bot_obj,
                                                        channel=channel_obj,
                                                        failure_message=failure_message,
                                                        authentication_message=authentication_message,
                                                        channel_params=channel_params,
                                                        reprompt_message=reprompt_message,
                                                        initial_messages=initial_messages,
                                                        sticky_intent=sticky_intent,
                                                        sticky_intent_menu=sticky_intent_menu,
                                                        failure_recommendations=failure_recommendations,
                                                        session_end_message=session_end_message,
                                                        speech_message=speech_message,
                                                        redirection_url=redirection_url,
                                                        image_url=image_url)
            return bot_channel_obj
        else:
            bot_channel_obj = bot_channel_objs[0]
            bot_channel_obj.welcome_message = welcome_message
            bot_channel_obj.failure_message = failure_message
            bot_channel_obj.authentication_message = authentication_message
            bot_channel_obj.channel_params = channel_params
            bot_channel_obj.reprompt_message = reprompt_message
            bot_channel_obj.initial_messages = initial_messages
            bot_channel_obj.sticky_intent = sticky_intent
            bot_channel_obj.sticky_intent_menu = sticky_intent_menu
            bot_channel_obj.failure_recommendations = failure_recommendations
            bot_channel_obj.session_end_message = session_end_message
            bot_channel_obj.speech_message = speech_message
            bot_channel_obj.redirection_url = redirection_url
            bot_channel_obj.image_url = image_url
            bot_channel_obj.save()
            return bot_channel_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_bot_channel_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


def import_easychat_welcome_banner_obj(welcome_banner_obj, active_bot_obj, reverse_map_intent_key):
    try:
        action_type = welcome_banner_obj['action_type']
        image_url = welcome_banner_obj['image_url']
        redirection_url = welcome_banner_obj['redirection_url']
        intent_pk = welcome_banner_obj['intent']
        intent_obj = None
        if intent_pk:
            intent_pk = reverse_map_intent_key[str(intent_pk)]
            intent_obj = Intent.objects.get(pk=int(intent_pk))
        channel_name = welcome_banner_obj['channel_name']
        bot_channel_obj = BotChannel.objects.get(
            channel__name=channel_name, bot=active_bot_obj)

        welcome_banner_existing_objs = WelcomeBanner.objects.filter(
            bot_channel=bot_channel_obj)
        serial_number = welcome_banner_existing_objs.count() + 1

        WelcomeBanner.objects.create(bot_channel=bot_channel_obj,
                                     action_type=action_type,
                                     image_url=image_url,
                                     redirection_url=redirection_url,
                                     intent=intent_obj,
                                     serial_number=serial_number)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_welcome_banner_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def import_emoji_bot_response_obj(emoji_bot_response_obj, active_bot_obj):
    try:
        add_livechat_intent = emoji_bot_response_obj['add_livechat_intent']
        emoji_angry_response_text = emoji_bot_response_obj['emoji_angry_response_text']
        emoji_happy_response_text = emoji_bot_response_obj['emoji_happy_response_text']
        emoji_neutral_response_text = emoji_bot_response_obj['emoji_neutral_response_text']
        emoji_sad_response_text = emoji_bot_response_obj['emoji_sad_response_text']

        active_emoji_bot_response_obj = EmojiBotResponse.objects.filter(
            bot=active_bot_obj)
        if active_emoji_bot_response_obj.exists():
            active_emoji_bot_response_obj = active_emoji_bot_response_obj.first()
            active_emoji_bot_response_obj.add_livechat_intent = add_livechat_intent
            active_emoji_bot_response_obj.emoji_angry_response_text = emoji_angry_response_text
            active_emoji_bot_response_obj.emoji_happy_response_text = emoji_happy_response_text
            active_emoji_bot_response_obj.emoji_neutral_response_text = emoji_neutral_response_text
            active_emoji_bot_response_obj.emoji_sad_response_text = emoji_sad_response_text
            active_emoji_bot_response_obj.save()
        else:
            EmojiBotResponse.objects.create(bot=active_bot_obj,
                                            add_livechat_intent=add_livechat_intent,
                                            emoji_angry_response_text=emoji_angry_response_text,
                                            emoji_happy_response_text=emoji_happy_response_text,
                                            emoji_neutral_response_text=emoji_neutral_response_text,
                                            emoji_sad_response_text=emoji_sad_response_text)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_emoji_bot_response_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def import_analytics_monitoring_obj(analytics_monitoring_obj, bot_obj):
    try:
        active_hours_start = analytics_monitoring_obj['active_hours_start']
        active_hours_end = analytics_monitoring_obj['active_hours_end']
        message_limit = analytics_monitoring_obj['message_limit']
        consecutive_hours = analytics_monitoring_obj['consecutive_hours']
        email_addr_list = analytics_monitoring_obj['email_addr_list']

        active_hours_start = datetime.datetime.strptime(
            active_hours_start, '%H:%M:%S').time()
        active_hours_end = datetime.datetime.strptime(
            active_hours_end, '%H:%M:%S').time()

        active_analytics_monitoring_obj = AnalyticsMonitoring.objects.filter(
            bot=bot_obj)
        if active_analytics_monitoring_obj.exists():
            active_analytics_monitoring_obj = active_analytics_monitoring_obj.first()
            active_analytics_monitoring_obj.active_hours_start = active_hours_start
            active_analytics_monitoring_obj.active_hours_end = active_hours_end
            active_analytics_monitoring_obj.message_limit = message_limit
            active_analytics_monitoring_obj.consecutive_hours = consecutive_hours
            active_analytics_monitoring_obj.email_addr_list = email_addr_list
            active_analytics_monitoring_obj.save()
        else:
            active_analytics_monitoring_obj = AnalyticsMonitoring.objects.create(bot=bot_obj,
                                                                                 message_limit=message_limit,
                                                                                 consecutive_hours=consecutive_hours,
                                                                                 email_addr_list=email_addr_list)
            active_analytics_monitoring_obj.active_hours_start = active_hours_start
            active_analytics_monitoring_obj.active_hours_end = active_hours_end
            active_analytics_monitoring_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_analytics_monitoring_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def import_nps_obj(nps_obj, bot_obj):
    try:
        whatsapp_nps_time = nps_obj['whatsapp_nps_time']
        csat_reset_duration = nps_obj['csat_reset_duration']
        channel_names = nps_obj['channel_names']

        active_nps_obj = NPS.objects.filter(
            bot=bot_obj)
        if active_nps_obj.exists():
            active_nps_obj = active_nps_obj.first()
            active_nps_obj.whatsapp_nps_time = whatsapp_nps_time
            active_nps_obj.csat_reset_duration = csat_reset_duration
            active_nps_obj.channel.clear()
            for channel in channel_names:
                channel_obj = Channel.objects.get(name=channel)
                active_nps_obj.channel.add(channel_obj)
            active_nps_obj.save()
        else:
            active_nps_obj = NPS.objects.create(bot=bot_obj,
                                                whatsapp_nps_time=whatsapp_nps_time,
                                                csat_reset_duration=csat_reset_duration)
            for channel in channel_names:
                channel_obj = Channel.objects.get(name=channel)
                active_nps_obj.channel.add(channel_obj)
            active_nps_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_nps_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def import_csat_feedback_obj(csat_feedback_obj, bot_obj):
    try:
        number_of_feedbacks = csat_feedback_obj['number_of_feedbacks']
        collect_phone_number = csat_feedback_obj['collect_phone_number']
        collect_email_id = csat_feedback_obj['collect_email_id']
        mark_all_fields_mandatory = csat_feedback_obj['mark_all_fields_mandatory']
        all_feedbacks = csat_feedback_obj['all_feedbacks']

        active_csat_feedback_obj = CSATFeedBackDetails.objects.filter(
            bot_obj=bot_obj)
        if active_csat_feedback_obj.exists():
            active_csat_feedback_obj = active_csat_feedback_obj.first()
            active_csat_feedback_obj.number_of_feedbacks = number_of_feedbacks
            active_csat_feedback_obj.collect_phone_number = collect_phone_number
            active_csat_feedback_obj.collect_email_id = collect_email_id
            active_csat_feedback_obj.mark_all_fields_mandatory = mark_all_fields_mandatory
            active_csat_feedback_obj.all_feedbacks = all_feedbacks

            active_csat_feedback_obj.save()
        else:
            CSATFeedBackDetails.objects.create(bot_obj=bot_obj,
                                               number_of_feedbacks=number_of_feedbacks,
                                               collect_phone_number=collect_phone_number,
                                               collect_email_id=collect_email_id,
                                               mark_all_fields_mandatory=mark_all_fields_mandatory,
                                               all_feedbacks=all_feedbacks)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_csat_feedback_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: import_easychat_bot_settings
input params:
    easychat_object: new bot obj
    active_bot_obj: active bot object
    reverse_map_intent_key : to reverse map intents
"""


def import_easychat_bot_settings(easychat_object, active_bot_obj, reverse_map_intent_key):
    try:
        active_bot_obj.trigger_keywords = easychat_object[
            "fields"]["trigger_keywords"]
        active_bot_obj.stop_keywords = easychat_object[
            "fields"]["stop_keywords"]
        active_bot_obj.font = easychat_object["fields"]["font"]
        active_bot_obj.font_size = easychat_object["fields"]["font_size"]
        active_bot_obj.bot_type = easychat_object["fields"]["bot_type"]
        active_bot_obj.bot_theme_color = easychat_object[
            "fields"]["bot_theme_color"]
        active_bot_obj.is_text_to_speech_required = easychat_object[
            "fields"]["is_text_to_speech_required"]
        active_bot_obj.is_easy_search_allowed = easychat_object[
            "fields"]["is_easy_search_allowed"]
        active_bot_obj.terms_and_condition = easychat_object[
            "fields"]["terms_and_condition"]
        active_bot_obj.is_form_assist_enabled = easychat_object[
            "fields"]["is_form_assist_enabled"]
        active_bot_obj.is_livechat_enabled = easychat_object[
            "fields"]["is_livechat_enabled"]
        active_bot_obj.is_easy_assist_allowed = easychat_object[
            "fields"]["is_easy_assist_allowed"]
        active_bot_obj.is_tms_allowed = easychat_object[
            "fields"]["is_tms_allowed"]
        active_bot_obj.is_lead_generation_enabled = easychat_object[
            "fields"]["is_lead_generation_enabled"]
        active_bot_obj.max_suggestions = easychat_object[
            "fields"]["max_suggestions"]
        active_bot_obj.is_auto_pop_allowed = easychat_object[
            "fields"]["is_auto_pop_allowed"]
        active_bot_obj.auto_pop_timer = easychat_object[
            "fields"]["auto_pop_timer"]
        active_bot_obj.bot_position = easychat_object["fields"]["bot_position"]
        active_bot_obj.is_feedback_required = easychat_object[
            "fields"]["is_feedback_required"]
        active_bot_obj.is_form_assist_auto_pop_allowed = easychat_object[
            "fields"]["is_form_assist_auto_pop_allowed"]
        active_bot_obj.form_assist_autopop_up_timer = easychat_object[
            "fields"]["form_assist_autopop_up_timer"]
        active_bot_obj.form_assist_inactivity_timer = easychat_object[
            "fields"]["form_assist_inactivity_timer"]
        active_bot_obj.flow_termination_keywords = easychat_object[
            "fields"]["flow_termination_keywords"]
        active_bot_obj.flow_termination_bot_response = easychat_object[
            "fields"]["flow_termination_bot_response"]
        active_bot_obj.flow_termination_confirmation_display_message = easychat_object[
            "fields"]["flow_termination_confirmation_display_message"]
        active_bot_obj.is_nps_required = easychat_object[
            "fields"]["is_nps_required"]
        active_bot_obj.scale_rating_5 = easychat_object[
            "fields"]["scale_rating_5"]
        active_bot_obj.csat_feedback_form_enabled = easychat_object[
            "fields"]["csat_feedback_form_enabled"]
        active_bot_obj.is_small_talk_disable = easychat_object[
            "fields"]["is_small_talk_disable"]
        active_bot_obj.is_synonyms_included_in_paraphrase = easychat_object[
            "fields"]["is_synonyms_included_in_paraphrase"]
        active_bot_obj.bot_inactivity_response = easychat_object[
            "fields"]["bot_inactivity_response"]
        active_bot_obj.bot_userid_cookie_timeout = easychat_object[
            "fields"]["bot_userid_cookie_timeout"]
        active_bot_obj.is_minimization_enabled = easychat_object[
            "fields"]["is_minimization_enabled"]
        active_bot_obj.bot_image = easychat_object[
            "fields"]["bot_image"]
        active_bot_obj.bot_logo = easychat_object[
            "fields"]["bot_logo"]
        active_bot_obj.message_image = easychat_object[
            "fields"]["message_image"]
        active_bot_obj.bot_response_delay_allowed = easychat_object[
            "fields"]["bot_response_delay_allowed"]
        active_bot_obj.bot_response_delay_timer = easychat_object[
            "fields"]["bot_response_delay_timer"]
        active_bot_obj.bot_response_delay_message = easychat_object[
            "fields"]["bot_response_delay_message"]
        active_bot_obj.is_inactivity_timer_enabled = easychat_object[
            "fields"]["is_inactivity_timer_enabled"]
        active_bot_obj.bot_inactivity_timer = easychat_object[
            "fields"]["bot_inactivity_timer"]
        active_bot_obj.bot_inactivity_response = easychat_object[
            "fields"]["bot_inactivity_response"]
        active_bot_obj.default_order_of_response = easychat_object[
            "fields"]["default_order_of_response"]
        active_bot_obj.is_email_notifiication_enabled = easychat_object[
            "fields"]["is_email_notifiication_enabled"]
        active_bot_obj.is_api_fail_email_notifiication_enabled = easychat_object[
            "fields"]["is_api_fail_email_notifiication_enabled"]
        active_bot_obj.mail_sender_time_interval = easychat_object[
            "fields"]["mail_sender_time_interval"]
        active_bot_obj.mail_sent_to_list = easychat_object[
            "fields"]["mail_sent_to_list"]
        active_bot_obj.show_intent_threshold_functionality = easychat_object[
            "fields"]["show_intent_threshold_functionality"]
        active_bot_obj.intent_score_threshold = easychat_object[
            "fields"]["intent_score_threshold"]
        active_bot_obj.enable_intent_level_nlp = easychat_object[
            "fields"]["enable_intent_level_nlp"]
        active_bot_obj.is_analytics_monitoring_enabled = easychat_object[
            "fields"]["is_analytics_monitoring_enabled"]

        bot_default_theme = easychat_object["fields"]["default_theme"]
        easychat_theme_obj = None
        if bot_default_theme != 'null':
            easychat_theme_obj = EasyChatTheme.objects.filter(
                name=bot_default_theme)
            if easychat_theme_obj:
                easychat_theme_obj = easychat_theme_obj[0]
            else:
                easychat_theme_obj = None

        active_bot_obj.default_theme = easychat_theme_obj

        initial_intent_pk = str(easychat_object["fields"]["initial_intent"])
        if initial_intent_pk is not None and initial_intent_pk in reverse_map_intent_key.keys():
            intent_objects = Intent.objects.filter(pk=int(
                reverse_map_intent_key[initial_intent_pk]), is_deleted=False, is_hidden=False)
            if(intent_objects.count() > 0):
                active_bot_obj.initial_intent = intent_objects[0]

        livechat_default_intent = str(
            easychat_object["fields"]["livechat_default_intent"])
        if livechat_default_intent is not None and livechat_default_intent in reverse_map_intent_key.keys():
            intent_objects = Intent.objects.filter(pk=int(
                reverse_map_intent_key[livechat_default_intent]), is_deleted=False, is_hidden=False)
            if(intent_objects.count() > 0):
                active_bot_obj.livechat_default_intent = intent_objects[0]

        active_bot_obj.save()
        is_form_assist_enabled = easychat_object["fields"]["is_form_assist_enabled"]
        if is_form_assist_enabled:
            form_assist_obj = FormAssistBotData.objects.filter(
                bot=active_bot_obj)
            if not form_assist_obj.exists():
                form_assist_obj = FormAssistBotData.objects.create(
                    bot=active_bot_obj)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_bot_settings: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_processor_obj
input params:
    easychat_object: object containing processor data

returns processor object depend on processor data [used while importing bot]
"""


def import_easychat_processor_obj(easychat_object, bot_name="AllinCall"):
    try:
        from EasyChatApp.models import Processor
        name = easychat_object["fields"]["name"]
        function = easychat_object["fields"]["function"]

        processor_obj = Processor.objects.create(name=name + str(bot_name),
                                                 function=function)

        return processor_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_processor_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_choice_obj
input params:
    easychat_object: object containing choice data

returns choice object depend on choice data [used while importing bot]
"""


def import_easychat_choice_obj(easychat_object):
    try:
        from EasyChatApp.models import Choice
        display = easychat_object["fields"]["display"]
        value = easychat_object["fields"]["value"]

        choice_obj = Choice.objects.create(display=display,
                                           value=value)

        return choice_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_choice_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_bot_response_obj
input params:
    easychat_object: object containing bot response data
    easychat_choice_dict: dict containing choice data
returns bot response depend on bot response data [used while importing bot]
"""


def import_easychat_bot_response_obj(easychat_object, easychat_choice_dict):
    try:
        from EasyChatApp.models import BotResponse
        auto_response = easychat_object["fields"]["auto_response"]
        modes = easychat_object["fields"]["modes"]
        videos = easychat_object["fields"]["videos"]
        sentence = easychat_object["fields"]["sentence"]
        is_timed_response_present = easychat_object[
            "fields"]["is_timed_response_present"]
        image_url = json.loads(easychat_object["fields"]["images"])["items"]
        image_url_list = []
        for url in image_url:
            path = get_temp_file_path(url)
            if path != "None":
                image_url_list.append(
                    settings.EASYCHAT_HOST_URL + get_local_file_path(path))
            else:
                image_url_list.append(url)

        images = json.dumps({"items": image_url_list})
        recommendations = easychat_object["fields"]["recommendations"]
        cards = json.loads(easychat_object["fields"]["cards"])["items"]
        card_list = []
        for url in cards:
            try:
                link = get_temp_file_path(url["link"])
                if link != "None":
                    link = settings.EASYCHAT_HOST_URL + \
                        get_local_file_path(link)
                else:
                    link = url["link"]

                image_url = get_temp_file_path(url["img_url"])
                if image_url != "None":
                    image_url = settings.EASYCHAT_HOST_URL + \
                        get_local_file_path(image_url)
                else:
                    image_url = url["img_url"]

                card_list.append(
                    {"title": url["title"], "content": url["content"], "link": link, "img_url": image_url})
            except Exception:
                pass

        cards = json.dumps({"items": card_list})
        timer_value = easychat_object["fields"]["timer_value"]
        modes_param = easychat_object["fields"]["modes_param"]
        choices = easychat_object["fields"]["choices"]
        table = easychat_object["fields"]["table"]

        bot_response_obj = BotResponse.objects.create(auto_response=auto_response,
                                                      modes=modes,
                                                      videos=videos,
                                                      sentence=sentence,
                                                      is_timed_response_present=is_timed_response_present,
                                                      images=images,
                                                      recommendations=recommendations,
                                                      cards=cards,
                                                      timer_value=timer_value,
                                                      modes_param=modes_param,
                                                      table=table)

        for choice_pk in choices:
            bot_response_obj.choices.add(easychat_choice_dict[str(choice_pk)])

        bot_response_obj.save()
        return bot_response_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_bot_response_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_api_tree_obj
input params:
    easychat_object: object containing api tree data
    active_user_obj: active user data
returns api tree depend on api tree data [used while importing bot]
"""


def import_easychat_api_tree_obj(easychat_object, active_user_obj, bot_name="AllinCall"):
    try:
        from EasyChatApp.models import ApiTree
        name = easychat_object["fields"]["name"]
        api_caller = easychat_object["fields"]["api_caller"]
        is_cache = easychat_object["fields"]["is_cache"]
        cache_variable = easychat_object["fields"]["cache_variable"]

        api_tree_obj = ApiTree.objects.create(name=name + str(bot_name),
                                              api_caller=api_caller,
                                              is_cache=is_cache,
                                              cache_variable=cache_variable)

        api_tree_obj.users.add(active_user_obj)
        api_tree_obj.save(True)
        return api_tree_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_api_tree_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_tree_obj
input params:
    easychat_object: object containing tree data
    easychat_bot_response_dict: dict containing bot respobse data
    easychat_processor_dict: dict containing processor data
    easychat_api_tree_dict: dict containing api tree data
    easychat_tree_dict: dict containing tree data
returns tree depend on tree data [used while importing bot]
"""


def import_easychat_tree_obj(easychat_object,
                             easychat_bot_response_dict,
                             easychat_processor_dict,
                             easychat_api_tree_dict,
                             easychat_tree_dict):
    from EasyChatApp.models import Tree
    try:
        is_deleted = easychat_object["fields"]["is_deleted"]
        name = easychat_object["fields"]["name"]
        api_tree = easychat_object["fields"]["api_tree"]
        accept_keywords = easychat_object["fields"]["accept_keywords"]
        pre_processor = easychat_object["fields"]["pre_processor"]
        pipe_processor = easychat_object["fields"]["pipe_processor"]
        post_processor = easychat_object["fields"]["post_processor"]
        response = easychat_object["fields"]["response"]
        order_of_response = easychat_object["fields"]["order_of_response"]

        if len(name) > INTENT_TREE_NAME_CHARACTER_LIMIT:
            logger.error("import_easychat_tree_obj: %s at %s",
                            "Tree Name Cannot Contain More Than 500 Characters", str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return None

        is_child_tree_visible = True
        if "is_child_tree_visible" in easychat_object["fields"]:
            is_child_tree_visible = easychat_object[
                "fields"]["is_child_tree_visible"]

        if pre_processor != None:
            pre_processor = easychat_processor_dict[str(pre_processor)]

        if pipe_processor != None:
            pipe_processor = easychat_processor_dict[str(pipe_processor)]

        if post_processor != None:
            post_processor = easychat_processor_dict[str(post_processor)]

        if api_tree != None:
            api_tree = easychat_api_tree_dict[str(api_tree)]

        if response != None:
            response = easychat_bot_response_dict[str(response)]

        tree_obj = Tree.objects.create(is_deleted=is_deleted,
                                       name=name,
                                       api_tree=api_tree,
                                       accept_keywords=accept_keywords,
                                       pre_processor=pre_processor,
                                       pipe_processor=pipe_processor,
                                       post_processor=post_processor,
                                       response=response,
                                       is_child_tree_visible=is_child_tree_visible,
                                       order_of_response=order_of_response)

        tree_obj.save()
        return tree_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_tree_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_authentication_obj
input params:
    easychat_object: object containing authentication data
    easychat_tree_dict: dict containing tree data

returns authentication object depend on authentication data [used while importing bot]
"""


def import_easychat_authentication_obj(easychat_object, easychat_tree_dict):
    try:
        from EasyChatApp.models import Authentication
        name = easychat_object["fields"]["name"]
        auth_time = easychat_object["fields"]["auth_time"]
        tree = easychat_object["fields"]["tree"]

        if tree != None:
            tree = easychat_tree_dict[str(tree)]

        authetication_obj = Authentication.objects.create(name=name,
                                                          auth_time=auth_time,
                                                          tree=tree)

        return authetication_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_authentication_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_user_authentication_obj
input params:
    easychat_object: object containing user authentication data
    easychat_authentication_dict: dict containing authentication data
    easychat_profile_dict: dict containing profile data

returns user authentication object depend on user authentication data [used while importing bot]
"""


def import_easychat_user_authentication_obj(easychat_object,
                                            easychat_authentication_dict,
                                            easychat_profile_dict):
    try:
        from EasyChatApp.models import UserAuthentication
        auth_type = easychat_object["fields"]["auth_type"]
        user = easychat_object["fields"]["user"]
        user_params = easychat_object["fields"]["user_params"]

        if auth_type != None:
            auth_type = easychat_object[str(auth_type)]

        if user != None:
            user = easychat_object[str(user)]

        user_authentication_obj = UserAuthentication.objects.create(auth_type=auth_type,
                                                                    user=user,
                                                                    user_params=user_params)

        return user_authentication_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_user_authentication_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_data_obj
input params:
    easychat_object: object containing data model data
    easychat_profile_dict: dict containing profile data

returns data object depend on given data [used while importing bot]
"""


def import_easychat_data_obj(easychat_object, easychat_profile_dict):
    try:
        from EasyChatApp.models import Data
        variable_data = easychat_object["fields"]["variable"]
        user = easychat_object["fields"]["user"]
        value = easychat_object["fields"]["value"]
        is_cache = easychat_object["fields"]["is_cache"]

        if user != None:
            user = easychat_profile_dict[str(user)]

        data_obj = Data.objects.create(variable=variable_data,
                                       user=user,
                                       value=value,
                                       is_cache=is_cache)

        return data_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_data_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_language_obj
input params:
    easychat_object: object containing language data

returns language object depend on given language data [used while importing bot]
"""


def import_easychat_language_obj(easychat_object):
    try:
        from EasyChatApp.models import Language
        lang = easychat_object["fields"]["lang"]

        language_objs = Language.objects.filter(lang=lang)

        if len(language_objs) == 0:
            return Language.objects.create(lang=lang)
        else:
            return language_objs[0]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_language_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_config_obj
input params:
    easychat_object: object containing config data
    easychat_language_dict: dict containing language data

returns Config object depend on given Config data [used while importing bot]
"""


def import_easychat_config_obj(easychat_object, easychat_language_dict):
    try:
        from EasyChatApp.models import Config
        app_url = easychat_object["fields"]["app_url"]
        no_of_bots_allowed = easychat_object["fields"]["no_of_bots_allowed"]
        monthly_analytics_parameter = easychat_object[
            "fields"]["monthly_analytics_parameter"]
        allow_bot_switch = easychat_object["fields"]["allow_bot_switch"]
        is_bot_shareable = easychat_object["fields"]["is_bot_shareable"]
        daily_analytics_parameter = easychat_object[
            "fields"]["daily_analytics_parameter"]
        is_google_search_allowed = easychat_object[
            "fields"]["is_google_search_allowed"]
        sample_questions = easychat_object["fields"]["sample_questions"]
        is_feedback_required = easychat_object[
            "fields"]["is_feedback_required"]
        show_licence = easychat_object["fields"]["show_licence"]
        top_intents_parameter = easychat_object[
            "fields"]["top_intents_parameter"]
        cached_duration = easychat_object["fields"]["cached_duration"]
        site_title = easychat_object["fields"]["site_title"]
        intent_not_found_response = easychat_object[
            "fields"]["intent_not_found_response"]
        generic_error_response = easychat_object[
            "fields"]["generic_error_response"]
        prod = easychat_object["fields"]["prod"]
        languages_supported = easychat_object["fields"]["languages_supported"]

        config_objs = Config.objects.all()
        config_obj = None
        if len(config_objs) == 0:
            config_obj = Config.objects.create()
        else:
            config_obj = config_objs[0]

        config_obj.app_url = app_url
        config_obj.no_of_bots_allowed = no_of_bots_allowed
        config_obj.monthly_analytics_parameter = monthly_analytics_parameter
        config_obj.allow_bot_switch = allow_bot_switch
        config_obj.is_bot_shareable = is_bot_shareable
        config_obj.daily_analytics_parameter = daily_analytics_parameter
        config_obj.is_google_search_allowed = is_google_search_allowed
        config_obj.sample_questions = sample_questions
        config_obj.is_feedback_required = is_feedback_required
        config_obj.show_licence = show_licence
        config_obj.top_intents_parameter = top_intents_parameter
        config_obj.cached_duration = cached_duration
        config_obj.site_title = site_title
        config_obj.intent_not_found_response = intent_not_found_response
        config_obj.generic_error_response = generic_error_response
        config_obj.prod = prod

        for language in languages_supported:
            config_obj.languages_supported.add(
                easychat_language_dict[str(language)])

        config_obj.save()
        return config_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_config_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_testcase_obj
input params:
    easychat_object: object containing testcase data
    easychat_intent_dict: dict containing intent data
    easychat_profile_dict: dict containing profile data

returns testcase object depend on given testcase data [used while importing bot]
"""


def import_easychat_testcase_obj(easychat_object,
                                 easychat_intent_dict,
                                 easychat_profile_dict):
    try:
        from EasyChatApp.models import TestCase
        sentence = easychat_object["fields"]["sentence"]
        is_active = easychat_object["fields"]["is_active"]
        intent = easychat_object["fields"]["intent"]
        user = easychat_object["fields"]["user"]

        if intent != None:
            intent = easychat_intent_dict[str(intent)]

        if user != None:
            user = easychat_profile_dict[str(user)]

        testcase_obj = TestCase.objects.create(sentence=sentence,
                                               is_active=is_active,
                                               intent=intent,
                                               user=user)

        return testcase_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_testcase_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_misdashboard_obj
input params:
    easychat_object: object containing mis dashboard data
    active_bot_obj: active bot object

returns  mis dashboard object depend on given  mis dashboard data [used while importing bot]
"""


def import_misdashboard_obj(easychat_object,
                            active_bot_obj):
    try:
        from EasyChatApp.models import MISDashboard
        api_response_parameter_used = easychat_object[
            "fields"]["api_response_parameter_used"]
        api_request_packet = easychat_object["fields"]["api_request_packet"]
        user_id = easychat_object["fields"]["user_id"]
        channel_name = easychat_object["fields"]["channel_name"]
        api_request_parameter_used = easychat_object[
            "fields"]["api_request_parameter_used"]
        intent_name = easychat_object["fields"]["intent_name"]
        message_received = easychat_object["fields"]["message_received"]
        api_response_packet = easychat_object["fields"]["api_response_packet"]
        bot_response = easychat_object["fields"]["bot_response"]

        mis_dashboard_obj = MISDashboard.objects.create(api_response_parameter_used=api_response_parameter_used,
                                                        api_request_packet=api_request_packet,
                                                        user_id=user_id,
                                                        channel_name=channel_name,
                                                        api_request_parameter_used=api_request_parameter_used,
                                                        intent_name=intent_name,
                                                        message_received=message_received,
                                                        api_response_packet=api_response_packet,
                                                        bot_response=bot_response,
                                                        bot=active_bot_obj)
        return mis_dashboard_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_misdashboard_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_tagmapper_obj
input params:
    easychat_object: object containing tagmapper data
    easychat_api_tree_dict: dict containing api tree data

returns tagmapper object depend on given tagmapper data [used while importing bot]
"""


def import_easychat_tagmapper_obj(easychat_object,
                                  easychat_api_tree_dict):
    try:
        from EasyChatApp.models import TagMapper
        display_variable = easychat_object["fields"]["display_variable"]
        alias_variable = easychat_object["fields"]["alias_variable"]
        description = easychat_object["fields"]["description"]
        api_tree = easychat_object["fields"]["api_tree"]

        if api_tree != None:
            api_tree = easychat_api_tree_dict[str(api_tree)]

        tag_mapper_obj = TagMapper.objects.create(display_variable=display_variable,
                                                  alias_variable=alias_variable,
                                                  description=description,
                                                  api_tree=api_tree)
        return tag_mapper_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_tagmapper_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_intent_obj
input params:
    easychat_object: object containing intent data
    easychat_tree_dict: dict containing tree data
    easychat_authentication_dict: dict containing authentication data
    easychat_channel_objs_dict: dict containing channel data
    active_bot_obj: active bot object

returns intent object depend on given intent data [used while importing bot]
"""


def import_easychat_intent_obj(easychat_object,
                               easychat_tree_dict,
                               easychat_authentication_dict,
                               easychat_channel_objs_dict,
                               easychat_category_dict,
                               active_bot_obj):
    try:

        name = easychat_object["fields"]["name"]
        tree = easychat_object["fields"]["tree"]
        keywords = easychat_object["fields"]["keywords"]
        training_data = easychat_object["fields"]["training_data"]
        restricted_keywords = easychat_object["fields"]["restricted_keywords"]
        necessary_keywords = easychat_object["fields"]["necessary_keywords"]
        channels = easychat_object["fields"]["channels"]
        threshold = easychat_object["fields"]["threshold"]
        is_feedback_required = easychat_object[
            "fields"]["is_feedback_required"]
        is_authentication_required = easychat_object[
            "fields"]["is_authentication_required"]
        is_part_of_suggestion_list = easychat_object[
            "fields"]["is_part_of_suggestion_list"]
        is_deleted = easychat_object["fields"]["is_deleted"]
        intent_icon = easychat_object["fields"]["intent_icon"]
        build_in_intent_icon = easychat_object["fields"]["build_in_intent_icon"]
        build_in_intent_icon_obj = None
        if build_in_intent_icon:
            build_in_intent_icon_obj = BuiltInIntentIcon.objects.get(
                pk=build_in_intent_icon)
        order_of_response = easychat_object["fields"]["order_of_response"]

        if len(name) > INTENT_TREE_NAME_CHARACTER_LIMIT:
            logger.error("import_easychat_intent_obj: %s at %s -- %s pk = %s",
                         "Intent Name Cannot Contain More Than 500 Characters", str(exc_tb.tb_lineno), intent_obj.is_hidden, intent_pk, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return None, None

        # Support for old database
        is_livechat_enabled = False
        if "is_livechat_enabled" in easychat_object["fields"]:
            is_livechat_enabled = easychat_object[
                "fields"]["is_livechat_enabled"]

        # Support for old database
        is_form_assist_enabled = False
        if "is_form_assist_enabled" in easychat_object["fields"]:
            is_form_assist_enabled = easychat_object[
                "fields"]["is_form_assist_enabled"]

        is_hidden = False
        try:
            if "is_hidden" in easychat_object["fields"]:
                is_hidden = easychat_object["fields"]["is_hidden"]
        except Exception:
            pass

        is_small_talk = False
        if "is_small_talk" in easychat_object["fields"]:
            is_small_talk = easychat_object["fields"]["is_small_talk"]

        is_easy_assist_allowed = False
        if "is_easy_assist_allowed" in easychat_object["fields"]:
            is_easy_assist_allowed = easychat_object[
                "fields"]["is_easy_assist_allowed"]

        is_easy_tms_allowed = False
        if "is_easy_tms_allowed" in easychat_object["fields"]:
            is_easy_tms_allowed = easychat_object[
                "fields"]["is_easy_tms_allowed"]

        auth_type = easychat_object["fields"]["auth_type"]

        # Support for old database
        category = None
        if "category" in easychat_object["fields"]:
            category = easychat_object["fields"]["category"]
        if auth_type != None:
            auth_type = easychat_authentication_dict[str(auth_type)]

        try:
            if category != None:
                category = easychat_category_dict[str(category)]
            else:
                category_obj = Category.objects.filter(
                    name="Others", bot=active_bot_obj)
                if category_obj:
                    category = category_obj[0]
                else:
                    category = Category.objects.create(
                        name="Others", bot=active_bot_obj)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("import_easychat_intent_obj: %s at %s -- %s pk = %s",
                         str(e), str(exc_tb.tb_lineno), intent_obj.is_hidden, intent_pk, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            pass

        if tree != None:
            tree = easychat_tree_dict[str(tree)]
        else:
            return None
        intent_obj = None
        intent_pk = None
        stem_words = get_stem_words_of_sentence(
            name, None, None, None, active_bot_obj)
        stem_words.sort()
        hashed_name = ' '.join(stem_words)
        hashed_name = hashlib.md5(hashed_name.encode()).hexdigest()
        intent_obj = Intent.objects.filter(
            name=name, bots__in=[active_bot_obj])
        if intent_obj.exists():
            intent_obj = intent_obj.first()
            intent_obj.auth_type = auth_type
            intent_obj.is_deleted = is_deleted
            intent_obj.intent_hash = hashed_name
            intent_obj.is_part_of_suggestion_list = is_part_of_suggestion_list
            intent_obj.restricted_keywords = restricted_keywords
            intent_obj.necessary_keywords = necessary_keywords
            intent_obj.is_authentication_required = is_authentication_required
            intent_obj.tree = tree
            intent_obj.threshold = threshold
            intent_obj.is_feedback_required = is_feedback_required
            intent_obj.is_livechat_enabled = is_livechat_enabled
            intent_obj.is_form_assist_enabled = is_form_assist_enabled
            intent_obj.training_data = training_data
            intent_obj.is_hidden = is_hidden
            intent_obj.is_small_talk = is_small_talk
            intent_obj.keywords = keywords
            intent_obj.is_easy_assist_allowed = is_easy_assist_allowed
            intent_obj.is_easy_tms_allowed = is_easy_tms_allowed
            intent_obj.category = category
            intent_obj.intent_icon = intent_icon
            intent_obj.build_in_intent_icon = build_in_intent_icon_obj
            intent_obj.order_of_response = order_of_response
            intent_obj.save()
            intent_pk = intent_obj.pk
            for channel in channels:
                if easychat_channel_objs_dict[str(channel)] != None:
                    intent_obj.channels.add(
                        easychat_channel_objs_dict[str(channel)])
            intent_obj.save()
        else:
            intent_obj = Intent.objects.create(auth_type=auth_type,
                                               is_deleted=is_deleted,
                                               name=name,
                                               intent_hash=hashed_name,
                                               is_part_of_suggestion_list=is_part_of_suggestion_list,
                                               restricted_keywords=restricted_keywords,
                                               necessary_keywords=necessary_keywords,
                                               is_authentication_required=is_authentication_required,
                                               tree=tree,
                                               threshold=threshold,
                                               is_feedback_required=is_feedback_required,
                                               is_livechat_enabled=is_livechat_enabled,
                                               is_form_assist_enabled=is_form_assist_enabled,
                                               training_data=training_data,
                                               is_hidden=is_hidden,
                                               is_small_talk=is_small_talk,
                                               keywords=keywords,
                                               is_easy_assist_allowed=is_easy_assist_allowed,
                                               is_easy_tms_allowed=is_easy_tms_allowed,
                                               category=category,
                                               intent_icon=intent_icon,
                                               build_in_intent_icon=build_in_intent_icon_obj,
                                               order_of_response=order_of_response)

            for channel in channels:
                if easychat_channel_objs_dict[str(channel)] != None:
                    intent_obj.channels.add(
                        easychat_channel_objs_dict[str(channel)])
            intent_obj.bots.add(active_bot_obj)
            intent_pk = intent_obj.pk
            intent_obj.save()

        return intent_obj, intent_pk
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_intent_obj: %s at %s -- %s pk = %s",
                     str(e), str(exc_tb.tb_lineno), intent_obj.is_hidden, intent_pk, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return None, intent_pk


def check_intent_exists(easychat_object, active_bot_obj):
    try:
        name = easychat_object["fields"]["name"]

        if Intent.objects.filter(name=name, bots=active_bot_obj, is_deleted=False):
            return "Intent already exists"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_intent_exists: %s at %s ",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return None


"""
function: import_easychat_trainingtemplatesentence_obj
input params:
    easychat_object: object containing training template sentence data
    
returns training template sentence object depend on given training template sentence data [used while importing bot]
"""


def import_easychat_trainingtemplatesentence_obj(easychat_object):
    try:
        from EasyChatApp.models import TrainingTemplateSentence
        sentence = easychat_object["fields"]["sentence"]

        training_template_sentence_objs = TrainingTemplateSentence.objects.filter(
            sentence__icontains=sentence)

        if len(training_template_sentence_objs) == 0:
            return TrainingTemplateSentence.objects.create(sentence=sentence)
        else:
            return training_template_sentence_objs[0]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_trainingtemplatesentence_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_trainingtemplate_obj
input params:
    easychat_object: object containing training template data
    easychat_trainingtemplatesentence_dict: dict containing training template sentence data
    
returns training template object depend on given training template data [used while importing bot]
"""


def import_easychat_trainingtemplate_obj(easychat_object, easychat_trainingtemplatesentence_dict):
    try:
        from EasyChatApp.models import TrainingTemplate
        sentences = easychat_object["fields"]["sentences"]

        training_template_obj = TrainingTemplate.objects.create()

        for sentence in sentences:
            training_template_obj.sentences.add(
                easychat_trainingtemplatesentence_dict[str(sentence)])

        training_template_obj.save()
        return training_template_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_trainingtemplate_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_processor_validator_obj
input params:
    easychat_object: object containing processor validator data
    easychat_processor_dict: dict containing processor data
    
returns processor validator object depend on given processor validator data [used while importing bot]
"""


def import_easychat_processor_validator_obj(easychat_object, easychat_processor_dict):
    try:
        from EasyChatApp.models import ProcessorValidator
        name = easychat_object["fields"]["name"]
        processor = easychat_object["fields"]["processor"]

        if processor != None:
            processor = easychat_processor_dict[str(processor)]

        processor_validator_objs = ProcessorValidator.objects.filter(name=name)

        if len(processor_validator_objs) == 0:
            processor_validator_obj = ProcessorValidator.objects.create(name=name,
                                                                        processor=processor)
            return processor_validator_obj
        else:
            return processor_validator_objs[0]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_processor_validator_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_feedback_obj
input params:
    easychat_object: object containing feedback data
    
returns feedback object depend on given feedback data [used while importing bot]
"""


def import_easychat_feedback_obj(easychat_object):
    try:
        from EasyChatApp.models import Feedback
        rating = easychat_object["fields"]["rating"]
        user_id = easychat_object["fields"]["user_id"]
        comments = easychat_object["fields"]["comments"]

        feedback_obj = Feedback.objects.create(rating=rating,
                                               user_id=user_id,
                                               comments=comments)
        return feedback_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_feedback_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_worddictionary_obj
input params:
    easychat_object: object containing word dictionary data
    
returns word dictionary object depend on given word dictionary data [used while importing bot]
"""


def import_easychat_worddictionary_obj(easychat_object):
    try:
        from EasyChatApp.models import WordDictionary
        word_dict = easychat_object["fields"]["word_dict"]

        word_dict_objs = WordDictionary.objects.all()

        word_dict_obj = None
        if len(word_dict_objs) == 0:
            word_dict_obj = WordDictionary.objects.create(word_dict=word_dict)
        else:
            word_dict_obj = word_dict_objs[0]
            word_dict_obj.word_dict = word_dict
            word_dict_obj.save()

        return word_dict_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_worddictionary_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_easychat_default_intent_obj
input params:
    easychat_object: object containing default intent data
    
returns default intent object depend on given default intent data [used while importing bot]
"""


def import_easychat_default_intent_obj(easychat_object):
    try:
        from EasyChatApp.models import DefaultIntent
        answer = easychat_object["fields"]["answer"]
        intent_name = easychat_object["fields"]["intent_name"]
        variations = easychat_object["fields"]["variations"]

        default_intent_objs = DefaultIntent.objects.filter(
            intent_name__icontains=intent_name)

        if len(default_intent_objs) == 0:
            default_intent_obj = DefaultIntent.objects.create(answer=answer,
                                                              intent_name=intent_name,
                                                              variations=variations)
            return default_intent_obj
        else:
            return default_intent_objs[0]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_easychat_default_intent_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: import_data
input params:
    username: active user's username
    active_bot_obj: active bot object
    imported_file_path: file path of data file
    
imports data to given bot object
"""


def import_data(username, active_bot_obj, imported_file_path, bot_pk, event_obj):
    try:
        intent_pk_reverse_mapping_list = {}
        active_user_obj = User.objects.get(username=username)

        with open(imported_file_path, "r+") as file:
            data_str = file.read()
            import_bot_data(username, data_str, bot_pk, active_user_obj,
                            active_bot_obj, event_obj, intent_pk_reverse_mapping_list)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_data: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        event_obj.is_failed = True
        event_obj.save()


"""
function: import_data_as_zip
input params:
    username: active user's username
    active_bot_obj: active bot object
    imported_file_path: file path of data file
    
imports data to given bot object
"""


def import_data_as_zip(username, active_bot_obj, imported_file_path, bot_pk, event_obj):
    try:
        intent_pk_reverse_mapping_list = {}
        active_user_obj = User.objects.get(username=username)

        with ZipFile(imported_file_path, 'r') as zip:
            zip.extractall(path=settings.MEDIA_ROOT +
                           '/imports/', members=None, pwd=None)

        json_file_path = settings.MEDIA_ROOT + \
            'imports/easychat_datadump/easychat_datadump.json'
        with open(json_file_path, "r+") as file:

            data_str = file.read()
            import_bot_data(username, data_str, bot_pk, active_user_obj,
                            active_bot_obj, event_obj, intent_pk_reverse_mapping_list)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_data_as_zip: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        event_obj.is_failed = True
        event_obj.save()


def import_intent(username, active_bot_obj, imported_file_path, bot_pk, event_obj):
    try:
        intent_pk_reverse_mapping_list = {}
        active_user_obj = User.objects.get(username=username)

        with open(imported_file_path, "r+") as file:
            data_str = file.read()
            json_data_dict = json.loads(data_str)
            easychat_channel_objs_dict = {}
            easychat_processor_dict = {}
            easychat_choice_dict = {}
            easychat_bot_response_dict = {}
            easychat_api_tree_dict = {}
            easychat_tree_dict = {}
            easychat_authentication_dict = {}
            easychat_category_dict = {}
            for easychat_object in json_data_dict["easychat_intents"]:
                intent = check_intent_exists(easychat_object, active_bot_obj)
                if intent == "Intent already exists":
                    event_obj.is_failed = True
                    event_obj.failed_message = 'Intent already exists'
                    event_obj.save()
                    return intent

            event_obj.event_progress += 7
            event_obj.save()

            for easychat_object in json_data_dict["easychat_channels"]:
                existing_pk = easychat_object["pk"]
                imported_channel_obj = import_easychat_channel_object(
                    easychat_object)
                easychat_channel_objs_dict[str(
                    existing_pk)] = imported_channel_obj

            event_obj.event_progress += 7
            event_obj.save()

            # Support for old database
            if "easychat_category" in json_data_dict:
                for easychat_object in json_data_dict["easychat_category"]:
                    existing_pk = easychat_object["pk"]
                    imported_category_obj = import_easychat_category_object(
                        easychat_object, active_bot_obj)
                    easychat_category_dict[str(
                        existing_pk)] = imported_category_obj
                if len(json_data_dict["easychat_category"]) == 0:
                    existing_pk = json_data_dict["easychat_bots"][0]["pk"]
                    other_category = Category.objects.filter(name="Others")
                    if len(other_category) == 0:
                        other_category = Category.objects.create(name="Others")
                    else:
                        other_category = other_category[0]
                    easychat_category_dict["Others"] = other_category

            event_obj.event_progress += 7
            event_obj.save()

            for easychat_object in json_data_dict["easychat_processors"]:
                existing_pk = easychat_object["pk"]
                imported_processor_obj = import_easychat_processor_obj(
                    easychat_object, active_bot_obj.name)
                easychat_processor_dict[str(
                    existing_pk)] = imported_processor_obj

            event_obj.event_progress += 7
            event_obj.save()

            for easychat_object in json_data_dict["easychat_choices"]:
                existing_pk = easychat_object["pk"]
                imported_choice_obj = import_easychat_choice_obj(
                    easychat_object)
                easychat_choice_dict[str(existing_pk)] = imported_choice_obj

            event_obj.event_progress += 7
            event_obj.save()

            for easychat_object in json_data_dict["easychat_botresponses"]:
                existing_pk = easychat_object["pk"]
                imported_bot_response_obj = import_easychat_bot_response_obj(easychat_object,
                                                                             easychat_choice_dict)
                easychat_bot_response_dict[str(
                    existing_pk)] = imported_bot_response_obj

            event_obj.event_progress += 7
            event_obj.save()

            for easychat_object in json_data_dict["easychat_apitrees"]:
                existing_pk = easychat_object["pk"]
                imported_api_tree_obj = import_easychat_api_tree_obj(easychat_object,
                                                                     active_user_obj, active_bot_obj.name)
                easychat_api_tree_dict[str(
                    existing_pk)] = imported_api_tree_obj

            event_obj.event_progress += 7
            event_obj.save()

            for easychat_object in json_data_dict["easychat_trees"]:
                existing_pk = easychat_object["pk"]
                imported_tree_obj = import_easychat_tree_obj(easychat_object,
                                                             easychat_bot_response_dict,
                                                             easychat_processor_dict,
                                                             easychat_api_tree_dict,
                                                             easychat_tree_dict)
                easychat_tree_dict[str(existing_pk)] = imported_tree_obj

            event_obj.event_progress += 7
            event_obj.save()

            # Add Child Tree
            for easychat_object in json_data_dict["easychat_trees"]:
                existing_pk = easychat_object["pk"]
                children = easychat_object["fields"]["children"]

                new_easychat_tree_obj = easychat_tree_dict[str(existing_pk)]
                for child in children:
                    new_easychat_tree_obj.children.add(
                        easychat_tree_dict[str(child)])
                new_easychat_tree_obj.save()

            event_obj.event_progress += 8
            event_obj.save()

            for easychat_object in json_data_dict["easychat_tagmappers"]:
                existing_pk = easychat_object["pk"]
                imported_tag_mapper_obj = import_easychat_tagmapper_obj(  # noqa: F841
                    easychat_object, easychat_api_tree_dict)

            event_obj.event_progress += 8
            event_obj.save()

            # key -> imported_intent_pk
            # value -> export_intent_pk
            reverse_map_intent_key = {}

            for easychat_object in json_data_dict["easychat_intents"]:
                existing_pk = easychat_object["pk"]
                try:
                    imported_intent_obj, intent_pk = import_easychat_intent_obj(easychat_object,  # noqa: F841
                                                                                easychat_tree_dict,
                                                                                easychat_authentication_dict,
                                                                                easychat_channel_objs_dict,
                                                                                easychat_category_dict,
                                                                                active_bot_obj)
                    reverse_map_intent_key[str(existing_pk)] = str(intent_pk)
                    intent_pk_reverse_mapping_list[
                        str(existing_pk)] = str(imported_intent_obj.pk)
                except Exception:
                    logger.warning("intent already exist:", extra={
                                   'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            reverse_map_recommendations(
                easychat_bot_response_dict, intent_pk_reverse_mapping_list)

            event_obj.event_progress += 20
            event_obj.save()

            for easychat_object in json_data_dict["easychat_processor_validators"]:
                existing_pk = easychat_object["pk"]
                imported_processor_validator_obj = import_easychat_processor_validator_obj(  # noqa: F841
                    easychat_object, easychat_processor_dict)

            event_obj.event_progress += 8
            event_obj.is_completed = True
            event_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_intent: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        event_obj.is_failed = True
        event_obj.save()


def update_or_create_bot_response_obj(response_pk, multilingual_text_response, language_obj):
    try:
        response_obj = BotResponse.objects.get(pk=response_pk)

        sentence = ""
        if LanguageTuningBotResponseTable.objects.filter(bot_response=response_obj, language=language_obj):
            lang_bot_resp_obj = LanguageTuningBotResponseTable.objects.filter(
                bot_response=response_obj, language=language_obj).first()
            if multilingual_text_response == "":
                return lang_bot_resp_obj
            sentence = json.loads(lang_bot_resp_obj.sentence)
            sentence["items"][0]["text_response"] = multilingual_text_response
        else:
            lang_bot_resp_obj = LanguageTuningBotResponseTable.objects.create(
                language=language_obj, bot_response=response_obj)
            if multilingual_text_response == "":
                eng_text_resp = json.loads(response_obj.sentence)[
                    "items"][0]["text_response"]
                multilingual_text_response = get_translated_text(
                    eng_text_resp, language_obj.lang, EasyChatTranslationCache)

            validation_obj = EasyChatInputValidation()

            sentence = json.loads(lang_bot_resp_obj.sentence)
            sentence["items"][0]["text_response"] = multilingual_text_response
            sentence["items"][0]["speech_response"] = validation_obj.remo_html_from_string(
                multilingual_text_response)
            sentence["items"][0][
                "text_reprompt_response"] = multilingual_text_response
            sentence["items"][0][
                "speech_reprompt_response"] = multilingual_text_response
        sentence = json.dumps(sentence)
        lang_bot_resp_obj.sentence = sentence
        lang_bot_resp_obj.save()
        return lang_bot_resp_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_or_create_bot_response_obj: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


def update_or_create_language_fine_tuned_objects_for_bot(intent_pk, tree_pk, mulitlingual_name, response_pk, multilingual_text_response, language_obj, bot_id):
    try:
        intent_obj = Intent.objects.filter(pk=intent_pk)

        if intent_obj.exists():
            intent_obj = intent_obj.first()
            intent_bot_id = intent_obj.bots.all()[0].pk
            lang_tree_obj = None
            if intent_bot_id != bot_id:
                return 400, "Intent's Does not belong to this Bot"
            lang_bot_respone_obj = update_or_create_bot_response_obj(
                response_pk, multilingual_text_response, language_obj)
            if intent_obj.tree.pk == tree_pk:
                # not a flow intent
                if LanguageTuningIntentTable.objects.filter(language=language_obj, intent=intent_obj).exists():
                    if mulitlingual_name != "":
                        language_tuned_intent_obj = LanguageTuningIntentTable.objects.filter(
                            language=language_obj, intent=intent_obj).first()
                        language_tuned_intent_obj.multilingual_name = mulitlingual_name
                        lang_tree_obj = language_tuned_intent_obj.tree
                        lang_tree_obj.multilingual_name = mulitlingual_name
                        language_tuned_intent_obj.save()
                        lang_tree_obj.save()
                else:
                    if mulitlingual_name == "":
                        mulitlingual_name = get_translated_text(
                            intent_obj.name, language_obj.lang, EasyChatTranslationCache)
                    lang_tree_obj = LanguageTuningTreeTable.objects.create(
                        tree=intent_obj.tree, multilingual_name=mulitlingual_name, language=language_obj, response=lang_bot_respone_obj)
                    LanguageTuningIntentTable.objects.get_or_create(intent=intent_obj, language=language_obj, defaults={"multilingual_name": mulitlingual_name, "tree": lang_tree_obj})
            else:
                # this is a flow tree
                tree_obj = Tree.objects.get(pk=tree_pk)
                if LanguageTuningTreeTable.objects.filter(tree=tree_obj, language=language_obj).exists():
                    if mulitlingual_name != "":
                        lang_tree_obj = LanguageTuningTreeTable.objects.filter(
                            tree=tree_obj, language=language_obj).first()
                        lang_tree_obj.multilingual_name = mulitlingual_name
                        lang_tree_obj.save()
                else:
                    if mulitlingual_name == "":
                        mulitlingual_name = get_translated_text(
                            tree_obj.name, language_obj.lang, EasyChatTranslationCache)
                    lang_tree_obj = LanguageTuningTreeTable.objects.create(
                        tree=tree_obj, multilingual_name=mulitlingual_name, language=language_obj, response=lang_bot_respone_obj)
        return 200, "Import Succesfull"

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_language_object: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return 500, "Unable to Update Intent"


def add_multilingual_intents_into_bot_from_excel(file_path, bot_id, event_obj):
    try:
        validation_obj = EasyChatInputValidation()

        wb = xlrd.open_workbook(file_path)
        intent_trans_sheet = wb.sheet_by_index(1)
        response_trans_sheet = wb.sheet_by_index(2)
        rows_limit = intent_trans_sheet.nrows
        no_of_cols = intent_trans_sheet.ncols

        if no_of_cols < 3:
            event_obj.is_failed = True
            event_obj.failed_message = "No Language Found for Fine Tuning!"
            event_obj.save()
            return 400, "No Language Found for Fine Tuning!"

        progress_interval = 100 / (no_of_cols - 2)

        for col in range(2, no_of_cols):
            lang = (intent_trans_sheet.cell_value(0, col)).split("-")[1]
            lang = lang.strip()
            language_objs = Language.objects.filter(lang=lang)
            if not language_objs.exists():
                continue

            language_obj = language_objs[0]
            for row in range(1, rows_limit):
                intent_pk, tree_pk = get_intent_tree_pk(
                    intent_trans_sheet.cell_value(row, 0))
                mulitlingual_name = intent_trans_sheet.cell_value(
                    row, col).strip()
                mulitlingual_name = validation_obj.remo_html_from_string(
                    mulitlingual_name)
                response_pk = int(response_trans_sheet.cell_value(row, 0))
                multilingual_text_response = response_trans_sheet.cell_value(
                    row, col).strip()
                multilingual_text_response = validation_obj.remo_html_from_string(
                    multilingual_text_response)
                if mulitlingual_name == "" and multilingual_text_response == "":
                    continue
                status, status_message = update_or_create_language_fine_tuned_objects_for_bot(
                    intent_pk, tree_pk, mulitlingual_name, response_pk, multilingual_text_response, language_obj, bot_id)
                if status == 400:
                    event_obj.is_failed = True
                    event_obj.failed_message = status_message
                    event_obj.save()
                    return status, status_message

            event_obj.event_progress = min(
                event_obj.event_progress + int(progress_interval), 100)
            event_obj.save()

        event_obj.event_progress = 100
        event_obj.is_completed = True
        event_obj.save()
        return 200, "Language fine tunning export succesful."
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_multilingual_intents_into_bot_from_excel: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        event_obj.is_failed = True
        event_obj.save()


def get_intent_tree_pk(intent_tree_pk):
    intent_tree_pk = intent_tree_pk.split(",")
    intent_pk = int(intent_tree_pk[0])
    tree_pk = int(intent_tree_pk[1])
    return intent_pk, tree_pk


def import_bot_data(username, data_str, bot_pk, active_user_obj, active_bot_obj, event_obj, intent_pk_reverse_mapping_list):
    try:
        json_data_dict = json.loads(data_str)
        easychat_channel_objs_dict = {}
        easychat_processor_dict = {}
        easychat_choice_dict = {}
        easychat_bot_response_dict = {}
        easychat_api_tree_dict = {}
        easychat_tree_dict = {}
        easychat_authentication_dict = {}
        easychat_trainingtemplatesentence_dict = {}
        easychat_category_dict = {}

        for easychat_object in json_data_dict["easychat_channels"]:
            existing_pk = easychat_object["pk"]
            imported_channel_obj = import_easychat_channel_object(
                easychat_object)
            easychat_channel_objs_dict[str(
                existing_pk)] = imported_channel_obj

        event_obj.event_progress += 5
        event_obj.save()

        # Support for old database
        if "easychat_category" in json_data_dict:
            for easychat_object in json_data_dict["easychat_category"]:
                existing_pk = easychat_object["pk"]
                imported_category_obj = import_easychat_category_object(
                    easychat_object, active_bot_obj)
                easychat_category_dict[str(
                    existing_pk)] = imported_category_obj
            if len(json_data_dict["easychat_category"]) == 0:
                existing_pk = json_data_dict["easychat_bots"][0]["pk"]
                other_category = Category.objects.filter(name="Others")
                if len(other_category) == 0:
                    other_category = Category.objects.create(name="Others")
                else:
                    other_category = other_category[0]
                easychat_category_dict["Others"] = other_category

        event_obj.event_progress += 5
        event_obj.save()

        if "easychat_wordmappers" in json_data_dict:
            for easychat_object in json_data_dict["easychat_wordmappers"]:
                existing_pk = easychat_object["pk"]
                imported_word_mapper_obj = import_easychat_word_mapper_obj(easychat_object,  # noqa: F841
                                                                            active_bot_obj)

        event_obj.event_progress += 5
        event_obj.save()

        for easychat_object in json_data_dict["easychat_processors"]:
            existing_pk = easychat_object["pk"]
            imported_processor_obj = import_easychat_processor_obj(
                easychat_object, active_bot_obj.name)
            easychat_processor_dict[str(
                existing_pk)] = imported_processor_obj

        event_obj.event_progress += 5
        event_obj.save()

        for easychat_object in json_data_dict["easychat_choices"]:
            existing_pk = easychat_object["pk"]
            imported_choice_obj = import_easychat_choice_obj(
                easychat_object)
            easychat_choice_dict[str(existing_pk)] = imported_choice_obj

        event_obj.event_progress += 5
        event_obj.save()

        for easychat_object in json_data_dict["easychat_botresponses"]:
            existing_pk = easychat_object["pk"]
            imported_bot_response_obj = import_easychat_bot_response_obj(easychat_object,
                                                                         easychat_choice_dict)
            easychat_bot_response_dict[str(
                existing_pk)] = imported_bot_response_obj

        event_obj.event_progress += 5
        event_obj.save()

        for easychat_object in json_data_dict["easychat_apitrees"]:
            existing_pk = easychat_object["pk"]
            imported_api_tree_obj = import_easychat_api_tree_obj(easychat_object,
                                                                 active_user_obj, active_bot_obj.name)
            easychat_api_tree_dict[str(
                existing_pk)] = imported_api_tree_obj

        event_obj.event_progress += 5
        event_obj.save()

        for easychat_object in json_data_dict["easychat_trees"]:
            # for easychat_object in json_data_dict["easychat_trees"]:
            existing_pk = easychat_object["pk"]
            imported_tree_obj = import_easychat_tree_obj(easychat_object,
                                                         easychat_bot_response_dict,
                                                         easychat_processor_dict,
                                                         easychat_api_tree_dict,
                                                         easychat_tree_dict)
            easychat_tree_dict[str(existing_pk)] = imported_tree_obj

        event_obj.event_progress += 5
        event_obj.save()

        # Add Child Tree
        for easychat_object in json_data_dict["easychat_trees"]:
            existing_pk = easychat_object["pk"]
            children = easychat_object["fields"]["children"]

            new_easychat_tree_obj = easychat_tree_dict[str(existing_pk)]
            for child in children:
                new_easychat_tree_obj.children.add(
                    easychat_tree_dict[str(child)])
            new_easychat_tree_obj.save()

        event_obj.event_progress += 5
        event_obj.save()

        for easychat_object in json_data_dict["easychat_authentications"]:
            existing_pk = easychat_object["pk"]
            imported_authentication_obj = import_easychat_authentication_obj(easychat_object,
                                                                             easychat_tree_dict)
            easychat_authentication_dict[
                str(existing_pk)] = imported_authentication_obj

        event_obj.event_progress += 5
        event_obj.save()

        for easychat_object in json_data_dict["easychat_tagmappers"]:
            existing_pk = easychat_object["pk"]
            imported_tag_mapper_obj = import_easychat_tagmapper_obj(  # noqa: F841
                easychat_object, easychat_api_tree_dict)

        # key -> imported_intent_pk
        # value -> export_intent_pk
        reverse_map_intent_key = {}

        event_obj.event_progress += 5
        event_obj.save()

        total_intents = len(json_data_dict["easychat_intents"])
        progress_each_intent = 15 / total_intents

        total_progress = 0
        for easychat_object in json_data_dict["easychat_intents"]:
            existing_pk = easychat_object["pk"]
            try:
                imported_intent_obj, intent_pk = import_easychat_intent_obj(easychat_object,  # noqa: F841
                                                                            easychat_tree_dict,
                                                                            easychat_authentication_dict,
                                                                            easychat_channel_objs_dict,
                                                                            easychat_category_dict,
                                                                            active_bot_obj)
                reverse_map_intent_key[str(existing_pk)] = str(intent_pk)
                intent_pk_reverse_mapping_list[
                    str(existing_pk)] = str(imported_intent_obj.pk)
            except Exception:
                logger.warning("intent already exist:", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            total_progress += progress_each_intent

            if (total_progress >= 1):
                event_obj.event_progress += 1
                event_obj.save()
                total_progress = total_progress - 1

        event_obj.event_progress = 70
        event_obj.save()

        reverse_map_recommendations(
            easychat_bot_response_dict, intent_pk_reverse_mapping_list)

        for easychat_object in json_data_dict["easychat_trainingtemplatesentence"]:
            existing_pk = easychat_object["pk"]
            imported_training_template_sentence = import_easychat_trainingtemplatesentence_obj(  # noqa: F841
                easychat_object)
            easychat_trainingtemplatesentence_dict[str(
                existing_pk)] = imported_training_template_sentence

        event_obj.event_progress += 5
        event_obj.save()

        for easychat_object in json_data_dict["easychat_trainingsentence"]:
            existing_pk = easychat_object["pk"]
            imported_trainingtemplate_obj = import_easychat_trainingtemplate_obj(  # noqa: F841
                easychat_object, easychat_trainingtemplatesentence_dict)

        event_obj.event_progress += 5
        event_obj.save()

        for easychat_object in json_data_dict["easychat_processor_validators"]:
            existing_pk = easychat_object["pk"]
            imported_processor_validator_obj = import_easychat_processor_validator_obj(  # noqa: F841
                easychat_object, easychat_processor_dict)

        event_obj.event_progress += 5
        event_obj.save()

        for easychat_object in json_data_dict["easychat_botchannels"]:
            existing_pk = easychat_object["pk"]
            imported_bot_channel_obj = import_easychat_bot_channel_obj(easychat_object,  # noqa: F841
                                                                        easychat_channel_objs_dict,
                                                                        active_bot_obj,
                                                                        reverse_map_intent_key)

        if 'easychat_welcomebanners' in json_data_dict:
            for welcome_banner_obj in json_data_dict["easychat_welcomebanners"]:
                if 'fields' in welcome_banner_obj:
                    import_easychat_welcome_banner_obj(welcome_banner_obj['fields'],
                                                       active_bot_obj,
                                                       reverse_map_intent_key)

        if 'easychat_emojibotresponse' in json_data_dict:
            for emoji_bot_response_obj in json_data_dict["easychat_emojibotresponse"]:
                if 'fields' in emoji_bot_response_obj:
                    import_emoji_bot_response_obj(emoji_bot_response_obj['fields'],
                                                  active_bot_obj)

        if 'easychat_analyticsmonitoring' in json_data_dict:
            for analytics_monitoring_obj in json_data_dict["easychat_analyticsmonitoring"]:
                if 'fields' in analytics_monitoring_obj:
                    import_analytics_monitoring_obj(analytics_monitoring_obj['fields'],
                                                    active_bot_obj)

        if 'easychat_nps' in json_data_dict:
            for nps_obj in json_data_dict['easychat_nps']:
                if 'fields' in nps_obj:
                    import_nps_obj(nps_obj['fields'],
                                   active_bot_obj)

        if 'easychat_csatfeedbackdetails' in json_data_dict:
            for csat_feedback_obj in json_data_dict['easychat_csatfeedbackdetails']:
                if 'fields' in csat_feedback_obj:
                    import_csat_feedback_obj(csat_feedback_obj['fields'],
                                             active_bot_obj)

        event_obj.event_progress += 5
        event_obj.save()

        for easychat_object in json_data_dict["easychat_bots"]:
            existing_pk = easychat_object["pk"]
            try:
                user_obj = User.objects.get(username=str(username))
                bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                    user_obj], is_deleted=False)
                manage_default_livechat_intent(easychat_object[
                    "fields"]["is_livechat_enabled"], bot_obj)
                manage_bot_to_admin_account(user_obj, easychat_object[
                    "fields"]["is_livechat_enabled"], bot_obj)
            except Exception:
                pass
            imported_bot_settings = import_easychat_bot_settings(easychat_object,  # noqa: F841
                                                                    active_bot_obj,
                                                                    reverse_map_intent_key)

        event_obj.event_progress += 5
        event_obj.save()

        try:
            common_utils_object = CommonUtilsFile.objects.get(
                bot=Bot.objects.get(pk=int(bot_pk)))
            common_utils_object.code = common_utils_object.code + \
                "\n" + json_data_dict['content']
            common_utils_object.save()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("No common utils: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            CommonUtilsFile.objects.create(bot=Bot.objects.get(
                pk=int(bot_pk)), code=json_data_dict['content'])
            pass

        event_obj.event_progress += 5
        event_obj.is_completed = True
        event_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("import_bot_data: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        event_obj.is_failed = True
        event_obj.save()
