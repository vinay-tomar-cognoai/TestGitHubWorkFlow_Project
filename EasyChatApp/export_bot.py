from EasyChatApp.models import *
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from EasyChatApp.cryptography import encrypt_long_text
from EasyChatApp.constants import ALEXA_TRAINING_JSON, EXPORT_BOT_AS_MULITILINGUAL_EXCEL_INSTRUCTIONS
from EasyChatApp.utils_bot import get_multilingual_auto_popup_response, get_supported_languages
from EasyChatApp.utils import send_otp_mail

from django.core import serializers
from time import gmtime, strftime
from django.http import HttpResponse

import re
import sys
import os
import json
import logging
import requests
import shutil
import datetime
from bs4 import BeautifulSoup
from xlwt import Workbook
from EasyChat.settings import BASE_DIR

logger = logging.getLogger(__name__)


def clear_temporary_file():
    try:
        shutil.rmtree(settings.MEDIA_ROOT + '/temporary')
        os.makedirs(settings.MEDIA_ROOT + '/temporary')
    except Exception:
        pass


def get_temp_file_path(path):
    try:
        from urllib.parse import urlparse
        file_path = urlparse(str(path))
        if file_path.hostname != settings.EASYCHAT_DOMAIN:
            return "None"
        return settings.BASE_DIR + file_path.path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_temp_file_path: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return "None"


"""
function: json_serialize
input params:
    objects: object which has to be json serialized
output params:
    returns json serialize data
"""


def json_serialize(objects):
    return json.loads(str(serializers.serialize("json", objects)))


"""
function: export_data
input params:
    bot_slug: slug of the bot which has to be exported
    username: default is None (optional)

generates jsonfile containing bot data in encrypted form
"""


