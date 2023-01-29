import sys
import json
import logging

# Django REST framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication

# Django imports
from django.shortcuts import render, HttpResponse, HttpResponseRedirect

from EasyChat import settings
from LiveChatApp.models import *
from LiveChatApp.constants import *
from LiveChatApp.utils import get_admin_config
from LiveChatApp.utils_validation import LiveChatInputValidation
from EasyChatApp.models import User

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


def LiveChatIntegrationsPage(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            if user_obj.status == "1":
                admin_config = get_admin_config(
                    user_obj, LiveChatAdminConfig, LiveChatUser)

                return render(request, 'LiveChatApp/livechat_integrations.html', {
                    "admin_config": admin_config,
                    "user_obj": user_obj,
                })
            else:
                return HttpResponse(AUTHORIZATION_DENIED)
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("LiveChatIntegrationsPage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


def MSDynamicsIntegrationPage(request):
    try:
        if request.user.is_authenticated:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            if user_obj.status == "1":
                integrations_obj = LiveChatIntegrations.objects.filter(
                    admin=user_obj)

                url = ''
                if integrations_obj and integrations_obj[0].ms_dynamics_config:

                    url = integrations_obj[0].ms_dynamics_config.integration_url

                admin_config = get_admin_config(
                    user_obj, LiveChatAdminConfig, LiveChatUser)

                return render(request, 'LiveChatApp/ms_integration.html', {
                    "admin_config": admin_config,
                    "user_obj": user_obj,
                    "url": url,
                })
            else:
                return HttpResponse(AUTHORIZATION_DENIED)
        else:
            return HttpResponseRedirect(CHAT_LOGIN_PATH)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("MSDynamicsIntegrationPage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect(CHAT_LOGIN_PATH)


class SaveLiveChatIntegrationsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def invalid_response(self, message, response):
        response["status"] = 400
        response["message"] = message
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            url = data['url']
            url = validation_obj.remo_html_from_string(url.strip())

            if (url == ''):
                return self.invalid_response('Microsoft Dynamics environment URL cannot be blank', response)

            if (not validation_obj.is_url(url)):
                return self.invalid_response('Please enter valid URL', response)

            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            if user_obj.status != '1':
                return self.invalid_response('You are not authorized to perform this operation', response)

            integrations_obj = LiveChatIntegrations.objects.filter(
                admin=user_obj)

            if not integrations_obj:
                integrations_obj = LiveChatIntegrations.objects.create(
                    admin=user_obj)
            else:
                integrations_obj = integrations_obj.first()

            if not integrations_obj.ms_dynamics_config:
                ms_dynamics_config = MSDynamicsIntegration.objects.create(
                    integration_url=url)
                integrations_obj.ms_dynamics_config = ms_dynamics_config
                integrations_obj.save()
            else:
                ms_dynamics_config = integrations_obj.ms_dynamics_config
                ms_dynamics_config.integration_url = url
                ms_dynamics_config.save()

            try:
                with open(f'{settings.MEDIA_ROOT}livechat_integrations/config.json', 'r') as config_file:
                    data = json.load(config_file)

                    data['ms_dynamics']['is_integrated'] = True
                    data['ms_dynamics']['CSRF_TRUSTED_ORIGINS'] = [url]

                with open(f'{settings.MEDIA_ROOT}livechat_integrations/config.json', 'w') as config_file:
                    json.dump(data, config_file)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Failed to write file: %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                return self.invalid_response('Failed to save configuration', response)

            response["status"] = 200
            response["message"] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveLiveChatIntegrationsAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveLiveChatIntegrations = SaveLiveChatIntegrationsAPI.as_view()


class DownloadMSIntegrationDocAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            user_obj = LiveChatUser.objects.get(
                user=User.objects.get(username=str(request.user.username)), is_deleted=False)

            export_path = None
            export_path_exist = None
            if user_obj.status == "1":
                export_path = "/files/livechat_integrations/MS_Dynamics_Integration.docx"
                export_path_exist = os.path.exists(export_path[1:])

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DownloadMSIntegrationDocAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DownloadMSIntegrationDoc = DownloadMSIntegrationDocAPI.as_view()
