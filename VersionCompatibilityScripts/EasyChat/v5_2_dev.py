from EasyChatApp.models import *
from EasyChatApp.utils_bot import get_supported_languages, get_translated_text
from EasyChatApp.constants_language import *
from EasyChatApp.constants_icon import *


def create_google_rcs_channel():
    try:
        if Channel.objects.filter(name='GoogleRCS'):
            return

        Channel.objects.create(name='GoogleRCS', icon=GOOGLE_RCS_ICON)
    except Exception as e:
        logger.error("Error in create_google_rcs_channel: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def create_google_rcs_bot_channel_object_for_old_bots():
    try:
        bots = Bot.objects.filter(is_deleted=False)
        channel_obj = Channel.objects.get(name='GoogleRCS')
        languages_supported = Language.objects.get(lang="en")
        for bot in bots:
            if BotChannel.objects.filter(bot=bot, channel=channel_obj):
                continue
            bot_channel = BotChannel.objects.create(
                bot=bot, channel=channel_obj)
            bot_channel.languages_supported.add(languages_supported)
            bot_channel.save()

    except Exception as e:
        logger.error("Error in create_google_rcs_channel_object_for_old_bots: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def add_google_rcs_channel_to_old_bots_intents():
    try:
        channel_obj = Channel.objects.get(name='GoogleRCS')
        intents = Intent.objects.exclude(channels__in=[channel_obj])
        for intent in intents:
            intent.channels.add(channel_obj)
            intent.save()

    except Exception as e:
        logger.error("Error in add_google_rcs_channel_to_old_bots_intents: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def change_rcs_channel_name():
    try:
        channel_obj = Channel.objects.get(name='google_rcs')
        channel_obj.name = 'GoogleRCS'
        channel_obj.save()

    except Exception as e:
        logger.error("Error in change_rcs_channel_name: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_old_bot_template_objects():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        default_language_text = "Do you want to change your language to {}?$$$The language detected in the query is {} is not available in the Bot. Available language in the Bot are: "

        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang
            bot_template_obj.auto_language_detection_text = get_translated_text(
                default_language_text, lang, EasyChatTranslationCache)
            bot_template_obj.save()

    except Exception as e:
        logger.error("Error in update_old_bot_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def create_old_bot_info_objects():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        for bot in bot_objs:
            if BotInfo.objects.filter(bot=bot):
                continue
            activity_update = {
                "is_bot_inactivity_response_updated": "false",
                "is_bot_response_delay_message_updated": "false",
                "is_flow_termination_bot_response_updated": "false",
                "is_flow_termination_confirmation_display_message_updated": "false",
            }
            activity_update = json.dumps(activity_update)

            words_file = os.path.join(
                (os.path.abspath(os.path.dirname(__file__))), 'badwords.txt')

            with open(words_file, 'r') as f:
                censor_list = [line.strip() for line in f.readlines()]

            bad_words = json.dumps(censor_list)

            BotInfo.objects.create(
                bot=bot, activity_update=activity_update, bad_keywords=bad_words)

    except Exception as e:
        logger.error("Error in create_old_bot_info_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


create_google_rcs_channel()
create_google_rcs_bot_channel_object_for_old_bots()
add_google_rcs_channel_to_old_bots_intents()
change_rcs_channel_name()
update_old_bot_template_objects()
create_old_bot_info_objects()
