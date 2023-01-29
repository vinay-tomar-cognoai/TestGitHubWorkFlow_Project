from django.db import models
from django.db.models import Q, Count
from django.utils import timezone
from django.conf import settings
# from django.contrib.auth.models import AbstractUser
# from django.db.models.signals import post_save
# from django.dispatch import receiver

from EasyAssistApp.models import *
from EasyChatApp.models import User, UserSession

from EasyAssistSalesforceApp.encrypt import CustomEncrypt


# Create your models here.
import json
import uuid
import logging
import hashlib
import datetime

logger = logging.getLogger(__name__)


class SalesforceAgent(models.Model):

    email = models.CharField(
        max_length=1000, null=False, blank=False, help_text="email id of the salesforce user")

    user_id = models.CharField(
        max_length=500, default="", null=False, blank=False, help_text="user id of the salesforce user")
    
    web_tab_name = models.CharField(
        max_length=500, default="Cobrowsing", null=False, blank=False, help_text="tab name of web tab for the salesforce user")

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'SalesforceAgent'
        verbose_name_plural = 'SalesforceAgent'


class SalesforceNotificationManager(models.Model):

    client_id = models.CharField(
        max_length=500, null=False, blank=False, help_text="client_id of salesforce connected app")

    client_secret = models.CharField(
        max_length=500, null=False, blank=False, help_text="client_secret of salesforce connected app")

    username = models.CharField(
        max_length=500, null=False, blank=False, help_text="username of the salesforce user")

    password = models.CharField(
        max_length=500, null=False, blank=False, help_text="password + security token of the salesforce user")

    access_token = models.ForeignKey(
        'EasyAssistApp.CobrowseAccessToken', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'SalesforceNotificationManager'
        verbose_name_plural = 'SalesforceNotificationManager'
