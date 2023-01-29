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
import imgkit

from operator import itemgetter
from collections import OrderedDict

logger = logging.getLogger(__name__)


def CobrowseIOAgentReverserPage(request, session_id):
    try:

        cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

        if cobrowse_io.is_archived:
            return render(request, "EasyAssistApp/cobrowsing_session_expired_reverse.html", {
                "logo": cobrowse_io.access_token.source_easyassist_cobrowse_logo, 
                "message": "Customer support session has been ended.<br>Please close this tab for security reasons.",
                "easyassist_font_family": cobrowse_io.access_token.font_family,
            })

        if 'session_ended' in request.GET:
            return render(request, "EasyAssistApp/cobrowsing_session_expired_reverse.html", {
                "logo": cobrowse_io.access_token.source_easyassist_cobrowse_logo, 
                "message": "You left the session..<br>Please close this tab for security reasons.",
                "easyassist_font_family": cobrowse_io.access_token.font_family,
            })

        agent_admin = cobrowse_io.access_token.agent
        is_socket = cobrowse_io.access_token.is_socket
        supported_language_objs = agent_admin.supported_language.filter(is_deleted=False).order_by('index')
        allow_language_support = cobrowse_io.access_token.allow_language_support
        product_category_objs = agent_admin.product_category.filter(is_deleted=False).order_by('index')
        choose_product_category = cobrowse_io.access_token.choose_product_category
        floating_button_bg_color = cobrowse_io.access_token.floating_button_bg_color
        allow_cobrowsing_meeting = cobrowse_io.access_token.allow_cobrowsing_meeting
        enable_voip_calling = cobrowse_io.access_token.enable_voip_calling
        enable_voip_with_video_calling = cobrowse_io.access_token.enable_voip_with_video_calling
        voip_with_video_calling_message = cobrowse_io.access_token.voip_with_video_calling_message
        voip_calling_message = cobrowse_io.access_token.voip_calling_message
        support_agents = get_list_agents_under_admin(agent_admin, None)
        enable_edit_access = cobrowse_io.access_token.enable_edit_access
        enable_optimized_cobrowsing = cobrowse_io.access_token.enable_optimized_cobrowsing
        is_client_in_mobile = cobrowse_io.is_client_in_mobile
        enable_cobrowsing_annotation = cobrowse_io.access_token.enable_cobrowsing_annotation
        enable_chat_functionality = cobrowse_io.access_token.enable_chat_functionality
        enable_chat_bubble = cobrowse_io.access_token.enable_chat_bubble
        chat_bubble_icon_source = cobrowse_io.access_token.chat_bubble_icon_source

        invited_agent_details_obj = None
        if cobrowse_io.access_token.enable_invite_agent_in_cobrowsing:
            invited_agent_details_objs = CobrowseIOInvitedAgentsDetails.objects.filter(cobrowse_io=cobrowse_io)
            if invited_agent_details_objs:
                invited_agent_details_obj = invited_agent_details_objs[0]

        admin_agent_username = ""
        invited_agent_username = ""
        display_agent_profile = cobrowse_io.access_token.display_agent_profile
        invited_agent_profile_pic_source = ""

        agent_name = cobrowse_io.agent.user.first_name
        admin_agent_username = cobrowse_io.agent.user.username
        if agent_name is None or agent_name.strip() == "":
            agent_name = cobrowse_io.agent.user.username
        admin_agent_profile_pic_source = agent_admin.agent_profile_pic_source

        client_name = cobrowse_io.full_name
        cobrowse_io.is_active = True
        cobrowse_io.last_update_datetime = timezone.now()
        if cobrowse_io.cobrowsing_start_datetime == None:
            cobrowse_io.cobrowsing_start_datetime = timezone.now()
        cobrowse_io.save()

        is_agent = False
        invited_agent_name = ""

        invited_agent = None
        agent_identifier = ""
        agent_joined_first_time = True

        if 'id' in request.GET:
            agent_identifier = request.GET['id']
            invited_agent = CobrowseAgent.objects.filter(virtual_agent_code=agent_identifier).first()
            if invited_agent == None:
                return HttpResponse(status=404)
            if invited_agent not in cobrowse_io.support_agents.all():
                return HttpResponse(status=404)

        if invited_agent:
            is_agent = True
            invited_agent.is_cobrowsing_active = True
            invited_agent.save()
            if invited_agent_details_obj != None:
                invited_agent_details_obj.support_agents_joined.add(invited_agent)
                invited_agent_details_obj.save()
            if cobrowse_io.meeting_start_datetime != None:
                meeting_io = CobrowseVideoConferencing.objects.filter(meeting_id=session_id)
                if meeting_io:
                    meeting_io = meeting_io.first()
                    video_audit_trail_obj = CobrowseVideoAuditTrail.objects.filter(cobrowse_video=meeting_io)
                    if video_audit_trail_obj:
                        video_audit_trail_obj = video_audit_trail_obj.first()
                        video_audit_trail_obj.meeting_agents_invited.add(invited_agent)
                        video_audit_trail_obj.save()
            invited_agent_name = invited_agent.user.first_name
            invited_agent_username = invited_agent.user.username
            invited_agent_profile_pic_source = invited_agent.agent_profile_pic_source    
            if invited_agent_name is None or invited_agent_name.strip() == "":
                invited_agent_name = invited_agent.user.username  

            system_audit_trail_obj = SystemAuditTrail.objects.filter(
                cobrowse_io=cobrowse_io,
                sender=invited_agent,
                category="session_join").count()
            if system_audit_trail_obj > 0:
                agent_joined_first_time = False

            if invited_agent:
                agent_joined_first_time = True
                
            category = "session_join"
            description = "Agent " + str(invited_agent.user.username) + " has joined session."
            save_system_audit_trail(category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, invited_agent)

        return render(request, "EasyAssistApp/cobrowse_agent_reverse.html", {
            "cobrowse_io": cobrowse_io,
            "enable_edit_access": enable_edit_access,
            "floating_button_bg_color": floating_button_bg_color,
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
            # "is_admin_agent": is_admin_agent,
            "toast_timeout": COBROWSE_TOAST_TIMEOUT,
            "access_token": str(cobrowse_io.access_token.key),
            "DEVELOPMENT": settings.DEVELOPMENT,
            "enable_voip_calling": enable_voip_calling,
            "voip_calling_message": voip_calling_message,
            "enable_voip_with_video_calling": enable_voip_with_video_calling,
            "voip_with_video_calling_message": voip_with_video_calling_message,
            "allow_cobrowsing_meeting": allow_cobrowsing_meeting,
            "enable_optimized_cobrowsing": enable_optimized_cobrowsing,
            "cobrowse_agent": cobrowse_io.agent,
            "is_mobile": request.user_agent.is_mobile,
            "is_client_in_mobile": is_client_in_mobile,
            "is_agent": is_agent,
            "invited_agent_name": invited_agent_name,
            "admin_agent_username": admin_agent_username,
            "invited_agent_username": invited_agent_username,
            "agent_identifier": agent_identifier,
            "agent_joined_first_time": agent_joined_first_time,
            "enable_cobrowsing_annotation": enable_cobrowsing_annotation,
            "easyassist_font_family": cobrowse_io.access_token.font_family,
            "enable_chat_functionality": enable_chat_functionality,
            "admin_agent_profile_pic_source": admin_agent_profile_pic_source,
            "invited_agent_profile_pic_source": invited_agent_profile_pic_source,
            "display_agent_profile": display_agent_profile,
            "floating_button_position": cobrowse_io.access_token.floating_button_position,
            "enable_chat_bubble": enable_chat_bubble,
            "chat_bubble_icon_source": chat_bubble_icon_source,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CobrowseIOReverseInitializeAPI %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(status=401)


class CheckClientReverseCobrowseStatusAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = data["session_id"]
            session_id = remo_html_from_string(session_id)

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            cobrowse_io.is_active = True
            cobrowse_io.last_update_datetime = timezone.now()
            cobrowse_io.save()

            response["is_agent_connected"] = cobrowse_io.is_agent_active_timer(
            ) and cobrowse_io.is_agent_connected
            response["agent_name"] = cobrowse_io.agent.user.username
            response["is_archived"] = cobrowse_io.is_archived
            response[
                "agent_meeting_request_status"] = cobrowse_io.agent_meeting_request_status
            response["allow_agent_meeting"] = cobrowse_io.allow_agent_meeting
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckClientReverseCobrowseStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckClientReverseCobrowseStatus = CheckClientReverseCobrowseStatusAPI.as_view()


class SyncInvitedAgentStatusAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = data["session_id"]
            session_id = remo_html_from_string(session_id)

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            cobrowse_io.save()

            response["is_archived"] = cobrowse_io.is_archived
            response["agent_meeting_request_status"] = cobrowse_io.agent_meeting_request_status
            response["allow_agent_meeting"] = cobrowse_io.allow_agent_meeting
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SyncInvitedAgentStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SyncInvitedAgentStatus = SyncInvitedAgentStatusAPI.as_view()


class SaveReverseCobrowsingChatAPI(APIView):

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
            attachment_file_name = strip_html_tags(
                data["attachment_file_name"])
            attachment_file_name = remo_html_from_string(attachment_file_name)
            agent_username = strip_html_tags(data["agent_username"])
            agent_username = remo_html_from_string(agent_username)
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            chat_type = strip_html_tags(data["chat_type"])
            chat_type = remo_html_from_string(chat_type)
            cobrowse_agent = CobrowseAgent.objects.filter(user__username=agent_username).first()

            if not cobrowse_io.is_archived:
                agent_profile_pic_source = ""
                if sender != "client":
                    agent_profile_pic_source = remo_special_html_from_string(
                        strip_html_tags(data["agent_profile_pic_source"]))

                attachment = remo_special_html_from_string(attachment)
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
            logger.error("Error SaveReverseCobrowsingChatAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveReverseCobrowsingChat = SaveReverseCobrowsingChatAPI.as_view()


class GetReverseCobrowsingChatHistoryAPI(APIView):

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
            client_name = cobrowse_io.full_name

            cobrowsing_chat_history_objs = cobrowse_io.get_cobrowsing_chat_history()

            chat_history = []

            for cobrowsing_chat_history_obj in cobrowsing_chat_history_objs:

                est = pytz.timezone(settings.TIME_ZONE)
                chat_datetime = cobrowsing_chat_history_obj.datetime.astimezone(
                    est).strftime("%d %b %Y %I:%M %p")

                sender = "client"
                sender_name = ""
                agent_profile_pic_source = cobrowsing_chat_history_obj.agent_profile_pic_source
                is_admin_message = False

                if cobrowsing_chat_history_obj.sender != None:
                    sender = cobrowsing_chat_history_obj.sender.name()
                    sender_name = cobrowsing_chat_history_obj.sender.agent_name()
                    if cobrowsing_chat_history_obj.sender == cobrowse_io.agent:
                        is_admin_message = True

                chat_history.append({
                    "sender": sender,
                    "message": cobrowsing_chat_history_obj.message,
                    "attachment": cobrowsing_chat_history_obj.attachment,
                    "attachment_file_name": cobrowsing_chat_history_obj.attachment_file_name,
                    "datetime": chat_datetime,
                    "sender_name": sender_name,
                    "chat_type": cobrowsing_chat_history_obj.chat_type,
                    "is_admin_message": is_admin_message,
                    "agent_profile_pic_source": agent_profile_pic_source,
                })

            response["status"] = 200
            response["message"] = "success"
            response["chat_history"] = chat_history
            response["client_name"] = client_name
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetReverseCobrowsingChatHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetReverseCobrowsingChatHistory = GetReverseCobrowsingChatHistoryAPI.as_view()


class CloseReverseCobrowsingSessionAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = strip_html_tags(data["session_id"])
            id = remo_html_from_string(id)
            comments = strip_html_tags(data["comments"])
            rating = data["rating"]

            cobrowse_io = CobrowseIO.objects.get(session_id=id)

            cobrowse_io.is_active = False
            cobrowse_io.client_comments = comments
            active_agent = cobrowse_io.agent
            active_agent.is_cobrowsing_active = False
            active_agent.is_cognomeet_active = False
            active_agent.save(update_fields=["is_cobrowsing_active", "is_cognomeet_active"])

            if cobrowse_io.is_archived == False:
                cobrowse_io.last_update_datetime = timezone.now()

            cobrowse_io.client_session_end_time = timezone.now()
            cobrowse_io.is_archived = True

            if rating != "None" and rating != None and (int(rating) < 0 or int(rating) > 10):
                response["status"] = "400"
                response["message"] = "Invalid rating"
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)
                
            if rating != "None" and rating != None:
                cobrowse_io.agent_rating = int(rating)
            else:
                cobrowse_io.agent_rating = None
            cobrowse_io.save()

            meeting_io = CobrowseVideoConferencing.objects.filter(
                meeting_id=id).first()

            if meeting_io:
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
                    logger.error("Error CloseReverseCobrowsingSessionAPI %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

            category = "session_closed"

            description = "Session is closed by customer after submitting feedback"

            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, None)

            if cobrowse_io.session_archived_cause == None:
                cobrowse_io.session_archived_cause = "CLIENT_ENDED"
                cobrowse_io.session_archived_datetime = timezone.now()
                cobrowse_io.save()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CloseReverseCobrowsingSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CloseReverseCobrowsingSession = CloseReverseCobrowsingSessionAPI.as_view()


class UpdateReverseCobrowseMeetingRequestAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = data["id"]

            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            cobrowse_access_token_obj = cobrowse_io.access_token

            if data["status"] == "true":
                cobrowse_io.allow_agent_meeting = "true"
                cobrowse_io.agent_meeting_request_status = False
                cobrowse_io.meeting_start_datetime = timezone.now()
                description = "Meeting request accepted by customer"

            elif data["status"] == "false":
                cobrowse_io.allow_agent_meeting = "false"
                cobrowse_io.agent_meeting_request_status = False
                cobrowse_io.meeting_start_datetime = None
                description = "Meeting request declined by customer"

            category = "session_details"

            if cobrowse_access_token_obj != None:
                save_system_audit_trail(
                    category, description, cobrowse_io, cobrowse_access_token_obj, SystemAuditTrail, None)

            cobrowse_io.save()
            response["status"] = 200
            response["message"] = "success"
            response["meeting_allowed"] = data["status"]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateReverseCobrowseMeetingRequestAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateReverseCobrowseMeetingRequest = UpdateReverseCobrowseMeetingRequestAPI.as_view()


class CloseCobrowsingSessionReverseAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            id = data["id"]
            agent_username = data["agent_username"]

            cobrowse_io = CobrowseIO.objects.get(session_id=id)
            cobrowse_access_token_obj = cobrowse_io.access_token
            active_agent = CobrowseAgent.objects.filter(user__username=agent_username).first()

            if active_agent and cobrowse_access_token_obj and cobrowse_io:
                category = "session_details"
                description = "Agent " + active_agent.agent_name() + " has left the session."
                save_system_audit_trail(category, description, cobrowse_io, cobrowse_access_token_obj, SystemAuditTrail, None)
                active_agent.is_active = False
                active_agent.is_cobrowsing_active = False
                active_agent.is_cognomeet_active = False
                active_agent.save(update_fields=["is_active", "is_cobrowsing_active", "is_cognomeet_active"])

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CloseCobrowsingSessionReverseAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CloseCobrowsingSessionReverse = CloseCobrowsingSessionReverseAPI.as_view()
