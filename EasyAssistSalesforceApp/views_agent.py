from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core import serializers
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.encoding import smart_str
from django.contrib.sessions.models import Session

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
"""For user authentication"""
from django.contrib.auth import authenticate, login, logout

from EasyAssistSalesforceApp.models import *
from EasyAssistSalesforceApp.utils import *
from EasyAssistSalesforceApp.html_parser import strip_html_tags
# from EasyChatApp.models import User, UserSession
# from EasyAssistApp.views_table import *
from EasyAssistSalesforceApp.send_email import send_password_over_email, send_drop_link_over_email

from urllib.parse import quote_plus, unquote

import os
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
import mimetypes
import math

from operator import itemgetter
from collections import OrderedDict

logger = logging.getLogger(__name__)

# @csrf_exempt


def SalesAILoginPage(request):
    try:
        logger.info("Inside SalesAILoginPage", extra={
                    'AppName': 'EasyAssistSalesforce'})
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)

        salesforce_token = authenticate_salesforce_user(
            request, SalesforceAgent, User, CobrowseAgent, CobrowseAccessToken)
        if salesforce_token == None:
            return HttpResponse(status=401)
        # return HttpResponse(salesforce_token)
        logger.info("salesforce_token: " + salesforce_token,
                    extra={'AppName': 'EasyAssistSalesforce'})

        return redirect("/easy-assist-salesforce/sales-ai/dashboard/?salesforce_token=" + salesforce_token)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAILoginPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse("Invalid Access")


# @csrf_exempt
def SalesAIDashboard(request):
    try:
        logger.info("Inside SalesAIDashboard", extra={
                    'AppName': 'EasyAssistSalesforce'})
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)
        # return HttpResponse("user: " + user.username)

        access_token_obj = cobrowse_agent.get_access_token_obj()
        # easyassist_auto_archive(access_token_obj, CobrowseIO)

        agents = []
        if cobrowse_agent.role == "agent":
            agents = [cobrowse_agent]
        elif cobrowse_agent.role == "supervisor":
            agents = list(cobrowse_agent.agents.all())
        else:
            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None)

        cobrowse_io_objs = CobrowseIO.objects.filter(
            is_archived=False, agent__in=agents)
        cobrowse_io_support_objs = CobrowseIO.objects.filter(
            is_archived=False, support_agents__in=agents)
        cobrowse_io_objs = cobrowse_io_objs | cobrowse_io_support_objs
        cobrowse_io_objs = cobrowse_io_objs.order_by("-request_datetime")
        access_token_obj = cobrowse_agent.get_access_token_obj()

        agent_admin = access_token_obj.agent
        agents_list = get_list_agents_under_admin(agent_admin, is_active=True)
        agent_objs = []
        for agent_obj in agents_list:
            if agent_obj.pk != cobrowse_agent.pk:
                agent_objs.append(agent_obj)

        return render(request, "EasyAssistSalesforceApp/sales_dashboard.html", {
            "salesforce_token": quote_plus(request.GET["salesforce_token"]),
            "cobrowse_agent": cobrowse_agent,
            "cobrowse_io_objs": cobrowse_io_objs,
            "access_token_obj": access_token_obj,
            "agent_objs": agent_objs
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAIDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse("Invalid Access")


# @csrf_exempt
def SalesAnalyticsSettings(request):
    try:
        logger.info("Inside SalesAnalyticsSettings", extra={
                    'AppName': 'EasyAssistSalesforce'})
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        if cobrowse_agent.role != "admin":

            cobrowse_admin = get_admin_from_active_agent(
                cobrowse_agent, CobrowseAgent)
            supported_language = []
            for language in cobrowse_admin.supported_language.all():
                if language in cobrowse_agent.supported_language.all():
                    supported_language.append({
                        "key": language.pk,
                        "value": language.title,
                        "is_selected": True,
                    })
                else:
                    supported_language.append({
                        "key": language.pk,
                        "value": language.title,
                        "is_selected": False,
                    })

            product_category = []
            for product in cobrowse_admin.product_category.all():
                if product in cobrowse_agent.product_category.all():
                    product_category.append({
                        "key": product.pk,
                        "value": product.title,
                        "is_selected": True,
                    })
                else:
                    product_category.append({
                        "key": product.pk,
                        "value": product.title,
                        "is_selected": False,
                    })

            return render(request, "EasyAssistSalesforceApp/sales_settings_agent.html", {
                "salesforce_token": quote_plus(request.GET["salesforce_token"]),
                "cobrowse_agent": cobrowse_agent,
                "supported_language": supported_language,
                "product_category": product_category
            })
        else:
            access_token_obj = cobrowse_agent.get_access_token_obj()
            product_category_list = access_token_obj.get_product_categories()
            product_categories = [x.strip()
                                  for x in str(product_category_list).split(',')]
            return render(request, "EasyAssistSalesforceApp/sales_settings.html", {
                "salesforce_token": quote_plus(request.GET["salesforce_token"]),
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "FLOATING_BUTTON_POSITION": FLOATING_BUTTON_POSITION,
                "product_category": json.dumps(product_categories)
            })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAnalyticsSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return HttpResponse("Invalid Access")


class SwitchAgentModeAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logger.info("Inside SwitchAgentModeAPI", extra={
                    'AppName': 'EasyAssistSalesforce'})
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            status = data["active_status"]

            if status == True or status == False:

                if active_agent.is_switch_allowed and status:
                    active_agent.role = "agent"
                    active_agent.agents.add(active_agent)
                    active_agent.is_active = True
                elif active_agent.is_switch_allowed and not status:
                    active_agent.role = "admin"
                    active_agent.is_active = False
                    active_agent.agents.remove(active_agent)

                active_agent.save()
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SwitchAgentModeAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        logger.info("Successfully exited from SwitchAgentModeAPI",
                    extra={'AppName': 'EasyAssistSalesforce'})
        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SwitchAgentMode = SwitchAgentModeAPI.as_view()


class ChangeAgentActiveStatusAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logger.info("Inside ChangeAgentActiveStatusAPI",
                    extra={'AppName': 'EasyAssistSalesforce'})
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            status = data["active_status"]

            if status == True or status == False:
                # active_agent = get_active_agent_obj(
                #     request, User, CobrowseAgent)
                location = str(data['location'])
                if location != "None" and location.strip() != "" and location != active_agent.location:
                    active_agent.location = remo_html_from_string(location)

                logger.info("Agent location of %s is %s:", active_agent, active_agent.location, extra={
                            'AppName': 'EasyAssistSalesforce'})

                if status == True:
                    time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=1)
                    agent_online_audit_trail_obj = CobrowseAgentOnlineAuditTrail.objects.filter(
                        agent=active_agent,
                        last_online_end_datetime__gte=time_threshold).order_by(
                            '-last_online_start_datetime').first()

                    if agent_online_audit_trail_obj != None:
                        agent_online_audit_trail_obj.last_online_end_datetime = timezone.now()
                        agent_online_audit_trail_obj.save()
                    else:
                        agent_online_audit_trail_obj = CobrowseAgentOnlineAuditTrail.objects.create(
                            agent=active_agent,
                            last_online_start_datetime=timezone.now(),
                            last_online_end_datetime=timezone.now())
                        agent_online_audit_trail_obj.save()

                cobrowse_io_obj_count = CobrowseIO.objects.filter(
                    is_archived=False, agent__in=[active_agent]).count()

                meeting_io_obj_count = CobrowseVideoConferencing.objects.filter(
                    is_expired=False,
                    support_meeting_agents__in=[active_agent]).count()

                active_agent.is_active = status
                active_agent.last_agent_active_datetime = timezone.now()
                active_agent.is_cobrowsing_active = False
                active_agent.save()

                response["status"] = 200
                response["message"] = "success"
                response["cobrowsing_count"] = cobrowse_io_obj_count
                response["video_meeting_count"] = meeting_io_obj_count
                response["location"] = location

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ChangeAgentActiveStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        logger.info("Successfully exited from ChangeAgentActiveStatusAPI", extra={
                    'AppName': 'EasyAssistSalesforce'})
        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ChangeAgentActiveStatus = ChangeAgentActiveStatusAPI.as_view()


class SaveCobrowsingMetaDetailsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            if active_agent.role == "admin":
                active_agent.options = json.dumps(data)
                active_agent.save()

                cobrowse_access_token = active_agent.get_access_token_obj()

                if data["reset"] == "false":
                    # inbound settings
                    cobrowse_access_token.show_floating_easyassist_button = data[
                        "show_floating_easyassist_button"]

                    if cobrowse_access_token.show_easyassist_connect_agent_icon != data["show_easyassist_connect_agent_icon"]:
                        cobrowse_access_token.show_easyassist_connect_agent_icon = data[
                            "show_easyassist_connect_agent_icon"]
                        # cobrowse_access_token.source_easyassist_connect_agent_icon = data[
                        #     "source_easyassist_connect_agent_icon"]

                    cobrowse_access_token.show_only_if_agent_available = data[
                        "show_only_if_agent_available"]
                    cobrowse_access_token.floating_button_position = strip_html_tags(
                        data["floating_button_position"])
                    cobrowse_access_token.floating_button_bg_color = "#" + strip_html_tags(
                        data["floating_button_bg_color"])

                    if data["cobrowsing_console_theme_color"] is None:
                        cobrowse_access_token.cobrowsing_console_theme_color = None
                    else:
                        cobrowse_access_token.cobrowsing_console_theme_color = json.dumps(
                            data["cobrowsing_console_theme_color"])

                    cobrowse_access_token.disable_connect_button_if_agent_unavailable = data[
                        "disable_connect_button_if_agent_unavailable"]
                    cobrowse_access_token.message_if_agent_unavailable = data[
                        "message_if_agent_unavailable"]
                    cobrowse_access_token.start_time = datetime.datetime.strptime(
                        data["start_time"], '%H:%M').time()
                    cobrowse_access_token.end_time = datetime.datetime.strptime(
                        data["end_time"], '%H:%M').time()
                    cobrowse_access_token.message_on_non_working_hours = data[
                        "message_on_non_working_hours"]

                    # admin settings
                    cobrowse_access_token.enable_edit_access = data[
                        "enable_edit_access"]
                    cobrowse_access_token.allow_capture_screenshots_in_cobrowsing = data[
                        "allow_capture_screenshots_in_cobrowsing"]
                    cobrowse_access_token.allow_support_documents = data[
                        "allow_support_documents"]
                    cobrowse_access_token.share_document_from_livechat = data[
                        "share_document_from_livechat"]
                    cobrowse_access_token.enable_invite_agent_in_cobrowsing = data[
                        "enable_invite_agent_in_cobrowsing"]
                    cobrowse_access_token.field_stuck_event_handler = data[
                        "field_stuck_event_handler"]
                    cobrowse_access_token.field_recursive_stuck_event_check = data[
                        "field_recursive_stuck_event_check"]
                    cobrowse_access_token.get_sharable_link = data[
                        "get_sharable_link"]
                    cobrowse_access_token.lead_generation = data[
                        "lead_generation"]
                    cobrowse_access_token.field_stuck_timer = int(
                        data["field_stuck_timer"])
                    cobrowse_access_token.proxy_server = strip_html_tags(
                        data["proxy_server"])
                    cobrowse_access_token.connect_message = strip_html_tags(
                        data["connect_message"])
                    cobrowse_access_token.assist_message = strip_html_tags(
                        data["assistant_message"])
                    cobrowse_access_token.whitelisted_domain = strip_html_tags(
                        data["whitelisted_domain"])
                    cobrowse_access_token.urls_consider_lead_converted = strip_html_tags(
                        data["urls_consider_lead_converted"])
                    cobrowse_access_token.masking_type = data[
                        "masking_type"]
                    cobrowse_access_token.allow_only_support_documents = data[
                        "allow_only_support_documents"]
                    cobrowse_access_token.enable_verification_code_popup = data[
                        "enable_verification_code_popup"]
                    cobrowse_access_token.allow_language_support = data[
                        "allow_language_support"]
                    cobrowse_access_token.meeting_default_password = data[
                        "meeting_default_password"]
                    cobrowse_access_token.go_live_date = data["go_live_date"]
                    if data["allow_language_support"]:
                        save_language_support(
                            active_agent, data["supported_language_list"], LanguageSupport)
                    cobrowse_access_token.allow_generate_meeting = data[
                        "allow_generate_meeting"]
                    cobrowse_access_token.meeting_host_url = data[
                        "meeting_url"]
                    cobrowse_access_token.allow_screen_recording = data[
                        "allow_screen_recording"]
                    cobrowse_access_token.recording_expires_in_days = data[
                        "recording_expires_in_days"]
                    cobrowse_access_token.lead_conversion_checkbox_text = data[
                        "lead_conversion_checkbox_text"]
                    cobrowse_access_token.allow_cobrowsing_meeting = data[
                        "allow_video_calling_cobrowsing"]
                    cobrowse_access_token.allow_screen_sharing_cobrowse = data[
                        "allow_screen_sharing_cobrowse"]
                    cobrowse_access_token.show_cobrowsing_meeting_lobby = data[
                        "show_cobrowsing_meeting_lobby"]
                    cobrowse_access_token.meet_background_color = data["meet_background_color"]
                    cobrowse_access_token.choose_product_category = data["choose_product_category"]
                    if data["choose_product_category"]:
                        save_product_category(
                            active_agent, data["product_category_list"], ProductCategory)
                    cobrowse_access_token.allow_meeting_feedback = data[
                        "allow_meeting_feedback"]
                    cobrowse_access_token.allow_meeting_end_time = data[
                        "allow_meeting_end_time"]
                    cobrowse_access_token.meeting_end_time = data[
                        "meeting_end_time"]
                    cobrowse_access_token.enable_predefined_remarks = data[
                        "enable_predefined_remarks"]
                    cobrowse_access_token.predefined_remarks = strip_html_tags(data[
                        "predefined_remarks_list"])
                    cobrowse_access_token.allow_video_meeting_only = data[
                        "allow_video_meeting_only"]
                    cobrowse_access_token.enable_agent_connect_message = data[
                        "enable_agent_connect_message"]
                    cobrowse_access_token.agent_connect_message = strip_html_tags(data[
                        "agent_connect_message"])
                    cobrowse_access_token.enable_masked_field_warning = data[
                        "enable_masked_field_warning"]
                    cobrowse_access_token.masked_field_warning_text = strip_html_tags(data[
                        "masked_field_warning_text"])
                    cobrowse_access_token.save()

                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     "Custom App Configuration Changes", CobrowsingAuditTrail)
                elif data["reset"] == "true":
                    # inbound settings
                    cobrowse_access_token.show_floating_easyassist_button = True
                    cobrowse_access_token.show_easyassist_connect_agent_icon = False
                    cobrowse_access_token.floating_button_position = "left"
                    cobrowse_access_token.floating_button_bg_color = "#C72F2C"
                    cobrowse_access_token.cobrowsing_console_theme_color = None
                    cobrowse_access_token.show_only_if_agent_available = False
                    cobrowse_access_token.disable_connect_button_if_agent_unavailable = False
                    cobrowse_access_token.message_if_agent_unavailable = ""
                    cobrowse_access_token.start_time = datetime.datetime.strptime(
                        "00:00", '%H:%M').time()
                    cobrowse_access_token.end_time = datetime.datetime.strptime(
                        "23:59", '%H:%M').time()
                    cobrowse_access_token.message_on_non_working_hours = ""

                    # admin settings
                    cobrowse_access_token.enable_edit_access = False
                    cobrowse_access_token.field_stuck_event_handler = False
                    cobrowse_access_token.field_recursive_stuck_event_check = False
                    cobrowse_access_token.get_sharable_link = False
                    cobrowse_access_token.lead_generation = True
                    cobrowse_access_token.field_stuck_timer = 5
                    cobrowse_access_token.proxy_server = ""
                    cobrowse_access_token.connect_message = "Please provide your contact details for our Experts to Assist you."
                    cobrowse_access_token.assist_message = "We would like to assist you in filling your form. By clicking 'Allow' our Customer Service Agent will be able to see your screen and assist you. Please don't worry, your personal data is safe and will not be visible to our Agent"
                    cobrowse_access_token.whitelisted_domain = ""
                    cobrowse_access_token.urls_consider_lead_converted = ""
                    cobrowse_access_token.strip_js = True
                    cobrowse_access_token.is_socket = True
                    cobrowse_access_token.masking_type = "partial-masking"
                    cobrowse_access_token.enable_verification_code_popup = True
                    cobrowse_access_token.allow_language_support = False
                    cobrowse_access_token.choose_product_category = False
                    cobrowse_access_token.allow_screen_recording = False
                    cobrowse_access_token.recording_expires_in_days = 15
                    cobrowse_access_token.lead_conversion_checkbox_text = "Lead has been closed successfully."
                    cobrowse_access_token.allow_screen_sharing_cobrowse = False
                    cobrowse_access_token.enable_predefined_remarks = False
                    cobrowse_access_token.predefined_remarks = ""
                    cobrowse_access_token.allow_capture_screenshots_in_cobrowsing = True
                    cobrowse_access_token.allow_support_documents = True
                    cobrowse_access_token.share_document_from_livechat = True
                    cobrowse_access_token.enable_invite_agent_in_cobrowsing = True
                    cobrowse_access_token.allow_video_meeting_only = False
                    cobrowse_access_token.enable_agent_connect_message = False
                    cobrowse_access_token.agent_connect_message = "Hello, thank you for choosing Cogno Cobrowsing Support!  We are glad to welcome you to Cogno Cobrowsing Bank family. My Name  is agent_name. I will  be assisting you."
                    cobrowse_access_token.enable_masked_field_warning = False
                    cobrowse_access_token.masked_field_warning_text = "This Field is not visible to agent"
                    cobrowse_access_token.save()
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     "Custom App Configuration has been reset", CobrowsingAuditTrail)

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowsingMetaDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowsingMetaDetails = SaveCobrowsingMetaDetailsAPI.as_view()


