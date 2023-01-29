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

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
"""For user authentication"""
from django.contrib.auth import authenticate, login, logout
# Create your views here.
from EasyChatApp.models import User
from EasyAssistApp.models import *
from EasyAssistApp.utils import *
from EasyAssistApp.send_email import send_invite_link_over_mail_reverse_cobrowsing, send_reverse_cobrowse_invite_link
from EasyAssistApp.utils_validation import is_email_valid


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


class CobrowseIOReverseInitializeAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            HTTP_USER_AGENT = None
            HTTP_X_FORWARDED_FOR = None
            if settings.ENABLE_IP_TRACKING:
                HTTP_X_FORWARDED_FOR = request.META["HTTP_X_FORWARDED_FOR"]
                HTTP_USER_AGENT = request.META["HTTP_USER_AGENT"]

            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            origin = get_request_origin(request)

            if cobrowse_access_token_obj == None:
                return Response(status=401)
            elif not cobrowse_access_token_obj.is_valid_domain(origin):
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

                virtual_agent_code = data["virtual_agent_code"]
                virtual_agent_code = remo_html_from_string(virtual_agent_code)
                virtual_agent_code = remo_special_tag_from_string(
                    virtual_agent_code)
                
                client_email = data["client_email"]
                client_email = remo_html_from_string(client_email)
                client_email = remo_special_html_from_string(client_email)
                client_email = client_email.strip()

                if client_email != "" and (not is_email_valid(client_email)):
                    response["status"] = 104
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(
                        response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                
                meta_data = data["meta_data"]

                if "product_details" in meta_data and "url" in meta_data["product_details"]:
                    if is_url_valid(meta_data["product_details"]["url"].strip()) == False:
                        response["status"] = 500
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(
                            response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)
                
                cobrowse_agent = None
                try:
                    cobrowse_agent = CobrowseAgent.objects.get(
                        virtual_agent_code=virtual_agent_code)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error CobrowseIOReverseInitializeAPI %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                is_client_in_mobile = False
                try:
                    is_client_in_mobile = request.user_agent.is_mobile
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error CobrowseIOReverseInitializeAPI %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                if cobrowse_agent != None:

                    mobile_number = mobile_number.strip().lower()
                    primary_id = hashlib.md5(
                        mobile_number.encode()).hexdigest()

                    request_meta_details = {
                        "HTTP_USER_AGENT": HTTP_USER_AGENT,
                        "HTTP_X_FORWARDED_FOR": HTTP_X_FORWARDED_FOR
                    }

                    cobrowse_io = CobrowseIO.objects.create(full_name=name,
                                                            mobile_number=mobile_number,
                                                            primary_value=primary_id)

                    if "product_details" in meta_data and "title" in meta_data["product_details"]:
                        cobrowse_io.title = meta_data[
                            "product_details"]["title"].strip()

                    if "product_details" in meta_data and "url" in meta_data["product_details"]:
                        cobrowse_io.active_url = meta_data[
                            "product_details"]["url"].strip()
                    
                    if client_email != "":
                        send_reverse_cobrowse_invite_link(client_email, str(cobrowse_agent.user.username), str(cobrowse_io.session_id))

                    meta_data = json.dumps(meta_data)
                    meta_data = custom_encrypt_obj.encrypt(meta_data)
                    cobrowse_io.meta_data = meta_data
                    cobrowse_io.is_active = True
                    cobrowse_io.last_agent_update_datetime = timezone.now()
                    cobrowse_io.is_agent_connected = True
                    cobrowse_io.cobrowsing_start_datetime = None
                    cobrowse_io.is_lead = False
                    cobrowse_io.is_reverse_cobrowsing = True
                    cobrowse_io.access_token = cobrowse_access_token_obj
                    cobrowse_io.request_meta_details = json.dumps(
                        request_meta_details)
                    cobrowse_io.agent = cobrowse_agent
                    cobrowse_io.last_update_datetime = timezone.now()
                    cobrowse_io.is_client_in_mobile = is_client_in_mobile
                    cobrowse_io.save()

                    send_page_refresh_request_to_agent(cobrowse_agent)

                    response["session_id"] = str(cobrowse_io.session_id)
                    response["status"] = 200
                    response["message"] = "success"
                else:
                    response["status"] = 101
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseIOReverseInitializeAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CobrowseIOReverseInitialize = CobrowseIOReverseInitializeAPI.as_view()


class CheckAgentReverseCobrowseStatusAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:

            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            origin = get_request_origin(request)

            auth_params = extract_authorization_params(request)

            if auth_params == None:
                return Response(status=401)
            if cobrowse_access_token_obj == None:
                return Response(status=401)
            elif not cobrowse_access_token_obj.is_valid_domain(origin):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                session_id = data["session_id"]
                session_id = remo_html_from_string(session_id)

                cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
                cobrowse_io.is_updated = True
                cobrowse_io.last_agent_update_datetime = timezone.now()
                cobrowse_io.is_agent_connected = True
                cobrowse_io.save()
                
                cobrowse_agent = cobrowse_io.agent
                cobrowse_agent.last_agent_active_datetime = timezone.now()
                cobrowse_agent.is_cobrowsing_active = True
                cobrowse_agent.is_active = True
                cobrowse_agent.save()

                try:
                    time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=1)
                    agent_work_audit_trail_obj = CobrowseAgentWorkAuditTrail.objects.filter(
                        agent=cobrowse_agent,
                        session_end_datetime__gte=time_threshold).order_by(
                            '-session_start_datetime').first()

                    if agent_work_audit_trail_obj != None:
                        agent_work_audit_trail_obj.session_end_datetime = timezone.now()
                        agent_work_audit_trail_obj.save()
                    else:
                        agent_work_audit_trail_obj = CobrowseAgentWorkAuditTrail.objects.create(
                            agent=cobrowse_agent,
                            session_start_datetime=timezone.now(),
                            session_end_datetime=timezone.now())
                        agent_work_audit_trail_obj.save()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error CheckAgentReverseCobrowseStatusAPI %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                response["message"] = "success"
                response["is_customer_connected"] = cobrowse_io.is_active_timer(
                ) and cobrowse_io.is_active
                response["is_archived"] = cobrowse_io.is_archived
                response["status"] = 200
                response["agent_name"] = cobrowse_agent.agent_name()
                response["agent_username"] = cobrowse_agent.user.username
                response["agent_profile_pic_source"] = cobrowse_agent.agent_profile_pic_source
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckAgentReverseCobrowseStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckAgentReverseCobrowseStatus = CheckAgentReverseCobrowseStatusAPI.as_view()


