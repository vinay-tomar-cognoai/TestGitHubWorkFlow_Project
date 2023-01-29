from googletrans import Translator
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication  # noqa F401
from django.contrib.sessions.models import Session

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.utils.encoding import smart_str
# from django.utils.safestring import mark_safe

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import HttpResponseNotFound
from CampaignApp.models import CampaignBotWSPConfig, CampaignWhatsAppServiceProvider
from CampaignApp.utils_aws_sqs import send_delivery_packet_to_sqs

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_alexa_query import build_alexa_response
from EasyChatApp.utils_google_home_query import build_google_home_response
from EasyChatApp.utils_faq import *
from EasyChatApp.constants import *

from EasyAssistApp.utils import get_active_agent_obj, easyassist_check_for_admin_expired_credentials, easyassist_is_active_user
from EasyAssistApp.utils import save_audit_trail as save_audit_trail_easyassist
from EasyChatApp.utils_validation import EasyChatInputValidation, EasyChatFileValidation
from EasyChatApp.utils_general_feedback import *
from EasyChatApp.utils_self_learning import *
from EasyChatApp.utils_automated_testing import perform_automated_testing, delete_test_result_objs_till_now, get_parsed_automated_test_result_data, \
    get_total_intent_sentence_based_on_percentage, return_single_sentence_test_details, create_and_send_automated_testing_report_mail
from DeveloperConsoleApp.utils import get_developer_console_settings

from EasyChatApp.views_wordmapper import *
from EasyChatApp.views_upload import *
from EasyChatApp.views_tree import *
from EasyChatApp.views_intent import *
from EasyChatApp.views_channels import *
from EasyChatApp.views_bot import *
from EasyChatApp.views_analytics import *
from EasyChatApp.views_test import *
from EasyChatApp.views_formassist import *
from EasyChatApp.views_servicerequest import *
from EasyChatApp.views_editstatic import *
from EasyChatApp.views_lead_generation import *
from EasyChatApp.captcha_key import *
from EasyChatApp.views_category import *
from EasyChatApp.views_paraphrase import *
from EasyChatApp.views_facebook import *
from EasyChatApp.views_instagram import *
from EasyChatApp.views_microsoft import *
from EasyChatApp.views_twitter import *
from EasyChatApp.views_api_integration import *
from EasyChatApp.views_android import *
from EasyChatApp.telegram.utils_telegram import *
from EasyChatApp.views_pdf_searcher import *
from EasyChatApp.utils_google_buisness_messages import *
from EasyChatApp.utils_bot_usage_analytics import *
from EasyChatApp.email_html_constants import *
from EasyChatApp.utils_bot import get_translated_text, process_response_based_on_language
from EasyChatApp.utils_userflow import create_bot_with_questions_variations_answers
from EasyChatApp.constants_self_learning import *
from EasyChatApp.views_voip import *
from EasyChatApp.views_rcs import *
from EasyChatApp.views_fusion_editor import *

from LiveChatApp.utils import save_audit_trail_data, get_cobrowsing_request_text, send_event_for_agent_not_ready, send_event_for_report_creation
from EasyTMSApp.models import TicketCategory, Agent
from LiveChatApp.models import LiveChatCobrowsingData, LiveChatSessionManagement, LiveChatUser, LiveChatMISDashboard, LiveChatGuestAgentAudit

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.feature_extraction import text as sklearn_text
from django.core.files.storage import FileSystemStorage
from EasyChat.settings import BASE_DIR, EASYCHAT_HOST_URL
from dateutil import tz
from rest_framework.decorators import permission_classes

import json
import datetime
import xlrd
import logging
import uuid
import threading
import re
import sys
import time
import mimetypes
import random
import hashlib
import pytz
import urllib

from queue import Queue
from xlwt import Workbook
from PIL import Image
from oauth2client.service_account import ServiceAccountCredentials
from django.views.decorators.http import require_POST

from businessmessages import businessmessages_v1_client as bm_client
from businessmessages.businessmessages_v1_messages import (
    BusinessMessagesCarouselCard, BusinessMessagesCardContent, BusinessMessagesContentInfo,
    BusinessMessagesDialAction, BusinessmessagesConversationsMessagesCreateRequest,
    BusinessMessagesOpenUrlAction, BusinessMessagesMedia, BusinessMessagesMessage,
    BusinessMessagesRichCard, BusinessMessagesStandaloneCard,
    BusinessMessagesSuggestion, BusinessMessagesSuggestedAction, BusinessMessagesSuggestedReply,
    BusinessMessagesRepresentative, BusinessMessagesImage)


livechat_queue = Queue()

google_translator = Translator()

logger = logging.getLogger(__name__)

ensure_element_tree(xlrd)


def GetAMP(request):
    return render(request, 'EasyChatApp/amp.html')


def TestData(request):
    return render(request, 'EasyChatApp/platform/testdata.html')


def TestExternalFunction(request):
    return render(request, 'EasyChatApp/test_external_function.html')


def AgentIframe(request):  # noqa: N802
    validation_obj = EasyChatInputValidation()

    user_id = request.GET["user_id"]
    user_id = validation_obj.remo_html_from_string(user_id)

    livechat_session = LiveChatSession.objects.get(
        profile=Profile.objects.get(user_id=user_id), is_active=True)
    message_history = json.loads(livechat_session.message_history)
    message_history = message_history['message_history']

    return render(request, 'EasyChatApp/agent_chatbox.html', {
        "user_id": user_id,
        "message_history": message_history
    })


@xframe_options_exempt
def EasyChatPage(request):  # noqa: N802
    try:
        if request.method == "GET":
            validation_obj = EasyChatInputValidation()
            bot_id = request.GET["id"]
            bot_id = validation_obj.remo_html_from_string(str(bot_id))
            try:
                channel = request.GET["channel"]
            except:
                channel = "Web"
            is_webview_link = False
            try:
                webview_link = request.GET["is_webview_link"]
                webview_link = validation_obj.remo_html_from_string(
                    webview_link)
                if request.GET["is_webview_link"] == "true":
                    is_webview_link = True
            except:
                pass
            
            selected_language = "en"
            if "selected_language" in request.GET:
                selected_language = request.GET["selected_language"]
                selected_language = validation_obj.remo_html_from_string(
                    selected_language)

            language_obj = Language.objects.get(lang=selected_language)
            language_script_type = language_obj.language_script_type

            bot_obj = Bot.objects.get(
                pk=int(bot_id), is_uat=True, is_deleted=False)

            if bot_obj.is_custom_js_required:
                create_custom_js_file(bot_id)

            if bot_obj.is_custom_css_required:
                create_custom_css_file(bot_id, bot_obj.default_theme.name)

            channel_obj = Channel.objects.filter(name=channel).first()
            bot_channel_obj = BotChannel.objects.filter(channel=channel_obj, bot=bot_obj).first()
            chat_page = settings.EASYCHAT_DEFAULT_CHAT_PAGE
            is_nps_required = False
            nps_obj = NPS.objects.filter(bot=bot_obj, channel__name=channel)
            csat_required_checkboxes = []
            collect_phone_number = False
            collect_email_id = False
            mark_all_fields_mandatory = False
            csat_obj = CSATFeedBackDetails.objects.filter(bot_obj=bot_obj)
            mandatory_text = "Mandatory"
            if nps_obj:
                is_nps_required = True
                if csat_obj:
                    csat_obj = csat_obj[0]
                    csat_required_checkboxes = json.loads(
                        csat_obj.all_feedbacks)
                    csat_required_checkboxes.append("Other")
                    # If language is not english(default)
                    if selected_language != "en":
                        translated_csat_required_checkboxes = []
                        for text_data in csat_required_checkboxes:
                            translated_csat_required_checkboxes.append(get_translated_text(
                                text_data, selected_language, EasyChatTranslationCache))
                        csat_required_checkboxes = translated_csat_required_checkboxes
                        mandatory_text = get_translated_text(
                            mandatory_text, selected_language, EasyChatTranslationCache)
                    collect_phone_number = csat_obj.collect_phone_number
                    collect_email_id = csat_obj.collect_email_id
                    mark_all_fields_mandatory = csat_obj.mark_all_fields_mandatory

            bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()
            # voip info
            is_voip_from_customer_end_enabled = False
            voip_type = 'none'
            # suggestion related data 
            chunk_of_suggestion = ChunksOfSuggestions.objects.filter(bot=bot_obj)
            total_no_chunks = chunk_of_suggestion.count()
            suggestion_chunk_limit_and_total_no_chunks = str(CHUNK_OF_SUGGESTION_LIMIT) + "-" + str(total_no_chunks)
            meeting_domain = "meet-uat.allincall.in"
            is_transcript_enabled = False
            try:
                config_obj = LiveChatConfig.objects.get(bot=bot_obj)
                meeting_domain = config_obj.meeting_domain
                is_transcript_enabled = config_obj.is_transcript_enabled

                if config_obj.call_type != 'none':
                    is_voip_from_customer_end_enabled = config_obj.is_call_from_customer_end_enabled and bot_info_obj.livechat_provider == "cogno_livechat"
                    voip_type = config_obj.call_type
            except Exception:
                pass

            try:
                theme_obj = bot_obj.default_theme
                chat_page = theme_obj.chat_page
            except Exception:
                logger.warning("EasyChatPage: theme is not defined:", extra={
                               'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET["id"])})
                pass

            try:
                message_img = bot_obj.message_image
            except Exception:
                logger.warning("EasyChatPage: message image is not defined:", extra={
                               'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET["id"])})
                pass

            query_token_id = generate_query_token()

            category_objs = TicketCategory.objects.filter(bot=bot_obj)

            svg_icon_color = bot_obj.bot_theme_color
            if svg_icon_color.strip().lower() == "ffffff":
                svg_icon_color = "767B87"

            language_template_obj = RequiredBotTemplate.objects.filter(
                bot=bot_obj, language=Language.objects.get(lang=selected_language)).first()
            language_display_name = Language.objects.get(lang=selected_language).display
            if not language_template_obj.bot_name:
                ## If bot_name not present in case of bots that was created before this feature
                ## It will try to translate the bot_display_name
                ## Otherwise set bot_name as bot_display_name
                translated_name, translate_api_call_status = get_translated_text_with_api_status(
                    bot_obj.bot_display_name, selected_language, EasyChatTranslationCache, translate_api_call_status=True)
                if translate_api_call_status:
                    language_template_obj.bot_name = translated_name
                else:
                    language_template_obj.bot_name = bot_obj.bot_display_name
                language_template_obj.save()
            bot_channel = BotChannel.objects.filter(
                bot=bot_obj, channel=Channel.objects.get(name=channel))[0]
            is_web_bot_phonetic_typing_enabled = bot_channel.is_web_bot_phonetic_typing_enabled
            languages_supported = bot_channel.languages_supported.all()
            disclaimer_text = bot_channel.phonetic_typing_disclaimer_text
            config_obj = Config.objects.all()[0]
            version = config_obj.static_file_version
            cobrowsing_request_text = get_cobrowsing_request_text(
                bot_obj, LiveChatConfig)
            cobrowsing_request_text = get_translated_text(
                cobrowsing_request_text, selected_language, EasyChatTranslationCache)
            response = render(request, chat_page, {"bot_obj": bot_obj,
                                                   "category_objs": category_objs,
                                                   "is_nps_required": is_nps_required,
                                                   "query_token_id": query_token_id,
                                                   "message_img": message_img,
                                                   "csat_required_checkboxes": csat_required_checkboxes,
                                                   "collect_phone_number": collect_phone_number,
                                                   "collect_email_id": collect_email_id,
                                                   "mark_all_fields_mandatory": mark_all_fields_mandatory,
                                                   "language_template_obj": language_template_obj,
                                                   "languages_supported": languages_supported,
                                                   "selected_language": selected_language,
                                                   "language_display_name": language_display_name,
                                                   "version": version,
                                                   "is_webview_link": is_webview_link,
                                                   "is_web_bot_phonetic_typing_enabled": is_web_bot_phonetic_typing_enabled,
                                                   "disclaimer_text": disclaimer_text,
                                                   "channel": channel,
                                                   "is_voip_from_customer_end_enabled": is_voip_from_customer_end_enabled,
                                                   "voip_type": voip_type,
                                                   "svg_icon_color": svg_icon_color,
                                                   "meeting_domain": meeting_domain,
                                                   "cobrowsing_request_text": cobrowsing_request_text,
                                                   "language_script_type": language_script_type,
                                                   "bot_channel_obj": bot_channel_obj,
                                                   "mandatory": mandatory_text,
                                                   "bot_info_obj": bot_info_obj,
                                                   "is_transcript_enabled": is_transcript_enabled,
                                                   "suggestion_chunk_limit_and_total_no_chunks": suggestion_chunk_limit_and_total_no_chunks,
                                                   })

            # Checking if project is hosted and accessible through secure http
            # protocol(commenting for now, it may be useful in future)

            # if not settings.DEBUG:
            #     response.set_cookie("easychat_session_id", session_id, max_age=None,
            #                         expires=None, path='/', secure="secure", httponly=True)
            # else:
            #     response.set_cookie("easychat_session_id", session_id)

            return response
        else:
            # return HttpResponse("500")
            return render(request, 'EasyChatApp/error_500.html')

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EasyChatPage: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET["id"])})
        # return HttpResponse("Invalid Access")
        return render(request, 'EasyChatApp/error_404_text.html')


def EasyChatBotPage(request):  # noqa: N802
    main_page = settings.EASYCHAT_DEFAULT_MAIN_PAGE

    try:
        if request.method == "GET":
            validation_obj = EasyChatInputValidation()

            bot_id = request.GET["id"]
            bot_id = validation_obj.remo_html_from_string(str(bot_id))
            bot_obj = Bot.objects.get(pk=int(bot_id))

            if bot_obj.is_custom_js_required:
                create_custom_js_file(bot_id)
            if bot_obj.is_custom_css_required:
                create_custom_css_file(bot_id, bot_obj.default_theme.name)
            is_nps_required = False
            nps_obj = NPS.objects.filter(bot=bot_obj, channel__name='Web')
            if nps_obj:
                is_nps_required = True
            try:
                # theme = request.GET["theme"]
                # theme = remo_html_from_string(theme)
                theme_obj = bot_obj.default_theme
                main_page = theme_obj.main_page
            except Exception:
                pass

            return render(request, str(main_page), {
                "bot_obj": bot_obj,
                "is_nps_required": is_nps_required,
            })
        else:
            # return HttpResponse("Invalid request")
            return render(request, 'EasyChatApp/error_500.html')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EasyChatBotPage: %s at line %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET["id"])})
        # return HttpResponse("Invalid Access")
        return render(request, 'EasyChatApp/page_not_found.html')


def EasyChatHomePage(request):  # noqa: N802
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        return HttpResponseRedirect("/chat/home")
    else:
        return HttpResponseRedirect("/chat/login")


def AppHomePage(request):
    request.session["EASYCHAT_VERSION"] = settings.EASYCHAT_VERSION
    request.session[
        "EASYCHAT_DATE_OF_RELEASE"] = settings.EASYCHAT_DATE_OF_RELEASE
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        is_chatbot_allowed = True
        is_tms_allowed = is_tms_access_allowed(request, Agent)
        is_livechat_allowed = is_livechat_access_allowed(request, BotInfo)
        is_fusion_allowed = is_fusion_access_allowed(request, BotInfo)
        is_easyassist_allowed = is_easyassist_access_allowed(request)

        if is_livechat_allowed:
            redirect_obj = redirect_to_livechat(
                request, LiveChatUser, Supervisor, HttpResponseRedirect)
            if redirect_obj:
                return redirect_obj

        if is_easyassist_allowed:
            redirect_obj = redirect_to_easyassist(
                request, HttpResponseRedirect)
            if redirect_obj:
                return redirect_obj

        try:
            user_obj = User.objects.get(username=str(request.user.username))
            mark_livechat_user_online(user_obj)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Mark LiveChat User Online %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return render(request, "EasyChatApp/platform/home.html", {
            "is_chatbot_allowed": is_chatbot_allowed,
            "is_tms_allowed": is_tms_allowed,
            "is_livechat_allowed": is_livechat_allowed,
            "is_easyassist_allowed": is_easyassist_allowed,
            "is_fusion_allowed": is_fusion_allowed
        })
    elif request.user.is_authenticated:
        is_easyassist_allowed = is_easyassist_access_allowed(request)
        is_tms_allowed = is_tms_access_allowed(request, Agent)
        is_livechat_allowed = is_livechat_access_allowed(request, BotInfo)

        allowed_app_count = is_livechat_allowed + is_easyassist_allowed + is_tms_allowed

        if is_livechat_allowed and allowed_app_count == 1:
            redirect_obj = redirect_to_livechat(
                request, LiveChatUser, Supervisor, HttpResponseRedirect)
            if redirect_obj:
                return redirect_obj

        if is_easyassist_allowed and allowed_app_count == 1:
            redirect_obj = redirect_to_easyassist(
                request, HttpResponseRedirect)
            if redirect_obj:
                return redirect_obj

        if is_tms_allowed and allowed_app_count == 1:
            return HttpResponseRedirect("/tms")

        return render(request, "EasyChatApp/platform/home.html", {
            "is_chatbot_allowed": False,
            "is_tms_allowed": is_tms_allowed,
            "is_livechat_allowed": is_livechat_allowed,
            "is_easyassist_allowed": is_easyassist_allowed,
            "is_fusion_allowed": False
        })
    else:
        return HttpResponseRedirect("/chat/login")


# def Login(request):  # noqa: N802
#     if is_allowed(request, [BOT_BUILDER_ROLE, CUSTOMER_CARE_AGENT_ROLE]):
#         if request.user.role == "customer_care_agent":
#             if LiveChatUser.objects.filter(user=User.objects.get(username=str(request.user.username))).count():
#                 livechat_user = LiveChatUser.objects.get(
#                     user=User.objects.get(username=str(request.user.username)))
#                 livechat_user.resolved_chats = 0
#                 livechat_user.save()
#                 return HttpResponseRedirect("/livechat")
#             if request.user.status in ["1", "2"]:
#                 return HttpResponseRedirect("/tms")
#             else:
#                 return HttpResponseRedirect("/chat/home")
#         else:
#             return HttpResponseRedirect("/chat/home")
#     else:
#         captcha_image = get_random_captcha_image()
#         captcha_image = str(
#             "/static/EasyChatApp/captcha_images/" + captcha_image)
#         EasyChatAccessToken.objects.filter(is_expired=True).delete()
#         easychat_access_token = EasyChatAccessToken.objects.create()

#         if request.user_agent.is_mobile:
#             return render(request, 'EasyChatApp/mobile_login.html', {"captcha_image": captcha_image, "easychat_access_token": easychat_access_token})
#         else:
# return render(request, 'EasyChatApp/login.html', {"captcha_image":
# captcha_image, "easychat_access_token": easychat_access_token})


# def SalesLogin(request):  # noqa: N802
#     if is_allowed(request, [BOT_BUILDER_ROLE, CUSTOMER_CARE_AGENT_ROLE]):
#         if request.user.role == "customer_care_agent":
#             if len(LiveChatUser.objects.filter(user=User.objects.get(username=str(request.user.username)))):
#                 return HttpResponseRedirect("/livechat")
#             if request.user.status in ["1", "2"]:
#                 return HttpResponseRedirect("/tms")
#             else:
#                 return HttpResponseRedirect("/chat/bots")
#         else:
#             return HttpResponseRedirect("/chat/bots")
#     else:
#         captcha_image = get_random_captcha_image()
#         captcha_image = str(
#             "/static/EasyChatApp/captcha_images/" + captcha_image)
#         EasyChatAccessToken.objects.filter(is_expired=True).delete()
#         easychat_access_token = EasyChatAccessToken.objects.create()
# return render(request, 'EasyChatApp/sales_login.html', {"captcha_image":
# captcha_image, "easychat_access_token": easychat_access_token})


