import sys
import logging
import smtplib
import base64

from django.conf import settings
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from EasyChat.settings import EASYCHAT_HOST_URL
from DeveloperConsoleApp.constants import GENERAL_LOGIN_LOGO
from EasyAssistApp.constants import COGNOAI_LOGO_PATH, ANALYTICS_MAIL_BUTTON_CSS
import json

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
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_password_over_email(email, name, password, platform_url):
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
                Dear """ + name + """,
            </p>
            <p>
            Your password to login into Cobrowsing Console <a href=\"""" + platform_url + """\" target="_blank">""" + platform_url + """</a> for <b>User ID</b> '""" + email + """' is <b>""" + password + """</b>
            </p>

            <p>Kindly connect with us incase of any issue.</p>
            <p>&nbsp;</p>
        """

        config = get_developer_console_settings()

        body += config.custom_report_template_signature
        
        body += """</div></body>"""
        
        logger.info("Sending email to %s", email,
                    extra={'AppName': 'EasyAssist'})
        send_email_to_customer_via_awsses(email, "Cobrowsing Console - Access Management", body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_password_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_drop_link_over_email(email, customer_name, agent_name, generated_link):
    try:
        body_text = """Hi <b>{customer_name}</b>,<br><br>
            <b>{agent_name}</b>
            has invited you to join a co-browsing support
            session. Please click on the button below to join 
            the co-browsing session.
        """.format(
            customer_name=customer_name,
            agent_name=agent_name   
        )

        email_subject = "Co-Browsing DropLink"

        mail_footer = """
            <a href="{generated_link}" style="{ANALYTICS_MAIL_BUTTON_CSS}" target="_blank" data-saferedirecturl="#">
                Join session
            </a>
        """.format(
            generated_link=generated_link,
            ANALYTICS_MAIL_BUTTON_CSS=ANALYTICS_MAIL_BUTTON_CSS
        )

        body = get_mail_template(body_text, email_subject, mail_footer)
        
        logger.info("Sending email to %s", email,
                    extra={'AppName': 'EasyAssist'})
        send_email_to_customer_via_awsses(email, email_subject, body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_drop_link_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_meeting_link_over_mail(email, name, meeting_url, agent_name, start_time, meeting_date, join_password):
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

        logger.info("Sending email to %s", email,
                    extra={'AppName': 'EasyAssist'})
        send_email_to_customer_via_awsses(email, "Video Conference Link", body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_meeting_link_over_mail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_invite_link_over_mail(email, meeting_url, agent_name, start_time, meeting_date, join_password):
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

        logger.info("Sending email to %s", email,
                    extra={'AppName': 'EasyAssist'})

        send_email_to_customer_via_awsses(email, "Video Conference Link", body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_invite_link_over_mail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_masking_pii_data_otp_mail(email_ids, otp, username):

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
            """ + str(username) + """ is trying to turn off the PII Masking settings for cobrowse and cognomeet. Code to accept it is <b>""" + str(otp) + """<b>.
        </p>
    </div>
    </body>"""

    for email_id in email_ids:
        send_email_to_customer_via_awsses(email_id, "PII Change Request", body)


def send_invite_link_over_mail_reverse_cobrowsing(email, cobrowsing_url, agent_name):
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
                Hi,
            </p>
            <p>
            Agent """ + agent_name + """ has invited you to a Cobrowsing session.<br><br>
            Please join using the link:<br><br>
            Link: <a href=\"""" + cobrowsing_url + """\" target="_blank">""" + cobrowsing_url + """</a><br>
            </p>
        </div>

        </body>"""

        logger.info("Sending email to %s", email,
                    extra={'AppName': 'EasyAssist'})
        send_email_to_customer_via_awsses(email, "Invitation for Cobrowsing Session", body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_invite_link_over_mail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_reported_bug_over_email(email, bug_report_obj, sender_name, imp_info):
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
                Hi,
            </p>
            <div>
            Agent <b>""" + sender_name + """</b> has reported a bug.<br>
            <b>Domain</b> : """ + settings.EASYCHAT_DOMAIN + """<br>
            <b>Issue ID</b> : """ + str(bug_report_obj.pk) + """<br>
            <b>Issue Description</b> : """ + bug_report_obj.description + """<br>
            <b>URL</b> : """ + imp_info['href'] + """<br>
            <b>Internet Speed</b> : """ + imp_info['internet_speed'] + """<br>
            <b>System Config</b> : """ + imp_info['SystemInfo'] + """<br><br>
            Please find relevant attachment below:<br>
            </div>
        </div>

        </body>"""

        attachment_list = []
        files = json.loads(bug_report_obj.files)
        for file_type in files:
            file_path = files[file_type]
            if file_path == "":
                continue
            attachment_obj = {
                "base64": "",
                "filename": ""
            }
            filename = file_path.split('/')[-1]
            # open the file to be sent
            attachment = open(file_path, "rb")
            encoded_str = base64.b64encode(attachment.read())
            encoded_str = encoded_str.decode('utf-8')
            attachment_obj["base64"] = encoded_str
            attachment_obj["filename"] = filename
            attachment_list.append(attachment_obj)

        logger.info("Sending email to %s", email,
                    extra={'AppName': 'EasyAssist'})

        send_email_to_customer_via_awsses(email, "Cobrowsing Issue Report", body, attachment_list=attachment_list)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_reported_bug_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_analytics_over_email(email, email_subject, body):
    try:
        """With this function we send out our html email"""
        send_email_to_customer_via_awsses(email, email_subject, body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_analytics_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_reverse_cobrowse_invite_link(email, agent_email, session_id):
    try:

        path = EASYCHAT_HOST_URL + "/easy-assist/client/" + session_id

        email_subject = "Invitation for Co-Browsing Session"
        body_text = """ Hi, 
            {agent_email}
            has invited you to join a co-browsing support
            session. Please click on the button below to join 
            the co-browsing session.
        """.format(agent_email=agent_email)

        mail_footer = """
            <a href="{path}" style="{ANALYTICS_MAIL_BUTTON_CSS}" target="_blank" data-saferedirecturl="#">
                Join session
            </a>
        """.format(
            path=path,
            ANALYTICS_MAIL_BUTTON_CSS=ANALYTICS_MAIL_BUTTON_CSS
        )

        body = get_mail_template(body_text, email_subject, mail_footer)
        
        send_email_to_customer_via_awsses(email, email_subject, body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_reverse_cobrowse_invite_link %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_cobrowse_proxy_drop_link_over_email(email, agent_username, generated_link):
    try:
        
        email_subject = "Invitation for Co-browsing Session"
        body_text = """ Hi, 
            {agent_name} has invited you to join a co-browsing support session. 
            Please click on the button below to join the co-browsing session.
        """.format(
            agent_name=agent_username
        )

        mail_footer = """
            <a href="{generated_link}" style="{ANALYTICS_MAIL_BUTTON_CSS}" target="_blank" data-saferedirecturl="#">
                Join Session
            </a>
        """.format(
            generated_link=generated_link,
            ANALYTICS_MAIL_BUTTON_CSS=ANALYTICS_MAIL_BUTTON_CSS
        )
        
        body = get_mail_template(body_text, email_subject, mail_footer)
        
        logger.info("Sending email to %s", email,
                    extra={'AppName': 'EasyAssist'})
        send_email_to_customer_via_awsses(
            email, email_subject, body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_cobrowse_proxy_drop_link_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def get_mail_template(body_text, email_subject, mail_footer):
    try:
        config = get_developer_console_settings()
        cognoai_logo_url = settings.EASYCHAT_HOST_URL + config.login_logo
        if config.login_logo == GENERAL_LOGIN_LOGO:
            cognoai_logo_url = settings.EASYCHAT_HOST_URL + COGNOAI_LOGO_PATH
        
        body = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Email</title>
        </head>
        <body>
                <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0" dir="ltr"
                style="background-color:rgb(242,245,247);background:#3905D6; height: 100%;">
                <tbody>
                    <tr>
                        <td align="center" valign="top" style="margin:0;padding:30px 15px 40px">
                            <table width="600" align="center" border="0" cellspacing="0" cellpadding="0" style="width:600px">
                            <tbody>
                                <tr>
                                    <td align="center" valign="center" style="margin:0;padding:0;border-radius:30px">
                                        <table align="center" border="0" cellpadding="0" cellspacing="0">
                                        <tbody>
                                            <tr>
                                                <td valign="top" align="center" style="padding:0px;margin:0px">
                                                <img src="{cognoai_logo_url}"  width="200" height="60"
                                                    style="border:none;font-weight:bold;height:auto;line-height:100%;outline:none;text-decoration:none;text-transform:capitalize;border-width:0px;border-style:none;border-color:transparent;font-size:12px;display:block;margin-bottom:10px;"
                                                    class="CToWUd"> </td>
                                            </tr>
                                        </tbody>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" valign="top" style="margin:0;padding:0">
                                        <table width="100%" align="center" border="0" cellpadding="0" cellspacing="0"
                                        bgcolor="#ffffff" style="border-radius:30px!important">
                                        <tbody>
                                            <tr style="border-radius:30px!important">
                                                <td align="center" valign="top"
                                                    style="margin:0px;padding:40px;background-color:rgb(255,255,255);font-size:18px;font-family:'DM Sans','Silka',-apple-system,BlinkMacSystemFont,'Segoe UI','Roboto','Oxygen','Ubuntu','Cantarell','Fira Sans','Droid Sans','Helvetica Neue',sans-serif;line-height:1.33;border-radius:30px!important"
                                                    class="m_-5602263282612371593heading">
                                                    <span style="font-family:'DM Sans','Silka',-apple-system,BlinkMacSystemFont,'Segoe UI','Roboto','Oxygen','Ubuntu','Cantarell','Fira Sans','Droid Sans','Helvetica Neue',sans-serif;color:#181818;font-size:26px">
                                                        <span style="font-weight:700">
                                                            <table>
                                                                <tbody>
                                                                    <tr style="background:white">
                                                                        <td>
                                                                            <p style="font-style:normal;aliign-items:left;font-weight:700;font-size:20px;line-height:35px;letter-spacing:0.025em;color:#1E293B;margin:0;"> 
                                                                                {email_subject} 
                                                                            </p>
                                                                            <p style="font-weight: 400;
                                                                                font-size: 14px;
                                                                                line-height: 138%;
                                                                                color: #475569; margin-bottom:
                                                                                30px;">
                                                                                {body_text}
                                                                            </p>
                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                            {mail_footer}
                                                        </span>
                                                    </span>
                                                </td>
                                            </tr>
                                        </tbody>
                                        </table>
                                    </td>
                                </tr>
                            </tbody>
                            </table>
                        </td>
                    </tr>
                </tbody>
                </table>
        </body>
        </html>
        """.format(
            cognoai_logo_url=cognoai_logo_url,
            body_text=body_text,
            email_subject=email_subject,
            mail_footer=mail_footer
        )

        return body

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_mail_template %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})

        return ""

"""
function: send_analytics_mail_to_customer
input params:
    email: mail on which email will be sent.
    start_date: report period start date.
    end_date: report period end date.
    sender_name: name of the sender.
    report_type: type of report requested.
    attachment_file_path: path of the file which have to be downloaded from mail.
    card_name: name of the analytics card for which the mail has been requested.
output:

    This function creates the body of mail and send it to the given email ID.

"""


def send_analytics_mail_to_customer(email, start_date, end_date, sender_name, report_type, attachment_file_path, card_name=""):
    try:
        attachment_file_path = settings.EASYCHAT_HOST_URL + '/' + attachment_file_path
        email_subject = report_type + " Co-Browsing Report"
        mail_body_text = report_type + " Co-Browsing"
        if card_name:
            email_subject = report_type + " Co-Browsing || " + card_name
            card_name = " " + card_name
            mail_body_text += card_name
        else:
            mail_body_text += " Analytics"

        body_text = """Hi <b>{sender_name}</b>,<br><br>
            We have received a request to provide you with the {mail_body_text} report from <b>{start_date}</b> to <b>{end_date}</b>. 
            Please download the report by clicking on the button below.""".format(
            sender_name=sender_name,
            mail_body_text=mail_body_text,
            start_date=start_date,
            end_date=end_date
        )

        mail_footer = """
            <a href="{file_path}" style="{ANALYTICS_MAIL_BUTTON_CSS}" target="_blank" data-saferedirecturl="#">
                Download Report
            </a>
        """.format(
            file_path=attachment_file_path,
            ANALYTICS_MAIL_BUTTON_CSS=ANALYTICS_MAIL_BUTTON_CSS
        )

        body = get_mail_template(body_text, email_subject, mail_footer)

        send_email_to_customer_via_awsses(email, email_subject, body)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_analytics_mail_to_customer %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_no_data_found_email(email, start_date, end_date, sender_name, report_type, email_subject):
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
                        We have received a request to provide you with the EasyAssist {} report from {} to {}.
                    <p>
                    <br/>
                    <p> 
                        <b>Please note, that no records have been found in the selected report period.</b>
                    </p>
                    <p>&nbsp;</p>
                    <p>Technology Development</p>
                    <p>Cogno AI</p>
                    <a href="https://getcogno.ai/">https://getcogno.ai/</a>
                </div>
            </body>
        """

        body = body.format(sender_name, report_type, str(start_date), str(
            end_date))

        send_email_to_customer_via_awsses(email, email_subject, body)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_no_data_found_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})
