from EasyChatApp.utils_validation import EasyChatFileValidation, EasyChatInputValidation
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django.conf import settings
from django.utils.encoding import smart_str

from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect, redirect

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_bot import *
from EasyChatApp.utils_analytics import *
from EasyChatApp.utils_build_bot import build_bot, update_word_dictionary
from EasyChatApp.utils_processor_validator import create_default_processor_validators
from DeveloperConsoleApp.utils import get_developer_console_settings
from django.http import HttpResponseNotFound, HttpResponseBadRequest

from EasyChatApp.export_bot import export_data, export_faq_excel, export_data_as_zip, export_large_bot, generate_alexa_training_json, export_intent, export_multilingual_intent_excel
from EasyChatApp.import_bot import import_data, import_data_as_zip, import_intent, add_multilingual_intents_into_bot_from_excel
from DeveloperConsoleApp.constants import MASKING_PII_DATA_OTP_EMAIL
from EasySearchApp.models import *
from EasyChatApp.lead_deploy_script import *
from LiveChatApp.models import LiveChatUser, LiveChatCategory
from LiveChatApp.utils import get_livechat_category_object
from EasyAssistApp.models import CobrowseAccessToken
from EasyTMSApp.models import TicketCategory, Agent
from EasyChat.settings import *
from django.db.models import Q
from slugify import slugify
from EasyChatApp.utils_mailer_analytics import send_test_mail_based_on_config
from EasyChat.settings import BASE_DIR
from django.http import FileResponse
from nltk.corpus import stopwords
import json
import logging
import sys
import threading
import os.path

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class BotsListsAPI(APIView):
    
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            if is_allowed(request, [BOT_BUILDER_ROLE]):

                user_obj = request.user
                bot_obj_list = get_uat_bots(user_obj)
                bot_obj_list = bot_obj_list.order_by('-created_datetime')
                is_bot_shareable = Config.objects.all()[0].is_bot_shareable
                is_user_guest = user_obj.is_guest
                
                response["status"] = 200
                response["data"] = {
                    "get_bot_related_access_perm": request.user.get_bot_related_access_perm(),
                    "bot_obj_list": list(bot_obj_list.values("name", "is_lead_generation_enabled", "is_form_assist_enabled", "bot_image", "is_easy_search_allowed", "is_form_assist_enabled", "font", "id")),
                    "no_of_bots": bot_obj_list.count(),
                    "is_bot_shareable": is_bot_shareable,
                    "is_sandbox_user": request.user.is_sandbox_user,
                    "is_user_guest": is_user_guest,
                    "is_chatbot_creation_allowed": request.user.is_chatbot_creation_allowed,
                }
                response["message"] = "Success"
                
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("BotsListsAPI %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response["status"] = 500
            response["message"] = "We are currently unable to load your bots. Please try again later."

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response, default=str))
        return Response(data=response)


