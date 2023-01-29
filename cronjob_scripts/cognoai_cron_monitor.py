from cronjob_scripts.cognoai_cronjob_utils import send_cron_not_running_email
from cronjob_scripts.cron_log_manager import CronLogManager
from django.conf import settings
from croniter import croniter
import datetime
import os
import re
import pytz

cron_log_manager_obj = CronLogManager()


cron_file_time_map = dict()
log_file_time_map = dict()
email_sent_time_map = dict()
cronjobs = settings.CRONJOBS


# Update cron_file_time_map
for cronjob in cronjobs:
    cron_str = cronjob[0]
    file_name = cronjob[1].split('.')[1]
    cron_file_time_map[file_name] = cron_str


log_file_time_map = cron_log_manager_obj.get_file_run_time_map()

# Monitor all cronjob files
for file_name, cron_pattern in cron_file_time_map.items():
    if "easyassist" not in file_name:
        continue

    base = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
    cron = croniter(cron_pattern, base)

    prev_time = cron.get_prev(datetime.datetime)
    prev_time = prev_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(settings.TIME_ZONE))
    prev_time = prev_time.replace(tzinfo=None)

    next_time = cron.get_next(datetime.datetime)
    next_time = next_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(settings.TIME_ZONE))
    next_time = next_time.replace(tzinfo=None)

    cron_time_diff = (next_time - prev_time).total_seconds()
    time_offset = int(0.01 * cron_time_diff)
    cron_time_diff = cron_time_diff // 60

    if prev_time.date() < datetime.datetime.now().date():
        continue

    cron_run_time = None
    send_cron_fail_report = False
    if file_name not in log_file_time_map:
        prev_time_offset = prev_time + datetime.timedelta(seconds=time_offset)
        # If the file is just started running
        # giving 1% of total cron time difference to the file to get executed before sending email
        if prev_time_offset < datetime.datetime.now():
            send_cron_fail_report = True

    else:
        cron_run_time = log_file_time_map[file_name]
        file_run_time_time_diff = (datetime.datetime.now() - cron_run_time).total_seconds()
        file_run_time_time_diff = file_run_time_time_diff // 60

        if file_run_time_time_diff > 2 * cron_time_diff:
            send_cron_fail_report = True

    if send_cron_fail_report == True:
        send_cron_not_running_email(file_name, cron_run_time)
