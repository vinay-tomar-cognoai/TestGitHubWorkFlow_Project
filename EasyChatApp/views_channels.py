from EasyChatApp.models import RCSDetails
from EasyChatApp.utils_build_bot import get_hash_value
from EasyChatApp.utils_catalogue import validate_catalogue_details
from EasyChatApp.utils_validation import EasyChatInputValidation
from googletrans import client
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password

from django.core.files.storage import FileSystemStorage

from django.contrib.auth import authenticate, login
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect
from django.http import HttpResponseNotFound, HttpResponseForbidden

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_bot import *
from EasyChatApp.utils_channels import *
from EasyChatApp.telegram.utils_telegram import set_telegram_webhook
from EasyChatApp.utils_google_buisness_messages import update_welcome_msg_for_gbm_agent
from EasyChatApp.views_editstatic import get_dynamic_variables, check_common_utils_line
from EasyChatApp.constants import *
from LiveChatApp.models import LiveChatConfig
from DeveloperConsoleApp.utils import get_developer_console_settings
from django.conf import settings
from oauth2_provider.models import Application
from EasyChatApp.constants_language import *
import datetime
import re
import json
import uuid
import logging
import sys
from bs4 import BeautifulSoup
import urllib.parse

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


# def ChannelsPage(request):  # noqa: N802
#     try:
#         if is_allowed(request, [BOT_BUILDER_ROLE]):
#             if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
#                 return HttpResponseNotFound("You do not have access to this page")
#             return render(request, 'EasyChatApp/channels/channels.html')
#         else:
#             return HttpResponseRedirect("/chat/login/")
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("ChannelsPage ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
#             request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#         return None


def EditChannels(request, bot_pk):  # noqa: N802
    if request.user.is_authenticated:
        try:
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_uat=True, is_deleted=False)
            if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                return HttpResponseNotFound("You do not have access to this page")
                # return render(request, 'EasyChatApp/error_404.html')

            return render(request, 'EasyChatApp/platform/edit_channels.html', {
                "user_obj": user_obj,
                "bot_obj": bot_obj,
                "selected_bot_obj": bot_obj,
            })
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditChannels %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
            # return HttpResponse("<h5>Invalid Request</h5>")
            return render(request, 'EasyChatApp/error_500.html')
    else:
        return HttpResponseRedirect("/chat/login")


