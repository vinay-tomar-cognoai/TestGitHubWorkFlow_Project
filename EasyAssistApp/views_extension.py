from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated

from EasyAssistApp.utils import *
from EasyAssistApp.models import *

import os
import sys
import pytz
import time
import json
import base64
import operator
import logging
import requests
import datetime
import random
from zipfile import ZipFile

logger = logging.getLogger(__name__)


class VerifyExtensionLoginAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Invalid username or password"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cognoai_access_token = data["cognoai_access_token"]
            cognoai_agent_email_id = data["cognoai_agent_email_id"]
            cognoai_agent_password = data["cognoai_agent_password"]

            cognoai_access_token = remo_html_from_string(cognoai_access_token)
            cognoai_access_token = remo_special_tag_from_string(
                cognoai_access_token)

            cognoai_agent_email_id = remo_html_from_string(
                cognoai_agent_email_id)
            cognoai_agent_email_id = remo_special_tag_from_string(
                cognoai_agent_email_id)

            cognoai_agent_password = remo_html_from_string(
                cognoai_agent_password)

            user = authenticate(username=cognoai_agent_email_id,
                                password=cognoai_agent_password)

            if user is not None:
                response["status"] = 200
                response["verification_token"] = cognoai_agent_email_id
            else:
                response["status"] = 500
                response["message"] = "Invalid username or password"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error VerifyExtensionLoginAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


VerifyExtensionLogin = VerifyExtensionLoginAPI.as_view()


class VerifyExtensionTokenAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Invalid username or password"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cognoai_access_token = data["cognoai_access_token"]
            cognoai_agent_verification_token = data["cognoai_agent_verification_token"]

            cognoai_access_token = remo_html_from_string(cognoai_access_token)
            cognoai_access_token = remo_special_tag_from_string(
                cognoai_access_token)

            cognoai_agent_verification_token = remo_html_from_string(
                cognoai_agent_verification_token)
            cognoai_agent_verification_token = remo_special_tag_from_string(
                cognoai_agent_verification_token)

            access_token_obj = CobrowseAccessToken.objects.get(
                key=cognoai_access_token)

            source_easyassist_cobrowse_logo = access_token_obj.source_easyassist_cobrowse_logo
            if source_easyassist_cobrowse_logo == None or source_easyassist_cobrowse_logo.strip() == "":
                source_easyassist_cobrowse_logo = 'static/EasyAssistApp/img/cobrowseLogo.svg'

            response["status"] = 200
            response["COGNOAI_META_DATA"] = {
                "source_easyassist_cobrowse_logo": source_easyassist_cobrowse_logo,
            }

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error VerifyExtensionTokenAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


VerifyExtensionToken = VerifyExtensionTokenAPI.as_view()


class ExtensionAuthenticationAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Authentication Failed"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cognoai_access_token = data["cognoai_access_token"]

            cognoai_access_token = remo_html_from_string(cognoai_access_token)
            cognoai_access_token = remo_special_tag_from_string(
                cognoai_access_token)

            access_token_obj = CobrowseAccessToken.objects.get(
                key=cognoai_access_token)

            source_easyassist_cobrowse_logo = access_token_obj.source_easyassist_cobrowse_logo
            if source_easyassist_cobrowse_logo == None or source_easyassist_cobrowse_logo.strip() == "":
                source_easyassist_cobrowse_logo = 'static/EasyAssistApp/img/cobrowseLogo.svg'

            response["status"] = 200
            response["COGNOAI_META_DATA"] = {
                "source_easyassist_cobrowse_logo": source_easyassist_cobrowse_logo,
            }

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExtensionAuthenticationAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExtensionAuthentication = ExtensionAuthenticationAPI.as_view()


class SaveExtensionAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            extension_name = data["extension_name"]
            deploy_links = data["deploy_links"]
            access_token = data["access_token"]

            extension_name = remo_html_from_string(extension_name)
            extension_name = remo_special_tag_from_string(
                extension_name)

            access_token_obj = CobrowseAccessToken.objects.get(
                key=access_token)

            chrome_extension_obj = ChromeExtensionDetails.objects.filter(
                access_token=access_token_obj)
            if chrome_extension_obj:
                chrome_extension_obj = chrome_extension_obj[0]
                chrome_extension_obj.extension_name = extension_name
                chrome_extension_obj.deploy_links = deploy_links
                chrome_extension_obj.save()
            else:
                chrome_extension_obj = ChromeExtensionDetails.objects.create(access_token=access_token_obj,
                                                                             extension_name=str(
                                                                                 extension_name),
                                                                             deploy_links=deploy_links)

            if not os.path.exists(EASYASSISTAPP_CHROME_EXTENSION_FILES_PATH + str(access_token)):
                os.makedirs(
                    EASYASSISTAPP_CHROME_EXTENSION_FILES_PATH + str(access_token))

            manifest_json_data = CHROME_EXTENSION_MANIFEST_DATA
            manifest_json_data["name"] = str(extension_name)
            manifest_json_data["short_name"] = str(extension_name.lower())

            manifest_json_data_file_path = EASYASSISTAPP_CHROME_EXTENSION_FILES_PATH + \
                str(access_token) + "/manifest.json"

            manifest_json_data_file = open(manifest_json_data_file_path, "w")
            manifest_json_data_file.write(json.dumps(manifest_json_data))
            manifest_json_data_file.close()

            deploy_links = deploy_links.split(",")
            cognoai_crm_extension_file = open(
                settings.BASE_DIR + "/EasyAssistApp/static/EasyAssistApp/js/cognoai_crm_extension.js", "r")

            meta_data = "COGNOAI_SERVER_URL='" + settings.EASYCHAT_HOST_URL + "';"
            meta_data += "ACCESS_TOKEN='" + str(access_token) + "';"
            meta_data += "ALLOWED_HOST=["

            for link in deploy_links:
                meta_data += "'" + link + "',"
            meta_data += "];"

            write_file = meta_data + cognoai_crm_extension_file.read()
            cognoai_crm_extension_file.close()
            file_path = EASYASSISTAPP_CHROME_EXTENSION_FILES_PATH + \
                str(access_token) + "/cognoai_crm_extension.js"
            cognoai_crm_extension_file = open(file_path, "w")
            cognoai_crm_extension_file.write(write_file)
            cognoai_crm_extension_file.close()

            zip_file_path = EASYASSISTAPP_CHROME_EXTENSION_FILES_PATH + \
                str(access_token) + '/' + "cognoai_chrome_extension.zip"

            zip_obj = ZipFile(zip_file_path, 'w')
            zip_obj.write(settings.SECURE_MEDIA_ROOT + '/EasyAssistApp/chrome_extension/' + str(access_token) + "/cognoai_crm_extension.js",
                          basename(EASYASSISTAPP_CHROME_EXTENSION_FILES_PATH + str(access_token) + "/cognoai_crm_extension.js"))
            zip_obj.write(settings.SECURE_MEDIA_ROOT + '/EasyAssistApp/chrome_extension/' + str(access_token) + "/manifest.json",
                          basename(EASYASSISTAPP_CHROME_EXTENSION_FILES_PATH + str(access_token) + "/manifest.json"))
            zip_obj.close()
            
            if get_save_in_s3_bucket_status():
                key = s3_bucket_upload_file_by_file_path(zip_file_path, str(access_token) + '_' + "cognoai_chrome_extension.zip")
                s3_file_path = s3_bucket_download_file(key, 'EasyAssistApp/chrome_extension/', '.zip')
                zip_file_path = s3_file_path.split("EasyChat/", 1)[1]

            zip_file_path = "/" + zip_file_path
            zip_file_obj = CobrowsingFileAccessManagement.objects.create(
                file_path=zip_file_path, is_public=False, access_token=access_token_obj)
            zip_file_path = settings.EASYCHAT_HOST_URL + \
                '/easy-assist/download-file/' + str(zip_file_obj.key)

            chrome_extension_obj.extension_path = zip_file_path
            chrome_extension_obj.save()

            response["status"] = 200
            response["message"] = "Success"
            response["path"] = zip_file_path

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveExtensionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveExtension = SaveExtensionAPI.as_view()


