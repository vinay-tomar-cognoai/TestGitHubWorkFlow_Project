import nltk
import ast
import pdfplumber
from elasticsearch import Elasticsearch

from django.utils import timezone
from django.conf import settings
from EasySearchApp.constants import PDF_SEARCH_ACTIVE_STATUS, PDF_SEARCH_INACTIVE_STATUS, \
    PDF_SEARCH_INDEXING_STATUS, PDF_SEARCH_NOT_INDEXED_STATUS, PDF_SEARCH_INDEXED_STATUS

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import logging
import sys
import os

logger = logging.getLogger(__name__)

PDF_INDEX_KEY = "easysearch_pdf_index_{domain_name}_{bot_id}"
PDF_CONTENT_MAX_LEN = 300


def easysearch_start_indexing(bot_obj, EasyPDFSearcher, PDFSearchIndexStat):
    bot_pk = None
    try:
        bot_pk = bot_obj.pk

        domain_name = settings.EASYCHAT_DOMAIN

        pdf_index_key = PDF_INDEX_KEY.format(
            domain_name=domain_name,
            bot_id=str(bot_obj.pk))

        pdf_search_index_stat_obj = PDFSearchIndexStat.objects.filter(bot=bot_obj).first()
        pdf_search_index_stat_obj.is_indexing_in_progress = True
        pdf_search_index_stat_obj.start_datetime = timezone.now()
        pdf_search_index_stat_obj.save()

        easysearch_delete_index(pdf_index_key)

        pdf_search_objs = EasyPDFSearcher.objects.filter(
            bot_obj=bot_obj, is_deleted=False)

        logger.error("START PDF INDEXING",
                     extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        is_all_pdf_indexed = True
        for pdf_search_obj in pdf_search_objs:
            is_indexing_done = create_easysearch_index(pdf_search_obj, pdf_index_key)

            if is_indexing_done == False:
                is_all_pdf_indexed = False

        pdf_search_index_stat_obj.is_indexing_in_progress = False
        pdf_search_index_stat_obj.save()

        if is_all_pdf_indexed:
            easysearch_set_indexing_required(False, bot_obj, PDFSearchIndexStat)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error easysearch_start_indexing %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})


def easysearch_check_index_exist(pdf_index_key):
    try:
        if settings.ELASTIC_SEARCH_OBJ.indices.exists(index=pdf_index_key):
            return True

        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error easysearch_start_indexing %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return False


def easysearch_delete_index(pdf_index_key):
    try:
        if easysearch_check_index_exist(pdf_index_key):
            settings.ELASTIC_SEARCH_OBJ.indices.delete(index=pdf_index_key)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error easysearch_start_indexing %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def easysearch_get_saturated_text(text):
    try:
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text)

        filtered_text_list = []

        for word in word_tokens:
            if word not in stop_words:
                filtered_text_list.append(word)

        filtered_text = " ".join(filtered_text_list)
        return filtered_text

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error easysearch_start_indexing %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return text


