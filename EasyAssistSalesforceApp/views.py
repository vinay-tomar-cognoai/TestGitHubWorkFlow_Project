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
from EasyAssistSalesforceApp.models import *
from EasyAssistSalesforceApp.utils import *
from EasyAssistSalesforceApp.views_agent import *
from EasyAssistSalesforceApp.views_analytics import *
# from EasyAssistApp.views_screensharing_cobrowse import *


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

# changes done


@xframe_options_exempt
def SalesAIIframePage(request):

    token_id = request.GET.get("id", None)

    if token_id == None:
        return HttpResponse(status=401)

    cobrowse_access_token = None
    try:
        cobrowse_access_token = CobrowseAccessToken.objects.get(key=token_id)
    except Exception:
        logger.warning("Invalid access token", extra={
                       'AppName': 'EasyAssistSalesforce'})

    if cobrowse_access_token == None:
        return HttpResponse(status=401)

    eacSession = None
    try:
        existing_value = request.COOKIES.get("eacSession", None)
        eacSession = str(request.GET.get("eacSession", existing_value))
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAIIframePage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

    response = render(request, "EasyAssistSalesforceApp/sales-iframe.html", {
        "eacSession": str(eacSession)
    })

    response.set_cookie("eacSession", eacSession)

    return response

# changes done


@xframe_options_exempt
def SalesAIClientLiveChatWindow(request):
    access_token = CobrowseAccessToken.objects.get(
        key=request.GET["access_token"])
    return render(request, "EasyAssistSalesforceApp/client-chatbot.html", {
        "access_token": access_token
    })

# changes done


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
                longitude = data["longitude"]
                longitude = remo_html_from_string(str(longitude))
                latitude = data["latitude"]
                latitude = remo_html_from_string(str(latitude))
                mobile_number = data["mobile_number"]
                mobile_number = remo_html_from_string(mobile_number)
                mobile_number = remo_special_tag_from_string(mobile_number)
                selected_language = data["selected_language"]
                selected_product_category = data["selected_product_category"]
                meta_data = data["meta_data"]

                virtual_agent_code = "None"
                if "virtual_agent_code" in data:
                    virtual_agent_code = data["virtual_agent_code"]

                virtual_agent_selected = None

                if cobrowse_access_token_obj.allow_connect_with_virtual_agent_code:

                    try:
                        virtual_agent_selected = CobrowseAgent.objects.get(
                            virtual_agent_code=virtual_agent_code)
                    except Exception:
                        pass

                    if virtual_agent_selected == None:
                        response["status"] = 103
                        response["message"] = "Invalid username and password"
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(
                            response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)

                    logger.info("Customer connected through virtual agent code %s",
                                virtual_agent_selected, extra={'AppName': 'EasyAssistSalesforce'})

                mobile_number = mobile_number.strip().lower()
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
                    cobrowse_io.title = meta_data[
                        "product_details"]["title"].strip()

                if "product_details" in meta_data and "url" in meta_data["product_details"]:
                    cobrowse_io.active_url = meta_data[
                        "product_details"]["url"].strip()

                meta_data = json.dumps(meta_data)
                meta_data = custom_encrypt_obj.encrypt(meta_data)
                cobrowse_io.meta_data = meta_data
                cobrowse_io.is_active = True
                cobrowse_io.last_update_datetime = timezone.now()
                cobrowse_io.is_agent_connected = False
                cobrowse_io.cobrowsing_start_datetime = None
                cobrowse_io.latitude = str(latitude)
                cobrowse_io.longitude = str(longitude)

                if share_client_session or virtual_agent_selected != None:
                    cobrowse_io.allow_agent_cobrowse = "true"

                cobrowse_io.is_lead = False
                cobrowse_io.access_token = cobrowse_access_token_obj
                cobrowse_io.request_meta_details = json.dumps(
                    request_meta_details)
                cobrowse_io.agent = virtual_agent_selected
                cobrowse_io.save()

                if "customer_id" in data and data["customer_id"] != "None":
                    try:
                        easyassist_customer = EasyAssistCustomer.objects.get(
                            customer_id=data["customer_id"])
                        easyassist_customer.cobrowse_io = cobrowse_io
                        easyassist_customer.save()
                    except Exception:
                        pass

                if virtual_agent_selected != None:
                    send_agent_customer_connected_notification(
                        virtual_agent_selected, cobrowse_io)

                response["session_id"] = str(cobrowse_io.session_id)
                response["status"] = 200
                response["message"] = "success"
                response["sessionid"] = request.session.session_key
                response["csrf"] = csrf.get_token(request)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseIOInitializeAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CobrowseIOInitialize = CobrowseIOInitializeAPI.as_view()

