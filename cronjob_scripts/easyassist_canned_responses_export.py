import sys

from EasyAssistApp.models import *
from EasyAssistApp.utils import logger, \
    get_canned_responses_data_dump, \
    get_admin_from_active_agent, \
    get_supervisors_list_under_admin

from EasyAssistApp.utils_cronjob import get_easyassist_cronjob_tracker_obj, \
    create_easyassist_cronjob_tracker_obj, \
    delete_easyassist_cronjob_tracker_obj, \
    is_cronjob_tracker_object_expired, \
    delete_and_create_cron_tracker_obj

from DeveloperConsoleApp.utils import send_email_to_customer_via_awsses

from cronjob_scripts.cognoai_cronjob_utils import send_cron_error_report

from django.conf import settings


def send_mail(from_email_id, to_emai_id, message_as_string, from_email_id_password):
    import smtplib
    # The actual sending of the e-mail
    server = smtplib.SMTP('smtp.gmail.com:587')
    # Credentials (if needed) for sending the mail
    password = from_email_id_password
    # Start tls handshaking
    server.starttls()
    # Login to server
    server.login(from_email_id, password)
    # Send mail
    server.sendmail(from_email_id, to_emai_id, message_as_string)
    # Close session
    server.quit()


def send_data_file_over_email(email, sender_name, report_type, email_subject, attachment_file_path):
    try:
        body = """
            <head>
              <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
              <title>Cogno AI</title>
              <style type="text/css" media="screen">
              </style>
            </head>
            <body>
                <div style="padding:1em;border:0.1em black solid;" class="container">
                    <p>
                        Dear {},
                    </p>
                    <p>
                        We have received a request to provide you with the EasyAssist {}. Please click on the link below to download the file.
                    </p>
                    <a href="{}/{}">click here</a>
                    <p>&nbsp;</p>
                    <p>Technology Development</p>
                    <p>Cogno AI</p>
                    <a href="https://getcogno.ai/">https://getcogno.ai/</a>
                </div>
            </body>
        """

        domain = settings.EASYCHAT_HOST_URL
        body = body.format(sender_name, report_type,
                           domain, attachment_file_path)

        send_email_to_customer_via_awsses(email, email_subject, body)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_data_file_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_cron_error_report_utils(error_list, function_name):
    try:
        file_name = "easyassist_canned_response_export"
        send_cron_error_report(error_list, function_name, file_name)
    except Exception as e:
        print(e)


def get_file_download_path(file_relative_path, access_token):

    file_access_management_obj = CobrowsingFileAccessManagement.objects.create(
        file_path="/" + file_relative_path, is_public=True, access_token=access_token)

    return 'easy-assist/download-file/' + str(file_access_management_obj.key)


def cronjob():

    easyassist_cronjob_tracker_obj = get_easyassist_cronjob_tracker_obj(
        EXPORT_CANNED_RESPONSE_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
    if easyassist_cronjob_tracker_obj:
        if is_cronjob_tracker_object_expired(easyassist_cronjob_tracker_obj):
            delete_and_create_cron_tracker_obj(
                EXPORT_CANNED_RESPONSE_CRONJOB_CONSTANT, EasyAssistCronjobTracker)
        else:
            logger.info("easyassist_canned_responses_export is already running!",
                        extra={'AppName': 'EasyAssist'})
            return
    else:
        create_easyassist_cronjob_tracker_obj(EXPORT_CANNED_RESPONSE_CRONJOB_CONSTANT, EasyAssistCronjobTracker)

    create_canned_response_export_cronjob()

    delete_easyassist_cronjob_tracker_obj(
        EXPORT_CANNED_RESPONSE_CRONJOB_CONSTANT, EasyAssistCronjobTracker)


def create_canned_response_export_cronjob():
    cron_error_list = []
    try:
        for export_date_request in EasyAssistExportDataRequest.objects.filter(is_completed=False, report_type="canned-response").iterator():
            try:
                if export_date_request.agent.role == "admin":
                    supervisors_obj = get_supervisors_list_under_admin(export_date_request.agent)
                    supervisors_obj.append(export_date_request.agent)
                elif export_date_request.agent.role == "supervisor":
                    admin_agent = get_admin_from_active_agent(
                        export_date_request.agent, CobrowseAgent)
                    supervisors_obj = [export_date_request.agent, admin_agent]
                else:
                    continue

                canned_responses_obj = LiveChatCannedResponse.objects.filter(
                    agent__in=supervisors_obj, access_token=export_date_request.agent.get_access_token_obj(), is_deleted=False)
                relative_file_path = get_canned_responses_data_dump(
                    export_date_request.agent, canned_responses_obj)
                file_download_path = get_file_download_path(
                    relative_file_path, export_date_request.agent.get_access_token_obj())

                username = export_date_request.agent.user.username

                email_id = export_date_request.agent.user.username
                
                email_subject = "EasyAssist Canned Responses | " + \
                    str(username)
                send_data_file_over_email(
                    email_id, username, "canned responses", email_subject, file_download_path)

                export_date_request.is_completed = True
                export_date_request.save()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                cron_error_list.append([str(e), str(exc_tb.tb_lineno)])
                logger.error("create_canned_response_export_cronjob! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyAssist'})
                export_date_request.is_completed = False
                export_date_request.save()

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        cron_error_list.append([str(exc), str(exc_tb.tb_lineno)])
        logger.error("cronjob: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

    send_cron_error_report_utils(
        cron_error_list, "create_canned_response_export_cronjob")
