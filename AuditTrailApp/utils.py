# Logger
import logging
import mimetypes
import os
import sys
from datetime import datetime, timedelta
from os import path
from os.path import basename
from zipfile import ZipFile

import pytz
from django.conf import settings
from django.db.models import Q
from django.shortcuts import HttpResponse
from django.utils.encoding import smart_str
from xlwt import Workbook
from AuditTrailApp.constants import *

# Django REST framework

logger = logging.getLogger(__name__)


def logout_all(username, UserSession, Session):
    try:
        logger.info("In logout_all", extra={
                    'AppName': 'AuditTrailApp', 'user_id': str(username)})
        user_session_objs = UserSession.objects.filter(user__username=username)
        for user_session_obj in user_session_objs:
            delete_user_session(user_session_obj, Session)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In logout_all: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'AuditTrailApp', 'user_id': str(username)})


def delete_user_session(user_session, Session):
    try:
        logger.info("In delete_user_session", extra={'AppName': 'AuditTrailApp',
                                                     'user_id': user_session.user.username})
        session_objs = Session.objects.filter(pk=user_session.session_key)
        user_session.delete()
        if session_objs:
            session_objs.delete()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In delete_user_session: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'AuditTrailApp', 'user_id': str(user_session.user.username)})


def get_formatted_date(date_obj):
    data = None
    try:
        if date_obj:
            est = pytz.timezone(settings.TIME_ZONE)
            data = date_obj.astimezone(
                est).strftime("%d %b %Y %I:%M:%S %p")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_formatted_date %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'AuditTrailApp'})
    return data


def get_app_display_name(given_app_name):
    display_name = ""
    for app_name in APP_NAMES:
        if app_name[0].lower() == given_app_name.lower():
            display_name = app_name[1]
    return display_name


def parse_audit_trail_details(audit_trail_obj):
    data = {}
    try:
        data = {
            "id": audit_trail_obj.id,
            "app_name": get_app_display_name(audit_trail_obj.app_name),
            "user": audit_trail_obj.user.username,
            "datetime": get_formatted_date(audit_trail_obj.datetime),
            "action_type": audit_trail_obj.action_type,
            "description": audit_trail_obj.description,
            "request_data_dump": audit_trail_obj.request_data_dump,
            "api_end_point": audit_trail_obj.api_end_point,
            "ip_address": audit_trail_obj.ip_address,
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In parse_audit_trail_details: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'AuditTrailApp'})
    return data


def add_audit_trail(app_name, user, action_type, description, request_data_dump, api_end_point, ip_address):
    try:
        try:
            ip_address = ip_address.split(",")[0].strip()
        except Exception:
            pass

        from AuditTrailApp.models import CognoAIAuditTrail
        CognoAIAuditTrail.objects.create(
            app_name=app_name,
            user=user,
            action_type=action_type,
            description=description,
            request_data_dump=request_data_dump,
            api_end_point=api_end_point,
            ip_address=ip_address
        )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In add_audit_trail: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'AuditTrailApp'})


def get_requested_data_for_daily():
    # Last day data

    start_date = datetime.now() - timedelta(days=1)
    start_date = start_date.strftime(COMMON_DATE_FORMAT)
    end_date = start_date

    requested_data = {
        "startdate": start_date,
        "enddate": end_date,
    }
    return requested_data


def get_requested_data_for_week():
    # Last 7 days data

    start_date = datetime.now() - timedelta(days=7)
    start_date = start_date.strftime(COMMON_DATE_FORMAT)
    end_date = datetime.now() - timedelta(days=1)
    end_date = end_date.strftime(COMMON_DATE_FORMAT)

    requested_data = {
        "startdate": start_date,
        "enddate": end_date,
    }
    return requested_data


def get_requested_data_for_month():
    # Last 30 days data

    start_date = datetime.now() - timedelta(days=30)
    start_date = start_date.strftime(COMMON_DATE_FORMAT)
    end_date = datetime.now() - timedelta(days=1)
    end_date = end_date.strftime(COMMON_DATE_FORMAT)

    requested_data = {
        "startdate": start_date,
        "enddate": end_date,
    }
    return requested_data


def get_requested_data_custom(start_date, end_date):

    start_date = start_date.strftime(COMMON_DATE_FORMAT)
    end_date = end_date.strftime(COMMON_DATE_FORMAT)

    requested_data = {
        "startdate": start_date,
        "enddate": end_date,
    }
    return requested_data