# changes done


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

                    cobrowse_io = CobrowseIO.objects.create(full_name=name,
                                                            mobile_number=mobile_number,
                                                            share_client_session=share_client_session,
                                                            primary_value=primary_id)

                    if "product_details" in meta_data and "title" in meta_data["product_details"]:
                        cobrowse_io.title = meta_data[
                            "product_details"]["title"].strip()

                    if "product_details" in meta_data and "url" in meta_data["product_details"]:
                        cobrowse_io.active_url = meta_data[
                            "product_details"]["url"].strip()

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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CobrowseIOInitializeUsingDroplink = CobrowseIOInitializeUsingDroplinkAPI.as_view()

# changes done


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
                    easyassist_customer.title = meta_data[
                        "product_details"]["title"].strip()

                if "product_details" in meta_data and "url" in meta_data["product_details"]:
                    easyassist_customer.active_url = meta_data[
                        "product_details"]["url"].strip()

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
                easyassist_customer.save()

                response["customer_id"] = str(easyassist_customer.customer_id)
                response["status"] = 200
                response["message"] = "success"
                response["csrf"] = csrf.get_token(request)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EasyAssistCustomerSetAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


EasyAssistCustomerSet = EasyAssistCustomerSetAPI.as_view()

# changes done


class SyncCobrowseIOAPI(APIView):

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
            elif cobrowse_access_token_obj == None and False:
                return Response(status=401)
            elif False and (not cobrowse_access_token_obj.is_valid_domain(origin)):
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
                # cobrowse_io.active_url = active_url
                cobrowse_io.is_active = True
                cobrowse_io.is_updated = True
                cobrowse_io.save()

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SyncCobrowseIOAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SyncCobrowseIO = SyncCobrowseIOAPI.as_view()

# changes done


class HighlightCheckCobrowseIOAPI(APIView):

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
                id = remo_html_from_string(id)

                if auth_params[0] != id:
                    return Response(status=401)

                cobrowse_io = CobrowseIO.objects.get(session_id=id)

                is_session_closed = False

                if cobrowse_io.cobrowsing_start_datetime != None and not cobrowse_io.is_active_timer():
                    cobrowse_io.is_active = False
                    is_session_closed = True
                    logger.info(
                        "Closing cobrowsing session due to inactivity...", extra={'AppName': 'EasyAssistSalesforce'})
                else:
                    cobrowse_io.is_active = True
                    cobrowse_io.last_update_datetime = timezone.now()

                cobrowse_io.is_updated = True
                cobrowse_io.save()

                agent_name = None
                agent_location = None
                if cobrowse_io.agent != None:
                    agent_name = str(cobrowse_io.agent.user.username)
                    if agent_name.strip() == "" or agent_name == "None":
                        agent_name = str(cobrowse_io.agent.user.username)
                    agent_location = str(cobrowse_io.agent.location)

                response["message"] = "success"
                response["is_agent_connected"] = cobrowse_io.is_agent_active_timer(
                ) and cobrowse_io.is_agent_connected
                response["agent_name"] = agent_name
                response["agent_location"] = agent_location
                response[
                    "agent_assistant_request_status"] = cobrowse_io.agent_assistant_request_status
                response["allow_agent_cobrowse"] = cobrowse_io.allow_agent_cobrowse
                response[
                    "agent_meeting_request_status"] = cobrowse_io.agent_meeting_request_status
                response["allow_agent_meeting"] = cobrowse_io.allow_agent_meeting
                response["is_lead"] = cobrowse_io.is_lead
                response["is_archived"] = cobrowse_io.is_archived
                response["is_session_closed"] = is_session_closed
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error HighlightCheckCobrowseIOAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


HighlightCheckCobrowseIO = HighlightCheckCobrowseIOAPI.as_view()

