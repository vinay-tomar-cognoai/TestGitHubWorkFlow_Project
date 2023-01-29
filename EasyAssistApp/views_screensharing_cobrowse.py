from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.middleware import csrf
"""For user authentication"""
from django.contrib.auth import authenticate, login, logout
# Create your views here.
from EasyAssistApp.models import *
from EasyAssistApp.utils import *
from EasyAssistApp.views_agent import *
from EasyAssistApp.views_analytics import *
from EasyAssistApp.views_app import *


import os
import sys
import json
import time
import base64
import uuid
import operator
import logging
import hashlib
import requests
import datetime
import urllib.parse

from operator import itemgetter
from collections import OrderedDict

logger = logging.getLogger(__name__)


def EasyAssistScreensharingCobrowse(request):

    try:
        logger.info("Inside EasyAssistScreensharingCobrowse...", extra={'AppName': 'EasyAssist'})
        session_id = None
        session_id = request.GET.get("id", None)

        if session_id == None:
            return HttpResponse(status=401)

        cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

        return render(request, "EasyAssistApp/screensharing_cobrowse.html", {
            "easyassist_session_id": session_id,
            "cobrowse_io": cobrowse_io,
            "easyassist_access_token": cobrowse_io.access_token,
            "easyassist_cobrowse_host": settings.EASYCHAT_DOMAIN,
            "easyassist_host_protocol": "http" if settings.DEBUG else "https",
            "DEVELOPMENT": settings.DEVELOPMENT,
            "access_token": str(cobrowse_io.access_token.key),
            "easyassist_font_family": cobrowse_io.access_token.font_family,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error EasyAssistScreensharingCobrowse %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(status=401)


def CobrowseIDScreensharingPage(request, session_id):
    try:
        logger.info("Inside CobrowseIDScreensharingPage...", extra={'AppName': 'EasyAssist'})
        cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

        if not request.user.is_authenticated:
            return redirect("/easy-assist/sales-ai/login")

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)

        access_token_obj = cobrowse_agent.get_access_token_obj()

        enable_edit_access = access_token_obj.enable_edit_access

        allow_cobrowsing_meeting = access_token_obj.allow_cobrowsing_meeting

        enable_screenshot_agent = access_token_obj.enable_screenshot_agent

        enable_invite_agent_in_cobrowsing = access_token_obj.enable_invite_agent_in_cobrowsing

        allow_support_documents = access_token_obj.allow_support_documents

        enable_optimized_cobrowsing = access_token_obj.enable_optimized_cobrowsing

        enable_predefined_remarks = access_token_obj.enable_predefined_remarks

        predefined_remarks = json.loads(access_token_obj.predefined_remarks)

        enable_predefined_subremarks = access_token_obj.enable_predefined_subremarks

        predefined_remarks_optional = access_token_obj.predefined_remarks_optional

        enable_predefined_remarks_with_buttons = access_token_obj.enable_predefined_remarks_with_buttons

        predefined_remarks_with_buttons = access_token_obj.predefined_remarks_with_buttons

        enable_low_bandwidth_cobrowsing = access_token_obj.enable_low_bandwidth_cobrowsing

        low_bandwidth_cobrowsing_threshold = access_token_obj.low_bandwidth_cobrowsing_threshold

        voip_decline_meeting_message = access_token_obj.agent_connect_message

        enable_agent_connect_message = access_token_obj.enable_agent_connect_message

        enable_chat_functionality = access_token_obj.enable_chat_functionality

        if len(predefined_remarks_with_buttons) == 0:
            predefined_remarks_with_buttons = []
        else:
            predefined_remarks_with_buttons = predefined_remarks_with_buttons.split(
                ',')

        if cobrowse_io.allow_agent_cobrowse != "true" and (not cobrowse_io.is_archived):
            return HttpResponse(status=401)

        is_cobrowsing_allowed = False

        agent_admin = cobrowse_io.access_token.agent
        is_socket = cobrowse_io.access_token.is_socket
        supported_language_objs = agent_admin.supported_language.filter(is_deleted=False).order_by('index')
        allow_language_support = cobrowse_io.access_token.allow_language_support
        product_category_objs = agent_admin.product_category.filter(is_deleted=False).order_by('index')
        choose_product_category = cobrowse_io.access_token.choose_product_category
        floating_button_bg_color = cobrowse_io.access_token.floating_button_bg_color
        support_agents = get_list_agents_under_admin(agent_admin, None)

        is_admin_agent = False
        if cobrowse_agent == cobrowse_io.agent:
            is_admin_agent = True

        if cobrowse_io.is_archived == True:
            return render(request, "EasyAssistApp/cobrowsing_session_expired.html", {
                "logo": access_token_obj.source_easyassist_cobrowse_logo,
                "cobrowse_agent": cobrowse_agent,
                "enable_predefined_remarks": enable_predefined_remarks,
                "enable_predefined_subremarks": enable_predefined_subremarks,
                "predefined_remarks": predefined_remarks,
                "predefined_remarks_optional": predefined_remarks_optional,
                "enable_predefined_remarks_with_buttons": enable_predefined_remarks_with_buttons,
                "predefined_remarks_with_buttons": predefined_remarks_with_buttons,
                "lead_conversion_checkbox_text": cobrowse_io.access_token.lead_conversion_checkbox_text,
                "DEVELOPMENT": settings.DEVELOPMENT,
                "access_token": str(cobrowse_io.access_token.key),
                "enable_optimized_cobrowsing": enable_optimized_cobrowsing,
                "session_id": session_id,
                "floating_button_bg_color": floating_button_bg_color,
                "is_admin_agent": is_admin_agent,
            })

        if "token" in request.GET and request.GET["token"] == "sales-ai":
            is_cobrowsing_allowed = True
        elif request.user.is_authenticated:
            user_obj = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
            cobrowse_agent.is_cobrowsing_active = True

            if cobrowse_io.agent == cobrowse_agent:
                is_cobrowsing_allowed = True
            elif cobrowse_agent in cobrowse_io.support_agents.all():
                is_cobrowsing_allowed = True

        if not is_cobrowsing_allowed:
            return HttpResponse(status=401)

        agent_name = cobrowse_agent.user.first_name
        if agent_name is None or agent_name.strip() == "":
            agent_name = cobrowse_agent.user.username
        client_name = cobrowse_io.full_name
        cobrowse_io.is_agent_connected = True
        if cobrowse_io.cobrowsing_start_datetime == None:
            cobrowse_io.cobrowsing_start_datetime = timezone.now()
        cobrowse_io.save()

        agent_joined_first_time = True
        system_audit_trail_obj = SystemAuditTrail.objects.filter(
            cobrowse_io=cobrowse_io,
            sender=cobrowse_agent,
            category="session_join").count()
        if system_audit_trail_obj > 0:
            agent_joined_first_time = False

        category = "session_join"
        description = "Agent " + str(cobrowse_agent.user.username) + " has joined session."
        save_system_audit_trail(category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, cobrowse_agent)

        try:
            voip_decline_meeting_message = voip_decline_meeting_message.replace(
                'agent_name', agent_name)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseIDScreensharingPage %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return render(request, "EasyAssistApp/screensharing_cobrowse_agent.html", {
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
            "enable_predefined_remarks": enable_predefined_remarks,
            "enable_predefined_subremarks": enable_predefined_subremarks,
            "predefined_remarks": predefined_remarks,
            "predefined_remarks_optional": predefined_remarks_optional,
            "enable_predefined_remarks_with_buttons": enable_predefined_remarks_with_buttons,
            "predefined_remarks_with_buttons": predefined_remarks_with_buttons,
            "lead_conversion_checkbox_text": cobrowse_io.access_token.lead_conversion_checkbox_text,
            "allow_cobrowsing_meeting": allow_cobrowsing_meeting,
            "easyassist_session_id": session_id,
            "easyassist_access_token": cobrowse_io.access_token,
            "toast_timeout": COBROWSE_TOAST_TIMEOUT,
            "agent_unique_id": str(uuid.uuid4()),
            "is_admin_agent": is_admin_agent,
            "enable_optimized_cobrowsing": enable_optimized_cobrowsing,
            "enable_screenshot_agent": enable_screenshot_agent,
            "allow_support_documents": allow_support_documents,
            "enable_invite_agent_in_cobrowsing": enable_invite_agent_in_cobrowsing,
            "access_token": str(access_token_obj.key),
            "DEVELOPMENT": settings.DEVELOPMENT,
            "enable_low_bandwidth_cobrowsing": enable_low_bandwidth_cobrowsing,
            "low_bandwidth_cobrowsing_threshold": low_bandwidth_cobrowsing_threshold,
            "voip_decline_meeting_message": voip_decline_meeting_message,
            "enable_agent_connect_message": enable_agent_connect_message,
            "agent_joined_first_time": agent_joined_first_time,
            "easyassist_font_family": cobrowse_io.access_token.font_family,
            "enable_chat_functionality": enable_chat_functionality,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowseIDScreensharingPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)
