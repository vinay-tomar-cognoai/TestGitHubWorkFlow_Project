from EasyChatApp.utils_execute_query import *
import logging

from re import sub
from decimal import Decimal
import imghdr
import pytz

from EasyChatApp.utils_validation import EasyChatFileValidation

logger = logging.getLogger(__name__)
log_param = {'AppName': 'EasyChat', 'user_id': 'None',
             'source': 'None', 'channel': 'None', 'bot_id': 'None'}

TIME_ZONE = pytz.timezone(settings.TIME_ZONE)


def parse_catalogue_items_details(catalogue_item):
    active_catalogue_item = dict()
    try:

        active_catalogue_item = {
            "item_id": catalogue_item.item_id,
            "name": catalogue_item.item_name,
            "availability": catalogue_item.availability,
            "gender": catalogue_item.gender,
            "price": catalogue_item.price,
            "currency": catalogue_item.currency,
            "retailer_id": catalogue_item.retailer_id,
            "condition": catalogue_item.condition,
            "brand": catalogue_item.brand,
            "image_url": catalogue_item.image_url,
            "preview_image_urls": catalogue_item.preview_image_urls,
            "details_dump": catalogue_item.item_details
        }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error parse_catalogue_items_details %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return active_catalogue_item


def populate_missing_catalogue_details(catalogue_item):
    try:
        if "id" not in catalogue_item or str(catalogue_item["id"]).strip() == "":
            catalogue_item["id"] = "-"
        if "retailer_id" not in catalogue_item or str(catalogue_item["retailer_id"]).strip() == "":
            catalogue_item["retailer_id"] = "-"
        if "brand" not in catalogue_item or str(catalogue_item["brand"]).strip() == "":
            catalogue_item["brand"] = "-"
        if "gender" not in catalogue_item or str(catalogue_item["gender"]).strip() == "":
            catalogue_item["gender"] = "-"
        if "price" not in catalogue_item or str(catalogue_item["price"]).strip() == "":
            catalogue_item["price"] = "-"
        if "sale_price" not in catalogue_item or str(catalogue_item["sale_price"]).strip() == "":
            catalogue_item["sale_price"] = ""
        if "condition" not in catalogue_item or str(catalogue_item["condition"]).strip() == "":
            catalogue_item["condition"] = "-"
        if "currency" not in catalogue_item or str(catalogue_item["currency"]).strip() == "":
            catalogue_item["currency"] = "-"
        if "availability" not in catalogue_item or str(catalogue_item["availability"]).strip() == "":
            catalogue_item["availability"] = "-"
        if "image_url" not in catalogue_item or str(catalogue_item["image_url"]).strip() == "":
            catalogue_item["image_url"] = "-"
        if "description" not in catalogue_item or str(catalogue_item["description"]).strip() == "":
            catalogue_item["description"] = ""
        if "category" not in catalogue_item or str(catalogue_item["category"]).strip() == "":
            catalogue_item["category"] = ""
        if "pattern" not in catalogue_item or str(catalogue_item["pattern"]).strip() == "":
            catalogue_item["pattern"] = ""
        if "material" not in catalogue_item or str(catalogue_item["material"]).strip() == "":
            catalogue_item["material"] = ""
        if "color" not in catalogue_item or str(catalogue_item["color"]).strip() == "":
            catalogue_item["color"] = ""
        if "fb_product_category" not in catalogue_item or str(catalogue_item["fb_product_category"]).strip() == "":
            catalogue_item["fb_product_category"] = ""

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error populate_missing_catalogue_details %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return catalogue_item


