from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.middleware import csrf
"""For user authentication"""
# Create your views here.
from EasyChatApp.models import User
from EasyAssistApp.models import *
from EasyAssistApp.utils import *
from EasyAssistApp.utils_proxy import *
from requests_html import HTMLSession

import sys
import json
import logging
import hashlib
import requests

logger = logging.getLogger(__name__)


@csrf_exempt
def CognoAICobrowse(request):

    try:
        if request.user.is_authenticated:
            return render(request, "EasyAssistApp/cognoai_cobrowse.html")
        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CognoAICobrowse %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)


class InitializeProxySessionAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            active_agent = get_active_agent_obj(
                request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            if active_agent.role == "agent" and access_token_obj.get_proxy_config_obj().enable_proxy_cobrowsing:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                website_url = remo_html_from_string(data["website_url"])
                customer_name = sanitize_input_string(data["customer_name"])
                customer_mobile_number = remo_special_tag_from_string(remo_html_from_string(
                    data["customer_mobile"]))
                customer_email_id = remo_html_from_string(
                    data["customer_email_id"])

                domain = urlparse(website_url).netloc
                if not access_token_obj.is_valid_domain(domain):
                    response["status"] = 305
                    response["message"] = "Unable to initiate co-browsing as domain is not whitelisted."
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                if not is_url_valid(website_url):
                    response["status"] = 301
                    response["message"] = "Please enter a valid website url."
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                if not check_valid_name(customer_name):
                    response["status"] = 304
                    response["message"] = "Please enter a valid customer name."
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                
                if not is_mobile_valid(customer_mobile_number):
                    response["status"] = 303
                    response["message"] = "Please enter a valid 10 digit mobile number."
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))
                
                if customer_email_id and not is_email_valid(customer_email_id):
                    response["status"] = 302
                    response["message"] = "Please enter a valid customer email id."
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                proxy_cobrowse_io = ProxyCobrowseIO.objects.create(
                    client_page_link=website_url)
                proxy_cobrowse_io.access_token = access_token_obj
                proxy_cobrowse_io.save()

                cobrowse_drop_link_obj = CobrowseDropLink.objects.create(
                    client_page_link=website_url,
                    agent=active_agent,
                    customer_name=customer_name,
                    customer_mobile=customer_mobile_number,
                    proxy_cobrowse_io=proxy_cobrowse_io)

                generated_link = settings.EASYCHAT_HOST_URL + \
                    "/easy-assist/cognoai-cobrowse/proxy-key/" + \
                    str(proxy_cobrowse_io.session_id)

                if customer_email_id:
                    cobrowse_drop_link_obj.customer_email = customer_email_id
                    cobrowse_drop_link_obj.save(update_fields=["customer_email"])
                cobrowse_drop_link_obj.generated_link = generated_link
                cobrowse_drop_link_obj.save(update_fields=["generated_link"])

                email_proxy_drop_link(
                    website_url, active_agent, customer_email_id, generated_link)

                response["status"] = 200
                response["message"] = "success"
                response["generated_link"] = generated_link
            else:
                response["status"] = 401
                response["message"] = "Invalid access"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error InitializeProxySessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


InitializeProxySession = InitializeProxySessionAPI.as_view()


def ProxyCobrowseSession(request, proxy_key):
    try:
        proxy_cobrowse_io = ProxyCobrowseIO.objects.filter(
            session_id=proxy_key).first()

        cobrowse_io = CobrowseIO.objects.filter(
            proxy_key_list__in=[proxy_key]).first()
        cobrowse_access_token_obj = proxy_cobrowse_io.access_token

        cobrowse_config_obj = get_developer_console_cobrowsing_settings()

        if proxy_cobrowse_io and not proxy_cobrowse_io.is_link_valid() and cobrowse_io and cobrowse_io.is_archived:
            return render(request, "EasyAssistApp/proxy_cobrowse_session_expire.html", {
                "logo": cobrowse_access_token_obj.source_easyassist_cobrowse_logo,
                "DEVELOPMENT": settings.DEVELOPMENT,
                "access_token": str(cobrowse_access_token_obj.key),
                "floating_button_bg_color": cobrowse_access_token_obj.floating_button_bg_color,
                "easyassist_font_family": cobrowse_io.access_token.font_family,
                "enable_s3_bucket": cobrowse_access_token_obj.agent.user.enable_s3_bucket,
                "cobrowse_config_obj": cobrowse_config_obj
            })

        response = render(request, "EasyAssistApp/proxy_cobrowse.html", {
            "proxy_cobrowse_io": proxy_cobrowse_io,
            "easychat_host_url": settings.EASYCHAT_HOST_URL,
            "access_token": proxy_cobrowse_io.access_token.key,
        })

        response.set_cookie("is_proxy_cobrowsing", "true", max_age=24 * 60 * 60, httponly=True)

        return response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ProxyCobrowseSession %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)


