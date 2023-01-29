from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render, HttpResponseRedirect, HttpResponse

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_analytics import *

from django.http import HttpResponseNotFound
import json
import logging

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def FormAssistPage(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Form Assist Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            user_obj = User.objects.get(username=str(request.user.username))
            form_assist_bot_objs = get_form_assist_uat_bots(user_obj)

            selected_bot_obj = None
            if "bot_pk" in request.GET:
                bot_pk = request.GET["bot_pk"]
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

            if selected_bot_obj == None:
                return HttpResponse("Page not Found")

            bot_obj = None
            intent_master_objs = []
            form_assist_objs = []
            if "bot_pk" in request.GET:
                bot_id = request.GET["bot_pk"]
                if not check_access_for_user(request.user, bot_id, "Form Assist Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                bot_obj = Bot.objects.get(
                    pk=int(bot_id), is_deleted=False, is_uat=True, is_form_assist_enabled=True)
                intent_master_objs = Intent.objects.filter(bots__in=[
                                                           bot_obj], is_deleted=False, is_hidden=False).distinct()
                form_assist_objs = FormAssist.objects.filter(
                    bot=bot_obj, intent__is_deleted=False)

            return render(request, 'EasyChatApp/platform/form_assist.html', {
                "selected_bot_obj": selected_bot_obj,
                "form_assist_bot_objs": form_assist_bot_objs,
                "intent_master_objs": intent_master_objs,
                "form_assist_objs": form_assist_objs,
                "bot_obj": bot_obj
            })
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("FormAssistPage ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        return HttpResponse("Page not Found")


class FormAssistResponseAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            tag_id = data['tag_id']
            bot_id = data['bot_id']
            bot_obj = Bot.objects.get(
                pk=int(bot_id), is_deleted=False, is_uat=True, is_form_assist_enabled=True)
            form_assist_obj = FormAssist.objects.get(
                tag_id=str(tag_id), bot=bot_obj)

            form_assist_intent_name = form_assist_obj.intent.name
            form_assist_id = form_assist_obj.pk

            response["form_assist_intent_name"] = form_assist_intent_name
            response["form_assist_id"] = str(form_assist_id)
            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FormAssistAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        return Response(data=response)


class SaveFormAssistTagAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)
            tag_id = data["form_assist_tag_id"]
            bot = data["bot_id"]
            form_assist_intent = data["form_assist_intent"]
            form_assist_popup_timer = data["form_assist_popup_timer"]

            if not form_assist_popup_timer.isnumeric():
                response["status"] = 300
                response["message"] = "Form assist popup timer should contain only numbers"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)            

            bot_obj = Bot.objects.get(
                pk=int(bot), is_deleted=False, is_form_assist_enabled=True, is_uat=True)

            intent_obj = Intent.objects.get(pk=int(form_assist_intent),
                                            bots=bot_obj,
                                            is_deleted=False,
                                            is_hidden=False)

            check_form_assist_tag_id = FormAssist.objects.filter(
                tag_id=str(tag_id), bot=bot_obj)
            if check_form_assist_tag_id:
                response["status"] = 301
            else:
                check_form_assist_intent_id = FormAssist.objects.filter(
                    intent=intent_obj, bot=bot_obj)
                if check_form_assist_intent_id:
                    response["status"] = 301
                else:
                    intent_obj.is_form_assist_enabled = True
                    intent_obj.save()
                    form_assist_obj = FormAssist.objects.create(tag_id=str(tag_id),
                                                                intent=intent_obj,
                                                                bot=bot_obj,
                                                                popup_timer=form_assist_popup_timer)
                    form_assist_obj.save()
                    response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveFormAssistTagAPI : %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class EditFormAssistTagAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)
            tag_id = data["form_assist_tag_id"]
            bot = data["bot_id"]
            form_assist_intent = data["form_assist_intent"]
            form_assist_id = data["form_assist_id"]
            form_assist_popup_timer = data["form_assist_popup_timer"]

            if not form_assist_popup_timer.isnumeric():
                response["status"] = 300
                response["message"] = "Form assist popup timer should contain only numbers"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)    

            bot_obj = Bot.objects.get(
                pk=int(bot), is_deleted=False, is_form_assist_enabled=True, is_uat=True)

            intent_obj = Intent.objects.get(pk=int(form_assist_intent),
                                            bots=bot_obj,
                                            is_deleted=False,
                                            is_hidden=False)

            check_form_assist_tag_id = FormAssist.objects.filter(
                tag_id=str(tag_id), bot=bot_obj).exclude(pk=form_assist_id)
            if check_form_assist_tag_id:
                response["status"] = 301
            else:
                check_form_assist_intent_id = FormAssist.objects.filter(
                    intent=intent_obj, bot=bot_obj).exclude(pk=form_assist_id)
                if check_form_assist_intent_id:
                    response["status"] = 301
                else:
                    form_assist_obj = FormAssist.objects.get(pk=form_assist_id)

                    form_assist_obj.intent.is_form_assist_enabled = False
                    form_assist_obj.intent.save()
                    intent_obj.is_form_assist_enabled = True
                    intent_obj.save()

                    form_assist_obj.tag_id = tag_id
                    form_assist_obj.bot = bot_obj
                    form_assist_obj.intent = intent_obj
                    form_assist_obj.popup_timer = form_assist_popup_timer
                    form_assist_obj.save()
                    response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EditFormAssistTagAPI : %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DeleteFormAssistTagAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            form_assist_id = data["form_assist_id"]
            bot_id = data["bot_id"]
            bot_obj = Bot.objects.get(
                pk=int(bot_id), is_deleted=False, is_form_assist_enabled=True, is_uat=True)
            instance = FormAssist.objects.get(
                pk=int(form_assist_id), bot=bot_obj)
            instance.intent.is_form_assist_enabled = False
            instance.intent.save()
            instance.delete()
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteFormAssistTagAPI : %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetFormAssistTagsAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            bot_id = data['bot_id']
            bot_obj = Bot.objects.get(
                pk=int(bot_id), is_deleted=False, is_uat=True, is_form_assist_enabled=True)
            form_assist_objs = FormAssist.objects.filter(bot=bot_obj)

            form_assist_tags = {}

            for form_assist_obj in form_assist_objs:
                form_assist_tags[form_assist_obj.tag_id] = form_assist_obj.pk

            response["form_assist_tags"] = form_assist_tags
            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FormAssistAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        return Response(data=response)


GetFormAssistTags = GetFormAssistTagsAPI.as_view()

FormAssistResponse = FormAssistResponseAPI.as_view()

SaveFormAssistTag = SaveFormAssistTagAPI.as_view()

DeleteFormAssistTag = DeleteFormAssistTagAPI.as_view()

EditFormAssistTag = EditFormAssistTagAPI.as_view()
