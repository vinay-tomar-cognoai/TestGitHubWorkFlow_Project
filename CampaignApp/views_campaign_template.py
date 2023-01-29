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

from CampaignApp.views_api_integration import *
from CampaignApp.views_tag_audience import *
from CampaignApp.utils_campaign_rcs import *
from EasyChatApp.utils_validation import EasyChatInputValidation

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


class GetCampaignTemplatesAPI(APIView):

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
            searched_template = data["searched_template"]

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            campaign_obj = Campaign.objects.get(
                pk=int(campaign_id), bot=bot_obj)

            channel_name = campaign_obj.channel.name

            if channel_name == 'RCS':
                campaign_template_objs = CampaignRCSTemplate.objects.filter(
                    is_deleted=False, bot=bot_obj)

            else:
                campaign_template_objs = CampaignTemplate.objects.filter(
                    is_deleted=False, bot=bot_obj)

            if searched_template:
                searched_template = searched_template.lower()
                campaign_template_objs = campaign_template_objs.filter(
                    template_name__icontains=searched_template)
            
            selected_template = None
            selected_template_pk = data.get('selected_template_pk', 0)
            
            if not selected_template_pk:
                if channel_name == 'RCS':
                    selected_template = campaign_obj.campaign_template_rcs
                else:
                    selected_template = campaign_obj.campaign_template
            else:
                if channel_name == 'RCS':
                    selected_template = campaign_template_objs.filter(
                        pk=selected_template_pk).first()
                else:
                    selected_template = campaign_template_objs.filter(
                        pk=selected_template_pk).first()

            response['selected_template_pk'] = selected_template.pk if selected_template else 0

            campaign_template_objs = campaign_template_objs.order_by(
                '-created_datetime')

            total_rows_per_pages = 100
            total_campaign_objs = campaign_template_objs.count()

            campaign_templates = []
            if selected_template and not searched_template:
                campaign_template_objs = campaign_template_objs.exclude(
                    pk=selected_template.pk)
                campaign_templates.append(
                    parse_campaign_template_details(selected_template))

            paginator = Paginator(
                campaign_template_objs, total_rows_per_pages)

            try:
                campaign_template_objs = paginator.page(page)
            except PageNotAnInteger:
                campaign_template_objs = paginator.page(1)
            except EmptyPage:
                campaign_template_objs = paginator.page(paginator.num_pages)

            if page != None:
                start_point = total_rows_per_pages * (int(page) - 1) + 1
                end_point = min(total_rows_per_pages *
                                int(page), total_campaign_objs)
                if start_point > end_point:
                    start_point = max(
                        end_point - len(campaign_template_objs) + 1, 1)
            else:
                start_point = 1
                end_point = min(total_rows_per_pages, total_campaign_objs)

            start_point = min(start_point, end_point)

            pagination_range = campaign_template_objs.paginator.page_range

            has_next = campaign_template_objs.has_next()
            has_previous = campaign_template_objs.has_previous()
            next_page_number = -1
            previous_page_number = -1

            if has_next:
                next_page_number = campaign_template_objs.next_page_number()
            if has_previous:
                previous_page_number = campaign_template_objs.previous_page_number()

            pagination_metadata = {
                'total_count': total_campaign_objs,
                'start_point': start_point,
                'end_point': end_point,
                'page_range': [pagination_range.start, pagination_range.stop],
                'has_next': has_next,
                'has_previous': has_previous,
                'next_page_number': next_page_number,
                'previous_page_number': previous_page_number,
                'number': campaign_template_objs.number,
                'num_pages': campaign_template_objs.paginator.num_pages
            }

            for campaign_template_obj in campaign_template_objs:
                if channel_name == 'RCS':
                    campaign_templates.append(
                        parse_rcs_campaign_template_details(campaign_template_obj))
                else:
                    campaign_templates.append(parse_campaign_template_details(
                        campaign_template_obj))

            response["status"] = 200
            response["message"] = "success"
            response["campaign_templates"] = campaign_templates
            response["pagination_metadata"] = pagination_metadata
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCampaignTemplatesAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCampaignTemplates = GetCampaignTemplatesAPI.as_view()


class GetCampaignTemplateDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response["message"] = "Internal Server Error"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            bot_pk = data["bot_pk"]
            template_pk = data["template_pk"]
            campaign_channel = data["campaign_channel"]

            bot_obj = Bot.objects.get(pk=int(bot_pk))
            if request.user not in bot_obj.users.all():
                response['message'] = 'You are not authorised to perform this operation.'
            else:
                if campaign_channel == 'RCS':
                    campaign_template_obj = CampaignRCSTemplate.objects.get(
                        pk=int(template_pk), bot=bot_obj)
                    campaign_template_data = campaign_template_obj.template_metadata
                else:
                    campaign_template_obj = CampaignTemplate.objects.get(
                        pk=int(template_pk), bot=bot_obj)
                    campaign_template_data = parse_campaign_template_details(
                        campaign_template_obj)
                response["status"] = 200
                response["message"] = "success"
                response["template_data"] = campaign_template_data
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCampaignTemplateDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetCampaignTemplateDetails = GetCampaignTemplateDetailsAPI.as_view()


class DownloadCampaignTemplateAPI(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            template_pk = data['template_pk']
            bot_pk = data['bot_pk']

            bot_obj = Bot.objects.filter(pk=int(bot_pk)).first()

            if not bot_obj or request.user not in bot_obj.users.all():
                response['message'] = 'You are not authorised to perform this operation.'
            
            campaign_template_obj = CampaignTemplate.objects.filter(
                pk=int(template_pk), is_deleted=False, bot=bot_obj).first()
            response["status"] = 200
            if campaign_template_obj:
                response["download_file_path"] = json.loads(campaign_template_obj.template_metadata)['template_file_path']
                
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DownloadCampaignTemplateAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["message"] = str(e)

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DownloadCampaignTemplate = DownloadCampaignTemplateAPI.as_view()


class AddTemplateToCampaignAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['message'] = 'Failed to add template.'

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            template_pk = data['selected_template_pk']
            campaign_id = data['campaign_id']
            bot_pk = data['bot_pk']
            campaign_channel = data['campaign_channel']

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response['message'] = 'You are not authorised to perform this operation.'
            else:
                if campaign_channel == 'RCS':
                    campaign_template_obj = CampaignRCSTemplate.objects.filter(
                        pk=int(template_pk), is_deleted=False, bot=bot_obj).first()
                else:
                    campaign_template_obj = CampaignTemplate.objects.filter(
                        pk=int(template_pk), is_deleted=False, bot=bot_obj).first()

                if campaign_template_obj:
                    campaign_obj = Campaign.objects.get(
                        pk=int(campaign_id), bot=bot_obj)

                    if campaign_obj.status == CAMPAIGN_IN_PROGRESS:
                        response['status'] = 401
                        response['campaign_id'] = campaign_id
                        response['message'] = 'Not able to assign batch. Campaign is in progress'

                    else:
                        if campaign_channel == 'RCS':
                            campaign_obj.campaign_template_rcs = campaign_template_obj
                        else:
                            campaign_obj.campaign_template = campaign_template_obj
                        campaign_obj.last_saved_state = CAMPAIGN_TEMPLATE_STATE
                        campaign_obj.save()

                        if campaign_channel != 'RCS':
                            body_variables = data.get('variables', [])
                            dynamic_cta_url_variable = data.get('dynamic_cta_url_variable', [])
                            header_variable = data.get('header_variable', [])

                            try:
                                template_var_obj = CampaignTemplateVariable.objects.get(
                                    campaign=campaign_obj, template=campaign_template_obj, batch=campaign_obj.batch)
                            except Exception:
                                template_var_obj = CampaignTemplateVariable.objects.create(
                                    campaign=campaign_obj, template=campaign_template_obj, batch=campaign_obj.batch)

                            template_var_obj.variables = json.dumps(body_variables)
                            template_var_obj.total_variables = len(body_variables)
                            template_var_obj.dynamic_cta_url_variable = json.dumps(dynamic_cta_url_variable)
                            template_var_obj.header_variable = json.dumps(header_variable)
                            template_var_obj.save(update_fields=["variables", "total_variables", "dynamic_cta_url_variable", "header_variable"])

                        response['status'] = 200
                        response['campaign_id'] = campaign_id
                        response['message'] = 'success'
                else:
                    response["status"] = 402
                    response["message"] = "Template does not exist"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddTemplateToCampaignAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddTemplateToCampaign = AddTemplateToCampaignAPI.as_view()


class DownloadSampleCampaignTemplateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            export_path = ("/files/templates/campaign" +
                           "/Sample_Template.xlsx")
            export_path_exist = path.exists(export_path[1:])

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DownloadSampleCampaignTemplateAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
            response["message"] = str(e)

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DownloadSampleCampaignTemplate = DownloadSampleCampaignTemplateAPI.as_view()


class UploadNewTemplateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            bot_pk = data["bot_pk"]

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            filename = strip_html_tags(data["filename"])
            base64_data = strip_html_tags(data["base64_file"])

            original_file_name = filename
            filename = generate_random_key(
                10) + "_" + filename.replace(" ", "")

            file_extention = filename.split(".")[-1]
            file_extention = file_extention.lower()

            allowed_files_list = ["xls", "xlsx", "xlsm",
                                  "xlt", "xltm", "xlb", "a", "bin"]
            if file_extention in allowed_files_list:
                media_type = "excel"
            else:
                media_type = None

            if media_type == None or check_malicious_file_from_filename(original_file_name, allowed_files_list) or check_malicious_file_from_content(base64_data, allowed_files_list):
                response["status"] = 400
                response["message"] = "The file could not be uploaded. Only files with the following extensions are allowed: XLS and XLSX."
            else:
                if not os.path.exists('secured_files/CampaignApp/campaign_template'):
                    os.makedirs(
                        'secured_files/CampaignApp/campaign_template')

                file_path = "secured_files/CampaignApp/campaign_template/" + filename

                fh = open(file_path, "wb")
                fh.write(base64.b64decode(base64_data))
                fh.close()

                status_code, row_errors, sample_data, template_exist_rows = get_sample_data_from_template_file(
                    file_path, bot_obj)

                if len(row_errors) != 0:
                    os.remove(file_path)
                    response['status'] = status_code
                    response['row_errors'] = row_errors
                else:

                    file_access_management_obj = CampaignFileAccessManagement.objects.create(
                        file_path=file_path, is_public=False, original_file_name=original_file_name)

                    response["status"] = 200
                    response["message"] = "success"

                    response["file_path"] = str(file_access_management_obj.key)
                    response["original_file_name"] = original_file_name
                    response['sample_data'] = sample_data
                    response['template_exist_rows'] = template_exist_rows
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadNewTemplateAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadNewTemplate = UploadNewTemplateAPI.as_view()


class DeleteCampaignTemplateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['message'] = 'Failed to delete template.'

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            template_pk = data['template_pk']
            bot_pk = data['bot_pk']
            campaign_channel = data['campaign_channel']

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response['message'] = 'You are not authorised to delete this batch.'
            else:
                if campaign_channel == 'RCS':
                    campaign_template_obj = CampaignRCSTemplate.objects.filter(
                        pk=int(template_pk), bot=bot_obj, is_deleted=False).first()
                else:
                    campaign_template_obj = CampaignTemplate.objects.filter(
                        pk=int(template_pk), bot=bot_obj, is_deleted=False).first()

                if campaign_template_obj:
                    is_active_campaign_exists, campaign_name = get_active_campaign_usign_template(
                        campaign_template_obj, campaign_channel, Campaign)

                    if is_active_campaign_exists:
                        response['message'] = "A campaign with name '" + campaign_name + \
                            "' is in progress on this template so you cannot delete it."
                    else:
                        campaign_template_obj.is_deleted = True
                        campaign_template_obj.save()

                        # TODO Set the status to be in draft
                        if campaign_channel == 'RCS':
                            campaigns = Campaign.objects.filter(
                                campaign_template_rcs=campaign_template_obj)
                        else:
                            campaigns = Campaign.objects.filter(
                                campaign_template=campaign_template_obj)
                        for campaign in campaigns:
                            campaign.campaign_template = None
                            campaign.save()

                        response['status'] = 200
                        response['message'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteCampaignTemplateAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteCampaignTemplate = DeleteCampaignTemplateAPI.as_view()


class DeleteUploadedTemplateFileAPI(APIView):

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
                key = file_path

                is_deleted = delete_file_by_key(
                    key, CampaignFileAccessManagement)

                if not is_deleted:
                    response['message'] = 'File does not exist.'
                else:
                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteUploadedTemplateFileAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteUploadedTemplateFile = DeleteUploadedTemplateFileAPI.as_view()


class SaveCampaignTemplateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            file_key = data['file_path']
            bot_pk = data["bot_pk"]

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response["message"] = "You are not authorised to upload campaign template for this bot."
            else:
                file_access_object = CampaignFileAccessManagement.objects.filter(
                    key=file_key).first()
                file_path = file_access_object.file_path
                file_name = file_access_object.original_file_name

                error_data = create_campaign_templates_from_file(
                    file_path, file_name, file_key, bot_obj, CampaignTemplate, CampaignTemplateLanguage, CampaignTemplateCategory, CampaignTemplateStatus, CampaignTemplateType)

                response["status"] = 200
                response["error_data"] = error_data
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCampaignTemplateAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCampaignTemplate = SaveCampaignTemplateAPI.as_view()


class SaveCampaignTemplateRCSAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            bot_pk = data["bot_pk"]
            template_name = data["template_name"].strip()
            message_type = data["message_type"]
            update_template = data["update_template"]
            validation_obj = EasyChatInputValidation()

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = "You are not authorised to upload campaign template for this bot."
            
            template_name = validation_obj.remo_complete_html_and_special_tags(template_name)
            
            if template_name == "":
                response["status"] = 300
                response["message"] = "Template name cannot be empty!"

            template_obj = CampaignRCSTemplate.objects.filter(
                bot=bot_obj, template_name=template_name, is_deleted=False)

            if template_obj.exists() and update_template == False:
                response["status"] = 300
                response["message"] = "Template with same name already exists!"

            if str(message_type).strip() == "":
                response["status"] = 300
                response["message"] = "Please select a valid template type!"

            if response["status"] == 300 or response["status"] == 401:
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            if message_type == 1:
                text_message = str(data["text_message"]).strip()
                if text_message == "":
                    response["status"] = 300
                    response["message"] = "Message text cannot be empty!"

            elif message_type == 2:
                media_url = data["media_url"]
                if not validation_obj.is_valid_url(media_url):
                    response["status"] = 300
                    response["message"] = "Please enter a valid media URL!"

            elif message_type == 3:
                error_message = validate_rich_and_carousel_cards(
                    data, validation_obj)
                if error_message is not None:
                    response["status"] = 300
                    response["message"] = error_message

            elif message_type == 4:
                carousel_cards = data["carousel_cards"]
                if len(carousel_cards) < 2:
                    response["status"] = 300
                    response["message"] = "Minimum 2 cards are required in Carousel else use the Rich Card for adding a single card."
                elif len(carousel_cards) > 10:
                    response["status"] = 300
                    response["message"] = "Maximum 10 Carousel Cards are supported!"
                else:
                    for carousel_card in carousel_cards:
                        error_message = validate_rich_and_carousel_cards(
                            carousel_card, validation_obj)
                        if error_message is not None:
                            response["status"] = 300
                            response["message"] = error_message
                            break

            suggested_reply = data["suggested_reply"]
            if response["status"] != 300 and len(suggested_reply) > 0:
                error_message = validate_suggested_reply(
                    suggested_reply, validation_obj)
                if error_message is not None:
                    response["status"] = 300
                    response["message"] = error_message

            if response["status"] == 300:
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            is_campaign_saved = save_rcs_campaign_template(bot_obj, data, template_name)
            response["status"] = 200
            if not is_campaign_saved:
                response["status"] = 300
                response["message"] = "Error in saving template!"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCampaignTemplateRCSAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCampaignTemplateRCS = SaveCampaignTemplateRCSAPI.as_view()
