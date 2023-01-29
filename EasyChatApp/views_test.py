from EasyChatApp.utils_validation import EasyChatInputValidation
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.shortcuts import HttpResponse, HttpResponseRedirect, render

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_analytics import *

import logging


logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def DeleteTestSentence(request, test_case_pk, sentence):  # noqa: N802
    try:
        if request.user.is_authenticated:
            user_obj = User.objects.get(username=request.user.username)
            test_case_obj = TestCase.objects.get(
                pk=test_case_pk, user=user_obj)
            index = test_case_obj.get_index(sentence)
            test_case_obj.remove_index(index)
            test_case_obj.save()
            return HttpResponseRedirect("/chat/test-chatbot/")
        else:
            # return HttpResponse("500")
            return render(request, 'EasyChatApp/error_500.html')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("DeleteTestSentence ! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return render(request, 'EasyChatApp/error_500.html')


class AddTestSentenceAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            validation_obj = EasyChatInputValidation()

            sentence = data['sentence']
            sentence = validation_obj.remo_html_from_string(sentence)
            intent_pk = data['intent_pk']
            intent_pk = validation_obj.remo_html_from_string(intent_pk)

            intent_obj = Intent.objects.get(pk=intent_pk, is_hidden=False)
            username = request.user.username
            user_obj = User.objects.get(username=username)

            test_case_obj = TestCase.objects.filter(
                intent=intent_obj, user=user_obj)

            if(len(test_case_obj) == 0):
                test_case_obj = TestCase.objects.create(
                    intent=intent_obj,
                    user=user_obj,
                )
                test_case_obj.add_sentence(sentence)
                test_case_obj.save()
            else:
                test_case_obj = test_case_obj[0]
                test_case_obj.add_sentence(sentence)
                test_case_obj.save()

            test_case_obj = TestCase.objects.filter(
                intent=intent_obj, user=user_obj)
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AddTestSentenceAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return Response(data=response)


class GetTestSentenceAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            # data = request.data
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            # bot_objs = Bot.objects.filter(users__in=[user_obj])
            # bot_objs = get_uat_bots(user_obj)
            # intent_objs = Intent.objects.filter(
            #     bots__in=bot_objs, is_deleted=False).distinct()

            test_case_obj_list = TestCase.objects.filter(user=user_obj)
            sentence_list = []
            is_active_list = []
            intent_list = []
            test_sentence_pk_list = []

            if(len(test_case_obj_list) != 0):
                for test_case_obj in test_case_obj_list:
                    test_case_sentence_list = test_case_obj.get_list()
                    test_case_is_active_list = test_case_obj.get_is_active_list()
                    iterator = 0
                    for sentence in test_case_sentence_list:
                        sentence_list.append(sentence)
                        is_active_list.append(test_case_is_active_list[iterator])
                        iterator += 1
                        test_sentence_pk_list.append(test_case_obj.pk)
                        intent_list.append({
                            "pk": test_case_obj.intent.pk,
                            "name": test_case_obj.intent.name,
                        })

            response['intent_list'] = intent_list
            response['sentence_list'] = sentence_list
            response['is_active_list'] = is_active_list
            response['test_sentence_pk_list'] = test_sentence_pk_list
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetTestSentenceAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SetTestSentenceActiveAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.get(username=username)
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            test_case_pk = data['test_sentence_pk']
            test_case_pk = validation_obj.remo_html_from_string(test_case_pk)
            sentence = data['sentence']
            sentence = validation_obj.remo_html_from_string(sentence)
            is_active = data['is_active']
            is_active = validation_obj.remo_html_from_string(is_active)

            if(is_active == "true"):
                is_active = True
            elif(is_active == "false"):
                is_active = False

            test_case_obj = TestCase.objects.get(
                pk=test_case_pk, user=user_obj)
            index = test_case_obj.get_index(sentence)
            test_case_obj.change_is_active(index, is_active)
            test_case_obj.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SetTestSentenceActiveAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

SetTestSentenceActive = SetTestSentenceActiveAPI.as_view()
AddTestSentence = AddTestSentenceAPI.as_view()
GetTestSentence = GetTestSentenceAPI.as_view()