class CloseReverseAgentCobrowsingSessionAPI(APIView):

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

            feedback = data["feedback"]
            feedback = remo_html_from_string(feedback)
            feedback = remo_special_tag_from_string(feedback)

            subcomments = data["subcomments"]
            subcomments = remo_html_from_string(subcomments)
            subcomments = remo_special_tag_from_string(subcomments)

            comment_desc = ""
            if "comment_desc" in data:
                comment_desc = strip_html_tags(data["comment_desc"])

            is_helpful = False
            if "is_helpful" in data:
                is_helpful = data["is_helpful"]

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            cobrowse_io.is_active = False
            if cobrowse_io.agent_comments == "":
                cobrowse_io.agent_comments = feedback
            cobrowse_io.is_helpful = is_helpful

            if cobrowse_io.is_archived == False:
                cobrowse_io.last_agent_update_datetime = timezone.now()

            cobrowse_io.is_archived = True
            active_agent = cobrowse_io.agent
            active_agent.is_active = False
            active_agent.is_cobrowsing_active = False
            active_agent.is_cognomeet_active = False
            active_agent.save(update_fields=["is_active", "is_cobrowsing_active", "is_cognomeet_active"])
            
            cobrowse_io.save()

            meeting_io = CobrowseVideoConferencing.objects.filter(
                meeting_id=session_id).first()

            if meeting_io:
                meeting_io.is_expired = True
                meeting_io.agent_comments = comment_desc
                meeting_io.save()

                try:
                    audit_trail = CobrowseVideoAuditTrail.objects.get(
                        cobrowse_video=meeting_io)
                    audit_trail.meeting_ended = timezone.now()
                    audit_trail.is_meeting_ended = True
                    audit_trail.save()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error CloseReverseAgentCobrowsingSessionAPI %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

            category = "session_closed"

            description = "Session is closed by " + \
                str(cobrowse_io.agent.user.username) + \
                " after submitting feedback"

            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, None)
            current_session_comments = CobrowseAgentComment.objects.filter(cobrowse_io=cobrowse_io)
            if current_session_comments.exists() == False:
                save_agent_closing_comments_cobrowseio(
                    cobrowse_io, active_agent, feedback, CobrowseAgentComment, comment_desc, subcomments)

            if cobrowse_io.session_archived_cause == None:
                if cobrowse_io.cobrowsing_start_datetime == None and cobrowse_io.meeting_start_datetime == None:
                    cobrowse_io.session_archived_cause = "UNATTENDED"
                else:
                    cobrowse_io.session_archived_cause = "AGENT_ENDED"
                cobrowse_io.session_archived_datetime = timezone.now()
                cobrowse_io.save()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CloseReverseAgentCobrowsingSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CloseReverseAgentCobrowsingSession = CloseReverseAgentCobrowsingSessionAPI.as_view()


