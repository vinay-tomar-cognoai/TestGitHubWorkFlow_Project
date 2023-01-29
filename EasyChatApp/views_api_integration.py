from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect
from EasyChatApp.models import *
from EasyChatApp.utils import *
from django.http import HttpResponseNotFound
from EasyChatApp.utils import logger
import xmltodict
import json
import logging
from dict2xml import dict2xml
from copy import copy
from EasyChatApp.utils_api_integration import *


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return

# Used for generating code for access token


def AccessTokenForAPI(request):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Intent Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            else:
                intent_pk = request.GET["intent_pk"]
                intent_obj = Intent.objects.get(pk=intent_pk)
                parent_tree_pk = intent_obj.tree.pk
                tree_pk = request.GET["tree_pk"]

                type_of_request = request.GET["type"]

                url_access_token = ""
                header_access_token = ""
                url = ""
                response_packet = "{ }"
                error_response_packet = "{ }"
                basic_authorization_username = ""
                basic_authorization_password = ""
                bot_response_variable = ""
                bot_response_value = ""
                bot_error_response_value = ""

                tree_obj = Tree.objects.get(pk=tree_pk)
                api_integration_obj = ApiIntegrationDetail.objects.filter(
                    tree=tree_obj)

                if api_integration_obj.count() == 1:
                    url_access_token = api_integration_obj[0].url_access_token
                    header_access_token = api_integration_obj[
                        0].header_access_token
                    url = api_integration_obj[0].url
                    header = api_integration_obj[0].header
                    request_packet = api_integration_obj[0].request_packet
                    response_packet = api_integration_obj[0].response_packet
                    error_response_packet = api_integration_obj[
                        0].error_response_packet
                    basic_authorization_username = api_integration_obj[
                        0].basic_authorization_username
                    basic_authorization_password = api_integration_obj[
                        0].basic_authorization_password
                    bot_response_variable = api_integration_obj[
                        0].bot_response_variable
                    bot_response_value = api_integration_obj[
                        0].bot_response_value
                    bot_error_response_value = api_integration_obj[
                        0].bot_error_response_value

                else:
                    if type_of_request == "rest":
                        header = '{"Content-Type":"application/json"}'
                        request_packet = "{ }"
                    elif type_of_request == "soap":
                        header = '{"Content-Type":"application/xml"}'
                        request_packet = '<XML></XML>'

                return render(request, "EasyChatApp/api_integration.html", {
                    "intent_pk": intent_pk,
                    "tree_pk": tree_pk,
                    "parent_tree_pk": parent_tree_pk,
                    "type_of_request": type_of_request,
                    "url_access_token": url_access_token,
                    "header_access_token": header_access_token,
                    "url": url,
                    "header": header,
                    "request_packet": request_packet,
                    "response_packet": response_packet,
                    "error_response_packet": error_response_packet,
                    "basic_authorization_username": basic_authorization_username,
                    "basic_authorization_password": basic_authorization_password,
                    "bot_response_variable": bot_response_variable,
                    "bot_response_value": bot_response_value,
                    "bot_error_response_value": bot_error_response_value
                })
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ApiIntegration ! %s %s",
                     str(e), str(exc_tb.tb_lineno))
        return HttpResponseNotFound("INVALID_REQUEST")

# generates trees based on request
# response and error packets