def WebChannel(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            # bot_pk_list = list(Bot.objects.filter(users__in=[user_obj]).values_list("pk", flat=True))
            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = "en"
                try:
                    selected_language = request.GET['selected_lang']
                except:
                    selected_language = "en"

                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

                deploy_url = "/files/deploy/embed_chatbot_" + \
                    str(selected_bot_obj.pk) + ".js"
                is_deploy_js_exist = os.path.exists(
                    settings.BASE_DIR + "/files/deploy/embed_chatbot_" + str(selected_bot_obj.pk) + ".js")

                domain_list = []
                if is_deploy_js_exist:
                    domains = ServiceRequest.objects.filter(
                        user=user_obj, bot=selected_bot_obj)
                    for domain in domains:
                        domain_list.extend(domain.get_domains())

                # google_home_url = settings.EASYCHAT_HOST_URL + "/chat/webhook/googlehome/?id=" + \
                #     str(selected_bot_obj.pk) + "&name=" + \
                #     str(selected_bot_obj.slug)

                channel_obj = Channel.objects.filter(name="Web").first()

                bot_channel_obj = BotChannel.objects.filter(bot=selected_bot_obj, channel=channel_obj).first()

                initial_messages_updated_list = json.loads(bot_channel_obj.initial_messages)

                initial_messages_pk_list = initial_messages_updated_list["items"]
                if "new_tag_list" in initial_messages_updated_list:
                    initial_messages_new_tag_list = initial_messages_updated_list["new_tag_list"]
                else:
                    initial_messages_new_tag_list = []

                failure_messages_pk_list = json.loads(bot_channel_obj.failure_recommendations)["items"]
                sticky_messages_pk_list = json.loads(bot_channel_obj.sticky_intent)["items"]
                sticky_menu_messages_pk_list = json.loads(bot_channel_obj.sticky_intent_menu)["items"]

                hamburger_items_list = json.loads(bot_channel_obj.hamburger_items)["items"]

                quick_items_list = json.loads(bot_channel_obj.quick_items)["items"]

                theme_selected = None
                if selected_bot_obj.default_theme:
                    theme_selected = selected_bot_obj.default_theme.name

                intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj], channels=channel_obj,
                                                    is_deleted=False,
                                                    is_form_assist_enabled=False,
                                                    is_hidden=False)

                intent_name_list = []
                intent_name_list_failure = []
                intent_name_list_sticky = []
                intent_name_menu_sticky = []

                hamburger_items = []
                quick_items = []
                for idx, intent_obj_pk in enumerate(initial_messages_pk_list):
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            is_new_tag = False
                            if len(initial_messages_new_tag_list) > 0 and initial_messages_new_tag_list[idx]:
                                is_new_tag = initial_messages_new_tag_list[idx][str(
                                    intent_obj.pk)]
                            intent_name_list.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk,
                                "new_tag": is_new_tag,
                            })
                for intent_obj_pk in failure_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                # Sticky Intents
                for intent_obj_pk in sticky_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_sticky.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in sticky_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_sticky.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                # Hamburger Items
                for hamburger_objs in hamburger_items_list:
                    intent_obj_pk = hamburger_objs[1]

                    is_link_selected = False
                    nil = "nil"
                    if hamburger_objs[5] == nil:
                        is_link_selected = False
                    else:
                        is_link_selected = True

                    hamburger_items.append({
                        "is_link_selected": is_link_selected,
                        "hamburger_pk": hamburger_objs[0],
                        "hamburger_intent_pk": hamburger_objs[1],
                        "hamburger_intent_icon": hamburger_objs[2],
                        "hamburger_menu_title": hamburger_objs[3],
                        "hamburger_intent_name": hamburger_objs[4],
                        "hamburger_link": hamburger_objs[5],
                    })

                # Quick Menu Items
                for quick_objs in quick_items_list:
                    try:
                        intent_obj_pk = quick_objs[1]
                    except Exception:
                        break
                    is_link_selected = False
                    nil = "nil"
                    if quick_objs[5] == nil:
                        is_link_selected = False
                    else:
                        is_link_selected = True

                    quick_items.append({
                        "is_link_selected": is_link_selected,
                        "quick_pk": quick_objs[0],
                        "quick_intent_pk": quick_objs[1],
                        "quick_intent_icon": quick_objs[2],
                        "quick_menu_title": quick_objs[3],
                        "quick_intent_name": quick_objs[4],
                        "quick_link": quick_objs[5],
                    })

                # Sticky Intents Menu
                for sticky_menu_objs in sticky_menu_messages_pk_list:
                    intent_obj_pk = sticky_menu_objs[0]
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_menu_sticky.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk,
                                "intent_icon": sticky_menu_objs[1]
                            })
                
                for intent_obj in all_intent_objs:
                    for sticky_messages in sticky_menu_messages_pk_list:
                        if str(intent_obj.pk) not in sticky_messages:
                            small_talk = intent_obj.is_small_talk
                            if small_talk == False:
                                intent_name_menu_sticky.append({
                                    "is_selected": False,
                                    "intent_name": intent_obj.name,
                                    "intent_pk": intent_obj.pk,
                                    "intent_icon": None
                                })
                intent_name_list_temp = []
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in initial_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_temp.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk,
                                "new_tag": False,
                            })

                intent_name_list_temp.sort(
                    key=lambda x: x['intent_name'].lower())
                intent_name_list.extend(intent_name_list_temp)

                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in failure_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk,
                            })
                language_tuned_object = bot_channel_obj
                auto_pop_up_text = selected_bot_obj.auto_pop_text
                bot_web_landing_list = json.loads(
                    selected_bot_obj.web_url_landing_data)

                form_assist_obj = FormAssistBotData.objects.filter(
                    bot=selected_bot_obj)
                form_assist_popup_text = ""
                selected_form_assist_intent = []
                if form_assist_obj.exists():
                    form_assist_obj = form_assist_obj[0]
                    selected_form_assist_intent = form_assist_obj.form_assist_intent_bubble.all()
                    form_assist_popup_text = form_assist_obj.form_assist_auto_pop_text
                else:
                    form_assist_obj = None

                form_assist_list = list(FormAssist.objects.filter(
                    bot=selected_bot_obj).values_list('intent', flat=True))
                form_assist_intent = Intent.objects.filter(
                    pk__in=form_assist_list)

                if selected_language != "en":
                    response = {}
                    response["welcome_message"] = bot_channel_obj.welcome_message
                    response["failure_message"] = bot_channel_obj.failure_message
                    response[
                        "authentication_message"] = bot_channel_obj.authentication_message
                    create_language_tuned_object = True
                    check_and_create_channel_details_language_tuning_objects(
                        response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                    lang_obj = Language.objects.get(lang=selected_language)
                    language_tuned_object = LanguageTunedBotChannel.objects.filter(
                        language=lang_obj, bot_channel=bot_channel_obj)[0]

                    bot_language_tuned_object = check_and_create_language_tuned_bot_objects(
                        selected_bot_obj, selected_language, form_assist_obj, Language, LanguageTunedBot, EasyChatTranslationCache)
                    auto_pop_up_text = bot_language_tuned_object.auto_pop_up_text
                    form_assist_popup_text = bot_language_tuned_object.form_assist_popup_text
                    tuned_bot_web_landing = json.loads(
                        bot_language_tuned_object.web_url_landing_data)
                    bot_web_landing_list = get_multilingual_bot_web_landing_list(
                        bot_web_landing_list, tuned_bot_web_landing)

                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages
                # are selected  after first three
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3

                master_languages = selected_bot_obj.languages_supported.all()
                initial_intent_present = selected_bot_obj.web_url_initial_intent_present
                is_welcome_message_present = selected_bot_obj.web_url_is_welcome_message_present
                initial_image_present = selected_bot_obj.web_url_initial_image_present
                initial_videos_present = selected_bot_obj.web_url_initial_videos_present
                is_welcome_banner_present = selected_bot_obj.web_url_is_welcome_banner_present
                activity_update = json.loads(bot_channel_obj.activity_update)
                is_phonetic_language_supported = False
                phonetic_typing_enabled_languages = get_list_of_phonetic_typing_suported_languages(
                    LANGUGES_SUPPORTING_PHONETIC_TYPING)
                if bot_channel_obj.languages_supported.all().filter(lang__in=phonetic_typing_enabled_languages).exists():
                    is_phonetic_language_supported = True
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(bot_channel_obj,
                                                                                        activity_update, selected_language, LanguageTunedBotChannel)
                easychat_themes = EasyChatTheme.objects.all().order_by("name")

                welcome_banner_objs = WelcomeBanner.objects.filter(
                    bot_channel=bot_channel_obj).order_by("serial_number")

                bot_info_obj = BotInfo.objects.get(bot=selected_bot_obj)
                custom_intent_is_for = bot_info_obj.custom_intents_for
                custom_intent_objs = CustomIntentBubblesForWebpages.objects.filter(
                    bot=selected_bot_obj)

                return render(request, 'EasyChatApp/channels/web_channel.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "bot_position_choices": BOT_POSITION_CHOICES,
                    "deploy_url": deploy_url,
                    "is_deploy_js_exist": is_deploy_js_exist,
                    # "google_home_deploy_url": google_home_url,
                    "theme_selected": theme_selected,
                    "domain_list": domain_list,
                    "intent_name_list_sticky": intent_name_list_sticky,
                    "bot_channel_obj": bot_channel_obj,
                    "bot_web_landing_list": bot_web_landing_list,
                    "initial_intent_present": initial_intent_present,
                    "is_welcome_message_present": is_welcome_message_present,
                    "initial_image_present": initial_image_present,
                    "initial_videos_present": initial_videos_present,
                    "is_welcome_banner_present": is_welcome_banner_present,
                    "intent_name_menu_sticky": intent_name_menu_sticky,
                    "hamburger_items": hamburger_items,
                    "quick_items": quick_items,
                    "all_intent_objs": all_intent_objs,
                    "character_limit_medium_text": CHARACTER_LIMIT_MEDIUM_TEXT,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "auto_pop_up_text": auto_pop_up_text,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                    "is_phonetic_language_supported": is_phonetic_language_supported,
                    "form_assist_obj": form_assist_obj,
                    "form_assist_popup_text": form_assist_popup_text,
                    "form_assist_intent": form_assist_intent,
                    "selected_form_assist_intent": selected_form_assist_intent,
                    "easychat_themes": easychat_themes,
                    "welcome_banner_intent_objs": all_intent_objs.filter(channels__in=Channel.objects.filter(name="Web")),
                    "welcome_banner_objs": welcome_banner_objs,
                    "bot_info_obj": bot_info_obj,
                    "phonetic_typing_enabled_languages": phonetic_typing_enabled_languages,
                    "custom_intent_is_for": custom_intent_is_for,
                    "custom_intent_objs": custom_intent_objs,
                    "intent_icon_choices_info": INTENT_ICON_CHOICES_INFO,
                    "intent_icon_channel_choices_info": bot_info_obj.get_intent_icon_channel_choices_info(),
                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("WebChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(selected_bot_obj.pk)})
        return render(request, 'EasyChatApp/error_404.html')


def GoogleAssistantChannel(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            # bot_pk_list = list(Bot.objects.filter(users__in=[user_obj]).values_list("pk", flat=True))
            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = request.GET.get("selected_lang", "en")
                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

                channel_obj = Channel.objects.get(name="GoogleHome")
                bot_channel_obj = BotChannel.objects.get(bot=selected_bot_obj, channel=channel_obj)

                initial_messages_pk_list = json.loads(bot_channel_obj.initial_messages)["items"]
                failure_messages_pk_list = json.loads(bot_channel_obj.failure_recommendations)["items"]

                intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj], channels=channel_obj,
                                                    is_deleted=False,
                                                    is_form_assist_enabled=False,
                                                    is_hidden=False)

                intent_name_list = []
                intent_name_list_failure = []
                for intent_obj_pk in initial_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                for intent_obj_pk in failure_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)

                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in initial_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in failure_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                # name = "GoogleHome_" + request.GET['id']
                project_id = ""
                welcome_image_src = ""
                proj_details_obj_pk = ""
                channel = Channel.objects.filter(name="GoogleHome").first()
                is_get_otp_added = False
                is_verify_otp_added = False
                if GoogleAlexaProjectDetails.objects.filter(bot=selected_bot_obj, channel=channel).exists():
                    google_assistant_details_obj = GoogleAlexaProjectDetails.objects.filter(
                        bot=selected_bot_obj, channel=channel).first()
                    proj_details_obj_pk = google_assistant_details_obj.pk
                    project_id = google_assistant_details_obj.project_id
                    welcome_image_src = google_assistant_details_obj.welcome_image_src
                    if google_assistant_details_obj.get_otp_processor:
                        is_get_otp_added = True
                    if google_assistant_details_obj.verify_otp_processor:
                        is_verify_otp_added = True

                master_languages = selected_bot_obj.languages_supported.all()
                language_tuned_object = bot_channel_obj
                activity_update = json.loads(bot_channel_obj.activity_update)
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(
                    bot_channel_obj, activity_update, selected_language, LanguageTunedBotChannel)

                if selected_language != "en":
                    response = {}
                    response["welcome_message"] = bot_channel_obj.welcome_message
                    response["failure_message"] = bot_channel_obj.failure_message
                    response[
                        "authentication_message"] = bot_channel_obj.authentication_message
                    create_language_tuned_object = True
                    check_and_create_channel_details_language_tuning_objects(
                        response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                    lang_obj = Language.objects.get(lang=selected_language)
                    language_tuned_object = LanguageTunedBotChannel.objects.filter(
                        language=lang_obj, bot_channel=bot_channel_obj)[0]

                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages
                # are selected  after first five
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3

                return render(request, 'EasyChatApp/channels/google_channel.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "bot_channel_obj": bot_channel_obj,
                    "project_id": project_id,
                    "welcome_image_src": welcome_image_src,
                    "proj_details_obj_pk": proj_details_obj_pk,
                    "is_get_otp_added": is_get_otp_added,
                    "is_verify_otp_added": is_verify_otp_added,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("GoogleAssistantChannel ! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET['id'])})
        return None


def AlexaChannel(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            # bot_pk_list = list(Bot.objects.filter(users__in=[user_obj]).values_list("pk", flat=True))
            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = request.GET.get("selected_lang", "en")
                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

                channel_obj = Channel.objects.get(name="Alexa")
                bot_channel_obj = BotChannel.objects.get(bot=selected_bot_obj, channel=channel_obj)
                initial_messages_pk_list = json.loads(bot_channel_obj.initial_messages)["items"]
                failure_messages_pk_list = json.loads(bot_channel_obj.failure_recommendations)["items"]

                intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj], channels=channel_obj,
                                                    is_deleted=False,
                                                    is_form_assist_enabled=False,
                                                    is_hidden=False)

                intent_name_list = []
                intent_name_list_failure = []
                for intent_obj_pk in initial_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                for intent_obj_pk in failure_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)

                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in initial_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in failure_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                # name = "Alexa_" + request.GET['id']
                project_id = ""
                welcome_image_src = ""
                proj_details_obj_pk = ""
                channel = Channel.objects.filter(name="Alexa").first()
                is_get_otp_added = False
                is_verify_otp_added = False
                if GoogleAlexaProjectDetails.objects.filter(bot=selected_bot_obj, channel=channel).exists():
                    google_assistant_details_obj = GoogleAlexaProjectDetails.objects.filter(
                        bot=selected_bot_obj, channel=channel).first()
                    proj_details_obj_pk = google_assistant_details_obj.pk
                    project_id = google_assistant_details_obj.project_id
                    welcome_image_src = google_assistant_details_obj.welcome_image_src
                    if google_assistant_details_obj.get_otp_processor:
                        is_get_otp_added = True
                    if google_assistant_details_obj.verify_otp_processor:
                        is_verify_otp_added = True

                master_languages = selected_bot_obj.languages_supported.all()
                language_tuned_object = bot_channel_obj
                activity_update = json.loads(bot_channel_obj.activity_update)
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(
                    bot_channel_obj, activity_update, selected_language, LanguageTunedBotChannel)

                if selected_language != "en":
                    response = {}
                    response["welcome_message"] = bot_channel_obj.welcome_message
                    response["failure_message"] = bot_channel_obj.failure_message
                    response[
                        "authentication_message"] = bot_channel_obj.authentication_message
                    create_language_tuned_object = True
                    check_and_create_channel_details_language_tuning_objects(
                        response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                    lang_obj = Language.objects.get(lang=selected_language)
                    language_tuned_object = LanguageTunedBotChannel.objects.filter(
                        language=lang_obj, bot_channel=bot_channel_obj)[0]

                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages
                # are selected  after first five
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3

                return render(request, 'EasyChatApp/channels/alexa_channel.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "bot_channel_obj": bot_channel_obj,
                    "project_id": project_id,
                    "welcome_image_src": welcome_image_src,
                    "proj_details_obj_pk": proj_details_obj_pk,
                    "is_get_otp_added": is_get_otp_added,
                    "is_verify_otp_added": is_verify_otp_added,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AlexaChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET['id'])})
        return None


def AndroidChannel(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            # bot_pk_list = list(Bot.objects.filter(users__in=[user_obj]).values_list("pk", flat=True))
            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = "en"
                try:
                    selected_language = request.GET['selected_lang']
                except:
                    selected_language = "en"

                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

                channel_obj = Channel.objects.get(name="Android")

                bot_channel_obj = BotChannel.objects.get(bot=selected_bot_obj, channel=channel_obj)

                initial_messages_pk_list = json.loads(bot_channel_obj.initial_messages)["items"]
                failure_messages_pk_list = json.loads(bot_channel_obj.failure_recommendations)["items"]
                sticky_messages_pk_list = json.loads(bot_channel_obj.sticky_intent)["items"]
                sticky_menu_messages_pk_list = json.loads(bot_channel_obj.sticky_intent_menu)["items"]

                theme_selected = None
                if selected_bot_obj.default_theme:
                    theme_selected = selected_bot_obj.default_theme.name

                intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj], channels=channel_obj,
                                                    is_deleted=False,
                                                    is_form_assist_enabled=False,
                                                    is_hidden=False)

                intent_name_list = []
                intent_name_list_failure = []
                intent_name_list_sticky = []
                intent_name_menu_sticky = []

                intent_name_list = initialize_intent_name_lists(
                    initial_messages_pk_list, channel_obj)

                intent_name_list_failure = initialize_intent_name_lists(
                    failure_messages_pk_list, channel_obj)

                # Sticky Intents
                intent_name_list_sticky = initialize_intent_name_lists(
                    sticky_messages_pk_list, channel_obj)
                intent_name_list_sticky = append_all_intent_objects_list(
                    sticky_messages_pk_list, intent_name_list_sticky, selected_bot_obj, channel_obj)

                # Sticky Intents Menu
                for sticky_menu_objs in sticky_menu_messages_pk_list:
                    intent_obj_pk = sticky_menu_objs[0]
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_menu_sticky.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk,
                                "intent_icon": sticky_menu_objs[1]
                            })
                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)
                for intent_obj in all_intent_objs:
                    for sticky_messages in sticky_menu_messages_pk_list:
                        if str(intent_obj.pk) not in sticky_messages:
                            small_talk = intent_obj.is_small_talk
                            if small_talk == False:
                                intent_name_menu_sticky.append({
                                    "is_selected": False,
                                    "intent_name": intent_obj.name,
                                    "intent_pk": intent_obj.pk,
                                    "intent_icon": None
                                })

                intent_name_list = append_all_intent_objects_list(
                    initial_messages_pk_list, intent_name_list, selected_bot_obj, channel_obj)

                intent_name_list_failure = append_all_intent_objects_list(
                    failure_messages_pk_list, intent_name_list_failure, selected_bot_obj, channel_obj)

                language_tuned_object = bot_channel_obj

                language_tuned_object = get_languange_tuned_object(
                    selected_language, selected_bot_obj, channel_obj)

                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages are selected  after first three
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3

                master_languages = selected_bot_obj.languages_supported.all()
                initial_intent_present = selected_bot_obj.web_url_initial_intent_present
                is_welcome_message_present = selected_bot_obj.web_url_is_welcome_message_present
                initial_image_present = selected_bot_obj.web_url_initial_image_present
                initial_videos_present = selected_bot_obj.web_url_initial_videos_present
                is_welcome_banner_present = selected_bot_obj.web_url_is_welcome_banner_present
                activity_update = json.loads(bot_channel_obj.activity_update)
                is_phonetic_language_supported = False
                phonetic_typing_enabled_languages = get_list_of_phonetic_typing_suported_languages(
                    LANGUGES_SUPPORTING_PHONETIC_TYPING)
                if bot_channel_obj.languages_supported.all().filter(lang__in=phonetic_typing_enabled_languages).exists():
                    is_phonetic_language_supported = True
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(bot_channel_obj,
                                                                                        activity_update, selected_language, LanguageTunedBotChannel)

                deployment_url = settings.EASYCHAT_HOST_URL + \
                    "/chat/index/?id=" + str(bot_pk) + "&channel=Android"

                deployment_dependency = "implementation 'com.allincall:easychatsdkwebview:2.6'"
                deployment_dependency_flutter = "implementation 'com.allincall:easychatsdkwebviewflutter:1.9'"
                easychat_themes = EasyChatTheme.objects.all().order_by("name")

                welcome_banner_objs = WelcomeBanner.objects.filter(
                    bot_channel=bot_channel_obj).order_by("serial_number")

                bot_info_obj = BotInfo.objects.get(bot=selected_bot_obj)

                return render(request, 'EasyChatApp/channels/android_channel.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "bot_position_choices": BOT_POSITION_CHOICES,
                    # "google_home_deploy_url": google_home_url,
                    "theme_selected": theme_selected,
                    "intent_name_list_sticky": intent_name_list_sticky,
                    "bot_channel_obj": bot_channel_obj,
                    "initial_intent_present": initial_intent_present,
                    "is_welcome_message_present": is_welcome_message_present,
                    "initial_image_present": initial_image_present,
                    "initial_videos_present": initial_videos_present,
                    "is_welcome_banner_present": is_welcome_banner_present,
                    "intent_name_menu_sticky": intent_name_menu_sticky,
                    "all_intent_objs": all_intent_objs,
                    "character_limit_medium_text": CHARACTER_LIMIT_MEDIUM_TEXT,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                    "is_phonetic_language_supported": is_phonetic_language_supported,
                    "deployment_url": deployment_url,
                    "deployment_dependency": deployment_dependency,
                    "deployment_dependency_flutter": deployment_dependency_flutter,
                    "easychat_themes": easychat_themes,
                    "welcome_banner_intent_objs": all_intent_objs.filter(channels__in=Channel.objects.filter(name="Android")),
                    "welcome_banner_objs": welcome_banner_objs,
                    "bot_info_obj": bot_info_obj,
                    "phonetic_typing_enabled_languages": phonetic_typing_enabled_languages,
                    "intent_icon_choices_info": INTENT_ICON_CHOICES_INFO,
                    "intent_icon_channel_choices_info": bot_info_obj.get_intent_icon_channel_choices_info(),
                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("AndroidChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(selected_bot_obj.pk)})
        return render(request, 'EasyChatApp/error_404.html')


def WhatsAppChannel(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            # bot_pk_list = list(Bot.objects.filter(users__in=[user_obj]).values_list("pk", flat=True))
            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = "en"
                try:
                    selected_language = request.GET['selected_lang']
                except:
                    selected_language = "en"

                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)
                channel_obj = Channel.objects.get(name="WhatsApp")
                bot_channel_obj = BotChannel.objects.get(
                    bot=selected_bot_obj, channel=channel_obj)
                initial_messages_pk_list = json.loads(
                    bot_channel_obj.initial_messages)["items"]
                failure_messages_pk_list = json.loads(
                    bot_channel_obj.failure_recommendations)["items"]
                api_fail_email_configured = False

                blocked_config_obj = BlockConfig.objects.filter(bot=selected_bot_obj).first()

                whatsapp_credentials_obj = WhatsappCredentialsConfig.objects.filter(bot=selected_bot_obj).first()

                if not blocked_config_obj:
                    blocked_config_obj = BlockConfig.objects.create(bot=selected_bot_obj)

                if len(json.loads(bot_channel_obj.mail_sent_to_list)["items"]):
                    api_fail_email_configured = True

                intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj], channels=channel_obj,
                                                    is_deleted=False,
                                                    is_form_assist_enabled=False,
                                                    is_hidden=False)

                intent_name_list = []
                intent_name_list_failure = []
                for intent_obj_pk in initial_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                for intent_obj_pk in failure_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in initial_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in failure_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                whatsapp_url = settings.EASYCHAT_HOST_URL + "/chat/webhook/whatsapp/?id=" + \
                    str(bot_pk)
                master_languages = selected_bot_obj.languages_supported.all()
                language_tuned_object = bot_channel_obj
                activity_update = json.loads(bot_channel_obj.activity_update)
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(bot_channel_obj,
                                                                                        activity_update, selected_language, LanguageTunedBotChannel)
                language_tuned_query_warning_message_text = blocked_config_obj.user_query_warning_message_text
                language_tuned_query_block_message_text = blocked_config_obj.user_query_block_message_text
                language_tuned_keywords_warning_message_text = blocked_config_obj.spam_keywords_warning_message_text
                language_tuned_keywords_block_message_text = blocked_config_obj.spam_keywords_block_message_text

                if selected_language != "en":
                    response = {}
                    response["welcome_message"] = bot_channel_obj.welcome_message
                    response["failure_message"] = bot_channel_obj.failure_message
                    response[
                        "authentication_message"] = bot_channel_obj.authentication_message
                    response["query_warning_message_text"] = blocked_config_obj.user_query_warning_message_text
                    response["query_block_message_text"] = blocked_config_obj.user_query_block_message_text
                    response["keywords_warning_message_text"] = blocked_config_obj.spam_keywords_warning_message_text
                    response["keywords_block_message_text"] = blocked_config_obj.spam_keywords_block_message_text

                    create_language_tuned_object = True
                    check_and_create_channel_details_language_tuning_objects(
                        response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                    update_catalogue_language_tuning(
                        selected_bot_obj, selected_language, Language, LanguageTunedBot, EasyChatTranslationCache, WhatsappCatalogueDetails)
                    lang_obj = Language.objects.get(lang=selected_language)
                    language_tuned_object = LanguageTunedBotChannel.objects.filter(
                        language=lang_obj, bot_channel=bot_channel_obj)[0]
                    language_tuned_whatsapp_data = json.loads(language_tuned_object.block_spam_data)
                    language_tuned_query_warning_message_text = language_tuned_whatsapp_data["query_warning_message_text"]
                    language_tuned_query_block_message_text = language_tuned_whatsapp_data["query_block_message_text"]
                    language_tuned_keywords_warning_message_text = language_tuned_whatsapp_data["keywords_warning_message_text"]
                    language_tuned_keywords_block_message_text = language_tuned_whatsapp_data["keywords_block_message_text"]
                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages
                # are selected  after first five
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3
                return render(request, 'EasyChatApp/channels/whatsapp_channel.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "bot_channel_obj": bot_channel_obj,
                    "api_fail_email_configured": api_fail_email_configured,
                    "whatsapp_url": whatsapp_url,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                    "blocked_config_obj": blocked_config_obj,
                    "language_tuned_query_warning_message_text": language_tuned_query_warning_message_text,
                    "language_tuned_query_block_message_text": language_tuned_query_block_message_text,
                    "language_tuned_keywords_warning_message_text": language_tuned_keywords_warning_message_text,
                    "language_tuned_keywords_block_message_text": language_tuned_keywords_block_message_text,
                    "whatsapp_credentials_obj": whatsapp_credentials_obj,
                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("WhatsAppChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET['id'])})
        return None


def FacebookChannel(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            # bot_pk_list = list(Bot.objects.filter(users__in=[user_obj]).values_list("pk", flat=True))
            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = request.GET.get("selected_lang", "en")
                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

                channel_obj = Channel.objects.get(name="Facebook")
                bot_channel_obj = BotChannel.objects.get(bot=selected_bot_obj, channel=channel_obj)
                initial_messages_pk_list = json.loads(bot_channel_obj.initial_messages)["items"]
                failure_messages_pk_list = json.loads(bot_channel_obj.failure_recommendations)["items"]
                verification_code = bot_channel_obj.verification_code
                page_access_token = bot_channel_obj.page_access_token

                intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj], channels=channel_obj,
                                                    is_deleted=False,
                                                    is_form_assist_enabled=False,
                                                    is_hidden=False)

                intent_name_list = []
                intent_name_list_failure = []
                for intent_obj_pk in initial_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                for intent_obj_pk in failure_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in initial_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in failure_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                master_languages = selected_bot_obj.languages_supported.all()
                language_tuned_object = bot_channel_obj
                activity_update = json.loads(bot_channel_obj.activity_update)
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(
                    bot_channel_obj, activity_update, selected_language, LanguageTunedBotChannel)

                if selected_language != "en":
                    response = {}
                    response["welcome_message"] = bot_channel_obj.welcome_message
                    response["failure_message"] = bot_channel_obj.failure_message
                    response[
                        "authentication_message"] = bot_channel_obj.authentication_message
                    create_language_tuned_object = True
                    check_and_create_channel_details_language_tuning_objects(
                        response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                    lang_obj = Language.objects.get(lang=selected_language)
                    language_tuned_object = LanguageTunedBotChannel.objects.filter(
                        language=lang_obj, bot_channel=bot_channel_obj)[0]

                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages
                # are selected  after first five
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3

                return render(request, 'EasyChatApp/channels/facebook_channel.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "verification_code": verification_code,
                    "page_access_token": page_access_token,
                    "bot_channel_obj": bot_channel_obj,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("FacebookChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET['id'])})
        # return HttpResponseNotFound("500")
        return render(request, 'EasyChatApp/error_500.html')


def InstagramChannel(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            # bot_pk_list = list(Bot.objects.filter(users__in=[user_obj]).values_list("pk", flat=True))
            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = request.GET.get("selected_lang", "en")
                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

                channel_obj = Channel.objects.get(name="Instagram")
                bot_channel_obj = BotChannel.objects.get(bot=selected_bot_obj, channel=channel_obj)
                initial_messages_pk_list = json.loads(bot_channel_obj.initial_messages)["items"]
                failure_messages_pk_list = json.loads(bot_channel_obj.failure_recommendations)["items"]
                verification_code = bot_channel_obj.verification_code
                page_access_token = bot_channel_obj.page_access_token
                intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj], channels=channel_obj,
                                                    is_deleted=False,
                                                    is_form_assist_enabled=False,
                                                    is_hidden=False)

                intent_name_list = []
                intent_name_list_failure = []
                for intent_obj_pk in initial_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                for intent_obj_pk in failure_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in initial_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in failure_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                master_languages = selected_bot_obj.languages_supported.all()
                language_tuned_object = bot_channel_obj
                activity_update = json.loads(bot_channel_obj.activity_update)
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(
                    bot_channel_obj, activity_update, selected_language, LanguageTunedBotChannel)

                if selected_language != "en":
                    response = {}
                    response["welcome_message"] = bot_channel_obj.welcome_message
                    response["failure_message"] = bot_channel_obj.failure_message
                    response[
                        "authentication_message"] = bot_channel_obj.authentication_message
                    create_language_tuned_object = True
                    check_and_create_channel_details_language_tuning_objects(
                        response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                    lang_obj = Language.objects.get(lang=selected_language)
                    language_tuned_object = LanguageTunedBotChannel.objects.filter(
                        language=lang_obj, bot_channel=bot_channel_obj)[0]

                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages
                # are selected  after first five
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3
                data_initial_messages = json.loads(bot_channel_obj.initial_messages)
                data_image = ""
                data_video = ""
                if "images" in data_initial_messages:
                    if len(data_initial_messages["images"]) != 0:
                        data_image = data_initial_messages["images"][0]
                if "videos" in data_initial_messages:
                    if len(data_initial_messages["videos"]) != 0:
                        data_video = data_initial_messages["videos"][0]
                
                return render(request, 'EasyChatApp/channels/instagram_channel.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "verification_code": verification_code,
                    "page_access_token": page_access_token,
                    "bot_channel_obj": bot_channel_obj,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                    "image_url": data_image,
                    "video_url": data_video
                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("InstagramChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET['id'])})
        # return HttpResponseNotFound("500")
        return render(request, 'EasyChatApp/error_500.html')


###############################  Telegram Channel   ######################


def TelegramChannel(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")

            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = request.GET.get("selected_lang", "en")
                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

                # telegram api token
                try:
                    telegram_obj = TelegramDetails.objects.filter(
                        bot=selected_bot_obj)[0]
                except Exception:
                    telegram_obj = TelegramDetails.objects.create(
                        bot=selected_bot_obj)
                    logger.info("Creating new TelegramDetails objects", extra={
                                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass
                telegram_api_token = "XXXXXXXXXXXXXXXXXXXXXXXX" + \
                    (telegram_obj.telegram_api_token)[
                        -4:] if telegram_obj.is_active else ""
                channel_obj = Channel.objects.get(name="Telegram")
                bot_channel_obj = BotChannel.objects.get(
                    bot=selected_bot_obj, channel=channel_obj)
                initial_messages_pk_list = json.loads(
                    bot_channel_obj.initial_messages)["items"]
                failure_messages_pk_list = json.loads(
                    bot_channel_obj.failure_recommendations)["items"]

                intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj], channels=channel_obj,
                                                    is_deleted=False,
                                                    is_form_assist_enabled=False,
                                                    is_hidden=False)
                intent_name_list = []
                intent_name_list_failure = []
                for intent_obj_pk in initial_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                for intent_obj_pk in failure_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in initial_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in failure_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                telegram_url = settings.EASYCHAT_HOST_URL + \
                    "/chat/webhook/telegram/?id=" + str(bot_pk)
                master_languages = selected_bot_obj.languages_supported.all()
                language_tuned_object = bot_channel_obj
                activity_update = json.loads(bot_channel_obj.activity_update)
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(
                    bot_channel_obj, activity_update, selected_language, LanguageTunedBotChannel)

                if selected_language != "en":
                    response = {}
                    response["welcome_message"] = bot_channel_obj.welcome_message
                    response["failure_message"] = bot_channel_obj.failure_message
                    response[
                        "authentication_message"] = bot_channel_obj.authentication_message
                    create_language_tuned_object = True
                    check_and_create_channel_details_language_tuning_objects(
                        response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                    lang_obj = Language.objects.get(lang=selected_language)
                    language_tuned_object = LanguageTunedBotChannel.objects.filter(
                        language=lang_obj, bot_channel=bot_channel_obj)[0]

                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages
                # are selected  after first five
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3

                return render(request, 'EasyChatApp/channels/telegram_channel.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "bot_channel_obj": bot_channel_obj,
                    "telegram_url": telegram_url,
                    "telegram_api_token": telegram_api_token,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("TelegramChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET['id'])})
        return None


def ETSourceChannel(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")

            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = request.GET.get("selected_lang", "en")
                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

                channel_obj = Channel.objects.get(name="ET-Source")
                bot_channel_obj = BotChannel.objects.get(
                    bot=selected_bot_obj, channel=channel_obj)
                initial_messages_pk_list = json.loads(
                    bot_channel_obj.initial_messages)["items"]
                failure_messages_pk_list = json.loads(
                    bot_channel_obj.failure_recommendations)["items"]

                intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj], channels=channel_obj,
                                                    is_deleted=False,
                                                    is_form_assist_enabled=False,
                                                    is_hidden=False)

                intent_name_list = []
                intent_name_list_failure = []
                for intent_obj_pk in initial_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                for intent_obj_pk in failure_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in initial_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in failure_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                et_source_url = settings.EASYCHAT_HOST_URL + "/chat/webhook/chatbot/"

                master_languages = selected_bot_obj.languages_supported.all()
                language_tuned_object = bot_channel_obj
                activity_update = json.loads(bot_channel_obj.activity_update)
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(
                    bot_channel_obj, activity_update, selected_language, LanguageTunedBotChannel)

                if selected_language != "en":
                    response = {}
                    response["welcome_message"] = bot_channel_obj.welcome_message
                    response["failure_message"] = bot_channel_obj.failure_message
                    response[
                        "authentication_message"] = bot_channel_obj.authentication_message
                    create_language_tuned_object = True
                    check_and_create_channel_details_language_tuning_objects(
                        response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                    lang_obj = Language.objects.get(lang=selected_language)
                    language_tuned_object = LanguageTunedBotChannel.objects.filter(
                        language=lang_obj, bot_channel=bot_channel_obj)[0]

                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages
                # are selected  after first five
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3

                return render(request, 'EasyChatApp/channels/et_source_channel.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "bot_channel_obj": bot_channel_obj,
                    "et_source_url": et_source_url,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("TelegramChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET['id'])})
        return None


def GoogleBusinessMessagesChannel(request):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            # bot_pk_list = list(Bot.objects.filter(users__in=[user_obj]).values_list("pk", flat=True))
            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = request.GET.get("selected_lang", "en")
                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

                channel_obj = Channel.objects.get(name="GoogleBusinessMessages")
                bot_channel_obj = BotChannel.objects.get(
                    bot=selected_bot_obj, channel=channel_obj)

                initial_messages_pk_list = json.loads(bot_channel_obj.initial_messages)["items"]
                failure_messages_pk_list = json.loads(bot_channel_obj.failure_recommendations)["items"]

                intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj], channels=channel_obj,
                                                    is_deleted=False,
                                                    is_form_assist_enabled=False,
                                                    is_hidden=False)

                gmb_obj = GMBDetails.objects.filter(bot=selected_bot_obj)
                gmb_credentials_file_name = ""
                if gmb_obj.count() == 0:
                    gmb_obj = GMBDetails.objects.create(
                        bot=selected_bot_obj)

                else:
                    gmb_obj = gmb_obj[0]
                    gmb_credentials_file_name = (
                        gmb_obj.gmb_credentials_file_path).split("/")[-1]

                intent_name_list = []
                intent_name_list_failure = []
                for intent_obj_pk in initial_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                for intent_obj_pk in failure_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)

                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in initial_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in failure_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                gmb_url = settings.EASYCHAT_HOST_URL + \
                    "/chat/webhook/gbm/?id=" + str(bot_pk)

                client_access_token = bot_channel_obj.page_access_token

                if not client_access_token:
                    client_access_token = ""

                master_languages = selected_bot_obj.languages_supported.all()
                language_tuned_object = bot_channel_obj
                activity_update = json.loads(bot_channel_obj.activity_update)
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(
                    bot_channel_obj, activity_update, selected_language, LanguageTunedBotChannel)

                if selected_language != "en":
                    response = {}
                    response["welcome_message"] = bot_channel_obj.welcome_message
                    response["failure_message"] = bot_channel_obj.failure_message
                    response[
                        "authentication_message"] = bot_channel_obj.authentication_message
                    create_language_tuned_object = True
                    check_and_create_channel_details_language_tuning_objects(
                        response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                    lang_obj = Language.objects.get(lang=selected_language)
                    language_tuned_object = LanguageTunedBotChannel.objects.filter(
                        language=lang_obj, bot_channel=bot_channel_obj)[0]

                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages
                # are selected  after first five
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3

                return render(request, 'EasyChatApp/channels/google_my_buisness.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "bot_channel_obj": bot_channel_obj,
                    "gmb_url": gmb_url,
                    "gmb_obj": gmb_obj,
                    "gmb_credentials_file_name": gmb_credentials_file_name,
                    "client_access_token": client_access_token,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("GoogleBusinessMessagesChannel ! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET['id'])})
        return None

# def AndroidChannel(request):  # noqa: N802
#     try:
#         if is_allowed(request, [BOT_BUILDER_ROLE]):
#             user_obj = User.objects.get(username=str(request.user.username))
#             if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
#                 return HttpResponseNotFound("You do not have access to this page")
#             # bot_pk_list = list(Bot.objects.filter(users__in=[user_obj]).values_list("pk", flat=True))
#             bot_pk_list = get_uat_bots_pk_list(user_obj)
#             if int(request.GET['id']) in bot_pk_list:
#                 bot_pk = request.GET['id']
#                 if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
#                     return HttpResponseNotFound("You do not have access to this page")
#                 selected_bot_obj = Bot.objects.get(
#                     pk=int(bot_pk), is_deleted=False, is_uat=True)
#                 initial_messages_pk_list = json.loads(BotChannel.objects.get(bot=selected_bot_obj, channel=Channel.objects.get(name="Android")).initial_messages)["items"]
#                 failure_messages_pk_list = json.loads(BotChannel.objects.get(bot=selected_bot_obj, channel=Channel.objects.get(name="Android")).failure_recommendations)["items"]

#                 intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj],
#                                                             is_deleted=False,
#                                                             is_form_assist_enabled=False,
#                                                             is_hidden=False)

#                 intent_name_list = []
#                 intent_name_list_failure = []
#                 for intent_obj in intent_objs:
#                     if str(intent_obj.pk) not in initial_messages_pk_list:
#                         intent_name_list.append({
#                             "is_selected": False,
#                             "intent_name": intent_obj.name,
#                             "intent_pk": intent_obj.pk
#                         })
#                     else:
#                         intent_name_list.append({
#                             "is_selected": True,
#                             "intent_name": intent_obj.name,
#                             "intent_pk": intent_obj.pk
#                         })

#                     if str(intent_obj.pk) not in failure_messages_pk_list:
#                         intent_name_list_failure.append({
#                             "is_selected": False,
#                             "intent_name": intent_obj.name,
#                             "intent_pk": intent_obj.pk
#                         })
#                     else:
#                         intent_name_list_failure.append({
#                             "is_selected": True,
#                             "intent_name": intent_obj.name,
#                             "intent_pk": intent_obj.pk
#                         })
#                 return render(request, 'EasyChatApp/channels/android_channel.html', {
#                     "selected_bot_obj": selected_bot_obj,
#                     "bot_id": request.GET['id'],
#                     "intent_name_list": intent_name_list,
#                     "intent_name_list_failure": intent_name_list_failure
#                 })
#             else:
#                 return HttpResponseNotFound(INVALID_REQUEST)
#         else:
#             return HttpResponseRedirect("/chat/login/")
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("AndroidChannel ! %s %s", str(e), str(exc_tb.tb_lineno))
#         return None


class SaveChannelLanguageTunedObjectsAPI(APIView):
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

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)
            validation_obj = EasyChatInputValidation()
            welcome_message = data["welcome_message"]
            failure_message = data["failure_message"]
            authentication_message = data["authentication_message"]
            save_auto_pop_up_text = data['save_auto_pop_up_text']
            bot_id = data["bot_id"]
            channel_name = str(data["channel_name"])
            channel_name = channel_name.strip()
            selected_language = data["selected_language"]
            selected_language = str(selected_language).strip()

            bot = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            channel = Channel.objects.filter(name=channel_name)[0]

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot_channel = BotChannel.objects.filter(
                bot=bot, channel=channel)[0]
            lang_obj = Language.objects.get(lang=selected_language)
            language_tuned_object = LanguageTunedBotChannel.objects.filter(
                language=lang_obj, bot_channel=bot_channel)[0]
            language_tuned_object.welcome_message = welcome_message
            language_tuned_object.failure_message = failure_message
            language_tuned_object.authentication_message = authentication_message

            if channel.name == "Web" and save_auto_pop_up_text:
                auto_pop_up_text = validation_obj.sanitize_html(data["auto_popup_text"])
                lang_tuned_bot_obj = LanguageTunedBot.objects.filter(
                    language=lang_obj, bot=bot)[0]
                lang_tuned_bot_obj.auto_pop_up_text = auto_pop_up_text
                lang_tuned_bot_obj.save()

            if channel.name == "WhatsApp":
                is_catalogue_enabled = data['is_catalogue_enabled']
                if is_catalogue_enabled:
                    catalogue_metadata = data['catalogue_metadata']
                    catalogue_type = catalogue_metadata['catalogue_type']
                    error_message, catalogue_metadata = validate_catalogue_details(catalogue_type, catalogue_metadata)
                    if error_message is not None:
                        response["status"] = "400"
                        response["message"] = error_message
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(json.dumps(response))
                        return Response(data=response)
                    catalogue_metadata = json.dumps(catalogue_metadata)
                    LanguageTunedBot.objects.filter(
                        language=lang_obj, bot=bot).update(whatsapp_catalogue_data=catalogue_metadata)
                is_enabled_block_spam_user = data["is_enabled_block_spam_user"]
                if is_enabled_block_spam_user:
                    query_warning_message_text = data["query_warning_message_text"]
                    query_block_message_text = data["query_block_message_text"]
                    keywords_warning_message_text = data["keywords_warning_message_text"]
                    keywords_block_message_text = data["keywords_block_message_text"]

                    message_list = [query_warning_message_text, query_block_message_text, 
                                    keywords_warning_message_text, keywords_block_message_text]

                    [query_warning_message_text, query_block_message_text, 
                        keywords_warning_message_text, keywords_block_message_text] = list(map(parse_messages, message_list))

                    response["status"], response["message"] = check_channel_warning_and_block_message(
                        query_warning_message_text, query_block_message_text,
                        keywords_warning_message_text, keywords_block_message_text)

                    if response["status"] == 400:
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(json.dumps(response))
                        return Response(data=response)

                    block_spam_data = json.dumps({
                        "query_warning_message_text": query_warning_message_text,
                        "query_block_message_text": query_block_message_text,
                        "keywords_warning_message_text": keywords_warning_message_text,
                        "keywords_block_message_text": keywords_block_message_text
                    })
                    language_tuned_object.block_spam_data = block_spam_data

            language_tuned_object.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveChannelLanguageTunedObjectsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveWebChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]
            # welcome_message = validation_obj.custom_remo_html_tags(welcome_message)
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            # failure_message = validation_obj.custom_remo_html_tags(failure_message)
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            # authentication_message = validation_obj.custom_remo_html_tags(authentication_message)
            authentication_message = validation_obj.clean_html(
                authentication_message)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            initial_message_list = data["initial_message_list"]
            initial_questions_new_tag_list = data["initial_questions_new_tag_list"]
            failure_recommendation_list = data["failure_recommendation_list"]
            image_url = data["image_url"]
            compressed_image_url = data["compressed_image_url"]
            video_url = data["video_url"]
            bot_id = data["bot_id"]
            carousel_img_url_list = data["carousel_img_url_list"]
            redirect_url_list = data["redirect_url_list"]
            compressed_img_url_list = data["compressed_img_url_list"]
            bot_theme_color = data["bot_theme_color"]
            is_enable_gradient = data["is_enable_gradient"]
            bot_position = data["bot_position"]
            theme_selected = data["theme_selected"]
            is_minimization_enabled = data["is_minimization_enabled"]
            sticky_intent_list = data["sticky_intent_list"]
            is_automatic_carousel_enabled = data[
                "is_automatic_carousel_enabled"]
            sticky_intent_list_menu = data["sticky_intent_list_menu"]
            sticky_button_format = data["sticky_button_format"]
            hamburger_items = data["hamburger_items"]
            quick_items = data["quick_items"]
            is_automatic_carousel_enabled = data[
                "is_automatic_carousel_enabled"]
            carousel_time = data["carousel_time"]
            is_auto_popup_enabled_desktop = data[
                "is_auto_popup_enabled_desktop"]
            is_auto_popup_enabled_mobile = data["is_auto_popup_enabled_mobile"]
            auto_popup_timer = data["auto_popup_timer"]
            auto_popup_type = data["auto_popup_type"]
            auto_popup_text = validation_obj.sanitize_html(data["auto_popup_text"])
            auto_popup_initial_message_list = data["auto_popup_initial_message_list"]
            is_auto_popup_inactivity_enabled = data["is_auto_popup_inactivity_enabled"]
            selected_supported_languages = data["selected_supported_languages"]
            is_web_bot_phonetic_typing_enabled = data[
                "is_web_bot_phonetic_typing_enabled"]
            disclaimer_message = data["disclaimer_message"]
            is_form_assist_enabled = data["is_form_assist_enabled"]
            is_voice_based_form_assist_enabled = data["is_voice_based_form_assist_enabled"]
            enable_response_form_assist = data["enable_response_form_assist"]
            form_assist_auto_popup_type = data["form_assist_auto_popup_type"]
            form_assist_autopop_up_timer = data["form_assist_autopop_up_timer"]
            form_assist_autopop_up_inactivity_timer = data["form_assist_autopop_up_inactivity_timer"]
            form_assist_intent_bubble_timer = data["form_assist_intent_bubble_timer"]
            form_assist_intent_bubble_inactivity_timer = data[
                "form_assist_intent_bubble_inactivity_timer"]
            form_assist_intent_bubble_type = data["form_assist_intent_bubble_type"]
            form_assist_auto_pop_text = validation_obj.sanitize_html(data["form_assist_auto_pop_text"])
            form_assist_intents = data["form_assist_intents"]
            welcome_banner_id_list = data["welcome_banner_list"]
            is_language_auto_detection_enabled = data["is_language_auto_detection_enabled"]
            is_enabled_intent_icon = data["is_enabled_intent_icon"]
            intent_icon_channel_choices = data["intent_icon_channel_choices"]
            is_textfield_input_enabled = data["is_textfield_input_enabled"]
            disable_auto_popup_minimized = data["disable_auto_popup_minimized"]
            enable_custom_intent_bubbles = data["enable_custom_intent_bubbles"]
            custom_intents_for = data["custom_intents_for"]

            disclaimer_message = str(BeautifulSoup(
                disclaimer_message, 'html.parser'))
            disclaimer_message = disclaimer_message.strip()
            if is_web_bot_phonetic_typing_enabled:
                if disclaimer_message == "":
                    response["status"] = 400
                    response[
                        "message"] = "Disclaimer message cannot be left blank"
                if len(disclaimer_message) > 256:
                    response["status"] = 400
                    response["message"] = "Disclaimer message Too Long"

            if form_assist_auto_pop_text.strip() == "" and form_assist_auto_popup_type == "2" and is_form_assist_enabled:
                response["status"] = 400
                response["message"] = "Auto popup text cannot be empty."

            if form_assist_intent_bubble_type == "2" and len(form_assist_intents) == 0 and form_assist_auto_popup_type == "2" and is_form_assist_enabled:
                response["status"] = 400
                response["message"] = "Please select intent for form assist intent bubble"

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if form_assist_autopop_up_timer == "":
                form_assist_autopop_up_timer = 10

            if form_assist_autopop_up_inactivity_timer == "":
                form_assist_autopop_up_inactivity_timer = 5

            if form_assist_intent_bubble_timer == "":
                form_assist_intent_bubble_timer = 10

            if form_assist_intent_bubble_inactivity_timer == "":
                form_assist_intent_bubble_inactivity_timer = 5

            images = []
            if image_url != "":
                images = [image_url]

            compressed_images = []
            if compressed_image_url != "":
                compressed_images = [compressed_image_url]

            videos = []
            if video_url != "":
                if validation_obj.is_valid_url(video_url):
                    videos = [video_url]

            bot = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if request.user not in bot.users.all():
                return HttpResponseForbidden("You do not have access to this page")

            Intent.objects.filter(bots=bot).update(
                is_part_of_initial_web_trigger_intent=False)

            final_initial_questions_new_tag_list = []
            for idx, value in enumerate(initial_message_list):
                obj = {str(value): initial_questions_new_tag_list[idx]}
                final_initial_questions_new_tag_list.append(obj)

            for intent_obj_pk in auto_popup_initial_message_list:
                intent_obj = Intent.objects.filter(
                    pk=int(intent_obj_pk), is_deleted=False, bots=bot)[0]
                intent_obj.is_part_of_initial_web_trigger_intent = True
                intent_obj.save()

            bot.default_theme = get_easychat_theme_obj(theme_selected)
            bot.bot_theme_color = bot_theme_color
            bot.is_enable_gradient = is_enable_gradient
            bot.bot_position = bot_position
            bot.is_minimization_enabled = is_minimization_enabled
            bot.disable_auto_popup_minimized = disable_auto_popup_minimized
            bot.is_auto_pop_allowed_desktop = is_auto_popup_enabled_desktop
            bot.is_auto_pop_allowed_mobile = is_auto_popup_enabled_mobile
            bot.auto_popup_type = auto_popup_type
            bot.auto_pop_timer = auto_popup_timer
            bot.is_form_assist_enabled = is_form_assist_enabled
            if is_form_assist_enabled:
                bot.is_lead_generation_enabled = False

            bot.is_auto_popup_inactivity_enabled = is_auto_popup_inactivity_enabled
            is_auto_pop_up_text_updated = "false"
            if bot.auto_pop_text != auto_popup_text and (int(auto_popup_type) == 2 or int(auto_popup_type) == 3):
                is_auto_pop_up_text_updated = "true"
            bot.auto_pop_text = auto_popup_text
            bot.auto_popup_initial_messages = json.dumps(
                auto_popup_initial_message_list)
            bot.save()

            bot_info_obj = BotInfo.objects.get(bot=bot)
            bot_info_obj.enable_custom_intent_bubbles = enable_custom_intent_bubbles
            if(custom_intents_for != ""):
                if(CUSTOM_INTENTS_FOR_DICT[custom_intents_for] == AUTO_POPUP):
                    if(is_auto_popup_enabled_desktop == False and is_auto_popup_enabled_mobile == False):
                        bot_info_obj.enable_custom_intent_bubbles = False
                elif(CUSTOM_INTENTS_FOR_DICT[custom_intents_for] == FORM_ASSIST):
                    if(not is_form_assist_enabled):
                        bot_info_obj.enable_custom_intent_bubbles = False

            bot_info_obj.enable_intent_icon = is_enabled_intent_icon
            if is_enabled_intent_icon:
                intent_icon_selected_channel_choices = bot_info_obj.get_intent_icon_channel_choices_info()
                intent_icon_selected_channel_choices["web"] = intent_icon_channel_choices
                bot_info_obj.intent_icon_channel_choices_info = json.dumps(intent_icon_selected_channel_choices)
                
            if custom_intents_for != "":
                bot_info_obj.custom_intents_for = CUSTOM_INTENTS_FOR_DICT[custom_intents_for]
            bot_info_obj.save()

            form_assist_obj = FormAssistBotData.objects.filter(bot=bot)
            if form_assist_obj.exists():
                form_assist_obj = form_assist_obj[0]
            else:
                form_assist_obj = FormAssistBotData.objects.create(bot=bot)
            form_assist_obj.form_assist_auto_popup_type = form_assist_auto_popup_type
            form_assist_obj.form_assist_autopop_up_timer = form_assist_autopop_up_timer
            form_assist_obj.form_assist_autopop_up_inactivity_timer = form_assist_autopop_up_inactivity_timer
            form_assist_obj.form_assist_intent_bubble_timer = form_assist_intent_bubble_timer
            form_assist_obj.form_assist_intent_bubble_inactivity_timer = form_assist_intent_bubble_inactivity_timer
            form_assist_obj.form_assist_intent_bubble_type = form_assist_intent_bubble_type
            form_assist_obj.form_assist_auto_pop_text = form_assist_auto_pop_text
            form_assist_intent_objs = Intent.objects.filter(
                pk__in=form_assist_intents)
            form_assist_obj.form_assist_intent_bubble.clear()
            form_assist_obj.form_assist_intent_bubble.add(
                *form_assist_intent_objs)
            form_assist_obj.is_voice_based_form_assist_enabled = is_voice_based_form_assist_enabled
            form_assist_obj.enable_response_form_assist = enable_response_form_assist
            form_assist_obj.save()

            check_and_create_bot_language_template_obj(
                bot, selected_supported_languages, RequiredBotTemplate, Language)

            channels = Channel.objects.filter(name__in=["Web"])
            for channel_bot in channels:
                channel = BotChannel.objects.get(bot=bot, channel=channel_bot)
                channel.languages_supported.clear()
                channel.is_textfield_input_enabled = is_textfield_input_enabled
                for selected_lang in selected_supported_languages:
                    lang_obj = Language.objects.get(lang=selected_lang)
                    channel.languages_supported.add(lang_obj)
                activity_update = json.loads(channel.activity_update)

                is_welcome_message_updated = "false"
                if channel.welcome_message != welcome_message:
                    is_welcome_message_updated = "true"
                channel.welcome_message = welcome_message
                is_failure_message_updated = "false"
                if channel.failure_message != failure_message:
                    is_failure_message_updated = "true"
                channel.failure_message = failure_message
                is_authentication_message_updated = "false"
                if channel.authentication_message != authentication_message:
                    is_authentication_message_updated = "true"
                channel.authentication_message = authentication_message
                activity_update[
                    "is_welcome_message_updated"] = is_welcome_message_updated
                activity_update[
                    "is_failure_message_updated"] = is_failure_message_updated
                activity_update[
                    "is_authentication_message_updated"] = is_authentication_message_updated
                activity_update[
                    "is_auto_pop_up_text_updated"] = is_auto_pop_up_text_updated
                activity_update["is_web_prompt_message_updated"] = "false"
                # editing web prompt message has a diffrent api its upated or
                # not is handled thier here in saving web channel marking
                # is_web_prompt_message_updated false
                channel.activity_update = json.dumps(activity_update)
                channel.is_web_bot_phonetic_typing_enabled = is_web_bot_phonetic_typing_enabled
                if is_web_bot_phonetic_typing_enabled:
                    channel.phonetic_typing_disclaimer_text = disclaimer_message
                channel.initial_messages = json.dumps(
                    {"items": initial_message_list, "images": images, "compressed_images": compressed_images, "videos": videos, "new_tag_list": final_initial_questions_new_tag_list})
                channel.image_url = json.dumps(
                    {
                        "items": carousel_img_url_list,
                        "compressed_items": compressed_img_url_list,
                    })
                channel.redirection_url = json.dumps(
                    {"items": redirect_url_list})
                channel.failure_recommendations = json.dumps(
                    {"items": failure_recommendation_list})

                channel.sticky_button_display_format = sticky_button_format
                if sticky_button_format == "Menu":
                    channel.sticky_intent_menu = json.dumps(
                        {"items": sticky_intent_list_menu})
                else:
                    channel.sticky_intent = json.dumps(
                        {"items": sticky_intent_list})

                channel.hamburger_items = json.dumps(
                    {"items": hamburger_items})

                channel.quick_items = json.dumps(
                    {"items": quick_items})

                channel.is_automatic_carousel_enabled = is_automatic_carousel_enabled

                if is_automatic_carousel_enabled:
                    channel.carousel_time = carousel_time

                count = 1
                for welcome_banner_id in welcome_banner_id_list:
                    welcome_banner_obj = WelcomeBanner.objects.get(
                        pk=welcome_banner_id)
                    welcome_banner_obj.serial_number = count
                    welcome_banner_obj.save()
                    count += 1

                channel.is_language_auto_detection_enabled = is_language_auto_detection_enabled
                if "is_bot_notification_sound_enabled" in data:
                    channel.is_bot_notification_sound_enabled = data[
                        "is_bot_notification_sound_enabled"]
                elif theme_selected == 'theme_1':
                    channel.is_bot_notification_sound_enabled = True

                channel.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveWebChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveGoogleHomeChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]
            # welcome_message = validation_obj.custom_remo_html_tags(welcome_message)
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            # failure_message = validation_obj.custom_remo_html_tags(failure_message)
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            # authentication_message = validation_obj.custom_remo_html_tags(authentication_message)
            authentication_message = validation_obj.clean_html(
                authentication_message)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            initial_message_list = data["initial_message_list"]
            failure_recommendation_list = data["failure_recommendation_list"]
            image_url = data["image_url"]
            video_url = data["video_url"]
            bot_id = data["bot_id"]

            welcome_message = validation_obj.remo_html_from_string(
                welcome_message)

            images = []
            if image_url != "":
                images = [image_url]

            videos = []
            if video_url != "":
                videos = [video_url]

            initial_message_list = [
                str(message) for message in initial_message_list if message != ""]

            bot = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if user_obj not in bot.users.all():
                return HttpResponseForbidden("You do not have access to this page")
            channel = Channel.objects.get(name="GoogleHome")
            channel = BotChannel.objects.get(bot=bot, channel=channel)
            channel.initial_messages = json.dumps(
                {"items": initial_message_list, "images": images, "videos": videos})
            channel.failure_recommendations = json.dumps(
                {"items": failure_recommendation_list})

            # Language specific
            language_specific_action(
                data, channel, bot, welcome_message, failure_message, authentication_message)

            channel.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveGoogleHomeChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveAlexaChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]
            # welcome_message = validation_obj.custom_remo_html_tags(welcome_message)
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            # failure_message = validation_obj.custom_remo_html_tags(failure_message)
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            # authentication_message = validation_obj.custom_remo_html_tags(authentication_message)
            authentication_message = validation_obj.clean_html(
                authentication_message)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            initial_message_list = data["initial_message_list"]
            failure_recommendation_list = data["failure_recommendation_list"]
            image_url = data["image_url"]
            video_url = data["video_url"]
            bot_id = data["bot_id"]

            welcome_message = validation_obj.remo_html_from_string(
                welcome_message)

            images = []
            if image_url != "":
                images = [image_url]

            videos = []
            if video_url != "":
                videos = [video_url]

            initial_message_list = [
                str(message) for message in initial_message_list if message != ""]

            bot = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
              
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if user_obj not in bot.users.all():
                return HttpResponseForbidden("You do not have access to this page")
            channel = Channel.objects.get(name="Alexa")
            channel = BotChannel.objects.get(bot=bot, channel=channel)

            # Language specific
            language_specific_action(
                data, channel, bot, welcome_message, failure_message, authentication_message)

            channel.initial_messages = json.dumps(
                {"items": initial_message_list, "images": images, "videos": videos})
            channel.failure_recommendations = json.dumps(
                {"items": failure_recommendation_list})
            channel.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveAlexaChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveAndroidChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]
            # welcome_message = validation_obj.custom_remo_html_tags(welcome_message)
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            # failure_message = validation_obj.custom_remo_html_tags(failure_message)
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            # authentication_message = validation_obj.custom_remo_html_tags(authentication_message)
            authentication_message = validation_obj.clean_html(
                authentication_message)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            initial_message_list = data["initial_message_list"]
            failure_recommendation_list = data["failure_recommendation_list"]
            image_url = data["image_url"]
            compressed_image_url = data["compressed_image_url"]
            video_url = data["video_url"]
            bot_id = data["bot_id"]
            carousel_img_url_list = data["carousel_img_url_list"]
            redirect_url_list = data["redirect_url_list"]
            compressed_img_url_list = data["compressed_img_url_list"]
            bot_theme_color = data["bot_theme_color"]
            theme_selected = data["theme_selected"]
            sticky_intent_list = data["sticky_intent_list"]
            is_automatic_carousel_enabled = data[
                "is_automatic_carousel_enabled"]
            sticky_intent_list_menu = data["sticky_intent_list_menu"]
            sticky_button_format = data["sticky_button_format"]
            is_automatic_carousel_enabled = data[
                "is_automatic_carousel_enabled"]
            carousel_time = data["carousel_time"]
            selected_supported_languages = data["selected_supported_languages"]
            is_web_bot_phonetic_typing_enabled = data["is_web_bot_phonetic_typing_enabled"]
            disclaimer_message = data["disclaimer_message"]
            welcome_banner_id_list = data["welcome_banner_list"]
            is_language_auto_detection_enabled = data["is_language_auto_detection_enabled"]
            is_enabled_intent_icon = data["is_enabled_intent_icon"]
            intent_icon_channel_choices = data["intent_icon_channel_choices"]
            is_textfield_input_enabled = data["is_textfield_input_enabled"]

            disclaimer_message = str(BeautifulSoup(
                disclaimer_message, 'html.parser'))
            disclaimer_message = disclaimer_message.strip()
            if is_web_bot_phonetic_typing_enabled:
                if disclaimer_message == "":
                    response["status"] = 400
                    response["message"] = "Disclaimer message cannot be left blank"
                if len(disclaimer_message) > 256:
                    response["status"] = 400
                    response["message"] = "Disclaimer message Too Long"

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            images = url_to_list(image_url)
            compressed_images = url_to_list(compressed_image_url)
            videos = url_to_list(video_url)

            bot = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if user_obj not in bot.users.all():
                return HttpResponseForbidden("You do not have access to this page")
            bot_info_obj = BotInfo.objects.get(bot=bot)

            bot_info_obj.enable_intent_icon = is_enabled_intent_icon
            if is_enabled_intent_icon:
                intent_icon_selected_channel_choices = bot_info_obj.get_intent_icon_channel_choices_info()
                intent_icon_selected_channel_choices["android"] = intent_icon_channel_choices
                bot_info_obj.intent_icon_channel_choices_info = json.dumps(intent_icon_selected_channel_choices)
            bot_info_obj.save()

            Intent.objects.filter(bots=bot).update(
                is_part_of_initial_web_trigger_intent=False)

            bot.default_theme = get_easychat_theme_obj(theme_selected)
            bot.bot_theme_color = bot_theme_color
            bot.save()
            check_and_create_bot_language_template_obj(
                bot, selected_supported_languages, RequiredBotTemplate, Language)

            channels = Channel.objects.filter(name__in=["Android"])
            for channel_bot in channels:
                channel = BotChannel.objects.get(bot=bot, channel=channel_bot)
                channel.languages_supported.clear()
                channel.is_textfield_input_enabled = is_textfield_input_enabled
                for selected_lang in selected_supported_languages:
                    lang_obj = Language.objects.get(lang=selected_lang)
                    channel.languages_supported.add(lang_obj)
                activity_update = json.loads(channel.activity_update)
                is_welcome_message_updated = "false"
                if channel.welcome_message != welcome_message:
                    is_welcome_message_updated = "true"
                channel.welcome_message = welcome_message
                is_failure_message_updated = "false"
                if channel.failure_message != failure_message:
                    is_failure_message_updated = "true"
                channel.failure_message = failure_message
                is_authentication_message_updated = "false"
                if channel.authentication_message != authentication_message:
                    is_authentication_message_updated = "true"
                channel.authentication_message = authentication_message
                activity_update["is_welcome_message_updated"] = is_welcome_message_updated
                activity_update["is_failure_message_updated"] = is_failure_message_updated
                activity_update["is_authentication_message_updated"] = is_authentication_message_updated
                activity_update["is_web_prompt_message_updated"] = "false"
                # editing web prompt message has a diffrent api its upated or not is handled thier here in saving web channel marking is_web_prompt_message_updated false
                channel.activity_update = json.dumps(activity_update)
                channel.is_web_bot_phonetic_typing_enabled = is_web_bot_phonetic_typing_enabled
                if is_web_bot_phonetic_typing_enabled:
                    channel.phonetic_typing_disclaimer_text = disclaimer_message
                channel.initial_messages = json.dumps(
                    {"items": initial_message_list, "images": images, "compressed_images": compressed_images, "videos": videos})
                channel.image_url = json.dumps(
                    {
                        "items": carousel_img_url_list,
                        "compressed_items": compressed_img_url_list,
                    })
                channel.redirection_url = json.dumps(
                    {"items": redirect_url_list})
                channel.failure_recommendations = json.dumps(
                    {"items": failure_recommendation_list})

                channel.sticky_button_display_format = sticky_button_format
                if sticky_button_format == "Menu":
                    channel.sticky_intent_menu = json.dumps(
                        {"items": sticky_intent_list_menu})
                else:
                    channel.sticky_intent = json.dumps(
                        {"items": sticky_intent_list})

                channel.is_automatic_carousel_enabled = is_automatic_carousel_enabled

                if is_automatic_carousel_enabled:
                    channel.carousel_time = carousel_time

                count = 1
                for welcome_banner_id in welcome_banner_id_list:
                    welcome_banner_obj = WelcomeBanner.objects.get(
                        pk=welcome_banner_id)
                    welcome_banner_obj.serial_number = count
                    welcome_banner_obj.save()
                    count += 1

                if "is_bot_notification_sound_enabled" in data:
                    channel.is_bot_notification_sound_enabled = data[
                        "is_bot_notification_sound_enabled"]
                elif theme_selected == 'theme_1':
                    channel.is_bot_notification_sound_enabled = True

                channel.is_language_auto_detection_enabled = is_language_auto_detection_enabled

                channel.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveAndroidChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveWhatsAppChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]
            # welcome_message = validation_obj.custom_remo_html_tags(welcome_message)
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            # failure_message = validation_obj.custom_remo_html_tags(failure_message)
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            # authentication_message = validation_obj.custom_remo_html_tags(authentication_message)
            authentication_message = validation_obj.clean_html(
                authentication_message)
            is_language_auto_detection_enabled = data["is_language_auto_detection_enabled"]

            ## Block configs
            is_enabled_block_spam_user = data["is_enabled_block_spam_user"]
            is_enabled_block_spam_query = data["is_enabled_block_spam_query"]
            is_enabled_block_spam_keywords = data["is_enabled_block_spam_keywords"]
            query_warning_message_thresold = min(int(float(data["query_warning_message_thresold"])), BLOCK_SPAM_WARNING_THRESOLD_MAX_VALUE)
            query_block_message_thresold = max(int(float(data["query_block_message_thresold"])), query_warning_message_thresold + 1)
            query_block_message_thresold = min(query_block_message_thresold, BLOCK_SPAM_BLOCK_THRESOLD_MAX_VALUE)
            query_block_duration = min(int(float(data["query_block_duration"])), BLOCK_SPAM_BLOCK_MAX_DURATION)
            keywords_warning_message_thresold = min(int(float(data["keywords_warning_message_thresold"])), BLOCK_SPAM_WARNING_THRESOLD_MAX_VALUE)
            keywords_block_message_thresold = max(int(float(data["keywords_block_message_thresold"])), keywords_warning_message_thresold + 1)
            keywords_block_message_thresold = min(keywords_block_message_thresold, BLOCK_SPAM_BLOCK_THRESOLD_MAX_VALUE)
            keywords_block_duration = min(int(float(data["keywords_block_duration"])), BLOCK_SPAM_BLOCK_MAX_DURATION)
            spam_keywords = data["spam_keywords"]
            spam_keywords = set(map(validation_obj.remo_html_from_string, spam_keywords))
            spam_keywords = ",".join(spam_keywords)
            query_warning_message_text = data["query_warning_message_text"]
            query_warning_message_text = validation_obj.clean_html(query_warning_message_text)
            query_block_message_text = data["query_block_message_text"]
            query_block_message_text = validation_obj.clean_html(query_block_message_text)
            keywords_warning_message_text = data["keywords_warning_message_text"]
            keywords_warning_message_text = validation_obj.clean_html(keywords_warning_message_text)
            keywords_block_message_text = data["keywords_block_message_text"]
            keywords_block_message_text = validation_obj.clean_html(keywords_block_message_text)
            username = validation_obj.remo_html_from_string(data["username"])
            password = validation_obj.remo_html_from_string(data["password"])
            host_url = data["host_url"].strip()
            is_enable_choose_language_flow_enabled_for_welcome_response = data[
                "is_enable_choose_language_flow_enabled_for_welcome_response"]

            message_list = [welcome_message, failure_message, authentication_message,
                            query_warning_message_text, query_block_message_text, 
                            keywords_warning_message_text, keywords_block_message_text]

            [welcome_message, failure_message, authentication_message,
                query_warning_message_text, query_block_message_text, 
                keywords_warning_message_text, keywords_block_message_text] = list(map(parse_messages, message_list))

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if is_enabled_block_spam_user:
                response["status"], response["message"] = check_channel_warning_and_block_message(
                    query_warning_message_text, query_block_message_text,
                    keywords_warning_message_text, keywords_block_message_text)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            initial_message_list = data["initial_message_list"]
            failure_recommendation_list = data["failure_recommendation_list"]
            image_url = data["image_url"]
            video_url = data["video_url"]
            bot_id = data["bot_id"]
            is_email_notifiication_enabled = data[
                "is_email_notifiication_enabled"]

            integrated_whatsapp_mobile = data["integrated_whatsapp_mobile"]

            integrated_whatsapp_mobile = validation_obj.remo_html_from_string(
                integrated_whatsapp_mobile)

            mobile_number_masking_enabled = data["whatsapp_number_masking"]
            selected_supported_languages = data["selected_supported_languages"]

            images = []
            if image_url != "":
                images = [image_url]

            videos = []
            if video_url != "":
                videos = [video_url]

            initial_message_list = [
                str(message) for message in initial_message_list if message != ""]

            bot = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if request.user not in bot.users.all():
                return HttpResponseForbidden("You do not have access to this page")
            channel = Channel.objects.get(name="WhatsApp")
            channel = BotChannel.objects.get(bot=bot, channel=channel)
            block_config = BlockConfig.objects.filter(bot=bot).first()

            if not block_config:
                block_config = BlockConfig.objects.create(bot=bot)
            
            is_whatsapp_credential_valid, status_message = check_if_whatsapp_credentials_are_valid(validation_obj, username, password, host_url)

            if not is_whatsapp_credential_valid:
                response["status"] = 400
                response["message"] = status_message
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            whatsapp_credentials_obj = WhatsappCredentialsConfig.objects.filter(bot=bot).first()

            if not whatsapp_credentials_obj:
                whatsapp_credentials_obj = WhatsappCredentialsConfig.objects.create(bot=bot)

            whatsapp_credentials_obj.username = username
            whatsapp_credentials_obj.password = password
            whatsapp_credentials_obj.host_url = host_url
            whatsapp_credentials_obj.save(update_fields=["username", "password", "host_url"])

            whatsapp_vendor_obj = WhatsAppVendorConfig.objects.filter(session_api_host=host_url).first()

            if not whatsapp_vendor_obj:
                WhatsAppVendorConfig.objects.create(wsp_name="1", username=username, password=password, session_api_host=host_url)

            check_and_create_bot_language_template_obj(
                bot, selected_supported_languages, RequiredBotTemplate, Language)
            channel.languages_supported.clear()
            for selected_lang in selected_supported_languages:
                lang_obj = Language.objects.get(lang=selected_lang)
                channel.languages_supported.add(lang_obj)
            activity_update = json.loads(channel.activity_update)
            is_welcome_message_updated = "false"
            if channel.welcome_message != welcome_message:
                is_welcome_message_updated = "true"
            channel.welcome_message = welcome_message
            is_failure_message_updated = "false"
            if channel.failure_message != failure_message:
                is_failure_message_updated = "true"
            channel.failure_message = failure_message
            is_authentication_message_updated = "false"
            if channel.authentication_message != authentication_message:
                is_authentication_message_updated = "true"
            channel.authentication_message = authentication_message
            is_block_spam_data_updated = "false"
            block_spam_field = ""

            if is_enabled_block_spam_user:
                if block_config.user_query_warning_message_text != query_warning_message_text:
                    is_block_spam_data_updated = "true"
                    block_spam_field += "query_warning "
                if block_config.user_query_block_message_text != query_block_message_text:
                    is_block_spam_data_updated = "true"
                    block_spam_field += "query_block "
                if block_config.spam_keywords_warning_message_text != keywords_warning_message_text:
                    is_block_spam_data_updated = "true"
                    block_spam_field += "keyword_warning "
                if block_config.spam_keywords_block_message_text != keywords_block_message_text:
                    is_block_spam_data_updated = "true"
                    block_spam_field += "keyword_block "

            activity_update[
                "is_welcome_message_updated"] = is_welcome_message_updated
            activity_update[
                "is_failure_message_updated"] = is_failure_message_updated
            activity_update[
                "is_authentication_message_updated"] = is_authentication_message_updated
            activity_update[
                "is_block_spam_data_updated"] = is_block_spam_data_updated
            activity_update[
                "block_spam_field"] = block_spam_field
            
            channel.is_language_auto_detection_enabled = is_language_auto_detection_enabled
            channel.is_enable_choose_language_flow_enabled_for_welcome_response = is_enable_choose_language_flow_enabled_for_welcome_response
            # channel.welcome_message = welcome_message
            # channel.failure_message = failure_message
            # channel.authentication_message = authentication_message
            channel.is_email_notifiication_enabled = is_email_notifiication_enabled
            channel.initial_messages = json.dumps(
                {"items": initial_message_list, "images": images, "videos": videos})
            channel.failure_recommendations = json.dumps(
                {"items": failure_recommendation_list})
            channel.integrated_whatsapp_mobile = integrated_whatsapp_mobile
            channel.mobile_number_masking_enabled = mobile_number_masking_enabled
            is_catalogue_enabled = data['is_catalogue_enabled']
            if is_catalogue_enabled:
                catalogue_metadata = data['catalogue_metadata']
                catalogue_via = data["catalogue_via"]
                error_message, catalogue_metadata = validate_catalogue_details(catalogue_via, catalogue_metadata)
                if error_message is not None:
                    response["status"] = "400"
                    response["message"] = error_message
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
                activity_update = check_and_update_catalogue_fine_tuning(
                    bot, activity_update, catalogue_via, catalogue_metadata, WhatsappCatalogueDetails, EasyChatTranslationCache)
                catalogue_id = catalogue_metadata["catalogue_id"]
                catalogue_metadata = json.dumps(catalogue_metadata)
                catalogue_count = WhatsappCatalogueDetails.objects.filter(
                    bot=bot).update(catalogue_metadata=catalogue_metadata, 
                                    catalogue_type=catalogue_via, 
                                    is_catalogue_enabled=is_catalogue_enabled,
                                    catalogue_id=catalogue_id)
                if not catalogue_count:
                    WhatsappCatalogueDetails.objects.create(bot=bot, 
                                                            catalogue_metadata=catalogue_metadata, 
                                                            catalogue_type=catalogue_via, 
                                                            is_catalogue_enabled=is_catalogue_enabled,
                                                            catalogue_id=catalogue_id)
                if catalogue_via == API_CATALOGUE_CHOICE:
                    catalogue_metadata = json.loads(catalogue_metadata)
                    catalogue_business_id = catalogue_metadata["business_id"]
                    catalogue_access_token = catalogue_metadata["access_token"]
                    WhatsappCatalogueDetails.objects.filter(
                        bot=bot).update(business_id=catalogue_business_id, 
                                        access_token=catalogue_access_token)
            else:
                WhatsappCatalogueDetails.objects.filter(
                    bot=bot).update(is_catalogue_enabled=is_catalogue_enabled)

            channel.activity_update = json.dumps(activity_update)
            update_fields = []
            block_config.is_block_spam_user_enabled = is_enabled_block_spam_user
            update_fields.append("is_block_spam_user_enabled")
            if is_enabled_block_spam_user:
                block_config.is_block_based_on_user_queries_enabled = is_enabled_block_spam_query
                update_fields.append("is_block_based_on_user_queries_enabled")
                if is_enabled_block_spam_query:
                    block_config.user_query_warning_thresold = query_warning_message_thresold
                    block_config.user_query_warning_message_text = query_warning_message_text
                    block_config.user_query_block_thresold = query_block_message_thresold
                    block_config.user_query_block_message_text = query_block_message_text
                    block_config.user_query_block_duration = query_block_duration
                    update_fields.extend([
                        "user_query_warning_thresold",
                        "user_query_warning_message_text",
                        "user_query_block_thresold",
                        "user_query_block_message_text",
                        "user_query_block_duration",
                    ])

                block_config.is_block_based_on_spam_keywords_enabled = is_enabled_block_spam_keywords
                update_fields.append("is_block_based_on_spam_keywords_enabled")
                if is_enabled_block_spam_keywords:
                    block_config.spam_keywords = spam_keywords
                    block_config.spam_keywords_warning_thresold = keywords_warning_message_thresold
                    block_config.spam_keywords_warning_message_text = keywords_warning_message_text
                    block_config.spam_keywords_block_thresold = keywords_block_message_thresold
                    block_config.spam_keywords_block_message_text = keywords_block_message_text
                    block_config.spam_keywords_block_duration = keywords_block_duration
                    update_fields.extend([
                        "spam_keywords",
                        "spam_keywords_warning_thresold",
                        "spam_keywords_warning_message_text",
                        "spam_keywords_block_thresold",
                        "spam_keywords_block_message_text",
                        "spam_keywords_block_duration",
                    ])

            channel.save()
            block_config.save(update_fields=update_fields)

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveWhatsAppChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveWatsAppEmailConfigAPI(APIView):

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

            bot_channel_pk = data['bot_channel_pk']
            mail_sender_time_interval = data["mail_sender_time_interval"]
            mail_sent_to_list = data["mail_sent_to_list"]

            bot_channel_obj = BotChannel.objects.get(pk=int(bot_channel_pk))
            bot_channel_obj.mail_sender_time_interval = mail_sender_time_interval
            bot_channel_obj.mail_sent_to_list = json.dumps(
                {"items": mail_sent_to_list})
            if len(mail_sent_to_list):
                response["email_configured"] = True
            else:
                response["email_configured"] = False
            bot_channel_obj.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveWatsAppEmailConfigAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveWatsAppEmailConfig = SaveWatsAppEmailConfigAPI.as_view()


class SendWhatsAppTestEmailAPI(APIView):

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

            bot_channel_pk = data['bot_channel_pk']

            bot_channel_obj = BotChannel.objects.get(pk=int(bot_channel_pk))

            bot_obj = bot_channel_obj.bot

            api_name = "WhatsAppTest"
            api_request_packet = {"url": "https://dummytesting.in"}
            api_response_packet = {"url": "https://dummytesting.in"}
            mail_sent_to_list = json.loads(
                bot_channel_obj.mail_sent_to_list)["items"]

            for item in mail_sent_to_list:
                thread = threading.Thread(target=send_whatsapp_endpoint_fail_mail, args=(api_name, json.dumps(
                    api_request_packet, indent=2), json.dumps(api_response_packet, indent=2), bot_obj, item), daemon=True)
                thread.start()
                logger.info("Threading started...", extra={'AppName': 'EasyChat', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SendWhatsAppTestEmailAPI! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SendWhatsAppTestEmail = SendWhatsAppTestEmailAPI.as_view()


class SaveFacebookChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]
            # welcome_message = validation_obj.custom_remo_html_tags(welcome_message)
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            # failure_message = validation_obj.custom_remo_html_tags(failure_message)
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            # authentication_message = validation_obj.custom_remo_html_tags(authentication_message)
            authentication_message = validation_obj.clean_html(
                authentication_message)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            initial_message_list = data["initial_message_list"]
            failure_recommendation_list = data["failure_recommendation_list"]
            image_url = data["image_url"]
            video_url = data["video_url"]
            bot_id = data["bot_id"]
            verification_code = data["verification_code"]
            page_access_token = data["page_access_token"]

            images = []
            if image_url != "":
                images = [image_url]

            videos = []
            if video_url != "":
                videos = [video_url]

            initial_message_list = [
                str(message) for message in initial_message_list if message != ""]

            bot = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if user_obj not in bot.users.all():
                return HttpResponseForbidden("You do not have access to this page")
            channel = Channel.objects.get(name="Facebook")
            channel = BotChannel.objects.get(bot=bot, channel=channel)

            # Language specific
            language_specific_action(
                data, channel, bot, welcome_message, failure_message, authentication_message)

            channel.initial_messages = json.dumps(
                {"items": initial_message_list, "images": images, "videos": videos})
            channel.failure_recommendations = json.dumps(
                {"items": failure_recommendation_list})
            channel.verification_code = verification_code
            channel.page_access_token = page_access_token
            channel.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveFacebookChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveInstagramChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]
            # welcome_message = validation_obj.custom_remo_html_tags(welcome_message)
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            # failure_message = validation_obj.custom_remo_html_tags(failure_message)
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            # authentication_message = validation_obj.custom_remo_html_tags(authentication_message)
            authentication_message = validation_obj.clean_html(
                authentication_message)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            initial_message_list = data["initial_message_list"]
            failure_recommendation_list = data["failure_recommendation_list"]
            image_url = data["image_url"]
            video_url = data["video_url"]
            bot_id = data["bot_id"]
            verification_code = data["verification_code"]
            page_access_token = data["page_access_token"]

            welcome_message = validation_obj.remo_html_from_string(
                welcome_message)
            images = []
            if image_url != "":
                images = [image_url]

            videos = []
            if video_url != "":
                videos = [video_url]
            
            initial_message_list = [
                str(message) for message in initial_message_list if message != ""]

            bot = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if user_obj not in bot.users.all():
                return HttpResponseForbidden("You do not have access to this page")
            channel = Channel.objects.get(name="Instagram")
            bot_channel = BotChannel.objects.get(bot=bot, channel=channel)

            # Language specific
            language_specific_action(
                data, bot_channel, bot, welcome_message, failure_message, authentication_message)

            bot_channel.failure_recommendations = json.dumps(
                {"items": failure_recommendation_list})

            bot_channel.initial_messages = json.dumps(
                {"items": initial_message_list, "images": images, "videos": videos})

            bot_channel.verification_code = verification_code
            bot_channel.page_access_token = page_access_token

            bot_channel.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveInstagramChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


# class SaveAndroidChannelDetailsAPI(APIView):

#     permission_classes = (IsAuthenticated,)

#     authentication_classes = (
#         CsrfExemptSessionAuthentication, BasicAuthentication)

#     def post(self, request, *args, **kwargs):
#         response = {}
#         response["status"] = 500
#         try:
#             data = request.data

#             if not isinstance(data, dict):
#                 data = json.loads(data)

#             json_string = DecryptVariable(data["json_string"])

#             data = json.loads(json_string)

#             welcome_message = data["welcome_message"]
#             failure_message = data["failure_message"]
#             authentication_message = data["authentication_message"]
#             initial_message_list = data["initial_message_list"]
#             failure_recommendation_list = data["failure_recommendation_list"]
#             image_url = data["image_url"]
#             video_url = data["video_url"]
#             bot_id = data["bot_id"]

#             images = []
#             if image_url != "":
#                 images = [image_url]

#             videos = []
#             if video_url != "":
#                 videos = [video_url]

#             initial_message_list = [
# str(message) for message in initial_message_list if message != ""]

#             bot = Bot.objects.get(pk=int(bot_id), is_deleted=False)
#             channel = Channel.objects.get(name="Android")
#             channel = BotChannel.objects.get(bot=bot, channel=channel)
#             channel.welcome_message = welcome_message
#             channel.failure_message = failure_message
#             channel.authentication_message = authentication_message
#             channel.initial_messages = json.dumps(
#                 {"items": initial_message_list, "images": images, "videos": videos})
#             channel.failure_recommendations = json.dumps(
#                 {"items": failure_recommendation_list})
#             channel.save()

#             response["status"] = 200
#         except Exception as e:  # noqa: F841
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error("SaveAndroidChannelDetailsAPI ! %s %s",
#                          str(e), str(exc_tb.tb_lineno))

#         custom_encrypt_obj = CustomEncrypt()
#         response = custom_encrypt_obj.encrypt(json.dumps(response))
#         return Response(data=response)


class EditWebChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_pk = data["bot_id"]
            selected_language = "en"
            if "selected_language" in data:
                selected_language = data['selected_language']
                selected_language = validation_obj.remo_html_from_string(
                    selected_language)
                selected_language = selected_language.strip()
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_uat=True, is_deleted=False)

            channel = Channel.objects.get(name="Web")
            botchannel = BotChannel.objects.get(bot=bot_obj, channel=channel)
            response["welcome_message"] = botchannel.welcome_message
            response["failure_message"] = botchannel.failure_message
            response["authentication_message"] = botchannel.authentication_message
            if selected_language != "en":
                create_language_tuned_object = True
                welcome_message, failure_message, authentication_message = check_and_create_channel_details_language_tuning_objects(
                    response, selected_language, botchannel, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                response["welcome_message"] = welcome_message
                response["failure_message"] = failure_message
                response["authentication_message"] = authentication_message
            initial_messages = json.loads(botchannel.initial_messages)
            initial_messages_list = get_message_list_using_pk(
                initial_messages["items"])

            try:
                initial_messages = {"items": initial_messages_list, "images": initial_messages[
                    "images"], "compressed_images": initial_messages["compressed_images"], "videos": initial_messages["videos"]}
            except Exception:
                initial_messages = {"items": initial_messages_list}
            response["initial_message"] = initial_messages
            response["failure_recommendations"] = get_message_list_using_pk(json.loads(
                botchannel.failure_recommendations)["items"])
            response["carousel_img_url_list"] = json.loads(
                botchannel.image_url)
            response["redirect_url_list"] = json.loads(
                botchannel.redirection_url)
            response["welcome_banner_count"] = WelcomeBanner.objects.filter(
                bot_channel=botchannel).count()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditWebChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class EditGoogleChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)
            bot_pk = data["bot_id"]
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_deleted=False)

            channel = Channel.objects.get(name="GoogleHome")
            botchannel = BotChannel.objects.get(bot=bot_obj, channel=channel)
            response["welcome_message"] = botchannel.welcome_message
            response["failure_message"] = botchannel.failure_message
            response["authentication_message"] = botchannel.authentication_message
            initial_messages = json.loads(botchannel.initial_messages)
            initial_messages_list = get_message_list_using_pk(
                initial_messages["items"])

            try:
                initial_messages = {"items": initial_messages_list, "images": initial_messages[
                    "images"], "videos": initial_messages["videos"]}
            except Exception:
                initial_messages = {"items": initial_messages_list}
            response["initial_message"] = initial_messages
            response["failure_recommendations"] = get_message_list_using_pk(json.loads(
                botchannel.failure_recommendations)["items"])
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditGoogleChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class EditAlexaChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data["bot_id"]
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_deleted=False)

            channel = Channel.objects.get(name="Alexa")
            botchannel = BotChannel.objects.get(bot=bot_obj, channel=channel)
            response["welcome_message"] = botchannel.welcome_message
            response["failure_message"] = botchannel.failure_message
            response["authentication_message"] = botchannel.authentication_message
            initial_messages = json.loads(botchannel.initial_messages)
            initial_messages_list = get_message_list_using_pk(
                initial_messages["items"])

            try:
                initial_messages = {"items": initial_messages_list, "images": initial_messages[
                    "images"], "videos": initial_messages["videos"]}
            except Exception:
                initial_messages = {"items": initial_messages_list}
            response["initial_message"] = initial_messages
            response["failure_recommendations"] = get_message_list_using_pk(json.loads(
                botchannel.failure_recommendations)["items"])
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditAlexaChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class EditAndroidChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_pk = data["bot_id"]
            selected_language = "en"
            if "selected_language" in data:
                selected_language = data['selected_language']
                selected_language = validation_obj.remo_html_from_string(
                    selected_language)
                selected_language = selected_language.strip()
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_uat=True, is_deleted=False)

            channel = Channel.objects.get(name="Android")
            botchannel = BotChannel.objects.get(bot=bot_obj, channel=channel)
            response["welcome_message"] = botchannel.welcome_message
            response["failure_message"] = botchannel.failure_message
            response["authentication_message"] = botchannel.authentication_message
            if selected_language != "en":
                create_language_tuned_object = True
                welcome_message, failure_message, authentication_message = check_and_create_channel_details_language_tuning_objects(
                    response, selected_language, botchannel, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                response["welcome_message"] = welcome_message
                response["failure_message"] = failure_message
                response["authentication_message"] = authentication_message
            initial_messages = json.loads(botchannel.initial_messages)
            initial_messages_list = get_message_list_using_pk(
                initial_messages["items"])

            try:
                initial_messages = {"items": initial_messages_list, "images": initial_messages[
                    "images"], "compressed_images": initial_messages["compressed_images"], "videos": initial_messages["videos"]}
            except Exception:
                initial_messages = {"items": initial_messages_list}
            response["initial_message"] = initial_messages
            response["failure_recommendations"] = get_message_list_using_pk(json.loads(
                botchannel.failure_recommendations)["items"])
            response["carousel_img_url_list"] = json.loads(
                botchannel.image_url)
            response["redirect_url_list"] = json.loads(
                botchannel.redirection_url)
            response["welcome_banner_count"] = WelcomeBanner.objects.filter(
                bot_channel=botchannel).count()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditAndroidChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class EditWhatsAppChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data["bot_id"]
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_deleted=False)

            channel = Channel.objects.get(name="WhatsApp")
            botchannel = BotChannel.objects.get(bot=bot_obj, channel=channel)
            response["welcome_message"] = botchannel.welcome_message
            response["failure_message"] = botchannel.failure_message
            response["authentication_message"] = botchannel.authentication_message
            initial_messages = json.loads(botchannel.initial_messages)
            initial_messages_list = get_message_list_using_pk(
                initial_messages["items"])
            try:
                initial_messages = {"items": initial_messages_list, "images": initial_messages[
                    "images"], "videos": initial_messages["videos"]}
            except Exception:
                initial_messages = {"items": initial_messages_list}
            response["initial_message"] = initial_messages

            response["failure_recommendations"] = get_message_list_using_pk(json.loads(
                botchannel.failure_recommendations)["items"])
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditWhatsAppChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class EditFacebookChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data["bot_id"]
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_deleted=False)

            channel = Channel.objects.get(name="Facebook")
            botchannel = BotChannel.objects.get(bot=bot_obj, channel=channel)
            response["welcome_message"] = botchannel.welcome_message
            response["failure_message"] = botchannel.failure_message
            response["authentication_message"] = botchannel.authentication_message
            initial_messages = json.loads(botchannel.initial_messages)
            initial_messages_list = get_message_list_using_pk(
                initial_messages["items"])
            try:
                initial_messages = {"items": initial_messages_list, "images": initial_messages[
                    "images"], "videos": initial_messages["videos"]}
            except Exception:
                initial_messages = {"items": initial_messages_list}
            response["initial_message"] = initial_messages

            response["failure_recommendations"] = get_message_list_using_pk(json.loads(
                botchannel.failure_recommendations)["items"])
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditFacebookChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


"""
API Tested: GetChannelDetailsAPI
input queries:
    bot_id: pk of current bot
    bot_name: "uat" or may be othername
    user_id:
    session_id:
    channel_name: name of channel by which bot is getting the equest.
expected output:
    status: 200 // SUCCESS
Return:
    return the basic details of bot...like welcome message, banners etc.
"""


class GetChannelDetailsAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)
            channel_name = data["channel_name"]
            bot_id = data["bot_id"]
            bot_name = data["bot_name"]
            user_id = data["user_id"]
            session_id = data["session_id"]
            selected_language = "en"
            if "selected_language" in data:
                selected_language = data["selected_language"]

            session_id = check_and_return_easychat_session_if_expired(
                session_id)

            is_user_session_retained = False

            if user_id != "" and session_id != "":
                is_user_session_retained = True

            channel_obj = Channel.objects.get(name=str(channel_name))

            config_obj = get_developer_console_settings()

            bot_obj = None

            if(bot_name == 'uat'):
                bot_obj = Bot.objects.get(
                    pk=bot_id, is_uat=True, is_deleted=False)
            else:
                bot_obj = Bot.objects.filter(
                    slug=bot_name, is_active=True, is_deleted=False).order_by('-pk')[0]

            language_obj = Language.objects.filter(
                lang=selected_language).first()

            reseting_user_details(user_id, bot_obj)

            show_livechat_form_or_no = bot_obj.show_livechat_form_or_no

            response["show_livechat_form_or_no"] = show_livechat_form_or_no

            # TimeSpentByUser.objects.create(
            #     user_id=user_id, session_id=session_id, start_datetime=start_datetime, end_datetime=start_datetime, bot=bot_obj, web_page=bot_web_page, web_page_source=web_page_source)

            channel_obj = BotChannel.objects.filter(
                bot=bot_obj, channel=channel_obj)[0]

            bot_info_obj = BotInfo.objects.get(bot=bot_obj)

            regex_compiler = re.compile(r'<.*?>')

            response["speech_message"] = regex_compiler.sub(
                "", channel_obj.speech_message)

            if str(channel_name) in ["Web", "Android", "iOS"]:
                welcome_message = channel_obj.welcome_message

                welcome_message = str(BeautifulSoup(
                    welcome_message, 'html.parser'))
                response["welcome_message"] = welcome_message
                # response["speech_welcome_message"] = BeautifulSoup(
                #     channel_obj.welcome_message).text
                response["speech_welcome_message"] = process_speech_response_query(
                    welcome_message)
            else:
                response["welcome_message"] = regex_compiler.sub(
                    "", channel_obj.welcome_message)
            response["failure_message"] = regex_compiler.sub(
                "", channel_obj.failure_message)
            response["reprompt_message"] = regex_compiler.sub(
                "", channel_obj.reprompt_message)

            response["session_end_message"] = regex_compiler.sub(
                "", channel_obj.session_end_message)

            initial_messages = json.loads(channel_obj.initial_messages)
            try:
                new_tag_list = initial_messages["new_tag_list"]
            except:
                new_tag_list = []

            lower_channel_name = channel_obj.channel.name.strip().lower().replace(" ", "_")
            intent_icon_channel_choices_info = bot_info_obj.get_intent_icon_channel_choices_info()

            enable_intent_icon = False
            if bot_info_obj.enable_intent_icon and (lower_channel_name in intent_icon_channel_choices_info) and ("1" in intent_icon_channel_choices_info[lower_channel_name]):
                enable_intent_icon = True

            initial_messages_list = get_message_list_with_pk(
                initial_messages["items"], new_tag_list, enable_intent_icon, channel_obj=channel_obj.channel)
            try:
                initial_messages = {"items": initial_messages_list, "images": initial_messages[
                    "images"], "compressed_images": initial_messages["compressed_images"], "videos": initial_messages["videos"]}
            except Exception:
                initial_messages = {"items": initial_messages_list}
            response["initial_messages"] = initial_messages

            welcome_banner_objs = WelcomeBanner.objects.filter(
                bot_channel=channel_obj).order_by("serial_number")
            welcome_banner_list = []
            for welcome_banner_obj in welcome_banner_objs:
                intent_name = str(welcome_banner_obj.get_intent_name()).strip()
                if selected_language != 'en':
                    intent_name = process_welcome_banner_list_based_on_language(
                        intent_name, welcome_banner_obj.intent, language_obj, selected_language, EasyChatTranslationCache, LanguageTuningIntentTable)
                welcome_banner_list.append({
                    "action_type": welcome_banner_obj.action_type,
                    "image_url": welcome_banner_obj.image_url,
                    "redirection_url": welcome_banner_obj.redirection_url,
                    "intent_name": intent_name.strip().replace(" ", "_"),
                    "intent_pk": welcome_banner_obj.get_intent_pk(),
                    "welcome_banner_id": welcome_banner_obj.pk
                })

            response["welcome_banner_list"] = welcome_banner_list
            response[
                "is_text_to_speech_required"] = bot_obj.is_text_to_speech_required
            response["is_powered_by_required"] = bot_obj.is_powered_by_required

            response[
                "bot_inactivity_detection_enabled"] = bot_obj.is_inactivity_timer_enabled
            response["bot_inactivity_msg"] = bot_obj.bot_inactivity_response
            response["bot_inactivity_time"] = bot_obj.bot_inactivity_timer

            response[
                "bot_response_delay_allowed"] = bot_obj.bot_response_delay_allowed
            response["bot_response_delay_timer"] = bot_obj.bot_response_delay_timer
            response[
                "bot_response_delay_message"] = bot_obj.bot_response_delay_message

            response['bot_start_conversation_intent'] = None
            if bot_obj.start_conversation != None and bot_obj.start_conversation != "":
                response[
                    "bot_start_conversation_intent"] = bot_obj.start_conversation

            sticky_intents = json.loads(channel_obj.sticky_intent)
            sticky_intent_list = get_message_list_with_pk(
                sticky_intents["items"], channel_obj=channel_obj.channel)
            sticky_intents_menu = json.loads(channel_obj.sticky_intent_menu)
            hamburger_items = json.loads(channel_obj.hamburger_items)
            hamburger_items = hamburger_items["items"]
            quick_items = json.loads(channel_obj.quick_items)
            quick_items = quick_items["items"]
            sticky_intent_list_menu = get_message_list_and_icon_name(
                sticky_intents_menu["items"], Intent)
            bot_theme_obj = bot_obj.default_theme
            try:
                bot_theme = bot_theme_obj.name
            except Exception:
                bot_theme = ""

            if str(channel_name) in ["Web", "Android", "iOS"]:
                try:
                    response[
                        "is_automatic_carousel_enabled"] = channel_obj.is_automatic_carousel_enabled
                    response["carousel_time"] = channel_obj.carousel_time
                except Exception:
                    response["is_automatic_carousel_enabled"] = False

                response[
                    "is_bot_notification_sound_enabled"] = channel_obj.is_bot_notification_sound_enabled

                response["phonetic_typing_supported_langugage_list"] = get_list_of_phonetic_typing_suported_languages(
                    LANGUGES_SUPPORTING_PHONETIC_TYPING)
                response["phonetic_typing_disclaimer_text_dict"] = get_language_based_disclaimer_text_dict(
                    channel_obj, LANGUGES_SUPPORTING_PHONETIC_TYPING, EasyChatTranslationCache, RequiredBotTemplate)
            try:
                livechat_obj = LiveChatConfig.objects.get(bot=bot_obj)
                response['queue_timer'] = livechat_obj.queue_timer
            except Exception:
                response['queue_timer'] = 30
                pass
            response["bot_theme"] = bot_theme
            response["sticky_intents_list"] = sticky_intent_list
            response["sticky_intents_list_menu"] = sticky_intent_list_menu
            response["hamburger_items"] = hamburger_items
            response["quick_items"] = quick_items
            response[
                "sticky_button_display_format"] = channel_obj.sticky_button_display_format
            response["session_id"] = session_id
            response["status"] = 200
            response["query_token_id"] = generate_query_token()

            response[
                "web_url_initial_intent_present"] = bot_obj.web_url_initial_intent_present
            response[
                "web_url_is_welcome_message_present"] = bot_obj.web_url_is_welcome_message_present
            response[
                "web_url_initial_image_present"] = bot_obj.web_url_initial_image_present
            response[
                "web_url_initial_videos_present"] = bot_obj.web_url_initial_videos_present
            response[
                "web_url_is_welcome_banner_present"] = bot_obj.web_url_is_welcome_banner_present
            # initial intent trigger
            response["initial_intent"] = None

            bot_info_obj = get_bot_info_object(bot_obj)

            if bot_obj.initial_intent is not None and (not (bot_info_obj.is_bot_chat_history_to_be_shown_on_refresh and is_user_session_retained)):
                response["initial_intent"] = bot_obj.initial_intent.pk

            default_order_of_response = json.loads(
                bot_obj.default_order_of_response)
            default_order_of_response_list = []
            for elements in default_order_of_response:
                default_order_of_response_list.append(elements)
            csat_object = CSATFeedBackDetails.objects.filter(bot_obj=bot_obj)

            if csat_object:
                csat_object = csat_object[0]
                response[
                    'mark_all_fields_mandatory'] = csat_object.mark_all_fields_mandatory
                response['collect_email_id'] = csat_object.collect_email_id
                response['collect_phone_number'] = csat_object.collect_phone_number
                response['all_feedbacks'] = csat_object.all_feedbacks
            else:
                response['mark_all_fields_mandatory'] = False
                response['collect_email_id'] = False
                response['collect_phone_number'] = False
                response['all_feedbacks'] = ""
            response["user_id"] = user_id
            response['default_order_of_response'] = default_order_of_response_list
            response['max_file_size_allowed'] = bot_obj.max_file_size_allowed
            response[
                'csat_feedback_form_enabled'] = bot_obj.csat_feedback_form_enabled
            response['mask_confidential_info'] = bot_obj. mask_confidential_info
            response[
                'is_audio_notification_enabled'] = bot_obj.enable_audio_notification

            response["words_list"] = []
            response['spell_check_api_endpoint'] = ""
            response['spell_check_id'] = ""

            response["is_intent_icon_enabled_for_dnd"] = False
            if (lower_channel_name in intent_icon_channel_choices_info and "6" in intent_icon_channel_choices_info[lower_channel_name]):
                response["is_intent_icon_enabled_for_dnd"] = True
            
            response["is_spell_check_while_typing_enabled"] = bot_info_obj.enable_spell_check_while_typing
            if bot_obj.default_theme.name == 'theme_4':
                response["faq_intents"] = get_faq_intents(bot_obj, language_obj, selected_language)
            
            if bot_info_obj.enable_spell_check_while_typing:
                word_dict_obj = WordDictionary.objects.filter(
                    bot=bot_obj).first()

                if not word_dict_obj:
                    word_dict_obj = WordDictionary.objects.create(bot=bot_obj)
                    word_dict_obj.save()

                response["words_list"] = json.loads(
                    word_dict_obj.word_dict)["items"]
                response['spell_check_api_endpoint'] = config_obj.spell_check_api_endpoint
                response['spell_check_id'] = get_hash_value(bot_id, settings.EASYCHAT_DOMAIN)

            if selected_language != "en":
                create_language_tuned_object = False
                response = process_channel_details_based_on_language(
                    response, selected_language, channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache, bot_info_obj)

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error GetChannelDetailsAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


def RenderGAAuthPage(request, bot_id):  # noqa: N802

    try:
        selected_bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
        channel = Channel.objects.filter(name="GoogleHome").first()
        google_project_obj = GoogleAlexaProjectDetails.objects.get(
            bot=selected_bot_obj, channel=channel)

        return render(request, "EasyChatApp/channels/ga_auth.html", {"google_project_obj": google_project_obj})

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error RenderGAAuthPage %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return HttpResponseRedirect("/chat/login")


def RenderAlexaAuthPage(request, bot_id):  # noqa: N802

    try:
        selected_bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
        channel = Channel.objects.filter(name="Alexa").first()
        google_project_obj = GoogleAlexaProjectDetails.objects.get(
            bot=selected_bot_obj, channel=channel)

        return render(request, "EasyChatApp/channels/ga_auth.html", {"google_project_obj": google_project_obj})

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error RenderGAAuthPage %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return HttpResponseRedirect("/chat/login")


# @csrf_exempt
# def VerificationOfDetails(request):  # noqa: N802
#     if request.method == "POST":
#         try:
#             json_data = {
#                 "status_code": 500
#             }
#             logger.info(request.POST, extra={'AppName': 'EasyChat', 'user_id': str(
#                 request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#             data = request.POST
#             mobilenumber = data["mobilenumber"]
#             dob = data["dob"]
#             r = requests.get(url="https://clg.icicibank.com/hc_bot_api/HCTOBOTV1.0/applicant/authenticatecandidate?MobileNumber=" +
#                              str(mobilenumber) + "&DOB=" + str(dob))
#
#             data = json.loads(r.text)
#             if data["Code"] == "SUCCESS0000":
#                 # OTP = sendOTP(str(mobilenumber))
#                 user = None
#                 try:
#                     user = CustomUser.objects.get(username=str(mobilenumber))
#                 except Exception:  # noqa: F841
#                     user = CustomUser.objects.create(username=str(mobilenumber), password=make_password(
#                         str(uuid.uuid4())), is_staff=True, is_superuser=False)
#
#                 user_params = {}
#                 user_params["MobileNumber"] = str(mobilenumber)
#                 user_params["DOB"] = str(dob)
#                 user.user_params = json.dumps(user_params)
#                 user.save()
#                 logger.info("User saved successfully.", extra={'AppName': 'EasyChat', 'user_id': str(
#                     request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#
#                 user_authenticated = authenticate(user=user)
#                 logger.info("User authenticated " + str(user_authenticated), extra={'AppName': 'EasyChat', 'user_id': str(
#                     request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#                 login(request, user)
#                 logger.info("User loged in " + str(user), extra={'AppName': 'EasyChat', 'user_id': str(
#                     request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#                 json_data["status_code"] = 200
#             else:
#                 json_data["status_code"] = 300
#             return HttpResponse(json.dumps(json_data), content_type="application/json")
#         except Exception as e:  # noqa: F841
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error("VerificationOfDetails ! %s %s",
#                          str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
#             return HttpResponse(json.dumps(json_data), content_type="application/json")
#     else:
#         return render(request, 'EasyChatApp/error_500.html')

class EditWebLandingAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data["bot_id"]
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_deleted=False)
            intent_name = data["intent_value"]
            new_web_url = data["web_url"]
            web_url_id = data["id"]

            show_prompt_message_after_timer = data[
                "show_prompt_message_after_timer"]
            prompt_message = data["prompt_message"]
            prompt_message_timer = data["prompt_message_timer"]

            web_url_landing_data = json.loads(bot_obj.web_url_landing_data)

            status = False

            # dictionary is made
            # to check whether the same exact dictionary
            # already exists in bot_obj.web_url_landing_data
            dict_check_web_landing_list = {}
            dict_check_web_landing_list["id"] = str(web_url_id)
            dict_check_web_landing_list["url"] = str(new_web_url)
            dict_check_web_landing_list["intent_name"] = str(intent_name)
            dict_check_web_landing_list["show_prompt_message_after_timer"] = str(
                show_prompt_message_after_timer).lower()
            dict_check_web_landing_list["prompt_message"] = str(prompt_message)
            dict_check_web_landing_list[
                "prompt_message_timer"] = str(prompt_message_timer)

            if dict_check_web_landing_list in web_url_landing_data:
                status = True

            if status:
                response["status"] = 301
            elif status == False:
                bot_channel = BotChannel.objects.filter(
                    bot=bot_obj, channel=Channel.objects.filter(name="Web").first()).first()
                is_prompt_message_updated = "false"
                list_of_updated_ids = []
                for url_index in range(0, len(web_url_landing_data)):
                    if web_url_landing_data[url_index]["id"] == web_url_id:
                        web_url_landing_data[url_index]["url"] = new_web_url
                        web_url_landing_data[url_index][
                            "intent_name"] = intent_name
                        trigger_intent_obj = Intent.objects.filter(name=intent_name, is_deleted=False).first()
                        trigger_intent_pk = ""
                        if trigger_intent_obj:
                            trigger_intent_pk = trigger_intent_obj.pk
                        web_url_landing_data[url_index]["trigger_intent_pk"] = str(trigger_intent_pk)
                        web_url_landing_data[url_index]["show_prompt_message_after_timer"] = str(
                            show_prompt_message_after_timer).lower()
                        old_prompt_msg = web_url_landing_data[
                            url_index]["prompt_message"]

                        web_url_landing_data[url_index]["prompt_message"] = ""
                        web_url_landing_data[url_index][
                            "prompt_message_timer"] = ""
                        if(web_url_landing_data[url_index]["show_prompt_message_after_timer"] == "true"):
                            if old_prompt_msg != prompt_message:
                                is_prompt_message_updated = "true"
                                list_of_updated_ids.append(web_url_id)
                            web_url_landing_data[url_index][
                                "prompt_message"] = prompt_message
                            web_url_landing_data[url_index][
                                "prompt_message_timer"] = prompt_message_timer
                        bot_obj.web_url_landing_data = json.dumps(
                            web_url_landing_data)
                        bot_obj.save()
                list_of_updated_ids = json.dumps(list_of_updated_ids)
                activity_update = json.loads(bot_channel.activity_update)
                activity_update[
                    "is_web_prompt_message_updated"] = is_prompt_message_updated
                activity_update["list_of_updated_ids"] = list_of_updated_ids
                bot_channel.activity_update = json.dumps(activity_update)
                bot_channel.save()
                response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditWebLandingAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class EditWebLandingForNonPrimaryLanguageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            bot_pk = data["bot_id"]
            selected_language = validation_obj.remo_html_from_string(
                data["selected_language"])
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_deleted=False)
            lang_obj = Language.objects.get(lang=selected_language)
            lang_tuned_bot_obj = LanguageTunedBot.objects.filter(
                language=lang_obj, bot=bot_obj)[0]
            web_url_id = validation_obj.remo_html_from_string(data["id"])
            prompt_message = validation_obj.remo_html_from_string(
                data["prompt_message"])

            web_url_landing_data = json.loads(
                lang_tuned_bot_obj.web_url_landing_data)

            for url_index in range(0, len(web_url_landing_data)):
                if web_url_landing_data[url_index]["id"] == web_url_id:
                    web_url_landing_data[url_index][
                        "prompt_message"] = prompt_message
                    lang_tuned_bot_obj.web_url_landing_data = json.dumps(
                        web_url_landing_data)
                    lang_tuned_bot_obj.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditWebLandingForNonPrimaryLanguageAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DeleteWebLandingAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data["bot_id"]
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_deleted=False)
            web_url_id = data["id"]
            web_url_landing_data = json.loads(bot_obj.web_url_landing_data)

            update_web_url_landing = []
            for url_index in range(0, len(web_url_landing_data)):
                web_url_landing_data[url_index]
                if web_url_landing_data[url_index]["id"] != web_url_id:
                    update_web_url_landing.append(
                        web_url_landing_data[url_index])

            bot_obj.web_url_landing_data = json.dumps(update_web_url_landing)
            bot_obj.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteWebLandingAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveCustomIntentsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)
            validation_obj = EasyChatInputValidation()
            bot_pk = data["bot_id"]
            bot_obj = Bot.objects.filter(
                pk=int(bot_pk), is_deleted=False).first()

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['status_message'] = 'You are not authorised to perform this operation.'
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            custom_intent_url = data["custom_intent_url"]
            custom_intent_url = validation_obj.remo_html_from_string(
                custom_intent_url)
            custom_intent_list = data["custom_intent_list"]
            custom_intents_for = data["custom_intents_for"]
            custom_intents_for = validation_obj.remo_html_from_string(
                custom_intents_for)

            if custom_intents_for in CUSTOM_INTENTS_FOR_DICT:
                custom_intents_for = CUSTOM_INTENTS_FOR_DICT[custom_intents_for]
            else:
                response["status"] = 208
                response['status_message'] = "Custom intents are not available"
                return Response(data=response)

            custom_intent_obj_data = CustomIntentBubblesForWebpages.objects.filter(
                bot=bot_obj, web_page=custom_intent_url, custom_intents_for=custom_intents_for)
            if custom_intent_obj_data.exists():
                response["status"] = 301
            else:
                custom_bubble_obj = CustomIntentBubblesForWebpages.objects.create(
                    bot=bot_obj, web_page=custom_intent_url, custom_intents_for=custom_intents_for)
                custom_intent_bubble = Intent.objects.filter(
                    pk__in=custom_intent_list)
                custom_bubble_obj.custom_intent_bubble.add(
                    *custom_intent_bubble)
                intent_string = ""
                for intent_name in custom_intent_bubble.all():
                    intent_string += intent_name.name + ","

                response["custom_intent_list"] = intent_string[:-1]
                response["custom_intents_pk"] = str(custom_bubble_obj.pk)
                response["webpage"] = custom_bubble_obj.web_page
                custom_bubble_obj.save()
                response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveCustomIntentsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class EditCustomIntentsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)
            bot_pk = data["bot_id"]
            bot_obj = Bot.objects.filter(
                pk=int(bot_pk), is_deleted=False).first()

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['status_message'] = 'You are not authorised to perform this operation.'
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            custom_intent_list = data["custom_intent_list"]
            custom_intents_bubble_pk = int(data["custom_intents_pk"])
            custom_intent_obj_data = CustomIntentBubblesForWebpages.objects.filter(
                bot=bot_obj, pk=custom_intents_bubble_pk).first()

            if custom_intent_obj_data:
                custom_intent_bubble = Intent.objects.filter(
                    pk__in=custom_intent_list)
                custom_intent_obj_data.custom_intent_bubble.clear()
                custom_intent_obj_data.custom_intent_bubble.add(
                    *custom_intent_bubble)
                intent_string = ""
                for intent_name in custom_intent_bubble.all():
                    intent_string += intent_name.name + ","

                response["custom_intent_list"] = intent_string[:-1]
                response["custom_intents_pk"] = str(custom_intent_obj_data.pk)
                custom_intent_obj_data.save()
                response["status"] = 200
            else:
                response["status"] = 301

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditCustomIntentsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DeleteCustomIntentsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data["bot_id"]
            bot_obj = Bot.objects.filter(
                pk=int(bot_pk), is_deleted=False).first()

            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['status_message'] = 'You are not authorised to perform this operation.'
                response = json.dumps(response)
                encrypted_response = custom_encrypt_obj.encrypt(response)
                response = {"Response": encrypted_response}
                return Response(data=response)

            custom_intents_bubble_pk = int(data["custom_intents_pk"])
            custom_intent_obj_data = CustomIntentBubblesForWebpages.objects.filter(
                bot=bot_obj, pk=custom_intents_bubble_pk).first()

            if custom_intent_obj_data:
                custom_intent_obj_data.delete()
                response["status"] = 200
            else:
                response["status"] = 301

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteCustomIntentsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveWebLandingAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data["bot_id"]
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_deleted=False)
            web_landing_url = data["web_landing_url"]
            web_initial_intent = data["web_initial_intent"]
            show_prompt_message_after_timer = data[
                "show_prompt_message_after_timer"]
            prompt_message = data["prompt_message"]

            prompt_message_timer = data["prompt_message_timer"]

            web_url_landing_data = json.loads(bot_obj.web_url_landing_data)

            intent_name = Intent.objects.get(pk=int(web_initial_intent))

            url_id = str(uuid.uuid4())

            status = False
            for url_data in web_url_landing_data:
                if url_data["url"] == web_landing_url:
                    status = True
            if status == False:
                web_landing_dict = {
                    "id": url_id, "url": web_landing_url, "intent_name": intent_name.name, "trigger_intent_pk": web_initial_intent, "show_prompt_message_after_timer": str(show_prompt_message_after_timer).lower(), "prompt_message": prompt_message, "prompt_message_timer": prompt_message_timer}
                web_url_landing_data.append(web_landing_dict)
                bot_obj.web_url_landing_data = json.dumps(web_url_landing_data)
                bot_obj.save()
                response["status"] = 200
                response["id"] = url_id
                response["intent_name"] = str(intent_name.name)
            else:
                response["status"] = 301
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveWebLandingAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


