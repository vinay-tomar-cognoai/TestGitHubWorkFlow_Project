import os
import sys
import json
import uuid
import xlrd
import random
import logging
import datetime
import mimetypes
import urllib.parse

# Django REST framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# Django imports
from django.db.models import Q
from django.http import FileResponse
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render, HttpResponse, HttpResponseRedirect

from EasyChat import settings
from EasyChatApp.utils import *
from LiveChatApp.utils import *
from LiveChatApp.models import *
from LiveChatApp.constants import *
from LiveChatApp.utils_custom_encryption import *
from LiveChatApp.utils_validation import LiveChatFileValidation, LiveChatInputValidation


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class LiveChatUploadInternalChatAttachmentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}

        try:
            data = request.data
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = LiveChatInputValidation()
            file_validation_obj = LiveChatFileValidation()

            uploaded_file_encrypted_data = data["uploaded_file"]
            uploaded_file_encrypted_data = DecryptVariable(
                uploaded_file_encrypted_data)
            uploaded_file_encrypted_data = json.loads(
                uploaded_file_encrypted_data)
            file_name = uploaded_file_encrypted_data[0]["filename"]
            file_name = validation_obj.remo_html_from_string(file_name)
            base64_content = uploaded_file_encrypted_data[0]["base64_file"]

            chat_type = data["chat_type"]
            group_id = data["group_id"]
            user_group_id = data["user_group_id"]
            receiver_username = data["receiver_username"]

            file_size = (len(base64_content) * 3) / 4 - \
                base64_content.count('=', -2)

            if file_validation_obj.check_malicious_file(file_name):
                response['status'] = 500
                response['status_message'] = 'Malicious File'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            file_extension = file_name.split(".")[-1].lower()

            allowed_file_extensions = ["png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "jpe", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg", "mp2",
                                       "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt", "flv", "swf", "avchd", "pdf", "docs", "docx", "doc", "PDF", "txt", "TXT"]

            if file_size > 5000000:
                response['status'] = 500
                response['status_message'] = 'File Size Bigger Than Expected'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if file_extension not in allowed_file_extensions:
                response['status'] = 500
                response['status_message'] = 'Malicious File'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if file_validation_obj.check_malicious_file_from_content(base64_content, allowed_file_extensions):
                response['status'] = 500
                response['status_message'] = 'Malicious File'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if not os.path.exists('secured_files/LiveChatApp/attachment'):
                os.makedirs('secured_files/LiveChatApp/attachment')

            path = os.path.join(settings.SECURE_MEDIA_ROOT,
                                "LiveChatApp/attachment/")

            fh = open(path + file_name, "wb")
            fh.write(base64.b64decode(base64_content))
            fh.close()

            path = "/secured_files/LiveChatApp/attachment/" + file_name

            file_access_management_obj = LiveChatFileAccessManagement.objects.create(
                file_path=path, is_public=False)
            
            file_access_management_obj = update_file_access_type(
                chat_type, group_id, user_group_id, receiver_username, request.user.username, file_access_management_obj, LiveChatUser, LiveChatInternalChatGroup, LiveChatInternalUserGroup)

            file_url = '/livechat/download-file/' + \
                str(file_access_management_obj.key) + '/' + file_name

            thumbnail_file_name = ""
            if file_extension in ["png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "jfif", "tiff", "exif", "bmp", "gif", "GIF"]:
                thumbnail_file_name = create_image_thumbnail(file_name)
            elif file_extension in ["MPEG", "mpeg", "MP4", "mp4", "MOV", "mov", "AVI", "avi", "flv"]:
                thumbnail_file_name = create_video_thumbnail(file_name)

            thumbnail_url = ""

            if thumbnail_file_name != "":
                path_of_thumbnail = "/secured_files/LiveChatApp/attachment/" + thumbnail_file_name
                file_access_management_obj = LiveChatFileAccessManagement.objects.create(
                    file_path=path_of_thumbnail, is_public=False)

                file_access_management_obj = update_file_access_type(
                    chat_type, group_id, user_group_id, receiver_username, request.user.username, file_access_management_obj, LiveChatUser, LiveChatInternalChatGroup, LiveChatInternalUserGroup)

                thumbnail_url = '/livechat/download-file/' + \
                    str(file_access_management_obj.key) + \
                    '/' + thumbnail_file_name

            response["status"] = 200
            response["src"] = file_url
            response["name"] = file_name
            response["thumbnail_url"] = thumbnail_url

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside LiveChatUploadInternalChatAttachmentAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status"] = 500
            response["name"] = "no_name"
            response["src"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


LiveChatUploadInternalChatAttachment = LiveChatUploadInternalChatAttachmentAPI.as_view()


class UpdateInternalChatHistoryAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            receiver_username = validation_obj.remo_html_from_string(
                data["receiver_username"])

            chat_index = data['chat_index']
            curr_user_username = request.user.username

            curr_user = LiveChatUser.objects.get(user=User.objects.get(
                username=str(curr_user_username)), is_deleted=False)

            if not curr_user:
                response['status_message'] = "Something went wrong. Please try again after refreshing the page"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            receiver_user = LiveChatUser.objects.filter(user=User.objects.get(
                username=str(receiver_username)), is_deleted=False)

            if receiver_user.exists():
                receiver_user = receiver_user.first()
                response["message_history"], response['all_chat_loaded'], response['last_seen_on_chat'] = get_internal_one_to_one_chat_message_history(
                    curr_user, receiver_user, chat_index, LiveChatInternalMISDashboard, LiveChatInternalUserGroup, LiveChatInternalChatLastSeen)

                response['last_seen_time'] = receiver_user.last_updated_time.timestamp() * 1000

            response["status"] = 200
            response["message"] = "success"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UpdateInternalChatHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateInternalChatHistory = UpdateInternalChatHistoryAPI.as_view()


class GetInternalChatGroupHistoryAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            group_id = data['group_id']
            chat_index = data['chat_index']

            group_obj = LiveChatInternalChatGroup.objects.filter(
                group_id=group_id, is_removed=False)

            if group_obj:
                group_obj = group_obj.first()
                curr_user = LiveChatUser.objects.get(user=request.user)
                response["message_history"], response['all_chat_loaded'] = get_internal_group_message_history(
                    group_obj, curr_user, chat_index, LiveChatInternalMISDashboard, LiveChatInternalChatGroupMembers)

                group_members = group_obj.members.filter(is_removed=False, has_left=False)

                if group_members:
                    try:
                        last_seen_time = group_members.first().user.last_updated_time.timestamp() * 1000
                    except Exception:
                        last_seen_time = 0

                    last_seen_on_chat = -1
                    for group_member in group_members:
                        if group_member.user.user == request.user:
                            continue
                        
                        last_seen_obj = LiveChatInternalChatLastSeen.objects.filter(user=group_member.user, group=group_obj)

                        if last_seen_obj:
                            if last_seen_on_chat == -1:
                                last_seen_on_chat = last_seen_obj.first().last_seen.timestamp() * 1000
                            else:
                                last_seen_on_chat = min(last_seen_on_chat, last_seen_obj.first().last_seen.timestamp() * 1000)
                        else:
                            last_seen_on_chat = 0

                        if group_member.user.last_updated_time:
                            last_seen_time = min(last_seen_time, group_member.user.last_updated_time.timestamp() * 1000)
                        else:
                            last_seen_time = 0

                response["status"] = 200
                response["message"] = "success"
                response["last_seen_time"] = last_seen_time
                response["last_seen_on_chat"] = last_seen_on_chat
            else:
                response['message'] = 'Group does not exists'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetInternalChatGroupHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetInternalChatGroupHistory = GetInternalChatGroupHistoryAPI.as_view()


class GetInternalUserGroupHistoryAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            group_id = data['group_id']
            chat_index = data['chat_index']

            user_group_obj = LiveChatInternalUserGroup.objects.filter(
                group_id=group_id)

            if user_group_obj:
                user_group_obj = user_group_obj.first()
                curr_user = LiveChatUser.objects.get(user=request.user)
                response["message_history"], response['all_chat_loaded'] = get_internal_user_group_message_history(
                    user_group_obj, curr_user, chat_index, LiveChatInternalMISDashboard)

                group_members = user_group_obj.members.all()

                try:
                    last_seen_time = group_members.first().last_updated_time.timestamp() * 1000
                except Exception:
                    last_seen_time = 0

                last_seen_on_chat = -1
                for group_member in group_members:
                    if group_member.user == request.user:
                        continue
                        
                    last_seen_obj = LiveChatInternalChatLastSeen.objects.filter(user=group_member, user_group=user_group_obj)

                    if last_seen_obj:
                        if last_seen_on_chat == -1:
                            last_seen_on_chat = last_seen_obj.first().last_seen.timestamp() * 1000
                        else:
                            last_seen_on_chat = min(last_seen_on_chat, last_seen_obj.first().last_seen.timestamp() * 1000)
                    else:
                        last_seen_on_chat = 0
                    
                    if group_member.last_updated_time:
                        last_seen_time = min(last_seen_time, group_member.last_updated_time.timestamp() * 1000)
                    else:
                        last_seen_time = 0

                response['last_seen_time'] = last_seen_time
                response['last_seen_on_chat'] = last_seen_on_chat
                response["status"] = 200
                response["message"] = "success"
            else:
                response['message'] = 'Group does not exists'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetInternalUserGroupHistoryAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "error"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetInternalUserGroupHistory = GetInternalUserGroupHistoryAPI.as_view()


class CheckImageFileAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            filename = data['filename']
            base64_content = data['base64_file']
            filedata = data['filedata']

            file_validation_obj = LiveChatFileValidation()

            if file_validation_obj.check_malicious_file(filename):
                response['status'] = 500
                response['message'] = 'File name is invalid. Please remove .(dot) from file name.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(
                    json.dumps(response))
                return Response(data=response)

            allowed_file_extensions = [
                "png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "jpe", ]

            if file_validation_obj.check_malicious_file_from_content(base64_content, allowed_file_extensions):
                response['status'] = 500
                response['message'] = 'File content is malicious. Please upload file in valid format.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(
                    json.dumps(response))
                return Response(data=response)

            response['status'] = 200
            response['message'] = "success"
            response['data'] = filedata
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside CheckImageFileAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "Unable to process your request. Please try again after some time."

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CheckImageFile = CheckImageFileAPI.as_view()


class SaveInternalChatAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = "Internal server Error"
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            message = data["message"]
            sender = data["sender"]
            sender = validation_obj.remo_html_from_string(sender).strip()
            attached_file_src = data["attached_file_src"]
            thumbnail_file_src = data["thumbnail_url"]
            receiver_username = data["receiver_username"]
            receiver_username = validation_obj.remo_html_from_string(
                receiver_username).strip()
            message = validation_obj.remo_html_from_string(message)
            sender_username = str(request.user.username).strip()
            attached_file_src = validation_obj.remo_html_from_string(attached_file_src)

            # Getting details for replied message by Supervisor/Admin
            is_replied_message = False
            reply_message_text = ""
            reply_attached_file_src = ""
            reply_thumbnail_file_src = ""
            is_uploaded_file = False

            if 'is_uploaded_file' in data:
                is_uploaded_file = data["is_uploaded_file"]

            if 'is_replied_message' in data:
                is_replied_message = data["is_replied_message"]

            if 'reply_message_text' in data:
                reply_message_text = data["reply_message_text"]

            if 'reply_attached_file_src' in data:
                reply_attached_file_src = data["reply_attached_file_src"]

            if 'reply_thumbnail_file_src' in data:
                reply_thumbnail_file_src = data["reply_thumbnail_file_src"]

            sender_obj = LiveChatUser.objects.filter(user=User.objects.get(
                username=sender_username), is_deleted=False).first()
            reply_attached_file_src = validation_obj.remo_html_from_string(reply_attached_file_src)

            admin_config = get_admin_config(sender_obj, LiveChatAdminConfig, LiveChatUser)
            if is_replied_message:
                if (reply_message_text and reply_message_text != ""):
                    reply_message_text = validation_obj.remo_html_from_string(reply_message_text)
                    if (not validation_obj.is_valid_url(reply_message_text) and not admin_config.is_special_character_allowed_in_chat):
                        reply_message_text = validation_obj.remove_special_charater_from_string(reply_message_text)

                if reply_message_text == "" and reply_attached_file_src == "":
                    response["status_code"] = "300"
            else:
                if (message and message != ""):
                    if (not validation_obj.is_valid_url(message) and not admin_config.is_special_character_allowed_in_chat):
                        message = validation_obj.remove_special_charater_from_string(message)
                
                if message == "" and attached_file_src == "":
                    response["status_code"] = "300"
            
            if response["status_code"] == "300":
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            sender_name = str(sender_obj.user.first_name) + \
                " " + str(sender_obj.user.last_name)

            if sender == "System":
                sender_name = "System"

            if sender_name.strip() == "":
                sender_name = str(sender_obj.user.username)

            attachment_file_name = ""
            preview_file_src = ""
            if attached_file_src != "":
                attachment_file_name = attached_file_src.split("/")[-1]

            reply_attachment_file_name = ""
            if reply_attached_file_src != "":
                reply_attachment_file_name = reply_attached_file_src.split(
                    "/")[-1]
            
            if is_replied_message and reply_attachment_file_name != "":
                if admin_config.is_special_character_allowed_in_file_name:
                    reply_attachment_file_name = validation_obj.replace_special_character_in_file_name(reply_attachment_file_name)
                elif(not is_uploaded_file and validation_obj.is_special_character_present_in_file_name(reply_attachment_file_name)):
                    response['status_code'] = "300"

            elif attachment_file_name != "":
                if admin_config.is_special_character_allowed_in_file_name:
                    attachment_file_name = validation_obj.replace_special_character_in_file_name(attachment_file_name)
                elif(not is_uploaded_file and validation_obj.is_special_character_present_in_file_name(attachment_file_name)):
                    response['status_code'] = "300"
                    
            if response['status_code'] == "300":
                response['status_message'] = 'Special characters are not allowed in file name'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            logger.info("inside SaveInternalChatAPI:",
                        extra={'AppName': 'LiveChat'})

            msg_info_obj = LiveChatInternalMessageInfo.objects.create(
                message_text=message, attached_file_src=attached_file_src, attached_file_name=attachment_file_name, thumbnail_file_src=thumbnail_file_src, preview_file_src=preview_file_src)

            # Save replied message details to Message Info Object
            if is_replied_message:
                msg_info_obj.is_replied_message = is_replied_message
                msg_info_obj.reply_message_text = reply_message_text
                msg_info_obj.reply_attached_file_src = reply_attached_file_src
                msg_info_obj.reply_attachment_file_name = reply_attachment_file_name
                msg_info_obj.reply_thumbnail_file_src = reply_thumbnail_file_src
                msg_info_obj.reply_message_time = timezone.now()
                msg_info_obj.save()

            if receiver_username == 'group':

                group_id = data['group_id']
                group_obj = LiveChatInternalChatGroup.objects.filter(
                    group_id=group_id)

                if group_obj:
                    group_obj[0].last_msg_datetime = timezone.now()
                    group_obj[0].save()
                    livechat_mis_obj = LiveChatInternalMISDashboard.objects.create(
                        sender_name=sender_name, sender=sender_obj, group=group_obj[0], message_info=msg_info_obj)
            elif receiver_username == 'user_group':

                group_id = data['group_id']
                group_obj = LiveChatInternalUserGroup.objects.filter(
                    group_id=group_id)

                if group_obj:
                    group_obj[0].last_msg_datetime = timezone.now()
                    group_obj[0].save()
                    livechat_mis_obj = LiveChatInternalMISDashboard.objects.create(
                        sender_name=sender_name, sender=sender_obj, user_group=group_obj[0], message_info=msg_info_obj)
            else:

                receiver_obj = LiveChatUser.objects.filter(
                    user=User.objects.get(username=receiver_username), is_deleted=False)

                if receiver_username != "" and receiver_obj.exists():
                    # this is one on one chat
                    receiver_obj = receiver_obj.first()
                    user_group_obj = check_and_update_user_group(
                        sender_obj, receiver_obj, LiveChatInternalUserGroup)

                    user_group_obj.last_msg_datetime = timezone.now()
                    user_group_obj.save()
                    livechat_mis_obj = LiveChatInternalMISDashboard.objects.create(
                        sender_name=sender_name, sender=sender_obj, receiver=receiver_obj, group=None, user_group=user_group_obj, message_info=msg_info_obj)

            message_dict = {}
            if livechat_mis_obj:
                curr_user = LiveChatUser.objects.filter(user__username=request.user.username)
                message_dict = get_message_history_dict(livechat_mis_obj, curr_user)
            
            response['message_dict'] = message_dict
            response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveAgentChatAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["status_message"] = str(e)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveInternalChat = SaveInternalChatAPI.as_view()


def InternalChatPage(request):
    from pytz import timezone
    try:
        if request.user.is_authenticated:
            user_obj = None
            try:
                user_obj = LiveChatUser.objects.get(user=User.objects.get(
                    username=str(request.user.username)), is_deleted=False)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("User Does Not Exist: %s at %s",
                             e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            if user_obj == None or (user_obj.is_allow_toggle and user_obj.status == '3'):
                return HttpResponseRedirect("/chat/login")

            admin_config = get_admin_config(
                user_obj, LiveChatAdminConfig, LiveChatUser)

            agent_obj_list = get_agents_and_supervisor_under_this_user(
                user_obj)
            
            if user_obj.status == '2':
                admin = get_admin_from_active_agent(user_obj, LiveChatUser)
                agent_obj_list.append(admin)

                if admin_config.allow_supervisor_to_add_supervisor:
                    agent_obj_list += get_other_supervisors(user_obj, admin)

            agents = []
            for agent in agent_obj_list:
                agents.append(agent.user.username)

            validation_obj = LiveChatInputValidation()

            sender_username = validation_obj.remo_html_from_string(
                request.user.username).strip()

            return render(request, 'LiveChatApp/internal_chat_console.html',
                          {
                              "sender_websocket_token": get_agent_token_based_on_username(sender_username),
                              "user_obj": user_obj,
                              "admin_config": admin_config,
                              "agents": agents,
                              "character_limit_small_text": LIVECHAT_CHARACTER_LIMIT_SMALL_TEXT,
                              "character_limit_large_text": LIVECHAT_CHARACTER_LIMIT_LARGE_TEXT,
                              "sender_name": user_obj.get_agent_name(),
                          })
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("InternalChatPage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
    return HttpResponseRedirect("/chat/login")


class CreateChatGroupAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()
            file_validation_obj = LiveChatFileValidation()

            group_name = data['group_name']
            group_name = validation_obj.remo_html_from_string(group_name)

            group_desc = data['group_desc']
            group_desc = validation_obj.remo_html_from_string(group_desc)

            group_members = data['group_members']

            user = request.user
            livechat_user = LiveChatUser.objects.get(
                user=user, is_deleted=False)
            livechat_user = check_if_livechat_only_admin(
                livechat_user, LiveChatUser)
            
            admin_config = get_admin_config(livechat_user, LiveChatAdminConfig, LiveChatUser)

            group_chat_obj = LiveChatInternalChatGroup.objects.filter(
                group_name__iexact=group_name, created_by=livechat_user, is_deleted=False)

            if group_chat_obj:
                response['message'] = 'Group with this name already exists in your account. Please use different group name.'
            elif len(group_members) + 1 > admin_config.group_size_limit:
                response['message'] = f'Exceeding group size limit of {admin_config.group_size_limit} members.'
            else:
                if 'filename' in data:
                    filename = data['filename']
                    base64_content = data['base64_file']

                    if file_validation_obj.check_malicious_file(filename):
                        response['status'] = 500
                        response['message'] = 'File name is invalid. Please remove .(dot) from file name.'
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)

                    allowed_file_extensions = [
                        "png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "jpe", ]

                    if file_validation_obj.check_malicious_file_from_content(base64_content, allowed_file_extensions):
                        response['status'] = 500
                        response['message'] = 'File content is malicious. Please upload file in valid format.'
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)

                group_chat_obj = LiveChatInternalChatGroup.objects.create(
                    group_name=group_name, group_description=group_desc, created_by=livechat_user)

                group_member_obj = LiveChatInternalChatGroupMembers.objects.create(
                    user=livechat_user, group=group_chat_obj)
                group_chat_obj.members.add(group_member_obj)

                livechat_users_list = get_agents_and_supervisor_under_this_user(livechat_user)
                admin = get_admin_from_active_agent(livechat_user, LiveChatUser)
                for member in group_members:
                    livechat_member = LiveChatUser.objects.filter(
                        user__username=member).first()

                    if livechat_member and (livechat_member == admin or livechat_member.status != 3 or livechat_member in livechat_users_list):
                        group_member_obj = LiveChatInternalChatGroupMembers.objects.create(
                            user=livechat_member, group=group_chat_obj)

                        group_chat_obj.members.add(group_member_obj)

                if 'filename' in data:

                    filename = generate_random_key(
                        10) + "_" + filename.replace(" ", "")

                    if not os.path.exists('files/group_icons/'):
                        os.makedirs('files/group_icons/')

                    path = os.path.join(settings.MEDIA_ROOT,
                                        "group_icons/")

                    fh = open(path + filename, "wb")
                    fh.write(base64.b64decode(base64_content))
                    fh.close()

                    path = 'files/group_icons/' + filename

                    group_chat_obj.icon_path = path

                group_chat_obj.save()

                response['status'] = 200
                description = "Group Created by name " + \
                    " (" + str(group_name) + " and group members " + \
                    str(group_members) + ")"
                add_audit_trail(
                    "LIVECHATAPP",
                    livechat_user.user,
                    "Create-Group",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside CreateChatGroupAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})
            response["message"] = "Unable to process your request. Please try again after some time."

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CreateChatGroup = CreateChatGroupAPI.as_view()


class UpdateChatGroupListAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}

        try:
            user = request.user

            try:
                livechat_user = LiveChatUser.objects.get(
                    user=user, is_deleted=False)
            except Exception:
                response['status'] = 500
                response['message'] = 'User does not exist'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            livechat_user = check_if_livechat_only_admin(
                livechat_user, LiveChatUser)

            group_member_objs = LiveChatInternalChatGroupMembers.objects.filter(
                user=livechat_user, is_deleted=False)

            group_chat_objs = LiveChatInternalChatGroup.objects.filter(
                members__in=group_member_objs).exclude(created_by=None).order_by('-last_msg_datetime')

            group_chat_list = get_group_chat_list(
                group_chat_objs, livechat_user, LiveChatInternalMISDashboard, LiveChatInternalChatGroupMembers, LiveChatInternalChatLastSeen)
            
            admin_config = get_admin_config(livechat_user, LiveChatAdminConfig, LiveChatUser)

            user_list = []
            if livechat_user.status == "1":
                agents_and_supervisors = get_agents_and_supervisor_under_this_user(livechat_user)
                check_and_create_bulk_user_groups(agents_and_supervisors, livechat_user, LiveChatInternalUserGroup)

            elif livechat_user.status == "2":
                agents_and_supervisors = livechat_user.agents.all()
                
                check_and_create_bulk_user_groups(agents_and_supervisors, livechat_user, LiveChatInternalUserGroup)

                admin_and_supervisors = LiveChatUser.objects.filter(
                    agents__in=[livechat_user])
                
                check_and_create_bulk_user_groups(admin_and_supervisors, livechat_user, LiveChatInternalUserGroup)

                if admin_config.allow_supervisor_to_add_supervisor:
                    admin = get_admin_from_active_agent(livechat_user, LiveChatUser)
                    supervisor_list = get_other_supervisors(livechat_user, admin)

                    check_and_create_bulk_user_groups(supervisor_list, livechat_user, LiveChatInternalUserGroup)

            elif livechat_user.status == "3":
                admin_and_supervisors = LiveChatUser.objects.filter(
                    agents__in=[livechat_user]).first()

                if admin_and_supervisors:
                
                    user_list = [admin_and_supervisors]
                    if admin_and_supervisors.status == '2':
                        admin = get_admin_from_active_agent(admin_and_supervisors, LiveChatUser)
                        user_list.append(admin)

                    check_and_create_bulk_user_groups(user_list, livechat_user, LiveChatInternalUserGroup)

            user_group_objs = LiveChatInternalUserGroup.objects.filter(
                members__in=[livechat_user]).order_by('-last_msg_datetime')
            user_group_list = get_user_group_list(
                user_group_objs, livechat_user, LiveChatInternalMISDashboard, LiveChatInternalChatLastSeen)

            # response['user_list'] = user_list
            response['sender_websocket_token'] = get_agent_token_based_on_username(
                str(request.user.username))
            response['group_chat_list'] = group_chat_list
            response['user_group_list'] = user_group_list
            response['status'] = 200
            response['message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside UpdateChatGroupListAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateChatGroupList = UpdateChatGroupListAPI.as_view()


class EditChatGroupDetailsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            group_id = data['group_id']

            group_obj = LiveChatInternalChatGroup.objects.get(
                group_id=group_id)

            if (group_obj.is_deleted or group_obj.is_removed) and 'remove_group' not in data and 'delete_group' not in data:
                response['message'] = 'You are not authorised to edit this group.'
            else:
                user = request.user
                livechat_user = LiveChatUser.objects.get(
                    user=user, is_deleted=False)
                livechat_user = check_if_livechat_only_admin(
                    livechat_user, LiveChatUser)
                
                admin_config = get_admin_config(livechat_user, LiveChatAdminConfig, LiveChatUser)

                group_member_obj = LiveChatInternalChatGroupMembers.objects.filter(
                    user=livechat_user, group=group_obj)

                validation_obj = LiveChatInputValidation()

                has_left = group_member_obj[0].has_left
                is_removed = group_member_obj[0].is_removed

                if not group_member_obj or group_member_obj[0].user.user.status == '3' or ((has_left or is_removed) and 'delete_group' not in data):
                    response['message'] = 'You are not authorised to edit this group.'
                else:

                    if 'desc' in data:
                        desc = data['desc']
                        desc = validation_obj.remo_html_from_string(desc)
                        group_obj.group_description = desc
                        msg_info_obj = LiveChatInternalMessageInfo.objects.create(
                            message_text='changed the group description')
                        LiveChatInternalMISDashboard.objects.create(
                            sender_name='System', sender=livechat_user, group=group_obj, message_info=msg_info_obj)

                    if 'name' in data:
                        name = data['name']
                        name = validation_obj.remo_html_from_string(name)

                        chat_group_obj = LiveChatInternalChatGroup.objects.filter(
                            group_name__iexact=name, created_by=livechat_user, is_removed=False)

                        if chat_group_obj:
                            response['message'] = 'Group with this name already exists in your account. Please use different group name.'
                            custom_encrypt_obj = CustomEncrypt()
                            response = custom_encrypt_obj.encrypt(
                                json.dumps(response))
                            return Response(data=response)

                        group_obj.group_name = name
                        msg_info_obj = LiveChatInternalMessageInfo.objects.create(
                            message_text='changed the group name')
                        LiveChatInternalMISDashboard.objects.create(
                            sender_name='System', sender=livechat_user, group=group_obj, message_info=msg_info_obj)

                    if 'added_members' in data:
                        added_members = data['added_members']

                        if len(added_members) + group_obj.members.filter(is_removed=False, has_left=False).count() > admin_config.group_size_limit:
                            response["message"] = f'Exceeding group size limit of {admin_config.group_size_limit} members.'
                            custom_encrypt_obj = CustomEncrypt()
                            response = custom_encrypt_obj.encrypt(
                                json.dumps(response))
                            return Response(data=response)

                        livechat_users_list = get_agents_and_supervisor_under_this_user(livechat_user)
                        admin = get_admin_from_active_agent(livechat_user, LiveChatUser)
                        for member in added_members:
                            livechat_member = LiveChatUser.objects.filter(
                                user__username=member).first()

                            if livechat_member and (livechat_member == admin or livechat_member.status != 3 or livechat_member in livechat_users_list):
                                group_member_obj = LiveChatInternalChatGroupMembers.objects.filter(
                                    user=livechat_member, group=group_obj)

                                if group_member_obj:
                                    group_member_obj[0].is_removed = False
                                    group_member_obj[0].is_deleted = False
                                    group_member_obj[0].has_left = False
                                    group_member_obj[0].save()
                                else:
                                    group_member_obj = LiveChatInternalChatGroupMembers.objects.create(
                                        user=livechat_member, group=group_obj)
                                    group_obj.members.add(group_member_obj)

                                msg_text = 'added ' + member + ' to the chat'
                                msg_info_obj = LiveChatInternalMessageInfo.objects.create(
                                    message_text=msg_text)
                                LiveChatInternalMISDashboard.objects.create(
                                    sender_name='System', sender=livechat_user, group=group_obj, message_info=msg_info_obj)

                    if 'remove_member' in data:
                        member = data['remove_member']

                        livechat_member = LiveChatUser.objects.filter(
                            user__username=member)
                        group_member_obj = LiveChatInternalChatGroupMembers.objects.filter(
                            user=livechat_member[0], group=group_obj)
                        if group_member_obj:
                            remove_datetime = timezone.now()
                            group_member_obj[0].is_removed = True

                            group_member_obj[0].remove_datetime = remove_datetime
                            group_member_obj[0].save()
                            msg_text = 'removed ' + member + ' from the chat'
                            msg_info_obj = LiveChatInternalMessageInfo.objects.create(
                                message_text=msg_text)
                            LiveChatInternalMISDashboard.objects.create(
                                message_datetime=remove_datetime, sender_name='System', sender=livechat_user, group=group_obj, message_info=msg_info_obj)

                    if 'delete_group' in data:
                        if group_obj.created_by != livechat_user:
                            group_member_obj[0].is_deleted = True
                            group_member_obj[0].save()
                        else:
                            group_obj.is_deleted = True
                            group_obj.delete_datetime = timezone.now()

                            group_member_obj[0].is_deleted = True
                            group_member_obj[0].save()
                            msg_text = 'This group is deleted'
                            msg_info_obj = LiveChatInternalMessageInfo.objects.create(
                                message_text=msg_text)
                            LiveChatInternalMISDashboard.objects.create(
                                message_datetime=group_obj.delete_datetime, sender_name='System', sender=livechat_user, group=group_obj, message_info=msg_info_obj)

                    if 'remove_group' in data:
                        if group_obj.created_by != livechat_user:
                            response["message"] = 'You are not authorised to remove this group'
                            custom_encrypt_obj = CustomEncrypt()
                            response = custom_encrypt_obj.encrypt(
                                json.dumps(response))
                            return Response(data=response)

                        group_obj.is_removed = True
                        group_obj.removed_datetime = timezone.now()

                    group_obj.last_updated_datetime = timezone.now()
                    group_obj.last_msg_datetime = timezone.now()
                    group_obj.save()

                    response['status'] = 200
                    response['message'] = 'success'

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside EditChatGroupDetailsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EditChatGroupDetails = EditChatGroupDetailsAPI.as_view()


class GetLiveChatUserDetailsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        import pytz
        import os
        response = {}
        response['status'] = 500
        tz = pytz.timezone(settings.TIME_ZONE)
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = LiveChatInputValidation()

            username = data['username']

            username = validation_obj.remo_html_from_string(username)

            livechat_user = LiveChatUser.objects.get(
                user=User.objects.get(username=username), is_deleted=False)
            full_name = str(livechat_user.user.first_name) + \
                " " + str(livechat_user.user.last_name)

            if livechat_user.status == "1":
                response["user_status"] = "Admin"
            elif livechat_user.status == "2":
                response["user_status"] = "Supervisor"
            else:
                response["user_status"] = "Agent"

            response["last_seen_date"] = get_livechat_date_format(
                livechat_user.last_updated_time.astimezone(tz))
            response["last_seen_time"] = get_time(
                livechat_user.last_updated_time)
            response['status'] = 200
            response['message'] = 'success'
            response["email"] = str(livechat_user.user.email)
            response["phone"] = str(livechat_user.phone_number)
            response["name"] = full_name.strip()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside GetLiveChatUserDetailsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLiveChatUserDetails = GetLiveChatUserDetailsAPI.as_view()


class AddUsertoUserGroupAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        import pytz
        import os
        response = {}
        response['status'] = 500
        response['message'] = 'Failed to add users.'
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user = request.user
            livechat_user = LiveChatUser.objects.get(
                user=user, is_deleted=False)
            livechat_user = check_if_livechat_only_admin(
                livechat_user, LiveChatUser)
            
            if livechat_user.status == '3':
                response['message'] = 'You are not authorized to add members.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            
            admin_config = get_admin_config(livechat_user, LiveChatAdminConfig, LiveChatUser)

            is_user_group = data['is_user_group']
            selected_users = data['selected_users']

            if not is_user_group:
                if len(selected_users) + 2 > admin_config.group_size_limit:
                    response['message'] = f'Exceeding group size limit of {admin_config.group_size_limit} members.'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                chat_belong_to = data['chat_belong_to']

                user_obj = LiveChatUser.objects.filter(
                    user__username=chat_belong_to).first()
                user = LiveChatUser.objects.filter(
                    user__username=request.user.username).first()

                user_group_obj = check_and_update_user_group(
                    user_obj, user, LiveChatInternalUserGroup)

                user_group_obj.chat_belong_to = user_obj
            else:

                group_id = data['group_id']
                user_group_obj = LiveChatInternalUserGroup.objects.filter(
                    group_id=group_id)

                if user_group_obj:
                    user_group_obj = user_group_obj.first()

                    if len(selected_users) + user_group_obj.members.all().count() > admin_config.group_size_limit:
                        response['message'] = f'Exceeding group size limit of {admin_config.group_size_limit} members.'
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(json.dumps(response))
                        return Response(data=response)

            for username in selected_users:
                user_obj = LiveChatUser.objects.filter(
                    user__username=username).first()

                if user_obj:
                    user_group_obj.members.add(user_obj)

                    msg_text = 'added ' + username + ' to the chat'
                    msg_info_obj = LiveChatInternalMessageInfo.objects.create(
                        message_text=msg_text)
                    LiveChatInternalMISDashboard.objects.create(
                        sender_name='System', sender=livechat_user, user_group=user_group_obj, message_info=msg_info_obj)

            user_group_obj.is_converted_into_group = True
            user_group_obj.last_updated_time = timezone.now()
            user_group_obj.save()

            response['group_id'] = str(user_group_obj.group_id)
            response["status"] = 200
            response['message'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside AddUsertoUserGroupAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AddUsertoUserGroup = AddUsertoUserGroupAPI.as_view()


class UpdateLastSeenOnChatsAPI(APIView):
    permission_classes = (IsAuthenticated,)
 
    def post(self, request, *args, **kwargs):
        import pytz
        import os
        response = {}
        response['status'] = 500
        response['message'] = 'Failed to update last seen.'
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            user = request.user
            livechat_user = LiveChatUser.objects.get(
                user=user, is_deleted=False)
            livechat_user = check_if_livechat_only_admin(
                livechat_user, LiveChatUser)

            validation_obj = LiveChatInputValidation()
            
            if 'single_chats' in data:
                single_chats = data['single_chats']

                for user_name in single_chats:
                    receiver_obj = LiveChatUser.objects.filter(
                        user=User.objects.get(username=user_name), is_deleted=False)

                    if user_name != "" and receiver_obj.exists():
                        receiver_obj = receiver_obj.first()
                        
                        user_group_obj = check_and_update_user_group(
                            livechat_user, receiver_obj, LiveChatInternalUserGroup)
                        
                        last_seen_obj = get_last_seen_object_based_user_group(livechat_user, user_group_obj, LiveChatInternalChatLastSeen)

                        last_seen_time = single_chats[user_name]
                        last_seen_time = datetime.fromtimestamp(last_seen_time / 1000.0)

                        last_seen_obj.last_seen = last_seen_time
                        last_seen_obj.save()
            
            if 'groups' in data:
                groups = data['groups']

                for group_id in groups:
                    if not validation_obj.is_valid_uuid(group_id):
                        continue

                    group_obj = LiveChatInternalChatGroup.objects.filter(group_id=group_id)

                    if group_obj:
                        group_obj = group_obj.first()

                        last_seen_obj = get_last_seen_object_based_group(livechat_user, group_obj, LiveChatInternalChatLastSeen)

                        last_seen_time = groups[group_id]
                        last_seen_time = datetime.fromtimestamp(last_seen_time / 1000.0)

                        last_seen_obj.last_seen = last_seen_time
                        last_seen_obj.save()

            if 'user_groups' in data:
                user_groups = data['user_groups']

                for group_id in user_groups:
                    if not validation_obj.is_valid_uuid(group_id):
                        continue
                    
                    group_obj = LiveChatInternalUserGroup.objects.filter(group_id=group_id)

                    if group_obj:
                        group_obj = group_obj.first()

                        last_seen_obj = get_last_seen_object_based_user_group(livechat_user, group_obj, LiveChatInternalChatLastSeen)

                        last_seen_time = user_groups[group_id]
                        last_seen_time = datetime.fromtimestamp(last_seen_time / 1000.0)

                        last_seen_obj.last_seen = last_seen_time
                        last_seen_obj.save()

            response["status"] = 200
            response['message'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside UpdateLastSeenOnChatsAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateLastSeenOnChats = UpdateLastSeenOnChatsAPI.as_view()


class LeaveGroupAPI(APIView):
    permission_classes = (IsAuthenticated,)
 
    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['message'] = 'Failed to leave group.'
        try:
            group_id = kwargs['group_id']

            group_obj = LiveChatInternalChatGroup.objects.get(
                group_id=group_id)

            livechat_member = LiveChatUser.objects.filter(
                user__username=request.user.username)

            group_member_obj = LiveChatInternalChatGroupMembers.objects.filter(
                user=livechat_member.first(), group=group_obj)

            if group_member_obj:
                group_member_obj[0].has_left = True
                
                leave_datetime = timezone.now()
                group_member_obj[0].left_datetime = leave_datetime
                group_member_obj[0].save()
                msg_text = f'{request.user.username} has left the chat'
                msg_info_obj = LiveChatInternalMessageInfo.objects.create(
                    message_text=msg_text)
                LiveChatInternalMISDashboard.objects.create(
                    message_datetime=leave_datetime, sender_name='System', sender=livechat_member.first(), group=group_obj, message_info=msg_info_obj)

                response['status'] = 200
                response['message'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside LeaveGroupAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

LeaveGroup = LeaveGroupAPI.as_view()


class SetChatStartedAPI(APIView):
    permission_classes = (IsAuthenticated,)
 
    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        response['message'] = 'Failed to leave group.'
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            is_user_group = data['is_user_group']

            user_obj = LiveChatUser.objects.get(
                user__username=request.user.username)

            if not is_user_group:
                username = data['username']

                livechat_member = LiveChatUser.objects.get(
                    user__username=username)

                user_group_obj = check_and_update_user_group(user_obj, livechat_member, LiveChatInternalUserGroup)
            else:
                user_group_id = data['user_group_id']
                user_group_obj = LiveChatInternalUserGroup.objects.filter(group_id=user_group_id, members__in=[user_obj]).first()
            
            if user_group_obj:
                user_group_obj.is_chat_started = True
                user_group_obj.last_msg_datetime = timezone.now()
                user_group_obj.save()

                response['status'] = 200
                response['message'] = 'success'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside SetChatStartedAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

SetChatStarted = SetChatStartedAPI.as_view()