def file_download(file_key, FileAccessManagement):
    try:
        file_access_management_obj = FileAccessManagement.objects.get(
            key=file_key)

        path_to_file = file_access_management_obj.file_path
        original_file_name = file_access_management_obj.original_file_name

        if original_file_name is None:
            original_file_name = path_to_file.split("/")[-1]

        path_to_file = settings.BASE_DIR + path_to_file
        mime_type, _ = mimetypes.guess_type(path_to_file)

        if os.path.exists(path_to_file):
            with open(path_to_file, 'rb') as fh:
                response = HttpResponse(
                    fh.read(), status=200, content_type=mime_type)
                response['Content-Disposition'] = 'attachment; filename="%s"' % smart_str(
                    str(original_file_name))
                return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error FileDownload %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'AuditTrailApp'})

    return HttpResponse(status=404)


def get_custom_audit_trail_dump(requested_data, user, CognoAIAuditTrail):

    def get_folder_path():
        folder_path = "AuditTrailApp/AuditTrailDump/" + str(user.username) + "/"
        return folder_path

    def get_file_name(extension):
        file_name = "audit_trail_" + str(start_date) + "_to_" + str(end_date) + extension
        return file_name

    def get_relative_file_path(extension=".xls"):
        return "secured_files/" + get_folder_path() + get_file_name(extension)

    def get_absolute_file_path(extension=".xls"):
        absolute_folder_path = settings.SECURE_MEDIA_ROOT + get_folder_path()
        if not os.path.exists(absolute_folder_path):
            os.mkdir(absolute_folder_path)
        return absolute_folder_path + get_file_name(extension)

    def create_new_sheet():
        nonlocal wb_index

        new_sheet = data_dump_wb.add_sheet("Support History - " + str(wb_index))
        wb_index += 1

        new_sheet.write(0, 0, "App Name")
        new_sheet.col(0).width = 256 * 20
        new_sheet.write(0, 1, "User")
        new_sheet.col(1).width = 256 * 20
        new_sheet.write(0, 2, "Time Stamp")
        new_sheet.col(2).width = 256 * 25
        new_sheet.write(0, 3, "Event Category")
        new_sheet.col(3).width = 256 * 30
        new_sheet.write(0, 4, "Change Summary")
        new_sheet.col(4).width = 256 * 30
        new_sheet.write(0, 5, "Change Object")
        new_sheet.col(5).width = 256 * 50
        new_sheet.write(0, 6, "API End Point")
        new_sheet.col(6).width = 256 * 50
        new_sheet.write(0, 7, "IP Address")
        new_sheet.col(7).width = 256 * 20

        return new_sheet

    try:
        logger.info("Inside get_custom_audit_trail_dump", extra={'AppName': 'EasyAssist'})
        from datetime import datetime, timedelta
        start_date = requested_data["startdate"]
        end_date = requested_data["enddate"]

        start_date = datetime.strptime(start_date, COMMON_DATE_FORMAT).date()
        end_date = datetime.strptime(end_date, COMMON_DATE_FORMAT).date()

        relative_file_path = get_relative_file_path()
        absolute_file_path = get_absolute_file_path()

        yesterdays_date = (datetime.now() - timedelta(days=1)).date()

        if os.path.exists(absolute_file_path) and end_date < yesterdays_date:
            return relative_file_path

        data_dump_wb = Workbook()

        data_dump_objects = CognoAIAuditTrail.objects.filter(
            datetime__date__gte=start_date, datetime__date__lte=end_date)

        wb_index = 1
        sheet = create_new_sheet()

        index = 1
        for data_dump_object in data_dump_objects:

            if index > 50000:
                index = 1
                sheet = create_new_sheet()

            sheet.write(index, 0, get_app_display_name(data_dump_object.app_name))
            if data_dump_object.user:
                sheet.write(index, 1, data_dump_object.user.username)
            else:
                sheet.write(index, 1, "-")
            sheet.write(index, 2, get_formatted_date(data_dump_object.datetime))
            sheet.write(index, 3, data_dump_object.action_type)
            sheet.write(index, 4, data_dump_object.description)
            sheet.write(index, 5, data_dump_object.request_data_dump[:32767])
            sheet.write(index, 6, data_dump_object.api_end_point)
            sheet.write(index, 7, data_dump_object.ip_address)

            index += 1

        data_dump_wb.save(absolute_file_path)

        return relative_file_path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_custom_audit_trail_dump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'AuditTrailApp'})

        return "None"


def check_is_allincall_user(user):
    if user.username.endswith("@getcogno.ai") or user.username.endswith("@allincall.in"):
        return True
    else:
        return False
