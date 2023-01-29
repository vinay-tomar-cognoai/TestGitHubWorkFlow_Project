from django.test import TestCase
from EasyChatApp.models import Tree, Processor
from EasyChatApp.utils_api_integration import *
from EasyChatApp.utils import logger
import sys


class ApiIntegration(TestCase):

    def test_get_json_tree(self):
        beginning = Tree.objects.create(name="test")
        processor = Processor.objects.create(
            name="test_processor", function="def f(x):\n    return x")
        beginning.post_processor = processor
        beginning.post_processor.post_processor_direct_value = "test_variable"
        selecthtml = ""
        if beginning.post_processor.post_processor_direct_value != None:
            select_html = '<option value="' + beginning.post_processor.post_processor_direct_value + \
                '">{/' + beginning.post_processor.post_processor_direct_value + '/}</option>'
            while len(beginning.children.all()) != 0:
                try:
                    if beginning.children.all()[0].post_processor != None:
                        if beginning.children.all()[0].post_processor.post_processor_direct_value != None:
                            select_html = selecthtml + '<option value="' + beginning.children.all()[0].post_processor.post_processor_direct_value + '">{/' + beginning.children.all()[
                                0].post_processor.post_processor_direct_value + '/}</option>'

                    beginning = beginning.children.all()[0]

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    logger.error("RequestResponseTree ! %s %s",
                                 str(e), str(exc_tb.tb_lineno))
                    break

        # test for normal dictionary
        test_input_plain_dictionary = {"key1": "value1", "key2": "value2"}
        expected_output = '<ul id="myUL1"><li><span class="caret">key1</span><select name="key1" id= "key1jpd" ><option value="defaultallincallvaluevalue1" class="tree">value1</option><option value="test_variable">{/test_variable/}</option></select></li><li><span class="caret">key2</span><select name="key2" id= "key2jpd" ><option value="defaultallincallvaluevalue2" class="tree">value2</option><option value="test_variable">{/test_variable/}</option></select></li></ul>'
        correct_output = json_parser(
            test_input_plain_dictionary, '<ul id="myUL1">', select_html)
        self.assertEqual(expected_output, correct_output)

        # test for nested dictionary
        test_input_nested_dictionary = {"key1": {"key2": "value"}}
        expected_output = '<ul id="myUL1"><li><span class="caret">key1</span><ul class="nested"><li><span class="caret">key2</span><select name="key2" id= "key2jpd" ><option value="defaultallincallvaluevalue" class="tree">value</option><option value="test_variable">{/test_variable/}</option></select></li></ul></ul>'
        correct_output = json_parser(
            test_input_nested_dictionary, '<ul id="myUL1">', select_html)
        self.assertEqual(expected_output, correct_output)

        # test for nested dictionary with list
        test_input_nested_dictionary_list = {"key1": [{"key2": "value"}]}
        expected_output = '<ul id="myUL1"><li><span class="caret">key1</span><ul class="nested"><li><span class="caret">key2</span><select name="key2" id= "key2jpd" ><option value="defaultallincallvaluevalue" class="tree">value</option><option value="test_variable">{/test_variable/}</option></select></li></ul>'
        correct_output = json_parser(
            test_input_nested_dictionary_list, '<ul id="myUL1">', select_html)
        self.assertEqual(expected_output, correct_output)

    def test_get_response_tree(self):
        beginning = Tree.objects.create(name="test")
        processor = Processor.objects.create(
            name="test_processor", function="def f(x):\n    return x")
        beginning.post_processor = processor
        beginning.post_processor.post_processor_direct_value = "test_variable"
        # selecthtml = ""
        # if beginning.post_processor.post_processor_direct_value != None:
        #     select_html = '<option value="' + beginning.post_processor.post_processor_direct_value + \
        #         '">{/' + beginning.post_processor.post_processor_direct_value + '/}</option>'
        #     while len(beginning.children.all()) != 0:
        #         try:
        #             if beginning.children.all()[0].post_processor != None:
        #                 if beginning.children.all()[0].post_processor.post_processor_direct_value != None:
        #                     select_html = selecthtml + '<option value="' + beginning.children.all()[0].post_processor.post_processor_direct_value + '">{/' + beginning.children.all()[
        #                         0].post_processor.post_processor_direct_value + '/}</option>'

        #             beginning = beginning.children.all()[0]

        #         except Exception as e:
        #             exc_type, exc_obj, exc_tb = sys.exc_info()
        #             logger.error("RequestResponseTree ! %s %s",
        #                          str(e), str(exc_tb.tb_lineno))
        #             break
        # test for normal dictionary
        test_input_plain_dictionary = {"key1": "value1", "key2": "value2"}
        expected_output = '<ul id="myUL"><li><span class="caret"><input type="text" name="key1" id= "key1" value="key1"></span>value1</li><li><span class="caret"><input type="text" name="key2" id= "key2" value="key2"></span>value2</li></ul>'
        correct_output = response_parser(
            test_input_plain_dictionary, '<ul id="myUL">')
        self.assertEqual(expected_output, correct_output)

        # test for nested dictionary
        test_input_nested_dictionary = {"key1": {"key2": "value"}}
        expected_output = '<ul id="myUL"><li><span class="caret"><input type="text" name="key1" id= "key1" value="key1"></span><ul class="nested"><li><span class="caret"><input type="text" name="key2" id= "key2" value="key2"></span>value</li></ul></ul>'
        correct_output = response_parser(
            test_input_nested_dictionary, '<ul id="myUL">')
        self.assertEqual(expected_output, correct_output)

        # test for nested dictionary with list
        test_input_nested_dictionary_list = {"key1": [{"key2": "value"}]}
        expected_output = '<ul id="myUL"><li><span class="caret"><input type="text" name="key1" id= "key1" value="key1"></span><ul class="nested"><li><span class="caret"><input type="text" name="key2" id= "key2" value="key2"></span>value</li></ul>'
        correct_output = response_parser(
            test_input_nested_dictionary_list, '<ul id="myUL">')
        self.assertEqual(expected_output, correct_output)

    def test_json_key(self):
        # test for normal dictionary
        test_input_plain_dictionary = {"key1": "value1", "key2": "value2"}
        request_data = {'key1': 'test_variable',
                        'key2': 'defaultallincallvaluevalue2'}
        json_key(test_input_plain_dictionary, request_data)
        correct_output = test_input_plain_dictionary
        expected_output = {'key1': '{/test_variable/}', 'key2': 'value2'}
        self.assertEqual(expected_output, correct_output)

        # test for nested dictionary
        test_input_nested_dictionary = {"key1": {"key2": "value"}}
        request_data = {'key2': 'test_variable'}
        json_key(test_input_nested_dictionary, request_data)
        correct_output = test_input_nested_dictionary
        expected_output = {'key1': {'key2': '{/test_variable/}'}}
        self.assertEqual(expected_output, correct_output)

        # test for nested dictionary with list
        test_input_nested_dictionary_list = {"key1": [{"key2": "value"}]}
        request_data = {'key2': 'test_variable'}
        json_key(test_input_nested_dictionary_list, request_data)
        correct_output = test_input_nested_dictionary_list
        expected_output = {'key1': [{'key2': '{/test_variable/}'}]}
        self.assertEqual(expected_output, correct_output)

    def test_json_key_response(self):
        # test for normal dictionary
        test_input_response_plain_dictionary = {
            "key1": "value1", "key2": "value2"}
        response_data = {'': 'wQeYZdzasRmbmZrqMMLcqLaSy5oojSU3P471VjWtgkVP0XX5DHocCiWTUYuKaoyX', 'global_search': '',
                         'key1': 'key1_value_changed', 'key2': 'key2', 'input_upload_feedback_screenshot': '', 'input_upload_feedback_screenshot2': ''}
        correct_parsed_response_dictionary = {}
        json_key_response(test_input_response_plain_dictionary,
                          response_data, correct_parsed_response_dictionary)
        expected_parsed_response_dictionary = {
            'key1_value_changed': "['key1']", 'key2': "['key2']"}
        self.assertEqual(correct_parsed_response_dictionary,
                         expected_parsed_response_dictionary)

        # test for nested dictionary
        test_input_nested_dictionary = {"key1": {"key2": "value"}}
        response_data = {'': '4zqr7eP0sS2muGFhzd4RHQBSCJK9NVo8nNju3kcjglB08EbWq8HRTnnTYCQvEr22', 'global_search': '',
                         'key1': 'key1', 'key2': 'key2', 'input_upload_feedback_screenshot': '', 'input_upload_feedback_screenshot2': ''}
        correct_parsed_response_dictionary = {}
        json_key_response(test_input_nested_dictionary,
                          response_data, correct_parsed_response_dictionary)
        expected_parsed_response_dictionary = {
            'key1': "['key1']", 'key2': "['key1']['key2']"}
        self.assertEqual(correct_parsed_response_dictionary,
                         expected_parsed_response_dictionary)

        # test for nested dictionary with list
        test_input_nested_dictionary_list = {"key1": [{"key2": "value"}]}
        response_data = {'': 'zVDoJRNLr7IpxCo7ucIkbR2cbCHxgdAZS9wrFXa4fAh3bAUMl7lknoOdxvNT7JeT', 'global_search': '',
                         'key1': 'key1_changed', 'key2': 'key2_changed', 'input_upload_feedback_screenshot': '', 'input_upload_feedback_screenshot2': ''}
        correct_parsed_response_dictionary = {}
        json_key_response(test_input_nested_dictionary_list,
                          response_data, correct_parsed_response_dictionary)
        expected_parsed_response_dictionary = {
            'key1_changed': "['key1']", 'key2_changed': "['key1'][0]['key2']"}
        self.assertEqual(correct_parsed_response_dictionary,
                         expected_parsed_response_dictionary)