def BotConsole(request):
    request.session["EASYCHAT_VERSION"] = settings.EASYCHAT_VERSION
    request.session[
        "EASYCHAT_DATE_OF_RELEASE"] = settings.EASYCHAT_DATE_OF_RELEASE
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):

            logger.info("Into Bot Console....", extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            is_bot_shareable = Config.objects.all()[0].is_bot_shareable
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            is_livechat_manager = check_two_minute_livechat_manager(username)
            is_easy_search_user = is_it_easysearch_manager(username)
            is_easy_assist_admin = is_it_easyassist_admin(username)
            is_easytms_admin = is_it_easytms_admin(username, Agent)
            manager_objs = []

            try:
                supervisor_obj = Supervisor.objects.filter(
                    supervisor=user_obj).first()
                manager_objs = supervisor_obj.managers.all()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("BotConsole %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            # Specific AllinCall Access Changes
            if user_obj.username.endswith("@getcogno.ai"):
                if manager_objs != []:
                    manager_objs = manager_objs | User.objects.filter(
                        username__icontains="@getcogno.ai")
                else:
                    manager_objs = User.objects.filter(
                        username__icontains="@getcogno.ai")

            # Share access for Sandbox users

            try:
                if user_obj.username.endswith("@getcogno.ai"):
                    for sandbox_user_obj in user_obj.sandbox_users.all():
                        if manager_objs != []:
                            manager_objs = manager_objs | User.objects.filter(username=sandbox_user_obj.username)
                        else:
                            manager_objs = User.objects.filter(username=sandbox_user_obj.username)
                        
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("BotConsole %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            bot_obj_list = get_uat_bots(user_obj)
            user_objs = User.objects.all()
            shared_with = {}

            master_languages = Language.objects.all()

            for bot in bot_obj_list:
                managers_per_bot = bot.users.filter(
                    username__in=[manager.username for manager in manager_objs])
                shared_with[bot.pk] = [(managers_per_bot, bot.created_by == user_obj)]
                
            bot_obj_list = bot_obj_list.order_by('-created_datetime')

            all_channels = Channel.objects.filter(is_easychat_channel=True)
            voice_channels = []
            non_voice_channels = []

            for channel in all_channels:
                if channel.name in ["Alexa", "GoogleHome", "Voice"]:
                    voice_channels.append({
                        "name": channel_name_formatter(channel.name),
                        "icon": channel.icon,
                        "channel_id": convert_to_channel_url_param(channel.name),
                        "channel_pk": channel.id,
                    })
                else:
                    non_voice_channels.append({
                        "name": channel_name_formatter(channel.name),
                        "icon": channel.icon,
                        "channel_id": convert_to_channel_url_param(channel.name),
                        "channel_pk": channel.id,
                    })

            is_user_guest = user_obj.is_guest

            is_chatbot_allowed = True
            is_tms_allowed = is_tms_access_allowed(request, Agent)
            is_livechat_allowed = is_livechat_access_allowed(request, BotInfo)
            is_easyassist_allowed = is_easyassist_access_allowed(request)
            
            return render(request, 'EasyChatApp/platform/bots.html', {
                "get_bot_related_access_perm": request.user.get_bot_related_access_perm(),
                "bot_obj_list": bot_obj_list,
                "no_of_bots": bot_obj_list.count(),
                "user_objs": user_objs,
                "is_bot_shareable": is_bot_shareable,
                "manager_objs": manager_objs,
                "shared_with": shared_with,
                "is_user_guest": is_user_guest,
                "is_bot_manager_user": Supervisor.objects.filter(managers__in=[request.user]).count() != 0,
                "expanded_logo": True,
                "master_languages": master_languages,
                "is_livechat_manager": is_livechat_manager,
                "is_easy_search_user": is_easy_search_user,
                "is_easy_assist_admin": is_easy_assist_admin,
                "is_easytms_admin": is_easytms_admin,
                "voice_channels": voice_channels,
                "non_voice_channels": non_voice_channels,
                "is_chatbot_allowed": is_chatbot_allowed,
                "is_tms_allowed": is_tms_allowed,
                "is_livechat_allowed": is_livechat_allowed,
                "is_easyassist_allowed": is_easyassist_allowed,
            })
        else:
            return HttpResponseRedirect("/chat/login/")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("BotConsole %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        # return HttpResponse("500")
        return render(request, 'EasyChatApp/error_500.html')


def CreateQuickBotConsole(request):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):

            bot_pk = request.GET["bot_pk"]
            selected_bot_obj = None
            if "bot_pk" in request.GET:
                bot_pk = request.GET["bot_pk"]
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

            if selected_bot_obj == None:
                return HttpResponse("Page not found")

            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            bot_objs = get_uat_bots(user_obj)
            description = "Bot has been created for (" + username + ")."
            add_audit_trail(
                "EASYCHATAPP",
                user_obj,
                "Add-Bot",
                description,
                json.dumps({}),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )
            return render(request, 'EasyChatApp/platform/create_quick_bot.html', {
                "bot_objs": bot_objs,
                "selected_bot_obj": selected_bot_obj,
                "bot_pk": bot_pk,
                "selected_language": "en",
            })
        else:
            return HttpResponseRedirect("/chat/login/")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("CreateQuickBotConsole: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        # return HttpResponse("500")
        return render(request, 'EasyChatApp/error_500.html')


class DeleteBotImageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Can't delete bot image."
        error = False
        try:
            data = request.data
            validation_obj = EasyChatInputValidation()
            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)
            if "bot_id" in data:
                bot_id = data["bot_id"]
                bot_id = validation_obj.remo_html_from_string(bot_id)
            else:
                response["status"] = 400
                response["message"] = "Bot id not found."
                error = True

            bot_objs = Bot.objects.filter(
                pk=int(bot_id), is_uat=True, is_deleted=False)
            if bot_objs.exists():
                bot_obj = bot_objs.first()
            else:
                response["status"] = 400
                response["message"] = "Bot doesn't exist for the provided bot id."
                error = True

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = "You are not authorised to perform this operation."
                error = True

            if error == False:
                bot_obj.bot_image = None
                bot_obj.save()
                response["status"] = 200
                response["message"] = "Bot image deleted successfully."

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteBotImage: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
            response["status"] = 500
            response["message"] = "Can't delete bot image."

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


def DeleteBotLogo(request, bot_pk):
    try:
        bot_obj = Bot.objects.get(pk=int(bot_pk), is_uat=True)
        bot_obj.bot_logo = None
        bot_obj.save()
        return HttpResponseRedirect("/chat/channels/web/?id=" + str(bot_obj.pk))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("DeleteBotLogo: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        # return HttpResponse("500")
        return render(request, 'EasyChatApp/error_500.html')


def DeleteMessageImage(request, bot_pk):
    try:
        bot_obj = Bot.objects.get(pk=int(bot_pk), is_uat=True)
        bot_obj.message_image = None
        bot_obj.save()
        return HttpResponseRedirect("/chat/channels/web/?id=" + str(bot_obj.pk))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("DeleteMessageImage: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        return HttpResponse("500")


def ExportBot(request, bot_pk):
    try:
        response = {}
        response["status_code"] = 500
        response["status_message"] = ""
        if is_allowed(request, [BOT_BUILDER_ROLE]) and request.method == "GET":
            user_obj = request.user
            bot_obj = Bot.objects.filter(pk=int(bot_pk), is_uat=True, is_deleted=False).first()
            if not bot_obj or user_obj not in bot_obj.users.all():
                return render(request, 'EasyChatApp/unauthorized.html')
            file_url, _ = export_data(bot_obj.slug, bot_pk, None)

            audit_trail_data = json.dumps({
                "bot_pk": bot_obj.pk
            })
            save_audit_trail(
                user_obj, EXPORT_BOT_AS_JSON_ACTION, audit_trail_data)
            return HttpResponseRedirect(f'/{file_url}')
        else:
            # return HttpResponse(500)
            return render(request, 'EasyChatApp/error_500.html')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Export Bot: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        # return HttpResponse("500")
        return render(request, 'EasyChatApp/error_500.html')


def ExportIntent(request, intent_pk):

    try:
        response = {}
        response["status_code"] = 500
        response["status_message"] = ""
        if is_allowed(request, [BOT_BUILDER_ROLE]) and request.method == "GET":
            user_obj = User.objects.get(username=str(request.user.username))
            filename = export_intent(intent_pk)
            path_to_file = '/files/private/' + str(filename)
            response = HttpResponse(
                status=200, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(
                str(filename))
            response['X-Sendfile'] = smart_str(path_to_file)
            response['X-Accel-Redirect'] = path_to_file
            audit_trail_data = json.dumps({
                "intent_pk": intent_pk
            })
            save_audit_trail(
                user_obj, EXPORT_INTENT_AS_JSON_ACTION, audit_trail_data)
            return response
        else:
            return render(request, 'EasyChatApp/error_500.html')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Export Intent: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None'})


def ExportBotAsZip(request, bot_pk):
    try:
        response = {}
        response["status_code"] = 500
        response["status_message"] = ""
        if is_allowed(request, [BOT_BUILDER_ROLE]) and request.method == "GET":
            user_obj = request.user
            bot_obj = Bot.objects.filter(pk=int(bot_pk), is_uat=True, is_deleted=False).first()
            if not bot_obj or user_obj not in bot_obj.users.all():
                return render(request, 'EasyChatApp/unauthorized.html')

            file_path, bytes_io = export_data_as_zip(bot_obj.slug, bot_pk)

            if file_path != "None":
                audit_trail_data = json.dumps({
                    "bot_pk": bot_obj.pk
                })
                save_audit_trail(
                    user_obj, EXPORT_BOT_AS_ZIP_ACTION, audit_trail_data)

                response = HttpResponse(
                    bytes_io.getvalue(), content_type="application/x-zip-compressed")
                response['Content-Disposition'] = 'attachment; filename=%s' % file_path

                return response

            # return HttpResponse("Internal server error.")
            return render(request, 'EasyChatApp/error_500.html')
        else:
            # return HttpResponse(500)
            return render(request, 'EasyChatApp/error_500.html')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Export Bot As ZIP: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        # return HttpResponse("500")
        return render(request, 'EasyChatApp/error_500.html')


def ExportMultilingualIntentsAsExcel(request, bot_pk):
    try:
        response = {}
        response["status_code"] = 500
        response["status_message"] = ""
        if is_allowed(request, [BOT_BUILDER_ROLE]) and request.method == "GET":
            bot_obj = Bot.objects.filter(pk=int(bot_pk), is_uat=True, is_deleted=False).first()
            if not bot_obj or request.user not in bot_obj.users.all():
                return render(request, 'EasyChatApp/unauthorized.html')
            file_url = export_multilingual_intent_excel(bot_obj)
            if file_url == None:
                return render(request, 'EasyChatApp/error_500.html')

            return HttpResponseRedirect(f'/{file_url}')
        else:
            return render(request, 'EasyChatApp/error_500.html')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ExportMultilingualIntentsAsExcel: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        # return HttpResponse("500")
        return render(request, 'EasyChatApp/error_500.html')


def ExportFAQExcel(request, bot_pk):
    try:
        response = {}
        response["status_code"] = 500
        response["status_message"] = ""
        if is_allowed(request, [BOT_BUILDER_ROLE]) and request.method == "GET":
            bot_obj = Bot.objects.filter(pk=int(bot_pk), is_uat=True, is_deleted=False).first()
            if not bot_obj or request.user not in bot_obj.users.all():
                return render(request, 'EasyChatApp/unauthorized.html')
            file_url = export_faq_excel(bot_obj)

            if file_url == None:
                # return HttpResponse(500)
                return render(request, 'EasyChatApp/error_500.html')

            return HttpResponseRedirect(f'/{file_url}')
        else:
            # return HttpResponse(500)
            return render(request, 'EasyChatApp/error_500.html')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ExportFAQExcel: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        # return HttpResponse("500")
        return render(request, 'EasyChatApp/error_500.html')


def ExportAlexaJSON(request, bot_pk):
    try:
        response = {}
        response["status_code"] = 500
        response["status_message"] = ""
        if is_allowed(request, [BOT_BUILDER_ROLE]) and request.method == "GET":
            bot_obj = Bot.objects.filter(pk=int(bot_pk), is_deleted=False).first()
            if not bot_obj or request.user not in bot_obj.users.all():
                return render(request, 'EasyChatApp/unauthorized.html')

            path_to_file = generate_alexa_training_json(bot_pk, Bot, Intent)

            if path_to_file == None:
                # return HttpResponse(500)
                return render(request, 'EasyChatApp/error_500.html')

            return HttpResponseRedirect(f'/{path_to_file}')
        else:
            # return HttpResponse(500)
            return render(request, 'EasyChatApp/error_500.html')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ExportFAQExcel: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        # return HttpResponse("500")
        return render(request, 'EasyChatApp/error_500.html')


def EditBot(request, bot_pk):  # noqa: N802
    if request.user.is_authenticated:
        try:
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            is_livechat_manager = is_it_livechat_manager(username, bot_pk)
            is_easy_search_user = is_it_easysearch_manager(username)
            is_easy_assist_admin = is_it_easyassist_admin(username)
            is_easytms_admin = is_it_easytms_admin(username, Agent)

            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_uat=True, is_deleted=False)
            if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                return HttpResponseNotFound("You do not have access to this page")
                # return render(request, 'EasyChatApp/error_404.html')

            selected_language = "en"
            if "selected_language" in request.GET:
                selected_language = request.GET["selected_language"]

            is_g_search_enabled = True
            is_e_search_enabled = False
            search_cx = ""
            search_obj = None
            website_link_obj = None

            website_link_size = 0
            if bot_obj.is_easy_search_allowed:
                try:
                    easy_search_cofig = EasySearchConfig.objects.get(
                        bot=bot_obj)
                    config_feature = easy_search_cofig.feature
                    if config_feature == "1":
                        is_e_search_enabled = True
                        try:
                            search_obj = SearchUser.objects.get(user=user_obj)
                            website_link_obj = WebsiteLink.objects.filter(
                                search_user=search_obj, bot=bot_obj)
                            website_link_size = len(website_link_obj)
                            search_cx = easy_search_cofig.search_cx
                            if search_cx == None:
                                search_cx = ""
                        except Exception:
                            pass
                    elif config_feature == "2":
                        is_g_search_enabled = True
                        search_cx = easy_search_cofig.search_cx
                        try:
                            search_obj = SearchUser.objects.get(user=user_obj)
                            website_link_obj = WebsiteLink.objects.filter(
                                search_user=search_obj, bot=bot_obj)
                            website_link_size = len(website_link_obj)
                        except Exception:
                            pass
                except Exception:
                    easy_search_cofig = ""

            is_livechat_enabled = bot_obj.is_livechat_enabled
            is_easy_search_allowed = bot_obj.is_easy_search_allowed
            is_form_assist_enabled = bot_obj.is_form_assist_enabled
            is_lead_generation_enabled = bot_obj.is_lead_generation_enabled
            is_easy_assist_allowed = bot_obj.is_easy_assist_allowed
            is_pdf_search_allowed = bot_obj.is_pdf_search_allowed
            is_tms_allowed = bot_obj.is_tms_allowed
            is_feedback_required = bot_obj.is_feedback_required
            is_synonyms_included_in_paraphrase = bot_obj.is_synonyms_included_in_paraphrase
            is_email_notifiication_enabled = bot_obj.is_email_notifiication_enabled
            # is_nps_required = bot_obj.is_nps_required

            bot_inactivity_detection_enabled = bot_obj.is_inactivity_timer_enabled
            bot_inactivity_msg = bot_obj.bot_inactivity_response
            bot_inactivity_time = bot_obj.bot_inactivity_timer
            bot_response_delay_message = bot_obj.bot_response_delay_message

            is_theme_greater_than_five = False
            if (bot_obj.default_theme != None):
                try:
                    theme_no = int(bot_obj.default_theme.name.split("_")[-1])

                    if(theme_no > 4):
                        is_theme_greater_than_five = True
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("EditBot %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

            is_analytics_monitoring_enabled = bot_obj.is_analytics_monitoring_enabled
            show_form_enabled = bot_obj.show_livechat_form_or_no
            use_customer_details_processor = bot_obj.use_show_customer_detail_livechat_processor
            use_end_chat_processor = bot_obj.use_end_chat_processor_livechat

            email_config_obj = None
            email_config_channel_list = []
            email_config_analytics_list = []
            email_config_logs_list = []
            email_config_email_address_list = []

            profile_dict = get_mailer_profile_data(
                bot_obj, EasyChatMailerAnalyticsProfile, EasyChatMailerTableParameters)

            trees = Tree.objects.exclude(children=None)
            flows = Intent.objects.filter(
                bots__in=[bot_obj], tree__in=trees, is_hidden=False, is_deleted=False)
            traffic_objs = TrafficSources.objects.filter(
                bot=bot_obj).values('web_page').distinct()

            if is_email_notifiication_enabled:
                try:
                    email_config_obj = EmailConfiguration.objects.get(
                        bot=bot_obj)
                    email_config_email_address = json.loads(
                        email_config_obj.email_address)
                    email_config_logs_list = json.loads(
                        email_config_obj.chat_history)
                    email_config_analytics_list = json.loads(
                        email_config_obj.analytics)
                    email_config_channel_list = json.loads(
                        email_config_obj.channel)
                    for email_addresses in email_config_email_address:
                        email_config_email_address_list.append(
                            {"tag": email_addresses})

                except Exception:
                    logger.info(
                        "Email Configuration object not present for bot id: " + str(bot_obj.pk), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

            analytics_monitoring_obj = None
            analytics_monitoring_email_address_list = []

            start_hour, end_hour = "", ""

            if is_analytics_monitoring_enabled:
                try:
                    analytics_monitoring_obj = AnalyticsMonitoring.objects.get(
                        bot=bot_obj)
                    start_hour = analytics_monitoring_obj.active_hours_start
                    start_hour = start_hour.strftime('%H:%M')
                    end_hour = analytics_monitoring_obj.active_hours_end
                    end_hour = end_hour.strftime('%H:%M')
                    email_config_email_address = json.loads(
                        analytics_monitoring_obj.email_addr_list)['items']
                    for email_addresses in email_config_email_address:
                        analytics_monitoring_email_address_list.append({
                                                                       "tag": email_addresses})
                except Exception:
                    logger.info(
                        "Analytics Monitoring object not present for bot id: " + str(bot_obj.pk), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

            activity_update = {}
            is_trigger_livechat_enabled = False
            autosuggest_livechat_word_limit = 30
            if BotInfo.objects.filter(bot=bot_obj).exists():
                bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()
                activity_update = json.loads(bot_info_obj.activity_update)
                is_trigger_livechat_enabled = bot_info_obj.is_trigger_livechat_enabled
                autosuggest_livechat_word_limit = bot_info_obj.autosuggest_livechat_word_limit

            mail_sent_to_list = json.loads(bot_obj.mail_sent_to_list)["items"]
            api_fail_email_configured = False
            if len(mail_sent_to_list):
                api_fail_email_configured = True

            bot_break_mail_sent_to_list = json.loads(
                bot_info_obj.bot_break_mail_sent_to_list)["items"]
            bot_break_email_configured = False
            if len(bot_break_mail_sent_to_list):
                bot_break_email_configured = True

            mask_confidential_info = bot_obj.mask_confidential_info
            go_live_date = bot_obj.go_live_date
            master_languages = Language.objects.all()

            app_config = Config.objects.all()[0]

            intent_name_list = []
            intent_objs = Intent.objects.filter(
                bots__pk=bot_pk, is_hidden=False, is_deleted=False)

            for intent_obj in intent_objs:
                if bot_obj.initial_intent != None and bot_obj.initial_intent == intent_obj:
                    intent_name_list.append({
                        "is_selected": True,
                        "intent_name": intent_obj.name,
                        "intent_pk": intent_obj.pk
                    })
                else:
                    intent_name_list.append({
                        "is_selected": False,
                        "intent_name": intent_obj.name,
                        "intent_pk": intent_obj.pk
                    })

            channel_list = Channel.objects.filter(is_easychat_channel=True)

            select_channels_list = list(NPS.objects.filter(bot=bot_obj))
            whatsapp_nps_time = 2
            viber_nps_time = 2
            if select_channels_list:
                whatsapp_nps_time = select_channels_list[0].whatsapp_nps_time
                viber_nps_time = select_channels_list[0].viber_nps_time
                select_channels_list = select_channels_list[0].channel.all()
            
            channel_list_names = []
            for channel in channel_list:
                if channel.name == 'Web' or channel.name == 'WhatsApp' or channel.name == 'Android' or channel.name == "iOS" or channel.name == 'Viber':
                    if channel in select_channels_list:
                        channel_list_names.append({
                            "channel": channel,
                            "is_selected": True
                        })
                    else:
                        channel_list_names.append({
                            "channel": channel,
                            "is_selected": False
                        })

            masking_enabled = bot_obj.masking_enabled
            masking_time = bot_obj.masking_time
            csat_feedback_form_enabled = bot_obj.csat_feedback_form_enabled

            total_feedback_options = 0
            max_feedback_allowed = bot_obj.max_feedback_allowed
            all_csat_feedbacks = []
            collect_phone_number = False
            collect_email_id = False
            mark_all_fields_mandatory = False

            choice_list = TicketCategory.objects.filter(
                bot=bot_obj, is_deleted=False).values_list('ticket_category')
            tms_cat_drop_down_choices_list = [item[0] for item in choice_list]
            tms_cat_drop_down_choices_value = ""
            for value in tms_cat_drop_down_choices_list:
                tms_cat_drop_down_choices_value += str(value) + "_"

            if CSATFeedBackDetails.objects.filter(bot_obj=bot_obj):
                csat_feedback_obj = CSATFeedBackDetails.objects.filter(bot_obj=bot_obj)[
                    0]
                all_csat_feedbacks = json.loads(
                    csat_feedback_obj.all_feedbacks)
                total_feedback_options = len(all_csat_feedbacks)
                collect_phone_number = csat_feedback_obj.collect_phone_number
                collect_email_id = csat_feedback_obj.collect_email_id
                mark_all_fields_mandatory = csat_feedback_obj.mark_all_fields_mandatory

            supported_languages = get_supported_languages(
                bot_obj, BotChannel)

            is_livechat_profanity_words_enabled, profanity_response_obj = check_if_trigger_livechat_enabled_for_profanity_words(
                bot_obj)
            language_profanity_response = ""
            if not is_livechat_enabled:
                is_livechat_profanity_words_enabled = False

            eng_lang_obj = None
            need_to_show_auto_fix_popup = False
            if Language.objects.filter(lang="en"):
                eng_lang_obj = Language.objects.get(lang="en")
            need_to_show_auto_fix_popup = need_to_show_auto_fix_popup_for_bot_configuration(
                bot_obj, activity_update, selected_language, eng_lang_obj, LanguageTunedBot)

            if selected_language != "en":
                lang_obj = Language.objects.get(lang=selected_language)
                if lang_obj not in supported_languages:
                    return HttpResponseRedirect("/chat/bot/edit/" + str(bot_pk) + "/?selected_language=en")
                lang_tuned_bot_obj = check_and_update_langauge_tuned_bot_configuration(
                    bot_obj, lang_obj, LanguageTunedBot, EasyChatTranslationCache, EmojiBotResponse)
                bot_inactivity_msg = lang_tuned_bot_obj.bot_inactivity_response
                bot_response_delay_message = lang_tuned_bot_obj.bot_response_delay_message
                language_profanity_response = lang_tuned_bot_obj.profanity_bot_response

            masking_pii_otp_email_sentence = "OTP is send to "
            config_obj = get_developer_console_settings()
            email_ids = config_obj.get_masking_pii_data_otp_emails()

            if len(email_ids) == 0:
                config_obj.masking_pii_data_otp_email = json.dumps(
                    MASKING_PII_DATA_OTP_EMAIL)
                config_obj.save()
                email_ids = MASKING_PII_DATA_OTP_EMAIL

            for index, email_id in enumerate(email_ids):
                if (index + 1) == len(email_ids) and (index != 0):
                    masking_pii_otp_email_sentence += " and "
                elif (index != 0):
                    masking_pii_otp_email_sentence += ", "

                masking_pii_otp_email_sentence += email_id

            is_pdf_searcher_access_allowed = False
            is_lead_generation_access_allowed = False
            bot_related_access_perm = request.user.get_bot_related_access_perm(bot_obj.pk)
            if "Full Access" in bot_related_access_perm[bot_obj.pk]:
                is_pdf_searcher_access_allowed = True
                is_lead_generation_access_allowed = True
            else:
                if "PDF Searcher" in bot_related_access_perm[bot_obj.pk]:
                    is_pdf_searcher_access_allowed = True
                if "Lead Gen Related" in bot_related_access_perm[bot_obj.pk]:
                    is_lead_generation_access_allowed = True

            return render(request, 'EasyChatApp/platform/edit_bot.html', {
                "user_obj": user_obj,
                "bot_obj": bot_obj,
                "selected_bot_obj": bot_obj,
                "bot_info_obj": bot_info_obj,
                "app_config": app_config,
                "is_form_assist_enabled": is_form_assist_enabled,
                "website_link_obj": website_link_obj,
                "website_link_size": website_link_size,
                "is_lead_generation_enabled": is_lead_generation_enabled,
                "is_easy_search_user": is_easy_search_user,
                "is_easy_search_allowed": is_easy_search_allowed,
                "is_pdf_search_allowed": is_pdf_search_allowed,
                "is_livechat_manager": is_livechat_manager,
                "is_livechat_enabled": is_livechat_enabled,
                "is_synonyms_included_in_paraphrase": is_synonyms_included_in_paraphrase,
                "is_email_notifiication_enabled": is_email_notifiication_enabled,
                "is_easy_assist_admin": is_easy_assist_admin,
                "is_easy_assist_allowed": is_easy_assist_allowed,
                "is_easytms_admin": is_easytms_admin,
                "is_tms_allowed": is_tms_allowed,
                "is_feedback_required": is_feedback_required,
                "email_config_channel_list": email_config_channel_list,
                "email_config_analytics_list": email_config_analytics_list,
                "email_config_logs_list": email_config_logs_list,
                "email_config_email_address_list": email_config_email_address_list,
                "email_config_obj": email_config_obj,
                "mask_confidential_info": mask_confidential_info,
                "export_list": get_export_option_list(),
                "import_list": get_import_option_list(),
                "bot_position_choices": BOT_POSITION_CHOICES,
                "is_e_search_enabled": is_e_search_enabled,
                "is_g_search_enabled": is_g_search_enabled,
                "search_cx": search_cx,
                "bot_inactivity_detection_enabled": bot_inactivity_detection_enabled,
                "bot_inactivity_msg": bot_inactivity_msg,
                "bot_response_delay_message": bot_response_delay_message,
                "bot_inactivity_time": bot_inactivity_time,
                "go_live_date": go_live_date,
                "api_fail_email_configured": api_fail_email_configured,
                "bot_break_email_configured": bot_break_email_configured,
                "mail_sent_to_list": mail_sent_to_list,
                "bot_break_mail_sent_to_list": bot_break_mail_sent_to_list,
                "analytics_monitoring_obj": analytics_monitoring_obj,
                "analytics_monitoring_email_address_list": analytics_monitoring_email_address_list,
                "intent_name_list": intent_name_list,
                "channel_list": channel_list_names,
                "whatsapp_nps_time": whatsapp_nps_time,
                "viber_nps_time": viber_nps_time,
                "master_languages": master_languages,
                "start_hour": start_hour,
                "end_hour": end_hour,
                "is_theme_greater_than_five": is_theme_greater_than_five,
                "show_form_enabled": show_form_enabled,
                "use_customer_details_processor": use_customer_details_processor,
                "use_end_chat_processor": use_end_chat_processor,
                "masking_enabled": masking_enabled,
                "masking_time": masking_time,
                "csat_feedback_form_enabled": csat_feedback_form_enabled,
                "total_feedback_options": total_feedback_options,
                "max_feedback_allowed": max_feedback_allowed,
                "all_csat_feedbacks": all_csat_feedbacks,
                "range_total_feedback_options": range(max_feedback_allowed + 1),
                "collect_phone_number": collect_phone_number,
                "collect_email_id": collect_email_id,
                "mark_all_fields_mandatory": mark_all_fields_mandatory,
                "tms_cat_drop_down_choices_value": tms_cat_drop_down_choices_value,
                "profile_dict": profile_dict,
                "default_email_subject": DEFAULT_MAIL_SUBJECT,
                "intent_objs": intent_objs,
                "flows": flows,
                "traffic_objs": traffic_objs,
                "character_limit_small_text": CHARACTER_LIMIT_SMALL_TEXT,
                "character_limit_medium_text": CHARACTER_LIMIT_MEDIUM_TEXT,
                "selected_language": selected_language,
                "supported_languages": supported_languages,
                "need_to_show_auto_fix_popup": need_to_show_auto_fix_popup,
                "is_trigger_livechat_enabled": is_trigger_livechat_enabled,
                "autosuggest_livechat_word_limit": autosuggest_livechat_word_limit,
                "all_channel_list": channel_list,
                "masking_pii_otp_email_sentence": masking_pii_otp_email_sentence,
                "is_livechat_profanity_words_enabled": is_livechat_profanity_words_enabled,
                "profanity_response_obj": profanity_response_obj,
                "language_profanity_response": language_profanity_response,
                "is_pdf_searcher_access_allowed": is_pdf_searcher_access_allowed,
                "is_lead_generation_access_allowed": is_lead_generation_access_allowed
            })
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditBot %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
            # return HttpResponse("<h5>Invalid Request</h5>")
            return render(request, 'EasyChatApp/error_500.html')
    else:
        return redirect("/chat/login")


def EditEasySearch(request, bot_pk):  # noqa: N802
    if request.user.is_authenticated:
        try:
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            is_easy_search_user = is_it_easysearch_manager(username)
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_uat=True, is_deleted=False)
            if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                return HttpResponseNotFound("You do not have access to this page")
                # return render(request, 'EasyChatApp/error_404.html')

            is_g_search_enabled = True
            is_e_search_enabled = False
            search_cx = ""
            search_obj = None
            website_link_obj = None

            website_link_size = 0
            if bot_obj.is_easy_search_allowed:
                try:
                    easy_search_cofig = EasySearchConfig.objects.get(
                        bot=bot_obj)
                    config_feature = easy_search_cofig.feature
                    if config_feature == "1":
                        is_e_search_enabled = True
                        try:
                            search_obj = SearchUser.objects.get(user=user_obj)
                            website_link_obj = WebsiteLink.objects.filter(
                                search_user=search_obj, bot=bot_obj)
                            website_link_size = len(website_link_obj)
                            search_cx = easy_search_cofig.search_cx
                            if search_cx == None:
                                search_cx = ""
                        except Exception:
                            pass
                    elif config_feature == "2":
                        is_g_search_enabled = True
                        search_cx = easy_search_cofig.search_cx
                        try:
                            search_obj = SearchUser.objects.get(user=user_obj)
                            website_link_obj = WebsiteLink.objects.filter(
                                search_user=search_obj, bot=bot_obj)
                            website_link_size = len(website_link_obj)
                        except Exception:
                            pass
                except Exception:
                    easy_search_cofig = ""

            is_easy_search_allowed = bot_obj.is_easy_search_allowed

            return render(request, 'EasyChatApp/platform/easysearch.html', {
                "user_obj": user_obj,
                "bot_obj": bot_obj,
                "selected_bot_obj": bot_obj,
                "is_easy_search_user": is_easy_search_user,
                "is_easy_search_allowed": is_easy_search_allowed,
                "is_e_search_enabled": is_e_search_enabled,
                "is_g_search_enabled": is_g_search_enabled,
                "search_cx": search_cx,
                "website_link_obj": website_link_obj,
                "website_link_size": website_link_size,
            })
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditEasySearch %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
            # return HttpResponse("<h5>Invalid Request</h5>")
            return render(request, 'EasyChatApp/error_500.html')
    else:
        return redirect("/chat/login")


def ExportImportBot(request, bot_pk):  # noqa: N802
    if request.user.is_authenticated:
        try:
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_uat=True, is_deleted=False)
            if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                return HttpResponseNotFound("You do not have access to this page")
                # return render(request, 'EasyChatApp/error_404.html')

            intent_objs = Intent.objects.filter(
                bots__pk=bot_pk, is_hidden=False, is_deleted=False)

            return render(request, 'EasyChatApp/platform/export_import.html', {
                "user_obj": user_obj,
                "bot_obj": bot_obj,
                "selected_bot_obj": bot_obj,
                "export_list": get_export_option_list(),
                "import_list": get_import_option_list(),
                "intent_objs": intent_objs,
            })
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportImportBot %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
            # return HttpResponse("<h5>Invalid Request</h5>")
            return render(request, 'EasyChatApp/error_500.html')
    else:
        return redirect("/chat/login")


def ShareBot(request):  # noqa: N802
    response = {}
    response["status"] = 500

    if request.user.is_authenticated and request.method == "POST":
        username = request.user.username
        user_supervisor = User.objects.get(username=str(username))
        data = DecryptVariable(request.POST["data"])
        data = json.loads(data)
        bot_id = data["bot_id"]
        user_id_list = data["user_id_list"]
        access_type = data["access_type"]
        custom_access_array = data["custom_access_array"]
        bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)

        if user_supervisor not in bot_obj.users.all():
            response["status"] = 400
            custom_encrypt_obj = CustomEncrypt()
            response = custom_encrypt_obj.encrypt(json.dumps(response))
            return HttpResponse(json.dumps(response), content_type="application/json")

        is_livechat_supervisor_access_guaranted = str(
            data["is_livechat_supervisor_access_guaranted"]).strip().lower()
        is_tms_supervisor_access_guaranted = str(
            data["is_tms_supervisor_access_guaranted"]).strip().lower()

        access_type_obj_list = []
        if access_type == "full_access":
            access_type_obj_list += [
                AccessType.objects.get(name="Full Access")]
        if access_type == "custom_access":
            if len(custom_access_array) > 0:
                if "access_intent_related" in custom_access_array:
                    access_type_obj_list += [
                        AccessType.objects.get(name="Intent Related")]
                if "access_bot_setting" in custom_access_array:
                    access_type_obj_list += [
                        AccessType.objects.get(name="Bot Setting Related")]
                if "access_lead_gen" in custom_access_array:
                    access_type_obj_list += [
                        AccessType.objects.get(name="Lead Gen Related")]
                if "access_form_assist" in custom_access_array:
                    access_type_obj_list += [
                        AccessType.objects.get(name="Form Assist Related")]
                if "access_self_learning" in custom_access_array:
                    access_type_obj_list += [
                        AccessType.objects.get(name="Self Learning Related")]
                if "access_msg_history_analytics" in custom_access_array:
                    access_type_obj_list += [
                        AccessType.objects.get(name="Analytics Related")]
                if "access_easydrive" in custom_access_array:
                    access_type_obj_list += [
                        AccessType.objects.get(name="EasyDrive Related")]
                if "access_data_collection" in custom_access_array:
                    access_type_obj_list += [AccessType.objects.get(
                        name="EasyDataCollection Related")]
                if "access_word_mapper" in custom_access_array:
                    access_type_obj_list += [AccessType.objects.get(
                        name="Word Mapper Related")]
                if "access_create_bot_with_excel" in custom_access_array:
                    access_type_obj_list += [AccessType.objects.get(
                        name="Create Bot With Excel Related")]
                if "access_extract_faq" in custom_access_array:
                    access_type_obj_list += [AccessType.objects.get(
                        name="Extract FAQ Related")]
                if "access_word_mapper" in custom_access_array:
                    access_type_obj_list += [AccessType.objects.get(
                        name="Word Mapper Related")]
                if "access_only_message_history" in custom_access_array:
                    access_type_obj_list += [AccessType.objects.get(
                        name="Message History Related")]
                if "access_api_analytics" in custom_access_array:
                    access_type_obj_list += [AccessType.objects.get(
                        name="API Analytics Related")]
                if "access_easychat_categories" in custom_access_array:
                    access_type_obj_list += [AccessType.objects.get(
                        name="Categories")]
                if "access_automated_testing" in custom_access_array:
                    access_type_obj_list += [AccessType.objects.get(
                        name="Automated Testing")]
                if "access_pdf_searcher" in custom_access_array:
                    access_type_obj_list += [AccessType.objects.get(
                        name="PDF Searcher")]

        if bot_obj.is_livechat_enabled and bot_obj.created_by == user_supervisor:
            livechat_supervisor_obj = LiveChatUser.objects.get(
                user=user_supervisor, is_deleted=False)
            livechat_others_category_obj = get_livechat_category_object(
                -1, bot_obj, LiveChatCategory)

        if bot_obj.is_tms_allowed and bot_obj.created_by == user_supervisor:
            tms_supervisor_obj = Agent.objects.filter(
                user=user_supervisor, is_account_active=True).first()
            try:
                tms_others_category_obj = TicketCategory.objects.get(
                    bot=bot_obj, ticket_category="Others")
            except:
                tms_others_category_obj = TicketCategory.objects.create(
                    bot=bot_obj, ticket_category="Others")

        if len(access_type_obj_list) > 0:
            for user_id in user_id_list:
                user_obj = User.objects.get(pk=int(user_id))
                try:
                    access_mng_obj = AccessManagement.objects.get(
                        user=user_obj, bot=bot_obj)
                except Exception:
                    access_mng_obj = AccessManagement.objects.create(
                        user=user_obj, bot=bot_obj)
                access_mng_obj.access_type.clear()
                for access_type_obj in access_type_obj_list:
                    access_mng_obj.access_type.add(access_type_obj)
                access_mng_obj.save()
                bot_obj.users.add(user_obj)

                # Livechat supervisor access
                if is_livechat_supervisor_access_guaranted == "true" and bot_obj.is_livechat_enabled and bot_obj.created_by == user_supervisor:

                    livechat_user_obj = LiveChatUser.objects.filter(
                        user=user_obj).first()
                    if not livechat_user_obj:
                        livechat_user_obj = LiveChatUser.objects.create(
                            user=user_obj, status="2")

                    if str(livechat_user_obj.status) == "2":
                        livechat_user_obj.max_customers_allowed = 1
                        livechat_user_obj.bots.add(bot_obj)

                        livechat_user_obj.category.add(
                            livechat_others_category_obj)
                        livechat_user_obj.save()

                        livechat_supervisor_obj.agents.add(livechat_user_obj)
                        livechat_supervisor_obj.save()

                elif is_livechat_supervisor_access_guaranted == "false" and bot_obj.is_livechat_enabled and bot_obj.created_by == user_supervisor:

                    livechat_user_obj = LiveChatUser.objects.filter(
                        user=user_obj, status=2, bots__in=[bot_obj]).first()
                    if livechat_user_obj:
                        supervisor_agents = livechat_user_obj.agents.filter(bots__in=[
                                                                            bot_obj])
                        for supervisor_agent in supervisor_agents:
                            livechat_user_obj.agents.remove(supervisor_agent)
                            livechat_supervisor_obj.agents.add(
                                supervisor_agent)

                        livechat_category_objs = livechat_user_obj.category.filter(
                            bot=bot_obj)
                        for livechat_category_obj in livechat_category_objs:
                            livechat_user_obj.category.remove(
                                livechat_category_obj)

                        livechat_user_obj.bots.remove(bot_obj)

                        livechat_user_obj.save()
                        livechat_supervisor_obj.save()

                # TMS supervisor access
                if is_tms_supervisor_access_guaranted == "true" and bot_obj.is_tms_allowed and bot_obj.created_by == user_supervisor:

                    tms_user_obj = Agent.objects.filter(user=user_obj).first()
                    if not tms_user_obj:
                        tms_user_obj = Agent.objects.create(
                            user=user_obj, role="supervisor")

                    if tms_user_obj.role == "supervisor":
                        tms_user_obj.bots.add(bot_obj)
                        tms_user_obj.ticket_categories.add(
                            tms_others_category_obj)
                        tms_user_obj.save()

                        tms_supervisor_obj.agents.add(tms_user_obj)
                        tms_supervisor_obj.save()

                elif is_tms_supervisor_access_guaranted == "false" and bot_obj.is_tms_allowed and bot_obj.created_by == user_supervisor:

                    tms_user_obj = Agent.objects.filter(
                        user=user_obj, role="supervisor", bots__in=[bot_obj]).first()
                    if tms_user_obj:
                        supervisor_agents = tms_user_obj.agents.filter(bots__in=[
                                                                       bot_obj])
                        for supervisor_agent in supervisor_agents:
                            tms_user_obj.agents.remove(supervisor_agent)
                            tms_supervisor_obj.agents.add(supervisor_agent)

                        tms_category_objs = tms_user_obj.ticket_categories.filter(
                            bot=bot_obj)
                        for tms_category_obj in tms_category_objs:
                            tms_user_obj.ticket_categories.remove(
                                tms_category_obj)

                        tms_user_obj.bots.remove(bot_obj)

                        tms_user_obj.save()
                        tms_supervisor_obj.save()

            bot_obj.save()
            response["status"] = 200
            response["bot_id"] = bot_id
            audit_trail_data = json.dumps({
                "bot_pk": bot_id,
                "user_id_list": user_id_list
            })
            save_audit_trail(
                user_supervisor, SHARE_BOT_ACTION, audit_trail_data)

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return HttpResponse(json.dumps(response), content_type="application/json")


def UnShareBot(request):
    response = {}
    response["status"] = 500
    if request.user.is_authenticated and request.method == "POST":
        username = request.user.username
        user_supervisor = User.objects.get(username=str(username))
        data = DecryptVariable(request.POST["data"])
        data = json.loads(data)
        bot_id = data["bot_id"]
        user_id = data["user_id"]
        bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)

        if request.user not in bot_obj.users.all():
            response["status"] = 401
            response["message"] = "You are not authorised to perform this operation."
            return HttpResponse(json.dumps(response), content_type="application/json")

        user_obj = User.objects.get(pk=int(user_id))
        bot_obj.users.remove(user_obj)
        bot_obj.save()

        # Revoke livechat supervisor access
        try:
            livechat_supervisor_obj = LiveChatUser.objects.get(
                user=user_supervisor, is_deleted=False)
            livechat_user_obj = LiveChatUser.objects.get(
                user=user_obj, status=2)

            livechat_supervisor_agents = livechat_user_obj.agents.filter(bots__in=[
                                                                         bot_obj])
            for supervisor_agent in livechat_supervisor_agents:
                livechat_user_obj.agents.remove(supervisor_agent)
                livechat_supervisor_obj.agents.add(supervisor_agent)

            livechat_supervisor_obj.agents.remove(livechat_user_obj)
            livechat_user_obj.bots.remove(bot_obj)

            livechat_category_objs = livechat_user_obj.category.filter(
                bot=bot_obj)
            for category_obj in livechat_category_objs:
                livechat_user_obj.category.remove(category_obj)

            livechat_supervisor_obj.save()
            livechat_user_obj.save()
        except Exception as e:
            logger.error(str(e), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
            pass

        # Revoke tms supervisor access
        try:
            tms_supervisor_obj = Agent.objects.filter(
                user=user_supervisor, is_account_active=True).first()
            tms_user_obj = Agent.objects.get(
                user=user_obj, status="supervisor")

            tms_supervisor_agents = tms_user_obj.agents.filter(bots__in=[
                                                               bot_obj])
            for supervisor_agent in tms_supervisor_agents:
                tms_user_obj.agents.remove(supervisor_agent)
                tms_supervisor_obj.agents.add(supervisor_agent)

            tms_supervisor_obj.agents.remove(tms_user_obj)
            tms_user_obj.bots.remove(bot_obj)

            tms_category_objs = tms_user_obj.ticket_categories.filter(
                bot=bot_obj)
            for category_obj in tms_category_objs:
                tms_user_obj.ticket_categories.remove(category_obj)

            tms_supervisor_obj.save()
            tms_user_obj.save()
        except Exception as e:
            logger.error(str(e), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
            pass

        response["status"] = 200
        audit_trail_data = json.dumps({
            "bot_pk": bot_id,
            "user_id": user_id
        })
        save_audit_trail(user_supervisor, UNSHARE_BOT_ACTION, audit_trail_data)
        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        return HttpResponse(json.dumps(response), content_type="application/json")


def ShareAPI(request):  # noqa: N802
    response = {}
    response["status"] = 500
    if request.user.is_authenticated and request.method == "POST":
        data = DecryptVariable(request.POST["data"])
        data = json.loads(data)
        api_alias_name = data["api_alias_name"]
        user_id_list = data["user_id_list"]
        tag_mapper_obj = TagMapper.objects.get(
            alias_variable=str(api_alias_name))
        api_tree = tag_mapper_obj.api_tree
        for user_id in user_id_list:
            user_obj = User.objects.get(pk=int(user_id))
            api_tree.users.add(user_obj)
        api_tree.save()
        tag_mapper_obj.api_tree = api_tree
        tag_mapper_obj.save()
        response["status"] = 200
        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        return HttpResponse(json.dumps(response), content_type="application/json")


class ImportBotAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            user_obj = User.objects.get(username=str(request.user.username))
            data = request.data
            input_json_file = data["input_json_file"]
            data = json.loads(data["data"])
            bot_id = data["bot_id"]

            file_validation_obj = EasyChatFileValidation()

            if file_validation_obj.check_malicious_file(input_json_file.name):
                response["status"] = 300
                return Response(data=response)

            bot_obj = Bot.objects.get(
                pk=int(bot_id), is_uat=True, is_deleted=False)

            file_name = get_dot_replaced_file_name(input_json_file.name)
            path = default_storage.save(
                "imports/" + file_name, ContentFile(input_json_file.read()))

            event_obj = EventProgress.objects.create(
                user=user_obj,
                bot=bot_obj,
                event_type='import_bot',
                event_info=json.dumps({'file_uploaded': input_json_file.name})
            )

            import_bot_thread = threading.Thread(
                target=import_data, args=(request.user.username, bot_obj, settings.MEDIA_ROOT + path, bot_id, event_obj))
            import_bot_thread.daemon = True
            import_bot_thread.start()

            audit_trail_data = json.dumps({
                "bot_pk": bot_obj.pk
            })
            save_audit_trail(
                user_obj, IMPORT_BOT_FROM_JSON_ACTION, audit_trail_data)
            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ImportBotAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        return Response(data=response)


class ImportIntentAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            user_obj = User.objects.get(username=str(request.user.username))
            data = request.data
            input_json_file = data["input_json_file"]
            data = json.loads(data["data"])
            bot_id = data["bot_id"]

            file_validation_obj = EasyChatFileValidation()

            if file_validation_obj.check_malicious_file(input_json_file.name):
                response["status"] = 300
                return Response(data=response)

            bot_obj = Bot.objects.get(
                pk=int(bot_id), is_uat=True, is_deleted=False)

            file_name = get_dot_replaced_file_name(input_json_file.name)
            path = default_storage.save(
                "imports/" + file_name, ContentFile(input_json_file.read()))

            event_obj = EventProgress.objects.create(
                user=request.user,
                bot=bot_obj,
                event_type='import_bot',
                event_info=json.dumps({'file_uploaded': input_json_file.name})
            )

            import_bot_thread = threading.Thread(
                target=import_intent, args=(request.user.username, bot_obj, settings.MEDIA_ROOT + path, bot_id, event_obj))
            import_bot_thread.daemon = True
            import_bot_thread.start()

            audit_trail_data = json.dumps({
                "bot_pk": bot_obj.pk
            })
            save_audit_trail(
                user_obj, IMPORT_INTENT_FROM_JSON_ACTION, audit_trail_data)
            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ImportIntentAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        return Response(data=response)


ImportIntent = ImportIntentAPI.as_view()


class ImportBotFromZipAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            user_obj = User.objects.get(username=str(request.user.username))
            data = request.data
            input_zip_file = data["input_zip_file"]
            data = json.loads(data["data"])
            bot_id = data["bot_id"]

            file_validation_obj = EasyChatFileValidation()

            if file_validation_obj.check_malicious_file(input_zip_file.name):
                response["status"] = 300
                return Response(data=response)

            bot_obj = Bot.objects.get(
                pk=int(bot_id), is_uat=True, is_deleted=False)

            file_name = get_dot_replaced_file_name(input_zip_file.name)
            if os.path.exists("files/imports/" + str(file_name)):
                cmd = "rm -rf files/imports/" + str(file_name)
                subprocess.run(cmd, shell=True)
            path = default_storage.save(
                "imports/" + file_name, ContentFile(input_zip_file.read()))

            event_obj = EventProgress.objects.create(
                user=user_obj,
                bot=bot_obj,
                event_type='import_bot',
                event_info=json.dumps({'file_uploaded': input_zip_file.name})
            )

            import_bot_thread = threading.Thread(
                target=import_data_as_zip, args=(request.user.username, bot_obj, settings.MEDIA_ROOT + path, bot_id, event_obj))
            import_bot_thread.daemon = True
            import_bot_thread.start()

            audit_trail_data = json.dumps({
                "bot_pk": bot_obj.pk
            })
            save_audit_trail(
                user_obj, IMPORT_BOT_FROM_ZIP_ACTION, audit_trail_data)
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ImportBotAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        return Response(data=response)


ImportBotFromZip = ImportBotFromZipAPI.as_view()


class DeleteBotAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_id = data["bot_id"]
            Bot.objects.get(pk=int(bot_id), users__in=[
                            user_obj], is_deleted=False).disable()

            # marking BotQATesting deleted
            try:
                bot_qa_testing_obj = BotQATesting.objects.filter(bot_id=int(bot_id))[
                    0]
                bot_qa_testing_obj.is_deleted = True
                bot_qa_testing_obj.save()
            except Exception:
                pass
            # disabling bot break email
            try:
                bot_info_obj = BotInfo.objects.filter(bot__pk=int(bot_id))[0]
                bot_info_obj.is_bot_break_email_notification_enabled = False
                bot_info_obj.save()
            except Exception:
                pass
            audit_trail_data = json.dumps({
                "bot_pk": bot_id
            })
            save_audit_trail(user_obj, DELETE_BOT_ACTION, audit_trail_data)
            description = "Bot deleted with bot id" + \
                " (" + str(bot_id) + ")"
            add_audit_trail(
                "EASYCHATAPP",
                user_obj,
                "Delete-Bot",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )
            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteBotAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveBotAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["data"])

            validation_obj = EasyChatInputValidation()

            data = json.loads(json_string)
            bot_id = data["bot_id"]
            bot_name = data["bot_name"]
            bot_name = validation_obj.remo_html_from_string(bot_name)
            bot_name = validation_obj.remo_unwanted_characters(bot_name)
            selected_channels_list_nps = data["selected_channels_list_nps"]
            is_nps_required = data["is_nps_required"]
            whatsapp_nps_timer = data["whatsapp_nps_timer"]
            viber_nps_timer = data["viber_nps_timer"]
            create_csat_flow = data["create_csat_flow"]
            is_text_to_speech_required = data["is_text_to_speech_required"]
            is_easyassist_enabled = data["is_easyassist_enabled"]
            is_livechat_enabled = data["is_livechat_enabled"]
            livechat_provider = data["livechat_provider"]
            is_livechat_manager = is_it_livechat_manager(username, bot_id)
            # emoji initializations

            angry_emoji_response = data["angry_emoji_response"]
            angry_emoji_response = validation_obj.clean_html(
                angry_emoji_response)
            happy_emoji_response = data["happy_emoji_response"]
            happy_emoji_response = validation_obj.clean_html(
                happy_emoji_response)
            neutral_emoji_response = data["neutral_emoji_response"]
            neutral_emoji_response = validation_obj.clean_html(
                neutral_emoji_response)
            sad_emoji_response = data["sad_emoji_response"]
            sad_emoji_response = validation_obj.clean_html(sad_emoji_response)
            emoji_livechat_checkbox_value_list = data["emoji_livechat_checkbox_value_list"]

            # emoji initializations end

            is_suggest_livechat_for_profanity_words_enabled = data[
                "is_suggest_livechat_for_profanity_words_enabled"]

            profanity_response_text = data["profanity_response_text"]
            profanity_response_text = validation_obj.clean_html(
                profanity_response_text)

            add_livechat_as_quick_recommendation = data["add_livechat_as_quick_recommendation"]

            trigger_livechat_intent = data["trigger_livechat_intent"]

            is_easysearch_enabled = data["is_easysearch_enabled"]
            is_pdfsearch_enabled = data["is_pdfsearch_enabled"]
            is_lead_generation_enabled = data["is_lead_generation_enabled"]
            is_bot_intent_threshold_enabled = data["is_bot_intent_threshold_enabled"]
            intent_score_threshold = data["intent_score_threshold"]
            is_intent_level_nlp_functionality_enabled = data["is_intent_level_nlp_functionality_enabled"]
            is_easytms_enabled = data["is_easytms_enabled"]
            tms_category_list = data["tms_drop_down_cat_list"]
            termination_keyword_list = data["termination_keyword_list"]
            flow_termination_bot_response = data[
                "flow_termination_bot_response"]
            flow_termination_bot_response = validation_obj.clean_html(
                flow_termination_bot_response)
            flow_termination_confirmation_display_message = data[
                "flow_termination_confirmation_display_message"]
            flow_termination_confirmation_display_message = validation_obj.clean_html(flow_termination_confirmation_display_message)
            is_feedback_required = data["is_feedback_required"]
            is_synonyms_incuded_var_gen = data["is_synonyms_incuded_var_gen"]
            is_email_notifiication_enabled = data[
                "is_email_notifiication_enabled"]
            # is_nps_required = data["is_nps_required"]
            mask_confidential_info = data["mask_confidential_info"]
            go_live_date = data["go_live_date"]
            is_api_fail_email_notifiication_enabled = data[
                "is_api_fail_email_notifiication_enabled"]

            is_bot_break_email_notification_enabled = data[
                "is_bot_break_email_notification_enabled"]

            bot_inactivity_detection_enabled = data[
                "bot_inactivity_detection_enabled"]
            bot_inactivity_msg = data["bot_inactivity_msg"]
            bot_inactivity_time = data["bot_inactivity_time"]
            bot_userid_cookie_timeout = data["bot_userid_cookie_timeout"]
            is_analytics_monitoring_enabled = data[
                "is_analytics_monitoring_enabled"]
            initial_intent_pk = data["initial_intent_pk"]
            # selected_supported_languages = data["selected_supported_languages"]
            show_brand_name = data["show_brand_name"]
            custom_bot_js_required = data["custom_bot_js_required"]
            custom_bot_css_required = data["custom_bot_css_required"]
            bot_response_delay_allowed = data["bot_response_delay_allowed"]
            bot_response_delay_timer = data["bot_response_delay_timer"]
            bot_response_delay_message = data["bot_response_delay_message"]
            bot_response_delay_message = validation_obj.sanitize_html(
                bot_response_delay_message)
            # bot_response_delay_message = validation_obj.remo_html_from_string(bot_response_delay_message)
            # bot_response_delay_message = validation_obj.remo_unwanted_characters(bot_response_delay_message)
            default_order_of_response = data["default_order_of_response"]
            max_file_size_allowed = data["max_file_size_allowed"]
            show_form = data["show_form"]
            use_customer_details_processor = data[
                "use_customer_details_processor"]
            use_end_chat_processor = data["use_end_chat_processor"]
            use_assign_agent_processor = data["use_assign_agent_processor"]
            masking_enabled = data["masking_enabled"]
            masking_time = data["masking_time"]
            token = data["token"]
            csat_feedback_form_enabled = data["csat_feedback_form_enabled"]
            scale_rating = data["scale_rating"]
            enable_audio_notification = data["enable_audio_notification"]
            is_trigger_livechat_enabled = data["is_trigger_livechat_enabled"]
            autosuggest_livechat_word_limit = data["autosuggest_livechat_word_limit"]

            is_bot_inactivity_response_updated = "false"
            is_bot_response_delay_message_updated = "false"
            is_flow_termination_bot_response_updated = "false"
            is_flow_termination_confirmation_display_message_updated = "false"

            is_abort_flow_enabled = data["is_abort_flow_enabled"]
            is_advance_tree_level_nlp_enabled = data["is_advance_tree_level_nlp_enabled"]

            enable_do_not_translate = data["enable_do_not_translate"]
            no_translate_keywords = data["no_translate_keywords"]
            no_translate_regex = data["no_translate_regex"]

            if not validation_obj.is_valid_bot_name(bot_name) or len(bot_name) > 18:
                response["status"] = 300
                response["msg"] = "Invalid Bot Name(Only alphabets, 0-9, ?, !, & are allowed. Max length: 18 characters)"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if bot_inactivity_detection_enabled:
                if bot_inactivity_msg.strip() == "":
                    response = {}
                    response["status"] = 300
                    response["msg"] = "Bot inactivity message can't be empty."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
                try:
                    if bot_inactivity_time.strip() == "" or int(bot_inactivity_time.strip()) < 1:
                        response = {}
                        response["status"] = 300
                        response["msg"] = "Time must be greater than or equal to 1."
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("SaveBotAPI: %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

                    response = {}
                    response["status"] = 300
                    response["msg"] = "Invalid time input."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            if is_livechat_manager and is_livechat_enabled and is_suggest_livechat_for_profanity_words_enabled:
                if profanity_response_text.strip() == "":
                    response = {}
                    response["status"] = 300
                    response["msg"] = "Profanity Bot Respone can't be empty."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            if bot_response_delay_allowed:
                if bot_response_delay_message.strip() == "":
                    response = {}
                    response["status"] = 300
                    response["msg"] = "Bot delay message can't be empty."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                try:
                    if bot_response_delay_timer.strip() == "" or int(bot_response_delay_timer.strip()) < 1:
                        response = {}
                        response["status"] = 300
                        response["msg"] = "Invalid time input."
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("SaveBotAPI: %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
                    response = {}
                    response["status"] = 300
                    response["msg"] = "Invalid time input."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            if Bot.objects.filter(~Q(pk=int(bot_id)), slug=slugify(bot_name), users__in=[user_obj], is_deleted=False):
                response["status"] = 400
            else:
                bot_obj = Bot.objects.get(pk=int(bot_id), users__in=[
                                          user_obj], is_deleted=False)

                try:
                    logger.info("Updating livechat bot configuration", extra={'AppName': 'EasyChat', 'user_id': str(
                        request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
                    if user_obj.pk == bot_obj.created_by.pk and LiveChatUser.objects.filter(user=user_obj).count():
                        manage_default_livechat_intent(
                            is_livechat_enabled, bot_obj)
                        manage_bot_to_admin_account(
                            user_obj, is_livechat_enabled, bot_obj)
                        check_and_create_default_livechat_category(
                            bot_obj, user_obj)
                        bot_obj.is_livechat_enabled = is_livechat_enabled
                        logger.info("Successfully Updated livechat bot configuration", extra={'AppName': 'EasyChat', 'user_id': str(
                            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("LiveChat bot configuration: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                 'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
                    pass
                emoji_activity_update = save_emoji_data(EmojiBotResponse, bot_obj, angry_emoji_response, happy_emoji_response,
                                                        neutral_emoji_response, sad_emoji_response, emoji_livechat_checkbox_value_list)

                profanity_activity_update = {
                    "is_profanity_response_text_updated": "false"
                }
                if is_livechat_manager:
                    profanity_activity_update = save_profanity_data(bot_obj, profanity_response_text, is_suggest_livechat_for_profanity_words_enabled,
                                                                    add_livechat_as_quick_recommendation, trigger_livechat_intent, ProfanityBotResponse)
                # old_bot_slug = bot_obj.slug

                # Adding language template

                # check_and_create_bot_language_template_obj(
                #     bot_obj, selected_supported_languages, RequiredBotTemplate, Language)

                if bot_obj.name != bot_name:
                    bot_obj.name = bot_name
                    bot_obj.save(update_fields=["name"])
                    update_multilingual_bot_name(bot_obj, RequiredBotTemplate, EasyChatTranslationCache)

                bot_obj.is_text_to_speech_required = is_text_to_speech_required
                bot_obj.is_easy_assist_allowed = is_easyassist_enabled
                bot_obj.is_easy_search_allowed = is_easysearch_enabled
                bot_obj.is_pdf_search_allowed = is_pdfsearch_enabled
                bot_obj.is_lead_generation_enabled = is_lead_generation_enabled
                bot_obj.is_tms_allowed = is_easytms_enabled
                bot_obj.is_synonyms_included_in_paraphrase = is_synonyms_incuded_var_gen
                bot_obj.is_email_notifiication_enabled = is_email_notifiication_enabled

                if len(termination_keyword_list) > 0 and bot_obj.flow_termination_bot_response != flow_termination_bot_response:
                    is_flow_termination_bot_response_updated = "true"
                bot_obj.flow_termination_bot_response = flow_termination_bot_response
                bot_obj.flow_termination_keywords = json.dumps(
                    {"items": termination_keyword_list})

                if bot_obj.flow_termination_confirmation_display_message != flow_termination_confirmation_display_message:
                    is_flow_termination_confirmation_display_message_updated = "true"

                bot_obj.flow_termination_confirmation_display_message = flow_termination_confirmation_display_message
                
                # if intent level feedback is enabled and it was disabled previosuly then we have to  
                # enable intent level feedback of its intent except small talk
                if is_feedback_required and (not bot_obj.is_feedback_required):
                    Intent.objects.filter(
                        bots__in=[bot_obj], is_small_talk=False, is_deleted=False).update(is_feedback_required=is_feedback_required)
                    # Note Intent object has post save signal still .update() is bieng used because we are only changing 
                    # the field is_feedback_required no training questions have been updated so firing of post save signal is not required

                    if bot_obj.livechat_default_intent != None and not bot_obj.livechat_default_intent.is_deleted:
                        intent_obj = bot_obj.livechat_default_intent
                        intent_obj.is_feedback_required = False
                        intent_obj.save(update_fields=["is_feedback_required"])

                bot_obj.is_feedback_required = is_feedback_required
                if(len(selected_channels_list_nps)) > 0 and is_nps_required:
                    bot_obj.is_nps_required = True
                else:
                    bot_obj.is_nps_required = False
                    whatsapp_nps_timer = 0
                    viber_nps_timer = 0
                    selected_channels_list_nps = []
                    csat_feedback_form_enabled = False
                    scale_rating = "4_scale"
                if create_csat_flow:
                    create_default_csat_flow(bot_id)
                else:
                    intent_objs = Intent.objects.filter(
                        bots__in=[bot_obj], is_whatsapp_csat=True)
                    intent_objs.delete()

                set_easyassist_intent(bot_obj, is_easyassist_enabled)

                set_easytms_intent(bot_obj, is_easytms_enabled)

                if(is_easytms_enabled):
                    create_tms_categories(
                        tms_category_list, bot_obj, TicketCategory, True)
                    set_tms_bot_admin(user_obj, Agent, bot_obj, TicketCategory)

                bot_obj.show_intent_threshold_functionality = is_bot_intent_threshold_enabled

                if intent_score_threshold == "None":
                    bot_obj.intent_score_threshold = 0
                else:
                    bot_obj.intent_score_threshold = float(
                        intent_score_threshold)

                bot_obj.enable_intent_level_nlp = is_intent_level_nlp_functionality_enabled

                bot_obj.bot_display_name = bot_name
                bot_obj.mask_confidential_info = mask_confidential_info
                bot_obj.is_inactivity_timer_enabled = bot_inactivity_detection_enabled
                if bot_obj.bot_inactivity_response != bot_inactivity_msg:
                    is_bot_inactivity_response_updated = "true"
                bot_obj.bot_inactivity_response = bot_inactivity_msg
                bot_obj.bot_inactivity_timer = bot_inactivity_time
                bot_obj.is_api_fail_email_notifiication_enabled = is_api_fail_email_notifiication_enabled
                bot_obj.bot_userid_cookie_timeout = bot_userid_cookie_timeout
                bot_obj.is_analytics_monitoring_enabled = is_analytics_monitoring_enabled
                bot_obj.show_brand_name = show_brand_name
                bot_obj.is_custom_js_required = custom_bot_js_required
                bot_obj.is_custom_css_required = custom_bot_css_required
                bot_obj.bot_response_delay_allowed = bot_response_delay_allowed
                bot_obj.bot_response_delay_timer = bot_response_delay_timer
                if bot_obj.bot_response_delay_message != bot_response_delay_message:
                    is_bot_response_delay_message_updated = "true"
                bot_obj.bot_response_delay_message = bot_response_delay_message

                if initial_intent_pk == "":
                    bot_obj.initial_intent = None
                else:
                    intent_objs = Intent.objects.filter(pk=initial_intent_pk)
                    if intent_objs.count() > 0:
                        bot_obj.initial_intent = intent_objs[0]

                # bot_obj.languages_supported.clear()
                # for selected_lang in selected_supported_languages:
                #     lang_obj = Language.objects.get(lang=selected_lang)
                #     bot_obj.languages_supported.add(lang_obj)

                date_format = "%Y-%m-%d"
                go_live_date = datetime.datetime.strptime(
                    go_live_date, date_format)
                bot_obj.go_live_date = go_live_date

                bot_obj.default_order_of_response = json.dumps(
                    default_order_of_response)
                bot_obj.max_file_size_allowed = max_file_size_allowed
                bot_obj.show_livechat_form_or_no = show_form
                bot_obj.use_show_customer_detail_livechat_processor = use_customer_details_processor
                bot_obj.use_end_chat_processor_livechat = use_end_chat_processor
                bot_obj.use_assign_agent_processor_livechat = use_assign_agent_processor

                if (bot_obj.masking_enabled and not masking_enabled) or bot_obj.masking_time != int(masking_time):
                    data_toggle_obj = EasyChatPIIDataToggle.objects.get(
                        user=user_obj, bot=bot_obj)

                    if data_toggle_obj and not data_toggle_obj.is_expired:
                        generated_token = str(data_toggle_obj.token)
                        if token == generated_token:
                            bot_obj.masking_enabled = masking_enabled
                            bot_obj.masking_time = masking_time
                            data_toggle_obj.is_expired = True
                            data_toggle_obj.save()
                        else:
                            logger.info("%s is trying to change the data masking toggle unethically", str(request.user.username), extra={'AppName': 'EasyChat', 'user_id': str(
                                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
                    else:
                        logger.info("%s is trying to change the data masking toggle unethically", str(request.user.username), extra={'AppName': 'EasyChat', 'user_id': str(
                            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
                else:
                    bot_obj.masking_enabled = masking_enabled

                bot_obj.csat_feedback_form_enabled = csat_feedback_form_enabled

                if scale_rating == "4_scale":
                    bot_obj.scale_rating_5 = False
                else:
                    bot_obj.scale_rating_5 = True

                bot_obj.enable_audio_notification = enable_audio_notification

                bot_obj.save()
                activity_update = {}
                if BotInfo.objects.filter(bot=bot_obj).exists():
                    bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()
                else:
                    words_file = os.path.join(
                        (os.path.abspath(os.path.dirname(__file__))), 'badwords.txt')
                    with open(words_file, 'r') as f:
                        censor_list = [line.strip() for line in f.readlines()]
                    bad_words = json.dumps(censor_list)
                    bot_info_obj = BotInfo.objects.create(
                        bot=bot_obj, activity_update=json.dumps(activity_update), bad_keywords=bad_words)

                activity_update = json.loads(bot_info_obj.activity_update)
                activity_update["is_bot_inactivity_response_updated"] = is_bot_inactivity_response_updated
                activity_update["is_bot_response_delay_message_updated"] = is_bot_response_delay_message_updated
                activity_update["is_flow_termination_bot_response_updated"] = is_flow_termination_bot_response_updated
                activity_update["is_flow_termination_confirmation_display_message_updated"] = is_flow_termination_confirmation_display_message_updated
                activity_update.update(emoji_activity_update)
                activity_update.update(profanity_activity_update)
                bot_info_obj.activity_update = json.dumps(activity_update)

                if is_trigger_livechat_enabled and autosuggest_livechat_word_limit == "":
                    autosuggest_livechat_word_limit = 30

                if is_livechat_manager:
                    bot_info_obj.is_trigger_livechat_enabled = is_trigger_livechat_enabled
                    bot_info_obj.autosuggest_livechat_word_limit = int(
                        autosuggest_livechat_word_limit)

                bot_info_obj.enable_abort_flow_feature = is_abort_flow_enabled
                bot_info_obj.is_advance_tree_level_nlp_enabled = is_advance_tree_level_nlp_enabled
                bot_info_obj.is_bot_break_email_notification_enabled = is_bot_break_email_notification_enabled
                bot_info_obj.livechat_provider = livechat_provider

                bot_info_obj.enable_do_not_translate = enable_do_not_translate
                bot_info_obj.do_not_translate_keywords_list = json.dumps(no_translate_keywords)
                bot_info_obj.do_not_translate_regex_list = json.dumps(no_translate_regex)

                bot_info_obj.save()

                logger.info("Bot Saved Successfully with SaveBotAPI", extra={'AppName': 'EasyChat', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
                # for old_bot_obj in Bot.objects.filter(slug=old_bot_slug):
                #     old_bot_obj.name = bot_obj.name
                #     old_bot_obj.save()

                nps_obj = NPS.objects.filter(bot=bot_obj)
                if nps_obj:
                    nps_obj = nps_obj[0]
                    nps_obj.channel.clear()
                    nps_obj.save()
                    for channel_name in selected_channels_list_nps:
                        channel_obj = Channel.objects.get(name=channel_name)
                        nps_obj.channel.add(channel_obj)
                        nps_obj.whatsapp_nps_time = whatsapp_nps_timer
                        nps_obj.viber_nps_time = viber_nps_timer
                        nps_obj.save()
                else:
                    nps_obj = NPS.objects.create(bot=bot_obj)
                    for channel_name in selected_channels_list_nps:
                        channel_obj = Channel.objects.get(name=channel_name)
                        nps_obj.channel.add(channel_obj)
                        nps_obj.whatsapp_nps_time = whatsapp_nps_timer
                        nps_obj.viber_nps_time = viber_nps_timer
                        nps_obj.save()
                # if ChunksOfSuggestions.objects.filter(bot=Bot.objects.get(pk=bot_id)):
                #     ChunksOfSuggestions.objects.filter(
                #         bot=Bot.objects.get(pk=bot_id)).delete()
                # build_suggestions_and_word_mapper_thread = threading.Thread(
                #     target=build_suggestions_and_word_mapper, args=(bot_id, Bot, WordMapper, Channel, Intent, ChunksOfSuggestions))
                # build_suggestions_and_word_mapper_thread.daemon = True
                # build_suggestions_and_word_mapper_thread.start()
                description = "Bot updated with bot id" + \
                    " (" + str(bot_id) + ")"
                add_audit_trail(
                    "EASYCHATAPP",
                    user_obj,
                    "Update-Bot",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveBotAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveMultilingualBotAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["data"])

            validation_obj = EasyChatInputValidation()

            data = json.loads(json_string)
            bot_id = data["bot_id"]
            selected_language = validation_obj.remo_html_from_string(
                data["selected_language"])
            flow_termination_bot_response = data[
                "flow_termination_bot_response"]
            flow_termination_bot_response = validation_obj.clean_html(
                flow_termination_bot_response)
            flow_termination_confirmation_display_message = data[
                "flow_termination_confirmation_display_message"]

            bot_inactivity_detection_enabled = data[
                "bot_inactivity_detection_enabled"]
            bot_inactivity_msg = data["bot_inactivity_msg"]

            bot_response_delay_allowed = data["bot_response_delay_allowed"]

            bot_response_delay_message = data["bot_response_delay_message"]

            is_suggest_livechat_for_profanity_words_enabled = data[
                "is_suggest_livechat_for_profanity_words_enabled"]

            profanity_response_text = data["profanity_response_text"]
            # emoji initializations

            angry_emoji_response = data["angry_emoji_response"]
            angry_emoji_response = validation_obj.clean_html(
                angry_emoji_response)
            happy_emoji_response = data["happy_emoji_response"]
            happy_emoji_response = validation_obj.clean_html(
                happy_emoji_response)
            neutral_emoji_response = data["neutral_emoji_response"]
            neutral_emoji_response = validation_obj.clean_html(
                neutral_emoji_response)
            sad_emoji_response = data["sad_emoji_response"]
            sad_emoji_response = validation_obj.clean_html(sad_emoji_response)

            # emoji initializations end

            if bot_inactivity_detection_enabled:
                if bot_inactivity_msg.strip() == "":
                    response = {}
                    response["status"] = 300
                    response["msg"] = "Bot inactivity message can't be empty."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            if bot_response_delay_allowed:
                if bot_response_delay_message.strip() == "":
                    response = {}
                    response["status"] = 300
                    response["msg"] = "Bot delay message can't be empty."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            if is_suggest_livechat_for_profanity_words_enabled.strip().lower() == "true":
                if profanity_response_text.strip() == "":
                    response = {}
                    response["status"] = 300
                    response["msg"] = "Profanity Bot Respone can't be empty."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            bot_obj = Bot.objects.filter(id=int(bot_id))
            if not bot_obj.exists():
                response = {}
                response["status"] = 300
                response["msg"] = "Bot Does not exists"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot_obj = bot_obj.first()
            language_obj = Language.objects.get(lang=selected_language)

            lang_tuned_bot_obj = LanguageTunedBot.objects.get(
                bot=bot_obj, language=language_obj)

            lang_tuned_bot_obj.flow_termination_bot_response = flow_termination_bot_response

            lang_tuned_bot_obj.flow_termination_confirmation_display_message = flow_termination_confirmation_display_message

            lang_tuned_bot_obj.emoji_angry_response_text = angry_emoji_response

            lang_tuned_bot_obj.emoji_happy_response_text = happy_emoji_response

            lang_tuned_bot_obj.emoji_neutral_response_text = neutral_emoji_response

            lang_tuned_bot_obj.emoji_sad_response_text = sad_emoji_response

            if bot_inactivity_detection_enabled:
                lang_tuned_bot_obj.bot_inactivity_response = bot_inactivity_msg

            if bot_response_delay_allowed:
                lang_tuned_bot_obj.bot_response_delay_message = bot_response_delay_message

            if is_suggest_livechat_for_profanity_words_enabled.strip().lower() == "true":
                lang_tuned_bot_obj.profanity_bot_response = profanity_response_text

            lang_tuned_bot_obj.save()

            description = "Multilingual Bot Configurations updated for language " + language_obj.name_in_english + " with bot id" + \
                " (" + str(bot_id) + ")"
            add_audit_trail(
                "EASYCHATAPP",
                user_obj,
                "Update-Bot",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveMultilingualBotAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetBotImageAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        channel_name = "Web"
        bot_id = ""
        try:
            data = request.data
            data = json.loads(data["json_string"])
            bot_id = data['bot_id']
            web_page = data['web_page']
            web_page_source = data["web_page_source"]
            selected_language = "en"
            if "selected_language" in data:
                selected_language = data["selected_language"]

            page_url_without_params = web_page.split('?')[0]

            traffic_source = TrafficSources.objects.filter(visiting_date=datetime.datetime.today().date(
            ), web_page=page_url_without_params, bot=Bot.objects.get(pk=bot_id), web_page_source__iexact=web_page_source)
            if traffic_source:
                traffic_source[0].web_page_visited = traffic_source[
                    0].web_page_visited + 1
                traffic_source[0].save()
            else:
                origin = urlparse(web_page)
                if origin.netloc not in settings.ALLOWED_HOSTS:
                    TrafficSources.objects.create(
                        web_page=page_url_without_params, web_page_visited=1, bot=Bot.objects.get(pk=bot_id), web_page_source=web_page_source)

            validation_obj = EasyChatInputValidation()

            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            channel = Channel.objects.filter(name="Web")[0]
            bot_channel = BotChannel.objects.filter(
                bot=bot_obj, channel=channel)[0]

            # checking if language template not present, then it will create default English language template
            try:
                selected_language_obj = Language.objects.get(
                    lang=selected_language)
                if selected_language_obj in bot_channel.languages_supported.all():
                    language_template_obj = RequiredBotTemplate.objects.get(
                        bot=bot_obj, language=Language.objects.get(lang=selected_language))
                else:
                    selected_language = "en"
                    check_and_create_bot_language_template_obj(
                        bot_obj, ["en"], RequiredBotTemplate, Language)
                    language_template_obj = RequiredBotTemplate.objects.get(
                        bot=bot_obj, language=Language.objects.get(lang=selected_language))
            except Exception:
                selected_language = "en"
                check_and_create_bot_language_template_obj(
                    bot_obj, ["en"], RequiredBotTemplate, Language)
                language_template_obj = RequiredBotTemplate.objects.get(
                    bot=bot_obj, language=Language.objects.get(lang=selected_language))
                pass

            origin = get_request_origin(request)
            service_valid = ServiceRequest.objects.filter(
                bot=bot_obj, request__contains=origin).count()

            if((str(request.META.get('HTTP_HOST')) != (str(origin))) and (service_valid == 0)):
                logger.info("Invalid access for bot", extra={
                    'AppName': 'EasyChatApp', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': bot_id})
                return HttpResponseBadRequest("Not allow on this domain")

            bot_image_url = str(bot_obj.bot_image)
            bot_image_url = urlparse(bot_image_url).path
            bot_position = bot_obj.bot_position
            bot_theme = None
            if bot_obj.default_theme != None:
                bot_theme = bot_obj.default_theme.pk
            bot_image_visible = bot_obj.bot_image_visible
            form_assist_obj = FormAssistBotData.objects.filter(bot=bot_obj)

            if not validation_obj.is_valid_url(settings.EASYCHAT_HOST_URL + bot_image_url) or bot_image_url[0:1] == "@":
                bot_image_url = ""

            response['bot_image_url'] = bot_image_url
            response['is_auto_pop_allowed'] = bot_obj.is_auto_pop_allowed
            response['is_auto_pop_allowed_desktop'] = bot_obj.is_auto_pop_allowed_desktop
            response['is_auto_pop_allowed_mobile'] = bot_obj.is_auto_pop_allowed_mobile
            response['is_auto_popup_inactivity_enabled'] = bot_obj.is_auto_popup_inactivity_enabled
            response['auto_pop_timer'] = bot_obj.auto_pop_timer
            response['auto_popup_type'] = bot_obj.auto_popup_type

            bot_info_obj = BotInfo.objects.get(bot=bot_obj)
            response['is_geolocation_enabled'] = bot_info_obj.is_geolocation_enabled
            custom_intents_enabled = bot_info_obj.enable_custom_intent_bubbles
            custom_intents_for = bot_info_obj.custom_intents_for
            custom_bubble_obj = CustomIntentBubblesForWebpages.objects.filter(
                bot=bot_obj, web_page=web_page, custom_intents_for=custom_intents_for).first()
            if(custom_intents_enabled and custom_bubble_obj != None):
                custom_intent_bubbles = list(
                    custom_bubble_obj.custom_intent_bubble.values_list('name'))
                custom_intent_bubbles = [str(intent_name[0])
                                         for intent_name in custom_intent_bubbles]
                custom_intent_bubbles = '", "'.join(custom_intent_bubbles)
                custom_intent_bubbles = '["' + custom_intent_bubbles + '"]'
                response['auto_popup_initial_messages'] = json.dumps(get_translated_text(
                    "$$$".join(json.loads(custom_intent_bubbles)), selected_language, EasyChatTranslationCache).split("$$$"))
            else:
                try:
                    auto_popup_initial_messages_list = json.loads(bot_obj.auto_popup_initial_messages)
                    translated_auto_popup_initial_messages_list = []
                    for intent_obj_pk in auto_popup_initial_messages_list:
                        temp_popup_intent = ""
                        lang_tuned_obj = LanguageTuningIntentTable.objects.filter(
                            language__lang=selected_language, intent__pk=intent_obj_pk).first()
                        if lang_tuned_obj:
                            temp_popup_intent = lang_tuned_obj.multilingual_name
                        else:
                            intent_obj = Intent.objects.get(pk=int(intent_obj_pk))
                            temp_popup_intent = get_translated_text(
                                intent_obj.name, selected_language, EasyChatTranslationCache)
                        translated_auto_popup_initial_messages_list.append(temp_popup_intent)
                    response['auto_popup_initial_messages'] = json.dumps(translated_auto_popup_initial_messages_list)
                except Exception:
                    response['auto_popup_initial_messages'] = json.dumps(get_translated_text(
                        "$$$".join(json.loads(bot_obj.auto_popup_initial_messages)), selected_language, EasyChatTranslationCache).split("$$$"))
            response['auto_pop_text'] = get_multilingual_auto_popup_response(
                bot_obj, selected_language, Language, LanguageTunedBot, EasyChatTranslationCache)
            response["bot_position"] = bot_position
            response["bot_theme"] = bot_theme
            response["bot_theme_color"] = bot_obj.bot_theme_color
            response["bot_theme_light_color"] = bot_obj.get_bot_theme_light_color_two()
            response["bot_image_visible"] = bot_image_visible
            response["autocorrect_bot_replace"] = list(
                bot_obj.autcorrect_replace_bot)
            response[
                "form_assist_autopop_up_timer"] = bot_obj.form_assist_autopop_up_timer
            response[
                "form_assist_inactivity_timer"] = bot_obj.form_assist_inactivity_timer
            response[
                "is_form_assist_auto_pop_allowed"] = bot_obj.is_form_assist_enabled
            response["is_minimization_enabled"] = bot_obj.is_minimization_enabled
            response['disable_auto_popup_minimized'] = bot_obj.disable_auto_popup_minimized
            response['font_style'] = bot_obj.font
            response['is_nps_required'] = bot_obj.is_nps_required
            response[
                'last_bot_updated_time'] = bot_obj.last_bot_updated_datetime.strftime('%s')
            response['allowed_hosts'] = settings.ALLOWED_HOSTS
            response["maximize_text"] = language_template_obj.maximize_text
            response["minimize_text"] = language_template_obj.minimize_text
            response["selected_language"] = selected_language
            response["form_assist_auto_popup_type"] = "1"
            response["form_assist_intent_bubble_timer"] = 10
            response["form_assist_intent_bubble_inactivity_timer"] = 5
            response["form_assist_intent_bubble_type"] = "1"
            response["form_assist_auto_pop_text"] = get_translated_text(
                "Welcome. How may I help you today?", selected_language, EasyChatTranslationCache)
            response["form_assist_intent_bubble"] = "[]"
            response["is_voice_based_form_assist_enabled"] = False
            response["form_assist_tag_timer"] = "[]"
            response["form_assist_intent_responses_dict"] = "[]"
            response["form_assist_tag_intents"] = "[]"
            response["form_assist_tag_mapping"] = "[]"

            # check and get form assist popup detils
            if form_assist_obj.exists():
                form_assist_obj = form_assist_obj[0]
                response["form_assist_auto_popup_type"] = form_assist_obj.form_assist_auto_popup_type
                response["form_assist_autopop_up_timer"] = form_assist_obj.form_assist_autopop_up_timer
                response["form_assist_inactivity_timer"] = form_assist_obj.form_assist_autopop_up_inactivity_timer
                response["form_assist_intent_bubble_timer"] = form_assist_obj.form_assist_intent_bubble_timer
                response["form_assist_intent_bubble_inactivity_timer"] = form_assist_obj.form_assist_intent_bubble_inactivity_timer
                response["form_assist_intent_bubble_type"] = form_assist_obj.form_assist_intent_bubble_type
                response["form_assist_auto_pop_text"] = get_multilingual_form_assist_auto_popup_response(
                    bot_obj, form_assist_obj, selected_language, Language, LanguageTunedBot, EasyChatTranslationCache)
                response["is_voice_based_form_assist_enabled"] = form_assist_obj.is_voice_based_form_assist_enabled
                response["enable_response_form_assist"] = form_assist_obj.enable_response_form_assist

                custom_bubble_obj = CustomIntentBubblesForWebpages.objects.filter(
                    bot=bot_obj, web_page=web_page, custom_intents_for=FORM_ASSIST).first()
                if(custom_intents_enabled and custom_bubble_obj != None):
                    selected_form_assist_intents = dict(
                        custom_bubble_obj.custom_intent_bubble.all().values_list('pk', 'name'))
                    response["form_assist_intent_bubble"] = json.dumps(get_translated_text(
                        selected_form_assist_intents, selected_language, EasyChatTranslationCache))
                else:
                    selected_form_assist_intents = dict(
                        form_assist_obj.form_assist_intent_bubble.all().values_list('pk', 'name'))
                    response["form_assist_intent_bubble"] = json.dumps(get_translated_text(
                        selected_form_assist_intents, selected_language, EasyChatTranslationCache))

                form_assist_tag_timer = dict(FormAssist.objects.filter(
                    bot=bot_obj).values_list('tag_id', 'popup_timer'))

                form_assist_tag_intents = dict(FormAssist.objects.filter(
                    bot=bot_obj).values_list('intent__pk', 'intent__name'))

                form_assist_tag_mapping_obj = FormAssist.objects.filter(
                    bot=bot_obj)
                form_assist_tag_mapping = {}
                for tags in form_assist_tag_mapping_obj:
                    temp_list = [tags.intent.pk, tags.popup_timer]
                    form_assist_tag_mapping[tags.tag_id] = temp_list
                response["form_assist_tag_mapping"] = json.dumps(
                    form_assist_tag_mapping)

                response["form_assist_tag_intents"] = json.dumps(get_translated_text(
                    form_assist_tag_intents, selected_language, EasyChatTranslationCache))

                response["form_assist_tag_timer"] = json.dumps(
                    form_assist_tag_timer)

                form_assist_intent_responses = FormAssist.objects.filter(
                    bot=bot_obj).values_list('pk', 'intent__tree__response__sentence')
                form_assist_intent_responses_dict = {}
                for form_assist_intent_response in form_assist_intent_responses:
                    form_assist_intent_responses_dict[form_assist_intent_response[0]] = (
                        json.loads(form_assist_intent_response[1]))['items'][0]['speech_response']

                response["form_assist_intent_responses_dict"] = json.dumps(get_translated_text(
                    form_assist_intent_responses_dict, selected_language, EasyChatTranslationCache))
            # response['multilingual_web_landing_list'] = multilingual_web_landing_list
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "GetBotImageAPI {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': ''})

            try:
                if type(data) != dict:
                    data = json.loads(data)
                meta_data = data
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel_name, "", json.dumps(meta_data))

        return Response(data=response)


"""
API Tested: GetBotMessageImageAPI
input queries:
    bot_id: pk of current bot
expected output:
    status: 200 // SUCCESS
Return:
    return the bot theme color, path of bot message image, bot display name and bot terms and conditions.
"""


class GetBotMessageImageAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)

            validation_obj = EasyChatInputValidation()

            data = json.loads(data)
            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            bot_message_image_url = bot_obj.message_image.name
            bot_theme_color = bot_obj.bot_theme_color
            bot_display_name = bot_obj.bot_display_name
            bot_terms_and_conditions = bot_obj.terms_and_condition

            response['bot_theme_color'] = bot_theme_color
            response['bot_display_name'] = bot_display_name
            response['bot_message_image_url'] = bot_message_image_url
            response['bot_terms_and_conditions'] = bot_terms_and_conditions
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetBotMessageImageAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SubmitBotAdvanceSettingsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            json_string = DecryptVariable(request.data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_type = data["bot_type"]
            bot_type = validation_obj.remo_html_from_string(bot_type)
            child_bot_pk_list = data["child_bot_pk_list"]
            bot_trigger_keywords = data["bot_trigger_keywords"]
            bot_stop_keywords = data["bot_stop_keywords"]
            intent_score_threshold = data["intent_score_threshold"]
            is_auto_pop_allowed = data["is_bot_auto_popup_allowed"]

            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            bot_obj.bot_type = bot_type
            bot_obj.trigger_keywords = validation_obj.remo_html_from_string(
                bot_trigger_keywords)
            bot_obj.stop_keywords = json.dumps(bot_stop_keywords)
            if bot_type == "Composite":
                bot_obj.remove_all_child_bots()
                for bot_pk in child_bot_pk_list:
                    child_bot_obj = Bot.objects.get(
                        pk=int(bot_pk), is_deleted=False)
                    bot_obj.child_bots.add(child_bot_obj)

            bot_obj.intent_score_threshold = float(intent_score_threshold)
            bot_obj.is_auto_pop_allowed = is_auto_pop_allowed
            bot_obj.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SubmitBotAdvanceSettingsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class ChangeBotThemeColorAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            validation_obj = EasyChatInputValidation()

            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            bot_theme_color = bot_obj.bot_theme_color
            bot_display_name = bot_obj.bot_display_name
            response['bot_theme_color'] = bot_theme_color
            response['bot_display_name'] = bot_display_name
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ChangeBotThemeColorAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        return Response(data=response)


"""
function: prod_choice_obj_dict_func
input params:
    choice_obj_list: list of choice objects
output:
    return choice objects list

moves/creates choice objects from uat to production 
"""


def prod_choice_obj_dict_func(choice_obj_list):
    try:
        logger.info("Inside prod_choice_obj_dict_func", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        prod_choice_obj_dict = {}
        for choice_obj in choice_obj_list:
            choice_obj_pk = choice_obj.pk
            choice_prod_obj = Choice.objects.create(
                display=choice_obj.display,
                value=choice_obj.value)
            prod_choice_obj_dict[choice_obj_pk] = choice_prod_obj

        logger.info("Exit from prod_choice_obj_dict_func", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return prod_choice_obj_dict
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("prod_choice_obj_dict_func %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: prod_botresponse_obj_dict_func
input params:
    botresponse_obj_list: list of bot response objects
    prod_choice_obj_dict: dict of production choices
output:

moves/creates bot response objects from uat to production 
"""


def prod_botresponse_obj_dict_func(botresponse_obj_list, prod_choice_obj_dict):
    try:
        logger.info("Inside prod_botresponse_obj_dict_func", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        prod_botresponse_obj_dict = {}
        for botresponse_obj in botresponse_obj_list:
            botresponse_pk = botresponse_obj.pk
            botresponse_prod_obj = BotResponse.objects.create(sentence=botresponse_obj.sentence,
                                                              recommendations=botresponse_obj.recommendations,
                                                              cards=botresponse_obj.cards,
                                                              images=botresponse_obj.images,
                                                              videos=botresponse_obj.videos,
                                                              modes=botresponse_obj.modes,
                                                              modes_param=botresponse_obj.modes_param,
                                                              is_timed_response_present=botresponse_obj.is_timed_response_present,
                                                              timer_value=botresponse_obj.timer_value,
                                                              auto_response=botresponse_obj.auto_response)
            choice_obj_list = botresponse_obj.choices.all()
            for choice_obj in choice_obj_list:
                botresponse_prod_obj.choices.add(
                    prod_choice_obj_dict[choice_obj.pk])
            botresponse_prod_obj.save()

            prod_botresponse_obj_dict[botresponse_pk] = botresponse_prod_obj

        logger.info("Exit from prod_botresponse_obj_dict_func", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return prod_botresponse_obj_dict
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("prod_botresponse_obj_dict_func %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: prod_processor_obj_dict_func
input params:
    processor_obj_list: list of processor objects
output:

moves/creates processor objects from uat to production 
"""


def prod_processor_obj_dict_func(processor_obj_list):
    try:
        logger.info("Inside prod_processor_obj_dict_func", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        prod_processor_obj_dict = {}
        for processor_obj in processor_obj_list:
            processor_obj_pk = processor_obj.pk
            processor_prod_obj = Processor.objects.create(name=processor_obj.name,
                                                          function=processor_obj.function)
            prod_processor_obj_dict[processor_obj_pk] = processor_prod_obj

        logger.info("Exit from prod_processor_obj_dict_func", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return prod_processor_obj_dict
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("prod_processor_obj_dict_func %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: prod_apitree_obj_dict_func
input params:
    apitree_obj_list: list of API tree objects
output:

moves/creates API tree objects from uat to production 
"""


def prod_apitree_obj_dict_func(apitree_obj_list):
    try:
        logger.info("Inside prod_apitree_obj_dict_func", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        prod_apitree_obj_dict = {}
        for apitree_obj in apitree_obj_list:
            apitree_obj_pk = apitree_obj.pk
            apitree_prod_obj = ApiTree.objects.create(name=apitree_obj.name,
                                                      api_caller=apitree_obj.api_caller,
                                                      is_cache=apitree_obj.is_cache,
                                                      cache_variable=apitree_obj.cache_variable,
                                                      )
            users_obj_list = apitree_obj.users.all()
            if(users_obj_list != None):
                for user_obj in users_obj_list:
                    apitree_prod_obj.users.add(user_obj)

            prod_apitree_obj_dict[apitree_obj_pk] = apitree_prod_obj

        logger.info("Exit from prod_apitree_obj_dict_func", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return prod_apitree_obj_dict
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("prod_apitree_obj_dict_func %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


prod_tree_dict = {}


"""
function: create_prod_tree_obj
input params:
    tree_obj: tree object 
    prod_botresponse_obj_dict: dict containing  details of bot responses
    prod_apitree_obj_dict: dict containing  details of api trees
    prod_processor_obj_dict: dict containing  details of processor
output:

moves/creates tree objects from uat to production 
"""


def create_prod_tree_obj(tree_obj, prod_botresponse_obj_dict, prod_apitree_obj_dict, prod_processor_obj_dict):
    try:
        if(tree_obj.pk in prod_tree_dict):
            return

        tree_prod_obj = Tree.objects.create(name=tree_obj.name,
                                            accept_keywords=tree_obj.accept_keywords)

        response_obj = tree_obj.response
        pre_processor_obj = tree_obj.pre_processor
        post_processor_obj = tree_obj.post_processor
        pipe_processor_obj = tree_obj.pipe_processor
        api_tree_obj = tree_obj.api_tree

        if(response_obj != None):
            tree_prod_obj.response = prod_botresponse_obj_dict[response_obj.pk]

        if(pre_processor_obj != None):
            tree_prod_obj.pre_processor = prod_processor_obj_dict[
                pre_processor_obj.pk]

        if(post_processor_obj != None):
            tree_prod_obj.post_processor = prod_processor_obj_dict[
                post_processor_obj.pk]

        if(pipe_processor_obj != None):
            tree_prod_obj.pipe_processor = prod_processor_obj_dict[
                pipe_processor_obj.pk]

        if(api_tree_obj != None):
            tree_prod_obj.api_tree = prod_apitree_obj_dict[api_tree_obj.pk]

        if(len(tree_obj.children.all()) == 0):
            tree_obj_pk = tree_obj.pk
            prod_tree_dict[tree_obj_pk] = tree_prod_obj
            tree_prod_obj.save()
            return

        prod_tree_dict[tree_obj.pk] = tree_prod_obj

        for children_obj in tree_obj.children.all():
            if(children_obj.pk not in prod_tree_dict):
                create_prod_tree_obj(children_obj, prod_botresponse_obj_dict,
                                     prod_apitree_obj_dict, prod_processor_obj_dict)
            tree_prod_obj.children.add(prod_tree_dict[children_obj.pk])

        tree_prod_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_prod_tree_obj: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: prod_tree_obj_dict_func
input params:
    tree_obj_list: list of tree objects
    prod_botresponse_obj_dict: dict containing  details of bot responses
    prod_apitree_obj_dict: dict containing  details of api trees
    prod_processor_obj_dict: dict containing  details of processor
output:

moves/creates tree objects from uat to production 
"""


def prod_tree_obj_dict_func(tree_obj_list, prod_botresponse_obj_dict, prod_apitree_obj_dict, prod_processor_obj_dict):
    try:
        logger.info("Inside prod_tree_obj_dict_func", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        for tree_obj in tree_obj_list:
            create_prod_tree_obj(tree_obj,
                                 prod_botresponse_obj_dict,
                                 prod_apitree_obj_dict,
                                 prod_processor_obj_dict)

        logger.info("Exit from prod_tree_obj_dict_func", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("prod_tree_obj_dict_func %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


prod_bot_dict = {}

"""
function: create_prod_bot_obj
input params:
    bot_obj: Bot object
output:

moves/creates bot objects from uat to production 
"""


def create_prod_bot_obj(bot_obj):
    try:
        if(bot_obj.pk in prod_bot_dict):
            return
        bot_prod_obj = Bot.objects.create(name=bot_obj.name,
                                          trigger_keywords=bot_obj.trigger_keywords,
                                          stop_keywords=bot_obj.stop_keywords,
                                          bot_type=bot_obj.bot_type,
                                          bot_theme_color=bot_obj.bot_theme_color,
                                          bot_image=bot_obj.bot_image,
                                          message_image=bot_obj.message_image,
                                          is_uat=False,
                                          is_active=True,
                                          )

        users_obj_list = bot_obj.users.all()
        if(users_obj_list != None):
            for user_obj in users_obj_list:
                bot_prod_obj.users.add(user_obj)

        if(len(bot_obj.child_bots.all()) == 0):
            bot_obj_pk = bot_obj.pk
            prod_bot_dict[bot_obj_pk] = bot_prod_obj
            return

        prod_bot_dict[bot_obj.pk] = bot_prod_obj

        for child_obj in bot_obj.child_bots.all():
            if(child_obj.pk not in prod_bot_dict):
                create_prod_bot_obj(child_obj)
            bot_prod_obj.child_bots.add(prod_bot_dict[child_obj.pk])

        bot_prod_obj.save()
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("prod_tree_obj_dict_func %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})


"""
function: prod_bot_obj_dict_func
input params:
    bot_obj_list: list of Bot objects
output:

moves/creates bot objects from uat to production 
"""


def prod_bot_obj_dict_func(bot_obj_list):
    try:
        logger.info("Inside prod_bot_obj_dict_func", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        for bot_obj in bot_obj_list:
            create_prod_bot_obj(bot_obj)

        logger.info("Exit from prod_bot_obj_dict_func", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("prod_bot_obj_dict_func %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: prod_authentication_obj_func
input params:
    authentication_obj_list: list of authentication objects
output:

moves/creates authentication objects from uat to production 
"""


# def prod_authentication_obj_func(authentication_obj_list):
#     logger.info("Inside prod_authentication_obj", extra={
#                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#     try:
#         prod_authentication_obj_dict = {}
#         # print('0000000000000000000000000000000000000000000000000000000000000000')
#         # print(authentication_obj_list)
#         for authentication_obj in authentication_obj_list:
#             authentication_obj_pk = authentication_obj.pk
#             # print('authentication_obj_pk ', authentication_obj_pk)
#             authentication_prod_obj = Authentication.objects.create(name=authentication_obj.name,
#                                                                     auth_time=authentication_obj.auth_time
#                                                                     )
#             tree_obj = authentication_obj.tree
#             # print('tree object ')
#             # print(tree_obj)
#             # print(tree_obj.pk)

#             # print('authentication_prod_obj_pk ', authentication_prod_obj.pk)

#             if(tree_obj != None):
#                 # print('value of prod tree is ', prod_tree_dict[tree_obj.pk])
#                 authentication_prod_obj.tree = prod_tree_dict[tree_obj.pk]
#             authentication_prod_obj.save()

#             prod_authentication_obj_dict[
#                 authentication_obj_pk] = authentication_prod_obj

#         return prod_authentication_obj_dict

#     except Exception as e:  # noqa: F841
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("prod_authentication_obj_func %s at %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#         # return HttpResponse("500")
#         return render(request, 'EasyChatApp/error_500.html')


"""
function: prod_userauthentication_obj_func
input params:
    userauthentication_obj_list: list of user authentication objects
    prod_authentication_dict: dict of detail containing authentication objects
output:

moves/creates user authentication objects from uat to production 
"""


# def prod_userauthentication_obj_func(userauthentication_obj_list, prod_authentication_dict):
#     logger.info("Inside prod_userauthentication_obj_func", extra={
#                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

#     try:
#         for userauthentication_obj in userauthentication_obj_list:
#             UserAuthentication.objects.create(user=userauthentication_obj.user,
#                                               auth_type=prod_authentication_dict[
#                                                   userauthentication_obj.auth_type.pk],
#                                               start_time=userauthentication_obj.start_time,
#                                               user_params=userauthentication_obj.user_params)
#             # print(userauthentication_prod_obj.pk,userauthentication_prod_obj.auth_type.pk)
#     except Exception as e:  # noqa: F841
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("prod_userauthentication_obj_func %s at %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

#     logger.info("Exit from prod_userauthentication_obj_func", extra={
#                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: prod_botchannel_obj_func
input params:
    botchannel_obj_list: list of user bot channel objects
    bot_obj: bot object
output:

moves/creates bot channel objects from uat to production 
"""


def prod_botchannel_obj_func(botchannel_obj_list, bot_obj):
    logger.info("Inside prod_botchannel_obj_func", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

    try:
        prod_botchannel_obj_dict = {}
        # print(botchannel_obj_list)
        BotChannel.objects.filter(bot__in=[prod_bot_dict[bot_obj.pk]]).delete()
        for botchannel_obj in botchannel_obj_list:

            BotChannel.objects.filter(
                bot=prod_bot_dict[bot_obj.pk], channel=botchannel_obj.channel).delete()

            botchannel_obj_pk = botchannel_obj.pk

            botchannel_prod_obj = None

            if len(BotChannel.objects.filter(bot=prod_bot_dict[bot_obj.pk], channel=botchannel_obj.channel)) == 0:
                botchannel_prod_obj = BotChannel.objects.create(bot=prod_bot_dict[bot_obj.pk],
                                                                channel=botchannel_obj.channel,
                                                                welcome_message=botchannel_obj.welcome_message,
                                                                authentication_message=botchannel_obj.authentication_message,
                                                                reprompt_message=botchannel_obj.reprompt_message,
                                                                session_end_message=botchannel_obj.session_end_message,
                                                                initial_messages=botchannel_obj.initial_messages,
                                                                channel_params=botchannel_obj.channel_params,
                                                                )
            else:
                botchannel_prod_obj.welcome_message = botchannel_obj.welcome_message
                botchannel_prod_obj.authentication_message = botchannel_obj.authentication_message
                botchannel_prod_obj.reprompt_message = botchannel_obj.reprompt_message
                botchannel_prod_obj.session_end_message = botchannel_obj.session_end_message
                botchannel_prod_obj.initial_messages = botchannel_obj.initial_messages
                botchannel_prod_obj.channel_params = botchannel_obj.channel_params
                botchannel_prod_obj.save()

            prod_botchannel_obj_dict[
                botchannel_obj_pk] = botchannel_prod_obj

        return prod_botchannel_obj_dict

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("prod_botchannel_obj_func %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

    logger.info("Exit from prod_botchannel_obj_func", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})


"""
function: create_prod_intent_obj
input params:
    prod_authentication_dict: dict of authentication objects
    intent_obj: intent object
output:

moves/creates intent objects from uat to production 
"""


def create_prod_intent_obj(intent_obj, prod_authentication_dict):
    # logger.info("Inside create_prod_intent_obj")
    try:
        prod_intent_obj = Intent.objects.create(name=intent_obj.name,
                                                keywords=intent_obj.keywords,
                                                training_data=intent_obj.training_data,
                                                restricted_keywords=intent_obj.restricted_keywords,
                                                necessary_keywords=intent_obj.necessary_keywords,
                                                threshold=intent_obj.threshold,
                                                last_modified=intent_obj.last_modified,
                                                is_feedback_required=intent_obj.is_feedback_required,
                                                is_authentication_required=intent_obj.is_authentication_required,
                                                auth_type=intent_obj.auth_type,
                                                )

        prod_intent_obj.auth_type = None
        default_created_tree_obj = prod_intent_obj.tree
        if(default_created_tree_obj != None):
            default_created_tree_obj.delete()

        tree_obj = intent_obj.tree
        bot_obj_list = intent_obj.bots.all()
        try:
            stem_words = get_stem_words_of_sentence(
                intent_obj.name, None, None, None, bot_obj_list[0])
            stem_words.sort()
            hashed_name = ' '.join(stem_words)
            hashed_name = hashlib.md5(hashed_name.encode()).hexdigest()
            prod_intent_obj.intent_hash = hashed_name
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[create_prod_intent_obj] %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        channel_obj_list = intent_obj.channels.all()
        auth_type_obj = intent_obj.auth_type
        if auth_type_obj != None:
            prod_intent_obj.auth_type = prod_authentication_dict[
                auth_type_obj.pk]
        if tree_obj != None:
            prod_intent_obj.tree = prod_tree_dict[tree_obj.pk]

        prod_intent_obj.save()
        for bot_obj in bot_obj_list:
            if bot_obj.pk in prod_bot_dict:
                prod_intent_obj.bots.add(prod_bot_dict[bot_obj.pk])
            else:
                logger.info(
                    'this bot is not in dictionary this bot is not in dictionary this bot is not in dictionary ', extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        for channel_obj in channel_obj_list:
            prod_intent_obj.channels.add(channel_obj)

        prod_intent_obj.save()

        return intent_obj
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[create_prod_intent_obj] %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: prod_intent_obj_func
input params:
    prod_authentication_dict: dict of authentication objects
    intent_obj_list: intent object list
output:

moves/creates intent objects from uat to production 
"""


def prod_intent_obj_func(intent_obj_list, prod_authentication_dict):
    logger.info("Inside prod_intent_obj", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    try:
        for intent_obj in intent_obj_list:
            create_prod_intent_obj(
                intent_obj, prod_authentication_dict)
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error prod_intent_obj_func ! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    logger.info("Exit from prod_intent_obj", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: get_intent_related_to_bot
input params:
    bot_obj: bot object
output:
returns list of intents associated with that bot objects 
"""


# def get_intent_related_to_bot(bot_obj):
#     try:
#         intents = Intent.objects.filter(
#             bots__in=[bot_obj], is_deleted=False, is_hidden=False)
#         return intents
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("get_intent_related_to_bot ! %s %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})
#         # return HttpResponse("500")
#         return render(request, 'EasyChatApp/error_500.html')


"""
function: get_trees_related_to_intents
input params:
    intent_list: list of intents
output:
returns list of trees associated with given list of intents
"""


# def get_trees_related_to_intents(intent_list):
#     try:
#         tree_list = []
#         for intent in intent_list:
#             if(intent.tree not in tree_list and intent.tree != None):
#                 tree_list.append(intent.tree)

#         return tree_list
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("get_trees_related_to_intents ! %s %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#         # return HttpResponse("500")
#         return render(request, 'EasyChatApp/error_500.html')


"""
function: get_bot_response_related_to_trees
input params:
    tree_list: list of trees
output:
returns list of bot responses associated with given list of trees
"""


# def get_bot_response_related_to_trees(tree_list):
#     try:
#         bot_response_list = []
#         for tree in tree_list:
#             if(tree.response not in bot_response_list and tree.response != None):
#                 bot_response_list.append(tree.response)

#         return bot_response_list
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("get_bot_response_related_to_trees ! %s %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#         # return HttpResponse("500")
#         return render(request, 'EasyChatApp/error_500.html')


"""
function: get_choice_related_to_bot_responses
input params:
    bot_response_list: list of bot responses
output:
returns list of choices associated with given list of bot responses
"""


def get_choice_related_to_bot_responses(bot_response_list):
    try:
        choice_list = []
        for bot_response in bot_response_list:
            for choice in bot_response.choices.all():
                if(choice not in choice_list and choice != None):
                    choice_list.append(choice)

        return choice_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_choice_related_to_bot_responses ! %s %s",
                     str(e), str(exc_tb.tb_lineno))
        return HttpResponse("500", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: get_all_trees
input params:
    tree_obj: tree object
    final_tree_obj_list: list of child trees
output:
returns list of child trees associated with given tree object
"""


def get_all_trees(tree_obj, final_tree_obj_list):
    try:
        if(tree_obj == None):
            return
        if(tree_obj in final_tree_obj_list):
            return
        if(len(tree_obj.children.all()) == 0):
            final_tree_obj_list.append(tree_obj)
            return
        final_tree_obj_list.append(tree_obj)
        for children_obj in tree_obj.children.all():
            if(children_obj not in final_tree_obj_list and children_obj != None):
                get_all_trees(children_obj, final_tree_obj_list)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_all_trees ! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: get_trees_related_to_trees
input params:
    tree_list: list of trees
output:
returns list of child trees associated with given tree object list
"""


# def get_trees_related_to_trees(tree_list):
#     final_tree_obj_list = []
#     try:
#         for tree in tree_list:
#             get_all_trees(tree, final_tree_obj_list)
#         return final_tree_obj_list
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("get_trees_related_to_trees ! %s %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#         # return HttpResponse("500")
#         return render(request, 'EasyChatApp/error_500.html')


"""
function: get_api_trees_related_to_trees
input params:
    tree_list: list of trees
output:
returns list of api trees associated with given tree object list
"""


# def get_api_trees_related_to_trees(tree_list):
#     api_tree_list = []
#     try:
#         for tree in tree_list:
#             if tree.api_tree not in api_tree_list and tree.api_tree != None:
#                 api_tree_list.append(tree.api_tree)
#         return api_tree_list
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("get_api_trees_related_to_trees ! %s %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#         # return HttpResponse("500")
#         return render(request, 'EasyChatApp/error_500.html')


"""
function: get_processors_from_tree_list
input params:
    tree_list: list of trees
output:
returns list of processors associated with given tree object list
"""


# def get_processors_from_tree_list(tree_list):
#     try:
#         processor_list = []
#         for tree in tree_list:
#             if tree.pre_processor not in processor_list and tree.pre_processor != None:
#                 processor_list.append(tree.pre_processor)
#             if tree.post_processor not in processor_list and tree.post_processor != None:
#                 processor_list.append(tree.post_processor)
#             if tree.pipe_processor not in processor_list and tree.pipe_processor != None:
#                 processor_list.append(tree.pipe_processor)
#         return processor_list
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("get_processors_from_tree_list ! %s %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#         # return HttpResponse("500")
#         return render(request, 'EasyChatApp/error_500.html')


"""
function: get_authentication_objects_from_intent
input params:
    intent_obj_list: list of intent objects
output:
returns list of authentication objs associated with given intent object list
"""


# def get_authentication_objects_from_intent(intent_obj_list):
#     try:
#         authentication_obj_list = []

#         for intent_obj in intent_obj_list:
#             if(intent_obj.auth_type not in authentication_obj_list and intent_obj.auth_type != None):
#                 authentication_obj_list.append(intent_obj.auth_type)
#         return authentication_obj_list
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("get_authentication_objects_from_intent ! %s %s",
#                      str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#         # return HttpResponse("500")
#         return render(request, 'EasyChatApp/error_500.html')


"""
function: get_userauthentication_objects_from_authentication
input params:
    authentication_obj_list: list of authentication objects
output:
returns list of user authentication objs associated with given authentication object list
"""


# def get_userauthentication_objects_from_authentication(authentication_obj_list):
#     try:
#         userauthentication_obj_list = []
#         all_userauthentication_obj_list = UserAuthentication.objects.all()
#         for userauthentication_obj in all_userauthentication_obj_list:
#             if(userauthentication_obj.auth_type in authentication_obj_list and userauthentication_obj.auth_type not in userauthentication_obj_list and userauthentication_obj.auth_type != None):
#                 userauthentication_obj_list.append(userauthentication_obj)
#         return userauthentication_obj_list
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("get_userauthentication_objects_from_authentication ! %s %s", str(
#             e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#         # return HttpResponse("500")
#         return render(request, 'EasyChatApp/error_500.html')


"""
function: move_misdashboard_objects_to_new_bot
input params:
    bot_prod_obj: production bot object
output:
moves all mis objects from old production bot to new production bot object
"""


def move_misdashboard_objects_to_new_bot(bot_prod_obj):
    logger.info("Inside move_misdashboard_objects_to_new_bot...", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    try:
        curr_prod_bot = bot_prod_obj.order_by('-pk')[0]
        old_prod_bot_list = bot_prod_obj.order_by('-pk')[1:]

        for old_prod_bot in old_prod_bot_list:
            misdashboard_objs = MISDashboard.objects.filter(bot=old_prod_bot)
            for misdashboard_obj in misdashboard_objs:
                misdashboard_obj.bot = curr_prod_bot
                misdashboard_obj.save()
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in move_misdashboard_objects_to_new_bot: %s at %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    logger.info("Exit from move_misdashboard_objects_to_new_bot...", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: move_to_production
input params:
    user_obj: active user object
    bot_id: pk of bot which is to be moved to production
output:
moves given bot object to production
"""


def move_to_production(user_obj, bot_id):
    logger.info("Inside move_to_production", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
    try:
        bot_obj = Bot.objects.get(pk=bot_id, is_deleted=False)

        intent_obj_list = get_intent_related_to_bot(bot_obj)

        if(intent_obj_list == None):
            raise ValueError('Intent Object List Empty')

        authentication_obj_list = get_authentication_objects_from_intent(
            intent_obj_list)

        if(authentication_obj_list == None):
            raise ValueError('Authentication Object List Empty')

        userauthentication_obj_list = get_userauthentication_objects_from_authentication(
            authentication_obj_list)

        if(userauthentication_obj_list == None):
            raise ValueError('User Authentication Object List Empty')

        tree_obj_list = get_trees_related_to_intents(intent_obj_list)

        if(tree_obj_list == None):
            raise ValueError('Tree Object List Empty')

        for authentication_obj in authentication_obj_list:
            if(authentication_obj.tree != None):
                tree_obj_list.append(authentication_obj.tree)

        final_tree_obj_list = get_trees_related_to_trees(tree_obj_list)

        if(final_tree_obj_list == None):
            raise ValueError('Final Tree Object List Empty')

        bot_response_obj_list = get_bot_response_related_to_trees(
            final_tree_obj_list)

        if(bot_response_obj_list == None):
            raise ValueError('Bot Response Object List Empty')

        choice_obj_list = get_choice_related_to_bot_responses(
            bot_response_obj_list)

        if(choice_obj_list == None):
            raise ValueError('Choice Object List Empty')

        api_tree_obj_list = get_api_trees_related_to_trees(final_tree_obj_list)

        if(api_tree_obj_list == None):
            raise ValueError('API Tree Object List Empty')

        processor_obj_list = get_processors_from_tree_list(final_tree_obj_list)

        if(processor_obj_list == None):
            raise ValueError('Processor Object List Empty')

        prod_choice_obj_dict = prod_choice_obj_dict_func(choice_obj_list)

        prod_botresponse_obj_dict = prod_botresponse_obj_dict_func(
            bot_response_obj_list, prod_choice_obj_dict)

        prod_processor_obj_dict = prod_processor_obj_dict_func(
            processor_obj_list)

        prod_apitree_obj_dict = prod_apitree_obj_dict_func(api_tree_obj_list)

        prod_bot_dict.clear()

        prod_bot_obj_dict_func([bot_obj])

        prod_tree_dict.clear()

        prod_tree_obj_dict_func(
            final_tree_obj_list, prod_botresponse_obj_dict, prod_apitree_obj_dict, prod_processor_obj_dict)

        prod_authentication_dict = prod_authentication_obj_func(
            authentication_obj_list)

        prod_userauthentication_obj_func(
            userauthentication_obj_list, prod_authentication_dict)

        bot_channel_list = BotChannel.objects.filter(bot__in=[bot_obj])

        prod_botchannel_dict = prod_botchannel_obj_func(  # noqa: F841
            bot_channel_list, bot_obj)

        bot_mis_obj = bot_obj
        bot_prod_obj = Bot.objects.filter(
            slug=bot_obj.slug, is_active=True, is_deleted=False)

        if(len(bot_prod_obj) > 0):
            bot_mis_obj = bot_prod_obj.order_by('-pk')[0]  # noqa: F841

        prod_intent_obj_func(intent_obj_list, prod_authentication_dict)

        move_misdashboard_objects_to_new_bot(bot_prod_obj)

        delete_prod_bot_objs = bot_prod_obj.order_by('-pk')[2:]

        for bot_obj in delete_prod_bot_objs:

            intent_obj_list = get_intent_related_to_bot(bot_obj)

            if(intent_obj_list == None):
                raise ValueError('Intent Object List Empty')

            authentication_obj_list = get_authentication_objects_from_intent(
                intent_obj_list)

            if(authentication_obj_list == None):
                raise ValueError('Authentication Object List Empty')

            userauthentication_obj_list = get_userauthentication_objects_from_authentication(
                authentication_obj_list)

            if(userauthentication_obj_list == None):
                raise ValueError('User Authentication Object List Empty')

            tree_obj_list = get_trees_related_to_intents(intent_obj_list)

            if(tree_obj_list == None):
                raise ValueError('Tree Object List Empty')

            for authentication_obj in authentication_obj_list:
                if(authentication_obj.tree != None):
                    tree_obj_list.append(authentication_obj.tree)

            final_tree_obj_list = get_trees_related_to_trees(tree_obj_list)

            if(final_tree_obj_list == None):
                raise ValueError('Final Tree Object List Empty')

            bot_response_obj_list = get_bot_response_related_to_trees(
                final_tree_obj_list)

            if(bot_response_obj_list == None):
                raise ValueError('Bot Response Object List Empty')

            choice_obj_list = get_choice_related_to_bot_responses(
                bot_response_obj_list)

            if(choice_obj_list == None):
                raise ValueError('Choice Object List Empty')

            api_tree_obj_list = get_api_trees_related_to_trees(
                final_tree_obj_list)

            if(api_tree_obj_list == None):
                raise ValueError('API Tree Object List Empty')

            processor_obj_list = get_processors_from_tree_list(
                final_tree_obj_list)

            if(processor_obj_list == None):
                raise ValueError('Processor Object List Empty')

            for intent_obj in intent_obj_list:
                try:
                    intent_obj.delete()
                except Exception as e:  # noqa: F841
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("move_to_production %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

            for authentication_obj in authentication_obj_list:
                try:
                    authentication_obj.delete()
                except Exception as e:  # noqa: F841
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("move_to_production %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

            for userauthentication_obj in userauthentication_obj_list:
                try:
                    userauthentication_obj.delete()
                except Exception as e:  # noqa: F841
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("move_to_production %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

            for tree_obj in final_tree_obj_list:
                try:
                    tree_obj.delete()
                except Exception as e:  # noqa: F841
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("move_to_production %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

            for bot_response_obj in bot_response_obj_list:
                try:
                    bot_response_obj.delete()
                except Exception as e:  # noqa: F841
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("move_to_production %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

            for choice_obj in choice_obj_list:
                try:
                    choice_obj.delete()
                except Exception as e:  # noqa: F841
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("move_to_production %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

            for api_tree_obj in api_tree_obj_list:
                try:
                    api_tree_obj.delete()
                except Exception as e:  # noqa: F841
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("move_to_production %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

            for processor_obj in processor_obj_list:
                try:
                    processor_obj.delete()
                except Exception as e:  # noqa: F841
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("move_to_production %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

            bot_obj.delete()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error move_to_production! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
    logger.info("Exit from move_to_production", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})


# class MoveBotToProductionAPI(APIView):

#     permission_classes = (IsAuthenticated,)

#     authentication_classes = (
#         CsrfExemptSessionAuthentication, BasicAuthentication)

#     def post(self, request, *args, **kwargs):
#         response = {}
#         response["status"] = 500
#         try:
#             data = request.data
#             username = request.user.username
#             user_obj = User.objects.get(username=str(username))

#             data = DecryptVariable(data["json_string"])
#             data = json.loads(data)

#             validation_obj = EasyChatInputValidation()

#             bot_id = data['bot_id']
#             bot_id = validation_obj.remo_html_from_string(bot_id)

#             move_to_production_thread = threading.Thread(
#                 target=move_to_production, args=(user_obj, bot_id,))
#             move_to_production_thread.daemon = True
#             move_to_production_thread.start()
#             response["status"] = 200
#         except Exception as e:  # noqa: F841
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error("Error MoveBotToProductionAPI! %s %s",
#                          str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

#         custom_encrypt_obj = CustomEncrypt()
#         response = custom_encrypt_obj.encrypt(json.dumps(response))
#         return Response(data=response)


class DeployChatBotAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(bot_id)
            server_url = data['server_url']
            server_url = validation_obj.remo_html_from_string(server_url)

            bot_obj = Bot.objects.get(pk=bot_id, is_deleted=False)
            bot_is_form_assist_enabled = bot_obj.is_form_assist_enabled
            bot_is_lead_generation_enabled = bot_obj.is_lead_generation_enabled

            bot_theme = "null"
            if bot_obj.default_theme:
                bot_theme = bot_obj.default_theme.pk

            bot_position = bot_obj.bot_position
            bot_image_visible = bot_obj.bot_image_visible

            theme3_embed_file = open(
                settings.BASE_DIR + "/EasyChatApp/static/EasyChatApp/js/theme2_embed.js", "r")

            try:
                if bot_obj.default_theme.main_page == "EasyChatApp/theme1_bot.html":
                    theme3_embed_file = open(
                        settings.BASE_DIR + "/EasyChatApp/static/EasyChatApp/js/theme1_embed.js", "r")
                if bot_obj.default_theme.main_page == "EasyChatApp/theme2_bot.html":
                    theme3_embed_file = open(
                        settings.BASE_DIR + "/EasyChatApp/static/EasyChatApp/js/theme2_embed.js", "r")
                if bot_obj.default_theme.main_page == "EasyChatApp/theme3_bot.html":
                    theme3_embed_file = open(
                        settings.BASE_DIR + "/EasyChatApp/static/EasyChatApp/js/theme3_embed.js", "r")
                if bot_obj.default_theme.main_page == "EasyChatApp/theme4_bot.html":
                    theme3_embed_file = open(
                        settings.BASE_DIR + "/EasyChatApp/static/EasyChatApp/js/theme4_embed.js", "r")

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Default Theme is selected! %s %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
                pass

            meta_data = "SERVER_URL='" + server_url + "';"
            meta_data += "BOT_ID=" + str(bot_id) + ";"
            meta_data += "BOT_NAME='uat';"
            meta_data += "BOT_THEME='" + str(bot_theme) + "';"
            meta_data += "BOT_POSITION='" + str(bot_position) + "';"

            if bot_image_visible:
                meta_data += "bot_click_image = 'true';"
            else:
                meta_data += "bot_click_image = 'false';"

            if bot_is_form_assist_enabled == True:
                meta_data += "is_form_assist='true';"
            else:
                meta_data += "is_form_assist='false';"

            if bot_is_lead_generation_enabled == True:
                create_lead_bot_intent_flow(bot_obj)

            if bot_is_lead_generation_enabled == True:
                lead_generation_intent_obj = Intent.objects.filter(
                    bots__in=[bot_obj], name="Learn more about us", is_deleted=False).first()
                if lead_generation_intent_obj:
                    meta_data += "is_lead_generation='true';"
                    meta_data += "lead_generation_intent_id='" + \
                        str(lead_generation_intent_obj.pk) + "';"
                else:
                    meta_data += "is_lead_generation='false';"
                    meta_data += "lead_generation_intent_id='';"
            else:
                meta_data += "is_lead_generation='false';"
                meta_data += "lead_generation_intent_id='';"

            auth_user_obj = User.objects.get(username=request.user.username)

            cobrowse_access_token_obj = None
            try:
                cobrowse_access_token_obj = CobrowseAccessToken.objects.get(
                    agent__user=auth_user_obj)
            except Exception:
                pass

            if bot_obj.is_easy_assist_allowed == True and cobrowse_access_token_obj != None:
                meta_data += "is_easyassist_enabled='true';"
                meta_data += "easyassist_token='" + \
                    str(cobrowse_access_token_obj.key) + "';"
            else:
                meta_data += "is_easyassist_enabled='false';"
                meta_data += "easyassist_token='';"

            web_landing_list = []
            web_landing_list.append(
                {"selected_language": "en", "data": json.loads(bot_obj.web_url_landing_data)})

            web_landing_list = get_translated_bot_web_landing_list(
                bot_obj, web_landing_list, BotChannel, LanguageTunedBot, EasyChatTranslationCache)
            meta_data += "var web_landing_list=" + str(web_landing_list) + ";"
            meta_data += "notif_and_cross_div = document.createElement('div');"
            meta_data += "notif_and_cross_div.innerHTML =" + "\"""<div id='notif_and_cross_div' onmouseover='show_cross()' onmouseout='dont_show_cross()' style='position:fixed;right:90px;bottom:7em;height:100px;width:400px;display:none;z-index:9999999999'><svg onclick='hide_notification()' id='cross-chatbox-notification' width='28' height='28' viewBox='0 0 28 28' fill='none' xmlns='http://www.w3.org/2000/svg' style='position: fixed;cursor: pointer;right: 90px;bottom: 12.5em;z-index: 2147483647;display: none;'><circle cx='14' cy='14' r='14' fill='#3871F0' fill-opacity='0.08'></circle><path d='M10.3335 9.21192L14.0001 12.8781L17.6667 9.22303C17.7388 9.14959 17.8255 9.09192 17.9211 9.05367C18.0167 9.01542 18.1193 8.99743 18.2222 9.00084C18.4242 9.01391 18.6145 9.10004 18.7576 9.24315C18.9007 9.38625 18.9869 9.57656 19 9.77852C19.001 9.87782 18.9818 9.97629 18.9436 10.068C18.9054 10.1596 18.849 10.2426 18.7777 10.3118L15.1001 14.0002L18.7777 17.6886C18.9222 17.8286 19.0022 18.0219 19 18.2219C18.9869 18.4239 18.9007 18.6142 18.7576 18.7573C18.6145 18.9004 18.4242 18.9865 18.2222 18.9996C18.1193 19.003 18.0167 18.985 17.9211 18.9468C17.8255 18.9085 17.7388 18.8508 17.6667 18.7774L14.0001 15.1223L10.3446 18.7774C10.2724 18.8508 10.1858 18.9085 10.0902 18.9468C9.99455 18.985 9.89203 19.003 9.78909 18.9996C9.58334 18.9889 9.38886 18.9023 9.24317 18.7567C9.09749 18.611 9.01094 18.4165 9.00023 18.2108C8.99922 18.1115 9.0184 18.013 9.0566 17.9214C9.0948 17.8297 9.15122 17.7467 9.22244 17.6775L12.9001 14.0002L9.21133 10.3118C9.14211 10.2416 9.08775 10.1583 9.05147 10.0666C9.0152 9.97502 8.99777 9.87703 9.00023 9.77852C9.0133 9.57656 9.09944 9.38625 9.24256 9.24315C9.38568 9.10004 9.576 9.01391 9.77798 9.00084C9.88012 8.99599 9.98215 9.01223 10.0777 9.04854C10.1733 9.08486 10.2604 9.14048 10.3335 9.21192V9.21192Z' fill='#3871F0'></path></svg><svg width='351' height='117' viewBox='0 0 351 117' fill='none' xmlns='http://www.w3.org/2000/svg' style='position: fixed;cursor: pointer;right: 80px;bottom: 5em;z-index: 2147483647;display: none;' id='chatbox-notification' onclick='open_up_bot()' class='animate__animated animate__pulse'><g filter='url(#filter0_d)'><rect x='15' y='15' width='321' height='62' rx='31' fill='white'></rect><path d='M298.764 102C298.764 102 270.667 92.1219 268.253 73.243H295.013C288.51 76.7439 282.248 82.7811 298.764 102Z' fill='white'></path></g><defs><filter id='filter0_d' x='0' y='0' width='351' height='117' filterUnits='userSpaceOnUse' color-interpolation-filters='sRGB'><feFlood flood-opacity='0' result='BackgroundImageFix'></feFlood><feColorMatrix in='SourceAlpha' type='matrix' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0'></feColorMatrix><feOffset></feOffset><feGaussianBlur stdDeviation='7.5'></feGaussianBlur><feColorMatrix type='matrix' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.1 0'></feColorMatrix><feBlend mode='normal' in2='BackgroundImageFix' result='effect1_dropShadow'></feBlend><feBlend mode='normal' in='SourceGraphic' in2='effect1_dropShadow' result='shape'></feBlend></filter></defs><text x='50%' y='40%' dominant-baseline='middle' text-anchor='middle' fill='#4D4D4D' id='prompt-text'>I love SVG</text></svg></div><svg  class='animate__animated animate__fadeIn' id='one-popup-on-bot' width='25' height='25' viewBox='0 0 22 22' fill='none' xmlns='http://www.w3.org/2000/svg' style='position: fixed;cursor: pointer;right: 34px;bottom: 8.3em;z-index: 99999999999999999999;display: none;'><circle cx='11' cy='11' r='11' fill='#E82D2D'></circle><path d='M7.93018 8.85889V7.1084C8.90674 7.1084 9.58789 6.979 9.97363 6.72021C10.3594 6.46143 10.5522 6.05371 10.5522 5.49707H12.7275V16H10.3765V8.85889H7.93018Z' fill='white'></path></svg>\"""" + ";"
            meta_data += "try{document.body.appendChild(notif_and_cross_div);}catch(err){window.onload = () => {document.body.appendChild(notif_and_cross_div)};}"

            write_file = meta_data + theme3_embed_file.read()
            theme3_embed_file.close()
            file_path = "files/deploy/embed_chatbot_" + bot_id + ".js"

            theme3_embed_file = open(file_path, "w")
            theme3_embed_file.write(write_file)
            theme3_embed_file.close()

            response['file_path'] = file_path
            response['bot_id'] = bot_id
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeployChatBotAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetGeneralDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = DecryptVariable(data["data"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            selected_bot_pk = None
            selected_bot_pk = data['selected_bot_pk']
            selected_language = validation_obj.remo_html_from_string(
                data["selected_language"])
            bot_obj = Bot.objects.get(pk=int(selected_bot_pk))

            emoji_bot_response_obj = EmojiBotResponse.objects.filter(
                bot=bot_obj)
            if not emoji_bot_response_obj.exists():
                emoji_bot_response_obj = EmojiBotResponse.objects.create(
                    bot=bot_obj)
            else:
                emoji_bot_response_obj = emoji_bot_response_obj.first()

            response["stop_words"] = bot_obj.stop_keywords

            if response["stop_words"] == None or len(response["stop_words"]) == 0:
                try:
                    # This variable imported from utils_analytics.py after.
                    # This is the list of stopwords after ignoring words
                    # mentioned in ignore_list in constants.py
                    bot_obj.stop_keywords = stop
                    bot_obj.save()
                    response["stop_words"] = bot_obj.stop_keywords
                except Exception:
                    logger.warning("Could not save stopwords:", extra={
                        'AppName': 'EasyChat', 'bot_id': bot_obj.pk})

            default_order_of_response = json.loads(
                bot_obj.default_order_of_response)
            default_order_of_response_list = []
            for elements in default_order_of_response:
                default_order_of_response_list.append(elements)

            response['default_order_of_response'] = default_order_of_response_list
            response["flow_termination_keywords"] = json.loads(
                bot_obj.flow_termination_keywords)["items"]
            response[
                "flow_termination_bot_response"] = bot_obj.flow_termination_bot_response
            response['flow_termination_confirmation_display_message'] = bot_obj.flow_termination_confirmation_display_message

            response["emoji_angry_response_text"] = emoji_bot_response_obj.emoji_angry_response_text
            response["emoji_happy_response_text"] = emoji_bot_response_obj.emoji_happy_response_text
            response["emoji_neutral_response_text"] = emoji_bot_response_obj.emoji_neutral_response_text
            response["emoji_sad_response_text"] = emoji_bot_response_obj.emoji_sad_response_text

            response["add_livechat_intent"] = emoji_bot_response_obj.add_livechat_intent

            if selected_language != "en" and Language.objects.filter(lang=selected_language):
                lang_obj = Language.objects.get(lang=selected_language)
                lang_bot_obj = LanguageTunedBot.objects.get(
                    bot=bot_obj, language=lang_obj)
                response[
                    "flow_termination_bot_response"] = lang_bot_obj.flow_termination_bot_response
                response['flow_termination_confirmation_display_message'] = lang_bot_obj.flow_termination_confirmation_display_message
                response["emoji_angry_response_text"] = lang_bot_obj.emoji_angry_response_text
                response["emoji_happy_response_text"] = lang_bot_obj.emoji_happy_response_text
                response["emoji_neutral_response_text"] = lang_bot_obj.emoji_neutral_response_text
                response["emoji_sad_response_text"] = lang_bot_obj.emoji_sad_response_text
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetGeneralDetailsAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(selected_bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveEmailConfigurationAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = DecryptVariable(data["data"])
            data = json.loads(data)
            bot_id = data['bot_id']
            email_freq = data["email_freq"]
            email_addr_list = data["email_addr_list"]
            chat_history_list = data["chat_history_list"]
            analytics_list = data["analytics_list"]
            channel_list = data["channel_list"]
            bot_accuracy_threshold = data["bot_accuracy_threshold"]
            email_subject = data["email_subject"]
            email_content = data["email_content"]

            bot_obj = Bot.objects.get(pk=int(bot_id))

            email_config_obj = None
            try:
                email_config_obj = EmailConfiguration.objects.get(bot=bot_obj)
            except Exception:
                email_config_obj = EmailConfiguration.objects.create(
                    bot=bot_obj)

            bot_accuracy_regex = re.compile('^[0-9]$|^[1-9][0-9]$|^(100)$')

            if re.fullmatch(bot_accuracy_regex, bot_accuracy_threshold) == None:
                response["status"] = 400
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            email_config_obj.email_freq = email_freq
            email_config_obj.email_address = json.dumps(email_addr_list)
            email_config_obj.chat_history = json.dumps(chat_history_list)
            email_config_obj.channel = json.dumps(channel_list)
            email_config_obj.analytics = json.dumps(analytics_list)
            email_config_obj.bot_accuracy_threshold = bot_accuracy_threshold
            email_config_obj.subject = email_subject
            email_config_obj.content = email_content
            email_config_obj.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveEmailConfigurationAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveAnalyticsMonitoringSettingAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = DecryptVariable(data["data"])
            data = json.loads(data)

            bot_id = data['bot_id']
            bot_obj = Bot.objects.get(pk=int(bot_id))
            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['message'] = 'You are not authorised to perform this operation.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            consecutive_hours = data["consecutive_hours"]
            email_addr_list = data["email_addr_list"]
            message_limit = data["message_limit"]
            start_hour = data["start_hour"]
            end_hour = data["end_hour"]

            start_hour = datetime.datetime.strptime(start_hour, '%H:%M').time()
            end_hour = datetime.datetime.strptime(end_hour, '%H:%M').time()

            analytics_monitoring_obj = None
            try:
                analytics_monitoring_obj = AnalyticsMonitoring.objects.get(
                    bot=bot_obj)
            except Exception:
                analytics_monitoring_obj = AnalyticsMonitoring.objects.create(
                    bot=bot_obj)

            analytics_monitoring_obj.consecutive_hours = consecutive_hours
            analytics_monitoring_obj.email_addr_list = json.dumps(
                {'items': email_addr_list})
            analytics_monitoring_obj.message_limit = message_limit
            analytics_monitoring_obj.active_hours_start = start_hour
            analytics_monitoring_obj.active_hours_end = end_hour
            analytics_monitoring_obj.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveAnalyticsMonitoringSettingAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SendTestEmailBasedConfigurationAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            profile_id = data['profile_id']

            profile_obj = EasyChatMailerAnalyticsProfile.objects.get(
                pk=int(profile_id))

            status_code = send_test_mail_based_on_config(profile_obj)
            if status_code == 102:
                response["message"] = str(
                    get_developer_console_settings().email_api_failure_message)
                response["status"] = 102
            else:
                response["status"] = 200
                response["message"] = "Success"
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SendTestEmailBasedConfigurationAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveAPIFailEmailConfigAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = DecryptVariable(data["data"])
            data = json.loads(data)

            from_processor = "false"
            try:
                from_processor = data['from_processor']
            except:
                from_processor = "false"

            bot_id = data['bot_id']
            bot_obj = Bot.objects.get(pk=int(bot_id))
            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['message'] = 'You are not authorised to perform this operation.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            mail_sender_time_interval = data["mail_sender_time_interval"]

            try:
                if mail_sender_time_interval.strip() == "" or int(mail_sender_time_interval.strip()) <= 0:
                    response = {}
                    response["status"] = 300
                    response["msg"] = "Kindly enter a valid time interval."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error SaveAPIFailEmailConfigAPI! %s %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
                response = {}
                response["status"] = 300
                response["msg"] = "Kindly enter a valid time interval."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            mail_sent_to_list = data["mail_sent_to_list"]

            if len(mail_sent_to_list):
                response["email_configured"] = True
            else:
                response["email_configured"] = False

            bot_obj.mail_sender_time_interval = mail_sender_time_interval
            bot_obj.mail_sent_to_list = json.dumps(
                {"items": mail_sent_to_list})

            if from_processor == "true":
                bot_obj.is_api_fail_email_notifiication_enabled = True

            bot_obj.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveAPIFailEmailConfigAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveAPIFailEmailConfig = SaveAPIFailEmailConfigAPI.as_view()


class SaveBotFailEmailConfigAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = DecryptVariable(data["data"])
            data = json.loads(data)
            error_detected = False

            validation_obj = EasyChatInputValidation()

            bot_id = data['bot_id']
            bot_obj = Bot.objects.get(pk=int(bot_id))
            bot_info_obj = BotInfo.objects.get(bot=bot_obj)
            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['message'] = 'You are not authorised to perform this operation.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            mail_sender_time_interval = data["mail_sender_time_interval"]

            try:
                if mail_sender_time_interval.strip() == "" or int(mail_sender_time_interval.strip()) < 0:
                    response["status"] = 300
                    response["msg"] = "Kindly enter a valid time interval."

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error SaveAPIFailEmailConfigAPI! %s %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
                response["status"] = 300
                response["msg"] = "Kindly enter a valid time interval."
                error_detected = True

            mail_sent_to_list = data["mail_sent_to_list"]
            for mail in mail_sent_to_list:
                if not validation_obj.is_valid_email(mail):
                    response["msg"] = "Kindly enter a valid email."
                    response["status"] = 300
                    error_detected = True
                    break

            if len(mail_sent_to_list):
                response["email_configured"] = True
            else:
                response["email_configured"] = False
                error_detected = True

            if error_detected:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot_info_obj.bot_break_mail_sender_time_interval = mail_sender_time_interval
            bot_info_obj.bot_break_mail_sent_to_list = json.dumps(
                {"items": mail_sent_to_list})

            bot_info_obj.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveBotFailEmailConfigAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveBotFailEmailConfig = SaveBotFailEmailConfigAPI.as_view()


class SendAPIFailTestEmailAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = DecryptVariable(data["data"])
            data = json.loads(data)

            bot_id = data['bot_id']

            bot_obj = Bot.objects.get(pk=int(bot_id))

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['message'] = 'You are not authorised to perform this operation.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            api_name = "TestAPI"
            api_request_packet = {"url": "https://dummytesting.in"}
            api_response_packet = {"url": "https://dummytesting.in"}
            mail_sent_to_list = json.loads(bot_obj.mail_sent_to_list)["items"]
            new_parameters_list = json.dumps({
                "intent_name": "Test Intent",
                "intent_pk": "45044",
                "tree_name": "Test Tree",
                "tree_id": "87668"
            })

            for item in mail_sent_to_list:
                thread = threading.Thread(target=send_api_fail_mail, args=(api_name, json.dumps(api_request_packet, indent=2), json.dumps(
                    api_response_packet, indent=2), bot_obj, item, new_parameters_list), daemon=True)
                thread.start()
                logger.info("Threading started...", extra={'AppName': 'EasyChat', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SendAPIFailTestEmailAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SendBotBreakFailTestEmailAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = DecryptVariable(data["data"])
            data = json.loads(data)
            bot_id = data['bot_id']

            bot_obj = Bot.objects.get(pk=int(bot_id))

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['message'] = 'You are not authorised to perform this operation.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot_info_obj = BotInfo.objects.get(bot=bot_obj)

            mail_sent_to_list = json.loads(
                bot_info_obj.bot_break_mail_sent_to_list)["items"]

            for item in mail_sent_to_list:
                thread = threading.Thread(target=send_bot_break_mail, args=(
                    item, bot_id, "Web", "https://dummytesting.in"), daemon=True)
                thread.start()
                logger.info("Threading started...", extra={'AppName': 'EasyChat', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SendBotBreakFailTestEmailAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveBotFontAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            bot_id = data['bot_id']

            font = data['font']

            font_size = data['font_size']

            try:
                bot_obj = Bot.objects.get(pk=int(bot_id))
                bot_obj.font = font
                bot_obj.font_size = font_size
                bot_obj.save()
                response['status'] = 200
            except Exception:
                logger.info("SaveBotFontAPI: bot_id: %s does not exist : %s", str(
                    bot_id), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveNewPasswordAPI %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SsoMetaFileFunctionality(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['data'])

            data = DecryptVariable(data)

            data = json.loads(data)

            sso_metadata = data['sso_metadata']

            util_path = os.path.join(BASE_DIR)

            ldap_conf_file_name = util_path + '/google-ldap.conf'

            ldap_conf_file = open(ldap_conf_file_name, 'w')

            ldap_conf_file.write(sso_metadata)
            ldap_conf_file.close()

            response['status'] = 200
            response['status_message'] = "Success"

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveSsoMeta %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)

    def get(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            ldap_content_file_path = EASYCHAT_ROOT + 'ldap.conf'
            ldap_content_file = open(ldap_content_file_path, 'r')

            if "HTTP_HOST" in request.META:
                ldap_content = ldap_content_file.read().replace(
                    "allincall.in", request.META["HTTP_HOST"])
            else:
                ldap_content = ldap_content_file.read()
            ldap_content_file.close()

            ldap_file_to_download = open(
                settings.MEDIA_ROOT + 'private/ldap.conf', 'w')

            ldap_file_to_download.write(ldap_content)

            ldap_file_to_download.close()
            path_to_file = settings.MEDIA_ROOT + 'private/ldap.conf'
            response = FileResponse(open(path_to_file, 'rb'))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="ldap.conf"'
            response['Content-Length'] = os.path.getsize(path_to_file)
            os.remove(settings.MEDIA_ROOT + 'private/ldap.conf')
            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveSsoMeta %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return response


class SaveStopWordsAPI (APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            json_string = DecryptVariable(request.data["json_string"])
            data = json.loads(json_string)
            bot_id = data['bot_id']
            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['message'] = 'You are not authorised to perform this operation.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot_stop_keywords = data["bot_stop_keywords"]

            bot_obj.stop_keywords = json.dumps(bot_stop_keywords)

            bot_obj.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveStopWordsAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveCSATFeedbackAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            input_value = data["input_value"]
            feedback_options_inputs = data["feedback_options_inputs"]
            collect_phone_number = data["collect_phone_number"]
            collect_email_id = data["collect_email_id"]
            mark_all_fields_mandatory = data["mark_all_fields_mandatory"]
            bot_pk = data["bot_id"]
            bot_obj = Bot.objects.get(pk=int(bot_pk))

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = 'You are not authorised to perform this operation.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            csat_feedback_obj = CSATFeedBackDetails.objects.filter(
                bot_obj__pk=bot_pk)
            if csat_feedback_obj:
                csat_feedback_obj = csat_feedback_obj[0]
                csat_feedback_obj.number_of_feedbacks = int(input_value)
                csat_feedback_obj.all_feedbacks = feedback_options_inputs
                csat_feedback_obj.collect_phone_number = collect_phone_number
                csat_feedback_obj.collect_email_id = collect_email_id
                csat_feedback_obj.mark_all_fields_mandatory = mark_all_fields_mandatory
                csat_feedback_obj.save()
            else:
                CSATFeedBackDetails.objects.create(number_of_feedbacks=int(input_value), all_feedbacks=feedback_options_inputs,
                                                   collect_phone_number=collect_phone_number, collect_email_id=collect_email_id, mark_all_fields_mandatory=mark_all_fields_mandatory, bot_obj=Bot.objects.get(pk=bot_pk))

            response["status"] = 200
            response["message"] = "CSAT Feedback successfully saved."
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveBotAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveBotFont = SaveBotFontAPI.as_view()

SendAPIFailTestEmail = SendAPIFailTestEmailAPI.as_view()

SendBotBreakFailTestEmail = SendBotBreakFailTestEmailAPI.as_view()

SaveAnalyticsMonitoringSetting = SaveAnalyticsMonitoringSettingAPI.as_view()

GetGeneralDetails = GetGeneralDetailsAPI.as_view()

SendTestEmailBasedConfiguration = SendTestEmailBasedConfigurationAPI.as_view()

GetGeneralDetails = GetGeneralDetailsAPI.as_view()

SaveEmailConfiguration = SaveEmailConfigurationAPI.as_view()

# MoveBotToProduction = MoveBotToProductionAPI.as_view()

ChangeBotThemeColor = ChangeBotThemeColorAPI.as_view()

SubmitBotAdvanceSettings = SubmitBotAdvanceSettingsAPI.as_view()

GetBotMessageImage = GetBotMessageImageAPI.as_view()

GetBotImage = GetBotImageAPI.as_view()

SaveBot = SaveBotAPI.as_view()

SaveMultilingualBot = SaveMultilingualBotAPI.as_view()

DeleteBot = DeleteBotAPI.as_view()

DeleteBotImage = DeleteBotImageAPI.as_view()

BotsLists = BotsListsAPI.as_view()

ImportBot = ImportBotAPI.as_view()

DeployChatBot = DeployChatBotAPI.as_view()

SsoMetaFileFunctionality = SsoMetaFileFunctionality.as_view()

SaveStopWords = SaveStopWordsAPI.as_view()

SaveCSATFeedback = SaveCSATFeedbackAPI.as_view()


class GetLanguageTemplateAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            selected_language = data["selected_language"]
            selected_language = validation_obj.remo_html_from_string(
                selected_language)

            bot_obj = Bot.objects.get(pk=int(bot_id))
            language_obj = Language.objects.get(lang=selected_language)
            language_template_obj = RequiredBotTemplate.objects.get(
                bot=bot_obj, language=language_obj)
            bot_channel_dict = {}
            bot_channel_dict["bot_inactivity_msg"] = bot_obj.bot_inactivity_response
            bot_channel_dict[
                "bot_response_delay_message"] = bot_obj.bot_response_delay_message

            language_script_type = language_obj.language_script_type

            bot_inactivity_msg, bot_response_delay_message = get_fine_tuned_bot_inactivity_and_delay_response(
                bot_channel_dict, bot_obj, selected_language, Language, EasyChatTranslationCache)

            days_list = ["Monday", "Tueday", "Wednesday",
                         "Thursday", "Friday", "Saturday", "Sunday"]
            language_days_list = []

            for day in days_list:
                language_days_list.append(get_translated_text_with_api_status(
                    day, selected_language, EasyChatTranslationCache, True)[0])

            months_list = ["Jan", "Feb", "Mar", "Apr", "May",
                           "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            language_months_list = []

            for month in months_list:
                language_months_list.append(get_translated_text_with_api_status(
                    month, selected_language, EasyChatTranslationCache, True)[0])

            response["bot_name"] = language_template_obj.bot_name
            response["placeholder"] = language_template_obj.placeholder
            response["widgets_placeholder_text"] = language_template_obj.widgets_placeholder_text
            response["close_button_tooltip"] = language_template_obj.close_button_tooltip
            response["minimize_button_tooltip"] = language_template_obj.minimize_button_tooltip
            response["home_button_tooltip"] = language_template_obj.home_button_tooltip
            response["mic_button_tooltip"] = language_template_obj.mic_button_tooltip
            response["typing_text"] = language_template_obj.typing_text
            response["send_text"] = language_template_obj.send_text
            response["cards_text"] = language_template_obj.cards_text
            response["go_back_text"] = language_template_obj.go_back_text
            response["back_text"] = language_template_obj.back_text
            response["menu_text"] = language_template_obj.menu_text
            response["search_text"] = language_template_obj.search_text
            response["dropdown_text"] = language_template_obj.dropdown_text
            response["start_text"] = language_template_obj.start_text
            response["stop_text"] = language_template_obj.stop_text
            response["submit_text"] = language_template_obj.submit_text
            response["uploading_video_text"] = language_template_obj.uploading_video_text
            response["cancel_text"] = language_template_obj.cancel_text
            response["file_size_limit_text"] = language_template_obj.file_size_limit_text
            response["file_attachment_text"] = language_template_obj.file_attachment_text
            response["feedback_text"] = language_template_obj.feedback_text
            response["positive_feedback_options_text"] = language_template_obj.positive_feedback_options_text
            response["negative_feedback_options_text"] = language_template_obj.negative_feedback_options_text
            response["feedback_error_text"] = language_template_obj.feedback_error_text
            response["success_feedback_text"] = language_template_obj.success_feedback_text
            response["csat_form_error_mobile_email_text"] = language_template_obj.csat_form_error_mobile_email_text
            response["csat_form_text"] = language_template_obj.csat_form_text
            response["date_range_picker_text"] = language_template_obj.date_range_picker_text
            response["csat_emoji_text"] = language_template_obj.csat_emoji_text
            response["invalid_session_id_response"] = language_template_obj.get_invalid_session_id_text_response()
            response["form_widget_text"] = language_template_obj.form_widget_text
            response["range_slider_error_messages"] = language_template_obj.range_slider_error_messages
            response["general_text"] = language_template_obj.general_text
            response["minimize_text"] = language_template_obj.minimize_text
            response["maximize_text"] = language_template_obj.maximize_text
            response["mute_text"] = language_template_obj.mute_tooltip_text
            response["unmute_text"] = language_template_obj.unmute_tooltip_text
            response["no_result_found"] = language_template_obj.no_result_found_text
            response["form_widget_error_text"] = language_template_obj.form_widget_error_text
            response["widgets_response_text"] = language_template_obj.widgets_response_text
            response["greeting_and_welcome_text"] = language_template_obj.greeting_and_welcome_text
            response["choose_language"] = language_template_obj.choose_language
            response["end_chat"] = language_template_obj.end_chat
            response["bot_inactivity_msg"] = bot_inactivity_msg
            response["bot_response_delay_message"] = bot_response_delay_message
            response["livechat_form_text"] = language_template_obj.livechat_form_text
            response["livechat_system_notifications"] = language_template_obj.livechat_system_notifications
            response["livechat_feedback_text"] = language_template_obj.livechat_feedback_text
            response["livechat_validation_text"] = language_template_obj.livechat_validation_text
            response["livechat_voicecall_notifications"] = language_template_obj.livechat_voicecall_notifications
            response["livechat_vc_notifications"] = language_template_obj.livechat_vc_notifications
            response["attachment_tooltip_text"] = language_template_obj.attachment_tooltip_text
            response["powered_by_text"] = language_template_obj.powered_by_text
            response['cb_text'] = language_template_obj.livechat_cb_notifications
            response['do_not_disturb_text'] = language_template_obj.do_not_disturb_text
            response['pdf_view_document_text'] = language_template_obj.pdf_view_document_text
            response["language_script_type"] = language_script_type
            response["language_days_list"] = language_days_list
            response["language_months_list"] = language_months_list
            response['invalid_number_text'] = language_template_obj.invalid_number_text
            response['invalid_country_code'] = language_template_obj.invalid_country_code
            response['phone_number_too_short_text'] = language_template_obj.phone_number_too_short_text
            response['phone_number_too_long_text'] = language_template_obj.phone_number_too_long_text
            response['frequently_asked_questions_text'] = language_template_obj.frequently_asked_questions_text
            response["chat_with_text"] = language_template_obj.chat_with_text
            response["query_api_failure_text"] = language_template_obj.query_api_failure_text
            response["livechat_transcript_text"] = language_template_obj.livechat_transcript_text
            response["livechat_system_notifications_ios"] = language_template_obj.livechat_system_notifications_ios

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLanguageTemplateAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLanguageTemplate = GetLanguageTemplateAPI.as_view()


class GetLanguageUpdatedBotItemsAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            selected_language = data["selected_language"]
            selected_language = validation_obj.remo_html_from_string(
                selected_language)
            channel_name = data["channel_name"]
            channel_name = validation_obj.remo_html_from_string(channel_name)

            bot_obj = Bot.objects.get(pk=int(bot_id))
            channel_obj = Channel.objects.filter(name=channel_name).first()
            bot_channel = BotChannel.objects.filter(
                bot=bot_obj, channel=channel_obj).first()
            welcome_message = bot_channel.welcome_message

            sticky_intents = json.loads(bot_channel.sticky_intent)
            sticky_intent_list = get_message_list_with_pk(
                sticky_intents["items"], channel_obj=channel_obj)
            sticky_intents_menu = json.loads(bot_channel.sticky_intent_menu)
            sticky_intent_list_menu = get_message_list_and_icon_name(
                sticky_intents_menu["items"], Intent)

            csat_obj = CSATFeedBackDetails.objects.filter(bot_obj=bot_obj)
            csat_required_checkboxes = []

            if csat_obj:
                csat_obj = csat_obj[0]
                csat_required_checkboxes = json.loads(
                    csat_obj.all_feedbacks)

            translated_sticky_intents_list = sticky_intent_list
            translated_sticky_intents_list_menu = sticky_intent_list_menu

            if selected_language != "en":
                translated_csat_required_checkboxes = []

                for text_data in csat_required_checkboxes:
                    translated_csat_required_checkboxes.append(get_translated_text(
                        text_data, selected_language, EasyChatTranslationCache))

                csat_required_checkboxes = translated_csat_required_checkboxes

                translated_sticky_intents_list = []

                for sticky_intent in sticky_intent_list:
                    translated_sticky_intents_list.append(get_translated_text(
                        sticky_intent, selected_language, EasyChatTranslationCache))

                translated_sticky_intents_list_menu = []

                for sticky_intent in sticky_intent_list_menu:
                    sticky_intents_temp = []
                    sticky_intents_temp.append(get_translated_text(
                        sticky_intent[0], selected_language, EasyChatTranslationCache))
                    sticky_intents_temp.append(sticky_intent[1])
                    translated_sticky_intents_list_menu.append(
                        sticky_intents_temp)

                language_obj = Language.objects.filter(
                    lang=selected_language).first()

                language_tunned_bot_channel = LanguageTunedBotChannel.objects.filter(
                    bot_channel=bot_channel, language=language_obj).first()

                if language_tunned_bot_channel:
                    welcome_message = language_tunned_bot_channel.welcome_message
                else:
                    welcome_message = get_translated_text(
                        welcome_message, selected_language, EasyChatTranslationCache)

            response["sticky_intents_list"] = translated_sticky_intents_list
            response["sticky_intents_list_menu"] = translated_sticky_intents_list_menu
            response["csat_required_checkboxes"] = csat_required_checkboxes
            response[
                "sticky_button_display_format"] = bot_channel.sticky_button_display_format

            response["welcome_message"] = welcome_message
            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLanguageTemplateAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLanguageUpdatedBotItems = GetLanguageUpdatedBotItemsAPI.as_view()


class GetLanguageUpdatedFormAssistDetailsAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            selected_language = data["selected_language"]
            selected_language = validation_obj.remo_html_from_string(
                selected_language)

            bot_obj = Bot.objects.get(pk=int(bot_id))
            is_form_assist_enabled = bot_obj.is_form_assist_enabled

            if is_form_assist_enabled:

                form_assist_obj = FormAssistBotData.objects.filter(bot=bot_obj)

                if form_assist_obj.exists():
                    form_assist_obj = form_assist_obj[0]
                    response["form_assist_auto_pop_text"] = get_multilingual_form_assist_auto_popup_response(
                        bot_obj, form_assist_obj, selected_language, Language, LanguageTunedBot, EasyChatTranslationCache)

                    selected_form_assist_intents = dict(
                        form_assist_obj.form_assist_intent_bubble.all().values_list('pk', 'name'))

                    form_assist_tag_intents = dict(FormAssist.objects.filter(
                        bot=bot_obj).values_list('intent__pk', 'intent__name'))

                    form_assist_intent_bubble = selected_form_assist_intents | form_assist_tag_intents

                    response["form_assist_intent_bubble"] = json.dumps(get_translated_text(
                        form_assist_intent_bubble, selected_language, EasyChatTranslationCache))

                    form_assist_intent_responses = FormAssist.objects.filter(
                        bot=bot_obj).values_list('pk', 'intent__tree__response__sentence')

                    form_assist_intent_responses_dict = {}

                    for form_assist_intent_response in form_assist_intent_responses:
                        form_assist_intent_responses_dict[form_assist_intent_response[0]] = (
                            json.loads(form_assist_intent_response[1]))['items'][0]['speech_response']

                    response["form_assist_intent_responses_dict"] = json.dumps(get_translated_text(
                        form_assist_intent_responses_dict, selected_language, EasyChatTranslationCache))

            response[
                "is_form_assist_auto_pop_allowed"] = is_form_assist_enabled

            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetLanguageTemplateAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetLanguageUpdatedFormAssistDetails = GetLanguageUpdatedFormAssistDetailsAPI.as_view()


class UpdateNeedToBuildBotAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)

            bot_obj = Bot.objects.get(pk=int(bot_id))
            bot_obj.need_to_build = False
            bot_obj.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateNeedToBuildBotAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateNeedToBuildBot = UpdateNeedToBuildBotAPI.as_view()


class BuildBotAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)

            bot_obj = Bot.objects.get(pk=int(bot_id))

            bot_obj.need_to_build = False
            bot_obj.save()

            event_obj = EventProgress.objects.create(
                user=request.user,
                bot=bot_obj,
                event_type='build_bot',
            )

            build_bot_thread = threading.Thread(
                target=build_bot, args=(bot_obj, event_obj))
            build_bot_thread.daemon = True
            build_bot_thread.start()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("BuildBotAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


BuildBot = BuildBotAPI.as_view()


class SaveMailerProfileAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response['message'] = 'Some error occured. Please try again later.'
        try:
            data = request.data
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data['bot_id']
            bot_obj = Bot.objects.get(pk=int(bot_id))
            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['message'] = 'You are not authorised to perform this operation.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            profile_name = data['profile_name'].strip()
            profile_name = validation_obj.remo_html_from_string(profile_name)
            profile_name = validation_obj.remo_unwanted_characters_from_message(
                profile_name, bot_id)

            email_frequency = data['email_frequency']

            email_subject = data['email_subject']
            email_subject = validation_obj.remo_html_from_string(email_subject)
            email_subject = validation_obj.remo_unwanted_characters_from_message(
                email_subject, bot_id)

            if email_subject == "":
                email_subject = DEFAULT_MAIL_SUBJECT

            if profile_name == "" or not validation_obj.is_alphanumeric(profile_name):
                response["status"] = 400
                response["message"] = "Please enter a valid profile name."

            if len(profile_name) > CHARACTER_LIMIT_SMALL_TEXT:
                response["status"] = 400
                response["message"] = "Profile Name is exceeding character limit of " + \
                    str(CHARACTER_LIMIT_SMALL_TEXT) + " characters."

            if len(email_subject) > CHARACTER_LIMIT_MEDIUM_TEXT:
                response["status"] = 400
                response["message"] = "Email Subject is exceeding character limit of " + \
                    str(CHARACTER_LIMIT_MEDIUM_TEXT) + " characters."

            if response['status'] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            emails = data['emails']
            bot_accuracy = data['bot_accuracy']
            table_params = json.loads(data['table_params'])
            graph_params = json.loads(data['graph_params'])
            attachment_params = json.loads(data['attachment_params'])

            if len(emails) == 0:
                response["status"] = 400
                response["message"] = "Please enter at least one email address."

            if 'profile_id' in data:
                profile_id = data['profile_id']
            else:
                profile_id = ''

            profile_obj = EasyChatMailerAnalyticsProfile.objects.filter(
                name__iexact=profile_name, bot=bot_obj, is_deleted=False)

            if profile_obj and profile_id == '':
                response['message'] = 'A Profile with this name already exists. Please try different profile name.'
            else:
                if profile_id == '':
                    profile_obj = EasyChatMailerAnalyticsProfile.objects.create(name=profile_name, bot=bot_obj, email_frequency=json.dumps(
                        email_frequency), email_address=json.dumps(emails), email_subject=email_subject, bot_accuracy_threshold=bot_accuracy)

                    profile_obj.is_table_enabled = table_params['is_table_enabled']
                    profile_obj.is_graph_enabled = graph_params['is_graph_enabled']
                    profile_obj.is_attachment_enabled = attachment_params['is_attachment_enabled']

                    if table_params['is_table_enabled']:
                        table_obj = create_mailer_table_object(
                            profile_obj, table_params, EasyChatMailerTableParameters)
                        profile_obj.table_parameters = table_obj

                    if graph_params['is_graph_enabled']:
                        graph_obj = create_mailer_graph_object(
                            profile_obj, graph_params, EasyChatMailerGraphParameters)
                        profile_obj.graph_parameters = graph_obj

                    if attachment_params['is_attachment_enabled']:
                        attachment_obj = EasyChatMailerAttachmentParameters.objects.create(
                            profile=profile_obj, attachments=json.dumps(attachment_params['attachments']))
                        profile_obj.attachment_parameters = attachment_obj

                else:
                    profile_obj = EasyChatMailerAnalyticsProfile.objects.get(
                        pk=int(profile_id))
                    profile_obj.name = profile_name
                    profile_obj.email_frequency = json.dumps(email_frequency)
                    profile_obj.email_address = json.dumps(emails)
                    profile_obj.email_subject = email_subject
                    profile_obj.bot_accuracy_threshold = bot_accuracy
                    profile_obj.is_table_enabled = table_params['is_table_enabled']
                    profile_obj.is_graph_enabled = graph_params['is_graph_enabled']
                    profile_obj.is_attachment_enabled = attachment_params['is_attachment_enabled']

                    if table_params['is_table_enabled']:
                        table_obj = profile_obj.table_parameters

                        if table_obj:
                            table_obj.count_variation = json.dumps(
                                table_params['count_variation'])
                            table_obj.channels = json.dumps(
                                table_params['channels'])
                            table_obj.message_analytics = json.dumps(
                                table_params['message_analytics'])
                            table_obj.session_analytics = json.dumps(
                                table_params['session_analytics'])
                            table_obj.user_analytics = json.dumps(
                                table_params['user_analytics'])
                            table_obj.livechat_analytics = json.dumps(
                                table_params['livechat_analytics'])
                            table_obj.flow_completion = json.dumps(
                                table_params['flow_analytics'])
                            table_obj.intent_analytics = json.dumps(
                                table_params['intent_analytics'])
                            table_obj.traffic_analytics = json.dumps(
                                table_params['traffic_analytics'])
                            table_obj.language_analytics = json.dumps(
                                table_params['language_analytics'])
                            if table_params['language_analytics']:
                                table_obj.language_query_analytics = json.dumps(
                                    table_params['language_query_analytics'])
                            else:
                                table_obj.language_query_analytics = '[]'

                            table_obj.save()
                        else:
                            table_obj = create_mailer_table_object(
                                profile_obj, table_params, EasyChatMailerTableParameters)
                            profile_obj.table_parameters = table_obj

                    if graph_params['is_graph_enabled']:
                        graph_obj = profile_obj.graph_parameters

                        if graph_obj:
                            graph_obj.graph_parameters = json.dumps(
                                graph_params['graph_parameters'])
                            graph_obj.message_analytics_graph = json.dumps(
                                graph_params['message_analytics_graph'])
                            graph_obj.save()
                        else:
                            graph_obj = create_mailer_graph_object(
                                profile_obj, graph_params, EasyChatMailerGraphParameters)
                            profile_obj.graph_parameters = graph_obj

                    if attachment_params['is_attachment_enabled']:
                        attachment_obj = profile_obj.attachment_parameters

                        if attachment_obj:
                            attachment_obj.attachments = json.dumps(
                                attachment_params['attachments'])
                            attachment_obj.save()
                        else:
                            attachment_obj = EasyChatMailerAttachmentParameters.objects.create(
                                profile=profile_obj, attachments=json.dumps(attachment_params['attachments']))
                            profile_obj.attachment_parameters = attachment_obj

                profile_obj.save()
                bot_obj.is_email_notifiication_enabled = True
                bot_obj.save()

                response["status"] = 200
                response['message'] = 'success'
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveMailerProfileAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveMailerProfile = SaveMailerProfileAPI.as_view()


class DeleteMailerProfileAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response['message'] = 'Some error occured. Please try again later.'
        try:
            data = request.data
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)

            profile_id = data['profile_id']

            profile_obj = EasyChatMailerAnalyticsProfile.objects.filter(
                pk=int(profile_id))

            if profile_obj:
                profile_obj[0].is_deleted = True
                profile_obj[0].save()

                response["status"] = 200
                response['message'] = 'success'
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteMailerProfileAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DeleteMailerProfile = DeleteMailerProfileAPI.as_view()


class ImportMultilingualIntentsFromExcelAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = request.data
            uploaded_file = data["input_file"]
            data = json.loads(data["data"])

            validation_obj = EasyChatInputValidation()

            bot_id = validation_obj.remo_html_from_string(data["bot_id"])
            bot_id = int(bot_id)

            bot_obj = Bot.objects.get(pk=int(bot_id))

            file_validation_obj = EasyChatFileValidation()

            if file_validation_obj.check_malicious_file(uploaded_file.name):
                response["status"] = 101
                response["message"] = "Kindly upload file in xls or xlsx format."
                return Response(data=response)

            file_name = get_dot_replaced_file_name(uploaded_file.name)
            path = default_storage.save(
                file_name, ContentFile(uploaded_file.read()))
            ext = path.split(".")[-1]
            if ext.lower() not in ["xls", "xlsx"]:
                response["status"] = 101
                response["message"] = "Kindly upload file in xls or xlsx format."
                return Response(data=response)

            file_path = settings.MEDIA_ROOT + path

            event_obj = EventProgress.objects.create(
                user=request.user,
                bot=bot_obj,
                event_type='import_bot',
                event_info=json.dumps({'file_uploaded': uploaded_file.name})
            )

            import_bot_thread = threading.Thread(
                target=add_multilingual_intents_into_bot_from_excel, args=(file_path, bot_id, event_obj))
            import_bot_thread.daemon = True
            import_bot_thread.start()

            response['status'] = 200
            response['message'] = 'success'

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ImportMultilingualIntentsFromExcelAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response = build_error_response(
                "There are some internal issues. Please try again later.")

        return Response(data=response)


ImportMultilingualIntentsFromExcel = ImportMultilingualIntentsFromExcelAPI.as_view()


class SaveBubbleClickInfoAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id).strip()
            bubble_name = data["bubble_name"]
            bubble_name = validation_obj.remo_html_from_string(
                bubble_name).strip()
            selected_language = validation_obj.remo_html_from_string(
                data["selected_language"])
            language_obj = Language.objects.filter(
                lang=selected_language).first()

            bot_obj = Bot.objects.get(pk=bot_id)

            AutoPopUpClickInfo.objects.create(
                name=bubble_name, bot=bot_obj, selected_language=language_obj)

            response["status"] = 200
            response["message"] = "Success"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveBubbleClickInfoAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return Response(data=response)


SaveBubbleClickInfo = SaveBubbleClickInfoAPI.as_view()


class GetBotManagerAccessDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)

            manager_id = data["manager_id"]
            manager_id = validation_obj.remo_html_from_string(manager_id)

            bot_obj = Bot.objects.get(pk=bot_id)

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response["message"] = "You are not authorised to perform this operation."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            manager_obj = User.objects.get(pk=manager_id)

            access_management_obj = AccessManagement.objects.get(
                user=manager_obj, bot=bot_obj)

            access_type = "custom_access"
            custom_access_type = []

            custom_access_objs = access_management_obj.access_type.all()
            for custom_access_obj in custom_access_objs:
                if custom_access_obj.value == "full_access":
                    access_type = "full_access"
                    custom_access_type = []
                    break
                else:
                    custom_access_type.append(custom_access_obj.value)

            is_livechat_supervisor_access = "false"
            if bot_obj.is_livechat_enabled:
                livechat_user_obj = LiveChatUser.objects.filter(
                    user=manager_obj, status="2", bots__in=[bot_obj])
                if livechat_user_obj.count():
                    is_livechat_supervisor_access = "true"

            is_tms_supervisor_access = "false"
            if bot_obj.is_tms_allowed:
                tms_user_obj = Agent.objects.filter(
                    user=manager_obj, role="supervisor", bots__in=[bot_obj])
                if tms_user_obj.count():
                    is_tms_supervisor_access = "true"

            response["access_type"] = access_type
            response["custom_access_type"] = custom_access_type
            response["is_tms_supervisor_access"] = is_tms_supervisor_access
            response["is_livechat_supervisor_access"] = is_livechat_supervisor_access
            response["bot_id"] = bot_id
            response["message"] = "Success"
            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetBotManagerAccessDetailsAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetBotManagerAccessDetails = GetBotManagerAccessDetailsAPI.as_view()


class ExportLargeBotAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)

            export_type = data["export_type"]
            export_type = validation_obj.remo_html_from_string(export_type)

            email_id = data["email_id"]
            email_id = validation_obj.remo_html_from_string(email_id)

            bot_obj = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot_obj or request.user not in bot_obj.users.all():
                response["message"] = "You are not authorised to perform this operation."
                response["status"] = 401

            export_bot_thread = threading.Thread(
                target=export_large_bot, args=(bot_obj, email_id, export_type, None))

            export_bot_thread.daemon = True
            export_bot_thread.start()

            response["message"] = "Success"
            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportLargeBotAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ExportLargeBot = ExportLargeBotAPI.as_view()