@csrf_exempt
def RenderProxyRequest(request, proxy_key, url_path):
    try:
        # proxy_cobrowse_io = ProxyCobrowseIO.objects.filter(
        #     session_id=proxy_key).first()
        
        # current_page_url = proxy_cobrowse_io.client_page_link

        """
        Example: url_path = https://getcogno.ai//https://cognoalhiring.hire.trakstar.com/
        We are not interested in the first domain which we have appended and hence we are 
        stripping apart.
        """

        logger.info("Proxy URL path (initial) === " + url_path, extra={'AppName': 'EasyAssist'})
        
        # change for POST request landing
        url_path = url_path.replace('"', "")
        
        if url_path.count("http") > 1:
            last_http_index = url_path.rfind("http")
            current_url = url_path[last_http_index:]
            url_path = current_url
        logger.info("Proxy URL path (after http strip) === " + url_path, extra={'AppName': 'EasyAssist'})
        current_page_domain = get_origin_from_url(url_path)
        if current_page_domain + "/" in url_path:
            url_path = url_path.replace(current_page_domain + "/", "")
        elif current_page_domain in url_path:
            url_path = url_path.replace(current_page_domain, "")
        logger.info("Proxy URL path before function call === " + url_path, extra={'AppName': 'EasyAssist'})
        logger.info("Proxy current page domain before function call === " + current_page_domain, extra={'AppName': 'EasyAssist'})
        url = get_absolute_link(current_page_domain, url_path)
        logger.info("Proxy absolute link for request === " + url, extra={'AppName': 'EasyAssist'})
        
        request_meta = request.META.copy()
        for request_meta_key, request_meta_value in request.META.items():
            if not isinstance(request_meta_value, str):
                request_meta.pop(request_meta_key)

        request_meta.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"})
        session = HTMLSession()

        if request.method == "GET":

            requested_data = [str(key) + "=" + str(value)
                              for key, value in request.GET.items()]
            requested_data = "&".join(requested_data)

            if len(requested_data) > 0:
                url = url + "?" + requested_data

            client_response = requests.get(
                url, headers=request_meta, timeout=30, verify=False)
        else:
            logger.info("Proxy POST request case triggered", extra={'AppName': 'EasyAssist'})
            request_data = request.POST
            try:
                request_data = json.loads(str(request.body, encoding='utf-8'))
            except Exception:
                pass
            client_response = session.post(
                url, headers=request_meta, data=request_data, timeout=30, verify=False)
        content = client_response.content

        content_type = "text/plain"
        try:
            content_type = client_response.headers["Content-Type"]
        except Exception:
            pass
        if not is_static_file_based_on_url(url):
            content = process_request_content(content, content_type, proxy_key, current_page_domain)
        
        response = HttpResponse(content, content_type=content_type)

        for cookie in client_response.cookies:
            '''
            Things exempted in set_cookie method - max_age, domain, httponly, samesite
            '''
            response.set_cookie(key=cookie.name, value=cookie.value, expires=cookie.expires, path=cookie.path,
                                secure=cookie.secure, httponly=True)

        # changes for POST request landing
        if current_page_domain[-1:] == "/":
            current_page_domain = current_page_domain[:-1]
        current_page_domain = current_page_domain.replace('"', "")
        response.set_cookie("proxy_key", proxy_key, max_age=24 * 60 * 60, httponly=True)
        response.set_cookie("current_active_url", current_page_domain, max_age=24 * 60 * 60, httponly=True)
        # changes end for POST request landing

        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error RenderProxyRequest: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(status=401)


class StartProxyCobrowsingAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            HTTP_USER_AGENT = None
            HTTP_X_FORWARDED_FOR = None
            if settings.ENABLE_IP_TRACKING:
                HTTP_X_FORWARDED_FOR = request.META["HTTP_X_FORWARDED_FOR"]
                HTTP_USER_AGENT = request.META["HTTP_USER_AGENT"]

            cobrowse_access_token_obj = get_cobrowse_access_token_obj(
                request, CobrowseAccessToken)

            if cobrowse_access_token_obj == None:
                return Response(status=401)
            else:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                proxy_key = data["proxy_key"]
                longitude = data["longitude"]
                latitude = data["latitude"]
                meta_data = data["meta_data"]

                proxy_key = remo_html_from_string(proxy_key)
                longitude = remo_html_from_string(str(longitude))
                latitude = remo_html_from_string(str(latitude))

                cobrowse_drop_link_obj = None

                try:
                    cobrowse_drop_link_obj = CobrowseDropLink.objects.filter(
                        proxy_cobrowse_io__session_id=proxy_key).first()
                except Exception:
                    pass

                if cobrowse_drop_link_obj:
                    name = cobrowse_drop_link_obj.customer_name
                    mobile_number = cobrowse_drop_link_obj.customer_mobile
                    agent_selected = cobrowse_drop_link_obj.agent

                    primary_id = hashlib.md5(
                        mobile_number.encode()).hexdigest()

                    request_meta_details = {
                        "HTTP_USER_AGENT": HTTP_USER_AGENT,
                        "HTTP_X_FORWARDED_FOR": HTTP_X_FORWARDED_FOR
                    }

                    cobrowse_io = cobrowse_drop_link_obj.cobrowse_io

                    if cobrowse_io == None:

                        cobrowse_io = CobrowseIO.objects.create(full_name=name,
                                                                mobile_number=mobile_number,
                                                                share_client_session=False,
                                                                primary_value=primary_id)

                        if "product_details" in meta_data and "title" in meta_data["product_details"]:
                            cobrowse_io.title = strip_html_tags(meta_data[
                                "product_details"]["title"].strip())

                        if "product_details" in meta_data and "url" in meta_data["product_details"]:
                            cobrowse_io.active_url = meta_data[
                                "product_details"]["url"].strip()

                        if "product_details" in meta_data and "description" in meta_data["product_details"]:
                            meta_data["product_details"]["description"] = strip_html_tags(meta_data[
                                "product_details"]["description"].strip())

                        meta_data = json.dumps(meta_data)
                        meta_data = custom_encrypt_obj.encrypt(meta_data)
                        cobrowse_io.meta_data = meta_data
                        cobrowse_io.is_active = True
                        cobrowse_io.last_update_datetime = timezone.now()
                        cobrowse_io.is_agent_connected = False
                        cobrowse_io.cobrowsing_start_datetime = None
                        cobrowse_io.latitude = str(latitude)
                        cobrowse_io.longitude = str(longitude)

                        cobrowse_io.is_lead = False
                        cobrowse_io.access_token = cobrowse_access_token_obj
                        cobrowse_io.request_meta_details = json.dumps(
                            request_meta_details)
                        cobrowse_io.agent = agent_selected
                        if cobrowse_access_token_obj.show_verification_code_modal == False:
                            cobrowse_io.allow_agent_cobrowse = "true"
                        else:
                            otp = random_with_n_digits(4)
                            cobrowse_io.otp_validation = otp
                            cobrowse_io.agent_assistant_request_status = True
                            cobrowse_io.is_agent_request_for_cobrowsing = True

                        cobrowse_io.cobrowsing_type = "outbound-proxy-cobrowsing"
                        cobrowse_io.is_meeting_only_session = False
                        cobrowse_io.proxy_key_list.add(
                            cobrowse_drop_link_obj.proxy_cobrowse_io)
                        cobrowse_io.save()

                        cobrowse_drop_link_obj.cobrowse_io = cobrowse_io
                        cobrowse_drop_link_obj.save(update_fields=["cobrowse_io"])

                        send_agent_customer_connected_notification(
                            agent_selected, cobrowse_io)

                    response["session_id"] = str(cobrowse_io.session_id)
                    response["status"] = 200
                    response["message"] = "success"
                    response["csrf"] = csrf.get_token(request)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error StartProxyCobrowsingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


