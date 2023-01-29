from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.utils.encoding import smart_str
from django.shortcuts import HttpResponse
from django import forms
from EasyAssistApp.constants_mailer_analytics_css import *
from EasyAssistApp.encrypt import CustomEncrypt, generate_random_key
from EasyAssistApp.send_email import send_analytics_over_email
from EasyAssistApp.html_parser import strip_html_tags
from EasyAssistApp.constants import *
from EasyAssistApp.utils import *
from DeveloperConsoleApp.utils import get_developer_console_settings
from DeveloperConsoleApp.constants import GENERAL_LOGIN_LOGO
from EasyAssistApp.constants import COGNOAI_LOGO_PATH
import plotly.graph_objects as go


import hashlib
import requests
import sys
import json
import operator
import logging
import re
import ast
import random
import array
import pytz
import threading
import os
import uuid
import mimetypes

from xlwt import Workbook, XFStyle, Font, Alignment
import xlrd
from xlrd import open_workbook

from urllib.parse import urljoin, urlparse, urlencode
from random import randint
from os import path
from os.path import basename

from datetime import datetime, timedelta
from PIL import Image

logger = logging.getLogger(__name__)


def get_email_analytics_data():

    data = {}
    try:
        data = {
            "email_subject": EMAIL_SUBJECT,
            "record_attachments": RECORDS_ATTACHMENTS,
            "count_variation_list": COUNT_VARIATION_LIST,
            "records_analytics_table": RECORDS_ANALYTICS_TABLE,
            "records_analytics_graph": RECORDS_ANALYTICS_GRAPH,
        }
        data = json.dumps(data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_email_analytics_data %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyAssist'})

    return data


def create_new_email_analytics_profile(
        data, access_token,
        CobrowseMailerAnalyticsProfile,
        CobrowseMailerAnalyticsGraph,
        CobrowseMailerAnalyticsTable,
        CobrowseMailerAnalyticsAttachment,
        CobrowseMailerAnalyticsCalendar):

    status = 500
    message = "Internal Server Error"

    try:
        profile_name = data["profile_name"]
        profile_name_regex = r'^[a-zA-Z0-9 _-]+$'
        if not len(profile_name.strip()):
            status = 302
            message = "Please enter profile name to conitue"
            return (status, message)

        if not re.fullmatch(profile_name_regex, profile_name):
            status = 302
            message = "Please enter a valid profile name. Only A-Z, a-z, 0-9, -, _ and space are allowed"
            return (status, message)

        email_frequency = data["email_frequency"]
        email_address_list = data["email_address_list"]

        email_subject = data["email_subject"]
        email_subject = remo_html_from_string(email_subject)
        email_subject = remo_special_tag_from_string(email_subject)

        graphic_parameters = data["graphic_parameters"]
        table_parameters = data["table_parameter"]
        attachment_parameter = data["attachment_parameter"]

        graphic_parameters_enabled = graphic_parameters["is_enabled"]
        graph_records = graphic_parameters["graph_parameter_records"]
        graph_records = json.dumps(graph_records)

        table_parameter_enabled = table_parameters["is_enabled"]
        count_variation = table_parameters["count_variation"]
        table_records = table_parameters["table_parameter_records"]
        table_records = json.dumps(table_records)

        attachment_parameter_enabled = attachment_parameter["is_enabled"]
        attachment_records = attachment_parameter["attachment_parameter_records"]
        attachment_records = json.dumps(attachment_records)
        use_single_file = attachment_parameter["use_single_file"]

        email_address_list = json.dumps(email_address_list)

        email_analytics_profile_obj = CobrowseMailerAnalyticsProfile.objects.create(
            name=profile_name,
            access_token=access_token,
            email_address=email_address_list,
            email_subject=email_subject,
            include_graphs=graphic_parameters_enabled,
            include_tables=table_parameter_enabled,
            include_attachment=attachment_parameter_enabled)

        # Save Graph Profile
        email_analytics_graph_obj = CobrowseMailerAnalyticsGraph.objects.create(
            profile=email_analytics_profile_obj,
            records=graph_records)

        # Save Table Profile
        count_variation = json.dumps(count_variation)
        email_analytics_table_obj = CobrowseMailerAnalyticsTable.objects.create(
            profile=email_analytics_profile_obj,
            count_variation=count_variation,
            records=table_records)

        # Save Attachment
        email_analytics_attachment_obj = CobrowseMailerAnalyticsAttachment.objects.create(
            profile=email_analytics_profile_obj,
            records=attachment_records,
            use_single_file=use_single_file)

        email_analytics_profile_obj.analytics_graph = email_analytics_graph_obj
        email_analytics_profile_obj.analytics_table = email_analytics_table_obj
        email_analytics_profile_obj.analytics_attachment = email_analytics_attachment_obj
        email_analytics_profile_obj.save()

        calendar_obj = CobrowseMailerAnalyticsCalendar.objects.filter(
            profile=email_analytics_profile_obj).first()
        if calendar_obj == None:
            calendar_obj = CobrowseMailerAnalyticsCalendar.objects.create(
                profile=email_analytics_profile_obj)

        update_email_frequency(email_frequency, calendar_obj)

        status = 200
        message = "success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In create_new_email_analytics_profile: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})

    return (status, message)


def update_existing_profile(
        data, access_token_obj,
        email_analytics_profile_obj,
        CobrowseMailerAnalyticsProfile,
        CobrowseMailerAnalyticsGraph,
        CobrowseMailerAnalyticsTable,
        CobrowseMailerAnalyticsAttachment,
        CobrowseMailerAnalyticsCalendar):

    status = 500
    message = "Internal Server Error"

    try:
        profile_name = data["profile_name"]
        profile_name_regex = r'^[a-zA-Z0-9 _-]+$'
        
        if not len(profile_name.strip()):
            status = 302
            message = "Please enter profile name to conitue"
            return (status, message)
        
        if not re.fullmatch(profile_name_regex, profile_name):
            status = 302
            message = "Please enter a valid profile name. Only A-Z, a-z, 0-9, -, _ and space are allowed"
            return (status, message)

        email_frequency = data["email_frequency"]
        email_address_list = data["email_address_list"]

        email_subject = data["email_subject"]
        email_subject = remo_html_from_string(email_subject)
        email_subject = remo_special_tag_from_string(email_subject)

        graphic_parameters = data["graphic_parameters"]
        table_parameters = data["table_parameter"]
        attachment_parameter = data["attachment_parameter"]

        graphic_parameters_enabled = graphic_parameters["is_enabled"]
        graph_records = graphic_parameters["graph_parameter_records"]
        graph_records = json.dumps(graph_records)

        table_parameter_enabled = table_parameters["is_enabled"]
        count_variation = table_parameters["count_variation"]
        table_records = table_parameters["table_parameter_records"]
        table_records = json.dumps(table_records)

        attachment_parameter_enabled = attachment_parameter["is_enabled"]
        attachment_records = attachment_parameter["attachment_parameter_records"]
        attachment_records = json.dumps(attachment_records)
        use_single_file = attachment_parameter["use_single_file"]

        email_address_list = json.dumps(email_address_list)

        email_analytics_profile_obj.name = profile_name
        email_analytics_profile_obj.email_address = email_address_list
        email_analytics_profile_obj.email_subject = email_subject

        if graphic_parameters_enabled == True:
            email_analytics_profile_obj.include_graphs = True
        else:
            email_analytics_profile_obj.include_graphs = False

        if table_parameter_enabled == True:
            email_analytics_profile_obj.include_tables = True
        else:
            email_analytics_profile_obj.include_tables = False

        if attachment_parameter_enabled == True:
            email_analytics_profile_obj.include_attachment = True
        else:
            email_analytics_profile_obj.include_attachment = False

        email_analytics_profile_obj.save()

        # Save Graph Profile
        email_analytics_graph_obj = email_analytics_profile_obj.analytics_graph
        if email_analytics_graph_obj is None:
            email_analytics_graph_obj = CobrowseMailerAnalyticsGraph.objects.create(
                profile=email_analytics_profile_obj,
                records=graph_records)
        else:
            email_analytics_graph_obj.records = graph_records
            email_analytics_graph_obj.save()

        # Save Table Profile
        count_variation = json.dumps(count_variation)
        email_analytics_table_obj = email_analytics_profile_obj.analytics_table
        if email_analytics_table_obj is None:
            email_analytics_table_obj = CobrowseMailerAnalyticsTable.objects.create(
                profile=email_analytics_profile_obj,
                count_variation=count_variation,
                records=table_records)
        else:
            email_analytics_table_obj.count_variation = count_variation
            email_analytics_table_obj.records = table_records
            email_analytics_table_obj.save()

        # Save Attachment
        email_analytics_attachment_obj = email_analytics_profile_obj.analytics_attachment
        if email_analytics_attachment_obj is None:
            email_analytics_attachment_obj = CobrowseMailerAnalyticsAttachment.objects.create(
                profile=email_analytics_profile_obj,
                records=attachment_records,
                use_single_file=use_single_file)
        else:
            email_analytics_attachment_obj.use_single_file = use_single_file
            email_analytics_attachment_obj.records = attachment_records
            email_analytics_attachment_obj.save()

        email_analytics_profile_obj.analytics_graph = email_analytics_graph_obj
        email_analytics_profile_obj.analytics_table = email_analytics_table_obj
        email_analytics_profile_obj.analytics_attachment = email_analytics_attachment_obj
        email_analytics_profile_obj.save()

        calendar_obj = CobrowseMailerAnalyticsCalendar.objects.filter(
            profile=email_analytics_profile_obj).first()
        if calendar_obj == None:
            calendar_obj = CobrowseMailerAnalyticsCalendar.objects.create(
                profile=email_analytics_profile_obj)

        update_email_frequency(email_frequency, calendar_obj)

        status = 200
        message = "success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In update_existing_profile: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})

    return (status, message)


def update_email_frequency(email_frequency, calendar_obj):
    try:
        try:
            days = json.loads(calendar_obj.days)
        except Exception:
            days = {}

        email_frequency = [str(item) for item in email_frequency]

        for date in range(1, 32):
            date = str(date)

            if date not in days:
                days[date] = []

            if "1" in email_frequency:
                days[date].append("1")
            else:
                if "1" in days[date]:
                    days[date].remove("1")

            if "7" in email_frequency:
                if date in ["1", "8", "15", "22", "29"]:
                    days[date].append("7")
            else:
                if "7" in days[date]:
                    days[date].remove("7")

            if "30" in email_frequency:
                if date == "1":
                    days[date].append("30")
            else:
                if "30" in days[date]:
                    days[date].remove("30")

            if "60" in email_frequency:
                if date == "1":
                    days[date].append("60")
            else:
                if "60" in days[date]:
                    days[date].remove("60")

            if "90" in email_frequency:
                if date == "1":
                    days[date].append("90")
            else:
                if "90" in days[date]:
                    days[date].remove("90")

            days[date] = list(set(days[date]))

        calendar_obj.days = json.dumps(days)
        calendar_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In update_email_frequency: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})


def get_email_frequency_from_calendar_obj(calendar_obj):
    try:
        if calendar_obj is None:
            return []

        days = calendar_obj.days
        days = json.loads(days)

        email_frequency_set = set()
        for day, frequency_list in days.items():
            for frequency in frequency_list:
                email_frequency_set.add(frequency)

        email_frequency_list = list(email_frequency_set)
        return email_frequency_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_email_frequency_from_calendar_obj: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})
        return []


