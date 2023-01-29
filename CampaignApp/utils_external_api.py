import uuid
import sys
import re
from django.conf import settings
from xlwt import Workbook
import threading
import func_timeout
import operator
from functools import reduce
from django.db.models import Q

from CampaignApp.html_parser import strip_html_tags
from CampaignApp.constants import *
from CampaignApp.models import *
from EasyChatApp.models import Profile
from CampaignApp.utils import *
from CampaignApp.utils_export import *

import json
from CampaignApp.utils_custom_encryption import *
from CampaignApp.utils_parse import *
from EasyChatApp.utils_validation import EasyChatInputValidation
from CampaignApp.utils_validation import CampaignInputValidation
from CampaignApp.utils_campaign_rcs import *
from datetime import datetime
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses


# Logger
import logging
logger = logging.getLogger(__name__)
validation_obj = CampaignInputValidation()
easychat_validation_obj = EasyChatInputValidation()
masking_enabled = False


def add_template_external_api(data, bot_obj):
    
    campaign_template_obj = None
    try:
        template_type = ""
        template_language = ""
        template_name = "",
        template_category = "",
        template_message_body = "",
        template_message_header = ""
        template_message_footer = ""
        template_attachment_url = ""

        if "template_variables" not in data:
            return 400, "Please specify template variables", None
        else:
            template_variables = data["template_variables"]
        
        if "template_name" not in template_variables:
            return 400, "Please specify template name", None
        else:
            try:
                template_name = template_variables["template_name"]
                template_name = str(template_name).lower().strip()
                template_name = remo_html_from_string(template_name)
                template_name = remo_special_tag_from_string(template_name)
                template_language = template_variables["language"]
                template_language = str(template_language).lower().strip()
                template_language = remo_html_from_string(template_language)
                template_language = remo_special_tag_from_string(template_language)
                if template_name == "" or template_language == "":
                    return 400, "Template Name, Language can't be empty", None
            except:
                return 400, "Please specify a valid template name, language", None

            language_obj = CampaignTemplateLanguage.objects.filter(
                title=template_language).first()

            if not language_obj:
                language_obj = CampaignTemplateLanguage.objects.create(
                    title=template_language)

            campaign_template_obj = CampaignTemplate.objects.filter(
                template_name=template_name, language=language_obj, is_deleted=False, bot=bot_obj).first()

            if campaign_template_obj:
                return 202, f"Campaign created successfully but not able to upload this template because Template Name '{template_name.capitalize()}' for the '{language_obj.title.capitalize()}' Language already exists.", campaign_template_obj

        try:
            template_type = template_variables["type"]
            template_category = template_variables["category"]
            template_message_body = template_variables["message_body_template"]
            
            template_category = str(template_category).lower().strip()
            template_type = str(template_type).lower().strip()  

            template_type = remo_html_from_string(template_type)
            template_category = remo_html_from_string(template_category)
            template_message_body = remo_html_from_string(template_message_body) 
            template_category = remo_special_tag_from_string(template_category)
            template_type = remo_special_tag_from_string(template_type)

            if template_type == "" or template_category == "" or template_message_body == "":
                return 400, "Type, Category and Message Body Template can't be empty!", None
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("In add_template_external_api: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'Campaign'})
            return 400, "Type, Language, Category and Message Body Template should be as per the standards!", None
        
        error_message = validation_on_template_variables(template_variables, template_type)
        
        if error_message:
            return 400, error_message, None

        template_message_header, template_message_footer, template_cta_button_text, template_cta_button_link, template_attachment_url, template_metadata = initialize_optional_variables(template_variables)

        if not check_url_valid(template_attachment_url) and template_type.lower().strip() != "text":
            template_attachment_url = ""
            return 400, "Please enter a valid template attachment url!", None

        if not check_url_valid(template_cta_button_link) and template_type.lower().strip() != "text":
            template_cta_button_link = ""

        campaign_template_obj = CampaignTemplate.objects.create(
            template_name=template_name,
            template_header=template_message_header,
            template_body=template_message_body,
            template_footer=template_message_footer,
            cta_text=template_cta_button_text,
            cta_link=template_cta_button_link,
            attachment_src=template_attachment_url,
            template_metadata=template_metadata)

        category_obj = CampaignTemplateCategory.objects.filter(
            title=template_category).first()
        if category_obj is None:
            category_obj = CampaignTemplateCategory.objects.create(
                title=template_category)

        template_type_obj = CampaignTemplateType.objects.filter(
            title=template_type).first()
        if template_type_obj is None:
            template_type_obj = CampaignTemplateType.objects.create(
                title=template_type)

        template_status_obj = CampaignTemplateStatus.objects.filter(
            title="approved").first()
        campaign_template_obj.language = language_obj
        campaign_template_obj.category = category_obj
        campaign_template_obj.status = template_status_obj
        campaign_template_obj.template_type = template_type_obj
        campaign_template_obj.bot = bot_obj
        campaign_template_obj.save(update_fields=["language", "category", "status", "template_type", "bot"])
        return 200, "Template created successfully", campaign_template_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In add_template_external_api: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return 400, "Not able to create template. Make sure the inputs are as per the standards.", None


def add_template_external_api_voicebot(data, bot_obj, campaign_name, channel_obj):
    
    try:
        campaign_obj = None
        validation_obj = EasyChatInputValidation()
        caller_id = data['caller_id']
        caller_id = clean_input(caller_id)

        start_date = data['start_date']
        start_date = datetime.strptime(
            start_date, DATE_FORMAT).date()

        end_date = data['end_date']
        end_date = datetime.strptime(
            end_date, DATE_FORMAT).date()

        start_time = data['start_time']
        start_time = datetime.strptime(
            start_time, TIME_FORMAT)

        end_time = data['end_time']
        end_time = datetime.strptime(
            end_time, TIME_FORMAT)

        error_occured = False
        error_text = ""

        status, message = check_and_validate_date_for_voicebot(start_date, start_time, end_date, end_time)

        if status == 400:
            error_occured = True
            error_text = message

        retry_mechanism = data['retry_mechanism']
        no_of_retries = data['no_of_retries']
        retry_interval = data['retry_interval']
        is_busy_enabled = data['is_busy_enabled']
        is_no_answer_enabled = data['is_no_answer_enabled']
        is_failed_enabled = data['is_failed_enabled']

        if not caller_id.isnumeric() or not validation_obj.validate_phone_number(caller_id):
            error_occured = True
            error_text = "Caller id should be a vaild number."

        elif retry_mechanism.lower() not in ["linear", "exponential"]:
            error_occured = True
            error_text = "Retry mechanism should be either linear or exponential."
        elif no_of_retries not in ["1", "2", "3"]:
            error_occured = True
            error_text = "Number of retries should be in range 1 - 3."
        
        elif not retry_interval.isnumeric():
            error_occured = True
            error_text = "Retry interval should be a valid number."
        
        elif not isinstance(is_busy_enabled, (bool)):
            error_occured = True
            error_text = "Call status should be either true or false."
        
        elif not isinstance(is_no_answer_enabled, (bool)):
            error_occured = True
            error_text = "Call status should be either true or false."
        
        elif not isinstance(is_no_answer_enabled, (bool)):
            error_occured = True
            error_text = "Call status should be either true or false."
        
        if error_occured:
            return 400, error_text, None

        campaign_obj = Campaign.objects.create(
            name=campaign_name,
            channel=channel_obj,
            bot=bot_obj,
            status=CAMPAIGN_DRAFT
        )

        trigger_setting_obj = CampaignVoiceBotSetting.objects.filter(
            campaign=campaign_obj)

        if trigger_setting_obj.exists():
            return 400, "This campaign is already created.", campaign_obj

        trigger_setting_obj = CampaignVoiceBotSetting.objects.create(
            campaign=campaign_obj)

        retry_setting = VoiceBotRetrySetting.objects.create()

        trigger_setting_obj.retry_setting = retry_setting
        trigger_setting_obj.save()

        if trigger_setting_obj:

            trigger_setting_obj.caller_id = caller_id
            trigger_setting_obj.start_date = start_date
            trigger_setting_obj.end_date = end_date
            trigger_setting_obj.start_time = start_time
            trigger_setting_obj.end_time = end_time

            app_id = get_app_id_from_caller_id(caller_id, VoiceBotCallerID)

            trigger_setting_obj.app_id = app_id
            trigger_setting_obj.is_saved = True
            trigger_setting_obj.save()

            retry_setting = trigger_setting_obj.retry_setting

            retry_setting.mechanism = retry_mechanism
            retry_setting.no_of_retries = no_of_retries
            retry_setting.retry_interval = retry_interval
            retry_setting.is_busy_enabled = is_busy_enabled
            retry_setting.is_no_answer_enabled = is_no_answer_enabled
            retry_setting.is_failed_enabled = is_failed_enabled
            retry_setting.save()

            campaign_obj.last_saved_state = CAMPAIGN_SETTINGS_STATE
            campaign_obj.save()
            return 200, "Campaign created successfully with settings.", campaign_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In add_template_external_api_voicebot: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return 400, "Not able to create template. Make sure the inputs are as per the standards.", campaign_obj


def add_template_external_api_rcs(data, bot_obj):
    
    try:
        if "template_variables" not in data:
            return 400, "Please specify template variables", None
        else:
            template_variables = data["template_variables"]
        
        data = template_variables

        template_name = data["template_name"].strip()
        message_type = data["message_type"]
        update_template = False
        validation_obj = EasyChatInputValidation()
        response = {}
        response["status"] = 500
        if template_name == "":
            response["status"] = 400
            response["message"] = "Template name cannot be empty!"
        
        template_name = validation_obj.remo_complete_html_and_special_tags(template_name)

        template_obj = CampaignRCSTemplate.objects.filter(
            bot=bot_obj, template_name=template_name, is_deleted=False)

        if template_obj.exists() and update_template == False:
            response["status"] = 400
            response["message"] = "Template with same name already exists!"

        if str(message_type).strip() == "":
            response["status"] = 400
            response["message"] = "Please select a valid template type!"

        if response["status"] == 400:
            return 400, response["message"], None

        if message_type == 1:
            text_message = str(data["text_message"]).strip()
            if text_message == "":
                response["status"] = 400
                response["message"] = "Message text cannot be empty!"

        elif message_type == 2:
            media_url = data["media_url"]
            if not validation_obj.is_valid_url(media_url):
                response["status"] = 400
                response["message"] = "Please enter a valid media URL!"

        elif message_type == 3:
            error_message = validate_rich_and_carousel_cards(
                data, validation_obj)
            if error_message is not None:
                response["status"] = 400
                response["message"] = error_message

        elif message_type == 4:
            carousel_cards = data["carousel_cards"]
            if len(carousel_cards) < 2:
                response["status"] = 400
                response["message"] = "Minimum 2 cards are required in Carousel else use the Rich Card for adding a single card."
            elif len(carousel_cards) > 10:
                response["status"] = 400
                response["message"] = "Maximum 10 Carousel Cards are supported!"
            else:
                for carousel_card in carousel_cards:
                    error_message = validate_rich_and_carousel_cards(
                        carousel_card, validation_obj)
                    if error_message is not None:
                        response["status"] = 400
                        response["message"] = error_message
                        break
        else:
            return 400, "Message type can only be in range 1 - 4.", None

        suggested_reply = data.get("suggested_reply", [])
        if response["status"] != 400 and len(suggested_reply) > 0:
            error_message = validate_suggested_reply(
                suggested_reply, validation_obj)
            if error_message is not None:
                response["status"] = 400
                response["message"] = error_message

        if response["status"] == 400:
            return response["status"], response["message"], None

        rcs_template_obj = save_rcs_campaign_template_external(bot_obj, data, template_name)
        response["status"] = 200
        response["message"] = "Campaign RCS template is saved successfully."

        return response["status"], response["message"], rcs_template_obj

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In add_template_external_api_rcs: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return 400, "Not able to create template. Make sure the inputs are as per the standards.", None


def validate_dynamic_attachment_details(media_send_type):
    try:
        if media_send_type != None and (not media_send_type.strip() or media_send_type.strip() not in ['static', 'dynamic']):
            return 400, "The provided media_type is not valid, please select from the 2 expected categories that are 'Static' or 'Dynamic' based on the requirement. Select Static if you want to send the same media file to all the users or select Dynamic if you want to send a different media file to each user."
        return 200, "Validation checks completed"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In validate_dynamic_attachment_details: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return 400, "Something went wrong while validating your data"


def add_batch_external_api_and_send_message(data, bot_obj, username, campaign_obj):
    
    message = "Couldn't send message successfully"
    status = 500
    campaign_batch_obj = None
    try:
        rcs_enabled_user_list = []
        phone_numbers = []
        auto_delete_invalid_number = data.get("auto_delete_invalid_number", False)
        deleted_rows_count = 0

        if "batch_name" in data:
            batch_name = data["batch_name"]
            batch_name = batch_name.strip()
            batch_name = remo_html_from_string(batch_name)
            batch_name = remo_special_tag_from_string(batch_name)
            if bool(re.match('^[\W_ ]+$', batch_name)):
                return 400, "Batch name can't contain only special characters.", []

        else:
            return 400, "Make sure batch name is specified!", []

        if batch_name == "":
            return 400, "Batch name can't be empty!", []

        clients_data = data.get("client_data", [])

        total_opted_in = 0
        total_batch_count = len(clients_data)
        whatsapp_bsp = data.get("whatsapp_bsp", "1")

        if campaign_obj.channel.value == "rcs":
            rcs_enabled_users_found, rcs_enabled_user_list, invalid_phone_number_index, error_message, deleted_rows_count = check_rcs_enabled_users_external(
                bot_obj, clients_data, total_batch_count, auto_delete_invalid_number)
            total_batch_count -= deleted_rows_count
            if not rcs_enabled_users_found:
                if invalid_phone_number_index == -1:
                    return 400, "Unable to upload batch, please make sure the rcs credentials are setup and at least one valid phone number with rcs enabled is provided.", rcs_enabled_user_list
                elif error_message:
                    return 400, error_message, rcs_enabled_user_list
                else:
                    return 400, "Unable to upload batch, please check the phone number at position " + str(invalid_phone_number_index), rcs_enabled_user_list
            else:
                if len(rcs_enabled_user_list) == 0:
                    return 400, "Unable to upload batch, please make sure the rcs credentials are setup and at least one valid phone number with rcs enabled is provided.", rcs_enabled_user_list

            total_opted_in = len(rcs_enabled_user_list)
        elif campaign_obj.channel.value == "whatsapp" or campaign_obj.channel.value == "voicebot":
            if campaign_obj.channel.value == "whatsapp" and not whatsapp_bsp.isdigit():
                return 400, "Please enter a valid bot bsp", []
            
            if campaign_obj.campaign_template.template_type.title != 'text':
                status_code, status_message = validate_dynamic_attachment_details(data.get('media_send_type'))
                if status_code == 400:
                    return status_code, status_message, []
            idx = 0
            while idx < total_batch_count:
                phone_number = ""
                name = ""
                try:
                    client = clients_data[idx]
                    phone_number = client["phone_number"]
                    phone_number = validation_obj.removing_phone_non_digit_element(
                        phone_number)
                    phone_number = remo_html_from_string(str(phone_number))
                    name = client["name"]
                    if campaign_obj.channel.value == "whatsapp":
                        if phone_number[0] != '+':
                            phone_number = '+' + phone_number
                        if not validate_mobile_number_with_country_code(phone_number):
                            if auto_delete_invalid_number:
                                deleted_rows_count += 1
                                clients_data.pop(idx)
                                total_batch_count -= 1
                                continue
                            return 400, "Invalid phone number in clients data at position " + str(idx + 1), []
                    if campaign_obj.channel.value == "voicebot":
                        if not easychat_validation_obj.validate_phone_number(phone_number):
                            if auto_delete_invalid_number:
                                deleted_rows_count += 1
                                clients_data.pop(idx)
                                total_batch_count -= 1
                                continue
                            return 400, "Invalid phone number in clients data at position " + str(idx + 1), []

                    phone_number = remo_special_tag_from_string(phone_number)
                    phone_number = phone_number.strip()
                    name = remo_html_from_string(str(name))
                    name = remo_special_tag_from_string(name)
                    name = name.strip()

                    if name == "":
                        return 400, "Invalid name in clients data at position " + str(idx + 1), []

                    if phone_number == "":
                        if auto_delete_invalid_number:
                            deleted_rows_count += 1
                            clients_data.pop(idx)
                            total_batch_count -= 1
                            continue
                        return 400, "Invalid phone number in clients data at position " + str(idx + 1), []

                    phone_numbers.append(str(int(phone_number)))
                    idx += 1

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("In add_batch_external_api: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                        'AppName': 'Campaign'})
                    return 400, "Phone number or name is empty or not defined in some entry of the client data", []

            if not phone_numbers:
                return 400, "Unable to upload the file as the auto delete toggle was true and all the invalid numbers were deleted from the file. Please make sure to add atleast one valid phone number.", []

            if campaign_obj.channel.value == "voicebot":
                campaign_obj.total_audience = total_batch_count
                campaign_obj.save()

            total_opted_in = Profile.objects.filter(
                user_id__in=phone_numbers, campaign_optin=True).count()

        status, message, campaign_batch_obj = save_batch_data(
            total_batch_count, total_opted_in, username, bot_obj, batch_name, campaign_obj.channel)

        if campaign_batch_obj == None:
            return status, message, rcs_enabled_user_list
        else:
            status, message = send_external_campaign_message(str(
                campaign_obj.pk), campaign_batch_obj, data, rcs_enabled_user_list, whatsapp_bsp, phone_numbers)
            if auto_delete_invalid_number and status == 200:
                return status, message + " Note: As the auto delete invalid number was set to True, " + str(deleted_rows_count) + " invalid phone number(s) have been deleted.", rcs_enabled_user_list
            else:
                return status, message, rcs_enabled_user_list

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In add_batch_external_api: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return 400, "Not able to send message successfully. Please try again", rcs_enabled_user_list


def send_external_campaign_message(campaign_id, campaign_batch_obj, data, rcs_enabled_user_list, whatsapp_bsp, phone_numbers):
    try:
        campaign_obj = Campaign.objects.filter(pk=int(campaign_id)).first()
        if not campaign_obj:
            return 400, "Campaign doesn't exists for the given id."

        campaign_api = CampaignAPI.objects.filter(
            campaign=campaign_obj)

        channel_value = campaign_obj.channel.value
        if not campaign_api or not campaign_api[0].is_api_completed:
            return 400, "Send Campaign failed because API Integration is pending."
        else:
            if channel_value == "whatsapp":
                campaign_api = campaign_api[0]
                wsp_obj = CampaignWhatsAppServiceProvider.objects.filter(name=whatsapp_bsp).first()  # this is value code for bsp used, defaults to 1(Ameyo)
                if not wsp_obj:
                    return 400, "Whatsapp BSP doesn't exists for value " + whatsapp_bsp    
                bot_wsp_obj = CampaignBotWSPConfig.objects.filter(bot=campaign_obj.bot, whatsapp_service_provider=wsp_obj).first()
                if not bot_wsp_obj:
                    
                    bot_wsp_obj = CampaignBotWSPConfig.objects.create(bot=campaign_obj.bot, whatsapp_service_provider=wsp_obj) 
                    file_obj = open(wsp_obj.default_code_file_path, "r")
                    code = file_obj.read()
                    file_obj.close()
                    bot_wsp_obj.code = code
                    bot_wsp_obj.save()              

                campaign_api.campaign_bot_wsp_config = bot_wsp_obj
                campaign_api.save()

                campaign_wsp_config_meta = {"code": bot_wsp_obj.code, "namespace": bot_wsp_obj.namespace,
                                            "enable_queuing_system": bot_wsp_obj.enable_queuing_system, "bot_wsp_id": bot_wsp_obj.pk}

                if campaign_wsp_config_meta["enable_queuing_system"]:
                    sqs_response = validate_aws_sqs_credentials(
                        bot_wsp_obj, campaign_wsp_config_meta)

                    if sqs_response == None:
                        return 404, "Unable to connect to the queueing system due to invalid credentials. Please connect with our support team to get this resolved."

            campaign_batch_obj.campaigns.add(campaign_obj)
            campaign_batch_obj.save()
            campaign_obj.batch = campaign_batch_obj
            campaign_obj.save(update_fields=["batch"])

            if channel_value == "whatsapp" and not campaign_obj.campaign_template:
                return 404, "The template related to this campaign has been removed." 
            elif channel_value == "rcs" and not campaign_obj.campaign_template_rcs:
                return 404, "The template related to this campaign has been removed." 

            if channel_value == "whatsapp":
                t1 = threading.Thread(target=execute_send_campaign_external, args=(
                    campaign_wsp_config_meta, campaign_obj, data))
            elif channel_value == "rcs":
                clients_data_dict = clients_data_build_dict(
                    data.get("client_data", []), key="phone_number")
                t1 = threading.Thread(target=execute_send_campaign_external_rcs, args=(
                    campaign_obj, rcs_enabled_user_list, clients_data_dict))
            elif channel_value == "voicebot":
                voice_bot_obj = CampaignVoiceBotSetting.objects.get(
                    campaign=campaign_obj)
                start_date = voice_bot_obj.start_date
                start_time = voice_bot_obj.start_time
                status, message = check_and_validate_date_for_voicebot_wrt_current_time(
                    start_date, start_time)
                if status == 400:
                    return 400, message

                t1 = threading.Thread(target=execute_send_campaign_external_voicebot, args=(
                    campaign_id, data.get("client_data", []), phone_numbers))

            t1.daemon = True
            t1.start()

            return 200, "Please check reports to get the updated details."

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In send_external_campaign_message: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return 400, "Error while sending campaign message"


def execute_send_campaign_external(campaign_wsp_config_meta, campaign_obj, data):
    try:
        clients_data = data.get('client_data', [])
        
        campaign_obj.is_source_dashboard = False  # False because campaign is being sent from External API
        campaign_obj.status = CAMPAIGN_IN_PROGRESS
        campaign_obj.start_datetime = datetime.now()
        campaign_obj.show_processed_datetime = True
        campaign_obj.save(update_fields=['is_source_dashboard', 'status', 'start_datetime', 'show_processed_datetime'])

        logger.info("Campaign: %s started", campaign_obj.name, extra={
            'AppName': 'Campaign'})

        campaign_batch = campaign_obj.batch
        campaign_template = campaign_obj.campaign_template

        lang_code = get_language_code(campaign_template)

        code, namespace, enable_queuing_system = campaign_wsp_config_meta[
            "code"], campaign_wsp_config_meta["namespace"], campaign_wsp_config_meta["enable_queuing_system"]
        if enable_queuing_system:
            aws_sqs, sqs_client = campaign_wsp_config_meta[
                "aws_sqs"], campaign_wsp_config_meta["sqs_client"]
            sqs_domain = f'{settings.EASYCHAT_HOST_URL}/campaign/lambda/push-message/'
            campaign_id = campaign_obj.pk

        if not CampaignAnalytics.objects.filter(campaign=campaign_obj).exists():
            CampaignAnalytics.objects.create(
                campaign=campaign_obj, total_audience=campaign_batch.total_audience)
        
        template_type = campaign_template.template_type.title

        if template_type != 'text':
            media_send_type = data.get('media_send_type', 'static').strip()
            static_media_url = data.get('media_url', '')

        template_metadata_json = json.loads(campaign_template.template_metadata)
        
        document_file_name = CAMPAIGN_DOCUMENT_FILE_NAME

        if template_type == 'document':
            document_file_name = get_document_name(template_metadata_json, data)

        api_key = get_whatsapp_api_access_token(campaign_obj.bot)
        for client in clients_data:
            phone_number = client["phone_number"]
            phone_number = validation_obj.removing_phone_non_digit_element(phone_number)
            phone_number = remo_html_from_string(str(phone_number))
            phone_number = remo_special_tag_from_string(phone_number)
            phone_number = phone_number.strip()
            
            unique_id = client.get('unique_id', '')
            if unique_id:
                unique_id = get_audience_unique_id(unique_id)
            
            variable_details, unfilled_variables = get_external_variable_details(client)
            
            dynamic_cta_url_variable_details_list = []
            dynamic_cta_url_variable_details = get_dynamic_cta_url_variable_details(client, campaign_template)

            if dynamic_cta_url_variable_details:
                dynamic_cta_url_variable_details_list.append(dynamic_cta_url_variable_details)
            if len(dynamic_cta_url_variable_details_list) == 0 and 'dynamic_cta' in client:
                unfilled_variables.add('dynamic_cta')

            header_variable_list = []
            header_variable = get_header_variable_details(client)

            if header_variable:
                header_variable_list.append(header_variable)
            if len(header_variable_list) == 0 and 'header_variable' in client:
                unfilled_variables.add('header_variable')
            
            attachment_src = campaign_template.attachment_src
            if template_type != 'text':
                attachment_data = dict()
                attachment_data['media_send_type'] = media_send_type
                attachment_data['media_url'] = static_media_url
                attachment_data['attachment_src'] = attachment_src
                attachment_src, unfilled_attachment_src = get_attachment_variable_details(attachment_data, client)
                if unfilled_attachment_src:
                    unfilled_variables.add('media_url')

            client['media_url'] = attachment_src

            audience_obj = CampaignAudience.objects.create(
                audience_id=int(phone_number), channel=campaign_obj.channel, batch=campaign_batch, record=json.dumps(client), campaign=campaign_obj, audience_unique_id=unique_id)

            if unfilled_variables:
                audience_log_obj = CampaignAudienceLog.objects.create(
                    audience=audience_obj, campaign=campaign_obj)
                unfilled_variable_failure_response(
                    unfilled_variables, audience_log_obj)
                continue

            if is_livechat_connected(phone_number, campaign_obj.bot):
                audience_log_obj = CampaignAudienceLog.objects.create(
                    audience=audience_obj, campaign=campaign_obj)
                livechat_active_session_failure_response(audience_log_obj)
                continue

            if template_type == 'document' and media_send_type == 'dynamic':
                document_file_name = client.get('document_filename', '').strip()
                if not document_file_name:
                    document_file_name = get_document_name(template_metadata_json, data)

            parameter = {
                'mobile_number': phone_number,
                'template': {
                    'name': campaign_template.template_name,
                    'type': template_type,
                    'language': lang_code,
                    'link': attachment_src,
                    'cta_text': campaign_template.cta_text,
                    'cta_link': campaign_template.cta_link,
                },
                'user_details': [],
                'variables': variable_details,
                'header_variable': header_variable_list,
                'dynamic_cta_url_variable': dynamic_cta_url_variable_details_list,
                'type_of_first_cta_btton': template_metadata_json.get('type_of_first_cta_btton'),
                'document_file_name': document_file_name,
                'namespace': namespace,
                'api_key': api_key,
            }

            logger.info("parameter: %s", str(parameter), extra={
                'AppName': 'Campaign'})

            if enable_queuing_system:
                sqs_packet = {
                    "url": sqs_domain,
                    "campaign_id": campaign_id,
                    "bot_wsp_id": campaign_wsp_config_meta["bot_wsp_id"],
                    "audience_id": audience_obj.pk,
                    "parameter": parameter,
                    "event_name": "SEND_MESSAGE_EVENT"
                }
                send_message_into_campaign_sqs(
                    json.dumps(sqs_packet), sqs_client, aws_sqs)

            else:
                try:
                    response = func_timeout.func_timeout(
                        CAMPAIGN_APP_MAX_TIMEOUT_LIMIT, execute_bsp_code, args=[code, parameter]) 
                except func_timeout.FunctionTimedOut:
                    response = {}
                    response['response'] = {"errors": [{"code": 408, "title": "Function timed out!",
                                                        "details": "Request timed out for this entry!"}]}
                    response['request'] = parameter 

                logger.info("response: %s", str(response), extra={
                    'AppName': 'Campaign'})

                audience_log_obj = CampaignAudienceLog.objects.create(audience=audience_obj, campaign=campaign_obj)
                if response.get('response') and 'request_id' in response['response']:
                    audience_log_obj.recepient_id = response['response']['request_id']
                else:
                    audience_log_obj.is_failed = True
                
                if response.get('request') and response.get("response"):
                    audience_log_obj.request = json.dumps(response['request'])
                    audience_log_obj.response = json.dumps(response['response'])

                audience_log_obj.is_processed = True
                audience_log_obj.save(update_fields=["recepient_id", "request", "response", "is_failed", "is_processed"])
            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In execute_send_campaign_external: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})


