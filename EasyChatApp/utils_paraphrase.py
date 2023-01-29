import spacy
from pyinflect import getAllInflections
import nltk
from nltk.corpus import wordnet
from functools import partial
from itertools import combinations, product
import re

nlp = spacy.load('en_core_web_sm')  # download the model using python -m spacy

# download en_core_web_sm

ALL_TEMPLATES = {
    "what_is": {
        "all": [
            "I do not understand what is",
            "What do you mean by",
            "what you meant by",
            "Explain what is",
            "what is",
            "tell me about",
            "I want to know about",
            "Give me information about",
            "Give me information on",
            "Can you explain",
            "I am confused about",
            "Explain",
            "Details about",
            "Details on",
            "Information about",
            "Information on",
            "Help me understand",
            "I do not know about",
            "what are the things i need to know about"
        ]
    },
    "how_do": {
        "all": ["how will i",
                "how will one",
                "how can i",
                "how can one",
                "how do i",
                "how to"]
    },
    "can_i": {
        "all": [
            "would PRON be able to",
            "would PRON have the option to",
            "would PRON have the choice to",
            "i do not know whether PRON can",
            "i confused about whether PRON can",
            "explain whether PRON can",
            "help me whether PRON can",
            "i want to know whether PRON can",
            "tell me whether PRON can",
            "details on whether PRON can",
            "can PRON",
        ]
    },
    "who": {
        "all": [
        ]
    },
    "is_there_any": {
        "all": [
            "is there",
            "i do not know whether there is",
            "i confused about whether there is",
            "explain whether there is",
            "help me whether there is",
            "i want to know whether there is",
            "tell me whether there is",
            "details on whether there is",
        ]
    },
    "is_it": {
        "all": [
            "is PRON",
            "i do not know whether PRON is",
            "i confused about whether PRON is",
            "explain whether PRON is",
            "help me whether PRON is",
            "i want to know whether it is",
            "tell me whether it is",
            "details on whether it is",
        ]
    }
}

"""
function: decontracted
input params:
    phrase : string
decontract the given sentence
"""


def decontracted(phrase):
    phrase = phrase.replace("able to", "can")
    phrase = phrase.replace("unable to", "can not")
    # specific
    phrase = re.sub(r"won\'t", "will not", phrase)
    phrase = re.sub(r"can\'t", "can not", phrase)

    # general
    phrase = re.sub(r"n\'t", " not", phrase)
    phrase = re.sub(r"\'re", " are", phrase)
    phrase = re.sub(r"\'d", " would", phrase)
    phrase = re.sub(r"\'ll", " will", phrase)
    phrase = re.sub(r"\'t", " not", phrase)
    phrase = re.sub(r"\'ve", " have", phrase)
    phrase = re.sub(r"\'m", " am", phrase)

    return phrase

"""
function: nounify
input params:
    verb_word : verb
returns noun form of verb
"""


def nounify(verb_word):
    verb_synsets = wordnet.synsets(verb_word, pos="v")

    # Word not found
    if not verb_synsets:
        return []
    # print(verb_synsets)
    verb_lemmas = []
    for synsets_items in verb_synsets:
        for lemma_iterator in synsets_items.lemmas():
            if synsets_items.name().split('.')[1] == 'v':
                verb_lemmas.append(lemma_iterator)

    derivationally_related_forms = [(lemma, lemma.derivationally_related_forms())
                                    for lemma in verb_lemmas]

    related_noun_lemmas = [lemma for drf in derivationally_related_forms
                           for lemma in drf[1] if lemma.synset().name().split('.')[1] == 'n']

    # Extract the words from the lemmas
    words = [lemma.name() for lemma in related_noun_lemmas]
    len_words = len(words)
    # Build the result in the form of a list containing tuples (word,
    # probability)
    result = [(word, float(words.count(word)) / len_words) for word in set(words)]
    result.sort(key=lambda word: -word[1])
    # return all the possibilities sorted by probability
    if len(result) > 0:
        if result[0][1] > 0.15:
            return [result[0][0]]
        else:
            return []
    return result