def parse_email_analytics_profile(profile_obj, CobrowseMailerAnalyticsCalendar):
    try:
        profile_pk = str(profile_obj.pk)

        profile_name = profile_obj.name

        email_subject = profile_obj.email_subject
        email_id_list = json.loads(profile_obj.email_address)

        enable_graphic_parameters = profile_obj.include_graphs
        graph_records = json.loads(profile_obj.analytics_graph.records)

        enable_table_parameters = profile_obj.include_tables
        table_records = json.loads(profile_obj.analytics_table.records)
        count_variation = profile_obj.analytics_table.count_variation
        count_variation = json.loads(count_variation)

        enable_attachment_parameters = profile_obj.include_attachment
        attachment_records = json.loads(
            profile_obj.analytics_attachment.records)
        use_single_file = profile_obj.analytics_attachment.use_single_file

        email_analytics_calendar_obj = CobrowseMailerAnalyticsCalendar.objects.filter(
            profile=profile_obj).first()
        email_frequency = get_email_frequency_from_calendar_obj(
            email_analytics_calendar_obj)

        parsed_data = {
            "pk": profile_pk,
            "profile_name": profile_name,
            "email_subject": email_subject,
            "email_id_list": email_id_list,
            "email_frequency": email_frequency,
            "graphic_parameters": {
                "is_enabled": enable_graphic_parameters,
                "records": graph_records,
            },
            "table_parameters": {
                "is_enabled": enable_table_parameters,
                "records": table_records,
                "count_variation": count_variation,
            },
            "attachment_parameter": {
                "is_enabled": enable_attachment_parameters,
                "records": attachment_records,
                "use_single_file": use_single_file,
            }
        }

        return parsed_data
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In parse_email_analytics_profile: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})

        return {}


def get_inbound_table_records(access_token, CobrowseDateWiseInboundAnalytics, date_interval):
    from EasyAssistApp.models import CobrowseIO
    analytics_data = {
        "request_initiated": 0,
        "request_attended": 0,
        "request_unattended": 0,
        "followup_leads": 0,
        "declined_leads": 0,
        "customer_converted": 0,
        "customer_converted_by_url": 0,
        "avg_session_time": 0,
        "request_assistance_avg_wait_time": 0,
        "unique_customers": 0,
        "repeated_customers": 0,
    }

    try:
        admin_agent = access_token.agent
        start_date = date_interval["start_date"]
        end_date = date_interval["end_date"]

        agent_list = get_list_agents_under_admin(
            admin_agent, is_active=None, is_account_active=None)

        inbound_analytics_objs = CobrowseDateWiseInboundAnalytics.objects.filter(
            agent__in=agent_list, date__gte=start_date, date__lte=end_date)

        total_request_initiated = 0
        total_request_attended = 0
        total_request_unattended = 0
        total_customer_converted = 0
        total_customer_converted_by_url = 0
        total_declined_leads = 0
        request_assistance_total_wait_time = 0
        total_session_time = 0
        total_followup_leads = 0
        
        cobrowse_io_objs = CobrowseIO.objects.filter(access_token=access_token, request_datetime__date__gte=access_token.go_live_date).filter(
            is_test=False, is_archived=True, is_lead=False, is_reverse_cobrowsing=False, agent__in=agent_list,
            request_datetime__date__gte=start_date, request_datetime__date__lte=end_date).exclude(
            cobrowsing_type="outbound-proxy-cobrowsing").values("mobile_number").annotate(customer_count=Count('mobile_number'))
        unique_customers = cobrowse_io_objs.filter(customer_count=1).count()
        repeated_customers = cobrowse_io_objs.filter(customer_count__gt=1).count()

        for inbound_analytics_obj in inbound_analytics_objs.iterator():
            total_request_initiated += inbound_analytics_obj.request_initiated
            total_request_attended += inbound_analytics_obj.request_attended
            total_request_unattended += inbound_analytics_obj.request_unattended
            total_customer_converted += inbound_analytics_obj.customers_converted
            total_customer_converted_by_url += inbound_analytics_obj.customers_converted_by_url
            total_declined_leads += inbound_analytics_obj.declined_leads
            total_followup_leads += inbound_analytics_obj.followup_leads
            total_session_time += inbound_analytics_obj.total_session_time
            request_assistance_total_wait_time += inbound_analytics_obj.request_assistance_total_wait_time

        average_session_time = get_readable_average_time(
            total_session_time, total_request_attended)

        request_assistance_avg_wait_time = get_readable_average_time(
            request_assistance_total_wait_time, total_request_initiated)

        analytics_data["request_initiated"] = total_request_initiated
        analytics_data["request_attended"] = total_request_attended
        analytics_data["request_unattended"] = total_request_unattended
        analytics_data["customer_converted"] = total_customer_converted
        analytics_data["customers_converted_by_url"] = total_customer_converted_by_url
        analytics_data["declined_leads"] = total_declined_leads
        analytics_data["followup_leads"] = total_followup_leads
        analytics_data["avg_session_time"] = average_session_time
        analytics_data["request_assistance_avg_wait_time"] = request_assistance_avg_wait_time
        analytics_data["unique_customers"] = unique_customers
        analytics_data["repeated_customers"] = repeated_customers

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_inbound_table_records: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})

    return analytics_data


def get_outbound_search_lead_table_records(access_token, CobrowseDateWiseOutboundAnalytics, date_interval):
    from EasyAssistApp.models import CobrowseIO, CobrowseCapturedLeadData, CobrowseLeadHTMLField

    analytics_data = {
        "captured_leads": 0,
        "searched_leads": 0,
        "request_attended": 0,
        "request_unattended": 0,
        "customer_converted": 0,
        "customer_converted_by_url": 0,
        "avg_session_time": 0,
        "requests_denied_by_customers": 0,
        "unique_customers": 0,
        "repeated_customers": 0,
    }

    try:
        admin_agent = access_token.agent
        start_date = date_interval["start_date"]
        end_date = date_interval["end_date"]

        agent_list = get_list_agents_under_admin(
            admin_agent, is_active=None, is_account_active=None)

        outbound_analytics_objs = CobrowseDateWiseOutboundAnalytics.objects.filter(
            agent__in=agent_list, date__gte=start_date, date__lte=end_date)

        total_captured_leads = 0
        total_searched_leads = 0
        total_request_attended = 0
        total_request_unattended = 0
        total_customer_converted = 0
        total_customer_converted_by_url = 0
        total_requests_denied_by_customers = 0
        total_session_time = 0
        cobrowse_io_objs = CobrowseIO.objects.filter(
            is_test=False, access_token=access_token, request_datetime__date__gte=access_token.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
            request_datetime__date__gte=start_date, request_datetime__date__lte=end_date).filter(
            is_lead=True)

        cobrowse_io_objs = cobrowse_io_objs.filter(agent__in=agent_list)
        
        unique_identifier_field = access_token.search_fields.filter(
            unique_identifier=True)

        captured_data = CobrowseCapturedLeadData.objects.filter(search_field__in=unique_identifier_field, agent_searched=True).values("primary_value").annotate(
            value_count=Count('primary_value')).filter(value_count=1).values_list("primary_value", flat=True)

        unique_cobrowse_io_objs = cobrowse_io_objs.filter(
            session_id__in=CobrowseCapturedLeadData.objects.filter(primary_value__in=captured_data, agent_searched=True).values_list("session_id", flat=True))

        non_unique_identifier_field = access_token.search_fields.filter(
            unique_identifier=False)

        off_field_captured_data = CobrowseCapturedLeadData.objects.filter(
            search_field__in=non_unique_identifier_field, agent_searched=True).values_list("session_id", flat=True)

        non_unique_captured_session = cobrowse_io_objs.filter(
            session_id__in=off_field_captured_data)

        unique_customers = unique_cobrowse_io_objs.count(
        ) + non_unique_captured_session.count()

        repeated_captured_data = CobrowseCapturedLeadData.objects.filter(search_field__in=unique_identifier_field, agent_searched=True).values(
            "primary_value").annotate(value_count=Count('primary_value')).filter(value_count__gt=1).values_list("primary_value", flat=True)

        repeated_cobrowse_io_objs = cobrowse_io_objs.filter(session_id__in=CobrowseCapturedLeadData.objects.filter(
            primary_value__in=repeated_captured_data, agent_searched=True).values_list("session_id", flat=True))

        prev_value_list = {}
        repeated_customers = 0
        for cobrowse_io_obj in repeated_cobrowse_io_objs.iterator():
            data_captured = cobrowse_io_obj.captured_lead.filter(
                agent_searched=True).first()
            if data_captured and data_captured.primary_value not in prev_value_list and repeated_captured_data.filter(primary_value=data_captured.primary_value).count():
                prev_value_list[data_captured.primary_value] = 1
                repeated_customers += 1
            else:
                continue

        for outbound_analytics_obj in outbound_analytics_objs.iterator():
            total_searched_leads += outbound_analytics_obj.searched_leads
            total_request_attended += outbound_analytics_obj.request_attended
            total_request_unattended += outbound_analytics_obj.request_unattended
            total_customer_converted += outbound_analytics_obj.customers_converted
            total_customer_converted_by_url += outbound_analytics_obj.customers_converted_by_url
            total_session_time += outbound_analytics_obj.total_session_time
            total_requests_denied_by_customers += outbound_analytics_obj.requests_denied_by_customers

            if outbound_analytics_obj.agent == admin_agent:
                total_captured_leads += outbound_analytics_obj.captured_leads

        average_session_time = get_readable_average_time(
            total_session_time, total_request_attended)

        analytics_data["captured_leads"] = total_captured_leads
        analytics_data["searched_leads"] = total_searched_leads
        analytics_data["request_attended"] = total_request_attended
        analytics_data["request_unattended"] = total_request_unattended
        analytics_data["customer_converted"] = total_customer_converted
        analytics_data["customers_converted_by_url"] = total_customer_converted_by_url
        analytics_data["avg_session_time"] = average_session_time
        analytics_data["requests_denied_by_customers"] = total_requests_denied_by_customers
        analytics_data["unique_customers"] = unique_customers
        analytics_data["repeated_customers"] = repeated_customers

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_outbound_search_lead_table_records: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})

    return analytics_data


def get_outbound_droplink_table_records(access_token, CobrowseDateWiseOutboundDroplinkAnalytics, date_interval):
    analytics_data = {
        "request_initiated": 0,
        "declined_leads": 0,
        "request_attended": 0,
        "request_unattended": 0,
        "customer_converted": 0,
        "customer_converted_by_url": 0,
        "avg_session_time": 0,
    }

    try:
        admin_agent = access_token.agent
        start_date = date_interval["start_date"]
        end_date = date_interval["end_date"]

        agent_list = get_list_agents_under_admin(
            admin_agent, is_active=None, is_account_active=None)

        outbound_analytics_objs = CobrowseDateWiseOutboundDroplinkAnalytics.objects.filter(
            agent__in=agent_list, date__gte=start_date, date__lte=end_date)

        total_request_initiated = 0
        total_request_attended = 0
        total_request_unattended = 0
        total_customer_converted = 0
        total_customer_converted_by_url = 0
        total_declined_leads = 0
        total_session_time = 0

        for outbound_analytics_obj in outbound_analytics_objs.iterator():
            total_request_initiated += outbound_analytics_obj.request_initiated
            total_request_attended += outbound_analytics_obj.request_attended
            total_request_unattended += outbound_analytics_obj.request_unattended
            total_customer_converted += outbound_analytics_obj.customers_converted
            total_customer_converted_by_url += outbound_analytics_obj.customers_converted_by_url
            total_session_time += outbound_analytics_obj.total_session_time
            total_declined_leads += outbound_analytics_obj.declined_leads

        average_session_time = get_readable_average_time(
            total_session_time, total_request_attended)

        analytics_data["request_initiated"] = total_request_initiated
        analytics_data["request_attended"] = total_request_attended
        analytics_data["request_unattended"] = total_request_unattended
        analytics_data["customer_converted"] = total_customer_converted
        analytics_data["customers_converted_by_url"] = total_customer_converted_by_url
        analytics_data["avg_session_time"] = average_session_time
        analytics_data["declined_leads"] = total_declined_leads

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_outbound_droplink_table_records: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})

    return analytics_data