def execute_send_campaign_external_rcs(campaign_obj, rcs_enabled_users_list, clients_data_dict):
    try:
        campaign_obj.is_source_dashboard = False  # False because campaign is being sent from External API
        logger.info("Campaign: RCS %s started", campaign_obj.name, extra={
            'AppName': 'Campaign'})

        campaign_batch = campaign_obj.batch
        campaign_template = campaign_obj.campaign_template_rcs

        if CampaignRCSDetailedAnalytics.objects.filter(campaign=campaign_obj).count() == 0:
            analytics_obj = CampaignRCSDetailedAnalytics.objects.create(
                campaign=campaign_obj,
                submitted=campaign_batch.total_audience,
                template=campaign_template,
                message_type=campaign_template.get_message_type_display(),
                bot=campaign_obj.bot)
        else:
            analytics_obj = CampaignRCSDetailedAnalytics.objects.filter(
                campaign=campaign_obj).first()

        tz = pytz.timezone(settings.TIME_ZONE)

        is_completed_successfully = True
        unsuccessful = 0
        analytics_obj.start_time = timezone.now().astimezone(tz)

        for msdin in rcs_enabled_users_list:

            unique_id = clients_data_dict.get(int(msdin)).get('unique_id')
            if unique_id:
                unique_id = get_audience_unique_id(unique_id)

            audience_obj = CampaignAudience.objects.create(
                audience_id=int(msdin), channel=campaign_obj.channel, batch=campaign_batch, record=json.dumps(msdin), campaign=campaign_obj, audience_unique_id=unique_id)

            if campaign_template.message_type == '1':
                message_text, suggestion_chip_list = parse_text_message_type(
                    json.loads(campaign_template.template_metadata))
                message_text = messages.TextMessage(message_text)

            if campaign_template.message_type == '2':
                media_url, suggestion_chip_list = parse_media_message_type(
                    json.loads(campaign_template.template_metadata))
                message_text = messages.FileMessage(media_url)

            if campaign_template.message_type == '3':
                card_content, suggestion_chip_list = parse_card_message_type(
                    json.loads(campaign_template.template_metadata))
                if card_content != {}:
                    card_title = card_content["card_title"]
                    card_media_url = card_content["card_media_url"]
                    card_description = card_content["card_description"]
                    card_reply = card_content["card_reply"]

                    card_suggetions = append_suggestion_chip_to_cluster(
                        None, card_reply, messages)

                    message_text = messages.StandaloneCard('VERTICAL',
                                                           card_title,
                                                           card_description,
                                                           card_suggetions,
                                                           card_media_url,
                                                           None,
                                                           None,
                                                           'MEDIUM')

            if campaign_template.message_type == '4':
                carousel_content, suggestion_chip_list = parse_carousel_message_type(
                    json.loads(campaign_template.template_metadata))
                cards = []
                for carousel in carousel_content:
                    card_content, _ = parse_card_message_type(carousel)
                    if card_content != {}:
                        card_title = card_content["card_title"]
                        card_media_url = card_content["card_media_url"]
                        card_description = card_content["card_description"]
                        card_reply = card_content["card_reply"]

                        card_suggetions = append_suggestion_chip_to_cluster(
                            None, card_reply, messages)
                        cards.append(messages.CardContent(card_title,
                                                          card_description,
                                                          card_media_url,
                                                          'SHORT',
                                                          card_suggetions))

                message_text = messages.CarouselCard('MEDIUM', cards)

            # Send text message to the device
            cluster = messages.MessageCluster().append_message(message_text)
            cluster = append_suggestion_chip_to_cluster(
                cluster, suggestion_chip_list, messages)

            rcs_obj = RCSDetails.objects.filter(bot=campaign_obj.bot)

            if rcs_obj.exists():
                rcs_obj = rcs_obj.first()

                service_account_location = settings.BASE_DIR + "/" + rcs_obj.rcs_credentials_file_path

                response = cluster.send_to_msisdn(
                    msdin, service_account_location)

                response = json.loads(response[1])
                
                audience_log_obj = CampaignAudienceLog.objects.create(
                    audience=audience_obj, campaign=campaign_obj)

            if 'name' in response:
                recepient_id = response["name"].split('/')[3]
                audience_log_obj.recepient_id = recepient_id
            else:
                unsuccessful += 1
                is_completed_successfully = False

            audience_log_obj.request = json.dumps({})
            audience_log_obj.response = json.dumps({})
            audience_log_obj.is_processed = True
            audience_log_obj.save()

            analytics_obj.end_time = timezone.now().astimezone(tz)
            analytics_obj.failed = unsuccessful
            analytics_obj.save()

        if is_completed_successfully:
            campaign_obj.status = CAMPAIGN_COMPLETED
        else:
            campaign_obj.status = CAMPAIGN_PARTIALLY_COMPLETED
            if unsuccessful == campaign_obj.batch.total_audience_opted:
                campaign_obj.status = CAMPAIGN_FAILED

        campaign_obj.save(update_fields=['status', 'is_source_dashboard'])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In execute_send_campaign_external_rcs: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
        
        campaign_obj.status = CAMPAIGN_PARTIALLY_COMPLETED
        campaign_obj.save(update_fields=['status', 'is_source_dashboard'])


