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

from EasyChatApp.models import User
from EasyAssistApp.models import *
from EasyAssistApp.utils import *
from EasyAssistApp.views_table import *
from EasyAssistApp.send_email import send_password_over_email

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
                is_lead=False, is_reverse_cobrowsing=False).filter(
                ~Q(title=None)).filter(
                ~Q(cobrowsing_start_datetime=None)).exclude(cobrowsing_type="outbound-proxy-cobrowsing")

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


class GetQueryPageAnalyticsAPI(APIView):

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
                datetime_end = datetime.datetime.strptime(
                    end_date, date_format).date()
            except Exception:
                pass

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False).filter(
                ~Q(cobrowsing_start_datetime=None)).exclude(cobrowsing_type="outbound-proxy-cobrowsing")

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
            logger.error("Error GetQueryPageAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetQueryPageAnalytics = GetQueryPageAnalyticsAPI.as_view()


class GetQueryPageAnalyticsCountAPI(APIView):

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
                datetime_end = datetime.datetime.strptime(
                    end_date, date_format).date()
            except Exception:
                logger.info("No requested date time found in GetQueryPageAnalyticsCountAPI",
                            extra={'AppName': 'EasyAssist'})

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False, is_archived=True).filter(
                ~Q(cobrowsing_start_datetime=None)).exclude(cobrowsing_type="outbound-proxy-cobrowsing")

            cobrowse_page_visit_objs = CobrowsePageVisitCount.objects.filter(
                cobrowse_access_token=access_token_obj, page_visit_date__lte=datetime_end, page_visit_date__gte=datetime_start)

            if cobrowse_page_visit_objs != None and title != None:
                cobrowse_page_visit_objs = cobrowse_page_visit_objs.filter(
                    page_title=title)

            query_page_visit = []

            if active_agent.role in ["admin", "supervisor", "admin_ally"]:

                query_page_visit = cobrowse_page_visit_objs.values('page_url', 'page_title').annotate(
                    page_visit_count=Sum('page_count')).order_by("-page_visit_count")

                cobrowse_count_objs = cobrowse_io_objs.values(
                    'title', 'active_url').annotate(cobrowse_count=Count(1))
                cobrowse_count_data = dict()
                for cobrowse_count_obj in cobrowse_count_objs:
                    cobrowse_count_data[(
                        cobrowse_count_obj['title'], cobrowse_count_obj['active_url'])] = cobrowse_count_obj['cobrowse_count']

                logger.warning("GetQueryPageAnalyticsCountAPI Total page visit objects %s",
                               str(len(query_page_visit)), extra={'AppName': 'EasyAssist'})

                for query_page_visit_obj in query_page_visit:
                    query_tuple = (
                        query_page_visit_obj['page_title'], query_page_visit_obj['page_url'])
                    page_cobrowse_count = cobrowse_count_data.get(
                        query_tuple, 0)
                    # query_page_visit_obj['page_cobrowse_count'] = cobrowse_io_objs.filter(title=query_page_visit_obj['page_title'], active_url=query_page_visit_obj['page_url']).count()
                    query_page_visit_obj['page_cobrowse_count'] = page_cobrowse_count

                paginator = Paginator(query_page_visit, 5)
                no_pages = paginator.num_pages

                is_last_page = False
                if int(page) >= int(no_pages):
                    is_last_page = True

                try:
                    query_page_visit = paginator.page(page)
                except PageNotAnInteger:
                    query_page_visit = paginator.page(1)
                except EmptyPage:
                    query_page_visit = paginator.page(paginator.num_pages)

                response["status"] = 200
                response["message"] = "success"
                response["query_page_visit"] = list(query_page_visit)
                response["is_last_page"] = is_last_page
            else:
                response["status"] = 401
                response["message"] = "Unauthorized access"
                response["query_page_visit"] = query_page_visit

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetQueryPageAnalyticsCountAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetQueryPageAnalyticsCount = GetQueryPageAnalyticsCountAPI.as_view()


class GetAgentWiseRequestAnalyticsAPI(APIView):

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

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False).exclude(cobrowsing_type="outbound-proxy-cobrowsing")

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

                total_sr_not_closed = cobrowse_io_objs.filter(
                    agent=agent, is_helpful=False).filter(~Q(cobrowsing_start_datetime=None)).count()

                total_sr_not_attended = cobrowse_io_objs.filter(
                    agent=agent).filter(Q(cobrowsing_start_datetime=None)).filter(~Q(allow_agent_cobrowse="false")).exclude(
                    session_archived_cause__in=["FOLLOWUP", "UNASSIGNED"]).count()

                total_sr_attended = cobrowse_io_objs.filter(
                    agent=agent).filter(~Q(cobrowsing_start_datetime=None)).count()

                self_assign_count = 0
                average_self_assign_time = "0 sec"
                if access_token_obj.enable_request_in_queue:
                    self_assign_ios = cobrowse_io_objs.filter(agent=agent).filter(~Q(self_assign_time=None))
                    self_assign_count = self_assign_ios.count()
                    average_self_assign_time = get_average_self_assign_time(self_assign_count, self_assign_ios)
                    if not average_self_assign_time:
                        average_self_assign_time = "-"

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
                            "total_sr_not_closed": total_sr_not_closed,
                            "total_sr_attended": total_sr_attended,
                            "total_sr_not_attended": total_sr_not_attended,
                            "group_cobrowse_request_initiated": group_cobrowse_request_initiated,
                            "group_cobrowse_request_received": group_cobrowse_request_received,
                            "group_cobrowse_request_connected": group_cobrowse_request_connected,
                            "transferred_agents_requests_received": transferred_agents_requests_received,
                            "transferred_agents_requests_connected": transferred_agents_requests_connected,
                            "transferred_agents_requests_rejected": transferred_agents_requests_rejected,
                            "self_assign_count": self_assign_count,
                            "average_self_assign_time": average_self_assign_time,
                        })
                    else:
                        agent_request_analytics_list.append({
                            "agent": agent.user.username,
                            "supervisor": agent.get_supervisors(),
                            "total_sr": total_sr,
                            "total_sr_closed": total_sr_closed,
                            "total_sr_not_closed": total_sr_not_closed,
                            "total_sr_attended": total_sr_attended,
                            "total_sr_not_attended": total_sr_not_attended,
                            "group_cobrowse_request_initiated": group_cobrowse_request_initiated,
                            "group_cobrowse_request_received": group_cobrowse_request_received,
                            "group_cobrowse_request_connected": group_cobrowse_request_connected,
                            "self_assign_count": self_assign_count,
                            "average_self_assign_time": average_self_assign_time,
                        })
                else:
                    agent_request_analytics_list.append({
                        "agent": agent.user.username,
                        "supervisor": agent.get_supervisors(),
                        "total_sr": total_sr,
                        "total_sr_closed": total_sr_closed,
                        "total_sr_not_closed": total_sr_not_closed,
                        "total_sr_attended": total_sr_attended,
                        "total_sr_not_attended": total_sr_not_attended,
                        "self_assign_count": self_assign_count,
                        "average_self_assign_time": average_self_assign_time,
                    })

            if access_token_obj.enable_invite_agent_in_cobrowsing:
                if access_token_obj.enable_session_transfer_in_cobrowsing:
                    agent_request_analytics_list.sort(key=lambda data: (
                        data['total_sr'],
                        data['total_sr_attended'],
                        data['total_sr_closed'],
                        data['total_sr_not_attended'],
                        data['total_sr_not_closed'],
                        data['group_cobrowse_request_initiated'],
                        data['group_cobrowse_request_received'],
                        data['group_cobrowse_request_connected'],
                        data['transferred_agents_requests_received'],
                        data['transferred_agents_requests_connected'],
                        data['transferred_agents_requests_rejected'],
                        data["self_assign_count"],
                        data["average_self_assign_time"],
                    ), reverse=True)
                else: 
                    agent_request_analytics_list.sort(key=lambda data: (
                        data['total_sr'],
                        data['total_sr_attended'],
                        data['total_sr_closed'],
                        data['total_sr_not_attended'],
                        data['total_sr_not_closed'],
                        data['group_cobrowse_request_initiated'],
                        data['group_cobrowse_request_received'],
                        data['group_cobrowse_request_connected'],
                        data["self_assign_count"],
                        data["average_self_assign_time"],
                    ), reverse=True)
            else:
                agent_request_analytics_list.sort(key=lambda data: (
                    data['total_sr'],
                    data['total_sr_attended'],
                    data['total_sr_closed'],
                    data['total_sr_not_attended'],
                    data['total_sr_not_closed'],
                    data["self_assign_count"],
                    data["average_self_assign_time"],
                ), reverse=True)

            response["status"] = 200
            response["message"] = "success"
            response["agent_request_analytics_list"] = agent_request_analytics_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentWiseRequestAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentWiseRequestAnalytics = GetAgentWiseRequestAnalyticsAPI.as_view()


