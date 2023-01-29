from EasyChatApp.models import AnalyticsMonitoring, Bot, \
    AnalyticsMonitoringLogs
from EasyChatApp.utils_bot_usage_analytics \
    import get_last_hour_message_count, generate_mail
import json
import sys
from EasyChatApp.utils import logger
from datetime import datetime, timedelta
from cronjob_scripts.EasyChatAppCronjobUtilityFunctions.utils_cronjob import *

from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses

"""
compare_two_time_fields
paramters - time 1 and time 2
return 
1 if time_one is greater than time_two
0  if both time are equal 
-1 if time_two is  greater 
"""


def compare_two_time_fields(time_one, time_two):
    try:
        time_one_hour = time_one.hour
        time_two_hour = time_two.hour

        if time_one_hour > time_two_hour:
            return 1

        elif time_two_hour > time_one_hour:
            return -1

        else:
            time_one_mins = time_one.minute
            time_two_mins = time_two.minute

            if time_one_mins > time_two_mins:
                return 1

            elif time_two_mins > time_one_mins:
                return -1

            else:
                return 0

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def cronjob():
    cronjob_id = "easychat_check_bot_usage_cron"
    cronjob_is_running, cronjob_objs = check_if_cronjob_is_running(cronjob_id)
    if cronjob_is_running:
        return
    try:
        bot_objs = Bot.objects.filter(is_analytics_monitoring_enabled=True, is_deleted=False)
        moniter_objs = AnalyticsMonitoring.objects.filter(bot__in=bot_objs)
        for moniter_obj in moniter_objs:
            try:
                bot_obj = moniter_obj.bot
                consecutive_hours = moniter_obj.consecutive_hours
                active_hours_start = moniter_obj.active_hours_start
                active_hours_end = moniter_obj.active_hours_end
                message_limit = moniter_obj.message_limit
                email_addr_list = moniter_obj.email_addr_list

                current_hour = datetime.now().hour

                check_analytics = False

                if compare_two_time_fields(active_hours_end, active_hours_start) == 1:

                    if active_hours_start.hour < current_hour and active_hours_end.hour > current_hour:
                        check_analytics = True

                elif compare_two_time_fields(active_hours_end, active_hours_start) == 0:
                    check_analytics = True

                elif active_hours_start.hour > current_hour or active_hours_end.hour < current_hour:
                    check_analytics = True

                if check_analytics:
                    msg_count = get_last_hour_message_count(bot_obj)
                    if msg_count > message_limit:
                        AnalyticsMonitoringLogs.objects.filter(
                            monitoring_obj=moniter_obj).delete()
                    else:
                        # time_threshold = datetime.now() - timedelta(hours=2)
                        # analytics_monitoring_obj = AnalyticsMonitoringLogs.objects.filter(monitoring_obj=moniter_obj, last_modified__lte=time_threshold)  # noqa: E501
                        log_objs = AnalyticsMonitoringLogs.objects.filter(monitoring_obj=moniter_obj)  # noqa: E501
                        if log_objs.count() > 0:
                            log_obj = log_objs[0]
                        else:
                            log_obj = AnalyticsMonitoringLogs.objects.create(
                                monitoring_obj=moniter_obj)

                        current_consecutive_count = \
                            log_obj.count_of_consecutive_anamoly + 1
                        log_obj.count_of_consecutive_anamoly =\
                            current_consecutive_count
                        logs = json.loads(log_obj.logs)['items']
                        temp_dict = {'datetime': datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"), 'msg_count': msg_count}
                        logs.append(temp_dict)
                        log_obj.logs = json.dumps({'items': logs})
                        log_obj.save()

                        if current_consecutive_count >= consecutive_hours:
                            email_subject = "Decreased Usage in " \
                                + bot_obj.name + " Bot"
                            email_receivers = json.loads(
                                email_addr_list)['items']
                            email_content = """Dear Admin,<br>
                            We have noticed a decrease in usage of the """
                            email_content += bot_obj.name + """ Bot on """
                            email_content += datetime.now().strftime('%Y-%m-%d')

                            email_content += """.
                            <br>Please get in touch with AllinCall Customer\
                            Success team so we can find out the the reason\
                            for the drop and resolve the issues, if any.<br>"""

                            config_obj = get_developer_console_settings()
                            email_content += config_obj.custom_report_template_signature

                            for email in email_receivers:
                                try:
                                    send_email_to_customer_via_awsses(
                                        email, email_subject, email_content)
                                except Exception:
                                    continue
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    
    complete_cronjob_execution(cronjob_objs)
