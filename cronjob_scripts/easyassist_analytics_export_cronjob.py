import os
import sys
import json
import smtplib
import base64

from xlwt import Workbook
from EasyAssistApp.models import *
from EasyAssistApp.utils import logger, \
    update_inbound_analytics_model, update_outbound_analytics_model, update_reverse_analytics_model, \
    get_inbound_analytics_data_dump, get_outbound_analytics_data_dump, get_reverse_analytics_data_dump, \
    get_general_analytics_data_dump, update_outbound_analytics_droplink_model, get_list_agents_under_admin, \
    create_excel_easyassist_repeated_customers_outbound, create_excel_easyassist_repeated_customers, \
    create_excel_easyassist_unique_customers, create_excel_easyassist_unique_customers_outbound, get_generated_link_data_dump, \
    create_excel_easyassist_capture_leads

from EasyAssistApp.utils_cronjob import get_easyassist_cronjob_tracker_obj, create_easyassist_cronjob_tracker_obj, \
    delete_easyassist_cronjob_tracker_obj, is_cronjob_tracker_object_expired, delete_and_create_cron_tracker_obj

from EasyAssistApp.proxy_cobrowse_analytics_utils import update_outbound_proxy_analytics_model, \
    get_outbound_proxy_analytics_data_dump

from EasyAssistApp.send_email import send_analytics_mail_to_customer, send_no_data_found_email

from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses
from DeveloperConsoleApp.constants import GENERAL_LOGIN_LOGO

from cronjob_scripts.cognoai_cronjob_utils import send_cron_error_report

from zipfile import ZipFile
from datetime import datetime, timedelta
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pytz

from os import path
from os.path import basename


def send_gmail(FROM, TO, message_as_string, PASSWORD):
    try:
        # # The actual sending of the e-mail
        server = smtplib.SMTP('smtp.gmail.com:587')
        # Credentials (if needed) for sending the mail
        password = PASSWORD
        # Start tls handshaking
        server.starttls()
        # Login to server
        server.login(FROM, password)
        # Send mail
        server.sendmail(FROM, TO, message_as_string)
        # Close session
        server.quit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_gmail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def get_file_download_path(file_relative_path, access_token):

    file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
        file_path="/" + file_relative_path, is_public=True, access_token=access_token)

    return 'easy-assist/download-file/' + str(file_access_management_obj.key)


def send_cron_error_report_utils(error_list, function_name):
    try:
        file_name = "easyassist_analytics_export_cronjob"
        send_cron_error_report(error_list, function_name, file_name)
    except Exception as e:
        print(e)


