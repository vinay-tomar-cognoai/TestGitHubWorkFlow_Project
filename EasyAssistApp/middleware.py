from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

import logging
import ipaddress

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

    def __call__(self, request):

        client_ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        request_path_info = request.META.get('PATH_INFO')
        whitelisted_ip_address_list = settings.WHITELISTED_IP_ADDRESSES
        whitelisted_request_path_list = settings.WHITELISTED_URLPATTERNS

        if request_path_info not in whitelisted_request_path_list and len(whitelisted_ip_address_list) != 0:

            is_valid_user = False

            for ip_address in whitelisted_ip_address_list:

                if isinstance(ip_address, str) and ip_address == client_ip_address:
                    is_valid_user = True
                    break

                if isinstance(ip_address, tuple) and len(ip_address) == 2 and self.ip_address_in_given_range(ip_address[0], ip_address[1], client_ip_address):
                    is_valid_user = True
                    break

            if not is_valid_user:
                return HttpResponse(status=401)

        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        # return HttpResponse(status=401)
        return response
