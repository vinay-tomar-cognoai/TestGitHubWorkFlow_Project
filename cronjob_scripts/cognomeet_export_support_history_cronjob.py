import json
import sys
from datetime import datetime
from CognoMeetApp.models import CognoMeetIO, CognoMeetCronjobTracker, \
    CognoMeetAuditTrail, CognoMeetExportDataRequest, CognoMeetFileAccessManagement, \
    CognoMeetAccessToken, CognoMeetAgent
from CognoMeetApp.utils_cronjob_tracker import *
from CognoMeetApp.utils import get_custom_meeting_support_history, get_cognomeet_access_token_obj, \
    get_requested_data_for_daily, get_requested_data_for_week, get_requested_data_for_month, \
    create_file_access_management_obj
from CognoMeetApp.send_email import send_data_file_over_email
from cronjob_scripts.cognoai_cronjob_utils import create_cronjob_start_log, create_cronjob_end_log, send_cron_error_report


def cronjob():
    cognomeet_cronjob_tracker_obj = get_cognomeet_cronjob_tracker_obj(
        COGNOMEET_SUPPORT_HISTORY, CognoMeetCronjobTracker)
    if cognomeet_cronjob_tracker_obj:
        logger.info("cognomeet_export_support_history_cronjob is already running!",
                    extra={'AppName': 'CognoMeet'})
        return
    else:
        create_cognomeet_cronjob_tracker_obj(
            COGNOMEET_SUPPORT_HISTORY, CognoMeetCronjobTracker)

    curr_file_name = "cognomeet_export_support_history_cronjob"
    cron_error_list = []
    try:
        log_obj_id = create_cronjob_start_log(curr_file_name)

        export_request_objs = CognoMeetExportDataRequest.objects.filter(
            report_type="meeting-support-history", is_completed=False)
        for export_request_obj in export_request_objs:
            requested_data = json.loads(export_request_obj.filter_param)

            cognomeet_access_token = requested_data["cognomeet_access_token"]
            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                cognomeet_access_token, CognoMeetAccessToken)
            cogno_meet_agent = export_request_obj.agent

            agents_list = []
            if 'agents_list' in requested_data:
                agents_list = requested_data["agents_list"]

            cognomeet_agents_objs = CognoMeetAgent.objects.filter(
                user__username__in=agents_list)

            if requested_data["selected_filter_value"] == "1":
                requested_data_date_range = get_requested_data_for_daily()

            elif requested_data["selected_filter_value"] == "2":
                requested_data_date_range = get_requested_data_for_week()

            elif requested_data["selected_filter_value"] == "3":
                requested_data_date_range = get_requested_data_for_month()

            elif requested_data["selected_filter_value"] == "4":
                requested_data_date_range = {
                    "startdate": requested_data["startdate"],
                    "enddate": requested_data["enddate"]
                }
            export_path = get_custom_meeting_support_history(
                cognomeet_access_token_obj, requested_data_date_range, cogno_meet_agent, CognoMeetIO, CognoMeetAuditTrail,
                CognoMeetFileAccessManagement, cognomeet_agents_objs)
            if export_path == "None" or export_path == None:
                logger.error("Support history could not be generated for %s ",
                             str(cogno_meet_agent.user.username), extra={'AppName': 'CognoMeet'})
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

            email_str = requested_data["email"]
            if email_str.strip() == '':
                email_str = str(cogno_meet_agent.user.email)

            email_list = [email.strip()
                          for email in email_str.split(",") if email != ""]

            for email_id in email_list:
                email_subject = "CognoMeet Support History | " + \
                    str(cogno_meet_agent.user.username)
                send_data_file_over_email(email_id, start_date, end_date, cogno_meet_agent.user.username, "Support History",
                                          email_subject, file_download_path)
            export_request_obj.is_completed = True
            export_request_obj.save()
        delete_cognomeet_cronjob_tracker_obj(
            COGNOMEET_SUPPORT_HISTORY, CognoMeetCronjobTracker)
    except Exception as e:
        delete_cognomeet_cronjob_tracker_obj(
            COGNOMEET_SUPPORT_HISTORY, CognoMeetCronjobTracker)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
        logger.error("CognoMeet export support history cronjob: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

    send_cron_error_report(cron_error_list, "cronjob", curr_file_name)

    create_cronjob_end_log(log_obj_id)
