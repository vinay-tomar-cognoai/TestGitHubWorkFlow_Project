# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django App
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings

# Libraries
from elasticsearch import Elasticsearch
import threading

# Apps modules
from EasySearchApp.constants import *
from EasySearchApp.utils import *
from EasyChatApp.models import *

# Logger
import logging
logger = logging.getLogger(__name__)

"""
    User Module
"""


class SearchUser(models.Model):

    user = models.OneToOneField(
        'EasyChatApp.User', on_delete=models.CASCADE, primary_key=True)

    is_depth_indexing_allowed = models.BooleanField(
        default=True, help_text="Designates whether depth indexing is allowed or not.")

    show_documents = models.BooleanField(
        default=True, help_text="Designates whether documents should be shown in search result or not.")

    spell_checker = models.BooleanField(
        default=True, help_text="Designates whether query entered by user should be corrected or not using spell checker.")

    next_indexing = models.IntegerField(
        default=None, null=True, blank=True, help_text="Number of days after which indexing should be done.")

    is_auto_indexing_allowed = models.BooleanField(
        default=False, help_text="Designates whether auto indexing is allowed or not.")

    logo_file = models.FileField(upload_to="adminLogo/", null=True, blank=True)

    def name(self):
        return self.user.username

    def __str__(self):
        return self.name()

    class Meta:
        verbose_name = 'SearchUser'
        verbose_name_plural = 'SearchUsers'


class EasySearchConfig(models.Model):
    FEATURE_CHOICES = (
        ("1", "Elastic Search"),
        ("2", "Google Search"))

    bot = models.OneToOneField(
        'EasyChatApp.Bot', on_delete=models.CASCADE, null=True, blank=True)

    feature = models.CharField(max_length=1,
                               null=True,
                               blank=True,
                               choices=FEATURE_CHOICES)
    search_cx = models.CharField(max_length=1024, null=True, blank=True,
                                 help_text="Add Search cx id in case if Google Search")

    def __str__(self):
        return self.bot.name

    class Meta:
        verbose_name = 'EasySearchConfig'
        verbose_name_plural = 'EasySearchConfigs'


"""
    Website Link:
        1. link: Store the URL of the website
        2. click_count: Increment click count when user click on a link.
            [FUTURE USE]: It is will use to set the priority of the link on the basis of click count on particular queries
        3. search_user: User who is searching
        4. index_level: Depth of URL tree
        5.hyper_text: URL will be "http" or "https"
"""


class WebsiteLink(models.Model):

    link = models.CharField(max_length=600,
                            null=True,
                            blank=True,
                            help_text="Website link which will be crawled and indexed.")

    bot = models.ForeignKey(
        'EasyChatApp.Bot', on_delete=models.CASCADE, null=True, blank=True, help_text="Selected bot will show the result.")

    click_count = models.IntegerField(
        default=0, help_text="Number of times users clicked on the link.")

    search_user = models.ForeignKey(
        SearchUser, on_delete=models.CASCADE, null=True, blank=True, help_text="Selected user will see the crawled links in EasyChat console and can do searching.")

    index_level = models.IntegerField(null=True, blank=True,
                                      help_text='Indexing will be done till the given depth. Use "-1" for indexing the whole website.')

    hyper_text = models.CharField(max_length=5,
                                  null=True,
                                  blank=True,
                                  choices=HTTP_CHOICES,
                                  help_text="Website with the chooseen hyper text will be crawled")

    last_indexed = models.DateTimeField(
        default=timezone.now, null=True, blank=True, help_text="Date and time when the website is indexed.")

    is_indexed = models.BooleanField(
        default=False, help_text="Designates that website link is indexed in elasticsearch or not.")

    is_crawl = models.BooleanField(
        default=False, help_text="Designates that it should be crawled or not.")

    def __str__(self):
        try:
            return self.link
        except Exception:
            return "Empty links"

    def save(self, *args, **kwargs):
        super(WebsiteLink, self).save(*args, **kwargs)
        logger.info("WebsiteLink has been save successfully", extra={'AppName': 'EasySearch'})

    class Meta:
        verbose_name = 'WebsiteLink'
        verbose_name_plural = 'WebsiteLinks'


"""
    Post Indexing:  After the WebsiteLink model is be saved it will call this function.
    We are using threding here to do INDEXING and CRAWLING side by side.
    The functions is written in "utils.py"
"""


class EasyPDFSearcher(models.Model):
    key = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, help_text='unique PDF key')
    
    name = models.CharField(
        max_length=25, null=False, blank=False, help_text='PDF name')

    file_path = models.TextField(
        default="", null=False, blank=False, help_text='PDF file path')

    important_pages = models.TextField(
        default="", null=True, blank=True, help_text="Important pages of pdf")

    skipped_pages = models.TextField(
        default="", null=True, blank=True, help_text="Pages to skip while performing elastic search in pdf")

    status = models.CharField(
        max_length=20, choices=PDF_SEARCH_STATUS_CHOICES)

    bot_obj = models.ForeignKey(
        'EasyChatApp.Bot', null=True, blank=True, on_delete=models.SET_NULL)

    created_datetime = models.DateTimeField(default=timezone.now)

    last_indexed_datetime = models.DateTimeField(null=True, blank=True)

    is_deleted = models.BooleanField(default=False)

    deleted_datetime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "EasyPDFSearcher"
        verbose_name_plural = "EasyPDFSearcher"


class EasyPDFSearcherAnalytics(models.Model):
    pdf_searcher = models.ForeignKey(
        'EasyPDFSearcher', null=True, blank=True, on_delete=models.SET_NULL)

    click_count = models.IntegerField(
        null=True, default=0, blank=True, help_text="The number of times a document was clicked by end user")

    search_count = models.IntegerField(
        null=True, default=0, blank=True, help_text="The number of times a document was part of the Bot response")
    
    def open_rate(self):
        try:
            if self.search_count == 0:
                return 0
            pdf_open_rate = (self.click_count / self.search_count) * 100
            pdf_open_rate = round(pdf_open_rate, 2)
            return pdf_open_rate
        except Exception:
            return 0
    
    def __str__(self):
        if self.pdf_searcher:
            return self.pdf_searcher

        return "Deleted PDF Analytics"

    class Meta:
        verbose_name = "EasyPDFSearcherAnalytics"
        verbose_name_plural = "EasyPDFSearcherAnalytics"


class PDFSearchExportRequest(models.Model):
    email_id = models.CharField(
        max_length=500, null=False, blank=False, help_text='Email address to send report')

    start_date = models.DateField(default=timezone.now)

    end_date = models.DateField(default=timezone.now)

    user = models.ForeignKey(
        'EasyChatApp.User', null=False, blank=False, on_delete=models.CASCADE)

    bot = models.ForeignKey(
        'EasyChatApp.Bot', null=True, blank=False, on_delete=models.SET_NULL)

    is_completed = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return self.email_id

    class Meta:
        verbose_name = 'PDFSearchExportRequest'
        verbose_name_plural = 'PDFSearchExportRequests'


class PDFSearchIndexStat(models.Model):

    bot = models.ForeignKey(
        'EasyChatApp.Bot', null=True, blank=False, on_delete=models.SET_NULL)

    is_indexing_required = models.BooleanField(default=False)

    is_indexing_in_progress = models.BooleanField(default=False)

    start_datetime = models.DateTimeField(
        null=True, blank=True, help_text='datetime when elastic search indexing start')

    def __str__(self):
        return str(self.bot.name)

    class Meta:
        verbose_name = 'PDFSearchIndexStat'
        verbose_name_plural = 'PDFSearchIndexStats'
