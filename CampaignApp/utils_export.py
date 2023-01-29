from os.path import basename
from openpyxl.cell import WriteOnlyCell
from zipfile import ZipFile
from CampaignApp.models import *
from CampaignApp.utils_validation import CampaignInputValidation
from CampaignApp.constants import OVERALL_DETAILS_SHEET_COLUMNS_LIST, DETAILED_SHEET_COLUMNS_LIST, WHATSAPP_AUDIENCE_SHEET_COLUMNS_LIST
import os
import sys
import pytz
import json
from django.conf import settings
from openpyxl.styles import Font
bold = Font(bold=True)


def get_campaign_details_data(campaign_obj):
    campaign_details = {"bot_name": "-", "campaign_name": "-", "whatsapp_bsp_name": "-", "create_datetime": "-", "source": "-", "time_zone": "-", "message_processed": "-", "open_rate": "-", "message_sent": "-", "message_unsuccessful": "-", "message_delivered": "-",
                        "message_read": "-", "message_replied": "-", "test_message_sent": "-", "test_message_unsuccessful": "-", "batch_name": "-", "total_audience": "-", "template_name": "-", "template_type": "-"}
    try:
        campaign_api_obj = CampaignAPI.objects.filter(
            campaign=campaign_obj).first()

        bot_wsp_obj = campaign_api_obj.campaign_bot_wsp_config if campaign_api_obj else None
        whatsapp_bsp_name = bot_wsp_obj.whatsapp_service_provider.get_name_display(
        ) if bot_wsp_obj else "-"
        time_zone = settings.TIME_ZONE

        campaign_details["bot_name"] = campaign_obj.bot.name
        campaign_details["campaign_name"] = campaign_obj.name
        campaign_details["whatsapp_bsp_name"] = whatsapp_bsp_name
        campaign_details["create_datetime"] = campaign_obj.create_datetime.astimezone(
            pytz.timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
        campaign_details["source"] = "Dashboard" if campaign_obj.is_source_dashboard else "External API"
        campaign_details["time_zone"] = time_zone

        campaign_analytics_obj = CampaignAnalytics.objects.filter(
            campaign=campaign_obj).first()
        if campaign_analytics_obj:
            campaign_details["message_processed"] = str(
                campaign_analytics_obj.message_processed)
            campaign_details["open_rate"] = str(
                campaign_analytics_obj.open_rate()) + "%"

            campaign_details["message_sent"] = str(
                campaign_analytics_obj.message_sent)
            campaign_details["message_unsuccessful"] = str(
                campaign_analytics_obj.message_unsuccessful)
            campaign_details["message_delivered"] = str(
                campaign_analytics_obj.message_delivered)
            campaign_details["message_read"] = str(
                campaign_analytics_obj.message_read)
            campaign_details["message_replied"] = str(
                campaign_analytics_obj.message_replied)

            campaign_details["test_message_sent"] = str(
                campaign_analytics_obj.test_message_sent)
            campaign_details["test_message_unsuccessful"] = str(
                campaign_analytics_obj.test_message_unsuccessful)

        if campaign_obj.batch:
            campaign_details["batch_name"] = campaign_obj.batch.batch_name
            campaign_details["total_audience"] = str(
                campaign_obj.batch.total_audience)

        if campaign_obj.campaign_template:
            campaign_details["template_name"] = campaign_obj.campaign_template.template_name
            campaign_details["template_type"] = campaign_obj.campaign_template.template_type.title

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_campaign_details_data: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return campaign_details


def add_campaign_details(sheet, campaign_details):
    try:
        overall_details_bold_columns = []
        for value in OVERALL_DETAILS_SHEET_COLUMNS_LIST[:8]:
            cell = WriteOnlyCell(sheet, value=value)
            cell.font = bold
            overall_details_bold_columns.append(cell)

        sheet.append(overall_details_bold_columns[:7])
        sheet.append([campaign_details["bot_name"], campaign_details["campaign_name"], campaign_details["whatsapp_bsp_name"],
                     campaign_details["create_datetime"], campaign_details["open_rate"], campaign_details["source"], campaign_details["time_zone"]])
        sheet.append([])

        sheet.append([overall_details_bold_columns[7]])
        sheet.append([campaign_details["message_processed"]])
        sheet.append([])

        cell = WriteOnlyCell(sheet, value="Campaign Messages")
        cell.font = bold
        sheet.append([cell])
        sheet.append(OVERALL_DETAILS_SHEET_COLUMNS_LIST[8:-2])
        sheet.append([campaign_details["message_sent"], campaign_details["message_unsuccessful"], campaign_details["message_delivered"], campaign_details["message_read"], campaign_details["message_replied"],
                     campaign_details["batch_name"], campaign_details["total_audience"], campaign_details["template_name"], campaign_details["template_type"]])
        sheet.append([])

        cell = WriteOnlyCell(sheet, value="Test Messages")
        cell.font = bold
        sheet.append([cell])
        sheet.append(OVERALL_DETAILS_SHEET_COLUMNS_LIST[-2:])
        sheet.append([campaign_details["test_message_sent"],
                     campaign_details["test_message_unsuccessful"]])

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_campaign_details: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def add_default_detailed_columns(sheet, is_external_api_export):
    detailed_columns = []
    for value in DETAILED_SHEET_COLUMNS_LIST:
        cell = WriteOnlyCell(sheet, value=value)
        cell.font = bold
        detailed_columns.append(cell)

    if is_external_api_export:
        cell = WriteOnlyCell(sheet, value="Unique ID")
        cell.font = bold
        detailed_columns.append(cell)

    sheet.append(detailed_columns)


def add_audience_details(audience_log_obj, sheet, masking_enabled, whatsapp_bsp_name, is_external_campaign_export=False):
    try:
        audience_details = get_audience_details_wtsp_reports(audience_log_obj, is_external_campaign_export)

        mobile_number = get_mobile_number(
            audience_log_obj['audience__audience_id'], False, masking_enabled)

        _, status_message, issue, failure_reason = add_status_for_bsp_reports(
            whatsapp_bsp_name, audience_log_obj)

        attachment_url = ''
        audience_obj_record = json.loads(audience_log_obj['audience__record'])
        if isinstance(audience_obj_record, dict):
            attachment_url = audience_obj_record.get('media_url', '')
        elif isinstance(audience_obj_record, list):
            attachment_url = json.loads(audience_log_obj['audience__record'])[
                -1] if json.loads(audience_log_obj['audience__record']) else ''

        if attachment_url:
            cell = WriteOnlyCell(sheet, value=attachment_url)
            cell.hyperlink = attachment_url
            cell.style = "Hyperlink"
            attachment_url = cell
        else:
            attachment_url = '-'

        audience_details_list = [mobile_number, audience_details["recepient_id"], audience_details["sent_datetime"], audience_details["delivered_datetime"], audience_details["read_datetime"],
                                 audience_details["replied_datetime"], audience_details["quick_reply"], status_message, issue, failure_reason, attachment_url, audience_details["message_payload"], audience_details["response_body"]]

        if is_external_campaign_export:
            audience_details_list.append(audience_details["audience_unique_id"])
        
        sheet.append(audience_details_list)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_audience_details: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


# Getting user name from audience records from its type
def get_user_name_from_audience_record(audience_records):
    try:
        if isinstance(audience_records, list):
            audience_records_length = len(audience_records)
            if audience_records_length > 1:
                user_name = audience_records[1].strip() 
            if audience_records_length > 2:
                user_name += ' ' + audience_records[2].strip()
        elif isinstance(audience_records, dict):
            user_name = str(audience_records.get("name")).strip()
        else:
            user_name = ''
        return user_name
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in get_user_name_from_audience_record: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
        return ''


def get_audience_details_wtsp_reports(audience_log_obj, is_external_campaign_export):
    try:
        # adding audience_details dictionary directly in this scope so no cached data return in response.
        audience_details = {"recepient_id": "-",
                            "sent_datetime": "-",
                            "delivered_datetime": "-",
                            "read_datetime": "-",
                            "replied_datetime": "-",
                            "quick_reply": "-",
                            "message_payload": "-",
                            "response_body": "-",
                            "audience_unique_id": "-"
                            }
        time_zone = settings.TIME_ZONE
        recepient_id = str(audience_log_obj['recepient_id']).strip()
        if recepient_id and recepient_id != "None":
            audience_details["recepient_id"] = recepient_id

        audience_details["sent_datetime"] = audience_log_obj['sent_datetime'].astimezone(
            pytz.timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
        if audience_log_obj['is_delivered']:
            audience_details["delivered_datetime"] = audience_log_obj['delivered_datetime'].astimezone(
                pytz.timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
        if audience_log_obj['is_read']:
            audience_details["read_datetime"] = audience_log_obj['read_datetime'].astimezone(
                pytz.timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
        if audience_log_obj['is_replied']:
            audience_details["replied_datetime"] = audience_log_obj['replied_datetime'].astimezone(
                pytz.timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
            quick_reply_obj = ', '.join(list(QuickReply.objects.filter(
                audience_log__pk=audience_log_obj['id']).values_list('name', flat=True)))
            audience_details["quick_reply"] = quick_reply_obj

        if is_external_campaign_export:
            audience_unique_id = audience_log_obj['audience__audience_unique_id']
            if audience_unique_id:
                audience_details["audience_unique_id"] = audience_unique_id

        audience_details["message_payload"] = audience_log_obj['request']
        audience_details["response_body"] = audience_log_obj['response']

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_audience_details_wtsp_reports: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return audience_details


def get_mobile_number(mobile_number, is_voice_bot, masking_enabled):
    try:
        if masking_enabled:
            if is_voice_bot:
                mobile_number = mobile_number[:2] + \
                    'XXXXXXX' + mobile_number[-1]
            else:
                mobile_number = mobile_number[:4] + \
                    'XXXXXXX' + mobile_number[-1]

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_mobile_number: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return mobile_number


def add_status_for_bsp_reports(whatsapp_bsp_name, audience_log_obj):
    try:
        response = json.loads(audience_log_obj['response'])

        if whatsapp_bsp_name.strip().lower() == "ameyo":
            if audience_log_obj['recepient_id'] and not str(audience_log_obj['recepient_id']).isspace() and audience_log_obj['is_sent']:
                return ["200", "Success", "-", "-"]
            elif audience_log_obj['is_failed']:
                error_message = str(response['errors'][0]['details']).strip()
                error_title = str(response['errors'][0]['title']).strip()
                return ["500", "Failed", error_message, error_title]
            else:
                return ["500", "Not Available", "-", "-"]
        else:
            if response.get("status") == 'processing':
                return ["200", "Success", "-", "-"]
            else:
                return ["500", "Failed", "Failed", "Unknown Error"]

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_status_for_bsp_reports: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return ["500", "Failed", "Failed", "Unknown Error"]


def add_status_for_bsp(campaign_obj, audience_log_obj):
    try:
        campaign_api_obj = CampaignAPI.objects.filter(
            campaign=campaign_obj).first()
        bot_wsp_obj = None
        if campaign_api_obj:
            bot_wsp_obj = campaign_api_obj.campaign_bot_wsp_config

        whatsapp_bsp_name = "Ameyo"
        if bot_wsp_obj:
            whatsapp_bsp_name = bot_wsp_obj.whatsapp_service_provider.get_name_display()

        try:
            response = json.loads(audience_log_obj.response)

            if whatsapp_bsp_name.strip().lower() == "ameyo":
                if audience_log_obj.recepient_id and not str(audience_log_obj.recepient_id).isspace() and audience_log_obj.is_sent:
                    return ["200", "Success", "-", "-"]
                elif audience_log_obj.is_failed:
                    error_message = str(
                        response['errors'][0]['details']).strip()
                    error_title = str(response['errors'][0]['title']).strip()
                    return ["500", "Failed", error_message, error_title]
                else:
                    return ["500", "Not Available", "-", "-"]
            else:
                if response.get("status") == 'processing':
                    return ["200", "Success", "-", "-"]
                else:
                    return ["500", "Failed", "Failed", "Unknown Error"]
        except:
            return ["500", "Failed", "Failed", "Unknown Error"]

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_status_for_bsp: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

        return "500", "Failed", "Failed", "Unknown Error"


def add_default_whatsapp_audience_history_columns(sheet):
    whatsapp_detailed_columns = []
    for value in WHATSAPP_AUDIENCE_SHEET_COLUMNS_LIST:
        cell = WriteOnlyCell(sheet, value=value)
        cell.font = bold
        whatsapp_detailed_columns.append(cell)

    sheet.append(whatsapp_detailed_columns)


def add_whatsapp_overall_details(sheet, user_stats, campaign_details, data):
    try:
        overall_details_bold_columns = []
        status_filter = data["status_filter"]
        quick_reply_filter = data["quick_reply"]
        searched_type = data["searched_type"]
        searched_value = data['searched_value']
        test_message_filter = data.get('test_message_filter', list())

        for value in OVERALL_DETAILS_SHEET_COLUMNS_LIST[:8]:
            if value == "Open Rate":
                continue
            cell = WriteOnlyCell(sheet, value=value)
            cell.font = bold
            overall_details_bold_columns.append(cell)

        sheet.append(overall_details_bold_columns[:6])
        sheet.append([campaign_details["bot_name"], campaign_details["campaign_name"], campaign_details["whatsapp_bsp_name"],
                     campaign_details["create_datetime"], campaign_details["source"], campaign_details["time_zone"]])
        sheet.append([])

        sheet.append([overall_details_bold_columns[6]])
        sheet.append([str(user_stats[0]["total_processed"])])
        sheet.append([])

        cell = WriteOnlyCell(sheet, value="Campaign Messages")
        cell.font = bold
        sheet.append([cell])
        sheet.append(OVERALL_DETAILS_SHEET_COLUMNS_LIST[8:-2])
        sheet.append([str(user_stats[0]["total_sent"]), str(user_stats[0]["total_failed"]), str(user_stats[0]["total_delivered"]), str(user_stats[0]["total_read"]), str(user_stats[0]["total_replied"]),
                     campaign_details["batch_name"], campaign_details["total_audience"], campaign_details["template_name"], campaign_details["template_type"]])
        sheet.append([])

        cell = WriteOnlyCell(sheet, value="Test Messages")
        cell.font = bold
        sheet.append([cell])
        sheet.append(OVERALL_DETAILS_SHEET_COLUMNS_LIST[-2:])
        sheet.append([str(user_stats[0]["total_test_sent"]),
                     str(user_stats[0]["total_test_failed"])])
        sheet.append([])

        cell = WriteOnlyCell(sheet, value="Filters Applied")
        cell.font = bold
        sheet.append([cell])

        sheet.append(
            ["Phone Number", searched_value if searched_type == "phone_number" else "NA"])
        sheet.append(
            ["Recipient ID", searched_value if searched_type == "recipient_id" else "NA"])

        if len(status_filter) == 1:
            sheet.append(["Status", status_filter[0]])
        else:
            sheet.append(["Status", "Success, Failed"])

        if len(test_message_filter) == 1:
            sheet.append(["Message Type", test_message_filter[0]])
        else:
            sheet.append(["Message Type", "Campaign Message, Test Message"])

        if quick_reply_filter:
            quick_reply_filter = ', '.join(quick_reply_filter)
            sheet.append(["Quick Reply", quick_reply_filter])
        else:
            sheet.append(["Quick Reply", "NA"])

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_whatsapp_overall_details: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def add_sheet_whatsapp_audience_history_report(audience_log_obj, sheet, whatsapp_bsp_name):
    try:
        audience_details = get_audience_details_wtsp_reports(
            audience_log_obj, False)

        mobile_number = get_mobile_number(
            audience_log_obj['audience__audience_id'], False, False)

        message_type = "Test" if audience_log_obj["is_test"] else "Campaign"

        _, status_message, _, failure_reason = add_status_for_bsp_reports(
            whatsapp_bsp_name, audience_log_obj)

        request = json.loads(audience_log_obj['request'])
        template_name = request.get('template', {}).get('name', '-')

        whatsapp_audience_details_list = [mobile_number, audience_details["recepient_id"], status_message, message_type, template_name, failure_reason,
                                          audience_details["quick_reply"], audience_details["sent_datetime"], audience_details["delivered_datetime"], audience_details["read_datetime"]]

        sheet.append(whatsapp_audience_details_list)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_sheet_whatsapp_audience_history_report: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def get_test_campaign_details_data(campaign_obj):
    campaign_details = {"bot_name": "-", "campaign_name": "-", "whatsapp_bsp_name": "-", "create_datetime": "-", "source": "-",
                        "time_zone": "-", "test_message_processed": "-", "test_message_sent": "-", "test_message_unsuccessful": "-"}
    try:
        campaign_api_obj = CampaignAPI.objects.filter(
            campaign=campaign_obj).first()

        bot_wsp_obj = campaign_api_obj.campaign_bot_wsp_config if campaign_api_obj else None
        whatsapp_bsp_name = bot_wsp_obj.whatsapp_service_provider.get_name_display(
        ) if bot_wsp_obj else "-"
        time_zone = settings.TIME_ZONE

        campaign_details["bot_name"] = campaign_obj.bot.name
        campaign_details["campaign_name"] = campaign_obj.name
        campaign_details["whatsapp_bsp_name"] = whatsapp_bsp_name
        campaign_details["create_datetime"] = campaign_obj.create_datetime.astimezone(
            pytz.timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
        campaign_details["source"] = "Dashboard" if campaign_obj.is_source_dashboard else "External API"
        campaign_details["time_zone"] = time_zone

        campaign_analytics_obj = CampaignAnalytics.objects.filter(
            campaign=campaign_obj).first()
        if campaign_analytics_obj:
            campaign_details["test_message_processed"] = str(
                campaign_analytics_obj.total_tested)
            campaign_details["test_message_sent"] = str(
                campaign_analytics_obj.test_message_sent)
            campaign_details["test_message_unsuccessful"] = str(
                campaign_analytics_obj.test_message_unsuccessful)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_test_campaign_details_data: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})

    return campaign_details


def add_campaign_test_details(sheet, campaign_details):
    try:
        overall_details_bold_columns = []
        for value in OVERALL_TEST_DETAILS_SHEET_COLUMNS_LIST[:6]:
            cell = WriteOnlyCell(sheet, value=value)
            cell.font = bold
            overall_details_bold_columns.append(cell)

        sheet.append(overall_details_bold_columns[:6])
        sheet.append([campaign_details["bot_name"], campaign_details["campaign_name"], campaign_details["whatsapp_bsp_name"],
                     campaign_details["create_datetime"], campaign_details["source"], campaign_details["time_zone"]])
        sheet.append([])

        cell = WriteOnlyCell(sheet, value="Test Messages")
        cell.font = bold
        sheet.append([cell])
        sheet.append(OVERALL_TEST_DETAILS_SHEET_COLUMNS_LIST[-3:])
        sheet.append([campaign_details["test_message_processed"],
                     campaign_details["test_message_sent"], campaign_details["test_message_unsuccessful"]])

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_campaign_test_details: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def add_whatsapp_test_sheet_columns(sheet):
    test_detailed_columns = []
    for value in WHATSAPP_TEST_AUDIENCE_SHEET_COLUMNS_LIST:
        cell = WriteOnlyCell(sheet, value=value)
        cell.font = bold
        test_detailed_columns.append(cell)

    sheet.append(test_detailed_columns)


def add_test_audience_details(audience_log_obj, sheet, masking_enabled, whatsapp_bsp_name):
    try:
        audience_details = get_audience_details_wtsp_reports(
            audience_log_obj, False)

        mobile_number = get_mobile_number(
            audience_log_obj['audience__audience_id'], False, masking_enabled)

        _, status_message, issue, failure_reason = add_status_for_bsp_reports(
            whatsapp_bsp_name, audience_log_obj)

        attachment_url = ''
        audience_obj_record = json.loads(audience_log_obj['audience__record'])
        if isinstance(audience_obj_record, dict):
            attachment_url = audience_obj_record.get('media_url', '')
        elif isinstance(audience_obj_record, list):
            attachment_url = json.loads(audience_log_obj['audience__record'])[
                -1] if json.loads(audience_log_obj['audience__record']) else ''

        if attachment_url:
            cell = WriteOnlyCell(sheet, value=attachment_url)
            cell.hyperlink = attachment_url
            cell.style = "Hyperlink"
            attachment_url = cell
        else:
            attachment_url = '-'

        request = json.loads(audience_log_obj['request'])
        template = request.get('template', {})
        template_name = template.get('name', '-')
        template_type = template.get('components', [{}])[0].get(
            'parameters', [{}])[0].get('type', '-')

        audience_details_list = [mobile_number, audience_details["recepient_id"], template_name, template_type, audience_details["sent_datetime"], audience_details["delivered_datetime"], audience_details["read_datetime"],
                                 audience_details["replied_datetime"], audience_details["quick_reply"], status_message, issue, failure_reason, attachment_url, audience_details["message_payload"], audience_details["response_body"]]

        sheet.append(audience_details_list)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_test_audience_details: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'Campaign'})


def get_zip_file_path(file_path, export_zip_file_path):
    try:
        zip_obj = ZipFile(settings.BASE_DIR + '/' +
                          export_zip_file_path, 'w')

        for file_path_value in file_path:
            try:
                zip_obj.write(settings.MEDIA_ROOT +
                              file_path_value, basename(file_path_value))
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("Campaign Report Datadump Zip! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'Campaign'})
                pass

        zip_obj.close()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("get_zip_file_path: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'Campaign'})

    return export_zip_file_path