@xframe_options_exempt
def SalesAILiveChatWindow(request):
    if not check_for_salesforce_request(request):
        return HttpResponse(status=401)
    active_agent = get_active_agent_obj(request, User, CobrowseAgent)
    if active_agent == None:
        return HttpResponse(status=401)

    session_id = request.GET["session_id"]
    session_id = remo_html_from_string(session_id)
    cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
    access_token = cobrowse_io.access_token
    floating_button_bg_color = cobrowse_io.access_token.floating_button_bg_color
    return render(request, "EasyAssistSalesforceApp/chatbot.html", {
        "salesforce_token": quote_plus(request.GET["salesforce_token"]),
        "access_token": access_token,
        "floating_button_bg_color": floating_button_bg_color
    })


def CobrowseIOAgentPage(request, session_id):
    try:
        logger.info("Inside CobrowseIOAgentPage", extra={
                    'AppName': 'EasyAssistSalesforce'})
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)
        logger.info("Inside CobrowseIOAgentPage checkpoint 1",
                    extra={'AppName': 'EasyAssistSalesforce'})

        cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

        access_token_obj = cobrowse_agent.get_access_token_obj()

        enable_edit_access = access_token_obj.enable_edit_access

        allow_capture_screenshots_in_cobrowsing = access_token_obj.allow_capture_screenshots_in_cobrowsing

        allow_support_documents = access_token_obj.allow_support_documents

        allow_cobrowsing_meeting = access_token_obj.allow_cobrowsing_meeting

        enable_invite_agent_in_cobrowsing = access_token_obj.enable_invite_agent_in_cobrowsing

        enable_predefined_remarks = access_token_obj.enable_predefined_remarks

        predefined_remarks = access_token_obj.predefined_remarks

        if len(predefined_remarks) == 0:
            predefined_remarks = []
        else:
            predefined_remarks = predefined_remarks.split(',')

        if cobrowse_io.allow_agent_cobrowse != "true" and (not cobrowse_io.is_archived):
            return HttpResponse(status=401)
        logger.info("Inside CobrowseIOAgentPage checkpoint 2",
                    extra={'AppName': 'EasyAssistSalesforce'})

        is_cobrowsing_allowed = False

        agent_admin = cobrowse_io.access_token.agent
        is_socket = cobrowse_io.access_token.is_socket
        supported_language_objs = agent_admin.supported_language.all()
        allow_language_support = cobrowse_io.access_token.allow_language_support
        product_category_objs = agent_admin.product_category.all()
        choose_product_category = cobrowse_io.access_token.choose_product_category
        floating_button_bg_color = cobrowse_io.access_token.floating_button_bg_color
        support_agents = get_list_agents_under_admin(agent_admin, None)

        if "token" in request.GET and request.GET["token"] == "sales-ai":
            is_cobrowsing_allowed = True
        else:
            cobrowse_agent.is_cobrowsing_active = True

            if cobrowse_io.agent == cobrowse_agent:
                is_cobrowsing_allowed = True
            elif cobrowse_agent in cobrowse_io.support_agents.all():
                is_cobrowsing_allowed = True

        if not is_cobrowsing_allowed:
            return HttpResponse(status=401)
        logger.info("Inside CobrowseIOAgentPage checkpoint 3",
                    extra={'AppName': 'EasyAssistSalesforce'})

        is_admin_agent = False

        if cobrowse_agent == cobrowse_io.agent:
            is_admin_agent = True

        agent_name = cobrowse_agent.user.first_name
        if agent_name is None or agent_name.strip() == "":
            agent_name = cobrowse_agent.user.username
        client_name = cobrowse_io.full_name
        cobrowse_io.is_agent_connected = True
        if cobrowse_io.cobrowsing_start_datetime == None:
            cobrowse_io.cobrowsing_start_datetime = timezone.now()
        cobrowse_io.save()
        return render(request, "EasyAssistSalesforceApp/cobrowse_agent.html", {
            "salesforce_token": quote_plus(request.GET["salesforce_token"]),
            "floating_button_bg_color": floating_button_bg_color,
            "enable_edit_access": enable_edit_access,
            "agent_name": agent_name,
            "client_name": client_name,
            "session_id": session_id,
            "support_agents": support_agents,
            "is_socket": is_socket,
            "supported_language_objs": supported_language_objs,
            "allow_language_support": allow_language_support,
            "product_category_objs": product_category_objs,
            "choose_product_category": choose_product_category,
            "allow_screen_recording": cobrowse_io.access_token.allow_screen_recording,
            "lead_conversion_checkbox_text": cobrowse_io.access_token.lead_conversion_checkbox_text,
            "allow_cobrowsing_meeting": allow_cobrowsing_meeting,
            "is_admin_agent": is_admin_agent,
            "allow_capture_screenshots_in_cobrowsing": allow_capture_screenshots_in_cobrowsing,
            "allow_support_documents": allow_support_documents,
            "enable_invite_agent_in_cobrowsing": enable_invite_agent_in_cobrowsing,
            "enable_predefined_remarks": enable_predefined_remarks,
            "predefined_remarks": predefined_remarks,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowseIOAgentPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse(status=401)


def SalesSupportHistory(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        agents = []
        if cobrowse_agent.role == "agent":
            agents = [cobrowse_agent]
        elif cobrowse_agent.role == "supervisor":
            agents = cobrowse_agent.agents.all()
        else:
            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None)

        cobrowse_io_objs = CobrowseIO.objects.filter(
            agent__in=agents, is_test=False).filter(~Q(cobrowsing_start_datetime=None))
        is_filter_applied = False

        if "startdate" in request.GET:
            date_format = "%Y-%m-%d"
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                cobrowsing_start_datetime__date__gte=datetime_start)
            is_filter_applied = True

        if "enddate" in request.GET:
            date_format = "%Y-%m-%d"
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                cobrowsing_start_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if "title" in request.GET:
            title = request.GET.getlist("title")[0]
            title = remo_html_from_string(title)
            cobrowse_io_objs = cobrowse_io_objs.filter(title=title)
            is_filter_applied = True

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")[0]
            agent_email = remo_html_from_string(agent_email)
            selected_agent = CobrowseAgent.objects.get(
                user__username=agent_email)
            cobrowse_io_objs = cobrowse_io_objs.filter(agent=selected_agent)
            is_filter_applied = True

        if "session-status" in request.GET:
            session_status = request.GET.getlist("session-status")[0]
            session_status = remo_html_from_string(session_status)
            if session_status == "converted":
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    is_helpful=True, is_archived=True)
                is_filter_applied = True
            elif session_status == "notconverted":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_helpful=False)
                is_filter_applied = True

        if "session_id" in request.GET:
            session_id = request.GET.getlist("session_id")[0]
            session_id = remo_html_from_string(session_id)
            cobrowse_io_objs = cobrowse_io_objs.filter(session_id=session_id)
            is_filter_applied = True

        if not is_filter_applied:
            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()
            datetime_end = datetime.datetime.today().date()
            cobrowse_io_objs = cobrowse_io_objs.filter(cobrowsing_start_datetime__date__gte=datetime_start,
                                                       cobrowsing_start_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if cobrowse_io_objs.count() > 0:
            cobrowse_io_objs = cobrowse_io_objs.order_by('-request_datetime')

        title_list = get_visited_page_title_list_with_agent(
            cobrowse_agent, CobrowseAgent, CobrowseIO)

        edit_access_audit_trail_objs = {}

        for cobrowse_io_obj in cobrowse_io_objs:
            edit_access_audit_trail_objs[
                cobrowse_io_obj.session_id] = [1, 2, 3]

        return render(request, "EasyAssistSalesforceApp/sales_support_history.html", {
            "salesforce_token": quote_plus(request.GET["salesforce_token"]),
            "cobrowse_agent": cobrowse_agent,
            "is_filter_applied": is_filter_applied,
            "cobrowse_io_objs": cobrowse_io_objs,
            "agents": agents,
            "title_list": title_list,
            "edit_access_audit_trail_objs": edit_access_audit_trail_objs
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesSupportHistory %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse("Invalid Access")


def SalesMeetings(request):
    try:
        logger.info("Inside SalesMeetings", extra={
                    'AppName': 'EasyAssistSalesforce'})
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)
        logger.info("Inside SalesMeetings checkpoint 1",
                    extra={'AppName': 'EasyAssistSalesforce'})

        access_token_obj = cobrowse_agent.get_access_token_obj()
        allow_meeting_end_time = access_token_obj.allow_meeting_end_time
        meeting_end_time = '30'
        if allow_meeting_end_time:
            meeting_end_time = access_token_obj.meeting_end_time
        if access_token_obj.allow_generate_meeting:
            cognovid_objs = CobrowseVideoConferencing.objects.filter(
                agent=cobrowse_agent, is_expired=False).order_by('-meeting_start_date')
            if not cognovid_objs:
                cognovid_objs = CobrowseVideoConferencing.objects.filter(
                    support_meeting_agents=cobrowse_agent, is_expired=False).order_by('-meeting_start_date')

            unexpired_cognovid_objs = []
            for cognovid_obj in cognovid_objs:
                check_cogno_meet_status(cognovid_obj)
                if cognovid_obj.is_expired == False:
                    unexpired_cognovid_objs.append(cognovid_obj)

            default_password = access_token_obj.meeting_default_password
            if default_password == "" or default_password == None:
                default_password = ""
            agent_objs = CobrowseAgent.objects.filter(
                is_account_active=True).exclude(pk=int(cobrowse_agent.pk))
            return render(request, "EasyAssistSalesforceApp/sales_meeting.html", {
                "salesforce_token": quote_plus(request.GET["salesforce_token"]),
                "cognovid_objs": unexpired_cognovid_objs,
                "cobrowse_agent": cobrowse_agent,
                "default_password": default_password,
                "agent_objs": agent_objs,
                "meeting_end_time": meeting_end_time
            })
        else:
            return HttpResponse("Invalid Access")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesMeetings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse("Invalid Access")


def ScreenRecordingAuditTrail(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        agents = []
        if cobrowse_agent.role == "agent":
            agents = [cobrowse_agent]
        elif cobrowse_agent.role == "supervisor":
            agents = cobrowse_agent.agents.all()
        else:
            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None)

        screen_recording_objs = CobrowseScreenRecordingAuditTrail.objects.filter(
            agent__in=agents).order_by('-recording_ended')

        return render(request, "EasyAssistSalesforceApp/screen_recording_audit_trail.html", {
            "salesforce_token": quote_plus(request.GET["salesforce_token"]),
            "cobrowse_agent": cobrowse_agent,
            "screen_recording_objs": screen_recording_objs,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ScreenRecordingAuditTrail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse("Invalid Access")


class ExportSalesSupportHistoryAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if cobrowse_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            filter_dict = json.loads(data)

            agents = []
            if cobrowse_agent.role == "agent":
                agents = [cobrowse_agent]
            elif cobrowse_agent.role == "supervisor":
                agents = cobrowse_agent.agents.all()
            else:
                agents = get_list_agents_under_admin(
                    cobrowse_agent, is_active=None)

            cobrowse_io_objs = CobrowseIO.objects.filter(
                agent__in=agents, is_test=False).filter(~Q(cobrowsing_start_datetime=None))
            is_filter_applied = False

            if "startdate" in filter_dict:
                date_format = "%Y-%m-%d"
                start_date = filter_dict["startdate"][0]
                start_date = remo_html_from_string(start_date)
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    cobrowsing_start_datetime__date__gte=datetime_start)
                is_filter_applied = True

            if "enddate" in filter_dict:
                date_format = "%Y-%m-%d"
                end_date = filter_dict["enddate"][0]
                end_date = remo_html_from_string(end_date)
                datetime_end = datetime.datetime.strptime(
                    end_date, date_format).date()
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    cobrowsing_start_datetime__date__lte=datetime_end)
                is_filter_applied = True

            if "title" in filter_dict:
                title = filter_dict["title"][0]
                title = remo_html_from_string(title)
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)
                is_filter_applied = True

            if "agent" in filter_dict:
                agent_email = filter_dict["agent"][0]
                agent_email = remo_html_from_string(agent_email)
                selected_agent = CobrowseAgent.objects.get(
                    user__username=agent_email)
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    agent=selected_agent)
                is_filter_applied = True

            if "session-status" in filter_dict:
                session_status = filter_dict["session-status"][0]
                session_status = remo_html_from_string(session_status)
                if session_status == "converted":
                    cobrowse_io_objs = cobrowse_io_objs.filter(
                        is_helpful=True, is_archived=True)
                    is_filter_applied = True
                elif session_status == "notconverted":
                    cobrowse_io_objs = cobrowse_io_objs.filter(
                        is_helpful=False)
                    is_filter_applied = True

            if "session_id" in filter_dict:
                session_id = filter_dict["session_id"][0]
                session_id = remo_html_from_string(session_id)
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    session_id=session_id)
                is_filter_applied = True

            if not is_filter_applied:
                datetime_start = (datetime.datetime.today() -
                                  datetime.timedelta(7)).date()
                datetime_end = datetime.datetime.today().date()
                cobrowse_io_objs = cobrowse_io_objs.filter(cobrowsing_start_datetime__date__gte=datetime_start,
                                                           cobrowsing_start_datetime__date__lte=datetime_end)
                is_filter_applied = True

            if cobrowse_io_objs.count() > 0:
                cobrowse_io_objs = cobrowse_io_objs.order_by(
                    '-request_datetime')

            export_path = create_excel_sales_support_history(
                cobrowse_agent.user, cobrowse_io_objs, cobrowse_agent.get_access_token_obj())
            export_path = "/" + export_path
            file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                file_path=export_path, is_public=False)
            response["export_path"] = 'easy-assist-salesforce/download-file/' + \
                str(file_access_management_obj.key)
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportSalesSupportHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportSalesSupportHistory = ExportSalesSupportHistoryAPI.as_view()


