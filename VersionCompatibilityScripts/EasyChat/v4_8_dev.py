from EasyChatApp.models import *
from EasyChatApp.utils_bot import get_supported_languages, get_translated_text
from EasyChatApp.constants_language import *
from EasyChatApp.constants_icon import *
import json


def change_username_to_getcognoai():
    try:
        users = User.objects.all()

        for user in users:
            try:
                if user.email.endswith("@allincall.in"):
                    user.email = user.email.replace(
                        "allincall.in", "getcogno.ai")
                    user.username = user.username.replace(
                        "allincall.in", "getcogno.ai")
                    user.save()
            except:
                logger.warning("Ignore if allincall user exists", extra={
                               'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
                pass

    except Exception as e:
        logger.error("Error in change_username_to_getcognoai: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        pass


def add_default_language_objects():
    try:
        for language in LANGUAGE_LIST:
            name_in_english = language[0]
            lang = language[1]
            if not Language.objects.filter(lang=lang).exists():
                display = get_translated_text(
                    name_in_english, lang, EasyChatTranslationCache)
                Language.objects.create(
                    name_in_english=name_in_english, lang=lang, display=display)

    except Exception as e:
        logger.error("Error in add_default_language_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def set_language_support_for_previous_bots():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)
        for bot in bot_objs:
            languages_supported = bot.languages_supported.all()
            if languages_supported.count() == 0:
                prev_lang_supported = get_supported_languages(bot, BotChannel)
                bot.languages_supported.add(*prev_lang_supported)

                # * adds all objects of the queryset in many 2 many field

    except Exception as e:
        logger.error("Error in set_language_support_for_previous_bots: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def create_instagram_channel():
    try:
        if Channel.objects.filter(name='Instagram'):
            return

        Channel.objects.create(name='Instagram', icon=INSTAGRAM_ICON)
    except Exception as e:
        logger.error("Error in create_instagram_channel: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def create_instagram_bot_channel_object_for_old_bots():
    try:
        bots = Bot.objects.filter(is_deleted=False)
        channel_obj = Channel.objects.get(name='Instagram')
        languages_supported = Language.objects.get(lang="en")

        for bot in bots:
            if BotChannel.objects.filter(bot=bot, channel=channel_obj):
                continue

            bot_channel = BotChannel.objects.create(
                bot=bot, channel=channel_obj)
            bot_channel.languages_supported.add(languages_supported)
            bot_channel.save()

    except Exception as e:
        logger.error("Error in create_instagram_bot_channel_object_for_old_bots: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})

change_username_to_getcognoai()

set_language_support_for_previous_bots()

add_default_language_objects()

create_instagram_channel()

create_instagram_bot_channel_object_for_old_bots()