class RequestVoipMeetingAPI(APIView):

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
            active_agent = cobrowse_io.agent

            cobrowse_io.agent_meeting_request_status = True
            cobrowse_io.allow_agent_meeting = None
            cobrowse_io.meeting_start_datetime = None
            cobrowse_io.save()

            category = "session_details"
            description = "Request for meeting sent by " + \
                str(active_agent.user.username)
            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, active_agent)

            cobrowse_agent = cobrowse_io.agent
            try:
                cobrowse_video_conf_obj = CobrowseVideoConferencing.objects.get(meeting_id=session_id)
            except Exception:
                is_voip_meeting = False
                if cobrowse_agent.get_access_token_obj().enable_voip_calling == True: 
                    is_voip_meeting = True
                elif cobrowse_agent.get_access_token_obj().enable_voip_with_video_calling == True:
                    is_voip_meeting = True
                else:
                    is_voip_meeting = False
                cobrowse_video_conf_obj = CobrowseVideoConferencing.objects.create(
                    meeting_id=session_id,
                    agent=cobrowse_agent,
                    meeting_description="Cobrowsing Meeting",
                    meeting_start_date=timezone.now(),
                    meeting_start_time=timezone.localtime(timezone.now()),
                    full_name=cobrowse_io.full_name,
                    mobile_number=cobrowse_io.mobile_number,
                    is_cobrowsing_meeting=True,
                    is_voip_meeting=is_voip_meeting)
            
            audit_trail_obj = CobrowseVideoAuditTrail.objects.filter(cobrowse_video=cobrowse_video_conf_obj)
            if audit_trail_obj:
                audit_trail_obj = audit_trail_obj.first()
            else:
                audit_trail_obj = CobrowseVideoAuditTrail.objects.create(cobrowse_video=cobrowse_video_conf_obj)

            for agent in cobrowse_io.support_agents.all():
                if agent.is_cobrowsing_active:
                    audit_trail_obj.meeting_agents_invited.add(agent)
            audit_trail_obj.save()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RequestVoipMeetingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


RequestVoipMeeting = RequestVoipMeetingAPI.as_view()


