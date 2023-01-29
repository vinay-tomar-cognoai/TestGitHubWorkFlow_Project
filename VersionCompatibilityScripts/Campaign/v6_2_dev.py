from CampaignApp.models import VoiceBotCallerID, CampaignConfig, CampaignVoiceBotAPI, CampaignVoiceBotDetailedAnalytics
from CampaignApp.constants import VOICE_BOT_SAMPLE_API_CODE
from EasyChatApp.utils import logger


def create_old_voice_caller_objs_for_all_bots():
    try:
        campaign_config_objs = CampaignConfig.objects.all()
        voice_caller_objs = VoiceBotCallerID.objects.filter(bot=None)

        for campaign_config_obj in campaign_config_objs:
            for voice_caller_obj in voice_caller_objs:
                voice_caller_id_obj = VoiceBotCallerID.objects.filter(bot=campaign_config_obj.bot, caller_id=voice_caller_obj.caller_id).first()
                voice_app_id_obj = VoiceBotCallerID.objects.filter(bot=campaign_config_obj.bot, app_id=voice_caller_obj.app_id).first()
                if not voice_caller_id_obj and not voice_app_id_obj:
                    VoiceBotCallerID.objects.create(bot=campaign_config_obj.bot, caller_id=voice_caller_obj.caller_id, app_id=voice_caller_obj.app_id)

        voice_caller_objs.delete()

    except Exception as e:
        logger.error("Error in create_old_voice_caller_objs_for_all_bots: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''}) 


def update_campaign_api_code():
    try:
        api_objs = CampaignVoiceBotAPI.objects.all()
        for api_obj in api_objs:
            api_obj.api_code = VOICE_BOT_SAMPLE_API_CODE
            api_obj.save()
    except Exception as e:
        logger.error("Error in update_campaign_api_code: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def update_null_campaign_objs():
    try:
        CampaignVoiceBotDetailedAnalytics.objects.filter(campaign=None).delete()
    except Exception as e:
        logger.error("Error in update_null_campaign_objs: %s", str(e), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


print("Running create_old_voice_caller_objs_for_all_bots...\n")

create_old_voice_caller_objs_for_all_bots()

print("Running update_campaign_api_code...\n")

update_campaign_api_code()

print("Running update_null_campaign_objs...\n")

update_null_campaign_objs()
