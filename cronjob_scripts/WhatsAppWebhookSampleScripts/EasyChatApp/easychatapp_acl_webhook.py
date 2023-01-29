from EasyChatApp.utils import *
from EasyChatApp.models import *
from LiveChatApp.models import *
from EasyChatApp.utils_bot import process_response_based_on_language
from LiveChatApp.utils import *
from django.conf import settings
import emoji
import time
import json
import sys
import requests
import http.client
import mimetypes
import datetime
from bs4 import BeautifulSoup
from django.utils import timezone as tz
import urllib
import re

log_param = {'AppName': 'EasyChat', 'user_id': 'None',
             'source': 'None', 'channel': 'WhatsApp', 'bot_id': 'None'}

# ========================== TEXT FORMATTING FUNCTIONS =========================


def youtube_link_formatter(message):
    if "https://www.youtube.com" in message:
        message = message.replace(
            "embed/", "").replace("www.youtube.com", "youtu.be")
    return message


def html_list_formatter(sent):
    try:
        logger.info("---Html list string found---", extra=log_param)
        list_strings = []
        ul_end_position = 0
        ol_end_position = 0
        if "<ul>" in sent:
            for i in range(sent.count("<ul>")):
                list_strings_dict = {}
                ul_position = sent.find("<ul>", ul_end_position)
                ul_end_position = sent.find("</ul>", ul_position)
                list_str = sent[ul_position:ul_end_position+5]
                logger.info("HTML LIST STRING "+str(i+1)+": %s",
                            str(list_str), extra=log_param)
                list_str1 = list_str.replace("<ul>", "").replace(
                    "</ul>", "").replace("<li>", "")
                items = list_str1.split("</li>")
                items[-2] = items[-2]+"<br><br>"
                formatted_list_str = ""
                for item in items:
                    if item.strip() != "":
                        formatted_list_str += "\n\n- "+item.strip()+"\n"
                sent = sent.replace(list_str, formatted_list_str).replace(
                    "<br>", "\n")+"\n"
                sent = sent.strip()
                logger.info("---Html list string formatted---",
                            extra=log_param)
        if "<ol>" in sent:
            # print("yes ol")
            for i in range(sent.count("<ol>")):
                list_strings_dict = {}
                ol_position = sent.find("<ol>", ol_end_position)
                ol_end_position = sent.find("</ol>", ol_position)
                list_str = sent[ol_position:ol_end_position+5]
                logger.info("HTML LIST STRING "+str(i+1)+": %s",
                            str(list_str), extra=log_param)
                list_str1 = list_str.replace("<li>", "").replace(
                    "<ol>", "").replace("</ol>", "")
                items = list_str1.split("</li>")
                items[-2] = items[-2]+"<br><br>"
                formatted_list_str = ""
                for j, item in enumerate(items[:-1]):
                    if item.strip() != "":
                        formatted_list_str += "\n"+str(j+1)+". "+item.strip()
                sent = sent.replace(list_str, formatted_list_str)
                sent = sent.strip().replace("<br>", "\n")
                logger.info("---Html list string formatted---",
                            extra=log_param)
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Failed to format html list string: %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
        # print("Failed to format html list string: %s", str(E))
    return sent


def html_tags_formatter(message):
    tags = {
        "<br>": "\n", "<br/>": "\n", "<br />": "\n",
        "<b>": " *", "</b>": "* ",
        "<em>": "_", "</em>": "_",
        "<i>": "_", "</i>": "_",
        "<strong>": " *", "</strong>": "* ",
        "<p>": "", "</p>": ""
    }
    for tag in tags:
        message = message.replace(tag, tags[tag])
        message = message.replace(tag+"<a", "<a")
        message = message.replace("</a>"+tag, "</a>")
        message = message.replace("</a>\n"+tag, "</a>")

    if "</a>" in message:
        end = ""
        if "tel:" in message:
            end = ""
        message = message.replace("mailto:", "").replace("tel:", "")
        soup = BeautifulSoup(message, "html.parser")
        for link in soup.findAll('a'):
            href = link.get('href')
            link_name = link.string
            link_element = message[message.find(
                "<a"):message.find("</a>")]+"</a>"
            if link_name.replace("http://", "").replace("https://", "").strip() == href.replace("http://", "").replace("https://", "").strip():
                message = message.replace(link_element, href+end)
            else:
                message = message.replace(link_element, link_name+" "+href+end)
    return message


def unicode_formatter(message):
    unicodes = {"&nbsp;": " ", "&#39;": "\'", "&rsquo;": "\'", "&amp;": "&", "&hellip;": "...", "&quot;": "\"", "\\n": "\n",
                "\\u2019": "'", "\\u2013": "'", "\\u2018": "'", "&lt;": "<", "&gt;": ">"}
    for code in unicodes:
        message = message.replace(code, unicodes[code])
    return message


def get_hindi_to_english_number(message):
    hindi_numbers_map = {"१": "1", "२": "2", "३": "3", "४": "4",
                         "५": "5", "६": "6", "७": "7", "८": "8", "९": "9"}
    for num in hindi_numbers_map:
        message = message.replace(num, hindi_numbers_map[num])
    return message


def get_emojized_message(message):
    return emoji.emojize(message, language='alias')


def get_demojized_message(message):
    try:
        import emoji
        return emoji.demojize(message)
    except Exception as e:
        return ""

# ====================== end ===================================================

# ====================== Utils =================================================
# Calculate difference b/w datetime objects


def get_time_delta(date_str1, date_str2):
    delta_obj = {"minutes": 0.0, "hours": 0.0}
    try:
        from datetime import date, datetime
        if "." in date_str1:
            date_str1 = str(date_str1).split(".")[0]
        if "." in date_str2:
            date_str2 = str(date_str2).split(".")[0]
        date_str1 = datetime.strptime(date_str1, "%Y-%m-%d %H:%M:%S")
        date_str2 = datetime.strptime(date_str2, "%Y-%m-%d %H:%M:%S")
        delta = date_str2 - date_str1  # 2nd date is greater
        duration_in_s = delta.total_seconds()
        delta_obj = {
            "seconds": duration_in_s,
            # divmod(duration_in_s, 60)[0],
            "minutes": round(duration_in_s/60, 1),
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


def save_file_from_remote_server_to_local(remote_url, local_path):
    is_saved = False
    try:
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
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_file_from_remote_server_to_local: %s at %s", str(
            E), str(exc_tb.tb_lineno), extra=log_param)
    return is_saved


