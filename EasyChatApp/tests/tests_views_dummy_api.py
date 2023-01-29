from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from rest_framework.test import APIClient
from EasyChatApp.models import Bot, User, MISDashboard, Profile, Feedback, Channel, Tree, Intent, Config, BotResponse, BotChannel, EasyChatQueryToken
from LiveChatApp.models import LiveChatUser, LiveChatCustomer, CannedResponse, LiveChatConfig
from LiveChatApp.utils import get_time, is_agent_live
from EasyChatApp.utils_custom_encryption import *
import requests
import logging
import json
import random
import execjs
import base64
from datetime import datetime
from Crypto import Random
from Crypto.Cipher import AES
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

"""
Test of dummy apis
"""


class DummyAPI(TestCase):

    def test_ValuationAPI(self):
        header = {
            "Content-Type": "application/json"
        }
        client_instance = Client()
        request = client_instance.post(
            "/chat/fetch-valuation/", {"valuation_id": "10058816"}, follow=True, **header)
        response = request.data
        self.assertEqual(response['status'], '200')

        header = {
            "Content-Type": "application/json"
        }
        request = client_instance.post(
            "/chat/fetch-valuation/", {"valuation_id": "12349000"}, follow=True, **header)
        response = request.data
        self.assertEqual(response['status'], '500')

    def test_BalanceAPI(self):
        header = {
            "Authorization": "Bearer GObtAZ7KFKUHoMv5Sp7mQxTb8MhSzB9iEKJEigqhuIgtT",
            "Content-Type": "application/json"
        }
        client_instance = Client()
        request = client_instance.post(
            "/chat/fetch-balance/", {"MobNb": "7905358546"}, **header)
        response = request.data
        self.assertEqual(response['status'], '200')

        header = {
            "Content-Type": "application/json"
        }
        client_instance = Client()
        request = client_instance.post(
            "/chat/fetch-balance/", {"MobNb": "7905358546"}, **header)
        response = request.data
        self.assertEqual(response['status'], '200')

        header = {
            "Content-Type": "application/json"
        }
        client_instance = Client()
        request = client_instance.post(
            "/chat/fetch-balance/", {"MobNb": "9920262298"}, **header)
        response = request.data
        self.assertEqual(response['status'], '500')