def RequestResponseTree(request):
    response = {}
    response['status_code'] = 500
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            data = request.POST['data']
            data = DecryptVariable(data)

            data = json.loads(data)

            parent_tree_pk = data['parent_tree_pk']

            type_of_request = data['type_of_request']

            if type_of_request == "rest":
                request_packet = data['request_packet']

                request_packet = request_packet.replace("'", '"')
                request_packet = json.loads(request_packet)

                response_packet = data['response_packet']

                response_packet = response_packet.replace("'", '"')
                response_packet = json.loads(response_packet)

                error_response_packet = data['error_response_packet']

                if error_response_packet != "":
                    error_response_packet = error_response_packet.replace(
                        "'", '"')
                    error_response_packet = json.loads(error_response_packet)

            else:
                request_packet = data['request_packet']

                request_packet = json.loads(
                    json.dumps(xmltodict.parse(request_packet)))

                response_packet = data['response_packet']

                response_packet = json.loads(
                    json.dumps(xmltodict.parse(response_packet)))

                error_response_packet = data['error_response_packet']
                if error_response_packet != "":
                    error_response_packet = json.loads(
                        json.dumps(xmltodict(error_response_packet)))

            post_processor_variable_dropdown = ""
            parent_tree = Tree.objects.get(pk=parent_tree_pk)
            if parent_tree.post_processor != None:
                if parent_tree.post_processor.post_processor_direct_value != None:
                    post_processor_variable_dropdown = '<option value="' + parent_tree.post_processor.post_processor_direct_value + \
                        '">{/' + parent_tree.post_processor.post_processor_direct_value + '/}</option>'
                while len(parent_tree.children.all()) != 0:
                    try:
                        if parent_tree.children.all()[0].post_processor != None:
                            if parent_tree.children.all()[0].post_processor.post_processor_direct_value != None:
                                post_processor_variable_dropdown = post_processor_variable_dropdown + '<option value="' + parent_tree.children.all()[0].post_processor.post_processor_direct_value + '">{/' + parent_tree.children.all()[
                                    0].post_processor.post_processor_direct_value + '/}</option>'

                        parent_tree = parent_tree.children.all()[0]

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("RequestResponseTree ! %s %s",
                                     str(e), str(exc_tb.tb_lineno))
                        break

            request_tree_html = json_parser(
                request_packet, '<ul id="ul-request-packet">', post_processor_variable_dropdown)

            response_tree_html = response_parser(
                response_packet, '<ul id="ul-response-packet">')

            response['status_code'] = 200
            response['request_tree_html'] = request_tree_html
            response['response_tree_html'] = response_tree_html
            response['request_packet'] = json.dumps(request_packet)
            response['response_packet'] = json.dumps(response_packet)

            if error_response_packet != "":
                html_error_response = error_response_parser(
                    error_response_packet, '<ul id="ul-error-response-packet">')
                html_error_response = html_error_response + "<br>"

                response['error_response_packet'] = json.dumps(
                    error_response_packet)
            else:
                html_error_response = "<br>"
                response['error_response_packet'] = ""

            response['html_error_response'] = html_error_response
            return HttpResponse(json.dumps(response), content_type="application/json")

        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("RequestResponseTree ! %s %s",
                     str(e), str(exc_tb.tb_lineno))
        return HttpResponse(json.dumps(response), content_type="application/json")

# generates final api tree code