class GetAgentNPSAnalyticsAPI(APIView):

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
                datetime_end = datetime.datetime.strptime(
                    end_date, date_format).date()
            except Exception:
                pass

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False).filter(
                ~Q(cobrowsing_start_datetime=None)).exclude(cobrowsing_type="outbound-proxy-cobrowsing")

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
            logger.error("Error GetAgentNPSAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentNPSAnalytics = GetAgentNPSAnalyticsAPI.as_view()


class GetAgentBasicAnalyticsAPI(APIView):

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

            total_sr = 0
            total_sr_closed = 0
            total_sr_closed_by_url = 0
            total_sr_not_closed = 0
            total_sr_attended = 0
            total_sr_not_initiated_after_request = 0
            cobrowse_io_objs = None
            avg_session_duration = 0
            avg_wait_time = 0
            avg_wait_time_unattended = 0
            browsing_time_before_connect_click = 0
            unique_customers = 0
            repeated_customers = 0
            self_assign_count = 0
            average_self_assign_time = ""

            agent_objs = [active_agent]

            if active_agent.role in ["admin", "admin_ally"]:
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False, agent__in=agent_objs).exclude(cobrowsing_type="outbound-proxy-cobrowsing")

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            total_sr_not_initiated_after_request = EasyAssistCustomer.objects.filter(
                access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                cobrowse_io=None).count()

            # The below code has been commented because this leads to a count of 0 for "Cobrowsing Requests Unattended"
            # time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=5)

            # total_sr_not_initiated_after_assigned = cobrowse_io_objs.filter(cobrowsing_start_datetime=None).filter(
            #     Q(request_datetime__lte=time_threshold) & Q(is_archived=False)).exclude(session_archived_cause__in=["FOLLOWUP", "UNASSIGNED"]).count()

            total_sr_not_initiated_after_assigned = cobrowse_io_objs.filter(cobrowsing_start_datetime=None).exclude(session_archived_cause__in=["FOLLOWUP", "UNASSIGNED"]).count()

            total_links_generated = CobrowseDropLink.objects.filter(agent__in=agent_objs, generate_datetime__date__gte=access_token_obj.go_live_date).filter(
                generate_datetime__date__gte=datetime_start, generate_datetime__date__lte=datetime_end, proxy_cobrowse_io=None).count()

            nps = "..."
            if cobrowse_io_objs != None:

                total_sr = cobrowse_io_objs.count()

                total_sr_closed = cobrowse_io_objs.filter(
                    is_helpful=True, is_archived=True, is_lead_converted_by_url=False).filter(~Q(cobrowsing_start_datetime=None)).count()

                total_sr_closed_by_url = cobrowse_io_objs.filter(
                    is_helpful=True, is_archived=True, is_lead_converted_by_url=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                total_sr_not_closed = cobrowse_io_objs.filter(
                    is_helpful=False).filter(~Q(cobrowsing_start_datetime=None)).count()

                total_sr_attended = cobrowse_io_objs.filter(
                    ~Q(cobrowsing_start_datetime=None)).count()

                total_sr_nps = cobrowse_io_objs.filter(
                    is_archived=True).filter(~Q(agent_rating=None)).filter(~Q(cobrowsing_start_datetime=None)).count()

                customers_details = cobrowse_io_objs.values("mobile_number").annotate(customer_count=Count('mobile_number')) 
                unique_customers = customers_details.filter(customer_count=1).count()
                repeated_customers = customers_details.filter(customer_count__gt=1).count()

                if access_token_obj.enable_request_in_queue:
                    self_assign_ios = cobrowse_io_objs.filter(~Q(self_assign_time=None))
                    self_assign_count = self_assign_ios.count()
                    average_self_assign_time = get_average_self_assign_time(self_assign_count, self_assign_ios, True)
                    
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
                except Exception:
                    logger.warning("divide by zero", extra={
                        'AppName': 'EasyAssist'})

                cobrowse_io_not_initiated = cobrowse_io_objs.filter(
                    Q(cobrowsing_start_datetime=None)).exclude(session_archived_cause__in=["FOLLOWUP", "UNASSIGNED"])
                total_sr_unattended = cobrowse_io_not_initiated.count()

                for cobrowse_io in cobrowse_io_not_initiated:
                    avg_wait_time_unattended += cobrowse_io.customer_wait_time_in_seconds()
                try:
                    avg_wait_time_unattended = avg_wait_time_unattended / (
                        total_sr_unattended * 60)
                except Exception:
                    logger.warning("divide by zero", extra={
                        'AppName': 'EasyAssist'})

                browsing_time_before_connect_click = cobrowse_io_objs.aggregate(
                    Sum('browsing_time_before_connect_click'))

                if total_sr and browsing_time_before_connect_click['browsing_time_before_connect_click__sum']:
                    browsing_time_before_connect_click = browsing_time_before_connect_click[
                        'browsing_time_before_connect_click__sum'] / total_sr
                else:
                    browsing_time_before_connect_click = 0
            total_sr_greeting_bubble = cobrowse_io_objs.filter(
                lead_initiated_by='greeting_bubble').count()
            total_sr_floating_button = cobrowse_io_objs.filter(
                lead_initiated_by__in=['floating_button', "icon"]).count()
            total_sr_exit_intent = cobrowse_io_objs.filter(
                lead_initiated_by='exit_intent').count()
            total_sr_inactivity_popup = cobrowse_io_objs.filter(
                lead_initiated_by='inactivity_popup').count()
            response["total_sr"] = total_sr
            response["total_sr_greeting_bubble"] = total_sr_greeting_bubble
            response['total_sr_floating_button'] = total_sr_floating_button
            response["total_sr_inactivity_popup"] = total_sr_inactivity_popup
            response['total_sr_exit_intent'] = total_sr_exit_intent
            response["total_sr_closed"] = total_sr_closed
            response["total_sr_closed_by_url"] = total_sr_closed_by_url
            response["total_sr_not_closed"] = total_sr_not_closed
            response["total_sr_attended"] = total_sr_attended
            response[
                "total_sr_not_initiated_after_request"] = total_sr_not_initiated_after_request
            response[
                "total_sr_not_initiated_after_assigned"] = total_sr_not_initiated_after_assigned
            response["nps"] = nps
            response["avg_session_duration"] = avg_session_duration
            response["avg_wait_time"] = avg_wait_time
            response["avg_wait_time_unattended"] = avg_wait_time_unattended
            response["browsing_time_before_connect_click"] = browsing_time_before_connect_click
            response["unique_customers"] = unique_customers
            response["repeated_customers"] = repeated_customers
            response["self_assign_count"] = self_assign_count
            response["average_self_assign_time"] = average_self_assign_time
            response["total_links_generated"] = total_links_generated
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentBasicAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentBasicAnalytics = GetAgentBasicAnalyticsAPI.as_view()


class GetAgentServiceRequestAnalyticsAPI(APIView):

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
                datetime_end = datetime.datetime.strptime(
                    end_date, date_format).date()
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
                is_lead=False, agent__in=agent_objs).exclude(cobrowsing_type="outbound-proxy-cobrowsing")

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            service_request_analytics = []
            if timeline == "daily":
                no_days = (datetime_end - datetime_start).days + 1
                for day in range(no_days):
                    temp_datetime = datetime_start + datetime.timedelta(day)

                    date_filtered_cobrowse_io_objs = cobrowse_io_objs.filter(
                        request_datetime__date=temp_datetime)

                    total_sr_not_initiated_after_request = EasyAssistCustomer.objects.filter(
                        access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date).filter(
                        request_datetime__date=temp_datetime).filter(
                        cobrowse_io=None).count()

                    time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=5)
                    total_sr_not_initiated_after_assigned = date_filtered_cobrowse_io_objs.filter(
                        Q(cobrowsing_start_datetime=None)).filter(request_datetime__lte=time_threshold).exclude(
                            session_archived_cause__in=["FOLLOWUP", "UNASSIGNED"]).count()

                    total_sr = date_filtered_cobrowse_io_objs.count()

                    total_sr_closed = date_filtered_cobrowse_io_objs.filter(
                        is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                    total_remaining_sr = date_filtered_cobrowse_io_objs.filter(
                        is_helpful=False).filter(~Q(cobrowsing_start_datetime=None)).count()

                    total_sr_attended = date_filtered_cobrowse_io_objs.filter(
                        ~Q(cobrowsing_start_datetime=None)).count()

                    service_request_analytics.append({
                        "label": str(temp_datetime.strftime("%d-%b-%y")),
                        "total_sr": total_sr,
                        "total_sr_closed": total_sr_closed,
                        "total_remaining_sr": total_remaining_sr,
                        "total_sr_attended": total_sr_attended,
                        "total_sr_not_initiated_after_request": total_sr_not_initiated_after_request,
                        "total_sr_not_initiated_after_assigned": total_sr_not_initiated_after_assigned
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

                    total_sr_not_initiated_after_request = EasyAssistCustomer.objects.filter(
                        access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date).filter(
                        request_datetime__date__gte=temp_start_datetime, request_datetime__date__lt=temp_end_datetime).filter(
                        cobrowse_io=None).count()

                    time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=5)
                    total_sr_not_initiated_after_assigned = date_filtered_cobrowse_io_objs.filter(
                        Q(cobrowsing_start_datetime=None)).filter(request_datetime__lte=time_threshold).exclude(
                            session_archived_cause__in=["FOLLOWUP", "UNASSIGNED"]).count()

                    total_sr = date_filtered_cobrowse_io_objs.count()
                    total_sr_closed = date_filtered_cobrowse_io_objs.filter(
                        is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()
                    total_remaining_sr = date_filtered_cobrowse_io_objs.filter(
                        is_helpful=False).filter(~Q(cobrowsing_start_datetime=None)).count()
                    total_sr_attended = date_filtered_cobrowse_io_objs.filter(
                        ~Q(cobrowsing_start_datetime=None)).count()

                    temp_start_datetime_str = temp_start_datetime.strftime(
                        "%d/%m")
                    temp_end_datetime_str = (
                        temp_end_datetime - datetime.timedelta(1)).strftime("%d/%m")

                    service_request_analytics.append({
                        "label": temp_start_datetime_str + "-" + temp_end_datetime_str,
                        "total_sr": total_sr,
                        "total_sr_closed": total_sr_closed,
                        "total_remaining_sr": total_remaining_sr,
                        "total_sr_attended": total_sr_attended,
                        "start_date": str(temp_start_datetime),
                        "end_date": str(temp_end_datetime - datetime.timedelta(1)),
                        "total_sr_not_initiated_after_request": total_sr_not_initiated_after_request,
                        "total_sr_not_initiated_after_assigned": total_sr_not_initiated_after_assigned
                    })
            elif timeline == "monthly":
                month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
                    r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days)).keys())

                for month in month_list:
                    temp_month = month_to_num_dict[month.split("-")[0]]
                    temp_year = int(month.split("-")[1])
                    date_filtered_cobrowse_io_objs = cobrowse_io_objs.filter(
                        request_datetime__date__month=temp_month, request_datetime__date__year=temp_year)

                    total_sr_not_initiated_after_request = EasyAssistCustomer.objects.filter(
                        access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date).filter(
                        request_datetime__date__month=temp_month, request_datetime__date__year=temp_year).filter(
                        cobrowse_io=None).count()

                    time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=5)
                    total_sr_not_initiated_after_assigned = date_filtered_cobrowse_io_objs.filter(
                        Q(cobrowsing_start_datetime=None)).filter(request_datetime__lte=time_threshold).exclude(
                            session_archived_cause__in=["FOLLOWUP", "UNASSIGNED"]).count()

                    total_sr = date_filtered_cobrowse_io_objs.count()
                    total_sr_closed = date_filtered_cobrowse_io_objs.filter(
                        is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()
                    total_remaining_sr = date_filtered_cobrowse_io_objs.filter(
                        is_helpful=False).filter(~Q(cobrowsing_start_datetime=None)).count()
                    total_sr_attended = date_filtered_cobrowse_io_objs.filter(
                        ~Q(cobrowsing_start_datetime=None)).count()

                    service_request_analytics.append({
                        "label": month,
                        "total_sr": total_sr,
                        "total_sr_closed": total_sr_closed,
                        "total_remaining_sr": total_remaining_sr,
                        "total_sr_attended": total_sr_attended,
                        "total_sr_not_initiated_after_request": total_sr_not_initiated_after_request,
                        "total_sr_not_initiated_after_assigned": total_sr_not_initiated_after_assigned
                    })
            else:
                logger.info("invalid timeline", extra={
                            'AppName': 'EasyAssist'})

            response["active_agent_role"] = active_agent.role
            response["service_request_analytics"] = service_request_analytics
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentServiceRequestAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentServiceRequestAnalytics = GetAgentServiceRequestAnalyticsAPI.as_view()


class ExportNotInitiatedCustomerDetailsAPI(APIView):

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

            sr_not_initiated_after_request = EasyAssistCustomer.objects.filter(
                access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                cobrowse_io=None)

            if sr_not_initiated_after_request != None and title != None:
                sr_not_initiated_after_request = sr_not_initiated_after_request.filter(
                    title=title)

            export_path = create_excel_easyassist_customer_details(
                active_agent, sr_not_initiated_after_request)

            if export_path:
                file_path = "/" + export_path
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)

                response["export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportNotInitiatedCustomerDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportNotInitiatedCustomerDetails = ExportNotInitiatedCustomerDetailsAPI.as_view()


class ExportConversionsByURLAPI(APIView):

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
            cobrowsing_type = data["cobrowsing_type"]
            cobrowsing_type = remo_html_from_string(cobrowsing_type)

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

            if active_agent.role in ["admin", "admin_ally"]:
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())

            is_reverse_cobrowsing = False
            is_lead = False

            if cobrowsing_type == "outbound":
                is_lead = True

            elif cobrowsing_type == "reverse":
                is_reverse_cobrowsing = True

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=is_reverse_cobrowsing).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=is_lead, agent__in=agent_objs).exclude(cobrowsing_type="outbound-proxy-cobrowsing")

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            if cobrowse_io_objs != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    is_helpful=True, is_archived=True, is_lead_converted_by_url=True).filter(~Q(cobrowsing_start_datetime=None))

            export_path = create_excel_easyassist_conversions_by_url(
                cobrowsing_type, active_agent, cobrowse_io_objs)

            if export_path:
                file_path = "/" + export_path
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)

                response["export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportConversionsByURLAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportConversionsByURL = ExportConversionsByURLAPI.as_view()


class GetCognoMeetBasicAnalyticsAPI(APIView):

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

            if active_agent.role in ["admin", "admin_ally"]:
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())
            else:
                agent_objs = [active_agent]

            cogno_vid_objs = CobrowseVideoConferencing.objects.filter(
                meeting_start_date__gte=datetime_start,
                meeting_start_date__lte=datetime_end, agent__in=agent_objs)

            total_meeting_scheduled = cogno_vid_objs.filter(
                is_cobrowsing_meeting=False).count()
            total_meeting_scheduled_by_customer = CobrowseIO.objects.filter(
                session_id__in=cogno_vid_objs.values_list('pk', flat=True))
            total_meeting_scheduled_by_greeting_bubble = total_meeting_scheduled_by_customer.filter(
                lead_initiated_by="greeting_bubble").count()
            total_meeting_scheduled_by_floating_button = total_meeting_scheduled_by_customer.filter(
                lead_initiated_by__in=["floating_button", "icon"]).count()
            total_meeting_scheduled_by_inactivity_popup = total_meeting_scheduled_by_customer.filter(
                lead_initiated_by="inactivity_popup").count()
            total_meeting_scheduled_by_exit_intent = total_meeting_scheduled_by_customer.filter(
                lead_initiated_by="exit_intent").count()

            total_meeting_completed = cogno_vid_objs.filter(
                is_expired=True).count()
            total_ongoing_meeting = analytics_ongoing_meeting_count(
                cogno_vid_objs, CobrowseVideoAuditTrail)
            avg_call_duration = 0
            self_assign_objs = CobrowseIO.objects.filter(is_meeting_only_session=True, request_datetime__date__gte=datetime_start,
                                                         request_datetime__date__lte=datetime_end, agent__in=agent_objs).filter(~Q(self_assign_time=None))
            self_assign_sessions = self_assign_objs.count()
            average_self_assign_time = get_average_self_assign_time(
                self_assign_sessions, self_assign_objs, True)

            for cogno_vid_obj in cogno_vid_objs:
                if cogno_vid_obj.is_expired == True:
                    try:
                        cogno_vid_audit_trail = CobrowseVideoAuditTrail.objects.get(
                            cobrowse_video=cogno_vid_obj.meeting_id)
                        avg_call_duration += cogno_vid_audit_trail.get_meeting_duration_in_seconds()
                    except Exception:
                        logger.warning("cogno video audit train object doesn't exist", extra={
                                       'AppName': 'EasyAssist'})
            try:
                avg_call_duration = avg_call_duration // (
                    total_meeting_completed * 60)
            except Exception:
                logger.warning("divide by zero", extra={
                               'AppName': 'EasyAssist'})

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                is_meeting_only_session=True).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=True)

            cobrowse_io_objs = cobrowse_io_objs.filter(agent__in=agent_objs)

            total_sr = cobrowse_io_objs.count()

            response["total_meeting_scheduled"] = total_meeting_scheduled
            response["total_meeting_completed"] = total_meeting_completed
            response["total_ongoing_meeting"] = total_ongoing_meeting
            response["total_meeting_scheduled_by_floating_button"] = total_meeting_scheduled_by_floating_button
            response["total_meeting_scheduled_by_greeting_bubble"] = total_meeting_scheduled_by_greeting_bubble
            response["total_meeting_scheduled_by_exit_intent"] = total_meeting_scheduled_by_exit_intent
            response["total_meeting_scheduled_by_inactivity_popup"] = total_meeting_scheduled_by_inactivity_popup
            response["avg_call_duration"] = avg_call_duration
            response["total_sr"] = total_sr
            response["self_assign_sessions"] = self_assign_sessions
            response["average_self_assign_time"] = average_self_assign_time
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCognoMeetBasicAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCognoMeetBasicAnalytics = GetCognoMeetBasicAnalyticsAPI.as_view()