def cronjob():
    
    easyassist_cronjob_tracker_obj = get_easyassist_cronjob_tracker_obj(EXPORT_ANALYTICS_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
    if easyassist_cronjob_tracker_obj:
        if is_cronjob_tracker_object_expired(easyassist_cronjob_tracker_obj):
            delete_and_create_cron_tracker_obj(
                EXPORT_ANALYTICS_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
        else:
            logger.info("easyassist_analytics_export_cronjob is already running!",
                        extra={'AppName': 'EasyAssist'})
            return
    else:
        create_easyassist_cronjob_tracker_obj(EXPORT_ANALYTICS_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
    
    update_todays_analytics_cronjob()
    create_excel_inbound_analytics_cronjob()
    create_excel_outbound_analytics_cronjob()
    create_excel_reverse_analytics_cronjob()
    create_excel_general_analytics_cronjob()
    create_excel_inbound_unique_customers_cronjob()
    create_excel_inbound_repeated_customers_cronjob()
    create_excel_reverse_unique_customers_cronjob()
    create_excel_reverse_repeated_customers_cronjob()
    create_excel_outbound_unique_customers_cronjob()
    create_excel_outbound_repeated_customers_cronjob()
    create_excel_outbound_captured_leads_cronjob()
    create_excel_outbound_proxy_analytics_cronjob()
    create_excel_gdl_generated_links_cronjob()
    delete_easyassist_cronjob_tracker_obj(EXPORT_ANALYTICS_CRONJOB_CONSTANT, EasyAssistCronjobTracker)


def update_todays_analytics_cronjob():
    cron_error_list = []
    try:
        today_date = datetime.now() - timedelta(days=1)
        today_date = today_date.date()
        update_inbound_analytics_model(
            CobrowseDateWiseInboundAnalytics, CobrowseIO, EasyAssistCustomer, CobrowseAccessToken, today_date)

        update_outbound_analytics_model(
            CobrowseDateWiseOutboundAnalytics, CobrowseIO, CobrowseAccessToken, today_date)

        update_reverse_analytics_model(
            CobrowseDateWiseReverseAnalytics, CobrowseIO, CobrowseAccessToken, today_date)

        update_outbound_analytics_droplink_model(
            CobrowseDateWiseOutboundDroplinkAnalytics, CobrowseIO, CobrowseAccessToken, CobrowseDropLink, today_date)

        update_outbound_proxy_analytics_model(today_date, CobrowseDateWiseOutboundProxyAnalytics, CobrowseIO,
                                              CobrowseAccessToken, CobrowseDropLink, CobrowseIOInvitedAgentsDetails,
                                              CobrowseIOTransferredAgentsLogs)
            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
        logger.error("update_todays_analytics_cronjob: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "update_todays_analytics_cronjob")


def create_excel_inbound_analytics_cronjob():
    cron_error_list = []
    try:
        date_format = "%Y-%m-%d"

        try:
            print("create_excel_inbound_analytics_cronjob")

            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/InboundAnalytics/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT +
                            'EasyAssistApp/InboundAnalytics/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    if agent.role not in ["admin", "supervisor", "admin_ally"] and agent.is_switch_allowed == False:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/InboundAnalytics/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT +
                                    'EasyAssistApp/InboundAnalytics/' + str(agent.user.username))

                    # Check whether file exist for last 1, 7 and 30 days. If not create an excel file for the same.
                    date_format = "%Y-%m-%d"
                    for day in [1, 7, 30]:
                        start_date = datetime.now() - timedelta(days=day)
                        start_date = start_date.strftime(date_format)
                        end_date = datetime.now() - timedelta(days=1)
                        end_date = end_date.strftime(date_format)

                        file_path = settings.SECURE_MEDIA_ROOT + "EasyAssistApp/InboundAnalytics/" + \
                            str(agent.user.username) + \
                            "/inbound_analytics_" + \
                            str(start_date) + "-" + str(end_date) + ".xls"

                        if not os.path.exists(file_path):
                            requested_data = {
                                "startdate": start_date,
                                "enddate": end_date,
                            }
                            get_inbound_analytics_data_dump(
                                requested_data, agent, CobrowseDateWiseInboundAnalytics, CobrowseDateWiseOutboundDroplinkAnalytics)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("Inbound Analytics history Datadump %s %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Inbound Analytics Datadump! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="inbound-analytics").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]
                email_str = filter_param["email"]

                export_file_path = get_inbound_analytics_data_dump(
                    filter_param, export_date_request.agent, CobrowseDateWiseInboundAnalytics, CobrowseDateWiseOutboundDroplinkAnalytics)
                
                email_list = [email.strip()
                              for email in email_str.split(",") if email != ""]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                file_path = "EasyAssistApp/InboundAnalytics/" + str(export_date_request.agent.user.username) + \
                    "/inbound_analytics_" + \
                    str(start_date) + "-" + str(end_date) + '.xls'
                file_path = settings.SECURE_MEDIA_ROOT + file_path

                if not os.path.exists(file_path):
                    continue
                
                export_download_path = get_file_download_path(export_file_path[1:], export_date_request.agent.get_access_token_obj())
                
                username = export_date_request.agent.user.username
                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                for email_id in email_list:
                    send_analytics_mail_to_customer(
                        email_id, start_date, end_date, username, "Inbound", export_download_path)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Inbound Analytics %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_excel_inbound_analytics_cronjob")


def create_excel_outbound_analytics_cronjob():
    cron_error_list = []
    try:
        date_format = "%Y-%m-%d"

        try:
            print("create_excel_outbound_analytics_cronjob")

            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/OutboundAnalytics/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT +
                            'EasyAssistApp/OutboundAnalytics/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    if agent.role not in ["admin", "supervisor", "admin_ally"] and agent.is_switch_allowed == False:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/OutboundAnalytics/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT +
                                    'EasyAssistApp/OutboundAnalytics/' + str(agent.user.username))

                    # Check whether file exist for last 1, 7 and 30 days. If not create an excel file for the same.
                    date_format = "%Y-%m-%d"
                    for day in [1, 7, 30]:
                        start_date = datetime.now() - timedelta(days=day)
                        start_date = start_date.strftime(date_format)
                        end_date = datetime.now() - timedelta(days=1)
                        end_date = end_date.strftime(date_format)

                        file_path = settings.SECURE_MEDIA_ROOT + "EasyAssistApp/OutboundAnalytics/" + \
                            str(agent.user.username) + \
                            "/outbound_analytics_" + \
                            str(start_date) + "-" + str(end_date) + ".xls"

                        if not os.path.exists(file_path):
                            requested_data = {
                                "startdate": start_date,
                                "enddate": end_date,
                            }
                            get_outbound_analytics_data_dump(
                                requested_data, agent, CobrowseDateWiseOutboundAnalytics)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("Outbound Analytics history Datadump %s %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Outbound Analytics Datadump %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="outbound-analytics").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]
                email_str = filter_param["email"]

                export_file_path = get_outbound_analytics_data_dump(
                    filter_param, export_date_request.agent, CobrowseDateWiseOutboundAnalytics)
                
                email_list = [email.strip()
                              for email in email_str.split(",") if email != ""]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                file_path = "EasyAssistApp/OutboundAnalytics/" + str(export_date_request.agent.user.username) + \
                    "/outbound_analytics_" + \
                    str(start_date) + "-" + str(end_date) + '.xls'
                file_path = settings.SECURE_MEDIA_ROOT + file_path

                if not os.path.exists(file_path):
                    continue

                export_download_path = get_file_download_path(export_file_path[1:], export_date_request.agent.get_access_token_obj())
                
                username = export_date_request.agent.user.username
                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                for email_id in email_list:
                    send_analytics_mail_to_customer(
                        email_id, start_date, end_date, username, "Outbound", export_download_path)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Outbound Analytics %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_excel_outbound_analytics_cronjob")


def create_excel_reverse_analytics_cronjob():
    cron_error_list = []
    try:
        date_format = "%Y-%m-%d"

        try:
            print("create_excel_reverse_analytics_cronjob")

            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/ReverseAnalytics/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT +
                            'EasyAssistApp/ReverseAnalytics/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    if agent.role not in ["admin", "supervisor", "admin_ally"] and agent.is_switch_allowed == False:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/ReverseAnalytics/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT +
                                    'EasyAssistApp/ReverseAnalytics/' + str(agent.user.username))

                    # Check whether file exist for last 1, 7 and 30 days. If not create an excel file for the same.
                    date_format = "%Y-%m-%d"
                    for day in [1, 7, 30]:
                        start_date = datetime.now() - timedelta(days=day)
                        start_date = start_date.strftime(date_format)
                        end_date = datetime.now() - timedelta(days=1)
                        end_date = end_date.strftime(date_format)

                        file_path = settings.SECURE_MEDIA_ROOT + "EasyAssistApp/ReverseAnalytics/" + \
                            str(agent.user.username) + \
                            "/reverse_analytics_" + \
                            str(start_date) + "-" + str(end_date) + ".xls"

                        if not os.path.exists(file_path):
                            requested_data = {
                                "startdate": start_date,
                                "enddate": end_date,
                            }
                            get_reverse_analytics_data_dump(
                                requested_data, agent, CobrowseDateWiseReverseAnalytics)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("Reverse Analytics history Datadump %s %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Reverse Analytics Datadump %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="reverse-analytics").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]
                email_str = filter_param["email"]

                export_file_path = get_reverse_analytics_data_dump(
                    filter_param, export_date_request.agent, CobrowseDateWiseReverseAnalytics)
                email_list = [email.strip()
                              for email in email_str.split(",") if email != ""]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                file_path = "EasyAssistApp/ReverseAnalytics/" + str(export_date_request.agent.user.username) + \
                    "/reverse_analytics_" + \
                    str(start_date) + "-" + str(end_date) + '.xls'
                file_path = settings.SECURE_MEDIA_ROOT + file_path

                if not os.path.exists(file_path):
                    continue
                
                export_download_path = get_file_download_path(export_file_path[1:], export_date_request.agent.get_access_token_obj())
                
                username = export_date_request.agent.user.username
                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                for email_id in email_list:
                    send_analytics_mail_to_customer(
                        email_id, start_date, end_date, username, "Reverse", export_download_path)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Reverse Analytics %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_excel_reverse_analytics_cronjob")


def create_excel_general_analytics_cronjob():
    cron_error_list = []
    try:
        date_format = "%Y-%m-%d"

        try:
            print("create_excel_general_analytics_cronjob")

            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/GeneralAnalytics/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT +
                            'EasyAssistApp/GeneralAnalytics/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if agent.get_access_token_obj() == None:
                        continue

                    if agent.role not in ["admin", "supervisor", "admin_ally"] and agent.is_switch_allowed == False:
                        continue

                    # Check whether directory for given access token exists or not: If not create one
                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/GeneralAnalytics/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT +
                                    'EasyAssistApp/GeneralAnalytics/' + str(agent.user.username))

                    # Check whether file exist for last 1, 7 and 30 days. If not create an excel file for the same.
                    date_format = "%Y-%m-%d"
                    for day in [1, 7, 30]:
                        start_date = datetime.now() - timedelta(days=day)
                        start_date = start_date.strftime(date_format)
                        end_date = datetime.now() - timedelta(days=1)
                        end_date = end_date.strftime(date_format)

                        file_path = settings.SECURE_MEDIA_ROOT + "EasyAssistApp/GeneralAnalytics/" + \
                            str(agent.user.username) + \
                            "/general_analytics_" + \
                            str(start_date) + "-" + str(end_date) + ".xls"

                        if not os.path.exists(file_path):
                            requested_data = {
                                "startdate": start_date,
                                "enddate": end_date,
                            }
                            get_general_analytics_data_dump(
                                requested_data, agent, CobrowseDateWiseInboundAnalytics, CobrowseDateWiseOutboundAnalytics, CobrowseDateWiseOutboundDroplinkAnalytics)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("General Analytics history Datadump %s %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("General Analytics Datadump %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="general-analytics").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]
                email_str = filter_param["email"]
                export_file_path = get_general_analytics_data_dump(
                    filter_param, export_date_request.agent, CobrowseDateWiseInboundAnalytics, CobrowseDateWiseOutboundAnalytics, CobrowseDateWiseOutboundDroplinkAnalytics)
                
                email_list = [email.strip()
                              for email in email_str.split(",") if email != ""]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                file_path = "EasyAssistApp/GeneralAnalytics/" + str(export_date_request.agent.user.username) + \
                    "/general_analytics_" + \
                    str(start_date) + "-" + str(end_date) + '.xls'
                file_path = settings.SECURE_MEDIA_ROOT + file_path

                if not os.path.exists(file_path):
                    continue

                export_download_path = get_file_download_path(export_file_path[1:], export_date_request.agent.get_access_token_obj())
                
                username = export_date_request.agent.user.username
                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                for email_id in email_list:
                    send_analytics_mail_to_customer(
                        email_id, start_date, end_date, username, "General", export_download_path)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("General Analytics %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_excel_general_analytics_cronjob")


def create_excel_inbound_unique_customers_cronjob():
    cron_error_list = []
    try:
        date_format = "%d/%m/%Y"
        print("Inside create_excel_inbound_unique_customers_cronjob")

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="inbound-unique-customers").iterator():
            try:
                agent = export_date_request.agent
                if agent.get_access_token_obj() == None:
                    continue
                access_token_obj = agent.get_access_token_obj()

                if agent.role in ["admin", "admin_ally"]:
                    agent_objs = get_list_agents_under_admin(
                        agent, is_active=None, is_account_active=None)
                else:
                    agent_objs = list(agent.agents.all())

                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["start_date"]
                end_date = filter_param["end_date"]

                data = {
                    "start_date": start_date,
                    "end_date": end_date,
                }

                email_list = filter_param["email"]
                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                cobrowse_io_objs = CobrowseIO.objects.filter(is_test=False, access_token=access_token_obj,
                                                             request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                    request_datetime__date__gte=start_date, request_datetime__date__lte=end_date).filter(
                    is_lead=False, agent__in=agent_objs)

                unique_mobile_numbers = cobrowse_io_objs.values("mobile_number").annotate(
                    customer_count=Count('mobile_number')).filter(customer_count__lte=1)
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    mobile_number__in=unique_mobile_numbers.values_list('mobile_number', flat=True))
                export_file_path = create_excel_easyassist_unique_customers(
                    "inbound", agent, cobrowse_io_objs, access_token_obj, data)
                
                if not os.path.exists(export_file_path):
                    continue

                export_download_path = get_file_download_path("/" + export_file_path, export_date_request.agent.get_access_token_obj())
                
                username = export_date_request.agent.user.username
                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                if email_list:
                    for email_id in email_list:
                        send_analytics_mail_to_customer(
                            email_id, start_date, end_date, username, "Inbound", export_download_path, "Unique Customers")

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Inbound Unique Customers %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_excel_inbound_unique_customers_cronjob")


