import sys
import logging
import smtplib

from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


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
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def send_password_over_email(email, name, password, platform_url):
    try:
        global send_gmail
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
            Your password to login into Cobrowsing Console <a href=\"""" + platform_url + """\" target="_blank">""" + platform_url + """</a> for <b>User ID</b> '""" + email + """' is <b>""" + password + """</b>
            </p>

            <p>Kindly connect with us incase of any issue.</p>
            <p>&nbsp;</p>
            <p>Technology Development</p>
            <p>Cogno AI</p>
            <a href="https://getcogno.ai/">https://getcogno.ai/</a>
        </div>

        </body>"""

        """With this function we send out our html email"""
        to_emai_id = email
        # FROM = settings.EMAIL_HOST_USER
        # PASSWORD = settings.EMAIL_HOST_PASSWORD
        from_email_id = settings.EMAIL_HOST_USER
        from_email_id_password = settings.EMAIL_HOST_PASSWORD
        # Create message container - the correct MIME type is
        # multipart/alternative here!
        email_message = MIMEMultipart('alternative')
        email_message[
            'subject'] = "Cobrowsing Console - Access Management"
        email_message['To'] = email
        email_message['From'] = from_email_id
        email_message.preamble = """"""
        logger.info("Sending email to %s", email,
                    extra={'AppName': 'EasyAssistSalesforce'})
        # # Record the MIME type text/html.
        email_html_body = MIMEText(body, 'html')
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        email_message.attach(email_html_body)
        send_gmail(from_email_id, to_emai_id,
                   email_message.as_string(), from_email_id_password)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_password_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def send_drop_link_over_email(email, customer_name, agent_name, client_page_link, generated_link):
    try:
        global send_gmail
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
                Dear """ + customer_name + """,
            </p>
            <p>
            """ + agent_name + """ from our Customer Support Team would like to assist you to explore our website <a href=\"""" + client_page_link + """\" target="_blank">""" + client_page_link + """</a>
            <br>
            Please click on the link below and connect with the Agent for assistance:
            <br>
            <a href=\"""" + generated_link + """\" target="_blank">""" + generated_link + """</a>
            </p>

        </div>

        </body>"""

        """With this function we send out our html email"""
        to_emai_id = email
        # FROM = settings.EMAIL_HOST_USER
        # PASSWORD = settings.EMAIL_HOST_PASSWORD
        from_email_id = settings.EMAIL_HOST_USER
        from_email_id_password = settings.EMAIL_HOST_PASSWORD
        # Create message container - the correct MIME type is
        # multipart/alternative here!
        email_message = MIMEMultipart('alternative')
        email_message[
            'subject'] = "Cobrowsing Drop Link"
        email_message['To'] = email
        email_message['From'] = from_email_id
        email_message.preamble = """"""
        logger.info("Sending email to %s", email,
                    extra={'AppName': 'EasyAssistSalesforce'})
        # # Record the MIME type text/html.
        email_html_body = MIMEText(body, 'html')
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        email_message.attach(email_html_body)
        send_gmail(from_email_id, to_emai_id,
                   email_message.as_string(), from_email_id_password)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_drop_link_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def send_meeting_link_over_mail(email, name, meeting_url, agent_name, start_time, meeting_date, join_password):
    try:
        global send_gmail
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
            A video conference meeting has been scheduled between you and """ + agent_name + """.<br>
            For your convenience, please find the meeting details below:<br><br>
            Time: """ + start_time + """ <br>
            Date: """ + meeting_date + """<br>
            Link: <a href=\"""" + meeting_url + """\" target="_blank">""" + meeting_url + """</a><br>
            Password: """ + join_password + """
            <br><br>See you there!
        </div>

        </body>"""

        """With this function we send out our html email"""
        to_emai_id = email
        # FROM = settings.EMAIL_HOST_USER
        # PASSWORD = settings.EMAIL_HOST_PASSWORD
        from_email_id = settings.EMAIL_HOST_USER
        from_email_id_password = settings.EMAIL_HOST_PASSWORD
        # Create message container - the correct MIME type is
        # multipart/alternative here!
        email_message = MIMEMultipart('alternative')
        email_message[
            'subject'] = "Video Conference Link"
        email_message['To'] = email
        email_message['From'] = from_email_id
        email_message.preamble = """"""
        logger.info("Sending email to %s", email, extra={
                    'AppName': 'EasyAssistSalesforce'})
        # # Record the MIME type text/html.
        email_html_body = MIMEText(body, 'html')
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        email_message.attach(email_html_body)
        send_gmail(from_email_id, to_emai_id,
                   email_message.as_string(), from_email_id_password)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_meeting_link_over_mail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})


def send_invite_link_over_mail(email, meeting_url, agent_name, start_time, meeting_date, join_password):
    try:
        global send_gmail
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
                Hi,
            </p>
            <p>
            """ + agent_name + """ has invited you to join a video call.<br><br>
            For your convenience, please find the meeting details below:<br><br>
            Link: <a href=\"""" + meeting_url + """\" target="_blank">""" + meeting_url + """</a><br>
            Password: """ + join_password + """
            </p>
        </div>

        </body>"""

        """With this function we send out our html email"""
        to_emai_id = email
        # FROM = settings.EMAIL_HOST_USER
        # PASSWORD = settings.EMAIL_HOST_PASSWORD
        from_email_id = settings.EMAIL_HOST_USER
        from_email_id_password = settings.EMAIL_HOST_PASSWORD
        # Create message container - the correct MIME type is
        # multipart/alternative here!
        email_message = MIMEMultipart('alternative')
        email_message[
            'subject'] = "Video Conference Link"
        email_message['To'] = email
        email_message['From'] = from_email_id
        email_message.preamble = """"""
        logger.info("Sending email to %s", email, extra={
                    'AppName': 'EasyAssistSalesforce'})
        # # Record the MIME type text/html.
        email_html_body = MIMEText(body, 'html')
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        email_message.attach(email_html_body)
        send_gmail(from_email_id, to_emai_id,
                   email_message.as_string(), from_email_id_password)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_invite_link_over_mail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssistSalesforce'})
