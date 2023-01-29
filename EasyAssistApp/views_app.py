from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.encoding import smart_str


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
"""For user authentication"""
from django.contrib.auth import authenticate, login, logout

from EasyChatApp.models import User, UserSession
from rest_framework.authtoken.models import Token

from EasyAssistApp.models import *
from EasyAssistApp.utils import *

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

from operator import itemgetter
from collections import OrderedDict

logger = logging.getLogger(__name__)


def SalesAIAppDashboard(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/easy-assist/sales-ai/login/")

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)

        if cobrowse_agent.role != "admin":
            return HttpResponse(status=401)

        agents = get_list_agents_under_admin(cobrowse_agent, is_active=False)

        cobrowse_io_objs = CobrowseIO.objects.filter(is_archived=False,
                                                     is_active=True,
                                                     share_client_session=True,
                                                     agent__in=agents).order_by("-request_datetime")

        return render(request, "EasyAssistApp/sales_app_dashboard.html", {
            "cobrowse_io_objs": cobrowse_io_objs, "cobrowse_agent": cobrowse_agent
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAIAppDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(status=401)


def CobrowseIOClientPage(request, session_id):
    try:
        
        client_session_token = None
        if "cs_token" in request.COOKIES:
            client_session_token = request.COOKIES["cs_token"]

        cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

        if cobrowse_io.access_token.enable_app_type == "customer":
            return redirect("/easy-assist/app/" + session_id)
        
        utm_source = request.GET["utm"]
        client_ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        client_user_agent = request.META.get('HTTP_USER_AGENT')

        if cobrowse_io.is_archived:
            response = redirect("/easy-assist/session-closed/")
            if client_session_token != None:
                response.delete_cookie("cs_token")
            return response

        elif cobrowse_io.allow_agent_cobrowse != "true":
            response = HttpResponse(
                "You are not allowed to access this page. Please contact system administrator if case problem continues.")
            if client_session_token != None:
                response.delete_cookie("cs_token")
            return response

        try:
            AppCobrowsingSessionManagement.objects.get(cobrowse_io=cobrowse_io,
                                                       user_token=client_session_token,
                                                       user_type=utm_source)
            logger.info("Connected with right session",
                        extra={'AppName': 'EasyAssist'})
        except Exception:
            logger.info("Requested for different session",
                        extra={'AppName': 'EasyAssist'})
            client_session_token = None

        cobrowse_access_token = cobrowse_io.access_token
        capping_max_connections = cobrowse_access_token.app_capping_max_connections
        
        if utm_source == "client" and client_user_agent.lower().find("whatsapp") == -1:
            client_app_cobrowsing_session_objs = AppCobrowsingSessionManagement.objects.filter(cobrowse_io=cobrowse_io,
                                                                                               user_type="client")

            active_client_app_cobrowsing_session_objs = client_app_cobrowsing_session_objs.filter(
                is_closed=False)

            if "close_session" in request.GET and request.GET["close_session"] == "true":
                if client_session_token != None:
                    active_client_app_cobrowsing_session_obj = AppCobrowsingSessionManagement.objects.get(
                        user_token=client_session_token)
                    active_client_app_cobrowsing_session_obj.is_closed = True
                    active_client_app_cobrowsing_session_obj.save()

                response = HttpResponse(
                    "Co-browsing session has been closed. Please close this tab for security reasons.")

                if client_session_token != None:
                    response.delete_cookie("cs_token")
                return response
            
            count_active_client_app_cobrowsing_sessions = active_client_app_cobrowsing_session_objs.count()

            if capping_max_connections == False:
                if client_session_token == None:
                    client_session_token = create_app_cobrowsing_session(
                        cobrowse_io, "client", AppCobrowsingSessionManagement).user_token

            elif count_active_client_app_cobrowsing_sessions != 0:
                if client_session_token != active_client_app_cobrowsing_session_objs[0].user_token:
                    session_validation_url = "/easy-assist/session-validation/?session=" + \
                        session_id + "&utm=" + utm_source
                    return redirect(session_validation_url)
            else:
                user_type = "client"
                client_session_token = create_app_cobrowsing_session(
                    cobrowse_io, user_type, AppCobrowsingSessionManagement).user_token

        elif utm_source == "expert" and client_user_agent.lower().find("whatsapp") == -1:
            expert_app_cobrowsing_session_objs = AppCobrowsingSessionManagement.objects.filter(cobrowse_io=cobrowse_io,
                                                                                               user_type="expert")

            active_expert_app_cobrowsing_session_objs = expert_app_cobrowsing_session_objs.filter(
                is_closed=False)

            if capping_max_connections == False:
                if client_session_token == None:
                    client_session_token = create_app_cobrowsing_session(
                        cobrowse_io, "expert", AppCobrowsingSessionManagement).user_token
            
            elif active_expert_app_cobrowsing_session_objs.count() != 0:
                active_user_token_list = list(
                    active_expert_app_cobrowsing_session_objs.values_list("user_token", flat=True))

                if client_session_token not in active_user_token_list:
                    if len(active_user_token_list) >= 2:
                        return redirect("/easy-assist/session-validation/expert/?session=" + session_id + "&utm=" + utm_source)
                    else:
                        client_session_token = create_app_cobrowsing_session(
                            cobrowse_io, "expert", AppCobrowsingSessionManagement).user_token
            else:
                client_session_token = create_app_cobrowsing_session(
                    cobrowse_io, "expert", AppCobrowsingSessionManagement).user_token

        app_cobrowsing_session_obj = None
        try:
            app_cobrowsing_session_obj = AppCobrowsingSessionManagement.objects.get(cobrowse_io=cobrowse_io,
                                                                                    user_token=client_session_token)
        except Exception:
            pass
        """
        
        if cobrowse_io.access_token.enable_app_video_conferencing_dialog:
            
            if meeting_joining_cookie == None or meeting_joining_cookie != session_id:
                
                return redirect("/easy-assist/app/meeting-lobby/" + session_id)
        """

        floating_button_bg_color = cobrowse_io.access_token.floating_button_bg_color
        
        agent_name = None
        if cobrowse_io.agent != None:
            agent_name = str(cobrowse_io.agent.user.first_name)
            if agent_name.strip() == "" or agent_name == "None":
                agent_name = str(cobrowse_io.agent.user.username)

        response = render(request, "EasyAssistApp/cobrowse_client.html", {
            "session_id": session_id,
            "cobrowse_io": cobrowse_io,
            "utm_source": utm_source,
            "client_ip_address": client_ip_address,
            "app_cobrowsing_session_obj": app_cobrowsing_session_obj,
            "floating_button_bg_color": floating_button_bg_color,
            "is_mobile": request.user_agent.is_mobile,
            "access_token": cobrowse_io.access_token.key,
            "agent_name": agent_name
        })

        response.set_cookie("cs_token", client_session_token)

        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowseIOClientPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


def CobrowsingAppSessionValidation(request):
    try:
        client_ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        session_id = request.GET["session"]
        cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            
        if cobrowse_io.is_archived:
            return redirect("/easy-assist/session-closed/")
        elif cobrowse_io.allow_agent_cobrowse != "true":
            return HttpResponse("You are not allowed to access this page. Please contact system administrator if case problem continues.")

        client_app_cobrowsing_session_objs = AppCobrowsingSessionManagement.objects.filter(cobrowse_io=cobrowse_io,
                                                                                           user_type="client",
                                                                                           is_closed=False)

        for client_app_cobrowsing_session_obj in client_app_cobrowsing_session_objs:

            last_update_datetime = client_app_cobrowsing_session_obj.last_update_datetime

            total_sec = (timezone.now() - last_update_datetime).total_seconds()

            if total_sec >= 20:
                client_app_cobrowsing_session_obj.is_closed = True
                client_app_cobrowsing_session_obj.save()

        client_app_cobrowsing_session_objs = AppCobrowsingSessionManagement.objects.filter(cobrowse_io=cobrowse_io,
                                                                                           user_type="client",
                                                                                           is_closed=False)

        if client_app_cobrowsing_session_objs.count() == 0:
            redirect_url = "/easy-assist/customer/" + session_id + "?utm=client"
            return redirect(redirect_url)

        return render(request, "EasyAssistApp/session_validation_customer.html", {
            "session_id": session_id,
            "client_ip_address": client_ip_address
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowsingAppSessionValidation %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


def CobrowsingAppSessionValidationExpert(request):
    try:
        if request.method == "GET":
            session_id = request.GET["session"]
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            if cobrowse_io.is_archived:
                return redirect("/easy-assist/session-closed/")
            elif cobrowse_io.allow_agent_cobrowse != "true":
                return HttpResponse("You are not allowed to access this page. Please contact system administrator if case problem continues.")

            expert_app_cobrowsing_session_objs = AppCobrowsingSessionManagement.objects.filter(cobrowse_io=cobrowse_io,
                                                                                               user_type="expert",
                                                                                               is_closed=False)

            for expert_app_cobrowsing_session_obj in expert_app_cobrowsing_session_objs:
                last_update_datetime = expert_app_cobrowsing_session_obj.last_update_datetime

                total_sec = (timezone.now() -
                             last_update_datetime).total_seconds()

                if total_sec >= 20:
                    expert_app_cobrowsing_session_obj.is_closed = True
                    expert_app_cobrowsing_session_obj.save()

            expert_app_cobrowsing_session_objs = AppCobrowsingSessionManagement.objects.filter(cobrowse_io=cobrowse_io,
                                                                                               user_type="expert",
                                                                                               is_closed=False)

            if expert_app_cobrowsing_session_objs.count() < 2:
                redirect_url = "/easy-assist/customer/" + session_id + "?utm=expert"
                return redirect(redirect_url)

            return render(request, "EasyAssistApp/session_validation_expert.html", {})
        else:
            return HttpResponse(status=405)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowsingAppSessionValidationExpert %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


def CobrowsingAppSessionAccessDenied(request):
    try:
        if request.method == "GET":
            return render(request, "EasyAssistApp/access_denied.html", {})
        else:
            return HttpResponse(status=405)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowsingAppSessionAccessDenied %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


def CobrowsingAppSessionEnded(request):
    try:
        if request.method == "GET":
            return render(request, "EasyAssistApp/closed_session.html", {})
        else:
            return HttpResponse(status=405)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowsingAppSessionEnded %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


def CobrowsingAppMeetingLobby(request, session_id):
    try:
        meeting_joining_cookie = None
        if "eac_meeting_allowed" in request.COOKIES:
            meeting_joining_cookie = request.COOKIES["eac_meeting_allowed"]

        if request.method == "GET":

            if meeting_joining_cookie == session_id:
                return redirect("/easy-assist/customer/" + session_id)

            return render(request, "EasyAssistApp/join_app_meeting.html", {
                "session_id": session_id
            })
        else:
            return HttpResponse(status=405)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowsingAppMeetingLobby %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


def CobrowsingAppAgentPage(request, session_id):
    try:
        if request.method == "GET":
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            if cobrowse_io.is_archived:
                return redirect("/easy-assist/session-closed/")
            
            elif cobrowse_io.allow_agent_cobrowse != "true":
                return HttpResponse("You are not allowed to access this page. Please contact system administrator if case problem continues.")

            if cobrowse_io.cobrowsing_start_datetime == None:
                cobrowse_io.cobrowsing_start_datetime = timezone.now()
                cobrowse_io.save()

            predefined_remarks = cobrowse_io.access_token.predefined_remarks
            try:
                predefined_remarks = json.loads(predefined_remarks)
            except Exception:
                predefined_remarks = []
            
            floating_button_bg_color = cobrowse_io.access_token.floating_button_bg_color

            agent_joined_first_time = True
            if cobrowse_io.last_agent_update_datetime != None:
                agent_joined_first_time = False

            agent_name = None
            agent_name = str(cobrowse_io.agent.user.first_name)
            if agent_name.strip() == "" or agent_name == "None":
                agent_name = str(cobrowse_io.agent.user.username)
            
            return render(request, "EasyAssistApp/cobrowse_agent_app.html", {
                "session_id": session_id,
                "cobrowse_io": cobrowse_io,
                "utm_source": "agent",
                "predefined_remarks": predefined_remarks,
                "floating_button_bg_color": floating_button_bg_color,
                "is_mobile": request.user_agent.is_mobile,
                "agent_joined_first_time": agent_joined_first_time,
                "enable_agent_connect_message": cobrowse_io.access_token.enable_agent_connect_message,
                "agent_connect_message": cobrowse_io.access_token.agent_connect_message,
                "agent_name": agent_name
            })
        else:
            return HttpResponse(status=405)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowsingAppAgentPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


class AppClientAuthenticationAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            key = data["key"]

            cobrowse_access_token = CobrowseAccessToken.objects.get(key=key)

            if cobrowse_access_token.enable_app_cobrowsing and cobrowse_access_token.is_active:

                response[
                    "easyassist_host_protocol"] = settings.EASYASSIST_HOST_PROTOCOL
                response["easyassist_host"] = settings.EASYASSISTAPP_HOST
                response["allow_cobrowsing"] = False
                response[
                    "show_floating_easyassist_button"] = cobrowse_access_token.show_floating_easyassist_button
                response[
                    "field_stuck_event_handler"] = cobrowse_access_token.field_stuck_event_handler
                response[
                    "field_recursive_stuck_event_check"] = cobrowse_access_token.field_recursive_stuck_event_check
                response[
                    "get_sharable_link"] = cobrowse_access_token.get_sharable_link
                response["enable_app_search_lead"] = cobrowse_access_token.enable_app_type_search_lead
                response[
                    "field_stuck_timer"] = cobrowse_access_token.field_stuck_timer
                response["toast_timeout"] = 4000
                response["browser_tab_switch_timer"] = 120000

                response["proxy_server"] = ""
                if cobrowse_access_token.proxy_server != None and cobrowse_access_token.proxy_server != "":
                    response["proxy_server"] = cobrowse_access_token.proxy_server

                response["assist_message"] = cobrowse_access_token.assist_message
                response[
                    "floating_button_position"] = cobrowse_access_token.floating_button_position
                response[
                    "floating_button_bg_color"] = cobrowse_access_token.floating_button_bg_color
                response["strip_js"] = cobrowse_access_token.strip_js
                response["is_socket"] = cobrowse_access_token.is_socket
                response["access_token"] = str(cobrowse_access_token.key)
                response[
                    "bitmap_compress_ratio"] = cobrowse_access_token.bitmap_compress_ratio
                response[
                    "app_inactivity_timer"] = cobrowse_access_token.app_inactivity_timer
                response[
                    "app_close_session_timer"] = cobrowse_access_token.app_close_session_timer

                response["client_logo"] = None
                try:
                    response["client_logo"] = settings.EASYCHAT_HOST_URL + \
                        cobrowse_access_token.app_client_logo.url
                except Exception:
                    pass

                response["cobrowse_logo"] = None
                try:
                    response["cobrowse_logo"] = settings.EASYCHAT_HOST_URL + \
                        cobrowse_access_token.app_cobrowse_logo.url
                except Exception:
                    pass

                response["blocked_html_tags"] = list(
                    cobrowse_access_token.blacklisted_tags.values_list('tag', flat=True))

                response["search_html_field"] = {

                }

                for search_field in cobrowse_access_token.search_fields.all():

                    if search_field.tag not in response["search_html_field"]:
                        response["search_html_field"][search_field.tag] = []

                    response["search_html_field"][search_field.tag].append({
                        "name": search_field.tag_name,
                        "label": search_field.tag_label,
                        "id": search_field.tag_id,
                        "data-reactid": search_field.tag_reactid,
                        "type": search_field.tag_type
                    })

                response["obfuscated_fields"] = []
                for obfuscated_field in cobrowse_access_token.obfuscated_fields.all():
                    response["obfuscated_fields"].append({
                        "key": obfuscated_field.key,
                        "value": obfuscated_field.value
                    })

                if User.objects.filter(username=cobrowse_access_token.client_id).count() == 0:
                    User.objects.create(username=cobrowse_access_token.client_id,
                                        password=cobrowse_access_token.client_key)

                response["client_id"] = cobrowse_access_token.client_id
                response["client_key"] = cobrowse_access_token.client_key
                response[
                    "allow_public_document_sharing"] = cobrowse_access_token.app_allow_public_document_sharing
                response[
                    "link_sharing_dialog"] = cobrowse_access_token.enable_app_link_sharing
                response[
                    "chat_dialog"] = cobrowse_access_token.enable_app_chat_dialog
                response[
                    "video_kyc_dialog"] = cobrowse_access_token.enable_app_video_kyc_dialog
                response[
                    "photo_kyc_dialog"] = cobrowse_access_token.enable_app_photo_kyc_dialog
                response["video_conferencing_dialog"] = False
                response[
                    "screen_share_dialog"] = cobrowse_access_token.enable_app_screen_share_dialog
                response["video_conferencing_link"] = "None"
                response[
                    "in_app_video_conferencing_dialog"] = cobrowse_access_token.enable_app_video_conferencing_dialog
                response[
                    "in_app_meet_domain"] = "https://" + cobrowse_access_token.meeting_host_url
                response["call_customer_dialog"] = cobrowse_access_token.enable_app_audio_call_dialog
                response["enable_app_youtube_player"] = cobrowse_access_token.enable_app_youtube_player
                response["request_edit_access_dialog"] = False
                response["enable_app_type"] = cobrowse_access_token.enable_app_type
                response[
                    "app_client_share_link_message"] = cobrowse_access_token.app_client_share_link_message
                response[
                    "app_expert_share_link_message"] = cobrowse_access_token.app_expert_share_link_message
                response[
                    "show_only_if_agent_available"] = cobrowse_access_token.show_only_if_agent_available
                response[
                    "message_if_agent_unavailable"] = cobrowse_access_token.message_if_agent_unavailable
                response[
                    "enable_non_working_hours_modal_popup"] = cobrowse_access_token.enable_non_working_hours_modal_popup
                
                non_working_hours_message = cobrowse_access_token.message_on_non_working_hours

                if len(non_working_hours_message) == 0:
                    non_working_hours_message = NON_WORKING_HOURS_MESSAGE

                response[
                    "message_on_non_working_hours"] = non_working_hours_message
                
                response["enable_followup_leads"] = cobrowse_access_token.enable_followup_leads_tab
                response["no_agent_connects_toast"] = cobrowse_access_token.no_agent_connects_toast
                response["no_agent_connects_toast_text"] = cobrowse_access_token.no_agent_connects_toast_text
                response["no_agent_connects_toast_threshold"] = cobrowse_access_token.no_agent_connects_toast_threshold
                response["archive_message_on_unassigned_time_threshold"] = cobrowse_access_token.archive_message_on_unassigned_time_threshold

                auto_response = ""
                cobrowse_admin = cobrowse_access_token.agent
                cobrowse_calendar_obj = CobrowseCalendar.objects.filter(created_by=cobrowse_admin, event_date__date=str(datetime.datetime.now().date()), event_type="1")
                if cobrowse_calendar_obj.exists():
                    cobrowse_calendar_obj = cobrowse_calendar_obj[0]
                    response["is_working_day"] = True
                    response["start_time"] = str(cobrowse_calendar_obj.start_time)[0:5]
                    response["end_time"] = str(cobrowse_calendar_obj.end_time)[0:5]
                    auto_response = cobrowse_calendar_obj.auto_response
                else:
                    response["is_working_day"] = False
                    cobrowse_calendar_obj = CobrowseCalendar.objects.filter(created_by=cobrowse_admin, event_date__date=str(datetime.datetime.now().date()), event_type="2")
                    if cobrowse_calendar_obj.exists():
                        cobrowse_calendar_obj = cobrowse_calendar_obj[0]
                        auto_response = cobrowse_calendar_obj.auto_response
                if len(auto_response) == 0:
                    response["auto_response"] = non_working_hours_message
                else:
                    response["auto_response"] = auto_response

                response["otp_dialog_required"] = cobrowse_access_token.enable_verification_code_popup
                response["enable_app_field_masking"] = cobrowse_access_token.enable_app_field_masking
                response["enable_app_quick_access_tray"] = cobrowse_access_token.enable_app_quick_access_tray
                response["enable_app_screen_border"] = cobrowse_access_token.enable_app_screen_border
                response["enable_app_system_file_picker"] = cobrowse_access_token.enable_app_system_file_picker
                response["enable_predefined_remarks"] = cobrowse_access_token.enable_predefined_remarks
                response["predefined_remarks"] = json.loads(cobrowse_access_token.predefined_remarks)
                response["enable_predefined_subremarks"] = cobrowse_access_token.enable_predefined_subremarks
                response["are_remarks_optional"] = cobrowse_access_token.predefined_remarks_optional
                response["enable_agent_connect_message"] = cobrowse_access_token.enable_agent_connect_message
                
                masked_fields = AppCobrowseMaskedFields.objects.filter(cobrowse_access_token=cobrowse_access_token)
                
                if len(masked_fields) != 0:
                    app_masking_field_names = {}
                    for masked_field in masked_fields:
                        ids_list = masked_field.ids.split(',')
                        app_masking_field_names[masked_field.activity_name] = ids_list
                    response["app_masking_field_names"] = json.dumps(app_masking_field_names)
                
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AppClientAuthenticationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppClientAuthentication = AppClientAuthenticationAPI.as_view()


class CobrowseAppCreateSessionAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            if cobrowse_access_token_obj == None:
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                name = data["name"]
                mobile_number = data["mobile_number"]
                meta_data = data["meta_data"]
                app_channel = data["channel"]

                if cobrowse_access_token_obj.enable_app_type == "customer" and \
                        cobrowse_access_token_obj.enable_app_type_search_lead:
                    
                    easyassist_sync_data = []
                    easyassist_sync_data.append({
                        "value": name,
                        "sync_type": "primary",
                        "name": "Name"
                    })
                    easyassist_sync_data.append({
                        "value": mobile_number,
                        "sync_type": "primary",
                        "name": "Phone"
                    })
                    meta_data["easyassist_sync_data"] = easyassist_sync_data
                
                admin_agent = cobrowse_access_token_obj.agent

                agent_obj = None
                if "agent_code" in data and data["agent_code"] != "None":
                    try:
                        agent_obj = CobrowseAgent.objects.get(
                            agent_code=data["agent_code"])
                    except Exception:
                        new_user = User.objects.create(
                            username=data["agent_code"], password=str(uuid.uuid4()))
                        agent_obj = CobrowseAgent.objects.create(
                            user=new_user, agent_code=data["agent_code"], role="agent", access_token=cobrowse_access_token_obj)
                        admin_agent.agents.add(agent_obj)
                        admin_agent.save()
                        logger.info("New agent has been created: %s",
                                    data["agent_code"], extra={'AppName': 'EasyAssist'})

                share_client_session = True

                cobrowse_io = CobrowseIO.objects.create(full_name=name,
                                                        mobile_number=mobile_number,
                                                        share_client_session=share_client_session,
                                                        app_channel=app_channel)
                cobrowse_io.is_app_cobrowse_session = True
                if "product_details" in meta_data and "title" in meta_data["product_details"]:
                    cobrowse_io.title = meta_data[
                        "product_details"]["title"].strip()

                if "product_details" in meta_data and "url" in meta_data["product_details"]:
                    cobrowse_io.active_url = meta_data[
                        "product_details"]["url"].strip()

                meta_data = json.dumps(meta_data)
                meta_data = custom_encrypt_obj.encrypt(meta_data)
                cobrowse_io.meta_data = meta_data
                
                if cobrowse_access_token_obj.enable_app_type == "agent":
                    cobrowse_io.is_active = True
                    cobrowse_io.last_update_datetime = timezone.now()
                    cobrowse_io.cobrowsing_start_datetime = timezone.now()
                    cobrowse_io.last_agent_update_datetime = timezone.now()
                    cobrowse_io.is_agent_connected = False
                    cobrowse_io.allow_agent_cobrowse = "true"
                    cobrowse_io.is_lead = False
                    cobrowse_io.access_token = cobrowse_access_token_obj
                    cobrowse_io.agent = agent_obj
                else:
                    if cobrowse_access_token_obj.enable_app_type_search_lead:
                        primary_id = mobile_number.strip().lower()
                        primary_id = hashlib.md5(
                            primary_id.encode()).hexdigest()

                        cobrowse_io.is_active = True
                        cobrowse_io.primary_value = primary_id
                        cobrowse_io.last_update_datetime = timezone.now()
                        cobrowse_io.cobrowsing_start_datetime = None
                        cobrowse_io.last_agent_update_datetime = None
                        cobrowse_io.is_agent_connected = False
                        cobrowse_io.is_lead = True
                        cobrowse_io.access_token = cobrowse_access_token_obj
                        cobrowse_io.agent = None
                    else:
                        cobrowse_io.is_active = True
                        cobrowse_io.last_update_datetime = timezone.now()
                        cobrowse_io.is_agent_connected = False
                        cobrowse_io.cobrowsing_start_datetime = None
                        cobrowse_io.is_lead = False
                        cobrowse_io.access_token = cobrowse_access_token_obj
                        cobrowse_io.allow_agent_cobrowse = "true"
                        cobrowse_io.agent = None

                cobrowse_io.save()

                if cobrowse_io.is_lead:

                    captured_lead_obj = {
                        "value": mobile_number,
                        "label": ""
                    }
                    
                    primary_value_list = [captured_lead_obj]

                    check_and_update_lead(
                        primary_value_list, meta_data, cobrowse_io, CobrowseCapturedLeadData)

                response["session_id"] = str(cobrowse_io.session_id)
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseAppCreateSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CobrowseAppCreateSession = CobrowseAppCreateSessionAPI.as_view()


class AppCloseCobrowsingSessionAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            logger.info(data, extra={'AppName': 'EasyAssist'})

            id = strip_html_tags(data["id"])
            comments_received = strip_html_tags(data["comments"])
            remarks_received = strip_html_tags(data["remarks"])
            sub_remarks_received = strip_html_tags(data["sub_remarks"])
            
            is_helpful = data["is_helpful"]

            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            cobrowse_io.is_agent_connected = False
            cobrowse_io.is_closed_session = True
            cobrowse_io.is_archived = True
            cobrowse_io.is_active = False
            cobrowse_io.feedback_rating = is_helpful
            cobrowse_io.is_helpful = is_helpful
            cobrowse_io.last_agent_update_datetime = timezone.now()
            if remarks_received != "" and remarks_received != None:
                cobrowse_io.agent_comments = remarks_received
            else:
                cobrowse_io.agent_comments = comments_received
            cobrowse_io.save()

            if cobrowse_io.agent != None:

                active_agent = cobrowse_io.agent

                if remarks_received != "" and remarks_received != None:
                    comments = remarks_received
                    comments_desc = comments_received
                else:
                    comments = comments_received
                    comments_desc = ""

                save_agent_closing_comments_cobrowseio(
                    cobrowse_io, active_agent, comments, CobrowseAgentComment, comments_desc, sub_remarks_received)

                category = "session_closed"
                description = "Session is archived by " + \
                    str(active_agent.user.username) + \
                    " after submitting comments"

                save_system_audit_trail(
                    category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail)

                if cobrowse_io.session_archived_cause == None:
                    cobrowse_io.session_archived_cause = "AGENT_ENDED"
                    cobrowse_io.session_archived_datetime = timezone.now()
                    cobrowse_io.save()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AppCloseCobrowsingSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppCloseCobrowsingSession = AppCloseCobrowsingSessionAPI.as_view()


class AppAgentUpdateCobrowseIOAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            if cobrowse_access_token_obj == None:
                return Response(status=401)
            else:
                id = data["id"]
                cobrowse_io_obj = CobrowseIO.objects.get(session_id=id)
                cobrowse_io_obj.last_agent_update_datetime = timezone.now()
                cobrowse_io_obj.is_agent_connected = True
                cobrowse_io_obj.save()
                logger.info(data, extra={'AppName': 'EasyAssist'})

                response[
                    "is_client_connected"] = cobrowse_io_obj.is_active and cobrowse_io_obj.is_active_timer()
                response["is_active"] = cobrowse_io_obj.is_active
                response["is_archived"] = cobrowse_io_obj.is_archived

                logger.info(cobrowse_io_obj.is_archived,
                            extra={'AppName': 'EasyAssist'})

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AppAgentUpdateCobrowseIOAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppAgentUpdateCobrowseIO = AppAgentUpdateCobrowseIOAPI.as_view()


# pass the session id in the request packet to get the accesstoken.
# This accesstoken is used while creating of CobrowsingFileAccessManagement obj
class AppSaveDocumentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            filename = strip_html_tags(data["filename"])
            base64_data = strip_html_tags(data["base64_file"])

            is_public = False
            if "is_public" in data and data["is_public"]:
                is_public = True

            filename = generate_random_key(10) + "_" + filename

            if not os.path.exists('files/attachments'):
                os.makedirs('files/attachments')

            file_path = "files/attachments/" + filename

            fh = open(file_path, "wb")
            fh.write(base64.b64decode(base64_data))
            fh.close()

            if get_save_in_s3_bucket_status():
                key = s3_bucket_upload_file_by_file_path(file_path, filename)
                s3_file_path = s3_bucket_download_file(key, 'EasyAssistApp/attachments/', filename.rsplit('.', 1)[1])
                file_path = s3_file_path.split("EasyChat/", 1)[1]

            file_path = "/" + file_path

            file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                file_path=file_path, is_public=is_public)

            response["status"] = 200
            response["message"] = "success"

            if is_public:
                response["file_path"] = file_path
            else:
                response["file_path"] = "/easy-assist/download-file/" + \
                    str(file_access_management_obj.key) + "/"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AppSaveDocumentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppSaveDocument = AppSaveDocumentAPI.as_view()


class AppSaveCobrowsingChatAPI(APIView):

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
            sender = strip_html_tags(data["sender"])
            message = remo_html_from_string(data["message"])
            attachment = strip_html_tags(data["attachment"])

            attachment_file_name = ""
            if "attachment_file_name" in data:
                attachment_file_name = strip_html_tags(data["attachment_file_name"])

            cobrowse_agent = None
            if sender != "client":
                user_obj = User.objects.get(username=sender)
                cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            if attachment == "None":
                attachment = None

            if attachment_file_name == "":
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
            logger.error("Error AppSaveCobrowsingChatAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppSaveCobrowsingChat = AppSaveCobrowsingChatAPI.as_view()


class GetAppCobrowsingChatHistoryAPI(APIView):

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

            cobrowsing_chat_history_objs = cobrowse_io.get_cobrowsing_chat_history()

            chat_history = []
            for cobrowsing_chat_history_obj in cobrowsing_chat_history_objs:

                est = pytz.timezone(settings.TIME_ZONE)
                chat_datetime = cobrowsing_chat_history_obj.datetime.astimezone(
                    est).strftime("%d %b %Y %I:%M %p")

                sender = "client"
                if cobrowsing_chat_history_obj.sender != None:
                    sender = cobrowsing_chat_history_obj.sender.name()

                chat_history.append({
                    "sender": sender,
                    "message": cobrowsing_chat_history_obj.message,
                    "attachment": cobrowsing_chat_history_obj.attachment,
                    "datetime": chat_datetime,
                    "file_name": cobrowsing_chat_history_obj.attachment_file_name
                })

            response["status"] = 200
            response["message"] = "success"
            response["chat_history"] = chat_history
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAppCobrowsingChatHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAppCobrowsingChatHistory = GetAppCobrowsingChatHistoryAPI.as_view()


class GetCobrowsingSupportDocumentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            """
            support_document_objs = cobrowse_admin.get_uploaded_support_documents()

            support_documents = []

            for support_document_obj in support_document_objs:

                cobrowse_file_obj = support_document_obj.cobrowse_file

                file_path = None

                if cobrowse_file_obj.is_public:
                    file_path = cobrowse_file_obj.file_path
                else:
                    file_path = "/easy-assist/download-file/" + str(cobrowse_file_obj.key) + "/"

                support_documents.append({
                                    "file_path": file_path
                                })
            """
            
            support_documents = [{"file_path": "https://www.getcogno.ai/static/CognoAIApp/assets/illustration2.svg",
                                  "THUMBNAILURL": "https://www.the-digital-insurer.com/wp-content/uploads/2019/09/AllinCall_logo.png", "fileName": "CognoAI.png"}]

            response["status"] = 200
            response["message"] = "success"
            response["support_documents"] = support_documents
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCobrowsingSupportDocumentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCobrowsingSupportDocument = GetCobrowsingSupportDocumentAPI.as_view()


class AppClientStatusUpdateAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:

            if True:

                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                id = data["id"]
                
                auto_close_session = False
                if "auto_close_session" in data:
                    auto_close_session = data["auto_close_session"]

                user_token = request.COOKIES.get("cs_token")

                cobrowse_io = CobrowseIO.objects.get(session_id=id)

                app_cobrowse_session_obj = AppCobrowsingSessionManagement.objects.get(user_token=user_token,
                                                                                      cobrowse_io=cobrowse_io)

                if auto_close_session:
                    cobrowse_io.is_agent_connected = False
                    cobrowse_io.is_closed_session = True
                    cobrowse_io.is_archived = True
                    cobrowse_io.is_active = False
                    if cobrowse_io_obj.session_archived_cause == None:
                        cobrowse_io_obj.session_archived_cause = "CLIENT_INACTIVITY"
                        cobrowse_io_obj.session_archived_datetime = timezone.now()
                else:
                    cobrowse_io.is_updated = True
                    cobrowse_io.is_active = True

                cobrowse_io.last_update_datetime = timezone.now()
                cobrowse_io.save()

                app_cobrowse_session_obj.last_update_datetime = timezone.now()
                app_cobrowse_session_obj.save()

                agent_name = None
                if cobrowse_io.agent != None:
                    agent_name = str(cobrowse_io.agent.user.username)

                response["is_agent_connected"] = cobrowse_io.is_agent_active_timer(
                ) and cobrowse_io.is_agent_connected
                response["agent_name"] = agent_name
                response[
                    "agent_assistant_request_status"] = cobrowse_io.agent_assistant_request_status
                response["allow_agent_cobrowse"] = cobrowse_io.allow_agent_cobrowse
                response["is_archived"] = cobrowse_io.is_archived
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AppClientStatusUpdateAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppClientStatusUpdate = AppClientStatusUpdateAPI.as_view()


class AppClientSaveCobrowsingChatAPI(APIView):

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
            sender = strip_html_tags(data["sender"])
            message = remo_html_from_string(data["message"])
            attachment = strip_html_tags(data["attachment"])
            attachment_file_name = ""
            if "attachment_file_name" in data:
                attachment_file_name = strip_html_tags(data["attachment_file_name"])

            cobrowse_agent = None

            if cobrowse_io.access_token.enable_app_type == "agent":

                user_token = request.COOKIES.get("cs_token")
                app_cobrowse_session_obj = AppCobrowsingSessionManagement.objects.get(user_token=user_token,
                                                                                      cobrowse_io=cobrowse_io)
                sender = app_cobrowse_session_obj.user_alias

                if sender.find("expert") != -1:
                    try:
                        user_obj = User.objects.get(username=sender)
                        cobrowse_agent = CobrowseAgent.objects.get(
                            user=user_obj)
                    except Exception:
                        user_obj = User.objects.create(
                            username=sender, password=str(uuid.uuid4()))
                        cobrowse_agent = CobrowseAgent.objects.create(
                            user=user_obj, role="agent", access_token=cobrowse_io.access_token)

            else:
                user_obj = User.objects.get(username=sender)
                cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            if attachment == "None":
                attachment = None

            if attachment_file_name == "":
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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppClientSaveCobrowsingChat = AppClientSaveCobrowsingChatAPI.as_view()


class AppClientUpdateCobrowseIOAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            if cobrowse_access_token_obj == None:
                return Response(status=401)
            else:
                session_id = data["session_id"]
                cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

                is_session_closed = False

                if cobrowse_io.cobrowsing_start_datetime != None and not cobrowse_io.is_active_timer():
                    cobrowse_io.is_active = False
                    is_session_closed = True
                    logger.info(
                        "Closing cobrowsing session due to inactivity...", extra={'AppName': 'EasyAssist'})
                else:
                    cobrowse_io.is_active = True

                cobrowse_io.is_updated = True
                cobrowse_io.last_update_datetime = timezone.now()
                cobrowse_io.save()

                agent_name = None
                if cobrowse_io.agent != None:
                    agent_name = str(cobrowse_io.agent.user.username)

                session_archive_cause = ""
                if cobrowse_io.is_archived:
                    if cobrowse_io.session_archived_cause:
                        session_archive_cause = cobrowse_io.session_archived_cause
                
                response["message"] = "success"
                response["is_agent_connected"] = cobrowse_io.is_agent_active_timer(
                ) and cobrowse_io.is_agent_connected
                response["agent_name"] = agent_name
                response[
                    "agent_assistant_request_status"] = cobrowse_io.agent_assistant_request_status
                response["allow_agent_cobrowse"] = cobrowse_io.allow_agent_cobrowse
                response["is_lead"] = cobrowse_io.is_lead
                response["is_archived"] = cobrowse_io.is_archived
                response["session_archive_cause"] = session_archive_cause
                response["is_session_closed"] = is_session_closed
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AppClientUpdateCobrowseIOAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppClientUpdateCobrowseIO = AppClientUpdateCobrowseIOAPI.as_view()


class AppUpdateAgentAssistantRequestAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:

            if True:

                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)
                id = data["session_id"]
                otp = data["otp"]

                cobrowse_io = CobrowseIO.objects.get(session_id=id)

                if data["status"] == "true" and str(cobrowse_io.otp_validation) != str(otp) and cobrowse_io.access_token.enable_verification_code_popup:
                    response["status"] = 101
                    response[
                        "message"] = "Please enter valid verification code shared by our agent"
                else:
                    if data["status"] == "true":
                        cobrowse_io.allow_agent_cobrowse = "true"
                        cobrowse_io.agent_assistant_request_status = False
                        cobrowse_io.consent_allow_count = cobrowse_io.consent_allow_count + 1
                        cobrowse_io.cobrowsing_start_datetime = timezone.now()
                        response["status"] = 200
                        response["message"] = "success"
                    elif data["status"] == "false":
                        cobrowse_io.allow_agent_cobrowse = "false"
                        cobrowse_io.agent_assistant_request_status = False
                        cobrowse_io.consent_cancel_count = cobrowse_io.consent_cancel_count + 1
                        cobrowse_io.cobrowsing_start_datetime = None

                    cobrowse_io.save()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AppUpdateAgentAssistantRequestAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        logger.info(response, extra={'AppName': 'EasyAssist'})
        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppUpdateAgentAssistantRequest = AppUpdateAgentAssistantRequestAPI.as_view()


class AppAgentStatusUpdateAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            id = data["session_id"]
            cobrowse_io_obj = CobrowseIO.objects.get(session_id=id)
            cobrowse_io_obj.last_agent_update_datetime = timezone.now()
            cobrowse_io_obj.is_agent_connected = True
            cobrowse_io_obj.save()

            active_agent = get_active_agent_obj(request, CobrowseAgent)
            if active_agent:
                active_agent.last_agent_active_datetime = timezone.now()
                active_agent.save()

            response[
                "is_client_connected"] = cobrowse_io_obj.is_active and cobrowse_io_obj.is_active_timer()
            response["is_active"] = cobrowse_io_obj.is_active
            response["is_archived"] = cobrowse_io_obj.is_archived
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AppAgentStatusUpdateAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppAgentStatusUpdate = AppAgentStatusUpdateAPI.as_view()


class AppScheduleMeetingAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            logger.info(data, extra={'AppName': 'EasyAssist'})
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AppScheduleMeetingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppScheduleMeeting = AppScheduleMeetingAPI.as_view()


class AppCaptureClientScreenAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:

            if True:

                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                id = data["id"]
                content = data["content"]
                type_screenshot = data["type_screenshot"]

                cobrowse_io = CobrowseIO.objects.get(session_id=id)

                client_screen_root_dir = "client-screens"

                if not os.path.exists("files/" + client_screen_root_dir):
                    os.makedirs("files/" + client_screen_root_dir)

                image_screen_dir = client_screen_root_dir + \
                    "/" + str(cobrowse_io.session_id)

                if not os.path.exists("files/" + image_screen_dir):
                    os.makedirs("files/" + image_screen_dir)

                if type_screenshot == "pageshot":

                    pageshot_filepath = image_screen_dir + \
                        "/" + str(int(time.time())) + ".html"
                    pageshot_file = open(
                        settings.MEDIA_ROOT + pageshot_filepath, "w")

                    pageshot_file.write(content)
                    pageshot_file.close()

                    CobrowsingSessionMetaData.objects.create(cobrowse_io=cobrowse_io,
                                                             type_screenshot=type_screenshot,
                                                             content=settings.MEDIA_URL + pageshot_filepath)

                elif type_screenshot == "screenshot":

                    format, imgstr = content.split(';base64,')
                    ext = format.split('/')[-1]
                    image_name = str(int(time.time())) + "." + str(ext)
                    imgstr = imgstr.replace("%0A", "")
                    data = ContentFile(base64.b64decode(
                        imgstr), name='temp.' + ext)
                    image_path = default_storage.save(
                        image_screen_dir + "/" + image_name, data)
                    image_path = settings.MEDIA_URL + image_path

                    logger.info(image_path, extra={'AppName': 'EasyAssist'})

                    CobrowsingSessionMetaData.objects.create(cobrowse_io=cobrowse_io,
                                                             type_screenshot=type_screenshot,
                                                             content=image_path)

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseIOCaptureClientScreenAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppCaptureClientScreen = AppCaptureClientScreenAPI.as_view()


class AppClientCloseSessionAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            logger.info(data, extra={'AppName': 'EasyAssist'})
            session_id = sanitize_input_string(data["session_id"])
            feedback = sanitize_input_string(data["feedback"])
            nps_rating = sanitize_input_string(data["nps_rating"])

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            logger.info(cobrowse_io, extra={'AppName': 'EasyAssist'})

            cobrowse_io.is_active = False
            if not cobrowse_io.client_comments:
                cobrowse_io.client_comments = feedback
            if nps_rating != "None":
                nps_rating = int(nps_rating)
            else:
                nps_rating = None
            cobrowse_io.agent_rating = nps_rating
            cobrowse_io.last_update_datetime = timezone.now()
            cobrowse_io.client_session_end_time = timezone.now()
            cobrowse_io.is_archived = True
            cobrowse_io.save()

            logger.info(cobrowse_io.is_archived, extra={
                        'AppName': 'EasyAssist'})

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AppClientCloseSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        logger.info(response, extra={'AppName': 'EasyAssist'})
        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppClientCloseSession = AppClientCloseSessionAPI.as_view()


class AppRecordedSessionVideoAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            filename = strip_html_tags(data["session_id"])
            base64_data = strip_html_tags(data["base64_file"])

            if not os.path.exists('files/app-session-videos'):
                os.makedirs('files/app-session-videos')

            file_path = "files/app-session-videos/" + filename

            fh = open(file_path, "wb")
            fh.write(base64.b64decode(base64_data))
            fh.close()

            file_path = "/" + file_path

            response["status"] = 200
            response["message"] = "success"
            response["file_path"] = file_path
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AppRecordedSessionVideoAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppRecordedSessionVideo = AppRecordedSessionVideoAPI.as_view()


class GetAppCaptchaAPI(APIView):

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
                captcha = json.loads(captcha_py.read())
                captcha_py.flush()
                captcha_py.close()

            selected_captcha = random.choice(captcha)

            delete_expired_cobrowse_middleware_token(
                CobrowsingMiddlewareAccessToken)

            middleware_token = create_cobrowse_middleware_token(
                CobrowsingMiddlewareAccessToken)

            response["status"] = 200
            response["message"] = "success"
            response["file"] = settings.EASYCHAT_HOST_URL + "/static/EasyAssistApp/captcha_images/" + \
                selected_captcha["file"]
            response["cobrowsemiddlewaretoken"] = str(middleware_token.token)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCaptchaAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAppCaptcha = GetAppCaptchaAPI.as_view()


class AppAgentAuthenticationAPI(APIView):

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
            username = remo_html_from_string(username)
            username = remo_special_tag_from_string(username)
            password = remo_html_from_string(password)
            
            if False:
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

                    is_login_allowed = True
                    is_secured_login_allowed = True

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
            logger.error("Error AppAgentAuthenticationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppAgentAuthentication = AppAgentAuthenticationAPI.as_view()


class GetAppClientCobrowsingChatHistoryAPI(APIView):

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

            chat_history = []
            for cobrowsing_chat_history_obj in cobrowsing_chat_history_objs:

                est = pytz.timezone(settings.TIME_ZONE)
                chat_datetime = cobrowsing_chat_history_obj.datetime.astimezone(
                    est).strftime("%I:%M %p")

                sender = "client"
                if cobrowsing_chat_history_obj.sender != None:
                    sender = cobrowsing_chat_history_obj.sender.name()

                chat_history.append({
                    "sender": sender,
                    "message": cobrowsing_chat_history_obj.message,
                    "attachment": cobrowsing_chat_history_obj.attachment,
                    "attachment_file_name": cobrowsing_chat_history_obj.attachment_file_name,
                    "datetime": chat_datetime
                })

            response["status"] = 200
            response["message"] = "success"
            response["chat_history"] = chat_history
            logger.info(response, extra={"AppName": "EasyAssist"})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAppClientCobrowsingChatHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAppClientCobrowsingChatHistory = GetAppClientCobrowsingChatHistoryAPI.as_view()


class AppSubmitClientFeedbackAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = sanitize_input_string(data["session_id"])
            client_feedback = sanitize_input_string(data["feedback"])
            nps_rating = data["rating"]
            if nps_rating != None:
                nps_rating = sanitize_input_string(str(nps_rating))
            
            cobrowse_io = CobrowseIO.objects.filter(session_id=session_id).first()

            if cobrowse_io:
                cobrowse_io.is_active = False
                if not cobrowse_io.client_comments:
                    cobrowse_io.client_comments = client_feedback
                
                if nps_rating == "None" or nps_rating == None:
                    cobrowse_io.agent_rating = None
                else:
                    if int(nps_rating) < 0 or int(nps_rating) > 10:
                        response["message"] = "Invaild NPS rating provided"
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)
                    else:
                        cobrowse_io.agent_rating = int(nps_rating)
                
                if not cobrowse_io.is_archived:
                    cobrowse_io.last_update_datetime = timezone.now()
                cobrowse_io.client_session_end_time = timezone.now()
                cobrowse_io.is_archived = True
                if cobrowse_io.session_archived_cause == None:
                    cobrowse_io.session_archived_cause = "CLIENT_ENDED"
                    cobrowse_io.session_archived_datetime = timezone.now()
                cobrowse_io.save()
                
                category = "session_closed"
                description = "Session is closed by customer after submitting feedback"
                save_system_audit_trail(
                    category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, None)

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AppSubmitClientFeedbackAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppSubmitClientFeedback = AppSubmitClientFeedbackAPI.as_view()


class AppCobrowsingAvailableAgentListAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            access_token = strip_html_tags(data["access_token"])
            access_token = remo_html_from_string(access_token)
            cobrowse_access_token_obj = None

            try:
                cobrowse_access_token_obj = CobrowseAccessToken.objects.get(
                    key=access_token)
            except Exception:
                pass

            if cobrowse_access_token_obj is not None:

                agent_admin = cobrowse_access_token_obj.agent

                agents = get_list_agents_under_admin(
                    agent_admin, is_active=True)

                available_agent_count = 0

                for agent in agents:
                    if agent.is_cobrowsing_active == False:
                        available_agent_count += 1

                if available_agent_count > 0:
                    response["agent_available"] = True
                else:
                    response["agent_available"] = False

                response["available_agent_count"] = available_agent_count
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AvailableAgentListAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppCobrowsingAvailableAgentList = AppCobrowsingAvailableAgentListAPI.as_view()


class AppSaveNonWorkingHourCustomerDetailAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            
            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            if cobrowse_access_token_obj == None:
                return Response(status=401)
            elif cobrowse_access_token_obj.enable_app_type != "customer":
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                name = data["name"]
                name = remo_html_from_string(name)
                name = remo_special_tag_from_string(name)
                mobile_number = data["mobile_number"]
                mobile_number = remo_html_from_string(mobile_number)
                mobile_number = remo_special_tag_from_string(mobile_number)
                meta_data = data["meta_data"]
                app_channel = data["channel"]

                primary_id = mobile_number.strip().lower()
                primary_id = hashlib.md5(primary_id.encode()).hexdigest()

                share_client_session = False

                cobrowse_io = CobrowseIO.objects.create(full_name=name,
                                                        mobile_number=mobile_number,
                                                        share_client_session=share_client_session,
                                                        app_channel=app_channel,
                                                        primary_value=primary_id)

                cobrowse_io.is_app_cobrowse_session = True

                if "product_details" in meta_data and "title" in meta_data["product_details"]:
                    cobrowse_io.title = strip_html_tags(meta_data[
                        "product_details"]["title"].strip())

                if "product_details" in meta_data and "url" in meta_data["product_details"]:
                    cobrowse_io.active_url = meta_data[
                        "product_details"]["url"].strip()

                if "product_details" in meta_data and "description" in meta_data["product_details"]:
                    meta_data["product_details"]["description"] = strip_html_tags(meta_data[
                        "product_details"]["description"].strip())

                meta_data = json.dumps(meta_data)
                meta_data = custom_encrypt_obj.encrypt(meta_data)
                cobrowse_io.meta_data = meta_data
                cobrowse_io.is_active = False
                cobrowse_io.is_archived = True
                cobrowse_io.last_update_datetime = timezone.now()
                cobrowse_io.is_agent_connected = False
                cobrowse_io.cobrowsing_start_datetime = None
                cobrowse_io.is_lead = False
                cobrowse_io.access_token = cobrowse_access_token_obj
                cobrowse_io.agent = None

                if cobrowse_io.session_archived_cause == None:
                    cobrowse_io.session_archived_cause = "FOLLOWUP"
                    cobrowse_io.session_archived_datetime = timezone.now()

                cobrowse_io.save()

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AppSaveNonWorkingHourCustomerDetailAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AppSaveNonWorkingHourCustomerDetail = AppSaveNonWorkingHourCustomerDetailAPI.as_view()