def create_excel_inbound_repeated_customers_cronjob():
    cron_error_list = []
    try:
        date_format = "%d/%m/%Y"
        print("Inside create_excel_inbound_repeated_customers_cronjob")

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="inbound-repeated-customers").iterator():
            try:
                agent = export_date_request.agent
                if agent.get_access_token_obj() == None:
                    continue
                access_token_obj = agent.get_access_token_obj()
                if agent.role in ["admin", "admin_ally"]:
                    agent_objs = get_list_agents_under_admin(
                        agent, is_active=None, is_account_active=None)
                else:
                    agent_objs = list(agent.agents.all())

                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["start_date"]
                end_date = filter_param["end_date"]

                data = {
                    "start_date": start_date,
                    "end_date": end_date,
                }

                email_list = filter_param["email"]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                cobrowse_io_objs = CobrowseIO.objects.filter(is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                    request_datetime__date__gte=start_date, request_datetime__date__lte=end_date).filter(
                    is_lead=False, agent__in=agent_objs)
                repeated_mobile_numbers = cobrowse_io_objs.values("mobile_number").annotate(
                    customer_count=Count('mobile_number')).filter(customer_count__gt=1)
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    mobile_number__in=repeated_mobile_numbers.values_list('mobile_number', flat=True))
                export_file_path = create_excel_easyassist_repeated_customers(
                    "inbound", cobrowse_io_objs, agent, data)
                
                if not os.path.exists(export_file_path):
                    continue

                export_download_path = get_file_download_path("/" + export_file_path, export_date_request.agent.get_access_token_obj())
                username = export_date_request.agent.user.username
                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                if email_list:
                    for email_id in email_list:
                        send_analytics_mail_to_customer(
                            email_id, start_date, end_date, username, "Inbound", export_download_path, "Repeated Customers")

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Inbound Repeated Customers %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_excel_inbound_repeated_customers_cronjob")


