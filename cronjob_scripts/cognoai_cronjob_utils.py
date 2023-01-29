from datetime import datetime
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from cronjob_scripts.cron_log_manager import CronLogManager, log_cron_error
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses

import os
import sys

LOG_FOLDER = os.path.join(settings.BASE_DIR, 'log/cron/')
cron_log_manager_obj = CronLogManager()


def create_cronjob_start_log(file_name):
    try:
        prev_record_obj = cron_log_manager_obj.get_prev_record(file_name)
        if prev_record_obj and prev_record_obj["end_time"] == None:
            send_cron_already_running_email(file_name, prev_record_obj["start_time"])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_cron_error("create_cronjob_start_log", e, exc_tb.tb_lineno)

    log_obj_id = None
    try:
        log_obj_id = cron_log_manager_obj.create_start_cron_log(file_name)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_cron_error("create_cronjob_start_log", e, exc_tb.tb_lineno)

    return log_obj_id


def create_cronjob_end_log(log_obj_id):
    cron_log_manager_obj.create_end_cron_log(log_obj_id)


def send_cron_report_over_email(cron_last_run_time, file_name, message):

    def send_email(from_email_id, email_ids, message_as_string, from_email_id_password):
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
        server.sendmail(from_email_id, email_ids, message_as_string)
        # Close session
        server.quit()

    try:
        emails = settings.CRONJOB_REPORT_EMAIL

        console_config = get_developer_console_settings()
        if console_config:
            emails = console_config.get_cronjob_report_email()

        if len(emails) == 0:
            return

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
                    Dear Team,
                </p>
                <p>
                    {}
                </p>
                <p>
                    Please check the complete log in <b>{}</b> file on server.
                </p>"""

        body += console_config.custom_report_template_signature

        body += """</div></body>"""

        cron_error_file_path = LOG_FOLDER + "cron_error.log"
        server_name = settings.EASYCHAT_DOMAIN
        to_email_id = emails[0]

        body = body.format(message, cron_error_file_path)
        subject = "Alert: Cronjob failed on {}".format(server_name)
        cc = ",".join(emails[1:])

        send_email_to_customer_via_awsses(to_email_id, subject, body, cc=cc)
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_cron_error("send_cron_report_over_email", e, exc_tb.tb_lineno)


def send_cron_fail_email(cron_file_name, cron_last_run_time, error_message):
    try:
        if check_mail_already_sent(cron_file_name):
            return

        if cron_last_run_time is not None:
            cron_last_run_time = cron_last_run_time.strftime("%d %b %Y, %I:%M:%S %p")

        message = "Cronjob for file <b>{}</b> has been failed.<br>Last execution time: <b>{}</b>."
        message = message.format(cron_file_name, cron_last_run_time)
        message += "<pre style='background: black; color: white; padding: 2em 1em;'>" + error_message + "</pre>"

        try:
            send_cron_report_over_email(cron_last_run_time, cron_file_name, message)
        except Exception as e:
            print(e)

        # Add email send report
        create_email_sent_record(cron_file_name)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_cron_error("send_cron_fail_email", e, exc_tb.tb_lineno)


def send_cron_already_running_email(cron_file_name, cron_last_run_time):
    try:
        if check_mail_already_sent(cron_file_name):
            return

        if cron_last_run_time is not None:
            cron_last_run_time = cron_last_run_time.strftime("%d %b %Y, %I:%M:%S %p")

        message = "Second instance of the cronjob for file <b>{}</b> has started running but previous instance is not finished yet.<br>"
        message += "Last execution time: <b>{}</b>"
        message = message.format(cron_file_name, cron_last_run_time)

        try:
            send_cron_report_over_email(cron_last_run_time, cron_file_name, message)
        except Exception as e:
            print(e)

        # Add email send report
        create_email_sent_record(cron_file_name)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_cron_error("send_cron_already_running_email", e, exc_tb.tb_lineno)


def send_cron_not_running_email(cron_file_name, cron_last_run_time):
    try:
        if check_mail_already_sent(cron_file_name):
            return

        if cron_last_run_time is not None:
            cron_last_run_time = cron_last_run_time.strftime("%d %b %Y, %I:%M:%S %p")

        message = ""
        if cron_last_run_time is None:
            message = "Cronjob for file <b>{}</b> didn't run two times in a row."
            message = message.format(cron_file_name)
        else:
            message = "Cronjob for file <b>{}</b> didn't run since <b>{}</b>"
            message = message.format(cron_file_name, cron_last_run_time)

        try:
            send_cron_report_over_email(cron_last_run_time, cron_file_name, message)
        except Exception as e:
            print(e)

        # Add email send report
        create_email_sent_record(cron_file_name)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_cron_error("send_cron_not_running_email", e, exc_tb.tb_lineno)


def create_email_sent_record(cron_file_name):
    try:
        cron_log_manager_obj.create_email_sent_log(cron_file_name)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_cron_error("create_email_sent_record", e, exc_tb.tb_lineno)


def check_mail_already_sent(file_name):
    try:
        last_mail_sent_time = cron_log_manager_obj.get_email_sent_time(file_name)
        if last_mail_sent_time is None:
            return False

        current_time = datetime.now()
        total_seconds = (current_time - last_mail_sent_time).total_seconds()
        if total_seconds >= 3600:
            return False
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_cron_error("check_mail_already_sent", e, exc_tb.tb_lineno)


def send_cron_error_report(error_list, function_name, file_name):
    '''
    Send cron error report via email
        Parameters:
            error_list (list): List of error objects
            error objects (list): [error, line_number]
    '''

    try:
        if len(error_list) == 0:
            return

        current_time = datetime.now()
        error_message = ""
        for error_obj in error_list:
            error_message += "[{}] Error {} - {}: {} at {}\n".format(
                current_time, file_name, function_name, error_obj[0], error_obj[1])

        send_cron_fail_email(file_name, current_time, error_message)

        cron_error_file = LOG_FOLDER + "cron_error.log"
        with open(cron_error_file, 'a') as file:
            file.write(error_message)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log_cron_error("send_cron_error_report", e, exc_tb.tb_lineno)
