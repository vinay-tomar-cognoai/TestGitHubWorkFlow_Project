from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect

# Django REST framework
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from EasyTMSApp.utils import *
from EasyTMSApp.models import *
from EasyChatApp.models import *
from EasyTMSApp.constants import *

import json
from django.conf import settings
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format

from django.db.models import Q, Count

import pytz
import uuid
import sys
from datetime import datetime, date, timedelta

from collections import OrderedDict

# Logger
import logging
logger = logging.getLogger(__name__)


class CardAnalyticsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            start_date = data["start_date"]
            end_date = data["end_date"]

            DEFAULT_ANALYTICS_START_DATETIME = (
                datetime.today() - timedelta(7)).date()

            DEFAULT_ANALYTICS_END_DATETIME = datetime.today().date()

            datetime_start = DEFAULT_ANALYTICS_START_DATETIME
            datetime_end = DEFAULT_ANALYTICS_END_DATETIME

            try:
                date_format = "%d/%m/%Y"
                datetime_start = datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception:
                pass

            active_agent = get_active_agent_obj(request, User, Agent)
            access_token = get_access_token_obj(
                active_agent, Agent, TMSAccessToken)

            ticket_objs = get_ticket_objs(
                active_agent, Agent, Ticket, TMSAccessToken, None)

            ticket_objs = ticket_objs.filter(
                issue_date_time__date__gte=datetime_start,
                issue_date_time__date__lte=datetime_end
            )

            analytics_data = {
                "TOTAL_TICKETS_GENERATED": ticket_objs.count()
            }

            ticket_status_objs = access_token.ticket_statuses.all()

            for ticket_status_obj in ticket_status_objs:
                analytics_data[ticket_status_obj.name] = ticket_objs.filter(
                    ticket_status=ticket_status_obj).count()

            response["status"] = 200
            response["message"] = "success"
            response["analytics_data"] = analytics_data
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CardAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CardAnalytics = CardAnalyticsAPI.as_view()


class ServiceRequestAnalyticsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            start_date = data["start_date"]
            end_date = data["end_date"]
            timeline = data["timeline"]

            DEFAULT_ANALYTICS_START_DATETIME = (
                datetime.today() - timedelta(7)).date()

            DEFAULT_ANALYTICS_END_DATETIME = datetime.today().date()

            datetime_start = DEFAULT_ANALYTICS_START_DATETIME
            datetime_end = DEFAULT_ANALYTICS_END_DATETIME

            try:
                date_format = "%d/%m/%Y"
                datetime_start = datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception:
                pass

            active_agent = get_active_agent_obj(request, User, Agent)
            access_token = get_access_token_obj(
                active_agent, Agent, TMSAccessToken)

            ticket_objs = get_ticket_objs(
                active_agent, Agent, Ticket, TMSAccessToken, None)

            ticket_objs = ticket_objs.filter(
                issue_date_time__date__gte=datetime_start,
                issue_date_time__date__lte=datetime_end
            )

            service_request_analytics = []
            if timeline == "daily":
                no_days = (datetime_end - datetime_start).days + 1
                for day in range(no_days):
                    temp_datetime = datetime_start + timedelta(day)

                    ticket_objs_tmp = ticket_objs.filter(
                        issue_date_time__date=temp_datetime)

                    analytics_data = {
                        "label": str(temp_datetime.strftime("%d-%b-%y")),
                        "TOTAL_TICKETS_GENERATED": ticket_objs_tmp.count()
                    }

                    ticket_status_objs = access_token.ticket_statuses.all()

                    for ticket_status_obj in ticket_status_objs:
                        analytics_data[ticket_status_obj.name] = ticket_objs_tmp.filter(
                            ticket_status=ticket_status_obj).count()

                    service_request_analytics.append(analytics_data)
            elif timeline == "weekly":
                no_days = (datetime_end - datetime_start).days
                no_weeks = int(no_days / 7.0) + 1

                for week in range(no_weeks):
                    temp_start_datetime = datetime_start + \
                        timedelta(week * 7)
                    temp_end_datetime = datetime_start + \
                        timedelta((week + 1) * 7)

                    ticket_objs_tmp = ticket_objs.filter(
                        issue_date_time__date__gte=temp_start_datetime, issue_date_time__date__lt=temp_end_datetime)

                    temp_start_datetime_str = temp_start_datetime.strftime(
                        "%d/%m")
                    temp_end_datetime_str = (
                        temp_end_datetime - timedelta(1)).strftime("%d/%m")

                    analytics_data = {
                        "label": temp_start_datetime_str + "-" + temp_end_datetime_str,
                        "TOTAL_TICKETS_GENERATED": ticket_objs_tmp.count()
                    }

                    ticket_status_objs = access_token.ticket_statuses.all()

                    for ticket_status_obj in ticket_status_objs:
                        analytics_data[ticket_status_obj.name] = ticket_objs_tmp.filter(
                            ticket_status=ticket_status_obj).count()

                    service_request_analytics.append(analytics_data)
            elif timeline == "monthly":
                month_list = list(OrderedDict(((datetime_start + timedelta(_)).strftime(
                    r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days)).keys())

                for month in month_list:
                    temp_month = month_to_num_dict[month.split("-")[0]]
                    temp_year = int(month.split("-")[1])
                    ticket_objs_tmp = ticket_objs.filter(
                        issue_date_time__date__month=temp_month, issue_date_time__date__year=temp_year)

                    analytics_data = {
                        "label": month,
                        "TOTAL_TICKETS_GENERATED": ticket_objs_tmp.count()
                    }

                    ticket_status_objs = access_token.ticket_statuses.all()

                    for ticket_status_obj in ticket_status_objs:
                        analytics_data[ticket_status_obj.name] = ticket_objs_tmp.filter(
                            ticket_status=ticket_status_obj).count()

                    service_request_analytics.append(analytics_data)
            else:
                logger.info("invalid timeline", extra={
                            'AppName': 'EasyAssist'})

            response["active_agent_role"] = active_agent.role
            response["service_request_analytics"] = service_request_analytics
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ServiceRequestAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ServiceRequestAnalytics = ServiceRequestAnalyticsAPI.as_view()


class ExportAnalyticsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {'status': 500, "export_path": "None", "export_path_exist": False}
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            email_id = data["email_id"]
            request_date_type = data['request_date_type']

            active_agent = get_active_agent_obj(request, User, Agent)
            export_path = None

            if request_date_type == "1":
                # Last day data
                export_path = get_custom_analytics_export(
                    get_requested_data_for_daily(), active_agent)

            elif request_date_type == "2":
                # Last 7 days data
                export_path = get_custom_analytics_export(
                    get_requested_data_for_week(), active_agent)

            elif request_date_type == "3":
                # Last 30 days data
                export_path = get_custom_analytics_export(
                    get_requested_data_for_month(), active_agent)

            elif request_date_type == "4":

                date_format = "%Y-%m-%d"
                start_date = datetime.strptime(
                    data['start_date'], date_format).date()
                end_date = datetime.strptime(
                    data["end_date"], date_format).date()

                today_date = datetime.today().date()

                if (today_date - start_date).days > 30:
                    ExportRequest.objects.create(
                        export_type='AnalyticsExport', agent=active_agent, start_date=start_date, end_date=end_date,
                        email_id=email_id)
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                else:
                    export_path = get_custom_analytics_export(
                        get_requested_data_custom(start_date, end_date), active_agent)

            if export_path and os.path.exists(export_path):
                response["export_path_exist"] = True
                file_access_management_obj = FileAccessManagement.objects.create(
                    file_path="/" + export_path)
                response["export_path"] = 'tms/download-file/' + \
                                          str(file_access_management_obj.key)
                response["status"] = 200

            response['status'] = 200
            response['message'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportAnalytics = ExportAnalyticsAPI.as_view()
