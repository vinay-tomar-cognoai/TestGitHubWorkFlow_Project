from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
"""For user authentication"""
from django.contrib.auth import authenticate, login, logout
# Create your views here.
from EasyChatApp.models import User
from EasyAssistApp.models import *
from EasyAssistApp.utils import *

import sys
import json
import base64
import operator
import logging
import requests
import urllib.parse

from operator import itemgetter

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def EasyAssistDemo(request):
    return render(request, "EasyAssistApp/demo.html", {})


def EasyAssistHomePage(request):
    return redirect("/easy-assist/sales-ai/login/")


def ICICIBankDemo(request):
    return render(request, "EasyAssistApp/icicibank.html", {})


def SBIMFDemo(request):
    return render(request, "EasyAssistApp/sbimf.html", {})


def WesternGeneralInsurance(request):
    return render(request, "EasyAssistApp/westen_general_insurance.html", {})


def CamsDemo(request):
    return render(request, "EasyAssistApp/cams.html", {})


@require_http_methods(["GET"])
def EasyAssistDashboard(request):

    if not request.user.is_authenticated:
        return redirect("/easy-assist/sales-ai/login")

    agent_obj = Agent.objects.get(username=request.user.username)

    client_screencast_objs = []
    filter_parameter = "unresolved"
    if "filter" in request.GET and request.GET["filter"] == "resolved":
        client_screencast_objs = get_list_of_resolved_screencast(
            ScreenCast, agent_obj)
        filter_parameter = "resolved"
    else:
        client_screencast_objs = get_list_of_unresolved_screencast(
            ScreenCast, agent_obj)

    return render(request, "EasyAssistApp/dashboard.html", {
        "filter_parameter": filter_parameter,
        "client_screencast_objs": client_screencast_objs
    })


