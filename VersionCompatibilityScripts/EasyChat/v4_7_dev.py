from EasyChatApp.models import *
from EasyChatApp.constants_icon import *
from EasyChatApp.constants import DEFAULT_THEME_IMAGE_DICT
import json


def create_ios_channel():
    try:
        if Channel.objects.filter(name='iOS'):
            return

        Channel.objects.create(name='iOS', icon=IOS_ICON)
    except Exception as e:
        logger.error("Error in create_ios_channel: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        pass


def create_et_source_channel():
    try:
        if Channel.objects.filter(name='ET-Source'):
            return

        Channel.objects.create(name='ET-Source', icon=ET_SOURCE_ICON)
    except Exception as e:
        logger.error("Error in create_et_source_channel: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        pass


def update_icons_for_all_channels():
    try:
        channels = Channel.objects.all()

        for channel in channels:
            if channel.name == "Web":
                channel.icon = WEB_ICON
            elif channel.name == "GoogleHome":
                channel.icon = GOOGLE_HOME_ICON
            elif channel.name == "Alexa":
                channel.icon = ALEXA_ICON
            elif channel.name == "WhatsApp":
                channel.icon = WHATSAPP_ICON
            elif channel.name == "Android":
                channel.icon = ANDROID_ICON
            elif channel.name == "Facebook":
                channel.icon = FACEBOOK_ICON
            elif channel.name == "Microsoft":
                channel.icon = MICROSOFT_ICON
            elif channel.name == "Telegram":
                channel.icon = TELEGRAM_ICON
            elif channel.name == "GoogleMyBusiness":
                channel.icon = GOOGLE_BUSINESS_MESSAGES_ICON
            elif channel.name == "iOS":
                channel.icon = IOS_ICON
            elif channel.name == "ET-Source":
                channel.icon = ET_SOURCE_ICON

            channel.save()
    except Exception as e:
        logger.error("Error in update_icons_for_all_channels: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        pass


def create_easychat_bot_theme_three():
    try:
        if not EasyChatTheme.objects.filter(name="theme_3").exists():

            theme_three_image_paths = json.dumps(
                DEFAULT_THEME_IMAGE_DICT["theme_3"])

            EasyChatTheme.objects.create(
                name="theme_3", main_page="EasyChatApp/theme3_bot.html", chat_page="EasyChatApp/theme3.html", theme_image_paths=theme_three_image_paths)

    except Exception as e:
        logger.error("Error in create_easychat_bot_theme_three: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        pass


def update_access_type_objs():
    try:
        access_type_objs = AccessType.objects.all()

        for access_type_obj in access_type_objs:
            if access_type_obj.name == "Full Access":
                access_type_obj.value = "full_access"
            elif access_type_obj.name == "Intent Related":
                access_type_obj.value = "access_intent_related"
            elif access_type_obj.name == "Bot Setting Related":
                access_type_obj.value = "access_bot_setting"
            elif access_type_obj.name == "Lead Gen Related":
                access_type_obj.value = "access_lead_gen"
            elif access_type_obj.name == "Form Assist Related":
                access_type_obj.value = "access_form_assist"
            elif access_type_obj.name == "Self Learning Related":
                access_type_obj.value = "access_self_learning"
            elif access_type_obj.name == "Analytics Related":
                access_type_obj.value = "access_msg_history_analytics"
            elif access_type_obj.name == "EasyDrive Related":
                access_type_obj.value = "access_easydrive"
            elif access_type_obj.name == "Word Mapper Related":
                access_type_obj.value = "access_word_mapper"
            elif access_type_obj.name == "Create Bot With Excel Related":
                access_type_obj.value = "access_create_bot_with_excel"
            elif access_type_obj.name == "Extract FAQ Related":
                access_type_obj.value = "access_extract_faq"
            elif access_type_obj.name == "Message History Related":
                access_type_obj.value = "access_only_message_history"
            elif access_type_obj.name == "API Analytics Related":
                access_type_obj.value = "access_api_analytics"
            elif access_type_obj.name == "Categories":
                access_type_obj.value = "access_easychat_categories"
            elif access_type_obj.name == "Automated Testing":
                access_type_obj.value = "access_automated_testing"
            elif access_type_obj.name == "Easy Data Collection":
                access_type_obj.value = "access_data_collection"

            access_type_obj.save()

    except Exception as e:
        logger.error("Error in update_access_type_objs: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        pass


def create_bot_channel_object_for_old_bots():
    try:
        bots = Bot.objects.filter(is_deleted=False)

        channel_obj = Channel.objects.get(name='iOS')

        languages_supported = Language.objects.get(lang="en")

        for bot in bots:
            if BotChannel.objects.filter(bot=bot, channel=channel_obj):
                continue
            bot_channel = BotChannel.objects.create(
                bot=bot, channel=channel_obj)
            bot_channel.languages_supported.add(languages_supported)
            bot_channel.save()

    except Exception as e:
        logger.error("Error in create_bot_channel_object_for_old_bots: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
        pass

create_ios_channel()
create_et_source_channel()
update_icons_for_all_channels()
update_access_type_objs()
create_bot_channel_object_for_old_bots()
