from django.conf import settings
from django.shortcuts import HttpResponse
from django.utils.encoding import smart_str
from django.core.paginator import Page, Paginator, EmptyPage, PageNotAnInteger

import hashlib
import re
import sys
import logging
import mimetypes
import os
import pytz
import geocoder
from zipfile import ZipFile
import uuid
import json
from django.utils import timezone
from datetime import datetime, timedelta

from xlwt import Workbook, XFStyle, Font, Formula, easyxf

from CognoMeetApp.constants import *
from CognoMeetApp.utils_dyte_apis import *

from os import path

logger = logging.getLogger(__name__)


def create_cognomeet_config_objects(cognomeet_access_token_obj, CognoMeetConfig, CognoMeetTimers):
    CognoMeetConfig.objects.create(
        cogno_meet_access_token=cognomeet_access_token_obj)
    CognoMeetTimers.objects.create(
        cogno_meet_access_token=cognomeet_access_token_obj)


def get_cognomeet_agent_from_request(request, CognoMeetAgent):
    try:
        cogno_meet_agent_obj = CognoMeetAgent.objects.filter(user=request.user).first()
        return cogno_meet_agent_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in get_cognomeet_agent_from_request: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
    return None


def hash_crucial_info_in_data(message):
    final_string = message
    try:
        if message == None:
            return message

        # pan
        pan_pattern = re.findall(
            r"\b[a-zA-Z]{3}[pP][a-zA-Z][1-9][0-9]{3}[a-zA-Z]\b", message)
        for item in pan_pattern:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # email id
        email_pattern = re.findall(r"\S+@\S+", message)
        for item in email_pattern:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # dates
        # Regex date format: dd/mm/yyyy
        date_format_ddmmyyyy = re.findall(
            r"[\d]{1,2}/[\d]{1,2}/[\d]{2,4}", message)
        for item in date_format_ddmmyyyy:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # Regex date format: dd-mm-yy
        date_format_ddmmyyyy_two = re.findall(
            r"[\d]{1,2}-[\d]{1,2}-[\d]{2}", message)
        for item in date_format_ddmmyyyy_two:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # Regex date format: dd AUG YYYY
        date_format_ddmonthnameyyyy = re.findall(
            r"[\d]{1,2} [ADFJMNOS]\w* [\d]{2,4}", message)
        for item in date_format_ddmonthnameyyyy:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # Regex date format: AUG dd YYYY
        date_format_monthnameddyyyy = re.findall(
            r"[ADFJMNOS]\w* [\d]{1,2} [\d]{2,4}", message)
        for item in date_format_monthnameddyyyy:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # mobile number, account number, aadhar number (10-12 digits number
        # should have space before and after)
        mobile_pattern = re.findall(r"\b[0-9]{10,12}\b", message)
        for item in mobile_pattern:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # age and address (1-3 digits number
        # should have space before and after)
        age_pattern = re.findall(r"\b[0-9]{1,3}\b", message)
        for item in age_pattern:
            message = message.replace(
                item, hashlib.sha256(item.encode()).hexdigest())

        # customer_id (any string that contains atleast 1 digit)
        id_pattern = re.findall(r"\b[A-Za-z0-9]*\d[A-Za-z0-9]*\b", message)
        for item in id_pattern:
            if len(item) == 64:
                continue
            reg = r"\b" + str(item) + r"\b"
            message = re.sub(reg, hashlib.sha256(
                item.encode()).hexdigest(), message)

        final_string = message
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("hash_crucial_info_in_data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
    return final_string


def get_masked_data_if_hashed(message):
    final_string = message
    try:
        reg_pattern = r"[a-fA-F0-9]{64}"
        hash_pattern = re.findall(reg_pattern, message)
        for item in hash_pattern:
            message = message.replace(
                item, mask_hashed_data(item))

        final_string = message
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_masked_data_if_hashed: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

    return final_string


def file_download(file_key, CognoMeetFileAccessManagement, is_download_required=True):
    file_access_management_obj = None
    try:
        file_access_management_obj = CognoMeetFileAccessManagement.objects.get(
            key=file_key)

        path_to_file = file_access_management_obj.file_path

        original_file_name = file_access_management_obj.original_file_name

        filename = path_to_file.split("/")[-1]

        if original_file_name == None:
            original_file_name = filename

        path_to_file = settings.BASE_DIR + path_to_file
        mime_type, _ = mimetypes.guess_type(path_to_file)

        if os.path.exists(path_to_file):
            with open(path_to_file, 'rb') as fh:
                response = HttpResponse(
                    fh.read(), status=200, content_type=mime_type)

                if is_download_required:
                    response['Content-Disposition'] = 'attachment; filename="%s"' % smart_str(
                        str(original_file_name))
                return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error FileDownload %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

    return HttpResponse(status=404)


def get_cognomeet_access_token_obj(cognomeet_access_token, CognoMeetAccessToken):
    try:
        cognomeet_access_token_obj = CognoMeetAccessToken.objects.filter(
            key=cognomeet_access_token).first()
        return cognomeet_access_token_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_cognomeet_access_token_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
        return None


def get_invalid_access_token_response(custom_encrypt_obj, json):
    response = {}
    response['status'] = 500
    response['message'] = "Invalid Access Token"
    response = json.dumps(response)
    encrypted_response = custom_encrypt_obj.encrypt(response)
    response = {"Response": encrypted_response}
    return response


def get_requested_data_for_daily():
    # Last day data
    date_format = DATE_TIME_FORMAT

    start_date = datetime.now() - timedelta(days=1)
    start_date = start_date.strftime(date_format)
    end_date = start_date

    requested_data = {
        "startdate": start_date,
        "enddate": end_date,
    }
    return requested_data


def get_requested_data_for_week():
    # Last 7 days data
    date_format = DATE_TIME_FORMAT

    start_date = datetime.now() - timedelta(days=7)
    start_date = start_date.strftime(date_format)
    end_date = datetime.now() - timedelta(days=1)
    end_date = end_date.strftime(date_format)

    requested_data = {
        "startdate": start_date,
        "enddate": end_date,
    }
    return requested_data


def get_requested_data_for_month():
    # Last 30 days data
    date_format = DATE_TIME_FORMAT

    start_date = datetime.now() - timedelta(days=30)
    start_date = start_date.strftime(date_format)
    end_date = datetime.now() - timedelta(days=1)
    end_date = end_date.strftime(date_format)

    requested_data = {
        "startdate": start_date,
        "enddate": end_date,
    }
    return requested_data


def get_custom_meeting_support_history(cognomeet_access_token_obj, requested_data, cogno_meet_agent, CognoMeetIO, CognoMeetAuditTrail, CognoMeetFileAccessManagement, cogno_meet_agent_list=None, audit_trail_objs=None):

    def get_folder_path():
        folder_path = "CognoMeetApp/MeetingSupportHistory/" + \
            str(cogno_meet_agent.user.username) + "/"
        return folder_path

    def get_file_name(extention):
        file_name = "meeting_support_history_" + \
            str(start_date) + "_to_" + str(end_date) + extention
        return file_name

    def get_relative_file_path(extention=".xls"):
        relative_file_path = SECURED_FILES_PATH + \
            get_folder_path() + get_file_name(extention)
        return relative_file_path

    def get_absolute_file_path(extention=".xls"):
        absolute_folder_path = settings.SECURE_MEDIA_ROOT + get_folder_path()
        if not path.exists(absolute_folder_path):
            os.makedirs(absolute_folder_path)
        absolute_file_path = absolute_folder_path + get_file_name(extention)
        return absolute_file_path

    def create_new_sheet():
        global supervisor_col, agents_invited_col, invited_agents_connected_col, meeting_start_datetime_col, \
            meeting_end_datetime_col, time_spent_col, meeting_status_col, meeting_id_col, meeting_notes_col, \
            customer_location_col, attachment_col, auto_assigned_agent_col, session_initiated_by, meeting_initiated_by_col, \
            assigned_agents_count_col
        nonlocal wb_index

        sheet = support_history_wb.add_sheet(
            "Meeting Support History - " + str(wb_index))
        wb_index += 1

        sheet.write(0, 0, CUSTOMER_NAME)
        sheet.col(0).width = 256 * 20
        sheet.write(0, 1, CUSTOMER_MOBILE_NUMBER)
        sheet.col(1).width = 256 * 25
        sheet.write(0, 2, "Agent")
        sheet.col(2).width = 256 * 35

        prev_col = 2

        session_initiated_by = prev_col + 1
        sheet.write(0, session_initiated_by, "Session Initiated By")
        sheet.col(session_initiated_by).width = 256 * 35
        prev_col = session_initiated_by

        if cognomeet_access_token_obj.enable_invite_agent:
            agents_invited_col = prev_col + 1
            sheet.write(0, agents_invited_col, "Support Agents")
            sheet.col(agents_invited_col).width = 256 * 35
            prev_col = agents_invited_col

            invited_agents_connected_col = prev_col + 1
            sheet.write(0, invited_agents_connected_col,
                        "Support Agents Connected")
            sheet.col(invited_agents_connected_col).width = 256 * 35
            prev_col = invited_agents_connected_col

        meeting_initiated_by_col = prev_col + 1
        sheet.write(0, meeting_initiated_by_col, "Meeting Initiated By")
        sheet.col(meeting_initiated_by_col).width = 256 * 25
        prev_col = meeting_initiated_by_col

        meeting_start_datetime_col = prev_col + 1
        sheet.write(0, meeting_start_datetime_col, "Meeting Start Datetime")
        sheet.col(meeting_start_datetime_col).width = 256 * 25
        prev_col = meeting_start_datetime_col

        meeting_end_datetime_col = prev_col + 1
        sheet.write(0, meeting_end_datetime_col, "Meeting End Datetime")
        sheet.col(meeting_end_datetime_col).width = 256 * 25
        prev_col = meeting_end_datetime_col

        time_spent_col = prev_col + 1
        sheet.write(0, time_spent_col, "Time Spent")
        sheet.col(time_spent_col).width = 256 * 15
        prev_col = time_spent_col

        meeting_status_col = prev_col + 1
        sheet.write(0, meeting_status_col, "Meeting Status")
        sheet.col(meeting_status_col).width = 256 * 15
        prev_col = meeting_status_col

        meeting_id_col = prev_col + 1
        sheet.write(0, meeting_id_col, "Meeting ID")
        sheet.col(meeting_id_col).width = 256 * 45
        prev_col = meeting_id_col

        meeting_notes_col = prev_col + 1
        sheet.write(0, meeting_notes_col, "Meeting Notes")
        sheet.col(meeting_notes_col).width = 256 * 45
        prev_col = meeting_notes_col

        customer_location_col = prev_col + 1
        sheet.write(0, customer_location_col, "Customer Location")
        sheet.col(customer_location_col).width = 256 * 90
        prev_col = customer_location_col

        attachment_col = prev_col + 1
        sheet.write(0, attachment_col, "Attachment")
        sheet.col(attachment_col).width = 256 * 45
        prev_col = attachment_col

        if cogno_meet_agent.role == "admin_ally":
            supervisor_col = prev_col + 1
            sheet.write(0, supervisor_col, "Supervisors")
            sheet.col(supervisor_col).width = 256 * 20
            prev_col = supervisor_col

        return sheet

    try:
        logger.info("Inside get_custom_meeting_support_history",
                    extra={'AppName': 'CognoMeet'})
        start_date = requested_data["startdate"]
        end_date = requested_data["enddate"]

        date_format = DATE_TIME_FORMAT

        start_date = datetime.strptime(start_date, date_format).date()
        end_date = datetime.strptime(end_date, date_format).date()

        relative_file_path = get_relative_file_path()
        absolute_file_path = get_absolute_file_path()

        support_history_wb = Workbook()

        if not audit_trail_objs:
            cogno_meet_io = CognoMeetIO.objects.filter(
                cogno_meet_agent__in=cogno_meet_agent_list, meeting_start_date__gte=start_date, meeting_start_date__lte=end_date, is_meeting_expired=True)

            audit_trail_objs = CognoMeetAuditTrail.objects.filter(
                cogno_meet_io__in=cogno_meet_io).order_by('-pk')

        wb_index = 1
        sheet = create_new_sheet()

        index = 1
        for audit_trail_obj in audit_trail_objs:

            if index > 50000:
                index = 1
                sheet = create_new_sheet()

            client_location_details = json.loads(
                audit_trail_obj.customer_location_details)
            client_address = []
            for location_obj in client_location_details['items']:
                client_name = location_obj['client_name']
                longitude = location_obj['longitude']
                latitude = location_obj['latitude']
                if latitude == 'None' or longitude == 'None':
                    continue

                if "address" in location_obj and location_obj["address"] != "None":
                    client_address.append(
                        client_name + " - " + location_obj["address"])
                else:
                    try:
                        location = geocoder.google(
                            [latitude, longitude], method="reverse", key=GOOGLE_GEOCODER_KEY)
                        client_address.append(
                            client_name + " - " + location.address)
                        location_obj["address"] = location.address
                    except Exception:
                        logger.warning("Error in get_custom_meeting_support_history, client's address not found",
                                       extra={'AppName': 'CognoMeet'})

            screenshots = json.loads(audit_trail_obj.meeting_screenshorts_urls)
            audit_trail_obj.customer_location_details = json.dumps(
                client_location_details)
            audit_trail_obj.save()

            attachment_link = ""
            if len(screenshots['items']) > 0:
                zip_file_path = "secured_files/CognoMeetApp/MeetingSupportHistory/attachment_" + \
                    uuid.uuid4().hex + ".zip"

                zip_obj = ZipFile(zip_file_path, 'w')

                for screenshot_obj in screenshots['items']:
                    file_key = screenshot_obj['screenshot']
                    try:
                        file_access_management_obj = CognoMeetFileAccessManagement.objects.get(
                            key=file_key, is_public=False)

                        path_to_file = file_access_management_obj.file_path
                        file_name = path_to_file.split(os.sep)[-1]
                        zip_obj.write(path_to_file[1:], file_name)

                    except Exception:
                        logger.warning("Error in get_custom_meeting_support_history, Invalid file_key",
                                       extra={'AppName': 'CognoMeet'})
                zip_obj.close()

                zip_file_path = "/" + zip_file_path
                zip_file_obj = CognoMeetFileAccessManagement.objects.create(
                    file_path=zip_file_path, is_public=False, cogno_meet_access_token=cognomeet_access_token_obj, original_file_name='attachment.zip')
                attachment_link = settings.EASYCHAT_HOST_URL + \
                    '/cogno-meet/download-file/' + str(zip_file_obj.key)

            sheet.write(index, 0, audit_trail_obj.cogno_meet_io.customer_name)
            sheet.write(
                index, 1, get_masked_data_if_hashed(audit_trail_obj.cogno_meet_io.customer_mobile))

            meeting_agent_name = audit_trail_obj.cogno_meet_io.cogno_meet_agent.user.username

            sheet.write(
                index, 2, meeting_agent_name)
            
            if cognomeet_access_token_obj.enable_invite_agent:                
                agents_invited_list = audit_trail_obj.get_support_agents_invited()
                agents_invited_connected_list = audit_trail_obj.get_support_agents_joined()

                sheet.write(index, agents_invited_col, agents_invited_list)
                sheet.write(index, invited_agents_connected_col,
                            agents_invited_connected_list)

            lead_initiated_by = "-"
            sheet.write(index, session_initiated_by, lead_initiated_by)

            start_time = audit_trail_obj.cogno_meet_io.meeting_start_time
            end_time = audit_trail_obj.cogno_meet_io.meeting_end_time
            start_date = audit_trail_obj.cogno_meet_io.meeting_start_date
            start_time = datetime.combine(start_date, start_time)
            end_time = datetime.combine(start_date, end_time)
            sheet.write(index, meeting_initiated_by_col, "agent")
            sheet.write(index, meeting_start_datetime_col, str(start_time.astimezone(
                pytz.timezone(settings.TIME_ZONE)).strftime("%d-%m-%Y - %I:%M %p")))
            sheet.write(index, meeting_end_datetime_col, str(end_time.astimezone(
                pytz.timezone(settings.TIME_ZONE)).strftime("%d-%m-%Y - %I:%M %p")))
            sheet.write(index, time_spent_col, str(
                audit_trail_obj.get_readable_meeting_duration()))

            # Hardcoded as Completed as only expired meeting are being exported
            sheet.write(index, meeting_status_col, 'Completed')

            sheet.write(index, meeting_id_col, str(
                audit_trail_obj.cogno_meet_io.session_id))

            if audit_trail_obj.agent_notes == None:
                sheet.write(index, meeting_notes_col, "")
            else:
                sheet.write(index, meeting_notes_col,
                            audit_trail_obj.agent_notes)

            sheet.write(index, customer_location_col,
                        " | ".join(client_address))
            sheet.write(index, attachment_col, attachment_link)

            index += 1

        support_history_wb.save(absolute_file_path)

        logger.info("Returning file path " + str(relative_file_path),
                    extra={'AppName': 'CognoMeet'})
        return relative_file_path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_custom_meeting_support_history! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'CognoMeet'})

        return "None"