#   GET WMESSAGE FROM REVERSE MAPPING
def get_message_from_reverse_whatsapp_mapping(user_message, mobile):
    logger.info(" === Inside Reverse Message mapping === ",  extra=log_param)
    message = None
    try:
        is_suggestion = False
        user = Profile.objects.get(user_id=str(mobile))
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
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_message_from_reverse_whatsapp_mapping: %s",
                     str(E),  extra=log_param)
    return message, is_suggestion


#   Check Intent Level Feedback:
def check_intent_level_feedback(mobile, user_message):
    logger.info(
        " === Inside check_intent_level_feedback mapping === ",  extra=log_param)
    is_intent_feedback_asked = False
    message = user_message
    feedback_type = 0
    try:
        is_suggestion = False
        user = Profile.objects.get(user_id=str(mobile))
        data_obj = Data.objects.filter(
            user=user, variable="is_intent_feedback_asked")[0]
        is_intent_feedback_asked = json.loads(str(data_obj.get_value()))
        logger.info("is_intent_feedback_asked: %s", str(
            is_intent_feedback_asked), extra=log_param)
        if user_message != None and user_message.strip() != "" and is_intent_feedback_asked == True:
            if user_message.lower() == "helpful":
                feedback_type = 1
            elif user_message.lower() == "unhelpful":
                feedback_type = -1
            if feedback_type in [1, -1]:
                logger.info("feedback_type: %s", str(
                    feedback_type), extra=log_param)
                mis_obj = MISDashboard.objects.filter(
                    user_id=user.user_id).latest('id')
                mis_obj.feedback_info = json.dumps(
                    {"is_helpful": int(feedback_type), "comments": ""})
                mis_obj.is_helpful_field = feedback_type
                mis_obj.save()
                logger.info("Intent level feedback saved: %s",
                            str(feedback_type), extra=log_param)
                feedback_dict = {"is_intent_feedback_asked": False}
                save_data(user, json_data=feedback_dict,  src="None",
                          channel="WhatsApp", bot_id=mis_obj.bot.id,  is_cache=True)
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_intent_level_feedback: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return message


def change_language_response_required(sender, bot_id):
    try:
        bot_obj = Bot.objects.get(pk=int(bot_id))
        channel = Channel.objects.filter(name="WhatsApp")[0]
        # bot_channel_obj = BotChannel.objects.filter(
        #     bot=bot_obj, channel=channel)[0]
        languages_supported = bot_obj.languages_supported.all()
        profile_obj = Profile.objects.get(user_id=str(sender))

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


def is_change_language_triggered(sender):
    try:
        user = Profile.objects.get(user_id=sender)
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
        languages_supported = bot_obj.languages_supported.all()

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
# ====================== end ===================================================

# ====================== Vendor Specifics ======================================


def get_whatsapp_file_attachment(userid, password, attachment_packet):
    attachment_path = None
    try:
        from urllib.parse import urlparse
        from urllib.parse import parse_qs

        remote_url = attachment_packet["url"]
        mime_type = attachment_packet["mime_type"]
        path = urlparse(remote_url).path

        filename = path.split('/')[-1]
        caption = attachment_packet["caption"]
        if caption != "None" and caption != None and caption != "":
            filename = caption
        if filename.split('.')[-1] == "unknown":
            ext = "."+mime_type.split("/")[-1]
            if mime_type in ["application/msword", "application/vnd.ms-pwerpoint", "application/vnd.ms-excel"]:
                if mime_type == "application/msword":
                    ext = ".doc"
                elif mime_type == "application/vnd.ms-pwerpoint":
                    ext = ".ppt"
                elif mime_type == "application/vnd.ms-excel":
                    ext = ".xls"
            filename = filename.split('.')[0] + ext
        filename = filename.replace(" ", "-")
        if not os.path.exists(settings.MEDIA_ROOT + 'WhatsAppMedia'):
            os.makedirs(settings.MEDIA_ROOT + 'WhatsAppMedia')
        file_path = settings.MEDIA_ROOT+"WhatsAppMedia/"+filename
        file_path_rel = "files/WhatsAppMedia/"+filename
        save_file_from_remote_server_to_local(remote_url, file_path)
        attachment_path = settings.EASYCHAT_HOST_URL+"/"+file_path_rel
        logger.info("is_whatsapp_file_attachment: Filename %s",
                    filename, extra=log_param)
        logger.info("is_whatsapp_file_attachment: Filepath %s",
                    attachment_path, extra=log_param)
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_file_from_remote_server_to_local: %s at %s", str(
            E), str(exc_tb.tb_lineno), extra=log_param)
    return attachment_path


#   WHATSAPP SEND TEXT MESSAGE API:
def sendWhatsAppTextMessage(userid, password, acl_api_url, bot_mobile_number, message, phone_number, preview_url=False):
    try:
        logger.info("=== Inside Send WA Text Message API ===", extra=log_param)

        url = acl_api_url

        headers = {
            'Content-Type': 'application/json',
            'User':  userid,
            'Pass': password
        }

        payload = {
            "messages": [
                {
                    "sender": bot_mobile_number,
                    "to": phone_number,
                    "transaction_id": "11343434",
                    "channel": "WA",
                    "type": "text",
                    "text": {
                        "content": message,
                        "previewFirstUrl": preview_url
                    }
                }
            ],
            "responseType": "json"
        }
        logger.info("Send WA Text API URL: %s", url, extra=log_param)
        logger.info("Send WA Text API Request: %s",
                    str(payload), extra=log_param)
        r = requests.request("POST", url, headers=headers,
                             data=json.dumps(payload), timeout=20, verify=False)
        logger.info("Send WA Text API Response: %s",
                    str(r.text), extra=log_param)
        if str(r.status_code) == "200":
            content = json.loads(r.text)
            if "success" in content and content["success"] == "true":
                logger.info("Text message sent succesfully", extra=log_param)
                return True
            else:
                logger.error("Failed to Send Text Message.", extra=log_param)
                return False
        else:
            logger.error("Failed to Send Text Message.", extra=log_param)
            return False
    except requests.Timeout as RT:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(RT) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppText API Timeout error: %s at %s",
                     str(RT), str(exc_tb.tb_lineno), extra=log_param)
        return False
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(E) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppText API Failed: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return False