def create_excel_reverse_unique_customers_cronjob():
    cron_error_list = []
    try:
        date_format = "%d/%m/%Y"
        print("Inside create_excel_reverse_unique_customers_cronjob")

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="reverse-unique-customers").iterator():
            try:
                agent = export_date_request.agent
                if agent.get_access_token_obj() == None:
                    continue
                access_token_obj = agent.get_access_token_obj()
                if agent.role in ["admin", "admin_ally"]:
                    agent_objs = get_list_agents_under_admin(
                        agent, is_active=None, is_account_active=None)
                else:
                    agent_objs = list(agent.agents.all())
                    
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["start_date"]
                end_date = filter_param["end_date"]

                data = {
                    "start_date": start_date,
                    "end_date": end_date,
                }

                email_list = filter_param["email"]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                cobrowse_io_objs = CobrowseIO.objects.filter(is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=True).filter(
                    request_datetime__date__gte=start_date, request_datetime__date__lte=end_date).filter(
                    is_lead=False, agent__in=agent_objs)

                unique_mobile_numbers = cobrowse_io_objs.values("mobile_number").annotate(
                    customer_count=Count('mobile_number')).filter(customer_count__lte=1)
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    mobile_number__in=unique_mobile_numbers.values_list('mobile_number', flat=True))
                export_file_path = create_excel_easyassist_unique_customers(
                    "reverse", agent, cobrowse_io_objs, access_token_obj, data)
                
                if not os.path.exists(export_file_path):
                    continue

                export_download_path = get_file_download_path("/" + export_file_path, export_date_request.agent.get_access_token_obj())

                username = export_date_request.agent.user.username
                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                if email_list:
                    for email_id in email_list:
                        send_analytics_mail_to_customer(
                            email_id, start_date, end_date, username, "Reverse", export_download_path, "Unique Customers")

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Reverse Unique Customers %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_excel_reverse_unique_customers_cronjob")


