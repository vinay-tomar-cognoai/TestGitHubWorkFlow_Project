from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
from EasyChatApp.models import User
from EasyAssistApp.models import *
from EasyAssistApp.proxy_cobrowse_analytics_utils import *
from EasyAssistApp.views_table import *
from DeveloperConsoleApp.utils import *
from DeveloperConsoleApp.utils_aws_s3 import *

import sys
import json
import logging
import datetime

from collections import OrderedDict

logger = logging.getLogger(__name__)


class GetOutboundProxyAnalyticsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()
            if access_token_obj.get_proxy_config_obj().enable_proxy_cobrowsing:
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
                    date_format = "%Y-%m-%d"
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
                cobrowse_io_objs = CobrowseIO.objects.filter(
                    agent__in=agent_objs, is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                    request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                    is_lead=False, cobrowsing_type="outbound-proxy-cobrowsing")

                total_customer_converted = 0
                total_customer_converted_by_url = 0
                total_unique_customers = 0
                total_repeated_customers = 0
                total_links_generated = 0
                total_customer_joined = 0
                avg_session_duration = 0
                avg_wait_time = 0
                avg_wait_time_unattended = 0
                nps = 0

                if cobrowse_io_objs:
                    drop_link_obj = CobrowseDropLink.objects.filter(
                        agent__in=agent_objs, generate_datetime__date__gte=datetime_start, generate_datetime__date__lte=datetime_end)
                    total_links_generated = drop_link_obj.filter(
                        ~Q(proxy_cobrowse_io=None)).count()
                    total_customer_joined = cobrowse_io_objs.count()

                    cobrowse_io_initiated = cobrowse_io_objs.filter(
                        ~Q(cobrowsing_start_datetime=None))
                    avg_session_duration = 0
                    avg_wait_time = 0

                    for cobrowse_io in cobrowse_io_initiated:
                        avg_session_duration += cobrowse_io.session_time_in_seconds()
                        avg_wait_time += cobrowse_io.customer_wait_time_in_seconds()
                    if total_customer_joined:
                        avg_session_duration = avg_session_duration / (
                            total_customer_joined * 60)
                        avg_wait_time = avg_wait_time / (
                            total_customer_joined * 60)

                    cobrowse_io_not_initiated = cobrowse_io_objs.filter(
                        Q(cobrowsing_start_datetime=None))
                    total_sr_unattended = cobrowse_io_not_initiated.count()
                    avg_wait_time_unattended = 0
                    for cobrowse_io in cobrowse_io_not_initiated:
                        avg_wait_time_unattended += cobrowse_io.customer_wait_time_in_seconds()
                    if total_sr_unattended:
                        avg_wait_time_unattended = avg_wait_time_unattended / (
                            total_sr_unattended * 60)

                    total_customer_converted = cobrowse_io_objs.filter(
                        is_helpful=True, is_archived=True, is_lead_converted_by_url=False).filter(~Q(cobrowsing_start_datetime=None)).count()

                    total_customer_converted_by_url = cobrowse_io_objs.filter(
                        is_helpful=True, is_archived=True, is_lead_converted_by_url=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                    total_unique_customers = cobrowse_io_objs.values(
                        'mobile_number').annotate(mobile_number_count=Count('mobile_number')).filter(mobile_number_count=1).count()

                    total_repeated_customers = cobrowse_io_objs.values(
                        'mobile_number').annotate(mobile_number_count=Count('mobile_number')).filter(mobile_number_count__gt=1).count()

                    nps_obj = cobrowse_io_objs.filter(
                        is_archived=True).filter(~Q(agent_rating=None)).filter(~Q(cobrowsing_start_datetime=None)).count()

                    if nps_obj:
                        promoter_count = cobrowse_io_objs.filter(
                            is_archived=True, agent_rating__gte=9).filter(~Q(cobrowsing_start_datetime=None)).count()
                        detractor_count = cobrowse_io_objs.filter(
                            is_archived=True, agent_rating__lte=6).filter(~Q(cobrowsing_start_datetime=None)).count()
                        nps = ((promoter_count - detractor_count) * 100) / nps_obj
                        nps = round(nps)

                response["total_customer_converted"] = total_customer_converted
                response["total_customer_converted_by_url"] = total_customer_converted_by_url
                response["total_unique_customers"] = total_unique_customers
                response["total_repeated_customers"] = total_repeated_customers
                response["total_links_generated"] = total_links_generated
                response["total_customer_joined"] = total_customer_joined
                response["avg_session_duration"] = avg_session_duration
                response["nps"] = nps
                response["avg_wait_time"] = avg_wait_time
                response["avg_wait_time_unattended"] = avg_wait_time_unattended
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetOutboundProxyAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


GetOutboundProxyAnalytics = GetOutboundProxyAnalyticsAPI.as_view()


class GetAgentProxyServiceRequestAnalyticsOutboundAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetAgentProxyServiceRequestAnalyticsOutboundAPI", extra={
                        'AppName': 'EasyAssist'})

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            if access_token_obj.get_proxy_config_obj().enable_proxy_cobrowsing:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                start_date = data["start_date"]
                start_date = remo_html_from_string(start_date)
                end_date = data["end_date"]
                end_date = remo_html_from_string(end_date)
                timeline = data["timeline"]
                timeline = remo_html_from_string(timeline)

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
                    date_format = "%Y-%m-%d"
                    datetime_start = datetime.datetime.strptime(
                        start_date, date_format).date()
                    datetime_end = datetime.datetime.strptime(
                        end_date, date_format).date()
                except Exception:
                    logger.error(
                        "In GetAgentProxyServiceRequestAnalyticsOutboundAPI invalid start and end date. Select default start and end date:", extra={'AppName': 'EasyAssist'})

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
                    is_lead=False, cobrowsing_type="outbound-proxy-cobrowsing")

                if cobrowse_io_objs != None and title != None:
                    cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

                service_request_analytics = []
                if timeline == "daily":
                    no_days = (datetime_end - datetime_start).days + 1
                    for day in range(no_days):
                        temp_datetime = datetime_start + \
                            datetime.timedelta(day)

                        date_filtered_cobrowse_io_objs = cobrowse_io_objs.filter(
                            request_datetime__date=temp_datetime)

                        date_filtered_drop_link_objs = CobrowseDropLink.objects.filter(
                            agent__in=agent_objs, generate_datetime__date=temp_datetime)

                        total_links_generated = date_filtered_drop_link_objs.filter(
                            ~Q(proxy_cobrowse_io=None)).count()

                        total_customers_joined = date_filtered_cobrowse_io_objs.count()

                        total_customers_converted = date_filtered_cobrowse_io_objs.filter(
                            is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                        service_request_analytics.append({
                            "label": str(temp_datetime.strftime("%d-%b-%y")),
                            "total_links_generated": total_links_generated,
                            "total_customers_joined": total_customers_joined,
                            "total_customers_converted": total_customers_converted,
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

                        date_filtered_drop_link_objs = CobrowseDropLink.objects.filter(
                            agent__in=agent_objs, generate_datetime__date__gte=temp_start_datetime, generate_datetime__date__lte=temp_end_datetime)

                        total_links_generated = date_filtered_drop_link_objs.filter(
                            ~Q(proxy_cobrowse_io=None))

                        total_customers_joined = date_filtered_cobrowse_io_objs.count()

                        total_customers_converted = date_filtered_cobrowse_io_objs.filter(
                            is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                        temp_start_datetime_str = temp_start_datetime.strftime(
                            "%d/%m")
                        temp_end_datetime_str = (
                            temp_end_datetime - datetime.timedelta(1)).strftime("%d/%m")

                        service_request_analytics.append({
                            "label": temp_start_datetime_str + "-" + temp_end_datetime_str,
                            "total_links_generated": total_links_generated,
                            "total_customers_joined": total_customers_joined,
                            "total_customers_converted": total_customers_converted,
                        })
                elif timeline == "monthly":
                    month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
                        r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days)).keys())

                    for month in month_list:
                        temp_month = month_to_num_dict[month.split("-")[0]]
                        temp_year = int(month.split("-")[1])

                        date_filtered_cobrowse_io_objs = cobrowse_io_objs.filter(
                            request_datetime__date__month=temp_month, request_datetime__date__year=temp_year)

                        date_filtered_drop_link_objs = CobrowseDropLink.objects.filter(
                            agent__in=agent_objs, generate_datetime__date__month=temp_month, generate_datetime__date__year=temp_year)

                        total_links_generated = date_filtered_drop_link_objs.filter(
                            ~Q(proxy_cobrowse_io=None))

                        total_customers_joined = date_filtered_cobrowse_io_objs.count()

                        total_customers_converted = date_filtered_cobrowse_io_objs.filter(
                            is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                        service_request_analytics.append({
                            "label": month,
                            "total_links_generated": total_links_generated,
                            "total_customers_joined": total_customers_joined,
                            "total_customers_converted": total_customers_converted,
                        })
                else:
                    logger.info("Invalid timeline in GetAgentServiceRequestAnalyticsOutboundAPI", extra={
                                'AppName': 'EasyAssist'})

                response["active_agent_role"] = active_agent.role
                response["service_request_analytics"] = service_request_analytics
                response["status"] = 200
                logger.info("Successfully exited from GetAgentProxyServiceRequestAnalyticsOutboundAPI", extra={
                            'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentServiceRequestAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


GetAgentProxyServiceRequestAnalyticsOutbound = GetAgentProxyServiceRequestAnalyticsOutboundAPI.as_view()


class GetAgentWiseProxyRequestAnalyticsOutboundAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetAgentWiseProxyRequestAnalyticsOutboundAPI", extra={
                        'AppName': 'EasyAssist'})

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()
            if access_token_obj.get_proxy_config_obj().enable_proxy_cobrowsing:
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
                    date_format = "%Y-%m-%d"
                    datetime_start = datetime.datetime.strptime(
                        start_date, date_format).date()
                    datetime_end = datetime.datetime.strptime(
                        end_date, date_format).date()
                except Exception:
                    pass

                active_agent = get_active_agent_obj(
                    request, CobrowseAgent)
                access_token_obj = active_agent.get_access_token_obj()

                cobrowse_io_objs = CobrowseIO.objects.filter(
                    is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                    request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                    is_lead=False, cobrowsing_type="outbound-proxy-cobrowsing")

                droplink_objs = CobrowseDropLink.objects.filter(generate_datetime__date__gte=datetime_start, generate_datetime__date__lte=datetime_end).filter(
                    ~Q(proxy_cobrowse_io=None))

                if cobrowse_io_objs != None and title != None:
                    cobrowse_io_objs = cobrowse_io_objs.filter(title=title)

                agent_request_analytics_list, agent_objs = [], []

                if active_agent.role in ["admin", "admin_ally"]:
                    agent_objs = get_list_agents_under_admin(
                        active_agent, is_active=None, is_account_active=None)
                elif active_agent.role == "supervisor":
                    agent_objs = list(active_agent.agents.all())
                else:
                    logger.info("Invalid User Access in GetAgentWiseProxyRequestAnalyticsOutboundAPI", extra={
                                'AppName': 'EasyAssist'})

                for agent in agent_objs:
                    total_links_generated = droplink_objs.filter(
                        agent=agent).count()

                    total_customers_converted = cobrowse_io_objs.filter(
                        agent=agent, is_helpful=True, is_archived=True).filter(~Q(cobrowsing_start_datetime=None)).count()

                    total_customers_joined = cobrowse_io_objs.filter(
                        agent=agent).count()

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
                            transferred_agents_requests_rejected = transferred_agents_requests_received - \
                                transferred_agents_requests_connected

                    if access_token_obj.enable_invite_agent_in_cobrowsing:
                        if access_token_obj.enable_session_transfer_in_cobrowsing:
                            agent_request_analytics_list.append({
                                "agent": agent.user.username,
                                "supervisor": agent.get_supervisors(),
                                "total_links_generated": total_links_generated,
                                "total_customers_joined": total_customers_joined,
                                "total_customers_converted": total_customers_converted,
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
                                "total_links_generated": total_links_generated,
                                "total_customers_joined": total_customers_joined,
                                "total_customers_converted": total_customers_converted,
                                "group_cobrowse_request_initiated": group_cobrowse_request_initiated,
                                "group_cobrowse_request_received": group_cobrowse_request_received,
                                "group_cobrowse_request_connected": group_cobrowse_request_connected
                            })
                    else:
                        agent_request_analytics_list.append({
                            "agent": agent.user.username,
                            "supervisor": agent.get_supervisors(),
                            "total_links_generated": total_links_generated,
                            "total_customers_joined": total_customers_joined,
                            "total_customers_converted": total_customers_converted,
                        })

                if access_token_obj.enable_invite_agent_in_cobrowsing:
                    if access_token_obj.enable_session_transfer_in_cobrowsing:
                        agent_request_analytics_list.sort(key=lambda data: (
                            data['total_customers_joined'],
                            data['total_links_generated'],
                            data['total_customers_converted'],
                            data['group_cobrowse_request_initiated'],
                            data['group_cobrowse_request_received'],
                            data['group_cobrowse_request_connected'],
                            data['transferred_agents_requests_received'],
                            data['transferred_agents_requests_connected'],
                            data['transferred_agents_requests_rejected'],
                        ), reverse=True)
                    else:
                        agent_request_analytics_list.sort(key=lambda data: (
                            data['total_customers_joined'],
                            data['total_links_generated'],
                            data['total_customers_converted'],
                            data['group_cobrowse_request_initiated'],
                            data['group_cobrowse_request_received'],
                            data['group_cobrowse_request_connected'],
                        ), reverse=True)
                else:
                    agent_request_analytics_list.sort(key=lambda data: (
                        data['total_customers_joined'],
                        data['total_links_generated'],
                        data['total_customers_converted'],
                    ), reverse=True)

                response["status"] = 200
                response["message"] = "success"
                response["agent_request_analytics_list"] = agent_request_analytics_list
                logger.info("Successfully exited from GetAgentWiseProxyRequestAnalyticsOutboundAPI", extra={
                            'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentWiseProxyRequestAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


GetAgentWiseProxyRequestAnalyticsOutbound = GetAgentWiseProxyRequestAnalyticsOutboundAPI.as_view()


class GetAgentNPSProxyAnalyticsOutboundAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetAgentNPSProxyAnalyticsOutboundAPI",
                        extra={'AppName': 'EasyAssist'})

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            if access_token_obj.get_proxy_config_obj().enable_proxy_cobrowsing:
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
                    date_format = "%Y-%m-%d"
                    datetime_start = datetime.datetime.strptime(
                        start_date, date_format).date()
                    datetime_end = datetime.datetime.strptime(
                        end_date, date_format).date()
                except Exception:
                    pass

                cobrowse_io_objs = CobrowseIO.objects.filter(
                    is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                    request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                    is_lead=False, cobrowsing_type="outbound-proxy-cobrowsing").filter(
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
                    logger.info("Invalid User Access in GetAgentWiseProxyRequestAnalyticsOutboundAPI", extra={
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
                    agent_nps_analytics_list = paginator.page(
                        paginator.num_pages)

                response["status"] = 200
                response["message"] = "success"
                response["agent_nps_analytics_list"] = list(
                    agent_nps_analytics_list)
                response["is_last_page"] = is_last_page
                logger.info("Successfully exited from GetAgentNPSProxyAnalyticsOutboundAPI", extra={
                            'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentNPSProxyAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


GetAgentNPSProxyAnalyticsOutbound = GetAgentNPSProxyAnalyticsOutboundAPI.as_view()


class GetQueryPageProxyAnalyticsOutboundAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside GetQueryPageProxyAnalyticsOutboundAPI",
                        extra={'AppName': 'EasyAssist'})

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            if access_token_obj.get_proxy_config_obj().enable_proxy_cobrowsing:
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
                    date_format = "%Y-%m-%d"
                    datetime_start = datetime.datetime.strptime(
                        start_date, date_format).date()
                    datetime_end = datetime.datetime.strptime(
                        end_date, date_format).date()
                except Exception:
                    pass

                cobrowse_io_objs = CobrowseIO.objects.filter(
                    is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                    request_datetime__date__gte=datetime_start, request_datetime__date__lte=datetime_end).filter(
                    is_lead=False, cobrowsing_type="outbound-proxy-cobrowsing").filter(
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
                logger.info("Successfully exited from GetQueryPageProxyAnalyticsOutboundAPI", extra={
                            'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetQueryPageProxyAnalyticsOutboundAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


GetQueryPageProxyAnalyticsOutbound = GetQueryPageProxyAnalyticsOutboundAPI.as_view()


class ExportOutboundProxyAnalyticsAPI(APIView):

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
                    "/outbound_proxy_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "2":
                # Last 7 days data
                start_date = datetime.datetime.now() - datetime.timedelta(days=7)
                start_date = start_date.strftime(date_format)
                end_date = datetime.datetime.now() - datetime.timedelta(days=1)
                end_date = end_date.strftime(date_format)

                export_path = "/secured_files/EasyAssistApp/OutboundAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/outbound_proxy_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "3":
                # Last 30 days data
                start_date = datetime.datetime.now() - datetime.timedelta(days=30)
                start_date = start_date.strftime(date_format)
                end_date = datetime.datetime.now() - datetime.timedelta(days=1)
                end_date = end_date.strftime(date_format)

                export_path = "/secured_files/EasyAssistApp/OutboundAnalytics/" + \
                    str(cobrowse_agent.user.username) + \
                    "/outbound_proxy_analytics_" + \
                    str(start_date) + "-" + str(end_date) + ".xls"

            elif requested_data["selected_filter_value"] == "4":

                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()
                end_date = datetime.datetime.strptime(
                    requested_data["enddate"], date_format).date()

                today_date = datetime.datetime.today().date()

                if (today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='outbound-proxy-analytics', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                else:
                    agents = get_list_agents_under_admin(
                        cobrowse_agent, is_active=None, is_account_active=None)

                    outbound_analytics_objs = CobrowseDateWiseOutboundProxyAnalytics.objects.filter(
                        date__gte=start_date, date__lte=end_date, agent__in=agents)
                    if outbound_analytics_objs.count() > 1000:
                        EasyAssistExportDataRequest.objects.create(
                            report_type='outbound-proxy-analytics', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                        response["status"] = 300
                        response["export_path"] = "None"
                        response["export_path_exist"] = False
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                    else:
                        export_path = get_outbound_proxy_analytics_data_dump(
                            requested_data, cobrowse_agent, CobrowseDateWiseOutboundProxyAnalytics, agents, outbound_analytics_objs)

            if os.path.exists(export_path[1:]) == True:
                if get_save_in_s3_bucket_status():
                    if requested_data["selected_filter_value"] == "4":
                        key = s3_bucket_upload_file_by_file_path(
                            export_path[1:], "/outbound_path_proxy_analytics_" + requested_data["startdate"] + "-" + requested_data["enddate"] + ".xls")
                    else:
                        key = s3_bucket_upload_file_by_file_path(
                            export_path[1:], "/outbound_proxy_analytics_" + str(start_date) + "-" + str(end_date) + ".xls")
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
            logger.error("Error ExportOutboundProxyAnalyticsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


ExportOutboundProxyAnalytics = ExportOutboundProxyAnalyticsAPI.as_view()
