from EasyChatApp.utils import logger
from CampaignApp.models import CampaignCronjobTracker
import sys


def check_if_cronjob_is_running(cronjob_id):
    cronjob_objs = None
    try:
        cronjob_objs = CampaignCronjobTracker.objects.filter(function_id=cronjob_id).first()
        if cronjob_objs:
            return True, cronjob_objs
        else:
            cronjob_objs = CampaignCronjobTracker.objects.create(function_id=cronjob_id)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In check_if_cronjob_is_running check_if_cronjob_id_exists: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'CampaignApp'})
    return False, cronjob_objs


def complete_cronjob_execution(cronjob_objs):
    try:
        if cronjob_objs:
            cronjob_objs.delete()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In complete_cronjob_execution cronjob check_if_cronjob_id_exists: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'CampaignApp'})


def get_campaign_cronjob_tracker_obj(cronjob_id):
    try:
        campaign_cronjob_tracker_obj = CampaignCronjobTracker.objects.filter(function_id=cronjob_id).first()

        return campaign_cronjob_tracker_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in get_campaign_cronjob_tracker_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CampaignApp'})
    return None


def delete_campaign_cronjob_tracker_obj(cronjob_id):
    try:
        campaign_cronjob_tracker_obj = CampaignCronjobTracker.objects.filter(function_id=cronjob_id).first()
        if campaign_cronjob_tracker_obj:
            campaign_cronjob_tracker_obj.delete()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in delete_campaign_cronjob_tracker_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CampaignApp'})


def create_campaign_cronjob_tracker_obj(cronjob_id):
    try:
        CampaignCronjobTracker.objects.create(function_id=cronjob_id)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in create_campaign_cronjob_tracker_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CampaignApp'})
