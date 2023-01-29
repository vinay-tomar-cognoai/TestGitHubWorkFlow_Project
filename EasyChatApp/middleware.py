from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponseRedirect, redirect
from django.contrib import auth
from datetime import datetime, timedelta
from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.constants import *
from DeveloperConsoleApp.utils import get_developer_console_settings

import sys
import json
import logging
import ipaddress
from django.contrib.sessions.models import Session

logger = logging.getLogger(__name__)


class IPAddressCheckMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def ip_address_in_given_range(self, start_ip_address, end_ip_address, check_ip_address):
        try:
            start_address = ipaddress.IPv4Address(start_ip_address)
            end_address = ipaddress.IPv4Address(end_ip_address)
            check_address = ipaddress.IPv4Address(check_ip_address)

            if check_address >= start_address and check_address <= end_address:
                return True
            else:
                return False
        except Exception:
            return False

    def check_path_is_blocked(self, request_path_info, blocked_request_path_list):
        for blocked_request_path in blocked_request_path_list:
            if request_path_info.startswith(blocked_request_path):
                return True
        return False

    def __call__(self, request):

        client_ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        request_path_info = request.META.get('PATH_INFO')

        config_obj = get_developer_console_settings()
        whitelisted_ip_address_list = config_obj.get_whitelisted_ip_addresses()
        
        whitelisted_request_path_list = settings.WHITELISTED_URLPATTERNS
        whitelisted_ips_for_blocked_urls = settings.WHITELISTED_IP_FOR_BLOCKED_URLS
        blocked_request_path_list = settings.BLOCKED_URLPATTERNS

        client_real_ip_address = client_ip_address
        if client_real_ip_address:
            client_real_ip_address = client_real_ip_address.split(',')[0]

        origin = request.META.get('HTTP_ORIGIN')
        if origin != None and settings.DEBUG == False and settings.CORS_ORIGIN_ALLOW_ALL == False:
            cors_origin_whitelist = settings.CORS_ORIGIN_WHITELIST
            origin = urlparse(origin)
            if origin.scheme + "://" + origin.netloc not in cors_origin_whitelist:
                return HttpResponse(status=401)

            if origin.path != "":
                return HttpResponse(status=401)

        if self.check_path_is_blocked(request_path_info, blocked_request_path_list):
            if client_real_ip_address not in whitelisted_ips_for_blocked_urls:
                return HttpResponse(status=401)

        if request_path_info not in whitelisted_request_path_list and len(whitelisted_ip_address_list) != 0:
            is_valid_user = False

            for ip_address in whitelisted_ip_address_list:

                if isinstance(ip_address, str) and ip_address == client_real_ip_address:
                    is_valid_user = True
                    break

                if isinstance(ip_address, tuple) and len(ip_address) == 2:
                    if self.ip_address_in_given_range(ip_address[0], ip_address[1], client_ip_address):
                        is_valid_user = True
                        break

            if not is_valid_user:
                return HttpResponse(status=401)

        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)

        return response


class AutoLogout(object):

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):

        # Can't log out if not logged in
        if not request.user.is_authenticated:
            response = self.get_response(request)
            return response

        try:
            # searching user session by session key
            user_session = UserSession.objects.filter(
                session_key=request.session.session_key)
            user = request.user

            if not user_session:
                # if user newly logged in then create UserSession object
                # for that user
                UserSession.objects.create(
                    session_key=request.session.session_key, user=user)
            else:
                # is user session object found for that perticular request session then
                # update last request datetime
                user_session = user_session[0]
                if user_session:
                    user_session.last_update_datetime = timezone.now()
                    user_session.save(update_fields=['last_update_datetime'])

            user.is_online = True
            user.save(update_fields=['is_online'])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AutoLogout %s at %s",
                         str(e), str(exc_tb.tb_lineno))

        response = self.get_response(request)
        return response
