from EasyChatApp.models import MISDashboard
from datetime import datetime, timedelta
from django.db.models import Q
from django.conf import settings
import sys
import logging

logger = logging.getLogger(__name__)

FROM = settings.EMAIL_HOST_USER 
PASSWORD = settings.EMAIL_HOST_PASSWORD
host_url = settings.EASYCHAT_HOST_URL

from DeveloperConsoleApp.utils import send_email_to_customer_via_awsses


# def send_mail(FROM, TO, message_as_string, PASSWORD):
#     import smtplib
#     # # The actual sending of the e-mail
#     server = smtplib.SMTP('smtp.gmail.com:587')
#     # Credentials (if needed) for sending the mail
#     password = PASSWORD
#     # Start tls handshaking
#     server.starttls()
#     # Login to server
#     server.login(FROM, password)
#     # Send mail
#     server.sendmail(FROM, TO, message_as_string)
#     # Close session
#     server.quit()


def get_last_hour_message_count(bot_obj):
    time_threshold = datetime.now() - timedelta(hours=1)
    mis_objects = MISDashboard.objects.filter(
        date__gte=time_threshold, bot=bot_obj)
    return mis_objects.filter(~Q(intent_name=None)).count()


def generate_mail(email, message_subject, email_content):

    body = """
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      <title>Cogno AI</title>
      <style type="text/css" media="screen">
      </style>
    </head>
    <body>
    <div style="padding:1em;border:0.1em black solid;" class="container">
        <p>""" + email_content + """
         </p>
    </div>
    </body>"""

    send_email_to_customer_via_awsses(email, message_subject, body)
