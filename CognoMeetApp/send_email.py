import sys
import logging
import smtplib
import base64

from django.conf import settings
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses
from CognoMeetApp.constants_mailer_analytics import *
from CognoMeetApp.constants import COGNOAI_LOGO_WHITE
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
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
        send_email_to_customer_via_awsses(
            email, "Cobrowsing Console - Access Management", body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_password_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_drop_link_over_email(email, customer_name, agent_name, client_page_link, generated_link):
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

        logger.info("Sending email to %s", email,
                    extra={'AppName': 'EasyAssist'})
        send_email_to_customer_via_awsses(email, "Cobrowsing Drop Link", body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_drop_link_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyAssist'})


def send_meeting_link_over_mail(email, name, meeting_url, agent_name, start_time, end_time, meeting_date, join_password):
    try:
        config = get_developer_console_settings()
        cognoai_logo_url = settings.EASYCHAT_HOST_URL + config.login_logo
        if config.login_logo == "/static/EasyChatApp/img/Cogno_Logo.svg":
            cognoai_logo_url = settings.EASYCHAT_HOST_URL + COGNOAI_LOGO_WHITE

        body = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta http-equiv="X-UA-Compatible" content="IE=edge" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Meeting Invitation</title>
            <style>
            @font-face {{
                font-family: "Silka";
                src: url("../Silka/Silka-Medium.woff2");
                font-weight: 500;
                font-style: normal;
            }}
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                background:#3905D6;
                height: 100vh;
                font-family: "Silka";
            }}
            </style>
        </head>
        <body>
            <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0" dir="ltr"
            style="background-color: #3905D6; height: 100%;">
            <tbody>
                <tr>
                <td align="center" valign="top" style="margin:0;padding:30px 15px 40px">
                    <table width="600" align="center" border="0" cellspacing="0" cellpadding="0" style="width:700px">
                    <tbody>
                        <tr>
                        <td align="center" valign="center" style="margin:0;padding:0;border-radius:30px">
                            <table align="center" border="0" cellpadding="0" cellspacing="0">
                            <tbody>
                                <tr>
                                <td valign="top" align="center" style="padding:0px;margin:0px"> <img src="{logo_url}"
                                    width="200" height="60"
                                    style="border:none;font-weight:bold;height:auto;line-height:100%;outline:none;text-decoration:none;text-transform:capitalize;border-width:0px;border-style:none;border-color:transparent;font-size:12px;display:block"
                                    class="CToWUd"> </td>
                                </tr>
                            </tbody>
                            </table>
                        </td>
                        </tr>
                        <tr>
                        <td align="center" valign="top" height="30" style="margin:0px;padding:0"></td>
                        </tr>
                        <tr>
                        <td align="center" valign="top" style="margin:0;padding:0">
                            <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:100%">
                            <tbody>
                                <tr> </tr>
                            </tbody>
                            </table>
                        </td>
                        </tr>
                        <tr>
                        <td align="center" valign="top" style="margin:0;padding:0">
                            <table width="100%" align="center" border="0" cellpadding="0" cellspacing="0" bgcolor="#ffffff"
                            style="border-radius:30px!important">
                            <tbody>
                                <tr style="border-radius:30px!important">
                                <td align="center" valign="top"
                                    style="margin:0px;padding:40px;background-color:rgb(255,255,255);font-size:18px;font-family:'DM Sans','Silka',-apple-system,BlinkMacSystemFont,'Segoe UI','Roboto','Oxygen','Ubuntu','Cantarell','Fira Sans','Droid Sans','Helvetica Neue',sans-serif;line-height:1.33;border-radius:30px!important"
                                    class="m_-5602263282612371593heading">
                                    <span
                                    style="font-family:'DM Sans','Silka',-apple-system,BlinkMacSystemFont,'Segoe UI','Roboto','Oxygen','Ubuntu','Cantarell','Fira Sans','Droid Sans','Helvetica Neue',sans-serif;color:#181818;font-size:26px">
                                    <span style="font-weight:700">
                                        <table>
                                        <tbody>
                                            <tr style="background:white">
                                            <td>
                                                <p
                                                style="font-style:normal;font-weight:700;font-size:20px;line-height:35px;letter-spacing:0.025em;color:#1E293B;margin-bottom: 12px;">
                                                Video Conference Link
                                                </p>
                                                <p style="font-weight: 600;
                                                font-size: 14px;
                                                line-height: 138%;
                                                color: #475569; margin-bottom:
                                                12px;">Dear {customer_name},</p>
                                                <p style="font-weight: 400;
                                                font-size: 14px;
                                                line-height: 138%;
                                                color: #475569; margin-bottom:
                                                30px;">A video conference meeting has been scheduled between you and {agent_name}. For your convenience, please find the meeting details
                                                below:
                                                </p>
                                                <p style="font-weight: 500;
                                                font-size: 14px;
                                                line-height: 138%;
                                                color: #475569;">Date: {meeting_date}</p>
                                                <p style="font-weight: 500;
                                                font-size: 14px;
                                                line-height: 138%;
                                                color: #475569;">Time: {meeting_start_time} - {meeting_end_time}</p>
                                                <p style="font-weight: 500;
                                                font-size: 14px;
                                                line-height: 138%;
                                                color: #475569;margin-bottom: 30px;">Password: {password}</p>
                                            </td>
                                            </tr>
                                        </tbody>
                                        </table>
                                        <a href="{meeting_url}"
                                        style="height:41px;width:259px;border-radius:30px;background:#3905D6;border-radius:30px;color:white;text-decoration:none;font-family:Silka;font-style:normal;font-weight:bold;font-size:14px;line-height:17px;letter-spacing:0.025em;color:#ffffff;padding:10px"
                                        target="_blank" data-saferedirecturl="#">
                                        Join the meeting</a>
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
        </html>""".format(
            logo_url=cognoai_logo_url,
            customer_name=name,
            agent_name=agent_name,
            meeting_date=meeting_date,
            meeting_start_time=start_time,
            meeting_end_time=end_time,
            password=join_password,
            meeting_url=meeting_url
        )

        logger.info("Sending email to %s", email,
                    extra={'AppName': 'CognoMeet'})
        send_email_to_customer_via_awsses(email, "Video Conference Link", body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_meeting_link_over_mail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})


def send_invite_link_over_mail(email, meeting_url, agent_name, start_time, meeting_date, join_password):
    try:
        config = get_developer_console_settings()
        cognoai_logo_url = settings.EASYCHAT_HOST_URL + config.login_logo
        if config.login_logo == "/static/EasyChatApp/img/Cogno_Logo.svg":
            cognoai_logo_url = settings.EASYCHAT_HOST_URL + COGNOAI_LOGO_WHITE
            
        body = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta http-equiv="X-UA-Compatible" content="IE=edge" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Meeting Invite</title>
            <style>
            @font-face {{
                font-family: "Silka";
                src: url("../Silka/Silka-Medium.woff2");
                font-weight: 500;
                font-style: normal;
            }}
            *{{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: "Silka";
                background:#3905D6;
                height: 100vh;
            }}
            </style>
        </head>
        <body>
            <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0" dir="ltr"
            style="background-color:#3905D6; height: 100%;">
            <tbody>
                <tr>
                <td align="center" valign="top" style="margin:0;padding:30px 15px 40px">
                    <table width="600" align="center" border="0" cellspacing="0" cellpadding="0" style="width:700px">
                    <tbody>
                        <tr>
                        <td align="center" valign="center" style="margin:0;padding:0;border-radius:30px">
                            <table align="center" border="0" cellpadding="0" cellspacing="0">
                            <tbody>
                                <tr>
                                <td valign="top" align="center" style="padding:0px;margin:0px"> <img src="{cognoai_logo}"
                                    width="200" height="60"
                                    style="border:none;font-weight:bold;height:auto;line-height:100%;outline:none;text-decoration:none;text-transform:capitalize;border-width:0px;border-style:none;border-color:transparent;font-size:12px;display:block"
                                    class="CToWUd"> </td>
                                </tr>
                            </tbody>
                            </table>
                        </td>
                        </tr>
                        <tr>
                        <td align="center" valign="top" height="30" style="margin:0px;padding:0"></td>
                        </tr>
                        <tr>
                        <td align="center" valign="top" style="margin:0;padding:0">
                            <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:100%">
                            <tbody>
                                <tr> </tr>
                            </tbody>
                            </table>
                        </td>
                        </tr>
                        <tr>
                        <td align="center" valign="top" style="margin:0;padding:0">
                            <table width="100%" align="center" border="0" cellpadding="0" cellspacing="0" bgcolor="#ffffff"
                            style="border-radius:30px!important">
                            <tbody>
                                <tr style="border-radius:30px!important">
                                <td align="center" valign="top"
                                    style="margin:0px;padding:40px;background-color:rgb(255,255,255);font-size:18px;font-family:'DM Sans','Silka',-apple-system,BlinkMacSystemFont,'Segoe UI','Roboto','Oxygen','Ubuntu','Cantarell','Fira Sans','Droid Sans','Helvetica Neue',sans-serif;line-height:1.33;border-radius:30px!important"
                                    class="m_-5602263282612371593heading">
                                    <span
                                    style="font-family:'DM Sans','Silka',-apple-system,BlinkMacSystemFont,'Segoe UI','Roboto','Oxygen','Ubuntu','Cantarell','Fira Sans','Droid Sans','Helvetica Neue',sans-serif;color:#181818;font-size:26px">
                                    <span style="font-weight:700">
                                        <table>
                                        <tbody>
                                            <tr style="background:white">
                                            <td>
                                                <p
                                                style="font-style:normal;font-weight:700;font-size:20px;line-height:35px;letter-spacing:0.025em;color:#1E293B;margin-bottom: 12px;">
                                                Video Conference Link
                                                </p>
                                                <p style="font-weight: 400;
                                                font-size: 14px;
                                                line-height: 138%;
                                                color: #475569; margin-bottom:
                                                30px;">Hi, {agent_name} has invited you to join a video call. For
                                                your convenience, please find the meeting details below:<br/><br/>
                                                {meeting_url}
                                                </p>
                                                <p style="font-weight: 500;
                                                font-size: 14px;
                                                line-height: 138%;
                                                color: #475569;margin-bottom: 24px;">Password: {password}</p>
                                            </td>
                                            </tr>
                                        </tbody>
                                        </table>
                                        <a href="{meeting_url}"
                                        style="height:41px;width:259px;border-radius:30px;background:#3905D6;border-radius:30px;color:white;text-decoration:none;font-family:Silka;font-style:normal;font-weight:bold;font-size:14px;line-height:17px;letter-spacing:0.025em;color:#ffffff;padding:10px"
                                        target="_blank" data-saferedirecturl="#">
                                        Join the meeting</a>
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
        </html>""".format(
            agent_name=agent_name,
            meeting_url=meeting_url,
            password=join_password,
            cognoai_logo=cognoai_logo_url
        )

        logger.info("Sending email to %s", email,
                    extra={'AppName': 'CognoMeet'})

        send_email_to_customer_via_awsses(email, "Video Conference Link", body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_invite_link_over_mail %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})


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
        send_email_to_customer_via_awsses(
            email, "Invitation for Cobrowsing Session", body)
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

        send_email_to_customer_via_awsses(
            email, "Cobrowsing Issue Report", body, attachment_list=attachment_list)
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

                
def send_data_file_over_email(email, start_date, end_date, sender_name, report_type, email_subject, attachment_file_path):
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
                        We have received a request to provide you with the CognoMeet {} report from {} to {}. Please click on the link below to download the file.
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
        body = body.format(sender_name, report_type, str(start_date), str(
            end_date), domain, attachment_file_path)
        logger.info("Sending mail for %s", str(report_type), extra={'AppName': 'CognoMeet'})
        send_email_to_customer_via_awsses(email, email_subject, body)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_data_file_over_email %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'CognoMeet'})
