# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.test import TestCase
from EasySearchApp.utils import get_website_title, get_meta_keywords, get_meta_description
import logging
import json
import requests
from bs4 import BeautifulSoup
logger = logging.getLogger(__name__)


"""
Test of All functions which are independent of models 
"""


class UtilsFunctionsWithoutModels(TestCase):

    def setUp(self):
        logger.info(
            "Setting up the test environment for EasySearchApp: UtilsFunctionsWithoutModels...", extra={'AppName': 'EasySearch'})

    """
    function tested: test_title
    input queries:
        query containing html code of webpage
    expected output:
        return webpage title
    checks for:
        same expected output and output from function tested
    """

    # def test_title(self):
    #     url = 'https://allincall.in/'
    #     response = requests.get(url)
    #     input_query = BeautifulSoup(response.text, "html.parser")
    #     expected_responses = "Cogno AI"
    #     corrected = get_website_title(input_query)
    #     self.assertEqual(expected_responses, corrected)

    """
    function tested: test_keywords
    input queries:
        query containing html code of webpage
    expected output:
        return webpage keyword
    checks for:
        same expected output and output from function tested
    """

    def test_keywords(self):
        url = 'https://www.hdfc.com/'
        response = requests.get(url)
        input_query = BeautifulSoup(response.text, "html.parser")
        expected_responses = "housing finance, housing finance companies, housing finance ltd."
        corrected = get_meta_keywords(input_query)
        self.assertEqual(expected_responses, corrected)

    """
    function tested: test_description
    input queries:
        query containing html code of webpage
    expected output:
        return webpage description
    checks for:
        same expected output and output from function tested
    """

    # def test_description(self):
    #     url = 'https://www.hdfccredila.com/'
    #     response = requests.get(url)
    #     input_query = BeautifulSoup(response.text, "html.parser")
    #     expected_responses = "HDFC Credila is India's First Dedicated Education Loan company and a pioneer in the field of education loan. Avail hassle free loans for higher studies with attractive tax benefits under section 80E."
    #     corrected = get_meta_description(input_query)
    #     self.assertEqual(expected_responses, corrected)
