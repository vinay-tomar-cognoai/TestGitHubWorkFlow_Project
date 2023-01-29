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
from EasyAssistApp.views_screensharing_cobrowse import *
from EasyAssistApp.views_reverse import *
from EasyAssistApp.views_reverse_client import *
from EasyAssistApp.views_calendar import *
from EasyAssistApp.utils_execute_api_processor import execute_code_with_time_limit


import os
import sys
import json
import jsonpickle
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
import shutil

from operator import itemgetter
from collections import OrderedDict

logger = logging.getLogger(__name__)


@xframe_options_exempt
def SalesAIIframePage(request):

    token_id = request.GET.get("id", None)

    if token_id == None:
        return HttpResponse(status=401)

    cobrowse_access_token = None
    try:
        cobrowse_access_token = CobrowseAccessToken.objects.get(key=token_id)
    except Exception:
        logger.warning("Invalid access token", extra={'AppName': 'EasyAssist'})

    if cobrowse_access_token == None:
        return HttpResponse(status=401)

    eacSession = None
    try:
        existing_value = request.COOKIES.get("eacSession", None)
        eacSession = str(request.GET.get("eacSession", existing_value))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAIIframePage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    response = render(request, "EasyAssistApp/sales-iframe.html", {
        "eacSession": str(eacSession)
    })

    response.set_cookie("eacSession", eacSession)

    return response


@xframe_options_exempt
def SalesAIClientLiveChatWindow(request):
    access_token = CobrowseAccessToken.objects.get(
        key=request.GET["access_token"])
    cobrowse_agent = access_token.agent
    if "session_id" in request.GET:
        cobrowse_io_obj = CobrowseIO.objects.filter(
            session_id=request.GET["session_id"]).first()
        if cobrowse_io_obj:
            cobrowse_agent = cobrowse_io_obj.agent
    enable_s3_bucket = access_token.agent.user.enable_s3_bucket
    floating_button_bg_color = access_token.floating_button_bg_color
    allow_agent_to_customer_cobrowsing = access_token.allow_agent_to_customer_cobrowsing
    share_document_from_livechat = access_token.share_document_from_livechat
    enable_agent_connect_message = access_token.enable_agent_connect_message
    allow_only_support_documents = access_token.allow_only_support_documents
    is_mobile = request.user_agent.is_mobile
    admin_agent = access_token.agent
    canned_responses = []
    commonly_used_canned_resposnse_obj = []
    canned_response_obj = []

    if allow_agent_to_customer_cobrowsing:
        if cobrowse_agent == admin_agent:
            commonly_used_canned_resposnse_obj = AgentFrequentLiveChatCannedResponses.objects.filter(
                agent=cobrowse_agent, access_token=access_token, canned_response__is_deleted=False).order_by("-frequency")
            canned_response_obj = LiveChatCannedResponse.objects.filter(
                access_token=access_token, is_deleted=False).filter(~Q(pk__in=commonly_used_canned_resposnse_obj.values_list("canned_response"))).order_by("keyword")
        else:
            supervisors_list = get_supervisors_of_active_agent(
                cobrowse_agent, CobrowseAgent)
            supervisors_obj = supervisors_list + \
                [cobrowse_agent, admin_agent]
            commonly_used_canned_resposnse_obj = AgentFrequentLiveChatCannedResponses.objects.filter(
                agent__in=supervisors_obj, access_token=access_token, canned_response__is_deleted=False).order_by("-frequency")
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

    return render(request, "EasyAssistApp/client-chatbot.html", {
        "enable_s3_bucket": enable_s3_bucket,
        "floating_button_bg_color": floating_button_bg_color,
        "allow_agent_to_customer_cobrowsing": allow_agent_to_customer_cobrowsing,
        "share_document_from_livechat": share_document_from_livechat,
        "enable_agent_connect_message": enable_agent_connect_message,
        "allow_only_support_documents": allow_only_support_documents,
        "easyassist_font_family": access_token.font_family,
        "display_agent_profile": access_token.display_agent_profile,
        "enable_chat_functionality": access_token.enable_chat_functionality,
        "enable_preview_functionality": access_token.enable_preview_functionality,
        "enable_chat_bubble": access_token.enable_chat_bubble,
        "chat_bubble_icon_source": access_token.chat_bubble_icon_source,
        "is_mobile": is_mobile,
        "canned_responses_list": canned_responses,
        "access_token": access_token.key,
    })


