from rest_framework.response import Response
from django.shortcuts import HttpResponse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.views import APIView
from rest_framework_xml.renderers import XMLRenderer
from rest_framework_xml.parsers import XMLParser
from django.views import View

import sys
import json
import base64
import random
import string
from Crypto.Cipher import AES
from Crypto import Random
import xmltodict

import logging
logger = logging.getLogger(__name__)


BLOCK_SIZE = 16

client_id = '0JVJJjKQzaqK4A79SUwVXPl8pBqUaf'
client_secret = 'dy3pHlo3ldJ1ycO8XqOPLHgZFbUTxs'
grant_type = 'client_credentials'
access_token = 'GObtAZ7KFKUHoMv5Sp7mQxTb8MhSzB9iEKJEigqhuIgtT'

username = "AllinCall"
password = "AllinCall@123$"
dummy_data = "Welcome, AllinCall"
dob = "1995-06-09"
pan = "LOLOP1254L"


balance_api_data_dictionary = {"balance": [
    {
        "mobnumber": "7905358546",
        "name": "Aman Goel",
        "account_id": "106673251",
        "balance": "5,00,00,000"
    },
    {
        "mobnumber": "8087073287",
        "name": "Himanshu Kherde",
        "account_id": "105893635",
        "balance": "3,00,00,000"
    },
    {
        "mobnumber": "9723625972",
        "name": "Shivam Gupta",
        "account_id": "103453232",
        "balance": "4,20,00,00,00,000"
    },
]}


valuation_dictionary = {"valuation_dictionary": [
    {
        "valuation_id": "10058816",
        "scheme": "ICICI Prudential Multicap Fund - Direct Plan - Growth",
        "scheme_balance": "Rs 3,00,000",
        "NAV": "Rs 40,000",
        "NAV_Date": "07-08-2020"
    },
    {
        "valuation_id": "19779920",
        "scheme": "ICICI Prudential Equity & Debt Fund",
        "scheme_balance": "Rs 6,00,000",
        "NAV": "Rs 30,000",
        "NAV_Date": "08-07-2020"
    },
    {
        "valuation_id": "13456678",
        "scheme": "ICICI Prudential Medium Term Bond Fund",
        "scheme_balance": "Rs 7,00,000",
        "NAV": "Rs 35,000",
        "NAV_Date": "06-06-2020"
    },
    {
        "valuation_id": "13455897",
        "scheme": " ICICI Prudential Savings Plan",
        "scheme_balance": "Rs 9,00,000",
        "NAV": "Rs 50,000",
        "NAV_Date": "07-05-2020"
    },
]}


soap_fault_packet = """
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <soap:Body>
        <soap:Fault>
            <faultcode>soap:Server</faultcode>
            <faultstring>An error occurred while performing the export operation: </faultstring>
            <detail>
                <WebServiceFault xmlns="http://www.taleo.com/ws/integration/toolkit/2005/07">
                    <code>SystemError</code>
                    <message>An Exception Occurred</message>
                </WebServiceFault>
            </detail>
        </soap:Fault>
    </soap:Body>
</soap:Envelope>
"""

soap_data_packet = """
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <soap:Body>
        <ns1:findPartialEntitiesResponse xmlns:ns1="http://www.taleo.com/ws/tee800/2009/01/find">
            <root:Entities xmlns:root="http://www.taleo.com/ws/tee800/2009/01/find" xmlns:e="http://www.taleo.com/ws/tee800/2009/01" xmlns="http://www.taleo.com/ws/integration/toolkit/2005/07" pageIndex="1" pageCount="1" pagingSize="200" entityCount="1">
                <e:Entity xsi:type="e:Candidate">
                    <e:EmailAddress>arsd@sdfg.com</e:EmailAddress>
                    <e:FirstName>Adfghjk</e:FirstName>
                    <e:LastName>asdf</e:LastName>
                    <e:MobilePhone>8320303417</e:MobilePhone>
                    <e:Number>100009662</e:Number>
                </e:Entity>
            </root:Entities>
        </ns1:findPartialEntitiesResponse>
    </soap:Body>
</soap:Envelope>
"""

