from django.shortcuts import render, HttpResponse, redirect

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from DeveloperConsoleApp.models import *
from DeveloperConsoleApp.constants import *

from DeveloperConsoleApp.utils import *

from EasyChatApp.models import User, DecryptVariable, CustomEncrypt
from AuditTrailApp.models import CognoAIAuditTrail
from AuditTrailApp.utils import add_audit_trail

import sys
import pytz
import time
import json
import logging
import datetime

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def DeveloperSettings(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        config_obj = get_developer_console_settings()

        # user = User.objects.get(username=request.user.username)
        return render(request, "DeveloperConsoleApp/developer_settings.html", {"config_obj": config_obj})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error DeveloperSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        return HttpResponse(INVALID_ACCESS_CONSTANT)


def WhitelableChatbotPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)

        if user.enable_white_label_option:

            audit_trail_obj = CognoAIAuditTrail.objects.filter(app_name="DEVELOPERCONSOLEAPP", action_type="Edit-White-Labeling-Config").order_by("-pk").first()
            time_diff_str = ""

            if audit_trail_obj:
                time_diff_str = get_human_readable_time_difference(datetime.datetime.now(datetime.timezone.utc), audit_trail_obj.datetime)

            easychatapp_config_obj = get_developer_console_easychat_settings()

            chatbot_logo_name = easychatapp_config_obj.chatbot_logo.split("/")[-1]
            chatbot_tab_icon_name = easychatapp_config_obj.tab_logo.split("/")[-1]

            return render(request, "DeveloperConsoleApp/chatbot.html", {
                "audit_trail_obj": audit_trail_obj,
                "time_diff_str": time_diff_str,
                "easychatapp_config_obj": easychatapp_config_obj,
                "chatbot_logo_name": chatbot_logo_name,
                "chatbot_tab_icon_name": chatbot_tab_icon_name
            })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error DeveloperSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def WhitelableGeneralPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        config_obj = get_developer_console_settings()

        user = User.objects.get(username=request.user.username)

        if user.enable_white_label_option:

            audit_trail_obj = CognoAIAuditTrail.objects.filter(app_name="DEVELOPERCONSOLEAPP", action_type="Edit-White-Labeling-Config").order_by("-pk").first()
            time_diff_str = ""

            if audit_trail_obj:
                time_diff_str = get_human_readable_time_difference(datetime.datetime.now(datetime.timezone.utc), audit_trail_obj.datetime)

            login_logo_name = config_obj.login_logo.split("/")[-1]
            general_page_logo_name = config_obj.general_page_logo.split("/")[-1]
            general_favicon_name = config_obj.general_favicon.split("/")[-1]

            return render(request, "DeveloperConsoleApp/general.html", {
                "config_obj": config_obj,
                "audit_trail_obj": audit_trail_obj,
                "time_diff_str": time_diff_str,
                "login_logo_name": login_logo_name,
                "general_page_logo_name": general_page_logo_name,
                "general_favicon_name": general_favicon_name
            })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error DeveloperSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def WhitelableCobrowsePage(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)

        if user.enable_white_label_option:

            audit_trail_obj = CognoAIAuditTrail.objects.filter(app_name="DEVELOPERCONSOLEAPP", action_type="Edit-White-Labeling-Config").order_by("-pk").first()
            time_diff_str = ""

            if audit_trail_obj:
                time_diff_str = get_human_readable_time_difference(datetime.datetime.now(datetime.timezone.utc), audit_trail_obj.datetime)

            cobrowsing_config_obj = get_developer_console_cobrowsing_settings()
            cobrowsing_logo_name = cobrowsing_config_obj.cobrowsing_logo.split('/')[-1]
            cobrowsing_favicon_name = cobrowsing_config_obj.cobrowsing_favicon.split('/')[-1]
            email_id_list = json.loads(cobrowsing_config_obj.cobrowsing_masking_pii_data_otp_email)
            
            return render(request, "DeveloperConsoleApp/cobrowse.html", {
                "audit_trail_obj": audit_trail_obj,
                "time_diff_str": time_diff_str,
                "cobrowsing_config_obj": cobrowsing_config_obj,
                "cobrowsing_logo_name": cobrowsing_logo_name,
                "cobrowsing_favicon_name": cobrowsing_favicon_name,
                "email_id_list": email_id_list
            })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error DeveloperSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def WhitelableLiveChatPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)

        if user.enable_white_label_option:
            
            audit_trail_obj = CognoAIAuditTrail.objects.filter(app_name="DEVELOPERCONSOLEAPP", action_type="Edit-White-Labeling-Config").order_by("-pk").first()
            time_diff_str = ""

            if audit_trail_obj:
                time_diff_str = get_human_readable_time_difference(datetime.datetime.now(datetime.timezone.utc), audit_trail_obj.datetime)

            livechat_config_obj = get_developer_console_livechat_settings()
            email_list = json.loads(livechat_config_obj.livechat_masking_pii_data_otp_email)
            livechat_logo_name = livechat_config_obj.livechat_logo.split('/')[-1]
            livechat_favicon_name = livechat_config_obj.livechat_favicon.split('/')[-1]

            return render(request, "DeveloperConsoleApp/livechat.html", {
                "livechat_config_obj": livechat_config_obj,
                "email_list": email_list,
                "livechat_logo_name": livechat_logo_name,
                "livechat_favicon_name": livechat_favicon_name,
                "audit_trail_obj": audit_trail_obj,
                "time_diff_str": time_diff_str
            })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error DeveloperSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def WhitelableCognoDeskPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)

        if user.enable_white_label_option:

            audit_trail_obj = CognoAIAuditTrail.objects.filter(app_name="DEVELOPERCONSOLEAPP", action_type="Edit-White-Labeling-Config").order_by("-pk").first()
            time_diff_str = ""

            if audit_trail_obj:
                time_diff_str = get_human_readable_time_difference(datetime.datetime.now(datetime.timezone.utc), audit_trail_obj.datetime)

            cognodesk_config_obj = get_developer_console_cognodesk_settings()

            cognodesk_logo_name = cognodesk_config_obj.chatbot_logo.split("/")[-1]
            cognadesk_tab_icon_name = cognodesk_config_obj.tab_logo.split("/")[-1]

            return render(request, "DeveloperConsoleApp/cognodesk.html", {
                "audit_trail_obj": audit_trail_obj,
                "time_diff_str": time_diff_str,
                "cognodesk_logo_name": cognodesk_logo_name,
                "cognadesk_tab_icon_name": cognadesk_tab_icon_name
            })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error DeveloperSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