class CobrowseIOInitializeAPI(APIView):

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
                name = strip_html_tags(name)
                longitude = data["longitude"]
                longitude = remo_html_from_string(str(longitude))
                latitude = data["latitude"]
                latitude = remo_html_from_string(str(latitude))
                mobile_number = data["mobile_number"]
                mobile_number = remo_html_from_string(mobile_number)
                mobile_number = remo_special_tag_from_string(mobile_number)
                mobile_number = strip_html_tags(mobile_number)
                selected_language = data["selected_language"]
                selected_product_category = data["selected_product_category"]
                meta_data = data["meta_data"]
                browsing_time_before_connect_click = data["browsing_time_before_connect_click"]

                is_client_in_mobile = False
                try:
                    is_client_in_mobile = request.user_agent.is_mobile
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error CobrowseIOInitializeAPI %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                virtual_agent_selected = None

                if cobrowse_access_token_obj.allow_connect_with_virtual_agent_code:
                    
                    virtual_agent_code = ""
                    if "virtual_agent_code" in data:
                        virtual_agent_code = sanitize_input_string(data["virtual_agent_code"])
                        virtual_agent_code = remo_special_tag_from_string(virtual_agent_code)
                        virtual_agent_code = virtual_agent_code.strip()

                    if cobrowse_access_token_obj.connect_with_virtual_agent_code_mandatory and virtual_agent_code == "":
                        response["status"] = 103
                        response["message"] = "Please enter a valid agent code"
                        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                        
                    if virtual_agent_code != "":
                        virtual_agent_selected = CobrowseAgent.objects.filter(
                            virtual_agent_code=virtual_agent_code).first()

                        if not virtual_agent_selected:
                            response["status"] = 103
                            response["message"] = "Please enter a valid agent code"
                            if not cobrowse_access_token_obj.connect_with_virtual_agent_code_mandatory:
                                response["message"] = "Please enter a valid agent code or continue without a code"
                            return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                        else:
                            if virtual_agent_selected.is_cognomeet_active or virtual_agent_selected.is_cobrowsing_active:
                                response["status"] = 103
                                response["message"] = "Please enter a valid agent code"
                                if not cobrowse_access_token_obj.connect_with_virtual_agent_code_mandatory:
                                    response["message"] = "Please enter a valid agent code or continue without a code"
                                return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                            if cobrowse_access_token_obj.allow_language_support and \
                                    cobrowse_access_token_obj.choose_product_category:

                                response["status"] = 103
                                response[
                                    "message"] = f'Invalid category or language selection. Agent code being used is assigned with "{virtual_agent_selected.get_product_categories()}" and "{virtual_agent_selected.get_supported_languages()}". Please update your selection and try again.'

                                if not virtual_agent_selected.get_product_categories() or \
                                        not virtual_agent_selected.get_supported_languages():
                                    response["message"] = "Unable to raise a request as entered agent code doesn't have any categories or languages assigned to them. Please contact the support team."
                                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                                product_category_obj = ProductCategory.objects.filter(
                                    pk=int(selected_product_category)).first()
                                language_obj = LanguageSupport.objects.filter(
                                    pk=int(selected_language)).first()

                                if not language_obj or not product_category_obj:
                                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                                    
                                if product_category_obj not in virtual_agent_selected.product_category.filter(is_deleted=False) or \
                                        language_obj not in virtual_agent_selected.supported_language.filter(is_deleted=False):
                                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                            elif cobrowse_access_token_obj.choose_product_category:

                                response["status"] = 103
                                response[
                                    "message"] = f'Invalid category selection. Agent code being used is assigned with "{virtual_agent_selected.get_product_categories()}". Please update your selection and try again.'
                                
                                if not virtual_agent_selected.get_product_categories():
                                    response["message"] = "Unable to raise a request as entered agent code doesn't have any categories assigned to them. Please contact the support team."
                                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                                    
                                product_category_obj = ProductCategory.objects.filter(
                                    pk=int(selected_product_category)).first()

                                if not product_category_obj:
                                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                                if product_category_obj not in virtual_agent_selected.product_category.filter(is_deleted=False):
                                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                            elif cobrowse_access_token_obj.allow_language_support:

                                response["status"] = 103
                                response[
                                    "message"] = f'Invalid language selection. Agent code being used is assigned with "{virtual_agent_selected.get_supported_languages()}". Please update your selection and try again.'

                                if not virtual_agent_selected.get_supported_languages():
                                    response["message"] = "Unable to raise a request as entered agent code doesn't have any languages assigned to them. Please contact the support team."
                                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                                
                                language_obj = LanguageSupport.objects.filter(
                                    pk=int(selected_language)).first()

                                if not language_obj:
                                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                                if language_obj not in virtual_agent_selected.supported_language.filter(is_deleted=False):
                                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                    logger.info("Customer connected through virtual agent code %s",
                                virtual_agent_selected, extra={'AppName': 'EasyAssist'})

                if not re.match(r'^[a-zA-Z ]+$', name):
                    response["status"] = 105
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(
                        response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                
                mobile_number = mobile_number.strip().lower()
                if not re.match(r'^([\s\d]+)$', mobile_number):
                    response["status"] = 104
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(
                        response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                
                if "product_details" in meta_data and "url" in meta_data["product_details"]:
                    if is_url_valid(meta_data["product_details"]["url"].strip()) == False:
                        response["status"] = 500
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(
                            response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)
  
                primary_id = hashlib.md5(mobile_number.encode()).hexdigest()

                share_client_session = False
                if "share_client_session" in data and data["share_client_session"] == True:
                    share_client_session = True

                request_meta_details = {
                    "HTTP_USER_AGENT": HTTP_USER_AGENT,
                    "HTTP_X_FORWARDED_FOR": HTTP_X_FORWARDED_FOR
                }

                cobrowse_io = CobrowseIO.objects.create(full_name=name,
                                                        mobile_number=mobile_number,
                                                        share_client_session=share_client_session,
                                                        primary_value=primary_id)

                if str(selected_language) != "-1":
                    cobrowse_io.supported_language = LanguageSupport.objects.get(
                        pk=int(selected_language))

                if str(selected_product_category) != "-1":
                    cobrowse_io.product_category = ProductCategory.objects.get(
                        pk=int(selected_product_category))

                if "product_details" in meta_data and "title" in meta_data["product_details"]:
                    meta_data["product_details"]["title"] = remo_html_from_string(meta_data["product_details"]["title"]).replace("<", "").replace(">", "")
                    cobrowse_io.title = meta_data[
                        "product_details"]["title"].strip()

                if "product_details" in meta_data and "url" in meta_data["product_details"]:
                    cobrowse_io.active_url = meta_data[
                        "product_details"]["url"].strip()

                if "product_details" in meta_data and "description" in meta_data["product_details"]:
                    meta_data["product_details"]["description"] = remo_html_from_string(strip_html_tags(meta_data[
                        "product_details"]["description"].strip()))

                meta_data = json.dumps(meta_data)
                meta_data = custom_encrypt_obj.encrypt(meta_data)
                cobrowse_io.meta_data = meta_data
                cobrowse_io.is_active = True
                cobrowse_io.last_update_datetime = timezone.now()
                cobrowse_io.is_agent_connected = False
                cobrowse_io.cobrowsing_start_datetime = None
                cobrowse_io.latitude = str(latitude)
                cobrowse_io.longitude = str(longitude)
                cobrowse_io.is_client_in_mobile = is_client_in_mobile

                if share_client_session:
                    cobrowse_io.allow_agent_cobrowse = "true"
                elif virtual_agent_selected and not cobrowse_access_token_obj.allow_video_meeting_only:
                    cobrowse_io.allow_agent_cobrowse = "true"

                cobrowse_io.is_lead = False
                cobrowse_io.access_token = cobrowse_access_token_obj
                cobrowse_io.request_meta_details = json.dumps(
                    request_meta_details)
                cobrowse_io.agent = virtual_agent_selected
                cobrowse_io.is_meeting_only_session = cobrowse_access_token_obj.allow_video_meeting_only
                cobrowse_io.browsing_time_before_connect_click = browsing_time_before_connect_click

                if "is_request_from_greeting_bubble" in data and data["is_request_from_greeting_bubble"]:
                    cobrowse_io.lead_initiated_by = "greeting_bubble"
                elif "is_request_from_inactivity_popup" in data and data["is_request_from_inactivity_popup"]:
                    cobrowse_io.lead_initiated_by = "inactivity_popup"
                elif "is_request_from_exit_intent" in data and data["is_request_from_exit_intent"]:
                    cobrowse_io.lead_initiated_by = "exit_intent"
                elif cobrowse_access_token_obj.show_easyassist_connect_agent_icon:
                    cobrowse_io.lead_initiated_by = "icon"
                else:
                    cobrowse_io.lead_initiated_by = "floating_button"

                cobrowse_io.save()

                if "customer_id" in data and data["customer_id"] != "None":
                    try:
                        easyassist_customer = EasyAssistCustomer.objects.get(
                            customer_id=data["customer_id"])
                        easyassist_customer.cobrowse_io = cobrowse_io
                        easyassist_customer.save()
                    except Exception:
                        pass

                if virtual_agent_selected:
                    cobrowse_io.cobrowsing_type = "modified-inbound"
                    cobrowse_io.save(update_fields=["cobrowsing_type"])
                    send_agent_customer_connected_notification(
                        virtual_agent_selected, cobrowse_io)
                
                if 'is_livechat_request' in data:
                    assigned_agent_username = data['assigned_agent_username']
                    cobrowse_agent = CobrowseAgent.objects.filter(user__username=assigned_agent_username)

                    if cobrowse_agent:
                        cobrowse_agent = cobrowse_agent.first()
                        cobrowse_agent.last_lead_assigned_datetime = timezone.now()
                        cobrowse_io.agent = cobrowse_agent

                        if cobrowse_io.access_token.show_verification_code_modal == False:
                            cobrowse_io.allow_agent_cobrowse = 'true'

                        cobrowse_io.last_agent_assignment_datetime = timezone.now()
                        cobrowse_io.is_cobrowsing_from_livechat = True
                        cobrowse_io.save()

                response["session_id"] = str(cobrowse_io.session_id)
                response["status"] = 200
                response["message"] = "success"
                response["sessionid"] = request.session.session_key
                response["csrf"] = csrf.get_token(request)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseIOInitializeAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CobrowseIOInitialize = CobrowseIOInitializeAPI.as_view()


class SaveNonWorkingHourCurstomerDetailAPI(APIView):

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
                longitude = data["longitude"]
                longitude = remo_html_from_string(str(longitude))
                latitude = data["latitude"]
                latitude = remo_html_from_string(str(latitude))
                mobile_number = data["mobile_number"]
                mobile_number = remo_html_from_string(mobile_number)
                mobile_number = remo_special_tag_from_string(mobile_number)
                meta_data = data["meta_data"]
                selected_language = data["selected_language"]
                selected_product_category = data["selected_product_category"]

                virtual_agent_selected = None

                if cobrowse_access_token_obj.allow_connect_with_virtual_agent_code:
                    
                    virtual_agent_code = ""
                    if "virtual_agent_code" in data:
                        virtual_agent_code = sanitize_input_string(data["virtual_agent_code"])
                        virtual_agent_code = remo_special_tag_from_string(virtual_agent_code)
                        virtual_agent_code = virtual_agent_code.strip()

                    if cobrowse_access_token_obj.connect_with_virtual_agent_code_mandatory and virtual_agent_code == "":
                        response["status"] = 103
                        response["message"] = "Please enter a valid agent code"
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(
                            response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)
                        
                    if virtual_agent_code != "":
                        virtual_agent_selected = CobrowseAgent.objects.filter(
                            virtual_agent_code=virtual_agent_code).first()

                        if not virtual_agent_selected:
                            response["status"] = 103
                            response["message"] = "Please enter a valid agent code"
                            if not cobrowse_access_token_obj.connect_with_virtual_agent_code_mandatory:
                                response["message"] = "Please enter a valid agent code or continue without a code"
                            response = json.dumps(response)
                            encrypted_response = custom_encrypt_obj.encrypt(
                                response)
                            response = {"Response": encrypted_response}
                            return Response(data=response)
                        else:
                            if cobrowse_access_token_obj.allow_language_support and \
                                    cobrowse_access_token_obj.choose_product_category:

                                response["status"] = 103
                                response[
                                    "message"] = f'Invalid category or language selection. Agent code being used is assigned with "{virtual_agent_selected.get_product_categories()}" and "{virtual_agent_selected.get_supported_languages()}". Please update your selection and try again.'

                                if not virtual_agent_selected.get_product_categories() or \
                                        not virtual_agent_selected.get_supported_languages():
                                    response["message"] = "Unable to raise a request as entered agent code doesn't have any categories or languages assigned to them. Please contact the support team."
                                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                                product_category_obj = ProductCategory.objects.filter(
                                    pk=int(selected_product_category)).first()
                                language_obj = LanguageSupport.objects.filter(
                                    pk=int(selected_language)).first()

                                if not language_obj or not product_category_obj:
                                    response = json.dumps(response)
                                    encrypted_response = custom_encrypt_obj.encrypt(
                                        response)
                                    response = {"Response": encrypted_response}
                                    return Response(data=response)

                                if product_category_obj not in virtual_agent_selected.product_category.filter(is_deleted=False) or \
                                        language_obj not in virtual_agent_selected.supported_language.filter(is_deleted=False):
                                    response = json.dumps(response)
                                    encrypted_response = custom_encrypt_obj.encrypt(
                                        response)
                                    response = {"Response": encrypted_response}
                                    return Response(data=response)

                            elif cobrowse_access_token_obj.choose_product_category:

                                response["status"] = 103
                                response[
                                    "message"] = f'Invalid category selection. Agent code being used is assigned with "{virtual_agent_selected.get_product_categories()}". Please update your selection and try again.'

                                if not virtual_agent_selected.get_product_categories():
                                    response["message"] = "Unable to raise a request as entered agent code doesn't have any categories assigned to them. Please contact the support team."
                                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                                
                                product_category_obj = ProductCategory.objects.filter(
                                    pk=int(selected_product_category)).first()

                                if not product_category_obj:
                                    response = json.dumps(response)
                                    encrypted_response = custom_encrypt_obj.encrypt(
                                        response)
                                    response = {"Response": encrypted_response}
                                    return Response(data=response)

                                if product_category_obj not in virtual_agent_selected.product_category.filter(is_deleted=False):
                                    response = json.dumps(response)
                                    encrypted_response = custom_encrypt_obj.encrypt(
                                        response)
                                    response = {"Response": encrypted_response}
                                    return Response(data=response)

                            elif cobrowse_access_token_obj.allow_language_support:

                                response["status"] = 103
                                response[
                                    "message"] = f'Invalid language selection. Agent code being used is assigned with "{virtual_agent_selected.get_supported_languages()}". Please update your selection and try again.'

                                if not virtual_agent_selected.get_supported_languages():
                                    response["message"] = "Unable to raise a request as entered agent code doesn't have any languages assigned to them. Please contact the support team."
                                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                                
                                language_obj = LanguageSupport.objects.filter(
                                    pk=int(selected_language)).first()

                                if not language_obj:
                                    response = json.dumps(response)
                                    encrypted_response = custom_encrypt_obj.encrypt(
                                        response)
                                    response = {"Response": encrypted_response}
                                    return Response(data=response)

                                if language_obj not in virtual_agent_selected.supported_language.filter(is_deleted=False):
                                    response = json.dumps(response)
                                    encrypted_response = custom_encrypt_obj.encrypt(
                                        response)
                                    response = {"Response": encrypted_response}
                                    return Response(data=response)

                    logger.info("Request agent to connect in non working hours is %s",
                                virtual_agent_selected, extra={'AppName': 'EasyAssist'})

                mobile_number = mobile_number.strip().lower()
                primary_id = hashlib.md5(mobile_number.encode()).hexdigest()

                share_client_session = False

                request_meta_details = {
                    "HTTP_USER_AGENT": HTTP_USER_AGENT,
                    "HTTP_X_FORWARDED_FOR": HTTP_X_FORWARDED_FOR
                }

                cobrowse_io = CobrowseIO.objects.create(full_name=name,
                                                        mobile_number=mobile_number,
                                                        share_client_session=share_client_session,
                                                        primary_value=primary_id)

                if "product_details" in meta_data and "title" in meta_data["product_details"]:
                    cobrowse_io.title = strip_html_tags(meta_data[
                        "product_details"]["title"].strip())

                if "product_details" in meta_data and "url" in meta_data["product_details"]:
                    cobrowse_io.active_url = meta_data[
                        "product_details"]["url"].strip()

                if "product_details" in meta_data and "description" in meta_data["product_details"]:
                    meta_data["product_details"]["description"] = strip_html_tags(meta_data[
                        "product_details"]["description"].strip())

                if str(selected_language) != "-1":
                    cobrowse_io.supported_language = LanguageSupport.objects.get(
                        pk=int(selected_language))

                if str(selected_product_category) != "-1":
                    cobrowse_io.product_category = ProductCategory.objects.get(
                        pk=int(selected_product_category))

                meta_data = json.dumps(meta_data)
                meta_data = custom_encrypt_obj.encrypt(meta_data)
                cobrowse_io.meta_data = meta_data
                cobrowse_io.is_active = False
                cobrowse_io.is_archived = True
                cobrowse_io.last_update_datetime = timezone.now()
                cobrowse_io.is_agent_connected = False
                cobrowse_io.cobrowsing_start_datetime = None
                cobrowse_io.latitude = str(latitude)
                cobrowse_io.longitude = str(longitude)

                cobrowse_io.is_lead = False
                cobrowse_io.access_token = cobrowse_access_token_obj
                cobrowse_io.request_meta_details = json.dumps(
                    request_meta_details)
                cobrowse_io.agent = virtual_agent_selected

                if cobrowse_io.session_archived_cause == None:
                    cobrowse_io.session_archived_cause = "FOLLOWUP"
                    cobrowse_io.session_archived_datetime = timezone.now()

                if "is_request_from_greeting_bubble" in data and data["is_request_from_greeting_bubble"]:
                    cobrowse_io.lead_initiated_by = "greeting_bubble"
                elif "is_request_from_inactivity_popup" in data and data["is_request_from_inactivity_popup"]:
                    cobrowse_io.lead_initiated_by = "inactivity_popup"
                elif "is_request_from_exit_intent" in data and data["is_request_from_exit_intent"]:
                    cobrowse_io.lead_initiated_by = "exit_intent"
                elif cobrowse_access_token_obj.show_easyassist_connect_agent_icon:
                    cobrowse_io.lead_initiated_by = "icon"
                else:
                    cobrowse_io.lead_initiated_by = "floating_button"

                if virtual_agent_selected:
                    cobrowse_io.cobrowsing_type = "modified-inbound"
                
                cobrowse_io.save()

                if "customer_id" in data and data["customer_id"] != "None":
                    try:
                        easyassist_customer = EasyAssistCustomer.objects.get(
                            customer_id=data["customer_id"])
                        easyassist_customer.cobrowse_io = cobrowse_io
                        easyassist_customer.save()
                    except Exception:
                        pass

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveNonWorkingHourCurstomerDetailAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveNonWorkingHourCurstomerDetail = SaveNonWorkingHourCurstomerDetailAPI.as_view()


class CobrowseIOInitializeUsingDroplinkAPI(APIView):

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

                drop_link_key = data["drop_link_key"]
                longitude = data["longitude"]
                latitude = data["latitude"]
                active_url = data["active_url"]
                meta_data = data["meta_data"]

                drop_link_key = remo_html_from_string(drop_link_key)
                longitude = remo_html_from_string(str(longitude))
                latitude = remo_html_from_string(str(latitude))
                active_url = remo_html_from_string(active_url)

                cobrowse_drop_link_obj = None

                try:
                    cobrowse_drop_link_obj = CobrowseDropLink.objects.filter(
                        key=str(drop_link_key)).first()
                except Exception:
                    pass

                if cobrowse_drop_link_obj is not None:
                    name = cobrowse_drop_link_obj.customer_name
                    mobile_number = cobrowse_drop_link_obj.customer_mobile
                    agent_selected = cobrowse_drop_link_obj.agent

                    primary_id = hashlib.md5(
                        mobile_number.encode()).hexdigest()

                    share_client_session = False
                    if "share_client_session" in data and data["share_client_session"] == True:
                        share_client_session = True

                    request_meta_details = {
                        "HTTP_USER_AGENT": HTTP_USER_AGENT,
                        "HTTP_X_FORWARDED_FOR": HTTP_X_FORWARDED_FOR
                    }

                    cobrowse_io = cobrowse_drop_link_obj.cobrowse_io

                    if cobrowse_io == None:
                        
                        cobrowse_io = CobrowseIO.objects.create(full_name=name,
                                                                mobile_number=mobile_number,
                                                                share_client_session=share_client_session,
                                                                primary_value=primary_id)

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
                        cobrowse_io.is_active = True
                        cobrowse_io.last_update_datetime = timezone.now()
                        cobrowse_io.is_agent_connected = False
                        cobrowse_io.cobrowsing_start_datetime = None
                        cobrowse_io.latitude = str(latitude)
                        cobrowse_io.longitude = str(longitude)

                        cobrowse_io.is_lead = False
                        cobrowse_io.access_token = cobrowse_access_token_obj
                        cobrowse_io.request_meta_details = json.dumps(
                            request_meta_details)
                        cobrowse_io.agent = agent_selected
                        if cobrowse_access_token_obj.show_verification_code_modal == False:
                            cobrowse_io.allow_agent_cobrowse = "true"
                        else:
                            otp = random_with_n_digits(4)
                            cobrowse_io.otp_validation = otp
                            cobrowse_io.agent_assistant_request_status = True
                            cobrowse_io.is_agent_request_for_cobrowsing = True

                        cobrowse_io.is_droplink_lead = True
                        cobrowse_io.is_meeting_only_session = cobrowse_access_token_obj.allow_video_meeting_only
                        cobrowse_io.save()

                        cobrowse_drop_link_obj.cobrowse_io = cobrowse_io
                    cobrowse_drop_link_obj.save()

                    if "customer_id" in data and data["customer_id"] != "None":
                        try:
                            easyassist_customer = EasyAssistCustomer.objects.get(
                                customer_id=data["customer_id"])
                            easyassist_customer.cobrowse_io = cobrowse_io
                            easyassist_customer.save()
                        except Exception:
                            pass

                    send_agent_customer_connected_notification(
                        agent_selected, cobrowse_io)

                    response["session_id"] = str(cobrowse_io.session_id)
                    response["status"] = 200
                    response["message"] = "success"
                    response["csrf"] = csrf.get_token(request)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseIOInitializeUsingDroplinkAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CobrowseIOInitializeUsingDroplink = CobrowseIOInitializeUsingDroplinkAPI.as_view()


def InitiateDropLinkSession(request):
    try:
        drop_link_key = ""
        if "eadKey" in request.GET:
            drop_link_key = request.GET["eadKey"]

        cobrowse_drop_link_obj = None

        if drop_link_key != "":
            try:
                cobrowse_drop_link_obj = CobrowseDropLink.objects.filter(
                    key=str(drop_link_key)).first()
            except Exception:
                pass

            if cobrowse_drop_link_obj is not None:
                if cobrowse_drop_link_obj.is_link_valid():
                    client_page_link = cobrowse_drop_link_obj.client_page_link
                    session_link = client_page_link
                    first_index = client_page_link.find("?")
                    if first_index < 0:
                        session_link += "?eadKey=" + str(cobrowse_drop_link_obj.key)
                    else:
                        session_link += "&eadKey=" + str(cobrowse_drop_link_obj.key)
                    return redirect(session_link)
                else:
                    return render(request, "EasyAssistApp/drop_link_expired.html", {
                        "cobrowse_agent": cobrowse_drop_link_obj.agent,
                        "meeting_expiry_time": cobrowse_drop_link_obj.agent.get_access_token_obj().drop_link_expiry_time,
                    })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error InitiateDropLinkSession %s at %s",
                        str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


class EasyAssistCustomerSetAPI(APIView):

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

                meta_data = data["meta_data"]

                easyassist_customer_id = data["easyassist_customer_id"]
                full_name = data["full_name"]
                mobile_number = data["mobile_number"]

                full_name = remo_html_from_string(full_name)
                mobile_number = remo_html_from_string(mobile_number)
                easyassist_customer = None
                try:
                    easyassist_customer = EasyAssistCustomer.objects.get(
                        customer_id=easyassist_customer_id)
                except Exception:
                    easyassist_customer = EasyAssistCustomer.objects.create()

                if "product_details" in meta_data and "title" in meta_data["product_details"]:
                    easyassist_customer.title = strip_html_tags(meta_data[
                        "product_details"]["title"].strip())

                if "product_details" in meta_data and "url" in meta_data["product_details"]:
                    easyassist_customer.active_url = meta_data[
                        "product_details"]["url"].strip()

                if "product_details" in meta_data and "description" in meta_data["product_details"]:
                    meta_data["product_details"]["description"] = strip_html_tags(meta_data[
                        "product_details"]["description"].strip())

                meta_data = json.dumps(meta_data)
                meta_data = custom_encrypt_obj.encrypt(meta_data)
                easyassist_customer.meta_data = meta_data

                request_meta_details = {
                    "HTTP_USER_AGENT": HTTP_USER_AGENT,
                    "HTTP_X_FORWARDED_FOR": HTTP_X_FORWARDED_FOR
                }

                if full_name != "None" and full_name != "":
                    easyassist_customer.full_name = full_name
                if mobile_number != "None" and mobile_number != "":
                    easyassist_customer.mobile_number = mobile_number
                easyassist_customer.access_token = cobrowse_access_token_obj
                easyassist_customer.request_meta_details = json.dumps(
                    request_meta_details)

                if "is_request_from_greeting_bubble" in data and data["is_request_from_greeting_bubble"]:
                    easyassist_customer.lead_initiated_by = "greeting_bubble"
                elif "is_request_from_inactivity_popup" in data and data["is_request_from_inactivity_popup"]:
                    easyassist_customer.lead_initiated_by = "inactivity_popup"
                elif "is_request_from_exit_intent" in data and data["is_request_from_exit_intent"]:
                    easyassist_customer.lead_initiated_by = "exit_intent"
                elif "is_request_from_button" in data and data["is_request_from_button"]:
                    easyassist_customer.lead_initiated_by = "floating_button"
                else:
                    easyassist_customer.lead_initiated_by = "icon"
                easyassist_customer.save()

                response["customer_id"] = str(easyassist_customer.customer_id)
                response["status"] = 200
                response["message"] = "success"
                response["csrf"] = csrf.get_token(request)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EasyAssistCustomerSetAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


EasyAssistCustomerSet = EasyAssistCustomerSetAPI.as_view()


class SyncCobrowseIOAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            # HTTP_X_FORWARDED_FOR = None
            # if settings.ENABLE_IP_TRACKING:
            #     HTTP_X_FORWARDED_FOR = request.META["HTTP_X_FORWARDED_FOR"]
            #     HTTP_USER_AGENT = request.META["HTTP_USER_AGENT"]

            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            origin = get_request_origin(request)

            auth_params = extract_authorization_params(request)

            if auth_params == None:
                return Response(status=401)
            elif cobrowse_access_token_obj == None and False:
                return Response(status=401)
            elif False and (not is_valid_domain(request, origin, cobrowse_access_token_obj)):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                id = data["id"]
                id = remo_html_from_string(id)

                if auth_params[0] != id:
                    return Response(status=401)

                html = data["html"]
                active_url = data["active_url"]
                html = convert_absolute_path_in_html(html, active_url)

                cobrowse_io = CobrowseIO.objects.get(session_id=id)
                cobrowse_io.html = html
                cobrowse_io.is_active = True
                cobrowse_io.is_updated = True
                cobrowse_io.save()

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SyncCobrowseIOAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SyncCobrowseIO = SyncCobrowseIOAPI.as_view()


class HighlightCheckCobrowseIOAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            # HTTP_X_FORWARDED_FOR = None
            # if settings.ENABLE_IP_TRACKING:
            #     HTTP_X_FORWARDED_FOR = request.META["HTTP_X_FORWARDED_FOR"]
            #     HTTP_USER_AGENT = request.META["HTTP_USER_AGENT"]

            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            origin = get_request_origin(request)

            auth_params = extract_authorization_params(request)

            if auth_params == None:
                return Response(status=401)
            if cobrowse_access_token_obj == None:
                return Response(status=401)
            elif not is_valid_domain(request, origin, cobrowse_access_token_obj):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                id = data["id"]
                id = remo_html_from_string(id)

                if auth_params[0] != id:
                    return Response(status=401)

                cobrowse_io = CobrowseIO.objects.get(session_id=id)
                
                drop_off_meta_data = data["drop_off_meta_data"]
                
                if "product_details" in drop_off_meta_data and "url" in drop_off_meta_data["product_details"]:
                    if is_url_valid(drop_off_meta_data["product_details"]["url"].strip()) == False:
                        drop_off_meta_data["product_details"]["url"] = ""
                        
                if "product_details" in drop_off_meta_data and "title" in drop_off_meta_data["product_details"]:
                    drop_off_meta_data["product_details"]["title"] = remo_html_from_string(drop_off_meta_data["product_details"]["title"]).replace("<", "").replace(">", "")
                    
                drop_off_meta_data = json.dumps(drop_off_meta_data)
                drop_off_meta_data = custom_encrypt_obj.encrypt(drop_off_meta_data)
                cobrowse_io.drop_off_meta_data = drop_off_meta_data
                cobrowse_io.save()
                
                is_session_closed = False

                if cobrowse_io.is_active_timer() == False:
                    if cobrowse_io.cobrowsing_start_datetime:
                        cobrowse_io.is_active = False
                        is_session_closed = True
                        logger.info("Closing cobrowsing session due to inactivity...", extra={'AppName': 'EasyAssist'})
                    else:
                        cobrowse_io.is_active = False
                        is_session_closed = True
                        logger.info("Closing cobrowsing session not started...", extra={'AppName': 'EasyAssist'})
                else:
                    cobrowse_io.is_active = True
                    cobrowse_io.last_update_datetime = timezone.now()

                cobrowse_io.is_updated = True
                cobrowse_io.save()

                agent_name = None
                if cobrowse_io.agent != None:
                    agent_name = str(cobrowse_io.agent.user.first_name)
                    if agent_name.strip() == "" or agent_name == "None":
                        agent_name = str(cobrowse_io.agent.user.username)

                session_ended_by_agent = False
                if cobrowse_io.session_archived_cause == "AGENT_ENDED" or cobrowse_io.session_archived_cause == "AGENT_INACTIVITY":
                    session_ended_by_agent = True

                cobrowsing_start_datetime = None

                if cobrowse_io.cobrowsing_start_datetime != None:
                    est = pytz.timezone(settings.TIME_ZONE)
                    cobrowsing_start_datetime = cobrowse_io.cobrowsing_start_datetime.astimezone(
                        est).strftime("%d %b %Y %I:%M:%S %p")
                
                meeting_start_datetime = None

                if cobrowse_io.meeting_start_datetime:
                    est = pytz.timezone(settings.TIME_ZONE)
                    meeting_start_datetime = cobrowse_io.meeting_start_datetime.astimezone(
                        est).strftime("%d %b %Y %I:%M:%S %p")

                session_archived_datetime = None
                is_unassigned_lead = False

                if cobrowse_io.session_archived_datetime != None:
                    est = pytz.timezone(settings.TIME_ZONE)
                    session_archived_datetime = cobrowse_io.session_archived_datetime.astimezone(
                        est).strftime("%d %b %Y %I:%M:%S %p ")

                if cobrowse_io.is_lead == False and cobrowse_io.session_archived_cause == "UNASSIGNED":
                    is_unassigned_lead = True

                notify_client_about_reassignment = False
                is_auto_reassign_enabled = cobrowse_access_token_obj.enable_auto_assign_unattended_lead
                auto_assign_unattended_lead_message = cobrowse_access_token_obj.auto_assign_unattended_lead_message
                auto_assign_lead_end_session_message = cobrowse_access_token_obj.auto_assign_lead_end_session_message
                archive_message_on_unassigned_time_threshold = cobrowse_access_token_obj.archive_message_on_unassigned_time_threshold

                if is_auto_reassign_enabled:
                    if cobrowse_io.is_customer_notified == False and cobrowse_io.lead_reassignment_counter != 0:
                        notify_client_about_reassignment = True
                        cobrowse_io.is_customer_notified = True
                        cobrowse_io.save()

                response["is_agent_connected"] = cobrowse_io.is_agent_active_timer(
                ) and cobrowse_io.is_agent_connected
                response["agent_name"] = agent_name
                response["session_ended_by_agent"] = session_ended_by_agent
                response[
                    "agent_assistant_request_status"] = cobrowse_io.agent_assistant_request_status
                response["allow_agent_cobrowse"] = cobrowse_io.allow_agent_cobrowse
                response[
                    "agent_meeting_request_status"] = cobrowse_io.agent_meeting_request_status
                response["cobrowsing_start_datetime"] = cobrowsing_start_datetime
                response["meeting_start_datetime"] = meeting_start_datetime
                response["session_archived_datetime"] = session_archived_datetime
                response["is_unassigned_lead"] = is_unassigned_lead
                response["allow_agent_meeting"] = cobrowse_io.allow_agent_meeting
                response["is_lead"] = cobrowse_io.is_lead
                response["is_archived"] = cobrowse_io.is_archived
                response["is_session_closed"] = is_session_closed
                response["is_auto_reassign_enabled"] = is_auto_reassign_enabled
                response["notify_client_about_reassignment"] = notify_client_about_reassignment
                response["auto_assign_unattended_lead_message"] = auto_assign_unattended_lead_message
                response["auto_assign_lead_end_session_message"] = auto_assign_lead_end_session_message
                response["archive_message_on_unassigned_time_threshold"] = archive_message_on_unassigned_time_threshold
                response['is_cobrowsing_from_livechat'] = cobrowse_io.is_cobrowsing_from_livechat
                response["is_modified_inbound_session"] = True if cobrowse_io.cobrowsing_type == "modified-inbound" else False
                response["status"] = 200
                response["message"] = "success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error HighlightCheckCobrowseIOAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


HighlightCheckCobrowseIO = HighlightCheckCobrowseIOAPI.as_view()


class CobrowseIOCloseSessionAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            # HTTP_X_FORWARDED_FOR = None
            # if settings.ENABLE_IP_TRACKING:
            #     HTTP_X_FORWARDED_FOR = request.META["HTTP_X_FORWARDED_FOR"]
            #     HTTP_USER_AGENT = request.META["HTTP_USER_AGENT"]

            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            origin = get_request_origin(request)

            auth_params = extract_authorization_params(request)

            if auth_params == None:
                return Response(status=401)
            if cobrowse_access_token_obj == None:
                return Response(status=401)
            elif not is_valid_domain(request, origin, cobrowse_access_token_obj):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)
                id = data["id"]
                id = remo_html_from_string(id)

                if auth_params[0] != id:
                    return Response(status=401)

                cobrowse_io = CobrowseIO.objects.get(session_id=id)
                cobrowse_io.is_active = False
                cobrowse_io.last_update_datetime = timezone.now()
                cobrowse_io.save()

                category = "session_closed"
                description = "Session is closed by customer"
                save_system_audit_trail(
                    category, description, cobrowse_io, cobrowse_access_token_obj, SystemAuditTrail, None)

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseIOCloseSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CobrowseIOCloseSession = CobrowseIOCloseSessionAPI.as_view()


class CobrowseIOCaptureClientScreenAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            # HTTP_X_FORWARDED_FOR = None
            # if settings.ENABLE_IP_TRACKING:
            #     HTTP_X_FORWARDED_FOR = request.META["HTTP_X_FORWARDED_FOR"]
            #     HTTP_USER_AGENT = request.META["HTTP_USER_AGENT"]

            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            origin = get_request_origin(request)

            auth_params = extract_authorization_params(request)

            if auth_params == None:
                return Response(status=401)
            if cobrowse_access_token_obj == None:
                return Response(status=401)
            elif not is_valid_domain(request, origin, cobrowse_access_token_obj):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)
                id = data["id"]
                id = remo_html_from_string(id)

                if auth_params[0] != id:
                    return Response(status=401)

                content = data["content"]
                type_screenshot = data["type_screenshot"]
                type_screenshot = remo_html_from_string(type_screenshot)
                cobrowse_io = CobrowseIO.objects.get(session_id=id)

                client_screen_root_dir = "client-screens"

                easyassist_dir = settings.BASE_DIR + '/secured_files/EasyAssistApp/'
                if not os.path.exists(EASYASSISTAPP_SECURED_FILES_PATH + client_screen_root_dir):
                    os.makedirs(EASYASSISTAPP_SECURED_FILES_PATH +
                                client_screen_root_dir)

                image_screen_dir = client_screen_root_dir + \
                    "/" + str(cobrowse_io.session_id)

                if not os.path.exists(EASYASSISTAPP_SECURED_FILES_PATH + image_screen_dir):
                    os.makedirs(EASYASSISTAPP_SECURED_FILES_PATH +
                                image_screen_dir)

                if type_screenshot == "pageshot":

                    pageshot_filepath = image_screen_dir + \
                        "/" + str(int(time.time())) + ".html"
                    pageshot_file = open(
                        easyassist_dir + pageshot_filepath, "w")
                    pageshot_file.write(content)
                    pageshot_file.close()

                    CobrowsingSessionMetaData.objects.create(cobrowse_io=cobrowse_io,
                                                             type_screenshot=type_screenshot,
                                                             content=easyassist_dir + pageshot_filepath)
                elif type_screenshot == "screenshot":

                    format, imgstr = content.split(';base64,')
                    ext = format.split('/')[-1]
                    image_name = str(int(time.time())) + "." + str(ext)

                    image_path = EASYASSISTAPP_SECURED_FILES_PATH + image_screen_dir + "/" + image_name

                    fh = open(image_path, "wb")
                    fh.write(base64.b64decode(imgstr))
                    fh.close()

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


