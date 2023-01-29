from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
import openpyxl

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
import os
from CampaignApp.utils_validation import CampaignInputValidation

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


class GetCampaignBatchesAPI(APIView):

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
            bot_pk = data["bot_pk"]
            campaign_id = data["campaign_id"]
            campaign_channel = data["campaign_channel"]
            searched_batch = data["searched_batch"]
            selected_batch_id = data.get('selected_batch_id', 0)
            selected_campaign_id = data.get('selected_campaign_id')
            campaign_obj = Campaign.objects.get(pk=int(campaign_id))

            selected_batch = None

            if not selected_batch_id:
                selected_batch = campaign_obj.batch
                if selected_batch:
                    selected_batch_id = selected_batch.pk
                else:
                    selected_batch_id = 0
            else:
                selected_batch = CampaignBatch.objects.filter(pk=selected_batch_id).first()

            response['selected_batch_id'] = selected_batch_id
            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if selected_campaign_id:
                selected_campaign_obj = Campaign.objects.get(pk=int(selected_campaign_id))
                if campaign_channel == 'RCS':
                    campaign_batch_objs = CampaignBatch.objects.filter(bot=bot_obj, channel__name=campaign_channel, campaigns__in=[selected_campaign_obj])
                else:
                    campaign_batch_objs = CampaignBatch.objects.filter(~Q(channel__name='RCS'), bot=bot_obj, campaigns__in=[
                                                                       selected_campaign_obj], channel__is_deleted=False)
            else:
                if campaign_channel == 'RCS':
                    campaign_batch_objs = CampaignBatch.objects.filter(bot=bot_obj, channel__name=campaign_channel)
                else:
                    campaign_batch_objs = CampaignBatch.objects.filter(
                        ~Q(channel__name='RCS'), bot=bot_obj, channel__is_deleted=False)

            if searched_batch:
                campaign_batch_objs = campaign_batch_objs.filter(
                    batch_name__icontains=searched_batch)

            campaign_batch_objs = campaign_batch_objs.order_by('-created_datetime')

            total_rows_per_pages = 100
            total_campaign_objs = campaign_batch_objs.count()

            campaign_batches = []
            if selected_batch and not selected_campaign_id and not searched_batch:
                campaign_batch_objs = campaign_batch_objs.exclude(
                    pk=selected_batch.pk)
                campaign_batches.append(
                    parse_campaign_batch_details(selected_batch))

            paginator = Paginator(
                campaign_batch_objs, total_rows_per_pages)

            try:
                campaign_batch_objs = paginator.page(page)
            except PageNotAnInteger:
                campaign_batch_objs = paginator.page(1)
            except EmptyPage:
                campaign_batch_objs = paginator.page(paginator.num_pages)

            if page != None:
                start_point = total_rows_per_pages * (int(page) - 1) + 1
                end_point = min(total_rows_per_pages *
                                int(page), total_campaign_objs)
                if start_point > end_point:
                    start_point = max(end_point - len(campaign_batch_objs) + 1, 1)
            else:
                start_point = 1
                end_point = min(total_rows_per_pages, total_campaign_objs)

            start_point = min(start_point, end_point)

            pagination_range = campaign_batch_objs.paginator.page_range

            has_next = campaign_batch_objs.has_next()
            has_previous = campaign_batch_objs.has_previous()
            next_page_number = -1
            previous_page_number = -1

            if has_next:
                next_page_number = campaign_batch_objs.next_page_number()
            if has_previous:
                previous_page_number = campaign_batch_objs.previous_page_number()

            pagination_metadata = {
                'total_count': total_campaign_objs,
                'start_point': start_point,
                'end_point': end_point,
                'page_range': [pagination_range.start, pagination_range.stop],
                'has_next': has_next,
                'has_previous': has_previous,
                'next_page_number': next_page_number,
                'previous_page_number': previous_page_number,
                'number': campaign_batch_objs.number,
                'num_pages': campaign_batch_objs.paginator.num_pages
            }

            for campaign_obj in campaign_batch_objs:
                campaign_batches.append(parse_campaign_batch_details(
                    campaign_obj))
            if campaign_channel == 'RCS':
                campaign_objs = Campaign.objects.filter(
                    bot=bot_obj, channel__name='RCS', is_deleted=False)
            else:
                campaign_objs = Campaign.objects.filter(
                    bot=bot_obj, is_deleted=False).exclude(channel__name='RCS')
            response['campaign_objs'] = list(campaign_objs.values_list('pk', 'name'))
            response["status"] = 200
            response["message"] = "success"
            response["campaign_batches"] = campaign_batches
            response["pagination_metadata"] = pagination_metadata
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCampaignBatchesAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCampaignBatches = GetCampaignBatchesAPI.as_view()


class DownloadCampaignBatchTemplateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            campaign_channel = data['campaign_channel']
            if campaign_channel == 'RCS':
                export_path = ("/files/templates/campaign" +
                               "/Audience_Batch_Sample_RCS_Campaign.xlsx")
            elif campaign_channel == "Voice Bot":
                export_path = ("/files/templates/campaign" +
                               "/Audience_Batch_Sample_Voice_Bot_Campaign.xlsx")
            else:
                export_path = ("/files/templates/campaign" +
                               "/Audience_Batch_Sample_WhatsApp_Campaign.xlsx")
            export_path_exist = os.path.exists(export_path[1:])
            
            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DownloadCampaignBatchTemplateAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["message"] = str(e)

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)

DownloadCampaignBatchTemplate = DownloadCampaignBatchTemplateAPI.as_view()


class DownloadCampaignBatchFileAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            batch_id = data["batch_id"]
            bot_pk = data["bot_pk"]

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            batch_objs = CampaignBatch.objects.filter(bot=bot_obj, pk=int(batch_id))
            if batch_objs.exists():
                batch_obj = batch_objs.first()
                response["download_file_path"] = batch_obj.file_path
                response["download_file_name"] = batch_obj.file_name
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DownloadCampaignBatchFileAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["message"] = str(e)

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)

DownloadCampaignBatchFile = DownloadCampaignBatchFileAPI.as_view()


class UploadNewBatchAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response["status_message"] = "Unable to upload batch file"
        custom_encrypt_obj = CustomEncrypt()
        try:
            batch_file = request.data["file"]
            params = request.data["params"]
            params = json.loads(params)
            data = params["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            original_file_name = data["filename"]
            filename, file_extention = original_file_name.split(".")
            filename = strip_html_tags(filename)
            audience_data = batch_file.read()
            campaign_channel = strip_html_tags(data["campaign_channel"])
            bot_id = strip_html_tags(data["bot_id"])
            auto_delete_checked = data["auto_delete_checked"]
            error_rows = data["error_rows"]
            bot_objs = Bot.objects.filter(
                pk=int(bot_id), is_deleted=False, is_uat=True)

            if bot_objs.exists():
                bot_obj = bot_objs.first()
            else:
                response["status"] = 401
                response["status_message"] = "Bot does not exists."
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['status_message'] = 'You are not authorised to perform this operation.'
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            if check_running_upload_events(request.user, bot_obj, "upload_batch", 3):
                response["status"] = 400
                response[
                    "message"] = "You have reached the maximum limit of 3 concurrent file upload allowed in multiple tabs, please wait while one of the files get uploaded successfully."
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            filename = generate_random_key(
                10) + "_" + filename.replace(" ", "")

            file_extention = file_extention.lower()

            allowed_files_list = ["xls", "xlsx", "csv", "psv"]
            if file_extention in allowed_files_list:
                media_type = "excel"
            else:
                media_type = None

            if media_type == None or check_malicious_file_from_filename(original_file_name, allowed_files_list) or check_malicious_file_from_content(audience_data, allowed_files_list):
                response["status"] = 400
                response["message"] = "The file could not be uploaded. Only files with the following extensions are allowed: XLS, XLSX, and CSV."
            else:
                if not os.path.exists('secured_files/CampaignApp/campaign_batch'):
                    os.makedirs(
                        'secured_files/CampaignApp/campaign_batch')

                file_path = f"secured_files/CampaignApp/campaign_batch/{filename}.{file_extention}"
                fh = open(file_path, "wb")
                fh.write(audience_data)
                fh.close()

                if file_extention in ["csv", "psv"]:
                    if file_extention == "psv":
                        delimiter = "|"
                    else:
                        delimiter = ","
                    with open(file_path, 'r') as csv_sheet:
                        max_row, max_column, is_pipe = get_csv_sheet_details(csv_sheet, delimiter)
                    if is_pipe:
                        delimiter = '|'
                    metadata = {"max_row": max_row, "max_column": max_column, "delimiter": delimiter,
                                "auto_delete_checked": auto_delete_checked, "error_rows": error_rows}
                    if max_row > CAMPAIGN_MAXIMUM_AUDIENCE_CSV_BATCH_LIMIT:
                        response["status"] = 400
                        response[
                            "message"] = "Batch size too large. Upto 1,048,575 entries are allowed in a batch(Try deleting the empty rows in-between other entries if any)"
                    else:
                        response["status"] = 200
                        response["message"] = "success"
                        event_obj = create_campaign_event_progress_tracker_obj(request.user, bot_obj, "upload_batch")
                        thread = threading.Thread(target=csv_sample_data_wrapper_function, args=(file_path, Profile, campaign_channel, original_file_name,
                                                                                                    event_obj, bot_obj, response["status_message"], metadata))
                        thread.daemon = True
                        thread.start()
                else:
                    workbook = xlrd.open_workbook(file_path)
                    sheet = workbook.sheet_by_index(0)
                    max_row, max_column = sheet.nrows, sheet.ncols

                    metadata = {"max_row": max_row, "max_column": max_column,
                                "auto_delete_checked": auto_delete_checked, "error_rows": error_rows}

                    if max_row > CAMPAIGN_MAXIMUM_AUDIENCE_BATCH_LIMIT:
                        response["status"] = 400
                        response[
                            "message"] = "Batch size too large. Upto 1,048,575 entries are allowed in a batch(Try deleting the empty rows in-between other entries if any)"
                    else:
                        response["status"] = 200
                        response["message"] = "success"
                        event_obj = create_campaign_event_progress_tracker_obj(request.user, bot_obj, "upload_batch")
                        thread = threading.Thread(target=sample_data_wrapper_function, args=(file_path, Profile, campaign_channel, sheet, original_file_name,
                                                                                                event_obj, bot_obj, response["status_message"], metadata))
                        thread.daemon = True
                        thread.start()

                if event_obj:
                    response["event_progress_id"] = event_obj.pk
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadNewBatchAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadNewBatch = UploadNewBatchAPI.as_view()


class SaveCampaignBatchAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            batch_name = data['batch_name']
            batch_name = batch_name.strip()
            batch_name = remo_html_from_string(batch_name)
            batch_name = remo_special_tag_from_batch_name(batch_name)

            batch_header_meta = data['batch_header_meta']
            sample_data = data['sample_data']
            total_audience = data['total_audience']
            total_opted_in = data['total_opted_in']
            file_path = data['file_path']
            file_name = data["file_name"]
            bot_pk = data["bot_pk"]
            campaign_channel = data["campaign_channel"]

            bot_obj = Bot.objects.get(pk=int(bot_pk))
            campaign_channel_obj = CampaignChannel.objects.get(name=campaign_channel)

            if request.user not in bot_obj.users.all():
                response["message"] = "You are not authorised to upload campaign batch for this bot."
            else:
                if 'batch_id' in data and data['batch_id'] != '':
                    batch_id = data['batch_id']

                    campaign_batch_obj = CampaignBatch.objects.filter(pk=int(batch_id), bot=bot_obj)

                    if not campaign_batch_obj:
                        response["message"] = "You are not authorised to edit campaign batch for this bot."
                    else:
                        batch_obj = CampaignBatch.objects.filter(batch_name=batch_name, bot=bot_obj)

                        if batch_obj and batch_obj[0].pk != int(batch_id):
                            response["message"] = "A batch with same batch name already exists. Please use different batch name."
                        else:
                            campaign_batch_obj = campaign_batch_obj[0]

                            is_active_campaign_exists, campaign_name = get_active_campaign_usign_batch_id(campaign_batch_obj)

                            if is_active_campaign_exists:
                                response['message'] = "A campaign with name '" + campaign_name + "' is in progress on this batch so you cannot edit it."
                            else:
                                campaign_batch_obj.batch_name = batch_name
                                campaign_batch_obj.batch_header_meta = json.dumps(batch_header_meta)
                                campaign_batch_obj.sample_data = json.dumps(sample_data)
                                campaign_batch_obj.total_audience = total_audience
                                
                                if file_path != campaign_batch_obj.file_path:
                                    campaign_batch_obj.total_audience_opted = total_opted_in
                                    key = campaign_batch_obj.file_path.split('/')[-2]
                                    delete_file_by_key(key, CampaignFileAccessManagement)
                                
                                campaign_batch_obj.file_path = file_path
                                campaign_batch_obj.file_name = file_name
                                campaign_batch_obj.bot = bot_obj
                                campaign_batch_obj.channel = campaign_channel_obj
                                campaign_batch_obj.save()

                                response["status"] = 200
                                response["message"] = "success"
                else:

                    campaign_batch_obj = CampaignBatch.objects.filter(batch_name=batch_name, bot=bot_obj)

                    if campaign_batch_obj:
                        response["message"] = "A batch with same batch name already exists. Please use different batch name."
                    else:
                        campaign_batch_obj = CampaignBatch.objects.create(batch_name=batch_name)
                        campaign_batch_obj.batch_header_meta = json.dumps(batch_header_meta)
                        campaign_batch_obj.sample_data = json.dumps(sample_data)
                        campaign_batch_obj.total_audience = total_audience
                        campaign_batch_obj.total_audience_opted = total_opted_in
                        campaign_batch_obj.file_path = file_path
                        campaign_batch_obj.file_name = file_name
                        campaign_batch_obj.bot = bot_obj
                        campaign_batch_obj.channel = campaign_channel_obj
                        campaign_batch_obj.save()

                        response["status"] = 200
                        response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCampaignBatchAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCampaignBatch = SaveCampaignBatchAPI.as_view()


class DeleteUploadedBatchFileAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['message'] = 'Failed to delete file.'

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            file_path = data['file_path']
            bot_pk = data['bot_pk']

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response['message'] = 'You are not authorised to delete batch file'
            else:
                key = file_path.split('/')[-2]

                is_deleted = delete_file_by_key(key, CampaignFileAccessManagement)

                if not is_deleted:
                    response['message'] = 'File does not exist.'
                else:
                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteUploadedBatchFileAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteUploadedBatchFile = DeleteUploadedBatchFileAPI.as_view()


class DeleteBatchAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['message'] = 'Failed to delete batch.'

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            batch_id = data['batch_id']
            bot_pk = data['bot_pk']

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response['message'] = 'You are not authorised to delete this batch.'
            else:
                campaign_batch_obj = CampaignBatch.objects.filter(pk=int(batch_id))

                if campaign_batch_obj:
                    campaign_batch_obj = campaign_batch_obj[0]
                    is_active_campaign_exists, campaign_name = get_active_campaign_usign_batch_id(campaign_batch_obj)

                    if is_active_campaign_exists:
                        response['message'] = "A campaign with name '" + campaign_name + "' is in progress on this batch so you cannot delete it."
                    else:
                        campaign_batch_obj.delete()

                        response['status'] = 200
                        response['message'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteBatchAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteBatch = DeleteBatchAPI.as_view()


class AddBatchToCampaignAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['message'] = 'Failed to add batch.'

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            batch_id = data['selected_batch_id']
            campaign_id = data['campaign_id']
            bot_pk = data['bot_pk']

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response['message'] = 'You are not authorised to perform this operation.'
            else:
                campaign_batch_obj = CampaignBatch.objects.filter(pk=int(batch_id))

                if campaign_batch_obj:
                    campaign_obj = Campaign.objects.get(pk=int(campaign_id))

                    if campaign_obj.status == CAMPAIGN_IN_PROGRESS:
                        response['status'] = 401
                        response['campaign_id'] = campaign_id
                        response['message'] = 'Not able to assign batch. Campaign is in progress'
                    else:
                        campaign_obj.batch = campaign_batch_obj[0]
                        campaign_obj.total_audience = campaign_batch_obj[0].total_audience
                        campaign_obj.last_saved_state = CAMPAIGN_TAG_AUDIENCE_STATE
                        campaign_obj.save()

                        campaign_batch_obj[0].campaigns.add(campaign_obj)
                        campaign_batch_obj[0].save()

                        response['status'] = 200
                        response['campaign_id'] = campaign_id
                        response['message'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddBatchToCampaignAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddBatchToCampaign = AddBatchToCampaignAPI.as_view()


class GetTestAudienceDataAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['message'] = 'Failed to fetch batch.'

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            campaign_id = data.get('campaign_id')
            campaign_obj = Campaign.objects.filter(pk=campaign_id).first()
            if request.user not in campaign_obj.bot.users.all():
                response['message'] = 'You are not authorised to save campaign for this bot.'
            else:
                sample_data = []
                campaign_batch = campaign_obj.batch
                max_row = data.get('max_row', 0) + 1
                file_path = campaign_batch.file_path
                file_name = campaign_batch.file_name
                file_extention = file_name.split('.')[-1]
                file_key = file_path.split('/')[-2]

                file_access = CampaignFileAccessManagement.objects.filter(
                    key=file_key).first()
                if file_access:
                    file_path = file_access.file_path

                if file_extention in ["csv", "psv"]:
                    if file_extention == "psv":
                        delimiter = "|"
                    else:
                        delimiter = ","

                    with open(file_path, 'r') as csv_sheet:
                        _, max_column, is_pipe = get_csv_sheet_details(
                            csv_sheet, delimiter)
                    if is_pipe:
                        delimiter = "|"
                    csv_sheet = open(file_path, 'r')
                    csv_reader = csv.reader(csv_sheet, delimiter=delimiter)
                    next(csv_reader)
                    row_processed = 1

                    for row in csv_reader:
                        mobile_number = row[0]
                        if row_processed < max_row:
                            row_data_value = [mobile_number]
                            for col_index in range(1, max_column):
                                value = row[col_index] if col_index < len(
                                    row) else '-'
                                row_data_value.append(clean_input(
                                    value) if value and value != '-' else '-')
                            sample_data.append(row_data_value)
                        else:
                            break
                        row_processed += 1
                else:
                    workbook = xlrd.open_workbook(file_path)
                    sheet = workbook.sheet_by_index(0)
                    max_column = sheet.ncols
                    for row in range(1, max_row):
                        if row < max_row:
                            sample_data.append(
                                get_sample_data(sheet, max_column, row))

                batch_header_meta = campaign_batch.batch_header_meta
                if batch_header_meta:
                    batch_header_meta = json.loads(batch_header_meta)

            response['header_name'] = batch_header_meta
            response['sample_data'] = sample_data
            response['status'] = 200
            response['message'] = 'Fetched Data'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetTestAudienceDataAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetTestAudienceData = GetTestAudienceDataAPI.as_view()
