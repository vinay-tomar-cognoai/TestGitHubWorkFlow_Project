from django.shortcuts import redirect, HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render, HttpResponseRedirect

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


"""
def LeadGenerationPage(request):  # noqa: N802
    return render(request, 'EasyChatApp/platform/lead_generation.html')
"""


def LeadGenerationPage(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Lead Gen Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            selected_bot_obj = None
            if "bot_pk" in request.GET:
                bot_pk = request.GET["bot_pk"]
                if not check_access_for_user(request.user, bot_pk, "Lead Gen Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

            if selected_bot_obj == None:
                return HttpResponse("Page not Found")

            user_obj = User.objects.get(username=str(request.user.username))
            lead_generation_bot_objs = get_lead_generation_uat_bots(user_obj)
            bot_obj = None
            lead_generation_objs = []
            if "bot_pk" in request.GET:
                bot_id = request.GET["bot_pk"]
                if not check_access_for_user(request.user, bot_pk, "Lead Gen Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                bot_obj = Bot.objects.get(
                    pk=int(bot_id), is_deleted=False, is_uat=True, is_lead_generation_enabled=True)
            lead_generation_objs = LeadGeneration.objects.filter(bot=bot_obj)

            return render(request, 'EasyChatApp/platform/lead_generation.html', {
                "lead_generation_bot_objs": lead_generation_bot_objs,
                "lead_generation_objs": lead_generation_objs,
                "bot_obj": bot_obj,
                "selected_bot_obj": selected_bot_obj
            })
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("LeadGenerationPage ! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        # return HttpResponse("Page not Found")
        return render(request, 'EasyChatApp/error_404.html')