CobrowseIOCaptureClientScreen = CobrowseIOCaptureClientScreenAPI.as_view()


class CobrowseIOCaptureLeadAPI(APIView): 

    def post(self, request, *args, **kwargs):
        logger.info("Inside CobrowseIOCaptureLeadAPI",
                    extra={'AppName': 'EasyAssist'})
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:

            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            origin = get_request_origin(request)

            if cobrowse_access_token_obj == None:
                return Response(status=401)
            elif not is_valid_domain(request, origin, cobrowse_access_token_obj):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)
                logger.info("Request: " + json.dumps(data),
                            extra={'AppName': 'EasyAssist'})

                primary_value_list = data["primary_value_list"]
                session_id = data["session_id"]
                session_id = remo_html_from_string(session_id)
                meta_data = data["meta_data"]
                selected_product_category = "-1"
                if "selected_product_category" in data:
                    selected_product_category = data["selected_product_category"]

                cobrowse_io = None
                cobrowsing_new_sesion = False
                if session_id != "None":
                    cobrowse_io = CobrowseIO.objects.filter(
                        session_id=session_id, is_archived=False).first()
                    if cobrowse_io == None:
                        session_id = "None"

                if session_id == "None":
                    cobrowse_io = CobrowseIO.objects.create(is_lead=True)
                    cobrowse_io.access_token = cobrowse_access_token_obj
                    cobrowse_io.request_datetime = timezone.now()
                    cobrowse_io.is_agent_connected = False
                    cobrowse_io.product_category = cobrowse_access_token_obj.agent.product_category.filter(
                        title__iexact=selected_product_category, is_deleted=False).first()
                    cobrowse_io.is_meeting_only_session = cobrowse_access_token_obj.allow_video_meeting_only
                    cobrowsing_new_sesion = True

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
                cobrowse_io.save()
                check_and_update_lead(
                    primary_value_list, meta_data, cobrowse_io, CobrowseCapturedLeadData)
                response["status"] = 200
                response["message"] = "success"
                response["session_id"] = str(cobrowse_io.session_id)
                response["cobrowsing_new_sesion"] = cobrowsing_new_sesion
                logger.info("Response: " + json.dumps(response),
                            extra={'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseIOCaptureLeadAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        logger.info("Successfully exited from CobrowseIOCaptureLeadAPI", extra={
                    'AppName': 'EasyAssist'})
        return Response(data=response)