class UpdateAgentCobrowsingDetailsAPI(APIView):

    def change_agent_active_status(self, active_agent, is_active):

        if is_active == None:
            return active_agent.is_active

        if is_active == True:
            time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=1)
            agent_online_audit_trail_obj = CobrowseAgentOnlineAuditTrail.objects.filter(
                agent=active_agent,
                last_online_end_datetime__gte=time_threshold).order_by(
                    '-last_online_start_datetime').first()

            if agent_online_audit_trail_obj != None:
                agent_online_audit_trail_obj.last_online_end_datetime = timezone.now()
                agent_online_audit_trail_obj.save()
            else:
                agent_online_audit_trail_obj = CobrowseAgentOnlineAuditTrail.objects.create(
                    agent=active_agent,
                    last_online_start_datetime=timezone.now(),
                    last_online_end_datetime=timezone.now())
                agent_online_audit_trail_obj.save()

            update_online_audit_trail_idle_time(
                active_agent, agent_online_audit_trail_obj, CobrowseAgentWorkAuditTrail)

        active_agent.is_active = is_active
        active_agent.last_agent_active_datetime = timezone.now()
        active_agent.save()

        return active_agent.is_active

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cognoai_access_token = data["cognoai_access_token"]
            cognoai_agent_verification_token = data["cognoai_agent_verification_token"]
            is_active = data["is_active"]

            cognoai_access_token = remo_html_from_string(cognoai_access_token)
            cognoai_access_token = remo_special_tag_from_string(
                cognoai_access_token)

            cognoai_agent_verification_token = remo_html_from_string(
                cognoai_agent_verification_token)
            cognoai_agent_verification_token = remo_special_tag_from_string(
                cognoai_agent_verification_token)

            active_agent = CobrowseAgent.objects.filter(
                user__username=cognoai_agent_verification_token).first()

            cobrowse_io_objs = CobrowseIO.objects.filter(
                is_archived=False).filter(
                agent=active_agent)

            response["is_active"] = self.change_agent_active_status(
                active_agent, is_active)
            response["cobrowse_io_details"] = parse_cobrowse_io_data(
                cobrowse_io_objs)
            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateAgentCobrowsingDetailsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UpdateAgentCobrowsingDetails = UpdateAgentCobrowsingDetailsAPI.as_view()


class GenerateDropLinkAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            cognoai_access_token = data["cognoai_access_token"]
            cognoai_agent_verification_token = data["cognoai_agent_verification_token"]

            cognoai_access_token = remo_html_from_string(cognoai_access_token)
            cognoai_access_token = remo_special_tag_from_string(
                cognoai_access_token)

            cognoai_agent_verification_token = remo_html_from_string(
                cognoai_agent_verification_token)
            cognoai_agent_verification_token = remo_special_tag_from_string(
                cognoai_agent_verification_token)

            active_agent = CobrowseAgent.objects.filter(
                user__username=cognoai_agent_verification_token).first()

            client_page_link = data["client_page_link"]
            client_page_link = remo_html_from_string(client_page_link)
            customer_name = data["customer_name"]
            customer_name = remo_html_from_string(customer_name)
            customer_name = remo_special_tag_from_string(customer_name)
            customer_mobile_number = data["customer_mobile_number"]
            customer_mobile_number = remo_html_from_string(
                customer_mobile_number)
            customer_mobile_number = remo_special_tag_from_string(
                customer_mobile_number)
            customer_email_id = data["customer_email_id"]
            customer_email_id = remo_html_from_string(customer_email_id)

            cobrowse_drop_link_obj = generate_drop_link_with_data(
                request, client_page_link, active_agent, customer_name, customer_email_id, customer_mobile_number, CobrowseDropLink)

            if cobrowse_drop_link_obj == None:
                response["status"] = 300
                response["message"] = "Link not generated"
            else:
                response["status"] = 200
                response["message"] = "success"
                response["generated_link"] = cobrowse_drop_link_obj.generated_link
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GenerateDropLinkAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GenerateDropLink = GenerateDropLinkAPI.as_view()