# WHATSAPP SEND MEDIA MESSAGE API:
def sendWhatsAppMediaMessage(userid, password, acl_api_url, bot_mobile_number, media_type, media_url, phone_number, caption=None):
    try:
        logger.info("=== Inside Send WA Media Message API ===",
                    extra=log_param)
        logger.info("Media Type: %s", media_type, extra=log_param)

        url = acl_api_url

        if caption == None:
            caption = ""

        contentType = mimetypes.guess_type(media_url)[0]

        payload = {
            "messages": [
                {
                    "sender": bot_mobile_number,
                    "to": phone_number,
                    "transactionId": "11343434",
                    "channel": "WA",
                    "type": "media",
                    "media": {
                            "contentType": contentType,
                            "caption": caption,
                            "mediaUrl": media_url
                    }
                }
            ],
            "responseType": "json"
        }

        headers = {
            'Content-Type': 'application/json',
            'User': userid,
            'Pass': password
        }
        logger.info("Send WA MEDIA API URL: %s", url, extra=log_param)
        logger.info("Send WA "+media_type.upper() +
                    " API request: %s", str(payload), extra=log_param)
        r = requests.request("POST", url, headers=headers,
                             data=json.dumps(payload), timeout=20)
        logger.info("Send WA "+media_type.upper() +
                    " API Response: %s", str(r.text), extra=log_param)
        if str(r.status_code) == "200":
            content = json.loads(r.text)
            if "success" in content and content["success"] == "true":
                logger.info(media_type.upper() +
                            "Text message sent succesfully", extra=log_param)
                return True
            else:
                logger.error("Failed to Send "+media_type.upper() +
                             " Message.", extra=log_param)
                return False
        else:
            logger.error("Failed to send "+media_type.upper() +
                         " message", extra=log_param)
            return False
    except requests.Timeout as RT:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(RT) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppMediaMessage Timeout error: %s at %s", str(
            RT), str(exc_tb.tb_lineno), extra=log_param)
        return False
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(E) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppMediaMessage Failed: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return False


