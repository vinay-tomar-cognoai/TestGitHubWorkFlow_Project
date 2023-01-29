from functools import reduce
import logging
import operator
from django.db.models import Q
import sys
from CampaignApp.constants import CAMPAIGN_SCHEDULED
from CampaignApp.models import Campaign, CampaignAPI, CampaignAnalytics, CampaignAudience, CampaignAudienceLog, CampaignChannel, CampaignFileAccessManagement, CampaignSchedule, CampaignScheduleObject, CampaignTemplateVariable
from datetime import datetime
from CampaignApp.utils import create_cloned_campaign, execute_send_campaign, create_remaining_schedule_objects, validate_aws_sqs_credentials
from cronjob_scripts.utils_campaign_cronjob_validator import check_if_cronjob_is_running, complete_cronjob_execution

logger = logging.getLogger(__name__)


def create_new_campaign(campaign_obj, campaign_creation_date, campaign_batch_obj):
    try:
        campaign_creation_date = campaign_creation_date.strftime(
            "%d_%h_%y %I_%M %p")
        campaign_name = campaign_obj.name + ' ' + \
            campaign_creation_date + ' (S)'
        campaign_obj = create_cloned_campaign(
            campaign_obj, campaign_name, campaign_batch_obj)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_new_campaign cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return campaign_obj


def cronjob():

    cronjob_detector_id = "Whatsapp_campaign_trigger_cronjob"
    is_cronjob_exists, cronjob_tracker_obj = check_if_cronjob_is_running(
        cronjob_detector_id)
    if is_cronjob_exists:
        return

    try:
        current_date_time = datetime.now()
        campaign_objs = Campaign.objects.filter(
            status=CAMPAIGN_SCHEDULED, is_deleted=False)
        campaign_objs = list(campaign_objs)
        campaign_query = None
        if campaign_objs:
            campaign_query = reduce(operator.or_, (Q(campaign=campaign_obj)
                                                   for campaign_obj in campaign_objs))
            all_campaign_schedules = CampaignSchedule.objects.filter(
                campaign_query)
        else:
            all_campaign_schedules = CampaignSchedule.objects.none()
        for obj in all_campaign_schedules.iterator():
            upto_date = obj.updated_upto
            start_date = current_date_time.date()
            if upto_date != None:
                delta = upto_date - start_date
                delta = delta.days
                if delta < 5:
                    create_remaining_schedule_objects(
                        obj, None, CampaignScheduleObject)

        channel_obj = CampaignChannel.objects.filter(
            name="Whatsapp Business").first()
        if channel_obj:
            current_date = current_date_time.strftime("%Y-%m-%d")
            current_time = current_date_time.strftime("%H:%M %p")
            campaign_schedule_objects = CampaignScheduleObject.objects.filter(
                date=current_date, time=current_time, channel=channel_obj, is_sent=False)
            if campaign_query:
                campaign_schedule_objects = campaign_schedule_objects.filter(
                    campaign_query)
            else:
                campaign_schedule_objects = CampaignScheduleObject.objects.none()
            for campaign_schedule_object in campaign_schedule_objects.iterator():
                campaign_obj = campaign_schedule_object.campaign
                campaign_api = CampaignAPI.objects.filter(
                    campaign=campaign_obj).first()
                if campaign_api:
                    bot_wsp_obj = campaign_api.campaign_bot_wsp_config
                    campaign_wsp_config_meta = {"code": bot_wsp_obj.code, "namespace": bot_wsp_obj.namespace,
                                                "enable_queuing_system": bot_wsp_obj.enable_queuing_system, "bot_wsp_id": bot_wsp_obj.pk}
                    if campaign_wsp_config_meta["enable_queuing_system"]:
                        sqs_response = validate_aws_sqs_credentials(
                            bot_wsp_obj, campaign_wsp_config_meta)
                        if not sqs_response:
                            continue
                    campaign_obj = create_new_campaign(
                        campaign_obj, current_date_time, campaign_schedule_object.campaign_batch)
                    execute_send_campaign(campaign_wsp_config_meta, campaign_obj.pk, Campaign, CampaignFileAccessManagement, CampaignAudience, CampaignAudienceLog, CampaignAnalytics, CampaignTemplateVariable)
                    campaign_schedule_object.is_sent = True
                    campaign_schedule_object.save(update_fields=["is_sent"])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_campaign_message_whatsapp cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    complete_cronjob_execution(cronjob_tracker_obj)