@csrf_exempt
@require_http_methods(["POST"])
def ConnectToAgent(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = request.POST["data"]
        plain_data = base64.b64decode(data).decode("utf-8", errors='ignore')
        data = json.loads(plain_data)

        client_name = data["client_name"]
        client_mobile_number = data["client_mobile_number"]
        active_website_url = data["active_website_url"]
        html_input_elements = data["html_input_elements"]
        html_textarea_elements = data["html_textarea_elements"]
        html_select_elements = data["html_select_elements"]
        session_id = data["session_id"]
        currently_focused_element = data["currently_focused_element"]
        total_time_spent = data["total_time_spent"]
        agent_username = data["agent_username"]

        input_html_elements = json.dumps({
            "html_input_elements": html_input_elements,
            "html_textarea_elements": html_textarea_elements,
            "html_select_elements": html_select_elements
        })

        agent_obj = None
        try:
            agent_obj = Agent.objects.get(username=agent_username)
        except Exception:
            logger.info("No agent selected. Autoassign task to agent.", extra={
                        'AppName': 'EasyAssist'})
            try:
                agent_dict = {}
                for agent in Agent.objects.all():
                    agent_dict[agent.username] = 0

                screen_cast_list = ScreenCast.objects.filter(~Q(agent=None)).values(
                    'agent__username').annotate(total=Count('agent')).order_by('total')
                for screen_cast in screen_cast_list:
                    agent_dict[screen_cast["agent__username"]
                               ] = screen_cast["total"]

                agent_username = max(agent_dict.items(),
                                     key=operator.itemgetter(1))[0]
                agent_obj = Agent.objects.get(username=agent_username)
            except Exception:
                agent_objs = Agent.objects.all()
                if agent_objs.count() > 0:
                    agent_obj = agent_objs[0]

        if session_id == None:
            screen_cast_obj = ScreenCast.objects.create(input_html_elements=input_html_elements,
                                                        client_name=client_name,
                                                        client_mobile_number=client_mobile_number,
                                                        website_url=active_website_url,
                                                        status="unresolved",
                                                        state=currently_focused_element)
            session_id = str(screen_cast_obj.session_id)
            screen_cast_obj.last_update_datetime = timezone.now()
            screen_cast_obj.total_time_spent = str(total_time_spent)
            screen_cast_obj.agent = agent_obj
            screen_cast_obj.is_agent_access_allowed = True
            screen_cast_obj.save()
        else:
            screen_cast_objs = ScreenCast.objects.filter(session_id=session_id)
            if len(screen_cast_objs) > 0:
                screen_cast_obj = screen_cast_objs[0]
                screen_cast_obj.input_html_elements = input_html_elements
                screen_cast_obj.last_update_datetime = timezone.now()
                screen_cast_obj.total_time_spent = str(total_time_spent)
                screen_cast_obj.agent = agent_obj
                screen_cast_obj.website_url = active_website_url
                screen_cast_obj.is_agent_access_allowed = True
                screen_cast_obj.state = currently_focused_element
                screen_cast_obj.save()

        response["status"] = 200
        response["message"] = "success"
        response["session_id"] = session_id
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ConnectToAgent %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


@csrf_exempt
@require_http_methods(["POST"])
def SyncAgentScreen(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = json.loads(request.POST["data"])
        session_id = data["session_id"]

        screen_cast_obj = None
        try:
            screen_cast_obj = ScreenCast.objects.get(session_id=session_id)
        except Exception:
            pass

        if screen_cast_obj == None:
            response["status"] = 101
            response["message"] = NO_MATCHING_SESSION_FOUND_MSG
        else:
            if screen_cast_obj.is_connection_closed:
                response["status"] = 101
                response["message"] = "Customer has left the page."
            else:
                response["status"] = 200
                response["message"] = "success"
                input_html_elements = perform_masking(screen_cast_obj, Field)

                if input_html_elements == None:
                    input_html_elements = json.loads(
                        screen_cast_obj.input_html_elements)

                html_textarea_elements = []
                for key in input_html_elements["html_textarea_elements"]:
                    temp_dict = input_html_elements[
                        "html_textarea_elements"][key]
                    temp_dict["md5_string"] = key
                    html_textarea_elements.append(temp_dict)

                html_input_elements = []
                for key in input_html_elements["html_input_elements"]:
                    temp_dict = input_html_elements["html_input_elements"][key]
                    temp_dict["md5_string"] = key
                    html_input_elements.append(temp_dict)

                html_select_elements = []
                for key in input_html_elements["html_select_elements"]:
                    temp_dict = input_html_elements[
                        "html_select_elements"][key]
                    temp_dict["md5_string"] = key
                    html_select_elements.append(temp_dict)

                html_input_elements = sorted(
                    html_input_elements, key=itemgetter('index'))
                html_select_elements = sorted(
                    html_select_elements, key=itemgetter('index'))
                html_textarea_elements = sorted(
                    html_textarea_elements, key=itemgetter('index'))

                input_html_elements = {
                    "html_textarea_elements": html_textarea_elements,
                    "html_input_elements": html_input_elements,
                    "html_select_elements": html_select_elements
                }

                response["html_elements"] = input_html_elements

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SyncAgentScreen %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


@csrf_exempt
@require_http_methods(["POST"])
def ClientDisconnected(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = json.loads(request.POST["data"])
        session_id = data["session_id"]

        screen_cast_obj = None
        try:
            screen_cast_obj = ScreenCast.objects.get(session_id=session_id)
        except Exception:
            pass

        if screen_cast_obj == None:
            response["status"] = 101
            response["message"] = NO_MATCHING_SESSION_FOUND_MSG
        else:
            screen_cast_obj.is_connection_closed = True
            screen_cast_obj.last_update_datetime = timezone.now()
            screen_cast_obj.save()
            response["status"] = 200
            response["message"] = "success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ClientDisconnected %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


@csrf_exempt
@require_http_methods(["POST"])
def ActivateHighlightElement(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = json.loads(request.POST["data"])
        session_id = data["session_id"]
        highlight_element_details = {
            "html_element_tag": data["html_element_tag"],
            "md5hash_str": data["md5hash_str"]
        }

        screen_cast_obj = None
        try:
            screen_cast_obj = ScreenCast.objects.get(session_id=session_id)
        except Exception:
            pass

        if screen_cast_obj == None:
            response["status"] = 101
            response["message"] = NO_MATCHING_SESSION_FOUND_MSG
        else:
            screen_cast_obj.highlight_text = json.dumps(
                highlight_element_details)
            screen_cast_obj.save()
            response["status"] = 200
            response["message"] = "success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ActivateHighlightElement %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


@csrf_exempt
@require_http_methods(["POST"])
def DeactivateHighlightElement(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = json.loads(request.POST["data"])
        session_id = data["session_id"]

        screen_cast_obj = None
        try:
            screen_cast_obj = ScreenCast.objects.get(session_id=session_id)
        except Exception:
            pass

        if screen_cast_obj == None:
            response["status"] = 101
            response["message"] = NO_MATCHING_SESSION_FOUND_MSG
        else:
            screen_cast_obj.highlight_text = None
            screen_cast_obj.save()
            response["status"] = 200
            response["message"] = "success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error DeactivateHighlightElement %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


@csrf_exempt
@require_http_methods(["POST"])
def CheckHighlightedElement(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = json.loads(request.POST["data"])
        session_id = data["session_id"]

        screen_cast_obj = None
        try:
            screen_cast_obj = ScreenCast.objects.get(session_id=session_id)
        except Exception:
            pass

        if screen_cast_obj == None:
            response["status"] = 101
            response["message"] = NO_MATCHING_SESSION_FOUND_MSG
        else:
            response["status"] = 200
            response["highlight_text"] = None
            if screen_cast_obj.highlight_text != None:
                response["highlight_text"] = json.loads(
                    screen_cast_obj.highlight_text)
            response["message"] = "success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CheckHighlightedElement %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


@csrf_exempt
@require_http_methods(["POST"])
def CheckFormSubmit(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = json.loads(request.POST["data"])
        session_id = data["session_id"]
        button_md5 = data["button_md5"]

        screen_cast_obj = None
        try:
            screen_cast_obj = ScreenCast.objects.get(session_id=session_id)
        except Exception:
            pass

        if screen_cast_obj == None:
            response["status"] = 101
            response["message"] = NO_MATCHING_SESSION_FOUND_MSG
        else:
            website_url = screen_cast_obj.website_url
            field_obj = None
            try:
                field_obj = Field.objects.get(
                    form__url=website_url, field_id=button_md5)
            except Exception:
                pass

            if field_obj:
                screen_cast_obj.status = "resolved"
                screen_cast_obj.save()

            response["status"] = 200
            response["message"] = "success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CheckFormSubmit %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


def SettingsPage(request):
    if not request.user.is_authenticated:
        return redirect("/easy-assist/login")

    agent_obj = Agent.objects.get(username=request.user.username)
    return render(request, "EasyAssistApp/settings.html", {
        "agent_obj": agent_obj
    })


def ManageForms(request):
    if not request.user.is_authenticated:
        return redirect("/easy-assist/login")

    agent_obj = Agent.objects.get(username=request.user.username)

    if agent_obj.role != "supervisor":
        return HttpResponse("Unauthorized Access")

    forms = Form.objects.filter(agent=agent_obj)

    return render(request, "EasyAssistApp/manage-forms.html", {
        "agent_obj": agent_obj,
        "forms": forms
    })


def ManageFields(request):
    if not request.user.is_authenticated:
        return redirect("/easy-assist/login")

    agent_obj = Agent.objects.get(username=request.user.username)

    if agent_obj.role != "supervisor":
        return HttpResponse("Unauthorized Access")

    forms = Form.objects.filter(agent=agent_obj)

    fields = []
    selected_form = None
    if "form" in request.GET:
        try:
            selected_form = Form.objects.get(pk=int(request.GET["form"]))
            fields = Field.objects.filter(form=selected_form)
        except Exception:
            pass

    return render(request, "EasyAssistApp/manage-fields.html", {
        "agent_obj": agent_obj,
        "forms": forms,
        "selected_form": selected_form,
        "fields": fields
    })


def AgentAssistance(request):
    if not request.user.is_authenticated:
        return redirect("/easy-assist/login")

    try:
        screen_cast_objs = ScreenCast.objects.filter(
            session_id=request.GET["session_id"])

        if len(screen_cast_objs) == 0:
            return HttpResponse(INVALID_ACCESS_CONSTANT)
        form_obj = None
        try:
            website_url = screen_cast_objs[0].website_url
            form_obj = Form.objects.filter(url=website_url)[0]
        except Exception:
            pass

        return render(request, "EasyAssistApp/agent-page.html", {
            "screen_cast_obj": screen_cast_objs[0],
            "form_obj": form_obj
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error AgentAssistance %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def MarkAsResolved(request, screen_pk):
    if not request.user.is_authenticated:
        return redirect("/easy-assist/login")

    try:
        screen_cast_obj = ScreenCast.objects.get(pk=screen_pk)
        screen_cast_obj.status = "resolved"
        screen_cast_obj.save()
        return redirect("/easy-assist/dashboard/?filter=unresolved")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error MarkAsResolved %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def AgentAssistRequest(request, screen_pk):
    if not request.user.is_authenticated:
        return redirect("/easy-assist/login")

    try:
        agent_obj = Agent.objects.get(username=request.user.username)
        screen_cast_obj = ScreenCast.objects.get(pk=screen_pk)
        screen_cast_obj.request_form_assist = True
        screen_cast_obj.is_agent_access_allowed = False
        screen_cast_obj.agent = agent_obj
        screen_cast_obj.save()
        return redirect("/easy-assist/dashboard/?filter=unresolved")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error AgentAssistRequest %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


@csrf_exempt
@require_http_methods(["POST"])
def CheckAgentAssistanceRequest(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = json.loads(request.POST["data"])
        session_id = data["session_id"]
        screen_cast_obj = None
        try:
            screen_cast_obj = ScreenCast.objects.get(session_id=session_id)
        except Exception:
            pass

        if screen_cast_obj == None:
            response["status"] = 101
            response["message"] = NO_MATCHING_SESSION_FOUND_MSG
        else:
            response["agent_requested"] = screen_cast_obj.request_form_assist
            response["client_name"] = screen_cast_obj.client_name
            response["client_mobile_number"] = screen_cast_obj.client_mobile_number
            response["agent"] = None
            if screen_cast_obj.agent != None:
                response["agent"] = screen_cast_obj.agent.username
            response["status"] = 200
            response["message"] = "success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CheckAgentAssistanceRequest %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


@csrf_exempt
@require_http_methods(["POST"])
def CancelAgentAssistanceRequest(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = json.loads(request.POST["data"])
        session_id = data["session_id"]
        screen_cast_obj = None
        try:
            screen_cast_obj = ScreenCast.objects.get(session_id=session_id)
        except Exception:
            pass

        if screen_cast_obj == None:
            response["status"] = 101
            response["message"] = NO_MATCHING_SESSION_FOUND_MSG
        else:
            screen_cast_obj.request_form_assist = False
            screen_cast_obj.save()
            response["status"] = 200
            response["message"] = "success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CancelAgentAssistanceRequest %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


@csrf_exempt
@require_http_methods(["POST"])
def AutoSessionInit(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = json.loads(request.POST["data"])
        session_id = data["session_id"]
        mobile_number = data["mobile_number"]
        website_url = data["website_url"]

        screen_cast_obj = None
        try:
            screen_cast_obj = ScreenCast.objects.get(session_id=session_id)
        except Exception:
            pass

        if screen_cast_obj == None:
            screen_cast_obj = ScreenCast.objects.create(website_url=website_url,
                                                        status="unresolved",
                                                        client_mobile_number=mobile_number)
            screen_cast_obj.last_update_datetime = timezone.now()
            screen_cast_obj.save()
        else:
            screen_cast_obj.client_mobile_number = mobile_number
            screen_cast_obj.last_update_datetime = timezone.now()
            screen_cast_obj.save()

        response["status"] = 200
        response["message"] = "success"
        response["session_id"] = str(screen_cast_obj.pk)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error AutoSessionInit %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


@csrf_exempt
@require_http_methods(["POST"])
def GetFormInformation(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = request.POST["data"]
        plain_data = base64.b64decode(data).decode("utf-8")
        data = json.loads(plain_data)
        form_url = data["form_url"]
        form_obj = Form.objects.get(url=form_url)
        response["status"] = 200
        response["message"] = "success"
        response["confirm_message"] = form_obj.confirm_message
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ClientDisconnected %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


@csrf_exempt
@require_http_methods(["POST"])
def CreateAgentAssistanceRequest(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = request.GET
        name = data["name"]
        mobile_number = data["mobile_number"]
        website_url = data["website_url"]
        screen_cast_obj = ScreenCast.objects.create(
            client_name=name, client_mobile_number=mobile_number, website_url=website_url, status="unresolved")
        cobrowse_obj = CobrowseIO.objects.create(full_name=name,
                                                 mobile_number=mobile_number,
                                                 meta_data=json.dumps({"product_details": {"title": "General Insurance", "url": "https://easyassist.allincall.in/easy-assist/general-insurance/", "description": "Protect your loved ones with affordable Term Life Insurance. Choose from term durations that best meets your needs and budget."}}), is_active=True)
        cobrowse_obj.last_update_datetime = timezone.now()
        cobrowse_obj.save()
        screen_cast_obj.last_update_datetime = timezone.now()
        screen_cast_obj.save()
        response["status"] = 200
        response["message"] = "success"
        response["session_id"] = str(cobrowse_obj.session_id)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ClientDisconnected %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


@csrf_exempt
@require_http_methods(["POST"])
def CreateNewFormRequest(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = json.loads(request.POST["data"])
        form_name = data["form_name"]
        confirm_message = data["form_confirm_message"]
        website_url = data["website_url"]

        form_obj = None
        try:
            form_obj = Form.objects.get(url=website_url)
            form_obj.confirm_message = confirm_message
            form_obj.name = form_name
            form_obj.save()
        except Exception:
            form_obj = Form.objects.create(
                url=website_url, confirm_message=confirm_message, name=form_name)

        response["status"] = 200
        response["message"] = "success"
        response["form_id"] = form_obj.pk
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CreateNewFormRequest %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


@csrf_exempt
@require_http_methods(["POST"])
def CreateNewFieldRequest(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = json.loads(request.POST["data"])
        md5_string = data["md5_string"]
        form_id = data["active_form_id"]
        field_name = data["field_name"]
        is_masked = data["is_masked"]
        group_number = int(data["group_number"])

        form_obj = Form.objects.get(pk=int(form_id))

        field_obj = None
        try:
            field_obj = Field.objects.get(field_id=md5_string, form=form_obj)
            field_obj.name = field_name
            field_obj.is_masked = is_masked
            field_obj.group_order = group_number
            field_obj.save()
        except Exception:
            field_obj = Field.objects.create(
                field_id=md5_string, form=form_obj, name=field_name, is_masked=is_masked, group_order=group_number)

        response["status"] = 200
        response["message"] = "success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CreateNewFormRequest %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE, extra={'AppName': 'EasyAssist'})


def AgentAssistanceV2(request):
    if not request.user.is_authenticated:
        return redirect("/easy-assist/login")

    try:
        screen_cast_objs = ScreenCast.objects.filter(
            session_id=request.GET["session_id"])

        if len(screen_cast_objs) == 0:
            return HttpResponse(INVALID_ACCESS_CONSTANT)

        return render(request, "EasyAssistApp/agent-page-2.html", {
            "screen_cast_obj": screen_cast_objs[0]
        })
    except Exception:
        return HttpResponse(INVALID_ACCESS_CONSTANT)


@csrf_exempt
@require_http_methods(["POST"])
def SyncAgentScreenV2(request):
    response = {}
    response["status"] = 500
    response["message"] = INTERNAL_SERVER_ERROR_MSG_2
    try:
        data = json.loads(request.POST["data"])
        session_id = data["session_id"]

        screen_cast_obj = None
        try:
            screen_cast_obj = ScreenCast.objects.get(session_id=session_id)
        except Exception:
            pass

        if screen_cast_obj == None:
            response["status"] = 101
            response["message"] = NO_MATCHING_SESSION_FOUND_MSG
        else:
            if screen_cast_obj.is_connection_closed:
                response["status"] = 101
                response["message"] = "Customer has left the page."
            else:
                currently_focused_field = screen_cast_obj.state

                field_obj = None
                try:
                    field_obj = Field.objects.get(
                        field_id=currently_focused_field)
                except Exception:
                    pass

                if field_obj != None:

                    same_group_field_objs = Field.objects.filter(
                        form=field_obj.form, group_order=field_obj.group_order)
                    html_content_list = []

                    input_html_elements = json.loads(
                        screen_cast_obj.input_html_elements)
                    for group_field_obj in same_group_field_objs:

                        if group_field_obj.field_id in input_html_elements["html_input_elements"]:
                            input_element = input_html_elements[
                                "html_input_elements"][group_field_obj.field_id]
                            input_element["html_tag"] = "input"
                            html_content_list.append(input_element)
                        elif group_field_obj.field_id in input_html_elements["html_select_elements"]:
                            input_element = input_html_elements[
                                "html_select_elements"][group_field_obj.field_id]
                            input_element["html_tag"] = "select"
                            html_content_list.append(input_element)
                        elif group_field_obj.field_id in input_html_elements["html_textarea_elements"]:
                            input_element = input_html_elements[
                                "html_textarea_elements"][group_field_obj.field_id]
                            input_element["html_tag"] = "textarea"
                            html_content_list.append(input_element)

                    response["status"] = 200
                    response["message"] = "success"
                    response["html_content_list"] = html_content_list
                else:
                    response["status"] = 101
                    response["message"] = ""
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SyncAgentScreenV2 %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    return HttpResponse(json.dumps(response), content_type=APPLICATION_JSON_CONTENT_TYPE)


def ProxyPass(request, address):
    try:
        if len(request.GET) > 0:
            address += "?"
            address_params = []
            for param in request.GET:
                address_params.append(str(param) + "=" + request.GET[param])
            address += "&".join(address_params)

        request_response = requests.get(url=address, timeout=10)
        content_type = request_response.headers.get('content-type')

        if content_type == "text/css":
            content = convert_relative_path_to_absolute(
                request_response.text, address)
        else:
            content = request_response.text

        if content != None:
            http_response = HttpResponse(
                status=request_response.status_code, content=content, content_type=content_type)
            accept_headers = ["x-content-type-options",
                              "vary", "accept-ranges"]
            for request_response_header in request_response.headers:
                if request_response_header.lower() in accept_headers:
                    http_response[request_response_header] = request_response.headers.get(
                        request_response_header)
            return http_response
        else:
            return HttpResponse(status=404)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ProxyPass %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return HttpResponse(status=404)
