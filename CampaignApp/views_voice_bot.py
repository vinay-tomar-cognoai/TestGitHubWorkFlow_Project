from distutils.command.clean import clean
from tracemalloc import start
from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from numpy import tri

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
from tenacity import retry

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
import os


import pytz
import uuid
import sys
from datetime import datetime, date, timedelta
import threading


# Logger
import logging
logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class SaveTriggerSettingsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            campaign_id = data['campaign_id']
            campaign_id = clean_input(campaign_id)

            caller_id = data['caller_id']
            caller_id = clean_input(caller_id)

            start_date = data['start_date']
            start_date = datetime.strptime(
                start_date, DATE_FORMAT).date()

            end_date = data['end_date']
            end_date = datetime.strptime(
                end_date, DATE_FORMAT).date()

            start_time = data['start_time']
            start_time = datetime.strptime(
                start_time, TIME_FORMAT)

            end_time = data['end_time']
            end_time = datetime.strptime(
                end_time, TIME_FORMAT)

            retry_mechanism = data['retry_mechanism']
            no_of_retries = data['no_of_retries']
            retry_interval = data['retry_interval']
            is_busy_enabled = data['is_busy_enabled']
            is_no_answer_enabled = data['is_no_answer_enabled']
            is_failed_enabled = data['is_failed_enabled']

            campaign_obj = Campaign.objects.get(pk=int(campaign_id))
            trigger_setting_obj = CampaignVoiceBotSetting.objects.filter(
                campaign=campaign_obj)

            if trigger_setting_obj:
                trigger_setting_obj = trigger_setting_obj.first()

                trigger_setting_obj.caller_id = caller_id
                trigger_setting_obj.start_date = start_date
                trigger_setting_obj.end_date = end_date
                trigger_setting_obj.start_time = start_time
                trigger_setting_obj.end_time = end_time

                app_id = get_app_id_from_caller_id(caller_id, VoiceBotCallerID)

                check_and_create_campaign_users(trigger_setting_obj)

                trigger_setting_obj.app_id = app_id
                trigger_setting_obj.is_saved = True
                trigger_setting_obj.save()

                retry_setting = trigger_setting_obj.retry_setting

                retry_setting.mechanism = retry_mechanism
                retry_setting.no_of_retries = no_of_retries
                retry_setting.retry_interval = retry_interval
                retry_setting.is_busy_enabled = is_busy_enabled
                retry_setting.is_no_answer_enabled = is_no_answer_enabled
                retry_setting.is_failed_enabled = is_failed_enabled
                retry_setting.save()

                campaign_obj.last_saved_state = CAMPAIGN_SETTINGS_STATE
                campaign_obj.save()

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveTriggerSettingsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveTriggerSettings = SaveTriggerSettingsAPI.as_view()


class SendVoiceBotCampaignAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            campaign_id = data['campaign_id']
            campaign_id = clean_input(campaign_id)

            campaign_obj = Campaign.objects.filter(pk=int(campaign_id))

            if campaign_obj:
                campaign_obj = campaign_obj.first()
                voice_bot_obj = CampaignVoiceBotSetting.objects.get(
                    campaign=campaign_obj)

                trigger_setting = parse_trigger_settings(voice_bot_obj)

                user_details, _ = get_user_details_from_batch(
                    campaign_obj.batch, CampaignFileAccessManagement)

                start_date = voice_bot_obj.start_date
                start_time = voice_bot_obj.start_time

                start_date = datetime(start_date.year, start_date.month, start_date.day, start_time.hour, start_time.minute)

                if start_date < datetime.now():
                    response['status'] = 400
                    response['message'] = 'Cannot start campaign for past date'
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)

                trigger_setting['campaign_id'] = campaign_id
                trigger_setting['app_id'] = voice_bot_obj.app_id
                trigger_setting['from'] = get_mob_numbers_from_user_details(
                    user_details)
                trigger_setting['name'] = campaign_obj.name
                trigger_setting['send_at_date'] = str(voice_bot_obj.start_date)
                trigger_setting['send_at_time'] = str(voice_bot_obj.start_time)
                trigger_setting['end_at_date'] = str(voice_bot_obj.end_date)
                trigger_setting['end_at_time'] = str(voice_bot_obj.end_time)
                trigger_setting['call_status_callback'] = f'{settings.EASYCHAT_HOST_URL}/campaign/call-end-call-back/'
                trigger_setting['status_callback'] = f'{settings.EASYCHAT_HOST_URL}/campaign/campaign-end-call-back/'
                trigger_setting['bot_id'] = str(campaign_obj.bot.pk)

                api_obj = check_and_create_voice_bot_api_obj(
                    campaign_obj, CampaignVoiceBotAPI)
                api_code = api_obj.api_code

                processor_check_dictionary = {'open': open_file}

                exec(str(api_code), processor_check_dictionary)

                if voice_bot_obj.campaign_sid and voice_bot_obj.campaign_sid != '':
                    trigger_setting['campaign_sid'] = voice_bot_obj.campaign_sid
                    json_data = processor_check_dictionary['update_campaign'](
                        json.dumps(trigger_setting))
                else:
                    json_data = processor_check_dictionary['create_campaign'](
                        json.dumps(trigger_setting))

                request_body = json_data['request']
                response_body = json_data['response']

                voice_bot_obj.request = request_body
                voice_bot_obj.response = response_body
                voice_bot_obj.url = request_body['campaigns'][0]['url']
                voice_bot_obj.save()

                if response_body['response'][0]['code'] == 200:
                    campaign_obj.status = CAMPAIGN_SCHEDULED
                    voice_bot_obj.campaign_sid = response_body['response'][0]['data']['id']
                    campaign_obj.is_source_dashboard = True  # True because campaign is being sent from GUI
                    campaign_obj.save(update_fields=['status', 'is_source_dashboard'])
                    voice_bot_obj.save()

                response["status"] = 200
                response["message"] = "success"
                response["response"] = response_body
            else:
                response['status'] = 500
                response['message'] = 'Campaign does not exist'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SendVoiceBotCampaignAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SendVoiceBotCampaign = SendVoiceBotCampaignAPI.as_view()


class CampaignEndCallBackAPI(APIView):

    def post(self, request, *args, **kwargs):
        try:
            logger.info("request %s",
                         str(request.data), extra={'AppName': 'Campaign'})

            data = request.data

            campaign_sid = data['campaign_sid']
            status = data['status']

            voice_bot_obj = CampaignVoiceBotSetting.objects.filter(
                campaign_sid=campaign_sid).first()

            if voice_bot_obj:
                campaign_obj = voice_bot_obj.campaign

                if status.lower() == 'inprogress':
                    campaign_obj.status = CAMPAIGN_IN_PROGRESS
                elif status.lower() == 'failed':
                    campaign_obj.status = CAMPAIGN_PARTIALLY_COMPLETED
                    update_voice_campaign_user_call_status(voice_bot_obj)
                elif status.lower() == 'completed':
                    campaign_obj.status = CAMPAIGN_COMPLETED
                    update_voice_campaign_user_call_status(voice_bot_obj)

                campaign_obj.save()

            return HttpResponse(status=200)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CallBackAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


CampaignEndCallBack = CampaignEndCallBackAPI.as_view()


