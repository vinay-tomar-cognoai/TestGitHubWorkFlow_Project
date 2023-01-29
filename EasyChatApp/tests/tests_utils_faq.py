# -*- coding: utf-8 -*-

from EasyChatApp.utils import ensure_element_tree
from django.test import TestCase

from EasyChatApp.utils_faq import write_excel, extract_faqs
from EasyChatApp.models import User, Bot
import xlrd
import logging
logger = logging.getLogger(__name__)


"""
Test of all functions which are in utils_alexa.py 
"""


class EasyChatAppUtilsFAQS(TestCase):

    def setUp(self):
        logger.info(
            "Setting up the test environment for EasyChatAppUtilsFAQS...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    """
    function tested: write_excel
    input params:
        questions: list of questions
        answers: list answers corresponding to qustion list
    saves excel containing qustion & answers pair 
    """

    def test_write_excel(self):

        logger.info("Testing write_excel is going on...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting write_excel is going on...\n")

        questions = ["hi", "bye", "testing"]
        answers = ["hello, how may I assist you?",
                   "Thanks for using, hoping to see you again.", "okay, I can wait."]
        corrected_questions_list = []
        corrected_answers_list = []

        write_excel(questions, answers)

        ensure_element_tree(xlrd)
        
        automated_flow_create_wb = xlrd.open_workbook("files/FAQs.xls")
        excel_flows = automated_flow_create_wb.sheet_by_index(0)
        rows_limit = excel_flows.nrows
        # cols_limit = excel_flows.ncols

        row_count = 1

        for row in range(rows_limit - 1):
            corrected_questions_list.append(
                excel_flows.cell_value(row_count, 0))
            corrected_answers_list.append(excel_flows.cell_value(row_count, 2))
            row_count += 1

        self.assertEqual(questions, corrected_questions_list)
        self.assertEqual(answers, corrected_answers_list)

    """
    function tested: extract_faqs
    input params:
        url_html:url/html from which FAQs to be extracted

    returns json containing question answer pair
    """

    def test_extract_faqs(self):
        user_obj = User.objects.create(username="temporary", password="temporary")
        bot_obj = Bot.objects.create(
            name="testbot", slug="testbot", bot_display_name="testbot", bot_type="2")
        logger.info("Testing write_excel is going on...", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        print("\nTesting write_excel is going on...\n")

        url_html = "https://retail.onlinesbi.com/personal/faq.html"

        try:
            extract_faqs(url_html, user_obj, bot_obj)
        except Exception:
            print("Extract FAQS failed")
            assert 1 == 2