def WhitelableCognoMeetPage(request):
    try:
        if not request.user.is_authenticated:
            return redirect(REDIRECT_LOGIN_PATH)

        user = User.objects.get(username=request.user.username)

        if user.enable_white_label_option:
            audit_trail_obj = CognoAIAuditTrail.objects.filter(app_name="DEVELOPERCONSOLEAPP", action_type="Edit-White-Labeling-Config").order_by("-pk").first()
            time_diff_str = ""

            if audit_trail_obj:
                time_diff_str = get_human_readable_time_difference(datetime.datetime.now(datetime.timezone.utc), audit_trail_obj.datetime)

            cognomeet_config_obj = get_developer_console_cognomeet_settings()
            cognomeet_logo_name = cognomeet_config_obj.cognomeet_logo.split('/')[-1]
            cognomeet_favicon_name = cognomeet_config_obj.cognomeet_favicon.split('/')[-1]
            
            return render(request, "DeveloperConsoleApp/cognomeet.html", {
                "audit_trail_obj": audit_trail_obj,
                "time_diff_str": time_diff_str,
                "cognomeet_config_obj": cognomeet_config_obj,
                "cognomeet_logo_name": cognomeet_logo_name,
                "cognomeet_favicon_name": cognomeet_favicon_name
            })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error DeveloperSettings %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

    return HttpResponse(INVALID_ACCESS_CONSTANT)


class SaveGeneralWhitelabelSettingsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)

            if not user.enable_white_label_option:
                response["message"] = "Invalid Access"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            is_reset = data["reset"].lower()
            reset_type = data["reset_type"].lower()

            config_obj = get_developer_console_settings()

            if is_reset == "false":
                general_logo = data["general_logo"]
                general_page_logo = data["general_page_logo"]
                general_primary_color = data["general_primary_color"]
                general_secondary_color = data["general_secondary_color"]
                hide_login_with_gsuite_button = data[
                    "hide_login_with_gsuite_button"]
                disabled_multifactor_authentication_button = data["disabled_multifactor_authentication_button"]
                general_favicon = data["general_favicon"]
                smtp_email_id = data["smtp_email_id"]
                smtp_email_password = data["smtp_email_password"]
                replace_name_over_entire_console = data[
                    "replace_name_over_entire_console"]
                general_email_signature = data["general_email_signature"]
                enable_footer_over_entire_console = data[
                    "enable_footer_over_entire_console"]
                legal_name = data["legal_name"]
                general_title = data["general_title"]

                config_obj.login_logo = general_logo
                config_obj.general_page_logo = general_page_logo
                config_obj.primary_color = general_primary_color
                config_obj.secondary_color = general_secondary_color
                config_obj.hide_login_with_gsuite = hide_login_with_gsuite_button
                config_obj.disabled_multifactor_authentication = disabled_multifactor_authentication_button
                config_obj.general_favicon = general_favicon
                config_obj.email_host_user = smtp_email_id
                config_obj.email_host_password = smtp_email_password
                config_obj.replace_easychat_over_console = replace_name_over_entire_console
                config_obj.custom_report_template_signature = general_email_signature
                config_obj.enable_footer_over_entire_console = enable_footer_over_entire_console
                config_obj.legal_name = legal_name
                config_obj.general_title = general_title
            
            elif is_reset == "true" and reset_type == "general-login-logo":
                config_obj.login_logo = GENERAL_LOGIN_LOGO

            elif is_reset == "true" and reset_type == "general-favicon-logo":
                config_obj.general_favicon = GENERAL_FAVICON
            
            elif is_reset == "true" and reset_type == "general-primary-color":
                config_obj.primary_color = CONSOLE_PRIMARY_COLOR
            
            elif is_reset == "true" and reset_type == "general-secondary-color":
                config_obj.secondary_color = CONSOLE_SECONDARY_COLOR
            
            elif is_reset == "true" and reset_type == "general-page-logo":
                config_obj.general_page_logo = GENERAL_PAGE_LOGO

            config_obj.save()

            description = "{} changed White Labeling Configurations.".format(user.username)

            add_audit_trail(
                "DEVELOPERCONSOLEAPP",
                user,
                "Edit-White-Labeling-Config",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveGeneralWhitelabelSettingsAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveGeneralWhitelabelSettings = SaveGeneralWhitelabelSettingsAPI.as_view()


class SaveLiveChatWhitelabelSettingsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)

            if not user.enable_white_label_option:
                response["message"] = "Invalid Access"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            livechat_console_logo = data["livechat_console_logo"]
            livechat_console_favicon = data["livechat_console_favicon"]
            livechat_console_title = data["livechat_console_title"]
            email_address = data["email_address"]

            livechat_config_obj = get_developer_console_livechat_settings()

            livechat_config_obj.livechat_logo = livechat_console_logo
            livechat_config_obj.livechat_favicon = livechat_console_favicon
            livechat_config_obj.livechat_title = livechat_console_title
            livechat_config_obj.livechat_masking_pii_data_otp_email = json.dumps(
                email_address)
            livechat_config_obj.save()

            description = "{} changed White Labeling LiveChat Configurations.".format(user.username)

            add_audit_trail(
                "DEVELOPERCONSOLEAPP",
                user,
                "Edit-White-Labeling-Config",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveLiveChatWhitelabelSettingsAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveLiveChatWhitelabelSettings = SaveLiveChatWhitelabelSettingsAPI.as_view()


class ResetLiveChatWhitelabelSettingsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)

            if not user.enable_white_label_option:
                response["message"] = "Invalid Access"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            setting_type = data["setting_type"]
            livechat_config_obj = get_developer_console_livechat_settings()

            if setting_type == 'logo':
                livechat_config_obj.livechat_logo = DEFAULT_LIVECHAT_LOGO_PATH
                livechat_config_obj.save()
                response["src"] = DEFAULT_LIVECHAT_LOGO_PATH
                response["filename"] = DEFAULT_LIVECHAT_LOGO_PATH.split(
                    '/')[-1]

            elif setting_type == 'favicon':
                livechat_config_obj.livechat_favicon = DEFAULT_LIVECHAT_FAVICON_PATH
                livechat_config_obj.save()
                response["src"] = DEFAULT_LIVECHAT_FAVICON_PATH
                response["filename"] = DEFAULT_LIVECHAT_FAVICON_PATH.split(
                    '/')[-1]

            description = "{} reset livechat white labeling logo configurations.".format(user.username)

            add_audit_trail(
                "DEVELOPERCONSOLEAPP",
                user,
                "Edit-White-Labeling-Config",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ResetLiveChatWhitelabelSettingsAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ResetLiveChatWhitelabelSettings = ResetLiveChatWhitelabelSettingsAPI.as_view()


class SaveCobrowsingWhitelabelSettingsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)

            if not user.enable_white_label_option:
                response["message"] = "Invalid Access"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            cobrowse_console_logo = data["cobrowse_console_logo"]
            cobrowse_console_favicon = data["cobrowse_console_favicon"]
            cobrowse_console_title = data["cobrowse_console_title"]
            masking_pii_email_ids = data["masking_pii_email_ids"]

            cobrowsing_config_obj = get_developer_console_cobrowsing_settings()

            cobrowsing_config_obj.cobrowsing_logo = cobrowse_console_logo
            cobrowsing_config_obj.cobrowsing_favicon = cobrowse_console_favicon
            cobrowsing_config_obj.cobrowsing_title_text = cobrowse_console_title
            cobrowsing_config_obj.cobrowsing_masking_pii_data_otp_email = json.dumps(masking_pii_email_ids)
            cobrowsing_config_obj.save()

            description = "{} changed White Labeling Cobrowse Configurations.".format(user.username)

            add_audit_trail(
                "DEVELOPERCONSOLEAPP",
                user,
                "Edit-White-Labeling-Config",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCobrowsingWhitelabelSettingsAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveCobrowsingWhitelabelSettings = SaveCobrowsingWhitelabelSettingsAPI.as_view()


class ResetCobrowseWhitelabelSettingsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)

            if not user.enable_white_label_option:
                response["message"] = "Invalid Access"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            setting_type = data["setting_type"]
            
            cobrowsing_config_obj = get_developer_console_cobrowsing_settings()

            if setting_type == 'logo':
                cobrowsing_config_obj.cobrowsing_logo = DEFAULT_COBROWSING_LOGO
                cobrowsing_config_obj.save()
                response["src"] = DEFAULT_COBROWSING_LOGO
                response["filename"] = DEFAULT_COBROWSING_LOGO.split(
                    '/')[-1]

            elif setting_type == 'favicon':
                cobrowsing_config_obj.cobrowsing_favicon = DEFAULT_COBROWSING_TAB_LOGO
                cobrowsing_config_obj.save()
                response["src"] = DEFAULT_COBROWSING_TAB_LOGO
                response["filename"] = DEFAULT_COBROWSING_TAB_LOGO.split(
                    '/')[-1]

            description = "{} reset Cobrowse White Labeling logo configurations.".format(user.username)

            add_audit_trail(
                "DEVELOPERCONSOLEAPP",
                user,
                "Edit-White-Labeling-Config",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ResetCobrowseWhitelabelSettingsAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ResetCobrowseWhitelabelSettings = ResetCobrowseWhitelabelSettingsAPI.as_view()


class SaveCognoMeetWhitelabelSettingsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)

            if not user.enable_white_label_option:
                response["message"] = "Invalid Access"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            cognomeet_console_logo = data["cognomeet_console_logo"]
            cognomeet_console_favicon = data["cognomeet_console_favicon"]
            cognomeet_console_title = data["cognomeet_console_title"]

            cognomeet_config_obj = get_developer_console_cognomeet_settings()

            cognomeet_config_obj.cognomeet_logo = cognomeet_console_logo
            cognomeet_config_obj.cognomeet_favicon = cognomeet_console_favicon
            cognomeet_config_obj.cognomeet_title_text = cognomeet_console_title
            cognomeet_config_obj.save()

            description = "{} changed White Labeling Cogno Meet Configurations.".format(user.username)

            add_audit_trail(
                "DEVELOPERCONSOLEAPP",
                user,
                "Edit-White-Labeling-Config",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCognoMeetWhitelabelSettingsAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveCognoMeetWhitelabelSettings = SaveCognoMeetWhitelabelSettingsAPI.as_view()


class ResetCognoMeetWhitelabelSettingsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)

            if not user.enable_white_label_option:
                response["message"] = "Invalid Access"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            setting_type = data["setting_type"]
            
            cognomeet_config_obj = get_developer_console_cognomeet_settings()

            if setting_type == 'logo':
                cognomeet_config_obj.cognomeet_logo = DEFAULT_COGNOMEET_LOGO
                cognomeet_config_obj.save()
                response["src"] = DEFAULT_COGNOMEET_LOGO
                response["filename"] = DEFAULT_COGNOMEET_LOGO.split(
                    '/')[-1]

            elif setting_type == 'favicon':
                cognomeet_config_obj.cognomeet_favicon = DEFAULT_COGNOMEET_TAB_LOGO
                cognomeet_config_obj.save()
                response["src"] = DEFAULT_COGNOMEET_TAB_LOGO
                response["filename"] = DEFAULT_COGNOMEET_TAB_LOGO.split(
                    '/')[-1]

            description = "{} reset Cogno Meet White Labeling logo configurations.".format(user.username)

            add_audit_trail(
                "DEVELOPERCONSOLEAPP",
                user,
                "Edit-White-Labeling-Config",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ResetCognoMeetWhitelabelSettingsAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ResetCognoMeetWhitelabelSettings = ResetCognoMeetWhitelabelSettingsAPI.as_view()


class SaveEasyChatAppWhiteLabelSettingsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)

            if not user.enable_white_label_option:
                response["message"] = "Invalid Access"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            easychatapp_config_obj = get_developer_console_easychat_settings()
            config_obj = get_developer_console_settings()

            is_reset = data["reset"].lower()
            reset_type = data["reset_type"].lower()

            if is_reset == "false":
                easychatapp_config_obj.chatbot_logo = str(data["chatbot_logo"])
                easychatapp_config_obj.tab_logo = str(data["tab_logo"])
                easychatapp_config_obj.title_text = str(data["title_text"])
                easychatapp_config_obj.disable_show_brand_name = data["disable_show_brand_name"]
                config_obj.masking_pii_data_otp_email = json.dumps(data["masking_pii_email_ids"])

            elif is_reset == "true" and reset_type == "easychat-logo":
                easychatapp_config_obj.chatbot_logo = DEFAULT_CHATBOT_LOGO

            elif is_reset == "true" and reset_type == "easychat-tab-logo":
                easychatapp_config_obj.tab_logo = DEFAULT_CHATBOT_TAB_LOGO

            elif is_reset == "true" and reset_type == "all":
                easychatapp_config_obj.chatbot_logo = DEFAULT_CHATBOT_LOGO
                easychatapp_config_obj.tab_logo = DEFAULT_CHATBOT_TAB_LOGO
                easychatapp_config_obj.title_text = DEFAULT_CHATBOT_TITLE_TEXT
                easychatapp_config_obj.disable_show_brand_name = False
                config_obj.masking_pii_data_otp_email = json.dumps(MASKING_PII_DATA_OTP_EMAIL)

            easychatapp_config_obj.save()
            config_obj.save()

            description = "{} changed White Labeling EasyChat Configurations.".format(user.username)

            add_audit_trail(
                "DEVELOPERCONSOLEAPP",
                user,
                "Edit-White-Labeling-Config",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

            response["status"] = 200
            response["message"] = "Success"
            
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveEasyChatAppWhiteLabelSettingsAPI : %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)        

