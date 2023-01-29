from EasyChatApp.utils_validation import EasyChatInputValidation
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from EasyChat.settings import APP_LOG_FILENAME, LOGTAILER_LINES
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect

from django.http import FileResponse, HttpResponseNotFound

from subprocess import check_output

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_analytics import *
from EasyChatApp.utils_bot import get_paginator_meta_data
from EasyChatApp.constants import *
from EasyChatApp.utils_processor_validator import *

import os
import json
import logging
import subprocess
import sys
import threading
from datetime import datetime, timezone
from EasyChat.settings import BASE_DIR
import re
from os import path
import func_timeout

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class LoadStaticFileAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = DecryptVariable(request.data["data"])
            data = json.loads(data)
            filename = data["filename"]

            if filename.find("/static/") == -1:
                response["status"] = 101
                response["message"] = "Only static file edit is allowed"
            elif path.exists(settings.BASE_DIR + "/" + filename):
                code = open(settings.BASE_DIR + "/" + filename).read()
                response["status"] = 200
                response["code"] = code
                response["message"] = "success"
            else:
                response["status"] = 101
                response["message"] = "Matching file doesn't exists"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LoadStaticFileAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LoadStaticFile = LoadStaticFileAPI.as_view()


class SaveStaticFileAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = DecryptVariable(request.data["data"])
            data = json.loads(data)
            filename = data["filename"]
            code = data["code"]

            if filename.find("/static/") == -1:
                response["status"] = 101
                response["message"] = "Only static file edit is allowed"
            elif path.exists(settings.BASE_DIR + "/" + filename):
                static_file = open(settings.BASE_DIR + "/" + filename, "w")
                static_file.write(code)
                static_file.close()

                if path.exists(settings.BASE_DIR + "/static" + filename.split("static")[-1]):
                    static_file = open(
                        settings.BASE_DIR + "/static" + filename.split("static")[-1], "w")
                    static_file.write(code)
                    static_file.close()

                response["status"] = 200
                response["message"] = "success"
            else:
                response["status"] = 101
                response["message"] = "Matching file doesn't exists"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveStaticFileAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveStaticFile = SaveStaticFileAPI.as_view()


def EditStaticPage(request):
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        return render(request, "EasyChatApp/edit_static.html")
    else:
        return HttpResponseRedirect("/chat/login")


def LogAnalytics(request):
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        return render(request, "EasyChatApp/log_file.html", {
            "expanded_logo": True
        })
    else:
        return HttpResponseRedirect("/chat/login")


def DownloadEasyChatLogs(request):
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        final_log_file = open(settings.MEDIA_ROOT + 'private/app.log', 'w')
        log_file = open(APP_LOG_FILENAME, 'r')

        data = request.POST
        if(len(data) == 0):
            final_log_file.write(log_file.read())
        else:
            try:
                data = DecryptVariable(data["json_string"])
                data = json.loads(data)
                date_start = data["date_start"]
                date_end = data["date_end"]
                time_start = data["time_start"]
                time_end = data["time_end"]
                start_date_time = date_start + " " + time_start + ":00"
                end_start_time = date_end + " " + time_end + ":00"
                start_date_time = datetime.strptime(
                    start_date_time, '%Y-%m-%d %H:%M:%S')
                end_start_time = datetime.strptime(
                    end_start_time, '%Y-%m-%d %H:%M:%S')
                with log_file as file:
                    for line in file:
                        date_splitter = line.split(" ")[:2]
                        if(len(date_splitter) > 1):
                            dates = (date_splitter[0] + " " + date_splitter[1]
                                     ).replace("[", "").replace("]", "")
                            try:
                                dates = datetime.strptime(
                                    dates, '%d-%b-%Y %H:%M:%S')

                                if dates >= start_date_time and dates <= end_start_time:
                                    final_log_file.write(line)

                            except Exception:
                                final_log_file.write(line)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("LogContent: %s at %s",
                             str(e), str(exc_tb.tb_lineno))

        final_log_file.close()
        path_to_file = settings.MEDIA_ROOT + 'private/app.log'
        try:
            response = FileResponse(open(path_to_file, 'rb'))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="app.log"'
            response['Content-Length'] = os.path.getsize(path_to_file)
            return response
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LogContent: %s at %s", str(e), str(exc_tb.tb_lineno))
            # return HttpResponse("Invalid request")
            return render(request, 'EasyChatApp/error_500.html')

    else:
        return HttpResponseRedirect("/chat/login")

########################  API Integration in console ###################


def check_common_utils_line(code, bot_pk):
    code = code.splitlines()
    for code_iterator in range(0, len(code)):
        if re.search("current_bot_id = ", code[code_iterator]):
            code[
                code_iterator] = "    current_bot_id = " + bot_pk
    updated_code = ""
    for code_iterator in range(0, len(code)):
        updated_code = updated_code + code[code_iterator] + "\n"
    return updated_code


def ProcessorConsole(request):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Intent Related", "overall"):
                return render(request, 'EasyChatApp/unauthorized.html')
            if request.user.supervisor and request.user.is_staff:
                tree_pk = request.GET["tree_pk"]
                intent_pk = request.GET["intent_pk"]
                processor = request.GET["processor"]
                bot_pk = request.GET["bot_pk"]
                bot_obj = Bot.objects.get(pk=int(bot_pk))
                if request.user not in bot_obj.users.all():
                    return render(request, 'EasyChatApp/unauthorized.html')
                lang = "1"
                if tree_pk == "-1":
                    tree_pk = Intent.objects.get(
                        pk=intent_pk, is_hidden=False).tree.pk

                tree_obj = Tree.objects.get(pk=tree_pk)
                apis_used = []
                # without special characters and spaces
                apis_used_ids = {}

                if processor == "post":
                    if tree_obj.post_processor != None:
                        name = tree_obj.post_processor.name

                        code = check_common_utils_line(
                            tree_obj.post_processor.function, bot_pk)
                        lang = tree_obj.post_processor.processor_lang
                        apis_used = tree_obj.post_processor.apis_used.split("****")
                        if len(apis_used) > 1:
                            for item in apis_used[:-1]:
                                apis_used_ids[
                                    re.sub('[^A-Za-z0-9]+', '', item)] = item
                    else:
                        name = "asdhs524fdbghdagfht52eg2fc"
                        code = get_common_utils_file_code(bot_pk)
                        code += POST_PROCESSOR_BASE_PYTHON_CODE
                elif processor == "pipe":
                    if tree_obj.pipe_processor != None:
                        name = tree_obj.pipe_processor.name
                        code = check_common_utils_line(
                            tree_obj.pipe_processor.function, bot_pk)
                        lang = tree_obj.pipe_processor.processor_lang
                        apis_used = tree_obj.pipe_processor.apis_used.split("****")
                        if len(apis_used) > 1:
                            for item in apis_used[:-1]:
                                apis_used_ids[
                                    re.sub('[^A-Za-z0-9]+', '', item)] = item
                    else:
                        name = "asdhs524fdbghdagfht52eg2fc"
                        code = get_common_utils_file_code(bot_pk)
                        code += PIPE_PROCESSOR_BASE_PYTHON_CODE
                else:

                    if tree_obj.api_tree != None:
                        name = tree_obj.api_tree.name
                        code = check_common_utils_line(
                            tree_obj.api_tree.api_caller, bot_pk)
                        lang = tree_obj.api_tree.processor_lang
                        apis_used = tree_obj.api_tree.apis_used.split("****")
                        if len(apis_used) > 1:
                            for item in apis_used[:-1]:
                                apis_used_ids[
                                    re.sub('[^A-Za-z0-9]+', '', item)] = item
                    else:
                        name = "asdhs524fdbghdagfht52eg2fc"
                        code = get_common_utils_file_code(bot_pk)
                        code += API_TREE_BASE_PYTHON_CODE

                dynamic_variable = get_dynamic_variables(code)

                config_obj = Config.objects.all()[0]
                system_commands = json.loads(
                    config_obj.system_commands.replace("'", '"'))
                
                mail_sent_to_list = json.loads(bot_obj.mail_sent_to_list)["items"]
                api_fail_email_configured = False

                if bot_obj.is_api_fail_email_notifiication_enabled:
                    api_fail_email_configured = True

                if processor == "post":
                    return render(request, "EasyChatApp/post_processor.html", {
                        "name": name,
                        "code": code,
                        "processor": processor,
                        "tree_pk": tree_pk,
                        "language_list": LANGUAGE_CHOICES,
                        "lang": lang,
                        "dynamic_variable": dynamic_variable,
                        "apis_used_ids": apis_used_ids,
                        "system_commands": system_commands,
                        "mail_sent_to_list": mail_sent_to_list,
                        "bot_obj": bot_obj,
                        "api_fail_email_configured": api_fail_email_configured,
                        "expanded_logo": True,
                    })
                elif processor == "pipe":
                    is_automatic_recursion_enabled = tree_obj.is_automatic_recursion_enabled
                    return render(request, "EasyChatApp/pipe_processor.html", {
                        "name": name,
                        "code": code,
                        "processor": processor,
                        "tree_pk": tree_pk,
                        "language_list": LANGUAGE_CHOICES,
                        "lang": lang,
                        "dynamic_variable": dynamic_variable,
                        "is_automatic_recursion_enabled": is_automatic_recursion_enabled,
                        "apis_used_ids": apis_used_ids,
                        "system_commands": system_commands,
                        "mail_sent_to_list": mail_sent_to_list,
                        "bot_obj": bot_obj,
                        "api_fail_email_configured": api_fail_email_configured,
                        "expanded_logo": True,
                    })
                else:
                    return render(request, "EasyChatApp/api_tree.html", {
                        "name": name,
                        "code": code,
                        "processor": processor,
                        "tree_pk": tree_pk,
                        "language_list": LANGUAGE_CHOICES,
                        "lang": lang,
                        "dynamic_variable": dynamic_variable,
                        "apis_used_ids": apis_used_ids,
                        "system_commands": system_commands,
                        "mail_sent_to_list": mail_sent_to_list,
                        "bot_obj": bot_obj,
                        "api_fail_email_configured": api_fail_email_configured,
                        "expanded_logo": True,
                    })
            else:
                # return HttpResponse("Invalid Access")
                return render(request, 'EasyChatApp/unauthorized.html')
        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ProcessorConsole: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
    return render(request, 'EasyChatApp/error_404.html')


