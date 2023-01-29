from EasyChatApp.models import EasyChatCronjobTracker
from EasyChatApp.utils import logger
import sys


def check_if_cronjob_is_running(cronjob_id):
    cronjob_objs = None
    try:
        cronjob_objs = EasyChatCronjobTracker.objects.filter(
            function_id=cronjob_id)
        if cronjob_objs.exists():
            return True, cronjob_objs
        else:
            cronjob_objs = EasyChatCronjobTracker.objects.create(
                function_id=cronjob_id)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In check_if_cronjob_id_exists: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat'})
    return False, cronjob_objs


def complete_cronjob_execution(cronjob_objs):
    try:
        if cronjob_objs:
            cronjob_objs.delete()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In check_if_cronjob_id_exists: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat'})