SaveEasyChatAppWhiteLabelSettings = SaveEasyChatAppWhiteLabelSettingsAPI.as_view()


class SaveCognoDeskAppWhiteLabelSettingsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            user = User.objects.get(username=request.user.username)

            if not user.enable_white_label_option:
                response["message"] = "Invalid Access"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            cognodesk_config_obj = get_developer_console_cognodesk_settings()

            is_reset = data["reset"].lower()
            reset_type = data["reset_type"].lower()

            if is_reset == "false":
                cognodesk_config_obj.chatbot_logo = str(data["chatbot_logo"])
                cognodesk_config_obj.tab_logo = str(data["tab_logo"])
                cognodesk_config_obj.title_text = str(data["title_text"])

            elif is_reset == "true" and reset_type == "cognodesk-logo":
                cognodesk_config_obj.chatbot_logo = DEFAULT_DESK_LOGO

            elif is_reset == "true" and reset_type == "cognodesk-tab-logo":
                cognodesk_config_obj.tab_logo = DEFAULT_DESK_TAB_LOGO

            elif is_reset == "true" and reset_type == "all":
                cognodesk_config_obj.chatbot_logo = DEFAULT_DESK_LOGO
                cognodesk_config_obj.tab_logo = DEFAULT_DESK_TAB_LOGO
                cognodesk_config_obj.title_text = DEFAULT_DESK_TITLE_TEXT

            cognodesk_config_obj.save()

            description = "{} changed White Labeling Cogno Desk Configurations.".format(user.username)

            add_audit_trail(
                "DEVELOPERCONSOLEAPP",
                user,
                "Edit-White-Labeling-Config",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

            response["status"] = 200
            response["message"] = "Success"
            
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCognoDeskAppWhiteLabelSettingsAPI : %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'DeveloperConsole'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)        

SaveCognoDeskAppWhiteLabelSettings = SaveCognoDeskAppWhiteLabelSettingsAPI.as_view()