class SearchCobrowsingLeadAPI(APIView):

    def post(self, request, *args, **kwargs):
        logger.info("Inside SearchCobrowsingLeadAPI",
                    extra={'AppName': 'EasyAssist'})
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            logger.info("Request: " + json.dumps(data),
                        extra={'AppName': 'EasyAssist'})

            cognoai_access_token = data["cognoai_access_token"]
            cognoai_agent_verification_token = data["cognoai_agent_verification_token"]

            cognoai_access_token = remo_html_from_string(cognoai_access_token)
            cognoai_access_token = remo_special_tag_from_string(
                cognoai_access_token)

            access_token_obj = CobrowseAccessToken.objects.get(
                key=cognoai_access_token)

            cognoai_agent_verification_token = remo_html_from_string(
                cognoai_agent_verification_token)
            cognoai_agent_verification_token = remo_special_tag_from_string(
                cognoai_agent_verification_token)

            active_agent = CobrowseAgent.objects.filter(
                user__username=cognoai_agent_verification_token).first()

            search_value = strip_html_tags(data["search_value"])
            search_value = search_value.strip().lower()
            md5_primary_id = hashlib.md5(search_value.encode()).hexdigest()

            active_admin_user = get_admin_from_active_agent(
                active_agent, CobrowseAgent)

            cobrowse_io_list = []

            if "session_id_list" in data:
                cobrowse_io_list = CobrowseIO.objects.filter(
                    session_id__in=data["session_id_list"])
            else:
                cobrowse_leads = CobrowseCapturedLeadData.objects.filter(
                    primary_value=md5_primary_id)
                cobrowse_io_list = CobrowseIO.objects.filter(is_lead=True,
                                                             is_archived=False,
                                                             captured_lead__in=cobrowse_leads,
                                                             access_token__agent=active_admin_user,
                                                             agent=None).order_by('-last_update_datetime')

                if access_token_obj.enable_tag_based_assignment_for_outbound:
                    cobrowse_io_list = cobrowse_io_list.filter(
                        product_category__in=active_agent.product_category.filter(is_deleted=False))
            cobrowse_io_details = []

            show_verification_code_modal = access_token_obj.show_verification_code_modal

            for cobrowse_io_obj in cobrowse_io_list:
                if cobrowse_io_obj.is_lead:
                    cobrowse_io_obj.agent = active_agent
                    if show_verification_code_modal == False:
                        cobrowse_io_obj.allow_agent_cobrowse = "true"
                    cobrowse_io_obj.save()

            cobrowse_io_details = parse_cobrowse_io_data(
                cobrowse_io_list)

            response["status"] = 200
            response["message"] = "success"
            response["cobrowse_io_details"] = cobrowse_io_details[:5]
            logger.info("Response: " + json.dumps(response),
                        extra={'AppName': 'EasyAssist'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SearchCobrowsingLeadAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        logger.info("Successfully exited from SearchCobrowsingLeadAPI", extra={
                    'AppName': 'EasyAssist'})
        return Response(data=response)


SearchCobrowsingLead = SearchCobrowsingLeadAPI.as_view()


class AssignCobrowsingLeadAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            logger.info("Request: " + json.dumps(data),
                        extra={'AppName': 'EasyAssist'})

            cognoai_access_token = data["cognoai_access_token"]
            cognoai_agent_verification_token = data["cognoai_agent_verification_token"]

            cognoai_access_token = remo_html_from_string(cognoai_access_token)
            cognoai_access_token = remo_special_tag_from_string(
                cognoai_access_token)

            cognoai_agent_verification_token = remo_html_from_string(
                cognoai_agent_verification_token)
            cognoai_agent_verification_token = remo_special_tag_from_string(
                cognoai_agent_verification_token)

            active_agent = CobrowseAgent.objects.filter(
                user__username=cognoai_agent_verification_token).first()

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)
            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)

            if cobrowse_io.allow_agent_cobrowse == "true":
                cobrowse_io.agent = active_agent
                cobrowse_io.save()

            login_token_obj = CRMCobrowseLoginToken.objects.create(
                cobrowse_io=cobrowse_io)

            response["status"] = 200
            response["message"] = "success"
            response["allow_screen_sharing_cobrowse"] = cobrowse_io.access_token.allow_screen_sharing_cobrowse
            response["login_token"] = str(login_token_obj.token)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AssignCobrowsingLeadAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AssignCobrowsingLead = AssignCobrowsingLeadAPI.as_view()


class RequestCobrowsingAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            logger.info("Request: " + json.dumps(data),
                        extra={'AppName': 'EasyAssist'})

            cognoai_access_token = data["cognoai_access_token"]
            cognoai_agent_verification_token = data["cognoai_agent_verification_token"]

            cognoai_access_token = remo_html_from_string(cognoai_access_token)
            cognoai_access_token = remo_special_tag_from_string(
                cognoai_access_token)

            cognoai_agent_verification_token = remo_html_from_string(
                cognoai_agent_verification_token)
            cognoai_agent_verification_token = remo_special_tag_from_string(
                cognoai_agent_verification_token)

            active_agent = CobrowseAgent.objects.filter(
                user__username=cognoai_agent_verification_token).first()

            session_id = strip_html_tags(data["session_id"])
            session_id = remo_html_from_string(session_id)

            otp = random_with_n_digits(4)

            cobrowse_io = CobrowseIO.objects.get(session_id=session_id)
            cobrowse_io.agent_assistant_request_status = True
            cobrowse_io.is_agent_request_for_cobrowsing = True
            cobrowse_io.allow_agent_cobrowse = None
            cobrowse_io.cobrowsing_start_datetime = None
            cobrowse_io.otp_validation = otp
            cobrowse_io.save()

            category = "session_details"
            description = "Request for cobrowsing sent by " + \
                str(active_agent.user.username)
            save_system_audit_trail(
                category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, active_agent)

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RequestCobrowsingAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


