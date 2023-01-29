from http import server
import imp
from EasyAssistApp.utils import is_meeting_expired
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.shortcuts import render, HttpResponse
"""For user authentication"""
from django.contrib.auth import authenticate, login, logout
from CognoMeetApp.encrypt import CustomEncrypt
from CognoMeetApp.html_parser import strip_html_tags

from CognoMeetApp.models import *
from EasyChatApp.models import User
from django.conf import settings
from CognoMeetApp.utils_validation import remo_html_from_string, check_malicious_file_from_filename, check_malicious_file_from_content, remo_special_tag_from_string, sanitize_input_string
from CognoMeetApp.constants import *
from CognoMeetApp.utils import *

import os
import sys
import logging
import json
import base64
import time
import re
import uuid
import pytz
import datetime
from collections import OrderedDict


logger = logging.getLogger(__name__)


class GetBasicAnalyticsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            start_date = sanitize_input_string(data["start_date"])
            end_date = sanitize_input_string(data["end_date"])
            agents_usernames_list = data["agents_usernames_list"]
            cognomeet_access_token = sanitize_input_string(
                data["cognomeet_access_token"])
            total_meeting_scheduled_count = 0
            total_meeting_completed_count = 0
            total_ongoing_meetings_count = 0
            average_call_duration_in_min = 0

            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                cognomeet_access_token, CognoMeetAccessToken)

            if not cognomeet_access_token_obj:
                return Response(data=get_invalid_access_token_response(custom_encrypt_obj, json))

            cognomeet_agents_objs = CognoMeetAgent.objects.filter(
                user__username__in=agents_usernames_list)

            time_zone = pytz.timezone(settings.TIME_ZONE)

            start_date = datetime.datetime.strptime(
                start_date, "%d/%m/%Y").date()
            end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y").date()

            cognomeet_io_objs = CognoMeetIO.objects.filter(cogno_meet_access_token=cognomeet_access_token_obj, cogno_meet_agent__in=cognomeet_agents_objs,
                                                           meeting_start_date__gte=start_date, meeting_start_date__lte=end_date)

            total_meeting_scheduled_count = cognomeet_io_objs.count()

            completed_meeting_objs = cognomeet_io_objs.filter(
                is_meeting_expired=True)
            total_meeting_completed_count = completed_meeting_objs.count()
            total_meeting_time = 0
            audit_trail_objs = CognoMeetAuditTrail.objects.filter(
                cogno_meet_io__in=completed_meeting_objs)
            for audit_trail_obj in audit_trail_objs:
                total_meeting_time += audit_trail_obj.total_call_duration

            average_call_duration_in_min = 0
            if total_meeting_completed_count:
                average_call_duration_in_sec = total_meeting_time / total_meeting_completed_count
                average_call_duration_in_min = round(
                    average_call_duration_in_sec / 60)

            current_date = timezone.now().astimezone(time_zone).date()
            current_time = timezone.now().astimezone(time_zone).time()
            # TODO this count can be shown by either time intersection or by checking if audit trail objs for meet has been created or not
            ongoing_meeting_objs = cognomeet_io_objs.filter(
                meeting_start_date=current_date, meeting_start_time__lte=current_time, is_meeting_expired=False)
            total_ongoing_meetings_count = CognoMeetAuditTrail.objects.filter(
                cogno_meet_io__in=ongoing_meeting_objs).count()

            response["status"] = 200
            response["message"] = "success"
            response["total_meeting_scheduled_count"] = total_meeting_scheduled_count
            response["total_meeting_completed_count"] = total_meeting_completed_count
            response["total_ongoing_meetings_count"] = total_ongoing_meetings_count
            response["average_call_duration_in_min"] = average_call_duration_in_min

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetBasicAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetBasicAnalytics = GetBasicAnalyticsAPI.as_view()


class GetTimelineBasedAnalyticsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            start_date = sanitize_input_string(data["start_date"])
            end_date = sanitize_input_string(data["end_date"])
            cognomeet_access_token = sanitize_input_string(
                data["cognomeet_access_token"])
            agent_usernames_list = data["agents_usernames_list"]
            timeline = sanitize_input_string(data["timeline"])

            DEFAULT_ANALYTICS_START_DATETIME = (
                datetime.datetime.today() - datetime.timedelta(7)).date()

            DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

            try:
                date_format = "%d/%m/%Y"
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(
                    end_date, date_format).date()
            except Exception:
                datetime_start = DEFAULT_ANALYTICS_START_DATETIME
                datetime_end = DEFAULT_ANALYTICS_END_DATETIME

            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                cognomeet_access_token, CognoMeetAccessToken)

            if not cognomeet_access_token_obj:
                return Response(data=get_invalid_access_token_response(custom_encrypt_obj, json))

            cognomeet_agents_objs = CognoMeetAgent.objects.filter(
                user__username__in=agent_usernames_list)

            time_zone = pytz.timezone(settings.TIME_ZONE)

            cognomeet_io_objs = CognoMeetIO.objects.filter(cogno_meet_access_token=cognomeet_access_token_obj, cogno_meet_agent__in=cognomeet_agents_objs,
                                                           meeting_start_date__gte=datetime_start, meeting_start_date__lte=datetime_end)

            timeline_based_analytics = []

            if timeline == "daily":
                no_days = (datetime_end - datetime_start).days + 1
                for day in range(no_days):
                    temp_datetime = datetime_start + datetime.timedelta(day)

                    date_filtered_cognomeet_io_objs = cognomeet_io_objs.filter(
                        meeting_start_date=temp_datetime)

                    total_meeting_scheduled = date_filtered_cognomeet_io_objs.count()
                    total_meeting_completed = date_filtered_cognomeet_io_objs.filter(
                        is_meeting_expired=True).count()

                    current_time = timezone.now().astimezone(time_zone).time()
                    # TODO this count can be shown by either time intersection or by checking if audit trail objs for meet has been created or not
                    ongoing_meeting_objs = date_filtered_cognomeet_io_objs.filter(
                        meeting_start_time__lte=current_time, is_meeting_expired=False)
                    total_ongoing_meeting = 0
                    if ongoing_meeting_objs:
                        total_ongoing_meeting = CognoMeetAuditTrail.objects.filter(
                            cogno_meet_io__in=ongoing_meeting_objs).count()

                    timeline_based_analytics.append({
                        "label": str(temp_datetime.strftime("%d-%b-%y")),
                        "total_meeting_scheduled": total_meeting_scheduled,
                        "total_meeting_completed": total_meeting_completed,
                        "total_ongoing_meeting": total_ongoing_meeting,
                    })

            elif timeline == "weekly":
                no_days = (datetime_end - datetime_start).days
                no_weeks = int(no_days / 7.0) + 1

                for week in range(no_weeks):
                    temp_start_datetime = datetime_start + \
                        datetime.timedelta(week * 7)
                    temp_end_datetime = datetime_start + \
                        datetime.timedelta((week + 1) * 7)

                    date_filtered_cognomeet_io_objs = cognomeet_io_objs.filter(
                        meeting_start_date__gte=temp_start_datetime, meeting_start_date__lte=temp_end_datetime)

                    total_meeting_scheduled = date_filtered_cognomeet_io_objs.count()
                    total_meeting_completed = date_filtered_cognomeet_io_objs.filter(
                        is_meeting_expired=True).count()

                    current_time = timezone.now().astimezone(time_zone).time()
                    # TODO this count can be shown by either time intersection or by checking if audit trail objs for meet has been created or not
                    ongoing_meeting_objs = date_filtered_cognomeet_io_objs.filter(
                        meeting_start_time__lte=current_time, is_meeting_expired=False)
                    total_ongoing_meeting = 0
                    if ongoing_meeting_objs:
                        total_ongoing_meeting = CognoMeetAuditTrail.objects.filter(
                            cogno_meet_io__in=ongoing_meeting_objs).count()

                    temp_start_datetime_str = temp_start_datetime.strftime(
                        "%d/%m")
                    temp_end_datetime_str = (
                        temp_end_datetime - datetime.timedelta(1)).strftime("%d/%m")

                    timeline_based_analytics.append({
                        "label": temp_start_datetime_str + "-" + temp_end_datetime_str,
                        "start_date": str(temp_start_datetime),
                        "end_date": str(temp_end_datetime - datetime.timedelta(1)),
                        "total_meeting_scheduled": total_meeting_scheduled,
                        "total_meeting_completed": total_meeting_completed,
                        "total_ongoing_meeting": total_ongoing_meeting,
                    })

            elif timeline == "monthly":
                month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
                    r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days)).keys())

                for month in month_list:
                    temp_month = month_to_num_dict[month.split("-")[0]]
                    temp_year = int(month.split("-")[1])

                    date_filtered_cognomeet_io_objs = cognomeet_io_objs.filter(
                        meeting_start_date__month=temp_month, meeting_start_date__year=temp_year)

                    total_meeting_scheduled = date_filtered_cognomeet_io_objs.count()
                    total_meeting_completed = date_filtered_cognomeet_io_objs.filter(
                        is_meeting_expired=True).count()

                    current_time = timezone.now().astimezone(time_zone).time()
                    # TODO this count can be shown by either time intersection or by checking if audit trail objs for meet has been created or not
                    ongoing_meeting_objs = date_filtered_cognomeet_io_objs.filter(
                        meeting_start_time__lte=current_time, is_meeting_expired=False)
                    total_ongoing_meeting = 0
                    if ongoing_meeting_objs:
                        total_ongoing_meeting = CognoMeetAuditTrail.objects.filter(
                            cogno_meet_io__in=ongoing_meeting_objs).count()

                    timeline_based_analytics.append({
                        "label": month,
                        "total_meeting_scheduled": total_meeting_scheduled,
                        "total_meeting_completed": total_meeting_completed,
                        "total_ongoing_meeting": total_ongoing_meeting,
                    })

            response["status"] = 200
            response["timeline_based_analytics"] = timeline_based_analytics

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetTimelineBasedAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetTimelineBasedAnalytics = GetTimelineBasedAnalyticsAPI.as_view()


class GetDailyCallTimeTrendAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            agents_usernames_list = data["agents_usernames_list"]
            cognomeet_access_token = sanitize_input_string(
                data["cognomeet_access_token"])

            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                cognomeet_access_token, CognoMeetAccessToken)

            if not cognomeet_access_token_obj:
                return Response(data=get_invalid_access_token_response(custom_encrypt_obj, json))

            cognomeet_agents_objs = CognoMeetAgent.objects.filter(
                user__username__in=agents_usernames_list)

            today_date = datetime.datetime.today()
            start_time = datetime.datetime(
                today_date.year, today_date.month, today_date.day)
            end_time = start_time + datetime.timedelta(hours=1)
            today_date = today_date.date()

            cognomeet_io_objs = CognoMeetIO.objects.filter(cogno_meet_access_token=cognomeet_access_token_obj, cogno_meet_agent__in=cognomeet_agents_objs,
                                                           meeting_start_date=today_date, is_meeting_expired=True)

            daily_time_trend = []

            time_zone = pytz.timezone(settings.TIME_ZONE)
            current_hour = datetime.datetime.now().astimezone(time_zone).hour
            for hour in range(current_hour + 1):
                total_meetings_count = cognomeet_io_objs.filter(
                    meeting_start_time__gte=start_time.time(), meeting_start_time__lte=end_time.time()).count()

                daily_time_trend.append({
                    "label": str(start_time.strftime("%-I %p")) + "-" + str(end_time.strftime("%-I %p")),
                    "total_meetings_count": total_meetings_count,
                })

                start_time = end_time
                end_time = end_time + datetime.timedelta(hours=1)

            response["daily_time_trend"] = daily_time_trend
            response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetDailyCallTimeTrendAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetDailyCallTimeTrend = GetDailyCallTimeTrendAPI.as_view()


class GetAgentWiseAnalyticsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            start_date = sanitize_input_string(data["start_date"])
            end_date = sanitize_input_string(data["end_date"])
            agent_key = sanitize_input_string(data["agent_key"])
            cognomeet_access_token = sanitize_input_string(
                data["cognomeet_access_token"])
            timeline = sanitize_input_string(data["timeline"])

            DEFAULT_ANALYTICS_START_DATETIME = (
                datetime.datetime.today() - datetime.timedelta(7)).date()

            DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

            try:
                date_format = "%d/%m/%Y"
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(
                    end_date, date_format).date()
            except Exception:
                datetime_start = DEFAULT_ANALYTICS_START_DATETIME
                datetime_end = DEFAULT_ANALYTICS_END_DATETIME

            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                cognomeet_access_token, CognoMeetAccessToken)

            if not cognomeet_access_token_obj:
                return Response(data=get_invalid_access_token_response(custom_encrypt_obj, json))

            cognomeet_agent_obj = CognoMeetAgent.objects.filter(
                user__pk=agent_key).first()

            cognomeet_io_objs = CognoMeetIO.objects.filter(cogno_meet_access_token=cognomeet_access_token_obj, cogno_meet_agent=cognomeet_agent_obj,
                                                            meeting_start_date__gte=datetime_start, meeting_start_date__lte=datetime_end)

            timeline_based_analytics = []

            if timeline == "daily":
                no_days = (datetime_end - datetime_start).days + 1
                for day in range(no_days):
                    temp_datetime = datetime_start + \
                        datetime.timedelta(day)

                    date_filtered_cognomeet_io_objs = cognomeet_io_objs.filter(
                        meeting_start_date=temp_datetime)

                    total_meeting_scheduled = date_filtered_cognomeet_io_objs.count()
                    total_meeting_completed = date_filtered_cognomeet_io_objs.filter(
                        is_meeting_expired=True).count()

                    timeline_based_analytics.append({
                        "label": str(temp_datetime.strftime("%d-%b-%y")),
                        "total_meeting_scheduled": total_meeting_scheduled,
                        "total_meeting_completed": total_meeting_completed
                    })

            elif timeline == "weekly":
                no_days = (datetime_end - datetime_start).days
                no_weeks = int(no_days / 7.0) + 1

                for week in range(no_weeks):
                    temp_start_datetime = datetime_start + \
                        datetime.timedelta(week * 7)
                    temp_end_datetime = datetime_start + \
                        datetime.timedelta((week + 1) * 7)

                    date_filtered_cognomeet_io_objs = cognomeet_io_objs.filter(
                        meeting_start_date__gte=temp_start_datetime, meeting_start_date__lte=temp_end_datetime)

                    total_meeting_scheduled = date_filtered_cognomeet_io_objs.count()
                    total_meeting_completed = date_filtered_cognomeet_io_objs.filter(
                        is_meeting_expired=True).count()

                    temp_start_datetime_str = temp_start_datetime.strftime(
                        "%d/%m")
                    temp_end_datetime_str = (
                        temp_end_datetime - datetime.timedelta(1)).strftime("%d/%m")

                    timeline_based_analytics.append({
                        "label": temp_start_datetime_str + "-" + temp_end_datetime_str,
                        "start_date": str(temp_start_datetime),
                        "end_date": str(temp_end_datetime - datetime.timedelta(1)),
                        "total_meeting_scheduled": total_meeting_scheduled,
                        "total_meeting_completed": total_meeting_completed
                    })

            elif timeline == "monthly":
                month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
                    r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days)).keys())

                for month in month_list:
                    temp_month = month_to_num_dict[month.split("-")[0]]
                    temp_year = int(month.split("-")[1])

                    date_filtered_cognomeet_io_objs = cognomeet_io_objs.filter(
                        meeting_start_date__month=temp_month, meeting_start_date__year=temp_year)

                    total_meeting_scheduled = date_filtered_cognomeet_io_objs.count()
                    total_meeting_completed = date_filtered_cognomeet_io_objs.filter(
                        is_meeting_expired=True).count()

                    timeline_based_analytics.append({
                        "label": month,
                        "total_meeting_scheduled": total_meeting_scheduled,
                        "total_meeting_completed": total_meeting_completed
                    })

            response["status"] = 200
            response["timeline_based_analytics"] = timeline_based_analytics

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentWiseAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentWiseAnalytics = GetAgentWiseAnalyticsAPI.as_view()


class ExportMeetingAnalyticsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cognomeet_access_token = sanitize_input_string(
                data["cognomeet_access_token"])
            cognomeet_access_token_obj = get_cognomeet_access_token_obj(
                cognomeet_access_token, CognoMeetAccessToken)

            if not cognomeet_access_token_obj:
                return Response(data=get_invalid_access_token_response(custom_encrypt_obj, json))
            
            cogno_meet_agent = get_cognomeet_agent_from_request(request, CognoMeetAgent)
            if cogno_meet_agent.role == "agent":
                response["export_path"] = "None"
                response["status"] = 401
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            data["cogno_meet_agent_username"] = cogno_meet_agent.user.username
            is_custom_date_range_requirement = False
            agents_usernames_list = data["agents_usernames_list"]
            start_date = sanitize_input_string(data["start_date"])
            end_date = sanitize_input_string(data["end_date"])
            selected_filter_value = sanitize_input_string(
                data["selected_filter_value"])

            if selected_filter_value == "1":
                requested_data_date_range = get_requested_data_for_daily()

            elif selected_filter_value == "2":
                requested_data_date_range = get_requested_data_for_week()

            elif selected_filter_value == "3":
                requested_data_date_range = get_requested_data_for_month()

            elif selected_filter_value == "4":
                is_custom_date_range_requirement = True
                requested_data_date_range = {
                    "startdate": start_date,
                    "enddate": end_date,
                }

            export_path = None
            start_date = requested_data_date_range["startdate"]
            end_date = requested_data_date_range["enddate"]

            cogno_meet_agent_list = CognoMeetAgent.objects.filter(
                user__username__in=agents_usernames_list)
            cognomeet_io_objs = CognoMeetIO.objects.filter(
                cogno_meet_agent__in=cogno_meet_agent_list, meeting_start_date__gte=start_date, meeting_start_date__lte=end_date, is_meeting_expired=True)

            audit_trail_objs = CognoMeetAuditTrail.objects.filter(
                cogno_meet_io__in=cognomeet_io_objs)

            if audit_trail_objs.count() > REPORT_GENERATION_CAP:
                create_export_data_request_obj(
                    cogno_meet_agent, "meeting-analytics", json.dumps(data), CognoMeetExportDataRequest)
                response["status"] = 301
                if is_custom_date_range_requirement:
                    response["message"] = "The requested report would be sent to the entered email IDs within the next 1 hour."
                else:
                    response["message"] = "Your requested report would be sent to you over your email ID in the next 1 hour."
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)
            else:
                export_path = get_custom_meeting_analytics(
                    cognomeet_access_token_obj, requested_data_date_range, cogno_meet_agent, CognoMeetIO, CognoMeetAuditTrail, CognoMeetFileAccessManagement, CognoMeetAgent, agents_usernames_list)

            if export_path and os.path.exists(export_path):

                response["export_path_exist"] = True
                file_path = "/" + export_path

                file_access_management_key = create_file_access_management_obj(
                    CognoMeetFileAccessManagement, cognomeet_access_token_obj, file_path)
                response["export_path"] = 'cogno-meet/download-file/' + \
                    file_access_management_key
            
            response["status"] = 200
            response["message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportMeetingAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportMeetingAnalytics = ExportMeetingAnalyticsAPI.as_view()
