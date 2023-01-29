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

from EasyChatApp.utils import *
from EasyChatApp.models import Bot
from EasyChatApp.utils_paraphrase import make_final_variations
from EasyChatApp.utils_custom_encryption import *

import json
import logging


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class GetVariationsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)
            intent_name = data["intent_name"].strip()
            bot_id = data["bot_id"].strip()
            page_no = int(data["page_no"])
            get_all_results = True
            is_synonyms_included_in_paraphrase = Bot.objects.get(
                pk=int(bot_id)).is_synonyms_included_in_paraphrase
            response["more_var"] = False
            if intent_name != "":
                general_var_list, syn_var_list = make_final_variations(
                    intent_name, is_synonyms_included_in_paraphrase, get_all_results)
                total_list = []
                if (page_no * 15 < len(general_var_list + syn_var_list)):
                    total_list = general_var_list + syn_var_list
                    start = 15 * (page_no - 1)
                    end = 15 * (page_no)
                    total_list = total_list[start:end]
                    response["more_var"] = True
                else:
                    total_list = general_var_list + syn_var_list
                response["variation_list"] = total_list
            else:
                response["variation_list"] = []
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetVariationsAPI : %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

GetVariations = GetVariationsAPI.as_view()
