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

import json
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


class AddCampaignScheduleAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        response['message'] = 'Failed to add schedule.'

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            campaign_id = data['campaign_id']
            bot_pk = data['bot_pk']

            choice_selected = data["choice_selected"]
            start_date = data["start_date"]
            end_date = data["end_date"]
            time_slots = data["time_slots"]
            days = data["days"]
            days = json.dumps(days)
            date_format = "%Y-%m-%d"

            if start_date != "":
                start_date = datetime.strptime(
                    start_date, date_format).date()
            if end_date != "":
                end_date = datetime.strptime(
                    end_date, date_format).date()

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response['message'] = 'You are not authorised to perform this operation.'
            else:               
                campaign_obj = Campaign.objects.filter(
                    pk=int(campaign_id), bot=bot_obj).first()
                bot_wsp_obj = CampaignBotWSPConfig.objects.filter(bot=bot_obj).first()
                campaign_wsp_config_meta = {"code": bot_wsp_obj.code, "namespace": bot_wsp_obj.namespace,
                                                "enable_queuing_system": bot_wsp_obj.enable_queuing_system, "bot_wsp_id": bot_wsp_obj.pk}
                if campaign_wsp_config_meta["enable_queuing_system"]:
                    sqs_response = validate_aws_sqs_credentials(
                        bot_wsp_obj, campaign_wsp_config_meta)

                    if not sqs_response:
                        response['message'] = 'Unable to connect to the queueing system due to invalid credentials. Please connect with our support team to get this resolved.'
                        response['status'] = 404
                        return make_response_packet(response, custom_encrypt_obj)

                metadata = []
                batch_obj_pk = campaign_obj.batch.pk
                metadata = get_schedule_metadata(time_slots, batch_obj_pk)
                final_end_date = None
                if choice_selected == "custom" and end_date != "":
                    final_end_date = end_date
                    delta = end_date - start_date
                    if delta.days > 365:
                        response['status'] = 300
                        response['message'] = "Custom end date can't be greater than 1 year."
                        return make_response_packet(response, custom_encrypt_obj)

                campaign_schedule_obj = CampaignSchedule.objects.create(
                    choices=choice_selected,
                    days=days,
                    metadata=metadata,
                    start_date=start_date,
                    end_date=final_end_date,
                    campaign=campaign_obj,
                    bot=bot_obj
                )
                metadata = json.loads(metadata)
                checking_schedule_obj = CampaignScheduleObject.objects.filter(
                    campaign=campaign_schedule_obj.campaign,
                    date=start_date,
                    time=datetime.strptime(metadata[0]['time'], '%I:%M %p').time(),
                ).first()
                if checking_schedule_obj:
                    response['status'] = 400
                else:
                    days = json.loads(days)
                    create_objects_related_to_schedule(start_date, final_end_date, choice_selected, metadata, campaign_schedule_obj, CampaignScheduleObject, days, batch_pk=batch_obj_pk)
                    response['status'] = 200
                    response['campaign_id'] = campaign_id
                    response['message'] = 'success'
                
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddCampaignScheduleAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return make_response_packet(response, custom_encrypt_obj)


AddCampaignSchedule = AddCampaignScheduleAPI.as_view()


class EditScheduleCampaignAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        response['message'] = 'Failed to edit schedule.'

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            campaign_id = data['campaign_id']
            bot_pk = data['bot_pk']

            start_date = data["start_date"]
            end_date = data["end_date"]

            date_format = "%Y-%m-%d"
            mode_occurence = data["mode_occurence"]
            original_metadata = data["original_metadata"]
            current_slot_pk = data["current_slot_pk"]
            update_time_slot_value = data["update_time_slot_value"]
            edited_uid = data['edited_uid']
            new_batch_pk = data.get('new_batch_pk')

            if start_date != "":
                start_date = datetime.strptime(
                    start_date, date_format).date()
            if end_date != "":
                end_date = datetime.strptime(
                    end_date, date_format).date()

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response['message'] = 'You are not authorised to perform this operation.'
            else:     
                campaign_obj = Campaign.objects.get(
                    pk=int(campaign_id), bot=bot_obj)
                new_campaign_batch_obj = verify_selected_batch_for_scheduling(campaign_obj, new_batch_pk, response)
                if response["status"] != 200:
                    return make_response_packet(response, custom_encrypt_obj)
                batch_pk = new_campaign_batch_obj.pk

                edited_on = timezone.now()
                if mode_occurence == "single_occurence":
                    edited_schedule = CampaignScheduleObject.objects.filter(pk=int(current_slot_pk)).first()
                    if edited_schedule:
                        edited_schedule.date = start_date
                        edited_schedule.time = datetime.strptime(update_time_slot_value, '%I:%M %p').time()
                        edited_schedule.campaign_batch_id = batch_pk
                        edited_schedule.edited_on = edited_on
                        edited_schedule.save(update_fields=['date', 'time', 'campaign_batch', 'edited_on'])
                elif mode_occurence == "current_and_remaing":
                    list_uid_from_original_metadata = [meta_obj["uid"] for meta_obj in original_metadata]
                    index = list_uid_from_original_metadata.index(edited_uid)
                    original_metadata[index]["time"] = update_time_slot_value
                    original_metadata[index]['batch_pk'] = batch_pk
                    original_metadata[index]['edited_on'] = str((edited_on + timedelta(hours=5, minutes=30)).strftime("%d %b %Y, %I:%M %p"))
                    edited_schedule = CampaignScheduleObject.objects.filter(pk=int(current_slot_pk)).first()
                    if edited_schedule:
                        uid_to_be_updated = edited_schedule.uid
                        edited_schedule_date = edited_schedule.date
                        schedule_objects_as_per_uid = CampaignScheduleObject.objects.filter(uid=uid_to_be_updated, date__gte=edited_schedule_date)
                        for obj in schedule_objects_as_per_uid:
                            obj.time = datetime.strptime(update_time_slot_value, '%I:%M %p').time()
                            obj.campaign_batch_id = batch_pk
                            obj.edited_on = edited_on
                            obj.save(update_fields=['time', 'campaign_batch', 'edited_on'])
                        
                        edited_schedule.campaign_schedule.metadata = json.dumps(original_metadata)
                        edited_schedule.campaign_schedule.save(update_fields=['metadata'])

                response['status'] = 200
                response['campaign_id'] = campaign_id
                response['message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EditScheduleCampaignAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return make_response_packet(response, custom_encrypt_obj)


EditScheduleCampaign = EditScheduleCampaignAPI.as_view()


class DeleteScheduleCampaignAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        response['message'] = 'Failed to delete schedule.'

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            campaign_id = data['campaign_id']
            bot_pk = data['bot_pk']
            mode_occurence = data["mode_occurence"]
            schedule_pk = data["schedule_pk"]
            current_slot_pk = data["current_slot_pk"]
            uid = data["uid"]
            selected_items = data["selected_items"]
            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response['message'] = 'You are not authorised to perform this operation.'
            else:               
                campaign_obj = Campaign.objects.get(
                    pk=int(campaign_id), bot=bot_obj)

                if mode_occurence == "single_occurence":
                    campaign_schedule = CampaignSchedule.objects.filter(pk=int(schedule_pk), campaign=campaign_obj, bot=bot_obj).first()
                    if campaign_schedule:
                        schedule_to_be_deleted = CampaignScheduleObject.objects.filter(pk=int(current_slot_pk), campaign_schedule=campaign_schedule)
                        if schedule_to_be_deleted.count() > 0:
                            schedule_to_be_deleted = schedule_to_be_deleted.first()
                            schedule_to_be_deleted.delete()

                elif mode_occurence == "selected_items":
                    for item in selected_items:
                        schedule_objs = CampaignScheduleObject.objects.filter(pk=int(item)).first()
                        if schedule_objs:
                            if schedule_objs.campaign_schedule.bot == bot_obj:
                                schedule_objs.delete()
                            else:
                                response['message'] = 'You are not authorised to perform this operation.'
                
                elif mode_occurence == "current_and_remaing":
                    schedule_obj = CampaignScheduleObject.objects.filter(pk=int(current_slot_pk)).first()
                    if schedule_obj:
                        campaign_schedule = schedule_obj.campaign_schedule
                        campaign_schedule.end_date = schedule_obj.date
                        campaign_schedule.choices = SCHEDULE_CHOICES[0][0]
                        campaign_schedule.save(update_fields=['end_date', 'choices'])
                        uid_to_be_updated = schedule_obj.uid
                        edited_schedule_date = schedule_obj.date
                        schedule_objects_as_per_uid = CampaignScheduleObject.objects.filter(uid=uid_to_be_updated, date__gte=edited_schedule_date)
                        for campaign_schedule_obj in schedule_objects_as_per_uid.iterator():
                            campaign_schedule_obj.delete()

                elif mode_occurence == 'whole_campaign':
                    campaign_schedules = CampaignSchedule.objects.filter(campaign=campaign_obj)
                    for campaign_schedule in campaign_schedules.iterator():
                        campaign_schedules.delete()

                elif mode_occurence == "multiple_occurence":
                    campaign_schedule = CampaignSchedule.objects.filter(pk=int(schedule_pk), campaign=campaign_obj, bot=bot_obj)
                    if campaign_schedule.count() > 0:
                        campaign_schedule = campaign_schedule.first()
                        schedule_to_be_deleted = CampaignScheduleObject.objects.filter(campaign_schedule=campaign_schedule, uid=uuid.UUID(uid))
                        if schedule_to_be_deleted.count() > 0:
                            schedule_to_be_deleted.delete()
                            metadata = json.loads(campaign_schedule.metadata)
                            for obj in metadata:
                                if obj["uid"] == uid:
                                    metadata.remove(obj)
                                    break

                            campaign_schedule.metadata = json.dumps(metadata)
                            campaign_schedule.save()

                elif mode_occurence == "all_occurence":
                    campaign_schedule = CampaignSchedule.objects.filter(pk=int(schedule_pk), campaign=campaign_obj, bot=bot_obj)
                    if campaign_schedule.first():
                        campaign_schedule = campaign_schedule.delete()

                response['status'] = 200
                response['campaign_id'] = campaign_id
                response['message'] = 'success'
                
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteScheduleCampaignAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteScheduleCampaign = DeleteScheduleCampaignAPI.as_view()


class GetUpcomingScheduleAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        response['message'] = 'Failed to add schedule.'

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            campaign_id = data['campaign_id']
            bot_pk = data['bot_pk']
            start_date = data["start_date"]
            end_date = data["end_date"]
            page = data["page"]
            date_format = "%Y-%m-%d"
            if start_date != "" and end_date != "":
                start_date = datetime.strptime(
                    start_date, date_format).date()

                end_date = datetime.strptime(
                    end_date, date_format).date()

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response['message'] = 'You are not authorised to perform this operation.'
            else:               
                campaign_obj = Campaign.objects.get(
                    pk=int(campaign_id), bot=bot_obj)

                campaign_schedule_objs = CampaignSchedule.objects.filter(
                    campaign=campaign_obj,
                    bot=bot_obj
                )
                campaign_schedule_objs = list(campaign_schedule_objs)
                campaign_schedule_query = None
                if campaign_schedule_objs:
                    campaign_schedule_query = reduce(operator.or_, (Q(campaign_schedule=campaign_schedule_obj)
                                                                    for campaign_schedule_obj in campaign_schedule_objs))
                if start_date == "" or end_date == "":
                    if campaign_schedule_query:
                        campaign_schedules = CampaignScheduleObject.objects.filter(is_sent=False)
                        campaign_schedules = campaign_schedules.filter(campaign_schedule_query)
                    
                        campaign_schedules = campaign_schedules.order_by('date', 'time')

                        paginator = Paginator(
                            campaign_schedules, 25)
                        page_diff = paginator.num_pages - page

                        if page_diff < 5:
                            for single_schedule in campaign_schedule_objs:
                                create_remaining_schedule_objects(single_schedule, None, CampaignScheduleObject)
                            
                            campaign_schedules = CampaignScheduleObject.objects.filter(campaign_schedule__in=campaign_schedule_objs, is_sent=False)

                            campaign_schedules = campaign_schedules.order_by('date', 'time')
                    else:
                        campaign_schedules = CampaignScheduleObject.objects.none()
            
                else:
                    for single_schedule in campaign_schedule_objs:
                        create_remaining_schedule_objects(single_schedule, end_date, CampaignScheduleObject)

                    if campaign_schedule_query:
                        campaign_schedules = CampaignScheduleObject.objects.filter(
                            date__gte=start_date,
                            date__lte=end_date,
                            is_sent=False
                        )
                        campaign_schedules = campaign_schedules.filter(campaign_schedule_query)
                        campaign_schedules = campaign_schedules.order_by('date', 'time')
                    else:
                        campaign_schedules = CampaignScheduleObject.objects.none()

                paginator = Paginator(campaign_schedules, 25)
                if page <= paginator.num_pages:
                    try:
                        campaign_schedules = paginator.page(page)
                    except PageNotAnInteger:
                        campaign_schedules = paginator.page(1)
                    except EmptyPage:
                        campaign_schedules = paginator.page(paginator.num_pages)

                    response["page_exist"] = True
                else:
                    response["page_exist"] = False
                    page = page - 1

                campaign_schedules = get_schedules_list_obj(campaign_schedules)
                response['status'] = 200
                response['campaign_id'] = campaign_id
                response['message'] = 'success'
                response['update_schedule_list'] = campaign_schedules
                response["total_entries"] = len(campaign_schedules)
                response["total_pages"] = paginator.num_pages
                response["current_page"] = page

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetUpcomingScheduleAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetUpcomingSchedule = GetUpcomingScheduleAPI.as_view()


class GetSingleScheduleDataAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        response['message'] = 'Failed to add schedule.'

        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            bot_pk = data['bot_pk']
            schedule_pk = data['schedule_pk']
            current_slot_pk = data['current_slot_pk']

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response['message'] = 'You are not authorised to perform this operation.'
            else:
                campaign_schedule = CampaignSchedule.objects.filter(pk=int(schedule_pk), bot=bot_obj).first()
                if campaign_schedule:
                    current_schedule_object = CampaignScheduleObject.objects.filter(pk=int(current_slot_pk), campaign_schedule=campaign_schedule).first()
                    if current_schedule_object:
                        end_date = campaign_schedule.end_date
                        if end_date == None:
                            end_date = ""
                        else:
                            end_date.strftime("%d-%m-%Y")
                        campaign_edit_obj = {
                            "original_start_date": str(campaign_schedule.start_date.strftime("%d-%m-%Y")),
                            "original_end_date": str(end_date),
                            "original_updated_upto": str(campaign_schedule.updated_upto.strftime("%d-%m-%Y")),
                            "edited_start_date": str(current_schedule_object.date.strftime("%d-%m-%Y")),
                            "edited_trigger_time": str(current_schedule_object.time.strftime("%I:%M %p")),
                            "edited_uid": str(current_schedule_object.uid),
                            "choice_selected": campaign_schedule.choices,
                            "batch_pk": current_schedule_object.campaign_batch_id,
                        }
                        campaign_days = json.loads(campaign_schedule.days)
                        campaign_meta_data = json.loads(campaign_schedule.metadata)
                    else:
                        response['message'] = 'You are not authorised to perform this operation.'
                        response = json.dumps(response)
                        encrypted_response = custom_encrypt_obj.encrypt(response)
                        response = {"Response": encrypted_response}
                        return Response(data=response)

                else:
                    response['message'] = 'You are not authorised to perform this operation.'
                    response = json.dumps(response)
                    encrypted_response = custom_encrypt_obj.encrypt(response)
                    response = {"Response": encrypted_response}
                    return Response(data=response)
                
                response['status'] = 200
                response['message'] = 'success'
                response['campaign_schedule'] = campaign_edit_obj
                response["campaign_meta_data"] = campaign_meta_data
                response["campaign_days"] = campaign_days

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetUpcomingScheduleAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetSingleScheduleData = GetSingleScheduleDataAPI.as_view()