class CheckReverseCobrowsingMeetingStatusAPI(APIView):

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

            active_agent = cobrowse_io.agent
            is_cognomeet_active = None
            if active_agent:
                is_cognomeet_active = active_agent.is_cognomeet_active
            is_meeting_allowed = False
            
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
            logger.error("Error CheckReverseCobrowsingMeetingStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckReverseCobrowsingMeetingStatus = CheckReverseCobrowsingMeetingStatusAPI.as_view()


class SaveClientLocationAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            session_id = data["session_id"]
            latitude = data["latitude"]
            longitude = data["longitude"]

            session_id = remo_html_from_string(session_id)
            latitude = remo_html_from_string(str(latitude))
            longitude = remo_html_from_string(str(longitude))

            cobrowse_io_obj = CobrowseIO.objects.get(
                session_id=session_id)

            cobrowse_io_obj.latitude = latitude
            cobrowse_io_obj.longitude = longitude

            cobrowse_io_obj.save()

            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SaveClientLocationAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status"] = 500

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveClientLocation = SaveClientLocationAPI.as_view()


class GetCobrowsingMetaInformationReverseAPI(APIView):

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
            logger.error("Error GetCobrowsingMetaInformationReverseAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCobrowsingMetaInformationReverse = GetCobrowsingMetaInformationReverseAPI.as_view()


class GetListOfSupportAgentsReverseAPI(APIView):

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
            agent_admin = cobrowse_io.access_token.agent

            agents = get_list_agents_under_admin(agent_admin, is_active=None)
            support_agents = []

            for agent in agents:
                if cobrowse_io.agent.user.pk == agent.user.pk:
                    continue
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
            logger.error("Error GetListOfSupportAgentsReverseAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetListOfSupportAgentsReverse = GetListOfSupportAgentsReverseAPI.as_view()


class ShareCobrowsingSessionReverseAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            session_id = strip_html_tags(data["id"])
            session_id = remo_html_from_string(session_id)
            support_agents = data["support_agents"]
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            access_token_obj = cobrowse_io.access_token

            invited_agent_details_obj = None
            if access_token_obj.enable_invite_agent_in_cobrowsing:
                invited_agent_details_objs = CobrowseIOInvitedAgentsDetails.objects.filter(cobrowse_io=cobrowse_io)
                if invited_agent_details_objs:
                    invited_agent_details_obj = invited_agent_details_objs[0]
                else:
                    invited_agent_details_obj = CobrowseIOInvitedAgentsDetails.objects.create(cobrowse_io=cobrowse_io)
            
            agent_username_list = []
            for user_id in support_agents:
                user_obj = User.objects.get(pk=int(user_id))
                cobrowse_agent = CobrowseAgent.objects.get(user=user_obj)

                cobrowsing_url = settings.EASYCHAT_HOST_URL + "/easy-assist/client/" + session_id + '?id=' + str(cobrowse_agent.virtual_agent_code)

                agent_name = cobrowse_agent.user.first_name
                if agent_name is None or agent_name.strip() == "":
                    agent_name = cobrowse_agent.user.username

                send_invite_link_over_mail_reverse_cobrowsing(cobrowse_agent.user.email, cobrowsing_url, agent_name)

                cobrowse_io.support_agents.add(cobrowse_agent)
                if invited_agent_details_obj != None:
                    invited_agent_details_obj.support_agents_invited.add(cobrowse_agent)
                agent_username_list.append(cobrowse_agent.user.username)

            if invited_agent_details_obj != None:
                invited_agent_details_obj.save()

            shared_agent_details = ", ".join(agent_username_list)
            category = "session_details"
            if len(agent_username_list) == 1:
                description = "Agent " + shared_agent_details + " was invited to the session"
            else:
                description = "Agents " + shared_agent_details + " were invited to the session"

            active_agent = cobrowse_io.agent

            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, active_agent)

            cobrowse_io.save()
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ShareCobrowsingSessionReverseAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ShareCobrowsingSessionReverse = ShareCobrowsingSessionReverseAPI.as_view()


class GetSupportMaterialAgentReverseAPI(APIView):

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
            agent_admin = cobrowse_io.access_token.agent
            active_agent = cobrowse_io.agent

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
            logger.error("Error GetSupportMaterialAgentReverseAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetSupportMaterialAgentReverse = GetSupportMaterialAgentReverseAPI.as_view()
