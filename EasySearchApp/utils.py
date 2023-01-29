from django.conf import settings

# Libraries
from elasticsearch import Elasticsearch
import json
import requests
from bs4 import BeautifulSoup
import os
import sys
from lxml import html
from urllib.parse import urljoin
import tldextract
import textract
import urllib.request

# App Modules
from EasySearchApp.constants import *
from EasyChatApp.models import *

# Logger
import logging

# Encryption
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Cipher import PKCS1_v1_5 as CipherPKCS1_v1_5
from Crypto.Signature import PKCS1_v1_5 as SignaturePKCS1_v1_5
from Crypto.Hash import SHA256
from pkcs7 import PKCS7Encoder
from EasyChatApp.utils_analytics import *
from EasyChatApp.utils_google import *
from EasyChatApp.profanityfilter import ProfanityFilter
from EasySearchApp.utils_custom_encryption import *
import base64

logger = logging.getLogger(__name__)


def decrypt_variable(data):
    try:
        custom_encrypt_obj = CustomEncrypt()
        data = custom_encrypt_obj.decrypt(data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside decrypt_variable: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})
    return data


"""
This function will do searching in ElasticSearch

    Search Queries w.r.t:
        1. Description: 'description'
        2. Content: 'content'
        3. Title: 'title'
        4. URL: 'url'
        5. Keywords: 'keywords'
"""


def search_query(query):
    # Searching on the basis on "description"
    try:
        result = ''
        result = settings.ELASTIC_SEARCH_OBJ.search(index='integrated_easysearch', body={'query':
                                                                                         {'match':
                                                                                          {
                                                                                              'description': query
                                                                                          }
                                                                                          }
                                                                                         })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("search_query: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})
    return result


"""
function: get_website_title

Getting website "title"
"""


def get_website_title(response_soup):
    try:
        title = response_soup.select('title')
        title = title[0].text
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_website_title: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})
        return ""
    return title


"""
function: get_meta_keywords

Getting website ""keywords" in meta tags
"""


def get_meta_keywords(response_soup):
    try:
        meta = response_soup.find_all('meta')
        keywords = ""
        for tag in meta:
            if 'name' in tag.attrs.keys() and tag.attrs['name'].strip().lower() in 'keywords':
                keywords = tag.attrs['content']
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_meta_keywords: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})
        return ""
    return keywords


"""
function: get_meta_description

Getting website "description" in meta tag
"""


def get_meta_description(response_soup):
    try:
        meta = response_soup.find_all('meta')
        description = ""
        for tag in meta:
            if 'name' in tag.attrs.keys() and tag.attrs['name'].strip().lower() in 'description':
                description = tag.attrs['content']
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_meta_description: %s at %s",
                     e, str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})
        return ""
    return description


"""
function: index_website
input params:
            website_url_obj (mandatory)

Indexing of the website
"""


