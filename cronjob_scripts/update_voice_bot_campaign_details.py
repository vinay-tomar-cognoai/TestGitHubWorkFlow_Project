from CampaignApp.constants import CAMPAIGN_COMPLETED, CAMPAIGN_IN_PROGRESS, CAMPAIGN_PARTIALLY_COMPLETED
from CampaignApp.models import Campaign, CampaignVoiceBotAPI, CampaignVoiceBotAnalytics, CampaignVoiceBotSetting
from CampaignApp.utils import check_and_create_voice_bot_api_obj, open_file, update_voice_campaign_user_call_status
from cronjob_scripts.utils_campaign_cronjob_validator import check_if_cronjob_is_running, complete_cronjob_execution

import logging
logger = logging.getLogger(__name__)

import sys
import time
import json


def cronjob():
    cronjob_detector_id = "update_voice_bot_campaign_details"
    is_cronjob_exists, cronjob_tracker_obj = check_if_cronjob_is_running(cronjob_detector_id)
    if is_cronjob_exists:
        return
    try:
        campaign_objs = Campaign.objects.filter(
            channel__name='Voice Bot', status=CAMPAIGN_IN_PROGRESS)

        for campaign_obj in campaign_objs:
            voice_bot_obj = CampaignVoiceBotSetting.objects.filter(
                campaign=campaign_obj)

            if voice_bot_obj:
                voice_bot_obj = voice_bot_obj.first()
                campaign_sid = voice_bot_obj.campaign_sid

                if campaign_sid != '':
                    api_obj = check_and_create_voice_bot_api_obj(
                        campaign_obj, CampaignVoiceBotAPI)
                    api_code = api_obj.api_code

                    processor_check_dictionary = {'open': open_file}

                    param = {
                        "campaign_sid": campaign_sid,
                        "bot_id": str(campaign_obj.bot.pk)
                    }

                    exec(str(api_code), processor_check_dictionary)
                    response_body = processor_check_dictionary['get_campaign_details'](json.dumps(param))

                    response = response_body['response']

                    logger.info('campaign details: %s', str(
                        response), extra={'AppName': 'Campaign'})

                    if response and len(response) > 0:
                        stats = response[0]['data']['stats']
                        summary = response[0]['summary']
                        status = response[0]['data']['status']

                        analytics_obj = check_and_create_voice_bot_analytics_obj(
                            campaign_obj)

                        analytics_obj.call_scheduled = summary['call_scheduled']
                        analytics_obj.call_initiated = summary['call_initialized']
                        analytics_obj.call_completed = summary['call_completed']
                        analytics_obj.call_failed = summary['call_failed']
                        analytics_obj.call_in_progress = summary['call_inprogress']
                        analytics_obj.call_invalid = stats['invalid']
                        analytics_obj.call_failed_dnd = stats['failed-dnd']
                        analytics_obj.call_retry = stats['retry']
                        analytics_obj.call_retrying = stats['retrying']
                        analytics_obj.call_created = stats['created']

                        analytics_obj.save()

                        if status == 'Failed':
                            campaign_obj.status = CAMPAIGN_PARTIALLY_COMPLETED
                            update_voice_campaign_user_call_status(voice_bot_obj)
                        elif status == 'Completed':
                            campaign_obj.status = CAMPAIGN_COMPLETED
                            update_voice_campaign_user_call_status(voice_bot_obj)

                        campaign_obj.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    complete_cronjob_execution(cronjob_tracker_obj)


def check_and_create_voice_bot_analytics_obj(campaign_obj):
    try:
        analytics_obj = CampaignVoiceBotAnalytics.objects.filter(
            campaign=campaign_obj)

        if analytics_obj:
            return analytics_obj.first()

        analytics_obj = CampaignVoiceBotAnalytics.objects.create(
            campaign=campaign_obj)

        return analytics_obj
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_create_voice_bot_analytics_obj: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})    