#   MAIN FUNCTION
def whatsapp_webhook(request_packet):
    log_param = {'AppName': 'EasyChat', 'user_id': 'None',
                 'source': 'None', 'channel': 'WhatsApp', 'bot_id': 'None'}
    send_status = False
    response = {}
    response["status_code"] = 500
    response["status_message"] = "Internal server issues"
    response["mobile_number"] = "919833330151"
    try:

        #   ACL DELIVERY STATUS:
        if "delivery_status" in request_packet.keys() or "del_status" in request_packet.keys():
            logger.info("INCOMING_DELIVERY_PACKET WA WEBHOOK: %s",
                        str(request_packet), extra=log_param)
            try:
                response["mobile_number"] = request_packet["statuses"][0]["recipient_id"]
            except:
                pass
            response["status_code"] = 200
            response["status_message"] = "Request processed successfully."
            return response

    #   WEBHOOK INIT
        logger.info("INSIDE ACL WA WEBHOOK", extra=log_param)
        logger.info("ACL WA WEBHOOK INCOMING_REQUEST_PACKET: %s",
                    str(request_packet), extra=log_param)

    # == CREDENTIALS AND DETAILS: ==============================================
        acl_username = 'icicidwts'
        acl_password = 'icicidwts2'
        acl_api_url = 'https://push.aclwhatsapp.com/pull-platform-receiver/wa/messages'
        BOT_ID = "11"

        try:
            sender = remo_html_from_string(
                str(request_packet["message"]["from"]))
            receiver = remo_html_from_string(
                str(request_packet["message"]["to"]))
            message_type = request_packet["message"]["type"]
        except:
            sender = remo_html_from_string(str(request_packet["MSISDN"]))
            receiver = remo_html_from_string(str(request_packet["WHATSAPPNO"]))
            message_type = "text"
            try:
                if "MEDIA_URL" in request_packet:
                    message_type = "not_text"
            except:
                pass

        logger.info("Message Type: %s", message_type, extra=log_param)
        response["mobile_number"] = sender
        log_param["user_id"] = sender
        log_param["bot_id"] = BOT_ID
        logger.info("Sender: %s", str(sender), extra=log_param)
        logger.info("Reciever: %s", str(receiver), extra=log_param)
    # ==========================================================================

    #   GLOBAL VARIABLES:
        RESET_KEYWORDS = ["reset", "exit"]

    #   CHECK FOR NEW USER:
        first_time_user = "false"
        check_user = Profile.objects.filter(user_id=str(sender))
        if check_user.count() == 0:
            first_time_user = "true"
        logger.info("Is New User: %s", first_time_user, extra=log_param)

    #   CHECK USER MESSAGE TYPE: text, image, document, voice, location
        # message_type = request_packet["message"]["type"]
        # logger.info("Message Type: %s", message_type, extra=log_param)

    #   GLOBAL VARIABLES:
        main_menu_intent_name = "Hi"
        sticky_recommendations = ["Main Menu"]
        sticky_choices = []
        # Single new line after each option
        is_compact_recommendations_choices = True
        max_choices_recommendations_bubble_size = 12
        choices_recommendations_header = "Please enter the *option number* from the below option(s):\n\n"
        choices_recommendations_footer = "\n_*Please type your query (if it is not mentioned in the above options)._\n\n✉ to us on helpdesk@icicidirect.com\n\n📞 Customer Care:\nhttps://www.icicidirect.com/cuscarenos.htm"
        max_cards_bubble_size = 20

    #   GET USER ATTACHMENTS AND MESSAGES:
        is_location = True
        is_attachement = True
        message = None
        filepath = None
        is_suggestion = False
        file_caption = None
        is_go_back_enabled = False
        REVERSE_WHATSAPP_MESSAGE_DICT = {}
        is_feedback_required = False
        reverse_mapping_index = 0
        if message_type == "text":
            is_attachement = False
            is_location = False
        if is_attachement:
            # image, document, voice
            attachment_packet = request_packet["message"]["type"]
            attachment_type = message_type
            logger.info(" Whatsapp attachment packet: %s",
                        str(attachment_packet), extra=log_param)
            if attachment_type != "document" and "caption" in attachment_packet:
                file_caption = attachment_packet["caption"]
            filepath = get_whatsapp_file_attachment(
                acl_username, acl_password, attachment_packet)
            message = "attachment"
        else:
            #   else get user Message:
            try:
                message = request_packet["message"][message_type]["body"]
            except:
                message = request_packet["BODYTXT"]

            try:
                import urllib.parse
                message = urllib.parse.unquote(message)
            except:
                pass

            reverse_message = None
            reverse_message, is_suggestion = get_message_from_reverse_whatsapp_mapping(
                message, sender)
            if reverse_message != None:
                message = reverse_message
            else:
                is_suggestion = False

            # Intent Level Feedback Check
            message = check_intent_level_feedback(sender, message)

            # Go Back Check
            is_go_back_enabled = False
            if first_time_user == "false":
                user = Profile.objects.get(user_id=str(sender))
                check_go_back_enabled = Data.objects.filter(
                    user=user, variable="is_go_back_enabled")

                if len(check_go_back_enabled) > 0 and str(check_go_back_enabled[0].value) == 'true':
                    is_go_back_enabled = True
            if first_time_user == "true":
                message = "Change language"
        user_query = message
        logger.info("User Message: %s", str(message), extra=log_param)

    #   GET PREVIOUS BOT ID
        user_obj = Profile.objects.filter(user_id=str(sender))
        if user_obj:
            data_obj = Data.objects.filter(user=user_obj, variable="bot_id")
            if data_obj:
                BOT_ID = int(data_obj[0].get_value().replace('"', ""))
                logger.info('Bot id is : %s', str(BOT_ID), extra=log_param)

    #   CHECK IF CHANGE LANGUAGE WAS TRIGGERED
        if is_change_language_triggered(sender):
            try:
                lang_obj = Language.objects.get(lang=message)
                profile_obj = Profile.objects.get(user_id=str(sender))
                profile_obj.selected_language = lang_obj
                profile_obj.save()
                text_message = "You have selected " + \
                    str(lang_obj.display) + \
                    ". If you want to change your language again please type"
                text_message = get_translated_text(
                    text_message, lang_obj.lang, EasyChatTranslationCache)
                text_message = text_message + ' "Change Language"'
                send_status = sendWhatsAppTextMessage(acl_username, acl_password, acl_api_url, str(
                    receiver), text_message, str(sender), preview_url=False)
                response["status_code"] = 200
                response["status_message"] = "Request processed successfully."
                return response
            except Exception as e:
                logger.error("is_change_language_triggered: %s at %s",
                             str(e), extra=log_param)

    #   CHECK IF CHANGE LANGUAGE IS CALLED
        if isinstance(message, str) and message.lower().strip() == "change language":
            REVERSE_WHATSAPP_MESSAGE_DICT = {}
            language_str, REVERSE_WHATSAPP_MESSAGE_DICT = get_language_change_response(
                BOT_ID, REVERSE_WHATSAPP_MESSAGE_DICT)
            if language_str != "":
                language_str = get_emojized_message(language_str)
                send_status = sendWhatsAppTextMessage(acl_username, acl_password, acl_api_url, str(
                    receiver), language_str, str(sender), preview_url=False)
                logger.info("Is change language response sent: %s",
                            str(send_status), extra=log_param)

                user = set_user(str(sender), message,
                                "None", "WhatsApp", BOT_ID)
                save_data(user, json_data={"CHANGE_LANGUAGE_TRIGGERED": True},
                          src="None", channel="WhatsApp", bot_id=BOT_ID, is_cache=True)

                logger.info("REVERSE_WHATSAPP_MESSAGE_DICT: %s", str(
                    REVERSE_WHATSAPP_MESSAGE_DICT), extra=log_param)
                save_data(user, json_data={"REVERSE_WHATSAPP_MESSAGE_DICT": REVERSE_WHATSAPP_MESSAGE_DICT},
                          src="None", channel="WhatsApp", bot_id=BOT_ID, is_cache=True)
                response["status_code"] = 200
                response["status_message"] = "Request processed successfully."
                return response

    #   GET LANGUAGE SELECTED BY USER
        try:
            selected_language = Profile.objects.get(
                user_id=str(sender)).selected_language

            if not selected_language:
                selected_language = "en"
            else:
                selected_language = selected_language.lang
                languages_supported = Bot.objects.get(
                    pk=int(BOT_ID)).languages_supported
                languages_supported = languages_supported.filter(
                    lang=selected_language)

                if not languages_supported:
                    selected_language = "en"
        except Exception:
            selected_language = 'en'

        mobile = str(sender)  # User mobile
        waNumber = str(receiver)  # Bot Whatsapp Number

    #   WEBHOOK EXECUTE FUNCTION CALL
        channel_params = {"user_mobile": mobile, "bot_wa_number": waNumber, "whatsapp_file_attachment": filepath,
                          "whatsapp_file_caption": file_caption, "is_new_user": first_time_user, "QueryChannel": "WhatsApp", "is_go_back_enabled": is_go_back_enabled, "entered_suggestion": is_suggestion}
        logger.info("ACLCallBack Channel params:  %s",
                    str(channel_params), extra=log_param)
        whatsapp_response = execute_query(mobile, BOT_ID, "uat", str(message), selected_language, "WhatsApp", json.dumps(
            channel_params), message, Config, Channel, Bot, TimeSpentByUser, Feedback, MISDashboard, Data, Intent, FlowAnalytics, Tree, FormAssist)
        logger.info("ACLCallBack execute_query response %s",
                    str(whatsapp_response), extra=log_param)

        if selected_language != "en":
            whatsapp_response = process_response_based_on_language(
                whatsapp_response, selected_language, EasyChatTranslationCache)

        #   USER OBJECT:
        user = Profile.objects.get(user_id=str(mobile))
        # user.is_session_exp_msg_sent = False
        # user.save()

    #   Check LiveChat:
        if "is_livechat" in whatsapp_response and whatsapp_response["is_livechat"] == "true":
            if message.lower() == "end chat":
                livechat_notification = "LiveChat Session has ended."
                send_status = sendWhatsAppTextMessage(
                    acl_username, acl_password, acl_api_url, waNumber, livechat_notification, str(mobile), preview_url=False)
            return whatsapp_response

    #   Auto Trigger Last Intent after Authentication:
        try:
            if whatsapp_response != {}:
                if str(whatsapp_response['status_code']) == '200' and whatsapp_response['response'] != {}:
                    if 'modes' in whatsapp_response['response']["text_response"] and whatsapp_response['response']["text_response"]['modes'] != {}:
                        if 'auto_trigger_last_intent' in whatsapp_response['response']["text_response"]['modes'] and whatsapp_response['response']["text_response"]['modes']['auto_trigger_last_intent'] == 'true':
                            if 'last_identified_intent_name' in whatsapp_response['response'] and whatsapp_response['response']['last_identified_intent_name'] != '':
                                message = whatsapp_response['response']['last_identified_intent_name']
                                whatsapp_response = execute_query(
                                    mobile, BOT_ID, "uat", message, "en", "WhatsApp", json.dumps(channel_params), message)
                                logger.info("ACLCallBack: execute_query after Auth response %s", str(
                                    whatsapp_response), extra=log_param)
        except Exception as E:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Cannot identify Last Intent: %s at %s",
                         str(E), str(exc_tb.tb_lineno), extra=log_param)

    #   BOT RESPONSES: images, videos, cards, choices, recommendations
        message = whatsapp_response["response"]["text_response"]["text"]
        modes = whatsapp_response["response"]["text_response"]["modes"]
        modes_param = whatsapp_response["response"]["text_response"]["modes_param"]
        recommendations = whatsapp_response["response"]["recommendations"]
        images = whatsapp_response["response"]["images"]
        videos = whatsapp_response["response"]["videos"]
        cards = whatsapp_response["response"]["cards"]
        choices = whatsapp_response["response"]["choices"]

    #   TEXT FORMATTING AND EMOJIZING:
        logger.info("Bot Message(Original): %s", str(message), extra=log_param)
        message = html_tags_formatter(message)
        message = unicode_formatter(message)
        message = get_emojized_message(message)
        choices_recommendations_header = get_emojized_message(
            unicode_formatter(html_tags_formatter(choices_recommendations_header)))
        choices_recommendations_footer = get_emojized_message(
            unicode_formatter(html_tags_formatter(choices_recommendations_footer)))
        logger.info("Bot Message(Formatted): %s",
                    str(message), extra=log_param)

        if message is None or message == "":
            message = "None"

    #   Modes & Modes Params Based Actions
        if "hide_bot_response" in modes.keys() and modes['hide_bot_response'] == "true":
            message = ""

    #	Go Back Check

        if "is_go_back_enabled" in whatsapp_response["response"]:
            is_go_back_enabled = whatsapp_response["response"]["is_go_back_enabled"]
            save_data(user, json_data={"is_go_back_enabled": is_go_back_enabled},
                      src="None", channel="WhatsApp", bot_id=BOT_ID, is_cache=True)

    #   Check FeedBack Required:
        if "is_feedback_required" in whatsapp_response["response"]:
            is_feedback_required = whatsapp_response["response"]["is_feedback_required"]

    #   EMOJI NUMBERS: 1 to 9
        emojized_numbers = [":one:", ":two:", ":three:", ":four:",
                            ":five:", ":six:", ":seven:", ":eight:", ":nine:"]

    #   Flow Ended Check:
        if whatsapp_response["response"]["is_flow_ended"]:
            if "last_identified_intent_name" in whatsapp_response and whatsapp_response["response"]["last_identified_intent_name"] != main_menu_intent_name:
                choices = choices + sticky_choices
                recommendations = recommendations + sticky_choices

    #   CHOICES:
        choice_dict = {}
        choice_display_list = []
        for choice in choices:
            if choice["display"] == "Helpful" or choice["display"] == "Unhelpful":
                continue
            choice_dict[choice["display"]] = choice["value"]
            choice_display_list.append(choice["display"])
        choice_str = ""
        if choice_display_list != []:
            # if whatsapp_response["response"]["is_flow_ended"]:
            #     choice_str += ""
            # else:
            #     choice_str += "\n\nSelect one of the following :point_down::\n\n"
            for index in range(len(choice_display_list)):
                if index % max_choices_recommendations_bubble_size == 0 and index != 0:
                    choice_str += "$$$"
                REVERSE_WHATSAPP_MESSAGE_DICT[str(
                    index+1)] = str(choice_dict[choice_display_list[index]])
                choice_str += "Enter *" + \
                    str(index+1)+"* :point_right:  " + \
                    str(choice_display_list[index])+"\n"
                if is_compact_recommendations_choices == False:
                    choice_str = +"\n"
            choice_str = get_emojized_message(choice_str)  # +"\n\n\n"
            choice_str = html_tags_formatter(choice_str)
            reverse_mapping_index = len(choice_display_list)
        logger.info("Choices: %s", str(choice_str), extra=log_param)

    #   RECOMMENDATIONS:
        recommendation_str = ""
        if recommendations != []:
            cleaned_recommendations = []
            for recm in recommendations:
                if isinstance(recm, dict) and "name" in recm:
                    cleaned_recommendations.append(recm["name"])
                else:
                    cleaned_recommendations.append(recm)
            recommendations = cleaned_recommendations
            # if whatsapp_response["response"]["is_flow_ended"]:
            #     recommendation_str += ""
            # else:
            #     recommendation_str += "\n\nSelect one of the following :\n\n"
            if choice_str != "":
                for index in range(len(recommendations)):
                    if index % max_choices_recommendations_bubble_size == 0:
                        recommendation_str += "$$$"
                    REVERSE_WHATSAPP_MESSAGE_DICT[str(
                        reverse_mapping_index+index+1)] = str(recommendations[index])
                    recommendation_str += "Enter *" + \
                        str(reverse_mapping_index+index+1) + \
                        "* :point_right:  "+str(recommendations[index])+"\n"
                    if is_compact_recommendations_choices == False:
                        recommendation_str = +"\n"
                if is_go_back_enabled:
                    REVERSE_WHATSAPP_MESSAGE_DICT[str(
                        reverse_mapping_index+len(recommendations)+1)] = "Go Back"
                    recommendation_str += "Enter *" + \
                        str(reverse_mapping_index+len(recommendations)+1) + \
                        "* :point_right:  Go Back"+"\n"
                    if is_compact_recommendations_choices == False:
                        recommendation_str = +"\n"

            else:
                for index in range(len(recommendations)):
                    if index % max_choices_recommendations_bubble_size == 0 and index != 0:
                        recommendation_str += "$$$"
                    REVERSE_WHATSAPP_MESSAGE_DICT[str(
                        index+1)] = str(recommendations[index])
                    recommendation_str += "Enter *" + \
                        str(index+1)+"* :point_right:  " + \
                        str(recommendations[index])+"\n"
                    if is_compact_recommendations_choices == False:
                        recommendation_str = +"\n"
                if is_go_back_enabled:
                    REVERSE_WHATSAPP_MESSAGE_DICT[str(
                        len(recommendations)+1)] = "Go Back"
                    recommendation_str += "Enter *" + \
                        str(len(recommendations)+1) + \
                        "* :point_right:  Go Back"+"\n"
                    if is_compact_recommendations_choices == False:
                        recommendation_str = +"\n"
            recommendation_str = get_emojized_message(recommendation_str)
        else:
            if is_go_back_enabled:
                le = len(recommendations)
                if le == 0:
                    le = len(choice_display_list)
                REVERSE_WHATSAPP_MESSAGE_DICT[str(le+1)] = "Go Back"
                recommendation_str += "Enter *" + \
                    str(le+1)+"* :point_right:  Go Back:"+"\n"
                if is_compact_recommendations_choices == False:
                    recommendation_str = +"\n"
                recommendation_str = get_emojized_message(recommendation_str)
        logger.info("Recommendations: %s", str(
            recommendation_str), extra=log_param)
        logger.info("Choices: %s", str(choice_str), extra=log_param)
        logger.info("Reverse Mapper: %s", str(
            REVERSE_WHATSAPP_MESSAGE_DICT), extra=log_param)

    #   RESPONSE MODES:
    #   1.SANDWICH CHOICES: sending choices in between to small texts in a single bubble:
        is_sandwich_choice = False  # is sandwich choice sent flag:
        if "is_sandwich_choice" in modes.keys() and modes['is_sandwich_choice'] == "true":
            choice_position = "1"  # 2nd position
            is_single_message = True
            is_sandwich_choice = True
        else:
            choice_position = ""
            is_single_message = False

    #   2.STICKY CHOICES: sending choices and message in same bubble.
        message_with_choice = False
        if "message_with_choice" in modes.keys() and modes["message_with_choice"] == "true":
            message_with_choice = True
        if recommendation_str == "" and choice_str == "":
            message_with_choice = False

    #   3. BOT LINK CARDS: sending cards containing urls/links
        if "card_for_links" in modes.keys() and modes["card_for_links"] == "true":
            card_text = ""
            for card in cards:
                redirect_url = str(
                    card["link"]) if card["link"] is not None else ""
                title = str(card["title"] if card["title"] is not None else "")
                card_text += " :point_right: *"+title+"* \n   "
                card_text += " :link: "+redirect_url+"$$$"
            message += get_emojized_message("$$$" + card_text)
            cards = []

    #   SEND SINGLE BUBBLE TEXT:
        final_text_message = ""
        for count, small_message in enumerate(message.split("$$$"), 0):
            if str(choice_position) != "" and str(choice_position) == str(count):
                # 1. Sandwich choices text:
                if len(choice_str) > 0 and len(recommendation_str) > 0:
                    final_text_message += choice_str + recommendation_str
                    choice_str = ""
                    recommendation_str = ""
                if len(choice_str) > 0:
                    final_text_message += choices_recommendations_header + \
                        choice_str + choices_recommendations_footer
                if len(recommendation_str) > 0:
                    final_text_message += choices_recommendations_header + \
                        recommendation_str + choices_recommendations_footer
                final_text_message += small_message + "$$$"
            else:
                final_text_message += small_message + "$$$"
        if is_single_message:
            final_text_message = final_text_message.replace("$$$", "")
            if final_text_message != "":
                if "http://" in final_text_message or "https://" in final_text_message:
                    final_text_message = youtube_link_formatter(
                        final_text_message)
                    send_status = sendWhatsAppTextMessage(
                        acl_username, acl_password, acl_api_url, waNumber, final_text_message, str(mobile), preview_url=True)
                    is_sandwich_choice = True
                else:
                    send_status = sendWhatsAppTextMessage(
                        acl_username, acl_password, acl_api_url, waNumber, final_text_message, str(mobile), preview_url=False)
                    is_sandwich_choice = True
                recommendation_str = ""
                choice_str = ""
        else:
            if message_with_choice == True:
                # 2. Sticky choices text:
                final_text_message = message.replace("$$$", "")
                if len(choice_display_list) > 0 and len(recommendations) > 0:
                    final_text_message = final_text_message.strip("\n") + "\n\n" + choices_recommendations_header + choice_str.replace(
                        "$$$",  "").strip("\n") + recommendation_str.replace("$$$", "").strip("\n") + choices_recommendations_footer
                    choice_display_list = []
                    recommendations = []
                    logger.info("Sticky choices + recommendations : %s",
                                str(final_text_message), extra=log_param)
                if len(choice_display_list) > 0:
                    final_text_message = final_text_message.strip(
                        "\n") + "\n\n" + choices_recommendations_header + choice_str.replace("$$$",  "").strip("\n") + choices_recommendations_footer
                    logger.info("Sticky choices: %s", str(
                        final_text_message), extra=log_param)

                if len(recommendations) > 0:
                    final_text_message = final_text_message.strip(
                        "\n") + "\n\n" + choices_recommendations_header + recommendation_str.replace("$$$", "").strip("\n") + choices_recommendations_footer
                    final_text_message = final_text_message.replace(
                        "\n\n\n", "\n")
                    logger.info("Sticky recommendations: %s", str(
                        final_text_message), extra=log_param)

                if "http://" in final_text_message or "https://" in final_text_message:
                    final_text_message = youtube_link_formatter(
                        final_text_message)
                    send_status = sendWhatsAppTextMessage(
                        acl_username, acl_password, acl_api_url, waNumber, final_text_message, str(mobile), preview_url=True)
                else:
                    send_status = sendWhatsAppTextMessage(
                        acl_username, acl_password, acl_api_url, waNumber, final_text_message, str(mobile), preview_url=False)
                recommendation_str = ""
                choice_str = ""
            else:
                # 3. Regular single text:
                logger.info("Regular Small Text: %s", str(
                    final_text_message), extra=log_param)
                for small_message in final_text_message.split("$$$"):
                    small_message = html_list_formatter(small_message)
                    if small_message != "":
                        if "http://" in small_message or "https://" in small_message:
                            small_message = youtube_link_formatter(
                                small_message)
                            send_status = sendWhatsAppTextMessage(
                                acl_username, acl_password, acl_api_url, waNumber, small_message, str(mobile), preview_url=True)
                        else:
                            send_status = sendWhatsAppTextMessage(
                                acl_username, acl_password, acl_api_url, waNumber, small_message, str(mobile), preview_url=False)
                        time.sleep(0.1)

    #   SENDING CARDS, IMAGES, VIDEOS:
        logger.info("Cards: %s", str(cards), extra=log_param)
        logger.info("Images: %s", str(images), extra=log_param)
        logger.info("Videos: %s", str(videos), extra=log_param)

        if len(cards) > 0:
            # Cards with documnet links:  Use 'card_with_document:true' in modes
            if "card_with_document" in modes.keys() and modes["card_with_document"] == "true":
                logger.info("Inside Cards with documents", extra=log_param)
                for card in cards:
                    doc_caption = str(card["title"])
                    doc_url = str(card["link"])
                    logger.info("DOCUMENT NAME: %s", str(
                        doc_caption), extra=log_param)
                    logger.info("DOCUMENT URL: %s", str(
                        doc_url), extra=log_param)
                    try:
                        send_status = sendWhatsAppMediaMessage(
                            acl_username, acl_password, acl_api_url, waNumber, "document", str(doc_url), str(mobile), caption=None)
                        logger.info("Is Card sent: %s", str(
                            send_status), extra=log_param)
                    except Exception as E:
                        logger.error("Cannot send card with document: %s", str(
                            E), extra=log_param)
            else:
                # Cards with text, link or images
                card_str = ""
                for index, card in enumerate(cards):
                    logger.info("Inside Regular Card", extra=log_param)
                    title = str(card["title"])
                    content = str(
                        "\n" + card["content"] + "\n") if card["content"] != "" else ""
                    image_url = str(card["img_url"])
                    redirect_url = youtube_link_formatter(str(card["link"]))
                    caption = "*" + title + "* " + content + " " + redirect_url
                    if image_url != "":
                        logger.info("Card Image available", extra=log_param)
                        send_status = sendWhatsAppMediaMessage(
                            acl_username, acl_password, acl_api_url, waNumber, "image", str(image_url), str(mobile), caption=caption)
                        logger.info("Is Card with image sent: %s",
                                    str(send_status), extra=log_param)
                        time.sleep(0.5)
                    else:
                        # send_status = sendWhatsAppTextMessage(acl_username, acl_password, acl_api_url, waNumber, str(get_emojized_message(caption)), str(mobile), preview_url=True)
                        if index % max_cards_bubble_size == 0:
                            card_str += "$$$"
                        card_str += caption + "\n\n"
                        logger.info("Is Card with link sent: %s",
                                    str(send_status), extra=log_param)
                if card_str != "":
                    for card_bubble in card_str.split("$$$"):
                        if card_bubble.strip() == "":
                            continue
                        send_status = sendWhatsAppTextMessage(acl_username, acl_password, acl_api_url, waNumber, str(
                            get_emojized_message(card_bubble)), str(mobile), preview_url=True)
                time.sleep(0.5)
        elif len(videos) > 0:
            logger.info("== Inside Videos ==", extra=log_param)
            for i in range(len(videos)):
                if 'video_link' in str(videos[i]):
                    video_url = youtube_link_formatter(
                        str(videos[i]['video_link']))
                    if "youtu.be" in video_url:
                        send_status = sendWhatsAppTextMessage(
                            acl_username, acl_password, acl_api_url, waNumber, video_url, str(mobile), preview_url=True)
                    else:
                        send_status = sendWhatsAppMediaMessage(
                            acl_username, acl_password, acl_api_url, waNumber, "video", str(video_url), str(mobile), caption=None)
                    logger.info("Is Video sent: %s", str(
                        send_status), extra=log_param)
                else:
                    video_url = youtube_link_formatter(str(videos[i]))
                    if "youtu.be" in video_url:
                        send_status = sendWhatsAppTextMessage(
                            acl_username, acl_password, acl_api_url, waNumber, video_url, str(mobile), preview_url=True)
                    else:
                        send_status = sendWhatsAppMediaMessage(
                            acl_username, acl_password, acl_api_url, waNumber, "video", str(video_url), str(mobile), caption=None)
                    logger.info("Is Video sent: %s", str(
                        send_status), extra=log_param)

        elif len(images) > 0:
            logger.info("== Inside Images ==", extra=log_param)
            for i in range(len(images)):
                if 'img_url' in images[i] and 'content' in images[i]:
                    logger.info("== Image with caption ==", extra=log_param)
                    send_status = sendWhatsAppMediaMessage(acl_username, acl_password, acl_api_url, waNumber, "image", str(
                        images[i]["img_url"]), str(mobile), caption=str(images[i]['content']))
                    logger.info("Is Image sent: %s", str(
                        send_status), extra=log_param)
                else:
                    logger.info("== Image without caption ==")
                    send_status = sendWhatsAppMediaMessage(acl_username, acl_password, acl_api_url, waNumber, "image", str(
                        images[i]["img_url"]), str(mobile), caption=None)
                    logger.info("Is Image sent: %s", str(
                        send_status), extra=log_param)

    #   SENDING CHOICES AND RECOMMENDATIONS BOTH:
        if len(choice_str) > 0 and len(recommendation_str) > 0:
            mixed_choice = choices_recommendations_header + choice_str + \
                recommendation_str + choices_recommendations_footer
            time.sleep(0.6)
            send_status = sendWhatsAppTextMessage(acl_username, acl_password, acl_api_url, waNumber, mixed_choice.replace(
                "\n\n\n", "").replace("$$$", ""), str(mobile), preview_url=False)
            logger.info("Is Mixed Choices sent: %s",
                        str(send_status), extra=log_param)
            choice_str = ""
            recommendation_str = ""

    #   SENDING CHOICES:
        if len(choice_str) > 0:
            choice_str = choices_recommendations_header + \
                choice_str + choices_recommendations_footer
            if "$$$" in choice_str:
                for bubble in choice_str.split("$$$"):
                    if bubble.strip() == "":
                        continue
                    time.sleep(0.6)
                    send_status = sendWhatsAppTextMessage(
                        acl_username, acl_password, acl_api_url, waNumber, bubble, str(mobile), preview_url=False)
                logger.info("Is choices sent: %s", str(
                    send_status), extra=log_param)
            else:
                time.sleep(0.6)
                send_status = sendWhatsAppTextMessage(
                    acl_username, acl_password, acl_api_url, waNumber, choice_str, str(mobile), preview_url=False)
                logger.info("Is choices sent: %s", str(
                    send_status), extra=log_param)

    #   SENDING RECOMMENDATIONS:
        if len(recommendation_str) > 0:
            recommendation_str = choices_recommendations_header + \
                recommendation_str + choices_recommendations_footer
            if "$$$" in recommendation_str:
                for bubble in recommendation_str.split("$$$"):
                    if bubble.strip() == "":
                        continue
                    time.sleep(0.6)
                    send_status = sendWhatsAppTextMessage(
                        acl_username, acl_password, acl_api_url, waNumber, bubble, str(mobile), preview_url=False)
                    logger.info("Is recommendations sent: %s",
                                str(send_status), extra=log_param)
            else:
                time.sleep(0.6)
                send_status = sendWhatsAppTextMessage(
                    acl_username, acl_password, acl_api_url, waNumber, recommendation_str, str(mobile), preview_url=False)
                logger.info("Is recommendations sent: %s",
                            str(send_status), extra=log_param)

    #
        if change_language_response_required(sender, BOT_ID):
            language_str, REVERSE_WHATSAPP_MESSAGE_DICT = get_language_change_response(
                BOT_ID, REVERSE_WHATSAPP_MESSAGE_DICT)
            if language_str != "":
                language_str = get_emojized_message(language_str)
                send_status = sendWhatsAppTextMessage(
                    acl_username, acl_password, acl_api_url, waNumber, language_str, str(mobile), preview_url=False)
                logger.info("Is change language response sent: %s",
                            str(send_status), extra=log_param)
                save_data(user, json_data={"CHANGE_LANGUAGE_TRIGGERED": True},
                          src="None", channel="WhatsApp", bot_id=BOT_ID, is_cache=True)

    #   SENDING Helpful_Unhelpful_Choices:
        if is_feedback_required:
            time.sleep(0.7)
            feedback_str = "Enter :thumbs_up: for Helpful\n\nEnter :thumbs_down: for Unhelpful"
            send_status = sendWhatsAppTextMessage(acl_username, acl_password, acl_api_url, waNumber, get_emojized_message(
                feedback_str), str(mobile), preview_url=False)
            REVERSE_WHATSAPP_MESSAGE_DICT[get_emojized_message(
                ":thumbs_up:")] = "Helpful"
            REVERSE_WHATSAPP_MESSAGE_DICT[get_emojized_message(
                ":thumbs_up_light_skin_tone:")] = "Helpful"
            REVERSE_WHATSAPP_MESSAGE_DICT[get_emojized_message(
                ":thumbs_up_medium_light_skin_tone:")] = "Helpful"
            REVERSE_WHATSAPP_MESSAGE_DICT[get_emojized_message(
                ":thumbs_up_medium_skin_tone:")] = "Helpful"
            REVERSE_WHATSAPP_MESSAGE_DICT[get_emojized_message(
                ":thumbs_up_medium_dark_skin_tone:")] = "Helpful"
            REVERSE_WHATSAPP_MESSAGE_DICT[get_emojized_message(
                ":thumbs_up_dark_skin_tone:")] = "Helpful"
            REVERSE_WHATSAPP_MESSAGE_DICT[get_emojized_message(
                ":thumbs_down:")] = "Unhelpful"
            REVERSE_WHATSAPP_MESSAGE_DICT[get_emojized_message(
                ":thumbs_down_light_skin_tone:")] = "Unhelpful"
            REVERSE_WHATSAPP_MESSAGE_DICT[get_emojized_message(
                ":thumbs_down_medium_light_skin_tone:")] = "Unhelpful"
            REVERSE_WHATSAPP_MESSAGE_DICT[get_emojized_message(
                ":thumbs_down_medium_skin_tone:")] = "Unhelpful"
            REVERSE_WHATSAPP_MESSAGE_DICT[get_emojized_message(
                ":thumbs_down_medium_dark_skin_tone:")] = "Unhelpful"
            REVERSE_WHATSAPP_MESSAGE_DICT[get_emojized_message(
                ":thumbs_down_dark_skin_tone:")] = "Unhelpful"
            feedback_dict = {"is_intent_feedback_asked": True}
            save_data(user, json_data=feedback_dict,  src="None",
                      channel="WhatsApp", bot_id=BOT_ID,  is_cache=True)

        logger.info("REVERSE_WHATSAPP_MESSAGE_DICT: %s", str(
            REVERSE_WHATSAPP_MESSAGE_DICT), extra=log_param)
        save_data(user, json_data={"REVERSE_WHATSAPP_MESSAGE_DICT": REVERSE_WHATSAPP_MESSAGE_DICT},
                  src="None", channel="WhatsApp", bot_id=BOT_ID,  is_cache=True)

        response["status_code"] = 200
        response["status_message"] = "Request processed successfully."
        logger.info("ACLCallBack: %s", str(response), extra=log_param)
        return response
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(E) + str(exc_tb.tb_lineno)
        logger.error("ACLCallBack: %s at %s", str(
            E), str(exc_tb.tb_lineno), extra=log_param)
        return response