# changes done


class CobrowseIOCloseSessionAPI(APIView):

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
                id = remo_html_from_string(id)

                if auth_params[0] != id:
                    return Response(status=401)

                cobrowse_io = CobrowseIO.objects.get(session_id=id)
                cobrowse_io.is_active = False
                cobrowse_io.last_update_datetime = timezone.now()
                cobrowse_io.save()

                category = "session_closed"
                description = "Session is closed by client"
                save_system_audit_trail(
                    category, description, cobrowse_io, cobrowse_access_token_obj, SystemAuditTrail, None)

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseIOCloseSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CobrowseIOCloseSession = CobrowseIOCloseSessionAPI.as_view()

# changes done


class CobrowseIOCaptureClientScreenAPI(APIView):

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
                id = remo_html_from_string(id)

                if auth_params[0] != id:
                    return Response(status=401)

                content = data["content"]
                type_screenshot = data["type_screenshot"]
                type_screenshot = remo_html_from_string(type_screenshot)
                cobrowse_io = CobrowseIO.objects.get(session_id=id)

                client_screen_root_dir = "client-screens"

                easyassist_dir = settings.BASE_DIR + '/secured_files/EasyAssistSalesforceApp/'
                if not os.path.exists("secured_files/EasyAssistSalesforceApp/" + client_screen_root_dir):
                    os.makedirs(
                        "secured_files/EasyAssistSalesforceApp/" + client_screen_root_dir)

                image_screen_dir = client_screen_root_dir + \
                    "/" + str(cobrowse_io.session_id)

                if not os.path.exists("secured_files/EasyAssistSalesforceApp/" + image_screen_dir):
                    os.makedirs(
                        "secured_files/EasyAssistSalesforceApp/" + image_screen_dir)

                if type_screenshot == "pageshot":

                    pageshot_filepath = image_screen_dir + \
                        "/" + str(int(time.time())) + ".html"
                    pageshot_file = open(
                        easyassist_dir + pageshot_filepath, "w")
                    pageshot_file.write(content)
                    pageshot_file.close()

                    # image_filepath = image_screen_dir + \
                    #     "/" + str(int(time.time())) + ".png"
                    # imgkit.from_file(easyassist_dir + pageshot_filepath, easyassist_dir + image_filepath, options={"xvfb": ""})

                    CobrowsingSessionMetaData.objects.create(cobrowse_io=cobrowse_io,
                                                             type_screenshot=type_screenshot,
                                                             content=easyassist_dir + pageshot_filepath)
                elif type_screenshot == "screenshot":

                    format, imgstr = content.split(';base64,')
                    ext = format.split('/')[-1]
                    image_name = str(int(time.time())) + "." + str(ext)
                    data = ContentFile(base64.b64decode(
                        imgstr), name='temp.' + ext)
                    image_path = default_storage.save(
                        image_screen_dir + "/" + image_name, data)
                    image_path = easyassist_dir + image_path

                    CobrowsingSessionMetaData.objects.create(cobrowse_io=cobrowse_io,
                                                             type_screenshot=type_screenshot,
                                                             content=image_path)

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseIOCaptureClientScreenAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CobrowseIOCaptureClientScreen = CobrowseIOCaptureClientScreenAPI.as_view()

# changes done


