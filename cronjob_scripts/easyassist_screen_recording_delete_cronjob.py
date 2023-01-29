import os
import sys
from EasyAssistApp.models import *
from cronjob_scripts.cognoai_cronjob_utils import send_cron_error_report
from EasyAssistApp.utils_cronjob import get_easyassist_cronjob_tracker_obj, \
    create_easyassist_cronjob_tracker_obj, \
    delete_easyassist_cronjob_tracker_obj, \
    is_cronjob_tracker_object_expired, \
    delete_and_create_cron_tracker_obj


def cronjob():

    easyassist_cronjob_tracker_obj = get_easyassist_cronjob_tracker_obj(SCREEN_RECORDING_DELETE_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
    if easyassist_cronjob_tracker_obj:
        if is_cronjob_tracker_object_expired(easyassist_cronjob_tracker_obj):
            delete_and_create_cron_tracker_obj(
                SCREEN_RECORDING_DELETE_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
        else:
            logger.info("easyassist_screen_recording_delete_cronjob is already running!",
                        extra={'AppName': 'EasyAssist'})
            return

    curr_file_name = "easyassist_screen_recording_delete_cronjob"
    cron_error_list = []
    try:
        screen_recording_objs = CobrowseScreenRecordingAuditTrail.objects.filter(is_expired=False)
        for screen_recording_obj in screen_recording_objs.iterator():
            if screen_recording_obj.get_recording_expiration_time() == "Today":
                screen_recording_obj.is_expired = True
                screen_recording_obj.save()
    
        delete_easyassist_cronjob_tracker_obj(SCREEN_RECORDING_DELETE_CRONJOB_CONSTANT, EasyAssistCronjobTracker)

    except Exception as e:
        delete_easyassist_cronjob_tracker_obj(SCREEN_RECORDING_DELETE_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
        logger.error("In easyassist_screen_recording_delete_cronjob: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})

    send_cron_error_report(cron_error_list, "cronjob", curr_file_name)