def export_data(bot_slug, bot_pk, username=None):
    try:

        data = get_bot_data(bot_slug, bot_pk, username)

        if bot_slug == None:
            bot_slug = str(username)

        import datetime
        current_datetime_str = datetime.datetime.strftime(
            datetime.datetime.now(), "%Y-%m-%d_%H-%M-%S")
        filename = "easychat_datadump_" + \
            str(bot_slug) + "_" + str(current_datetime_str) + ".json"

        if not os.path.exists('secured_files/EasyChatApp/exported_bot'):
            os.makedirs('secured_files/EasyChatApp/exported_bot')

        with open(settings.SECURE_MEDIA_ROOT + "EasyChatApp/exported_bot/" + filename, "w+") as dumpfile:
            dumpfile.write(data)
            dumpfile.close()

        path = '/secured_files/EasyChatApp/exported_bot/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_public=True, is_customer_attachment=True)

        file_url = 'chat/download-file/' + \
            str(file_access_management_obj.key) + '/' + filename

        licence_filename = None
        if username != None:
            licence_filename = "licence_" + current_datetime_str + ".key"
            with open(settings.MEDIA_ROOT + "private/" + licence_filename, "w+") as licence_file:
                encrypted_data = encrypt_long_text(
                    data, settings.MEDIA_ROOT + "private/allincall_public_key.pem")
                logger.info("EasyChat Licence File Encrypted Successfully.", extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                licence_file.write(encrypted_data)
                licence_file.close()

        return file_url, licence_filename

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_data: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: export_data
input params:
    bot_slug: slug of the bot which has to be exported
    username: default is None (optional)

generates jsonfile containing bot data in encrypted form
"""


def export_data_as_zip(bot_slug, bot_pk, username=None):
    try:
        import os
        import zipfile
        from io import BytesIO

        import datetime
        current_datetime_str = datetime.datetime.strftime(
            datetime.datetime.now(), "%Y-%m-%d_%H-%M-%S")
        zip_subdir = "easychat_datadump"
        zip_dir = zip_subdir + "_" + \
            str(bot_slug) + "_" + str(current_datetime_str)
        zip_filename = "%s.zip" % zip_dir

        bytes_io = BytesIO()
        zf = zipfile.ZipFile(bytes_io, "w")

        data = get_bot_data(bot_slug, bot_pk, username)

        filename = "easychat_datadump.json"
        with open(settings.MEDIA_ROOT + "private/" + filename, "w+") as dumpfile:
            dumpfile.write(data)
            dumpfile.close()

        json_filepath = settings.MEDIA_ROOT + "private/" + filename
        filedir, filename = os.path.split(json_filepath)
        zip_path = os.path.join(zip_subdir, filename)

        zf.write(json_filepath, zip_path)
        zf.close()

        clear_temporary_file()

        default_storage.save(
            "private/" + zip_filename, ContentFile(bytes_io.getvalue()))

        return zip_filename, bytes_io

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_data_as_zip: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return "None", "None"


"""
function: export_faq_excel
input params:
    uat_bot_obj: uat bot object whose intent data to be downloaded

generates excel file containing intent data of that bot data
"""


def export_faq_excel(uat_bot_obj):
    try:
        export_faq_wb = Workbook()
        sheet_name = str(uat_bot_obj.slug) + " FAQs"
        sheet1 = export_faq_wb.add_sheet(sheet_name)
        sheet1.write(0, 0, "Question")
        sheet1.write(0, 1, "Variation")
        sheet1.write(0, 2, "Answer")
        sheet1.write(0, 3, "Recommendations")
        sheet1.write(0, 4, "Category")
        sheet1.write(0, 5, "Cards")
        sheet1.write(0, 6, "Images")
        sheet1.write(0, 7, "Videos")
        sheet1.write(0, 8, "Channel")

        index = 0
        for intent in Intent.objects.filter(bots__in=[uat_bot_obj], is_deleted=False, is_hidden=False).distinct():
            intent_name = intent.name
            intent_training_data = json.loads(intent.training_data)

            training_data_list = []
            for key in intent_training_data:
                training_data_list.append(intent_training_data[key])

            training_data_str = "$$$".join(training_data_list)

            if not intent.tree.response:
                logger.error("in export faq excel response not found for intent: %s at",
                             str(intent.tree), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                continue

            response = json.loads(intent.tree.response.sentence)["items"]
            text_response = response[0]["text_response"]

            cards = json.loads(intent.tree.response.cards)["items"]
            card_list = []

            for card in cards:
                title = card["title"]
                content = card["content"]
                url = card["link"]
                img_url = card["img_url"]

                card_list.append(title + "$$$" + content +
                                 "$$$" + url + "$$$" + img_url)

            card_list_str = "@@@".join(card_list)

            image_list_str, video_list_str, recommendation_list_str = "", "", ""

            try:
                images = json.loads(intent.tree.response.images)["items"]
                image_list_str = "$$$".join(images)
            except Exception:  # noqa: F841
                pass

            try:
                videos = json.loads(intent.tree.response.videos)["items"]
                video_list_str = "$$$".join(videos)
            except Exception:  # noqa: F841
                pass

            try:
                recommendation_list_str = "$$$".join(
                    intent.get_recommendations())
            except Exception:
                pass

            category_name = ""
            if intent.category:
                category_name = intent.category.name

            channel_str = "all"

            if Channel.objects.filter(is_easychat_channel=True).count() != intent.channels.all().count():
                channel_str = intent.get_comma_seprated_supported_channel_name()

            sheet1.write(index + 1, 0, intent_name)
            sheet1.write(index + 1, 1, training_data_str)
            sheet1.write(index + 1, 2, text_response)
            sheet1.write(index + 1, 3, recommendation_list_str)
            sheet1.write(index + 1, 4, category_name)
            sheet1.write(index + 1, 5, card_list_str)
            sheet1.write(index + 1, 6, image_list_str)
            sheet1.write(index + 1, 7, video_list_str)
            sheet1.write(index + 1, 8, channel_str)
            index += 1

        current_datetime_str = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
        filename = str(uat_bot_obj.slug) + "_" + \
            str(current_datetime_str) + ".xls"

        if not os.path.exists('secured_files/EasyChatApp/exported_bot'):
            os.makedirs('secured_files/EasyChatApp/exported_bot')

        export_faq_wb.save(settings.SECURE_MEDIA_ROOT +
                           "EasyChatApp/exported_bot/" + filename)

        path = '/secured_files/EasyChatApp/exported_bot/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_public=True, is_customer_attachment=True)

        file_url = 'chat/download-file/' + \
            str(file_access_management_obj.key) + '/' + filename

        return file_url
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_faq_excel: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


def get_language_tuned_intent_name(intent, language):
    multilingual_intent_name = ""
    try:
        language_tuned_object = LanguageTuningIntentTable.objects.filter(
            intent=intent, language=language)
        if language_tuned_object.exists():
            language_tuned_object = language_tuned_object.first()
            multilingual_intent_name = language_tuned_object.multilingual_name
        return multilingual_intent_name
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_language_tuned_intent_name: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        multilingual_intent_name = ""
    return multilingual_intent_name


def get_language_tuned_tree_name(tree, language):
    multilingual_tree_name = ""
    try:
        language_tuned_object = LanguageTuningTreeTable.objects.filter(
            tree=tree, language=language)
        if language_tuned_object.exists():
            language_tuned_object = language_tuned_object.first()
            multilingual_tree_name = language_tuned_object.multilingual_name
        return multilingual_tree_name
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_language_tuned_tree_name: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        multilingual_tree_name = ""
    return multilingual_tree_name


def get_multilingual_bot_text_response(response_obj, language):
    multilingual_text_response = ""
    try:
        language_tuned_object = LanguageTuningBotResponseTable.objects.filter(
            bot_response=response_obj, language=language)
        if language_tuned_object.exists():
            language_tuned_object = language_tuned_object.first()
            multilingual_text_response = json.loads(language_tuned_object.sentence)[
                "items"][0]["text_response"]
        return multilingual_text_response
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_multilingual_bot_text_response: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        multilingual_text_response = ""
    return multilingual_text_response


def write_multilingual_intent_in_sheet(intent, tree_obj, intent_trans_sheet, response_trans_sheet, row, supported_languages, tree_pk_list=[]):
    try:
        intent_tree_pk = str(intent.pk) + "," + str(tree_obj.pk)
        intent_trans_sheet.write(row, 0, intent_tree_pk)
        intent_trans_sheet.write(row, 1, tree_obj.name)
        response_obj = tree_obj.response
        response_trans_sheet.write(row, 0, response_obj.pk)
        response = json.loads(response_obj.sentence)["items"]
        text_response = response[0]["text_response"]
        text_response = BeautifulSoup(text_response).text.strip()
        response_trans_sheet.write(row, 1, text_response)
        col = 2
        for language in supported_languages:
            if language.lang == "en":
                continue
            lang_intent_name = get_language_tuned_tree_name(tree_obj, language)
            intent_trans_sheet.write(row, col, lang_intent_name)
            multilingual_bot_response = get_multilingual_bot_text_response(
                response_obj, language)
            multilingual_bot_response = BeautifulSoup(
                multilingual_bot_response).text.strip()
            response_trans_sheet.write(row, col, multilingual_bot_response)
            col = col + 1
        tree_pk_list.append(tree_obj.pk)
        if tree_obj.children.exists():
            for child in tree_obj.children.all():
                # recursively writing all the children objects as well
                if child.pk not in tree_pk_list:
                    row = write_multilingual_intent_in_sheet(
                        intent, child, intent_trans_sheet, response_trans_sheet, row + 1, supported_languages, tree_pk_list)
            pass
        return row
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("write_multilingual_intent_in_sheet: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return row


def export_multilingual_intent_excel(bot_obj):
    try:
        export_multilingual_wb = Workbook()
        worksheet_names = ['Instruction',
                           'Intent Translation', 'Response Translation']

        for name in worksheet_names:
            export_multilingual_wb.add_sheet(name)
        instruction_sheet = export_multilingual_wb.get_sheet(0)
        instruction_sheet.write(0, 0, "S.No")
        instruction_sheet.write(0, 1, "Instrcutions/Suggestions")
        row = 1
        for instruction in EXPORT_BOT_AS_MULITILINGUAL_EXCEL_INSTRUCTIONS:
            instruction_sheet.write(row, 0, row)
            instruction_sheet.write(row, 1, instruction)
            row = row + 1
        supported_languages = get_supported_languages(bot_obj, BotChannel)

        intent_trans_sheet = export_multilingual_wb.get_sheet(1)
        intent_trans_sheet.write(0, 0, "Intent and Tree Primary Key")
        intent_trans_sheet.write(0, 1, "Intent/Tree Name (English)")
        col = 2
        for language in supported_languages:
            if language.lang == "en":
                continue
            lang_col_name = str(language.display) + "-" + str(language.lang)
            intent_trans_sheet.write(0, col, lang_col_name)
            col = col + 1
        response_trans_sheet = export_multilingual_wb.get_sheet(2)
        response_trans_sheet.write(0, 0, "Response Primary Key")
        response_trans_sheet.write(0, 1, "Response (English)")
        col = 2
        for language in supported_languages:
            if language.lang == "en":
                continue
            lang_col_name = str(language.display) + "-" + str(language.lang)
            response_trans_sheet.write(0, col, lang_col_name)
            col = col + 1

        row = 1
        for intent in Intent.objects.filter(bots__in=[bot_obj], is_deleted=False, is_hidden=False).distinct():
            row = write_multilingual_intent_in_sheet(
                intent, intent.tree, intent_trans_sheet, response_trans_sheet, row, supported_languages)
            row = row + 1

        current_datetime_str = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
        filename = str(bot_obj.slug) + "_" + \
            str(current_datetime_str) + ".xls"

        if not os.path.exists('secured_files/EasyChatApp/exported_bot'):
            os.makedirs('secured_files/EasyChatApp/exported_bot')

        export_multilingual_wb.save(
            settings.SECURE_MEDIA_ROOT + "EasyChatApp/exported_bot/" + filename)

        path = '/secured_files/EasyChatApp/exported_bot/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_public=True, is_customer_attachment=True)

        file_url = 'chat/download-file/' + \
            str(file_access_management_obj.key) + '/' + filename

        return file_url
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_multilingual_intent_excel: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


def generate_alexa_training_json(bot_id, Bot, Intent):
    file_url = None
    try:
        bot_obj = Bot.objects.get(pk=int(bot_id))
        bot_name = bot_obj.name
        bot_name = re.sub('[^A-Za-z ]', ' ', bot_name)

        training_data_list = []

        for intent in Intent.objects.filter(bots__in=[bot_obj], is_deleted=False):

            training_data = json.loads(intent.training_data)

            for key in training_data:

                value = training_data[key]
                value = re.sub('[^A-Za-z ]', ' ', value)

                training_data_list.append({
                    "name": {
                        "value": value
                    }
                })

        ALEXA_TRAINING_JSON["interactionModel"]["languageModel"][
            "types"][0]["values"] = training_data_list
        ALEXA_TRAINING_JSON["interactionModel"][
            "languageModel"]["invocationName"] = bot_name

        filename = f'alexa-{str(bot_id)}.json'

        if not os.path.exists('secured_files/EasyChatApp/exported_bot'):
            os.makedirs('secured_files/EasyChatApp/exported_bot')

        with open(settings.SECURE_MEDIA_ROOT + "EasyChatApp/exported_bot/" + filename, "w+") as dumpfile:
            dumpfile.write(json.dumps(ALEXA_TRAINING_JSON, indent=4))
            dumpfile.close()

        path = '/secured_files/EasyChatApp/exported_bot/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_public=True, is_customer_attachment=True)

        file_url = 'chat/download-file/' + \
            str(file_access_management_obj.key) + '/' + filename

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("generate_alexa_training_json: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        file_url = None

    return file_url


def export_intent(intent_pk):
    try:

        # Intent Details
        intent_obj = Intent.objects.get(
            pk=intent_pk, is_deleted=False)

        tree_objs_list = []
        bot_response_objs_list = []
        processor_objs_list = []
        api_tree_objs_list = []

        def get_tree_objs_list(current_tree_obj):

            if current_tree_obj == None:
                return

            if current_tree_obj not in tree_objs_list:
                tree_objs_list.append(current_tree_obj)

                if current_tree_obj.response != None:
                    bot_response_objs_list.append(current_tree_obj.response)

                if current_tree_obj.pre_processor != None:
                    processor_objs_list.append(current_tree_obj.pre_processor)

                if current_tree_obj.pipe_processor != None:
                    processor_objs_list.append(current_tree_obj.pipe_processor)

                if current_tree_obj.post_processor != None:
                    processor_objs_list.append(current_tree_obj.post_processor)

                if current_tree_obj.api_tree != None:
                    api_tree_objs_list.append(current_tree_obj.api_tree)

            child_tree_objs = current_tree_obj.children.all()

            for child_tree in child_tree_objs:

                if child_tree not in tree_objs_list:

                    tree_objs_list.append(child_tree)

                    if child_tree.response != None:
                        bot_response_objs_list.append(child_tree.response)

                    if child_tree.pre_processor != None:
                        processor_objs_list.append(child_tree.pre_processor)

                    if child_tree.pipe_processor != None:
                        processor_objs_list.append(child_tree.pipe_processor)

                    if child_tree.post_processor != None:
                        processor_objs_list.append(child_tree.post_processor)

                    if child_tree.api_tree != None:
                        api_tree_objs_list.append(child_tree.api_tree)

                    get_tree_objs_list(child_tree)

        get_tree_objs_list(intent_obj.tree)
        channel_objs_list = Channel.objects.filter(
            is_easychat_channel=True).distinct()
        channel_json_data_list = json_serialize(channel_objs_list)
        logger.info("Channel objects are exported successfully.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        processor_json_data_list = json_serialize(processor_objs_list)
        logger.info("Processor objects are exported successfully.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        choice_objs_list = []
        for bot_response_obj in bot_response_objs_list:
            choice_objs_list += bot_response_obj.choices.all()

        choice_json_data_list = json_serialize(choice_objs_list)
        logger.info("Choice objects are exported successfully.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        bot_response_json_data_list = json_serialize(bot_response_objs_list)
        logger.info("BotResponse objects are exported successfully.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        api_tree_json_data_list = json_serialize(api_tree_objs_list)
        logger.info("ApiTree objects are exported successfully.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        tree_objs_list.reverse()
        tree_json_data_list = json_serialize(tree_objs_list)
        tree_json_data_list = sorted(
            tree_json_data_list, key=lambda x: x["pk"])
        logger.info(json.dumps(tree_json_data_list), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        logger.info("Tree objects are exported successfully.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        tag_mapper_objs_list = TagMapper.objects.filter(
            api_tree__in=api_tree_objs_list).distinct()
        tag_mapper_json_data_list = json_serialize(tag_mapper_objs_list)
        logger.info("TagMapper objects are exported successfully.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        category_objs_list = []
        if intent_obj.category != None:
            category_objs_list += [intent_obj.category]

        category_json_data_list = json_serialize(category_objs_list)
        logger.info("Category objects are exported successfully.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        intent_json_data_list = json_serialize([intent_obj])
        logger.info("Intent objects are exported successfully.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        processor_validator_objs_list = ProcessorValidator.objects.filter(
            processor__in=processor_objs_list).distinct()
        processor_validator_json_data_list = json_serialize(
            processor_validator_objs_list)
        logger.info("ProcessorValidator objects are exported successfully.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        json_data_dict = {
            "easychat_channels": channel_json_data_list,
            "easychat_processors": processor_json_data_list,
            "easychat_choices": choice_json_data_list,
            "easychat_botresponses": bot_response_json_data_list,
            "easychat_apitrees": api_tree_json_data_list,
            "easychat_trees": tree_json_data_list,
            "easychat_tagmappers": tag_mapper_json_data_list,
            "easychat_intents": intent_json_data_list,
            "easychat_processor_validators": processor_validator_json_data_list,
            "easychat_category": category_json_data_list,
        }

        data = json.dumps(json_data_dict, indent=4)

        current_datetime_str = datetime.datetime.strftime(
            datetime.datetime.now(), "%Y-%m-%d_%H-%M-%S")
        filename = "easychat_datadump_" + \
            str(intent_pk) + "_" + str(current_datetime_str) + ".json"

        with open(settings.MEDIA_ROOT + "private/" + filename, "w+") as dumpfile:
            dumpfile.write(data)
            dumpfile.close()

        return filename

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_intent: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def export_large_bot(bot_obj, email_id, export_type, username=None):
    try:
        if export_type == '0':
            filename, _ = export_data(bot_obj.slug, bot_obj.pk, None)

        elif export_type == '1':
            filename, _ = export_data_as_zip(bot_obj.slug, bot_obj.pk)
            filename = 'files/private/' + filename

        elif export_type == '2':
            filename = export_faq_excel(bot_obj)

        elif export_type == '3':
            filename = generate_alexa_training_json(bot_obj.pk, Bot, Intent)

        else:
            filename = export_multilingual_intent_excel(bot_obj)

        subject = 'Export Bot'

        content = f'Hi, <br> Your bot {bot_obj.name} has been exported successfully. Please click below to download the file.\
                    <br> <a href="{settings.EASYCHAT_HOST_URL}/{filename}" download>Click Here</a>'

        send_otp_mail([email_id], subject, content)
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_large_bot: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_updated_welcomebanner_json_list(welcome_banners):
    try:
        for welcome_banner in welcome_banners:
            bot_channel_pk = welcome_banner['fields']['bot_channel']
            bot_channel_obj = BotChannel.objects.get(pk=bot_channel_pk)
            welcome_banner['fields']['channel_name'] = bot_channel_obj.channel.name

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_large_bot: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return welcome_banners


def get_updated_nps_json_list(nps_objs):
    try:
        for nps_obj in nps_objs:
            channels = nps_obj['fields']['channel']
            channel_names = []
            for channel in channels:
                channel_obj = Channel.objects.get(pk=int(channel))
                channel_names.append(channel_obj.name)
            nps_obj['fields']['channel_names'] = channel_names

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_large_bot: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return nps_objs


def get_bot_data(bot_slug, bot_pk, username=None):
    user_obj_list = None
    if username:
        user_obj_list = User.objects.filter(username=username)

    logger.info("User objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    # Get Bot Details
    bot_objs_list = []

    def get_bot_objs_list(current_bot_obj):

        if current_bot_obj == None:
            return

        if current_bot_obj not in bot_objs_list:
            bot_objs_list.append(current_bot_obj)

        child_bots = current_bot_obj.child_bots.all()

        for child_bot in child_bots:
            if child_bot not in bot_objs_list:
                bot_objs_list.append(child_bot)
                get_bot_objs_list(child_bot)

    bot_objs = []
    if username == None:
        bot_objs = Bot.objects.filter(
            slug=bot_slug, is_uat=True, is_deleted=False)
    else:
        bot_objs = Bot.objects.filter(users__in=user_obj_list).distinct()

    for bot_obj in bot_objs:
        get_bot_objs_list(bot_obj)

    bot_objs_list.reverse()
    bot_json_data_list = json_serialize(bot_objs_list)
    logger.info("Bot objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    try:
        bot_selected_theme = bot_objs_list[0].default_theme.name
        bot_json_data_temp = bot_json_data_list[0]
        bot_json_data_temp["fields"]["default_theme"] = str(
            bot_selected_theme)
        bot_json_data_temp = json.dumps(bot_json_data_temp)
        bot_json_data_temp = json.loads(bot_json_data_temp)
    except Exception:
        pass

    # Channel List Objects
    channel_objs_list = Channel.objects.filter(
        is_easychat_channel=True).distinct()
    channel_json_data_list = json_serialize(channel_objs_list)
    logger.info("Channel objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    # WordMapper Details
    word_mapper_objs_list = WordMapper.objects.filter(
        bots__in=bot_objs_list).distinct()
    word_mapper_json_data_list = json_serialize(word_mapper_objs_list)
    logger.info("WordMapper objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    # BotChannel Details
    botchannel_objs_list = BotChannel.objects.filter(
        bot__in=bot_objs_list, channel__in=channel_objs_list).distinct()
    botchannel_json_data_list = json_serialize(botchannel_objs_list)
    logger.info("BotChannel objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    # WelcomeBanner Details
    welcomebanner_objs_list = WelcomeBanner.objects.filter(
        bot_channel__in=botchannel_objs_list)
    welcomebanner_json_data_list = json_serialize(welcomebanner_objs_list)
    welcomebanner_json_data_list = get_updated_welcomebanner_json_list(
        welcomebanner_json_data_list)
    logger.info("WelcomeBanner objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    # EmojiBotResponse Details
    emoji_bot_response_objs = EmojiBotResponse.objects.filter(
        bot__in=bot_objs_list)
    emoji_bot_response_json_data_list = json_serialize(emoji_bot_response_objs)
    logger.info("EmojiBotResponse objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    # AnalyticsMonitoring Details
    analytics_monitoring_objs = AnalyticsMonitoring.objects.filter(
        bot__in=bot_objs_list)
    analytics_monitoring_json_list = json_serialize(analytics_monitoring_objs)
    logger.info("AnalyticsMonitoring objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    # NPS Details
    nps_objs = NPS.objects.filter(bot__in=bot_objs_list)
    nps_objs_json_list = json_serialize(nps_objs)
    nps_objs_json_list = get_updated_nps_json_list(nps_objs_json_list)
    logger.info("NPS objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    # CSAT Feedback Details
    csat_feedback_objs = CSATFeedBackDetails.objects.filter(
        bot_obj__in=bot_objs_list)
    csat_feedback_objs = json_serialize(csat_feedback_objs)
    logger.info("CSATFeedBackDetails objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    # Intent Details
    intent_objs_list = Intent.objects.filter(
        bots__in=bot_objs_list, is_deleted=False).distinct()

    tree_objs_list = []
    bot_response_objs_list = []
    processor_objs_list = []
    api_tree_objs_list = []

    def get_tree_objs_list(current_tree_obj):

        if current_tree_obj == None:
            return

        if current_tree_obj not in tree_objs_list:
            tree_objs_list.append(current_tree_obj)

            if current_tree_obj.response != None:
                bot_response_objs_list.append(current_tree_obj.response)

            if current_tree_obj.pre_processor != None:
                processor_objs_list.append(current_tree_obj.pre_processor)

            if current_tree_obj.pipe_processor != None:
                processor_objs_list.append(current_tree_obj.pipe_processor)

            if current_tree_obj.post_processor != None:
                processor_objs_list.append(current_tree_obj.post_processor)

            if current_tree_obj.api_tree != None:
                api_tree_objs_list.append(current_tree_obj.api_tree)

        child_tree_objs = current_tree_obj.children.all()

        for child_tree in child_tree_objs:

            if child_tree not in tree_objs_list:

                tree_objs_list.append(child_tree)

                if child_tree.response != None:
                    bot_response_objs_list.append(child_tree.response)

                if child_tree.pre_processor != None:
                    processor_objs_list.append(child_tree.pre_processor)

                if child_tree.pipe_processor != None:
                    processor_objs_list.append(child_tree.pipe_processor)

                if child_tree.post_processor != None:
                    processor_objs_list.append(child_tree.post_processor)

                if child_tree.api_tree != None:
                    api_tree_objs_list.append(child_tree.api_tree)

                get_tree_objs_list(child_tree)

    for intent in intent_objs_list:
        get_tree_objs_list(intent.tree)

    authentication_objs_list = Authentication.objects.filter(
        bot__in=bot_objs_list)

    for authentication_obj in authentication_objs_list:
        get_tree_objs_list(authentication_obj.tree)

    processor_json_data_list = json_serialize(processor_objs_list)
    logger.info("Processor objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    choice_objs_list = []
    for bot_response_obj in bot_response_objs_list:
        choice_objs_list += bot_response_obj.choices.all()

    choice_json_data_list = json_serialize(choice_objs_list)
    logger.info("Choice objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    bot_response_json_data_list = json_serialize(bot_response_objs_list)
    logger.info("BotResponse objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    api_tree_json_data_list = json_serialize(api_tree_objs_list)
    logger.info("ApiTree objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    tree_objs_list.reverse()
    tree_json_data_list = json_serialize(tree_objs_list)
    tree_json_data_list = sorted(
        tree_json_data_list, key=lambda x: x["pk"])
    logger.info(json.dumps(tree_json_data_list), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    logger.info("Tree objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    authentication_json_data_list = json_serialize(
        authentication_objs_list)
    logger.info("Authentication objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    user_authentication_objs_list = UserAuthentication.objects.filter(
        auth_type__in=authentication_objs_list)
    user_authentication_json_data_list = json_serialize(
        user_authentication_objs_list)
    logger.info("UserAuthentication objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    data_json_data_list = []
    # data_objs_list = Data.objects.all()
    # data_json_data_list = json_serialize(data_objs_list)
    logger.info("Data objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    languages_objs_list = Language.objects.all()
    languages_json_data_list = json_serialize(languages_objs_list)
    logger.info("Language objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    mis_dashboard_json_data_list = []

    logger.info("MISDashboard objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    tag_mapper_objs_list = TagMapper.objects.filter(
        api_tree__in=api_tree_objs_list).distinct()
    tag_mapper_json_data_list = json_serialize(tag_mapper_objs_list)
    logger.info("TagMapper objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    category_objs_list = []
    for intent_obj in intent_objs_list:
        if intent_obj.category != None:
            category_objs_list += [intent_obj.category]

    category_json_data_list = json_serialize(category_objs_list)
    logger.info("Category objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    intent_json_data_list = json_serialize(intent_objs_list)
    # logger.info(intent_json_data_list)
    logger.info("Intent objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    test_case_json_data_list = []
    # test_case_objs_list = TestCase.objects.filter(
    #    intent__in=intent_objs_list).distinct()
    # test_case_json_data_list = json_serialize(test_case_objs_list)
    logger.info("TestCase objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    training_template_sentence_json_data_list = []
    # training_template_sentence_objs_list = TrainingTemplateSentence.objects.all()
    # training_template_sentence_json_data_list = json_serialize(
    #    training_template_sentence_objs_list)
    logger.info(
        "TrainingTemplateSentence objects are exported successfully.", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    training_template_json_data_list = []
    # training_template_objs_list = TrainingTemplate.objects.all()
    # training_template_json_data_list = json_serialize(
    #    training_template_objs_list)
    logger.info("TrainingTemplate objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    processor_validator_objs_list = ProcessorValidator.objects.filter(
        processor__in=processor_objs_list).distinct()
    processor_validator_json_data_list = json_serialize(
        processor_validator_objs_list)
    logger.info("ProcessorValidator objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    feedback_json_data_list = []
    # feedback_objs_list = Feedback.objects.all()
    # feedback_json_data_list = json_serialize(feedback_objs_list)
    logger.info("Feedback objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    word_dict_objs_list = WordDictionary.objects.all()
    word_dict_json_data_list = json_serialize(word_dict_objs_list)
    logger.info("WordDictionary objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    default_intent_json_data_list = []
    # default_intent_objs_list = DefaultIntent.objects.all()
    # default_intent_json_data_list = json_serialize(
    #     default_intent_objs_list)
    logger.info("DefaultIntent objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    form_assist_objs_list = FormAssist.objects.filter(
        bot__in=bot_objs_list)
    form_assist_json_data_list = json_serialize(form_assist_objs_list)
    logger.info("FormAssist objects are exported successfully.", extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    common_utils_content = ""
    try:
        common_utils_content = CommonUtilsFile.objects.get(
            bot=Bot.objects.get(pk=bot_pk)).code
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Common Utils export: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        pass

    json_data_dict = {
        "easychat_channels": channel_json_data_list,
        "easychat_bots": bot_json_data_list,
        "easychat_wordmappers": word_mapper_json_data_list,
        "easychat_botchannels": botchannel_json_data_list,
        "easychat_welcomebanners": welcomebanner_json_data_list,
        "easychat_processors": processor_json_data_list,
        "easychat_choices": choice_json_data_list,
        "easychat_botresponses": bot_response_json_data_list,
        "easychat_emojibotresponse": emoji_bot_response_json_data_list,
        "easychat_apitrees": api_tree_json_data_list,
        "easychat_trees": tree_json_data_list,
        "easychat_authentications": authentication_json_data_list,
        "easychat_userauthentications": user_authentication_json_data_list,
        "easychat_data": data_json_data_list,
        "easychat_languages": languages_json_data_list,
        "easychat_misdashboard": mis_dashboard_json_data_list,
        "easychat_tagmappers": tag_mapper_json_data_list,
        "easychat_intents": intent_json_data_list,
        "easychat_testcases": test_case_json_data_list,
        "easychat_trainingtemplatesentence": training_template_sentence_json_data_list,
        "easychat_trainingsentence": training_template_json_data_list,
        "easychat_processor_validators": processor_validator_json_data_list,
        "easychat_feedbacks": feedback_json_data_list,
        "easychat_worddict": word_dict_json_data_list,
        "easychat_defaultintents": default_intent_json_data_list,
        "easychat_formassist": form_assist_json_data_list,
        "easychat_category": category_json_data_list,
        "easychat_analyticsmonitoring": analytics_monitoring_json_list,
        "easychat_nps": nps_objs_json_list,
        "easychat_csatfeedbackdetails": csat_feedback_objs,
        "content": common_utils_content
    }

    data = json.dumps(json_data_dict, indent=4)
    return data