def UnattendedLeadsDetails(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        agents = []
        if cobrowse_agent.role == "agent":
            agents = [cobrowse_agent]
        elif cobrowse_agent.role == "supervisor":
            agents = cobrowse_agent.agents.all()
        else:
            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None)

        time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=5)
        cobrowse_io_objs = CobrowseIO.objects.filter(
            agent__in=agents).filter(Q(cobrowsing_start_datetime=None)).filter(request_datetime__lte=time_threshold)

        is_filter_applied = False
        if "startdate" in request.GET:
            date_format = "%Y-%m-%d"
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                request_datetime__date__gte=datetime_start)
            is_filter_applied = True

        if "enddate" in request.GET:
            date_format = "%Y-%m-%d"
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                request_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if "title" in request.GET:
            title = request.GET.getlist("title")[0]
            title = remo_html_from_string(title)
            cobrowse_io_objs = cobrowse_io_objs.filter(title=title)
            is_filter_applied = True

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")[0]
            agent_email = remo_html_from_string(agent_email)
            selected_agent = CobrowseAgent.objects.get(
                user__username=agent_email)
            cobrowse_io_objs = cobrowse_io_objs.filter(agent=selected_agent)
            is_filter_applied = True

        if not is_filter_applied:
            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()
            datetime_end = datetime.datetime.today().date()
            cobrowse_io_objs = cobrowse_io_objs.filter(request_datetime__date__gte=datetime_start,
                                                       request_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if cobrowse_io_objs.count() > 0:
            cobrowse_io_objs = cobrowse_io_objs.order_by('-request_datetime')

        title_list = get_visited_page_title_list_with_agent(
            cobrowse_agent, CobrowseAgent, CobrowseIO)

        return render(request, "EasyAssistSalesforceApp/sales_unattended_leads_detail.html", {
            "salesforce_token": quote_plus(request.GET["salesforce_token"]),
            "cobrowse_agent": cobrowse_agent,
            "is_filter_applied": is_filter_applied,
            "cobrowse_io_objs": cobrowse_io_objs,
            "agents": agents,
            "title_list": title_list
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error UnattendedLeadsDetails %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse("Invalid Access")


class ExportUnattentedLeadsDetalsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if cobrowse_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            filter_dict = json.loads(data)

            agents = []
            if cobrowse_agent.role == "agent":
                agents = [cobrowse_agent]
            elif cobrowse_agent.role == "supervisor":
                agents = cobrowse_agent.agents.all()
            else:
                agents = get_list_agents_under_admin(
                    cobrowse_agent, is_active=None)

            time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=5)
            cobrowse_io_objs = CobrowseIO.objects.filter(
                agent__in=agents).filter(Q(cobrowsing_start_datetime=None)).filter(request_datetime__lte=time_threshold)

            is_filter_applied = False

            if "startdate" in filter_dict:
                date_format = "%Y-%m-%d"
                start_date = filter_dict["startdate"][0]
                start_date = remo_html_from_string(start_date)
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    request_datetime__date__gte=datetime_start)
                is_filter_applied = True

            if "enddate" in filter_dict:
                date_format = "%Y-%m-%d"
                end_date = filter_dict["enddate"][0]
                end_date = remo_html_from_string(end_date)
                datetime_end = datetime.datetime.strptime(
                    end_date, date_format).date()
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    request_datetime__date__lte=datetime_end)
                is_filter_applied = True

            if "title" in filter_dict:
                title = filter_dict["title"][0]
                title = remo_html_from_string(title)
                cobrowse_io_objs = cobrowse_io_objs.filter(title=title)
                is_filter_applied = True

            if "agent" in filter_dict:
                agent_email = filter_dict["agent"][0]
                agent_email = remo_html_from_string(agent_email)
                selected_agent = CobrowseAgent.objects.get(
                    user__username=agent_email)
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    agent=selected_agent)
                is_filter_applied = True

            if not is_filter_applied:
                datetime_start = (datetime.datetime.today() -
                                  datetime.timedelta(7)).date()
                datetime_end = datetime.datetime.today().date()
                cobrowse_io_objs = cobrowse_io_objs.filter(request_datetime__date__gte=datetime_start,
                                                           request_datetime__date__lte=datetime_end)
                is_filter_applied = True

            if cobrowse_io_objs.count() > 0:
                cobrowse_io_objs = cobrowse_io_objs.order_by(
                    '-request_datetime')

            export_path = create_excel_unattended_leads_datails(
                cobrowse_agent.user, cobrowse_io_objs, cobrowse_agent.get_access_token_obj())
            export_path = "/" + export_path
            file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                file_path=export_path, is_public=False)
            response["export_path"] = 'easy-assist-salesforce/download-file/' + \
                str(file_access_management_obj.key)
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportUnattentedLeadsDetalsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportUnattentedLeadsDetals = ExportUnattentedLeadsDetalsAPI.as_view()


class ExportMeetingSupportHistoryAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if cobrowse_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            filter_dict = json.loads(data)

            agents = []
            if cobrowse_agent.role == "agent":
                agents = [cobrowse_agent]
            elif cobrowse_agent.role == "supervisor":
                agents = cobrowse_agent.agents.all()
            else:
                agents = get_list_agents_under_admin(
                    cobrowse_agent, is_active=None)

            cobrowse_video_objs = CobrowseVideoConferencing.objects.filter(
                agent__in=agents)

            if "startdate" in filter_dict:
                date_format = "%Y-%m-%d"
                start_date = filter_dict["startdate"][0]
                start_date = remo_html_from_string(start_date)
                datetime_start = datetime.datetime.strptime(
                    start_date, date_format).date()

                cobrowse_video_objs = cobrowse_video_objs.filter(
                    meeting_start_date__gte=datetime_start)

            if "enddate" in filter_dict:
                date_format = "%Y-%m-%d"
                end_date = filter_dict["enddate"][0]
                end_date = remo_html_from_string(end_date)
                datetime_end = datetime.datetime.strptime(
                    end_date, date_format).date()
                cobrowse_video_objs = cobrowse_video_objs.filter(
                    meeting_start_date__lte=datetime_end)

            if "agent" in filter_dict:
                agent_email = filter_dict["agent"][0]
                agent_email = remo_html_from_string(agent_email)

                try:
                    selected_agent = CobrowseAgent.objects.get(
                        user__username=agent_email)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error CognoVidAuditTrail %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
                    selected_agent = []

                cobrowse_video_objs = cobrowse_video_objs.filter(
                    agent=selected_agent)

            if "meeting-status" in filter_dict:
                meeting_status = filter_dict["meeting-status"][0]
                meeting_status = remo_html_from_string(meeting_status)
                if meeting_status == "completed":
                    cobrowse_video_objs = cobrowse_video_objs.filter(
                        is_expired=True)
                elif meeting_status == "notcompleted":
                    cobrowse_video_objs = cobrowse_video_objs.filter(
                        is_expired=False)

            audit_trail_objs = CobrowseVideoAuditTrail.objects.filter(
                cobrowse_video__in=cobrowse_video_objs).order_by('-pk')

            export_path = create_excel_meeting_support_history(
                cobrowse_agent.user, audit_trail_objs)
            export_path = "/" + export_path
            file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                file_path=export_path, is_public=False)
            response["export_path"] = 'easy-assist-salesforce/download-file/' + \
                str(file_access_management_obj.key) + "/"

            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportMeetingSupportHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportMeetingSupportHistory = ExportMeetingSupportHistoryAPI.as_view()


