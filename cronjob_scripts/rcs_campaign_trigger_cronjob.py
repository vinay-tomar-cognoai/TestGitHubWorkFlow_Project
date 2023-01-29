import os
import sys
import json
import threading

from CampaignApp.models import *
from EasyChatApp.utils import logger
from datetime import datetime, timedelta
from django.conf import settings
from CampaignApp.utils import execute_send_rcs_campaign, create_remaining_schedule_objects
from cronjob_scripts.utils_campaign_cronjob_validator import check_if_cronjob_is_running, complete_cronjob_execution

from os import path
from os.path import basename


def cronjob():

    cronjob_detector_id = "rcs_campaign_trigger_cronjob"
    is_cronjob_exists, cronjob_tracker_obj = check_if_cronjob_is_running(cronjob_detector_id)
    if is_cronjob_exists:
        return

    try:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M %p")
        all_campaign_schedules = CampaignSchedule.objects.all()
        for obj in all_campaign_schedules:
            upto_date = obj.updated_upto
            start_date = now.date()
            if upto_date != None:
                delta = upto_date - start_date
                delta = delta.days
                if delta < 5:
                    create_remaining_schedule_objects(obj, None, CampaignScheduleObject)

        channel_objs = CampaignChannel.objects.filter(name="RCS")
        if channel_objs.exists():
            channel_obj = channel_objs.first()
            campaign_schedule_objects = CampaignScheduleObject.objects.filter(date=current_date, time=current_time, channel=channel_obj)
            if campaign_schedule_objects.count() > 0:
                for obj in campaign_schedule_objects:
                    campaign_obj = obj.campaign_schedule.campaign
                    execute_send_rcs_campaign(campaign_obj.pk, obj, Campaign, CampaignFileAccessManagement, CampaignAudience, CampaignAudienceLog, CampaignAnalytics, CampaignTemplateVariable)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_campaign_message_rcs cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    complete_cronjob_execution(cronjob_tracker_obj)
