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
from EasyAssistApp.views_table import *
from EasyAssistApp.send_email import send_password_over_email, send_drop_link_over_email, send_masking_pii_data_otp_mail, send_meeting_link_over_mail
from EasyChat.settings import APP_LOG_FILENAME, LOGTAILER_LINES
from EasyAssistApp.utils_parse_sandbox_user import *

from DeveloperConsoleApp.utils import get_developer_console_settings

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

from operator import itemgetter
from collections import OrderedDict

logger = logging.getLogger(__name__)


def SandboxUserDashboard(request):

    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login/")

        user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        if cobrowse_agent.role != "admin":
            return redirect('/easy-assist/sales-ai/settings/')
        access_token_obj = cobrowse_agent.get_access_token_obj()

        if not (user.is_staff or cobrowse_agent.is_cognoai_user):
            return HttpResponse("Invalid Access")

        return render(request, "EasyAssistApp/sandbox_user_dashboard.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SandboxUserDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse("Invalid Access")


class CreateSandboxUserAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            email_id = data["email_id"]
            password = data["password"]
            is_cobrowsing_enabled = data["is_cobrowsing_enabled"]
            inbound_enabled = data["inbound_enabled"]
            outbound_enabled = data["outbound_enabled"]
            reverse_cobrowsing_enabled = data["reverse_cobrowsing_enabled"]
            video_meeting_enabled = data["video_meeting_enabled"]

            if not is_cobrowsing_enabled:
                inbound_enabled = False
                outbound_enabled = False
                reverse_cobrowsing_enabled = False
            else:
                if inbound_enabled or outbound_enabled:
                    reverse_cobrowsing_enabled = False

            is_user_exist = User.objects.filter(username=email_id).first()
            if is_user_exist:
                response["status"] = 301
            else:
                user_first_name = "Sandbox User"
                platform_url = settings.EASYCHAT_HOST_URL
                agent_role = "admin"
                support_level = "L1"

                todays_datetime = datetime.datetime.now()
                credentials_expire_datetime = todays_datetime + \
                    datetime.timedelta(days=15)
                credentials_expire_date = credentials_expire_datetime.date()

                user = User.objects.create(
                    first_name=user_first_name,
                    email=email_id,
                    username=email_id,
                    status="2",
                    role="bot_builder")
                user.is_sandbox_user = True

                user.set_password(password)
                user.save()

                thread = threading.Thread(target=send_password_over_email, args=(
                    email_id, user_first_name, password, platform_url, ), daemon=True)
                thread.start()

                cobrowse_agent = CobrowseAgent.objects.create(
                    user=user,
                    role=agent_role,
                    support_level=support_level)
                cobrowse_agent.is_switch_allowed = True
                cobrowse_agent.save()

                sandbox_user = CobrowseSandboxUser.objects.create(
                    user=user,
                    password=password,
                    enable_cobrowsing=is_cobrowsing_enabled,
                    enable_inbound=inbound_enabled,
                    enable_outbound=outbound_enabled,
                    enable_reverse_cobrowsing=reverse_cobrowsing_enabled,
                    enable_video_meeting=video_meeting_enabled)

                sandbox_user.expire_date = credentials_expire_date
                sandbox_user.save()

                access_token_obj = cobrowse_agent.get_access_token_obj()
                update_sandbox_user_cobrowsing_settings(
                    sandbox_user, access_token_obj)

                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CreateSandboxUserAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CreateSandboxUser = CreateSandboxUserAPI.as_view()


class GetAllSandboxUserAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            page = data["page"]

            sandbox_user_objs = CobrowseSandboxUser.objects.all().order_by('-create_datetime')

            total_rows_per_pages = 20
            total_sandbox_users = sandbox_user_objs.count()

            paginator = Paginator(
                sandbox_user_objs, total_rows_per_pages)

            try:
                sandbox_user_objs = paginator.page(page)
            except PageNotAnInteger:
                sandbox_user_objs = paginator.page(1)
            except EmptyPage:
                sandbox_user_objs = paginator.page(paginator.num_pages)

            if page != None:
                start_point = total_rows_per_pages * (int(page) - 1) + 1
                end_point = min(total_rows_per_pages *
                                int(page), total_sandbox_users)
                if start_point > end_point:
                    start_point = max(
                        end_point - len(sandbox_user_objs) + 1, 1)
            else:
                start_point = 1
                end_point = min(total_rows_per_pages, total_sandbox_users)

            start_point = min(start_point, end_point)

            pagination_range = sandbox_user_objs.paginator.page_range

            has_next = sandbox_user_objs.has_next()
            has_previous = sandbox_user_objs.has_previous()
            next_page_number = -1
            previous_page_number = -1

            if has_next:
                next_page_number = sandbox_user_objs.next_page_number()
            if has_previous:
                previous_page_number = sandbox_user_objs.previous_page_number()

            pagination_metadata = {
                'total_count': total_sandbox_users,
                'start_point': start_point,
                'end_point': end_point,
                'page_range': [pagination_range.start, pagination_range.stop],
                'has_next': has_next,
                'has_previous': has_previous,
                'next_page_number': next_page_number,
                'previous_page_number': previous_page_number,
                'number': sandbox_user_objs.number,
                'num_pages': sandbox_user_objs.paginator.num_pages
            }

            active_sandbox_users = []
            for sandbox_user_obj in sandbox_user_objs:
                active_sandbox_users.append(parse_sandbox_user_obj(
                    sandbox_user_obj))

            response["status"] = 200
            response["message"] = "success"
            response["active_sandbox_users"] = active_sandbox_users
            response["pagination_metadata"] = pagination_metadata

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAllSandboxUserAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAllSandboxUser = GetAllSandboxUserAPI.as_view()


class DeleteSandboxUserAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            sandbox_user_id = data["sandbox_user_id"]
            sandbox_user_id = remo_html_from_string(sandbox_user_id)

            sandbox_user_obj = CobrowseSandboxUser.objects.filter(
                pk=sandbox_user_id).first()

            if not sandbox_user_obj:
                reponse["status"] = 301
            else:
                user = sandbox_user_obj.user
                cobrowse_agent = CobrowseAgent.objects.filter(user=user)
                if cobrowse_agent:
                    cobrowse_agent.delete()

                sandbox_user_obj.delete()
                user.delete()
                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteSandboxUserAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteSandboxUser = DeleteSandboxUserAPI.as_view()


class GetSandboxUserDataAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            sandbox_user_id = data["sandbox_user_id"]
            sandbox_user_id = remo_html_from_string(sandbox_user_id)

            sandbox_user_obj = CobrowseSandboxUser.objects.filter(
                pk=sandbox_user_id).first()

            if not sandbox_user_obj:
                reponse["status"] = 301
            else:
                sandbox_user_password = sandbox_user_obj.password
                sandbox_user_data = parse_sandbox_user_obj(sandbox_user_obj)
                sandbox_user_data["sandbox_user_password"] = sandbox_user_password

                response["status"] = 200
                response["sandbox_user_data"] = sandbox_user_data
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetSandboxUserDataAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetSandboxUserData = GetSandboxUserDataAPI.as_view()


class SaveSandboxUserDataAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            email_id = data["email_id"]
            password = data["password"]
            cobrowsing_enabled = data["cobrowsing_enabled"]
            inbound_enabled = data["inbound_enabled"]
            outbound_enabled = data["outbound_enabled"]
            reverse_cobrowsing_enabled = data["reverse_cobrowsing_enabled"]
            video_meeting_enabled = data["video_meeting_enabled"]

            if not cobrowsing_enabled:
                inbound_enabled = False
                outbound_enabled = False
                reverse_cobrowsing_enabled = False
            else:
                if inbound_enabled or outbound_enabled:
                    reverse_cobrowsing_enabled = False
                    video_meeting_enabled = False

                if reverse_cobrowsing_enabled:
                    inbound_enabled = False
                    outbound_enabled = False
                    video_meeting_enabled = False

                if video_meeting_enabled:
                    cobrowsing_enabled = False
                    inbound_enabled = False
                    outbound_enabled = False
                    reverse_cobrowsing_enabled = False

            user = User.objects.filter(
                username=email_id, is_sandbox_user=True).first()
            if not user:
                reponse["status"] = 301
            else:
                user.set_password(password)
                user.save()

                user_first_name = user.first_name
                platform_url = settings.EASYCHAT_HOST_URL

                thread = threading.Thread(target=send_password_over_email, args=(
                    email_id, user_first_name, password, platform_url, ), daemon=True)
                thread.start()

                sandbox_user_obj = CobrowseSandboxUser.objects.get(user=user)

                sandbox_user_obj.enable_cobrowsing = cobrowsing_enabled
                sandbox_user_obj.enable_inbound = inbound_enabled
                sandbox_user_obj.enable_outbound = outbound_enabled
                sandbox_user_obj.enable_reverse_cobrowsing = reverse_cobrowsing_enabled
                sandbox_user_obj.enable_video_meeting = video_meeting_enabled
                sandbox_user_obj.last_update_datetime = timezone.now()
                sandbox_user_obj.password = password
                sandbox_user_obj.save()

                cobrowse_agent = CobrowseAgent.objects.get(user=user)
                access_token_obj = cobrowse_agent.get_access_token_obj()

                update_sandbox_user_cobrowsing_settings(
                    sandbox_user_obj, access_token_obj)

                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveSandboxUserDataAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveSandboxUserData = SaveSandboxUserDataAPI.as_view()


class SandboxUserUpdateExpireDateAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            sandbox_user_id = data["sandbox_user_id"]
            sandbox_user_id = remo_html_from_string(sandbox_user_id)

            expire_date = data["expire_date"]

            sandbox_user_obj = CobrowseSandboxUser.objects.filter(
                pk=sandbox_user_id).first()

            if not sandbox_user_obj:
                response["status"] = 301
            else:
                expire_date_obj = datetime.datetime.strptime(
                    expire_date, "%m/%d/%Y")
                sandbox_user_obj.expire_date = expire_date_obj
                sandbox_user_obj.is_expired = False
                sandbox_user_obj.save()
                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SandboxUserUpdateExpireDateAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SandboxUserUpdateExpireDate = SandboxUserUpdateExpireDateAPI.as_view()