def get_support_analytics_table_records(
        access_token,
        CobrowseDateWiseInboundAnalytics,
        CobrowseDateWiseOutboundAnalytics,
        CobrowseVideoConferencing,
        CobrowseVideoAuditTrail,
        date_interval):

    analytics_data = {
        "request_attended": 0,
        "request_unattended": 0,
        "declined_leads": 0,
        "followup_leads": 0,
        "customer_converted": 0,
        "customer_converted_by_url": 0,
        "total_meetings": 0,
    }

    try:
        admin_agent = access_token.agent
        start_date = date_interval["start_date"]
        end_date = date_interval["end_date"]

        agent_list = get_list_agents_under_admin(
            admin_agent, is_active=None, is_account_active=None)

        inbound_analytics_objs = CobrowseDateWiseInboundAnalytics.objects.filter(
            agent__in=agent_list, date__gte=start_date, date__lte=end_date)

        outbound_analytics_objs = CobrowseDateWiseOutboundAnalytics.objects.filter(
            agent__in=agent_list, date__gte=start_date, date__lte=end_date)

        cobrowse_video_objs = CobrowseVideoConferencing.objects.filter(
            agent__in=agent_list, meeting_start_date__gte=start_date, meeting_start_date__lte=end_date)
        total_meetings = CobrowseVideoAuditTrail.objects.filter(cobrowse_video__in=cobrowse_video_objs).count()

        total_request_attended = 0
        total_request_unattended = 0
        total_customer_converted = 0
        total_customer_converted_by_url = 0
        total_declined_leads = 0
        total_followup_leads = 0

        for inbound_analytics_obj in inbound_analytics_objs.iterator():
            total_request_attended += inbound_analytics_obj.request_attended
            total_request_unattended += inbound_analytics_obj.request_unattended
            total_customer_converted += inbound_analytics_obj.customers_converted
            total_customer_converted_by_url += inbound_analytics_obj.customers_converted_by_url
            total_declined_leads += inbound_analytics_obj.declined_leads
            total_followup_leads += inbound_analytics_obj.followup_leads

        for outbound_analytics_obj in outbound_analytics_objs.iterator():
            total_request_attended += outbound_analytics_obj.request_attended
            total_request_unattended += outbound_analytics_obj.request_unattended
            total_customer_converted += outbound_analytics_obj.customers_converted
            total_customer_converted_by_url += outbound_analytics_obj.customers_converted_by_url
            total_declined_leads += outbound_analytics_obj.requests_denied_by_customers

        analytics_data["request_attended"] = total_request_attended
        analytics_data["request_unattended"] = total_request_unattended
        analytics_data["customer_converted"] = total_customer_converted
        analytics_data["customers_converted_by_url"] = total_customer_converted_by_url
        analytics_data["declined_leads"] = total_declined_leads
        analytics_data["total_meetings"] = total_meetings
        analytics_data["followup_leads"] = total_followup_leads

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_support_analytics_table_records: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})

    return analytics_data


def get_general_mailer_analytics_data(
        access_token,
        date_interval,
        CobrowseDateWiseInboundAnalytics,
        CobrowseDateWiseOutboundAnalytics):

    analytics_data = {
        "inbound_request_initiated": 0,
        "inbound_request_attended": 0,
        "inbound_customer_converted": 0,
        "outbound_request_initiated": 0,
        "outbound_request_attended": 0,
        "outbound_customer_converted": 0,
    }

    try:

        start_date = date_interval["start_date"]
        end_date = date_interval["end_date"]

        admin_agent = access_token.agent
        agent_list = get_list_agents_under_admin(
            admin_agent, is_active=None, is_account_active=None)

        inbound_analytics_objs = CobrowseDateWiseInboundAnalytics.objects.filter(
            agent__in=agent_list, date__gte=start_date, date__lte=end_date)

        outbound_analytics_objs = CobrowseDateWiseOutboundAnalytics.objects.filter(
            agent__in=agent_list, date__gte=start_date, date__lte=end_date)

        inbound_total_request_initiated = 0
        inbound_total_request_attended = 0
        inbound_customer_converted = 0
        outbound_total_request_initiated = 0
        outbound_total_request_attended = 0
        outbound_customer_converted = 0

        for inbound_analytics_obj in inbound_analytics_objs.iterator():
            inbound_total_request_initiated += inbound_analytics_obj.request_initiated
            inbound_total_request_attended += inbound_analytics_obj.request_attended
            inbound_customer_converted += inbound_analytics_obj.customers_converted

        for outbound_analytics_obj in outbound_analytics_objs.iterator():
            outbound_total_request_initiated += outbound_analytics_obj.searched_leads
            outbound_total_request_attended += outbound_analytics_obj.request_attended
            outbound_customer_converted += outbound_analytics_obj.customers_converted

        analytics_data["inbound_request_initiated"] = inbound_total_request_initiated
        analytics_data["inbound_request_attended"] = inbound_total_request_attended
        analytics_data["inbound_customer_converted"] = inbound_customer_converted

        analytics_data["outbound_request_initiated"] = outbound_total_request_initiated
        analytics_data["outbound_request_attended"] = outbound_total_request_attended
        analytics_data["outbound_customer_converted"] = outbound_customer_converted

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_general_mailer_analytics_data: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})

    return analytics_data


def get_inbound_service_request_analytics_data(
        access_token,
        date_interval,
        CobrowseDateWiseInboundAnalytics):

    analytics_data = []
    try:

        start_date = date_interval["start_date"]
        end_date = date_interval["end_date"]

        admin_agent = access_token.agent
        agent_list = get_list_agents_under_admin(
            admin_agent, is_active=None, is_account_active=None)

        inbound_analytics_objs = CobrowseDateWiseInboundAnalytics.objects.filter(
            agent__in=agent_list, date__gte=start_date, date__lte=end_date).order_by("date")

        date_wise_analytics_data = {}
        date_obj_list = []

        for inbound_analytics_obj in inbound_analytics_objs.iterator():
            date_obj = inbound_analytics_obj.date

            if date_obj not in date_wise_analytics_data:
                date_obj_list.append(date_obj)

                date_wise_analytics_data[date_obj] = {
                    "request_initiated": 0,
                    "request_attended": 0,
                    "customer_converted": 0,
                    "request_declined": 0,
                    "date": date_obj,
                }

            date_wise_analytics_data[date_obj]["request_initiated"] += inbound_analytics_obj.request_initiated
            date_wise_analytics_data[date_obj]["request_attended"] += inbound_analytics_obj.request_attended
            date_wise_analytics_data[date_obj]["customer_converted"] += inbound_analytics_obj.customers_converted
            date_wise_analytics_data[date_obj]["customer_converted"] += inbound_analytics_obj.customers_converted_by_url
            date_wise_analytics_data[date_obj]["request_declined"] += inbound_analytics_obj.declined_leads

        for date_obj in date_obj_list:
            analytics_data.append(date_wise_analytics_data[date_obj])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_inbound_service_request_analytics_data: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})

    return analytics_data


def get_outbound_service_request_analytics_data(
        access_token,
        date_interval,
        CobrowseDateWiseOutboundAnalytics):

    analytics_data = []
    try:

        start_date = date_interval["start_date"]
        end_date = date_interval["end_date"]

        admin_agent = access_token.agent
        agent_list = get_list_agents_under_admin(
            admin_agent, is_active=None, is_account_active=None)

        outbound_analytics_objs = CobrowseDateWiseOutboundAnalytics.objects.filter(
            agent__in=agent_list, date__gte=start_date, date__lte=end_date).order_by("date")

        date_wise_analytics_data = {}
        date_obj_list = []

        for outbound_analytics_obj in outbound_analytics_objs.iterator():
            date_obj = outbound_analytics_obj.date

            if date_obj not in date_wise_analytics_data:
                date_obj_list.append(date_obj)

                date_wise_analytics_data[date_obj] = {
                    "captured_leads": 0,
                    "request_attended": 0,
                    "customer_converted": 0,
                    "request_declined": 0,
                    "date": date_obj,
                }

            date_wise_analytics_data[date_obj]["captured_leads"] += outbound_analytics_obj.captured_leads
            date_wise_analytics_data[date_obj]["request_attended"] += outbound_analytics_obj.request_attended
            date_wise_analytics_data[date_obj]["customer_converted"] += outbound_analytics_obj.customers_converted
            date_wise_analytics_data[date_obj]["customer_converted"] += outbound_analytics_obj.customers_converted_by_url
            date_wise_analytics_data[date_obj]["request_declined"] += outbound_analytics_obj.requests_denied_by_customers

        for date_obj in date_obj_list:
            analytics_data.append(date_wise_analytics_data[date_obj])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_outbound_service_request_analytics_data: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssist'})

    return analytics_data


def get_image_file_name(file_name_prefix, access_token, graph_duration):
    try:
        admin_agent = access_token.agent
        agent_username = admin_agent.user.username
        todays_date = datetime.now().date()

        image_file_name = "{}_{}days_{}_{}.jpg".format(
            file_name_prefix, graph_duration + 1, agent_username, str(todays_date))

        return image_file_name
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_image_file_name %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return "None"