@require_POST
@permission_classes([IsAuthenticated])
def Logout(request):  # noqa: N802
    if request.user.is_authenticated:

        user = User.objects.get(username=request.user.username)
        user.is_online = False
        user.save()
        secured_login = SecuredLogin.objects.get(user=user)
        secured_login.failed_attempts = 0
        secured_login.save()

        audit_trail_data = json.dumps({
            "user_id": user.pk
        })
        try:
            livechat_user = LiveChatUser.objects.get(user=user)
            sessions_obj = LiveChatSessionManagement.objects.filter(
                user=livechat_user, session_completed=False)[0]
            trigger_agent_not_ready_report = False
            if sessions_obj.user.is_online:
                diff = datetime.datetime.now(
                    timezone.utc) - sessions_obj.session_ends_at
                sessions_obj.online_time += diff.seconds
                sessions_obj.session_ends_at = timezone.now()
                sessions_obj.session_completed = True
                sessions_obj.is_idle = False
                time_diff = datetime.datetime.now(
                    timezone.utc) - sessions_obj.last_idle_time
                sessions_obj.idle_time += time_diff.seconds
                if livechat_user.current_status == "0":
                    diff = timezone.now() - sessions_obj.time_marked_stop_interaction
                    sessions_obj.stop_interaction_time += diff.seconds
                    agent_not_ready_obj = sessions_obj.agent_not_ready.all().order_by(
                        '-not_ready_starts_at')[0]
                    agent_not_ready_obj.stop_interaction_duration = diff.seconds
                    agent_not_ready_obj.save()
                    trigger_agent_not_ready_report = True

                sessions_obj.save()
            else:
                diff = datetime.datetime.now(
                    timezone.utc) - sessions_obj.session_ends_at
                sessions_obj.offline_time += diff.seconds
                sessions_obj.session_ends_at = timezone.now()
                sessions_obj.session_completed = True
                if livechat_user.current_status == "0":
                    diff = timezone.now() - sessions_obj.time_marked_stop_interaction
                    sessions_obj.stop_interaction_time += diff.seconds
                    agent_not_ready_obj = sessions_obj.agent_not_ready.all().order_by(
                        '-not_ready_starts_at')[0]
                    agent_not_ready_obj.stop_interaction_duration = diff.seconds
                    agent_not_ready_obj.save()
                    trigger_agent_not_ready_report = True

                if sessions_obj.agent_not_ready.all().count():
                    agent_not_ready_obj = sessions_obj.agent_not_ready.all().order_by(
                        '-not_ready_starts_at')[0]
                    agent_not_ready_obj.not_ready_ends_at = timezone.now()
                    agent_not_ready_obj.is_expired = True
                    agent_not_ready_obj.save()
                    trigger_agent_not_ready_report = True     
                sessions_obj.save()
            send_event_for_login_logout(livechat_user, sessions_obj, LiveChatUser, LiveChatAdminConfig, LiveChatConfig, Bot, True)
            send_event_for_performance_report(livechat_user, sessions_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot, True)
            if trigger_agent_not_ready_report:
                send_event_for_agent_not_ready(livechat_user, agent_not_ready_obj, LiveChatUser, LiveChatConfig, LiveChatAdminConfig, Bot, True)
            livechat_user.is_online = False
            livechat_user.is_session_exp = True
            livechat_user.resolved_chats = 0
            livechat_cust_objs = LiveChatCustomer.objects.filter(
                agent_id=livechat_user, is_session_exp=False).exclude(channel=Channel.objects.filter(name="Email").first())
            for livechat_cust_obj in livechat_cust_objs:
                diff = datetime.datetime.now(
                    timezone.utc) - livechat_cust_obj.joined_date
                livechat_cust_obj.is_session_exp = True
                livechat_cust_obj.abruptly_closed = True
                livechat_cust_obj.chat_duration = diff.seconds
                livechat_cust_obj.last_appearance_date = datetime.datetime.now()
                livechat_cust_obj.chat_ended_by = "System"
                livechat_cust_obj.save()
                send_event_for_report_creation(livechat_cust_obj, LiveChatUser, LiveChatAdminConfig, LiveChatConfig, Bot)
            livechat_guest_agent_cust_objs = LiveChatCustomer.objects.filter(
                guest_agents=livechat_user, is_session_exp=False)
            for livechat_guest_agent_cust_obj in livechat_guest_agent_cust_objs:
                livechat_guest_agent_cust_obj.guest_agents.remove(
                    livechat_user)
                guest_session_status = json.loads(
                    livechat_guest_agent_cust_obj.guest_session_status)
                if guest_session_status[livechat_user.user.username] == "accept":
                    guest_session_status[livechat_user.user.username] = "exit"
                elif guest_session_status[livechat_user.user.username] == "onhold":
                    guest_session_status[
                        livechat_user.user.username] = "no_response"
                    action_datetime = datetime.datetime.now() - datetime.timedelta(minutes=1)
                    LiveChatGuestAgentAudit.objects.create(
                        livechat_customer=livechat_guest_agent_cust_obj,
                        livechat_agent=livechat_user,
                        action="no_response",
                        action_datetime=action_datetime)
                livechat_guest_agent_cust_obj.guest_session_status = json.dumps(
                    guest_session_status)
                livechat_guest_agent_cust_obj.save()
            livechat_user.ongoing_chats = 0
            livechat_user.save()

            description = "Logout from System"
            add_audit_trail(
                "EASYCHATAPP",
                user,
                "Logout",
                description,
                json.dumps({}),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

            save_audit_trail_data("8", livechat_user, LiveChatAuditTrail)
        except Exception:
            pass

        save_audit_trail(user, USER_LOGGED_OUT, audit_trail_data)

        try:
            active_agent = get_active_agent_obj(request, User, CobrowseAgent)
            active_agent.is_active = False
            active_agent.save()
            save_audit_trail_easyassist(active_agent, "2",
                                        "Logout from System", CobrowsingAuditTrail)
        except Exception:
            pass

        user_session_obj = UserSession.objects.filter(
            user__username=request.user.username)
        logout(request)

        if user_session_obj:
            delete_user_session(user_session_obj[0])

    return HttpResponseRedirect("/chat/login")


def Home(request):  # noqa: N802
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        return render(request, "EasyChatApp/home.html")
    else:
        return HttpResponseRedirect("/chat/login")


def DeveloperConsole(request):  # noqa: N802
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        # return HttpResponseRedirect("/chat/bots")
        return HttpResponseRedirect("/chat/bots/")
        # return render(request, "EasyChatApp/console.html")
    else:
        return HttpResponseRedirect("/chat/login")


def AuditTrailPage(request):  # noqa: N802
    if is_allowed(request, [BOT_BUILDER_ROLE]):

        user_obj = User.objects.get(username=request.user.username)

        user_obj_list = [user_obj]

        if user_obj.is_staff:
            supervisor_obj = None
            try:
                supervisor_obj = Supervisor.objects.get(supervisor=user_obj)
            except Exception:
                pass

            if supervisor_obj != None:
                managers = supervisor_obj.managers.all()
                user_obj_list += list(managers)

        audit_trail_objs = AuditTrail.objects.filter(
            user__in=user_obj_list).order_by('-pk')
        # total_audit_objs = len(audit_trail_objs)
        paginator = Paginator(
            audit_trail_objs, 100)
        page = request.GET.get('page')

        try:
            audit_trail_objs = paginator.page(page)
        except PageNotAnInteger:
            audit_trail_objs = paginator.page(1)
        except EmptyPage:
            audit_trail_objs = paginator.page(paginator.num_pages)

        # if page != None:
        #     start_point = 100 * (int(page) - 1) + 1
        #     end_point = min(100 * int(page), total_audit_objs)
        # else:
        #     start_point = 1
        #     end_point = min(100, total_audit_objs)

        description = "Open Audit Trail"
        add_audit_trail(
            "EASYCHATAPP",
            user_obj,
            "EasychatAuditTrail",
            description,
            json.dumps({}),
            request.META.get("PATH_INFO"),
            request.META.get('HTTP_X_FORWARDED_FOR')
        )

        return HttpResponseRedirect("/audit-trail/dashboard/?selected_date_filter=1&selected_apps=easychatapp&")
    else:
        return HttpResponseRedirect("/chat/login")


def SupervisorPage(request):  # noqa: N802
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        if request.user.is_staff:
            user_obj = User.objects.get(username=request.user.username)
            supervisor_obj = Supervisor.objects.filter(supervisor=user_obj)[0]
            managers = supervisor_obj.get_managers_list()
            sandbox_users = user_obj.sandbox_users.all()
            return render(request, "EasyChatApp/platform/supervisor.html", {
                "supervisor_obj": supervisor_obj,
                "managers": managers,
                "sandbox_users": sandbox_users,
                "expanded_logo": True
            })
        else:
            # return HttpResponse("401")
            return render(request, 'EasyChatApp/error_404.html')
    else:
        return HttpResponseRedirect("/chat/login")


def EasyChatDrivePage(request):  # noqa: N802
    if is_allowed(request, [BOT_BUILDER_ROLE]) and request.user.check_data_drive_permission():

        user_obj = User.objects.get(username=request.user.username)
        easychat_drive_objs = EasyChatDrive.objects.filter(user=user_obj)

        username = request.user.username
        user_obj = User.objects.get(username=str(username))
        bot_objs = get_uat_bots(user_obj)

        intent_objs = Intent.objects.filter(
            bots__in=bot_objs, is_deleted=False, is_hidden=False).distinct()

        return render(request, "EasyChatApp/analytics/easychat_drive.html", {
            "easychat_drive_objs": easychat_drive_objs,
            "intent_objs": intent_objs,
            "bot_objs": bot_objs
        })
    else:
        return HttpResponseRedirect("/chat/login")


def SelfLearning(request):  # noqa: N802
    if is_allowed(request, [BOT_BUILDER_ROLE]):

        current_datetime_obj = datetime.datetime.now().date()
        previous_datetime_obj = datetime.datetime.now().date() - datetime.timedelta(30)
        to_date = datetime.datetime.strftime(current_datetime_obj, "%Y-%m-%d")
        from_date = datetime.datetime.strftime(
            previous_datetime_obj, "%Y-%m-%d")
        excel_to_date = datetime.datetime.strftime(
            current_datetime_obj, "%d-%m-%Y")
        excel_from_date = datetime.datetime.strftime(
            previous_datetime_obj, "%d-%m-%Y")

        validation_obj = EasyChatInputValidation()

        selected_bot_obj = None
        if "bot_pk" in request.GET:
            bot_pk = request.GET["bot_pk"]
            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))
            selected_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)
            if not check_access_for_user(request.user, selected_bot_obj.pk, "Self Learning Related"):
                return HttpResponseNotFound("You do not have access to this page")

        if selected_bot_obj == None:
            return render(request, 'EasyChatApp/error_404.html')

        bot_objs = Bot.objects.filter(pk=int(selected_bot_obj.pk))

        maximum_clusters = 0

        if selected_bot_obj.static_analytics:
            maximum_clusters = NUMBER_OF_DEFAULT_CLUSTER
        else:
            user_message_list = MISDashboard.objects.filter(intent_name=None).filter(
                creation_date__gte=from_date).filter(
                creation_date__lte=to_date).filter(
                bot__in=bot_objs).order_by('-date')

            maximum_clusters = user_message_list.count()

        no_classes = min(maximum_clusters, DEFAULT_NO_OF_CLASSES_SELF_LEARNING)

        bots = get_uat_bots(User.objects.get(username=request.user.username))

        return render(request, "EasyChatApp/platform/self_learning.html", {
            "selected_bot_obj": selected_bot_obj,
            "to_date": to_date,
            "from_date": from_date,
            "no_classes": no_classes,
            "bots": bots,
            "maximum_clusters": maximum_clusters,
            "excel_to_date": excel_to_date,
            "excel_from_date": excel_from_date,
        })
    else:
        return HttpResponseRedirect("/chat/login")


def ExtractFAQs(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Intent Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page or the bot might have been deleted.")
            if "bot_pk" in request.GET:
                bot_pk = request.GET["bot_pk"]

            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if not Bot.objects.filter(pk=int(bot_pk), users=user_obj, is_deleted=False).count():
                return HttpResponseNotFound("You do not have access to this page")
            else:
                bot_obj = Bot.objects.get(
                    pk=int(bot_pk), users=user_obj, is_deleted=False)

            bot_objs = user_obj.get_related_bot_objs_for_access_type(
                "Analytics Related")
            return render(request, "EasyChatApp/platform/extract_faqs.html", {
                "bot_objs": bot_objs,
                "selected_bot_obj": bot_obj
            })

        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ExtractFAQs %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def Edit(request):  # noqa: N802
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        if not (check_access_for_user(request.user, None, "Bot Related", "overall") or check_access_for_user(request.user, None, "Intent Related", "overall")):
            return HttpResponseNotFound("You do not have access to this page")
        return render(request, 'EasyChatApp/edit.html')
    else:
        return HttpResponseRedirect("/chat/login")


def SettingsConsole(request):  # noqa: N802
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        app_config = Config.objects.all()[0]
        return render(request, 'EasyChatApp/platform/settings.html', {
            "app_config": app_config
        })
    else:
        return HttpResponseRedirect("/chat/login/")


def AutomatedTestConsole(request):  # noqa: N802
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        username = request.user.username
        user_obj = User.objects.get(username=str(username))
        bot_objs = get_uat_bots(user_obj)
        if not check_access_for_user(request.user, None, "Automated Testing", "overall"):
            return HttpResponseNotFound("You do not have access to this page")

        validation_obj = EasyChatInputValidation()

        selected_bot_obj = None
        if "bot_pk" in request.GET:
            bot_pk = request.GET["bot_pk"]
            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))
            selected_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)
            bot_objs = [selected_bot_obj]
            if not check_access_for_user(request.user, bot_pk, "Automated Testing"):
                return HttpResponseNotFound("You do not have access to this page")

        if selected_bot_obj == None:
            return render(request, 'EasyChatApp/error_404.html')

        intent_objs = Intent.objects.filter(
            bots__in=bot_objs, is_deleted=False, is_hidden=False).distinct()

        total_sentences = 0
        for intent_obj in intent_objs:
            training_data_dict = json.loads(intent_obj.training_data)
            total_sentences += len(training_data_dict.keys())

        context = {
            "selected_bot_obj": selected_bot_obj,
            'intent_objs': intent_objs,
            'bot_objs': bot_objs,
            'total_sentences': total_sentences
        }

        test_case_obj_list = TestCase.objects.filter(user=user_obj)
        sentence_list = []
        intent_list = []

        if(len(test_case_obj_list) != 0):
            for test_case_obj in test_case_obj_list:
                test_case_sentence_list = json.loads(
                    test_case_obj.sentence)["sentence_list"]
                test_case_is_active_list = json.loads(
                    test_case_obj.is_active)["is_active_list"]
                counter = 0
                for sentence in test_case_sentence_list:
                    if test_case_is_active_list[counter] == True:
                        sentence_list.append(sentence)
                        intent_list.append(test_case_obj.intent)
                    counter += 1

            context = {
                'intent_objs': intent_objs,
                'sentence_list': sentence_list,
                'intent_list': intent_list,
                'bot_objs': bot_objs,
                'total_sentences': total_sentences
            }

        return render(request, 'EasyChatApp/platform/automated_testing.html', context)
    else:
        return HttpResponseRedirect("/chat/login/")


def CreateBotManager(request):  # noqa: N802
    response = {}
    response["status"] = 500
    response["message"] = "Internal Server Error"
    try:
        if request.user.is_authenticated and request.user.is_staff:

            supervisor = User.objects.get(username=request.user.username)
            data = json.loads(DecryptVariable(request.POST["data"]))

            validation_obj = EasyChatInputValidation()

            manager_id = data["manager_id"]
            manager_id = validation_obj.remo_html_from_string(str(manager_id))
            first_name = data["first_name"]
            last_name = data["last_name"]
            password = data["password"]
            password = validation_obj.remo_html_from_string(password)
            email = data["email"]

            if not validation_obj.is_valid_name(first_name):
                response["status"] = 302
                response["message"] = "Please enter a valid first name"

            if not validation_obj.is_valid_name(last_name):
                response["status"] = 302
                response["message"] = "Please enter a valid last name"

            if not validation_obj.is_valid_email(email):
                response["status"] = 302
                response["message"] = "Please enter a valid email"

            if response["status"] == 302:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                response = {"response": response}
                return HttpResponse(json.dumps(response), content_type="application/json")

            username = email

            """
            manager_id's value will be None if user is creating new bot manager
            else it will have some value.
            """
            if manager_id == "None":
                user_objs = User.objects.filter(username=username)
                if user_objs.count() == 0:
                    if len(password) >= 8:
                        user_obj = User.objects.create(username=username,
                                                       password=password,
                                                       email=email,
                                                       first_name=first_name,
                                                       last_name=last_name,
                                                       role="bot_builder")

                        PasswordHistory.objects.create(
                            user=user_obj, password=password)
                        supervisor_obj = Supervisor.objects.filter(
                            supervisor=supervisor).first()
                        supervisor_obj.managers.add(user_obj)
                        supervisor_obj.save()
                        response["status"] = 200
                        response["message"] = "success"
                    else:
                        response["status"] = 301
                        response[
                            "message"] = "Password should be of aleast 8 characters"
                else:
                    response["status"] = 301
                    response["message"] = "Matching bot manager already exists"
            else:
                user_obj = User.objects.get(pk=int(manager_id))
                # we are checking whether matching bot manager already exists
                # before creating/updating existing one.
                user_obj.first_name = first_name
                user_obj.last_name = last_name
                user_obj.save()
                response["status"] = 200
                response["message"] = "success"

            description = "New Bot Manager" + \
                " (" + first_name + " " + last_name + ") has been added"
            add_audit_trail(
                "EASYCHATAPP",
                user_obj,
                "Add-Manager",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )
        else:
            response["status"] = 401
            response["message"] = "Unauthorised access"
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[CreateBotManager] %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    custom_encrypt_obj = CustomEncrypt()
    response = custom_encrypt_obj.encrypt(json.dumps(response))
    response = {"response": response}
    return HttpResponse(json.dumps(response), content_type="application/json")


