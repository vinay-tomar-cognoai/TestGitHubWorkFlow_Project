import os
import sys
from EasyAssistApp.models import *
from EasyAssistApp.utils import mask_cobrowseio_customer_details, mask_cogno_meet_customer_details
from EasyAssistApp.utils_cronjob import get_easyassist_cronjob_tracker_obj, create_easyassist_cronjob_tracker_obj, \
    delete_easyassist_cronjob_tracker_obj, is_cronjob_tracker_object_expired, delete_and_create_cron_tracker_obj
from cronjob_scripts.cognoai_cronjob_utils import create_cronjob_start_log, create_cronjob_end_log, send_cron_error_report
from datetime import datetime


def cronjob():

    easyassist_cronjob_tracker_obj = get_easyassist_cronjob_tracker_obj(MASK_CUSTOMER_DETAILS_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
    
    if easyassist_cronjob_tracker_obj:
        if is_cronjob_tracker_object_expired(easyassist_cronjob_tracker_obj, True):
            delete_and_create_cron_tracker_obj(
                MASK_CUSTOMER_DETAILS_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
        else:
            logger.info("easyassist_mask_customer_details_cronjob is already running!",
                        extra={'AppName': 'EasyAssist'})
            return
    else:
        create_easyassist_cronjob_tracker_obj(MASK_CUSTOMER_DETAILS_CRONJOB_CONSTANT, EasyAssistCronjobTracker)

    curr_file_name = "easyassist_mask_customer_details_cronjob"
    cron_error_list = []
    try:
        log_obj_id = create_cronjob_start_log(curr_file_name)

        mask_cobrowseio_customer_details(CobrowseDropLink, CobrowseChatHistory)
        mask_cogno_meet_customer_details(CobrowseVideoAuditTrail)
        delete_easyassist_cronjob_tracker_obj(MASK_CUSTOMER_DETAILS_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
    except Exception as e:
        delete_easyassist_cronjob_tracker_obj(MASK_CUSTOMER_DETAILS_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(e), str(exc_tb.tb_lineno)])

    send_cron_error_report(cron_error_list, "cronjob", curr_file_name)

    create_cronjob_end_log(log_obj_id)
