from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

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
"""For user authentication"""
from django.contrib.auth import authenticate, login, logout

from EasyAssistSalesforceApp.models import *
from EasyAssistSalesforceApp.utils import *

from urllib.parse import quote_plus, unquote


# @csrf_exempt
def SalesAILoginPage(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)

        salesforce_token = authenticate_salesforce_user(request, SalesforceAgent, User, CobrowseAgent)
        if salesforce_token == None:
            return HttpResponse(status=401)
        # return HttpResponse(salesforce_token)
        logger.info("salesforce_token: " + salesforce_token, extra={'AppName': 'EasyAssistSalesforce'})

        return redirect("/easy-assist-salesforce/sales-ai/dashboard/?salesforce_token="+salesforce_token)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAILoginPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse("Invalid Access")


# @csrf_exempt
def SalesAIDashboard(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        user = get_authenticated_user(request, User)
        if user == None:
            return HttpResponse(status=401)
        # return HttpResponse("user: " + user.username)
        
        # user = User.objects.get(username=request.user.username)
        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        access_token_obj = cobrowse_agent.get_access_token_obj()

        agents = []
        if cobrowse_agent.role == "agent":
            agents = [cobrowse_agent]
        elif cobrowse_agent.role == "supervisor":
            agents = list(cobrowse_agent.agents.all())
        else:
            agents = get_list_agents_under_admin(
                cobrowse_agent, is_active=None)

        cobrowse_io_objs = CobrowseIO.objects.filter(
            is_archived=False, agent__in=agents)
        cobrowse_io_support_objs = CobrowseIO.objects.filter(
            is_archived=False, support_agents__in=agents)
        cobrowse_io_objs = cobrowse_io_objs | cobrowse_io_support_objs
        cobrowse_io_objs = cobrowse_io_objs.order_by("-request_datetime")
        access_token_obj = cobrowse_agent.get_access_token_obj()

        agent_admin = access_token_obj.agent
        agents_list = get_list_agents_under_admin(agent_admin, is_active=True)
        agent_objs = []
        for agent_obj in agents_list:
            if agent_obj.pk != cobrowse_agent.pk:
                agent_objs.append(agent_obj)

        return render(request, "EasyAssistSalesforceApp/sales_dashboard.html", {
            "salesforce_token": quote_plus(request.GET["salesforce_token"]),
            "user": user,
            "cobrowse_io_objs": cobrowse_io_objs,
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "agent_objs": agent_objs
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAIDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return HttpResponse("Invalid Access")


# @csrf_exempt
def SalesAnalyticsSettings(request):
    try:
        if not check_for_salesforce_request(request):
            return HttpResponse(status=401)
        user = get_authenticated_user(request, User)
        if user == None:
            return HttpResponse(status=401)

        # return HttpResponse("Hurray analytics")

        cobrowse_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)

        if cobrowse_agent.role != "admin":

            cobrowse_admin = get_admin_from_active_agent(
                cobrowse_agent, CobrowseAgent)
            supported_language = []
            for language in cobrowse_admin.supported_language.all():
                if language in cobrowse_agent.supported_language.all():
                    supported_language.append({
                        "key": language.pk,
                        "value": language.title,
                        "is_selected": True,
                    })
                else:
                    supported_language.append({
                        "key": language.pk,
                        "value": language.title,
                        "is_selected": False,
                    })

            product_category = []
            for product in cobrowse_admin.product_category.all():
                if product in cobrowse_agent.product_category.all():
                    product_category.append({
                        "key": product.pk,
                        "value": product.title,
                        "is_selected": True,
                    })
                else:
                    product_category.append({
                        "key": product.pk,
                        "value": product.title,
                        "is_selected": False,
                    })

            return render(request, "EasyAssistSalesforceApp/sales_settings_agent.html", {
                "salesforce_token": quote_plus(request.GET["salesforce_token"]),
                "user": user,
                "cobrowse_agent": cobrowse_agent, 
                "supported_language": supported_language, 
                "product_category": product_category
            })
        else:
            access_token_obj = cobrowse_agent.get_access_token_obj()
            product_category_list=access_token_obj.get_product_categories()
            product_categories= [x.strip() for x in str(product_category_list).split(',')]
            return render(request, "EasyAssistSalesforceApp/sales_settings.html", {
                "salesforce_token": quote_plus(request.GET["salesforce_token"]),
                "user": user,
                "cobrowse_agent": cobrowse_agent, 
                "access_token_obj": access_token_obj, 
                "FLOATING_BUTTON_POSITION": FLOATING_BUTTON_POSITION,
                "product_category": json.dumps(product_categories)
            })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error SalesAnalyticsSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return HttpResponse("Invalid Access")