def MSTeamsChannel(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            # bot_pk_list = list(Bot.objects.filter(users__in=[user_obj]).values_list("pk", flat=True))
            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = request.GET.get("selected_lang", "en")
                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)
                
                channel_obj = Channel.objects.get(name="Microsoft")
                bot_channel_obj = BotChannel.objects.get(
                    bot=selected_bot_obj, channel=channel_obj)
                initial_messages_pk_list = json.loads(bot_channel_obj.initial_messages)["items"]
                failure_messages_pk_list = json.loads(bot_channel_obj.failure_recommendations)["items"]
                ms_team_app_code = bot_channel_obj.ms_team_app_code
                ms_team_app_password = bot_channel_obj.ms_team_app_password

                intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj], channels=channel_obj,
                                                    is_deleted=False,
                                                    is_form_assist_enabled=False,
                                                    is_hidden=False)

                intent_name_list = []
                intent_name_list_failure = []
                for intent_obj_pk in initial_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                for intent_obj_pk in failure_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in initial_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in failure_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                master_languages = selected_bot_obj.languages_supported.all()
                language_tuned_object = bot_channel_obj
                activity_update = json.loads(bot_channel_obj.activity_update)
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(
                    bot_channel_obj, activity_update, selected_language, LanguageTunedBotChannel)

                if selected_language != "en":
                    response = {}
                    response["welcome_message"] = bot_channel_obj.welcome_message
                    response["failure_message"] = bot_channel_obj.failure_message
                    response[
                        "authentication_message"] = bot_channel_obj.authentication_message
                    create_language_tuned_object = True
                    check_and_create_channel_details_language_tuning_objects(
                        response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                    lang_obj = Language.objects.get(lang=selected_language)
                    language_tuned_object = LanguageTunedBotChannel.objects.filter(
                        language=lang_obj, bot_channel=bot_channel_obj)[0]

                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages
                # are selected  after first five
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3

                return render(request, 'EasyChatApp/channels/microsoft_channels.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "ms_team_app_code": ms_team_app_code,
                    "ms_team_app_password": ms_team_app_password,
                    "bot_channel_obj": bot_channel_obj,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                })
            else:
                # return HttpResponseNotFound(INVALID_REQUEST)
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("MSTeamsChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET['id'])})
        # return HttpResponseNotFound("500")
        return render(request, 'EasyChatApp/error_500.html')


class SaveMSTeamsChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]
            # welcome_message = validation_obj.custom_remo_html_tags(welcome_message)
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            # failure_message = validation_obj.custom_remo_html_tags(failure_message)
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            # authentication_message = validation_obj.custom_remo_html_tags(authentication_message)
            authentication_message = validation_obj.clean_html(
                authentication_message)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot_id = data["bot_id"]
            ms_team_app_password = data["ms_team_app_password"]
            ms_team_app_code = data["ms_team_app_code"]

            images = []
            videos = []
            initial_message_list = []
            failure_recommendation_list = []

            bot = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if user_obj not in bot.users.all():
                return HttpResponseForbidden("You do not have access to this page")
            channel = Channel.objects.get(name="Microsoft")
            channel = BotChannel.objects.get(bot=bot, channel=channel)

            # Language specific
            language_specific_action(
                data, channel, bot, welcome_message, failure_message, authentication_message)

            channel.initial_messages = json.dumps(
                {"items": initial_message_list, "images": images, "videos": videos})
            channel.failure_recommendations = json.dumps(
                {"items": failure_recommendation_list})
            channel.ms_team_app_password = ms_team_app_password
            channel.ms_team_app_code = ms_team_app_code
            channel.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveMSTeamsChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveWebLandingInitialMessagesAPI(APIView):

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

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data["bot_id"]
            initial_intent_present = data["initial_intent_present"]
            is_welcome_message_present = data["is_welcome_message_present"]
            initial_image_present = data["initial_image_present"]
            initial_videos_present = data["initial_videos_present"]
            is_welcome_banner_present = data["is_welcome_banner_present"]

            bot_obj = Bot.objects.get(pk=int(bot_pk))

            bot_obj.web_url_initial_intent_present = initial_intent_present
            bot_obj.web_url_is_welcome_message_present = is_welcome_message_present
            bot_obj.web_url_initial_image_present = initial_image_present
            bot_obj.web_url_initial_videos_present = initial_videos_present
            bot_obj.web_url_is_welcome_banner_present = is_welcome_banner_present
            bot_obj.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveWebLandingInitialMessagesAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveMSTeamsChannelDetails = SaveMSTeamsChannelDetailsAPI.as_view()