class GetCognoMeetAnalyticsAPI(APIView):

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
                logger.error(
                    "Invalid start and end date. Select default start and end date:", extra={'AppName': 'EasyAssist'})

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            if active_agent.role in ["admin", "admin_ally"]:
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())
            else:
                agent_objs = [active_agent]

            cogno_vid_objs = CobrowseVideoConferencing.objects.filter(
                meeting_start_date__gte=datetime_start,
                meeting_start_date__lte=datetime_end, agent__in=agent_objs)

            cogno_meet_analytics = []
            if timeline == "daily":
                no_days = (datetime_end - datetime_start).days + 1
                for day in range(no_days):
                    temp_datetime = datetime_start + datetime.timedelta(day)

                    date_filtered_cogno_vid_objs = cogno_vid_objs.filter(
                        meeting_start_date=temp_datetime)

                    total_meeting_scheduled = date_filtered_cogno_vid_objs.filter(
                        is_cobrowsing_meeting=False).count()
                    total_meeting_completed = date_filtered_cogno_vid_objs.filter(
                        is_expired=True).count()
                    total_ongoing_meeting = analytics_ongoing_meeting_count(
                        date_filtered_cogno_vid_objs, CobrowseVideoAuditTrail)

                    cogno_meet_analytics.append({
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

                    date_filtered_cogno_vid_objs = cogno_vid_objs.filter(
                        meeting_start_date__gte=temp_start_datetime, meeting_start_date__lte=temp_end_datetime)

                    total_meeting_scheduled = date_filtered_cogno_vid_objs.count()
                    total_meeting_completed = date_filtered_cogno_vid_objs.filter(
                        is_expired=True).count()
                    total_ongoing_meeting = analytics_ongoing_meeting_count(
                        date_filtered_cogno_vid_objs, CobrowseVideoAuditTrail)

                    temp_start_datetime_str = temp_start_datetime.strftime(
                        "%d/%m")
                    temp_end_datetime_str = (
                        temp_end_datetime - datetime.timedelta(1)).strftime("%d/%m")

                    cogno_meet_analytics.append({
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

                    date_filtered_cogno_vid_objs = cogno_vid_objs.filter(
                        meeting_start_date__month=temp_month, meeting_start_date__year=temp_year)

                    total_meeting_scheduled = date_filtered_cogno_vid_objs.count()
                    total_meeting_completed = date_filtered_cogno_vid_objs.filter(
                        is_expired=True).count()
                    total_ongoing_meeting = analytics_ongoing_meeting_count(
                        date_filtered_cogno_vid_objs, CobrowseVideoAuditTrail)

                    cogno_meet_analytics.append({
                        "label": month,
                        "total_meeting_scheduled": total_meeting_scheduled,
                        "total_meeting_completed": total_meeting_completed,
                        "total_ongoing_meeting": total_ongoing_meeting,
                    })
            else:
                logger.info("invalid timeline", extra={
                            'AppName': 'EasyAssist'})

            response["cogno_meet_analytics"] = cogno_meet_analytics
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCognoMeetAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCognoMeetAnalytics = GetCognoMeetAnalyticsAPI.as_view()


class GetCognoMeetDailyTimeTrendAnalyticsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            today_date = datetime.datetime.today()
            start_time = datetime.datetime(
                today_date.year, today_date.month, today_date.day)
            end_time = start_time + datetime.timedelta(hours=1)
            today_date = today_date.date()

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            if active_agent.role in ["admin", "admin_ally"]:
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())
            else:
                agent_objs = [active_agent]

            cogno_vid_objs = CobrowseVideoConferencing.objects.filter(
                meeting_start_date=today_date, agent__in=agent_objs)

            current_hour = datetime.datetime.now().hour
            cogno_meet_daily_time_trend = []

            for hour in range(current_hour + 1):
                time_filtered_cogno_vid_objs = cogno_vid_objs.filter(
                    meeting_start_time__gte=start_time.time(), meeting_start_time__lte=end_time.time())

                total_ongoing_meeting = analytics_ongoing_meeting_count(
                    time_filtered_cogno_vid_objs, CobrowseVideoAuditTrail)
                cogno_meet_daily_time_trend.append({
                    "label": str(start_time.strftime("%-I %p")) + "-" + str(end_time.strftime("%-I %p")),
                    "total_ongoing_meeting": total_ongoing_meeting,
                })

                start_time = end_time
                end_time = end_time + datetime.timedelta(hours=1)

            response["cogno_meet_daily_time_trend"] = cogno_meet_daily_time_trend
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCognoMeetDailyTimeTrendAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCognoMeetDailyTimeTrendAnalytics = GetCognoMeetDailyTimeTrendAnalyticsAPI.as_view()


class GetAgentWiseCognoMeetAnalyticsAPI(APIView):

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
            agent_id = data["agent_id"]
            timeline = data["timeline"]

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
                logger.error(
                    "Invalid start and end date. Select default start and end date:", extra={'AppName': 'EasyAssist'})

            try:
                agent_objs = [CobrowseAgent.objects.get(pk=agent_id)]
            except Exception:
                logger.error("Agent not found", extra={
                             'AppName': 'EasyAssist'})
                agent_objs = []

            cogno_vid_objs = CobrowseVideoConferencing.objects.filter(
                meeting_start_date__gte=datetime_start,
                meeting_start_date__lte=datetime_end, agent__in=agent_objs)

            cogno_meet_agent_wise_analytics = []
            if timeline == "daily":
                no_days = (datetime_end - datetime_start).days + 1
                for day in range(no_days):
                    temp_datetime = datetime_start + datetime.timedelta(day)

                    date_filtered_cogno_vid_objs = cogno_vid_objs.filter(
                        meeting_start_date=temp_datetime)

                    total_meeting_scheduled = date_filtered_cogno_vid_objs.count()
                    total_meeting_completed = date_filtered_cogno_vid_objs.filter(
                        is_expired=True).count()

                    cogno_meet_agent_wise_analytics.append({
                        "label": str(temp_datetime.strftime("%d-%b-%y")),
                        "total_meeting_scheduled": total_meeting_scheduled,
                        "total_meeting_completed": total_meeting_completed,
                    })
            elif timeline == "weekly":
                no_days = (datetime_end - datetime_start).days
                no_weeks = int(no_days / 7.0) + 1

                for week in range(no_weeks):
                    temp_start_datetime = datetime_start + \
                        datetime.timedelta(week * 7)
                    temp_end_datetime = datetime_start + \
                        datetime.timedelta((week + 1) * 7)

                    date_filtered_cogno_vid_objs = cogno_vid_objs.filter(
                        meeting_start_date__gte=temp_start_datetime, meeting_start_date__lte=temp_end_datetime)

                    total_meeting_scheduled = date_filtered_cogno_vid_objs.count()
                    total_meeting_completed = date_filtered_cogno_vid_objs.filter(
                        is_expired=True).count()

                    temp_start_datetime_str = temp_start_datetime.strftime(
                        "%d/%m")
                    temp_end_datetime_str = (
                        temp_end_datetime - datetime.timedelta(1)).strftime("%d/%m")

                    cogno_meet_agent_wise_analytics.append({
                        "label": temp_start_datetime_str + "-" + temp_end_datetime_str,
                        "start_date": str(temp_start_datetime),
                        "end_date": str(temp_end_datetime - datetime.timedelta(1)),
                        "total_meeting_scheduled": total_meeting_scheduled,
                        "total_meeting_completed": total_meeting_completed,
                    })
            elif timeline == "monthly":
                month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
                    r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days)).keys())

                for month in month_list:
                    temp_month = month_to_num_dict[month.split("-")[0]]
                    temp_year = int(month.split("-")[1])

                    date_filtered_cogno_vid_objs = cogno_vid_objs.filter(
                        meeting_start_date__month=temp_month, meeting_start_date__year=temp_year)

                    total_meeting_scheduled = date_filtered_cogno_vid_objs.count()
                    total_meeting_completed = date_filtered_cogno_vid_objs.filter(
                        is_expired=True).count()

                    cogno_meet_agent_wise_analytics.append({
                        "label": month,
                        "total_meeting_scheduled": total_meeting_scheduled,
                        "total_meeting_completed": total_meeting_completed,
                    })
            else:
                logger.info("invalid timeline", extra={
                            'AppName': 'EasyAssist'})

            response[
                "cogno_meet_agent_wise_analytics"] = cogno_meet_agent_wise_analytics
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentWiseCognoMeetAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentWiseCognoMeetAnalytics = GetAgentWiseCognoMeetAnalyticsAPI.as_view()


