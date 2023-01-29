from EasyChatApp.utils import *
from EasyChatApp.models import *
from LiveChatApp.models import *
from CampaignApp.models import CampaignAnalytics, CampaignAudienceLog
from EasyChatApp.utils_bot import process_response_based_on_language
from LiveChatApp.utils import *
from LiveChatApp.livechat_channels_webhook import get_livechat_response
from EasyChatApp.utils_validation import EasyChatInputValidation
# from LiveChatApp.utils_ksec_api_handler import send_ksec_api_failure_mail
from django.conf import settings
import emoji
import time
import json
import sys
import copy
import requests
import http.client
import mimetypes
import datetime
from bs4 import BeautifulSoup
from django.utils import timezone as tz

log_param = {'AppName': 'EasyChat', 'user_id': 'None',
             'source': 'None', 'channel': 'WhatsApp', 'bot_id': '61'}

# ========================== TEXT FORMATTING FUNCTIONS =========================


def youtube_link_formatter(message):
    if "https://www.youtube.com" in message:
        message = message.replace(
            "embed/", "").replace("www.youtube.com", "youtu.be")
    return message


def html_list_formatter(sent):
    try:
        logger.info("---Html list string found---", extra=log_param)
        ul_end_position = 0
        ol_end_position = 0
        if "<ul>" in sent:
            for itr in range(sent.count("<ul>")):
                ul_position = sent.find("<ul>", ul_end_position)
                ul_end_position = sent.find("</ul>", ul_position)
                list_str = sent[ul_position:ul_end_position + 5]
                logger.info("HTML LIST STRING " + str(itr + 1) + ": %s",
                            str(list_str), extra=log_param)
                list_str1 = list_str.replace("<ul>", "").replace(
                    "</ul>", "").replace("<li>", "")
                items = list_str1.split("</li>")
                items[-2] = items[-2] + "<br><br>"
                formatted_list_str = ""
                for item in items:
                    if item.strip() != "":
                        formatted_list_str += "\n\n- " + item.strip() + "\n"
                sent = sent.replace(list_str, formatted_list_str).replace(
                    "<br>", "\n") + "\n"
                sent = sent.strip()
                logger.info("---Html list string formatted---",
                            extra=log_param)
        if "<ol>" in sent:
            # print("yes ol")
            for itr in range(sent.count("<ol>")):
                ol_position = sent.find("<ol>", ol_end_position)
                ol_end_position = sent.find("</ol>", ol_position)
                list_str = sent[ol_position:ol_end_position + 5]
                logger.info("HTML LIST STRING " + str(itr + 1) + ": %s",
                            str(list_str), extra=log_param)
                list_str1 = list_str.replace("<li>", "").replace(
                    "<ol>", "").replace("</ol>", "")
                items = list_str1.split("</li>")
                items[-2] = items[-2] + "<br><br>"
                formatted_list_str = ""
                for ind, item in enumerate(items[:-1]):
                    if item.strip() != "":
                        formatted_list_str += "\n" + \
                            str(ind + 1) + ". " + item.strip()
                sent = sent.replace(list_str, formatted_list_str)
                sent = sent.strip().replace("<br>", "\n")
                logger.info("---Html list string formatted---",
                            extra=log_param)
    except Exception as E:
        logger.error("Failed to format html list string: %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
        # print("Failed to format html list string: %s", str(E))
    return sent


def html_tags_formatter(message):
    logger.info("Inside html_tags_formatter", extra={
                'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "61"})
    tags = {
        "<br>": "\n", "<br/>": "\n", "<br />": "\n",
        "<b>": "*", "</b>": "*",
        "<em>": " _", "</em>": "_ ",
        "<i>": " _", "</i>": "_ ",
        "<strong>": "*", "</strong>": "*",
        "<p>": "", "</p>": "",
        "<div>": "", "</div>": "",
    }
    for tag in tags:
        message = message.replace(tag + "<a", "<a")
        message = message.replace("</a>" + tag, "</a>")
        message = message.replace("</a>\n" + tag, "</a>")
        message = message.replace(tag, tags[tag])

    if "</a>" in message:
        end = "\n"
        if "tel:" in message:
            end = ""
        message = message.replace("mailto:", "").replace("tel:", "")
        soup = BeautifulSoup(message, "html.parser")

        for link in soup.findAll('a'):
            href = link.get('href')
            if not href:
                continue
            link_name = link.string

            link_element = message[message.find(
                "<a"):message.find("</a>")] + "</a>"
            logger.info("html_tags_formatter href: %s", str(href), extra={
                        'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "61"})
            logger.info("html_tags_formatter link_name: %s", str(link_name), extra={
                        'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "61"})
            # if "tel:" in href:
            #     new_link_element = link_name
            if link_name.replace("http://", "").replace("https://", "").strip() == href.replace("http://", "").replace("https://", "").strip():
                message = message.replace(link_element, href + end)
            else:
                message = message.replace(
                    link_element, link_name + " " + href + end)

        message = message.replace("<a>", "").replace("</a>", "")
    return message


def unicode_formatter(message):
    unicodes = {"&nbsp;": " ", "&#39;": "\'", "&rsquo;": "\'", "&amp;": "&",
                "&hellip;": "...", "&quot;": "\"", "&rdquo;": "\"", "&ldquo;": "\""}
    for code in unicodes:
        message = message.replace(code, unicodes[code])
    return message
# ====================== end ===================================================


def save_file_from_remote_server_to_local(remote_url, local_path):
    is_saved = False
    try:
        logger.info("save_file_from_remote_server_to_local: remote_url: %s secs", str(
            remote_url), extra=log_param)
        start_time = time.time()
        response = requests.get(url=remote_url, timeout=10)
        response_time = response.elapsed.total_seconds()
        logger.info("save_file_from_remote_server_to_local: API response time: %s secs", str(
            response_time), extra=log_param)
        raw_data = response.content
        file_to_save = open(local_path, "wb")
        file_to_save.write(raw_data)
        file_to_save.close()
        end_time = time.time()
        response_time = end_time - start_time
        logger.info("save_file_from_remote_server_to_local: Total response time: %s secs", str(
            response_time), extra=log_param)
        is_saved = True
    except Exception as e:
        logger.error("save_file_from_remove_server_to_local: %s",
                     str(e), extra=log_param)
    return is_saved


def get_whatsapp_file_attachment(API_KEY, attachment_packet, attachment_type):
    attachment_path = None
    try:
        remote_url = attachment_packet["media_url"]
        mime_type = attachment_packet["mime_type"]
        signature = attachment_packet["id"]
        ext = mime_type.split("/")[-1]
        if "caption" in attachment_packet:
            filename = attachment_packet["caption"]
            if "application/pdf" in mime_type and ".pdf" not in filename:
                filename = filename + "." + ext
            else:
                filename = signature + "." + ext
        else:
            filename = signature + "." + ext
        filename = filename.replace(" ", "-")
        if not os.path.exists(settings.MEDIA_ROOT + 'WhatsAppMedia'):
            os.makedirs(settings.MEDIA_ROOT + 'WhatsAppMedia')
        file_path = settings.MEDIA_ROOT + "WhatsAppMedia/" + filename
        file_path_rel = "/files/WhatsAppMedia/" + filename
        save_file_from_remote_server_to_local(remote_url, file_path)
        attachment_path = file_path_rel
        logger.info("is_whatsapp_file_attachment: Filename %s",
                    filename, extra=log_param)
        logger.info("is_whatsapp_file_attachment: Filepath(Relative)%s",
                    attachment_path, extra=log_param)
    except Exception as e:
        logger.error("save_file_from_remote_server_to_local: %s",
                     str(e), extra=log_param)
    return attachment_path


#############################    LiveChat    ###################################
def customer_end_livechat(user_id, bot_obj):
    """
        Ends the livechat session of given username

    """
    try:
        user_obj = Profile.objects.filter(
            user_id=user_id, bot=bot_obj).order_by("-pk")[0]
        user_obj.livechat_connected = False
        user_obj.save()
        try:
            livechat_user_id = user_obj.livechat_user_id
            customer_obj = LiveChatCustomer.objects.get(
                user_id=livechat_user_id)
            mis_obj = customer_obj.mis_dashboard.all()[0]
            if customer_obj.is_agent_assigned == False and mis_obj.agent_id == None:
                customer_obj.is_agent_assigned = True
                customer_obj.save()
                mis_obj.is_session_exp = True
                mis_obj.abruptly_closed = True
                mis_obj.save()
        except Exception as E:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("customer_end_livechat: Partial Error %s",
                         str(E), str(exc_tb.tb_lineno), extra=log_param)
            pass
        return True
    except:
        return False


def check_for_livechat(user_id, bot_obj):
    """
        Checks whether the given user 's Livechat session is active or not.

    """
    try:
        user_obj = Profile.objects.filter(
            user_id=user_id, bot=bot_obj).order_by("-pk")[0]
        return user_obj.livechat_connected
    except:
        return False


def create_and_enable_livechat(mobile_number, channel, bot_obj, message):

    log_param = {'AppName': 'EasyChat', 'user_id': 'None',
                 'source': 'None', 'channel': str(channel), 'bot_id': 'None'}
    logger.info("INSIDE create and enable livechat", extra=log_param)
    try:
        # Depends if whatsapp vendor provides name of customer
        username = str(mobile_number)
        email = "None"
        active_url = settings.EASYCHAT_HOST_URL
        session_id = str(uuid.uuid4())

        # category_obj = get_livechat_category_object(
        #     category, bot_obj, LiveChatCategory)

        customer_obj = LiveChatCustomer.objects.create(session_id=session_id,
                                                       username=username,
                                                       phone=mobile_number,
                                                       email=email,
                                                       is_online=True,
                                                       easychat_user_id=mobile_number,
                                                       bot=bot_obj,
                                                       channel=Channel.objects.get(
                                                           name=channel),
                                                       active_url=active_url,
                                                       message=message)

        try:
            agent_unavialable_response = LiveChatConfig.objects.get(
                bot=bot_obj).agent_unavialable_response
        except Exception:
            agent_unavialable_response = "Our chat representatives are unavailable right now. Please try again in some time."
            pass

        try:
            boolian_var, response = check_for_holiday(
                bot_obj, LiveChatCalender, LiveChatUser)
            if boolian_var:
                customer_obj.is_denied = True
                customer_obj.is_session_exp = True
                customer_obj.system_denied_response = response["message"]
                customer_obj.is_system_denied = True
                customer_obj.last_appearance_date = timezone.now()
                customer_obj.is_online = False
                customer_obj.save()
                logger.error("message for holiday" +
                             str(response["message"]), extra=log_param)
                return response["message"]

            boolian_var, response = check_for_non_working_hour(
                bot_obj, LiveChatCalender, LiveChatConfig, LiveChatUser)

            if boolian_var:
                customer_obj.is_denied = True
                customer_obj.is_session_exp = True
                customer_obj.system_denied_response = response["message"]
                customer_obj.is_system_denied = True
                customer_obj.last_appearance_date = timezone.now()
                customer_obj.is_online = False
                customer_obj.save()
                logger.error("message for non working hour" +
                             str(response["message"]), extra=log_param)

                return response["message"]

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("create_and_enable_livechat Holiday check: %s at %s", str(e), str(
                exc_tb.tb_lineno), extra=log_param)

            customer_obj.is_denied = True
            customer_obj.is_session_exp = True
            customer_obj.system_denied_response = agent_unavialable_response
            customer_obj.last_appearance_date = timezone.now()
            customer_obj.is_online = False
            customer_obj.save()
            return agent_unavialable_response

        user_obj = Profile.objects.get(user_id=str(mobile_number), bot=bot_obj)
        user_obj.livechat_connected = True
        user_obj.livechat_session_id = str(customer_obj.session_id)
        user_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_and_enable_livechat Holiday check: %s at %s", str(e), str(
            exc_tb.tb_lineno), extra=log_param)
        return "Our chat representatives are busy right now. Please try again in some time."

    return ""


############################### END LIVECHAT MODULE ############################


# Calculate difference b/w datetime objects
def get_time_delta(date_str1, date_str2):
    delta_obj = {"minutes": 0.0, "hours": 0.0}
    try:
        if "." in date_str1:
            date_str1 = str(date_str1).split(".")[0]
        if "." in date_str2:
            date_str2 = str(date_str2).split(".")[0]
        date_str1 = datetime.datetime.strptime(date_str1, "%Y-%m-%d %H:%M:%S")
        date_str2 = datetime.datetime.strptime(date_str2, "%Y-%m-%d %H:%M:%S")
        delta = date_str2 - date_str1  # 2nd date is greater
        duration_in_s = delta.total_seconds()
        delta_obj = {
            "seconds": duration_in_s,
            # divmod(duration_in_s, 60)[0],
            "minutes": round(duration_in_s / 60, 1),
            "hours": divmod(duration_in_s, 3600)[0],
            "days": divmod(duration_in_s, 86400)[0],
            "years": divmod(duration_in_s, 31536000)[0]
        }
        return delta_obj
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_time_delta: %s at %s", str(
            E), str(exc_tb.tb_lineno), extra=log_param)
        return delta_obj


#   GET WMESSAGE FROM REVERSE MAPPING
def get_message_from_reverse_whatsapp_mapping(user_message, mobile, bot_obj):
    message = None
    try:
        is_suggestion = False
        logger.info(" === Reverse Message mapping === ", extra=log_param)

        user = Profile.objects.get(user_id=str(mobile), bot=bot_obj)
        data_obj = Data.objects.filter(
            user=user, variable="REVERSE_WHATSAPP_MESSAGE_DICT")[0]
        data_dict = json.loads(str(data_obj.get_value()))
        logger.info("reverse message: %s", str(data_dict), extra=log_param)
        if str(user_message) in data_dict:
            message = data_dict[str(user_message)]

            try:
                message = json.loads(message.replace("'", '"'))
                message = message["id"]
                is_suggestion = True
            except:
                is_suggestion = False

        logger.info(str(message), extra=log_param)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_message_from_reverse_whatsapp_mapping: %s %s" +
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    logger.info("final message: %s", str(message), extra=log_param)
    return message, is_suggestion


#   GET ROUTE MOBILE API KEY:
def GET_API_KEY(username, password):
    API_KEY = ""
    try:
        logger.info("=== Inside RouteMobile_GET_API_KEY API ===",
                    extra=log_param)
        url = "https://apis.rmlconnect.net/auth/v1/login/"
        payload = {
            "username": username,
            "password": password
        }
        headers = {
            'Content-Type': 'application/json'
        }
        req = requests.request("POST", url, headers=headers,
                               data=json.dumps(payload), timeout=10, verify=True)
        content = json.loads(req.text)
        logger.info("RouteMobile_GET_API_KEY Response: %s",
                    str(content), extra=log_param)
        if str(req.status_code) == "200" or str(req.status_code) == "201":
            API_KEY = content["JWTAUTH"]

        return API_KEY
    except requests.Timeout as rt:
        logger.error("RouteMobile_GET_API_KEY Timeout error: %s",
                     str(rt), extra=log_param)

    except Exception as e:
        logger.error("RouteMobile_GET_API_KEY Failed: %s",
                     str(e), extra=log_param)
    return API_KEY


# CACHING ROUTE MOBILE API KEY:


def GET_RML_JWT_TOKEN(username, password):
    API_KEY = None
    try:
        logger.info("=== Inside GET_RML_JWT_TOKEN 1===", extra=log_param)
        token_obj = RouteMobileToken.objects.all()
        if token_obj.count() < 0:
            logger.info("--- token object not found", extra=log_param)
            API_KEY = GET_API_KEY(username, password)
            token_obj = RouteMobileToken.objects.create(token=API_KEY)
        elif token_obj[0].token == None or token_obj[0].token == "" or token_obj[0].token == "token":
            logger.info("--- token object is None", extra=log_param)
            API_KEY = GET_API_KEY(username, password)
            token_pk = token_obj[0].id
            token_obj = RouteMobileToken.objects.get(id=token_pk)
            token_obj.token = API_KEY
            token_obj.token_generated_on = tz.now()
            token_obj.save()
            logger.info("--- token object updated", extra=log_param)
        else:
            token_pk = token_obj[0].id
            token_generated_on = str(token_obj[0].token_generated_on)
            current_time = str(tz.now())
            time_diff = get_time_delta(
                str(token_generated_on), str(current_time))["minutes"]
            logger.info("--- Token Minutes:  %s",
                        str(time_diff), extra=log_param)
            API_KEY = token_obj[0].token
            if float(time_diff) > 55.0:
                logger.info("--- token expired", extra=log_param)
                API_KEY = GET_API_KEY(username, password)
                token_obj = RouteMobileToken.objects.get(id=token_pk)
                token_obj.token = API_KEY
                token_obj.token_generated_on = tz.now()
                token_obj.save()
                logger.info("--- token object updated", extra=log_param)
        logger.info("=== END GET_RML_JWT_TOKEN 1===", extra=log_param)
        return API_KEY
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("GET_RML_JWT_TOKEN API 1 Failed: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
        logger.info("=== END GET_RML_JWT_TOKEN 1===", extra=log_param)
    return API_KEY

#   WHATSAPP SEND TEXT MESSAGE API:


def sendWhatsAppTextMessage(api_key, message, phone_number, preview_url=False):
    try:
        logger.info("=== Inside Send WA Text Message API ===", extra=log_param)
        url = "https://apis.rmlconnect.net/wba/v1/messages"
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if preview_url == True:
            payload = {
                "phone": "+" + phone_number,
                "text": message,
                "preview_url": True
            }
        else:
            payload = {
                "phone": "+" + phone_number,
                "text": message
            }
        req = requests.request("POST", url, headers=headers,
                               data=json.dumps(payload), timeout=10, verify=True)
        content = json.dumps(req.text)
        logger.info("Send WA Text API Response: %s",
                    str(content), extra=log_param)
        if str(req.status_code) == "200" or str(req.status_code) == "202":
            logger.info("Text message sent succesfully", extra=log_param)

            return True
        else:
            logger.error("Failed to Send Text Message.", extra=log_param)
            return False
    except requests.Timeout as rt:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(rt) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppText API Timeout error: %s",
                     str(rt), str(exc_tb.tb_lineno), extra=log_param)

        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(e) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppText API Failed: %s", str(e),
                     str(exc_tb.tb_lineno), extra=log_param)
    return False


# WHATSAPP SEND MEDIA MESSAGE API:
def sendWhatsAppMediaMessage(api_key, media_type, media_url, phone_number, caption=None):
    try:
        logger.info("=== Inside Send WA Media Message API ===",
                    extra=log_param)
        logger.info("Media Type: %s", media_type, extra=log_param)
        if media_type == "document" and caption == None:
            caption = "FileAttachment"
        elif caption == None:
            caption = ""
        url = "https://apis.rmlconnect.net/wba/v1/messages"
        headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            "phone": "+" + phone_number,
            "media": {
                "type": media_type,
                "url": media_url,
                "file": media_url.split("/")[-1],
                "caption": caption
            }
        }

        req = requests.request("POST", url, headers=headers,
                               data=json.dumps(payload), timeout=10, verify=True)

        content = json.loads(req.text)
        logger.info("Send WA " + media_type.upper() +
                    " API Response: %s", str(content), extra=log_param)
        if str(req.status_code) == "200" or str(req.status_code) == "202":
            logger.info(media_type.upper() +
                        " message sent successfully", extra=log_param)
            return True
        else:
            logger.error(url, extra=log_param)
            logger.error(headers, extra=log_param)
            logger.error(payload, extra=log_param)
            logger.error(content, extra=log_param)
            logger.error("Failed to send " + media_type.upper() +
                         " message: %s", extra=log_param)

            return False
    except requests.Timeout as rt:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(rt) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppMediaMessage Timeout error: %s",
                     str(rt), str(exc_tb.tb_lineno), extra=log_param)

        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(e) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppMediaMessage Failed: %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)
    return False


