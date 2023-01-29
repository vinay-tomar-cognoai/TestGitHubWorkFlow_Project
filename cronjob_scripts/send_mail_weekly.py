from EasyChatApp.models import EmailConfiguration, MISDashboard, MessageAnalyticsDaily, Channel, UniqueUsers, Category
from EasyChatApp.utils_email_configuration import get_bot_analytics, \
    export_bot_user_msg_history, export_unanswered_data, \
    export_form_assist_history, generate_mail, get_flow_analytics, get_message_analytics_chart_config, \
    get_analytics_html_for_line_chart, get_analytics_html_for_pie_chart, get_analytics_date,\
    get_user_analytics_chart_config, get_channel_chart_config, get_category_chart_config
from EasyChatApp.email_html_constants import *
import os
import sys
import json
import datetime
from urllib.parse import quote
from EasyChatApp.utils import logger


def cronjob():
    try:
        email_configurations = EmailConfiguration.objects.filter(
            email_freq="2")
        start_date = (datetime.datetime.now() - datetime.timedelta(7)).date()
        end_date = (datetime.datetime.now() - datetime.timedelta(0)).date()
        analytics_type = "2"
        for email_config in email_configurations:
            try:
                bot_obj = email_config.bot
                if bot_obj.is_deleted:
                    continue
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

                    # analytics = json.loads(email_config.analytics)

                    analytics_string = ""
                    analytics_date = ""
                    flow_analytics_string = ""

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
                            generate_mail(bot_obj.name,
                                          analytics_date,
                                          analytics_string,
                                          email,
                                          email_subject,
                                          file_data,
                                          email_content, flow_analytics_string)
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            logger.error("Send Mail Weekly! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                            continue
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Send Mail Weekly! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                continue
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Send Mail Weekly! %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        pass