def index_website(website_url_obj):
    try:
        response = requests.get(website_url_obj.link)
        """
        Checking the content type of the website link
            1. HTML Page: 'text/html'
            2. PDF: 'application/pdf'
            3. Image: 'text/html; charset=iso-8859-1'
        """
        content_type = response.headers.get('content-type')
        if 'text/html' in content_type:
            soup = BeautifulSoup(response.text, "html.parser")

            # Getting all the paragraph.
            paragraph_texts = soup.select('p')

            # Getting the title.
            title = get_website_title(soup)

            # Getting the ketword.
            keywords = get_meta_keywords(soup)
            if(keywords == ""):
                keywords = title
            # Getting description.
            description = get_meta_description(soup)
            if(description == ""):
                description = title

            # IMPROVING SERCH RESULT

            description = str(description + " " + keywords + " " + title)

            texts = ""
            for paragraph_text in paragraph_texts:
                texts += paragraph_text.text
            texts = texts.split(" ")

            saturated_text = ""
            for text in texts:
                if(text not in STOP_WORDS):
                    saturated_text += text
                    saturated_text += " "

            # Content
            saturated_text = description + " " + keywords + " " + saturated_text + " " + title
            username = website_url_obj.search_user.user.username

            logger.info("Username: %s", username, extra={'AppName': 'EasySearch'})

            bot_slug = website_url_obj.bot.slug

            logger.info("Website URL: %s", website_url_obj.bot, extra={'AppName': 'EasySearch'})

            logger.info("Bot Slug: %s", bot_slug, extra={'AppName': 'EasySearch'})

            # Create file if not exist
            if not os.path.exists('files/' + str(username)):
                os.makedirs("files/" + str(username))

            # Storing INDEX

            with open("files/" + str(username) + "/indexed-data-" + str(website_url_obj.pk) + ".json", "w") as fp:
                logger.info("file saved", extra={'AppName': 'EasySearch'})
                json.dump({'type': 'html', 'name': str(username), 'bot': bot_slug, 'content': saturated_text, 'url': website_url_obj.link,
                           'title': title, 'url_pk': website_url_obj.pk, 'keywords': keywords, 'description': description}, fp)

            # Getting index data
            read_file = open("files/" + str(username) +
                             "/indexed-data-" + str(website_url_obj.pk) + ".json", 'r')
            data = json.load(read_file)
            logger.info(website_url_obj.pk, extra={'AppName': 'EasySearch'})

            # Doing Indexing in ElasticSearch
            settings.ELASTIC_SEARCH_OBJ.index(
                index="integrated_easysearch", doc_type='search', id=int(website_url_obj.pk), body=data)

        elif 'application/pdf' in content_type:

            logger.info("[PDF] document in %s", website_url_obj.link, extra={'AppName': 'EasySearch'})

            try:
                request_response = requests.get(website_url_obj.link, stream=True)

                logger.info("%s is active url %s",
                            website_url_obj.link, str(request_response.status_code), extra={'AppName': 'EasySearch'})

                username = website_url_obj.search_user.user.username

                if not os.path.exists('documents/' + str(username)):
                    os.makedirs("documents/" + str(username))

                open("documents/" + str(username) + "/document-data-" +
                     str(website_url_obj.pk) + ".pdf", "wb").write(response.content)

                file_text_pdf = ""
                file_name = str("documents/" + str(username) +
                                "/document-data-" + str(website_url_obj.pk) + ".pdf")
                file_text_pdf = str(
                    (textract.process(file_name)).decode('ascii', 'ignore'))

                if not os.path.exists('files/' + str(username)):
                    os.makedirs("files/" + str(username))

                title = ""
                title = website_url_obj.link
                title = title.split("/")[-1]
                title = urllib.request.unquote(title)
                bot_slug = website_url_obj.bot.slug

                file_text_pdf = str(title + " " + file_text_pdf)
                with open("files/" + str(username) + "/document-data-" + str(website_url_obj.pk) + ".json", "w") as fp:
                    json.dump({'type': 'pdf', 'name': str(username), 'bot': bot_slug, 'content': file_text_pdf, 'url': website_url_obj.link,
                               'title': title, 'url_pk': website_url_obj.pk, 'keywords': file_text_pdf, 'description': file_text_pdf}, fp)
                read_file = open(
                    "files/" + str(username) + "/document-data-" + str(website_url_obj.pk) + ".json", 'r')
                data = json.load(read_file)

                settings.ELASTIC_SEARCH_OBJ.index(
                    index="integrated_easysearch", doc_type='search', id=int(website_url_obj.pk), body=data)

            except Exception as es:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("index_website: %s at %s",
                             es, str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})

        website_url_obj.is_indexed = True
        website_url_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("index_website: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})
        website_url_obj.is_indexed = True
        website_url_obj.save()


"""
function: create_websitelink
input params:
            website_url_obj (mandatory)
            parsed_url (mandatory)
            WebsiteLink (mandatory)
"""


def create_websitelink(website_url_obj, parsed_url, WebsiteLink):
    hyper_link = website_url_obj.hyper_text
    user_obj = website_url_obj.search_user
    try:
        WebsiteLink.objects.get(link=str(parsed_url))
    except Exception:
        logger.warning("website matching url doesn't exist. Creating new", extra={'AppName': 'EasySearch'})
        WebsiteLink.objects.create(link=str(parsed_url),
                                   search_user=user_obj,
                                   hyper_text=str(hyper_link),
                                   bot=website_url_obj.bot)


"""
function: EasySearchCrawler

"""


class EasySearchCrawler:

    def __init__(self, start_page):
        self.visited_url = {}
        self.queue_url = [start_page]

    def get_url_list(self, website_url_obj, url, WebsiteLink):
        try:
            domain_name = tldextract.extract(url)
            domain = domain_name.domain
            suffix = domain_name.suffix
            if str(website_url_obj.hyper_text) in url:
                domain = str(domain) + "." + str(suffix)
                if str(domain) in url:
                    try:
                        parsed_html = ""
                        url = url.lower()
                        response = requests.get(url, timeout=10.0)
                        raw_html = response.text
                        parsed_html = html.fromstring(raw_html)
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("EasySearchCrawler: get_url_list: %s at line no %s", str(
                            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})

                    url_title_item = parsed_html.xpath('//title')
                    url_title = '(NO TITLE)'
                    try:
                        url_title = url_title_item[0].text
                    except Exception:
                        url_title = '(ERROR TITLE)'

                    self.visited_url[url] = url_title

                    for a_tag in parsed_html.xpath('//a'):
                        raw_url = a_tag.get('href')
                        if raw_url is None:
                            continue
                        parsed_url = urljoin(url, raw_url)

                        if str(domain) not in parsed_url:
                            continue

                        if parsed_url not in list(self.visited_url.keys()) and parsed_url not in self.queue_url:
                            if str(website_url_obj.hyper_text) in url:
                                if str(domain) in url:
                                    self.queue_url.append(parsed_url)
                                    create_websitelink(
                                        website_url_obj, parsed_url, WebsiteLink)
                else:
                    logger.info("Ignoring this url: %s ", url, extra={'AppName': 'EasySearch'})
            else:
                logger.info("Ignoring this url: %s ", website_url_obj.hyper_text, extra={'AppName': 'EasySearch'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("get_url_list: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})

    def start_crawler(self, website_url_obj, index_level, WebsiteLink):
        try:
            while index_level != 0:
                this_url = self.queue_url[0]
                self.get_url_list(website_url_obj, this_url, WebsiteLink)

                if len(self.queue_url) == 1:
                    break
                else:
                    self.queue_url = self.queue_url[1:]
                index_level -= 1

            logger.info("Crwaling is completed.", extra={'AppName': 'EasySearch'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("start_crawler: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})


"""
function: crawl_weblink
input params:
            website_url_obj (mandatory)
            WebsiteLink(mandatory)
            SearchUser(mandatory)

"""


def crawl_weblink(website_url_obj, WebsiteLink, SearchUser):
    try:
        crawl_obj = EasySearchCrawler(website_url_obj.link)
        crawl_obj.start_crawler(
            website_url_obj, website_url_obj.index_level, WebsiteLink)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("crawl_weblink: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'EasySearch'})
