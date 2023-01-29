from CampaignApp.models import CampaignChannel, CampaignConfig
from EasyChatApp.models import *
from EasyChatApp.utils_bot import check_and_update_langauge_tuned_bot_configuration, get_translated_text


def add_voice_bot_channel_in_campaign():
    try:
        voice_bot_channel = CampaignChannel.objects.filter(name="Voice Bot")

        if not voice_bot_channel:
            CampaignChannel.objects.create(
                name="Voice Bot",
                description="Start engaging with your customers using the most popular Interactive voice response",
                logo="files/Campaign/voice_bot_channel.svg",
                value="voicebot",
                order=3,
            )

    except Exception as e:
        logger.error("Error in add_voice_bot_channel_in_campaign: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def create_campaign_config_objs():
    try:
        bot_objs = Bot.objects.filter(is_deleted=False)

        for bot_obj in bot_objs:
            config_obj = CampaignConfig.objects.filter(bot=bot_obj)

            if not config_obj:
                CampaignConfig.objects.create(bot=bot_obj)

    except Exception as e:
        logger.error("Error in create_campaign_config_objs: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_campaign_channel_value():
    try:
        channel_objs = CampaignChannel.objects.all()

        for channel in channel_objs:
            if channel.name == 'Whatsapp Business':
                channel.value = 'whatsapp'
            elif channel.name == 'Voice Bot':
                channel.value = 'voicebot'

            channel.save()

    except Exception as e:
        logger.error("Error in update_campaign_channel_value: %s", str(e), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running add_voice_bot_channel_in_campaign...\n")

add_voice_bot_channel_in_campaign()

print("Running create_campaign_config_objs...\n")

create_campaign_config_objs()

print("Running update_campaign_channel_value...\n")

update_campaign_channel_value()