soap_zero_data_packet = """
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <soap:Body>
        <ns1:findPartialEntitiesResponse xmlns:ns1="http://easychat.allincall.in/ws/tee800/2009/01/find">
            <root:Entities xmlns:root="http:/easychat.allincall.in/ws/tee800/2009/01/find" xmlns:e="http://www.taleo.com/ws/tee800/2009/01" xmlns="http://www.taleo.com/ws/integration/toolkit/2005/07" pageIndex="1" pageCount="0" pagingSize="200" entityCount="0"/>
        </ns1:findPartialEntitiesResponse>
    </soap:Body>
</soap:Envelope>
"""


def pad(string_pad):
    return string_pad + (BLOCK_SIZE - len(string_pad) %
                         BLOCK_SIZE) * chr(BLOCK_SIZE - len(string_pad) % BLOCK_SIZE)


def unpad(string_unpad):
    return string_unpad[:-ord(string_unpad[len(string_unpad) - 1:])]


def aes256encrypt(raw, password, iv):
    raw = pad(raw)
    cipher = AES.new(password.encode('utf-8'), AES.MODE_CBC, iv)
    return base64.b64encode(cipher.encrypt(raw.encode('utf-8'))).decode("utf-8")


def aes256decrypt(enc, password, iv):
    enc = base64.b64decode(enc)
    cipher = AES.new(password, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc)).decode("utf-8")


def generate_random_key(length):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))