def create_excel_reverse_repeated_customers_cronjob():
    cron_error_list = []
    try:
        date_format = "%d/%m/%Y"
        print("Inside create_excel_reverse_repeated_customers_cronjob")

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="reverse-repeated-customers").iterator():
            try:
                agent = export_date_request.agent
                if agent.get_access_token_obj() == None:
                    continue
                access_token_obj = agent.get_access_token_obj()

                if agent.role in ["admin", "admin_ally"]:
                    agent_objs = get_list_agents_under_admin(
                        agent, is_active=None, is_account_active=None)
                else:
                    agent_objs = list(agent.agents.all())

                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["start_date"]
                end_date = filter_param["end_date"]

                data = {
                    "start_date": start_date,
                    "end_date": end_date,
                }

                email_list = filter_param["email"]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                cobrowse_io_objs = CobrowseIO.objects.filter(is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=True).filter(
                    request_datetime__date__gte=start_date, request_datetime__date__lte=end_date).filter(
                    is_lead=False, agent__in=agent_objs).filter(~Q(mobile_number=""))
                repeated_mobile_numbers = cobrowse_io_objs.values("mobile_number").annotate(
                    customer_count=Count('mobile_number')).filter(customer_count__gt=1)
                cobrowse_io_objs = cobrowse_io_objs.filter(
                    mobile_number__in=repeated_mobile_numbers.values_list('mobile_number', flat=True))
                export_file_path = create_excel_easyassist_repeated_customers(
                    "reverse", cobrowse_io_objs, agent, data)
                
                if not os.path.exists(export_file_path):
                    continue

                export_download_path = get_file_download_path("/" + export_file_path, export_date_request.agent.get_access_token_obj())
                username = export_date_request.agent.user.username
                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                if email_list:
                    for email_id in email_list:
                        send_analytics_mail_to_customer(
                            email_id, start_date, end_date, username, "Reverse", export_download_path, "Repeated Customers")

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Reverse Repeated Customers %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_excel_reverse_repeated_customers_cronjob")


