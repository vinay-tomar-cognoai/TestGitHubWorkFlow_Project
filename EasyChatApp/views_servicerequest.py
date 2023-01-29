from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from EasyChatApp.models import *
# from EasyChatApp.utils import *
# from EasyChatApp.utils_analytics import *

from django.conf import settings

# from os.path import basename
from email.mime.multipart import MIMEMultipart
# from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

import json
import logging
import smtplib
import threading
from EasyChatApp.utils import *
from DeveloperConsoleApp.utils import get_developer_console_settings

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class SaveDeploymentRequestAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            user_obj = user_obj = User.objects.get(
                username=request.user.username)

            bot_id = data["bot_id"]
            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False, is_uat=True)

            customer_name = request.user.first_name + ' ' + request.user.last_name

            whitelisted_domain = data["whitelisted_domain"]

            thread_deployment = threading.Thread(target=allow_deployment, args=(
                request.user.username, customer_name, whitelisted_domain,))

            thread_deployment.start()

            try:
                service_obj = ServiceRequest.objects.get(user=user_obj, bot=bot_obj)
                service_obj.customer_name = customer_name
                service_obj.request = whitelisted_domain
                service_obj.save()
            except Exception:
                ServiceRequest.objects.create(user=user_obj, customer_name=customer_name, request=whitelisted_domain, bot=bot_obj)

            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveDeploymentRequestAPI : %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


"""
@params FROM: Email id from which mail will be sent
@params TO: List of email ids to whom mail will be sent
@params message_as_string: Message as string
@params PASSWORD: account password
"""


# def send_mail(from_email_id, to_emai_id, message_as_string, from_email_id_password):
#     # # The actual sending of the e-mail
#     server = smtplib.SMTP('smtp.gmail.com:587')
#     # Credentials (if needed) for sending the mail
#     password = from_email_id_password
#     # Start tls handshaking
#     server.starttls()
#     # Login to server
#     server.login(from_email_id, password)
#     # Send mail
#     server.sendmail(from_email_id, to_emai_id, message_as_string)
#     # Close session
#     server.quit()


def allow_deployment(user, name, domain_list):
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
            Hello Harshita,
        </p>
        <p>
            The following request has been raised by """ + str(user) + """.
        </p>
        <p>Name: """ + str(name) + """</p>
        <p>Domain name/names: """ + str(domain_list) + """</p>
        <p>Please allowed the requested domain to deploy our Bot.</p>
        <p>&nbsp;</p>"""

    config = get_developer_console_settings()

    body += config.custom_report_template_signature

    body += """</div></body>"""

    """With this function we send out our html email"""
    to_email_id = "tech.team.allincall@gmail.com"

    send_email_to_customer_via_awsses(to_email_id, "Allow following domain for Bot @CognoAI", body)


SaveDeploymentRequest = SaveDeploymentRequestAPI.as_view()