class CobrowseIOCaptureLeadAPI(APIView):

    def post(self, request, *args, **kwargs):
        logger.info("Inside CobrowseIOCaptureLeadAPI",
                    extra={'AppName': 'EasyAssistSalesforce'})
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            origin = get_request_origin(request)

            if cobrowse_access_token_obj == None:
                response["status"] = 401
                response["message"] = "Unauthorized Access"
            elif not cobrowse_access_token_obj.is_valid_domain(origin):
                response["status"] = 401
                response["message"] = "Unauthorized Access"
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)
                logger.info("Request: " + json.dumps(data),
                            extra={'AppName': 'EasyAssistSalesforce'})

                primary_value_list = data["primary_value_list"]
                session_id = data["session_id"]
                session_id = remo_html_from_string(session_id)
                meta_data = data["meta_data"]

                cobrowse_io = None
                if session_id == "None":
                    cobrowse_io = CobrowseIO.objects.create(is_lead=True)
                    cobrowse_io.access_token = cobrowse_access_token_obj
                    cobrowse_io.request_datetime = timezone.now()
                else:
                    cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

                if "product_details" in meta_data and "title" in meta_data["product_details"]:
                    cobrowse_io.title = meta_data[
                        "product_details"]["title"].strip()

                if "product_details" in meta_data and "url" in meta_data["product_details"]:
                    cobrowse_io.active_url = meta_data[
                        "product_details"]["url"].strip()

                meta_data = json.dumps(meta_data)
                meta_data = custom_encrypt_obj.encrypt(meta_data)
                cobrowse_io.save()
                check_and_update_lead(
                    primary_value_list, meta_data, cobrowse_io, CobrowseCapturedLeadData)
                response["status"] = 200
                response["message"] = "success"
                response["session_id"] = str(cobrowse_io.session_id)
                logger.info("Response: " + json.dumps(response),
                            extra={'AppName': 'EasyAssistSalesforce'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CobrowseIOCaptureLeadAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        logger.info("Successfully exited from SearchCobrowsingLeadAPI", extra={
                    'AppName': 'EasyAssistSalesforce'})
        return Response(data=response)


CobrowseIOCaptureLead = CobrowseIOCaptureLeadAPI.as_view()

# changes done


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
            elif not cobrowse_access_token_obj.is_valid_domain(origin):
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
                        description = "Cobrowsing request accepted by client"
                    elif data["status"] == "false":
                        cobrowse_io.allow_agent_cobrowse = "false"
                        cobrowse_io.consent_cancel_count = cobrowse_io.consent_cancel_count + 1
                        description = "Cobrowsing request declined by client"

                    category = "session_details"
                    save_system_audit_trail(
                        category, description, cobrowse_io, cobrowse_access_token_obj, SystemAuditTrail, None)

                    cobrowse_io.save()
                    response["status"] = 200
                    response["message"] = "success"
                    response["cobrowsing_allowed"] = data["status"]
                    response["allow_screen_sharing_cobrowse"] = cobrowse_access_token_obj.allow_screen_sharing_cobrowse
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateAgentAssistantRequestAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

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

                cobrowse_io.agent_assistant_request_status = False

                if data["status"] == "true":
                    cobrowse_io.allow_agent_meeting = "true"
                    cobrowse_io.agent_meeting_request_status = False
                    cobrowse_io.meeting_start_datetime = timezone.now()
                    description = "Meeting request accepted by client"

                elif data["status"] == "false":
                    cobrowse_io.allow_agent_meeting = "false"
                    cobrowse_io.agent_meeting_request_status = False
                    cobrowse_io.meeting_start_datetime = None
                    description = "Meeting request declined by client"

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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateAgentMeetingRequest = UpdateAgentMeetingRequestAPI.as_view()

# changes done


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
            elif not cobrowse_access_token_obj.is_valid_domain(origin):
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

                if rating != "None":
                    cobrowse_io.agent_rating = int(rating)
                else:
                    cobrowse_io.agent_rating = None

                cobrowse_io.last_update_datetime = timezone.now()
                cobrowse_io.client_session_end_time = timezone.now()
                cobrowse_io.is_archived = True
                cobrowse_io.save()
                logger.info("Client feedback has beed saved successfully.", extra={
                            'AppName': 'EasyAssistSalesforce'})

                category = "session_closed"
                description = "Session is closed by client after submitting feedback"
                save_system_audit_trail(
                    category, description, cobrowse_io, cobrowse_access_token_obj, SystemAuditTrail, None)
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SubmitClientFeedbackAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SubmitClientFeedback = SubmitClientFeedbackAPI.as_view()

# changes done


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

            origin = get_request_origin(request)

            cobrowse_access_token = CobrowseAccessToken.objects.get(key=key)

            if cobrowse_access_token.is_valid_domain(origin) and cobrowse_access_token.is_active:

                response[
                    "easyassist_host_protocol"] = settings.EASYASSIST_HOST_PROTOCOL
                response["easyassist_host"] = settings.EASYASSISTSALESFOCEAPP_HOST
                response["allow_cobrowsing"] = False
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
                response["toast_timeout"] = 5000
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
                response["start_time"] = cobrowse_access_token.get_start_time()
                response["end_time"] = cobrowse_access_token.get_end_time()
                response[
                    "enable_verification_code_popup"] = cobrowse_access_token.enable_verification_code_popup
                response[
                    "show_verification_code_modal"] = cobrowse_access_token.show_verification_code_modal
                response[
                    "disable_connect_button_if_agent_unavailable"] = cobrowse_access_token.disable_connect_button_if_agent_unavailable
                response[
                    "message_if_agent_unavailable"] = cobrowse_access_token.message_if_agent_unavailable
                response[
                    "message_on_non_working_hours"] = cobrowse_access_token.message_on_non_working_hours
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
                    "allow_connect_with_virtual_agent_code"] = cobrowse_access_token.allow_connect_with_virtual_agent_code
                response[
                    "allow_connect_with_drop_link"] = cobrowse_access_token.allow_connect_with_drop_link
                response[
                    "highlight_api_call_frequency"] = cobrowse_access_token.highlight_api_call_frequency
                response[
                    "floating_button_left_right_position"] = cobrowse_access_token.floating_button_left_right_position
                response[
                    "message_on_choose_product_category_modal"] = cobrowse_access_token.message_on_choose_product_category_modal
                response["allow_file_verification"] = cobrowse_access_token.allow_file_verification
                response["allow_agent_to_customer_cobrowsing"] = cobrowse_access_token.allow_agent_to_customer_cobrowsing
                response["enable_waitlist"] = cobrowse_access_token.enable_waitlist
                response[
                    "show_floating_button_on_enable_waitlist"] = cobrowse_access_token.show_floating_button_on_enable_waitlist
                response["enable_masked_field_warning"] = cobrowse_access_token.enable_masked_field_warning
                response["masked_field_warning_text"] = cobrowse_access_token.masked_field_warning_text
                response["allow_video_meeting_only"] = cobrowse_access_token.allow_video_meeting_only
                for search_field in cobrowse_access_token.search_fields.all():
                    if search_field.tag not in response["search_html_field"]:
                        response["search_html_field"][search_field.tag] = []

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
                for language in cobrowse_access_token.agent.supported_language.all():
                    response["supported_language"].append({
                        "key": language.pk,
                        "value": language.title
                    })

                response[
                    "choose_product_category"] = cobrowse_access_token.choose_product_category
                response["product_category_list"] = []
                for category in cobrowse_access_token.agent.product_category.all():
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

                try:
                    visitor_obj = EasyAssistVisitor.objects.get(
                        visiting_date=datetime.datetime.today().date(), access_token=cobrowse_access_token)
                    visitor_obj.visitor_count += 1
                    visitor_obj.save()
                except Exception:
                    EasyAssistVisitor.objects.create(visiting_date=datetime.datetime.today(
                    ).date(), access_token=cobrowse_access_token)
                    pass

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ClientAuthenticationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ClientAuthentication = ClientAuthenticationAPI.as_view()

# changes done


class CobrowseIOCreateTokenAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            origin = get_request_origin(request)

            if cobrowse_access_token_obj == None:
                response["status"] = 401
                response["message"] = "Unauthorized Access"
            elif not cobrowse_access_token_obj.is_valid_domain(origin):
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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

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
            if not check_for_salesforce_request(request):
                return HttpResponse(status=401)
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            if active_agent == None:
                return HttpResponse(status=401)
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

            if cobrowse_io != None:
                cobrowse_access_token = cobrowse_io.access_token

            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_access_token, SystemAuditTrail, active_agent)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveSystemAuditTrailAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveSystemAuditTrail = SaveSystemAuditTrailAPI.as_view()

# changes done


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
            elif not cobrowse_access_token_obj.is_valid_domain(origin):
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
                response["client_name"] = client_name
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetClientCobrowsingChatHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetClientCobrowsingChatHistory = GetClientCobrowsingChatHistoryAPI.as_view()

# changes done


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
            elif not cobrowse_access_token_obj.is_valid_domain(origin):
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
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


MarkLeadAsConverted = MarkLeadAsConvertedAPI.as_view()

# changes done


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
                         str(e), str(exc_tb.tb_lineno))

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AvailableAgentList = AvailableAgentListAPI.as_view()