def execute_send_campaign_external_voicebot(campaign_id, clients_data, phone_numbers):
    try:
        campaign_id = clean_input(campaign_id)

        campaign_obj = Campaign.objects.filter(pk=int(campaign_id))

        if campaign_obj:
            campaign_obj = campaign_obj.first()
            voice_bot_obj = CampaignVoiceBotSetting.objects.get(
                campaign=campaign_obj)
            campaign_obj.is_source_dashboard = False  # False because campaign is being sent from External API

            trigger_setting = parse_trigger_settings(voice_bot_obj)

            trigger_setting['campaign_id'] = campaign_id
            trigger_setting['app_id'] = voice_bot_obj.app_id
            trigger_setting['from'] = phone_numbers
            trigger_setting['name'] = campaign_obj.name
            trigger_setting['send_at_date'] = str(voice_bot_obj.start_date)
            trigger_setting['send_at_time'] = str(voice_bot_obj.start_time)
            trigger_setting['end_at_date'] = str(voice_bot_obj.end_date)
            trigger_setting['end_at_time'] = str(voice_bot_obj.end_time)
            trigger_setting['call_status_callback'] = f'{settings.EASYCHAT_HOST_URL}/campaign/call-end-call-back/'
            trigger_setting['status_callback'] = f'{settings.EASYCHAT_HOST_URL}/campaign/campaign-end-call-back/'
            trigger_setting['bot_id'] = str(campaign_obj.bot.pk)

            api_obj = check_and_create_voice_bot_api_obj(
                campaign_obj, CampaignVoiceBotAPI)
            api_code = api_obj.api_code

            processor_check_dictionary = {'open': open_file}

            exec(str(api_code), processor_check_dictionary)

            if voice_bot_obj.campaign_sid and voice_bot_obj.campaign_sid != '':
                trigger_setting['campaign_sid'] = voice_bot_obj.campaign_sid
                json_data = processor_check_dictionary['update_campaign'](
                    json.dumps(trigger_setting))
            else:
                json_data = processor_check_dictionary['create_campaign'](
                    json.dumps(trigger_setting))

            request_body = json_data['request']
            response_body = json_data['response']
            clients_data_dict = clients_data_build_dict(clients_data, key="phone_number")
            request_body['clients_data_dict'] = clients_data_dict
           
            voice_bot_obj.request = json.dumps(request_body)
            voice_bot_obj.response = response_body
            voice_bot_obj.url = request_body['campaigns'][0]['url']
            voice_bot_obj.save()

            if response_body['response'][0]['code'] == 200:
                campaign_obj.status = CAMPAIGN_SCHEDULED
                voice_bot_obj.campaign_sid = response_body['response'][0]['data']['id']
                campaign_obj.save(update_fields=['status', 'is_source_dashboard'])
                voice_bot_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In execute_send_campaign_external_voicebot: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
        
        campaign_obj.status = CAMPAIGN_PARTIALLY_COMPLETED
        campaign_obj.save(update_fields=['status', 'is_source_dashboard'])


