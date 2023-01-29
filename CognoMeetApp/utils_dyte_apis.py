import os
import sys
import json
import logging
import time
import requests
from django.conf import settings
from dateutil.parser import parse
from CognoMeetApp.constants import *
from requests.exceptions import Timeout
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


def end_dyte_meeting_api(cognomeet_io_obj, CognoMeetAuditTrail, MeetingActualStartEndTime):
    try:
        server_details_obj = cognomeet_io_obj.cogno_meet_access_token.get_cognomeet_config_object()

        meeting_audit_trail = CognoMeetAuditTrail.objects.filter(
            cogno_meet_io=cognomeet_io_obj).first()

        if not meeting_audit_trail:
            meeting_audit_trail = CognoMeetAuditTrail.objects.create(
                cogno_meet_io=cognomeet_io_obj)

        HEADERS = {
            'Authorization': server_details_obj.api_key,
            'Content-Type': 'application/json'
        }

        DATA = json.dumps({'status': 'CLOSED'})

        URL = str(server_details_obj.base_url) + \
            f'/organizations/{server_details_obj.organization_id}/meetings/{cognomeet_io_obj.meeting_id}'

        try:            
            dyte_meeting_detail = requests.put(
                url=URL, headers=HEADERS, data=DATA)

            status_code = int(dyte_meeting_detail.status_code)
            response_data = json.loads(dyte_meeting_detail.content)

            # success and status code
            if status_code == 200:

                cognomeet_io_obj.meeting_status = "completed"
                cognomeet_io_obj.is_meeting_expired = True
                cognomeet_io_obj.save()

                # Updating meeting stats
                HEADERS = {
                    'Authorization': server_details_obj.api_key,
                    'Content-Type': 'application/json'
                }

                DATA = json.dumps({})

                URL = str(server_details_obj.base_url) + \
                    f'/organizations/{server_details_obj.organization_id}/meetings/{cognomeet_io_obj.meeting_id}/analytics'

                dyte_meeting_detail = requests.get(
                    url=URL, headers=HEADERS, data=DATA, timeout=server_details_obj.api_timeout_time)

                status_code = int(dyte_meeting_detail.status_code)
                response_data = json.loads(dyte_meeting_detail.content)

                if status_code == 200:
                    meeting_analytics = response_data["analytics"]

                    if len(meeting_analytics):
                        min_time = None
                        max_time = None
                        for data in meeting_analytics:
                            for participat_specific_data in data["events"]:
                                if min_time == None or max_time == None:
                                    min_time = parse(
                                        participat_specific_data["time"])
                                    max_time = parse(
                                        participat_specific_data["time"])
                                else:
                                    parsed_time = parse(
                                        participat_specific_data["time"])
                                    if(parsed_time < min_time):
                                        min_time = parsed_time
                                    if(parsed_time > max_time):
                                        max_time = parsed_time

                        time_diff = max_time - min_time
                        actul_start_end_time_obj = MeetingActualStartEndTime.objects.create(
                            start_time=min_time, end_time=max_time, cogno_meet_io=cognomeet_io_obj)
                        actul_start_end_time_obj.save()
                        meeting_audit_trail.total_call_duration = (
                            time_diff.seconds + time_diff.microseconds / 1000000)
                        meeting_audit_trail.save()

            else:
                logger.error(f'Error while closing Dyte meeting: {response_data}', extra={
                    'AppName': 'CognoMeet'})
        except Timeout as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Timeout end_dyte_meeting_api %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        except Exception as e:
            response_data = json.loads(dyte_meeting_detail.content)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(f'Error while closing Dyte meeting: {response_data}', extra={
                'AppName': 'CognoMeet'})
            logger.error("Inside end_dyte_meeting_api %s at %s", str(e),
                         str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error end_dyte_meeting_api %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})


