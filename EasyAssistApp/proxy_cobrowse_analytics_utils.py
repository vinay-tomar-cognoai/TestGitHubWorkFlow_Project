from django.conf import settings
from EasyAssistApp.constants import *
from EasyAssistApp.utils_validation import *
from EasyAssistApp.utils import *
from DeveloperConsoleApp.utils import *
from DeveloperConsoleApp.utils_aws_s3 import *
from datetime import datetime, timedelta

import sys
import logging
import os
from os import path

logger = logging.getLogger(__name__)


def update_outbound_proxy_analytics_model(date, CobrowseDateWiseOutboundProxyAnalytics, CobrowseIO, CobrowseAccessToken, CobrowseDropLink, CobrowseIOInvitedAgentsDetails, CobrowseIOTransferredAgentsLogs):
    try:
        access_token_objs = CobrowseAccessToken.objects.all()

        cobrowse_io_objs = CobrowseIO.objects.filter(
            is_test=False, is_archived=True, is_reverse_cobrowsing=False, is_lead=False,
            request_datetime__date=date, cobrowsing_type="outbound-proxy-cobrowsing")

        for access_token_obj in access_token_objs.iterator():
            admin_agent = access_token_obj.agent
            if not admin_agent:
                continue

            agent_objs = get_list_agents_under_admin(
                admin_agent, is_active=None, is_account_active=None)

            agent_objs += get_list_supervisor_under_admin(admin_agent, None)

            filtered_cobrowse_io_objs = cobrowse_io_objs.filter(
                access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date)

            for agent in agent_objs:
                drop_link_objs = CobrowseDropLink.objects.filter(agent=agent, generate_datetime__date=date).filter(
                    ~Q(proxy_cobrowse_io=None))
                analytics_data = get_agent_wise_outbound_proxy_analytics(
                    filtered_cobrowse_io_objs, drop_link_objs, agent, CobrowseIOInvitedAgentsDetails, CobrowseIOTransferredAgentsLogs)
                if not analytics_data:
                    continue

                cobrowse_analytics_obj = CobrowseDateWiseOutboundProxyAnalytics.objects.filter(
                    date=date, agent=agent).first()

                if not cobrowse_analytics_obj:
                    cobrowse_analytics_obj = CobrowseDateWiseOutboundProxyAnalytics.objects.create(
                        agent=agent,
                        date=date,
                        links_generated=analytics_data["links_generated"],
                        customers_joined=analytics_data["customers_joined"],
                        request_attended=analytics_data["request_attended"],
                        request_unattended=analytics_data[
                            "request_unattended"],
                        customers_converted=analytics_data[
                            "customers_converted"],
                        customers_converted_by_url=analytics_data[
                            "customers_converted_by_url"],
                        total_session_time=analytics_data[
                            "total_session_time"],
                        attended_leads_total_wait_time=analytics_data[
                            "attended_leads_total_wait_time"],
                        unattended_leads_total_wait_time=analytics_data[
                            "unattended_leads_total_wait_time"],
                        group_cobrowse_request_initiated=analytics_data[
                            "group_cobrowse_request_initiated"],
                        group_cobrowse_request_received=analytics_data[
                            "group_cobrowse_request_received"],
                        group_cobrowse_request_connected=analytics_data["group_cobrowse_request_connected"],
                        transfer_requests_received=analytics_data["transfer_requests_received"],
                        transfer_requests_connected=analytics_data["transfer_requests_connected"],
                        transfer_requests_rejected=analytics_data["transfer_requests_rejected"],
                        repeated_customers=analytics_data["repeated_customers"],
                        unique_customers=analytics_data["unique_customers"],)
                else:
                    cobrowse_analytics_obj.links_generated = analytics_data[
                        "links_generated"]
                    cobrowse_analytics_obj.request_attended = analytics_data[
                        "request_attended"]
                    cobrowse_analytics_obj.request_unattended = analytics_data[
                        "request_unattended"]
                    cobrowse_analytics_obj.customers_converted = analytics_data[
                        "customers_converted"]
                    cobrowse_analytics_obj.customers_converted_by_url = analytics_data[
                        "customers_converted_by_url"]
                    cobrowse_analytics_obj.customers_joined = analytics_data[
                        "customers_joined"]
                    cobrowse_analytics_obj.total_session_time = analytics_data[
                        "total_session_time"]
                    cobrowse_analytics_obj.attended_leads_total_wait_time = analytics_data[
                        "attended_leads_total_wait_time"]
                    cobrowse_analytics_obj.unattended_leads_total_wait_time = analytics_data[
                        "unattended_leads_total_wait_time"]
                    cobrowse_analytics_obj.group_cobrowse_request_initiated = analytics_data[
                        "group_cobrowse_request_initiated"]
                    cobrowse_analytics_obj.group_cobrowse_request_received = analytics_data[
                        "group_cobrowse_request_received"]
                    cobrowse_analytics_obj.group_cobrowse_request_connected = analytics_data[
                        "group_cobrowse_request_connected"]
                    cobrowse_analytics_obj.transfer_requests_received = analytics_data[
                        "transfer_requests_received"]
                    cobrowse_analytics_obj.transfer_requests_connected = analytics_data[
                        "transfer_requests_connected"]
                    cobrowse_analytics_obj.transfer_requests_rejected = analytics_data[
                        "transfer_requests_rejected"]
                    cobrowse_analytics_obj.repeated_customers = analytics_data[
                        "repeated_customers"]
                    cobrowse_analytics_obj.unique_customers = analytics_data[
                        "unique_customers"]

                    cobrowse_analytics_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_outbound_proxy_analytics_model %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyAssist'})