def DataModelEntries(request):
    request.session["EASYCHAT_VERSION"] = settings.EASYCHAT_VERSION
    request.session[
        "EASYCHAT_DATE_OF_RELEASE"] = settings.EASYCHAT_DATE_OF_RELEASE
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        if not check_access_for_user(request.user, None, "Intent Related", "overall") or not request.user.is_staff:
            return HttpResponseNotFound("You do not have access to this page")
        if request.user.supervisor:

            easychat_customers = Profile.objects.all().order_by('-pk')[:1000]
            bot_pk = 0
            selected_user = "All"
            selected_variable = "All"

            try:
                bot_pk = int(request.GET["bot_pk"])
            except Exception:
                pass
            try:
                selected_user = request.GET["selected_user"]
            except Exception:
                pass
            try:
                selected_variable = request.GET["selected_variable"]
            except Exception:
                pass

            if selected_user == "All":
                if selected_variable == "All":
                    data_objs = Data.objects.all()
                else:
                    data_objs = Data.objects.filter(
                        variable=selected_variable)
            else:
                if selected_variable == "All":
                    data_objs = Data.objects.filter(user=Profile.objects.get(
                        pk=selected_user))
                else:
                    data_objs = Data.objects.filter(user=Profile.objects.get(
                        pk=selected_user), variable=selected_variable)
            data_objs = data_objs.order_by('-pk')[:1000]
            variable_list = set(Data.objects.all().order_by(
                '-pk')[:1000].values_list('variable', flat=True))

            all_pages_entries = data_objs.count()

            no_of_records_per_page = DEFAULT_NO_OF_DAYS_WHATSAPP_HISTORY_RECORD_LIST[0]

            if "no_of_records_per_page" in request.GET:
                if request.GET["no_of_records_per_page"].isdigit():
                    temp_no_of_records_per_page = int(request.GET["no_of_records_per_page"])
                if temp_no_of_records_per_page in DEFAULT_NO_OF_DAYS_WHATSAPP_HISTORY_RECORD_LIST:
                    no_of_records_per_page = temp_no_of_records_per_page

            page = request.GET.get('page')
            pagination_metadata = get_paginator_meta_data(data_objs, no_of_records_per_page, page)
            
            pagination_metadata = json.dumps(pagination_metadata)

            paginator = Paginator(data_objs, no_of_records_per_page)
            page = request.GET.get('page')

            try:
                data_objs = paginator.page(page)
            except PageNotAnInteger:
                data_objs = paginator.page(1)
                page = 1
            except EmptyPage:
                data_objs = paginator.page(paginator.num_pages)
                page = paginator.num_pages

            start_entry_number = ((int(page) - 1) * no_of_records_per_page) + 1
            
            return render(request, "EasyChatApp/data_model.html", {
                "easychat_customers": easychat_customers,
                "bot_pk": bot_pk,
                "data_objs": data_objs,
                "selected_user": selected_user,
                "selected_variable": selected_variable,
                "variable_list": variable_list,
                "expanded_logo": True,
                "start_entry_number": start_entry_number,
                "end_entry_number": (start_entry_number - 1) + len(data_objs),
                "all_pages_entries": all_pages_entries,
                "pagination_metadata": pagination_metadata
            })
        else:
            # return HttpResponse("Invalid Access")
            return render(request, 'EasyChatApp/error_404.html')
    else:
        return HttpResponseRedirect("/chat/login")


class DecryptDataModelValuesAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            data_model_values = data["data_model_values"]

            decrypted_data_model_values = []
            for data_model_value in data_model_values:
                if data_model_value.strip() == "":
                    decrypted_data_model_values.append(data_model_value)
                else:
                    decrypted_value = DecryptVariable(data_model_value)
                    if decrypted_value:
                        decrypted_data_model_values.append(decrypted_value)
                    else:
                        decrypted_data_model_values.append(data_model_value)

            response["status"] = 200
            response["message"] = "SUCCESS"
            response["decrypted_values"] = decrypted_data_model_values

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DecryptDataModelValuesAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DecryptDataModelValues = DecryptDataModelValuesAPI.as_view()


def WhatsAppWebHookConsole(request):
    request.session["EASYCHAT_VERSION"] = settings.EASYCHAT_VERSION
    request.session[
        "EASYCHAT_DATE_OF_RELEASE"] = settings.EASYCHAT_DATE_OF_RELEASE
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        if not check_access_for_user(request.user, None, "Intent Related", "overall"):
            return HttpResponseNotFound("You do not have access to this page")
        if request.user.supervisor:
            try:
                bot_pk = int(request.GET["bot_pk"])
            except Exception:
                pass
            bot_obj = Bot.objects.filter(pk=int(bot_pk), users__username=request.user.username).first()
            
            if not bot_obj:
                return HttpResponseNotFound("You do not have access to this page")

            user = User.objects.get(username=request.user.username)
            selected_whatsapp_service_provider = None
            is_any_other_user_active = False
            code = ""
            active_user_mail = ""

            whatsapp_webhook_obj = WhatsAppWebhook.objects.filter(
                bot=bot_obj)
            if whatsapp_webhook_obj:
                code = whatsapp_webhook_obj[0].function
                selected_whatsapp_service_provider = whatsapp_webhook_obj[0].whatsapp_service_provider

                time_diff = datetime.now(
                    timezone.utc) - whatsapp_webhook_obj[0].last_updated_timestamp
                if (time_diff.days == 0 and time_diff.seconds <= 60):
                    if user not in whatsapp_webhook_obj[0].users_active.all():
                        is_any_other_user_active = True
                        active_user_obj = whatsapp_webhook_obj[0].users_active.all().first()
                        if active_user_obj:
                            active_user_mail = active_user_obj.email
                else:
                    whatsapp_webhook_obj[0].users_active.clear()
                    whatsapp_webhook_obj[0].users_active.add(user)
                    whatsapp_webhook_obj[0].last_updated_datetime = datetime.now()
                    whatsapp_webhook_obj[0].save()
            
            config_obj = Config.objects.all()[0]
            system_commands = json.loads(
                config_obj.system_commands.replace("'", '"'))
            whatsapp_service_providers = WhatsAppServiceProvider.objects.all().order_by("pk")
            return render(request, "EasyChatApp/whatsapp_webhook_console.html", {
                "bot_obj": bot_obj,
                "code": code,
                "system_commands": system_commands,
                "whatsapp_service_providers": whatsapp_service_providers,
                "selected_whatsapp_service_provider": selected_whatsapp_service_provider,
                "is_any_other_user_active": is_any_other_user_active,
                "active_user_mail": active_user_mail
            })
        else:
            # return HttpResponse("Invalid Access")
            return render(request, 'EasyChatApp/error_404.html')
    else:
        return HttpResponseRedirect("/chat/login")


