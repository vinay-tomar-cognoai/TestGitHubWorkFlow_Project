from EasyChatApp.models import *
from EasyChat.settings import EASYCHAT_HOST_URL
from EasyChatApp.utils_analytics import remove_whitespace, embed_url, get_stem_words_of_sentence
from EasyChatApp.utils_paraphrase import make_final_variations
from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.constants import *

import xlrd
import json
import sys
import logging
import os
import requests
import datetime

logger = logging.getLogger(__name__)

"""
Stores the static file to local system using url
"""

"""
function: store_this_data_locally
input params:
    url: url for that file

returns url of static file in local system
"""


def store_this_data_locally(url):
    if url == "":
        return url

    filedir, filename = os.path.split(url)
    file_to_store = requests.get(url)
    open(settings.MEDIA_ROOT + filename, 'wb').write(file_to_store.content)

    return EASYCHAT_HOST_URL + "/files/" + filename


"""
create flow with excel supports flow creation upto two level
"""

"""
function: create_intent_for_user_flow
input params:
    intent_name: name of intent
    bot_objs_list: list of bot objects
    category: category of intent

returns newly created intent object and added to bots
"""


def create_intent_for_user_flow(intent_name, bot_objs_list, category):
    intent_obj = Intent.objects.filter(
        name=intent_name, bots=bot_objs_list[0], is_deleted=False)
    if intent_obj:
        intent_obj = intent_obj[0]
    else:
        stem_words = get_stem_words_of_sentence(
            intent_name, None, None, None, bot_objs_list[0])
        stem_words.sort()
        hashed_name = ' '.join(stem_words)
        hashed_name = hashlib.md5(hashed_name.encode()).hexdigest()
        intent_obj = Intent.objects.create(
            name=intent_name, intent_hash=hashed_name, training_data=json.dumps({"0": intent_name}))

        for bot_obj in bot_objs_list:
            if category is None:
                intent_obj.bots.add(bot_obj)
                intent_obj.category = None
            else:
                category_obj = Category.objects.filter(
                    name=category, bot=bot_obj)

                if category_obj.count() > 0:
                    intent_obj.bots.add(bot_obj)
                    intent_obj.category = category_obj[0]
                else:
                    category_obj = Category.objects.create(
                        name=category, bot=bot_obj)
                    intent_obj.bots.add(bot_obj)
                    intent_obj.category = category_obj

        for channel_obj in Channel.objects.filter(is_easychat_channel=True):
            intent_obj.channels.add(channel_obj)

        intent_obj.save()

    return intent_obj


"""
function: create_bot_response
input params:
    answer: answer

returns bot response using answer
"""


def create_bot_response(answer):

    sentence = {
        "items": [
            {
                "text_response": str(answer),
                "speech_response": str(answer),
                "text_reprompt_response": str(answer),
                "speech_reprompt_response": str(answer),
                "ssml_response": str(answer),
            }
        ]
    }

    cards = {
        "items": [
        ]
    }

    modes = {
        "is_typable": "true",
        "is_button": "true",
        "is_slidable": "false",
        "is_date": "false",
        "is_dropdown": "false"
    }

    modes_param = {
        "is_slidable": [{
            "max": "",
            "min": "",
            "step": "",
            "placeholder": ""
        }]
    }

    bot_response_obj = BotResponse.objects.create(
        sentence=json.dumps(sentence),
        cards=json.dumps(cards),
        modes=json.dumps(modes),
        modes_param=json.dumps(modes_param))

    return bot_response_obj


"""
function: create_tree
input params:
    tree_name: name of tree

returns newly created tree object of given tree name
"""


def create_tree(tree_name):
    return Tree.objects.create(name=tree_name)


"""
function: create_user_flow_with_excel
input params:
    filepath: path of excel
    bot_objs_list: list of bot objects

creates 2-level flow with excel
"""


