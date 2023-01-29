from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count
from django.utils.encoding import smart_str
from django.shortcuts import HttpResponse

from EasyAssistSalesforceApp.encrypt import CustomEncrypt, generate_random_key
from EasyAssistSalesforceApp.constants import *
from EasyAssistSalesforceApp.html_parser import strip_html_tags
from EasyAssistSalesforceApp.send_email import send_password_over_email
from EasyAssistSalesforceApp.utils_client_server_signal import send_data_from_server_to_client

import hashlib
import requests
import sys
import json
import operator
import logging
import re
import ast
import random
import array
import datetime
import pytz
import threading
import os
import uuid
import mimetypes
from zipfile import ZipFile
import geocoder

from urllib.parse import urljoin, urlparse, urlencode, quote_plus, unquote
from random import randint
from xlwt import Workbook
from xlrd import open_workbook

logger = logging.getLogger(__name__)


def check_for_salesforce_request(request):
    try:
        if "salesforce" in request.META['HTTP_REFERER']:
            return True
        logger.error("Not a salesforce request", extra={
                     'AppName': 'EasyAssistSalesforce'})
        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_for_salesforce_request %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return False


def generate_salesforce_token(username):
    try:
        custom_encrypt_obj = CustomEncrypt()
        response = {}
        response["username"] = username
        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        return quote_plus(encrypted_response)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error generate_salesforce_token %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return None

# commenting the function for future reference
# def authenticate_salesforce_user(request, SalesforceAgent, User, CobrowseAgent):
#     try:
#         request_json = request.GET
#         email = request_json["email"]
#         first_name = request_json["firstName"]
#         last_name = request_json["lastName"]
#         username = request_json["userName"]
#         role = request_json["role"]
#         password = hashlib.sha256(email.encode()).hexdigest()

#         if role not in ["admin", "supervisor", "agent"]:
#             return None

#         salesforce_agent_obj = SalesforceAgent.objects.filter(email=email).first()
#         if salesforce_agent_obj:
#             user = User.objects.get(email=email)
#             cobrowse_agent = CobrowseAgent.objects.get(user=user)
#             if not cobrowse_agent.is_account_active:
#                 return None

#             user.is_online = True
#             user.save()
#             cobrowse_agent.is_active = True
#             cobrowse_agent.save()
#             logger.info("Found user with email: " + str(email), extra={'AppName': 'EasyAssistSalesforce'})
#         else:
#             if role == "admin":
#                 status = "1"
#             else:
#                 status = "2"
#             SalesforceAgent.objects.create(email=email)
#             user = User.objects.create(username=username,
#                                         email=email,
#                                         first_name=first_name,
#                                         last_name=last_name,
#                                         status=status,
#                                         role="bot_builder")

#             user.set_password(password)
#             user.save()

#             cobrowse_agent = CobrowseAgent.objects.create(user=user)
#             cobrowse_agent.is_active = True
#             cobrowse_agent.role = role
#             if role == "admin":
#                 cobrowse_agent.is_switch_allowed = True
#             cobrowse_agent.save()
#             logger.info("Added user with email: " + str(email), extra={'AppName': 'EasyAssistSalesforce'})