def execute_bsp_code(code_to_execute, parameter):
    response = None
    try:
        processor_check_dictionary = {'open': open_file}
        exec(str(code_to_execute), processor_check_dictionary)
        response = processor_check_dictionary['f'](json.dumps(parameter))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("execute_bsp_code %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return response


def get_external_variable_details(client):
    try:
        dynamic_data = client.get("dynamic_data", "")
        
        variable_details = []
        unfilled_variables = set()
        if dynamic_data != "":
            for key, value in dynamic_data.items():
                if not value:
                    unfilled_variables.add(key)
                else:
                    variable_details.append(value)        
        return variable_details, unfilled_variables
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_external_variable_details Failed: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
        
        return [], set()


def save_batch_data(total_batch_count, total_opted_in, username, bot_obj, batch_name, channel_obj):
    try:
        batch_header_meta = []
        sample_data = []
        total_audience = total_batch_count
        total_opted_in = total_opted_in
        file_path = ""
        file_name = ""
        if username not in bot_obj.users.all():
            return 401, "You are not authorised to upload campaign batch for this bot.!", None
        
        else:

            campaign_batch_obj = CampaignBatch.objects.filter(batch_name=batch_name, bot=bot_obj)
            if campaign_batch_obj:
                return 409, "A batch with same batch name already exists. Please use different batch name.", None
            else:
                try:
                    campaign_batch_obj = CampaignBatch.objects.create(batch_name=batch_name)
                    campaign_batch_obj.batch_header_meta = json.dumps(batch_header_meta)
                    campaign_batch_obj.sample_data = json.dumps(sample_data)
                    campaign_batch_obj.total_audience = total_audience
                    campaign_batch_obj.total_audience_opted = total_opted_in
                    campaign_batch_obj.file_path = file_path
                    campaign_batch_obj.file_name = file_name
                    campaign_batch_obj.bot = bot_obj
                    campaign_batch_obj.channel = channel_obj
                    campaign_batch_obj.save()
                    return 200, "batch created successfully", campaign_batch_obj
                except:
                    return 400, "couldn't create batch successfully", None
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In save_batch_data: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})


def validation_on_template_variables(template_variables, template_type):
    try:
        template_message_header = template_variables.get('message_header_template', '').strip()
        template_cta_button_link = template_variables.get('website_url', '').strip()
        template_callus_text = template_variables.get("call_us_button_text", '').strip()
        template_callus_number = template_variables.get("phone_number", '').strip()
        template_cta_button_text = template_variables.get('website_button_text', '').strip()
        template_qr_1 = template_variables.get("quick_reply_1", '').strip()
        template_qr_2 = template_variables.get("quick_reply_2", '').strip()
        template_qr_3 = template_variables.get("quick_reply_3", '').strip()
        template_button_type = template_variables.get('button_type', '').strip().lower()
        type_of_first_cta_button = template_variables.get("type_of_first_cta_button", '').strip().lower()
        template_attachment_url = template_variables.get('attachment_url', '').strip()
        document_file_name = template_variables.get('document_file_name', '').strip()
        
        if template_type == 'text':
            if template_attachment_url != '':
                return "Selected type 'Text' does not expect an URL in the attachment_url field."
            if len(template_message_header.replace('{{1}}', '_')) > 60:
                return "message_header_template cannot be greater than 60"
        if (template_type == 'document' or template_type == 'image' or template_type == 'video'):
            if template_attachment_url == '' or template_attachment_url == None:
                return "Expect an URL in the attachment_url field."
            if template_message_header:
                return f"{template_type} should not have any data in message_header_template field."
            if template_type == "document":
                if len(document_file_name) > 100:
                    return "The 'Document File Name' can't be greater than 100 characters."
                if document_file_name.strip() and not validation_obj.is_filename_alphanumeric(document_file_name):
                    return "Make sure that the 'Document File Name' must have atleast one alphanumeric character and only special characters ['&', '@', '-'] are used in addition to alphanumerics(if required)."

        if template_attachment_url and not validation_obj.is_valid_url(template_attachment_url):
            return 'Please enter valid URL in attachment_url'
        if template_button_type and template_button_type not in ['quick_reply', 'cta', 'none']:
            return "button_type allows only quick_reply, cta, none"
        if type_of_first_cta_button and type_of_first_cta_button not in ['call_us', 'website_link', 'none']:
            return "type_of_first_cta_button allows only call_us, website_link, none"
        
        # Validation for button type is selected quick_reply
        if template_button_type == 'quick_reply': 
            if template_qr_1 and len(template_qr_1) > 25:
                return "Quick Reply 1 cannot be greater than 25."
            if template_qr_2 and len(template_qr_2) > 25:
                return "Quick Reply 2 cannot be greater than 25."
            if template_qr_3 and len(template_qr_3) > 25:
                return "Quick Reply 3 cannot be greater than 25."
            if template_qr_1 == '' and template_qr_2 == '' and template_qr_3 == '':
                return "Selected button type 'Quick Reply' expects Text values in quick_reply_1 or quick_reply_2 or quick_reply_3."
        
        # Validation for button type is selected cta
        if template_button_type == 'cta': 
            if template_callus_text and len(template_callus_text) > 25:
                return "Call Us Button Text length cannot be greater than 25."
            if template_cta_button_text and len(template_cta_button_text) > 25:
                return "Website Button Text length cannot be greater than 25."
            if template_cta_button_link:
                if ('{{1}}' in template_cta_button_link and len(template_cta_button_link) - 5 > 2000) or len(template_cta_button_link) > 2000:
                    return "Websit URL length cannot be greater than 2000."
                if '{{1}}' in template_cta_button_link and not validation_obj.is_valid_url(template_cta_button_link[:-5]):
                    return "Please enter valid URL in website_url"
                elif '{{1}}' not in template_cta_button_link and not validation_obj.is_valid_url(template_cta_button_link):
                    return "Please enter valid URL in website_url"
            if template_callus_number and len(template_callus_number) > 20:
                return "Phone Number length cannot be greater than 20."
            if (template_callus_number and not template_callus_text) or (not template_callus_number and template_callus_text):
                return "Please fill both call_us_button_text and phone_number if you are using call_us."
            if (template_cta_button_link and not template_cta_button_text) or (not template_cta_button_link and template_cta_button_text):
                return "Please fill both website_button_text and website_url if you are using website_cta."
            if template_callus_number:
                if not validate_mobile_number_with_country_code(template_callus_number):
                    return 'Invalid phone number in phone_number'
            if not ((template_cta_button_link and template_cta_button_text) or (template_callus_text and template_callus_number)):
                return "Selected button type 'CTA' expects values in website_url or phone_number."
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in  validation_on_template_variables: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
    return None


