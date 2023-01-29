import threading
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from EasyChatApp.utils import check_access_for_user
from EasyChatApp.utils_catalogue import get_item_price_after_offset, parse_catalogue_items_details, populate_missing_catalogue_details, sync_products_from_facebook, upload_catalogue_products_via_csv, validate_catalogue_csv_upload_item
from EasyChatApp.utils_validation import EasyChatInputValidation

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from EasyChatApp.models import *

from EasyChatApp.constants import *
from EasyChatApp.constants_catalogue import *

import json
import logging
import sys

import base64
import csv

logger = logging.getLogger(__name__)


class GetCatalogueDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)
            bot_id = data["bot_id"]
            bot_obj = Bot.objects.filter(
                pk=int(bot_id), is_deleted=False).first()
            if not bot_obj or request.user not in bot_obj.users.all():
                response["status"] = 401
                response["status_message"] = "You are not authorised to perform this operation."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            catalogue_object = WhatsappCatalogueDetails.objects.filter(
                bot=bot_obj).first()
            selected_language = data["selected_language"]
            if catalogue_object:
                if selected_language != "en":
                    language_obj = Language.objects.filter(
                        lang=selected_language).first()
                    lang_tuned_bot_obj = LanguageTunedBot.objects.filter(
                        language=language_obj, bot=bot_obj).first()
                    if lang_tuned_bot_obj and json.loads(lang_tuned_bot_obj.whatsapp_catalogue_data) != {}:
                        response["catalogue_metadata"] = lang_tuned_bot_obj.whatsapp_catalogue_data
                    else:
                        response["catalogue_metadata"] = catalogue_object.catalogue_metadata
                else:
                    response["catalogue_metadata"] = catalogue_object.catalogue_metadata
                response["is_catalogue_enabled"] = catalogue_object.is_catalogue_enabled
                response["catalogue_type"] = catalogue_object.catalogue_type
                response["catalogue_id"] = catalogue_object.catalogue_id
                response["catalogue_access_token"] = catalogue_object.access_token
                response["catalogue_business_id"] = catalogue_object.business_id
                catalogue_items_map = list(WhatsappCatalogueItems.objects.filter(
                    catalogue_id=catalogue_object.catalogue_id).values("item_name", "retailer_id"))
                response["catalogue_items_map"] = catalogue_items_map
                response["status"] = 200
            else:
                response["status"] = 404
                response["status_message"] = "No catalogue found for this bot!"

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In GetCatalogueDetailsAPI: %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetCatalogueDetails = GetCatalogueDetailsAPI.as_view()


class GetCatalogueProductsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Unable to fetch Catalogue Items, please try again later."
        try:
            data = request.GET

            if not isinstance(data, dict):
                data = json.loads(data)

            bot_id = data["bot_id"]
            page = data["page"]

            bot_obj = Bot.objects.filter(
                pk=int(bot_id), is_deleted=False).first()

            if not bot_obj or request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = "You are not authorised to perform this operation."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response, status=401)

            catalogue_object = WhatsappCatalogueDetails.objects.filter(
                bot=bot_obj).first()

            if catalogue_object:
                catalogue_id = catalogue_object.catalogue_id
                search_term = data.get("search_term", "")
                catalogue_items_obj = WhatsappCatalogueItems.objects.filter(
                    catalogue_id=catalogue_id)
                if search_term:
                    catalogue_items_obj = catalogue_items_obj.filter(
                        Q(item_name__icontains=search_term) | Q(retailer_id__icontains=search_term))

                if "currency" in data and data["currency"] != "" and data["currency"].lower() != "all":
                    catalogue_items_obj = catalogue_items_obj.filter(
                        currency__iexact=data["currency"])
                if "price_from" in data and data["price_from"] != "":
                    if str(data["price_from"]).isdigit():
                        price_from = int(data["price_from"])
                        catalogue_items_obj = catalogue_items_obj.filter(
                            price__gte=price_from)
                if "price_to" in data and data["price_to"] != "":
                    if str(data["price_to"]).isdigit():
                        price_to = int(data["price_to"])
                        catalogue_items_obj = catalogue_items_obj.filter(
                            price__lte=price_to)
                if "availability" in data:
                    if data["availability"] == "1":
                        catalogue_items_obj = catalogue_items_obj.filter(
                            availability__iexact="in stock")
                    elif data["availability"] == "2":
                        catalogue_items_obj = catalogue_items_obj.filter(
                            availability__iexact="out of stock")
                    elif data["availability"] == "3":
                        catalogue_items_obj = catalogue_items_obj.filter(
                            availability__iexact="available for order")
                    elif data["availability"] == "4":
                        catalogue_items_obj = catalogue_items_obj.filter(
                            availability__iexact="preorder")
                    elif data["availability"] == "5":
                        catalogue_items_obj = catalogue_items_obj.filter(
                            availability__iexact="discontinued")
                if "condition" in data and data["condition"] in ["new", "refurbished", "used_like_new", "used_good", "used_fair"]:
                    catalogue_items_obj = catalogue_items_obj.filter(
                        condition__iexact=data["condition"])
                if "gender" in data and data["gender"] in ["male", "female", "unisex"]:
                    catalogue_items_obj = catalogue_items_obj.filter(
                        gender__iexact=data["gender"])

                try:
                    total_rows_per_pages = int(data["items_per_page"])
                except:
                    total_rows_per_pages = 25

                if total_rows_per_pages not in [10, 25, 50, 75, 100]:
                    total_rows_per_pages = 25

                total_catalogue_objs = len(catalogue_items_obj)

                paginator = Paginator(
                    catalogue_items_obj, total_rows_per_pages)

                try:
                    catalogue_items_obj = paginator.page(page)
                except PageNotAnInteger:
                    catalogue_items_obj = paginator.page(1)
                except EmptyPage:
                    catalogue_items_obj = paginator.page(paginator.num_pages)

                if page != None:
                    start_point = total_rows_per_pages * (int(page) - 1) + 1
                    end_point = min(total_rows_per_pages *
                                    int(page), total_catalogue_objs)
                    if start_point > end_point:
                        start_point = max(
                            end_point - len(catalogue_items_obj) + 1, 1)
                else:
                    start_point = 1
                    end_point = min(total_rows_per_pages, total_catalogue_objs)

                start_point = min(start_point, end_point)

                pagination_range = catalogue_items_obj.paginator.page_range

                has_next = catalogue_items_obj.has_next()
                has_previous = catalogue_items_obj.has_previous()
                next_page_number = -1
                previous_page_number = -1

                if has_next:
                    next_page_number = catalogue_items_obj.next_page_number()
                if has_previous:
                    previous_page_number = catalogue_items_obj.previous_page_number()

                pagination_metadata = {
                    'total_count': total_catalogue_objs,
                    'start_point': start_point,
                    'end_point': end_point,
                    'page_range': [pagination_range.start, pagination_range.stop],
                    'has_next': has_next,
                    'has_previous': has_previous,
                    'next_page_number': next_page_number,
                    'previous_page_number': previous_page_number,
                    'number': catalogue_items_obj.number,
                    'num_pages': catalogue_items_obj.paginator.num_pages
                }
                catalogue_items = []
                for catalogue_item in catalogue_items_obj:
                    catalogue_items.append(parse_catalogue_items_details(
                        catalogue_item))
                response["catalogue_items"] = catalogue_items
                response["pagination_metadata"] = pagination_metadata
                response["status"] = 200
                response["message"] = "Success"

            else:
                response["status"] = 404
                response["message"] = "No Catalogue found for this bot!"

        except requests.Timeout as RT:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetCatalogueItemsAPI Timeout error: %s", str(RT), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response["status"] = 408
            response["message"] = "Request for fetching Catalogue Items Timed Out. Please try again later."

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In GetCatalogueItemsAPI: %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        api_response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=api_response)


