from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.utils.encoding import smart_str
from django.db.models import Sum

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
"""For user authentication"""
from django.contrib.auth import authenticate, login, logout
# Create your views here.
from EasyChatApp.models import User
from EasyAssistApp.models import *
from EasyAssistApp.utils import *
from EasyAssistApp.views_table import *
from EasyAssistApp.send_email import send_password_over_email
from DeveloperConsoleApp.utils import *
from DeveloperConsoleApp.utils_aws_s3 import *

import sys
import pytz
import time
import json
import base64
import operator
import logging
import hashlib
import requests
import datetime
import random
import urllib.parse
import threading

from operator import itemgetter
from collections import OrderedDict

logger = logging.getLogger(__name__)


class GetReverseCobrowseBasicAnalyticsAPI(APIView):

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
            start_date = remo_html_from_string(start_date)
            end_date = data["end_date"]
            end_date = remo_html_from_string(end_date)

            title = None
            if "title" in data and data["title"] != "all":
                title = data["title"]
                title = remo_html_from_string(title)

            DEFAULT_ANALYTICS_START_DATETIME = (
                datetime.datetime.today() - datetime.timedelta(7)).date()

            DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

            datetime_start = DEFAULT_ANALYTICS_START_DATETIME
            datetime_end = DEFAULT_ANALYTICS_END_DATETIME
            try:
                date_format = "%d/%m/%Y"
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception:
                pass

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            total_sr = 0
            total_sr_closed = 0
            total_sr_closed_by_url = 0
            total_sr_attended = 0
            cobrowse_io_objs = None
            avg_session_duration = 0
            unique_customers = 0
            repeated_customers = 0

            agent_objs = [active_agent]

            if active_agent.role in ["admin", "admin_ally"]:
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=True).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False, agent__in=agent_objs)

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            nps = 0
            if cobrowse_io_objs != None:
                total_sr = cobrowse_io_objs.count()

                total_sr_closed = cobrowse_io_objs.filter(
                    is_helpful=True, is_archived=True, is_lead_converted_by_url=False).filter(~Q(cobrowsing_start_datetime=None)).count()

                total_sr_closed_by_url = cobrowse_io_objs.filter(
                    is_helpful=True, is_archived=True, is_lead_converted_by_url=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                total_sr_attended = cobrowse_io_objs.filter(
                    ~Q(cobrowsing_start_datetime=None)).count()

                customers_details = cobrowse_io_objs.values("mobile_number").annotate(customer_count=Count('mobile_number')) 
                unique_customers = customers_details.filter(customer_count__lte=1).count()
                repeated_customers = customers_details.filter(customer_count__gt=1).count()
                
                total_sr_nps = cobrowse_io_objs.filter(
                    is_archived=True).filter(~Q(agent_rating=None)).filter(~Q(cobrowsing_start_datetime=None)).count()

                if total_sr_nps != 0:
                    promoter_count = cobrowse_io_objs.filter(
                        is_archived=True, agent_rating__gte=9).filter(~Q(cobrowsing_start_datetime=None)).count()
                    detractor_count = cobrowse_io_objs.filter(
                        is_archived=True, agent_rating__lte=6).filter(~Q(cobrowsing_start_datetime=None)).count()
                    nps = ((promoter_count - detractor_count) * 100) / total_sr_nps
                    nps = round(nps, 2)

                cobrowse_io_initiated = cobrowse_io_objs.filter(
                    ~Q(cobrowsing_start_datetime=None))

                for cobrowse_io in cobrowse_io_initiated:
                    avg_session_duration += cobrowse_io.session_time_in_seconds()

                try:
                    avg_session_duration = avg_session_duration / (
                        total_sr_attended * 60)
                except Exception:
                    logger.warning("divide by zero", extra={
                        'AppName': 'EasyAssist'})

            response["total_sr"] = total_sr
            response["total_sr_closed"] = total_sr_closed
            response["total_sr_closed_by_url"] = total_sr_closed_by_url
            response["total_sr_attended"] = total_sr_attended
            response["nps"] = nps
            response["avg_session_duration"] = avg_session_duration
            response["unique_customers"] = unique_customers
            response["repeated_customers"] = repeated_customers
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetReverseCobrowseBasicAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetReverseCobrowseBasicAnalytics = GetReverseCobrowseBasicAnalyticsAPI.as_view()


class GetAgentCobrowseRequestAnalyticsAPI(APIView):

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
            start_date = remo_html_from_string(start_date)
            end_date = data["end_date"]
            end_date = remo_html_from_string(end_date)
            timeline = data["timeline"]

            title = None
            if "title" in data and data["title"] != "all":
                title = data["title"]
                title = remo_html_from_string(title)

            DEFAULT_ANALYTICS_START_DATETIME = (
                datetime.datetime.today() - datetime.timedelta(7)).date()

            DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

            datetime_start = DEFAULT_ANALYTICS_START_DATETIME
            datetime_end = DEFAULT_ANALYTICS_END_DATETIME
            try:
                date_format = "%d/%m/%Y"
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception:
                logger.error(
                    "Invalid start and end date. Select default start and end date:", extra={'AppName': 'EasyAssist'})

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = None

            agent_objs = [active_agent]

            if active_agent.role in ["admin", "admin_ally"]:
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=True).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False, agent__in=agent_objs)

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            cobrowse_request_analytics = []
            if timeline == "daily":
                no_days = (datetime_end - datetime_start).days + 1
                for day in range(no_days):
                    temp_datetime = datetime_start + datetime.timedelta(day)

                    date_filtered_cobrowse_io_objs = cobrowse_io_objs.filter(
                        request_datetime__date=temp_datetime)

                    # total cobrowsing request Initiated/Notinitiated
                    total_sr = date_filtered_cobrowse_io_objs.count()

                    # total cobrowsing request initiated and converted
                    # successfully
                    total_sr_closed = date_filtered_cobrowse_io_objs.filter(
                        is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                    # total cobrowsing request attended
                    total_sr_attended = date_filtered_cobrowse_io_objs.filter(
                        ~Q(cobrowsing_start_datetime=None)).count()

                    cobrowse_request_analytics.append({
                        "label": str(temp_datetime.strftime("%d-%b-%y")),
                        "total_sr": total_sr,
                        "total_sr_closed": total_sr_closed,
                        "total_sr_attended": total_sr_attended,
                    })
            elif timeline == "weekly":
                no_days = (datetime_end - datetime_start).days
                no_weeks = int(no_days / 7.0) + 1

                for week in range(no_weeks):
                    temp_start_datetime = datetime_start + \
                        datetime.timedelta(week * 7)
                    temp_end_datetime = datetime_start + \
                        datetime.timedelta((week + 1) * 7)

                    date_filtered_cobrowse_io_objs = cobrowse_io_objs.filter(
                        request_datetime__date__gte=temp_start_datetime, request_datetime__date__lt=temp_end_datetime)

                    total_sr = date_filtered_cobrowse_io_objs.count()
                    total_sr_closed = date_filtered_cobrowse_io_objs.filter(
                        is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()
                    total_sr_attended = date_filtered_cobrowse_io_objs.filter(
                        ~Q(cobrowsing_start_datetime=None)).count()

                    temp_start_datetime_str = temp_start_datetime.strftime(
                        "%d/%m")
                    temp_end_datetime_str = (
                        temp_end_datetime - datetime.timedelta(1)).strftime("%d/%m")

                    cobrowse_request_analytics.append({
                        "label": temp_start_datetime_str + "-" + temp_end_datetime_str,
                        "total_sr": total_sr,
                        "total_sr_closed": total_sr_closed,
                        "total_sr_attended": total_sr_attended,
                        "start_date": str(temp_start_datetime),
                        "end_date": str(temp_end_datetime - datetime.timedelta(1)),
                    })
            elif timeline == "monthly":
                month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
                    r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days)).keys())

                for month in month_list:
                    temp_month = month_to_num_dict[month.split("-")[0]]
                    temp_year = int(month.split("-")[1])
                    date_filtered_cobrowse_io_objs = cobrowse_io_objs.filter(
                        request_datetime__date__month=temp_month, request_datetime__date__year=temp_year)

                    total_sr = date_filtered_cobrowse_io_objs.count()
                    total_sr_closed = date_filtered_cobrowse_io_objs.filter(
                        is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()
                    total_sr_attended = date_filtered_cobrowse_io_objs.filter(
                        ~Q(cobrowsing_start_datetime=None)).count()

                    cobrowse_request_analytics.append({
                        "label": month,
                        "total_sr": total_sr,
                        "total_sr_closed": total_sr_closed,
                        "total_sr_attended": total_sr_attended,
                    })
            else:
                logger.info("invalid timeline", extra={
                            'AppName': 'EasyAssist'})

            response["active_agent_role"] = active_agent.role
            response["cobrowse_request_analytics"] = cobrowse_request_analytics
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentCobrowseRequestAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentCobrowseRequestAnalytics = GetAgentCobrowseRequestAnalyticsAPI.as_view()


class GetAgentWiseRequestAnalyticsReverseAPI(APIView):

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
            start_date = remo_html_from_string(start_date)
            end_date = data["end_date"]
            end_date = remo_html_from_string(end_date)

            title = None
            if "title" in data and data["title"] != "all":
                title = data["title"]
                title = remo_html_from_string(title)

            DEFAULT_ANALYTICS_START_DATETIME = (
                datetime.datetime.today() - datetime.timedelta(7)).date()

            DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

            datetime_start = DEFAULT_ANALYTICS_START_DATETIME
            datetime_end = DEFAULT_ANALYTICS_END_DATETIME
            try:
                date_format = "%d/%m/%Y"
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception:
                pass

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=True).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False)

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            agent_request_analytics_list, agent_objs = [], []
            agent_objs = []

            if active_agent.role in ["admin", "admin_ally"]:
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())
            else:
                logger.info("Invalid User Access", extra={
                            'AppName': 'EasyAssist'})

            for agent in agent_objs:
                total_sr = cobrowse_io_objs.filter(agent=agent).count()

                total_sr_closed = cobrowse_io_objs.filter(
                    agent=agent, is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                total_sr_attended = cobrowse_io_objs.filter(
                    agent=agent).filter(~Q(cobrowsing_start_datetime=None)).count()

                if access_token_obj.enable_invite_agent_in_cobrowsing:
                    filtered_agent_wise_cobrowse_io = cobrowse_io_objs.filter(
                        agent=agent)
                    group_cobrowse_request_initiated = CobrowseIOInvitedAgentsDetails.objects.filter(
                        cobrowse_io__in=filtered_agent_wise_cobrowse_io).count()
                    group_cobrowse_request_received = CobrowseIOInvitedAgentsDetails.objects.filter(
                        cobrowse_io__in=cobrowse_io_objs, support_agents_invited__in=[agent]).count()
                    group_cobrowse_request_connected = CobrowseIOInvitedAgentsDetails.objects.filter(
                        cobrowse_io__in=cobrowse_io_objs, support_agents_joined__in=[agent]).count()

                if access_token_obj.enable_invite_agent_in_cobrowsing:
                    agent_request_analytics_list.append({
                        "agent": agent.user.username,
                        "total_sr": total_sr,
                        "total_sr_closed": total_sr_closed,
                        "total_sr_attended": total_sr_attended,
                        "group_cobrowse_request_initiated": group_cobrowse_request_initiated,
                        "group_cobrowse_request_received": group_cobrowse_request_received,
                        "group_cobrowse_request_connected": group_cobrowse_request_connected,
                    })
                else:
                    agent_request_analytics_list.append({
                        "agent": agent.user.username,
                        "total_sr": total_sr,
                        "total_sr_closed": total_sr_closed,
                        "total_sr_attended": total_sr_attended,
                    })

            if access_token_obj.enable_invite_agent_in_cobrowsing:
                agent_request_analytics_list.sort(key=lambda data: (
                    data['total_sr'],
                    data['total_sr_attended'],
                    data['total_sr_closed'],
                    data['group_cobrowse_request_initiated'],
                    data['group_cobrowse_request_received'],
                    data['group_cobrowse_request_connected'],
                ), reverse=True)
            else:
                agent_request_analytics_list.sort(key=lambda data: (
                    data['total_sr'],
                    data['total_sr_attended'],
                    data['total_sr_closed'],
                ), reverse=True)

            response["status"] = 200
            response["message"] = "success"
            response["agent_request_analytics_list"] = agent_request_analytics_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentWiseRequestAnalyticsReverseAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentWiseRequestAnalyticsReverse = GetAgentWiseRequestAnalyticsReverseAPI.as_view()


class GetAgentNPSAnalyticsReverseAPI(APIView):

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
            start_date = remo_html_from_string(start_date)
            end_date = data["end_date"]
            end_date = remo_html_from_string(end_date)
            page = data["page"]

            title = None
            if "title" in data and data["title"] != "all":
                title = data["title"]
                title = remo_html_from_string(title)

            DEFAULT_ANALYTICS_START_DATETIME = (
                datetime.datetime.today() - datetime.timedelta(7)).date()

            DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

            datetime_start = DEFAULT_ANALYTICS_START_DATETIME
            datetime_end = DEFAULT_ANALYTICS_END_DATETIME
            try:
                date_format = "%d/%m/%Y"
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception:
                pass

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=True).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False).filter(
                ~Q(cobrowsing_start_datetime=None))

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            agent_nps_analytics_list, agent_objs = [], []

            if active_agent.role in ["admin", "admin_ally"]:
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())
            else:
                logger.info("Invalid User Access", extra={
                            'AppName': 'EasyAssist'})

            for agent in agent_objs:
                nps = None
                total_sr_closed = cobrowse_io_objs.filter(
                    is_archived=True, agent=agent).filter(~Q(agent_rating=None)).count()
                if total_sr_closed != 0:
                    promoter_count = cobrowse_io_objs.filter(
                        is_archived=True, agent_rating__gte=9, agent=agent).count()
                    detractor_count = cobrowse_io_objs.filter(
                        is_archived=True, agent_rating__lte=6, agent=agent).count()
                    nps = ((promoter_count - detractor_count) * 100) / total_sr_closed
                    nps = round(nps, 2)

                if nps == None:
                    continue

                agent_nps_analytics_list.append({
                    "agent": agent.user.username,
                    "nps": nps
                })

            paginator = Paginator(agent_nps_analytics_list, 5)
            no_pages = paginator.num_pages

            is_last_page = False
            if int(page) >= int(no_pages):
                is_last_page = True

            try:
                agent_nps_analytics_list = paginator.page(page)
            except PageNotAnInteger:
                agent_nps_analytics_list = paginator.page(1)
            except EmptyPage:
                agent_nps_analytics_list = paginator.page(paginator.num_pages)

            response["status"] = 200
            response["message"] = "success"
            response["agent_nps_analytics_list"] = list(
                agent_nps_analytics_list)
            response["is_last_page"] = is_last_page
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentNPSAnalyticsReverseAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentNPSAnalyticsReverse = GetAgentNPSAnalyticsReverseAPI.as_view()