def create_user_flow_with_excel(filepath, bot_objs_list, user_obj):
    file_excel_user_flow = open('files/create_bot_with_excel_' +
                                user_obj.username + '_' + str(bot_objs_list[0].pk) + "_" + '.txt', 'w')
    current_date_time = datetime.datetime.now()
    current_date_time = current_date_time.strftime('%Y-%m-%d %H:%M %p')
    file_excel_user_flow.write(
        'Last updated on: ' + str(current_date_time) + '<br>')
    file_excel_user_flow.write('Uploaded Userflow Excel.<br>')
    response = {}
    response["status"] = 500
    user_flow_status_msg = "Something Went Wrong"
    created_intent_obj_list = []
    created_tree_obj_list = []
    try:
        ensure_element_tree(xlrd)
        # Open ExcelFile
        automated_flow_create_wb = xlrd.open_workbook(filepath)
        excel_flows = automated_flow_create_wb.sheet_by_index(0)
        rows_limit = excel_flows.nrows
        cols_limit = excel_flows.ncols

        row_index = 1

        last_parent_intent = ""

        flow_data_dict = {}
        user_flow_status_msg = "Please Check Excel file format: Refer userflow excel format for reference"

        while row_index in range(1, rows_limit):

            parent_intent = excel_flows.cell_value(row_index, 1)
            category = excel_flows.cell_value(row_index, 2)

            if category == "":
                category = None

            if parent_intent != "":
                last_parent_intent = parent_intent
                flow_data_dict[parent_intent] = {
                    'category': category,
                    'child_intents': []
                }

            child_intent_level_one = excel_flows.cell_value(row_index, 3)
            child_intent_level_one_answer = excel_flows.cell_value(
                row_index + 1, 3)

            child_intent_level_two_list = []
            column_index = 4
            while True:

                if column_index >= cols_limit:
                    break

                child_intent_level_two = excel_flows.cell_value(
                    row_index, column_index)
                child_intent_level_two_answer = excel_flows.cell_value(
                    row_index + 1, column_index)

                if child_intent_level_two == "":
                    break

                child_intent_level_two_list.append({
                    "question": child_intent_level_two,
                    "answer": child_intent_level_two_answer
                })

                column_index += 1

            flow_data_dict[last_parent_intent]['child_intents'].append({
                "question": child_intent_level_one,
                "answer": child_intent_level_one_answer,
                "child_intents": child_intent_level_two_list
            })

            row_index += 2

        logger.info("JSON from Userflow excel file created successfully.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        logger.info("Creating intent object...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        user_flow_status_msg = "Error while creating flow: Check for Duplicate Intent"
        created_intent_obj_list = []

        created_tree_obj_list = []

        for intent_name in flow_data_dict.keys():
            category = flow_data_dict[intent_name]['category']
            intent_obj = create_intent_for_user_flow(
                intent_name, bot_objs_list, category)
            created_intent_obj_list.append(intent_obj)

            bot_response_obj = create_bot_response(
                "Please select option from one of the following.")

            tree_obj = intent_obj.tree
            created_tree_obj_list.append(tree_obj)

            tree_obj.response = bot_response_obj

            bot_response_obj = BotResponse.objects.create()

            level_one_intent_dict_list = flow_data_dict[
                intent_name]['child_intents']

            for level_one_intent_dict in level_one_intent_dict_list:

                level_one_tree_name = level_one_intent_dict["question"]
                level_one_tree_answer = level_one_intent_dict["answer"]

                level_one_tree_obj = create_tree(level_one_tree_name)
                created_tree_obj_list.append(level_one_tree_obj)

                level_one_bot_response_obj = create_bot_response(
                    level_one_tree_answer)
                level_one_tree_obj.response = level_one_bot_response_obj

                for level_two_intent_dict in level_one_intent_dict["child_intents"]:

                    level_two_tree_name = level_two_intent_dict["question"]
                    level_two_tree_answer = level_two_intent_dict["answer"]

                    level_two_tree_obj = create_tree(level_two_tree_name)
                    created_tree_obj_list.append(level_two_tree_obj)

                    level_two_bot_response_obj = create_bot_response(
                        level_two_tree_answer)
                    level_two_tree_obj.response = level_two_bot_response_obj
                    level_two_tree_obj.save()

                    level_one_tree_obj.children.add(level_two_tree_obj)

                level_one_tree_obj.save()

                tree_obj.children.add(level_one_tree_obj)

            tree_obj.save()

        logger.info("Intent object from json created successfully.", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        user_flow_status_msg = ""
        response["status"] = 200

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_user_flow_with_excel: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        for intent_obj in created_intent_obj_list:
            intent_obj.delete()

        for tree_obj in created_tree_obj_list:
            tree_obj.delete()
    response["status_message"] = user_flow_status_msg
    file_excel_user_flow.write(user_flow_status_msg + '<br>')
    file_excel_user_flow.close()
    return response


"""
function: create_bot_with_excel
input params:
    filepath: path of excel
    bot_objs_list: list of bot objects

creates FAQ bot with excel
"""


def create_bot_with_excel(filepath, bot_objs_list, user_obj, excel_processing_obj):
    file_bot_excel = open('files/create_bot_with_excel_' +
                          user_obj.username + '_' + str(bot_objs_list[0].pk) + '_' + '.txt', 'w')
    current_date_time = datetime.datetime.now()
    current_date_time = current_date_time.strftime('%Y-%M-%d %H:%M %p')
    file_bot_excel.write('Last updated on: ' + str(current_date_time) + '<br>')
    file_bot_excel.write('Uploaded FAQ Bot Excel. <br>')
    response = {}
    response["status"] = 500
    response["message"] = "Internal Server Error"
    is_error = False
    error_message = ""
    created_intent_obj_list = []
    validation_obj = EasyChatInputValidation()

    try:
        ensure_element_tree(xlrd)

        wb = xlrd.open_workbook(filepath)
        faqs = wb.sheet_by_index(0)
        rows_limit = faqs.nrows
        recommedation_intent_dict = {}
        for index in range(1, rows_limit):
            # collect question and answer and process it
            question_list = []
            try:
                query_question = faqs.cell_value(index, 0)
                query_question = query_question.strip()
                query_question = validation_obj.remo_complete_html_and_special_tags(
                    query_question)
                if query_question == "":
                    is_error = True
                    if error_message != "":
                        error_message += "<br>"
                    error_message += "Main Question is empty in row {} and column 1 or invalid main question.".format(
                        index)
                    file_bot_excel.write(error_message + '<br>')
                if len(query_question) > INTENT_TREE_NAME_CHARACTER_LIMIT:
                    is_error = True
                    if error_message != "":
                        error_message += "<br>"
                    error_message += "{} at row {} and column 2.".format(
                        "Main Question Cannot Contain More Than 500 Characters", index)
                    file_bot_excel.write(error_message + '<br>')
                question_list.append(query_question)
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("create_bot_with_excel: load_main_question: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                is_error = True
                if error_message != "":
                    error_message += "<br>"
                error_message += "{} at row {} and column 1.".format(
                    str(e), index)
                file_bot_excel.write(error_message + '<br>')

            try:
                variations_str = faqs.cell_value(index, 1)
                if variations_str == "":
                    variations_list = make_final_variations(query_question)
                else:
                    variations_list = [validation_obj.remo_complete_html_and_special_tags(variation.strip()) for variation in variations_str.split(
                        "$$$") if validation_obj.remo_complete_html_and_special_tags(variation.strip()) != ""]
                question_list.extend(variations_list)
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("create_bot_with_excel: load_variations: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                if error_message != "":
                    error_message += "<br>"
                error_message += "{} at row {} and column 2.".format(
                    str(e), index)
                file_bot_excel.write(error_message + '<br>')
                is_error = True

            answer = ""
            try:
                answer = faqs.cell_value(index, 2)
                answer = validation_obj.custom_remo_html_tags(answer)
                if answer == "":
                    is_error = True
                    error_message += "Answer is not available or invalid answer text in row no " + \
                        str(index) + "::"
                    file_bot_excel.write(error_message + '<br>')
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("create_bot_with_excel: load_answer: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                is_error = True
                if error_message != "":
                    error_message += "<br>"
                error_message += "{} at row {} and column 3.".format(
                    str(e), index)
                file_bot_excel.write(error_message + '<br>')

            recommedation_intent_name_list = []
            try:
                recommedations = faqs.cell_value(index, 3)
                recommedations_list = recommedations.split("$$$")
                recommedation_intent_name_list = [validation_obj.remo_complete_html_and_special_tags(recommedation.strip(
                )) for recommedation in recommedations_list if validation_obj.remo_complete_html_and_special_tags(recommedation.strip()) != ""]
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("create_bot_with_excel: load_recommendations: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            category = ""
            try:
                category = faqs.cell_value(index, 4)
                category = validation_obj.remo_complete_html_and_special_tags(
                    category)
                category = validation_obj.remo_special_characters_from_string(category)
                if len(category) > 25:
                    category = category[:25]
                if category == "":
                    category = "Others"
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("create_bot_with_excel: category: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                category = "Others"

            cards_list = []
            try:
                card_excel = faqs.cell_value(index, 5)
                cards_list = [card.strip() for card in card_excel.split(
                    "@@@") if card.strip() != ""]

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("create_bot_with_excel: load_cards: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            img_list = []
            try:
                img_excel = faqs.cell_value(index, 6)
                if img_excel != "":
                    img_list = [store_this_data_locally(
                        img.strip())for img in img_excel.split("$$$") if img != ""]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("create_bot_with_excel: load_images: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                pass

            videos_list = []

            try:
                videos_excel = faqs.cell_value(index, 7)
                if videos_excel != "":
                    videos_list = [vids.strip()
                                   for vids in videos_excel.split("$$$") if vids != ""]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("create_bot_with_excel: load_videos: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                pass

            channel_objs = []
            try:
                channels = faqs.cell_value(index, 8).strip().lower()
                if channels != "" and channels != "all":
                    channels = [validation_obj.remo_complete_html_and_special_tags(channel.strip().lower()) for channel in channels.split(
                        ",") if validation_obj.remo_complete_html_and_special_tags(channel.strip()) != ""]
                    for channel in channels:
                        channel_objs.append(
                            Channel.objects.get(name__icontains=channel))
                else:
                    channel_objs = Channel.objects.filter(is_easychat_channel=True)
            except:
                channel_objs = Channel.objects.filter(is_easychat_channel=True)

            # Insert into database
            if not is_error:
                if isinstance(query_question, str) == False:
                    query_question = str(query_question)
                intent_name = query_question.encode("ascii", errors="ignore")
                intent_name = intent_name.decode("ASCII")
                keyword_dict = {}
                training_data = {}

                if isinstance(answer, str) == False:
                    answer = str(answer)
                speech_answer = answer.encode("ascii", errors="ignore")
                speech_answer = speech_answer.decode("ASCII")
                text_answer = answer.replace("\n", "<br>")

                card_list = []
                final_card_list = []
                for index in range(0, len(cards_list)):

                    card_temp = cards_list[index]

                    temp_card_list = card_temp.split("$$$")
                    card_list = []
                    for card_item_index in range(0, len(temp_card_list)):
                        card_item = temp_card_list[card_item_index]
                        # for title and content remove special chars completly
                        if card_item_index in [0, 1]:
                            card_item = validation_obj.remo_complete_html_and_special_tags(
                                card_item)
                        # else for image and card link sanitize diffrently
                        else:
                            card_item = validation_obj.remo_html_from_string(
                                card_item)
                            if not validation_obj.is_valid_url(card_item):
                                card_item = ""
                        card_list.append(card_item)

                    title = ""
                    content = ""
                    link = ""
                    img_url = ""

                    if len(card_list) == 4:
                        title = card_list[0]
                        content = card_list[1]
                        link = card_list[2]
                        img_url = card_list[3]

                    elif len(card_list) == 3:
                        title = card_list[0]
                        content = card_list[1]
                        link = card_list[2]

                    temp_dict = {
                        "title": title,
                        "content": content,
                        "link": link,
                        "img_url": store_this_data_locally(img_url)
                    }
                    final_card_list.append(temp_dict)

                sentence = {
                    "items": [
                        {
                            "text_response": text_answer,
                            "speech_response": speech_answer,
                            "text_reprompt_response": text_answer,
                            "speech_reprompt_response": speech_answer
                        }
                    ]
                }

                cards = {
                    "items": final_card_list
                }

                imgs = {
                    "items": img_list
                }

                videos = {
                    "items": videos_list
                }

                modes = {
                    "is_typable": "true",
                    "is_button": "true",
                    "is_slidable": "false",
                    "is_date": "false",
                    "is_dropdown": "false"
                }

                modes_param = {
                    "is_slidable": [{
                        "max": "",
                        "min": "",
                        "step": "",
                        "placeholder": ""
                    }]
                }

                for index, question in enumerate(question_list):
                    training_data[str(index)] = question.encode(
                        "ascii", errors="ignore")
                    training_data[str(index)] = training_data[str(
                        index)].decode("ASCII")

                stem_words = get_stem_words_of_sentence(
                    intent_name, None, None, None, bot_objs_list[0])
                stem_words.sort()
                hashed_name = ' '.join(stem_words)
                hashed_name = hashlib.md5(hashed_name.encode()).hexdigest()
                intent_obj = Intent.objects.create(
                    name=intent_name,
                    intent_hash=hashed_name,
                    keywords=json.dumps(keyword_dict),
                    training_data=json.dumps(training_data),
                    threshold=1.0)

                created_intent_obj_list.append(intent_obj)

                try:
                    for channel_obj in channel_objs:
                        intent_obj.channels.add(channel_obj)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("create_bot_with_excel: channel_obj: %s at line no %s", str(e), str(exc_tb.tb_lineno), extra={
                                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass

                try:
                    for bot_obj in bot_objs_list:
                        category_obj = Category.objects.filter(
                            name=category, bot=bot_obj)
                        if category_obj.count() > 0:
                            intent_obj.bots.add(bot_obj)
                            intent_obj.category = category_obj[0]
                        else:
                            category_obj = Category.objects.create(
                                name=category, bot=bot_obj)
                            intent_obj.bots.add(bot_obj)
                            intent_obj.category = category_obj

                        bot_obj.need_to_build = True
                        bot_obj.save()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("create_bot_with_excel: category: %s at line no %s", str(e), str(exc_tb.tb_lineno), extra={
                                 'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    pass

                duplicate_intent_exist = False
                try:
                    intent_obj.save()
                except DuplicateIntentExceptionError as e:
                    logger.warning("CreateFAQBotAPI: %s", str(e), extra={
                                   'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    duplicate_intent_exist = True

                if duplicate_intent_exist:
                    intent_name = remove_whitespace(intent_name)
                    intent_objs = Intent.objects.filter(
                        bots__in=bot_objs_list, is_deleted=False, is_hidden=False, channels__in=channel_objs).distinct()
                    intent_objs = intent_objs.filter(intent_hash=hashed_name)
                    if intent_objs.count() == 1:
                        intent_obj = intent_objs[0]
                        final_question_list = training_data.values()

                        training_data = {}

                        for index, question in enumerate(final_question_list):
                            training_data[str(index)] = question.encode(
                                "ascii", errors="ignore")
                            training_data[str(index)] = training_data[str(
                                index)].decode("ASCII")

                        intent_obj.training_data = json.dumps(training_data)

                        intent_obj.channels.clear()
                        for channel_obj in channel_objs:
                            intent_obj.channels.add(channel_obj)

                        intent_obj.save()

                        tree_obj = intent_obj.tree
                        bot_response_obj = tree_obj.response
                        bot_response_obj.sentence = json.dumps(sentence)
                        bot_response_obj.save()
                        final_card = cards['items']

                        seen = set()
                        new_list = []
                        for dictionary in final_card:
                            training_tuple = tuple(dictionary.items())
                            for index in seen:
                                if (training_tuple[0] == index[0]):
                                    seen.add(training_tuple)
                                    seen.discard(index)
                                    for item in new_list:
                                        if(item['title'] == dictionary['title']):
                                            new_list.remove(item)
                                            new_list.append(dictionary)
                                            break
                                    break
                            if training_tuple not in seen:
                                seen.add(training_tuple)
                                new_list.append(dictionary)

                        cards['items'] = new_list
                        final_imgs_list = imgs['items']

                        imgs['items'] = final_imgs_list
                        final_videos_list = videos['items']

                        embed_video_url_list = []
                        for video_url in final_videos_list:
                            embed_video_url_list.append(embed_url(video_url))

                        videos['items'] = embed_video_url_list
                        bot_response_obj.sentence = json.dumps(sentence)
                        bot_response_obj.cards = json.dumps(cards)
                        bot_response_obj.images = json.dumps(imgs)
                        bot_response_obj.videos = json.dumps(videos)
                        bot_response_obj.save()

                    else:
                        if intent_objs.exists():
                            current_intent_name = intent_objs[0].name
                        else:
                            current_intent_name = intent_name
                        is_error = True
                        if error_message != "":
                            error_message += "<br>"
                        error_message += "'{}' intent already exists".format(
                            current_intent_name)
                else:
                    tree_obj = intent_obj.tree

                    bot_response_obj = BotResponse.objects.create(
                        sentence=json.dumps(sentence),
                        cards=json.dumps(cards),
                        images=json.dumps(imgs),
                        videos=json.dumps(videos),
                        modes=json.dumps(modes),
                        modes_param=json.dumps(modes_param))

                    tree_obj.response = bot_response_obj
                    tree_obj.save()

                if str(intent_obj.pk) != "None":
                    recommedation_intent_dict[str(
                        intent_obj.pk)] = recommedation_intent_name_list

            else:
                break
        # Add
        for intent_pk in recommedation_intent_dict.keys():
            recommedation_intent_pk_list = []
            for recommedation in recommedation_intent_dict[str(intent_pk)]:
                intent_objs = Intent.objects.filter(
                    bots__in=bot_objs_list, name__iexact=recommedation, is_deleted=False, is_hidden=False)
                if len(intent_objs) > 0:
                    recommedation_intent_pk_list.append(str(intent_objs[0].pk))

            intent_obj = Intent.objects.get(pk=int(intent_pk), is_hidden=False)
            bot_response_obj = intent_obj.tree.response
            bot_response_obj.recommendations = json.dumps({
                "items": recommedation_intent_pk_list
            })
            bot_response_obj.save()

            intent_obj.tree.response = bot_response_obj
            intent_obj.save()
        if not is_error:
            response['status'] = 200
            audit_trail_data = json.dumps({
                "bot_pk": bot_objs_list[0].pk,
                "action": str(rows_limit - 1),
                "filepath": "/files/" + filepath.split("/")[-1],
            })
            AuditTrail.objects.create(
                user=user_obj, action=FAQ_EXCEL_UPLOADED_ACTION, data=audit_trail_data)
            excel_processing_obj.is_processing_completed = True
            excel_processing_obj.status = "200"
            excel_processing_obj.status_message = "Success"
            excel_processing_obj.save()
        else:
            response['status'] = 300
            response['message'] = error_message
            file_bot_excel.write(error_message + '<br>')
            excel_processing_obj.is_processing_completed = True
            excel_processing_obj.status = "500"
            excel_processing_obj.status_message = error_message
            excel_processing_obj.save()
        file_bot_excel.close()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_bot_with_excel: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        for intent_obj in created_intent_obj_list:
            intent_obj.tree.delete()
        file_bot_excel.write(error_message + '<br>')
        file_bot_excel.close()
        excel_processing_obj.is_processing_completed = True
        excel_processing_obj.status = "500"
        excel_processing_obj.status_message = "Internal Server Error: " + \
            str(e)
        excel_processing_obj.save()

    return response


def create_bot_with_questions_variations_answers(questions, variations, answers, bot_obj, user_obj):
    response = {}
    response["status"] = 500
    is_error = False
    error_message = ""
    created_intent_obj_list = []

    if(len(questions) != len(variations) or len(variations) != len(answers)):
        response['message'] = 'Enough questions|variations|answers not provided'
        return response

    try:
        logger.info("Intent creation started", extra={'AppName': 'EasyChatApp', 'user_id': str(
            user_obj.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

        validation_obj = EasyChatInputValidation()

        recommedation_intent_dict = {}

        rows_limit = len(questions)
        for index in range(0, rows_limit):

            question_list = []
            try:
                query_question = questions[index]
                query_question = query_question.strip()
                query_question = validation_obj.remo_special_tag_from_string(
                    query_question)
                if query_question == "":
                    is_error = True
                    error_message += "Main Question is empty in row no " + \
                        str(index) + "::"
                if len(query_question) > INTENT_TREE_NAME_CHARACTER_LIMIT:
                    is_error = True
                    error_message += "Main Question Cannot Contain More Than 500 Characters at row no " + \
                        str(index) + "::"
                    
                question_list.append(query_question)
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("create_bot_with_excel: load_main_question: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                is_error = True
                error_message += ". Questions list column is not present (column 1)::"

            try:
                variations_str = variations[index]
                variations_list = [variation.strip() for variation in variations_str.split(
                    "$$$") if variation != ""]
                question_list.extend(variations_list)
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("create_bot_with_excel: load_variations: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                error_message += ". Variations list column is not present (column 2)::"
                is_error = True

            answer = ""
            try:
                answer = answers[index]
                if answer == "":
                    is_error = True
                    error_message += "Answer is not available in row no " + \
                        str(index) + "::"
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("create_bot_with_excel: load_answer: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                is_error = True
                error_message += ". Answer column is not present(column 3)::"

            recommedation_intent_name_list = []
            try:
                recommedations = ""
                recommedations_list = recommedations.split("$$$")
                recommedation_intent_name_list = [recommedation.strip(
                ) for recommedation in recommedations_list if recommedation != ""]
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("create_bot_with_excel: load_recommendations: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            category = ""
            try:
                category = ""
                if category == "":
                    category = "Others"
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("create_bot_with_excel: category: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                category = "Others"

            cards_list = []
            try:
                card_excel = ""
                cards_list = [card.strip()
                              for card in card_excel.split("@@@") if card != ""]

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("create_bot_with_excel: load_cards: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            img_list = []
            try:
                img_excel = ""
                img_list = [store_this_data_locally(img.strip())
                            for img in img_excel.split("$$$") if img != ""]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.warning("create_bot_with_excel: load_images: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            videos_list = []

            try:
                videos_excel = ""
                videos_list = [vids.strip()
                               for vids in videos_excel.split("$$$") if vids != ""]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("create_bot_with_excel: load_videos: %s at line no %s", str(
                    e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            # Insert into database
            if not is_error:
                intent_name = query_question.encode("ascii", errors="ignore")
                intent_name = intent_name.decode("ASCII")
                keyword_dict = {}
                training_data = {}

                # speech_answer = answer.encode("ascii", errors="ignore")
                # speech_answer = speech_answer.decode("ASCII")
                speech_answer = answer
                text_answer = speech_answer.replace("\n", "<br>")

                card_list = []
                final_card_list = []
                for index in range(0, len(cards_list)):

                    card_temp = cards_list[index]
                    card_list = [card.strip()
                                 for card in card_temp.split("$$$") if card != ""]

                    title = ""
                    content = ""
                    link = ""
                    img_url = ""

                    if len(card_list) == 4:
                        title = card_list[0]
                        content = card_list[1]
                        link = card_list[2]
                        img_url = card_list[3]

                    elif len(card_list) == 3:
                        title = card_list[0]
                        content = card_list[1]
                        link = card_list[2]

                    temp_dict = {
                        "title": title,
                        "content": content,
                        "link": store_this_data_locally(link),
                        "img_url": store_this_data_locally(img_url)
                    }
                    final_card_list.append(temp_dict)

                sentence = {
                    "items": [
                        {
                            "text_response": text_answer,
                            "speech_response": speech_answer,
                            "text_reprompt_response": text_answer,
                            "speech_reprompt_response": speech_answer
                        }
                    ]
                }

                cards = {
                    "items": final_card_list
                }

                imgs = {
                    "items": img_list
                }

                videos = {
                    "items": videos_list
                }

                modes = {
                    "is_typable": "true",
                    "is_button": "true",
                    "is_slidable": "false",
                    "is_date": "false",
                    "is_dropdown": "false"
                }

                modes_param = {
                    "is_slidable": [{
                        "max": "",
                        "min": "",
                        "step": "",
                        "placeholder": ""
                    }]
                }

                for index, question in enumerate(question_list):
                    training_data[str(index)] = question.encode(
                        "ascii", errors="ignore")
                    training_data[str(index)] = training_data[str(
                        index)].decode("ASCII")

                stem_words = get_stem_words_of_sentence(
                    intent_name, None, None, None, bot_obj)
                stem_words.sort()
                hashed_name = ' '.join(stem_words)
                hashed_name = hashlib.md5(hashed_name.encode()).hexdigest()
                intent_obj = Intent.objects.create(
                    name=intent_name,
                    intent_hash=hashed_name,
                    keywords=json.dumps(keyword_dict),
                    training_data=json.dumps(training_data),
                    threshold=1.0)

                created_intent_obj_list.append(intent_obj)

                for channel_obj in Channel.objects.filter(is_easychat_channel=True):
                    intent_obj.channels.add(channel_obj)

                category_obj = Category.objects.filter(
                    name=category, bot=bot_obj)
                if category_obj.count() > 0:
                    intent_obj.bots.add(bot_obj)
                    intent_obj.category = category_obj[0]
                else:
                    category_obj = Category.objects.create(
                        name=category, bot=bot_obj)
                    intent_obj.bots.add(bot_obj)
                    intent_obj.category = category_obj

                duplicate_intent_exist = False
                try:
                    intent_obj.synced = False
                    intent_obj.trained = False
                    bot_obj.need_to_build = True
                    bot_obj.save()
                    intent_obj.save()
                except DuplicateIntentExceptionError as e:
                    logger.warning("CreateFAQBotAPI: %s", str(e), extra={
                                   'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                    duplicate_intent_exist = True

                if duplicate_intent_exist:
                    intent_name = remove_whitespace(intent_name)
                    intent_objs = Intent.objects.filter(
                        bots=bot_obj, is_hidden=False, is_deleted="False").distinct()
                    intent_objs = intent_objs.filter(intent_hash=hashed_name)
                    if len(intent_objs) > 0:
                        intent_obj = intent_objs[0]

                        training_data_temp = json.loads(
                            intent_obj.training_data)
                        training_data_temp_list = list(
                            training_data_temp.values())
                        training_data_list = list(training_data.values())

                        final_question_list = set(
                            training_data_temp_list + training_data_list)

                        training_data = {}

                        for index, question in enumerate(final_question_list):
                            training_data[str(index)] = question.encode(
                                "ascii", errors="ignore")
                            training_data[str(index)] = training_data[str(
                                index)].decode("ASCII")

                        intent_obj.training_data = json.dumps(training_data)

                        tree_obj = intent_obj.tree
                        bot_response_obj = tree_obj.response

                        # sentence_temp = json.loads(bot_response_obj.sentence)
                        # sentence.update(sentence_temp)

                        bot_response_obj.sentence = json.dumps(sentence)

                        bot_response_obj.save()
                        intent_obj.save()
                else:
                    tree_obj = intent_obj.tree

                    bot_response_obj = BotResponse.objects.create(
                        sentence=json.dumps(sentence),
                        cards=json.dumps(cards),
                        images=json.dumps(imgs),
                        videos=json.dumps(videos),
                        modes=json.dumps(modes),
                        modes_param=json.dumps(modes_param))

                    tree_obj.response = bot_response_obj
                    tree_obj.save()

                recommedation_intent_dict[
                    str(intent_obj.pk)] = recommedation_intent_name_list

        # Add
        intent_pk_list = []
        for intent_pk in recommedation_intent_dict.keys():

            recommedation_intent_pk_list = []
            intent_pk_list.append(intent_pk)

            for recommedation in recommedation_intent_dict[str(intent_pk)]:
                intent_objs = Intent.objects.filter(
                    bots=bot_obj, name__iexact=recommedation, is_deleted=False, is_hidden=False)
                if len(intent_objs) > 0:
                    recommedation_intent_pk_list.append(str(intent_objs[0].pk))

            intent_obj = Intent.objects.get(pk=int(intent_pk), is_hidden=False)
            bot_response_obj = intent_obj.tree.response
            bot_response_obj.recommendations = json.dumps({
                "items": recommedation_intent_pk_list
            })
            bot_response_obj.save()

        if not is_error:
            response['status'] = 200
            response['message'] = 'Intent added successfully'

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
                "bot_pk": str(bot_obj.pk),
            })

            try:
                AuditTrail.objects.create(
                    user=user_obj, action=CREATE_INTENT_FROM_FAQ_ACTION, data=audit_trail_data)
            except Exception as e:  # noqa: F841
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("save_audit_trail %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            logger.info("Intent added", extra={'AppName': 'EasyChatApp', 'user_id': str(
                user_obj.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})
        else:
            response['status'] = 300
            response['message'] = error_message
            logger.warning("Intent not added error %s", error_message, extra={'AppName': 'EasyChatApp', 'user_id': str(
                user_obj.username), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_bot_with_questions_variations_answers: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response['status'] = 500
        response['message'] = "Not able to add intent some error occured"
        for intent_obj in created_intent_obj_list:
            intent_obj.tree.delete()
    return response


def create_sentence_response(text_answer, speech_answer):
    return {
        "items": [
            {
                "text_response": text_answer,
                "speech_response": speech_answer,
                "text_reprompt_response": text_answer,
                "speech_reprompt_response": speech_answer
            }
        ]
    }


def create_cards_response(cards_list):
    return {
        "items": cards_list
    }


def create_images_response(img_list):
    return {
        "items": img_list
    }


def create_videos_response(videos_list):
    return {
        "items": videos_list
    }


def create_modes_response():
    return {
        "is_typable": "true",
        "is_button": "true",
        "is_slidable": "false",
        "is_date": "false",
        "is_dropdown": "false"
    }


def create_modes_param_response():
    return {
        "is_slidable": [{
            "max": "",
            "min": "",
            "step": "",
            "placeholder": ""
        }]
    }


def create_flow_using_excel(filepath, bot_objs_list, user_obj, excel_processing_obj):
    response = {}
    response["status"] = 500
    is_error = False
    is_error_in_trees = False
    is_error_in_relations = False
    error_message = ""

    try:
        ensure_element_tree(xlrd)

        wb = xlrd.open_workbook(filepath)
        trees = wb.sheet_by_index(0)
        rows_limit = trees.nrows
        question_list = []

        error_message = ""

        # First create the intent..
        intent_name = ""
        validation_obj = EasyChatInputValidation()
        try:
            intent_name = trees.cell_value(1, 1).strip()
            intent_name = validation_obj.remo_complete_html_and_special_tags(
                intent_name)
            if intent_name == "":
                is_error = True
                if error_message != "":
                    error_message += "<br>"
                error_message += "Intent name empty in Intent/Trees sheet at row 2 and column 2  or invalid intent name"

            if len(intent_name) > INTENT_TREE_NAME_CHARACTER_LIMIT:
                is_error = True
                if error_message != "":
                    error_message += "<br>"
                error_message += "Intent Name Cannot Contain More Than 500 Characters at row 2 and column 2"
            question_list.append(intent_name)

        except Exception as e:
            is_error = True
            if error_message != "":
                error_message += "<br>"
            error_message += "{} in Intent/Trees sheet at row 2 and column 2.".format(
                str(e))
            pass

        variations_str = ""
        try:
            variations_str = trees.cell_value(1, 3).strip()
            if variations_str == "":
                variations_list = make_final_variations(intent_name)
            else:
                variations_list = [validation_obj.remo_complete_html_and_special_tags(variation.strip()) for variation in variations_str.split(
                    "$$$") if validation_obj.remo_complete_html_and_special_tags(variation.strip()) != ""]
            question_list.extend(variations_list)
        except Exception as e:
            is_error = True
            if error_message != "":
                error_message += "<br>"
            error_message += "{} in Intent/Trees sheet at row 2 and column 4.".format(
                str(e))
            pass

        answer = ""
        try:
            answer = trees.cell_value(1, 2).strip()
            answer = validation_obj.custom_remo_html_tags(answer)
            if answer == "":
                is_error = True
                if error_message != "":
                    error_message += "<br>"
                error_message += "Intent answer empty in Intent/Trees sheet at row 2 and column 3 or invalid intent answer"
        except Exception as e:
            is_error = True
            if error_message != "":
                error_message += "<br>"
            error_message += "{} in Intent/Trees sheet at row 2 and column 3.".format(
                str(e))

        category = "Others"

        if not is_error:
            keyword_dict = {}
            training_data = {}
            final_card_list = []
            img_list = []
            videos_list = []

            if isinstance(answer, str) == False:
                answer = str(answer)
            speech_answer = answer.encode("ascii", errors="ignore")
            speech_answer = speech_answer.decode("ASCII")
            text_answer = speech_answer.replace("\n", "<br>")

            sentence = create_sentence_response(text_answer, speech_answer)

            cards = create_cards_response(final_card_list)

            imgs = create_images_response(img_list)

            videos = create_videos_response(videos_list)

            modes = create_modes_response()

            modes_param = create_modes_param_response()

            for index, question in enumerate(question_list):
                training_data[str(index)] = question.encode(
                    "ascii", errors="ignore")
                training_data[str(index)] = training_data[str(
                    index)].decode("ASCII")

            stem_words = get_stem_words_of_sentence(
                intent_name, None, None, None, bot_objs_list[0])
            
            stem_words.sort()
            hashed_name = ' '.join(stem_words)
            hashed_name = hashlib.md5(hashed_name.encode()).hexdigest()

            intent_obj = Intent.objects.create(
                name=intent_name,
                intent_hash=hashed_name,
                keywords=json.dumps(keyword_dict),
                training_data=json.dumps(training_data),
                threshold=1.0)

            for channel_obj in Channel.objects.filter(is_easychat_channel=True):
                intent_obj.channels.add(channel_obj)

            for bot_obj in bot_objs_list:
                category_obj = Category.objects.filter(
                    name=category, bot=bot_obj)
                if category_obj:
                    intent_obj.bots.add(bot_obj)
                    intent_obj.category = category_obj[0]
                else:
                    category_obj = Category.objects.create(
                        name=category, bot=bot_obj)
                    intent_obj.bots.add(bot_obj)
                    intent_obj.category = category_obj

                bot_obj.need_to_build = True
                bot_obj.save()

            for bot_obj in bot_objs_list:
                intent_obj.bots.add(bot_obj)

            duplicate_intent_exist = False
            try:
                intent_obj.save()
            except:
                intent_tree = intent_obj.tree
                intent_tree.delete()
                duplicate_intent_exist = True

            if not duplicate_intent_exist:
                tree_obj = intent_obj.tree

                bot_response_obj = BotResponse.objects.create(
                    sentence=json.dumps(sentence),
                    cards=json.dumps(cards),
                    images=json.dumps(imgs),
                    videos=json.dumps(videos),
                    modes=json.dumps(modes),
                    modes_param=json.dumps(modes_param))

                tree_obj.response = bot_response_obj
                tree_obj.save()

            else:
                raise Exception("Already intent exists.")

            # Create all trees..
            creating_trees_error_message = ""
            created_flow_trees = [intent_obj.tree]
            for index in range(2, rows_limit):
                tree_name = ""
                try:
                    tree_name = trees.cell_value(index, 1).strip()
                    tree_name = validation_obj.remo_complete_html_and_special_tags(
                        tree_name)
                    if tree_name == "":
                        is_error_in_trees = True
                        if creating_trees_error_message != "":
                            creating_trees_error_message += "<br>"
                        creating_trees_error_message += "Tree name empty in Intent/Trees sheet at row {} and column 2  or invalid tree name".format(
                            index + 1)
                    if len(tree_name) > INTENT_TREE_NAME_CHARACTER_LIMIT:
                        is_error_in_trees = True
                        if creating_trees_error_message != "":
                            creating_trees_error_message += "<br>"
                        creating_trees_error_message += "Tree Name Cannot Contain More Than 500 Characters at row {} and column 2".format(
                            index + 1)
                except Exception as e:
                    is_error_in_trees = True
                    if creating_trees_error_message != "":
                        creating_trees_error_message += "<br>"
                    creating_trees_error_message += "{} at Intent/Trees sheet at row {} and column 2.".format(
                        str(e), index + 1)

                tree_response = ""
                try:
                    tree_response = trees.cell_value(index, 2).strip()
                    tree_response = validation_obj.custom_remo_html_tags(
                        tree_response)
                    if tree_response == "":
                        is_error_in_trees = True
                        if creating_trees_error_message != "":
                            creating_trees_error_message += "<br>"
                        creating_trees_error_message += "Tree response empty in Intent/Trees sheet at row {} and column 3  or tree response".format(
                            index + 1)
                except Exception as e:
                    is_error_in_trees = True
                    if creating_trees_error_message != "":
                        creating_trees_error_message += "<br>"
                    creating_trees_error_message += "{} at Intent/Trees sheet at row {} and column 3.".format(
                        str(e), index + 1)

                if not is_error_in_trees:
                    tree_obj = Tree.objects.create(name=tree_name)
                    keyword_dict = {}
                    training_data = {}
                    final_card_list = []
                    img_list = []
                    videos_list = []

                    if isinstance(tree_response, str) == False:
                        tree_response = str(tree_response)
                    speech_answer = tree_response.encode(
                        "ascii", errors="ignore")
                    speech_answer = speech_answer.decode("ASCII")
                    text_answer = speech_answer.replace("\n", "<br>")

                    sentence = create_sentence_response(
                        text_answer, speech_answer)

                    cards = create_cards_response(final_card_list)

                    imgs = create_images_response(img_list)

                    videos = create_videos_response(videos_list)

                    modes = create_modes_response()

                    modes_param = create_modes_param_response()

                    bot_response_obj = BotResponse.objects.create(
                        sentence=json.dumps(sentence),
                        cards=json.dumps(cards),
                        images=json.dumps(imgs),
                        videos=json.dumps(videos),
                        modes=json.dumps(modes),
                        modes_param=json.dumps(modes_param))

                    tree_obj.response = bot_response_obj
                    tree_obj.save()

                    created_flow_trees.append(tree_obj)

                else:
                    for created_tree_index in range(len(created_flow_trees)):
                        created_tree = created_flow_trees[created_tree_index]
                        created_flow_trees[created_tree_index] = created_tree.pk
                        created_tree.delete()

                    intent_obj.delete()
                    raise Exception(creating_trees_error_message)

            # Create flow..
            creating_relations_error_message = ""
            relations = wb.sheet_by_index(1)
            nrelations = relations.nrows
            for relation_index in range(1, nrelations):
                try:
                    parent_tree = int(relations.cell_value(relation_index, 0))
                except Exception as e:
                    is_error_in_relations = True
                    if creating_relations_error_message != "":
                        creating_relations_error_message += "<br>"
                    creating_relations_error_message += "{} in Flow Relations sheet at row {} and column 1.".format(
                        str(e), relation_index + 1)

                try:
                    children_trees = str(relations.cell_value(
                        relation_index, 1)).strip().split(",")
                    children_trees = [int(float(children.strip()))
                                      for children in children_trees]
                except Exception as e:
                    is_error_in_relations = True
                    if creating_relations_error_message != "":
                        creating_relations_error_message += "<br>"
                    creating_relations_error_message += "{} in Flow Relations sheet at row {} and column 2.".format(
                        str(e), relation_index + 1)

                if not is_error_in_relations:
                    parent_tree_obj = created_flow_trees[parent_tree - 1]
                    for children in children_trees:
                        parent_tree_obj.children.add(
                            created_flow_trees[children - 1])
                    parent_tree_obj.save()
                    excel_processing_obj.status = "200"
                    excel_processing_obj.status_message = "Success"
                    excel_processing_obj.is_processing_completed = True
                    excel_processing_obj.save()
                else:
                    for created_tree_index in range(len(created_flow_trees)):
                        created_tree = created_flow_trees[created_tree_index]
                        created_flow_trees[created_tree_index] = created_tree.pk
                        created_tree.delete()

                    intent_obj.delete()
                    raise Exception(creating_relations_error_message)

            # Make last tree boolean 
            if not is_error_in_relations:
                for tree_obj in created_flow_trees[1:]:
                    if not tree_obj.children.all():
                        tree_obj.is_last_tree = True
                        tree_obj.save()

        else:
            raise Exception(error_message)

    except Exception as e:
        excel_processing_obj.status = "500"
        excel_processing_obj.status_message = str(e)
        excel_processing_obj.is_processing_completed = True
        excel_processing_obj.save()


def ensure_element_tree(xlrd):
    try:
        xlrd.xlsx.ensure_elementtree_imported(False, None)
        xlrd.xlsx.Element_has_iter = True
    except Exception:
        pass
