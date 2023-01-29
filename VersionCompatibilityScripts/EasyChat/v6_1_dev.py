from EasyChatApp.models import *
from EasyChatApp.constants_icon import *
from EasyChatApp.constants import DEFAULT_THEME_IMAGE_DICT
import json

from EasyChatApp.utils_bot import get_translated_text


def create_theme_four_object():
    try:
        if not EasyChatTheme.objects.filter(name="theme_4").exists():
            EasyChatTheme.objects.create(
                name="theme_4", main_page="EasyChatApp/theme4_bot.html", chat_page="EasyChatApp/theme4.html", theme_image_paths=json.dumps(DEFAULT_THEME_IMAGE_DICT["theme_4"]))

    except Exception as e:
        logger.error("Error in create_theme_four_object: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_old_bot_template_objects():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        frequently_asked_questions_text = "Frequently asked questions$$$Questions customer ask oftenly$$$Search here$$$View All$$$Was it helpful?$$$Skip$$$Ask your query"

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.frequently_asked_questions_text = get_translated_text(
                frequently_asked_questions_text, lang, EasyChatTranslationCache)

            bot_template_obj.save()

    except Exception as e:
        logger.error("Error in update_old_bot_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_old_bot_template_csat_text():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        csat_emoji_text = "Angry$$$Sad$$$Neutral$$$Happy$$$Very Happy"

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.csat_emoji_text = get_translated_text(
                csat_emoji_text, lang, EasyChatTranslationCache)

            bot_template_obj.save()

    except Exception as e:
        logger.error("Error in update_old_bot_template_csat_text: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_old_bot_template_chat_with_text():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        chat_with_text = "Chat with"

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.chat_with_text = get_translated_text(
                chat_with_text, lang, EasyChatTranslationCache)

            bot_template_obj.save()

    except Exception as e:
        logger.error("Error in update_old_bot_template_chat_with_text: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def create_viber_bot_channel_object_for_old_bots():
    try:
        bots = Bot.objects.filter(is_deleted=False)
        channel_obj = Channel.objects.get(name='Viber')
        languages_supported = Language.objects.get(lang="en")
        for bot in bots:
            if BotChannel.objects.filter(bot=bot, channel=channel_obj):
                continue
            bot_channel = BotChannel.objects.create(
                bot=bot, channel=channel_obj)
            bot_channel.languages_supported.add(languages_supported)
            bot_channel.save()

    except Exception as e:
        logger.error("Error in create_viber_bot_channel_object_for_old_bots: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def create_viber_bot_configuration_objects():
    try:
        viber_obj = Channel.objects.filter(name='Viber').first()
        if not viber_obj:
            Channel.objects.create(name='Viber', icon=VIBER_ICON)
    except Exception as e:
        logger.error("Error in create_viber_bot_configuration_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def add_viber_channel_to_old_bots_intents():
    try:
        channel_obj = Channel.objects.get(name='Viber')
        intents = Intent.objects.exclude(channels__in=[channel_obj])
        for intent in intents:
            intent.channels.add(channel_obj)

    except Exception as e:
        logger.error("Error in add_viber_channel_to_old_bots_intents: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def add_intent_pk_in_old_bot_template_web_url_landing_data():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)
        for bot_obj in bot_objs:

            if "intent_name" in bot_obj.web_url_landing_data:
                
                web_url_landing_data = json.loads(bot_obj.web_url_landing_data)

                for idx, data in enumerate(web_url_landing_data):
                    trigger_intent_pk = Intent.objects.get(name=data["intent_name"], is_deleted=False, bots__in=[bot_obj]).pk
                    web_url_landing_data[idx]["trigger_intent_pk"] = str(trigger_intent_pk)

                bot_obj.web_url_landing_data = json.dumps(web_url_landing_data)
                bot_obj.save()

            bot_language_tuned_objs = LanguageTunedBot.objects.filter(bot=bot_obj)
            for bot_language_tuned_obj in bot_language_tuned_objs:
                web_url_landing_data = json.loads(bot_language_tuned_obj.web_url_landing_data)

                for idx, data in enumerate(web_url_landing_data):
                    trigger_intent_pk = Intent.objects.get(name=data["intent_name"], is_deleted=False, bots__in=[bot_obj]).pk
                    web_url_landing_data[idx]["trigger_intent_pk"] = str(trigger_intent_pk)

                bot_language_tuned_obj.web_url_landing_data = json.dumps(web_url_landing_data)
                bot_language_tuned_obj.save()

    except Exception as e:
        logger.error("Error in add_intent_pk_in_old_bot_template_web_url_landing_data: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_reset_datapipe_processor():
    try:
        processor_objs = Processor.objects.filter(
            name__icontains="reset_pipe_processor_")
        code = '''
from EasyChatApp.utils import logger
import sys
def f(x):
    json_response = {}
    json_response['status_code'] = '500'
    json_response['status_message'] = 'Internal server error.'
    json_response['recur_flag'] = False
    json_response['message'] = 'reset_pipe_processor'
    json_response['API_REQUEST_PACKET'] = {}
    json_response['API_RESPONSE_PACKET'] = {}
    json_response['data'] = {}
    try:
        #write your code here
        json_response['recur_flag'] = True
        json_response['status_code'] = '200'
        json_response['print'] = 'Hello world!'
        return json_response
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('PipeProcessorContent: %s at %s',str(E), str(exc_tb.tb_lineno))
        json_response['status_code'] = '500'
        json_response['status_message'] = 'ERROR :-  '+str(E)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return json_response
        '''

        for processor_obj in processor_objs:
            processor_obj.function = code
            processor_obj.save()

        confirm_reset_parent_objs = Tree.objects.filter(
            name__icontains="ConfirmReset")
        for confirm_reset_parent_obj in confirm_reset_parent_objs:
            confirm_reset_parent_obj.accept_keywords += ",confirm reset"
            confirm_reset_parent_obj.save()

    except Exception as e:
        logger.error("Error in update_reset_datapipe_processor: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running create_theme_four_object...\n")

create_theme_four_object()

print("Running update_old_bot_template_objects...\n")

update_old_bot_template_objects()

print("Running update_old_bot_template_csat_text...\n")

update_old_bot_template_csat_text()

print("Running update_old_bot_template_chat_with_text...\n")

update_old_bot_template_chat_with_text()

print("Running create_viber_bot_configuration_objects...\n")

create_viber_bot_configuration_objects()

print("Running create_viber_bot_channel_object_for_old_bots...\n")

create_viber_bot_channel_object_for_old_bots()

print("Running add_viber_channel_to_old_bots_intents...\n")

add_viber_channel_to_old_bots_intents()

print("Running add_intent_pk_in_old_bot_template_web_url_landing_data...\n")

add_intent_pk_in_old_bot_template_web_url_landing_data()

print("Running update_reset_datapipe_processor...\n")

update_reset_datapipe_processor()
