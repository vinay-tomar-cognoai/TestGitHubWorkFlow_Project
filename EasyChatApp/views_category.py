from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core import serializers

from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect, redirect
from django.http import HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_analytics import *
from EasyChatApp.constants import *

import json
import logging


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def CategoryPage(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            bot_objs = get_uat_bots(user_obj)

            if not check_access_for_user(request.user, None, "Categories", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            
            page_count = request.GET.get("count", MAX_MESSAGE_PER_PAGE)

            if page_count not in ["10", "25", "50", "75", "100"]:
                page_count = "10"

            selected_bot_obj = None
            if "bot_pk" in request.GET:
                bot_pk = request.GET["bot_pk"]
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

            if selected_bot_obj == None:
                return HttpResponse("Page not Found")

            bot_obj = None
            intent_master_objs = []
            category_objs = []
            if "bot_pk" in request.GET:
                bot_id = request.GET["bot_pk"]
                if not check_access_for_user(request.user, bot_id, "Categories"):
                    return HttpResponseNotFound("You do not have access to this page")
                bot_obj = Bot.objects.get(
                    pk=int(bot_id), is_deleted=False, is_uat=True)
                intent_master_objs = Intent.objects.filter(is_form_assist_enabled=False, bots__in=[
                                                           bot_obj], is_deleted=False).distinct()
                category_objs = Category.objects.filter(bot=bot_obj)

                if "page" in request.GET:
                    page = request.GET["page"]
                else:
                    page = 1

                paginator = Paginator(category_objs, page_count)

                try:
                    category_objs = paginator.page(page)
                except PageNotAnInteger:
                    category_objs = paginator.page(1)
                except EmptyPage:
                    category_objs = paginator.page(paginator.num_pages)
            else:
                return HttpResponseNotFound("You haven't provided valid bot id.")

            return render(request, 'EasyChatApp/platform/category.html', {
                "selected_bot_obj": selected_bot_obj,
                "bot_objs": bot_objs,
                "intent_master_objs": intent_master_objs,
                "category_objs": category_objs,
                "bot_obj": bot_obj,
                "character_limit_small_text": CHARACTER_LIMIT_SMALL_TEXT,
                "bot_id": bot_id
            })
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("CategoryPage %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
        # return HttpResponse("Page not Found")
        return render(request, 'EasyChatApp/error_404.html')


class SaveCategoryAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            category_id = data["category_id"]
            category_name = data["category_name"]
            category_name = category_name.strip()
            bot = data["bot_id"]

            validation_object = EasyChatInputValidation()

            category_name = validation_object.remo_complete_html_and_special_tags(category_name)

            if re.sub("[!?&]", "", category_name).strip() == "":
                response["status"] = "400"
                response["message"] = "Bot name should have atleast one alphanumeric character."

            if len(category_name) > CHARACTER_LIMIT_SMALL_TEXT:
                response["status"] = "400"
                response["message"] = "Exceeding character limit of " + \
                    str(CHARACTER_LIMIT_SMALL_TEXT) + " characters"

            if response["status"] == "400":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot_obj = Bot.objects.get(
                pk=int(bot), is_deleted=False, is_uat=True)

            if Category.objects.filter(name__iexact=str(category_name), bot=bot_obj).count():
                response["status"] = 301
            else:
                if category_id == "":
                    category_obj = Category.objects.create(
                        name=str(category_name), bot=bot_obj)
                else:
                    category_obj = Category.objects.get(pk=int(category_id))
                    category_obj.name = str(category_name)
                    category_obj.save()

                response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCategoryAPI : %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DeleteCategoryAPI(APIView):
    
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:

            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)
            context_id = data["category_id"]
            bot_id = data["bot_id"]
            bot_obj = Bot.objects.get(
                pk=int(bot_id), is_deleted=False, is_uat=True)
            category_obj = Category.objects.get(
                pk=int(context_id), bot=bot_obj)
            category_obj.delete()
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteCategoryAPI : %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveCategory = SaveCategoryAPI.as_view()
DeleteCategory = DeleteCategoryAPI.as_view()
