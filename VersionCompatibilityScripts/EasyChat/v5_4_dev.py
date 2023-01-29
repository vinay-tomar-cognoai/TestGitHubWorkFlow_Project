from EasyChatApp.models import *
from EasyChatApp.constants_icon import *
from EasyChatApp.utils_bot import get_translated_text, get_translated_text_with_api_status
from EasyChatApp.utils_execute_query import get_hashed_intent_name
from EasyChatApp.intent_icons_constants import INTENT_ICONS
from EasyChatApp.constants_icon import GOOGLE_BUSINESS_MESSAGES_ICON, TWITTER_ICON, GOOGLE_RCS_ICON


def create_built_in_intent_icons():

    for intent_icon in INTENT_ICONS:
        intent_icon_obj = BuiltInIntentIcon.objects.filter(
            unique_id=intent_icon[0]).first()
        if not intent_icon_obj:
            BuiltInIntentIcon.objects.create(
                unique_id=intent_icon[0], icon=intent_icon[1])


def update_gmb_channel_name():
    try:
        gmbchannel = Channel.objects.filter(name="GoogleMyBusiness")
        for gmb in gmbchannel:
            gmb.name = "GoogleBusinessMessages"
            gmb.icon = GOOGLE_BUSINESS_MESSAGES_ICON
            gmb.save()
    except Exception as e:
        logger.error("Error in create_google_rcs_channel: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_twitter_channel_name():
    try:
        twitter_channel = Channel.objects.filter(name="Twitter")
        for twitter in twitter_channel:
            twitter.icon = TWITTER_ICON
            twitter.save()
    except Exception as e:
        logger.error("Error in create_twitter_channel: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_grcs_channel_name():
    try:
        grcs_channel = Channel.objects.filter(name="GoogleRCS")
        for grcs in grcs_channel:
            grcs.icon = GOOGLE_RCS_ICON
            grcs.save()
    except Exception as e:
        logger.error("Error in create_googlercs_channel: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_old_bot_template_objects():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        bot_template_objs = RequiredBotTemplate.objects.filter(
            bot__in=bot_objs)

        default_language_text = "Submit$$$Confirm"
        updated_choose_langauge_text = "Choose Language$$$Disclaimer"
        mic_text = "Microphone"
        genreal_text = "Did you mean one of the following?$$$There are some internal issue, please try again later. Sorry for your inconvenience.$$$Looks like I don't have answer for selected bot query.$$$Looks like I don't have support for this channel.$$$Session is running in another tab. Please end running sessions and try again.$$$I can tell you are upset. If my answers were not helpful, you can reach out to our customer care team.$$$Sorry to hear that, we would appreciate if you could give your comments on what went wrong. Please type 'Skip' in case you don't wish to give a comment.$$$Glad that you liked our service. Hope to see you again.$$$Thanks, we would try to improve.$$$Looks like I don't have an answer to that. Here's what I found on the web.$$$Sure, How may I assist you now?$$$Looks like, I can not not answer your query for now. Please try again after some time.$$$Read More$$$Read Less$$$Show Less$$$View more$$$speak now"
        for bot_template_obj in bot_template_objs:

            lang = bot_template_obj.language.lang

            bot_template_obj.mic_button_tooltip = get_translated_text(
                mic_text, lang, EasyChatTranslationCache)
            bot_template_obj.submit_text = get_translated_text(
                default_language_text, lang, EasyChatTranslationCache)
            bot_template_obj.choose_language = get_translated_text(
                updated_choose_langauge_text, lang, EasyChatTranslationCache)
            bot_template_obj.general_text = get_translated_text(
                genreal_text, lang, EasyChatTranslationCache)
            bot_template_obj.save()

    except Exception as e:
        logger.error("Error in update_old_bot_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_bot_channel_obj_disclaimer_text():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        disclaimer_text = "This will translate conversations across the bot into Language selected and translations might not be accurate everywhere. Do you still want to continue?"

        channels = Channel.objects.filter(name__in=["Web", "Android", "iOS"])

        bot_channels = BotChannel.objects.filter(
            bot__in=bot_objs, channel__in=channels)
        for bot_channel in bot_channels:
            bot_channel.phonetic_typing_disclaimer_text = disclaimer_text
            bot_channel.save()
    except Exception as e:
        logger.error("Error in update_old_bot_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_chinease_language_code():
    try:
        chinese_lang = Language.objects.filter(lang="zh-CN").first()

        if chinese_lang:
            chinese_lang.lang = "zh"
            chinese_lang.save()

    except Exception as e:
        logger.error("Error in update_old_bot_template_objects: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def disable_lead_generation_if_form_assist_enabled():
    try:
        bot_objs = Bot.objects.filter(is_form_assist_enabled=True)
        for bot_obj in bot_objs:
            bot_obj.is_lead_generation_enabled = False
            bot_obj.save()

    except Exception as e:
        logger.error("Error in disable_lead_generation_if_form_assist_enabled: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_powered_by_text_of_language_template_object():
    try:
        language_template_objs = RequiredBotTemplate.objects.all()

        for language_template_obj in language_template_objs:
            language_template_obj.powered_by_text = get_translated_text_with_api_status(
                language_template_obj.powered_by_text, language_template_obj.language.lang, EasyChatTranslationCache, True)[0]
            language_template_obj.save()

    except Exception as e:
        logger.error("Error in update_powered_by_text_of_language_template_object: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_intent_hash_of_old_intents():
    try:
        intent_objs = Intent.objects.filter(intent_hash="", is_deleted=False)
        for intent in intent_objs:
            bot_obj = intent.bots.all()[0]
            hashed_name = get_hashed_intent_name(intent.name, bot_obj)
            intent.intent_hash = hashed_name        
            intent.save()
    except Exception as e:
        logger.error("Error in update_powered_by_text_of_language_template_object: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def create_ivr_channel():
    try:
        if Channel.objects.filter(name='IVR'):
            return

        Channel.objects.create(name='IVR', icon=IVR_ICON)
    except Exception as e:
        logger.error("Error in create_ivr_channel: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def create_ivr_bot_channel_object_for_old_bots():
    try:
        bots = Bot.objects.filter(is_deleted=False)
        channel_obj = Channel.objects.get(name='IVR')
        languages_supported = Language.objects.get(lang="en")
        for bot in bots:
            if BotChannel.objects.filter(bot=bot, channel=channel_obj):
                continue
            bot_channel = BotChannel.objects.create(
                bot=bot, channel=channel_obj)
            bot_channel.languages_supported.add(languages_supported)
            bot_channel.save()

    except Exception as e:
        logger.error("Error in create_ivr_bot_channel_object_for_old_bots: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def add_ivr_channel_to_old_bots_intents():
    try:
        channel_obj = Channel.objects.get(name='IVR')
        intents = Intent.objects.exclude(channels__in=[channel_obj])
        for intent in intents:
            intent.channels.add(channel_obj)
            intent.save()

    except Exception as e:
        logger.error("Error in add_ivr_channel_to_old_bots_intents: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running create_ivr_channel...\n")

create_ivr_channel()

print("Completed create_ivr_channel\n")
print("Running create_ivr_bot_channel_object_for_old_bots...\n")

create_ivr_bot_channel_object_for_old_bots()

print("Completed create_ivr_channel\n")
print("Running create_ivr_bot_channel_object_for_old_bots...\n")

add_ivr_channel_to_old_bots_intents()

print("Completed add_ivr_channel_to_old_bots_intents\n")
print("Running update_intent_hash_of_old_intents...\n")

update_intent_hash_of_old_intents()

print("Completed update_intent_hash_of_old_intents\n")
print("Running update_chinease_language_code...\n")

update_chinease_language_code()

print("Completed update_chinease_language_code\n")
print("Running update_bot_channel_obj_disclaimer_text...\n")

update_bot_channel_obj_disclaimer_text()

print("Completed update_bot_channel_obj_disclaimer_text\n")
print("Running update_old_bot_template_objects...\n")

update_old_bot_template_objects()

print("Completed update_old_bot_template_objects\n")
print("Running update_gmb_channel_name...\n")

update_gmb_channel_name()

print("Completed update_gmb_channel_name\n")
print("Running create_built_in_intent_icons...\n")

create_built_in_intent_icons()

print("Completed create_built_in_intent_icons\n")
print("Running update_twitter_channel_name...\n")

update_twitter_channel_name()

print("Completed update_twitter_channel_name\n")
print("Running update_grcs_channel_name...\n")

update_grcs_channel_name()

print("Completed update_grcs_channel_name\n")
print("Running disable_lead_generation_if_form_assist_enabled...\n")

disable_lead_generation_if_form_assist_enabled()

print("Completed disable_lead_generation_if_form_assist_enabled\n")
print("Running update_powered_by_text_of_language_template_object...\n")

update_powered_by_text_of_language_template_object()

print("Completed update_powered_by_text_of_language_template_object\n")
