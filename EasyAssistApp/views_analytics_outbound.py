from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.utils.encoding import smart_str

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


class GetVisitedPageTitleListOutboundAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetVisitedPageTitleListOutboundAPI",
                        extra={'AppName': 'EasyAssist'})
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                is_lead=True).filter(
                ~Q(title=None))

            if access_token_obj.get_proxy_config_obj().enable_proxy_cobrowsing:
                proxy_cobrowse_io_objs = CobrowseIO.objects.filter(
                    is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                    is_lead=False, cobrowsing_type="outbound-proxy-cobrowsing").filter(
                    ~Q(title=None)).filter(~Q(title=""))

                cobrowse_io_objs = cobrowse_io_objs | proxy_cobrowse_io_objs

            query_pages = list(
                set(list(cobrowse_io_objs.values_list('title', flat=True))))

            response["status"] = 200
            response["message"] = "success"
            response["query_pages"] = query_pages
            response["active_agent_role"] = active_agent.role
            logger.info("Successfully exited from GetVisitedPageTitleListOutboundAPI", extra={
                        'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RequestCobrowsingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetVisitedPageTitleListOutbound = GetVisitedPageTitleListOutboundAPI.as_view()


class GetQueryPageAnalyticsOutboundAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetQueryPageAnalyticsOutboundAPI",
                        extra={'AppName': 'EasyAssist'})
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
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=True).filter(
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
            logger.info("Successfully exited from GetQueryPageAnalyticsOutboundAPI", extra={
                        'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetQueryPageAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetQueryPageAnalyticsOutbound = GetQueryPageAnalyticsOutboundAPI.as_view()


class GetAgentWiseRequestAnalyticsOutboundAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetAgentWiseRequestAnalyticsOutboundAPI", extra={
                        'AppName': 'EasyAssist'})
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
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=True)

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

                total_sr_customer_denied = cobrowse_io_objs.filter(
                    agent=agent, consent_cancel_count__gte=1, allow_agent_cobrowse="false", cobrowsing_start_datetime=None).count()

                if access_token_obj.enable_invite_agent_in_cobrowsing:
                    filtered_agent_wise_cobrowse_io = cobrowse_io_objs.filter(
                        agent=agent)
                    group_cobrowse_request_initiated = CobrowseIOInvitedAgentsDetails.objects.filter(
                        cobrowse_io__in=filtered_agent_wise_cobrowse_io).count()
                    group_cobrowse_request_received = CobrowseIOInvitedAgentsDetails.objects.filter(
                        cobrowse_io__in=cobrowse_io_objs, support_agents_invited__in=[agent]).count()
                    group_cobrowse_request_connected = CobrowseIOInvitedAgentsDetails.objects.filter(
                        cobrowse_io__in=cobrowse_io_objs, support_agents_joined__in=[agent]).count()

                    if access_token_obj.enable_session_transfer_in_cobrowsing:
                        transferred_agents_requests_received = CobrowseIOTransferredAgentsLogs.objects.filter(
                            transferred_agent=agent, cobrowse_request_type="transferred", cobrowse_io__in=cobrowse_io_objs).count()
                        transferred_agents_requests_connected = CobrowseIOTransferredAgentsLogs.objects.filter(
                            transferred_agent=agent, cobrowse_request_type="transferred", cobrowse_io__in=cobrowse_io_objs, transferred_status="accepted").count()
                        transferred_agents_requests_rejected = transferred_agents_requests_received - transferred_agents_requests_connected

                if access_token_obj.enable_invite_agent_in_cobrowsing:
                    if access_token_obj.enable_session_transfer_in_cobrowsing:
                        agent_request_analytics_list.append({
                            "agent": agent.user.username,
                            "supervisor": agent.get_supervisors(),
                            "total_sr": total_sr,
                            "total_sr_closed": total_sr_closed,
                            "total_sr_attended": total_sr_attended,
                            "total_sr_customer_denied": total_sr_customer_denied,
                            "group_cobrowse_request_initiated": group_cobrowse_request_initiated,
                            "group_cobrowse_request_received": group_cobrowse_request_received,
                            "group_cobrowse_request_connected": group_cobrowse_request_connected,
                            "transferred_agents_requests_received": transferred_agents_requests_received,
                            "transferred_agents_requests_connected": transferred_agents_requests_connected,
                            "transferred_agents_requests_rejected": transferred_agents_requests_rejected,
                        })
                    else:
                        agent_request_analytics_list.append({
                            "agent": agent.user.username,
                            "supervisor": agent.get_supervisors(),
                            "total_sr": total_sr,
                            "total_sr_closed": total_sr_closed,
                            "total_sr_attended": total_sr_attended,
                            "total_sr_customer_denied": total_sr_customer_denied,
                            "group_cobrowse_request_initiated": group_cobrowse_request_initiated,
                            "group_cobrowse_request_received": group_cobrowse_request_received,
                            "group_cobrowse_request_connected": group_cobrowse_request_connected
                        })
                else:
                    agent_request_analytics_list.append({
                        "agent": agent.user.username,
                        "supervisor": agent.get_supervisors(),
                        "total_sr": total_sr,
                        "total_sr_closed": total_sr_closed,
                        "total_sr_attended": total_sr_attended,
                        "total_sr_customer_denied": total_sr_customer_denied
                    })

            if access_token_obj.enable_invite_agent_in_cobrowsing:
                if access_token_obj.enable_session_transfer_in_cobrowsing:
                    agent_request_analytics_list.sort(key=lambda data: (
                        data['total_sr'],
                        data['total_sr_attended'],
                        data['total_sr_closed'],
                        data['total_sr_customer_denied'],
                        data['group_cobrowse_request_initiated'],
                        data['group_cobrowse_request_received'],
                        data['group_cobrowse_request_connected'],
                        data['transferred_agents_requests_received'],
                        data['transferred_agents_requests_connected'],
                        data['transferred_agents_requests_rejected'],
                    ), reverse=True)
                else:
                    agent_request_analytics_list.sort(key=lambda data: (
                        data['total_sr'],
                        data['total_sr_attended'],
                        data['total_sr_closed'],
                        data['total_sr_customer_denied'],
                        data['group_cobrowse_request_initiated'],
                        data['group_cobrowse_request_received'],
                        data['group_cobrowse_request_connected'],
                    ), reverse=True)
            else:
                agent_request_analytics_list.sort(key=lambda data: (
                    data['total_sr'],
                    data['total_sr_attended'],
                    data['total_sr_closed'],
                    data['total_sr_customer_denied'],
                ), reverse=True)

            response["status"] = 200
            response["message"] = "success"
            response["agent_request_analytics_list"] = agent_request_analytics_list
            logger.info("Successfully exited from GetAgentWiseRequestAnalyticsOutboundAPI", extra={
                        'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentWiseRequestAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentWiseRequestAnalyticsOutbound = GetAgentWiseRequestAnalyticsOutboundAPI.as_view()


class GetAgentNPSAnalyticsOutboundAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetAgentNPSAnalyticsOutboundAPI",
                        extra={'AppName': 'EasyAssist'})
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
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=True).filter(
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
            logger.info("Successfully exited from GetAgentNPSAnalyticsOutboundAPI", extra={
                        'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentNPSAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentNPSAnalyticsOutbound = GetAgentNPSAnalyticsOutboundAPI.as_view()


class GetAgentBasicAnalyticsOutboundAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetAgentBasicAnalyticsOutboundAPI",
                        extra={'AppName': 'EasyAssist'})
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
            total_sr_lead_captured = 0
            total_sr_customer_denied = 0
            cobrowse_io_objs = None
            avg_session_duration = 0
            conversion_rate = 0
            avg_wait_time = 0
            avg_wait_time_unattended = 0
            unique_customers = 0
            repeated_customers = 0

            agent_objs = [active_agent]

            if active_agent.role in ["admin", "admin_ally"]:
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=True)

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            # total cobrowsing lead captured
            total_sr_lead_captured = cobrowse_io_objs.filter(
                access_token=access_token_obj).count()

            cobrowse_io_objs = cobrowse_io_objs.filter(agent__in=agent_objs)

            unique_identifier_field = access_token_obj.search_fields.filter(
                unique_identifier=True)

            captured_data = CobrowseCapturedLeadData.objects.filter(search_field__in=unique_identifier_field, agent_searched=True).values("primary_value").annotate(
                value_count=Count('primary_value')).filter(value_count=1).values_list("primary_value", flat=True)

            unique_cobrowse_io_objs = cobrowse_io_objs.filter(
                session_id__in=CobrowseCapturedLeadData.objects.filter(primary_value__in=captured_data, agent_searched=True).values_list("session_id", flat=True))

            non_unique_identifier_field = access_token_obj.search_fields.filter(
                unique_identifier=False)

            off_field_captured_data = CobrowseCapturedLeadData.objects.filter(
                search_field__in=non_unique_identifier_field, agent_searched=True).values_list("session_id", flat=True)

            non_unique_captured_session = cobrowse_io_objs.filter(
                session_id__in=off_field_captured_data)

            unique_customers = unique_cobrowse_io_objs.count() + non_unique_captured_session.count()

            repeated_captured_data = CobrowseCapturedLeadData.objects.filter(search_field__in=unique_identifier_field, agent_searched=True).values(
                "primary_value").annotate(value_count=Count('primary_value')).filter(value_count__gt=1).values_list("primary_value", flat=True)

            repeated_cobrowse_io_objs = cobrowse_io_objs.filter(session_id__in=CobrowseCapturedLeadData.objects.filter(primary_value__in=repeated_captured_data, agent_searched=True).values_list("session_id", flat=True))

            prev_value_list = {}
    
            for cobrowse_io_obj in repeated_cobrowse_io_objs:
                data_captured = cobrowse_io_obj.captured_lead.filter(
                    agent_searched=True).first()
                if data_captured and data_captured.primary_value not in prev_value_list and repeated_captured_data.filter(primary_value=data_captured.primary_value).count():
                    prev_value_list[data_captured.primary_value] = 1
                    repeated_customers += 1
                else:
                    continue

            nps = "..."
            if cobrowse_io_objs != None:
                # total cobrowsing request Initiated/Notinitiated
                total_sr = cobrowse_io_objs.count()

                # total cobrowsing request initiated and converted successfully
                total_sr_closed = cobrowse_io_objs.filter(
                    is_helpful=True, is_archived=True, is_lead_converted_by_url=False).filter(~Q(cobrowsing_start_datetime=None)).count()

                # total cobrowsing request initiated and converted successfully by landing at specified URL
                total_sr_closed_by_url = cobrowse_io_objs.filter(
                    is_helpful=True, is_archived=True, is_lead_converted_by_url=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                # total cobrowsing request attended
                total_sr_attended = cobrowse_io_objs.filter(
                    ~Q(cobrowsing_start_datetime=None)).count()

                # total cobrowsing request denied by customer
                total_sr_customer_denied = cobrowse_io_objs.filter(
                    consent_cancel_count__gte=1, allow_agent_cobrowse="false", cobrowsing_start_datetime=None).count()

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
                    avg_wait_time += cobrowse_io.customer_wait_time_in_seconds()
                try:
                    avg_session_duration = avg_session_duration / (
                        total_sr_attended * 60)
                    avg_wait_time = avg_wait_time / (
                        total_sr_attended * 60)
                    conversion_rate = (total_sr_closed /
                                       total_sr_attended) * 100
                    conversion_rate = round(conversion_rate)
                    conversion_rate = str(conversion_rate)
                except Exception:
                    logger.warning("divide by zero", extra={
                        'AppName': 'EasyAssist'})

                cobrowse_io_not_initiated = cobrowse_io_objs.filter(
                    Q(cobrowsing_start_datetime=None))
                total_sr_unattended = cobrowse_io_not_initiated.count()

                for cobrowse_io in cobrowse_io_not_initiated:
                    avg_wait_time_unattended += cobrowse_io.customer_wait_time_in_seconds()
                try:
                    avg_wait_time_unattended = avg_wait_time_unattended / (
                        total_sr_unattended * 60)
                except Exception:
                    logger.warning("divide by zero", extra={
                        'AppName': 'EasyAssist'})

            response["total_sr"] = total_sr
            response["total_sr_closed"] = total_sr_closed
            response["total_sr_closed_by_url"] = total_sr_closed_by_url
            response["total_sr_attended"] = total_sr_attended
            response["total_sr_lead_captured"] = total_sr_lead_captured
            response["total_sr_customer_denied"] = total_sr_customer_denied
            response["nps"] = nps
            response["avg_session_duration"] = avg_session_duration
            response["conversion_rate"] = conversion_rate
            response["avg_wait_time"] = avg_wait_time
            response["avg_wait_time_unattended"] = avg_wait_time_unattended
            response["unique_customers"] = unique_customers
            response["repeated_customers"] = repeated_customers
            response["status"] = 200
            logger.info("Successfully exited from GetAgentBasicAnalyticsOutboundAPI", extra={
                        'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentBasicAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentBasicAnalyticsOutbound = GetAgentBasicAnalyticsOutboundAPI.as_view()


class GetAgentServiceRequestAnalyticsOutboundAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetAgentServiceRequestAnalyticsOutboundAPI", extra={
                        'AppName': 'EasyAssist'})
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
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=True)

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            service_request_analytics = []
            if timeline == "daily":
                no_days = (datetime_end - datetime_start).days + 1
                for day in range(no_days):
                    temp_datetime = datetime_start + datetime.timedelta(day)

                    date_filtered_cobrowse_io_objs = cobrowse_io_objs.filter(
                        request_datetime__date=temp_datetime)

                    # total cobrowsing lead captured
                    total_sr_lead_captured = date_filtered_cobrowse_io_objs.filter(
                        access_token=access_token_obj).count()

                    date_filtered_cobrowse_io_objs = date_filtered_cobrowse_io_objs.filter(
                        agent__in=agent_objs)

                    # total cobrowsing request Initiated/Notinitiated
                    total_sr = date_filtered_cobrowse_io_objs.count()

                    # total cobrowsing request initiated and converted
                    # successfully
                    total_sr_closed = date_filtered_cobrowse_io_objs.filter(
                        is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                    # total cobrowsing request attended
                    total_sr_attended = date_filtered_cobrowse_io_objs.filter(
                        ~Q(cobrowsing_start_datetime=None)).count()

                    # total cobrowsing request denied by customer
                    total_sr_customer_denied = date_filtered_cobrowse_io_objs.filter(
                        consent_cancel_count__gte=1, allow_agent_cobrowse="false", cobrowsing_start_datetime=None).count()

                    service_request_analytics.append({
                        "label": str(temp_datetime.strftime("%d-%b-%y")),
                        "total_sr": total_sr,
                        "total_sr_closed": total_sr_closed,
                        "total_sr_attended": total_sr_attended,
                        "total_sr_lead_captured": total_sr_lead_captured,
                        "total_sr_customer_denied": total_sr_customer_denied
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

                    total_sr_lead_captured = date_filtered_cobrowse_io_objs.filter(
                        access_token=access_token_obj).count()

                    date_filtered_cobrowse_io_objs = date_filtered_cobrowse_io_objs.filter(
                        agent__in=agent_objs)

                    total_sr = date_filtered_cobrowse_io_objs.count()
                    total_sr_closed = date_filtered_cobrowse_io_objs.filter(
                        is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()
                    total_sr_attended = date_filtered_cobrowse_io_objs.filter(
                        ~Q(cobrowsing_start_datetime=None)).count()
                    total_sr_customer_denied = date_filtered_cobrowse_io_objs.filter(
                        consent_cancel_count__gte=1, allow_agent_cobrowse="false", cobrowsing_start_datetime=None).count()

                    temp_start_datetime_str = temp_start_datetime.strftime(
                        "%d/%m")
                    temp_end_datetime_str = (
                        temp_end_datetime - datetime.timedelta(1)).strftime("%d/%m")

                    service_request_analytics.append({
                        "label": temp_start_datetime_str + "-" + temp_end_datetime_str,
                        "total_sr": total_sr,
                        "total_sr_closed": total_sr_closed,
                        "total_sr_attended": total_sr_attended,
                        "start_date": str(temp_start_datetime),
                        "end_date": str(temp_end_datetime - datetime.timedelta(1)),
                        "total_sr_lead_captured": total_sr_lead_captured,
                        "total_sr_customer_denied": total_sr_customer_denied
                    })
            elif timeline == "monthly":
                month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
                    r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days)).keys())

                for month in month_list:
                    temp_month = month_to_num_dict[month.split("-")[0]]
                    temp_year = int(month.split("-")[1])
                    date_filtered_cobrowse_io_objs = cobrowse_io_objs.filter(
                        request_datetime__date__month=temp_month, request_datetime__date__year=temp_year)

                    total_sr_lead_captured = date_filtered_cobrowse_io_objs.filter(
                        access_token=access_token_obj).count()

                    date_filtered_cobrowse_io_objs = date_filtered_cobrowse_io_objs.filter(
                        agent__in=agent_objs)

                    total_sr = date_filtered_cobrowse_io_objs.count()
                    total_sr_closed = date_filtered_cobrowse_io_objs.filter(
                        is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()
                    total_sr_attended = date_filtered_cobrowse_io_objs.filter(
                        ~Q(cobrowsing_start_datetime=None)).count()
                    total_sr_customer_denied = date_filtered_cobrowse_io_objs.filter(
                        consent_cancel_count__gte=1, allow_agent_cobrowse="false", cobrowsing_start_datetime=None).count()

                    service_request_analytics.append({
                        "label": month,
                        "total_sr": total_sr,
                        "total_sr_closed": total_sr_closed,
                        "total_sr_attended": total_sr_attended,
                        "total_sr_lead_captured": total_sr_lead_captured,
                        "total_sr_customer_denied": total_sr_customer_denied
                    })
            else:
                logger.info("invalid timeline", extra={
                            'AppName': 'EasyAssist'})

            response["active_agent_role"] = active_agent.role
            response["service_request_analytics"] = service_request_analytics
            response["status"] = 200
            logger.info("Successfully exited from GetAgentServiceRequestAnalyticsOutboundAPI", extra={
                        'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentServiceRequestAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentServiceRequestAnalyticsOutbound = GetAgentServiceRequestAnalyticsOutboundAPI.as_view()


class ExportOutboundAnalyticsAPI(APIView):

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

                export_path = "/secured_files/EasyAssistApp/OutboundAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/outbound_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "2":
                # Last 7 days data
                start_date = datetime.datetime.now() - datetime.timedelta(days=7)
                start_date = start_date.strftime(date_format)
                end_date = datetime.datetime.now() - datetime.timedelta(days=1)
                end_date = end_date.strftime(date_format)

                export_path = "/secured_files/EasyAssistApp/OutboundAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/outbound_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "3":
                # Last 30 days data
                start_date = datetime.datetime.now() - datetime.timedelta(days=30)
                start_date = start_date.strftime(date_format)
                end_date = datetime.datetime.now() - datetime.timedelta(days=1)
                end_date = end_date.strftime(date_format)

                export_path = "/secured_files/EasyAssistApp/OutboundAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/outbound_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "4":

                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()

                today_date = datetime.datetime.today().date()

                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='outbound-analytics', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                else:
                    export_path = get_outbound_analytics_data_dump(
                        requested_data, cobrowse_agent, CobrowseDateWiseOutboundAnalytics)

            if os.path.exists(export_path[1:]) == True:
                if get_save_in_s3_bucket_status():
                    if requested_data["selected_filter_value"] == "4":
                        key = s3_bucket_upload_file_by_file_path(
                            export_path[1:], "/outbound_analytics_" + requested_data["startdate"] + "-" + requested_data["enddate"] + ".xls")
                    else:
                        key = s3_bucket_upload_file_by_file_path(
                            export_path[1:], "/outbound_analytics_" + str(start_date) + "-" + str(end_date) + ".xls")
                    s3_file_path = s3_bucket_download_file(
                        key, 'EasyAssistApp/OutboundAnalytics/', '.xls')
                    export_path = "/" + s3_file_path.split("EasyChat/", 1)[1]
                response["export_path_exist"] = True
                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=export_path, is_public=False, access_token=cobrowse_agent.get_access_token_obj())
                response["export_path"] = 'easy-assist/download-file/' + \
                    str(file_access_management_obj.key)
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportOutboundAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportOutboundAnalytics = ExportOutboundAnalyticsAPI.as_view()


class ExportUniqueCustomersOutboundAPI(APIView):

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

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=True, agent__in=agent_objs)
            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            unique_identifier_field = access_token_obj.search_fields.filter(
                unique_identifier=True)
                
            captured_data = CobrowseCapturedLeadData.objects.filter(search_field__in=unique_identifier_field, agent_searched=True).values("primary_value").annotate(
                value_count=Count('primary_value')).filter(value_count=1).values_list("primary_value", flat=True)

            unique_cobrowse_io_objs = cobrowse_io_objs.filter(
                session_id__in=CobrowseCapturedLeadData.objects.filter(primary_value__in=captured_data, agent_searched=True).values_list("session_id", flat=True))

            non_unique_identifier_field = access_token_obj.search_fields.filter(
                unique_identifier=False)

            off_field_captured_data = CobrowseCapturedLeadData.objects.filter(
                search_field__in=non_unique_identifier_field, agent_searched=True).values_list("session_id", flat=True)

            non_unique_captured_session = cobrowse_io_objs.filter(
                session_id__in=off_field_captured_data)

            cobrowse_io_objs = unique_cobrowse_io_objs | non_unique_captured_session
            
            if cobrowse_io_objs.count() > EXPORTS_UPPER_CAP_LIMIT:
                response["export_path"] = ""
                response["status"] = 301
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            export_path = create_excel_easyassist_unique_customers_outbound(
                cobrowse_io_objs, active_agent, access_token_obj, data)

            if export_path:
                file_path = "/" + export_path
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)

                response["export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportUniqueCustomersOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportUniqueCustomersOutbound = ExportUniqueCustomersOutboundAPI.as_view()


class ExportRepeatedCustomersOutboundAPI(APIView):

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

            cobrowse_io_objs = CobrowseIO.objects.filter(is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=True, agent__in=agent_objs)

            unique_identifier_field = access_token_obj.search_fields.filter(
                unique_identifier=True)

            repeated_captured_data = CobrowseCapturedLeadData.objects.filter(search_field__in=unique_identifier_field, agent_searched=True).values(
                "primary_value").annotate(value_count=Count('primary_value')).filter(value_count__gt=1).values_list("primary_value", flat=True)

            captured_data_session = CobrowseCapturedLeadData.objects.filter(primary_value__in=repeated_captured_data, agent_searched=True).values_list("session_id", flat=True)

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            cobrowse_io_objs = cobrowse_io_objs.filter(session_id__in=captured_data_session)
            
            if cobrowse_io_objs.count() > EXPORTS_UPPER_CAP_LIMIT:
                response["export_path"] = ""
                response["status"] = 301
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            export_path = create_excel_easyassist_repeated_customers_outbound(
                cobrowse_io_objs, active_agent, repeated_captured_data, captured_data_session, data)

            if export_path:
                file_path = "/" + export_path
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)

                response["export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportRepeatedCustomersOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportRepeatedCustomersOutbound = ExportRepeatedCustomersOutboundAPI.as_view()


class ExportCronRequestUniqueCustomersOutboundAPI(APIView):

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
                report_type="outbound-unique-customers", agent=active_agent, filter_param=json.dumps(data))

            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportCronRequestUniqueCustomersOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportCronRequestUniqueCustomersOutbound = ExportCronRequestUniqueCustomersOutboundAPI.as_view()


class ExportCronRequestRepeatedCustomersOutboundAPI(APIView):

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
                report_type="outbound-repeated-customers", agent=active_agent, filter_param=json.dumps(data))

            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportCronRequestRepeatedCustomersOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportCronRequestRepeatedCustomersOutbound = ExportCronRequestRepeatedCustomersOutboundAPI.as_view()


class ExportCapturedLeadsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        export_path = ""

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            start_date = data["start_date"]
            start_date = remo_html_from_string(start_date)
            end_date = data["end_date"]
            end_date = remo_html_from_string(end_date)

            try:
                date_format = "%d/%m/%Y"
                start_date = datetime.datetime.strptime(
                    start_date, date_format).date()
                end_date = datetime.datetime.strptime(
                    end_date, date_format).date()

                if start_date > end_date:
                    response["status"] = 300
                    response["message"] = "Start date cannot be greater than the end date"
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error ExportCapturedLeadsAPI %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

            data["start_date"] = start_date
            data["end_date"] = end_date

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, is_archived=True, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_reverse_cobrowsing=False, is_lead=True).filter(
                request_datetime__date__gte=start_date, request_datetime__date__lte=end_date)

            total_captured_lead_count = cobrowse_io_objs.count()

            if total_captured_lead_count < EXPORTS_UPPER_CAP_LIMIT:
                export_path = create_excel_easyassist_capture_leads(
                    data, cobrowse_io_objs, access_token_obj)

                if export_path:
                    file_path = "/" + export_path
                    file_access_management_key = create_file_access_management_obj(
                        CobrowsingFileAccessManagement, access_token_obj, file_path)

                    response["export_path"] = 'easy-assist/download-file/' + \
                        file_access_management_key
                    response["status"] = 200
            else:
                response["status"] = 103
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportCapturedLeadsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportCapturedLeads = ExportCapturedLeadsAPI.as_view()


class EmailCapturedLeadsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            regEmail = '^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$'
            start_date = data["start_date"]
            start_date = remo_html_from_string(start_date)
            end_date = data["end_date"]
            end_date = remo_html_from_string(end_date)
            email_id_list = data["email_id_list"].split(",")

            try:
                date_format = "%d/%m/%Y"
                startdate = datetime.datetime.strptime(
                    start_date, date_format).date()
                enddate = datetime.datetime.strptime(
                    end_date, date_format).date()

                if startdate > enddate:
                    response["status"] = 300
                    response["message"] = "Start date cannot be greater than the end date"
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error EmailCapturedLeadsAPI %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

            for index, email_id in enumerate(email_id_list):
                if not re.search(regEmail, email_id.strip()):
                    response["status"] = 300
                    response["message"] = "Please enter valid Email ID."
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

                email_id_list[index] = email_id.strip()

            data["start_date"] = start_date
            data["end_date"] = end_date
            data["email_id_list"] = email_id_list

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            EasyAssistExportDataRequest.objects.create(
                report_type='outbound-captured-leads', agent=active_agent, filter_param=json.dumps(data))

            response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EmailCapturedLeadsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


EmailCapturedLeads = EmailCapturedLeadsAPI.as_view()
