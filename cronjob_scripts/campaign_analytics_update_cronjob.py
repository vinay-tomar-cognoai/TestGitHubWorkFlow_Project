import sys
from CampaignApp.constants import CAMPAIGN_ANALYTICS_SCHEDULAR_EXPIRY_TIME, CAMPAIGN_ANALYTICS_SCHEDULAR_ID_CONSTANT
from CampaignApp.utils import update_campaigns_analytics
import logging
logger = logging.getLogger(__name__)
from cronjob_scripts.utils_campaign_cronjob_validator import create_campaign_cronjob_tracker_obj, delete_campaign_cronjob_tracker_obj, get_campaign_cronjob_tracker_obj


def cronjob():
    try:
        cronjob_detector_id = CAMPAIGN_ANALYTICS_SCHEDULAR_ID_CONSTANT
        expiration_time = CAMPAIGN_ANALYTICS_SCHEDULAR_EXPIRY_TIME

        campaign_cronjob_tracker_obj = get_campaign_cronjob_tracker_obj(
            cronjob_detector_id)
        if campaign_cronjob_tracker_obj:
            if campaign_cronjob_tracker_obj.is_object_expired(expiration_time):
                delete_campaign_cronjob_tracker_obj(cronjob_detector_id)
                create_campaign_cronjob_tracker_obj(cronjob_detector_id)
            else:
                logger.info("Campaign App update analytics service is already running!",
                            extra={'AppName': 'CampaignApp'})
                return
        else:
            create_campaign_cronjob_tracker_obj(cronjob_detector_id)
            update_campaigns_analytics()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_campaigns_analytics cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
    
    delete_campaign_cronjob_tracker_obj(cronjob_detector_id)