def initialize_optional_variables(template_variables):
    template_metadata = {}
    template_message_header = template_variables.get('message_header_template', '').strip()
    template_message_footer = template_variables.get('message_footer_template', '').strip()
    template_attachment_url = template_variables.get('attachment_url', '').strip()
    template_button_type = template_variables.get('button_type', '')
    document_file_name = template_variables.get('document_file_name', '').strip()
    template_qr_1 = template_qr_2 = template_qr_3 = None
    template_cta_button_link = template_callus_text = template_callus_number = type_of_first_cta_button = template_cta_button_text = None

    if template_message_header:
        template_message_header = remo_html_from_string(template_message_header)

    if template_message_footer:
        template_message_footer = remo_html_from_string(template_message_footer)

    if template_attachment_url:
        template_attachment_url = remo_html_from_string(template_attachment_url)
    
    if template_button_type:
        template_button_type = remo_html_from_string(template_button_type)
        template_button_type = template_button_type.strip().lower()
    
    if template_button_type == 'cta':
        template_cta_button_link = template_variables.get('website_url', '').strip()
        template_callus_text = template_variables.get("call_us_button_text", '').strip()
        template_callus_number = template_variables.get("phone_number", '').strip()
        type_of_first_cta_button = template_variables.get("type_of_first_cta_button", '').strip()
        template_cta_button_text = template_variables.get('website_button_text', '').strip()
        if template_cta_button_text:
            template_cta_button_text = remo_html_from_string(template_cta_button_text)
        if type_of_first_cta_button:         
            type_of_first_cta_button = remo_html_from_string(type_of_first_cta_button)
        if template_cta_button_link:
            template_cta_button_link = remo_html_from_string(template_cta_button_link)
        if template_callus_text:
            template_callus_text = remo_html_from_string(template_callus_text)
        if template_callus_number:
            template_callus_number = remo_html_from_string(template_callus_number)
    elif template_button_type == 'quick_reply':
        template_qr_1 = template_variables.get("quick_reply_1", '').strip()
        template_qr_2 = template_variables.get("quick_reply_2", '').strip()
        template_qr_3 = template_variables.get("quick_reply_3", '').strip()
        if template_qr_1:
            template_qr_1 = remo_html_from_string(template_qr_1)
        if template_qr_2:
            template_qr_2 = remo_html_from_string(template_qr_2)
        if template_qr_3:
            template_qr_3 = remo_html_from_string(template_qr_3)
    else:
        template_button_type = None
        template_callus_text = None
        template_callus_number = None
        template_qr_1 = None
        template_qr_2 = None
        template_qr_3 = None
        type_of_first_cta_button = None
        template_cta_button_text = None
        template_cta_button_link = None

    template_metadata['button_type'] = template_button_type
    template_metadata['callus_text'] = template_callus_text
    template_metadata['callus_number'] = template_callus_number
    template_metadata['template_qr_1'] = template_qr_1
    template_metadata['template_qr_2'] = template_qr_2
    template_metadata['template_qr_3'] = template_qr_3
    template_metadata['type_of_first_cta_btton'] = type_of_first_cta_button
    template_metadata['document_file_name'] = document_file_name
    template_metadata = json.dumps(template_metadata)

    return template_message_header, template_message_footer, template_cta_button_text, template_cta_button_link, template_attachment_url, template_metadata


def get_audience_log_unique_id_filtered_data(audience_unique_id, audience_objs):
    try:
        if not isinstance(audience_unique_id, str):
            audience_unique_id = str(audience_unique_id)
        audience_unique_id = re.sub("\s*,\s*", ",", audience_unique_id).strip()
        if audience_unique_id:
            query = reduce(operator.or_, (Q(audience__audience_unique_id=id)
                           for id in audience_unique_id.split(',')))
            audience_objs = audience_objs.filter(query)
        # elif isinstance(campaign_audience_id, dict): for future scalability
        #     for unique_id in campaign_audience_id:
        #         audience_unique_id = re.sub("\s*,\s*", ",", campaign_audience_id[unique_id]).strip()
        #         query = reduce(operator.or_, (Q(audience_unique_id__contains = f'"{unique_id.strip()}": "{id}"') for id in audience_unique_id.split(',')))
        #         audience_log = audience_log.filter(query)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_audience_log_unique_id_filtered_data: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
    return audience_objs


def get_phone_number_list(phone_number):
    try:
        phone_number = re.sub("\s*,\s*", ",", phone_number).strip()
        phone_number = phone_number.split(',')
        while '' in phone_number:
            phone_number.remove('')
        return phone_number
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_phone_number_list: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
        return []


def get_audience_log_phone_number_filtered_data(phone_number, audience_objs):
    try:
        query = reduce(operator.or_, (Q(audience__audience_id=number)
                       for number in phone_number))
        audience_objs = audience_objs.filter(query)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_audience_log_phone_number_filtered_data: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
    return audience_objs