def GenerateApiCode(request):
    response = {}
    response['status_code'] = 500
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            data = request.POST['data']
            data = DecryptVariable(data)
            data = json.loads(data)
            tree_pk = data['tree_pk']
            url = data['url']
            url = url.strip()
            url = url.replace("'", "")
            url = url.replace('"', "")
            header = data['header']
            header = header.replace("'", '"')

            type_of_request = data['type_of_request']

            request_packet = data['request_packet']
            request_packet = request_packet.replace("'", '"')

            response_packet = data['response_packet']
            response_packet = response_packet.replace("'", '"')

            error_response_packet = data['error_response_packet']
            error_response_packet = error_response_packet.replace("'", '"')

            username_basic_authorization = data['username_basic_authorization']
            password_basic_authorization = data['password_basic_authorization']

            bot_response_variable = data['bot_response_variable']
            bot_response_value = data['bot_response_value']
            bot_error_response_value = data['bot_error_response_value']

            bot_response_value_list = bot_response_value.split(" ")
            bot_response_value = ""
            for iterator in range(0, len(bot_response_value_list)):
                if "{/" and "/}" in bot_response_value_list[iterator]:
                    bot_response_value_list[iterator] = bot_response_value_list[
                        iterator].replace("{/", "").replace("/}", "")
                    bot_response_value_list[
                        iterator] = "\"+response['data']['" + bot_response_value_list[iterator] + "']+\""
                    bot_response_value = bot_response_value + \
                        bot_response_value_list[iterator] + " "
                else:
                    bot_response_value = bot_response_value + \
                        bot_response_value_list[iterator] + " "

            bot_error_response_value_list = bot_error_response_value.split(" ")
            bot_error_response_value = ""
            for iterator in range(0, len(bot_error_response_value_list)):
                if "{/" and "/}" in bot_error_response_value_list[iterator]:
                    bot_error_response_value_list[iterator] = bot_error_response_value_list[
                        iterator].replace("{/", "").replace("/}", "")
                    bot_error_response_value_list[
                        iterator] = "\"+response['data']['" + bot_error_response_value_list[iterator] + "']+\""
                    bot_error_response_value = bot_error_response_value + \
                        bot_error_response_value_list[iterator] + " "
                else:
                    bot_error_response_value = bot_error_response_value + \
                        bot_error_response_value_list[iterator] + " "

            if type_of_request == "rest":
                request_packet = json.loads(request_packet)
                response_packet = json.loads(response_packet)
                if error_response_packet != "":
                    error_response_packet = json.loads(error_response_packet)
            else:
                request_packet = json.loads(
                    json.dumps(xmltodict.parse(request_packet)))
                response_packet = json.loads(
                    json.dumps(xmltodict.parse(response_packet)))
                if error_response_packet != "":
                    error_response_packet = json.loads(
                        json.dumps(xmltodict.parse(error_response_packet)))

            request_data = data['request_dict']

            if isinstance(request_packet, list):
                for item in request_packet:
                    json_key(item, request_data)
            else:
                json_key(request_packet, request_data)

            if type_of_request == "soap":
                xml_requestpacket = dict2xml(request_packet)

            request_packet1 = json.dumps(request_packet)

            response_data = data['response_dict']

            parse_response_keys_blank_dict = {}
            json_key_response(response_packet, response_data,
                              parse_response_keys_blank_dict)

            if error_response_packet != "":
                parse_error_response_keys_blank_dict = {}
                error_response_data = data['error_response_dict']
                json_key_response(
                    error_response_packet, error_response_data, parse_error_response_keys_blank_dict)

            access_token_code = "from EasyChatApp.utils import logger\nimport json\nimport requests\nimport xmltodict \nimport sys\n"
            url_access_token = data['url_access_token'].strip()
            header_access_token = data['header_access_token']
            if (url_access_token != "" and header_access_token != ""):
                access_token_code = access_token_code + 'def access_token():\n    url="' + url_access_token + '"\n    header=' + header_access_token + \
                    '\n    resp=requests.get(url=url,headers=header)\n' + \
                    '    response=json.loads(resp.text)\n' + \
                    '    return response["access_token"]\n'

            if type_of_request == "rest":

                code = access_token_code + 'def f():\n    response = {}\n    response["status_code"] = 500\n    response["status_message"] = "Internal server error."\n    response["data"] = {}\n    response["cards"] = []\n    response["choices"] = []\n    response["images"] = []\n    response["videos"] = []\n    response["recommendations"] = []\n    response["API_REQUEST_PACKET"] = {}\n    response["API_RESPONSE_PACKET"] = {}\n    try:\n' + \
                    '        url = "' + url + '"\n        header = '

                header = json.loads(header)
                code = code + '{'
                for key, value in header.items():
                    if key.lower() == "authorization" or key.lower() == "accesstoken" or key.lower() == "access_token":
                        code = code + '"' + "Authorization" + '": "Bearer " + access_token() ,'
                    else:
                        code = code + '"' + key + '":"' + value + '",'

                code = code[:-1]
                code = code + '}'

                if username_basic_authorization != "" and password_basic_authorization != "":
                    code = code + '\n        payload = ' + request_packet1 + '\n' + \
                        '        resp=requests.post(url=url,data=json.dumps(payload),headers=header,auth=("' + username_basic_authorization + '","' + password_basic_authorization + \
                        '"))\n        api_response=json.loads(resp.text)\n        response["API_REQUEST_PACKET"] = {"url":url,"headers":header,"data":payload}\n        response["API_RESPONSE_PACKET"] = {"response":api_response} \n'
                else:
                    code = code + '\n        payload = ' + request_packet1 + '\n' + \
                        '        resp=requests.post(url=url,data=json.dumps(payload),headers=header)\n        api_response=json.loads(resp.text)\n        response["API_REQUEST_PACKET"] = {"url":url,"headers":header,"data":payload}\n        response["API_RESPONSE_PACKET"] = {"response":api_response} \n'

            elif type_of_request == "soap":
                code = access_token_code + "def f():\n    response = {}\n    response['status_code'] = 500\n    response['status_message'] = 'Internal server error.'\n    response['data'] = {}\n    response['cards'] = []\n    response['choices'] = []\n    response['images'] = []\n    response['videos'] = []\n    response['recommendations'] = []\n    response['API_REQUEST_PACKET'] = {}\n    response['API_RESPONSE_PACKET'] = {}\n    try:\n" + \
                    "        url = '" + url + "'\n        header = "

                header = json.loads(header)
                code = code + '{'
                for key, value in header.items():
                    if key.lower() == "authorization" or key.lower() == "accesstoken" or key.lower() == "access_token":
                        code = code + '"' + "Authorization" + '": "Bearer " + access_token() ,'
                    else:
                        code = code + '"' + key + '":"' + value + '",'

                code = code[:-1]
                code = code + '}'

                if username_basic_authorization != "" and password_basic_authorization != "":
                    code = code + "\n        payload = " + "'''" + xml_requestpacket + "'''" + "\n" + \
                        "        resp=requests.post(url=url,data=payload,headers=header,auth=('" + username_basic_authorization + "','" + password_basic_authorization + \
                        "'))\n        api_response = xmltodict.parse(resp)\n        \n        api_response = json.loads(json.dumps(api_response))\n        response['API_REQUEST_PACKET'] = {'url':url,'headers':header,'data':payload}\n        response['API_RESPONSE_PACKET'] = {'response':api_response} \n"

                else:
                    code = code + "\n        payload = " + "'''" + xml_requestpacket + "'''" + "\n" + \
                        "        resp=requests.post(url=url,data=payload,headers=header)\n        api_response = xmltodict.parse(resp)\n        \n        api_response = json.loads(json.dumps(api_response))\n        response['API_REQUEST_PACKET'] = {'url':url,'headers':header,'data':payload}\n        response['API_RESPONSE_PACKET'] = {'response':api_response} \n"

            if error_response_packet != "":
                code = code + '\n        try:'
                for key, value in parse_response_keys_blank_dict.items():
                    code = code + \
                        '\n            response["data"]["' + \
                        str(key) + '"]=' + 'api_response' + str(value)
                code = code + '\n            response["data"]["' + str(
                    bot_response_variable) + '"]="' + str(bot_response_value) + '"'

                code = code + '\n        except:'
                for key, value in parse_error_response_keys_blank_dict.items():
                    code = code + \
                        '\n            response["data"]["' + \
                        str(key) + '"]=' + 'api_response' + str(value)
                code = code + '\n            response["data"]["' + str(
                    bot_response_variable) + '"]="' + str(bot_error_response_value) + '"'
            else:
                for key, value in parse_response_keys_blank_dict.items():
                    code = code + \
                        '\n        response["data"]["' + \
                        str(key) + '"]=' + 'api_response' + str(value)
                code = code + '\n        response["data"]["' + str(
                    bot_response_variable) + '"]="' + str(bot_response_value) + '"'

            code = code + '\n        response["status_code"] = "200"\n        response["print"] = "Hello world!"\n        return response\n    except Exception as E:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error("ApiTreeContent: %s at %s",str(E), str(exc_tb.tb_lineno), extra={"AppName": "EasyChat", "user_id": "None", "source": "None", "channel": "None", "bot_id": "None"})\n        response["status_code"] = 500\n        response["status_message"] = "ERROR :-  "+str(E)+ " at line no: " +str(exc_tb.tb_lineno)\n        return response  # noqa: F841'
            tree_obj = Tree.objects.get(pk=tree_pk)
            tree_name = tree_obj.name
            processor_obj = ApiTree.objects.create(
                name="APITree_" + str(tree_name), api_caller=code)
            tree_obj.api_tree = processor_obj
            tree_obj.save()

            if data['bot_response_variable'] != "":
                sentence_json = {
                    "items": []
                }
                sentence_json["items"].append({
                    "text_response": "{/" + data['bot_response_variable'] + "/}",
                    "speech_response": "",
                    "hinglish_response": "",
                    "text_reprompt_response": "",
                    "speech_reprompt_response": "",
                    "tooltip_response": "",
                })
                bot_response_obj = BotResponse.objects.create(
                    sentence=json.dumps(sentence_json))
                tree_obj.response = bot_response_obj
                tree_obj.save()

            # checks if APIIntegrationDetail objects exists for that tree
            # if Yes, it's updated, otherwise new is created.
            api_integration_obj = ApiIntegrationDetail.objects.filter(
                tree=tree_obj)
            if (api_integration_obj):
                api_integration_obj.update(
                    tree=tree_obj,
                    url_access_token=url_access_token,
                    header_access_token=header_access_token,
                    url=url,
                    header=header,
                    request_packet=request_packet,
                    response_packet=response_packet,
                    error_response_packet=error_response_packet,
                    basic_authorization_username=data[
                        'username_basic_authorization'],
                    basic_authorization_password=data[
                        'password_basic_authorization'],
                    bot_response_variable=data['bot_response_variable'],
                    bot_response_value=data['bot_response_value'],
                    bot_error_response_value=data['bot_error_response_value']
                )
            else:
                api_integration_obj = ApiIntegrationDetail.objects.create(
                    tree=tree_obj,
                    url_access_token=url_access_token,
                    header_access_token=header_access_token,
                    url=url,
                    header=header,
                    request_packet=request_packet,
                    response_packet=response_packet,
                    error_response_packet=error_response_packet,
                    basic_authorization_username=data[
                        'username_basic_authorization'],
                    basic_authorization_password=data[
                        'password_basic_authorization'],
                    bot_response_variable=data['bot_response_variable'],
                    bot_response_value=data['bot_response_value'],
                    bot_error_response_value=data['bot_error_response_value']
                )
                api_integration_obj.save()

            response['status_code'] = 200
            return HttpResponse(json.dumps(response), content_type="application/json")
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("RequestResponseTree ! %s %s",
                     str(e), str(exc_tb.tb_lineno))
        return HttpResponse(json.dumps(response), content_type="application/json")
