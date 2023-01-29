from EasyAssistApp.constants import CRONJOB_TRACKER_EXPIRY_TIME, HOURLY_CRONJOB_TRACKER_EXPIRY_TIME
from django.utils import timezone
from EasyAssistApp.utils import logger
import sys


def get_easyassist_cronjob_tracker_obj(cronjob_id, EasyAssistCronjobTracker):
    try:
        easyassist_cronjob_tracker_obj = EasyAssistCronjobTracker.objects.filter(cronjob_id=cronjob_id).first()

        return easyassist_cronjob_tracker_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in get_easyassist_cronjob_tracker_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
    return None


def create_easyassist_cronjob_tracker_obj(cronjob_id, EasyAssistCronjobTracker):
    try:
        EasyAssistCronjobTracker.objects.create(cronjob_id=cronjob_id)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in create_easyassist_cronjob_tracker_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def delete_easyassist_cronjob_tracker_obj(cronjob_id, EasyAssistCronjobTracker):
    try:
        easyassist_cronjob_tracker_obj = EasyAssistCronjobTracker.objects.filter(cronjob_id=cronjob_id).first()
        if easyassist_cronjob_tracker_obj:
            easyassist_cronjob_tracker_obj.delete()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in delete_easyassist_cronjob_tracker_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def is_cronjob_tracker_object_expired(cronjob_tacker_object, is_hourly_cronjob=False):
    datetime_difference = int((timezone.now() - cronjob_tacker_object.creation_datetime).total_seconds())
    if datetime_difference >= CRONJOB_TRACKER_EXPIRY_TIME:
        return True
    if is_hourly_cronjob and datetime_difference >= HOURLY_CRONJOB_TRACKER_EXPIRY_TIME:
        return True
    else:
        return False
            

def delete_and_create_cron_tracker_obj(CRONJOB_CONSTANT, EasyAssistCronjobTracker):
    delete_easyassist_cronjob_tracker_obj(CRONJOB_CONSTANT, EasyAssistCronjobTracker)
    create_easyassist_cronjob_tracker_obj(CRONJOB_CONSTANT, EasyAssistCronjobTracker)
