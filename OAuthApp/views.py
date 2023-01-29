from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import login, logout, get_user_model
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

from OAuthApp.models import REMOTE_ACCESS_URL, REMOTE_ACCESS_IP_ADDRESSES, CentralizedAccessToken
from OAuthApp.utils import generate_password, allow_incoming_request, CustomEncrypt, custom_request_decrypt

from ast import literal_eval
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

from django.apps import apps

import sys
import json
import requests
import logging
import uuid


logger = logging.getLogger(__name__)

User = get_user_model()


def oauth_validation(request):
    try:
        access_token = request.GET["access_token"]
        access_token_obj = CentralizedAccessToken.objects.get(
            session_id=access_token, is_expired=False)

        validation_token = access_token_obj.validation_token

        custom_encrypt_obj = CustomEncrypt()
        request_packet = json.dumps(
            {"validation_token": validation_token, "access_token": access_token})

        encrypted_response = custom_encrypt_obj.encrypt(request_packet)
        request_packet = {"Request": encrypted_response}

        validate_token_response = requests.post(url=REMOTE_ACCESS_URL + "/remote-access/oauth/validation/",
                                                data=json.dumps(request_packet), headers={"Content-Type": "application/json"})

        json_response = json.loads(validate_token_response.text)
        json_response = custom_request_decrypt(json_response)

        access_token_obj.is_expired = True
        access_token_obj.save()

        if json_response["status"] == 200:

            user = None
            admin_login = False
            superuser_login = False
            admin_username = ""
            try:

                admin_login = json_response["admin_login"]
                superuser_login = json_response["superuser_login"]

                user = User.objects.get(username=access_token_obj.user_id)

                if admin_login == True:
                    admin_username = json_response["admin_username"]
                    user = User.objects.get(username=admin_username)

                if superuser_login == True:
                    user.is_superuser = True
                else:
                    user.is_superuser = False

            except Exception:
                user = User.objects.create(username=access_token_obj.user_id, is_staff=True, is_bot_invocation_enabled=True,
                                           is_superuser=False, role="bot_builder", status="1", is_chatbot_creation_allowed="1")

                if admin_login == True:
                    admin_username = json_response["admin_username"]
                    user = User.objects.get(username=admin_username)
                    user.is_staff = True

                if superuser_login == True:
                    user.is_superuser = True
                else:
                    user.is_superuser = False

            if user.username.endswith("@allincall.in") or user.username.endswith("getcogno.ai"):
                user.is_staff = True
                user.save()

            user.set_password(generate_password(
                "CognoAI") + str(uuid.uuid4()))
            user.save()

            try:
                audit_trail_data = json.dumps({
                    "original_user": json_response["original_user"],
                    "admin_username": json_response["admin_username"],
                    "admin_login": json_response["admin_login"],
                    "superuser_login": json_response["superuser_login"]
                })

                from EasyChatApp.models import AuditTrail
                USER_LOGGED_IN = "6"
                AuditTrail.objects.create(
                    user=user, action=USER_LOGGED_IN, data=audit_trail_data)

                from AuditTrailApp.utils import add_audit_trail
                add_audit_trail(
                    "OAUTHApp",
                    user,
                    "Login",
                    "Loggin Activity",
                    audit_trail_data,
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error AuditTrailApp error %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'OAuthApp'})
                pass

            if user != None:
                login(request, user,
                      backend='django.contrib.auth.backends.ModelBackend')
                user.is_online = True
                user.save()
                return redirect("/chat/login/")
            else:
                return HttpResponse(status=403)
        else:
            return HttpResponse(status=403)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error ClientConsoleOAuthAPI %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'OAuthApp'})

    return HttpResponse(status=403)


class ClientConsoleOAuthAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data
            data = custom_request_decrypt(data)

            client_ip_addresses = request.META.get("HTTP_X_FORWARDED_FOR")

            if client_ip_addresses:
                client_ip_addresses = client_ip_addresses.split(',')

            common_addresses = list(
                set(REMOTE_ACCESS_IP_ADDRESSES) & set(client_ip_addresses))

            if len(common_addresses) != 0:

                user_id = data["user_id"]

                validation_token = data["validation_token"]

                CentralizedAccessToken.objects.filter(user_id=user_id).delete()

                access_token = CentralizedAccessToken.objects.create(
                    user_id=user_id, validation_token=validation_token)

                response["status"] = 200
                response["message"] = "success"
                response["token"] = str(access_token.session_id)
            else:
                response["status"] = 401
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ClientConsoleOAuthAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'OAuthApp'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}

        return Response(data=response)


class RemoveAccessAPI(APIView):

    def post(self, request, *args, **kwargs):
        if allow_incoming_request(request) == False:
            return HttpResponse(status=403)

        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            for user in User.objects.filter(is_staff=True):
                user.user_permissions.clear()
                user.is_superuser = False
                user.save()

            for user in User.objects.filter(is_superuser=True):
                user.user_permissions.clear()
                user.is_superuser = False
                user.save()

            response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RemoveAccessAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'OAuthApp'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}

        return Response(data=response)


class GetModelNamesAPI(APIView):

    def post(self, request, *args, **kwargs):
        if allow_incoming_request(request) == False:
            return HttpResponse(status=403)
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            models = [(model._meta.app_label + "." + model.__name__)
                      for model in apps.get_models()]

            response["all_models"] = models
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RemoveAccessAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'OAuthApp'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}

        return Response(data=response)


class ModelAccessAPI(APIView):

    def post(self, request, *args, **kwargs):
        if allow_incoming_request(request) == False:
            return HttpResponse(status=403)
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:

            data = request.data
            data = custom_request_decrypt(data)
            model_list = data["model_list"]
            username = data["username"]

            user = User.objects.get(username=username)
            models = {(model._meta.app_label + "." + model.__name__): model for model in apps.get_models()}
            for item in model_list:
                content_type = ContentType.objects.get_for_model(models[item])
                permission = Permission.objects.filter(
                    content_type=content_type)
                for perm in permission:
                    user.user_permissions.add(perm)
                    user.save()
            response["status"] = 200

        except Exception as e:
            response["status_message"] = str(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ModelAccess %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'OAuthApp'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}

        return Response(data=response)


ClientConsoleOAuth = ClientConsoleOAuthAPI.as_view()

RemoveAccess = RemoveAccessAPI.as_view()

GetModelNamesAPI = GetModelNamesAPI.as_view()

ModelAccess = ModelAccessAPI.as_view()