class GetCognoMeetCobrowsingAnalyticsAPI(APIView):

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
                logger.error(
                    "Invalid start and end date. Select default start and end date:", extra={'AppName': 'EasyAssist'})

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            agent_objs = [active_agent]

            if active_agent.role in ["admin", "admin_ally"]:
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                agent__in=agent_objs)

            cobrowsing_requests = cobrowse_io_objs.filter(
                allow_agent_cobrowse='true')
            meeting_requests = cobrowse_io_objs.filter(
                allow_agent_meeting='true')

            cobrowsing_request_count = 0
            meeting_request_count = 0

            for cobrowsing_request in cobrowsing_requests:
                if cobrowsing_request.allow_agent_meeting == "true":
                    cobrowsing_start_datetime = cobrowsing_request.cobrowsing_start_datetime
                    meeting_start_datetime = cobrowsing_request.meeting_start_datetime

                    if cobrowsing_start_datetime != None and (meeting_start_datetime == None or cobrowsing_start_datetime < meeting_start_datetime):
                        cobrowsing_request_count += 1

                else:
                    cobrowsing_request_count += 1

            for meeting_request in meeting_requests:
                if meeting_request.allow_agent_cobrowse == "true":
                    cobrowsing_start_datetime = meeting_request.cobrowsing_start_datetime
                    meeting_start_datetime = meeting_request.meeting_start_datetime

                    if meeting_start_datetime != None and (cobrowsing_start_datetime == None or cobrowsing_start_datetime > meeting_start_datetime):
                        meeting_request_count += 1
                else:
                    meeting_request_count += 1

            response["cogno_meet_cobrowsing_analytics"] = {
                "meeting_request_count": meeting_request_count,
                "cobrowsing_request_count": cobrowsing_request_count
            }
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentWiseCognoMeetAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCognoMeetCobrowsingAnalytics = GetCognoMeetCobrowsingAnalyticsAPI.as_view()


class GetGeneralVisitedPageTitleListAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetGeneralVisitedPageTitleListAPI",
                        extra={'AppName': 'EasyAssist'})
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                ~Q(title=None))

            query_pages = list(
                set(list(cobrowse_io_objs.values_list('title', flat=True))))

            response["status"] = 200
            response["message"] = "success"
            response["query_pages"] = query_pages
            response["active_agent_role"] = active_agent.role
            logger.info("Successfully exited from GetGeneralVisitedPageTitleListAPI", extra={
                        'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RequestCobrowsingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetGeneralVisitedPageTitleList = GetGeneralVisitedPageTitleListAPI.as_view()


class GetGeneralAnalyticsDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            logger.info("Inside GetGeneralAnalyticsDetailsAPI ",
                        extra={'AppName': 'EasyAssistApp'})

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

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

            agent_objs = [active_agent]
            if active_agent.role in ["admin", "admin_ally"]:
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())

            total_inbound_request_initiated = 0
            total_outbound_request_initiated = 0
            total_inbound_request_attended = 0
            total_outbound_request_attended = 0
            total_inbound_request_converted = 0
            total_outbound_request_converted = 0
            inbound_nps_score = 0
            outbound_nps_score = 0

            inbound_cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False, agent__in=agent_objs).exclude(cobrowsing_type="outbound-proxy-cobrowsing")

            outbound_cobrowse_io_objs = CobrowseIO.objects.filter(
                is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=True, agent__in=agent_objs)

            agent_objs = [active_agent]

            if active_agent.role in ["admin", "admin_ally"]:
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())

            if inbound_cobrowse_io_objs != None:

                if(title != None):
                    inbound_cobrowse_io_objs = inbound_cobrowse_io_objs.filter(
                        title=title)

                total_inbound_request_initiated = inbound_cobrowse_io_objs.count()

                total_inbound_request_attended = inbound_cobrowse_io_objs.filter(
                    ~Q(cobrowsing_start_datetime=None)).count()

                total_inbound_request_converted = inbound_cobrowse_io_objs.filter(
                    ~Q(cobrowsing_start_datetime=None)).filter(is_helpful=True, is_archived=True).count()

                total_sr_closed = inbound_cobrowse_io_objs.filter(
                    is_archived=True).filter(~Q(agent_rating=None)).count()

                if total_sr_closed != 0:
                    promoter_count = inbound_cobrowse_io_objs.filter(
                        is_archived=True, agent_rating__gte=9).count()
                    detractor_count = inbound_cobrowse_io_objs.filter(
                        is_archived=True, agent_rating__lte=6).count()

                    inbound_nps_score = (
                        (promoter_count - detractor_count) * 100) / total_sr_closed
                    inbound_nps_score = round(inbound_nps_score, 2)

            if outbound_cobrowse_io_objs != None:

                if(title != None):
                    outbound_cobrowse_io_objs = outbound_cobrowse_io_objs.filter(
                        title=title)

                total_outbound_request_initiated = outbound_cobrowse_io_objs.count()

                total_outbound_request_attended = outbound_cobrowse_io_objs.filter(
                    ~Q(cobrowsing_start_datetime=None)).count()

                total_outbound_request_converted = outbound_cobrowse_io_objs.filter(
                    ~Q(cobrowsing_start_datetime=None)).filter(is_helpful=True, is_archived=True).count()

                total_sr_closed = outbound_cobrowse_io_objs.filter(
                    is_archived=True).filter(~Q(agent_rating=None)).count()

                if total_sr_closed != 0:
                    promoter_count = outbound_cobrowse_io_objs.filter(
                        is_archived=True, agent_rating__gte=9).count()
                    detractor_count = outbound_cobrowse_io_objs.filter(
                        is_archived=True, agent_rating__lte=6).count()
                    outbound_nps_score = (
                        (promoter_count - detractor_count) * 100) / total_sr_closed
                    outbound_nps_score = round(outbound_nps_score, 2)

            response["total_inbound_request_initiated"] = total_inbound_request_initiated
            response["total_outbound_request_initiated"] = total_outbound_request_initiated
            response["total_inbound_request_attended"] = total_inbound_request_attended
            response["total_outbound_request_attended"] = total_outbound_request_attended
            response["total_inbound_request_converted"] = total_inbound_request_converted
            response["total_outbound_request_converted"] = total_outbound_request_converted
            response["inbound_nps_score"] = inbound_nps_score
            response["outbound_nps_score"] = outbound_nps_score
            response['status'] = 200
            logger.info("Successfully exited from GetGeneralAnalyticsDetailsAPI", extra={
                        'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetGeneralAnalyticsDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetGeneralAnalyticsDetails = GetGeneralAnalyticsDetailsAPI.as_view()


class ExportInboundAnalyticsAPI(APIView):

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
                start_date = datetime.datetime.now() - datetime.timedelta(days=1)
                start_date = start_date.strftime(date_format)
                end_date = start_date

                export_path = "/secured_files/EasyAssistApp/InboundAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/inbound_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "2":

                start_date = datetime.datetime.now() - datetime.timedelta(days=7)
                start_date = start_date.strftime(date_format)
                end_date = datetime.datetime.now() - datetime.timedelta(days=1)
                end_date = end_date.strftime(date_format)

                export_path = "/secured_files/EasyAssistApp/InboundAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/inbound_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "3":

                start_date = datetime.datetime.now() - datetime.timedelta(days=30)
                start_date = start_date.strftime(date_format)
                end_date = datetime.datetime.now() - datetime.timedelta(days=1)
                end_date = end_date.strftime(date_format)

                export_path = "/secured_files/EasyAssistApp/InboundAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/inbound_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "4":

                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()

                today_date = datetime.datetime.today().date()

                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='inbound-analytics', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                else:
                    export_path = get_inbound_analytics_data_dump(
                        requested_data, cobrowse_agent, CobrowseDateWiseInboundAnalytics, CobrowseDateWiseOutboundDroplinkAnalytics)

            if os.path.exists(export_path[1:]) == True:
                if get_save_in_s3_bucket_status():
                    if requested_data["selected_filter_value"] == "4":
                        key = s3_bucket_upload_file_by_file_path(
                            export_path[1:], "/inbound_analytics_" + requested_data["startdate"] + "-" + requested_data["enddate"] + ".xls")
                    else:
                        key = s3_bucket_upload_file_by_file_path(
                            export_path[1:], "/inbound_analytics_" + str(start_date) + "-" + str(end_date) + ".xls")
                    s3_file_path = s3_bucket_download_file(
                        key, 'EasyAssistApp/InboundAnalytics/', '.xls')
                    export_path = "/" + s3_file_path.split("EasyChat/", 1)[1]

                response["export_path_exist"] = True
                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=export_path, is_public=False, access_token=cobrowse_agent.get_access_token_obj())
                response["export_path"] = 'easy-assist/download-file/' + \
                    str(file_access_management_obj.key)
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportInboundAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportInboundAnalytics = ExportInboundAnalyticsAPI.as_view()


class ExportGeneralAnalyticsAPI(APIView):
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

                start_date = datetime.datetime.now() - datetime.timedelta(days=1)
                start_date = start_date.strftime(date_format)
                end_date = start_date

                export_path = "/secured_files/EasyAssistApp/GeneralAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/general_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "2":

                start_date = datetime.datetime.now() - datetime.timedelta(days=7)
                start_date = start_date.strftime(date_format)
                end_date = datetime.datetime.now() - datetime.timedelta(days=1)
                end_date = end_date.strftime(date_format)

                export_path = "/secured_files/EasyAssistApp/GeneralAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/general_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "3":

                start_date = datetime.datetime.now() - datetime.timedelta(days=30)
                start_date = start_date.strftime(date_format)
                end_date = datetime.datetime.now() - datetime.timedelta(days=1)
                end_date = end_date.strftime(date_format)

                export_path = "/secured_files/EasyAssistApp/GeneralAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/general_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "4":

                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()

                today_date = datetime.datetime.today().date()

                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='general-analytics', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                else:
                    export_path = get_general_analytics_data_dump(
                        requested_data, cobrowse_agent, CobrowseDateWiseInboundAnalytics, CobrowseDateWiseOutboundAnalytics, CobrowseDateWiseOutboundDroplinkAnalytics)

            if os.path.exists(export_path[1:]) == True:
                if get_save_in_s3_bucket_status():
                    if requested_data["selected_filter_value"] == "4":
                        key = s3_bucket_upload_file_by_file_path(
                            export_path[1:], "/general_analytics_" + requested_data["startdate"] + "-" + requested_data["enddate"] + ".xls")
                    else:
                        key = s3_bucket_upload_file_by_file_path(
                            export_path[1:], "/general_analytics_" + str(start_date) + "-" + str(end_date) + ".xls")
                    s3_file_path = s3_bucket_download_file(
                        key, 'EasyAssistApp/GeneralAnalytics/', '.xls')
                    export_path = "/" + s3_file_path.split("EasyChat/", 1)[1]
                response["export_path_exist"] = True
                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=export_path, is_public=False, access_token=cobrowse_agent.get_access_token_obj())
                response["export_path"] = 'easy-assist/download-file/' + \
                    str(file_access_management_obj.key)
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportGeneralAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportGeneralAnalytics = ExportGeneralAnalyticsAPI.as_view()