SaveCustomIntents = SaveCustomIntentsAPI.as_view()

EditCustomIntents = EditCustomIntentsAPI.as_view()

DeleteCustomIntents = DeleteCustomIntentsAPI.as_view()

SaveWebLanding = SaveWebLandingAPI.as_view()

DeleteWebLanding = DeleteWebLandingAPI.as_view()

EditWebLanding = EditWebLandingAPI.as_view()

EditWebLandingForNonPrimaryLanguage = EditWebLandingForNonPrimaryLanguageAPI.as_view()

SaveWebChannelDetails = SaveWebChannelDetailsAPI.as_view()

SaveChannelLanguageTunedObjects = SaveChannelLanguageTunedObjectsAPI.as_view()

SaveGoogleHomeChannelDetails = SaveGoogleHomeChannelDetailsAPI.as_view()

SaveAlexaChannelDetails = SaveAlexaChannelDetailsAPI.as_view()

SaveAndroidChannelDetails = SaveAndroidChannelDetailsAPI.as_view()

SaveWhatsAppChannelDetails = SaveWhatsAppChannelDetailsAPI.as_view()

SaveFacebookChannelDetails = SaveFacebookChannelDetailsAPI.as_view()

SaveInstagramChannelDetails = SaveInstagramChannelDetailsAPI.as_view()

