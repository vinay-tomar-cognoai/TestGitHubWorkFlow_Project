from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication

from django.shortcuts import render, HttpResponse, redirect

from EasyAssistApp.models import *
from EasyAssistApp.utils import *
from EasyAssistApp.utils_email_analytics import *
from EasyAssistApp.utils_calendar import *
from EasyAssistApp.views_table import *
from EasyAssistApp.views_sandbox_user import *

import sys
import pytz
import json
import datetime
import logging
from urllib.parse import urlparse
from urllib.parse import parse_qs


logger = logging.getLogger(__name__)


def SalesCalendarSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        cobrowse_agent = get_active_agent_obj(request, CobrowseAgent)
        access_token_obj = cobrowse_agent.get_access_token_obj()
        if not access_token_obj.enable_inbound and cobrowse_agent.role == "admin":
            return redirect("sales-settings-options")
        if not access_token_obj.enable_inbound and cobrowse_agent.role != "admin":
            return redirect("sales-settings-agent-home-page")
        current_month = str(datetime.datetime.now().month)
        current_year = str(datetime.datetime.now().year)
        calendar_type = request.GET.get('days')
        selected_month = request.GET.get('month')
        selected_year = request.GET.get('years')
        filter_dropdown_year_list = [str(i) for i in range(int(current_year) - 7, int(current_year) + 6)]
        work_time_year_list = [str(i) for i in range(int(current_year), int(current_year) + 6)] 
        if selected_month:
            parsed_url = urlparse(request.get_full_path())
            selected_month = parse_qs(parsed_url.query)['month']

            months_list = []
            for month in selected_month:
                months_list.append(month_to_num_dict[month])
            selected_month = months_list
        if calendar_type and calendar_type == "Holidays":
            calendar_type = "2"
        else:
            calendar_type = "1"
        
        if selected_year and not selected_month:
            selected_month = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        
        if not selected_year:
            selected_year = current_year

        if not selected_month:
            selected_month = [int(current_month)]

        if cobrowse_agent.role != "admin":

            cobrowse_admin = get_admin_from_active_agent(
                cobrowse_agent, CobrowseAgent)

            calendar_objs = CobrowseCalendar.objects.filter(created_by=cobrowse_admin, event_type=calendar_type, event_date__year=int(
                selected_year), event_date__month__in=selected_month).order_by('event_date')

            total_rows_per_pages = 31
            page = request.GET.get('page')
            
            page_object_count, calendar_objs, start_point, end_point = paginate(
                calendar_objs, total_rows_per_pages, page)

            return render(request, "EasyAssistApp/sales_agent_calendar_setting.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "COBROWSING_AGENT_SUPPORT": COBROWSING_AGENT_SUPPORT,
                "calendar_type": calendar_type,
                "selected_month": selected_month,
                "selected_year": selected_year,
                "calendar_objs": calendar_objs,
                "start_point": start_point,
                "end_point": end_point,
                "total_calendar_objs": page_object_count,
                "calendar_created_by": cobrowse_admin,
                "filter_dropdown_year_list": filter_dropdown_year_list,
            })

        else:
            agent_working_days = access_token_obj.get_cobrowse_working_days()

            calendar_objs = CobrowseCalendar.objects.filter(created_by=cobrowse_agent, event_type=calendar_type, event_date__year=int(
                selected_year), event_date__month__in=selected_month).order_by('event_date')

            total_rows_per_pages = 31
            page = request.GET.get('page')
            
            page_object_count, calendar_objs, start_point, end_point = paginate(
                calendar_objs, total_rows_per_pages, page)

            return render(request, "EasyAssistApp/sales_calendar_settings.html", {
                "cobrowse_agent": cobrowse_agent,
                "access_token_obj": access_token_obj,
                "agent_working_days": agent_working_days,
                "cobrowsing_days": COBROWSING_DAYS,
                "calendar_type": calendar_type,
                "selected_month": selected_month,
                "selected_year": selected_year,
                "calendar_objs": calendar_objs,
                "start_point": start_point,
                "end_point": end_point,
                "total_calendar_objs": page_object_count,
                "filter_dropdown_year_list": filter_dropdown_year_list,
                "work_time_year_list": work_time_year_list
            })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesCalendarSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


class AddHolidayCalendarAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = "Internal Server Error"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data['Request']
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cobrowse_agent = get_active_agent_obj(request, CobrowseAgent)
            if cobrowse_agent.role == "admin":
                holiday_date = data["holiday_date"]
                description = data["description"]
                auto_response = data["auto_response"]

                holiday_date = holiday_date.split("-")
                holiday_date = datetime.datetime(int(holiday_date[0]), int(
                    holiday_date[1]), int(holiday_date[2]))

                if holiday_date.strftime('%Y-%m-%d') < datetime.datetime.today().strftime('%Y-%m-%d'):
                    response["status_code"] = 300
                    response["status_message"] = "Unable to add holiday as the selected date is in the past"
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                
                if CobrowseCalendar.objects.filter(event_date=holiday_date, created_by=cobrowse_agent).count():
                    cobrowse_calendar_obj = CobrowseCalendar.objects.filter(event_date=holiday_date, created_by=cobrowse_agent).first()
                    if cobrowse_calendar_obj.event_type == "2":
                        response["status_code"] = "300"
                    else:
                        cobrowse_calendar_obj.event_type = "2"
                        cobrowse_calendar_obj.event_date = holiday_date
                        cobrowse_calendar_obj.description = description
                        cobrowse_calendar_obj.auto_response = auto_response
                        cobrowse_calendar_obj.modified_by = cobrowse_agent
                        cobrowse_calendar_obj.modified_date = datetime.datetime.now()
                        cobrowse_calendar_obj.save()
                        response["status_code"] = "200"
                else:
                    CobrowseCalendar.objects.create(
                        event_type="2", event_date=holiday_date, description=description, auto_response=auto_response, created_by=cobrowse_agent)
                    response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AddHolidayCalendar: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistApp'})

            response["status_code"] = "500"
            response["status_message"] = str(e)

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddHolidayCalendar = AddHolidayCalendarAPI.as_view()


class EditCalendarEventAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = "Internal Server Error"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data['Request']
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cobrowse_agent = get_active_agent_obj(request, CobrowseAgent)
            if cobrowse_agent.role == "admin":
                pk = data["pk"]
                selected_event = data["selected_event"]
                start_time = convert_time_to_24_hrs(data["start_time"])
                end_time = convert_time_to_24_hrs(data["end_time"])
                description = data["description"]
                auto_response = data["auto_response"]
                cobrowse_calender_obj = CobrowseCalendar.objects.filter(pk=int(pk)).first()

                calander_event_date = cobrowse_calender_obj.event_date.astimezone(
                    pytz.timezone(settings.TIME_ZONE)).strftime(DATE_TIME_FORMAT)

                today_date = datetime.datetime.today().strftime('%Y-%m-%d')

                if cobrowse_calender_obj.event_type != selected_event and calander_event_date < today_date:
                    response["status_code"] = 300
                    response["status_message"] = "Unable to update event as the event date is in the past"
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                check_and_update_based_on_event_type(
                    cobrowse_agent, cobrowse_calender_obj, selected_event, start_time, end_time, description, auto_response)
                response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside EditCalenderEventAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistApp'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


EditCalendarEvent = EditCalendarEventAPI.as_view()


class CreateWorkingHoursAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["message"] = "Internal Server Error"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data['Request']
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cobrowse_agent = get_active_agent_obj(request, CobrowseAgent)
            if cobrowse_agent.role == "admin":
                month = data["month"]
                year = data["year"]
                start_time = convert_time_to_24_hrs(data["start_time"])
                end_time = convert_time_to_24_hrs(data["end_time"])
                days_list = data["days_list"]
                mode = data["mode"]
                if mode == "1":
                    month = str(month)
                    no_days = get_number_of_day(year, month)
                    try:
                        for day in range(1, no_days + 1):
                            today_date = datetime.datetime(
                                int(year), int(month), int(day))
                            week_day = today_date.strftime("%A")
                            if str(week_day) in days_list:
                                cobrowse_calender_obj = CobrowseCalendar.objects.filter(event_date=today_date, created_by=cobrowse_agent)
                                if cobrowse_calender_obj.exists():
                                    cobrowse_calender_obj = cobrowse_calender_obj[0]
                                    if cobrowse_calender_obj.event_type == "1":
                                        cobrowse_calender_obj.delete()
                            else:
                                cobrowse_calender_obj = CobrowseCalendar.objects.filter(event_date=today_date, created_by=cobrowse_agent)
                                if cobrowse_calender_obj.exists():
                                    cobrowse_calender_obj = cobrowse_calender_obj[0]
                                    if cobrowse_calender_obj.event_type == "1":
                                        cobrowse_calender_obj.start_time = start_time
                                        cobrowse_calender_obj.end_time = end_time
                                        cobrowse_calender_obj.save()
                                else:
                                    CobrowseCalendar.objects.create(
                                        event_type="1", event_date=today_date, created_by=cobrowse_agent, start_time=start_time, end_time=end_time)
                            response["status_code"] = "200"
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("CreateWorkingHoursAPI: %s at %s",
                                        e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistApp'})
                elif mode == "2":
                    for month in range(1, 13):
                        month = str(month)
                        no_days = get_number_of_day(year, month)
                        try:
                            for day in range(1, no_days + 1):
                                today_date = datetime.datetime(
                                    int(year), int(month), int(day))
                                week_day = today_date.strftime("%A")
                                if str(week_day) in days_list:
                                    cobrowse_calender_obj = CobrowseCalendar.objects.filter(event_date=today_date, created_by=cobrowse_agent)
                                    if cobrowse_calender_obj.exists():
                                        cobrowse_calender_obj = cobrowse_calender_obj[0]
                                        if cobrowse_calender_obj.event_type == "1":
                                            cobrowse_calender_obj.delete()
                                else:
                                    cobrowse_calender_obj = CobrowseCalendar.objects.filter(event_date=today_date, created_by=cobrowse_agent)
                                    if cobrowse_calender_obj.exists():
                                        cobrowse_calender_obj = cobrowse_calender_obj[0]
                                        if cobrowse_calender_obj.event_type == "1":
                                            cobrowse_calender_obj.start_time = start_time
                                            cobrowse_calender_obj.end_time = end_time
                                            cobrowse_calender_obj.save()
                                    else:
                                        CobrowseCalendar.objects.create(
                                            event_type="1", event_date=today_date, created_by=cobrowse_agent, start_time=start_time, end_time=end_time)
                            response["status_code"] = "200"
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("CreateWorkingHoursAPI: %s at %s",
                                            e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistApp'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside CreateWorkingHoursAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistApp'})
            response["status_code"] = "500"
            response["status_message"] = str(e)

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CreateWorkingHours = CreateWorkingHoursAPI.as_view()