def validate_catalogue_details(catalogue_via, catalogue_metadata):
    try:
        error_message = None
        validation_obj = EasyChatInputValidation()
        if catalogue_via == COMMERCE_MANAGER_CATALOGUE_CHOICE:
            error_message, catalogue_metadata = validate_catalogue_via_commerce_manager_data(
                catalogue_metadata, validation_obj)
        elif catalogue_via == API_CATALOGUE_CHOICE:
            error_message, catalogue_metadata = validate_catalogue_via_api_data(
                catalogue_metadata, validation_obj)
        return error_message, catalogue_metadata
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("validate_catalogue_details: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

        return "Error in validating catalogue details, please verify all the details", catalogue_metadata


def validate_catalogue_via_api_data(catalogue_metadata, validation_obj):
    try:
        error_message = None
        if "business_id" not in catalogue_metadata:
            error_message = "Please enter a valid Business ID"
        if "access_token" not in catalogue_metadata:
            error_message = "Please enter a valid Access Token"
        catalogue_metadata['business_id'] = validation_obj.remo_html_from_string(
            catalogue_metadata['business_id'])
        catalogue_metadata['access_token'] = validation_obj.remo_html_from_string(
            catalogue_metadata['access_token'])
        if catalogue_metadata['business_id'].strip() == "":
            error_message = "Business ID cannot be empty!"
        if catalogue_metadata['access_token'].strip() == "":
            error_message = "Access Token cannot be empty!"
        catalogue_metadata['body_text'] = validation_obj.clean_html(
            catalogue_metadata['body_text'].strip())
        if catalogue_metadata['body_text'] == "":
            error_message = "Body Text cannot be empty!"
        catalogue_metadata['catalogue_id'] = validation_obj.remo_html_from_string(
            catalogue_metadata['catalogue_id'])
        catalogue_metadata['footer_text'] = validation_obj.remo_html_from_string(
            catalogue_metadata['footer_text'])

        if catalogue_metadata['catalogue_id'].strip() == "":
            error_message = "Catalogue ID cannot be empty!"
        sections_to_be_deleted = []
        for section_id in catalogue_metadata["sections"]:
            if section_id == "active_section":
                sections_to_be_deleted.append(section_id)
                continue
            if catalogue_metadata["sections"][section_id]["catalogue_type"] != API_CATALOGUE_CHOICE:
                sections_to_be_deleted.append(section_id)
                continue
            for product_id in catalogue_metadata["sections"][section_id]["product_ids"]:
                if product_id.strip() == "":
                    error_message = "Product ID cannot be empty!"
            section_title = catalogue_metadata["sections"][section_id]["section_title"].strip(
            )
            if section_title == "" or len(section_title) > 24:
                error_message = "Please enter a valid Section Title (Max 24 characters)"
        for section_id in sections_to_be_deleted:
            del catalogue_metadata["sections"][section_id]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in validate_catalogue_via_api_data %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return error_message, catalogue_metadata


def validate_catalogue_via_commerce_manager_data(catalogue_metadata, validation_obj):
    try:
        error_message = None
        catalogue_type = catalogue_metadata["catalogue_type"]
        if catalogue_type not in [SINGLE_PRODUCT_CHOICE, MULTIPLE_PRODUCT_CHOICE]:
            error_message = "Please select a valid Catalogue Type!"
        if catalogue_metadata['body_text'].strip() == "":
            error_message = "Body Text cannot be empty!"
        catalogue_metadata['footer_text'] = validation_obj.remo_html_from_string(
            catalogue_metadata['footer_text'])
        catalogue_metadata['catalogue_id'] = validation_obj.remo_html_from_string(
            catalogue_metadata['catalogue_id'])
        catalogue_metadata['body_text'] = validation_obj.clean_html(
            catalogue_metadata['body_text'].strip())

        if catalogue_metadata['catalogue_id'].strip() == "":
            error_message = "Catalogue ID cannot be empty!"
        if catalogue_type == SINGLE_PRODUCT_CHOICE:
            catalogue_metadata['product_id'] = validation_obj.remo_html_from_string(
                catalogue_metadata['product_id'])
            if catalogue_metadata['product_id'].strip() == "":
                error_message = "Product ID cannot be empty!"
            return error_message, catalogue_metadata
        catalogue_metadata['header_text'] = validation_obj.remo_html_from_string(
            catalogue_metadata['header_text'])
        if catalogue_metadata['header_text'].strip() == "":
            error_message = "Header Text cannot be empty!"
        # if not len(catalogue_metadata["sections"]):
        #     error_message = "Atleast one section is required for Multiple Product Catalogue."
        #     return error_message, catalogue_metadata
        sections_to_be_deleted = []
        for section_id in catalogue_metadata["sections"]:
            if section_id == "active_section":
                sections_to_be_deleted.append(section_id)
                continue
            if catalogue_metadata["sections"][section_id]["catalogue_type"] != COMMERCE_MANAGER_CATALOGUE_CHOICE:
                sections_to_be_deleted.append(section_id)
                continue
            for product_id in catalogue_metadata["sections"][section_id]["product_ids"]:
                if product_id.strip() == "":
                    error_message = "Product ID cannot be empty!"
            section_title = catalogue_metadata["sections"][section_id]["section_title"].strip(
            )
            if section_title == "" or len(section_title) > 24:
                error_message = "Please enter a valid Section Title (Max 24 characters)"
        for section_id in sections_to_be_deleted:
            del catalogue_metadata["sections"][section_id]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in validate_catalogue_via_commerce_manager_data %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return error_message, catalogue_metadata


def sync_products_from_facebook(response, catalogue_id, access_token, bot_obj, user_obj, catalogue_items_map_required=False):
    try:
        event_obj = EventProgress.objects.create(
            user=user_obj,
            bot=bot_obj,
            event_type='sync_products',
        )
        catalogue_items_obj = []
        request_obj = requests.get(
            url=FACEBOOK_GRAPH_BASE_URL + catalogue_id + "/products?access_token=" + access_token + "&fields=id,retailer_id,name,price,currency,image_url,description,sale_price,sale_price_start_date,sale_price_end_date,condition,gender,retailer_product_group_id,origin_country,product_group,availability,url,brand,category,pattern,material,color,fb_product_category,additional_image_urls")
        item_ids = []
        if request_obj.status_code == 200:
            facebook_response = json.loads(request_obj.text)
            catalogue_items_obj += facebook_response["data"]
            try:
                while "paging" in facebook_response and "next" in facebook_response["paging"]:
                    pagination_req_obj = requests.get(
                        url=facebook_response["paging"]["next"])
                    facebook_response = json.loads(pagination_req_obj.text)
                    if "data" in json.loads(request_obj.text):
                        catalogue_items_obj += facebook_response["data"]
            except:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error in sync_products_from_facebook %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra=log_param)

            for item in catalogue_items_obj:
                item = populate_missing_catalogue_details(item)
                item_ids.append(item["id"])

                item_price = Decimal(
                    sub(r'[^\d\-.]', '', item["price"]))  # Removing Currency Symbols and other special symbols

                preview_image_urls = store_media_on_server(item)
                update_status = WhatsappCatalogueItems.objects.filter(
                    catalogue_id=catalogue_id, retailer_id=item["retailer_id"]).update(item_details=json.dumps(item),
                                                                                       item_id=item["id"],
                                                                                       item_name=item["name"],
                                                                                       brand=item["brand"],
                                                                                       price=item_price,
                                                                                       gender=item["gender"],
                                                                                       condition=item["condition"],
                                                                                       currency=item["currency"],
                                                                                       availability=item["availability"],
                                                                                       image_url=item["image_url"],
                                                                                       preview_image_urls=json.dumps(preview_image_urls))
                if not update_status:
                    WhatsappCatalogueItems.objects.create(catalogue_id=catalogue_id,
                                                          item_id=item["id"],
                                                          retailer_id=item["retailer_id"],
                                                          item_details=json.dumps(
                                                              item),
                                                          brand=item["brand"],
                                                          item_name=item["name"],
                                                          price=item_price,
                                                          gender=item["gender"],
                                                          condition=item["condition"],
                                                          currency=item["currency"],
                                                          availability=item["availability"],
                                                          image_url=item["image_url"],
                                                          preview_image_urls=json.dumps(preview_image_urls))
            WhatsappCatalogueItems.objects.filter(
                catalogue_id=catalogue_id).exclude(item_id__in=item_ids).delete()
            response["status"] = 200
            response["message"] = "Success"

        else:
            response_packet = json.loads(request_obj.text)
            response["status"] = request_obj.status_code
            if "error" in response_packet and "message" in response_packet["error"]:
                response["message"] = response_packet["error"]["message"]

        if catalogue_items_map_required:
            catalogue_items_map = list(WhatsappCatalogueItems.objects.filter(
                catalogue_id=catalogue_id).values("item_name", "retailer_id"))

            response["catalogue_items_map"] = catalogue_items_map

        event_obj.event_info = json.dumps(response)
        event_obj.is_completed = True
        event_obj.event_progress = 100
        event_obj.completed_datetime = datetime.datetime.now()
        event_obj.save(update_fields=['event_info', 'is_completed', 'event_progress', 'completed_datetime'])

    except requests.Timeout as RT:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("CatalogueProductsAPI sync_products_from_facebook Timeout error: %s",
                     str(RT), extra=log_param)
        response["status"] = 408
        response["message"] = "Request for fetching Catalogue Items Timed Out. Please try again later."
        event_obj.event_info = json.dumps(response)
        event_obj.is_failed = True
        event_obj.is_completed = False
        event_obj.save(update_fields=['event_info', 'is_completed', 'is_failed'])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in sync_products_from_facebook %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
        event_obj.event_info = json.dumps(response)
        event_obj.is_failed = True
        event_obj.is_completed = False
        event_obj.save(update_fields=['event_info', 'is_completed', 'is_failed'])

    return response


