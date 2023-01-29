from cronjob_scripts.cognoai_cronjob_utils import create_cronjob_start_log, create_cronjob_end_log, send_cron_error_report

from EasyAssistApp.models import *
from EasyAssistApp.utils import logger

from EasyAssistApp.utils_cronjob import get_easyassist_cronjob_tracker_obj, \
    create_easyassist_cronjob_tracker_obj, \
    delete_easyassist_cronjob_tracker_obj, \
    is_cronjob_tracker_object_expired, \
    delete_and_create_cron_tracker_obj

from datetime import datetime

import sys


def cronjob():

    easyassist_cronjob_tracker_obj = get_easyassist_cronjob_tracker_obj(TRANSFER_LOG_EXPIRY_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
    if easyassist_cronjob_tracker_obj:
        if is_cronjob_tracker_object_expired(easyassist_cronjob_tracker_obj):
            delete_and_create_cron_tracker_obj(
                TRANSFER_LOG_EXPIRY_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
        else:
            logger.info("easyassist_expire_transfer_log is already running!",
                        extra={'AppName': 'EasyAssist'})
            return
    else:
        create_easyassist_cronjob_tracker_obj(TRANSFER_LOG_EXPIRY_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
    
    curr_file_name = "easyassist_expire_transfer_log"
    log_obj_id = create_cronjob_start_log(curr_file_name)

    cron_error_list = []

    try:
        transferred_io_objs = CobrowseIOTransferredAgentsLogs.objects.filter(
            cobrowse_request_type="transferred", transferred_status="")
        invited_io_objs = CobrowseIOTransferredAgentsLogs.objects.filter(
            cobrowse_request_type="invited", invited_status="")
        for transferred_io in transferred_io_objs.iterator():
            transferred_io.transferred_status = "expired"
            transferred_io.save()
        for invited_io_obj in invited_io_objs.iterator():
            invited_io_obj.invited_status = "expired"
            invited_io_obj.save()
        
        delete_easyassist_cronjob_tracker_obj(TRANSFER_LOG_EXPIRY_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
    except Exception as e:
        delete_easyassist_cronjob_tracker_obj(TRANSFER_LOG_EXPIRY_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(e), str(exc_tb.tb_lineno)])

    send_cron_error_report(cron_error_list, "cronjob", curr_file_name)

    create_cronjob_end_log(log_obj_id)