def get_agent_wise_outbound_proxy_analytics(cobrowse_io_objs, drop_link_obj, agent, CobrowseIOInvitedAgentsDetails, CobrowseIOTransferredAgentsLogs):
    try:
        total_links_generated = 0
        total_customers_joined = 0
        total_customers_converted = 0
        total_customers_converted_by_url = 0
        total_leads_attended = 0
        total_session_duration = 0
        total_wait_time = 0
        total_wait_time_unattended = 0
        group_cobrowse_request_initiated = 0
        group_cobrowse_request_received = 0
        group_cobrowse_request_connected = 0
        transfer_requests_connected = 0
        transfer_requests_rejected = 0
        transfer_requests_received = 0
        repeated_customers = 0
        unique_customers = 0
        total_leads_unattended = 0

        group_cobrowse_request_received = CobrowseIOInvitedAgentsDetails.objects.filter(
            cobrowse_io__in=cobrowse_io_objs, support_agents_invited__in=[agent]).count()
        group_cobrowse_request_connected = CobrowseIOInvitedAgentsDetails.objects.filter(
            cobrowse_io__in=cobrowse_io_objs, support_agents_joined__in=[agent]).count()

        transfer_requests_received = CobrowseIOTransferredAgentsLogs.objects.filter(
            cobrowse_io__in=cobrowse_io_objs, cobrowse_request_type="transferred", transferred_agent__in=[agent]).count()
        transfer_requests_connected = CobrowseIOTransferredAgentsLogs.objects.filter(
            cobrowse_io__in=cobrowse_io_objs, transferred_agent__in=[agent], cobrowse_request_type="transferred", transferred_status="accepted").count()
        transfer_requests_rejected = transfer_requests_received - transfer_requests_connected

        cobrowse_io_objs = cobrowse_io_objs.filter(agent=agent)

        total_customers_joined = cobrowse_io_objs.count()

        total_links_generated = drop_link_obj.count()

        if total_customers_joined > 0:

            total_customers_converted = cobrowse_io_objs.filter(
                is_helpful=True, is_archived=True, is_lead_converted_by_url=False).filter(~Q(cobrowsing_start_datetime=None)).count()

            total_customers_converted_by_url = cobrowse_io_objs.filter(
                is_helpful=True, is_archived=True, is_lead_converted_by_url=True).filter(~Q(cobrowsing_start_datetime=None)).count()

            total_leads_attended = cobrowse_io_objs.filter(
                ~Q(cobrowsing_start_datetime=None)).count()

            cobrowse_io_initiated = cobrowse_io_objs.filter(
                ~Q(cobrowsing_start_datetime=None))
            for cobrowse_io in cobrowse_io_initiated:
                total_session_duration += cobrowse_io.session_time_in_seconds()
                total_wait_time += cobrowse_io.customer_wait_time_in_seconds()

            cobrowse_io_not_initiated = cobrowse_io_objs.filter(
                Q(cobrowsing_start_datetime=None))

            total_leads_unattended = cobrowse_io_not_initiated.count()

            for cobrowse_io in cobrowse_io_not_initiated:
                total_wait_time_unattended += cobrowse_io.customer_wait_time_in_seconds()

            group_cobrowse_request_initiated = CobrowseIOInvitedAgentsDetails.objects.filter(
                cobrowse_io__in=cobrowse_io_objs).count()

            unique_customers = cobrowse_io_objs.values(
                'mobile_number').annotate(mobile_number_count=Count('mobile_number')).filter(mobile_number_count=1).count()

            repeated_customers = cobrowse_io_objs.values(
                'mobile_number').annotate(mobile_number_count=Count('mobile_number')).filter(mobile_number_count__gt=1).count()

        return {
            "links_generated": total_links_generated,
            "customers_joined": total_customers_joined,
            "request_attended": total_leads_attended,
            "request_unattended": total_leads_unattended,
            "customers_converted": total_customers_converted,
            "customers_converted_by_url": total_customers_converted_by_url,
            "total_session_time": total_session_duration,
            "attended_leads_total_wait_time": total_wait_time,
            "unattended_leads_total_wait_time": total_wait_time_unattended,
            "group_cobrowse_request_initiated": group_cobrowse_request_initiated,
            "group_cobrowse_request_received": group_cobrowse_request_received,
            "group_cobrowse_request_connected": group_cobrowse_request_connected,
            "transfer_requests_received": transfer_requests_received,
            "transfer_requests_connected": transfer_requests_connected,
            "transfer_requests_rejected": transfer_requests_rejected,
            "unique_customers": unique_customers,
            "repeated_customers": repeated_customers,
        }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_agent_wise_outbound_proxy_analytics %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyAssist'})

    return None