def store_media_on_server(item_obj):
    try:
        preview_image_urls = []
        allowed_files_list = ["png", "jpg", "jpeg", "bmp",
                              "tiff", "exif", "jfif", "webm", "webp", "mpg", "jpe"]
        file_validation_obj = EasyChatFileValidation()
        main_image_url = item_obj["image_url"]
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1",
                   "DNT": "1", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate"}
        product_image_urls = [main_image_url]
        if "additional_image_urls" in item_obj and item_obj["additional_image_urls"]:
            product_image_urls += item_obj["additional_image_urls"]
        for product_image_url in product_image_urls:
            try:
                url_hash = hashlib.md5(product_image_url.encode()).hexdigest()
                parsed_url = urlparse(product_image_url)
                # No need to cache if the URL is already of our server
                if parsed_url.hostname == settings.EASYCHAT_DOMAIN:
                    preview_url = product_image_url
                else:
                    file_cache_obj = EasyChatFileCaching.objects.filter(
                        url_hash=url_hash).first()
                    if file_cache_obj:
                        preview_url = file_cache_obj.file_url
                    else:
                        response = requests.get(
                            url=product_image_url, headers=headers, timeout=10)
                        image_base64_data = base64.b64encode(response.content)

                        file_ext = imghdr.what(file=None, h=response.content)

                        # If we do not get file extension from imghdr.what
                        # We split the url and try to get file extension, and if we do not get the extension in it
                        # We use get_file_extension_from_content to guess extension with MIME type
                        if file_ext is None:
                            file_name_split = product_image_url.split('.')
                            if file_name_split:
                                file_ext = file_name_split[-1]
                        if file_ext is None or file_ext.lower() not in allowed_files_list:
                            file_ext_from_mime_type = file_validation_obj.get_file_extension_from_content(
                                image_base64_data)
                            if file_ext_from_mime_type:
                                file_ext = file_ext_from_mime_type.split(
                                    ".")[-1]
                        if file_ext is None or file_ext.lower() not in allowed_files_list:
                            preview_image_urls.append("-")
                            continue
                        file_name = str(uuid.uuid4()) + '.' + file_ext

                        if not os.path.exists(settings.MEDIA_ROOT + 'FileCache'):
                            os.makedirs(settings.MEDIA_ROOT + 'FileCache')

                        file_path = settings.MEDIA_ROOT + 'FileCache/' + file_name
                        fh = open(file_path, "wb")
                        fh.write(base64.b64decode(image_base64_data))
                        fh.close()

                        original_file = Image.open(
                            settings.MEDIA_ROOT + 'FileCache/' + file_name)
                        original_file.thumbnail((1024, 1024))

                        original_file.save(
                            settings.MEDIA_ROOT + 'FileCache/' + file_name)

                        preview_url = settings.EASYCHAT_HOST_URL + "/files/FileCache/" + \
                            file_name

                        EasyChatFileCaching.objects.create(
                            url_hash=url_hash, file_url=preview_url, file_path=file_path, original_url=product_image_url)

                preview_image_urls.append(preview_url)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("store_media_on_server: %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra=log_param)
                preview_image_urls.append("-")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("store_media_on_server: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
        preview_image_urls.append("-")

    return preview_image_urls


def upload_catalogue_products_via_csv(original_file_name, file_path, user_obj, bot_obj, access_token, catalogue_id):
    try:
        start_time = time.time()
        event_obj = EventProgress.objects.create(
            user=user_obj,
            bot=bot_obj,
            event_type='upload_catalogue_products',
        )
        response = {}
        total_rows = 0
        headers = []
        error_present_headers = []
        headers_index_map = {}
        index_headers_map = {}
        item_details = {}
        errors_map = {}
        with open(file_path, 'r') as products_csv_file:
            reader = csv.reader(
                products_csv_file, quoting=csv.QUOTE_ALL, skipinitialspace=True)
            for row in reader:
                if total_rows >= 152:
                    response["products_limit_exceed"] = True
                    event_obj.event_info = json.dumps(response)
                    event_obj.save(update_fields=["event_info"])
                    break
                total_rows += 1
                if total_rows == 2:  # 2nd row consists of the headers
                    headers = row
                    for index in range(len(headers)):
                        if headers[index] in headers_index_map:
                            continue
                        headers_index_map[headers[index]] = index
                        index_headers_map[index] = headers[index]
                    for header in REQUIRED_CATALOGUE_HEADERS:
                        if header not in headers_index_map and header not in error_present_headers:  # Required header is missing
                            error_present_headers.append(header)
                            errors_map["header_missing"] = True
                elif total_rows > 2:  # From 3rd row, item details start
                    # item = row[:len(index_headers_map)]
                    item = row
                    required_header_missing = False
                    if "header_missing" in errors_map:
                        errors_map[total_rows] = {}
                        errors_map[total_rows]["item_details"] = item
                        errors_map[total_rows]["error_mapping"] = {
                            -1: "Required header is missing"}
                        required_header_missing = True
                    error_in_item, active_item, errors_map, error_present_headers = validate_catalogue_csv_upload_item(
                        item, total_rows, errors_map, index_headers_map, error_present_headers, required_header_missing)
                    if not error_in_item and "header_missing" not in errors_map:
                        item_details[total_rows] = active_item
                    else:
                        item_details[total_rows] = "error_in_item"
        if total_rows > 2:
            errors_map = upload_item_details_on_facebook(
                item_details, errors_map, bot_obj, access_token, catalogue_id, event_obj)
        if (len(errors_map)):
            response["status"] = 201
        elif total_rows <= 2:
            response["status"] = 202
        else:
            response["status"] = 200

        response["errors_map"] = errors_map
        # Because first 2 rows are not items
        response["total_items"] = total_rows - 2
        response["headers_index_map"] = headers_index_map
        response["error_present_headers"] = error_present_headers
        response["original_file_name"] = original_file_name
        event_obj.event_info = json.dumps(response)
        event_obj.is_completed = True
        event_obj.event_progress = 100
        event_obj.completed_datetime = timezone.now()
        event_obj.time_taken = time.time() - start_time
        event_obj.save(update_fields=[
                       'event_info', 'is_completed', 'event_progress', 'completed_datetime', 'time_taken'])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("upload_catalogue_products_via_csv: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
        response["message"] = "Failed to upload the file, please make sure it is a valid CSV file and all the inputs are according to standard"
        event_obj.event_info = json.dumps(response)
        event_obj.is_failed = True
        event_obj.is_completed = False
        event_obj.time_taken = time.time() - start_time
        event_obj.save(
            update_fields=['event_info', 'is_completed', 'is_failed', 'time_taken'])


def validate_catalogue_csv_upload_item(item, row, errors_map, index_headers_map, error_present_headers, required_header_missing):
    try:
        validation_obj = EasyChatInputValidation()
        active_item = {}
        error_in_item = False
        error_mapping = {}
        for index, detail in enumerate(item):
            if index not in index_headers_map:
                continue
            detail = str(detail).strip()
            space_removing_pattern = re.compile(r'\s+')
            header_name = str(index_headers_map[index]).lower()
            if header_name not in FB_SUPPORTED_CATALOGUE_FIELDS:
                continue
            if detail == "" and header_name in REQUIRED_CATALOGUE_HEADERS:
                # Required field is empty
                error_in_item = True
                error_mapping[index] = header_name + " is missing"
                if header_name not in error_present_headers:
                    error_present_headers.append(header_name)
                continue
            elif detail == "" and header_name not in REQUIRED_CATALOGUE_HEADERS:
                continue
            if header_name == "name" and len(detail) > 150:
                error_in_item = True
                error_mapping[index] = "Character limit exceeded, " + header_name + \
                    " length should be less than 150 characters"
                if header_name not in error_present_headers:
                    error_present_headers.append(header_name)
                continue
            if header_name == "description" and len(detail) > 9999:
                error_in_item = True
                error_mapping[index] = "Character limit exceeded, " + header_name + \
                    " length should be less than 9999 characters"
                if header_name not in error_present_headers:
                    error_present_headers.append(header_name)
                continue
            if header_name in ["retailer_id", "category", "fb_product_category", "retailer_product_group_id", "color", "material", "pattern"] and len(detail) > 100:
                error_in_item = True
                error_mapping[index] = "Character limit exceeded, " + header_name + \
                    " length should be less than 100 characters"
                if header_name not in error_present_headers:
                    error_present_headers.append(header_name)
                continue
            if header_name == "url" or header_name == "image_url":
                if not validation_obj.is_valid_url(detail):
                    error_in_item = True
                    error_mapping[index] = "Invalid input type, " + header_name + \
                        " needs to be a valid URL"
                    if header_name not in error_present_headers:
                        error_present_headers.append(header_name)
                    continue
            if header_name == "price" or header_name == "sale_price":
                if header_name == "sale_price" and detail == "":
                    continue
                if not validation_obj.is_numeric(detail):
                    error_in_item = True
                    error_mapping[index] = "Invalid input type, " + header_name + \
                        " needs to be a number"
                    if header_name not in error_present_headers:
                        error_present_headers.append(header_name)
                    continue
                elif float(detail) <= 0:
                    error_in_item = True
                    error_mapping[index] = "Invalid input type, " + header_name + \
                        " needs to be greater than 0"
                    if header_name not in error_present_headers:
                        error_present_headers.append(header_name)
                    continue
            if header_name in ["condition", "gender", "availability"]:
                detail = detail.lower()
            if header_name == "availability":
                detail = item_availability_mapping(detail, space_removing_pattern)
                if not detail:
                    error_in_item = True
                    error_mapping[index] = "Invalid input type, " + header_name + \
                        " value should be 'in stock', 'out of stock', 'available for order', 'preorder' or 'discontinued'"
                    if header_name not in error_present_headers:
                        error_present_headers.append(header_name)
                    continue
            if header_name == "condition":
                detail = item_condition_mapping(detail, space_removing_pattern)
                if not detail:
                    error_in_item = True
                    error_mapping[index] = "Invalid input type, " + header_name + \
                        " value should be 'new', 'refurbished', 'used(like new), 'used(good)' or 'used(fair)'"
                    if header_name not in error_present_headers:
                        error_present_headers.append(header_name)
                    continue
            if header_name == "gender":
                if detail not in ["male", "female", "unisex"]:
                    error_in_item = True
                    error_mapping[index] = "Invalid input type, " + header_name + \
                        " value should be 'male', 'female', or 'unisex'"
                    if header_name not in error_present_headers:
                        error_present_headers.append(header_name)
                    continue
            if header_name == "currency":
                detail = detail.upper()
                if detail not in CATALOGUE_SUPPORTED_CURRENCIES:
                    error_in_item = True
                    error_mapping[index] = header_name + \
                        " value should be a valid ISO 4217 currency code"
                    if header_name not in error_present_headers:
                        error_present_headers.append(header_name)
                    continue
            if header_name == "origin_country":
                detail = detail.upper()
                if detail not in CATALOGUE_COUNTRY_OPTIONS:
                    error_in_item = True
                    error_mapping[index] = header_name + \
                        " value should be a valid 2 character country code"
                    if header_name not in error_present_headers:
                        error_present_headers.append(header_name)
                    continue
            if header_name == "sale_price_start_date" or header_name == "sale_price_end_date":
                try:
                    detail = datetime.datetime.strptime(
                        detail, "%d/%m/%Y %H:%M").astimezone(TIME_ZONE).isoformat()
                except:
                    error_in_item = True
                    error_mapping[index] = header_name + \
                        " value should be in DD/MM/YYYY HH:MM Format"
                    if header_name not in error_present_headers:
                        error_present_headers.append(header_name)
                    continue

            if header_name == "additional_image_urls":
                detail = validate_additional_image_urls(detail, space_removing_pattern, validation_obj)
                if not detail:
                    error_in_item = True
                    error_mapping[index] = header_name + \
                        " should have valid comma (,) separated URLs"
                    if header_name not in error_present_headers:
                        error_present_headers.append(header_name)

            if detail != "":
                active_item[header_name] = detail
        if error_in_item or required_header_missing:
            errors_map[row] = {}
            errors_map[row]["item_details"] = item
            errors_map[row]["error_mapping"] = error_mapping
            if required_header_missing:
                errors_map[row]["error_mapping"]["-1"] = "Required header is missing"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("validate_catalogue_csv_upload_item: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return error_in_item, active_item, errors_map, error_present_headers


def upload_item_details_on_facebook(item_details, errors_map, bot_obj, access_token, catalogue_id, event_obj):
    try:
        error_dump = ""
        total_items = len(item_details)
        items_traversed = 0
        for catalogue_item in item_details:
            items_traversed += 1
            if total_items > 5:
                if items_traversed % 5 == 0:
                    event_obj.event_progress = (
                        items_traversed / total_items) * 100
                    event_obj.save(update_fields=["event_progress"])
            else:
                event_obj.event_progress = (
                    items_traversed / total_items) * 100
                event_obj.save(update_fields=["event_progress"])
            active_item = item_details[catalogue_item]
            if active_item == "error_in_item":
                continue
            active_item["access_token"] = access_token
            active_item = get_item_price_after_offset(active_item)
            facebook_api = FACEBOOK_GRAPH_BASE_URL + catalogue_id + "/products/"
            try:
                facebook_api_request = requests.post(
                    facebook_api, json=active_item, timeout=20, verify=True)

                if facebook_api_request.status_code != 200:
                    error_dump += "Error in row " + \
                        str(catalogue_item) + ": " + facebook_api_request.text + " \n"

                    facebook_api_response = json.loads(
                        facebook_api_request.text)
                    errors_map[catalogue_item] = {}
                    errors_map[catalogue_item]["item_details"] = active_item
                    errors_map[catalogue_item]["error_from_facebook"] = "Failed to upload this item, please make sure all the details are valid"

                    if "error" in facebook_api_response and "message" in facebook_api_response["error"]:
                        errors_map[catalogue_item]["error_from_facebook"] = facebook_api_response["error"]["message"]
                        if "error_user_msg" in facebook_api_response["error"]:
                            errors_map[catalogue_item]["error_from_facebook"] = facebook_api_response["error"]["message"] + \
                                " " + \
                                facebook_api_response["error"]["error_user_msg"]
            except requests.Timeout as RT:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Create CatalogueProductsAPI Timeout error: %s", str(RT), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                errors_map[catalogue_item]["error_from_facebook"] = "Request for creating this Catalogue Item Timed Out."
        if error_dump:
            check_and_send_broken_bot_mail(
                bot_obj.pk, "Web", "", error_dump)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("upload_item_details_on_facebook: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return errors_map


def item_condition_mapping(condition, space_removing_pattern):
    try:
        condition = re.sub(space_removing_pattern, '', condition)
        if condition in ["new", "refurbished"]:
            return condition
        if condition == "used(likenew)":
            return "used_like_new"
        if condition == "used(good)":
            return "used_good"
        if condition == "used(fair)":
            return "used_fair"
        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("item_condition_mapping: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
        return "new"


def item_availability_mapping(availability, space_removing_pattern):
    try:
        availability = re.sub(space_removing_pattern, '', availability)
        if availability == "instock":
            return "in stock"
        if availability == "outofstock":
            return "out of stock"
        if availability == "availablefororder":
            return "available for order"
        if availability == "preorder":
            return "preorder"
        if availability == "discontinued":
            return "discontinued"
        return False

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("item_availability_mapping: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
        return "in stock"


def validate_additional_image_urls(additional_urls, space_removing_pattern, validation_obj):
    try:
        additional_urls = re.sub(space_removing_pattern, '', additional_urls)
        additional_urls_list = additional_urls.split(",")
        for url in additional_urls_list:
            if not validation_obj.is_valid_url(url):
                return False
        return additional_urls_list

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("validate_additional_image_urls: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
    return False


def get_item_price_after_offset(item):
    try:
        if item["currency"] not in OFFSET_1_CURRENCIES:
            item["price"] = int(float(item["price"]) * 100)
            if "sale_price" in item:
                item["sale_price"] = int(
                    float(item["sale_price"]) * 100)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_item_price_after_offset: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return item
