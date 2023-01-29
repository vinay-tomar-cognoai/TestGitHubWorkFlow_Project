from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.exceptions import APIException

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

from EasyAssistApp.models import CobrowseAgent
"""For user authentication"""
from django.contrib.auth import authenticate, login, logout

from EasyChatApp.models import User, UserSession
from EasyAssistApp.models import *
from EasyAssistApp.utils import *
from EasyAssistApp.utils_email_analytics import *
from EasyAssistApp.utils_calendar import *
from EasyAssistApp.utils_execute_api_processor import execute_code_with_time_limit, execute_processor_python_code
from EasyAssistApp.views_table import *
from EasyAssistApp.views_sandbox_user import *
from EasyAssistApp.constants import *
from EasyAssistApp.send_email import send_password_over_email, send_drop_link_over_email, send_masking_pii_data_otp_mail, send_meeting_link_over_mail
from EasyChat.settings import APP_LOG_FILENAME, LOGTAILER_LINES

from DeveloperConsoleApp.utils import get_developer_console_settings, get_developer_console_cobrowsing_settings
from DeveloperConsoleApp.utils_aws_s3 import *

from PIL import Image
from urllib.parse import urlparse
from urllib.parse import parse_qs

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
import string
import func_timeout

from operator import itemgetter
from collections import OrderedDict
from EasyAssistApp.views_crm import *

logger = logging.getLogger(__name__)


def CobrowseForgotPassword(request):

    if request.user.is_authenticated:
        return redirect("/easy-assist/dashboard")

    return render(request, "EasyAssistApp/forgot-password.html")


@xframe_options_exempt
def SalesAILiveChatWindow(request):
    session_id = request.GET["session_id"]
    session_id = remo_html_from_string(session_id)
    is_agent = False
    initialize_canned_response = False
    if "is_agent" in request.GET and request.GET['is_agent'] == "True":
        is_agent = True

    cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
    access_token = cobrowse_io.access_token
    admin_agent = access_token.agent
    is_client_in_mobile = request.user_agent.is_mobile
    enable_s3_bucket = access_token.agent.user.enable_s3_bucket
    allow_agent_to_customer_cobrowsing = access_token.allow_agent_to_customer_cobrowsing
    allow_only_support_documents = access_token.allow_only_support_documents
    share_document_from_livechat = access_token.share_document_from_livechat
    enable_agent_connect_message = access_token.enable_agent_connect_message
    display_agent_profile = access_token.display_agent_profile
    canned_responses = []

    if allow_agent_to_customer_cobrowsing and "agent_code" in request.GET:
        agent_identifier = request.GET['agent_code']
        if agent_identifier:
            cobrowse_agent = CobrowseAgent.objects.filter(virtual_agent_code=agent_identifier).first()
        else:
            cobrowse_agent = None
    else:
        cobrowse_agent = get_active_agent_obj(request, CobrowseAgent)
    
    canned_responses = []
    commonly_used_canned_resposnse_obj = []
    canned_response_obj = []
    if cobrowse_agent:
        initialize_canned_response = True
        if cobrowse_agent == admin_agent:
            commonly_used_canned_resposnse_obj = AgentFrequentLiveChatCannedResponses.objects.filter(
                agent=cobrowse_agent, access_token=access_token, canned_response__is_deleted=False).order_by("-frequency")
            canned_response_obj = LiveChatCannedResponse.objects.filter(
                access_token=access_token, is_deleted=False).filter(~Q(pk__in=commonly_used_canned_resposnse_obj.values_list("canned_response"))).order_by("keyword")
        else:
            supervisors_list = get_supervisors_of_active_agent(
                cobrowse_agent, CobrowseAgent)
            supervisors_obj = supervisors_list + [admin_agent]
            commonly_used_canned_resposnse_obj = AgentFrequentLiveChatCannedResponses.objects.filter(
                agent=cobrowse_agent, access_token=access_token, canned_response__is_deleted=False).order_by("-frequency")
            canned_response_obj = LiveChatCannedResponse.objects.filter(
                agent__in=supervisors_obj, access_token=access_token, is_deleted=False).filter(~Q(pk__in=commonly_used_canned_resposnse_obj.values_list("canned_response"))).order_by("keyword")

        for response_obj in commonly_used_canned_resposnse_obj:
            canned_responses.append({
                "pk": response_obj.canned_response.pk,
                "keyword": response_obj.canned_response.keyword,
                "response": response_obj.canned_response.response,
            })

        for response_obj in canned_response_obj:
            canned_responses.append({
                "pk": response_obj.pk,
                "keyword": response_obj.keyword,
                "response": response_obj.response,
            })

    floating_button_bg_color = cobrowse_io.access_token.floating_button_bg_color
    
    return render(request, "EasyAssistApp/chatbot.html", {
        "access_token": access_token,
        "floating_button_bg_color": floating_button_bg_color,
        "enable_s3_bucket": enable_s3_bucket,
        "allow_agent_to_customer_cobrowsing": allow_agent_to_customer_cobrowsing,
        "allow_only_support_documents": allow_only_support_documents,
        "share_document_from_livechat": share_document_from_livechat,
        "enable_agent_connect_message": enable_agent_connect_message,
        "is_agent": is_agent,
        "easyassist_font_family": access_token.font_family,
        "display_agent_profile": display_agent_profile,
        "is_mobile": is_client_in_mobile,
        "enable_chat_functionality": access_token.enable_chat_functionality,
        "enable_preview_functionality": cobrowse_io.access_token.enable_preview_functionality,
        "enable_chat_bubble": access_token.enable_chat_bubble,
        "chat_bubble_icon_source": access_token.chat_bubble_icon_source,
        "canned_responses_list": canned_responses,
        "initialize_canned_response": initialize_canned_response,
    })


@authentication_classes([CsrfExemptSessionAuthentication, BasicAuthentication])
def LogoutAPI(request):
    if request.user.is_authenticated:
        active_agent = get_active_agent_obj(request, CobrowseAgent)
        user_obj = User.objects.get(username=request.user.username)
        user_obj.is_online = False
        user_obj.save()
        try:
            secured_login_obj = SecuredLogin.objects.get(user=user_obj)
            secured_login_obj.failed_attempts = 0
            secured_login_obj.is_online = False
            secured_login_obj.save()
        except Exception:
            pass
        active_agent.is_active = False
        active_agent.save()

        description = "Logout from System"
        save_audit_trail(active_agent, COBROWSING_LOGOUT_ACTION,
                         description, CobrowsingAuditTrail)

        add_audit_trail(
            "EASYASSISTAPP",
            active_agent.user,
            "Logout",
            description,
            json.dumps({}),
            request.META.get("PATH_INFO"),
            request.META.get('HTTP_X_FORWARDED_FOR')
        )

        logout_all(request.user.username, UserSession, Session)
        logout(request)

    return redirect("/chat/login/")


class AgentAuthenticationAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Invalid username or password"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cobrowsemiddlewaretoken = data["cobrowsemiddlewaretoken"]
            username = data["username"]
            password = data["password"]
            captcha = data["captcha"]
            user_captcha = data["user_captcha"]

            username = remo_html_from_string(username)
            username = remo_special_tag_from_string(username)
            password = remo_html_from_string(password)
            user_captcha = remo_html_from_string(user_captcha)
            user_captcha = remo_special_tag_from_string(user_captcha)

            user_captcha = generate_md5(user_captcha)

            captcha, _ = captcha.split(".")

            console_config = get_developer_console_settings()
            wrong_password_attempts = settings.wrong_password_attempts
            wrong_password_lockin_timeout = settings.wrong_password_lockin_timeout

            if console_config:
                wrong_password_attempts = console_config.wrong_password_attempts
                wrong_password_lockin_timeout = console_config.wrong_password_lockin_timeout

            if user_captcha != captcha:
                response["status"] = 101
                response["message"] = "Invalid captcha"
            else:

                user_obj = None
                try:
                    user_obj = User.objects.get(username=username)
                except Exception:
                    pass

                if user_obj != None:

                    user = authenticate(
                        request, username=username, password=password)
                    user_obj.is_online = is_online(username, UserSession)

                    access_token = None
                    try:
                        access_token = CobrowsingMiddlewareAccessToken.objects.get(
                            token=cobrowsemiddlewaretoken, is_expired=False)
                    except Exception:
                        pass

                    secured_login_obj = None
                    try:
                        secured_login_obj = SecuredLogin.objects.get(
                            user=user_obj)
                    except Exception:
                        secured_login_obj = SecuredLogin.objects.create(
                            user=user_obj)

                    logout_other = data["logout_other"]
                    logout_other = remo_html_from_string(logout_other)
                    logout_other = remo_special_tag_from_string(logout_other)
                    if logout_other == "true":
                        logout_all(user.username, UserSession, Session)
                        user_obj.is_online = False

                        try:
                            cobrowse_agent = CobrowseAgent.objects.get(
                                user=user_obj)
                            save_audit_trail(
                                cobrowse_agent, COBROWSING_LOGOUT_ACTION, "Logout from System", CobrowsingAuditTrail)
                        except Exception:
                            logger.error("Cobrowse Agent does not exist", extra={
                                         'AppName': 'EasyAssist'})

                    last_attempt_datetime_secs = secured_login_obj.last_attempted_datetime_secs()

                    is_login_allowed = True

                    if not settings.ALLOW_SIMULTANEOUS_LOGIN and user_obj.is_online:
                        response["status"] = 300
                        response[
                            "message"] = "Session is already running on other device. Kindly logout from past sessions."
                        is_login_allowed = False

                    is_secured_login_allowed = True
                    if secured_login_obj.failed_attempts >= wrong_password_attempts:
                        if last_attempt_datetime_secs <= wrong_password_lockin_timeout:
                            response["status"] = 101
                            response["message"] = "To many wrong attemps. Kindly try again after " + str(
                                int(wrong_password_lockin_timeout / 60)) + " mins"
                            is_secured_login_allowed = False
                        else:
                            secured_login_obj.failed_attempts = 0
                            secured_login_obj.last_attempt_datetime = timezone.now()
                            secured_login_obj.save()

                    logger.info("Is login allowed: %s", is_login_allowed, extra={
                                'AppName': 'EasyAssist'})
                    logger.info("Is secured login allowed: %s",
                                is_secured_login_allowed, extra={'AppName': 'EasyAssist'})

                    if is_login_allowed and is_secured_login_allowed:
                        if user is not None and access_token is not None:
                            access_token.is_expired = True
                            access_token.save()

                            cobrowse_agent = None
                            try:
                                cobrowse_agent = CobrowseAgent.objects.get(
                                    user=user)
                            except Exception:
                                pass

                            if cobrowse_agent != None and cobrowse_agent.is_account_active:
                                cobrowse_agent.is_active = True
                                cobrowse_agent.save()

                                user_obj.is_online = True
                                user_obj.save()

                                secured_login_obj.is_online = True

                                save_audit_trail(
                                    cobrowse_agent, COBROWSING_LOGIN_ACTION, "Login into System", CobrowsingAuditTrail)

                                login(request, user)
                                response["status"] = 200
                                response["message"] = "success"
                                response[
                                    "redirect"] = "/easy-assist/sales-ai/dashboard"
                            else:
                                response["status"] = 101
                                response[
                                    "message"] = "Matching user account doesn't exist."

                            secured_login_obj.failed_attempts = 0
                            secured_login_obj.last_attempt_datetime = timezone.now()
                            secured_login_obj.save()
                        else:
                            secured_login_obj.failed_attempts = secured_login_obj.failed_attempts + 1
                            secured_login_obj.last_attempt_datetime = timezone.now()
                            secured_login_obj.save()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AgentAuthenticationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AgentAuthentication = AgentAuthenticationAPI.as_view()


def CobrowseIOAgentPage(request, session_id):
    try:
        cobrowse_io = CobrowseIO.objects.filter(session_id=session_id).first()        
        if not request.user.is_authenticated:
            return redirect("/chat/login/")

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)

        access_token_obj = cobrowse_agent.get_access_token_obj()

        invited_agent_details_obj = None
        if access_token_obj.enable_invite_agent_in_cobrowsing:
            invited_agent_details_objs = CobrowseIOInvitedAgentsDetails.objects.filter(
                cobrowse_io=cobrowse_io)
            if invited_agent_details_objs:
                invited_agent_details_obj = invited_agent_details_objs[0]

        invited_agent_username = ""

        enable_edit_access = access_token_obj.enable_edit_access

        enable_screenshot_agent = access_token_obj.enable_screenshot_agent

        allow_support_documents = access_token_obj.allow_support_documents

        allow_cobrowsing_meeting = access_token_obj.allow_cobrowsing_meeting

        enable_chat_bubble = access_token_obj.enable_chat_bubble

        chat_bubble_icon_source = access_token_obj.chat_bubble_icon_source

        enable_invite_agent_in_cobrowsing = access_token_obj.enable_invite_agent_in_cobrowsing and (
            not cobrowse_io.is_cobrowsing_from_livechat)

        enable_predefined_remarks = access_token_obj.enable_predefined_remarks

        predefined_remarks = access_token_obj.predefined_remarks

        enable_predefined_subremarks = access_token_obj.enable_predefined_subremarks

        predefined_remarks_optional = access_token_obj.predefined_remarks_optional

        enable_predefined_remarks_with_buttons = access_token_obj.enable_predefined_remarks_with_buttons

        predefined_remarks_with_buttons = access_token_obj.predefined_remarks_with_buttons

        enable_voip_calling = access_token_obj.enable_voip_calling

        enable_voip_with_video_calling = access_token_obj.enable_voip_with_video_calling

        voip_decline_meeting_message = access_token_obj.agent_connect_message

        allow_video_meeting_only = access_token_obj.allow_video_meeting_only

        enable_auto_voip_calling_for_first_time = access_token_obj.enable_auto_voip_calling_for_first_time

        enable_auto_voip_with_video_calling_for_first_time = access_token_obj.enable_auto_voip_with_video_calling_for_first_time

        enable_optimized_cobrowsing = access_token_obj.enable_optimized_cobrowsing

        enable_low_bandwidth_cobrowsing = access_token_obj.enable_low_bandwidth_cobrowsing

        enable_manual_switching = access_token_obj.enable_manual_switching

        low_bandwidth_cobrowsing_threshold = access_token_obj.low_bandwidth_cobrowsing_threshold

        enable_agent_connect_message = access_token_obj.enable_agent_connect_message

        enable_cobrowsing_annotation = access_token_obj.enable_cobrowsing_annotation

        enable_iframe_cobrowsing = access_token_obj.enable_iframe_cobrowsing

        enable_chat_functionality = access_token_obj.enable_chat_functionality

        enable_auto_calling = False
        if enable_voip_calling and enable_auto_voip_calling_for_first_time:
            enable_auto_calling = True

        if enable_voip_with_video_calling and enable_auto_voip_with_video_calling_for_first_time:
            enable_auto_calling = True

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
        supported_language_objs = agent_admin.supported_language.filter(
            is_deleted=False).order_by('index')
        allow_language_support = cobrowse_io.access_token.allow_language_support
        product_category_objs = agent_admin.product_category.filter(
            is_deleted=False).order_by('index')
        choose_product_category = cobrowse_io.access_token.choose_product_category
        floating_button_bg_color = cobrowse_io.access_token.floating_button_bg_color
        support_agents = get_list_agents_under_admin(agent_admin, None)
        is_client_in_mobile = cobrowse_io.is_client_in_mobile

        is_admin_agent = False

        if cobrowse_agent == cobrowse_io.agent:
            is_admin_agent = True

        try:
            predefined_remarks = json.loads(predefined_remarks)
        except Exception:
            predefined_remarks = []

        if cobrowse_io.is_archived == True:
            return render(request, "EasyAssistApp/cobrowsing_session_expired.html", {
                "logo": access_token_obj.source_easyassist_cobrowse_logo,
                "cobrowse_agent": cobrowse_agent,
                "enable_predefined_remarks": enable_predefined_remarks,
                "enable_predefined_subremarks": enable_predefined_subremarks,
                "predefined_remarks": predefined_remarks,
                "enable_predefined_remarks_with_buttons": enable_predefined_remarks_with_buttons,
                "predefined_remarks_with_buttons": predefined_remarks_with_buttons,
                "predefined_remarks_optional": predefined_remarks_optional,
                "lead_conversion_checkbox_text": cobrowse_io.access_token.lead_conversion_checkbox_text,
                "DEVELOPMENT": settings.DEVELOPMENT,
                "access_token": str(cobrowse_io.access_token.key),
                "enable_optimized_cobrowsing": enable_optimized_cobrowsing,
                "session_id": session_id,
                "floating_button_bg_color": floating_button_bg_color,
                "is_admin_agent": is_admin_agent,
                "easyassist_font_family": cobrowse_io.access_token.font_family,
            })

        if "token" in request.GET and request.GET["token"] == "sales-ai":
            is_cobrowsing_allowed = True
        elif request.user.is_authenticated:
            user_obj = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
            cobrowse_agent.is_cobrowsing_active = True
            transferred_io_objs = CobrowseIOTransferredAgentsLogs.objects.filter(
                cobrowse_io=cobrowse_io, cobrowse_request_type="transferred", transferred_status="accepted").order_by("-log_request_datetime").first()
            if cobrowse_io.agent == cobrowse_agent:
                is_cobrowsing_allowed = True
            if transferred_io_objs:
                is_cobrowsing_allowed = True
            elif cobrowse_agent in cobrowse_io.support_agents.all():
                is_cobrowsing_allowed = True
                if invited_agent_details_obj != None:
                    invited_agent_details_obj.support_agents_joined.add(
                        cobrowse_agent)
                    transferred_io_log_objs = CobrowseIOTransferredAgentsLogs.objects.filter(
                        cobrowse_io=cobrowse_io, cobrowse_request_type="invited", invited_status="").order_by("-log_request_datetime").first()
                    if transferred_io_log_objs:
                        transferred_io_log_objs.invited_status = "accepted"
                        transferred_io_log_objs.save()
                    invited_agent_details_obj.save()
                    invited_agent_username = cobrowse_agent.user.username
                if cobrowse_io.meeting_start_datetime != None:
                    meeting_io = CobrowseVideoConferencing.objects.filter(
                        meeting_id=session_id)
                    if meeting_io:
                        meeting_io = meeting_io.first()
                        video_audit_trail_obj = CobrowseVideoAuditTrail.objects.filter(
                            cobrowse_video=meeting_io)
                        if video_audit_trail_obj:
                            video_audit_trail_obj = video_audit_trail_obj.first()
                            video_audit_trail_obj.meeting_agents_invited.add(
                                cobrowse_agent)
                            video_audit_trail_obj.save()

        if not is_cobrowsing_allowed:
            return HttpResponse(status=401)

        agent_name = cobrowse_agent.user.first_name
        if agent_name is None or agent_name.strip() == "":
            agent_name = cobrowse_agent.user.username
        agent_profile_pic_source = cobrowse_agent.agent_profile_pic_source
        display_agent_profile = cobrowse_io.access_token.display_agent_profile
        client_name = cobrowse_io.full_name
        cobrowse_io.is_agent_connected = True
        cobrowse_io.last_agent_update_datetime = timezone.now()
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
        
        if transferred_io_objs:
            agent_joined_first_time = False

        if cobrowse_io.agent != cobrowse_agent:
            agent_joined_first_time = True

        category = "session_join"
        description = "Agent " + \
            str(cobrowse_agent.user.username) + " has joined session."
        save_system_audit_trail(category, description, cobrowse_io,
                                cobrowse_io.access_token, SystemAuditTrail, cobrowse_agent)
        try:
            voip_decline_meeting_message = voip_decline_meeting_message.replace(
                'agent_name', agent_name)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseIOAgentPage %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        
        generated_link = ""
        proxy_client_email = ""
        if access_token_obj.get_proxy_config_obj().enable_proxy_cobrowsing:
            proxy_key_obj = cobrowse_io.proxy_key_list.all().order_by("key_generation_datetime").first()
            if proxy_key_obj:
                drop_link_obj = CobrowseDropLink.objects.filter(proxy_cobrowse_io=proxy_key_obj).first()
                if drop_link_obj:
                    proxy_client_email = drop_link_obj.customer_email
                    generated_link = drop_link_obj.generated_link
        
        return render(request, "EasyAssistApp/cobrowse_agent.html", {
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
            "enable_screenshot_agent": enable_screenshot_agent,
            "allow_support_documents": allow_support_documents,
            "enable_invite_agent_in_cobrowsing": enable_invite_agent_in_cobrowsing,
            "enable_predefined_remarks": enable_predefined_remarks,
            "enable_predefined_subremarks": enable_predefined_subremarks,
            "predefined_remarks": predefined_remarks,
            "enable_predefined_remarks_with_buttons": enable_predefined_remarks_with_buttons,
            "predefined_remarks_with_buttons": predefined_remarks_with_buttons,
            "predefined_remarks_optional": predefined_remarks_optional,
            "enable_voip_calling": enable_voip_calling,
            "enable_voip_with_video_calling": enable_voip_with_video_calling,
            "voip_decline_meeting_message": voip_decline_meeting_message,
            "allow_video_meeting_only": allow_video_meeting_only,
            "agent_unique_id": str(uuid.uuid4()),
            "enable_auto_calling": enable_auto_calling,
            "toast_timeout": COBROWSE_TOAST_TIMEOUT,
            "enable_optimized_cobrowsing": enable_optimized_cobrowsing,
            "access_token": str(cobrowse_io.access_token.key),
            "DEVELOPMENT": settings.DEVELOPMENT,
            "is_mobile": request.user_agent.is_mobile,
            "is_client_in_mobile": is_client_in_mobile,
            "enable_low_bandwidth_cobrowsing": enable_low_bandwidth_cobrowsing,
            "enable_manual_switching": enable_manual_switching,
            "low_bandwidth_cobrowsing_threshold": low_bandwidth_cobrowsing_threshold,
            "agent_joined_first_time": agent_joined_first_time,
            "enable_agent_connect_message": enable_agent_connect_message,
            "enable_cobrowsing_annotation": enable_cobrowsing_annotation,
            "easyassist_font_family": cobrowse_io.access_token.font_family,
            "enable_iframe_cobrowsing": enable_iframe_cobrowsing,
            "enable_chat_functionality": enable_chat_functionality,
            "invited_agent_username": invited_agent_username,
            "agent_profile_pic_source": agent_profile_pic_source,
            "display_agent_profile": display_agent_profile,
            "floating_button_position": cobrowse_io.access_token.floating_button_position,
            "enable_chat_bubble": enable_chat_bubble,
            "enable_session_transfer_in_cobrowsing": cobrowse_io.access_token.enable_session_transfer_in_cobrowsing,
            "chat_bubble_icon_source": chat_bubble_icon_source,
            "enable_proxy_cobrowsing": cobrowse_io.access_token.get_proxy_config_obj().enable_proxy_cobrowsing,
            "generated_link": generated_link,
            "cobrowsing_type": cobrowse_io.cobrowsing_type,
            "proxy_client_email": proxy_client_email,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowseIOAgentPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)


def SalesAIDashboard(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login/")

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        access_token_obj = cobrowse_agent.get_access_token_obj()

        agents = []
        if cobrowse_agent.role == "agent":
            agents = [cobrowse_agent]
        elif cobrowse_agent.role == "supervisor":
            agents = list(cobrowse_agent.agents.all())
        else:
            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None)

        cobrowse_admin = get_admin_from_active_agent(
            cobrowse_agent, CobrowseAgent)

        build_default_calendar(cobrowse_admin, CobrowseCalendar)

        cobrowse_io_objs = CobrowseIO.objects.filter(
            is_archived=False, agent__in=agents)
        cobrowse_io_support_objs = CobrowseIO.objects.filter(
            is_archived=False, support_agents__in=agents)
        cobrowse_io_objs = cobrowse_io_objs | cobrowse_io_support_objs
        cobrowse_io_objs = cobrowse_io_objs.order_by("-request_datetime")

        total_active_session = cobrowse_io_objs.filter(
            allow_agent_cobrowse="true").count()

        enable_predefined_remarks = access_token_obj.enable_predefined_remarks

        enable_predefined_subremarks = access_token_obj.enable_predefined_subremarks

        predefined_remarks = json.loads(access_token_obj.predefined_remarks)

        enable_predefined_remarks_with_buttons = access_token_obj.enable_predefined_remarks_with_buttons

        predefined_remarks_with_buttons = access_token_obj.predefined_remarks_with_buttons

        if len(predefined_remarks_with_buttons) == 0:
            predefined_remarks_with_buttons = []
        else:
            predefined_remarks_with_buttons = predefined_remarks_with_buttons.split(
                ',')

        predefined_remarks_optional = access_token_obj.predefined_remarks_optional

        is_cognomeet_token_generated = False

        if access_token_obj.cogno_meet_access_token:
            is_cognomeet_token_generated = True

        return render(request, "EasyAssistApp/sales_dashboard.html", {
            "cobrowse_io_objs": cobrowse_io_objs,
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "total_active_session": total_active_session,
            "enable_predefined_remarks": enable_predefined_remarks,
            "enable_predefined_subremarks": enable_predefined_subremarks,
            "predefined_remarks": predefined_remarks,
            "enable_predefined_remarks_with_buttons": enable_predefined_remarks_with_buttons,
            "predefined_remarks_optional": predefined_remarks_optional,
            "predefined_remarks_with_buttons": predefined_remarks_with_buttons,
            "is_cognomeet_token_generated": is_cognomeet_token_generated
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAIDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesSupportHistory(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        active_agent = get_active_agent_obj(request, CobrowseAgent)
        access_token_obj = active_agent.get_access_token_obj()

        agent_objs = [active_agent]
        supervisor_objs = []

        if active_agent.role in ["admin", "admin_ally"]:
            agent_objs = get_list_agents_under_admin(
                active_agent, is_active=None, is_account_active=None)
            supervisor_objs = active_agent.agents.filter(role="supervisor")
        elif active_agent.role == "supervisor":
            agent_objs = list(active_agent.agents.all())
        
        cobrowse_io_objs = CobrowseIO.objects.filter(
            is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True).filter(
            agent__in=agent_objs).filter(
            ~Q(cobrowsing_start_datetime=None))

        if active_agent.role in ["agent", "supervisor"] and access_token_obj.enable_invite_agent_in_cobrowsing:
            invited_agent_details_objs = CobrowseIOInvitedAgentsDetails.objects.select_related(
                'cobrowse_io').filter(support_agents_joined__in=agent_objs)
            if invited_agent_details_objs:
                invited_session_ids = []
                for invited_agent_details_obj in invited_agent_details_objs:
                    invited_session_ids.append(
                        invited_agent_details_obj.cobrowse_io.session_id)
                invited_sessions_cobrowse_objs = CobrowseIO.objects.filter(session_id__in=invited_session_ids, is_test=False, access_token=access_token_obj,
                                                                           request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True).filter(~Q(cobrowsing_start_datetime=None))
                cobrowse_io_objs = cobrowse_io_objs | invited_sessions_cobrowse_objs
        
            if access_token_obj.enable_session_transfer_in_cobrowsing:
                transferred_agent_details_objs = CobrowseIOTransferredAgentsLogs.objects.select_related(
                    'cobrowse_io').filter(transferred_agent__in=agent_objs, transferred_status="accepted")
                if transferred_agent_details_objs:
                    transferred_session_ids = []
                    for transferred_agent_details_obj in transferred_agent_details_objs:
                        transferred_session_ids.append(
                            transferred_agent_details_obj.cobrowse_io.session_id)
                    transferred_sessions_cobrowse_objs = CobrowseIO.objects.filter(session_id__in=transferred_session_ids, is_test=False, access_token=access_token_obj,
                                                                                   request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True).filter(~Q(cobrowsing_start_datetime=None))
                    cobrowse_io_objs = cobrowse_io_objs | transferred_sessions_cobrowse_objs
        is_support_history_empty = False
        if cobrowse_io_objs.count() == 0:
            is_support_history_empty = True

        is_filter_applied = False

        if "startdate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                request_datetime__date__gte=datetime_start)
            is_filter_applied = True

        if "enddate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                request_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if "title" in request.GET:
            title = request.GET.getlist("title")
            title = remo_html_from_string(title)
            cobrowse_io_objs = cobrowse_io_objs.filter(title__in=title)
            is_filter_applied = True

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")
            selected_agents = CobrowseAgent.objects.filter(
                user__username__in=agent_email)
            cobrowse_io_objs = cobrowse_io_objs.filter(
                agent__in=selected_agents)
            is_filter_applied = True

        if "supervisor" in request.GET:
            supervisor_email_id_list = request.GET.getlist("supervisor")
            selected_agents = []
            for agent_email_id in supervisor_email_id_list:
                selected_supervisor = active_agent.agents.filter(
                    user__username=agent_email_id).first()
                selected_agents += list(selected_supervisor.agents.all())
            cobrowse_io_objs = cobrowse_io_objs.filter(
                agent__in=selected_agents)
            is_filter_applied = True

        if "status" in request.GET:
            session_status = request.GET.getlist("status")[0]
            session_status = remo_html_from_string(session_status)
            if session_status == "Converted":
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    is_helpful=True, is_archived=True)
                is_filter_applied = True
            elif session_status == "Not Converted":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_helpful=False)
                is_filter_applied = True

        if "lead-type" in request.GET:
            lead_type = request.GET.getlist("lead-type")[0]
            lead_type = remo_html_from_string(lead_type)
            if lead_type == "Outbound":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_lead=True)
                is_filter_applied = True
            elif lead_type == "Reverse":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_reverse_cobrowsing=True)
                is_filter_applied = True
            elif lead_type == "Drop Link":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_droplink_lead=True)
                is_filter_applied = True
            elif lead_type == "Modified Inbound":
                cobrowse_io_objs = cobrowse_io_objs.filter(cobrowsing_type="modified-inbound")
                is_filter_applied = True
            elif lead_type == "Outbound Proxy":
                cobrowse_io_objs = cobrowse_io_objs.filter(cobrowsing_type="outbound-proxy-cobrowsing")
                is_filter_applied = True
            else:
                cobrowse_io_objs = cobrowse_io_objs.filter(is_lead=False, is_reverse_cobrowsing=False, is_droplink_lead=False).filter(
                    ~Q(cobrowsing_type__in=["outbound-proxy-cobrowsing", "modified-inbound"]))
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
            cobrowse_io_objs = cobrowse_io_objs.filter(request_datetime__date__gte=datetime_start,
                                                       request_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if cobrowse_io_objs.count() > 0:
            cobrowse_io_objs = cobrowse_io_objs.order_by('-request_datetime')

        title_list = get_visited_page_title_list_with_agent(
            active_agent, CobrowseIO)

        edit_access_audit_trail_objs = {}

        for cobrowse_io_obj in cobrowse_io_objs:
            edit_access_audit_trail_objs[
                cobrowse_io_obj.session_id] = [1, 2, 3]

        total_rows_per_pages = 20
        total_cobrowse_objs = len(cobrowse_io_objs)
        paginator = Paginator(
            cobrowse_io_objs, total_rows_per_pages)
        page = request.GET.get('page')

        try:
            cobrowse_io_objs = paginator.page(page)
        except PageNotAnInteger:
            cobrowse_io_objs = paginator.page(1)
        except EmptyPage:
            cobrowse_io_objs = paginator.page(paginator.num_pages)

        if page != None:
            start_point = total_rows_per_pages * (int(page) - 1) + 1
            end_point = min(total_rows_per_pages *
                            int(page), total_cobrowse_objs)
            if start_point > end_point:
                start_point = max(end_point - len(cobrowse_io_objs) + 1, 1)
        else:
            start_point = 1
            end_point = min(total_rows_per_pages, total_cobrowse_objs)
        
        return render(request, "EasyAssistApp/sales_support_history.html", {
            "is_filter_applied": is_filter_applied,
            "cobrowse_io_objs": cobrowse_io_objs,
            "cobrowse_agent": active_agent,
            "access_token_obj": access_token_obj,
            "agents": agent_objs,
            "title_list": title_list,
            "edit_access_audit_trail_objs": edit_access_audit_trail_objs,
            "start_point": start_point,
            "end_point": end_point,
            "total_cobrowse_objs": total_cobrowse_objs,
            "is_support_history_empty": is_support_history_empty,
            "supervisors": supervisor_objs,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesSupportHistory %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesMeetings(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login/")

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)        
        cogno_meet_access_token_key = None

        access_token = CobrowseAccessToken.objects.filter(
            agent=cobrowse_agent).first()
        if(access_token):
            cogno_meet_access_token_key = access_token.cogno_meet_access_token            

        cogno_meet_data = {}
        cogno_meet_data["agent_type"] = cobrowse_agent.role
        agent_role = None
        agents = []
        supervisor_objs = []
        
        if cobrowse_agent.role == "agent":
            agent_role = 'agent'
            agents = [cobrowse_agent]
        elif cobrowse_agent.role == "supervisor":
            agent_role = 'supervisor'
            agents = list(cobrowse_agent.agents.all()) + [cobrowse_agent]
        else:
            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None, is_account_active=None)
            supervisor_objs = cobrowse_agent.agents.filter(role="supervisor")

        if cobrowse_agent.role == "supervisor":
            agents.append(cobrowse_agent)
        elif cobrowse_agent.role == "admin_ally":
            agent_role = 'admin_ally'
            agents += cobrowse_agent.agents.all().filter(role="supervisor")
            supervisor_objs |= cobrowse_agent.agents.all().filter(role="supervisor")
        elif cobrowse_agent.role == "admin":
            agent_role = "admin"
            admin_ally_objs = cobrowse_agent.agents.all().filter(role="admin_ally")
            for admin_ally_obj in admin_ally_objs:
                agents += admin_ally_obj.agents.all().filter(role="supervisor")
                supervisor_objs |= admin_ally_obj.agents.all().filter(role="supervisor")
            agents += cobrowse_agent.agents.all().filter(role="supervisor")

        AGENTS_LIST = []
        for agent in agents:
            AGENTS_LIST.append(agent.user.username)
        
        supervisor_list = []
        AGENT_VS_SUPERVISOR_MAP = {}
        for agent_obj in supervisor_objs:
            supervisor_list.append(agent_obj.user.username)
            cobrowse_agent_temp = CobrowseAgent.objects.filter(
                user=agent_obj.user, is_account_active=True).first()
            if cobrowse_agent_temp:
                for agents in cobrowse_agent_temp.agents.all():
                    AGENT_VS_SUPERVISOR_MAP[str(agents.user.username)] = str(
                        cobrowse_agent_temp.user.username)

        access_token_obj = cobrowse_agent.get_access_token_obj()
        cogno_meet_access_token_key = access_token_obj.cogno_meet_access_token
        allow_meeting_end_time = access_token_obj.allow_meeting_end_time
        meeting_end_time = '30'
        if allow_meeting_end_time:
            meeting_end_time = access_token_obj.meeting_end_time
        if access_token_obj.allow_generate_meeting:
            cognovid_objs = CobrowseVideoConferencing.objects.filter(
                agent=cobrowse_agent, is_expired=False, is_cobrowsing_meeting=False).order_by('-meeting_start_date')

            cognovid_support_meeting_objs = CobrowseVideoConferencing.objects.filter(
                support_meeting_agents=cobrowse_agent, is_expired=False, is_cobrowsing_meeting=False).order_by('-meeting_start_date')

            cognovid_objs = cognovid_objs | cognovid_support_meeting_objs

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

            if access_token_obj.enable_cognomeet:
                return render(request, "EasyAssistApp/sales_meeting_dyte.html", {
                    "cognovid_objs": unexpired_cognovid_objs,
                    "cobrowse_agent": cobrowse_agent,
                    "access_token_obj": access_token_obj,
                    "default_password": default_password,
                    "agent_objs": agent_objs,
                    "meeting_end_time": meeting_end_time,
                    "agents_list": list(set(AGENTS_LIST)),
                    "agent_vs_supervisor_map": AGENT_VS_SUPERVISOR_MAP,
                    "cogno_meet_access_token": cogno_meet_access_token_key,
                    "agent_role": agent_role,
                    "supervisor_list": list(set(supervisor_list))
                })
            else:
                return render(request, "EasyAssistApp/sales_meeting.html", {
                    "cognovid_objs": unexpired_cognovid_objs,
                    "cobrowse_agent": cobrowse_agent,
                    "access_token_obj": access_token_obj,
                    "default_password": default_password,
                    "agent_objs": agent_objs,
                    "meeting_end_time": meeting_end_time,
                })
        else:
            return HttpResponse(INVALID_ACCESS_CONSTANT)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesMeetings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(INVALID_ACCESS_CONSTANT)


def ScreenRecordingAuditTrail(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        active_agent = get_active_agent_obj(request, CobrowseAgent)
        access_token_obj = active_agent.get_access_token_obj()

        agent_objs = [active_agent]
        supervisor_objs = []

        if active_agent.role in ["admin", "admin_ally"]:
            agent_objs = get_list_agents_under_admin(
                active_agent, is_active=None, is_account_active=None)
            supervisor_objs = active_agent.agents.filter(role="supervisor")
        elif active_agent.role == "supervisor":
            agent_objs = list(active_agent.agents.all())

        screen_recording_objs = CobrowseScreenRecordingAuditTrail.objects.filter(
            cobrowse_io__is_test=False, cobrowse_io__access_token=access_token_obj, recording_started__date__gte=access_token_obj.go_live_date).filter(
            agent__in=agent_objs, is_expired=False)

        is_audit_trail_empty = False
        is_filter_applied = False
        if screen_recording_objs.count() == 0:
            is_audit_trail_empty = True

        if "startdate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()

            screen_recording_objs = screen_recording_objs.filter(
                recording_started__date__gte=datetime_start)
            is_filter_applied = True

        if "enddate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()
            screen_recording_objs = screen_recording_objs.filter(
                recording_started__date__lte=datetime_end)
            is_filter_applied = True

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")
            selected_agents = CobrowseAgent.objects.filter(
                user__username__in=agent_email)
            screen_recording_objs = screen_recording_objs.filter(
                agent__in=selected_agents)
            is_filter_applied = True

        if "supervisor" in request.GET:
            supervisor_email_id_list = request.GET.getlist("supervisor")
            selected_agents = []
            for agent_email_id in supervisor_email_id_list:
                selected_supervisor = active_agent.agents.filter(
                    user__username=agent_email_id).first()
                selected_agents += list(selected_supervisor.agents.all())
            screen_recording_objs = screen_recording_objs.filter(
                agent__in=selected_agents)
            is_filter_applied = True

        if not is_filter_applied:
            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()
            datetime_end = datetime.datetime.today().date()
            screen_recording_objs = screen_recording_objs.filter(
                recording_started__date__gte=datetime_start, recording_started__date__lte=datetime_end)
            is_filter_applied = True

        screen_recording_objs = screen_recording_objs.order_by(
            '-recording_ended')

        total_rows_per_pages = 20
        total_screen_recording_objs = len(screen_recording_objs)
        paginator = Paginator(
            screen_recording_objs, total_rows_per_pages)
        page = request.GET.get('page')

        try:
            screen_recording_objs = paginator.page(page)
        except PageNotAnInteger:
            screen_recording_objs = paginator.page(1)
        except EmptyPage:
            screen_recording_objs = paginator.page(paginator.num_pages)

        if page != None:
            start_point = total_rows_per_pages * (int(page) - 1) + 1
            end_point = min(total_rows_per_pages * int(page),
                            total_screen_recording_objs)
            if start_point > end_point:
                start_point = max(
                    end_point - len(screen_recording_objs) + 1, 1)
        else:
            start_point = 1
            end_point = min(total_rows_per_pages, total_screen_recording_objs)

        return render(request, "EasyAssistApp/screen_recording_audit_trail.html", {
            "screen_recording_objs": screen_recording_objs,
            "cobrowse_agent": active_agent,
            "access_token_obj": access_token_obj,
            "start_point": start_point,
            "end_point": end_point,
            "total_screen_recording_objs": total_screen_recording_objs,
            "agents": agent_objs,
            "is_audit_trail_empty": is_audit_trail_empty,
            "is_filter_applied": is_filter_applied,
            "supervisors": supervisor_objs,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ScreenRecordingAuditTrail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(INVALID_ACCESS_CONSTANT)


class ExportSalesSupportHistoryAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['chat_status'] = 500
        response['support_status'] = 500
        response["export_path"] = "None"
        response["export_path_exist"] = False
        response["chat_export_path"] = "None"
        response["chat_export_path_exist"] = False
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
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
            
            if requested_data["selected_filter_value"] == "4":
                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], DATE_TIME_FORMAT).date()
                end_date = datetime.datetime.strptime(
                    requested_data["enddate"], DATE_TIME_FORMAT).date()
                agents = get_list_agents_under_admin(
                    cobrowse_agent, is_active=None, is_account_active=None)
                access_token_obj = cobrowse_agent.get_access_token_obj()

                cobrowse_io_objs = CobrowseIO.objects.filter(
                    is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True).filter(
                    request_datetime__date__gte=start_date, request_datetime__date__lte=end_date, agent__in=agents).filter(
                    ~Q(cobrowsing_start_datetime=None))

                if cobrowse_agent.role == "supervisor" and access_token_obj.enable_invite_agent_in_cobrowsing:
                    invited_agent_details_objs = CobrowseIOInvitedAgentsDetails.objects.select_related(
                        'cobrowse_io').filter(support_agents_joined__in=agents)
                    if invited_agent_details_objs:
                        invited_session_ids = []
                        for invited_agent_details_obj in invited_agent_details_objs:
                            invited_session_ids.append(
                                invited_agent_details_obj.cobrowse_io.session_id)
                        invited_sessions_cobrowse_objs = CobrowseIO.objects.filter(session_id__in=invited_session_ids, is_test=False, access_token=access_token_obj,
                                                                                   request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True).filter(
                            request_datetime__date__gte=start_date, request_datetime__date__lte=end_date).filter(~Q(cobrowsing_start_datetime=None))
                        cobrowse_io_objs = cobrowse_io_objs | invited_sessions_cobrowse_objs

                    if access_token_obj.enable_session_transfer_in_cobrowsing:
                        transferred_agent_details_objs = CobrowseIOTransferredAgentsLogs.objects.filter(
                            transferred_agent__in=agents, cobrowse_request_type="transferred")
                        if transferred_agent_details_objs:
                            transferred_session_ids = []
                            for transferred_agent_details_obj in transferred_agent_details_objs:
                                transferred_session_ids.append(
                                    transferred_agent_details_obj.cobrowse_io.session_id)
                            transferred_sessions_cobrowse_objs = CobrowseIO.objects.filter(session_id__in=transferred_session_ids, is_test=False, access_token=access_token_obj,
                                                                                           request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True).filter(
                                request_datetime__date__gte=start_date, request_datetime__date__lte=end_date).filter(~Q(cobrowsing_start_datetime=None))
                            cobrowse_io_objs = cobrowse_io_objs | transferred_sessions_cobrowse_objs

                if not cobrowse_io_objs:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            if requested_data["is_support_history"]:
                if requested_data["selected_filter_value"] == "1":
                    export_path = get_custom_support_history(
                        get_requested_data_for_daily(), cobrowse_agent, CobrowseIO)
                    if export_path == NO_DATA:
                        return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))
                    
                elif requested_data["selected_filter_value"] == "2":
                    export_path = get_custom_support_history(
                        get_requested_data_for_week(), cobrowse_agent, CobrowseIO)

                    if export_path == NO_DATA:
                        return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

                elif requested_data["selected_filter_value"] == "3":
                    export_path = get_custom_support_history(
                        get_requested_data_for_month(), cobrowse_agent, CobrowseIO)

                    if export_path == NO_DATA:
                        return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

                elif requested_data["selected_filter_value"] == "4":

                    today_date = datetime.datetime.today().date()

                    if(today_date - start_date).days > 30:
                        EasyAssistExportDataRequest.objects.create(
                            report_type='support-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                        response["support_status"] = 300
                        response["export_path"] = "None"
                        response["export_path_exist"] = False
                    else:
                        if cobrowse_io_objs.count() > EXPORTS_UPPER_CAP_LIMIT:
                            EasyAssistExportDataRequest.objects.create(
                                report_type='support-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                            response["support_status"] = 300
                            response["export_path"] = "None"
                            response["export_path_exist"] = False
                        else:
                            export_path = get_custom_support_history(
                                requested_data, cobrowse_agent, CobrowseIO, cobrowse_io_objs)

            if requested_data["is_chat_history"]:
                                        
                if requested_data["selected_filter_value"] == "1":
                    chat_history_export_path = get_custom_live_chat_history(
                        get_requested_data_for_daily(), cobrowse_agent, CobrowseIO, CobrowseIOInvitedAgentsDetails,
                        CobrowseIOTransferredAgentsLogs, CobrowseChatHistory)
                    
                    if chat_history_export_path == NO_DATA:
                        return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))
                    
                elif requested_data["selected_filter_value"] == "2":
                    chat_history_export_path = get_custom_live_chat_history(
                        get_requested_data_for_week(), cobrowse_agent, CobrowseIO, CobrowseIOInvitedAgentsDetails,
                        CobrowseIOTransferredAgentsLogs, CobrowseChatHistory) 

                    if chat_history_export_path == NO_DATA:
                        return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

                elif requested_data["selected_filter_value"] == "3":
                    chat_history_export_path = get_custom_live_chat_history(
                        get_requested_data_for_month(), cobrowse_agent, CobrowseIO, CobrowseIOInvitedAgentsDetails,
                        CobrowseIOTransferredAgentsLogs, CobrowseChatHistory) 

                    if chat_history_export_path == NO_DATA:
                        return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

                elif requested_data["selected_filter_value"] == "4":

                    today_date = datetime.datetime.today().date()

                    if(today_date - start_date).days > 30:
                        EasyAssistExportDataRequest.objects.create(
                            report_type='live-chat-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                        response["chat_status"] = 300
                        response["chat_export_path"] = "None"
                        response["chat_export_path_exist"] = False
                    else:                        
                        count = CobrowseChatHistory.objects.filter(cobrowse_io__in=cobrowse_io_objs,
                                                                   chat_type="chat_message").count()
                        if count > EXPORTS_UPPER_CAP_LIMIT:
                            EasyAssistExportDataRequest.objects.create(
                                report_type='live-chat-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                            response["chat_status"] = 300
                            response["chat_export_path"] = "None"
                            response["chat_export_path_exist"] = False
                        else:
                            chat_history_export_path = get_custom_live_chat_history(
                                requested_data, cobrowse_agent, CobrowseIO, CobrowseIOInvitedAgentsDetails, 
                                CobrowseIOTransferredAgentsLogs, CobrowseChatHistory, cobrowse_io_objs)
                            
            if requested_data["is_support_history"] and requested_data["is_chat_history"] and response["support_status"] != 300 and response["chat_status"] != 300:
                zip_file_path = "secured_files/EasyAssistApp/support-history/" + str(cobrowse_agent.user.username) + "/support-history" + \
                    uuid.uuid4().hex + ".zip"
            
                zip_obj = ZipFile(zip_file_path, 'w')
                if os.path.exists(export_path) == True:
                    response["export_path_exist"] = True
                    file_path = "/" + export_path
                    access_token_obj = cobrowse_agent.get_access_token_obj()
                    file_access_management_key = create_file_access_management_obj(
                        CobrowsingFileAccessManagement, access_token_obj, file_path)

                    file_name = file_path.split(os.sep)[-1]
                    zip_obj.write(file_path[1:], file_name)
                    response["status"] = 200
            
                if os.path.exists(chat_history_export_path) == True:
                    response["chat_export_path_exist"] = True
                    file_path = "/" + chat_history_export_path
                    access_token_obj = cobrowse_agent.get_access_token_obj()
                    file_access_management_key = create_file_access_management_obj(
                        CobrowsingFileAccessManagement, access_token_obj, file_path)

                    file_name = file_path.split(os.sep)[-1]
                    zip_obj.write(file_path[1:], file_name)
                    response["status"] = 200
                zip_obj.close()

                zip_file_path = "/" + zip_file_path
                zip_file_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=zip_file_path, is_public=False, access_token=access_token_obj)
                response["export_path"] = 'easy-assist/download-file/' + str(zip_file_obj.key)
                
            elif requested_data["is_support_history"] and response["support_status"] != 300:
                response["export_path_exist"] = True
                file_path = "/" + export_path
                access_token_obj = cobrowse_agent.get_access_token_obj()
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)
                response["export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["support_status"] = 200
                
            elif requested_data["is_chat_history"] and response["chat_status"] != 300:
                response["chat_export_path_exist"] = True
                file_path = "/" + chat_history_export_path
                access_token_obj = cobrowse_agent.get_access_token_obj()
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)
                response["chat_export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["chat_status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportSalesSupportHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

ExportSalesSupportHistory = ExportSalesSupportHistoryAPI.as_view()


def UnattendedLeadsDetails(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        active_agent = get_active_agent_obj(request, CobrowseAgent)
        access_token_obj = active_agent.get_access_token_obj()

        agent_objs = [active_agent]
        supervisor_objs = []

        if active_agent.role in ["admin", "admin_ally"]:
            agent_objs = get_list_agents_under_admin(
                active_agent, is_active=None, is_account_active=None)
            supervisor_objs = active_agent.agents.filter(role="supervisor")
        elif active_agent.role == "supervisor":
            agent_objs = list(active_agent.agents.all())

        cobrowse_io_objs = CobrowseIO.objects.filter(
            is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_lead_manually_converted=False).filter(
            agent__in=agent_objs).filter(
            Q(cobrowsing_start_datetime=None)).filter(
            ~Q(allow_agent_cobrowse="false")).filter(session_archived_cause="UNATTENDED")

        is_unattended_leads_empty = False
        if cobrowse_io_objs.count() == 0:
            is_unattended_leads_empty = True

        is_filter_applied = False
        if "startdate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                request_datetime__date__gte=datetime_start)
            is_filter_applied = True

        if "enddate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                request_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if "title" in request.GET:
            title = request.GET.getlist("title")

            cobrowse_io_objs = cobrowse_io_objs.filter(title__in=title)
            is_filter_applied = True

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")
            selected_agents = CobrowseAgent.objects.filter(
                user__username__in=agent_email)
            cobrowse_io_objs = cobrowse_io_objs.filter(
                agent__in=selected_agents)
            is_filter_applied = True

        if "supervisor" in request.GET:
            supervisor_email_id_list = request.GET.getlist("supervisor")
            selected_agents = []
            for agent_email_id in supervisor_email_id_list:
                selected_supervisor = active_agent.agents.filter(
                    user__username=agent_email_id).first()
                selected_agents += list(selected_supervisor.agents.all())
            cobrowse_io_objs = cobrowse_io_objs.filter(
                agent__in=selected_agents)
            is_filter_applied = True

        if "lead-type" in request.GET:
            lead_type = request.GET.getlist("lead-type")[0]
            lead_type = remo_html_from_string(lead_type)
            if lead_type == "Outbound":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_lead=True)
                is_filter_applied = True
            elif lead_type == "Reverse":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_reverse_cobrowsing=True)
                is_filter_applied = True
            elif lead_type == "Drop Link":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_droplink_lead=True)
                is_filter_applied = True
            elif lead_type == "Modified Inbound":
                cobrowse_io_objs = cobrowse_io_objs.filter(cobrowsing_type="modified-inbound")
                is_filter_applied = True
            else:
                cobrowse_io_objs = cobrowse_io_objs.filter(is_lead=False, is_reverse_cobrowsing=False, is_droplink_lead=False).filter(
                    ~Q(cobrowsing_type__in=["outbound-proxy-cobrowsing", "modified-inbound"]))
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
            active_agent, CobrowseIO)

        agent_comments_dict = get_cobrowseio_agent_comments(
            cobrowse_io_objs, CobrowseAgent, CobrowseIO, CobrowseAgentComment)

        console_color = access_token_obj.get_cobrowsing_console_theme_color()

        if console_color == None:
            console_color = {}
            console_color["hex"] = "#2755cb"

        predefined_remarks = access_token_obj.predefined_remarks
        try:
            predefined_remarks = json.loads(predefined_remarks)
        except Exception:
            predefined_remarks = []

        predefined_remarks_with_buttons = access_token_obj.predefined_remarks_with_buttons
        if len(predefined_remarks_with_buttons) == 0:
            predefined_remarks_with_buttons = []
        else:
            predefined_remarks_with_buttons = predefined_remarks_with_buttons.split(
                ',')

        total_rows_per_pages = 20
        total_cobrowse_objs = len(cobrowse_io_objs)
        paginator = Paginator(
            cobrowse_io_objs, total_rows_per_pages)
        page = request.GET.get('page')

        try:
            cobrowse_io_objs = paginator.page(page)
        except PageNotAnInteger:
            cobrowse_io_objs = paginator.page(1)
        except EmptyPage:
            cobrowse_io_objs = paginator.page(paginator.num_pages)

        if page != None:
            start_point = total_rows_per_pages * (int(page) - 1) + 1
            end_point = min(total_rows_per_pages *
                            int(page), total_cobrowse_objs)
            if start_point > end_point:
                start_point = max(end_point - len(cobrowse_io_objs) + 1, 1)
        else:
            start_point = 1
            end_point = min(total_rows_per_pages, total_cobrowse_objs)

        return render(request, "EasyAssistApp/sales_unattended_leads_detail.html", {
            "is_filter_applied": is_filter_applied,
            "cobrowse_io_objs": cobrowse_io_objs,
            "cobrowse_agent": active_agent,
            "access_token_obj": access_token_obj,
            "agents": agent_objs,
            "title_list": title_list,
            "start_point": start_point,
            "end_point": end_point,
            "total_cobrowse_objs": total_cobrowse_objs,
            "is_unattended_leads_empty": is_unattended_leads_empty,
            "supervisors": supervisor_objs,
            "predefined_remarks": predefined_remarks,
            "predefined_remarks_with_buttons": predefined_remarks_with_buttons,
            "agent_comments_dict": agent_comments_dict,
            "console_color": console_color,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error UnattendedLeadsDetails %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(INVALID_ACCESS_CONSTANT)


def DeclinedLeadsDetails(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        active_agent = get_active_agent_obj(request, CobrowseAgent)
        access_token_obj = active_agent.get_access_token_obj()

        agent_objs = [active_agent]
        supervisor_objs = []

        if active_agent.role in ["admin", "admin_ally"]:
            agent_objs = get_list_agents_under_admin(
                active_agent, is_active=None, is_account_active=None)
            supervisor_objs = active_agent.agents.filter(role="supervisor")
        elif active_agent.role == "supervisor":
            agent_objs = list(active_agent.agents.all())

        cobrowse_io_objs = CobrowseIO.objects.filter(
            is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True).filter(
            agent__in=agent_objs).filter(
            Q(cobrowsing_start_datetime=None)).filter(
            allow_agent_cobrowse="false")

        is_declined_leads_empty = False
        if cobrowse_io_objs.count() == 0:
            is_declined_leads_empty = True

        is_filter_applied = False
        if "startdate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                request_datetime__date__gte=datetime_start)
            is_filter_applied = True

        if "enddate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                request_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if "title" in request.GET:
            title = request.GET.getlist("title")
            title = remo_html_from_string(title)
            cobrowse_io_objs = cobrowse_io_objs.filter(title__in=title)
            is_filter_applied = True

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")

            selected_agents = CobrowseAgent.objects.filter(
                user__username__in=agent_email)
            cobrowse_io_objs = cobrowse_io_objs.filter(
                agent__in=selected_agents)
            is_filter_applied = True

        if "supervisor" in request.GET:
            supervisor_email_id_list = request.GET.getlist("supervisor")
            selected_agents = []
            for agent_email_id in supervisor_email_id_list:
                selected_supervisor = active_agent.agents.filter(
                    user__username=agent_email_id).first()
                selected_agents += list(selected_supervisor.agents.all())
            cobrowse_io_objs = cobrowse_io_objs.filter(
                agent__in=selected_agents)
            is_filter_applied = True

        if "lead-type" in request.GET:
            lead_type = request.GET.getlist("lead-type")[0]
            lead_type = remo_html_from_string(lead_type)
            if lead_type == "Outbound":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_lead=True)
                is_filter_applied = True
            elif lead_type == "Reverse":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_reverse_cobrowsing=True)
                is_filter_applied = True
            elif lead_type == "Drop Link":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_droplink_lead=True)
                is_filter_applied = True
            elif lead_type == "Modified Inbound":
                cobrowse_io_objs = cobrowse_io_objs.filter(cobrowsing_type="modified-inbound")
                is_filter_applied = True
            else:
                cobrowse_io_objs = cobrowse_io_objs.filter(is_lead=False, is_reverse_cobrowsing=False, is_droplink_lead=False).filter(
                    ~Q(cobrowsing_type__in=["outbound-proxy-cobrowsing", "modified-inbound"]))
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
            active_agent, CobrowseIO)

        total_rows_per_pages = 20
        total_cobrowse_objs = len(cobrowse_io_objs)
        paginator = Paginator(
            cobrowse_io_objs, total_rows_per_pages)
        page = request.GET.get('page')

        try:
            cobrowse_io_objs = paginator.page(page)
        except PageNotAnInteger:
            cobrowse_io_objs = paginator.page(1)
        except EmptyPage:
            cobrowse_io_objs = paginator.page(paginator.num_pages)

        if page != None:
            start_point = total_rows_per_pages * (int(page) - 1) + 1
            end_point = min(total_rows_per_pages *
                            int(page), total_cobrowse_objs)
            if start_point > end_point:
                start_point = max(end_point - len(cobrowse_io_objs) + 1, 1)
        else:
            start_point = 1
            end_point = min(total_rows_per_pages, total_cobrowse_objs)

        return render(request, "EasyAssistApp/sales_declined_leads_details.html", {
            "is_filter_applied": is_filter_applied,
            "cobrowse_io_objs": cobrowse_io_objs,
            "cobrowse_agent": active_agent,
            "access_token_obj": access_token_obj,
            "agents": agent_objs,
            "title_list": title_list,
            "start_point": start_point,
            "end_point": end_point,
            "total_cobrowse_objs": total_cobrowse_objs,
            "is_declined_leads_empty": is_declined_leads_empty,
            "supervisors": supervisor_objs,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error DeclinedLeadsDetails %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(INVALID_ACCESS_CONSTANT)


def FollowUpLeadsDetails(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        active_agent = get_active_agent_obj(request, CobrowseAgent)

        access_token_obj = active_agent.get_access_token_obj()

        agent_objs = [active_agent]

        if active_agent.role in ["admin", "admin_ally"]:
            agent_objs = get_list_agents_under_admin(
                active_agent, is_active=None, is_account_active=None)
        elif active_agent.role == "supervisor":
            agent_objs = list(active_agent.agents.all())

        cobrowse_io_objs = CobrowseIO.objects.filter(
            access_token=access_token_obj, is_test=False, request_datetime__date__gte=access_token_obj.go_live_date,
            agent__in=agent_objs, is_archived=True, is_lead=False, session_archived_cause__in=["UNASSIGNED", "FOLLOWUP"],
            is_lead_manually_converted=False)

        is_followup_leads_empty = False
        if cobrowse_io_objs.count() == 0:
            is_followup_leads_empty = True

        is_filter_applied = False
        if "startdate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                request_datetime__date__gte=datetime_start)
            is_filter_applied = True

        if "enddate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                request_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if "title" in request.GET:
            title = request.GET.getlist("title")
            title = remo_html_from_string(title)
            cobrowse_io_objs = cobrowse_io_objs.filter(title__in=title)
            is_filter_applied = True

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")
            selected_agents = CobrowseAgent.objects.filter(
                user__username__in=agent_email)
            cobrowse_io_objs = cobrowse_io_objs.filter(
                agent__in=selected_agents)
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
            active_agent, CobrowseIO)

        console_color = access_token_obj.get_cobrowsing_console_theme_color()

        if console_color == None:
            console_color = {}
            console_color["hex"] = "#2755cb"

        predefined_remarks = access_token_obj.predefined_remarks
        try:
            predefined_remarks = json.loads(predefined_remarks)
        except Exception:
            predefined_remarks = []

        predefined_remarks_with_buttons = access_token_obj.predefined_remarks_with_buttons
        if len(predefined_remarks_with_buttons) == 0:
            predefined_remarks_with_buttons = []
        else:
            predefined_remarks_with_buttons = predefined_remarks_with_buttons.split(
                ',')

        total_rows_per_pages = 20
        total_cobrowse_objs = len(cobrowse_io_objs)
        paginator = Paginator(
            cobrowse_io_objs, total_rows_per_pages)
        page = request.GET.get('page')

        try:
            cobrowse_io_objs = paginator.page(page)
        except PageNotAnInteger:
            cobrowse_io_objs = paginator.page(1)
        except EmptyPage:
            cobrowse_io_objs = paginator.page(paginator.num_pages)

        if page != None:
            start_point = total_rows_per_pages * (int(page) - 1) + 1
            end_point = min(total_rows_per_pages *
                            int(page), total_cobrowse_objs)
            if start_point > end_point:
                start_point = max(end_point - len(cobrowse_io_objs) + 1, 1)
        else:
            start_point = 1
            end_point = min(total_rows_per_pages, total_cobrowse_objs)

        return render(request, "EasyAssistApp/sales_followup_leads_details.html", {
            "is_filter_applied": is_filter_applied,
            "cobrowse_io_objs": cobrowse_io_objs,
            "cobrowse_agent": active_agent,
            "agents": agent_objs,
            "access_token_obj": access_token_obj,
            "title_list": title_list,
            "start_point": start_point,
            "end_point": end_point,
            "total_cobrowse_objs": total_cobrowse_objs,
            "is_followup_leads_empty": is_followup_leads_empty,
            "predefined_remarks": predefined_remarks,
            "predefined_remarks_with_buttons": predefined_remarks_with_buttons,
            "console_color": console_color,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error FollowUpLeadsDetails %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(INVALID_ACCESS_CONSTANT)


def ManuallyConvertedLeadsDetails(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        active_agent = get_active_agent_obj(request, CobrowseAgent)
        access_token_obj = active_agent.get_access_token_obj()

        agent_objs = [active_agent]
        supervisor_objs = []

        if active_agent.role in ["admin", "admin_ally"]:
            agent_objs = get_list_agents_under_admin(
                active_agent, is_active=None, is_account_active=None)
            supervisor_objs = active_agent.agents.filter(role="supervisor")
        elif active_agent.role == "supervisor":
            agent_objs = list(active_agent.agents.all())

        session_archive_cause = ["UNATTENDED"]
        if access_token_obj.enable_followup_leads_tab:
            session_archive_cause = ["UNASSIGNED", "FOLLOWUP", "UNATTENDED"]

        cobrowse_io_objs = CobrowseIO.objects.filter(
            access_token=access_token_obj, is_test=False, request_datetime__date__gte=access_token_obj.go_live_date, agent__in=agent_objs,
            is_archived=True, cobrowsing_start_datetime=None, session_archived_cause__in=session_archive_cause, 
            is_lead_manually_converted=True)

        is_manually_converted_leads_empty = False
        if cobrowse_io_objs.count() == 0:
            is_manually_converted_leads_empty = True

        is_filter_applied = False
        if "startdate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                request_datetime__date__gte=datetime_start)
            is_filter_applied = True

        if "enddate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()
            cobrowse_io_objs = cobrowse_io_objs.filter(
                request_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if "title" in request.GET:
            title = request.GET.getlist("title")

            cobrowse_io_objs = cobrowse_io_objs.filter(title__in=title)
            is_filter_applied = True

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")
            selected_agents = CobrowseAgent.objects.filter(
                user__username__in=agent_email)
            cobrowse_io_objs = cobrowse_io_objs.filter(
                agent__in=selected_agents)
            is_filter_applied = True

        if "status" in request.GET:
            session_status = request.GET.getlist("status")[0]
            session_status = remo_html_from_string(session_status)
            if session_status == "Converted":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_helpful=True)
                is_filter_applied = True
            elif session_status == "Not Converted":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_helpful=False)
                is_filter_applied = True

        if "lead-type" in request.GET:
            lead_type = request.GET.getlist("lead-type")[0]
            lead_type = remo_html_from_string(lead_type)
            if lead_type == "Outbound":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_lead=True)
                is_filter_applied = True
            elif lead_type == "Reverse":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_reverse_cobrowsing=True)
                is_filter_applied = True
            elif lead_type == "Drop Link":
                cobrowse_io_objs = cobrowse_io_objs.filter(is_droplink_lead=True)
                is_filter_applied = True
            elif lead_type == "Modified Inbound":
                cobrowse_io_objs = cobrowse_io_objs.filter(cobrowsing_type="modified-inbound")
                is_filter_applied = True
            else:
                cobrowse_io_objs = cobrowse_io_objs.filter(is_lead=False, is_reverse_cobrowsing=False, is_droplink_lead=False).filter(
                    ~Q(cobrowsing_type__in=["outbound-proxy-cobrowsing", "modified-inbound"]))
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
            active_agent, CobrowseIO)

        agent_comments_dict = cobrowseio_agent_comments_manually_converted_leads(
            cobrowse_io_objs, CobrowseAgentComment)

        console_color = access_token_obj.get_cobrowsing_console_theme_color()

        total_rows_per_pages = 20
        total_cobrowse_objs = len(cobrowse_io_objs)
        paginator = Paginator(
            cobrowse_io_objs, total_rows_per_pages)
        page = request.GET.get('page')

        try:
            cobrowse_io_objs = paginator.page(page)
        except PageNotAnInteger:
            cobrowse_io_objs = paginator.page(1)
        except EmptyPage:
            cobrowse_io_objs = paginator.page(paginator.num_pages)

        if page != None:
            start_point = total_rows_per_pages * (int(page) - 1) + 1
            end_point = min(total_rows_per_pages *
                            int(page), total_cobrowse_objs)
            if start_point > end_point:
                start_point = max(end_point - len(cobrowse_io_objs) + 1, 1)
        else:
            start_point = 1
            end_point = min(total_rows_per_pages, total_cobrowse_objs)

        return render(request, "EasyAssistApp/sales_manually_converted_leads_details.html", {
            "is_filter_applied": is_filter_applied,
            "cobrowse_io_objs": cobrowse_io_objs,
            "cobrowse_agent": active_agent,
            "access_token_obj": access_token_obj,
            "agents": agent_objs,
            "title_list": title_list,
            "start_point": start_point,
            "end_point": end_point,
            "total_cobrowse_objs": total_cobrowse_objs,
            "is_manually_converted_leads_empty": is_manually_converted_leads_empty,
            "supervisors": supervisor_objs,
            "agent_comments_dict": agent_comments_dict,
            "console_color": console_color,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ManuallyConvertedLeadsDetails %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(INVALID_ACCESS_CONSTANT)


class ExportManuallyConvertedLeadsAPI(APIView):

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
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

            if requested_data["selected_filter_value"] == "1":

                export_path = get_custom_manually_converted_leads_history(
                    get_requested_data_for_daily(), cobrowse_agent, CobrowseIO)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "2":

                export_path = get_custom_manually_converted_leads_history(
                    get_requested_data_for_week(), cobrowse_agent, CobrowseIO)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "3":

                export_path = get_custom_manually_converted_leads_history(
                    get_requested_data_for_month(), cobrowse_agent, CobrowseIO)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "4":

                date_format = DATE_TIME_FORMAT
                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()
                today_date = datetime.datetime.today().date()

                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='manually-converted-leads', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
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
                    session_archive_cause = ["UNATTENDED"]
                    if access_token_obj.enable_followup_leads_tab:
                        session_archive_cause = ["UNASSIGNED", "FOLLOWUP", "UNATTENDED"]

                    cobrowse_io_objs = CobrowseIO.objects.filter(
                        access_token=access_token_obj, is_test=False, request_datetime__date__gte=access_token_obj.go_live_date, agent__in=agent_objs,
                        is_archived=True, cobrowsing_start_datetime=None, session_archived_cause__in=session_archive_cause, is_lead_manually_converted=True).filter(
                        request_datetime__date__gte=start_date, request_datetime__date__lte=end_date)

                    if not cobrowse_io_objs:
                        return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))
                    
                    if cobrowse_io_objs.count() > EXPORTS_UPPER_CAP_LIMIT:

                        EasyAssistExportDataRequest.objects.create(
                            report_type='manually-converted-leads', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                        response["status"] = 300
                        response["export_path"] = "None"
                        response["export_path_exist"] = False
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                    else:
                        export_path = get_custom_manually_converted_leads_history(
                            requested_data, cobrowse_agent, CobrowseIO, cobrowse_io_objs)

            if os.path.exists(export_path) == True:
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
            logger.error("Error ExportManuallyConvertedLeadsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


ExportManuallyConvertedLeads = ExportManuallyConvertedLeadsAPI.as_view()


class ExportUnattentedLeadsDetalsAPI(APIView):

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
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

            if requested_data["selected_filter_value"] == "1":

                export_path = get_custom_unattended_leads_history(
                    get_requested_data_for_daily(), cobrowse_agent, CobrowseIO)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "2":

                export_path = get_custom_unattended_leads_history(
                    get_requested_data_for_week(), cobrowse_agent, CobrowseIO)
                
                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "3":

                export_path = get_custom_unattended_leads_history(
                    get_requested_data_for_month(), cobrowse_agent, CobrowseIO)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "4":

                date_format = DATE_TIME_FORMAT
                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()
                today_date = datetime.datetime.today().date()

                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='unattended-lead-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                else:
                    end_date = datetime.datetime.strptime(
                        requested_data["enddate"], date_format).date()             

                    agents = get_list_agents_under_admin(
                        cobrowse_agent, is_active=None, is_account_active=None)

                    access_token_obj = cobrowse_agent.get_access_token_obj()
                    
                    cobrowse_io_objs = CobrowseIO.objects.filter(
                        is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date,
                        is_archived=True, is_lead_manually_converted=False).filter(
                        request_datetime__date__gte=start_date, request_datetime__date__lte=end_date, agent__in=agents).filter(
                        Q(cobrowsing_start_datetime=None)).filter(~Q(allow_agent_cobrowse="false")).filter(session_archived_cause="UNATTENDED")
                    
                    if not cobrowse_io_objs:
                        return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))
                        
                    if cobrowse_io_objs.count() > EXPORTS_UPPER_CAP_LIMIT:
                        EasyAssistExportDataRequest.objects.create(
                            report_type='unattended-lead-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                        response["status"] = 300
                        response["export_path"] = "None"
                        response["export_path_exist"] = False
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                    else:
                        export_path = get_custom_unattended_leads_history(
                            requested_data, cobrowse_agent, CobrowseIO, cobrowse_io_objs)

            if os.path.exists(export_path) == True:

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
            logger.error("Error ExportUnattentedLeadsDetalsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


ExportUnattentedLeadsDetals = ExportUnattentedLeadsDetalsAPI.as_view()


class ExportFollowUpLeadsDetalsAPI(APIView):

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
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

            if requested_data["selected_filter_value"] == "1":

                export_path = get_custom_followup_leads_history(
                    get_requested_data_for_daily(), cobrowse_agent, CobrowseIO)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "2":

                export_path = get_custom_followup_leads_history(
                    get_requested_data_for_week(), cobrowse_agent, CobrowseIO)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "3":

                export_path = get_custom_followup_leads_history(
                    get_requested_data_for_month(), cobrowse_agent, CobrowseIO)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "4":

                date_format = DATE_TIME_FORMAT
                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()
                today_date = datetime.datetime.today().date()

                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='followup-lead-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
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
                    cobrowse_io_objs = CobrowseIO.objects.filter(
                        access_token=access_token_obj, is_test=False, request_datetime__date__gte=access_token_obj.go_live_date,
                        agent__in=agent_objs, is_archived=True, is_lead=False, session_archived_cause__in=["UNASSIGNED", "FOLLOWUP"], is_lead_manually_converted=False).filter(
                            request_datetime__date__gte=start_date, request_datetime__date__lte=end_date)

                    if not cobrowse_io_objs:
                        return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

                    if cobrowse_io_objs.count() > EXPORTS_UPPER_CAP_LIMIT:
                        EasyAssistExportDataRequest.objects.create(
                            report_type='followup-lead-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                        response["status"] = 300
                        response["export_path"] = "None"
                        response["export_path_exist"] = False
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                    else:
                        export_path = get_custom_followup_leads_history(
                            requested_data, cobrowse_agent, CobrowseIO, cobrowse_io_objs)

            if os.path.exists(export_path) == True:

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
            logger.error("Error ExportFollowUpLeadsDetalsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


ExportFollowUpLeadsDetals = ExportFollowUpLeadsDetalsAPI.as_view()


class ExportDeclinedLeadsDetalsAPI(APIView):

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
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

            if requested_data["selected_filter_value"] == "1":

                export_path = get_custom_declined_leads_history(
                    get_requested_data_for_daily(), cobrowse_agent, CobrowseIO)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "2":

                export_path = get_custom_declined_leads_history(
                    get_requested_data_for_week(), cobrowse_agent, CobrowseIO)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "3":

                export_path = get_custom_declined_leads_history(
                    get_requested_data_for_month(), cobrowse_agent, CobrowseIO)

                if export_path == NO_DATA:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "4":

                date_format = DATE_TIME_FORMAT
                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()
                today_date = datetime.datetime.today().date()

                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='declined-lead-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                else:
                    end_date = datetime.datetime.strptime(
                        requested_data["enddate"], date_format).date()
                    agents = get_list_agents_under_admin(
                        cobrowse_agent, is_active=None, is_account_active=None)
                    time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=5)
                    access_token_obj = cobrowse_agent.get_access_token_obj()

                    cobrowse_io_objs = CobrowseIO.objects.filter(
                        is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True).filter(
                        request_datetime__lte=time_threshold, request_datetime__date__gte=start_date, request_datetime__date__lte=end_date).filter(
                        agent__in=agents).filter(Q(cobrowsing_start_datetime=None)).filter(allow_agent_cobrowse="false")
                    
                    if not cobrowse_io_objs:
                        return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))
                    
                    if cobrowse_io_objs.count() > EXPORTS_UPPER_CAP_LIMIT:
                        EasyAssistExportDataRequest.objects.create(
                            report_type='declined-lead-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                        response["status"] = 300
                        response["export_path"] = "None"
                        response["export_path_exist"] = False
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                    else:
                        export_path = get_custom_declined_leads_history(
                            requested_data, cobrowse_agent, CobrowseIO, cobrowse_io_objs)

            if os.path.exists(export_path) == True:

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
            logger.error("Error ExportDeclinedLeadsDetalsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


ExportDeclinedLeadsDetals = ExportDeclinedLeadsDetalsAPI.as_view()


class ExportMeetingSupportHistoryAPI(APIView):

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
            export_path = None

            if cobrowse_agent.role == "agent":
                response["export_path"] = "None"
                response["status"] = 401
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

            if requested_data["selected_filter_value"] == "1":

                export_path = get_custom_meeting_support_history(
                    get_requested_data_for_daily(), cobrowse_agent, CobrowseVideoConferencing, CobrowseVideoAuditTrail, CobrowsingFileAccessManagement)

                if not export_path:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "2":

                export_path = get_custom_meeting_support_history(
                    get_requested_data_for_week(), cobrowse_agent, CobrowseVideoConferencing, CobrowseVideoAuditTrail, CobrowsingFileAccessManagement)

                if not export_path:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "3":

                export_path = get_custom_meeting_support_history(
                    get_requested_data_for_month(), cobrowse_agent, CobrowseVideoConferencing, CobrowseVideoAuditTrail, CobrowsingFileAccessManagement)

                if not export_path:
                    return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

            elif requested_data["selected_filter_value"] == "4":
                date_format = DATE_TIME_FORMAT
                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()
                today_date = datetime.datetime.today().date()
                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='meeting-support-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                else:
                    end_date = datetime.datetime.strptime(
                        requested_data["enddate"], date_format).date()
                    agents = get_list_agents_under_admin(
                        cobrowse_agent, is_active=None, is_account_active=None)
                    access_token_obj = cobrowse_agent.get_access_token_obj()
                    cobrowse_video_objs = CobrowseVideoConferencing.objects.filter(
                        agent__in=agents, meeting_start_date__gte=start_date, meeting_start_date__lte=end_date)

                    if cobrowse_agent.role == "supervisor" and (access_token_obj.enable_invite_agent_in_meeting or access_token_obj.enable_invite_agent_in_cobrowsing):
                        invited_agent_video_audit_objs = CobrowseVideoAuditTrail.objects.filter(
                            meeting_agents__in=agents)
                        if invited_agent_video_audit_objs:
                            invited_session_ids = []
                            for invited_agent_video_audit_obj in invited_agent_video_audit_objs:
                                invited_session_ids.append(
                                    invited_agent_video_audit_obj.cobrowse_video.meeting_id)
                            invited_sessions_cobrowse_objs = CobrowseVideoConferencing.objects.filter(
                                meeting_id__in=invited_session_ids, meeting_start_date__gte=start_date, meeting_start_date__lte=end_date)
                            cobrowse_video_objs = cobrowse_video_objs | invited_sessions_cobrowse_objs

                    video_meeting_audit_trail_objs = CobrowseVideoAuditTrail.objects.filter(
                        cobrowse_video__in=cobrowse_video_objs)

                    if not video_meeting_audit_trail_objs:
                        return Response(data=get_encrypted_no_data_response_packet(custom_encrypt_obj))

                    if video_meeting_audit_trail_objs.count() > EXPORTS_UPPER_CAP_LIMIT:
                        EasyAssistExportDataRequest.objects.create(
                            report_type='meeting-support-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                        response["status"] = 300
                        response["export_path"] = "None"
                        response["export_path_exist"] = False
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                    else:
                        export_path = get_custom_meeting_support_history(
                            requested_data, cobrowse_agent, CobrowseVideoConferencing, CobrowseVideoAuditTrail, CobrowsingFileAccessManagement, video_meeting_audit_trail_objs)

            if os.path.exists(export_path) == True:

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
            logger.error("Error ExportMeetingSupportHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


ExportMeetingSupportHistory = ExportMeetingSupportHistoryAPI.as_view()


class ExportScreenRecordingHistoryAPI(APIView):

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

            if requested_data["selected_filter_value"] == "1":

                export_path = get_custom_screen_recording_history(
                    get_requested_data_for_daily(), cobrowse_agent, CobrowseScreenRecordingAuditTrail)

            elif requested_data["selected_filter_value"] == "2":

                export_path = get_custom_screen_recording_history(
                    get_requested_data_for_week(), cobrowse_agent, CobrowseScreenRecordingAuditTrail)

            elif requested_data["selected_filter_value"] == "3":

                export_path = get_custom_screen_recording_history(
                    get_requested_data_for_month(), cobrowse_agent, CobrowseScreenRecordingAuditTrail)

            elif requested_data["selected_filter_value"] == "4":

                date_format = DATE_TIME_FORMAT
                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()
                end_date = datetime.datetime.strptime(
                    requested_data["enddate"], date_format).date()

                today_date = datetime.datetime.today().date()

                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='screen-recording-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                else:
                    agents = get_list_agents_under_admin(
                        cobrowse_agent, is_active=None, is_account_active=None)

                    screen_recording_objs = CobrowseScreenRecordingAuditTrail.objects.filter(
                        agent__in=agents, recording_started__date__gte=start_date, recording_started__date__lte=end_date)

                    if screen_recording_objs.count() > EXPORTS_UPPER_CAP_LIMIT:
                        EasyAssistExportDataRequest.objects.create(
                            report_type='screen-recording-history', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                        response["status"] = 300
                        response["export_path"] = "None"
                        response["export_path_exist"] = False
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)
                    else:
                        export_path = get_custom_screen_recording_history(
                            requested_data, cobrowse_agent, CobrowseScreenRecordingAuditTrail, screen_recording_objs)

            if os.path.exists(export_path) == True:

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
            logger.error("Error ExportScreenRecordingHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportScreenRecordingHistory = ExportScreenRecordingHistoryAPI.as_view()


def SalesAnalyticsDashboard(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        DEFAULT_ANALYTICS_START_DATETIME = (
            datetime.datetime.today() - datetime.timedelta(7)).date()

        DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        access_token_obj = cobrowse_agent.get_access_token_obj()

        if cobrowse_agent.show_static_analytics:
            return render(request, "EasyAssistApp/static-analytics.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
            })
        else:
            return render(request, "EasyAssistApp/analytics.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
            })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAnalyticsDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


class ExportAuditTrailDetalsAPI(APIView):

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

            if requested_data["selected_filter_value"] == "1":
                export_path = get_audit_trail_dump(
                    get_requested_data_for_daily(), cobrowse_agent, CobrowsingAuditTrail)

            elif requested_data["selected_filter_value"] == "2":

                export_path = get_audit_trail_dump(
                    get_requested_data_for_week(), cobrowse_agent, CobrowsingAuditTrail)

            elif requested_data["selected_filter_value"] == "3":

                export_path = get_audit_trail_dump(
                    get_requested_data_for_month(), cobrowse_agent, CobrowsingAuditTrail)

            elif requested_data["selected_filter_value"] == "4":

                date_format = DATE_TIME_FORMAT
                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()
                end_date = datetime.datetime.strptime(
                    requested_data["enddate"], date_format).date()

                today_date = datetime.datetime.today().date()

                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='audit-trail', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                else:
                    agents = get_list_agents_under_admin(
                        cobrowse_agent, is_active=None, is_account_active=None)
                        
                    agents += cobrowse_agent.agents.all().filter(
                        role="supervisor")

                    if cobrowse_agent not in agents:
                        agents += [cobrowse_agent]

                    audit_trail_objs = CobrowsingAuditTrail.objects.filter(
                        agent__in=agents, datetime__date__gte=start_date, datetime__date__lte=end_date)

                    if audit_trail_objs.count() > EXPORTS_UPPER_CAP_LIMIT:
                        EasyAssistExportDataRequest.objects.create(
                            report_type='audit-trail', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                        response["status"] = 300
                        response["export_path"] = "None"
                        response["export_path_exist"] = False
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)
                    else:
                        export_path = get_audit_trail_dump(
                            requested_data, cobrowse_agent, CobrowsingAuditTrail, audit_trail_objs)

            if os.path.exists(export_path) == True:

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
            logger.error("Error ExportAuditTrailDetalsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportAuditTrailDetals = ExportAuditTrailDetalsAPI.as_view()


class ExportAgentAuditTrailDetalsAPI(APIView):

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

            if requested_data["selected_filter_value"] == "1":

                export_path = get_agent_audit_trail_dump(
                    get_requested_data_for_daily(), cobrowse_agent, CobrowsingAuditTrail, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail)

            elif requested_data["selected_filter_value"] == "2":

                export_path = get_agent_audit_trail_dump(
                    get_requested_data_for_week(), cobrowse_agent, CobrowsingAuditTrail, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail)

            elif requested_data["selected_filter_value"] == "3":

                export_path = get_agent_audit_trail_dump(
                    get_requested_data_for_month(), cobrowse_agent, CobrowsingAuditTrail, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail)

            elif requested_data["selected_filter_value"] == "4":

                date_format = DATE_TIME_FORMAT
                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()
                end_date = datetime.datetime.strptime(
                    requested_data["enddate"], date_format).date()

                today_date = datetime.datetime.today().date()

                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='agent-audit-trail', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                else:
                    agents = get_agents_under_cobrowse_agent(cobrowse_agent)
                    agent_audit_trail_list = CobrowsingAuditTrail.objects.filter(
                        agent__in=agents, action__in=[COBROWSING_LOGIN_ACTION, COBROWSING_LOGOUT_ACTION], datetime__date__gte=start_date, datetime__date__lte=end_date)

                    if agent_audit_trail_list.count() > EXPORTS_UPPER_CAP_LIMIT:
                        EasyAssistExportDataRequest.objects.create(
                            report_type='agent-audit-trail', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                        response["status"] = 300
                        response["export_path"] = "None"
                        response["export_path_exist"] = False
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)
                    else:
                        export_path = get_agent_audit_trail_dump(
                            requested_data, cobrowse_agent, CobrowsingAuditTrail, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail, agent_audit_trail_list)

            if os.path.exists(export_path) == True:

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
            logger.error("Error ExportAgentAuditTrailDetalsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportAgentAuditTrailDetals = ExportAgentAuditTrailDetalsAPI.as_view()


class ExportAgentOnlineAuditTrailDetalsAPI(APIView):

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

            date_format = DATE_TIME_FORMAT

            if requested_data["selected_filter_value"] == "1":

                start_date = datetime.datetime.now() - datetime.timedelta(days=1)
                start_date = start_date.strftime(date_format)
                end_date = start_date

                requested_data = {
                    "startdate": start_date,
                    "enddate": end_date,
                }

                export_path = get_agent_online_audit_trail_dump(
                    requested_data, cobrowse_agent, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail)

            elif requested_data["selected_filter_value"] == "2":

                start_date = datetime.datetime.now() - datetime.timedelta(days=7)
                start_date = start_date.strftime(date_format)
                end_date = datetime.datetime.now() - datetime.timedelta(days=1)
                end_date = end_date.strftime(date_format)

                requested_data = {
                    "startdate": start_date,
                    "enddate": end_date,
                }

                export_path = get_agent_online_audit_trail_dump(
                    requested_data, cobrowse_agent, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail)

            elif requested_data["selected_filter_value"] == "3":

                start_date = datetime.datetime.now() - datetime.timedelta(days=30)
                start_date = start_date.strftime(date_format)
                end_date = datetime.datetime.now() - datetime.timedelta(days=1)
                end_date = end_date.strftime(date_format)

                requested_data = {
                    "startdate": start_date,
                    "enddate": end_date,
                }

                export_path = get_agent_online_audit_trail_dump(
                    requested_data, cobrowse_agent, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail)

            elif requested_data["selected_filter_value"] == "4":

                start_date = datetime.datetime.strptime(
                    requested_data["startdate"], date_format).date()
                end_date = datetime.datetime.strptime(
                    requested_data["enddate"], date_format).date()

                today_date = datetime.datetime.today().date()

                if(today_date - start_date).days > 30:
                    EasyAssistExportDataRequest.objects.create(
                        report_type='agent-online-audit-trail', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                    response["status"] = 300
                    response["export_path"] = "None"
                    response["export_path_exist"] = False
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                else:
                    agents = get_agents_under_cobrowse_agent(cobrowse_agent)

                    agent_online_audit_trail_objs = CobrowseAgentOnlineAuditTrail.objects.filter(
                        agent__in=agents,
                        last_online_start_datetime__date__gte=start_date,
                        last_online_end_datetime__date__lte=end_date)

                    if agent_online_audit_trail_objs.count() > EXPORTS_UPPER_CAP_LIMIT:
                        EasyAssistExportDataRequest.objects.create(
                            report_type='agent-online-audit-trail', agent=cobrowse_agent, filter_param=json.dumps(requested_data))
                        response["status"] = 300
                        response["export_path"] = "None"
                        response["export_path_exist"] = False
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)
                    else:
                        export_path = get_agent_online_audit_trail_dump(
                            requested_data, cobrowse_agent, CobrowseAgentWorkAuditTrail, CobrowseAgentOnlineAuditTrail, agent_online_audit_trail_objs)

            if os.path.exists(export_path) == True:

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
            logger.error("Error ExportAgentOnlineAuditTrailDetalsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportAgentOnlineAuditTrailDetals = ExportAgentOnlineAuditTrailDetalsAPI.as_view()


def SalesAnalyticsOutboundDashboard(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        DEFAULT_ANALYTICS_START_DATETIME = (
            datetime.datetime.today() - datetime.timedelta(7)).date()

        DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        access_token_obj = cobrowse_agent.get_access_token_obj()

        if cobrowse_agent.show_static_analytics:
            return render(request, "EasyAssistApp/analytics_outbound_static.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
            })
        else:
            contains_unique_identifier = 0
            if access_token_obj.search_fields:
                contains_unique_identifier = access_token_obj.search_fields.filter(
                    unique_identifier=True).count()
            return render(request, "EasyAssistApp/analytics_outbound.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME,
                "contains_unique_identifier": contains_unique_identifier,
            })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAnalyticsOutboundDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesGeneralAnalyticsDashboard(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        DEFAULT_ANALYTICS_START_DATETIME = (
            datetime.datetime.today() - datetime.timedelta(7)).date()

        DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        access_token_obj = cobrowse_agent.get_access_token_obj()

        if cobrowse_agent.role == "agent":
            return HttpResponse(status=401)

        if cobrowse_agent.show_static_analytics:
            return render(request, "EasyAssistApp/general_analytics_static.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
            })
        else:
            return render(request, "EasyAssistApp/general_analytics.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
            })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesGeneralAnalyticsDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesReverseAnalyticsDashboard(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        DEFAULT_ANALYTICS_START_DATETIME = (
            datetime.datetime.today() - datetime.timedelta(7)).date()

        DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/analytics_reverse.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
            "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesGeneralAnalyticsDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesAgentProfileSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        cobrowse_agent = get_active_agent_obj(
            request, CobrowseAgent)
        access_token_obj = cobrowse_agent.get_access_token_obj()

        if cobrowse_agent.role != "admin":

            cobrowse_admin = get_admin_from_active_agent(
                cobrowse_agent, CobrowseAgent)

            supported_language = []
            agent_supported_language = []
            for language in cobrowse_admin.supported_language.filter(is_deleted=False).order_by('index'):
                if language in cobrowse_agent.supported_language.all():
                    supported_language.append({
                        "key": language.pk,
                        "value": language.title,
                        "is_selected": True,
                    })
                    agent_supported_language.append(language.title)
                else:
                    supported_language.append({
                        "key": language.pk,
                        "value": language.title,
                        "is_selected": False,
                    })

            product_category = []
            agent_product_category = []
            for product in cobrowse_admin.product_category.filter(is_deleted=False).order_by('index'):
                if product in cobrowse_agent.product_category.all():
                    product_category.append({
                        "key": product.pk,
                        "value": product.title,
                        "is_selected": True,
                    })
                    agent_product_category.append(product.title)
                else:
                    product_category.append({
                        "key": product.pk,
                        "value": product.title,
                        "is_selected": False,
                    })

            supported_language_string = ", ".join(agent_supported_language)
            product_category_string = ", ".join(agent_product_category)

        return render(request, "EasyAssistApp/sales_agent_profile.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "supported_language": supported_language,
            "product_category": product_category,
            "supported_language_string": supported_language_string,
            "product_category_string": product_category_string
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAgentProfileSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesAgentHomeSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        cobrowse_agent = get_active_agent_obj(
            request, CobrowseAgent)
        access_token_obj = cobrowse_agent.get_access_token_obj()

        if cobrowse_agent.role != "admin":
            return render(request, "EasyAssistApp/sales_settings_agent_home.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj
            })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAgentHomeSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesAnalyticsSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        cobrowse_agent = get_active_agent_obj(request, CobrowseAgent)
        access_token_obj = cobrowse_agent.get_access_token_obj()
        current_month = str(datetime.datetime.now().month)
        current_year = str(datetime.datetime.now().year)
        calendar_type = request.GET.get('days')
        selected_month = request.GET.get('month')
        selected_year = request.GET.get('years')
        if selected_month:
            parsed_url = urlparse(request.get_full_path())
            selected_month = parse_qs(parsed_url.query)['month']

            months_list = []
            for month in selected_month:
                months_list.append(month_to_num_dict[month])
        if calendar_type:
            if calendar_type == "Holidays":
                calendar_type = "2"
            else:
                calendar_type = "1"
        else:
            calendar_type = "1"
        if selected_year and selected_month:
            months_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            selected_month = True
        selected_year = current_year if selected_year == None else selected_year
        selected_month = [
            int(current_month)] if selected_month == None else months_list
        if cobrowse_agent.role != "admin":

            cobrowse_admin = get_admin_from_active_agent(
                cobrowse_agent, CobrowseAgent)

            calendar_objs = CobrowseCalendar.objects.filter(created_by=cobrowse_admin, event_type=calendar_type, event_date__year=int(
                selected_year), event_date__month__in=selected_month).order_by('event_date')

            supported_language = []
            agent_supported_language = []
            for language in cobrowse_admin.supported_language.filter(is_deleted=False).order_by('index').iterator():
                if language in cobrowse_agent.supported_language.all():
                    supported_language.append({
                        "key": language.pk,
                        "value": language.title,
                        "is_selected": True,
                    })
                    agent_supported_language.append(language.title)
                else:
                    supported_language.append({
                        "key": language.pk,
                        "value": language.title,
                        "is_selected": False,
                    })

            product_category = []
            agent_product_category = []
            for product in cobrowse_admin.product_category.filter(is_deleted=False).order_by('index').iterator():
                if product in cobrowse_agent.product_category.all():
                    product_category.append({
                        "key": product.pk,
                        "value": product.title,
                        "is_selected": True,
                    })
                    agent_product_category.append(product.title)
                else:
                    product_category.append({
                        "key": product.pk,
                        "value": product.title,
                        "is_selected": False,
                    })

            supported_language_string = ", ".join(agent_supported_language)
            product_category_string = ", ".join(agent_product_category)

            total_rows_per_pages = 31
            page = request.GET.get('page')

            page_object_count, calendar_objs, start_point, end_point = paginate(
                calendar_objs, total_rows_per_pages, page)

            return render(request, "EasyAssistApp/sales_settings_agent_home.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "supported_language": supported_language,
                "product_category": product_category,
                "supported_language_string": supported_language_string,
                "product_category_string": product_category_string,
                "COBROWSING_AGENT_SUPPORT": COBROWSING_AGENT_SUPPORT,
                "calendar_type": calendar_type,
                "selected_month": selected_month,
                "selected_year": selected_year,
                "calendar_objs": calendar_objs,
                "start_point": start_point,
                "end_point": end_point,
                "total_calendar_objs": page_object_count,
                "calendar_created_by": cobrowse_admin
            })
        else:
            return render(request, "EasyAssistApp/sales_settings.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
            })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAnalyticsSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesAdvancedSettingsStatic(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        if cobrowse_agent.role == "admin":
            access_token_objs = CobrowseAccessToken.objects.all()
            return render(request, "EasyAssistApp/sales_advanced_settings_static.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "access_token_objs": access_token_objs,
            })
        else:
            return HttpResponse(INVALID_ACCESS_CONSTANT)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAdvancedSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesAdvancedSettingsAssignTask(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        access_token_objs = CobrowseAccessToken.objects.all()
        return render(request, "EasyAssistApp/sales_advanced_settings_assigntask.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "access_token_objs": access_token_objs,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAdvancedSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesAdvancedSettingsAPIIntegration(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        access_token_objs = CobrowseAccessToken.objects.all()
        return render(request, "EasyAssistApp/sales_advanced_settings_api_integration.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "access_token_objs": access_token_objs,
        })
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAdvancedSettingsAPIIntegration %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesAdvancedSettingsLogs(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        access_token_objs = CobrowseAccessToken.objects.all()
        return render(request, "EasyAssistApp/sales_advanced_settings_logs.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "access_token_objs": access_token_objs,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAdvancedSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesAdvancedSettingsCRM(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')

        access_token_obj = cobrowse_agent.get_access_token_obj()
        return render(request, "EasyAssistApp/sales_advanced_settings_crm.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "auth_token_generation_api_doc": AUTH_TOKEN_GENERATION_API_DOCUMENTATION,
            "cogno_cobrowse_api_docs_links": COBROWSE_API_DOCUMENTS_DOCUMENTATION,
            "cogno_meet_api_docs_links": COGNO_MEET_API_DOCUMENTS_DOCUMENTATION,
            "agent_management_api_docs_links": AGENT_MANAGEMENT_API_DOCUMENTS_DOCUMENTATION,
        })
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAdvancedSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesAccessManagement(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        access_token_obj = cobrowse_agent.get_access_token_obj()

        if cobrowse_agent.role not in ["admin", "supervisor", "admin_ally"]:
            return HttpResponse(status=401)

        supported_language_objs = cobrowse_agent.supported_language.filter(
            is_deleted=False).order_by('index')
        product_category_objs = cobrowse_agent.product_category.filter(
            is_deleted=False).order_by('index')
        agents = cobrowse_agent.agents.filter(role="agent")
        supervisors = cobrowse_agent.agents.filter(role="supervisor")
        admin_allies = cobrowse_agent.agents.filter(role="admin_ally")

        for admin_ally in admin_allies:
            ally_supervisors = admin_ally.agents.filter(role="supervisor")
            supervisors = supervisors | ally_supervisors
        for supervisor in supervisors:
            agents = agents | supervisor.agents.all()
        agents = agents.distinct()
        supervisors = supervisors.distinct()

        agents = agents.order_by('-agent_creation_datetime')
        supervisors = supervisors.order_by('-agent_creation_datetime')
        if cobrowse_agent.show_static_analytics:
            return render(request, "EasyAssistApp/sales_access_management_static.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "agents": agents, "supervisors": supervisors,
                "COBROWSING_AGENT_SUPPORT": COBROWSING_AGENT_SUPPORT,
                "supported_language_objs": supported_language_objs,
                "product_category_objs": product_category_objs,
            })
        return render(request, "EasyAssistApp/sales_access_management.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "agents": agents, "supervisors": supervisors,
            "COBROWSING_AGENT_SUPPORT": COBROWSING_AGENT_SUPPORT,
            "supported_language_objs": supported_language_objs,
            "product_category_objs": product_category_objs,
            "admin_allies": admin_allies,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAccessManagement %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesAuditTrail(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        access_token_obj = cobrowse_agent.get_access_token_obj()
        supervisor_objs = []

        if cobrowse_agent.role in ["admin", "admin_ally"]:
            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None, is_account_active=None)
            supervisor_objs = cobrowse_agent.agents.filter(role="supervisor")
            agents += cobrowse_agent.agents.all().filter(
                role="supervisor")
        elif cobrowse_agent.role == "supervisor":
            agents = list(cobrowse_agent.agents.all())

        else:
            return HttpResponse(status=401)

        if cobrowse_agent not in agents:
            agents += [cobrowse_agent]

        audit_trail_objs = CobrowsingAuditTrail.objects.filter(
            agent__in=agents)

        is_filter_applied = False

        if "startdate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()
            audit_trail_objs = audit_trail_objs.filter(
                datetime__date__gte=datetime_start)
            is_filter_applied = True

        if "enddate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()
            audit_trail_objs = audit_trail_objs.filter(
                datetime__date__lte=datetime_end)
            is_filter_applied = True

        if "action" in request.GET:
            filter_action_list = request.GET.getlist("action")
            action_list = []
            for action in filter_action_list:
                action = remo_html_from_string(action)
                action_list.append(COBROWSING_REVERSE_ACTION_DICT[action])

            audit_trail_objs = audit_trail_objs.filter(action__in=action_list)
            is_filter_applied = True

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")

            selected_agents = CobrowseAgent.objects.filter(
                user__username__in=agent_email)
            audit_trail_objs = audit_trail_objs.filter(
                agent__in=selected_agents)
            is_filter_applied = True

        if "supervisor" in request.GET:
            supervisor_email_id_list = request.GET.getlist("supervisor")
            selected_agents = []
            for agent_email_id in supervisor_email_id_list:
                selected_supervisor = cobrowse_agent.agents.filter(
                    user__username=agent_email_id).first()
                selected_agents += list(selected_supervisor.agents.all())
            audit_trail_objs = audit_trail_objs.filter(
                agent__in=selected_agents)
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

        total_rows_per_pages = 20
        total_audit_trail_objs = len(audit_trail_objs)
        paginator = Paginator(
            audit_trail_objs, total_rows_per_pages)
        page = request.GET.get('page')

        try:
            audit_trail_objs = paginator.page(page)
        except PageNotAnInteger:
            audit_trail_objs = paginator.page(1)
        except EmptyPage:
            audit_trail_objs = paginator.page(paginator.num_pages)

        if page != None:
            start_point = total_rows_per_pages * (int(page) - 1) + 1
            end_point = min(total_rows_per_pages * int(page),
                            total_audit_trail_objs)
            if start_point > end_point:
                start_point = max(end_point - len(audit_trail_objs) + 1, 1)
        else:
            start_point = 1
            end_point = min(total_rows_per_pages, total_audit_trail_objs)

        return render(request, "EasyAssistApp/sales_audit_trail.html", {
            "agents": agents,
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "audit_trail_objs": audit_trail_objs,
            "action_list": COBROWSING_ACTION_LIST,
            "is_filter_applied": is_filter_applied,
            "start_point": start_point,
            "end_point": end_point,
            "total_audit_trail_objs": total_audit_trail_objs,
            "change_app_config": COBROWSING_CHANGEAPPCONFIG_ACTION,
            "supervisors": supervisor_objs,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAuditTrail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesAgentAuditTrail(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        supervisor_objs = []

        if cobrowse_agent.role in ["admin", "admin_ally"]:
            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None, is_account_active=None)
            supervisor_objs = cobrowse_agent.agents.filter(role="supervisor")
            if cobrowse_agent not in agents:
                agents += [cobrowse_agent]

        elif cobrowse_agent.role == "supervisor":
            agents = list(cobrowse_agent.agents.all())
            if cobrowse_agent.is_switch_allowed:
                agents += [cobrowse_agent]
        else:
            return HttpResponse(status=401)

        access_token_obj = cobrowse_agent.get_access_token_obj()

        agent_audit_trail_list = CobrowsingAuditTrail.objects.filter(
            agent__in=agents, action__in=[COBROWSING_LOGIN_ACTION, COBROWSING_LOGOUT_ACTION])

        agent_online_audit_trail_objs = CobrowseAgentOnlineAuditTrail.objects.filter(
            agent__in=agents)

        is_filter_applied = False

        if "startdate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()
            agent_audit_trail_list = agent_audit_trail_list.filter(
                datetime__date__gte=datetime_start)
            agent_online_audit_trail_objs = agent_online_audit_trail_objs.filter(
                last_online_start_datetime__date__gte=datetime_start)
            is_filter_applied = True

        if "enddate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()
            agent_audit_trail_list = agent_audit_trail_list.filter(
                datetime__date__lte=datetime_end)
            agent_online_audit_trail_objs = agent_online_audit_trail_objs.filter(
                last_online_end_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")

            selected_agent = CobrowseAgent.objects.filter(
                user__username__in=agent_email)
            agent_audit_trail_list = agent_audit_trail_list.filter(
                agent__in=selected_agent)
            agent_online_audit_trail_objs = agent_online_audit_trail_objs.filter(
                agent__in=selected_agent)
            is_filter_applied = True

        if "supervisor" in request.GET:
            supervisor_email_id_list = request.GET.getlist("supervisor")
            selected_agents = []
            for agent_email_id in supervisor_email_id_list:
                selected_supervisor = cobrowse_agent.agents.filter(
                    user__username=agent_email_id).first()
                selected_agents += list(selected_supervisor.agents.all())
            agent_audit_trail_list = agent_audit_trail_list.filter(
                agent__in=selected_agents)
            is_filter_applied = True

        if not is_filter_applied:
            datetime_start = (datetime.datetime.today() -
                              datetime.timedelta(7)).date()
            datetime_end = datetime.datetime.today().date()
            agent_audit_trail_list = agent_audit_trail_list.filter(datetime__date__gte=datetime_start,
                                                                   datetime__date__lte=datetime_end)
            agent_online_audit_trail_objs = agent_online_audit_trail_objs.filter(last_online_start_datetime__date__gte=datetime_start,
                                                                                 last_online_end_datetime__date__lte=datetime_end)
            is_filter_applied = True

        if agent_audit_trail_list.count() > 0:
            agent_audit_trail_list = agent_audit_trail_list.order_by(
                '-datetime')
        agent_wise_audit_trail = get_agent_wise_audit_trail(
            agent_audit_trail_list, cobrowse_agent, agents, agent_online_audit_trail_objs, CobrowseAgentWorkAuditTrail)
        total_rows_per_pages = 20
        total_audit_trail_objs = len(agent_wise_audit_trail)
        paginator = Paginator(
            agent_wise_audit_trail, total_rows_per_pages)
        page = request.GET.get('page')

        try:
            agent_wise_audit_trail = paginator.page(page)
        except PageNotAnInteger:
            agent_wise_audit_trail = paginator.page(1)
        except EmptyPage:
            agent_wise_audit_trail = paginator.page(paginator.num_pages)

        if page != None:
            start_point = total_rows_per_pages * (int(page) - 1) + 1
            end_point = min(total_rows_per_pages * int(page),
                            total_audit_trail_objs)
            if start_point > end_point:
                start_point = max(
                    end_point - len(agent_wise_audit_trail) + 1, 1)
        else:
            start_point = 1
            end_point = min(total_rows_per_pages, total_audit_trail_objs)

        return render(request, "EasyAssistApp/sales_agent_audit_trail.html", {
            "agents": agents,
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "agent_wise_audit_trail": agent_wise_audit_trail,
            "is_filter_applied": is_filter_applied,
            "start_point": start_point,
            "end_point": end_point,
            "total_audit_trail_objs": total_audit_trail_objs,
            "supervisors": supervisor_objs,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAgentAuditTrail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesAgentOnlineAuditTrail(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        supervisor_objs = []

        if cobrowse_agent.role in ["admin", "admin_ally"]:
            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None, is_account_active=None)
            supervisor_objs = cobrowse_agent.agents.filter(role="supervisor")
            if cobrowse_agent not in agents:
                agents += [cobrowse_agent]
        elif cobrowse_agent.role == "supervisor":
            agents = list(cobrowse_agent.agents.all())
            if cobrowse_agent.is_switch_allowed:
                agents += [cobrowse_agent]
        else:
            return HttpResponse(status=401)

        access_token_obj = cobrowse_agent.get_access_token_obj()

        agent_online_audit_trail_objs = CobrowseAgentOnlineAuditTrail.objects.filter(
            agent__in=agents)

        is_filter_applied = False

        if "startdate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            start_date = request.GET.getlist("startdate")[0]
            start_date = remo_html_from_string(start_date)
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()

            agent_online_audit_trail_objs = agent_online_audit_trail_objs.filter(
                last_online_start_datetime__date__gte=datetime_start)

            is_filter_applied = True

        if "enddate" in request.GET:
            date_format = DATE_TIME_FORMAT_6
            end_date = request.GET.getlist("enddate")[0]
            end_date = remo_html_from_string(end_date)
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()

            agent_online_audit_trail_objs = agent_online_audit_trail_objs.filter(
                last_online_end_datetime__date__lte=datetime_end)

            is_filter_applied = True

        if "agent" in request.GET:
            agent_email = request.GET.getlist("agent")

            selected_agent = CobrowseAgent.objects.filter(
                user__username__in=agent_email)

            agent_online_audit_trail_objs = agent_online_audit_trail_objs.filter(
                agent__in=selected_agent)

            is_filter_applied = True

        if "supervisor" in request.GET:
            supervisor_email_id_list = request.GET.getlist("supervisor")
            selected_agents = []
            for agent_email_id in supervisor_email_id_list:
                selected_supervisor = cobrowse_agent.agents.filter(
                    user__username=agent_email_id).first()
                selected_agents += list(selected_supervisor.agents.all())
            agent_online_audit_trail_objs = agent_online_audit_trail_objs.filter(
                agent__in=selected_agents)
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

        agent_wise_audit_trail = get_agent_wise_online_audit_trail(
            cobrowse_agent, agents, agent_online_audit_trail_objs, CobrowseAgentWorkAuditTrail)

        total_rows_per_pages = 20
        total_audit_trail_objs = len(agent_wise_audit_trail)
        paginator = Paginator(
            agent_wise_audit_trail, total_rows_per_pages)
        page = request.GET.get('page')

        try:
            agent_wise_audit_trail = paginator.page(page)
        except PageNotAnInteger:
            agent_wise_audit_trail = paginator.page(1)
        except EmptyPage:
            agent_wise_audit_trail = paginator.page(paginator.num_pages)

        if page != None:
            start_point = total_rows_per_pages * (int(page) - 1) + 1
            end_point = min(total_rows_per_pages * int(page),
                            total_audit_trail_objs)
            if start_point > end_point:
                start_point = max(
                    end_point - len(agent_wise_audit_trail) + 1, 1)
        else:
            start_point = 1
            end_point = min(total_rows_per_pages, total_audit_trail_objs)

        return render(request, "EasyAssistApp/sales_agent_online_audit_trail.html", {
            "agents": agents,
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "agent_wise_audit_trail": agent_wise_audit_trail,
            "is_filter_applied": is_filter_applied,
            "start_point": start_point,
            "end_point": end_point,
            "total_audit_trail_objs": total_audit_trail_objs,
            "supervisors": supervisor_objs,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAgentOnlineAuditTrail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def ArchiveCobrowsingLead(request, session_id):
    try:
        if not request.user.is_authenticated:
            return HttpResponse("Unauthorized Access")

        cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
        cobrowse_io.is_archived = True
        cobrowse_io.save()
        logger.warning("ArchiveCobrowsingLead should not run",
                       extra={'AppName': 'EasyAssist'})
        return redirect("/easy-assist/sales-ai/dashboard/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ArchiveCobrowsingLead %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse("Invalid Request")


def RenderLastStateOfCobrowsingSession(request, session_id):
    try:
        if not request.user.is_authenticated:
            return HttpResponse("Unauthorized Access")

        cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
        return render(request, "EasyAssistApp/last_state.html", {"cobrowse_io_obj": cobrowse_io})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error RenderLastStateOfCobrowsingSession %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse("Invalid Request")


class SyncCobrowseIOAgentAPI(APIView):

    permission_classes = [IsAuthenticated]

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

            cobrowse_io_obj = None
            try:
                cobrowse_io_obj = CobrowseIO.objects.get(session_id=id)
            except Exception:
                pass

            if cobrowse_io_obj != None:

                try:
                    active_agent = get_active_agent_obj(
                        request, CobrowseAgent)
                    time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=1)
                    agent_work_audit_trail_obj = CobrowseAgentWorkAuditTrail.objects.filter(
                        agent=active_agent,
                        session_end_datetime__gte=time_threshold).order_by(
                            '-session_start_datetime').first()

                    if agent_work_audit_trail_obj != None:
                        agent_work_audit_trail_obj.session_end_datetime = timezone.now()
                        agent_work_audit_trail_obj.save()
                    else:
                        agent_work_audit_trail_obj = CobrowseAgentWorkAuditTrail.objects.create(
                            agent=active_agent,
                            session_start_datetime=timezone.now(),
                            session_end_datetime=timezone.now())
                        agent_work_audit_trail_obj.save()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error SyncCobrowseIOAgentAPI %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                if cobrowse_io_obj.is_archived == False:
                    cobrowse_io_obj.last_agent_update_datetime = timezone.now()

                cobrowse_io_obj.is_agent_connected = True
                cobrowse_io_obj.save()

                user_obj = User.objects.get(username=request.user.username)
                cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
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
                response["customer_meeting_request_status"] = cobrowse_io_obj.customer_meeting_request_status
                response["allow_customer_meeting"] = cobrowse_io_obj.allow_customer_meeting
                response["status"] = 200
                response["message"] = "success"
            else:
                response["is_client_connected"] = False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SyncCobrowseIOAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SyncHighlightCobrowseIOAgent = SyncHighlightCobrowseIOAgentAPI.as_view()


class TakeClientScreenshotAPI(APIView):

    permission_classes = [IsAuthenticated]

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
            screenshot_type = data["screenshot_type"]
            screenshot_type = remo_html_from_string(screenshot_type)
            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            cobrowse_io.take_screenshot = True
            cobrowse_io.type_screenshot = screenshot_type
            cobrowse_io.save()
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error TakeClientScreenshotAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


TakeClientScreenshot = TakeClientScreenshotAPI.as_view()


class CloseCobrowsingSessionAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["id"])
            id = remo_html_from_string(id)
            is_lead_updated = False
            if "is_lead_updated" in data:
                is_lead_updated = True

            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            active_agent = get_active_agent_obj(request, CobrowseAgent)

            response["is_cobrowsing_from_livechat"] = cobrowse_io.is_cobrowsing_from_livechat

            if "is_leaving" in data:
                cobrowse_io.support_agents.remove(active_agent)
                cobrowse_io.save()
                response['status'] = 200
            else:
                comments = strip_html_tags(data["comments"])
                subcomments = strip_html_tags(data["subcomments"])
                comment_desc = ""
                if "comment_desc" in data:
                    comment_desc = strip_html_tags(data["comment_desc"])

                meeting_io = CobrowseVideoConferencing.objects.filter(
                    meeting_id=id)

                if meeting_io:
                    meeting_io = meeting_io[0]
                    meeting_io.is_expired = True
                    meeting_io.agent_comments = comments
                    meeting_io.save()

                    try:
                        audit_trail_objs = CobrowseVideoAuditTrail.objects.filter(
                            cobrowse_video=meeting_io)
                        if audit_trail_objs:
                            audit_trail = audit_trail_objs[0]
                            audit_trail.meeting_ended = timezone.now()
                            audit_trail.is_meeting_ended = True
                            audit_trail.save()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Error CloseCobrowsingSessionAPI %s at %s",
                                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                is_helpful = True
                if cobrowse_io.is_helpful == False:
                    if "is_helpful" in data:
                        is_helpful = data["is_helpful"]

                is_test = False
                if "is_test" in data:
                    is_test = data["is_test"]

                if str(active_agent.user.username) == str(cobrowse_io.agent):
                    if not cobrowse_io.is_archived:
                        update_virtual_agent_code(cobrowse_io)
                    cobrowse_io.is_archived = True
                    cobrowse_io.is_agent_connected = False
                    cobrowse_io.is_closed_session = True
                    cobrowse_io.is_helpful = is_helpful
                    cobrowse_io.is_test = is_test
                    if not cobrowse_io.agent_comments:
                        cobrowse_io.agent_comments = comments
                    cobrowse_io.agent_session_end_time = timezone.now()
                    if cobrowse_io.session_archived_cause == None:
                        if cobrowse_io.cobrowsing_start_datetime == None and cobrowse_io.meeting_start_datetime == None and cobrowse_io.allow_agent_cobrowse != "false":
                            cobrowse_io.session_archived_cause = "UNATTENDED"
                        else:
                            cobrowse_io.session_archived_cause = "AGENT_ENDED"
                        cobrowse_io.session_archived_datetime = timezone.now()
                    if is_lead_updated == False:
                        cobrowse_io.agent_session_end_time = timezone.now()
                    cobrowse_io.save()
                    current_session_comments = CobrowseAgentComment.objects.filter(
                        cobrowse_io=cobrowse_io)
                    if current_session_comments.exists() == False:
                        save_agent_closing_comments_cobrowseio(
                            cobrowse_io, active_agent, comments, CobrowseAgentComment, comment_desc, subcomments)

                if is_lead_updated:
                    category = "session_lead_status_update"
                    description = "Lead status is updated by " + \
                        str(active_agent.user.username)
                else:
                    category = "session_closed"
                    description = "Session is archived by " + \
                        str(active_agent.user.username) + \
                        " after submitting comments"
                save_system_audit_trail(
                    category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, active_agent)

                if "is_agent_code_required" in data:
                    active_agent = get_active_agent_obj(request, CobrowseAgent)
                    response["agent_code"] = active_agent.virtual_agent_code
                
                response["status"] = 200
                response["message"] = "success"

            active_agent.is_cobrowsing_active = False
            active_agent.is_cognomeet_active = False
            active_agent.save(update_fields=["is_cobrowsing_active", "is_cognomeet_active"])
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CloseCobrowsingSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CloseCobrowsingSession = CloseCobrowsingSessionAPI.as_view()


class ManuallyConvertLeadAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["id"])
            id = remo_html_from_string(id)

            cobrowse_io = CobrowseIO.objects.filter(session_id=id).first()
            active_agent = get_active_agent_obj(request, CobrowseAgent)

            if not cobrowse_io.is_lead_manually_converted:
                comments = strip_html_tags(data["comments"])
                subcomments = strip_html_tags(data["subcomments"])
                comment_desc = strip_html_tags(data["comment_desc"])
                is_helpful = data["is_helpful"]
                cobrowse_io.is_helpful = is_helpful
                cobrowse_io.is_lead_manually_converted = True
                cobrowse_io.agent_manually_converted_lead = active_agent
                cobrowse_io.save(update_fields=["is_helpful", "is_lead_manually_converted", "agent_manually_converted_lead"])

                save_agent_closing_comments_cobrowseio(
                    cobrowse_io, active_agent, comments, CobrowseAgentComment, comment_desc, subcomments)

                response["status"] = 200
                response["message"] = "success"

            else:
                lead_converted_by_agent = cobrowse_io.agent_manually_converted_lead.user.username
                response["message"] = lead_converted_by_agent + \
                    " has already converted the lead manually"
                response["status"] = 300

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ManuallyConvertLeadAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ManuallyConvertLead = ManuallyConvertLeadAPI.as_view()


class CheckLeadManuallyConvertedAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["id"])
            id = remo_html_from_string(id)

            cobrowse_io = CobrowseIO.objects.get(session_id=id)

            is_lead_manually_converted = False
            lead_converted_by_agent = ""
            if cobrowse_io.is_lead_manually_converted:
                is_lead_manually_converted = True
                lead_converted_by_agent = cobrowse_io.agent_manually_converted_lead.user.username

            response["status"] = 200
            response["is_lead_manually_converted"] = is_lead_manually_converted
            response["lead_converted_by_agent"] = lead_converted_by_agent
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckLeadManuallyConvertedAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckLeadManuallyConverted = CheckLeadManuallyConvertedAPI.as_view()


class GetCobrowsingMetaInformationAPI(APIView):

    permission_classes = [IsAuthenticated]

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
            page = data["page"]

            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            cobrowse_meta_objs = CobrowsingSessionMetaData.objects.filter(
                cobrowse_io=cobrowse_io).order_by('-datetime')
            access_token_obj = cobrowse_io.agent.get_access_token_obj()

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
                    est).strftime("%I:%M %p")

                file_path = cobrowse_meta_obj.content
                file_name = file_path.split("/")[-1]

                file_access_management_obj = CobrowsingFileAccessManagement.objects.filter(
                    file_path="/" + file_path, is_public=False, original_file_name=file_name).first()

                if not file_access_management_obj:
                    file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                        file_path="/" + file_path, is_public=False, original_file_name=file_name, access_token=access_token_obj)

                meta_information_list.append({
                    "id": str(file_access_management_obj.pk),
                    "type": cobrowse_meta_obj.type_screenshot,
                    "content": "/easy-assist/pageshot/" + str(cobrowse_meta_obj.pk),
                    "datetime": datetime
                })

            response["status"] = 200
            response["message"] = "success"
            response["is_last_page"] = is_last_page
            response["meta_information_list"] = meta_information_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCobrowsingMetaInformationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCobrowsingMetaInformation = GetCobrowsingMetaInformationAPI.as_view()


class ChangeAgentActiveStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            status = data["active_status"]

            if status == True or status == False:
                active_agent = get_active_agent_obj(
                    request, CobrowseAgent)

                location = str(data['location'])
                if location != "None" and location.strip() != "" and location != active_agent.location:
                    active_agent.location = remo_html_from_string(location)

                change_agent_is_active_flag(
                    status, active_agent, CobrowseAgentOnlineAuditTrail, CobrowseAgentWorkAuditTrail)

                cobrowse_io_objs = CobrowseIO.objects.filter(
                    is_archived=False, agent__in=[active_agent], is_active=True)

                cobrowse_io_obj_count = 0

                for cobrowse_io_obj in cobrowse_io_objs:
                    if cobrowse_io_obj.is_active_timer() == True:
                        cobrowse_io_obj_count += 1

                meeting_io_obj_count = CobrowseVideoConferencing.objects.filter(
                    is_expired=False,
                    support_meeting_agents__in=[active_agent]).count()

                response["status"] = 200
                response["message"] = "success"
                response["cobrowsing_count"] = cobrowse_io_obj_count
                response["video_meeting_count"] = meeting_io_obj_count
                response["location"] = location
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ChangeAgentActiveStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ChangeAgentActiveStatus = ChangeAgentActiveStatusAPI.as_view()


class SaveAgentDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)
            user = active_agent.user

            old_password = remo_html_from_string(data["old_password"])
            new_password = remo_html_from_string(data["new_password"])

            old_password = remo_special_tag_from_string(old_password)
            new_password = remo_special_tag_from_string(new_password)

            changed_data = {}

            if "agent_mobile_number" in data:
                agent_mobile_number = sanitize_input_string(data["agent_mobile_number"])
                if not len(agent_mobile_number):
                    response["status"] = 301
                    response["message"] = "Please enter mobile number to continue"
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                if not is_mobile_valid(agent_mobile_number):
                    response["status"] = 301
                    response["message"] = "Please enter valid 10 digit mobile number"
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                changed_data["agent_mobile_number"] = agent_mobile_number

            if "agent_name" in data:
                agent_name = sanitize_input_string(data["agent_name"])
                if not len(agent_name):
                    response["status"] = 301
                    response["message"] = "Please enter name to continue"
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                if not check_valid_name(agent_name):
                    response["status"] = 301
                    response["message"] = "Please enter a valid name"
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                changed_data["agent_name"] = agent_name

            is_valid_password = True
            is_password_changed = False
            if old_password != "":
                if not user.check_password(old_password):
                    is_valid_password = False
                else:
                    is_password_changed = True

            if is_valid_password:

                if is_password_changed:
                    if(validate_user_new_password(active_agent, new_password, old_password, AgentPasswordHistory) == "VALID"):
                        user.is_online = False
                        user.set_password(new_password)
                        user.save()

                        new_password_hash = hashlib.sha256(
                            new_password.encode()).hexdigest()
                        AgentPasswordHistory.objects.create(
                            agent=active_agent, password_hash=new_password_hash)

                        description = "User (" + user.first_name + \
                            "'s) password was changed"
                        save_audit_trail(active_agent, COBROWSING_UPDATEUSER_ACTION,
                                         description, CobrowsingAuditTrail)

                        add_audit_trail(
                            "EASYASSISTAPP",
                            active_agent.user,
                            "Updated-User",
                            description,
                            json.dumps({}),
                            request.META.get("PATH_INFO"),
                            request.META.get('HTTP_X_FORWARDED_FOR')
                        )
                    else:
                        response["status"] = 102
                        response["message"] = "Password Matched with previous password"

                if response["status"] != 102:
                    personal_details_changed = False
                    if user.first_name != strip_html_tags(data["agent_name"]):
                        personal_details_changed = True
                    description = "User (" + user.first_name + \
                        "'s) personal details changed"

                    user.first_name = strip_html_tags(data["agent_name"])
                    user.save()
                    if active_agent.role != "admin":

                        if active_agent.mobile_number != strip_html_tags(data["agent_mobile_number"]):
                            personal_details_changed = True

                        active_agent.mobile_number = strip_html_tags(
                            data["agent_mobile_number"])

                        if is_password_changed:
                            active_agent.is_active = False

                        active_agent.save()

                    if personal_details_changed:
                        save_audit_trail(
                            active_agent, COBROWSING_UPDATEUSER_ACTION, description, CobrowsingAuditTrail)

                        add_audit_trail(
                            "EASYASSISTAPP",
                            active_agent.user,
                            "Updated-User",
                            description,
                            json.dumps(changed_data),
                            request.META.get("PATH_INFO"),
                            request.META.get('HTTP_X_FORWARDED_FOR')
                        )

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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveAgentDetails = SaveAgentDetailsAPI.as_view()


class AddNewAgentDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()
            user_type = strip_html_tags(data["user_type"])
            user_type = remo_html_from_string(user_type)
            
            if user_type == "agent" and active_agent.is_agent_creation_limit_exhausted():
                response["status"] = 307
                response["message"] = AGENT_CREATION_LIMIT_EXHAUST_ERROR
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
            
            if user_type == "supervisor" and active_agent.is_supervisor_creation_limit_exhausted():
                response["status"] = 307
                response["message"] = SUPERVISOR_CREATION_LIMIT_EXHAUST_ERROR
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

            if active_agent.role != "agent":
                agent_mobile = strip_html_tags(data["agent_mobile"])
                agent_mobile = remo_html_from_string(agent_mobile)

                assign_followup_lead_to_agent = True
                if "assign_followup_lead_to_agent" in data and data["assign_followup_lead_to_agent"] != None:
                    assign_followup_lead_to_agent = data["assign_followup_lead_to_agent"]

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

                elif data["user_type"] in ["agent", "supervisor", "admin_ally"]:

                    agent_name = strip_html_tags(data["agent_name"])
                    agent_name = remo_html_from_string(agent_name)
                    if not agent_name:
                        response["status"] = 309
                        response["message"] = "Full name cannot be empty."
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(
                            response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)
                    agent_email = strip_html_tags(data["agent_email"])
                    agent_email = remo_html_from_string(agent_email)
                    reg_name = r'^[a-zA-Z ]*$'
                    reg_email = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
                    if not re.fullmatch(reg_name, agent_name):
                        response["status"] = 401
                        response["message"] = "Please enter full name (only A-Z, a-z and space is allowed)"
                    elif not re.fullmatch(reg_email, agent_email):
                        response["status"] = 401
                        response["message"] = "Please enter valid Email Id."
                    else:
                        support_level = strip_html_tags(data["support_level"])
                        support_level = remo_html_from_string(support_level)

                        if is_url_valid(data["platform_url"].strip()) == False:
                            response["status"] = 500
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(
                                response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)

                        platform_url = strip_html_tags(data["platform_url"])
                        platform_url = remo_html_from_string(platform_url)
                        selected_supervisor_pk_list = data[
                            "selected_supervisor_pk_list"]
                        selected_language_pk_list = data[
                            "selected_language_pk_list"]
                        selected_product_category_pk_list = data[
                            "selected_product_category_pk_list"]
                        
                        if active_agent.role == "admin_ally" and user_type == "agent" and len(selected_supervisor_pk_list) == 1 and selected_supervisor_pk_list[0] == -1:
                            response["status"] = 307
                            response["message"] = "No supervisor selected."
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(
                                response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)

                        category_matched = check_for_supervisor_category_language_match(active_agent, user_type, selected_supervisor_pk_list,
                                                                                        selected_language_pk_list, selected_product_category_pk_list,
                                                                                        CobrowseAgent)

                        if len(category_matched):
                            response["status"] = 303
                            response["message"] = category_matched
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(
                                response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)

                        user = None

                        password = generate_password(
                            access_token_obj.password_prefix)

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
                                                                      support_level=support_level,
                                                                      assign_followup_leads=assign_followup_lead_to_agent,
                                                                      access_token=access_token_obj)

                        add_selected_supervisor(
                            selected_supervisor_pk_list, active_agent, cobrowse_agent, CobrowseAgent)
                        add_supported_language(
                            cobrowse_agent, selected_language_pk_list, LanguageSupport)
                        add_product_category_to_user(
                            cobrowse_agent, selected_product_category_pk_list, ProductCategory)
                        update_agents_supervisors_creation_count(active_agent, user_type)

                        description = "New " + \
                            data["user_type"] + \
                            " (" + agent_name + ") has been added"
                        save_audit_trail(
                            active_agent, COBROWSING_ADDUSER_ACTION, description, CobrowsingAuditTrail)

                        add_audit_trail(
                            "EASYASSISTAPP",
                            active_agent.user,
                            "Add-User",
                            description,
                            json.dumps(data),
                            request.META.get("PATH_INFO"),
                            request.META.get('HTTP_X_FORWARDED_FOR')
                        )

                        response["status"] = 200
                        response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddNewAgentDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddNewAgentDetails = AddNewAgentDetailsAPI.as_view()


class UpdateAgentDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logger.info("Into Update Agent Details API",
                    extra={'AppName': 'EasyAssist'})
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

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

                    elif data["user_type"] in ["agent", "supervisor", "admin_ally"]:

                        agent_name = strip_html_tags(data["agent_name"])
                        agent_name = remo_html_from_string(agent_name)
                        if not agent_name:
                            response["status"] = 309
                            response["message"] = "Full name not cannot be empty."
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(
                                response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)
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
                            agents__pk=cobrowse_agent.pk).filter(~Q(role="admin_ally"))
                        selected_language_pk_list = data[
                            "selected_language_pk_list"]
                        selected_product_category_pk_list = data[
                            "selected_product_category_pk_list"]
                        previous_role = CobrowseAgent.objects.filter(user__username=agent_email).first().role
                        if previous_role != user_type and user_type == "agent" and active_agent.is_agent_creation_limit_exhausted():
                            response["status"] = 307
                            response["message"] = AGENT_CREATION_LIMIT_EXHAUST_ERROR
                            return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                        
                        if previous_role != user_type and user_type == "supervisor" and active_agent.is_supervisor_creation_limit_exhausted():
                            response["status"] = 307
                            response["message"] = SUPERVISOR_CREATION_LIMIT_EXHAUST_ERROR
                            return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                        if active_agent.role == "admin_ally" and user_type == "agent" and len(selected_supervisor_pk_list) == 1 and selected_supervisor_pk_list[0] == "-1":
                            response["status"] = 307
                            response["message"] = "No supervisor selected."
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(
                                response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)

                        if user_type != "agent":
                            response_message = check_for_details_match(active_agent, user_type, agent_email, selected_language_pk_list,
                                                                       selected_product_category_pk_list, CobrowseAgent, User)
                            if response_message:
                                response["status"] = 311
                                response["message"] = response_message
                                response = json.dumps(response)
                                encrypted_response = custom_encrypt_obj.encrypt(
                                    response)
                                response = {"Response": encrypted_response}
                                return Response(data=response)
                        
                        category_matched = check_for_supervisor_category_language_match(active_agent, user_type, selected_supervisor_pk_list,
                                                                                        selected_language_pk_list, selected_product_category_pk_list,
                                                                                        CobrowseAgent)
                        if len(category_matched):
                            response["status"] = 303
                            response["message"] = category_matched
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(
                                response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)

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

                        if "assign_followup_lead_to_agent" in data and data["assign_followup_lead_to_agent"] != None:
                            cobrowse_agent.assign_followup_leads = data["assign_followup_lead_to_agent"]

                        if user_type == "supervisor":
                            supervisors_objs = CobrowseAgent.objects.filter(
                                role="supervisor", agents=cobrowse_agent)
                            for obj in supervisors_objs:
                                obj.agents.remove(cobrowse_agent)

                        if user_type == "agent":
                            agents = cobrowse_agent.agents.all()
                            admin_agent = get_admin_from_active_agent(active_agent, CobrowseAgent)
                            for agent in agents:
                                cobrowse_agent.agents.remove(agent)
                                cobrowse_agent.save()
                                supervisor_count = CobrowseAgent.objects.filter(
                                    agents=agent).count()
                                if supervisor_count == 0:
                                    admin_agent.agents.add(agent)
                                    admin_agent.save()

                        if active_agent.role == "admin" and user_type == "agent":
                            for previous_supervisor in previous_supervisor_list:
                                previous_supervisor.agents.remove(
                                    cobrowse_agent)
                                previous_supervisor.save()

                        if active_agent.role == "admin" and user_type == "admin_ally":
                            previous_supervisors_admin_ally = cobrowse_agent.agents.all()
                            for previous_supervisor in previous_supervisors_admin_ally:
                                cobrowse_agent.agents.remove(
                                    previous_supervisor)

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
                        if previous_role != user_type:
                            update_agents_supervisors_creation_count(active_agent, user_type)

                        description = "New Details for " + \
                            data["user_type"] + \
                            " (" + agent_name + ") has been added"
                        save_audit_trail(
                            active_agent, COBROWSING_UPDATEUSER_ACTION, description, CobrowsingAuditTrail)

                        add_audit_trail(
                            "EASYASSISTAPP",
                            active_agent.user,
                            "Updated-User",
                            description,
                            json.dumps(data),
                            request.META.get("PATH_INFO"),
                            request.META.get('HTTP_X_FORWARDED_FOR')
                        )

                        response["status"] = 200
                        response["message"] = "success"
                        logger.info("Successfully exited Update Agent Details API", extra={
                                    'AppName': 'EasyAssist'})

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error Agent not found %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateAgentDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateAgentDetails = UpdateAgentDetailsAPI.as_view()


class GetAgentsFollowupLeadTransferAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logger.info("Into GetAgentsFollowupLeadTransferAPI",
                    extra={'AppName': 'EasyAssist'})
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            selected_leads_id = data["selected_leads_id"]

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            access_token_obj = active_agent.get_access_token_obj()

            if active_agent.role != "agent":

                agent_objs = []

                # if product category or language support is enabled then further filter agents
                if access_token_obj.allow_language_support or access_token_obj.choose_product_category:

                    cobrowse_io_objs = []
                    product_category_list = []
                    language_list = []

                    for session_id in selected_leads_id:
                        try:
                            cobrowse_io = CobrowseIO.objects.filter(
                                access_token=access_token_obj, pk=session_id).first()
                            if cobrowse_io is not None:
                                cobrowse_io_objs.append(cobrowse_io)
                        except Exception as e:
                            logger.error("Error GetAgentsFollowupLeadTransferAPI CobrowseIO object not found %s", str(
                                e), extra={'AppName': 'EasyAssist'})
                            continue

                    if len(cobrowse_io_objs) != 0:
                        for cobrowse_io_obj in cobrowse_io_objs:

                            if cobrowse_io_obj.supported_language not in language_list:
                                language_list.append(
                                    cobrowse_io_obj.supported_language)

                            if cobrowse_io_obj.product_category not in product_category_list:
                                product_category_list.append(
                                    cobrowse_io_obj.product_category)

                        filtered_agents_list = []

                        if active_agent.role in ["admin", "admin_ally"]:

                            agents_under_admin = get_list_agents_under_admin(
                                active_agent, is_active=None)

                            agents_under_admin = get_agents_with_followup_enabled(
                                agents_under_admin)

                            if access_token_obj.allow_language_support and access_token_obj.choose_product_category:
                                # filtered_agents_list = CobrowseAgent.objects.filter(role="agent", is_account_active=True,
                                #     assign_followup_leads=True, supported_language__in=language_list, product_category__in=product_category_list)

                                filtered_agents_list = get_agents_for_product_and_language(agents_under_admin, product_category_list, language_list,
                                                                                           access_token_obj.allow_language_support, access_token_obj.choose_product_category)

                            elif access_token_obj.allow_language_support:
                                # filtered_agents_list = CobrowseAgent.objects.filter(role="agent", is_account_active=True,
                                #     assign_followup_leads=True, supported_language__in=language_list)

                                filtered_agents_list = get_agents_for_product_and_language(agents_under_admin, [], language_list,
                                                                                           access_token_obj.allow_language_support, access_token_obj.choose_product_category)

                            elif access_token_obj.choose_product_category:
                                # filtered_agents_list = CobrowseAgent.objects.filter(role="agent", is_account_active=True,
                                #     assign_followup_leads=True, product_category__in=product_category_list)

                                filtered_agents_list = get_agents_for_product_and_language(agents_under_admin, product_category_list, [],
                                                                                           access_token_obj.allow_language_support, access_token_obj.choose_product_category)

                        elif active_agent.role == "supervisor":
                            filtered_agents_list = active_agent.agents.all()
                            if access_token_obj.allow_language_support and access_token_obj.choose_product_category:

                                filtered_agents_list = filtered_agents_list.filter(is_account_active=True, assign_followup_leads=True,
                                                                                   supported_language__in=language_list, product_category__in=product_category_list)

                                filtered_agents_list = get_agents_for_product_and_language(filtered_agents_list, product_category_list, language_list,
                                                                                           access_token_obj.allow_language_support, access_token_obj.choose_product_category)

                            elif access_token_obj.allow_language_support:
                                filtered_agents_list = filtered_agents_list.filter(
                                    is_account_active=True, assign_followup_leads=True, supported_language__in=language_list)

                                filtered_agents_list = get_agents_for_product_and_language(filtered_agents_list, [], language_list,
                                                                                           access_token_obj.allow_language_support, access_token_obj.choose_product_category)

                            elif access_token_obj.choose_product_category:
                                filtered_agents_list = filtered_agents_list.filter(
                                    is_account_active=True, assign_followup_leads=True, product_category__in=product_category_list)

                                filtered_agents_list = get_agents_for_product_and_language(filtered_agents_list, product_category_list, [],
                                                                                           access_token_obj.allow_language_support, access_token_obj.choose_product_category)

                        filtered_agents_list = set(filtered_agents_list)
                        agent_objs = filtered_agents_list

                else:
                    if active_agent.role in ["admin", "admin_ally"]:
                        agent_objs = get_list_agents_under_admin(
                            active_agent, is_active=None)

                    elif active_agent.role == "supervisor":
                        agent_objs = active_agent.agents.all()
                        agent_objs = agent_objs.filter(is_account_active=True)
                        agent_objs = list(agent_objs)

                    agent_objs = get_agents_with_followup_enabled(agent_objs)

                agents_list_for_lead_transfer = []
                if len(agent_objs) != 0:
                    for agent in agent_objs:
                        agent_detail = {
                            "pk": agent.pk,
                            "username": agent.user.username
                        }
                        agents_list_for_lead_transfer.append(agent_detail)

                response["status"] = 200
                response["message"] = "success"

                response["agents_list_for_lead_transfer"] = agents_list_for_lead_transfer
                logger.info("Successfully exited GetAgentsFollowupLeadTransferAPI", extra={
                            'AppName': 'EasyAssist'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentsFollowupLeadTransferAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentsFollowupLeadTransfer = GetAgentsFollowupLeadTransferAPI.as_view()


class TransferFollowupLeadsToAgentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logger.info("Into TransferFollowupLeadsToAgentAPI",
                    extra={'AppName': 'EasyAssist'})
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            selected_leads_id = data["selected_leads_id"]
            agent_pk = data["agent_pk"]

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            access_token_obj = active_agent.get_access_token_obj()

            if active_agent.role != "agent":

                selected_cobrowse_agent = CobrowseAgent.objects.get(
                    pk=agent_pk)

                # list of selected cobrowseio that need to be transfered
                cobrowse_io_objs = []
                for session_id in selected_leads_id:
                    try:
                        cobrowse_io = CobrowseIO.objects.filter(
                            access_token=access_token_obj, pk=session_id).first()
                        if cobrowse_io is not None:
                            cobrowse_io_objs.append(cobrowse_io)
                    except Exception as e:
                        logger.error("Error GetAgentsFollowupLeadTransferAPI CobrowseIO object not found %s", str(
                            e), extra={'AppName': 'EasyAssist'})
                        continue

                if len(cobrowse_io_objs) != 0:
                    if access_token_obj.allow_language_support or access_token_obj.choose_product_category:
                        lead_assignment_track = {}
                        for cobrowse_io_obj in cobrowse_io_objs:
                            lead_assignment_track[cobrowse_io_obj.session_id] = {
                                "is_assigned": False
                            }

                            if cobrowse_io_obj.access_token.allow_language_support:
                                if cobrowse_io_obj.supported_language in selected_cobrowse_agent.supported_language.filter(is_deleted=False):
                                    if cobrowse_io_obj.access_token.choose_product_category:
                                        if cobrowse_io_obj.product_category in selected_cobrowse_agent.product_category.filter(is_deleted=False):
                                            cobrowse_io_obj.agent = selected_cobrowse_agent
                                            selected_cobrowse_agent.last_lead_assigned_datetime = timezone.now()
                                            selected_cobrowse_agent.save()
                                            lead_assignment_track[cobrowse_io_obj.session_id]["is_assigned"] = True
                                    else:
                                        cobrowse_io_obj.agent = selected_cobrowse_agent
                                        selected_cobrowse_agent.last_lead_assigned_datetime = timezone.now()
                                        selected_cobrowse_agent.save()
                                        lead_assignment_track[cobrowse_io_obj.session_id]["is_assigned"] = True
                            else:
                                if cobrowse_io_obj.access_token.choose_product_category:
                                    if cobrowse_io_obj.product_category in selected_cobrowse_agent.product_category.filter(is_deleted=False):
                                        cobrowse_io_obj.agent = selected_cobrowse_agent
                                        selected_cobrowse_agent.last_lead_assigned_datetime = timezone.now()
                                        selected_cobrowse_agent.save()
                                        lead_assignment_track[cobrowse_io_obj.session_id]["is_assigned"] = True

                            cobrowse_io_obj.save()

                        response["status"] = 200
                        response["message"] = "success"

                        for cobrowse_io_obj in cobrowse_io_objs:
                            if lead_assignment_track[cobrowse_io_obj.session_id]["is_assigned"] == False:
                                response["status"] = 300
                                response["message"] = "Transfer of leads for the selected agent was not successful."
                                break

                    else:
                        for cobrowse_io_obj in cobrowse_io_objs:
                            cobrowse_io_obj.agent = selected_cobrowse_agent
                            cobrowse_io_obj.save()
                            selected_cobrowse_agent.last_lead_assigned_datetime = timezone.now()
                            selected_cobrowse_agent.save()

                        response["status"] = 200
                        response["message"] = "success"

                logger.info("Successfully exited TransferFollowupLeadsToAgentAPI", extra={
                            'AppName': 'EasyAssist'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error TransferFollowupLeadsToAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


TransferFollowupLeadsToAgent = TransferFollowupLeadsToAgentAPI.as_view()


class DeleteCobrowseAgentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            agent_pk = data["agent_pk"]
            agent_pk = strip_html_tags(agent_pk)
            agent_pk = remo_special_tag_from_string(agent_pk)

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            cobrowse_agent = CobrowseAgent.objects.get(pk=agent_pk)
            if cobrowse_agent == None:
                response['status'] = 300
            else:
                agent_name = cobrowse_agent.user.username
                user_type = cobrowse_agent.role
                cobrowse_agent.delete()
                response['status'] = 200
                description = user_type[
                    0].upper() + user_type[1:] + " (" + agent_name + ") has been deleted"
                save_audit_trail(
                    active_agent, COBROWSING_DELETEUSER_ACTION, description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Delete-User",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteCobrowseAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteCobrowseAgent = DeleteCobrowseAgentAPI.as_view()


class ResendAccountPasswordAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            user_pk = data["user_pk"]
            platform_url = data["platform_url"]

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            try:
                cobrowse_agent = CobrowseAgent.objects.get(pk=int(user_pk))
                update_resend_password_counter(cobrowse_agent)

                if cobrowse_agent.resend_password_count >= 0:
                    user = cobrowse_agent.user

                    password = generate_password(
                        cobrowse_agent.get_access_token_obj().password_prefix)

                    thread = threading.Thread(target=send_password_over_email, args=(
                        user.email, user.first_name, password, platform_url, ), daemon=True)
                    thread.start()

                    user.set_password(password)
                    user.save()

                    cobrowse_agent.user = user
                    cobrowse_agent.save()

                    message = "New password sent to " + \
                        str(cobrowse_agent.user.email)
                    response["message"] = message

                    description = message

                    save_audit_trail(
                        active_agent, COBROWSING_PASSWORD_RESENT_ACTION, description, CobrowsingAuditTrail)

                    add_audit_trail(
                        "EASYASSISTAPP",
                        active_agent.user,
                        "Password-Resent",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )
                else:
                    response["message"] = str(cobrowse_agent.user.email) + \
                        " has reached daily resend password limit"

                response["status"] = 200
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error ResendAccountPasswordAPI %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
                response["status"] = 300
                response["message"] = "Could not send the password"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ResendAccountPasswordAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ResendAccountPassword = ResendAccountPasswordAPI.as_view()


class UploadUserDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role in ["admin", "admin_ally"]:

                filename = strip_html_tags(data["filename"])
                filename = remo_html_from_string(filename)
                base64_data = strip_html_tags(data["base64_file"])

                filename = generate_random_key(
                    10) + "_" + filename.replace(" ", "")

                file_path = "secured_files/" + filename

                file_extension = file_path.split(".")[-1]
                file_extension = file_extension.lower()

                allowed_files_list = ["xls", "xlsx",
                                      "xlsm", "xlt", "xltm", "xlb"]
                if file_extension in allowed_files_list:
                    media_type = "excel"
                else:
                    media_type = None

                if media_type == None or check_malicious_file_from_filename(filename, allowed_files_list) or check_malicious_file_from_content(base64_data, allowed_files_list):
                    response["status"] = 300
                else:
                    fh = open(file_path, "wb")
                    fh.write(base64.b64decode(base64_data))
                    fh.close()

                    response_data = add_users_from_excel_document(
                        file_path, active_agent, User, CobrowseAgent, LanguageSupport, ProductCategory, CobrowsingFileAccessManagement)

                    if response_data["status"] == 200:
                        response["status"] = 200
                        response["message"] = response_data["message"]
                    elif response_data["status"] == 304:
                        response["status"] = 304
                        response["message"] = response_data["message"]
                    elif response_data["status"] == 301:
                        response["status"] = 301
                        response["message"] = response_data["message"]
                    elif response_data["status"] == 302:
                        response["status"] = 302
                        response["message"] = response_data["message"]
                        response["file_path"] = response_data["file_path"]

                description = "New users has been added using excel file"
                save_audit_trail(
                    active_agent, COBROWSING_ADDUSER_ACTION, description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Add-User",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadUserDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadUserDetails = UploadUserDetailsAPI.as_view()


class ExportUserDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            export_path = create_excel_user_details(active_agent)

            if export_path:
                file_path = '/' + export_path
                access_token_obj = active_agent.get_access_token_obj()
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)

                response["export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportUserDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportUserDetails = ExportUserDetailsAPI.as_view()


class ExportSupervisorDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            export_path = create_excel_supervisor_details(active_agent)

            if export_path != None:
                file_path = "/" + export_path
                access_token_obj = active_agent.get_access_token_obj()
                file_access_management_key = create_file_access_management_obj(
                    CobrowsingFileAccessManagement, access_token_obj, file_path)

                response["export_path"] = 'easy-assist/download-file/' + \
                    file_access_management_key
                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportSupervisorDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportSupervisorDetails = ExportSupervisorDetailsAPI.as_view()


class DownloadUserDetailsTemplateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            export_path = "files/templates/easyassist-template/User_Details_Template.xlsx"
            response["export_path"] = export_path
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DownloadUserDetailsTemplateAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DownloadUserDetailsTemplate = DownloadUserDetailsTemplateAPI.as_view()


class SaveCobrowsingMetaDetailsCobrowsingAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":
                active_agent.options = json.dumps(data)
                active_agent.save()

                cobrowse_access_token = active_agent.get_access_token_obj()

                agent_connect_message = strip_html_tags(
                    data["agent_connect_message"])
                masked_field_warning_text = strip_html_tags(
                    data["masked_field_warning_text"])
                voip_calling_message = strip_html_tags(
                    data["voip_calling_text"])
                voip_with_video_calling_message = strip_html_tags(
                    data["voip_with_video_calling_text"])
                lead_conversion_text = strip_html_tags(
                    data["lead_conversion_checkbox_text"])
                assistant_message = strip_html_tags(
                    data["assistant_message"])

                cobrowse_access_token.enable_edit_access = data[
                    "enable_edit_access"]
                cobrowse_access_token.enable_screenshot_agent = data[
                    "enable_screenshot_agent"]
                cobrowse_access_token.enable_invite_agent_in_cobrowsing = data[
                    "enable_invite_agent_in_cobrowsing"]
                cobrowse_access_token.allow_screen_recording = data[
                    "allow_screen_recording"]
                cobrowse_access_token.recording_expires_in_days = data[
                    "recording_expires_in_days"]

                if lead_conversion_text != "":
                    cobrowse_access_token.lead_conversion_checkbox_text = lead_conversion_text

                cobrowse_access_token.allow_screen_sharing_cobrowse = data[
                    "allow_screen_sharing_cobrowse"]
                cobrowse_access_token.enable_predefined_remarks = data[
                    "enable_predefined_remarks"]
                cobrowse_access_token.enable_predefined_remarks_with_buttons = data[
                    "enable_predefined_remarks_with_buttons"]
                cobrowse_access_token.enable_predefined_subremarks = data[
                    "enable_predefined_subremarks"]

                predefined_remark_list = data["predefined_remarks_list"]
                for remarks in predefined_remark_list:
                    remarks["remark"] = sanitize_input_string(
                        remarks["remark"])
                    if remarks["subremark"]:
                        for subremark in remarks["subremark"]:
                            subremark["remark"] = sanitize_input_string(
                                subremark["remark"])
                try:
                    predefined_remark_list = json.dumps(predefined_remark_list)
                except Exception:
                    predefined_remark_list = json.dumps([])

                cobrowse_access_token.predefined_remarks = predefined_remark_list

                cobrowse_access_token.predefined_remarks_with_buttons = strip_html_tags(data[
                    "predefined_remarks_with_buttons"])

                cobrowse_access_token.predefined_remarks_optional = data[
                    'predefined_remarks_optional']

                cobrowse_access_token.enable_agent_connect_message = data[
                    "enable_agent_connect_message"]
                if agent_connect_message != "":
                    cobrowse_access_token.agent_connect_message = agent_connect_message

                cobrowse_access_token.enable_masked_field_warning = data[
                    "enable_masked_field_warning"]
                if masked_field_warning_text != "":
                    cobrowse_access_token.masked_field_warning_text = masked_field_warning_text

                cobrowse_access_token.enable_voip_calling = data[
                    "enable_voip_calling"]

                cobrowse_access_token.customer_initiate_voice_call = data[
                    "customer_initiate_voice_call"
                ]

                cobrowse_access_token.enable_voip_with_video_calling = data[
                    "enable_voip_with_video_calling"]

                cobrowse_access_token.customer_initiate_video_call_as_pip = data[
                    "customer_initiate_video_call_as_pip"
                ]

                if voip_calling_message != "":
                    cobrowse_access_token.voip_calling_message = voip_calling_message

                if voip_with_video_calling_message != "":
                    cobrowse_access_token.voip_with_video_calling_message = voip_with_video_calling_message

                cobrowse_access_token.enable_auto_voip_calling_for_first_time = data[
                    "enable_auto_voip_calling_for_first_time"]

                cobrowse_access_token.enable_auto_voip_with_video_calling_for_first_time = data[
                    "enable_auto_voip_with_video_calling_for_first_time"]

                cobrowse_access_token.masking_type = data[
                    "masking_type"]

                cobrowse_access_token.allow_cobrowsing_meeting = data[
                    "allow_video_calling_cobrowsing"]

                cobrowse_access_token.customer_initiate_video_call = data[
                    "customer_initiate_video_call"]

                cobrowse_access_token.show_verification_code_modal = data[
                    "show_verification_code_modal"]

                cobrowse_access_token.enable_verification_code_popup = data[
                    "enable_verification_code_popup"]

                if assistant_message != "":
                    cobrowse_access_token.assist_message = assistant_message

                cobrowse_access_token.urls_consider_lead_converted = strip_html_tags(
                    data["urls_consider_lead_converted"])

                cobrowse_access_token.restricted_urls = strip_html_tags(
                    data["restricted_urls"])

                cobrowse_access_token.archive_on_common_inactivity_threshold = data[
                    "archive_on_common_inactivity_threshold"]

                cobrowse_access_token.drop_link_expiry_time = data[
                    "drop_link_expiry_time"]

                cobrowse_access_token.enable_low_bandwidth_cobrowsing = data[
                    "enable_low_bandwidth_cobrowsing"]

                cobrowse_access_token.enable_manual_switching = data[
                    "enable_manual_switching"]

                cobrowse_access_token.low_bandwidth_cobrowsing_threshold = data[
                    "low_bandwidth_cobrowsing_threshold"]

                cobrowse_access_token.enable_smart_agent_assignment = data[
                    "enable_smart_agent_assignment"]

                cobrowse_access_token.smart_agent_assignment_reconnecting_window = data[
                    "reconnecting_window_timer_input"]

                cobrowse_access_token.save()

                description = "Custom App Configuration Changes - Cobrowsing"
                save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                 description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowsingMetaDetailsCobrowsingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowsingMetaDetailsCobrowsing = SaveCobrowsingMetaDetailsCobrowsingAPI.as_view()


class SaveCobrowsingMetaDetailsMeetingAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":
                active_agent.options = json.dumps(data)
                active_agent.save()

                cobrowse_access_token = active_agent.get_access_token_obj()

                cobrowse_access_token.proxy_server = strip_html_tags(
                    data["proxy_server"])
                cobrowse_access_token.meeting_default_password = strip_html_tags(data[
                    "meeting_default_password"])

                cobrowse_access_token.meeting_host_url = strip_html_tags(data[
                    "meeting_url"])

                cobrowse_access_token.show_cobrowsing_meeting_lobby = data[
                    "show_cobrowsing_meeting_lobby"]

                cobrowse_access_token.meet_background_color = data[
                    "meet_background_color"]

                cobrowse_access_token.allow_meeting_feedback = data[
                    "allow_meeting_feedback"]

                cobrowse_access_token.allow_meeting_end_time = data[
                    "allow_meeting_end_time"]

                cobrowse_access_token.meeting_end_time = data[
                    "meeting_end_time"]

                cobrowse_access_token.allow_capture_screenshots = data[
                    "allow_capture_screenshots"]

                cobrowse_access_token.enable_invite_agent_in_meeting = data[
                    "enable_invite_agent_in_meeting"]

                cobrowse_access_token.allow_video_meeting_only = data[
                    "allow_video_meeting_only"]

                cobrowse_access_token.enable_no_agent_connects_toast_meeting = data[
                    "enable_no_agent_connects_toast_meeting"]

                no_agent_connects_meeting_toast_text = strip_html_tags(data[
                    "no_agent_connects_meeting_toast_text"]).strip()

                if no_agent_connects_meeting_toast_text != "":
                    cobrowse_access_token.no_agent_connects_meeting_toast_text = no_agent_connects_meeting_toast_text

                cobrowse_access_token.no_agent_connects_meeting_toast_threshold = data[
                    "no_agent_connects_meeting_toast_threshold"]

                if cobrowse_access_token.allow_video_meeting_only == True:
                    cobrowse_access_token.allow_agent_to_customer_cobrowsing = False
                    cobrowse_access_token.lead_generation = True
                    cobrowse_access_token.enable_inbound = True

                cobrowse_access_token.save()

                description = "Custom App Configuration Changes - Meeting"
                save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                 description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowsingMetaDetailsMeetingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowsingMetaDetailsMeeting = SaveCobrowsingMetaDetailsMeetingAPI.as_view()


class SaveCobrowsingMetaDetailsGeneralAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":
                active_agent.options = json.dumps(data)
                active_agent.save()

                cobrowse_access_token = active_agent.get_access_token_obj()

                message_on_non_working_hours = remo_html_from_string(strip_html_tags(
                    data["message_on_non_working_hours"]))

                connect_message = remo_html_from_string(
                    strip_html_tags(data["connect_message"]))

                greeting_bubble_text = remo_html_from_string(
                    strip_html_tags(data["greeting_bubble_text"]))

                product_category_message = remo_html_from_string(strip_html_tags(
                    data["message_on_choose_product_category_modal"]))

                message_if_agent_unavailable = remo_html_from_string(strip_html_tags(
                    data["message_if_agent_unavailable"]))

                password_prefix = remo_html_from_string(
                    strip_html_tags(data["password_prefix"]))

                archive_message_on_unassigned_time_threshold = remo_html_from_string(strip_html_tags(
                    data["archive_message_on_unassigned_time_threshold"]))

                cobrowse_access_token.no_agent_connects_toast_text = remo_html_from_string(strip_html_tags(data[
                    "no_agent_connects_toast_text"]))

                cobrowse_access_token.no_agent_connects_toast_reset_message = sanitize_input_string(data[
                    "no_agent_connect_timer_reset_message"])

                cobrowse_access_token.no_agent_connects_toast_reset_count = int(sanitize_input_string(data[
                    "no_agent_connect_timer_reset_count"]))

                cobrowse_access_token.unattended_lead_auto_assignment_counter = int(sanitize_input_string(data[
                    "auto_assign_unattended_lead_transfer_count"]))

                cobrowse_access_token.allow_agent_to_customer_cobrowsing = data[
                    "allow_agent_to_customer_cobrowsing"]

                cobrowse_access_token.allow_agent_to_screen_record_customer_cobrowsing = data[
                    "allow_agent_to_screen_record_customer_cobrowsing"]

                cobrowse_access_token.allow_agent_to_audio_record_customer_cobrowsing = data[
                    "allow_agent_to_audio_record_customer_cobrowsing"]

                cobrowse_access_token.show_floating_easyassist_button = data[
                    "show_floating_easyassist_button"]

                if cobrowse_access_token.show_easyassist_connect_agent_icon != data["show_easyassist_connect_agent_icon"]:
                    cobrowse_access_token.show_easyassist_connect_agent_icon = data[
                        "show_easyassist_connect_agent_icon"]

                cobrowse_access_token.show_only_if_agent_available = data[
                    "show_only_if_agent_available"]
                cobrowse_access_token.floating_button_position = remo_html_from_string(strip_html_tags(
                    data["floating_button_position"]))

                cobrowse_access_token.floating_button_bg_color = "#" + remo_html_from_string(strip_html_tags(
                    data["floating_button_bg_color"]))

                if data["cobrowsing_console_theme_color"] is None:
                    cobrowse_access_token.cobrowsing_console_theme_color = None
                else:
                    cobrowse_access_token.cobrowsing_console_theme_color = remo_html_from_string(strip_html_tags(json.dumps(
                        data["cobrowsing_console_theme_color"])))

                cobrowse_access_token.enable_greeting_bubble = data[
                    "enable_greeting_bubble"]
                cobrowse_access_token.greeting_bubble_auto_popup_timer = data[
                    "greeting_bubble_auto_popup_timer"]
                cobrowse_access_token.greeting_bubble_text = greeting_bubble_text

                cobrowse_access_token.disable_connect_button_if_agent_unavailable = data[
                    "disable_connect_button_if_agent_unavailable"]

                if password_prefix != "":
                    cobrowse_access_token.password_prefix = password_prefix

                if message_if_agent_unavailable != "":
                    cobrowse_access_token.message_if_agent_unavailable = message_if_agent_unavailable

                cobrowse_access_token.enable_non_working_hours_modal_popup = data[
                    "enable_non_working_hours_modal_popup"]

                if message_on_non_working_hours != "":
                    cobrowse_access_token.message_on_non_working_hours = message_on_non_working_hours

                cobrowse_access_token.allow_support_documents = data[
                    "allow_support_documents"]
                cobrowse_access_token.share_document_from_livechat = data[
                    "share_document_from_livechat"]
                cobrowse_access_token.enable_chat_functionality = data[
                    "enable_chat_functionality"]
                cobrowse_access_token.enable_preview_functionality = data[
                    "enable_preview_functionality"]
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
                cobrowse_access_token.inactivity_auto_popup_number = int(
                    data["inactivity_auto_popup_number"])
                cobrowse_access_token.display_agent_profile = data["display_agent_profile"]

                if connect_message != "":
                    cobrowse_access_token.connect_message = connect_message

                cobrowse_access_token.whitelisted_domain = remo_html_from_string(strip_html_tags(
                    data["whitelisted_domain"]))
                cobrowse_access_token.allow_only_support_documents = data[
                    "allow_only_support_documents"]
                cobrowse_access_token.allow_language_support = data[
                    "allow_language_support"]
                cobrowse_access_token.go_live_date = data["go_live_date"]

                if data["allow_language_support"]:
                    save_language_support(
                        active_agent, data["supported_language_list"], LanguageSupport)

                cobrowse_access_token.choose_product_category = data[
                    "choose_product_category"]
                if data["choose_product_category"] or data["enable_tag_based_assignment_for_outbound"]:
                    save_product_category(
                        active_agent, data["product_category_list"], ProductCategory)

                if product_category_message != "":
                    cobrowse_access_token.message_on_choose_product_category_modal = product_category_message

                cobrowse_access_token.no_agent_connects_toast = data[
                    "no_agent_connects_toast"]

                cobrowse_access_token.no_agent_connects_toast_threshold = data[
                    "no_agent_connects_toast_threshold"]

                cobrowse_access_token.show_floating_button_after_lead_search = data[
                    "show_floating_button_after_lead_search"]

                cobrowse_access_token.enable_tag_based_assignment_for_outbound = data[
                    "enable_tag_based_assignment_for_outbound"]

                cobrowse_access_token.enable_followup_leads_tab = data[
                    "enable_followup_leads_tab"]

                cobrowse_access_token.allow_popup_on_browser_leave = data[
                    "allow_popup_on_browser_leave"]

                cobrowse_access_token.enable_recursive_browser_leave_popup = data[
                    "enable_recursive_browser_leave_popup"]

                if data["enable_recursive_browser_leave_popup"] == False:
                    cobrowse_access_token.no_of_times_exit_intent_popup = data[
                        "exit_intent_popup_count"]

                cobrowse_access_token.enable_inbound = data[
                    "enable_inbound"]

                cobrowse_access_token.maximum_active_leads = data[
                    "maximum_active_leads"]

                cobrowse_access_token.maximum_active_leads_threshold = data[
                    "maximum_active_leads_threshold"]

                cobrowse_access_token.deploy_chatbot_flag = data[
                    "deploy_chatbot_flag"]

                cobrowse_access_token.deploy_chatbot_url = data[
                    "deploy_chatbot_url"]

                cobrowse_access_token.font_family = data[
                    "easyassit_font_family"]

                cobrowse_access_token.enable_auto_assign_unattended_lead = data[
                    "enable_auto_assign_unattended_lead"]
                cobrowse_access_token.enable_auto_assign_to_one_agent = data[
                    "enable_auto_assign_to_one_agent"]
                cobrowse_access_token.assign_agent_under_same_supervisor = data[
                    "assign_agent_under_same_supervisor"]
                cobrowse_access_token.auto_assign_unattended_lead_timer = int(data[
                    "auto_assign_unattended_lead_timer"])
                auto_assign_unattended_lead_message = remo_html_from_string(strip_html_tags(data[
                    "auto_assign_unattended_lead_message"].strip()))

                cobrowse_access_token.auto_assigned_unattended_lead_archive_timer = int(sanitize_input_string(
                    data["auto_assigned_unattended_lead_archive_timer"]))

                auto_assign_lead_end_session_message = remo_html_from_string(strip_html_tags(data[
                    "auto_assign_lead_end_session_message"].strip()))
                if auto_assign_unattended_lead_message != "":
                    cobrowse_access_token.auto_assign_unattended_lead_message = auto_assign_unattended_lead_message
                if auto_assign_lead_end_session_message != "":
                    cobrowse_access_token.auto_assign_lead_end_session_message = auto_assign_lead_end_session_message

                cobrowse_access_token.floating_button_left_right_position = data[
                    "floating_button_left_right_position"]
                cobrowse_access_token.enable_chat_bubble = data["enable_chat_bubble"]

                if(data["enable_auto_offline_agent"] == True):
                    cobrowse_access_token.disable_auto_offline_agent = False
                else:
                    cobrowse_access_token.disable_auto_offline_agent = True

                if cobrowse_access_token.allow_agent_to_customer_cobrowsing == True:
                    cobrowse_access_token.enable_inbound = False
                    cobrowse_access_token.enable_greeting_bubble = False
                    cobrowse_access_token.lead_generation = False
                    cobrowse_access_token.show_cobrowsing_meeting_lobby = False
                    cobrowse_access_token.enable_no_agent_connects_toast_meeting = False
                    cobrowse_access_token.allow_video_meeting_only = False

                if cobrowse_access_token.enable_inbound == True or cobrowse_access_token.lead_generation == True:
                    cobrowse_access_token.allow_agent_to_customer_cobrowsing = False

                cobrowse_access_token.archive_message_on_unassigned_time_threshold = archive_message_on_unassigned_time_threshold

                cobrowse_access_token.archive_on_unassigned_time_threshold = int(
                    remo_html_from_string(strip_html_tags(data["archive_on_unassigned_time_threshold"])))

                cobrowse_access_token.save()

                disable_inbound_cobrowsing_features(cobrowse_access_token)

                description = "Custom App Configuration Changes - General"
                save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                 description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowsingMetaDetailsGeneralAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowsingMetaDetailsGeneral = SaveCobrowsingMetaDetailsGeneralAPI.as_view()


class SaveCobrowsingMetaCustomerDetailsCobrowsingAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":

                cobrowse_access_token = active_agent.get_access_token_obj()

                masked_field_warning_text = strip_html_tags(
                    data["masked_field_warning_text"])
                if masked_field_warning_text != "":
                    cobrowse_access_token.masked_field_warning_text = masked_field_warning_text

                cobrowse_access_token.enable_masked_field_warning = data[
                    "enable_masked_field_warning"]

                assistant_message = remo_html_from_string(
                    data["assistant_message"])
                if assistant_message != "":
                    cobrowse_access_token.assist_message = assistant_message

                cobrowse_access_token.show_verification_code_modal = data[
                    "show_verification_code_modal"]

                cobrowse_access_token.enable_verification_code_popup = data[
                    "enable_verification_code_popup"]

                if data["show_verification_code_modal"]:
                    proxy_config_obj = cobrowse_access_token.get_proxy_config_obj()
                    proxy_config_obj.enable_proxy_cobrowsing = False
                    proxy_config_obj.save(update_fields=["enable_proxy_cobrowsing"])

                cobrowse_access_token.save()

                description = "Custom App Configuration Changes - Cobrowsing"
                save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                 description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowsingMetaCustomerDetailsCobrowsingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowsingMetaCustomerDetailsCobrowsing = SaveCobrowsingMetaCustomerDetailsCobrowsingAPI.as_view()


class SaveCobrowsingMetaCustomerDetailsGeneralAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":

                cobrowse_access_token = active_agent.get_access_token_obj()

                cobrowse_access_token.font_family = data[
                    "easyassit_font_family"]

                cobrowse_access_token.save()

                description = "Custom App Configuration Changes - General"
                save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                 description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowsingMetaCustomerDetailsGeneralAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowsingMetaCustomerDetailsGeneral = SaveCobrowsingMetaCustomerDetailsGeneralAPI.as_view()


class ResetCobrowsingMetaDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":
                if data["reset"]:
                    cobrowse_access_token = active_agent.get_access_token_obj()
                    popup_configurations_obj = get_easyassist_popup_configurations_obj(
                        cobrowse_access_token, EasyAssistPopupConfigurations)

                    if data["general"] == True:
                        cobrowse_access_token.show_floating_easyassist_button = True
                        cobrowse_access_token.show_easyassist_connect_agent_icon = False
                        cobrowse_access_token.show_only_if_agent_available = False
                        cobrowse_access_token.floating_button_position = "left"
                        cobrowse_access_token.floating_button_bg_color = "#0254D7"
                        cobrowse_access_token.cobrowsing_console_theme_color = None
                        cobrowse_access_token.disable_connect_button_if_agent_unavailable = False
                        cobrowse_access_token.message_if_agent_unavailable = AGENT_UNAVAILABLE_MESSAGE
                        cobrowse_access_token.start_time = datetime.datetime.strptime(
                            "00:00", '%H:%M').time()
                        cobrowse_access_token.end_timeble = datetime.datetime.strptime(
                            "23:59", '%H:%M').time()
                        cobrowse_access_token.enable_non_working_hours_modal_popup = False
                        cobrowse_access_token.message_on_non_working_hours = NON_WORKING_HOURS_MESSAGE
                        cobrowse_access_token.allow_support_documents = True
                        cobrowse_access_token.share_document_from_livechat = True
                        cobrowse_access_token.enable_chat_functionality = True
                        cobrowse_access_token.enable_preview_functionality = True
                        cobrowse_access_token.enable_chat_bubble = True
                        cobrowse_access_token.chat_bubble_icon_source = ""
                        cobrowse_access_token.enable_lead_status = True
                        cobrowse_access_token.field_stuck_event_handler = False
                        cobrowse_access_token.field_recursive_stuck_event_check = False
                        cobrowse_access_token.get_sharable_link = False
                        cobrowse_access_token.lead_generation = True
                        cobrowse_access_token.field_stuck_timer = 5
                        cobrowse_access_token.inactivity_auto_popup_number = 5
                        cobrowse_access_token.display_agent_profile = True
                        cobrowse_access_token.connect_message = CONNECT_MESSAGE
                        cobrowse_access_token.whitelisted_domain = ""
                        cobrowse_access_token.allow_only_support_documents = False
                        cobrowse_access_token.allow_language_support = False
                        cobrowse_access_token.choose_product_category = False
                        cobrowse_access_token.message_on_choose_product_category_modal = MESSAGE_ON_CHOOSE_PRODUCT_CATEGORY_MODAL
                        cobrowse_access_token.no_agent_connects_toast = False
                        cobrowse_access_token.no_agent_connects_toast_threshold = 1
                        cobrowse_access_token.no_agent_connects_toast_text = NO_AGENT_CONNECTS_TOAST_TEXT
                        cobrowse_access_token.no_agent_connects_toast_reset_message = NO_AGENT_CONNECTS_TOAST_RESET_MESSAGE
                        cobrowse_access_token.no_agent_connects_toast_reset_count = 2
                        cobrowse_access_token.show_floating_button_after_lead_search = True
                        cobrowse_access_token.enable_tag_based_assignment_for_outbound = False
                        cobrowse_access_token.enable_followup_leads_tab = True
                        cobrowse_access_token.allow_popup_on_browser_leave = False
                        cobrowse_access_token.no_of_times_exit_intent_popup = 1
                        cobrowse_access_token.enable_recursive_browser_leave_popup = False
                        cobrowse_access_token.enable_inbound = True
                        cobrowse_access_token.maximum_active_leads = True
                        cobrowse_access_token.maximum_active_leads_threshold = 3
                        cobrowse_access_token.password_prefix = DEFAULT_PASSWORD_PREFIX
                        cobrowse_access_token.deploy_chatbot_flag = False
                        cobrowse_access_token.deploy_chatbot_url = ""
                        cobrowse_access_token.font_family = "Silka"
                        cobrowse_access_token.floating_button_left_right_position = 0
                        cobrowse_access_token.disable_auto_offline_agent = False
                        cobrowse_access_token.enable_request_in_queue = True
                        cobrowse_access_token.enable_auto_assign_unattended_lead = False
                        cobrowse_access_token.enable_auto_assign_to_one_agent = True
                        cobrowse_access_token.unattended_lead_auto_assignment_counter = 2
                        cobrowse_access_token.assign_agent_under_same_supervisor = False
                        cobrowse_access_token.auto_assign_unattended_lead_timer = 100
                        cobrowse_access_token.auto_assign_unattended_lead_message = AUTO_ASSIGN_UNATTENDED_LEAD_MESSAGE
                        cobrowse_access_token.auto_assigned_unattended_lead_archive_timer = 10
                        cobrowse_access_token.auto_assign_lead_end_session_message = AUTO_ASSIGN_LEAD_END_SESSION_MESSAGE
                        cobrowse_access_token.allow_agent_to_customer_cobrowsing = False
                        cobrowse_access_token.allow_agent_to_screen_record_customer_cobrowsing = False
                        cobrowse_access_token.allow_agent_to_audio_record_customer_cobrowsing = False
                        cobrowse_access_token.archive_on_unassigned_time_threshold = 10
                        cobrowse_access_token.archive_message_on_unassigned_time_threshold = UNASSIGNED_LEAD_DEFAULT_MESSAGE
                        cobrowse_access_token.source_easyassist_connect_agent_icon = "null"
                        cobrowse_access_token.greeting_bubble_auto_popup_timer = 5
                        cobrowse_access_token.enable_greeting_bubble = True
                        cobrowse_access_token.greeting_bubble_text = "Welcome, Please click here to request for agent assistance."
                        popup_configurations_obj.enable_url_based_inactivity_popup = False
                        popup_configurations_obj.enable_url_based_exit_intent_popup = False
                        cobrowse_access_token.allow_connect_with_virtual_agent_code = False
                        cobrowse_access_token.connect_with_virtual_agent_code_mandatory = False
                        proxy_config_obj = cobrowse_access_token.get_proxy_config_obj()
                        proxy_config_obj.enable_proxy_cobrowsing = False
                        proxy_config_obj.proxy_link_expire_time = 60
                        proxy_config_obj.save(update_fields=["enable_proxy_cobrowsing", "proxy_link_expire_time"])
                        
                    if data["cobrowse"] == True:
                        cobrowse_access_token.enable_edit_access = False
                        cobrowse_access_token.enable_screenshot_agent = True
                        cobrowse_access_token.enable_invite_agent_in_cobrowsing = True
                        cobrowse_access_token.enable_session_transfer_in_cobrowsing = True
                        cobrowse_access_token.allow_screen_recording = False
                        cobrowse_access_token.recording_expires_in_days = 30
                        cobrowse_access_token.lead_conversion_checkbox_text = "Lead has been closed successfully."
                        cobrowse_access_token.allow_screen_sharing_cobrowse = False
                        cobrowse_access_token.enable_predefined_remarks = False
                        cobrowse_access_token.enable_predefined_remarks_with_buttons = False
                        cobrowse_access_token.predefined_remarks = "[]"
                        cobrowse_access_token.predefined_remarks_with_buttons = ""
                        cobrowse_access_token.enable_agent_connect_message = False
                        cobrowse_access_token.agent_connect_message = AGENT_CONNECT_MESSAGE
                        cobrowse_access_token.enable_masked_field_warning = False
                        cobrowse_access_token.masked_field_warning_text = MASKED_FIELD_WARNING_TEXT
                        cobrowse_access_token.enable_voip_calling = False
                        cobrowse_access_token.customer_initiate_voice_call = False
                        cobrowse_access_token.enable_voip_with_video_calling = True
                        cobrowse_access_token.customer_initiate_video_call_as_pip = False
                        cobrowse_access_token.customer_initiate_video_call = False
                        cobrowse_access_token.voip_calling_message = VOIP_CALLING_MESSAGE
                        cobrowse_access_token.voip_with_video_calling_message = VOIP_WITH_VIDEO_CALLING_MESSAGE
                        cobrowse_access_token.enable_auto_voip_calling_for_first_time = True
                        cobrowse_access_token.enable_auto_voip_with_video_calling_for_first_time = True
                        cobrowse_access_token.masking_type = "partial-masking"
                        cobrowse_access_token.allow_cobrowsing_meeting = False
                        cobrowse_access_token.show_verification_code_modal = True
                        cobrowse_access_token.assist_message = ASSIST_MESSAGE
                        cobrowse_access_token.enable_verification_code_popup = True
                        cobrowse_access_token.urls_consider_lead_converted = ""
                        cobrowse_access_token.restricted_urls = ""
                        cobrowse_access_token.archive_on_common_inactivity = True
                        cobrowse_access_token.archive_on_common_inactivity_threshold = 20
                        cobrowse_access_token.enable_low_bandwidth_cobrowsing = True
                        cobrowse_access_token.enable_manual_switching = False
                        cobrowse_access_token.low_bandwidth_cobrowsing_threshold = 1024
                        cobrowse_access_token.drop_link_expiry_time = DEFAULT_DROP_LINK_EXPIRY_TIME
                        cobrowse_access_token.enable_smart_agent_assignment = False
                        cobrowse_access_token.smart_agent_assignment_reconnecting_window = 10

                    if data["meeting"] == True:
                        cobrowse_access_token.proxy_server = ""
                        cobrowse_access_token.meeting_host_url = "meet-uat.allincall.in"
                        cobrowse_access_token.meeting_default_password = ""
                        cobrowse_access_token.show_cobrowsing_meeting_lobby = True
                        cobrowse_access_token.meet_background_color = "#474747"
                        cobrowse_access_token.allow_meeting_feedback = True
                        cobrowse_access_token.allow_meeting_end_time = False
                        cobrowse_access_token.meeting_end_time = "60"
                        cobrowse_access_token.allow_capture_screenshots = True
                        cobrowse_access_token.enable_invite_agent_in_meeting = True
                        cobrowse_access_token.allow_video_meeting_only = False
                        cobrowse_access_token.enable_no_agent_connects_toast_meeting = True
                        cobrowse_access_token.no_agent_connects_meeting_toast_text = NO_AGENT_CONNECTS_TOAST_TEXT_MEETING
                        cobrowse_access_token.no_agent_connects_meeting_toast_threshold = 1

                    cobrowse_access_token.save()
                    popup_configurations_obj.save()

                    description = "Custom App Configuration has been reset"
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)

                    add_audit_trail(
                        "EASYASSISTAPP",
                        active_agent.user,
                        "Change-App-Config",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

                    response["status"] = 200
                    response["message"] = "success"
                else:
                    response["status"] = 300
            else:
                response["status"] = 401

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ResetCobrowsingMetaDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ResetCobrowsingMetaDetails = ResetCobrowsingMetaDetailsAPI.as_view()


class DeleteCobrowserLogoAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":

                cobrowse_access_token = active_agent.get_access_token_obj()
                cobrowse_access_token.source_easyassist_cobrowse_logo = ""
                cobrowse_access_token.save()
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteCobrowserLogoAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteCobrowserLogo = DeleteCobrowserLogoAPI.as_view()


class UploadCobrowserLogoAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":

                cobrowse_access_token = active_agent.get_access_token_obj()

                filename = strip_html_tags(data["filename"])
                base64_data = strip_html_tags(data["base64_file"])

                filename = generate_random_key(
                    10) + "_" + filename.replace(" ", "")

                file_path = "files/" + filename

                file_extention = file_path.split(".")[-1]
                file_extention = file_extention.lower()
                allowed_files_list = ["png", "jpg", "jpeg", "bmp",
                                      "gif", "tiff", "exif", "jfif", "webm", "mpg", "jpe"]
                if file_extention in allowed_files_list:
                    media_type = "image"
                else:
                    media_type = None

                if media_type == None or check_malicious_file_from_filename(filename, allowed_files_list) or check_malicious_file_from_content(base64_data, allowed_files_list):
                    response["status"] = 300
                else:
                    fh = open(file_path, "wb")
                    fh.write(base64.b64decode(base64_data))
                    fh.close()
                    cobrowse_access_token.source_easyassist_cobrowse_logo = file_path
                    cobrowse_access_token.save()

                    response["status"] = 200
                    response["message"] = "success"
                    response["file_path"] = file_path
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadCobrowserLogoAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadCobrowserLogo = UploadCobrowserLogoAPI.as_view()


class UploadConnectWithAgentIconAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

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

                allowed_files_list = ["png", "jpg", "jpeg", "jpe",
                                      "svg", "bmp", "gif", "tiff", "exif", "jfif"]
                if file_extention in allowed_files_list:
                    media_type = "image"
                else:
                    media_type = None

                if media_type == None or check_malicious_file_from_filename(filename, allowed_files_list) or check_malicious_file_from_content(base64_data, allowed_files_list):
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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadConnectWithAgentIcon = UploadConnectWithAgentIconAPI.as_view()


class SaveAgentCommentsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            agent_comments = strip_html_tags(data["agent_comments"])
            agent_comments = remo_html_from_string(agent_comments)
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            active_agent = get_active_agent_obj(request, CobrowseAgent)
            if cobrowse_io.agent_comments == "":
                cobrowse_io.agent_comments = agent_comments
            cobrowse_io.save()
            current_session_comments = CobrowseAgentComment.objects.filter(
                cobrowse_io=cobrowse_io)
            if current_session_comments.exists() == False:
                save_agent_closing_comments_cobrowseio(
                    cobrowse_io, active_agent, agent_comments, CobrowseAgentComment)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveAgentCommentsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveAgentComments = SaveAgentCommentsAPI.as_view()


class SearchCobrowsingLeadAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logger.info("Inside SearchCobrowsingLeadAPI",
                    extra={'AppName': 'EasyAssist'})
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            logger.info("Request: " + json.dumps(data),
                        extra={'AppName': 'EasyAssist'})

            search_value = strip_html_tags(data["search_value"])
            search_value = search_value.strip().lower()
            md5_primary_id = hashlib.md5(search_value.encode()).hexdigest()

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)
            cobrowse_access_token = active_agent.get_access_token_obj()

            cobrowse_io_list = []

            if "session_id_list" in data:
                cobrowse_io_list = CobrowseIO.objects.filter(
                    session_id__in=data["session_id_list"])
            else:
                cobrowse_leads = CobrowseCapturedLeadData.objects.filter(
                    primary_value=md5_primary_id)

                cobrowse_io_list = CobrowseIO.objects.filter(is_lead=True,
                                                             is_archived=False,
                                                             captured_lead__in=cobrowse_leads,
                                                             access_token=cobrowse_access_token,
                                                             agent=None).order_by('-last_update_datetime')

                if cobrowse_access_token.enable_tag_based_assignment_for_outbound:
                    cobrowse_io_list = cobrowse_io_list.filter(
                        product_category__in=active_agent.product_category.filter(is_deleted=False))

            show_verification_code = False
            allow_cobrowsing_meeting = False
            allow_video_meeting_only = False
            cobrowse_io_details = []

            for cobrowse_io in cobrowse_io_list:
                allow_video_meeting_only = cobrowse_io.access_token.allow_video_meeting_only
                allow_cobrowsing_meeting = cobrowse_io.access_token.allow_cobrowsing_meeting

                est = pytz.timezone(settings.TIME_ZONE)

                datetime = cobrowse_io.last_update_datetime.astimezone(
                    est).strftime("%d %b %Y %I:%M %p")

                is_active = cobrowse_io.is_active_timer() and cobrowse_io.is_active

                show_verification_code = cobrowse_io.access_token.enable_verification_code_popup

                show_verification_code_modal = cobrowse_io.access_token.show_verification_code_modal

                OTP = "-"
                if is_active and cobrowse_io.otp_validation != None and show_verification_code_modal == True:
                    OTP = cobrowse_io.otp_validation

                if cobrowse_io.is_lead:
                    if cobrowse_io.agent == None:
                        cobrowse_io.agent = active_agent
                        for cobrowse_lead in cobrowse_io.captured_lead.all():
                            if cobrowse_lead in cobrowse_leads:
                                cobrowse_lead.agent_searched = True
                                cobrowse_lead.save()
                    if show_verification_code_modal == False:
                        cobrowse_io.allow_agent_cobrowse = "true"
                    cobrowse_io.save()

                cobrowse_io_details.append({
                    "session_id": str(cobrowse_io.session_id),
                    "is_active": is_active,
                    "datetime": datetime,
                    "agent_assistant_request_status": cobrowse_io.agent_assistant_request_status,
                    "agent_meeting_request_status": cobrowse_io.agent_meeting_request_status,
                    "allow_agent_meeting": cobrowse_io.allow_agent_meeting,
                    "allow_agent_cobrowse": cobrowse_io.allow_agent_cobrowse,
                    "otp": OTP,
                    "share_client_session": cobrowse_io.share_client_session
                })

            response["status"] = 200
            response["message"] = "success"
            response["cobrowse_io_details"] = cobrowse_io_details[:5]
            response["show_verification_code"] = show_verification_code
            response["allow_cobrowsing_meeting"] = allow_cobrowsing_meeting
            response["allow_video_meeting_only"] = allow_video_meeting_only
            logger.info("Response: " + json.dumps(response),
                        extra={'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SearchCobrowsingLeadAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        logger.info("Successfully exited from SearchCobrowsingLeadAPI", extra={
                    'AppName': 'EasyAssist'})
        return Response(data=response)


SearchCobrowsingLead = SearchCobrowsingLeadAPI.as_view()


class AssignCobrowsingLeadAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            active_agent = get_active_agent_obj(request, CobrowseAgent)
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            if cobrowse_io.allow_agent_cobrowse == "true":
                cobrowse_io.agent = active_agent
                cobrowse_io.save()

            response["status"] = 200
            response["message"] = "success"
            response[
                "allow_screen_sharing_cobrowse"] = cobrowse_io.access_token.allow_screen_sharing_cobrowse
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AssignCobrowsingLeadAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AssignCobrowsingLead = AssignCobrowsingLeadAPI.as_view()


class AssignCobrowsingSessionAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            agent_id = strip_html_tags(data["agent_id"])

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            cobrowse_agent = CobrowseAgent.objects.get(pk=int(agent_id))

            product_name = "Cogno Cobrowse"
            cobrowse_config_obj = get_developer_console_cobrowsing_settings()
            if cobrowse_config_obj:
                product_name = cobrowse_config_obj.cobrowsing_title_text

            if cobrowse_agent.is_active == True:
                cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
                cobrowse_io.agent = cobrowse_agent
                if cobrowse_io.access_token.enable_auto_assign_unattended_lead:
                    cobrowse_io.last_agent_assignment_datetime = timezone.now()
                cobrowse_io.save()

                notification_message = "Hi, " + cobrowse_agent.user.username + \
                    "! A customer is waiting for you to connect on " + product_name + "."
                NotificationManagement.objects.create(show_notification=True,
                                                      agent=cobrowse_agent,
                                                      notification_message=notification_message,
                                                      cobrowse_io=cobrowse_io,
                                                      product_name=product_name)

                send_notification_to_agent(
                    cobrowse_agent, NotificationManagement)

                category = "session_transfer"
                description = "Session is transferred to " + \
                    str(cobrowse_agent.user.username)
                save_system_audit_trail(category, description, cobrowse_io,
                                        cobrowse_io.access_token, SystemAuditTrail, active_agent)

                response["status"] = 200
                response["message"] = "success"
            else:
                response["status"] = 400
                response["message"] = "failed"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AssignCobrowsingSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AssignCobrowsingSession = AssignCobrowsingSessionAPI.as_view()


class SupervisoAssignCobrowsingLeadAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            agent_id = strip_html_tags(data["agent_id"])
            supervisor = get_active_agent_obj(request, CobrowseAgent)

            if supervisor.role == "supervisor":
                cobrowse_io_obj = CobrowseIO.objects.get(session_id=session_id)
                transfer_agent = CobrowseAgent.objects.filter(
                    pk=int(agent_id)).first()
                current_agent = cobrowse_io_obj.agent
                if cobrowse_io_obj.access_token.maximum_active_leads:
                    agent_active_sessions = CobrowseIO.objects.filter(agent=transfer_agent, is_archived=False).count()
                    if agent_active_sessions >= cobrowse_io_obj.access_token.maximum_active_leads_threshold:
                        response["status"] = 501
                        response["message"] = str(transfer_agent.user.username) + \
                                        " has reached maximum lead capacity. Please try again later."
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)
                
                if transfer_agent and transfer_agent.is_active == True:
                    if cobrowse_io_obj.cobrowsing_start_datetime == None and cobrowse_io_obj.is_agent_request_for_cobrowsing == False and cobrowse_io_obj.is_archived == False:
                        if transfer_agent == current_agent:
                            response["status"] = 301
                            response["message"] = "Session is already assigned to " + \
                                str(current_agent.user.username)
                        else:
                            cobrowse_io_obj.agent = transfer_agent
                            if cobrowse_io_obj.access_token.enable_auto_assign_unattended_lead:
                                cobrowse_io_obj.last_agent_assignment_datetime = timezone.now()
                            cobrowse_io_obj.save()

                            product_name = get_product_name()
                            
                            create_notification_objects(transfer_agent, cobrowse_io_obj, product_name, NotificationManagement)
                            
                            send_notification_to_agent(
                                transfer_agent, NotificationManagement)

                            notification_message = "Hi, " + current_agent.user.username + \
                                "! Your lead has been transferred to " + str(transfer_agent.user.username) + \
                                " by your supervisor " + \
                                str(supervisor.user.username) + "."
                                
                            create_notification_objects(transfer_agent, cobrowse_io_obj, product_name, NotificationManagement, notification_message)

                            send_notification_to_agent(
                                current_agent, NotificationManagement)

                            category = "session_transfer_by_supervisor"
                            description = str(supervisor.user.username) + " transferred the session from " + \
                                str(current_agent.user.username) + \
                                " to " + str(transfer_agent.user.username)
                            save_system_audit_trail(category, description, cobrowse_io_obj,
                                                    cobrowse_io_obj.access_token, SystemAuditTrail, supervisor)

                            response["status"] = 200
                    else:
                        if cobrowse_io_obj.is_archived:
                            response["status"] = 304
                            response["message"] = "Session cannot be transferred because the session \
                                has already been archived."
                        else:
                            response["status"] = 303
                            response["message"] = "Session cannot be transferred to " + \
                                str(transfer_agent.user.username) + " because " + str(current_agent.user.username) + \
                                " has already joined the session"
                else:
                    response["status"] = 302
                    if not transfer_agent:
                        response["message"] = "Invalid Agent"
                    else:
                        response["message"] = "Agent " + \
                            str(transfer_agent.user.username) + " is offline"
            else:
                response["status"] = 401

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SupervisoAssignCobrowsingLeadAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SupervisoAssignCobrowsingLead = SupervisoAssignCobrowsingLeadAPI.as_view()


class RequestCobrowsingAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            active_agent = get_active_agent_obj(request, CobrowseAgent)

            otp = random_with_n_digits(4)

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            cobrowse_io.agent_assistant_request_status = True
            cobrowse_io.is_agent_request_for_cobrowsing = True
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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


RequestCobrowsing = RequestCobrowsingAPI.as_view()


class MarkLeadInactiveAPI(APIView):

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
            cobrowse_io_objs = CobrowseIO.objects.filter(
                agent=active_agent, is_lead=True, allow_agent_cobrowse="true", is_agent_connected=True, is_archived=False)

            for cobrowse_io_obj in cobrowse_io_objs:
                cobrowse_io_obj.is_archived = True
                cobrowse_io_obj.is_agent_connected = False
                if cobrowse_io_obj.session_archived_cause == None:
                    cobrowse_io_obj.session_archived_cause = "AGENT_ENDED"
                    cobrowse_io_obj.session_archived_datetime = timezone.now()
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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


MarkLeadInactive = MarkLeadInactiveAPI.as_view()


class ChangeAgentActivateStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            agent_id_list = data["agent_id_list"]
            activate = data["activate"]

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            if active_agent.role == "admin" and (activate == True or activate == False):
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
                    agents_list = []
                    supervisors_list = []
                    admin_allys_list = []
                    if active_agent.role == "admin":
                        agents_list = get_list_agents_under_admin(
                            admin_user=active_agent, is_active=None, is_account_active=None)
                        supervisors_list = get_list_supervisor_under_admin(
                            admin_user=active_agent, is_active=None, is_account_active=None)
                        admin_allys_list = get_list_admin_ally(
                            active_agent, is_active=None, is_account_active=None)
                        for admin_ally in admin_allys_list:
                            supervisors_list += get_list_supervisor_under_admin(
                                admin_ally, is_active=None, is_account_active=None)

                    for agent_id in agent_id_list:
                        agent = CobrowseAgent.objects.get(pk=int(agent_id))
                        if agent in agents_list or agent in supervisors_list or agent in admin_allys_list:
                            change_agent_is_account_active_flag(
                                activate, active_agent, agent, request, data, CobrowsingAuditTrail)
                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ChangeAgentActivateStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ChangeAgentActivateStatus = ChangeAgentActivateStatusAPI.as_view()


class GetCaptchaAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            captcha = []
            with open(settings.BASE_DIR + "/EasyAssistApp/captcha.py") as captcha_py:
                captcha = captcha_py.read()
                captcha = ast.literal_eval(captcha)

            selected_captcha = random.choice(captcha)

            response["status"] = 200
            response["message"] = "success"
            response["file"] = "/static/EasyAssistApp/captcha_images/" + \
                selected_captcha["file"]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCaptchaAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCaptcha = GetCaptchaAPI.as_view()


class AgentResetPasswordAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Invalid username or password"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            username = strip_html_tags(data["username"])
            username = remo_html_from_string(username)
            username = remo_special_tag_from_string(username)
            captcha = strip_html_tags(data["captcha"])
            user_captcha = strip_html_tags(data["user_captcha"])
            user_captcha = remo_html_from_string(user_captcha)
            platform_url = strip_html_tags(data["platform_url"])
            platform_url = remo_html_from_string(platform_url)

            user_captcha = generate_md5(user_captcha)
            captcha, _ = captcha.split(".")

            if user_captcha != captcha:
                response["status"] = 101
                response["message"] = "Invalid captcha"
            else:
                user_obj = None
                try:
                    user_obj = User.objects.get(username=username)
                except Exception:
                    pass

                if user_obj != None:
                    password = generate_random_password()

                    thread = threading.Thread(target=send_password_over_email, args=(
                        user_obj.username, user_obj.first_name, password, platform_url, ), daemon=True)
                    thread.start()

                    user_obj.set_password(password)
                    user_obj.save()
                    response["status"] = 200
                    response[
                        "message"] = "If email/username exists in our DB, an email for your password reset will be sent!"
                else:
                    response["status"] = 101
                    response[
                        "message"] = "If email/username exists in our DB, an email for your password reset will be sent!"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AgentResetPasswordAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AgentResetPassword = AgentResetPasswordAPI.as_view()


class ShareCobrowsingSessionAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["id"])
            id = remo_html_from_string(id)
            support_agents = data["support_agents"]
            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            agent_admin = cobrowse_io.access_token.agent
            access_token_obj = cobrowse_io.access_token
            agents = get_list_agents_under_admin(agent_admin, is_active=True)

            if access_token_obj.enable_session_transfer_in_cobrowsing:
                user_obj = User.objects.get(pk=int(support_agents[0]))
                transferred_agent_obj = CobrowseAgent.objects.get(user=user_obj)
                active_transferred_agent_requests = CobrowseIOTransferredAgentsLogs.objects.filter(cobrowse_io=cobrowse_io, transferred_agent=transferred_agent_obj, cobrowse_request_type="transferred", transferred_status="")
                if active_transferred_agent_requests:
                    response["status"] = 301
                    response["message"] = "success"
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

            invited_agent_details_obj = None
            if access_token_obj.enable_invite_agent_in_cobrowsing:
                invited_agent_details_objs = CobrowseIOInvitedAgentsDetails.objects.filter(
                    cobrowse_io=cobrowse_io)
                if invited_agent_details_objs:
                    invited_agent_details_obj = invited_agent_details_objs[0]
                else:
                    invited_agent_details_obj = CobrowseIOInvitedAgentsDetails.objects.create(
                        cobrowse_io=cobrowse_io)
                
                invited_agent_log_io = CobrowseIOTransferredAgentsLogs.objects.create(cobrowse_io=cobrowse_io)
                invited_agent_log_io.inviting_agent = get_active_agent_obj(request, CobrowseAgent)
                invited_agent_log_io.transferred_agent = CobrowseAgent.objects.get(user=User.objects.get(pk=int(support_agents[0])))
                invited_agent_log_io.cobrowse_request_type = "invited"
                invited_agent_log_io.save()
                
            agent_username_list = []
            for user_id in support_agents:
                user_obj = User.objects.get(pk=int(user_id))
                cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
                if cobrowse_agent in agents:
                    cobrowse_io.support_agents.add(cobrowse_agent)
                    if invited_agent_details_obj != None:
                        invited_agent_details_obj.support_agents_invited.add(
                            cobrowse_agent)
                    agent_username_list.append(cobrowse_agent.user.username)

            if invited_agent_details_obj != None:
                invited_agent_details_obj.save()

            shared_agent_details = ", ".join(agent_username_list)
            category = "session_details"
            if len(agent_username_list) == 1:
                description = "Agent " + shared_agent_details + " was invited to the session"
            else:
                description = "Agents " + shared_agent_details + " were invited to the session"

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, active_agent)
               
            cobrowse_io.save()
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ShareCobrowsingSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ShareCobrowsingSession = ShareCobrowsingSessionAPI.as_view()


class GetListOfSupportAgentsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
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
                if agent.user.username != request.user.username and agent != cobrowse_io.agent:

                    cobrowse_io_objs = CobrowseIO.objects.filter(
                        is_archived=False, agent=agent)

                    cobrowse_io_support_objs = CobrowseIO.objects.filter(
                        is_archived=False, support_agents=agent)
                    
                    cobrowse_io_objs = cobrowse_io_objs | cobrowse_io_support_objs
                    cobrowse_io_objs = cobrowse_io_objs.order_by(
                        "-request_datetime")

                    total_active_session = cobrowse_io_objs.filter(
                        allow_agent_cobrowse="true").count()
                    if total_active_session == 0:
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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetListOfSupportAgents = GetListOfSupportAgentsAPI.as_view()


class GetSupportMaterialAgentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["id"])
            id = remo_html_from_string(id)

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            agent_admin = cobrowse_io.access_token.agent

            agents_for_support_document = get_supervisor_from_active_agent(
                active_agent, CobrowseAgent)
            agents_for_support_document.append(agent_admin)

            support_document_objs = SupportDocument.objects.filter(
                agent__in=agents_for_support_document, is_usable=True, is_deleted=False)

            support_document = []
            for support_document_obj in support_document_objs:
                file_path = "easy-assist/download-file/" + \
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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetSupportMaterialAgent = GetSupportMaterialAgentAPI.as_view()


def ExportCapturedData(request, meta_data_pk):
    try:
        if request.user.is_authenticated and request.method == "GET":

            type = request.GET["type"]
            type = remo_html_from_string(type)

            meta_data_obj = CobrowsingSessionMetaData.objects.get(
                pk=int(meta_data_pk))
            path_to_file = None

            if type == "html":
                path_to_file = meta_data_obj.content
            elif type == "img":
                path_to_file = meta_data_obj.content
                logger.info("export as image", extra={'AppName': 'EasyAssist'})

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
                    return response
        else:
            return HttpResponse(500)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Export Captured Data: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(500)


class GetCobrowsingAgentCommentsAPI(APIView):

    permission_classes = [IsAuthenticated]

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
                    est).strftime("%d-%b-%Y %I:%M %p")

                comment_desc = "-"
                if len(cobrowse_agent_comment.comment_desc) > 0:
                    comment_desc = cobrowse_agent_comment.comment_desc

                agent_subcomments = "-"
                if cobrowse_agent_comment.agent_subcomments:
                    agent_subcomments = cobrowse_agent_comment.agent_subcomments

                agent_comments_list.append({
                    "id": cobrowse_agent_comment.pk,
                    "agent": cobrowse_agent_comment.agent.user.username,
                    "comments": cobrowse_agent_comment.agent_comments,
                    "subcomments": agent_subcomments,
                    "comment_desc": comment_desc,
                    "datetime": datetime
                })

            response["status"] = 200
            response["message"] = "success"
            response["is_last_page"] = is_last_page
            response["agent_comments_list"] = agent_comments_list
            response[
                "enable_predefined_remarks"] = cobrowse_io.access_token.enable_predefined_remarks
            response[
                "enable_predefined_subremarks"] = cobrowse_io.access_token.enable_predefined_subremarks
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCobrowsingAgentCommentsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCobrowsingAgentComments = GetCobrowsingAgentCommentsAPI.as_view()


class GetSystemAuditTrailBasicActivityAPI(APIView):

    permission_classes = [IsAuthenticated]

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
                    est).strftime("%d-%b-%Y %I:%M %p")

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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetSystemAuditTrailBasicActivity = GetSystemAuditTrailBasicActivityAPI.as_view()


class SwitchAgentModeAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            status = data["active_status"]

            if status == True or status == False:

                active_agent = get_active_agent_obj(
                    request, CobrowseAgent)

                if active_agent.is_switch_allowed and status:
                    active_agent.role = "agent"
                    active_agent.agents.add(active_agent)
                    active_agent.is_active = True
                elif active_agent.is_switch_allowed and not status:
                    if active_agent.get_access_token_obj().agent == active_agent:
                        active_agent.role = "admin"
                    else:
                        active_agent.role = "supervisor"
                    active_agent.is_active = False
                    active_agent.agents.remove(active_agent)

                active_agent.save()
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SwitchAgentModeAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SwitchAgentMode = SwitchAgentModeAPI.as_view()


class SaveCobrowsingChatAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            sender = strip_html_tags(data["sender"])
            sender = remo_html_from_string(sender)
            message = strip_html_tags(data["message"])
            message = remo_html_from_string(message)
            message = remo_special_html_from_string(message)
            attachment = strip_html_tags(data["attachment"])
            attachment = remo_html_from_string(attachment)
            chat_type = strip_html_tags(data["chat_type"])
            chat_type = remo_html_from_string(chat_type)
            attachment_file_name = strip_html_tags(
                data["attachment_file_name"])
            attachment_file_name = remo_html_from_string(attachment_file_name)
            test_file_attached_name = attachment_file_name[:attachment_file_name.find(
                '.')]
            reg_file = r'^[a-zA-Z0-9_ -]+$'

            if not re.fullmatch(reg_file, test_file_attached_name):
                response["status"] = 301
                response[
                    "message"] = "Please do not use special characters other than space( ), hiphen(-) and (_) underscore in file name"
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            agent_profile_pic_source = ""

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            if cobrowse_io.is_archived == False:
                if sender != "client":
                    data["agent_profile_pic_source"] = strip_html_tags(
                        data["agent_profile_pic_source"].strip())
                    data["agent_profile_pic_source"] = remo_special_html_from_string(
                        data["agent_profile_pic_source"])
                    agent_profile_pic_source = data["agent_profile_pic_source"]

                attachment = remo_special_html_from_string(attachment)

                if len(attachment) == 0:
                    response["status"] = 300
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

                user_obj = User.objects.get(username=request.user.username)
                cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)

                if sender == "client":
                    cobrowse_agent = None
                if attachment == "None":
                    attachment = None

                if attachment_file_name == "None":
                    attachment_file_name = None

                CobrowseChatHistory.objects.create(cobrowse_io=cobrowse_io,
                                                   sender=cobrowse_agent,
                                                   message=message,
                                                   attachment=attachment,
                                                   attachment_file_name=attachment_file_name,
                                                   chat_type=chat_type,
                                                   agent_profile_pic_source=agent_profile_pic_source,)

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowsingChatAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowsingChat = SaveCobrowsingChatAPI.as_view()


class GetCobrowsingChatHistoryAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            cobrowsing_chat_history_objs = cobrowse_io.get_cobrowsing_chat_history()

            user = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(user=user)
            agent_name = cobrowse_agent.user.first_name
            if agent_name is None or agent_name.strip() == "":
                agent_name = cobrowse_agent.user.username

            client_name = cobrowse_io.full_name

            if cobrowse_io.access_token.enable_agent_connect_message:
                agent_connect_message = cobrowse_io.access_token.agent_connect_message.replace(
                    'agent_name', agent_name)
            else:
                agent_connect_message = ""

            chat_history = []
            display_agent_profile = cobrowse_io.access_token.display_agent_profile
            for cobrowsing_chat_history_obj in cobrowsing_chat_history_objs:

                est = pytz.timezone(settings.TIME_ZONE)
                datetime = cobrowsing_chat_history_obj.datetime.astimezone(
                    est).strftime("%d %b %Y %I:%M %p")

                sender = "client"
                sender_name = "client"
                agent_profile_pic_source = ""
                is_invited_agent = False
                if cobrowsing_chat_history_obj.sender != None:
                    sender = cobrowsing_chat_history_obj.sender.name()
                    sender_name = cobrowsing_chat_history_obj.sender.agent_name()
                    agent_profile_pic_source = cobrowsing_chat_history_obj.agent_profile_pic_source
                    if cobrowsing_chat_history_obj.sender == cobrowse_io.agent:
                        is_invited_agent = False
                    else:
                        is_invited_agent = True

                chat_history.append({
                    "sender": sender,
                    "message": get_masked_data_if_hashed(cobrowsing_chat_history_obj.message),
                    "attachment": cobrowsing_chat_history_obj.attachment,
                    "attachment_file_name": cobrowsing_chat_history_obj.attachment_file_name,
                    "datetime": datetime,
                    "is_invited_agent": is_invited_agent,
                    "chat_type": cobrowsing_chat_history_obj.chat_type,
                    "sender_name": sender_name,
                    "display_agent_profile": display_agent_profile,
                    "agent_profile_pic_source": agent_profile_pic_source,
                })

            response["status"] = 200
            response["message"] = "success"
            response["chat_history"] = chat_history
            response["agent_connect_message"] = agent_connect_message
            response["agent_name"] = agent_name
            response["client_name"] = client_name
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCobrowsingChatHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCobrowsingChatHistory = GetCobrowsingChatHistoryAPI.as_view()


class SaveDocumentAPI(APIView):

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
            session_id = remo_html_from_string(
                strip_html_tags(data["session_id"]))
            cobrowse_io_obj = CobrowseIO.objects.filter(
                session_id=session_id).first()

            if cobrowse_io_obj:
                access_token_obj = cobrowse_io_obj.agent.get_access_token_obj()
            else:
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            check_file_ext = filename.split(".")
            if len(check_file_ext) != 2:
                response["status"] = 301
            else:
                file_extention = filename.replace(" ", "").split(".")[-1]
                file_extention = file_extention.lower()

                if file_extention not in ["png", "jpg", "jpeg", "jpe", "pdf", "doc", "docx"]:
                    response["status"] = 302
                else:
                    base64_data = strip_html_tags(data["base64_file"])

                    is_public = False
                    if "is_public" in data and data["is_public"]:
                        is_public = True

                    original_file_name = filename
                    filename = generate_random_key(10) + "_" + filename

                    if is_public == False:
                        if not os.path.exists('secured_files/EasyAssistApp/attachments'):
                            os.makedirs(
                                'secured_files/EasyAssistApp/attachments')

                        file_path = "secured_files/EasyAssistApp/attachments/" + filename
                    else:
                        if not os.path.exists('files/attachments'):
                            os.makedirs('files/attachments')

                        file_path = "files/attachments/" + filename

                    fh = open(file_path, "wb")
                    fh.write(base64.b64decode(base64_data))
                    fh.close()
                    if get_save_in_s3_bucket_status():
                        key = s3_bucket_upload_file_by_file_path(
                            file_path, filename)
                        s3_file_path = s3_bucket_download_file(
                            key, 'EasyAssistApp/attachments/', file_extention)
                        file_path = s3_file_path.split("EasyChat/", 1)[1]
                    file_path = "/" + file_path

                    file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                        file_path=file_path, is_public=is_public, original_file_name=original_file_name, access_token=access_token_obj)

                    response["status"] = 200
                    response["message"] = "success"

                    if is_public:
                        response["file_path"] = file_path
                    else:
                        response["file_path"] = "/easy-assist/download-file/" + \
                            str(file_access_management_obj.key) + "/"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveDocumentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveDocument = SaveDocumentAPI.as_view()


class SaveMultipleDocumentAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = sanitize_input_string(data["session_id"])
            cobrowse_io_obj = CobrowseIO.objects.get(session_id=session_id)
            access_token_obj = cobrowse_io_obj.agent.get_access_token_obj()

            file_upload_success = []
            file_upload_fail = []

            for file_data_obj in data["files"]:
                try:
                    filename = "null"
                    filename = remove_special_chars_from_filename(
                        file_data_obj["filename"])
                    filename = strip_html_tags(filename)
                    filename = remo_html_from_string(filename)
                    check_file_ext = filename.split(".")
                    if len(check_file_ext) != 2:
                        file_upload_fail.append(filename)
                    else:
                        base64_data = strip_html_tags(
                            file_data_obj["base64_file"])

                        file_extention = filename.replace(
                            " ", "").split(".")[-1]
                        file_extention = file_extention.lower()

                        allowed_files_list = [
                            "png", "jpg", "jpeg", "jpe", "pdf", "doc", "docx"]
                        if check_malicious_file_from_filename(filename, allowed_files_list) or check_malicious_file_from_content(base64_data, allowed_files_list):
                            file_upload_fail.append(filename)
                        else:
                            is_public = False
                            if "is_public" in file_data_obj and file_data_obj["is_public"]:
                                is_public = True

                            original_file_name = filename
                            filename = generate_random_key(10) + "_" + filename

                            if is_public == False:
                                if not os.path.exists('secured_files/EasyAssistApp/attachments'):
                                    os.makedirs(
                                        'secured_files/EasyAssistApp/attachments')

                                file_path = "secured_files/EasyAssistApp/attachments/" + filename
                            else:
                                if not os.path.exists('files/attachments'):
                                    os.makedirs('files/attachments')

                                file_path = "files/attachments/" + filename

                            fh = open(file_path, "wb")
                            fh.write(base64.b64decode(base64_data))
                            fh.close()

                            if get_save_in_s3_bucket_status():
                                key = s3_bucket_upload_file_by_file_path(
                                    file_path, filename)
                                s3_file_path = s3_bucket_download_file(
                                    key, 'EasyAssistApp/attachments/', file_extention)
                                file_path = s3_file_path.split(
                                    "EasyChat/", 1)[1]
                            file_path = "/" + file_path

                            # Removing the Exif if it is image file
                            if not check_malicious_file_from_filename(filename, ["png", "jpg", "jpeg", "jpe"]):
                                original_file = Image.open(
                                    settings.BASE_DIR + file_path)
                                original_file.save(
                                    settings.BASE_DIR + file_path)

                            file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                                file_path=file_path, is_public=is_public, original_file_name=original_file_name, access_token=access_token_obj)

                            if is_public:
                                file_upload_success.append({
                                    "file_name": original_file_name,
                                    "file_path": file_path,
                                    "file_id": file_data_obj["file_id"],
                                })
                            else:
                                file_upload_success.append({
                                    "file_name": original_file_name,
                                    "file_path": "/easy-assist/download-file/" + str(file_access_management_obj.key) + "/",
                                    "file_id": file_data_obj["file_id"],
                                })
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error SaveMultipleDocumentAPI %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

            response["uploaded_files"] = file_upload_success
            response["file_upload_fail"] = file_upload_fail
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveMultipleDocumentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveMultipleDocument = SaveMultipleDocumentAPI.as_view()


def FileAccess(request, file_key):
    try:
        if request.user.is_authenticated:
            if check_access_token(request, file_key, CobrowseAgent, CobrowsingFileAccessManagement):
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
                        session_id=request.GET["vctoken"])
                    if not cobrowse_io_obj.is_archived:
                        return file_download(file_key, CobrowsingFileAccessManagement, SupportDocument)
                else:
                    status = check_cogno_meet_status(vc_session_obj)
                    vc_session_obj = CobrowseVideoConferencing.objects.get(
                        meeting_id=request.GET["vctoken"])
                    logger.info("VC : %s : %s", status, vc_session_obj.is_expired, extra={
                                'AppName': 'EasyAssist'})

                    if not vc_session_obj.is_expired:
                        return file_download(file_key, CobrowsingFileAccessManagement, SupportDocument)

            file_access_management_obj = CobrowsingFileAccessManagement.objects.filter(
                key=file_key, is_public=True).first()
            if file_access_management_obj and file_access_management_obj.is_obj_time_limit_exceeded() == False:
                return file_download(file_key, CobrowsingFileAccessManagement, SupportDocument)

            return HttpResponse(status=404)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error FileAccess %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
    return HttpResponse(status=404)


def ViewFile(request, file_key):
    try:
        if request.user.is_authenticated:
            if check_access_token(request, file_key, CobrowseAgent, CobrowsingFileAccessManagement):
                return file_download(file_key, CobrowsingFileAccessManagement, SupportDocument, is_download_required=False)
        else:
            if "session_id" in request.GET:
                session_id = request.GET["session_id"]
                cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
                if cobrowse_io.is_archived == True:
                    return HttpResponse(status=404)
                else:
                    return file_download(file_key, CobrowsingFileAccessManagement, SupportDocument, is_download_required=False)

            elif "vctoken" in request.GET:

                vc_session_obj = CobrowseVideoConferencing.objects.get(
                    meeting_id=request.GET["vctoken"])

                if vc_session_obj.is_cobrowsing_meeting:
                    cobrowse_io_obj = CobrowseIO.objects.get(
                        session_id=request.GET["vctoken"])
                    if not cobrowse_io_obj.is_archived:
                        return file_download(file_key, CobrowsingFileAccessManagement, SupportDocument, is_download_required=False)
                else:
                    status = check_cogno_meet_status(vc_session_obj)
                    vc_session_obj = CobrowseVideoConferencing.objects.get(
                        meeting_id=request.GET["vctoken"])
                    logger.info("VC : %s : %s", status, vc_session_obj.is_expired, extra={
                                'AppName': 'EasyAssist'})

                    if not vc_session_obj.is_expired:
                        return file_download(file_key, CobrowsingFileAccessManagement, SupportDocument, is_download_required=False)

            return HttpResponse(status=404)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ViewFile %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
    return HttpResponse(status=404)


def CustomerSupportDocuments(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)

        if cobrowse_agent.role not in ["admin", "supervisor"]:
            return HttpResponse(status=401)

        access_token_obj = cobrowse_agent.get_access_token_obj()
        agent_list = [cobrowse_agent]
        if cobrowse_agent.role == "admin":
            agent_list += get_supervisors_list_under_admin(cobrowse_agent)
        elif cobrowse_agent.role == "supervisor":
            agent_list += [access_token_obj.agent]
        support_document_objs = SupportDocument.objects.filter(
            agent__in=agent_list, is_deleted=False).order_by("-added_on")

        return render(request, "EasyAssistApp/customer_support_documents.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "support_document_objs": support_document_objs
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CustomerSupportDocuments %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def CobrowseForms(request):

    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)

        if cobrowse_agent.role not in ["admin", "supervisor"]:
            return HttpResponse(status=401)

        access_token_obj = cobrowse_agent.get_access_token_obj()

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

        product_categories = cobrowse_agent.product_category.filter(
            is_deleted=False).order_by('index')

        return render(request, "EasyAssistApp/cobrowse_forms.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "cogno_vid_forms": cogno_vid_forms,
            "agent_objs": agent_objs,
            "product_categories": product_categories
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowseForms %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def CreateCobrowseForms(request):

    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)

        agent_objs = get_list_agents_under_admin(
            cobrowse_agent, is_active=None)
        product_categories = cobrowse_agent.product_category.filter(
            is_deleted=False).order_by('index')

        return render(request, "EasyAssistApp/create_cobrowse_form.html", {
            "cobrowse_agent": cobrowse_agent,
            "agent_objs": agent_objs,
            "product_categories": product_categories,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CreateCobrowseForms %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


class AddNewCobrowseFormAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(
                user=user, is_account_active=True)

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
                cobrowse_form_obj.agents.set(agents)
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
                                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error Form Category cannot be created %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

            response['status'] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddNewCobrowseFormAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddNewCobrowseForm = AddNewCobrowseFormAPI.as_view()


def EditCobrowseForms(request, form_id):

    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)

        try:
            product_categories = cobrowse_agent.product_category.filter(
                is_deleted=False).order_by('index')

            cobrowse_form_obj = CobrowseVideoConferencingForm.objects.get(
                pk=form_id, is_deleted=False)

            cobrowse_form_category_objs = CobrowseVideoconferencingFormCategory.objects.filter(
                form=cobrowse_form_obj, is_deleted=False).order_by('pk')

            cobrowse_form_elements = CobrowseVideoConferencingFormElement.objects.filter(
                form_category__in=cobrowse_form_category_objs, is_deleted=False).order_by('pk')

            return render(request, "EasyAssistApp/edit_cobrowse_form.html", {
                "cobrowse_agent": cobrowse_agent,
                "cobrowse_form_obj": cobrowse_form_obj,
                'cobrowse_form_categories': cobrowse_form_category_objs,
                "cobrowse_form_elements": cobrowse_form_elements,
                "product_categories": product_categories,
            })

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EditCobrowseForms %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

            return HttpResponse("Form does not exist")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error EditCobrowseForms %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


class SaveCobrowseFormAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

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
                                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Error Form Category cannot be created %s at %s",
                                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
                response['status'] = 200

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error SaveCobrowseFormAPI, Form does not exist %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                response["status"] = 300

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowseFormAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowseForm = SaveCobrowseFormAPI.as_view()


class DeleteVideoConferencingFormAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
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
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
                response['status'] = 300

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteVideoConferencingFormAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteVideoConferencingForm = DeleteVideoConferencingFormAPI.as_view()


class DeleteCobrowseFormCategoryAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
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
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
                response['status'] = 300

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteCobrowseFormCategory %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteCobrowseFormCategory = DeleteCobrowseFormCategoryAPI.as_view()


class DeleteCobrowseFormCategoryQuestionAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
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
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
                response['status'] = 300

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteCobrowseFormCategoryQuestionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteCobrowseFormCategoryQuestion = DeleteCobrowseFormCategoryQuestionAPI.as_view()


class ChangeCobrowseFormAgentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            form_id = remo_html_from_string(data['form_id'])
            selected_agents = data["selected_agents"]

            user = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(
                user=user, is_account_active=True)

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
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
                response['status'] = 300

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ChangeCobrowseFormAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ChangeCobrowseFormAgent = ChangeCobrowseFormAgentAPI.as_view()


class UploadCustomerSupportDocumentsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(
                user=user, is_account_active=True)
            access_token_obj = cobrowse_agent.get_access_token_obj()

            file_upload_success = []
            file_upload_fail = []
            for file_data_obj in data:
                try:
                    filename = "null"
                    filename = strip_html_tags(file_data_obj["filename"])
                    filename = remo_html_from_string(filename)
                    filename = remo_special_html_from_string(filename)
                    check_file_ext = filename.split(".")
                    if len(check_file_ext) != 2:
                        response["status"] = 302
                        break
                    elif not len(check_file_ext[0]):
                        response["status"] = 302
                        break
                    else:
                        base64_data = strip_html_tags(
                            file_data_obj["base64_file"])
                        original_file_name = filename

                        file_already_exist = False
                        support_doc_obj = SupportDocument.objects.filter(
                            file_name=original_file_name, is_deleted=False).first()
                        if support_doc_obj:
                            file_already_exist = True

                        filename = generate_random_key(
                            10) + "_" + filename.replace(" ", "")

                        if not os.path.exists('secured_files/EasyAssistApp/customer-support'):
                            os.makedirs(
                                'secured_files/EasyAssistApp/customer-support')

                        file_path = "secured_files/EasyAssistApp/customer-support/" + filename

                        file_extention = file_path.split(".")[-1]
                        file_extention = file_extention.lower()

                        allowed_files_list = []
                        if file_extention in ["png", "jpg", "jpeg", "jpe", "bmp", "gif", "tiff", "exif", "jfif"]:
                            media_type = "image"
                            allowed_files_list += ["png", "jpg", "jpeg", "jpe",
                                                   "bmp", "gif", "tiff", "exif", "jfif"]
                        elif file_extention in ["ppt", "pptx", "pptm"]:
                            media_type = "ppt"
                            allowed_files_list += ["ppt", "pptx", "pptm"]
                        elif file_extention in ["doc", "docx", "odt", "rtf", "txt"]:
                            media_type = "docs"
                            allowed_files_list += ["doc",
                                                   "docx", "odt", "rtf", "txt"]
                        elif file_extention in ["pdf"]:
                            media_type = "pdf"
                            allowed_files_list += ["pdf"]
                        elif file_extention in ["xls", "xlsx", "xlsm", "xlt", "xltm", "xlb"]:
                            media_type = "excel"
                            allowed_files_list += ["xls",
                                                   "xlsx", "xlsm", "xlt", "xltm"]
                        elif file_extention in ["avi", "flv", "wmv", "mov", "mp4"]:
                            media_type = "video"
                            allowed_files_list += ["avi",
                                                   "flv", "wmv", "mov", "mp4"]
                        else:
                            media_type = None

                        if media_type == None or check_malicious_file_from_filename(filename, allowed_files_list) or check_malicious_file_from_content(base64_data, allowed_files_list):
                            file_upload_fail.append({
                                'file_name': original_file_name,
                                'error': 'unsupported_file_format',
                            })
                        elif file_already_exist:
                            file_upload_fail.append({
                                'file_name': original_file_name,
                                'error': 'file_already_exist',
                            })
                        else:
                            fh = open(file_path, "wb")
                            fh.write(base64.b64decode(base64_data))
                            fh.close()

                            if get_save_in_s3_bucket_status():
                                s3_bucket_upload_file_by_file_path(
                                    file_path, filename)

                            file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                                file_path="/" + file_path, is_public=False, access_token=access_token_obj)
                            file_access_management_key = file_access_management_obj.key
                            SupportDocument.objects.create(
                                file_path="/" + file_path, file_name=original_file_name, file_type=media_type, agent=cobrowse_agent, file_access_management_key=file_access_management_key)
                            file_upload_success.append(original_file_name)

                            description = "Support document (" + \
                                original_file_name + ") was uploaded"
                            save_audit_trail(cobrowse_agent, COBROWSING_DOCUMENTUPLOAD_ACTION,
                                             description, CobrowsingAuditTrail)

                            add_audit_trail(
                                "EASYASSISTAPP",
                                cobrowse_agent.user,
                                "Upload-Document",
                                description,
                                json.dumps(data),
                                request.META.get("PATH_INFO"),
                                request.META.get('HTTP_X_FORWARDED_FOR')
                            )

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error Fileupload_customer_support_loop %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
                    file_upload_fail.append({
                        'file_name': original_file_name,
                        'error': 'server_error',
                    })

                response["status"] = 200
                response["message"] = "success"
                response["file_upload_fail"] = file_upload_fail
                response["file_upload_success"] = file_upload_success
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadCustomerSupportDocumentsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadCustomerSupportDocuments = UploadCustomerSupportDocumentsAPI.as_view()


class UpdateSupportDocumentDetailAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            customer_support_document_update_dict = json.loads(data)
            is_file_data_changed_successfully = True
            is_valid_user = True
            active_agent = get_active_agent_obj(request, CobrowseAgent)
            for support_document_key in customer_support_document_update_dict.keys():
                user_input_obj = customer_support_document_update_dict[
                    support_document_key]
                support_document_obj = SupportDocument.objects.filter(
                    pk=support_document_key).first()
                if active_agent.role == "admin" or active_agent.role == support_document_obj.agent.role:
                    if "is_usable" in user_input_obj:
                        support_document_obj.is_usable = user_input_obj[
                            "is_usable"]
                    if "file_name" in user_input_obj:
                        raw_split_filename = user_input_obj["file_name"].split('.')[
                            0]
                        if not user_input_obj["file_name"].count("."):
                            response["status"] = 302
                            response["message"] = "File extension is missing in " + raw_split_filename
                            return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                        if not len(raw_split_filename.strip()):
                            response["status"] = 302
                            response["message"] = "Please enter file name to continue"
                            return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                        if user_input_obj["file_name"].count(".") > 1:
                            response["status"] = 302
                            response["message"] = "Please do not use dot(.) in file name"
                            return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                        if not is_valid_filename(raw_split_filename):
                            response["status"] = 302
                            response["message"] = raw_split_filename + " is invalid file name. Only A-Z, a-z, 0-9, - and _ are allowed"
                            return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                        
                        filename = strip_html_tags(user_input_obj["file_name"])
                        filename = remo_html_from_string(filename)
                        filename = remo_special_html_from_string(filename)
                        split_filename = filename.split(".")
                        if not len(split_filename[0]):
                            is_file_data_changed_successfully = False
                            break
                        support_document_obj.file_name = filename
                    support_document_obj.save()
                else:
                    is_valid_user = False
                    
            if not is_valid_user:
                response["status"] = 302
                response["message"] = "You don't have permission to perform this operation as this document has been uploaded by the admin"

            if is_file_data_changed_successfully:
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateSupportDocumentDetailAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateSupportDocumentDetail = UpdateSupportDocumentDetailAPI.as_view()


class DeleteSupportDocumentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            support_document_id = data["support_document_id"]

            support_document_obj = SupportDocument.objects.get(
                pk=support_document_id)

            support_document_name = support_document_obj.file_name

            support_document_obj.is_deleted = True
            support_document_obj.save()

            description = "Support document (" + \
                support_document_name + ") was deleted"

            save_audit_trail(active_agent, COBROWSING_DOCUMENTDELETE_ACTION,
                             description, CobrowsingAuditTrail)

            add_audit_trail(
                "EASYASSISTAPP",
                active_agent.user,
                "Delete-Document",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteSupportDocumentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteSupportDocument = DeleteSupportDocumentAPI.as_view()


class SetNotificationForAgentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            product_name = "Cogno Cobrowse"
            cobrowse_config_obj = get_developer_console_cobrowsing_settings()
            if cobrowse_config_obj:
                product_name = cobrowse_config_obj.cobrowsing_title_text

            if "agent_id_list" in data:
                agent_id_list = data["agent_id_list"]
                for agent_id in agent_id_list:
                    cobrowse_agent = CobrowseAgent.objects.get(
                        pk=int(agent_id))

                    notification_message = "Hi, " + cobrowse_agent.user.username + \
                        "! A customer is waiting for you to connect on " + product_name + "."
                    NotificationManagement.objects.create(show_notification=True,
                                                          agent=cobrowse_agent,
                                                          notification_message=notification_message,
                                                          cobrowse_io=cobrowse_io,
                                                          product_name=product_name)

                    if "support_request_notify" not in data:
                        cobrowse_io.agent_notified_count += 1
                        cobrowse_io.save()
                    else:
                        if data["support_request_notify"] == True:
                            send_notification_to_agent(
                                cobrowse_agent, NotificationManagement)
            else:
                agent = cobrowse_io.agent

                notification_message = "Hi, " + agent.user.username + \
                    "! A customer is waiting for you to connect on " + product_name + "."
                NotificationManagement.objects.create(show_notification=True,
                                                      agent=agent,
                                                      notification_message=notification_message,
                                                      cobrowse_io=cobrowse_io,
                                                      product_name=product_name)
                cobrowse_io.agent_notified_count += 1
                cobrowse_io.save()

                send_notification_to_agent(agent, NotificationManagement)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SetNotificationForAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SetNotificationForAgent = SetNotificationForAgentAPI.as_view()


class AddNewObfuscatedFieldAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)
            cobrowse_access_token = active_agent.get_access_token_obj()

            if active_agent.role == "admin":
                key = strip_html_tags(data["field_key"])
                key = remo_html_from_string(key)

                value = data["field_value"].strip()
                if not value:
                    response["status"] = 302
                    response["message"] = "Masking field value cannot be empty"
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                value = remo_html_from_string(value)
                masking_type = strip_html_tags(data["masking_type"])

                if cobrowse_access_token.obfuscated_fields.filter(key=key, value=value).count() > 0:
                    response["status"] = 301
                    response["message"] = "Matching cobrowse obfuscated field already exists"

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

                    add_audit_trail(
                        "EASYASSISTAPP",
                        active_agent.user,
                        "Change-App-Config",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddNewObfuscatedFieldAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddNewObfuscatedField = AddNewObfuscatedFieldAPI.as_view()


class EditObfuscatedFieldAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":
                key = strip_html_tags(data["field_key"])
                key = remo_html_from_string(key)
                value = strip_html_tags(data["field_value"])
                value = remo_html_from_string(value)
                masking_type = strip_html_tags(data["masking_type"])
                field_id = strip_html_tags(data["field_id"])
                field_id = remo_html_from_string(data["field_id"])

                cobrowse_obfuscated_field = CobrowseObfuscatedField.objects.filter(
                    pk=field_id).first()

                if cobrowse_obfuscated_field:
                    cobrowse_obfuscated_field.key = key
                    cobrowse_obfuscated_field.value = value
                    cobrowse_obfuscated_field.masking_type = masking_type

                    cobrowse_obfuscated_field.save()

                    description = key + "=" + value + " masking field updated."
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)

                    add_audit_trail(
                        "EASYASSISTAPP",
                        active_agent.user,
                        "Change-App-Config",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

                    response["status"] = 200
                    response["message"] = "success"
                else:
                    response["status"] = 301
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EditObfuscatedFieldAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


EditObfuscatedField = EditObfuscatedFieldAPI.as_view()


class DeleteObfuscatedFieldsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            obfuscated_field_id_list = data["obfuscated_field_id_list"]

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            if active_agent.role == "admin":

                for obfuscated_field_id in obfuscated_field_id_list:
                    field = CobrowseObfuscatedField.objects.get(
                        pk=int(obfuscated_field_id))
                    field.delete()

                    description = field.key + "=" + field.value + " masking field deleted."
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)

                    add_audit_trail(
                        "EASYASSISTAPP",
                        active_agent.user,
                        "Change-App-Config",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteObfuscatedFieldsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteObfuscatedFields = DeleteObfuscatedFieldsAPI.as_view()


class AddNewLeadHTMLFieldAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)
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
                unique_identifier = data["unique_identifier"]

                cobrowse_lead_html_field = cobrowse_access_token.search_fields.filter(
                    tag_key=tag_key, tag_value=tag_value).first()

                if cobrowse_lead_html_field:

                    if cobrowse_lead_html_field.is_deleted == False:
                        response["status"] = 301
                        response[
                            "message"] = "Matching cobrowse lead html field already exists"
                    else:
                        cobrowse_lead_html_field.tag = tag
                        cobrowse_lead_html_field.tag_label = tag_label
                        cobrowse_lead_html_field.tag_type = tag_type
                        cobrowse_lead_html_field.is_deleted = False
                        cobrowse_lead_html_field.unique_identifier = unique_identifier

                        cobrowse_lead_html_field.save()

                        response["status"] = 200
                        response["message"] = "success"

                        description = tag_key + "=" + tag_value + " search tag field added."
                        save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                         description, CobrowsingAuditTrail)

                        add_audit_trail(
                            "EASYASSISTAPP",
                            active_agent.user,
                            "Change-App-Config",
                            description,
                            json.dumps(data),
                            request.META.get("PATH_INFO"),
                            request.META.get('HTTP_X_FORWARDED_FOR')
                        )

                        response["status"] = 200
                        response[
                            "message"] = "success"
                else:
                    cobrowse_lead_html_field = CobrowseLeadHTMLField.objects.create(tag=tag,
                                                                                    tag_label=tag_label,
                                                                                    tag_key=tag_key,
                                                                                    tag_value=tag_value,
                                                                                    tag_type=tag_type,
                                                                                    unique_identifier=unique_identifier,)

                    cobrowse_access_token.search_fields.add(
                        cobrowse_lead_html_field)
                    cobrowse_access_token.save()

                    description = tag_key + "=" + tag_value + " search tag field added."
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)

                    add_audit_trail(
                        "EASYASSISTAPP",
                        active_agent.user,
                        "Change-App-Config",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddNewLeadHTMLFieldAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddNewLeadHTMLField = AddNewLeadHTMLFieldAPI.as_view()


class EditLeadHTMLFieldAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":
                tag = strip_html_tags(data["tag"])
                tag_label = strip_html_tags(data["tag_label"])
                tag_label = remo_html_from_string(tag_label)
                tag_key = strip_html_tags(data["tag_key"])
                tag_key = remo_html_from_string(tag_key)
                tag_value = strip_html_tags(data["tag_value"])
                tag_value = remo_html_from_string(tag_value)
                tag_type = strip_html_tags(data["tag_type"])
                field_id = remo_html_from_string(data["field_id"])
                field_id = strip_html_tags(field_id)
                unique_identifier = data["unique_identifier"]

                cobrowse_lead_html_field = CobrowseLeadHTMLField.objects.filter(
                    pk=field_id).first()
                if cobrowse_lead_html_field:
                    cobrowse_lead_html_field.tag = tag
                    cobrowse_lead_html_field.tag_label = tag_label
                    cobrowse_lead_html_field.tag_key = tag_key
                    cobrowse_lead_html_field.tag_value = tag_value
                    cobrowse_lead_html_field.tag_type = tag_type
                    cobrowse_lead_html_field.unique_identifier = unique_identifier
                    cobrowse_lead_html_field.save()
                    description = tag_key + "=" + tag_value + " search tag field updated."
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)

                    add_audit_trail(
                        "EASYASSISTAPP",
                        active_agent.user,
                        "Change-App-Config",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

                    response["status"] = 200
                    response["message"] = "success"
                else:
                    response["status"] = 301
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EditLeadHTMLFieldAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


EditLeadHTMLField = EditLeadHTMLFieldAPI.as_view()


class DeleteLeadHTMLFieldsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            search_tag_field_id_list = data["search_tag_field_id_list"]

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            if active_agent.role == "admin":
                for search_tag_field_id in search_tag_field_id_list:
                    field = CobrowseLeadHTMLField.objects.get(
                        pk=int(search_tag_field_id))
                    field.is_deleted = True
                    field.save()

                    description = field.tag_key + "=" + field.tag_value + " search tag field deleted."
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)

                    add_audit_trail(
                        "EASYASSISTAPP",
                        active_agent.user,
                        "Change-App-Config",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteLeadHTMLFieldsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteLeadHTMLFields = DeleteLeadHTMLFieldsAPI.as_view()


class AddNewAutoFetchFieldAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)
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

                    add_audit_trail(
                        "EASYASSISTAPP",
                        active_agent.user,
                        "Change-App-Config",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddNewAutoFetchFieldAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddNewAutoFetchField = AddNewAutoFetchFieldAPI.as_view()


class EditAutoFetchFieldAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":
                fetch_field_key = strip_html_tags(data["fetch_field_key"])
                fetch_field_key = remo_html_from_string(fetch_field_key)
                fetch_field_value = strip_html_tags(data["fetch_field_value"])
                fetch_field_value = remo_html_from_string(fetch_field_value)
                modal_field_key = strip_html_tags(data["modal_field_key"])
                modal_field_key = remo_html_from_string(modal_field_key)
                modal_field_value = strip_html_tags(data["modal_field_value"])
                modal_field_value = remo_html_from_string(modal_field_value)
                field_id = strip_html_tags(data["field_id"])
                field_id = remo_html_from_string(field_id)

                cobrowse_auto_fetch_field = CobrowseAutoFetchField.objects.filter(
                    pk=field_id).first()

                if cobrowse_auto_fetch_field:
                    cobrowse_auto_fetch_field.fetch_field_key = fetch_field_key
                    cobrowse_auto_fetch_field.fetch_field_value = fetch_field_value
                    cobrowse_auto_fetch_field.modal_field_key = modal_field_key
                    cobrowse_auto_fetch_field.modal_field_value = modal_field_value
                    cobrowse_auto_fetch_field.save()

                    description = fetch_field_key + "=" + \
                        fetch_field_value + " auto fetch field updated."
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)

                    add_audit_trail(
                        "EASYASSISTAPP",
                        active_agent.user,
                        "Change-App-Config",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

                    response["status"] = 200
                    response["message"] = "success"
                else:
                    response["status"] = 301
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EditAutoFetchFieldAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


EditAutoFetchField = EditAutoFetchFieldAPI.as_view()


class DeleteAutoFetchFieldsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            auto_fetch_field_id_list = data["auto_fetch_field_id_list"]

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            if active_agent.role == "admin":
                for auto_fetch_field_id in auto_fetch_field_id_list:
                    field = CobrowseAutoFetchField.objects.get(
                        pk=int(auto_fetch_field_id))
                    field.delete()

                    description = field.fetch_field_key + "=" + \
                        field.fetch_field_value + " auto fetch field deleted."
                    save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                     description, CobrowsingAuditTrail)

                    add_audit_trail(
                        "EASYASSISTAPP",
                        active_agent.user,
                        "Change-App-Config",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteAutoFetchFieldsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteAutoFetchFields = DeleteAutoFetchFieldsAPI.as_view()


class SaveCobrowseAgentAdvancedDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowseAgentAdvancedDetails = SaveCobrowseAgentAdvancedDetailsAPI.as_view()


class GetLeadStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(
                user=user, is_account_active=True)

            agents = [cobrowse_agent]

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_archived=False, agent__in=agents)
            cobrowse_io_support_objs = CobrowseIO.objects.filter(
                is_archived=False, support_agents__in=agents)
            cobrowse_io_objs = cobrowse_io_objs | cobrowse_io_support_objs

            total_active_session = 0
            inactive_session_ids = []
            for cobrowse_io_obj in cobrowse_io_objs:
                if cobrowse_io_obj.allow_agent_cobrowse == "true":
                    total_active_session += 1
                else:
                    inactive_session_ids.append(
                        str(cobrowse_io_obj.session_id))

            cobrowse_io_obj = CobrowseIO.objects.filter(
                session_id=data["session_id"]).order_by('-request_datetime')[0]

            response["cobrowsing_start_datetime"] = str(
                cobrowse_io_obj.cobrowsing_start_datetime)
            response["meeting_start_datetime"] = str(
                cobrowse_io_obj.meeting_start_datetime)
            response["is_active_timer"] = cobrowse_io_obj.is_active_timer()
            response["is_active"] = cobrowse_io_obj.is_active
            response["total_time_spent"] = cobrowse_io_obj.total_time_spent()
            response["share_client_session"] = cobrowse_io_obj.share_client_session
            response["allow_agent_cobrowse"] = cobrowse_io_obj.allow_agent_cobrowse
            response[
                "allow_video_meeting"] = cobrowse_io_obj.access_token.allow_video_meeting_only
            response["status"] = 200
            response["message"] = "success"
            response["pk"] = str(cobrowse_io_obj.pk)
            response["mobile_number"] = str(cobrowse_io_obj.mobile_number)
            response["inactive_session_ids"] = inactive_session_ids
            response["total_active_session"] = total_active_session
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetLeadStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetLeadStatus = GetLeadStatusAPI.as_view()


'''
class GetAllActiveLeadStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            user = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(
                user=user, is_account_active=True)

            access_token_obj = cobrowse_agent.get_access_token_obj()

            if cobrowse_agent.role == "admin":
                agents = get_list_agents_under_admin(cobrowse_agent)
            elif cobrowse_agent.role == "supervisor":
                agents = list(cobrowse_agent.agents.all())
            else:
                agents = [cobrowse_agent]

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_archived=False, agent__in=agents)
            cobrowse_io_support_objs = CobrowseIO.objects.filter(
                is_archived=False, support_agents__in=agents)
            cobrowse_io_objs = cobrowse_io_objs | cobrowse_io_support_objs

            cobrowse_lead_details = []
            total_active_session = 0
            inactive_session_ids = []
            for cobrowse_io_obj in cobrowse_io_objs:
                cobrowse_lead_details.append({
                    "session_id": str(cobrowse_io_obj.session_id),
                    "cobrowsing_start_datetime": str(cobrowse_io_obj.cobrowsing_start_datetime),
                    "meeting_start_datetime": str(cobrowse_io_obj.meeting_start_datetime),
                    "total_time_spent": cobrowse_io_obj.total_time_spent(),
                    "allow_agent_cobrowse": cobrowse_io_obj.allow_agent_cobrowse,
                    "allow_agent_meeting": cobrowse_io_obj.allow_agent_meeting,
                    "share_client_session": cobrowse_io_obj.share_client_session,
                    "allow_video_meeting": cobrowse_io_obj.access_token.allow_video_meeting_only,
                    "is_active_timer": cobrowse_io_obj.is_active_timer(),
                    "agent_assistant_request_status": cobrowse_io_obj.agent_assistant_request_status,
                    "is_active": cobrowse_io_obj.is_active,
                    "mobile_number": cobrowse_io_obj.mobile_number,
                    "agent_id": cobrowse_io_obj.agent.pk,
                    "agent_username": cobrowse_io_obj.agent.user.username,
                    "is_agent_request_for_cobrowsing": cobrowse_io_obj.is_agent_request_for_cobrowsing,
                    "is_droplink_lead": cobrowse_io_obj.is_droplink_lead,
                    "is_reverse_cobrowsing": cobrowse_io_obj.is_reverse_cobrowsing,
                })

                if cobrowse_io_obj.allow_agent_cobrowse == "true":
                    total_active_session += 1
                else:
                    inactive_session_ids.append(
                        str(cobrowse_io_obj.session_id))

            response["status"] = 200
            response["message"] = "success"
            response["cobrowse_lead_details"] = cobrowse_lead_details
            response["allow_agent_to_customer_cobrowsing"] = access_token_obj.allow_agent_to_customer_cobrowsing
            response["allow_screen_sharing_cobrowse"] = access_token_obj.allow_screen_sharing_cobrowse
            response["allow_cobrowsing_meeting"] = access_token_obj.allow_cobrowsing_meeting
            response["show_verification_code_modal"] = access_token_obj.show_verification_code_modal
            response["enable_verification_code_popup"] = access_token_obj.enable_verification_code_popup
            response["inactive_session_ids"] = inactive_session_ids
            response["total_active_session"] = total_active_session
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAllActiveLeadStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)
'''


class GetAllActiveLeadStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(
                user=user, is_account_active=True)
            access_token_obj = cobrowse_agent.get_access_token_obj()
            if cobrowse_agent.role in ["admin", "admin_ally"]:
                agents = get_list_agents_under_admin(cobrowse_agent, None)
            elif cobrowse_agent.role == "supervisor":
                agents = get_list_agents_under_admin(cobrowse_agent, None)
            else:
                agents = [cobrowse_agent]

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_archived=False, agent__in=agents)
            if access_token_obj.enable_invite_agent_in_cobrowsing or access_token_obj.enable_invite_agent_in_meeting:
                cobrowse_io_support_objs = CobrowseIO.objects.filter(
                    is_archived=False, support_agents__in=agents)
                cobrowse_io_objs = cobrowse_io_objs | cobrowse_io_support_objs
            if access_token_obj.enable_session_transfer_in_cobrowsing:
                transfer_io = CobrowseIOTransferredAgentsLogs.objects.filter(
                    transferred_agent__in=agents, cobrowse_request_type="transferred", transferred_status="").values_list("cobrowse_io").order_by("-log_request_datetime")
                if transfer_io:
                    cobrowse_io_transfer_objs = CobrowseIO.objects.filter(
                        is_archived=False, session_id__in=transfer_io)
                    cobrowse_io_objs = cobrowse_io_objs | cobrowse_io_transfer_objs

            cobrowse_io_objs = cobrowse_io_objs.distinct()
            cobrowse_io_objs = cobrowse_io_objs.order_by('-request_datetime')

            total_cobrowse_io_objs = cobrowse_io_objs.count()
            page_number = int(data["page_number"])
            total_cobrowse_io_objs, paginated_cobrowse_io_objs, start_point, end_point = paginate(
                cobrowse_io_objs, ACTIVE_LEADS_COUNT, page_number)

            cobrowse_lead_details = parse_cobrowse_io_data(
                paginated_cobrowse_io_objs, agents, cobrowse_agent)

            response["status"] = 200
            response["message"] = "success"
            response["cobrowse_lead_details"] = cobrowse_lead_details
            response['paginated_data'] = get_pagination_data(
                paginated_cobrowse_io_objs)
            response["total_cobrowse_io_objs"] = total_cobrowse_io_objs
            response["start"] = start_point
            response["end"] = end_point

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAllActiveLeadStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAllActiveLeadStatus = GetAllActiveLeadStatusAPI.as_view()


class SaveCobrowsingScreenRecordedDataAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}

        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)
            uploaded_file = data["uploaded_data"]
            session_id = data["session_id"]
            session_id = strip_html_tags(data["session_id"])
            screen_recorder_on = data["screen_recorder_on"]
            is_first_packet = data["is_first_packet"]

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
                    key=screen_recording_obj.recorded_file, is_public=False)
                file_path = file_access_management_obj.file_path[1:]
            except Exception:
                filename = session_id + "_" + str(CobrowseScreenRecordingAuditTrail.objects.filter(
                    cobrowse_io=cobrowse_io, agent=active_agent).count()) + ".webm"
                file_path = "secured_files/EasyAssistApp/recordings/" + filename

                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path="/" + file_path, is_public=False, access_token=active_agent.get_access_token_obj())

            if is_first_packet == "false":
                media_file = open(file_path, "ab+")
                media_file.write(uploaded_file.read())
                media_file.close()

            if get_save_in_s3_bucket_status():
                s3_bucket_upload_file_by_file_path(file_path, filename)

            screen_recording_obj.recorded_file = file_access_management_obj.key
            screen_recording_obj.is_recording_ended = False if screen_recorder_on == "true" else True
            screen_recording_obj.recording_ended = datetime.datetime.now()
            screen_recording_obj.save()

            response["status"] = 200
            response["src"] = "/" + file_path
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveScreenRecordedDataAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status"] = 500
            response["src"] = "error"

        return Response(data=response)


SaveCobrowsingScreenRecordedData = SaveCobrowsingScreenRecordedDataAPI.as_view()


class SaveReverseCobrowsingScreenRecordedDataAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            uploaded_file = data["uploaded_data"]
            session_id = data["session_id"]
            session_id = strip_html_tags(data["session_id"])
            screen_recorder_on = data["screen_recorder_on"]

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            active_agent = cobrowse_io.agent

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
                    key=screen_recording_obj.recorded_file, is_public=False)
                file_path = file_access_management_obj.file_path[1:]
            except Exception:
                filename = session_id + "_" + str(CobrowseScreenRecordingAuditTrail.objects.filter(
                    cobrowse_io=cobrowse_io, agent=active_agent).count()) + ".webm"
                file_path = "secured_files/EasyAssistApp/recordings/" + filename

                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path="/" + file_path, is_public=False, access_token=active_agent.get_access_token_obj())

            media_file = open(file_path, "ab+")
            media_file.write(uploaded_file.read())
            media_file.close()

            if get_save_in_s3_bucket_status():
                s3_bucket_upload_file_by_file_path(file_path, filename)

            screen_recording_obj.recorded_file = file_access_management_obj.key
            screen_recording_obj.is_recording_ended = False if screen_recorder_on == "true" else True
            screen_recording_obj.recording_ended = datetime.datetime.now()
            screen_recording_obj.save()

            response["status"] = 200
            response["src"] = "/" + file_path
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveReverseCobrowsingScreenRecordedDataAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status"] = 500
            response["src"] = "error"

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveReverseCobrowsingScreenRecordedData = SaveReverseCobrowsingScreenRecordedDataAPI.as_view()


class RequestCobrowsingMeetingAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            active_agent = get_active_agent_obj(request, CobrowseAgent)

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            cobrowse_io.agent_meeting_request_status = True
            cobrowse_io.is_agent_request_for_cobrowsing = True

            cobrowse_io.allow_agent_meeting = None
            cobrowse_io.meeting_start_datetime = None
            cobrowse_io.save()

            category = "session_details"
            description = "Request for meeting sent by " + \
                str(active_agent.user.username)
            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, active_agent)

            user_obj = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
            try:
                cobrowse_video_conf_obj = CobrowseVideoConferencing.objects.get(
                    meeting_id=session_id)
            except Exception:
                is_voip_meeting = False
                if cobrowse_agent.get_access_token_obj().enable_voip_calling == True:
                    is_voip_meeting = True
                elif cobrowse_agent.get_access_token_obj().enable_voip_with_video_calling == True:
                    is_voip_meeting = True
                else:
                    is_voip_meeting = False
                if is_voip_meeting == True:
                    cobrowse_video_conf_obj = CobrowseVideoConferencing.objects.create(
                        meeting_id=session_id,
                        agent=cobrowse_agent,
                        meeting_description="VoIP Meeting",
                        meeting_start_date=timezone.now(),
                        meeting_start_time=timezone.localtime(timezone.now()),
                        full_name=cobrowse_io.full_name,
                        mobile_number=cobrowse_io.mobile_number,
                        is_cobrowsing_meeting=True,
                        is_voip_meeting=True)
                else:
                    cobrowse_video_conf_obj = CobrowseVideoConferencing.objects.create(
                        meeting_id=session_id,
                        agent=cobrowse_agent,
                        meeting_description="Cobrowsing Meeting",
                        meeting_start_date=timezone.now(),
                        meeting_start_time=timezone.localtime(timezone.now()),
                        full_name=cobrowse_io.full_name,
                        mobile_number=cobrowse_io.mobile_number,
                        is_cobrowsing_meeting=True,
                        is_voip_meeting=False)
            # Adding all the support agents connected to the invited section of audit trail
            audit_trail_obj = CobrowseVideoAuditTrail.objects.filter(
                cobrowse_video=cobrowse_video_conf_obj)
            if audit_trail_obj:
                audit_trail_obj = audit_trail_obj.first()
            else:
                audit_trail_obj = CobrowseVideoAuditTrail.objects.create(
                    cobrowse_video=cobrowse_video_conf_obj)

            if audit_trail_obj.meeting_initiated_by == None:
                audit_trail_obj.meeting_initiated_by = "agent"

            for agent in cobrowse_io.support_agents.all():
                if agent.is_cobrowsing_active:
                    audit_trail_obj.meeting_agents_invited.add(agent)
            audit_trail_obj.save()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RequestCobrowsingMeetingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


RequestCobrowsingMeeting = RequestCobrowsingMeetingAPI.as_view()


class CheckMeetingStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            active_agent = get_active_agent_obj(request, CobrowseAgent)
            is_cognomeet_active = None
            if active_agent:
                is_cognomeet_active = active_agent.is_cognomeet_active
            is_meeting_allowed = False
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            if cobrowse_io.allow_agent_meeting == 'None' or cobrowse_io.allow_agent_meeting == None:
                response["is_meeting_allowed"] = is_meeting_allowed
                response["is_client_answer"] = False
                response["is_cognomeet_active"] = is_cognomeet_active
                response["status"] = 301
                response["message"] = "success"
            elif cobrowse_io.allow_agent_meeting == 'true':
                is_meeting_allowed = True

                response["is_meeting_allowed"] = is_meeting_allowed
                response["is_client_answer"] = True
                response["is_cognomeet_active"] = is_cognomeet_active
                response["status"] = 200
                response["message"] = "success"
            else:
                is_meeting_allowed = False

                response["is_meeting_allowed"] = is_meeting_allowed
                response["is_client_answer"] = True
                response["is_cognomeet_active"] = is_cognomeet_active
                response["status"] = 200
                response["message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckMeetingStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckMeetingStatus = CheckMeetingStatusAPI.as_view()


def EasyAssistPageShot(request, pageshot_id):
    if request.user.is_authenticated:
        try:
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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
    else:
        return HttpResponse("Invalid Request")


class GenerateDropLinkAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            client_page_link = sanitize_input_string(data["client_page_link"])
            customer_name = sanitize_input_string(data["customer_name"])
            customer_mobile_number = remo_special_tag_from_string(remo_html_from_string(data["customer_mobile_number"]))
            customer_email_id = remo_html_from_string(data["customer_email_id"])
            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            if not is_url_valid(client_page_link):
                response["status"] = 301
                response["message"] = "Please enter a valid Website URL"
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

            if not check_valid_name(customer_name):
                response["status"] = 302
                response["message"] = "Please enter a valid Customer Name"
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
            
            if not is_mobile_valid(customer_mobile_number):
                response["status"] = 303
                response["message"] = "Please enter a valid 10 digit mobile number"
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
            
            if access_token_obj.is_droplink_email_mandatory and not is_email_valid(customer_email_id):
                response["status"] = 304
                response["message"] = "Please enter a valid Customer Email ID"
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))     
            elif customer_email_id and not is_email_valid(customer_email_id):
                response["status"] = 304
                response["message"] = "Please enter a valid Customer Email ID"
                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

            cobrowse_drop_link_obj = generate_drop_link_with_data(
                request, client_page_link, active_agent, customer_name, customer_email_id, customer_mobile_number, CobrowseDropLink)

            if cobrowse_drop_link_obj:
                response["status"] = 200
                response["message"] = "success"
                response["generated_link"] = cobrowse_drop_link_obj.generated_link
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GenerateDropLinkAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GenerateDropLink = GenerateDropLinkAPI.as_view()


def CognoMeetAnalyticsDashboard(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        DEFAULT_ANALYTICS_START_DATETIME = (
            datetime.datetime.today() - datetime.timedelta(7)).date()

        DEFAULT_ANALYTICS_END_DATETIME = datetime.datetime.today().date()

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)

        access_token_obj = cobrowse_agent.get_access_token_obj()

        agent_objs = []
        if cobrowse_agent.role == "agent":
            agent_objs = [cobrowse_agent]
        elif cobrowse_agent.role == "supervisor":
            agent_objs = list(cobrowse_agent.agents.all())
        else:
            agent_objs = get_list_agents_under_admin(
                cobrowse_agent, is_active=None, is_account_active=None)

        if access_token_obj.enable_cognomeet:
            
            if cobrowse_agent.role == "supervisor":
                agent_objs.append(cobrowse_agent)
            elif cobrowse_agent.role == "admin_ally":
                agent_objs += cobrowse_agent.agents.all().filter(role="supervisor")
            elif cobrowse_agent.role == "admin":
                admin_ally_objs = cobrowse_agent.agents.all().filter(role="admin_ally")
                for admin_ally_obj in admin_ally_objs:
                    agent_objs += admin_ally_obj.agents.all().filter(role="supervisor")
                agent_objs += cobrowse_agent.agents.all().filter(role="supervisor")
            
            agent_objs = list(set(agent_objs))
            agent_usernames_list = []
            for agent in agent_objs:
                agent_usernames_list.append(agent.user.username)

            return render(request, "EasyAssistApp/analytics_cognomeet_new.html", {
                "agent_objs": agent_objs,
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "agent_usernames_list": agent_usernames_list,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME,
                "agent_role": cobrowse_agent.role
            })
        else:
            if cobrowse_agent.show_static_analytics:
                return render(request, "EasyAssistApp/analytics_cogno_meet_static.html", {
                    "agent_objs": agent_objs,
                    "cobrowse_agent": cobrowse_agent,
                    "access_token_obj": access_token_obj,
                    "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                    "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
                })
            else:
                return render(request, "EasyAssistApp/analytics_cogno_meet.html", {
                    "agent_objs": agent_objs,
                    "cobrowse_agent": cobrowse_agent,
                    "access_token_obj": access_token_obj,
                    "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                    "datetime_end": DEFAULT_ANALYTICS_END_DATETIME
                })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CognoMeetAnalyticsDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


@csrf_exempt
def service_worker(request):
    try:
        filename = '/EasyAssistApp/static/EasyAssistApp/js/service-worker-cobrowse.js'
        jsfile = open(settings.BASE_DIR + filename, 'rb')
        response = HttpResponse(content=jsfile)
        response['Content-Type'] = 'text/javascript'
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error service_worker %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(status=401)


class UpdateLogFileAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            log_file = open(APP_LOG_FILENAME, 'r')
            line_count = 0
            response["code"] = ""
            temp_file_list = []

            for line in reversed(list(log_file)):
                if line.find("EasyAssist") >= 0:
                    line_count += 1
                    if line_count <= LOGTAILER_LINES:
                        temp_file_list.append(line)
                    else:
                        break

            temp_file_list = reversed(temp_file_list)
            for line in temp_file_list:
                response["code"] += line

            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateLogFileAPI %s at %s", str(e), str(
                exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateLogFile = UpdateLogFileAPI.as_view()


class DownloadEasyAssistLogFileAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            log_file = open(APP_LOG_FILENAME, 'r')

            if not os.path.exists('secured_files/EasyAssistApp/LogFile'):
                os.makedirs('secured_files/EasyAssistApp/LogFile')

            file_name = "app_" + str(uuid.uuid4().hex[:10]) + ".log"
            file_path = "secured_files/EasyAssistApp/LogFile/" + file_name
            final_log_file = open(file_path, 'w')
            final_log_file.write(log_file.read())
            final_log_file.close()

            if get_save_in_s3_bucket_status():
                s3_bucket_upload_file_by_file_path(file_path, file_name)

            file_path = "/" + file_path
            file_access_management_obj = CobrowsingFileAccessManagement.objects.filter(
                file_path=file_path, is_public=False)
            if not file_access_management_obj:
                active_agent = get_active_agent_obj(
                    request, CobrowseAgent)
                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=file_path, is_public=False, access_token=active_agent.get_access_token_obj())

            response["status"] = 200
            response["file_id"] = str(file_access_management_obj.key)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DownloadEasyAssistLogFile %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DownloadEasyAssistLogFile = DownloadEasyAssistLogFileAPI.as_view()


class SaveAssignTaskProcessorCodeAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            access_token_key = data["access_token_key"]
            assign_task_process_id = data["process_id"]
            assign_task_processor_code = data["processor_code"]

            try:
                assign_task_process = AssignTaskProcessor.objects.get(
                    pk=assign_task_process_id)
                access_token_obj = CobrowseAccessToken.objects.get(
                    key=access_token_key)

                if assign_task_process.access_token == access_token_obj:
                    assign_task_process.function = assign_task_processor_code
                    assign_task_process.save()
                    response["status"] = 200
                else:
                    response["status"] = 401
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error SaveAssignTaskProcessorCodeAPI %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
                response["status"] = 301

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveAssignTaskProcessorCodeAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveAssignTaskProcessorCode = SaveAssignTaskProcessorCodeAPI.as_view()


class SaveAgentDetailsAPIProcessorCodeAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            access_token_key = remo_html_from_string(data["access_token_key"])
            agent_details_api_process_id = remo_html_from_string(
                data["agent_details_api_process_id"])
            agent_details_api_process_id = remo_special_tag_from_string(
                agent_details_api_process_id)
            agent_details_api_processor_code = data["agent_details_api_processor_code"]

            if is_system_command_present(agent_details_api_processor_code):
                response["status"] = 400
                response["message"] = "System commands are present in the code. Please remove them and try again."
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            access_token_obj = CobrowseAccessToken.objects.filter(
                key=access_token_key).first()

            if access_token_obj:
                agent_details_api_processor_obj = access_token_obj.get_agent_details_api_processor_obj()
                agent_details_api_processor_obj.function = agent_details_api_processor_code
                agent_details_api_processor_obj.save()
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveAgentDetailsAPIProcessorCodeAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveAgentDetailsAPIProcessorCode = SaveAgentDetailsAPIProcessorCodeAPI.as_view()


class RunAgentDetailsAPIProcessorCodeAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal server error"
        response["total_execution_time"] = "0"
        api_response = None
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            agent_unique_identifier = data["agent_unique_identifier"]
            agent_details_api_processor_code = data["agent_details_api_processor_code"]

            if is_system_command_present(agent_details_api_processor_code):
                response["status"] = 400
                response["message"] = "System commands are present in the code. Please remove them and try again."
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            start_time = time.time()

            try:
                api_response = func_timeout.func_timeout(
                    EASYASSIST_MAX_API_RUNTIME_LIMIT, execute_processor_python_code, args=[agent_details_api_processor_code, agent_unique_identifier])
                response["message"] = api_response
                response["status"] = 200

            except func_timeout.FunctionTimedOut:
                logger.error("Error RunAgentDetailsAPIProcessorCodeAPI timeout in code execution ", extra={
                             'AppName': 'EasyAssist'})
                response["status"] = 301
                response["message"] = "Time limit exceeded for processor execution."

            end_time = time.time()
            total_execution_time = end_time - start_time
            response["total_execution_time"] = str(total_execution_time)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RunAgentDetailsAPIProcessorCodeAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status"] = 300
            response["message"] = str(e)

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


RunAgentDetailsAPIProcessorCode = RunAgentDetailsAPIProcessorCodeAPI.as_view()


class FetchStaticFileListAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            access_token = data["access_token"]
            cobrowse_access_token_obj = CobrowseAccessToken.objects.filter(
                key=access_token).first()

            if cobrowse_access_token_obj != None:
                file_obj_list = cobrowse_access_token_obj.get_static_file_token_wise_list()
                response["status"] = 200
                response["message"] = "success"
                response["file_obj_list"] = file_obj_list
            else:
                response["status"] = 301
                response["message"] = "Accesstoken Not Exists"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FetchStaticFileListAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


FetchStaticFileList = FetchStaticFileListAPI.as_view()


class FetchStaticFileContentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            relative_path = data["relative_path"]
            file_name = relative_path.split("/")[-1]
            file_type = file_name[file_name.rfind(".") + 1:]
            file_content = read_file_content(relative_path)

            response["status"] = 200
            response["message"] = "success"
            response["file_content"] = file_content
            response["file_name"] = file_name
            response["file_type"] = file_type
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FetchStaticFileContentAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


FetchStaticFileContent = FetchStaticFileContentAPI.as_view()


class SaveStaticFileContentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            access_token = data["access_token"]
            selected_file_relative_path = data["selected_file_relative_path"]
            selected_file_new_data = data["selected_file_new_data"]

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            cobrowse_access_token_obj = CobrowseAccessToken.objects.filter(
                key=access_token).first()

            if cobrowse_access_token_obj:

                backup_static_file(
                    selected_file_relative_path, cobrowse_access_token_obj, active_agent, StaticFileChangeLogger)

                write_file_content(
                    selected_file_relative_path, selected_file_new_data)
                write_file_content(get_similar_static_files_path(
                    selected_file_relative_path), selected_file_new_data)

                file_content = read_file_content(selected_file_relative_path)

                response["status"] = 200
                response["message"] = "success"
                response["file_content"] = file_content
            else:
                response["status"] = 301
                response["message"] = "Invalid Accesstoken"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveStaticFileContentAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveStaticFileContent = SaveStaticFileContentAPI.as_view()


class ResetStaticFileContentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            selected_file_relative_path = data["selected_file_relative_path"]
            access_token = data["access_token"]

            dst_file_path = selected_file_relative_path
            src_file_path = dst_file_path.replace(access_token + "/", "")

            file_content = read_file_content(src_file_path)
            write_file_content(dst_file_path, file_content)
            write_file_content(get_similar_static_files_path(
                dst_file_path), file_content)

            file_content = read_file_content(src_file_path)

            response["status"] = 200
            response["message"] = "success"
            response["file_content"] = file_content
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ResetStaticFileContentAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ResetStaticFileContent = ResetStaticFileContentAPI.as_view()


class GetStaticFileSaveAuditTrailAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetStaticFileSaveAuditTrailAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetStaticFileSaveAuditTrail = GetStaticFileSaveAuditTrailAPI.as_view()


def CRMCobrowsingAutoLogin(request, token):
    try:
        logger.info("token = %s ", str(token), extra={'AppName': 'EasyAssist'})
        login_token_obj = CRMCobrowseLoginToken.objects.filter(
            token=token).first()

        if login_token_obj == None:
            return HttpResponse('Login Failed')
        elif login_token_obj.is_expired == True:
            return HttpResponse('Session Expired')

        if login_token_obj.cobrowse_drop_link:
            cobrowse_io_obj = login_token_obj.cobrowse_drop_link.cobrowse_io
            if cobrowse_io_obj == None:
                return HttpResponse("Customer has not opened shared link")
        else:
            cobrowse_io_obj = login_token_obj.cobrowse_io

        user_obj = cobrowse_io_obj.agent.user
        login_token_obj.is_expired = True
        login_token_obj.save()

        if not request.user.is_authenticated:
            login(request, user_obj)

            description = "Login into System"
            save_audit_trail(
                cobrowse_io_obj.agent, COBROWSING_LOGIN_ACTION, description, CobrowsingAuditTrail)

            add_audit_trail(
                "EASYASSISTAPP",
                cobrowse_io_obj.agent.user,
                "Login",
                description,
                json.dumps({"token": token}),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

        access_token = cobrowse_io_obj.access_token
        if access_token.allow_screen_sharing_cobrowse == True:
            return redirect('/easy-assist/agent/screensharing-cobrowse/' + str(cobrowse_io_obj.session_id))
        else:
            return redirect('/easy-assist/agent/' + str(cobrowse_io_obj.session_id))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CRMCobrowsingAutoLogin %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse("Invalid token")


class CRMGenerateAuthTokenAPI(APIView):

    authentication_classes = [BasicAuthentication]

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            username = request.user.username
            cobrowse_agent = CobrowseAgent.objects.get(user__username=username)
            access_token = cobrowse_agent.get_access_token_obj()

            crm_integration_model = CRMIntegrationModel.objects.create(
                access_token=access_token)

            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
            response["Body"]['auth_token'] = str(
                crm_integration_model.auth_token)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMGenerateAuthTokenAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMGenerateAuthToken = CRMGenerateAuthTokenAPI.as_view()


class CRMInboundIntegrationAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            request_data = request.data

            is_all_data_available = True
            required_inputs = ["agent_id", "session_id"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            agent_id = request_data['agent_id']
            session_id = request_data['session_id']

            agent_obj = CobrowseAgent.objects.filter(
                user__username__iexact=agent_id, is_account_active=True).first()

            if agent_obj == None:
                agent_obj = CobrowseAgent.objects.filter(
                    virtual_agent_code__iexact=agent_id, is_account_active=True).first()

            if agent_obj == None:
                agent_obj = CobrowseAgent.objects.filter(
                    agent_code__iexact=agent_id, is_account_active=True).first()

            if agent_obj == None:
                response["Head"]['ResponseCode'] = 303
                response["Head"]['Description'] = 'Agent not exist'
                return Response(data=response)

            cobrowse_io_obj = None
            try:
                cobrowse_io_obj = CobrowseIO.objects.filter(
                    session_id=session_id, access_token=crm_integration_model.access_token).first()
            except Exception:
                cobrowse_io_obj = None

            if cobrowse_io_obj == None:
                response["Head"]['ResponseCode'] = 304
                response["Head"][
                    'Description'] = 'Requested Session does not exist'
                return Response(data=response)

            cobrowse_io_obj.agent = agent_obj
            cobrowse_io_obj.allow_agent_cobrowse = "true"
            cobrowse_io_obj.save()
            login_token_obj = CRMCobrowseLoginToken.objects.create(
                cobrowse_io=cobrowse_io_obj)
            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
            response["Body"]['cobrowsing_url'] = settings.EASYASSISTAPP_HOST + \
                "/easy-assist/crm/cobrowsing/" + str(login_token_obj.token)

            try:
                category = "CRMInboundIntegration"
                description = json.dumps(response)
                save_system_audit_trail(category, description, cobrowse_io_obj,
                                        crm_integration_model.access_token, SystemAuditTrail, agent_obj)
            except:
                pass
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMInboundIntegrationAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMInboundIntegration = CRMInboundIntegrationAPI.as_view()


class CRMCaptureLeadIntegrationAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            request_data = request.data

            if ("Name" not in request_data) or ("Number" not in request_data) or ("Email" not in request_data):
                response["Head"]["ResponseCode"] = 301
                response["Head"]['Description'] = 'No Content - Some required parameter is not passed'
                return Response(data=response)

            user_name = request_data["Name"].strip()

            user_number = request_data["Number"].strip()

            user_email = request_data["Email"].strip()

            if user_name == "" and user_number == "" and user_email == "":
                response["Head"]["ResponseCode"] = 302
                response["Head"]['Description'] = 'All required parameter cannot be empty'
                return Response(data=response)

            try:
                site_title = request_data["SiteTitle"].strip()
            except Exception:
                site_title = ""

            try:
                site_url = request_data["SiteUrl"].strip()
            except Exception:
                site_url = ""

            cobrowse_io_obj = None

            primary_value_list = []

            easyassist_sync_data = []

            cobrowse_io_obj = CobrowseIO.objects.create(
                is_lead=True,
                access_token=crm_integration_model.access_token,
                request_datetime=timezone.now(),
                is_agent_connected=False,
            )

            if user_name != "":
                cobrowse_io_obj.full_name = user_name
                captured_lead_name_obj = {
                    "value": user_name,
                    "label": "Name"
                }
                primary_value_list.append(captured_lead_name_obj)
                easyassist_sync_data.append(
                    {"sync_type": "primary", "name": "Name", "value": user_name})

            if user_number != "":
                cobrowse_io_obj.mobile_number = user_number
                captured_lead_number_obj = {
                    "value": user_number,
                    "label": "Number"
                }
                primary_value_list.append(captured_lead_number_obj)
                easyassist_sync_data.append(
                    {"sync_type": "primary", "name": "Number", "value": user_number})

            if user_email != "":
                captured_lead_email_obj = {
                    "value": user_email,
                    "label": "Email"
                }
                primary_value_list.append(captured_lead_email_obj)
                easyassist_sync_data.append(
                    {"sync_type": "primary", "name": "Email", "value": user_email})

            if site_title != "":
                cobrowse_io_obj.title = site_title

            if site_url != "":
                cobrowse_io_obj.active_url = site_url

            meta_data = {
                "product_details": {
                    "title": site_title,
                    "url": site_url,
                },
                "easyassist_sync_data": easyassist_sync_data
            }
            custom_encrypt_obj = CustomEncrypt()
            meta_data = custom_encrypt_obj.encrypt(json.dumps(meta_data))
            cobrowse_io_obj.meta_data = meta_data
            cobrowse_io_obj.save()

            check_and_update_lead(
                primary_value_list,
                meta_data,
                cobrowse_io_obj,
                CobrowseCapturedLeadData,
            )

            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
            response["Body"]['SessionId'] = str(cobrowse_io_obj.session_id)

        except Exception as e:
            logger.error(
                f'{str(e)} at {sys.exc_info()[2].tb_lineno}] in CRMCaptureLeadIntegrationAPI',
                extra={'AppName': 'EasyAssist'}
            )

        return Response(data=response)


CRMCaptureLeadIntegration = CRMCaptureLeadIntegrationAPI.as_view()


class CRMSearchLeadIntegrationAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            request_data = request.data

            is_all_data_available = True
            required_inputs = ["agent_id", "search_value"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            agent_id = request_data['agent_id']
            search_value = request_data['search_value']

            agent_obj = CobrowseAgent.objects.filter(
                user__username__iexact=agent_id, is_account_active=True).first()

            if agent_obj == None:
                agent_obj = CobrowseAgent.objects.filter(
                    virtual_agent_code__iexact=agent_id, is_account_active=True).first()

            if agent_obj == None:
                agent_obj = CobrowseAgent.objects.filter(
                    agent_code__iexact=agent_id, is_account_active=True).first()

            if agent_obj == None:
                response["Head"]['ResponseCode'] = 303
                response["Head"]['Description'] = 'Agent not exist'
                return Response(data=response)

            search_value = search_value.strip().lower()
            md5_primary_id = hashlib.md5(search_value.encode()).hexdigest()
            cobrowse_leads = CobrowseCapturedLeadData.objects.filter(
                primary_value=md5_primary_id)
            cobrowse_io_obj = CobrowseIO.objects.filter(is_lead=True,
                                                        is_archived=False,
                                                        captured_lead__in=cobrowse_leads,
                                                        access_token=crm_integration_model.access_token).order_by('-last_update_datetime').first()

            if cobrowse_io_obj == None:
                response["Head"]['ResponseCode'] = 304
                response["Head"][
                    'Description'] = 'Requested Session does not exist'
                return Response(data=response)

            cobrowse_io_obj.agent = agent_obj
            cobrowse_io_obj.allow_agent_cobrowse = "true"
            cobrowse_io_obj.save()
            login_token_obj = CRMCobrowseLoginToken.objects.create(
                cobrowse_io=cobrowse_io_obj)
            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
            response["Body"]['cobrowsing_url'] = settings.EASYASSISTAPP_HOST + \
                "/easy-assist/crm/cobrowsing/" + str(login_token_obj.token)

            try:
                category = "CRMSearchLeadIntegration"
                description = json.dumps(response)
                save_system_audit_trail(category, description, cobrowse_io_obj,
                                        crm_integration_model.access_token, SystemAuditTrail, agent_obj)
            except:
                pass
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMSearchLeadIntegrationAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMSearchLeadIntegration = CRMSearchLeadIntegrationAPI.as_view()


class CRMDropLinkIntegrationAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            request_data = request.data

            is_all_data_available = True
            required_inputs = ["agent_id",
                               "client_page_link", "customer_name"]
            required_either_of_one = [
                "customer_mobile_number", "customer_email_id"]

            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available:
                is_all_data_available = False
                for required_input in required_either_of_one:
                    if required_input in request_data:
                        is_all_data_available = True

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            agent_id = request_data['agent_id']
            client_page_link = request_data["client_page_link"]
            client_page_link = remo_html_from_string(client_page_link)
            customer_name = request_data["customer_name"]
            customer_name = remo_html_from_string(customer_name)
            customer_name = remo_special_tag_from_string(customer_name)

            customer_mobile_number = ""
            if "customer_mobile_number" in request_data:
                customer_mobile_number = request_data["customer_mobile_number"]
                customer_mobile_number = remo_html_from_string(
                    customer_mobile_number)
                customer_mobile_number = remo_special_tag_from_string(
                    customer_mobile_number)

            customer_email_id = ""
            if "customer_email_id" in request_data:
                customer_email_id = request_data["customer_email_id"]
                customer_email_id = remo_html_from_string(customer_email_id)

            agent_obj = CobrowseAgent.objects.filter(
                user__username__iexact=agent_id, is_account_active=True).first()

            if agent_obj == None:
                agent_obj = CobrowseAgent.objects.filter(
                    virtual_agent_code__iexact=agent_id, is_account_active=True).first()

            if agent_obj == None:
                agent_obj = CobrowseAgent.objects.filter(
                    agent_code__iexact=agent_id, is_account_active=True).first()

            if agent_obj == None:
                response["Head"]['ResponseCode'] = 303
                response["Head"]['Description'] = 'Agent not exist'
                return Response(data=response)

            cobrowse_drop_link_obj = generate_drop_link_with_data(
                request, client_page_link, agent_obj, customer_name, customer_email_id, customer_mobile_number, CobrowseDropLink)

            if cobrowse_drop_link_obj == None or cobrowse_drop_link_obj.generated_link == "Error":
                response["Head"]['ResponseCode'] = 305
                response["Head"]['Description'] = 'Droplink generation failed'
                return Response(data=response)

            login_token_obj = CRMCobrowseLoginToken.objects.create(
                cobrowse_drop_link=cobrowse_drop_link_obj)

            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
            response["Body"]['cobrowsing_url'] = settings.EASYASSISTAPP_HOST + \
                "/easy-assist/crm/cobrowsing/" + str(login_token_obj.token)
            response["Body"][
                'link_for_customer'] = cobrowse_drop_link_obj.generated_link

            try:
                category = "CRMDropLinkIntegration"
                description = json.dumps(response)
                save_system_audit_trail(
                    category, description, None, crm_integration_model.access_token, SystemAuditTrail, agent_obj)
            except:
                pass
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMDropLinkIntegrationAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMDropLinkIntegration = CRMDropLinkIntegrationAPI.as_view()


def DownloadCRMDocuments(request, document_type):
    try:
        if request.user.is_authenticated:

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            cobrowse_access_token = active_agent.get_access_token_obj()

            original_file_name = CRM_DOCUMENTS[document_type]["original_file_name"]
            display_file_name = CRM_DOCUMENTS[document_type]["display_file_name"]

            path_to_file = "secured_files/EasyAssistApp/crm-documents/" + \
                str(cobrowse_access_token.key) + "/" + original_file_name

            if not path.exists(path_to_file):
                generate_crm_api_document(cobrowse_access_token)

            if path.exists(path_to_file):
                with open(path_to_file, 'rb') as fh:
                    response = HttpResponse(
                        fh.read(), status=200, content_type="docs")
                    response['Content-Disposition'] = 'attachment; filename="%s"' % smart_str(
                        str(display_file_name))
                    return response
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse(status=404)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error DownloadCRMDocuments %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
    return HttpResponse(status=404)


class CRMGenerateAPIDocumentsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            client_id = data["client_id"]

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()
            CRMIntegrationModel.objects.create(
                access_token=access_token_obj, client_id=client_id)
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMGenerateAPIDocumentsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CRMGenerateAPIDocuments = CRMGenerateAPIDocumentsAPI.as_view()


class AgentOnlineAuditTrailAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            agent_username = data["agent_username"]
            date = data["date"]
            date = datetime.datetime.strptime(date, DATE_TIME_FORMAT)

            est = pytz.timezone(settings.TIME_ZONE)
            try:
                user_obj = User.objects.get(username=agent_username)
                cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)
                login_audit_trail_objs = CobrowsingAuditTrail.objects.filter(
                    agent=cobrowse_agent, datetime__date=date, action__in=[COBROWSING_LOGIN_ACTION, COBROWSING_LOGOUT_ACTION]).order_by("datetime")

                agent_audit_trail_list = []
                last_login_time = None
                for agent_login_logout_data in login_audit_trail_objs:
                    if agent_login_logout_data.action == COBROWSING_LOGIN_ACTION:
                        if last_login_time:
                            agent_audit_trail_list.append({
                                "login_time": last_login_time,
                                "logout_time": None,
                                "online_duration": 0
                            })
                        last_login_time = agent_login_logout_data.datetime
                    else:
                        if last_login_time == None:
                            agent_audit_trail_list.append({
                                "login_time": None,
                                "logout_time": agent_login_logout_data.datetime,
                                "online_duration": 0
                            })
                        else:
                            agent_audit_trail_list.append({
                                "login_time": last_login_time,
                                "logout_time": agent_login_logout_data.datetime,
                                "online_duration": 0
                            })
                        last_login_time = None

                if last_login_time:
                    agent_audit_trail_list.append({
                        "login_time": last_login_time,
                        "logout_time": None,
                        "online_duration": 0
                    })

                agent_online_audit_trail_objs = CobrowseAgentOnlineAuditTrail.objects.filter(
                    agent=cobrowse_agent, last_online_start_datetime__date=date)

                agent_work_audit_trail_objs = CobrowseAgentWorkAuditTrail.objects.filter(
                    agent=cobrowse_agent, session_start_datetime__date=date)

                for agent_online_audit_trail_obj in agent_online_audit_trail_objs:
                    for audit_trail_obj in agent_audit_trail_list:
                        if audit_trail_obj["login_time"] and audit_trail_obj["logout_time"]:
                            audit_trail_obj["online_duration"] += get_online_duration_within_agent_login_session(
                                audit_trail_obj["login_time"],
                                audit_trail_obj["logout_time"],
                                agent_online_audit_trail_obj.last_online_start_datetime,
                                agent_online_audit_trail_obj.last_online_end_datetime)

                for agent_work_audit_trail_obj in agent_work_audit_trail_objs:
                    for audit_trail_obj in agent_audit_trail_list:
                        if audit_trail_obj["login_time"] and audit_trail_obj["logout_time"]:
                            audit_trail_obj["online_duration"] += get_session_duration_within_agent_login_session(
                                audit_trail_obj["login_time"],
                                audit_trail_obj["logout_time"],
                                agent_work_audit_trail_obj.session_start_datetime,
                                agent_work_audit_trail_obj.session_end_datetime)

                for audit_trail_obj in agent_audit_trail_list:
                    common_time_list = []
                    for agent_online_audit_trail_obj in agent_online_audit_trail_objs:
                        time_duration = get_time_duration_with_login_session(
                            audit_trail_obj["login_time"],
                            audit_trail_obj["logout_time"],
                            agent_online_audit_trail_obj.last_online_start_datetime,
                            agent_online_audit_trail_obj.last_online_end_datetime)

                        if time_duration:
                            common_time_list.append(
                                [time_duration[0], time_duration[1], "online"])

                    for agent_work_audit_trail_obj in agent_work_audit_trail_objs:
                        time_duration = get_time_duration_with_login_session(
                            audit_trail_obj["login_time"],
                            audit_trail_obj["logout_time"],
                            agent_work_audit_trail_obj.session_start_datetime,
                            agent_work_audit_trail_obj.session_end_datetime)

                        if time_duration:
                            common_time_list.append(
                                [time_duration[0], time_duration[1], "work"])

                    agent_session_online_common_time = calcuate_agent_online_session_common_time(
                        common_time_list)
                    audit_trail_obj["online_duration"] -= agent_session_online_common_time

                date_format = "%B %-d, %Y %I:%M %p"
                for audit_trail_obj in agent_audit_trail_list:

                    audit_trail_obj["online_duration"] = convert_seconds_to_hours_minutes(
                        audit_trail_obj["online_duration"])

                    if audit_trail_obj["login_time"]:
                        audit_trail_obj["login_time"] = audit_trail_obj[
                            "login_time"].astimezone(est).strftime(date_format)
                    else:
                        audit_trail_obj["login_time"] = "-"

                    if audit_trail_obj["logout_time"]:
                        audit_trail_obj["logout_time"] = audit_trail_obj[
                            "logout_time"].astimezone(est).strftime(date_format)
                    else:
                        audit_trail_obj["logout_time"] = "-"

                response["status"] = 200
                response["audit_trail_list"] = agent_audit_trail_list
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error AgentOnlineAuditTrail %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
                response["status"] = 401

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AgentOnlineAuditTrail %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AgentOnlineAuditTrail = AgentOnlineAuditTrailAPI.as_view()


class CRMCobrowsingSupportHistoryAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            request_data = request.data

            is_all_data_available = True
            required_inputs = ["session_id"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            session_id = request_data["session_id"]

            cobrowse_io_obj = None

            try:
                cobrowse_io_obj = CobrowseIO.objects.filter(
                    session_id=session_id, access_token=crm_integration_model.access_token).first()
            except:
                pass

            if cobrowse_io_obj == None:
                response["Head"]['ResponseCode'] = 304
                response["Head"]['Description'] = 'Requested Session does not exist'
                return Response(data=response)

            session_data = parse_cobrowse_io_data_public_api(
                cobrowse_io_obj, CobrowsingFileAccessManagement)

            if session_data:
                response["Head"]['ResponseCode'] = 200
                response["Head"]['Description'] = 'success'
                response["Body"]['data'] = session_data

            try:
                category = "CRMCobrowsingSupportHistory"
                description = json.dumps(response)
                save_system_audit_trail(category, description, cobrowse_io_obj,
                                        crm_integration_model.access_token, SystemAuditTrail, None)
            except:
                pass
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMCobrowsingSupportHistoryAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMCobrowsingSupportHistory = CRMCobrowsingSupportHistoryAPI.as_view()


class CRMCobrowsingChatHistoryAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            request_data = request.data

            is_all_data_available = True
            required_inputs = ["session_id"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            session_id = request_data["session_id"]

            cobrowse_io_obj = None

            try:
                cobrowse_io_obj = CobrowseIO.objects.filter(
                    session_id=session_id, access_token=crm_integration_model.access_token).first()
            except:
                pass

            if cobrowse_io_obj == None:
                response["Head"]['ResponseCode'] = 304
                response["Head"]['Description'] = 'Requested Session does not exist'
                return Response(data=response)

            chat_history = parse_cobrowse_io_chat_history(cobrowse_io_obj)

            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
            response["Body"]['data'] = chat_history

            try:
                category = "CRMCobrowsingChatHistory"
                description = json.dumps(response)
                save_system_audit_trail(category, description, cobrowse_io_obj,
                                        crm_integration_model.access_token, SystemAuditTrail, None)
            except:
                pass
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMCobrowsingChatHistoryAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMCobrowsingChatHistory = CRMCobrowsingChatHistoryAPI.as_view()


def CRMCognoMeetAutoLogin(request, token):
    try:
        logger.info("token = %s ", str(token), extra={'AppName': 'EasyAssist'})
        login_token_obj = CRMCobrowseLoginToken.objects.filter(
            token=token).first()

        if login_token_obj == None:
            return HttpResponse('Login Failed')

        meeting_io = login_token_obj.meeting_io
        if meeting_io == None:
            return HttpResponse("Invalid Meeting")

        if is_meeting_expired(meeting_io):
            login_token_obj.is_expired = True
            login_token_obj.save()

        if login_token_obj.is_expired == True:
            return HttpResponse('Login Session Expired')

        user_obj = meeting_io.agent.user

        if not request.user.is_authenticated:
            login(request, user_obj)

            description = "Login into System"
            save_audit_trail(
                meeting_io.agent, COBROWSING_LOGIN_ACTION, description, CobrowsingAuditTrail)

            add_audit_trail(
                "EASYASSISTAPP",
                meeting_io.agent.user,
                "Login",
                description,
                json.dumps({"token": token}),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

        meeting_link = "/easy-assist/meeting/" + str(meeting_io.meeting_id)
        return redirect(meeting_link)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CRMCognoMeetAutoLogin %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse("Invalid token")


class CRMCognoMeetCreateMeetingAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            request_data = request.data

            is_all_data_available = True

            required_inputs = [
                "full_name",
                "mobile_number",
                "meeting_start_date",
                "meeting_start_time",
                "meeting_end_time",
                "email",
                "agent_id",
                "send_email_to_customer",
                "send_email_to_agent",
            ]

            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            full_name = strip_html_tags(request_data["full_name"])
            mobile_number = strip_html_tags(request_data["mobile_number"])
            meeting_start_date = strip_html_tags(
                request_data["meeting_start_date"])
            meeting_start_time = strip_html_tags(
                request_data["meeting_start_time"])
            meeting_end_time = strip_html_tags(
                request_data["meeting_end_time"])
            email_id = strip_html_tags(request_data["email"])
            agent_id = strip_html_tags(request_data["agent_id"])
            send_email_to_customer = request_data["send_email_to_customer"]
            send_email_to_agent = request_data["send_email_to_agent"]

            meeting_description = ""
            meeting_password = ""

            if "meeting_description" in request_data:
                meeting_description = strip_html_tags(
                    request_data["meeting_description"])

            if "meeting_password" in request_data:
                meeting_password = strip_html_tags(
                    request_data["meeting_password"])

            agent_obj = CobrowseAgent.objects.filter(
                user__username__iexact=agent_id, is_account_active=True).first()

            if agent_obj == None:
                agent_obj = CobrowseAgent.objects.filter(
                    virtual_agent_code__iexact=agent_id, is_account_active=True).first()

            if agent_obj == None:
                agent_obj = CobrowseAgent.objects.filter(
                    agent_code__iexact=agent_id, is_account_active=True).first()

            if agent_obj == None:
                response["Head"]['ResponseCode'] = 303
                response["Head"]['Description'] = 'Agent not exist'
                return Response(data=response)

            meeting_io = CobrowseVideoConferencing.objects.create(
                full_name=full_name,
                mobile_number=mobile_number,
                email_id=email_id,
                agent=agent_obj,
                meeting_description=str(meeting_description),
                meeting_start_date=meeting_start_date,
                meeting_start_time=meeting_start_time,
                meeting_end_time=meeting_end_time)

            if meeting_password != "":
                meeting_io.meeting_password = meeting_password
                meeting_io.save()

            login_token_obj = CRMCobrowseLoginToken.objects.create(
                meeting_io=meeting_io)

            agent_meeting_url = settings.EASYASSISTAPP_HOST + \
                "/easy-assist/crm/meeting/" + str(login_token_obj.token)

            client_meeting_url = str(settings.EASYASSISTAPP_HOST) + \
                "/easy-assist/meeting/" + str(meeting_io.meeting_id)

            try:
                agent_name = agent_obj.agent_name()

                start_time = meeting_io.meeting_start_time
                start_time = datetime.datetime.strptime(
                    start_time, "%H:%M:%S").time()
                start_time = start_time.strftime("%I:%M %p")

                meeting_date = meeting_io.meeting_start_date
                meeting_date = datetime.datetime.strptime(
                    meeting_date, '%Y-%m-%d')
                meeting_date = meeting_date.strftime("%d %B, %Y")

                join_password = ""
                if meeting_password != "":
                    join_password = meeting_password
                else:
                    join_password = 'No Password Required.'

                if send_email_to_customer:
                    thread = threading.Thread(target=send_meeting_link_over_mail, args=(
                        email_id, full_name, client_meeting_url, agent_name, start_time, meeting_date, join_password), daemon=True)
                    thread.start()

                if send_email_to_agent:
                    agent_email_id = agent_obj.user.email

                    thread = threading.Thread(target=send_meeting_link_over_mail, args=(
                        agent_email_id, agent_name, agent_meeting_url, full_name, start_time, meeting_date, join_password), daemon=True)
                    thread.start()

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error CRMCognoMeetCreateMeetingAPI Send Mail %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
            response["Body"]["meeting_id"] = str(meeting_io.meeting_id)
            response["Body"]['agent_meeting_url'] = agent_meeting_url
            response["Body"]['client_meeting_url'] = client_meeting_url

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMCognoMeetCreateMeetingAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMCognoMeetCreateMeeting = CRMCognoMeetCreateMeetingAPI.as_view()


class CRMCognoMeetDeleteMeetingAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            request_data = request.data

            is_all_data_available = True
            required_inputs = ["meeting_id"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            meeting_id = strip_html_tags(request_data["meeting_id"])
            try:
                cobrowse_video_obj = CobrowseVideoConferencing.objects.filter(
                    meeting_id=meeting_id, is_deleted=False).first()
            except Exception:
                cobrowse_video_obj = None

            if cobrowse_video_obj == None:
                response["Head"]["ResponseCode"] = 304
                response["Head"]["Description"] = "Meeting does exist"
            else:
                cobrowse_video_obj.is_deleted = True
                cobrowse_video_obj.save()
                response["Head"]['ResponseCode'] = 200
                response["Head"]['Description'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMCognoMeetDeleteMeetingAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMCognoMeetDeleteMeeting = CRMCognoMeetDeleteMeetingAPI.as_view()


class CRMCognoMeetMeetingStatusAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            request_data = request.data

            is_all_data_available = True
            required_inputs = ["meeting_id"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            meeting_id = strip_html_tags(request_data["meeting_id"])
            try:
                cobrowse_video_obj = CobrowseVideoConferencing.objects.filter(
                    meeting_id=meeting_id, is_deleted=False).first()
            except Exception:
                cobrowse_video_obj = None

            if cobrowse_video_obj == None:
                response["Head"]["ResponseCode"] = 304
                response["Head"]["Description"] = "Meeting does not exist"
            else:
                meeting_audit_trail = CobrowseVideoAuditTrail.objects.filter(
                    cobrowse_video=cobrowse_video_obj).first()

                customer_name = cobrowse_video_obj.full_name
                mobile_number = cobrowse_video_obj.mobile_number

                meeting_start_date_time = None
                if cobrowse_video_obj.meeting_start_date and cobrowse_video_obj.meeting_start_time:
                    meeting_start_date = cobrowse_video_obj.meeting_start_date.strftime(
                        DATE_TIME_FORMAT)
                    meeting_start_time = str(
                        cobrowse_video_obj.meeting_start_time.strftime("%I:%M:%S %p"))
                    meeting_start_date_time = meeting_start_date + " " + meeting_start_time

                agent_join_time = None
                meeting_status = "NotStarted"
                meeting_duration = None

                if meeting_audit_trail:
                    meeting_duration = meeting_audit_trail.get_meeting_duration_in_seconds()

                    meeting_status = None
                    if meeting_audit_trail.is_meeting_ended == True:
                        meeting_status = "Completed"
                    else:
                        meeting_status = "Ongoing"

                    agent_join_time = None
                    if meeting_audit_trail.agent_joined:
                        agent_join_time = meeting_audit_trail.agent_joined.astimezone(
                            pytz.timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d %I:%M:%S %p")

                response["Body"]["customer_name"] = customer_name
                response["Body"]["mobile_number"] = mobile_number
                response["Body"]["meeting_start_time"] = meeting_start_date_time
                response["Body"]["agent_join_time"] = agent_join_time
                response["Body"]["meeting_status"] = meeting_status
                response["Body"]["meeting_duration"] = meeting_duration
                response["Head"]["ResponseCode"] = 200
                response["Head"]['Description'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMCognoMeetMeetingStatusAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMCognoMeetMeetingStatus = CRMCognoMeetMeetingStatusAPI.as_view()


class CRMCognoMeetMeetingDetailsAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            request_data = request.data

            is_all_data_available = True
            required_inputs = ["meeting_id"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            meeting_id = strip_html_tags(request_data["meeting_id"])

            try:
                cobrowse_video_obj = CobrowseVideoConferencing.objects.filter(
                    meeting_id=meeting_id, is_deleted=False).first()
            except Exception:
                cobrowse_video_obj = None

            if cobrowse_video_obj == None:
                response["Head"]['ResponseCode'] = 304
                response["Head"]['Description'] = 'Meeting does not exist'
            else:
                resp = parse_meeting_details_crm(
                    cobrowse_video_obj, CobrowseVideoAuditTrail)

                response["Head"]['ResponseCode'] = 200
                response["Head"]['Description'] = 'success'
                response["Body"] = resp
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMCognoMeetMeetingDetailsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMCognoMeetMeetingDetails = CRMCognoMeetMeetingDetailsAPI.as_view()


# This API is Deprecated
class CRMAgentAddAPI(APIView):

    def validate_request_data(self, request_data, access_token_obj):

        def is_email_valid(email):
            emailRegex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
            if(re.fullmatch(emailRegex, email)):
                return True
            else:
                return False

        def is_mobile_valid(mobile):
            mobileRegex = r'^[6-9]{1}[0-9]{9}$'
            if(re.fullmatch(mobileRegex, mobile)):
                return True
            else:
                return False

        def is_supervisor_list_valid(supervisor_list):
            for supervisor_name in supervisor_list:
                supervisor_obj = CobrowseAgent.objects.filter(
                    user__username__iexact=supervisor_name).first()
                if supervisor_obj == None:
                    return False

                if is_agent_under_me(access_token_obj.agent, supervisor_name) == False:
                    return False
            return True

        def is_language_list_valid(language_list):
            for language_name in language_list:
                language_name = language_name.strip()
                if len(language_name) <= 1 or len(language_name) > 25:
                    return False
            return True

        def is_product_category_list_valid(product_category_list):
            for product_category_name in product_category_list:
                product_category_name = product_category_name.strip()
                if len(product_category_name) <= 1 or len(product_category_name) > 25:
                    return False
            return True

        validation_response = {
            "status": "VALID",
            "ValidatorResult": {
                "agent_id": "-",
                "agent_name": "-",
                "agent_email": "-",
                "agent_mobile": "-",
                "agent_type": "-",
                "support_level": "-",
                "supervisor_list": "-",
                "language_list": "-",
                "product_category_list": "-",
            }
        }
        try:
            agent_id = request_data["agent_id"]
            agent_id = agent_id.strip()
            cobrowse_agent = CobrowseAgent.objects.filter(
                user__username__iexact=agent_id).first()
            if cobrowse_agent is not None:
                validation_response["ValidatorResult"]["agent_id"] = "ALREADY_EXIST"
                validation_response["status"] = "INVALID"
            else:
                validation_response["ValidatorResult"]["agent_id"] = "VALID"

            agent_name = request_data["agent_name"]
            agent_name = agent_name.strip()
            if len(agent_name) <= 1:
                validation_response["ValidatorResult"]["agent_name"] = "INVALID"
                validation_response["status"] = "INVALID"
            else:
                validation_response["ValidatorResult"]["agent_name"] = "VALID"

            agent_email = request_data["agent_email"]
            agent_email = agent_email.strip()
            if is_email_valid(agent_email) == False:
                validation_response["ValidatorResult"]["agent_email"] = "Expected valid email id"
                validation_response["status"] = "INVALID"
            else:
                validation_response["ValidatorResult"]["agent_email"] = "VALID"

            agent_mobile = request_data["agent_mobile"]
            agent_mobile = agent_mobile.strip()
            if is_mobile_valid(agent_mobile) == False:
                validation_response["ValidatorResult"]["agent_mobile"] = "Expected 10 digit"
                validation_response["status"] = "INVALID"
            else:
                validation_response["ValidatorResult"]["agent_mobile"] = "VALID"

            agent_type = request_data["agent_type"]
            agent_type = agent_type.strip()
            if agent_type.lower() not in ["agent", "supervisor"]:
                validation_response["ValidatorResult"]["agent_type"] = "Expected from ['agent', 'supervisor']"
                validation_response["status"] = "INVALID"
            else:
                validation_response["ValidatorResult"]["agent_type"] = "VALID"

            support_level = request_data["support_level"]
            support_level = support_level.strip()
            if support_level.lower() not in ["l1", "l2", "l3"]:
                validation_response["ValidatorResult"]["support_level"] = "Expected from ['l1', 'l2', 'l3']"
                validation_response["status"] = "INVALID"
            else:
                validation_response["ValidatorResult"]["support_level"] = "VALID"

            supervisor_list = request_data["supervisor_list"]
            if is_supervisor_list_valid(supervisor_list) == False:
                validation_response["ValidatorResult"]["supervisor_list"] = "Invalid Supervisor"
                validation_response["status"] = "INVALID"
            else:
                validation_response["ValidatorResult"]["supervisor_list"] = "VALID"

            language_list = request_data["language_list"]
            if is_language_list_valid(language_list) == False:
                validation_response["ValidatorResult"]["language_list"] = "Invalid Language"
                validation_response["status"] = "INVALID"
            else:
                validation_response["ValidatorResult"]["language_list"] = "VALID"

            product_category_list = request_data["product_category_list"]
            if is_product_category_list_valid(product_category_list) == False:
                validation_response["ValidatorResult"]["product_category_list"] = "Invalid Product Category"
                validation_response["status"] = "INVALID"
            else:
                validation_response["ValidatorResult"]["product_category_list"] = "VALID"
        except Exception:
            validation_response["status"] = "INVALID"

        return validation_response

    def create_new_agent(self, request_data, access_token_obj):
        agent_id = request_data["agent_id"]
        agent_name = request_data["agent_name"]
        agent_email = request_data["agent_email"]
        agent_mobile = request_data["agent_mobile"]
        agent_type = request_data["agent_type"]
        support_level = request_data["support_level"]
        supervisor_list = request_data["supervisor_list"]
        language_list = request_data["language_list"]
        product_category_list = request_data["product_category_list"]

        support_level = support_level[0].upper() + support_level[1:]
        active_agent = access_token_obj.agent

        user = None
        try:
            user = User.objects.get(username__iexact=agent_id)
        except Exception:
            user = User.objects.create(first_name=agent_name,
                                       email=agent_email,
                                       username=agent_id,
                                       status="2",
                                       role="bot_builder")

        password = generate_password(access_token_obj.password_prefix)
        user.email = agent_email
        user.set_password(password)
        user.save()

        cobrowse_agent = CobrowseAgent.objects.create(user=user,
                                                      mobile_number=agent_mobile,
                                                      role=agent_type.lower(),
                                                      support_level=support_level.upper(),
                                                      access_token=access_token_obj)

        thread = threading.Thread(target=send_password_over_email, args=(
            agent_email, agent_name, password, settings.EASYCHAT_HOST_URL, ), daemon=True)
        thread.start()

        selected_product_category_pk_list = []
        for product_category in product_category_list:
            product_category = str(product_category).strip()
            product_category = product_category[0].upper(
            ) + product_category[1:].lower()
            product_category_obj = active_agent.product_category.filter(
                title=product_category).first()
            if product_category_obj == None:
                total_product_category = active_agent.product_category.all().count()
                product_category_obj = ProductCategory.objects.create(
                    title=product_category)
                product_category_obj.index = total_product_category
                product_category_obj.is_deleted = False
                product_category_obj.save()
                active_agent.product_category.add(product_category_obj)
                active_agent.save()
            if product_category_obj:
                selected_product_category_pk_list.append(
                    product_category_obj.pk)
            else:
                selected_product_category_pk_list.clear()
                break

        selected_language_pk_list = []
        for language in language_list:
            language = str(language).strip()
            language = language[0].upper() + language[1:].lower()
            language_obj = active_agent.supported_language.filter(
                title=language).first()
            if language_obj == None:
                total_language_count = active_agent.supported_language.all().count()
                language_obj = LanguageSupport.objects.create(
                    title=language)
                language_obj.index = total_language_count
                language_obj.is_deleted = False
                language_obj.save()

                active_agent.supported_language.add(language_obj)
                active_agent.save()
            if language_obj:
                selected_language_pk_list.append(language_obj.pk)
            else:
                selected_language_pk_list.clear()

        selected_supervisor_pk_list = []
        for supervisor_username in supervisor_list:
            if agent_type == "agent":
                supervisor_obj = active_agent.agents.all().filter(
                    role="supervisor", is_account_active=True, user__username__iexact=supervisor_username).first()
                if supervisor_obj is None and (active_agent.user.username.lower() == supervisor_username.lower()):
                    supervisor_obj = active_agent
            else:
                supervisor_obj = active_agent

            selected_supervisor_pk_list.append(supervisor_obj.pk)

        add_selected_supervisor(
            selected_supervisor_pk_list, active_agent, cobrowse_agent, CobrowseAgent)
        add_supported_language(
            cobrowse_agent, selected_language_pk_list, LanguageSupport)
        add_product_category_to_user(
            cobrowse_agent, selected_product_category_pk_list, ProductCategory)

        for selected_supervisor_pk in selected_supervisor_pk_list:
            supervisor_obj = CobrowseAgent.objects.filter(
                pk=selected_supervisor_pk).first()
            add_supported_language(
                supervisor_obj, selected_language_pk_list, LanguageSupport)
            add_product_category_to_user(
                supervisor_obj, selected_product_category_pk_list, ProductCategory)

        try:
            description = "New " + agent_type + \
                " (" + agent_name + ") has been added through CRM Api"
            save_audit_trail(
                active_agent, COBROWSING_ADDUSER_ACTION, description, CobrowsingAuditTrail)

            add_audit_trail(
                "EASYASSISTAPP",
                active_agent.user,
                "Add-User",
                description,
                json.dumps(request_data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )
        except Exception:
            pass

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            access_token_obj = crm_integration_model.access_token

            request_data = request.data

            is_all_data_available = True
            required_inputs = [
                "agent_id",
                "agent_name",
                "agent_email",
                "agent_mobile",
                "support_level",
                "agent_type",
                "supervisor_list",
                "language_list",
                "product_category_list"
            ]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            validation_response = self.validate_request_data(
                request_data, access_token_obj)
            if validation_response["status"] == "INVALID":
                response["Head"]['ResponseCode'] = 306
                response["Head"]['Description'] = 'Invalid Input'
                response["Body"]['ValidatorResult'] = validation_response["ValidatorResult"]
                return Response(data=response)

            self.create_new_agent(request_data, access_token_obj)

            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMAgentAddAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMAgentAdd = CRMAgentAddAPI.as_view()


# This API is Deprecated
class CRMAgentDeleteAPI(APIView):

    def delete_agent(self, request_data, access_token_obj, request):
        agent_id = request_data["agent_id"]
        active_agent = access_token_obj.agent

        cobrowse_agent = CobrowseAgent.objects.filter(
            user__username__iexact=agent_id).first()
        agent_name = cobrowse_agent.user.username
        user_type = cobrowse_agent.role
        cobrowse_agent.delete()

        try:
            description = user_type[0].upper(
            ) + user_type[1:] + " (" + agent_name + ") has been deleted through CRM Api"
            save_audit_trail(
                active_agent, COBROWSING_DELETEUSER_ACTION, description, CobrowsingAuditTrail)

            add_audit_trail(
                "EASYASSISTAPP",
                active_agent.user,
                "Delete-User",
                description,
                json.dumps(request_data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )
        except Exception:
            pass

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            access_token_obj = crm_integration_model.access_token
            active_agent = access_token_obj.agent

            request_data = request.data

            is_all_data_available = True
            required_inputs = ["agent_id"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            agent_id = request_data["agent_id"]

            is_under_me = is_agent_under_me(active_agent, agent_id)

            if is_under_me == False:
                response["Head"]["ResponseCode"] = 303
                response["Head"]['Description'] = 'Agent not exists'
                return Response(data=response)

            self.delete_agent(request_data, access_token_obj, request)

            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMAgentDeleteAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMAgentDelete = CRMAgentDeleteAPI.as_view()


# This API is Deprecated
class CRMAgentChangeStatusAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            access_token_obj = crm_integration_model.access_token
            active_agent = access_token_obj.agent

            request_data = request.data

            is_all_data_available = True
            required_inputs = ["agent_id"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            agent_id = request_data["agent_id"]

            is_under_me = is_agent_under_me(active_agent, agent_id)

            if is_under_me == False:
                response["Head"]["ResponseCode"] = 303
                response["Head"]['Description'] = 'Agent not exists'
                return Response(data=response)

            cobrowse_agent = CobrowseAgent.objects.filter(
                user__username__iexact=agent_id).first()

            if "is_active" in request_data:
                is_active = request_data["is_active"]
                change_agent_is_active_flag(
                    is_active, cobrowse_agent, CobrowseAgentOnlineAuditTrail, CobrowseAgentWorkAuditTrail)

            if "is_account_active" in request_data:
                is_account_active = request_data["is_account_active"]
                change_agent_is_account_active_flag(
                    is_account_active, active_agent, cobrowse_agent, request, request_data, CobrowsingAuditTrail)

                response["Head"]['ResponseCode'] = 200
                response["Head"]['Description'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMAgentChangeStatusAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMAgentChangeStatus = CRMAgentChangeStatusAPI.as_view()


# This API is Deprecated
class CRMAgentChangePasswordAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            access_token_obj = crm_integration_model.access_token
            active_agent = access_token_obj.agent

            request_data = request.data

            is_all_data_available = True
            required_inputs = ["agent_id", "old_password", "new_password"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            agent_id = request_data["agent_id"]

            is_under_me = is_agent_under_me(active_agent, agent_id)

            if is_under_me == False:
                response["Head"]["ResponseCode"] = 303
                response["Head"]['Description'] = 'Agent not exists'
                return Response(data=response)

            old_password = request_data["old_password"]
            new_password = request_data["new_password"]

            cobrowse_agent = CobrowseAgent.objects.filter(
                user__username__iexact=agent_id).first()
            user_obj = cobrowse_agent.user

            is_valid_password = False
            if user_obj.check_password(old_password):
                is_valid_password = True

            if is_valid_password:

                if(validate_user_new_password(cobrowse_agent, new_password, old_password, AgentPasswordHistory) == "VALID"):
                    user_obj.is_online = False
                    user_obj.set_password(new_password)
                    user_obj.save()

                    new_password_hash = hashlib.sha256(
                        new_password.encode()).hexdigest()
                    AgentPasswordHistory.objects.create(
                        agent=cobrowse_agent, password_hash=new_password_hash)

                    description = "User (" + user_obj.username + \
                        "'s) password was changed through CRM"
                    save_audit_trail(cobrowse_agent, COBROWSING_UPDATEUSER_ACTION,
                                     description, CobrowsingAuditTrail)

                    add_audit_trail(
                        "EASYASSISTAPP",
                        user_obj,
                        "Updated-User",
                        description,
                        json.dumps({}),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )
                    cobrowse_agent.is_active = False
                    cobrowse_agent.save()

                    response["Head"]['ResponseCode'] = 200
                    response["Head"]['Description'] = 'success'

                else:
                    response["Head"]['ResponseCode'] = 307
                    response["Head"]['Description'] = 'Password Matched with previous password'

            else:
                response["Head"]['ResponseCode'] = 306
                response["Head"]['Description'] = 'Your old password is incorrect. Kindly enter valid password'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMAgentChangePasswordAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMAgentChangePassword = CRMAgentChangePasswordAPI.as_view()


class CRMUpdateMeetingSettingsAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            access_token_obj = crm_integration_model.access_token

            request_data = request.data

            is_all_data_available = True

            required_inputs = []

            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            required_any_one = [
                "allow_meeting_feedback",
                "meeting_default_password",
                "meeting_host_url",
                "allow_meeting_end_time",
                "meeting_end_time",
                "meet_background_color",
                "allow_support_documents",
                "share_document_from_livechat",
                "allow_only_support_documents",
                "enable_chat_functionality",
            ]

            if is_all_data_available:
                is_all_data_available = False
                for required_input in required_any_one:
                    if required_input in request_data:
                        is_all_data_available = True

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            for attribute_name in required_any_one:
                if attribute_name in request_data:
                    attribute_value = request_data[attribute_name]
                    access_token_obj.__setattr__(
                        attribute_name, attribute_value)

            access_token_obj.save()

            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMUpdateMeetingSettingsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMUpdateMeetingSettings = CRMUpdateMeetingSettingsAPI.as_view()


class CRMAgentMeetingsAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            access_token_obj = crm_integration_model.access_token
            active_agent = access_token_obj.agent

            request_data = request.data

            is_all_data_available = True
            required_inputs = ["agent_id"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            agent_id = request_data["agent_id"]

            is_under_me = is_agent_under_me(active_agent, agent_id)

            if is_under_me == False:
                response["Head"]["ResponseCode"] = 303
                response["Head"]['Description'] = 'Agent not exists'
                return Response(data=response)

            cobrowse_agent = CobrowseAgent.objects.filter(
                user__username__iexact=agent_id).first()

            cognovid_objs = CobrowseVideoConferencing.objects.filter(
                agent=cobrowse_agent, is_expired=False, is_cobrowsing_meeting=False).order_by('-meeting_start_date')

            cognovid_support_meeting_objs = CobrowseVideoConferencing.objects.filter(
                support_meeting_agents=cobrowse_agent, is_expired=False, is_cobrowsing_meeting=False).order_by('-meeting_start_date')

            cognovid_objs = cognovid_objs | cognovid_support_meeting_objs

            unexpired_cognovid_objs = []
            for cognovid_obj in cognovid_objs:
                check_cogno_meet_status(cognovid_obj)
                if cognovid_obj.is_expired == False:
                    unexpired_cognovid_objs.append(cognovid_obj)

            meetings = []
            for cobrowse_video_obj in unexpired_cognovid_objs:
                resp = parse_meeting_details_crm(
                    cobrowse_video_obj, CobrowseVideoAuditTrail)
                meetings.append(resp)

            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
            response["Body"]['meetings'] = meetings
            response["Body"]['count'] = len(meetings)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMAgentMeetingsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMAgentMeetings = CRMAgentMeetingsAPI.as_view()


class CRMMeetingAnalyticsAPI(APIView):

    def validate_request_data(self, request_data, access_token_obj):
        validation_response = {
            "status": "VALID",
            "ValidatorResult": {
                "start_date": "VALID",
                "end_date": "VALID",
            }
        }
        try:
            date_regex = r'^[0-9]{2}-[0-9]{2}-[0-9]{4}$'

            start_date = request_data["start_date"]
            if not re.fullmatch(date_regex, start_date):
                validation_response["ValidatorResult"]["start_date"] = "Expected date format : DD-MM-YYYY"
                validation_response["status"] = "INVALID"

            end_date = request_data["end_date"]
            if not re.fullmatch(date_regex, end_date):
                validation_response["ValidatorResult"]["end_date"] = "Expected date format : DD-MM-YYYY"
                validation_response["status"] = "INVALID"
        except Exception:
            validation_response["status"] = "INVALID"

        return validation_response

    def get_crm_analytics_obj(self, datetime_start, datetime_end, agent_objs):
        cogno_vid_objs = CobrowseVideoConferencing.objects.filter(
            meeting_start_date__gte=datetime_start,
            meeting_start_date__lte=datetime_end, agent__in=agent_objs)

        total_meeting_scheduled = cogno_vid_objs.count()
        total_meeting_completed = cogno_vid_objs.filter(
            is_expired=True).count()
        total_ongoing_meeting = analytics_ongoing_meeting_count(
            cogno_vid_objs, CobrowseVideoAuditTrail)
        avg_call_duration = 0

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

        return {
            "total_meeting_scheduled": total_meeting_scheduled,
            "total_meeting_completed": total_meeting_completed,
            "total_ongoing_meeting": total_ongoing_meeting,
            "avg_call_duration": avg_call_duration,
        }

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(
                request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            access_token_obj = crm_integration_model.access_token
            active_agent = access_token_obj.agent

            request_data = request.data

            is_all_data_available = True
            required_inputs = ["start_date", "end_date"]
            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            validation_response = self.validate_request_data(
                request_data, access_token_obj)
            if validation_response["status"] == "INVALID":
                response["Head"]['ResponseCode'] = 306
                response["Head"]['Description'] = 'Invalid Input'
                response["Body"]['ValidatorResult'] = validation_response["ValidatorResult"]
                return Response(data=response)

            start_date = request_data["start_date"]
            end_date = request_data["end_date"]

            date_format = DATE_TIME_FORMAT_6
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()

            agent_objs = get_list_agents_under_admin(
                active_agent, is_active=None, is_account_active=None)

            all_agent_dump = self.get_crm_analytics_obj(
                datetime_start, datetime_end, agent_objs)

            agent_wise_analytics = []
            for agent_obj in agent_objs:
                agent_analytics_dump = self.get_crm_analytics_obj(
                    datetime_start, datetime_end, [agent_obj])
                agent_analytics_dump["agent_id"] = agent_obj.user.username
                agent_wise_analytics.append(agent_analytics_dump)

            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
            response["Body"] = {
                "total_meeting_scheduled": all_agent_dump["total_meeting_scheduled"],
                "total_meeting_completed": all_agent_dump["total_meeting_completed"],
                "total_ongoing_meeting": all_agent_dump["total_ongoing_meeting"],
                "avg_call_duration": all_agent_dump["avg_call_duration"],
                "agent_wise_analytics": agent_wise_analytics,
            }
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMMeetingAnalyticsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=response)


CRMMeetingAnalytics = CRMMeetingAnalyticsAPI.as_view()


class MaskingPIIDataOTPAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            agent_username = active_agent.user.username
            try:
                pii_data_obj = CobrowsePIIDataOTP.objects.get(
                    agent=active_agent)
            except Exception:
                logger.info("Creating new CobrowsePIIDataOTP object for %s",
                            str(agent_username), extra={'AppName': 'EasyAssist'})
                pii_data_obj = CobrowsePIIDataOTP.objects.create(
                    agent=active_agent)

            otp = random.randrange(10**5, 10**6)

            pii_data_obj.otp = otp
            pii_data_obj.save()

            email_ids = []
            cobrowse_config_obj = get_developer_console_cobrowsing_settings()
            if cobrowse_config_obj:
                email_ids = json.loads(
                    cobrowse_config_obj.cobrowsing_masking_pii_data_otp_email)

            if len(email_ids) == 0 or email_ids == None:
                email_ids = settings.MASKING_PII_DATA_OTP_EMAIL
                console_config = get_developer_console_settings()
                if console_config:
                    email_ids = console_config.get_masking_pii_data_otp_emails()

            thread = threading.Thread(target=send_masking_pii_data_otp_mail, args=(
                email_ids, otp, agent_username), daemon=True)
            thread.start()

            response["status"] = "200"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error MaskingPIIDataOTPAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


MaskingPIIDataOTP = MaskingPIIDataOTPAPI.as_view()


class VerifyMaskingPIIDataOTPAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            otp = data["otp"]

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            pii_data_obj = CobrowsePIIDataOTP.objects.filter(
                agent=active_agent).first()

            if pii_data_obj:
                if otp == pii_data_obj.otp:
                    response["status"] = 200
                    access_token_obj.enable_masking_pii_data = False
                    
                    save_audit_trail(
                        active_agent, 
                        COBROWSING_CHANGESETTINGS_ACTION, 
                        "Disabled Masking PII Toggle", 
                        CobrowsingAuditTrail
                    )
                    
                    access_token_obj.save()
                else:
                    response["status"] = 301
            else:
                response["status"] = 401
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error VerifyMaskingPIIDataOTPAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


VerifyMaskingPIIDataOTP = VerifyMaskingPIIDataOTPAPI.as_view()


class EnableMaskingPIIDataAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            if active_agent.role == "admin":
                access_token_obj = active_agent.get_access_token_obj()
                access_token_obj.enable_masking_pii_data = True
                
                save_audit_trail(
                    active_agent, 
                    COBROWSING_CHANGESETTINGS_ACTION, 
                    "Enabled Masking PII Toggle", 
                    CobrowsingAuditTrail
                )

                access_token_obj.save()
                response["status"] = "200"
            else:
                response["status"] = "401"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EnableMaskingPIIDataAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


EnableMaskingPIIData = EnableMaskingPIIDataAPI.as_view()


def SalesEmailAnalyticsSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        if cobrowse_agent.role == "admin":

            email_analytics_default_data = get_email_analytics_data()

            return render(request, "EasyAssistApp/cobrowse_email_analytics_settings.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "email_analytics_default_data": email_analytics_default_data,
            })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesEmailAnalyticsSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


class SaveEnableEmailSettingsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            enable_email_settings = data["enable_email_settings"]

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            if active_agent.role == "admin":
                access_token_obj = active_agent.get_access_token_obj()
                access_token_obj.enable_mailer_analytics = enable_email_settings
                access_token_obj.save()

                if enable_email_settings:
                    audit_trail_action = "EnableEmailAnalyticsSettings"
                    audit_trail_description = "Enable email analytics settings"
                    cobrowse_audit_trail_action = ENABLE_EMAIL_ANALYTICS_ACTION
                else:
                    audit_trail_action = "DisableEmailAnalyticsSettings"
                    audit_trail_description = "Disable email analytics settings"
                    cobrowse_audit_trail_action = DISABLE_EMAIL_ANALYTICS_ACTION

                save_audit_trail(
                    active_agent,
                    cobrowse_audit_trail_action,
                    audit_trail_description,
                    CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    audit_trail_action,
                    audit_trail_description,
                    json.dumps({}),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
            else:
                response["status"] = 401

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveEnableEmailSettingsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveEnableEmailSettings = SaveEnableEmailSettingsAPI.as_view()


class SaveEmailAnalyticsProfileAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            if active_agent.role == "admin":

                if not data["email_frequency"]:
                    response["status"] = 302
                    response["message"] = "Please select email frequency to continue"
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                is_existing_profile = False
                existing_profile_obj = None

                if "profile_id" in data:
                    profile_id = data["profile_id"]

                    access_token_obj = active_agent.get_access_token_obj()

                    existing_profile_obj = CobrowseMailerAnalyticsProfile.objects.filter(
                        pk=int(profile_id), access_token=access_token_obj).first()

                    if existing_profile_obj:
                        is_existing_profile = True

                email_address_list = data["email_address_list"]
                if len(email_address_list):
                    for email_id in email_address_list:
                        if not is_email_valid(email_id):
                            response["status"] = 301
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)
                            
                if is_existing_profile:
                    status, message = update_existing_profile(
                        data, access_token_obj,
                        existing_profile_obj,
                        CobrowseMailerAnalyticsProfile,
                        CobrowseMailerAnalyticsGraph,
                        CobrowseMailerAnalyticsTable,
                        CobrowseMailerAnalyticsAttachment,
                        CobrowseMailerAnalyticsCalendar)

                else:
                    status, message = create_new_email_analytics_profile(
                        data, access_token_obj,
                        CobrowseMailerAnalyticsProfile,
                        CobrowseMailerAnalyticsGraph,
                        CobrowseMailerAnalyticsTable,
                        CobrowseMailerAnalyticsAttachment,
                        CobrowseMailerAnalyticsCalendar)

                if status == 302:
                    response["status"] = status
                    response["message"] = message
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                    
                if status == 200:

                    if is_existing_profile:
                        audit_trail_action = "UpdateEmailAnalyticsProfile"
                        audit_trail_description = "Update email analytics profile"
                        cobrowse_audit_trail_action = UPDATE_EMAIL_ANALYTICS_PROFILE_ACTION

                    else:
                        audit_trail_action = "CreateEmailAnalyticsProfile"
                        audit_trail_description = "Create email analytics profile"
                        cobrowse_audit_trail_action = CREATE_EMAIL_ANALYTICS_PROFILE_ACTION

                    save_audit_trail(
                        active_agent,
                        cobrowse_audit_trail_action,
                        audit_trail_description,
                        CobrowsingAuditTrail)

                    add_audit_trail(
                        "EASYASSISTAPP",
                        active_agent.user,
                        audit_trail_action,
                        audit_trail_description,
                        json.dumps({}),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

                response["status"] = status
                response["message"] = message
            else:
                response["status"] = "401"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveEmailAnalyticsProfileAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveEmailAnalyticsProfile = SaveEmailAnalyticsProfileAPI.as_view()


class GetEmailAnalyticsProfilesAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = get_active_agent_obj(request, CobrowseAgent)
            if active_agent.role == "admin":
                access_token_obj = active_agent.get_access_token_obj()
                profile_objs = CobrowseMailerAnalyticsProfile.objects.filter(
                    access_token=access_token_obj, is_deleted=False)

                analytics_profiles = []
                for profile_obj in profile_objs:
                    parsed_profile_data = parse_email_analytics_profile(
                        profile_obj, CobrowseMailerAnalyticsCalendar)
                    analytics_profiles.append(parsed_profile_data)

                response["status"] = 200
                response["analytics_profiles"] = analytics_profiles
            else:
                response["status"] = "401"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetEmailAnalyticsProfilesAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetEmailAnalyticsProfiles = GetEmailAnalyticsProfilesAPI.as_view()


class DeleteEmailAnalyticsProfileAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            if active_agent.role == "admin":
                profile_id = data["profile_id"]

                access_token_obj = active_agent.get_access_token_obj()
                profile_obj = CobrowseMailerAnalyticsProfile.objects.filter(
                    pk=profile_id, access_token=access_token_obj, is_deleted=False).first()

                if profile_obj:
                    profile_obj.is_deleted = True
                    profile_obj.save()

                    audit_trail_action = "DeleteEmailAnalyticsProfile"
                    audit_trail_description = "Delete email analytics profile"

                    save_audit_trail(
                        active_agent,
                        DELETE_EMAIL_ANALYTICS_PROFILE_ACTION,
                        audit_trail_description,
                        CobrowsingAuditTrail)

                    add_audit_trail(
                        "EASYASSISTAPP",
                        active_agent.user,
                        audit_trail_action,
                        audit_trail_description,
                        json.dumps({}),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )
                    response["status"] = 200
                else:
                    response["status"] = 301

            else:
                response["status"] = 401
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteEmailAnalyticsProfileAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteEmailAnalyticsProfile = DeleteEmailAnalyticsProfileAPI.as_view()


class TriggerEmailAnalyticsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            if active_agent.role == "admin":
                profile_id = data["profile_id"]

                access_token_obj = active_agent.get_access_token_obj()
                profile_obj = CobrowseMailerAnalyticsProfile.objects.filter(
                    pk=profile_id, access_token=access_token_obj, is_deleted=False).first()

                email_sent_audit_trail_obj = CobrowseMailerProfileStaticEmailAuditTrail.objects.filter(
                    profile=profile_obj).first()

                if email_sent_audit_trail_obj is None:
                    email_sent_audit_trail_obj = CobrowseMailerProfileStaticEmailAuditTrail.objects.create(
                        profile=profile_obj)

                current_time = timezone.now()
                last_email_sent_time = email_sent_audit_trail_obj.last_static_email_sent_time

                total_time_diff = (
                    current_time - last_email_sent_time).total_seconds()

                if total_time_diff >= 3600:
                    email_sent_audit_trail_obj.last_email_sent_time = timezone.now()
                    email_sent_audit_trail_obj.email_sent_count = STATIC_EMAIL_TRIGGER_COUNT
                    email_sent_audit_trail_obj.save()

                email_sent_count = email_sent_audit_trail_obj.email_sent_count
                if email_sent_count <= 0:
                    response["status"] = 301
                else:
                    email_sent_count = email_sent_count - 1
                    email_sent_audit_trail_obj.email_sent_count = email_sent_count
                    email_sent_audit_trail_obj.save()
                    status = process_profile_data_and_send_email(
                        profile_obj, access_token_obj, None, True, CobrowseVideoAuditTrail)
                    response["status"] = status
            else:
                response["status"] = 401
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error TriggerEmailAnalyticsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


TriggerEmailAnalytics = TriggerEmailAnalyticsAPI.as_view()


def PDFrender(request):
    return render(request, "EasyAssistApp/render_pdf.html")


class CheckCobrowsingStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

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

            cobrowse_io_obj = None
            try:
                cobrowse_io_obj = CobrowseIO.objects.get(session_id=id)
            except Exception:
                pass

            if cobrowse_io_obj != None:
                response["is_archived"] = cobrowse_io_obj.is_archived
            else:
                response["is_archived"] = True

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckCobrowsingStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckCobrowsingStatus = CheckCobrowsingStatusAPI.as_view()


class UpdateCustomerMeetingRequestAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = data["id"]

            cobrowse_io = CobrowseIO.objects.get(session_id=id)

            if data["status"] == "true":
                cobrowse_io.allow_customer_meeting = "true"
                cobrowse_io.customer_meeting_request_status = False
                cobrowse_io.meeting_start_datetime = timezone.now()
                description = "Meeting request accepted by agent"

            elif data["status"] == "false":
                cobrowse_io.allow_customer_meeting = "false"
                cobrowse_io.customer_meeting_request_status = False
                cobrowse_io.meeting_start_datetime = None
                description = "Meeting request declined by agent"

            category = "session_details"
            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, None)

            cobrowse_io.save()
            response["status"] = 200
            response["message"] = "success"
            response["meeting_allowed"] = data["status"]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateAgentMeetingRequestAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateCustomerMeetingRequest = UpdateCustomerMeetingRequestAPI.as_view()


class CustomerInitiateMeetingStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            active_agent = get_active_agent_obj(request, CobrowseAgent)
            is_cognomeet_active = None
            if active_agent:
                is_cognomeet_active = active_agent.is_cognomeet_active
            is_meeting_allowed = False
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            if cobrowse_io.allow_customer_meeting == 'None' or cobrowse_io.allow_customer_meeting == None:
                response["is_meeting_allowed"] = is_meeting_allowed
                response["is_agent_answer"] = False
                response["is_cognomeet_active"] = is_cognomeet_active
                response["status"] = 301
                response["message"] = "success"
            elif cobrowse_io.allow_customer_meeting == 'true':
                is_meeting_allowed = True

                response["is_meeting_allowed"] = is_meeting_allowed
                response["is_agent_answer"] = True
                response["is_cognomeet_active"] = is_cognomeet_active
                response["status"] = 200
                response["message"] = "success"
            else:
                is_meeting_allowed = False

                response["is_meeting_allowed"] = is_meeting_allowed
                response["is_agent_answer"] = True
                response["is_cognomeet_active"] = is_cognomeet_active
                response["status"] = 200
                response["message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckMeetingStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CustomerInitiateMeetingStatus = CustomerInitiateMeetingStatusAPI.as_view()


class UploadAgentPictureAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "agent":

                cobrowse_access_token = active_agent.get_access_token_obj()

                filename = strip_html_tags(data["filename"])
                base64_data = strip_html_tags(data["base64_file"])

                if filename == "" or filename == "null":
                    response["status"] = 301
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

                filename = generate_random_key(
                    10) + "_" + filename.replace(" ", "")

                absolute_path = "files/EasyAssistApp/AgentProfilePicture/" + \
                    str(cobrowse_access_token.key) + '/' + \
                    str(active_agent.user.pk)
                if not os.path.isdir(absolute_path):
                    os.makedirs(absolute_path)

                file_path = absolute_path + '/' + filename

                file_extention = file_path.split(".")[-1]
                file_extention = file_extention.lower()
                allowed_files_list = ["png", "jpg", "jpeg"]
                if file_extention in allowed_files_list:
                    media_type = "image"
                else:
                    media_type = None

                if media_type == None or check_malicious_file_from_filename(filename, allowed_files_list) or check_malicious_file_from_content(base64_data, allowed_files_list):
                    response["status"] = 300
                else:
                    fh = open(file_path, "wb")
                    fh.write(base64.b64decode(base64_data))
                    fh.close()
                    active_agent.agent_profile_pic_source = file_path
                    active_agent.save()
                    response["status"] = 200
                    response["message"] = "success"
                    response["file_path"] = file_path
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadAgentPictureAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadAgentPicture = UploadAgentPictureAPI.as_view()


class DeleteAgentProfilePictureAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "agent":
                active_agent.agent_profile_pic_source = ""
                active_agent.save()
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteCobrowserLogoAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteAgentProfilePicture = DeleteAgentProfilePictureAPI.as_view()


class MaliciousProfilePictureAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            base64_data = strip_html_tags(data["base64_file"])
            allowed_files_list = ["png", "jpg", "jpeg"]
            if check_malicious_file_from_content(base64_data, allowed_files_list):
                response["status"] = 300
            else:
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("MalicioustProfilePictureAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


MalicioustProfilePicture = MaliciousProfilePictureAPI.as_view()


class UploadChatBubbleIconAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            filename = sanitize_input_string(data["filename"])
            base64_data = strip_html_tags(data["base64_file"])

            if active_agent.role == "admin" and filename != "" and base64_data != "":

                cobrowse_access_token = active_agent.get_access_token_obj()

                filename = generate_random_key(
                    10) + "_" + filename.replace(" ", "")

                file_path = "files/EasyAssistApp/img/" + filename

                file_extention = file_path.split(".")[-1]
                file_extention = file_extention.lower()

                allowed_files_list = ["png"]

                if file_extention in allowed_files_list:
                    media_type = "image"
                else:
                    media_type = None

                if media_type == None or check_malicious_file_from_filename(filename, allowed_files_list) or check_malicious_file_from_content(base64_data, allowed_files_list):
                    response["status"] = 300
                else:
                    fh = open(file_path, "wb")
                    fh.write(base64.b64decode(base64_data))
                    fh.close()
                    cobrowse_access_token.chat_bubble_icon_source = file_path
                    cobrowse_access_token.save()

                    response["status"] = 200
                    response["file_path"] = file_path
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadChatBubbleIconAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadChatBubbleIcon = UploadChatBubbleIconAPI.as_view()


class ResetChatBubbleIconAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":
                cobrowse_access_token = active_agent.get_access_token_obj()
                cobrowse_access_token.chat_bubble_icon_source = ""
                cobrowse_access_token.save()
                response["status"] = 200
                response["file_path"] = ""
                response["message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ResetChatBubbleIconAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ResetChatBubbleIcon = ResetChatBubbleIconAPI.as_view()


def SalesAdminProfileSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/admin_profile.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAdminProfileSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesIntegrationSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/sales_integration.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesIntegrationSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesChromeExtensionSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        chrome_extension_obj = ChromeExtensionDetails.objects.filter(
            access_token=access_token_obj)
        if chrome_extension_obj:
            chrome_extension_obj = chrome_extension_obj[0]

        return render(request, "EasyAssistApp/sales_chrome_extension.html", {
            "chrome_extension_obj": chrome_extension_obj,
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesEmailAnalyticsSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesAdvancedSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()
        email_ids = []
        cobrowse_config_obj = get_developer_console_cobrowsing_settings()

        if cobrowse_config_obj:
            email_ids = json.loads(
                cobrowse_config_obj.cobrowsing_masking_pii_data_otp_email)

        if len(email_ids) == 0 or email_ids == None:
            email_ids = settings.MASKING_PII_DATA_OTP_EMAIL
            console_config = get_developer_console_settings()
            if console_config:
                email_ids = console_config.get_masking_pii_data_otp_emails()

        return render(request, "EasyAssistApp/advanced_settings.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "email_ids": email_ids,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAdvancedSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesSettingsOptions(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/settings_option.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesSettingsOptions %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesGeneralOptionsSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/sales_settings_options_general.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesGeneralOptionsSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesGeneralAgentSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/sales_settings_general_agent.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "FLOATING_BUTTON_POSITION": FLOATING_BUTTON_POSITION,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesGeneralAgentSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesGeneralAdminSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()
        product_category_list = access_token_obj.get_product_categories()
        product_categories = [x.strip()
                              for x in str(product_category_list).split(',')]
        popup_configurations_obj = get_easyassist_popup_configurations_obj(
            access_token_obj, EasyAssistPopupConfigurations)

        inactivity_popup_urls = json.loads(
            popup_configurations_obj.inactivity_popup_urls)
        exit_intent_popup_urls = json.loads(
            popup_configurations_obj.exit_intent_popup_urls)

        return render(request, "EasyAssistApp/sales_settings_general_admin.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "popup_configurations_obj": popup_configurations_obj,
            "product_category": json.dumps(product_categories),
            "inactivity_popup_urls": inactivity_popup_urls,
            "exit_intent_popup_urls": exit_intent_popup_urls,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesGeneralAdminSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesGeneralCustomerSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/sales_customer_side_settings.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesGeneralCustomerSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesGeneralConsoleSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/sales_general_console_settings.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesGeneralConsoleSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesCobrowseSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        if access_token_obj.allow_video_meeting_only:
            return redirect("sales-settings-options")

        return render(request, "EasyAssistApp/sales_cobrowse_settings.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesGeneralConsoleSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesCobrowseAgentSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/sales_cobrowse_agent_settings.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesCobrowseAgentSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesCobrowseAdminSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/sales_cobrowse_admin_settings.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesCobrowseAdminSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesCobrowseCustomersSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/sales_cobrowse_customer_side_settings.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesGeneralConsoleSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesCobrowseGeneralSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()
        return render(request, "EasyAssistApp/sales_cobrowse_general_settings.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesCobrowseGeneralSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesVideoCallSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/sales_video_call_settings.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesVideoCallSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesVideoCallAgentSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/sales_video_call_agent_settings.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesVideoCallAgentSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesVideoCallAdminSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        return render(request, "EasyAssistApp/sales_video_call_admin_settings.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesVideoCallAdminSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def SalesCalendarSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        access_token_obj = cobrowse_agent.get_access_token_obj()
        if not access_token_obj.enable_inbound and cobrowse_agent.role == "admin":
            return redirect("sales-settings-options")
        if not access_token_obj.enable_inbound and cobrowse_agent.role != "admin":
            return redirect("sales-settings-agent-home-page")
        current_month = str(datetime.datetime.now().month)
        current_year = str(datetime.datetime.now().year)
        calendar_type = request.GET.get('days')
        selected_month = request.GET.get('month')
        selected_year = request.GET.get('years')
        if selected_month is not None:
            full_path = request.get_full_path()
            full_path = full_path.split('?')
            months = full_path[-1].split('month=')
            months_list = []
            for month in months:
                if "Jan" in month:
                    months_list.append(1)
                if "Feb" in month:
                    months_list.append(2)
                if "Mar" in month:
                    months_list.append(3)
                if "Apr" in month:
                    months_list.append(4)
                if "May" in month:
                    months_list.append(5)
                if "Jun" in month:
                    months_list.append(6)
                if "Jul" in month:
                    months_list.append(7)
                if "Aug" in month:
                    months_list.append(8)
                if "Sep" in month:
                    months_list.append(9)
                if "Oct" in month:
                    months_list.append(10)
                if "Nov" in month:
                    months_list.append(11)
                if "Dec" in month:
                    months_list.append(12)
        if calendar_type is not None:
            if calendar_type == "Holidays":
                calendar_type = "2"
            else:
                calendar_type = "1"
        else:
            calendar_type = "1"
        if selected_year and selected_month is None:
            months_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            selected_month = True
        selected_year = current_year if selected_year == None else selected_year
        selected_month = [
            int(current_month)] if selected_month == None else months_list

        if cobrowse_agent.role != "admin":

            cobrowse_admin = get_admin_from_active_agent(
                cobrowse_agent, CobrowseAgent)

            calendar_objs = CobrowseCalendar.objects.filter(created_by=cobrowse_admin, event_type=calendar_type, event_date__year=int(
                selected_year), event_date__month__in=selected_month).order_by('event_date')

            total_rows_per_pages = 31
            total_calendar_objs = len(calendar_objs)
            paginator = Paginator(
                calendar_objs, total_rows_per_pages)
            page = request.GET.get('page')

            try:
                calendar_objs = paginator.page(page)
            except PageNotAnInteger:
                calendar_objs = paginator.page(1)
            except EmptyPage:
                calendar_objs = paginator.page(paginator.num_pages)

            if page != None:
                start_point = total_rows_per_pages * (int(page) - 1) + 1
                end_point = min(total_rows_per_pages *
                                int(page), total_calendar_objs)
                if start_point > end_point:
                    start_point = max(end_point - len(calendar_objs) + 1, 1)
            else:
                start_point = 1
                end_point = min(total_rows_per_pages, total_calendar_objs)
            return render(request, "EasyAssistApp/sales_agent_calendar_setting.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "COBROWSING_AGENT_SUPPORT": COBROWSING_AGENT_SUPPORT,
                "calendar_type": calendar_type,
                "selected_month": selected_month,
                "selected_year": selected_year,
                "calendar_objs": calendar_objs,
                "start_point": start_point,
                "end_point": end_point,
                "total_calendar_objs": total_calendar_objs,
                "calendar_created_by": cobrowse_admin
            })

        else:
            agent_working_days = access_token_obj.get_cobrowse_working_days()

            calendar_objs = CobrowseCalendar.objects.filter(created_by=cobrowse_agent, event_type=calendar_type, event_date__year=int(
                selected_year), event_date__month__in=selected_month).order_by('event_date')

            total_rows_per_pages = 31
            total_calendar_objs = len(calendar_objs)
            paginator = Paginator(
                calendar_objs, total_rows_per_pages)
            page = request.GET.get('page')

            try:
                calendar_objs = paginator.page(page)
            except PageNotAnInteger:
                calendar_objs = paginator.page(1)
            except EmptyPage:
                calendar_objs = paginator.page(paginator.num_pages)

            if page != None:
                start_point = total_rows_per_pages * (int(page) - 1) + 1
                end_point = min(total_rows_per_pages *
                                int(page), total_calendar_objs)
                if start_point > end_point:
                    start_point = max(end_point - len(calendar_objs) + 1, 1)
            else:
                start_point = 1
                end_point = min(total_rows_per_pages, total_calendar_objs)

            return render(request, "EasyAssistApp/sales_calendar_settings.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "agent_working_days": agent_working_days,
                "cobrowsing_days": COBROWSING_DAYS,
                "calendar_type": calendar_type,
                "selected_month": selected_month,
                "selected_year": selected_year,
                "calendar_objs": calendar_objs,
                "start_point": start_point,
                "end_point": end_point,
                "total_calendar_objs": total_calendar_objs,
            })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesCalendarSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


class SaveGeneralAgentSettingsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":

                cobrowse_access_token = active_agent.get_access_token_obj()

                cobrowse_access_token.enable_chat_functionality = data[
                    "enable_chat_functionality"]

                cobrowse_access_token.enable_preview_functionality = data[
                    "enable_preview_functionality"]

                cobrowse_access_token.enable_chat_bubble = data["enable_chat_bubble"]

                cobrowse_access_token.floating_button_position = sanitize_input_string(
                    data["floating_button_position"])

                cobrowse_access_token.share_document_from_livechat = data[
                    "share_document_from_livechat"]

                cobrowse_access_token.allow_support_documents = data["allow_support_documents"]

                cobrowse_access_token.allow_only_support_documents = data[
                    "allow_only_support_documents"]

                if data["enable_auto_offline_agent"] == True:
                    cobrowse_access_token.disable_auto_offline_agent = False
                else:
                    cobrowse_access_token.disable_auto_offline_agent = True

                cobrowse_access_token.display_agent_profile = data["display_agent_profile"]

                cobrowse_access_token.save()

                description = "Custom App Configuration Changes - General"
                save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                 description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveGeneralAgentSettingsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveGeneralAgentSettings = SaveGeneralAgentSettingsAPI.as_view()


class SaveGeneralAdminSettingsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":
                if data["enable_inbound"] and data["maximum_active_leads"] and not data["maximum_active_leads_threshold"]:
                    response['status'] = 302
                    response['message'] = "Maximum leads that can be assigned to an agent should be greater than 0"
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                if data["enable_auto_assign_unattended_lead"]:
                    if not int(data["auto_assign_unattended_lead_timer"]):
                        response['status'] = 302
                        response['message'] = "Auto assign timer cannot be empty or 0"
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                    if data["enable_auto_assign_to_one_agent"]:
                        if not len(data["auto_assign_lead_end_session_message"].strip()):
                            response['status'] = 302
                            response['message'] = "Auto end session message cannot be empty"
                            return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                        if not len(data["auto_assigned_unattended_lead_archive_timer"].strip()) or not int(data["auto_assigned_unattended_lead_archive_timer"]):
                            response['status'] = 302
                            response['message'] = "Auto end session timer cannot be empty or 0"
                            return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                if data["allow_popup_on_browser_leave"] and not data["enable_recursive_browser_leave_popup"]:
                    if not len(data["exit_intent_popup_count"].strip()) or not int(data["exit_intent_popup_count"]):
                        response['status'] = 302
                        response['message'] = "Number of times Exit Intent should pop up cannot be empty or 0"
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                if not len(data["archive_on_unassigned_time_threshold"].strip()) or not int(data["archive_on_unassigned_time_threshold"]):
                    response['status'] = 302
                    response['message'] = "Auto archive timer cannot be empty or 0"
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                if data["field_stuck_event_handler"]:
                    if not data["field_recursive_stuck_event_check"]:
                        if not len(data["inactivity_auto_popup_number"].strip()) or not int(data["inactivity_auto_popup_number"]):
                            response['status'] = 302
                            response['message'] = "Number of times connect with an agent auto pop up after in-activity cannot be empty or 0"
                            return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                        if not validate_input_number(data["inactivity_auto_popup_number"]):
                            response['status'] = 302
                            response['message'] = "Please enter number of times connect with an agent auto pop up after in-activity without special characters"
                            return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                    if not data["field_stuck_timer"] or data["field_stuck_timer"] <= 0 or data["field_stuck_timer"] > 3600:
                        response['status'] = 302
                        response['message'] = "Session in-activity time interval should be between 1-3600 seconds"
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                        
                if data["enable_greeting_bubble"]:
                    if not data["greeting_bubble_auto_popup_timer"]:
                        response['status'] = 302
                        response['message'] = "Number of times greeting bubble pops up cannot be 0 or empty"
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                    if not len(data["greeting_bubble_text"].strip()):
                        response['status'] = 302
                        response['message'] = "Greeting bubble text cannot be empty"
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                if data["lead_generation"] and data["enable_proxy_cobrowsing"]:
                    if not data["proxy_link_expire_time"] or data["proxy_link_expire_time"] < 1 or data["proxy_link_expire_time"] > 1440:
                        response['status'] = 302
                        response["message"] = "Link expiry time should be between 1-1440 minutes"
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                cobrowse_access_token = active_agent.get_access_token_obj()
                popup_configurations_obj = get_easyassist_popup_configurations_obj(
                    cobrowse_access_token, EasyAssistPopupConfigurations)

                cobrowse_access_token.enable_inbound = data[
                    "enable_inbound"]

                cobrowse_access_token.enable_request_in_queue = data["enable_request_in_queue"]
                
                cobrowse_access_token.floating_button_bg_color = "#" + remo_html_from_string(strip_html_tags(
                    data["floating_button_bg_color"]))

                cobrowse_access_token.enable_greeting_bubble = data[
                    "enable_greeting_bubble"]

                if data["enable_greeting_bubble"]:
                    cobrowse_access_token.greeting_bubble_auto_popup_timer = data[
                        "greeting_bubble_auto_popup_timer"]

                    cobrowse_access_token.greeting_bubble_text = sanitize_input_string(
                        data["greeting_bubble_text"])
                    
                cobrowse_access_token.enable_lead_status = data["enable_lead_status"]
                
                cobrowse_access_token.maximum_active_leads = data[
                    "maximum_active_leads"]

                if data["enable_inbound"] and data["maximum_active_leads"]:
                    cobrowse_access_token.maximum_active_leads_threshold = data[
                        "maximum_active_leads_threshold"]
                
                if data["enable_request_in_queue"]:
                    cobrowse_access_token.enable_auto_assign_unattended_lead = False
                else:    
                    cobrowse_access_token.enable_auto_assign_unattended_lead = data[
                        "enable_auto_assign_unattended_lead"]

                auto_assign_unattended_lead_message = remo_html_from_string(strip_html_tags(data[
                    "auto_assign_unattended_lead_message"].strip()))
                if auto_assign_unattended_lead_message != "":
                    cobrowse_access_token.auto_assign_unattended_lead_message = auto_assign_unattended_lead_message

                cobrowse_access_token.enable_auto_assign_to_one_agent = data[
                    "enable_auto_assign_to_one_agent"]

                if data["enable_auto_assign_unattended_lead"]:
                    if data["enable_auto_assign_to_one_agent"]:
                        cobrowse_access_token.auto_assign_lead_end_session_message = remo_html_from_string(strip_html_tags(data[
                            "auto_assign_lead_end_session_message"].strip()))
                        cobrowse_access_token.auto_assigned_unattended_lead_archive_timer = int(sanitize_input_string(
                            data["auto_assigned_unattended_lead_archive_timer"]))

                    cobrowse_access_token.auto_assign_unattended_lead_timer = int(data[
                        "auto_assign_unattended_lead_timer"])

                cobrowse_access_token.show_floating_easyassist_button = data[
                    "show_floating_easyassist_button"]

                cobrowse_access_token.show_only_if_agent_available = data[
                    "show_only_if_agent_available"]

                cobrowse_access_token.floating_button_left_right_position = data[
                    "floating_button_left_right_position"]

                cobrowse_access_token.allow_language_support = data[
                    "allow_language_support"]

                if "allow_language_support" in data and "supported_language_list" in data:
                    save_language_support(
                        active_agent, data["supported_language_list"], LanguageSupport)

                cobrowse_access_token.disable_connect_button_if_agent_unavailable = data[
                    "disable_connect_button_if_agent_unavailable"]

                cobrowse_access_token.enable_non_working_hours_modal_popup = data[
                    "enable_non_working_hours_modal_popup"]

                message_if_agent_unavailable = remo_html_from_string(strip_html_tags(
                    data["message_if_agent_unavailable"]))
                if message_if_agent_unavailable != "":
                    cobrowse_access_token.message_if_agent_unavailable = message_if_agent_unavailable

                message_on_non_working_hours = remo_html_from_string(strip_html_tags(
                    data["message_on_non_working_hours"]))
                if message_on_non_working_hours != "":
                    cobrowse_access_token.message_on_non_working_hours = message_on_non_working_hours

                cobrowse_access_token.enable_followup_leads_tab = data[
                    "enable_followup_leads_tab"]

                cobrowse_access_token.choose_product_category = data[
                    "choose_product_category"]

                product_category_message = remo_html_from_string(strip_html_tags(
                    data["message_on_choose_product_category_modal"]))

                if product_category_message != "":
                    cobrowse_access_token.message_on_choose_product_category_modal = product_category_message

                if data["choose_product_category"] or data["enable_tag_based_assignment_for_outbound"]:
                    save_product_category(
                        active_agent, data["product_category_list"], ProductCategory)

                connect_message = sanitize_input_string(
                    data["connect_message"])
                if connect_message != "":
                    cobrowse_access_token.connect_message = connect_message

                cobrowse_access_token.no_agent_connects_toast = data[
                    "no_agent_connects_toast"]

                cobrowse_access_token.no_agent_connects_toast_threshold = data[
                    "no_agent_connects_toast_threshold"]

                cobrowse_access_token.no_agent_connects_toast_text = remo_html_from_string(strip_html_tags(data[
                    "no_agent_connects_toast_text"]))

                cobrowse_access_token.no_agent_connects_toast_reset_message = sanitize_input_string(data[
                    "no_agent_connect_timer_reset_message"])

                cobrowse_access_token.no_agent_connects_toast_reset_count = int(sanitize_input_string(data[
                    "no_agent_connect_timer_reset_count"]))

                cobrowse_access_token.archive_on_unassigned_time_threshold = int(
                    remo_html_from_string(strip_html_tags(data["archive_on_unassigned_time_threshold"])))

                archive_message_on_unassigned_time_threshold = sanitize_input_string(
                    data["archive_message_on_unassigned_time_threshold"])

                cobrowse_access_token.archive_message_on_unassigned_time_threshold = archive_message_on_unassigned_time_threshold

                cobrowse_access_token.field_stuck_event_handler = data[
                    "field_stuck_event_handler"]

                if data["field_stuck_event_handler"]:
                    popup_configurations_obj.enable_url_based_inactivity_popup = data[
                        "enable_url_based_inactivity_popup"]

                    cobrowse_access_token.field_stuck_timer = int(
                        data["field_stuck_timer"])

                    if not data["field_recursive_stuck_event_check"]:
                        cobrowse_access_token.inactivity_auto_popup_number = int(
                            data["inactivity_auto_popup_number"])

                cobrowse_access_token.field_recursive_stuck_event_check = data[
                    "field_recursive_stuck_event_check"]

                cobrowse_access_token.allow_popup_on_browser_leave = data[
                    "allow_popup_on_browser_leave"]

                if data["allow_popup_on_browser_leave"]:
                    popup_configurations_obj.enable_url_based_exit_intent_popup = data[
                        "enable_url_based_exit_intent_popup"]

                    if not data["enable_recursive_browser_leave_popup"]:
                        cobrowse_access_token.no_of_times_exit_intent_popup = data[
                            "exit_intent_popup_count"]

                cobrowse_access_token.enable_recursive_browser_leave_popup = data[
                    "enable_recursive_browser_leave_popup"]

                cobrowse_access_token.show_easyassist_connect_agent_icon = data[
                    "show_easyassist_connect_agent_icon"]

                cobrowse_access_token.lead_generation = data[
                    "lead_generation"]

                cobrowse_access_token.show_floating_button_after_lead_search = data[
                    "show_floating_button_after_lead_search"]

                cobrowse_access_token.enable_tag_based_assignment_for_outbound = data[
                    "enable_tag_based_assignment_for_outbound"]

                cobrowse_access_token.allow_agent_to_customer_cobrowsing = data[
                    "allow_agent_to_customer_cobrowsing"]

                cobrowse_access_token.allow_agent_to_screen_record_customer_cobrowsing = data[
                    "allow_agent_to_screen_record_customer_cobrowsing"]

                cobrowse_access_token.allow_agent_to_audio_record_customer_cobrowsing = data[
                    "allow_agent_to_audio_record_customer_cobrowsing"]

                cobrowse_access_token.unattended_lead_auto_assignment_counter = int(sanitize_input_string(data[
                    "auto_assign_unattended_lead_transfer_count"]))

                cobrowse_access_token.assign_agent_under_same_supervisor = data[
                    "assign_agent_under_same_supervisor"]

                cobrowse_access_token.allow_connect_with_virtual_agent_code = data[
                    "allow_connect_with_virtual_agent_code"]

                cobrowse_access_token.connect_with_virtual_agent_code_mandatory = data[
                    "connect_with_virtual_agent_code_mandatory"]

                if data["connect_with_virtual_agent_code_mandatory"]:
                    cobrowse_access_token.enable_auto_assign_unattended_lead = False
                    cobrowse_access_token.enable_request_in_queue = False
                
                if cobrowse_access_token.allow_agent_to_customer_cobrowsing == True:
                    cobrowse_access_token.enable_inbound = False
                    cobrowse_access_token.enable_greeting_bubble = False
                    cobrowse_access_token.lead_generation = False
                    cobrowse_access_token.show_cobrowsing_meeting_lobby = False
                    cobrowse_access_token.enable_no_agent_connects_toast_meeting = False
                    cobrowse_access_token.allow_video_meeting_only = False

                if cobrowse_access_token.enable_inbound == True or cobrowse_access_token.lead_generation == True:
                    cobrowse_access_token.allow_agent_to_customer_cobrowsing = False

                proxy_config_obj = cobrowse_access_token.get_proxy_config_obj()
                proxy_config_obj.enable_proxy_cobrowsing = data["enable_proxy_cobrowsing"]

                if data["lead_generation"] and data["enable_proxy_cobrowsing"]:
                    cobrowse_access_token.enable_verification_code_popup = False
                    cobrowse_access_token.show_verification_code_modal = False
                    cobrowse_access_token.enable_low_bandwidth_cobrowsing = False
                    proxy_config_obj.proxy_link_expire_time = data["proxy_link_expire_time"]
                    proxy_config_obj.save(update_fields=["enable_proxy_cobrowsing", "proxy_link_expire_time"])
        
                cobrowse_access_token.save()
                popup_configurations_obj.save()

                disable_inbound_cobrowsing_features(cobrowse_access_token)

                description = "Custom App Configuration Changes - General"
                save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                 description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveGeneralAdminSettingsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveGeneralAdminSettings = SaveGeneralAdminSettingsAPI.as_view()


class SaveGeneralConsoleSettingsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":

                cobrowse_access_token = active_agent.get_access_token_obj()
                password_prefix = remo_html_from_string(
                    strip_html_tags(data["password_prefix"]))
                if password_prefix != "":
                    cobrowse_access_token.password_prefix = password_prefix

                if data["cobrowsing_console_theme_color"] is None:
                    cobrowse_access_token.cobrowsing_console_theme_color = None
                else:
                    cobrowse_access_token.cobrowsing_console_theme_color = remo_html_from_string(strip_html_tags(json.dumps(
                        data["cobrowsing_console_theme_color"])))

                cobrowse_access_token.whitelisted_domain = remo_html_from_string(strip_html_tags(
                    data["whitelisted_domain"]))

                cobrowse_access_token.go_live_date = data["go_live_date"]

                cobrowse_access_token.deploy_chatbot_flag = data[
                    "deploy_chatbot_flag"]

                cobrowse_access_token.deploy_chatbot_url = data[
                    "deploy_chatbot_url"]

                cobrowse_access_token.save()

                description = "Custom App Configuration Changes - General"
                save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                 description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveGeneralConsoleSettingsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveGeneralConsoleSettings = SaveGeneralConsoleSettingsAPI.as_view()


class SaveCobrowseAgentSettingsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":

                cobrowse_access_token = active_agent.get_access_token_obj()

                cobrowse_access_token.enable_screenshot_agent = data[
                    "enable_screenshot_agent"]

                cobrowse_access_token.enable_invite_agent_in_cobrowsing = data[
                    "enable_invite_agent_in_cobrowsing"]

                if not data["enable_invite_agent_in_cobrowsing"]:
                    cobrowse_access_token.enable_session_transfer_in_cobrowsing = False
                else:
                    cobrowse_access_token.enable_session_transfer_in_cobrowsing = data[
                        "enable_session_transfer_in_cobrowsing"]

                cobrowse_access_token.transfer_request_archive_time = sanitize_input_string(data[
                    "transfer_request_archive_time"])

                cobrowse_access_token.enable_edit_access = data[
                    "enable_edit_access"]

                cobrowse_access_token.allow_cobrowsing_meeting = data[
                    "allow_video_calling_cobrowsing"]

                cobrowse_access_token.customer_initiate_video_call = data[
                    "customer_initiate_video_call"]

                cobrowse_access_token.customer_initiate_voice_call = data[
                    "customer_initiate_voice_call"
                ]

                cobrowse_access_token.customer_initiate_video_call_as_pip = data[
                    "customer_initiate_video_call_as_pip"]

                cobrowse_access_token.enable_voip_calling = data[
                    "enable_voip_calling"]

                voip_calling_message = strip_html_tags(
                    data["voip_calling_text"])
                if voip_calling_message != "":
                    cobrowse_access_token.voip_calling_message = voip_calling_message

                voip_with_video_calling_message = strip_html_tags(
                    data["voip_with_video_calling_text"])
                if voip_with_video_calling_message != "":
                    cobrowse_access_token.voip_with_video_calling_message = voip_with_video_calling_message

                cobrowse_access_token.enable_auto_voip_with_video_calling_for_first_time = data[
                    "enable_auto_voip_with_video_calling_for_first_time"]

                cobrowse_access_token.enable_auto_voip_calling_for_first_time = data[
                    "enable_auto_voip_calling_for_first_time"]

                cobrowse_access_token.enable_voip_with_video_calling = data[
                    "enable_voip_with_video_calling"]

                cobrowse_access_token.allow_screen_recording = data[
                    "allow_screen_recording"]

                cobrowse_access_token.recording_expires_in_days = data[
                    "recording_expires_in_days"]

                cobrowse_access_token.save()

                description = "Custom App Configuration Changes - General"
                save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                 description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowseAgentSettingsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowseAgentSettings = SaveCobrowseAgentSettingsAPI.as_view()


class SaveCobrowseAdminSettingsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":

                if not len(str(data["archive_on_common_inactivity_threshold"]).strip()) or \
                        int(data["archive_on_common_inactivity_threshold"]) <= 0 \
                        or int(data["archive_on_common_inactivity_threshold"]) >= 60:
                    response["status"] = 302
                    response["message"] = "Session in-activity value should be between 1 and 60"
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                cobrowse_access_token = active_agent.get_access_token_obj()

                cobrowse_access_token.masking_type = data[
                    "masking_type"]

                cobrowse_access_token.allow_screen_sharing_cobrowse = data[
                    "allow_screen_sharing_cobrowse"]

                cobrowse_access_token.enable_manual_switching = data[
                    "enable_manual_switching"]

                cobrowse_access_token.enable_low_bandwidth_cobrowsing = data[
                    "enable_low_bandwidth_cobrowsing"]
                
                if data["enable_low_bandwidth_cobrowsing"]:
                    proxy_config_obj = cobrowse_access_token.get_proxy_config_obj()
                    proxy_config_obj.enable_proxy_cobrowsing = False
                    proxy_config_obj.save(update_fields=["enable_proxy_cobrowsing"])

                cobrowse_access_token.low_bandwidth_cobrowsing_threshold = data[
                    "low_bandwidth_cobrowsing_threshold"]

                cobrowse_access_token.archive_on_common_inactivity_threshold = data[
                    "archive_on_common_inactivity_threshold"]

                cobrowse_access_token.drop_link_expiry_time = data[
                    "drop_link_expiry_time"]

                cobrowse_access_token.urls_consider_lead_converted = strip_html_tags(
                    data["urls_consider_lead_converted"])

                cobrowse_access_token.restricted_urls = strip_html_tags(
                    data["restricted_urls"])

                cobrowse_access_token.save()

                description = "Custom App Configuration Changes - General"
                save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                 description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowseAdminSettingsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowseAdminSettings = SaveCobrowseAdminSettingsAPI.as_view()


class SaveCobrowseGeneralSettingsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":

                cobrowse_access_token = active_agent.get_access_token_obj()
                if data["enable_smart_agent_assignment"]:
                    if not len(data["reconnecting_window_timer_input"].strip()) or not int(data["reconnecting_window_timer_input"]):
                        response["status"] = 302
                        response["message"] = "Reconnecting window timer cannot be empty or 0"
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                lead_conversion_text = strip_html_tags(
                    data["lead_conversion_checkbox_text"])
                if lead_conversion_text != "":
                    cobrowse_access_token.lead_conversion_checkbox_text = lead_conversion_text

                cobrowse_access_token.enable_predefined_remarks = data[
                    "enable_predefined_remarks"]
                
                if data["enable_predefined_remarks"]:
                    cobrowse_access_token.predefined_remarks_optional = data[
                        'predefined_remarks_optional']
                else:
                    cobrowse_access_token.predefined_remarks_optional = False

                cobrowse_access_token.enable_predefined_remarks_with_buttons = data[
                    "enable_predefined_remarks_with_buttons"]

                cobrowse_access_token.enable_predefined_subremarks = data[
                    "enable_predefined_subremarks"]
                predefined_remark_list = data["predefined_remarks_list"]
                for remarks in predefined_remark_list:
                    remarks["remark"] = sanitize_input_string(
                        remarks["remark"])
                    if remarks["subremark"]:
                        for subremark in remarks["subremark"]:
                            subremark["remark"] = sanitize_input_string(
                                subremark["remark"])
                try:
                    predefined_remark_list = json.dumps(
                        predefined_remark_list)
                except Exception:
                    predefined_remark_list = json.dumps([])

                cobrowse_access_token.predefined_remarks = predefined_remark_list

                cobrowse_access_token.predefined_remarks_with_buttons = strip_html_tags(data[
                    "predefined_remarks_with_buttons"])

                agent_connect_message = strip_html_tags(
                    data["agent_connect_message"])
                cobrowse_access_token.enable_agent_connect_message = data[
                    "enable_agent_connect_message"]
                if agent_connect_message != "":
                    cobrowse_access_token.agent_connect_message = agent_connect_message

                cobrowse_access_token.enable_smart_agent_assignment = data[
                    "enable_smart_agent_assignment"]

                if data["enable_smart_agent_assignment"]:
                    cobrowse_access_token.smart_agent_assignment_reconnecting_window = int(data[
                        "reconnecting_window_timer_input"])

                cobrowse_access_token.save()

                description = "Custom App Configuration Changes - General"
                save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                 description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowseAdminSettingsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCobrowseGeneralSettings = SaveCobrowseGeneralSettingsAPI.as_view()


class SaveVideoAgentSettingsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":

                cobrowse_access_token = active_agent.get_access_token_obj()

                cobrowse_access_token.allow_capture_screenshots = data[
                    "allow_capture_screenshots"]

                cobrowse_access_token.enable_invite_agent_in_meeting = data[
                    "enable_invite_agent_in_meeting"]

                cobrowse_access_token.show_cobrowsing_meeting_lobby = data[
                    "show_cobrowsing_meeting_lobby"]

                cobrowse_access_token.enable_screen_sharing = data["enable_screen_sharing"]

                cobrowse_access_token.save()

                description = "Custom App Configuration Changes - General"
                save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                 description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveVideoAgentSettingsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveVideoAgentSettings = SaveVideoAgentSettingsAPI.as_view()


class SaveVideoAdminSettingsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, CobrowseAgent)

            if active_agent.role == "admin":

                cobrowse_access_token = active_agent.get_access_token_obj()

                cobrowse_access_token.proxy_server = strip_html_tags(
                    data["proxy_server"])

                cobrowse_access_token.meeting_default_password = strip_html_tags(data[
                    "meeting_default_password"])

                cobrowse_access_token.meeting_host_url = strip_html_tags(data[
                    "meeting_url"])

                cobrowse_access_token.meet_background_color = data[
                    "meet_background_color"]

                cobrowse_access_token.allow_meeting_feedback = data[
                    "allow_meeting_feedback"]

                cobrowse_access_token.allow_meeting_end_time = data[
                    "allow_meeting_end_time"]

                if data["allow_meeting_end_time"]:
                    cobrowse_access_token.meeting_end_time = data[
                        "meeting_end_time"]

                cobrowse_access_token.allow_video_meeting_only = data[
                    "allow_video_meeting_only"]

                if data["allow_video_meeting_only"]:
                    cobrowse_access_token.show_cobrowsing_meeting_lobby = True

                cobrowse_access_token.enable_no_agent_connects_toast_meeting = data[
                    "enable_no_agent_connects_toast_meeting"]

                no_agent_connects_meeting_toast_text = strip_html_tags(data[
                    "no_agent_connects_meeting_toast_text"]).strip()
                if no_agent_connects_meeting_toast_text != "":
                    cobrowse_access_token.no_agent_connects_meeting_toast_text = no_agent_connects_meeting_toast_text

                cobrowse_access_token.no_agent_connects_meeting_toast_threshold = data[
                    "no_agent_connects_meeting_toast_threshold"]

                if cobrowse_access_token.allow_video_meeting_only == True:
                    cobrowse_access_token.allow_agent_to_customer_cobrowsing = False
                    cobrowse_access_token.lead_generation = True
                    cobrowse_access_token.enable_inbound = True

                cobrowse_access_token.allow_generate_meeting = data["allow_generate_meeting"]
                cobrowse_access_token.enable_cognomeet = data["enable_cognomeet"]
                cobrowse_access_token.enable_meeting_recording = data["enable_meeting_recording"]

                if not (cobrowse_access_token.allow_generate_meeting or cobrowse_access_token.enable_cognomeet):
                    cobrowse_access_token.enable_cognomeet = False
                    cobrowse_access_token.enable_screen_sharing = False

                cobrowse_access_token.save()

                description = "Custom App Configuration Changes - Meeting"
                save_audit_trail(active_agent, COBROWSING_CHANGEAPPCONFIG_ACTION,
                                 description, CobrowsingAuditTrail)

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveVideoAdminSettingsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveVideoAdminSettings = SaveVideoAdminSettingsAPI.as_view()


class TransferCobrowsingSessionAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            agent_id = strip_html_tags(data["agent_id"])
            active_agent = get_active_agent_obj(request, CobrowseAgent)
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            cobrowse_agent = CobrowseAgent.objects.get(pk=int(agent_id))

            if cobrowse_io.allow_agent_cobrowse == "true" and cobrowse_io.access_token.enable_session_transfer_in_cobrowsing:
                transfer_agent_log = CobrowseIOTransferredAgentsLogs.objects.create(
                    cobrowse_io=cobrowse_io)
                transfer_agent_log.transferred_agent = cobrowse_agent
                transfer_agent_log.cobrowse_request_type = "transferred"
                transfer_agent_log.save()

                product_name = "Cogno Cobrowse"
                cobrowse_config_obj = get_developer_console_cobrowsing_settings()
                if cobrowse_config_obj:
                    product_name = cobrowse_config_obj.cobrowsing_title_text

                notification_message = "Hi, " + cobrowse_agent.user.username + \
                    "! A customer is waiting for you to connect on " + product_name + "."
                NotificationManagement.objects.create(show_notification=True,
                                                      agent=cobrowse_agent,
                                                      notification_message=notification_message,
                                                      cobrowse_io=cobrowse_io,
                                                      product_name=product_name)

                send_notification_to_agent(
                    cobrowse_agent, NotificationManagement)

                category = "session_transfer"
                description = "Session is transferred to " + \
                    str(cobrowse_agent.user.username)
                save_system_audit_trail(category, description, cobrowse_io,
                                        cobrowse_io.access_token, SystemAuditTrail, active_agent)

                response["status"] = 200
                response["agent_name"] = cobrowse_agent.user.first_name
                response["message"] = "success"
            else:
                response["status"] = 301
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error TransferCobrowsingSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


TransferCobrowsingSession = TransferCobrowsingSessionAPI.as_view()


class UpdateTransferCobrowsingSessionLogsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            transfer_agent_log = CobrowseIOTransferredAgentsLogs.objects.filter(
                cobrowse_io=cobrowse_io, transferred_status="", cobrowse_request_type="transferred").order_by("-log_request_datetime").first()
            cobrowse_agent = cobrowse_io.agent
            if cobrowse_io.allow_agent_cobrowse == "true" and transfer_agent_log:
                if "reject_request" in data:
                    transfer_agent_log.transferred_status = "rejected"
                    transfer_agent_log.save()
                else:
                    transfer_agent_log.transferred_status = "accepted"
                    cobrowse_io.agent = transfer_agent_log.transferred_agent
                    cobrowse_io.support_agents.add(cobrowse_agent)
                    cobrowse_io.save()
                    
                    invited_agent_details_objs = CobrowseIOInvitedAgentsDetails.objects.filter(
                        cobrowse_io=cobrowse_io)
                    if invited_agent_details_objs:
                        invited_agent_details_obj = invited_agent_details_objs[0]
                    else:
                        invited_agent_details_obj = CobrowseIOInvitedAgentsDetails.objects.create(
                            cobrowse_io=cobrowse_io)

                    if invited_agent_details_obj:
                        invited_agent_details_obj.support_agents_invited.add(
                            cobrowse_agent)
                        invited_agent_details_obj.support_agents_joined.add(
                            cobrowse_agent)
                        invited_agent_details_obj.save()
                    transfer_agent_log.save()
                response["status"] = 200
                response["message"] = "success"
            else:
                response["status"] = 301
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateTransferCobrowsingSessionLogsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateTransferCobrowsingSessionLogs = UpdateTransferCobrowsingSessionLogsAPI.as_view()


class GetTransferCobrowsingSessionLogsUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            if cobrowse_io.allow_agent_cobrowse == "true":
                transfer_agent_log = CobrowseIOTransferredAgentsLogs.objects.filter(
                    cobrowse_io=cobrowse_io, cobrowse_request_type="transferred").order_by("-log_request_datetime").first()
                if transfer_agent_log:
                    response["status"] = 200
                    response["agent_email"] = transfer_agent_log.transferred_agent.user.email
                    response["agent_name"] = transfer_agent_log.transferred_agent.user.first_name
                    response["agent_username"] = transfer_agent_log.transferred_agent.user.username
                    response["agent_id"] = transfer_agent_log.transferred_agent.user.pk
                    response["message"] = transfer_agent_log.transferred_status
            else:
                response["status"] = 301
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetTransferCobrowsingSessionLogsUpdateAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetTransferCobrowsingSessionLogsUpdate = GetTransferCobrowsingSessionLogsUpdateAPI.as_view()


class SaveInactivityPopupURLsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            if active_agent.role == "admin":
                urls_list = data["urls_list"]
                urls_list = list(set(urls_list))

                if not urls_list:
                    response["status"] = 301
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(
                        response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                    
                access_token_obj = active_agent.get_access_token_obj()
                popup_configurations_obj = get_easyassist_popup_configurations_obj(
                    access_token_obj, EasyAssistPopupConfigurations)
                inactivity_popup_urls = json.loads(
                    popup_configurations_obj.inactivity_popup_urls)

                for index, url in enumerate(urls_list):
                    url = remo_html_from_string(url)

                    if not is_url_valid(url):
                        response["status"] = 300
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(
                            response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)

                    urls_list[index] = url

                inactivity_popup_urls = json.dumps(urls_list)
                popup_configurations_obj.inactivity_popup_urls = inactivity_popup_urls
                popup_configurations_obj.save()

                response["status"] = 200
            else:
                response["status"] = 401
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveInactivityPopupURLsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveInactivityPopupURLs = SaveInactivityPopupURLsAPI.as_view()


class SaveExitIntentPopupURLsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            if active_agent.role == "admin":
                urls_list = data["urls_list"]
                urls_list = list(set(urls_list))

                if not urls_list:
                    response["status"] = 301
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(
                        response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                
                access_token_obj = active_agent.get_access_token_obj()
                popup_configurations_obj = get_easyassist_popup_configurations_obj(
                    access_token_obj, EasyAssistPopupConfigurations)
                exit_intent_popup_urls = json.loads(
                    popup_configurations_obj.exit_intent_popup_urls)

                for index, url in enumerate(urls_list):
                    url = remo_html_from_string(url)

                    if not is_url_valid(url):
                        response["status"] = 300
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(
                            response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)
                    urls_list[index] = url

                exit_intent_popup_urls = json.dumps(urls_list)
                popup_configurations_obj.exit_intent_popup_urls = exit_intent_popup_urls
                popup_configurations_obj.save()

                response["status"] = 200
            else:
                response["status"] = 401
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveExitIntentPopupURLsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveExitIntentPopupURLs = SaveExitIntentPopupURLsAPI.as_view()


def SalesAIQueueDashboard(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login/")

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        access_token_obj = cobrowse_agent.get_access_token_obj()

        if not access_token_obj.enable_request_in_queue:
            return redirect("/sales-ai/dashboard/")

        return render(request, "EasyAssistApp/queue_dashboard.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAIQueueDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(INVALID_ACCESS_CONSTANT)


class SelfAssignCobrowsingSessionAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)

            cobrowse_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = cobrowse_agent.get_access_token_obj()
            if cobrowse_agent.is_active:
                cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
                if access_token_obj.maximum_active_leads:
                    agent_active_leads = CobrowseIO.objects.filter(agent=cobrowse_agent, is_archived=False).count()
                    if agent_active_leads >= access_token_obj.maximum_active_leads_threshold:    
                        response["status"] = 401
                        response["agent_username"] = cobrowse_agent.user.username
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)

                if cobrowse_io.agent:
                    response["status"] = 501
                    response["agent_username"] = cobrowse_io.agent.user.username

                else:
                    cobrowse_io.agent = cobrowse_agent
                    if cobrowse_io.access_token.show_verification_code_modal == False:
                        cobrowse_io.allow_agent_cobrowse = "true"
                    cobrowse_io.self_assign_time = timezone.now()
                    cobrowse_io.save()

                    product_name = get_product_name()

                    create_notification_objects(
                        cobrowse_agent, cobrowse_io, product_name, NotificationManagement)
                    send_notification_to_agent(
                        cobrowse_agent, NotificationManagement)

                    category = "self_assigned"
                    description = "Session is self assigned to " + \
                        str(cobrowse_agent.user.username)
                    save_system_audit_trail(category, description, cobrowse_io,
                                            cobrowse_io.access_token, SystemAuditTrail, cobrowse_agent)

                    response["status"] = 200
                    response["agent_username"] = cobrowse_agent.user.username
                    response["message"] = "success"
            else:
                response["agent_username"] = cobrowse_agent.user.username
                response["status"] = 400

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SelfAssignCobrowsingSessionAPI %s at %s",
                            str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SelfAssignCobrowsingSession = SelfAssignCobrowsingSessionAPI.as_view()


class GetAllActiveQueueStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)
            cobrowse_agent = CobrowseAgent.objects.get(
                user=user, is_account_active=True)
            access_token_obj = cobrowse_agent.get_access_token_obj()
            request_io_objs = CobrowseIO.objects.filter(is_active=True, access_token=access_token_obj,
                                                        is_archived=False, agent=None, is_lead=False, is_reverse_cobrowsing=False).order_by('-request_datetime')

            if access_token_obj.choose_product_category and access_token_obj.allow_language_support:
                request_io_objs = request_io_objs.filter(product_category__in=cobrowse_agent.product_category.all(),
                                                         supported_language__in=cobrowse_agent.supported_language.all())
            elif access_token_obj.choose_product_category:
                request_io_objs = request_io_objs.filter(
                    product_category__in=cobrowse_agent.product_category.all())
            elif access_token_obj.allow_language_support:
                request_io_objs = request_io_objs.filter(
                    supported_language__in=cobrowse_agent.supported_language.all())
            
            total_request_objs = len(request_io_objs)
            page_number = int(data["page_number"])
            total_request_io_objs, paginate_request_ios, start_point, end_point = paginate(
                request_io_objs, QUEUE_LEADS_COUNT, page_number)

            cobrowse_request_lead_details = parse_request_io_data(
                paginate_request_ios, cobrowse_agent)

            response["status"] = 200
            response["message"] = "success"
            response["cobrowse_request_lead_details"] = cobrowse_request_lead_details
            response['pagination_data'] = get_pagination_data(
                paginate_request_ios)
            response["total_request_io"] = total_request_objs
            response["start"] = start_point
            response["end"] = end_point

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAllActiveQueueStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAllActiveQueueStatus = GetAllActiveQueueStatusAPI.as_view()


class AssignAgentCobrowsingLeadAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            agent_id = strip_html_tags(data["agent_id"])
            cobrowse_agent = get_active_agent_obj(request, CobrowseAgent)

            if cobrowse_agent.role in ["supervisor", "admin_ally"]:
                cobrowse_io_obj = CobrowseIO.objects.get(session_id=session_id)

                if cobrowse_io_obj.agent:
                    response["status"] = 307
                    response["message"] = "Lead has been already assigned to " + \
                        str(cobrowse_io_obj.agent.user.username) + "."
                else:
                    assign_agent = CobrowseAgent.objects.filter(
                        pk=int(agent_id)).first()

                    if cobrowse_io_obj.access_token.maximum_active_leads:
                        agent_active_leads = CobrowseIO.objects.filter(agent=assign_agent, is_archived=False).count()
                        if agent_active_leads >= cobrowse_io_obj.access_token.maximum_active_leads_threshold:    
                            response["status"] = 501
                            response["message"] = str(assign_agent.user.username) + \
                                " has reached maximum lead capacity. Please try again later. "
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)
                    if assign_agent and assign_agent.is_active == True:
                        if cobrowse_io_obj.cobrowsing_start_datetime == None and cobrowse_io_obj.is_agent_request_for_cobrowsing == False and cobrowse_io_obj.is_archived == False:
                            agent_active_leads = CobrowseIO.objects.filter(
                                agent=assign_agent, is_archived=False).count()
                            cobrowse_io_obj.agent = assign_agent
                            if cobrowse_io_obj.access_token.show_verification_code_modal == False:
                                cobrowse_io_obj.allow_agent_cobrowse = "true"
                            cobrowse_io_obj.save()

                            product_name = get_product_name()

                            create_notification_objects(
                                assign_agent, cobrowse_io_obj, product_name, NotificationManagement)

                            send_notification_to_agent(
                                assign_agent, NotificationManagement)

                            category = "session_assign"
                            description = str(cobrowse_agent.user.username) + " assigned the session from " + \
                                str(cobrowse_agent.user.username) + \
                                " to " + str(assign_agent.user.username)
                            save_system_audit_trail(category, description, cobrowse_io_obj,
                                                    cobrowse_io_obj.access_token, SystemAuditTrail, cobrowse_agent)

                            response["status"] = 200
                            response["message"] = "Lead has been successfully assigned to " + \
                                assign_agent.user.username
                        else:
                            if cobrowse_io_obj.is_archived:
                                response["status"] = 304
                                response["message"] = "Session cannot be assigned because the session \
                                    has already been archived."
                            else:
                                response["status"] = 303
                                response["message"] = "Session cannot be assigned to " + \
                                    str(assign_agent.user.username) + " because " + str(cobrowse_agent.user.username) + \
                                    " has already joined the session"
                    else:
                        response["status"] = 302
                        if not assign_agent:
                            response["message"] = "Invalid Agent"
                        else:
                            response["message"] = "Agent " + \
                                str(assign_agent.user.username) + " is offline"
            else:
                response["status"] = 401

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AssignAgentCobrowsingLeadAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AssignAgentCobrowsingLead = AssignAgentCobrowsingLeadAPI.as_view()


class GetAllActiveLeadCountAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            user = request.user
            cobrowse_agent = CobrowseAgent.objects.get(
                user=user, is_account_active=True)
            access_token_obj = cobrowse_agent.get_access_token_obj()
            if cobrowse_agent.role in ["admin", "admin_ally"]:
                agents = get_list_agents_under_admin(cobrowse_agent, None)
            elif cobrowse_agent.role == "supervisor":
                agents = get_list_agents_under_admin(cobrowse_agent, None)
            else:
                agents = [cobrowse_agent]

            if access_token_obj.enable_request_in_queue:
                request_io_objs = CobrowseIO.objects.filter(is_active=True, access_token=access_token_obj,
                                                            is_archived=False, agent=None, is_lead=False, is_reverse_cobrowsing=False)

                if access_token_obj.choose_product_category and access_token_obj.allow_language_support:
                    request_io_objs = request_io_objs.filter(product_category__in=cobrowse_agent.product_category.all(),
                                                             supported_language__in=cobrowse_agent.supported_language.all())
                elif access_token_obj.choose_product_category:
                    request_io_objs = request_io_objs.filter(
                        product_category__in=cobrowse_agent.product_category.all())
                elif access_token_obj.allow_language_support:
                    request_io_objs = request_io_objs.filter(
                        supported_language__in=cobrowse_agent.supported_language.all())

                response["total_active_requests_in_queue"] = request_io_objs.count()

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_archived=False, agent__in=agents)
            if access_token_obj.enable_invite_agent_in_cobrowsing or access_token_obj.enable_invite_agent_in_meeting:
                cobrowse_io_support_objs = CobrowseIO.objects.filter(
                    is_archived=False, support_agents__in=agents)
                cobrowse_io_objs = cobrowse_io_objs | cobrowse_io_support_objs
            if access_token_obj.enable_session_transfer_in_cobrowsing:
                transfer_io = CobrowseIOTransferredAgentsLogs.objects.filter(
                    transferred_agent__in=agents, cobrowse_request_type="transferred", transferred_status="").values_list("cobrowse_io").order_by("-log_request_datetime")
                if transfer_io:
                    cobrowse_io_transfer_objs = CobrowseIO.objects.filter(
                        is_archived=False, session_id__in=transfer_io)
                    cobrowse_io_objs = cobrowse_io_objs | cobrowse_io_transfer_objs

            cobrowse_io_objs = cobrowse_io_objs.distinct()
            response["status"] = 200
            response["message"] = "success"
            response["total_active_leads"] = cobrowse_io_objs.count()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAllActiveLeadCountAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAllActiveLeadCount = GetAllActiveLeadCountAPI.as_view()


class SaveCognoMeetAccessTokenAPI(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cogno_meet_access_token = sanitize_input_string(data["cogno_meet_access_token"])
            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()
            if not access_token_obj.cogno_meet_access_token:
                access_token_obj.cogno_meet_access_token = cogno_meet_access_token
                access_token_obj.save()
            
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCognoMeetAccessTokenAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCognoMeetAccessToken = SaveCognoMeetAccessTokenAPI.as_view()


class UpdateActiveAgentsDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = 500
        response["status_message"] = "Internal server error."
        custom_encrypt_obj = CustomEncrypt()
        try:
            requested_agent = None
            requested_agent_firstname = ""
            cobrowse_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = cobrowse_agent.get_access_token_obj()

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            agent_pk = sanitize_input_string(str(data["agent_pk"]))

            if agent_pk:
                agent_pk = int(agent_pk)
                requested_agent = CobrowseAgent.objects.filter(
                    pk=agent_pk).first()
                requested_agent_firstname = requested_agent.user.first_name.capitalize()
                agents = requested_agent.agents.filter(role="agent")
            else:
                agents = cobrowse_agent.agents.filter(role="agent")

            applied_filter = sanitize_input_string(data["applied_filter"])
            if not requested_agent:
                if cobrowse_agent.role == "admin":
                    supervisors = cobrowse_agent.agents.filter(
                        role="supervisor")
                    admin_allies = cobrowse_agent.agents.filter(
                        role="admin_ally")

                    for admin_ally in admin_allies:
                        ally_supervisors = admin_ally.agents.filter(
                            role="supervisor")
                        supervisors = supervisors | ally_supervisors

                    for supervisor in supervisors:
                        agents = agents | supervisor.agents.all()
                elif cobrowse_agent.role == "admin_ally":
                    supervisors = cobrowse_agent.agents.filter(
                        role="supervisor")
                    for supervisor in supervisors:
                        agents = agents | supervisor.agents.all()
            else:
                if requested_agent.role == "admin_ally":
                    supervisors = cobrowse_agent.agents.filter(role="supervisor")
                    for supervisor in supervisors:
                        agents |= supervisor.agents.filter(role="agent")
            
            agents = agents.distinct()
            total_agent_count = agents.count()
            online_agent_count = agents.filter(is_active=True).count()
            offline_agent_count = total_agent_count - online_agent_count
            active_agent_account_count = agents.filter(
                is_account_active=True).count()
            available_agents_count = agents.filter(
                is_active=True, is_cobrowsing_active=False, is_cognomeet_active=False).count()
            inactive_agent_account_count = total_agent_count - active_agent_account_count
            busy_agents_count = online_agent_count - available_agents_count

            filter_online = False
            filter_offline = False
            filter_active_account = False
            filter_deactivated_account = False
            filter_available_agent = False
            filter_busy_agent = False

            if applied_filter:
                if applied_filter == "online":
                    agents = agents.filter(is_active=True)
                    filter_online = True
                elif applied_filter == "offline":
                    filter_offline = True
                    agents = agents.filter(is_active=False)
                elif applied_filter == "active":
                    agents = agents.filter(is_account_active=True)
                    filter_active_account = True
                elif applied_filter == "inactive":
                    filter_deactivated_account = True
                    agents = agents.filter(is_account_active=False)
                elif applied_filter == "available":
                    filter_available_agent = True
                    agents = agents.filter(
                        is_active=True, is_cobrowsing_active=False, is_cognomeet_active=False)
                elif applied_filter == "busy":
                    filter_busy_agent = True
                    agents = agents.filter(is_active=True).filter(
                        Q(is_cobrowsing_active=True) | Q(is_cognomeet_active=True))

            agents = agents.order_by('-agent_creation_datetime')

            response["status_code"] = 200
            response["status_message"] = "success"
            response["total_agent_count"] = total_agent_count
            response["online_agent_count"] = online_agent_count
            response["offline_agent_count"] = offline_agent_count
            response["active_agent_account_count"] = active_agent_account_count
            response["available_agents_count"] = available_agents_count
            response["inactive_agent_account_count"] = inactive_agent_account_count
            response["busy_agents_count"] = busy_agents_count
            response["filter_online"] = filter_online
            response["filter_offline"] = filter_offline
            response["filter_active_account"] = filter_active_account
            response["filter_deactivated_account"] = filter_deactivated_account
            response["filter_busy_agent"] = filter_busy_agent
            response["filter_available_agent"] = filter_available_agent
            response["requested_agent_firstname"] = requested_agent_firstname
            response["cobrowse_agent_details"] = parse_cobrowse_agent_details(
                agents, access_token_obj)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateActiveAgentsDetailsAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


UpdateActiveAgentsDetails = UpdateActiveAgentsDetailsAPI.as_view()


class ToggleAgentStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status_code'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = get_active_agent_obj(request, CobrowseAgent)
            if active_agent.role in ["admin", "supervisor"]:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)
                agent_pk = sanitize_input_string(str(data["agent_pk"]))
                agent_pk = int(agent_pk)
                status = data["active_status"]
                cobrowse_agent = CobrowseAgent.objects.filter(
                    pk=agent_pk, role="agent", is_account_active=True).first()
                
                if cobrowse_agent:
                    if not check_user_online_status(cobrowse_agent, UserSession, Session, SecuredLogin, CobrowsingAuditTrail):
                        response["status_code"] = 302
                        response["status_message"] = "Seems like agent " + cobrowse_agent.user.first_name + \
                            " has logged out of their console"
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                    if cobrowse_agent.is_cobrowsing_active or cobrowse_agent.is_cognomeet_active:
                        response["status_code"] = 302
                        response["status_message"] = "Agent " + \
                            cobrowse_agent.user.first_name + " is already inside a session"
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                    change_agent_is_active_flag(
                        status, cobrowse_agent, CobrowseAgentOnlineAuditTrail, CobrowseAgentWorkAuditTrail)

                    active_agent_toast_message = ""
                    cobrowse_agent_toast_message = ""

                    if cobrowse_agent.is_active == status:
                        if status:
                            active_agent_toast_message = "Agent " + \
                                cobrowse_agent.user.first_name + " has been marked online"
                            cobrowse_agent_toast_message = active_agent.role.capitalize(
                            ) + " " + active_agent.user.first_name + " has marked you online"
                        else:
                            active_agent_toast_message = "Agent " + \
                                cobrowse_agent.user.first_name + " has been marked offline"
                            cobrowse_agent_toast_message = active_agent.role.capitalize(
                            ) + " " + active_agent.user.first_name + " has marked you offline"

                        send_data_from_server_to_client(
                            "agent_status_change_message", cobrowse_agent_toast_message, cobrowse_agent.user)

                        response["status_code"] = 200
                        response["status_message"] = active_agent_toast_message
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ToggleAgentStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            
        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


ToggleAgentStatus = ToggleAgentStatusAPI.as_view()