class ExportInboundUniqueCustomersAPI(APIView):

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

            requested_data = {
                "start_date": start_date,
                "end_date": end_date,
            }

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()
            agent_objs = [active_agent]
            if active_agent.role == "admin":
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)

            cobrowse_io_objs = CobrowseIO.objects.filter(is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                is_lead=False, agent__in=agent_objs).exclude(cobrowsing_type="outbound-proxy-cobrowsing")
       
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
                "inbound", active_agent, cobrowse_io_objs, access_token_obj, requested_data)

            if export_path:
                file_path = "/" + export_path
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)

                response["export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportUniqueCustomersAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportInboundUniqueCustomers = ExportInboundUniqueCustomersAPI.as_view()


class ExportInboundRepeatedCustomersAPI(APIView):

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
                is_lead=False, agent__in=agent_objs).exclude(cobrowsing_type="outbound-proxy-cobrowsing")

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
                "inbound", cobrowse_io_objs, active_agent, data)

            if export_path:
                file_path = "/" + export_path
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)

                response["export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportRepeatedCustomersAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportInboundRepeatedCustomers = ExportInboundRepeatedCustomersAPI.as_view()


class ExportCronRequestUniqueCustomersInboundAPI(APIView):

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
                report_type="inbound-unique-customers", agent=active_agent, filter_param=json.dumps(data))
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportCronRequestUniqueCustomersInboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportCronRequestUniqueCustomersInbound = ExportCronRequestUniqueCustomersInboundAPI.as_view()


