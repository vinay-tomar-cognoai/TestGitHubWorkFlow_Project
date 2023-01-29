from uuid import uuid4
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_analytics import *
from EasyChatApp.utils_validation import EasyChatFileValidation, EasyChatInputValidation

import json
import os
import base64
import requests
import logging

from PIL import Image

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class UploadImageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            uploaded_file = data[0]

            file_name = uploaded_file["filename"]
            file_name = validation_obj.remo_html_from_string(file_name)

            base64_content = uploaded_file["base64_file"]
            
            file_validation_obj = EasyChatFileValidation()

            if file_validation_obj.check_malicious_file(file_name):
                response["status"] = 300
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            file_name = get_dot_replaced_file_name(file_name)
            file_extention = file_name.split(".")[-1]
            file_extention = file_extention.lower()

            allowed_files_list = ["png", "jpg", "jpeg", "bmp",
                                  "gif", "tiff", "exif", "jfif", "webm", "mpg", "jpe"]
            if file_extention in allowed_files_list:
                
                if file_validation_obj.check_malicious_file_from_content(base64_content, allowed_files_list):
                    response["status"] = 300
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                file_name = str(uuid.uuid4()) + '.' + file_extention
                file_path = settings.MEDIA_ROOT + file_name
                fh = open(file_path, "wb")
                fh.write(base64.b64decode(base64_content))
                fh.close()

                response["compressed_image_path"] = ""
                if file_extention not in ["gif", "GIF"]:
                    config_obj = Config.objects.all()[0]
                    size = config_obj.image_compress_size
                    original_file = Image.open(settings.MEDIA_ROOT + file_name)
                    # image exif remover

                    # By default, exif data is not included when reading a image.
                    # original_file = file_validation_obj.remove_image_exif(original_file)

                    original_file.thumbnail((size, size))

                    compressed_file_name = file_name.split(
                        '.')[0] + '_compressed.' + file_name.split('.')[1]

                    original_file.save(
                        settings.MEDIA_ROOT + compressed_file_name)

                    response["compressed_image_path"] = "/files/" + \
                        compressed_file_name

                    # updated code v5.4 
                    response["src"] = response["compressed_image_path"] 
                else:
                    # updated code v5.4 
                    # response["src"] = response["compressed_image_path"] 
                    response["src"] = "/files/" + file_name
                    
                response["status"] = 200
            else:
                response["status"] = 300
                logger.info("File format is not supported", extra={'AppName': 'EasyChat', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadImageAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class UploadFileCardAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            uploaded_file = data[0]

            file_name = uploaded_file["filename"]
            file_name = validation_obj.remo_html_from_string(file_name)

            base64_content = uploaded_file["base64_file"]

            file_validation_obj = EasyChatFileValidation()

            if file_validation_obj.check_malicious_file(file_name):
                response["status"] = 300
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            file_name = get_dot_replaced_file_name(file_name)
            file_extention = file_name.split(".")[-1]
            file_extention = file_extention.lower()

            allowed_files_list = ["pdf"]
            if file_extention in allowed_files_list:

                if file_validation_obj.check_malicious_file_from_content(base64_content, allowed_files_list):
                    response["status"] = 300
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                file_name = str(uuid.uuid4()) + '.' + file_extention
                file_path = settings.MEDIA_ROOT + file_name
                fh = open(file_path, "wb")
                fh.write(base64.b64decode(base64_content))
                fh.close()
                response["src"] = "/files/" + file_name
                response["status"] = 200
            else:
                response["status"] = 300
                logger.info("File format is not supported", extra={'AppName': 'EasyChat', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadFileCardAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DuplicateImageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            image_source = data["image_source"]
            duplicate_image_source = data["duplicate_image_source"]

            image = Image.open(image_source)
            image.save(duplicate_image_source)
            response["status"] = 200
            logger.info("DuplicateImageAPI saved image_source = %s, duplicate_image_source = %s", image_source, duplicate_image_source, extra={
                        'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DuplicateImageAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return Response(data=response)


class SaveBotImageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            image = data['src']
            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = "You are not authorised to perform this operation."
            else:
                if image[0:1] == "@":
                    response["status"] = 400
                else:   
                    file_extention = image.split(".")[-1]
                    file_extention = file_extention.lower()

                    if file_extention in ["png", "jpg", "jpeg", "bmp", "gif", "tiff", "exif", "jfif"]:
                        bot_obj.bot_image = image
                        bot_obj.save()
                        response["status"] = 200
                    else:
                        response["status"] = 300
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.info("File format is not supported at %s",
                                    str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveBotImageAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveBotLogoAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            image = data['src']
            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)

            file_extention = image.split(".")[-1]
            file_extention = file_extention.lower()

            if file_extention in ["png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"]:
                bot_obj.bot_logo = image
                bot_obj.save()
                response["status"] = 200
            else:
                response["status"] = 300
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.info("File format is not supported at %s",
                            str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveBotLogoAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveBotMessageImageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 300
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            image = data['src']
            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)

            file_extention = image.split(".")[-1]
            file_extention = file_extention.lower()

            if file_extention in ["png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"]:
                bot_obj.message_image = image
                bot_obj.save()
                response["status"] = 200
            else:
                response["status"] = 300
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.info("File format is not supported at %s",
                            str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveBotMessageImageAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class UploadFilesIntoDriveAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            uploaded_files = request.FILES.getlist('file')

            user_obj = User.objects.get(username=request.user.username)
            media_type = None
            if len(uploaded_files) > 10:
                response["status"] = 302
                response["message"] = "At max 10 files are allowed at a time."
                return Response(data=response)

            file_validation_obj = EasyChatFileValidation()

            for uploaded_file in uploaded_files:
                if file_validation_obj.check_malicious_file(uploaded_file.name):
                    response["status"] = 300
                    return Response(data=response)

            for uploaded_file in uploaded_files:
                try:

                    if not os.path.exists('secured_files/EasyChatApp/drive'):
                        os.makedirs('secured_files/EasyChatApp/drive')

                    path = os.path.join(
                        settings.SECURE_MEDIA_ROOT, "EasyChatApp/drive/")

                    fs = FileSystemStorage(location=path)
                    file_name = get_dot_replaced_file_name(uploaded_file.name)
                    filename = fs.save(
                        file_name, uploaded_file)

                    path = "/secured_files/EasyChatApp/drive/" + filename

                    file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
                        file_path=path, is_public=False)

                    file_url = '/chat/download-file/' + \
                        str(file_access_management_obj.key) + '/' + filename

                    file_extention = path.split(".")[-1]
                    file_extention = file_extention.lower()

                    filename = path.split("/")[-1]

                    if file_extention in ["png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"]:
                        media_type = MEDIA_IMAGE
                    elif file_extention in ["ppt", "pptx", "pptm"]:
                        media_type = MEDIA_PPT
                    elif file_extention in ["doc", "docx", "odt", "rtf", "txt"]:
                        media_type = MEDIA_DOC
                    elif file_extention in ["pdf"]:
                        media_type = MEDIA_PDF
                    elif file_extention in ["xls", "xlsx", "xlsm", "xlt", "xltm"]:
                        media_type = MEDIA_XLS
                    elif file_extention in ["avi", "flv", "wmv", "mov", "mp4"]:
                        media_type = MEDIA_VIDEO
                    else:
                        pass

                    if media_type != None:
                        EasyChatDrive.objects.create(user=user_obj,
                                                     media_name=uploaded_file.name,
                                                     media_url=file_url,
                                                     media_type=media_type)
                except Exception as e:  # noqa: F841
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Error UploadFilesIntoDriveAPI For Loop: %s at %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            if media_type != None:
                response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadFilesIntoDriveAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return Response(data=response)


class RemoveFilesFromDriveAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = json.loads(DecryptVariable(data["data"]))
            file_id_list = data["file_id_list"]
            user_obj = User.objects.get(username=request.user.username)
            for file_id in file_id_list:
                EasyChatDrive.objects.get(
                    pk=int(file_id), user=user_obj).delete()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RemoveFilesFromDriveAPI: %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


"""
# Commenting this function because we have implemented different functionality for uploading attachment
class UploadAttachmentAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            logger.info("Into UploadAttachment...", extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            data = request.data
            uploaded_file = data["upload_attachment"]
            logger.info("uploaded_file recieving...", extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            if uploaded_file.name.find("<") != -1 or uploaded_file.name.find(">") != -1 or uploaded_file.name.find("=") != -1:
                return Response(data=response)

            path = default_storage.save(
                "attachment/" + uploaded_file.name.replace(" ", ""), ContentFile(uploaded_file.read()))
            response["status"] = 200
            response["src"] = "/files/" + path
            logger.info("path %s", response["src"], extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            logger.info("uploaded_file saving...", extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            logger.info("Exit from UploadAttachment", extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[ENGINE] %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response = build_error_response(
                "Bot is under maintenance. Please try again later.")
        return Response(data=response)"""


class SaveImageLocallyAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "No such file exists"
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            image_url = data["image_url"]
            filedir, filename = os.path.split(image_url)
            file_image = requests.get(image_url)
            open(settings.MEDIA_ROOT + filename,
                 'wb').write(file_image.content)

            response["src"] = "/files/" + filename
            response["status"] = 200
            response["message"] = "SUCCESS"
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveImageLocallyAPI: %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveImageLocally = SaveImageLocallyAPI.as_view()

# UploadAttachment = UploadAttachmentAPI.as_view()

RemoveFilesFromDrive = RemoveFilesFromDriveAPI.as_view()

UploadImage = UploadImageAPI.as_view()

DuplicateImage = DuplicateImageAPI.as_view()

SaveBotImage = SaveBotImageAPI.as_view()

SaveBotMessageImage = SaveBotMessageImageAPI.as_view()

UploadFilesIntoDrive = UploadFilesIntoDriveAPI.as_view()

SaveBotLogo = SaveBotLogoAPI.as_view()

UploadFileCard = UploadFileCardAPI.as_view()


class UploadImagesOnServerAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            uploaded_files = data

            file_id_url_map = {}

            for uploaded_file in uploaded_files:

                file_id = uploaded_file["file_id"]
                file_id_url_map[file_id] = {}

                file_name = uploaded_file["filename"]
                file_name = validation_obj.remo_html_from_string(file_name)

                base64_content = uploaded_file["base64_file"]
                base64_content = base64_content.replace(
                    'data:image/png;base64,', '')
                base64_content = base64_content.replace(
                    'data:image/jpg;base64,', '')
                base64_content = base64_content.replace(
                    'data:image/jpeg;base64,', '')

                file_validation_obj = EasyChatFileValidation()

                if file_validation_obj.check_malicious_file(file_name):
                    file_id_url_map[file_id]["status"] = 300
                    file_id_url_map[file_id]["message"] = "Malicious File Name"
                    continue

                file_name = get_dot_replaced_file_name(file_name)
                file_extention = file_name.split(".")[-1]
                file_extention = file_extention.lower()

                allowed_files_list = ["png", "jpeg"]
                if file_extention in allowed_files_list:

                    if file_validation_obj.check_malicious_file_from_content(base64_content, allowed_files_list):
                        file_id_url_map[file_id]["status"] = 300
                        file_id_url_map[file_id]["message"] = "Malicious File Content"
                        continue

                    file_name = str(uuid.uuid4()) + '.' + file_extention
                    file_path = settings.MEDIA_ROOT + file_name
                    fh = open(file_path, "wb")
                    fh.write(base64.b64decode(base64_content))
                    fh.close()

                    size = 1024  # in KB

                    original_file = Image.open(settings.MEDIA_ROOT + file_name)
                    original_file.thumbnail((size, size))
                    original_file.save(
                        settings.MEDIA_ROOT + file_name)

                    file_id_url_map[file_id]["compressed_path"] = settings.EASYCHAT_HOST_URL + "/files/" + \
                        file_name

                    file_id_url_map[file_id]["status"] = 200
                else:
                    file_id_url_map[file_id]["status"] = 300
                    file_id_url_map[file_id]["message"] = "File format not supported"
                    logger.info("File format is not supported", extra={'AppName': 'EasyChat', 'user_id': str(
                        request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            response["files_data"] = json.dumps(file_id_url_map)
            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadImagesOnServerAPI : %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UploadImagesOnServer = UploadImagesOnServerAPI.as_view()
