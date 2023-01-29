import os
import sys
import json
import uuid
import pytz
import random
import logging
from datetime import datetime

from django.http import FileResponse
from django.utils.safestring import mark_safe
from django.shortcuts import render, HttpResponse, HttpResponseRedirect

# Django REST framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.contrib.auth import get_user_model

from LiveChatApp.utils import *
from LiveChatApp.models import *
from LiveChatApp.constants import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils_validation import LiveChatInputValidation
from LiveChatApp.utils_calendar import *

User = get_user_model()

# Logger


logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def LiveChatCalenderPage(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)
            current_date = str(datetime.now().day)
            current_month = str(datetime.now().month)
            current_year = str(datetime.now().year)

            selected_month = request.GET.get('selected_month')
            selected_year = request.GET.get('selected_year')

            selected_month = current_month if selected_month == None else selected_month
            selected_year = current_year if selected_year == None else selected_year

            if int(selected_month) <= 0 or int(selected_month) > 12 or int(selected_year) < 2020 or int(selected_year) > 2031:
                return HttpResponse("Invalid month or year")

            prev_month, prev_year = get_prev_month(selected_month, selected_year)
            next_month, next_year = get_next_month(selected_month, selected_year)

            if user_obj.status == "1":
                calendar_objs = LiveChatCalender.objects.filter(created_by=user_obj, event_date__year=int(
                    selected_year), event_date__month=int(selected_month)).order_by('event_date')
                latest_modified_calendar_obj = LiveChatCalender.objects.filter(created_by=user_obj, event_date__year=int(
                    selected_year), event_date__month=int(selected_month)).order_by('-modified_date').first()

                prev_month_calendar_objs_count = LiveChatCalender.objects.filter(created_by=user_obj, event_date__year=int(
                    prev_year), event_date__month=int(prev_month)).count()  
                next_month_calendar_objs_count = LiveChatCalender.objects.filter(created_by=user_obj, event_date__year=int(
                    next_year), event_date__month=int(next_month)).count()

                today_calendar_obj = LiveChatCalender.objects.get(created_by=user_obj, event_date__year=int(
                    current_year), event_date__month=int(current_month), event_date__day=int(current_date))                
            else:
                parent_user = get_admin_from_active_agent(
                    user_obj, LiveChatUser)
                calendar_objs = LiveChatCalender.objects.filter(created_by=parent_user, event_date__year=int(
                    selected_year), event_date__month=int(selected_month)).order_by('event_date')
                latest_modified_calendar_obj = LiveChatCalender.objects.filter(created_by=parent_user, event_date__year=int(
                    selected_year), event_date__month=int(selected_month)).order_by('-modified_date').first()

                prev_month_calendar_objs_count = LiveChatCalender.objects.filter(created_by=parent_user, event_date__year=int(
                    prev_year), event_date__month=int(prev_month)).count()
                next_month_calendar_objs_count = LiveChatCalender.objects.filter(created_by=parent_user, event_date__year=int(
                    next_year), event_date__month=int(next_month)).count()  

                today_calendar_obj = LiveChatCalender.objects.get(created_by=parent_user, event_date__year=int(
                    current_year), event_date__month=int(current_month), event_date__day=int(current_date))          

            timezone = pytz.timezone(settings.TIME_ZONE)

            calender_list = []
            if calendar_objs:
                calender_list = convert_to_calender(calendar_objs)

            total_calender_objs = calendar_objs.count()

            selected_month_name = get_month_list()[int(selected_month) - 1]['value']

            user_obj = LiveChatUser.objects.get(user=User.objects.get(
                username=str(request.user.username)), is_deleted=False)
            if user_obj.status == "1":
                return render(request, 'LiveChatApp/calender.html', {

                    "user_obj": user_obj,
                    "selected_month": selected_month,
                    "selected_year": selected_year,
                    "calender_month": get_month_list(),
                    "calender_year": get_year_list(),
                    "calendar_objs": calendar_objs,
                    "total_calender_objs": total_calender_objs,
                    "admin_config": admin_config,
                    "char_limit_medium_text": LIVECHAT_CHARACTER_LIMIT_MEDIUM_TEXT,
                    "char_limit_large_text": LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT,
                    "calender_list": calender_list,
                    "selected_month_name": selected_month_name,
                    "latest_modified_calendar_obj": latest_modified_calendar_obj,
                    "time_zone": timezone,
                })

            return render(request, 'LiveChatApp/agent_calender.html', {

                "user_obj": user_obj,
                "selected_month": selected_month,
                "selected_year": selected_year,
                "calender_month": get_month_list(),
                "calender_year": get_year_list(),
                "calendar_objs": calendar_objs,
                "total_calender_objs": total_calender_objs,
                "admin_config": admin_config,
                "calender_list": calender_list,
                "selected_month_name": selected_month_name,
                "time_zone": timezone,
                "prev_month_calendar_objs_count": prev_month_calendar_objs_count,
                "next_month_calendar_objs_count": next_month_calendar_objs_count,
                "today_calendar_obj": today_calendar_obj,
            })
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("LiveChatCalender ! %s %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
        return HttpResponse("Invalid request")


class AddHolidayCalenderAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_obj = LiveChatUser.objects.filter(status="1").get(
                user=User.objects.get(username=str(request.user.username)))
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            holiday_dates = data["holiday_date_array"]
            
            description = data["description"]
            auto_response = data["auto_response"]

            validation_obj = LiveChatInputValidation()

            description = validation_obj.remo_html_from_string(description)
            auto_response = validation_obj.remo_html_from_string(auto_response)

            if len(holiday_dates) == 0:
                response["message"] = "Holiday date(s) are not selected"
                response["status_code"] = "400"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
 
            if len(description) > LIVECHAT_CHARACTER_LIMIT_MEDIUM_TEXT:
                response['message'] = f'{EXCEEDING_CHARACTER_LIMIT} {LIVECHAT_CHARACTER_LIMIT_MEDIUM_TEXT} characters in description'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if len(auto_response) > LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT:
                response['message'] = f'{EXCEEDING_CHARACTER_LIMIT} {LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT} characters in auto response'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            for holiday_date in holiday_dates:
                holiday_date = holiday_date.split("-")
                holiday_date = datetime(int(holiday_date[0]), int(
                    holiday_date[1]), int(holiday_date[2]))
                if LiveChatCalender.objects.filter(event_date=holiday_date, created_by=user_obj).count():
                    livechat_calendar_obj = LiveChatCalender.objects.get(event_date=holiday_date, created_by=user_obj)
                    if livechat_calendar_obj.event_type != "2":
                        livechat_calendar_obj.event_type = "2"
                        livechat_calendar_obj.event_date = holiday_date

                    livechat_calendar_obj.description = description
                    livechat_calendar_obj.auto_response = auto_response
                    livechat_calendar_obj.modified_by = user_obj
                    livechat_calendar_obj.modified_date = datetime.now()
                    livechat_calendar_obj.save()    
                else:
                    LiveChatCalender.objects.create(
                        event_type="2", event_date=holiday_date, description=description, auto_response=auto_response, created_by=user_obj)
                response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside AddHolidayCalenderAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            response["status_code"] = "500"
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AddHolidayCalender = AddHolidayCalenderAPI.as_view()


class DeleteCalenderEventAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_obj = LiveChatUser.objects.filter(status="1").get(
                user=User.objects.get(username=str(request.user.username)))
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            pk = data["pk"]
            livechat_calender_obj = LiveChatCalender.objects.get(pk=int(pk))
            if user_obj.status == "1":
                livechat_calender_obj.delete()
                response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside DeleteCalenderEventAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DeleteCalenderEvent = DeleteCalenderEventAPI.as_view()


class EditCalenderEventAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_obj = LiveChatUser.objects.filter(status="1").get(
                user=User.objects.get(username=str(request.user.username)))
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            pk = data["pk"]
            selected_event = data["selected_event"]
            start_time = data["start_time"]
            end_time = data["end_time"]
            description = data["description"]
            auto_response = data["auto_response"]
            livechat_calender_obj = LiveChatCalender.objects.get(pk=int(pk))
            check_and_update_based_on_event_type(
                user_obj, livechat_calender_obj, selected_event, start_time, end_time, description, auto_response)
            response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside EditCalenderEventAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EditCalenderEvent = EditCalenderEventAPI.as_view()


class CreateWorkingHoursAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = INTERNAL_SERVER_ERROR
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user_obj = LiveChatUser.objects.filter(status="1").get(
                user=User.objects.get(username=str(request.user.username)))
            user_obj = check_if_livechat_only_admin(user_obj, LiveChatUser)
            month = data["month"]
            year = data["year"]
            start_time = data["start_time"]
            end_time = data["end_time"]
            days_list = data["days_list"]
            mode = data["mode"]
            if mode == "1":
                month = str(month)
                no_days = get_number_of_day(year, month)
                try:
                    LiveChatCalender.objects.filter(
                        event_date__month=int(month), event_date__year=int(year), created_by=user_obj).delete()
                    for day in range(1, no_days + 1):
                        today_date = datetime(
                            int(year), int(month), int(day))
                        week_day = today_date.strftime("%A")
                        if str(week_day) in days_list:
                            LiveChatCalender.objects.create(
                                event_type="2", event_date=today_date, created_by=user_obj, auto_response="Hi! Thanks for contacting us. All our agents are on a holiday today. Please try again on the next working day.", description="Default Holiday")
                        else:
                            LiveChatCalender.objects.create(
                                event_type="1", event_date=today_date, created_by=user_obj, start_time=start_time, end_time=end_time)
                        response["status_code"] = "200"
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("CreateWorkingHoursAPI: %s at %s",
                                 e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            elif mode == "2":
                for month in range(1, 13):
                    month = str(month)
                    no_days = get_number_of_day(year, month)
                    try:
                        LiveChatCalender.objects.filter(
                            event_date__month=int(month), event_date__year=int(year), created_by=user_obj).delete()
                        for day in range(1, no_days + 1):
                            today_date = datetime(
                                int(year), int(month), int(day))
                            week_day = today_date.strftime("%A")
                            if str(week_day) in days_list:
                                LiveChatCalender.objects.create(
                                    event_type="2", event_date=today_date, created_by=user_obj, auto_response="Hi! Thanks for contacting us. All our agents are on a holiday today. Please try again on the next working day.", description="Default Holiday")
                            else:
                                LiveChatCalender.objects.create(
                                    event_type="1", event_date=today_date, created_by=user_obj, start_time=start_time, end_time=end_time)
                        response["status_code"] = "200"
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("CreateWorkingHoursAPI: %s at %s",
                                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            elif mode == "3":
                for current_month in range(3):
                    month = str(month)
                    no_days = get_number_of_day(year, month)
                    try:
                        LiveChatCalender.objects.filter(
                            event_date__month=int(month), event_date__year=int(year), created_by=user_obj).delete()
                        for day in range(1, no_days + 1):
                            today_date = datetime(
                                int(year), int(month), int(day))
                            week_day = today_date.strftime("%A")
                            if str(week_day) in days_list:
                                LiveChatCalender.objects.create(
                                    event_type="2", event_date=today_date, created_by=user_obj, auto_response="Hi! Thanks for contacting us. All our agents are on a holiday today. Please try again on the next working day.", description="Default Holiday")
                            else:
                                LiveChatCalender.objects.create(
                                    event_type="1", event_date=today_date, created_by=user_obj, start_time=start_time, end_time=end_time)
                            response["status_code"] = "200"
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("CreateWorkingHoursAPI: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'}) 
                    if int(month) > 0 and int(month) <= 12 and int(year) >= 2020 and int(year) <= 2031:                           
                        month, year = get_next_month(month, year)
                    else:
                        response["status_code"] = "400"
                        response["status_message"] = "Invalid month or year"  
                        return Response(data=response)                          
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside CreateWorkingHoursAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CreateWorkingHours = CreateWorkingHoursAPI.as_view()
