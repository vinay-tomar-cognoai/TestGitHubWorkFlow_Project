import sys
import logging
import smtplib

from django.conf import settings
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
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'Campaign'})