def create_easysearch_index(pdf_search_obj, pdf_index_key):

    prev_pdf_search_status = PDF_SEARCH_NOT_INDEXED_STATUS
    try:
        prev_pdf_search_status = pdf_search_obj.status
        pdf_search_obj_key = str(pdf_search_obj.key)
        pdf_search_obj.status = PDF_SEARCH_INDEXING_STATUS
        pdf_search_obj.save()

        important_pages = pdf_search_obj.important_pages
        if important_pages:
            important_pages = important_pages.strip().split(",")
        else:
            important_pages = []

        skipped_pages = pdf_search_obj.skipped_pages
        if skipped_pages:
            skipped_pages = skipped_pages.strip().split(",")
        else:
            skipped_pages = []

        file_path = pdf_search_obj.file_path
        file_path = settings.BASE_DIR + file_path

        pdf_file_name = pdf_search_obj.name

        if not os.path.exists(file_path):
            return

        logger.error("Open PDF file: pdf index key %s",
                     pdf_index_key, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)

            for page_index in range(0, total_pages):
                page_number = page_index + 1
                if str(page_number) in skipped_pages:
                    continue

                is_important_page = False
                if str(page_number) in important_pages:
                    is_important_page = True

                page_obj = pdf.pages[page_index]
                page_text = page_obj.extract_text()
                saturated_text = easysearch_get_saturated_text(page_text)
                page_id = pdf_search_obj_key + "__" + str(page_index)

                data = {
                    "page_index": page_index,
                    "page_number": page_number,
                    "pdf_search_obj_key": pdf_search_obj_key,
                    "text": page_text,
                    "saturated_text": saturated_text,
                    "is_important_page": is_important_page,
                    "pdf_file_name": pdf_file_name,
                }

                settings.ELASTIC_SEARCH_OBJ.index(
                    index=pdf_index_key,
                    doc_type='search',
                    id=page_id,
                    body=data,
                    refresh='wait_for')

            logger.error("Close PDF file: pdf index key %s",
                         pdf_index_key, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        logger.error("Post Close PDF file: pdf index key %s",
                     pdf_index_key, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        pdf_search_obj.status = PDF_SEARCH_ACTIVE_STATUS
        pdf_search_obj.save()

        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_easysearch_index %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        pdf_search_obj.status = prev_pdf_search_status
        pdf_search_obj.save()

        return False


def easysearch_record_pdf_search_analytics(pdf_search_obj, EasyPDFSearcherAnalytics):
    try:
        pdf_search_analytics_obj = EasyPDFSearcherAnalytics.objects.filter(
            pdf_searcher=pdf_search_obj).first()
        if pdf_search_analytics_obj is None:
            pdf_search_analytics_obj = EasyPDFSearcherAnalytics.objects.create(
                pdf_searcher=pdf_search_obj)

        pdf_search_analytics_obj.search_count += 1
        pdf_search_analytics_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error easysearch_record_pdf_search_analytics %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def easysearch_get_matched_pdf_text(pdf_content, pattern):
    try:
        searched_index = pdf_content.lower().find(pattern.lower())
        if searched_index < 0:
            return pdf_content

        pdf_content = pdf_content[searched_index:]
        pdf_content = pdf_content[:PDF_CONTENT_MAX_LEN]

        return pdf_content

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error easysearch_get_matched_pdf_text %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return pdf_content


def get_easysearch_pdf_result(bot_obj, text, EasyPDFSearcher, EasyPDFSearcherAnalytics):
    bot_pk = None
    try:
        token_list = nltk.word_tokenize(text)
        stop_words = ast.literal_eval(bot_obj.stop_keywords)
        token_list = [token for token in token_list if token not in stop_words]
        text = ' '.join(token_list)
        bot_pk = bot_obj.pk
        if not text:
            return []

        if len(text) < 3:
            return []

        domain_name = settings.EASYCHAT_DOMAIN

        pdf_index_key = PDF_INDEX_KEY.format(
            domain_name=domain_name,
            bot_id=str(bot_obj.pk))

        logger.info("PDF Searching Start : pdf index key %s",
                     pdf_index_key, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        searched_result = settings.ELASTIC_SEARCH_OBJ.search(
            index=pdf_index_key,
            body={
                'query': {
                    'match': {
                        "saturated_text": text,
                    }
                }
            })

        result = searched_result["hits"]["hits"]

        result = sorted(
            result, key=lambda obj: obj['_source']['is_important_page'], reverse=True)

        pdf_search_result = []
        pdf_search_key_instance_map = dict()
        total_searched_results = 0

        for result_obj in result:
            result_data = result_obj['_source']

            pdf_search_obj_key = result_data["pdf_search_obj_key"]

            if pdf_search_obj_key not in pdf_search_key_instance_map:
                pdf_search_obj = EasyPDFSearcher.objects.filter(
                    key=pdf_search_obj_key, status=PDF_SEARCH_ACTIVE_STATUS, is_deleted=False).first()

                if pdf_search_obj is None:
                    continue

                pdf_search_key_instance_map[pdf_search_obj_key] = pdf_search_obj

            page_number = result_data["page_number"]
            pdf_file_name = result_data["pdf_file_name"]
            pdf_content = easysearch_get_matched_pdf_text(
                result_data["text"], text)

            source_url = settings.EASYCHAT_HOST_URL + "/chat/pdf/redirect/" + \
                pdf_search_obj_key + "/" + str(page_number)

            pdf_search_result.append({
                "content": pdf_content,
                "page_number": page_number,
                "link": source_url,
                "title": pdf_file_name,
                "pattern": text,
            })

            total_searched_results += 1
            if total_searched_results == 10:
                break

        for pdf_search_obj in pdf_search_key_instance_map.values():
            easysearch_record_pdf_search_analytics(
                pdf_search_obj, EasyPDFSearcherAnalytics)

        logger.info("Total searched Result for pdf index key %s is %s for text %s",
                     pdf_index_key, str(len(pdf_search_result)), str(text), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        return pdf_search_result
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_easysearch_pdf_result %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})
        return []


def easysearch_check_indexing_in_progress(bot_obj, PDFSearchIndexStat):
    bot_pk = None
    try:
        bot_pk = bot_obj.pk
        indexing_stat_obj = PDFSearchIndexStat.objects.filter(
            bot=bot_obj).first()

        is_indexing_in_progress = False
        current_time = timezone.now()

        if indexing_stat_obj is not None:
            if indexing_stat_obj.is_indexing_in_progress:
                total_seconds = int(
                    (current_time - indexing_stat_obj.start_datetime).total_seconds())
                if total_seconds <= 3600:
                    is_indexing_in_progress = True

        return is_indexing_in_progress
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error easysearch_check_indexing_in_progress %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        return False


def easysearch_set_indexing_required(is_indexing_required, bot_obj, PDFSearchIndexStat):
    bot_pk = None
    try:

        bot_pk = bot_obj.pk

        pdf_search_index_stat_obj = PDFSearchIndexStat.objects.filter(bot=bot_obj).first()
        if pdf_search_index_stat_obj is None:
            pdf_search_index_stat_obj = PDFSearchIndexStat.objects.create(bot=bot_obj)

        pdf_search_index_stat_obj.is_indexing_required = is_indexing_required
        pdf_search_index_stat_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error easysearch_set_indexing_required %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})


def easysearch_check_indexing_required(bot_obj, PDFSearchIndexStat):
    bot_pk = None
    try:
        bot_pk = bot_obj.pk

        indexing_stat_obj = PDFSearchIndexStat.objects.filter(
            bot=bot_obj).first()

        if indexing_stat_obj is None:
            return False

        if indexing_stat_obj.is_indexing_required:
            return True

        return False

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error easysearch_check_indexing_required %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_pk)})

        return False


def easysearch_check_server_active():
    try:
        pdf_index_key = "test_index"
        settings.ELASTIC_SEARCH_OBJ.indices.exists(index=pdf_index_key)

        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error easysearch_check_server_active %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return False