def get_emojized_message(message):
    return emoji.emojize(message, language='alias')


def change_language_response_required(sender, bot_id, bot):
    try:
        bot_obj = Bot.objects.get(pk=int(bot_id))
        channel = Channel.objects.filter(name="WhatsApp")[0]
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()

        profile_obj = Profile.objects.get(user_id=str(sender), bot=bot)

        if languages_supported.count() == 1:
            profile_obj.selected_language = languages_supported[0]
            profile_obj.save()

        if profile_obj.selected_language:
            return False

        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("change_language_response_required: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return True

# def change_language_response_required(sender):
#     try:
#         profile_obj = Profile.objects.get(user_id=str(sender))
#         logger.error("profile obj  " + str(profile_obj), extra=log_param)
#         if profile_obj.selected_language:
#             return False

#         return True
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error("change_language_response_required: %s at %s",
#                      str(e), str(exc_tb.tb_lineno), extra=log_param)

#     return True


def is_change_language_triggered(sender, bot_obj):
    try:
        user = Profile.objects.get(user_id=sender, bot=bot_obj)
        logger.error("profile obj  " + str(user), extra=log_param)
        data_obj = Data.objects.filter(
            user=user, variable="CHANGE_LANGUAGE_TRIGGERED")[0]

        if data_obj.get_value() == 'true':
            data_obj.value = False
            data_obj.save()
            return True

        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_change_language_triggered: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return False


def get_language_change_response(bot_id, REVERSE_WHATSAPP_MESSAGE_DICT):
    try:
        bot_obj = Bot.objects.get(pk=int(bot_id))
        logger.error("bot id in  get_language_change response " +
                     str(bot_id), extra=log_param)
        channel = Channel.objects.filter(name="WhatsApp")[0]
        bot_channel_obj = BotChannel.objects.filter(
            bot=bot_obj, channel=channel)[0]
        languages_supported = bot_channel_obj.languages_supported.all()
        # languages_supported = bot_obj.languages_supported.all()

        language_str = ""
        if languages_supported.count() > 1:
            languages = list(languages_supported.values('lang', 'display'))

            REVERSE_WHATSAPP_MESSAGE_DICT = {}
            language_str = "Please choose your language\n\n"
            for index in range(len(languages)):
                language = languages[index]['display']

                REVERSE_WHATSAPP_MESSAGE_DICT[str(
                    index + 1)] = str(languages[index]['lang'])
                language_str += ":point_right: Press " + \
                    str(index + 1) + " for " + str(language) + "\n\n"

        return language_str, REVERSE_WHATSAPP_MESSAGE_DICT
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_language_change_response: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return "", REVERSE_WHATSAPP_MESSAGE_DICT


def convert_timestamp_to_normal(timestamp):
    from datetime import datetime
    import pytz

    tz = pytz.timezone(settings.TIME_ZONE)
    dt_object = datetime.fromtimestamp(timestamp)

    return dt_object.astimezone(tz)


def check_if_go_back_enabled(user):
    try:
        data_obj = Data.objects.filter(
            user=user, variable="is_go_back_enabled")

        if data_obj:
            data_obj = data_obj.first()
            is_go_back_enabled = data_obj.get_value()

            return is_go_back_enabled == 'true'

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_if_go_back_enabled: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=log_param)

    return False


#   MAIN FUNCTION
def whatsapp_webhook(request_packet):
    validation_obj = EasyChatInputValidation()

    log_param = {'AppName': 'EasyChat', 'user_id': 'None',
                 'source': 'None', 'channel': 'WhatsApp', 'bot_id': '61'}
    send_status = False
    response = {}
    response["status_code"] = 500
    response["status_message"] = ""
    response["mobile_number"] = "917738988888"
    try:
        logger.info("INSIDE ROUTE MOBILE WA WEBHOOK", extra=log_param)
    #   DELIVERY STATUS:
        logger.error("INCOMING_DELIVERY_PACKET WA WEBHOOK: %s",
                     str(request_packet), extra=log_param)
        if "meta" in request_packet.keys() or "statuses" in request_packet.keys():
            logger.error("INCOMING_DELIVERY_PACKET WA WEBHOOK: %s",
                         str(request_packet), extra=log_param)
            try:
                # mobile_number = request_packet["statuses"][0]["recipient_id"]
                request_id = request_packet["statuses"][0]["id"]
                status = request_packet["statuses"][0]["status"]
                timestamp = request_packet["statuses"][0]["timestamp"]

                normal_timestamp = convert_timestamp_to_normal(int(timestamp))

                audience_log_obj = CampaignAudienceLog.objects.get(
                    recepient_id=request_id)
                campaign = audience_log_obj.campaign
                analytics_obj = CampaignAnalytics.objects.get(
                    campaign=campaign)

                if status == "sent" and audience_log_obj.is_sent == False:
                    audience_log_obj.is_sent = True
                    audience_log_obj.sent_datetime = normal_timestamp
                    audience_log_obj.sent_date = normal_timestamp.date()

                if status == "delivered" and audience_log_obj.is_delivered == False:
                    if audience_log_obj.is_sent == False:
                        audience_log_obj.is_sent = True
                        audience_log_obj.sent_datetime = normal_timestamp
                        audience_log_obj.sent_date = normal_timestamp.date()

                    audience_log_obj.is_delivered = True
                    audience_log_obj.delivered_datetime = normal_timestamp
                    audience_log_obj.delivered_date = normal_timestamp.date()

                if status == "read" and audience_log_obj.is_read == False:
                    if audience_log_obj.is_sent == False:
                        audience_log_obj.is_sent = True
                        audience_log_obj.sent_datetime = normal_timestamp
                        audience_log_obj.sent_date = normal_timestamp.date()

                    if audience_log_obj.is_delivered == False:
                        audience_log_obj.is_delivered = True
                        audience_log_obj.delivered_datetime = normal_timestamp
                        audience_log_obj.delivered_date = normal_timestamp.date()

                    audience_log_obj.is_read = True
                    audience_log_obj.read_datetime = normal_timestamp
                    audience_log_obj.read_date = normal_timestamp.date()

                audience_log_obj.save()
                analytics_obj.message_sent = CampaignAudienceLog.objects.filter(
                    campaign=campaign, is_sent=True).count()
                analytics_obj.message_read = CampaignAudienceLog.objects.filter(
                    campaign=campaign, is_read=True).count()
                analytics_obj.message_delivered = CampaignAudienceLog.objects.filter(
                    campaign=campaign, is_delivered=True).count()

                analytics_obj.save()

                response["mobile_number"] = request_packet["statuses"][0]["recipient_id"]

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Failed to extract: %s at %s", str(
                    e), str(exc_tb.tb_lineno), extra=log_param)
                pass

            return response

            response["status_code"] = 200
            response["status_message"] = "Request processed successfully."
            logger.info("RouteMobileDeliveryCheck: %s",
                        str(response), extra=log_param)

        logger.info("INSIDE ROUTE MOBILE WA WEBHOOK", extra=log_param)
        logger.info("INCOMING_REQUEST_PACKET WA WEBHOOK: %s",
                    str(request_packet), extra=log_param)

    # == CREDENTIALS AND DETAILS: ==============================================
        rm_username = "RMLBot2"
        rm_password = "Product@123"
        API_KEY = GET_API_KEY(rm_username, rm_password)
        # API_KEY = GET_RML_JWT_TOKEN(rm_username, rm_password)
        logger.info("RML JWT TOKEN: %s", str(API_KEY), extra=log_param)

        DEFAULT_BOT_ID = "61"
        BOT_ID = "61"
        sender = validation_obj.remo_html_from_string(
            str(request_packet["messages"][0]["from"]))
        receiver = validation_obj.remo_html_from_string(
            str(response["mobile_number"]))
        response["mobile_number"] = sender
        log_param["user_id"] = sender
        logger.info("Sender: %s", str(sender), extra=log_param)
        logger.info("Reciever: %s", str(receiver), extra=log_param)
    # ==========================================================================

        bot_obj = Bot.objects.get(pk=int(BOT_ID))

    #   GET PREVIOUS BOT ID
        user_obj = Profile.objects.filter(user_id=str(sender), bot=bot_obj)
        if user_obj:
            user_obj = user_obj[0]
            data_obj = Data.objects.filter(user=user_obj, variable="bot_id")
            logger.error("data obj is  " + str(data_obj), extra=log_param)

            if data_obj:
                logger.error("Bot id " + str(BOT_ID), extra=log_param)
                logger.error(
                    "Bot id " + str(data_obj[0].get_value().replace('"', "")), extra=log_param)
                BOT_ID = int(data_obj[0].get_value().replace('"', ""))
                logger.error("Bot id after data obj" +
                             str(BOT_ID), extra=log_param)
                # logger.info('Bot id is : ', str(BOT_ID), extra=log_param)

        bot_obj = Bot.objects.get(pk=int(BOT_ID))
        user_obj = Profile.objects.filter(user_id=str(sender), bot=bot_obj)

    #   CHECK FOR NEW USER:
        first_time_user = "false"
        check_user = Profile.objects.filter(user_id=str(sender), bot=bot_obj)
        if check_user.count() == 0:
            first_time_user = "true"
        logger.info("New User: %s", first_time_user, extra=log_param)

    #   CHECK USER MESSAGE TYPE: text, image, document, voice, location
        message_type = request_packet["messages"][0]["type"]
        logger.info("Message Type: %s", message_type, extra=log_param)

    #   GET USER ATTACHMENTS AND MESSAGES:
        # is_location = True
        is_attachement = True
        message = None
        filepath = None
        if message_type == "text":
            is_attachement = False
            # is_location = False

        is_suggestion = False
        if is_attachement:
            # image, document, voice
            attachment_packet = request_packet["messages"][0][message_type]
            attachment_type = message_type

            logger.info(str(attachment_packet), extra=log_param)
            if attachment_type != "document" and "caption" in attachment_packet:
                message = attachment_packet["caption"]
            else:
                message = "attachment"

            filepath = get_whatsapp_file_attachment(
                API_KEY, attachment_packet, attachment_type)
            logger.error(filepath, extra=log_param)
        else:
            # else get user Message:
            message = request_packet["messages"][0]["text"]["body"]
            reverse_message, is_suggestion = get_message_from_reverse_whatsapp_mapping(
                message, sender, bot_obj)

            if reverse_message != None:
                message = reverse_message
            else:
                is_suggestion = False
        logger.info("User Message: %s", str(message), extra=log_param)

        mobile = str(sender)  # User mobile
        waNumber = str(receiver)  # Bot Whatsapp Number

        is_go_back_enabled = check_if_go_back_enabled(user_obj.first())

        channel_params = {"user_mobile": mobile, "bot_number": waNumber, "attached_file_path": filepath,
                          "is_new_user": first_time_user, "QueryChannel": "WhatsApp", "entered_suggestion": is_suggestion, "is_go_back_enabled": is_go_back_enabled}

    #   CHECK FOR LIVECHAT:
        if check_for_livechat(mobile, bot_obj):
            logger.info("INSIDE CHECK FOR LIVECHAT", extra=log_param)
            if message.lower() == "end chat":
                customer_end_livechat(mobile, bot_obj)

                response["status_code"] = 200
                response["status_message"] = "Request processed successfully."
            return get_livechat_response(mobile, message, "WhatsApp", BOT_ID, json.dumps(channel_params))

    #   CHECK IF CHANGE LANGUAGE WAS TRIGGERED
        if is_change_language_triggered(sender, bot_obj):
            try:
                lang_obj = Language.objects.get(lang=message)
                profile_obj = Profile.objects.get(
                    user_id=str(sender), bot=bot_obj)
                profile_obj.selected_language = lang_obj
                profile_obj.save()

                text_message = "You have selected " + \
                    str(lang_obj.display) + \
                    ". If you want to change your language again please type"
                text_message = get_translated_text(
                    text_message, lang_obj.lang, EasyChatTranslationCache)
                text_message = text_message + ' "Change Language"'
                send_status = sendWhatsAppTextMessage(
                    API_KEY, text_message, mobile, preview_url=False)
                response["status_code"] = 200
                response["status_message"] = "Request processed successfully."
                return response
            except Exception as e:
                logger.error("is_change_language_triggered: %s at %s",
                             str(e), extra=log_param)

    #   CHECK IF CHANGE LANGUAGE IS CALLED
        if isinstance(message, str) and message.lower().strip() == "change language":
            logger.error("BOt id " + str(BOT_ID), extra=log_param)
            REVERSE_WHATSAPP_MESSAGE_DICT = {}
            language_str, REVERSE_WHATSAPP_MESSAGE_DICT = get_language_change_response(
                BOT_ID, REVERSE_WHATSAPP_MESSAGE_DICT)

            if language_str != "":
                language_str = get_emojized_message(language_str)
                send_status = sendWhatsAppTextMessage(
                    API_KEY, language_str, mobile)
                logger.info("Is change language response sent: %s",
                            str(send_status), extra=log_param)

                save_data(user_obj, json_data={"CHANGE_LANGUAGE_TRIGGERED": True},
                          src="None", channel="WhatsApp", bot_id="61", is_cache=True)

                logger.info("REVERSE_WHATSAPP_MESSAGE_DICT: %s", str(
                    REVERSE_WHATSAPP_MESSAGE_DICT), extra=log_param)
                save_data(user_obj, json_data={"REVERSE_WHATSAPP_MESSAGE_DICT": REVERSE_WHATSAPP_MESSAGE_DICT},
                          src="None", channel="WhatsApp", bot_id="61", is_cache=True)

                response["status_code"] = 200
                response["status_message"] = "Request processed successfully."
                return response

    #   GET LANGUAGE SELECTED BY USER
        try:
            selected_language = user_obj.selected_language
            logger.error("sleected_lang here " +
                         str(selected_language), extra=log_param)
            if not selected_language:
                selected_language = "en"
            else:
                selected_language = selected_language.lang
                # languages_supported = Bot.objects.get(
                #     pk=int(BOT_ID)).languages_supported
                bot_obj = Bot.objects.get(pk=int(BOT_ID))
                channel = Channel.objects.filter(name="WhatsApp")[0]
                bot_channel_obj = BotChannel.objects.filter(
                    bot=bot_obj, channel=channel)[0]
                languages_supported = bot_channel_obj.languages_supported
                languages_supported = languages_supported.filter(
                    lang=selected_language)

                if not languages_supported:
                    selected_language = "en"
        except Exception:
            selected_language = 'en'

    #   WEBHOOK EXECUTE FUNCTION CALL
        logger.error('Bot id before exec query : ' +
                     str(BOT_ID), extra=log_param)
        whatsapp_response = execute_query(mobile, BOT_ID, "uat", str(message), selected_language, "WhatsApp", json.dumps(
            channel_params), message)

        response_copy = copy.deepcopy(whatsapp_response)

        if selected_language != "en":
            whatsapp_response = process_response_based_on_language(
                whatsapp_response, selected_language, EasyChatTranslationCache)

        if 'bot_id' in whatsapp_response:
            bot_id = whatsapp_response['bot_id']

            default_bot_obj = Bot.objects.get(pk=int(DEFAULT_BOT_ID))
            profile_obj = Profile.objects.filter(
                user_id=str(mobile), bot=default_bot_obj)

            if profile_obj:
                save_data(profile_obj[0], {
                          "LAST_SELECTED_BOT": bot_id}, "None", "WhatsApp", bot_id, is_cache=True)

                save_data(profile_obj[0], {"bot_id": str(bot_id)},
                          "None", "WhatsApp", bot_id, is_cache=True)

            bot_obj = Bot.objects.get(pk=int(bot_id))

        user = Profile.objects.get(user_id=str(mobile), bot=bot_obj)
        # user.is_session_exp_msg_sent = False
        # user.save()

        logger.error("Bot Message: %s", str(
            whatsapp_response), extra=log_param)
    #   BOT RESPONSES: images, videos, cards, choices, recommendations
        message = whatsapp_response["response"]["text_response"]["text"]
        modes = whatsapp_response["response"]["text_response"]["modes"]
        # modes_param = whatsapp_response["response"]["text_response"]["modes_param"]
        recommendations = whatsapp_response["response"]["recommendations"]
        images = whatsapp_response["response"]["images"]
        videos = whatsapp_response["response"]["videos"]
        cards = whatsapp_response["response"]["cards"]
        choices = whatsapp_response["response"]["choices"]

        # Go Back Check
        is_go_back_enabled = False
        if "is_go_back_enabled" in whatsapp_response["response"]:
            is_go_back_enabled = whatsapp_response["response"]["is_go_back_enabled"]
            save_data(user, json_data={"is_go_back_enabled": is_go_back_enabled},
                      src="None", channel="WhatsApp", bot_id=BOT_ID, is_cache=True)

        REVERSE_WHATSAPP_MESSAGE_DICT = {}
        reverse_mapping_index = 0

    #   EMOJI NUMBERS: 1 to 9
        # emojized_numbers = [":one:", ":two:", ":three:", ":four:",
        #                     ":five:", ":six:", ":seven:", ":eight:", ":nine:"]

    #   CHOICES:
        choice_dict = {}
        choice_display_list = []

        try:
            last_identified_intent = whatsapp_response["response"]["last_identified_intent_name"]
        except Exception:
            last_identified_intent = ""

        logger.info('this is the last_identified_intent: %s',
                    last_identified_intent, extra=log_param)
        logger.error(choices, extra=log_param)
        for ind in range(len(choices)):
            if (("is_livechat" in modes and modes["is_livechat"] == "true") or last_identified_intent == 'Helpful' or last_identified_intent == 'Unhelpful' or last_identified_intent == "") and (choices[ind]["display"] == "Helpful" or choices[ind]["display"] == "Unhelpful"):
                continue
            choice_dict[choices[ind]["display"]
                        ] = response_copy["response"]["choices"][ind]["value"]
            choice_display_list.append(choices[ind]["display"])

        logger.info('choice dict: %s',
                    str(choice_dict), extra=log_param)

        choice_str = ""
        if choice_display_list != []:
            if whatsapp_response["response"]["is_flow_ended"]:
                choice_str += "\n\n"
            # else:
            #     choice_str += "\n\nSelect one of the following :point_down::\n\n"
            for index in range(len(choice_display_list)):
                REVERSE_WHATSAPP_MESSAGE_DICT[str(
                    index + 1)] = str(choice_dict[choice_display_list[index]])
                choice_str += "Enter *" + \
                    str(index + 1) + "* :point_right:  " + \
                    str(choice_display_list[index]) + "\n\n"
            choice_str = get_emojized_message(choice_str) + "\n\n\n"
            reverse_mapping_index = len(choice_display_list)

    #   RECOMMENDATIONS:
        recommendation_str = ""
        if recommendations != []:
            if whatsapp_response["response"]["is_flow_ended"]:
                recommendation_str += "\n\n"
            # else:
            #     recommendation_str += "\n\nSelect one of the following :\n\n"
            if choice_str != "":
                for index in range(len(recommendations)):
                    rec_name = recommendations[index]
                    if recommendations[index]['name']:
                        rec_name = recommendations[index]['name']

                    if index % 10 == 0:
                        recommendation_str += "$$$"
                    REVERSE_WHATSAPP_MESSAGE_DICT[str(
                        reverse_mapping_index + index + 1)] = str(response_copy["response"]["recommendations"][index])
                    recommendation_str += "Enter *" + \
                        str(reverse_mapping_index + index + 1) + \
                        "* :point_right:  " + str(rec_name) + "\n\n"
                if is_go_back_enabled:
                    REVERSE_WHATSAPP_MESSAGE_DICT[str(
                        reverse_mapping_index + len(recommendations) + 1)] = "Go Back"
                    recommendation_str += "Enter *" + \
                        str(reverse_mapping_index + len(recommendations) + 1) + \
                        "* :point_right:  Go Back \n\n"

            else:
                for index in range(len(recommendations)):
                    rec_name = recommendations[index]
                    if isinstance(rec_name, dict):
                        rec_name = rec_name["name"]

                    if index % 10 == 0:
                        recommendation_str += "$$$"
                    REVERSE_WHATSAPP_MESSAGE_DICT[str(
                        index + 1)] = str(response_copy["response"]["recommendations"][index])
                    recommendation_str += "Enter *" + \
                        str(index + 1) + "* :point_right:  " + \
                        str(rec_name) + "\n\n"

                if is_go_back_enabled:
                    REVERSE_WHATSAPP_MESSAGE_DICT[str(
                        len(recommendations) + 1)] = "Go Back"
                    recommendation_str += "Enter *" + \
                        str(len(recommendations) + 1) + \
                        "* :point_right:  Go Back \n\n"

            recommendation_str = get_emojized_message(recommendation_str)
        else:
            if is_go_back_enabled:
                le = len(recommendations)
                if le == 0:
                    le = len(choice_display_list)
                REVERSE_WHATSAPP_MESSAGE_DICT[str(le + 1)] = "Go Back"
                recommendation_str += "Enter *" + \
                    str(le + 1) + "* :point_right:  Go Back \n\n"
                recommendation_str = get_emojized_message(recommendation_str)

    #   TEXT FORMATTING AND EMOJIZING:
        # message = message.replace("*"," • ")
        message = html_tags_formatter(message)
        message = unicode_formatter(message)
        message = get_emojized_message(message)
        logger.info("Bot Message: %s", str(message), extra=log_param)

    #   RESPONSE MODES:

        # 1. Regular single text:
        for small_message in message.split("$$$"):
            small_message = html_list_formatter(small_message)
            if small_message != "":
                if "http://" in small_message or "https://" in small_message:
                    small_message = youtube_link_formatter(small_message)
                    send_status = sendWhatsAppTextMessage(
                        API_KEY, small_message, mobile, preview_url=True)
                else:
                    send_status = sendWhatsAppTextMessage(
                        API_KEY, small_message, mobile, preview_url=False)
                time.sleep(0.05)

    #   SENDING CARDS, IMAGES, VIDEOS:
        logger.info("Cards: %s", str(cards), extra=log_param)
        logger.info("Images: %s", str(images), extra=log_param)
        logger.info("Videos: %s", str(videos), extra=log_param)

        if len(cards) > 0:
            # Cards with documnet links:  Use 'card_with_document:true' in modes
            if "card_with_document" in modes.keys() and modes["card_with_document"] == "true":
                API_KEY = GET_API_KEY(rm_username, rm_password)
                logger.info("Inside Cards with documents", extra=log_param)
                for card in cards:
                    doc_caption = str(card["title"])
                    doc_url = str(card["link"])
                    logger.info("DOCUMENT NAME: %s", str(
                        doc_caption), extra=log_param)
                    logger.info("DOCUMENT URL: %s", str(
                        doc_url), extra=log_param)
                    try:
                        logger.info("API KEY AVAILABLE: %s",
                                    str(API_KEY), extra=log_param)
                        send_status = sendWhatsAppMediaMessage(
                            API_KEY, "document", str(doc_url), mobile, caption=str(doc_caption))
                        logger.info("Is Card sent: %s", str(
                            send_status), extra=log_param)
                    except Exception as E:
                        logger.error("Cannot send card with document: %s", str(
                            E), extra=log_param)
            else:
                for card in cards:
                    logger.info("Inside Regular Card", extra=log_param)
                    title = str(card["title"])
                    content = str("\n" + card["content"] + "\n")
                    image_url = str(card["img_url"])
                    redirect_url = youtube_link_formatter(str(card["link"]))
                    caption = "*" + title + "* " + content + " " + redirect_url
                    if image_url != "":
                        logger.info("Card Image available", extra=log_param)
                        send_status = sendWhatsAppMediaMessage(
                            API_KEY, 'image', str(image_url), mobile, caption=caption)
                        logger.info("Is Card with image sent: %s",
                                    str(send_status), extra=log_param)
                    else:
                        send_status = sendWhatsAppTextMessage(
                            API_KEY, get_emojized_message(caption), mobile, preview_url=True)
                        logger.info("Is Card with link sent: %s",
                                    str(send_status), extra=log_param)

        if len(videos) > 0:
            for itr in range(len(videos)):
                logger.info("== Inside Videos ==", extra=log_param)
                if 'video_link' in str(videos[itr]):
                    video_url = youtube_link_formatter(
                        str(videos[itr]['video_link']))  # youtube links
                    send_status = sendWhatsAppTextMessage(
                        API_KEY, video_url, mobile, preview_url=True)
                    logger.info("Is Video sent: %s", str(
                        send_status), extra=log_param)
                else:
                    video_url = youtube_link_formatter(
                        str(videos[itr]))  # youtube links
                    send_status = sendWhatsAppTextMessage(
                        API_KEY, video_url, mobile, preview_url=True)
                    logger.info("Is Video sent: %s", str(
                        send_status), extra=log_param)
        if len(images) > 0:
            logger.info("== Inside Images ==", extra=log_param)
            for itr in range(len(images)):
                if 'content' in str(images[itr]):
                    logger.info("== Image with caption ==", extra=log_param)
                    send_status = sendWhatsAppMediaMessage(API_KEY, 'image', str(
                        images[itr]["img_url"]), mobile, caption=str(images[itr]['content']))
                    logger.info("Is Image sent: %s", str(
                        send_status), extra=log_param)
                else:
                    logger.info("== Image without caption ==")
                    send_status = sendWhatsAppMediaMessage(
                        API_KEY, 'image', str(images[itr]), mobile, caption=None)
                    logger.info("Is Image sent: %s", str(
                        send_status), extra=log_param)

    #   SENDING CHOICES AND RECOMMENDATIONS BOTH:
        if len(choice_str) > 0 and len(recommendation_str) > 0:
            mixed_choice = choice_str + "" + recommendation_str
            time.sleep(0.05)
            send_status = sendWhatsAppTextMessage(
                API_KEY, mixed_choice.replace("\n\n\n", "").replace("$$$", ""), mobile)
            logger.info("Is Mixed Choices sent: %s",
                        str(send_status), extra=log_param)
            choice_str = ""
            recommendation_str = ""

    #       SENDING CHOICES:
        if len(choice_str) > 0:
            time.sleep(0.05)
            send_status = sendWhatsAppTextMessage(API_KEY, choice_str, mobile)
            logger.info("Is choices sent: %s", str(
                send_status), extra=log_param)

    #   SENDING RECOMMENDATIONS:
        if len(recommendation_str) > 0:
            if "$$$" in recommendation_str:
                for bubble in recommendation_str.split("$$$"):
                    time.sleep(0.05)
                    send_status = sendWhatsAppTextMessage(
                        API_KEY, bubble, mobile)
                    logger.info("Is recommendations sent: %s",
                                str(send_status), extra=log_param)
            else:
                time.sleep(0.05)
                send_status = sendWhatsAppTextMessage(
                    API_KEY, recommendation_str, mobile)
                logger.info("Is recommendations sent: %s",
                            str(send_status), extra=log_param)

    #   SENDING LIVECHAT NOTIFICATION:
        # if "is_livechat" in modes and modes["is_livechat"] == "true":
        #     logger.error("INSIDE LIVECHAT NOTIFICATION", extra=log_param)
        #     bot_obj = Bot.objects.get(pk=int(BOT_ID))
        #     livechat_notification = create_and_enable_livechat(mobile, "WhatsApp", bot_obj, message)
        #     logger.error("LIVECHAT NOTIFICATION: %s", str(livechat_notification), extra=log_param)
        #     if livechat_notification != "":
        #         sendWhatsAppTextMessage(API_KEY, livechat_notification, str(mobile))

        if change_language_response_required(sender, BOT_ID, bot_obj):
            language_str, REVERSE_WHATSAPP_MESSAGE_DICT = get_language_change_response(
                BOT_ID, REVERSE_WHATSAPP_MESSAGE_DICT)

            if language_str != "":
                language_str = get_emojized_message(language_str)
                send_status = sendWhatsAppTextMessage(
                    API_KEY, language_str, mobile)
                logger.info("Is change language response sent: %s",
                            str(send_status), extra=log_param)

                save_data(user, json_data={"CHANGE_LANGUAGE_TRIGGERED": True},
                          src="None", channel="WhatsApp", bot_id="61", is_cache=True)

        logger.info("REVERSE_WHATSAPP_MESSAGE_DICT: %s", str(
            REVERSE_WHATSAPP_MESSAGE_DICT), extra=log_param)
        save_data(user, json_data={"REVERSE_WHATSAPP_MESSAGE_DICT": REVERSE_WHATSAPP_MESSAGE_DICT},
                  src="None", channel="WhatsApp", bot_id="61", is_cache=True)

        response["status_code"] = 200
        response["status_message"] = "Request processed successfully."
        logger.info("RouteMobileCallBack: %s", str(response), extra=log_param)
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(e) + str(exc_tb.tb_lineno)
        logger.error("RouteMobileCallBack: %s at %s", str(e),
                     str(exc_tb.tb_lineno), extra=log_param)
        return response
