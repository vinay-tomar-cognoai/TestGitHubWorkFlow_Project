import sys
import logging
from CognoMeetApp.constants import *

logger = logging.getLogger(__name__)


def get_cognomeet_cronjob_tracker_obj(cronjob_id, CognoMeetCronjobTracker):
    try:
        cognomeet_cronjob_tracker_obj = CognoMeetCronjobTracker.objects.filter(
            cronjob_id=cronjob_id).first()

        return cognomeet_cronjob_tracker_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in get_cognomeet_cronjob_tracker_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
    return None


def create_cognomeet_cronjob_tracker_obj(cronjob_id, CognoMeetCronjobTracker):
    try:
        CognoMeetCronjobTracker.objects.create(cronjob_id=cronjob_id)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in create_cognomeet_cronjob_tracker_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})


def delete_cognomeet_cronjob_tracker_obj(cronjob_id, CognoMeetCronjobTracker):
    try:
        cognomeet_cronjob_tracker_obj = CognoMeetCronjobTracker.objects.filter(
            cronjob_id=cronjob_id).first()
        if cognomeet_cronjob_tracker_obj:
            cognomeet_cronjob_tracker_obj.delete()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in delete_cognomeet_cronjob_tracker_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
