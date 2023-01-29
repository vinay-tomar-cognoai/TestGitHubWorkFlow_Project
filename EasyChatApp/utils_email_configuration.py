from EasyChatApp.utils_validation import EasyChatInputValidation
from EasyChatApp.email_html_constants import *
from EasyChatApp.constants import DEFAULT_NO_OF_DAYS_FOR_DAILY_MAILER_ANALYTICS
from django.conf import settings
import sys
import logging
from sklearn.feature_extraction import text as sklearn_text
import re
from django.db.models import Sum, Q, Count

from DeveloperConsoleApp.utils import send_email_to_customer_via_awsses

import datetime
import time
import math
from urllib.parse import quote
from collections import OrderedDict
from os import path
from orderedset import OrderedSet
logger = logging.getLogger(__name__)

FROM = settings.EMAIL_HOST_USER
PASSWORD = settings.EMAIL_HOST_PASSWORD
host_url = settings.EASYCHAT_HOST_URL


"""
send_mail : Send mail to the given email id.
"""


# def send_mail(FROM, TO, message_as_string, PASSWORD):
#     import smtplib
#     # # The actual sending of the e-mail
#     server = smtplib.SMTP('smtp.gmail.com:587')
#     # Credentials (if needed) for sending the mail
#     password = PASSWORD
#     # Start tls handshaking
#     server.starttls()
#     # Login to server
#     server.login(FROM, password)
#     # Send mail
#     server.sendmail(FROM, TO, message_as_string)
#     # Close session
#     server.quit()


"""
get_bot_analytics : Return a HTML with Bot analytics of selected channels.
"""


def get_bot_analytics(start_date, end_date, channels, form_assist_reqd, bot, analytics_type):

    from EasyChatApp.models import MISDashboard, FormAssistAnalytics
    import datetime
    import pytz
    if analytics_type == "1":
        date = str(start_date.strftime("%d-%B-%Y"))
    elif analytics_type == "2":
        date = str(start_date.strftime("%d-%B-%Y")) + \
            " - " + str(end_date.strftime("%d-%B-%Y"))
    elif analytics_type == "3":
        date = str(start_date.strftime("%d-%B-%Y")) + \
            " - " + str(end_date.strftime("%d-%B-%Y"))
    category_html = ""
    mis_objs_list = MISDashboard.objects.filter(
        creation_date__gte=start_date, creation_date__lt=end_date, bot=bot)

    for channel in channels:
        category_html += EMAIL_CATEGORY_HTML + str(channel) + '</th>'

    category_html += '</tr></thead>'

    category_html += EMAIL_ANALYTICS_BODY

    for channel in channels:
        channel_filter = mis_objs_list.filter(channel_name=channel)
        total_count = channel_filter.count()
        category_html += EMAIL_ANLYTICS_VALUES + \
            str(total_count) + '</span></td>'
    category_html += '</tr>' + EMAIL_ACCURACY_BODY

    validation_obj = EasyChatInputValidation()

    for channel in channels:
        channel_filter = mis_objs_list.filter(channel_name=channel)
        total_count = channel_filter.count()
        unidentified_filter = channel_filter.filter(intent_name=None)
        unidentified_count = 0
        for mis_obj in unidentified_filter:
            if validation_obj.is_valid_query(mis_obj.get_message_received()):
                unidentified_count += 1

        if total_count != 0:
            category_html += EMAIL_ACCURACY_VALUES + \
                str(round((100 * (total_count - unidentified_count)) /
                          total_count, 2)) + '</td>'
        else:
            category_html += EMAIL_ACCURACY_VALUES + 'NA</td>'

    category_html += '</tr>' + EMAIL_IDENTIFIED_BODY

    for channel in channels:
        channel_filter = mis_objs_list.filter(channel_name=channel)
        total_count = channel_filter.count()
        unidentified_filter = channel_filter.filter(intent_name=None)
        unidentified_count = 0
        for mis_obj in unidentified_filter:
            if validation_obj.is_valid_query(mis_obj.get_message_received()):
                unidentified_count += 1

        category_html += EMAIL_IDENTIFIED_VALUES + \
            str(total_count - unidentified_count) + '</td>'
    category_html += '</tr>' + EMAIL_UNIDENTIFIED_BODY

    for channel in channels:
        channel_filter = mis_objs_list.filter(channel_name=channel)
        total_count = channel_filter.count()
        unidentified_filter = channel_filter.filter(intent_name=None)
        unidentified_count = 0
        for mis_obj in unidentified_filter:
            if validation_obj.is_valid_query(mis_obj.get_message_received()):
                unidentified_count += 1

        category_html += EMAIL_UNDENTIFIED_VALUES + \
            str(unidentified_count) + '</td>'

    category_html += '</tr>' + EMAIL_MTD_BODY

    for channel in channels:
        start_date = (datetime.datetime.today() -
                      datetime.timedelta(30)).date()
        end_date = datetime.datetime.today()
        mis_objs_list = MISDashboard.objects.filter(
            creation_date__gte=start_date, creation_date__lt=end_date, bot=bot)
        channel_filter = mis_objs_list.filter(channel_name=channel)
        category_html += EMAIL_UNDENTIFIED_VALUES + \
            str(len(list(set(list(channel_filter.values_list("user_id")))))) + '</td>'

    category_html += '</tr>' + EMAIL_YTD_BODY

    for channel in channels:
        start_date = bot.go_live_date
        end_date = datetime.datetime.today()
        mis_objs_list = MISDashboard.objects.filter(
            creation_date__gte=start_date, creation_date__lt=end_date, bot=bot)
        channel_filter = mis_objs_list.filter(channel_name=channel)
        category_html += EMAIL_UNDENTIFIED_VALUES + \
            str(len(list(set(list(channel_filter.values_list("user_id")))))) + '</td>'

    if form_assist_reqd:
        category_html += '</tr>' + EMAIL_FORM_BODY
    else:
        category_html += '</tr>'

    if form_assist_reqd:
        form_assist_filter = FormAssistAnalytics.objects.all()
        total_form_assist_queries = form_assist_filter.count()
        users_assisted_via_form_assist = len(
            list(set(list(form_assist_filter.values_list("user_id")))))
        category_html += EMAIL_UNDENTIFIED_VALUES + \
            str(str(total_form_assist_queries)) + '</td>'
        category_html += '</tr>' + EMAIL_FORM_UNIQUE_BODY
        category_html += EMAIL_UNDENTIFIED_VALUES + \
            str(str(users_assisted_via_form_assist)) + '</td>'
        category_html += '</td>'
    category_html += '</tr>'
    return date, category_html