class GetQueryPageAnalyticsReverseAPI(APIView):

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
            start_date = remo_html_from_string(start_date)
            end_date = data["end_date"]
            end_date = remo_html_from_string(end_date)
            page = data["page"]

            title = None
            if "title" in data and data["title"] != "all":
                title = data["title"]
                title = remo_html_from_string(title)

            DEFAULT_ANALYTICS_START_DATETIME = (
                datetime.datetime.today() - datetime.timedelta(7)).date()

            DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

            datetime_start = DEFAULT_ANALYTICS_START_DATETIME
            datetime_end = DEFAULT_ANALYTICS_END_DATETIME
            try:
                date_format = "%d/%m/%Y"
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(end_date, date_format).date()  # noqa: F841
            except Exception:
                pass

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=True).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False).filter(
                ~Q(cobrowsing_start_datetime=None))

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            query_pages = []

            if active_agent.role in ["admin", "supervisor", "admin_ally"]:

                query_pages = list(cobrowse_io_objs.values('active_url', 'title').annotate(
                    total=Count('active_url')).order_by("-total"))

                paginator = Paginator(query_pages, 5)
                no_pages = paginator.num_pages

                is_last_page = False
                if int(page) >= int(no_pages):
                    is_last_page = True

                try:
                    query_pages = paginator.page(page)
                except PageNotAnInteger:
                    query_pages = paginator.page(1)
                except EmptyPage:
                    query_pages = paginator.page(paginator.num_pages)

                response["status"] = 200
                response["message"] = "success"
                response["total_pages"] = cobrowse_io_objs.count()
                response["query_pages"] = list(query_pages)
                response["is_last_page"] = is_last_page
            else:
                response["status"] = 401
                response["message"] = "Unauthorized access"
                response["query_pages"] = query_pages

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetQueryPageAnalyticsReverseAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetQueryPageAnalyticsReverse = GetQueryPageAnalyticsReverseAPI.as_view()


class GetVisitedPageTitleListAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True).filter(
                is_lead=False).filter(
                ~Q(title=None)).filter(
                ~Q(cobrowsing_start_datetime=None))

            query_pages = list(
                set(list(cobrowse_io_objs.values_list('title', flat=True))))

            response["status"] = 200
            response["message"] = "success"
            response["query_pages"] = query_pages
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RequestCobrowsingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetVisitedPageTitleList = GetVisitedPageTitleListAPI.as_view()


class ExportReverseAnalyticsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response["export_path"] = "None"
        response["export_path_exist"] = False
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            requested_data = json.loads(data)

            user = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(
                user=user, is_account_active=True)

            if cobrowse_agent.role == "agent":
                response["export_path"] = "None"
                response["status"] = 401
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            date_format = "%Y-%m-%d"

            if requested_data["selected_filter_value"] == "1":
                # Last day data
                start_date = datetime.datetime.now() - datetime.timedelta(days=1)
                start_date = start_date.strftime(date_format)
                end_date = start_date

                export_path = "/secured_files/EasyAssistApp/ReverseAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/reverse_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "2":
                # Last 7 days data
                start_date = datetime.datetime.now() - datetime.timedelta(days=7)
                start_date = start_date.strftime(date_format)
                end_date = datetime.datetime.now() - datetime.timedelta(days=1)
                end_date = end_date.strftime(date_format)

                export_path = "/secured_files/EasyAssistApp/ReverseAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/reverse_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "3":
                # Last 30 days data
                start_date = datetime.datetime.now() - datetime.timedelta(days=30)
                start_date = start_date.strftime(date_format)
                end_date = datetime.datetime.now() - datetime.timedelta(days=1)
                end_date = end_date.strftime(date_format)

                export_path = "/secured_files/EasyAssistApp/ReverseAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/reverse_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "4":

                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()

                today_date = datetime.datetime.today().date()

                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='reverse-analytics', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                else:
                    export_path = get_reverse_analytics_data_dump(
                        requested_data, cobrowse_agent, CobrowseDateWiseReverseAnalytics)

            if os.path.exists(export_path[1:]) == True:
                if get_save_in_s3_bucket_status():
                    if requested_data["selected_filter_value"] == "4":
                        s3_bucket_upload_file_by_file_path(
                            export_path[1:], "/reverse_analytics_" + requested_data["startdate"] + "-" + requested_data["enddate"] + ".xls")
                    else:
                        s3_bucket_upload_file_by_file_path(
                            export_path[1:], "/reverse_analytics_" + str(start_date) + "-" + str(end_date) + ".xls")

                response["export_path_exist"] = True
                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=export_path, is_public=False, access_token=cobrowse_agent.get_access_token_obj())
                response["export_path"] = 'easy-assist/download-file/' + \
                    str(file_access_management_obj.key)
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportReverseAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportReverseAnalytics = ExportReverseAnalyticsAPI.as_view()


