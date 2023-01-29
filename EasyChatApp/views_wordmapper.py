from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_analytics import *
from EasyChatApp.utils_validation import EasyChatFileValidation, EasyChatInputValidation
from django.http import HttpResponseNotFound

import json
import logging
import xlrd
from os import path


logger = logging.getLogger(__name__)

ensure_element_tree(xlrd)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def WordMapperConsole(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Intent Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            selected_bot_obj = None
            if "bot_pk" in request.GET:
                bot_pk = request.GET["bot_pk"]
                if not check_access_for_user(request.user, bot_pk, "Intent Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

            username = request.user.username
            user_obj = User.objects.get(username=username)
            bot_objs = Bot.objects.filter(
                users__in=[user_obj], is_uat=True, is_deleted=False)

            word_mapper_objs = []
            if selected_bot_obj != None:

                word_mapper_objs = WordMapper.objects.filter(
                    bots__in=[selected_bot_obj])

            return render(request, "EasyChatApp/platform/word_mapper.html", {
                'selected_bot_obj': selected_bot_obj,
                'bot_objs': bot_objs,
                'word_mapper_objs': word_mapper_objs
            })
        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("WordMapperConsole: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        return render(request, 'EasyChatApp/error_500.html')


def DeleteWordMapper(request, pk):  # noqa: N802
    response = {}
    response["status"] = 500
    response["message"] = "Internal Server Error"
    try:
        if request.method == "POST" and request.user.is_authenticated:
            try:
                word_mapper_obj = WordMapper.objects.get(pk=int(pk))
                bot_objs = list(word_mapper_obj.bots.all())
                if request.user not in bot_objs[0].users.all():
                    return HttpResponseNotFound("You do not have access to this page")
                word_mapper_obj.delete()
                if len(bot_objs) > 0:
                    return HttpResponseRedirect('/chat/word-mappers/?bot_pk=' + str(bot_objs[0].pk))
                else:
                    return HttpResponseRedirect('/chat/word-mappers/')
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("DeleteWordMapper: %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        else:
            return HttpResponseNotFound("You do not have access to this page")
        # return HttpResponse("Invalid Request")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("DeleteWordMapper: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        response = {"response": response}
        return HttpResponse(json.dumps(response), content_type="application/json")


class SaveWordMapperAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = DecryptVariable(request.data["data"])
            data = json.loads(data)
            values = data["values"]
            keyword = data["keyword"]
            keyword = keyword.strip()
            selected_bot_id = data["selected_bot_id"]
            word_mapper_pk = data["word_mapper_pk"]

            bot_obj = Bot.objects.get(
                pk=int(selected_bot_id), is_uat=True, is_deleted=False)

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['message'] = 'You are not authorised to perform this operation.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            values_list = [value.strip().lower()
                           for value in str(values).split(",") if value != ""]

            for value in values_list:
                if len(str(value).split()) > 1:
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            if values_list == []:
                response['status'] == 400
                response['message'] == 'Input single words can not be empty.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if keyword == "":
                response['status'] == 400
                response['message'] == 'Keyword can not be empty.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            word_mapper_objs = WordMapper.objects.filter(
                bots__in=[bot_obj])
            total_value_list = []
            for word_mapper_obj in word_mapper_objs:
                try:
                    if word_mapper_obj.pk == int(word_mapper_pk):
                        continue
                except Exception:
                    pass
                temp_values_list = [value.strip().lower()
                                    for value in str(word_mapper_obj.similar_words).split(",") if value != ""]
                total_value_list += temp_values_list

            common_value_list = list(set(values_list) & set(total_value_list))
            if len(common_value_list) > 0:
                response["status"] = 101
                response[
                    "message"] = "Matching similar words already exist for the given bot."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            word_mapper_obj = None
            if word_mapper_pk == None:

                word_mapper_objs = WordMapper.objects.filter(
                    bots__in=[bot_obj], keyword__icontains=keyword)

                if len(word_mapper_objs) > 0:
                    response["status"] = 101
                    response[
                        "message"] = "Matching word mapper keyword already exist in given bot."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                word_mapper_obj = WordMapper.objects.create(
                    keyword=keyword, similar_words=values)
            else:
                word_mapper_obj = WordMapper.objects.get(
                    pk=int(word_mapper_pk))
                word_mapper_obj.bots.clear()
                word_mapper_obj.keyword = keyword
                word_mapper_obj.similar_words = values
                word_mapper_obj.synced = False

            word_mapper_obj.bots.add(bot_obj)
            word_mapper_obj.save()
            bot_obj.need_to_build = True
            bot_obj.save()
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveWordMapperAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(selected_bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetWordMapperAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args):
        response = {}
        response["status"] = 500
        try:
            word_mapper_list = []
            for word_mapper_obj in WordMapper.objects.all():
                word_mapper_list.append({
                    "keyword": word_mapper_obj.keyword,
                    "similar_words": word_mapper_obj.similar_words,
                    "pk": word_mapper_obj.pk
                })
            response["word_mapper_list"] = word_mapper_list
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetWordMapperAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DownloadWordMapperExcelTemplateAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            if is_allowed(request, [BOT_BUILDER_ROLE]):
                export_path = None
                export_path_exist = None

                export_path = ("/files/templates/easychat-word-mapper" +
                               "/create_word_mapper_excel_template.xlsx")
                export_path_exist = path.exists(export_path[1:])

                response["status"] = 200
                response["export_path"] = export_path
                response["export_path_exist"] = export_path_exist
            else:
                response["status"] = 403
                response["export_path"] = None
                response["export_path_exist"] = None
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DownloadWordMapperExcelTemplateAPI! %s %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class UploadWordMapperExcelAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            if is_allowed(request, [BOT_BUILDER_ROLE]):
                data = request.data
                input_file = data["input_file"]
                data = json.loads(data["data"])
                bot_id = data["bot_id"]

                validation_obj = EasyChatInputValidation()
                file_validation_obj = EasyChatFileValidation()

                if file_validation_obj.check_malicious_file(input_file.name):
                    response["status"] = 300
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                if input_file.name.split('.')[-1] not in ['xls', 'xlsx']:
                    response["status"] = 300
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                bot_obj = Bot.objects.get(pk=int(bot_id), is_uat=True)
                file_name = get_dot_replaced_file_name(input_file.name)
                path = default_storage.save(
                    file_name, ContentFile(input_file.read()))
                file_path = settings.MEDIA_ROOT + path

                is_all_words_created_successfully = True

                wb = xlrd.open_workbook(file_path)
                sheet = wb.sheet_by_index(0)
                for row in range(1, sheet.nrows):
                    try:
                        values = str(sheet.cell_value(row, 0)).strip()
                        values = validation_obj.remo_html_from_string(values)

                        keyword = str(sheet.cell_value(row, 1)).strip()
                        keyword = validation_obj.remo_html_from_string(keyword)

                        values_list = [value.strip().lower()
                                       for value in str(values).split(",") if value != ""]

                        if not is_similar_words_format_correct(values_list):
                            is_all_words_created_successfully = False
                            response["message"] = "Some of the words have not been created because their mappers are not in correct format."
                            continue

                        if keyword == '':
                            is_all_words_created_successfully = False
                            response["message"] = "Some of the words have not been created because their keyword is empty."
                            continue

                        if is_similar_words_already_exist(values_list, bot_obj, WordMapper):
                            is_all_words_created_successfully = False
                            response["message"] = "Duplicate entries found. Please remove the duplicate entries and try again.."
                            continue

                        contains_special_symbols = False
                        for value in values_list:
                            if not validation_obj.is_alphanumeric(str(value)):
                                contains_special_symbols = True
                                break

                        if contains_special_symbols:
                            is_all_words_created_successfully = False
                            response["message"] = "Some of the words have not been created because their mappers contain special symbols."
                            continue

                        if not validation_obj.is_alphanumeric(keyword):
                            is_all_words_created_successfully = False
                            response["message"] = "Some of the words have not been created because their keyword contains special symbols."
                            continue

                        word_mapper_objs = WordMapper.objects.filter(
                            bots__in=[bot_obj], keyword__icontains=keyword)

                        if word_mapper_objs:
                            is_all_words_created_successfully = False
                            continue

                        word_mapper_obj = WordMapper.objects.create(
                            keyword=keyword, similar_words=values)

                        word_mapper_obj.bots.add(bot_obj)
                        word_mapper_obj.save()
                    except Exception:
                        response["status"] = 101
                        return Response(data=response)

                response["status"] = 200

                if not is_all_words_created_successfully:
                    response["status"] = 401

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UploadWordMapperExcelAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UploadWordMapperExcel = UploadWordMapperExcelAPI.as_view()

DownloadWordMapperExcelTemplate = DownloadWordMapperExcelTemplateAPI.as_view()

SaveWordMapper = SaveWordMapperAPI.as_view()

GetWordMapper = GetWordMapperAPI.as_view()