def SalesAnalyticsDashboard(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        DEFAULT_ANALYTICS_START_DATETIME = (
            datetime.datetime.today() - datetime.timedelta(7)).date()

        DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

        if cobrowse_agent.show_static_analytics:
            return render(request, "EasyAssistSalesforceApp/static-analytics.html", {
                "salesforce_token": quote_plus(request.GET["salesforce_token"]),
                "cobrowse_agent": cobrowse_agent,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
            })
        else:
            return render(request, "EasyAssistSalesforceApp/analytics.html", {
                "salesforce_token": quote_plus(request.GET["salesforce_token"]),
                "cobrowse_agent": cobrowse_agent,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
            })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAnalyticsDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return HttpResponse("Invalid Access")


def SalesAnalyticsOutboundDashboard(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        DEFAULT_ANALYTICS_START_DATETIME = (
            datetime.datetime.today() - datetime.timedelta(7)).date()

        DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

        if cobrowse_agent.show_static_analytics:
            return render(request, "EasyAssistSalesforceApp/analytics_outbound_static.html", {
                "salesforce_token": quote_plus(request.GET["salesforce_token"]),
                "cobrowse_agent": cobrowse_agent,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
            })
        else:
            return render(request, "EasyAssistSalesforceApp/analytics_outbound.html", {
                "salesforce_token": quote_plus(request.GET["salesforce_token"]),
                "cobrowse_agent": cobrowse_agent,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
            })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAnalyticsOutboundDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return HttpResponse("Invalid Access")


def SalesAccessManagement(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        if cobrowse_agent.role not in ["admin", "supervisor"]:
            return HttpResponse(status=401)

        supported_language_objs = cobrowse_agent.supported_language.all()
        product_category_objs = cobrowse_agent.product_category.all()
        agents = cobrowse_agent.agents.filter(role="agent")
        supervisors = cobrowse_agent.agents.filter(role="supervisor")

        for supervisor in supervisors:
            agents = agents | supervisor.agents.all()
        agents = agents.distinct()
        total_agent_count = agents.count()
        active_agent_count = agents.filter(is_active=True).count()
        offline_agent_count = total_agent_count - active_agent_count

        if "is_active" in request.GET:
            is_active = request.GET["is_active"]
            is_active = remo_html_from_string(is_active)
            is_active = remo_special_tag_from_string(is_active)
            if(is_active == "true"):
                agents = agents.filter(is_active=True)
            elif is_active == "false":
                agents = agents.filter(is_active=False)

        if cobrowse_agent.show_static_analytics:
            return render(request, "EasyAssistSalesforceApp/sales_access_management_static.html", {
                "salesforce_token": quote_plus(request.GET["salesforce_token"]),
                "cobrowse_agent": cobrowse_agent,
                "agents": agents, "supervisors": supervisors,
                "COBROWSING_AGENT_SUPPORT": COBROWSING_AGENT_SUPPORT,
                "total_agent_count": total_agent_count,
                "active_agent_count": active_agent_count,
                "offline_agent_count": offline_agent_count,
                "supported_language_objs": supported_language_objs,
                "product_category_objs": product_category_objs
            })

        return render(request, "EasyAssistSalesforceApp/sales_access_management.html", {
            "salesforce_token": quote_plus(request.GET["salesforce_token"]),
            "cobrowse_agent": cobrowse_agent,
            "agents": agents, "supervisors": supervisors,
            "COBROWSING_AGENT_SUPPORT": COBROWSING_AGENT_SUPPORT,
            "total_agent_count": total_agent_count,
            "active_agent_count": active_agent_count,
            "offline_agent_count": offline_agent_count,
            "supported_language_objs": supported_language_objs,
            "product_category_objs": product_category_objs
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAccessManagement %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return HttpResponse("Invalid Access")


def SalesAuditTrail(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        if cobrowse_agent.role not in ["admin"]:
            return HttpResponse(status=401)

        agents = get_list_agents_under_admin(cobrowse_agent, is_active=None)

        if cobrowse_agent not in agents:
            agents += [cobrowse_agent]

        audit_trail_objs = CobrowsingAuditTrail.objects.filter(
            agent__in=agents)

        is_filter_applied = False

        if "startdate" in request.GET:
            date_format = "%Y-%m-%d"
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()
            audit_trail_objs = audit_trail_objs.filter(
                datetime__date__gte=datetime_start)
            is_filter_applied = True

        if "enddate" in request.GET:
            date_format = "%Y-%m-%d"
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()
            audit_trail_objs = audit_trail_objs.filter(
                datetime__date__lte=datetime_end)
            is_filter_applied = True

        if "action" in request.GET:
            action = request.GET.getlist("action")[0]
            action = remo_html_from_string(action)
            action = COBROWSING_REVERSE_ACTION_DICT[action]
            audit_trail_objs = audit_trail_objs.filter(action=action)
            is_filter_applied = True

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")[0]
            agent_email = remo_html_from_string(agent_email)
            selected_agent = CobrowseAgent.objects.get(
                user__username=agent_email)
            audit_trail_objs = audit_trail_objs.filter(agent=selected_agent)
            is_filter_applied = True

        if not is_filter_applied:
            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()
            datetime_end = datetime.datetime.today().date()
            audit_trail_objs = audit_trail_objs.filter(datetime__date__gte=datetime_start,
                                                       datetime__date__lte=datetime_end)
            is_filter_applied = True

        if audit_trail_objs.count() > 0:
            audit_trail_objs = audit_trail_objs.order_by('-datetime')

        return render(request, "EasyAssistSalesforceApp/sales_audit_trail.html", {
            "salesforce_token": quote_plus(request.GET["salesforce_token"]),
            "cobrowse_agent": cobrowse_agent,
            "agents": agents,
            "audit_trail_objs": audit_trail_objs,
            "action_list": COBROWSING_ACTION_LIST,
            "is_filter_applied": is_filter_applied
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAuditTrail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return HttpResponse("Invalid Access")


def SalesAgentAuditTrail(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        if cobrowse_agent.role not in ["admin"]:
            return HttpResponse(status=401)

        agents = get_list_agents_under_admin(cobrowse_agent, is_active=None)

        if cobrowse_agent not in agents:
            agents += [cobrowse_agent]

        agent_online_audit_trail_objs = CobrowseAgentOnlineAuditTrail.objects.filter(
            agent__in=agents)

        is_filter_applied = False

        if "startdate" in request.GET:
            date_format = "%Y-%m-%d"
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()
            agent_online_audit_trail_objs = agent_online_audit_trail_objs.filter(
                last_online_start_datetime__date__gte=datetime_start)
            is_filter_applied = True

        if "enddate" in request.GET:
            date_format = "%Y-%m-%d"
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()
            agent_online_audit_trail_objs = agent_online_audit_trail_objs.filter(
                last_online_start_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")[0]
            agent_email = remo_html_from_string(agent_email)
            selected_agent = CobrowseAgent.objects.get(
                user__username=agent_email)
            agent_online_audit_trail_objs = agent_online_audit_trail_objs.filter(
                agent=selected_agent)
            is_filter_applied = True

        if not is_filter_applied:
            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()
            datetime_end = datetime.datetime.today().date()
            agent_online_audit_trail_objs = agent_online_audit_trail_objs.filter(last_online_start_datetime__date__gte=datetime_start,
                                                                                 last_online_end_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if agent_online_audit_trail_objs.count() > 0:
            agent_online_audit_trail_objs = agent_online_audit_trail_objs.order_by(
                '-last_online_start_datetime')

        agent_date_wise_duration = {}
        for audit_trail_obj in agent_online_audit_trail_objs:
            duration = audit_trail_obj.last_online_end_datetime - \
                audit_trail_obj.last_online_start_datetime
            est = pytz.timezone(settings.TIME_ZONE)
            date_string = audit_trail_obj.last_online_start_datetime.astimezone(
                est).strftime("%b. %d, %Y")

            if date_string not in agent_date_wise_duration:
                agent_date_wise_duration[date_string] = {}

            if str(audit_trail_obj.agent.user.username) not in agent_date_wise_duration[date_string]:
                agent_date_wise_duration[date_string][str(
                    audit_trail_obj.agent.user.username)] = 0

            agent_date_wise_duration[date_string][str(
                audit_trail_obj.agent.user.username)] += duration.seconds

        agent_wise_audit_trail = []
        for date_string in agent_date_wise_duration:
            for agent_username in agent_date_wise_duration[date_string]:
                agent_wise_audit_trail.append({
                    "agent_username": agent_username,
                    "date": date_string,
                    "duration": convert_seconds_to_hours_minutes(agent_date_wise_duration[date_string][agent_username])
                })

        return render(request, "EasyAssistSalesforceApp/sales_agent_audit_trail.html", {
            "salesforce_token": quote_plus(request.GET["salesforce_token"]),
            "cobrowse_agent": cobrowse_agent,
            "agents": agents,
            "agent_wise_audit_trail": agent_wise_audit_trail,
            "is_filter_applied": is_filter_applied
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAgentAuditTrail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return HttpResponse("Invalid Access")


def ArchiveCobrowsingLead(request, session_id):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
        cobrowse_io.is_archived = True
        cobrowse_io.save()
        return redirect("/easy-assist-salesforce/sales-ai/dashboard/?salesforce_token=" + quote_plus(request.GET["salesforce_token"]))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ArchiveCobrowsingLead %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return HttpResponse("Invalid Request")


# def RenderLastStateOfCobrowsingSession(request, session_id):
#     try:
#         if not request.user.is_authenticated:
#             return HttpResponse("Unauthorized Access")

#         cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
#         return render(request, "EasyAssistSalesforceApp/last_state.html", {"cobrowse_io_obj": cobrowse_io})
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("Error RenderLastStateOfCobrowsingSession %s at %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

#         return HttpResponse("Invalid Request")


class SyncCobrowseIOAgentAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if cobrowse_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            id = data["id"]
            id = remo_html_from_string(id)

            cobrowse_io_obj = None
            try:
                cobrowse_io_obj = CobrowseIO.objects.get(session_id=id)
            except Exception:
                pass

            if cobrowse_io_obj != None:

                cobrowse_io_obj.last_agent_update_datetime = timezone.now()
                cobrowse_io_obj.is_agent_connected = True
                cobrowse_io_obj.save()

                cobrowse_agent.is_cobrowsing_active = True
                cobrowse_agent.is_active = True
                cobrowse_agent.last_agent_active_datetime = timezone.now()
                cobrowse_agent.save()

                response[
                    "is_client_connected"] = cobrowse_io_obj.is_active and cobrowse_io_obj.is_active_timer()
                response["is_active"] = cobrowse_io_obj.is_active
                response["is_archived"] = cobrowse_io_obj.is_archived
                response[
                    "init_transaction"] = cobrowse_io_obj.init_transaction and cobrowse_io_obj.is_transaction_active_timer()
                response["status"] = 200
                response["message"] = "success"
            else:
                response["is_client_connected"] = False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SyncCobrowseIOAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SyncCobrowseIOAgent = SyncCobrowseIOAgentAPI.as_view()


class SyncHighlightCobrowseIOAgentAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = data["id"]
            id = remo_html_from_string(id)
            position = data["position"]
            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            cobrowse_io.is_highlighted = True
            cobrowse_io.position = json.dumps(position)
            cobrowse_io.save()
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SyncHighlightCobrowseIOAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SyncHighlightCobrowseIOAgent = SyncHighlightCobrowseIOAgentAPI.as_view()


# class TakeClientScreenshotAPI(APIView):

#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         response = {}
#         response['status'] = 500
#         custom_encrypt_obj = CustomEncrypt()
#         try:
#             data = request.data["Request"]
#             data = custom_encrypt_obj.decrypt(data)
#             data = json.loads(data)
#             id = data["id"]
#             id = remo_html_from_string(id)
#             screenshot_type = data["screenshot_type"]
#             screenshot_type = remo_html_from_string(screenshot_type)
#             cobrowse_io = CobrowseIO.objects.get(session_id=id)
#             cobrowse_io.take_screenshot = True
#             cobrowse_io.type_screenshot = screenshot_type
#             cobrowse_io.save()
#             response["status"] = 200
#             response["message"] = "success"
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error("Error TakeClientScreenshotAPI %s at %s",
#                          str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

#         response = json.dumps(response)
#         encrypted_response = custom_encrypt_obj.encrypt(response)
#         response = {"Response": encrypted_response}
#         return Response(data=response)


# TakeClientScreenshot = TakeClientScreenshotAPI.as_view()


class CloseCobrowsingSessionAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["id"])
            id = remo_html_from_string(id)
            comments = strip_html_tags(data["comments"])

            meeting_io = CobrowseVideoConferencing.objects.filter(
                meeting_id=id)

            if meeting_io:
                meeting_io = meeting_io[0]
                meeting_io.is_expired = True
                meeting_io.save()

                try:
                    audit_trail = CobrowseVideoAuditTrail.objects.get(
                        cobrowse_video=meeting_io)
                    audit_trail.meeting_ended = timezone.now()
                    audit_trail.is_meeting_ended = True
                    audit_trail.save()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error CloseCobrowsingSessionAPI %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

            cobrowse_io = CobrowseIO.objects.get(session_id=id)

            is_helpful = True
            if cobrowse_io.is_helpful == False:
                if "is_helpful" in data:
                    is_helpful = data["is_helpful"]

            is_test = False
            if "is_test" in data:
                is_test = data["is_test"]

            if str(active_agent.user.username) == str(cobrowse_io.agent):
                cobrowse_io.is_archived = True
                cobrowse_io.is_agent_connected = False
                cobrowse_io.is_closed_session = True
                cobrowse_io.is_helpful = is_helpful
                cobrowse_io.is_test = is_test
                cobrowse_io.agent_comments = comments
                cobrowse_io.agent_session_end_time = timezone.now()
                cobrowse_io.save()

            save_agent_closing_comments_cobrowseio(
                cobrowse_io, active_agent, comments, CobrowseAgentComment)

            category = "session_closed"
            description = "Session is archived by " + \
                str(active_agent.user.username) + " after submitting comments"
            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, active_agent)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CloseCobrowsingSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CloseCobrowsingSession = CloseCobrowsingSessionAPI.as_view()


class GetCobrowsingMetaInformationAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = data["id"]
            id = remo_html_from_string(id)
            page = data["page"]

            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            cobrowse_meta_objs = CobrowsingSessionMetaData.objects.filter(
                cobrowse_io=cobrowse_io).order_by('-datetime')

            paginator = Paginator(cobrowse_meta_objs, 4)
            no_pages = paginator.num_pages

            is_last_page = False
            if int(page) >= int(no_pages):
                is_last_page = True

            try:
                cobrowse_meta_objs = paginator.page(page)
            except PageNotAnInteger:
                cobrowse_meta_objs = paginator.page(1)
            except EmptyPage:
                cobrowse_meta_objs = paginator.page(
                    paginator.num_pages)

            meta_information_list = []
            for cobrowse_meta_obj in cobrowse_meta_objs:

                est = pytz.timezone(settings.TIME_ZONE)
                datetime = cobrowse_meta_obj.datetime.astimezone(
                    est).strftime("%b %d %Y %I:%M %p")

                meta_information_list.append({
                    "id": cobrowse_meta_obj.pk,
                    "type": cobrowse_meta_obj.type_screenshot,
                    "content": "/easy-assist-salesforce/pageshot/" + str(cobrowse_meta_obj.pk),
                    "datetime": datetime
                })

            response["status"] = 200
            response["message"] = "success"
            response["is_last_page"] = is_last_page
            response["meta_information_list"] = meta_information_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCobrowsingMetaInformationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCobrowsingMetaInformation = GetCobrowsingMetaInformationAPI.as_view()


class SaveAgentDetailsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            user = active_agent.user

            old_password = strip_html_tags(data["old_password"])
            new_password = strip_html_tags(data["new_password"])

            is_valid_password = True
            is_password_changed = False
            if old_password != "":
                if not user.check_password(old_password):
                    is_valid_password = False
                else:
                    is_password_changed = True

            if is_valid_password:

                user.first_name = strip_html_tags(data["agent_name"])

                if is_password_changed:
                    user.is_online = False
                    user.set_password(new_password)

                user.save()

                if active_agent.role != "admin":

                    active_agent.mobile_number = strip_html_tags(
                        data["agent_mobile_number"])

                    active_agent.support_level = strip_html_tags(
                        data["agent_support_level"])

                    if is_password_changed:
                        active_agent.is_active = False

                    active_agent.save()

                save_audit_trail(active_agent, COBROWSING_CHANGESETTINGS_ACTION,
                                 "General Settings has been changed", CobrowsingAuditTrail)

                response["status"] = 200
                response["message"] = "success"
                response["is_password_changed"] = is_password_changed
            else:
                response["status"] = 101
                response[
                    "message"] = "Your old password is incorrect. Kindly enter valid password."
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveAgentDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveAgentDetails = SaveAgentDetailsAPI.as_view()


class AddNewAgentDetailsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            if active_agent.role != "agent":
                agent_mobile = strip_html_tags(data["agent_mobile"])
                agent_mobile = remo_html_from_string(agent_mobile)
                if agent_mobile == "":
                    agent_mobile = None

                if CobrowseAgent.objects.filter(user__email=data["agent_email"]).count() > 0:
                    response["status"] = 301
                    response[
                        "message"] = "Matching cobrowsing agent already exists"

                elif agent_mobile != None and CobrowseAgent.objects.filter(mobile_number=agent_mobile).count() > 0:
                    response["status"] = 301
                    response[
                        "message"] = "Matching cobrowsing agent already exists"

                elif data["user_type"] in ["agent", "supervisor"]:

                    agent_name = strip_html_tags(data["agent_name"])
                    agent_name = remo_html_from_string(agent_name)
                    agent_email = strip_html_tags(data["agent_email"])
                    agent_email = remo_html_from_string(agent_email)
                    user_type = strip_html_tags(data["user_type"])
                    user_type = remo_html_from_string(user_type)
                    support_level = strip_html_tags(data["support_level"])
                    support_level = remo_html_from_string(support_level)
                    platform_url = strip_html_tags(data["platform_url"])
                    platform_url = remo_html_from_string(platform_url)
                    selected_supervisor_pk_list = data[
                        "selected_supervisor_pk_list"]
                    selected_language_pk_list = data[
                        "selected_language_pk_list"]
                    selected_product_category_pk_list = data[
                        "selected_product_category_pk_list"]

                    user = None
                    password = generate_random_password()

                    try:
                        user = User.objects.get(username=agent_email)
                        user.email = agent_email
                        user.save()
                    except Exception:
                        user = User.objects.create(first_name=agent_name,
                                                   email=agent_email,
                                                   username=agent_email,
                                                   status="2",
                                                   role="bot_builder")
                        user.set_password(password)
                        user.save()

                    thread = threading.Thread(target=send_password_over_email, args=(
                        agent_email, agent_name, password, platform_url, ), daemon=True)
                    thread.start()

                    user.set_password(password)
                    user.save()

                    cobrowse_agent = CobrowseAgent.objects.create(user=user,
                                                                  mobile_number=agent_mobile,
                                                                  role=user_type,
                                                                  support_level=support_level)

                    add_selected_supervisor(
                        selected_supervisor_pk_list, active_agent, cobrowse_agent, CobrowseAgent)
                    add_supported_language(
                        cobrowse_agent, selected_language_pk_list, LanguageSupport)
                    add_product_category_to_user(
                        cobrowse_agent, selected_product_category_pk_list, ProductCategory)

                    SalesforceAgent.objects.create(email=agent_email)

                    description = "New " + \
                        data["user_type"] + \
                        " (" + agent_name + ") has been added"
                    save_audit_trail(
                        active_agent, COBROWSING_ADDUSER_ACTION, description, CobrowsingAuditTrail)
                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddNewAgentDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddNewAgentDetails = AddNewAgentDetailsAPI.as_view()


class UpdateAgentDetailsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logger.info("Into Update Agent Details API",
                    extra={'AppName': 'EasyAssistSalesforce'})
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, User, CobrowseAgent)

            if active_agent.role != "agent":
                try:
                    pk = strip_html_tags(data["pk"])
                    pk = remo_html_from_string(pk)
                    cobrowse_agent = CobrowseAgent.objects.get(
                        user=User.objects.get(pk=int(pk)))
                    agent_mobile = strip_html_tags(data["agent_mobile"])
                    agent_mobile = remo_html_from_string(agent_mobile)

                    if agent_mobile == "":
                        agent_mobile = None

                    if cobrowse_agent.user.email != data["agent_email"] and CobrowseAgent.objects.filter(user__email=data["agent_email"]).count() > 0:
                        response["status"] = 301
                        response[
                            "message"] = "Matching cobrowsing agent already exists"

                    elif agent_mobile != None and cobrowse_agent.mobile_number != agent_mobile and CobrowseAgent.objects.filter(mobile_number=agent_mobile).count() > 0:
                        response["status"] = 301
                        response[
                            "message"] = "Matching cobrowsing agent already exists"

                    elif data["user_type"] in ["agent", "supervisor"]:

                        agent_name = strip_html_tags(data["agent_name"])
                        agent_name = remo_html_from_string(agent_name)
                        agent_email = strip_html_tags(data["agent_email"])
                        agent_email = remo_html_from_string(agent_email)
                        user_type = strip_html_tags(data["user_type"])
                        user_type = remo_html_from_string(user_type)
                        support_level = strip_html_tags(data["support_level"])
                        support_level = remo_html_from_string(support_level)
                        platform_url = strip_html_tags(data["platform_url"])
                        platform_url = remo_html_from_string(platform_url)
                        selected_supervisor_pk_list = data[
                            "selected_supervisor_pk_list"]
                        previous_supervisor_list = CobrowseAgent.objects.filter(
                            agents__pk=cobrowse_agent.pk)
                        selected_language_pk_list = data[
                            "selected_language_pk_list"]
                        selected_product_category_pk_list = data[
                            "selected_product_category_pk_list"]

                        if cobrowse_agent.user.email != agent_email:
                            password = generate_random_password()
                            cobrowse_agent.user.set_password(password)
                            cobrowse_agent.user.save()
                            thread = threading.Thread(target=send_password_over_email, args=(
                                agent_email, agent_name, password, platform_url, ), daemon=True)
                            thread.start()

                        cobrowse_agent.user.first_name = agent_name
                        cobrowse_agent.user.email = agent_email
                        cobrowse_agent.user.username = agent_email

                        cobrowse_agent.mobile_number = agent_mobile
                        cobrowse_agent.support_level = support_level
                        cobrowse_agent.role = user_type

                        agents = cobrowse_agent.agents.all()
                        for agent in agents:
                            cobrowse_agent.agents.remove(agent)
                            cobrowse_agent.save()
                            active_agent.agents.add(agent)
                            active_agent.save()

                        for previous_supervisor in previous_supervisor_list:
                            previous_supervisor.agents.remove(cobrowse_agent)
                            previous_supervisor.save()

                        add_selected_supervisor(
                            selected_supervisor_pk_list, active_agent, cobrowse_agent, CobrowseAgent)

                        cobrowse_agent.supported_language.clear()
                        cobrowse_agent.product_category.clear()
                        cobrowse_agent.user.save()
                        cobrowse_agent.save()
                        active_agent.save()
                        add_supported_language(
                            cobrowse_agent, selected_language_pk_list, LanguageSupport)
                        add_product_category_to_user(
                            cobrowse_agent, selected_product_category_pk_list, ProductCategory)

                        description = "New Details for " + \
                            data["user_type"] + \
                            " (" + agent_name + ") has been added"
                        save_audit_trail(
                            active_agent, COBROWSING_ADDUSER_ACTION, description, CobrowsingAuditTrail)
                        response["status"] = 200
                        response["message"] = "success"
                        logger.info("Successfully exited Update Agent Details API", extra={
                                    'AppName': 'EasyAssistSalesforce'})

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error Agent not found %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateAgentDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateAgentDetails = UpdateAgentDetailsAPI.as_view()


class ResendAccountPasswordAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            user_pk = data["user_pk"]
            platform_url = data["platform_url"]

            try:
                cobrowse_agent = CobrowseAgent.objects.get(pk=int(user_pk))
                user = cobrowse_agent.user

                password = generate_random_password()

                thread = threading.Thread(target=send_password_over_email, args=(
                    user.email, user.first_name, password, platform_url, ), daemon=True)
                thread.start()

                user.set_password(password)
                user.save()

                cobrowse_agent.user = user
                cobrowse_agent.save()

                response["status"] = 200
                response["message"] = "Password sent to " + \
                    str(cobrowse_agent.user.email)
            except Exception:
                response["status"] = 300
                response["message"] = "Could not send the password"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ResendAccountPasswordAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ResendAccountPassword = ResendAccountPasswordAPI.as_view()


class UploadUserDetailsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            if active_agent.role == "admin":

                filename = strip_html_tags(data["filename"])
                filename = remo_html_from_string(filename)
                base64_data = strip_html_tags(data["base64_file"])

                filename = generate_random_key(
                    10) + "_" + filename.replace(" ", "")

                file_path = "files/" + filename

                file_extension = file_path.split(".")[-1]
                file_extension = file_extension.lower()

                if file_extension in ["xls", "xlsx", "xlsm", "xlt", "xltm"]:
                    media_type = "excel"
                else:
                    media_type = None

                if media_type == None or check_malicious_file_from_filename(filename):
                    response["status"] = 300
                else:
                    fh = open(file_path, "wb")
                    fh.write(base64.b64decode(base64_data))
                    fh.close()

                    add_users_from_excel_document(file_path, active_agent,
                                                  User, CobrowseAgent, LanguageSupport, SalesforceAgent)

                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadUserDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadUserDetails = UploadUserDetailsAPI.as_view()


class ExportUserDetailsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)

            export_path = create_excel_user_details(active_agent)
            response["export_path"] = export_path
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportUserDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportUserDetails = ExportUserDetailsAPI.as_view()


class DownloadUserDetailsTemplateAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            export_path = "files/templates/User_Details_Template.xlsx"
            response["export_path"] = export_path
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DownloadUserDetailsTemplateAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DownloadUserDetailsTemplate = DownloadUserDetailsTemplateAPI.as_view()


class DeleteCobrowserLogoAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)

            if active_agent.role == "admin":

                cobrowse_access_token = active_agent.get_access_token_obj()
                cobrowse_access_token.source_easyassist_cobrowse_logo = ""
                cobrowse_access_token.save()
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteCobrowserLogoAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteCobrowserLogo = DeleteCobrowserLogoAPI.as_view()


class UploadCobrowserLogoAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            if active_agent.role == "admin":

                cobrowse_access_token = active_agent.get_access_token_obj()

                filename = strip_html_tags(data["filename"])
                base64_data = strip_html_tags(data["base64_file"])

                filename = generate_random_key(
                    10) + "_" + filename.replace(" ", "")

                file_path = "files/" + filename

                file_extention = file_path.split(".")[-1]
                file_extention = file_extention.lower()
                if file_extention in ["png", "jpg", "jpeg", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg", "jpe"]:
                    media_type = "image"
                else:
                    media_type = None

                if media_type == None or check_malicious_file_from_filename(filename):
                    response["status"] = 300
                else:
                    fh = open(file_path, "wb")
                    fh.write(base64.b64decode(base64_data))
                    fh.close()
                    cobrowse_access_token.source_easyassist_cobrowse_logo = file_path
                    cobrowse_access_token.save()

                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadCobrowserLogoAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadCobrowserLogo = UploadCobrowserLogoAPI.as_view()


class UploadConnectWithAgentIconAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            if active_agent.role == "admin":

                cobrowse_access_token = active_agent.get_access_token_obj()

                filename = strip_html_tags(data["filename"])
                filename = remo_html_from_string(filename)
                base64_data = strip_html_tags(data["base64_file"])

                filename = generate_random_key(
                    10) + "_" + filename.replace(" ", "")

                file_path = "files/" + filename

                file_extention = file_path.split(".")[-1]
                file_extention = file_extention.lower()

                if file_extention in ["png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"]:
                    media_type = "image"
                else:
                    media_type = None

                if media_type == None or check_malicious_file_from_filename(filename):
                    response["status"] = 300
                else:
                    fh = open(file_path, "wb")
                    fh.write(base64.b64decode(base64_data))
                    fh.close()
                    cobrowse_access_token.source_easyassist_connect_agent_icon = file_path
                    cobrowse_access_token.save()

                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadConnectWithAgentIconAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadConnectWithAgentIcon = UploadConnectWithAgentIconAPI.as_view()


class SaveAgentCommentsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            agent_comments = strip_html_tags(data["agent_comments"])
            agent_comments = remo_html_from_string(agent_comments)

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            cobrowse_io.agent_comments = agent_comments
            cobrowse_io.save()

            save_agent_closing_comments_cobrowseio(
                cobrowse_io, active_agent, agent_comments, CobrowseAgentComment)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveAgentCommentsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveAgentComments = SaveAgentCommentsAPI.as_view()


class SearchCobrowsingLeadAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logger.info("Inside SearchCobrowsingLeadAPI",
                    extra={'AppName': 'EasyAssistSalesforce'})
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            logger.info("Request: " + json.dumps(data),
                        extra={'AppName': 'EasyAssistSalesforce'})

            search_value = strip_html_tags(data["search_value"])
            search_value = search_value.strip().lower()
            md5_primary_id = hashlib.md5(search_value.encode()).hexdigest()

            active_admin_user = get_admin_from_active_agent(
                active_agent, CobrowseAgent)

            cobrowse_io_list = []

            if "session_id" in data:
                cobrowse_io_list = CobrowseIO.objects.filter(
                    session_id=data["session_id"])
            else:
                cobrowse_leads = CobrowseCapturedLeadData.objects.filter(
                    primary_value=md5_primary_id)
                cobrowse_io_list = CobrowseIO.objects.filter(is_lead=True,
                                                             is_archived=False,
                                                             captured_lead__in=cobrowse_leads,
                                                             access_token__agent=active_admin_user).order_by('-last_update_datetime')

            show_verification_code = False
            allow_cobrowsing_meeting = False
            allow_video_meeting_only = False
            cobrowse_io_details = []

            for cobrowse_io in cobrowse_io_list:
                allow_cobrowsing_meeting = cobrowse_io.access_token.allow_cobrowsing_meeting
                allow_video_meeting_only = cobrowse_io.access_token.allow_video_meeting_only
                est = pytz.timezone(settings.TIME_ZONE)

                datetime = cobrowse_io.last_update_datetime.astimezone(
                    est).strftime("%d %b %Y %I:%M %p")

                is_active = cobrowse_io.is_active_timer() and cobrowse_io.is_active

                show_verification_code = cobrowse_io.access_token.enable_verification_code_popup

                OTP = "-"
                if is_active and cobrowse_io.otp_validation != None:
                    OTP = cobrowse_io.otp_validation

                if cobrowse_io.is_lead:
                    cobrowse_io.agent = active_agent
                    cobrowse_io.save()

                cobrowse_io_details.append({
                    "session_id": str(cobrowse_io.session_id),
                    "is_active": is_active,
                    "datetime": datetime,
                    "agent_assistant_request_status": cobrowse_io.agent_assistant_request_status,
                    "agent_meeting_request_status": cobrowse_io.agent_meeting_request_status,
                    "allow_agent_meeting": cobrowse_io.allow_agent_meeting,
                    "allow_agent_cobrowse": cobrowse_io.allow_agent_cobrowse,
                    "otp": OTP
                })

            response["status"] = 200
            response["message"] = "success"
            response["cobrowse_io_details"] = cobrowse_io_details[:5]
            response["show_verification_code"] = show_verification_code
            response["allow_cobrowsing_meeting"] = allow_cobrowsing_meeting
            response["allow_video_meeting_only"] = allow_video_meeting_only
            logger.info("Response: " + json.dumps(response),
                        extra={'AppName': 'EasyAssistSalesforce'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SearchCobrowsingLeadAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        logger.info("Successfully exited from SearchCobrowsingLeadAPI", extra={
                    'AppName': 'EasyAssistSalesforce'})
        return Response(data=response)


SearchCobrowsingLead = SearchCobrowsingLeadAPI.as_view()


class AssignCobrowsingLeadAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            if cobrowse_io.allow_agent_cobrowse == "true":
                cobrowse_io.agent = active_agent
                cobrowse_io.save()

            response["status"] = 200
            response["message"] = "success"
            response["allow_screen_sharing_cobrowse"] = cobrowse_io.access_token.allow_screen_sharing_cobrowse
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AssignCobrowsingLeadAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AssignCobrowsingLead = AssignCobrowsingLeadAPI.as_view()


class AssignCobrowsingSessionAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            agent_id = strip_html_tags(data["agent_id"])

            cobrowse_agent = CobrowseAgent.objects.get(pk=int(agent_id))
            if cobrowse_agent.is_active == True:
                cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
                cobrowse_io.agent = cobrowse_agent
                cobrowse_io.save()
                response["status"] = 200
                response["message"] = "success"
            else:
                response["status"] = 400
                response["message"] = "failed"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AssignCobrowsingSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AssignCobrowsingSession = AssignCobrowsingSessionAPI.as_view()


class RequestCobrowsingAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)

            otp = random_with_n_digits(4)

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            cobrowse_io.agent_assistant_request_status = True
            cobrowse_io.allow_agent_cobrowse = None
            cobrowse_io.cobrowsing_start_datetime = None
            cobrowse_io.otp_validation = otp
            cobrowse_io.save()

            category = "session_details"
            description = "Request for cobrowsing sent by " + \
                str(active_agent.user.username)
            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, active_agent)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RequestCobrowsingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


RequestCobrowsing = RequestCobrowsingAPI.as_view()


class MarkLeadInactiveAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cobrowse_io_objs = CobrowseIO.objects.filter(
                agent=active_agent, is_lead=True, allow_agent_cobrowse="true")

            for cobrowse_io_obj in cobrowse_io_objs:
                if cobrowse_io_obj.is_archived != True or cobrowse_io_obj.is_agent_connected != False:
                    cobrowse_io_obj.is_archived = True
                    cobrowse_io_obj.is_agent_connected = False
                    cobrowse_io_obj.save()

                    category = "session_closed"
                    description = "Cobrowsing lead is marked as inactive by " + \
                        str(active_agent.user.username)
                    save_system_audit_trail(
                        category, description, cobrowse_io_obj, cobrowse_io_obj.access_token, SystemAuditTrail, active_agent)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error MarkLeadInactiveAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


MarkLeadInactive = MarkLeadInactiveAPI.as_view()


class ChangeAgentActivateStatusAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            agent_id_list = data["agent_id_list"]
            activate = data["activate"]

            if active_agent.role != "agent" and (activate == True or activate == False):
                if activate == False:
                    for agent_id in agent_id_list:
                        agent = CobrowseAgent.objects.get(pk=int(agent_id))
                        if agent.is_cobrowsing_active == True:
                            response['status'] = 301
                            if len(agent_id_list) > 1:
                                response[
                                    'message'] = 'Some of the Agents are currently in Cobrowse Session'
                            else:
                                response[
                                    'message'] = 'Agent is currently in Cobrowse Session'

                if response['status'] != 301:
                    for agent_id in agent_id_list:
                        agent = CobrowseAgent.objects.get(pk=int(agent_id))
                        if agent in active_agent.agents.all():
                            agent.is_account_active = activate
                            agent.is_active = agent.is_active and activate
                            agent.save()

                            if not activate:
                                description = agent.user.username + \
                                    " (" + agent.role + ") is marked as inactive."
                                save_audit_trail(
                                    active_agent, COBROWSING_UPDATEUSER_ACTION, description, CobrowsingAuditTrail)
                            else:
                                description = agent.user.username + \
                                    " (" + agent.role + ") is marked as active."
                                save_audit_trail(
                                    active_agent, COBROWSING_UPDATEUSER_ACTION, description, CobrowsingAuditTrail)

                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ChangeAgentActivateStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ChangeAgentActivateStatus = ChangeAgentActivateStatusAPI.as_view()


# class GetCaptchaAPI(APIView):

#     def post(self, request, *args, **kwargs):
#         response = {}
#         response['status'] = 500
#         custom_encrypt_obj = CustomEncrypt()
#         try:
#             data = request.data["Request"]
#             data = custom_encrypt_obj.decrypt(data)
#             data = json.loads(data)

#             captcha = []
#             with open(settings.BASE_DIR + "/EasyAssistSalesforceApp/captcha.py") as captcha_py:
#                 captcha = json.loads(captcha_py.read())

#             selected_captcha = random.choice(captcha)

#             response["status"] = 200
#             response["message"] = "success"
#             response["file"] = "/static/EasyAssistSalesforceApp/captcha_images/" + \
#                 selected_captcha["file"]
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error("Error GetCaptchaAPI %s at %s",
#                          str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

#         response = json.dumps(response)
#         encrypted_response = custom_encrypt_obj.encrypt(response)
#         response = {"Response": encrypted_response}
#         return Response(data=response)


# GetCaptcha = GetCaptchaAPI.as_view()


# class AgentResetPasswordAPI(APIView):

#     def post(self, request, *args, **kwargs):
#         response = {}
#         response["status"] = 500
#         response["message"] = "Invalid username or password"
#         custom_encrypt_obj = CustomEncrypt()
#         try:
#             data = request.data["Request"]
#             data = custom_encrypt_obj.decrypt(data)
#             data = json.loads(data)

#             cobrowsemiddlewaretoken = strip_html_tags(
#                 data["cobrowsemiddlewaretoken"])
#             username = strip_html_tags(data["username"])
#             username = remo_html_from_string(username)
#             username = remo_special_tag_from_string(username)
#             captcha = strip_html_tags(data["captcha"])
#             user_captcha = strip_html_tags(data["user_captcha"])
#             user_captcha = remo_html_from_string(user_captcha)
#             platform_url = strip_html_tags(data["platform_url"])
#             platform_url = remo_html_from_string(platform_url)

#             user_captcha = generate_md5(user_captcha)
#             captcha, _ = captcha.split(".")

#             if user_captcha != captcha:
#                 response["status"] = 101
#                 response["message"] = "Invalid captcha"
#             else:
#                 user_obj = None
#                 try:
#                     user_obj = User.objects.get(username=username)
#                 except Exception:
#                     pass

#                 if user_obj != None:
#                     cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
#                     password = generate_random_password()

#                     thread = threading.Thread(target=send_password_over_email, args=(
#                         user_obj.username, user_obj.first_name, password, platform_url, ), daemon=True)
#                     thread.start()

#                     user_obj.set_password(password)
#                     user_obj.save()
#                     response["status"] = 200
#                     response["message"] = "success"
#                 else:
#                     response["status"] = 101
#                     response[
#                         "message"] = "If email/username exists in our DB, an email for your password reset will be sent!"
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error("Error AgentResetPasswordAPI %s at %s",
#                          str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

#         response = json.dumps(response)
#         encrypted_response = custom_encrypt_obj.encrypt(response)
#         response = {"Response": encrypted_response}
#         return Response(data=response)


# AgentResetPassword = AgentResetPasswordAPI.as_view()


class ShareCobrowsingSessionAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["id"])
            id = remo_html_from_string(id)
            support_agents = data["support_agents"]
            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            agent_admin = cobrowse_io.access_token.agent
            agents = get_list_agents_under_admin(agent_admin, is_active=True)

            agent_username_list = []
            for user_id in support_agents:
                user_obj = User.objects.get(pk=int(user_id))
                cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
                if cobrowse_agent in agents:
                    cobrowse_io.support_agents.add(cobrowse_agent)
                    agent_username_list.append(cobrowse_agent.user.username)

            shared_agent_details = ", ".join(agent_username_list)
            category = "session_details"
            description = "Cobrowsing session is shared with " + shared_agent_details

            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, active_agent)

            cobrowse_io.save()
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ShareCobrowsingSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ShareCobrowsingSession = ShareCobrowsingSessionAPI.as_view()


class GetListOfSupportAgentsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["id"])
            id = remo_html_from_string(id)
            selected_lang_pk = data["selected_lang_pk"]
            selected_product_category_pk = data["selected_product_category_pk"]

            selected_lang_obj = None
            if str(selected_lang_pk) != "-1":
                selected_lang_obj = LanguageSupport.objects.get(
                    pk=int(selected_lang_pk))

            selected_product_category_obj = None
            if str(selected_product_category_pk) != "-1":
                selected_product_category_obj = ProductCategory.objects.get(
                    pk=int(selected_product_category_pk))

            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            agent_admin = cobrowse_io.access_token.agent

            agents = get_list_agents_under_admin(agent_admin, is_active=True)

            support_agents = []
            for agent in agents:
                if agent.user.username != active_agent.user.username and agent != cobrowse_io.agent:
                    if cobrowse_io.access_token.allow_language_support:
                        if selected_lang_obj in agent.supported_language.all():
                            if cobrowse_io.access_token.choose_product_category:
                                if str(selected_product_category_pk) == "-1" or selected_product_category_obj in agent.product_category.all():
                                    support_agents.append({
                                        "id": agent.user.pk,
                                        "username": agent.user.username,
                                        "level": agent.support_level
                                    })
                            else:
                                support_agents.append({
                                    "id": agent.user.pk,
                                    "username": agent.user.username,
                                    "level": agent.support_level
                                })
                        elif str(selected_lang_pk) == "-1":
                            if cobrowse_io.access_token.choose_product_category:
                                if selected_product_category_obj in agent.product_category.all():
                                    support_agents.append({
                                        "id": agent.user.pk,
                                        "username": agent.user.username,
                                        "level": agent.support_level
                                    })
                    else:
                        if cobrowse_io.access_token.choose_product_category:
                            if selected_product_category_obj in agent.product_category.all():
                                support_agents.append({
                                    "id": agent.user.pk,
                                    "username": agent.user.username,
                                    "level": agent.support_level
                                })
                        else:
                            support_agents.append({
                                "id": agent.user.pk,
                                "username": agent.user.username,
                                "level": agent.support_level
                            })

            response["status"] = 200
            response["message"] = "success"
            response["support_agents"] = support_agents
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetListOfSupportAgentsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetListOfSupportAgents = GetListOfSupportAgentsAPI.as_view()


class GetSupportMaterialAgentAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["id"])
            id = remo_html_from_string(id)

            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            agent_admin = cobrowse_io.access_token.agent

            agents_for_support_document = get_supervisor_from_active_agent(
                active_agent, CobrowseAgent)
            agents_for_support_document.append(agent_admin)

            support_document_objs = SupportDocument.objects.filter(
                agent__in=agents_for_support_document, is_usable=True, is_deleted=False)

            support_document = []
            for support_document_obj in support_document_objs:
                file_path = "easy-assist-salesforce/download-file/" + \
                    support_document_obj.file_access_management_key + "/"
                support_document.append({
                    "file_name": support_document_obj.file_name,
                    "file_path": file_path,
                    "file_type": support_document_obj.file_type
                })

            response["status"] = 200
            response["message"] = "success"
            response["support_document"] = support_document
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetSupportMaterialAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetSupportMaterialAgent = GetSupportMaterialAgentAPI.as_view()


def ExportCapturedData(request, meta_data_pk):
    try:
        if request.method == "GET":
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)

            type = request.GET["type"]
            type = remo_html_from_string(type)

            meta_data_obj = CobrowsingSessionMetaData.objects.get(
                pk=int(meta_data_pk))
            path_to_file = None

            if type == "html":
                path_to_file = meta_data_obj.content
            elif type == "img":
                path_to_file = meta_data_obj.content
                logger.info("export as image", extra={
                            'AppName': 'EasyAssistSalesforce'})

                # try:
                #     str_time = str(int(time.time()))
                #     path_to_file = "files/client-screens/" + str(meta_data_obj.cobrowse_io.session_id) + "-" + str_time + ".jpg"
                #     imgkit.from_file(meta_data_obj.content[1:], path_to_file, options={"xvfb": ""})
                #     path_to_file = '/' + path_to_file
                #     logger.info("HTML to Image converted successfully.")
                # except Exception:
                #     logger.error("ExportCapturedData:")

            if path_to_file == None:
                return HttpResponse(status=500)

            filename = path_to_file.split("/")[-1]

            mime_type, _ = mimetypes.guess_type(path_to_file)

            if os.path.exists(path_to_file):
                with open(path_to_file, 'rb') as fh:
                    response = HttpResponse(
                        fh.read(), status=200, content_type=mime_type)
                    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(
                        str(filename))
                    response['X-Sendfile'] = smart_str(path_to_file)
                    # response['X-Accel-Redirect'] = path_to_file
                    return response
        else:
            return HttpResponse(500)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Export Captured Data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse(500)


class GetCobrowsingAgentCommentsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = data["id"]
            id = remo_html_from_string(id)
            page = data["page"]

            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            cobrowse_agent_comments = cobrowse_io.get_cobrowsing_session_closing_comments()

            paginator = Paginator(cobrowse_agent_comments, 4)
            no_pages = paginator.num_pages

            is_last_page = False
            if int(page) >= int(no_pages):
                is_last_page = True

            try:
                cobrowse_agent_comments = paginator.page(page)
            except PageNotAnInteger:
                cobrowse_agent_comments = paginator.page(1)
            except EmptyPage:
                cobrowse_agent_comments = paginator.page(
                    paginator.num_pages)

            agent_comments_list = []
            for cobrowse_agent_comment in cobrowse_agent_comments:

                est = pytz.timezone(settings.TIME_ZONE)
                datetime = cobrowse_agent_comment.datetime.astimezone(
                    est).strftime("%b %d %Y %I:%M %p")

                agent_comments_list.append({
                    "id": cobrowse_agent_comment.pk,
                    "agent": cobrowse_agent_comment.agent.user.username,
                    "comments": cobrowse_agent_comment.agent_comments,
                    "datetime": datetime
                })

            response["status"] = 200
            response["message"] = "success"
            response["is_last_page"] = is_last_page
            response["agent_comments_list"] = agent_comments_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCobrowsingAgentCommentsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCobrowsingAgentComments = GetCobrowsingAgentCommentsAPI.as_view()


class GetSystemAuditTrailBasicActivityAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = data["id"]
            id = remo_html_from_string(id)
            page = data["page"]

            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            basic_activity_audit_trail_objs = cobrowse_io.get_basic_activity_audit_trail_objs()

            paginator = Paginator(basic_activity_audit_trail_objs, 4)
            no_pages = paginator.num_pages

            is_last_page = False
            if int(page) >= int(no_pages):
                is_last_page = True

            try:
                basic_activity_audit_trail_objs = paginator.page(page)
            except PageNotAnInteger:
                basic_activity_audit_trail_objs = paginator.page(1)
            except EmptyPage:
                basic_activity_audit_trail_objs = paginator.page(
                    paginator.num_pages)

            basic_activity_audit_trail_obj_list = []
            for basic_activity_audit_trail_obj in basic_activity_audit_trail_objs:

                est = pytz.timezone(settings.TIME_ZONE)
                datetime = basic_activity_audit_trail_obj.datetime.astimezone(
                    est).strftime("%b %d %Y %I:%M %p")

                basic_activity_audit_trail_obj_list.append({
                    "datetime": datetime,
                    "description": basic_activity_audit_trail_obj.description,
                })

            response["status"] = 200
            response["message"] = "success"
            response["is_last_page"] = is_last_page
            response[
                "basic_activity_audit_trail_obj_list"] = basic_activity_audit_trail_obj_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetSystemAuditTrailBasicActivityAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetSystemAuditTrailBasicActivity = GetSystemAuditTrailBasicActivityAPI.as_view()


class SaveCobrowsingChatAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if cobrowse_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            sender = strip_html_tags(data["sender"])
            sender = remo_html_from_string(sender)
            message = strip_html_tags(data["message"])
            message = remo_html_from_string(message)
            attachment = strip_html_tags(data["attachment"])
            attachment = remo_html_from_string(attachment)
            attachment_file_name = strip_html_tags(
                data["attachment_file_name"])
            attachment_file_name = remo_html_from_string(attachment_file_name)

            if sender == "client":
                cobrowse_agent = None

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            if attachment == "None":
                attachment = None

            if attachment_file_name == "None":
                attachment_file_name = None

            CobrowseChatHistory.objects.create(cobrowse_io=cobrowse_io,
                                               sender=cobrowse_agent,
                                               message=message,
                                               attachment=attachment,
                                               attachment_file_name=attachment_file_name)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowsingChatAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowsingChat = SaveCobrowsingChatAPI.as_view()


class GetCobrowsingChatHistoryAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if cobrowse_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            cobrowsing_chat_history_objs = cobrowse_io.get_cobrowsing_chat_history()

            agent_name = cobrowse_io.agent.user.first_name
            if agent_name is None or agent_name.strip() == "":
                agent_name = cobrowse_io.agent.user.username

            if cobrowse_io.access_token.enable_agent_connect_message:
                agent_connect_message = cobrowse_io.access_token.agent_connect_message.replace(
                    'agent_name', agent_name)
            else:
                agent_connect_message = ""

            chat_history = []
            for cobrowsing_chat_history_obj in cobrowsing_chat_history_objs:

                est = pytz.timezone(settings.TIME_ZONE)
                datetime = cobrowsing_chat_history_obj.datetime.astimezone(
                    est).strftime("%d %b %Y %I:%M %p")

                sender = "client"
                if cobrowsing_chat_history_obj.sender != None:
                    sender = cobrowsing_chat_history_obj.sender.name()

                chat_history.append({
                    "sender": sender,
                    "message": cobrowsing_chat_history_obj.message,
                    "attachment": cobrowsing_chat_history_obj.attachment,
                    "attachment_file_name": cobrowsing_chat_history_obj.attachment_file_name,
                    "datetime": datetime
                })

            response["status"] = 200
            response["message"] = "success"
            response["chat_history"] = chat_history
            response["agent_connect_message"] = agent_connect_message
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCobrowsingChatHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCobrowsingChatHistory = GetCobrowsingChatHistoryAPI.as_view()


class SaveDocumentAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            filename = strip_html_tags(data["filename"])
            filename = remo_html_from_string(filename)
            # session_id = strip_html_tags(data["session_id"])
            # session_id = remo_html_from_string(session_id)

            check_file_ext = filename.split(".")
            if len(check_file_ext) != 2:
                response["status"] = 302
            else:
                file_extention = filename.replace(" ", "").split(".")[-1]
                file_extention = file_extention.lower()

                if file_extention not in ["png", "jpg", "jpeg", "pdf", "doc", "docx"]:
                    response["status"] = 302
                else:
                    base64_data = strip_html_tags(data["base64_file"])

                    is_public = False
                    if "is_public" in data and data["is_public"]:
                        is_public = True

                    filename = generate_random_key(10) + "_" + filename

                    if is_public == False:
                        if not os.path.exists('secured_files/EasyAssistSalesforceApp/attachments'):
                            os.makedirs(
                                'secured_files/EasyAssistSalesforceApp/attachments')

                        file_path = "secured_files/EasyAssistSalesforceApp/attachments/" + filename
                    else:
                        if not os.path.exists('files/attachments'):
                            os.makedirs('files/attachments')

                        file_path = "files/attachments/" + filename

                    fh = open(file_path, "wb")
                    fh.write(base64.b64decode(base64_data))
                    fh.close()

                    file_path = "/" + file_path

                    file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                        file_path=file_path, is_public=is_public)

                    response["status"] = 200
                    response["message"] = "success"

                    if is_public:
                        response["file_path"] = file_path
                    else:
                        response["file_path"] = "/easy-assist-salesforce/download-file/" + \
                            str(file_access_management_obj.key) + "/"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveDocumentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveDocument = SaveDocumentAPI.as_view()


def FileAccess(request, file_key):
    try:
        active_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if active_agent:
            return file_download(file_key, CobrowsingFileAccessManagement, SupportDocument)
        else:
            if "session_id" in request.GET:
                session_id = request.GET["session_id"]
                cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
                if cobrowse_io.is_archived == True:
                    return HttpResponse(status=404)
                else:
                    return file_download(file_key, CobrowsingFileAccessManagement, SupportDocument)

            elif "vctoken" in request.GET:

                vc_session_obj = CobrowseVideoConferencing.objects.get(
                    meeting_id=request.GET["vctoken"])

                if vc_session_obj.is_cobrowsing_meeting:
                    cobrowse_io_obj = CobrowseIO.objects.get(
                        session_id=request.GET["token"])
                    if not cobrowse_io_obj.is_archived:
                        return file_download(file_key, CobrowsingFileAccessManagement, SupportDocument)
                else:
                    status = check_cogno_meet_status(
                        vc_session_obj)
                    vc_session_obj = CobrowseVideoConferencing.objects.get(
                        meeting_id=request.GET["vctoken"])
                    logger.info("VC : %s : %s", status, vc_session_obj.is_expired, extra={
                        'AppName': 'EasyAssistSalesforce'})

                    if not vc_session_obj.is_expired:
                        return file_download(file_key, CobrowsingFileAccessManagement, SupportDocument)

            return HttpResponse(status=404)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error FileAccess %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse(status=404)
        # if file_access_management_obj.is_public:
    #     return response
    # else:
    #     if request.user.is_authenticated:
    #         return response
    #     else:
    #         try:
    #             eacSession = request.COOKIES["eacSession"]
    #             eacSession = base64.b64decode(eacSession).decode("utf-8")
    #             eacSession = json.loads(eacSession)
    #             easyassist_session_id = eacSession["easyassist_session_id"]
    #             if eacSession["easyassist_cobrowsing_allowed"] == "true" and CobrowseIO.objects.filter(session_id=easyassist_session_id, is_archived=False, is_active=True).count() > 0:
    #                 return response
    #         except Exception:
    #             pass


def CustomerSupportDocuments(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        support_document_objs = SupportDocument.objects.filter(
            agent=cobrowse_agent, is_deleted=False).order_by("-added_on")

        if cobrowse_agent.role not in ["admin", "supervisor"]:
            return HttpResponse(status=401)

        return render(request, "EasyAssistSalesforceApp/customer_support_documents.html", {
            "salesforce_token": quote_plus(request.GET["salesforce_token"]),
            "cobrowse_agent": cobrowse_agent,
            "support_document_objs": support_document_objs
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CustomerSupportDocuments %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return HttpResponse("Invalid Access")


class UploadCustomerSupportDocumentsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if cobrowse_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            file_upload_success = []
            file_upload_fail = []
            for file_data_obj in data:
                try:
                    filename = "null"
                    filename = strip_html_tags(file_data_obj["filename"])
                    filename = remo_html_from_string(filename)
                    check_file_ext = filename.split(".")
                    if len(check_file_ext) != 2:
                        response["status"] = 302
                        break
                    else:
                        base64_data = strip_html_tags(
                            file_data_obj["base64_file"])
                        original_file_name = filename

                        filename = generate_random_key(
                            10) + "_" + filename.replace(" ", "")

                        if not os.path.exists('secured_files/EasyAssistSalesforceApp/customer-support'):
                            os.makedirs(
                                'secured_files/EasyAssistSalesforceApp/customer-support')

                        file_path = "secured_files/EasyAssistSalesforceApp/customer-support/" + filename

                        file_extention = file_path.split(".")[-1]
                        file_extention = file_extention.lower()

                        if file_extention in ["png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"]:
                            media_type = "image"
                        elif file_extention in ["ppt", "pptx", "pptm"]:
                            media_type = "ppt"
                        elif file_extention in ["doc", "docx", "odt", "rtf", "txt"]:
                            media_type = "docs"
                        elif file_extention in ["pdf"]:
                            media_type = "pdf"
                        elif file_extention in ["xls", "xlsx", "xlsm", "xlt", "xltm"]:
                            media_type = "excel"
                        elif file_extention in ["avi", "flv", "wmv", "mov", "mp4"]:
                            media_type = "video"
                        else:
                            media_type = None

                        if media_type == None or check_malicious_file_from_filename(filename):
                            response["status"] = 300
                            file_upload_fail.append(original_file_name)
                        else:
                            fh = open(file_path, "wb")
                            fh.write(base64.b64decode(base64_data))
                            fh.close()

                            file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                                file_path="/" + file_path, is_public=True)
                            file_access_management_key = file_access_management_obj.key
                            SupportDocument.objects.create(
                                file_path="/" + file_path, file_name=original_file_name, file_type=media_type, agent=cobrowse_agent, file_access_management_key=file_access_management_key)
                            file_upload_success.append(original_file_name)

                            description = "Support document file named '" + original_file_name + "' added."
                            save_audit_trail(cobrowse_agent, COBROWSING_UPDATEUSER_ACTION,
                                             description, CobrowsingAuditTrail)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error Fileupload_customer_support_loop %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
                    file_upload_fail.append(original_file_name)

                response["status"] = 200
                response["message"] = "success"
                response["file_upload_fail"] = file_upload_fail
                response["file_upload_success"] = file_upload_success
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadCustomerSupportDocumentsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadCustomerSupportDocuments = UploadCustomerSupportDocumentsAPI.as_view()


class UpdateSupportDocumentDetailAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if cobrowse_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            customer_support_document_update_dict = json.loads(data)

            for support_document_key in customer_support_document_update_dict.keys():
                user_input_obj = customer_support_document_update_dict[
                    support_document_key]
                support_document_obj = SupportDocument.objects.get(
                    pk=support_document_key)
                if "is_usable" in user_input_obj:
                    support_document_obj.is_usable = user_input_obj[
                        "is_usable"]
                if "is_deleted" in user_input_obj:
                    support_document_obj.is_deleted = user_input_obj[
                        "is_deleted"]
                if "file_name" in user_input_obj:
                    support_document_obj.file_name = user_input_obj[
                        "file_name"]
                support_document_obj.save()
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateSupportDocumentDetailAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateSupportDocumentDetail = UpdateSupportDocumentDetailAPI.as_view()


class SetNotificationForAgentAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            if "agent_id_list" in data:
                agent_id_list = data["agent_id_list"]
                for agent_id in agent_id_list:
                    cobrowse_agent = CobrowseAgent.objects.get(
                        pk=int(agent_id))

                    notification_message = "Hi, " + cobrowse_agent.user.username + \
                        "! A customer is waiting for you to connect on Cogno Cobrowse."
                    NotificationManagement.objects.create(show_notification=True,
                                                          agent=cobrowse_agent,
                                                          notification_message=notification_message,
                                                          cobrowse_io=cobrowse_io)

                    if "support_request_notify" not in data:
                        cobrowse_io.agent_notified_count += 1
                        cobrowse_io.save()
            else:
                agent = cobrowse_io.agent

                notification_message = "Hi, " + agent.user.username + \
                    "! A customer is waiting for you to connect on Cogno Cobrowse."
                NotificationManagement.objects.create(show_notification=True,
                                                      agent=agent,
                                                      notification_message=notification_message,
                                                      cobrowse_io=cobrowse_io)
                cobrowse_io.agent_notified_count += 1
                cobrowse_io.save()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SetNotificationForAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SetNotificationForAgent = SetNotificationForAgentAPI.as_view()


class AddNewObfuscatedFieldAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cobrowse_access_token = active_agent.get_access_token_obj()

            if active_agent.role == "admin":
                key = strip_html_tags(data["field_key"])
                key = remo_html_from_string(key)
                value = strip_html_tags(data["field_value"])
                value = remo_html_from_string(value)
                masking_type = strip_html_tags(data["masking_type"])

                if cobrowse_access_token.obfuscated_fields.filter(key=key, value=value).count() > 0:
                    response["status"] = 301
                    response[
                        "message"] = "Matching cobrowse obfuscated field already exists"

                else:
                    cobrowse_obfuscated_field = CobrowseObfuscatedField.objects.create(key=key,
                                                                                       value=value,
                                                                                       masking_type=masking_type)

                    cobrowse_access_token.obfuscated_fields.add(
                        cobrowse_obfuscated_field)
                    cobrowse_access_token.save()

                    description = key + "=" + value + " masking field added."
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)
                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddNewObfuscatedFieldAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddNewObfuscatedField = AddNewObfuscatedFieldAPI.as_view()


class DeleteObfuscatedFieldsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            obfuscated_field_id_list = data["obfuscated_field_id_list"]

            if active_agent.role == "admin":

                for obfuscated_field_id in obfuscated_field_id_list:
                    field = CobrowseObfuscatedField.objects.get(
                        pk=int(obfuscated_field_id))
                    field.delete()

                    description = field.key + "=" + field.value + " masking field deleted."
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteObfuscatedFieldsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteObfuscatedFields = DeleteObfuscatedFieldsAPI.as_view()


class AddNewLeadHTMLFieldAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cobrowse_access_token = active_agent.get_access_token_obj()

            if active_agent.role == "admin":
                tag = strip_html_tags(data["tag"])
                tag_label = strip_html_tags(data["tag_label"])
                tag_label = remo_html_from_string(tag_label)
                tag_key = strip_html_tags(data["tag_key"])
                tag_key = remo_html_from_string(tag_key)
                tag_value = strip_html_tags(data["tag_value"])
                tag_value = remo_html_from_string(tag_value)
                tag_type = strip_html_tags(data["tag_type"])

                if cobrowse_access_token.search_fields.filter(tag_key=tag_key, tag_value=tag_value).count() > 0:
                    response["status"] = 301
                    response[
                        "message"] = "Matching cobrowse lead html field already exists"

                else:
                    cobrowse_lead_html_field = CobrowseLeadHTMLField.objects.create(tag=tag,
                                                                                    tag_label=tag_label,
                                                                                    tag_key=tag_key,
                                                                                    tag_value=tag_value,
                                                                                    tag_type=tag_type)

                    cobrowse_access_token.search_fields.add(
                        cobrowse_lead_html_field)
                    cobrowse_access_token.save()

                    description = tag_key + "=" + tag_value + " search tag field added."
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)
                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddNewLeadHTMLFieldAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddNewLeadHTMLField = AddNewLeadHTMLFieldAPI.as_view()


class DeleteLeadHTMLFieldsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            search_tag_field_id_list = data["search_tag_field_id_list"]

            if active_agent.role == "admin":

                for search_tag_field_id in search_tag_field_id_list:
                    field = CobrowseLeadHTMLField.objects.get(
                        pk=int(search_tag_field_id))
                    field.delete()

                    description = field.tag_key + "=" + field.tag_value + " search tag field deleted."
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteLeadHTMLFieldsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteLeadHTMLFields = DeleteLeadHTMLFieldsAPI.as_view()


class AddNewAutoFetchFieldAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cobrowse_access_token = active_agent.get_access_token_obj()

            if active_agent.role == "admin":
                fetch_field_key = strip_html_tags(data["fetch_field_key"])
                fetch_field_key = remo_html_from_string(fetch_field_key)
                fetch_field_value = strip_html_tags(data["fetch_field_value"])
                fetch_field_value = remo_html_from_string(fetch_field_value)
                modal_field_key = strip_html_tags(data["modal_field_key"])
                modal_field_key = remo_html_from_string(modal_field_key)
                modal_field_value = strip_html_tags(data["modal_field_value"])
                modal_field_value = remo_html_from_string(modal_field_value)

                if cobrowse_access_token.auto_fetch_fields.filter(fetch_field_key=fetch_field_key, fetch_field_value=fetch_field_value).count() > 0:
                    response["status"] = 301
                    response[
                        "message"] = "Matching cobrowse lead html field already exists"

                else:
                    cobrowse_auto_fetch_field = CobrowseAutoFetchField.objects.create(fetch_field_key=fetch_field_key,
                                                                                      fetch_field_value=fetch_field_value,
                                                                                      modal_field_key=modal_field_key,
                                                                                      modal_field_value=modal_field_value)

                    cobrowse_access_token.auto_fetch_fields.add(
                        cobrowse_auto_fetch_field)
                    cobrowse_access_token.save()

                    description = fetch_field_key + "=" + \
                        fetch_field_value + " auto fetch field added."
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)
                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddNewAutoFetchFieldAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddNewAutoFetchField = AddNewAutoFetchFieldAPI.as_view()


class DeleteAutoFetchFieldsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            auto_fetch_field_id_list = data["auto_fetch_field_id_list"]

            if active_agent.role == "admin":

                for auto_fetch_field_id in auto_fetch_field_id_list:
                    field = CobrowseAutoFetchField.objects.get(
                        pk=int(auto_fetch_field_id))
                    field.delete()

                    description = field.fetch_field_key + "=" + \
                        field.fetch_field_value + " auto fetch field deleted."
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteAutoFetchFieldsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteAutoFetchFields = DeleteAutoFetchFieldsAPI.as_view()


class SaveCobrowseAgentAdvancedDetailsAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent.supported_language.clear()
            active_agent.product_category.clear()

            selected_language_pk_list = data["selected_language_pk_list"]
            selected_product_category_list = data[
                "selected_product_category_list"]

            for product_category in selected_product_category_list:
                active_agent.product_category.add(
                    ProductCategory.objects.get(pk=int(product_category)))

            for language_pk in selected_language_pk_list:
                active_agent.supported_language.add(
                    LanguageSupport.objects.get(pk=int(language_pk)))

            active_agent.save()
            save_audit_trail(active_agent, COBROWSING_CHANGESETTINGS_ACTION,
                             "Advanced Settings has been changed", CobrowsingAuditTrail)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowseAgentAdvancedDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowseAgentAdvancedDetails = SaveCobrowseAgentAdvancedDetailsAPI.as_view()


class GetLeadStatusAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cobrowse_io_obj = CobrowseIO.objects.filter(
                session_id=data["session_id"]).order_by('-request_datetime').first()

            response["cobrowsing_start_datetime"] = str(
                cobrowse_io_obj.cobrowsing_start_datetime)
            response["is_active_timer"] = cobrowse_io_obj.is_active_timer()
            response["is_active"] = cobrowse_io_obj.is_active
            response["total_time_spent"] = cobrowse_io_obj.total_time_spent()
            response["share_client_session"] = cobrowse_io_obj.share_client_session
            response["allow_agent_cobrowse"] = cobrowse_io_obj.allow_agent_cobrowse
            response["allow_video_meeting"] = cobrowse_io_obj.access_token.allow_video_meeting_only
            response["status"] = 200
            response["message"] = "success"
            response["pk"] = str(cobrowse_io_obj.pk)
            response["mobile_number"] = str(cobrowse_io_obj.mobile_number)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetLeadStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetLeadStatus = GetLeadStatusAPI.as_view()


class SaveCobrowsingScreenRecordedDataAPI(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        response = {}

        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)

            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)
            # active_agent = get_active_agent_obj(
            #     request, User, CobrowseAgent)

            uploaded_file = data["uploaded_data"]
            session_id = data["session_id"]
            session_id = strip_html_tags(data["session_id"])
            screen_recorder_on = data["screen_recorder_on"]
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            screen_recording_obj = None

            try:
                screen_recording_obj = CobrowseScreenRecordingAuditTrail.objects.filter(
                    cobrowse_io=cobrowse_io, agent=active_agent, is_recording_ended=False)[0]
            except Exception:
                logger.info("Creating new CobrowseScreenRecordingAuditTrail.", extra={
                            'AppName': 'EasyAssist'})
                screen_recording_obj = CobrowseScreenRecordingAuditTrail.objects.create(
                    cobrowse_io=cobrowse_io, agent=active_agent, is_recording_ended=False)

            try:
                file_access_management_obj = CobrowsingFileAccessManagement.objects.get(
                    file_path=screen_recording_obj.key, is_public=False)
                file_path = file_access_management_obj.file_path[1:]
            except Exception:
                filename = session_id + "_" + str(CobrowseScreenRecordingAuditTrail.objects.filter(
                    cobrowse_io=cobrowse_io, agent=active_agent).count()) + ".webm"
                file_path = "secured_files/EasyAssistSalesforceApp/recordings/" + filename
                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path="/" + file_path, is_public=False)

            media_file = open(file_path, "ab+")
            media_file.write(uploaded_file.read())
            media_file.close()

            screen_recording_obj.recorded_file = file_access_management_obj.key
            screen_recording_obj.is_recording_ended = False if screen_recorder_on == "true" else True
            screen_recording_obj.recording_ended = datetime.datetime.now()
            screen_recording_obj.save()

            response["status"] = 200
            response["src"] = "/" + file_path
            logger.info(response, extra={'AppName': 'EasyAssistSalesforceApp'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveCobrowsingScreenRecordedDataAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status"] = 500
            response["src"] = "error"
        return Response(data=response)


SaveCobrowsingScreenRecordedData = SaveCobrowsingScreenRecordedDataAPI.as_view()


class RequestCobrowsingMeetingAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            cobrowse_io.agent_meeting_request_status = True
            cobrowse_io.allow_agent_meeting = None
            cobrowse_io.meeting_start_datetime = None
            cobrowse_io.save()

            category = "session_details"
            description = "Request for meeting sent by " + \
                str(active_agent.user.username)
            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, active_agent)

            cobrowse_agent = active_agent
            try:
                CobrowseVideoConferencing.objects.get(meeting_id=session_id)
            except Exception:
                CobrowseVideoConferencing.objects.create(meeting_id=session_id, agent=cobrowse_agent, meeting_description="Cobrowsing Meeting",
                                                         meeting_start_date=timezone.now(), meeting_start_time=timezone.localtime(timezone.now()), full_name=cobrowse_io.full_name, mobile_number=cobrowse_io.mobile_number, is_cobrowsing_meeting=True)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RequestCobrowsingMeetingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


RequestCobrowsingMeeting = RequestCobrowsingMeetingAPI.as_view()


class CheckMeetingStatusAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            is_meeting_allowed = False
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            if cobrowse_io.allow_agent_meeting == 'None' or cobrowse_io.allow_agent_meeting == None:
                response["is_meeting_allowed"] = is_meeting_allowed
                response["is_client_answer"] = False
                response["status"] = 301
                response["message"] = "success"
            elif cobrowse_io.allow_agent_meeting == 'true':
                is_meeting_allowed = True
                response["is_meeting_allowed"] = is_meeting_allowed
                response["is_client_answer"] = True
                response["status"] = 200
                response["message"] = "success"
            else:
                is_meeting_allowed = False
                response["is_meeting_allowed"] = is_meeting_allowed
                response["is_client_answer"] = True
                response["status"] = 200
                response["message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckMeetingStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckMeetingStatus = CheckMeetingStatusAPI.as_view()


def EasyAssistPageShot(request, pageshot_id):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        active_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if active_agent == None:
            return HttpResponse(status=401)

        cobrowse_meta_obj = CobrowsingSessionMetaData.objects.get(
            pk=int(pageshot_id))
        path_to_file = cobrowse_meta_obj.content

        response = HttpResponse(
            status=200, content_type='application/force-download')
        response[
            'Content-Disposition'] = 'attachment; filename=%s' % str(uuid.uuid4())
        response['X-Sendfile'] = smart_str(path_to_file)
        response['X-Accel-Redirect'] = path_to_file

        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error EasyAssistPageShot %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse("Invalid Request")


class GenerateDropLinkAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            client_page_link = data["client_page_link"]
            client_page_link = remo_html_from_string(client_page_link)
            customer_name = data["customer_name"]
            customer_name = remo_html_from_string(customer_name)
            customer_name = remo_special_tag_from_string(customer_name)
            customer_mobile_number = data["customer_mobile_number"]
            customer_mobile_number = remo_html_from_string(
                customer_mobile_number)
            customer_mobile_number = remo_special_tag_from_string(
                customer_mobile_number)
            customer_email_id = data["customer_email_id"]
            customer_email_id = remo_html_from_string(customer_email_id)

            cobrowse_drop_link_obj = CobrowseDropLink.objects.create(
                client_page_link=client_page_link,
                agent=active_agent,
                customer_name=customer_name)

            generated_link = client_page_link
            first_index = client_page_link.find("?")
            if first_index < 0:
                generated_link += "?eadKey=" + str(cobrowse_drop_link_obj.key)
            else:
                generated_link += "&eadKey=" + str(cobrowse_drop_link_obj.key)

            shorten_tiny_url_obj = UrlShortenTinyurl()
            generated_link = shorten_tiny_url_obj.shorten(generated_link)

            if customer_email_id != "":
                thread = threading.Thread(target=send_drop_link_over_email, args=(
                    customer_email_id, customer_name, str(active_agent.user.username), client_page_link, generated_link, ), daemon=True)
                thread.start()

            # customer_mobile_number = hashlib.md5(
            #     customer_mobile_number.encode()).hexdigest()
            customer_email_id = hashlib.md5(
                customer_email_id.encode()).hexdigest()
            cobrowse_drop_link_obj.customer_mobile = customer_mobile_number
            cobrowse_drop_link_obj.customer_email = customer_email_id
            cobrowse_drop_link_obj.generated_link = generated_link
            cobrowse_drop_link_obj.generate_datetime = timezone.now()
            cobrowse_drop_link_obj.save()

            response["status"] = 200
            response["generated_link"] = str(generated_link)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GenerateDropLinkAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GenerateDropLink = GenerateDropLinkAPI.as_view()


def CognoMeetAnalyticsDashboard(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        DEFAULT_ANALYTICS_START_DATETIME = (
            datetime.datetime.today() - datetime.timedelta(7)).date()

        DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

        agent_objs = []
        if cobrowse_agent.role == "agent":
            agent_objs = [cobrowse_agent]
        elif cobrowse_agent.role == "supervisor":
            agent_objs = list(cobrowse_agent.agents.all())
        else:
            agent_objs = get_list_agents_under_admin(
                cobrowse_agent, is_active=None)

        if cobrowse_agent.show_static_analytics:
            return render(request, "EasyAssistSalesforceApp/analytics_cogno_meet_static.html", {
                "salesforce_token": quote_plus(request.GET["salesforce_token"]),
                "agent_objs": agent_objs,
                "cobrowse_agent": cobrowse_agent,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
            })
        else:
            return render(request, "EasyAssistSalesforceApp/analytics_cogno_meet.html", {
                "salesforce_token": quote_plus(request.GET["salesforce_token"]),
                "agent_objs": agent_objs,
                "cobrowse_agent": cobrowse_agent,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
            })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CognoMeetAnalyticsDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return HttpResponse("Invalid Access")


class SendSalesforceNotificationAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside SendSalesforceNotification",
                        extra={'AppName': 'EasyAssistSalesforce'})
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
            salesforce_agent = SalesforceAgent.objects.filter(
                email=active_agent.user.username)[0]
            admin_account = get_admin_from_active_agent(
                active_agent, CobrowseAgent)
            salesforce_notification_manager = SalesforceNotificationManager.objects.filter(
                access_token__agent=admin_account)[0]

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            notification_message = data["notification_message"]
            notification_message = remo_html_from_string(notification_message)

            auth_url = "https://login.salesforce.com/services/oauth2/token"
            auth_body = {
                'grant_type': (None, 'password'),
                'client_id': (None, salesforce_notification_manager.client_id),
                'client_secret': (None, salesforce_notification_manager.client_secret),
                'username': (None, salesforce_notification_manager.username),
                'password': (None, salesforce_notification_manager.password),
            }
            auth_response = requests.post(auth_url, files=auth_body)
            auth_response = json.loads(auth_response.text)
            logger.info(auth_response,
                        extra={'AppName': 'EasyAssistSalesforce'})
            access_token = auth_response["access_token"]
            notification_list_url = "https://ap24.salesforce.com/services/data/v46.0/tooling/query/?q=SELECT+id,CustomNotifTypeName+from+CustomNotificationType"
            header = {
                "Authorization": "Bearer " + access_token
            }
            notification_list_response = requests.get(
                notification_list_url, headers=header)
            notification_list_response = json.loads(
                notification_list_response.text)
            logger.info(notification_list_response,
                        extra={'AppName': 'EasyAssistSalesforce'})
            custom_notification_id = notification_list_response["records"][0]["Id"]
            send_notification_url = "https://ap24.salesforce.com/services/data/v46.0/actions/standard/customNotificationAction"
            send_notification_body = {
                "inputs": [
                    {
                        "customNotifTypeId": custom_notification_id,
                        "recipientIds": [
                            salesforce_agent.user_id
                        ],
                        "title": "Cogno Cobrowse",
                        "body": notification_message,
                        "targetPageRef": "{type: 'standard__navItemPage',attributes: {apiName: '" + salesforce_agent.web_tab_name + "'} }"
                    }
                ]
            }
            send_notification_response = requests.post(
                send_notification_url, json=send_notification_body, headers=header)
            send_notification_response = json.loads(
                send_notification_response.text)
            logger.info(send_notification_response,
                        extra={'AppName': 'EasyAssistSalesforce'})

            if send_notification_response[0]["isSuccess"] == True:
                response["message"] = send_notification_response[0]["outputValues"]["SuccessMessage"]
                response["redirect_url"] = auth_response["instance_url"] + \
                    "/lightning/n/" + salesforce_agent.web_tab_name
                response["status"] = 200
                logger.info("Successfully exited from SendSalesforceNotification",
                            extra={'AppName': 'EasyAssistSalesforce'})
            else:
                logger.error(send_notification_response, extra={
                             'AppName': 'EasyAssistSalesforce'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SendSalesforceNotificationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SendSalesforceNotification = SendSalesforceNotificationAPI.as_view()


def CobrowseForms(request):

    try:
        logger.info("Inside CobrowseForms", extra={
                    'AppName': 'EasyAssistSalesforce'})
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        if cobrowse_agent.role not in ["admin", "supervisor"]:
            return HttpResponse(status=401)

        agent_list = get_list_agents_under_admin(
            cobrowse_agent, is_active=None)
        supervisor_list = get_list_supervisor_under_admin(
            cobrowse_agent, is_active=None)
        agent_list += supervisor_list

        agent_objs = []
        for agent in agent_list:
            if agent.pk != cobrowse_agent.pk:
                agent_objs.append(agent)

        cogno_vid_forms = CobrowseVideoConferencingForm.objects.filter(
            agents=cobrowse_agent, is_deleted=False)

        product_categories = cobrowse_agent.product_category.all()

        return render(request, "EasyAssistSalesforceApp/cobrowse_forms.html", {
            "salesforce_token": quote_plus(request.GET["salesforce_token"]),
            "cobrowse_agent": cobrowse_agent,
            "cogno_vid_forms": cogno_vid_forms,
            "agent_objs": agent_objs,
            "product_categories": product_categories
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowseForms %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return HttpResponse("Invalid Access")


def CreateCobrowseForms(request):

    try:
        logger.info("Inside CreateCobrowseForms", extra={
                    'AppName': 'EasyAssistSalesforce'})
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)

        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        agent_objs = get_list_agents_under_admin(
            cobrowse_agent, is_active=None)
        product_categories = cobrowse_agent.product_category.all()

        return render(request, "EasyAssistSalesforceApp/create_cobrowse_form.html", {
            "salesforce_token": quote_plus(request.GET["salesforce_token"]),
            "cobrowse_agent": cobrowse_agent,
            "agent_objs": agent_objs,
            "product_categories": product_categories,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CreateCobrowseForms %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return HttpResponse("Invalid Access")


class AddNewCobrowseFormAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            logger.info("Inside AddNewCobrowseFormAPI", extra={
                        'AppName': 'EasyAssistSalesforce'})
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)

            cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if cobrowse_agent == None:
                return HttpResponse(status=401)

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None)

            product_categories = data["product_categories"]
            form_name = data["form_name"]
            form_name = remo_html_from_string(form_name)
            form_name = remo_special_tag_from_string(form_name)
            form_data = data["form_data"]

            cobrowse_form_obj = CobrowseVideoConferencingForm.objects.create(
                form_name=form_name)

            if product_categories == "None":
                cobrowse_form_obj.agents = agents
                cobrowse_form_obj.save()
            else:
                for agent in agents:
                    if agent.product_category.filter(pk__in=product_categories):
                        cobrowse_form_obj.agents.add(agent)
                cobrowse_form_obj.save()

            for category in form_data:
                try:
                    category_name = category["category_name"]
                    category_name = remo_html_from_string(category_name)
                    category_name = remo_special_tag_from_string(category_name)

                    cobrowse_form_category_obj = CobrowseVideoconferencingFormCategory.objects.create(
                        form=cobrowse_form_obj, title=category_name)

                    for question in category["questions"]:
                        try:
                            question_type = question["question_type"]
                            question_type = remo_html_from_string(
                                question_type)
                            question_type = remo_special_tag_from_string(
                                question_type)

                            question_label = question["question_label"]
                            question_label = remo_html_from_string(
                                question_label)
                            question_label = remo_special_tag_from_string(
                                question_label)

                            question_choices = question["question_choices"]
                            is_mandatory = question["is_mandatory"]

                            filtered_question_choices = []
                            for question_choice in question_choices:
                                choice = remo_html_from_string(question_choice)
                                choice = remo_special_tag_from_string(choice)
                                filtered_question_choices.append(choice)

                            CobrowseVideoConferencingFormElement.objects.create(
                                form_category=cobrowse_form_category_obj,
                                element_type=question_type,
                                element_label=question_label,
                                element_choices=json.dumps(
                                    filtered_question_choices),
                                is_mandatory=is_mandatory)
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Error Form Question cannot be created %s at %s",
                                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error Form Category cannot be created %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

            response['status'] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddNewCobrowseFormAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddNewCobrowseForm = AddNewCobrowseFormAPI.as_view()


def EditCobrowseForms(request, form_id):

    try:
        logger.info("Inside EditCobrowseForms", extra={
                    'AppName': 'EasyAssistSalesforce'})
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)

        cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
        if cobrowse_agent == None:
            return HttpResponse(status=401)

        try:
            product_categories = cobrowse_agent.product_category.all()

            cobrowse_form_obj = CobrowseVideoConferencingForm.objects.get(
                pk=form_id, is_deleted=False)

            cobrowse_form_category_objs = CobrowseVideoconferencingFormCategory.objects.filter(
                form=cobrowse_form_obj, is_deleted=False).order_by('pk')

            cobrowse_form_elements = CobrowseVideoConferencingFormElement.objects.filter(
                form_category__in=cobrowse_form_category_objs, is_deleted=False).order_by('pk')

            return render(request, "EasyAssistSalesforceApp/edit_cobrowse_form.html", {
                "salesforce_token": quote_plus(request.GET["salesforce_token"]),
                "cobrowse_agent": cobrowse_agent,
                "cobrowse_form_obj": cobrowse_form_obj,
                'cobrowse_form_categories': cobrowse_form_category_objs,
                "cobrowse_form_elements": cobrowse_form_elements,
                "product_categories": product_categories,
            })

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EditCobrowseForms %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

            return HttpResponse("Form does not exist")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error EditCobrowseForms %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return HttpResponse("Invalid Access")


class SaveCobrowseFormAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            logger.info("Inside SaveCobrowseFormAPI", extra={
                        'AppName': 'EasyAssistSalesforce'})
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            # user = User.objects.get(username=request.user.username)
            # cobrowse_agent = CobrowseAgent.objects.get(
            #     user=user, is_account_active=True)

            # agents = get_list_agents_under_admin(
            #     cobrowse_agent, is_active=None)

            # product_categories = data["product_categories"]
            form_id = remo_html_from_string(data["form_id"])
            form_name = data["form_name"]
            form_name = remo_html_from_string(form_name)
            form_name = remo_special_tag_from_string(form_name)
            form_data = data["form_data"]

            try:
                cobrowse_form_obj = CobrowseVideoConferencingForm.objects.get(
                    pk=form_id)
                cobrowse_form_obj.form_name = form_name
                cobrowse_form_obj.save()

                for category in form_data:
                    try:
                        category_id = remo_html_from_string(
                            category["category_id"])
                        category_name = category["category_name"]
                        category_name = remo_html_from_string(category_name)
                        category_name = remo_special_tag_from_string(
                            category_name)

                        try:
                            cobrowse_form_category_obj = CobrowseVideoconferencingFormCategory.objects.get(
                                pk=category_id, is_deleted=False, form=cobrowse_form_obj)
                            cobrowse_form_category_obj.title = category_name
                            cobrowse_form_category_obj.save()
                        except Exception:
                            cobrowse_form_category_obj = CobrowseVideoconferencingFormCategory.objects.create(
                                form=cobrowse_form_obj, title=category_name)

                        for question in category["questions"]:
                            try:
                                question_id = remo_html_from_string(
                                    question["question_id"])
                                question_type = question["question_type"]
                                question_type = remo_html_from_string(
                                    question_type)
                                question_type = remo_special_tag_from_string(
                                    question_type)

                                question_label = question["question_label"]
                                question_label = remo_html_from_string(
                                    question_label)
                                question_label = remo_special_tag_from_string(
                                    question_label)

                                question_choices = question["question_choices"]
                                is_mandatory = question["is_mandatory"]

                                filtered_question_choices = []
                                for question_choice in question_choices:
                                    choice = remo_html_from_string(
                                        question_choice)
                                    choice = remo_special_tag_from_string(
                                        choice)
                                    filtered_question_choices.append(choice)

                                try:
                                    cobrowse_form_question_obj = CobrowseVideoConferencingFormElement.objects.get(
                                        pk=question_id, is_deleted=False, form_category=cobrowse_form_category_obj)
                                    cobrowse_form_question_obj.element_type = question_type
                                    cobrowse_form_question_obj.element_label = question_label
                                    cobrowse_form_question_obj.element_choices = json.dumps(
                                        filtered_question_choices)
                                    cobrowse_form_question_obj.is_mandatory = is_mandatory
                                    cobrowse_form_question_obj.save()
                                except Exception:
                                    CobrowseVideoConferencingFormElement.objects.create(
                                        form_category=cobrowse_form_category_obj,
                                        element_type=question_type,
                                        element_label=question_label,
                                        element_choices=json.dumps(
                                            filtered_question_choices),
                                        is_mandatory=is_mandatory)

                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logger.error("Error Form Question cannot be created %s at %s",
                                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Error Form Category cannot be created %s at %s",
                                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
                response['status'] = 200

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error SaveCobrowseFormAPI, Form does not exist %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

                response["status"] = 300

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowseFormAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowseForm = SaveCobrowseFormAPI.as_view()


class DeleteVideoConferencingFormAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside DeleteVideoConferencingFormAPI",
                        extra={'AppName': 'EasyAssistSalesforce'})
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            form_id = remo_html_from_string(data['form_id'])
            try:
                video_conferencing_form = CobrowseVideoConferencingForm.objects.get(
                    pk=form_id)
                video_conferencing_form.is_deleted = True
                video_conferencing_form.save()
                response['status'] = 200
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error Video Conferencing Form does not exist %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
                response['status'] = 300

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteVideoConferencingFormAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteVideoConferencingForm = DeleteVideoConferencingFormAPI.as_view()


class DeleteCobrowseFormCategoryAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside DeleteCobrowseFormCategoryAPI",
                        extra={'AppName': 'EasyAssistSalesforce'})
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            category_id = remo_html_from_string(data['category_id'])
            try:
                cobrowse_form_category_obj = CobrowseVideoconferencingFormCategory.objects.get(
                    pk=category_id, is_deleted=False)

                cobrowse_form_category_obj.is_deleted = True
                cobrowse_form_category_obj.save()
                response['status'] = 200
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error Video Conferencing Form Category does not exist %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
                response['status'] = 300

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteCobrowseFormCategory %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteCobrowseFormCategory = DeleteCobrowseFormCategoryAPI.as_view()


class DeleteCobrowseFormCategoryQuestionAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside DeleteCobrowseFormCategoryQuestionAPI", extra={
                        'AppName': 'EasyAssistSalesforce'})
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            question_id = remo_html_from_string(data['question_id'])
            try:
                cobrowse_form_element = CobrowseVideoConferencingFormElement.objects.get(
                    pk=question_id, is_deleted=False)

                cobrowse_form_element.is_deleted = True
                cobrowse_form_element.save()
                response['status'] = 200
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error Video Conferencing Form Question does not exist %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
                response['status'] = 300

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteCobrowseFormCategoryQuestionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteCobrowseFormCategoryQuestion = DeleteCobrowseFormCategoryQuestionAPI.as_view()


class ChangeCobrowseFormAgentAPI(APIView):

    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("Inside DeleteCobrowseFormCategoryQuestionAPI", extra={
                        'AppName': 'EasyAssistSalesforce'})
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)

            cobrowse_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if cobrowse_agent == None:
                return HttpResponse(status=401)

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            form_id = remo_html_from_string(data['form_id'])
            selected_agents = data["selected_agents"]

            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None)
            supervisors = get_list_supervisor_under_admin(
                cobrowse_agent, is_active=None)
            agents += supervisors

            try:
                cobrowse_form_obj = CobrowseVideoConferencingForm.objects.get(
                    pk=form_id, is_deleted=False)

                cobrowse_form_obj.agents.clear()
                for agent in agents:
                    if agent.pk == cobrowse_agent.pk:
                        cobrowse_form_obj.agents.add(agent)
                        continue

                    if str(agent.pk) in selected_agents:
                        cobrowse_form_obj.agents.add(agent)

                cobrowse_form_obj.save()
                response['status'] = 200
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error Video Conferencing Form does not exist %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
                response['status'] = 300

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ChangeCobrowseFormAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ChangeCobrowseFormAgent = ChangeCobrowseFormAgentAPI.as_view()