class ExportReverseUniqueCustomersAPI(APIView):

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
            start_date = remo_html_from_string(start_date)
            end_date = data["end_date"]
            end_date = remo_html_from_string(end_date)

            title = None
            if "title" in data and data["title"] != "all":
                title = data["title"]
                title = remo_html_from_string(title)

            DEFAULT_ANALYTICS_START_DATETIME = (
                datetime.datetime.today() - datetime.timedelta(7)).date()

            DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

            datetime_start = DEFAULT_ANALYTICS_START_DATETIME
            datetime_end = DEFAULT_ANALYTICS_END_DATETIME
            try:
                date_format = "%d/%m/%Y"
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(
                    end_date, date_format).date()
            except Exception:
                pass

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()
            agent_objs = [active_agent]
            if active_agent.role == "admin":
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)

            cobrowse_io_objs = CobrowseIO.objects.filter(is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=True).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False, agent__in=agent_objs)

            unique_mobile_numbers = cobrowse_io_objs.values("mobile_number").annotate(
                customer_count=Count('mobile_number')).filter(customer_count__lte=1)
            cobrowse_io_objs = cobrowse_io_objs.filter(
                mobile_number__in=unique_mobile_numbers.values_list('mobile_number', flat=True))

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)
            if cobrowse_io_objs.count() > EXPORTS_UPPER_CAP_LIMIT:
                response["export_path"] = ""
                response["status"] = 301
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)
            export_path = create_excel_easyassist_unique_customers(
                "reverse", active_agent, cobrowse_io_objs, access_token_obj, data)

            if export_path:
                file_path = "/" + export_path
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)

                response["export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportReverseUniqueCustomersAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportReverseUniqueCustomers = ExportReverseUniqueCustomersAPI.as_view()


class ExportReverseRepeatedCustomersAPI(APIView):

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
            start_date = remo_html_from_string(start_date)
            end_date = data["end_date"]
            end_date = remo_html_from_string(end_date)

            title = None
            if "title" in data and data["title"] != "all":
                title = data["title"]
                title = remo_html_from_string(title)

            DEFAULT_ANALYTICS_START_DATETIME = (
                datetime.datetime.today() - datetime.timedelta(7)).date()

            DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

            datetime_start = DEFAULT_ANALYTICS_START_DATETIME
            datetime_end = DEFAULT_ANALYTICS_END_DATETIME
            try:
                date_format = "%d/%m/%Y"
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(
                    end_date, date_format).date()
            except Exception:
                pass

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()
            agent_objs = [active_agent]
            if active_agent.role == "admin":
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)

            cobrowse_io_objs = CobrowseIO.objects.filter(is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=True).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False, agent__in=agent_objs)

            repeated_mobile_numbers = cobrowse_io_objs.values("mobile_number").annotate(
                customer_count=Count('mobile_number')).filter(customer_count__gt=1)
            cobrowse_io_objs = cobrowse_io_objs.filter(
                mobile_number__in=repeated_mobile_numbers.values_list('mobile_number', flat=True))
            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)
            if cobrowse_io_objs.count() > EXPORTS_UPPER_CAP_LIMIT:
                response["export_path"] = ""
                response["status"] = 301
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)
            export_path = create_excel_easyassist_repeated_customers(
                "reverse", cobrowse_io_objs, active_agent, data)

            if export_path:
                file_path = "/" + export_path
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)

                response["export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportReverseRepeatedCustomersAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportReverseRepeatedCustomers = ExportReverseRepeatedCustomersAPI.as_view()


class ExportCronRequestUniqueCustomersReverseAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            data["start_date"] = remo_html_from_string(data["start_date"])
            data["end_date"] = remo_html_from_string(data["end_date"])
            reg_email = '^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$'
            email_id_list = data["email"].split(",")
            for index, email_id in enumerate(email_id_list):
                if not re.search(reg_email, email_id.strip()):
                    response["status"] = 300
                    response["message"] = "Please enter valid Email ID."
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

                email_id_list[index] = email_id.strip()
            data["email"] = email_id_list
            if "title" in data and data["title"] != "all":
                data["title"] = remo_html_from_string(data["title"])
            active_agent = get_active_agent_obj(request, CobrowseAgent)

            EasyAssistExportDataRequest.objects.create(
                report_type="reverse-unique-customers", agent=active_agent, filter_param=json.dumps(data))
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportCronRequestUniqueCustomersReverseAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportCronRequestUniqueCustomersReverse = ExportCronRequestUniqueCustomersReverseAPI.as_view()


class ExportCronRequestRepeatedCustomersReverseAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            data["start_date"] = remo_html_from_string(data["start_date"])
            data["end_date"] = remo_html_from_string(data["end_date"])
            reg_email = '^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$'
            email_id_list = data["email"].split(",")
            for index, email_id in enumerate(email_id_list):
                if not re.search(reg_email, email_id.strip()):
                    response["status"] = 300
                    response["message"] = "Please enter valid Email ID."
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

                email_id_list[index] = email_id.strip()
            data["email"] = email_id_list
            if "title" in data and data["title"] != "all":
                data["title"] = remo_html_from_string(data["title"])
            active_agent = get_active_agent_obj(request, CobrowseAgent)

            EasyAssistExportDataRequest.objects.create(
                report_type="reverse-repeated-customers", agent=active_agent, filter_param=json.dumps(data))
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportCronRequestRepeatedCustomersReverseAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportCronRequestRepeatedCustomersReverse = ExportCronRequestRepeatedCustomersReverseAPI.as_view()
