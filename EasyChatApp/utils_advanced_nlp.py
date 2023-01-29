from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from collections import Counter
import re
import torch
from math import log
from sentence_transformers import SentenceTransformer
import numpy as np
from EasyChat.settings import BASE_DIR
from EasyChatApp.models import *
import logging
import threading

logger = logging.getLogger(__name__)
# Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability).
custom_words_corpus_list = open(BASE_DIR + "/custom_words_corpus.txt").read()
words = custom_words_corpus_list.split()
wordcost = dict((var_k, log((idx + 1) * log(len(words))))
                for idx, var_k in enumerate(words))
maxword = max(len(x) for x in words)

embedder = None
lemmatizer = None
text_embeddings = []


def initialize_embedder_and_lemmatizer():
    try:
        global embedder, lemmatizer

        # embedder = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        lemmatizer = WordNetLemmatizer()
        lemmatizer.lemmatize("stop")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("initialize_embedder_and_lemmatizer! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def load_repeat_variations_training_data():
    text_list_new = []
    try:
        global text_embeddings
        
        config_obj = Config.objects.all().first()
        text_list_new = json.loads(config_obj.repeat_event_variations)["items"]
        text_embeddings = embedder.encode(text_list_new)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("load_repeat_variations_training_data! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def words(text):
    return re.findall(r'\w+', text.lower())


WORDS = Counter(words(custom_words_corpus_list))

"""
load_data -> This functions loads the training data for the particular intent identifcation or tree recognztion
"""


def load_data(bot_obj, current_tree):
    text_embeddings = None
    text_list_new = []
    try:

        if current_tree != None:
            training_obj = TrainingData.objects.filter(
                data_type="2", tree=current_tree).first()
        else:
            training_obj = TrainingData.objects.filter(
                bot=bot_obj, data_type="1").first()

        if training_obj:
            text_list_new = json.loads(training_obj.training_data)["0"]
            torch.set_num_threads(1)
            text_embeddings = embedder.encode(text_list_new)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("load_data! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return text_embeddings, text_list_new


def convert_to_lower(text):
    return text.lower()


# convert the word into grouping together the different inflected forms of a word so they can be analyzed as a single item
# eg rocks --> rock, better-->good
def lemmatizing(text):
    tokens = word_tokenize(text)
    for token in range(len(tokens)):
        lemma_word = lemmatizer.lemmatize(tokens[token])
        tokens[token] = lemma_word
    return " ".join(tokens)


# remove extra white spaces like [ \t\r\n\f]
def remove_extra_white_spaces(text):
    single_char_pattern = r'\s+[a-zA-Z]\s+'
    without_sc = re.sub(pattern=single_char_pattern, repl=" ", string=text)
    return without_sc


# remove the special chracters
def remove_special_characters(text):
    special_character_pattern = r'[^A-Za-z0-9]+'
    without_special_character = re.sub(
        pattern=special_character_pattern, repl=" ", string=text)
    return without_special_character


def infer_spaces(word):
    """Uses dynamic programming to infer the location of spaces in a string
    without spaces."""

    # Find the best match for the idx first characters, assuming cost has
    # been built for the idx-1 first characters.
    # Returns a pair (match_cost, match_length).
    def best_match(idx):
        candidates = enumerate(reversed(cost[max(0, idx - maxword):idx]))
        return min((var_c + wordcost.get(word[idx - var_k - 1:idx], 9e999), var_k + 1) for var_k, var_c in candidates)

    # Build the cost array.
    cost = [0]
    for idx in range(1, len(word) + 1):
        var_c, var_k = best_match(idx)
        cost.append(var_c)

    # Backtrack to recover the minimal-cost string.
    out = []
    str_len = len(word)
    while str_len > 0:
        var_c, var_k = best_match(str_len)
        assert var_c == cost[str_len]
        out.append(word[str_len - var_k:str_len])
        str_len -= var_k

    return " ".join(reversed(out))


def P(word, total_word_count=sum(WORDS.values())):
    "Probability of `word`."
    return WORDS[word] / total_word_count


def correction(word):
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)


def candidates(word):
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])


def known(words):
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)


def edits1(word):
    "All edits that are one edit away from `word`."
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:idx], word[idx:]) for idx in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + var_c + R[1:] for L, R in splits if R for var_c in letters]
    inserts = [L + var_c + R for L, R in splits for var_c in letters]
    return set(deletes + transposes + replaces + inserts)


def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def get_text_after_spell_correction(text):
    new_correct_spell_text = text
    correct_text = ""
    try:
        word_list = text.split()

        for word in word_list:
            correct_text += correction(word) + " "

        correct_text = str.strip(correct_text)

        correct_split_text = correct_text.split()

        new_correct_spell_text = ""

        for word in correct_split_text:
            new_correct_spell_text += str(infer_spaces(word)) + " "

        new_correct_spell_text = str.strip(new_correct_spell_text)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_text_after_spell_correction! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return new_correct_spell_text


def pre_process_text(text):
    try:

        text = convert_to_lower(text)

        text = remove_special_characters(text)

        text = get_text_after_spell_correction(text)

        text = remove_extra_white_spaces(text)

        text = lemmatizing(text)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("pre_process_text! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return text


def identify_next_tree_semantic_similarities(text, current_tree, bot_info_obj):
    message = text
    try:
        logger.info("Inside identify_next_tree_semantic_similarities...", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        text = pre_process_text(text)
        logger.info("text after pre proccesing ." + str(text), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        
        torch.set_num_threads(1)
        text_embedding = embedder.encode(text)

        text_embedding_reshape = text_embedding.reshape(1, -1)

        text_embeddings, text_list_new = load_data(None, current_tree)

        cos_similarity = cosine_similarity(
            text_embedding_reshape,
            text_embeddings
        )

        max_similarity_value_index = np.argmax(cos_similarity)

        original_text = text_list_new.__getitem__(max_similarity_value_index)
        logger.info("[NLP] original text" + str(original_text), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        max_similar_value = max(map(max, cos_similarity))
        logger.info("[NLP] max similar value" + str(max_similar_value), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        if max_similar_value >= bot_info_obj.child_trees_similarity_threshold:
            return original_text

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[NLP]: Error identify_next_tree_semantic_similarities %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return message


def check_if_repeat_event_detected(message, bot_info_obj):
    try:
        text = message
        correct_text = ""
        new_correct_spell_text = ""
        text = convert_to_lower(text)
        text = remove_special_characters(text)
        split_text = text.split()
        for txt in split_text:
            correct_text += correction(txt) + " "
        correct_text = str.strip(correct_text)
        correct_split_text = correct_text.split()
        for txt in correct_split_text:
            new_correct_spell_text += str(infer_spaces(txt)) + " "
        new_correct_spell_text = str.strip(new_correct_spell_text)

        text = new_correct_spell_text
        text = remove_extra_white_spaces(text)

        # do the lemmatizing
        text = lemmatizing(text)
        torch.set_num_threads(1)
        text_embedding = embedder.encode(text)

        text_embedding_reshape = text_embedding.reshape(1, -1)

        cos_similarity = cosine_similarity(
            text_embedding_reshape,
            text_embeddings
        )

        max_similar_value = max(map(max, cos_similarity))

        logger.info("max similarity value %s", str(max_similar_value), extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
        if max_similar_value >= bot_info_obj.repeat_variation_similarity_threshold:
            return True

        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[NLP]: Error check_if_repeat_event_detected %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return False
