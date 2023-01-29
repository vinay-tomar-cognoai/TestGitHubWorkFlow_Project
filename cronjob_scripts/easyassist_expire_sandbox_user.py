from cronjob_scripts.cognoai_cronjob_utils import create_cronjob_start_log, create_cronjob_end_log, send_cron_error_report

from EasyAssistApp.models import *
from EasyAssistApp.utils import logger
from datetime import datetime

import sys


def cronjob():
    curr_file_name = "easyassist_expire_sandbox_user"
    log_obj_id = create_cronjob_start_log(curr_file_name)

    cron_error_list = []
    try:
        todays_date = datetime.now().date()

        sandbox_user_objs = CobrowseSandboxUser.objects.filter(is_expired=False)
        for sandbox_user_obj in sandbox_user_objs:
            expire_date = sandbox_user_obj.expire_date

            if expire_date < todays_date:
                sandbox_user_obj.is_expired = True
                sandbox_user_obj.save()

                cobrowse_agent = CobrowseAgent.objects.filter(user=sandbox_user_obj.user)
                access_token_obj = cobrowse_agent.get_access_token_obj()

                access_token_obj.is_active = False
                access_token_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(e), str(exc_tb.tb_lineno)])

    send_cron_error_report(cron_error_list, "cronjob", curr_file_name)

    create_cronjob_end_log(log_obj_id)