GetCatalogueProducts = GetCatalogueProductsAPI.as_view()


def WhatsappCatalogueManager(request):  # noqa: N802
    try:
        if request.user.is_authenticated:
            try:
                user_obj = request.user
                if "id" not in request.GET:
                    return HttpResponse("Invalid BOT ID")
                bot_pk = request.GET["id"]
                bot_obj = Bot.objects.filter(pk=int(bot_pk), users__in=[
                    user_obj], is_deleted=False).first()
                if not bot_obj or not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return render(request, 'EasyChatApp/unauthorized.html')

                return render(request, 'EasyChatApp/channels/whatsapp_catalogue_manager.html', {
                    "user_obj": user_obj,
                    "selected_bot_obj": bot_obj
                })
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("WhatsappCatalogueManager %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                return render(request, 'EasyChatApp/error_500.html')
        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("WhatsappCatalogueManager ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return render(request, 'EasyChatApp/error_404.html')


class CatalogueProductsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Unable to Sync and Fetch Catalogue Products, Please Try Again Later"
        try:
            data = request.GET

            if not isinstance(data, dict):
                data = json.loads(data)

            bot_id = data["bot_id"]

            bot_obj = Bot.objects.filter(
                pk=int(bot_id), is_deleted=False).first()

            if not bot_obj or request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = "You are not authorised to perform this operation."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response, status=401)

            catalogue_object = WhatsappCatalogueDetails.objects.filter(
                bot=bot_obj).first()

            if catalogue_object:

                catalogue_id = catalogue_object.catalogue_id
                access_token = catalogue_object.access_token
                if not catalogue_id or str(catalogue_id).strip() == "":
                    response["status"] = 404
                    response["message"] = "Catalogue ID not found, please make sure a valid Catalogue ID is saved for this Bot"
                if not access_token or str(access_token).strip() == "":
                    response["status"] = 404
                    response["message"] = "Access Token not found, please make sure a valid Access Token is saved for this Bot"
                if response["status"] == 404:
                    custom_encrypt_obj = CustomEncrypt()
                    api_response = custom_encrypt_obj.encrypt(
                        json.dumps(response))
                    return Response(data=api_response)

                sync_products_thread = threading.Thread(
                    target=sync_products_from_facebook, args=[response, catalogue_id, access_token, bot_obj, request.user])
                sync_products_thread.daemon = True
                sync_products_thread.start()
                response["status"] = 200
                # response = sync_products_from_facebook(
                #     response, catalogue_id, access_token, bot_obj, request.user)
            else:
                response["status"] = 404
                response["message"] = "No Catalogue found for the requested bot"

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In CatalogueProductsAPI: %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        api_response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=api_response)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error in creating catalogue items. Please try again later."
        try:
            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)
            bot_id = data["bot_id"]
            catalogue_items_data = data["catalogue_items_data"]

            bot_obj = Bot.objects.filter(
                pk=int(bot_id), is_deleted=False).first()

            if not bot_obj or request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = "You are not authorised to perform this operation."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response, status=401)

            catalogue_object = WhatsappCatalogueDetails.objects.filter(
                bot=bot_obj).first()
            if catalogue_object:
                access_token = catalogue_object.access_token
                catalogue_id = catalogue_object.catalogue_id
                if not catalogue_id or str(catalogue_id).strip() == "":
                    response["status"] = 404
                    response["message"] = "Catalogue ID not found, please make sure a valid Catalogue ID is saved for this Bot"
                if not access_token or str(access_token).strip() == "":
                    response["status"] = 404
                    response["message"] = "Access Token not found, please make sure a valid Access Token is saved for this Bot"
                if len(catalogue_items_data) > 6:
                    response["status"] = 304
                    response["message"] = "Maximum 5 items can be created at once!"
                if response["status"] == 404 or response["status"] == 304:
                    custom_encrypt_obj = CustomEncrypt()
                    api_response = custom_encrypt_obj.encrypt(
                        json.dumps(response))
                    return Response(data=api_response)

                successfully_added_items = []
                api_error_messages = {}

                for catalogue_item in catalogue_items_data:
                    active_item = catalogue_items_data[catalogue_item]
                    active_item["access_token"] = access_token
                    active_item = get_item_price_after_offset(active_item)
                    facebook_api = FACEBOOK_GRAPH_BASE_URL + catalogue_id + "/products/"
                    try:
                        facebook_api_request = requests.post(
                            facebook_api, json=active_item, timeout=20, verify=True)

                        if facebook_api_request.status_code == 200:
                            facebook_api_response = facebook_api_request.text
                            successfully_added_items.append(catalogue_item)
                        else:
                            facebook_api_response = json.loads(
                                facebook_api_request.text)
                            # response["status"] = facebook_api_response.status_code
                            if "error" in facebook_api_response and "message" in facebook_api_response["error"]:
                                api_error_messages[catalogue_item
                                                   ] = facebook_api_response["error"]["message"]
                                if "error_user_msg" in facebook_api_response["error"]:
                                    api_error_messages[catalogue_item
                                                       ] = facebook_api_response["error"]["message"] + " " + facebook_api_response["error"]["error_user_msg"]
                    except requests.Timeout as RT:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Create CatalogueProductsAPI Timeout error: %s", str(RT), extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        api_error_messages[catalogue_item
                                           ] = "Request for creating this Catalogue Item Timed Out."

                if not api_error_messages:
                    response["status"] = 200
                    response["message"] = "Items added successfully!"
                elif len(api_error_messages) == len(catalogue_items_data):
                    response["status"] = 300
                    response["message"] = "Failed to add items in WhatsApp Catalogue"
                    response["api_error_messages"] = json.dumps(
                        api_error_messages)
                    response["successfully_added_items"] = successfully_added_items
                else:
                    response["status"] = 302
                    response["message"] = "Failed to add some items in WhatsApp Catalogue"
                    response["api_error_messages"] = json.dumps(
                        api_error_messages)
                    response["successfully_added_items"] = successfully_added_items
            else:
                response["status"] = 305
                response["message"] = "No catalogue found for this bot!"
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In GetCatalogueDetailsAPI: %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CatalogueProducts = CatalogueProductsAPI.as_view()


class DeleteCatalogueProductsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error in deleting Catalogue Item(s), please try again later."
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)
            bot_id = data["bot_id"]
            bot_obj = Bot.objects.filter(
                pk=int(bot_id), is_deleted=False).first()
            if not bot_obj or request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = "You are not authorised to perform this operation."
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            catalogue_object = WhatsappCatalogueDetails.objects.filter(
                bot=bot_obj).first()

            if catalogue_object:
                access_token = catalogue_object.access_token
                if not access_token or str(access_token).strip() == "":
                    response["status"] = 404
                    response["message"] = "Access Token not found, please make sure a valid Access Token is saved for this Bot"
                if "product_ids" not in data:
                    response["status"] = 404
                    response["message"] = "Please provide valid Product IDs to be deleted"
                if response["status"] == 404:
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
                product_ids = data["product_ids"]
                api_error_messages = []
                for product_id in product_ids:
                    facebook_product_delete_api = FACEBOOK_GRAPH_BASE_URL + \
                        product_id + "?access_token=" + access_token
                    try:
                        facebook_api_request = requests.delete(
                            facebook_product_delete_api, timeout=20, verify=True)
                        if facebook_api_request.status_code != 200:
                            facebook_api_response = json.loads(
                                facebook_api_request.text)
                            if "error" in facebook_api_response and "message" in facebook_api_response["error"]:
                                api_error_messages.append(
                                    facebook_api_response["error"]["message"])
                    except requests.Timeout as RT:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("DeleteCatalogueProductAPI Timeout error: %s", str(RT), extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        api_error_messages.append(
                            "Request for deleting this Catalogue Item Timed Out.")
                if len(api_error_messages) == len(product_ids):
                    response["status"] = 300
                    response["message"] = "Failed to delete catalogue item(s), please try again later."
                    response["api_error_messages"] = api_error_messages
                elif len(api_error_messages) > 0 and len(api_error_messages) != len(product_ids):
                    response["status"] = 301
                    response[
                        "message"] = "Failed to delete some of the catalogue item(s), please try again later."
                    response["api_error_messages"] = api_error_messages
                else:
                    response["status"] = 200
                    response["message"] = "Item(s) deleted successfully!"
            else:
                response["status"] = 404
                response["message"] = "No catalogue found for this bot!"

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In DeleteCatalogueProductAPI: %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DeleteCatalogueProducts = DeleteCatalogueProductsAPI.as_view()


class UpdateCatalogueProductAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error in updating Catalogue Item, please try again later."
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)
            bot_id = data["bot_id"]
            bot_obj = Bot.objects.filter(
                pk=int(bot_id), is_deleted=False).first()
            if not bot_obj or request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = "You are not authorised to perform this operation."
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            catalogue_object = WhatsappCatalogueDetails.objects.filter(
                bot=bot_obj).first()

            if catalogue_object:
                access_token = catalogue_object.access_token
                if not access_token or str(access_token).strip() == "":
                    response["status"] = 404
                    response["message"] = "Access Token not found, please make sure a valid Access Token is saved for this Bot"
                if "product_id" not in data:
                    response["status"] = 404
                    response["message"] = "Please provide a valid Product ID to be updated"
                if "updated_item_data" not in data:
                    response["status"] = 404
                    response["message"] = "Please provide the data of the item to be updated"
                if response["status"] == 404:
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
                product_id = data["product_id"]
                updated_item_data = data["updated_item_data"]
                is_update_successfull = False
                updated_item_data["edit_item"] = get_item_price_after_offset(updated_item_data["edit_item"])
                facebook_product_update_api = FACEBOOK_GRAPH_BASE_URL + \
                    product_id + "?access_token=" + access_token
                try:
                    facebook_api_request = requests.post(
                        facebook_product_update_api, json=updated_item_data["edit_item"], timeout=20, verify=True)
                    if facebook_api_request.status_code == 200:
                        is_update_successfull = True
                    else:
                        is_update_successfull = False
                        facebook_api_response = json.loads(
                            facebook_api_request.text)
                        if "error" in facebook_api_response and "message" in facebook_api_response["error"]:
                            response["message"] = facebook_api_response["error"]["message"]
                            if "error_user_msg" in facebook_api_response["error"]:
                                response["message"] = response["message"] + " " + \
                                    facebook_api_response["error"]["error_user_msg"]
                except requests.Timeout as RT:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("UpdateCatalogueProductAPI Timeout error: %s", str(RT), extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    response["message"] = "Request for updating this Catalogue Item Timed Out."
                if not is_update_successfull:
                    response["status"] = 300
                else:
                    response["status"] = 200
                    response["message"] = "Item(s) deleted successfully!"
            else:
                response["status"] = 404
                response["message"] = "No catalogue found for this bot!"

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In UpdateCatalogueProductAPI: %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateCatalogueProduct = UpdateCatalogueProductAPI.as_view()


class AddCatalogueDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error in Adding and Syncing Catalogue Details, please try again later."
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            if "bot_id" not in data or str(data["bot_id"]).strip() == "":
                response["status"] = 304
                response["message"] = "Please provide a valid BOT ID."

            if "access_token" not in data or str(data["access_token"]).strip() == "":
                response["status"] = 304
                response["message"] = "Please provide a valid access token."

            if "catalogue_id" not in data or str(data["catalogue_id"]).strip() == "":
                response["status"] = 304
                response["message"] = "Please provide a valid catalogue ID."

            if response["status"] == 304:
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot_id = data["bot_id"]

            bot_obj = Bot.objects.filter(
                pk=int(bot_id), is_deleted=False).first()
            if not bot_obj or request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = "You are not authorised to perform this operation."
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            access_token = data["access_token"]
            catalogue_id = data["catalogue_id"]

            catalogue_object = WhatsappCatalogueDetails.objects.filter(
                bot=bot_obj).first()

            if not catalogue_object:
                catalogue_metadata = {
                    "access_token": access_token, "catalogue_id": catalogue_id}
                WhatsappCatalogueDetails.objects.create(
                    bot=bot_obj, access_token=access_token, catalogue_id=catalogue_id, catalogue_metadata=json.dumps(catalogue_metadata))

            sync_products_thread = threading.Thread(
                target=sync_products_from_facebook, args=[response, catalogue_id, access_token, bot_obj, request.user, True])
            sync_products_thread.daemon = True
            sync_products_thread.start()
            response["status"] = 200

            if response["status"] != 200:
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In AddCatalogueDetailsAPI: %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AddCatalogueDetails = AddCatalogueDetailsAPI.as_view()


class UploadProductsCSVAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error in creating products via CSV, please try again later."
        custom_encrypt_obj = CustomEncrypt()
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            bot_id = data["bot_id"]

            bot_obj = Bot.objects.filter(
                pk=int(bot_id), is_deleted=False).first()
            if not bot_obj or request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = "You are not authorised to perform this operation."
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            catalogue_object = WhatsappCatalogueDetails.objects.filter(
                bot=bot_obj).first()
            if catalogue_object:
                access_token = catalogue_object.access_token
                catalogue_id = catalogue_object.catalogue_id
                if not catalogue_id or str(catalogue_id).strip() == "":
                    response["status"] = 404
                    response["message"] = "Catalogue ID not found, please make sure a valid Catalogue ID is saved for this Bot"
                if not access_token or str(access_token).strip() == "":
                    response["status"] = 404
                    response["message"] = "Access Token not found, please make sure a valid Access Token is saved for this Bot"
            else:
                response["status"] = 404
                response["message"] = "No saved catalogue found for this bot, please make sure catalogue and its details are saved."

            if response["status"] == 404:
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            base64_data = data["base64_file"]
            original_file_name = data["filename"]
            if not os.path.exists('secured_files/EasyChatApp/catalogue_csv_uploads'):
                os.makedirs(
                    'secured_files/EasyChatApp/catalogue_csv_uploads')

            file_name = request.user.username + "_BOT-" + \
                str(bot_id) + "_" + \
                timezone.now().strftime("%d-%m-%Y %H:%M:%S") + '.csv'
            file_path = "secured_files/EasyChatApp/catalogue_csv_uploads/" + file_name
            fh = open(file_path, "wb")
            fh.write(base64.b64decode(base64_data))
            fh.close()

            upload_products_thread = threading.Thread(
                target=upload_catalogue_products_via_csv, args=[original_file_name, file_path, request.user, bot_obj, access_token, catalogue_id])
            upload_products_thread.daemon = True
            upload_products_thread.start()
            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In UploadProductsCSVAPI: %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UploadProductsCSV = UploadProductsCSVAPI.as_view()


class DownloadCatalogueCSVTemplateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        custom_encrypt_obj = CustomEncrypt()

        try:

            export_path = ("/files/templates/Catalogue_CSV_Template.csv")

            export_path_exist = os.path.exists(settings.BASE_DIR + export_path)

            response["status"] = 200
            response["export_path"] = export_path
            response["export_path_exist"] = export_path_exist
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In DownloadCatalogueCSVTemplateAPI: %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DownloadCatalogueCSVTemplate = DownloadCatalogueCSVTemplateAPI.as_view()
