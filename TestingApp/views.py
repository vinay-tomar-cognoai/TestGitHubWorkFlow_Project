from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from EasyChatApp.utils_validation import EasyChatInputValidation

# Create your views here.

from TestingApp.models import BotQATesting, Tester, BotQATestCase, BotQATestCaseFlow, timezone
from EasyChatApp.models import EasyChatAppFileAccessManagement
from TestingApp.utils import *

import logging

logger = logging.getLogger(__name__)


def Home(request):
    return redirect("/automation/home/")


# def AutomationLogin(request):
#     return render(request, "TestingApp/login.html")


def AutomationLogout(request):
    logout(request)
    return redirect("/")


@login_required
def AutomationAPI(request):
    return render(request, "TestingApp/query_api.html")


@login_required
def AutomationHome(request):
    try:
        bot_tester = Tester.objects.get(user__username=request.user.username)
        bots = BotQATesting.objects.filter(created_by=bot_tester, is_deleted=False)
        return render(request, "TestingApp/automation_home.html", {
            "bots": bots
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AutomationHome: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        return HttpResponse(status=404)


@login_required
def CreateNewAutomationBot(request):
    try:
        bot_tester = Tester.objects.get(user__username=request.user.username)

        if request.method == "POST":

            validation_obj = EasyChatInputValidation()

            bot_id = request.POST["new-bot-id"]
            bot_id = validation_obj.remo_html_from_string(str(bot_id))

            bot_name = request.POST["new-bot-name"]

            bot_name = validation_obj.remo_html_from_string(str(bot_name))
            bot_name = validation_obj.remo_unwanted_characters(str(bot_name))

            if not validation_obj.is_valid_bot_name(bot_name):
                return HttpResponse(status=400)

            bot_domain = request.POST["new-bot-hosted-domain"]
            if not bot_id.isnumeric():
                return HttpResponse(status=400)

            if not validation_obj.is_valid_url(bot_domain):
                return HttpResponse(status=400)

            qa_testing_bots = BotQATesting.objects.filter(bot_id=bot_id)

            if qa_testing_bots.count() == 0 or True:
                BotQATesting.objects.create(bot_id=bot_id,
                                            bot_name=bot_name,
                                            bot_domain=bot_domain,
                                            created_by=bot_tester)

            return redirect("/automation/home/")
        else:
            return HttpResponse(status=400)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("CreateNewAutomationBot: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        return HttpResponse(status=404)


@login_required
def EditAutomationBot(request, pk):
    try:
        bot_tester = Tester.objects.get(user__username=request.user.username)

        if request.method == "POST":
            bot_id = request.POST["edit-bot-id-" + str(pk)]
            bot_name = request.POST["edit-bot-name-" + str(pk)]
            bot_domain = request.POST["edit-bot-hosted-domain-" + str(pk)]

            validation_obj = EasyChatInputValidation()
            bot_id = bot_id + ""
            if not bot_id.isnumeric():
                return HttpResponse(status=400)

            bot_name = validation_obj.remo_html_from_string(bot_name)
            bot_name = validation_obj.remo_unwanted_characters(bot_name)

            if not validation_obj.is_valid_bot_name(bot_name):
                return HttpResponse(status=400)

            if not validation_obj.is_valid_url(bot_domain):
                return HttpResponse(status=400)

            qa_testing_bot = BotQATesting.objects.get(
                pk=pk, created_by=bot_tester)
            qa_testing_bot.bot_id = bot_id
            qa_testing_bot.bot_name = bot_name
            qa_testing_bot.bot_domain = bot_domain
            qa_testing_bot.save()
            return redirect("/automation/home/")
        else:
            return HttpResponse(status=400)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EditAutomationBot: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        return HttpResponse(status=404)


@login_required
def TestingBotConsole(request, pk):
    try:
        bot_tester = Tester.objects.get(user__username=request.user.username)
        qa_testing_bot = BotQATesting.objects.get(pk=pk, created_by=bot_tester)
        qa_testcases = BotQATestCase.objects.filter(bot=qa_testing_bot)
        return render(request, "TestingApp/testing_console.html", {
            "qa_testcases": qa_testcases,
            "qa_testing_bot": qa_testing_bot
        })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("TestingBotConsole: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        return HttpResponse(status=404)


@login_required
def DeleteAutomationBot(request, pk):
    try:
        bot_tester = Tester.objects.get(user__username=request.user.username)
        qa_testing_bot = BotQATesting.objects.get(pk=pk, created_by=bot_tester)
        qa_testing_bot.delete()
        return redirect("/automation/home/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("DeleteAutomationBot: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        return HttpResponse(status=404)


class UploadQATestcaseExcelAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            filename = strip_html_tags(data["filename"])
            filename = remo_html_from_string(filename)

            test_bot_id = strip_html_tags(data["test_bot_id"])
            test_bot_id = remo_html_from_string(test_bot_id)

            base64_data = strip_html_tags(data["base64_file"])

            qa_testing_bot = BotQATesting.objects.get(pk=int(test_bot_id))

            filename = generate_random_key(
                10) + "_" + filename.replace(" ", "")

            if not os.path.exists("files/test-" + str(test_bot_id)):
                os.makedirs("files/test-" + str(test_bot_id))

            file_path = "files/test-" + str(test_bot_id) + "/" + filename

            file_extension = file_path.split(".")[-1]
            file_extension = file_extension.lower()

            if file_extension != "csv":
                response["status"] = 300
            else:
                fh = open(file_path, "wb")
                fh.write(base64.b64decode(base64_data))
                fh.close()

                if not os.path.exists('secured_files/TestingApp/automated_testing/test-' + str(test_bot_id)):
                    os.makedirs('secured_files/TestingApp/automated_testing/test-' + str(test_bot_id))

                secured_file_path = "secured_files/TestingApp/automated_testing/test-" + str(test_bot_id) + "/" + filename

                fh = open(secured_file_path, "wb")
                fh.write(base64.b64decode(base64_data))
                fh.close()

                secured_file_path = "/" + secured_file_path
                file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
                    file_path=secured_file_path, is_public=False, is_customer_attachment=False)

                secured_file_url = 'chat/download-file/' + \
                    str(file_access_management_obj.key) + '/' + filename

                testcase = BotQATestCase.objects.create(bot=qa_testing_bot,
                                                        uploaded_excel=file_path,
                                                        secured_file_path=secured_file_url)
                testcase.is_uploaded = True
                testcase.save()

                response["status"] = 200
                response["message"] = "success"
                response["testcase_id"] = testcase.pk
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UploadQATestcaseExcelAPI: error %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


UploadQATestcaseExcel = UploadQATestcaseExcelAPI.as_view()


class ValidateQATestcaseExcelAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            testcase_id = strip_html_tags(str(data["testcase_id"]))
            testcase_id = remo_html_from_string(testcase_id)

            bot_testcase = BotQATestCase.objects.get(pk=int(testcase_id))

            status = validate_testcase_excel_sheet(
                bot_testcase, BotQATestCase, BotQATestCaseFlow)

            if status == None:
                response["status"] = 300
                response["message"] = "Failed"
            else:
                bot_testcase.testing_start_datetime = timezone.now()
                bot_testcase.save()
                response["status"] = 200
                response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ValidateQATestcaseExcelAPI: error %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


ValidateQATestcaseExcel = ValidateQATestcaseExcelAPI.as_view()


@login_required
def TestCasePreview(request, pk):
    try:
        qa_testcase = BotQATestCase.objects.get(pk=pk)
        parsed_json = qa_testcase.parsed_json
        parsed_json = json.dumps(json.loads(parsed_json), indent=4)
        return HttpResponse(parsed_json, content_type="application/json")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("TestCasePreview: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        return HttpResponse(status=400)


@login_required
def DeleteTestCase(request, pk):
    try:
        qa_testcase = BotQATestCase.objects.get(pk=pk)
        bot_pk = qa_testcase.bot.pk
        qa_testcase.delete()
        return redirect("/automation/test/" + str(bot_pk) + "/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("DeleteTestCase: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        return HttpResponse(status=400)


@login_required
def TestCaseResults(request, pk):
    qa_testcase = BotQATestCase.objects.get(pk=pk)
    qa_testcase_flows = BotQATestCaseFlow.objects.filter(
        qa_testcase=qa_testcase).order_by('pk')
    return render(request, "TestingApp/testcase_result.html", {
        "qa_testcase": qa_testcase,
        "qa_testcase_flows": qa_testcase_flows
    })


@login_required
def ResetTestCase(request, pk):
    qa_testcase_flow = BotQATestCaseFlow.objects.get(pk=pk)
    qa_testcase_flow.is_flow_testing_failed = False
    qa_testcase_flow.is_flow_tested = False
    qa_testcase_flow.output_flow = None
    qa_testcase_flow.save()
    return redirect("/automation/testcase/results/" + str(qa_testcase_flow.qa_testcase.pk) + "/")


@login_required
def ResetAllTestCase(request, pk):
    qa_testcase = BotQATestCase.objects.get(pk=pk)
    qa_testcase_flows = BotQATestCaseFlow.objects.filter(
        qa_testcase=qa_testcase)
    for qa_testcase_flow in qa_testcase_flows:
        qa_testcase_flow.is_flow_testing_failed = False
        qa_testcase_flow.is_flow_tested = False
        qa_testcase_flow.output_flow = None
        qa_testcase_flow.save()

    return redirect("/automation/testcase/results/" + str(qa_testcase.pk) + "/")


class GetTestCaseFlowOutputAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            qa_testcase_flow_id = data["qa_testcase_flow_id"]
            qa_testcase_flow_id = strip_html_tags(str(qa_testcase_flow_id))
            qa_testcase_flow_id = remo_html_from_string(qa_testcase_flow_id)

            qa_testcase_flow = BotQATestCaseFlow.objects.get(
                pk=int(qa_testcase_flow_id))
            flow_output = json.loads(qa_testcase_flow.minimized_output_flow)

            response["status"] = 200
            response["message"] = "success"
            response["flow_output"] = flow_output
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetTestCaseFlowOutputAPI: error %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetTestCaseFlowOutput = GetTestCaseFlowOutputAPI.as_view()


class TestAutomationQueryAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            bot_id = data["bot_id"]
            bot_id = strip_html_tags(str(bot_id))
            bot_id = remo_html_from_string(bot_id)

            qa_testing_bot = BotQATesting.objects.get(pk=int(bot_id))
            query_response = test_automation_query_api(qa_testing_bot, "hi")

            response["status"] = 200
            response["message"] = "success"
            response["query_response"] = query_response
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error TestAutomationQueryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno))

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


TestAutomationQuery = TestAutomationQueryAPI.as_view()