def process_profile_data_and_send_email(profile_obj, access_token, start_end_date, use_static_data, CobrowseVideoAuditTrail):

    def get_days_count():
        start_date = datetime.strptime(
            start_end_date["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(
            start_end_date["end_date"], "%Y-%m-%d").date()
        total_days = (end_date - start_date).days + 1
        return total_days

    exit_status = 500
    try:
        email_id_list = profile_obj.email_address
        email_subject = profile_obj.email_subject
        include_graphs = profile_obj.include_graphs
        include_tables = profile_obj.include_tables
        include_attachment = profile_obj.include_attachment

        email_id_list = json.loads(email_id_list)
        if len(email_id_list) == 0:
            return

        graph_html = ""
        if include_graphs:
            email_analytics_graph_obj = profile_obj.analytics_graph
            graph_html = get_graphic_analytics_html(
                email_analytics_graph_obj, access_token, start_end_date, use_static_data)

        attachment_html = ""
        if include_attachment:
            email_analytics_attachment_obj = profile_obj.analytics_attachment
            attachment_html = get_attachment_html(
                profile_obj,
                email_analytics_attachment_obj,
                access_token,
                start_end_date,
                use_static_data,
                CobrowseVideoAuditTrail)

        table_html = ""
        if include_tables:
            email_analytics_table_obj = profile_obj.analytics_table
            table_html = get_email_analytics_table_html(
                email_analytics_table_obj, access_token, use_static_data, CobrowseVideoAuditTrail)

        if use_static_data:
            email_subject += " (Sample)"
            cronjob_send_email = False
        else:
            cronjob_send_email = True

        create_email_template_and_send_email(
            email_id_list, email_subject, graph_html, table_html, attachment_html, cronjob_send_email)

        if use_static_data == False:
            from EasyAssistApp.models import CobrowseMailerAnalyticsAuditTrail
            CobrowseMailerAnalyticsAuditTrail.objects.create(
                profile=profile_obj,
                sent_days_count=get_days_count()
            )

        exit_status = 200

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error process_profile_data_and_send_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return exit_status


def get_start_end_date_list(profile_obj, calendar_obj):
    from EasyAssistApp.models import CobrowseMailerAnalyticsAuditTrail
    todays_date = str(datetime.now().day)

    start_end_date_list = []

    try:
        days = json.loads(calendar_obj.days)
    except Exception:
        days = {}

    if str(todays_date) in days:
        email_frequency = days[str(todays_date)]
        for frequency in email_frequency:
            start_date = (datetime.now() -
                          timedelta(days=int(frequency))).date()
            end_date = (datetime.now() - timedelta(days=1)).date()
            sent_days_count = (end_date - start_date).days + 1

            audit_trail_objs = CobrowseMailerAnalyticsAuditTrail.objects.filter(
                profile=profile_obj, datetime__date__gt=start_date, sent_days_count=sent_days_count)
            if not audit_trail_objs.count():
                start_end_date_list.append({
                    "start_date": str(start_date),
                    "end_date": str(end_date)
                })

    return start_end_date_list


def process_data_according_to_mailer_calendar(profile_obj, access_token, CobrowseVideoAuditTrail):
    try:
        from EasyAssistApp.models import CobrowseMailerAnalyticsCalendar
        calendar_obj = CobrowseMailerAnalyticsCalendar.objects.filter(
            profile=profile_obj).first()

        if calendar_obj == None:
            return

        start_end_date_list = get_start_end_date_list(
            profile_obj, calendar_obj)

        for start_end_date in start_end_date_list:
            process_profile_data_and_send_email(
                profile_obj, access_token, start_end_date, False, CobrowseVideoAuditTrail)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error process_data_according_to_mailer_calendar %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def create_email_template_and_send_email(email_id_list, email_subject, graph_html, table_html, attachment_html, cronjob_send_email):
    try:

        config = get_developer_console_settings()

        legal_name = config.legal_name
        cognoai_logo_url = settings.EASYCHAT_HOST_URL + config.login_logo
        if config.login_logo == GENERAL_LOGIN_LOGO:
            cognoai_logo_url = settings.EASYCHAT_HOST_URL + COGNOAI_LOGO_PATH
        todays_date = (datetime.now() - timedelta(days=1)).date()
        todays_date = todays_date.strftime("%B %d, %Y")

        email_body_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Email</title>
</head>
<body style="{body_css}">
    <div style="{container_css}">
        <div style="{header_css}">
            <img src="{cognoai_logo_url}" style="{header_img_css}" height="47">
        </div>
        <div>
            <div style="{content_title_container_css}">
                <div style="{content_title_text_css}">Here's usage analytics for your Cobrowser</div>
                <div style="{content_title_date_css}">{todays_date}</div>
            </div>
            {graph_html}
            {table_html}
            {attachment_html}
        </div>
        <div style="{footer_css}">
            <div style="{footer_text_bold_css}">© Copyright 2022 {legal_name}</div>
            <div style="{footer_text_css}">Visit our website to know more about us at: 
            <a href="https://www.getcogno.ai" style="{footer_link_css}">www.getcogno.ai</a></div>
        </div>
    </div>
</body>
</html>
    """.format(
            body_css=BODY_CSS,
            container_css=CONTAINER_CSS,
            header_css=HEADER_CSS,
            header_img_css=HEADER_IMG_CSS,
            content_title_container_css=CONTENT_TITLE_CONTAINER_CSS,
            content_title_text_css=CONTENT_TITLE_TEXT_CSS,
            content_title_date_css=CONTENT_TITLE_DATE_CSS,
            footer_css=FOOTER_CSS,
            footer_text_bold_css=FOOTER_TEXT_BOLD_CSS,
            footer_text_css=FOOTER_TEXT_CSS,
            footer_link_css=FOOTER_LINK_CSS,
            legal_name=legal_name,
            cognoai_logo_url=cognoai_logo_url,
            todays_date=todays_date,
            graph_html=graph_html,
            table_html=table_html,
            attachment_html=attachment_html)

        for email_id in email_id_list:
            if cronjob_send_email == False:
                # Trigger Sample Email
                thread = threading.Thread(target=send_analytics_over_email, args=(
                    email_id, email_subject, email_body_html), daemon=True)
                thread.start()
            else:
                # cronjob
                send_analytics_over_email(
                    email_id, email_subject, email_body_html)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_email_template_and_send_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def get_graphic_analytics_date_interval(start_end_date):
    try:
        start_date = datetime.strptime(start_end_date["start_date"], DATE_TIME_FORMAT).date()
        end_date = datetime.strptime(start_end_date["end_date"], DATE_TIME_FORMAT).date()

        graph_duration = (end_date - start_date).days

        if graph_duration:
            end_date = datetime.now().date()
            start_date = (datetime.now() - timedelta(days=7)).date()
        
        date_interval = {
            "start_date": start_date,
            "end_date": end_date,
        }
        return date_interval
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_graphic_analytics_date_interval %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return None


def get_graphic_analytics_html(email_analytics_graph_obj, access_token, start_end_date, use_static_data):
    try:
        image_urls = get_graphic_analytics_image_urls(
            email_analytics_graph_obj, access_token, start_end_date, use_static_data)
        graph_html = ""

        for image_url in image_urls:
            graph_html += """
            <div style="{content_graph_css}">
                <div style="{graph_container_css}">
                    <img src="{image_url}" style="{graph_container_img_css}">
                </div>
            </div>
            """.format(
                content_graph_css=CONTENT_GRAPH_CSS,
                graph_container_css=GRAPH_CONTAINER_CSS,
                graph_container_img_css=GRAPH_CONTAINER_IMG_CSS,
                image_url=image_url)

        return graph_html

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_graphic_analytics_html %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return ""


def get_graphic_analytics_image_urls(
        email_analytics_graph_obj,
        access_token,
        start_end_date,
        use_static_data):

    from EasyAssistApp.models import CobrowseDateWiseInboundAnalytics, CobrowseDateWiseOutboundAnalytics

    try:
        if email_analytics_graph_obj is None:
            return []

        graph_records = json.loads(email_analytics_graph_obj.records)

        general_graph_image_urls = []
        inbound_graph_image_urls = []
        outbound_graph_image_urls = []

        if "general_analytics" in graph_records:
            general_graph_image_urls = get_general_analytics_graph_urls(
                graph_records["general_analytics"],
                access_token,
                CobrowseDateWiseInboundAnalytics,
                CobrowseDateWiseOutboundAnalytics,
                start_end_date,
                use_static_data)

        if "inbound_analytics" in graph_records:
            inbound_graph_image_urls = get_inbound_analytics_graph_urls(
                graph_records["inbound_analytics"],
                access_token,
                CobrowseDateWiseInboundAnalytics,
                start_end_date,
                use_static_data)

        if "outbound_analytics" in graph_records:
            outbound_graph_image_urls = get_outbound_analytics_graph_urls(
                graph_records["outbound_analytics"],
                access_token,
                CobrowseDateWiseOutboundAnalytics,
                start_end_date,
                use_static_data)

        graph_image_urls = general_graph_image_urls + \
            inbound_graph_image_urls + outbound_graph_image_urls

        return graph_image_urls

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_graphic_analytics_image_urls %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return []


def get_general_analytics_graph_urls(
        graph_records,
        access_token,
        CobrowseDateWiseInboundAnalytics,
        CobrowseDateWiseOutboundAnalytics,
        start_end_date,
        use_static_data):

    try:
        image_urls = []

        if use_static_data == True:
            image_urls = get_static_general_analytics_graph_urls(graph_records)

        else:
            image_urls = get_real_general_analytics_graph_urls(
                graph_records,
                access_token,
                CobrowseDateWiseInboundAnalytics,
                CobrowseDateWiseOutboundAnalytics,
                start_end_date)

        return image_urls

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_general_analytics_graph_urls %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return []


def get_static_general_analytics_graph_urls(graph_records):
    try:
        image_urls = []

        if "request_details" in graph_records:
            image_url = settings.EASYCHAT_HOST_URL + \
                "/files/EasyAssistApp/img/request_details.jpg"
            image_urls.append(image_url)

        if "customer_session_details" in graph_records:
            image_url = settings.EASYCHAT_HOST_URL + \
                "/files/EasyAssistApp/img/customer_session_details.jpg"
            image_urls.append(image_url)

        return image_urls

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_static_general_analytics_graph_urls %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return []


def get_real_general_analytics_graph_urls(
        graph_records,
        access_token,
        CobrowseDateWiseInboundAnalytics,
        CobrowseDateWiseOutboundAnalytics,
        start_end_date):

    try:
        image_urls = []

        if "request_details" in graph_records:
            image_url = get_general_request_analytics_graph(
                graph_records["request_details"],
                access_token,
                CobrowseDateWiseInboundAnalytics,
                CobrowseDateWiseOutboundAnalytics,
                start_end_date)

            if image_url is not None:
                image_urls.append(image_url)

        if "customer_session_details" in graph_records:
            image_url = get_general_customer_session_analytics_graph(
                graph_records["customer_session_details"],
                access_token,
                CobrowseDateWiseInboundAnalytics,
                CobrowseDateWiseOutboundAnalytics,
                start_end_date)

            if image_url is not None:
                image_urls.append(image_url)

        return image_urls

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_real_general_analytics_graph_urls %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return []


def get_general_request_analytics_graph(
        records,
        access_token,
        CobrowseDateWiseInboundAnalytics,
        CobrowseDateWiseOutboundAnalytics,
        start_end_date):

    try:
        date_interval = get_graphic_analytics_date_interval(start_end_date)
        graph_duration = (
            date_interval["end_date"] - date_interval["start_date"]).days
        
        if graph_duration > 1:
            image_file_name = get_image_file_name(
                "request_details", access_token, graph_duration - 1)
        else:
            image_file_name = get_image_file_name(
                "request_details", access_token, graph_duration)

        analytics_data = get_general_mailer_analytics_data(
            access_token,
            date_interval,
            CobrowseDateWiseInboundAnalytics,
            CobrowseDateWiseOutboundAnalytics)

        if graph_duration:
            formatted_start_date = date_interval["start_date"].strftime(
                DATE_TIME_FORMAT_5)
            formatted_end_date = (date_interval["end_date"] - timedelta(days=1)).strftime(
                DATE_TIME_FORMAT_5)
            formatted_date_interval = formatted_start_date + " - " + formatted_end_date
        else:
            formatted_date_interval = date_interval["end_date"].strftime(
                DATE_TIME_FORMAT_5)

        inbound_analytics_data = []
        outbound_analytics_data = []
        analytics_x_axis_label = []

        if "initiated" in records:
            inbound_analytics_data.append(
                analytics_data["inbound_request_initiated"])
            outbound_analytics_data.append(
                analytics_data["outbound_request_initiated"])
            analytics_x_axis_label.append("Request Initiated")

        if "attended" in records:
            inbound_analytics_data.append(
                analytics_data["inbound_request_attended"])
            outbound_analytics_data.append(
                analytics_data["outbound_request_attended"])
            analytics_x_axis_label.append("Request Attended")

        if "converted" in records:
            inbound_analytics_data.append(
                analytics_data["inbound_customer_converted"])
            outbound_analytics_data.append(
                analytics_data["outbound_customer_converted"])
            analytics_x_axis_label.append("Customer Converted")

        graph_title = "Request Details<br><sup>{}</sup>".format(
            formatted_date_interval)

        if sum(inbound_analytics_data) + sum(outbound_analytics_data):
            plot = go.Figure(
                data=[
                    go.Bar(
                        name='Inbound',
                        x=analytics_x_axis_label,
                        y=inbound_analytics_data,
                        text=inbound_analytics_data,
                        textposition="auto",
                        marker_color="#0254d7",
                        textfont_size=14,
                        textfont_color="white"
                    ),
                    go.Bar(
                        name='Outbound',
                        x=analytics_x_axis_label,
                        y=outbound_analytics_data,
                        text=outbound_analytics_data,
                        textposition="auto",
                        marker_color="#6798e7",
                        textfont_size=14,
                        textfont_color="white"
                    )
                ],
                layout=go.Layout(
                    title=go.layout.Title(
                        text=graph_title,
                        font=go.layout.title.Font(color='#0036B5')
                    )
                )
            )

            plot.update_layout(barmode="group")
        else:
            plot = get_no_data_available_image(graph_title)

        file_path = ANALYTICS_FOLDER_PATH + image_file_name
        file_relative_path = ANALYTICS_FOLDER_RELATIVE_PATH + image_file_name
        plot.write_image(file_path)

        file_relative_path = settings.EASYCHAT_HOST_URL + "/" + file_relative_path
        return file_relative_path

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_general_request_analytics_graph %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return None


def get_general_customer_session_analytics_graph(
        records,
        access_token,
        CobrowseDateWiseInboundAnalytics,
        CobrowseDateWiseOutboundAnalytics,
        start_end_date):

    try:
        date_interval = get_graphic_analytics_date_interval(start_end_date)
        graph_duration = (
            date_interval["end_date"] - date_interval["start_date"]).days
        
        if graph_duration > 1:
            image_file_name = get_image_file_name(
                "customer_session_details_", access_token, graph_duration - 1)
        else:
            image_file_name = get_image_file_name(
                "customer_session_details_", access_token, graph_duration)

        analytics_data = get_general_mailer_analytics_data(
            access_token,
            date_interval,
            CobrowseDateWiseInboundAnalytics,
            CobrowseDateWiseOutboundAnalytics)

        if graph_duration:
            formatted_start_date = date_interval["start_date"].strftime(
                DATE_TIME_FORMAT_5)
            formatted_end_date = (date_interval["end_date"] - timedelta(days=1)).strftime(
                DATE_TIME_FORMAT_5)
            formatted_date_interval = formatted_start_date + " - " + formatted_end_date
        else:
            formatted_date_interval = date_interval["end_date"].strftime(
                DATE_TIME_FORMAT_5)

        analytics_graph_values = [
            analytics_data["inbound_request_attended"],
            analytics_data["outbound_request_attended"]
        ]

        analytics_x_axis_label = [
            "Inbound Analytics",
            "Outbound Analytics"
        ]

        graph_title = "Customer Session Attended<br><sup>{}</sup>".format(
            formatted_date_interval)

        plot = go.Figure(
            data=[
                go.Pie(
                    labels=analytics_x_axis_label,
                    values=analytics_graph_values)
            ],
            layout=go.Layout(
                title=go.layout.Title(
                    text=graph_title,
                    font=go.layout.title.Font(color='#0036B5')
                )
            )
        )

        pie_colors = ["#0254d7", "#6798e7"]
        plot.update_traces(
            marker=dict(colors=pie_colors),
            textfont_color="white",
            textfont_size=16
        )

        if not sum(analytics_graph_values):
            plot = get_no_data_available_image(graph_title)

        file_path = ANALYTICS_FOLDER_PATH + image_file_name
        file_relative_path = ANALYTICS_FOLDER_RELATIVE_PATH + image_file_name
        plot.write_image(file_path)

        file_relative_path = settings.EASYCHAT_HOST_URL + "/" + file_relative_path
        return file_relative_path

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_general_customer_session_analytics_graph %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return None


def get_inbound_analytics_graph_urls(
        graph_records,
        access_token,
        CobrowseDateWiseInboundAnalytics,
        start_end_date,
        use_static_data):

    try:
        image_urls = []

        if use_static_data == True:
            image_urls = get_static_inbound_analytics_graph_urls(graph_records)
        else:
            image_urls = get_real_inbound_analytics_graph_urls(
                graph_records,
                access_token,
                CobrowseDateWiseInboundAnalytics,
                start_end_date)

        return image_urls
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_inbound_analytics_graph_urls %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return []


def get_static_inbound_analytics_graph_urls(graph_records):
    try:
        image_urls = []

        if "service_request_analytics" in graph_records:
            image_url = settings.EASYCHAT_HOST_URL + \
                "/files/EasyAssistApp/img/inbound_service_request.jpg"
            image_urls.append(image_url)

        return image_urls

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_static_inbound_analytics_graph_urls %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return []


def get_real_inbound_analytics_graph_urls(
        graph_records,
        access_token,
        CobrowseDateWiseInboundAnalytics,
        start_end_date):

    try:
        image_urls = []

        if "service_request_analytics" in graph_records:
            image_url = get_inbound_service_request_analytics_graph(
                graph_records["service_request_analytics"],
                access_token,
                CobrowseDateWiseInboundAnalytics,
                start_end_date)

            if image_url is not None:
                image_urls.append(image_url)

        return image_urls

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_real_inbound_analytics_graph_urls %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return []


def get_inbound_service_request_analytics_graph(
        records,
        access_token,
        CobrowseDateWiseInboundAnalytics,
        start_end_date):

    try:
        date_interval = get_graphic_analytics_date_interval(start_end_date)
        graph_duration = (
            date_interval["end_date"] - date_interval["start_date"]).days

        if graph_duration > 1:
            image_file_name = get_image_file_name(
                "inbound_service_request", access_token, graph_duration - 1)
        else:
            image_file_name = get_image_file_name(
                "inbound_service_request", access_token, graph_duration)

        analytics_data = get_inbound_service_request_analytics_data(
            access_token,
            date_interval,
            CobrowseDateWiseInboundAnalytics)

        if graph_duration:
            formatted_start_date = date_interval["start_date"].strftime(
                DATE_TIME_FORMAT_5)
            formatted_end_date = (date_interval["end_date"] - timedelta(days=1)).strftime(
                DATE_TIME_FORMAT_5)
            formatted_date_interval = formatted_start_date + " - " + formatted_end_date
        else:
            formatted_date_interval = date_interval["end_date"].strftime(
                DATE_TIME_FORMAT_5)

        analytics_x_axis_label = []
        analytics_x_axis_date_label = []
        request_initiated_data = []
        request_attended_data = []
        request_declined_data = []
        customer_converted_data = []

        for analytics_obj in analytics_data:
            date_obj = analytics_obj["date"]

            formatted_date = date_obj.strftime("%d %b %Y")
            analytics_x_axis_date_label.append(formatted_date)

            request_initiated_data.append(analytics_obj["request_initiated"])
            request_attended_data.append(analytics_obj["request_attended"])
            request_declined_data.append(analytics_obj["request_declined"])
            customer_converted_data.append(analytics_obj["customer_converted"])

        if not graph_duration:
            analytics_x_axis_label = ["Leads<br>Captured", "Co-browsing<br>Request Attended",
                                      "Customers<br>Converted", "Requests Declined<br>by the Customer"]
            request_initiated_data = sum(request_initiated_data)
            request_attended_data = sum(request_attended_data)
            customer_converted_data = sum(customer_converted_data)
            request_declined_data = sum(request_declined_data)

            analytics_bar_chart_data = [
                request_initiated_data, request_attended_data, customer_converted_data, request_declined_data]

        graph_title = "Service Request Analytics (Inbound)<br><sup>{}</sup>".format(
            formatted_date_interval)

        show_no_data_available_image = False

        if graph_duration:
            analytics_bar_chart_data = [sum(request_attended_data), sum(
                request_initiated_data), sum(customer_converted_data), sum(request_declined_data)]
            if not sum(analytics_bar_chart_data):
                show_no_data_available_image = True
            else:
                plot = go.Figure(
                    layout=go.Layout(
                        title=go.layout.Title(
                            text=graph_title,
                            font=go.layout.title.Font(color='#0036B5')
                        )
                    )
                )

                if "lead_captured" in records:
                    plot.add_trace(
                        go.Scatter(
                            x=analytics_x_axis_date_label,
                            y=request_initiated_data,
                            mode=LINES_MARKERS,
                            name='Leads Captured'
                        )
                    )

                if "request_attended" in records:
                    plot.add_trace(
                        go.Scatter(
                            x=analytics_x_axis_date_label,
                            y=request_attended_data,
                            mode=LINES_MARKERS,
                            name='Co-browsing Request Attended'
                        )
                    )

                if "customer_converted" in records:
                    plot.add_trace(
                        go.Scatter(
                            x=analytics_x_axis_date_label,
                            y=customer_converted_data,
                            mode=LINES_MARKERS,
                            name='Customer Converted'
                        )
                    )

                if "request_declined" in records:
                    plot.add_trace(
                        go.Scatter(
                            x=analytics_x_axis_date_label,
                            y=request_declined_data,
                            mode=LINES_MARKERS,
                            name='Request declined by the Customer'
                        )
                    )

                plot.update_layout(
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.25,
                        xanchor="right",
                        x=1
                    )
                )
        else:
            if sum(analytics_bar_chart_data):
                plot = go.Figure(
                    data=[
                        go.Bar(
                            name='Inbound Analytics',
                            x=analytics_x_axis_label,
                            y=analytics_bar_chart_data,
                            text=analytics_bar_chart_data,
                            textposition="inside",
                            marker_color="#0254d7",
                            textfont_size=14,
                            textfont_color="white",
                            showlegend=True,
                        ),
                    ],
                    layout=go.Layout(
                        title=go.layout.Title(
                            text=graph_title,
                            font=go.layout.title.Font(color='#0036B5')
                        )
                    )
                )

                plot.update_traces(width=0.6)
            else:
                show_no_data_available_image = True

        if show_no_data_available_image:
            plot = get_no_data_available_image(graph_title)

        file_path = ANALYTICS_FOLDER_PATH + image_file_name
        file_relative_path = ANALYTICS_FOLDER_RELATIVE_PATH + image_file_name
        plot.write_image(file_path)

        file_relative_path = settings.EASYCHAT_HOST_URL + "/" + file_relative_path
        return file_relative_path

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_inbound_service_request_analytics_graph %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return None


def get_outbound_analytics_graph_urls(
        graph_records,
        access_token,
        CobrowseDateWiseOutboundAnalytics,
        start_end_date,
        use_static_data):

    try:
        image_urls = []

        if use_static_data == True:
            image_urls = get_static_outbound_analytics_graph_urls(
                graph_records)

        else:
            image_urls = get_real_outbound_analytics_graph_urls(
                graph_records,
                access_token,
                CobrowseDateWiseOutboundAnalytics,
                start_end_date)

        return image_urls

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_inbound_service_request_analytics_graph %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return []


def get_static_outbound_analytics_graph_urls(graph_records):
    try:
        image_urls = []

        if "service_request_analytics" in graph_records:
            image_url = settings.EASYCHAT_HOST_URL + \
                "/files/EasyAssistApp/img/outbound_service_request.jpg"
            image_urls.append(image_url)

        return image_urls

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_static_general_analytics_graph_urls %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return []


def get_real_outbound_analytics_graph_urls(graph_records, access_token, CobrowseDateWiseOutboundAnalytics, start_end_date):
    try:
        image_urls = []

        if "service_request_analytics" in graph_records:
            image_url = get_outbound_service_request_analytics_graph(
                graph_records["service_request_analytics"],
                access_token,
                CobrowseDateWiseOutboundAnalytics, start_end_date)

            if image_url is not None:
                image_urls.append(image_url)

        return image_urls

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_real_general_analytics_graph_urls %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return []


def get_outbound_service_request_analytics_graph(
        records,
        access_token,
        CobrowseDateWiseOutboundAnalytics,
        start_end_date):

    try:
        date_interval = get_graphic_analytics_date_interval(start_end_date)
        graph_duration = (
            date_interval["end_date"] - date_interval["start_date"]).days
        
        if graph_duration > 1:
            image_file_name = get_image_file_name(
                "outbound_service_request", access_token, graph_duration - 1)
        else:
            image_file_name = get_image_file_name(
                "outbound_service_request", access_token, graph_duration)

        analytics_data = get_outbound_service_request_analytics_data(
            access_token,
            date_interval,
            CobrowseDateWiseOutboundAnalytics)

        if graph_duration:
            formatted_start_date = date_interval["start_date"].strftime(
                DATE_TIME_FORMAT_5)
            formatted_end_date = (date_interval["end_date"] - timedelta(days=1)).strftime(
                DATE_TIME_FORMAT_5)
            formatted_date_interval = formatted_start_date + " - " + formatted_end_date
        else:
            formatted_date_interval = date_interval["end_date"].strftime(
                DATE_TIME_FORMAT_5)

        analytics_x_axis_label = []
        analytics_x_axis_date_label = []
        request_initiated_data = []
        request_attended_data = []
        request_declined_data = []
        customer_converted_data = []

        for analytics_obj in analytics_data:
            date_obj = analytics_obj["date"]

            formatted_date = date_obj.strftime("%d %b %Y")
            analytics_x_axis_date_label.append(formatted_date)

            request_initiated_data.append(analytics_obj["captured_leads"])
            request_attended_data.append(analytics_obj["request_attended"])
            request_declined_data.append(analytics_obj["request_declined"])
            customer_converted_data.append(
                analytics_obj["customer_converted"])

        if not graph_duration:
            analytics_x_axis_label = ["Leads<br>Captured", "Co-browsing<br>Request Attended",
                                      "Customers<br>Converted", "Requests Declined<br>by the Customer"]
            request_initiated_data = sum(request_initiated_data)
            request_attended_data = sum(request_attended_data)
            request_declined_data = sum(request_declined_data)
            customer_converted_data = sum(customer_converted_data)

            analytics_bar_chart_data = [
                request_initiated_data, request_attended_data, customer_converted_data, request_declined_data]

        graph_title = "Service Request Analytics (Outbound)<br><sup>{}</sup>".format(
            formatted_date_interval)

        show_no_data_available_image = False
        if graph_duration:
            analytics_bar_chart_data = [sum(request_initiated_data), sum(
                request_attended_data), sum(request_declined_data), sum(customer_converted_data)]
            if not sum(analytics_bar_chart_data):
                show_no_data_available_image = True
            else:
                plot = go.Figure(
                    layout=go.Layout(
                        title=go.layout.Title(
                            text=graph_title,
                            font=go.layout.title.Font(color='#0036B5')
                        )
                    )
                )

                if "lead_captured" in records:
                    plot.add_trace(
                        go.Scatter(
                            x=analytics_x_axis_date_label,
                            y=request_initiated_data,
                            mode=LINES_MARKERS,
                            name='Leads Captured'
                        )
                    )

                if "request_attended" in records:
                    plot.add_trace(
                        go.Scatter(
                            x=analytics_x_axis_date_label,
                            y=request_attended_data,
                            mode=LINES_MARKERS,
                            name='Co-browsing Request Attended'
                        )
                    )

                if "customer_converted" in records:
                    plot.add_trace(
                        go.Scatter(
                            x=analytics_x_axis_date_label,
                            y=customer_converted_data,
                            mode=LINES_MARKERS,
                            name='Customer Converted'
                        )
                    )

                if "request_declined" in records:
                    plot.add_trace(
                        go.Scatter(
                            x=analytics_x_axis_date_label,
                            y=request_declined_data,
                            mode=LINES_MARKERS,
                            name='Request declined by the Customer'
                        )
                    )

                plot.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.25,
                    xanchor="right",
                    x=1
                )
                )
        else:
            if sum(analytics_bar_chart_data):
                plot = go.Figure(
                    data=[
                        go.Bar(
                            name='Outbound Analytics',
                            x=analytics_x_axis_label,
                            y=analytics_bar_chart_data,
                            text=analytics_bar_chart_data,
                            textposition="inside",
                            marker_color="#6798e7",
                            textfont_size=14,
                            textfont_color="white",
                            showlegend=True,
                        ),
                    ],
                    layout=go.Layout(
                        title=go.layout.Title(
                            text=graph_title,
                            font=go.layout.title.Font(color='#0036B5')
                        )
                    )
                )

                plot.update_traces(width=0.6)
            else:
                show_no_data_available_image = True

        if show_no_data_available_image:
            plot = get_no_data_available_image(graph_title)

        file_path = ANALYTICS_FOLDER_PATH + image_file_name
        file_relative_path = ANALYTICS_FOLDER_RELATIVE_PATH + image_file_name
        plot.write_image(file_path)

        file_relative_path = settings.EASYCHAT_HOST_URL + "/" + file_relative_path
        return file_relative_path

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_outbound_service_request_analytics_graph %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return None


def get_attachment_html(profile_obj, email_analytics_attachment_obj, access_token, start_end_date, use_static_data, CobrowseVideoAuditTrail):
    try:
        button_objs = get_attachment_button_objs(
            profile_obj, email_analytics_attachment_obj, access_token, start_end_date, use_static_data, CobrowseVideoAuditTrail)
        attachment_html = '<div style="background: #F9F9F9; padding: 2em; text-align: center; border-bottom: 1px solid #E6e6e6;">'

        for button_obj in button_objs:
            attachment_html += """
                <button type="button" style="{attachment_button_css}">
                    <a href="{url}" style="{attachment_link_css}">
                        {name}
                    </a>
                </button>
            """.format(
                attachment_button_css=ATTACHMENT_BUTTON_CSS,
                attachment_link_css=ATTACHMENT_HYPERLINK_CSS,
                name=button_obj['name'],
                url=button_obj['url']
            )

        attachment_html += "</div>"

        return attachment_html

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_outbound_service_request_analytics_graph %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return ""


def get_attachment_button_objs(profile_obj, email_analytics_attachment_obj, access_token, start_end_date, use_static_data, CobrowseVideoAuditTrail):

    try:
        from EasyAssistApp.models import CobrowseIO

        from EasyAssistApp.utils import get_custom_support_history, \
            get_custom_unattended_leads_history, \
            get_custom_declined_leads_history, \
            get_custom_followup_leads_history, \
            get_agent_wise_bifurcation, \
            get_data_dump_in_one_file

        if use_static_data == True:
            todays_date = datetime.now().date()
            todays_date = str(todays_date)
            requested_data = {
                "startdate": todays_date,
                "enddate": todays_date,
            }
        else:
            requested_data = {
                "startdate": start_end_date["start_date"],
                "enddate": start_end_date["end_date"]
            }

        def get_attended_leads_button_object():
            relative_path = get_custom_support_history(
                requested_data, access_token.agent, CobrowseIO)
            if relative_path != NO_DATA:
                download_path = get_file_download_path(relative_path, access_token)
            else:
                download_path = get_file_download_path(NO_DATA_PDF_PATH, access_token)    
            return {
                "name": "Attended Leads",
                "url": download_path
            }

        def get_unattended_leads_button_object():
            relative_path = get_custom_unattended_leads_history(
                requested_data, access_token.agent, CobrowseIO)
            if relative_path != NO_DATA:
                download_path = get_file_download_path(relative_path, access_token)
            else:
                download_path = get_file_download_path(NO_DATA_PDF_PATH, access_token)
            return {
                "name": "Unattended Leads",
                "url": download_path
            }

        def get_declined_leads_button_object():
            relative_path = get_custom_declined_leads_history(
                requested_data, access_token.agent, CobrowseIO)
            if relative_path != NO_DATA:
                download_path = get_file_download_path(relative_path, access_token)
            else:
                download_path = get_file_download_path(NO_DATA_PDF_PATH, access_token)
            return {
                "name": Declined_Leads,
                "url": download_path
            }

        def get_followup_leads_button_object():
            relative_path = get_custom_followup_leads_history(
                requested_data, access_token.agent, CobrowseIO)
            if relative_path != NO_DATA:
                download_path = get_file_download_path(relative_path, access_token)
            else:
                download_path = get_file_download_path(NO_DATA_PDF_PATH, access_token)
            return {
                "name": "Followup Leads",
                "url": download_path
            }

        def get_agent_wise_reports_button_object():
            relative_path = get_agent_wise_bifurcation(
                requested_data, access_token.agent, CobrowseIO)
            if relative_path != NO_DATA:
                download_path = get_file_download_path(relative_path, access_token)
            else:
                download_path = get_file_download_path(NO_DATA_PDF_PATH, access_token)
            return {
                "name": "Agent Wise Bifurcation",
                "url": download_path
            }

        def get_data_into_single_file():
            relative_path = get_data_dump_in_one_file(
                requested_data, access_token.agent, attachment_records)
            if relative_path != NO_DATA:
                download_path = get_file_download_path(relative_path, access_token)
            else:
                download_path = get_file_download_path(NO_DATA_PDF_PATH, access_token)
            return {
                "name": "Download Reports",
                "url": download_path
            }

        def get_mailer_analytics_report_button_object():
            relative_path = get_mailer_analytics_excel_data(
                profile_obj, requested_data, access_token, use_static_data, CobrowseVideoAuditTrail)

            if relative_path is None:
                return

            download_path = get_file_download_path(relative_path, access_token)
            return {
                "name": "Download Summary",
                "url": download_path
            }

        button_objs = []

        attachment_records = json.loads(email_analytics_attachment_obj.records)

        if email_analytics_attachment_obj.use_single_file == True:
            button_objs += [get_data_into_single_file()]
        else:
            if "attended_leads" in attachment_records:
                button_objs += [get_attended_leads_button_object()]
            if "unattended_leads" in attachment_records:
                button_objs += [get_unattended_leads_button_object()]
            if "declined_leads" in attachment_records:
                button_objs += [get_declined_leads_button_object()]
            if "followup_leads" in attachment_records:
                button_objs += [get_followup_leads_button_object()]
            if "agent_wise_reports" in attachment_records:
                button_objs += [get_agent_wise_reports_button_object()]

            if profile_obj.include_mailer_analytics_attachment:
                button_obj = get_mailer_analytics_report_button_object()
                if button_obj:
                    button_objs += [button_obj]

        return button_objs
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_attachment_button_objs %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return []


def get_file_download_path(file_relative_path, access_token):
    try:
        from EasyAssistApp.models import CobrowsingFileAccessManagement

        file_path = "/" + file_relative_path

        file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
            file_path=file_path, is_public=True, access_token=access_token)

        return settings.EASYCHAT_HOST_URL + '/easy-assist/download-file/' + str(file_access_management_obj.key)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_file_download_path %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return None


def get_date_interval_from_count_variation(count_variation):
    try:
        end_date = datetime.now().date()
        start_date = datetime.now().date()
        if count_variation == "ytd":  # Year to date
            start_date = datetime.now().date().replace(month=1, day=1)

        elif count_variation == "mtd":  # Month to date
            start_date = datetime.now().date().replace(day=1)

        elif count_variation == "wtd":  # Week to date
            start_date = (datetime.now() - timedelta(days=7)).date()

        else:  # daily
            start_date = (datetime.now() - timedelta(days=1)).date()

        return {
            "start_date": start_date,
            "end_date": end_date,
        }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_datetime_interval_from_count_variation %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return {
            "start_date": datetime.now().date(),
            "end_date": datetime.now().date(),
        }


def get_email_analytics_table_html(email_analytics_table_obj, access_token, use_static_data, CobrowseVideoAuditTrail):
    try:
        from EasyAssistApp.models import CobrowseDateWiseInboundAnalytics,\
            CobrowseDateWiseOutboundAnalytics,\
            CobrowseDateWiseOutboundDroplinkAnalytics,\
            CobrowseVideoConferencing

        if email_analytics_table_obj is None:
            return ""

        count_variations = email_analytics_table_obj.count_variation
        count_variations = json.loads(count_variations)

        table_records = json.loads(email_analytics_table_obj.records)

        inbound_table_html = ""
        outbound_search_lead_table_html = ""
        outbound_droplink_table_html = ""
        support_table_html = ""

        if "inbound" in table_records:
            inbound_table_html = get_inbound_table_html(
                table_records["inbound"],
                access_token,
                count_variations,
                CobrowseDateWiseInboundAnalytics,
                use_static_data)

        if "outbound_search_leads" in table_records:
            outbound_search_lead_table_html = get_outbound_table_html(
                table_records["outbound_search_leads"],
                access_token,
                count_variations,
                CobrowseDateWiseOutboundAnalytics,
                use_static_data)

        if "outbound_gdl" in table_records:
            outbound_droplink_table_html = get_outbound_droplink_table_html(
                table_records["outbound_gdl"],
                access_token,
                count_variations,
                CobrowseDateWiseOutboundDroplinkAnalytics,
                use_static_data)

        if "support" in table_records:
            support_table_html = get_support_table_html(
                table_records["support"],
                access_token,
                count_variations,
                CobrowseDateWiseInboundAnalytics,
                CobrowseDateWiseOutboundAnalytics,
                CobrowseVideoConferencing,
                CobrowseVideoAuditTrail,
                use_static_data)

        table_html = inbound_table_html + outbound_search_lead_table_html + \
            outbound_droplink_table_html + support_table_html

        return table_html

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_email_analytics_table_html %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return ""


def get_analytics_data_column_html(record_id, record_name, analytics_data, count_variations):
    try:
        html = ""
        td_html = ""
        for count_variation in count_variations:
            td_html += "<td style='{table_td_css}'>{data_value}</td>".format(
                table_td_css=TABLE_TD_CSS,
                data_value=analytics_data[count_variation][record_id],
            )

        html += "<tr><th>{record_name}</th>{td_html}</tr>".format(
            record_name=record_name,
            td_html=td_html
        )

        return html
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_analytics_data_column_html %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return ""


def get_count_variation_row_html(count_variations):
    try:
        count_variation_html = ""
        for count_variation in count_variations:
            if count_variation == "ytd":
                count_variation_html += "<td style='{count_variation_title_css}'>YTD</td>".format(
                    count_variation_title_css=COUNT_VARIATION_TITLE_CSS)

            elif count_variation == "mtd":
                count_variation_html += "<td style='{count_variation_title_css}'>MTD</td>".format(
                    count_variation_title_css=COUNT_VARIATION_TITLE_CSS)

            elif count_variation == "wtd":
                count_variation_html += "<td style='{count_variation_title_css}'>WTD</td>".format(
                    count_variation_title_css=COUNT_VARIATION_TITLE_CSS)

            else:
                count_variation_html += "<td style='{count_variation_title_css}'>Daily</td>".format(
                    count_variation_title_css=COUNT_VARIATION_TITLE_CSS)

        html = "<tr><th></th>{}</tr>".format(count_variation_html)
        return html
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_count_variation_row_html %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return ""


def get_sample_inbound_table_records():
    try:
        analytics_data = {
            "request_initiated": 10,
            "request_attended": 5,
            "request_unattended": 3,
            "followup_leads": 2,
            "declined_leads": 3,
            "customer_converted": 2,
            "customers_converted_by_url": 2,
            "avg_session_time": "1 min",
            "request_assistance_avg_wait_time": "1 min",
            "unique_customers": 2,
            "repeated_customers": 5,
        }
        return analytics_data

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_sample_inbound_table_records %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return {}


def get_inbound_table_html(
        table_records,
        access_token,
        count_variations,
        CobrowseDateWiseInboundAnalytics,
        use_static_data):

    try:
        count_variation_analytics_data = {}
        for count_variation in count_variations:
            date_interval = get_date_interval_from_count_variation(
                count_variation)

            if use_static_data == True:
                analytics_data = get_sample_inbound_table_records()
            else:
                analytics_data = get_inbound_table_records(
                    access_token, CobrowseDateWiseInboundAnalytics, date_interval)

            count_variation_analytics_data[count_variation] = analytics_data

        html = get_count_variation_row_html(count_variations)

        if "request_initiated" in table_records:
            record_id = "request_initiated"
            record_name = "Request Initiated"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "request_attended" in table_records:
            record_id = "request_attended"
            record_name = Request_Attended
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "request_unattended" in table_records:
            record_id = "request_unattended"
            record_name = Request_Unattended
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "followup_leads" in table_records:
            record_id = "followup_leads"
            record_name = "Follow-up Leads"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "customer_converted" in table_records:
            record_id = "customer_converted"
            record_name = Customer_Converted_by_agent
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "customers_converted_by_url" in table_records:
            record_id = "customers_converted_by_url"
            record_name = Customer_Converted_through_URL
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "declined_leads" in table_records:
            record_id = "declined_leads"
            record_name = Declined_Leads
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "avg_session_time" in table_records:
            record_id = "avg_session_time"
            record_name = "Avg. Session time"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "request_assistance_avg_wait_time" in table_records:
            record_id = "request_assistance_avg_wait_time"
            record_name = "Avg. Waiting time for requesting Assistance"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "unique_customers" in table_records:
            record_id = "unique_customers"
            record_name = "Unique Customers"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "repeated_customers" in table_records:
            record_id = "repeated_customers"
            record_name = "Repeated Customers"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if html != "":
            html = """
            <div style="{table_container_css}">
                <div style="{table_heading_css}">
                    <div>Inbound</div>
                </div>
                <div>
                    <table style="{table_css}">{table_html}</table>
                </div>
            </div>
            """.format(
                table_container_css=TABLE_CONTAINER_CSS,
                table_heading_css=TABLE_HEADING_CSS,
                table_css=TABLE_CSS,
                table_html=html
            )
        return html
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_inbound_table_html %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return ""


def get_sample_outbound_table_records():
    try:
        analytics_data = {
            "captured_leads": 10,
            "searched_leads": 8,
            "request_attended": 5,
            "request_unattended": 3,
            "customer_converted": 2,
            "customers_converted_by_url": 2,
            "avg_session_time": "1 min",
            "requests_denied_by_customers": 3,
            "unique_customers": 2,
            "repeated_customers": 5,
        }
        return analytics_data

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_sample_inbound_table_records %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return {}


def get_outbound_table_html(
        table_records,
        access_token,
        count_variations,
        CobrowseDateWiseOutboundAnalytics,
        use_static_data):

    try:
        count_variation_analytics_data = {}
        for count_variation in count_variations:
            date_interval = get_date_interval_from_count_variation(
                count_variation)

            if use_static_data == True:
                analytics_data = get_sample_outbound_table_records()
            else:
                analytics_data = get_outbound_search_lead_table_records(
                    access_token, CobrowseDateWiseOutboundAnalytics, date_interval)

            count_variation_analytics_data[count_variation] = analytics_data

        html = get_count_variation_row_html(count_variations)

        if "lead_searched" in table_records:
            record_id = "searched_leads"
            record_name = "Lead Searched"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "request_attended" in table_records:
            record_id = "request_attended"
            record_name = Request_Attended
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "request_unattended" in table_records:
            record_id = "request_unattended"
            record_name = Request_Unattended
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "customers_converted_by_agent" in table_records:
            record_id = "customer_converted"
            record_name = Customer_Converted_by_agent
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "customers_converted_by_url" in table_records:
            record_id = "customers_converted_by_url"
            record_name = Customer_Converted_through_URL
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "declined_leads" in table_records:
            record_id = "requests_denied_by_customers"
            record_name = "Declined Leads"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "captured_leads" in table_records:
            record_id = "captured_leads"
            record_name = "Captured Leads"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "unique_customers" in table_records:
            record_id = "unique_customers"
            record_name = "Unique Customers"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "repeated_customers" in table_records:
            record_id = "repeated_customers"
            record_name = "Repeated Customers"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if html != "":
            html = """
            <div style="{table_container_css}">
                <div style="{table_heading_css}">
                    <div>Outbound Searched Leads</div>
                </div>
                <div>
                    <table style="{table_css}">{table_html}</table>
                </div>
            </div>
            """.format(
                table_container_css=TABLE_CONTAINER_CSS,
                table_heading_css=TABLE_HEADING_CSS,
                table_css=TABLE_CSS,
                table_html=html
            )
        return html
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_outbound_table_html %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return ""


def get_sample_outbound_droplink_table_records():
    try:
        analytics_data = {
            "request_initiated": 10,
            "declined_leads": 3,
            "request_attended": 5,
            "request_unattended": 2,
            "customer_converted": 2,
            "customers_converted_by_url": 2,
            "avg_session_time": "1 min",
        }
        return analytics_data

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_sample_outbound_droplink_table_records %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return {}


def get_outbound_droplink_table_html(
        table_records,
        access_token,
        count_variations,
        CobrowseDateWiseOutboundDroplinkAnalytics,
        use_static_data):

    try:
        count_variation_analytics_data = {}
        for count_variation in count_variations:
            date_interval = get_date_interval_from_count_variation(
                count_variation)

            if use_static_data == True:
                analytics_data = get_sample_outbound_droplink_table_records()
            else:
                analytics_data = get_outbound_droplink_table_records(
                    access_token, CobrowseDateWiseOutboundDroplinkAnalytics, date_interval)

            count_variation_analytics_data[count_variation] = analytics_data

        html = get_count_variation_row_html(count_variations)

        if "request_initiated" in table_records:
            record_id = "request_initiated"
            record_name = "Request Initiated"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "request_attended" in table_records:
            record_id = "request_attended"
            record_name = Request_Attended
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "request_unattended" in table_records:
            record_id = "request_unattended"
            record_name = Request_Unattended
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "customer_converted" in table_records:
            record_id = "customer_converted"
            record_name = Customer_Converted_by_agent
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "customers_converted_by_url" in table_records:
            record_id = "customers_converted_by_url"
            record_name = Customer_Converted_through_URL
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "declined_leads" in table_records:
            record_id = "declined_leads"
            record_name = Declined_Leads
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "avg_session_time" in table_records:
            record_id = "avg_session_time"
            record_name = "Avg. Session time"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if html != "":
            html = """
            <div style="{table_container_css}">
                <div style="{table_heading_css}">
                    <div>Outbound Droplink</div>
                </div>
                <div>
                    <table style="{table_css}">{table_html}</table>
                </div>
            </div>
            """.format(
                table_container_css=TABLE_CONTAINER_CSS,
                table_heading_css=TABLE_HEADING_CSS,
                table_css=TABLE_CSS,
                table_html=html
            )

        return html
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_outbound_droplink_table_html %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return ""


def get_sample_support_analytics_table_records():
    try:
        analytics_data = {
            "request_attended": 10,
            "request_unattended": 3,
            "declined_leads": 2,
            "followup_leads": 2,
            "customer_converted": 3,
            "customers_converted_by_url": 2,
            "total_meetings": 1,
        }
        return analytics_data

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_sample_outbound_droplink_table_records %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return {}


def get_support_table_html(
        table_records,
        access_token,
        count_variations,
        CobrowseDateWiseInboundAnalytics,
        CobrowseDateWiseOutboundAnalytics,
        CobrowseVideoConferencing,
        CobrowseVideoAuditTrail,
        use_static_data):

    try:
        count_variation_analytics_data = {}
        for count_variation in count_variations:
            date_interval = get_date_interval_from_count_variation(
                count_variation)

            if use_static_data == True:
                analytics_data = get_sample_support_analytics_table_records()
            else:
                analytics_data = get_support_analytics_table_records(
                    access_token,
                    CobrowseDateWiseInboundAnalytics,
                    CobrowseDateWiseOutboundAnalytics,
                    CobrowseVideoConferencing,
                    CobrowseVideoAuditTrail,
                    date_interval)

            count_variation_analytics_data[count_variation] = analytics_data

        html = get_count_variation_row_html(count_variations)

        if "attended" in table_records:
            record_id = "request_attended"
            record_name = "Attended"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "unattended" in table_records:
            record_id = "request_unattended"
            record_name = "Unattended"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "declined" in table_records:
            record_id = "declined_leads"
            record_name = Declined_Leads
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "followup_leads" in table_records:
            record_id = "followup_leads"
            record_name = "Follow-up Leads"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "customers_converted_by_agent" in table_records:
            record_id = "customer_converted"
            record_name = Customer_Converted_by_agent
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "customers_converted_by_url" in table_records:
            record_id = "customers_converted_by_url"
            record_name = Customer_Converted_through_URL
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if "meeting_support_history" in table_records:
            record_id = "total_meetings"
            record_name = "Meeting Support History"
            html += get_analytics_data_column_html(
                record_id, record_name, count_variation_analytics_data, count_variations)

        if html != "":
            html = """
            <div style="{table_container_css}">
                <div style="{table_heading_css}">
                    <div>Support</div>
                </div>
                <div>
                    <table style="{table_css}">{table_html}</table>
                </div>
            </div>
            """.format(
                table_container_css=TABLE_CONTAINER_CSS,
                table_heading_css=TABLE_HEADING_CSS,
                table_css=TABLE_CSS,
                table_html=html
            )
        return html
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_support_table_html %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return ""


def get_mailer_analytics_excel_data(profile_obj, requested_data, access_token, use_static_data, CobrowseVideoAuditTrail):
    try:
        if profile_obj.include_tables == False:
            return None

        email_analytics_table_obj = profile_obj.analytics_table
        file_path = get_email_analytics_table_excel(
            email_analytics_table_obj, requested_data, access_token, use_static_data, CobrowseVideoAuditTrail)

        return file_path

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_mailer_analytics_excel_data %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return None


def get_email_analytics_table_excel(email_analytics_table_obj, requested_data, access_token, use_static_data, CobrowseVideoAuditTrail):
    def get_folder_path():
        cobrowse_agent = access_token.agent
        folder_path = "secured_files/EasyAssistApp/MailerAnalyticsHistory/" + \
            str(cobrowse_agent.user.username) + "/"
        return folder_path

    def get_file_name(extention):
        file_name = "mailer_summary_" + \
            str(start_date) + "_to_" + str(end_date) + extention
        return file_name

    def get_relative_file_path(extention=".xls"):
        relative_file_path = get_folder_path() + get_file_name(extention)
        return relative_file_path

    def get_absolute_file_path(extention=".xls"):
        cobrowse_agent = access_token.agent
        absolute_folder_path = settings.SECURE_MEDIA_ROOT + \
            "EasyAssistApp/MailerAnalyticsHistory/" + \
            str(cobrowse_agent.user.username) + "/"
        if not path.exists(absolute_folder_path):
            os.makedirs(absolute_folder_path)
        absolute_file_path = absolute_folder_path + get_file_name(extention)
        return absolute_file_path

    try:
        from EasyAssistApp.models import CobrowseDateWiseInboundAnalytics,\
            CobrowseDateWiseOutboundAnalytics,\
            CobrowseDateWiseOutboundDroplinkAnalytics,\
            CobrowseVideoConferencing

        if email_analytics_table_obj is None:
            return None

        start_date = requested_data["startdate"]
        end_date = requested_data["enddate"]

        relative_file_path = get_relative_file_path()
        absolute_file_path = get_absolute_file_path()

        workbook = Workbook()
        sheet = workbook.add_sheet("Mailer Analytics")

        count_variations = email_analytics_table_obj.count_variation
        count_variations = json.loads(count_variations)

        add_count_variation_row_excel(
            sheet, count_variations, start_date, end_date)
        row_index = 2

        table_records = json.loads(email_analytics_table_obj.records)

        if "inbound" in table_records:
            row_index = add_inbound_table_data_in_excel(
                sheet,
                row_index,
                table_records["inbound"],
                access_token,
                count_variations,
                CobrowseDateWiseInboundAnalytics,
                use_static_data)

        if "outbound_search_leads" in table_records:
            row_index = add_outbound_table_data_in_excel(
                sheet,
                row_index,
                table_records["outbound_search_leads"],
                access_token,
                count_variations,
                CobrowseDateWiseOutboundAnalytics,
                use_static_data)

        if "outbound_gdl" in table_records:
            row_index = add_outbound_droplink_table_data_in_excel(
                sheet,
                row_index,
                table_records["outbound_gdl"],
                access_token,
                count_variations,
                CobrowseDateWiseOutboundDroplinkAnalytics,
                use_static_data)

        if "support" in table_records:
            row_index = add_support_table_data_in_excel(
                sheet,
                row_index,
                table_records["support"],
                access_token,
                count_variations,
                CobrowseDateWiseInboundAnalytics,
                CobrowseDateWiseOutboundAnalytics,
                CobrowseVideoConferencing,
                CobrowseVideoAuditTrail,
                use_static_data)

        workbook.save(absolute_file_path)

        return relative_file_path

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_mailer_analytics_excel_data %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return None


def add_count_variation_row_excel(sheet, count_variations, start_date, end_date):
    try:
        col_index = 0
        row_index = 0

        style = XFStyle()

        font = Font()
        font.bold = True
        style.font = font

        align = Alignment()
        align.horz = Alignment.HORZ_CENTER
        style.alignment = align

        sheet_start_date = datetime.strptime(
            start_date, "%Y-%m-%d").date()
        sheet_start_date = datetime.strftime(
            sheet_start_date, "%d-%m-%y")

        sheet_end_date = datetime.strptime(
            end_date, "%Y-%m-%d").date()
        sheet_end_date = datetime.strftime(
            sheet_end_date, "%d-%m-%y")

        date_range_string = "Count (" + sheet_start_date + \
            " - " + sheet_end_date + ")"

        sheet.write(row_index, col_index, date_range_string, style=style)
        sheet.col(col_index).width = 256 * 48
        col_index += 1

        for count_variation in count_variations:
            count_variation_name = ""
            if count_variation == "ytd":
                count_variation_name = "YTD"

            elif count_variation == "mtd":
                count_variation_name = "MTD"

            elif count_variation == "wtd":
                count_variation_name = "WTD"

            else:
                count_variation_name = "Daily"

            sheet.write(row_index, col_index,
                        count_variation_name, style=style)
            sheet.col(col_index).width = 256 * 20
            col_index += 1

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error add_count_variation_row_excel %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def add_analytics_data_column_excel(sheet, row_index, record_id, record_name, analytics_data, count_variations):
    try:
        col_index = 0
        sheet.write(row_index, col_index, record_name)
        col_index += 1

        for count_variation in count_variations:
            sheet.write(row_index, col_index,
                        analytics_data[count_variation][record_id])
            col_index += 1

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error add_analytics_data_column_excel %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def add_inbound_table_data_in_excel(
        workbook_sheet,
        row_index,
        table_records,
        access_token,
        count_variations,
        CobrowseDateWiseInboundAnalytics,
        use_static_data):

    try:
        count_variation_analytics_data = {}
        for count_variation in count_variations:
            date_interval = get_date_interval_from_count_variation(
                count_variation)

            if use_static_data == True:
                analytics_data = get_sample_inbound_table_records()
            else:
                analytics_data = get_inbound_table_records(
                    access_token, CobrowseDateWiseInboundAnalytics, date_interval)

            count_variation_analytics_data[count_variation] = analytics_data

        style = XFStyle()

        font = Font()
        font.bold = True
        style.font = font

        workbook_sheet.write(row_index, 0, "Inbound Analytics", style=style)
        row_index += 1

        if "request_initiated" in table_records:
            record_id = "request_initiated"
            record_name = "Request Initiated"
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "request_attended" in table_records:
            record_id = "request_attended"
            record_name = Request_Attended
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "request_unattended" in table_records:
            record_id = "request_unattended"
            record_name = Request_Unattended
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "followup_leads" in table_records:
            record_id = "followup_leads"
            record_name = "Follow-up Leads"
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "customer_converted" in table_records:
            record_id = "customer_converted"
            record_name = Customer_Converted_by_agent
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "customers_converted_by_url" in table_records:
            record_id = "customers_converted_by_url"
            record_name = Customer_Converted_through_URL
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "declined_leads" in table_records:
            record_id = "declined_leads"
            record_name = Declined_Leads
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "avg_session_time" in table_records:
            record_id = "avg_session_time"
            record_name = "Avg. Session time"
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "request_assistance_avg_wait_time" in table_records:
            record_id = "request_assistance_avg_wait_time"
            record_name = "Avg. Waiting time for requesting Assistance"
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        row_index += 1
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error add_inbound_table_data_in_excel %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return row_index


def add_outbound_table_data_in_excel(
        workbook_sheet,
        row_index,
        table_records,
        access_token,
        count_variations,
        CobrowseDateWiseOutboundAnalytics,
        use_static_data):

    try:
        count_variation_analytics_data = {}
        for count_variation in count_variations:
            date_interval = get_date_interval_from_count_variation(
                count_variation)

            if use_static_data == True:
                analytics_data = get_sample_outbound_table_records()
            else:
                analytics_data = get_outbound_search_lead_table_records(
                    access_token, CobrowseDateWiseOutboundAnalytics, date_interval)

            count_variation_analytics_data[count_variation] = analytics_data

        style = XFStyle()

        font = Font()
        font.bold = True
        style.font = font

        workbook_sheet.write(row_index, 0, "Outbound Analytics", style=style)
        row_index += 1

        if "lead_searched" in table_records:
            record_id = "searched_leads"
            record_name = "Lead Searched"
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "request_attended" in table_records:
            record_id = "request_attended"
            record_name = Request_Attended
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "request_unattended" in table_records:
            record_id = "request_unattended"
            record_name = Request_Unattended
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "customers_converted_by_agent" in table_records:
            record_id = "customer_converted"
            record_name = Customer_Converted_by_agent
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "customers_converted_by_url" in table_records:
            record_id = "customers_converted_by_url"
            record_name = Customer_Converted_through_URL
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "declined_leads" in table_records:
            record_id = "requests_denied_by_customers"
            record_name = "Declined Leads"
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        row_index += 1
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error add_outbound_table_data_in_excel %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return row_index


def add_outbound_droplink_table_data_in_excel(
        workbook_sheet,
        row_index,
        table_records,
        access_token,
        count_variations,
        CobrowseDateWiseOutboundDroplinkAnalytics,
        use_static_data):

    try:
        count_variation_analytics_data = {}
        for count_variation in count_variations:
            date_interval = get_date_interval_from_count_variation(
                count_variation)

            if use_static_data == True:
                analytics_data = get_sample_outbound_droplink_table_records()
            else:
                analytics_data = get_outbound_droplink_table_records(
                    access_token, CobrowseDateWiseOutboundDroplinkAnalytics, date_interval)

            count_variation_analytics_data[count_variation] = analytics_data

        style = XFStyle()

        font = Font()
        font.bold = True
        style.font = font

        workbook_sheet.write(
            row_index, 0, "Outbound Droplink Analytics", style=style)
        row_index += 1

        if "request_initiated" in table_records:
            record_id = "request_initiated"
            record_name = "Request Initiated"
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "request_attended" in table_records:
            record_id = "request_attended"
            record_name = Request_Attended
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "request_unattended" in table_records:
            record_id = "request_unattended"
            record_name = Request_Unattended
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "customer_converted" in table_records:
            record_id = "customer_converted"
            record_name = Customer_Converted_by_agent
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "customers_converted_by_url" in table_records:
            record_id = "customers_converted_by_url"
            record_name = Customer_Converted_through_URL
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "declined_leads" in table_records:
            record_id = "declined_leads"
            record_name = Declined_Leads
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "avg_session_time" in table_records:
            record_id = "avg_session_time"
            record_name = "Avg. Session time"
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        row_index += 1

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error add_outbound_droplink_table_data_in_excel %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return row_index


def add_support_table_data_in_excel(
        workbook_sheet,
        row_index,
        table_records,
        access_token,
        count_variations,
        CobrowseDateWiseInboundAnalytics,
        CobrowseDateWiseOutboundAnalytics,
        CobrowseVideoConferencing,
        CobrowseVideoAuditTrail,
        use_static_data):

    try:
        count_variation_analytics_data = {}
        for count_variation in count_variations:
            date_interval = get_date_interval_from_count_variation(
                count_variation)

            if use_static_data == True:
                analytics_data = get_sample_support_analytics_table_records()
            else:
                analytics_data = get_support_analytics_table_records(
                    access_token,
                    CobrowseDateWiseInboundAnalytics,
                    CobrowseDateWiseOutboundAnalytics,
                    CobrowseVideoConferencing,
                    CobrowseVideoAuditTrail,
                    date_interval)

            count_variation_analytics_data[count_variation] = analytics_data

        style = XFStyle()

        font = Font()
        font.bold = True
        style.font = font

        workbook_sheet.write(row_index, 0, "Support Analytics", style=style)
        row_index += 1

        if "attended" in table_records:
            record_id = "request_attended"
            record_name = "Attended"
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "unattended" in table_records:
            record_id = "request_unattended"
            record_name = "Unattended"
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "declined" in table_records:
            record_id = "declined_leads"
            record_name = Declined_Leads
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "followup_leads" in table_records:
            record_id = "followup_leads"
            record_name = "Follow-up Leads"
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "customers_converted_by_agent" in table_records:
            record_id = "customer_converted"
            record_name = Customer_Converted_by_agent
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "customers_converted_by_url" in table_records:
            record_id = "customers_converted_by_url"
            record_name = Customer_Converted_through_URL
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        if "meeting_support_history" in table_records:
            record_id = "total_meetings"
            record_name = "Meeting Support History"
            add_analytics_data_column_excel(
                workbook_sheet, row_index, record_id, record_name, count_variation_analytics_data, count_variations)
            row_index += 1

        row_index += 1
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error add_support_table_data_in_excel %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return row_index


def get_no_data_available_image(graph_title):
    try:

        plot = go.Figure(
            data=[],
            layout=go.Layout(
                title=go.layout.Title(
                    text=graph_title,
                    font=go.layout.title.Font(color='#0036B5')
                ),
                plot_bgcolor="white"
            )
        )
        no_data_available_image = Image.open(settings.BASE_DIR + "/" +
                                             NO_DATA_AVAILABLE_IMAGE_PATH)

        plot.add_layout_image(
            dict(
                source=no_data_available_image,
                xref="x",
                yref="y",
                x=1.5,
                y=2.75,
                sizex=2,
                sizey=2,
                opacity=1,
            )
        )

        # Configure axes
        plot.update_xaxes(
            visible=False,
        )

        plot.update_yaxes(
            visible=False,
            scaleanchor="x"
        )
        return plot
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_no_data_available_image %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
    return None