"""
function: get_synonyms
returns synonyms list based word and its part of speech
"""


def get_synonyms(word, pos):
    synonyms = []
    for syn in wordnet.synsets(word, pos=pos):
        for lemmas_iterator in syn.lemmas():
            if word.lower != lemmas_iterator.name():
                synonyms.append(lemmas_iterator.name())
    return list(set(synonyms))

"""
function: get_similerty_score
returns similerty score by putting candidate word in given sentence
"""


def get_similerty_score(doc, candidate, synonym):
    window_size = 5
    start = candidate.i - window_size
    if start < 0:
        start = 0
    end = candidate.i + window_size
    if end > len(doc):
        end = len(doc)
    try:
        return(doc[start:end].similarity(nlp(synonym)))
    except Exception:
        return(-1)

"""
function: get_similerty_score
returns similerty score by putting candidate word in given sentence
"""


def get_sentence_score(doc2, doc1):
    try:
        # print(doc1.similarity(doc2))
        return doc1.similarity(doc2)
    except Exception:
        return -1
"""
function: make_variation
input_params:
    sentence: input sentence
returns list of variations of input sentence by replacing 
    non-important words with its synonyms
"""


def make_variation(sentence):
    doc = nlp(sentence)
    chunks_index = []
    for chunk in doc.noun_chunks:
        chunks_index += list(range(chunk.start, chunk.end))
    chunks_index = list(set(chunks_index))
    final_sentences = []
    final_words = []
    for token in doc:
        if token.i in chunks_index:
            continue
        if token.pos_ not in ["VERB", "NOUN", "ADJ"]:
            continue
        if token.pos_ == "VERB":
            list_syns = get_synonyms(token.text, 'v')
        elif token.pos_ == "NOUN":
            list_syns = get_synonyms(token.text, 'n')
        elif token.pos_ == "ADJ":
            list_syns = get_synonyms(token.text, 'a')
        else:
            list_syns = get_synonyms(token.text, 'r')
        temp_syn_list = []
        for synonym in list_syns:
            if get_similerty_score(doc, token, synonym) > 0.7:
                replace_word = synonym
                if token.pos_ == "VERB":
                    try:
                        replace_word = getAllInflections(synonym)[
                            token.tag_][0]
                    except Exception:
                        pass
                temp_syn_list.append((replace_word, token.i))
        if len(temp_syn_list) > 0:
            final_words.append(temp_syn_list)

    final_word_list = [[sub_word] for word in final_words for sub_word in word]
    all_comb = []
    for iterator in range(2, len(final_words)):
        for item_comb in list(combinations(final_words, iterator)):
            all_comb += list(product(*list(item_comb)))
    all_comb += final_word_list

    for item_comb in all_comb:
        temp_sent = ""
        for iterator, comb_value in enumerate(item_comb):
            if iterator == 0:
                temp_sent += str(doc[:comb_value[1]]).strip() + " " + comb_value[0] + " "
            else:
                temp_sent += str(doc[item_comb[iterator - 1][1] + 1:comb_value[1]]
                                 ).strip() + " " + comb_value[0] + " "

        temp_sent += str(doc[item_comb[-1][1] + 1:]).strip()
        final_sentences.append(temp_sent.strip().lower())
    final_sentences = sorted(
        final_sentences, key=partial(get_sentence_score, doc1=doc))
    return final_sentences
"""
function: make_temp_variations_for_can_i
input_params
    sentence: input sentence
returns list of variations of for "can" type of questions
"""


def make_temp_variations_for_can_i(sentence):
    doc = nlp(sentence)
    sent_list = []
    template_found = ""
    if doc[1].pos_ == "PRON":
        # print("bhbj")
        template_found = "can " + doc[1].text
        pron_word = doc[1].text
    else:
        last = 0
        for doc_iterator in range(1, len(doc)):
            if doc[doc_iterator].tag_ in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
                last = doc_iterator
                break
            if doc[doc_iterator].pos_ not in ["NOUN", "PROPN", "NUM", "ADJ", "DET", "ADV"]:
                break
        if last != 0:
            template_found = "can " + doc[1:last].text
            pron_word = doc[1:last].text

    if template_found != "":
        for template in ALL_TEMPLATES["can_i"]["all"]:
            temp_sent = (sentence.replace(template_found.lower().strip(
            ), template.lower().replace("pron", pron_word).strip())).strip()
            sent_list.append(temp_sent)
    return sent_list