CobrowseIOCaptureLead = CobrowseIOCaptureLeadAPI.as_view()


class UpdateAgentAssistantRequestAPI(APIView):

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
            elif not is_valid_domain(request, origin, cobrowse_access_token_obj):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)
                id = data["id"]
                id = remo_html_from_string(id)

                if auth_params[0] != id:
                    return Response(status=401)

                otp = data["otp"]
                otp = remo_html_from_string(otp)
                otp = remo_special_tag_from_string(otp)
                cobrowse_io = CobrowseIO.objects.get(session_id=id)

                if cobrowse_io.access_token.enable_verification_code_popup == False:
                    cobrowse_io.otp_validation = "None"

                if data["status"] == "true" and cobrowse_io.otp_validation != otp:
                    response["status"] = 101
                    response["message"] = "Invalid OTP"
                else:
                    cobrowse_io.agent_assistant_request_status = False

                    if data["status"] == "true":
                        cobrowse_io.allow_agent_cobrowse = "true"
                        cobrowse_io.consent_allow_count = cobrowse_io.consent_allow_count + 1
                        description = "Cobrowsing request accepted by customer"
                    elif data["status"] == "false":
                        cobrowse_io.allow_agent_cobrowse = "false"
                        cobrowse_io.consent_cancel_count = cobrowse_io.consent_cancel_count + 1
                        description = "Cobrowsing request declined by customer"

                    category = "session_details"
                    save_system_audit_trail(
                        category, description, cobrowse_io, cobrowse_access_token_obj, SystemAuditTrail, None)

                    cobrowse_io.save()
                    response["status"] = 200
                    response["message"] = "success"
                    response["cobrowsing_allowed"] = data["status"]
                    response[
                        "allow_screen_sharing_cobrowse"] = cobrowse_access_token_obj.allow_screen_sharing_cobrowse
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateAgentAssistantRequestAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateAgentAssistantRequest = UpdateAgentAssistantRequestAPI.as_view()


