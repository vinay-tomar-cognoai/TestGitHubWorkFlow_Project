import json
import sys
from datetime import datetime
from CognoMeetApp.models import CognoMeetIO, CognoMeetCronjobTracker, \
    CognoMeetAuditTrail, CognoMeetExportDataRequest, CognoMeetFileAccessManagement, \
    CognoMeetAccessToken, CognoMeetAgent
from CognoMeetApp.utils_cronjob_tracker import *
from CognoMeetApp.utils import get_custom_meeting_analytics, get_cognomeet_access_token_obj, \
    get_requested_data_for_daily, get_requested_data_for_week, get_requested_data_for_month, \
    create_file_access_management_obj
from CognoMeetApp.send_email import send_data_file_over_email
from cronjob_scripts.cognoai_cronjob_utils import create_cronjob_start_log, create_cronjob_end_log, send_cron_error_report
from CognoMeetApp.utils_validation import sanitize_input_string


def cronjob():
    cognomeet_cronjob_tracker_obj = get_cognomeet_cronjob_tracker_obj(
        COGNOMEET_ANALYTICS, CognoMeetCronjobTracker)
    if cognomeet_cronjob_tracker_obj:
        logger.info("cognomeet_export_analytics_cronjob is already running!",
                    extra={'AppName': 'CognoMeet'})
        return
    else:
        create_cognomeet_cronjob_tracker_obj(
            COGNOMEET_ANALYTICS, CognoMeetCronjobTracker)

    curr_file_name = "cognomeet_export_analytics_cronjob"
    cron_error_list = []
    try:
        log_obj_id = create_cronjob_start_log(curr_file_name)

        export_request_objs = CognoMeetExportDataRequest.objects.filter(
            report_type="meeting-analytics", is_completed=False)
        for export_request_obj in export_request_objs:
            requested_data = json.loads(export_request_obj.filter_param)

            cognomeet_access_token = sanitize_input_string(
                requested_data["cognomeet_access_token"])
            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                cognomeet_access_token, CognoMeetAccessToken)

            agents_usernames_list = requested_data["agents_usernames_list"]
            start_date = sanitize_input_string(requested_data["start_date"])
            end_date = sanitize_input_string(requested_data["end_date"])
            selected_filter_value = sanitize_input_string(
                requested_data["selected_filter_value"])

            if selected_filter_value == "1":
                requested_data_date_range = get_requested_data_for_daily()

            elif selected_filter_value == "2":
                requested_data_date_range = get_requested_data_for_week()

            elif selected_filter_value == "3":
                requested_data_date_range = get_requested_data_for_month()

            elif selected_filter_value == "4":
                requested_data_date_range = {
                    "startdate": start_date,
                    "enddate": end_date,
                }

            export_path = None
            cogno_meet_agent_username = requested_data["cogno_meet_agent_username"]
            cogno_meet_agent_obj = CognoMeetAgent.objects.filter(
                user__username=cogno_meet_agent_username).first()
            export_path = get_custom_meeting_analytics(
                cognomeet_access_token_obj, requested_data_date_range, cogno_meet_agent_obj, CognoMeetIO, CognoMeetAuditTrail, CognoMeetFileAccessManagement, CognoMeetAgent, agents_usernames_list)

            if export_path == "None" or export_path == None:
                logger.error("Analytics could not be generated for %s ",
                             str(cogno_meet_agent_obj.user.username), extra={'AppName': 'CognoMeet'})
                continue

            start_date = requested_data_date_range["startdate"]
            end_date = requested_data_date_range["enddate"]

            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            start_date = datetime.strftime(start_date, "%d-%m-%Y")
            end_date = datetime.strftime(end_date, "%d-%m-%Y")

            file_path = "/" + export_path
            file_access_management_key = create_file_access_management_obj(
                CognoMeetFileAccessManagement, cognomeet_access_token_obj, file_path)

            file_download_path = 'cogno-meet/download-file/' + \
                str(file_access_management_key)

            email_str = requested_data["email_list"]
            if email_str.strip() == '':
                email_str = str(cogno_meet_agent_obj.user.email)

            email_list = [email.strip()
                          for email in email_str.split(",") if email != ""]

            for email_id in email_list:
                email_subject = "CognoMeet Analytics | " + \
                    str(cogno_meet_agent_obj.user.username)
                send_data_file_over_email(email_id, start_date, end_date, cogno_meet_agent_obj.user.username, "Analytics",
                                          email_subject, file_download_path)
            export_request_obj.is_completed = True
            export_request_obj.save()
        delete_cognomeet_cronjob_tracker_obj(
            COGNOMEET_ANALYTICS, CognoMeetCronjobTracker)
    except Exception as e:
        delete_cognomeet_cronjob_tracker_obj(
            COGNOMEET_ANALYTICS, CognoMeetCronjobTracker)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
        logger.error("CognoMeet export analytics cronjob: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

    send_cron_error_report(cron_error_list, "cronjob", curr_file_name)

    create_cronjob_end_log(log_obj_id)
