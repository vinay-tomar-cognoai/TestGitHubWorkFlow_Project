from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes

from django.shortcuts import render, HttpResponse, redirect

# Create your views here.

from AutomatedAPIApp.utils import *
from AutomatedAPIApp.models import *

import logging

logger = logging.getLogger(__name__)


def AutomatedAPIIntegrationConsoleOld(request):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            tree_id = request.GET["tree_id"]
            tree_obj = Tree.objects.get(pk=int(tree_id))

            automated_api_integration_obj = get_tree_associated_automated_api_integration_obj(
                tree_obj, Tree, AutomatedAPIIntegration)

            return render(request, "AutomatedAPIApp/console_old.html", {
                "tree_obj": tree_obj,
                "automated_api_integration_obj": automated_api_integration_obj
            })
        else:
            return HttpResponse("You are not allowed to access this page.")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AutomatedAPIIntegrationConsoleOld: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

    return HttpResponse(status=404)


def AutomatedAPIIntegrationConsole(request):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):

            get_params = dict(request.GET)

            tree_id = request.GET["tree_id"]
            tree_obj = Tree.objects.get(pk=int(tree_id))

            is_api_tree_already_present = False

            if tree_obj.api_tree:
                is_api_tree_already_present = True

            try:
                api_pk = int(request.GET["api_pk"])
            except Exception:
                api_pk = None
            old_api_pk = api_pk

            automated_api_integration_obj = get_tree_associated_automated_api_integration_obj(
                tree_obj, Tree, AutomatedAPIIntegration)

            function_name_list = get_function_name_list(
                automated_api_integration_obj.initial_api)

            if api_pk == None:
                if function_name_list:
                    api_pk = function_name_list[0]["pk"]
                else:
                    api_pk = -1
            elif api_pk != -1:
                selected_api_pk = None
                for function_name in function_name_list:
                    if function_name["pk"] == api_pk:
                        selected_api_pk = api_pk
                        break

                if selected_api_pk == None:
                    if function_name_list:
                        api_pk = function_name_list[0]["pk"]
                    else:
                        api_pk = -1

            if old_api_pk != api_pk:
                get_params["api_pk"] = [api_pk]
                url_with_paras = "/automated-api/build/?"

                for key, value in get_params.items():
                    url_with_paras += str(key) + "=" + str(value[0]) + "&"

                return redirect(url_with_paras)

            return render(request, "AutomatedAPIApp/workspace.html", {
                "tree_obj": tree_obj,
                "automated_api_integration_obj": automated_api_integration_obj,
                "function_name_list": function_name_list,
                "api_pk": api_pk,
                "is_api_tree_already_present": is_api_tree_already_present,
            })
        else:
            return HttpResponse("You are not allowed to access this page.")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AutomatedAPIIntegrationConsole: error %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

    return HttpResponse(status=404)


class AutomatedAPITestAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            request_url = data["url"]
            request_type = data["type"]
            request_body = data["body"]
            request_body = request_body.strip()
            headers = json.loads(data["headers"])
            authorization = json.loads(data["authorization"])

            request_body, headers = update_request_body_based_on_content_type(headers, request_body, True)

            logger.info(request_url, extra={"AppName": APP_NAME})
            logger.info(request_type, extra={"AppName": APP_NAME})
            logger.info(request_body, extra={"AppName": APP_NAME})
            logger.info(headers, extra={"AppName": APP_NAME})
            logger.info(authorization, extra={"AppName": APP_NAME})

            if request_url.strip() != "" and request_type.strip() != "":

                api_response = None

                if authorization["type"] == "bearer-token":

                    headers["Authorization"] = "Bearer " + \
                        authorization["params"]["token"]

                    api_response = requests.request(request_type,
                                                    url=request_url,
                                                    data=request_body,
                                                    headers=headers)

                elif authorization["type"] == "basic-auth":

                    username = authorization["params"]["username"]
                    password = authorization["params"]["password"]

                    api_response = requests.request(request_type,
                                                    url=request_url,
                                                    data=request_body,
                                                    headers=headers,
                                                    auth=HTTPBasicAuth(username, password))

                elif authorization["type"] == "digest-auth":

                    username = authorization["params"]["username"]
                    password = authorization["params"]["password"]

                    api_response = requests.request(request_type,
                                                    url=request_url,
                                                    data=request_body,
                                                    headers=headers,
                                                    auth=HTTPDigestAuth(username, password))

                elif authorization["type"] == "oauth-1.0-auth":

                    consumer_key = authorization["params"]["consumer-key"]
                    consumer_secret = authorization[
                        "params"]["consumer-secret"]
                    access_token = authorization["params"]["access-token"]
                    token_secret = authorization["params"]["token-secret"]

                    api_response = requests.request(request_type,
                                                    url=request_url,
                                                    data=request_body,
                                                    headers=headers,
                                                    auth=OAuth1(consumer_key, consumer_secret, access_token, token_secret))

                else:
                    api_response = requests.request(request_type,
                                                    url=request_url,
                                                    data=request_body,
                                                    headers=headers)

                response["status"] = 200
                response["api_response"] = {
                    "status": api_response.status_code,
                    "headers": dict(api_response.headers),
                    "body": api_response.text
                }
            else:
                response["status"] = 101
                response[
                    "message"] = "Request URL or Request type can not be empty"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AutomatedAPITestAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


AutomatedAPITest = AutomatedAPITestAPI.as_view()


class GetParentTreePostProcessorVariableNamesAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            current_tree_obj = Tree.objects.get(pk=int(data["tree_id"]))

            api_pk = int(data["api_pk"])

            tree_objects = []

            reverse_tree_objects(current_tree_obj, tree_objects, Tree)

            post_processor_variable_names = []
            for tree_obj in tree_objects:
                post_processor = tree_obj.post_processor
                if post_processor == None:
                    continue

                post_processor_direct_value = post_processor.post_processor_direct_value

                if post_processor_direct_value != None:
                    post_processor_variable_names.append(
                        post_processor_direct_value)

            automated_api_integration_obj = get_tree_associated_automated_api_integration_obj(
                current_tree_obj, Tree, AutomatedAPIIntegration)

            automated_api_obj = get_automated_api_obj(
                automated_api_integration_obj, api_pk)

            if automated_api_obj != None:

                response["integrated_api"] = {
                    "api_pk": automated_api_obj.pk,
                    "type": automated_api_obj.request_type,
                    "url": automated_api_obj.request_url,
                    "body": automated_api_obj.request_packet,
                    "headers": automated_api_obj.headers,
                    "authorization": automated_api_obj.authorization,
                    "variables": automated_api_obj.variables,
                }
            else:
                response["integrated_api"] = None

            all_api_variable_list = []
            index = 1
            for api_obj in get_automated_api_objs(automated_api_integration_obj.initial_api):
                all_api_variable_list.append(api_obj.variables)
                index += 1

            response["status"] = 200
            response["parent_variable_names"] = post_processor_variable_names
            response["all_api_variable_list"] = all_api_variable_list
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetParentTreePostProcessorVariableNamesAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GetParentTreePostProcessorVariableNames = GetParentTreePostProcessorVariableNamesAPI.as_view()


class TestGetAccountBalanceAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        # custom_encrypt_obj = CustomEncrypt()
        try:
            response["status"] = 200
            response["account_balance"] = 20000
            response["lien_balance"] = 15000
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error TestGetAccountBalanceAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        return Response(data=response)


TestGetAccountBalance = TestGetAccountBalanceAPI.as_view()


class TagAPIWithTreeAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)

            request_url = data["url"]
            request_type = data["type"]
            request_body = data["body"]
            tree_id = data["tree_id"]
            headers = data["headers"]
            authorization = data["authorization"]
            variables = data["variables"]
            api_pk = int(data["api_pk"])

            request_body, headers = update_request_body_based_on_content_type(headers, request_body, False)

            logger.info(request_url, extra={"AppName": APP_NAME})
            logger.info(request_type, extra={"AppName": APP_NAME})
            logger.info(request_body, extra={"AppName": APP_NAME})
            logger.info(headers, extra={"AppName": APP_NAME})
            logger.info(tree_id, extra={"AppName": APP_NAME})
            logger.info(authorization, extra={"AppName": APP_NAME})
            logger.info(variables, extra={"AppName": APP_NAME})

            tree_obj = Tree.objects.get(pk=int(tree_id))

            automated_api_integration_obj = get_tree_associated_automated_api_integration_obj(
                tree_obj, Tree, AutomatedAPIIntegration)

            try:
                automated_api_obj = AutomatedAPI.objects.get(pk=api_pk)
            except Exception:
                automated_api_obj = None

            if automated_api_obj == None:
                automated_api_obj = AutomatedAPI.objects.create(request_packet=request_body,
                                                                request_type=request_type,
                                                                request_url=request_url,
                                                                headers=headers,
                                                                authorization=authorization,
                                                                variables=variables,)
                if automated_api_integration_obj.initial_api == None:
                    automated_api_integration_obj.initial_api = automated_api_obj
                else:
                    api_objs = get_automated_api_objs(
                        automated_api_integration_obj.initial_api)
                    last_api_obj = api_objs[-1]
                    last_api_obj.next_api = automated_api_obj
                    last_api_obj.save()

                automated_api_integration_obj.save()
            else:
                automated_api_obj.request_packet = request_body
                automated_api_obj.request_type = request_type
                automated_api_obj.request_url = request_url
                automated_api_obj.headers = headers
                automated_api_obj.authorization = authorization
                automated_api_obj.variables = variables
                automated_api_obj.save()

            response["status"] = 200
            response["api_pk"] = automated_api_obj.pk
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error TagAPIWithTreeAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


TagAPIWithTree = TagAPIWithTreeAPI.as_view()


class GenerateAutomatedAPICodeAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            tree_id = data["tree_id"]
            tree_obj = Tree.objects.get(pk=int(tree_id))

            automated_api_integration_obj = get_tree_associated_automated_api_integration_obj(
                tree_obj, Tree, AutomatedAPIIntegration)

            generated_code = generate_automated_api_code(
                automated_api_integration_obj)

            response["status"] = 200
            response["generated_code"] = generated_code
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GenerateAutomatedAPICodeAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


GenerateAutomatedAPICode = GenerateAutomatedAPICodeAPI.as_view()


class SaveCodeIntoApiTreeAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data["Request"]
            data = custom_encrypt_obj.decrypt(data)
            data = json.loads(data)
            tree_id = data["tree_id"]
            tree_obj = Tree.objects.get(pk=int(tree_id))
            api_code = data["api_code"]

            automated_api_integration_obj = get_tree_associated_automated_api_integration_obj(
                tree_obj, Tree, AutomatedAPIIntegration)

            api_tree_obj = automated_api_integration_obj.api_tree
            if api_tree_obj == None:
                tree_name = tree_obj.name
                api_tree_obj = ApiTree.objects.create(name="AutomatedAPI_" + tree_name,
                                                      api_caller=api_code,
                                                      apis_used=True)
            else:
                api_tree_obj.api_caller = api_code
                api_tree_obj.apis_used = True
                api_tree_obj.save()

            automated_api_integration_obj.api_tree = api_tree_obj
            automated_api_integration_obj.save()

            tree_obj.api_tree = api_tree_obj
            tree_obj.save()
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveCodeIntoApiTreeAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': APP_NAME})

        response = json.dumps(response)
        encrypted_response = custom_encrypt_obj.encrypt(response)
        response = {"Response": encrypted_response}
        return Response(data=response)


SaveCodeIntoApiTree = SaveCodeIntoApiTreeAPI.as_view()
