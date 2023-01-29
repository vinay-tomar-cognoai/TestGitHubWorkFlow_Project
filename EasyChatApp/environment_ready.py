from EasyChatApp.utils import logger
from EasyChatApp.utils_execute_query import preprocess_spell_checker
from EasyChatApp.utils_advanced_nlp import initialize_embedder_and_lemmatizer, load_repeat_variations_training_data

import sys
import threading


def load_spell_checker():
    try:
        spell_check_thread = threading.Thread(target=preprocess_spell_checker, args=())
        spell_check_thread.daemon = True
        spell_check_thread.start()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('load_spell_checker! Error:  %s at %s', str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def load_advanced_nlp_dependencies():
    try:
        initialize_embedder_and_lemmatizer()

        load_repeat_variations_training_data_thread = threading.Thread(target=load_repeat_variations_training_data, args=())
        load_repeat_variations_training_data_thread.daemon = True
        load_repeat_variations_training_data_thread.start()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('load_advanced_nlp_dependencies! Error:  %s at %s', str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
