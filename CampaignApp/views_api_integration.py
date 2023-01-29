from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect

# Django REST framework
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from rest_framework.decorators import authentication_classes

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.sessions.models import Session

"""For user authentication"""
from django.contrib.auth import logout

from CampaignApp.utils import *
from CampaignApp.models import *
from EasyChatApp.models import *
from CampaignApp.constants import *

import json
import time
from django.conf import settings
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
from django.utils import timezone

from django.db.models import Q, Count, Max
import operator
from os import path


import pytz
import uuid
import sys
from datetime import datetime, date, timedelta
import threading


# Logger
import logging
logger = logging.getLogger(__name__)


def APIEditorPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        bot_pk = request.GET['bot_pk']
        bot_obj = Bot.objects.get(pk=int(bot_pk), is_deleted=False)

        if request.user in bot_obj.users.all():

            if 'campaign_id' in request.GET:
                selected_campaign_id = request.GET['campaign_id']
            else:
                selected_campaign_id = 'none'
            
            whatsapp_service_providers = CampaignWhatsAppServiceProvider.objects.all()

            config_obj = get_config_obj(CampaignConfig)
            system_commands = config_obj.system_commands

            return render(request, "CampaignApp/api_editor.html", {
                'selected_bot_obj': bot_obj,
                'whatsapp_service_providers': whatsapp_service_providers,
                'selected_campaign_id': selected_campaign_id,
                'system_commands': system_commands,
            })
        else:
            return redirect("/campaign/unauthorised/")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("APIEditorPage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return render(request, 'CampaignApp/error_500.html')


"""

SendOTPAPI : sends otp to the email entered by user

"""


class SendOTPAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            email = data['email']
            email = email.strip()

            email_ends_with = email.split('@')[1]

            if not check_valid_email(email):
                response["status_message"] = "Please enter valid Email ID."
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)
            
            if email_ends_with != 'getcogno.ai':
                response["status_message"] = "Email ID ending with getcogno.ai only is valid for API Integration."
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)                

            try:
                campaign_user_obj = CampaignAuthUser.objects.get(user=request.user, email_id=email)
            except Exception:
                campaign_user_obj = CampaignAuthUser.objects.create(user=request.user, email_id=email)

            otp = random.randrange(10**5, 10**6)

            if campaign_user_obj.otp_sent_count >= 5:
                response['status_message'] = 'Too many requests. Please try again later.'
            else:
                if campaign_user_obj.last_otp_sent_time and (timezone.now() - campaign_user_obj.last_otp_sent_time).total_seconds() > 3600:
                    campaign_user_obj.otp_sent_count = 0
                        
                campaign_user_obj.otp = otp
                campaign_user_obj.is_otp_expired = False
                campaign_user_obj.last_otp_sent_time = datetime.now()
                campaign_user_obj.otp_sent_count += 1
                campaign_user_obj.save()

                config_obj = get_config_obj(CampaignConfig)
                session_time = config_obj.session_time

                send_otp_mail(email, str(otp), str(session_time))

                response["status"] = "200"
                response["status_message"] = "OTP sent successfully."

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SendOTPAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["status_message"] = e

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SendOTP = SendOTPAPI.as_view()


"""

VerifyUserAPI : matches sent otp with the entered otp

"""


class VerifyUserAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            otp = data['otp']
            email = data['email']

            campaign_user_obj = CampaignAuthUser.objects.get(user=request.user, email_id=email)

            # OTP expires in 15 minutes
            if campaign_user_obj.is_otp_expired or (timezone.now() - campaign_user_obj.last_otp_sent_time).total_seconds() > 900:
                campaign_user_obj.is_otp_expired = True
                campaign_user_obj.save()

                response['status_message'] = "Please enter valid otp."
            else:
                if otp == campaign_user_obj.otp:
                    config_obj = get_config_obj(CampaignConfig)
                    session_time = config_obj.session_time
                    campaign_user_obj.expire_datetime = datetime.now() + timedelta(hours=session_time)
                    campaign_user_obj.is_otp_expired = True
                    campaign_user_obj.is_token_expired = False
                    campaign_user_obj.save()

                    response['access_token'] = str(campaign_user_obj.access_token)
                    response["status"] = "200"
                    response["status_message"] = "User Verified."
                else:
                    response['status_message'] = "Please enter valid otp."
                
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("VerifyUserAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["status_message"] = e

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


VerifyUser = VerifyUserAPI.as_view()


"""

GetSelectedCampaignCodeAPI : returnse api code for selected campaign

"""


class GetSelectedBotWSPCodeAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["status_message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            bot_pk = data['bot_pk']
            bot_obj = Bot.objects.get(pk=int(bot_pk))

            wsp_code = data["wsp_code"]
            is_reset = data["is_reset"]

            if request.user not in bot_obj.users.all():
                response['status_message'] = 'You are not authorised to access this code.'
            else:
                wsp_obj = CampaignWhatsAppServiceProvider.objects.get(name=wsp_code)

                bot_wsp_obj = CampaignBotWSPConfig.objects.filter(bot=bot_obj, whatsapp_service_provider=wsp_obj).first()

                if bot_wsp_obj and not is_reset:
                    code = bot_wsp_obj.code
                else:
                    file_obj = open(wsp_obj.default_code_file_path, "r")
                    code = file_obj.read()
                    file_obj.close()

                namespace = ""
                if bot_wsp_obj:
                    namespace = bot_wsp_obj.namespace

                response["api_code"] = code
                response["wsp_name"] = wsp_obj.get_name_display()
                response["wsp_code"] = wsp_code
                response["namespace"] = namespace
                response["status"] = 200
                response["status_message"] = "Success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetSelectedBotWSPCodeAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["status_message"] = str(e)

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetSelectedBotWSPCode = GetSelectedBotWSPCodeAPI.as_view()


class SaveCampaignAPICodeAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            wsp_code = data['wsp_code']
            code = data['code']
            bot_pk = data['bot_pk']
            namespace = data['namespace']

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response['status_message'] = 'You are not authorised to make changes in this code.'
            else:
                if check_for_system_commands(code, CampaignConfig):
                    response["status"] = 400
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                wsp_obj = CampaignWhatsAppServiceProvider.objects.get(name=wsp_code)
                bot_wsp_obj = CampaignBotWSPConfig.objects.filter(bot=bot_obj, whatsapp_service_provider=wsp_obj).first()

                if bot_wsp_obj:
                    bot_wsp_obj.code = code
                else:
                    bot_wsp_obj = CampaignBotWSPConfig.objects.create(bot=bot_obj, whatsapp_service_provider=wsp_obj)
                    bot_wsp_obj.code = code

                if wsp_code == "1":  # 1 is default value for Ameyo
                    bot_wsp_obj.namespace = namespace

                set_value_to_cache(CACHE_KEY_CAMPAIGN_BOT_WSP_CONFIG, str(bot_wsp_obj.pk), code)
                
                bot_wsp_obj.save()

            response['status_message'] = 'Changes Saved Successfully.'
            response['status'] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveCampaignAPICodeAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["status_message"] = e

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCampaignAPICode = SaveCampaignAPICodeAPI.as_view()


class MarkAPIIntegrationCompletedAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            campaign_id = data['campaign_id']
            access_token = data['access_token']
            bot_pk = data['bot_pk']

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response['status_message'] = 'You are not authorised to change status of this API.'
            else:
                campaign_user_obj = CampaignAuthUser.objects.get(access_token=access_token)

                if campaign_user_obj.is_token_expired or timezone.now() > campaign_user_obj.expire_datetime:
                    campaign_user_obj.is_token_expired = True
                    campaign_user_obj.save()

                    response['status_message'] = 'We cannot process your request because your session has expired.'
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

                campaign_obj = Campaign.objects.get(pk=int(campaign_id), bot=bot_obj)
                
                api_obj = CampaignAPI.objects.get(campaign=campaign_obj)
                api_obj.is_api_completed = True
                api_obj.api_complete_datetime = timezone.now()
                api_obj.save()

                response['status_message'] = 'API Integration marked completed successfully.'
                response['status'] = 200
                        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("MarkAPIIntegrationCompletedAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["status_message"] = e

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


MarkAPIIntegrationCompleted = MarkAPIIntegrationCompletedAPI.as_view()


class CampaignAPIRunAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        response["elapsed_time"] = "0.0000"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            code = data["code"]
            bot_pk = data['bot_pk']

            bot_pk = data['bot_pk']

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response['message'] = 'You are not authorised to run this code.'
            else:

                if check_for_system_commands(code, CampaignConfig):
                    response["status"] = 400
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                start_time = time.time()

                processor_check_dictionary = {'open': open_file}
                exec(str(code), processor_check_dictionary)
                json_data = processor_check_dictionary['f'](json.dumps({}))

                end_time = time.time()

                elapsed_time = end_time - start_time

                response["elapsed_time"] = str(elapsed_time)

                response["message"] = json_data
                response['status'] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EasyChatProcessorRunAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response["status"] = 300
            response["message"] = str(e)

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)

CampaignAPIRun = CampaignAPIRunAPI.as_view()


class ExtendCampaignAPIUserSessionAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["status_message"] = "Internal server Error"
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            access_token = data['access_token']

            campaign_user_obj = CampaignAuthUser.objects.get(access_token=access_token)

            if campaign_user_obj.is_token_expired or timezone.now() > campaign_user_obj.expire_datetime:
                response['status_message'] = 'Unable to extend session.'
            else:
                config_obj = get_config_obj(CampaignConfig)
                
                session_time = config_obj.session_time
                campaign_user_obj.expire_datetime = datetime.now() + timedelta(hours=session_time)
                campaign_user_obj.save()
            
                response['expire_time_seconds'] = campaign_user_obj.expire_datetime.timestamp()
                response['status_message'] = 'Session extended successfully.'
                response['status'] = 200
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExtendCampaignAPIUserSessionAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["status_message"] = e

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExtendCampaignAPIUserSession = ExtendCampaignAPIUserSessionAPI.as_view()
