from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.http import FileResponse
from django.shortcuts import render, HttpResponseRedirect, redirect,\
    HttpResponse
from django.http import HttpResponseNotFound
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Q

from EasyChatApp.models import *
from EasyChatApp.utils import *
from EasyChatApp.utils_analytics import *
from EasyChatApp.utils_validation import EasyChatFileValidation, EasyChatInputValidation
from EasyChatApp.utils_bot import get_supported_languages, check_and_update_tunning_object, need_to_show_auto_fix_popup_for_intents, save_intent_category
from EasyChatApp.utils_voicebot import get_selected_tts_provider_name
from EasyChatApp.constants import *
from EasyChatApp.intent_icons_constants import INTENT_ICONS
from EasyChatApp.utils_translation_module import translate_given_text_to_english
from EasyChatApp.utils_channels import check_and_update_whatsapp_menu_objs
from difflib import get_close_matches

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import json
import datetime
import logging
import sys
from bs4 import BeautifulSoup
import threading
import pytz
import os
import html
easychat_timezone = pytz.timezone(settings.TIME_ZONE)
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk import FreqDist
# from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def IntentConsole(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Intent Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")

            is_filter_applied = False

            selected_bot_obj = None
            if "bot_pk" in request.GET:
                bot_pk = request.GET["bot_pk"]
                if not check_access_for_user(request.user, bot_pk, "Intent Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

            intent_type = ""
            intent_type_name = ""
            if "intent_type" in request.GET:
                intent_type = request.GET["intent_type"]
                if intent_type == "all_intent":
                    intent_type = ""
                else:
                    is_filter_applied = True

            selected_language = "en"
            if "selected_language" in request.GET:
                selected_language = request.GET["selected_language"]

            channel_name = ""
            if "channel_name" in request.GET:
                channel_name = request.GET["channel_name"]
                is_filter_applied = True

            intent_objs = Intent.objects.none()
            if selected_bot_obj != None:
                intent_objs = Intent.objects.filter(
                    bots__in=[selected_bot_obj], is_deleted=False, is_hidden=False).order_by('-pk')

            category_obj = Category.objects.filter(
                bot=selected_bot_obj).order_by("pk")
            category = ""
            if "category" in request.GET:
                category = request.GET["category"]
                is_filter_applied = True

            if category not in ["", "all_category"]:
                intent_objs = intent_objs.filter(
                    category=category_obj.filter(name=category))

            category_id = "0"
            if "category_id" in request.GET:
                category_id = request.GET["category_id"]
                is_filter_applied = True

            selected_category_index = 0
            filtered_category_obj = None
            if category_id != "0":
                try:
                    filtered_category_obj = category_obj.filter(pk=category_id)[
                        0]
                    intent_objs = intent_objs.filter(
                        category=filtered_category_obj)

                    index = 1
                    for category in category_obj:
                        if category == filtered_category_obj:
                            selected_category_index = index
                            break
                        index += 1
                except:
                    filtered_category_obj = None

            if channel_name != "":
                channel_obj = Channel.objects.filter(name=channel_name)
                intent_objs = intent_objs.filter(channels__in=channel_obj)

            if intent_type not in ["", "all_intent"]:
                if intent_type == "is_form_assist_intent":
                    intent_objs = intent_objs.filter(
                        is_form_assist_enabled=True).order_by('-pk')
                    intent_type_name = "Form Assist Intents"
                elif intent_type == "is_attachment_required":
                    intents_list = []
                    for intent in intent_objs:
                        if intent.tree.response and 'is_attachment_required' in json.loads(intent.tree.response.modes):
                            if json.loads(intent.tree.response.modes)['is_attachment_required'] == 'true':
                                intents_list.append(intent)
                    intent_type_name = "Has Attachment(s)"

                    intent_objs = intents_list
                elif intent_type == "is_small_talk":
                    intent_objs = intent_objs.filter(
                        is_small_talk=True).order_by('-pk')
                    intent_type_name = "Small Talk"

            page = request.GET.get('page')
            page_no = 1
            try:
                page_no = int(page)
            except:
                page_no = 1

            start = ((page_no - 1) * MAX_INTENT_PER_PAGE)
            if start < 0:
                start = 0
            end = page_no * MAX_INTENT_PER_PAGE

            supported_language = get_supported_languages(
                selected_bot_obj, BotChannel)
            # Getting tuned language objects
            selected_language_obj = Language.objects.get(
                lang=selected_language)

            temp_intent_objs = intent_objs[start:end]

            for intent_obj in temp_intent_objs:
                check_and_update_tunning_object(intent_obj, selected_language_obj, LanguageTuningIntentTable, LanguageTuningTreeTable,
                                                LanguageTuningBotResponseTable, LanguageTuningChoicesTable, EasyChatTranslationCache)

            intent_tunning_objs = LanguageTuningIntentTable.objects.filter(
                intent__in=temp_intent_objs, language=selected_language_obj).order_by('-pk')
            total_intents = 0

            if isinstance(intent_objs, list):
                total_intents = len(intent_objs)
            else:
                total_intents = intent_objs.count()

            paginator = Paginator(intent_objs, MAX_INTENT_PER_PAGE)
            page = request.GET.get('page')

            try:
                intent_objs = paginator.page(page)
            except PageNotAnInteger:
                intent_objs = paginator.page(1)
            except EmptyPage:
                intent_objs = paginator.page(paginator.num_pages)

            selected_intents = len(intent_objs)

            is_small_talk_disable = selected_bot_obj.is_small_talk_disable
            if selected_language_obj not in supported_language:
                selected_language = "en"

            channel_list = get_channel_list(Channel)

            return render(request, 'EasyChatApp/platform/intent.html', {
                "selected_bot_obj": selected_bot_obj,
                "intent_objs": intent_objs,
                "selected_intents": selected_intents,
                "total_intents": total_intents,
                "intent_type": intent_type,
                "intent_type_name": intent_type_name,
                "is_small_talk_disable": is_small_talk_disable,
                "categories": category_obj,
                "selected_category": category,
                "supported_language": supported_language,
                "selected_language": selected_language,
                "intent_tunning_objs": intent_tunning_objs,
                "is_filter_applied": is_filter_applied,
                "channel_name": channel_name,
                "selected_category_index": selected_category_index,
                "filtered_category_obj": filtered_category_obj,
                "channel_list": channel_list
            })
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("IntentConsole ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        # return HttpResponseNotFound("Page not found")
        return render(request, 'EasyChatApp/error_404.html')


def CreateIntentConsole(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Intent Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            config = Config.objects.all()[0]

            selected_bot_obj = None
            if "bot_pk" in request.GET:
                bot_pk = request.GET["bot_pk"]
                if not check_access_for_user(request.user, bot_pk, "Intent Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

            if selected_bot_obj == None:
                return redirect("/chat/intent/")

            # user_obj = User.objects.get(username=str(request.user.username))
            user_obj = User.objects.get(username=str(request.user.username))

            # bot_objs = Bot.objects.filter(users__in=[user_obj])
            bot_objs = get_uat_bots(user_obj)

            intent_pk_list = []
            if selected_bot_obj == None:
                intent_pk_list = list(Intent.objects.filter(bots__in=bot_objs,
                                                            is_deleted=False,
                                                            is_form_assist_enabled=False,
                                                            is_hidden=False).values_list("pk", flat=True))
            else:
                intent_pk_list = list(Intent.objects.filter(bots__in=[selected_bot_obj],
                                                            is_deleted=False,
                                                            is_form_assist_enabled=False,
                                                            is_hidden=False).values_list("pk", flat=True))

            all_file_type = get_all_file_type()

            modified_intent_list = []
            for intent_pk in intent_pk_list:
                try:
                    intent = Intent.objects.get(
                        pk=int(intent_pk), is_hidden=False, is_deleted=False)
                except Exception:
                    intent = None

                small_talk = intent.is_small_talk
                if small_talk == False:
                    icon = None
                    if intent.build_in_intent_icon:
                        icon = intent.build_in_intent_icon.icon
                    elif intent.intent_icon:
                        icon = icon = "<img src='" + intent.intent_icon + "'>"
                    modified_intent_list.append({
                        "is_selected": False,
                        "intent_name": intent.name,
                        "intent_pk": intent_pk,
                        "icon": icon
                    })

            channel_list = list(
                Channel.objects.filter(is_easychat_channel=True).values("name", "icon"))
            modified_channel_list = []
            for channel in channel_list:
                modified_channel_list.append({
                    "is_selected": True,
                    "channel_name": channel["name"],
                    "icon": channel["icon"]
                })

            # livechatconfig = LiveChatConfig.objects.all()
            # livechat_config = livechatconfig[0]

            tag_mapper_objs = get_tag_mapper_list_for_given_user(request)

            authentication_objs = get_authentication_objs([selected_bot_obj])

            user_objs = User.objects.all()

            # languages_supported = selected_bot_obj.languages_supported.all()

            # language_supported = []
            # for language in languages_supported:
            #     language_supported.append(language.lang)

            hindi_supported = False
            # if len(language_supported) >= 1:
            #     hindi_supported = True

            validators = ProcessorValidator.objects.filter(
                bot=selected_bot_obj)
            selected_validator_obj = None

            bot_form_assist_enabled = False
            if selected_bot_obj != None:
                bot_form_assist_enabled = selected_bot_obj.is_form_assist_enabled

            if selected_bot_obj != None:
                category_objs = Category.objects.filter(bot=selected_bot_obj)
            else:
                category_objs = Category.objects.all()

            selected_category_obj = None
            try:
                selected_category_obj = Category.objects.get(
                    name="Others", bot=selected_bot_obj)
            except Exception:
                selected_category_obj = None
            need_to_show_auto_fix_popup = False

            bot_info_obj = BotInfo.objects.get(bot=selected_bot_obj)

            built_in_intent_icons = BuiltInIntentIcon.objects.all().order_by("pk")

            selected_tts_provider = get_selected_tts_provider_name(
                selected_bot_obj, BotChannel)

            supported_language = get_supported_languages(
                selected_bot_obj, BotChannel)

            welcome_message = []
            web_channel_obj = BotChannel.objects.filter(bot=selected_bot_obj, channel__name="Web").first()
            if web_channel_obj:
                welcome_message = web_channel_obj.welcome_message.split("$$$")

            if request.COOKIES.get("edit_intent_ui", "new") == "old":
                template_name = 'EasyChatApp/platform/edit_intent.html'
            else:
                template_name = 'EasyChatApp/platform/edit_intent_revised.html'

            return render(request, template_name, {
                'is_new_intent': True,
                'config': config,
                "selected_bot_obj": selected_bot_obj,
                'intent_name_list': modified_intent_list,
                'intent_name_list_updated': json.dumps(modified_intent_list),
                'channel_list': modified_channel_list,
                'short_name_enabled': True,
                'short_name_value': "",
                "intent_name": "",
                "multilingual_intent_name": "",
                "is_feedback_required": True,
                "is_attachment_required": False,
                "all_file_type": all_file_type,
                # "is_livechat_enabled": False,
                "is_authentication_required": False,
                "is_part_of_suggestion_list": True,
                "is_form_assist_enabled": False,
                "is_child_tree_visible": True,
                "is_small_talk": False,
                "tag_mapper_objs": tag_mapper_objs,
                "hindi_supported": hindi_supported,
                "user_objs": user_objs,
                "authentication_objs": authentication_objs,
                "validators": validators,
                "selected_validator_obj": selected_validator_obj,
                "bot_form_assist_enabled": bot_form_assist_enabled,
                "category_objs": category_objs,
                "selected_category_obj": selected_category_obj,
                "selected_language": "en",
                "need_to_show_auto_fix_popup": need_to_show_auto_fix_popup,
                "whatsapp_list_message_header": "Options",
                "bot_info_obj": bot_info_obj,
                "built_in_intent_icons": built_in_intent_icons,
                "selected_tts_provider": selected_tts_provider,
                "is_faq_intent": False,
                "disposition_code": "",
                "supported_language": supported_language,
                "show_whatsapp_menu_section_feature": True,
                "INTENT_TREE_NAME_CHARACTER_LIMIT": INTENT_TREE_NAME_CHARACTER_LIMIT,
                "welcome_message": welcome_message,
                # "livechat_config": livechat_config,
            })
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("CreateIntentConsole ! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        # return HttpResponseNotFound(INVALID_REQUEST)
        return render(request, 'EasyChatApp/error_500.html')


def EditIntentConsole(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Intent Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            config = Config.objects.all()[0]

            selected_bot_obj = None
            bot_pk = None
            if "bot_pk" in request.GET:
                bot_pk = request.GET["bot_pk"].split("#")[0]
                if not check_access_for_user(request.user, bot_pk, "Intent Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)

            selected_language = "en"

            if "selected_language" in request.GET:
                selected_language = request.GET["selected_language"].split("#")[0]

            if selected_language != "en" and request.COOKIES.get("edit_intent_ui", "new") == "old":
                return HttpResponseRedirect("/chat/edit-intent-multilingual/?intent_pk=" + str(request.GET['intent_pk']) + "&selected_language=" + selected_language)

            selected_language_obj = Language.objects.filter(
                lang=selected_language).first()

            if not selected_language_obj:
                selected_language = "en"
                selected_language_obj = Language.objects.filter(
                    lang=selected_language).first()

            # is_livechat_enabled = False
            user_obj = User.objects.get(username=str(request.user.username))
            bot_objs = get_uat_bots(user_obj)

            intent_obj = None
            rows = 0
            columns = 0
            table_list_of_list = None
            try:
                intent_pk = request.GET['intent_pk']
                intent_obj = Intent.objects.filter(
                    pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False).distinct()[0]
                intent_name = intent_obj.name
                
                root_tree_obj = Intent.objects.filter(
                    pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False)[0].tree
                tree_structure = get_child_tree_objs(root_tree_obj, [], selected_language_obj)

                # is_livechat_enabled = intent_obj.is_livechat_enabled
                table_list_of_list = intent_obj.tree.response.table
                if table_list_of_list != '{"items": ""}':
                    rows = len(json.loads(table_list_of_list)["items"])
                    columns = len(json.loads(table_list_of_list)["items"][0])
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()

                logger.error("EditIntentConsole ! %s %s",
                               str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

            answer_pk = None
            if intent_obj != None:
                selected_bot_obj = intent_obj.bots.all()[0]
                answer_pk = intent_obj.tree.response.pk

                channel_list = list(Channel.objects.filter(is_easychat_channel=True).values("name", "icon"))

                recommendation_list = []
                selected_channel_list = []

                selected_bot_obj_list = []
                try:
                    recommendation_list = json.loads(
                        intent_obj.tree.response.recommendations)["items"]
                    selected_channel_list = list(
                        intent_obj.channels.values_list("name", flat=True))
                    selected_bot_obj_list = intent_obj.bots.all()

                except Exception as e:  # noqa: F841
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("EditIntentConsole ! %s %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

                intent_objs_list = Intent.objects.filter(bots__in=selected_bot_obj_list, is_deleted=False, is_form_assist_enabled=False, is_hidden=False).distinct()

                modified_intent_list = []
                is_quick_recommendation_present = False
                for intent_pk in recommendation_list:
                    intent = Intent.objects.filter(pk=int(intent_pk), is_hidden=False, is_deleted=False, is_small_talk=False).first()
                    
                    if intent:
                        is_quick_recommendation_present = True
                        icon = None
                        if intent.build_in_intent_icon:
                            icon = intent.build_in_intent_icon.icon
                        elif intent.intent_icon:
                            icon = icon = "<img src='" + intent.intent_icon + "'>"

                        modified_intent_list.append({
                            "is_selected": True,
                            "intent_name": intent.name,
                            "intent_pk": intent_pk,
                            "icon": icon
                        })

                intent_dict = {}
                intent_name_list = []
                for int_obj in intent_objs_list:
                    if int_obj == intent_obj:
                        continue
                    intent_dict[int_obj.name.lower()] = int_obj
                    intent_name_list.append(int_obj.name.lower())

                    if not int_obj.is_small_talk and str(int_obj.pk) not in recommendation_list:

                        icon = None
                        if int_obj.build_in_intent_icon:
                            icon = int_obj.build_in_intent_icon.icon
                        elif int_obj.intent_icon:
                            icon = "<img src='" + int_obj.intent_icon + "'>"

                        modified_intent_list.append({
                            "is_selected": False,
                            "intent_name": int_obj.name,
                            "intent_pk": int_obj.pk,
                            "icon": icon
                        })

                recommeded_intents = get_close_matches(intent_name.lower(), intent_name_list, cutoff=0.3)[:3]
                recommeded_intents_dict_list = []
                for recommeded_intent in recommeded_intents:
                    int_obj = intent_dict[recommeded_intent]
                    if not int_obj.is_small_talk:
                        recommeded_intents_dict_list.append({
                            "pk": str(int_obj.pk),
                            "name": recommeded_intent
                        })

                selected_file_type = []
                modes = json.loads(intent_obj.tree.response.modes)
                modes_param = json.loads(intent_obj.tree.response.modes_param)

                if "choosen_file_type" in modes_param:
                    selected_file_type = modes_param["choosen_file_type"]
                else:
                    selected_file_type = "none"

                is_save_attachment_required = False
                if "is_attachment_required" in modes and str(modes["is_attachment_required"]) == "true":
                    is_attachment_required = True
                    if "is_save_attachment_required" in modes and str(modes["is_save_attachment_required"]) == "true":
                        is_save_attachment_required = True
                    else:
                        is_save_attachment_required = False
                else:
                    is_attachment_required = False

                is_date_picker_allowed = False
                is_single_date_picker_allowed = False
                is_multi_date_picker_allowed = False
                if "is_datepicker" in modes and str(modes["is_datepicker"]) == "true":
                    is_date_picker_allowed = True
                    if "is_single_datepicker" in modes and str(modes["is_single_datepicker"]) == "true":
                        is_single_date_picker_allowed = True
                        is_multi_date_picker_allowed = False
                    elif "is_multi_datepicker" in modes and str(modes["is_multi_datepicker"]) == "true":
                        is_single_date_picker_allowed = False
                        is_multi_date_picker_allowed = True
                else:
                    is_date_picker_allowed = False
                    is_single_date_picker_allowed = False
                    is_multi_date_picker_allowed = False
                is_time_picker_allowed = False
                is_single_time_picker_allowed = False
                is_multi_time_picker_allowed = False
                if "is_timepicker" in modes and str(modes["is_timepicker"]) == "true":
                    is_time_picker_allowed = True
                    if "is_single_timepicker" in modes and str(modes["is_single_timepicker"]) == "true":
                        is_single_time_picker_allowed = True
                        is_multi_time_picker_allowed = False
                    elif "is_multi_timepicker" in modes and str(modes["is_multi_timepicker"]) == "true":
                        is_single_time_picker_allowed = False
                        is_multi_time_picker_allowed = True
                else:
                    is_time_picker_allowed = False
                    is_single_time_picker_allowed = False
                    is_multi_time_picker_allowed = False

                is_calender_picker_allowed = False
                is_single_calender_date_picker_allowed = False
                is_multi_calender_date_picker_allowed = False
                is_single_calender_time_picker_allowed = False
                is_multi_calender_time_picker_allowed = False
                if "is_calender" in modes and str(modes["is_calender"]) == "true":
                    is_calender_picker_allowed = True
                    if "is_single_datepicker" in modes and str(modes["is_single_datepicker"]) == "true":
                        is_single_calender_date_picker_allowed = True
                        is_multi_calender_date_picker_allowed = False
                    if "is_multi_datepicker" in modes and str(modes["is_multi_datepicker"]) == "true":
                        is_single_calender_date_picker_allowed = False
                        is_multi_calender_date_picker_allowed = True
                    if "is_single_timepicker" in modes and str(modes["is_single_timepicker"]) == "true":
                        is_single_calender_time_picker_allowed = True
                        is_multi_calender_time_picker_allowed = False
                    if "is_multi_timepicker" in modes and str(modes["is_multi_timepicker"]) == "true":
                        is_single_calender_time_picker_allowed = False
                        is_multi_calender_time_picker_allowed = True

                else:
                    is_calender_picker_allowed = False
                    is_single_calender_date_picker_allowed = False
                    is_multi_calender_date_picker_allowed = False
                    is_single_calender_time_picker_allowed = False
                    is_multi_calender_time_picker_allowed = False

                is_range_slider_required = False
                minimum_range = 0
                maximum_range = 0
                range_slider_type = ""
                if "is_range_slider" in modes and str(modes["is_range_slider"]) == "true":
                    is_range_slider_required = True
                    modes_value = modes_param["range_slider_list"]
                    minimum_range = modes_value[0]["min"]
                    maximum_range = modes_value[0]["max"]
                    range_slider_type = modes_value[0]["range_type"]
                else:
                    is_range_slider_required = False

                is_radio_button_allowed = False
                radio_button_choices_list = []
                if "is_radio_button" in modes and str(modes["is_radio_button"]) == "true":
                    is_radio_button_allowed = True
                    radio_button_choices_list = modes_param[
                        "radio_button_choices"]
                else:
                    is_radio_button_allowed = False
                    radio_button_choices_list = []

                is_check_box_allowed = False
                check_box_choices_list = []
                if "is_check_box" in modes and str(modes["is_check_box"]) == "true":
                    is_check_box_allowed = True
                    check_box_choices_list = modes_param["check_box_choices"]
                else:
                    is_check_box_allowed = False
                    check_box_choices_list = []

                is_drop_down_allowed = False
                drop_down_choices_list = []
                if "is_drop_down" in modes and str(modes["is_drop_down"]) == "true":
                    is_drop_down_allowed = True
                    drop_down_choices_list = modes_param["drop_down_choices"]
                else:
                    is_drop_down_allowed = False
                    drop_down_choices_list = []

                is_video_recorder_allowed = False
                is_save_video_attachment = False
                if "is_video_recorder_allowed" in modes and str(modes["is_video_recorder_allowed"]) == "true":
                    is_video_recorder_allowed = True
                    if "is_save_video_attachment" in modes and str(modes["is_save_video_attachment"]) == "true":
                        is_save_video_attachment = True
                    else:
                        is_save_video_attachment = False
                else:
                    is_video_recorder_allowed = False

                is_phone_widget_enabled = False
                country_code = "in"
                if "is_phone_widget_enabled" in modes and str(modes["is_phone_widget_enabled"]) == "true":
                    is_phone_widget_enabled = True
                    country_code = modes_param["country_code"]
                else:
                    is_phone_widget_enabled = False
                    country_code = "in"

                is_create_form_allowed = False
                form_fields_list = []
                form_name = ""
                if "is_create_form_allowed" in modes and str(modes["is_create_form_allowed"]) == "true":
                    is_create_form_allowed = True
                    form_fields_list = json.loads(
                        modes_param["form_fields_list"])
                    form_name = modes_param["form_name"]

                if "is_recommendation_menu" in modes and str(modes["is_recommendation_menu"]) == "true":
                    is_recommendation_menu = True
                else:
                    is_recommendation_menu = False
                
                if "is_catalogue_added" in modes and str(modes["is_catalogue_added"]) == "true":
                    is_catalogue_added = True
                else:
                    is_catalogue_added = False

                is_catalogue_purchased = intent_obj.tree.is_catalogue_purchased

                try:
                    new_all_file_type = get_all_file_type()

                    all_file_type = []
                    for file_type in new_all_file_type:
                        if str(file_type["file_type"]) in selected_file_type:
                            all_file_type.append({
                                "is_selected": True,
                                "file_type": file_type["file_type"]
                            })
                        else:
                            all_file_type.append({
                                "is_selected": False,
                                "file_type": file_type["file_type"]
                            })

                except Exception as e:  # noqa: F841
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("EditIntentConsole %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

                modified_channel_list = []
                for channel in channel_list:
                    if str(channel["name"]) in selected_channel_list:
                        modified_channel_list.append({
                            "is_selected": True,
                            "channel_name": channel["name"],
                            "icon": channel["icon"]
                        })
                    else:
                        modified_channel_list.append({
                            "is_selected": False,
                            "channel_name": channel["name"],
                            "icon": channel["icon"]
                        })

                # languages_supported = selected_bot_obj.languages_supported.all()

                # language_supported = []

                # for language in languages_supported:
                #     language_supported.append(language.lang)

                hindi_supported = True
                # if 'en' in language_supported:
                #     hindi_supported = False

                multilingual_intent_name = ""

                # if hindi_supported:
                #     multilingual_intent_name = intent_obj.multilingual_name

                validators = ProcessorValidator.objects.filter(
                    bot=selected_bot_obj)
                post_processor_variable = ""
                selected_validator_obj = None
                if intent_obj.tree.post_processor:
                    processor_obj = intent_obj.tree.post_processor
                    post_processor_variable = processor_obj.post_processor_direct_value
                    if len(ProcessorValidator.objects.filter(processor=processor_obj)) != 0:
                        selected_validator_obj = ProcessorValidator.objects.filter(
                            processor=processor_obj)[0]
                if table_list_of_list == None:
                    table_list_of_list = json.dumps({"items": []})

                bot_form_assist_enabled = False
                if selected_bot_obj != None:
                    bot_form_assist_enabled = selected_bot_obj.is_form_assist_enabled

                is_go_back_enabled = intent_obj.tree.is_go_back_enabled
                selected_category_obj = intent_obj.category
                category_objs = []

                if intent_obj.tree.explanation == None:
                    explanation = ""
                else:
                    explanation = intent_obj.tree.explanation.explanation

                if selected_bot_obj != None:
                    category_objs = Category.objects.filter(
                        bot=selected_bot_obj)

                radio_button_choices_value = ""
                for value in radio_button_choices_list:
                    radio_button_choices_value += str(value) + "_"

                check_box_choices_value = ""
                for value in check_box_choices_list:
                    check_box_choices_value += str(value) + "_"

                drop_down_choices_value = ""
                for value in drop_down_choices_list:
                    drop_down_choices_value += str(value) + "_"
                is_automatic_recursion_enabled = intent_obj.tree.is_automatic_recursion_enabled

                pipe_processor_tree_name = ""
                api_tree_name = ""
                post_processor_tree_name = ""

                if intent_obj.tree.pipe_processor:
                    pipe_processor_tree_name = ": " + intent_obj.tree.pipe_processor.name
                if intent_obj.tree.api_tree:
                    api_tree_name = ": " + intent_obj.tree.api_tree.name
                if intent_obj.tree.post_processor:
                    post_processor_tree_name = ": " + intent_obj.tree.post_processor.name

                intent_children_list = []

                intent_children = intent_obj.tree.children.all()

                for children in intent_children:
                    intent_children_list.append(children.name)
                child_choices_list = []

                child_choices = intent_obj.tree.response.choices.all()

                for choice in child_choices:
                    child_choices_list.append(choice.value)
                if child_choices_list != [] and intent_children_list != child_choices_list:
                    choices_order_changed = True

                else:
                    choices_order_changed = False

                flow_analytics_variable = intent_obj.tree.flow_analytics_variable
                required_analytics_variable = False
                if flow_analytics_variable != "":
                    required_analytics_variable = True

                is_custom_order_selected = intent_obj.is_custom_order_selected
                order_of_response = intent_obj.order_of_response

                is_last_tree = intent_obj.tree.is_last_tree
                is_exit_tree = intent_obj.tree.is_exit_tree
                is_transfer_tree = intent_obj.tree.enable_transfer_agent

                supported_language = get_supported_languages(
                    selected_bot_obj, BotChannel)
                activity_update = json.loads(
                    intent_obj.tree.response.activity_update)
                eng_lang_obj = None
                if Language.objects.filter(lang="en"):
                    eng_lang_obj = Language.objects.get(lang="en")
                need_to_show_auto_fix_popup = need_to_show_auto_fix_popup_for_intents(
                    intent_obj.tree.response, activity_update, selected_language, eng_lang_obj, LanguageTuningBotResponseTable)

                bot_info_obj = BotInfo.objects.get(bot=selected_bot_obj)

                is_intent_level_feedback_required = False
                if selected_bot_obj.is_feedback_required and intent_obj.is_feedback_required:
                    is_intent_level_feedback_required = True

                built_in_intent_icons = BuiltInIntentIcon.objects.all().order_by("pk")

                selected_tts_provider = get_selected_tts_provider_name(
                    selected_bot_obj, BotChannel)

                short_name_enabled = False
                for channel in modified_channel_list:
                    if channel["channel_name"] == 'GoogleBusinessMessages' and channel["is_selected"]:
                        short_name_enabled = True

                is_whatsapp_channel_selected = False
                if "WhatsApp" in selected_channel_list:
                    is_whatsapp_channel_selected = True

                welcome_message = []
                web_channel_obj = BotChannel.objects.filter(bot=selected_bot_obj, channel__name="Web").first()
                if web_channel_obj:
                    welcome_message = web_channel_obj.welcome_message.split("$$$")

                if request.COOKIES.get("edit_intent_ui", "new") == "old":
                    tag_mapper_objs = get_tag_mapper_list_for_given_user(request)
                    user_objs = User.objects.all()
                    authentication_objs = get_authentication_objs(
                        [selected_bot_obj])
                    intent_tuning_obj = check_and_update_tunning_object(intent_obj, selected_language_obj, LanguageTuningIntentTable,
                                                                        LanguageTuningTreeTable, LanguageTuningBotResponseTable, LanguageTuningChoicesTable, EasyChatTranslationCache)
                    
                    whatsapp_channel_obj = Channel.objects.filter(name="WhatsApp").first()

                    selected_child_trees = []
                    selected_main_intents = []

                    whatsapp_menu_sections = WhatsAppMenuSection.objects.filter(tree=intent_obj.tree)

                    for whatsapp_menu_section in whatsapp_menu_sections:
                        if whatsapp_menu_section.child_trees:
                            selected_child_trees += json.loads(whatsapp_menu_section.child_trees)
                        if whatsapp_menu_section.main_intents:
                            selected_main_intents += json.loads(whatsapp_menu_section.main_intents)

                    unselected_child_trees = intent_obj.tree.children.filter(is_deleted=False).filter(~Q(pk__in=selected_child_trees))
                    if intent_obj.tree.children.filter(is_deleted=False).count() == 1 or not intent_obj.tree.is_child_tree_visible:
                        unselected_child_trees = []
                    unselected_main_intents = Intent.objects.filter(bots=selected_bot_obj, channels=whatsapp_channel_obj, is_deleted=False, is_hidden=False, is_small_talk=False).filter(~Q(pk__in=selected_main_intents))

                    whatsapp_menu_section_objs_list = WhatsAppMenuSection.objects.filter(tree=intent_obj.tree).order_by("pk")
                    whatsapp_menu_section_objs = []
                    for whatsapp_menu_section_obj in whatsapp_menu_section_objs_list:
                        whatsapp_menu_section_data = {}
                        whatsapp_menu_section_data["pk"] = whatsapp_menu_section_obj.pk
                        whatsapp_menu_section_data["title"] = whatsapp_menu_section_obj.title
                        whatsapp_menu_section_data["child_tree_details"] = whatsapp_menu_section_obj.get_child_tree_details()
                        whatsapp_menu_section_data["main_intent_details"] = whatsapp_menu_section_obj.get_main_intent_details()
                        whatsapp_menu_section_objs.append(whatsapp_menu_section_data)

                    whatsapp_quick_recommendations_allowed = 10

                    if intent_obj.tree.is_child_tree_visible and intent_obj.tree.children.filter(is_deleted=False).count() > 1:
                        whatsapp_quick_recommendations_allowed = 10 - intent_obj.tree.children.filter(is_deleted=False).count()
                        if whatsapp_quick_recommendations_allowed < 0:
                            whatsapp_quick_recommendations_allowed = 0

                    return render(request, 'EasyChatApp/platform/edit_intent.html', {
                        'explanation': explanation,
                        'is_new_intent': False,
                        'config': config,
                        'selected_bot_obj': selected_bot_obj,
                        'intent_name_list': modified_intent_list,
                        'is_quick_recommendation_present': is_quick_recommendation_present,
                        # "is_livechat_enabled": is_livechat_enabled,
                        'channel_list': modified_channel_list,
                        'short_name_enabled': short_name_enabled,
                        'short_name_value': str(intent_obj.tree.short_name),
                        "intent_name": str(intent_obj.name),
                        "is_category_response_allowed": intent_obj.is_category_response_allowed,
                        "campaign_link": str(intent_obj.campaign_link),
                        "multilingual_intent_name": str(multilingual_intent_name),
                        "recommeded_intents_dict_list": recommeded_intents_dict_list,
                        "is_feedback_required": intent_obj.is_feedback_required,
                        "is_intent_level_feedback_required": is_intent_level_feedback_required,
                        "is_attachment_required": is_attachment_required,
                        "all_file_type": all_file_type,
                        "is_authentication_required": intent_obj.is_authentication_required,
                        "is_part_of_suggestion_list": intent_obj.is_part_of_suggestion_list,
                        "is_child_tree_visible": intent_obj.tree.is_child_tree_visible,
                        "tag_mapper_objs": tag_mapper_objs,
                        "hindi_supported": hindi_supported,
                        "user_objs": user_objs,
                        "authentication_objs": authentication_objs,
                        "selected_user_authentication": intent_obj.auth_type,
                        "validators": validators,
                        "selected_validator_obj": selected_validator_obj,
                        "table_list_of_list": table_list_of_list,
                        "rows": rows,
                        "columns": columns,
                        "bot_form_assist_enabled": bot_form_assist_enabled,
                        "category_objs": category_objs,
                        "selected_category_obj": selected_category_obj,
                        "is_small_talk": intent_obj.is_small_talk,
                        "tree_pk": intent_obj.tree.pk,
                        "is_save_attachment_required": is_save_attachment_required,
                        "is_date_picker_allowed": is_date_picker_allowed,
                        "is_time_picker_allowed": is_time_picker_allowed,
                        "is_multi_date_picker_allowed": is_multi_date_picker_allowed,
                        "is_single_date_picker_allowed": is_single_date_picker_allowed,
                        "is_multi_time_picker_allowed": is_multi_time_picker_allowed,
                        "is_single_time_picker_allowed": is_single_time_picker_allowed,
                        "is_calender_picker_allowed": is_calender_picker_allowed,
                        "is_single_calender_date_picker_allowed": is_single_calender_date_picker_allowed,
                        "is_multi_calender_date_picker_allowed": is_multi_calender_date_picker_allowed,
                        "is_single_calender_time_picker_allowed": is_single_calender_time_picker_allowed,
                        "is_multi_calender_time_picker_allowed": is_multi_calender_time_picker_allowed,
                        "is_range_slider_required": is_range_slider_required,
                        "minimum_range": minimum_range,
                        "maximum_range": maximum_range,
                        "range_slider_type": range_slider_type,
                        "is_radio_button_allowed": is_radio_button_allowed,
                        "radio_button_choices_list": radio_button_choices_value,
                        "post_processor_variable": post_processor_variable,
                        "is_check_box_allowed": is_check_box_allowed,
                        "check_box_choices_list": check_box_choices_value,
                        "is_drop_down_allowed": is_drop_down_allowed,
                        "drop_down_choices_list": drop_down_choices_value,
                        "is_save_video_attachment": is_save_video_attachment,
                        "is_video_recorder_allowed": is_video_recorder_allowed,
                        "is_phone_widget_enabled": is_phone_widget_enabled,
                        "country_code": country_code,
                        "is_create_form_allowed": is_create_form_allowed,
                        "form_name": form_name,
                        "form_fields_list": form_fields_list,
                        "is_go_back_enabled": is_go_back_enabled,
                        "show_go_back_checkbox": False,
                        "is_automatic_recursion_enabled": is_automatic_recursion_enabled,
                        "is_recommendation_menu": is_recommendation_menu,
                        "is_catalogue_added": is_catalogue_added,
                        "is_catalogue_purchased": is_catalogue_purchased,
                        "post_processor_tree_name": post_processor_tree_name,
                        "api_tree_name": api_tree_name,
                        "pipe_processor_tree_name": pipe_processor_tree_name,
                        "intent_children_list": intent_children_list,
                        "choices_order_changed": choices_order_changed,
                        "child_choices_list": child_choices_list,
                        "flow_analytics_variable": flow_analytics_variable,
                        "required_analytics_variable": required_analytics_variable,
                        "order_of_response": order_of_response,
                        "is_custom_order_selected": is_custom_order_selected,
                        "is_last_tree": is_last_tree,
                        "is_exit_tree": is_exit_tree,
                        "is_transfer_tree": is_transfer_tree,
                        "intent_tuning_obj": intent_tuning_obj,
                        "selected_language": selected_language,
                        "supported_language": supported_language,
                        "need_to_show_auto_fix_popup": need_to_show_auto_fix_popup,
                        "necessary_keywords": str(intent_obj.necessary_keywords),
                        "restricted_keywords": str(intent_obj.restricted_keywords),
                        "intent_threshold": str(intent_obj.threshold),
                        "whatsapp_list_message_header": intent_obj.tree.response.whatsapp_list_message_header,
                        "bot_info_obj": bot_info_obj,
                        "built_in_intent_icons": built_in_intent_icons,
                        "intent_obj": intent_obj,
                        "selected_tts_provider": selected_tts_provider,
                        "allow_barge": intent_obj.tree.check_barge_in_enablement(),
                        "is_faq_intent": intent_obj.is_faq_intent,
                        "disposition_code": intent_obj.tree.disposition_code,
                        "is_whatsapp_channel_selected": is_whatsapp_channel_selected,
                        "unselected_child_trees": unselected_child_trees,
                        "unselected_main_intents": unselected_main_intents,
                        "whatsapp_menu_section_objs": whatsapp_menu_section_objs,
                        "whatsapp_quick_recommendations_allowed": whatsapp_quick_recommendations_allowed,
                        "show_whatsapp_menu_section_feature": True,
                        # "livechat_config": livechat_config,
                    })

                return render(request, 'EasyChatApp/platform/edit_intent_revised.html', {
                    'explanation': explanation,
                    'is_new_intent': False,
                    'config': config,
                    'selected_bot_obj': selected_bot_obj,
                    'intent_name_list': modified_intent_list,
                    'intent_name_list_updated': json.dumps(modified_intent_list),
                    'is_quick_recommendation_present': is_quick_recommendation_present,
                    # "is_livechat_enabled": is_livechat_enabled,
                    'channel_list': modified_channel_list,
                    'short_name_enabled': short_name_enabled,
                    'short_name_value': str(intent_obj.tree.short_name),
                    "intent_name": str(intent_obj.name),
                    "is_category_response_allowed": intent_obj.is_category_response_allowed,
                    "campaign_link": str(intent_obj.campaign_link),
                    "multilingual_intent_name": str(multilingual_intent_name),
                    "recommeded_intents_dict_list": recommeded_intents_dict_list,
                    "is_feedback_required": intent_obj.is_feedback_required,
                    "is_intent_level_feedback_required": is_intent_level_feedback_required,
                    "is_attachment_required": is_attachment_required,
                    "all_file_type": all_file_type,
                    "is_authentication_required": intent_obj.is_authentication_required,
                    "is_part_of_suggestion_list": intent_obj.is_part_of_suggestion_list,
                    "is_child_tree_visible": intent_obj.tree.is_child_tree_visible,
                    "hindi_supported": hindi_supported,
                    "selected_user_authentication": intent_obj.auth_type,
                    "validators": validators,
                    "selected_validator_obj": selected_validator_obj,
                    "rows": rows,
                    "columns": columns,
                    "bot_form_assist_enabled": bot_form_assist_enabled,
                    "category_objs": category_objs,
                    "selected_category_obj": selected_category_obj,
                    "is_small_talk": intent_obj.is_small_talk,
                    "tree_pk": intent_obj.tree.pk,
                    "is_save_attachment_required": is_save_attachment_required,
                    "is_date_picker_allowed": is_date_picker_allowed,
                    "is_time_picker_allowed": is_time_picker_allowed,
                    "is_multi_date_picker_allowed": is_multi_date_picker_allowed,
                    "is_single_date_picker_allowed": is_single_date_picker_allowed,
                    "is_multi_time_picker_allowed": is_multi_time_picker_allowed,
                    "is_single_time_picker_allowed": is_single_time_picker_allowed,
                    "is_calender_picker_allowed": is_calender_picker_allowed,
                    "is_single_calender_date_picker_allowed": is_single_calender_date_picker_allowed,
                    "is_multi_calender_date_picker_allowed": is_multi_calender_date_picker_allowed,
                    "is_single_calender_time_picker_allowed": is_single_calender_time_picker_allowed,
                    "is_multi_calender_time_picker_allowed": is_multi_calender_time_picker_allowed,
                    "is_range_slider_required": is_range_slider_required,
                    "minimum_range": minimum_range,
                    "maximum_range": maximum_range,
                    "range_slider_type": range_slider_type,
                    "is_radio_button_allowed": is_radio_button_allowed,
                    "post_processor_variable": post_processor_variable,
                    "is_check_box_allowed": is_check_box_allowed,
                    "is_drop_down_allowed": is_drop_down_allowed,
                    "is_save_video_attachment": is_save_video_attachment,
                    "is_video_recorder_allowed": is_video_recorder_allowed,
                    "is_phone_widget_enabled": is_phone_widget_enabled,
                    "country_code": country_code,
                    "is_create_form_allowed": is_create_form_allowed,
                    "form_name": form_name,
                    "form_fields_list": form_fields_list,
                    "is_go_back_enabled": is_go_back_enabled,
                    "show_go_back_checkbox": False,
                    "is_automatic_recursion_enabled": is_automatic_recursion_enabled,
                    "is_recommendation_menu": is_recommendation_menu,
                    "is_catalogue_added": is_catalogue_added,
                    "post_processor_tree_name": post_processor_tree_name,
                    "api_tree_name": api_tree_name,
                    "pipe_processor_tree_name": pipe_processor_tree_name,
                    "choices_order_changed": choices_order_changed,
                    "child_choices_list": child_choices_list,
                    "flow_analytics_variable": flow_analytics_variable,
                    "required_analytics_variable": required_analytics_variable,
                    "order_of_response": order_of_response,
                    "is_custom_order_selected": is_custom_order_selected,
                    "is_last_tree": is_last_tree,
                    "is_exit_tree": is_exit_tree,
                    "is_transfer_tree": is_transfer_tree,
                    "selected_language": selected_language,
                    "supported_language": supported_language,
                    "need_to_show_auto_fix_popup": need_to_show_auto_fix_popup,
                    "necessary_keywords": str(intent_obj.necessary_keywords),
                    "restricted_keywords": str(intent_obj.restricted_keywords),
                    "intent_threshold": str(intent_obj.threshold),
                    "whatsapp_list_message_header": intent_obj.tree.response.whatsapp_list_message_header,
                    "bot_info_obj": bot_info_obj,
                    "built_in_intent_icons": built_in_intent_icons,
                    "intent_obj": intent_obj,
                    "selected_tts_provider": selected_tts_provider,
                    "allow_barge": intent_obj.tree.check_barge_in_enablement(),
                    "is_faq_intent": intent_obj.is_faq_intent,
                    "disposition_code": intent_obj.tree.disposition_code,
                    "is_whatsapp_channel_selected": is_whatsapp_channel_selected,
                    "show_whatsapp_menu_section_feature": True,
                    "tree_structure": json.dumps(tree_structure),
                    "response_pk": answer_pk,
                    "language_direction": selected_language_obj.language_script_type,
                    "INTENT_TREE_NAME_CHARACTER_LIMIT": INTENT_TREE_NAME_CHARACTER_LIMIT,
                    "welcome_message": welcome_message,
                    # "livechat_config": livechat_config,
                })
            else:
                # return HttpResponseNotFound("<h1>No Page found</h1>")
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EditIntentConsole ! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        # return HttpResponseNotFound(INVALID_REQUEST)
        return render(request, 'EasyChatApp/error_500.html')


def EditIntentMultilingualConsole(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Intent Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            config = Config.objects.all()[0]

            selected_bot_obj = None

            selected_language = "en"

            if "selected_language" in request.GET:
                selected_language = request.GET["selected_language"]

            if selected_language == "en":
                return HttpResponseRedirect("/chat/edit-intent/?intent_pk=" + str(request.GET['intent_pk']) + "&selected_language=en")

            selected_language_obj = Language.objects.get(
                lang=selected_language)

            user_obj = User.objects.get(username=str(request.user.username))
            bot_objs = get_uat_bots(user_obj)

            intent_obj = None
            rows = 0
            columns = 0
            table_list_of_list = None
            try:
                intent_pk = request.GET['intent_pk']
                # intent_name = Intent.objects.get(
                #     pk=int(intent_pk), is_hidden=False).name
                intent_obj = Intent.objects.filter(
                    pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False).distinct()[0]

                intent_tuning_obj = check_and_update_tunning_object(intent_obj, selected_language_obj, LanguageTuningIntentTable,
                                                                    LanguageTuningTreeTable, LanguageTuningBotResponseTable, LanguageTuningChoicesTable, EasyChatTranslationCache)
                # is_livechat_enabled = intent_obj.is_livechat_enabled
                table_list_of_list = intent_tuning_obj.tree.response.table
                if table_list_of_list != '{"items": ""}':
                    rows = len(json.loads(table_list_of_list)["items"])
                    columns = len(json.loads(table_list_of_list)["items"][0])
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("EditIntentMultilingualConsole ! %s %s", str(e), str(exc_tb.tb_lineno), extra={
                               'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                pass

            selected_bot_obj = intent_obj.bots.all()[0]
            need_to_show_auto_fix_popup = False
            if intent_obj != None:
                supported_language = get_supported_languages(
                    selected_bot_obj, BotChannel)
                if selected_language_obj not in supported_language:
                    selected_language = "en"
                selected_tts_provider = get_selected_tts_provider_name(
                    selected_bot_obj, BotChannel)
                return render(request, 'EasyChatApp/platform/edit_intent.html', {
                    'config': config,
                    'selected_bot_obj': selected_bot_obj,
                    "intent_name": str(intent_obj.name),
                    "tree_pk": intent_obj.tree.pk,
                    "intent_tuning_obj": intent_tuning_obj,
                    "selected_language": selected_language,
                    "supported_language": supported_language,
                    "table_list_of_list": table_list_of_list,
                    "rows": rows,
                    "columns": columns,
                    "need_to_show_auto_fix_popup": need_to_show_auto_fix_popup,
                    "language_script_type": selected_language_obj.language_script_type,
                    "selected_tts_provider": selected_tts_provider,
                })
            else:
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EditIntentMultilingualConsole ! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return render(request, 'EasyChatApp/error_500.html')


def EasyChatAPIAnalytics(request):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "API Analytics Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            user_obj = User.objects.get(username=request.user.username)
            bot_objs = get_uat_bots(user_obj)
            get_all_file_type = [{"key": "last_week", "value": "Last Week"}, {"key": "last_month", "value": "Last Month"}, {
                "key": "since_go_live", "value": "Since Go Live Date"}, {"key": "custom_date", "value": "Custom Date"}, {"key": "custom_timestamp", "value": "Custom Timestamp"}]
            selected_bot_obj = None
            if "bot_pk" in request.GET:
                bot_pk = request.GET["bot_pk"]
                if not check_access_for_user(request.user, bot_pk, "API Analytics Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)
            api_analytics_objs = []
            if selected_bot_obj != None and selected_bot_obj in bot_objs:

                selected_api_name = request.GET.get('selected_api_name')
                selected_api_status = request.GET.get('selected_api_status')
                datetime_start = (datetime.datetime.today() -
                                  datetime.timedelta(7)).date()
                datetime_end = datetime.datetime.today().date()
                last_month_start_datetime = (
                    datetime.datetime.today() - datetime.timedelta(30)).date()
                default_analytics_start_datetime = (
                    datetime.datetime.today() - datetime.timedelta(7)).date()

                default_analytics_end_datetime = datetime.datetime.today().date()

                go_live_date = selected_bot_obj.go_live_date
                date_format = "%Y-%m-%d"
                start_date = default_analytics_start_datetime
                start_time = ""
                end_time = ""
                selected_user_id = ""
                if "user_id" in request.GET:
                    selected_user_id = request.GET["user_id"]
                try:
                    filter_type = request.GET.get('filter_type')
                    if filter_type == "custom_timestamp":
                        start_date = request.GET.get('start_date')
                        start_time = request.GET["start_time"]
                        end_time = request.GET["end_time"]
                        start_timestamp = start_date + " " + start_time
                        start_timestamp = datetime.datetime.strptime(
                            start_timestamp, "%Y-%m-%d %H:%M")

                        end_timestamp = start_date + " " + end_time
                        end_timestamp = datetime.datetime.strptime(
                            end_timestamp, "%Y-%m-%d %H:%M")

                        api_analytics_objs = apply_custom_filter_api_analytics(
                            selected_bot_obj, selected_api_name, selected_api_status, start_timestamp, end_timestamp, selected_user_id, APIElapsedTime)
                    else:
                        try:
                            start_date = request.GET.get('start_date')
                            end_date = request.GET.get('end_date')
                            filter_type = request.GET.get('filter_type')
                            datetime_start = datetime.datetime.strptime(
                                start_date, date_format)
                            datetime_end = datetime.datetime.strptime(
                                end_date, date_format)
                            api_analytics_objs = apply_filter_api_analytics(
                                selected_bot_obj, selected_api_name, selected_api_status, datetime_start, datetime_end, selected_user_id, APIElapsedTime)
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                                e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                            api_analytics_objs = apply_filter_api_analytics(
                                selected_bot_obj, selected_api_name, selected_api_status, datetime_start, datetime_end, selected_user_id, APIElapsedTime)
                            datetime_start = datetime_start.strftime(
                                date_format)
                            datetime_end = datetime_end.strftime(date_format)
                            filter_type = "last_week"
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                    api_analytics_objs = apply_filter_api_analytics(
                        selected_bot_obj, selected_api_name, selected_api_status, datetime_start, datetime_end, selected_user_id, APIElapsedTime)
                    datetime_start = datetime_start.strftime(date_format)
                    datetime_end = datetime_end.strftime(date_format)
                    filter_type = "last_week"

                paginator = Paginator(api_analytics_objs, 100)
                page = request.GET.get('page')
                # user_objs = APIElapsedTime.objects.all()
                # user_ids = []
                # for user in user_objs:
                #     try:
                #         user_ids.append(user.user.user_id)
                #     except Exception:
                #         pass
                try:
                    api_analytics_objs = paginator.page(page)
                except PageNotAnInteger:
                    api_analytics_objs = paginator.page(1)
                except EmptyPage:
                    api_analytics_objs = paginator.page(paginator.num_pages)
                if selected_bot_obj.static_analytics:
                    display_date = []
                    for index in range(5):
                        tz = timezone.now()
                        timezone.now() - datetime.timedelta(minutes=random.randint(120, 1440))
                        if tz.hour < 12:
                            flag = "AM"
                            hour1 = tz.hour
                        elif tz.hour == 12:
                            hour1 = tz.hour
                            flag = "PM"
                        else:
                            hour1 = tz.hour - 12
                            flag = "PM"

                        if hour1 <= 9:
                            hour2 = "0" + str(hour1)
                        else:
                            hour2 = str(hour1)

                        if tz.minute <= 9:
                            minute1 = "0" + str(tz.minute)
                        else:
                            minute1 = str(tz.minute)

                        time1 = str(hour2) + ":" + str(minute1) + " " + flag

                        display_date.append(
                            time1 + ", " + tz.strftime('%d-%b-%Y'))

                    return render(request, "EasyChatApp/platform/static_api_analytics.html", {
                        "api_analytics_objs": api_analytics_objs,
                        "selected_bot_obj": selected_bot_obj,
                        "start_date": datetime_start,
                        "end_date": datetime_end,
                        "display_date": display_date,
                        "selected_api_name": selected_api_name,
                        "selected_api_status": selected_api_status,
                        "status": "0",
                        "DEFAULT_ANALYTICS_START_DATETIME": default_analytics_start_datetime,
                        "DEFAULT_ANALYTICS_END_DATETIME": default_analytics_end_datetime,
                        "LAST_MONTH_START_DATETIME": last_month_start_datetime,
                        "go_live_date": go_live_date,
                        "filter_type": filter_type,
                        "filter_type_list": get_all_file_type,
                        "TIMESTAMP_DATE": start_date,
                        "TIMESTAMP_START_TIME": start_time,
                        "TIMESTAMP_END_TIME": end_time,
                        # "user_ids": user_ids,
                    })

                return render(request, "EasyChatApp/platform/api_analytics.html", {
                    "api_analytics_objs": api_analytics_objs,
                    "selected_bot_obj": selected_bot_obj,
                    "start_date": datetime_start,
                    "end_date": datetime_end,
                    "selected_api_name": selected_api_name,
                    "selected_api_status": selected_api_status,
                    "status": "0",
                    "DEFAULT_ANALYTICS_START_DATETIME": default_analytics_start_datetime,
                    "DEFAULT_ANALYTICS_END_DATETIME": default_analytics_end_datetime,
                    "LAST_MONTH_START_DATETIME": last_month_start_datetime,
                    "go_live_date": go_live_date,
                    "filter_type": filter_type,
                    "filter_type_list": get_all_file_type,
                    "api_objs_name_list": APIElapsedTime.objects.filter(bot=selected_bot_obj).values_list('api_name', flat=True).distinct(),
                    "TIMESTAMP_DATE": start_date,
                    "TIMESTAMP_START_TIME": start_time,
                    "TIMESTAMP_END_TIME": end_time,
                    # "user_ids": user_ids
                })
            else:
                # return HttpResponseNotFound("<h1>No Page found</h1>")
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EasyChatAPIAnalytics ! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        # return HttpResponseNotFound(INVALID_REQUEST)
        return render(request, 'EasyChatApp/error_500.html')


def EasyChatAPIStatistics(request):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "API Analytics Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            user_obj = User.objects.get(username=request.user.username)
            bot_objs = get_uat_bots(user_obj)
            selected_bot_obj = None
            if "bot_pk" in request.GET:
                bot_pk = request.GET["bot_pk"]
                if not check_access_for_user(request.user, bot_pk, "API Analytics Related"):
                    return HttpResponseNotFound("You do not have access to this page")
                selected_bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False, is_uat=True)
            api_analytics_objs = []
            if selected_bot_obj != None and selected_bot_obj in bot_objs:

                selected_api_name = request.GET.get('selected_api_name')
                datetime_start = (datetime.datetime.today() -
                                  datetime.timedelta(7)).date()
                datetime_end = datetime.datetime.today().date()
                last_month_start_datetime = (
                    datetime.datetime.today() - datetime.timedelta(30)).date()
                default_analytics_start_datetime = (
                    datetime.datetime.today() - datetime.timedelta(7)).date()

                default_analytics_end_datetime = datetime.datetime.today().date()

                go_live_date = selected_bot_obj.go_live_date
                date_format = "%Y-%m-%d"
                selected_user_id = ""
                if "user_id" in request.GET:
                    selected_user_id = request.GET["user_id"]

                try:
                    start_date = request.GET.get('start_date')
                    end_date = request.GET.get('end_date')
                    filter_type = request.GET.get('filter_type')
                    datetime_start = datetime.datetime.strptime(
                        start_date, date_format)
                    datetime_end = datetime.datetime.strptime(
                        end_date, date_format)
                    api_analytics_objs = apply_filter_api_analytics(
                        selected_bot_obj, selected_api_name, "All", datetime_start, datetime_end, selected_user_id, APIElapsedTime)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("datetime_start and datetime_end is not in valid format %s at line no %s", str(
                        e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
                    api_analytics_objs = apply_filter_api_analytics(
                        selected_bot_obj, selected_api_name, "All", datetime_start, datetime_end, selected_user_id, APIElapsedTime)
                    datetime_start = datetime_start.strftime(date_format)
                    datetime_end = datetime_end.strftime(date_format)
                    filter_type = "last_week"
                    pass

                api_objs_list = list(api_analytics_objs.values("api_name").order_by(
                    "api_name").annotate(frequency=Count("api_name")).order_by('-frequency'))
                final_api_obj_list = []
                for item in api_objs_list:
                    api_name = item["api_name"]
                    frequency = item["frequency"]
                    passed_frequecy = api_analytics_objs.filter(
                        api_name=api_name, api_status="Passed").count()
                    failed_frequency = frequency - passed_frequecy
                    final_api_obj_list.append({
                        "api_name": api_name,
                        "frequency": frequency,
                        "success": passed_frequecy,
                        "failed": failed_frequency
                    })

                paginator = Paginator(api_analytics_objs, 100)
                page = request.GET.get('page')

                try:
                    api_analytics_objs = paginator.page(page)
                except PageNotAnInteger:
                    api_analytics_objs = paginator.page(1)
                except EmptyPage:
                    api_analytics_objs = paginator.page(paginator.num_pages)

                if selected_bot_obj.static_analytics:
                    return render(request, "EasyChatApp/platform/static_api_statistics.html", {
                        "api_analytics_objs": final_api_obj_list,
                        "selected_bot_obj": selected_bot_obj,
                        "start_date": datetime_start,
                        "end_date": datetime_end,
                        "selected_api_name": selected_api_name,
                        "status": "1",
                        "DEFAULT_ANALYTICS_START_DATETIME": default_analytics_start_datetime,
                        "DEFAULT_ANALYTICS_END_DATETIME": default_analytics_end_datetime,
                        "LAST_MONTH_START_DATETIME": last_month_start_datetime,
                        "go_live_date": go_live_date,
                        "filter_type": filter_type,
                        "filter_type_list": get_date_filter_type,
                        "api_objs_name_list": APIElapsedTime.objects.filter(bot=selected_bot_obj).values_list('api_name', flat=True).distinct(),
                    })

                return render(request, "EasyChatApp/platform/api_statistics.html", {
                    "api_analytics_objs": final_api_obj_list,
                    "selected_bot_obj": selected_bot_obj,
                    "start_date": datetime_start,
                    "end_date": datetime_end,
                    "selected_api_name": selected_api_name,
                    "status": "1",
                    "DEFAULT_ANALYTICS_START_DATETIME": default_analytics_start_datetime,
                    "DEFAULT_ANALYTICS_END_DATETIME": default_analytics_end_datetime,
                    "LAST_MONTH_START_DATETIME": last_month_start_datetime,
                    "go_live_date": go_live_date,
                    "filter_type": filter_type,
                    "filter_type_list": get_date_filter_type,
                    "api_objs_name_list": APIElapsedTime.objects.filter(bot=selected_bot_obj).values_list('api_name', flat=True).distinct(),
                })
            else:
                # return HttpResponseNotFound("<h1>No Page found</h1>")
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EasyChatAPIStatistics ! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        # return HttpResponseNotFound(INVALID_REQUEST)
        return render(request, 'EasyChatApp/error_500.html')


def DownloadAPIAnalyticsData(request):
    response = {}
    response["status_code"] = 500
    response["status_message"] = ""
    try:
        if request.user.is_authenticated and request.method == "GET":

            api_pk = request.GET["api_pk"]
            request_type = request.GET["type"]

            api_obj = APIElapsedTime.objects.get(pk=int(api_pk))

            filename = 'API-' + str(request_type) + '-packet-' + \
                str(request.user.username) + '.json'
            filepath = 'files/' + filename
            json_file = open(filepath, "w")
            json_file.write(api_obj.get_request_packet())
            json_file.close()
            # path_to_file = settings.MEDIA_ROOT + 'private/' + str(filename)
            response = FileResponse(open(filepath, 'rb'))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="' + \
                filename + '"'
            response['Content-Length'] = os.path.getsize(filepath)
            return response
        else:
            # return HttpResponse(status=404)
            return render(request, 'EasyChatApp/error_404.html')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[NLP]: Error DownloadAPIAnalyticsData %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        # return HttpResponse(status=500)
        return render(request, 'EasyChatApp/error_500.html')


class FetchAllIntentsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:

            data = request.data
            username = request.user.username
            if not isinstance(data, dict):
                data = json.loads(data)

            data = DecryptVariable(data["data"])
            data = json.loads(data)
            bot_filter_list = data["bot_filter_list"]
            channel_filter_list = data["channel_filter_list"]

            user_obj = User.objects.get(username=str(username))
            # bot_objs = Bot.objects.filter(users__in=[user_obj])
            bot_objs = get_uat_bots(user_obj)
            intent_objs = Intent.objects.filter(
                bots__in=bot_objs, is_deleted=False, is_hidden=False).order_by('-pk').distinct()

            if len(bot_filter_list) != 0 or len(channel_filter_list) != 0:

                filter_bot_objs = [Bot.objects.get(pk=int(
                    filter_parameter), is_deleted=False, is_uat=True) for filter_parameter in bot_filter_list]
                filter_channel_objs = [Channel.objects.get(
                    pk=int(filter_parameter)) for filter_parameter in channel_filter_list]

                if len(filter_bot_objs) != 0 and len(filter_channel_objs) != 0:
                    intent_objs = intent_objs.filter(
                        bots__in=filter_bot_objs, channels__in=filter_channel_objs).distinct()
                elif len(filter_bot_objs) != 0 and len(filter_channel_objs) == 0:
                    intent_objs = intent_objs.filter(
                        bots__in=filter_bot_objs).distinct()
                elif len(filter_bot_objs) == 0 and len(filter_channel_objs) != 0:
                    intent_objs = intent_objs.filter(
                        channels__in=filter_channel_objs).distinct()
                else:
                    pass

            intent_name = []
            intent_pk = []
            intent_edit_url = []
            intent_training_sentence = []
            intent_last_modified_date = []
            intent_text_response_list = []
            intent_image_exist = []
            total_intents = len(intent_objs)

            for intent_obj in intent_objs:

                try:
                    sentence = json.loads(intent_obj.training_data)["0"]
                except Exception:  # noqa: F841
                    sentence = "Not available"

                try:
                    text_response = json.loads(intent_obj.tree.response.sentence)[
                        "items"][0]["text_response"]
                except Exception:  # noqa: F841
                    text_response = "Not available"

                intent_name.append(intent_obj.name)
                intent_pk.append(intent_obj.pk)
                intent_training_sentence.append(sentence)
                intent_text_response_list.append(text_response)
                intent_last_modified_date.append(
                    str(datetime.datetime.strftime(intent_obj.last_modified, "%d %b %Y")))
                intent_edit_url.append(
                    "/chat/edit-intent/?intent_pk=" + str(intent_obj.pk))
                intent_image_exist.append(intent_obj.image_exist())

            response['intent_name'] = intent_name
            response["intent_pk"] = intent_pk
            response["intent_edit_url"] = intent_edit_url
            response["intent_training_sentence"] = intent_training_sentence
            response["intent_last_modified_date"] = intent_last_modified_date
            response["intent_text_response_list"] = intent_text_response_list
            response["intent_image_exist"] = intent_image_exist
            response["total_intents"] = total_intents
            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("FetchAllIntentsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DeleteIntentAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)
            intent_pk_list = data['intent_pk_list']
            bot_pk = data["bot_pk"]

            bot_obj = Bot.objects.get(pk=int(bot_pk))
            if request.user not in bot_obj.users.all():
                response["status"] = 401
                response['message'] = 'You are not authorised to perform this operation.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            for intent_pk in intent_pk_list:
                if not delete_intent(intent_pk, user_obj):
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            bot_obj.need_to_build = True
            bot_obj.last_bot_updated_datetime = datetime.datetime.now()
            bot_obj.save()

            count = 0
            intent_name_list = []
            for intent_pk in intent_pk_list:
                count += 1
                intent_name_list.append({
                    "number": count,
                    "intent_name": Intent.objects.get(pk=int(intent_pk)).name,
                })

            audit_trail_data = json.dumps({
                "intent_pk_list": intent_pk_list,
                "change_data": intent_name_list,
                "bot_pk": str(bot_pk),
            })

            save_audit_trail(user_obj, DELETE_INTENT_ACTION, audit_trail_data)
            description = "Intent(s) deleted with id(s)" + \
                " (" + str(intent_pk_list) + ")"
            add_audit_trail(
                "EASYCHATAPP",
                user_obj,
                "Delete-Intent",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )
            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("DeleteIntentAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class AddTrainingQuestionsAPI(APIView):

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

            json_string = DecryptVariable(data["json_string"])

            data = json.loads(json_string)

            validation_obj = EasyChatInputValidation()

            intent_pk = data['intent_pk']
            bot_pk = data['bot_id']
            training_questions = data["training_questions"]

            intent_obj = None
            if intent_pk != None and intent_pk != '':
                intent_obj = Intent.objects.filter(
                    pk=int(intent_pk), is_deleted=False, is_hidden=False)[0]

            saturated_training_data = []

            for training in training_questions:
                training = validation_obj.remo_html_from_string(training)
                training = validation_obj.remo_special_tag_from_string(
                    training)
                if training not in saturated_training_data:
                    saturated_training_data.append(training)

            training_questions = []
            training_data_dict = json.loads(intent_obj.training_data)

            for index in range(len(training_data_dict)):
                training_questions.append(training_data_dict[str(index)])

            combined_list = training_questions + saturated_training_data
            list_set = set(combined_list)
            # convert the set to the list
            unique_list = (list(list_set))

            training_data_dict = {}
            for index, sentence in enumerate(unique_list):
                training_data_dict[str(index)] = sentence

            intent_obj.training_data = json.dumps(training_data_dict)
            bot_obj = Bot.objects.get(
                pk=int(bot_pk), is_deleted=False)

            intent_obj.synced = False
            intent_obj.trained = False
            bot_obj.need_to_build = True

            intent_obj.save()
            bot_obj.save()

            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AddTrainingQuestionsAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveIntentAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            bot_objs = get_uat_bots(user_obj)
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            
            response_sentence_list = get_response_sentence_list(json_string)

            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            explanation = data["explanation"]
            intent_pk = data["intent_pk"]
            intent_name = str(data['intent_name']).strip()
            intent_name = validation_obj.remo_html_from_string(intent_name)
            intent_name = validation_obj.remo_special_tag_from_string(
                intent_name).strip()
            intent_short_name = data['intent_short_name']

            intent_name_validation_error = False
            if intent_name == "":
                response["status"] = 303
                response["status_message"] = "The provided intent name is incorrect. Only valid text, special characters & emojis can be combined for the intent name."
                intent_name_validation_error = True

            if not intent_name_validation_error and validation_obj.is_string_only_contains_emoji(intent_name):
                response['status'] = 303
                response["status_message"] = "Intent name cannot have only emoji"
                intent_name_validation_error = True

            if not intent_name_validation_error and validation_obj.remo_special_characters_from_string(intent_name) == "":
                response['status'] = 303
                response["status_message"] = "Intent name cannot have only Special Symbols"
                intent_name_validation_error = True
                
            if len(intent_name) > INTENT_TREE_NAME_CHARACTER_LIMIT:
                response['status'] = 303
                response["status_message"] = "Intent Name Cannot Contain More Than 500 Characters"
                intent_name_validation_error = True

            if response["status"] == 303:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            
            if validation_obj.is_string_only_contains_emoji(intent_name):
                response['status'] = 303
                response["status_message"] = "Intent short name cannot have only emoji"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            intent_short_name = validation_obj.remo_html_from_string(intent_short_name)
            intent_short_name = validation_obj.remo_special_tag_from_string(intent_short_name)
            intent_short_name = intent_short_name.strip()

            if len(intent_short_name) > 25:
                response['status'] = 303
                response["status_message"] = "Intent short name cannot be more that 25 characters."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            is_feedback_required = data["is_feedback_required"]
            is_attachment_required = data["is_attachment_required"]
            is_save_attachment_required = data["is_save_attachment_required"]
            is_date_picker_allowed = data["is_date_picker_allowed"]
            is_single_date_picker_allowed = data[
                "is_single_date_picker_allowed"]
            is_multi_date_picker_allowed = data["is_multi_date_picker_allowed"]
            is_single_time_picker_allowed = data[
                "is_single_time_picker_allowed"]
            is_multi_time_picker_allowed = data["is_multi_time_picker_allowed"]
            is_time_picker_allowed = data["is_time_picker_allowed"]
            is_calender_picker_allowed = data["is_calender_picker_allowed"]
            is_single_calender_date_picker_allowed = data[
                "is_single_calender_date_picker_allowed"]
            is_multi_calender_date_picker_allowed = data[
                "is_multi_calender_date_picker_allowed"]
            is_single_calender_time_picker_allowed = data[
                "is_single_calender_time_picker_allowed"]
            is_multi_calender_time_picker_allowed = data[
                "is_multi_calender_time_picker_allowed"]
            is_range_slider_required = data["is_range_slider_required"]
            range_slider_type = data["range_slider_type"]
            minimum_range = data["minimum_range"]
            maximum_range = data["maximum_range"]
            is_radio_button_allowed = data["is_radio_button_allowed"]
            radio_button_choices = data["radio_button_choices"]
            is_check_box_allowed = data["is_check_box_allowed"]
            check_box_choices = data["checkbox_choices_list"]
            is_drop_down_allowed = data["is_drop_down_allowed"]
            drop_down_choices = data["dropdown_choices_list"]
            is_video_recorder_allowed = data["is_video_recorder_allowed"]
            is_save_video_attachment = data[
                "is_save_video_attachment_required"]
            choosen_file_type = data["choosen_file_type"]
            is_phone_widget_enabled = data["is_phone_widget_enabled"]
            country_code = data["country_code"]
            is_create_form_allowed = data["is_create_form_allowed"]
            form_name = data["form_name"]
            form_fields_list = data["form_fields_list"]
            is_part_of_suggestion_list = data["is_part_of_suggestion_list"]
            is_authentication_required = data["is_authentication_required"]
            is_child_intent_visible = data["is_child_intent_visible"]
            is_small_talk = data["is_small_talk"]
            authentication_id = data["authentication_id"]
            authentication_id = validation_obj.remo_html_from_string(
                str(authentication_id))
            channel_list = data['channel_list']
            training_data = data['training_data']
            selected_bot_pk_list = data['selected_bot_pk_list']
            multilingual_name = data['multilingual_name']
            is_automatic_recursion_enabled = data[
                'is_automate_recursion_enabled']
            # is_livechat_enabled = data['is_livechat_enabled']
            table_input_list_of_list = data['table_input_list_of_list']
            for iterator1 in range(len(table_input_list_of_list)):
                for iterator2 in range(len(table_input_list_of_list[iterator1])):
                    table_input_list_of_list[iterator1][iterator2] = validation_obj.sanitize_html(
                        table_input_list_of_list[iterator1][iterator2])
            category_obj_pk = data['category_obj_pk']
            post_processor_variable = data['post_processor_variable']
            is_go_back_enabled = data["is_go_back_enabled"]
            is_recommendation_menu = data["is_recommendation_menu"]
            is_catalogue_added = data["is_catalogue_added"]
            selected_catalogue_sections = data["selected_catalogue_sections"]
            if selected_catalogue_sections is None:
                selected_catalogue_sections = []
            is_catalogue_purchased = data["is_catalogue_purchased"]
            is_custom_order_selected = data["is_custom_order_selected"]
            order_of_response = data["order_of_response"]
            if user_obj.is_staff:
                flow_analytics_variable = data["flow_analytics_variable"]
                is_category_response_allowed = data[
                    "is_category_intent_allowed"]
            is_last_tree = data["is_last_tree"]
            is_exit_tree = data["is_exit_tree"]
            is_transfer_tree = data["is_transfer_tree"]
            allow_barge = data["allow_barge"]
            necessary_keywords = data["necessary_keywords"]
            restricted_keywords = data["restricted_keywords"]
            intent_threshold = data["intent_threshold"]
            whatsapp_list_message_header = data["whatsapp_list_message_header"]
            intent_icon_unique_id = data["intent_icon_unique_id"]
            is_faq_intent = data["is_faq_intent"]
            disposition_code = data["disposition_code"]
            enable_whatsapp_menu_format = data["enable_whatsapp_menu_format"]
            whatsapp_short_name = data["whatsapp_short_name"]
            whatsapp_description = data["whatsapp_description"]

            saturated_training_data = []
            for training in training_data:
                training = validation_obj.remo_html_from_string(training)
                training = validation_obj.remo_special_tag_from_string(
                    training)
                training = validation_obj.remo_special_characters_from_string(
                    training).strip()
                if training not in saturated_training_data:
                    saturated_training_data.append(training)

            training_data = saturated_training_data

            common_bot_pk_found = False

            if not common_bot_pk_found:
                # Check whether intent name is already in trainging data or not
                sanatized_intent_name = validation_obj.remo_special_characters_from_string(
                    intent_name).strip()
                if sanatized_intent_name not in training_data:
                    # If not then add value in training data
                    training_data += [sanatized_intent_name]

                # Add intent name to training data after running word mapper if
                # it does not exists
                for bot_pk in selected_bot_pk_list:
                    bot_obj = Bot.objects.get(
                        pk=int(bot_pk), is_deleted=False)

                    word_mapper_sentence = run_word_mapper(
                        WordMapper, str(intent_name), bot_obj, '', '', '')
                    word_mapper_sentence = validation_obj.remo_special_characters_from_string(
                        word_mapper_sentence).strip()
                    if word_mapper_sentence not in training_data:
                        training_data += [word_mapper_sentence]

                bot_pk = selected_bot_pk_list[0]
                bot_obj = Bot.objects.get(
                    pk=int(bot_pk), is_deleted=False)
                if user_obj not in bot_obj.users.all():
                    response["status"] = 302
                    response['message'] = 'You are not authorised to perform this operation.'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
                bot_info_obj = BotInfo.objects.get(bot=bot_obj)

                # Response
                image_list = data["image_list"]
                video_list = data["video_list"]
                recommended_intent_list = data["recommended_intent_list"]
                child_choices = data["child_choices"]
                card_list = data["card_list"]

                temp_image_list = []
                for image in image_list:
                    if not validation_obj.is_valid_url(image) or image.strip() == "":
                        return Response(data=return_invalid_response(response, "Image link is invalid.", 302))
                    temp_image_list.append(html.escape(image))

                image_list = temp_image_list

                temp_video_list = []
                for video in video_list:
                    if not validation_obj.is_valid_url(video) or video.strip() == "":
                        return Response(data=return_invalid_response(response, "Video link is invalid.", 302))
                    temp_video_list.append(html.escape(video))

                video_list = temp_video_list

                for card in card_list:
                    card_title = card["title"]
                    card_content = card["content"]
                    card_link = card["link"]
                    card_img_url = card["img_url"]
                    if not validation_obj.is_valid_card_name(card_title) or card_title.strip() == "":
                        return Response(data=return_invalid_response(response, "Card title can only contain alphabets, emojis and special characters (&, $, !, @, ?).", 302))

                    card_content = validation_obj.remo_html_from_string(
                        card_content)
                    card_content = validation_obj.remo_unwanted_security_characters(
                        card_content)
                    if card_content.strip() == "":
                        return Response(data=return_invalid_response(response, "Card content can only contain alphabets.", 302))

                    if not validation_obj.is_valid_url(card_link) or card_link.strip() == "":
                        return Response(data=return_invalid_response(response, "Card redirection link is invalid.", 302))

                    if not validation_obj.is_valid_url(card_img_url) or card_img_url.strip() == "":
                        return Response(data=return_invalid_response(response, "Card image link is invalid.", 302))

                    card["img_url"] = html.escape(card_img_url)
                    card["link"] = html.escape(card_link)

                validator_id = data["validator_id"]
                validator_id = validation_obj.remo_html_from_string(
                    validator_id)
                authentication_obj = None
                authentication_name = None
                try:
                    authentication_obj = Authentication.objects.get(
                        pk=int(authentication_id))
                    authentication_name = authentication_obj.name
                except Exception:  # noqa: F841
                    pass

                # Create Training data dict to store into database
                training_data_dict = {}
                for index, sentence in enumerate(training_data):
                    training_data_dict[str(index)] = sentence

                intent_obj = None
                change_data = []
                is_new_intent = True
                is_intent_name_updated = False
                if intent_pk != None and intent_pk != '':
                    intent_obj = Intent.objects.filter(
                        pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False).first()

                    bot_obj = intent_obj.bots.all()[0]

                    is_new_intent = False
                    change_data = add_changes(
                        change_data, intent_obj.name, intent_name, "Intent name")

                    if intent_obj.name != intent_name:
                        intent_obj.synced = False
                        intent_obj.trained = False
                        bot_obj.need_to_build = True
                        is_intent_name_updated = True

                    if is_duplicate_intent_exists(intent_name, bot_obj, intent_obj.pk, intent_obj.channels.all()):
                        return Response(data=return_invalid_response(response, "Intent with same name already exists", 301))

                    intent_obj.name = intent_name
                    hashed_name = get_hashed_intent_name(intent_name, bot_obj)
                    intent_obj.intent_hash = hashed_name
                    change_data = add_changes(change_data, json.loads(
                        intent_obj.training_data), training_data_dict, "Training questions")

                    if json.loads(intent_obj.training_data) != training_data_dict:
                        intent_obj.synced = False
                        intent_obj.trained = False
                        bot_obj.need_to_build = True

                    bot_obj.save()

                    intent_obj.training_data = json.dumps(training_data_dict)

                    change_data = add_changes(
                        change_data, intent_obj.is_feedback_required, is_feedback_required, "Feedback required")
                    intent_obj.is_feedback_required = is_feedback_required
                    change_data = add_changes(change_data, intent_obj.is_part_of_suggestion_list,
                                              is_part_of_suggestion_list, "Make intent part of suggestion list")
                    intent_obj.is_part_of_suggestion_list = is_part_of_suggestion_list
                    change_data = add_changes(
                        change_data, intent_obj.is_authentication_required, is_authentication_required, "Authentication required")
                    intent_obj.is_authentication_required = is_authentication_required
                    change_data = add_changes(
                        change_data, intent_obj.is_small_talk, is_small_talk, "Make intent as part of small talks")
                    intent_obj.is_small_talk = is_small_talk
                    if user_obj.is_staff:
                        intent_obj.is_category_response_allowed = is_category_response_allowed
                    if intent_obj.auth_type != None:
                        change_data = add_changes(
                            change_data, intent_obj.auth_type.name, authentication_name, "Auth type")
                    elif intent_obj.auth_type == None and authentication_obj != None:
                        change_data = add_changes(
                            change_data, None, authentication_name, "Added auth type")
                    intent_obj.auth_type = authentication_obj
                    change_data = add_changes(
                        change_data, intent_obj.order_of_response, order_of_response, "Order of response")
                    intent_obj.order_of_response = json.dumps(
                        order_of_response)
                    change_data = add_changes(
                        change_data, intent_obj.is_custom_order_selected, is_custom_order_selected, "Is custom order selected")
                    intent_obj.is_custom_order_selected = is_custom_order_selected
                    change_data = add_changes(
                        change_data, intent_obj.is_faq_intent, is_faq_intent, "Is intent marked as FAQ Intent")
                    intent_obj.is_faq_intent = is_faq_intent

                    for channel in intent_obj.channels.all():
                        if channel.name not in channel_list:
                            change_data.append({
                                "heading": "Removed channel",
                                "old_data": channel.name,
                                "new_data": ""
                            })

                    for channel in channel_list:
                        channel_obj = Channel.objects.get(
                            name=str(channel))
                        if channel_obj not in intent_obj.channels.all():
                            change_data.append({
                                "heading": "Added channel",
                                "old_data": "",
                                "new_data": channel
                            })
                    intent_obj.remove_all_channel_objects()
                    intent_obj.remove_all_bot_objects()

                    for channel_name in channel_list:
                        channel_obj = Channel.objects.get(
                            name=str(channel_name))
                        intent_obj.channels.add(channel_obj)

                    for bot_pk in selected_bot_pk_list:
                        bot_obj = Bot.objects.get(
                            pk=int(bot_pk), is_deleted=False)
                        intent_obj.bots.add(bot_obj)

                    if category_obj_pk != "" or category_obj_pk != None:
                        category_obj = Category.objects.get(
                            pk=int(category_obj_pk))
                        if intent_obj.category != None and intent_obj.category.name != category_obj.name:
                            change_data.append({
                                "heading": "Category changed",
                                "old_data": intent_obj.category.name,
                                "new_data": category_obj.name
                            })
                        elif intent_obj.category == None:
                            change_data.append({
                                "heading": "Category Added",
                                "old_data": "",
                                "new_data": category_obj.name
                            })
                        intent_obj.category = category_obj

                    if bot_info_obj.enable_intent_icon:
                        if intent_icon_unique_id != "0":
                            intent_obj.build_in_intent_icon = BuiltInIntentIcon.objects.filter(
                                unique_id=int(intent_icon_unique_id)).first()
                        else:
                            intent_obj.build_in_intent_icon = None

                else:
                    hashed_name = get_hashed_intent_name(intent_name, bot_obj)
                    intent_obj = Intent.objects.create(name=intent_name,
                                                       intent_hash=hashed_name,
                                                       training_data=json.dumps(
                                                           training_data_dict),
                                                       is_feedback_required=is_feedback_required,
                                                       is_part_of_suggestion_list=is_part_of_suggestion_list,
                                                       # is_livechat_enabled=is_livechat_enabled,
                                                       is_authentication_required=is_authentication_required,
                                                       threshold=1.0,
                                                       is_faq_intent=is_faq_intent)

                    for channel_name in channel_list:
                        channel_obj = Channel.objects.get(
                            name=str(channel_name))
                        intent_obj.channels.add(channel_obj)
                    intent_obj.bots.clear()
                    for bot_pk in selected_bot_pk_list:
                        bot_obj = Bot.objects.get(
                            pk=int(bot_pk), is_deleted=False)
                        intent_obj.bots.add(bot_obj)
                        bot_obj.need_to_build = True
                        bot_obj.save()

                    if category_obj_pk != "" or category_obj_pk != None:
                        category_obj = Category.objects.get(
                            pk=int(category_obj_pk))
                        intent_obj.category = category_obj

                    intent_obj.is_authentication_required = is_authentication_required
                    intent_obj.is_small_talk = is_small_talk
                    intent_obj.auth_type = authentication_obj

                    intent_obj.save()

                    audit_trail_data = json.dumps({
                        "intent_pk": intent_obj.pk
                    })

                    save_audit_trail(
                        user_obj, CREATE_INTENT_ACTION, audit_trail_data)

                    if bot_info_obj.enable_intent_icon:
                        intent_obj.build_in_intent_icon = BuiltInIntentIcon.objects.filter(
                            unique_id=int(intent_icon_unique_id)).first()

                if is_child_intent_visible != "None":
                    if intent_obj.tree.is_child_tree_visible != is_child_intent_visible and is_child_intent_visible:
                        intent_obj.tree.is_child_tree_visible = is_child_intent_visible
                        check_and_update_whatsapp_menu_objs(intent_obj.tree)

                    intent_obj.tree.is_child_tree_visible = is_child_intent_visible
                    intent_obj.tree.save()

                if user_obj.is_staff:
                    if is_category_response_allowed:
                        intent_obj.tree.is_child_tree_visible = False
                        intent_obj.tree.save()

                explanation_obj = None
                if intent_obj.tree.explanation == None:
                    explanation_obj = Explanation.objects.create()

                else:
                    explanation_obj = intent_obj.tree.explanation

                explanation_obj.explanation = explanation
                explanation_obj.save()
                intent_obj.tree.explanation = explanation_obj
                intent_obj.multilingual_name = multilingual_name

                response_obj = None
                if intent_obj.tree.response == None:
                    response_obj = BotResponse.objects.create()
                else:
                    response_obj = intent_obj.tree.response

                try:
                    previous_tree_sentence = json.loads(
                        response_obj.sentence)["items"][0]
                except Exception:
                    previous_tree_sentence = {"text_response": "", "speech_response": "",
                                              "text_reprompt_response": "", "speech_reprompt_response": "", "tooltip_text": ""}
                    pass
                sentence_json = {
                    "items": []
                }
                for sentence in response_sentence_list:
                    text_response = sentence["text_response"]
                    text_response = validation_obj.clean_html(text_response)
                    speech_response = sentence["speech_response"]
                    speech_response = validation_obj.custom_remo_html_tags(speech_response)
                    speech_response = validation_obj.clean_html(
                        speech_response)
                    hinglish_response = sentence["hinglish_response"]
                    hinglish_response = validation_obj.clean_html(
                        hinglish_response)
                    reprompt_response = sentence["reprompt_response"]
                    reprompt_response = validation_obj.clean_html(
                        reprompt_response)
                    speech_response = speech_response.replace("</p><p>", " ")
                    speech_response = validation_obj.remo_html_from_string(
                        speech_response)
                    ssml_response = sentence["ssml_response"].strip()

                    if speech_response == "":
                        speech_response = text_response.replace("</p><p>", " ")
                        speech_response = validation_obj.remo_html_from_string(
                            speech_response)

                    if reprompt_response == "":
                        reprompt_response = text_response
                    if ssml_response == "":
                        ssml_response = speech_response

                    try:
                        change_data = add_changes(
                            change_data, previous_tree_sentence["text_response"], text_response, "Bot text response")
                        change_data = add_changes(
                            change_data, previous_tree_sentence["speech_response"], speech_response, "Bot speech response")
                        change_data = add_changes(
                            change_data, previous_tree_sentence["hinglish_response"], hinglish_response, "Bot hinglish response")
                        change_data = add_changes(
                            change_data, previous_tree_sentence["reprompt_response"], reprompt_response, "Bot reprompt response")
                        change_data = add_changes(
                            change_data, previous_tree_sentence["ssml_response"], ssml_response, "Bot SSML response")    
                    except Exception:
                        pass

                    speech_response = BeautifulSoup(speech_response).text

                    sentence_json["items"].append({
                        "text_response": text_response,
                        "speech_response": speech_response,
                        "hinglish_response": hinglish_response,
                        "text_reprompt_response": reprompt_response,
                        "speech_reprompt_response": speech_response,
                        "tooltip_response": "",
                        "ssml_response": ssml_response,
                    })
                if not is_new_intent:
                    eng_lang_obj = None
                    if Language.objects.filter(lang="en"):
                        eng_lang_obj = Language.objects.get(lang="en")
                    activity_update = get_bot_response_activity_update_status(
                        response_obj, sentence, card_list, table_input_list_of_list, eng_lang_obj, LanguageTuningBotResponseTable)

                    if is_intent_name_updated:
                        update_intent_activity_status(intent_obj, activity_update, eng_lang_obj, LanguageTuningIntentTable)
                        update_tree_activity_status(intent_obj.tree, activity_update, eng_lang_obj, LanguageTuningTreeTable)
                    
                    response_obj.activity_update = json.dumps(activity_update)

                response_obj.sentence = json.dumps(sentence_json)
                change_data = add_changes(change_data, json.loads(response_obj.images)[
                                          "items"], image_list, "Images in bot response")
                response_obj.images = json.dumps({"items": image_list})
                change_data = add_changes(change_data, json.loads(response_obj.videos)[
                                          "items"], video_list, "Videos in bot response")
                response_obj.videos = json.dumps({"items": video_list})

                if json.loads(response_obj.recommendations)["items"] != recommended_intent_list:
                    old_data_list = []

                    for item in json.loads(response_obj.recommendations)["items"]:
                        old_data_list.append(
                            Intent.objects.get(pk=int(item)).name)

                    new_data_list = []

                    for item in recommended_intent_list:
                        new_data_list.append(
                            Intent.objects.get(pk=int(item)).name)

                    change_data.append({
                        "heading": "Quick recommendations in bot response",
                        "old_data": old_data_list,
                        "new_data": new_data_list
                    })
                response_obj.recommendations = json.dumps(
                    {"items": recommended_intent_list})
                response_obj.whatsapp_list_message_header = whatsapp_list_message_header
                change_data = add_changes(change_data, json.loads(response_obj.cards)[
                                          "items"], card_list, "Cards in bot response")
                response_obj.cards = json.dumps({"items": card_list})
                change_data = add_changes(change_data, json.loads(response_obj.table)[
                                          "items"], table_input_list_of_list, "Table in bot response")
                response_obj.table = json.dumps(
                    {"items": table_input_list_of_list})

                if child_choices != []:
                    if len(intent_obj.tree.children.all()) != len(child_choices):
                        response["status"] = 401
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)
                    else:
                        response_obj.choices.all().delete()
                        for choices in child_choices:
                            choice_obj = Choice.objects.create(
                                value=choices, display=choices)
                            response_obj.choices.add(choice_obj)
                        response_obj.save()
                else:
                    response_obj.choices.all().delete()
                    response_obj.save()

                modes = json.loads(response_obj.modes)
                modes_param = json.loads(response_obj.modes_param)
                modes_param["selected_catalogue_sections"] = selected_catalogue_sections

                # if is_livechat_enabled:
                #     modes["is_livechat"] = "true"
                # else:
                #     modes["is_livechat"] = "false"

                if is_attachment_required:
                    modes["is_attachment_required"] = "true"
                    modes_param["choosen_file_type"] = choosen_file_type
                    change_data = add_changes(
                        change_data, modes_param["choosen_file_type"], choosen_file_type, "Choose attachment type in bot response")
                    if is_save_attachment_required:
                        modes["is_save_attachment_required"] = "true"
                    else:
                        modes["is_save_attachment_required"] = "false"
                else:
                    modes["is_attachment_required"] = "false"
                    change_data = add_changes(
                        change_data, "none", "none", "Choose attachment type in bot response")
                    modes_param["choosen_file_type"] = "none"

                if is_date_picker_allowed:
                    modes["is_datepicker"] = "true"
                    if is_single_date_picker_allowed:
                        modes["is_single_datepicker"] = "true"
                        modes["is_multi_datepicker"] = "false"
                        modes_param["datepicker_list"] = [
                            {"placeholder": "Date"}]
                    elif is_multi_date_picker_allowed:
                        modes["is_single_datepicker"] = "false"
                        modes["is_multi_datepicker"] = "true"
                        modes_param["datepicker_list"] = [
                            {"placeholder": "From Date"}, {"placeholder": "To Date"}]
                else:
                    modes["is_datepicker"] = "false"
                    modes["is_single_datepicker"] = "false"
                    modes["is_multi_datepicker"] = "false"
                if is_time_picker_allowed:
                    modes["is_timepicker"] = "true"
                    if is_single_time_picker_allowed:
                        modes["is_single_timepicker"] = "true"
                        modes["is_multi_timepicker"] = "false"
                        modes_param["timepicker_list"] = [
                            {"placeholder": "Time"}]
                    elif is_multi_time_picker_allowed:
                        modes["is_single_timepicker"] = "false"
                        modes["is_multi_timepicker"] = "true"
                        modes_param["timepicker_list"] = [
                            {"placeholder": "From Time"}, {"placeholder": "To Time"}]
                else:
                    modes["is_timepicker"] = "false"
                    modes["is_single_timepicker"] = "false"
                    modes["is_multi_timepicker"] = "false"

                if is_calender_picker_allowed:
                    modes["is_calender"] = "true"
                    if is_single_calender_date_picker_allowed:
                        modes["is_single_datepicker"] = "true"
                        modes["is_multi_datepicker"] = "false"
                        modes_param["datepicker_list"] = [
                            {"placeholder": "Date"}]
                    elif is_multi_calender_date_picker_allowed:
                        modes["is_single_datepicker"] = "false"
                        modes["is_multi_datepicker"] = "true"
                        modes_param["datepicker_list"] = [
                            {"placeholder": "From Date"}, {"placeholder": "To Date"}]
                    else:
                        modes_param["datepicker_list"] = []

                    if is_single_calender_time_picker_allowed:
                        modes["is_single_timepicker"] = "true"
                        modes["is_multi_timepicker"] = "false"
                        modes_param["timepicker_list"] = [
                            {"placeholder": "Time"}]
                    elif is_multi_calender_time_picker_allowed:
                        modes["is_single_timepicker"] = "false"
                        modes["is_multi_timepicker"] = "true"
                        modes_param["timepicker_list"] = [
                            {"placeholder": "From Time"}, {"placeholder": "To Time"}]
                    else:
                        modes_param["timepicker_list"] = []

                else:
                    modes["is_calender"] = "false"

                if is_range_slider_required:
                    modes["is_range_slider"] = "true"
                    modes_param["range_slider_list"] = [
                        {"placeholder": "Select Range", "min": minimum_range, "max": maximum_range, "range_type": range_slider_type}]
                else:
                    modes["is_range_slider"] = "false"

                if is_radio_button_allowed:
                    modes["is_radio_button"] = "true"
                    modes_param["radio_button_choices"] = radio_button_choices
                else:
                    modes["is_radio_button"] = "false"

                if is_check_box_allowed:
                    modes["is_check_box"] = "true"
                    modes_param["check_box_choices"] = check_box_choices
                else:
                    modes["is_check_box"] = "false"

                if is_drop_down_allowed:
                    modes["is_drop_down"] = "true"
                    modes_param["drop_down_choices"] = drop_down_choices
                else:
                    modes["is_drop_down"] = "false"

                if is_video_recorder_allowed:
                    modes["is_video_recorder_allowed"] = "true"
                    if is_save_video_attachment:
                        modes["is_save_video_attachment"] = "true"
                    else:
                        modes["is_save_video_attachment"] = "false"
                else:
                    modes["is_video_recorder_allowed"] = "false"

                if is_phone_widget_enabled:
                    modes["is_phone_widget_enabled"] = "true"
                    modes_param["country_code"] = country_code

                else:
                    modes["is_phone_widget_enabled"] = "false"

                if is_create_form_allowed:
                    modes["is_create_form_allowed"] = "true"
                    modes_param["form_name"] = form_name
                    modes_param["form_fields_list"] = json.dumps(
                        form_fields_list)
                else:
                    modes["is_create_form_allowed"] = "false"

                if is_recommendation_menu:
                    modes["is_recommendation_menu"] = "true"
                    modes_param["country_code"] = country_code
                else:
                    modes["is_recommendation_menu"] = "false"

                modes["is_catalogue_added"] = "true" if is_catalogue_added else "false"

                response_obj.modes = json.dumps(modes)
                response_obj.modes_param = json.dumps(modes_param)
                response_obj.save()
                intent_obj.tree.response = response_obj
                intent_obj.tree.name = intent_name
                if Language.objects.filter(lang="en").exists():
                    eng_lang_obj = Language.objects.filter(lang="en").first()
                    update_english_language_tuned_object(
                        eng_lang_obj, intent_obj, response_obj, intent_name, LanguageTuningIntentTable)
                intent_obj.tree.multilingual_name = multilingual_name
                intent_obj.tree.short_name = intent_short_name

                intent_obj.tree.is_automatic_recursion_enabled = is_automatic_recursion_enabled

                if(validator_id != None and validator_id != ""):
                    validator_obj = Processor.objects.get(pk=int(validator_id))
                    intent_obj.tree.post_processor = validator_obj
                else:

                    # if there is a previously assigned post_processor, keeping
                    # it as it is in case of no validator being selected from
                    # console.

                    if not ProcessorValidator.objects.filter(processor=intent_obj.tree.post_processor).count():
                        if(post_processor_variable != ""):
                            if intent_obj.tree.post_processor != None and intent_obj.tree.post_processor.name == "PostProcessor_" + str(post_processor_variable):
                                pass
                            else:
                                code = "from EasyChatApp.utils import logger\nimport sys\ndef f(x):\n    json_response = {}\n    json_response['status_code'] = '500'\n    json_response['status_message'] = 'Internal server error.'\n    json_response['data'] = {}\n    try:\n        json_response['data']['" + post_processor_variable + \
                                    "']=x\n        #write your code here\n        json_response['status_code'] = '200'\n        json_response['print'] = 'Hello world!'\n        return json_response\n    except Exception as E:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('PostProcessorContent: %s at %s',str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        json_response['status_code'] = '500'\n        json_response['status_message'] = 'ERROR :-  '+str(E)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return json_response"
                                processor_obj = Processor.objects.create(name="PostProcessor_" + str(
                                    post_processor_variable), function=code, post_processor_direct_value=post_processor_variable)
                                intent_obj.tree.post_processor = processor_obj

                    else:
                        intent_obj.tree.post_processor = None

                intent_obj.tree.is_go_back_enabled = is_go_back_enabled
                intent_obj.tree.save()
                if user_obj.is_staff:
                    intent_obj.tree.flow_analytics_variable = flow_analytics_variable
                    intent_obj.tree.save()

                intent_obj.is_custom_order_selected = is_custom_order_selected
                intent_obj.order_of_response = json.dumps(order_of_response)

                if necessary_keywords != "None":
                    intent_obj.necessary_keywords = necessary_keywords.lower()

                if restricted_keywords != "None":
                    intent_obj.restricted_keywords = restricted_keywords.lower()

                if intent_threshold != "None":
                    intent_obj.threshold = float(intent_threshold)

                intent_obj.save()

                intent_obj.tree.is_last_tree = is_last_tree
                intent_obj.tree.is_exit_tree = is_exit_tree
                intent_obj.tree.enable_transfer_agent = is_transfer_tree
                intent_obj.tree.disposition_code = disposition_code

                voice_bot_conf = json.loads(intent_obj.tree.voice_bot_conf)
                voice_bot_conf["barge_in"] = allow_barge
                intent_obj.tree.voice_bot_conf = json.dumps(voice_bot_conf)

                intent_obj.tree.enable_whatsapp_menu_format = enable_whatsapp_menu_format
                intent_obj.tree.whatsapp_short_name = whatsapp_short_name
                intent_obj.tree.whatsapp_description = whatsapp_description

                intent_obj.tree.is_catalogue_purchased = is_catalogue_purchased
                
                intent_obj.tree.save()

                if intent_pk != None and intent_pk != '' and len(change_data):
                    audit_trail_data = json.dumps({
                        "intent_pk": intent_obj.pk,
                        "change_data": change_data
                    })
                    save_audit_trail(
                        user_obj, MODIFY_INTENT_ACTION, audit_trail_data)

                response['status'] = 200
                response["intent_pk"] = intent_obj.pk
                description = "Intent created with name " + \
                    " (" + intent_name + " and intent pk " + \
                    str(intent_obj.pk) + " )"
                add_audit_trail(
                    "EASYCHATAPP",
                    user_obj,
                    "Add-Intent",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )
        except DuplicateIntentExceptionError as e:
            response["status"] = 301
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveIntentAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveIntentAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveMultilingualIntentAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            bot_objs = get_uat_bots(user_obj)
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            response_sentence_list = get_response_sentence_list(json_string)
            json_string = validation_obj.custom_remo_html_tags(json_string)

            data = json.loads(json_string)

            intent_pk = data["intent_pk"]
            intent_name = data['intent_name']
            intent_name = validation_obj.remo_html_from_string(intent_name)
            intent_name = intent_name.strip()
            card_list = data["card_list"]
            table_input_list_of_list = data['table_input_list_of_list']
            for iterator1 in range(len(table_input_list_of_list)):
                for iterator2 in range(len(table_input_list_of_list[iterator1])):
                    table_input_list_of_list[iterator1][iterator2] = validation_obj.sanitize_html(
                        table_input_list_of_list[iterator1][iterator2])
            selected_language = data["selected_language"]
            selected_language = validation_obj.remo_html_from_string(
                selected_language)
            selected_language = validation_obj.remo_special_tag_from_string(
                selected_language)

            language_obj = Language.objects.get(lang=selected_language)
            intent_obj = None
            if intent_pk != None and intent_pk != '':
                intent_obj = Intent.objects.get(
                    pk=int(intent_pk), is_deleted=False, is_hidden=False)

                intent_tuning_obj = LanguageTuningIntentTable.objects.get(
                    intent=intent_obj, language=language_obj)

                if intent_tuning_obj.multilingual_name != intent_name:
                    training_data = list(json.loads(intent_obj.training_data).values())

                    english_translated_previous_intent_name = translate_given_text_to_english(intent_tuning_obj.multilingual_name)
                    if english_translated_previous_intent_name and english_translated_previous_intent_name != intent_tuning_obj.multilingual_name:
                        if english_translated_previous_intent_name.strip().lower() in training_data:
                            training_data.remove(english_translated_previous_intent_name.strip().lower())

                    english_translated_intent_name = translate_given_text_to_english(intent_name)
                    if english_translated_intent_name and english_translated_intent_name != intent_name:
                        if english_translated_intent_name.strip().lower() not in training_data:
                            training_data.append(english_translated_intent_name.strip().lower())

                    training_data_dict = {}
                    index = 0
                    for training_sentence in training_data:
                        training_data_dict[str(index)] = training_sentence
                        index += 1

                    intent_obj.training_data = json.dumps(training_data_dict)
                    intent_obj.synced = False
                    intent_obj.trained = False
                    intent_obj.save(update_fields=["training_data", "synced", "trained"])

                    bot_obj = intent_obj.bots.all().first()
                    bot_obj.need_to_build = True
                    bot_obj.save(update_fields=["need_to_build"])
                    
                intent_tuning_obj.multilingual_name = intent_name
                intent_tuning_obj.save()

                tuned_tree_obj = intent_tuning_obj.tree
                tuned_tree_obj.multilingual_name = intent_name
                tuned_tree_obj.save()

                bot_response_tuned_obj = intent_tuning_obj.tree.response

                sentence_json = {
                    "items": []
                }
                for sentence in response_sentence_list:
                    text_response = sentence["text_response"]
                    speech_response = sentence["speech_response"]
                    hinglish_response = sentence["hinglish_response"]
                    reprompt_response = sentence["reprompt_response"]
                    ssml_response = sentence["ssml_response"].strip()

                    speech_response = speech_response.replace("</p><p>", " ")
                    speech_response = validation_obj.remo_html_from_string(
                        speech_response)

                    if speech_response == "":
                        speech_response = text_response.replace("</p><p>", " ")
                        speech_response = validation_obj.remo_html_from_string(
                            speech_response)

                    if reprompt_response == "":
                        reprompt_response = text_response

                    if ssml_response == "":
                        ssml_response = speech_response

                    speech_response = BeautifulSoup(speech_response).text

                    sentence_json["items"].append({
                        "text_response": text_response,
                        "speech_response": speech_response,
                        "hinglish_response": hinglish_response,
                        "text_reprompt_response": reprompt_response,
                        "speech_reprompt_response": speech_response,
                        "tooltip_response": "",
                        "ssml_response": ssml_response,
                    })

                bot_response_tuned_obj.sentence = json.dumps(sentence_json)
                bot_response_tuned_obj.cards = json.dumps({"items": card_list})
                bot_response_tuned_obj.table = json.dumps(
                    {"items": table_input_list_of_list})
                bot_response_tuned_obj.save()

            response['status'] = 200
            response["intent_pk"] = intent_obj.pk
            description = "Multi lingual Intent created with name " + \
                " (" + intent_name + "and intent pk " + str(intent_pk) + " )"
            add_audit_trail(
                "EASYCHATAPP",
                user_obj,
                "Add-Intent",
                description,
                json.dumps(data),
                request.META.get("PATH_INFO"),
                request.META.get('HTTP_X_FORWARDED_FOR')
            )
        except DuplicateIntentExceptionError as e:
            response["status"] = 301
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveMultilingualIntentAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveMultilingualIntentAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveMultilingualIntent = SaveMultilingualIntentAPI.as_view()


class FetchIntentInformationAPI(APIView):

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

            validation_obj = EasyChatInputValidation()
            config = Config.objects.all().first()

            json_string = DecryptVariable(data["json_string"])
            json_string = json.loads(json_string)
            intent_pk = json_string["intent_pk"]
            bot_id = json_string["bot_id"]
            selected_language = json_string.get("selected_language", "en")
            bot_obj = Bot.objects.get(
                pk=int(bot_id), is_deleted=False)
            intent_obj = Intent.objects.filter(
                pk=int(intent_pk), bots__in=[bot_obj], is_deleted=False, is_hidden=False)[0]
            intent_name = intent_obj.name
            answer_pk = None
            intent_response = None
            recommendation_list = []
            if intent_obj.tree.response is not None:
                answer_pk = intent_obj.tree.response.pk
                intent_response = {}
                bot_response_obj = intent_obj.tree.response
                selected_language_obj = Language.objects.filter(
                    lang=selected_language).first()

                response_list = []
                choice_list = []
                card_list = []
                image_list = []
                video_list = []
                modes_dict = {}
                modes_params_dict = {}

                try:
                    table_list_of_list = bot_response_obj.table
                    if selected_language != "en":
                        intent_tuning_obj = check_and_update_tunning_object(intent_obj, selected_language_obj, LanguageTuningIntentTable,
                                                                            LanguageTuningTreeTable, LanguageTuningBotResponseTable, LanguageTuningChoicesTable, EasyChatTranslationCache)
                        table_list_of_list = intent_tuning_obj.tree.response.table
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("No table response %s %s", str(e),
                                   str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass

                # Extract speech text response
                try:
                    response_list = json.loads(
                        bot_response_obj.sentence)["items"]
                    if selected_language != "en":
                        tuned_bot_response = LanguageTuningBotResponseTable.objects.filter(
                            language=selected_language_obj, bot_response=bot_response_obj).first()
                        response_list = json.loads(
                            tuned_bot_response.sentence)["items"]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("No response %s %s", str(e),
                                   str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass

                ## Extract card list
                try:
                    card_list = json.loads(bot_response_obj.cards)["items"]
                    if selected_language != "en":
                        tuned_bot_response = LanguageTuningBotResponseTable.objects.filter(
                            language=selected_language_obj, bot_response=bot_response_obj).first()
                        card_list = json.loads(
                            tuned_bot_response.cards)["items"]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("No cards %s %s", str(e),
                                   str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass

                if selected_language != "en":
                    try:
                        intent_name = intent_tuning_obj.multilingual_name
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.warning("Multilingual name %s %s", str(e),
                                        str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        pass
                    intent_response["response_list"] = response_list
                    intent_response["card_list"] = card_list
                    intent_response["table_list_of_list"] = table_list_of_list
                    response['answer_pk'] = answer_pk
                    response['intent_response'] = intent_response
                    response["intent_name"] = intent_name
                    response["status"] = 200

                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

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
                    choice_obj = Choice.objects.filter(pk=int(choice_pk)).first()
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

                intent_response["response_list"] = response_list
                intent_response["image_list"] = image_list
                intent_response["video_list"] = video_list
                intent_response["choice_list"] = choice_list
                intent_response["recommendation_list"] = recommendation_list
                intent_response["card_list"] = card_list
                intent_response["modes"] = modes_dict
                intent_response["modes_param"] = modes_params_dict
                intent_response["table_list_of_list"] = table_list_of_list
                intent_response['status'] = 200

            response["intent_response"] = intent_response
            other_settings = {}

            other_settings["is_item_purchased"] = intent_obj.tree.is_catalogue_purchased

            intent_children_list = []

            intent_children = intent_obj.tree.children.all()

            for children in intent_children:
                intent_children_list.append(children.name)
            other_settings["intent_children_list"] = intent_children_list

            child_choices_list = []

            child_choices = intent_obj.tree.response.choices.all()

            for choice in child_choices:
                child_choices_list.append(choice.value)
            other_settings["child_choices_list"] = child_choices_list

            if child_choices_list != [] and intent_children_list != child_choices_list:
                choices_order_changed = True

            else:
                choices_order_changed = False
            other_settings["choices_order_changed"] = choices_order_changed

            # selected_bot_obj_list = intent_obj.bots.all()

            # intent_objs_list = Intent.objects.filter(bots__in=selected_bot_obj_list, is_deleted=False, is_form_assist_enabled=False, is_hidden=False).distinct()

            recommeded_intents_dict_list = []

            # modified_intent_list = []
            is_quick_recommendation_present = False

            for intent_pk in recommendation_list:
                intent = Intent.objects.filter(pk=int(intent_pk), is_hidden=False, is_deleted=False, is_small_talk=False).first()
                if intent:
                    is_quick_recommendation_present = True
                    recommeded_intents_dict_list.append(intent_pk)
                    # modified_intent_list.append({
                    #     "is_selected": True,
                    #     "intent_name": intent.name,
                    #     "intent_pk": intent_pk
                    # })
            # for int_obj in intent_objs_list:
            #     if not int_obj.is_small_talk and str(int_obj.pk) not in recommendation_list:
            #         modified_intent_list.append({
            #             "is_selected": False,
            #             "intent_name": int_obj.name,
            #             "intent_pk": int_obj.pk
            #         })
            other_settings["is_quick_recommendation_present"] = is_quick_recommendation_present

            is_faq_intent = intent_obj.is_faq_intent
            is_small_talk = intent_obj.is_small_talk
            is_part_of_suggestion_list = intent_obj.is_part_of_suggestion_list
            validators = ProcessorValidator.objects.filter(
                bot=bot_obj).values("name", "processor__pk")
            post_processor_variable = ""
            selected_validator_obj = None

            if intent_obj.tree.post_processor:
                processor_obj = intent_obj.tree.post_processor
                post_processor_variable = processor_obj.post_processor_direct_value
                if len(ProcessorValidator.objects.filter(processor=processor_obj)) != 0:
                    selected_validator_obj = ProcessorValidator.objects.filter(
                        processor=processor_obj).values("processor__pk").first()
            is_bot_feedback_required = bot_obj.is_feedback_required
            is_feedback_required = intent_obj.is_feedback_required
            authentication_objs = get_authentication_objs(
                [bot_obj])
            is_authentication_required = intent_obj.is_authentication_required
            selected_user_authentication = None
            if intent_obj.auth_type:
                selected_user_authentication = {"id": intent_obj.auth_type.pk, "name": intent_obj.auth_type.name}
            is_child_tree_visible = intent_obj.tree.is_child_tree_visible
            show_go_back_checkbox = False
            is_go_back_enabled = intent_obj.tree.is_go_back_enabled
            is_last_tree = intent_obj.tree.is_last_tree
            is_exit_tree = intent_obj.tree.is_exit_tree
            is_transfer_tree = intent_obj.tree.enable_transfer_agent
            allow_barge = intent_obj.tree.check_barge_in_enablement()
            enable_intent_level_nlp = bot_obj.enable_intent_level_nlp
            necessary_keywords = str(intent_obj.necessary_keywords)
            restricted_keywords = str(intent_obj.restricted_keywords)
            intent_threshold = str(intent_obj.threshold)
            is_automatic_recursion_enabled = intent_obj.tree.is_automatic_recursion_enabled
            pipe_processor_tree_name = ""
            api_tree_name = ""
            post_processor_tree_name = ""

            if intent_obj.tree.pipe_processor:
                pipe_processor_tree_name = ": " + intent_obj.tree.pipe_processor.name
            if intent_obj.tree.api_tree:
                api_tree_name = ": " + intent_obj.tree.api_tree.name
            if intent_obj.tree.post_processor:
                post_processor_tree_name = ": " + intent_obj.tree.post_processor.name

            is_package_installer_on = config.is_package_installer_on
            is_whatsapp_simulator_on = config.is_whatsapp_simulator_on
            is_custom_js_required = bot_obj.is_custom_js_required
            is_custom_css_required = bot_obj.is_custom_css_required
            flow_analytics_variable = intent_obj.tree.flow_analytics_variable
            required_analytics_variable = False
            if flow_analytics_variable != "":
                required_analytics_variable = True
            is_category_response_allowed = intent_obj.is_category_response_allowed

            other_settings.update({
                "is_package_installer_on": is_package_installer_on,
                "is_whatsapp_simulator_on": is_whatsapp_simulator_on,
                "is_faq_intent": is_faq_intent,
                "is_small_talk": is_small_talk,
                "is_part_of_suggestion_list": is_part_of_suggestion_list,
                "validators": list(validators),
                "post_processor_variable": post_processor_variable,
                "selected_validator_obj": selected_validator_obj,
                "is_bot_feedback_required": is_bot_feedback_required,
                "is_feedback_required": is_feedback_required,
                "authentication_objs": authentication_objs,
                "is_authentication_required": is_authentication_required,
                "selected_user_authentication": selected_user_authentication,
                "is_child_tree_visible": is_child_tree_visible,
                "show_go_back_checkbox": show_go_back_checkbox,
                "is_go_back_enabled": is_go_back_enabled,
                "is_last_tree": is_last_tree,
                "is_exit_tree": is_exit_tree,
                "is_transfer_tree": is_transfer_tree,
                "allow_barge": allow_barge,
                "enable_intent_level_nlp": enable_intent_level_nlp,
                "necessary_keywords": necessary_keywords,
                "restricted_keywords": restricted_keywords,
                "intent_threshold": intent_threshold,
                "is_automatic_recursion_enabled": is_automatic_recursion_enabled,
                "pipe_processor_tree_name": pipe_processor_tree_name,
                "api_tree_name": api_tree_name,
                "post_processor_tree_name": post_processor_tree_name,
                "is_package_installer_on": is_package_installer_on,
                "is_whatsapp_simulator_on": is_whatsapp_simulator_on,
                "is_custom_js_required": is_custom_js_required,
                "is_custom_css_required": is_custom_css_required,
                "flow_analytics_variable": flow_analytics_variable,
                "required_analytics_variable": required_analytics_variable,
                "is_category_response_allowed": is_category_response_allowed,
                "whatsapp_list_message_header": intent_obj.tree.response.whatsapp_list_message_header,
                "disposition_code": intent_obj.tree.disposition_code,
            })

            response["other_settings"] = other_settings
            supported_channel_list = list(
                intent_obj.channels.values_list("name", flat=True))
            if "default" in supported_channel_list:
                supported_channel_list.remove("default")

            # is_feedback_required = intent_obj.feedback_required

            training_data_list = []
            training_data = json.loads(intent_obj.training_data)
            for key in training_data.keys():
                training_data_list.append(training_data[key])
            is_custom_order_selected = intent_obj.is_custom_order_selected

            if intent_obj.tree.explanation == None:
                explanation = ""
            else:
                explanation = intent_obj.tree.explanation.explanation
            
            enable_intent_level_nlp = bot_obj.enable_intent_level_nlp

            short_name_enabled = False
            for channel in supported_channel_list:
                if channel == 'GoogleBusinessMessages':
                    short_name_enabled = True

            whatsapp_menu_section_objs_list = WhatsAppMenuSection.objects.filter(tree=intent_obj.tree).order_by("pk")
            whatsapp_menu_section_objs = []
            for whatsapp_menu_section_obj in whatsapp_menu_section_objs_list:
                whatsapp_menu_section_data = {}
                whatsapp_menu_section_data["pk"] = whatsapp_menu_section_obj.pk
                whatsapp_menu_section_data["title"] = whatsapp_menu_section_obj.title
                whatsapp_menu_section_data["child_tree_details"] = whatsapp_menu_section_obj.get_child_tree_details()
                whatsapp_menu_section_data["main_intent_details"] = whatsapp_menu_section_obj.get_main_intent_details()
                whatsapp_menu_section_objs.append(whatsapp_menu_section_data)

            whatsapp_quick_recommendations_allowed = 10

            if intent_obj.tree.is_child_tree_visible and intent_obj.tree.children.filter(is_deleted=False).exists():
                whatsapp_quick_recommendations_allowed = 10 - intent_obj.tree.children.filter(is_deleted=False).count()
                if whatsapp_quick_recommendations_allowed < 0:
                    whatsapp_quick_recommendations_allowed = 0

            whatsapp_channel_obj = Channel.objects.filter(name="WhatsApp").first()

            selected_child_trees = []
            selected_main_intents = []

            for whatsapp_menu_section in whatsapp_menu_section_objs_list:
                if whatsapp_menu_section.child_trees:
                    selected_child_trees += json.loads(whatsapp_menu_section.child_trees)
                if whatsapp_menu_section.main_intents:
                    selected_main_intents += json.loads(whatsapp_menu_section.main_intents)

            unselected_child_trees = intent_obj.tree.children.filter(is_deleted=False).exclude(pk__in=selected_child_trees).values("name", "pk")
            if intent_obj.tree.children.filter(is_deleted=False).count() == 1 or not intent_obj.tree.is_child_tree_visible:
                unselected_child_trees = []
            unselected_main_intents = Intent.objects.filter(bots=bot_obj, channels=whatsapp_channel_obj, is_deleted=False, is_hidden=False, is_small_talk=False).exclude(pk__in=selected_main_intents).values("name", "pk")

            response.update({
                "necessary_keywords": str(intent_obj.necessary_keywords),
                "restricted_keywords": str(intent_obj.restricted_keywords),
                "intent_threshold": str(intent_obj.threshold),
                "campaign_link": str(intent_obj.campaign_link),
                'short_name_enabled': short_name_enabled,
                'short_name_value': str(intent_obj.tree.short_name),
                'whatsapp_short_name': intent_obj.tree.get_whatsapp_short_name(),
                'whatsapp_description': intent_obj.tree.get_whatsapp_description(),
                "whatsapp_menu_section_objs": whatsapp_menu_section_objs,
                "whatsapp_quick_recommendations_allowed": whatsapp_quick_recommendations_allowed,
                "enable_whatsapp_menu_format": intent_obj.tree.enable_whatsapp_menu_format,
                "unselected_child_trees": list(unselected_child_trees),
                "unselected_main_intents": list(unselected_main_intents),
            })

            response["enable_intent_level_nlp"] = enable_intent_level_nlp
            response["explanation"] = explanation
            response["is_custom_order_selected"] = is_custom_order_selected
            # response["intent_name_list"] = modified_intent_list
            response["recommeded_intents_dict_list"] = recommeded_intents_dict_list
            response['intent_name'] = intent_name
            intent_name = validation_obj.remo_html_from_string(intent_name)
            intent_name = validation_obj.remo_special_tag_from_string(
                intent_name)
            response['answer_pk'] = answer_pk
            response['training_data'] = training_data_list
            response["supported_channel_list"] = supported_channel_list
            response["is_bot_feedback_required"] = bot_obj.is_feedback_required
            order_of_response = json.loads(intent_obj.order_of_response)
            default_order_of_response = json.loads(
                bot_obj.default_order_of_response)

            order_of_response_list = []
            for elements in order_of_response:
                order_of_response_list.append(elements)

            response['order_of_response'] = order_of_response_list

            default_order_of_response_list = []
            for elements in default_order_of_response:
                default_order_of_response_list.append(elements)

            response['default_order_of_response'] = default_order_of_response_list

            catalogue_obj = WhatsappCatalogueDetails.objects.filter(
                bot=bot_obj).first()
            catalogue_sections = {}
            if catalogue_obj:
                catalogue_metadata = json.loads(
                    catalogue_obj.catalogue_metadata)
                if "sections" in catalogue_metadata:
                    for section in catalogue_metadata["sections"]:
                        items_count = len(
                            catalogue_metadata["sections"][section]["product_ids"])
                        if items_count == 1:
                            items_str = " (" + str(items_count) + " item)"
                        else:
                            items_str = " (" + str(items_count) + " items)"
                        catalogue_sections[section] = catalogue_metadata["sections"][section]["section_title"] + items_str

            response["catalogue_sections"] = json.dumps(catalogue_sections)
            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FetchIntentInformationAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class FetchIntentTreeStructureAPI(APIView):

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
            # bot_objs = Bot.objects.filter(users__in=[user_obj])
            bot_objs = get_uat_bots(user_obj)

            if not isinstance(data, dict):
                return json.loads(data)

            validation_obj = EasyChatInputValidation()

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)
            intent_pk = data["intent_pk"]
            selected_language = validation_obj.remo_html_from_string(
                data['selected_language'])
            selected_language = selected_language.strip()
            root_tree_obj = Intent.objects.filter(
                pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False)[0].tree
            language_obj = Language.objects.get(lang=selected_language)
            activity_update = json.loads(
                root_tree_obj.response.activity_update)
            eng_lang_obj = Language.objects.filter(lang="en").first()
            need_to_show_auto_fix_popup = False
            need_to_show_auto_fix_popup = need_to_show_auto_fix_popup_for_intents(
                root_tree_obj.response, activity_update, selected_language, eng_lang_obj, LanguageTuningBotResponseTable)

            json_resp = get_child_tree_objs(root_tree_obj, [], language_obj)
            response["1"] = json_resp
            response["need_to_show_auto_fix_popup"] = need_to_show_auto_fix_popup
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FetchIntentTreeStructureAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


"""
API Tested: GetTrainingDataAPI
input queries:
    bot_id: 
    bot_name: "uat" or other name
expected output:
    status: 200 // SUCCESS
Return:
    return basic details of a bot. Ex. return the suggestion list and max_suggestion limit, word_mapper_list etc
"""


class GetTrainingDataAPI(APIView):

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

            bot_id = data["bot_id"]
            web_page = data["web_page"]
            # bot_name = data["bot_name"]

            page_url_without_params = web_page.split('?')[0]

            traffic_source = TrafficSources.objects.filter(
                web_page=page_url_without_params, visiting_date=datetime.datetime.today().date(), bot=Bot.objects.get(pk=bot_id))
            if traffic_source:
                traffic_source[0].bot_clicked_count = traffic_source[
                    0].bot_clicked_count + 1
                traffic_source[0].save()
            else:
                origin = urlparse(web_page)
                if origin.netloc not in settings.ALLOWED_HOSTS:
                    TrafficSources.objects.create(
                        web_page=page_url_without_params, web_page_visited=1, bot=Bot.objects.get(pk=bot_id))

            bot_obj = Bot.objects.get(pk=bot_id, is_deleted=False, is_uat=True)

            # last_query_time = bot_obj.last_query_time
            # current_time = timezone.now().astimezone(easychat_timezone)
            # last_suggestion_list_update = (
            #     current_time - last_query_time).total_seconds()
            # if last_suggestion_list_update >= settings.UPDATE_SUGGESTION_LIST_FREQUENCY:
            #     word_mapper_list = []
            #     word_mapper_objs = WordMapper.objects.filter(bots__in=[
            #                                                  bot_obj])
            #     for word_mapper in word_mapper_objs:
            #         word_mapper_list.append({
            #             "keyword": word_mapper.keyword,
            #             "similar_words": word_mapper.get_similar_word_list()
            #         })
            #     # cache.set('word_mapper_list_' + str(bot_id), json.dumps(word_mapper_list), 10 * 60)
            #     bot_obj.word_mapper_list = json.dumps(word_mapper_list)
            #     bot_obj.save()
            # else:
            #     word_mapper_list = json.loads(bot_obj.word_mapper_list)

            # if last_suggestion_list_update >= settings.UPDATE_SUGGESTION_LIST_FREQUENCY:
            #     sentence_list = []
            #     channel_obj = Channel.objects.get(name='Web')
            #     intent_objs = Intent.objects.filter(
            # bots__in=[bot_obj], is_part_of_suggestion_list=True,
            # is_deleted=False, is_form_assist_enabled=False, is_hidden=False,
            # channels__in=[channel_obj]).distinct()

            #     for intent_obj in intent_objs:
            #         training_data_dict = json.loads(intent_obj.training_data)
            #         intent_name = intent_obj.name
            #         intent_click_count = intent_obj.intent_click_count

            #         sentence_list.append({
            #             "key": intent_name,
            #             "value": intent_name,
            #             "count": intent_click_count
            #         })

            #         for key in training_data_dict:
            #             training_sentence_lower_str = training_data_dict[key].lower(
            #             )
            #             if training_sentence_lower_str not in sentence_list:
            #                 sentence_list.append({
            #                     "key": training_sentence_lower_str,
            #                     "value": intent_name,
            #                     "count": intent_click_count
            #                 })
            #     bot_obj.suggestion_list = json.dumps(sentence_list)
            #     bot_obj.save()
            # else:
            #     sentence_list = json.loads(bot_obj.suggestion_list)
            # response["sentence_list"] = sentence_list
            # response["max_suggestions"] = bot_obj.max_suggestions
            # response["word_mapper_list"] = word_mapper_list
            response["autocorrect_bot_replace"] = list(
                bot_obj.autcorrect_replace_bot)
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetTrainingDataAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class GetIntentNames(APIView):

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

            bot_id = data["bot_id"]
            # category = data["category"]
            category_id = data["category_id"]
            intent_type = data["intent_type"]
            channel_name = data["channel_name"]

            bot_obj = Bot.objects.get(pk=bot_id, is_deleted=False, is_uat=True)

            # channel_obj = Channel.objects.get(name='Web')
            intent_objs = Intent.objects.filter(
                bots__in=[bot_obj], is_deleted=False, is_hidden=False).distinct()

            if category_id != "":
                category_obj = Category.objects.get(
                    bot=bot_obj, pk=category_id)
                intent_objs = intent_objs.filter(category=category_obj)

            if channel_name != "":
                channel_objs = Channel.objects.filter(name=channel_name)
                intent_objs = intent_objs.filter(channels__in=channel_objs)

            if intent_type not in ["", "all_intent"]:
                if intent_type == "is_form_assist_intent":
                    intent_objs = intent_objs.filter(
                        is_form_assist_enabled=True).order_by('-pk')
                elif intent_type == "is_attachment_required":
                    intents_list = []
                    for intent in intent_objs:
                        if intent.tree.response and 'is_attachment_required' in json.loads(intent.tree.response.modes):
                            if json.loads(intent.tree.response.modes)['is_attachment_required'] == 'true':
                                intents_list.append(intent)

                    intent_objs = intents_list
                elif intent_type == "is_small_talk":
                    intent_objs = intent_objs.filter(
                        is_small_talk=True).order_by('-pk')

            # if category != "" and category != "all_category":
            #     category_obj = Category.objects.get(bot=bot_obj, name=category)
            #     intent_objs = intent_objs.filter(
            #         category=category_obj).order_by('-pk')

            intent_name = []
            intent_name_pk_dict = {}
            for intent_obj in intent_objs:

                intent_name.append(intent_obj.name.replace("'", ""))
                intent_name_pk_dict[
                    str(intent_obj.name).replace('"', '')] = intent_obj.pk

            response["intents_list"] = intent_name
            response["intent_name_pk_dict"] = intent_name_pk_dict
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetIntentNames ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': ''})
            response['error'] = str(e)
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class TrainingSentenceAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            # data = request.data
            training_sentences_obj = TrainingTemplate.objects.all()
            sentence_list = []
            for training_obj in training_sentences_obj:
                training_obj_sentence_list = []
                for sentence_obj in training_obj.sentences.all():
                    training_obj_sentence_list.append(sentence_obj.sentence)
                sentence_list.append(
                    [training_obj_sentence_list, training_obj.no_of_vars])

            response['abc'] = [1, 2, 3]
            response["sentence_list"] = json.dumps(sentence_list)
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("TrainingSentenceAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class InsertFileIntoIntentAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data
            data = json.loads(DecryptVariable(data["data"]))
            intent_id = data["intent_id"]
            tree_id = data["tree_id"]
            parent_id = data["parent_id"]
            file_id_list = data["file_id_list"]

            intent_obj = Intent.objects.get(pk=intent_id, is_hidden=False)

            user_obj = User.objects.get(username=request.user.username)

            easychat_drive_obj_list = []
            for file_id in file_id_list:
                easychat_drive_obj = EasyChatDrive.objects.get(
                    pk=int(file_id), user=user_obj)
                easychat_drive_obj_list.append(easychat_drive_obj)

            bot_response_obj = None
            if str(parent_id) == "-1":
                tree_obj = intent_obj.tree
                bot_response_obj = tree_obj.response
            else:
                tree_obj = Tree.objects.get(pk=int(tree_id))
                bot_response_obj = tree_obj.response

            insert_file_into_intent_from_drive(
                bot_response_obj, easychat_drive_obj_list)
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("InsertFileIntoIntentAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class TriggerIntentAPI(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            response['category'] = None
            response['status'] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("TriggerIntentAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return Response(data=response)


def EnableSmallTalk(request):
    response = {}
    response["status"] = 500
    try:
        if request.user.is_authenticated and request.method == "POST":
            data = DecryptVariable(request.POST["data"])
            data = json.loads(data)
            bot_id = data["bot_id"]
            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            intent_objs = Intent.objects.filter(bots=bot_obj)
            for intent_obj in intent_objs:
                if intent_obj.is_small_talk:
                    intent_obj.is_hidden = False
                    intent_obj.save()
            bot_obj.is_small_talk_disable = False
            bot_obj.save()
            response["status"] = 200
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EnableSmallTalk ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
    custom_encrypt_obj = CustomEncrypt()
    response = custom_encrypt_obj.encrypt(json.dumps(response))
    return HttpResponse(json.dumps(response), content_type="application/json")


def DisableSmallTalk(request):
    response = {}
    response["status"] = 500
    try:
        if request.user.is_authenticated and request.method == "POST":
            data = DecryptVariable(request.POST["data"])
            data = json.loads(data)
            bot_id = data["bot_id"]
            bot_obj = Bot.objects.get(pk=int(bot_id), is_deleted=False)
            intent_objs = Intent.objects.filter(bots=bot_obj)
            for intent_obj in intent_objs:
                if intent_obj.is_small_talk:
                    intent_obj.is_hidden = True
                    intent_obj.save()
            bot_obj.is_small_talk_disable = True
            bot_obj.save()
            response["status"] = 200
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("DisableSmallTalk ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
    custom_encrypt_obj = CustomEncrypt()
    response = custom_encrypt_obj.encrypt(json.dumps(response))
    return HttpResponse(json.dumps(response), content_type="application/json")


class CreateFlowExcelAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = request.data
            uploaded_file = data['my_excel_file']
            intent_id = data["intent_id"]
            try:
                intent_obj = Intent.objects.get(pk=int(intent_id))
            except Exception:
                response["status"] = 300
                response["message"] = "Intent doesn't exist."

            file_validation_obj = EasyChatFileValidation()

            if file_validation_obj.check_malicious_file(uploaded_file.name):
                response["status"] = 101
                response[
                    "message"] = "Kindly upload file in xls or xlsx format. Please do not use .(dot) in filename except for extension."
                return Response(data=response)

            file_name = get_dot_replaced_file_name(uploaded_file.name)
            path = default_storage.save(
                file_name, ContentFile(uploaded_file.read()))

            ext = path.split(".")[-1]
            is_allowed = True
            if ext.lower() not in ["xls", "xlsx"]:
                response["status"] = 101
                response["message"] = "Kindly upload file in xls or xlsx format."
                is_allowed = False

            if is_allowed:

                file_path = settings.MEDIA_ROOT + path
                logger.info(file_path, extra={'AppName': 'EasyChat', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                status, response_message, is_error_in_trees = create_flow_with_excel(
                    file_path, intent_obj)
                logger.info(status, response_message, extra={'AppName': 'EasyChat', 'user_id': str(
                    request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                if status:
                    response["status"] = 200
                    response["message"] = "Your Flow is Created Successfully"
                    if is_error_in_trees:
                        response["message"] = response_message
                else:
                    response["status"] = 300
                    response["status_message"] = response_message
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateFlowExcelAPI %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            response["status"] = 300
            response[
                "status_message"] = "There are some internal issues. Please try again later."
        return Response(data=response)


CreateFlowExcel = CreateFlowExcelAPI.as_view()


class GenerateCampaignLinkAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            if not isinstance(data, dict):
                data = json.loads(data)

            json_string = DecryptVariable(data["json_string"])

            validation_obj = EasyChatInputValidation()

            data = json.loads(json_string)
            intent_pk = data['intent_pk']
            bot_id = data['bot_pk']
            campaign_link = data["campaign_link"]
            campaign_link = validation_obj.remo_html_from_string(campaign_link)
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            bot_objs = Bot.objects.filter(pk=int(bot_id), is_deleted=False)
            if bot_objs.count() > 0:
                bot_obj = bot_objs.first()
                if user_obj in bot_obj.users.all():
                    intent_objs = Intent.objects.filter(pk=int(intent_pk))
                    if intent_objs.count() > 0:
                        intent_obj = intent_objs.first()
                    else:
                        return HttpResponseNotFound("You do not have access to this page")

                    if bot_obj not in intent_obj.bots.all():
                        return HttpResponseNotFound("You do not have access to this page")

                    if not validation_obj.is_valid_url(campaign_link):
                        response["message"] = "Invalid campaign link"
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)

                    campaign_link = campaign_link.strip()
                    if campaign_link == "":
                        response['status'] = 300
                        response["message"] = "Campaign link can not be empty."
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)
                    if len(campaign_link) > 500:
                        response['status'] = 300
                        response[
                            "message"] = "Campaign link should be less than 500 characters."
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)

                    campaign_link = str(campaign_link) + \
                        "?easychat_query=" + intent_pk

                    intent_obj.campaign_link = campaign_link
                    intent_obj.save()
                    response['status'] = 200
                    response["campaign_link"] = campaign_link
                else:
                    response["message"] = "Invalid Bot Id"
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

            else:
                return HttpResponseNotFound("You do not have access to this page")

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GenerateCampaignLinkAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


def resave_intent(intent_objs, start, end):
    for intent_obj in intent_objs[start:end]:
        try:
            intent_obj.save()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("resave_intent ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                                        'source': 'None', 'channel': 'None', 'bot_id': 'None'})


class ResaveAllIntentsAPI (APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500

        try:
            data = request.data
            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)

            bot_id = data['bot_id']

            bot_obj = Bot.objects.filter(pk=int(bot_id), is_deleted=False)
            intent_objs = Intent.objects.filter(
                bots__in=bot_obj, is_deleted=False)

            split_size = len(intent_objs)
            num_splits = 5

            threads = []
            for split_index in range(num_splits):
                start = split_index * split_size
                end = None if split_index + \
                    1 == num_splits else (split_index + 1) * split_size

                threads.append(threading.Thread(
                    target=resave_intent, args=(intent_objs, start, end)))
                threads[-1].start()

            for thread in threads:
                thread.join()

            response['status'] = 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("resave_all_intents ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat',
                                                                                             'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveFormDataAPI(APIView):

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
            user_id = data['user_id']
            form_name = data['form_name']
            form_values = data['form_data']
            bot_id = data["bot_id"]

            bot_obj = Bot.objects.get(pk=bot_id)
            user = Profile.objects.get(user_id=user_id, bot=bot_obj)

            try:
                data_obj = Data.objects.get(user=user, variable=form_name)
                data_obj.value = json.dumps(form_values)
                data_obj.cached_datetime = timezone.now()
                data_obj.is_cache = True
                data_obj.save()
            except Exception:
                data_obj = Data.objects.create(
                    user=user, bot=bot_obj, variable=form_name)
                data_obj.value = json.dumps(form_values)
                data_obj.cached_datetime = timezone.now()
                data_obj.is_cache = True
                data_obj.save()

            intent_obj = MISDashboard.objects.filter(user_id=user_id).exclude(
                intent_recognized=None).first()
            if intent_obj:
                intent_obj = intent_obj.intent_recognized

            FormWidgetDataCollection.objects.create(
                form_name=form_name, form_data=form_values, user_id=user, bot=bot_obj, intent=intent_obj)

            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SaveFormDataAPI ! %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


def DownloadFormDataExcel(request, *args, **kwargs):
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            mis_id = request.GET["pk_of_mis"]
            mis_obj = MISDashboard.objects.get(pk=mis_id)
            form_name_data = json.loads(mis_obj.form_data_widget)
            form_name = form_name_data[0]
            form_data = form_name_data[1]
            from xlwt import Workbook

            automated_email_wb = Workbook()
            sheet1 = automated_email_wb.add_sheet("FormExcel ")
            sheet1.write(0, 0, "UserId")
            sheet1.col(0).width = 256 * 75
            sheet1.write(0, 1, "Timestamp")
            sheet1.col(1).width = 256 * 75
            sheet1.write(0, 2, "Intent")
            iterator = 3
            for key, value in form_data.items():
                sheet1.write(0, iterator, key)

                if isinstance(value, list):
                    file_type = value[0]
                    input_val = value[1]

                    if file_type == 'file_attach':
                        file_src = settings.EASYCHAT_HOST_URL + input_val
                        sheet1.write(1, iterator, file_src)
                    else:
                        sheet1.write(1, iterator, str(input_val))
                else:
                    sheet1.write(1, iterator, str(value))

                iterator = iterator + 1

            sheet1.write(1, 0, mis_obj.user_id)
            sheet1.write(1, 1, mis_obj.get_datetime())
            try:
                sheet1.write(1, 2, FormWidgetDataCollection.objects.filter(
                    form_name=form_name, user_id=Profile.objects.get(user_id=mis_obj.user_id, bot=mis_obj.bot))[0].intent.name)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Download Form Data Excel %s in line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})
                sheet1.write(1, 2, 'None')
                pass
            form_file = "{}_excel_data.xls".format(mis_obj.user_id)
            filename = "files/" + form_file
            automated_email_wb.save(filename)

            response = FileResponse(open(filename, 'rb'))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="' + form_file + '"'
            response['Content-Length'] = os.path.getsize(filename)
            response['status'] = 200
            return response

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Download Form Data Excel %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})
        return render(request, 'EasyChatApp/error_500.html')


def FormWidgetData(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            selected_bot_obj = ""
            bot_objs = ""
            end_date = ""
            start_date = ""
            username = request.user.username
            user_obj = User.objects.get(username=str(username))
            manage_intents_permission = False
            if not check_access_for_user(request.user, None, "Message History Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")

            bot_objs = user_obj.get_related_bot_objs_for_access_type(
                "Message History Related")
            bot_id = None
            if 'bot_id' in request.GET:
                bot_id = request.GET['bot_id']
                selected_bot_obj = Bot.objects.get(pk=bot_id)
                if user_obj not in selected_bot_obj.users.all():
                    return HttpResponseNotFound("You do not have access to this page")

                form_data_list = FormWidgetDataCollection.objects.filter(bot=selected_bot_obj).values(
                    'pk', 'form_name', 'intent_name', 'intent').distinct().order_by('-pk')
                paginator = Paginator(
                    form_data_list, MAX_MESSAGE_PER_PAGE)
                page = request.GET.get('page')

                try:
                    form_data_list = paginator.page(page)
                except PageNotAnInteger:
                    form_data_list = paginator.page(1)
                except EmptyPage:
                    form_data_list = paginator.page(paginator.num_pages)

                end_date = datetime.datetime.now()
                start_date = end_date - datetime.timedelta(30)

            if check_access_for_user(request.user, bot_id, "Intent Related"):
                manage_intents_permission = True

            return render(request, 'EasyChatApp/analytics/form_widget.html', {
                "selected_bot_obj": selected_bot_obj,
                "bot_objs": bot_objs,
                "form_data_list": form_data_list,
                "end_date": end_date,
                "start_date": start_date,
                "manage_intents_permission": manage_intents_permission,
                "bot_id": bot_id
            })
        else:
            return HttpResponseRedirect("/chat/login")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("MessageHistory %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(
            request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
        # return HttpResponseNotFound(INVALID_REQUEST)
        return render(request, 'EasyChatApp/error_500.html')


def DownloadParticularFormConsolidatedUsers(request):
    response = {}
    response["status"] = 500
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            form_widget_pk = request.GET["form_widget_pk"]
            bot_pk = request.GET["bot_id"]
            bot_obj = Bot.objects.filter(pk=bot_pk, users=request.user).first()
            if not bot_obj:
                response["status"] = 401
                response["message"] = "You are not authorised to perform this operation."
            else:
                t1 = threading.Thread(target=send_form_data_csv, args=(
                    form_widget_pk, bot_obj, FormWidgetDataCollection, Bot, request.user.email))
                t1.daemon = True
                t1.start()
                response["status"] = 200
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Download Form Data Excel %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': "None"})
    custom_encrypt_obj = CustomEncrypt()
    response = custom_encrypt_obj.encrypt(json.dumps(response))
    return HttpResponse(json.dumps(response), content_type="application/json")


class GetIntentInformationAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:

            data = request.data
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            json_string = json.loads(json_string)
            intent_pk = json_string["intent_pk"]
            intent_pk = validation_obj.remo_html_from_string(intent_pk)
            bot_id = json_string["bot_id"]
            bot_id = validation_obj.remo_html_from_string(bot_id)

            bot_obj = Bot.objects.get(
                pk=int(bot_id), is_deleted=False)
            intent_obj = Intent.objects.filter(
                pk=int(intent_pk), bots__in=[bot_obj], is_deleted=False, is_hidden=False)[0]

            response['intent_name'] = intent_obj.name
            response["intent_pk"] = intent_obj.pk
            response['status'] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FetchIntentInformationAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class AddIntentIconAPI(APIView):
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

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            json_string = json.loads(json_string)

            intent_pk = json_string["intent_pk"]
            intent_pk = validation_obj.remo_html_from_string(intent_pk)

            icon_src = json_string["icon_src"]
            icon_src = html.escape(icon_src)

            if os.path.exists(settings.BASE_DIR + "/" + icon_src):
                intent_obj = Intent.objects.filter(
                    pk=intent_pk, is_deleted=False).first()
                if intent_obj:
                    intent_obj.intent_icon = icon_src
                    intent_obj.save()
                    response["status"] = 200
                    response["message"] = "Success"
                else:
                    response["message"] = "Intent does not exist."
            else:
                response["message"] = "Invalid path"

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddIntentIconAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class RemoveIntentIconAPI(APIView):
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

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            json_string = json.loads(json_string)

            intent_pk = json_string["intent_pk"]
            intent_pk = validation_obj.remo_html_from_string(intent_pk)

            intent_obj = Intent.objects.filter(
                pk=intent_pk, is_deleted=False).first()

            if intent_obj:
                os.remove(intent_obj.intent_icon[1:])
                intent_obj.intent_icon = None

                if not intent_obj.build_in_intent_icon:
                    default_intent_icon_obj = BuiltInIntentIcon.objects.filter(
                        unique_id=INTENT_ICONS[0][0]).first()

                    if not default_intent_icon_obj:
                        default_intent_icon_obj = BuiltInIntentIcon.objects.create(
                            unique_id=INTENT_ICONS[0][0], icon=INTENT_ICONS[0][1])
                        default_intent_icon_obj.save()

                    intent_obj.build_in_intent_icon = default_intent_icon_obj

                intent_obj.save()
                response["status"] = 200
                response["message"] = "Success"
            else:
                response["message"] = "Intent does not exist."

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RemoveIntentIconAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveBotResponseOfIntentAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.filter(username=str(username)).first()

            bot_objs = get_uat_bots(user_obj)
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            
            response_sentence_list = get_response_sentence_list(json_string)

            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            intent_pk = data["intent_pk"]
            intent_name = str(data['intent_name']).strip()
            intent_name = validation_obj.remo_html_from_string(intent_name)
            intent_name = validation_obj.remo_special_tag_from_string(
                intent_name).strip()

            intent_name_validation_error = False
            if intent_name == "":
                response["status"] = 303
                response["status_message"] = "The provided intent name is incorrect. Only valid text, special characters & emojis can be combined for the intent name."
                intent_name_validation_error = True

            if not intent_name_validation_error and validation_obj.is_string_only_contains_emoji(intent_name):
                response['status'] = 303
                response["status_message"] = "Intent name cannot have only emoji"
                intent_name_validation_error = True

            if not intent_name_validation_error and validation_obj.remo_special_characters_from_string(intent_name) == "":
                response['status'] = 303
                response["status_message"] = "Intent name cannot have only Special Symbols"
                intent_name_validation_error = True     

            if response["status"] == 303:
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            
            if validation_obj.is_string_only_contains_emoji(intent_name):
                response['status'] = 303
                response["status_message"] = "Intent short name cannot have only emoji"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if len(intent_name) > INTENT_TREE_NAME_CHARACTER_LIMIT:
                response['status'] = 303
                response["status_message"] = "Intent Name Cannot Contain More Than 500 Characters"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            training_data = data['training_data']
            selected_bot_pk_list = data['selected_bot_pk_list']
            table_input_list_of_list = data['table_input_list_of_list']
            for iterator1 in range(len(table_input_list_of_list)):
                for iterator2 in range(len(table_input_list_of_list[iterator1])):
                    table_input_list_of_list[iterator1][iterator2] = validation_obj.sanitize_html(
                        table_input_list_of_list[iterator1][iterator2])

            saturated_training_data = []
            for training in training_data:
                training = validation_obj.remo_html_from_string(training)
                training = validation_obj.remo_special_tag_from_string(
                    training)
                training = validation_obj.remo_special_characters_from_string(
                    training).strip()
                if training not in saturated_training_data:
                    saturated_training_data.append(training)

            training_data = saturated_training_data

            common_bot_pk_found = False

            if not common_bot_pk_found:
                # Check whether intent name is already in trainging data or not
                sanatized_intent_name = validation_obj.remo_special_characters_from_string(
                    intent_name).strip()
                if sanatized_intent_name not in training_data:
                    # If not then add value in training data
                    training_data += [sanatized_intent_name]

                # Add intent name to training data after running word mapper if
                # it does not exists
                for bot_pk in selected_bot_pk_list:
                    bot_obj = Bot.objects.filter(
                        pk=int(bot_pk), is_deleted=False).first()

                    word_mapper_sentence = run_word_mapper(
                        WordMapper, str(intent_name), bot_obj, '', '', '')
                    word_mapper_sentence = validation_obj.remo_special_characters_from_string(
                        word_mapper_sentence).strip()
                    if word_mapper_sentence not in training_data:
                        training_data += [word_mapper_sentence]

                bot_pk = selected_bot_pk_list[0]
                bot_obj = Bot.objects.filter(
                    pk=int(bot_pk), is_deleted=False).first()
                if user_obj not in bot_obj.users.all():
                    response["status"] = 302
                    response['message'] = 'You are not authorised to perform this operation.'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
                # Response
                image_list = data["image_list"]
                video_list = data["video_list"]
                card_list = data["card_list"]

                temp_image_list = []
                for image in image_list:
                    if not validation_obj.is_valid_url(image) or image.strip() == "":
                        return Response(data=return_invalid_response(response, "Image link is invalid.", 302))
                    temp_image_list.append(image)

                image_list = temp_image_list

                temp_video_list = []
                for video in video_list:
                    if not validation_obj.is_valid_url(video) or video.strip() == "":
                        return Response(data=return_invalid_response(response, "Video link is invalid.", 302))
                    temp_video_list.append(html.escape(video))

                video_list = temp_video_list

                for card in card_list:
                    card_title = card["title"]
                    card_content = card["content"]
                    card_link = card["link"]
                    card_img_url = card["img_url"]
                    if not validation_obj.is_valid_card_name(card_title) or card_title.strip() == "":
                        return Response(data=return_invalid_response(response, "Card title can only contain alphabets, emojis and special characters (&, $, !, @, ?).", 302))

                    card_content = validation_obj.remo_html_from_string(
                        card_content)
                    card_content = validation_obj.remo_unwanted_security_characters(
                        card_content)
                    if card_content.strip() == "":
                        return Response(data=return_invalid_response(response, "Card content can only contain alphabets.", 302))

                    if not validation_obj.is_valid_url(card_link) or card_link.strip() == "":
                        return Response(data=return_invalid_response(response, "Card redirection link is invalid.", 302))

                    if not validation_obj.is_valid_url(card_img_url) or card_img_url.strip() == "":
                        return Response(data=return_invalid_response(response, "Card image link is invalid.", 302))

                    card["img_url"] = html.escape(card_img_url)
                    card["link"] = html.escape(card_link)

                # Create Training data dict to store into database
                training_data_dict = {}
                for index, sentence in enumerate(training_data):
                    training_data_dict[str(index)] = sentence

                intent_obj = None
                change_data = []
                is_new_intent = True
                is_intent_name_updated = False
                if intent_pk != None and intent_pk != '':
                    intent_obj = Intent.objects.filter(
                        pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False).first()
                    bot_obj = intent_obj.bots.all()[0]

                    is_new_intent = False
                    change_data = add_changes(
                        change_data, intent_obj.name, intent_name, "Intent name")

                    if intent_obj.name != intent_name:
                        intent_obj.synced = False
                        intent_obj.trained = False
                        bot_obj.need_to_build = True
                        is_intent_name_updated = True

                    if is_duplicate_intent_exists(intent_name, bot_obj, intent_obj.pk, intent_obj.channels.all()):
                        return Response(data=return_invalid_response(response, "Intent with same name already exists", 301))

                    intent_obj.name = intent_name
                    hashed_name = get_hashed_intent_name(intent_name, bot_obj)
                    intent_obj.intent_hash = hashed_name
                    change_data = add_changes(change_data, json.loads(
                        intent_obj.training_data), training_data_dict, "Training questions")

                    if json.loads(intent_obj.training_data) != training_data_dict:
                        intent_obj.synced = False
                        intent_obj.trained = False
                        bot_obj.need_to_build = True

                    bot_obj.save()

                    intent_obj.training_data = json.dumps(training_data_dict)

                    for bot_pk in selected_bot_pk_list:
                        bot_obj = Bot.objects.filter(
                            pk=int(bot_pk), is_deleted=False).first()
                        intent_obj.bots.add(bot_obj)
                else:
                    hashed_name = get_hashed_intent_name(intent_name, bot_obj)
                    intent_obj = Intent.objects.create(name=intent_name,
                                                       intent_hash=hashed_name,
                                                       training_data=json.dumps(
                                                           training_data_dict),
                                                       is_feedback_required=False,
                                                       is_part_of_suggestion_list=True,
                                                       # is_livechat_enabled=is_livechat_enabled,
                                                       is_authentication_required=False,
                                                       threshold=1.0,
                                                       is_faq_intent=False)
                    
                    for channel in Channel.objects.filter(is_easychat_channel=True):
                        intent_obj.channels.add(channel)

                    intent_obj.bots.clear()
                    for bot_pk in selected_bot_pk_list:
                        bot_obj = Bot.objects.filter(
                            pk=int(bot_pk), is_deleted=False).first()
                        intent_obj.bots.add(bot_obj)
                        bot_obj.need_to_build = True
                        bot_obj.save()

                    intent_obj.save()

                    audit_trail_data = json.dumps({
                        "intent_pk": intent_obj.pk
                    })

                    save_audit_trail(
                        user_obj, CREATE_INTENT_ACTION, audit_trail_data)

                save_intent_category(data, user_obj, intent_obj, Category, save_audit_trail)
                response_obj = None
                if intent_obj.tree.response == None:
                    response_obj = BotResponse.objects.create()
                else:
                    response_obj = intent_obj.tree.response

                try:
                    previous_tree_sentence = json.loads(
                        response_obj.sentence)["items"][0]
                except Exception:
                    previous_tree_sentence = {"text_response": "", "speech_response": "",
                                              "text_reprompt_response": "", "speech_reprompt_response": "", "tooltip_text": ""}
                    pass
                sentence_json = {
                    "items": []
                }
                for sentence in response_sentence_list:
                    text_response = sentence["text_response"]
                    text_response = validation_obj.clean_html(text_response)
                    speech_response = sentence["speech_response"]
                    speech_response = validation_obj.custom_remo_html_tags(speech_response)
                    speech_response = validation_obj.clean_html(
                        speech_response)
                    hinglish_response = sentence["hinglish_response"]
                    hinglish_response = validation_obj.clean_html(
                        hinglish_response)
                    reprompt_response = sentence["reprompt_response"]
                    reprompt_response = validation_obj.clean_html(
                        reprompt_response)
                    speech_response = speech_response.replace("</p><p>", " ")
                    speech_response = validation_obj.remo_html_from_string(
                        speech_response)
                    ssml_response = sentence["ssml_response"].strip()

                    if speech_response == "":
                        speech_response = text_response.replace("</p><p>", " ")
                        speech_response = validation_obj.remo_html_from_string(
                            speech_response)

                    if reprompt_response == "":
                        reprompt_response = text_response
                    if ssml_response == "":
                        ssml_response = speech_response

                    try:
                        change_data = add_changes(
                            change_data, previous_tree_sentence["text_response"], text_response, "Bot text response")
                        change_data = add_changes(
                            change_data, previous_tree_sentence["speech_response"], speech_response, "Bot speech response")
                        change_data = add_changes(
                            change_data, previous_tree_sentence["hinglish_response"], hinglish_response, "Bot hinglish response")
                        change_data = add_changes(
                            change_data, previous_tree_sentence["reprompt_response"], reprompt_response, "Bot reprompt response")
                        change_data = add_changes(
                            change_data, previous_tree_sentence["ssml_response"], ssml_response, "Bot SSML response")    
                    except Exception:
                        pass

                    speech_response = BeautifulSoup(speech_response).text

                    sentence_json["items"].append({
                        "text_response": text_response,
                        "speech_response": speech_response,
                        "hinglish_response": hinglish_response,
                        "text_reprompt_response": reprompt_response,
                        "speech_reprompt_response": speech_response,
                        "tooltip_response": "",
                        "ssml_response": ssml_response,
                    })

                need_to_show_auto_fix_popup = False
                if not is_new_intent:
                    eng_lang_obj = Language.objects.filter(lang="en").first()
                    activity_update = get_bot_response_activity_update_status(
                        response_obj, sentence, card_list, table_input_list_of_list, eng_lang_obj, LanguageTuningBotResponseTable)
                    
                    if is_intent_name_updated:
                        update_intent_activity_status(intent_obj, activity_update, eng_lang_obj, LanguageTuningIntentTable)
                        update_tree_activity_status(intent_obj.tree, activity_update, eng_lang_obj, LanguageTuningTreeTable)
                    
                    response_obj.activity_update = json.dumps(activity_update)

                    need_to_show_auto_fix_popup = need_to_show_auto_fix_popup_for_intents(
                        intent_obj.tree.response, activity_update, "en", eng_lang_obj, LanguageTuningBotResponseTable)

                response_obj.sentence = json.dumps(sentence_json)
                change_data = add_changes(change_data, json.loads(response_obj.images)[
                                          "items"], image_list, "Images in bot response")
                response_obj.images = json.dumps({"items": image_list})
                change_data = add_changes(change_data, json.loads(response_obj.videos)[
                                          "items"], video_list, "Videos in bot response")
                response_obj.videos = json.dumps({"items": video_list})

                change_data = add_changes(change_data, json.loads(response_obj.cards)[
                                          "items"], card_list, "Cards in bot response")
                response_obj.cards = json.dumps({"items": card_list})
                change_data = add_changes(change_data, json.loads(response_obj.table)[
                                          "items"], table_input_list_of_list, "Table in bot response")
                response_obj.table = json.dumps(
                    {"items": table_input_list_of_list})

                response_obj.save()
                intent_obj.tree.response = response_obj
                intent_obj.tree.name = intent_name
                if Language.objects.filter(lang="en").exists():
                    eng_lang_obj = Language.objects.filter(lang="en").first()
                    update_english_language_tuned_object(
                        eng_lang_obj, intent_obj, response_obj, intent_name, LanguageTuningIntentTable)

                intent_obj.save()          
                intent_obj.tree.save()
                
                if intent_pk != None and intent_pk != '' and len(change_data):
                    audit_trail_data = json.dumps({
                        "intent_pk": intent_obj.pk,
                        "change_data": change_data
                    })
                    save_audit_trail(
                        user_obj, MODIFY_INTENT_ACTION, audit_trail_data)

                response['status'] = 200
                response["intent_pk"] = intent_obj.pk
                response["tree_pk"] = intent_obj.tree.pk
                response["answer_pk"] = intent_obj.tree.response.pk
                response["need_to_build"] = bot_obj.need_to_build
                response["need_to_show_auto_fix_popup"] = need_to_show_auto_fix_popup
                description = "Intent Bot Response Modified"
                add_audit_trail(
                    "EASYCHATAPP",
                    user_obj,
                    "Add-Intent",
                    description,
                    json.dumps(data),
                    request.META.get("PATH_INFO"),
                    request.META.get('HTTP_X_FORWARDED_FOR')
                )
        except DuplicateIntentExceptionError as e:
            response["status"] = 301
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EditBotResponseOfIntentAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EditBotResponseOfIntentAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveIntentIconAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            bot_objs = get_uat_bots(user_obj)
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
        
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            intent_pk = data["intent_pk"]
            selected_bot_pk_list = data['selected_bot_pk_list']
            intent_icon_unique_id = data["intent_icon_unique_id"]

            bot_pk = selected_bot_pk_list[0]
            bot_obj = Bot.objects.filter(
                pk=int(bot_pk), is_deleted=False).first()
            if user_obj not in bot_obj.users.all():
                response["status"] = 302
                response['message'] = 'You are not authorised to perform this operation.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            bot_info_obj = BotInfo.objects.filter(bot=bot_obj).first()

            intent_obj = None
            if intent_pk != None and intent_pk != '':
                intent_obj = Intent.objects.filter(
                    pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False).first()
                
                save_intent_category(data, user_obj, intent_obj, Category, save_audit_trail)
                
                if bot_info_obj.enable_intent_icon:
                    if intent_icon_unique_id != "0":
                        intent_obj.build_in_intent_icon = BuiltInIntentIcon.objects.filter(
                            unique_id=int(intent_icon_unique_id)).first()
                    else:
                        intent_obj.build_in_intent_icon = None

            intent_obj.save()
            response['status'] = 200
            response["intent_pk"] = intent_obj.pk
        
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveIntentIconAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveIntentChannelAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.filter(username=str(username)).first()

            bot_objs = get_uat_bots(user_obj)
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            intent_pk = data["intent_pk"]
            intent_short_name = data['intent_short_name']
            channel_list = data['channel_list']
            whatsapp_short_name = data["whatsapp_short_name"]
            whatsapp_description = data["whatsapp_description"]

            intent_short_name = validation_obj.remo_html_from_string(intent_short_name)
            intent_short_name = validation_obj.remo_special_tag_from_string(intent_short_name)
            intent_short_name = intent_short_name.strip()

            if len(intent_short_name) > 25:
                response['status'] = 303
                response["status_message"] = "Intent short name cannot be more that 25 characters."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            selected_bot_pk_list = data['selected_bot_pk_list']

            common_bot_pk_found = False

            if not common_bot_pk_found:
                bot_pk = selected_bot_pk_list[0]
                bot_obj = Bot.objects.filter(
                    pk=int(bot_pk), is_deleted=False).first()
                if user_obj not in bot_obj.users.all():
                    response["status"] = 302
                    response['message'] = 'You are not authorised to perform this operation.'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                intent_obj = None
                change_data = []
                if intent_pk != None and intent_pk != '':
                    intent_obj = Intent.objects.filter(
                        pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False).first()
                    
                    save_intent_category(data, user_obj, intent_obj, Category, save_audit_trail)
                    
                    for channel in intent_obj.channels.all():
                        if channel.name not in channel_list:
                            change_data.append({
                                "heading": "Removed channel",
                                "old_data": channel.name,
                                "new_data": ""
                            })

                    for channel in channel_list:
                        channel_obj = Channel.objects.filter(
                            name=str(channel)).first()
                        if channel_obj not in intent_obj.channels.all():
                            change_data.append({
                                "heading": "Added channel",
                                "old_data": "",
                                "new_data": channel
                            })
                    intent_obj.remove_all_channel_objects()
                    intent_obj.remove_all_bot_objects()

                    for channel_name in channel_list:
                        channel_obj = Channel.objects.filter(
                            name=str(channel_name)).first()
                        intent_obj.channels.add(channel_obj)
                    
                    for bot_pk in selected_bot_pk_list:
                        bot_obj = Bot.objects.filter(
                            pk=int(bot_pk), is_deleted=False).first()
                        intent_obj.bots.add(bot_obj)
                
                intent_obj.save()
                intent_obj.tree.short_name = intent_short_name
                intent_obj.tree.whatsapp_short_name = whatsapp_short_name
                intent_obj.tree.whatsapp_description = whatsapp_description
                intent_obj.tree.save()
                if intent_pk != None and intent_pk != '' and len(change_data):
                    audit_trail_data = json.dumps({
                        "intent_pk": intent_obj.pk,
                        "change_data": change_data
                    })
                    save_audit_trail(
                        user_obj, MODIFY_INTENT_ACTION, audit_trail_data)
                response['status'] = 200
                response["intent_pk"] = intent_obj.pk

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EditIntentChannelAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveWidgetResponseAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.filter(username=str(username)).first()

            bot_objs = get_uat_bots(user_obj)
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            intent_pk = data["intent_pk"]
            is_attachment_required = data["is_attachment_required"]
            is_save_attachment_required = data["is_save_attachment_required"]
            is_date_picker_allowed = data["is_date_picker_allowed"]
            is_single_date_picker_allowed = data[
                "is_single_date_picker_allowed"]
            is_multi_date_picker_allowed = data["is_multi_date_picker_allowed"]
            is_single_time_picker_allowed = data[
                "is_single_time_picker_allowed"]
            is_multi_time_picker_allowed = data["is_multi_time_picker_allowed"]
            is_time_picker_allowed = data["is_time_picker_allowed"]
            is_calender_picker_allowed = data["is_calender_picker_allowed"]
            is_single_calender_date_picker_allowed = data[
                "is_single_calender_date_picker_allowed"]
            is_multi_calender_date_picker_allowed = data[
                "is_multi_calender_date_picker_allowed"]
            is_single_calender_time_picker_allowed = data[
                "is_single_calender_time_picker_allowed"]
            is_multi_calender_time_picker_allowed = data[
                "is_multi_calender_time_picker_allowed"]
            is_range_slider_required = data["is_range_slider_required"]
            range_slider_type = data["range_slider_type"]
            minimum_range = data["minimum_range"]
            maximum_range = data["maximum_range"]
            is_radio_button_allowed = data["is_radio_button_allowed"]
            radio_button_choices = data["radio_button_choices"]
            is_check_box_allowed = data["is_check_box_allowed"]
            check_box_choices = data["checkbox_choices_list"]
            is_drop_down_allowed = data["is_drop_down_allowed"]
            drop_down_choices = data["dropdown_choices_list"]
            is_video_recorder_allowed = data["is_video_recorder_allowed"]
            is_save_video_attachment = data[
                "is_save_video_attachment_required"]
            choosen_file_type = data["choosen_file_type"]
            is_phone_widget_enabled = data["is_phone_widget_enabled"]
            country_code = data["country_code"]
            is_create_form_allowed = data["is_create_form_allowed"]
            form_name = data["form_name"]
            form_fields_list = data["form_fields_list"]
            selected_bot_pk_list = data['selected_bot_pk_list']
            common_bot_pk_found = False

            if not common_bot_pk_found:
                bot_pk = selected_bot_pk_list[0]
                bot_obj = Bot.objects.filter(
                    pk=int(bot_pk), is_deleted=False).first()
                if user_obj not in bot_obj.users.all():
                    response["status"] = 302
                    response['message'] = 'You are not authorized to perform this operation.'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                intent_obj = None
                change_data = []
                if intent_pk != None and intent_pk != '':
                    intent_obj = Intent.objects.filter(
                        pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False).first()

                    save_intent_category(data, user_obj, intent_obj, Category, save_audit_trail)

                response_obj = None
                if intent_obj.tree.response == None:
                    response_obj = BotResponse.objects.create()
                else:
                    response_obj = intent_obj.tree.response

                modes = json.loads(response_obj.modes)
                modes_param = json.loads(response_obj.modes_param)

                if is_attachment_required:
                    modes["is_attachment_required"] = "true"
                    modes_param["choosen_file_type"] = choosen_file_type
                    change_data = add_changes(
                        change_data, modes_param["choosen_file_type"], choosen_file_type, "Choose attachment type in bot response")
                    if is_save_attachment_required:
                        modes["is_save_attachment_required"] = "true"
                    else:
                        modes["is_save_attachment_required"] = "false"
                else:
                    modes["is_attachment_required"] = "false"
                    change_data = add_changes(
                        change_data, "none", "none", "Choose attachment type in bot response")
                    modes_param["choosen_file_type"] = "none"

                if is_date_picker_allowed:
                    # modes["is_datepicker"] = "true"
                    if is_single_date_picker_allowed:
                        modes["is_single_datepicker"] = "true"
                        modes["is_multi_datepicker"] = "false"
                        modes_param["datepicker_list"] = [
                            {"placeholder": "Date"}]
                    elif is_multi_date_picker_allowed:
                        modes["is_single_datepicker"] = "false"
                        modes["is_multi_datepicker"] = "true"
                        modes_param["datepicker_list"] = [
                            {"placeholder": "From Date"}, {"placeholder": "To Date"}]
                else:
                    modes["is_datepicker"] = "false"
                    modes["is_single_datepicker"] = "false"
                    modes["is_multi_datepicker"] = "false"
                if is_time_picker_allowed:
                    # modes["is_timepicker"] = "true"
                    if is_single_time_picker_allowed:
                        modes["is_single_timepicker"] = "true"
                        modes["is_multi_timepicker"] = "false"
                        modes_param["timepicker_list"] = [
                            {"placeholder": "Time"}]
                    elif is_multi_time_picker_allowed:
                        modes["is_single_timepicker"] = "false"
                        modes["is_multi_timepicker"] = "true"
                        modes_param["timepicker_list"] = [
                            {"placeholder": "From Time"}, {"placeholder": "To Time"}]
                else:
                    modes["is_timepicker"] = "false"
                    modes["is_single_timepicker"] = "false"
                    modes["is_multi_timepicker"] = "false"

                if is_calender_picker_allowed:
                    modes["is_calender"] = "true"
                    if is_single_calender_date_picker_allowed:
                        modes["is_single_datepicker"] = "true"
                        modes["is_multi_datepicker"] = "false"
                        modes_param["datepicker_list"] = [
                            {"placeholder": "Date"}]
                    elif is_multi_calender_date_picker_allowed:
                        modes["is_single_datepicker"] = "false"
                        modes["is_multi_datepicker"] = "true"
                        modes_param["datepicker_list"] = [
                            {"placeholder": "From Date"}, {"placeholder": "To Date"}]
                    else:
                        modes_param["datepicker_list"] = []

                    if is_single_calender_time_picker_allowed:
                        modes["is_single_timepicker"] = "true"
                        modes["is_multi_timepicker"] = "false"
                        modes_param["timepicker_list"] = [
                            {"placeholder": "Time"}]
                    elif is_multi_calender_time_picker_allowed:
                        modes["is_single_timepicker"] = "false"
                        modes["is_multi_timepicker"] = "true"
                        modes_param["timepicker_list"] = [
                            {"placeholder": "From Time"}, {"placeholder": "To Time"}]
                    else:
                        modes_param["timepicker_list"] = []

                else:
                    modes["is_calender"] = "false"

                if is_range_slider_required:
                    modes["is_range_slider"] = "true"
                    modes_param["range_slider_list"] = [
                        {"placeholder": "Select Range", "min": minimum_range, "max": maximum_range, "range_type": range_slider_type}]
                else:
                    modes["is_range_slider"] = "false"

                if is_radio_button_allowed:
                    modes["is_radio_button"] = "true"
                    modes_param["radio_button_choices"] = radio_button_choices
                else:
                    modes["is_radio_button"] = "false"

                if is_check_box_allowed:
                    modes["is_check_box"] = "true"
                    modes_param["check_box_choices"] = check_box_choices
                else:
                    modes["is_check_box"] = "false"

                if is_drop_down_allowed:
                    modes["is_drop_down"] = "true"
                    modes_param["drop_down_choices"] = drop_down_choices
                else:
                    modes["is_drop_down"] = "false"

                if is_video_recorder_allowed:
                    modes["is_video_recorder_allowed"] = "true"
                    if is_save_video_attachment:
                        modes["is_save_video_attachment"] = "true"
                    else:
                        modes["is_save_video_attachment"] = "false"
                else:
                    modes["is_video_recorder_allowed"] = "false"

                if is_phone_widget_enabled:
                    modes["is_phone_widget_enabled"] = "true"
                    modes_param["country_code"] = country_code

                else:
                    modes["is_phone_widget_enabled"] = "false"

                if is_create_form_allowed:
                    modes["is_create_form_allowed"] = "true"
                    modes_param["form_name"] = form_name
                    modes_param["form_fields_list"] = json.dumps(
                        form_fields_list)
                else:
                    modes["is_create_form_allowed"] = "false"

                if intent_pk != None and intent_pk != '' and len(change_data):
                    audit_trail_data = json.dumps({
                        "intent_pk": intent_obj.pk,
                        "change_data": change_data
                    })
                    save_audit_trail(
                        user_obj, MODIFY_INTENT_ACTION, audit_trail_data)

                response_obj.modes = json.dumps(modes)
                response_obj.modes_param = json.dumps(modes_param)
                response_obj.save()
                intent_obj.tree.response = response_obj
                intent_obj.save()              
                intent_obj.tree.save()

                response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveWidgetResponseAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveIntentQuickRecommendationAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.filter(username=str(username)).first()

            bot_objs = get_uat_bots(user_obj)
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            intent_pk = data["intent_pk"]
            selected_bot_pk_list = data['selected_bot_pk_list']
            is_recommendation_menu = data["is_recommendation_menu"]
            common_bot_pk_found = False

            if not common_bot_pk_found:
                bot_pk = selected_bot_pk_list[0]
                bot_obj = Bot.objects.filter(
                    pk=int(bot_pk), is_deleted=False).first()
                if user_obj not in bot_obj.users.all():
                    response["status"] = 302
                    response['message'] = 'You are not authorised to perform this operation.'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                recommended_intent_list = data["recommended_intent_list"]

                intent_obj = None
                change_data = []
                if intent_pk != None and intent_pk != '':
                    intent_obj = Intent.objects.filter(
                        pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False).first()

                    save_intent_category(data, user_obj, intent_obj, Category, save_audit_trail)
                
                response_obj = None
                if intent_obj.tree.response == None:
                    response_obj = BotResponse.objects.create()
                else:
                    response_obj = intent_obj.tree.response

                if json.loads(response_obj.recommendations)["items"] != recommended_intent_list:
                    old_data_list = []

                    for item in json.loads(response_obj.recommendations)["items"]:
                        old_data_list.append(
                            Intent.objects.filter(pk=int(item)).first().name)

                    new_data_list = []

                    for item in recommended_intent_list:
                        new_data_list.append(
                            Intent.objects.filter(pk=int(item)).first().name)

                    change_data.append({
                        "heading": "Quick recommendations in bot response",
                        "old_data": old_data_list,
                        "new_data": new_data_list
                    })
                response_obj.recommendations = json.dumps(
                    {"items": recommended_intent_list})

                modes = json.loads(response_obj.modes)
                modes_param = json.loads(response_obj.modes_param)

                if is_recommendation_menu:
                    modes["is_recommendation_menu"] = "true"
                else:
                    modes["is_recommendation_menu"] = "false"

                response_obj.modes = json.dumps(modes)
                response_obj.modes_param = json.dumps(modes_param)
                response_obj.save()
                intent_obj.tree.response = response_obj
                intent_obj.save()
                intent_obj.tree.save()

                if intent_pk != None and intent_pk != '' and len(change_data):
                    audit_trail_data = json.dumps({
                        "intent_pk": intent_obj.pk,
                        "change_data": change_data
                    })
                    save_audit_trail(
                        user_obj, MODIFY_INTENT_ACTION, audit_trail_data)
                response['status'] = 200
                response["intent_pk"] = intent_obj.pk
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveIntentQuickRecommendationAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveIntentOrderOfResponseAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.filter(username=str(username)).first()

            bot_objs = get_uat_bots(user_obj)
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            intent_pk = data["intent_pk"]
            selected_bot_pk_list = data['selected_bot_pk_list']
            is_custom_order_selected = data["is_custom_order_selected"]
            order_of_response = data["order_of_response"]

            common_bot_pk_found = False

            if not common_bot_pk_found:
                bot_pk = selected_bot_pk_list[0]
                bot_obj = Bot.objects.filter(
                    pk=int(bot_pk), is_deleted=False).first()
                if user_obj not in bot_obj.users.all():
                    response["status"] = 302
                    response['message'] = 'You are not authorised to perform this operation.'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)
                
                intent_obj = None
                change_data = []
                if intent_pk != None and intent_pk != '':
                    intent_obj = Intent.objects.filter(
                        pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False).first()

                    save_intent_category(data, user_obj, intent_obj, Category, save_audit_trail)
                    
                    change_data = add_changes(
                        change_data, intent_obj.order_of_response, order_of_response, "Order of response")
                    intent_obj.order_of_response = json.dumps(
                        order_of_response)
                    change_data = add_changes(
                        change_data, intent_obj.is_custom_order_selected, is_custom_order_selected, "Is custom order selected")
                    intent_obj.is_custom_order_selected = is_custom_order_selected
                
                if intent_pk != None and intent_pk != '' and len(change_data):
                    audit_trail_data = json.dumps({
                        "intent_pk": intent_obj.pk,
                        "change_data": change_data
                    })
                    save_audit_trail(
                        user_obj, MODIFY_INTENT_ACTION, audit_trail_data)

                intent_obj.is_custom_order_selected = is_custom_order_selected
                intent_obj.order_of_response = json.dumps(order_of_response)

                intent_obj.save()

                response['status'] = 200
                response["intent_pk"] = intent_obj.pk
        
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveIntentOrderOfResponseAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveIntentConversionFlowDescriptionAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.filter(username=str(username)).first()

            bot_objs = get_uat_bots(user_obj)
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            explanation = data["explanation"]
            intent_pk = data["intent_pk"]

            selected_bot_pk_list = data['selected_bot_pk_list']

            common_bot_pk_found = False

            if not common_bot_pk_found:
                bot_pk = selected_bot_pk_list[0]
                bot_obj = Bot.objects.filter(
                    pk=int(bot_pk), is_deleted=False).first()
                if user_obj not in bot_obj.users.all():
                    response["status"] = 302
                    response['message'] = 'You are not authorized to perform this operation.'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                intent_obj = None
                if intent_pk != None and intent_pk != '':
                    intent_obj = Intent.objects.filter(
                        pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False).first()

                    save_intent_category(data, user_obj, intent_obj, Category, save_audit_trail)
                
                explanation_obj = None
                if intent_obj.tree.explanation == None:
                    explanation_obj = Explanation.objects.create()

                else:
                    explanation_obj = intent_obj.tree.explanation

                explanation_obj.explanation = explanation
                explanation_obj.save()
                intent_obj.tree.explanation = explanation_obj

                response_obj = None
                if intent_obj.tree.response == None:
                    response_obj = BotResponse.objects.create()
                else:
                    response_obj = intent_obj.tree.response
                
                intent_obj.tree.response = response_obj
                intent_obj.save()
                intent_obj.tree.save()

                response['status'] = 200
                response["intent_pk"] = intent_obj.pk
        
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveIntentConversionFlowDescriptionAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)
       

class SaveIntentAdvanceNlpConfigAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.filter(username=str(username)).first()

            bot_objs = get_uat_bots(user_obj)
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            intent_pk = data["intent_pk"]
            necessary_keywords = data["necessary_keywords"]
            restricted_keywords = data["restricted_keywords"]
            intent_threshold = data["intent_threshold"]
            selected_bot_pk_list = data['selected_bot_pk_list']
            common_bot_pk_found = False

            if not common_bot_pk_found:
                bot_pk = selected_bot_pk_list[0]
                bot_obj = Bot.objects.filter(
                    pk=int(bot_pk), is_deleted=False).first()
                if user_obj not in bot_obj.users.all():
                    response["status"] = 302
                    response['message'] = 'You are not authorised to perform this operation.'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                intent_obj = None
                if intent_pk != None and intent_pk != '':
                    intent_obj = Intent.objects.filter(
                        pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False).first()

                    save_intent_category(data, user_obj, intent_obj, Category, save_audit_trail)
                    
                    bot_obj.save()
                
                if necessary_keywords != "None":
                    intent_obj.necessary_keywords = necessary_keywords.lower()

                if restricted_keywords != "None":
                    intent_obj.restricted_keywords = restricted_keywords.lower()

                if intent_threshold != "None":
                    intent_obj.threshold = float(intent_threshold)

                intent_obj.save()
                intent_obj.tree.save()

                response['status'] = 200
                response["intent_pk"] = intent_obj.pk

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveIntentAdvanceNlpConfigAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveIntentSettingsAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.filter(username=str(username)).first()

            bot_objs = get_uat_bots(user_obj)
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)
            intent_pk = data["intent_pk"]
            is_feedback_required = data["is_feedback_required"]
            is_part_of_suggestion_list = data["is_part_of_suggestion_list"]
            is_authentication_required = data["is_authentication_required"]
            is_child_intent_visible = data["is_child_intent_visible"]
            is_small_talk = data["is_small_talk"]
            authentication_id = data["authentication_id"]
            authentication_id = validation_obj.remo_html_from_string(
                str(authentication_id))
            selected_bot_pk_list = data['selected_bot_pk_list']
            is_automatic_recursion_enabled = data[
                'is_automate_recursion_enabled']
            post_processor_variable = data['post_processor_variable']
            is_go_back_enabled = data["is_go_back_enabled"]
            is_catalogue_added = data["is_catalogue_added"]
            selected_catalogue_sections = data["selected_catalogue_sections"]
            if selected_catalogue_sections is None:
                selected_catalogue_sections = []
            is_catalogue_purchased = data["is_catalogue_purchased"]
            if user_obj.is_staff:
                flow_analytics_variable = data["flow_analytics_variable"]
                is_category_response_allowed = data[
                    "is_category_intent_allowed"]
            is_last_tree = data["is_last_tree"]
            is_exit_tree = data["is_exit_tree"]
            is_transfer_tree = data["is_transfer_tree"]
            allow_barge = data["allow_barge"]
            is_faq_intent = data["is_faq_intent"]
            disposition_code = data["disposition_code"]
            child_choices = data["child_choices"]

            common_bot_pk_found = False

            if not common_bot_pk_found:
                bot_pk = selected_bot_pk_list[0]
                bot_obj = Bot.objects.filter(
                    pk=int(bot_pk), is_deleted=False).first()
                if user_obj not in bot_obj.users.all():
                    response["status"] = 302
                    response['message'] = 'You are not authorised to perform this operation.'
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                validator_id = data["validator_id"]
                validator_id = validation_obj.remo_html_from_string(
                    validator_id)
                authentication_obj = None
                authentication_name = None
                try:
                    authentication_obj = Authentication.objects.filter(
                        pk=int(authentication_id)).first()
                    authentication_name = authentication_obj.name
                except Exception:  # noqa: F841
                    pass

                intent_obj = None
                change_data = []
                if intent_pk != None and intent_pk != '':
                    intent_obj = Intent.objects.filter(
                        pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False).first()

                    save_intent_category(data, user_obj, intent_obj, Category, save_audit_trail)
                    
                    bot_obj = intent_obj.bots.all()[0]
                    change_data = add_changes(
                        change_data, intent_obj.is_feedback_required, is_feedback_required, "Feedback required")
                    intent_obj.is_feedback_required = is_feedback_required
                    change_data = add_changes(change_data, intent_obj.is_part_of_suggestion_list,
                                              is_part_of_suggestion_list, "Make intent part of suggestion list")
                    intent_obj.is_part_of_suggestion_list = is_part_of_suggestion_list
                    change_data = add_changes(
                        change_data, intent_obj.is_authentication_required, is_authentication_required, "Authentication required")
                    intent_obj.is_authentication_required = is_authentication_required
                    change_data = add_changes(
                        change_data, intent_obj.is_small_talk, is_small_talk, "Make intent as part of small talks")
                    intent_obj.is_small_talk = is_small_talk
                    if user_obj.is_staff:
                        intent_obj.is_category_response_allowed = is_category_response_allowed
                    if intent_obj.auth_type != None:
                        change_data = add_changes(
                            change_data, intent_obj.auth_type.name, authentication_name, "Auth type")
                    elif intent_obj.auth_type == None and authentication_obj != None:
                        change_data = add_changes(
                            change_data, None, authentication_name, "Added auth type")
                    intent_obj.auth_type = authentication_obj
                    change_data = add_changes(
                        change_data, intent_obj.is_faq_intent, is_faq_intent, "Is intent marked as FAQ Intent")
                    intent_obj.is_faq_intent = is_faq_intent

                if is_child_intent_visible != "None":
                    if intent_obj.tree.is_child_tree_visible != is_child_intent_visible and is_child_intent_visible:
                        intent_obj.tree.is_child_tree_visible = is_child_intent_visible
                        check_and_update_whatsapp_menu_objs(intent_obj.tree)

                    intent_obj.tree.is_child_tree_visible = is_child_intent_visible
                    intent_obj.tree.save()

                if user_obj.is_staff:
                    if is_category_response_allowed:
                        intent_obj.tree.is_child_tree_visible = False
                        intent_obj.tree.save()

                response_obj = None
                if intent_obj.tree.response == None:
                    response_obj = BotResponse.objects.create()
                else:
                    response_obj = intent_obj.tree.response

                if child_choices != []:
                    if len(intent_obj.tree.children.all()) != len(child_choices):
                        response_obj.save()
                        response["status"] = 401
                        custom_encrypt_obj = CustomEncrypt()
                        response = custom_encrypt_obj.encrypt(
                            json.dumps(response))
                        return Response(data=response)
                    else:
                        response_obj.choices.all().delete()
                        for choices in child_choices:
                            choice_obj = Choice.objects.create(
                                value=choices, display=choices)
                            response_obj.choices.add(choice_obj)
                        response["trigger_flow_change"] = True
                else:
                    response_obj.choices.all().delete()

                modes = json.loads(response_obj.modes)
                modes_param = json.loads(response_obj.modes_param)
                modes["is_catalogue_added"] = "true" if is_catalogue_added else "false"
                modes_param["selected_catalogue_sections"] = selected_catalogue_sections

                response_obj.modes = json.dumps(modes)
                response_obj.modes_param = json.dumps(modes_param)
                response_obj.save()
                intent_obj.tree.response = response_obj

                intent_obj.tree.is_automatic_recursion_enabled = is_automatic_recursion_enabled

                if(validator_id != None and validator_id != ""):
                    validator_obj = Processor.objects.filter(pk=int(validator_id)).first()
                    intent_obj.tree.post_processor = validator_obj
                else:

                    # if there is a previously assigned post_processor, keeping
                    # it as it is in case of no validator being selected from
                    # console.

                    if not ProcessorValidator.objects.filter(processor=intent_obj.tree.post_processor).count():
                        if(post_processor_variable != ""):
                            if intent_obj.tree.post_processor != None and intent_obj.tree.post_processor.name == "PostProcessor_" + str(post_processor_variable):
                                pass
                            else:
                                code = "from EasyChatApp.utils import logger\nimport sys\ndef f(x):\n    json_response = {}\n    json_response['status_code'] = '500'\n    json_response['status_message'] = 'Internal server error.'\n    json_response['data'] = {}\n    try:\n        json_response['data']['" + post_processor_variable + \
                                    "']=x\n        #write your code here\n        json_response['status_code'] = '200'\n        json_response['print'] = 'Hello world!'\n        return json_response\n    except Exception as E:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('PostProcessorContent: %s at %s',str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        json_response['status_code'] = '500'\n        json_response['status_message'] = 'ERROR :-  '+str(E)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return json_response"
                                processor_obj = Processor.objects.create(name="PostProcessor_" + str(
                                    post_processor_variable), function=code, post_processor_direct_value=post_processor_variable)
                                intent_obj.tree.post_processor = processor_obj

                    else:
                        intent_obj.tree.post_processor = None

                intent_obj.tree.is_go_back_enabled = is_go_back_enabled
                intent_obj.tree.save()
                if user_obj.is_staff:
                    intent_obj.tree.flow_analytics_variable = flow_analytics_variable
                    intent_obj.tree.save()

                intent_obj.save()

                intent_obj.tree.is_last_tree = is_last_tree
                intent_obj.tree.is_exit_tree = is_exit_tree
                intent_obj.tree.enable_transfer_agent = is_transfer_tree
                intent_obj.tree.disposition_code = disposition_code
                intent_obj.tree.is_catalogue_purchased = is_catalogue_purchased

                voice_bot_conf = json.loads(intent_obj.tree.voice_bot_conf)
                voice_bot_conf["barge_in"] = allow_barge
                intent_obj.tree.voice_bot_conf = json.dumps(voice_bot_conf)
                
                intent_obj.tree.save()

                if intent_pk != None and intent_pk != '' and len(change_data):
                    audit_trail_data = json.dumps({
                        "intent_pk": intent_obj.pk,
                        "change_data": change_data
                    })
                    save_audit_trail(
                        user_obj, MODIFY_INTENT_ACTION, audit_trail_data)

                response['status'] = 200
                response["intent_pk"] = intent_obj.pk

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveIntentSettingsAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveIntentWhatsappMenuFormatAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data
            username = request.user.username
            user_obj = User.objects.get(username=str(username))

            bot_objs = get_uat_bots(user_obj)
            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
        
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            intent_pk = data["intent_pk"]
            selected_bot_pk_list = data['selected_bot_pk_list']
            enable_whatsapp_menu_format = data["enable_whatsapp_menu_format"]
            whatsapp_list_message_header = data["whatsapp_list_message_header"]

            bot_pk = selected_bot_pk_list[0]
            bot_obj = Bot.objects.filter(
                pk=int(bot_pk), is_deleted=False).first()
            if user_obj not in bot_obj.users.all():
                response["status"] = 302
                response['message'] = 'You are not authorised to perform this operation.'
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            intent_obj = None
            if intent_pk != None and intent_pk != '':
                intent_obj = Intent.objects.filter(
                    pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False).first()
                
                save_intent_category(data, user_obj, intent_obj, Category, save_audit_trail)
                
                intent_obj.tree.enable_whatsapp_menu_format = enable_whatsapp_menu_format
                if enable_whatsapp_menu_format and intent_obj.tree.response:
                    response_obj = intent_obj.tree.response
                    response_obj.whatsapp_list_message_header = whatsapp_list_message_header
                    response_obj.save(update_fields=["whatsapp_list_message_header"])

            intent_obj.tree.save(update_fields=["enable_whatsapp_menu_format"])
            response['status'] = 200
            response["intent_pk"] = intent_obj.pk
        
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveIntentWhatsappMenuFormatAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


GenerateCampaignLink = GenerateCampaignLinkAPI.as_view()
InsertFileIntoIntent = InsertFileIntoIntentAPI.as_view()
FetchAllIntents = FetchAllIntentsAPI.as_view()
DeleteIntent = DeleteIntentAPI.as_view()
SaveIntent = SaveIntentAPI.as_view()
AddTrainingQuestions = AddTrainingQuestionsAPI.as_view()
FetchIntentInformation = FetchIntentInformationAPI.as_view()
FetchIntentTreeStructure = FetchIntentTreeStructureAPI.as_view()
GetTrainingData = GetTrainingDataAPI.as_view()
TrainingSentence = TrainingSentenceAPI.as_view()
TriggerIntent = TriggerIntentAPI.as_view()
GetIntentNames = GetIntentNames.as_view()
ResaveAllIntents = ResaveAllIntentsAPI.as_view()
SaveFormData = SaveFormDataAPI.as_view()
GetIntentInformation = GetIntentInformationAPI.as_view()
AddIntentIcon = AddIntentIconAPI.as_view()
RemoveIntentIcon = RemoveIntentIconAPI.as_view()
SaveBotResponseOfIntent = SaveBotResponseOfIntentAPI.as_view()
SaveIntentIcon = SaveIntentIconAPI.as_view()
SaveIntentChannel = SaveIntentChannelAPI.as_view()
SaveWidgetResponse = SaveWidgetResponseAPI.as_view()
SaveIntentQuickRecommendation = SaveIntentQuickRecommendationAPI.as_view()
SaveIntentOrderOfResponse = SaveIntentOrderOfResponseAPI.as_view()
SaveIntentConversionFlowDescription = SaveIntentConversionFlowDescriptionAPI.as_view()
SaveIntentAdvanceNlpConfig = SaveIntentAdvanceNlpConfigAPI.as_view()
SaveIntentSettings = SaveIntentSettingsAPI.as_view()
SaveIntentWhatsappMenuFormat = SaveIntentWhatsappMenuFormatAPI.as_view()
