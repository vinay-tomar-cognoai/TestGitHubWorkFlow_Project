from datetime import datetime
from CampaignApp.constants import CAMPAIGN_COMPLETED, CAMPAIGN_IN_PROGRESS, CAMPAIGN_PARTIALLY_COMPLETED
from CampaignApp.models import Campaign, CampaignVoiceBotAPI, CampaignVoiceBotAnalytics, CampaignVoiceBotDetailedAnalytics, CampaignVoiceBotSetting, CampaignVoiceUser
from CampaignApp.utils import check_and_create_call_details_obj, check_and_create_voice_bot_api_obj, open_file
from cronjob_scripts.utils_campaign_cronjob_validator import check_if_cronjob_is_running, complete_cronjob_execution

import logging
logger = logging.getLogger(__name__)

import sys
import time
import json


def cronjob():

    cronjob_detector_id = "update_call_details_cronjob"
    is_cronjob_exists, cronjob_tracker_obj = check_if_cronjob_is_running(cronjob_detector_id)
    if is_cronjob_exists:
        return
    
    try:

        call_details_objs = CampaignVoiceBotDetailedAnalytics.objects.filter(
            is_details_fetched=False)

        print(call_details_objs.count())
        for call_details_obj in call_details_objs:
            call_sid = call_details_obj.call_sid

            if call_sid != '':
                api_obj = check_and_create_voice_bot_api_obj(
                    call_details_obj.campaign, CampaignVoiceBotAPI)
                api_code = api_obj.api_code

                processor_check_dictionary = {'open': open_file}

                param = {
                    "call_sid": call_sid,
                    "bot_id": str(call_details_obj.campaign.bot.pk)
                }

                exec(str(api_code), processor_check_dictionary)
                response_body = processor_check_dictionary['get_call_details'](json.dumps(param))

                response = response_body['Call']

                logger.info('call details: %s', str(response),
                            extra={'AppName': 'Campaign'})

                if response:
                    call_details_obj = check_and_create_call_details_obj(
                        call_details_obj.campaign, response['Sid'], CampaignVoiceBotDetailedAnalytics)

                    call_details_obj.call_start_time = datetime.strptime(
                        response['StartTime'], "%Y-%m-%d %H:%M:%S")
                    call_details_obj.price = response['Price']
                    call_details_obj.direction = response['Direction']
                    call_details_obj.status = response['Status']
                    call_details_obj.is_details_fetched = True

                    call_details_obj.save() 

        campaign_objs = Campaign.objects.filter(status__in=["completed", "partially_completed", "failed"])
        voice_campaign_objs = CampaignVoiceBotSetting.objects.filter(campaign__in=campaign_objs, is_details_fetched=False)

        for voice_campaign_obj in voice_campaign_objs:
            voice_campaign_users = CampaignVoiceUser.objects.filter(voice_campaign=voice_campaign_obj)

            for voice_campaign_user in voice_campaign_users:
                call_sid = voice_campaign_user.call_sid

                if call_sid != '':
                    api_obj = check_and_create_voice_bot_api_obj(voice_campaign_obj.campaign, CampaignVoiceBotAPI)
                    api_code = api_obj.api_code

                    processor_check_dictionary = {'open': open_file}

                    param = {
                        "call_sid": call_sid,
                        "bot_id": str(voice_campaign_obj.campaign.bot.pk)
                    }

                    exec(str(api_code), processor_check_dictionary)
                    response_body = processor_check_dictionary['get_call_details'](json.dumps(param))
                    response = response_body['Call']

                    logger.info('call details: %s', str(response), extra={'AppName': 'Campaign'})

                    if response:
                        if response["Status"] == "completed":
                            voice_campaign_user.status = "completed"
                        elif response["Status"] == "no-answer":
                            voice_campaign_user.status = "rejected"
                        else:
                            voice_campaign_user.status = "failed"

                        voice_campaign_user.price = response["Price"]
                        voice_campaign_user.save()
       
            voice_campaign_obj.is_details_fetched = True
            voice_campaign_obj.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
    complete_cronjob_execution(cronjob_tracker_obj)
