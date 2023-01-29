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
from EasyAssistSalesforceApp.models import *
from EasyAssistSalesforceApp.utils import *
# from EasyAssistApp.views_table import *
from EasyAssistSalesforceApp.send_email import send_password_over_email

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

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetVisitedPageTitleListOutboundAPI",
                        extra={'AppName': 'EasyAssistSalesforce'})
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            if active_agent.role == "admin":
                active_admin_user = active_agent
            else:
                active_admin_user = get_admin_from_active_agent(
                    active_agent, CobrowseAgent)

            cobrowse_io_objs = CobrowseIO.objects.filter(is_lead=True, is_test=False,
                                                         access_token__agent=active_admin_user).filter(~Q(title=None))

            query_pages = list(
                set(list(cobrowse_io_objs.values_list('title', flat=True))))

            response["status"] = 200
            response["message"] = "success"
            response["query_pages"] = query_pages
            response["active_agent_role"] = active_agent.role
            logger.info("Successfully exited from GetVisitedPageTitleListOutboundAPI", extra={
                        'AppName': 'EasyAssistSalesforce'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RequestCobrowsingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetVisitedPageTitleListOutbound = GetVisitedPageTitleListOutboundAPI.as_view()


class GetQueryPageAnalyticsOutboundAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetQueryPageAnalyticsOutboundAPI",
                        extra={'AppName': 'EasyAssistSalesforce'})
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
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

            access_token_obj = active_agent.get_access_token_obj()

            if active_agent.role == "admin":
                active_admin_user = active_agent
            else:
                active_admin_user = get_admin_from_active_agent(
                    active_agent, CobrowseAgent)

            cobrowse_io_objs = CobrowseIO.objects.filter(is_lead=True, is_archived=True, is_test=False, access_token__agent=active_admin_user,
                                                         request_datetime__date__lte=datetime_end, request_datetime__date__gte=datetime_start).filter(
                ~Q(cobrowsing_start_datetime=None)).filter(
                request_datetime__date__gte=access_token_obj.go_live_date)

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            query_pages = []

            if active_agent.role == "admin" or active_agent.role == "supervisor":

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
                        'AppName': 'EasyAssistSalesforce'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetQueryPageAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetQueryPageAnalyticsOutbound = GetQueryPageAnalyticsOutboundAPI.as_view()


class GetAgentWiseRequestAnalyticsOutboundAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetAgentWiseRequestAnalyticsOutboundAPI",
                        extra={'AppName': 'EasyAssistSalesforce'})
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
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

            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = CobrowseIO.objects.filter(is_lead=True, is_test=False, request_datetime__date__gte=datetime_start,
                                                         request_datetime__date__lte=datetime_end).filter(
                request_datetime__date__gte=access_token_obj.go_live_date)

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            agent_request_analytics_list, agent_objs = [], []
            agent_objs = []

            if active_agent.role == "admin":
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())
            else:
                logger.info("Invalid User Access", extra={
                            'AppName': 'EasyAssistSalesforce'})

            for agent in agent_objs:
                total_sr = cobrowse_io_objs.filter(agent=agent).count()

                total_sr_closed = cobrowse_io_objs.filter(
                    agent=agent, is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                total_sr_attended = cobrowse_io_objs.filter(
                    agent=agent).filter(~Q(cobrowsing_start_datetime=None)).count()

                total_sr_customer_denied = cobrowse_io_objs.filter(
                    agent=agent, consent_cancel_count__gte=1, cobrowsing_start_datetime=None).count()

                agent_request_analytics_list.append({
                    "agent": agent.user.username,
                    "total_sr": total_sr,
                    "total_sr_closed": total_sr_closed,
                    "total_sr_attended": total_sr_attended,
                    "total_sr_customer_denied": total_sr_customer_denied
                })

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
                        'AppName': 'EasyAssistSalesforce'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentWiseRequestAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentWiseRequestAnalyticsOutbound = GetAgentWiseRequestAnalyticsOutboundAPI.as_view()


class GetAgentNPSAnalyticsOutboundAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetAgentNPSAnalyticsOutboundAPI",
                        extra={'AppName': 'EasyAssistSalesforce'})
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
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

            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = CobrowseIO.objects.filter(is_lead=True, is_test=False, request_datetime__date__gte=datetime_start,
                                                         request_datetime__date__lte=datetime_end).filter(
                ~Q(cobrowsing_start_datetime=None)).filter(
                request_datetime__date__gte=access_token_obj.go_live_date)

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            agent_nps_analytics_list, agent_objs = [], []

            if active_agent.role == "admin":
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())
            else:
                logger.info("Invalid User Access", extra={
                            'AppName': 'EasyAssistSalesforce'})

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
                        'AppName': 'EasyAssistSalesforce'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentNPSAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentNPSAnalyticsOutbound = GetAgentNPSAnalyticsOutboundAPI.as_view()


class GetAgentBasicAnalyticsOutboundAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetAgentBasicAnalyticsOutboundAPI",
                        extra={'AppName': 'EasyAssistSalesforce'})
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
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

            access_token_obj = active_agent.get_access_token_obj()

            total_sr = 0
            total_sr_closed = 0
            total_sr_attended = 0
            total_sr_lead_captured = 0
            total_sr_customer_denied = 0
            cobrowse_io_objs = None

            agent_objs = [active_agent]

            if active_agent.role == "admin":
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None)
                cobrowse_io_objs = CobrowseIO.objects.filter(is_lead=True, is_test=False, request_datetime__date__gte=datetime_start,
                                                             request_datetime__date__lte=datetime_end).filter(
                    request_datetime__date__gte=access_token_obj.go_live_date)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())
                cobrowse_io_objs = CobrowseIO.objects.filter(is_lead=True, is_test=False, request_datetime__date__gte=datetime_start,
                                                             request_datetime__date__lte=datetime_end).filter(
                    request_datetime__date__gte=access_token_obj.go_live_date)
            else:
                cobrowse_io_objs = CobrowseIO.objects.filter(is_lead=True, is_test=False, request_datetime__date__gte=datetime_start,
                                                             request_datetime__date__lte=datetime_end).filter(
                    request_datetime__date__gte=access_token_obj.go_live_date)

            if cobrowse_io_objs != None and title != None:
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

            # total cobrowsing lead captured
            total_sr_lead_captured = cobrowse_io_objs.filter(
                access_token=access_token_obj).count()

            cobrowse_io_objs = cobrowse_io_objs.filter(agent__in=agent_objs)

            nps = "..."
            if cobrowse_io_objs != None:
                # total cobrowsing request Initiated/Notinitiated
                total_sr = cobrowse_io_objs.count()

                # total cobrowsing request initiated and converted successfully
                total_sr_closed = cobrowse_io_objs.filter(
                    is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                # total cobrowsing request attended
                total_sr_attended = cobrowse_io_objs.filter(
                    ~Q(cobrowsing_start_datetime=None)).count()

                # total cobrowsing request denied by customer
                total_sr_customer_denied = cobrowse_io_objs.filter(
                    consent_cancel_count__gte=1, cobrowsing_start_datetime=None).count()

                total_sr_nps = cobrowse_io_objs.filter(
                    is_archived=True).filter(~Q(agent_rating=None)).filter(~Q(cobrowsing_start_datetime=None)).count()

                if total_sr_nps != 0:
                    promoter_count = cobrowse_io_objs.filter(
                        is_archived=True, agent_rating__gte=9).filter(~Q(cobrowsing_start_datetime=None)).count()
                    detractor_count = cobrowse_io_objs.filter(
                        is_archived=True, agent_rating__lte=6).filter(~Q(cobrowsing_start_datetime=None)).count()
                    nps = ((promoter_count - detractor_count) * 100) / total_sr_nps
                    nps = round(nps, 2)

            response["total_sr"] = total_sr
            response["total_sr_closed"] = total_sr_closed
            response["total_sr_attended"] = total_sr_attended
            response["total_sr_lead_captured"] = total_sr_lead_captured
            response["total_sr_customer_denied"] = total_sr_customer_denied
            response["nps"] = nps
            response["status"] = 200
            logger.info("Successfully exited from GetAgentBasicAnalyticsOutboundAPI", extra={
                        'AppName': 'EasyAssistSalesforce'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentBasicAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentBasicAnalyticsOutbound = GetAgentBasicAnalyticsOutboundAPI.as_view()


class GetAgentServiceRequestAnalyticsOutboundAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetAgentServiceRequestAnalyticsOutboundAPI",
                        extra={'AppName': 'EasyAssistSalesforce'})
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
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
                    "Invalid start and end date. Select default start and end date:", extra={'AppName': 'EasyAssistSalesforce'})

            access_token_obj = active_agent.get_access_token_obj()

            cobrowse_io_objs = None

            agent_objs = [active_agent]

            if active_agent.role == "admin":
                agent_objs = get_list_agents_under_admin(
                    active_agent, is_active=None)
                cobrowse_io_objs = CobrowseIO.objects.filter(is_lead=True, is_test=False, request_datetime__date__gte=datetime_start,
                                                             request_datetime__date__lte=datetime_end).filter(
                    request_datetime__date__gte=access_token_obj.go_live_date)
            elif active_agent.role == "supervisor":
                agent_objs = list(active_agent.agents.all())
                cobrowse_io_objs = CobrowseIO.objects.filter(is_lead=True, is_test=False, request_datetime__date__gte=datetime_start,
                                                             request_datetime__date__lte=datetime_end).filter(
                    request_datetime__date__gte=access_token_obj.go_live_date)
            else:
                cobrowse_io_objs = CobrowseIO.objects.filter(is_lead=True, is_test=False, request_datetime__date__gte=datetime_start,
                                                             request_datetime__date__lte=datetime_end).filter(
                    request_datetime__date__gte=access_token_obj.go_live_date)

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
                        consent_cancel_count__gte=1, cobrowsing_start_datetime=None).count()

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
                        consent_cancel_count__gte=1, cobrowsing_start_datetime=None).count()

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
                        consent_cancel_count__gte=1, cobrowsing_start_datetime=None).count()

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
                            'AppName': 'EasyAssistSalesforce'})

            response["active_agent_role"] = active_agent.role
            response["service_request_analytics"] = service_request_analytics
            response["status"] = 200
            logger.info("Successfully exited from GetAgentServiceRequestAnalyticsOutboundAPI", extra={
                        'AppName': 'EasyAssistSalesforce'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentServiceRequestAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentServiceRequestAnalyticsOutbound = GetAgentServiceRequestAnalyticsOutboundAPI.as_view()
