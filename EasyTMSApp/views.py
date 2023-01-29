from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect

# Django REST framework
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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

from EasyTMSApp.utils import *
from EasyTMSApp.models import *
from EasyChatApp.models import *
from EasyTMSApp.constants import *
from EasyTMSApp.send_email import send_password_over_email
from DeveloperConsoleApp.utils import get_developer_console_cognodesk_settings

import json
from django.conf import settings
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format

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


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


"""

logoutAPI() : Logout user from the current session

"""


@authentication_classes([CsrfExemptSessionAuthentication, BasicAuthentication])
def logoutAPI(request):
    if request.user.is_authenticated:
        user_obj = User.objects.get(username=request.user.username)
        user_obj.is_online = False
        user_obj.save()
        try:
            secured_login_obj = SecuredLogin.objects.get(user=user_obj)
            secured_login_obj.failed_attempts = 0
            secured_login_obj.is_online = False
            secured_login_obj.save()

            description = "Logout from System"
            add_audit_trail(
                "EASYTMSAPP",
                user_obj,
                "Logout",
                description,
                json.dumps({}),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("logoutAPI: %s at %s", e, str(
                exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        logout_all(request.user.username, UserSession, Session)
        logout(request)

    return redirect("/chat/login/")


"""

homePage() : Rendring the console page of TMS

"""


def homePage(request):
    try:
        return redirect("/tms/dashboard/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("homePage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
        return render(request, 'EasyTMSApp/error_500.html')


"""

Dashboard() : Rendring the dashboard page of TMS

"""


def dashboard(request):
    try:
        if request.user.is_authenticated:

            active_agent = get_active_agent_obj(request, User, Agent)

            if active_agent.role == "admin":
                agent_objs = get_mapped_agents(active_agent, Agent, is_active=True, is_account_active=True, include_supervisor=True, include_self=False, is_absent=False)
                all_agent_objs = get_mapped_agents(active_agent, Agent, is_active=None, is_account_active=None, include_supervisor=True, include_self=True, is_absent=None)
            else:
                agent_objs = get_mapped_agents(active_agent, Agent, is_active=True, is_account_active=True, include_supervisor=True, include_self=True, is_absent=False)
                all_agent_objs = get_mapped_agents(active_agent, Agent, is_active=None, is_account_active=None, include_supervisor=True, include_self=True, is_absent=None)

            access_token = get_access_token_obj(
                active_agent, Agent, TMSAccessToken)

            bot_objs = active_agent.bots.filter(is_deleted=False)
            ticket_categories_objs = active_agent.ticket_categories.filter(
                bot__in=bot_objs)

            ticket_statuses_objs = []
            ticket_priorities_objs = []

            if access_token:
                ticket_statuses_objs = access_token.ticket_statuses.all()
                ticket_priorities_objs = access_token.ticket_priorities.all()

            channel_list = Channel.objects.filter(is_easychat_channel=True)

            return render(request, 'EasyTMSApp/dashboard.html', {
                "active_agent": active_agent,
                "easychat_version": settings.EASYCHAT_VERSION,
                "agent_objs": agent_objs,
                "access_token": access_token,
                "bot_objs": bot_objs,
                "ticket_categories_objs": ticket_categories_objs,
                "ticket_statuses_objs": ticket_statuses_objs,
                "ticket_priorities_objs": ticket_priorities_objs,
                "default_start_date": (datetime.today() - timedelta(days=7)).date(),
                "default_end_date": (datetime.today()).date(),
                "all_agent_objs": all_agent_objs,
                "channel_list": channel_list,
            })
        else:
            return redirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("dashboard: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
        return render(request, 'EasyTMSApp/error_500.html')


"""

Analytics() : Rendring the analytics page of TMS

"""


def Analytics(request):
    try:
        if request.user.is_authenticated:

            active_agent = get_active_agent_obj(request, User, Agent)
            access_token = get_access_token_obj(
                active_agent, Agent, TMSAccessToken)

            DEFAULT_ANALYTICS_START_DATETIME = (
                datetime.today() - timedelta(7)).date()

            DEFAULT_ANALYTICS_END_DATETIME = datetime.today().date()

            return render(request, 'EasyTMSApp/analytics.html', {
                "active_agent": active_agent,
                "easychat_version": settings.EASYCHAT_VERSION,
                "datetime_start": DEFAULT_ANALYTICS_START_DATETIME,
                "datetime_end": DEFAULT_ANALYTICS_END_DATETIME,
                "access_token": access_token,
            })
        else:
            return redirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Analytics: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
        return render(request, 'EasyTMSApp/error_500.html')


"""

Notifications() : Rendring the analytics page of TMS

"""


def Notifications(request):
    try:
        if request.user.is_authenticated:

            active_agent = get_active_agent_obj(request, User, Agent)
            access_token = get_access_token_obj(
                active_agent, Agent, TMSAccessToken)

            return render(request, 'EasyTMSApp/notifications.html', {
                "active_agent": active_agent,
                "easychat_version": settings.EASYCHAT_VERSION,
                "access_token": access_token,
            })
        else:
            return redirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Notifications: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
        return render(request, 'EasyTMSApp/error_500.html')


def DeveloperSettingsApiIntegration(request):
    try:
        if request.user.is_authenticated:
            active_agent = get_active_agent_obj(request, User, Agent)
            access_token = get_access_token_obj(
                active_agent, Agent, TMSAccessToken)

            if active_agent.role == "admin":
                access_token_objs = TMSAccessToken.objects.all()
                return render(request, 'EasyTMSApp/dev_api_integration.html', {
                    "active_agent": active_agent,
                    "easychat_version": settings.EASYCHAT_VERSION,
                    "access_token": access_token,
                    "access_token_objs": access_token_objs,
                })
            else:
                return HttpResponse("Invalid Access")
        else:
            return redirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error DeveloperSettingsApiIntegration %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
        return render(request, 'EasyTMSApp/error_500.html')


"""

AccessManagement() : Rendring the AccessManagement page of TMS

"""


def AccessManagement(request):
    try:
        if request.user.is_authenticated:

            active_agent = get_active_agent_obj(request, User, Agent)
            access_token = get_access_token_obj(
                active_agent, Agent, TMSAccessToken)

            is_requested_data = False

            if active_agent.role not in ["admin", "supervisor"]:
                return HttpResponse(status=401)
            if "pk" in request.GET:
                if active_agent.role != "admin":
                    return HttpResponse(status=401)
                pk = request.GET["pk"]
                requested_supervisor = Agent.objects.get(pk=pk)
                is_requested_data = True
            else:
                requested_supervisor = active_agent

            if requested_supervisor == None:
                return HttpResponse(status=401)

            bots = active_agent.bots.filter(is_deleted=False)

            ticket_categories = active_agent.ticket_categories.filter(bot__in=bots, is_deleted=False)

            agents = requested_supervisor.agents.filter(role="agent")
            supervisors = active_agent.agents.filter(role="supervisor")

            if not is_requested_data:
                for supervisor in supervisors:
                    agents = agents | supervisor.agents.all()
            agents = agents.distinct()
            total_agent_count = agents.count()
            online_agent_count = agents.filter(is_active=True).count()
            offline_agent_count = total_agent_count - online_agent_count
            active_agent_account_count = agents.filter(
                is_account_active=True).count()
            inactive_agent_account_count = total_agent_count - active_agent_account_count
            present_agent_count = agents.filter(is_absent=False).count()
            absent_agent_count = agents.filter(is_absent=True).count()

            filter_is_absent = None
            filter_is_account_active = None

            if "is_active" in request.GET:
                is_active = request.GET["is_active"]
                if is_active == "true":
                    agents = agents.filter(is_active=True)
                elif is_active == "false":
                    agents = agents.filter(is_active=False)
            elif "is_account_active" in request.GET:
                is_account_active = request.GET["is_account_active"]
                if is_account_active == "true":
                    agents = agents.filter(is_account_active=True)
                    filter_is_account_active = True
                elif is_account_active == "false":
                    agents = agents.filter(is_account_active=False)
                    filter_is_account_active = False
            elif "is_absent" in request.GET:
                is_absent = request.GET["is_absent"]
                if(is_absent == "true"):
                    agents = agents.filter(is_absent=True)
                    filter_is_absent = True
                elif is_absent == "false":
                    agents = agents.filter(is_absent=False)
                    filter_is_absent = False

            agents = agents.order_by('-agent_creation_datetime')
            supervisors = supervisors.order_by('-agent_creation_datetime')

            return render(request, 'EasyTMSApp/access_management.html', {
                "active_agent": active_agent,
                "easychat_version": settings.EASYCHAT_VERSION,
                "access_token": access_token,
                "requested_supervisor": requested_supervisor,
                "agents": agents, "supervisors": supervisors,
                "AGENT_LEVELS": AGENT_LEVELS,
                "total_agent_count": total_agent_count,
                "online_agent_count": online_agent_count,
                "offline_agent_count": offline_agent_count,
                "active_agent_account_count": active_agent_account_count,
                "inactive_agent_account_count": inactive_agent_account_count,
                "present_agent_count": present_agent_count,
                "absent_agent_count": absent_agent_count,
                "bots": bots,
                "ticket_categories": ticket_categories,
                "is_requested_data": is_requested_data,
                "filter_is_absent": filter_is_absent,
                "filter_is_account_active": filter_is_account_active,
            })
        else:
            return redirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AccessManagement: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
        return render(request, 'EasyTMSApp/error_500.html')


"""

ConsoleSettings() : Rendring the console settings page of TMS

"""


def ConsoleSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login")

        active_agent = get_active_agent_obj(request, User, Agent)

        access_token_obj = get_access_token_obj(
            active_agent, Agent, TMSAccessToken)

        if active_agent.role != "admin":

            return render(request, "EasyTMSApp/console_settings_agent.html", {
                "access_token": access_token_obj,
                "active_agent": active_agent,
                "easychat_version": settings.EASYCHAT_VERSION,
            })
        else:

            return render(request, "EasyTMSApp/console_settings.html", {
                "access_token": access_token_obj,
                "active_agent": active_agent,
                "easychat_version": settings.EASYCHAT_VERSION,
            })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ConsoleSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        return HttpResponse("Invalid Access")


"""

SaveAgentDetailsAPI() : Save Agent Details API

"""


class SaveAgentDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, User, Agent)
            user = active_agent.user

            old_password = remo_html_from_string(data["old_password"])
            new_password = remo_html_from_string(data["new_password"])

            old_password = remo_special_tag_from_string(old_password)
            new_password = remo_special_tag_from_string(new_password)

            changed_data = {}

            if "agent_mobile_number" in data:
                changed_data["agent_mobile_number"] = data["agent_mobile_number"]

            if "agent_name" in data:
                changed_data["agent_name"] = data["agent_name"]

            is_valid_password = True
            is_password_changed = False
            if old_password != "":
                if not user.check_password(old_password):
                    is_valid_password = False
                else:
                    is_password_changed = True

            if is_valid_password:

                if is_password_changed:
                    if(validate_user_new_password(active_agent, new_password, old_password, AgentPasswordHistory) == "VALID"):
                        user.is_online = False
                        user.set_password(new_password)
                        user.save()

                        new_password_hash = hashlib.sha256(
                            new_password.encode()).hexdigest()
                        AgentPasswordHistory.objects.create(
                            agent=active_agent, password_hash=new_password_hash)

                        description = "User (" + user.first_name + "'s) password was changed"

                        add_audit_trail(
                            "EASYTMSAPP",
                            user,
                            "Updated-User",
                            description,
                            json.dumps({}),
                            request.META.get("PATH_INFO"),
                            request.META.get('HTTP_X_FORWARDED_FOR')
                        )
                    else:
                        response["status"] = 102
                        response["message"] = "Password Matched with previous password"

                if response["status"] != 102:
                    personal_details_changed = False
                    if user.first_name != strip_html_tags(data["agent_name"]):
                        personal_details_changed = True
                    description = "User (" + user.first_name + "'s) personal details changed"

                    agent_name = strip_html_tags(data["agent_name"])
                    agent_name = agent_name[0:30]
                    user.first_name = agent_name
                    user.save()
                    if active_agent.role != "admin":

                        if active_agent.phone_number != strip_html_tags(data["agent_mobile_number"]):
                            personal_details_changed = True

                        active_agent.phone_number = strip_html_tags(
                            data["agent_mobile_number"])

                        active_agent.save()

                    if personal_details_changed:
                        add_audit_trail(
                            "EASYTMSAPP",
                            user,
                            "Updated-User",
                            description,
                            json.dumps(changed_data),
                            request.META.get("PATH_INFO"),
                            request.META.get('HTTP_X_FORWARDED_FOR')
                        )

                    response["status"] = 200
                    response["message"] = "success"
                    response["is_password_changed"] = is_password_changed
            else:
                response["status"] = 101
                response[
                    "message"] = "Your old password is incorrect. Kindly enter valid password."
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveAgentDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveAgentDetails = SaveAgentDetailsAPI.as_view()


"""

SaveTMSMetaDetailsGeneralAPI() : Save TMS Meta Details API

"""


class SaveTMSMetaDetailsGeneralAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            active_agent = get_active_agent_obj(
                request, User, Agent)

            if active_agent.role == "admin":
                active_agent.options = json.dumps(data)
                active_agent.save()

                access_token_obj = get_access_token_obj(
                    active_agent, Agent, TMSAccessToken)

                if data["reset"] == "false":
                    if data["tms_console_theme_color"] is None:
                        access_token_obj.tms_console_theme_color = DEFAULT_TMS_CONSOLE_THEME_COLOR
                    else:
                        access_token_obj.tms_console_theme_color = json.dumps(
                            data["tms_console_theme_color"])

                    access_token_obj.save()

                elif data["reset"] == "true":
                    access_token_obj.tms_console_theme_color = DEFAULT_TMS_CONSOLE_THEME_COLOR
                    access_token_obj.tms_console_logo = None
                    access_token_obj.save()

                response["status"] = 200
                response["message"] = "success"

                description = "Custom App Configuration Changes"
                add_audit_trail(
                    "EASYTMSAPP",
                    active_agent.user,
                    "Change-App-Config",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveTMSMetaDetailsGeneralAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveTMSMetaDetailsGeneral = SaveTMSMetaDetailsGeneralAPI.as_view()


"""

DeleteTMSLogoAPI() : Delete TMS Logo API

"""


class DeleteTMSLogoAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            active_agent = get_active_agent_obj(
                request, User, Agent)

            if active_agent.role == "admin":

                access_token_obj = get_access_token_obj(
                    active_agent, Agent, TMSAccessToken)
                access_token_obj.tms_console_logo = ""
                access_token_obj.save()
                response["status"] = 200
                response["message"] = "success"
                response["tms_default_logo"] = TMS_DEFAULT_LOGO
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteTMSLogoAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteTMSLogo = DeleteTMSLogoAPI.as_view()


"""

UploadTMSLogoAPI() : Upload TMS Logo API

"""


class UploadTMSLogoAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(
                request, User, Agent)

            if active_agent.role == "admin":

                access_token_obj = get_access_token_obj(
                    active_agent, Agent, TMSAccessToken)

                filename = strip_html_tags(data["filename"])
                base64_data = strip_html_tags(data["base64_file"])

                filename = generate_random_key(
                    10) + "_" + filename.replace(" ", "")

                file_path = "files/" + filename

                file_extention = file_path.split(".")[-1]
                file_extention = file_extention.lower()

                allowed_files_list = ["png", "jpg", "jpeg", "bmp", 
                                      "gif", "tiff", "exif", "jfif", "webm", "mpg", "jpe"]
                if file_extention in allowed_files_list:
                    media_type = "image"
                else:
                    media_type = None

                if media_type == None or check_malicious_file_from_filename(filename, allowed_files_list) or check_malicious_file_from_content(base64_data, allowed_files_list):
                    response["status"] = 300
                else:
                    fh = open(file_path, "wb")
                    fh.write(base64.b64decode(base64_data))
                    fh.close()
                    access_token_obj.tms_console_logo = file_path
                    access_token_obj.save()

                    response["status"] = 200
                    response["message"] = "success"
                    response["file_path"] = file_path
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadTMSLogoAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadTMSLogo = UploadTMSLogoAPI.as_view()


"""

GetActiveTicketsAPI() : return all active ticket objs

"""


class GetActiveTicketsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def apply_bot_filter(self, data, ticket_objs):
        bots = data["bots"]
        filtered_bots = Bot.objects.filter(pk__in=bots)

        if bots and len(bots) > 0:
            ticket_objs = ticket_objs.filter(bot__in=filtered_bots)

        return ticket_objs

    def apply_bot_channel_filter(self, data, ticket_objs):
        bot_channels = data["bot_channels"]
        filtered_bot_channels = Channel.objects.filter(name__in=bot_channels)

        if bot_channels and len(bot_channels) > 0:
            ticket_objs = ticket_objs.filter(bot_channel__in=filtered_bot_channels)

        return ticket_objs

    def apply_ticket_status_filter(self, data, ticket_objs):
        ticket_status = data["ticket_status"]
        ticket_status_objs = TicketStatus.objects.filter(pk__in=ticket_status)

        if ticket_status and len(ticket_status) > 0:
            ticket_objs = ticket_objs.filter(ticket_status__in=ticket_status_objs)

        return ticket_objs

    def apply_ticket_category_filter(self, data, ticket_objs):
        ticket_category = data["ticket_category"]
        ticket_category_objs = TicketCategory.objects.filter(pk__in=ticket_category)

        if ticket_category and len(ticket_category) > 0:
            ticket_objs = ticket_objs.filter(ticket_category__in=ticket_category_objs)

        return ticket_objs

    def apply_ticket_priority_filter(self, data, ticket_objs):
        ticket_priority = data["ticket_priority"]
        ticket_priority_objs = TicketPriority.objects.filter(pk__in=ticket_priority)

        if ticket_priority and len(ticket_priority) > 0:
            ticket_objs = ticket_objs.filter(ticket_priority__in=ticket_priority_objs)

        return ticket_objs

    def apply_date_filters(self, data, ticket_objs):
        if 'selected_date_filter' in data and data['selected_date_filter'] != '':
            selected_date_filter = data['selected_date_filter']
        else:
            selected_date_filter = 'all'

        if selected_date_filter == '4':
            return ticket_objs

        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

        if selected_date_filter == '2':
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()

        elif selected_date_filter == '3':
            start_date = datetime.now() - timedelta(days=90)
            end_date = datetime.now()

        elif selected_date_filter == '5':
            date_format = "%Y-%m-%d"
            start_date = data['start_date']
            end_date = data['end_date']

            start_date = datetime.strptime(
                start_date, date_format).date()

            end_date = datetime.strptime(
                end_date, date_format).date()

        ticket_objs = ticket_objs.filter(
            issue_date_time__date__gte=start_date, issue_date_time__date__lte=end_date)

        return ticket_objs

    def apply_agent_filter(self, data, ticket_objs):
        agent_id_list = data["agent_id_list"]
        agent_objs = Agent.objects.filter(pk__in=agent_id_list)

        if agent_id_list and len(agent_id_list) > 0:
            ticket_objs = ticket_objs.filter(agent__in=agent_objs)

        return ticket_objs

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            page = data["page"]

            active_agent = get_active_agent_obj(request, User, Agent)
            ticket_objs = get_ticket_objs(
                active_agent, Agent, Ticket, TMSAccessToken, None)

            ticket_objs = self.apply_bot_filter(data, ticket_objs)
            ticket_objs = self.apply_bot_channel_filter(data, ticket_objs)
            ticket_objs = self.apply_ticket_status_filter(data, ticket_objs)
            ticket_objs = self.apply_ticket_category_filter(data, ticket_objs)
            ticket_objs = self.apply_ticket_priority_filter(data, ticket_objs)
            ticket_objs = self.apply_date_filters(data, ticket_objs)
            ticket_objs = self.apply_agent_filter(data, ticket_objs)

            ticket_objs = ticket_objs.order_by('-issue_date_time')

            total_rows_per_pages = 20
            total_ticket_objs = ticket_objs.count()

            paginator = Paginator(
                ticket_objs, total_rows_per_pages)

            try:
                ticket_objs = paginator.page(page)
            except PageNotAnInteger:
                ticket_objs = paginator.page(1)
            except EmptyPage:
                ticket_objs = paginator.page(paginator.num_pages)

            if page != None:
                start_point = total_rows_per_pages * (int(page) - 1) + 1
                end_point = min(total_rows_per_pages *
                                int(page), total_ticket_objs)
                if start_point > end_point:
                    start_point = max(end_point - len(ticket_objs) + 1, 1)
            else:
                start_point = 1
                end_point = min(total_rows_per_pages, total_ticket_objs)

            pagination_range = ticket_objs.paginator.page_range

            has_next = ticket_objs.has_next()
            has_previous = ticket_objs.has_previous()
            next_page_number = -1
            previous_page_number = -1

            if has_next:
                next_page_number = ticket_objs.next_page_number()
            if has_previous:
                previous_page_number = ticket_objs.previous_page_number()

            pagination_metadata = {
                'total_count': total_ticket_objs,
                'start_point': start_point,
                'end_point': end_point,
                'page_range': [pagination_range.start, pagination_range.stop],
                'has_next': has_next,
                'has_previous': has_previous,
                'next_page_number': next_page_number,
                'previous_page_number': previous_page_number,
                'number': ticket_objs.number,
                'num_pages': ticket_objs.paginator.num_pages
            }

            active_tickets = []
            for ticket_obj in ticket_objs:
                active_tickets.append(parse_ticket_details(ticket_obj))

            response["status"] = 200
            response["message"] = "success"
            response["active_tickets"] = active_tickets
            response["pagination_metadata"] = pagination_metadata
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetActiveTicketsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetActiveTickets = GetActiveTicketsAPI.as_view()


"""

GetTicketDetailsAPI() : return all active ticket objs

"""


class GetTicketDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            ticket_id = data["ticket_id"]

            ticket_obj = Ticket.objects.filter(ticket_id=ticket_id).first()

            if ticket_obj:
                ticket_details = parse_ticket_details(ticket_obj)
                response["status"] = 200
                response["message"] = "success"
                response["ticket_details"] = ticket_details
            else:
                response["status"] = 301
                response["message"] = "Invalid Ticket ID"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetTicketDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetTicketDetails = GetTicketDetailsAPI.as_view()


"""

GetMappedAgentsAPI() : return all active ticket objs

"""


class GetMappedAgentsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, User, Agent)

            if active_agent.role == "admin":
                agent_objs = get_mapped_agents(active_agent, Agent, is_active=True, is_account_active=True, include_supervisor=True, include_self=False, is_absent=False)
            else:
                agent_objs = get_mapped_agents(active_agent, Agent, is_active=True, is_account_active=True, include_supervisor=True, include_self=True, is_absent=False)

            active_agent_count = 0
            mapped_agents = []
            for agent_obj in agent_objs:
                agent_details = parse_agent_details(agent_obj)
                mapped_agents.append(agent_details)
                if agent_obj.is_active and agent_obj.is_account_active:
                    active_agent_count += 1

            response["status"] = 200
            response["message"] = "success"
            response["mapped_agents"] = mapped_agents
            response["active_agent_count"] = active_agent_count
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetMappedAgentsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetMappedAgents = GetMappedAgentsAPI.as_view()


"""

ActiveAgentMetaDataAPI() : return all active ticket objs

"""


class ActiveAgentMetaDataAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = get_active_agent_obj(request, User, Agent)
            access_token = get_access_token_obj(
                active_agent, Agent, TMSAccessToken)

            agent_metadata = json.loads(
                active_agent.console_meta_data)

            ticket_statuses = []
            ticket_statuses_objs = access_token.ticket_statuses.all()
            for ticket_statuses_obj in ticket_statuses_objs:
                ticket_statuses.append({
                    'pk': ticket_statuses_obj.pk,
                    'name': ticket_statuses_obj.name
                })

            ticket_priorities = []
            ticket_priorities_objs = access_token.ticket_priorities.all()
            for ticket_priorities_obj in ticket_priorities_objs:
                ticket_priorities.append({
                    'pk': ticket_priorities_obj.pk,
                    'name': ticket_priorities_obj.name
                })

            bots = []
            bot_objs = active_agent.bots.filter(is_deleted=False)
            for bot_obj in bot_objs:
                bots.append({
                    'pk': bot_obj.pk,
                    'name': bot_obj.name,
                    'bot_display_name': bot_obj.bot_display_name,
                })

            channels = []
            channel_objs = Channel.objects.filter(is_easychat_channel=True)
            for channel_obj in channel_objs:
                channels.append({
                    'pk': channel_obj.pk,
                    'name': channel_obj.name
                })

            ticket_categories = []
            ticket_categories_objs = active_agent.ticket_categories.filter(
                bot__in=bot_objs)
            for ticket_categories_obj in ticket_categories_objs:
                ticket_categories.append(parse_ticket_category(ticket_categories_obj))

            agent_metadata['ticket_statuses'] = ticket_statuses
            agent_metadata['ticket_priorities'] = ticket_priorities
            agent_metadata['bots'] = bots
            agent_metadata['channels'] = channels
            agent_metadata['ticket_categories'] = ticket_categories
            agent_metadata["active_agent_details"] = parse_agent_details(active_agent)
            agent_metadata["cognoai_celebration"] = access_token.cognoai_celebration
            agent_metadata["cognoai_quote"] = access_token.cognoai_quote

            response["status"] = 200
            response["message"] = "success"
            response["agent_metadata"] = agent_metadata
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ActiveAgentMetaDataAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ActiveAgentMetaData = ActiveAgentMetaDataAPI.as_view()


"""

SaveAgentLeadTableMetadataAPI() : return all active ticket objs

"""


class SaveAgentLeadTableMetadataAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            lead_data_cols = data['lead_data_cols']

            active_agent = get_active_agent_obj(request, User, Agent)
            console_meta_data = json.loads(active_agent.console_meta_data)
            console_meta_data['lead_data_cols'] = lead_data_cols

            active_agent.console_meta_data = json.dumps(console_meta_data)
            active_agent.save()

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveAgentLeadTableMetadataAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveAgentLeadTableMetadata = SaveAgentLeadTableMetadataAPI.as_view()


"""

UpdateTicketPriorityAPI() : update ticket_priority in ticket object

"""


class UpdateTicketPriorityAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, User, Agent)
            ticket_id = data['ticket_id']
            selected_priority_pk = data['selected_priority_pk']

            ticket_obj = Ticket.objects.filter(ticket_id=ticket_id).first()
            selected_priority_obj = TicketPriority.objects.filter(
                pk=selected_priority_pk).first()

            if ticket_obj and selected_priority_obj:
                response["status"] = 200
                response["message"] = "success"

                old_priority = ticket_obj.ticket_priority

                if old_priority == None or (old_priority and old_priority.name != selected_priority_obj.name):

                    ticket_obj.ticket_priority = selected_priority_obj

                    try:
                        action_type = "PRIORITY_CHANGED"
                        if old_priority == None:
                            description = active_agent.user.username + " set priority to " + selected_priority_obj.name.title()
                        else:
                            description = active_agent.user.username + " changed priority from " + old_priority.name.title() + " to " + selected_priority_obj.name.title()

                        save_ticket_audit_trail(ticket_obj, active_agent, action_type, description, TicketAuditTrail)

                        agent_objs = get_relevant_agent_list(ticket_obj, Agent)
                        for agent_obj in agent_objs:

                            if agent_obj != active_agent:
                                create_user_notification(agent_obj, ticket_obj, description, UserNotification)
                                send_action_info_to_agent(agent_obj, action_name="new_user_notification", action_info={
                                    "send_notification": True,
                                    "notification_message": description,
                                    "ticket_id": ticket_obj.ticket_id
                                })

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Error on Audit Trail Save in update priority %s at %s",
                                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

                ticket_obj.save()

            elif ticket_obj == None:
                response["status"] = 301
                response["message"] = "Invalid Ticket ID"
            elif selected_priority_obj == None:
                response["status"] = 302
                response["message"] = "Invalid Ticket Priority PK"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateTicketPriorityAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateTicketPriority = UpdateTicketPriorityAPI.as_view()


"""

UpdateTicketCategoryAPI() : update ticket_categoty in ticket object

"""


class UpdateTicketCategoryAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, User, Agent)
            ticket_id = data['ticket_id']
            selected_category_pk = data['selected_category_pk']

            ticket_obj = Ticket.objects.filter(ticket_id=ticket_id).first()
            selected_category_obj = TicketCategory.objects.filter(
                pk=selected_category_pk).first()

            if ticket_obj and selected_category_obj:
                response["status"] = 200
                response["message"] = "success"

                old_ticket_category = ticket_obj.ticket_category

                if old_ticket_category == None or (old_ticket_category and old_ticket_category.ticket_category != selected_category_obj.ticket_category):
                    ticket_obj.ticket_category = selected_category_obj

                    try:
                        action_type = "CATEGORY_CHANGED"
                        if old_ticket_category == None:
                            description = active_agent.user.username + " set category to " + selected_category_obj.ticket_category.title()
                        else:
                            description = active_agent.user.username + " changed category from " + old_ticket_category.ticket_category.title() + " to " + selected_category_obj.ticket_category.title()
                        save_ticket_audit_trail(ticket_obj, active_agent, action_type, description, TicketAuditTrail)

                        agent_objs = get_relevant_agent_list(ticket_obj, Agent)
                        for agent_obj in agent_objs:

                            if agent_obj != active_agent:
                                create_user_notification(agent_obj, ticket_obj, description, UserNotification)
                                send_action_info_to_agent(agent_obj, action_name="new_user_notification", action_info={
                                    "send_notification": True,
                                    "notification_message": description,
                                    "ticket_id": ticket_obj.ticket_id
                                })
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Error on Audit Trail Save in update category %s at %s",
                                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

                ticket_obj.save()

            elif ticket_obj == None:
                response["status"] = 301
                response["message"] = "Invalid Ticket ID"
            elif selected_category_obj == None:
                response["status"] = 302
                response["message"] = "Invalid Ticket Priority PK"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateTicketCategoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateTicketCategory = UpdateTicketCategoryAPI.as_view()


"""

AssignAgentAPI() : update ticket_categoty in ticket object

"""


class AssignAgentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, User, Agent)
            ticket_ids = data['ticket_ids']
            selected_agent_pk = data['selected_agent_pk']

            selected_agent_obj = Agent.objects.filter(
                pk=selected_agent_pk).first()

            if selected_agent_obj == None:
                response["status"] = 302
                response["message"] = "Invalid Agent PK"
            else:
                unassigned_ticket_list = []
                for ticket_id in ticket_ids:
                    ticket_obj = Ticket.objects.filter(
                        ticket_id=ticket_id).first()

                    if ticket_obj:

                        old_agent = ticket_obj.agent

                        if old_agent == None or (old_agent and old_agent.user.username != selected_agent_obj.user.username):
                            ticket_obj.agent = selected_agent_obj

                            try:
                                action_type = "AGENT_ASSIGN"
                                if old_agent == None:
                                    description = active_agent.user.username + " assigned to " + selected_agent_obj.user.username
                                else:
                                    description = active_agent.user.username + " changed assignee from " + old_agent.user.username + " to " + selected_agent_obj.user.username

                                save_ticket_audit_trail(ticket_obj, active_agent, action_type, description, TicketAuditTrail)

                                agent_objs = get_relevant_agent_list(ticket_obj, Agent)

                                for agent_obj in agent_objs:

                                    if agent_obj not in [selected_agent_obj, active_agent]:
                                        create_user_notification(agent_obj, ticket_obj, description, UserNotification)
                                        send_action_info_to_agent(agent_obj, action_name="new_user_notification", action_info={
                                            "send_notification": True,
                                            "notification_message": description,
                                            "ticket_id": ticket_obj.ticket_id
                                        })
                                    elif agent_obj == selected_agent_obj:
                                        create_user_notification(agent_obj, ticket_obj, description, UserNotification)
                                        notification_message = "Hi, " + get_agent_name(agent_obj) + "! A new ticket is assigned to you on Cogno desk."
                                        send_action_info_to_agent(agent_obj, action_name="new_ticket_assigned", action_info={
                                            "send_notification": True,
                                            "notification_message": notification_message,
                                            "ticket_id": ticket_obj.ticket_id
                                        })

                                if old_agent:
                                    description = get_agent_name(active_agent) + " removed you from assignee"
                                    create_user_notification(old_agent, ticket_obj, description, UserNotification)
                                    send_action_info_to_agent(old_agent, action_name="removed_from_assignee", action_info={
                                        "send_notification": True,
                                        "notification_message": description,
                                        "ticket_id": ticket_obj.ticket_id
                                    })
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logger.error("Error on Audit Trail Save on generate query %s at %s",
                                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

                        old_ticket_status = ticket_obj.ticket_status
                        if old_ticket_status == None or (old_ticket_status and old_ticket_status.name != "PENDING"):
                            change_ticket_status("PENDING", ticket_obj, TicketStatus)

                            try:
                                action_type = "STATUS_CHANGED"
                                if old_ticket_status == None:
                                    description = active_agent.user.username + " set status to " + "PENDING".title()
                                else:
                                    description = active_agent.user.username + " changed status from " + old_ticket_status.name.title() + " to " + "PENDING".title()
                                save_ticket_audit_trail(ticket_obj, active_agent, action_type, description, TicketAuditTrail)

                                agent_objs = get_relevant_agent_list(ticket_obj, Agent)

                                for agent_obj in agent_objs:

                                    if agent_obj != active_agent:
                                        create_user_notification(agent_obj, ticket_obj, description, UserNotification)
                                        send_action_info_to_agent(agent_obj, action_name="new_user_notification", action_info={
                                            "send_notification": True,
                                            "notification_message": description,
                                            "ticket_id": ticket_obj.ticket_id
                                        })
                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logger.error("Error on Audit Trail Save on agent query %s at %s",
                                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

                        ticket_obj.save()
                    else:
                        unassigned_ticket_list.append(ticket_id)

                if len(unassigned_ticket_list) == len(ticket_ids):
                    response["status"] = 301
                    response["message"] = "Invalid Ticket ID(s)"
                    response["unassigned_tickets"] = unassigned_ticket_list
                else:
                    response["status"] = 200
                    response["message"] = "success"
                    response["unassigned_tickets"] = unassigned_ticket_list

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AssignAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AssignAgent = AssignAgentAPI.as_view()


"""

SaveAgentCommentsAPI() : update ticket_categoty in ticket object

"""


class SaveAgentCommentsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            ticket_id = data['ticket_id']
            comment = data['comment']
            comment = process_agent_comment(comment)

            is_resolved = data['is_resolved']
            send_to_customer = data['send_to_customer']

            active_agent = get_active_agent_obj(request, User, Agent)
            access_token = get_access_token_obj(active_agent, Agent, TMSAccessToken)
            ticket_obj = Ticket.objects.filter(ticket_id=ticket_id).first()

            if comment == "":
                response["status"] = 302
                response["message"] = "Malicious Comment"
            elif ticket_obj:

                if is_resolved:
                    action_type = "RESOLVED_COMMENT"
                    description = comment
                    ticket_audit_trail_obj = save_ticket_audit_trail(ticket_obj, active_agent, action_type, description, TicketAuditTrail)

                    agent_objs = get_relevant_agent_list(ticket_obj, Agent)
                    for agent_obj in agent_objs:

                        if agent_obj != active_agent:
                            description = active_agent.user.username + " added comment."
                            create_user_notification(agent_obj, ticket_obj, description, UserNotification)
                            send_action_info_to_agent(agent_obj, action_name="new_user_notification", action_info={
                                "send_notification": True,
                                "notification_message": description,
                                "ticket_id": ticket_obj.ticket_id
                            })
                else:
                    action_type = "AGENT_COMMENT"
                    description = comment
                    ticket_audit_trail_obj = save_ticket_audit_trail(ticket_obj, active_agent, action_type, description, TicketAuditTrail)

                    agent_objs = get_relevant_agent_list(ticket_obj, Agent)
                    for agent_obj in agent_objs:

                        if agent_obj != active_agent:
                            description = active_agent.user.username + " added comment."
                            create_user_notification(agent_obj, ticket_obj, description, UserNotification)
                            send_action_info_to_agent(agent_obj, action_name="new_user_notification", action_info={
                                "send_notification": True,
                                "notification_message": description,
                                "ticket_id": ticket_obj.ticket_id
                            })

                if is_resolved:
                    ticket_resolved_action(active_agent, ticket_obj, TicketStatus, TicketAuditTrail, UserNotification, Agent)

                if send_to_customer:
                    generate_agent_query(active_agent, ticket_obj, access_token, ticket_audit_trail_obj, {}, AgentQuery)

                response["status"] = 200
                response["message"] = "success"
            elif ticket_obj == None:
                response["status"] = 301
                response["message"] = "Invalid Ticket ID"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveAgentCommentsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveAgentComments = SaveAgentCommentsAPI.as_view()


"""

GetAgentCommentsAPI() : update ticket_categoty in ticket object

"""


class GetAgentCommentsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            ticket_id = data['ticket_id']

            ticket_obj = Ticket.objects.filter(ticket_id=ticket_id).first()

            if ticket_obj:

                comments = []

                audit_trail_objs = TicketAuditTrail.objects.filter(
                    ticket=ticket_obj, action_type__in=["AGENT_COMMENT", "RESOLVED_COMMENT"])
                for audit_trail_obj in audit_trail_objs:
                    comments.append(parse_ticket_audit_trail(audit_trail_obj))

                response["status"] = 200
                response["message"] = "success"
                response["comments"] = comments
            elif ticket_obj == None:
                response["status"] = 301
                response["message"] = "Invalid Ticket ID"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAgentCommentsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetAgentComments = GetAgentCommentsAPI.as_view()


"""

GetTicketAuditTrailAPI() : get ticket audit trail

"""


class GetTicketAuditTrailAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            ticket_id = data['ticket_id']

            ticket_obj = Ticket.objects.filter(ticket_id=ticket_id).first()

            if ticket_obj:

                audit_trail_objs = TicketAuditTrail.objects.filter(ticket=ticket_obj)
                audit_trail_objs = audit_trail_objs.order_by('datetime')
                audit_trail = []
                for audit_trail_obj in audit_trail_objs:
                    audit_trail.append(parse_ticket_audit_trail(audit_trail_obj))

                response["status"] = 200
                response["message"] = "success"
                response["audit_trail"] = audit_trail
            elif ticket_obj == None:
                response["status"] = 301
                response["message"] = "Invalid Ticket ID"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetTicketAuditTrailAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetTicketAuditTrail = GetTicketAuditTrailAPI.as_view()


############################################## Access Management ##############################################


class AddNewAgentDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def check_agent_already_exist(self, agent_mobile, agent_email):

        if Agent.objects.filter(user__email=agent_email).count() > 0:
            return True

        elif agent_mobile != None and Agent.objects.filter(phone_number=agent_mobile).count() > 0:
            return True

        return False

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, User, Agent)

            if active_agent.role != "agent":
                agent_mobile = strip_html_tags(data["agent_mobile"])
                agent_mobile = remo_html_from_string(agent_mobile)
                agent_email = strip_html_tags(data["agent_email"])
                agent_email = remo_html_from_string(agent_email)

                if agent_mobile == "":
                    agent_mobile = None

                if self.check_agent_already_exist(agent_mobile, agent_email):

                    response["status"] = 301
                    response[
                        "message"] = "Matching agent already exists"
                elif data["user_type"] in ["agent", "supervisor"]:

                    agent_name = strip_html_tags(data["agent_name"])
                    agent_name = remo_html_from_string(agent_name)
                    user_type = strip_html_tags(data["user_type"])
                    user_type = remo_html_from_string(user_type)
                    platform_url = strip_html_tags(data["platform_url"])
                    platform_url = remo_html_from_string(platform_url)
                    selected_supervisor_pk_list = data[
                        "selected_supervisor_pk_list"]
                    selected_bot_pk_list = data[
                        "selected_bot_pk_list"]
                    selected_ticket_category_pk_list = data[
                        "selected_ticket_category_pk_list"]

                    user = None

                    password = generate_password("TMS")

                    try:
                        user = User.objects.get(username=agent_email)
                        user.email = agent_email
                        user.save()
                    except Exception:
                        user = User.objects.create(first_name=agent_name,
                                                   email=agent_email,
                                                   username=agent_email,
                                                   status="2",
                                                   role="bot_builder")
                        user.set_password(password)
                        user.save()

                    thread = threading.Thread(target=send_password_over_email, args=(
                        agent_email, agent_name, password, platform_url, ), daemon=True)
                    thread.start()

                    user.set_password(password)
                    user.save()

                    agent = Agent.objects.create(user=user,
                                                 phone_number=agent_mobile,
                                                 role=user_type
                                                 )

                    add_selected_supervisor(
                        selected_supervisor_pk_list, active_agent, agent, Agent)
                    add_bot_to_agent(
                        agent, selected_bot_pk_list, Bot)
                    add_ticket_category_to_agent(
                        agent, selected_ticket_category_pk_list, TicketCategory)

                    description = "New " + \
                        data["user_type"] + \
                        " (" + agent_name + ") has been added"

                    add_audit_trail(
                        "EASYTMSAPP",
                        active_agent.user,
                        "Add-User",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddNewAgentDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AddNewAgentDetails = AddNewAgentDetailsAPI.as_view()


class UpdateAgentDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def check_agent_already_exist(self, agent_mobile, agent_email, target_agent):

        if target_agent.user.email != agent_email and Agent.objects.filter(user__email=agent_email).count() > 0: 
            return True

        elif agent_mobile != None and target_agent.phone_number != agent_mobile and Agent.objects.filter(phone_number=agent_mobile).count() > 0:
            return True

        return False

    def post(self, request, *args, **kwargs):
        logger.info("Into Update Agent Details API",
                    extra={'AppName': 'EasyTMS'})
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, User, Agent)

            if active_agent.role != "agent":
                try:
                    pk = strip_html_tags(data["pk"])
                    pk = remo_html_from_string(pk)
                    agent = Agent.objects.get(
                        user=User.objects.get(pk=int(pk)))
                    agent_mobile = strip_html_tags(data["agent_mobile"])
                    agent_mobile = remo_html_from_string(agent_mobile)

                    agent_email = strip_html_tags(data["agent_email"])
                    agent_email = remo_html_from_string(agent_email)

                    if agent_mobile == "":
                        agent_mobile = None

                    if self.check_agent_already_exist(agent_mobile, agent_email, agent):
                        response["status"] = 301
                        response[
                            "message"] = "Matching cobrowsing agent already exists"

                    elif data["user_type"] in ["agent", "supervisor"]:

                        agent_name = strip_html_tags(data["agent_name"])
                        agent_name = remo_html_from_string(agent_name)
                        user_type = strip_html_tags(data["user_type"])
                        user_type = remo_html_from_string(user_type)
                        platform_url = strip_html_tags(data["platform_url"])
                        platform_url = remo_html_from_string(platform_url)
                        selected_supervisor_pk_list = data[
                            "selected_supervisor_pk_list"]
                        previous_supervisor_list = Agent.objects.filter(
                            agents__pk=agent.pk)
                        selected_bot_pk_list = data[
                            "selected_bot_pk_list"]
                        selected_ticket_category_pk_list = data[
                            "selected_ticket_category_pk_list"]

                        if agent.user.email != agent_email:
                            password = generate_password("TMS")
                            agent.user.set_password(password)
                            agent.user.save()
                            thread = threading.Thread(target=send_password_over_email, args=(
                                agent_email, agent_name, password, platform_url, ), daemon=True)
                            thread.start()

                        agent.user.first_name = agent_name
                        agent.user.email = agent_email
                        agent.user.username = agent_email

                        agent.phone_number = agent_mobile
                        agent.role = user_type
                        if user_type == "agent":
                            agents = agent.agents.all()
                            for agent_obj in agents:
                                agent.agents.remove(agent_obj)
                                agent.save()
                                supervisor_count = Agent.objects.filter(
                                    agents=agent_obj).count()
                                if supervisor_count == 0:
                                    active_agent.agents.add(agent_obj)
                                    active_agent.save()
                        if active_agent.role == "admin":
                            for previous_supervisor in previous_supervisor_list:
                                previous_supervisor.agents.remove(
                                    agent)
                                previous_supervisor.save()

                            add_selected_supervisor(
                                selected_supervisor_pk_list, active_agent, agent, Agent)

                        agent.bots.clear()
                        agent.ticket_categories.clear()
                        agent.user.save()
                        agent.save()
                        active_agent.save()

                        add_bot_to_agent(
                            agent, selected_bot_pk_list, Bot)
                        add_ticket_category_to_agent(
                            agent, selected_ticket_category_pk_list, TicketCategory)

                        description = "New Details for " + \
                            data["user_type"] + \
                            " (" + agent_name + ") has been added"

                        add_audit_trail(
                            "EASYTMSAPP",
                            active_agent.user,
                            "Updated-User",
                            description,
                            json.dumps(data),
                            request.META.get("PATH_INFO"),
                            request.META.get('HTTP_X_FORWARDED_FOR')
                        )

                        response["status"] = 200
                        response["message"] = "success"
                        logger.info("Successfully exited Update Agent Details API", extra={
                                    'AppName': 'EasyTMS'})

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error Agent not found %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateAgentDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateAgentDetails = UpdateAgentDetailsAPI.as_view()


class DeleteTMSAgentAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            agent_pk = data["agent_pk"]
            agent_pk = strip_html_tags(agent_pk)
            agent_pk = remo_special_tag_from_string(agent_pk)

            agent = Agent.objects.get(pk=agent_pk)
            if agent == None:
                response['status'] = 300
            else:
                agent_name = agent.user.username
                user_type = agent.role
                agent.delete()
                response['status'] = 200

            description = user_type[
                0].upper() + user_type[1:] + " (" + agent_name + ") has been deleted"

            add_audit_trail(
                "EASYTMSAPP",
                agent.user,
                "Delete-User",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteTMSAgentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DeleteTMSAgent = DeleteTMSAgentAPI.as_view()


class ChangeAgentActivateStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            agent_id_list = data["agent_id_list"]
            activate = data["activate"]

            active_agent = get_active_agent_obj(request, User, Agent)

            if active_agent.role != "agent" and (activate == True or activate == False):

                if response['status'] != 301:
                    agent_objs = get_mapped_agents(
                        active_agent, Agent, is_active=None, is_account_active=None, include_supervisor=True, include_self=True, is_absent=None)
                    for agent_id in agent_id_list:
                        agent = Agent.objects.get(pk=int(agent_id))
                        if agent in agent_objs:
                            agent.is_account_active = activate
                            agent.save()

                            if not activate:
                                description = agent.user.username + \
                                    " (" + agent.role + ") was marked as inactive"

                                add_audit_trail(
                                    "EASYTMSAPP",
                                    active_agent.user,
                                    "Deactivate-User",
                                    description,
                                    json.dumps(data),
                                    request.META.get("PATH_INFO"),
                                    request.META.get('HTTP_X_FORWARDED_FOR')
                                )
                            else:
                                description = agent.user.username + \
                                    " (" + agent.role + ") was marked as active"

                                add_audit_trail(
                                    "EASYTMSAPP",
                                    active_agent.user,
                                    "Activate-User",
                                    description,
                                    json.dumps(data),
                                    request.META.get("PATH_INFO"),
                                    request.META.get('HTTP_X_FORWARDED_FOR')
                                )

                    response["status"] = 200
                    response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ChangeAgentActivateStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ChangeAgentActivateStatus = ChangeAgentActivateStatusAPI.as_view()


class ChangeAgentAbsentStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            agent_id_list = data["agent_id_list"]
            is_absent = data["is_absent"]

            active_agent = get_active_agent_obj(request, User, Agent)

            if active_agent.role != "agent" and (is_absent == True or is_absent == False):

                agent_objs = get_mapped_agents(active_agent, Agent, is_active=None, is_account_active=None, include_supervisor=True, include_self=True, is_absent=None)

                for agent_id in agent_id_list:
                    agent = Agent.objects.get(pk=int(agent_id))
                    if agent in agent_objs:
                        agent.is_absent = is_absent
                        agent.save()

                        if is_absent == True:
                            description = agent.user.username + \
                                " (" + agent.role + ") was marked as absent"

                            add_audit_trail(
                                "EASYTMSAPP",
                                active_agent.user,
                                "User-Presence-Status",
                                description,
                                json.dumps(data),
                                request.META.get("PATH_INFO"),
                                request.META.get('HTTP_X_FORWARDED_FOR')
                            )
                        else:
                            description = agent.user.username + \
                                " (" + agent.role + ") was marked as present"

                            add_audit_trail(
                                "EASYTMSAPP",
                                active_agent.user,
                                "User-Presence-Status",
                                description,
                                json.dumps(data),
                                request.META.get("PATH_INFO"),
                                request.META.get('HTTP_X_FORWARDED_FOR')
                            )

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ChangeAgentAbsentStatusAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ChangeAgentAbsentStatus = ChangeAgentAbsentStatusAPI.as_view()


class ResendAccountPasswordAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            user_pk = data["user_pk"]
            platform_url = data["platform_url"]

            active_agent = get_active_agent_obj(request, User, Agent)

            try:
                agent = Agent.objects.get(pk=int(user_pk))
                update_resend_password_counter(agent)

                if agent.resend_password_count >= 0:
                    user = agent.user

                    password = generate_password("TMS")

                    thread = threading.Thread(target=send_password_over_email, args=(
                        user.email, user.first_name, password, platform_url, ), daemon=True)
                    thread.start()

                    user.set_password(password)
                    user.save()

                    agent.user = user
                    agent.save()

                    message = "New password sent to " + str(agent.user.email)
                    response["message"] = message

                    description = message
                    add_audit_trail(
                        "EASYTMSAPP",
                        active_agent.user,
                        "Password-Resent",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )
                else:
                    response["message"] = str(agent.user.email) + \
                        " has reached daily resend password limit"

                response["status"] = 200
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error ResendAccountPasswordAPI %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
                response["status"] = 300
                response["message"] = "Could not send the password"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ResendAccountPasswordAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ResendAccountPassword = ResendAccountPasswordAPI.as_view()


"""

FetchUserNotificationCountAPI() : return count of unchecked notification of active user

"""


class FetchUserNotificationCountAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = get_active_agent_obj(request, User, Agent)
            user_notification_objs = UserNotification.objects.filter(agent=active_agent, is_checked=False)
            count = user_notification_objs.count()

            cognodesk_title = get_developer_console_cognodesk_settings().title_text

            response["status"] = 200
            response["message"] = "success"
            response["count"] = count
            response["cognodesk_title"] = cognodesk_title
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FetchUserNotificationCountAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


FetchUserNotificationCount = FetchUserNotificationCountAPI.as_view()


"""

FetchUserNotificationAPI() : return all active ticket objs

"""


class FetchUserNotificationAPI(APIView):

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
            is_checked = data["is_checked"]

            datetime_limit = data["datetime_limit"]

            try:
                date_format = "%d %b %Y %I:%M:%S %p"
                datetime_limit = datetime.strptime(datetime_limit, date_format)
            except Exception:
                datetime_limit = (datetime.now() + timedelta(seconds=1)).replace(microsecond=0)

            active_agent = get_active_agent_obj(request, User, Agent)

            user_notification_objs = UserNotification.objects.filter(agent=active_agent, is_checked=is_checked, datetime__lte=datetime_limit)
            user_notification_objs = user_notification_objs.values('ticket__ticket_id').annotate(m=Max('datetime')).order_by('-m')

            total_rows_per_pages = 4
            total_user_notification_objs = user_notification_objs.count()

            paginator = Paginator(
                user_notification_objs, total_rows_per_pages)

            try:
                user_notification_objs = paginator.page(page)
            except PageNotAnInteger:
                user_notification_objs = paginator.page(1)
            except EmptyPage:
                user_notification_objs = paginator.page(paginator.num_pages)

            if page != None:
                start_point = total_rows_per_pages * (int(page) - 1) + 1
                end_point = min(total_rows_per_pages *
                                int(page), total_user_notification_objs)
                if start_point > end_point:
                    start_point = max(end_point - len(user_notification_objs) + 1, 1)
            else:
                start_point = 1
                end_point = min(total_rows_per_pages, total_user_notification_objs)

            pagination_range = user_notification_objs.paginator.page_range

            has_next = user_notification_objs.has_next()
            has_previous = user_notification_objs.has_previous()

            next_page_number = -1
            previous_page_number = -1

            if has_next:
                next_page_number = user_notification_objs.next_page_number()
            if has_previous:
                previous_page_number = user_notification_objs.previous_page_number()

            pagination_metadata = {
                'total_count': total_user_notification_objs,
                'start_point': start_point,
                'end_point': end_point,
                'page_range': [pagination_range.start, pagination_range.stop],
                'has_next': has_next,
                'has_previous': has_previous,
                'next_page_number': next_page_number,
                'previous_page_number': previous_page_number,
                'number': user_notification_objs.number,
                'num_pages': user_notification_objs.paginator.num_pages
            }

            notification_list = []

            for user_notification_obj in user_notification_objs:
                target_objs = UserNotification.objects.filter(agent=active_agent, is_checked=is_checked, ticket__ticket_id=user_notification_obj["ticket__ticket_id"]).order_by('-datetime')
                for target_obj in target_objs:
                    notification_list.append(parse_user_notification(target_obj))

            response["status"] = 200
            response["message"] = "success"
            response["notification_list"] = notification_list
            response["pagination_metadata"] = pagination_metadata
            response["datetime_limit"] = get_formatted_date(datetime_limit)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FetchUserNotificationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


FetchUserNotification = FetchUserNotificationAPI.as_view()


"""

ClearUserNotificationAPI() : expexted pk list of notifications

"""


class ClearUserNotificationAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            notifiction_pk_list = data["notifiction_pk_list"]

            user_notification_objs = UserNotification.objects.filter(pk__in=notifiction_pk_list)

            user_notification_objs.update(is_checked=True)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ClearUserNotificationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ClearUserNotification = ClearUserNotificationAPI.as_view()


def DownloadCRMDocuments(request, document_type):
    try:
        if request.user.is_authenticated:

            active_agent = get_active_agent_obj(request, User, Agent)
            access_token = get_access_token_obj(active_agent, Agent, TMSAccessToken)

            original_file_name = CRM_DOCUMENTS[document_type]["original_file_name"]
            display_file_name = CRM_DOCUMENTS[document_type]["display_file_name"]

            path_to_file = "secured_files/EasyTMSApp/CRMDocuments/" + str(access_token.key) + "/" + original_file_name

            if not path.exists(path_to_file):
                generate_crm_api_document(access_token)

            generate_crm_api_document(access_token)

            if path.exists(path_to_file):
                with open(path_to_file, 'rb') as fh:
                    response = HttpResponse(
                        fh.read(), status=200, content_type="docs")
                    response['Content-Disposition'] = 'attachment; filename="%s"' % smart_str(
                        str(display_file_name))
                    return response
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse(status=404)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error DownloadCRMDocuments %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
    return HttpResponse(status=404)


class CRMGenerateAuthTokenAPI(APIView):

    authentication_classes = [BasicAuthentication]

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            username = request.user.username
            active_agent = Agent.objects.get(user__username=username)
            access_token = get_access_token_obj(active_agent, Agent, TMSAccessToken)

            crm_integration_model = CRMIntegrationModel.objects.create(access_token=access_token)

            response["Head"]['ResponseCode'] = 200
            response["Head"]['Description'] = 'success'
            response["Body"]['auth_token'] = str(crm_integration_model.auth_token)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMGenerateAuthTokenAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        return Response(data=response)


CRMGenerateAuthToken = CRMGenerateAuthTokenAPI.as_view()


class CRMGenerateTicketAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            access_token = crm_integration_model.access_token
            request_data = request.data

            is_all_data_available = True
            required_inputs = ["customer_name", "issue_description"]

            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            processed_data = process_request_data(request_data, access_token)
            ticket_id = create_ticket_from_processed_data(processed_data)

            response["Head"]["ResponseCode"] = 200
            response["Head"]["Description"] = "Success"
            response["Body"]["TicketId"] = ticket_id

            try:
                ticket_obj = Ticket.objects.get(ticket_id=ticket_id)
                agent_objs = get_relevant_agent_list(ticket_obj, Agent)
                selected_agent_obj = ticket_obj.agent

                description = "A new ticket is generated and assigned to " + selected_agent_obj.user.username

                for agent_obj in agent_objs:

                    if agent_obj != selected_agent_obj:
                        create_user_notification(
                            agent_obj, ticket_obj, description, UserNotification)
                        send_action_info_to_agent(agent_obj, action_name="new_ticket_assigned", action_info={
                            "send_notification": True,
                            "notification_message": description,
                            "ticket_id": ticket_obj.ticket_id
                        })
                    elif agent_obj == selected_agent_obj:
                        create_user_notification(
                            agent_obj, ticket_obj, description, UserNotification)
                        notification_message = "Hi, " + agent_obj.user.username + "! A new ticket is assigned to you on Cogno desk."
                        send_action_info_to_agent(agent_obj, action_name="new_ticket_assigned", action_info={
                            "send_notification": True,
                            "notification_message": notification_message,
                            "ticket_id": ticket_obj.ticket_id
                        })
            except Exception:
                pass

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMGenerateTicketAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        return Response(data=response)


CRMGenerateTicket = CRMGenerateTicketAPI.as_view()


class CRMGetTicketInfoAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            access_token = crm_integration_model.access_token
            request_data = request.data

            is_all_data_available = True
            required_inputs = ["ticket_id"]

            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            ticket_id = request_data["ticket_id"]

            ticket_obj = None
            try:
                ticket_obj = Ticket.objects.get(ticket_id=ticket_id, access_token=access_token)
            except Exception:
                pass

            if ticket_obj == None:
                response["Head"]['ResponseCode'] = 304
                response["Head"]['Description'] = 'The requested ticket does not exist'
                return Response(data=response)

            ticket_info = get_ticket_data(ticket_obj)

            response["Head"]["ResponseCode"] = 200
            response["Head"]["Description"] = "Success"
            response["Body"]["Data"] = ticket_info
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMGetTicketInfoAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        return Response(data=response)


CRMGetTicketInfo = CRMGetTicketInfoAPI.as_view()


class CRMGetTicketActivityAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {
            "Head": {
                "ResponseCode": 500,
                "Description": "Internal Server Error"
            },
            "Body": {}
        }
        try:
            crm_integration_model = get_crm_integration_model(request, CRMIntegrationModel)

            if crm_integration_model is None:
                response["Head"]["ResponseCode"] = 401
                response["Head"]['Description'] = 'Unauthorized'
                return Response(data=response)

            access_token = crm_integration_model.access_token
            request_data = request.data

            is_all_data_available = True
            required_inputs = ["ticket_id"]

            for required_input in required_inputs:
                if not (required_input in request_data):
                    is_all_data_available = False

            if is_all_data_available == False:
                response["Head"]['ResponseCode'] = 301
                response["Head"]['Description'] = 'No Content'
                return Response(data=response)

            ticket_id = request_data["ticket_id"]
            ticket_obj = None

            try:
                ticket_obj = Ticket.objects.get(ticket_id=ticket_id, access_token=access_token)
            except Exception:
                pass

            if ticket_obj == None:
                response["Head"]['ResponseCode'] = 304
                response["Head"]['Description'] = 'The requested ticket does not exist'
                return Response(data=response)

            audit_trail_objs = TicketAuditTrail.objects.filter(ticket=ticket_obj)
            audit_trail_objs = audit_trail_objs.order_by('datetime')
            ticket_activity = []
            for audit_trail_obj in audit_trail_objs:
                ticket_activity.append(get_ticket_activity_data(audit_trail_obj))

            response["Head"]["ResponseCode"] = 200
            response["Head"]["Description"] = "Success"
            response["Body"]["Data"] = ticket_activity
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CRMGetTicketActivityAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        return Response(data=response)


CRMGetTicketActivity = CRMGetTicketActivityAPI.as_view()


def fileAccess(request, file_key):
    try:
        if request.user.is_authenticated:
            return file_download(file_key, FileAccessManagement)
        return HttpResponse(status=404)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error fileAccess %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
    return HttpResponse(status=404)


class DownloadUserDetailsTemplateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {'status': 500}
        custom_encrypt_obj = CustomEncrypt()
        try:
            export_path = "files/templates/tms-user-create-template/User_Details_Template.xlsx"
            response["export_path"] = export_path
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DownloadUserDetailsTemplateAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


DownloadUserDetailsTemplate = DownloadUserDetailsTemplateAPI.as_view()


class UploadUserDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, User, Agent)

            if active_agent.role == "admin":

                filename = strip_html_tags(data["filename"])
                filename = remo_html_from_string(filename)
                base64_data = strip_html_tags(data["base64_file"])

                filename = generate_random_key(
                    10) + "_" + filename.replace(" ", "")

                file_path = "files/" + filename

                file_extension = file_path.split(".")[-1]
                file_extension = file_extension.lower()

                allowed_files_list = ["xls", "xlsx",
                                      "xlsm", "xlt", "xltm", "xlb"]
                if file_extension in allowed_files_list:
                    media_type = "excel"
                else:
                    media_type = None

                if media_type is None or check_malicious_file_from_filename(filename, allowed_files_list) or check_malicious_file_from_content(base64_data, allowed_files_list + ["a"]):
                    response["status"] = 300
                else:
                    fh = open(file_path, "wb")
                    fh.write(base64.b64decode(base64_data))
                    fh.close()

                    response_data = add_users_from_excel_document(file_path, active_agent)

                    if response_data["status"] == 200:
                        response["status"] = 200
                        response["message"] = response_data["message"]
                    elif response_data["status"] == 301:
                        response["status"] = 301
                        response["message"] = response_data["message"]
                    elif response_data["status"] == 302:
                        response["status"] = 302
                        response["message"] = response_data["message"]
                        response["file_path"] = response_data["file_path"]

                description = "New users has been added using excel file"

                add_audit_trail(
                    "EASYTMSAPP",
                    active_agent.user,
                    "Add-User",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadUserDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadUserDetails = UploadUserDetailsAPI.as_view()


class ExportUserDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {'status': 500}
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = get_active_agent_obj(request, User, Agent)
            export_path = create_excel_user_details(active_agent, Agent)

            if export_path is not None:
                file_path = "/" + export_path
                file_access_management_obj = FileAccessManagement.objects.create(
                    file_path=file_path)
                export_path = "tms/download-file/" + \
                              str(file_access_management_obj.key) + "/"

            response["export_path"] = export_path
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportUserDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportUserDetails = ExportUserDetailsAPI.as_view()


class ExportSupervisorDetailsAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {'status': 500}
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = get_active_agent_obj(request, User, Agent)
            export_path = create_excel_supervisor_details(active_agent)

            if export_path is not None:
                file_path = "/" + export_path
                file_access_management_obj = FileAccessManagement.objects.create(
                    file_path=file_path)
                export_path = "tms/download-file/" + \
                    str(file_access_management_obj.key) + "/"

            response["export_path"] = export_path
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportSupervisorDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportSupervisorDetails = ExportSupervisorDetailsAPI.as_view()


class SaveWhatsappApiProcessorCodeAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            active_agent = get_active_agent_obj(request, User, Agent)

            access_token_key = data["access_token_key"]
            process_id = data["process_id"]
            processor_code = data["processor_code"]

            try:
                assign_task_process = WhatsappApiProcessor.objects.get(
                    pk=process_id)
                access_token_obj = TMSAccessToken.objects.get(
                    key=access_token_key)

                if assign_task_process.access_token == access_token_obj:
                    WhatsappApiProcessorLogger.objects.create(
                        agent=active_agent,
                        function=processor_code,
                        assign_task_process=assign_task_process
                    )
                    assign_task_process.function = processor_code
                    assign_task_process.save()
                    response["status"] = 200
                else:
                    response["status"] = 401
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error SaveWhatsappApiProcessorCodeAPI %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
                response["status"] = 301

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveWhatsappApiProcessorCodeAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveWhatsappApiProcessorCode = SaveWhatsappApiProcessorCodeAPI.as_view()