# SaveAndroidChannelDetails = SaveAndroidChannelDetailsAPI.as_view()

EditWebChannelDetails = EditWebChannelDetailsAPI.as_view()

EditGoogleChannelDetails = EditGoogleChannelDetailsAPI.as_view()

EditAlexaChannelDetails = EditAlexaChannelDetailsAPI.as_view()

EditAndroidChannelDetails = EditAndroidChannelDetailsAPI.as_view()

EditWhatsAppChannelDetails = EditWhatsAppChannelDetailsAPI.as_view()

EditFacebookChannelDetails = EditFacebookChannelDetailsAPI.as_view()

# EditAndroidChannelDetails = EditAndroidChannelDetailsAPI.as_view()
GetChannelDetails = GetChannelDetailsAPI.as_view()

SaveWebLandingInitialMessages = SaveWebLandingInitialMessagesAPI.as_view()


##################  Telegram Channel ###################


class EditTelegramChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data["bot_id"]
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_deleted=False)

            channel = Channel.objects.get(name="Telegram")
            botchannel = BotChannel.objects.get(bot=bot_obj, channel=channel)
            initial_messages = json.loads(botchannel.initial_messages)
            initial_messages_list = get_message_list_using_pk(
                initial_messages["items"])
            try:
                initial_messages = {"items": initial_messages_list, "images": initial_messages[
                    "images"], "videos": initial_messages["videos"]}
            except Exception:
                initial_messages = {"items": initial_messages_list}
            response["initial_message"] = initial_messages

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditTelegramChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EditTelegramChannelDetails = EditTelegramChannelDetailsAPI.as_view()