class UpdateAgentMeetingRequestAPI(APIView):

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
                id = data["id"]

                if auth_params[0] != id:
                    return Response(status=401)

                cobrowse_io = CobrowseIO.objects.get(session_id=id)

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
                save_system_audit_trail(
                    category, description, cobrowse_io, cobrowse_access_token_obj, SystemAuditTrail, None)

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


UpdateAgentMeetingRequest = UpdateAgentMeetingRequestAPI.as_view()


class SubmitClientFeedbackAPI(APIView):

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
            elif not is_valid_domain(request, origin, cobrowse_access_token_obj):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                session_id = data["session_id"]
                session_id = remo_html_from_string(session_id)

                if auth_params[0] != session_id:
                    return Response(status=401)

                feedback = data["feedback"]
                feedback = remo_html_from_string(feedback)
                feedback = remo_special_tag_from_string(feedback)
                rating = data["rating"]

                cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
                cobrowse_io.is_active = False
                cobrowse_io.client_comments = feedback
                
                drop_off_meta_data = data["drop_off_meta_data"]
                
                if "product_details" in drop_off_meta_data and "url" in drop_off_meta_data["product_details"]:
                    if is_url_valid(drop_off_meta_data["product_details"]["url"].strip()) == False:
                        drop_off_meta_data["product_details"]["url"] = ""
                        
                if "product_details" in drop_off_meta_data and "title" in drop_off_meta_data["product_details"]:
                    drop_off_meta_data["product_details"]["title"] = remo_html_from_string(drop_off_meta_data["product_details"]["title"]).replace("<", "").replace(">", "")
                    
                drop_off_meta_data = json.dumps(drop_off_meta_data)
                drop_off_meta_data = custom_encrypt_obj.encrypt(drop_off_meta_data)
                cobrowse_io.drop_off_meta_data = drop_off_meta_data
                cobrowse_io.save()

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

                if not cobrowse_io.is_archived:
                    update_virtual_agent_code(cobrowse_io)
                    cobrowse_io.last_update_datetime = timezone.now()

                cobrowse_io.client_session_end_time = timezone.now()
                cobrowse_io.is_archived = True
                if cobrowse_io.session_archived_cause == None:
                    cobrowse_io.session_archived_cause = "CLIENT_ENDED"
                    cobrowse_io.session_archived_datetime = timezone.now()
                cobrowse_io.save()
                logger.info("Client feedback has beed saved successfully.", extra={
                            'AppName': 'EasyAssist'})

                meeting_io = CobrowseVideoConferencing.objects.filter(
                    meeting_id=session_id, is_expired=False).first()

                if meeting_io:
                    meeting_io.is_expired = True
                    meeting_io.save()

                    try:
                        meeting_audit_trail = CobrowseVideoAuditTrail.objects.get(
                            cobrowse_video=meeting_io)
                        meeting_audit_trail.meeting_ended = timezone.now()
                        meeting_audit_trail.is_meeting_ended = True
                        meeting_audit_trail.save()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Error SubmitClientFeedbackAPI %s at %s",
                                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                category = "session_closed"
                description = "Session is closed by customer after submitting feedback"
                save_system_audit_trail(
                    category, description, cobrowse_io, cobrowse_access_token_obj, SystemAuditTrail, None)
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SubmitClientFeedbackAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SubmitClientFeedback = SubmitClientFeedbackAPI.as_view()


class ClientAuthenticationAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            key = data["key"]
            key = remo_html_from_string(key)

            cobrowse_access_token = CobrowseAccessToken.objects.get(key=key)
            popup_configurations_obj = get_easyassist_popup_configurations_obj(
                cobrowse_access_token, EasyAssistPopupConfigurations)
            
            origin = get_request_origin(request)
            if is_valid_domain(request, origin, cobrowse_access_token) and cobrowse_access_token.is_active:

                if "page_url" in data and 'page_title' in data:
                    try:

                        page_url = data['page_url'].strip()
                        page_title = data['page_title'].strip()
                        page_title = remo_html_from_string(page_title)

                        page_visit_obj = CobrowsePageVisitCount.objects.filter(
                            cobrowse_access_token=cobrowse_access_token, page_url=page_url, page_title=page_title, page_visit_date=timezone.now().date())[0]
                        page_visit_obj.page_count += 1

                        page_visit_obj.save()
                    except Exception:
                        logger.info("Page Visit Object doesnot exist in ClientAuthenticationAPI", extra={
                            'AppName': 'EasyAssist'})

                        page_visit_obj = CobrowsePageVisitCount.objects.create(
                            cobrowse_access_token=cobrowse_access_token, page_url=page_url, page_title=page_title, page_count=1)

                non_working_hours_message = cobrowse_access_token.message_on_non_working_hours

                if len(non_working_hours_message) == 0:
                    non_working_hours_message = NON_WORKING_HOURS_MESSAGE

                response[
                    "easyassist_host_protocol"] = settings.EASYASSIST_HOST_PROTOCOL
                response["easyassist_host"] = settings.EASYASSISTAPP_HOST
                response["enable_s3_bucket"] = cobrowse_access_token.agent.user.enable_s3_bucket
                response["allow_cobrowsing"] = False

                # This data is not required as of now. 
                # response["username"] = cobrowse_access_token.agent.user.username
                response["enable_location"] = cobrowse_access_token.enable_location
                response[
                    "show_floating_easyassist_button"] = cobrowse_access_token.show_floating_easyassist_button
                response[
                    "show_easyassist_connect_agent_icon"] = cobrowse_access_token.show_easyassist_connect_agent_icon
                response[
                    "source_easyassist_connect_agent_icon"] = cobrowse_access_token.source_easyassist_connect_agent_icon
                response[
                    "field_stuck_event_handler"] = cobrowse_access_token.field_stuck_event_handler
                response[
                    "show_only_if_agent_available"] = cobrowse_access_token.show_only_if_agent_available
                response[
                    "field_recursive_stuck_event_check"] = cobrowse_access_token.field_recursive_stuck_event_check
                response[
                    "get_sharable_link"] = cobrowse_access_token.get_sharable_link
                response["lead_generation"] = cobrowse_access_token.lead_generation
                response[
                    "field_stuck_timer"] = cobrowse_access_token.field_stuck_timer
                response["toast_timeout"] = COBROWSE_TOAST_TIMEOUT
                response["browser_tab_switch_timer"] = 120000

                response["proxy_server"] = ""
                if cobrowse_access_token.proxy_server != None and cobrowse_access_token.proxy_server != "":
                    response["proxy_server"] = cobrowse_access_token.proxy_server

                response["connect_message"] = cobrowse_access_token.connect_message
                response["assist_message"] = cobrowse_access_token.assist_message
                response["meeting_message"] = cobrowse_access_token.meeting_message
                response[
                    "floating_button_position"] = cobrowse_access_token.floating_button_position
                response[
                    "floating_button_bg_color"] = cobrowse_access_token.floating_button_bg_color
                response["strip_js"] = cobrowse_access_token.strip_js
                response["is_socket"] = cobrowse_access_token.is_socket
                response["access_token"] = str(cobrowse_access_token.key)
                response["blocked_html_tags"] = list(
                    cobrowse_access_token.blacklisted_tags.values_list('tag', flat=True))
                response["masking_type"] = cobrowse_access_token.masking_type
                response["search_html_field"] = {

                }
                response[
                    "urls_list_lead_converted"] = cobrowse_access_token.get_url_list_where_consider_lead_converted()
                response[
                    "restricted_urls_list"] = cobrowse_access_token.get_restricted_urls_list()
                # response["start_time"] = cobrowse_access_token.get_start_time()
                # response["end_time"] = cobrowse_access_token.get_end_time()
                response[
                    "enable_verification_code_popup"] = cobrowse_access_token.enable_verification_code_popup
                response[
                    "show_verification_code_modal"] = cobrowse_access_token.show_verification_code_modal
                response[
                    "disable_connect_button_if_agent_unavailable"] = cobrowse_access_token.disable_connect_button_if_agent_unavailable
                response[
                    "message_if_agent_unavailable"] = cobrowse_access_token.message_if_agent_unavailable
                response[
                    "message_on_non_working_hours"] = non_working_hours_message
                response[
                    "show_connect_confirmation_modal"] = cobrowse_access_token.show_connect_confirmation_modal
                response[
                    "message_on_connect_confirmation_modal"] = cobrowse_access_token.message_on_connect_confirmation_modal
                response[
                    "ask_client_mobile"] = cobrowse_access_token.ask_client_mobile
                response[
                    "is_client_mobile_mandatory"] = cobrowse_access_token.is_client_mobile_mandatory
                response[
                    "allow_popup_on_browser_leave"] = cobrowse_access_token.allow_popup_on_browser_leave
                response[
                    "no_of_times_exit_intent_popup"] = cobrowse_access_token.no_of_times_exit_intent_popup
                response[
                    "enable_recursive_browser_leave_popup"] = cobrowse_access_token.enable_recursive_browser_leave_popup
                response[
                    "allow_connect_with_virtual_agent_code"] = cobrowse_access_token.allow_connect_with_virtual_agent_code
                response[
                    "connect_with_virtual_agent_code_mandatory"] = cobrowse_access_token.connect_with_virtual_agent_code_mandatory
                response[
                    "allow_connect_with_drop_link"] = cobrowse_access_token.allow_connect_with_drop_link
                response[
                    "highlight_api_call_frequency"] = cobrowse_access_token.highlight_api_call_frequency
                response[
                    "floating_button_left_right_position"] = cobrowse_access_token.floating_button_left_right_position
                response[
                    "message_on_choose_product_category_modal"] = cobrowse_access_token.message_on_choose_product_category_modal
                response[
                    "allow_file_verification"] = cobrowse_access_token.allow_file_verification
                response[
                    "allow_agent_to_customer_cobrowsing"] = cobrowse_access_token.allow_agent_to_customer_cobrowsing
                response["enable_waitlist"] = cobrowse_access_token.enable_waitlist
                response[
                    "show_floating_button_on_enable_waitlist"] = cobrowse_access_token.show_floating_button_on_enable_waitlist
                response[
                    "enable_masked_field_warning"] = cobrowse_access_token.enable_masked_field_warning
                response[
                    "masked_field_warning_text"] = cobrowse_access_token.masked_field_warning_text
                response[
                    "allow_video_meeting_only"] = cobrowse_access_token.allow_video_meeting_only
                response[
                    "enable_voip_with_video_calling"] = cobrowse_access_token.enable_voip_with_video_calling
                response[
                    "voip_with_video_calling_message"] = cobrowse_access_token.voip_with_video_calling_message
                response[
                    "enable_voip_calling"] = cobrowse_access_token.enable_voip_calling
                response[
                    "voip_calling_message"] = cobrowse_access_token.voip_calling_message
                response[
                    "allow_agent_to_screen_record_customer_cobrowsing"] = cobrowse_access_token.allow_agent_to_screen_record_customer_cobrowsing
                response[
                    "allow_agent_to_audio_record_customer_cobrowsing"] = cobrowse_access_token.allow_agent_to_audio_record_customer_cobrowsing
                response[
                    "enable_optimized_cobrowsing"] = cobrowse_access_token.enable_optimized_cobrowsing
                response[
                    "cobrowsing_sync_html_interval"] = cobrowse_access_token.cobrowsing_sync_html_interval
                response[
                    "enable_custom_cobrowse_dropdown"] = cobrowse_access_token.enable_custom_cobrowse_dropdown
                response[
                    "allow_screen_sharing_cobrowse"] = cobrowse_access_token.allow_screen_sharing_cobrowse
                response[
                    "enable_non_working_hours_modal_popup"] = cobrowse_access_token.enable_non_working_hours_modal_popup
                response[
                    "no_agent_connects_toast"] = cobrowse_access_token.no_agent_connects_toast
                response[
                    "no_agent_connects_toast_text"] = cobrowse_access_token.no_agent_connects_toast_text
                response[
                    "lead_conversion_checkbox_text"] = cobrowse_access_token.lead_conversion_checkbox_text
                response[
                    "no_agent_connects_toast_threshold"] = cobrowse_access_token.no_agent_connects_toast_threshold
                response[
                    "no_agent_connects_toast_reset_count"] = cobrowse_access_token.no_agent_connects_toast_reset_count
                response[
                    "no_agent_connects_toast_reset_message"] = cobrowse_access_token.no_agent_connects_toast_reset_message
                response[
                    "show_floating_button_after_lead_search"] = cobrowse_access_token.show_floating_button_after_lead_search
                response[
                    "DEVELOPMENT"] = settings.DEVELOPMENT
                response[
                    "allow_cobrowsing_meeting"] = cobrowse_access_token.allow_cobrowsing_meeting
                response[
                    "enable_predefined_remarks"] = cobrowse_access_token.enable_predefined_remarks
                response[
                    "enable_predefined_subremarks"] = cobrowse_access_token.enable_predefined_subremarks
                response[
                    "enable_predefined_remarks_with_buttons"] = cobrowse_access_token.enable_predefined_remarks_with_buttons
                response[
                    "is_mobile"] = request.user_agent.is_mobile
                response[
                    "enable_low_bandwidth_cobrowsing"] = cobrowse_access_token.enable_low_bandwidth_cobrowsing
                response[
                    "low_bandwidth_cobrowsing_threshold"] = cobrowse_access_token.low_bandwidth_cobrowsing_threshold
                response[
                    "agent_working_days"] = cobrowse_access_token.get_cobrowse_working_days()
                response[
                    "enable_screenshot_agent"] = cobrowse_access_token.enable_screenshot_agent
                response[
                    "enable_invite_agent_in_cobrowsing"] = cobrowse_access_token.enable_invite_agent_in_cobrowsing
                response[
                    "allow_support_documents"] = cobrowse_access_token.allow_support_documents
                response[
                    "share_document_from_livechat"] = cobrowse_access_token.share_document_from_livechat
                response[
                    "allow_only_support_documents"] = cobrowse_access_token.allow_only_support_documents
                response[
                    "enable_agent_connect_message"] = cobrowse_access_token.enable_agent_connect_message
                response[
                    "agent_connect_message"] = cobrowse_access_token.agent_connect_message
                response[
                    "enable_cobrowsing_annotation"] = cobrowse_access_token.enable_cobrowsing_annotation
                response[
                    "enable_cobrowsing_on_react_website"] = cobrowse_access_token.enable_cobrowsing_on_react_website
                response[
                    "easyassist_font_family"] = cobrowse_access_token.font_family
                response[
                    "enable_iframe_cobrowsing"] = cobrowse_access_token.enable_iframe_cobrowsing
                response[
                    "enable_chat_functionality"] = cobrowse_access_token.enable_chat_functionality
                response[
                    "enable_auto_assign_unattended_lead"] = cobrowse_access_token.enable_auto_assign_unattended_lead
                response[
                    "auto_assign_lead_end_session_message"] = cobrowse_access_token.auto_assign_lead_end_session_message
                response[
                    "auto_assign_unattended_lead_message"] = cobrowse_access_token.auto_assign_unattended_lead_message
                response["enable_greeting_bubble"] = cobrowse_access_token.enable_greeting_bubble
                response[
                    "greeting_bubble_auto_popup_timer"] = cobrowse_access_token.greeting_bubble_auto_popup_timer
                response[
                    "greeting_bubble_text"] = cobrowse_access_token.greeting_bubble_text
                response["inactivity_auto_popup_number"] = cobrowse_access_token.inactivity_auto_popup_number
                response["customer_initiate_voice_call"] = cobrowse_access_token.customer_initiate_voice_call
                response["customer_initiate_video_call"] = cobrowse_access_token.customer_initiate_video_call
                response["customer_initiate_video_call_as_pip"] = cobrowse_access_token.customer_initiate_video_call_as_pip
                response["display_agent_profile"] = cobrowse_access_token.display_agent_profile
                response["enable_chat_bubble"] = cobrowse_access_token.enable_chat_bubble
                response["chat_bubble_icon_source"] = cobrowse_access_token.chat_bubble_icon_source
                response["enable_url_based_inactivity_popup"] = popup_configurations_obj.enable_url_based_inactivity_popup
                response["enable_url_based_exit_intent_popup"] = popup_configurations_obj.enable_url_based_exit_intent_popup
                response["enable_proxy_cobrowsing"] = cobrowse_access_token.get_proxy_config_obj().enable_proxy_cobrowsing
                response["enable_preview_functionality"] = cobrowse_access_token.enable_preview_functionality

                # removing get request params from the urls
                response["inactivity_popup_urls"] = json.dumps([i.split(
                    "?")[0] for i in json.loads(popup_configurations_obj.inactivity_popup_urls)])
                response["exit_intent_popup_urls"] = json.dumps([i.split(
                    "?")[0] for i in json.loads(popup_configurations_obj.exit_intent_popup_urls)])

                predefined_remarks = []
                predefined_remarks_with_buttons = []

                predefined_remarks = json.loads(cobrowse_access_token.predefined_remarks)

                if len(cobrowse_access_token.predefined_remarks_with_buttons) > 0:
                    predefined_remarks_with_buttons = cobrowse_access_token.predefined_remarks_with_buttons.split(',')

                response[
                    "predefined_remarks"] = predefined_remarks
                response[
                    "predefined_remarks_with_buttons"] = predefined_remarks_with_buttons
                response[
                    "predefined_remarks_optional"] = cobrowse_access_token.predefined_remarks_optional

                for search_field in cobrowse_access_token.search_fields.all():
                    if search_field.tag not in response["search_html_field"]:
                        response["search_html_field"][search_field.tag] = []

                    if search_field.is_deleted == False:
                        response["search_html_field"][search_field.tag].append({
                            "name": search_field.tag_name,
                            "label": search_field.tag_label,
                            "id": search_field.tag_id,
                            "data-reactid": search_field.tag_reactid,
                            "type": search_field.tag_type,
                            "key": search_field.tag_key,
                            "value": search_field.tag_value
                        })

                response["obfuscated_fields"] = []
                for obfuscated_field in cobrowse_access_token.obfuscated_fields.all():
                    response["obfuscated_fields"].append({
                        "key": obfuscated_field.key,
                        "value": obfuscated_field.value,
                        "masking_type": obfuscated_field.masking_type
                    })

                response["auto_fetch_fields"] = []
                for auto_fetch_field in cobrowse_access_token.auto_fetch_fields.all():
                    response["auto_fetch_fields"].append({
                        "fetch_field_key": auto_fetch_field.fetch_field_key,
                        "fetch_field_value": auto_fetch_field.fetch_field_value,
                        "modal_field_key": auto_fetch_field.modal_field_key,
                        "modal_field_value": auto_fetch_field.modal_field_value
                    })

                response[
                    "allow_language_support"] = cobrowse_access_token.allow_language_support
                response["supported_language"] = []
                for language in cobrowse_access_token.agent.supported_language.filter(is_deleted=False).order_by('index'):
                    response["supported_language"].append({
                        "key": language.pk,
                        "value": language.title
                    })

                response[
                    "choose_product_category"] = cobrowse_access_token.choose_product_category
                response["product_category_list"] = []
                for category in cobrowse_access_token.agent.product_category.filter(is_deleted=False).order_by('index'):
                    response["product_category_list"].append({
                        "key": category.pk,
                        "value": category.title
                    })

                response["disable_fields"] = []
                for disable_field in cobrowse_access_token.disable_fields.all():
                    response["disable_fields"].append({
                        "key": disable_field.key,
                        "value": disable_field.value,
                    })

                response["custom_select_removed_fields"] = []
                for remove_field in cobrowse_access_token.custom_select_remove_fields.all():
                    response["custom_select_removed_fields"].append({
                        "key": remove_field.key,
                        "value": remove_field.value,
                    })

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

                try:
                    visitor_obj = EasyAssistVisitor.objects.get(
                        visiting_date=datetime.datetime.today().date(), access_token=cobrowse_access_token)
                    visitor_obj.visitor_count += 1
                    visitor_obj.save()
                except Exception:
                    EasyAssistVisitor.objects.create(visiting_date=datetime.datetime.today(
                    ).date(), access_token=cobrowse_access_token)

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ClientAuthenticationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ClientAuthentication = ClientAuthenticationAPI.as_view()


class CobrowseIOCreateTokenAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            origin = get_request_origin(request)

            if cobrowse_access_token_obj == None or (not cobrowse_access_token_obj.is_valid_domain(origin)):
                response["status"] = 401
                response["message"] = "Unauthorized Access"
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                delete_expired_cobrowse_middleware_token(
                    CobrowsingMiddlewareAccessToken)
                middleware_token = create_cobrowse_middleware_token(
                    CobrowsingMiddlewareAccessToken)

                response["token"] = str(middleware_token.token)
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseIOCreateTokenAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CobrowseIOCreateToken = CobrowseIOCreateTokenAPI.as_view()


class SaveSystemAuditTrailAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            category = strip_html_tags(data["category"])
            category = remo_html_from_string(category)
            description = strip_html_tags(data["description"])
            description = remo_html_from_string(description)

            session_id = "None"
            if "session_id" in data:
                session_id = strip_html_tags(data["session_id"])
                session_id = remo_html_from_string(session_id)

            access_token = "None"
            if "access_token" in data:
                access_token = strip_html_tags(data["access_token"])

            cobrowse_io = None
            try:
                cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            except Exception:
                pass

            cobrowse_access_token = None
            try:
                cobrowse_access_token = CobrowseAccessToken.objects.get(
                    key=access_token)
            except Exception:
                pass

            active_agent = get_active_agent_obj(request, CobrowseAgent)

            if cobrowse_io != None:
                cobrowse_access_token = cobrowse_io.access_token

            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_access_token, SystemAuditTrail, active_agent)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveSystemAuditTrailAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveSystemAuditTrail = SaveSystemAuditTrailAPI.as_view()


class GetClientCobrowsingChatHistoryAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
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
            elif not is_valid_domain(request, origin, cobrowse_access_token_obj):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                session_id = strip_html_tags(data["session_id"])
                session_id = remo_html_from_string(session_id)

                if auth_params[0] != session_id:
                    return Response(status=401)

                cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
                cobrowsing_chat_history_objs = cobrowse_io.get_cobrowsing_chat_history()

                client_name = cobrowse_io.full_name

                chat_history = []
                for cobrowsing_chat_history_obj in cobrowsing_chat_history_objs:

                    est = pytz.timezone(settings.TIME_ZONE)
                    datetime = cobrowsing_chat_history_obj.datetime.astimezone(
                        est).strftime("%d %b %Y %I:%M %p")

                    sender = "client"
                    sender_name = "client"
                    agent_profile_pic_source = ""
                    if cobrowsing_chat_history_obj.sender != None:
                        sender = cobrowsing_chat_history_obj.sender.name()
                        sender_name = cobrowsing_chat_history_obj.sender.agent_name()
                        agent_profile_pic_source = cobrowsing_chat_history_obj.agent_profile_pic_source
                    chat_history.append({
                        "sender": sender,
                        "message": get_masked_data_if_hashed(cobrowsing_chat_history_obj.message),
                        "attachment": cobrowsing_chat_history_obj.attachment,
                        "attachment_file_name": cobrowsing_chat_history_obj.attachment_file_name,
                        "datetime": datetime,
                        "chat_type": cobrowsing_chat_history_obj.chat_type,
                        "sender_name": sender_name,
                        "agent_profile_pic_source": agent_profile_pic_source,
                    })

                response["status"] = 200
                response["message"] = "success"
                response["chat_history"] = chat_history
                response["client_name"] = client_name
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetClientCobrowsingChatHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetClientCobrowsingChatHistory = GetClientCobrowsingChatHistoryAPI.as_view()


class MarkLeadAsConvertedAPI(APIView):

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
            elif not is_valid_domain(request, origin, cobrowse_access_token_obj):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                session_id = data["session_id"]
                session_id = remo_html_from_string(session_id)

                if auth_params[0] != session_id:
                    return Response(status=401)

                cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
                cobrowse_io.is_helpful = True
                
                if cobrowse_io.is_lead_converted_by_url == False:
                    cobrowse_io.is_lead_converted_by_url = True
                    cobrowse_io.lead_converted_url = data["active_url"]
                    cobrowse_io.lead_converted_url_datetime = timezone.now()
                
                cobrowse_io.save()

                category = "lead_convertd"
                description = "Lead converted successfully at page " + \
                    data["active_url"]
                save_system_audit_trail(
                    category, description, cobrowse_io, cobrowse_access_token_obj, SystemAuditTrail, None)
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error MarkLeadAsConvertedAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


MarkLeadAsConverted = MarkLeadAsConvertedAPI.as_view()


class AvailableAgentListAPI(APIView):

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


AvailableAgentList = AvailableAgentListAPI.as_view()


class EasyAssistReportBugAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            request_meta = request.META.copy()
            if 'HTTP_X_CSRFTOKEN' in request_meta:
                request_meta.pop('HTTP_X_CSRFTOKEN')
            if 'CSRF_COOKIE' in request_meta:
                request_meta.pop('CSRF_COOKIE')

            meta_data = data['meta_data']
            HTTP_USER_AGENT = ""
            if 'HTTP_USER_AGENT' in request_meta:
                HTTP_USER_AGENT = request_meta['HTTP_USER_AGENT']
                request_meta.pop('HTTP_USER_AGENT')
            meta_data["imp_info"]["SystemInfo"] = HTTP_USER_AGENT
            meta_data['request_meta'] = request_meta

            files = {
                "image": "",
                "meta_data": "",
                "zip": "",
            }

            image_data = data["image_data"]

            username = data["username"]
            username = strip_html_tags(data["username"])
            username = remo_html_from_string(username)
            user = User.objects.filter(username=username).first()
            cobrowse_agent = CobrowseAgent.objects.filter(user=user).first()

            access_token = cobrowse_agent.get_access_token_obj()

            description = data["description"]
            description = strip_html_tags(data["description"])
            description = remo_html_from_string(description)

            session_id = data["session_id"]
            cobrowse_io = None
            if session_id:
                try:
                    session_id = strip_html_tags(data["session_id"])
                    session_id = remo_html_from_string(session_id)
                    cobrowse_io = CobrowseIO.objects.filter(session_id=session_id).first()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error EasyAssistReportBugAPI %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

            report_bug_dir = "bug-reports"

            if not os.path.exists(EASYASSISTAPP_SECURED_FILES_PATH + report_bug_dir):
                os.makedirs(EASYASSISTAPP_SECURED_FILES_PATH + report_bug_dir)

            # Create EasyAssistBugReport object and bug directory
            bug_report_obj = EasyAssistBugReport.objects.create(agent=cobrowse_agent, cobrowse_io=cobrowse_io, description=description)
            image_screen_dir = report_bug_dir + "/" + str(bug_report_obj.pk)
            meta_data["imp_info"]["issue_id"] = str(bug_report_obj.pk)
            meta_data["imp_info"]["description"] = description
            meta_data["imp_info"]["agent_username"] = cobrowse_agent.name()

            if not os.path.exists(EASYASSISTAPP_SECURED_FILES_PATH + image_screen_dir):
                os.makedirs(EASYASSISTAPP_SECURED_FILES_PATH + image_screen_dir)

            jsonpickle.set_encoder_options('json', indent=4)
            meta_data_dump = jsonpickle.encode(meta_data, unpicklable=True)
            bug_report_obj.meta_data = meta_data_dump
            # Create JSON META DATA File
            meta_data_path = EASYASSISTAPP_SECURED_FILES_PATH + image_screen_dir + "/meta_data_" + str(bug_report_obj.pk) + ".json"
            files["meta_data"] = meta_data_path

            with open(meta_data_path, "w") as outfile:
                outfile.write(meta_data_dump)

            # Create Image File
            if image_data:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                image_name = 'image_' + str(bug_report_obj.pk) + '.' + str(ext)

                image_path = EASYASSISTAPP_SECURED_FILES_PATH + image_screen_dir + "/" + image_name
                files["image"] = image_path

                fh = open(image_path, "wb")
                fh.write(base64.b64decode(imgstr))
                fh.close()

                bug_report_obj.image_path = image_path

            bug_report_obj.files = json.dumps(files, indent=4)
            bug_report_obj.save()

            # Send Email
            bug_report_mails = access_token.bug_report_mails
            bug_report_mails = bug_report_mails.split(",")
            for bug_report_mail in bug_report_mails:
                try:
                    bug_report_mail = bug_report_mail.strip()
                    # send_reported_bug_over_email(bug_report_mail, file_path, cobrowse_agent.agent_name(), description)
                    thread = threading.Thread(target=send_reported_bug_over_email, args=(
                        bug_report_mail, bug_report_obj, cobrowse_agent.agent_name(), meta_data["imp_info"]), daemon=True)
                    thread.start()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error EasyAssistReportBugAPI Sending mail %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EasyAssistReportBugAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