def get_flow_analytics(channel_list, bot_obj, analytics_type):
    from EasyChatApp.models import Intent, FlowAnalytics, Channel, DailyFlowAnalytics
    import datetime
    email_html = ""
    try:
        email_flow_analytics_header = FLOW_ANALYTICS_HEADER
        email_html += email_flow_analytics_header
        intent_list = Intent.objects.filter(
            bots__in=[bot_obj], is_deleted=False)
        if analytics_type == "1":
            for channel in channel_list:
                for intent in intent_list:
                    if intent.tree.children.count():
                        intent_obj = FlowAnalytics.objects.filter(
                            intent_indentifed=intent, current_tree=intent.tree, previous_tree=intent.tree, channel=Channel.objects.get(name=channel))
                        email_html += '<tr>' + FLOW_ANALYTICS_ROW + intent.name + '</td>'
                        email_html += FLOW_ANALYTICS_ROW + '<span>' + \
                            str(intent_obj.count()) + '</span></td>'
                        email_html += FLOW_ANALYTICS_ROW + '<span>' + str(FlowAnalytics.objects.filter(
                            intent_indentifed=intent, is_last_tree_child=True, channel=Channel.objects.get(name=channel)).count()) + '</span></td>'
                        email_html += FLOW_ANALYTICS_ROW + '<span>' + channel + '</span></td></tr>'
        elif analytics_type == "2":
            start_date = (datetime.datetime.today() -
                          datetime.timedelta(7)).date()
            end_date = datetime.datetime.today()
            for channel in channel_list:
                for intent in intent_list:
                    if intent.tree.children.count():
                        daily_intent_obj = DailyFlowAnalytics.objects.filter(intent_indentifed=intent, current_tree=intent.tree, previous_tree=intent.tree, channel=Channel.objects.get(
                            name=channel), created_time__gte=start_date, created_time__lt=end_date)
                        today_intent_obj = FlowAnalytics.objects.filter(
                            intent_indentifed=intent, current_tree=intent.tree, previous_tree=intent.tree, channel=Channel.objects.get(name=channel))
                        total_intent_called = daily_intent_obj.aggregate(
                            Sum('count'))['count__sum']
                        if not total_intent_called:
                            total_intent_called = 0
                        if today_intent_obj.count():
                            total_intent_called += today_intent_obj.count()

                        email_html += '<tr>' + FLOW_ANALYTICS_ROW + intent.name + '</td>'
                        email_html += FLOW_ANALYTICS_ROW + '<span>' + \
                            str(total_intent_called) + '</span></td>'
                        daily_intent_obj_completed = DailyFlowAnalytics.objects.filter(intent_indentifed=intent, is_last_tree_child=True, channel=Channel.objects.get(
                            name=channel), created_time__gte=start_date, created_time__lt=end_date).aggregate(Sum('count'))['count__sum']
                        total_intent_obj_completed = FlowAnalytics.objects.filter(
                            intent_indentifed=intent, is_last_tree_child=True, channel=Channel.objects.get(name=channel)).count()
                        if not daily_intent_obj_completed:
                            daily_intent_obj_completed = 0
                        if not total_intent_obj_completed:
                            total_intent_obj_completed = 0
                        email_html += FLOW_ANALYTICS_ROW + '<span>' + \
                            str(daily_intent_obj_completed +
                                total_intent_obj_completed) + '</span></td>'
                        email_html += FLOW_ANALYTICS_ROW + '<span>' + channel + '</span></td></tr>'
        elif analytics_type == "3":
            start_date = (datetime.datetime.today() -
                          datetime.timedelta(30)).date()
            end_date = datetime.datetime.today()
            for channel in channel_list:
                for intent in intent_list:
                    if intent.tree.children.count():
                        daily_intent_obj = DailyFlowAnalytics.objects.filter(intent_indentifed=intent, current_tree=intent.tree, previous_tree=intent.tree, channel=Channel.objects.get(
                            name=channel), created_time__gte=start_date, created_time__lt=end_date)
                        today_intent_obj = FlowAnalytics.objects.filter(
                            intent_indentifed=intent, current_tree=intent.tree, previous_tree=intent.tree, channel=Channel.objects.get(name=channel))
                        total_intent_called = daily_intent_obj.aggregate(
                            Sum('count'))['count__sum']
                        if not total_intent_called:
                            total_intent_called = 0
                        if today_intent_obj.count():
                            total_intent_called += today_intent_obj.count()

                        email_html += '<tr>' + FLOW_ANALYTICS_ROW + intent.name + '</td>'
                        email_html += FLOW_ANALYTICS_ROW + '<span>' + \
                            str(total_intent_called) + '</span></td>'
                        daily_intent_obj_completed = DailyFlowAnalytics.objects.filter(intent_indentifed=intent, is_last_tree_child=True, channel=Channel.objects.get(
                            name=channel), created_time__gte=start_date, created_time__lt=end_date).aggregate(Sum('count'))['count__sum']
                        total_intent_obj_completed = FlowAnalytics.objects.filter(
                            intent_indentifed=intent, is_last_tree_child=True, channel=Channel.objects.get(name=channel)).count()
                        if not daily_intent_obj_completed:
                            daily_intent_obj_completed = 0
                        if not total_intent_obj_completed:
                            total_intent_obj_completed = 0
                        email_html += FLOW_ANALYTICS_ROW + '<span>' + \
                            str(daily_intent_obj_completed +
                                total_intent_obj_completed) + '</span></td>'
                        email_html += FLOW_ANALYTICS_ROW + '<span>' + channel + '</span></td></tr>'

        email_html += '</tbody></table></tr>'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Get Flow Analytics: %s at line %s", e, str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return email_html


