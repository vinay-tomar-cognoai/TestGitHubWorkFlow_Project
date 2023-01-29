
import re
import sys
import os
import json
import logging
import pytz
from xlwt import Workbook
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from EasyChatApp.models import *
from EasyChatApp.utils_execute_query import identify_intent_tree
from EasyChat.settings import EASYCHAT_HOST_URL
from DeveloperConsoleApp.utils import get_developer_console_settings, send_email_to_customer_via_awsses

logger = logging.getLogger(__name__)


def delete_test_result_objs_till_now(progress_obj):
    try:
        logger.info("Deleting Test result objects for Automation testing", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        test_result_objs_till_now = AutomatedTestResult.objects.filter(
            automated_test_progress_obj=progress_obj)

        test_result_objs_till_now.delete()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("delete_intent %s in line no %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_identified_intent_objs(suggestion_list):

    identified_intent_objs = Intent.objects.none()

    try:
        for identified_intent in suggestion_list:
            identified_intent_pk = identified_intent["id"]

            intent_obj = Intent.objects.filter(pk=int(identified_intent_pk))
            identified_intent_objs = identified_intent_objs.union(intent_obj)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_identified_intent_objs %s in line no %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return identified_intent_objs


def create_automated_test_result_objs(query_sentence, status, cause, original_intent_obj, identified_intent_objs, progress_obj):
    automated_test_result_obj = None
    try:
        automated_test_result_obj = AutomatedTestResult.objects.create(
            automated_test_progress_obj=progress_obj, query_sentence=query_sentence, status=status, cause=cause, original_intent=original_intent_obj)

        if identified_intent_objs.exists():
            automated_test_result_obj.identified_intents.add(
                *identified_intent_objs)
            automated_test_result_obj.save()
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_automated_test_result_objs %s in line no %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return automated_test_result_obj


def get_total_intent_sentence_based_on_percentage(bot_obj, percentage_of_intents):
    total_sentences = 0
    try:

        intent_objs = get_intent_objs_based_on_percentage(
            0, percentage_of_intents, [bot_obj])

        for intent_obj in intent_objs:
            training_data_dict = json.loads(intent_obj.training_data)
            total_sentences += len(training_data_dict.keys())

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_total_intent_sentence_based_on_percentage %s in line no %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return total_sentences


def get_parsed_automated_test_result_data(test_result_objs):
    result_objs_list = []
    try:
        for test_result_obj in test_result_objs:

            test_result_data = {
                "query_sentence": test_result_obj.query_sentence,
                "original_intent_pk": test_result_obj.original_intent.pk,
                "original_intent_name": test_result_obj.original_intent.name,
                "cause": test_result_obj.cause,
                "status": test_result_obj.status,
                "identified_intent_name_list": test_result_obj.get_identified_intent_name_list(),
                "identified_intent_pk_list": test_result_obj.get_identified_intent_pk_list(),
                "test_result_obj_pk": test_result_obj.pk,
            }
            test_result_obj.is_processed = True
            test_result_obj.save()
            result_objs_list.append(test_result_data)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_parsed_automated_test_result_data %s in line no %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return result_objs_list


def get_single_intent_test_details_list(intent_obj, bot_obj, profile_obj):

    test_result_list = []
    total_test_case_passed = 0
    try:

        training_data_dict = json.loads(intent_obj.training_data)
        original_intent_pk = intent_obj.pk

        for data_key in training_data_dict.keys():

            sentence = training_data_dict[data_key]

            status, cause, identified_intent_obj = return_single_sentence_test_details(
                intent_obj, sentence, bot_obj, profile_obj)
            identified_intent_name_list = []
            identified_intent_pk_list = []

            if status == "Pass":
                total_test_case_passed += 1

            for intent in identified_intent_obj:
                identified_intent_name_list.append(intent.name)
                identified_intent_pk_list.append(intent.pk)

            test_result_dict = {
                "query_sentence": sentence,
                "status": status,
                "cause": cause,
                "identified_intent_name_list": identified_intent_name_list,
                "identified_intent_pk_list": identified_intent_pk_list,
                "original_intent_pk": original_intent_pk,
                "original_intent_name": intent_obj.name,

            }

            test_result_list.append(test_result_dict)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("return_single_intent_test_details %s in line no %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return test_result_list, total_test_case_passed


def return_single_sentence_test_details(intent_obj, sentence, bot_obj, profile_obj):
    try:
        status = "Pass"
        cause = "Valid intent identified."
        identified_intent_obj = Intent.objects.none()
        original_intent_pk = intent_obj.pk

        if intent_obj.is_authentication_required:
            cause = cause + "<br> Note: This Intent requires authentication and it is assumed that user is authenticated."

            authetication_type = intent_obj.auth_type.name
            authentication_obj = Authentication.objects.filter(
                name=authetication_type).order_by('-pk')[0]

            user_authentication_obj = UserAuthentication.objects.filter(
                user=profile_obj, auth_type=authentication_obj).first()

            if not user_authentication_obj:
                user_authentication_obj = UserAuthentication.objects.create(
                    user=profile_obj, auth_type=authentication_obj)
            else:
                tz = pytz.timezone(settings.TIME_ZONE)
                current_datetime_obj = timezone.now().astimezone(tz)
                user_authentication_obj.start_time = current_datetime_obj
                user_authentication_obj.save()

        identified_tree_obj, suggestion_list, _, __ = identify_intent_tree(
            profile_obj, bot_obj, sentence, "Web", "en", None, "", [], None)

        # Checking if exiting intent came into suggestions or not?

        if identified_tree_obj != None:
            identified_intent_obj = Intent.objects.filter(
                tree=identified_tree_obj)

        if identified_intent_obj.exists():
            if original_intent_pk != identified_intent_obj.first().pk:
                status = "Fail"
                cause = "Invalid intent is identified."

        else:
            if len(suggestion_list) == 0:
                status = "Fail"
                cause = "Intent identified is None."
            else:
                status = "Fail"
                cause = "Conflict in intent identification."
                identified_intent_obj = get_identified_intent_objs(
                    suggestion_list)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("return_single_intent_test_details %s in line no %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return status, cause, identified_intent_obj


def perform_automated_testing_on_given_intent_objs(intent_objs, bot_obj, profile_obj, progress_obj, user_obj):
    try:

        test_cases_processed = 0
        test_cases_passed = 0

        for intent_obj in intent_objs:

            training_data_dict = json.loads(intent_obj.training_data)

            temp_progress_obj = AutomatedTestProgress.objects.get(
                user=user_obj, bot=bot_obj)
            # this is for checking if testing is stooped in between or not
            if temp_progress_obj.is_testing_stopped_in_between:
                return
            logger.info("performing automated testing for intent " + str(intent_obj.name), extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})
            for data_key in training_data_dict.keys():

                sentence = training_data_dict[data_key]

                status, cause, identified_intent_obj = return_single_sentence_test_details(
                    intent_obj, sentence, bot_obj, profile_obj)

                create_automated_test_result_objs(
                    sentence, status, cause, intent_obj, identified_intent_obj, progress_obj)

                test_cases_processed += 1

                if status == "Pass":
                    test_cases_passed += 1

        progress_obj.last_tested_on = datetime.datetime.now()
        progress_obj.test_cases_passed = test_cases_passed
        progress_obj.test_cases_processed = str(test_cases_processed)
        progress_obj.is_automated_testing_completed = True
        progress_obj.save()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("perform_automated_testing_on_given_intent_objs %s in line no %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def add_heading_for_automated_excel():

    automated_testing_wb = Workbook()

    sheet1 = automated_testing_wb.add_sheet("Automated Testing Result")

    sheet1.write(0, 0, "Query")
    sheet1.col(0).width = 256 * 40

    sheet1.write(0, 1, "Ideal Intent Name")
    sheet1.col(1).width = 256 * 30

    sheet1.write(0, 2, "Identified Intent Name")
    sheet1.col(2).width = 256 * 30

    sheet1.write(0, 3, "Cause")
    sheet1.col(3).width = 256 * 30

    sheet1.write(0, 4, "Status")
    sheet1.col(4).width = 256 * 15

    sheet1.write(0, 5, "Total sentences")
    sheet1.col(5).width = 256 * 15

    sheet1.write(0, 6, "Correct sentences")
    sheet1.col(6).width = 256 * 17

    sheet1.write(0, 7, "Bot ID")
    sheet1.col(7).width = 256 * 15

    sheet1.write(0, 8, "Bot Name")
    sheet1.col(8).width = 256 * 15

    sheet1.write(0, 9, "Date of Test")
    sheet1.col(9).width = 256 * 25

    return sheet1, automated_testing_wb


def create_excel_for_automated_testing(bot_obj, username, progress_obj):
    filename_customer = ""
    try:
        import datetime
        sheet1, automated_testing_wb = add_heading_for_automated_excel()
        row_number = 1

        failed_test_result_objs = AutomatedTestResult.objects.filter(
            automated_test_progress_obj=progress_obj, status="Fail")

        passed_test_result_objs = AutomatedTestResult.objects.filter(
            automated_test_progress_obj=progress_obj, status="Pass")

        for test_result in failed_test_result_objs.union(passed_test_result_objs):

            sheet1.write(row_number, 0, test_result.query_sentence)

            sheet1.write(row_number, 1, test_result.original_intent.name)
            sheet1.write(
                row_number, 2, test_result.get_identified_intent_name_list())
            sheet1.write(row_number, 3, test_result.cause)
            sheet1.write(row_number, 4, test_result.status)

            row_number += 1

        correct_sentences = passed_test_result_objs.count()
        incorrect_senteces = failed_test_result_objs.count()

        total_sentences = correct_sentences + incorrect_senteces

        sheet1.write(1, 5, str(total_sentences))
        sheet1.write(1, 6, str(str(correct_sentences)))
        sheet1.write(1, 7, str(bot_obj.pk))
        sheet1.write(1, 8, str(bot_obj.name))

        filename_customer = "AutomatedTesting_Export" + \
            str(username) + "_" + str(bot_obj.pk) + "_" + \
            datetime.datetime.now().strftime("%d-%m-%Y") + ".xls"

        sheet1.write(
            1, 9, str(datetime.datetime.now().strftime("%d-%B-%Y %H:%M")))

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/automated_testing/' + str(bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        automated_testing_wb.save(secured_files_path + filename_customer)

        path = '/secured_files/EasyChatApp/automated_testing/' + str(bot_obj.pk) + '/' + filename_customer

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=bot_obj)
        
        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'
        
        progress_obj.is_excel_created = True
        progress_obj.save()

        logger.info("Excel file for internal use has been created Successfully.", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in create_excel_for_automated_testing %s in line no %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return file_url


def check_if_valid_percentage_value(number):

    return isinstance(number, int) and number >= 0 and number <= 100


def get_intent_objs_based_on_percentage(start_percentage, end_percentage, bot_objs):

    intent_objs = Intent.objects.filter(
        bots__in=bot_objs, is_deleted=False, is_hidden=False).distinct().order_by("-last_modified", "-pk")
    try:
        if check_if_valid_percentage_value(start_percentage) and check_if_valid_percentage_value(end_percentage):

            total_intents = intent_objs.count()

            start_value = round((start_percentage * total_intents) / 100)

            end_value = round((end_percentage * total_intents) / 100)

            intent_objs = intent_objs[start_value:end_value]

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in create_excel_for_automated_testing %s in line no %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return intent_objs


def perform_automated_testing(user_obj, bot_obj, percentage_of_intents):

    try:

        bot_objs = [bot_obj]

        intent_objs = get_intent_objs_based_on_percentage(
            0, percentage_of_intents, bot_objs)
        # this function return the particular percentage of intent objs  of the given bots
        # for eg to get top 30 % pass , 0 , 30 and bot_objs to get intents from 30 to 60 % pass 30 and 60

        profile_user_id = "FAQAutomatedTestingUser|" + \
            str(user_obj.username) + "|" + str(bot_obj.pk)
        profile_obj = Profile.objects.create(
            user_id=profile_user_id, bot=bot_obj)

        try:
            progress_obj = AutomatedTestProgress.objects.get(
                user=user_obj, bot=bot_obj)
        except Exception:
            logger.warning("creating AutomatedTestProgress object", extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                           'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            progress_obj = AutomatedTestProgress.objects.create(
                user=user_obj, bot=bot_obj)

        perform_automated_testing_on_given_intent_objs(
            intent_objs, bot_obj, profile_obj, progress_obj, user_obj)

    except Exception as e:  # noqa: F841

        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("perform_automated_testing %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def create_and_send_automated_testing_report_mail(bot_obj, username, progress_obj, email_id):
    try:

        file_src = create_excel_for_automated_testing(
            bot_obj, username, progress_obj)

        send_mail_of_automated_testing_report(
            "Automated Testing Report", file_src, email_id)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("perform_automated_testing %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_mail_of_automated_testing_report(to_send_in_message, file_src, to_email):
    try:

        body = """
                   <head>
                      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                      <title>Cogno AI</title>
                      <style type="text/css" media="screen">
                      </style>
                    </head>
                    <body>

                    <div style="padding:1em;border:0.1em black solid;" class="container">
                        <p>
                            Dear User,
                        </p>
                        <p>
                            We have received a request to provide you with the {}. Please click on the link below to download the file.
                        </p>
                        <a href="{}">click here</a>
                        <p>&nbsp;</p>"""

        config = get_developer_console_settings()

        body += config.custom_report_template_signature

        body += """</div></body>"""

        body = body.format(to_send_in_message, file_src)

        send_email_to_customer_via_awsses(to_email, to_send_in_message, body)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