EasyAssistReportBug = EasyAssistReportBugAPI.as_view()


def icici_demo_first(request, key):
    try:
        access_token_obj = CobrowseAccessToken.objects.filter(key=key)

        if access_token_obj:
            return render(request, 'EasyAssistApp/icici_demo_first.html', {
                "access_token": key,
                "DEVELOPMENT": settings.DEVELOPMENT,
            })
        else:
            return HttpResponse("Invalid Key")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error icici_demo_first %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


def idfc_demo_first(request, key):
    try:
        access_token_obj = CobrowseAccessToken.objects.filter(key=key)

        if access_token_obj:
            return render(request, 'EasyAssistApp/idfc_first_demo.html', {
                "access_token": key,
                "DEVELOPMENT": settings.DEVELOPMENT,
            })
        else:
            return HttpResponse(INVALID_ACCESS_TOKEN_MSG)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error idfc_demo_first %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


def icici_demo_second(request, key):
    try:
        access_token_obj = CobrowseAccessToken.objects.filter(key=key)

        if access_token_obj:
            return render(request, 'EasyAssistApp/icici_demo_second.html', {
                "access_token": key,
                "DEVELOPMENT": settings.DEVELOPMENT,
            })
        else:
            return HttpResponse(INVALID_ACCESS_TOKEN_MSG)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error icici_demo_second %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


def cobrowsing_form_demo(request, key):
    try:
        access_token_obj = CobrowseAccessToken.objects.filter(key=key)

        if access_token_obj:
            return render(request, 'EasyAssistApp/cobrowsing_form_demo.html', {
                "access_token": key,
                "DEVELOPMENT": settings.DEVELOPMENT,
            })
        else:
            return HttpResponse(INVALID_ACCESS_TOKEN_MSG)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error cobrowsing_form_demo %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


def cobrowsing_form_demo_first(request, key):
    try:
        access_token_obj = CobrowseAccessToken.objects.filter(key=key)

        if access_token_obj:
            return render(request, 'EasyAssistApp/cobrowsing_form_demo_first.html', {
                "access_token": key,
                "DEVELOPMENT": settings.DEVELOPMENT,
            })
        else:
            return HttpResponse(INVALID_ACCESS_TOKEN_MSG)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error cobrowsing_form_demo_first %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


def cobrowsing_form_demo_second(request, key):
    try:
        access_token_obj = CobrowseAccessToken.objects.filter(key=key)

        if access_token_obj:
            return render(request, 'EasyAssistApp/cobrowsing_form_demo_second.html', {
                "access_token": key,
                "DEVELOPMENT": settings.DEVELOPMENT,
            })
        else:
            return HttpResponse(INVALID_ACCESS_TOKEN_MSG)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error cobrowsing_form_demo_second %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=401)


class CustomerRequestCobrowsingMeetingAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            # HTTP_X_FORWARDED_FOR = None
            # if settings.ENABLE_IP_TRACKING:
            #     HTTP_X_FORWARDED_FOR = request.META["HTTP_X_FORWARDED_FOR"]
            #     HTTP_USER_AGENT = request.META["HTTP_USER_AGENT"]

            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            origin = get_request_origin(request)

            auth_params = extract_authorization_params(request)

            if auth_params == None:
                return Response(status=401)
            if cobrowse_access_token_obj == None:
                return Response(status=401)
            elif not is_valid_domain(request, origin, cobrowse_access_token_obj):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)
                session_id = strip_html_tags(data["id"])
                active_agent = get_active_agent_obj(request, CobrowseAgent)
                cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
                cobrowse_io.customer_meeting_request_status = True
                cobrowse_io.is_customer_request_for_cobrowsing = True

                cobrowse_io.allow_customer_meeting = None
                cobrowse_io.meeting_start_datetime = None
                cobrowse_io.save()

                category = "session_details"
                description = "Request for meeting sent by " + \
                    str(cobrowse_io.full_name)
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
                audit_trail_obj = CobrowseVideoAuditTrail.objects.filter(cobrowse_video=cobrowse_video_conf_obj)
                if audit_trail_obj:
                    audit_trail_obj = audit_trail_obj.first()
                else:
                    audit_trail_obj = CobrowseVideoAuditTrail.objects.create(cobrowse_video=cobrowse_video_conf_obj)
            
                if audit_trail_obj.meeting_initiated_by == None:
                    audit_trail_obj.meeting_initiated_by = "customer"
                
                for agent in cobrowse_io.support_agents.all():
                    if agent.is_cobrowsing_active:
                        audit_trail_obj.meeting_agents_invited.add(agent)
                audit_trail_obj.save()

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CustomerRequestCobrowsingMeetingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CustomerRequestCobrowsingMeeting = CustomerRequestCobrowsingMeetingAPI.as_view()


class CheckClientMeetingStatusAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
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
            elif not is_valid_domain(request, origin, cobrowse_access_token_obj):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                session_id = strip_html_tags(data["id"])
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

CheckClientMeetingStatus = CheckClientMeetingStatusAPI.as_view()


class EnableLiveChatCobrowseSettingsAPI(APIView):

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

            user_obj = None
            try:
                user_obj = User.objects.get(pk=id)
            except Exception:
                pass

            if user_obj == None:
                response['status'] = 400
                response['mesage'] = 'User does not exist'
            else:
                cobrowse_admin = CobrowseAgent.objects.filter(user=user_obj)

                if cobrowse_admin:
                    cobrowse_access_token = cobrowse_admin.first().get_access_token_obj()
                    enable_livechat_cobrowse_settings(cobrowse_access_token)
                    response['status'] = 200
                    response['message'] = 'Success'
                else:
                    response["status"] = 400
                    response["message"] = "Cobrowse user does not exist"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EnableLiveChatCobrowseSettingsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


EnableLiveChatCobrowseSettings = EnableLiveChatCobrowseSettingsAPI.as_view()


class CheckCobrowseAgentExistsAPI(APIView):

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

            cobrowse_agent = CobrowseAgent.objects.filter(user__pk=id)

            if cobrowse_agent:
                response['status'] = 200
                response['message'] = 'Success'
            else:
                response["status"] = 400
                response["message"] = "Cobrowse user does not exist"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckCobrowseAgentExistsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CheckCobrowseAgentExists = CheckCobrowseAgentExistsAPI.as_view()


class FetchConnectedAgentDetailsAPI(APIView):

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
            elif not is_valid_domain(request, origin, cobrowse_access_token_obj):
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)
                id = data["id"]
                id = remo_html_from_string(id)

                agent_name = None
                agent_location = None
                agent_email = None
                agent_additional_details_response = None

                if auth_params[0] != id:
                    return Response(status=401)

                cobrowse_io = CobrowseIO.objects.filter(session_id=id).first()
                display_agent_profile = cobrowse_access_token_obj.display_agent_profile
                if cobrowse_io:
                    if cobrowse_io.agent:
                        assigned_agent = cobrowse_io.agent
                        agent_name = str(assigned_agent.user.first_name)
                        if agent_name.strip() == "" or agent_name == "None":
                            agent_name = str(assigned_agent.user.username)
                        agent_location = str(assigned_agent.location)
                        agent_email = str(assigned_agent.user.email)
                        if agent_email.strip() == "" or agent_email == "None":
                            agent_email = str(assigned_agent.user.username)
                        agent_profile_pic_source = assigned_agent.agent_profile_pic_source
                        if cobrowse_access_token_obj.is_agent_details_api_enabled():
                            agent_details_api_processor_obj = cobrowse_access_token_obj.get_agent_details_api_processor_obj()
                            if assigned_agent.agent_code:
                                json_response = execute_code_with_time_limit(agent_details_api_processor_obj.function, str(assigned_agent.agent_code))
                                logger.info("Additional agent details API response %s", json.dumps(json_response), extra={'AppName': 'EasyAssist'})
                                if "status_code" in json_response and json_response["status_code"] == 200:
                                    if "response_body" in json_response and len(json_response["response_body"]):
                                        agent_additional_details_response = json_response["response_body"]
                        
                        response["agent_name"] = agent_name
                        response["agent_location"] = agent_location
                        response["agent_email"] = agent_email
                        response["agent_additional_details_response"] = agent_additional_details_response
                        response["show_agent_email"] = cobrowse_access_token_obj.show_agent_email
                        response["show_agent_details_modal"] = cobrowse_access_token_obj.show_agent_details_modal
                        response["agent_profile_pic_source"] = agent_profile_pic_source
                        response["display_agent_profile"] = display_agent_profile
                        response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FetchConnectedAgentDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


FetchConnectedAgentDetails = FetchConnectedAgentDetailsAPI.as_view()