class ExportCronRequestRepeatedCustomersInboundAPI(APIView):

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
                report_type="inbound-repeated-customers", agent=active_agent, filter_param=json.dumps(data))
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportCronRequestRepeatedCustomersInboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportCronRequestRepeatedCustomersInbound = ExportCronRequestRepeatedCustomersInboundAPI.as_view()


class DownloadGeneratedLinksAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = get_active_agent_obj(request, CobrowseAgent)

            if active_agent.role == "agent":
                response['status'] = 400
                response["message"] = "You do not have access for this"
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            start_date = data["startdate"]
            start_date = remo_html_from_string(start_date)
            end_date = data["enddate"]
            end_date = remo_html_from_string(end_date)

            title = None
            if "title" in data and data["title"] != "all":
                title = data["title"]
                title = remo_html_from_string(title)

            try:
                date_format = "%Y-%m-%d"
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                datetime_end = datetime.datetime.strptime(
                    end_date, date_format).date()
            except Exception:
                pass

            access_token_obj = active_agent.get_access_token_obj()
            agent_list = [active_agent]
            if active_agent.role in ["admin", "admin_ally"]:
                agent_list = get_list_agents_under_admin(
                    active_agent, is_active=None, is_account_active=None)
            else:
                agent_list = list(active_agent.agents.all())

            requested_data = {
                "startdate": start_date,
                "enddate": end_date,
            }

            drop_link_objs = CobrowseDropLink.objects.filter(agent__in=agent_list, generate_datetime__date__gte=access_token_obj.go_live_date).filter(
                generate_datetime__date__gte=datetime_start, generate_datetime__date__lte=datetime_end, proxy_cobrowse_io=None).order_by("generate_datetime")
            if drop_link_objs.count() > EXPORTS_UPPER_CAP_LIMIT:
                response["status"] = 302
                response["message"] = "Export upper limit reached"
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

            export_path = get_generated_link_data_dump(requested_data, active_agent, CobrowseDropLink, drop_link_objs)

            if export_path == NO_DATA:
                response["status"] = 301
                response["message"] = "No data found"
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

            if export_path != "None":
                file_path = "/" + export_path
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)

                response["export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DownloadGeneratedLinksAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DownloadGeneratedLinks = DownloadGeneratedLinksAPI.as_view()


class ExportGeneratedDropLinksAPI(APIView):

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

            cobrowse_agent = get_active_agent_obj(request, CobrowseAgent)

            if cobrowse_agent.role == "agent":
                response["export_path"] = "None"
                response["status"] = 400
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

            if requested_data["selected_filter_value"] == "1":

                export_path = get_generated_link_data_dump(get_requested_data_for_daily(), cobrowse_agent, CobrowseDropLink)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "2":

                export_path = get_generated_link_data_dump(get_requested_data_for_week(), cobrowse_agent, CobrowseDropLink)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "3":

                export_path = get_generated_link_data_dump(get_requested_data_for_month(), cobrowse_agent, CobrowseDropLink)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "4":

                date_format = DATE_TIME_FORMAT
                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()
                today_date = datetime.datetime.today().date()

                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='droplink-urls-generated', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                else:
                    end_date = datetime.datetime.strptime(
                        requested_data["enddate"], date_format).date()                

                    if cobrowse_agent.role in ["admin", "admin_ally"]:
                        agent_objs = get_list_agents_under_admin(
                            cobrowse_agent, is_active=None, is_account_active=None)
                    elif cobrowse_agent.role == "supervisor":
                        agent_objs = list(cobrowse_agent.agents.all())

                    access_token_obj = cobrowse_agent.get_access_token_obj()
                    drop_link_objs = CobrowseDropLink.objects.filter(agent__in=agent_objs, generate_datetime__date__gte=access_token_obj.go_live_date).filter(
                        generate_datetime__date__gte=start_date, generate_datetime__date__lte=end_date, proxy_cobrowse_io=None).order_by("generate_datetime")

                    if not drop_link_objs:
                        return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

                    if drop_link_objs.count() > EXPORTS_UPPER_CAP_LIMIT:

                        EasyAssistExportDataRequest.objects.create(
                            report_type='droplink-urls-generated', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                        response["status"] = 300
                        response["export_path"] = "None"
                        response["export_path_exist"] = False
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                    else:
                        export_path = get_generated_link_data_dump(requested_data, cobrowse_agent, CobrowseDropLink, drop_link_objs)

            if os.path.exists(export_path[1:]):
                response["export_path_exist"] = True
                file_path = "/" + export_path
                access_token_obj = cobrowse_agent.get_access_token_obj()
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)
                response["export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportGeneratedDropLinksAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


ExportGeneratedDropLinks = ExportGeneratedDropLinksAPI.as_view()
