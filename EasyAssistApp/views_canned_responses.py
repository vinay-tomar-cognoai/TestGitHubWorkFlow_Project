from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, HttpResponse, redirect
from EasyAssistApp.models import CobrowseAgent, LiveChatCannedResponse, CobrowsingFileAccessManagement, EasyAssistExportDataRequest, \
    AgentFrequentLiveChatCannedResponses, CobrowseIO
from EasyAssistApp.utils import get_supervisors_list_under_admin, get_supervisors_of_active_agent, CustomEncrypt, sanitize_input_string, \
    validate_canned_keyword, validate_canned_response, get_canned_response_list, add_audit_trail, remo_html_from_string, \
    create_excel_wrong_canned_response_data, create_file_access_management_obj, get_admin_from_active_agent, get_canned_responses_data_dump, \
    paginate, parse_canned_response_data, get_pagination_data, strip_html_tags, check_malicious_file_from_filename, check_malicious_file_from_content
from EasyAssistApp.constants import EXPORTS_UPPER_CAP_LIMIT, CHARACTERS_NOT_ALLOWED_IN_CANNED_RESPONSE, CHARACTER_LIMIT_CANNED_RESPONSE, \
    CHARACTER_LIMIT_CANNED_KEYWORD, CANNED_RESPONSE_ITEM_COUNT, INVALID_ACCESS_CONSTANT, NO_DATA_AVAILABLE_IMAGE_PATH, \
    CANNED_RESPONSE_EXPORT_TEMPLATE_PATH

from django.conf import settings
import sys
import json
import logging
import xlrd
import re
import uuid
import base64

logger = logging.getLogger(__name__)


