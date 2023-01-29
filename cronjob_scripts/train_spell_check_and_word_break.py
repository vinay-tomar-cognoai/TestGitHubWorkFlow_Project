import os
import json
import wordninja
from django.conf import settings
from spellchecker import SpellChecker
from EasyChatApp.models import Intent, EasyChatSpellCheckerWord


spell = SpellChecker()

lm = wordninja.LanguageModel(settings.MEDIA_ROOT + 'wordninja_words.txt.gz')

added_words = set()
already_checked_words = {}


def add_word_to_spell_checker(words, bot_obj):
    for word in words:

        if str(bot_obj.pk) in already_checked_words and word in already_checked_words[str(bot_obj.pk)]:
            continue
        elif str(bot_obj.pk) not in already_checked_words:
            already_checked_words[str(bot_obj.pk)] = set()

        already_checked_words[str(bot_obj.pk)].add(word)

        if EasyChatSpellCheckerWord.objects.filter(word=word.lower().strip(), bot=bot_obj):
            continue

        output_word = spell.correction(word)
        output_word = output_word.strip()

        if word != output_word:
            EasyChatSpellCheckerWord.objects.create(word=word.lower().strip(), bot=bot_obj)


def add_word_to_word_splitter(words):
    for word in words:
        if word in added_words:
            continue

        word_split = lm.split(word)

        if word != word_split[0]:
            added_words.add(word)
            print('Added')


def write_to_file():
    with open(settings.MEDIA_ROOT + 'wordninja_words.txt', 'r+') as f:
        content = f.read()

        for word in added_words:
            f.seek(0, 0)
            f.write(word.rstrip('\r\n') + '\n' + content)


def run():
    try:
        cmd = 'gzip -d ' + settings.MEDIA_ROOT + 'wordninja_words.txt.gz'
        os.system(cmd)

        intent_objs = Intent.objects.filter(is_deleted=False)

        count = 0
        for intent_obj in intent_objs:
            try:
                keyword_dict = json.loads(intent_obj.keywords)
                for index_key in keyword_dict.keys():
                    stem_words = set(keyword_dict[index_key].split(","))

                    add_word_to_spell_checker(stem_words, intent_obj.bots.all().first())
                    add_word_to_word_splitter(stem_words)

                count += 1

            except Exception as e:
                print(e)
                continue
        
        write_to_file()
        
        cmd = 'gzip ' + settings.MEDIA_ROOT + 'wordninja_words.txt'
        os.system(cmd)

    except Exception as e:
        cmd = 'gzip ' + settings.MEDIA_ROOT + 'wordninja_words.txt'
        os.system(cmd)
        print(e)