def add_campaign_details_in_reports_external(campaign_obj, users_parameter_data):
    json_obj = None
    try:
        audience_unique_id = users_parameter_data['audience_unique_id']
        phone_number = users_parameter_data['phone_number']
        campaign_analytics = CampaignAnalytics.objects.filter(
            campaign=campaign_obj)

        if not campaign_analytics.exists():
            status = 400
            message = "Campaign Analytics has not yet been generated. Please make sure that campaign is triggered atleast once."
            json_obj = {}
            return status, message, json_obj
        
        campaign_analytics = campaign_analytics.first()

        campaign_api_obj = CampaignAPI.objects.filter(
            campaign=campaign_obj).first()
        bot_wsp_obj = None
        if campaign_api_obj:
            bot_wsp_obj = campaign_api_obj.campaign_bot_wsp_config

        whatsapp_bsp_name = "-"
        if bot_wsp_obj:
            whatsapp_bsp_name = bot_wsp_obj.whatsapp_service_provider.get_name_display()

        if campaign_obj.campaign_template:
            template_type = campaign_obj.campaign_template.template_type.title if campaign_obj.campaign_template.template_type else "-"
            template_name = campaign_obj.campaign_template.template_name
        else:
            template_type = "-"
            template_name = "-"

        time_zone = settings.TIME_ZONE

        json_obj = {
            "Overall Report": {
                "bot_name": campaign_obj.bot.name,
                "campaign_name": campaign_obj.name,
                "whatsapp_bsp": whatsapp_bsp_name,
                "campaign_created_on": campaign_obj.create_datetime.astimezone(pytz.timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S"),
                "open_rate": str(campaign_analytics.open_rate()) + "%",
                "source": "Dashboard" if campaign_obj.is_source_dashboard else "External API",
                "timezone": time_zone,
                "total_message_submitted": campaign_analytics.message_processed,
                "message_sent": campaign_analytics.message_sent,
                "message_delivered": campaign_analytics.message_delivered,
                "message_read": campaign_analytics.message_read,
                "message_replied": campaign_analytics.message_replied,
                "message_failed": campaign_analytics.message_unsuccessful,
                "audience_batch_name": campaign_obj.batch.batch_name if campaign_obj.batch else "-",
                "total_audience_batch_size": campaign_obj.batch.total_audience,
                "template_name": template_name,
                "template_type": template_type
            },
            "Detailed Report": []
        }
        detailed_report = []
        if campaign_obj.status == CAMPAIGN_IN_PROGRESS:
            status = 200
            message = "Reports generated successfully"
            error_message = f'Incomplete Report: The campaign {campaign_obj.name} with Campaign ID {campaign_obj.pk} is still in progress and the reports will be available only once it is completed. Please check after some time to get the detailed report.'
            message_response = {'status_code': '409',
                                'status_message': error_message}
            detailed_report.append(message_response)
            json_obj["Detailed Report"] = detailed_report
            return status, message, json_obj

        audience_log_objs = CampaignAudienceLog.objects.filter(
            campaign=campaign_obj, is_test=False)

        if phone_number:
            phone_number = get_phone_number_list(phone_number)
            audience_log_objs = get_audience_log_phone_number_filtered_data(
                phone_number, audience_log_objs)
        if audience_unique_id:
            audience_log_objs = get_audience_log_unique_id_filtered_data(
                audience_unique_id, audience_log_objs)

        audience_log_objs = audience_log_objs.values('id', 'audience__audience_unique_id', 'audience__audience_id', 'recepient_id', 'is_sent', 'sent_datetime', 'audience__record',
                                                     'is_delivered', 'delivered_datetime', 'is_read', 'read_datetime', 'is_replied', 'replied_datetime', 'is_failed', 'request', 'response')

        total_audience = audience_log_objs.count()
        if total_audience == 0:
            audience_error = {'error_code': '409', 'error_message': f'No data found for the filtered data in the given Campaign ID {campaign_obj.pk}, please make sure you are providing the correct parameters which should be present in the above mentioned Campaign ID'}
            detailed_report.append(audience_error)

        elif total_audience <= CAMPAIGN_APP_MAX_RESPONSE_DATA_LIMIT:
            is_external_campaign_export = False if campaign_obj.is_source_dashboard else True
            for audience_log_obj in audience_log_objs.iterator():
                response_detailed_json_obj = add_audience_details_external(
                    audience_log_obj, whatsapp_bsp_name, is_external_campaign_export)
                detailed_report.append(response_detailed_json_obj)
        elif total_audience > CAMPAIGN_APP_MAX_RESPONSE_DATA_LIMIT:
            email_id = users_parameter_data['email_id']
            if not email_id:
                response_message = f'Please provide a valid email address. Since the data has exceeded {CAMPAIGN_APP_MAX_RESPONSE_DATA_LIMIT} for the provided Campaign ID, the report will be sent to the email ID provided within the next 24 hours.'
                audience_error = {'error_code': '408',
                                  'error_message': response_message}

                detailed_report.append(audience_error)
            else:
                filters_on_export = json.dumps({
                    "phone_number": phone_number,
                    "audience_unique_id": audience_unique_id
                })

                CampaignExportRequest.objects.create(
                    email_id=users_parameter_data['email_id'],
                    user=users_parameter_data['user'],
                    bot=campaign_obj.bot,
                    campaign=campaign_obj,
                    export_type='1',
                    filters_on_export=filters_on_export)
                message_response = {
                    'status_code': '200', 'message': 'You will receive the campaign report data dump on the above email ID within 24 hours.'}

                detailed_report.append(message_response)

        json_obj["Detailed Report"] = detailed_report

        status = 200
        message = "Reports generated successfully"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In add_campaign_details_in_reports_external: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
        status = 400
        message = "Error in generating reports. Please try again"
        json_obj = {}

    return status, message, json_obj


def add_campaign_details_in_reports_external_voicebot(campaign_obj, users_parameter_data):
    json_obj = None
    try:
        phone_number = users_parameter_data['phone_number']
        audience_unique_id = users_parameter_data['audience_unique_id']
        
        voice_bot_obj = CampaignVoiceBotSetting.objects.filter(
            campaign=campaign_obj).first()
        campaign_analytics = CampaignVoiceBotAnalytics.objects.filter(
            campaign=campaign_obj).first()

        if campaign_analytics == None:
            return 400, "The campaign analytics has not been updated yet", {}

        json_obj = {
            "Overall Report": {
                "Campaign Name": campaign_obj.name,
                "Audience Batch Name": campaign_obj.batch.batch_name,
                "Total Audience Batch Size": campaign_obj.batch.total_audience,
                "Call scheduled": campaign_analytics.call_scheduled,
                "Call Initiated": campaign_analytics.call_initiated,
                "Call completed": campaign_analytics.call_completed,
                "Failed": campaign_analytics.call_failed,
                "Inprogress": campaign_analytics.call_in_progress,
                "Invalid": campaign_analytics.call_invalid,
                "App ID": voice_bot_obj.app_id
            },
            "Detailed Report": []
        }

        detailed_report = []
        call_details_objs = CampaignVoiceBotDetailedAnalytics.objects.filter(
            campaign=campaign_obj)

        if phone_number:
            phone_number = get_phone_number_list(phone_number)
            if phone_number:
                query = reduce(operator.or_, (Q(from_number=number) for number in phone_number))
                call_details_objs = call_details_objs.filter(query)
        
        if audience_unique_id:
            call_details_objs = get_audience_log_unique_id_filtered_data(audience_unique_id, call_details_objs)  
        
        call_details_objs_count = call_details_objs.count()     

        if call_details_objs_count == 0:
            audience_error = {'error_code': '409', 'error_message': f'No data found for the filtered data in the given Campaign ID {campaign_obj.pk}, please make sure you are providing the correct parameters which should be present in the above mentioned Campaign ID'}
        
            detailed_report.append(audience_error)
        elif call_details_objs_count <= CAMPAIGN_APP_MAX_RESPONSE_DATA_LIMIT:
            for call_details_obj in call_details_objs.iterator():
                response_detailed_json_obj = add_audience_details_external_vb(call_details_obj, campaign_obj,)
                detailed_report.append(response_detailed_json_obj)
        elif call_details_objs_count > CAMPAIGN_APP_MAX_RESPONSE_DATA_LIMIT:
            email_id = users_parameter_data['email_id']
            if not email_id:
                response_message = f'Please provide a valid email address. Since the data has exceeded {CAMPAIGN_APP_MAX_RESPONSE_DATA_LIMIT} for the provided Campaign ID, the report will be sent to the email ID provided within the next 24 hours.'
                audience_error = {'error_code': '408', 'error_message': response_message}
            
                detailed_report.append(audience_error)
            else:
                filters_on_export = json.dumps({
                    "phone_number": phone_number,
                    "audience_unique_id": audience_unique_id
                })

                CampaignExportRequest.objects.create(
                    email_id=users_parameter_data['email_id'],
                    user=users_parameter_data['user'],
                    bot=campaign_obj.bot,
                    campaign=campaign_obj,
                    export_type='1',
                    filters_on_export=filters_on_export)
                message_response = {'status_code': '200', 'message': 'You will receive the campaign report data dump on the above email ID within 24 hours.'}
            
                detailed_report.append(message_response)

        json_obj["Detailed Report"] = detailed_report
            
        status = 200
        message = "Reports generated successfully"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In add_campaign_details_in_reports_external_voicebot: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
        status = 400
        message = "Error in generating reports. Please try again"
        json_obj = {}

    return status, message, json_obj 


def add_campaign_details_in_reports_external_rcs(campaign_obj, users_parameter_data):
    json_obj = None
    try:
        audience_unique_id = users_parameter_data['audience_unique_id']
        phone_number = users_parameter_data['phone_number']
        rcs_analytics_obj = CampaignRCSDetailedAnalytics.objects.filter(
            campaign=campaign_obj).first()

        if rcs_analytics_obj == None:
            return 400, "The campaign has not been triggered yet", {}

        json_obj = {
            "Overall Report": {
                "Campaign Name": campaign_obj.name,
                "Audience Batch Name": campaign_obj.batch.batch_name,
                "Total Audience Batch Size": rcs_analytics_obj.submitted,
                "Message Sent": rcs_analytics_obj.sent,
                "Message Delivered": rcs_analytics_obj.delivered,
                "Message Read": rcs_analytics_obj.read,
                "Failed": rcs_analytics_obj.failed,
                "Template Name": campaign_obj.campaign_template_rcs.template_name,
            },
            "Detailed Report": []
        }

        detailed_report = []
        if campaign_obj.status == CAMPAIGN_IN_PROGRESS:
            status = 200
            message = "Reports generated successfully"
            error_message = f'Incomplete Report: The campaign {campaign_obj.name} with Campaign ID {campaign_obj.pk} is still in progress and the reports will be available only once it is completed. Please check after some time to get the detailed report.'
            message_response = {'status_code': '409', 'status_message': error_message}
            detailed_report.append(message_response)
            json_obj["Detailed Report"] = detailed_report
            return status, message, json_obj 

        audience_objs = CampaignAudience.objects.filter(campaign=campaign_obj)
        if phone_number:
            phone_number = get_phone_number_list(phone_number)
            audience_objs = get_audience_log_phone_number_filtered_data(phone_number, audience_objs)
        if audience_unique_id:
            audience_objs = get_audience_log_unique_id_filtered_data(audience_unique_id, audience_objs)
        
        audience_objs_count = audience_objs.count()

        if audience_objs_count == 0:
            audience_error = {'error_code': '409', 'error_message': f'No data found for the filtered data in the given Campaign ID {campaign_obj.pk}, please make sure you are providing the correct parameters which should be present in the above mentioned Campaign ID'}
        
            detailed_report.append(audience_error)
        elif audience_objs_count <= CAMPAIGN_APP_MAX_RESPONSE_DATA_LIMIT:
            for audience_obj in audience_objs.iterator():
                audience_log = CampaignAudienceLog.objects.filter(audience=audience_obj).first()

                response_detailed_json_obj = add_audience_details_external_rcs(
                    audience_obj, audience_log, campaign_obj)
                detailed_report.append(response_detailed_json_obj)
        elif audience_objs_count > CAMPAIGN_APP_MAX_RESPONSE_DATA_LIMIT:
            email_id = users_parameter_data['email_id']
            if not email_id:
                response_message = f'Please provide a valid email address. Since the data has exceeded {CAMPAIGN_APP_MAX_RESPONSE_DATA_LIMIT} for the provided Campaign ID, the report will be sent to the email ID provided within the next 24 hours.'
                audience_error = {'error_code': '408', 'error_message': response_message}
            
                detailed_report.append(audience_error)
            else:
                filters_on_export = json.dumps({
                    "phone_number": phone_number,
                    "audience_unique_id": audience_unique_id
                })

                CampaignExportRequest.objects.create(
                    email_id=users_parameter_data['email_id'],
                    user=users_parameter_data['user'],
                    bot=campaign_obj.bot,
                    campaign=campaign_obj,
                    export_type='1',
                    filters_on_export=filters_on_export)
                message_response = {'status_code': '200', 'message': 'You will receive the campaign report data dump on the above email ID within 24 hours.'}
            
                detailed_report.append(message_response)
        
        json_obj["Detailed Report"] = detailed_report
            
        status = 200
        message = "Reports generated successfully"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In add_campaign_details_in_reports_external_rcs: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
        status = 400
        message = "Error in generating reports. Please try again"
        json_obj = {}

    return status, message, json_obj 


def add_audience_details_external(audience_log_obj, whatsapp_bsp_name, is_external_campaign_export):
    json_obj = {}
    try:
        audience_details = get_audience_details_wtsp_reports(
            audience_log_obj, is_external_campaign_export)

        mobile_number = get_mobile_number(
            audience_log_obj['audience__audience_id'], False, masking_enabled)

        _, status_message, issue, failure_reason = add_status_for_bsp_reports(
            whatsapp_bsp_name, audience_log_obj)

        attachment_url = ''
        audience_obj_record = json.loads(audience_log_obj['audience__record'])
        if isinstance(audience_obj_record, dict):
            attachment_url = audience_obj_record.get('media_url', '')
        elif isinstance(audience_obj_record, list):
            attachment_url = json.loads(audience_log_obj['audience__record'])[-1] if json.loads(audience_log_obj['audience__record']) else ''

        audience_details["attachment_url"] = attachment_url if attachment_url else '-'

        json_obj = {
            "phone_number": mobile_number,
            "unique_id": audience_details['audience_unique_id'],
            "recipient_id": audience_details["recepient_id"],
            "sent_time": audience_details["sent_datetime"],
            "delivered_time": audience_details["delivered_datetime"],
            "read_time": audience_details["read_datetime"],
            "reply_time": audience_details["replied_datetime"],
            "quick_reply": audience_details["quick_reply"],
            "status": status_message,
            "issue": issue,
            "failure_reason": failure_reason,
            "media_url": audience_details["attachment_url"],
            "message_payload": audience_details["message_payload"],
            "response_body": audience_details["response_body"]
        }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In add_audience_details_external: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        json_obj = {}

    return json_obj


def get_audience_details_rcs(audience_log_obj, campaign_obj):
    audience_details_rcs = {
        "Recipient ID": "-",
        "Sent Time": "-",
        "Delivered Time": "-",
        "Read Time": "-",
        "Template Type": "-",
        "Template Name": "-",
        "Status Code": "500"
    }
    try:
        time_zone = settings.TIME_ZONE
        recepient_id = audience_log_obj.recepient_id
        if recepient_id:
            recepient_id = recepient_id.strip()
            audience_details_rcs["Recipient ID"] = recepient_id

        audience_details_rcs["Sent Time"] = audience_log_obj.sent_datetime.astimezone(
            pytz.timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
        if audience_log_obj.is_delivered:
            audience_details_rcs["Delivered Time"] = audience_log_obj.delivered_datetime.astimezone(
                pytz.timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
            audience_details_rcs["Status Code"] = "200"
        if audience_log_obj.is_read:
            audience_details_rcs["Read Time"] = audience_log_obj.read_datetime.astimezone(
                pytz.timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")

        audience_details_rcs["Template Type"] = campaign_obj.campaign_template_rcs.get_message_type_display(
        )
        audience_details_rcs["Template Name"] = campaign_obj.campaign_template_rcs.template_name

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_audience_details_rcs: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return audience_details_rcs


def add_audience_details_external_rcs(audience_obj, audience_log_obj, campaign_obj):
    json_obj = {}
    try:
        mobile_number = get_mobile_number(
            audience_obj.audience_id, False, masking_enabled)
        audience_details_rcs = get_audience_details_rcs(
            audience_log_obj, campaign_obj)
        audience_unique_id = audience_obj.audience_unique_id
        json_obj = {
            "Mobile Number": mobile_number,
            "Recipient ID": audience_details_rcs["Recipient ID"],
            "Unique ID": audience_unique_id if audience_unique_id else "-",
            "Sent Time": audience_details_rcs["Sent Time"],
            "Delivered Time": audience_details_rcs["Delivered Time"],
            "Read Time": audience_details_rcs["Read Time"],
            "Template Type": audience_details_rcs["Template Type"],
            "Template Name": audience_details_rcs["Template Name"],
            "Status Code": audience_details_rcs["Status Code"]
        }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In add_audience_details_external_rcs: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        json_obj = {}

    return json_obj


def add_audience_details_external_vb(call_details_obj, campaign_obj):
    json_obj = {}
    try:
        voice_bot_obj = CampaignVoiceBotSetting.objects.filter(
            campaign=campaign_obj).first()

        # sending masking parameter False because masking is currently not needed in Voice bot
        mobile_number = get_mobile_number(
            str(call_details_obj.from_number), True, masking_enabled)
        json_obj = {
            "Campaign ID": str(voice_bot_obj.campaign_sid),
            "Number": mobile_number,
            "Unique ID": call_details_obj.audience_unique_id if call_details_obj.audience_unique_id else "-",
            "Status": call_details_obj.status,
            "Date Created": call_details_obj.date_created.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d %H:%M:%S"),
            "Date Updated": call_details_obj.date_updated.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d %H:%M:%S"),
            "Custom Data": "",
            "Call SID": call_details_obj.call_sid,
            "To": call_details_obj.to_number,
            "From": call_details_obj.from_number,
            "Direction": call_details_obj.direction,
            "Call Start Time": call_details_obj.call_start_time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d %H:%M:%S"),
            "Total Duration": call_details_obj.total_duration,
            "On Call Duration": call_details_obj.on_call_duration,
            "Price": str(call_details_obj.price),
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In add_audience_details_external_vb: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
        
        json_obj = {}

    return json_obj


def check_rcs_enabled_users_external(bot_obj, clients_data, total_batch_count, auto_delete_invalid_number):
    try:
        rcs_obj = RCSDetails.objects.filter(bot=bot_obj)
        rcs_enabled_user_list = []
        output_msdins = []
        deleted_rows_count = 0
        if rcs_obj.exists() and rcs_obj.first().rcs_credentials_file_path.strip() != "":
            rcs_obj = rcs_obj.first()
            service_account_location = rcs_obj.rcs_credentials_file_path
            for idx, client in enumerate(clients_data):
                phone_number = client['phone_number']
                phone_number = validation_obj.removing_phone_non_digit_element(phone_number)
                phone_number = remo_html_from_string(phone_number)
                phone_number = remo_special_tag_from_string(phone_number)
                if phone_number[0] != '+':
                    phone_number = '+' + phone_number
                if not validate_mobile_number_with_country_code(phone_number):
                    if auto_delete_invalid_number:
                        deleted_rows_count += 1 
                        continue
                    return False, [], idx + 1, '', deleted_rows_count
                else:
                    if phone_number in output_msdins:
                        return False, [], idx + 1, f'Duplicate phone number {phone_number} exists at position {idx + 1}', deleted_rows_count
                    output_msdins.append(phone_number)

            output_msdins = [output_msdins[itr:itr + 10000]
                             for itr in range(0, total_batch_count - deleted_rows_count, 10000)]
            
            try:
                for iterator in output_msdins:
                    content = rbm_service.make_batch_cap_request(
                        iterator, service_account_location)
                    if "reachableUsers" in content:
                        rcs_enabled_user_list += content["reachableUsers"]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("In check_rcs_enabled_users_external : %s %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'Campaign'})
                return False, [], -1, '', deleted_rows_count

            return True, rcs_enabled_user_list, -1, '', deleted_rows_count
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In check_rcs_enabled_users_external : %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
        return False, [], -1, deleted_rows_count


def validate_mobile_number_with_country_code(mobile_number):
    try:
        regex = INTERNATION_PHONE_NUMBER_REGEX
        if not re.match(regex, mobile_number):
            return False

        if mobile_number.find("+91") == 0:
            ind_number = mobile_number[3:None]
            if not validate_mobile_number_without_country_code(ind_number):
                return False
        
        if mobile_number.find("+") == 0:
            mobile_number = mobile_number[1:None]
            if not mobile_number.isdigit():
                return False

        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In validate_mobile_number_with_country_code : %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
        return False


def validate_mobile_number_without_country_code(mobile_number):
    try:
        regex = re.compile("[6-9][0-9]{9}")

        if re.fullmatch(regex, mobile_number) == None:
            return False
        
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In validate_mobile_number_without_country_code : %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
        return False


def check_and_validate_date_for_voicebot_wrt_current_time(start_date, start_time):
    status = 400
    message = ""
    try:
        start_date = datetime(start_date.year, start_date.month, start_date.day, start_time.hour, start_time.minute)

        if start_date < datetime.now():
            status = 400
            message = 'Campaign start date and time must be greater than current date and time.'
            return status, message

        status = 200
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In check_and_validate_date_for_voicebot_wrt_current_time : %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
    
    return status, message


def check_and_validate_date_for_voicebot(start_date, start_time, end_date, end_time):
    status = 400
    message = ""
    try:
        start_date = datetime(start_date.year, start_date.month, start_date.day, start_time.hour, start_time.minute)
        end_date = datetime(end_date.year, end_date.month, end_date.day, end_time.hour, end_time.minute)

        if start_date < datetime.now():
            status = 400
            message = 'Campaign start date and time must be greater than current date and time.'
            return status, message

        if end_date < start_date:
            status = 400
            message = 'Campaign end date and time must be greater than start date and time.'
            return status, message

        status = 200
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In check_and_validate_date_for_voicebot : %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
    
    return status, message
    

def validate_external_auth_token(auth_token, response):
    try:
        auth_token_obj = None

        if validate_uuid_auth_token(auth_token):
            auth_token_objs = CampaignAuthToken.objects.filter(
                token=uuid.UUID(str(auth_token)))
        else:
            response['status'] = 401
            response['status_message'] = 'Invalid authorization token!'
            return response, auth_token_obj

        if auth_token_objs.exists():
            auth_token_obj = auth_token_objs.first()
            token_create_time = auth_token_obj.created_datetime + timedelta(hours=EXTERNAL_CAMPAIGN_AUTH_TOKEN_VALIDITY_HOURS)
            tz = pytz.timezone(settings.TIME_ZONE)
            auth_datetime_obj = token_create_time.astimezone(
                tz)
            current_datetime_obj = timezone.now().astimezone(tz)
            if auth_datetime_obj < current_datetime_obj or auth_token_obj.is_expired:
                auth_token_obj.delete()
                response['status'] = 401
                response['status_message'] = 'Authorization token is either expired or invalid!'
                auth_token_obj = None
        else:
            response['status'] = 401
            response['status_message'] = 'Authorization token is either expired or invalid!'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In validate_external_auth_token: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

    return response, auth_token_obj


def validate_uuid_auth_token(auth_token):
    try:
        uuid.UUID(str(auth_token))
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In validate_uuid_auth_token: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return False


def add_single_batch_and_send_message_api(data, campaign_obj):
    
    response = {}
    response["status"] = 400
    response["status_message"] = "Not able to send message successfully. This is an internal error."
    campaign_batch_obj = None
    try:
        
        client = data.get("client_data", "")
        if client == "":
            response["status_message"] = "Please add valid client data"
            return 400, response

        whatsapp_bsp = data.get("whatsapp_bsp", "1")
        campaign_batch_obj = campaign_obj.batch
        if campaign_batch_obj == None:
            response["status"] = 404
            response["status_message"] = "Batch Not Found!"
            return 404, response

        if campaign_obj.channel.value == "whatsapp":
            phone_numbers = []
            
            if not whatsapp_bsp.isdigit():
                response["status_message"] = "Please enter a valid bot bsp"
                return 400, response

            try:
                phone_number = client.get("phone_number", "")
                phone_number = validation_obj.removing_phone_non_digit_element(
                    phone_number)
                phone_number = remo_html_from_string(phone_number)
                if phone_number[0] != '+':
                    phone_number = '+' + phone_number
                name = client.get("name", "")
                if campaign_obj.channel.value == "whatsapp":
                    if not validate_mobile_number_with_country_code(phone_number):
                        response["status_message"] = "Invalid phone number in client data"
                        return 400, response

                phone_number = remo_special_tag_from_string(phone_number)
                phone_number = phone_number.strip()
                name = remo_html_from_string(str(name))
                name = remo_special_tag_from_string(name)
                name = name.strip()

                if name == "":
                    response["status_message"] = "Invalid name in client data"
                    return 400, response

                phone_numbers.append(phone_number)

            except:
                return 400, "Phone number or name is empty or not defined in some entry of the client data"

            total_opted_in = Profile.objects.filter(user_id__in=phone_numbers, campaign_optin=True).count()
            campaign_batch_obj.total_audience += 1
            campaign_batch_obj.total_audience_opted = total_opted_in
            campaign_batch_obj.save(update_fields=["total_audience"])
            
        status, response = send_single_api_campaign_message(campaign_obj, client, whatsapp_bsp)
        return status, response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In add_single_batch_and_send_message_api: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
        return 400, response


def send_single_api_campaign_message(campaign_obj, client, whatsapp_bsp):
    response = {}
    response["status"] = 400
    try:

        campaign_api = CampaignAPI.objects.filter(
            campaign=campaign_obj)
        
        channel_value = campaign_obj.channel.value
        if not campaign_api.exists() or not campaign_api.first().is_api_completed:
            response["status_message"] = "Send Campaign failed because API Integration is pending."
            return 400, response
        else:
            if channel_value == "whatsapp":
                campaign_api = campaign_api.first()
                wsp_obj = CampaignWhatsAppServiceProvider.objects.filter(name=whatsapp_bsp).first()  # this is value code for bsp used, defaults to 1(Ameyo)
                if not wsp_obj:
                    response["status_message"] = "Whatsapp BSP doesn't exists for value " + whatsapp_bsp
                    return 400, response
                bot_wsp_obj = CampaignBotWSPConfig.objects.filter(bot=campaign_obj.bot, whatsapp_service_provider=wsp_obj).first()
                if not bot_wsp_obj:
                    
                    bot_wsp_obj = CampaignBotWSPConfig.objects.create(bot=campaign_obj.bot, whatsapp_service_provider=wsp_obj) 
                    file_obj = open(wsp_obj.default_code_file_path, "r")
                    code = file_obj.read()
                    file_obj.close()
                    bot_wsp_obj.code = code
                    bot_wsp_obj.save()              

                campaign_api.campaign_bot_wsp_config = bot_wsp_obj
                campaign_api.save()

            if channel_value == "whatsapp" and not campaign_obj.campaign_template:
                return 404, "The template related to this campaign has been removed."

            if channel_value == "whatsapp":
                response = execute_send_event_based_campaign_external(campaign_api, campaign_obj, client)

            return response["status"], response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In send_single_api_campaign_message: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
        response["status_message"] = "Send Campaign failed because API Integration is pending."
        return 400, response


def is_valid_campign_batch_template_name(name):
    try:
        name = validation_obj.sanitize_input(name)

        if validation_obj.check_for_special_characters(name) or name == "":
            return 400, name

        return 200, name
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In is_valid_campign_batch_template_name: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return 400, name


def unfilled_variable_failure_response(unfilled_variables, audience_log_obj):
    unfilled_variables = ', '.join(unfilled_variables)
    failure_response = {"errors": [{"code": 500, "title": "Failed to send message due to missing variable.",
                                            "details": f"Expected a value in {unfilled_variables} but send data was empty. Please fill in the required data for this user"}]}
    audience_log_obj.is_failed = True
    audience_log_obj.request = json.dumps({})
    audience_log_obj.response = json.dumps(failure_response)
    audience_log_obj.is_processed = True
    audience_log_obj.save(update_fields=["request", "response", "is_failed", "is_processed"])
    return failure_response


def execute_send_event_based_campaign_external(campaign_api_obj, campaign_obj, client):
    api_response = {}
    try:
        campaign_obj.is_source_dashboard = False
        campaign_obj.start_datetime = datetime.now()
        campaign_obj.save(update_fields=['status', 'is_source_dashboard', 'start_datetime'])
        campaign_batch = campaign_obj.batch
        campaign_template = campaign_obj.campaign_template

        lang_code = get_language_code(campaign_template)

        template_metadata_json = json.loads(campaign_template.template_metadata) 

        document_file_name = CAMPAIGN_DOCUMENT_FILE_NAME

        document_file_name = get_document_name(template_metadata_json, client)

        analytics_objs = CampaignAnalytics.objects.filter(campaign=campaign_obj)
        if analytics_objs.exists():
            analytics_obj = analytics_objs.first()
            analytics_obj.total_audience = campaign_obj.batch.total_audience
            analytics_obj.save(update_fields=["total_audience"])
        else:
            analytics_obj = CampaignAnalytics.objects.create(campaign=campaign_obj, total_audience=campaign_batch.total_audience)

        code = campaign_api_obj.campaign_bot_wsp_config.code 
        namespace = campaign_api_obj.campaign_bot_wsp_config.namespace

        phone_number = client.get("phone_number", "")
        phone_number = validation_obj.removing_phone_non_digit_element(phone_number)
        phone_number = remo_html_from_string(str(phone_number))
        phone_number = remo_special_tag_from_string(phone_number)
        phone_number = phone_number.strip()

        unique_id = client.get('unique_id', '')
        if unique_id:
            unique_id = get_audience_unique_id(unique_id)
                
        variable_details, unfilled_variables = get_external_variable_details(client)
        
        dynamic_cta_url_variable_details_list = []
        dynamic_cta_url_variable_details = get_dynamic_cta_url_variable_details(client, campaign_template)
        
        if dynamic_cta_url_variable_details:
            dynamic_cta_url_variable_details_list.append(dynamic_cta_url_variable_details)
        if len(dynamic_cta_url_variable_details) == 0 and 'dynamic_cta' in client:
            unfilled_variables.add('dynamic_cta')
        
        header_variable_list = []
        header_variable = get_header_variable_details(client)

        if header_variable:
            header_variable_list.append(header_variable)
        if len(header_variable_list) == 0 and 'header_variable' in client:
            unfilled_variables.add('header_variable')
        
        template_type = campaign_template.template_type.title

        attachment_src = campaign_template.attachment_src
        if template_type != 'text':
            media_url = client.get('media_url')
            if media_url != None and not media_url.strip():
                unfilled_variables.add('media_url')
                attachment_src = ""
            elif media_url:
                attachment_src = media_url.strip()

        client['media_url'] = attachment_src

        audience_obj = CampaignAudience.objects.create(
            audience_id=int(phone_number), channel=campaign_obj.channel, batch=campaign_batch, record=json.dumps(client), campaign=campaign_obj, audience_unique_id=unique_id)

        audience_log_obj = CampaignAudienceLog.objects.create(
            audience=audience_obj, campaign=campaign_obj)
        if unfilled_variables:
            failure_response = unfilled_variable_failure_response(unfilled_variables, audience_log_obj)
            api_response["status"] = 500
            api_response["status_message"] = failure_response
            return api_response

        if is_livechat_connected(phone_number, campaign_obj.bot):
            failure_response = livechat_active_session_failure_response(
                audience_log_obj)
            api_response["status"] = 500
            api_response["status_message"] = failure_response
            return api_response

        parameter = {
            'mobile_number': phone_number,
            'template': {
                'name': campaign_template.template_name,
                'type': template_type,
                'language': lang_code,
                'link': attachment_src,
                'cta_text': campaign_template.cta_text,
                'cta_link': campaign_template.cta_link,
            },
            'user_details': [],
            'variables': variable_details,
            'header_variable': header_variable_list,
            'dynamic_cta_url_variable': dynamic_cta_url_variable_details_list,
            'type_of_first_cta_btton': template_metadata_json.get('type_of_first_cta_btton'),
            'document_file_name': document_file_name,
            'namespace': namespace,
            'api_key': '',
        }

        try:
            response = func_timeout.func_timeout(
                CAMPAIGN_APP_MAX_TIMEOUT_LIMIT, execute_bsp_code, args=[code, parameter])  
        except func_timeout.FunctionTimedOut:
            response = {}
            response['response'] = {"errors": [{"code": 408, "title": "Function timed out!",
                                                "details": "Request timed out for this entry!"}]}
            response['request'] = parameter 

        if response.get('response') and 'request_id' in response['response']:
            audience_log_obj.recepient_id = response['response']['request_id']
        else:
            audience_log_obj.is_failed = True
        
        if response.get('request') and response.get("response"):
            audience_log_obj.request = json.dumps(response['request'])
            audience_log_obj.response = json.dumps(response['response'])

        audience_log_obj.is_processed = True    
        audience_log_obj.save(update_fields=["recepient_id", "request", "response", "is_failed", "is_processed"])
        campaign_obj.status = CAMPAIGN_ONGOING
        campaign_obj.save(update_fields=["status"])
        unsuccessful = CampaignAudienceLog.objects.filter(
            campaign=campaign_obj, is_failed=True).count()
        analytics_obj.message_unsuccessful = unsuccessful
        analytics_obj.save(update_fields=["message_unsuccessful"])

        api_response["status"] = 200
        api_response["status_message"] = response.get("status_message")

        if response.get("status") == 500:
            api_response["status"] = 500
            return api_response

        if response.get("response").get("errors"):
            api_response["status"] = 500
            if response.get("response").get("errors")[0].get("code") == 408:
                api_response["status"] = 408    
            api_response["status_message"] = response.get("response").get("errors")[0].get("details")
            return api_response

        api_response["recepient_id"] = response.get('response').get('request_id')

        return api_response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In execute_send_event_based_campaign_external: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        api_response["status"] = 500
        api_response["status_message"] = "There is some internal error while sending the campaign."
        return api_response


def add_single_api_campaign_details_in_reports(data, campaign_obj, date_filter_required, start_date_time, end_date_time, user):

    try:
        campaign_analytics = CampaignAnalytics.objects.filter(
            campaign=campaign_obj)

        email_id = data.get("email", "")
        if not campaign_analytics.exists():
            status = 400
            message = "Campaign Analytics has not yet been generated. Please make sure that campaign is triggered atleast once."
            json_obj = {}
            return status, message, json_obj
        
        audience_logs = CampaignAudienceLog.objects.filter(
            campaign=campaign_obj)

        audience_unique_id = data.get('unique_id', '')
        phone_number = data.get('phone_number', '').strip()
        phone_number = validation_obj.removing_phone_non_digit_element(
            phone_number)
        phone_number = remo_html_from_string(str(phone_number))
        phone_number = remo_special_tag_from_string(phone_number)

        if phone_number:
            phone_number = get_phone_number_list(phone_number)
            if phone_number:
                audience_logs = get_audience_log_phone_number_filtered_data(
                    phone_number, audience_logs)
        if audience_unique_id:
            audience_logs = get_audience_log_unique_id_filtered_data(
                audience_unique_id, audience_logs)

        campaign_analytics = campaign_analytics.first()
        if audience_logs.count() > CAMPAIGN_APP_MAX_RESPONSE_DATA_LIMIT:
            if validation_obj.is_valid_email(email_id):

                filters_on_export = json.dumps({
                    "phone_number": phone_number,
                    "audience_unique_id": audience_unique_id
                })
                campaign_export_request_obj = CampaignExportRequest.objects.create(
                    email_id=email_id,
                    user=user,
                    bot=campaign_obj.bot,
                    campaign=campaign_obj,
                    filters_on_export=filters_on_export)

                if date_filter_required:
                    export_type = 3
                    campaign_export_request_obj.export_type = export_type
                    campaign_export_request_obj.start_date = start_date_time
                    campaign_export_request_obj.end_date = end_date_time
                else:
                    export_type = 1
                    campaign_export_request_obj.export_type = export_type
                
                campaign_export_request_obj.save(update_fields=['export_type', 'start_date', 'end_date'])
                status = 200
                message = "You will receive the campaign report data dump on the above email ID within 24 hours."
                return status, message, {}
            else:
                status = 400
                message = f'Please provide a valid email address. Since the data has exceeded {CAMPAIGN_APP_MAX_RESPONSE_DATA_LIMIT} for the provided Campaign ID, the report will be sent to the email ID provided within the next 24 hours.'
                return status, message, {}

        bot_wsp_obj = None
        campaign_api_obj = CampaignAPI.objects.filter(campaign=campaign_obj).first()
        if campaign_api_obj:
            bot_wsp_obj = campaign_api_obj.campaign_bot_wsp_config
            
        whatsapp_bsp_name = "-"
        if bot_wsp_obj:
            whatsapp_bsp_name = bot_wsp_obj.whatsapp_service_provider.get_name_display()
        
        json_obj = {
            "Overall Report": {
                "campaign_name": campaign_obj.name,
                "whatsapp_bsp": whatsapp_bsp_name,
                "audience_batch_name": campaign_obj.batch.batch_name if campaign_obj.batch else "-",
                "total_audience_batch_size": campaign_obj.batch.total_audience,
                "message_sent": campaign_analytics.message_sent,
                "message_delivered": campaign_analytics.message_delivered,
                "message_read": campaign_analytics.message_read,
                "message_replied": campaign_analytics.message_replied,
                "failed": campaign_analytics.message_unsuccessful,
                "open_rate": str(campaign_analytics.open_rate()) + "%",
                "template_name": campaign_obj.campaign_template.template_name if campaign_obj.campaign_template else "-"
            
            },
            "Detailed Report": []
        }

        detailed_report = []

        if date_filter_required:
            audience_logs = audience_logs.filter(
                created_date__gte=start_date_time, created_date__lte=end_date_time)

        audience_logs = audience_logs.values('id', 'audience__audience_unique_id', 'audience__audience_id', 'recepient_id', 'is_sent', 'sent_datetime', 'audience__record',
                                             'is_delivered', 'delivered_datetime', 'is_read', 'read_datetime', 'is_replied', 'replied_datetime', 'is_failed', 'request', 'response')

        for audience_log in audience_logs.iterator():
            if not audience_log:
                continue
            else:
                is_external_campaign_export = False if campaign_obj.is_source_dashboard else True
                response_detailed_json_obj = add_audience_details_external(
                    audience_log, whatsapp_bsp_name, is_external_campaign_export)
                detailed_report.append(response_detailed_json_obj)
        if not detailed_report:
            audience_error = {'error_code': '409', 'error_message': f'No data found for the filtered data in the given Campaign ID {campaign_obj.pk}, please make sure you are providing the correct parameters which should be present in the above mentioned Campaign ID'}
            detailed_report.append(audience_error)
        json_obj["Detailed Report"] = detailed_report
            
        status = 200
        message = "Reports generated successfully"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In add_single_api_campaign_details_in_reports: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})
        status = 400
        message = "Error in generating reports. Please try again"
        json_obj = {}

    return status, message, json_obj 


def get_document_name(template_metadata_json, data):
    document_file_name = template_metadata_json.get('document_file_name', CAMPAIGN_DOCUMENT_FILE_NAME)
    if not document_file_name.strip():
        document_file_name = CAMPAIGN_DOCUMENT_FILE_NAME
    
    document_filename = data.get('document_filename', '').strip()
    if document_filename:
        document_file_name = document_filename
    return document_file_name


def get_attachment_variable_details(attachment_data, client):
    media_send_type = attachment_data.get('media_send_type', 'static').strip()
    static_media_url = attachment_data.get('media_url')
    attachment_src = attachment_data.get('attachment_src')
    if media_send_type == 'static' and static_media_url:
        attachment_src = static_media_url
    elif media_send_type == 'dynamic':
        dynamic_media_url = client.get('media_url')
        if dynamic_media_url == None or not dynamic_media_url.strip():
            return '', True
        attachment_src = dynamic_media_url

    return attachment_src, False


def get_header_variable_details(client):
    try:
        header_variable = client.get("header_variable", '').strip()
        if header_variable:
            header_variable = remo_html_from_string(header_variable)

        return header_variable
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_header_variable_details: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return header_variable


def get_dynamic_cta_url_variable_details(client, campaign_template):
    try:
        dynamic_cta_url_variable_details = client.get("dynamic_cta", '').strip()
        if dynamic_cta_url_variable_details:
            cta_link = campaign_template.cta_link
            if cta_link and '{{1}}' == cta_link.split('/')[-1]:
                cta_link = cta_link[:-5] 
            dynamic_cta_url_variable_details = dynamic_cta_url_variable_details.replace(cta_link, "")
            dynamic_cta_url_variable_details = remo_html_from_string(dynamic_cta_url_variable_details)

        return dynamic_cta_url_variable_details
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_dynamic_cta_url_variable_details: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

        return dynamic_cta_url_variable_details