def CannedResponseDashboard(request):
    try:
        if not request.user.is_authenticated:
            return redirect("/chat/login/")

        user = request.user
        cobrowse_agent = CobrowseAgent.objects.filter(
            user=user, is_account_active=True).first()
        access_token_obj = cobrowse_agent.get_access_token_obj()

        if cobrowse_agent.role == "admin_ally" or not access_token_obj.enable_chat_functionality:
            return redirect("/easy-assist/sales-ai/settings/")

        admin_agent = access_token_obj.agent

        if cobrowse_agent.role == "admin":
            supervisors_obj = get_supervisors_list_under_admin(cobrowse_agent)
            supervisors_obj.append(cobrowse_agent)
        elif cobrowse_agent.role == "supervisor":
            supervisors_obj = [admin_agent, cobrowse_agent]
        else:
            supervisors_list = get_supervisors_of_active_agent(
                cobrowse_agent, CobrowseAgent)
            supervisors_obj = supervisors_list + [admin_agent]

        supervisors_obj = list(set(supervisors_obj))

        return render(request, "EasyAssistApp/canned_responses_setting.html", {
            "cobrowse_agent": cobrowse_agent,
            "access_token_obj": access_token_obj,
            "no_data_available": NO_DATA_AVAILABLE_IMAGE_PATH,
            "supervisors": supervisors_obj,
            "admin_obj": admin_agent,
            "template_path": CANNED_RESPONSE_EXPORT_TEMPLATE_PATH,
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error CannedResponseDashboard %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
        return HttpResponse(INVALID_ACCESS_CONSTANT)


class EasyAssistAppUploadExcelAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            file_name = data["filename"]
            file_name = remo_html_from_string(file_name)
            base64_content = strip_html_tags(data["base64_file"])

            if file_name.find("<") != -1 or file_name.find(">") != -1 or file_name.find("=") != -1:
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if check_malicious_file_from_filename(file_name):
                response["status"] = 300
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            file_extension = file_name.split(".")[-1]
            file_extension = file_extension.lower()

            allowed_files_list = ["xls", "xlsx"]
            if file_extension in allowed_files_list:

                if check_malicious_file_from_content(base64_content, allowed_files_list):
                    response["status"] = 300
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                file_name = str(uuid.uuid4()) + '.' + file_extension
                file_path = settings.MEDIA_ROOT + file_name
                file_obj = open(file_path, "wb")
                file_obj.write(base64.b64decode(base64_content))
                file_obj.close()

                response["src"] = file_name
                response["status"] = 200
            else:
                response["status"] = 300
                logger.info("File format is not supported", extra={'AppName': 'EasyAssist'})

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EasyAssistAppUploadExcelAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EasyAssistAppUploadExcel = EasyAssistAppUploadExcelAPI.as_view()


class CreateNewCannedResponseAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = CobrowseAgent.objects.filter(
                user=request.user).first()
            access_token_obj = active_agent.get_access_token_obj()
            if active_agent.role in ["admin", "supervisor"] and access_token_obj.enable_chat_functionality:
                data = request.data['Request']
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                keyword = data["keyword"]
                canned_response = data["response"]

                character_set = set(canned_response).intersection(
                    CHARACTERS_NOT_ALLOWED_IN_CANNED_RESPONSE)

                if len(character_set) > 0:
                    characters = " ".join(character_set)
                    response["status_code"] = 302
                    response["status_message"] = characters + \
                        " are not allowed in canned response"
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                keyword = sanitize_input_string(keyword)
                canned_response = sanitize_input_string(canned_response)
                keyword = keyword.strip()
                canned_response = canned_response.strip()

                if not validate_canned_keyword(keyword):
                    response["status_code"] = 400
                    response["status_message"] = "Please enter a valid keyword (Only a-z 0-9 characters are allowed)"

                if not validate_canned_response(canned_response):
                    response["status_code"] = 400
                    response["status_message"] = "Please add a valid response (Only a-z A-Z @ . ? ! , 0-9 characters are allowed)"

                if len(keyword) > CHARACTER_LIMIT_CANNED_KEYWORD:
                    response["status_code"] = 400
                    response["status_message"] = "Keyword shouldn’t be more than 25 characters long"

                if not len(keyword):
                    response["status_code"] = 400
                    response["status_message"] = "Keyword cannot be empty"

                if len(canned_response) > CHARACTER_LIMIT_CANNED_RESPONSE:
                    response["status_code"] = 400
                    response["status_message"] = "Response shouldn’t be more than 500 characters long"

                if not len(canned_response):
                    response["status_code"] = 400
                    response["status_message"] = "Canned response cannot be empty"

                if response["status_code"] == 400:
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                canned_response_list = get_canned_response_list(
                    active_agent, LiveChatCannedResponse, CobrowseAgent)

                if canned_response_list.filter(keyword=keyword).count():
                    response["status_code"] = 300
                    response["status_message"] = "Keyword already exists, please try a different one"
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                LiveChatCannedResponse.objects.create(agent=active_agent,
                                                      keyword=keyword, response=canned_response, access_token=access_token_obj)

                response["status_code"] = 200
                response["status_message"] = "success"
                description = "Added canned response for id" + \
                    " (" + str(active_agent.pk) + ")"

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Add-Canned-response",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )
            else:
                response["status_code"] = 500

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateNewCannedResponseAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status_message"] = e

        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CreateNewCannedResponse = CreateNewCannedResponseAPI.as_view()


class EditCannedResponseAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = CobrowseAgent.objects.filter(
                user=request.user).first()
            access_token_obj = active_agent.get_access_token_obj()
            if active_agent.role in ["admin", "supervisor"] and access_token_obj.enable_chat_functionality:
                data = request.data['Request']
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                keyword = data["keyword"]
                canned_response = data["response"]
                canned_response_pk = data["canned_response_pk"]

                character_set = set(canned_response).intersection(
                    CHARACTERS_NOT_ALLOWED_IN_CANNED_RESPONSE)

                if len(character_set) > 0:
                    characters = " ".join(character_set)
                    response["status_code"] = 302
                    response["status_message"] = characters + \
                        " are not allowed in canned response"
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                keyword = sanitize_input_string(keyword)
                canned_response = sanitize_input_string(canned_response)
                canned_response_pk = remo_html_from_string(canned_response_pk)
                keyword = keyword.strip()
                canned_response = canned_response.strip()

                if len(keyword) > CHARACTER_LIMIT_CANNED_KEYWORD:
                    response["status_code"] = 400
                    response["status_message"] = "Keyword shouldn’t be more than 25 characters long"

                if not len(keyword):
                    response["status_code"] = 400
                    response["status_message"] = "Keyword cannot be empty"

                if len(canned_response) > CHARACTER_LIMIT_CANNED_RESPONSE:
                    response["status_code"] = 400
                    response["status_message"] = "Response shouldn’t be more than 500 characters long"

                if not len(canned_response):
                    response["status_code"] = 400
                    response["status_message"] = "Canned response cannot be empty"

                if not validate_canned_keyword(keyword):
                    response["status_code"] = 400
                    response["status_message"] = "Please enter a valid keyword (Only a-z 0-9 characters are allowed)"

                if not validate_canned_response(canned_response):
                    response["status_code"] = 400
                    response["status_message"] = "Please add a valid response (Only a-z A-Z @ . ? ! , 0-9 characters are allowed)"

                if response["status_code"] == 400:
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                canned_response_obj = LiveChatCannedResponse.objects.filter(
                    pk=int(canned_response_pk)).first()

                if canned_response_obj.keyword != keyword:
                    canned_response_list = get_canned_response_list(
                        active_agent, LiveChatCannedResponse, CobrowseAgent)
                    if canned_response_list.filter(keyword=keyword):
                        response["status_code"] = 300
                        response["status_message"] = "Keyword already exists, please try a different one"
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)

                canned_response_obj.keyword = keyword
                canned_response_obj.response = canned_response
                canned_response_obj.save()
                response["status_code"] = 200
                response["status_message"] = "success"
                description = "Updated canned response for id" + \
                    " (" + str(active_agent.pk) + ")"

                add_audit_trail(
                    "EASYASSISTAPP",
                    active_agent.user,
                    "Update-Canned-response",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditCannedResponseAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EditCannedResponse = EditCannedResponseAPI.as_view()


class DeleteCannedResponseAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = CobrowseAgent.objects.filter(
                user=request.user).first()
            access_token_obj = active_agent.get_access_token_obj()
            if active_agent.role in ["admin", "supervisor"] and access_token_obj.enable_chat_functionality:
                data = request.data['Request']
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)
                canned_response_pk_list = data["canned_response_pk_list"]
                admin_canned_response = 0
                for canned_response in canned_response_pk_list:
                    canned_response_obj = LiveChatCannedResponse.objects.filter(
                        pk=int(canned_response)).first()
                    if active_agent.role == "supervisor" and canned_response_obj.agent == active_agent:
                        canned_response_obj.is_deleted = True
                        canned_response_obj.save()
                    elif active_agent.role == "admin":
                        canned_response_obj.is_deleted = True
                        canned_response_obj.save()
                    else:
                        admin_canned_response += 1
                if admin_canned_response == len(canned_response_pk_list):
                    response["status_code"] = 407
                    response["status_message"] = "Responses added by the admin cannot be deleted"
                else:
                    response["status_code"] = 200
                    response["status_message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteCannedResponseAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DeleteCannedResponse = DeleteCannedResponseAPI.as_view()


class CreateCannedResponseWithExcelAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        logger.info("Into CreateAgentWithExcelAPI..",
                    extra={'AppName': 'EasyAssist'})
        response = {}
        response["status_code"] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:
            active_agent = CobrowseAgent.objects.filter(
                user=request.user).first()
            access_token_obj = active_agent.get_access_token_obj()
            if active_agent.role in ["admin", "supervisor"] and access_token_obj.enable_chat_functionality:
                data = request.data['Request']
                data = custom_encrypt_obj.decrypt(data)
                data = json.loads(data)

                file_path = settings.MEDIA_ROOT + data['src']

                wb = xlrd.open_workbook(file_path)
                sheet = wb.sheet_by_index(0)

                if sheet.nrows == 1:
                    response["status_code"] = 401
                    response["status_message"] = "Uploaded file is empty"
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                if sheet.nrows > 201:
                    response["status_code"] = 407
                    response["status_message"] = "Please upload a sheet containing up to 200 responses"
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                wrong_data_list = []

                canned_response_list = get_canned_response_list(
                    active_agent, LiveChatCannedResponse, CobrowseAgent)

                is_duplicate_count = 0
                for row in range(1, sheet.nrows):
                    is_duplicate = False
                    try:
                        keyword = sheet.cell_value(row, 0)
                        if isinstance(keyword, float):
                            keyword = str(int(keyword))
                        else:
                            keyword = str(keyword).strip()

                        canned_response = sheet.cell_value(row, 1)

                        if isinstance(canned_response, float):
                            canned_response = str(int(canned_response))
                        else:
                            canned_response = str(canned_response).strip()

                        keyword = sanitize_input_string(keyword)
                        canned_response = sanitize_input_string(
                            canned_response)

                        if " " in keyword:
                            wrong_data_list.append(
                                {"row_num": row, "keyword": keyword, "response": canned_response, "detail": "Keyword shouldn’t contain space between words"})
                            continue

                        if canned_response_list.filter(keyword=keyword):
                            wrong_data_list.append(
                                {"row_num": row, "keyword": keyword, "response": canned_response, "detail": "Keyword already exists, please try a different one"})
                            continue

                        if len(canned_response) > CHARACTER_LIMIT_CANNED_RESPONSE and len(keyword) > CHARACTER_LIMIT_CANNED_KEYWORD:
                            wrong_data_list.append(
                                {"row_num": row, "keyword": keyword, "response": canned_response, "detail": "Keywords shouldn't be 25 characters long and responses shouldn't be 500 characters long"})
                            continue

                        elif len(keyword) > CHARACTER_LIMIT_CANNED_KEYWORD:
                            wrong_data_list.append(
                                {"row_num": row, "keyword": keyword, "response": canned_response, "detail": "Keyword shouldn’t be more than 25 characters long"})
                            continue

                        elif len(canned_response) > CHARACTER_LIMIT_CANNED_RESPONSE:
                            wrong_data_list.append(
                                {"row_num": row, "keyword": keyword, "response": canned_response, "detail": "Response shouldn’t be more than 500 characters long"})
                            continue

                        if not len(keyword) and not len(canned_response):
                            wrong_data_list.append(
                                {"row_num": row, "keyword": keyword, "response": canned_response, "detail": "Please enter input values"})
                            continue

                        elif not len(keyword):
                            wrong_data_list.append(
                                {"row_num": row, "keyword": keyword, "response": canned_response, "detail": "Please add a keyword"})
                            continue

                        elif not len(canned_response):
                            wrong_data_list.append(
                                {"row_num": row, "keyword": keyword, "response": canned_response, "detail": "Please add a response"})
                            continue

                        if not validate_canned_keyword(keyword):
                            wrong_data_list.append(
                                {"row_num": row, "keyword": keyword, "response": canned_response, "detail": "Please enter a valid keyword (Only a-z 0-9 characters are allowed)"})
                            continue

                        if not validate_canned_response(canned_response):
                            wrong_data_list.append(
                                {"row_num": row, "keyword": keyword, "response": canned_response, "detail": "Please add a valid response (Only a-z A-Z @ . ? ! , 0-9 characters are allowed)"})
                            continue

                        if canned_response_list.filter(keyword=keyword).count():
                            is_duplicate = True
                            is_duplicate_count += 1

                        if not is_duplicate and is_duplicate_count == 0:
                            LiveChatCannedResponse.objects.create(agent=active_agent, keyword=keyword,
                                                                  response=canned_response, access_token=access_token_obj)
                            response["status_code"] = 200
                            response["status_message"] = "success"

                            description = "Added canned response with excel for id" + \
                                " (" + str(active_agent.pk) + ")"
                            add_audit_trail(
                                "EASYASSISTAPP",
                                active_agent.user,
                                "Add-Canned-response",
                                description,
                                json.dumps(data),
                                request.META.get("PATH_INFO"),
                                request.META.get('HTTP_X_FORWARDED_FOR')
                            )
                        else:
                            wrong_data_list.append(
                                {"row_num": row, "keyword": keyword, "response": canned_response, "detail": "Keyword already exists, please try a different one"})
                            continue

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("CreateCannedResponseWithExcelAPI: %s at %s", e,
                                     str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

                if len(wrong_data_list):
                    file_path = create_excel_wrong_canned_response_data(
                        wrong_data_list)
                    file_access_management_key = create_file_access_management_obj(
                        CobrowsingFileAccessManagement, access_token_obj, "/" + file_path)
                    response["file_path"] = 'easy-assist/download-file/' + \
                        file_access_management_key
                    response["status_code"] = 400
                    response["status_message"] = "Invalid values detected in the uploaded excel, please fix those and try uploading again"
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateCannedResponseWithExcelAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status_message"] = e

        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CreateCannedResponseWithExcel = CreateCannedResponseWithExcelAPI.as_view()


class ExportCannedResponsesAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response["export_path"] = "None"
        response["export_path_exist"] = False
        custom_encrypt_obj = CustomEncrypt()
        try:
            cobrowse_agent = CobrowseAgent.objects.filter(
                user=request.user, is_account_active=True).first()
            access_token_obj = cobrowse_agent.get_access_token_obj()

            if cobrowse_agent.role in ["agent", "admin_ally"] or not access_token_obj.enable_chat_functionality:
                response["export_path"] = "None"
                response["status"] = 401
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            if cobrowse_agent.role == "admin":
                supervisors_obj = get_supervisors_list_under_admin(
                    cobrowse_agent)
                supervisors_obj.append(cobrowse_agent)
            else:
                admin_agent = get_admin_from_active_agent(
                    cobrowse_agent, CobrowseAgent)
                supervisors_obj = [cobrowse_agent, admin_agent]

            canned_responses_obj = LiveChatCannedResponse.objects.filter(
                agent__in=supervisors_obj, access_token=cobrowse_agent.get_access_token_obj(), is_deleted=False)

            if canned_responses_obj.count() > EXPORTS_UPPER_CAP_LIMIT:
                EasyAssistExportDataRequest.objects.create(
                    report_type='canned-response', agent=cobrowse_agent, filter_param="")
                response["status"] = 300
                response["export_path"] = "None"
                response["export_path_exist"] = False
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)
            else:
                export_path = get_canned_responses_data_dump(
                    cobrowse_agent, canned_responses_obj)
                response["export_path_exist"] = True
                file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
                    file_path=export_path, is_public=False, access_token=cobrowse_agent.get_access_token_obj())
                response["export_path"] = 'easy-assist/download-file/' + \
                    str(file_access_management_obj.key)
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ExportCannedResponsesAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ExportCannedResponses = ExportCannedResponsesAPI.as_view()


class GetAllCannedResponsesAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = 500
        response["status_message"] = "Internal server error."
        custom_encrypt_obj = CustomEncrypt()
        try:
            cobrowse_agent = CobrowseAgent.objects.filter(
                user=request.user).first()
            access_token_obj = cobrowse_agent.get_access_token_obj()

            if cobrowse_agent.role == "admin_ally" or not access_token_obj.enable_chat_functionality:
                response["status_code"] = 405
                response["status_message"] = INVALID_ACCESS_CONSTANT
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            admin_agent = access_token_obj.agent

            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            selected_supervisors_list = ""
            searched_keyword = ""

            if "selected_supervisors" in data:
                selected_supervisors_list = data['selected_supervisors']

            if "searched_keyword" in data:
                searched_keyword = sanitize_input_string(
                    data['searched_keyword'])

            if cobrowse_agent.role == "admin":
                supervisors_obj = get_supervisors_list_under_admin(
                    cobrowse_agent)
                supervisors_obj.append(cobrowse_agent)
            elif cobrowse_agent.role == "supervisor":
                supervisors_obj = [admin_agent, cobrowse_agent]
            else:
                supervisors_list = get_supervisors_of_active_agent(
                    cobrowse_agent, CobrowseAgent)
                supervisors_obj = supervisors_list + \
                    [admin_agent, cobrowse_agent]

            supervisors_obj = list(set(supervisors_obj))
            
            if searched_keyword and selected_supervisors_list:
                selected_supervisors = CobrowseAgent.objects.filter(
                    user__username__in=selected_supervisors_list)
                searched_keyword = re.escape(searched_keyword)
                canned_responses_obj = LiveChatCannedResponse.objects.filter(
                    agent__in=selected_supervisors, access_token=access_token_obj, keyword__icontains=searched_keyword, is_deleted=False)
            elif selected_supervisors_list:
                selected_supervisors = CobrowseAgent.objects.filter(
                    user__username__in=selected_supervisors_list)
                canned_responses_obj = LiveChatCannedResponse.objects.filter(
                    agent__in=selected_supervisors, access_token=access_token_obj, is_deleted=False)
            elif searched_keyword:
                searched_keyword = re.escape(searched_keyword)
                canned_responses_obj = LiveChatCannedResponse.objects.filter(
                    agent__in=supervisors_obj, access_token=access_token_obj, keyword__icontains=searched_keyword, is_deleted=False)
            else:
                canned_responses_obj = LiveChatCannedResponse.objects.filter(
                    agent__in=supervisors_obj, access_token=access_token_obj, is_deleted=False)

            canned_responses_obj = canned_responses_obj.order_by("keyword")

            page = int(data["page_number"])
            total_canned_response, canned_responses_obj, start_point, end_point = paginate(
                canned_responses_obj, CANNED_RESPONSE_ITEM_COUNT, page)

            response["status_code"] = 200
            response["canned_response_list"] = parse_canned_response_data(
                canned_responses_obj)
            response['pagination_data'] = get_pagination_data(
                canned_responses_obj)
            response["total_canned_responses"] = total_canned_response
            response["start"] = start_point
            response["end"] = end_point
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetAllCannedResponsesAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
            response["status_message"] = e

        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetAllCannedResponses = GetAllCannedResponsesAPI.as_view()


class UpdateAgentCannedResponseReverseAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            active_agent = None
            if "session_id" in data:
                session_id = strip_html_tags(data["session_id"])
                session_id = remo_html_from_string(session_id)
                cobrowse_io = CobrowseIO.objects.filter(session_id=session_id).first()
                active_agent = cobrowse_io.agent
            
            if "agent_code" in data and data["agent_code"]:
                agent_code = remo_html_from_string(strip_html_tags(data["agent_code"]))
                active_agent = CobrowseAgent.objects.filter(virtual_agent_code=agent_code).first()
            
            keyword = sanitize_input_string(data["keyword"])
            canned_response_obj = []
            agent_canned_response_obj = []

            if active_agent:
                canned_response_obj = LiveChatCannedResponse.objects.filter(
                    access_token=active_agent.get_access_token_obj(), keyword=keyword, is_deleted=False).first()
                agent_canned_response_obj = AgentFrequentLiveChatCannedResponses.objects.filter(
                    agent=active_agent, access_token=active_agent.get_access_token_obj(), canned_response=canned_response_obj).first()

                if agent_canned_response_obj:
                    agent_canned_response_obj.frequency += 1
                    agent_canned_response_obj.save(update_fields=["frequency"])
                else:
                    AgentFrequentLiveChatCannedResponses.objects.create(
                        agent=active_agent, access_token=active_agent.get_access_token_obj(), canned_response=canned_response_obj)
                
                response["status_code"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateAgentCannedResponseReverseAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateAgentCannedResponseReverse = UpdateAgentCannedResponseReverseAPI.as_view()


class UpdateAgentCannedResponseAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            active_agent = CobrowseAgent.objects.filter(
                user=request.user).first()
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            keyword = sanitize_input_string(data["keyword"])

            canned_response_obj = LiveChatCannedResponse.objects.filter(
                access_token=active_agent.get_access_token_obj(), keyword=keyword, is_deleted=False).first()
            agent_canned_response_obj = AgentFrequentLiveChatCannedResponses.objects.filter(
                agent=active_agent, access_token=active_agent.get_access_token_obj(), canned_response=canned_response_obj).first()

            if agent_canned_response_obj:
                agent_canned_response_obj.frequency += 1
                agent_canned_response_obj.save()
            else:
                AgentFrequentLiveChatCannedResponses.objects.create(
                    agent=active_agent, access_token=active_agent.get_access_token_obj(), canned_response=canned_response_obj)

            response["status_code"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateAgentCannedResponseAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateAgentCannedResponse = UpdateAgentCannedResponseAPI.as_view()