def get_meeting_recording_url(cognomeet_io_obj, audit_trail_obj, CognoMeetRecording, CognoMeetFileAccessManagement):
    try:
        server_details_obj = cognomeet_io_obj.cogno_meet_access_token.get_cognomeet_config_object()

        HEADERS = {
            'Authorization': server_details_obj.api_key,
            'Content-Type': 'application/json'
        }

        DATA = json.dumps({})

        URL = str(server_details_obj.base_url) + \
            f'/organizations/{server_details_obj.organization_id}/meetings/{cognomeet_io_obj.meeting_id}/recordings'

        try:
            dyte_meeting_detail = requests.get(
                url=URL, headers=HEADERS, data=DATA, timeout=server_details_obj.api_timeout_time)

            status_code = int(dyte_meeting_detail.status_code)
            response_data = json.loads(dyte_meeting_detail.content)

            if status_code == 200:
                if 'success' in response_data and response_data['success']:
                    data = response_data['data']
                    recordings_list = data['recordings']
                    '''
                    This variable is used check if there is any recording from Dyte's side which is yet to be uploaded.
                    If there are recordings which have not been uploaded on their side, then we will again fetch recordings
                    for this meeting object during the next cronjob execution.
                    '''
                    all_recordings_uploaded = True
                    for recording in recordings_list:
                        if 'status' in recording and recording['status'] == "UPLOADED":
                            if 'downloadUrl' in recording and recording['downloadUrl']:
                                url = recording['downloadUrl']
                                cognomeet_recording_obj = CognoMeetRecording.objects.filter(cogno_meet_io=cognomeet_io_obj,
                                                                                            external_meeting_recording_url=url).first()
                                if not cognomeet_recording_obj:
                                    cognomeet_recording_obj = CognoMeetRecording.objects.create(
                                        cogno_meet_io=cognomeet_io_obj, external_meeting_recording_url=url)
                                    audit_trail_obj.cogno_meet_recording.add(
                                        cognomeet_recording_obj)
                            else:
                                all_recordings_uploaded = False
                        else:
                            all_recordings_uploaded = False
                    audit_trail_obj.save()

                    download_meeting_recording(
                        cognomeet_io_obj, audit_trail_obj, all_recordings_uploaded, CognoMeetRecording, CognoMeetFileAccessManagement)

            else:
                logger.error(f'Error while fetching meeting Dyte meeting recording: {response_data}', extra={
                    'AppName': 'CognoMeet'})

        except Timeout as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Timeout get_meeting_recording_url %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        except Exception:
            response_data = json.loads(dyte_meeting_detail.content)
            logger.error(f'Error while fetching meeting Dyte meeting recording: {response_data}', extra={
                'AppName': 'CognoMeet'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_meeting_recording_url %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})


def download_meeting_recording(cognomeet_io_obj, audit_trail_obj, all_recordings_uploaded, CognoMeetRecording, CognoMeetFileAccessManagement):
    try:

        recording_objs = audit_trail_obj.cogno_meet_recording.filter(
            file_access_management=None)

        for recording_obj in recording_objs:

            download_url = recording_obj.external_meeting_recording_url
            download_path = COGNOMEET_RECORDINGS_PATH + "/" + \
                str(cognomeet_io_obj.cogno_meet_access_token.key)
            file_name = str(cognomeet_io_obj.session_id) + \
                "_" + str(round(time.time())) + ".mp4"
            file_path = download_path + "/" + file_name

            if not os.path.exists(download_path):
                os.makedirs(download_path)

            response_data = requests.get(download_url)
            file_obj = open(file_path, 'wb')
            for chunk in response_data.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file_obj.write(chunk)

            file_obj.close()
            cognomeet_file_access_obj = CognoMeetFileAccessManagement.objects.create(
                file_path="/" + file_path, is_public=False, cogno_meet_access_token=cognomeet_io_obj.cogno_meet_access_token)

            recording_obj.file_access_management = cognomeet_file_access_obj
            recording_obj.save()

        if all_recordings_uploaded:
            cognomeet_io_obj.is_meeting_recording_fetched = True
            cognomeet_io_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error download_meeting_recording %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})


def get_dyte_meeting_total_participants(cognomeet_io_obj):
    try:
        total_number_of_participants = None

        server_details_obj = cognomeet_io_obj.cogno_meet_access_token.get_cognomeet_config_object()

        DATA = json.dumps({})

        URL = str(server_details_obj.base_url_v2) + \
            f'/meetings/{cognomeet_io_obj.meeting_id}/active-session'

        try:            
            dyte_meeting_detail = requests.get(url=URL, data=DATA, timeout=server_details_obj.api_timeout_time,
                                                auth=HTTPBasicAuth(server_details_obj.organization_id, server_details_obj.api_key))

            status_code = int(dyte_meeting_detail.status_code)
            response_data = json.loads(dyte_meeting_detail.content)

            if status_code == 200:
                if 'success' in response_data and response_data['success']:
                    total_number_of_participants = response_data['data']['live_participants']
                    
                    return total_number_of_participants
                else:
                    logger.error(f'Error while getting total participants in dyte meeting, success parameter value is: {response_data}', extra={
                        'AppName': 'CognoMeet'})    
            else:
                logger.error(f'Did not receive status_code as 200 in get_dyte_meeting_total_participants: {response_data}', extra={
                    'AppName': 'CognoMeet'})

        except Timeout as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Timeout get_dyte_meeting_total_participants %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
            return None
            
        except Exception as e:
            response_data = json.loads(dyte_meeting_detail.content)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(f'Error while getting dyte meeting participants count: {response_data}. Error {str(e)}', extra={
                'AppName': 'CognoMeet'})
            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_dyte_meeting_total_participants %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

    return total_number_of_participants
