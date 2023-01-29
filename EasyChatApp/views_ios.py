from EasyChatApp.utils_validation import EasyChatInputValidation
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password

from django.contrib.auth import authenticate, login
from django.shortcuts import render, HttpResponse, \
    HttpResponseRedirect
from django.http import HttpResponseNotFound, HttpResponseForbidden

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_channels import *
from EasyChatApp.utils_bot import *
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

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def IOSChannel(request):  # noqa: N802
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

                channel_obj = Channel.objects.get(name="iOS")

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
                auto_pop_up_text = selected_bot_obj.auto_pop_text
                bot_web_landing_list = json.loads(
                    selected_bot_obj.web_url_landing_data)

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
                phonetic_typing_enabled_languages = get_list_of_phonetic_typing_suported_languages(LANGUGES_SUPPORTING_PHONETIC_TYPING)
                if bot_channel_obj.languages_supported.all().filter(lang__in=phonetic_typing_enabled_languages).exists():
                    is_phonetic_language_supported = True
                need_to_show_auto_fix_pop_up = need_to_show_auto_fix_popup_for_channels(bot_channel_obj,
                                                                                        activity_update, selected_language, LanguageTunedBotChannel)

                deployment_url = settings.EASYCHAT_HOST_URL + \
                    "/chat/index/?id=" + str(bot_pk) + "&channel=iOS"

                easychat_themes = EasyChatTheme.objects.all().order_by("name")

                welcome_banner_objs = WelcomeBanner.objects.filter(bot_channel=bot_channel_obj).order_by("serial_number")

                bot_info_obj = BotInfo.objects.get(bot=selected_bot_obj)

                return render(request, 'EasyChatApp/channels/ios_channel.html', {
                    "selected_bot_obj": selected_bot_obj,
                    "bot_id": request.GET['id'],
                    "intent_name_list": intent_name_list,
                    "intent_name_list_failure": intent_name_list_failure,
                    "bot_position_choices": BOT_POSITION_CHOICES,
                    # "google_home_deploy_url": google_home_url,
                    "theme_selected": theme_selected,
                    "intent_name_list_sticky": intent_name_list_sticky,
                    "bot_channel_obj": bot_channel_obj,
                    "bot_web_landing_list": bot_web_landing_list,
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
                    "auto_pop_up_text": auto_pop_up_text,
                    "need_to_show_auto_fix_pop_up": need_to_show_auto_fix_pop_up,
                    "is_phonetic_language_supported": is_phonetic_language_supported,
                    "deployment_url": deployment_url,
                    "easychat_themes": easychat_themes,
                    "welcome_banner_intent_objs": all_intent_objs.filter(channels__in=Channel.objects.filter(name="iOS")),
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
        logger.error("iosChannel ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(selected_bot_obj.pk)})
        return render(request, 'EasyChatApp/error_404.html')


class SaveIOSChannelDetailsAPI(APIView):

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
            authentication_message = validation_obj.clean_html(authentication_message)

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
                intent_icon_selected_channel_choices["ios"] = intent_icon_channel_choices
                bot_info_obj.intent_icon_channel_choices_info = json.dumps(intent_icon_selected_channel_choices)
            
            bot_info_obj.save()
            
            Intent.objects.filter(bots=bot).update(
                is_part_of_initial_web_trigger_intent=False)

            bot.default_theme = get_easychat_theme_obj(theme_selected)
            bot.bot_theme_color = bot_theme_color
            bot.save()
            check_and_create_bot_language_template_obj(
                bot, selected_supported_languages, RequiredBotTemplate, Language)

            channels = Channel.objects.filter(name__in=["iOS"])
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
                    welcome_banner_obj = WelcomeBanner.objects.get(pk=welcome_banner_id)
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
            logger.error("SaveIOSChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class EditIOSChannelDetailsAPI(APIView):

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

            channel = Channel.objects.get(name="iOS")
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
            response["welcome_banner_count"] = WelcomeBanner.objects.filter(bot_channel=botchannel).count()
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("EditIOSChannelDetailsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveIOSChannelDetails = SaveIOSChannelDetailsAPI.as_view()

EditIOSChannelDetails = EditIOSChannelDetailsAPI.as_view()
