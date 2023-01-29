from EasyChatApp.utils_validation import EasyChatInputValidation
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication

from django.http import HttpResponseNotFound
from django.shortcuts import render, HttpResponseRedirect

from EasyChatApp.models import *
from EasyTMSApp.models import TicketCategory
from EasyChatApp.utils import *
from EasyChatApp.utils_analytics import *
from EasyChatApp.utils_bot import check_and_update_tunning_tree_object, need_to_show_auto_fix_popup_for_intents, recurse_tree_save, save_intent_category
from EasyChatApp.utils_voicebot import get_selected_tts_provider_name
from EasyChatApp.utils_translation_module import translate_given_text_to_english
from EasyChatApp.utils_channels import check_and_update_whatsapp_menu_objs

import sys
import json
import logging


logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def EditTreeConsole(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Intent Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            selected_bot_obj = None
            intent_obj = None
            parent_obj = None
            tree_obj = None
            try:
                intent_pk = request.GET['intent_pk']
                parent_pk = request.GET['parent_pk']
                tree_pk = request.GET['tree_pk']

                selected_language = "en"

                if "selected_language" in request.GET:
                    selected_language = request.GET["selected_language"]

                if int(parent_pk) == -1:
                    return HttpResponseRedirect("/chat/edit-intent/?intent_pk=" + str(intent_pk) + "&selected_language=" + selected_language)

                if selected_language != "en":
                    return HttpResponseRedirect("/chat/edit-tree-multilingual/?intent_pk=" + str(intent_pk) + "&parent_pk=" + parent_pk + "&tree_pk=" + tree_pk + "&selected_language=" + selected_language)

                intent_obj = Intent.objects.get(
                    pk=int(intent_pk), is_hidden=False)
                parent_obj = Tree.objects.get(
                    pk=int(parent_pk), is_deleted=False)
                tree_obj = Tree.objects.get(pk=int(tree_pk), is_deleted=False)
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("EditTreeConsole: %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                # return HttpResponseNotFound("<h1>No Page found</h1>")
                return render(request, 'EasyChatApp/error_404.html')

            if intent_obj != None and parent_obj != None and tree_obj != None:

                selected_bot_obj = intent_obj.bots.all()[0]
                is_attachment_required = False
                selected_file_type = []

                languages_supported = Config.objects.all()[
                    0].languages_supported.all()

                language_supported = []

                for language in languages_supported:
                    language_supported.append(language.lang)

                hindi_supported = False
                if 'hi' in language_supported:
                    hindi_supported = True

                multilingual_tree_name = ""
                if hindi_supported:
                    multilingual_tree_name = tree_obj.multilingual_name

                table_list_of_list = None
                rows = 0
                columns = 0

                is_save_attachment_required = False
                is_date_picker_allowed = False
                is_single_date_picker_allowed = False
                is_multi_date_picker_allowed = False
                is_time_picker_allowed = False
                is_single_time_picker_allowed = False
                is_multi_time_picker_allowed = False
                is_calender_picker_allowed = False
                is_single_calender_date_picker_allowed = False
                is_multi_calender_date_picker_allowed = False
                is_single_calender_time_picker_allowed = False
                is_multi_calender_time_picker_allowed = False
                is_range_slider_required = False
                minimum_range = 0
                maximum_range = 0
                range_slider_type = ""
                is_radio_button_allowed = False
                radio_button_choices_list = []
                is_check_box_allowed = False
                check_box_choices_list = []
                is_drop_down_allowed = False
                drop_down_choices_list = []
                is_video_recorder_allowed = False
                is_phone_widget_enabled = False
                country_code = "in"
                is_save_video_attachment = False
                is_recommendation_menu = False
                is_catalogue_added = False
                is_create_form_allowed = False
                form_fields_list = []
                form_name = ""

                is_catalogue_purchased = False
                if tree_obj.response == None:
                    is_attachment_required = False
                    selected_file_type = "none"
                else:
                    modes = json.loads(tree_obj.response.modes)
                    modes_param = json.loads(tree_obj.response.modes_param)

                    table_list_of_list = tree_obj.response.table
                    if table_list_of_list != '{"items": []}':
                        rows = len(json.loads(table_list_of_list)["items"])
                        if rows > 0:
                            columns = len(json.loads(
                                table_list_of_list)["items"][0])
                        else:
                            columns = 0

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
                        elif "is_multi_datepicker" in modes and str(modes["is_multi_datepicker"]) == "true":
                            is_single_calender_date_picker_allowed = False
                            is_multi_calender_date_picker_allowed = True
                        if "is_single_timepicker" in modes and str(modes["is_single_timepicker"]) == "true":
                            is_single_calender_time_picker_allowed = True
                            is_multi_calender_time_picker_allowed = False
                        elif "is_multi_timepicker" in modes and str(modes["is_multi_timepicker"]) == "true":
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
                        check_box_choices_list = modes_param[
                            "check_box_choices"]
                    else:
                        is_check_box_allowed = False
                        check_box_choices_list = []

                    is_drop_down_allowed = False
                    drop_down_choices_list = []
                    if "is_drop_down" in modes and str(modes["is_drop_down"]) == "true":
                        is_drop_down_allowed = True
                        drop_down_choices_list = modes_param[
                            "drop_down_choices"]
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

                    is_recommendation_menu = False
                    if "is_recommendation_menu" in modes and str(modes["is_recommendation_menu"]) == "true":
                        is_recommendation_menu = True
                    else:
                        is_recommendation_menu = False

                    if "is_catalogue_added" in modes and str(modes["is_catalogue_added"]) == "true":
                        is_catalogue_added = True
                    else:
                        is_catalogue_added = False

                    is_catalogue_purchased = tree_obj.is_catalogue_purchased

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
                    logger.error("EditTreeConsole: %s at %s",
                                 str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                recommendation_list = []

                if tree_obj != None and tree_obj.response != None:
                    recommendation_list = json.loads(
                        tree_obj.response.recommendations)["items"]

                is_go_back_enabled = tree_obj.is_go_back_enabled
                is_confirmation_and_reset_enabled = tree_obj.is_confirmation_and_reset_enabled
                selected_bot_pk_list = list(
                    intent_obj.bots.values_list("pk", flat=True))

                intent_pk_list = list(
                    Intent.objects.filter(bots__in=selected_bot_pk_list, is_deleted=False, is_hidden=False).distinct().values_list("pk", flat=True))

                modified_intent_list = []
                for intent_pk in recommendation_list:
                    try:
                        small_talk = Intent.objects.get(
                            pk=int(intent_pk), is_hidden=False).is_small_talk
                        if small_talk == False:
                            modified_intent_list.append({
                                "is_selected": True,
                                "intent_name": Intent.objects.get(pk=int(intent_pk), is_hidden=False).name,
                                "intent_pk": intent_pk
                            })
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("EditTreeConsole: %s at %s",
                                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        pass

                for intent_pk in intent_pk_list:
                    if str(intent_pk) not in recommendation_list:
                        small_talk = Intent.objects.get(
                            pk=int(intent_pk), is_hidden=False).is_small_talk
                        if small_talk == False:
                            modified_intent_list.append({
                                "is_selected": False,
                                "intent_name": Intent.objects.get(pk=int(intent_pk), is_hidden=False).name,
                                "intent_pk": intent_pk
                            })

                tag_mapper_objs = get_tag_mapper_list_for_given_user(request)
                if table_list_of_list == None:
                    table_list_of_list = json.dumps({"items": []})

                validators = ProcessorValidator.objects.filter(
                    bot=selected_bot_obj)
                post_processor_variable = ""
                selected_validator_obj = None

                if tree_obj.post_processor:
                    processor_obj = tree_obj.post_processor
                    post_processor_variable = processor_obj.post_processor_direct_value
                    if len(ProcessorValidator.objects.filter(processor=processor_obj)) != 0:
                        selected_validator_obj = ProcessorValidator.objects.filter(
                            processor=processor_obj)[0]

                if tree_obj.explanation == None:
                    explanation = ""
                else:
                    explanation = tree_obj.explanation.explanation

                radio_button_choices_value = ""
                for value in radio_button_choices_list:
                    radio_button_choices_value += str(value) + "_"

                check_box_choices_value = ""
                for value in check_box_choices_list:
                    check_box_choices_value += str(value) + "_"

                drop_down_choices_value = ""
                for value in drop_down_choices_list:
                    drop_down_choices_value += str(value) + "_"

                is_automatic_recursion_enabled = tree_obj.is_automatic_recursion_enabled

                pipe_processor_tree_name = ""
                api_tree_name = ""
                post_processor_tree_name = ""
                if tree_obj.pipe_processor:
                    pipe_processor_tree_name = ": " + tree_obj.pipe_processor.name
                if tree_obj.api_tree:
                    api_tree_name = ": " + tree_obj.api_tree.name
                if tree_obj.post_processor:
                    post_processor_tree_name = ": " + tree_obj.post_processor.name

                tree_children_list = []

                tree_children = tree_obj.children.all()

                for children in tree_children:
                    tree_children_list.append(children.name)

                child_choices_list = []
                need_to_show_auto_fix_popup = False
                if tree_obj != None and tree_obj.response != None:
                    child_choices = tree_obj.response.choices.all()

                    for choice in child_choices:
                        child_choices_list.append(choice.value)
                    eng_lang_obj = None
                    if Language.objects.filter(lang="en"):
                        eng_lang_obj = Language.objects.get(lang="en")
                    activity_update = json.loads(
                        tree_obj.response.activity_update)
                    need_to_show_auto_fix_popup = need_to_show_auto_fix_popup_for_intents(
                        tree_obj.response, activity_update, selected_language, eng_lang_obj, LanguageTuningBotResponseTable)

                if child_choices_list != [] and tree_children_list != child_choices_list:
                    choices_order_changed = True
                else:
                    choices_order_changed = False

                flow_analytics_variable = tree_obj.flow_analytics_variable
                required_analytics_variable = False
                if flow_analytics_variable != "":
                    required_analytics_variable = True

                is_custom_order_selected = tree_obj.is_custom_order_selected
                order_of_response = tree_obj.order_of_response

                is_last_tree = tree_obj.is_last_tree
                is_exit_tree = tree_obj.is_exit_tree
                is_exit_tree = tree_obj.is_exit_tree
                is_transfer_tree = tree_obj.enable_transfer_agent

                whatsapp_list_message_header = "Options"
                if tree_obj.response:
                    whatsapp_list_message_header = tree_obj.response.whatsapp_list_message_header

                intent_channel_list = intent_obj.channels.values_list("name", flat=True)

                selected_tts_provider = get_selected_tts_provider_name(
                    selected_bot_obj, BotChannel)

                whatsapp_channel_obj = Channel.objects.filter(name="WhatsApp").first()

                selected_child_trees = []
                selected_main_intents = []

                whatsapp_menu_sections = WhatsAppMenuSection.objects.filter(tree=tree_obj)

                for whatsapp_menu_section in whatsapp_menu_sections:
                    if whatsapp_menu_section.child_trees:
                        selected_child_trees += json.loads(whatsapp_menu_section.child_trees)
                    if whatsapp_menu_section.main_intents:
                        selected_main_intents += json.loads(whatsapp_menu_section.main_intents)

                unselected_child_trees = tree_obj.children.filter(is_deleted=False).filter(~Q(pk__in=selected_child_trees))
                if tree_obj.children.filter(is_deleted=False).count() == 1 or not tree_obj.is_child_tree_visible:
                    unselected_child_trees = []
                unselected_main_intents = Intent.objects.filter(bots=selected_bot_obj, channels=whatsapp_channel_obj, is_deleted=False, is_hidden=False, is_small_talk=False).filter(~Q(pk__in=selected_main_intents))

                whatsapp_menu_section_objs_list = WhatsAppMenuSection.objects.filter(tree=tree_obj).order_by("pk")
                whatsapp_menu_section_objs = []
                for whatsapp_menu_section_obj in whatsapp_menu_section_objs_list:
                    whatsapp_menu_section_data = {}
                    whatsapp_menu_section_data["pk"] = whatsapp_menu_section_obj.pk
                    whatsapp_menu_section_data["title"] = whatsapp_menu_section_obj.title
                    whatsapp_menu_section_data["child_tree_details"] = whatsapp_menu_section_obj.get_child_tree_details()
                    whatsapp_menu_section_data["main_intent_details"] = whatsapp_menu_section_obj.get_main_intent_details()
                    whatsapp_menu_section_objs.append(whatsapp_menu_section_data)

                whatsapp_quick_recommendations_allowed = 10

                if tree_obj.is_child_tree_visible and tree_obj.children.filter(is_deleted=False).count() > 1:
                    whatsapp_quick_recommendations_allowed = 10 - tree_obj.children.filter(is_deleted=False).count()
                    if whatsapp_quick_recommendations_allowed < 0:
                        whatsapp_quick_recommendations_allowed = 0

                return render(request, 'EasyChatApp/platform/edit_tree.html', {
                    "intent_name_list": modified_intent_list,
                    "tree_name": str(tree_obj.name),
                    "tree_short_name": str(tree_obj.short_name),
                    "tree_short_name_enabled": 'GoogleBusinessMessages' in intent_channel_list,
                    "is_category_response_allowed": tree_obj.is_category_response_allowed,
                    "multilingual_tree_name": str(multilingual_tree_name),
                    "is_attachment_required": is_attachment_required,
                    "all_file_type": all_file_type,
                    "accept_keywords": str(tree_obj.accept_keywords),
                    "tag_mapper_objs": tag_mapper_objs,
                    "is_child_tree_visible": tree_obj.is_child_tree_visible,
                    "table_list_of_list": table_list_of_list,
                    "rows": rows,
                    "columns": columns,
                    "validators": validators,
                    "selected_validator_obj": selected_validator_obj,
                    "selected_bot_obj": selected_bot_obj,
                    "tree_pk": tree_pk,
                    "hindi_supported": hindi_supported,
                    "explanation": explanation,
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
                    "is_save_attachment_required": is_save_attachment_required,
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
                    "is_automatic_recursion_enabled": is_automatic_recursion_enabled,
                    "is_go_back_enabled": is_go_back_enabled,
                    "show_go_back_checkbox": bool(tree_obj.children.filter(is_deleted=False)),
                    "is_confirmation_and_reset_enabled": is_confirmation_and_reset_enabled,
                    "is_recommendation_menu": is_recommendation_menu,
                    "is_catalogue_added": is_catalogue_added,
                    "is_catalogue_purchased": is_catalogue_purchased,
                    "post_processor_tree_name": post_processor_tree_name,
                    "api_tree_name": api_tree_name,
                    "pipe_processor_tree_name": pipe_processor_tree_name,
                    "tree_children_list": tree_children_list,
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
                    "need_to_show_auto_fix_popup": need_to_show_auto_fix_popup,
                    "whatsapp_list_message_header": whatsapp_list_message_header,
                    "is_whatsapp_channel_selected": "WhatsApp" in intent_channel_list,
                    "selected_tts_provider": selected_tts_provider,
                    "allow_barge": tree_obj.check_barge_in_enablement(),
                    "disposition_code": tree_obj.disposition_code,
                    "unselected_child_trees": unselected_child_trees,
                    "unselected_main_intents": unselected_main_intents,
                    "whatsapp_menu_section_objs": whatsapp_menu_section_objs,
                    "whatsapp_quick_recommendations_allowed": whatsapp_quick_recommendations_allowed,
                    "tree_obj": tree_obj,
                })
            else:
                # return HttpResponseNotFound("<h1>No Page found</h1>")
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EditTreeConsole: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        # return HttpResponseNotFound(INVALID_REQUEST)
        return render(request, 'EasyChatApp/error_500.html')


def EditMultilingualTreeConsole(request):  # noqa: N802
    try:
        if is_allowed(request, [BOT_BUILDER_ROLE]):
            if not check_access_for_user(request.user, None, "Intent Related", "overall"):
                return HttpResponseNotFound("You do not have access to this page")
            selected_bot_obj = None
            intent_obj = None
            parent_obj = None
            tree_obj = None
            try:
                intent_pk = request.GET['intent_pk']
                parent_pk = request.GET['parent_pk']
                tree_pk = request.GET['tree_pk']
                selected_language = "en"
                
                if "selected_language" in request.GET:
                    selected_language = request.GET["selected_language"]

                if int(parent_pk) == -1:
                    return HttpResponseRedirect("/chat/edit-intent/?intent_pk=" + str(intent_pk) + "&selected_language=" + selected_language)

                if selected_language == "en":
                    return HttpResponseRedirect("/chat/edit-tree/?intent_pk=" + str(intent_pk) + "&parent_pk=" + parent_pk + "&tree_pk=" + tree_pk + "&selected_language=en")

                intent_obj = Intent.objects.get(
                    pk=int(intent_pk), is_hidden=False)
                parent_obj = Tree.objects.get(
                    pk=int(parent_pk), is_deleted=False)
                tree_obj = Tree.objects.get(pk=int(tree_pk), is_deleted=False)
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("EditTreeConsole: %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                # return HttpResponseNotFound("<h1>No Page found</h1>")
                return render(request, 'EasyChatApp/error_404.html')
            table_list_of_list = None
            rows = 0
            columns = 0
            if intent_obj != None and parent_obj != None and tree_obj != None:
                selected_bot_obj = intent_obj.bots.all()[0]
                selected_language_obj = Language.objects.get(
                    lang=selected_language)
                tree_tuning_obj = check_and_update_tunning_tree_object(
                    tree_obj, selected_language_obj, LanguageTuningIntentTable, LanguageTuningTreeTable, LanguageTuningBotResponseTable, LanguageTuningChoicesTable, EasyChatTranslationCache)
                if tree_tuning_obj:
                    table_list_of_list = tree_tuning_obj.response.table
                    if table_list_of_list != '{"items": []}':
                        rows = len(json.loads(table_list_of_list)["items"])
                        if rows > 0:
                            columns = len(json.loads(
                                table_list_of_list)["items"][0])
                        else:
                            columns = 0
                need_to_show_auto_fix_popup = False
                selected_tts_provider = get_selected_tts_provider_name(
                    selected_bot_obj, BotChannel)
                return render(request, 'EasyChatApp/platform/edit_tree.html', {
                    "tree_tuning_obj": tree_tuning_obj,
                    "selected_language": selected_language,
                    "selected_bot_obj": selected_bot_obj,
                    "table_list_of_list": table_list_of_list,
                    "rows": rows,
                    "columns": columns,
                    "tree_pk": tree_pk,
                    "need_to_show_auto_fix_popup": need_to_show_auto_fix_popup,
                    "selected_tts_provider": selected_tts_provider,
                    "language_script_type": selected_language_obj.language_script_type,
                })
            else:
                # return HttpResponseNotFound("<h1>No Page found</h1>")
                return render(request, 'EasyChatApp/error_404.html')
        else:
            return HttpResponseRedirect("/chat/login/")
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EditTreeConsole: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        # return HttpResponseNotFound(INVALID_REQUEST)
        return render(request, 'EasyChatApp/error_500.html')


class RenameTreeAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                return json.loads(data)

            data = DecryptVariable(data["json_string"])

            data = json.loads(data)
            tree_pk = data["tree_pk"]
            tree_name = data["tree_name"]
            parent_pk = data["parent_pk"]

            tree_obj = Tree.objects.get(pk=int(tree_pk), is_deleted=False)

            old_name = tree_obj.name

            parent_choice_obj = Tree.objects.get(pk=int(parent_pk), is_deleted=False).response.choices.all(
            ).get(display=str(old_name), value=str(old_name))
            parent_choice_obj.display = tree_name
            parent_choice_obj.value = tree_name
            parent_choice_obj.save()

            tree_obj.name = str(tree_name)
            tree_obj.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error RenameTreeAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DeleteTreeAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                return json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            tree_pk = data["tree_pk"]
            intent_pk = data["intent_pk"]
            parent_pk = data["parent_pk"]

            root_tree_pk = Intent.objects.get(
                pk=int(intent_pk), is_hidden=False).tree.pk

            is_root_tree = False
            if int(root_tree_pk) == int(tree_pk):
                # if(delete_intent(int(intent_pk),request.user)):
                response["status"] = 200
                is_root_tree = True
            else:
                tree_obj = Tree.objects.get(pk=int(tree_pk), is_deleted=False)  # noqa: F841

                parent_tree_obj = Tree.objects.get(pk=int(parent_pk), is_deleted=False)
                parent_tree_obj.children.remove(tree_obj)

                choice = None
                if parent_tree_obj.response:
                    choice = parent_tree_obj.response.choices.filter(value=tree_obj.name).first()
                
                if choice:
                    parent_tree_obj.response.choices.remove(choice)

                if not parent_tree_obj.children.filter(is_deleted=False):
                    parent_tree_obj.is_last_tree = True
                
                parent_tree_obj.save(update_fields=["is_last_tree"])

                tree_obj.disable()
                response["status"] = 200

            response["is_root"] = is_root_tree

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteTreeAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class CreateTreeAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                return json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            tree_pk = data["tree_pk"]
            tree_name = data["tree_name"]
            tree_name = validation_obj.remo_html_from_string(tree_name)
            tree_name = tree_name.strip()
            tree_name = str(tree_name)

            parent_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()
            new_tree_obj = Tree.objects.create(name=str(tree_name), is_last_tree=True)
            Intent.objects.filter(
                tree=parent_obj, is_faq_intent=True).update(is_faq_intent=False)  # Disables FAQ Intent if child is created

            bot_response_obj = None
            if parent_obj.response == None:
                bot_response_obj = BotResponse.objects.create()
            else:
                bot_response_obj = parent_obj.response

            parent_obj.children.add(new_tree_obj)
            parent_obj.response = bot_response_obj
            parent_obj.is_last_tree = False
            parent_obj.save()

            check_and_update_whatsapp_menu_objs(parent_obj)

            response["status"] = 200
            response["child_tree_pk"] = new_tree_obj.pk
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error CreateTreeAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


def FetchTreeInformationOld(request, data):
    response = {}
    response["status"] = 500
    try:
        tree_pk = data["tree_pk"]
        bot_id = data["bot_id"]
        tree_obj = Tree.objects.get(pk=int(tree_pk), is_deleted=False)
        bot_obj = Bot.objects.get(
            pk=int(bot_id), is_deleted=False)
        tree_name = tree_obj.name

        modes = json.dumps({})
        modes_param = json.dumps({})

        response_pk = None
        if tree_obj.response != None:
            response_pk = tree_obj.response.pk
            modes = tree_obj.response.modes
            modes_param = tree_obj.response.modes_param

        accept_keywords = tree_obj.accept_keywords

        post_processor_name = ""
        post_processor_function = ""
        if tree_obj.post_processor != None:
            post_processor_name = tree_obj.post_processor.name
            post_processor_function = tree_obj.post_processor.function

        response["status"] = 200
        response["response_pk"] = response_pk
        response["tree_name"] = tree_name
        response["accept_keywords"] = accept_keywords
        response["post_processor_name"] = post_processor_name
        response["post_processor_function"] = post_processor_function
        response["modes"] = modes
        response["modes_param"] = modes_param
        order_of_response = json.loads(tree_obj.order_of_response)
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

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error FetchTreeInformationOld %s %s",
                        str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    custom_encrypt_obj = CustomEncrypt()
    response = custom_encrypt_obj.encrypt(json.dumps(response))
    return Response(data=response)


class FetchTreeInformationAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                return json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            if request.COOKIES.get("edit_intent_ui", "new") == "old":
                return FetchTreeInformationOld(request, data)

            tree_pk = data["tree_pk"]
            bot_id = data["bot_id"]
            intent_pk = data["intent_pk"]
            tree_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()
            bot_obj = Bot.objects.filter(
                pk=int(bot_id), is_deleted=False).first()
            tree_name = tree_obj.name
            selected_language = data.get("selected_language", "en")

            intent_response = None
            answer_pk = None
            recommendation_list = []
            child_choices = []
            child_choices_list = []
            whatsapp_list_message_header = None
            if tree_obj.response != None:
                answer_pk = tree_obj.response.pk
                intent_response = {}
                bot_response_obj = tree_obj.response
                selected_language_obj = Language.objects.filter(
                    lang=selected_language).first()

                response_list = []
                choice_list = []
                card_list = []
                image_list = []
                video_list = []
                modes_dict = {}
                modes_params_dict = {}

                if selected_language != "en":
                    tuned_bot_response = check_and_update_tunning_tree_object(
                        tree_obj, selected_language_obj, LanguageTuningIntentTable, LanguageTuningTreeTable, LanguageTuningBotResponseTable, LanguageTuningChoicesTable, EasyChatTranslationCache)
                
                try:
                    table_list_of_list = bot_response_obj.table
                    if selected_language != "en":
                        table_list_of_list = tuned_bot_response.response.table
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
                        response_list = json.loads(
                            tuned_bot_response.response.sentence)["items"]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("No response %s %s", str(e),
                                   str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass

                try:
                    card_list = json.loads(bot_response_obj.cards)["items"]
                    if selected_language != "en":
                        card_list = json.loads(
                            tuned_bot_response.response.cards)["items"]
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.warning("No cards %s %s", str(e),
                                   str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass

                if selected_language != "en":
                    try:
                        tree_name = tuned_bot_response.name
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
                    response["intent_name"] = tree_name
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

                child_choices = tree_obj.response.choices.all()
                whatsapp_list_message_header = tree_obj.response.whatsapp_list_message_header

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

            other_settings["is_item_purchased"] = tree_obj.is_catalogue_purchased

            intent_children_list = []

            intent_children = tree_obj.children.all()

            for children in intent_children:
                intent_children_list.append(children.name)
            other_settings["intent_children_list"] = intent_children_list

            for choice in child_choices:
                child_choices_list.append(choice.value)
            other_settings["child_choices_list"] = child_choices_list

            if child_choices_list != [] and intent_children_list != child_choices_list:
                choices_order_changed = True
            else:
                choices_order_changed = False
            other_settings["choices_order_changed"] = choices_order_changed

            accept_keywords = tree_obj.accept_keywords

            post_processor_name = ""
            post_processor_function = ""
            if tree_obj.post_processor != None:
                post_processor_name = tree_obj.post_processor.name
                post_processor_function = tree_obj.post_processor.function

            if tree_obj.explanation == None:
                explanation = ""
            else:
                explanation = tree_obj.explanation.explanation
            
            is_custom_order_selected = tree_obj.is_custom_order_selected

            order_of_response = tree_obj.order_of_response
            
            intent_obj = Intent.objects.filter(
                pk=int(intent_pk), is_hidden=False).first()
            
            # selected_bot_pk_list = list(
            #     intent_obj.bots.values_list("pk", flat=True))

            # intent_objs_list = Intent.objects.filter(bots__in=selected_bot_pk_list, is_deleted=False, is_hidden=False, is_small_talk=False).distinct()

            # modified_intent_list = []
            is_quick_recommendation_present = False
            recommeded_intents_dict_list = []
            
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
            #     if str(int_obj.pk) not in recommendation_list:
            #         modified_intent_list.append({
            #             "is_selected": False,
            #             "intent_name": int_obj.name,
            #             "intent_pk": int_obj.pk
            #         })
            other_settings["is_quick_recommendation_present"] = is_quick_recommendation_present
            post_processor_variable = ""
            selected_validator_obj = None

            validators = ProcessorValidator.objects.filter(
                bot=bot_obj).values("name", "processor__pk")

            if tree_obj.post_processor:
                processor_obj = tree_obj.post_processor
                post_processor_variable = processor_obj.post_processor_direct_value
                if len(ProcessorValidator.objects.filter(processor=processor_obj)) != 0:
                    selected_validator_obj = ProcessorValidator.objects.filter(
                        processor=processor_obj).values("processor__pk").first()
            
            is_child_tree_visible = tree_obj.is_child_tree_visible
            show_go_back_checkbox = bool(tree_obj.children.filter(is_deleted=False))
            is_go_back_enabled = tree_obj.is_go_back_enabled
            is_last_tree = tree_obj.is_last_tree
            is_exit_tree = tree_obj.is_exit_tree
            is_transfer_tree = tree_obj.enable_transfer_agent
            allow_barge = tree_obj.check_barge_in_enablement()
            is_automatic_recursion_enabled = tree_obj.is_automatic_recursion_enabled
            pipe_processor_tree_name = ""
            api_tree_name = ""
            post_processor_tree_name = ""

            if tree_obj.pipe_processor:
                pipe_processor_tree_name = ": " + tree_obj.pipe_processor.name
            if tree_obj.api_tree:
                api_tree_name = ": " + tree_obj.api_tree.name
            if tree_obj.post_processor:
                post_processor_tree_name = ": " + tree_obj.post_processor.name

            flow_analytics_variable = tree_obj.flow_analytics_variable
            required_analytics_variable = False
            if flow_analytics_variable != "":
                required_analytics_variable = True
            is_category_response_allowed = tree_obj.is_category_response_allowed

            other_settings.update({
                "post_processor_variable": post_processor_variable,
                "selected_validator_obj": selected_validator_obj,
                "is_child_tree_visible": is_child_tree_visible,
                "show_go_back_checkbox": show_go_back_checkbox,
                "is_go_back_enabled": is_go_back_enabled,
                "is_last_tree": is_last_tree,
                "is_exit_tree": is_exit_tree,
                "is_transfer_tree": is_transfer_tree,
                "allow_barge": allow_barge,
                "is_automatic_recursion_enabled": is_automatic_recursion_enabled,
                "pipe_processor_tree_name": pipe_processor_tree_name,
                "api_tree_name": api_tree_name,
                "post_processor_tree_name": post_processor_tree_name,
                "flow_analytics_variable": flow_analytics_variable,
                "required_analytics_variable": required_analytics_variable,
                "is_category_response_allowed": is_category_response_allowed,
                "whatsapp_list_message_header": whatsapp_list_message_header,
                "disposition_code": tree_obj.disposition_code,
                "validators": list(validators),
                'is_confirmation_and_reset_enabled': tree_obj.is_confirmation_and_reset_enabled
            })

            intent_channel_list = intent_obj.channels.values_list("name", flat=True)

            whatsapp_menu_section_objs_list = WhatsAppMenuSection.objects.filter(tree=tree_obj).order_by("pk")
            whatsapp_menu_section_objs = []
            for whatsapp_menu_section_obj in whatsapp_menu_section_objs_list:
                whatsapp_menu_section_data = {}
                whatsapp_menu_section_data["pk"] = whatsapp_menu_section_obj.pk
                whatsapp_menu_section_data["title"] = whatsapp_menu_section_obj.title
                whatsapp_menu_section_data["child_tree_details"] = whatsapp_menu_section_obj.get_child_tree_details()
                whatsapp_menu_section_data["main_intent_details"] = whatsapp_menu_section_obj.get_main_intent_details()
                whatsapp_menu_section_objs.append(whatsapp_menu_section_data)

            whatsapp_quick_recommendations_allowed = 10

            if tree_obj.is_child_tree_visible and tree_obj.children.filter(is_deleted=False).exists():
                whatsapp_quick_recommendations_allowed = 10 - tree_obj.children.filter(is_deleted=False).count()
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

            unselected_child_trees = tree_obj.children.filter(is_deleted=False).exclude(pk__in=selected_child_trees).values("name", "pk")
            if tree_obj.children.filter(is_deleted=False).count() == 1 or not tree_obj.is_child_tree_visible:
                unselected_child_trees = []
            unselected_main_intents = Intent.objects.filter(bots=bot_obj, channels=whatsapp_channel_obj, is_deleted=False, is_hidden=False, is_small_talk=False).exclude(pk__in=selected_main_intents).values("name", "pk")

            response.update({
                "explanation": explanation,
                # "intent_name_list": modified_intent_list,
                "is_custom_order_selected": is_custom_order_selected,
                "order_of_response": order_of_response,
                "short_name_value": str(tree_obj.short_name),
                "short_name_enabled": 'GoogleBusinessMessages' in intent_channel_list,
                'whatsapp_short_name': tree_obj.get_whatsapp_short_name(),
                'whatsapp_description': tree_obj.get_whatsapp_description(),
                'other_settings': other_settings,
                "recommeded_intents_dict_list": recommeded_intents_dict_list,
                "whatsapp_menu_section_objs": whatsapp_menu_section_objs,
                "whatsapp_quick_recommendations_allowed": whatsapp_quick_recommendations_allowed,
                "enable_whatsapp_menu_format": tree_obj.enable_whatsapp_menu_format,
                "unselected_child_trees": list(unselected_child_trees),
                "unselected_main_intents": list(unselected_main_intents),
            })

            response["status"] = 200
            response["answer_pk"] = answer_pk
            response["intent_name"] = tree_name
            response["accept_keywords"] = accept_keywords
            response["post_processor_name"] = post_processor_name
            response["post_processor_function"] = post_processor_function
            order_of_response = json.loads(tree_obj.order_of_response)
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

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FetchTreeInformationAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveTreeAPI(APIView):

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
            # print(data["json_string"])

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            response_sentence_list = get_response_sentence_list(json_string)
            data = json.loads(json_string)
            data = remove_custom_html_from_dict_values(data)

            intent_pk = data["intent_pk"]
            # Tree (fields)
            tree_pk = data["tree_pk"]
            # parent_pk = data["parent_pk"]
            tree_name = data["tree_name"]
            tree_short_name = data["tree_short_name"]
            tree_name = validation_obj.remo_html_from_string(tree_name)
            tree_name = validation_obj.remo_special_tag_from_string(tree_name)
            tree_name = tree_name.strip()
            tree_short_name = validation_obj.remo_html_from_string(tree_short_name)
            tree_short_name = validation_obj.remo_special_tag_from_string(tree_short_name)
            tree_short_name = tree_short_name.strip()
            
            accept_keywords = data["accept_keywords"]
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
            is_single_calender_date_picker_allowed = data["is_single_calender_date_picker_allowed"]
            is_multi_calender_date_picker_allowed = data["is_multi_calender_date_picker_allowed"]
            is_single_calender_time_picker_allowed = data["is_single_calender_time_picker_allowed"]
            is_multi_calender_time_picker_allowed = data["is_multi_calender_time_picker_allowed"]
            is_range_slider_required = data["is_range_slider_required"]
            range_slider_type = data["range_slider_type"]
            minimum_range = data["minimum_range"]
            maximum_range = data["maximum_range"]
            is_radio_button_allowed = data["is_radio_button_allowed"]
            radio_button_choices = data["radio_button_choices"]
            choosen_file_type = data["choosen_file_type"]
            table_input_list_of_list = data['table_input_list_of_list']
            is_video_recorder_allowed = data["is_video_recorder_allowed"]
            is_save_video_attachment = data[
                "is_save_video_attachment_required"]
            is_phone_widget_enabled = data["is_phone_widget_enabled"]
            country_code = data["country_code"]
            is_create_form_allowed = data["is_create_form_allowed"]
            form_name = data["form_name"]
            form_fields_list = data["form_fields_list"]
            is_automatic_recursion_enabled = data[
                'is_automate_recursion_enabled']
            multilingual_name = data['multilingual_name']

            enable_whatsapp_menu_format = data["enable_whatsapp_menu_format"]
            whatsapp_short_name = data["whatsapp_short_name"]
            whatsapp_description = data["whatsapp_description"]

            # print(table_input_list_of_list)

            # post_processor_name = data["post_processor_name"]
            # post_processor_function = data["post_processor_function"]

            # BotResponse (fields)
            # response_choice_list = data["response_choice_list"]
            response_image_list = data["response_image_list"]
            response_video_list = data["response_video_list"]
            is_child_tree_visible = data["is_child_tree_visible"]
            recommended_intent_list = data["recommended_intent_list"]
            card_list = data["card_list"]
            is_tree_name_updated = False

            for card in card_list:
                card_title = card["title"]
                card_content = card["content"]
                card_link = card["link"]
                card_img_url = card["img_url"]
                if not validation_obj.is_valid_card_name(card_title) or card_title.strip() == "":
                    return Response(data=return_invalid_response(response, "Card title can only contain alphabets, emojis and special characters (&, $, !, @, ?).", 300))

                card_content = validation_obj.remo_html_from_string(card_content)
                card_content = validation_obj.remo_unwanted_security_characters(card_content)
                if card_content.strip() == "":
                    return Response(data=return_invalid_response(response, "Card content can only contain alphabets.", 300))

                if not validation_obj.is_valid_url(card_link) or card_link.strip() == "":
                    return Response(data=return_invalid_response(response, "Card redirection link is invalid.", 300))

                if not validation_obj.is_valid_url(card_img_url) or card_img_url.strip() == "":
                    return Response(data=return_invalid_response(response, "Card image link is invalid.", 300))

            explanation = data["explanation"]
            validator_id = data["validator_id"]
            post_processor_variable = data["post_processor_variable"]
            is_check_box_allowed = data["is_check_box_allowed"]
            check_box_choices = data["checkbox_choices_list"]
            is_drop_down_allowed = data["is_drop_down_allowed"]
            drop_down_choices = data["dropdown_choices_list"]
            is_go_back_enabled = data["is_go_back_enabled"]
            is_confirmation_and_reset_enabled = data[
                "is_confirmation_and_reset_enabled"]
            is_recommendation_menu = data["is_recommendation_menu"]
            is_catalogue_added = data["is_catalogue_added"]
            selected_catalogue_sections = data["selected_catalogue_sections"]
            if selected_catalogue_sections is None:
                selected_catalogue_sections = []
            is_catalogue_purchased = data["is_catalogue_purchased"]
            is_custom_order_selected = data["is_custom_order_selected"]
            order_of_response = data["order_of_response"]
            whatsapp_list_message_header = data["whatsapp_list_message_header"]

            username = request.user.username
            user_obj = User.objects.filter(username=str(username)).first()
            if user_obj.is_staff:
                flow_analytics_variable = data["flow_analytics_variable"]
                category_response_allowed = data["category_response_allowed"]

            is_last_tree = data["is_last_tree"]
            is_exit_tree = data["is_exit_tree"]
            is_transfer_tree = data["is_transfer_tree"]
            allow_barge = data["allow_barge"]
            disposition_code = data["disposition_code"]

            tree_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()

            explanation_obj = None
            if tree_obj.explanation == None:
                explanation_obj = Explanation.objects.create()

            else:
                explanation_obj = tree_obj.explanation

            explanation_obj.explanation = explanation
            explanation_obj.save()
            tree_obj.explanation = explanation_obj
            tree_obj.save()
            if user_obj.is_staff:
                tree_obj.is_category_response_allowed = category_response_allowed
                tree_obj.save()

            if(validator_id != None and validator_id != ""):
                validator_obj = Processor.objects.filter(pk=int(validator_id)).first()
                tree_obj.post_processor = validator_obj
            else:
                # if there is a previously assigned post_processor, keeping it
                # as it is in case of no validator being selected from console.
                if len(ProcessorValidator.objects.filter(processor=tree_obj.post_processor)) == 0:
                    # tree_obj.post_processor = tree_obj.post_processor
                    if(post_processor_variable != ""):
                        if tree_obj.post_processor != None and tree_obj.post_processor.name == "PostProcessor_" + str(post_processor_variable):
                            pass
                        else:
                            code = "from EasyChatApp.utils import logger\nimport sys\ndef f(x):\n    json_response = {}\n    json_response['status_code'] = '500'\n    json_response['status_message'] = 'Internal server error.'\n    json_response['data'] = {}\n    try:\n        json_response['data']['" + post_processor_variable + \
                                "']=x\n        #write your code here\n        json_response['status_code'] = '200'\n        json_response['print'] = 'Hello world!'\n        return json_response\n    except Exception as E:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('PostProcessorContent: %s at %s',str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        json_response['status_code'] = '500'\n        json_response['status_message'] = 'ERROR :-  '+str(E)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return json_response"
                            processor_obj = Processor.objects.create(name="PostProcessor_" + str(
                                post_processor_variable), function=code, post_processor_direct_value=post_processor_variable)
                            tree_obj.post_processor = processor_obj
                else:
                    tree_obj.post_processor = None

            if tree_name == "":
                response["status"] = 300
                response["message"] = "Tree name can not be empty."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if len(tree_short_name) > 25:
                response["status"] = 300
                response["message"] = "Tree short name can not be more than 25 characters."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            # old_name = tree_obj.name

            # parent_choice_obj = Tree.objects.get(pk=int(parent_pk)).response.choices.all(
            # ).get(display=str(old_name), value=str(old_name))
            # parent_choice_obj.display = tree_name
            # parent_choice_obj.value = tree_name
            # parent_choice_obj.save()

            if tree_obj.name != tree_name:
                tree_obj.name = str(tree_name)
                is_tree_name_updated = True

            tree_obj.short_name = str(tree_short_name)
            tree_obj.accept_keywords = accept_keywords
            tree_obj.is_automatic_recursion_enabled = is_automatic_recursion_enabled
            tree_obj.name = tree_name
            tree_obj.multilingual_name = multilingual_name
            tree_obj.is_catalogue_purchased = is_catalogue_purchased

            if whatsapp_short_name:
                tree_obj.whatsapp_short_name = whatsapp_short_name

            if whatsapp_description:
                tree_obj.whatsapp_description = whatsapp_description

            tree_obj.enable_whatsapp_menu_format = enable_whatsapp_menu_format

            if is_child_tree_visible != "None":
                if tree_obj.is_child_tree_visible != is_child_tree_visible and is_child_tree_visible:
                    tree_obj.is_child_tree_visible = is_child_tree_visible
                    check_and_update_whatsapp_menu_objs(tree_obj)
                
                tree_obj.is_child_tree_visible = is_child_tree_visible
            if user_obj.is_staff:
                if category_response_allowed:
                    tree_obj.is_child_tree_visible = False
            # tree_obj.is_attachment_required = is_attachment_required
            # tree_obj.choosen_file_type = choosen_file_type
            tree_obj.save()
            if user_obj.is_staff:
                tree_obj.flow_analytics_variable = flow_analytics_variable
                tree_obj.save()

            if not len(response_sentence_list):
                response["status"] = 300
                response["message"] = "Bot response can not be empty."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            sentence_json = {
                "items": []
            }

            for sentence in response_sentence_list:
                text_response = sentence["text_response"]
                speech_response = sentence["speech_response"]
                hinglish_response = sentence["hinglish_response"]
                reprompt_response = sentence["reprompt_response"]
                ssml_response = sentence["ssml_response"].strip()

                if text_response == "":
                    response["status"] = 300
                    response[
                        "message"] = "Bot response can not be empty."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                speech_response = validation_obj.remo_html_from_string(speech_response)

                if speech_response == "":
                    speech_response = validation_obj.remo_html_from_string(text_response)

                if reprompt_response == "":
                    reprompt_response = text_response

                if ssml_response == "":
                    ssml_response = speech_response

                sentence_json["items"].append({
                    "text_response": text_response,
                    "speech_response": speech_response,
                    "hinglish_response": hinglish_response,
                    "text_reprompt_response": reprompt_response,
                    "speech_reprompt_response": speech_response,
                    "tooltip_response": "",
                    "ssml_response": ssml_response,
                })

            bot_response_obj = None
            need_to_update_activty_update = False
            if tree_obj.response == None:
                bot_response_obj = BotResponse.objects.create()
            else:
                need_to_update_activty_update = True
                bot_response_obj = tree_obj.response

                # if there are previously saved text_repromt_response or
                # speech_repromt_response, keeping them as it is
                text_reprompt_response = json.loads(bot_response_obj.sentence)["items"][
                    0]["text_reprompt_response"]
                speech_reprompt_response = json.loads(bot_response_obj.sentence)["items"][
                    0]["speech_reprompt_response"]
                if text_reprompt_response != "":
                    sentence_json["items"][0][
                        "text_reprompt_response"] = reprompt_response
                if speech_reprompt_response != "":
                    sentence_json["items"][0][
                        "speech_reprompt_response"] = speech_reprompt_response
            if need_to_update_activty_update:
                eng_lang_obj = None
                if Language.objects.filter(lang="en"):
                    eng_lang_obj = Language.objects.filter(lang="en").first()
                activity_update = get_bot_response_activity_update_status(
                    bot_response_obj, sentence, card_list, table_input_list_of_list, eng_lang_obj, LanguageTuningBotResponseTable)

                if is_tree_name_updated:
                    update_tree_activity_status(tree_obj, activity_update, eng_lang_obj, LanguageTuningTreeTable)

                bot_response_obj.activity_update = json.dumps(activity_update)
            #     existing_choice_obj_list = bot_response_obj.choices.all()
            #     for choice in existing_choice_obj_list:
            #         bot_response_obj.choices.remove(choice)
            #     bot_response_obj.save()

            # for choice_value in response_choice_list:
            #     choice_obj = Choice.objects.get(value=str(choice_value))
            #     bot_response_obj.choices.add(choice_obj)

            modes = json.loads(bot_response_obj.modes)
            modes_param = json.loads(bot_response_obj.modes_param)
            modes_param["selected_catalogue_sections"] = selected_catalogue_sections

            change_data = ""

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
                modes["is_calender"] = "false"

            if is_check_box_allowed:
                modes["is_check_box"] = "true"
                modes_param["check_box_choices"] = check_box_choices
            else:
                modes["is_check_box"] = "false"

            if is_drop_down_allowed:
                modes["is_drop_down"] = "true"
                check_for_tms_intent_and_create_categories(
                    intent_pk, drop_down_choices, TicketCategory)
                modes_param["drop_down_choices"] = drop_down_choices
            else:
                modes["is_drop_down"] = "false"

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
            else:
                modes["is_recommendation_menu"] = "false"

            modes["is_catalogue_added"] = "true" if is_catalogue_added else "false"

            bot_response_obj.modes = json.dumps(modes)
            bot_response_obj.modes_param = json.dumps(modes_param)

            bot_response_obj.sentence = json.dumps(sentence_json)
            bot_response_obj.table = json.dumps(
                {"items": table_input_list_of_list})
            bot_response_obj.images = json.dumps(
                {"items": response_image_list})
            bot_response_obj.videos = json.dumps(
                {"items": response_video_list})
            bot_response_obj.recommendations = json.dumps(
                {"items": recommended_intent_list})
            bot_response_obj.whatsapp_list_message_header = whatsapp_list_message_header
            bot_response_obj.cards = json.dumps({"items": card_list})

            child_choices = data["child_choices"]
            if child_choices != []:

                if len(tree_obj.children.all()) != len(child_choices):
                    response["status"] = 401
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                else:
                    bot_response_obj.choices.all().delete()
                    for choices in child_choices:
                        choice_obj = Choice.objects.create(
                            value=choices, display=choices)
                        bot_response_obj.choices.add(choice_obj)

                bot_response_obj.save()

            else:
                bot_response_obj.choices.all().delete()
                bot_response_obj.save()

            bot_response_obj.save()
            tree_obj.response = bot_response_obj
            tree_obj.is_go_back_enabled = is_go_back_enabled

            if is_confirmation_and_reset_enabled:
                if tree_obj.is_confirmation_and_reset_enabled == False or (tree_obj.confirmation_reset_tree_pk is None):
                    add_confirmation_and_reset_tree(tree_obj, intent_pk)

            if is_confirmation_and_reset_enabled == False:
                if tree_obj.is_confirmation_and_reset_enabled == True:
                    remove_confirmation_and_reset_tree(tree_obj)
                else:
                    tree_obj.confirmation_reset_tree_pk = None

            tree_obj.is_custom_order_selected = is_custom_order_selected
            tree_obj.order_of_response = json.dumps(order_of_response)
            tree_obj.is_last_tree = is_last_tree
            tree_obj.is_exit_tree = is_exit_tree
            tree_obj.enable_transfer_agent = is_transfer_tree
            tree_obj.disposition_code = disposition_code

            voice_bot_conf = json.loads(tree_obj.voice_bot_conf)
            voice_bot_conf["barge_in"] = allow_barge
            tree_obj.voice_bot_conf = json.dumps(voice_bot_conf)

            tree_obj.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveTreeAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveMultilingualTreeAPI(APIView):

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

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            response_sentence_list = get_response_sentence_list(json_string)
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            # intent_pk = data["intent_pk"]

            tree_pk = data["tree_pk"]
            tree_name = data["tree_name"]
            tree_name = validation_obj.remo_html_from_string(tree_name)
            tree_name = tree_name.strip()
            selected_language = data["selected_language"]
            selected_language = validation_obj.remo_html_from_string(selected_language)
            card_list = data["card_list"]
            table_input_list_of_list = data["table_input_list_of_list"]
            # username = request.user.username
            # user_obj = User.objects.get(username=str(username))

            language_obj = Language.objects.filter(lang=selected_language).first()

            tree_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()

            tree_tuning_obj = LanguageTuningTreeTable.objects.filter(
                tree=tree_obj, language=language_obj).first()
            if tree_tuning_obj.multilingual_name != tree_name:
                accept_keywords = str(tree_obj.accept_keywords).split(",")
                accept_keywords_list = [accept_keyword for accept_keyword in accept_keywords if accept_keyword.strip() != ""]

                english_translated_previous_tree_name = translate_given_text_to_english(tree_tuning_obj.multilingual_name)
                
                if english_translated_previous_tree_name and english_translated_previous_tree_name != tree_tuning_obj.multilingual_name:
                    if english_translated_previous_tree_name.strip().lower() in accept_keywords_list:
                        accept_keywords_list.remove(english_translated_previous_tree_name)

                english_translated_tree_name = translate_given_text_to_english(tree_name)
                if english_translated_tree_name and english_translated_tree_name != tree_name:
                    if english_translated_tree_name not in accept_keywords_list:
                        accept_keywords_list.append(english_translated_tree_name)

                tree_obj.accept_keywords = ",".join(accept_keywords_list)
                tree_obj.save(update_fields=["accept_keywords"])
                
            tree_tuning_obj.multilingual_name = tree_name
            tree_tuning_obj.save()

            bot_response_tuned_obj = tree_tuning_obj.response

            sentence_json = {
                "items": []
            }

            for sentence in response_sentence_list:
                text_response = sentence["text_response"]
                speech_response = sentence["speech_response"]
                hinglish_response = sentence["hinglish_response"]
                reprompt_response = sentence["reprompt_response"]
                ssml_response = sentence["ssml_response"]

                speech_response = validation_obj.remo_html_from_string(speech_response)

                if speech_response == "":
                    speech_response = validation_obj.remo_html_from_string(text_response)

                if reprompt_response == "":
                    reprompt_response = text_response

                if ssml_response == "":
                    ssml_response = speech_response

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
            bot_response_tuned_obj.table = json.dumps(
                {"items": table_input_list_of_list})
            bot_response_tuned_obj.cards = json.dumps({"items": card_list})
            bot_response_tuned_obj.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveMultilingualTreeAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveMultilingualTree = SaveMultilingualTreeAPI.as_view()


class FetchAllChoiceAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args):
        response = {}
        response["status"] = 500
        try:
            choice_objects = Choice.objects.all()
            choice_list = []

            for choice_obj in choice_objects:

                display = choice_obj.display
                value = choice_obj.value
                choice_list.append({
                    "display": str(display),
                    "value": str(value)
                })

            response["choice_list"] = choice_list
            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error FetchAllChoiceAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class AddNewChoiceAPI(APIView):

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

            display = data["display"]
            value = data["value"]
            
            Choice.objects.create(display=str(display), value=value)

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error AddNewChoiceAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class InsertTreeAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                return json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            tree_pk = data["tree_pk"]
            tree_name = data["tree_name"]

            tree_name = str(tree_name)

            parent_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()
            new_tree_obj = Tree.objects.create(name=str(tree_name))

            if not parent_obj.children.filter(is_deleted=False):
                parent_obj.is_last_tree = False
                new_tree_obj.is_last_tree = True

            bot_response_obj = None
            if parent_obj.response == None:
                bot_response_obj = BotResponse.objects.create()
            else:
                bot_response_obj = parent_obj.response
            parent_obj_childs = parent_obj.children.all()
            for child_tree_obj in parent_obj_childs:
                new_tree_obj.children.add(child_tree_obj)
            new_tree_obj.save()
            parent_obj.children.clear()
            parent_obj.children.add(new_tree_obj)
            parent_obj.response = bot_response_obj
            parent_obj.save()
            response["status"] = 200
            response["child_tree_pk"] = new_tree_obj.pk
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error InsertTreeAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DeleteTreeNodeAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                return json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            tree_pk = data["tree_pk"]
            intent_pk = data["intent_pk"]
            parent_pk = data["parent_pk"]

            root_intent = Intent.objects.filter(
                pk=int(intent_pk), is_hidden=False).first()
            root_tree = root_intent.tree
            root_tree_pk = root_tree.pk
            is_root_childs_present = False
            if int(root_tree_pk) == int(tree_pk):
                if len(root_tree.children.all()) == 1:
                    root_tree.disable()
                    root_intent.tree = root_tree.children.all()[0]
                    root_intent.save()
                else:
                    is_root_childs_present = True
            else:
                parent_tree_obj = Tree.objects.filter(pk=int(parent_pk)).first()
                tree_obj = Tree.objects.filter(pk=int(tree_pk)).first()
                tree_obj_childs = tree_obj.children.all()

                for child_tree_obj in tree_obj_childs:
                    parent_tree_obj.children.add(child_tree_obj)
                
                parent_tree_obj.children.remove(tree_obj)

                choice = None
                if parent_tree_obj.response:
                    choice = parent_tree_obj.response.choices.filter(value=tree_obj.name).first()
                
                if choice:
                    parent_tree_obj.response.choices.remove(choice)

                if not parent_tree_obj.children.filter(is_deleted=False):
                    parent_tree_obj.is_last_tree = True
                
                parent_tree_obj.save()
                
                tree_obj.disable()

            response["status"] = 200
            response["is_root_childs_present"] = is_root_childs_present

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteTreeNodeAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class PasteTreeNodeAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                return json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            tree_pk = data["tree_pk"]
            intent_pk = data["intent_pk"]
            copy_tree_id = data["copy_tree_id"]

            intent_obj = Intent.objects.filter(pk=intent_pk).first()

            # check whether the copied tree is an intent
            copied_tree_obj = Tree.objects.filter(pk=copy_tree_id).first()
            if (intent_obj.tree == copied_tree_obj):
                copied_tree_accepted_keywords = ""
                # to convert training data to comma separated
                for key, value in json.loads(intent_obj.training_data).items():
                    copied_tree_accepted_keywords += value + ","
                copied_tree_accepted_keywords = copied_tree_accepted_keywords[
                    :-1]
                copied_tree_obj.accept_keywords = copied_tree_accepted_keywords
                copied_tree_obj.save()

            tree_obj = Tree.objects.filter(pk=int(tree_pk)).first()
            # passing the below dictionary as parameter
            # will keep a check of tree and it's copy
            tree_children_list = {}
            tree_obj.children.add(make_copy_of_tree_obj(
                Tree.objects.filter(pk=int(copy_tree_id)).first(), tree_children_list))
            if tree_obj.children.filter(is_deleted=False):
                tree_obj.is_last_tree = False
            tree_obj.save()

            response["status"] = 200

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error PasteTreeNodeAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveWhatsAppMenuSectionAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"

        try:
            data = request.data

            if not isinstance(data, dict):
                return json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_id = data["bot_id"]
            bot_obj = Bot.objects.filter(pk=bot_id).first()

            user = User.objects.filter(username=request.user.username).first()

            validation_obj = EasyChatInputValidation()

            if bot_obj and user in bot_obj.users.all():    
                whatsapp_menu_section_id = data["whatsapp_menu_section_id"]
                whatsapp_menu_section_id = validation_obj.remo_html_from_string(whatsapp_menu_section_id)
                tree_pk = data["tree_pk"]
                tree_pk = validation_obj.remo_html_from_string(tree_pk)
                
                section_title = data["section_title"]
                section_title = validation_obj.remo_html_from_string(section_title)
                section_title = validation_obj.sanitize_html(section_title)

                child_tree_pk_list = data["child_tree_pk_list"]
                main_intent_pk_list = data["main_intent_pk_list"]

                tree_obj = Tree.objects.filter(pk=tree_pk).first()

                whatsapp_menu_section_obj = None
                if whatsapp_menu_section_id:
                    whatsapp_menu_section_obj = WhatsAppMenuSection.objects.filter(pk=whatsapp_menu_section_id, tree=tree_obj).first()
                else:
                    whatsapp_menu_section_obj = WhatsAppMenuSection.objects.create(tree=tree_obj)

                if whatsapp_menu_section_obj:
                    whatsapp_menu_section_obj.title = section_title
                    whatsapp_menu_section_obj.child_trees = json.dumps(child_tree_pk_list)
                    whatsapp_menu_section_obj.main_intents = json.dumps(main_intent_pk_list)
                    whatsapp_menu_section_obj.save()

                    response["status"] = 200
                    response["message"] = "Success"
                    response["data"] = {}
                    response["data"]["whatsapp_menu_section_id"] = whatsapp_menu_section_obj.pk
                    response["data"]["child_trees_data"] = whatsapp_menu_section_obj.get_child_tree_details()
                    response["data"]["main_intents_data"] = whatsapp_menu_section_obj.get_main_intent_details()
                    response["data"]["section_title"] = whatsapp_menu_section_obj.title

                else:
                    response["message"] = "Invalid data"

            else:
                response["message"] = "You are not authorised to access the bot."

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveWhatsAppMenuSectionAPI %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class DeleteWhatsAppMenuSectionAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"

        try:
            data = request.data

            if not isinstance(data, dict):
                return json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            bot_id = data["bot_id"]
            bot_obj = Bot.objects.filter(pk=bot_id).first()

            user = User.objects.filter(username=request.user.username).first()

            validation_obj = EasyChatInputValidation()

            if bot_obj and user in bot_obj.users.all():    
                whatsapp_menu_section_id = data["whatsapp_menu_section_id"]
                whatsapp_menu_section_id = validation_obj.remo_html_from_string(whatsapp_menu_section_id)
                
                whatsapp_menu_section_obj = WhatsAppMenuSection.objects.filter(pk=whatsapp_menu_section_id).first()
                if whatsapp_menu_section_obj:
                    whatsapp_menu_section_obj.delete()

                    response['status'] = 200
                    response["message"] = "Success"
                else:
                    response["message"] = "Invalid data"

            else:
                response["message"] = "You are not authorised to access the bot."

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error DeleteWhatsAppMenuSectionAPI %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveTreeResponseAPI(APIView):
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
            # print(data["json_string"])

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            response_sentence_list = get_response_sentence_list(json_string)
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            # Tree (fields)
            is_new_tree = data["is_new_tree"]
            tree_pk = data["tree_pk"]
            # parent_pk = data["parent_pk"]
            tree_name = data["tree_name"]
            tree_short_name = data["tree_short_name"]
            tree_name = validation_obj.remo_html_from_string(tree_name)
            tree_name = validation_obj.remo_special_tag_from_string(tree_name)
            tree_name = tree_name.strip()
            tree_short_name = validation_obj.remo_html_from_string(tree_short_name)
            tree_short_name = validation_obj.remo_special_tag_from_string(tree_short_name)
            tree_short_name = tree_short_name.strip()

            whatsapp_short_name = data["whatsapp_short_name"]
            whatsapp_description = data["whatsapp_description"]
            accept_keywords = data["accept_keywords"]

            response_image_list = data["image_list"]
            response_video_list = data["video_list"]
            table_input_list_of_list = data['table_input_list_of_list']
            card_list = data["card_list"]
            is_tree_name_updated = False

            for card in card_list:
                card_title = card["title"]
                card_content = card["content"]
                card_link = card["link"]
                card_img_url = card["img_url"]
                if not validation_obj.is_valid_card_name(card_title) or card_title.strip() == "":
                    return Response(data=return_invalid_response(response, "Card title can only contain alphabets, emojis and special characters (&, $, !, @, ?).", 300))

                card_content = validation_obj.remo_html_from_string(card_content)
                card_content = validation_obj.remo_unwanted_security_characters(card_content)
                if card_content.strip() == "":
                    return Response(data=return_invalid_response(response, "Card content can only contain alphabets.", 300))

                if not validation_obj.is_valid_url(card_link) or card_link.strip() == "":
                    return Response(data=return_invalid_response(response, "Card redirection link is invalid.", 300))

                if not validation_obj.is_valid_url(card_img_url) or card_img_url.strip() == "":
                    return Response(data=return_invalid_response(response, "Card image link is invalid.", 300))

            if tree_name == "":
                response["status"] = 300
                response["message"] = "Tree name can not be empty."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if len(tree_name) > INTENT_TREE_NAME_CHARACTER_LIMIT:
                response['status'] = 303
                response["status_message"] = "Tree name cannot contain more than 500 characters"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if len(tree_short_name) > 25:
                response["status"] = 300
                response["message"] = "Tree short name can not be more than 25 characters."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            if is_new_tree:
                is_in_between_tree = data["is_in_between_tree"]
                parent_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()
                tree_obj = Tree.objects.create(name=str(tree_name), is_last_tree=True)
                if is_in_between_tree:
                    parent_obj_childs = parent_obj.children.all()

                    for child_tree_obj in parent_obj_childs:
                        tree_obj.children.add(child_tree_obj)

                    tree_obj.is_last_tree = False
                    if not tree_obj.children.filter(is_deleted=False):
                        parent_obj.is_last_tree = False
                        tree_obj.is_last_tree = True

                    parent_obj.children.clear()
                else:
                    Intent.objects.filter(
                        tree=parent_obj, is_faq_intent=True).update(is_faq_intent=False)  # Disables FAQ Intent if child is created
                    parent_obj.is_last_tree = False
                
                if parent_obj.response == None:
                    parent_obj.response = BotResponse.objects.create()
                else:
                    if is_in_between_tree:
                        parent_obj.response.choices.all().delete()
                    elif parent_obj.response.choices.exists():
                        choice_obj = Choice.objects.create(
                            value=tree_name, display=tree_name)
                        parent_obj.response.choices.add(choice_obj)

                parent_obj.children.add(tree_obj)
                parent_obj.save()

                response["new_tree_pk"] = tree_obj.pk

                check_and_update_whatsapp_menu_objs(parent_obj)
            else:
                tree_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()
                if tree_obj.name != tree_name:
                    tree_obj.name = str(tree_name)
                    is_tree_name_updated = True
            
            tree_obj.short_name = str(tree_short_name)
            tree_obj.accept_keywords = accept_keywords

            if whatsapp_short_name:
                tree_obj.whatsapp_short_name = whatsapp_short_name

            if whatsapp_description:
                tree_obj.whatsapp_description = whatsapp_description

            if not len(response_sentence_list):
                response["status"] = 300
                response["message"] = "Bot response can not be empty."
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            sentence_json = {
                "items": []
            }

            for sentence in response_sentence_list:
                text_response = sentence["text_response"]
                speech_response = sentence["speech_response"]
                hinglish_response = sentence["hinglish_response"]
                reprompt_response = sentence["reprompt_response"]
                ssml_response = sentence["ssml_response"].strip()

                if text_response == "":
                    response["status"] = 300
                    response[
                        "message"] = "Bot response can not be empty."
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    return Response(data=response)

                speech_response = validation_obj.remo_html_from_string(speech_response)

                if speech_response == "":
                    speech_response = validation_obj.remo_html_from_string(text_response)

                if reprompt_response == "":
                    reprompt_response = text_response

                if ssml_response == "":
                    ssml_response = speech_response

                sentence_json["items"].append({
                    "text_response": text_response,
                    "speech_response": speech_response,
                    "hinglish_response": hinglish_response,
                    "text_reprompt_response": reprompt_response,
                    "speech_reprompt_response": speech_response,
                    "tooltip_response": "",
                    "ssml_response": ssml_response,
                })

            bot_response_obj = None
            need_to_update_activty_update = False
            if tree_obj.response == None:
                bot_response_obj = BotResponse.objects.create()
            else:
                need_to_update_activty_update = True
                bot_response_obj = tree_obj.response

                # if there are previously saved text_repromt_response or
                # speech_repromt_response, keeping them as it is
                text_reprompt_response = json.loads(bot_response_obj.sentence)["items"][
                    0]["text_reprompt_response"]
                speech_reprompt_response = json.loads(bot_response_obj.sentence)["items"][
                    0]["speech_reprompt_response"]
                if text_reprompt_response != "":
                    sentence_json["items"][0][
                        "text_reprompt_response"] = reprompt_response
                if speech_reprompt_response != "":
                    sentence_json["items"][0][
                        "speech_reprompt_response"] = speech_reprompt_response

            need_to_show_auto_fix_popup = False
            if need_to_update_activty_update:
                eng_lang_obj = Language.objects.filter(lang="en").first()
                activity_update = get_bot_response_activity_update_status(
                    bot_response_obj, sentence, card_list, table_input_list_of_list, eng_lang_obj, LanguageTuningBotResponseTable)

                if is_tree_name_updated:
                    update_tree_activity_status(tree_obj, activity_update, eng_lang_obj, LanguageTuningTreeTable)

                bot_response_obj.activity_update = json.dumps(activity_update)

                need_to_show_auto_fix_popup = need_to_show_auto_fix_popup_for_intents(
                    tree_obj.response, activity_update, "en", eng_lang_obj, LanguageTuningBotResponseTable)

            bot_response_obj.sentence = json.dumps(sentence_json)
            bot_response_obj.table = json.dumps(
                {"items": table_input_list_of_list})
            bot_response_obj.images = json.dumps(
                {"items": response_image_list})
            bot_response_obj.videos = json.dumps(
                {"items": response_video_list})
            bot_response_obj.cards = json.dumps({"items": card_list})

            bot_response_obj.save()
            tree_obj.response = bot_response_obj
            tree_obj.save()

            response["status"] = 200
            response["need_to_show_auto_fix_popup"] = need_to_show_auto_fix_popup
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveTreeResponseAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveTreeWidgetAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            tree_pk = data["tree_pk"]
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

            tree_obj = None
            change_data = []
            if tree_pk != None and tree_pk != '':
                tree_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()

            response_obj = None
            if tree_obj.response == None:
                response_obj = BotResponse.objects.create()
            else:
                response_obj = tree_obj.response

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

            response_obj.modes = json.dumps(modes)
            response_obj.modes_param = json.dumps(modes_param)
            response_obj.save()
            tree_obj.response = response_obj            
            tree_obj.save()

            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveTreeWidgetAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveTreeSettingsAPI(APIView):

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
            # print(data["json_string"])

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            tree_pk = data["tree_pk"]
            intent_pk = data["intent_pk"]
            validator_id = data["validator_id"]
            post_processor_variable = data["post_processor_variable"]
            is_go_back_enabled = data["is_go_back_enabled"]
            is_confirmation_and_reset_enabled = data[
                "is_confirmation_and_reset_enabled"]
            is_catalogue_added = data["is_catalogue_added"]
            selected_catalogue_sections = data["selected_catalogue_sections"]
            if selected_catalogue_sections is None:
                selected_catalogue_sections = []
            is_catalogue_purchased = data["is_catalogue_purchased"]

            username = request.user.username
            user_obj = User.objects.filter(username=str(username)).first()
            if user_obj.is_staff:
                flow_analytics_variable = data["flow_analytics_variable"]
                category_response_allowed = data["category_response_allowed"]

            is_last_tree = data["is_last_tree"]
            is_exit_tree = data["is_exit_tree"]
            is_transfer_tree = data["is_transfer_tree"]
            allow_barge = data["allow_barge"]
            disposition_code = data["disposition_code"]
            is_child_tree_visible = data["is_child_tree_visible"]
            is_automatic_recursion_enabled = data[
                'is_automate_recursion_enabled']
            required_analytics_variable = data["required_analytics_variable"]

            child_choices = data["child_choices"]
            child_choices = data["child_choices"]

            if tree_pk != None and tree_pk != '':
                tree_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()

            bot_response_obj = None
            if tree_obj.response == None:
                bot_response_obj = BotResponse.objects.create()
            else:
                bot_response_obj = tree_obj.response

            modes = json.loads(bot_response_obj.modes)
            modes_param = json.loads(bot_response_obj.modes_param)

            modes["is_catalogue_added"] = "true" if is_catalogue_added else "false"
            modes_param["selected_catalogue_sections"] = selected_catalogue_sections
            bot_response_obj.modes_param = json.dumps(modes_param)
            bot_response_obj.modes = json.dumps(modes)

            if user_obj.is_staff:
                tree_obj.is_category_response_allowed = category_response_allowed

            if(validator_id != None and validator_id != ""):
                validator_obj = Processor.objects.filter(pk=int(validator_id)).first()
                tree_obj.post_processor = validator_obj
            else:
                # if there is a previously assigned post_processor, keeping it
                # as it is in case of no validator being selected from console.
                if len(ProcessorValidator.objects.filter(processor=tree_obj.post_processor)) == 0:
                    # tree_obj.post_processor = tree_obj.post_processor
                    if(post_processor_variable != ""):
                        if tree_obj.post_processor != None and tree_obj.post_processor.name == "PostProcessor_" + str(post_processor_variable):
                            pass
                        else:
                            code = "from EasyChatApp.utils import logger\nimport sys\ndef f(x):\n    json_response = {}\n    json_response['status_code'] = '500'\n    json_response['status_message'] = 'Internal server error.'\n    json_response['data'] = {}\n    try:\n        json_response['data']['" + post_processor_variable + \
                                "']=x\n        #write your code here\n        json_response['status_code'] = '200'\n        json_response['print'] = 'Hello world!'\n        return json_response\n    except Exception as E:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('PostProcessorContent: %s at %s',str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        json_response['status_code'] = '500'\n        json_response['status_message'] = 'ERROR :-  '+str(E)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return json_response"
                            processor_obj = Processor.objects.create(name="PostProcessor_" + str(
                                post_processor_variable), function=code, post_processor_direct_value=post_processor_variable)
                            tree_obj.post_processor = processor_obj
                else:
                    tree_obj.post_processor = None

            if is_child_tree_visible != "None":
                if tree_obj.is_child_tree_visible != is_child_tree_visible and is_child_tree_visible:
                    tree_obj.is_child_tree_visible = is_child_tree_visible
                    check_and_update_whatsapp_menu_objs(tree_obj)
                
                tree_obj.is_child_tree_visible = is_child_tree_visible
            if user_obj.is_staff:
                if category_response_allowed:
                    tree_obj.is_child_tree_visible = False

            if user_obj.is_staff:
                if required_analytics_variable:
                    tree_obj.flow_analytics_variable = flow_analytics_variable
                else:
                    tree_obj.flow_analytics_variable = ""

            tree_obj.is_automatic_recursion_enabled = is_automatic_recursion_enabled

            if is_confirmation_and_reset_enabled:
                if tree_obj.is_confirmation_and_reset_enabled == False or (tree_obj.confirmation_reset_tree_pk is None):
                    add_confirmation_and_reset_tree(tree_obj, intent_pk)
            elif is_confirmation_and_reset_enabled == False:
                if tree_obj.is_confirmation_and_reset_enabled == True:
                    remove_confirmation_and_reset_tree(tree_obj)
                else:
                    tree_obj.confirmation_reset_tree_pk = None

            tree_obj.is_last_tree = is_last_tree
            tree_obj.is_exit_tree = is_exit_tree
            tree_obj.enable_transfer_agent = is_transfer_tree
            tree_obj.disposition_code = disposition_code
            tree_obj.is_go_back_enabled = is_go_back_enabled
            tree_obj.is_catalogue_purchased = is_catalogue_purchased

            voice_bot_conf = json.loads(tree_obj.voice_bot_conf)
            voice_bot_conf["barge_in"] = allow_barge
            tree_obj.voice_bot_conf = json.dumps(voice_bot_conf)

            if child_choices != []:
                if len(tree_obj.children.all()) != len(child_choices):
                    response["status"] = 401
                    custom_encrypt_obj = CustomEncrypt()
                    response = custom_encrypt_obj.encrypt(json.dumps(response))
                    bot_response_obj.save()
                    tree_obj.response = bot_response_obj
                    tree_obj.save()
                    return Response(data=response)
                else:
                    bot_response_obj.choices.all().delete()
                    for choices in child_choices:
                        choice_obj = Choice.objects.create(
                            value=choices, display=choices)
                        bot_response_obj.choices.add(choice_obj)
                    response["trigger_flow_change"] = True
            else:
                bot_response_obj.choices.all().delete()

            bot_response_obj.save()
            tree_obj.response = bot_response_obj
            tree_obj.save()

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveTreeAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveTreeQuickRecommendationAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            tree_pk = data["tree_pk"]
            is_recommendation_menu = data["is_recommendation_menu"]

            recommended_intent_list = data["recommended_intent_list"]

            tree_obj = None
            if tree_pk != None and tree_pk != '':
                tree_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()

            response_obj = None
            if tree_obj.response == None:
                response_obj = BotResponse.objects.create()
            else:
                response_obj = tree_obj.response

            response_obj.recommendations = json.dumps(
                {"items": recommended_intent_list})

            modes = json.loads(response_obj.modes)

            if is_recommendation_menu:
                modes["is_recommendation_menu"] = "true"
            else:
                modes["is_recommendation_menu"] = "false"

            response_obj.modes = json.dumps(modes)
            response_obj.save()
            tree_obj.response = response_obj
            tree_obj.save()

            response['status'] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveTreeQuickRecommendationAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveTreeOrderOfResponseAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            tree_pk = data["tree_pk"]
            is_custom_order_selected = data["is_custom_order_selected"]
            order_of_response = data["order_of_response"]
                
            tree_obj = None
            if tree_pk != None and tree_pk != '':
                tree_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()

            tree_obj.is_custom_order_selected = is_custom_order_selected
            tree_obj.order_of_response = json.dumps(order_of_response)

            tree_obj.save()

            response['status'] = 200
        
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveTreeOrderOfResponseAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveTreeConversionFlowDescriptionAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
            
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            explanation = data["explanation"]
            tree_pk = data["tree_pk"]

            tree_obj = None
            if tree_pk != None and tree_pk != '':
                tree_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()

            explanation_obj = None
            if tree_obj.explanation == None:
                explanation_obj = Explanation.objects.create()
            else:
                explanation_obj = tree_obj.explanation

            explanation_obj.explanation = explanation
            explanation_obj.save()
            tree_obj.explanation = explanation_obj

            tree_obj.save()

            response['status'] = 200
        
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveTreeConversionFlowDescriptionAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveFlowAPI(APIView):

    permission_classes = (IsAuthenticated,)

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                return json.loads(data)

            data = DecryptVariable(data["json_string"])
            data = json.loads(data)

            username = request.user.username
            user_obj = User.objects.filter(username=str(username)).first()
            intent_pk = data["intent_pk"]

            flow = data["flow"]

            if intent_pk != None and intent_pk != '':
                intent_obj = Intent.objects.filter(
                    pk=int(intent_pk), is_deleted=False, is_hidden=False).first()

            if flow is None:
                category_obj_pk = data["category_obj_pk"]
                if category_obj_pk == "add_category":
                    response["status"] = 300
                    response["message"] = "Invalid Category!"
                elif isinstance(int(category_obj_pk), int):
                    response["status"] = 200
                    save_intent_category(data, user_obj, intent_obj, Category, save_audit_trail)
                else:
                    response["status"] = 500
                    
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)
            
            save_intent_category(data, user_obj, intent_obj, Category, save_audit_trail)

            first_layer = list(flow.keys())
            if len(first_layer) != 1:
                response["status"] = 300
                response[
                    "message"] = "Invalid Flow!"
                custom_encrypt_obj = CustomEncrypt()
                response = custom_encrypt_obj.encrypt(json.dumps(response))
                return Response(data=response)

            tree_pk = first_layer[0]

            tree_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()

            recurse_tree_save(Tree, tree_obj, tree_pk, flow)

            response["status"] = 200
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveFlowAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


class SaveTreeWhatsappMenuFormatAPI(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            validation_obj = EasyChatInputValidation()

            json_string = DecryptVariable(data["json_string"])
            data = json.loads(json_string)
        
            json_string = validation_obj.custom_remo_html_tags(json_string)
            data = json.loads(json_string)

            enable_whatsapp_menu_format = data["enable_whatsapp_menu_format"]
            tree_pk = data["tree_pk"]
            whatsapp_list_message_header = data["whatsapp_list_message_header"]

            tree_obj = None
            if tree_pk != None and tree_pk != '':
                tree_obj = Tree.objects.filter(pk=int(tree_pk), is_deleted=False).first()

                tree_obj.enable_whatsapp_menu_format = enable_whatsapp_menu_format
                if enable_whatsapp_menu_format and tree_obj.response:
                    response_obj = tree_obj.response
                    response_obj.whatsapp_list_message_header = whatsapp_list_message_header
                    response_obj.save(update_fields=["whatsapp_list_message_header"])

            tree_obj.save(update_fields=["enable_whatsapp_menu_format"])
            response['status'] = 200
            response["tree_pk"] = tree_obj.pk
        
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error SaveTreeWhatsappMenuFormatAPI %s %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(request.user.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_objs[0].pk)})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


SaveWhatsAppMenuSection = SaveWhatsAppMenuSectionAPI.as_view()

DeleteWhatsAppMenuSection = DeleteWhatsAppMenuSectionAPI.as_view()

RenameTree = RenameTreeAPI.as_view()

DeleteTreeNode = DeleteTreeNodeAPI.as_view()

DeleteTree = DeleteTreeAPI.as_view()

CreateTree = CreateTreeAPI.as_view()

PasteTreeNode = PasteTreeNodeAPI.as_view()

InsertTree = InsertTreeAPI.as_view()

FetchTreeInformation = FetchTreeInformationAPI.as_view()

SaveTree = SaveTreeAPI.as_view()

FetchAllChoice = FetchAllChoiceAPI.as_view()

AddNewChoice = AddNewChoiceAPI.as_view()

SaveTreeResponse = SaveTreeResponseAPI.as_view()

SaveTreeWidget = SaveTreeWidgetAPI.as_view()

SaveTreeSettings = SaveTreeSettingsAPI.as_view()

SaveTreeQuickRecommendation = SaveTreeQuickRecommendationAPI.as_view()

SaveTreeOrderOfResponse = SaveTreeOrderOfResponseAPI.as_view()

SaveTreeConversionFlowDescription = SaveTreeConversionFlowDescriptionAPI.as_view()

SaveFlow = SaveFlowAPI.as_view()

SaveTreeWhatsappMenuFormat = SaveTreeWhatsappMenuFormatAPI.as_view()