"""
function: make_temp_variations_for_is_type
input_params
    sentence: input sentence
returns list of variations for "is" type question
"""


def make_temp_variations_for_is_type(sentence):
    syns_of_necess = ["necessary", "essential", "crucial",
                      "mandatory", "needed", "compulsory", "required"]
    sent_list = [sentence]
    template_found1 = ""
    doc = nlp(sentence)
    if doc[1].pos_ == "PRON":
        template_found1 = "is " + doc[1].text
        pron_word = doc[1].text
    else:
        last = 0
        for iterator in range(1, len(doc)):
            if doc[iterator].tag_ in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "ADJ", "ADV"]:
                last = iterator
                break
            if doc[iterator].pos_ not in ["NOUN", "PROPN", "NUM", "DET"]:
                break
        if last != 0:
            template_found1 = "is " + doc[1:last].text
            pron_word = doc[1:last].text
    if template_found1 != "":
        for template in ALL_TEMPLATES["is_it"]["all"]:
            temp_sent = (sentence.replace(template_found1.lower().strip(
            ), template.lower().replace("pron", pron_word).strip())).strip()
            sent_list.append(temp_sent)
    w_found = ""
    for syns_necess_items in syns_of_necess:
        if syns_necess_items in sentence:
            w_found = syns_necess_items
            break
    if w_found != "":
        for syns_necess_items in syns_of_necess:
            if w_found != syns_necess_items:
                sent_list.append(sentence.replace(w_found, syns_necess_items))
    final_sent_list = sent_list
    return list(set(final_sent_list))
"""
function: make_how_do_to_what_is
input_params
    sentence: input sentence
covenrts "how" type question into "what" type
"""


def make_how_do_to_what_is(sentence):
    doc = nlp(sentence)
    if(doc[1].text == "to"):
        try:
            verb_ing_wrds = getAllInflections(doc[2].text)['VBG']
        except Exception:
            verb_ing_wrds = nounify(doc[2].text)
        if len(verb_ing_wrds) > 0:
            if verb_ing_wrds[0] == "processing":
                start_sent = ["what are " + verb_ing_wrds[0] + " steps"]
            else:
                start_sent = ["what is " + verb_ing_wrds[0] +
                              " process", "what are " + verb_ing_wrds[0] + " steps"]
            try:
                if doc[3].pos_ != "ADP":
                    start_sent = [x + " for" for x in start_sent]
            except Exception:
                pass
            if verb_ing_wrds[0] == "processing":
                start_sent += ["what are the steps to process"]
            else:
                start_sent += ["what is the process to " +
                               doc[2].text, "what are the steps to " + doc[2].text]
            try:
                return [sentence.replace(doc[0:3].text, x.lower().strip()).strip() for x in start_sent]
            except Exception:
                return [sentence.replace(doc[0:2].text, x.lower().strip()).strip() for x in start_sent]
        else:
            return []
    elif (doc[1].pos_ == "AUX") or ("aux" in str(doc[1].dep_).lower()):
        last = 0
        for iterator in range(2, len(doc)):
            if doc[iterator].tag_ in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
                last = iterator
                break
            if doc[iterator].pos_ not in ["NOUN", "PROPN", "NUM", "ADJ", "DET", "ADV", "PRON"]:
                break

        if last != 0:
            template_found = "how " + doc[1:last].text
            # pron_word = doc[2:last].text
            if doc[len(template_found.split(" "))].text == "process":
                noun_verb = ["processing"]
            else:
                noun_verb = nounify(doc[len(template_found.split(" "))].text)
            if len(noun_verb) == 0:
                try:
                    noun_verb = getAllInflections(
                        doc[len(template_found.split(" "))].text)['VBG']
                except Exception:
                    pass

            if len(noun_verb) > 0:
                if noun_verb[0] == "processing":
                    start_sent = ["what are " + noun_verb[0] + " steps"]
                else:
                    start_sent = ["what is " + noun_verb[0] +
                                  " process", "what are " + noun_verb[0] + " steps"]
                try:
                    if doc[len(template_found.split(" ")) + 1].pos_ != "ADP":
                        start_sent = [word + " for" for word in start_sent]
                except Exception:
                    pass
                if noun_verb[0] == "processing":
                    start_sent += ["what are the steps to process"]
                else:
                    start_sent += ["what is the process to " + doc[len(template_found.split(
                        " "))].text, "what are the steps to " + doc[len(template_found.split(" "))].text]
                return [sentence.replace(template_found.lower().strip() + " " + doc[len(template_found.split(" "))].text, x.lower().strip()).strip() for x in start_sent]
            else:
                return []
        else:
            return[]
    else:
        return []
