import sys
import datetime
from EasyChatApp.utils import logger
from EasyChatApp.models import MISDashboard, UserSessionHealth
from EasyChatApp.utils_analytics import return_mis_objects_excluding_blocked_sessions
from EasyChatApp.utils_validation import EasyChatInputValidation
from cronjob_scripts.EasyChatAppCronjobUtilityFunctions.utils_cronjob import *


def cronjob():
    cronjob_id = "easychat_mis_dashboard_today_cron"
    cronjob_is_running, cronjob_objs = check_if_cronjob_is_running(cronjob_id)
    if cronjob_is_running:
        return
    try:
        total_unanswered_messages = MISDashboard.objects.filter(
            creation_date=datetime.datetime.now().date(), intent_name=None, is_unidentified_query=False)

        total_unanswered_messages = return_mis_objects_excluding_blocked_sessions(total_unanswered_messages, UserSessionHealth)

        validation_obj = EasyChatInputValidation()

        for mis_obj in total_unanswered_messages.iterator():
            if validation_obj.is_valid_query(mis_obj.get_message_received()):
                mis_obj.is_unidentified_query = True
                mis_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob mis dashboard today ! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    complete_cronjob_execution(cronjob_objs)