def add_outbound_proxy_analytics_in_excel_sheet(analytics_workbook, requested_data, cobrowse_agent, CobrowseDateWiseOutboundProxyAnalytics, agents=None, outbound_analytics_objs=None):
    try:
        date_format = "%Y-%m-%d"
        start_date = requested_data["startdate"]
        start_date = datetime.strptime(start_date, date_format).date()
        end_date = requested_data["enddate"]
        end_date = datetime.strptime(end_date, date_format).date()
        temp_date = start_date

        if not outbound_analytics_objs:
            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None, is_account_active=None)
            outbound_analytics_objs = CobrowseDateWiseOutboundProxyAnalytics.objects.filter(
                date__gte=start_date, date__lte=end_date, agent__in=agents)

        access_token_obj = cobrowse_agent.get_access_token_obj()

        date_wise_analytics_data = {}
        agent_wise_analytics_data = {}
        analytics_data_summary = {
            "links_generated": 0,
            "customers_joined": 0,
            "customers_converted": 0,
            "customers_converted_by_url": 0,
            "total_session_time": 0,
            "attended_leads_total_wait_time": 0,
            "unattended_leads_total_wait_time": 0,
            "request_attended": 0
        }

        for analytics_obj in outbound_analytics_objs.iterator():
            date = analytics_obj.date.strftime(DATE_TIME_FORMAT)
            agent_username = analytics_obj.agent.user.username

            if date not in date_wise_analytics_data:
                date_wise_analytics_data[date] = {
                    "links_generated": 0,
                    "customers_joined": 0,
                    "customers_converted": 0,
                    "customers_converted_by_url": 0,
                    "total_session_time": 0,
                    "attended_leads_total_wait_time": 0,
                    "unattended_leads_total_wait_time": 0,
                    "repeated_customers": 0,
                    "unique_customers": 0,
                    "request_unattended": 0,
                    "request_attended": 0,
                }

            if agent_username not in agent_wise_analytics_data:
                agent_wise_analytics_data[agent_username] = {
                    "links_generated": 0,
                    "customers_joined": 0,
                    "customers_converted": 0,
                    "customers_converted_by_url": 0,
                    "total_session_time": 0,
                    "attended_leads_total_wait_time": 0,
                    "unattended_leads_total_wait_time": 0,
                    "group_cobrowse_request_initiated": 0,
                    "group_cobrowse_request_received": 0,
                    "group_cobrowse_request_connected": 0,
                    "transfer_requests_received": 0,
                    "transfer_requests_connected": 0,
                    "transfer_requests_rejected": 0,
                    "request_unattended": 0,
                    "request_attended": 0,
                }

            date_wise_analytics_data[date][
                "links_generated"] += analytics_obj.links_generated
            date_wise_analytics_data[date][
                "customers_joined"] += analytics_obj.customers_joined
            date_wise_analytics_data[date][
                "request_attended"] += analytics_obj.request_attended
            date_wise_analytics_data[date][
                "request_unattended"] += analytics_obj.request_unattended
            date_wise_analytics_data[date][
                "customers_converted"] += analytics_obj.customers_converted
            date_wise_analytics_data[date][
                "customers_converted_by_url"] += analytics_obj.customers_converted_by_url
            date_wise_analytics_data[date][
                "total_session_time"] += analytics_obj.total_session_time
            date_wise_analytics_data[date][
                "attended_leads_total_wait_time"] += analytics_obj.attended_leads_total_wait_time
            date_wise_analytics_data[date][
                "unattended_leads_total_wait_time"] += analytics_obj.unattended_leads_total_wait_time
            date_wise_analytics_data[date][
                "repeated_customers"] += analytics_obj.repeated_customers
            date_wise_analytics_data[date][
                "unique_customers"] += analytics_obj.unique_customers

            agent_wise_analytics_data[agent_username][
                "links_generated"] += analytics_obj.links_generated
            agent_wise_analytics_data[agent_username][
                "customers_joined"] += analytics_obj.customers_joined
            agent_wise_analytics_data[agent_username][
                "request_attended"] += analytics_obj.request_attended
            agent_wise_analytics_data[agent_username][
                "request_unattended"] += analytics_obj.request_unattended
            agent_wise_analytics_data[agent_username][
                "customers_converted"] += analytics_obj.customers_converted
            agent_wise_analytics_data[agent_username][
                "customers_converted_by_url"] += analytics_obj.customers_converted_by_url
            agent_wise_analytics_data[agent_username][
                "total_session_time"] += analytics_obj.total_session_time
            agent_wise_analytics_data[agent_username][
                "attended_leads_total_wait_time"] += analytics_obj.attended_leads_total_wait_time
            agent_wise_analytics_data[agent_username][
                "unattended_leads_total_wait_time"] += analytics_obj.unattended_leads_total_wait_time
            agent_wise_analytics_data[agent_username][
                "group_cobrowse_request_initiated"] += analytics_obj.group_cobrowse_request_initiated
            agent_wise_analytics_data[agent_username][
                "group_cobrowse_request_received"] += analytics_obj.group_cobrowse_request_received
            agent_wise_analytics_data[agent_username][
                "group_cobrowse_request_connected"] += analytics_obj.group_cobrowse_request_connected
            agent_wise_analytics_data[agent_username][
                "transfer_requests_received"] += analytics_obj.transfer_requests_received
            agent_wise_analytics_data[agent_username][
                "transfer_requests_connected"] += analytics_obj.transfer_requests_connected
            agent_wise_analytics_data[agent_username][
                "transfer_requests_rejected"] += analytics_obj.transfer_requests_rejected

            analytics_data_summary["links_generated"] += analytics_obj.links_generated
            analytics_data_summary["customers_joined"] += analytics_obj.customers_joined
            analytics_data_summary["request_attended"] += analytics_obj.request_attended
            analytics_data_summary["customers_converted"] += analytics_obj.customers_converted
            analytics_data_summary["customers_converted_by_url"] += analytics_obj.customers_converted_by_url
            analytics_data_summary["total_session_time"] += analytics_obj.total_session_time
            analytics_data_summary["attended_leads_total_wait_time"] += analytics_obj.attended_leads_total_wait_time
            analytics_data_summary["unattended_leads_total_wait_time"] += analytics_obj.unattended_leads_total_wait_time

        sheet1 = analytics_workbook.add_sheet("Outbound Proxy")

        sheet1.write(0, 0, "Date")
        sheet1.col(0).width = 256 * 20
        sheet1.write(0, 1, "Links Generated")
        sheet1.col(1).width = 256 * 20
        sheet1.write(0, 2, "Sessions Joined by the Customer")
        sheet1.col(2).width = 256 * 25
        sheet1.write(0, 3, AVERAGE_SESSION_TIME)
        sheet1.col(3).width = 256 * 20
        sheet1.write(0, 4, AVERAGE_WAITING_TIME_FOR_ATTENDED_LEADS)
        sheet1.col(4).width = 256 * 40
        sheet1.write(0, 5, AVERAGE_WAITING_TIME_FOR_UNATTENDED_LEADS)
        sheet1.col(5).width = 256 * 40
        sheet1.write(0, 6, CUSTOMERS_CONVERTED_BY_AGENT)
        sheet1.col(6).width = 256 * 35
        sheet1.write(0, 7, CUSTOMERS_CONVERTED_THROUGH_URL)
        sheet1.col(7).width = 256 * 35
        sheet1.write(0, 8, "Repeated Customers")
        sheet1.col(8).width = 256 * 20
        sheet1.write(0, 9, "Unique Customers")
        sheet1.col(9).width = 256 * 25

        index = 1
        while temp_date <= end_date:

            date = temp_date.strftime(DATE_TIME_FORMAT)
            excel_sheet_date_format = temp_date.strftime(DATE_TIME_FORMAT_6)
            temp_date = temp_date + timedelta(1)

            if date not in date_wise_analytics_data:
                total_links_generated = 0
                total_customers_joined = 0
                total_request_attended = 0
                total_customers_converted = 0
                total_customers_converted_by_url = 0
                average_session_time = ZERO_SEC
                attended_leads_avg_wait_time = ZERO_SEC
                unattended_leads_avg_wait_time = ZERO_SEC
                unique_customers = 0
                repeated_customers = 0
            else:
                total_session_time = date_wise_analytics_data[
                    date]["total_session_time"]

                total_request_attended = date_wise_analytics_data[
                    date]["request_attended"]

                attended_leads_total_wait_time = date_wise_analytics_data[
                    date]["attended_leads_total_wait_time"]

                unattended_leads_total_wait_time = date_wise_analytics_data[
                    date]["unattended_leads_total_wait_time"]

                total_customers_converted = date_wise_analytics_data[
                    date]["customers_converted"]

                total_customers_converted_by_url = date_wise_analytics_data[
                    date]["customers_converted_by_url"]

                total_request_unattended = date_wise_analytics_data[
                    date]["request_unattended"]

                total_links_generated = date_wise_analytics_data[
                    date]["links_generated"]

                total_customers_joined = date_wise_analytics_data[
                    date]["customers_joined"]

                unique_customers = date_wise_analytics_data[
                    date]["unique_customers"]

                repeated_customers = date_wise_analytics_data[
                    date]["repeated_customers"]

                average_session_time = get_readable_average_time(
                    total_session_time, total_request_attended)

                attended_leads_avg_wait_time = get_readable_average_time(
                    attended_leads_total_wait_time, total_request_attended)

                unattended_leads_avg_wait_time = get_readable_average_time(
                    unattended_leads_total_wait_time, total_request_unattended)

            analytics_data_summary[
                "total_session_time"] += easyassist_time_in_seconds(average_session_time)
            analytics_data_summary[
                "attended_leads_total_wait_time"] += easyassist_time_in_seconds(attended_leads_avg_wait_time)
            analytics_data_summary[
                "unattended_leads_total_wait_time"] += easyassist_time_in_seconds(unattended_leads_avg_wait_time)

            sheet1.write(index, 0, excel_sheet_date_format)
            sheet1.write(index, 1, total_links_generated)
            sheet1.write(index, 2, total_customers_joined)
            sheet1.write(index, 3, average_session_time)
            sheet1.write(index, 4, attended_leads_avg_wait_time)
            sheet1.write(index, 5, unattended_leads_avg_wait_time)
            sheet1.write(index, 6, total_customers_converted)
            sheet1.write(index, 7, total_customers_converted_by_url)
            sheet1.write(index, 8, repeated_customers)
            sheet1.write(index, 9, unique_customers)

            index += 1

        sheet2 = analytics_workbook.add_sheet(
            "Agent Wise Analytics - Outbound")
        sheet2.write(0, 0, "Agent")
        sheet2.col(0).width = 256 * 20
        sheet2.write(0, 1, "Links Generated")
        sheet2.col(1).width = 256 * 20
        sheet2.write(0, 2, "Sessions Joined by the Customer")
        sheet2.col(2).width = 256 * 25
        sheet2.write(0, 3, AVERAGE_SESSION_TIME)
        sheet2.col(3).width = 256 * 20
        sheet2.write(0, 4, AVERAGE_WAITING_TIME_FOR_ATTENDED_LEADS)
        sheet2.col(4).width = 256 * 40
        sheet2.write(0, 5, AVERAGE_WAITING_TIME_FOR_UNATTENDED_LEADS)
        sheet2.col(5).width = 256 * 40
        sheet2.write(0, 6, CUSTOMERS_CONVERTED_BY_AGENT)
        sheet2.col(6).width = 256 * 35
        sheet2.write(0, 7, CUSTOMERS_CONVERTED_THROUGH_URL)
        sheet2.col(7).width = 256 * 35

        if access_token_obj and access_token_obj.enable_invite_agent_in_cobrowsing:
            sheet2.write(0, 8, "Group Cobrowse Request Initiated")
            sheet2.col(8).width = 256 * 40
            sheet2.write(0, 9, "Group Cobrowse Request Received")
            sheet2.col(9).width = 256 * 40
            sheet2.write(0, 10, "Group Cobrowse Request Connected")
            sheet2.col(10).width = 256 * 40

            if access_token_obj.enable_session_transfer_in_cobrowsing:
                sheet2.write(0, 11, "Transfer Requests Received")
                sheet2.col(11).width = 256 * 45
                sheet2.write(0, 12, "Transfer Requests Connected")
                sheet2.col(12).width = 256 * 45
                sheet2.write(0, 13, "Transferred Agent Not Connected")
                sheet2.col(13).width = 256 * 45

        index = 1
        for agent in agents:
            agent_username = agent.user.username
            if agent_username not in agent_wise_analytics_data:
                total_links_generated = 0
                total_customers_joined = 0
                total_request_attended = 0
                total_customers_converted = 0
                total_customers_converted_by_url = 0
                total_request_unattended = 0
                average_session_time = ZERO_SEC
                attended_leads_avg_wait_time = ZERO_SEC
                unattended_leads_avg_wait_time = ZERO_SEC
                group_cobrowse_request_initiated = 0
                group_cobrowse_request_received = 0
                group_cobrowse_request_connected = 0
                transfer_requests_connected = 0
                transfer_requests_rejected = 0
                transfer_requests_received = 0
            else:
                total_session_time = agent_wise_analytics_data[
                    agent_username]["total_session_time"]

                total_request_attended = agent_wise_analytics_data[
                    agent_username]["request_attended"]

                attended_leads_total_wait_time = agent_wise_analytics_data[
                    agent_username]["attended_leads_total_wait_time"]

                unattended_leads_total_wait_time = agent_wise_analytics_data[
                    agent_username]["unattended_leads_total_wait_time"]

                total_customers_converted = agent_wise_analytics_data[
                    agent_username]["customers_converted"]

                total_customers_converted_by_url = agent_wise_analytics_data[
                    agent_username]["customers_converted_by_url"]

                total_request_unattended = agent_wise_analytics_data[
                    agent_username]["request_unattended"]

                total_customers_joined = agent_wise_analytics_data[
                    agent_username]["customers_joined"]

                total_links_generated = agent_wise_analytics_data[
                    agent_username]["links_generated"]

                average_session_time = get_readable_average_time(
                    total_session_time, total_request_attended)

                attended_leads_avg_wait_time = get_readable_average_time(
                    attended_leads_total_wait_time, total_request_attended)

                unattended_leads_avg_wait_time = get_readable_average_time(
                    unattended_leads_total_wait_time, total_request_unattended)

                group_cobrowse_request_initiated = agent_wise_analytics_data[
                    agent_username]["group_cobrowse_request_initiated"]

                group_cobrowse_request_received = agent_wise_analytics_data[
                    agent_username]["group_cobrowse_request_received"]

                group_cobrowse_request_connected = agent_wise_analytics_data[
                    agent_username]["group_cobrowse_request_connected"]

                transfer_requests_received = agent_wise_analytics_data[
                    agent_username]["transfer_requests_received"]

                transfer_requests_connected = agent_wise_analytics_data[
                    agent_username]["transfer_requests_connected"]

                transfer_requests_rejected = agent_wise_analytics_data[
                    agent_username]["transfer_requests_rejected"]

            sheet2.write(index, 0, agent_username)
            sheet2.write(index, 1, total_links_generated)
            sheet2.write(index, 2, total_customers_joined)
            sheet2.write(index, 3, average_session_time)
            sheet2.write(index, 4, attended_leads_avg_wait_time)
            sheet2.write(index, 5, unattended_leads_avg_wait_time)
            sheet2.write(index, 6, total_customers_converted)
            sheet2.write(index, 7, total_customers_converted_by_url)

            if access_token_obj and access_token_obj.enable_invite_agent_in_cobrowsing:
                sheet2.write(index, 8, group_cobrowse_request_initiated)
                sheet2.write(index, 9, group_cobrowse_request_received)
                sheet2.write(index, 10, group_cobrowse_request_connected)

                if access_token_obj.enable_session_transfer_in_cobrowsing:
                    sheet2.write(index, 11, transfer_requests_received)
                    sheet2.write(index, 12, transfer_requests_connected)
                    sheet2.write(index, 13, transfer_requests_rejected)

            index += 1

        # sheet3 = analytics_workbook.add_sheet("Outbound Summary")

        # sheet3.write(0, 0, "Links Generated")
        # sheet3.col(0).width = 256 * 25
        # sheet3.write(0, 1, "Sessions Joined by the Customers")
        # sheet3.col(1).width = 256 * 25
        # sheet3.write(0, 2, "Co-browsing Requests Attended")
        # sheet3.col(2).width = 256 * 35
        # sheet3.write(0, 3, CUSTOMERS_CONVERTED_BY_AGENT)
        # sheet3.col(3).width = 256 * 35
        # sheet3.write(0, 4, CUSTOMERS_CONVERTED_THROUGH_URL)
        # sheet3.col(4).width = 256 * 35
        # sheet3.write(0, 5, AVERAGE_SESSION_TIME)
        # sheet3.col(5).width = 256 * 35
        # sheet3.write(0, 6, AVERAGE_WAITING_TIME_FOR_ATTENDED_LEADS)
        # sheet3.col(6).width = 256 * 35
        # sheet3.write(0, 7, AVERAGE_WAITING_TIME_FOR_UNATTENDED_LEADS)
        # sheet3.col(7).width = 256 * 40

        # sheet3.write(1, 0, analytics_data_summary["links_generated"])
        # sheet3.write(1, 1, analytics_data_summary["customers_joined"])
        # sheet3.write(1, 2, analytics_data_summary["request_attended"])
        # sheet3.write(1, 3, analytics_data_summary["customers_converted"])
        # sheet3.write(1, 4, analytics_data_summary["customers_converted_by_url"])

        # hours, minutes, seconds = easyassist_get_average_time(
        #     analytics_data_summary["total_session_time"], report_period_days)
        # average_session_time = readable_time_format(hours, minutes, seconds)
        # sheet3.write(1, 5, average_session_time)

        # hours, minutes, seconds = easyassist_get_average_time(
        #     analytics_data_summary["attended_leads_total_wait_time"], report_period_days)

        # attended_leads_avg_wait_time = readable_time_format(
        #     hours, minutes, seconds)
        # sheet3.write(1, 6, attended_leads_avg_wait_time)

        # hours, minutes, seconds = easyassist_get_average_time(
        #     analytics_data_summary["unattended_leads_total_wait_time"], report_period_days)

        # unattended_leads_avg_wait_time = readable_time_format(
        #     hours, minutes, seconds)
        # sheet3.write(1, 7, unattended_leads_avg_wait_time)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_outbound_proxy_analytics_in_excel_sheet %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyAssist'})