def create_file_access_management_obj(CognoMeetFileAccessManagement, access_token, file_path, is_public=False):
    try:
        file_access_management_obj = CognoMeetFileAccessManagement.objects.create(
            file_path=file_path, is_public=is_public, cogno_meet_access_token=access_token)

        return str(file_access_management_obj.key)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in create_file_access_management_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
    return None


def create_export_data_request_obj(cognomeet_agent, report_type, filter_param, CognoMeetExportDataRequest):
    CognoMeetExportDataRequest.objects.create(agent=cognomeet_agent, report_type=report_type, filter_param=filter_param)


def paginate(obj_list, items_per_page, page):
    try:
        page_object_count = obj_list.count()
    except Exception:
        page_object_count = len(obj_list)

    paginator = Paginator(obj_list, items_per_page)

    try:
        obj_list = paginator.page(page)
    except PageNotAnInteger:
        obj_list = paginator.page(1)
    except EmptyPage:
        obj_list = paginator.page(paginator.num_pages)

    if page:
        start_point = items_per_page * (int(page) - 1) + 1
        end_point = min(items_per_page *
                        int(page), page_object_count)
    else:
        start_point = 1
        end_point = min(items_per_page, page_object_count)

    return page_object_count, obj_list, start_point, end_point


def get_pagination_data(page_object: Page):
    try:
        pagination_data = {
            'has_other_pages': page_object.has_other_pages(),
            'page_range': page_object.paginator.page_range.stop,
            'number': page_object.number,
            'num_pages': page_object.paginator.num_pages,
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_pagination_data %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        pagination_data = {
            'has_other_pages': False,
        }

    return pagination_data


def parse_request_io_data(audit_trails, CognoMeetChatHistory):
    try:
        est = pytz.timezone(settings.TIME_ZONE)
        required_data_list = []
        for audit_trail in audit_trails:
            chat_history = CognoMeetChatHistory.filter(
                cogno_meet_io=audit_trail.cogno_meet_io)
            if chat_history.count() == 0:
                is_chat_available = False
            else:
                is_chat_available = True

            if len(audit_trail.get_meeting_screenshot()):
                is_screen_shot_available = True
            else:
                is_screen_shot_available = False

            if not (audit_trail.customer_location_details == None or audit_trail.customer_location_details == ""):
                client_location_details = json.loads(
                    audit_trail.customer_location_details)
                if (len(client_location_details["items"]) == 0):
                    location_available = False
                else:
                    location_available = True
            else:
                location_available = False
            
            start_time = audit_trail.cogno_meet_io.meeting_start_time.strftime("%-I:%M %p")
            end_time = audit_trail.cogno_meet_io.meeting_end_time.strftime("%-I:%M %p")
            if audit_trail.actual_meeting_start_time() != None:
                start_time, end_time = audit_trail.actual_meeting_start_time()
                if start_time == end_time:
                    end_time = audit_trail.cogno_meet_io.meeting_end_time.strftime("%-I:%M %p")
                else:
                    end_time = end_time.astimezone(est).strftime("%-I:%M %p")
                start_time = start_time.astimezone(est).strftime("%-I:%M %p")
            
            agent_joined_time = audit_trail.agent_joined_time
            if not agent_joined_time:
                agent_joined_time = '-'
            else:
                agent_joined_time = str(audit_trail.agent_joined_time.astimezone(est).strftime("%-I:%M %p"))
                
            curr = {
                'session_id': str(audit_trail.cogno_meet_io.session_id),
                'meeting_id': str(audit_trail.cogno_meet_io.meeting_id),
                'meeting_room_name': audit_trail.cogno_meet_io.meeting_room_name,
                'meeting_title': audit_trail.cogno_meet_io.meeting_title,
                'meeting_request_creation_datetime': str(audit_trail.cogno_meet_io.meeting_request_creation_datetime),
                'customer_name': audit_trail.cogno_meet_io.customer_name,
                'customer_mobile': str(audit_trail.cogno_meet_io.customer_mobile),
                'customer_email': str(audit_trail.cogno_meet_io.customer_email),
                'meeting_password': str(audit_trail.cogno_meet_io.meeting_password),
                'meeting_start_date': str(audit_trail.cogno_meet_io.meeting_start_date.strftime("%d-%b-%Y")),
                'meeting_start_time': start_time,
                'meeting_end_time': end_time,
                'meeting_status': str(audit_trail.cogno_meet_io.meeting_status),
                'is_meeting_expired': str(audit_trail.cogno_meet_io.is_meeting_expired),
                'cogno_meet_access_token': str(audit_trail.cogno_meet_io.cogno_meet_access_token.key),
                'cogno_meet_agent': str(audit_trail.cogno_meet_io.cogno_meet_agent.user.username),
                'meeting_screenshorts_urls': str(audit_trail.meeting_screenshorts_urls),
                'meeting_feedback_agent': audit_trail.meeting_feedback_agent,
                'agent_rating': str(audit_trail.agent_rating),
                'agent_notes': str(audit_trail.agent_notes),
                'customer_location_details': str(audit_trail.customer_location_details),
                'total_call_duration': str(audit_trail.total_call_duration),
                'agent_joined_time': agent_joined_time,
                'audit_trail_pk': str(audit_trail.pk),
                'actual_status': 'Completed',
                'is_chat_available': str(is_chat_available),
                'is_screen_shot_available': str(is_screen_shot_available),
                'location_available': str(location_available),
                'support_agents_invited': audit_trail.get_support_agents_invited(),
                'support_agents_joined': audit_trail.get_support_agents_joined()
            }
            required_data_list.append(curr)
        return required_data_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_request_io_data %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
        return []


def check_cogno_meet_status(meeting_io):
    try:
        start_date = meeting_io.meeting_start_date
        current_date = datetime.now()
        meeting_start_time = meeting_io.meeting_start_time
        current_time = current_date.strftime("%H:%M:%S")
        if start_date > current_date.date():
            return 'waiting'
        elif start_date < current_date.date():
            meeting_io.is_meeting_expired = True
            meeting_io.save()
        elif str(meeting_start_time) > str(current_time):
            return 'waiting'
        else:
            meeting_end_time = meeting_io.meeting_end_time
            if str(meeting_end_time) < str(current_time):
                meeting_io.is_meeting_expired = True
                meeting_io.save()
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_cogno_meet_status %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return False


def get_todays_meeting_data(meeting_io):
    meeting_list = []
    for meeting_obj in meeting_io:
        meeting_start_date = meeting_obj.meeting_start_date
        meeting_start_time = meeting_obj.meeting_start_time
        meeting_end_time = meeting_obj.meeting_end_time

        if meeting_start_date:
            meeting_start_date = meeting_start_date.strftime(
                "%b %d, %Y")

        if meeting_start_time:
            meeting_start_time = meeting_start_time.strftime(
                "%-I:%M %p")

        if meeting_end_time:
            meeting_end_time = meeting_end_time.strftime("%-I:%M %p")

        meeting_list.append({
            'id': str(meeting_obj.pk),
            "description": meeting_obj.meeting_title,
            "start_date": meeting_start_date,
            "start_time": meeting_start_time,
            "end_time": meeting_end_time,
            "is_expired": meeting_obj.is_meeting_expired,
            "agent": meeting_obj.cogno_meet_agent.user.username,
        })

    return meeting_list


def parse_meeting_data(meeting_io):
    try:
        requested_data = []
        for cogno_meet_obj in meeting_io:            
            if cogno_meet_obj.is_meeting_expired == False:
                current_data = {
                    'customer_name': str(cogno_meet_obj.customer_name),
                    'mobile_number': str(cogno_meet_obj.customer_mobile),
                    'customer_email': str(cogno_meet_obj.customer_email),
                    'meeting_title': str(cogno_meet_obj.meeting_title),
                    'meeting_start_date': str(cogno_meet_obj.meeting_start_date.strftime("%d-%b-%Y")),
                    'meeting_start_time': str(cogno_meet_obj.meeting_start_time.strftime("%-I:%M %p")),
                    'meeting_end_time': str(cogno_meet_obj.meeting_end_time.strftime("%-I:%M %p")),
                    'meeting_password': str(cogno_meet_obj.meeting_password),
                    'agent': str(cogno_meet_obj.cogno_meet_agent.user.username),
                    'agent_type': str(cogno_meet_obj.cogno_meet_agent.role),
                    'cogno_meet_pk': str(cogno_meet_obj.pk),
                    'meeting_start_date_unformatted': str(cogno_meet_obj.meeting_start_date.strftime('%d/%m/%Y')),
                    'meeting_start_time_unformatted': str(cogno_meet_obj.meeting_start_time.strftime),
                    'meeting_end_time_unformatted': str(cogno_meet_obj.meeting_end_time.strftime),
                    # 'supervisor':
                }
                requested_data.append(current_data)

        return requested_data
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_request_io_data %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
        return []


def archive_cognomeet_session(cognomeet_io_obj, CognoMeetAuditTrail, MeetingActualStartEndTime):
    try:
        end_dyte_meeting_api(cognomeet_io_obj, CognoMeetAuditTrail, MeetingActualStartEndTime)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error archive_cognomeet_session %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})