RequestCobrowsing = RequestCobrowsingAPI.as_view()


class CloseCobrowsingSessionAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            logger.info("Request: " + json.dumps(data),
                        extra={'AppName': 'EasyAssist'})

            cognoai_access_token = data["cognoai_access_token"]
            cognoai_agent_verification_token = data["cognoai_agent_verification_token"]

            cognoai_access_token = remo_html_from_string(cognoai_access_token)
            cognoai_access_token = remo_special_tag_from_string(
                cognoai_access_token)

            cognoai_agent_verification_token = remo_html_from_string(
                cognoai_agent_verification_token)
            cognoai_agent_verification_token = remo_special_tag_from_string(
                cognoai_agent_verification_token)
            active_agent = CobrowseAgent.objects.filter(
                user__username=cognoai_agent_verification_token).first()

            id = strip_html_tags(data["id"])
            id = remo_html_from_string(id)
            is_lead_updated = False
            if "is_lead_updated" in data:
                is_lead_updated = True

            cobrowse_io = CobrowseIO.objects.get(session_id=id)

            if "is_leaving" in data:
                cobrowse_io.support_agents.remove(active_agent)
                cobrowse_io.save()
                response['status'] = 200
            else:
                comments = strip_html_tags(data["comments"])
                comment_desc = ""
                if "comment_desc" in data:
                    comment_desc = strip_html_tags(data["comment_desc"])

                meeting_io = CobrowseVideoConferencing.objects.filter(
                    meeting_id=id)

                if meeting_io:
                    meeting_io = meeting_io[0]
                    meeting_io.is_expired = True
                    meeting_io.agent_comments = comments
                    meeting_io.save()

                    try:
                        audit_trail = CobrowseVideoAuditTrail.objects.get(
                            cobrowse_video=meeting_io)
                        audit_trail.meeting_ended = timezone.now()
                        audit_trail.is_meeting_ended = True
                        audit_trail.save()
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Error CloseCobrowsingSessionAPI %s at %s",
                                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                is_helpful = True
                if cobrowse_io.is_helpful == False:
                    if "is_helpful" in data:
                        is_helpful = data["is_helpful"]

                is_test = False
                if "is_test" in data:
                    is_test = data["is_test"]

                if str(active_agent.user.username) == str(cobrowse_io.agent):
                    cobrowse_io.is_archived = True
                    cobrowse_io.is_agent_connected = False
                    cobrowse_io.is_closed_session = True
                    cobrowse_io.is_helpful = is_helpful
                    cobrowse_io.is_test = is_test
                    cobrowse_io.agent_comments = comments
                    cobrowse_io.agent_session_end_time = timezone.now()
                    if cobrowse_io.session_archived_cause == None:
                        cobrowse_io.session_archived_cause = "AGENT_ENDED"
                        cobrowse_io.session_archived_datetime = timezone.now()
                    if is_lead_updated == False:
                        cobrowse_io.agent_session_end_time = timezone.now()
                    cobrowse_io.save()

                save_agent_closing_comments_cobrowseio(
                    cobrowse_io, active_agent, comments, CobrowseAgentComment, comment_desc)

                if is_lead_updated:
                    category = "session_lead_status_update"
                    description = "Lead status is updated by " + \
                        str(active_agent.user.username)
                else:
                    category = "session_closed"
                    description = "Session is archived by " + \
                        str(active_agent.user.username) + \
                        " after submitting comments"
                save_system_audit_trail(
                    category, description, cobrowse_io, cobrowse_io.access_token, SystemAuditTrail, active_agent)

                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CloseCobrowsingSessionAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


CloseCobrowsingSession = CloseCobrowsingSessionAPI.as_view()