class CallEndCallBackAPI(APIView):

    def post(self, request, *args, **kwargs):
        try:
            logger.info("request %s",
                         str(request.data), extra={'AppName': 'Campaign'})
            
            data = request.data

            campaign_sid = data['campaign_sid']

            voice_bot_obj = CampaignVoiceBotSetting.objects.filter(campaign_sid=campaign_sid).first()

            if voice_bot_obj:
                campaign_obj = voice_bot_obj.campaign

                call_details_obj = check_and_create_call_details_obj(campaign_obj, data['call_sid'], CampaignVoiceBotDetailedAnalytics)

                call_details_obj.from_number = data['from']
                call_details_obj.to_number = voice_bot_obj.caller_id
                call_details_obj.status = data['legs'][0]['status']
                
                call_details_obj.date_created = datetime.strptime(data['date_created'], "%Y-%m-%dT%H:%M:%S%z")
                call_details_obj.date_updated = datetime.strptime(data['date_updated'], "%Y-%m-%dT%H:%M:%S%z")
                
                call_details_obj.total_duration = data['duration']
                
                audience_unique_id = json.loads(voice_bot_obj.request).get('clients_data_dict', {})
                unique_id = audience_unique_id.get(data['from'], {}).get('unique_id', '')
                if unique_id:
                    unique_id = get_audience_unique_id(unique_id)
                call_details_obj.audience_unique_id = unique_id

                if data['legs']:
                    call_details_obj.on_call_duration = data['legs'][0]['on_call_duration']

                call_details_obj.save()

                voice_campaign_user_obj = CampaignVoiceUser.objects.filter(voice_campaign=voice_bot_obj, mobile_number=data['from']).first()
                if voice_campaign_user_obj:
                    if data["status"] == "completed":
                        voice_campaign_user_obj.status = "completed"
                    elif data["status"] == "no-answer":
                        voice_campaign_user_obj.status = "rejected"
                    else:
                        voice_campaign_user_obj.status = "failed"

                    voice_campaign_user_obj.call_sid = data["call_sid"]
                    voice_campaign_user_obj.duration = data["duration"]
                    if data['legs']:
                        voice_campaign_user_obj.on_call_duration = data['legs'][0]['on_call_duration']
                    voice_campaign_user_obj.date = datetime.strptime(data['date_created'].split("T")[0], "%Y-%m-%d").date()
                    voice_campaign_user_obj.time = datetime.strptime(data['date_created'].split("T")[1][:8], "%H:%M:%S").time()
                    voice_campaign_user_obj.save()

            return HttpResponse(status=200)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CallBackAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            return HttpResponse(status=500)


CallEndCallBack = CallEndCallBackAPI.as_view()


"""

VoiceCampaignDetailsPage() : Renders voice bot campaign details page

"""


@login_required(login_url="/chat/login")
def VoiceCampaignDetailsPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        bot_pk = request.GET['bot_pk']
        bot_obj = Bot.objects.get(pk=int(bot_pk))

        campaign_id = request.GET['campaign_id']

        selected_campaign_obj = Campaign.objects.filter(pk=campaign_id).first()

        campaign_objs = Campaign.objects.filter(channel__name="Voice Bot", bot=bot_obj, is_deleted=False)

        start_date = (datetime.now() - timedelta(7)).date()
        end_date = datetime.now().date()

        if request.user in bot_obj.users.all():
            return render(request, "CampaignApp/voice_campaign_details.html", {
                "selected_bot_obj": bot_obj,
                "selected_campaign_obj": selected_campaign_obj,
                "campaign_objs": campaign_objs,
                "start_date": str(start_date),
                "end_date": str(end_date)
            })
        else:
            return redirect("/campaign/unauthorised/")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error VoiceCampaignDetailsPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return render(request, 'CampaignApp/error_500.html')


class GetVoiceCampaignDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal Server Error"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            campaign_ids = data["campaign_ids"]
            bot_pk = data["bot_pk"]
            filter_date_type = data["filter_date_type"]
            status_filter = data["status_filter"]
            page = data["page"]

            bot_obj = Bot.objects.filter(pk=bot_pk).first()
            user = User.objects.get(username=request.user.username)

            if bot_obj and user in bot_obj.users.all():

                start_date = None
                end_date = None

                if filter_date_type == "1":
                    start_date = (datetime.now() - timedelta(days=7)).date()
                elif filter_date_type == "2":
                    start_date = (datetime.now() - timedelta(days=30)).date()
                elif filter_date_type == "3":
                    start_date = (datetime.now() - timedelta(days=90)).date()
                elif filter_date_type == "5":
                    start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
                    end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

                campaign_objs = Campaign.objects.filter(pk__in=campaign_ids)
                voice_campaign_objs = CampaignVoiceBotSetting.objects.filter(campaign__in=campaign_objs)
                voice_campaign_user_objs = CampaignVoiceUser.objects.filter(voice_campaign__in=voice_campaign_objs)

                if start_date:
                    voice_campaign_user_objs = voice_campaign_user_objs.filter(date__gte=start_date)
                if end_date:
                    voice_campaign_user_objs = voice_campaign_user_objs.filter(date__lte=end_date)

                if len(status_filter):
                    voice_campaign_user_objs = voice_campaign_user_objs.filter(status__in=status_filter)

                voice_campaign_user_objs = voice_campaign_user_objs.order_by("-pk")
                total_rows_per_pages = 20
                total_voice_campaign_user_objs = voice_campaign_user_objs.count()

                paginator = Paginator(
                    voice_campaign_user_objs, total_rows_per_pages)

                try:
                    voice_campaign_user_objs = paginator.page(page)
                except PageNotAnInteger:
                    voice_campaign_user_objs = paginator.page(1)
                except EmptyPage:
                    voice_campaign_user_objs = paginator.page(paginator.num_pages)

                if page != None:
                    start_point = total_rows_per_pages * (int(page) - 1) + 1
                    end_point = min(total_rows_per_pages *
                                    int(page), total_voice_campaign_user_objs)
                    if start_point > end_point:
                        start_point = max(end_point - len(voice_campaign_user_objs) + 1, 1)
                else:
                    start_point = 1
                    end_point = min(total_rows_per_pages, total_voice_campaign_user_objs)

                start_point = min(start_point, end_point)

                pagination_range = voice_campaign_user_objs.paginator.page_range

                has_next = voice_campaign_user_objs.has_next()
                has_previous = voice_campaign_user_objs.has_previous()
                next_page_number = -1
                previous_page_number = -1

                if has_next:
                    next_page_number = voice_campaign_user_objs.next_page_number()
                if has_previous:
                    previous_page_number = voice_campaign_user_objs.previous_page_number()

                pagination_metadata = {
                    'total_count': total_voice_campaign_user_objs,
                    'start_point': start_point,
                    'end_point': end_point,
                    'page_range': [pagination_range.start, pagination_range.stop],
                    'has_next': has_next,
                    'has_previous': has_previous,
                    'next_page_number': next_page_number,
                    'previous_page_number': previous_page_number,
                    'number': voice_campaign_user_objs.number,
                    'num_pages': voice_campaign_user_objs.paginator.num_pages
                }
                voice_campaign_data = []
                for voice_campaign_user_obj in voice_campaign_user_objs:
                    voice_campaign_data.append(get_voice_campaign_user_data(voice_campaign_user_obj))

                response["status"] = "200"
                response["message"] = "Success"
                response["data"] = voice_campaign_data
                response["pagination_metadata"] = pagination_metadata

            else:
                response["message"] = "You do not have access to this data"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCampaignDetailsAPI %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetVoiceCampaignDetails = GetVoiceCampaignDetailsAPI.as_view()


class SaveExportVoiceCampaignHistoryRequestAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal Server Error"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            bot_pk = data["bot_pk"]
            bot_obj = Bot.objects.filter(pk=bot_pk, is_deleted=False).first()

            user = User.objects.get(username=request.user.username)

            if bot_obj and user in bot_obj.users.all():
                
                VoiceCampaignHistoryExportRequest.objects.create(user=user, request_data=json.dumps(data))

                response["status"] = "200"
                response["message"] = "Success"

            else:
                response["message"] = "You do not have access to this data"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveExportVoiceCampaignHistoryRequestAPI %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)
            

SaveExportVoiceCampaignHistoryRequest = SaveExportVoiceCampaignHistoryRequestAPI.as_view()