StartProxyCobrowsing = StartProxyCobrowsingAPI.as_view()


class AddNewProxySessionTabAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            active_agent = get_active_agent_obj(request, CobrowseAgent)
            access_token_obj = active_agent.get_access_token_obj()

            if active_agent.role == "agent" and access_token_obj.get_proxy_config_obj().enable_proxy_cobrowsing:
                data = request.data["Request"]
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                website_url = remo_html_from_string(data["website_url"])
                session_id = strip_html_tags(data["session_id"])
                cobrowse_io_obj = CobrowseIO.objects.filter(
                    session_id=session_id).first()

                if not cobrowse_io_obj:
                    response["status"] = 301
                    response["message"] = "No session data is present."
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                if not is_url_valid(website_url):
                    response["status"] = 301
                    response["message"] = "Please enter a valid website link."
                    return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))

                proxy_cobrowse_io = ProxyCobrowseIO.objects.create(
                    client_page_link=website_url)
                proxy_cobrowse_io.access_token = access_token_obj
                generated_link = settings.EASYCHAT_HOST_URL + \
                    "/easy-assist/cognoai-cobrowse/proxy-key/" + \
                    str(proxy_cobrowse_io.session_id)
                proxy_cobrowse_io.save()
                cobrowse_io_obj.proxy_key_list.add(
                    proxy_cobrowse_io.session_id)
                cobrowse_io_obj.save(update_fields=['proxy_key_list'])

                response["status"] = 200
                response["message"] = "Success"
                response["generated_link"] = generated_link
            else:
                response["status"] = 401
                response["message"] = "Invalid access"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddNewProxySessionTabAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


AddNewProxySessionTab = AddNewProxySessionTabAPI.as_view()


def ProxyCobrowseSessionExpired(request):
    cobrowse_config_obj = get_developer_console_cobrowsing_settings()
    cobrowse_access_token_obj = get_cobrowse_access_token_obj(
        request, CobrowseAccessToken)
    return render(request, "EasyAssistApp/proxy_cobrowse_session_expire.html", {
        "logo": cobrowse_access_token_obj.source_easyassist_cobrowse_logo,
        "DEVELOPMENT": settings.DEVELOPMENT,
        "access_token": str(cobrowse_access_token_obj.key),
        "floating_button_bg_color": cobrowse_access_token_obj.floating_button_bg_color,
        "easyassist_font_family": cobrowse_access_token_obj.font_family,
        "enable_s3_bucket": cobrowse_access_token_obj.agent.user.enable_s3_bucket,
        "cobrowse_config_obj": cobrowse_config_obj
    })


def ProxyCobrowseSessionEnd(request):
    cobrowse_config_obj = get_developer_console_cobrowsing_settings()
    return render(request, "EasyAssistApp/proxy_session_end.html", {
        "DEVELOPMENT": settings.DEVELOPMENT,
        "cobrowse_config_obj": cobrowse_config_obj
    })


class ProxyCobrowseDebugAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            logger.info("=============== PROXY NEW REQUEST ===============",
                        extra={'AppName': 'EasyAssist'})
            logger.info("Received request type === " +
                        str(request.method), extra={'AppName': 'EasyAssist'})
            logger.info("Printing received headers",
                        extra={'AppName': 'EasyAssist'})

            for header_name, header_value in request.META.items():
                logger.info("Header name === " + str(header_name) + " header value === " +
                            str(header_value), extra={'AppName': 'EasyAssist'})

            logger.info("Printing received cookies",
                        extra={'AppName': 'EasyAssist'})

            for cookie_name, cookie_value in request.COOKIES.items():
                logger.info("Cookie name === " + str(cookie_name) + " cookie value === " +
                            str(cookie_value), extra={'AppName': 'EasyAssist'})

            if request.method == "POST":
                request_data = request.POST
                try:
                    request_data = json.loads(
                        str(request.body, encoding='utf-8'))
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("Error occurred while parsing received POST request data = %s at %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                logger.info("Received request data === " +
                            str(request_data), extra={'AppName': 'EasyAssist'})

            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ProxyCobrowseDebugAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return Response(data=get_encrypted_response_packet(response, custom_encrypt_obj))


ProxyCobrowseDebug = ProxyCobrowseDebugAPI.as_view()