#         return generate_salesforce_token(username)
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("Error authenticate_salesforce_user %s at %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
#         return None


def authenticate_salesforce_user(request, SalesforceAgent, User, CobrowseAgent, CobrowseAccessToken):
    try:
        request_json = request.GET
        email = request_json["email"]
        salesforce_user_id = request_json["user_id"]
        username = email

        salesforce_agent_obj = SalesforceAgent.objects.filter(
            email=email).first()
        if salesforce_agent_obj:
            user = User.objects.get(email=email)
            cobrowse_agent = CobrowseAgent.objects.get(user=user)
            if not cobrowse_agent.is_account_active:
                logger.info("User account with email: " + str(email) + " is deactivated",
                            extra={'AppName': 'EasyAssistSalesforce'})
                return None

            salesforce_agent_obj.user_id = salesforce_user_id
            salesforce_agent_obj.save()

            user.is_online = True
            user.save()
            cobrowse_agent.is_active = True
            cobrowse_agent.save()

            admin_account = get_admin_from_active_agent(
                cobrowse_agent, CobrowseAgent)
            access_token_obj = CobrowseAccessToken.objects.get(
                agent=admin_account)
            # access_token_obj.allow_screen_recording = True
            access_token_obj.allow_screen_sharing_cobrowse = False
            access_token_obj.save()

            logger.info("Found user with email: " + str(email),
                        extra={'AppName': 'EasyAssistSalesforce'})
        else:
            logger.error("User not found with email: " + str(email),
                         extra={'AppName': 'EasyAssistSalesforce'})
            return None

        return generate_salesforce_token(username)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error authenticate_salesforce_user %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return None


def get_active_agent_obj(request, User, CobrowseAgent):
    try:
        salesforce_token = request.GET["salesforce_token"]
        salesforce_token = unquote(salesforce_token)
        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.decrypt(salesforce_token)
        data = json.loads(data)
        username = data["username"]
        active_user = User.objects.get(username=username)
        active_agent = CobrowseAgent.objects.get(
            user=active_user, is_account_active=True)
        return active_agent
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_active_agent_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return None


def easyassist_auto_archive(access_token, CobrowseIO):
    try:
        logger.info("Inside easyassist_auto_archive", extra={
                    'AppName': 'EasyAssistSalesforce'})

        inactivity_datetime = datetime.datetime.now().astimezone(pytz.timezone(
            settings.TIME_ZONE)) - datetime.timedelta(seconds=ARCHIVE_COBROWSE_IO_TIME)
        cobrowse_io_objs = CobrowseIO.objects.filter(
            access_token=access_token, is_archived=False, request_datetime__lte=inactivity_datetime)

        for cobrowse_io in cobrowse_io_objs:
            cobrowse_io.is_archived = True
            cobrowse_io.save()
        logger.info("Successfully exited from easyassist_auto_archive", extra={
                    'AppName': 'EasyAssistSalesforce'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In easyassist_auto_archive: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssistSalesforce'})


def get_list_agents_under_admin(admin_user, is_active=True):
    try:
        cobrowse_agents = []
        agents = []
        if is_active == None:
            agents = list(admin_user.agents.all().filter(
                role="agent", is_account_active=True))
        else:
            agents = list(admin_user.agents.all().filter(
                role="agent", is_active=is_active, is_account_active=True))

        cobrowse_agents += agents
        supervisors = admin_user.agents.all().filter(
            role="supervisor", is_account_active=True)

        for supervisor in supervisors:
            if is_active == None:
                cobrowse_agents += list(supervisor.agents.all().filter(
                    role="agent", is_account_active=True))
            else:
                cobrowse_agents += list(supervisor.agents.all().filter(
                    role="agent", is_account_active=True, is_active=is_active))

        if admin_user.is_switch_allowed:
            if is_active == None:
                cobrowse_agents += [admin_user]
            elif is_active == False and admin_user.is_active == False:
                cobrowse_agents += [admin_user]
            elif is_active == True and admin_user.is_active == True:
                cobrowse_agents += [admin_user]

        return list(set(cobrowse_agents))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_list_agents_under_admin: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

    return []


def get_admin_from_active_agent(active_agent, CobrowseAgent):

    try:
        if active_agent.is_switch_allowed:
            return active_agent

        parent_user = CobrowseAgent.objects.filter(
            agents__pk=active_agent.pk)[0]
        try:
            second_parent = CobrowseAgent.objects.filter(
                agents__pk=parent_user.pk)[0]
            return second_parent
        except Exception:
            return parent_user

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_admin_from_active_agent %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

    return None


def save_audit_trail(cobrowse_agent, action, description, CobrowsingAuditTrail):
    try:
        CobrowsingAuditTrail.objects.create(agent=cobrowse_agent,
                                            action=action,
                                            action_description=description)
        logger.info("Audit Trail Saved Successfully.",
                    extra={'AppName': 'EasyAssistSalesforce'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_audit_trail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def add_supported_language(cobrowse_user, supported_language_list, LanguageSupport):
    try:
        for language_pk in supported_language_list:
            language_obj = LanguageSupport.objects.get(pk=int(language_pk))
            cobrowse_user.supported_language.add(language_obj)
        cobrowse_user.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error add_supported_language %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        pass


def add_selected_supervisor(selected_supervisor_pk_list, active_agent, cobrowse_agent, CobrowseAgent):
    logger.info("inside add supervisor ", extra={
                'AppName': 'EasyAssistSalesforce'})
    for current_supervisor_pk in selected_supervisor_pk_list:
        current_supervisor_pk = int(current_supervisor_pk)
        if current_supervisor_pk == -1:
            current_supervisor = active_agent
        else:
            current_supervisor = CobrowseAgent.objects.get(
                pk=current_supervisor_pk)
        current_supervisor.agents.add(cobrowse_agent)
        current_supervisor.save()
    logger.info("successfully exited add supervisor ",
                extra={'AppName': 'EasyAssistSalesforce'})


def reset_agents_language(cobrowse_user):
    try:

        for agent in cobrowse_user.agents.all():
            for language in agent.supported_language.all():
                if language not in cobrowse_user.supported_language.all():
                    agent.supported_language.remove(language)
                    agent.save()
                    reset_agents_language(cobrowse_user)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error reset_agents_language %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return


def save_language_support(cobrowse_user, supported_language, LanguageSupport):
    try:
        cobrowse_user.supported_language.clear()
        supported_language_list = supported_language.split(",")
        for language in supported_language_list:
            language = str(language).strip()
            if len(language) < 2:
                continue
            language = language[0].upper() + language[1:].lower()
            try:
                language_obj = LanguageSupport.objects.get(title=language)
            except Exception:
                language_obj = LanguageSupport.objects.create(title=language)

            cobrowse_user.supported_language.add(language_obj)
        cobrowse_user.save()

        reset_agents_language(cobrowse_user)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_language_support %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        pass


def save_product_category(cobrowse_user, product_category, ProductCategory):
    try:
        logger.info("Inside save_product_category", extra={
                    'AppName': 'EasyAssistSalesforce'})
        cobrowse_user.product_category.clear()
        product_category_list = product_category.split(",")
        for category in product_category_list:
            category = str(category).strip()
            if len(category) < 2:
                continue
            category = category[0].upper() + category[1:].lower()
            try:
                category_obj = ProductCategory.objects.get(title=category)
            except Exception:
                category_obj = ProductCategory.objects.create(title=category)

            cobrowse_user.product_category.add(category_obj)
        cobrowse_user.save()

        reset_agents_product_category(cobrowse_user)
        logger.info("Successfully exited from save_product_category",
                    extra={'AppName': 'EasyAssistSalesforce'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_product_category %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        pass


def reset_agents_product_category(cobrowse_user):
    try:
        logger.info("Inside reset_agents_product_category",
                    extra={'AppName': 'EasyAssistSalesforce'})
        for agent in cobrowse_user.agents.all():
            for category in agent.product_category.all():
                if category not in cobrowse_user.product_category.all():
                    agent.product_category.remove(category)
                    agent.save()
                    reset_agents_product_category(cobrowse_user)
        logger.info("Successfully exited from reset_agents_product_category", extra={
                    'AppName': 'EasyAssistSalesforce'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error reset_agents_product_category %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return


def add_product_category_to_user(cobrowse_user, selected_product_category_pk_list, ProductCategory):
    try:
        logger.info("Inside add_product_category_to_user",
                    extra={'AppName': 'EasyAssistSalesforce'})
        for product_category_pk in selected_product_category_pk_list:
            product_category_obj = ProductCategory.objects.get(
                pk=int(product_category_pk))
            if product_category_obj not in cobrowse_user.product_category.all():
                cobrowse_user.product_category.add(product_category_obj)
        cobrowse_user.save()
        logger.info("Successfully exited from add_product_category_to_user", extra={
                    'AppName': 'EasyAssistSalesforce'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error add_product_category_to_user %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def get_cobrowse_access_token_obj(request, CobrowseAccessToken):
    cobrowse_access_token = None
    try:
        access_token = request.META.get('HTTP_X_ACCESSTOKEN')
        cobrowse_access_token = CobrowseAccessToken.objects.get(
            key=access_token)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_cobrowse_access_token_obj %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

    return cobrowse_access_token


def get_request_origin(request):
    try:
        origin = request.META.get('HTTP_ORIGIN')
        origin = urlparse(origin)
        return origin.netloc
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_request_origin %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

    return None


def remo_html_from_string(raw_str):
    try:
        regex_cleaner = re.compile('<.*?>')
        cleaned_raw_str = re.sub(regex_cleaner, '', raw_str)
        return cleaned_raw_str
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In remo_html_from_string: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssistSalesforce'})
        return raw_str


def remo_special_tag_from_string(raw_str):
    try:
        cleaned_raw_str = raw_str.replace(
            "+", "").replace("|", "").replace("-", "").replace("=", "")
        return cleaned_raw_str
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In remo_special_tag_from_string: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssistSalesforce'})
        return raw_str


def send_agent_customer_connected_notification(agent, cobrowse_io):
    try:
        if agent == None:
            return

        if cobrowse_io == None:
            return

        socket_response = {}
        notification_list = ["Hi, " + agent.user.username +
                             "! A customer has connected with you on Cogno Cobrowse."]
        socket_response["status"] = 200
        socket_response["message"] = "success"
        socket_response["notification_list"] = notification_list
        send_data_from_server_to_client(
            "notification", socket_response, agent.user)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_agent_customer_connected_notification %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return False


def extract_authorization_params(request):
    try:
        custom_encrypt_obj = CustomEncrypt()
        auth_token = request.META["HTTP_AUTHORIZATION"].split(" ")[-1]
        auth_token = custom_encrypt_obj.decrypt(auth_token)
        return tuple(auth_token.split(":"))
    except Exception:
        return None


def check_and_update_lead(primary_value_list, meta_data, cobrowse_io, CobrowseCapturedLeadData):
    try:
        cobrowse_io.captured_lead.clear()
        for primary_id in primary_value_list:
            primary_id = primary_id.strip().lower()
            primary_value = hashlib.md5(primary_id.encode()).hexdigest()

            lead_obj = CobrowseCapturedLeadData.objects.filter(
                primary_value=primary_value, session_id=cobrowse_io.session_id).first()
            if lead_obj is None:
                logger.info("lead for " + str(cobrowse_io.session_id) +
                            " not found. Creating a new lead object.", extra={'AppName': 'EasyAssistSalesforce'})
                lead_obj = CobrowseCapturedLeadData.objects.create(
                    primary_value=primary_value, session_id=cobrowse_io.session_id)
            else:
                logger.info("lead for " + str(cobrowse_io.session_id) +
                            " found.", extra={'AppName': 'EasyAssistSalesforce'})

            cobrowse_io.captured_lead.add(lead_obj)

        cobrowse_io.meta_data = meta_data
        cobrowse_io.last_update_datetime = timezone.now()
        cobrowse_io.is_agent_connected = False
        cobrowse_io.is_active = True
        cobrowse_io.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_and_update_lead %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def save_system_audit_trail(category, description, cobrowse_io, cobrowse_access_token, SystemAuditTrail, sender=None):
    try:
        SystemAuditTrail.objects.create(category=category,
                                        description=description,
                                        cobrowse_io=cobrowse_io,
                                        cobrowse_access_token=cobrowse_access_token,
                                        sender=sender)
        logger.info("System Audit Trail saved successfully",
                    extra={'AppName': 'EasyAssistSalesforce'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_system_audit_trail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def delete_expired_cobrowse_middleware_token(CobrowsingMiddlewareAccessToken):
    try:
        current_date = (datetime.datetime.now() - datetime.timedelta(1)).date()
        CobrowsingMiddlewareAccessToken.objects.filter(
            timestamp__date__lte=current_date).delete()
        CobrowsingMiddlewareAccessToken.objects.filter(
            is_expired=True).delete()
        logger.info(
            "Expired Cobrowsing Middleware Access Token deleted successfully.", extra={'AppName': 'EasyAssistSalesforce'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error delete_expired_cobrowse_middleware_token %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def create_cobrowse_middleware_token(CobrowsingMiddlewareAccessToken):
    return CobrowsingMiddlewareAccessToken.objects.create()

# added from old


class UrlShortenTinyurl:
    URL = "http://tinyurl.com/api-create.php"

    def shorten(self, url_long):
        try:
            url = self.URL + "?" \
                + urlencode({"url": url_long})
            res = requests.get(url)
            return res.text
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error shorten %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
            return ""


def convert_seconds_to_hours_minutes(seconds):
    try:
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60

        duration = ""
        if hour > 0:
            duration = str(hour) + (" hours " if hour > 1 else " hour ")
        duration += str(minutes) + (" minutes" if minutes > 1 else " minute")
        return duration
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In convert_seconds_to_hours_minutes: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssistSalesforce'})
        return "0 minute"


def check_malicious_file_from_filename(filename):
    allowed_files_list = [
        "png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg",
        "mp2", "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt",
        "flv", "swf", "avchd", "mp3", "aac", "pdf", "xls", "xlsx", "json", "xlsm", "xlt", "xltm", "zip"
    ]

    try:
        if len(filename.split('.')) != 2:
            return True

        if filename.split('.')[-1] not in allowed_files_list:
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In check_malicious_file_from_filename: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssistSalesforce'})
        return True


def check_malicious_file(uploaded_file):
    return check_malicious_file_from_filename(uploaded_file.name)


def delete_user_session(user_session, Session):
    try:
        logger.info("In delete_user_session", extra={'AppName': 'EasyAssistSalesforce',
                                                     'user_id': user_session.user.username})
        session_objs = Session.objects.filter(pk=user_session.session_key)
        user_session.delete()
        if session_objs:
            session_objs.delete()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In delete_user_session: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyAssistSalesforce', 'user_id': str(user_session.user.username)})


def is_online(username, UserSession):
    try:
        logger.info("In is_online", extra={
                    'AppName': 'EasyAssistSalesforce', 'user_id': str(username)})
        user_session_objs = UserSession.objects.filter(user__username=username)
        logger.info("user sessions count: " + str(user_session_objs.count()), extra={
                    'AppName': 'EasyAssistSalesforce', 'user_id': str(username)})
        if user_session_objs:
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In is_online: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyAssistSalesforce'})
    return False


def logout_all(username, UserSession, Session):
    try:
        logger.info("In logout_all", extra={
                    'AppName': 'EasyAssistSalesforce', 'user_id': str(username)})
        user_session_objs = UserSession.objects.filter(user__username=username)
        for user_session_obj in user_session_objs:
            delete_user_session(user_session_obj, Session)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In delete_user_session: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyAssistSalesforce', 'user_id': str(username)})


def get_list_of_unresolved_screencast(ScreenCast, agent_obj):
    return ScreenCast.objects.filter(status="unresolved")


def get_list_of_resolved_screencast(ScreenCast, agent_obj):
    return ScreenCast.objects.filter(status="resolved")


def perform_masking(screen_cast_obj, Field):
    try:
        input_html_elements = json.loads(screen_cast_obj.input_html_elements)
        for html_element in input_html_elements:
            for md5_html_element_str in input_html_elements[html_element]:
                url = screen_cast_obj.website_url
                try:
                    field_obj = Field.objects.get(
                        form__url=url, field_id=md5_html_element_str)
                    name = field_obj.name
                    if field_obj.is_masked:
                        current_value = input_html_elements[
                            html_element][md5_html_element_str]["value"]
                        input_html_elements[html_element][md5_html_element_str]["value"] = "*" * len(
                            current_value)
                    input_html_elements[html_element][
                        md5_html_element_str]["name"] = name
                    input_html_elements[html_element][
                        md5_html_element_str]["is_valid_field"] = True
                    input_html_elements[html_element][md5_html_element_str][
                        "group_color"] = field_obj.group_color
                    input_html_elements[html_element][md5_html_element_str][
                        "field_order"] = field_obj.field_order
                except Exception:
                    input_html_elements[html_element][
                        md5_html_element_str]["is_valid_field"] = True
                    input_html_elements[html_element][
                        md5_html_element_str]["group_color"] = ""
                    input_html_elements[html_element][
                        md5_html_element_str]["field_order"] = 0

        return input_html_elements
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error perform_masking %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
    return None


def save_remote_file(url):
    try:
        response = requests.get(url, timeout=5)
        filename = url.split("/")[-1]
        with open(settings.MEDIA_ROOT + "static/" + filename, "wb") as temp_file:
            temp_file.write(response.content)
            temp_file.close()
        return "https://easyassist.allincall.in/files/static/" + filename
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_remote_file %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return url


def get_file_type(url):
    try:
        return str(url).split("/")[-1].split(".")[-1]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_file_type %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

        return None


def convert_relative_path_to_absolute(text, address):
    try:
        import re
        req_css_links = re.findall(r'url\((.*?)\)', text)
        content = text
        for req_css_link in req_css_links:
            css_link = req_css_link.replace("\"", "")
            css_link = css_link.replace("'", "")
            updated_css_link = urljoin(address, str(css_link))
            file_type = get_file_type(updated_css_link)
            if file_type in ["woff2", "woff", "tff", "png", "jpg", "jpeg"]:
                updated_css_link = save_remote_file(updated_css_link)
            elif updated_css_link != address:
                updated_css_link = "https://easyassist.allincal.in/easy-assist/files/" + updated_css_link

            content = content.replace(
                "url(" + req_css_link + ")", "url(" + updated_css_link + ")")
        return content
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error convert_relative_path_to_absolute %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

    return None


def convert_absolute_path_in_html(html, address):
    try:
        import re
        req_css_links = re.findall(r'url\((.*?)\)', html)
        content = html
        for req_css_link in req_css_links:
            css_link = req_css_link.replace("\"", "")
            css_link = css_link.replace("'", "")
            updated_css_link = urljoin(address, str(css_link))
            content = content.replace(
                "url(" + req_css_link + ")", "url(" + updated_css_link + ")")

        return content
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error convert_absolute_path_in_html %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

    return None


def get_least_loaded_agent(User, CobrowseAgent, CobrowseIO):
    agent_obj = None
    try:
        agent_dict = {}
        for agent in CobrowseAgent.objects.filter(role="agent"):
            agent_dict[agent.user.username] = 0

        cobrowseio_obj_list = CobrowseIO.objects.filter(~Q(agent=None)).values(
            'agent__user__username').annotate(total=Count('agent')).order_by("total")

        for cobrowseio_obj in cobrowseio_obj_list:
            agent_dict[cobrowseio_obj["agent__user__username"]
                       ] = cobrowseio_obj["total"]

        agent_username = min(agent_dict.items(), key=operator.itemgetter(1))[0]
        user = User.objects.get(username=agent_username)
        agent_obj = CobrowseAgent.objects.get(user=user)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_least_loaded_agent %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

    logger.info("get_least_loaded_agent: %s", agent_obj,
                extra={'AppName': 'EasyAssistSalesforce'})
    return agent_obj


def get_list_supervisor_under_admin(admin_user, is_active=True):
    try:
        cobrowse_agents = []
        agents = []
        if is_active == None:
            agents = list(admin_user.agents.all().filter(
                role="supervisor", is_account_active=True))
        else:
            agents = list(admin_user.agents.all().filter(
                role="supervisor", is_active=is_active, is_account_active=True))

        cobrowse_agents += agents

        return list(set(cobrowse_agents))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_list_supervisor_under_admin: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

    return []


def get_supervisor_from_active_agent(active_agent, CobrowseAgent):
    try:
        return list(CobrowseAgent.objects.filter(role="supervisor", is_account_active=True, agents__in=[active_agent]))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_supervisor_from_active_agent %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

    return []


def filter_free_active_agent(agent_list, cobrowse_io_obj):
    free_agent_list = []
    try:
        for agent in agent_list:
            if agent.is_cobrowsing_active == False:
                if cobrowse_io_obj.access_token.allow_language_support:
                    if cobrowse_io_obj.supported_language in agent.supported_language.all():
                        if cobrowse_io_obj.access_token.choose_product_category:
                            if cobrowse_io_obj.product_category in agent.product_category.all():
                                free_agent_list.append(agent)
                        else:
                            free_agent_list.append(agent)
                else:
                    if cobrowse_io_obj.access_token.choose_product_category:
                        if cobrowse_io_obj.product_category in agent.product_category.all():
                            free_agent_list.append(agent)
                    else:
                        free_agent_list.append(agent)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error filter_free_active_agent %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        free_agent_list = agent_list

    return free_agent_list


def generate_md5(str):
    return hashlib.md5(str.encode()).hexdigest()


def generate_random_password():
    # maximum length of password needed
    # this can be changed to suit your password length
    MAX_LEN = 12

    # declare arrays of the character that we need in out password
    # Represented as chars to enable easy string concatenation
    DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    LOCASE_CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                         'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                         'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                         'z']

    UPCASE_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                         'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q',
                         'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                         'Z']

    SYMBOLS = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>',
               '*', '(', ')']

    # combines all the character arrays above to form one array
    COMBINED_LIST = DIGITS + UPCASE_CHARACTERS + LOCASE_CHARACTERS + SYMBOLS

    # randomly select at least one character from each character set above
    rand_digit = random.choice(DIGITS)
    rand_upper = random.choice(UPCASE_CHARACTERS)
    rand_lower = random.choice(LOCASE_CHARACTERS)
    rand_symbol = random.choice(SYMBOLS)

    # combine the character randomly selected above
    # at this stage, the password contains only 4 characters but
    # we want a 12-character password
    temp_pass = rand_digit + rand_upper + rand_lower + rand_symbol

    # now that we are sure we have at least one character from each
    # set of characters, we fill the rest of
    # the password length by selecting randomly from the combined
    # list of character above.
    for value in range(MAX_LEN - 4):
        temp_pass = temp_pass + random.choice(COMBINED_LIST)
        # convert temporary password into array and shuffle to
        # prevent it from having a consistent pattern
        # where the beginning of the password is predictable

        temp_pass_list = [char for char in temp_pass]
        # temp_pass_list = array.array('d', temp_pass)
        random.shuffle(temp_pass_list)

    # traverse the temporary password array and append the chars
    # to form the password
    password = ""
    for value in temp_pass_list:
        password = password + value

    # print out password
    return password


def is_valid_cobrowse_middleware_token(token, CobrowsingMiddlewareAccessToken):
    is_valid = False
    try:
        access_token = CobrowsingMiddlewareAccessToken.objects.get(token=token)
        if access_token.is_expired:
            is_valid = False
        else:
            access_token.is_expired = True
            access_token.save()
            is_valid = True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error is_valid_cobrowse_middleware_token %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

    return is_valid


def random_with_n_digits(number):
    range_start = 10**(number - 1)
    range_end = (10**number) - 1
    return randint(range_start, range_end)


def save_agent_closing_comments_cobrowseio(cobrowse_io_obj,
                                           agent_obj,
                                           comments,
                                           CobrowseAgentComment):
    try:
        CobrowseAgentComment.objects.create(cobrowse_io=cobrowse_io_obj,
                                            agent=agent_obj,
                                            agent_comments=comments)
        logger.info("Cobrowsing session closing remarks saved successfully.", extra={
                    'AppName': 'EasyAssistSalesforce'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_agent_closing_comments_cobrowseio %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def get_visited_page_title_list_with_agent(active_agent, CobrowseAgent, CobrowseIO):
    try:
        if active_agent.role == "admin":
            active_admin_user = active_agent
        else:
            active_admin_user = get_admin_from_active_agent(
                active_agent, CobrowseAgent)

        cobrowse_io_objs = CobrowseIO.objects.filter(is_archived=True,
                                                     access_token__agent=active_admin_user).filter(~Q(title=None))

        query_pages = list(
            set(list(cobrowse_io_objs.values_list('title', flat=True))))

        return query_pages
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_visited_page_title_list_with_agent %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

    return []


def create_excel_sales_support_history(user, cobrowse_io_objs, access_token_obj):
    filename = None
    try:
        logger.info("create_excel_sales_support_history",
                    extra={'AppName': 'EasyAssistSalesforce'})

        support_history_wb = Workbook()
        sheet1 = support_history_wb.add_sheet("Support History")

        sheet1.write(0, 0, "Customer Name")
        sheet1.col(0).width = 256 * 20
        sheet1.write(0, 1, "Customer Mobile Number")
        sheet1.col(1).width = 256 * 25
        sheet1.write(0, 2, "Agent")
        sheet1.col(2).width = 256 * 35
        sheet1.write(0, 3, "Cobrowsing Start Datetime")
        sheet1.col(3).width = 256 * 25
        sheet1.write(0, 4, "Session End DateTime")
        sheet1.col(4).width = 256 * 25
        sheet1.write(0, 5, "Time Spent")
        sheet1.col(5).width = 256 * 15
        sheet1.write(0, 6, "Lead Status")
        sheet1.col(6).width = 256 * 15
        sheet1.write(0, 7, "Title")
        sheet1.col(7).width = 256 * 60
        sheet1.write(0, 8, "Session ID")
        sheet1.col(8).width = 256 * 45
        sheet1.write(0, 9, "Agent Remarks")
        sheet1.col(9).width = 256 * 80
        if access_token_obj is not None and access_token_obj.allow_language_support:
            sheet1.write(0, 10, "Language")
            sheet1.col(10).width = 256 * 25

        index = 1
        for cobrowse_io_obj in cobrowse_io_objs:

            if not cobrowse_io_obj.is_lead:
                sheet1.write(index, 0, cobrowse_io_obj.full_name)
                sheet1.write(index, 1, cobrowse_io_obj.mobile_number)
            else:
                sheet1.write(
                    index, 0, cobrowse_io_obj.get_sync_data_value("name"))
                sheet1.write(
                    index, 1, cobrowse_io_obj.get_sync_data_value("mobile"))
            sheet1.write(index, 2, cobrowse_io_obj.agent.user.username)
            sheet1.write(index, 3, str(cobrowse_io_obj.cobrowsing_start_datetime.astimezone(
                pytz.timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d %I:%M %p")))
            sheet1.write(index, 4, str(cobrowse_io_obj.last_agent_update_datetime.astimezone(
                pytz.timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d %I:%M %p")))
            sheet1.write(index, 5, str(cobrowse_io_obj.total_time_spent()))

            if cobrowse_io_obj.is_archived == True and cobrowse_io_obj.is_helpful == True:
                sheet1.write(index, 6, "Converted")
            else:
                sheet1.write(index, 6, "Not Converted")
            sheet1.write(index, 7, cobrowse_io_obj.title)
            sheet1.write(index, 8, str(cobrowse_io_obj.session_id))
            sheet1.write(index, 9, cobrowse_io_obj.agent_comments)
            if access_token_obj is not None and access_token_obj.allow_language_support:
                if cobrowse_io_obj.supported_language is not None:
                    sheet1.write(
                        index, 10, cobrowse_io_obj.supported_language.title)
                else:
                    sheet1.write(index, 10, "")
            index += 1

        if not os.path.exists('secured_files/EasyAssistSalesforceApp/CobrowseSupportHistory'):
            os.makedirs(
                'secured_files/EasyAssistSalesforceApp/CobrowseSupportHistory')

        filename = "secured_files/EasyAssistSalesforceApp/CobrowseSupportHistory/" + \
            str(user.username) + ".xls"
        support_history_wb.save(filename)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_excel_sales_support_history %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        filename = None
    return filename


def create_excel_unattended_leads_datails(user, cobrowse_io_objs, access_token_obj):
    filename = None
    try:
        logger.info("create_excel_unattended_leads_datails",
                    extra={'AppName': 'EasyAssistSalesforce'})

        support_history_wb = Workbook()
        sheet1 = support_history_wb.add_sheet("Support History")

        sheet1.write(0, 0, "Customer Name")
        sheet1.col(0).width = 256 * 20
        sheet1.write(0, 1, "Customer Mobile Number")
        sheet1.col(1).width = 256 * 25
        sheet1.write(0, 2, "Agent")
        sheet1.col(2).width = 256 * 35
        sheet1.write(0, 3, "Cobrowsing Request Datetime")
        sheet1.col(3).width = 256 * 30
        sheet1.write(0, 4, "Title")
        sheet1.col(4).width = 256 * 80
        sheet1.write(0, 5, "Agent Remarks")
        sheet1.col(5).width = 256 * 80
        if access_token_obj is not None and access_token_obj.allow_language_support:
            sheet1.write(0, 6, "Language")
            sheet1.col(6).width = 256 * 25

        index = 1
        for cobrowse_io_obj in cobrowse_io_objs:
            if not cobrowse_io_obj.is_lead:
                sheet1.write(index, 0, cobrowse_io_obj.full_name)
                sheet1.write(index, 1, cobrowse_io_obj.mobile_number)
            else:
                sheet1.write(
                    index, 0, cobrowse_io_obj.get_sync_data_value("name"))
                sheet1.write(
                    index, 1, cobrowse_io_obj.get_sync_data_value("mobile"))

            sheet1.write(index, 2, cobrowse_io_obj.agent.user.username)
            sheet1.write(index, 3, str(cobrowse_io_obj.request_datetime.astimezone(
                pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %I:%M %p")))
            sheet1.write(index, 4, cobrowse_io_obj.title)
            sheet1.write(index, 5, cobrowse_io_obj.agent_comments)
            if access_token_obj is not None and access_token_obj.allow_language_support:
                if cobrowse_io_obj.supported_language is not None:
                    sheet1.write(
                        index, 6, cobrowse_io_obj.supported_language.title)
                else:
                    sheet1.write(index, 6, "")
            index += 1

        if not os.path.exists('secured_files/EasyAssistSalesforceApp/UnattendedLeads'):
            os.makedirs(
                'secured_files/EasyAssistSalesforceApp/UnattendedLeads')

        filename = "secured_files/EasyAssistSalesforceApp/UnattendedLeads/" + \
            str(user.username) + ".xls"
        support_history_wb.save(filename)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_excel_unattended_leads_datails %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        filename = None
    return filename


def create_excel_meeting_support_history(user, audit_trail_objs, CobrowsingFileAccessManagement):
    filename = None
    try:
        logger.info("create_excel_meeting_support_history",
                    extra={'AppName': 'EasyAssistSalesforce'})
        if not os.path.exists('secured_files/EasyAssistApp/MeetingSupportHistory'):
            os.makedirs('secured_files/EasyAssistApp/MeetingSupportHistory')
        meeting_support_history_wb = Workbook()
        sheet1 = meeting_support_history_wb.add_sheet(
            "Meeting Support History")

        sheet1.write(0, 0, "Customer Name")
        sheet1.col(0).width = 256 * 20
        sheet1.write(0, 1, "Customer Mobile Number")
        sheet1.col(1).width = 256 * 25
        sheet1.write(0, 2, "Agent")
        sheet1.col(2).width = 256 * 35
        sheet1.write(0, 3, "Meeting Start Datetime")
        sheet1.col(3).width = 256 * 25
        sheet1.write(0, 4, "Meeting End DateTime")
        sheet1.col(4).width = 256 * 25
        sheet1.write(0, 5, "Time Spent")
        sheet1.col(5).width = 256 * 15
        sheet1.write(0, 6, "Meeting Status")
        sheet1.col(6).width = 256 * 15
        sheet1.write(0, 7, "Meeting ID")
        sheet1.col(7).width = 256 * 45
        sheet1.write(0, 8, "Meeting Notes")
        sheet1.col(8).width = 256 * 45
        sheet1.write(0, 9, "Client Location")
        sheet1.col(9).width = 256 * 90
        sheet1.write(0, 10, "Attachment")
        sheet1.col(10).width = 256 * 45

        index = 1
        for audit_trail_objs in audit_trail_objs:
            # user_address = ""
            client_location_details = json.loads(
                audit_trail_objs.client_location_details)
            client_address = []
            for location_obj in client_location_details['items']:
                client_name = location_obj['client_name']
                longitude = location_obj['longitude']
                latitude = location_obj['latitude']
                if latitude == 'None' or longitude == 'None':
                    continue

                try:
                    location = geocoder.google(
                        [latitude, longitude], method="reverse", key="AIzaSyBAHTtk1lkVvIl1X_i7_1aIK9RCrhqGEpQ")
                    client_address.append(
                        client_name + " - " + location.address)
                except Exception:
                    logger.warning("Error in create_excel_meeting_support_history, client's address not found",
                                   extra={'AppName': 'EasyAssist'})

            screenshots = json.loads(audit_trail_objs.meeting_screenshot)

            attachment_link = ""
            if len(screenshots['items']) > 0:
                zip_file_path = "secured_files/EasyAssistApp/MeetingSupportHistory/attachment_" + \
                    uuid.uuid4().hex + ".zip"

                zip_obj = ZipFile(zip_file_path, 'w')

                for screenshot_obj in screenshots['items']:
                    file_key = screenshot_obj['screenshot']
                    try:
                        file_access_management_obj = CobrowsingFileAccessManagement.objects.get(
                            key=file_key, is_public=False)

                        path_to_file = file_access_management_obj.file_path
                        file_name = path_to_file.split(os.sep)[-1]
                        zip_obj.write(path_to_file[1:], file_name)
                    except Exception:
                        logger.warning("Error in create_excel_meeting_support_history, Invalid file_key",
                                       extra={'AppName': 'EasyAssist'})
                zip_obj.close()

                zip_file_path = "/" + zip_file_path
                zip_file_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=zip_file_path, is_public=False)
                attachment_link = settings.EASYCHAT_HOST_URL + \
                    '/easy-assist/download-file/' + str(zip_file_obj.key)

            sheet1.write(index, 0, audit_trail_objs.cobrowse_video.full_name)
            sheet1.write(
                index, 1, audit_trail_objs.cobrowse_video.mobile_number)

            sheet1.write(
                index, 2, audit_trail_objs.cobrowse_video.agent.user.username)
            sheet1.write(index, 3, str(audit_trail_objs.agent_joined.astimezone(
                pytz.timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d %I:%M %p")))
            sheet1.write(index, 4, str(audit_trail_objs.meeting_ended.astimezone(
                pytz.timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d %I:%M %p")))
            sheet1.write(index, 5, str(
                audit_trail_objs.get_readable_meeting_duration()))

            if audit_trail_objs.is_meeting_ended == True:
                sheet1.write(index, 6, "Completed")
            else:
                sheet1.write(index, 6, "Not Completed")
            sheet1.write(index, 7, str(
                audit_trail_objs.cobrowse_video.meeting_id))
            if audit_trail_objs.agent_notes == None:
                sheet1.write(index, 8, "")
            else:
                sheet1.write(index, 8, audit_trail_objs.agent_notes)

            sheet1.write(index, 9, " | ".join(client_address))
            sheet1.write(index, 10, attachment_link)
            index += 1
        if not os.path.exists('secured_files/EasyAssistSalesforceApp/MeetingSupportHistory'):
            os.makedirs(
                'secured_files/EasyAssistSalesforceApp/MeetingSupportHistory')

        filename = "secured_files/EasyAssistSalesforceApp/MeetingSupportHistory/" + \
            str(user.username) + ".xls"
        meeting_support_history_wb.save(filename)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_excel_meeting_support_history %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        filename = None
    return filename


def create_excel_easyassist_customer_details(active_agent, easyassist_customer_objs):
    filename = None
    try:
        logger.info("create_excel_easyassist_customer_details",
                    extra={'AppName': 'EasyAssistSalesforce'})

        easyassist_customer_details_wb = Workbook()
        sheet1 = easyassist_customer_details_wb.add_sheet("Customer Details")

        sheet1.write(0, 0, "DateTime of Clicking Request for Support")
        sheet1.col(0).width = 256 * 50
        sheet1.write(0, 1, "Customer Name")
        sheet1.col(1).width = 256 * 20
        sheet1.write(0, 2, "Customer Mobile Number")
        sheet1.col(2).width = 256 * 25

        index = 1

        for easyassist_customer in easyassist_customer_objs:
            sheet1.write(index, 0, str(easyassist_customer.request_datetime.astimezone(
                pytz.timezone('Asia/Kolkata')).strftime("%d %b %Y %I:%M %p")))
            sheet1.write(index, 1, easyassist_customer.full_name)
            sheet1.write(index, 2, easyassist_customer.mobile_number)

            index += 1

        filename = "files/EasyAssist_CustomerDetails_" + \
            str(active_agent.user.username) + ".xlsx"
        easyassist_customer_details_wb.save(filename)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_excel_easyassist_customer_details %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        filename = None
    return filename


def create_excel_user_details(active_agent):
    filename = None
    try:
        logger.info("In create_excel_user_details",
                    extra={'AppName': 'EasyAssistSalesforce'})

        agents = active_agent.agents.filter(role="agent")
        current_datetime = datetime.datetime.now()

        support_history_wb = Workbook()
        sheet1 = support_history_wb.add_sheet("Agent Details")

        sheet1.write(0, 0, "DateTime")
        sheet1.col(0).width = 256 * 20
        sheet1.write(0, 1, "Name")
        sheet1.col(1).width = 256 * 20
        sheet1.write(0, 2, "Email")
        sheet1.col(2).width = 256 * 20
        sheet1.write(0, 3, "Mobile Number")
        sheet1.col(3).width = 256 * 20
        sheet1.write(0, 4, "Status")
        sheet1.col(4).width = 256 * 20

        index = 1
        for agent in agents:
            sheet1.write(index, 0, str(current_datetime.astimezone(
                pytz.timezone('Asia/Kolkata')).strftime("%d %b %Y %I:%M %p")))
            sheet1.write(index, 1, agent.user.first_name)
            sheet1.write(index, 2, agent.user.username)
            sheet1.write(index, 3, agent.mobile_number)
            if agent.is_active:
                sheet1.write(index, 4, "Online")
            else:
                sheet1.write(index, 4, "Offline")
            index += 1

        filename = "files/EasyAssist_Agent_Details_" + \
            str(active_agent.user.username) + ".xlsx"
        support_history_wb.save(filename)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_excel_user_details %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        filename = None
    return filename


def add_users_from_excel_document(file_path, active_agent, User, CobrowseAgent, LanguageSupport, SalesforceAgent):
    try:
        logger.info("Inside add_users_from_excel_document",
                    extra={'AppName': 'EasyAssistSalesforce'})
        cobrowse_access_token = active_agent.get_access_token_obj()

        workbook1 = open_workbook(file_path)
        sheet1 = workbook1.sheet_by_name(workbook1.sheet_names()[0])

        regName = '^[^\s][a-zA-Z ]+$'
        regEmail = '^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$'
        regMob = '^[6-9]{1}[0-9]{9}$'

        total_rows = sheet1.nrows
        for row_num in range(1, total_rows):
            logger.info("row: " + str(row_num),
                        extra={'AppName': 'EasyAssistSalesforce'})
            row_values = sheet1.row_values(row_num)
            logger.info("row_values: " + str(row_values),
                        extra={'AppName': 'EasyAssistSalesforce'})

            user_name = str(row_values[0]).strip()
            if len(user_name) == 0:
                continue
            if re.search(regName, user_name) == False:
                continue
            logger.info("Valid user_name: " + str(user_name),
                        extra={'AppName': 'EasyAssistSalesforce'})

            user_email = str(row_values[1]).strip()
            if len(user_email) == 0:
                continue
            if re.search(regEmail, user_email) == False:
                continue
            if CobrowseAgent.objects.filter(user__email=user_email, is_account_active=True).count() > 0:
                logger.info(str(user_email) + " is already an existing user",
                            extra={'AppName': 'EasyAssistSalesforce'})
                continue
            logger.info("Valid user_email: " +
                        str(user_email), extra={'AppName': 'EasyAssistSalesforce'})

            user_mobile = str(row_values[2]).strip()
            if user_mobile == "":
                user_mobile = None
            if user_mobile is not None:
                if len(user_mobile) < 10:
                    continue
                user_mobile = user_mobile[:10]
                if re.search(regMob, user_mobile) == False:
                    continue
                if CobrowseAgent.objects.filter(mobile_number=user_mobile, is_account_active=True).count() > 0:
                    logger.info(str(user_mobile) + " already exists for a user",
                                extra={'AppName': 'EasyAssistSalesforce'})
                    continue
            logger.info("Valid user_mobile: " +
                        str(user_mobile), extra={'AppName': 'EasyAssistSalesforce'})

            user_type = str(row_values[3]).strip()
            if len(user_type) == 0:
                continue
            user_type = user_type.lower()
            if user_type != "agent" and user_type != "supervisor":
                continue
            logger.info("Valid user_type: " +
                        str(user_type), extra={'AppName': 'EasyAssistSalesforce'})

            language_list = str(row_values[4]).strip()
            selected_language_pk_list = []
            if cobrowse_access_token.allow_language_support == True:
                supported_language_list = language_list.split(",")
                for language in supported_language_list:
                    language = str(language).strip()
                    if len(language) < 2:
                        continue
                    language = language[0].upper() + language[1:].lower()
                    language_obj = active_agent.supported_language.filter(
                        title=language).first()
                    if language_obj is not None:
                        selected_language_pk_list.append(language_obj.pk)
                    else:
                        selected_language_pk_list.clear()
                        break
                if len(selected_language_pk_list) == 0:
                    continue
            logger.info("Valid language_list: " +
                        str(language_list), extra={'AppName': 'EasyAssistSalesforce'})

            support_level = str(row_values[5]).strip()
            if len(support_level) == 0 or support_level not in COBROWSING_AGENT_SUPPORT_DICT:
                continue
            logger.info("Valid support_level: " +
                        str(support_level), extra={'AppName': 'EasyAssistSalesforce'})

            supervisor_username = str(row_values[6]).strip()
            supervisor_obj = None
            if user_type == "agent":
                if len(supervisor_username) == 0:
                    continue
                supervisor_obj = active_agent.agents.all().filter(
                    role="supervisor", is_account_active=True, user__username=supervisor_username).first()
                if supervisor_obj is None:
                    if active_agent.user.username == supervisor_username:
                        supervisor_obj = active_agent
                    else:
                        continue
            else:
                supervisor_obj = active_agent
            logger.info("Valid supervisor_username: " +
                        str(supervisor_username), extra={'AppName': 'EasyAssistSalesforce'})

            user = None
            password = generate_random_password()

            try:
                user = User.objects.get(username=user_email)
                user.email = user_email
                user.save()
            except Exception:
                user = User.objects.create(first_name=user_name,
                                           email=user_email,
                                           username=user_email,
                                           status="2",
                                           role="bot_builder")
                user.set_password(password)
                user.save()

            platform_url = settings.EASYCHAT_HOST_URL

            thread = threading.Thread(target=send_password_over_email, args=(
                user_email, user_name, password, platform_url, ), daemon=True)
            thread.start()

            user.set_password(password)
            user.save()

            cobrowse_agent = CobrowseAgent.objects.create(user=user,
                                                          mobile_number=user_mobile,
                                                          role=user_type,
                                                          support_level=support_level)

            supervisor_obj.agents.add(cobrowse_agent)
            supervisor_obj.save()
            add_supported_language(
                cobrowse_agent, selected_language_pk_list, LanguageSupport)

            SalesforceAgent.objects.create(email=user_email)
            logger.info("Added user user_name: " +
                        str(user_name), extra={'AppName': 'EasyAssistSalesforce'})

        logger.info("Successfully exited from add_users_from_excel_document",
                    extra={'AppName': 'EasyAssistSalesforce'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error add_users_from_excel_document %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def check_cogno_meet_status(meeting_io):
    try:
        start_date = meeting_io.meeting_start_date
        current_date = datetime.datetime.now()
        meeting_start_time = meeting_io.meeting_start_time
        current_time = current_date.strftime("%H:%M:%S")
        if start_date > current_date.date():
            return 'waiting'
        elif start_date < current_date.date():
            meeting_io.is_expired = True
            meeting_io.save()
        elif str(meeting_start_time) > str(current_time):
            return 'waiting'
        else:
            meeting_end_time = meeting_io.meeting_end_time
            if str(meeting_end_time) < str(current_time):
                meeting_io.is_expired = True
                meeting_io.save()
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error check_cogno_meet_status %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
        return False

# def create_app_cobrowsing_session(cobrowse_io, user_type, AppCobrowsingSessionManagement):
#     try:
#         total_sessions = AppCobrowsingSessionManagement.objects.filter(cobrowse_io=cobrowse_io, user_type=user_type).count()

#         user_alias = str(user_type) + "-" + str(total_sessions + 1)

#         return AppCobrowsingSessionManagement.objects.create(cobrowse_io=cobrowse_io,
#                                                              user_type=user_type,
#                                                              user_alias=user_alias)
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("Error create_app_cobrowsing_session %s at %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def file_download(file_key, CobrowsingFileAccessManagement, SupportDocument):
    file_access_management_obj = None
    try:
        file_access_management_obj = CobrowsingFileAccessManagement.objects.get(
            key=file_key)

        path_to_file = file_access_management_obj.file_path

        support_document_obj = SupportDocument.objects.filter(
            file_access_management_key=file_key)
        if support_document_obj.count() > 0:
            filename = support_document_obj[0].file_name
        else:
            filename = path_to_file.split("/")[-1]

        path_to_file = settings.BASE_DIR + path_to_file
        mime_type, _ = mimetypes.guess_type(path_to_file)

        if os.path.exists(path_to_file):
            with open(path_to_file, 'rb') as fh:
                response = HttpResponse(
                    fh.read(), status=200, content_type=mime_type)
                response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(
                    str(filename))
                response['X-Sendfile'] = smart_str(path_to_file)
                # response['X-Accel-Redirect'] = path_to_file
                return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error file_download %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})

    return HttpResponse(status=404)