"""
export_form_assist_history : Generate the excel for form assist data and return the HTML with the excel link
"""


def export_form_assist_history(start_date, end_date, bot):
    import json
    from django.db.models import Q
    from EasyChatApp.models import FormAssistAnalytics
    from django.conf import settings
    from xlwt import Workbook
    import datetime
    global host_url

    automated_email_wb = Workbook(encoding="UTF-8")
    sheet1 = automated_email_wb.add_sheet(
        "Form Assist Messages", cell_overwrite_ok=True)
    sheet1.write(0, 0, "Date and Time")
    sheet1.col(0).width = 256 * 15
    sheet1.write(0, 1, "User Id")
    sheet1.col(1).width = 256 * 20
    sheet1.write(0, 2, "Field")
    sheet1.col(2).width = 256 * 100
    sheet1.write(0, 3, "MetaData")
    sheet1.col(3).width = 256 * 100
    sheet1.write(0, 3, "IsHelpful")
    sheet1.col(4).width = 256 * 100

    mis_objs = FormAssistAnalytics.objects.filter(
        lead_datetime__date__gte=start_date, lead_datetime__date__lt=end_date, bot=bot)
    index = 0

    for mis_obj in mis_objs:
        try:
            date_db = str(mis_obj.lead_datetime).split(".")[0]
            date_formatted = datetime.datetime.strptime(
                date_db, "%Y-%m-%d  %H:%M:%S")
            date_humanized = datetime.datetime.strftime(
                date_formatted, "%d-%B-%Y %H:%M %p")
            field_name = mis_obj.form_assist_field.intent.name
            metadata = mis_obj.meta_data
            is_helpful = mis_obj.is_helpful

            sheet1.write(index + 1, 0, str(date_humanized))
            sheet1.write(index + 1, 1, str(mis_obj.user_id))
            sheet1.write(index + 1, 2, field_name)
            sheet1.write(index + 1, 3, metadata)
            sheet1.write(index + 1, 4, is_helpful)
            index += 1
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(str(e) + " at line no" + str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    filename = "files/email-excels/BotFormAssitHistory_" + str(bot.pk) + "-{}.xls".format(
        str(end_date))
    automated_email_wb.save(filename)
    filename = host_url + "/" + filename

    filename_html = EMAIL_FILE_BODY + '<div style="display:flex;"><a class="em_bold" href="' + filename + \
        '" target="_blank" style="color: #ffffff;text-decoration: none;display: block;line-height: 35px;width:20em;height:35px;width:245px;padding: 10px 24px;border-collapse: collapse;mso-line-height-rule: exactly;">Download Form Assist Data</a></div></td></tr></table></tr>'
    return filename_html


"""
get_accuracy_html : return the table html for accuracy drop alert
"""


def get_accuracy_html(total_queries, total_unanswered_queries, bot_accuracy):
    html = EMAIL_TOTAL_BODY + EMAIL_TOTAL_VALUES + str(total_queries) + \
        '</span></td></tr>'

    html += EMAIL_UNANSWERED_BODY + EMAIL_UNANSWERED_VALUES + str(total_unanswered_queries) + \
        '</span></td></tr>'

    html += EMAIL_ACCURACY_BODY + EMAIL_BOT_ACCURACY_VALUES + str(bot_accuracy) + \
        '</span></td></tr>'

    return html


"""
generate_mail : It will create the HTML and send the mail to the given email ids
"""


def generate_mail(bot_name, analytics_date, anaytics_html, email, message_subject, file_data, email_footer, flow_analytics):

    email_footer = EMAIL_FOOTER + str(email_footer)
    body = """
            """ + EMAIL_DAILY_MAIL_HEAD + """ Following is the analytics for """ + str(bot_name) + """ bot <br> <p style="font-weight:400;font-size:16px;"> Analysis for past week</p>""" + EMAIL_HEADING_END + anaytics_html + flow_analytics + EMAIL_ANALYTICS_END_LINE + file_data + email_footer + EMAIL_BODY_END + '</tbody></table>'"""
    """

    send_email_to_customer_via_awsses(email, message_subject, body)


def get_analytics_html_for_pie_chart(chart_url, chips_html, chart_heading):
    try:
        html = EMAIL_ANALYTICS_CHART_HEADING + \
            str(chart_heading) + EMAIL_HEADING_END
        html += "<tr><div class ='chart-container' style='padding-top: 20px;padding-bottom: 20px;'> <div class='img-container'>"
        html += "<img src ={} />".format(chart_url)
        html += """</div><div class="chips-wrapper">"""
        html += chips_html
        html += """</div> </div> </tr>"""
        return html

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_analytics_html_for_cat: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_analytics_html_for_line_chart(chart_url, chart_heading):
    try:
        html = EMAIL_ANALYTICS_CHART_HEADING + \
            str(chart_heading) + EMAIL_HEADING_END
        html += "<tr><div class ='chart-container''> <div class='img-container-line-chart' style='margin: auto;margin-top: 2em;'> "
        html += "<img src ={} />".format(chart_url)
        html += "</div> </tr>"
        return html

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_analytics_html_for_cat: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_analytics_date(analytics_type, start_date, end_date):
    date = ""
    try:
        if analytics_type == "1":
            date = str(start_date.strftime("%d-%B-%Y"))
        elif analytics_type == "2":
            date = str(start_date.strftime("%d-%B-%Y")) + \
                " - " + str(end_date.strftime("%d-%B-%Y"))
        elif analytics_type == "3":
            date = str(start_date.strftime("%d-%B-%Y")) + \
                " - " + str(end_date.strftime("%d-%B-%Y"))
        return date

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_analytics_html_for_cat: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return date


"""
send_test_mail_based_on_config : It will send the test email.
"""

"""
def send_test_mail_based_on_config(email_configuration_pk, email_freq, MISDashboard, UniqueUsers, MessageAnalyticsDaily, Channel, Category):
    from EasyChatApp.models import EmailConfiguration
    import json
    import datetime
    email_configurations = [
        EmailConfiguration.objects.get(pk=email_configuration_pk)]
    analytics_type = str(email_freq)
    if analytics_type == "1":
        start_date = (datetime.datetime.now() - datetime.timedelta(1)).date()
        end_date = (datetime.datetime.now() - datetime.timedelta(0)).date()
    elif analytics_type == "2":
        start_date = (datetime.datetime.now() - datetime.timedelta(7)).date()
        end_date = (datetime.datetime.now() - datetime.timedelta(0)).date()
    else:
        start_date = (datetime.datetime.now() - datetime.timedelta(30)).date()
        end_date = (datetime.datetime.now() - datetime.timedelta(0)).date()
    for email_config in email_configurations:
        try:
            bot_obj = email_config.bot
            if bot_obj.is_email_notifiication_enabled:
                email_receivers = json.loads(email_config.email_address)
                channel = json.loads(email_config.channel)
                channel_list = []
                if "email-config-channel-web" in channel:
                    channel_list.append("Web")
                if "email-config-channel-whatsapp" in channel:
                    channel_list.append("WhatsApp")
                if "email-config-channel-google-assistant" in channel:
                    channel_list.append("GoogleHome")
                if "email-config-channel-alexa" in channel:
                    channel_list.append("Alexa")
                if "email-config-channel-android" in channel:
                    channel_list.append("Android")

                ma_chart_config = get_message_analytics_chart_config(
                    bot_obj, channel_list, MessageAnalyticsDaily, MISDashboard, Channel)

                encoded_config = quote(json.dumps(ma_chart_config))
                ma_chart_url = f'https://quickchart.io/chart?c={encoded_config}'
                ua_chart_config = get_user_analytics_chart_config(
                    bot_obj, channel_list, MISDashboard, UniqueUsers, Channel)

                encoded_config = quote(json.dumps(ua_chart_config))
                ua_chart_url = f'https://quickchart.io/chart?c={encoded_config}'
                cat_chart_config, cat_chips_html = get_category_chart_config(
                    bot_obj, channel_list, MISDashboard, Category)

                encoded_config = quote(json.dumps(cat_chart_config))
                cat_chart_url = f'https://quickchart.io/chart?c={encoded_config}'
                channel_chart_config, channel_chips_html = get_channel_chart_config(
                    bot_obj, channel_list, MISDashboard)

                encoded_config = quote(json.dumps(channel_chart_config))
                channel_chart_url = f'https://quickchart.io/chart?c={encoded_config}'
                user_analytics = get_analytics_html_for_line_chart(
                    ua_chart_url, "Daily User Analytics")
                message_analytics = get_analytics_html_for_line_chart(
                    ma_chart_url, "Number of Messages")
                channel_analytics = get_analytics_html_for_pie_chart(
                    channel_chart_url, channel_chips_html, "Channel Usage")
                category_analytics = get_analytics_html_for_pie_chart(
                    cat_chart_url, cat_chips_html, "Category Usage")
                analytics_string = "<hr style='border:0.5px solid #E3E3E3'>"
                analytics_string += user_analytics
                analytics_string += message_analytics
                analytics_string += category_analytics
                analytics_string += channel_analytics

                analytics_date = ""
                email_content = ""
                email_subject = ""
                flow_analytics_string = ""
                analytics = json.loads(email_config.analytics)

                table_analytics_string = ""
                analytics_date = ""
                flow_analytics_string = ""
                if "email-config-analytics-msg" in analytics:
                    if "email-config-analytics-form-assist" in analytics:
                        if bot_obj.is_form_assist_enabled:
                            analytics_date, table_analytics_string = get_bot_analytics(
                                start_date, end_date, channel_list, True, bot_obj, analytics_type)
                        else:
                            analytics_date, table_analytics_string = get_bot_analytics(
                                start_date, end_date, channel_list, False, bot_obj, analytics_type)
                    else:
                        analytics_date, table_analytics_string = get_bot_analytics(
                            start_date, end_date, channel_list, False, bot_obj, analytics_type)
                elif "email-config-analytics-form-assist" in analytics:
                    if bot_obj.is_form_assist_enabled:
                        analytics_date, table_analytics_string = get_bot_analytics(
                            start_date, end_date, channel_list, True, bot_obj, analytics_type)
                if "flow-completion-analytics-msg" in analytics:
                    flow_analytics_string = get_flow_analytics(
                        channel_list, bot_obj, analytics_type)
                analytics_string += EMAIL_DAILY_BOT_USAGE_ANLAYTICS_HEADING_START + "Bot Usage Analytics for " + \
                    str(bot_obj.name) + EMAIL_HEADING_END
                if analytics_date == "" and table_analytics_string == "" and flow_analytics_string != "":
                    analytics_date = get_analytics_date(
                        analytics_type, start_date, end_date)
                    analytics_string += EMAIL_DAILY_ANALYTICS_DATE + \
                        str(analytics_date) + "</p> </td></tr>"
                if table_analytics_string != "":
                    analytics_string += EMAIL_DAILY_ANALYTICS_DATE + \
                        str(analytics_date) + EMAIL_CATEGORY_START + \
                        table_analytics_string

                chat_history = json.loads(email_config.chat_history)
                file_data = ""
                if "email-config-logs-all" in chat_history:
                    file_data += export_bot_user_msg_history(
                        start_date, end_date, channel_list, bot_obj)
                if "email-config-logs-unanswered" in chat_history:
                    file_data += export_unanswered_data(
                        start_date, end_date, bot_obj)
                if "email-config-logs-form-assist" in chat_history:
                    file_data += export_form_assist_history(
                        start_date, end_date, bot_obj)
                email_subject = email_config.subject
                email_content = email_config.content
                for email in email_receivers:
                    try:
                        generate_mail(bot_obj.name, analytics_date, analytics_string,
                                      email, email_subject, file_data, email_content, flow_analytics_string)
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("send_test_mail_based_on_config > genrate mail: %s %s", str(e), str(exc_tb.tb_lineno), extra={
                            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                        pass
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("send_test_mail_based_on_config: %s %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
"""

"""
generate_mail : It will create the HTML for bot accuracy alert and send the mail to the given email ids
"""


def generate_mail_for_bot_accuracy(bot_name, analytics_date, accuracy_html, email, message_subject, channel):

    analytics_date = str(analytics_date.strftime("%d-%B-%Y"))
    body = """
            """ + EMAIL_HEAD + """ ACCURACY DROP ALERT for """ + str(channel) + """ channel - """ + str(bot_name) + EMAIL_ANALYTICS_DATE + str(analytics_date) + EMAIL_ACCURACY_START + accuracy_html + EMAIL_BODY_END + '</tbody></table>'  """
    """

    send_email_to_customer_via_awsses(email, message_subject, body)


def get_message_analytics_chart_config(bot_obj, channels, MessageAnalyticsDaily, MISDashboard, Channel):

    total_messages_list = []
    total_answered_messages_list = []
    total_unanswered_messages_list = []
    label_list = []
    predicted_messages_no_list = []

    message_analytics_list = get_message_analytics_data(
        bot_obj, channels, MessageAnalyticsDaily, MISDashboard, Channel)
    for data in message_analytics_list:
        label_list.append(data['label'])
        total_messages_list.append(data['total_messages'])
        total_answered_messages_list.append(data['total_answered_messages'])
        total_unanswered_messages_list.append(
            data['total_unanswered_messages'])
        predicted_messages_no_list.append(data['predicted_messages_no'])

    chart_config = {
        'type': 'line',
        'data': {
            'labels': label_list,
            'fontColor': '#2E31A5',
            'datasets': [
                # {
                #     'label': "Projected",
                #     'fill': "+1",
                #     'backgroundColor': "rgba(47, 70, 132, 0.08)",
                #     'borderColor': "#90A6E2",
                #     # 'backgroundColor': "#90A6E2",
                #     'borderDash': [5, 5],
                #     'pointRadius': 2,
                #     'data': predicted_messages_no_list,

                # },
                {
                    'label': "Total",
                    'fill': "+1",
                    'backgroundColor': "rgba(255, 67, 135, 0.08)",
                    # 'backgroundColor': "#FF4387",
                    'borderColor': "rgba(255, 67, 135, 0.48)",
                    'color': "#FF4387",
                    'pointRadius': 2,
                    'data': total_messages_list,
                    "datalabels": {
                        "align": 'end',
                        'display': True,
                        # "color": "#FF4387",
                        'color': "#2d2d2d",
                        # 'backgroundColor': "rgba(255, 67, 135, 0.08)"
                    }
                },
                {
                    'label': "Answered",
                    'fill': "+1",
                    'backgroundColor': "rgba(107, 225, 25, 0.08)",
                    # 'backgroundColor': "#6BE119",
                    'borderColor': "rgba(107, 225, 25, 0.38)",
                    'pointRadius': 2,
                    'data': total_answered_messages_list,
                    "datalabels": {
                        "align": 'start',
                        'display': True,
                        # "color": "#6be119",
                        'color': "#2d2d2d",
                        # "backgroundColor": '#fff',
                        # 'backgroundColor': "rgba(107, 225, 25, 0.08)"

                    }

                },
                {
                    'label': "Unanswered",
                    'fill': True,
                    'backgroundColor': "rgba(53, 70, 198, 0.16)",
                    # 'backgroundColor': "#2F4684",
                    'borderColor': "rgba(53, 70, 198, 0.36)",
                    'pointRadius': 2,
                    'data': total_unanswered_messages_list,
                    "datalabels": {
                        "align": 'center',
                        'display': True,
                        # "backgroundColor": '#f9f9f9',
                        # "color": "#2F4684",
                        'color': "#2d2d2d",
                        # 'backgroundColor': "rgba(53, 70, 198, 0.16)"
                    }

                },

            ]
        },
        'options': {
            'title': {
                'display': False,
                'text': 'Number Of Messages'
            },
            "plugins": {
                "datalabels": {
                    "align": 'end',
                    'display': False,
                    "color": "rgba(53, 70, 198, 0.56)",
                }
            },
            'legend': {
                'display': True,
                'position': 'bottom',
                'align': 'center',
                "fullWidth": False,
                'labels': {
                    'fontFamily': "'Silka', 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
                    'fontColor': "#3445C6"
                },
            },
            "layout": {
                "padding": {
                    "left": 0,
                    "right": 0,
                    "top": 20,
                    "bottom": 0
                }
            },
            'scales': {
                'yAxes': [{
                    'ticks': {
                        'padding': 20,
                        'display': True,
                        # 'labelString': "No of users",
                        'beginAtZero': True,
                        # //stepSize: min_step_size,
                    },
                    "gridLines": {
                        "color": "#EDEDED"
                    },
                    "scaleLabel": {
                        "display": True,
                        "labelString": 'No of Messages'
                    },
                }],
                'xAxes': [{
                    'ticks': {
                        'padding': 20,
                        'display': True,
                        'beginAtZero': True,
                        # //stepSize: min_step_size,
                    },
                    "gridLines": {
                        "color": "#EDEDED"
                    },
                }]
            },

        }

    }
    return chart_config


def get_message_analytics_data(bot_obj, channels, MessageAnalyticsDaily, MISDashboard, Channel):
    message_analytics_list = []
    try:
        bot_objs = [bot_obj]
        start_date = (datetime.datetime.now(
        ) - datetime.timedelta(DEFAULT_NO_OF_DAYS_FOR_DAILY_MAILER_ANALYTICS)).date()
        end_date = (datetime.datetime.now() - datetime.timedelta(1)).date()
        datetime_start = start_date
        datetime_end = end_date

        mis_objects = MISDashboard.objects.filter(
            bot__in=bot_objs, creation_date=datetime.datetime.now().date(), channel_name__in=channels)
        previous_mis_objects = MessageAnalyticsDaily.objects.filter(
            bot__in=bot_objs, channel_message__in=list(Channel.objects.filter(name__in=channels)))

        total_hours_passed = datetime.datetime.today().hour
        avg_msgs = math.ceil((mis_objects.filter(
            creation_date=datetime.datetime.today()).count() / float(total_hours_passed)) * 24.0)

        if datetime_end.strftime("%d-%b-%y") == datetime.datetime.today().strftime("%d-%b-%y"):
            no_days = (datetime_end - datetime_start).days
        else:
            no_days = (datetime_end - datetime_start).days + 1
        for day in range(no_days):
            temp_datetime = datetime_start + datetime.timedelta(day)
            date_filtered_mis_objects = previous_mis_objects.filter(
                date_message_analytics=temp_datetime)
            total_messages = date_filtered_mis_objects.aggregate(
                Sum('total_messages_count'))['total_messages_count__sum']

            total_answered_messages = date_filtered_mis_objects.aggregate(
                Sum('answered_query_count'))['answered_query_count__sum']
            total_unanswered_messages = date_filtered_mis_objects.aggregate(
                Sum('unanswered_query_count'))['unanswered_query_count__sum']
            message_analytics_list.append({
                "label": str(temp_datetime.strftime("%d-%b-%y")),
                "total_messages": total_messages,
                "total_answered_messages": total_answered_messages,
                "total_unanswered_messages": total_unanswered_messages,
                "predicted_messages_no": total_messages
            })

        if datetime_end.strftime("%d-%b-%y") == datetime.datetime.today().strftime("%d-%b-%y"):
            date_filtered_mis_objects = mis_objects
            total_messages = date_filtered_mis_objects.count()

            total_unanswered_messages = date_filtered_mis_objects.filter(
                intent_name=None, is_unidentified_query=True).count()

            total_answered_messages = total_messages - total_unanswered_messages

            message_analytics_list.append({
                "label": str((datetime_end).strftime("%d-%b-%y")),
                "total_messages": total_messages,
                "total_answered_messages": total_answered_messages,
                "total_unanswered_messages": total_unanswered_messages,
                "predicted_messages_no": total_messages
            })
            message_analytics_list[-1]["predicted_messages_no"] = avg_msgs

        return message_analytics_list
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_message_analytics_data: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return message_analytics_list


def get_user_analytics(bot_obj, channels, MISDashboard, UniqueUsers, Channel):

    user_analytics_list = []

    try:
        start_date = (datetime.datetime.now(
        ) - datetime.timedelta(DEFAULT_NO_OF_DAYS_FOR_DAILY_MAILER_ANALYTICS)).date()
        end_date = (datetime.datetime.now() - datetime.timedelta(1)).date()
        datetime_start = start_date
        datetime_end = end_date
        bot_objs = [bot_obj]

        mis_objects = MISDashboard.objects.filter(
            bot__in=bot_objs, channel_name__in=channels, creation_date=datetime.datetime.now().date())
        previous_mis_objects = UniqueUsers.objects.filter(
            bot__in=bot_objs, channel__in=Channel.objects.filter(name__in=channels))

        if datetime_end.strftime("%d-%b-%y") == datetime.datetime.today().strftime("%d-%b-%y"):
            no_days = (datetime_end - datetime_start).days
        else:
            no_days = (datetime_end - datetime_start).days + 1
        for day in range(no_days):
            temp_datetime = datetime_start + datetime.timedelta(day)
            date_filtered_mis_objects = previous_mis_objects.filter(
                date=temp_datetime)
            count = date_filtered_mis_objects.aggregate(
                Sum('count'))['count__sum']

            if count == None:
                count = 0

            user_analytics_list.append({
                "label": str(temp_datetime.strftime("%d-%b-%y")),
                "count": count,
            })

        if datetime_end.strftime("%d-%b-%y") == datetime.datetime.today().strftime("%d-%b-%y"):
            date_filtered_mis_objects = mis_objects
            total_users = date_filtered_mis_objects.values(
                "user_id").distinct().count()

            user_analytics_list.append({
                "label": str((datetime_end).strftime("%d-%b-%y")),
                "count": total_users,
            })

        return user_analytics_list

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_user_analytics: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return user_analytics_list


def get_user_analytics_chart_config(bot_obj, channels, MISDashboard, UniqueUsers, Channel):

    user_analytics_list = get_user_analytics(
        bot_obj, channels, MISDashboard, UniqueUsers, Channel)
    label_list = []
    no_users_list = []
    for data in user_analytics_list:
        label_list.append(data['label'])
        no_users_list.append(data['count'])

    chart_config = {
        'type': 'line',
                'data': {
                    'labels': label_list,
                    'datasets': [{
                        'label': "Number of total users",
                        'fill': True,
                        # // lineTension: 0.1,
                        # //backgroundColor: gradient,
                        # // backgroundColor: "#3445C6",
                        'borderColor': "#3445C6",
                        'fontColor': '#fff',

                        'data': no_users_list,
                        # // spanGaps: false,
                    },
                    ]
                },
        'options': {
                    'title': {
                        'display': False,
                        'text': 'Daily User Analytics'
                    },
                    "plugins": {
                        "datalabels": {
                            "align": 'end',
                            'display': True,
                            "color": "#2d2d2d",
                        }
                    },
                    'legend': {
                        'display': True,
                        'position': 'bottom',
                        'align': 'center',
                        "fullWidth": False,
                        'labels': {
                            'fontFamily': "'Silka', 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
                            'fontColor': "#3445C6"
                        }
                    },
                    "layout": {
                        "padding": {
                            "left": 0,
                            "right": 0,
                            "top": 20,
                            "bottom": 0
                        }
                    },
                    'scales': {
                        'yAxes': [{
                            'ticks': {
                                'padding': 20,
                                'display': True,
                                'labelString': "No of users",
                                'beginAtZero': True,
                                # //stepSize: min_step_size,
                            },
                            "scaleLabel": {
                                "display": True,
                                "labelString": 'No of Users'
                            },
                            "gridLines": {
                                "color": "#EDEDED"
                            },
                        }],
                        'xAxes': [{
                            'ticks': {
                                'padding': 20,
                                'display': True,
                                'beginAtZero': True,
                                # //stepSize: min_step_size,
                            },
                            "gridLines": {
                                "color": "#EDEDED"
                            },
                        }]
                    },
                }

    }

    return chart_config


def get_category_chart_config(bot_obj, channels, MISDashboard, Category):

    color_list = ["#2697FF", "#6BE119", "#2F4684", "#FFCF26",
                  "#FFA113", "#FF4387", "#FFA113", "#FF4387", "#FFA113", "#FF4387"]
    background_color_list = ["rgba(38, 151, 255, 0.08)", "rgba(107, 225, 25, 0.08)", "rgba(47, 70, 132, 0.08);", "rgba(255, 207, 38, 0.08)", "rgba(255, 161, 19, 0.08)",
                             "rgba(255, 67, 135, 0.08)", "rgba(255, 161, 19, 0.08)", "rgba(255, 67, 135, 0.08)", "rgba(255, 161, 19, 0.08)", "rgba(255, 67, 135, 0.08)"]
    category_dict = get_category_analytics(
        bot_obj, channels, MISDashboard, Category)
    category_list = []
    message_count_list = []
    html = ""
    iterator = 0
    for data in category_dict:
        category_list.append(data)
        html += '<div class="chip" style="align-items:center;color:' + color_list[iterator] + ';background-color:' + background_color_list[iterator] + ';border: 1px solid ' + color_list[iterator] + \
            ';"><span class="dot" style="background-color:' + \
                color_list[iterator] + ';"></span> <span class="chip-label" style="margin:auto;"> ' + data + \
            ': <span style="font-weight:bold;">' + \
                str(category_dict[data]) + '</span></span></div>'
        message_count_list.append(category_dict[data])
        iterator += 1

    chart_config = {
        'type': 'doughnut',
        'data': {
            'labels': category_list,
            'datasets': [{
                'label': "Number of total users",
                'fill': True,
                'backgroundColor': color_list,
                'borderColor': color_list,
                'fontColor': '#fff',
                'data': message_count_list,
                # // spanGaps: false,
            },
            ]
        },
        'options': {
            'title': {
                'display': False,
                'text': 'Category Usage'
            },
            "plugins": {
                "datalabels": {
                    'display': False,
                    "color": "#fff",
                }
            },
            'legend': {
                'display': False,
                'position': 'right',
                'align': 'start',
                'labels': {
                    'boxWidth': 30,
                    'usePointStyle': True,
                    'padding': 50,
                    'fontColor': "#2d2d2d"
                }
            }
        }
    }

    return chart_config, html


def get_category_analytics(bot_obj, channels, MISDashboard, Category):
    category_dict = {}
    try:
        start_date = (datetime.datetime.now(
        ) - datetime.timedelta(DEFAULT_NO_OF_DAYS_FOR_DAILY_MAILER_ANALYTICS)).date()
        end_date = (datetime.datetime.now() - datetime.timedelta(1)).date()

        datetime_start = start_date
        datetime_end = end_date

        bot_objs = [bot_obj]
        mis_objects = MISDashboard.objects.filter(
            bot__in=bot_objs, channel_name__in=channels)
        if datetime_start != None and datetime_end != None:
            mis_objects = mis_objects.filter(
                date__date__gte=datetime_start, date__date__lte=datetime_end)

        category_name_frequency = list(mis_objects.filter(~Q(category__name="") & ~Q(category=None) & ~Q(category__name="ABC")).filter(small_talk_intent=False).values(
            "category__name").order_by("category__name").annotate(frequency=Count("category__name")).order_by('-frequency'))

        for category_obj in Category.objects.filter(bot=bot_objs[0]):
            category_dict[category_obj.name] = 0

        for category_detail in category_name_frequency:
            category_dict[category_detail["category__name"]
                          ] = category_detail["frequency"]

        sorted_category_dict = sorted(
            category_dict.items(), key=lambda x: x[1], reverse=True)
        final_dict = {}
        for iterator in range(0, min(5, len(sorted_category_dict))):
            final_dict[sorted_category_dict[iterator]
                       [0]] = sorted_category_dict[iterator][1]

        if "Others" not in final_dict and "Others" in category_dict:
            final_dict["Others"] = category_dict["Others"]

        return final_dict
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[NLP]: Error GetChannelAnalyticsAPI %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': "", 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

    return category_dict


def get_channel_chart_config(bot_obj, channels, MISDashboard):
    channel_dict = get_channel_analytics(bot_obj, channels, MISDashboard)
    channel_list = []
    message_count_list = []

    color_list = ["#2697FF", "#6BE119", "#2F4684", "#FFCF26",
                  "#FFA113", "#FF4387", "#FFA113", "#FF4387", "#FFA113", "#FF4387"]
    background_color_list = ["rgba(38, 151, 255, 0.08)", "rgba(107, 225, 25, 0.08)", "rgba(47, 70, 132, 0.08);", "rgba(255, 207, 38, 0.08)", "rgba(255, 161, 19, 0.08)",
                             "rgba(255, 67, 135, 0.08)", "rgba(255, 161, 19, 0.08)", "rgba(255, 67, 135, 0.08)", "rgba(255, 161, 19, 0.08)", "rgba(255, 67, 135, 0.08)"]
    html = ""
    iterator = 0
    for data in channel_dict:
        channel_list.append(data)
        message_count_list.append(channel_dict[data])
        html += '<div class="chip" style="align-items:center;color:' + color_list[iterator] + ';background-color:' + background_color_list[iterator] + ';border: 1px solid ' + color_list[iterator] + \
            ';"><span class="dot" style="background-color:' + \
                color_list[iterator] + ';"></span> <span class="chip-label" style="margin:auto;"> ' + data + \
            ': <span style="font-weight:bold;">' + \
                str(channel_dict[data]) + '</span></span></div>'
        iterator += 1

    chart_config = {
        'type': 'doughnut',
        'data': {
            'labels': channel_list,
            'datasets': [{
                'label': "Number of total users",
                'fill': True,
                'fontColor': '#fff',
                'backgroundColor': color_list,
                'borderColor': color_list,
                'data': message_count_list,
                'color': '#fff',
                'fontFamily': 'Silka, Helvetica, sans-serif',
                # // spanGaps: false,
            },
            ]
        },
        'options': {
            'title': {
                'display': False,
                'text': 'Channel Usage'
            },
            "plugins": {
                "datalabels": {
                    'display': False,
                    "color": "#fff",
                }
            },
            'legend': {
                'display': False,
                'position': 'right',
                'align': 'start',
            }
        }
    }

    return chart_config, html


def get_channel_analytics(bot_obj, channels, MISDashboard):
    channel_dict = {}
    try:

        start_date = (datetime.datetime.now(
        ) - datetime.timedelta(DEFAULT_NO_OF_DAYS_FOR_DAILY_MAILER_ANALYTICS)).date()
        end_date = (datetime.datetime.now() - datetime.timedelta(1)).date()

        datetime_start = start_date
        datetime_end = end_date

        bot_objs = [bot_obj]

        mis_objects = MISDashboard.objects.filter(
            bot__in=bot_objs, channel_name__in=channels)

        if datetime_start != None and datetime_end != None:
            mis_objects = mis_objects.filter(
                date__date__gte=datetime_start, date__date__lte=datetime_end)

        channel_name_frequency = list(mis_objects.filter(~Q(channel_name=None)).values(
            "channel_name").order_by("channel_name").annotate(frequency=Count("channel_name")).order_by('-frequency'))

        for channel in channels:
            channel_dict[channel] = 0

        for channel_detail in channel_name_frequency:
            channel_dict[channel_detail["channel_name"]
                         ] = channel_detail["frequency"]
        return channel_dict
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[NLP]: Error GetChannelAnalyticsAPI %s in line no %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': "", 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})

    return channel_dict
