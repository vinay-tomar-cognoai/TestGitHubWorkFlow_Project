import sys
import pytz
import datetime
from django.conf import settings
from CognoMeetApp.models import CognoMeetIO, CognoMeetCronjobTracker, CognoMeetAuditTrail, MeetingActualStartEndTime
from CognoMeetApp.utils_cronjob_tracker import *
from CognoMeetApp.utils import archive_cognomeet_session
from cronjob_scripts.cognoai_cronjob_utils import create_cronjob_start_log, create_cronjob_end_log, send_cron_error_report


def cronjob():
    cognomeet_cronjob_tracker_obj = get_cognomeet_cronjob_tracker_obj(COGNOMEET_ARCHIVE_MEETINGS, CognoMeetCronjobTracker)
    if cognomeet_cronjob_tracker_obj:
        logger.info("cognomeet_archive_meeting_sessions is already running!",
                    extra={'AppName': 'CognoMeet'})
        return
    else:
        create_cognomeet_cronjob_tracker_obj(COGNOMEET_ARCHIVE_MEETINGS, CognoMeetCronjobTracker)

    curr_file_name = "cognomeet_archive_meeting_sessions"
    cron_error_list = []
    try:
        log_obj_id = create_cronjob_start_log(curr_file_name)

        time_zone = pytz.timezone(settings.TIME_ZONE)
        current_time = datetime.datetime.now().astimezone(time_zone).time()
        current_date = datetime.datetime.now().astimezone(time_zone).date()
        # TODO optimize
        cognomeet_io_objs = []
        cognomeet_io_objs += CognoMeetIO.objects.filter(is_meeting_expired=False, meeting_start_date__lte=current_date)
        cognomeet_io_objs += CognoMeetIO.objects.filter(is_meeting_expired=False, meeting_end_time__lt=current_time)
        cognomeet_io_objs = list(set(cognomeet_io_objs))
        for cognomeet_io_obj in cognomeet_io_objs:
            archive_session = False
            
            if not cognomeet_io_obj.agent_update_datetime and not cognomeet_io_obj.customer_update_datetime:
                archive_session = True

            if not archive_session:
                # check for timers exhausted
                if cognomeet_io_obj.is_agent_inactivity_threshold_exceeded() and cognomeet_io_obj.is_customer_inactivity_threshold_exceeded():
                    archive_session = True

            if archive_session:
                archive_cognomeet_session(cognomeet_io_obj, CognoMeetAuditTrail, MeetingActualStartEndTime)

        delete_cognomeet_cronjob_tracker_obj(COGNOMEET_ARCHIVE_MEETINGS, CognoMeetCronjobTracker)
    except Exception as e:
        delete_cognomeet_cronjob_tracker_obj(COGNOMEET_ARCHIVE_MEETINGS, CognoMeetCronjobTracker)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("cognomeet_archive_meeting_sessions cronjob: %s at %s",
                        str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
        cron_error_list.append([str(e), str(exc_tb.tb_lineno)])

    send_cron_error_report(cron_error_list, "cronjob", curr_file_name)

    create_cronjob_end_log(log_obj_id)
