# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django REST framework
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.paginator import Paginator

# Django App
from django.shortcuts import render
from django.shortcuts import redirect, HttpResponse

# Apps modules
from EasySearchApp.models import *
from EasyChatApp.models import *
from EasySearchApp.utils import *

# Libraries
from spellchecker import SpellChecker

import sys
import time

# Logger
import logging

logger = logging.getLogger(__name__)

# Spell Checker Object
spell = SpellChecker()

"""
function: preprocess_SpellChecker

It will preprocess and save all the words defined in "constants.py" which can be used for spell checker.
"""


def preprocess_spell_checker():
    try:
        for word in BANK_KEYWORDS_ADD:
            spell.word_frequency.add(word)

        for word in BANK_KEYWORDS_REMOVE:
            try:
                if word in spell.word_frequency:
                    spell.word_frequency.remove(word)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("preprocess_spell_checker word does not exists: %s at %s",
                             str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("preprocess_spell_checker: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})


# Calling preprocess_SpellChecker
preprocess_spell_checker()


"""
function: HomePage

It is using GET method to get "source" -> User and "query" -> Search query and rendering to "search-result.html". 
It will not show documents( *.pdf etc).
"""


def HomePage(request):
    try:
        if request.method == "GET":
            if "query" in request.GET and "source" in request.GET:
                source = request.GET["source"]
                query = request.GET["query"]
                bot_id = request.GET["bot_id"]

                bot_obj = Bot.objects.get(pk=int(bot_id))
                bot_slug = bot_obj.slug
                # If user want to search the wrong query
                auto_correct = True
                if "auto_correct" in request.GET and request.GET["auto_correct"] == "false":
                    auto_correct = False

                username_obj = User.objects.get(username=str(source))
                search_user_obj = SearchUser.objects.get(user=username_obj)

                # Search Query time has been started
                start_time = time.time()

                show_documents = True
                if(search_user_obj.show_documents == False):
                    show_documents = False

                # Checking spelling of the query
                spell_check_flag = False
                corrected_query = ""

                logger.info("Running Spell Checker", extra={
                            'AppName': 'EasySearch'})
                if search_user_obj.spell_checker:
                    if auto_correct:
                        query_texts = query.split(" ")
                        for query_text in query_texts:
                            corrected_query += spell.correction(query_text)
                            corrected_query += " "
                        corrected_query = corrected_query[:-1]
                    else:
                        corrected_query = query
                else:
                    corrected_query = query

                # Searching query in elastic search
                if(corrected_query == query):
                    res = search_query(corrected_query)
                else:
                    spell_check_flag = True
                    res = search_query(corrected_query)

                # Getting ElasticSearch Response
                easysearch_hits = []
                try:
                    easysearch_hits = res["hits"]["hits"]
                except Exception:
                    pass

                """
                Getting all the required information from ElasticSearch Response
                    1. url_pk : ID of URL
                    2. url : URL of the website
                    3. title: Title of the website
                    4. Description: Description of the website
                    5. Content: All the <p> tag "rectified" content in the website
                """
                results = []
                for easysearch_hit in easysearch_hits:
                    bot_slug_search = easysearch_hit['_source']['bot']
                    if(bot_slug == bot_slug_search):
                        source_name = easysearch_hit['_source']['name']
                        source_name = source_name.lower()
                        if(easysearch_hit['_source']['type'] == "html" and source == source_name):
                            if "url_pk" not in easysearch_hit["_source"]:
                                continue
                            filter_url_pk = easysearch_hit[
                                '_source']['url_pk']
                            filter_url = easysearch_hit[
                                '_source']['url'][:90]
                            filter_title = easysearch_hit[
                                '_source']['title'][:60] + "..."
                            filter_description = easysearch_hit[
                                '_source']['description']
                            filter_content = easysearch_hit[
                                '_source']['content'][:200]
                            temp_dict = {}
                            temp_dict["url"] = filter_url
                            temp_dict["url_pk"] = filter_url_pk
                            temp_dict["title"] = filter_title
                            temp_dict["content"] = filter_content
                            temp_dict["description"] = filter_description
                            results.append(temp_dict)
                total_results = len(results)

                if(total_results == 0):
                    if(search_user_obj.show_documents):
                        results = []
                        for easysearch_hit in easysearch_hits:
                            bot_slug_search = easysearch_hit['_source']['bot']
                            if(bot_slug == bot_slug_search):
                                source_name = easysearch_hit['_source']['name']
                                source_name = source_name.lower()
                                if(easysearch_hit['_source']['type'] == "pdf" and source == source_name):
                                    if "url_pk" not in easysearch_hit["_source"]:
                                        continue
                                    filter_url_pk = easysearch_hit[
                                        '_source']['url_pk']
                                    filter_url = easysearch_hit[
                                        '_source']['url'][:90]
                                    filter_title = easysearch_hit[
                                        '_source']['title']
                                    filter_description = easysearch_hit[
                                        '_source']['description']
                                    filter_content = easysearch_hit[
                                        '_source']['content'][:200]
                                    temp_dict = {}
                                    temp_dict["url"] = filter_url
                                    temp_dict["url_pk"] = filter_url_pk
                                    temp_dict["title"] = filter_title
                                    temp_dict["content"] = filter_content
                                    temp_dict[
                                        "description"] = filter_description
                                    results.append(temp_dict)
                        total_results = len(results)
                # Search Query Time
                diff_time = round(time.time() - start_time, 3)

                return render(request, 'EasySearchApp/search_result.html', {
                    "source": source,
                    "query": query,
                    "results": results,
                    "diff_time": diff_time,
                    "total_results": total_results,
                    "spellCheckFlag": spell_check_flag,
                    "corrected_query": corrected_query,
                    "show_documents": show_documents,
                    "bot_id": bot_id
                })
        else:
            return render(request, 'EasySearchApp/error_500.html')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("HomePage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})
    return render(request, 'EasySearchApp/base.html')


"""
function: DocumentsPage

It is using GET method to get "source" -> User and "query" -> Search query and rendering to "search_documents.html".
It will only show documents.
"""


def DocumentsPage(request):
    try:
        if request.method == "GET":
            if "query" in request.GET and "source" in request.GET:
                source = request.GET["source"]
                query = request.GET["query"]
                bot_id = request.GET["bot_id"]
                bot_obj = Bot.objects.get(pk=int(bot_id))
                bot_slug = bot_obj.slug

                # If user want to search the wrong query
                auto_correct = True
                if "auto_correct" in request.GET and request.GET["auto_correct"] == "false":
                    auto_correct = False

                username_obj = User.objects.get(username=str(source))
                search_user_obj = SearchUser.objects.get(user=username_obj)

                # Search Query time has been started
                start_time = time.time()

                # Checking spelling of the query
                spell_check_flag = False
                corrected_query = ""
                logger.info("Running Spell Checker", extra={
                            'AppName': 'EasySearch'})
                if search_user_obj.spell_checker:
                    if auto_correct:
                        query_texts = query.split(" ")
                        for query_text in query_texts:
                            corrected_query += spell.correction(query_text)
                            corrected_query += " "
                        corrected_query = corrected_query[:-1]
                    else:
                        corrected_query = query
                else:
                    corrected_query = query
                # Searching query in elastic search
                if(corrected_query == query):
                    res = search_query(query)
                else:
                    spell_check_flag = True
                    res = search_query(corrected_query)

                # Getting ElasticSearch Response
                easysearch_hits = []
                try:
                    easysearch_hits = res["hits"]["hits"]
                except Exception:
                    pass

                """
                Getting all the required information from ElasticSearch Response
                    1. url_pk : ID of URL
                    2. url : URL of the website
                    3. title: Title of the website
                    4. Description: Description of the website
                    5. Content: All the <p> tag "rectified" content in the website
                """
                results = []
                for easysearch_hit in easysearch_hits:
                    bot_slug_search = easysearch_hit['_source']['bot']
                    if(bot_slug == bot_slug_search):
                        source_name = easysearch_hit['_source']['name']
                        source_name = source_name.lower()
                        if(easysearch_hit['_source']['type'] == "pdf" and source == source_name):
                            if "url_pk" not in easysearch_hit["_source"]:
                                continue
                            filter_url_pk = easysearch_hit[
                                '_source']['url_pk']
                            filter_url = easysearch_hit[
                                '_source']['url'][:90]
                            filter_title = easysearch_hit[
                                '_source']['title'][:60]
                            filter_description = easysearch_hit[
                                '_source']['description']
                            filter_content = easysearch_hit[
                                '_source']['content'][:200]
                            temp_dict = {}
                            temp_dict["url"] = filter_url
                            temp_dict["url_pk"] = filter_url_pk
                            temp_dict["title"] = filter_title
                            temp_dict["content"] = filter_content
                            temp_dict["description"] = filter_description
                            results.append(temp_dict)
                total_results = len(results)
                # Search Query Time
                diff_time = round(time.time() - start_time, 3)
                if(search_user_obj.show_documents):
                    return render(request, 'EasySearchApp/search_documents.html', {
                        "source": source,
                        "query": query,
                        "results": results,
                        "diff_time": diff_time,
                        "total_results": total_results,
                        "spellCheckFlag": spell_check_flag,
                        "corrected_query": corrected_query,
                        "bot_id": bot_id
                    })
                else:
                    return render(request, 'EasySearchApp/base.html', {})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("HomePage: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})
    return render(request, 'EasySearchApp/base.html', {})


"""
function: SearchRedirect
input params:
            url_pk (mandatory)

When user will click the link in EasySearch result than the click_count in WebsiteLink will be incremented
"""


def SearchRedirect(request, url_pk):
    try:
        website_url_obj = WebsiteLink.objects.get(pk=int(url_pk))
        website_url_obj.click_count = website_url_obj.click_count + 1
        website_url_obj.save()
        return redirect(str(website_url_obj.link))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("SearchRedirect: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})
        return render(request, 'EasySearchApp/error_500.html')


"""
function: StartCrawlingAPI

It crawl the links till a given depth.
"""


class StartCrawlingAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        try:
            username = request.user.username
            logger.info(request.data["json_string"],
                        extra={'AppName': 'EasySearch'})
            data = decrypt_variable(request.data["json_string"])
            data = json.loads(data)
            link = data["url"]
            hyper_text = "HTTPS"  # It may change as per requirement
            bot_id = data["bot_id"]
            index_value = "-1"  # It may change as per requirement
            bot_obj = Bot.objects.get(pk=int(bot_id))
            easy_search_config = EasySearchConfig.objects.filter(bot=bot_obj)
            if easy_search_config:
                if easy_search_config[0].feature == "1":
                    username_obj = User.objects.get(username=username)
                    search_user_obj = SearchUser.objects.get(user=username_obj)
                    website_obj = None
                    try:
                        website_obj = WebsiteLink.objects.get(
                            search_user=search_user_obj, link=link, bot=bot_obj)
                        website_obj.hyper_text = hyper_text.lower()
                        website_obj.index_level = index_value
                        website_obj.is_crawl = True
                        website_obj.save()
                    except Exception:
                        website_obj = WebsiteLink.objects.create(search_user=search_user_obj,
                                                                 link=link,
                                                                 hyper_text=hyper_text.lower(),
                                                                 bot=bot_obj, index_level=index_value, is_crawl=True)

                    response["message"] = "Save Successfully"
                    response["status"] = 200
                else:
                    response["message"] = "Unsuccessfull"
                    response["status"] = 305
            else:
                response["message"] = "Save Unsuccessfull"
                response["status"] = 305
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error StartCrawlingAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


StartCrawling = StartCrawlingAPI.as_view()

"""
function: EasySearchQueryAPI

API URL = http://127.0.0.1:8000/search/search/api?source="SOURCE'&query=QUERY&page=PAGENUMBER&auto_correct=BOOL
"""


class EasySearchQueryAPI(APIView):

    def get(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500
        response["message"] = "Internal Server Error"
        try:
            logger.info("Into EasySearchQueryAPI...",
                        extra={'AppName': 'EasySearch'})
            source = request.GET["source"]
            query = request.GET["query"]
            page = request.GET["page"]
            auto_correct = request.GET["auto_correct"]

            if auto_correct == "false":
                auto_correct = False

            username_obj = User.objects.get(username=str(source))
            search_user_obj = SearchUser.objects.get(user=username_obj)

            logger.info("User: %s", username_obj,
                        extra={'AppName': 'EasySearch'})
            logger.info("SearchUser: %s", search_user_obj,
                        extra={'AppName': 'EasySearch'})

            # Checking spelling of the query
            spell_check_flag = False
            corrected_query = ""
            logger.info("Running Spell Checker", extra={
                        'AppName': 'EasySearch'})
            if auto_correct:
                query_texts = query.split(" ")
                for query_text in query_texts:
                    corrected_query += spell.correction(query_text)
                    corrected_query += " "
            else:
                corrected_query = query
            # Search Query time has been started
            start_time = time.time()

            # Searching query in elastic search
            if(corrected_query == query):
                res = search_query(query)
            else:
                spell_check_flag = True
                res = search_query(corrected_query)

            logger.info("spellCheckFlag: %s", str(spell_check_flag),
                        extra={'AppName': 'EasySearch'})

            # Getting ElasticSearch Response
            easysearch_hits = []
            try:
                easysearch_hits = res["hits"]["hits"]
            except Exception:
                pass

            results = []
            for easysearch_hit in easysearch_hits:
                source_name = easysearch_hit['_source']['name']
                source_name = source_name.lower()
                if(source == source_name):
                    if "url_pk" not in easysearch_hit["_source"]:
                        continue

                    filter_url_pk = easysearch_hit['_source']['url_pk']
                    filter_url = easysearch_hit['_source']['url']
                    filter_title = easysearch_hit['_source']['title']
                    filter_description = easysearch_hit[
                        '_source']['description']
                    filter_content = easysearch_hit['_source']['content']
                    temp_dict = {}
                    temp_dict["url_pk"] = filter_url_pk
                    temp_dict["url"] = filter_url
                    temp_dict["title"] = filter_title
                    temp_dict["description"] = filter_description
                    temp_dict["content"] = filter_content
                    results.append(temp_dict)
            page_obj = Paginator(results, 10)

            page_result = page_obj.page(page)

            results = page_result.object_list
            diff_time = round(time.time() - start_time, 3)
            response["status"] = 200
            response["message"] = "success"
            response["query"] = corrected_query
            response["results"] = results
            response["search_time"] = diff_time
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Error EasySearchQueryAPI: %s at %s",
                         str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})

        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(json.dumps(response))
        return Response(data=response)


EasySearchQuery = EasySearchQueryAPI.as_view()


def EnableGoogleSearch(request):
    response = {
        "status_code": 500,
        "status_message": "Internal Server Error",
    }
    try:
        data = decrypt_variable(request.POST["data"])
        data = json.loads(data)
        bot_id = data["bot_id"]
        search_cx = data["search_cx"]
        bot_obj = Bot.objects.get(pk=int(bot_id))
        easy_search_config = EasySearchConfig.objects.filter(bot=bot_obj)
        if easy_search_config:
            easy_search_config[0].search_cx = search_cx
            easy_search_config[0].feature = "2"
            easy_search_config[0].save()
        else:
            EasySearchConfig.objects.create(bot=bot_obj,
                                            feature="2",
                                            search_cx=str(search_cx))
        response["status_code"] = 200
        response["status_message"] = "SUCCESS"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EnableGoogleSearch: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})

    custom_encrypt_obj = CustomEncrypt()
    response = custom_encrypt_obj.encrypt(json.dumps(response))
    return HttpResponse(json.dumps(response), content_type="application/json")


def EnableElasticSearch(request):
    response = {
        "status_code": 500,
        "status_message": "Internal Server Error",
    }
    try:
        data = decrypt_variable(request.POST["data"])
        data = json.loads(data)
        bot_id = data["bot_id"]
        bot_obj = Bot.objects.get(pk=int(bot_id))
        easy_search_config = EasySearchConfig.objects.filter(bot=bot_obj)
        if easy_search_config:
            easy_search_config[0].feature = "1"
            easy_search_config[0].save()
        else:
            EasySearchConfig.objects.create(bot=bot_obj,
                                            feature="1",)
        response["status_code"] = 200
        response["status_message"] = "SUCCESS"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("EnableElasticSearch: %s at %s", e, str(
            exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})

    custom_encrypt_obj = CustomEncrypt()
    response = custom_encrypt_obj.encrypt(json.dumps(response))
    return HttpResponse(json.dumps(response), content_type="application/json")