def create_excel_outbound_unique_customers_cronjob():
    cron_error_list = []
    try:
        date_format = "%d/%m/%Y"
        print("Inside create_excel_outbound_unique_customers_cronjob")

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="outbound-unique-customers").iterator():
            try:
                agent = export_date_request.agent
                if agent.get_access_token_obj() == None:
                    continue
                access_token_obj = agent.get_access_token_obj()
                if agent.role in ["admin", "admin_ally"]:
                    agent_objs = get_list_agents_under_admin(
                        agent, is_active=None, is_account_active=None)
                else:
                    agent_objs = list(agent.agents.all())
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["start_date"]
                end_date = filter_param["end_date"]
                email_list = filter_param["email"]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                data = {
                    "start_date": start_date,
                    "end_date": end_date,
                }

                cobrowse_io_objs = CobrowseIO.objects.filter(is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                    request_datetime__date__gte=start_date, request_datetime__date__lte=end_date).filter(
                    is_lead=True, agent__in=agent_objs)

                unique_identifier_field = access_token_obj.search_fields.filter(
                    unique_identifier=True)

                captured_data = CobrowseCapturedLeadData.objects.filter(search_field__in=unique_identifier_field, agent_searched=True).values("primary_value").annotate(
                    value_count=Count('primary_value')).filter(value_count=1).values_list("primary_value", flat=True)

                unique_cobrowse_io_objs = cobrowse_io_objs.filter(
                    session_id__in=CobrowseCapturedLeadData.objects.filter(primary_value__in=captured_data, agent_searched=True).values_list("session_id", flat=True))

                non_unique_identifier_field = access_token_obj.search_fields.filter(
                    unique_identifier=False)

                off_field_captured_data = CobrowseCapturedLeadData.objects.filter(
                    search_field__in=non_unique_identifier_field, agent_searched=True).values_list("session_id", flat=True)

                non_unique_captured_session = cobrowse_io_objs.filter(
                    session_id__in=off_field_captured_data)

                cobrowse_io_objs = unique_cobrowse_io_objs | non_unique_captured_session

                export_file_path = create_excel_easyassist_unique_customers_outbound(
                    cobrowse_io_objs, agent, access_token_obj, data)

                if not os.path.exists(export_file_path):
                    continue

                export_download_path = get_file_download_path("/" + export_file_path, export_date_request.agent.get_access_token_obj())

                username = export_date_request.agent.user.username
                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                if email_list:
                    for email_id in email_list:
                        send_analytics_mail_to_customer(
                            email_id, start_date, end_date, username, "Outbound", export_download_path, "Unique Customers")

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Outbound Unique Customers %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_excel_outbound_unique_customers_cronjob")


def create_excel_outbound_repeated_customers_cronjob():
    cron_error_list = []
    try:
        date_format = "%d/%m/%Y"
        print("Inside create_excel_outbound_repeated_customers_cronjob")

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="outbound-repeated-customers").iterator():
            try:
                agent = export_date_request.agent
                if agent.get_access_token_obj() == None:
                    continue
                access_token_obj = agent.get_access_token_obj()
                if agent.role in ["admin", "admin_ally"]:
                    agent_objs = get_list_agents_under_admin(
                        agent, is_active=None, is_account_active=None)
                else:
                    agent_objs = list(agent.agents.all())
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["start_date"]
                end_date = filter_param["end_date"]

                data = {
                    "start_date": start_date,
                    "end_date": end_date,
                }

                email_list = filter_param["email"]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                cobrowse_io_objs = CobrowseIO.objects.filter(is_test=False, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_archived=True, is_reverse_cobrowsing=False).filter(
                    request_datetime__date__gte=start_date, request_datetime__date__lte=end_date).filter(is_lead=True, agent__in=agent_objs)

                unique_identifier_field = access_token_obj.search_fields.filter(
                    unique_identifier=True)

                repeated_captured_data = CobrowseCapturedLeadData.objects.filter(search_field__in=unique_identifier_field, agent_searched=True).values(
                    "primary_value").annotate(value_count=Count('primary_value')).filter(value_count__gt=1).values_list("primary_value", flat=True)

                captured_data_session = CobrowseCapturedLeadData.objects.filter(
                    primary_value__in=repeated_captured_data, agent_searched=True).values_list("session_id", flat=True)

                cobrowse_io_objs = cobrowse_io_objs.filter(
                    session_id__in=captured_data_session)

                export_file_path = create_excel_easyassist_repeated_customers_outbound(
                    cobrowse_io_objs, agent, repeated_captured_data, captured_data_session, data)

                if not os.path.exists(export_file_path):
                    continue

                export_download_path = get_file_download_path("/" + export_file_path, export_date_request.agent.get_access_token_obj())
            
                username = export_date_request.agent.user.username
                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                if email_list:
                    for email_id in email_list:
                        send_analytics_mail_to_customer(
                            email_id, start_date, end_date, username, "Outbound", export_download_path, "Repeated Customers")

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Outbound Repeated Customers %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_excel_outbound_repeated_customers_cronjob")