"""
function: make_temp_variations
input_params
    sentence: input sentence
    templates: tempelate variation list
    template_found : matched template sub word in sentence
returns list of variations of input sentence 
"""


def make_temp_variations(sentence, templates, template_found):
    is_plural = False
    if "are" in sentence.split(" "):
        sentence = sentence.replace(" are ", " is ")
        is_plural = True
    sent_list = []
    for template in templates:
        if template_found.lower().strip() != template.lower().strip():
            temp_sent = (sentence.replace(
                template_found.lower().strip(), template.lower().strip())).strip()
            if is_plural:
                temp_sent = temp_sent.replace(" is ", " are ")
            sent_list.append(temp_sent)
    return sent_list
"""
function: make_final_variations
input_params:
    sentence: input sentence
    SYNONYM_RQD : True/False based on whether you want to consider 
        synonyms while generating variaitions
returns list of variations of input sentence based of templates/synonyms
"""


def make_final_variations(sentence, SYNONYM_RQD=False, get_all_results=False):
    sentence = sentence.strip().lower()
    sentence = decontracted(sentence)
    doc = nlp(sentence)
    template_found = ""
    template_type = ""
    total_variations = []

    if doc[0].pos_ == 'VERB':
        sentence = 'how to ' + sentence
        total_variations = [sentence]
    for temp_type in ALL_TEMPLATES:
        for template in ALL_TEMPLATES[temp_type]["all"]:
            if sentence.startswith(template.lower()):
                template_found = template.lower().strip()
                template_type = temp_type
                break
            if "are" in sentence.split(" "):
                if sentence.startswith(template.lower().replace("is", "are")):
                    template_found = template.lower().strip()
                    template_type = temp_type
                    break
            if "one" in sentence.split(" "):
                if sentence.startswith(template.lower().replace("i", "one")):
                    template_found = template.lower().strip()
                    template_type = temp_type
                    break
        if template_found != "":
            break
    synonyms_list = []
    if SYNONYM_RQD:
        synonyms_list = make_variation(sentence)
        total_variations += synonyms_list
    if "one" in sentence.split(" "):
        sentence = sentence.replace(" one ", " i ")
    temp_variations = []
    if sentence.startswith("can"):
        temp_variations = make_temp_variations_for_can_i(sentence)
    elif (sentence).startswith("is "):
        temp_variations += make_temp_variations_for_is_type(sentence)
    elif template_found != "":
        temp_variations = make_temp_variations(
            sentence, ALL_TEMPLATES[template_type]["all"], template_found)

    if template_type == "how_do" or sentence.startswith("how"):
        sent1 = make_how_do_to_what_is(sentence)
        if len(sent1) > 0:
            for sent1_items in sent1:
                temp_variations += make_temp_variations(
                    sent1_items, ALL_TEMPLATES["what_is"]["all"], "what is")
    if SYNONYM_RQD:
        for sent1_items in temp_variations:
            synonyms_list += make_variation(sent1_items)
        total_variations += synonyms_list
    total_variations += temp_variations
    if get_all_results:
        return list(set(temp_variations)), list(set(synonyms_list))
    else:
        return list(set(total_variations))[:10]
