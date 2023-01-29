import sys
import logging
import smtplib

from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses

from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json

logger = logging.getLogger(__name__)


# def send_gmail(from_email, to_email, message_as_string, password):
#     try:
#         # # The actual sending of the e-mail
#         server = smtplib.SMTP('smtp.gmail.com:587')
#         # Start tls handshaking
#         server.starttls()
#         # Login to server
#         server.login(from_email, password)
#         # Send mail
#         server.sendmail(from_email, to_email, message_as_string)
#         # Close session
#         server.quit()
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("Error send_gmail %s at %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})


def send_password_over_email(email, name, password, platform_url):
    try:
        config_obj = get_developer_console_settings()
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
                Dear """ + name + """,
            </p>
            <p>
            Your password to login into Cogno Desk Console <a href=\"""" + platform_url + """\" target="_blank">""" + platform_url + """</a> for <b>User ID</b> '""" + email + """' is <b>""" + password + """</b>
            </p>

            <p>Kindly connect with us incase of any issue.</p>
            <p>&nbsp;</p>"""

        body += config_obj.custom_report_template_signature
        
        body += """</div></body>"""

        send_email_to_customer_via_awsses(email, "Cogno Desk Console - Access Management", body)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_password_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})


def send_agent_query_message(metadata):
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
            """ + metadata["agent_comment"] + """
        </div>

        </body>"""

        """With this function we send out our html email"""
        email = metadata["customer_email_id"]

        send_email_to_customer_via_awsses(email, "Update on your ticket - " + metadata["ticket_id"], body)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_agent_query_message %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyTMS'})