class SaveTelegramChannelDetailsAPI(APIView):

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

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]
            # welcome_message = validation_obj.custom_remo_html_tags(welcome_message)
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            # failure_message = validation_obj.custom_remo_html_tags(failure_message)
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            # authentication_message = validation_obj.custom_remo_html_tags(authentication_message)
            authentication_message = validation_obj.clean_html(
                authentication_message)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            initial_message_list = data["initial_message_list"]
            failure_recommendation_list = data["failure_recommendation_list"]
            image_url = data["image_url"]
            video_url = data["video_url"]
            bot_id = data["bot_id"]

            images = []
            if image_url != "":
                images = [image_url]

            videos = []
            if video_url != "":
                videos = [video_url]

            initial_message_list = [
                str(message) for message in initial_message_list if message != ""]

            bot = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            channel = Channel.objects.get(name="Telegram")
            channel = BotChannel.objects.get(bot=bot, channel=channel)

            # Language specific
            language_specific_action(
                data, channel, bot, welcome_message, failure_message, authentication_message)

            channel.initial_messages = json.dumps(
                {"items": initial_message_list, "images": images, "videos": videos})
            channel.failure_recommendations = json.dumps(
                {"items": failure_recommendation_list})
            channel.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveTelegramChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveTelegramChannelDetails = SaveTelegramChannelDetailsAPI.as_view()