def WhatsAppWebhookFunctionConsole(request):
    request.session["EASYCHAT_VERSION"] = settings.EASYCHAT_VERSION
    request.session[
        "EASYCHAT_DATE_OF_RELEASE"] = settings.EASYCHAT_DATE_OF_RELEASE
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        if not check_access_for_user(request.user, None, "Intent Related", "overall"):
            return HttpResponseNotFound("You do not have access to this page")
        if request.user.supervisor:
            try:
                bot_pk = int(request.GET["bot_pk"])
            except Exception:
                pass
            bot_objs = Bot.objects.filter(
                users__username=request.user.username)
            bot_obj = bot_objs.filter(pk=int(bot_pk))
            if bot_obj:
                whatsapp_webhook_obj = WhatsAppWebhook.objects.filter(
                    bot=bot_obj)
                if whatsapp_webhook_obj:
                    code = whatsapp_webhook_obj[0].extra_function
                else:
                    code = WHATAPP_WEBHOOK_EXTRA_FUNCTION_BASE_PYTHON_CODE
            else:
                return HttpResponseNotFound("You do not have access to this page")

            config_obj = Config.objects.all()[0]
            system_commands = json.loads(
                config_obj.system_commands.replace("'", '"'))
            return render(request, "EasyChatApp/whatsapp_function_console.html", {
                "bot_pk": bot_pk,
                "code": code,
                "system_commands": system_commands
            })
        else:
            # return HttpResponse("Invalid Access")
            return render(request, 'EasyChatApp/error_404.html')
    else:
        return HttpResponseRedirect("/chat/login")


class SaveWhatsAppWebhookFunctionAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            code = data["code"]
            bot_id = data["bot_id"]

            bot_obj = Bot.objects.filter(pk=int(bot_id))
            if bot_obj:
                whatsapp_webhook_obj = WhatsAppWebhook.objects.filter(
                    bot=bot_obj[0])
                if whatsapp_webhook_obj:
                    whatsapp_webhook_obj[0].extra_function = code
                    whatsapp_webhook_obj[0].bot = bot_obj[0]
                    whatsapp_webhook_obj[0].save()
                else:
                    WhatsAppWebhook.objects.create(bot=bot_obj[0],
                                                   extra_function=code)

                if check_for_system_commands(code, Config):
                    response['status'] = 400
                    response['message'] = "Code contains system commands. Please remove them and then save."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(
                        json.dumps(response))
                    return Response(data=response)
                
                set_value_to_cache(CACHE_KEY_EASYCHAT_WHATSAPP_WEBHOOK, str(bot_obj[0].pk), code)

                response["status"] = 200
                response["message"] = "SUCCESS"
            else:
                response["status"] = 305
                response["message"] = "Bot not found."
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveWhatsAppWebhookFunctionAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveWhatsAppWebhookFunction = SaveWhatsAppWebhookFunctionAPI.as_view()


class SaveWhatsAppWebhookContentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            code = data["code"]
            bot_id = data["bot_id"]
            wsp_code = data["wsp_code"]
            wsp_obj = WhatsAppServiceProvider.objects.get(name=wsp_code)
            user = User.objects.get(username=request.user.username)

            bot_obj = Bot.objects.filter(pk=int(bot_id))
            if bot_obj:
                whatsapp_webhook_obj = WhatsAppWebhook.objects.filter(
                    bot=bot_obj[0])
                if whatsapp_webhook_obj:
                    whatsapp_webhook_obj[0].function = code
                    whatsapp_webhook_obj[0].bot = bot_obj[0]
                    whatsapp_webhook_obj[0].whatsapp_service_provider = wsp_obj
                    whatsapp_webhook_obj[0].last_updated_timestamp = datetime.now()
                    whatsapp_webhook_obj[0].users_active.add(user)
                    whatsapp_webhook_obj[0].save()
                else:
                    whatsapp_webhook_obj = WhatsAppWebhook.objects.create(
                        bot=bot_obj[0], function=code, whatsapp_service_provider=wsp_obj)
                    whatsapp_webhook_obj.users_active.add(user)
                    whatsapp_webhook_obj.save()

                if check_for_system_commands(code, Config):
                    response['status'] = 400
                    response['message'] = "Code contains system commands. Please remove them and then save."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(
                        json.dumps(response))
                    return Response(data=response)
                
                set_value_to_cache(CACHE_KEY_EASYCHAT_WHATSAPP_WEBHOOK, str(bot_obj[0].pk), code)
                response["status"] = 200
                response["message"] = "SUCCESS"
            else:
                response["status"] = 305
                response["message"] = "Bot not found."
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveWhatsAppWebhookContentAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveWhatsAppWebhookContent = SaveWhatsAppWebhookContentAPI.as_view()