def get_outbound_proxy_analytics_data_dump(requested_data, cobrowse_agent, CobrowseDateWiseOutboundProxyAnalytics, agents=None, outbound_analytics_objs=None):
    try:
        logger.info("Inside get_outbound_proxy_analytics_data_dump",
                    extra={'AppName': 'EasyAssist'})
        
        start_date = requested_data["startdate"]
        end_date = requested_data["enddate"]

        date_format = DATE_TIME_FORMAT

        start_date = datetime.strptime(start_date, date_format).date()
        end_date = datetime.strptime(end_date, date_format).date()

        file_directory = settings.SECURE_MEDIA_ROOT + \
            "EasyAssistApp/OutboundAnalytics/" + \
            str(cobrowse_agent.user.username)
        if not path.exists(file_directory):
            os.makedirs(file_directory)

        file_path = file_directory + "/outbound_proxy_analytics_" + \
            str(start_date) + "-" + str(end_date) + ".xls"
        absolute_file_path = "/secured_files/EasyAssistApp/OutboundAnalytics/" + \
            str(cobrowse_agent.user.username) + \
            "/outbound_proxy_analytics_" + \
            str(start_date) + "-" + str(end_date) + ".xls"

        analytics_workbook = Workbook()

        add_outbound_proxy_analytics_in_excel_sheet(
            analytics_workbook, requested_data, cobrowse_agent, CobrowseDateWiseOutboundProxyAnalytics, agents, outbound_analytics_objs)

        analytics_workbook.save(file_path)
        return absolute_file_path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_outbound_proxy_analytics_data_dump %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyAssist'})

        return None
