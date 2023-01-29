import sys
import pytz
import datetime
from django.conf import settings
from CognoMeetApp.models import CognoMeetFileAccessManagement, CognoMeetIO, CognoMeetCronjobTracker, CognoMeetAuditTrail, CognoMeetRecording
from CognoMeetApp.utils_cronjob_tracker import *
from CognoMeetApp.utils_dyte_apis import *
from cronjob_scripts.cognoai_cronjob_utils import create_cronjob_start_log, create_cronjob_end_log, send_cron_error_report


def cronjob():
    cognomeet_cronjob_tracker_obj = get_cognomeet_cronjob_tracker_obj(COGNOMEET_FETCH_RECORDINGS, CognoMeetCronjobTracker)
    if cognomeet_cronjob_tracker_obj:
        logger.info("cognomeet_fetch_meeting_recordings is already running!",
                    extra={'AppName': 'CognoMeet'})
        return
    else:
        create_cognomeet_cronjob_tracker_obj(COGNOMEET_FETCH_RECORDINGS, CognoMeetCronjobTracker)

    curr_file_name = "cognomeet_fetch_meeting_recordings"
    cron_error_list = []
    try:
        log_obj_id = create_cronjob_start_log(curr_file_name)

        cognomeet_io_objs = CognoMeetIO.objects.filter(is_meeting_expired=True, is_meeting_recording_fetched=False)
        for cognomeet_io_obj in cognomeet_io_objs:

            audit_trail_obj = CognoMeetAuditTrail.objects.filter(cogno_meet_io=cognomeet_io_obj).first()

            '''
            If there is no audit trail object then it means that the session has 
            not started and hence we do not fetch recordings for that session.
            '''
            if not audit_trail_obj:
                cognomeet_io_obj.is_meeting_recording_fetched = True
                cognomeet_io_obj.save()
                continue

            get_meeting_recording_url(cognomeet_io_obj, audit_trail_obj, CognoMeetRecording, CognoMeetFileAccessManagement)
            
        delete_cognomeet_cronjob_tracker_obj(COGNOMEET_FETCH_RECORDINGS, CognoMeetCronjobTracker)
    except Exception as e:
        delete_cognomeet_cronjob_tracker_obj(COGNOMEET_FETCH_RECORDINGS, CognoMeetCronjobTracker)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("CognoMeet fetch meeting recording cronjob: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
        cron_error_list.append([str(e), str(exc_tb.tb_lineno)])

    send_cron_error_report(cron_error_list, "cronjob", curr_file_name)

    create_cronjob_end_log(log_obj_id)