def get_agent_name_from_request(request):
    agent_name = request.user.username
    if request.user.first_name != "":
        agent_name = request.user.first_name
        if request.user.last_name != "":
            agent_name += " " + request.user.last_name

    return agent_name


def get_agent_name_from_user(user):
    agent_name = user.username
    if user.first_name != "":
        agent_name = user.first_name
        if user.last_name != "":
            agent_name += " " + user.last_name

    return agent_name


def get_custom_meeting_analytics(cognomeet_access_token_obj, requested_data, cogno_meet_agent, CognoMeetIO, CognoMeetAuditTrail, CognoMeetFileAccessManagement, CognoMeetAgent, cogno_meet_agents_list):

    def get_folder_path():
        folder_path = "CognoMeetApp/MeetingAnalytics/" + \
            str(cogno_meet_agent.user.username) + "/"
        return folder_path

    def get_file_name(extention):
        file_name = "Meeting_Analytics_FromDate(" + \
            str(start_date) + ")-ToDate(" + str(end_date) + ")" + extention
        return file_name

    def get_relative_file_path(extention=".xls"):
        relative_file_path = SECURED_FILES_PATH + \
            get_folder_path() + get_file_name(extention)
        return relative_file_path

    def get_absolute_file_path(extention=".xls"):
        absolute_folder_path = settings.SECURE_MEDIA_ROOT + get_folder_path()
        if not path.exists(absolute_folder_path):
            os.makedirs(absolute_folder_path)
        absolute_file_path = absolute_folder_path + get_file_name(extention)
        return absolute_file_path

    def create_meeting_analytics_sheet():
        global meeting_scheduled_col, meeting_initiated_by_customer_floating_button_col,\
            meeting_initiated_by_customer_greeting_bubble_col, meeting_initiated_by_customer_inactivity_pop_up_col,\
            meeting_initiated_by_customer_exit_intent, meetings_completed_col,\
            avg_call_duration, session_initiated_in_cobrowsing_col,\
            session_initiated_in_video_conference_col
        nonlocal wb_index

        # First Sheet
        sheet = meeting_analytics_wb.add_sheet(
            "Meeting Analytics")
        wb_index += 1
        prev_col = 0

        meeting_scheduled_col = prev_col
        sheet.write(0, meeting_scheduled_col, 'Meeting Scheduled')
        sheet.col(meeting_scheduled_col).width = 256 * 20
        prev_col = meeting_scheduled_col

        meeting_initiated_by_customer_floating_button_col = prev_col + 1
        sheet.write(0, meeting_initiated_by_customer_floating_button_col,
                    'Meeting initiated by customer (Floating Button/Icon)')
        sheet.col(
            meeting_initiated_by_customer_floating_button_col).width = 256 * 35
        prev_col = meeting_initiated_by_customer_floating_button_col

        meeting_initiated_by_customer_greeting_bubble_col = prev_col + 1
        sheet.write(0, meeting_initiated_by_customer_greeting_bubble_col,
                    'Meeting Initiated by customer (Greeting Bubble)')
        sheet.col(
            meeting_initiated_by_customer_greeting_bubble_col).width = 256 * 35
        prev_col = meeting_initiated_by_customer_greeting_bubble_col

        meeting_initiated_by_customer_inactivity_pop_up_col = prev_col + 1
        sheet.write(0, meeting_initiated_by_customer_inactivity_pop_up_col,
                    'Meeting Initiated by customer (Inactivity Pop up)')
        sheet.col(
            meeting_initiated_by_customer_inactivity_pop_up_col).width = 256 * 35
        prev_col = meeting_initiated_by_customer_inactivity_pop_up_col

        meeting_initiated_by_customer_exit_intent = prev_col + 1
        sheet.write(0, meeting_initiated_by_customer_exit_intent,
                    'Meeting Initiated by customer (Exit Intent)')
        sheet.col(meeting_initiated_by_customer_exit_intent).width = 256 * 35
        prev_col = meeting_initiated_by_customer_exit_intent

        meetings_completed_col = prev_col + 1
        sheet.write(0, meetings_completed_col, 'Meetings Completed')
        sheet.col(5).width = 256 * 35
        prev_col = meetings_completed_col

        avg_call_duration = prev_col + 1
        sheet.write(0, avg_call_duration, 'Average Call Duration (min.)')
        sheet.col(avg_call_duration).width = 256 * 35
        prev_col = avg_call_duration

        session_initiated_in_cobrowsing_col = prev_col + 1
        sheet.write(0, session_initiated_in_cobrowsing_col,
                    'Session Initiated in Co-browsing')
        sheet.col(session_initiated_in_cobrowsing_col).width = 256 * 35
        prev_col = session_initiated_in_cobrowsing_col

        session_initiated_in_video_conference_col = prev_col + 1
        sheet.write(0, session_initiated_in_video_conference_col,
                    'Session Initiated in Video Conference')
        sheet.col(session_initiated_in_video_conference_col).width = 256 * 35
        prev_col = session_initiated_in_video_conference_col

        return sheet

    def create_agent_wise_video_meeting_analytics_sheet():
        global agent_email_col, scheduled_meeting_col, completed_meeting_col
        nonlocal wb_index

        # Second Sheet
        sheet = meeting_analytics_wb.add_sheet("Agent-wise Analytics")
        wb_index += 1
        prev_col = 0

        agent_email_col = prev_col
        sheet.write(0, agent_email_col, 'Agent Email')
        sheet.col(agent_email_col).width = 256 * 35
        prev_col = agent_email_col

        scheduled_meeting_col = prev_col + 1
        sheet.write(0, scheduled_meeting_col,
                    'Scheduled Meeting')
        sheet.col(scheduled_meeting_col).width = 256 * 35
        prev_col = scheduled_meeting_col

        completed_meeting_col = prev_col + 1
        sheet.write(0, completed_meeting_col,
                    'Completed Meeting')
        sheet.col(completed_meeting_col).width = 256 * 35
        prev_col = completed_meeting_col

        return sheet

    try:
        logger.info("Inside create_meeting_analytics_sheet",
                    extra={'AppName': 'CognoMeet'})

        start_date = requested_data["startdate"]
        end_date = requested_data["enddate"]

        date_format = DATE_TIME_FORMAT

        start_date = datetime.strptime(start_date, date_format).date()
        end_date = datetime.strptime(end_date, date_format).date()

        relative_file_path = get_relative_file_path()
        absolute_file_path = get_absolute_file_path()

        meeting_analytics_wb = Workbook()

        cognomeet_agent_objs = CognoMeetAgent.objects.filter(
            user__username__in=cogno_meet_agents_list)

        cogno_meet_io = CognoMeetIO.objects.filter(cogno_meet_access_token=cognomeet_access_token_obj,
                                                   cogno_meet_agent__in=cognomeet_agent_objs, meeting_start_date__gte=start_date, meeting_start_date__lte=end_date)

        wb_index = 1
        sheet = create_meeting_analytics_sheet()

        # total schedule meeting count
        meeting_scheduled_count = cogno_meet_io.count()
        sheet.write(1, meeting_scheduled_col, meeting_scheduled_count)

        # Meeting initiated by customer (Floating Button/Icon) - will be 0 for scheduled meet
        sheet.write(1, meeting_initiated_by_customer_floating_button_col, 0)

        # Meeting Initiated by customer (Greeting Bubble) - will be 0 for scheduled meet
        sheet.write(1, meeting_initiated_by_customer_greeting_bubble_col, 0)

        # Meeting Initiated by customer (Inactivity Pop up) - will be 0 for scheduled meet
        sheet.write(1, meeting_initiated_by_customer_inactivity_pop_up_col, 0)

        # Meeting Initiated by customer (Exit Intent) - will be 0 for scheduled meet
        sheet.write(1, meeting_initiated_by_customer_exit_intent, 0)

        # Meetings Completed
        completed_meeting_objs = cogno_meet_io.filter(is_meeting_expired=True)
        completed_meeting_count = completed_meeting_objs.count()
        sheet.write(1, meetings_completed_col, completed_meeting_count)

        # average call duration
        total_meeting_time = 0
        audit_trail_objs = CognoMeetAuditTrail.objects.filter(
            cogno_meet_io__in=completed_meeting_objs)
        for audit_trail_obj in audit_trail_objs:
            total_meeting_time += audit_trail_obj.total_call_duration

        if completed_meeting_count:
            average_call_duration_in_sec = total_meeting_time / completed_meeting_count
        else:
            average_call_duration_in_sec = 0

        minutes_get, seconds_get = divmod(average_call_duration_in_sec, 60)
        hours_get, minutes_get = divmod(minutes_get, 60)
        duration_in_string = ''
        if hours_get:
            duration_in_string += str(hours_get) + ' hr '
        if minutes_get:
            duration_in_string += str(minutes_get) + ' min '
        if seconds_get:
            duration_in_string += str(int(seconds_get)) + ' sec'
        if duration_in_string == '':
            duration_in_string = '0 min'
        sheet.write(1, avg_call_duration, duration_in_string)

        # Session Initiated in Co-browsing - will be 0 for scheduled meet
        sheet.write(1, session_initiated_in_cobrowsing_col, 0)

        # Session Initiated in Video Conference - will be same as scheduled meeting for scheduled meet
        sheet.write(1, session_initiated_in_video_conference_col,
                    meeting_scheduled_count)

        sheet = create_agent_wise_video_meeting_analytics_sheet()
        index = 1
        for agent_username in cogno_meet_agents_list:

            cognomeet_agents_obj = CognoMeetAgent.objects.filter(
                user__username=agent_username).first()

            # agent email
            sheet.write(index, agent_email_col, agent_username)

            if cognomeet_agents_obj:
                # Scheduled meet
                cogno_meet_io_objs = CognoMeetIO.objects.filter(
                    cogno_meet_access_token=cognomeet_access_token_obj, cogno_meet_agent=cognomeet_agents_obj, meeting_start_date__gte=start_date, meeting_start_date__lte=end_date)
                scheduled_meet_count = cogno_meet_io_objs.count()
                sheet.write(index, scheduled_meeting_col, scheduled_meet_count)

                # Completed Meeting
                completed_meeting_count = cogno_meet_io_objs.filter(
                    is_meeting_expired=True).count()
                sheet.write(index, completed_meeting_col,
                            completed_meeting_count)
            else:
                # Scheduled meet
                sheet.write(index, scheduled_meeting_col, 0)

                # Completed Meeting
                sheet.write(index, completed_meeting_col, 0)

            index += 1

        meeting_analytics_wb.save(absolute_file_path)

        logger.info("Returning file path " + str(relative_file_path),
                    extra={'AppName': 'CognoMeet'})
        return relative_file_path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_meeting_analytics_sheet! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'CognoMeet'})

        return "None"


def check_access_token(request, file_key, CognoMeetAgent, CobrowsingFileAccessManagement):
    try:
        active_agent = get_cognomeet_agent_from_request(
            request, CognoMeetAgent)
        file_access_management_obj = CobrowsingFileAccessManagement.objects.filter(
            key=file_key).first()
        return active_agent.get_access_token_obj() == file_access_management_obj.cogno_meet_access_token
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in check_access_token %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
    return False