class TelegramWebhookSetupAPI(APIView):
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
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            telegram_api_token = data["telegram_api_token"]
            telegram_api_token = validation_obj.remo_html_from_string(
                telegram_api_token)
            telegram_api_token = "bot" + str(telegram_api_token)
            bot_id = data["bot_id"]

            bot = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            telegram_obj = TelegramDetails.objects.filter(bot=bot)[0]
            telegram_webhook_url = settings.EASYCHAT_HOST_URL + \
                "/chat/webhook/telegram/?id=" + str(bot_id)
            if set_telegram_webhook(telegram_webhook_url, telegram_obj.telegram_url, telegram_api_token):
                telegram_obj.telegram_api_token = telegram_api_token
                telegram_obj.is_active = True
                telegram_obj.save()
                response["status"] = 200
                response["telegram_api_token"] = "XXXXXXXXXXXXXXXXXXXXXXXX" + \
                    str(telegram_api_token[-4:])
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("TelegramWebhookSetupAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


TelegramWebhookSetup = TelegramWebhookSetupAPI.as_view()


class EditGoogleBusinessMessagesDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data["bot_id"]
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_deleted=False)

            channel = Channel.objects.get(name="GoogleBusinessMessages")
            botchannel = BotChannel.objects.get(bot=bot_obj, channel=channel)
            initial_messages = json.loads(botchannel.initial_messages)
            initial_messages_list = get_message_list_using_pk(
                initial_messages["items"])
            if "images" in initial_messages and "videos" in initial_messages:
                initial_messages = {"items": initial_messages_list, "images": initial_messages[
                    "images"], "videos": initial_messages["videos"]}
            else:
                initial_messages = {"items": initial_messages_list}
            response["initial_message"] = initial_messages
            response["failure_recommendations"] = {"items": []}
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditGoogleBusinessMessagesChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EditGoogleBusinessMessagesDetails = EditGoogleBusinessMessagesDetailsAPI.as_view()


class SaveGoogleBusinessMessagesDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]
            # welcome_message = validation_obj.custom_remo_html_tags(welcome_message)
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            # failure_message = validation_obj.custom_remo_html_tags(failure_message)
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            # authentication_message = validation_obj.custom_remo_html_tags(authentication_message)
            authentication_message = validation_obj.clean_html(
                authentication_message)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            initial_message_list = data["initial_message_list"]
            failure_recommendation_list = data["failure_recommendation_list"]

            bot_id = data["bot_id"]

            client_access_token = data["client_access_token"]
            client_access_token = validation_obj.remo_html_from_string(
                client_access_token)

            gmb_agent_id = data["gmb_agent_id"]
            gmb_agent_id = validation_obj.remo_html_from_string(gmb_agent_id)
            gmb_brand_id = data["gmb_brand_id"]
            gmb_brand_id = validation_obj.remo_html_from_string(gmb_brand_id)
            privacy_policy_url = data["gmb_privacy_policy_url"]
            gmb_bot_display_image_url = data["gmb_display_image_url"]
            gmb_bot_display_name = data["gmb_display_name"]
            gmb_bot_display_name = validation_obj.remo_html_from_string(
                gmb_bot_display_name)

            initial_message_list = [
                str(message) for message in initial_message_list if message != ""]
            initial_questions = []
            for intent_obj_pk in initial_message_list:
                intent_objs = Intent.objects.filter(
                    pk=int(intent_obj_pk), is_hidden=False, is_deleted=False)
                if intent_objs:
                    intent_obj = intent_objs[0]
                    initial_questions.append(intent_obj.name)

            bot = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if user_obj not in bot.users.all():
                return HttpResponseForbidden("You do not have access to this page")
            gmb_obj = GMBDetails.objects.filter(bot=bot)[0]

            service_account_location = gmb_obj.gmb_credentials_file_path

            if update_welcome_msg_for_gbm_agent(welcome_message, initial_questions, gmb_agent_id, gmb_brand_id, privacy_policy_url, service_account_location):
                gmb_obj.gmb_agent_id = gmb_agent_id
                gmb_obj.gmb_brand_id = gmb_brand_id
                gmb_obj.gmb_privacy_policy_url = privacy_policy_url
                gmb_obj.bot_display_name = gmb_bot_display_name
                gmb_obj.bot_display_image_url = gmb_bot_display_image_url
                gmb_obj.is_active = True
                gmb_obj.save()
                response["gmb_agent_id"] = gmb_agent_id
                response["gmb_brand_id"] = gmb_brand_id
            else:
                response["status"] = 400
                response["message"] = "Invalid GBM Credentials."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            bot = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            channel = Channel.objects.get(name="GoogleBusinessMessages")
            channel = BotChannel.objects.get(bot=bot, channel=channel)

            # Language specific
            language_specific_action(
                data, channel, bot, welcome_message, failure_message, authentication_message)

            channel.page_access_token = client_access_token
            channel.initial_messages = json.dumps(
                {"items": initial_message_list, })
            channel.failure_recommendations = json.dumps(
                {"items": failure_recommendation_list})
            channel.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveGoogleBusinessMessagesChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveGoogleBusinessMessagesChannelDetails = SaveGoogleBusinessMessagesDetailsAPI.as_view()


class UploadGMBCredentialFileAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            uploaded_file = request.FILES.getlist('file')[0]

            bot_id = request.data['bot_id']

            uploaded_file_name = uploaded_file.name

            uploaded_file_name = get_dot_replaced_file_name(uploaded_file_name)

            if uploaded_file_name.split('.')[-1] != "json":
                response["status"] = 300

                return Response(data=response)

            try:

                if not os.path.exists('secured_files/EasyChatApp/GmbCredentials'):
                    os.makedirs('secured_files/EasyChatApp/GmbCredentials')

                path = os.path.join(settings.SECURE_MEDIA_ROOT,
                                    "EasyChatApp/GmbCredentials/")

                fs = FileSystemStorage(location=path)
                filename = fs.save(
                    uploaded_file_name, uploaded_file)

                path = "/secured_files/EasyChatApp/GmbCredentials/" + filename

                EasyChatAppFileAccessManagement.objects.create(
                    file_path=path, is_public=False)

                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_id), is_deleted=False, is_uat=True)

                gmb_obj = GMBDetails.objects.filter(bot=selected_bot_obj)

                if gmb_obj.count() == 0:
                    gmb_obj = GMBDetails.objects.create(
                        bot=selected_bot_obj)

                else:
                    gmb_obj = gmb_obj[0]
                path = "secured_files/EasyChatApp/GmbCredentials/" + filename
                gmb_obj.gmb_credentials_file_path = path
                gmb_obj.save()

                filename = path.split("/")[-1]
                response['filename'] = filename

            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error UploadFilesIntoDriveAPI For Loop: %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadFilesIntoDriveAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return Response(data=response)


UploadGMBCredentialFile = UploadGMBCredentialFileAPI.as_view()


class IgnoreChangesInNonPrimaryLanguageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data["bot_id"]
            channel_name = data["channel_name"]
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_deleted=False)

            channel = Channel.objects.filter(name=channel_name)[0]
            botchannel = BotChannel.objects.get(bot=bot_obj, channel=channel)
            activity_update = {
                "is_welcome_message_updated": "false",
                "is_failure_message_updated": "false",
                "is_authentication_message_updated": "false",
                "is_auto_pop_up_text_updated": "false",
                "is_web_prompt_message_updated": "false",
                "list_of_updated_ids": "[]",
                "is_block_spam_data_updated": "false",
                "block_spam_field": ""
            }
            activity_update = json.dumps(activity_update)
            botchannel.activity_update = activity_update
            botchannel.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("IgnoreChangesInNonPrimaryLanguageAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


IgnoreChangesInNonPrimaryLanguage = IgnoreChangesInNonPrimaryLanguageAPI.as_view()


class AutoFixChangesInNonPrimaryLanguageAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data["bot_id"]
            channel_name = data["channel_name"]
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_deleted=False)

            channel = Channel.objects.filter(name=channel_name)[0]
            bot_channel = BotChannel.objects.get(bot=bot_obj, channel=channel)
            channel_activity_update = json.loads(bot_channel.activity_update)
            block_config = BlockConfig.objects.filter(bot=bot_obj).first()
            auto_fix_language_tuned_objects(
                bot_channel, channel_activity_update, LanguageTunedBotChannel, EasyChatTranslationCache, block_config)

            activity_update = {
                "is_welcome_message_updated": "false",
                "is_failure_message_updated": "false",
                "is_authentication_message_updated": "false",
                "is_auto_pop_up_text_updated": "false",
                "is_web_prompt_message_updated": "false",
                "list_of_updated_ids": "[]",
                "is_block_spam_data_updated": "false",
                "block_spam_field": ""
            }
            activity_update = json.dumps(activity_update)
            bot_channel.activity_update = activity_update
            bot_channel.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AutoFixChangesInNonPrimaryLanguageAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AutoFixChangesInNonPrimaryLanguage = AutoFixChangesInNonPrimaryLanguageAPI.as_view()


class GetGoogleAssistantAuthOTPAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            mobile_number = data["mobile_number"]
            mobile_number = validation_obj.remo_html_from_string(
                mobile_number.strip())
            mobile_number = validation_obj.remo_unwanted_characters(
                mobile_number)

            email_id = data["email_id"]
            email_id = validation_obj.remo_html_from_string(email_id.strip())

            custom_fields_list = data["custom_fields_list"]

            project_details_id = data["project_details_id"]

            parameter = {
                "mobile_number": mobile_number,
                "email_id": email_id,
                "custom_fields_list": custom_fields_list,
            }

            project_details_obj = GoogleAlexaProjectDetails.objects.get(
                pk=int(project_details_id))

            code = project_details_obj.get_otp_processor.api_caller
            processor_check_dictionary = {'open': open_file}
            exec(str(code), processor_check_dictionary)

            json_data = processor_check_dictionary['f'](json.dumps(parameter))

            if json_data['status_code'] == '200':
                response["status"] = 200
                response['message'] = 'success'

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetGoogleAssistantAuthOTPAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return Response(data=response)


GetGoogleAssistantAuthOTP = GetGoogleAssistantAuthOTPAPI.as_view()


class VerifyGoogleAssistantAuthOTPAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication,)
    import hashlib

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            mobile_number = data["mobile_number"]
            mobile_number = validation_obj.remo_html_from_string(
                mobile_number.strip())
            mobile_number = validation_obj.remo_unwanted_characters(
                mobile_number)

            email_id = data["email_id"]
            email_id = validation_obj.remo_html_from_string(email_id.strip())

            custom_fields_list = data["custom_fields_list"]

            otp = data["otp"]
            otp = validation_obj.remo_html_from_string(str(otp.strip()))
            otp = validation_obj.remo_unwanted_characters(otp)

            project_details_id = data["project_details_id"]

            if not otp.isnumeric() or len(otp) != 6:
                response['message'] = 'Please enter valid OTP.'
                return Response(data=response)

            parameter = {
                "mobile_number": mobile_number,
                "email_id": email_id,
                "custom_fields_list": custom_fields_list,
                "otp": otp,
            }

            project_details_obj = GoogleAlexaProjectDetails.objects.get(
                pk=int(project_details_id))

            code = project_details_obj.verify_otp_processor.api_caller
            processor_check_dictionary = {'open': open_file}
            exec(str(code), processor_check_dictionary)

            json_data = processor_check_dictionary['f'](json.dumps(parameter))

            if json_data['status_code'] == '200':
                user_params = json.dumps(
                    {"mobile_number": mobile_number, "email_id": email_id, "custom_fields_list": custom_fields_list})

                mobile_number_hash = hashlib.md5(
                    mobile_number.encode()).hexdigest()
                if User.objects.filter(username=mobile_number_hash):
                    user = User.objects.get(username=mobile_number_hash)
                else:
                    CustomUser.objects.create(
                        username=mobile_number_hash, user_params=user_params)
                    user = User.objects.get(username=mobile_number_hash)

                login(request, user,
                      backend='django.contrib.auth.backends.ModelBackend')
                response["status"] = 200

            logger.info(response, extra={'AppName': 'EasyChat', 'user_id': 'None',
                                         'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("VerifyGoogleAssistantAuthOTPAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return Response(data=response)


VerifyGoogleAssistantAuthOTP = VerifyGoogleAssistantAuthOTPAPI.as_view()


class AddGoogleAlexaProjectDetailsAPI(APIView):
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

            project_id = validation_obj.remo_html_from_string(
                data["project_id"]).strip()
            bot_id = data["bot_id"]
            # name = "GoogleHome_" + str(bot_id)
            channel_name = validation_obj.remo_html_from_string(
                data["channel_name"]).strip()
            welcome_image_src = data["attached_file_src"]

            name = channel_name + "_" + str(bot_id)
            redirect_uris = "https://oauth-redirect.googleusercontent.com/r/" + \
                str(project_id)
            if channel_name == "Alexa":
                redirect_uris = "https://layla.amazon.com/api/skill/link/" + \
                    str(project_id)

            client_type = "confidential"
            authorization_grant_type = "authorization-code"
            channel_obj = Channel.objects.filter(name=channel_name).first()
            selected_bot_obj = Bot.objects.get(
                pk=int(bot_id), is_deleted=False)
            if GoogleAlexaProjectDetails.objects.filter(bot=selected_bot_obj, channel=channel_obj).exists():
                google_assistant_details_obj = GoogleAlexaProjectDetails.objects.filter(
                    bot=selected_bot_obj, channel=channel_obj).first()
                google_assistant_details_obj.project_id = project_id
                google_assistant_details_obj.welcome_image_src = welcome_image_src
                google_assistant_details_obj.redirect_uris = redirect_uris
                client_type = google_assistant_details_obj.client_type
                authorization_grant_type = google_assistant_details_obj.authorization_grant_type
                applications_obj = Application.objects.filter(
                    user=request.user, client_id=google_assistant_details_obj.client_id).first()
                if applications_obj:
                    applications_obj.redirect_uris = redirect_uris
                    applications_obj.save()
            else:
                google_assistant_details_obj = GoogleAlexaProjectDetails.objects.create(
                    name=name, bot=selected_bot_obj, project_id=project_id, welcome_image_src=welcome_image_src, channel=channel_obj)
                application_obj = Application.objects.create(
                    name=name, user=request.user, client_type=client_type, authorization_grant_type=authorization_grant_type, redirect_uris=redirect_uris)
                google_assistant_details_obj.client_id = application_obj.client_id
                google_assistant_details_obj.client_secret = application_obj.client_secret
                google_assistant_details_obj.redirect_uris = redirect_uris
                google_assistant_details_obj.client_type = client_type
                google_assistant_details_obj.authorization_grant_type = authorization_grant_type
                create_new_auth_page(
                    google_assistant_details_obj.pk, channel_name)
            google_assistant_details_obj.save()

            client_id = google_assistant_details_obj.client_id
            client_secret = google_assistant_details_obj.client_secret
            response["client_id"] = client_id
            response["client_secret"] = client_secret
            response["project_id"] = project_id
            response["name"] = name
            response["redirect_uris"] = redirect_uris

            response["client_type"] = client_type
            response["authorization_grant_type"] = authorization_grant_type
            response["details_obj_id"] = google_assistant_details_obj.pk
            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AddGoogleAlexaProjectDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


AddGoogleAlexaProjectDetails = AddGoogleAlexaProjectDetailsAPI.as_view()


def SignInProcessorConsole(request):
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        if not check_access_for_user(request.user, None, "Intent Related", "overall"):
            return HttpResponseNotFound("You do not have access to this page")
        if request.user.supervisor:
            detail_obj_id = request.GET["id"]
            processor_type = request.GET["type"]

            google_assistant_details_obj = GoogleAlexaProjectDetails.objects.get(
                id=int(detail_obj_id))
            bot_pk = str(google_assistant_details_obj.bot.id)
            sign_in_processor = None
            if processor_type == "get_otp":
                sign_in_processor = google_assistant_details_obj.get_otp_processor
            else:
                sign_in_processor = google_assistant_details_obj.verify_otp_processor

            if sign_in_processor:
                name = sign_in_processor.name
                code = check_common_utils_line(
                    sign_in_processor.api_caller, bot_pk)
            else:
                name = "asdhs524fdbghdagfht52eg2fc"
                code = get_common_utils_file_code(bot_pk)
                code += SIGN_IN_PROCESSOR_BASE_PYTHON_CODE

            dynamic_variable = get_dynamic_variables(code)

            config_obj = Config.objects.all()[0]
            system_commands = json.loads(
                config_obj.system_commands.replace("'", '"'))

            return render(request, "EasyChatApp/edit_sign_in_processor.html", {
                "name": name,
                "code": code,
                "dynamic_variable": dynamic_variable,
                "system_commands": system_commands,
                "lang": "1",
                "processor_type": processor_type,
                "detail_obj_id": detail_obj_id,
            })
        else:
            # return HttpResponse("Invalid Access")
            return render(request, 'EasyChatApp/error_404.html')
    else:
        return HttpResponseRedirect("/chat/login")


def EditConsolePage(request):
    if is_allowed(request, [BOT_BUILDER_ROLE]):
        if not check_access_for_user(request.user, None, "Intent Related", "overall"):
            return HttpResponseNotFound("You do not have access to this page")
        if request.user.supervisor:
            detail_obj_id = request.GET["id"]
            channel = request.GET["channel"]

            if channel == "googlehome":
                html_file = open(
                    settings.BASE_DIR + "/EasyChatApp/templates/EasyChatApp/channels/ga_auth_" + str(detail_obj_id) + ".html", "r")
                code = html_file.read()
                html_file.close()
            elif channel == "alexa":
                html_file = open(
                    settings.BASE_DIR + "/EasyChatApp/templates/EasyChatApp/channels/alexa_auth_" + str(detail_obj_id) + ".html", "r")
                code = html_file.read()
                html_file.close()
            else:
                return HttpResponseRedirect("/chat/login")

            return render(request, "EasyChatApp/edit_console_page.html", {
                "code": code,
                "detail_obj_id": detail_obj_id,
                "channel": channel
            })
        else:
            # return HttpResponse("Invalid Access")
            return render(request, 'EasyChatApp/error_404.html')
    else:
        return HttpResponseRedirect("/chat/login")


class SaveSignInProcessorContentAPI(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            user_obj = User.objects.get(username=request.user.username)
            data = urllib.parse.unquote(request.data['json_string'])
            data = DecryptVariable(data)
            data = json.loads(data)

            code = data["code"]
            processor_type = data["processor_type"]
            detail_obj_id = data["detail_obj_id"]
            name = data["name"]
            is_new = data["is_new"]

            google_assistant_details_obj = GoogleAlexaProjectDetails.objects.get(
                id=int(detail_obj_id))

            if check_for_system_commands(code, Config):
                response['status'] = 400
                response[
                    'message'] = "Code contains system commands. Please remove them and then save."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(
                    json.dumps(response))
                return Response(data=response)

            if str(is_new) == "True":
                if processor_type == "get_otp":

                    if not SignInProcessor.objects.filter(name=name).exists():
                        processor_obj = SignInProcessor.objects.create(
                            name=name, api_caller=code)
                        google_assistant_details_obj.get_otp_processor = processor_obj
                    else:
                        response["status"] = 300
                        response["message"] = "Duplicate name exists."
                        logger.error("Duplicate name exists SaveSignInProcessorContentAPI", extra={'AppName': 'EasyChat', 'user_id': str(
                            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)

                else:
                    if not SignInProcessor.objects.filter(name=name).exists():
                        processor_obj = SignInProcessor.objects.create(
                            name=name, api_caller=code)
                        google_assistant_details_obj.verify_otp_processor = processor_obj
                    else:
                        response["status"] = 300
                        response["message"] = "Duplicate name exists."
                        logger.error("Duplicate name exists SaveSignInProcessorContentAPI", extra={'AppName': 'EasyChat', 'user_id': str(
                            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)
                audit_trail_data = json.dumps({
                    "processor": processor_type,
                    "processor_name": name
                })
                save_audit_trail(
                    user_obj, CREATE_PROCESSOR_ACTION, audit_trail_data)
            else:
                # any_change_detected = False
                if processor_type == "get_otp":
                    processor_obj = google_assistant_details_obj.get_otp_processor
                    # if processor_obj.api_caller != code:
                    #     any_change_detected = True
                    processor_obj.api_caller = code
                    processor_obj.name = name
                    processor_obj.save(True)

                else:
                    processor_obj = google_assistant_details_obj.verify_otp_processor
                    # if processor_obj.api_caller != code:
                    #     any_change_detected = True
                    processor_obj.api_caller = code
                    processor_obj.name = name
                    processor_obj.save(True)

                audit_trail_data = json.dumps({
                    "processor": processor_type,
                    "processor_name": name
                })

                save_audit_trail(
                    user_obj, EDIT_PROCESSOR_ACTION, audit_trail_data)

            google_assistant_details_obj.save()
            response["status"] = 200
            response["message"] = "SUCCESS"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveProcessorContent: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveSignInProcessorContent = SaveSignInProcessorContentAPI.as_view()


###################################### ET Source #########################


class EditETSourceChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            username = request.user.username

            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_pk = data["bot_id"]
            user_obj = User.objects.get(username=str(username))
            bot_obj = Bot.objects.get(pk=int(bot_pk), users__in=[
                                      user_obj], is_deleted=False)

            channel = Channel.objects.get(name="ET-Source")
            botchannel = BotChannel.objects.get(bot=bot_obj, channel=channel)
            initial_messages = json.loads(botchannel.initial_messages)
            initial_messages_list = get_message_list_using_pk(
                initial_messages["items"])
            try:
                initial_messages = {"items": initial_messages_list, "images": initial_messages[
                    "images"], "videos": initial_messages["videos"]}
            except Exception:
                initial_messages = {"items": initial_messages_list}
            response["initial_message"] = initial_messages

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditETSourceChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EditETSourceChannelDetails = EditETSourceChannelDetailsAPI.as_view()


class SaveETSourceChannelDetailsAPI(APIView):

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

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]
            # welcome_message = validation_obj.custom_remo_html_tags(welcome_message)
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            # failure_message = validation_obj.custom_remo_html_tags(failure_message)
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            # authentication_message = validation_obj.custom_remo_html_tags(authentication_message)
            authentication_message = validation_obj.clean_html(
                authentication_message)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            initial_message_list = data["initial_message_list"]
            failure_recommendation_list = data["failure_recommendation_list"]
            image_url = data["image_url"]
            video_url = data["video_url"]
            bot_id = data["bot_id"]
            validation_obj = EasyChatInputValidation()
            welcome_message = validation_obj.remo_html_from_string(
                welcome_message)

            images = []
            if image_url != "":
                images = [image_url]

            videos = []
            if video_url != "":
                videos = [video_url]

            initial_message_list = [
                str(message) for message in initial_message_list if message != ""]

            bot = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            channel = Channel.objects.get(name="ET-Source")
            channel = BotChannel.objects.get(bot=bot, channel=channel)

            # Language specific
            language_specific_action(
                data, channel, bot, welcome_message, failure_message, authentication_message)

            channel.initial_messages = json.dumps(
                {"items": initial_message_list, "images": images, "videos": videos})
            channel.failure_recommendations = json.dumps(
                {"items": failure_recommendation_list})
            channel.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveETSourceChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveETSourceChannelDetails = SaveETSourceChannelDetailsAPI.as_view()


class SaveWelcomeBannerAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            bot_id = data["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)
            channel_name = data["channel_name"]
            channel_name = validation_obj.remo_html_from_string(channel_name)
            action_type = data["action_type"]
            action_type = validation_obj.remo_html_from_string(action_type)
            image_url = data["image_url"]
            image_url = validation_obj.remo_html_from_string(image_url)

            redirection_url = data["redirection_url"]
            redirection_url = validation_obj.remo_html_from_string(
                redirection_url)
            incorrect_url = False

            if not validation_obj.is_valid_url(redirection_url) and action_type != "2":
                response["message"] = "Please enter valid redirection Url"
                incorrect_url = True

            if not validation_obj.is_valid_url(image_url):
                response["message"] = "Please enter valid image Url"
                incorrect_url = True

            if incorrect_url:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            intent_pk = data["intent_pk"]
            intent_pk = validation_obj.remo_html_from_string(intent_pk)

            bot_obj = Bot.objects.get(pk=bot_id)
            channel_obj = Channel.objects.get(name=channel_name)
            bot_channel_obj = BotChannel.objects.get(
                bot=bot_obj, channel=channel_obj)

            if action_type == "2":
                redirection_url = ""

            intent_obj = None
            if action_type == "2" or action_type == "3":
                intent_obj = Intent.objects.get(pk=intent_pk)

            welcome_banner_existing_objs = WelcomeBanner.objects.filter(
                bot_channel=bot_channel_obj)
            serial_number = welcome_banner_existing_objs.count() + 1

            welcome_banner_obj = WelcomeBanner.objects.create(
                action_type=action_type, image_url=image_url, redirection_url=redirection_url, intent=intent_obj, serial_number=serial_number, bot_channel=bot_channel_obj)
            welcome_banner_obj.save()

            response["status"] = 200
            response["message"] = "Welcome banner created successfully"
            response["welcome_banner_pk"] = welcome_banner_obj.pk
            response["action_type"] = welcome_banner_obj.action_type
            response["image_url"] = welcome_banner_obj.image_url
            response["redirection_url"] = welcome_banner_obj.get_redirection_url()
            response["intent_pk"] = welcome_banner_obj.get_intent_pk()
            response["intent_name"] = welcome_banner_obj.get_intent_name()
            response["image_name"] = welcome_banner_obj.get_image_name()

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveWelcomeBannerAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveWelcomeBanner = SaveWelcomeBannerAPI.as_view()


class EditWelcomeBannerAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "There are some issues while editing welcome banner."
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            wb_id = data["wb_id"]
            wb_id = validation_obj.remo_html_from_string(wb_id)
            redirected_url = data["redirected_url"]
            redirected_url = validation_obj.remo_html_from_string(
                redirected_url)

            intent_id = data["intent_id"]
            intent_id = validation_obj.remo_html_from_string(intent_id)

            welcome_banner_obj = WelcomeBanner.objects.get(pk=wb_id)

            if not validation_obj.is_valid_url(redirected_url) and welcome_banner_obj.action_type != "2":
                response["message"] = "Please enter valid redirect url."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            redirect_url = None
            if welcome_banner_obj.action_type != "2":
                redirect_url = redirected_url

            intent_obj = None
            if welcome_banner_obj.action_type != "1":
                intent_obj = Intent.objects.get(pk=intent_id)

            welcome_banner_obj.redirection_url = redirect_url
            welcome_banner_obj.intent = intent_obj
            welcome_banner_obj.save()

            response["status"] = 200
            response["action_type"] = welcome_banner_obj.action_type
            response["redirection_url"] = welcome_banner_obj.get_redirection_url()
            response["intent_id"] = welcome_banner_obj.get_intent_pk()
            response["wb_id"] = welcome_banner_obj.pk
            response["intent_name"] = welcome_banner_obj.get_intent_name()

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditWelcomeBannerAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EditWelcomeBanner = EditWelcomeBannerAPI.as_view()


class DeleteWelcomeBannerAPI(APIView):

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

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            wb_id = data["wb_id"]
            wb_id = validation_obj.remo_html_from_string(wb_id)

            wb_obj = WelcomeBanner.objects.get(pk=wb_id)
            bot_channel_obj = wb_obj.bot_channel
            wb_obj.delete()

            wb_objs = WelcomeBanner.objects.filter(
                bot_channel=bot_channel_obj).order_by("serial_number")

            count = 1
            for wb in wb_objs:
                wb.serial_number = count
                wb.save()
                count += 1

            response["status"] = 200
            response["wb_id"] = wb_id

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteWelcomeBannerAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


DeleteWelcomeBanner = DeleteWelcomeBannerAPI.as_view()


class GetWhatsAppWebhookDefaultCodeAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            wsp_value = data["wsp_code"]
            wsp_value = validation_obj.remo_html_from_string(wsp_value)

            wsp_obj = WhatsAppServiceProvider.objects.filter(
                name=wsp_value).first()

            if wsp_obj:
                sample_file_path = wsp_obj.default_code_file_path
                if sample_file_path != None and sample_file_path != "":
                    file_obj = open(sample_file_path, "r")
                    response["default_code"] = file_obj.read()
                    response["status"] = 200
                    response["message"] = "Success"
                else:
                    response["message"] = "Cannot find default code for {} WhatsApp BSP.".format(
                        wsp_obj.get_name_display())
                response["wsp_name"] = wsp_obj.get_name_display()
            else:
                response["message"] = "WhatsApp BSP does not exists."
                response["wsp_name"] = ""

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetWhatsAppWebhookDefaultCodeAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GetWhatsAppWebhookDefaultCode = GetWhatsAppWebhookDefaultCodeAPI.as_view()


def RCSChannel(request):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            user_obj = User.objects.get(username=str(request.user.username))
            if not check_access_for_user(request.user, None, "Bot Setting Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")

            bot_pk_list = get_uat_bots_pk_list(user_obj)
            if int(request.GET['id']) in bot_pk_list:
                bot_pk = request.GET['id']
                selected_language = request.GET.get("selected_lang", "en")
                if not check_access_for_user(request.user, bot_pk, "Bot Setting Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

                channel_obj = Channel.objects.get(name="GoogleRCS")
                bot_channel_obj = BotChannel.objects.get(bot=selected_bot_obj, channel=channel_obj)

                initial_messages_pk_list = json.loads(bot_channel_obj.initial_messages)["items"]
                failure_messages_pk_list = json.loads(bot_channel_obj.failure_recommendations)["items"]

                intent_objs = Intent.objects.filter(bots__in=[selected_bot_obj], channels=channel_obj,
                                                    is_deleted=False,
                                                    is_form_assist_enabled=False,
                                                    is_hidden=False)

                rcs_obj = RCSDetails.objects.filter(bot=selected_bot_obj)
                rcs_credentials_file_name = ""
                if rcs_obj.count() == 0:
                    rcs_obj = RCSDetails.objects.create(
                        bot=selected_bot_obj)

                else:
                    rcs_obj = rcs_obj[0]
                    rcs_credentials_file_name = (
                        rcs_obj.rcs_credentials_file_path).split("/")[-1]

                intent_name_list = []
                intent_name_list_failure = []
                for intent_obj_pk in initial_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                for intent_obj_pk in failure_messages_pk_list:
                    intent_objs = Intent.objects.filter(
                        pk=int(intent_obj_pk), channels=channel_obj, is_hidden=False, is_deleted=False)
                    if intent_objs:
                        intent_obj = intent_objs[0]
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": True,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                all_intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], channels=channel_obj, is_hidden=False, is_deleted=False)
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in initial_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })
                for intent_obj in all_intent_objs:
                    if str(intent_obj.pk) not in failure_messages_pk_list:
                        small_talk = intent_obj.is_small_talk
                        if small_talk == False:
                            intent_name_list_failure.append({
                                "is_selected": False,
                                "intent_name": intent_obj.name,
                                "intent_pk": intent_obj.pk
                            })

                master_languages = selected_bot_obj.languages_supported.all()
                language_tuned_object = bot_channel_obj
                activity_update = json.loads(bot_channel_obj.activity_update)
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(
                    bot_channel_obj, activity_update, selected_language, LanguageTunedBotChannel)

                if selected_language != "en":
                    response = {}
                    response["welcome_message"] = bot_channel_obj.welcome_message
                    response["failure_message"] = bot_channel_obj.failure_message
                    response[
                        "authentication_message"] = bot_channel_obj.authentication_message
                    create_language_tuned_object = True
                    check_and_create_channel_details_language_tuning_objects(
                        response, selected_language, bot_channel_obj, create_language_tuned_object, Language, LanguageTunedBotChannel, EasyChatTranslationCache)
                    lang_obj = Language.objects.get(lang=selected_language)
                    language_tuned_object = LanguageTunedBotChannel.objects.filter(
                        language=lang_obj, bot_channel=bot_channel_obj)[0]

                first_three_selected_languages = bot_channel_obj.languages_supported.all()[
                    :3]
                # count_of_overhead_languages > tells how many  more languages
                # are selected  after first five
                count_of_overhead_languages = bot_channel_obj.languages_supported.all().count() - 3

                return render(request, 'EasyChatApp/channels/google_rcs.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "bot_channel_obj": bot_channel_obj,
                    "rcs_credentials_file_name": rcs_credentials_file_name,
                    "master_languages": master_languages,
                    "first_three_selected_languages": first_three_selected_languages,
                    "count_of_overhead_languages": count_of_overhead_languages,
                    "selected_language": selected_language,
                    "language_tuned_object": language_tuned_object,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                })
            else:
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("RCSChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(request.GET['id'])})
        return render(request, 'EasyChatApp/error_500.html')


class SaveGoogleRCSChannelDetailsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            welcome_message = data["welcome_message"]
            # welcome_message = validation_obj.custom_remo_html_tags(welcome_message)
            welcome_message = validation_obj.clean_html(welcome_message)

            failure_message = data["failure_message"]
            # failure_message = validation_obj.custom_remo_html_tags(failure_message)
            failure_message = validation_obj.clean_html(failure_message)

            authentication_message = data["authentication_message"]
            # authentication_message = validation_obj.custom_remo_html_tags(authentication_message)
            authentication_message = validation_obj.clean_html(
                authentication_message)

            welcome_message, failure_message, authentication_message = check_and_parse_channel_messages(
                welcome_message, failure_message, authentication_message)

            response["status"], response["message"] = check_channel_status_and_message(
                welcome_message, failure_message, authentication_message)

            if response["status"] == 400:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            failure_recommendation_list = data["failure_recommendation_list"]
            image_url = ""
            video_url = ""
            bot_id = data["bot_id"]

            images = []
            if image_url != "":
                images = [image_url]

            videos = []
            if video_url != "":
                videos = [video_url]

            initial_message_list = []

            bot = Bot.objects.filter(pk=int(bot_id), is_deleted=False).first()

            if not bot:
                response["status"] = 402
                response["message"] = BOT_DELETED_ERROR_MESSAGE
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            if user_obj not in bot.users.all():
                return HttpResponseForbidden("You do not have access to this page")

            channel = Channel.objects.get(name="GoogleRCS")
            bot_channel = BotChannel.objects.get(bot=bot, channel=channel)

            # Language specific
            language_specific_action(
                data, bot_channel, bot, welcome_message, failure_message, authentication_message)

            bot_channel.failure_recommendations = json.dumps(
                {"items": failure_recommendation_list})

            bot_channel.initial_messages = json.dumps(
                {"items": initial_message_list, "images": images, "videos": videos})

            bot_channel.save()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveGoogleRCSChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveGoogleRCSChannelDetails = SaveGoogleRCSChannelDetailsAPI.as_view()


class UploadRCSCredentialFileAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            uploaded_file = request.FILES.getlist('file')[0]

            bot_id = request.data['bot_id']

            uploaded_file_name = uploaded_file.name
            uploaded_file_name = get_dot_replaced_file_name(uploaded_file_name)

            if uploaded_file_name.split('.')[-1] != "json":
                response["status"] = 300

                return Response(data=response)

            try:
                if not os.path.exists('secured_files/EasyChatApp/RCSCredentials'):
                    os.makedirs('secured_files/EasyChatApp/RCSCredentials')

                path = os.path.join(settings.SECURE_MEDIA_ROOT,
                                    "EasyChatApp/RCSCredentials/")

                fs = FileSystemStorage(location=path)
                filename = fs.save(
                    uploaded_file.name.replace(" ", ""), uploaded_file)

                path = "/secured_files/EasyChatApp/RCSCredentials/" + filename

                EasyChatAppFileAccessManagement.objects.create(
                    file_path=path, is_public=False)

                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_id), is_deleted=False, is_uat=True)

                rcs_obj = RCSDetails.objects.filter(bot=selected_bot_obj)

                if rcs_obj.count() == 0:
                    rcs_obj = RCSDetails.objects.create(
                        bot=selected_bot_obj)

                else:
                    rcs_obj = rcs_obj[0]
                path = "secured_files/EasyChatApp/RCSCredentials/" + filename
                rcs_obj.rcs_credentials_file_path = path
                rcs_obj.save()

                filename = path.split("/")[-1]
                response['filename'] = filename

            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error UploadFilesIntoDriveAPI For Loop: %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error UploadFilesIntoDriveAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return Response(data=response)


UploadRCSCredentialFile = UploadRCSCredentialFileAPI.as_view()


def GetAMPJS(request):

    try:
        bot_id = request.GET["id"]
        selected_bot_obj = None
        selected_bot_obj = Bot.objects.get(
            pk=int(bot_id), is_deleted=False, is_uat=True)

        if selected_bot_obj:

            deploy_url = "/files/deploy/embed_chatbot_" + \
                str(selected_bot_obj.pk) + ".js"
            is_deploy_js_exist = os.path.exists(
                settings.BASE_DIR + "/files/deploy/embed_chatbot_" + str(selected_bot_obj.pk) + ".js")

            if is_deploy_js_exist:
                return HttpResponse("<script src='" + settings.EASYCHAT_HOST_URL + deploy_url + "'></script>")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("GetAMPJS: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return HttpResponse("500")


def GetAMPBotImage(request, bot_id):
    try:
        bot_obj = Bot.objects.get(pk=bot_id)

        bot_image_path = os.getcwd() + "/EasyChatApp/static/EasyChatApp/img/popup-4.gif"
        if bot_obj.bot_image.name:
            bot_image_path = os.getcwd() + bot_obj.bot_image.name
        
        image_data = open(bot_image_path, "rb").read()

        mime = magic.Magic(mime=True)
        content_type = mime.from_file(bot_image_path)

        return HttpResponse(image_data, content_type=content_type)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("GetAMPBotImage: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