def create_excel_outbound_captured_leads_cronjob():
    cron_error_list = []
    try:
        print("create_excel_outbound_captured_leads_cronjob")

        date_format = "%d/%m/%Y"

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="outbound-captured-leads").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["start_date"]
                end_date = filter_param["end_date"]
                email_id_list = filter_param["email_id_list"]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                filter_param["start_date"] = start_date
                filter_param["end_date"] = end_date

                access_token_obj = export_date_request.agent.get_access_token_obj()
                cobrowse_io_objs = CobrowseIO.objects.filter(
                    is_test=False, is_archived=True, access_token=access_token_obj, request_datetime__date__gte=access_token_obj.go_live_date, is_reverse_cobrowsing=False, is_lead=True).filter(
                    request_datetime__date__gte=start_date, request_datetime__date__lte=end_date)

                file_path = create_excel_easyassist_capture_leads(
                    filter_param, cobrowse_io_objs, access_token_obj)

                if file_path is None:
                    continue

                if not os.path.exists(file_path):
                    continue
                    
                export_download_path = get_file_download_path("/" + file_path, export_date_request.agent.get_access_token_obj())

                username = export_date_request.agent.user.username

                for email_id in email_id_list:
                    try:
                        send_analytics_mail_to_customer(
                            email_id, start_date, end_date, username, "Outbound", export_download_path, "Captured Leads")
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                        logger.error("Outbound Captured Leads %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'EasyAssist'})

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Outbound Captured Leads %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_excel_outbound_captured_leads_cronjob")


def create_excel_outbound_proxy_analytics_cronjob():
    cron_error_list = []
    try:
        date_format = "%Y-%m-%d"

        try:
            print("create_excel_outbound_proxy_analytics_cronjob")

            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/OutboundAnalytics/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT +
                            'EasyAssistApp/OutboundAnalytics/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True)
            for agent in agent_objs.iterator():
                try:
                    if not agent.get_access_token_obj():
                        continue

                    if agent.role not in ["admin", "supervisor", "admin_ally"] and not agent.is_switch_allowed:
                        continue

                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/OutboundAnalytics/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT +
                                    'EasyAssistApp/OutboundAnalytics/' + str(agent.user.username))

                    for day in [1, 7, 30]:
                        start_date = datetime.now() - timedelta(days=day)
                        start_date = start_date.strftime(date_format)
                        end_date = datetime.now() - timedelta(days=1)
                        end_date = end_date.strftime(date_format)

                        file_path = settings.SECURE_MEDIA_ROOT + "EasyAssistApp/OutboundAnalytics/" + \
                            str(agent.user.username) + \
                            "/outbound_proxy_analytics_" + \
                            str(start_date) + "-" + str(end_date) + ".xls"

                        if not os.path.exists(file_path):
                            requested_data = {
                                "startdate": start_date,
                                "enddate": end_date,
                            }
                            get_outbound_proxy_analytics_data_dump(
                                requested_data, agent, CobrowseDateWiseOutboundProxyAnalytics)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("Outbound Proxy Analytics history Datadump %s %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("Outbound Analytics Datadump %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="outbound-proxy-analytics").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]
                email_str = filter_param["email"]

                export_file_path = get_outbound_proxy_analytics_data_dump(
                    filter_param, export_date_request.agent, CobrowseDateWiseOutboundProxyAnalytics)
                
                file_path = settings.SECURE_MEDIA_ROOT + export_file_path

                if not os.path.exists(file_path):
                    continue

                export_download_path = get_file_download_path(export_file_path[1:], export_date_request.agent.get_access_token_obj())

                email_list = [email.strip()
                              for email in email_str.split(",") if email != ""]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                file_path = settings.SECURE_MEDIA_ROOT + file_path
                username = export_date_request.agent.user.username
                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                for email_id in email_list:
                    send_analytics_mail_to_customer(
                        email_id, start_date, end_date, username, "Outbound", export_download_path, "Proxy")

                export_date_request.is_completed = True
                export_date_request.save(update_fields=["is_completed"])
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("Outbound Proxy Analytics %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save(update_fields=["is_completed"])

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_excel_outbound_proxy_analytics_cronjob")


def create_excel_gdl_generated_links_cronjob():
    cron_error_list = []
    try:
        date_format = "%Y-%m-%d"

        try:
            print("create_excel_gdl_generated_links_cronjob")

            if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/InboundAnalytics/'):
                os.makedirs(settings.SECURE_MEDIA_ROOT +
                            'EasyAssistApp/InboundAnalytics/')

            agent_objs = CobrowseAgent.objects.filter(is_account_active=True).filter(~Q(role="agent"))
            for agent in agent_objs.iterator():
                try:
                    access_token_obj = agent.get_access_token_obj()
                    if not agent.get_access_token_obj():
                        continue

                    if not os.path.exists(settings.SECURE_MEDIA_ROOT + 'EasyAssistApp/InboundAnalytics/' + str(agent.user.username)):
                        os.makedirs(settings.SECURE_MEDIA_ROOT +
                                    'EasyAssistApp/InboundAnalytics/' + str(agent.user.username))

                    agent_list = [agent]
                    if agent.role in ["admin", "admin_ally"]:
                        agent_list = get_list_agents_under_admin(
                            agent, is_active=None, is_account_active=None)
                    else:
                        agent_list = list(agent.agents.all())

                    date_format = "%Y-%m-%d"
                    end_date = datetime.now() - timedelta(days=1)
                    end_date = end_date.strftime(date_format)
                    for day in [1, 7, 30]:
                        start_date = datetime.now() - timedelta(days=day)
                        start_date = start_date.strftime(date_format)

                        requested_data = {
                            "startdate": start_date,
                            "enddate": end_date,
                        }

                        drop_link_objs = CobrowseDropLink.objects.filter(agent__in=agent_list, generate_datetime__date__gte=access_token_obj.go_live_date).filter(
                            generate_datetime__date__gte=start_date, generate_datetime__date__lte=end_date, proxy_cobrowse_io=None).order_by("generate_datetime")

                        if drop_link_objs:
                            get_generated_link_data_dump(
                                requested_data, agent, CobrowseDropLink, drop_link_objs)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                    logger.error("create_excel_gdl_generated_links_cronjob %s %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
            logger.error("create_excel_gdl_generated_links_cronjob %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyAssist'})

        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="droplink-urls-generated").iterator():
            try:
                filter_param = json.loads(export_date_request.filter_param)
                start_date = filter_param["startdate"]
                end_date = filter_param["enddate"]
                email_str = filter_param["email"]

                agent_list = []
                if export_date_request.agent.role in ["admin", "admin_ally"]:
                    agent_list = get_list_agents_under_admin(
                        export_date_request.agent, is_active=None, is_account_active=None)
                else:
                    agent_list = list(export_date_request.agent.agents.all())

                go_live_date = export_date_request.agent.get_access_token_obj().go_live_date
                drop_link_objs = CobrowseDropLink.objects.filter(agent__in=agent_list, generate_datetime__date__gte=go_live_date).filter(
                    generate_datetime__date__gte=start_date, generate_datetime__date__lte=end_date, proxy_cobrowse_io=None).order_by("generate_datetime")

                email_list = [email.strip()
                              for email in email_str.split(",") if email != ""]

                start_date = datetime.strptime(start_date, date_format).date()
                end_date = datetime.strptime(end_date, date_format).date()

                username = export_date_request.agent.user.username
                start_date = datetime.strftime(start_date, "%d-%m-%Y")
                end_date = datetime.strftime(end_date, "%d-%m-%Y")

                requested_data = {
                    "startdate": start_date,
                    "enddate": end_date,
                }

                export_path = get_generated_link_data_dump(
                    requested_data, export_date_request.agent, CobrowseDropLink, drop_link_objs)
                if export_path == NO_DATA:
                    for email_id in email_list:
                        email_subject = email_subject = "EasyAssist Analytics | " + \
                            str(username)
                        send_no_data_found_email(
                            email_id, start_date, end_date, username, "drop link", email_subject)
                else:
                    file_download_path = get_file_download_path(export_path[1:], export_date_request.agent.get_access_token_obj())
                    for email_id in email_list:
                        send_analytics_mail_to_customer(
                            email_id, start_date, end_date, username, "Inbound", file_download_path, "Links Generated")

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("create_excel_gdl_generated_links_cronjob %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_excel_gdl_generated_links_cronjob")