class CustomEncrypt:

    def __init__(self):
        self.key = generate_random_key(16)
        self.iv = Random.new().read(AES.block_size)

    def encrypt(self, plain_text):
        encrypted_str = aes256encrypt(plain_text, self.key, self.iv)
        return ".".join([self.key, encrypted_str, base64.b64encode(self.iv).decode("utf-8")])

    def decrypt(self, encrypted_text):
        key, encrypted_text, iv = encrypted_text.split(".")
        iv = base64.b64decode(iv.encode("utf-8"))
        decrypted_text = aes256decrypt(
            encrypted_text.encode("utf-8"), key.encode("utf-8"), iv)
        return decrypted_text


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def dummy_return_access_token(request):
    try:
        if request.method == 'GET':
            request_client_id = request.GET['client_id']
            request_client_secret = request.GET['client_secret']
            request_grant_type = request.GET['grant_type']
            if client_id == request_client_id and client_secret == request_client_secret and grant_type == request_grant_type:
                response = {}
                response['access_token'] = access_token
                return HttpResponse(json.dumps(response), content_type="application/json")
            else:
                return HttpResponse(status=500)
        else:
            return HttpResponse(500)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("dummy_return_access_token: %s at line %s", e, str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return HttpResponse(status=500)


class FetchDummyDataAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal Server Error"
        try:
            request_access_token = request.META['HTTP_AUTHORIZATION'].split(' ')[
                1]
            if(access_token == request_access_token):
                crypt = CustomEncrypt()
                data = request.data['data']
                decrypted_data = crypt.decrypt(data)
                data = json.loads(decrypted_data)
                request_username = data['username']
                request_password = data['password']
                if request_username == username and password == request_password:
                    response["status"] = "200"
                    response["message"] = "Success"
                    response['data'] = dummy_data
                response = crypt.encrypt(json.dumps(response))
                crypt = CustomEncrypt()
                return Response(data=response)
            else:
                return Response(status=403)
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("FetchDummyDataAPI: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return Response(status=500)


class FetchSoapDataAPI(APIView):
    media_type = 'application/xml'
    parser_classes = (XMLParser, )
    renderer_classes = (XMLRenderer,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        soap_packet = soap_fault_packet

        try:
            request_access_token = request.META['HTTP_AUTHORIZATION'].split(' ')[
                1]
            if(access_token == request_access_token):
                data = request.data
                # data = xmltodict.parse(data)
                request_dob = data['{ }Body']['{ }findPartialEntities']['{ }query'][
                    '{ }query']['{ }filterings']['{ }filtering']['{ }and']['{ }equal']['{ }date']
                request_pan = data['{ }Body']['{ }findPartialEntities']['{ }query']['{ }query'][
                    '{ }filterings']['{ }filtering']['{ }and']['{ }containsIgnoreCase']['{ }string']
                if request_dob == dob and request_pan == pan:
                    soap_packet = soap_data_packet
                else:
                    soap_packet = soap_zero_data_packet
                return Response(status=200, data=soap_packet)
            else:
                return Response(status=500, data=soap_packet)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("FetchSoapDataAPI: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return Response(status=200, data=soap_packet)


class AccessTokenAPI(APIView):

    def get(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal Server Error"
        try:
            request_client_id = request.META['HTTP_CLIENTID']
            request_client_secret = request.META['HTTP_CLIENTSECRET']
            request_grant_type = request.META['HTTP_GRANTTYPE']
            if client_id == request_client_id and client_secret == request_client_secret and grant_type == request_grant_type:
                response = {}
                response['access_token'] = access_token
                response['status'] = "200"
                return HttpResponse(json.dumps(response), content_type="application/json")
            else:
                return HttpResponse(json.dumps(response), content_type="application/json")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("dummy_access_token: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return HttpResponse(status=500)


class FetchDummyBalanceAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal Server Error"
        try:
            try:
                request_access_token = request.META[
                    'HTTP_AUTHORIZATION'].split(' ')[1]
                if(access_token == request_access_token):
                    data = request.data
                    if (isinstance(data, str)):
                        data = json.loads(data)
                    request_mobile_number = data['MobNb']
                    for balance_iterator in range(0, len(balance_api_data_dictionary["balance"])):
                        if request_mobile_number in balance_api_data_dictionary["balance"][balance_iterator]['mobnumber']:
                            response['status'] = "200"
                            response['message'] = "Success"
                            response['name'] = balance_api_data_dictionary[
                                "balance"][balance_iterator]['name']
                            response['mobnumber'] = balance_api_data_dictionary[
                                "balance"][balance_iterator]['mobnumber']
                            response['account_id'] = balance_api_data_dictionary[
                                "balance"][balance_iterator]['account_id']
                            response['balance'] = balance_api_data_dictionary[
                                "balance"][balance_iterator]['balance']
            except Exception:
                data = request.data
                if (isinstance(data, str)):
                    data = json.loads(data)
                request_mobile_number = data['MobNb']
                for balance_iterator in range(0, len(balance_api_data_dictionary["balance"])):
                    if request_mobile_number in balance_api_data_dictionary["balance"][balance_iterator]['mobnumber']:
                        response['status'] = "200"
                        response['message'] = "Success"
                        response['name'] = balance_api_data_dictionary[
                            "balance"][balance_iterator]['name']
                        response['mobnumber'] = balance_api_data_dictionary[
                            "balance"][balance_iterator]['mobnumber']
                        response['account_id'] = balance_api_data_dictionary[
                            "balance"][balance_iterator]['account_id']
                        response['balance'] = balance_api_data_dictionary[
                            "balance"][balance_iterator]['balance']                    

            return Response(data=response)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("FetchDummyDataAPI: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return Response(status=500)


class FetchValuationAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = "500"
        response["message"] = "Internal Server Error"
        try:
            data = request.data
            if (isinstance(data, str)):
                data = json.loads(data)
            request_valuation_number = data['valuation_id']
            for valuation_iterator in range(0, len(valuation_dictionary["valuation_dictionary"])):
                if request_valuation_number[-4:] in valuation_dictionary["valuation_dictionary"][valuation_iterator]['valuation_id']:
                    response['status'] = "200"
                    response['message'] = "Success"
                    response['valuation_id'] = valuation_dictionary[
                        "valuation_dictionary"][valuation_iterator]['valuation_id']
                    response['scheme'] = valuation_dictionary[
                        "valuation_dictionary"][valuation_iterator]['scheme']
                    response['scheme_balance'] = valuation_dictionary[
                        "valuation_dictionary"][valuation_iterator]['scheme_balance']
                    response['NAV'] = valuation_dictionary[
                        "valuation_dictionary"][valuation_iterator]['NAV']
                    response['NAV_Date'] = valuation_dictionary[
                        "valuation_dictionary"][valuation_iterator]['NAV_Date']

            return Response(data=response)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("FetchDummyDataAPI: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return Response(status=500)
