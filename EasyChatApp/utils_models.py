from django.utils import timezone
from EasyChatApp.utils_analytics import word_stemmer
from datetime import timedelta
import re
import sys
import json
import logging
from EasyChatApp.intent_icons_constants import INTENT_ICONS
import spacy

logger = logging.getLogger(__name__)

nlp = spacy.load('en_core_web_sm')


def get_fifteen_days_from_now():
    return timezone.now() + timezone.timedelta(days=15)


def get_default_intent_icon():
    from EasyChatApp.models import BuiltInIntentIcon

    default_intent_icon = BuiltInIntentIcon.objects.filter(
        unique_id=INTENT_ICONS[0][0]).first()

    if not default_intent_icon:
        default_intent_icon = BuiltInIntentIcon.objects.create(
            unique_id=INTENT_ICONS[0][0], icon=INTENT_ICONS[0][1])
        default_intent_icon.save()

    return default_intent_icon.pk


def get_user_query_pos_list(user_query, stopwords):
    user_query_list_with_pos = []
    try:
        user_query = re.sub('[^A-Za-z0-9]+', ' ', user_query)
        user_query = user_query.strip().lower()

        user_query_nlp = nlp(user_query)
        for token in user_query_nlp:
            if token.text.lower() not in stopwords:
                user_query_list_with_pos.append(word_stemmer(token.text) + "@@@" + token.pos_)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_user_query_pos_list %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return user_query_list_with_pos


def get_training_dict_with_pos(training_dict, stopwords):
    pos_training_dict = {}
    try:
        for key_index in training_dict:
            training_que = training_dict[key_index]
            training_que = re.sub('[^A-Za-z0-9]+', ' ', training_que)
            training_que = training_que.strip().lower()
            training_que_nlp_result = nlp(training_que)
            training_ques_with_pos = []
            for token in training_que_nlp_result:
                if token.text.lower() not in stopwords:
                    training_ques_with_pos.append(
                        word_stemmer(token.text) + "@@@" + token.pos_)

            training_ques_with_pos = ",".join(training_ques_with_pos)

            pos_training_dict[key_index] = training_ques_with_pos

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_training_dict_with_pos %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return pos_training_dict


def procces_string_for_tree_name(sentence, Config):
    try:
        configobject = Config.objects.all()[0]
        autocorrect_replace_space = configobject.autocorrect_replace_space
        autocorrect_do_nothing = configobject.autcorrect_do_nothing
        if autocorrect_replace_space != "":
            replace_space = "[" + autocorrect_replace_space + "]"
            sentence = re.sub(replace_space, ' ', sentence)

        do_nothing = "[^a-zA-Z0-9 " + autocorrect_do_nothing + "]+"
        sentence = re.sub(do_nothing, ' ', sentence)
        sentence = sentence.strip()
        sentence = re.sub('(\s+)(a|an|the)(\s+)', ' ', sentence)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("procces_string_for_tree_name %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return sentence


def get_data_for_suggestion_list_from_accept_keywords_and_tree_name(tree, Config):
    child_tree_accept_keywords = []

    try:
        child_tree_accept_keywords = [str(keyword).strip().lower(
        ) for keyword in tree.accept_keywords.split(",") if keyword != ""]

        tree_name = str(tree.name).strip().lower()
        tree_name = procces_string_for_tree_name(tree_name, Config)

        child_tree_accept_keywords.append(tree_name)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_data_for_suggestion_list_from_accept_keywords_and_tree_name %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return child_tree_accept_keywords


def sync_tree_object_training_data(tree_obj, TrainingData, Config):

    try:
        suggestions_list = []
        child_tree_list = tree_obj.children.filter(is_deleted=False)

        for child_tree in child_tree_list:

            child_tree_accept_keywords = get_data_for_suggestion_list_from_accept_keywords_and_tree_name(
                child_tree, Config)

            suggestions_list += child_tree_accept_keywords

        child_tree_accept_keywords = get_data_for_suggestion_list_from_accept_keywords_and_tree_name(
            tree_obj, Config)

        suggestions_list += child_tree_accept_keywords
        training_data_obj = TrainingData.objects.filter(
            tree=tree_obj, data_type="2").first()

        if training_data_obj:
            training_data_obj.training_data = json.dumps(
                {"0": suggestions_list})
            training_data_obj.save()
        else:
            TrainingData.objects.create(
                tree=tree_obj, data_type="2", training_data=json.dumps({"0": suggestions_list}))

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("sync_tree_object_training_data: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})