def WhatsAppWebhookHistory(request):
    
    try:
        request.session["EASYCHAT_VERSION"] = settings.EASYCHAT_VERSION
        request.session[
            "EASYCHAT_DATE_OF_RELEASE"] = settings.EASYCHAT_DATE_OF_RELEASE

        if not is_allowed(request, [BOT_BUILDER_ROLE]):
            return HttpResponseRedirect("/chat/login")

        if not check_access_for_user(request.user, None, "Intent Related", "overall"):
            return render(request, 'EasyChatApp/unauthorized.html')

        if not request.user.supervisor:
            return render(request, 'EasyChatApp/error_404.html')

        no_of_records_per_page = DEFAULT_NO_OF_DAYS_WHATSAPP_HISTORY_RECORD_LIST[0]
        bot_objs = Bot.objects.filter(
            users__username=request.user.username, is_deleted=False)
        whatsapp_history_objs = WhatsAppHistory.objects.filter(
            bot__in=bot_objs)

        validation_obj = EasyChatInputValidation()
        if 'bot_id' in request.GET:
            bot_id = request.GET["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_obj = Bot.objects.filter(pk=int(bot_id))
            whatsapp_history_objs = whatsapp_history_objs.filter(
                bot=bot_obj[0])
        if "mobile" in request.GET:
            mobile = request.GET["mobile"]
            mobile = validation_obj.remo_html_from_string(mobile)
            whatsapp_history_objs = whatsapp_history_objs.filter(
                mobile_number=str(mobile))

        if "received_date" in request.GET:
            received_date = request.GET["received_date"]
            received_date = validation_obj.remo_html_from_string(
                received_date)
            received_date = datetime.strptime(
                received_date, "%Y-%m-%d").date()
            whatsapp_history_objs = whatsapp_history_objs.filter(
                received_datetime__date=received_date)
        
        if "no_of_records_per_page" in request.GET:
            if request.GET["no_of_records_per_page"].isdigit():
                temp_no_of_records_per_page = int(request.GET["no_of_records_per_page"])
            if temp_no_of_records_per_page in DEFAULT_NO_OF_DAYS_WHATSAPP_HISTORY_RECORD_LIST:
                no_of_records_per_page = temp_no_of_records_per_page

        page = request.GET.get('page')

        pagination_metadata = get_paginator_meta_data(whatsapp_history_objs, no_of_records_per_page, page)
        
        pagination_metadata = json.dumps(pagination_metadata)

        paginator = Paginator(whatsapp_history_objs, no_of_records_per_page)
        
        try:
            whatsapp_history_objs = paginator.page(page)
        except PageNotAnInteger:
            whatsapp_history_objs = paginator.page(1)
        except EmptyPage:
            whatsapp_history_objs = paginator.page(paginator.num_pages)

        return render(request, "EasyChatApp/whatsapp_history.html", {
            "whatsapp_history_objs": whatsapp_history_objs,
            "whatsapp_bots": bot_objs,
            "expanded_logo": True,
            "pagination_metadata": pagination_metadata,
        })

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error WhatsAppWebhookHistory %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        # return HttpResponseNotFound("Internal Server Error")
        return render(request, 'EasyChatApp/error_500.html')


class SaveProcessorContentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            user_obj = User.objects.get(username=request.user.username)
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            code = data["code"]
            processor = data["processor"]
            tree_pk = data["tree_pk"]
            name = data["name"]
            is_new = data["is_new"]
            selected_lang = "1"  # setting the Default language for proccesor
            api_collection = data["api_collection"]
            original_processor_name = data["original_processor_name"]

            if processor == "field":
                field_id = data["field_id"]

            if processor != "field":
                tree_obj = Tree.objects.filter(pk=tree_pk).first()

            check_duplicate_name, response = check_duplicate_processor(
                name, original_processor_name, response, processor)
            if check_duplicate_name:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(
                    json.dumps(response))
                return Response(data=response)

            if check_for_system_commands(code, Config):
                response['status'] = 400
                response['message'] = "Code contains system commands. Please remove them and then save."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(
                    json.dumps(response))
                return Response(data=response)

            if str(is_new) == "True":
                if processor == "api":
                    try:
                        api_obj = create_apitree_console(name, code)
                        # api_obj.api_caller = code
                        api_obj.processor_lang = selected_lang
                        api_obj.is_cache = False
                        api_obj.cache_variable = ''
                        api_obj.users.add(user_obj)
                        api_obj.save(True)
                        tree_obj.api_tree = api_obj
                        tree_obj.save()
                    except Exception:
                        response["status"] = 300
                        response["message"] = "Duplicate name exists."
                        logger.error("Duplicate name exists at line 224", extra={'AppName': 'EasyChat', 'user_id': str(
                            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)
                elif processor == "post":
                    try:
                        processor_obj = create_processor_console(name, code)
                        # processor_obj.function = code
                        processor_obj.processor_lang = selected_lang
                        processor_obj.save(True)
                        tree_obj.post_processor = processor_obj
                        tree_obj.save()
                    except Exception:
                        response["status"] = 300
                        response["message"] = "Duplicate name exists"
                        logger.error("Duplicate name exists at line 234", extra={'AppName': 'EasyChat', 'user_id': str(
                            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)
                elif processor == "field":
                    try:
                        FormWidgetFieldProcessor.objects.create(
                            name=name, function=code, field_id=field_id, processor_lang=selected_lang)
                    except Exception as e:
                        response["status"] = 300
                        response["message"] = "Duplicate name exists"
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("SaveProcessorContent: %s at %s",
                                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)
                else:
                    try:
                        processor_obj = create_processor_console(name, code)
                        # processor_obj.function = code
                        processor_obj.processor_lang = selected_lang
                        processor_obj.save(True)
                        tree_obj.pipe_processor = processor_obj
                        tree_obj.save()
                    except Exception as e:
                        response["status"] = 300
                        response["message"] = "Duplicate name exists"
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Duplicate name exists at line 246 %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)
                audit_trail_data = json.dumps({
                    "processor": processor,
                    "processor_name": name
                })
                save_audit_trail(
                    user_obj, CREATE_PROCESSOR_ACTION, audit_trail_data)
            else:
                apis_used = ""
                for iterator in api_collection:
                    apis_used += iterator + "****"
                any_change_detected = False
                if processor == "api":
                    api_tree = tree_obj.api_tree
                    if api_tree.api_caller != code:
                        any_change_detected = True
                    api_tree.api_caller = code
                    api_tree.name = name
                    api_tree.processor_lang = selected_lang
                    api_tree.apis_used = apis_used
                    api_tree.save(True)
                    tree_obj.save()
                elif processor == "post":
                    post_processor = tree_obj.post_processor
                    if post_processor.function != code:
                        any_change_detected = True
                    post_processor.function = code
                    post_processor.name = name
                    post_processor.processor_lang = selected_lang
                    post_processor.apis_used = apis_used
                    post_processor.save(True)
                    tree_obj.save()
                elif processor == "field":
                    field_processor_obj = FormWidgetFieldProcessor.objects.get(
                        field_id=field_id)
                    field_processor_obj.name = name
                    field_processor_obj.function = code
                    field_processor_obj.processor_lang = selected_lang
                    field_processor_obj.save()
                else:
                    pipe_processor = tree_obj.pipe_processor
                    if pipe_processor.function != code:
                        any_change_detected = True
                    pipe_processor.function = code
                    pipe_processor.name = name
                    pipe_processor.processor_lang = selected_lang
                    pipe_processor.apis_used = apis_used
                    pipe_processor.save(True)
                    tree_obj.save()

                if any_change_detected:
                    audit_trail_data = json.dumps({
                        "processor": processor,
                        "processor_name": name
                    })
                    save_audit_trail(
                        user_obj, EDIT_PROCESSOR_ACTION, audit_trail_data)

            response["status"] = 200
            response["message"] = "SUCCESS"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveProcessorContent: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveProcessorContent = SaveProcessorContentAPI.as_view()


class DeleteProcessorContentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            user_obj = User.objects.get(username=request.user.username)
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            processor = data["processor"]

            if processor == "field":
                field_id = data["field_id"]
            processor_name = None

            if processor != "field":
                tree_pk = data["tree_pk"]
                tree_obj = Tree.objects.get(pk=tree_pk)

            if processor == "api":
                processor_name = tree_obj.api_tree.name
                tree_obj.api_tree = None
                tree_obj.save()
            elif processor == "post":
                processor_name = tree_obj.post_processor.name
                tree_obj.post_processor = None
                tree_obj.save()
            elif processor == "field":
                FormWidgetFieldProcessor.objects.filter(
                    field_id=field_id).delete()
            else:
                processor_name = tree_obj.pipe_processor.name
                tree_obj.pipe_processor = None
                tree_obj.save()

            audit_trail_data = json.dumps({
                "processor": processor,
                "processor_name": processor_name
            })
            save_audit_trail(
                user_obj, DELETE_PROCESSOR_ACTION, audit_trail_data)
            response["status"] = 200
            response["message"] = "SUCCESS"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteProcessorContent: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DeleteProcessorContent = DeleteProcessorContentAPI.as_view()


class EasyChatProcessorRunAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        response["elapsed_time"] = "0.0000"
        try:

            username = str(request.user.username)
            import urllib.parse
            import time
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            parameter = "parameter"
            code = data["code"]
            parameter = data["parameter"]
            processor = data["processor"]
            selected_lang = data["selected_lang"]
            dynamic_variables_list = data["dynamic_variables_list"]

            code = replace_data_values_console(code, dynamic_variables_list)

            if check_for_system_commands(code, Config):
                response["status"] = 400
                response["code"] = code
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if parameter == "":
                parameter = "no input parameter given."

            start_time = time.time()
            max_time_limit_for_code_execution = settings.EASYCHAT_PROCESSORS_MAX_RUNTIME_LIMIT
            if selected_lang == "1":
                try:
                    json_data = func_timeout.func_timeout(max_time_limit_for_code_execution, execute_processor_python_code, args=[str(code), open_file, processor, parameter]
                                                          )
                    response["status"] = 200
                except func_timeout.FunctionTimedOut:
                    logger.info("Proccesor was terminated beacuse it exceded time limit ...", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    json_data = {}
                    response["status"] = 302
                    response["status_message"] = "Time Limit Exceded for processor execution"

            elif selected_lang == "2":
                if not os.path.exists("files/language_support/" + str(username) + "/EasyChatConsole.java"):
                    cmd = "mkdir files/language_support/" + str(username)
                    subprocess.run(cmd, shell=True)
                    cmd = "touch files/language_support/" + \
                        str(username) + "/EasyChatConsole.java"
                    subprocess.run(cmd, shell=True)
                    cmd = "mkdir files/language_support/" + \
                        str(username) + "/org"
                    subprocess.run(cmd, shell=True)
                    cmd = "cp -r files/org/* files/language_support/" + \
                        str(username) + "/org"
                    subprocess.run(cmd, shell=True)

                # Opening .java file and writing the code inside the file.
                java_file = open("files/language_support/" + str(username) +
                                 "/EasyChatConsole.java", 'r+')
                # code = open("test_code.txt", 'r+')
                java_file.write(code)
                java_file.close()

                # Making .class, executable file.

                cmd = "javac files/language_support/" + \
                    str(username) + "/EasyChatConsole.java"

                try:
                    json_data, response_status = func_timeout.func_timeout(
                        max_time_limit_for_code_execution, execute_processor_java_code, args=[
                            cmd, username, parameter]
                    )
                    response["status"] = response_status
                except func_timeout.FunctionTimedOut:
                    logger.info("Proccesor was terminated beacuse it exceded time limit ...", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    json_data = {}
                    response["status"] = 302
                    response["status_message"] = "Time Limit Exceded for processor execution"

                # Clearing the .java file
                cmd = 'echo "" > "files/language_support/' + \
                    str(username) + '/EasyChatConsole.java" '
                subprocess.run(cmd, shell=True)

            elif selected_lang == "3":

                # Opening .php file and writing the code inside the file.
                code = code.replace("?>", "")
                code = code + "\n$parameter = '" + \
                    str(parameter) + \
                    "';\n    print_r(json_encode(f($parameter)));\n?>"
                # running .php file
                if not os.path.exists("files/language_support/" + str(username) + "/EasyChatConsole.php"):
                    cmd = "mkdir files/language_support/" + str(username)
                    subprocess.run(cmd, shell=True)
                    cmd = "touch files/language_support/" + \
                        str(username) + "/EasyChatConsole.php"
                    subprocess.run(cmd, shell=True)

                try:
                    json_data, response_status = func_timeout.func_timeout(
                        max_time_limit_for_code_execution, execute_processor_php_code, args=[
                            code, username]
                    )
                    response["status"] = response_status
                except func_timeout.FunctionTimedOut:
                    logger.info("Proccesor was terminated beacuse it exceded time limit ...", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    json_data = {}
                    response["status"] = 302
                    response["status_message"] = "Time Limit Exceded for processor execution"

                # Clearing the .php file
                cmd = ' echo "" > "files/language_support/' + \
                    str(username) + '/EasyChatConsole.php"'
                subprocess.run(cmd, shell=True)

            elif selected_lang == "4":
                try:
                    json_data = func_timeout.func_timeout(
                        max_time_limit_for_code_execution, execute_processor_javascript_code, args=[
                            code, parameter]
                    )
                    response["status"] = 200
                except func_timeout.FunctionTimedOut:
                    logger.info("Proccesor was terminated beacuse it exceded time limit ...", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    json_data = {}
                    response["status"] = 302
                    response["status_message"] = "Time Limit Exceded for processor execution"

            end_time = time.time()

            elapsed_time = end_time - start_time

            response["elapsed_time"] = str(elapsed_time)

            response["message"] = json_data
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EasyChatProcessorRunAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response["status"] = 300
            response["message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EasyChatProcessorRun = EasyChatProcessorRunAPI.as_view()


class ProcessorLanguageChangeAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            language = data["language"]
            processor = data["processor"]
            tree_pk = data["tree_pk"]
            is_new = data["is_new"]

            tree_obj = Tree.objects.get(pk=tree_pk)

            if str(language) == "1":
                response = get_updated_python_code(is_new, tree_obj, processor)
            elif str(language) == "2":
                response = get_updated_java_code(is_new, tree_obj, processor)
            elif str(language) == "3":
                response = get_updated_php_code(is_new, tree_obj, processor)
            else:
                response = get_updated_javascript_code(
                    is_new, tree_obj, processor)

            response["status"] = 200
            response["message"] = "SUCCESS"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ProcessorLanguageChangeAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ProcessorLanguageChange = ProcessorLanguageChangeAPI.as_view()

"""
function: create_apitree_console
input params:
    name: Name of new API Tree.
    code: code for api_caller
output:
    response: Returns the new api_tree with given name and api_caller. If duplicate name exists, then it returns None.

This function is used to create new API Tree. It also validate the name duplication.
"""


def create_apitree_console(name, code):
    try:
        api_objs = ApiTree.objects.filter(name=name)

        if api_objs:
            return None
        else:
            api_obj = ApiTree.objects.create(name=name, api_caller=code)
            return api_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_apitree_console: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: create_processor_console
input params:
    name: Name of new processor.
    code: code for processor function
output:
    response: Returns the new processor with given name and function code. If duplicate name exists, then it returns None.

This function is used to create new processor(pipe ane post). It also validate the name duplication.
"""


def create_processor_console(name, code):
    try:
        processor_obj = Processor.objects.filter(name=name)
        if len(processor_obj) > 0:
            return None
        else:
            processor_obj = Processor.objects.create(name=name, function=code)
            return processor_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_processor_console: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: get_updated_python_code
input params:
    is_new: It is true if a new processor requested.
    tree_obj: It is the tree obj.
    processor: It denotest the type of processor.
output:
    response: Returns the updated code in node for choosen processor of current tree.

This function is used to find updated code in python for choosen processor of current tree.
"""


def get_updated_python_code(is_new, tree_obj, processor):
    response = {}

    try:
        if str(is_new) == "True":
            if processor == "api":
                response["code"] = API_TREE_BASE_PYTHON_CODE
            elif processor == "post":
                response["code"] = POST_PROCESSOR_BASE_PYTHON_CODE
            else:
                response["code"] = PIPE_PROCESSOR_BASE_PYTHON_CODE
        else:
            if processor == "api":
                api_tree = tree_obj.api_tree
                if api_tree.processor_lang == "1":
                    response["code"] = api_tree.api_caller
                else:
                    response["code"] = API_TREE_BASE_PYTHON_CODE
            elif processor == "post":
                post_processor = tree_obj.post_processor
                if post_processor.processor_lang == "1":
                    response["code"] = post_processor.function
                else:
                    response["code"] = POST_PROCESSOR_BASE_PYTHON_CODE
            else:
                pipe_processor = tree_obj.pipe_processor
                if pipe_processor.processor_lang == "1":
                    response["code"] = pipe_processor.function
                else:
                    response["code"] = PIPE_PROCESSOR_BASE_PYTHON_CODE
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_updated_python_code: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response


"""
function: get_updated_java_code
input params:
    is_new: It is true if a new processor requested.
    tree_obj: It is the tree obj.
    processor: It denotest the type of processor.
output:
    response: Returns the updated code in node for choosen processor of current tree.

This function is used to find updated code in java for choosen processor of current tree.
"""


def get_updated_java_code(is_new, tree_obj, processor):
    response = {}
    try:
        if str(is_new) == "True":
            if processor == "api":
                response["code"] = API_TREE_BASE_JAVA_CODE
            elif processor == "post":
                response["code"] = POST_PROCESSOR_BASE_JAVA_CODE
            else:
                response["code"] = PIPE_PROCESSOR_BASE_JAVA_CODE
        else:
            if processor == "api":
                api_tree = tree_obj.api_tree
                if api_tree.processor_lang == "2":
                    response["code"] = api_tree.api_caller
                else:
                    response["code"] = API_TREE_BASE_JAVA_CODE
            elif processor == "post":
                post_processor = tree_obj.post_processor
                if post_processor.processor_lang == "2":
                    response["code"] = post_processor.function
                else:
                    response["code"] = POST_PROCESSOR_BASE_JAVA_CODE
            else:
                pipe_processor = tree_obj.pipe_processor
                if pipe_processor.processor_lang == "2":
                    response["code"] = pipe_processor.function
                else:
                    response["code"] = PIPE_PROCESSOR_BASE_JAVA_CODE
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_updated_java_code: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response


"""
function: get_updated_php_code
input params:
    is_new: It is true if a new processor requested.
    tree_obj: It is the tree obj.
    processor: It denotest the type of processor.
output:
    response: Returns the updated code in node for choosen processor of current tree.

This function is used to find updated code in php for choosen processor of current tree.
"""


def get_updated_php_code(is_new, tree_obj, processor):
    response = {}

    try:
        if str(is_new) == "True":
            if processor == "api":
                response["code"] = API_TREE_BASE_PHP_CODE
            elif processor == "post":
                response["code"] = POST_PROCESSOR_BASE_PHP_CODE
            else:
                response["code"] = PIPE_PROCESSOR_BASE_PHP_CODE
        else:
            if processor == "api":
                api_tree = tree_obj.api_tree
                if api_tree.processor_lang == "3":
                    response["code"] = api_tree.api_caller
                else:
                    response["code"] = API_TREE_BASE_PHP_CODE
            elif processor == "post":
                post_processor = tree_obj.post_processor
                if post_processor.processor_lang == "3":
                    response["code"] = post_processor.function
                else:
                    response["code"] = POST_PROCESSOR_BASE_PHP_CODE
            else:
                pipe_processor = tree_obj.pipe_processor
                if pipe_processor.processor_lang == "3":
                    response["code"] = pipe_processor.function
                else:
                    response["code"] = PIPE_PROCESSOR_BASE_PHP_CODE
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_updated_php_code: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response


"""
function: get_updated_javascript_code
input params:
    is_new: It is true if a new processor requested.
    tree_obj: It is the tree obj.
    processor: It denotest the type of processor.
output:
    response: Returns the updated code in node for choosen processor of current tree.

This function is used to find updated code in JS for choosen processor of current tree.
"""


def get_updated_javascript_code(is_new, tree_obj, processor):
    response = {}

    try:
        if str(is_new) == "True":
            if processor == "api":
                response["code"] = API_TREE_BASE_JS_CODE
            elif processor == "post":
                response["code"] = POST_PROCESSOR_BASE_JS_CODE
            else:
                response["code"] = PIPE_PROCESSOR_BASE_JS_CODE
        else:
            if processor == "api":
                api_tree = tree_obj.api_tree
                if api_tree.processor_lang == "4":
                    response["code"] = api_tree.api_caller
                else:
                    response["code"] = API_TREE_BASE_JS_CODE
            elif processor == "post":
                post_processor = tree_obj.post_processor
                if post_processor.processor_lang == "4":
                    response["code"] = post_processor.function
                else:
                    response["code"] = POST_PROCESSOR_BASE_JS_CODE
            else:
                pipe_processor = tree_obj.pipe_processor
                if pipe_processor.processor_lang == "4":
                    response["code"] = pipe_processor.function
                else:
                    response["code"] = PIPE_PROCESSOR_BASE_JS_CODE
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_updated_javascript_code: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response


"""
function: get_dynamic_variables
input params:
    code: Existing code of processor in console.
output:
    response: Returns the list of dictionay, which denotes the variables accessed from Data model.

If user trying to access the variables saved in Data model, then this function return the list of all variable.
"""


def get_dynamic_variables(code):
    logger.info("Into get_dynamic_variables...", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    dynamic_variable = []
    try:
        left_split_list = code.split("{/")
        for left_split in left_split_list:

            if "/}" in left_split:

                variable_name = left_split.split("/}")[0].strip()
                dynamic_variable.append({"key": variable_name, "value": ""})

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    logger.info("Exit from get_dynamic_variables...", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return dynamic_variable


"""
function: replace_data_values_console
input params:
    code: Existing code of processor in console.
    dynamic_variables_list: variable present in data model.
output:
    response: Returns the updated code after replacing the dynamic variables.

"""


def replace_data_values_console(code, dynamic_variables_list):
    logger.info("Into replace_data_values_console...", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    try:
        left_split_list = code.split("{/")
        for left_split in left_split_list:

            if "/}" in left_split:

                variable_name = left_split.split("/}")[0].strip()

                value = "None"

                if variable_name in dynamic_variables_list:
                    value = dynamic_variables_list[variable_name]

                variable_name = "{/" + str(variable_name) + "/}"

                code = code.replace(str(variable_name), str(value))

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ENGINE]: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    logger.info("Exit from replace_data_values_console...", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return code


def PackageInstaller(request):
    request.session["EASYCHAT_VERSION"] = settings.EASYCHAT_VERSION
    request.session[
        "EASYCHAT_DATE_OF_RELEASE"] = settings.EASYCHAT_DATE_OF_RELEASE
    if is_allowed(request, [BOT_BUILDER_ROLE]):

        if not check_access_for_user(request.user, None, "Intent Related", "overall"):
            return HttpResponseNotFound("You do not have access to this page")

        if request.user.is_superuser or request.user.supervisor:
            user_obj = User.objects.get(username=request.user.username)
            bots = Bot.objects.filter(users__in=[user_obj])

            package_managers = []

            if user_obj.package_reviewer:
                package_managers = PackageManager.objects.all().order_by('-request_datetime')
            else:
                package_managers = PackageManager.objects.filter(
                    request_user=user_obj).order_by('-request_datetime')

            return render(request, "EasyChatApp/package_installer.html", {
                "bots": bots,
                "package_managers": package_managers
            })
        else:
            # return HttpResponse("Invalid Access")
            return render(request, 'EasyChatApp/error_404.html')
    else:
        return HttpResponseRedirect("/chat/login")


class SubmitPackageInstallRequestAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def send_review_mail(self, package_manager_obj):
        for user_obj in User.objects.filter(package_reviewer=True):
            send_approval_mail_for_package_installation(
                package_manager_obj, user_obj.email)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = json.loads(DecryptVariable(data["data"]))

            validation_obj = EasyChatInputValidation()

            bot_id = validation_obj.remo_html_from_string(data["bot_id"])
            package = validation_obj.remo_html_from_string(data["package"])
            description = validation_obj.remo_html_from_string(
                data["description"])

            user_obj = User.objects.get(username=request.user.username)
            bot_obj = Bot.objects.get(pk=int(bot_id))

            package_manager_obj = PackageManager.objects.create(bot=bot_obj,
                                                                request_user=user_obj,
                                                                package=package,
                                                                description=description,
                                                                request_datetime=datetime.now())

            thread = threading.Thread(target=self.send_review_mail, args=(
                package_manager_obj, ), daemon=True)
            thread.start()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SubmitPackageInstallRequestAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SubmitPackageInstallRequest = SubmitPackageInstallRequestAPI.as_view()


class TakeActionPackageInstallationAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def install_package(self, package_manager_obj):
        try:
            output = subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_manager_obj.package])
            if output == 0:
                package_manager_obj.is_installed = True
            else:
                package_manager_obj.is_installed = False

            package_manager_obj.save()
            logger.info("Package installed successfully.", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("install_package ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = json.loads(DecryptVariable(data["data"]))

            validation_obj = EasyChatInputValidation()

            package_manager_id = validation_obj.remo_html_from_string(
                data["package_manager_id"])
            action = validation_obj.remo_html_from_string(data["action"])
            user_obj = User.objects.get(username=request.user.username)

            package_manager_obj = PackageManager.objects.get(
                pk=int(package_manager_id))

            if action == "approved":
                package_manager_obj.status = "approved"
                thread = threading.Thread(target=self.install_package, args=(
                    package_manager_obj, ), daemon=True)
                thread.start()
            else:
                package_manager_obj.status = "denied"

            package_manager_obj.approved_by = user_obj
            package_manager_obj.approved_datetime = datetime.now()
            package_manager_obj.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("TakeActionPackageInstallationAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


TakeActionPackageInstallation = TakeActionPackageInstallationAPI.as_view()


class UpdateLogFileAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = json.loads(DecryptVariable(data["json_string"]))
            log_file = open(APP_LOG_FILENAME, 'r')
            line_count = 0
            response["code"] = ""
            temp_file_list = []

            for line in reversed(list(log_file)):

                line_count += 1
                if line_count <= LOGTAILER_LINES:
                    temp_file_list.append(line)
                else:
                    break

            temp_file_list = reversed(temp_file_list)
            for line in temp_file_list:
                response["code"] += line

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateLogFileAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateLogFile = UpdateLogFileAPI.as_view()


def WhatsAppSimulator(request):
    request.session["EASYCHAT_VERSION"] = settings.EASYCHAT_VERSION
    request.session[
        "EASYCHAT_DATE_OF_RELEASE"] = settings.EASYCHAT_DATE_OF_RELEASE
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        if not check_access_for_user(request.user, None, "Intent Related", "overall"):
            return HttpResponseNotFound("You do not have access to this page")
        if request.user.supervisor:
            code = WHATSAPP_REQUEST_PACKET
            return render(request, "EasyChatApp/whatsapp_simulator.html", {
                "code": code
            })
        else:
            # return HttpResponse("Invalid Access")
            return render(request, 'EasyChatApp/error_404.html')
    else:
        return HttpResponseRedirect("/chat/login")


class GetWhatsAppSimulatorResponseAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["response_message"] = ""
        try:
            data = request.data
            data = json.loads(DecryptVariable(data["data"]))

            mobile_number = data["mobile_number"]
            end_point = data["end_point"]
            message = data["message"]
            payload = data["request_packet"]
            response_message = get_whatsapp_simulator_response(
                mobile_number, end_point, message, payload)
            response["response_message"] = response_message
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetWhatsAppSimulatorResponseAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


def CommonUtils(request):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            bot_pk = request.GET['bot_pk']
            bot_obj = Bot.objects.get(pk=bot_pk)
            code = ""
            edit_info = "Please click on Check Last Edit before saving"
            enable_save = "False"
            last_modified = ""
            if (request.method == "GET"):
                if("checklastedit" in request.GET):
                    edit_info = "Please check if changes are made by someone else and save here"
                    enable_save = "True"
                try:
                    common_utils_obj = CommonUtilsFile.objects.get(bot=bot_obj)
                    code = common_utils_obj.code
                    last_modified = common_utils_obj.last_opened
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Common Utils: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    last_modified = ""
                    pass
            elif(request.method == "POST"):
                data = DecryptVariable(request.POST['json_string'])
                data = json.loads(data)
                code = data["code"]
                if(data["to_save"] == "True"):
                    bot_obj = Bot.objects.get(pk=bot_pk)
                    if CommonUtilsFile.objects.filter(bot=bot_obj):
                        common_utils_obj = CommonUtilsFile.objects.get(
                            bot=bot_obj)
                        common_utils_obj.code = code
                        common_utils_obj.last_opened = datetime.now()
                        common_utils_obj.save()
                    else:
                        common_utils_obj = CommonUtilsFile.objects.create(
                            bot=bot_obj, code=code)
                    last_modified = common_utils_obj.last_opened

            config_obj = Config.objects.all()[0]
            system_commands = json.loads(
                config_obj.system_commands.replace("'", '"'))
            return render(request, "EasyChatApp/common_utils.html", {
                "bot_pk": bot_pk,
                "code": code,
                "last_modified": last_modified,
                "edit_info": edit_info,
                "enable_save": enable_save,
                "system_commands": system_commands,
                "expanded_logo": True,
            })
        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("CommonUtils ! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def ChatbotCustomJs(request):
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        bot_pk = request.GET['bot_pk']
        code = ""
        static_path = os.path.join(
            BASE_DIR, 'EasyChatApp/static/EasyChatApp/js/')
        name = static_path + 'theme3_' + bot_pk + '.js'
        if (request.method == "GET"):
            if os.path.isfile(name) == False:
                create_custom_js_file(bot_pk)
                theme3_js_file = open(
                    settings.BASE_DIR + "/EasyChatApp/static/EasyChatApp/js/theme3.js", "r")
                code = theme3_js_file.read()
            else:
                chatbot_js_file = open(name, 'r')
                with chatbot_js_file as file:
                    for line in file:
                        code = code + line
                chatbot_js_file.close()
        return render(request, "EasyChatApp/chatbot_custom_js.html", {
            "bot_pk": bot_pk,
            "code": code,
            "expanded_logo": True,
        })
    else:
        return HttpResponseRedirect("/chat/login")


def ChatbotCustomCss(request):
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        bot_pk = request.GET['bot_pk']
        code = ""
        bot_obj = Bot.objects.get(pk=int(bot_pk))
        theme_name = bot_obj.default_theme.name
        theme_id = theme_name.split("_")[1]
        static_path = os.path.join(
            BASE_DIR, 'EasyChatApp/static/EasyChatApp/css/')
        name = static_path + 'theme' + \
            str(theme_id) + "_" + str(bot_pk) + '.css'
        if (request.method == "GET"):
            if os.path.isfile(name) == False:
                create_custom_css_file(bot_pk, theme_name)
                css_file = open(
                    settings.BASE_DIR + "/EasyChatApp/static/EasyChatApp/css/theme" + str(theme_id) + ".css", "r")
                code = css_file.read()
                css_file.close()
            else:
                custom_css_file = open(name, 'r')
                with custom_css_file as file:
                    for line in file:
                        code = code + line
                custom_css_file.close()
        return render(request, "EasyChatApp/chatbot_custom_css.html", {
            "bot_pk": bot_pk,
            "code": code,
            "theme_id": theme_id,
            "bot_obj": bot_obj,
            "expanded_logo": True,
        })
    else:
        return HttpResponseRedirect("/chat/login")


class SaveChatbotCustomJsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)
            bot_id = data["bot_id"]
            code = data["code"]
            filename = 'EasyChatApp/static/EasyChatApp/js/theme3_' + \
                str(bot_id) + '.js'

            if path.exists(settings.BASE_DIR + "/" + filename):
                # Saving in main static folder
                static_file = open(settings.BASE_DIR + "/" + filename, "w")
                static_file.write(code)
                static_file.close()

                # Saving the same file in static folder
                try:
                    static_file = open(
                        settings.BASE_DIR + "/static/EasyChatApp/js/theme3_" + str(bot_id) + ".js", "w")
                    static_file.write(code)
                    static_file.close()
                except Exception:
                    pass

                response["status"] = 200
                response["message"] = "success"
            else:
                response["status"] = 101
                response["message"] = "Matching file doesn't exists"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveChatbotCustomJsAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveChatbotCustomJs = SaveChatbotCustomJsAPI.as_view()


class SaveChatbotCustomCssAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)
            bot_id = data["bot_id"]
            code = data["code"]
            bot_obj = Bot.objects.get(pk=int(bot_id))
            theme_name = bot_obj.default_theme.name
            theme_id = theme_name.split("_")[1]
            filename = 'EasyChatApp/static/EasyChatApp/css/theme' + \
                str(theme_id) + "_" + str(bot_id) + ".css"

            if path.exists(settings.BASE_DIR + "/" + filename):
                # Saving in main static folder
                static_file = open(settings.BASE_DIR + "/" + filename, "w")
                static_file.write(code)
                static_file.close()

                # Saving the same file in static folder
                try:
                    static_file = open(
                        settings.BASE_DIR + "/static/EasyChatApp/css/theme" + str(theme_id) + "_" + str(bot_id) + ".css", "w")
                    static_file.write(code)
                    static_file.close()
                except Exception:
                    pass

                response["status"] = 200
                response["message"] = "success"
            else:
                response["status"] = 101
                response["message"] = "Matching file doesn't exists"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveChatbotCustomCssAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveChatbotCustomCss = SaveChatbotCustomCssAPI.as_view()


def APIList(request):
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        try:
            bot_pk = request.GET["bot_pk"]
            api_name_url_used = {}

            bot_obj = Bot.objects.filter(pk=int(bot_pk))
            intent_obj = Intent.objects.filter(bots__in=bot_obj)

            intent_tree_name_tuple = []
            # every tuple will include:
            # intent pk
            # tree pk
            # api tree pk
            # api tree name
            # bot pk
            # type of processor
            # intent name
            # tree name

            for item in intent_obj:
                tree_pk_list = []
                intent_name = item
                tree_name = item.tree.name
                if item.tree.api_tree != None and item.tree.api_tree.apis_used != "":
                    intent_tree_name_tuple.append(
                        (item.pk, item.tree.pk, item.tree.api_tree.pk, item.tree.api_tree.name, bot_pk, "api", intent_name, tree_name))

                if item.tree.post_processor != None and item.tree.post_processor.apis_used != "":
                    intent_tree_name_tuple.append(
                        (item.pk, item.tree.pk, item.tree.post_processor.pk, item.tree.post_processor.name, bot_pk, "post", intent_name, tree_name))

                if item.tree.pipe_processor != None and item.tree.pipe_processor.apis_used != "":
                    intent_tree_name_tuple.append(
                        (item.pk, item.tree.pk, item.tree.pipe_processor.pk, item.tree.pipe_processor.name, bot_pk, "pipe", intent_name, tree_name))

                get_parent_child_pair_intent(item.tree, tree_pk_list)
                for iterator in tree_pk_list:
                    tree_name = iterator[0].name
                    if iterator[1] == "api":
                        intent_tree_name_tuple.append(
                            (item.pk, iterator[0].pk, iterator[0].api_tree.pk, iterator[0].api_tree.name, bot_pk, iterator[1], intent_name, tree_name))
                    if iterator[1] == "post":
                        intent_tree_name_tuple.append(
                            (item.pk, iterator[0].pk, iterator[0].post_processor.pk, iterator[0].post_processor.name, bot_pk, iterator[1], intent_name, tree_name))
                    if iterator[1] == "pipe":
                        intent_tree_name_tuple.append(
                            (item.pk, iterator[0].pk, iterator[0].pipe_processor.pk, iterator[0].pipe_processor.name, bot_pk, iterator[1], intent_name, tree_name))

            for item in intent_tree_name_tuple:
                try:
                    if item[5] == "api":
                        api_name_url_used[item] = ApiTree.objects.get(
                            pk=item[2]).apis_used.split("****")[:-1]
                    else:
                        api_name_url_used[item] = Processor.objects.get(
                            pk=item[2]).apis_used.split("****")[:-1]
                except Exception as e:  # noqa: F841
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("ERROR IN PROCESSOR GET: %s", str(e), str(exc_tb.tb_lineno), extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            return render(request, "EasyChatApp/platform/api_used_list.html", {
                "api_name_url_used": api_name_url_used
            })

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("API LIST RENDER VIEW: %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return render(request, 'EasyChatApp/error_404.html')
    else:
        return HttpResponseRedirect("/chat/login")


GetWhatsAppSimulatorResponse = GetWhatsAppSimulatorResponseAPI.as_view()


def FieldProcessorConsole(request):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Intent Related", "overall"):
                return render(request, 'EasyChatApp/unauthorized.html')
            
            if request.user.supervisor and request.user.is_staff:
                validation_obj = EasyChatInputValidation()

                field_id = request.GET["field_id"]
                field_id = validation_obj.remo_html_from_string(field_id)

                bot_pk = request.GET["bot_pk"]
                bot_pk = validation_obj.remo_html_from_string(bot_pk)
                bot_obj = Bot.objects.get(pk=int(bot_pk))
                if request.user not in bot_obj.users.all():
                    return render(request, 'EasyChatApp/unauthorized.html')
                lang = "1"

                field_processor_obj = FormWidgetFieldProcessor.objects.filter(
                    field_id=field_id)
                if field_processor_obj.exists():
                    field_processor_obj = field_processor_obj.first()
                    name = field_processor_obj.name

                    code = check_common_utils_line(
                        field_processor_obj.function, bot_pk)
                    lang = field_processor_obj.processor_lang
                else:
                    name = "asdhs524fdbghdagfht52eg2fc"
                    code = get_common_utils_file_code(bot_pk)
                    code += FIELD_PROCESSOR_BASE_PYTHON_CODE

                dynamic_variable = get_dynamic_variables(code)

                config_obj = Config.objects.all()[0]
                system_commands = json.loads(
                    config_obj.system_commands.replace("'", '"'))
                
                mail_sent_to_list = json.loads(bot_obj.mail_sent_to_list)["items"]
                api_fail_email_configured = False

                if bot_obj.is_api_fail_email_notifiication_enabled:
                    api_fail_email_configured = True

                return render(request, "EasyChatApp/field_processor.html", {
                    "name": name,
                    "code": code,
                    "processor": "field",
                    "language_list": LANGUAGE_CHOICES,
                    "lang": lang,
                    "dynamic_variable": dynamic_variable,
                    "system_commands": system_commands,
                    "mail_sent_to_list": mail_sent_to_list,
                    "bot_obj": bot_obj,
                    "api_fail_email_configured": api_fail_email_configured,
                    "expanded_logo": True,
                })
            else:
                # return HttpResponse("Invalid Access")
                return render(request, 'EasyChatApp/unauthorized.html')
        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("FieldProcessorConsole: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return render(request, 'EasyChatApp/error_404.html')


class UpdateFormWidgetDependentFieldsAPI(APIView):
    # permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)
            validation_obj = EasyChatInputValidation()

            field_id = data["field_id"]
            field_id = validation_obj.remo_html_from_string(field_id)

            channel_name = data["channel_name"]
            channel_name = validation_obj.remo_html_from_string(channel_name)

            selected_option = data["selected_option"]
            selected_option = validation_obj.remo_html_from_string(
                selected_option)

            user_id = data['user_id']
            user_id = validation_obj.remo_html_from_string(user_id)

            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(str(bot_id))

            src = data['web_page_source']
            src = validation_obj.remo_html_from_string(str(src))

            field_processor_obj = FormWidgetFieldProcessor.objects.filter(
                field_id=field_id)
            if field_processor_obj.exists():
                field_processor_obj = field_processor_obj.first()
                bot_obj = Bot.objects.get(pk=bot_id)
                user = Profile.objects.get(user_id=user_id, bot=bot_obj)
                api_caller = replace_data_values(
                    user, field_processor_obj.function, src, channel_name, bot_id)
                output = execute_code_under_time_limit(
                    field_processor_obj.processor_lang, api_caller, bot_obj, selected_option, True)
                response["options"] = '$$$'.join(output['options'])
                response["text_field_value"] = output['text_field_value']
                response["range_slider_min_value"] = output['range_slider_min_value']
                response["range_slider_max_value"] = output['range_slider_max_value']
                response["phone_widget_data"] = output['phone_widget_data']
                response["field_id"] = field_id
                response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateFormWidgetDependentFieldsAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateFormWidgetDependentFields = UpdateFormWidgetDependentFieldsAPI.as_view()


class FormWidgetAPIIntegrationStatusAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            field_ids = data["field_ids"]
            response["api_integrated_fields"] = []
            response["status"] = 200

            for field_id in field_ids:
                if FormWidgetFieldProcessor.objects.filter(field_id=field_id).exists():
                    response["api_integrated_fields"].append(field_id)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("FormWidgetAPIIntegrationStatusAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


FormWidgetAPIIntegrationStatus = FormWidgetAPIIntegrationStatusAPI.as_view()


class ResetFormWidgetAPIIntegrationAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            field_id = data["field_id"]

            field_ids = field_id.split('$$$')

            for id in field_ids:
                if FormWidgetFieldProcessor.objects.filter(field_id=id).exists():
                    FormWidgetFieldProcessor.objects.filter(
                        field_id=id).delete()

            response["status"] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ResetFormWidgetAPIIntegrationAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ResetFormWidgetAPIIntegration = ResetFormWidgetAPIIntegrationAPI.as_view()