def CreateSandboxUser(request):
    response = {}
    response["status"] = 500
    response["message"] = "Some error occurred, Please refresh the page and try again"
    try:
        if request.user.is_authenticated and request.user.is_staff:

            data = json.loads(DecryptVariable(request.POST["data"]))

            validation_obj = EasyChatInputValidation()

            username = data["username"]
            username = validation_obj.remo_html_from_string(username)
            password = data["password"]
            password = validation_obj.remo_html_from_string(password)
            if not validation_obj.is_valid_email(username) or len(username) > 100:
                response["status"] = 301
                response["message"] = "Please enter a valid Email Id"
                if len(username) > 100:
                    response[
                        "message"] = "Email Id should be less than 100 characters."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                response = {"response": response}
                return HttpResponse(json.dumps(response), content_type="application/json")

            if not validation_obj.is_valid_password(password):
                response["status"] = 301
                response["message"] = "Invalid Password"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                response = {"response": response}
                return HttpResponse(json.dumps(response), content_type="application/json")

            # supervisor is the user who is creating the sandboxuser
            supervisor_obj = User.objects.get(
                username=request.user.username)

            user_objs = User.objects.filter(username__iexact=username)

            if not user_objs.exists():
                user_obj = User.objects.create(username=username,
                                               password=password,
                                               is_staff=False,
                                               status="1", is_chatbot_creation_allowed="1",
                                               role="bot_builder", is_sandbox_user=True)

                PasswordHistory.objects.create(
                    user=user_obj, password=password)
                sandbox_user_obj = SandboxUser.objects.create(
                    username=username, password=password)

                supervisor_obj.sandbox_users.add(sandbox_user_obj)
                supervisor_obj.save()
                sandbox_user_obj.save()
                description = "New Sandbox User" + \
                    " (" + username + ") has been added"
                add_audit_trail(
                    "EASYCHATAPP",
                    supervisor_obj,
                    "Add-User",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response["status"] = 200
                response["message"] = "success"
            else:
                response["status"] = 301
                response[
                    "message"] = "An account with the same ID already exists. Please use another ID"

        else:
            response["status"] = 401
            response["message"] = "Unauthorised access"

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[CreateSandboxUser] %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    custom_encrypt_obj = CustomEncrypt()
    response = custom_encrypt_obj.encrypt(json.dumps(response))
    response = {"response": response}
    return HttpResponse(json.dumps(response), content_type="application/json")


def RemoveSandboxUser(request, user_pk):  # noqa: N802
    response = {}
    response["status"] = 500
    response["message"] = "Some error occurred, Please refresh the page and try again."
    try:
        if request.user.is_authenticated and request.user.is_staff:

            supervisor = User.objects.get(username=request.user.username)
            sandbox_user_obj = SandboxUser.objects.get(pk=int(user_pk))
            if sandbox_user_obj not in supervisor.sandbox_users.all():
                response["status"] = 401
                response["message"] = "Unauthorised access"
            else:
                username = sandbox_user_obj.username
                user_obj = User.objects.get(username=username)
                supervisor.sandbox_users.remove(sandbox_user_obj)
                supervisor.save()
                sandbox_user_obj.delete()
                user_obj.is_active = False
                user_obj.save()

                description = "SandboxUser" + \
                    " (" + username + ") has been deleted"
                add_audit_trail(
                    "EASYCHATAPP",
                    supervisor,
                    "Delete-User",
                    description,
                    json.dumps({}),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                return HttpResponseRedirect("/chat/supervisor/#sandbox-credentials")
        else:
            response["status"] = 401
            response["message"] = "Unauthorised access"
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[RemoveSandboxUser] %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    custom_encrypt_obj = CustomEncrypt()
    response = custom_encrypt_obj.encrypt(json.dumps(response))
    response = {"response": response}
    return HttpResponse(json.dumps(response), content_type="application/json")


def ExtendSandboxUser(request):  # noqa: N802
    response = {}
    response["status"] = 500
    response["message"] = "Some error occurred, Please refresh the page and try again."
    try:
        if request.user.is_authenticated and request.user.is_staff:
            data = json.loads(DecryptVariable(request.POST["data"]))
            user_pk = data["user_pk"]
            sandbox_user_obj = SandboxUser.objects.get(pk=int(user_pk))
            last_expiration_date = sandbox_user_obj.will_expire_on
            sandbox_user_obj.will_expire_on = last_expiration_date + \
                timezone.timedelta(days=15)
            sandbox_user_obj.last_extention_date = timezone.now()
            sandbox_user_obj.is_expired = False
            sandbox_user_obj.number_of_times_extended += 1
            sandbox_user_obj.save()

            response["status"] = 200
            response["message"] = "success"
            description = "SandboxUser with id" + \
                " (" + str(user_pk) + ") time has been extended"
            add_audit_trail(
                "EASYCHATAPP",
                sandbox_user_obj,
                "Update-User",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

        else:
            response["status"] = 401
            response["message"] = "Unauthorised access"
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[ExtendBotManager] " +
                     str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    custom_encrypt_obj = CustomEncrypt()
    response = custom_encrypt_obj.encrypt(json.dumps(response))
    response = {"response": response}
    return HttpResponse(json.dumps(response), content_type="application/json")


def RemoveBotManager(request, manager_pk):  # noqa: N802
    response = {}
    response["status"] = 500
    response["message"] = "Internal Server Error"
    try:
        if request.method == "POST" and request.user.is_authenticated and request.user.is_staff:
            supervisor = User.objects.get(username=request.user.username)
            manager = User.objects.get(pk=int(manager_pk))
            supervisor_obj = Supervisor.objects.get(supervisor=supervisor)
            if manager in supervisor_obj.managers.all():
                supervisor_obj.managers.remove(manager)
                supervisor_obj.save()
                manager.is_active = False
                manager.save()

                description = "Bot Manager" + \
                    " (" + manager.username + ") has been removed"
                add_audit_trail(
                    "EASYCHATAPP",
                    manager,
                    "Delete-User",
                    description,
                    json.dumps({}),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )
                return HttpResponseRedirect("/chat/supervisor/")
            else:
                return HttpResponseNotFound("You do not have access to this page")
        else:
            return HttpResponseNotFound("You do not have access to this page")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[RemoveBotManager] %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    custom_encrypt_obj = CustomEncrypt()
    response = custom_encrypt_obj.encrypt(json.dumps(response))
    response = {"response": response}
    return HttpResponse(json.dumps(response), content_type="application/json")


def GetEasyChatLicence(request):  # noqa: N802
    response = {}
    response["status_code"] = 500
    response["status_message"] = ""
    if request.user.is_authenticated and request.method == "GET":
        _, licence_filename = export_data(None, request.user.username)
        path_to_file = '/files/private/' + str(licence_filename)
        response = HttpResponse(
            status=200, content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(
            str(licence_filename))
        response['X-Sendfile'] = smart_str(path_to_file)
        response['X-Accel-Redirect'] = path_to_file
        return response
    else:
        return render(request, 'EasyChatApp/error_500.html')


class LoginSubmitAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        temp_user = None
        try:
            config = get_developer_console_settings()
            if(config.disabled_multifactor_authentication):
                data = request.data

                if not isinstance(data, dict):
                    data = json.loads(data)

                data = DecryptVariable(data["Request"])
                data = json.loads(data)

                username = data['username']
                # logger.info("username %s", type(username))
                username = DecryptVariable(username)

                password = data['password']
                password = DecryptVariable(password)
                captcha = data["captcha"]
                captcha = DecryptVariable(captcha)
                captcha_key = data["captcha_image"]
                captcha_key = DecryptVariable(captcha_key)
                easychat_access_token = data["easychat_access_token"]
                logger.info("easychat_access_token %s", easychat_access_token, extra={
                            'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                easychat_access_token = DecryptVariable(easychat_access_token)
                easychat_access_token_obj = EasyChatAccessToken.objects.filter(
                    token=easychat_access_token, is_expired=False)[0]
                captcha_key = captcha_key.split("/")[6].split(".")[0]
                captcha_key = next(item for item in captcha_image_dict if item["key"] == captcha_key)
                captcha_key = captcha_key["value"]

                try:
                    temp_user = User.objects.get(username=username)
                except Exception:
                    logger.warning("LoginSubmitAPI: Matching User doesn't exist.", extra={'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                if temp_user:
                    password_change_flag = False
                    secured_login_obj = SecuredLogin.objects.get(user=temp_user)
                    last_password_changed_date = secured_login_obj.last_password_change_date
                    prev_passwords = secured_login_obj.previous_password_hashes
                    prev_passwords = json.loads(prev_passwords)

                    if temp_user.password_change_duration and timezone.now() > (last_password_changed_date + datetime.timedelta(days=int(temp_user.password_change_duration))):
                        password_change_flag = True

                    if temp_user.is_first_login and len(prev_passwords["password_hash"]) <= 1:
                        password_change_flag = True

                    if password_change_flag == True:
                        response['status'] = 401
                        response[
                            'message'] = 'Your password has expired! please reset your password'
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(json.dumps(response))
                        return Response(data=response)

                if str(captcha) == str(captcha_key):
                    user = authenticate(username=username, password=password)
                    is_sandbox_user = user.is_sandbox_user
                    response["is_sandbox_user"] = is_sandbox_user
                    # checking for expired credentials for sandbox user

                    # Check for Cobrowse User
                    if easyassist_check_for_admin_expired_credentials(user, CobrowseAgent, CobrowseSandboxUser):
                        response['status'] = 303
                        response[
                            'message'] = 'Your credentials are expired, to use it, please contact the team'
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(json.dumps(response))
                        return Response(data=response)

                    # Check for Account Active Cobrowse User
                    if easyassist_is_active_user(user, CobrowseAgent) == False:
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(json.dumps(response))
                        return Response(data=response)
                        
                    if is_sandbox_user:
                        # Check for EasyChat User
                        if check_for_expired_credentials(user, SandboxUser):
                            response['status'] = 303
                            response[
                                'message'] = 'Your credentials are expired, please request again for access'
                            custom_encrypt_obj = CustomEncrypt()
                            response = custom_encrypt_obj.encrypt(
                                json.dumps(response))
                            return Response(data=response)

                    user.is_online = is_online(user.username)

                    logout_other = data["logout_other"]
                    logout_other = DecryptVariable(logout_other)

                    if logout_other == 'true':
                        logout_all(user.username)
                        user.is_online = False

                    try:
                        secured_login = SecuredLogin.objects.get(user=user)
                    except Exception:
                        secured_login = SecuredLogin.objects.create(user=user)

                    time_difference = (
                        timezone.now() - secured_login.last_attempt_datetime).seconds

                    # if time_difference >= settings.EASYCHAT_SESSION_AGE:
                    #     user.is_online = False
                    #     user.save()

                    if secured_login.failed_attempts > 5:
                        time_minutes = time_difference / 60
                        if time_minutes >= 60:
                            easychat_access_token_obj.is_expired = True
                            easychat_access_token_obj.save()
                            login(
                                request, user, backend='django.contrib.auth.backends.ModelBackend')
                            user.is_online = True
                            user.save()

                            audit_trail_data = json.dumps({
                                "user_id": user.pk
                            })

                            save_audit_trail(user, USER_LOGGED_IN,
                                                audit_trail_data)

                            try:
                                active_agent = get_active_agent_obj(
                                    request, User, CobrowseAgent)
                                active_agent.is_active = True
                                active_agent.save()
                                save_audit_trail_easyassist(active_agent, "1",
                                                            "Login from System", CobrowsingAuditTrail)
                            except Exception:
                                pass

                            secured_login.failed_attempts = 0
                            secured_login.save()
                            description = "Login into system"
                            add_audit_trail(
                                "EASYCHATAPP",
                                user,
                                "Login",
                                description,
                                json.dumps(data),
                                request.META.get("PATH_INFO"),
                                request.META.get('HTTP_X_FORWARDED_FOR')
                            )
                            response['status'] = 200
                            response['username'] = request.user.username
                        else:
                            response["status"] = 301
                    elif user.is_online:
                        logger.info("user is online", extra={'AppName': 'EasyChat', 'user_id': str(
                            username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        response["status"] = 300
                    else:
                        easychat_access_token_obj.is_expired = True
                        easychat_access_token_obj.save()

                        try:
                            # this condition checks that there is no user with same
                            # id password
                            # this is incase if a Livechatuser is made, then deleted
                            # then again a livechatuser is made with same id password.
                            # in that case user should be able to login
                            livechat_user_exists = LiveChatUser.objects.filter(
                                user=user, is_deleted=False)
                            if LiveChatUser.objects.filter(user=user, is_deleted=True) and livechat_user_exists.count() == 0:
                                response["status"] = 403
                                custom_encrypt_obj = CustomEncrypt()
                                response = custom_encrypt_obj.encrypt(
                                    json.dumps(response))
                                return Response(data=response)
                            else:
                                pass
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("LoginSubmitAPI Error %s at %s",
                                            str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                            pass

                        login(request, user,
                                backend='django.contrib.auth.backends.ModelBackend')

                        mark_livechat_user_online(user)
                        from user_agents import parse
                        ua_string = request.META.get('HTTP_USER_AGENT')
                        user_agent = parse(ua_string)
                        browser = user_agent.browser.family
                        source_ip = request.META.get('REMOTE_ADDR')

                        audit_trail_data = json.dumps({
                            "user_id": user.pk,
                            "browser": browser,
                            "source_ip": source_ip
                        })

                        save_audit_trail(user, USER_LOGGED_IN, audit_trail_data)

                        secured_login.failed_attempts = 0
                        secured_login.save()
                        user.is_online = True
                        user.save()

                        try:
                            active_agent = get_active_agent_obj(
                                request, User, CobrowseAgent)
                            active_agent.is_active = True
                            active_agent.save()
                            save_audit_trail_easyassist(active_agent, "1",
                                                        "Login from System", CobrowsingAuditTrail)
                        except Exception:
                            pass

                        description = "Login into system"
                        add_audit_trail(
                            "EASYCHATAPP",
                            user,
                            "Login",
                            description,
                            json.dumps(data),
                            request.META.get("PATH_INFO"),
                            request.META.get('HTTP_X_FORWARDED_FOR')
                        )

                        response['status'] = 200
                        response["username"] = request.user.username
                else:
                    response['status'] = 302
            else:
                import urllib.parse
                data = urllib.parse.unquote(request.data['json_string'])
                data = DecryptVariable(data)
                data = json.loads(data)

                validation_obj = EasyChatInputValidation()

                user_name = data['user_name']
                user_name = validation_obj.remo_html_from_string(user_name).strip()
                
                if not validation_obj.is_valid_email(user_name):
                    response["status"] = 301
                    response['status_message'] = "Username " + \
                        user_name + "Is Not a Valid Email"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                otp_access_token = data["otp_access_token"]
                otp_access_token = validation_obj.remo_html_from_string(
                    otp_access_token).strip()
                otp = data["otp"]
                otp = validation_obj.remo_html_from_string(otp).strip()
                temp_user = User.objects.filter(
                    username=user_name, is_active=True).first()

                if not temp_user:
                    response['status'] = 301
                    response['status_message'] = "Username " + \
                        user_name + " does not exists."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                otp_details_obj = EasyChatOTPDetails.objects.filter(
                    user=temp_user, token=uuid.UUID(otp_access_token)).first()

                if not otp_details_obj:
                    response["status"] = 301
                    response["status_message"] = "Their was Some Error in Verifying The OTP , Please Refresh and Try Again"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
                #  session is expired in 10 minutes
                if otp_details_obj.is_expired:
                    response["status"] = 302
                    response["status_message"] = "Incorrect/Expired OTP entered."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                time_difference = (
                    timezone.now() - otp_details_obj.otp_sent_on).total_seconds()

                if time_difference > config.authentication_otp_expire_after * 60:
                    otp_details_obj.is_expired = True
                    otp_details_obj.save()
                    response["status"] = 302
                    response["status_message"] = "Incorrect/Expired OTP entered."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                if otp != otp_details_obj.otp:
                    response["status"] = 302
                    response["status_message"] = "Incorrect/Expired OTP entered"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                temp_user.is_online = is_online(temp_user.username)

                logout_other = data["logout_other"]

                easychat_access_token = data["easychat_access_token"]
                logger.info("easychat_access_token %s", easychat_access_token, extra={
                            'AppName': 'EasyChat', 'user_id': str(user_name), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                easychat_access_token = DecryptVariable(easychat_access_token)
                easychat_access_token_obj = EasyChatAccessToken.objects.filter(
                    token=easychat_access_token, is_expired=False)[0]

                if logout_other:
                    logout_all(temp_user.username)
                    temp_user.is_online = False

                try:
                    secured_login = SecuredLogin.objects.get(user=temp_user)
                except Exception:
                    secured_login = SecuredLogin.objects.create(user=temp_user)

                time_difference = (
                    timezone.now() - secured_login.last_attempt_datetime).seconds

                # if time_difference >= settings.EASYCHAT_SESSION_AGE:
                #     user.is_online = False
                #     user.save()

                if secured_login.failed_attempts > 5:
                    time_minutes = time_difference / 60
                    if time_minutes >= 60:
                        easychat_access_token_obj.is_expired = True
                        easychat_access_token_obj.save()
                        login(
                            request, temp_user, backend='django.contrib.auth.backends.ModelBackend')
                        temp_user.is_online = True
                        temp_user.save()

                        audit_trail_data = json.dumps({
                            "user_id": temp_user.pk
                        })

                        save_audit_trail(temp_user, USER_LOGGED_IN,
                                            audit_trail_data)

                        try:
                            active_agent = get_active_agent_obj(
                                request, User, CobrowseAgent)
                            active_agent.is_active = True
                            active_agent.save()
                            save_audit_trail_easyassist(active_agent, "1",
                                                        "Login from System", CobrowsingAuditTrail)
                        except Exception:
                            pass

                        secured_login.failed_attempts = 0
                        secured_login.save()
                        otp_details_obj.is_expired = True
                        otp_details_obj.save()
                        description = "Login into system"
                        add_audit_trail(
                            "EASYCHATAPP",
                            temp_user,
                            "Login",
                            description,
                            json.dumps(data),
                            request.META.get("PATH_INFO"),
                            request.META.get('HTTP_X_FORWARDED_FOR')
                        )
                        response['status'] = 200
                        response['username'] = request.user.username
                    else:
                        response["status"] = 301
                        response["status_message"] = "You have failed your login more than 5 times. Kindly contact administrator or try after some time."
                elif temp_user.is_online:
                    logger.info("user is online", extra={'AppName': 'EasyChat', 'user_id': str(
                        user_name), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    response["status"] = 300
                else:
                    easychat_access_token_obj.is_expired = True
                    easychat_access_token_obj.save()

                    try:
                        # this condition checks that there is no user with same
                        # id password
                        # this is incase if a Livechatuser is made, then deleted
                        # then again a livechatuser is made with same id password.
                        # in that case user should be able to login
                        livechat_user_exists = LiveChatUser.objects.filter(
                            user=temp_user, is_deleted=False)
                        if LiveChatUser.objects.filter(user=temp_user, is_deleted=True) and livechat_user_exists.count() == 0:
                            response["status"] = 403
                            custom_encrypt_obj = CustomEncrypt()
                            response = custom_encrypt_obj.encrypt(
                                json.dumps(response))
                            return Response(data=response)
                        else:
                            pass
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("LoginSubmitAPI Error %s at %s",
                                        str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        pass

                    login(request, temp_user,
                            backend='django.contrib.auth.backends.ModelBackend')

                    mark_livechat_user_online(temp_user)
                    from user_agents import parse
                    ua_string = request.META.get('HTTP_USER_AGENT')
                    user_agent = parse(ua_string)
                    browser = user_agent.browser.family
                    source_ip = request.META.get('REMOTE_ADDR')

                    audit_trail_data = json.dumps({
                        "user_id": temp_user.pk,
                        "browser": browser,
                        "source_ip": source_ip
                    })

                    save_audit_trail(temp_user, USER_LOGGED_IN, audit_trail_data)

                    secured_login.failed_attempts = 0
                    secured_login.save()
                    temp_user.is_online = True
                    temp_user.save()
                    otp_details_obj.is_expired = True
                    otp_details_obj.save()

                    try:
                        active_agent = get_active_agent_obj(
                            request, User, CobrowseAgent)
                        active_agent.is_active = True
                        active_agent.save()
                        save_audit_trail_easyassist(active_agent, "1",
                                                    "Login from System", CobrowsingAuditTrail)
                    except Exception:
                        pass

                    description = "Login into system"
                    add_audit_trail(
                        "EASYCHATAPP",
                        temp_user,
                        "Login",
                        description,
                        json.dumps(data),
                        request.META.get("PATH_INFO"),
                        request.META.get('HTTP_X_FORWARDED_FOR')
                    )

                    response['status'] = 200
                    response["username"] = request.user.username

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LoginSubmitAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            if temp_user != None:
                secured_login = SecuredLogin.objects.get(user=temp_user)
                secured_login.last_attempt_datetime = timezone.now()
                if secured_login.failed_attempts > 5:
                    response["status"] = 301
                    response["status_message"] = "You have failed your login more than 5 times. Kindly contact administrator or try after some time."
                else:
                    secured_login.failed_attempts = secured_login.failed_attempts + 1
                secured_login.save()
    
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class LoginOTPAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        temp_user = None
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["Request"])
            data = json.loads(data)

            username = data['username']
            # logger.info("username %s", type(username))
            username = DecryptVariable(username)

            password = data['password']
            password = DecryptVariable(password)
            captcha = data["captcha"]
            captcha = DecryptVariable(captcha)
            captcha_key = data["captcha_image"]
            captcha_key = DecryptVariable(captcha_key)
            captcha_key = captcha_key.split("/")[6].split(".")[0]
            captcha_key = next(item for item in captcha_image_dict if item[
                               "key"] == captcha_key)
            captcha_key = captcha_key["value"]

            try:
                temp_user = User.objects.get(username=username)
            except Exception:
                logger.warning("LoginOTPAPI: Matching User doesn't exist.", extra={
                               'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            if temp_user:
                password_change_flag = False
                secured_login_obj = SecuredLogin.objects.get(user=temp_user)
                last_password_changed_date = secured_login_obj.last_password_change_date
                prev_passwords = secured_login_obj.previous_password_hashes
                prev_passwords = json.loads(prev_passwords)

                if temp_user.password_change_duration and timezone.now() > (last_password_changed_date + datetime.timedelta(days=int(temp_user.password_change_duration))):
                    password_change_flag = True

                if temp_user.is_first_login and len(prev_passwords["password_hash"]) <= 1:
                    password_change_flag = True

                if password_change_flag == True:
                    response['status'] = 401
                    response[
                        'message'] = 'Your password has expired! please reset your password'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
            
            else:
                response["status"] = 303
                response["message"] = "Username is Invalid"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if str(captcha) == str(captcha_key):
                user = authenticate(username=username, password=password)
                is_sandbox_user = user.is_sandbox_user
                response["is_sandbox_user"] = is_sandbox_user
                # checking for expired credentials for sandbox user

                # Check for Cobrowse User
                if easyassist_check_for_admin_expired_credentials(user, CobrowseAgent, CobrowseSandboxUser):
                    response['status'] = 303
                    response[
                        'message'] = 'Your credentials are expired, to use it, please contact the team'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                # Check for Account Active Cobrowse User
                if easyassist_is_active_user(user, CobrowseAgent) == False:
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
                    
                if is_sandbox_user:
                    # Check for EasyChat User
                    if check_for_expired_credentials(user, SandboxUser):
                        response['status'] = 303
                        response[
                            'message'] = 'Your credentials are expired, please request again for access'
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)
                
                if username != "":
                    otp_details_objs = EasyChatOTPDetails.objects.filter(
                        user=temp_user, email_id=username)

                    if otp_details_objs.exists():
                        otp_details_obj = otp_details_objs.first()
                        time_difference = (
                            timezone.now() - otp_details_obj.otp_sent_on).total_seconds()
                        if time_difference < 60:
                            response["status"] = 304
                            response["message"] = "Please wait Atleast 60 seconds before Resending OTP"
                            custom_encrypt_obj = CustomEncrypt()
                            response = custom_encrypt_obj.encrypt(json.dumps(response))
                            return Response(data=response)
                    else:
                        logger.info("Creating new OTP Details Object: %s: %s", extra={'AppName': 'EasyChat', 'user_id': str(
                            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        otp_details_obj = EasyChatOTPDetails.objects.create(
                            user=temp_user, email_id=username)

                    otp = random.randrange(10**5, 10**6)
                    token = uuid.uuid4()

                    otp_details_obj.otp = otp
                    otp_details_obj.is_expired = False
                    otp_details_obj.otp_sent_on = timezone.now()
                    otp_details_obj.token = token
                    otp_details_obj.save()

                    response["otp_access_token"] = str(token)

                    try:
                        send_login_otp_mail(username, temp_user.name(), otp)
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("Error LoginOTPAPI %s at %s",
                                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                    response["status"] = 200

                else:
                    response["status"] = 303
                    response["message"] = "Username is Invalid"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
            else:
                response['status'] = 302

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LoginOTPAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            if temp_user != None:
                secured_login = SecuredLogin.objects.get(user=temp_user)
                secured_login.last_attempt_datetime = timezone.now()
                if secured_login.failed_attempts > 5:
                    response["status"] = 301
                else:
                    secured_login.failed_attempts = secured_login.failed_attempts + 1
                secured_login.save()

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class ResendLoginOTPAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            user_name = data['user_name']
            user_name = validation_obj.remo_html_from_string(user_name).strip()
            otp_access_token = data["otp_access_token"]
            otp_access_token = validation_obj.remo_html_from_string(
                otp_access_token).strip()

            user_obj = User.objects.filter(
                username=user_name, is_active=True).first()

            if not user_obj:
                response['status'] = 301
                response['status_message'] = "User with Username " + \
                    user_name + " Does not exists."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            otp_access_token = uuid.UUID(otp_access_token)
            otp_details_obj = EasyChatOTPDetails.objects.filter(
                user=user_obj, token=otp_access_token).first()

            if not otp_details_obj:
                response["status"] = 301
                response["status_message"] = "Thier was Some Error in Resending The OTP , Please Refresh and Try Again"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            time_difference = (
                timezone.now() - otp_details_obj.otp_sent_on).total_seconds()
            if time_difference < 60:
                response["status"] = 301
                response["status_message"] = "Please wait Atleast 60 seconds before Resending OTP"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            otp = random.randrange(10**5, 10**6)

            otp_details_obj.otp = otp
            otp_details_obj.otp_sent_on = timezone.now()
            otp_details_obj.save()

            try:
                send_login_otp_mail(user_name, user_obj.name(), otp)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error ResendLoginOTPAPI %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ResendLoginOTPAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ResendLoginOTP = ResendLoginOTPAPI.as_view()


class CreateIntentFromClustersAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            sentences_list = data['selected_sentences']
            response['status'] = 200
            return render(request, "EasyChatApp/platform/edit_intent.html", {'sentences_list': sentences_list})
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateIntentFromClustersAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return Response(data=response)


class QueryAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def delete__token_ids(self):
        today_date_time = timezone.now()
        easychat_token_objs = EasyChatQueryToken.objects.filter(
            timestamp__date__lt=today_date_time.date())
        easychat_token_objs.delete()

    def get_session_id(self, request):
        try:
            HTTP_COOKIE = request.META["HTTP_COOKIE"]
            HTTP_COOKIE_LIST = HTTP_COOKIE.split(";")
            for cookie in HTTP_COOKIE_LIST:
                if cookie.find("easychat_session_id") != -1:
                    key, value = cookie.split("=")
                    return value
            return "None"
        except Exception as e:
            logger.info("Into get_session_id %s", e, extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return "None"

    def post(self, request, *args, **kwargs):
        response = {}
        import urllib.parse
        bot_id = ""
        channel = ""
        try:
            logger.info("Into QueryAPI...", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            is_mobile = False
            if request.user_agent.is_mobile:
                is_mobile = True

            user_id = data['user_id']

            user_id = validation_obj.remo_html_from_string(user_id)

            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(str(bot_id))

            message = data['message']
            message = validation_obj.remo_html_from_string(message)
            message = validation_obj.remo_unwanted_characters_from_message(
                message, int(bot_id))

            query_token_id = data["query_token_id"]
            selected_language = data["selected_language"]

            easychat_token_obj = EasyChatQueryToken.objects.filter(
                token=uuid.UUID(query_token_id))
            if easychat_token_obj:
                self.delete__token_ids()
            else:
                response["status_code"] = 500
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            file_attachment = json.loads(data["channel_params"])
            if file_attachment and file_attachment["attached_file_src"] != None and file_attachment["attached_file_src"] != "" and file_attachment["is_video_recorder_allowed"] == False:
                if file_attachment["file_extension"] and str(file_attachment["file_extension"].lower()) not in allowed_file_extensions:
                    response["status_code"] = 500
                    response = build_error_response(
                        "This file format is not supported. Please try uploading some other file.")
                    if selected_language != "en":
                        response = process_response_based_on_language(
                            response, selected_language, EasyChatTranslationCache)
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                file_validation_obj = EasyChatFileValidation()

                if file_validation_obj.check_malicious_file_from_content(file_attachment["attached_file_src"], allowed_file_extensions):
                    response["status_code"] = 500
                    response = build_error_response(
                        "This file format is not supported. Please try uploading some other file.")
                    if selected_language != "en":
                        response = process_response_based_on_language(
                            response, selected_language, EasyChatTranslationCache)
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            original_message = message
            restriction_of_characters_on_message = Bot.objects.get(
                pk=int(bot_id)).number_of_words_in_user_message
            try:
                original_message = original_message[
                    :restriction_of_characters_on_message]
                message = message[:restriction_of_characters_on_message]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error Restricting characters to 200 words %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                             'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
                pass

            channel = data['channel']
            channel = validation_obj.remo_html_from_string(channel)
            channel_params = data['channel_params']
            channel_params = validation_obj.remo_html_from_string(
                channel_params)
            bot_name = data['bot_name']
            bot_name = validation_obj.remo_html_from_string(bot_name)
            selected_language = "en"
            if "selected_language" in data:
                selected_language = data["selected_language"]
                selected_language = validation_obj.remo_html_from_string(
                    selected_language)

            logger.info("selected_language: %s", str(selected_language), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(selected_language), 'channel': str(channel), 'bot_id': str(bot_id)})
            logger.info("bot_id: %s", str(bot_id), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(selected_language), 'channel': str(channel), 'bot_id': str(bot_id)})
            logger.info("message: %s", str(message.encode("utf-8")), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(selected_language), 'channel': str(channel), 'bot_id': str(bot_id)})
            logger.info("selected_language: %s", str(selected_language), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(selected_language), 'channel': str(channel), 'bot_id': str(bot_id)})
            logger.info("channel: %s", str(channel), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(selected_language), 'channel': str(channel), 'bot_id': str(bot_id)})
            logger.info("channel_params: %s", str(channel_params), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(selected_language), 'channel': str(channel), 'bot_id': str(bot_id)})

            # Checking if easychat session is valid or not
            temp_channel_params = channel_params
            if not isinstance(channel_params, dict):
                temp_channel_params = json.loads(channel_params)

            easychat_session_id = temp_channel_params["session_id"]

            # In Android/iOS, we may get session id from URL Params of bot and hence in that case it
            # We simply use that session id instead of generating it from our end
            # This helps us in retaining chat history in iOS/Android
            # If it is the response of initial intent then we will not create the session unless user interacts with the bot

            if "is_initial_intent" in temp_channel_params and temp_channel_params["is_initial_intent"]:
                session_id = ""
            elif (easychat_session_id and (channel.lower().strip() == "android" or channel.lower().strip() == "ios")):
                session_id = easychat_session_id
            else:
                session_id, user_id = create_and_set_user_and_session_if_required(
                    easychat_session_id, user_id, bot_id, temp_channel_params)

            temp_channel_params["session_id"] = session_id
            temp_channel_params["is_mobile"] = is_mobile

            channel_params = json.dumps(temp_channel_params)

            # Valid easychat session id

            response = execute_query(
                user_id, bot_id, bot_name, message, selected_language, channel, channel_params, original_message)

            response["query_token_id"] = generate_query_token()
            response["session_id"] = session_id
            logger.info("Exit from QueryAPI", extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(selected_language), 'channel': str(channel), 'bot_id': str(bot_id)})

            if "language_src" in response["response"]:
                selected_language = response["response"]["language_src"]

            is_response_to_be_language_processed = True

            if "is_response_to_be_language_processed" in response["response"]:
                is_response_to_be_language_processed = response[
                    "response"]["is_response_to_be_language_processed"]

            if selected_language != "en" and is_response_to_be_language_processed:
                bot_info_obj = None
                if "bot_id" in response:
                    bot_info_obj = BotInfo.objects.filter(bot=Bot.objects.get(pk=response["bot_id"])).first()

                response = process_response_based_on_language(
                    response, selected_language, EasyChatTranslationCache, bot_info_obj)

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "[ENGINE] {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': 'None', 'channel': '', 'bot_id': 'None'})
            try:
                if type(data) != dict:
                    data = json.loads(data)
                meta_data = data
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))

            response = build_error_response(
                "We are facing some issues. Please try again later.")
            response["status_code"] = 500

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GoogleHomeQueryAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        bot_id = ""
        channel = "GoogleHome"
        try:
            validation_obj = EasyChatInputValidation()

            bot_id = str(request.GET["id"])
            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_name = 'uat'
            bot_name = validation_obj.remo_html_from_string(bot_name)
            webhook_request_packet = request.data
            webhook_response_packet = build_google_home_response(
                webhook_request_packet, bot_id, bot_name)
            response = webhook_response_packet
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "[ENGINE] {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
            try:
                if type(webhook_request_packet) != dict:
                    webhook_request_packet = json.loads(webhook_request_packet)
                meta_data = webhook_request_packet
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))
            response = DEFAULT_WEBHOOK_RESPONSE

        logger.info("response has been return", extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
        return Response(data=response)


class WhatsAppQueryAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        bot_id = ""
        channel = "WhatsApp"
        try:
            bot_id = request.GET["id"]
            validation_obj = EasyChatInputValidation()

            # if str(bot_id).strip() == "364":
            #     bot_id = 61
            bot_id = validation_obj.remo_html_from_string(str(bot_id))
            api_response = None
            received_datetime = timezone.now()
            data = request.data
            request_packet = {}
            response_packet = {}
            for key in data:
                request_packet[key] = data[key]

            request_packet["bot_id"] = bot_id

            bot_obj = Bot.objects.filter(pk=int(bot_id)).first()

            is_message_sent_to_delivery_queue = send_delivery_packet_to_sqs(request_packet, bot_obj, CampaignWhatsAppServiceProvider, CampaignBotWSPConfig)

            if is_message_sent_to_delivery_queue:
                response["status"] = 200
                response["message"] = "success"
                return Response(data=response)

            if bot_obj:
                code = get_value_from_cache(CACHE_KEY_EASYCHAT_WHATSAPP_WEBHOOK, str(bot_id))
                if not code:
                    whatsapp_webhook_obj = WhatsAppWebhook.objects.filter(
                        bot=bot_obj)
                    if not whatsapp_webhook_obj:
                        response["status"] = 101
                        response["message"] = "This channel currently not supported."
                    else:   
                        code = str(whatsapp_webhook_obj[0].function)
                        set_value_to_cache(CACHE_KEY_EASYCHAT_WHATSAPP_WEBHOOK, str(bot_id), code)
                    
                if response["status"] != 101:
                    result_dict = {}
                    exec(code, result_dict)
                    api_response = result_dict[
                        'whatsapp_webhook'](request_packet)
                    response["status"] = 200
                    response["message"] = "success"
                    response["response_packet"] = api_response
                    response_packet = api_response
            else:
                response["status"] = 101
                response["message"] = "This channel currently not supported."

            response_datetime = timezone.now()
            if bot_obj and api_response:
                whatsapp_number = api_response["mobile_number"]
                if whatsapp_number == "":
                    response["status"] = 101
                    response["message"] = "Please configure whatsapp number"
                else:
                    WhatsAppHistory.objects.create(bot=bot_obj,
                                                   mobile_number=whatsapp_number,
                                                   request_packet=json.dumps(
                                                       request_packet),
                                                   response_packet=json.dumps(
                                                       response_packet),
                                                   received_datetime=received_datetime,
                                                   response_datetime=response_datetime)
                    if api_response["status_code"] == '400':
                        check_and_send_whatsapp_endpoint_failed_mail("WhatsAppEndpoint", json.dumps(request_packet, indent=2), json.dumps(
                            request_packet, indent=2), bot_obj, BotChannel.objects.get(bot=bot_obj, channel=Channel.objects.get(name="WhatsApp")), EasyChatMAil)
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "[ENGINE] {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            try:
                if type(data) != dict:
                    data = json.loads(data)
                meta_data = data
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))

        return Response(data=response)

    def get(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            validation_obj = EasyChatInputValidation()

            bot_id = request.GET["bot_id"]
            bot_id = validation_obj.remo_html_from_string(str(bot_id))
            api_response = None
            received_datetime = timezone.now()
            data = request.GET
            request_packet = {}
            response_packet = {}
            for key in data:
                request_packet[key] = data[key]

            bot_obj = Bot.objects.filter(pk=int(bot_id)).first()
            if bot_obj:
                code = get_value_from_cache(CACHE_KEY_EASYCHAT_WHATSAPP_WEBHOOK, str(bot_id))
                if not code:
                    whatsapp_webhook_obj = WhatsAppWebhook.objects.filter(
                        bot=bot_obj)
                    if not whatsapp_webhook_obj:
                        response["status"] = 101
                        response["message"] = "This channel currently not supported."
                    else:   
                        code = str(whatsapp_webhook_obj[0].function)
                        set_value_to_cache(CACHE_KEY_EASYCHAT_WHATSAPP_WEBHOOK, str(bot_id), code)
                    
                if response["status"] != 101:
                    result_dict = {}
                    exec(code, result_dict)
                    api_response = result_dict[
                        'whatsapp_webhook'](request_packet)
                    response["status"] = 200
                    response["message"] = "success"
                    response["response_packet"] = api_response
                    response_packet = api_response
            else:
                response["status"] = 101
                response["message"] = "This channel currently not supported."

            response_datetime = timezone.now()

            if bot_obj and api_response:
                whatsapp_number = api_response["mobile_number"]
                if whatsapp_number == "":
                    response["status"] = 101
                    response["message"] = "Please configure whatsapp number"
                else:
                    WhatsAppHistory.objects.create(bot=bot_obj,
                                                   mobile_number=whatsapp_number,
                                                   request_packet=json.dumps(
                                                       request_packet),
                                                   response_packet=json.dumps(
                                                       response_packet),
                                                   received_datetime=received_datetime,
                                                   response_datetime=response_datetime)
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[ENGINE] %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        return Response(data=response)


class AlexaQueryAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        channel = "Alexa"
        try:
            validation_obj = EasyChatInputValidation()

            bot_id = str(request.GET["id"])
            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_name = 'uat'
            bot_name = validation_obj.remo_html_from_string(bot_name)
            request_packet = request.data
            response = build_alexa_response(request_packet, bot_id, bot_name)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "AlexaQueryAPI {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
            try:
                if type(request_packet) != dict:
                    request_packet = json.loads(request_packet)
                meta_data = request_packet
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))
        return Response(data=response)


AlexaQuery = AlexaQueryAPI.as_view()

"""
API Tested: ClearUserDataAPI
input queries:
    user_id: user id of easychat customer
expected output:
    status: 200 // SUCCESS
Return:
    Clears data of easychat customer from data model.
"""


class ClearUserDataAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            user_id = data['user_id']
            user_id = validation_obj.remo_html_from_string(user_id)
            logger.info("[ENGINE]: user_id: %s", str(user_id), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(bot_id)

            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)

            clear_user_data(user_id, bot_obj, 'Web')

            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ClearUserDataAPI %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class FetchBotResponseInformationAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:

            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            response_pk = data["response_pk"]
            selected_language = validation_obj.remo_html_from_string(
                data["selected_language"])
            response_list = []
            choice_list = []
            recommendation_list = []
            card_list = []
            image_list = []
            video_list = []
            modes_dict = {}
            modes_params_dict = {}

            bot_response_obj = None
            if response_pk != None or response_pk != "":
                bot_response_obj = BotResponse.objects.get(pk=int(response_pk))
                selected_language_obj = Language.objects.get(
                    lang=selected_language)

            if bot_response_obj != None:
                # Extract speech text response
                try:
                    response_list = json.loads(
                        bot_response_obj.sentence)["items"]
                    if selected_language != "en":
                        tuned_bot_response = LanguageTuningBotResponseTable.objects.get(
                            language=selected_language_obj, bot_response=bot_response_obj)
                        response_list = json.loads(
                            tuned_bot_response.sentence)["items"]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("No response %s %s", str(e),
                                   str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass

                # Images
                try:
                    image_list = json.loads(bot_response_obj.images)["items"]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("No images %s %s", str(e),
                                   str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass

                # Videos
                try:
                    video_list = json.loads(bot_response_obj.videos)["items"]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("No videos %s %s", str(e),
                                   str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass

                # Extract Choice List
                choice_pk_list = list(
                    bot_response_obj.choices.values_list('pk', flat=True))

                for choice_pk in choice_pk_list:
                    choice_obj = Choice.objects.get(pk=int(choice_pk))
                    display = choice_obj.display
                    value = choice_obj.value

                    choice_list.append({
                        "display": str(display),
                        "value": str(value)
                    })

                try:
                    recommendation_list = json.loads(
                        bot_response_obj.recommendations)["items"]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("No recommendations %s %s",
                                   str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass

                try:
                    card_list = json.loads(bot_response_obj.cards)["items"]
                    if selected_language != "en":
                        tuned_bot_response = LanguageTuningBotResponseTable.objects.get(
                            language=selected_language_obj, bot_response=bot_response_obj)
                        card_list = json.loads(
                            tuned_bot_response.cards)["items"]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("No cards %s %s", str(e),
                                   str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass

                modes_dict = json.loads(bot_response_obj.modes)
                modes_params_dict = json.loads(bot_response_obj.modes_param)

                if modes_dict == {}:
                    modes_dict = {
                        "is_typable": "true",
                        "is_button": "false",
                        "is_slidable": "false",
                        "is_date": "false",
                        "is_dropdown": "false"
                    }

                if modes_params_dict == {}:
                    modes_params_dict = {
                        "is_slidable": {
                            "max": "",
                            "min": "",
                            "step": ""
                        }
                    }

            response["response_list"] = response_list
            response["image_list"] = image_list
            response["video_list"] = video_list
            response["choice_list"] = choice_list
            response["recommendation_list"] = recommendation_list
            response["card_list"] = card_list
            response["modes"] = modes_dict
            response["modes_param"] = modes_params_dict
            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FetchBotResponseInformationAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class AutomatedTestAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            logger.info("automated testing", extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            username = request.user.username
            user_obj = User.objects.get(username=username)
            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            selected_bot_id = data["selected_bot_id"]
            selected_bot_id = validation_obj.remo_html_from_string(
                selected_bot_id)

            percentage_of_intents = data["percentage_of_intents"]
            percentage_of_intents = validation_obj.remo_html_from_string(
                percentage_of_intents)

            try:
                percentage_of_intents = int(percentage_of_intents)
            except:
                percentage_of_intents = "all"

            logger.info("automated testing", extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(selected_bot_id)})

            bot_obj = Bot.objects.get(pk=int(selected_bot_id),
                                      is_uat=True,
                                      is_deleted=False,
                                      users__in=[user_obj])

            try:
                progress_obj = AutomatedTestProgress.objects.get(
                    user=user_obj, bot=bot_obj)
                progress_obj.is_automated_testing_completed = False
                progress_obj.is_testing_stopped_in_between = False
                progress_obj.test_cases_processed = 0
                progress_obj.save()
                delete_test_result_objs_till_now(progress_obj)
            except Exception:
                pass

            t1 = threading.Thread(
                target=perform_automated_testing, args=(user_obj, bot_obj, percentage_of_intents,))
            t1.daemon = True
            t1.start()

            response["status"] = 200
            response["total_sentences"] = get_total_intent_sentence_based_on_percentage(
                bot_obj, percentage_of_intents)

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AutomatedTestAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(selected_bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class ExportAutomatedTestAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            logger.info("inside export automated testing", extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            username = request.user.username
            user_obj = User.objects.get(username=username)

            data = DecryptVariable(request.data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            selected_bot_id = data["selected_bot_id"]
            selected_bot_id = validation_obj.remo_html_from_string(
                selected_bot_id)

            email_id = data["email_id"]
            email_id = validation_obj.remo_html_from_string(
                email_id)

            bot_obj = Bot.objects.get(pk=int(selected_bot_id),
                                      is_uat=True,
                                      is_deleted=False,
                                      users__in=[user_obj])

            progress_obj = AutomatedTestProgress.objects.filter(
                user=user_obj, bot=bot_obj)

            if not progress_obj.exists():
                response["status"] = 400
                response[
                    "status_message"] = "Please First Test The Bot To Genreate Excel."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            else:
                progress_obj = progress_obj.first()

            if not validation_obj.is_valid_email(email_id):
                response["status"] = 400
                response["status_message"] = "Please Enter a Valid Email Id"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            t1 = threading.Thread(
                target=create_and_send_automated_testing_report_mail, args=(bot_obj, username, progress_obj, email_id))
            t1.daemon = True
            t1.start()

            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AutomatedTestAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(selected_bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ExportAutomatedTest = ExportAutomatedTestAPI.as_view()

"""
GetAutomatedTestingResultAPI reads from excel sheet generated by perform_automated_testing() in utils.py and
passes it over to frontend for rendering. It gets called from console.js every so often,
by renderAutomatedTestingResult()
"""


class GetAutomatedTestingResultAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args):
        response = {}
        response["status"] = 500
        try:

            username = request.user.username

            data = json.loads(request.GET["json_string"])
            validation_obj = EasyChatInputValidation()

            selected_bot_id = data["selected_bot_id"]
            selected_bot_id = validation_obj.remo_html_from_string(
                selected_bot_id)

            filter_type = data["filter_type"]
            filter_type = validation_obj.remo_html_from_string(filter_type)

            user_obj = User.objects.get(username=username)

            bot_obj = Bot.objects.get(pk=int(selected_bot_id),
                                      is_uat=True,
                                      is_deleted=False,
                                      users__in=[user_obj])

            progress_obj = AutomatedTestProgress.objects.get(
                user=user_obj, bot=bot_obj)

            filename_customer = "AutomatedTesting_Export" + \
                str(username) + "_" + str(bot_obj.pk) + ".xls"

            result_file_path = str(str(settings.MEDIA_ROOT).split(
                '/')[-2] + '/' + filename_customer)

            automated_test_result_objs = AutomatedTestResult.objects.filter(
                automated_test_progress_obj=progress_obj)

            passed_test_results = automated_test_result_objs.filter(
                status="Pass")

            test_result_details = automated_test_result_objs

            if filter_type == "1":
                test_result_details = passed_test_results

            if filter_type == "2":
                test_result_details = automated_test_result_objs.filter(
                    status="Fail")

            response["test_results_details"] = get_parsed_automated_test_result_data(
                test_result_details)

            response["total_sentences"] = automated_test_result_objs.count()
            response["correct_sentences"] = passed_test_results.count()

            response["result_bot_id"] = bot_obj.pk
            response["result_bot_name"] = bot_obj.name
            response["result_file_path"] = result_file_path

            tz = pytz.timezone(settings.TIME_ZONE)

            result_timestamp = progress_obj.last_tested_on.astimezone(tz)
            result_timestamp = str(result_timestamp.strftime("%d-%B-%Y %H:%M"))
            response["result_timestamp"] = result_timestamp

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetAutomatedTestingResultAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetAutomatedTestProgressAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            bot_id = data["selected_bot_id"]

            try:
                progress_obj = AutomatedTestProgress.objects.get(
                    user=request.user, bot=Bot.objects.get(pk=int(bot_id)))
            except Exception:
                progress_obj = None
                pass

            if progress_obj == None:
                test_cases_processed = 0
                one_test_process_time = 0
                test_cases_passed = 0
                is_automated_testing_completed = True
                is_excel_created = True
            else:
                test_cases_processed = progress_obj.test_cases_processed
                one_test_process_time = progress_obj.one_test_process_time
                test_cases_passed = progress_obj.test_cases_passed
                is_automated_testing_completed = progress_obj.is_automated_testing_completed
                is_excel_created = progress_obj.is_excel_created

            automated_test_result_objs = AutomatedTestResult.objects.filter(
                automated_test_progress_obj=progress_obj, is_processed=False)
            test_cases_processed = AutomatedTestResult.objects.filter(
                automated_test_progress_obj=progress_obj).count()
            test_cases_passed = AutomatedTestResult.objects.filter(
                automated_test_progress_obj=progress_obj, status="Pass").count()

            response["test_results_details"] = get_parsed_automated_test_result_data(
                automated_test_result_objs)

            response["test_cases_processed"] = test_cases_processed
            response["one_test_process_time"] = one_test_process_time
            response["test_cases_passed"] = test_cases_passed
            response[
                "is_automated_testing_completed"] = is_automated_testing_completed

            response["is_excel_created"] = is_excel_created
            response["status"] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetAutomatedTestProgressAPI %s at %s", str(e), str(
                exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})
            response["status"] = 500

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetAutomatedTestProgress = GetAutomatedTestProgressAPI.as_view()


class StopAutomatedTestingAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            bot_id = data["selected_bot_id"]

            try:
                progress_obj = AutomatedTestProgress.objects.get(
                    user=request.user, bot=Bot.objects.get(pk=int(bot_id)))

                progress_obj.is_testing_stopped_in_between = True
                progress_obj.is_automated_testing_completed = True
                progress_obj.save()
                response["status"] = 200

            except Exception:
                progress_obj = None
                # if progress obj is none then it implies testing is not going
                # on for this bot
                response["status"] = 300

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("StopAutomatedTestingAPI %s at %s", str(e), str(
                exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})
            response["status"] = 500

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


StopAutomatedTesting = StopAutomatedTestingAPI.as_view()


class ReRunAutomatedTestingAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)
            validation_obj = EasyChatInputValidation()

            bot_id = data["selected_bot_id"]
            bot_id = validation_obj.remo_html_from_string(
                bot_id)

            bot_obj = Bot.objects.get(pk=int(bot_id))
            test_result_obj_pk = data["test_result_obj_pk"]
            test_result_obj_pk = validation_obj.remo_html_from_string(
                test_result_obj_pk)

            test_result_obj = AutomatedTestResult.objects.get(
                pk=int(test_result_obj_pk))

            profile_user_id = "FAQAutomatedTestingUser|" + \
                str(request.user.username) + "|" + str(bot_obj.pk)

            profile_obj = Profile.objects.create(
                user_id=profile_user_id, bot=bot_obj)

            status, cause, identified_intent_objs = return_single_sentence_test_details(
                test_result_obj.original_intent, test_result_obj.query_sentence, bot_obj, profile_obj)

            test_result_obj.status = status
            test_result_obj.cause = cause
            test_result_obj.identified_intents.clear()

            progress_obj = test_result_obj.automated_test_progress_obj

            passed_objects = AutomatedTestResult.objects.filter(
                automated_test_progress_obj=progress_obj, status="Pass")

            if identified_intent_objs.exists():
                test_result_obj.identified_intents.add(
                    *identified_intent_objs)
            test_result_obj.save()

            response["status"] = 200
            response["test_result_details"] = get_parsed_automated_test_result_data([
                                                                                    test_result_obj])
            response["test_cases_passed"] = passed_objects.count()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("StopAutomatedTestingAPI %s at %s", str(e), str(
                exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})
            response["status"] = 500

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ReRunAutomatedTesting = ReRunAutomatedTestingAPI.as_view()


class GetClusterDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def strip_non_ascii(self, string):
        ''' Returns the string without non ASCII characters'''
        stripped = (c for c in string if 0 < ord(c) < 127)
        return ''.join(stripped)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        maximum_clusters = 2
        try:

            data = request.data

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            start_date = data['start_date']
            start_date = validation_obj.remo_html_from_string(start_date)
            end_date = data['end_date']
            end_date = validation_obj.remo_html_from_string(end_date)
            number_of_clusters = int(data['number_of_clusters'])

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(str(bot_id))
            bot_id = int(bot_id)

            date_format = "%Y-%m-%d"
            datetime_start = datetime.datetime.strptime(
                start_date, date_format).date()
            datetime_end = datetime.datetime.strptime(
                end_date, date_format).date()

            if datetime_end >= datetime_start:

                uat_bot_obj = Bot.objects.get(
                    pk=int(bot_id), is_uat=True, is_deleted=False)

                bot_objs = Bot.objects.filter(slug=uat_bot_obj.slug)

                user_message_list = MISDashboard.objects.filter(intent_name=None).filter(
                    creation_date__gte=datetime_start).filter(
                    creation_date__lte=datetime_end).filter(
                    bot__in=bot_objs).order_by('-date')

                maximum_clusters = user_message_list.count()

                temp_user_message_list = user_message_list

                user_message_list = []

                if uat_bot_obj.static_analytics:
                    user_message_list = SELF_LEARNING_DUMMY_MESSAGE_LIST
                else:
                    for message in temp_user_message_list:
                        user_message_list.append(
                            message.get_message_received())

                user_message_list = [self.strip_non_ascii(
                    user_message) for user_message in user_message_list if user_message != ""]

                my_stopword_list = []
                stop_words = sklearn_text.ENGLISH_STOP_WORDS.union(
                    my_stopword_list)

                vectorizer = TfidfVectorizer(stop_words=set(stop_words))
                vectorized_x = vectorizer.fit_transform(user_message_list)  # noqa: N806

                true_k = number_of_clusters

                model = KMeans(n_clusters=true_k, init='k-means++',
                               max_iter=100, n_init=1)
                model.fit(vectorized_x)

                cluster_dict = {}

                for user_message in user_message_list:
                    message = str(user_message).lower().strip()
                    vector_Y = vectorizer.transform([message])  # noqa: N806
                    prediction = model.predict(vector_Y)
                    regex_enc = r"[a-fA-F0-9]{64}"
                    if len(re.findall(regex_enc, message)) == 0 and message.strip() != "" and "**" not in message.strip():
                        if str(prediction[0]) in cluster_dict:
                            if message not in cluster_dict[str(prediction[0])]:
                                cluster_dict[
                                    str(prediction[0])].append(message)
                        else:
                            cluster_dict[str(prediction[0])] = [message]

                response["status"] = 200
                response["cluster_dict"] = cluster_dict
                response["maximum_clusters"] = maximum_clusters
                date_format = "%d-%m-%Y"
                datetime_start = datetime.datetime.strptime(
                    start_date, "%Y-%m-%d").strftime(date_format)
                datetime_end = datetime.datetime.strptime(
                    end_date, "%Y-%m-%d").strftime(date_format)
                write_excel_clusters(
                    cluster_dict, datetime_start, datetime_end)
            else:
                response["status"] = 101
                response["message"] = "Please enter valid start and end date."

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetClusterDetailsNewAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
            response["maximum_clusters"] = maximum_clusters

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


"""
API: SaveFeedbackAPI
input queries:
    user_id: user id of customer
    session_id: session id assigned to the customer for his session
    bot_id: bot pk of customer
    comments: optional --> It may be empty
    rating: rating given by livechat customer
expected output:
    status: 200 // SUCCESS
checks for:
    updates the rate value of easychat customer.
"""


class SaveFeedbackAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            user_id = data['user_id']
            user_id = validation_obj.remo_html_from_string(str(user_id))
            session_id = data['session_id']
            session_id = validation_obj.remo_html_from_string(session_id)
            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(str(bot_id))
            rating = data['rating']
            rating = validation_obj.remo_html_from_string(str(rating))
            comments = data['comments']
            comments = validation_obj.remo_html_from_string(comments)
            try:
                channel_name = data['channel_name']
            except:
                channel_name = "Web"

            bot_obj = Bot.objects.filter(pk=bot_id)[0]

            csat_feedback_form_enabled = bot_obj.csat_feedback_form_enabled
            feedback_country_code = data["feedback_country_code"]
            feedback_phone_number = ""
            feedback_email_id = ""
            checkbox_csat_clicked_list = "[]"
            channel = Channel.objects.get(name=channel_name)
            if csat_feedback_form_enabled:
                feedback_phone_number = validation_obj.remo_html_from_string(
                    str(data["feedback_phone_number"]))
                feedback_email_id = validation_obj.remo_html_from_string(
                    str(data["feedback_email_id"]))
                checkbox_csat_clicked_list = data["checkbox_csat_clicked_list"]
                Feedback.objects.create(user_id=user_id, bot=bot_obj, rating=rating, comments=comments, session_id=session_id, country_code=feedback_country_code,
                                        phone_number=feedback_phone_number, email_id=feedback_email_id, all_feedbacks=checkbox_csat_clicked_list, channel=channel, scale_rating_5=bot_obj.scale_rating_5)
            else:
                Feedback.objects.create(
                    user_id=user_id, bot=bot_obj, rating=rating, comments=comments, session_id=session_id, channel=channel, scale_rating_5=bot_obj.scale_rating_5)

            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveFeedbackAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


"""
API : SaveEasyChatIntentFeedbackAPI
input queries:
    feedback_id: user id of customer
    feedback_type: session id assigned to the customer for his session
    feedback_cnt: bot pk of customer
expected output:
    status: 200 // SUCCESS
checks for:
    This API call is used to record the user feedback for specific intent during chat.
"""


class SaveEasyChatIntentFeedbackAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            session_id = data['session_id']
            session_id = validation_obj.remo_html_from_string(
                str(session_id))

            user_id = data['user_id']
            user_id = validation_obj.remo_html_from_string(
                str(user_id))

            feedback_id = data['feedback_id']
            feedback_id = validation_obj.remo_html_from_string(
                str(feedback_id))

            feedback_type = data['feedback_type']
            feedback_type = validation_obj.remo_html_from_string(
                str(feedback_type))

            feedback_cmt = data['feedback_cmt']
            feedback_cmt = validation_obj.remo_html_from_string(
                feedback_cmt)

            mis_objs = MISDashboard.objects.filter(
                pk=feedback_id, session_id=session_id, user_id=user_id)
            if mis_objs.exists():
                # mis_objs[0].feedback_info = json.dumps(
                #     {"is_helpful": int(feedback_type), "comments": str(feedback_cmt)})
                mis_obj = mis_objs.first()
                mis_obj.is_helpful_field = feedback_type
                mis_obj.feedback_comment = str(feedback_cmt)
                mis_obj.save()
                response['status'] = 200
            else:
                response['status'] = 302

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveEasyChatIntentFeedbackAPI: %s %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class ExportExcelFAQsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:

            data = request.data

            questions = json.loads(DecryptVariable(data['questions']))
            answers = json.loads(DecryptVariable(data['answers']))

            file_url = write_excel(questions, answers)

            response['file_url'] = "/" + file_url
            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("ExportExcelFAQsAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class CreateIntentFromFAQsAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            logger.info("Thread created create_bot_with_questions_variations_answers", extra={'AppName': 'EasyChatApp', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            data = request.data

            questions = json.loads(DecryptVariable(data['questions']))

            variations = []
            for questions_iterator in range(len(questions)):
                temp_variations = "$$$".join(
                    make_final_variations(questions[questions_iterator]))
                variations.append(temp_variations)

            answers = json.loads(DecryptVariable(data['answers']))
            bot_pk = json.loads(DecryptVariable(data['bot_pk']))
            user_obj = User.objects.get(username=str(request.user.username))

            bot_obj = Bot.objects.filter(pk=int(bot_pk), users=user_obj)

            description = "Intent Created from FAQ"
            add_audit_trail(
                "EASYCHATAPP",
                user_obj,
                "Add-Intent",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )

            if bot_obj.count() == 1:
                bot_obj = bot_obj[0]
                logger.info("Thread created create_bot_with_questions_variations_answers", extra={'AppName': 'EasyChatApp', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

                # t1 = threading.Thread(
                #     target=create_bot_with_questions_variations_answers, args=(questions, variations, answers, bot_obj, user_obj,))
                # t1.daemon = True
                # t1.start()

                create_bot_with_questions_variations_answers(
                    questions, variations, answers, bot_obj, user_obj)

                response['status'] = 200
                response['message'] = "FAQs added to " + \
                    bot_obj.name + " successfully."
            else:
                response['status'] = 300
                response[
                    'message'] = "You do not have access to bot : " + bot_obj.name

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateIntentFromFAQsAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response['message'] = "Sorry! Not able to add intent!"

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class FetchFAQsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:

            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            url_html = data['url_html']
            bot_pk = data['bot_pk']

            bot_obj = Bot.objects.get(pk=int(bot_pk))
            if request.user not in bot_obj.users.all():
                response['status'] = 401
                response['message'] = 'You are not authorised to perform this operation.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            url_html = url_html.encode('ascii', errors='ignore')
            url_html = url_html.decode('ascii')

            faq_extraction_thread = threading.Thread(
                target=extract_faqs, args=[url_html, request.user, bot_obj])
            faq_extraction_thread.daemon = True
            faq_extraction_thread.start()
            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("FetchFAQsAPI %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveTimeSpentAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            user_id = data['user_id']
            session_id = data["session_id"]
            user_id = validation_obj.remo_html_from_string(user_id)
            session_id = validation_obj.remo_html_from_string(session_id)
            end_datetime = datetime.datetime.now()

            item_obj = TimeSpentByUser.objects.filter(
                user_id=user_id, session_id=session_id).last()

            if item_obj:
                item_obj.end_datetime = end_datetime
                item_obj.save()

            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveTimeSpentAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return Response(data=response)


class GetIntentListDriveAPI(APIView):  # noqa: N802
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}

        try:
            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(str(bot_id))

            bot_obj = Bot.objects.get(pk=int(bot_id))
            intent_objs = Intent.objects.filter(
                bots=bot_obj, is_deleted=False, is_hidden=False).distinct()

            intent_list = []
            for intent in intent_objs:
                intent_local = {}
                intent_local["pk"] = intent.pk
                intent_local["name"] = intent.name
                intent_list.append(intent_local)

            response["intent_objs"] = intent_list

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetIntentListDriveAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveEasyChatDataCollectAPI(APIView):  # noqa: N802

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = request.data
            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = data["json_string"]
            data = json.loads(json_string)

            bot_id = data["bot_id"]
            collect_form_data = data["collect_form_data"]
            bot_obj = Bot.objects.get(pk=int(bot_id))
            form_obj = EasyChatDataCollectForm.objects.filter(
                bot=bot_obj).order_by('-pk')[0]
            entry_obj = EasyChatDataCollect.objects.create(
                bot=bot_obj, form=form_obj)
            entry_obj.collect_form_data = json.dumps(collect_form_data)
            entry_obj.save()
            response['status'] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveEasyChatDataCollectAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        return Response(data=response)


def ShowEasyChatDataCollection(request):
    try:
        if request.user.is_authenticated and request.user.check_data_collection_permission():

            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            if not check_access_for_user(request.user, None, "EasyDataCollection Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")

            selected_bot_obj = None
            if "bot_pk" in request.GET:
                bot_pk = request.GET["bot_pk"]
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)
                if not check_access_for_user(request.user, bot_pk, "EasyDataCollection Related"):
                    return HttpResponseNotFound("You do not have access to this page")

            intent_objs = []
            if selected_bot_obj != None:
                intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], is_deleted=False, is_hidden=False)

            data_collect_form_obj = None
            try:
                data_collect_form_objs = EasyChatDataCollectForm.objects.filter(
                    bot=selected_bot_obj).order_by('-pk')
                data_collect_form_obj = data_collect_form_objs[0]
            except Exception:
                pass

            data_collect_form_ui_data = []
            if data_collect_form_obj is not None:
                data_collect_form_ui_data = json.loads(
                    data_collect_form_obj.form_ui_data)

            data_collect_obj_list = []
            if selected_bot_obj != None:
                data_collect_objs = EasyChatDataCollect.objects.filter(
                    bot__in=[selected_bot_obj], form__in=data_collect_form_objs).order_by('-pk')
                for data_collect_obj in data_collect_objs:
                    temp_form_data = json.loads(
                        data_collect_obj.collect_form_data)
                    temp_form_data['pk'] = data_collect_obj.pk
                    temp_form_data['time'] = data_collect_obj.get_datetime()
                    temp_form_data['more_info'] = False
                    if ((len(json.loads(data_collect_obj.collect_form_data)) > len(data_collect_form_ui_data)) or
                            (len(json.loads(data_collect_obj.collect_form_data)) > 3)):
                        temp_form_data['more_info'] = True
                    data_collect_obj_list.append(temp_form_data)

            total_data_objects = len(data_collect_obj_list)

            paginator = Paginator(data_collect_obj_list, 50)
            page = request.GET.get('page')

            try:
                data_collect_obj_list = paginator.page(page)
            except PageNotAnInteger:
                data_collect_obj_list = paginator.page(1)
            except EmptyPage:
                data_collect_obj_list = paginator.page(paginator.num_pages)

            user_obj = User.objects.get(username=str(username))
            # bot_objs = get_uat_bots(user_obj)
            bot_objs = user_obj.get_related_bot_objs_for_access_type(
                "Analytics Related")

            return render(request, 'EasyChatApp/show_easychat_data_collect.html', {
                'selected_bot_obj': selected_bot_obj,
                'data_collect_form_ui_data': data_collect_form_ui_data,
                "data_collect_list": data_collect_obj_list,
                "bot_objs": bot_objs,
                "total_data_objects": total_data_objects,
                "intent_objs": intent_objs
            })
        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("ShowEasyChatDataCollection %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET["bot_pk"])})
        # return HttpResponseNotFound(INVALID_REQUEST)
        return render(request, 'EasyChatApp/error_500.html')


def EasyChatDataCollectPage(request):  # noqa: N802
    selected_bot_obj = None

    if "id" in request.GET:
        bot_pk = request.GET["id"]
        selected_bot_obj = Bot.objects.get(
            pk=int(bot_pk), is_deleted=False, is_uat=True)

    form_obj = None
    try:
        form_obj = EasyChatDataCollectForm.objects.filter(
            bot=selected_bot_obj).order_by('-pk')[0]
    except Exception:
        pass

    bot_image_url = selected_bot_obj.bot_image.name

    form_ui_data = []
    if form_obj is not None:
        form_ui_data = json.loads(form_obj.form_ui_data)

    return render(request, "EasyChatApp/easychat_datacollect_form.html", {
        "form_ui_data": form_ui_data,
        "bot_image_url": bot_image_url
    })


class DeleteEasyChatDataCollectAPI(APIView):  # noqa: N802
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            date_entry_pk_list = data["date_entry_pk"].split(",")
            for date_entry_pk in date_entry_pk_list:
                if date_entry_pk.strip() != "":
                    EasyChatDataCollect.objects.get(
                        pk=int(date_entry_pk)).delete()
            response['status'] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteEasyChatDataCollectAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DownloadDataCollectionAsExcelAPI(APIView):  # noqa: N802
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            selected_bot_obj = Bot.objects.get(
                pk=int(data["bot_id"]), is_deleted=False, is_uat=True)
            automated_testing_wb = Workbook()
            # sheets_array = []
            form_objs = EasyChatDataCollectForm.objects.filter(
                bot=selected_bot_obj).order_by('-pk')
            sheet_index = 0
            for form_obj in form_objs:
                sheet_index += 1
                sheet1 = automated_testing_wb.add_sheet(
                    "Form " + str(sheet_index))
                form_label_data = json.loads(form_obj.form_ui_data)
                col_index = 0
                for data_obj in form_label_data:
                    sheet1.write(0, col_index, data_obj["input_name"])
                    sheet1.col(col_index).width = 256 * 40
                    col_index += 1
                sheet1.write(0, col_index, "Date & Time")
                sheet1.col(col_index).width = 256 * 20

                row_index = 0
                for elm_obj in EasyChatDataCollect.objects.filter(
                        bot__in=[selected_bot_obj], form__in=[form_obj]):
                    col_index = 0
                    user_input_data = json.loads(elm_obj.collect_form_data)
                    for data_obj in user_input_data:
                        sheet1.write(row_index + 1, col_index,
                                     user_input_data[data_obj]["value"])
                        col_index += 1

                    sheet1.write(row_index + 1, col_index, str(elm_obj.updated_at.astimezone(
                        tz.gettz("Asia/Kolkata")).strftime("%b %d %Y, %I:%M  %p")))

                    row_index += 1

            filename = "CollectedQuestions.xls"
            automated_testing_wb.save(
                settings.MEDIA_ROOT + filename)
            response['file_url'] = '/files/' + str(filename)
            response['status'] = 200

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DownloadDataCollectionAsExcelAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(selected_bot_obj.pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveEasyChatDataCollectFormAPI(APIView):  # noqa: N802

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = request.data
            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_pk = data["bot_pk"]
            bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)
            new_ui_data = data["form_ui_data"]
            form_obj = None
            is_create_new = False
            saturated = new_ui_data
            saturated_list = []
            for text in saturated:
                input_name = validation_obj.remo_html_from_string(
                    text["input_name"])
                input_name = validation_obj.remo_special_tag_from_string(
                    input_name)
                text["input_name"] = input_name
                saturated_list.append(text)
            new_ui_data = saturated_list
            try:
                form_obj = EasyChatDataCollectForm.objects.filter(
                    bot=bot_obj).order_by('-pk')[0]
                temp_data = json.loads(form_obj.form_ui_data)
                prev_ui_array = []
                for items in temp_data:
                    prev_ui_array.append(items["input_name"].lower())
                new_ui_array = []
                for items in new_ui_data:
                    new_ui_array.append(items["input_name"].lower())
                if prev_ui_array != new_ui_array:
                    is_create_new = True
            except Exception:
                form_obj = EasyChatDataCollectForm.objects.create(bot=bot_obj)

            if is_create_new:
                form_obj = EasyChatDataCollectForm.objects.create(bot=bot_obj)

            if form_obj is not None:
                form_obj.form_ui_data = json.dumps(new_ui_data)
                form_obj.save()
                response['status'] = 200
            else:
                response['status'] = 500

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveEasyChatDataCollectFormAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetCaptchaImageAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = request.data
            old_captcha_image = data["captcha_image"]
            old_captcha_image = DecryptVariable(old_captcha_image)
            old_captcha_image = old_captcha_image.split("/")[6].split(".")[0]
            old_captcha_image = str(old_captcha_image + ".png")
            # Get captcha image
            captcha_image = get_random_captcha_image()
            # Check if new captcha image is not same as previous
            # If yes then try again until you get diffrent captcha image
            while(str(captcha_image) == str(old_captcha_image)):
                captcha_image = get_random_captcha_image()
            captcha_image = str(
                "/static/EasyChatApp/captcha_images/" + captcha_image)
            response["captcha_image"] = captcha_image
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCaptchaImageAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class ForgotPasswordVerifyOTPAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            user_name = data['user_name']
            user_name = validation_obj.remo_html_from_string(user_name).strip()

            if not validation_obj.is_valid_email(user_name):
                response["status"] = 301
                response['status_message'] = "Username " + \
                    user_name + "Is Not a Valid Email"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            
            user_obj = User.objects.filter(
                username=user_name, is_active=True).first()

            if not user_obj:
                response['status'] = 301
                response['status_message'] = "Username " + \
                    user_name + " does not exists."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            otp_access_token = data["otp_access_token"]
            otp_access_token = validation_obj.remo_html_from_string(
                otp_access_token).strip()
            otp = data["otp"]
            otp = validation_obj.remo_html_from_string(otp).strip()

            otp_details_obj = EasyChatOTPDetails.objects.filter(
                user=user_obj, token=uuid.UUID(otp_access_token)).first()

            if not otp_details_obj:
                response["status"] = 301
                response["status_message"] = "Their was Some Error in Verifying The OTP , Please Refresh and Try Again"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            #  session is expired in 60 minutes
            if otp_details_obj.is_expired:
                response["status"] = 301
                response["status_message"] = "Your Reset Password Session Is Expired. Please Try Again in Some time."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            time_difference = (
                timezone.now() - otp_details_obj.otp_sent_on).total_seconds()
            #  session is expired in 60 minutes
            config = get_developer_console_settings()

            if time_difference > config.reset_password_details_expire_after * 60:
                otp_details_obj.is_expired = True
                otp_details_obj.save()
                response["status"] = 301
                response["status_message"] = "Your Reset Password Session is Expired Please Try Again in some time"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if otp == otp_details_obj.otp:
                otp_details_obj.is_expired = True
                otp_details_obj.save()

            else:
                response["status"] = 400
                response["status_message"] = "Incorrect/Expired OTP entered."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            reset_pass_obj = ResetPassword.objects.filter(
                user=user_obj).first()

            if reset_pass_obj:
                token = uuid.uuid4()
                reset_pass_obj.token = token
                reset_pass_obj.is_password_reseted_succesfully = False
                reset_pass_obj.save()
            else:
                reset_pass_obj = ResetPassword.objects.create(user=user_obj)

            time_difference = (
                timezone.now() - reset_pass_obj.last_request_datetime).total_seconds()
            if (reset_pass_obj.total_attempts >= 5) and (time_difference < (24 * 60 * 60)):
                reset_pass_obj.total_attempts = reset_pass_obj.total_attempts + 1
                response["status"] = 301
                response["status_message"] = "You have crossed the maximum limit of 5 attempts. Please try again later."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            else:
                if(reset_pass_obj.total_attempts > 5):
                    reset_pass_obj.total_attempts = 0
                reset_pass_obj.total_attempts = reset_pass_obj.total_attempts + 1
                reset_pass_obj.last_request_datetime = timezone.now()
            reset_pass_obj.save()

            host_url = EASYCHAT_HOST_URL
            access_token = reset_pass_obj.token
            reset_password_link = host_url + \
                "/chat/reset-forgot-password/?token=" + str(access_token)

            send_reset_password_mail(
                user_name, reset_password_link, user_obj.name())

            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ForgotPasswordVerifyOTPAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ForgotPasswordVerifyOTP = ForgotPasswordVerifyOTPAPI.as_view()


class ForgotPasswordResendOTPAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            user_name = data['user_name']
            user_name = validation_obj.remo_html_from_string(user_name).strip()

            user_obj = User.objects.filter(
                username=user_name, is_active=True).first()

            if not user_obj:
                response['status'] = 301
                response['status_message'] = "User with Username " + \
                    user_name + " Does not exists."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            otp_access_token = data["otp_access_token"]
            otp_access_token = validation_obj.remo_html_from_string(
                otp_access_token).strip()
            
            otp_access_token = uuid.UUID(otp_access_token)
            otp_details_obj = EasyChatOTPDetails.objects.filter(
                user=user_obj, token=otp_access_token).first()

            if not otp_details_obj:
                response["status"] = 301
                response["status_message"] = "Thier was Some Error in Resending The OTP , Please Refresh and Try Again"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            #  session is expired in 60 minutes
            if otp_details_obj.is_expired:
                response["status"] = 301
                response["status_message"] = "Your Reset Password Session Is Expired. Please Try Again in Some time."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            time_difference = (
                timezone.now() - otp_details_obj.otp_sent_on).total_seconds()
            if time_difference < 30:
                response["status"] = 301
                response["status_message"] = "Please wait Atleast 30 seconds before Resending OTP"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            config = get_developer_console_settings()

            if time_difference > config.reset_password_details_expire_after * 60:
                response["status"] = 304
                response["status_message"] = "Your Reset Password Session is Expired Please Try Again in some time"
                otp_details_obj.is_expired = True
                otp_details_obj.save()
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            otp = random.randrange(10**5, 10**6)

            otp_details_obj.otp = otp
            otp_details_obj.otp_sent_on = timezone.now()
            otp_details_obj.save()

            send_forgot_password_otp_mail(user_name, user_obj.name(), otp)

            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetCaptchaImageAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


ForgotPasswordResendOTP = ForgotPasswordResendOTPAPI.as_view()


class CheckUserExistsAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            user_name = data['user_name']
            user_name = validation_obj.remo_html_from_string(user_name).strip()
            user_name = "".join(user_name.split())

            if not validation_obj.is_valid_email(user_name):
                response["status"] = 303
                response["status_message"] = "Username is not a valid Email id"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            user_captcha = validation_obj.remo_html_from_string(
                str(data['captcha']))
            captcha_image = validation_obj.remo_html_from_string(
                data['captcha_image'])
            captcha_key = captcha_image.split('.')[0]
            captcha_key = next(item for item in captcha_image_dict if item[
                               "key"] == captcha_key)
            captcha_key = captcha_key["value"]

            if str(captcha_key) != str(user_captcha):
                response["status"] = 304
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            logger.info("CheckUserExistsAPI: user_name: %s", str(user_name), extra={
                        'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            user_obj = User.objects.filter(
                username=user_name, is_active=True).first()

            if not user_obj:
                response["status"] = 303
                response['status_message'] = "User with Username " + \
                    user_name + " Does not exists."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if user_obj.is_sandbox_user:
                if not SandboxUser.objects.filter(username=user_name).count():
                    response["status"] = 303
                    response["status_message"] = "Sandbox User does Not exist with username : " + user_name
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            user_email = ""
            if validation_obj.is_valid_email(user_name):
                user_email = user_name
            elif validation_obj.is_valid_email(user_obj.email.strip()):
                user_email = user_obj.email.strip()

            logger.info("CheckUserExistsAPI: email_id: %s",
                        str(user_email), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            if user_email != "":
                otp_details_objs = EasyChatOTPDetails.objects.filter(
                    user=user_obj, email_id=user_email)

                if otp_details_objs.exists():
                    otp_details_obj = otp_details_objs.first()
                else:
                    logger.info("Creating new OTP Details Object: %s: %s", extra={'AppName': 'EasyChat', 'user_id': str(
                        request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    otp_details_obj = EasyChatOTPDetails.objects.create(
                        user=user_obj, email_id=user_email)

                time_difference = (
                    timezone.now() - otp_details_obj.otp_sent_on).total_seconds()
                if time_difference < 30:
                    response["status"] = 303
                    response["status_message"] = "Please wait Atleast 30 seconds before Resending OTP"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                otp = random.randrange(10**5, 10**6)
                token = uuid.uuid4()

                otp_details_obj.otp = otp
                otp_details_obj.is_expired = False
                otp_details_obj.otp_sent_on = timezone.now()
                otp_details_obj.token = token
                otp_details_obj.save()

                response["otp_access_token"] = str(token)

                send_forgot_password_otp_mail(user_email, user_obj.name(), otp)

                response["status"] = 200

            else:
                response["status"] = 303
                response["status_message"] = "Username is Invalid"

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CheckUserExistsAPI %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class VerifyResetPasswordCodeAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            user_name = data['user_name']
            verification_code = data['verification_code']

            user_name = validation_obj.remo_html_from_string(user_name)
            verification_code = validation_obj.remo_html_from_string(
                verification_code)

            try:
                user = User.objects.get(username=user_name)
                reset_pass_obj = ResetPassword.objects.get(user=user)
                time_difference = (
                    timezone.now() - reset_pass_obj.last_attempt_datetime).seconds
                if time_difference < 300:
                    if reset_pass_obj.failed_attempts < 3:
                        if verification_code == reset_pass_obj.reset_pass_verifycode:
                            reset_pass_obj.failed_attempts = 0
                            reset_pass_obj.save()
                            response['status'] = 200
                        else:
                            reset_pass_obj.failed_attempts += 1
                            reset_pass_obj.save()
                            reset_pass_obj = ResetPassword.objects.get(
                                user=user)
                            response['status'] = 302
                            response['attempts_remaining'] = 3 - \
                                reset_pass_obj.failed_attempts
                    else:
                        response['status'] = 303
            except Exception:
                logger.info("VerifyResetPasswordCodeAPI: user_name: %s does not exist : %s", str(
                    user_name), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error VerifyResetPasswordCodeAPI %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveNewPasswordAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            user_name = data['user_name']
            verification_code = data['verification_code']
            new_password = data['new_password']

            user_name = validation_obj.remo_html_from_string(user_name)
            verification_code = validation_obj.remo_html_from_string(
                verification_code)
            new_password = validation_obj.remo_html_from_string(new_password)

            try:
                user = User.objects.get(username=user_name)
                secured_login_object = SecuredLogin.objects.get(user=user)
                reset_pass_obj = ResetPassword.objects.get(user=user)
                if reset_pass_obj.failed_attempts < 4:
                    if verification_code == reset_pass_obj.reset_pass_verifycode:
                        user.password = new_password
                        secured_login_object.last_password_change_date = timezone.now()
                        previous_password_hashes = json.loads(
                            secured_login_object.previous_password_hashes)

                        for hashed_password in previous_password_hashes["password_hash"]:
                            if check_password(new_password, hashed_password) == True:
                                response["status"] = 401
                                response[
                                    "message"] = "password previously used"
                                custom_encrypt_obj = CustomEncrypt()
                                response = custom_encrypt_obj.encrypt(
                                    json.dumps(response))
                                return Response(data=response)

                        if len(previous_password_hashes["password_hash"]) == 0:
                            previous_password_hashes["password_hash"].append(
                                make_password(user.password))
                        if len(previous_password_hashes["password_hash"]) >= 5:
                            previous_password_hashes["password_hash"].pop(0)
                        previous_password_hashes["password_hash"].append(
                            make_password(new_password))
                        secured_login_object.previous_password_hashes = json.dumps(
                            previous_password_hashes)
                        secured_login_object.save()
                        user.save()

                        description = "User password added"
                        add_audit_trail(
                            "EASYCHATAPP",
                            user,
                            "Update-Password",
                            description,
                            json.dumps(data),
                            request.META.get("PATH_INFO"),
                            request.META.get('HTTP_X_FORWARDED_FOR')
                        )
                        response['status'] = 200
            except Exception:
                logger.info("SaveNewPasswordAPI: user_name: %s does not exist : %s", str(
                    user_name), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveNewPasswordAPI %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class CropAndSaveImageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)

            dimension_x = data["x"]
            dimension_y = data["y"]
            width = data["width"]
            height = data["height"]
            image_path = data["image_path"]
            target_path = data["target_path"]

            # host_domain = str(str(request.META.get('HTTP_HOST')) + "/")
            image_path = "files/" + image_path.split('files/', 1)[1]
            target_path = "files/" + target_path.split('files/', 1)[1]

            image = Image.open(image_path)
            cropped_image = image.crop(
                (dimension_x, dimension_y, dimension_x + width, dimension_y + height))
            cropped_image.save(target_path)

            response["status"] = 200
            logger.info("CropAndSaveImageAPI %s croppped", image_path, extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CropAndSaveImageAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetImageDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)

            image_path = data["image_path"]

            image_objs = ImageData.objects.filter(image_path=image_path)

            if image_objs.count() == 0:
                response["status"] = 300
                logger.info("GetImageDataAPI %s image not exist", image_path, extra={'AppName': 'EasyChat', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            else:
                response["status"] = 200
                image_obj = image_objs[0]
                response["x"] = image_obj.left
                response["y"] = image_obj.right
                response["width"] = image_obj.width
                response["height"] = image_obj.height
                logger.info("GetImageDataAPI %s image data sent", image_path, extra={'AppName': 'EasyChat', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetImageDataAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SetImageDataAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)

            dimension_x = int(data["x"])
            dimension_y = int(data["y"])
            width = int(data["width"])
            height = int(data["height"])
            image_path = data["image_path"]

            image_objs = ImageData.objects.filter(image_path=image_path)

            if image_objs.count() == 0:
                response["status"] = 200
                ImageData.objects.create(
                    image_path=image_path, left=dimension_x, right=dimension_y, width=width, height=height)
                logger.info("SetImageDataAPI %s image data added", image_path, extra={'AppName': 'EasyChat', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            else:
                response["status"] = 200
                image_obj = image_objs[0]
                image_obj.left = dimension_x
                image_obj.right = dimension_y
                image_obj.width = width
                image_obj.height = height
                image_obj.save()
                logger.info("SetImageDataAPI %s image data updated x = %s y = %s, width = %s, height = %s", image_path, str(dimension_x), str(dimension_y), str(width), str(
                    height), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SetImageDataAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetPreviousSessionResponseAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)

            session_id = data["session_id"]
            bot_id = data["bot_id"]
            bot_obj = Bot.objects.get(pk=int(bot_id))

            bot_info_obj = get_bot_info_object(bot_obj)

            is_previous_chat_history_required = bot_info_obj.is_bot_chat_history_to_be_shown_on_refresh

            prev_session_response = []
            if is_previous_chat_history_required:
                mis_objs = MISDashboard.objects.filter(
                    session_id=session_id, bot=bot_obj).order_by('date')
                for mis_obj in mis_objs:
                    attach_file_src = ""
                    file_name = ""
                    response_json = mis_obj.response_json
                    message_received = mis_obj.get_message_received()
                    if mis_obj.attachment:
                        try:
                            attach_file_src = mis_obj.attachment
                            file_key = mis_obj.attachment.split("/")[-2]
                            file_obj = EasyChatAppFileAccessManagement.objects.get(
                                key=file_key, is_expired=False)
                            file_name = file_obj.file_path.split("/")[-1]
                        except Exception as e:
                            file_name = str(attach_file_src).split("/")[-1]
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("GetPreviousSessionResponseAPI %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id':
                                                                                                                         'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    if response_json != "":
                        prev_session_response.append(
                            {
                                'message_received': message_received,
                                'response_json': json.loads(response_json),
                                'message_sent': mis_obj.get_bot_response_with_html_tags_intact(),
                                "date_time": mis_obj.get_datetime(),
                                "attached_file_src": attach_file_src,
                                "attached_file_name": file_name,
                                "selected_language": mis_obj.selected_language.lang, 
                            }
                        )

            response["prev_session_response"] = prev_session_response
            response["is_previous_chat_history_required"] = is_previous_chat_history_required
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetPreviousSessionResponseAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetPreviousSessionResponse = GetPreviousSessionResponseAPI.as_view()


def NLPBenchmarkConsole(request):  # noqa: N802
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        username = request.user.username
        user_obj = User.objects.get(username=str(username))

        if "getcogno.ai" not in user_obj.username:
            # return HttpResponse("INVALID_REQUEST")
            return render(request, 'EasyChatApp/error_404.html')

        validation_obj = EasyChatInputValidation()

        selected_bot_obj = None
        if "bot_pk" in request.GET:
            bot_pk = request.GET["bot_pk"]
            bot_pk = validation_obj.remo_html_from_string(str(bot_pk))
            selected_bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False, is_uat=True)

        if selected_bot_obj == None:
            return render(request, 'EasyChatApp/error_404.html')

        context = {
            "selected_bot_obj": selected_bot_obj,
        }

        return render(request, 'EasyChatApp/platform/nlp_benchmark.html', context)
    else:
        return HttpResponseRedirect("/chat/login/")


"""
NLPBenchmarkingAPI executes perform_nlp_benchmarking functin defined in utils.py in a thread
"""


class NLPBenchmarkingAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            logger.info("nlp benchmarking", extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            username = request.user.username
            user_obj = User.objects.get(username=username)
            data = request.data

            uploaded_file = data['my_file']

            if uploaded_file.name.find("<") != -1 or uploaded_file.name.find(">") != -1 or uploaded_file.name.find("=") != -1:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            file_validation_obj = EasyChatFileValidation()

            if file_validation_obj.check_malicious_file(uploaded_file.name):
                response["status"] = 101
                response[
                    "message"] = "Kindly upload file in xls or xlsx format. Please do not use .(dot) except in filename for extension."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            file_name = get_dot_replaced_file_name(uploaded_file.name)
            path = default_storage.save(
                file_name, ContentFile(uploaded_file.read()))

            file_extension = path.split(".")[-1]

            if file_extension.lower() not in ["xls", "xlsx"]:
                response["status"] = 101
                response["message"] = "Kindly upload file in xls or xlsx format."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            validation_obj = EasyChatInputValidation()

            selected_bot_id = data["selected_bot_id"]
            selected_bot_id = validation_obj.remo_html_from_string(
                selected_bot_id)

            logger.info(selected_bot_id, extra={'AppName': 'EasyChat', 'user_id': str(
                request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(selected_bot_id)})

            bot_obj = Bot.objects.get(pk=int(selected_bot_id),
                                      is_uat=True,
                                      is_deleted=False,
                                      users__in=[user_obj])

            thread_process = threading.Thread(
                target=perform_nlp_benchmarking, args=(user_obj, bot_obj, request, path))
            thread_process.daemon = True
            thread_process.start()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error NLPBenchMarkingAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(selected_bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


"""
GetNLPBenchmarkingResultAPI reads from excel sheet generated by perform_nlp_benchmarking() in utils.py and
passes it over to frontend for rendering. It gets called from console.js every so often,
by renderNLPBenchmarking()
"""


class GetNLPBenchmarkingResultAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args):
        response = {}
        response["status"] = 500
        try:

            username = request.user.username
            selected_bot_id = request.GET["selected_bot_id"]
            filename = "NLPBenchmarking_" + \
                str(username).replace('.', '-') + \
                "_" + selected_bot_id + ".xls"

            nlp_benchmarking_wb = xlrd.open_workbook(
                settings.MEDIA_ROOT + filename)
            benchmarking_results = nlp_benchmarking_wb.sheet_by_name(
                "NLP Benchmarking Result")
            benchmarking_analytics = nlp_benchmarking_wb.sheet_by_name(
                "NLP Benchmarking Analytics")
            benchmarking_errors = nlp_benchmarking_wb.sheet_by_name(
                "List of intents not in bot")

            rows_limit = benchmarking_results.nrows

            user_query_list = []
            ideal_intent_name_list = []
            identified_intent_name_list = []
            not_found_intent_list = []
            total_queries_length = int(benchmarking_analytics.cell_value(1, 0))
            correct_queries_length = int(
                benchmarking_analytics.cell_value(1, 1))

            try:
                result_accuracy = str(benchmarking_analytics.cell_value(1, 2))
                result_timestamp = str(benchmarking_analytics.cell_value(1, 5))
                result_file_path = str(benchmarking_analytics.cell_value(1, 6))
            except Exception:
                pass

            for index in range(1, rows_limit):
                sentence = benchmarking_results.cell_value(index, 0)
                ideal_intent_name = benchmarking_results.cell_value(index, 1)
                identified_intent_name = benchmarking_results.cell_value(
                    index, 2)

                user_query_list.append(sentence)
                ideal_intent_name_list.append(ideal_intent_name)
                identified_intent_name_list.append(identified_intent_name)

            rows_limit = benchmarking_errors.nrows

            for index in range(1, rows_limit):
                not_found_intent_list.append(
                    benchmarking_errors.cell_value(index, 0))

            response["user_query_list"] = user_query_list
            response["ideal_intent_name_list"] = ideal_intent_name_list
            response["identified_intent_name_list"] = identified_intent_name_list
            response["total_queries_length"] = total_queries_length
            response["correct_queries_length"] = correct_queries_length
            response["result_file_path"] = result_file_path
            response["result_timestamp"] = result_timestamp
            response["result_accuracy"] = result_accuracy
            response["not_found_intent_list"] = not_found_intent_list

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetNLPBenchmarkingResultAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


"""
    API : SetSessionTimeLimitAPI
    is user in request is valid and authenticated
    then set session of that user to
"""


class SetSessionTimeLimitAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            user = User.objects.get(username=request.user.username)
            user.is_online = True
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SetSessionTimeLimitAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetBotListAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            user_obj = User.objects.get(username=request.user.username)
            bot_objs = user_obj.get_related_bot_objs_for_access_type(
                "Analytics Related")
            bot_obj_list = {}
            for bot_obj in bot_objs:
                bot_obj_list[bot_obj.name] = bot_obj.pk
            response["status"] = 200
            response["bot_obj_list"] = bot_obj_list
            logger.info("GetBotListAPI response = %s",
                        str(response), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetBotListAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return Response(data=response)


def SsoMetaData(request):
    try:
        if request.user.is_authenticated and request.user.check_sso_permission():
            return render(request, 'EasyChatApp/platform/sso_metdata.html')
        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("SsoMetaData %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None'})
        return render(request, 'EasyChatApp/error_500.html')


class UploadAttachmentAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["name"] = "no_name"
        response["src"] = "error"

        try:
            data = request.data["Request"]
            data = DecryptVariable(data)
            data = json.loads(data)

            uploaded_file = data[0]

            validation_obj = EasyChatInputValidation()

            filename = uploaded_file["filename"]
            filename = validation_obj.remo_html_from_string(filename)

            base64_content = uploaded_file["base64_file"]

            user_id = uploaded_file["user_id"]

            file_validation_obj = EasyChatFileValidation()

            if file_validation_obj.check_malicious_file(filename):
                response['status'] = 500
                response['status_message'] = 'Malicious File'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            file_extension = filename.split(".")[-1].lower()

            if file_extension in allowed_file_extensions:
                if file_validation_obj.check_malicious_file_from_content(base64_content, allowed_file_extensions):
                    response['status'] = 500
                    response['status_message'] = 'Malicious File'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                if not os.path.exists('secured_files/EasyChatApp/attachment'):
                    os.makedirs('secured_files/EasyChatApp/attachment')

                path = os.path.join(settings.SECURE_MEDIA_ROOT,
                                    "EasyChatApp/attachment/")

                file_name = str(uuid.uuid4()) + '.' + file_extension
                file_path = path + file_name
                fh = open(file_path, "wb")
                fh.write(base64.b64decode(base64_content))
                fh.close()

                path = '/secured_files/EasyChatApp/attachment/' + file_name

                file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
                    file_path=path, is_public=True, is_customer_attachment=True)

                preview_file_path = ""
                try:
                    preview_file_path = '/chat/access-file/' + \
                        str(file_access_management_obj.key) + \
                        "/?user_id=" + user_id
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("Inside UploadAttachmentAPI %s at %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

                file_url = '/chat/download-file/' + \
                    str(file_access_management_obj.key) + '/' + file_name

                thumbnail_file_name = ""
                if file_extension in ["png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "jfif", "JFIF", "tiff", "TIFF", "exif", "EXIF", "bmp", "BMP", "gif", "GIF"]:
                    thumbnail_file_name = create_image_thumbnail(file_name)
                elif file_extension in ["MPEG", "mpeg", "MP4", "mp4", "MOV", "mov", "AVI", "avi", "flv"]:
                    thumbnail_file_name = create_video_thumbnail(file_name)

                thumbnail_url = ""
                preview_thumbnail_url = ""

                if thumbnail_file_name != "":
                    path_of_thumbnail = "/secured_files/EasyChatApp/attachment/" + thumbnail_file_name
                    file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
                        file_path=path_of_thumbnail, is_public=True, is_customer_attachment=True)
                    thumbnail_url = '/chat/download-file/' + \
                        str(file_access_management_obj.key) + \
                        '/' + thumbnail_file_name
                    preview_thumbnail_url = '/chat/access-file/' + \
                        str(file_access_management_obj.key) + \
                        "/?user_id=" + user_id

                response["status"] = 200
                response["src"] = file_url
                response["name"] = file_name
                response["thumbnail_url"] = thumbnail_url
                response["preview_file_path"] = preview_file_path
                response["preview_thumbnail_url"] = preview_thumbnail_url

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Inside UploadAttachmentAPI %s at %s", str(
                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


def FileAccess(request, file_key, file_name):
    comes_from_excel = False
    if "source" in request.GET:
        comes_from_excel = True
    if not request.user.is_authenticated and comes_from_excel == False:
        return HttpResponse("Invalid Request")

    file_access_management_obj = None
    try:
        file_access_management_obj = EasyChatAppFileAccessManagement.objects.get(
            key=file_key)

        path_to_file = file_access_management_obj.file_path

        filename = path_to_file.split("/")[-1]

        path_to_file = settings.BASE_DIR + path_to_file

        mime_type, _ = mimetypes.guess_type(path_to_file)

        if os.path.exists(path_to_file):
            with open(path_to_file, 'rb') as fh:
                response = HttpResponse(
                    fh.read(), status=200, content_type=mime_type)
                response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(
                    str(filename))
                # response['X-Sendfile'] = smart_str(path_to_file)
                # response['X-Accel-Redirect'] = path_to_file
                return response

        return HttpResponse(status=401)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error FileAccess %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})
    return HttpResponse(status=404)


def LandingPage(request):
    try:
        if not request.user.is_authenticated:
            return HttpResponseRedirect("/chat/login/")

        logger.info("Into LandingPage....", extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        bot_id = request.GET["bot_pk"]
        selected_bot_obj = Bot.objects.get(pk=bot_id)
        show_bot_icon_and_link = True

        return render(request, 'EasyChatApp/console.html', {
            "selected_bot_obj": selected_bot_obj,
            "show_bot_icon_and_link": show_bot_icon_and_link
        })

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("LandingPage %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        # return HttpResponse("500")
        return render(request, 'EasyChatApp/error_500.html')


class SaveBotClickCountAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_id = data['bot_id']
            bot_web_page = data["bot_web_page"]
            web_page_source = data["web_page_source"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            bot_web_page = validation_obj.remo_html_from_string(bot_web_page)
            web_page_source = validation_obj.remo_html_from_string(
                web_page_source)
            bot_obj = Bot.objects.get(pk=bot_id)
            page_url_without_params = bot_web_page.split('?')[0]
            traffic_source = TrafficSources.objects.filter(
                web_page=page_url_without_params, visiting_date=datetime.datetime.today().date(), bot=bot_obj, web_page_source__iexact=web_page_source)
            if traffic_source:
                traffic_source[0].bot_clicked_count = traffic_source[
                    0].bot_clicked_count + 1
                traffic_source[0].save()
            else:
                origin = urlparse(bot_web_page)
                if origin.netloc not in settings.ALLOWED_HOSTS:
                    TrafficSources.objects.create(
                        web_page=page_url_without_params, web_page_visited=1, bot_clicked_count=1, bot=bot_obj, web_page_source=web_page_source)

            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveBotClickCountAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveWelcomeBannerClickCountAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_id = data['bot_id']
            user_id = data["user_id"]
            web_page_visited = data["web_page_visited"]
            preview_source = data["preview_source"]
            wb_id = data["wb_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            web_page_visited = validation_obj.remo_html_from_string(
                web_page_visited)
            preview_source = validation_obj.remo_html_from_string(
                preview_source)
            wb_id = validation_obj.remo_html_from_string(wb_id)
            bot_obj = Bot.objects.get(pk=bot_id)
            wb_obj = WelcomeBanner.objects.get(pk=wb_id)

            user = Profile.objects.filter(user_id=user_id, bot=bot_obj).first()
            if not user:
                user_id = str(uuid.uuid4())
                user = Profile.objects.create(user_id=user_id, bot=bot_obj)

            try:
                welcomeBannerClicks = WelcomeBannerClicks.objects.get(
                    web_page_visited=web_page_visited, visiting_date=datetime.datetime.today().date(), bot=bot_obj, preview_source__iexact=preview_source, intent=wb_obj.intent)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("SaveWelcomeBannerClickCountAPI: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                               'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                welcomeBannerObj = WelcomeBannerClicks.objects.create(
                    web_page_visited=web_page_visited, bot=bot_obj, preview_source=preview_source, intent=wb_obj.intent)
                welcomeBannerObj.user_id.add(user)
                response['status'] = 200
                response["message"] = "Row added successfully."
                response["user_id"] = user_id
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            welcomeBannerClicks.user_id.add(user)
            welcomeBannerClicks.save()
            response['status'] = 200
            response["message"] = "User id appended successfully."
            response["user_id"] = user_id

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveWelcomeBannerClickCountAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SetSessionTimeLimit = SetSessionTimeLimitAPI.as_view()

GetCaptchaImage = GetCaptchaImageAPI.as_view()

CheckUserExists = CheckUserExistsAPI.as_view()

VerifyResetPasswordCode = VerifyResetPasswordCodeAPI.as_view()

SaveNewPassword = SaveNewPasswordAPI.as_view()

SaveEasyChatDataCollectForm = SaveEasyChatDataCollectFormAPI.as_view()

DownloadDataCollectionAsExcel = DownloadDataCollectionAsExcelAPI.as_view()

DeleteEasyChatDataCollect = DeleteEasyChatDataCollectAPI.as_view()

SaveEasyChatDataCollect = SaveEasyChatDataCollectAPI.as_view()

Query = QueryAPI.as_view()

GoogleHomeQuery = GoogleHomeQueryAPI.as_view()

ClearUserData = ClearUserDataAPI.as_view()

LoginSubmit = LoginSubmitAPI.as_view()

LoginOTP = LoginOTPAPI.as_view()

FetchBotResponseInformation = FetchBotResponseInformationAPI.as_view()

AutomatedTest = AutomatedTestAPI.as_view()

GetAutomatedTestingResult = GetAutomatedTestingResultAPI.as_view()

GetClusterDetails = GetClusterDetailsAPI.as_view()

SaveFeedback = SaveFeedbackAPI.as_view()

ExportExcelFAQs = ExportExcelFAQsAPI.as_view()

CreateIntentFromFAQs = CreateIntentFromFAQsAPI.as_view()

FetchFAQs = FetchFAQsAPI.as_view()

CreateIntentFromClusters = CreateIntentFromClustersAPI.as_view()

WhatsAppQuery = WhatsAppQueryAPI.as_view()

SaveTimeSpent = SaveTimeSpentAPI.as_view()

GetIntentListDrive = GetIntentListDriveAPI.as_view()

SaveEasyChatIntentFeedback = SaveEasyChatIntentFeedbackAPI.as_view()

CropAndSaveImage = CropAndSaveImageAPI.as_view()

NLPBenchmarking = NLPBenchmarkingAPI.as_view()

GetNLPBenchmarkingResult = GetNLPBenchmarkingResultAPI.as_view()

GetImageData = GetImageDataAPI.as_view()

SetImageData = SetImageDataAPI.as_view()

GetBotList = GetBotListAPI.as_view()

UploadAttachment = UploadAttachmentAPI.as_view()

SaveBotClickCount = SaveBotClickCountAPI.as_view()

SaveWelcomeBannerClickCount = SaveWelcomeBannerClickCountAPI.as_view()


@permission_classes([IsAuthenticated])
def EasyChatShareableBotLink(request, bot_id):
    try:
        logger.info("Into EasyChatShareableBotLink....", extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
        bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)

        integrated_whatsapp_mobile = ""
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=Channel.objects.get(name="WhatsApp"))
        if bot_channel_obj.count():
            integrated_whatsapp_mobile = bot_channel_obj[
                0].integrated_whatsapp_mobile

        logger.info("Integrated mobile_number %s", str(integrated_whatsapp_mobile), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        return render(request, 'EasyChatApp/channels/bot_share.html', {"integrated_whatsapp_mobile": integrated_whatsapp_mobile, "bot_id": bot_id})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EasyChatShareableBotLink: %s at line %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET["id"])})
        # return HttpResponse("Invalid Access")
        return render(request, 'EasyChatApp/error_404.html')


class TelegramQueryAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = 500
        response["status_message"] = "Internal Server Error"
        channel = "Telegram"
        is_welcome_response = False
        try:
            channel_params = {}
            bot_name = "uat"
            bot_id = 1
            if "id" in request.GET:
                bot_id = request.GET["id"]
            logger.info(request.data, extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            data = request.data

            if "my_chat_member" in data and "chat" in data["my_chat_member"] and "type" in data["my_chat_member"]["chat"] and data["my_chat_member"]["chat"]["type"] == "supergroup":
                response["status_code"] = 200
                response["status_message"] = "Message type is supergroup."
                return Response(data=response)

            user_id = str(data["message"]["from"]["id"])
            chat_id = data["message"]["chat"]["id"]
            bot_obj = Bot.objects.get(pk=int(bot_id))
            # selected_language = "en"

            if "chat" in data["message"] and "type" in data["message"]["chat"] and data["message"]["chat"]["type"] == "supergroup":
                response["status_code"] = 200
                response["status_message"] = "Message type is supergroup."
                return Response(data=response)

            # This selected_language was not being used anywhere hence it has been commented.
            # if "language_code" in data["message"]["from"]:
            #     selected_language = data["message"]["from"]["language_code"]

            # checking if text message or media
            is_attachment = True
            if "text" in data["message"]:
                is_attachment = False
                message = data["message"]["text"]

            logger.info(user_id, extra={'AppName': 'EasyChat', 'user_id': 'None',
                                        'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            logger.info(chat_id, extra={'AppName': 'EasyChat', 'user_id': 'None',
                                        'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            logger.info(bot_id, extra={'AppName': 'EasyChat', 'user_id': 'None',
                                       'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            if not is_attachment and is_start_of_conversation(message):
                user, bot_response = build_telegram_welcome_response(
                    user_id, bot_obj, data)
                is_welcome_response = True
                EasyChatSessionIDGenerator.objects.filter(
                    user=user, is_expired=False).update(is_expired=True)
            else:
                user = set_user(user_id, "telegram", "src", "Telegram", bot_id)
                file_type = "text"
                caption = ""
                is_attachment_saved = False
                file_path = ""
                absolute_file_path = ""
                if is_attachment:
                    is_livechat = False
                    if "photo" in data["message"]:
                        file_type = "photo"
                    elif "voice" in data["message"]:
                        file_type = "voice"
                    elif "video" in data["message"]:
                        file_type = "video"
                    else:
                        file_type = "document"

                    if "caption" in data["message"]:
                        caption = data["message"]["caption"]

                    message = "attachment"
                    current_bot_object = get_bot_obj_from_data_models(user_id, bot_obj, {
                                                                      'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    
                    if not current_bot_object:
                        current_bot_object = bot_obj
                        
                    profile_obj = Profile.objects.filter(bot=current_bot_object, user_id=user_id).order_by("-pk").first()
                    if profile_obj:
                        is_livechat = profile_obj.livechat_connected

                    file_path, absolute_file_path, is_attachment_saved = get_telegram_file_attachment(
                        data["message"][file_type], bot_id, caption, file_type, int(bot_obj.max_file_size_allowed * 1024 * 1024), is_livechat)

                    if is_livechat and not is_attachment_saved:
                        file_not_save_response = build_file_not_saved_bot_response(bot_obj.max_file_size_allowed)
                        send_message_to_telegram_user(user, bot_id, file_not_save_response, chat_id, data)
                    
                    channel_params = {
                        "attached_file_path": file_path,
                        "attached_complete_file_path": absolute_file_path,
                        "is_attachment_saved": is_attachment_saved
                    }
                    
                    save_data(user, json_data={"attached_file_src": file_path},
                              src="None", channel="Telegram", bot_id=bot_id, is_cache=False)
                reverse_message = get_message_from_reverse_telegram_mapping(
                    message, user)
                if reverse_message != None:
                    message = reverse_message
                
                channel_params = json.dumps(channel_params)
                
                terminate, response = process_language_change_or_get_response(user_id, bot_id, chat_id, bot_name, channel, channel_params, message, bot_obj)
                if terminate:
                    return Response(data=response)
                bot_response = response

                if "is_livechat" in response and response["is_livechat"] == "true":
                    return HttpResponse("OK")
                
                save_bot_switch_data_variable_if_availabe(
                    user_id, bot_id, bot_response, channel)

            send_message_to_telegram_user(
                user, bot_id, bot_response, chat_id, data)

            if is_welcome_response and change_language_response_required(user_id, bot_id, bot_obj, channel):
                send_language_change_response(user_id, bot_id, chat_id, bot_obj, channel)
            response["status_code"] = 200
            response["status_message"] = "Request processed successfully."
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "[ENGINE] {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            try:
                if type(data) != dict:
                    data = json.loads(data)
                meta_data = data
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))

        return Response(data=response)


TelegramQuery = TelegramQueryAPI.as_view()


def Login(request):  # noqa: N802

    if is_allowed(request, [BOT_BUILDER_ROLE, CUSTOMER_CARE_AGENT_ROLE]):
        return HttpResponseRedirect("/chat/home")
    else:
        captcha_image = get_random_captcha_image()
        captcha_image = str(
            "/static/EasyChatApp/captcha_images/" + captcha_image)
        EasyChatAccessToken.objects.filter(is_expired=True).delete()
        easychat_access_token = EasyChatAccessToken.objects.create()

        config_obj = get_developer_console_settings()

        ms_integration_url = ""
        try:
            with open(f'{settings.MEDIA_ROOT}livechat_integrations/config.json', 'r') as config_file:
                data = json.load(config_file)

                if data['ms_dynamics']['is_integrated']:
                    url = data['ms_dynamics']['CSRF_TRUSTED_ORIGINS']

                    if len(url) != 0:
                        ms_integration_url = url[0]

                        if ms_integration_url[-1] != '/':
                            ms_integration_url += '/'
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error Fetching MS Dynamics Integration URL %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            pass

        if request.user_agent.is_mobile:
            return render(request, 'EasyChatApp/mobile_login.html', {"captcha_image": captcha_image, "easychat_access_token": easychat_access_token, "config_obj": config_obj})
        else:
            return render(request, 'EasyChatApp/login.html', {"captcha_image": captcha_image, "easychat_access_token": easychat_access_token, "config_obj": config_obj, "ms_integration_url": ms_integration_url})


def RedirectLogin(request):
    try:
        data = request.GET
        token = data["token"]
        self_signup_user = SelfSignupUser.objects.filter(
            token=uuid.UUID(token), is_completed=False)[0]

        config_obj = get_developer_console_settings()

        if request.user_agent.is_mobile:
            return render(request, 'EasyChatApp/redirect_after_login_mobile.html', {"token": self_signup_user.token, "config_obj": config_obj})

        return render(request, 'EasyChatApp/redirect_after_login.html', {"token": self_signup_user.token, "config_obj": config_obj})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error RedirectLogin Get %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return HttpResponse('Error while sending verification email.')


def PasswordSetup(request):
    if request.method == "GET":
        try:
            data = request.GET
            token = data["token"]
            self_signup_user = SelfSignupUser.objects.get(token=token)
            self_signup_user_exists = False
            if self_signup_user.is_completed:
                self_signup_user_exists = True
            if not self_signup_user_exists:
                time_zone = pytz.timezone(settings.TIME_ZONE)
                created_time = self_signup_user.timestamp_user_creation.astimezone(time_zone)
                expiration_time = (datetime.datetime.now() - timedelta(hours=SELF_SIGNUP_USER_EXPIRATION_TIME)).astimezone(time_zone)
                if created_time < expiration_time:
                    return HttpResponse('Your token has expired.')

            config_obj = get_developer_console_settings()

            if request.user_agent.is_mobile:
                return render(request, 'EasyChatApp/mobile_password_setup.html', {'self_signup_user_exists': self_signup_user_exists, "config_obj": config_obj})

            return render(request, 'EasyChatApp/password_setup.html', {'self_signup_user_exists': self_signup_user_exists, "config_obj": config_obj})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error PasswordSetup Get %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return HttpResponse('Your token has expired.')
    elif request.method == "POST":
        try:
            response = {}
            response["status"] = 500
            data = request.POST
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)
            access_token = data["access_token"]
            password_new = data["password_new"]
            self_signup_user = SelfSignupUser.objects.get(token=access_token)
            if self_signup_user.is_completed == False:
                User.objects.create(first_name=self_signup_user.firstname, last_name=self_signup_user.lastname, username=self_signup_user.email_id,
                                    password=password_new, email=self_signup_user.email_id, role=BOT_BUILDER_ROLE, status="1", is_chatbot_creation_allowed="1", is_guest=True)
                self_signup_user.is_completed = True
                self_signup_user.save()
                response["status"] = 200
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                email_body = '<p>Hello</p><p>A new account for EasyChat has been created. Here are the login credentials</p><p>Username - ' + \
                    self_signup_user.email_id + '</p><p>Password - ' + password_new + '</p>'

                thread = threading.Thread(target=generate_mail, args=(
                    'shivam@getcogno.ai', "Login details for new EasyChat account", str(email_body)), daemon=True)
                thread.start()

                return HttpResponse(json.dumps(response), content_type="application/json")
            else:
                response["status"] = 300
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return HttpResponse(json.dumps(response), content_type="application/json")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error PasswordSetup %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def SuccessLogin(request):
    return render(request, 'EasyChatApp/success_login.html')


class SignupAPI(APIView):

    def post(self, request, *args, **kwargs):
        from urllib.parse import quote_plus, unquote
        response = {}
        response["status"] = 500
        try:
            validation_obj = EasyChatInputValidation()
            data = request.data
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)

            firstname = data["first_name"]
            lastname = data["last_name"]
            email_id = data["email_id"]

            if not validation_obj.is_valid_name(firstname) or firstname.strip() == "":
                return Response(data=return_invalid_response(response, "Please enter a valid first name", 302))

            if not validation_obj.is_valid_name(lastname) or lastname.strip() == "":
                return Response(data=return_invalid_response(response, "Please enter a valid last name", 302))

            if User.objects.filter(username=email_id):
                response["status"] = 300
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            try:
                self_signup_user = SelfSignupUser.objects.get(
                    email_id=email_id)
            except Exception:
                logger.info("Creating new signup object: %s: %s", str(
                    email_id), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                self_signup_user = SelfSignupUser.objects.create(
                    firstname=firstname, lastname=lastname, email_id=email_id)
            self_signup_user.token = uuid.uuid4()
            self_signup_user.save(update_fields=['token'])
            time_difference = (
                timezone.now() - self_signup_user.timestamp_user_creation).total_seconds()
            if (self_signup_user.total_attempts >= 5) and (time_difference < (24 * 60 * 60)):
                self_signup_user.total_attempts = self_signup_user.total_attempts + 1
                self_signup_user.save()
                response['status'] = 305
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            else:
                if(self_signup_user.total_attempts > 5):
                    self_signup_user.total_attempts = 0
                self_signup_user.total_attempts = self_signup_user.total_attempts + 1
                self_signup_user.timestamp_user_creation = timezone.now()

                self_signup_user.save()

            access_token = self_signup_user.token
            host_url = EASYCHAT_HOST_URL

            path = host_url + \
                "/chat/password-setup/?token=" + str(access_token)

            config_obj = get_developer_console_settings()

            SECONDARY_COLOR = config_obj.secondary_color

            body = '<table><tr style="background:white"><td  style="font-style: normal;font-weight: 500;font-size: 15px;line-height: 35px;letter-spacing: 0.025em;color: #4D4D4D;"><p>Dear ' + firstname + ' ' + lastname + \
                ',</p><p>We have recieved a request to set up an EasyChat account for your email address.<p>Here are the details:</p><p>Username: ' + \
                email_id + '</p><p>Please click on the button below to create a new password (This link is only valid for ' + str(SELF_SIGNUP_USER_EXPIRATION_TIME) + ' hour)</p></td></tr></table>'

            body += '<a href=' + path + ' style="height: 41px;width: 259px;left: 633px;top: 552px;border-radius: 30px;background: #' + SECONDARY_COLOR + \
                ';border-radius: 30px;color: white;text-decoration: none;font-family: Silka;font-style: normal;font-weight: bold;font-size: 14px;line-height: 17px;letter-spacing: 0.025em;color: #FFFFFF;padding: 10px;" target="_blank">Create Password</a>'

            EMAIL_HEAD = get_email_head_from_email_html_constant()

            thread = threading.Thread(target=generate_mail, args=(
                str(email_id), "EasyChat Account Setup", str(EMAIL_HEAD + body)), daemon=True)
            thread.start()
            response["token"] = str(access_token)
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SignupAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


Signup = SignupAPI.as_view()


class ResendAPI(APIView):

    def post(self, request, *args, **kwargs):
        from urllib.parse import quote_plus, unquote
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)

            access_token = data["access_token"]

            self_signup_user = SelfSignupUser.objects.filter(
                token=access_token)[0]
            email_id = self_signup_user.email_id
            try:
                if User.objects.filter(username=email_id):
                    response["status"] = 300
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error Resend %s %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                pass

            new_access_token = uuid.uuid4()
            self_signup_user.token = new_access_token
            self_signup_user.save()

            access_token = new_access_token

            host_url = EASYCHAT_HOST_URL
            path = host_url + \
                "/chat/password-setup/?token=" + str(access_token)
            firstname = self_signup_user.firstname
            lastname = self_signup_user.lastname

            config_obj = get_developer_console_settings()

            SECONDARY_COLOR = config_obj.secondary_color

            body = '<table><tr style="background:white"><td  style="font-style: normal;font-weight: 500;font-size: 15px;line-height: 35px;letter-spacing: 0.025em;color: #4D4D4D;"><p>Dear ' + firstname + ' ' + lastname + \
                ',</p><p>We have recieved a request to set up an EasyChat account for your email address.<p>Here are the details:</p><p>Username: ' + \
                email_id + '</p><p>Please click on the button below to create a new password</p></td></tr></table>'

            body += '<a href=' + path + ' style="height: 41px;width: 259px;left: 633px;top: 552px;border-radius: 30px;background: #' + SECONDARY_COLOR + \
                ';border-radius: 30px;color: white;text-decoration: none;font-family: Silka;font-style: normal;font-weight: bold;font-size: 14px;line-height: 17px;letter-spacing: 0.025em;color: #FFFFFF;padding: 10px;" target="_blank">Create Password</a>'

            EMAIL_HEAD = get_email_head_from_email_html_constant()

            thread = threading.Thread(target=generate_mail, args=(
                str(email_id), "EasyChat Account Setup", str(EMAIL_HEAD + body)), daemon=True)
            thread.start()
            response["token"] = str(access_token)
            response["status"] = 200
            response["email_id"] = email_id
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SignupAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


Resend = ResendAPI.as_view()


def PageNotFoundView(request, exception):
    try:
        return render(request, "EasyChatApp/page_not_found.html")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error PageNotFoundView %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return HttpResponse(status=404)


class GBMQueryAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        request_data = request.body.decode('utf8').replace("'", '"')
        logger.info("Into GBMQueryAPI...", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'GoogleBusinessMessages', 'bot_id': 'None'})
        logger.info(str(request_data), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'GoogleBusinessMessages', 'bot_id': 'None'})

        request_body = json.loads(request_data)
        bot_id = ""
        channel = "GoogleBusinessMessages"
        try:
            bot_id = request.GET["id"]
            selected_bot_obj = Bot.objects.get(
                pk=int(bot_id), is_deleted=False, is_uat=True)

            gmb_obj = GMBDetails.objects.filter(bot=selected_bot_obj)[0]

            display_name = gmb_obj.bot_display_name
            display_image_url = gmb_obj.bot_display_image_url
            service_account_location = gmb_obj.gmb_credentials_file_path

            bot_representative = BusinessMessagesRepresentative(
                representativeType=BusinessMessagesRepresentative.RepresentativeTypeValueValuesEnum.BOT,
                displayName=display_name,
                avatarImage=display_image_url)

            conversation_id = request_body.get('conversationId')

            if ('message' in request_body and 'text' in request_body['message']) or ('suggestionResponse' in request_body):

                if ('suggestionResponse' in request_body):
                    message = request_body[
                        'suggestionResponse']['postbackData']
                    message_id = request_body['suggestionResponse']['message'].split(
                        "/")[-1]
                else:
                    message = request_body['message']['text']
                    message_id = request_body['message']['messageId']

                message_id_obj = GMBMessageDetails.objects.filter(
                    message_id=message_id)

                if message_id_obj.count() > 0:
                    return HttpResponse("message has been already responded")
                else:
                    message_id_obj = GMBMessageDetails.objects.create(
                        message_id=message_id)
                channel_params = {}

                if message == "custom_suggestion_link_click":
                    return HttpResponse("message has been already responded")

                # this is to check wheter user sent an image or not they send a image url as a text
                # and its given the image url will always start  from
                # https://storage.googleapis.com/

                if message.startswith("https://storage.googleapis.com/"):
                    img_url = message
                    file_src = save_and_get_gmb_image_src(img_url)
                    channel_params = {
                        "attached_file_path": file_src,
                    }
                    message = "attachment"

                channel_params = json.dumps(channel_params)

                terminate, response = process_language_change_or_get_response(conversation_id, bot_id, None, "uat", channel, channel_params, message, selected_bot_obj, service_account_location, None, bot_representative)
                if terminate:
                    return Response(data=response)
                bot_response = response

                # Authentication
                try:
                    if bot_response != {}:
                        if str(bot_response['status_code']) == '200' and bot_response['response'] != {}:
                            if 'modes' in bot_response['response']["text_response"] and bot_response['response']["text_response"]['modes'] != {}:
                                if 'auto_trigger_last_intent' in bot_response['response']["text_response"]['modes'] and bot_response['response']["text_response"]['modes']['auto_trigger_last_intent'] == 'true':
                                    if 'last_identified_intent_name' in bot_response['response'] and bot_response['response']['last_identified_intent_name'] != '':
                                        message = bot_response['response']['last_identified_intent_name']
                                        terminate, bot_response = process_language_change_or_get_response(conversation_id, bot_id, None, "uat", channel, channel_params, message, selected_bot_obj, service_account_location, None, bot_representative)
                                        if terminate:
                                            return Response(data=bot_response)
                                        logger.info("[GoogleBusinessMessages]GBM auto trigger: execute_query after Auth response %s", str(bot_response), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'GoogleBusinessMessages', 'bot_id': 'None'})
                except Exception as E:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("[GoogleBusinessMessages]GoogleBusinessMessages Cannot identify Last Intent: %s at %s", str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'GoogleBusinessMessages', 'bot_id': 'None'})

                if "is_livechat" in bot_response:
                    return HttpResponse("message recived to agent")

                save_bot_switch_data_variable_if_availabe(
                    conversation_id, bot_id, bot_response, "GoogleBusinessMessages")

                images = bot_response["response"]["images"]
                videos = bot_response["response"]["videos"]
                cards = bot_response["response"]["cards"]
                recommendations = bot_response["response"]["recommendations"]
                recommendation_list = create_recommendation_list(
                    recommendations)
                choices = bot_response["response"]["choices"]
                choice_list = create_choice_list(choices)

                validation_obj = EasyChatInputValidation()

                message = bot_response['response']['text_response']['text']
                message = gbm_text_formatting(message)
                message = html_list_formatter(message)
                message = validation_obj.remo_html_from_string(message)
                message = validation_obj.unicode_formatter(message)

                if (len(images) > 0):
                    for img in images:
                        send_image_response(
                            img, conversation_id, bot_representative, service_account_location)
                if (len(videos) > 0):
                    for vedio in videos:
                        send_text_message(
                            youtube_link_formatter(vedio), conversation_id, bot_representative, service_account_location)

                if(len(cards) == 1):
                    card = cards[0]
                    card_link = card['link']
                    suggestions = []
                    if card_link != "":
                        suggestions = [
                            BusinessMessagesSuggestion(
                                action=BusinessMessagesSuggestedAction(
                                    text='Click Here',
                                    postbackData='custom_suggestion_link_click',
                                    openUrlAction=BusinessMessagesOpenUrlAction(
                                        url=card_link))
                            ),
                        ]
                    send_single_card(card["title"], card["content"], suggestions, card["img_url"], conversation_id, bot_representative, service_account_location)

                if (len(cards) > 1):
                    card_contents = create_card_contents(cards)
                    send_multiple_cards(
                        card_contents, conversation_id, bot_representative, service_account_location)

                suggestions = recommendation_list + choice_list

                if (len(suggestions) > 0):
                    send_message_with_suggestions(
                        message, suggestions, conversation_id, bot_representative, service_account_location)
                    
                if (len(suggestions) == 0):

                    send_text_message(message, conversation_id,
                                      bot_representative, service_account_location)

                return HttpResponse("Message recevied and answered")
            elif 'surveyResponse' in request_body:
                channel_obj = Channel.objects.get(
                    name="GoogleBusinessMessages")
                survey_id = request_body['surveyResponse']['survey']
                # survey  is in format survey =
                # conversation/{conversation_id}/surveys/{survey_id}
                survey_id = survey_id.split("/")[-1]
                surveyQuestionId = request_body[
                    'surveyResponse']['surveyQuestionId']
                questionResponsePostbackData = request_body[
                    'surveyResponse']['questionResponsePostbackData']
                questionType = request_body['surveyResponse']['questionType']
                questionIndex = request_body['surveyResponse']['questionIndex']
                totalQuestionCount = request_body[
                    'surveyResponse']['totalQuestionCount']
                handle_gbm_survey_and_update_csat(conversation_id, survey_id, surveyQuestionId, questionResponsePostbackData, questionType,
                                                  questionIndex, totalQuestionCount, selected_bot_obj, channel_obj, Feedback, GBMCSATMapping, GBMSurveyQuestion)
            elif 'userStatus' in request_body:
                if 'isTyping' in request_body['userStatus']:
                    return HttpResponse("User is Typing")

            elif 'receipts' in request_body:
                receipt = request_body['receipts']['receipts'][0]
                receipt_type = receipt['receiptType']

                return HttpResponse(receipt_type)
            elif 'clientToken' in request_body and 'secret' in request_body:

                client_token = request_body["clientToken"]

                bot_channel_obj = BotChannel.objects.filter(
                    bot=selected_bot_obj, channel__name=channel).first()

                if bot_channel_obj.page_access_token.strip() != client_token:
                    return HttpResponse("UnVerified Source")

                secret = request_body["secret"]
                return HttpResponse(secret)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = "Error GBMQueryApi {} at {}".format(str(e), str(exc_tb.tb_lineno))
            logger.error(error_message, extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            try:
                if type(request_body) != dict:
                    request_body = json.loads(request_body)
                meta_data = request_body
            except:
                meta_data = {}
            meta_data["error"] = error_message
            check_and_send_broken_bot_mail(bot_id, channel, "", json.dumps(meta_data))

        return HttpResponse("response")


GBMQuery = GBMQueryAPI.as_view()


class QAAutomationTestingToolQueryAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            logger.info("Into QAAutomationToolQueryAPI...", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            data = request.data

            src = "en"
            if "src" in data:
                src = data["src"]

            validation_obj = EasyChatInputValidation()

            user_id = data['user_id']
            user_id = validation_obj.remo_html_from_string(user_id)
            message = data['message']
            message = validation_obj.remo_html_from_string(message)
            bot_id = data['bot_id']
            bot_id = validation_obj.remo_html_from_string(str(bot_id))

            channel = data['channel']
            channel = validation_obj.remo_html_from_string(channel)
            channel_params = data['channel_params']
            channel_params = validation_obj.remo_html_from_string(
                channel_params)
            bot_name = "uat"

            response = execute_query(
                user_id, bot_id, bot_name, message, src, channel, channel_params, message)

            logger.info("Exit from QAAutomationTestingToolQueryAPI : %s", json.dumps(response), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[ENGINE] %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
            response = build_error_response(
                "We are facing some issues. Please try again later.")
            response["status_code"] = 500

        return Response(data=response)


QAAutomationTestingToolQuery = QAAutomationTestingToolQueryAPI.as_view()


class IVRQueryAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            logger.info("Into IVRQueryAPI...", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            data = request.data

            src = "en"
            if "src" in data:
                src = data["src"]

            validation_obj = EasyChatInputValidation()

            user_id = data['user_id']
            user_id = validation_obj.remo_html_from_string(user_id)
            message = data['message']
            message = validation_obj.remo_html_from_string(message)
            message = message.replace(".", "")
            bot_id = data['id']
            bot_id = validation_obj.remo_html_from_string(str(bot_id))

            original_message = message

            channel = data['channel']
            channel = validation_obj.remo_html_from_string(channel)
            channel_params = "{}"
            # channel_params = remo_html_from_string(channel_params)
            bot_name = "uat"

            response = execute_query(
                user_id, bot_id, bot_name, message, src, channel, channel_params, original_message)

            response["response"]["text_response"]["text"] = BeautifulSoup(
                response["response"]["text_response"]["text"]).text
            response["response"]["text_response"]["text"] = response[
                "response"]["text_response"]["text"].replace("&nbsp;", " ")
            response["response"]["text_response"]["text"] = response[
                "response"]["text_response"]["text"].replace("\u00a0", " ")

            response["response"]["speech_response"]["text"] = BeautifulSoup(
                response["response"]["speech_response"]["text"]).text
            response["response"]["speech_response"]["text"] = response[
                "response"]["speech_response"]["text"].replace("&nbsp;", " ")
            response["response"]["speech_response"]["text"] = response[
                "response"]["speech_response"]["text"].replace("\u00a0", " ")

            logger.info("Exit from IVRQueryAPI : %s", json.dumps(response), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("[ENGINE] %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
                user_id), 'source': str(src), 'channel': str(channel), 'bot_id': str(bot_id)})
            response = build_error_response(
                "We are facing some issues. Please try again later.")
            response["status_code"] = 500

        return Response(data=response)


IVRQuery = IVRQueryAPI.as_view()


class GetIVRChannelWelcomeMessageAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status_code'] = 500
        try:
            data = request.data
            bot_id = data["bot_id"]
            bot_name = data["bot_name"]

            channel_name = "GoogleHome"

            channel_obj = Channel.objects.get(name=channel_name)

            bot_obj = None

            if(bot_name == 'uat'):
                bot_obj = Bot.objects.get(
                    pk=bot_id, is_uat=True, is_deleted=False)
            else:
                bot_obj = Bot.objects.filter(
                    slug=bot_name, is_active=True, is_deleted=False).order_by('-pk')[0]

            channel_obj = BotChannel.objects.filter(
                bot=bot_obj, channel=channel_obj)[0]

            regex_compiler = re.compile(r'<.*?>')

            response["text_welcome_message"] = regex_compiler.sub(
                "", channel_obj.welcome_message)
            response["speech_welcome_message"] = BeautifulSoup(
                channel_obj.welcome_message).text
            response["status_code"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetIVRChannelWelcomeMessageAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return Response(data=response)


GetIVRChannelWelcomeMessage = GetIVRChannelWelcomeMessageAPI.as_view()


class GetTrainingDataSuggestionsAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["sentence_list"] = []
        response["word_mapper_list"] = []
        try:
            import urllib.parse
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            bot_id = data["bot_id"]
            count_of_chunk = data["count_of_chunk"]
            bot_obj = Bot.objects.get(pk=bot_id, is_deleted=False, is_uat=True)
            word_mapper_list = bot_obj.word_mapper_list
            chunk_of_suggestion = ChunksOfSuggestions.objects.filter(
                bot=bot_obj)

            sentence_list = json.dumps([])
            if chunk_of_suggestion.exists():
                sentence_list = chunk_of_suggestion[count_of_chunk].suggestion_list
            
            response["sentence_list"] = sentence_list
            response["word_mapper_list"] = word_mapper_list
            response["status"] = 200
            response["total_length_of_chunk"] = chunk_of_suggestion.count()
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetTrainingDataAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetTrainingDataSuggestions = GetTrainingDataSuggestionsAPI.as_view()


class DataMaskToggleAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = "Internal server Error"
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_id = data["bot_id"]
            masking_enabled = data["masking_enabled"]
            masking_time = data["masking_time"]

            bot_obj = Bot.objects.get(pk=int(bot_id))
            user = request.user

            try:
                data_toggle_obj = EasyChatPIIDataToggle.objects.get(
                    user=user, bot=bot_obj)
                data_toggle_obj.token = uuid.uuid4()
            except Exception:
                logger.info("Creating new data toggle object: %s: %s", extra={'AppName': 'EasyChat', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
                data_toggle_obj = EasyChatPIIDataToggle.objects.create(
                    user=user, bot=bot_obj)

            otp = random.randrange(10**5, 10**6)

            data_toggle_obj.otp = otp
            data_toggle_obj.is_expired = False
            data_toggle_obj.save()

            if bot_obj.masking_enabled != masking_enabled:
                subject = "PII Change Request"
                content = str(user.username) + """ is trying to turn off the PII Masking settings for the bot """ + str(
                    bot_obj.name) + """ - """ + str(bot_obj.pk) + """. Code to accept it is <b>""" + str(otp) + """<b>."""
            else:
                subject = "PII Time Change Request"
                content = str(user.username) + """ is trying to change the PII timer for the bot """ + str(bot_obj.name) + """ - """ + str(bot_obj.pk) + \
                    """ from """ + str(bot_obj.masking_time) + """ min to """ + str(
                        masking_time) + """ min. Code to accept it is <b>""" + str(otp) + """<b>."""

            config_obj = get_developer_console_settings()
            if config_obj:
                email_ids = json.loads(config_obj.masking_pii_data_otp_email)
            else:
                email_ids = settings.MASKING_PII_DATA_OTP_EMAIL

            try:
                send_otp_mail(email_ids, subject, content)
                response["status_code"] = "200"
                response["status_message"] = "Success"
            except:
                response["status_code"] = "102"
                response["status_message"] = str(
                    get_developer_console_settings().email_api_failure_message)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DataMaskToggleAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DataMaskToggle = DataMaskToggleAPI.as_view()


class CheckDataToggleOtpAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status_code"] = "500"
        response["status_message"] = "Internal server Error"
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            bot_id = data["bot_id"]
            entered_otp = data["entered_otp"]

            user = request.user
            bot_obj = Bot.objects.get(pk=int(bot_id))

            data_toggle_obj = EasyChatPIIDataToggle.objects.get(
                user=user, bot=bot_obj)
            sent_otp = data_toggle_obj.otp

            if not data_toggle_obj.is_expired and entered_otp == sent_otp:
                response["message"] = "Matched"
                response["token"] = str(data_toggle_obj.token)
            else:
                response["message"] = "Not Matched"

            response["status_code"] = "200"

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CheckDataToggleOtpAPI: %s at %s",
                         e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response["status_message"] = e

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


CheckDataToggleOtp = CheckDataToggleOtpAPI.as_view()


class UpdateLastSeenChatbotAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            json_string = DecryptVariable(data['json_string'])
            data = json.loads(json_string)

            user_id = data["user_id"]
            bot_id = data['bot_id']

            bot_obj = Bot.objects.get(pk=int(bot_id))
            profile_obj = Profile.objects.get(user_id=user_id, bot=bot_obj)
            user_auth_obj = UserAuthentication.objects.get(user=profile_obj)
            user_auth_obj.last_update_time = timezone.now()
            user_auth_obj.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateLastSeenChatbotAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


UpdateLastSeenChatbot = UpdateLastSeenChatbotAPI.as_view()


def BotFileAccess(request, file_key):
    file_access_management_obj = None
    try:
        file_access_management_obj = EasyChatAppFileAccessManagement.objects.get(
            key=file_key, is_expired=False)

        if not is_valid_file_access_request(request.user, file_access_management_obj):
            return HttpResponse('This link has been expired')

        if file_access_management_obj.is_authentication_required:

            user_id = request.GET['user_id']
            profile = Profile.objects.filter(user_id=user_id).first()
            user_authentication_obj = UserAuthentication.objects.get(
                user=profile)

            tz = pytz.timezone(settings.TIME_ZONE)
            auth_datetime_obj = user_authentication_obj.last_update_time.astimezone(
                tz)
            current_datetime_obj = timezone.now().astimezone(tz)

            if (current_datetime_obj - auth_datetime_obj).total_seconds() > 60:
                return HttpResponse('Invalid Request')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error BotFileAccess %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return HttpResponse(status=404)

    try:
        path_to_file = file_access_management_obj.file_path
        filename = path_to_file.split("/")[-1]
        path_to_file = settings.BASE_DIR + path_to_file

        logger.info("BotFileAccess %s", str(path_to_file), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        mime_type, _ = mimetypes.guess_type(path_to_file)
        if os.path.exists(path_to_file):
            with open(path_to_file, 'rb') as file_h:
                response = HttpResponse(
                    file_h.read(), status=200, content_type=mime_type)
                response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(
                    str(filename))
                response['X-Sendfile'] = smart_str(path_to_file)

                if not file_access_management_obj.is_customer_attachment and not file_access_management_obj.is_analytics_file:
                    file_access_management_obj.is_expired = True
                    file_access_management_obj.save()
                return response

        return HttpResponse(status=401)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error BotFileAccess %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return HttpResponse(status=404)


class TrackEventProgressAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = DecryptVariable(data["data"])
            data = json.loads(data)

            bot_id = data['bot_id']
            event_type = data['event_type']

            bot_obj = Bot.objects.get(pk=int(bot_id))
            user_obj = request.user

            event_obj = EventProgress.objects.filter(
                user=user_obj, bot=bot_obj, event_type=event_type, is_toast_displayed=False).order_by('-pk')

            if event_obj:
                event_obj = event_obj.first()

                response['event_progress'] = event_obj.event_progress
                response['is_completed'] = event_obj.is_completed
                response['is_toast_displayed'] = event_obj.is_toast_displayed
                response['is_failed'] = event_obj.is_failed
                response['event_info'] = json.loads(event_obj.event_info)
                response['failed_message'] = event_obj.failed_message

                if event_obj.is_completed or event_obj.is_failed:
                    event_obj.is_toast_displayed = True
                    event_obj.save()

                response['status'] = 200
            else:
                response['status'] = 300

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("TrackEventProgressAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


TrackEventProgress = TrackEventProgressAPI.as_view()


def ResetForgotPassword(request):

    if request.method == "GET":
        try:
            data = request.GET
            token = data["token"]
            config_obj = get_developer_console_settings()

            reset_pass_obj = ResetPassword.objects.filter(
                token=uuid.UUID(token)).first()

            if not reset_pass_obj:
                return HttpResponse('Invalid Acess for this page')

            is_reset_pass_session_expired = False

            if check_if_reset_password_object_is_expired(reset_pass_obj):
                is_reset_pass_session_expired = True
            content_dict = {
                "config_obj": config_obj,
                "is_password_reseted": reset_pass_obj.is_password_reseted_succesfully,
                "is_reset_pass_session_expired": is_reset_pass_session_expired
            }
            if request.user_agent.is_mobile:
                return render(request, 'EasyChatApp/mobile_reset_password.html', content_dict)
            else:
                return render(request, 'EasyChatApp/web_reset_password.html', content_dict)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error ResetPassword Get %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            return HttpResponse('Your token has expired.')

    return HttpResponse('Your token has expired.')


class SaveResetedForgotPasswordAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            access_token = data["access_token"]
            access_token = validation_obj.remo_html_from_string(access_token)

            new_password = validation_obj.remo_html_from_string(
                data["password_new"])

            if not validation_obj.is_valid_password(new_password):
                response["status"] = 301
                response["message"] = "Invalid Password"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                response = {"response": response}
                return HttpResponse(json.dumps(response), content_type="application/json")

            reset_pass_obj = ResetPassword.objects.filter(
                token=uuid.UUID(access_token)).first()

            if not reset_pass_obj:
                response["status"] = 302
                response["message"] = "Thier is some Error in Reseting Your Password , Please Try Again."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                response = {"response": response}
                return HttpResponse(json.dumps(response), content_type="application/json")

            if check_if_reset_password_object_is_expired(reset_pass_obj):
                response["status"] = 302
                response["message"] = "Your Current Session to Reset Password is Expired, Please Try Again Later"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                response = {"response": response}
                return HttpResponse(json.dumps(response), content_type="application/json")

            user_obj = reset_pass_obj.user
            secured_login_object = SecuredLogin.objects.get(user=user_obj)
            if reset_pass_obj.failed_attempts <= 4:
                user_obj.password = new_password
                secured_login_object.last_password_change_date = timezone.now()
                previous_password_hashes = json.loads(
                    secured_login_object.previous_password_hashes)

                for hashed_password in previous_password_hashes["password_hash"]:
                    if check_password(new_password, hashed_password) == True:
                        response["status"] = 401
                        response[
                            "message"] = "password previously used"
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)

                if len(previous_password_hashes["password_hash"]) == 0:
                    previous_password_hashes["password_hash"].append(
                        make_password(user_obj.password))
                if len(previous_password_hashes["password_hash"]) >= 5:
                    previous_password_hashes["password_hash"].pop(0)
                previous_password_hashes["password_hash"].append(
                    make_password(new_password))
                secured_login_object.previous_password_hashes = json.dumps(
                    previous_password_hashes)
                secured_login_object.save()

                if user_obj.is_sandbox_user:
                    sandbox_user = SandboxUser.objects.filter(
                        username=user_obj.username).first()
                    if sandbox_user:
                        sandbox_user.password = new_password
                        sandbox_user.save()

                user_obj.save()
                reset_pass_obj.is_password_reseted_succesfully = True
                reset_pass_obj.save()

                description = "User password added"
                add_audit_trail(
                    "EASYCHATAPP",
                    user_obj,
                    "Update-Password",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )

                response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveResetedForgotPasswordAPI error: %s at line no: %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveResetedForgotPassword = SaveResetedForgotPasswordAPI.as_view()


def csrf_failure(request, reason=""):
    try:
        return render(request, 'EasyChatApp/error_403.html')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("csrf_failure error: %s at line no: %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return HttpResponse(status=403)
