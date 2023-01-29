from EasyChatApp.utils import *
from EasyChatApp.models import *
from LiveChatApp.models import *
from django.conf import settings
import emoji
import time
import json
import sys
import requests
import json
import http.client
import mimetypes
from bs4 import BeautifulSoup
from django.utils import timezone as tz
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
        "<b>": "*", "</b>": "*",
        "<em>": " _", "</em>": "_ ",
        "<i>": " _", "</i>": "_ ",
        "<strong>": "*", "</strong>": "*",
        "<p>": "", "</p>": ""
    }
    for tag in tags:
        message = message.replace(tag+"<a", "<a")
        message = message.replace("</a>"+tag, "</a>")
        message = message.replace("</a>\n"+tag, "</a>")
        message = message.replace(tag, tags[tag])

    if "</a>" in message:
        end = "\n"
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
                "\\u2019": "'", "\\u2013": "'", "\\u2018": "'"}
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
        logger.info(" === Reverse Message mapping === ",  extra=log_param)
        user = Profile.objects.get(user_id=str(mobile))
        data_obj = Data.objects.filter(
            user=user, variable="REVERSE_WHATSAPP_MESSAGE_DICT")[0]
        data_dict = json.loads(str(data_obj.value))
        logger.info("get_message_from_reverse_whatsapp_mapping Data Dictionary: %s", str(
            data_dict), extra=log_param)
        if str(user_message) in data_dict:
            message = data_dict[str(user_message)]
        logger.info(str(message), extra=log_param)
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_message_from_reverse_whatsapp_mapping: %s",
                     str(E),  extra=log_param)
    return message

# ====================== end ===================================================

# ====================== Vendor Specifics ======================================


def get_whatsapp_file_attachment(userid, password, message):
    filename = None
    try:
        message_dict = json.loads(message)
        signature = message_dict["signature"]
        mime_type = message_dict["mime_type"]
        remote_url = message_dict["url"]+str(signature)
        ext = mime_type.split("/")[-1]

        filename = None
        if "caption" in message_dict:
            filename = message_dict["caption"]
        else:
            filename = signature+"."+ext

        filename_bkp = filename
        filename = settings.MEDIA_ROOT+"WhatsAppMedia/"+filename
        save_file_from_remove_server_to_local(remote_url, filename)

        filename = settings.EASYCHAT_HOST_URL+"/files/WhatsAppMedia/"+filename_bkp
    except Exception as e:
        logger.error("is_whatsapp_file_attachment: %s", e, extra=log_param)

    return filename


def get_whatsapp_file_attachment(userid, password, request_packet):
    attachment_path = None
    try:
        attachment_packet = json.loads(request_packet)
        mime_type = attachment_packet["mime_type"]
        signature = attachment_packet["id"]
        ext = mime_type.split("/")[-1]
        remote_url = "https://unify.smsgupshup.com/WhatsApp/apis/getMedia.php?userid=" + \
            str(userid)+"&password="+str(password)+"&mediaid="+str(signature)
        if "caption" in attachment_packet:
            filename = attachment_packet["caption"]
            if "application/pdf" in mime_type and ".pdf" not in filename:
                filename = filename+"."+ext
            else:
                filename = signature+"."+ext
        else:
            filename = signature+"."+ext
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
def sendWhatsAppTextMessage(userid, password, message, phone_number, preview_url="false", is_unicode_text=False):
    import requests
    import urllib
    try:
        logger.info("=== Inside Send WA Text Message API ===", extra=log_param)
        message = urllib.parse.quote(message.encode('utf-8'))
        logger.info(message)
        url = """https://media.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to=""" + \
            str(phone_number)+"""&msg="""+message+"""&msg_type=TEXT&userid="""+str(userid) + \
            """&auth_scheme=plain&password=""" + \
            str(password)+"""&v=1.1&format=TEXT&preview_url="""+str(preview_url)

        if is_unicode_text:
            url += "&data_encoding=Unicode_text"

        logger.info("Send WA Text API URL: %s", url, extra=log_param)
        r = requests.get(url=url, timeout=15, verify=False)
        logger.info("Send WA Text API Response: %s",
                    str(r.text), extra=log_param)
        if str(r.text[:7]) == "success":
            logger.info("Text message sent succesfully", extra=log_param)
            return True
        else:
            logger.error("Failed to Send Text Message.", extra=log_param)
            return False
    except requests.Timeout as RT:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(RT) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppText API Timeout error: %s",
                     str(RT), str(exc_tb.tb_lineno), extra=log_param)
        return False
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(E) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppText API Failed: %s", str(E),
                     str(exc_tb.tb_lineno), extra=log_param)
    return False


# WHATSAPP SEND MEDIA MESSAGE API:
def sendWhatsAppMediaMessage(userid, password, media_type, media_url, caption, message, phone_number):
    import requests
    import urllib
    import json
    try:
        logger.info("=== Inside Send WA Media Message API ===",
                    extra=log_param)
        logger.info("Media Type: %s", media_type, extra=log_param)
        if media_type == "document" and caption == None:
            caption = "FileAttachment"
        elif caption == None:
            caption = ""
        message = urllib.parse.quote(message.encode('utf-8'))
        caption = urllib.parse.quote(caption.encode('utf-8'))
        url = """https://media.smsgupshup.com/GatewayAPI/rest?method=SendMediaMessage&send_to="""+str(phone_number)+"""&msg_type="""+str(media_type)+"""&userid="""+str(
            userid)+"""&auth_scheme=plain&password="""+str(password)+"""&v=1.1&format=json&media_url="""+str(media_url)+"""&caption="""+str(caption)+"""&msg="""+str(message)
        logger.info("Media Created URL: %s", url, extra=log_param)
        r = requests.get(url=url, timeout=15)
        content = json.loads(r.text)
        logger.info("sendWhatsAppMediaMessage Response: %s",
                    str(content), extra=log_param)

        if str(content['response']['status']) == "success":
            logger.info(media_type.upper() +
                        " message sent successfully", extra=log_param)
            return True
        else:
            logger.error("Failed to send "+media_type.upper() +
                         " message", extra=log_param)
            return False
    except requests.Timeout as RT:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(RT) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppMediaMessage Timeout error: %s",
                     str(RT), str(exc_tb.tb_lineno), extra=log_param)
        return False
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(E) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppMediaMessage Failed: %s",
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
    response["mobile_number"] = ""
    try:

        #   GUPSHUP DELIVERY STATUS:
        if "meta" in request_packet.keys() or "statuses" in request_packet.keys():
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
        logger.info("INSIDE GUPSHUP WA WEBHOOK", extra=log_param)
        logger.info("GUPSHUP WA WEBHOOK INCOMING_REQUEST_PACKET: %s",
                    str(request_packet), extra=log_param)

        if 'mobile' not in request_packet.keys():
            request_packet['mobile'] = request_packet['bot_id'].split('=')[-1]
            request_packet['bot_id'] = request_packet['bot_id'].split('?')[0]
            logger.info("Added Mobile and Bot id in INCOMING_REQUEST_PACKET: %s", str(
                request_packet), extra=log_param)

    # == CREDENTIALS AND DETAILS: ==============================================
        AUTHENTICATION_NUMBER = ''  # @settings.AUTHENTICATION_NUMBER
        AUTHENTICATION_KEY = ''  # settings.AUTHENTICATION_KEY
        BOT_ID = remo_html_from_string(str(request_packet['bot_id']))
        sender = remo_html_from_string(str(request_packet["mobile"]))
        receiver = remo_html_from_string(str(response["mobile_number"]))
        response["mobile_number"] = sender
        log_param["user_id"] = sender
        log_param["bot_id"] = BOT_ID
        logger.info("Sender: %s", str(sender), extra=log_param)
        logger.info("Reciever: %s", str(receiver), extra=log_param)
        GUPSHUP_MEDIA_CAPTION = str(BOT_ID)+"- Attachment"
    # ==========================================================================

    #   CHECK FOR NEW USER:
        first_time_user = "false"
        check_user = Profile.objects.filter(user_id=str(sender))
        if len(check_user) == 0:
            first_time_user = "true"
        logger.info("Is New User: %s", first_time_user, extra=log_param)

    #   CHECK USER MESSAGE TYPE: text, image, document, voice, location
        message_type = request_packet["type"]
        logger.info("Message Type: %s", message_type, extra=log_param)

    #   GET USER ATTACHMENTS AND MESSAGES:
        is_location = True
        is_attachement = True
        message = None
        filepath = None
        file_caption = None
        REVERSE_WHATSAPP_MESSAGE_DICT = {}
        reverse_mapping_index = 0
        if message_type == "text":
            is_attachement = False
            is_location = False
        if is_attachement:
            # image, document, voice
            attachment_packet = request_packet[request_packet["type"]]
            attachment_type = message_type
            logger.info(" Whatsapp attachment packet: %s",
                        str(attachment_packet), extra=log_param)
            if attachment_type != "document" and "caption" in attachment_packet:
                file_caption = attachment_packet["caption"]
            filepath = get_whatsapp_file_attachment(
                AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, attachment_packet)
            message = request_packet['text']  # "attachment"
        else:
            #   else get user Message:
            message = request_packet["text"]
            reverse_message = None
            reverse_message = get_message_from_reverse_whatsapp_mapping(
                message, sender)
            if reverse_message != None:
                message = reverse_message
            # Go Back Check
            is_go_back_enabled = False
            if first_time_user == "false":
                user = Profile.objects.get(user_id=str(sender))
                check_go_back_enabled = Data.objects.filter(
                    user=user, variable="is_go_back_enabled")

                if len(check_go_back_enabled) > 0 and str(check_go_back_enabled[0].value) == 'true':
                    is_go_back_enabled = True
        user_query = message
        logger.info("User Message(final): %s", str(message), extra=log_param)

    #   WEBHOOK EXECUTE FUNCTION CALL
        mobile = str(sender)  # User mobile
        waNumber = str(receiver)  # Bot Whatsapp Number

    #   WEBHOOK EXECUTE FUNCTION CALL
        channel_params = {"user_mobile": mobile, "bot_number": waNumber, "whatsapp_file_attachment": filepath, "whatsapp_file_caption": file_caption,
                          "is_new_user": first_time_user, "QueryChannel": "WhatsApp", "is_go_back_enabled": is_go_back_enabled}
        logger.info("GupShupCallBack Channel params:  %s",
                    str(channel_params), extra=log_param)
        whatsapp_response = execute_query(
            mobile, BOT_ID, "uat", message, "en", "WhatsApp", json.dumps(channel_params), message)
        logger.info("GupShupCallBack execute_query response %s",
                    str(whatsapp_response), extra=log_param)

    #   Check LiveChat:
        if "is_livechat" in whatsapp_response and whatsapp_response["is_livechat"] == "true":
            if message.lower() == "end chat":
                livechat_notification = "LiveChat Session has ended."
                send_status = sendWhatsAppTextMessage(
                    AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, livechat_notification, str(mobile), is_unicode_text=True)
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
                                logger.info("RouteMobileCallBack: execute_query after Auth response %s", str(
                                    whatsapp_response), extra=log_param)
        except Exception as E:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Cannot identify Last Intent: %s at %s",
                         str(E), str(exc_tb.tb_lineno), extra=log_param)

    #   USER OBJECT:
        user = Profile.objects.get(user_id=str(mobile))

    #   BOT RESPONSES: images, videos, cards, choices, recommendations
        message = whatsapp_response["response"]["text_response"]["text"]
        modes = whatsapp_response["response"]["text_response"]["modes"]
        modes_param = whatsapp_response["response"]["text_response"]["modes_param"]
        recommendations = whatsapp_response["response"]["recommendations"]
        images = whatsapp_response["response"]["images"]
        videos = whatsapp_response["response"]["videos"]
        cards = whatsapp_response["response"]["cards"]
        choices = whatsapp_response["response"]["choices"]

        if message is None or message == "":
            message = "None"

    #   Custom Inital Messages and recommendations when intent not found:
        is_intent_identified = True
        if "is_intent_identified" in whatsapp_response and is_intent_identified == False:
            is_intent_identified = whatsapp_response["is_intent_identified"]
            # uncomment to use:
            # message = "Your custom failure message..."
            # recommendations = []

    #	Go Back Check
        is_go_back_enabled = False
        if "is_go_back_enabled" in whatsapp_response["response"]:
            is_go_back_enabled = whatsapp_response["response"]["is_go_back_enabled"]
            save_data(user, json_data={"is_go_back_enabled": is_go_back_enabled},
                      src="None", channel="WhatsApp", bot_id=BOT_ID, is_cache=True)

    #   EMOJI NUMBERS: 1 to 9
        emojized_numbers = [":one:", ":two:", ":three:", ":four:",
                            ":five:", ":six:", ":seven:", ":eight:", ":nine:"]

    #   CHOICES:
        choice_dict = {}
        choice_display_list = []
        for choice in whatsapp_response["response"]["choices"]:
            if choice["display"] == "Helpful" or choice["display"] == "Unhelpful":
                continue
            choice_dict[choice["display"]] = choice["value"]
            choice_display_list.append(choice["display"])
        choice_str = ""
        if choice_display_list != []:
            if whatsapp_response["response"]["is_flow_ended"]:
                choice_str += "\n"
            # else:
            #     choice_str += "\n\nSelect one of the following :point_down::\n\n"
            for index in range(len(choice_display_list)):
                if index % 10 == 0 and index != 0:
                    choice_str += "$$$"
                REVERSE_WHATSAPP_MESSAGE_DICT[str(
                    index+1)] = str(choice_dict[choice_display_list[index]])
                choice_str += "Enter *" + \
                    str(index+1)+"* :point_right:  " + \
                    str(choice_display_list[index])+"\n\n"
            choice_str = get_emojized_message(choice_str)+"\n\n\n"
            choice_str = html_tags_formatter(choice_str)
            reverse_mapping_index = len(choice_display_list)
        logger.info("Choices: %s", str(choice_str), extra=log_param)

    #   RECOMMENDATIONS:
        recommendation_str = ""
        if recommendations != []:
            if whatsapp_response["response"]["is_flow_ended"]:
                recommendation_str += "\n\n"
            # else:
            #     recommendation_str += "\n\nSelect one of the following :\n\n"
            if choice_str != "":
                for index in range(len(recommendations)):
                    if index % 10 == 0:
                        recommendation_str += "$$$"
                    REVERSE_WHATSAPP_MESSAGE_DICT[str(
                        reverse_mapping_index+index+1)] = str(recommendations[index])
                    recommendation_str += "Enter *" + \
                        str(reverse_mapping_index+index+1) + \
                        "* :point_right:  " + \
                        str(recommendations[index])+"\n\n"
                if is_go_back_enabled:
                    REVERSE_WHATSAPP_MESSAGE_DICT[str(
                        reverse_mapping_index+len(recommendations)+1)] = "Go Back"
                    recommendation_str += "Enter *" + \
                        str(reverse_mapping_index+len(recommendations)+1) + \
                        "* :point_right:  Go Back \n\n"

            else:
                for index in range(len(recommendations)):
                    if index % 10 == 0 and index != 0:
                        recommendation_str += "$$$"
                    REVERSE_WHATSAPP_MESSAGE_DICT[str(
                        index+1)] = str(recommendations[index])
                    recommendation_str += "Enter *" + \
                        str(index+1)+"* :point_right:  " + \
                        str(recommendations[index])+"\n\n"
                if is_go_back_enabled:
                    REVERSE_WHATSAPP_MESSAGE_DICT[str(
                        len(recommendations)+1)] = "Go Back"
                    recommendation_str += "Enter *" + \
                        str(len(recommendations)+1) + \
                        "* :point_right:  Go Back \n\n"
            recommendation_str = get_emojized_message(recommendation_str)
        else:
            if is_go_back_enabled:
                le = len(recommendations)
                if le == 0:
                    le = len(choice_display_list)
                REVERSE_WHATSAPP_MESSAGE_DICT[str(le+1)] = "Go Back"
                recommendation_str += "Enter *" + \
                    str(le+1)+"* :point_right:  Go Back \n\n"
                recommendation_str = get_emojized_message(recommendation_str)
        logger.info("Recommendations: %s", str(
            recommendation_str), extra=log_param)
        logger.info("Choices: %s", str(choice_str), extra=log_param)
        logger.info("Reverse Mapper: %s", str(
            REVERSE_WHATSAPP_MESSAGE_DICT), extra=log_param)

    #   TEXT FORMATTING AND EMOJIZING:
        message = html_tags_formatter(message)
        message = unicode_formatter(message)
        message = get_emojized_message(message)
        logger.info("Bot Message: %s", str(message), extra=log_param)

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
                if len(choice_str) > 0:
                    final_text_message += choice_str
                if len(recommendation_str) > 0:
                    final_text_message += recommendation_str
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
                        AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, final_text_message, str(mobile),  preview_url="true")
                    # time.sleep(2)
                    is_sandwich_choice = True
                else:
                    send_status = sendWhatsAppTextMessage(
                        AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, final_text_message, str(mobile), is_unicode_text=True)
                    is_sandwich_choice = True
                    # time.sleep(2)
                recommendation_str = ""
                choice_str = ""
        else:
            if message_with_choice == True:
                # 2. Sticky choices text:
                final_text_message = message.replace("$$$", "")
                if len(recommendations) > 0:
                    final_text_message = final_text_message + \
                        recommendation_str.replace("$$$", "")
                    final_text_message = final_text_message.replace(
                        "\n\n\n", "\n")
                    logger.info("Sticky recommendations: %s", str(
                        final_text_message), extra=log_param)

                if len(choice_display_list) > 0:
                    final_text_message = final_text_message + \
                        choice_str.replace("$$$",  "")
                    logger.info("Sticky choices: %s", str(
                        final_text_message), extra=log_param)

                if "http://" in final_text_message or "https://" in final_text_message:
                    final_text_message = youtube_link_formatter(
                        final_text_message)
                    send_status = sendWhatsAppTextMessage(
                        AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, final_text_message, str(mobile),  preview_url="true")
                else:
                    send_status = sendWhatsAppTextMessage(
                        AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, final_text_message, str(mobile), is_unicode_text=True)
                recommendation_str = ""
                choice_str = ""
            else:
                # 3. Regular single text:
                for small_message in final_text_message.split("$$$"):
                    small_message = html_list_formatter(small_message)
                    if small_message != "":
                        if "http://" in small_message or "https://" in small_message:
                            small_message = youtube_link_formatter(
                                small_message)
                            send_status = sendWhatsAppTextMessage(
                                AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, small_message, str(mobile),  preview_url="true")
                        else:
                            send_status = sendWhatsAppTextMessage(
                                AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, small_message, str(mobile), is_unicode_text=True)
                        time.sleep(0.05)

    #   SENDING CARDS, IMAGES, VIDEOS:
        logger.info("Cards: %s", str(cards), extra=log_param)
        logger.info("Images: %s", str(images), extra=log_param)
        logger.info("Videos: %s", str(videos), extra=log_param)

        if len(cards) > 0:
            if "card_with_document" in modes.keys() and modes["card_with_document"] == "true":
                # Cards with documnet links:  Use 'card_with_document:true' in modes
                logger.info("Inside Cards with documents", extra=log_param)
                for card in cards:
                    doc_caption = str(card["title"])
                    doc_url = str(card["link"])
                    logger.info("DOCUMENT NAME: %s", str(
                        doc_caption), extra=log_param)
                    logger.info("DOCUMENT URL: %s", str(
                        doc_url), extra=log_param)
                    try:
                        send_status = sendWhatsAppMediaMessage(AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, "Document", str(
                            doc_url), str(doc_caption), GUPSHUP_MEDIA_CAPTION, str(mobile))
                        logger.info("Is Card sent: %s", str(
                            send_status), extra=log_param)
                    except Exception as E:
                        logger.error("Cannot send card with document: %s", str(
                            E), extra=log_param)
            else:
                # Cards with text, link or images
                for card in cards:
                    logger.info("Inside Regular Card", extra=log_param)
                    title = str(card["title"])
                    content = str("\n"+card["content"]+"\n")
                    image_url = str(card["img_url"])
                    redirect_url = youtube_link_formatter(str(card["link"]))
                    caption = "*"+title+"* "+content+" "+redirect_url
                    if image_url != "":
                        logger.info("Card Image available", extra=log_param)
                        send_status = sendWhatsAppMediaMessage(AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, "Image", str(
                            image_url), caption, GUPSHUP_MEDIA_CAPTION, str(mobile))
                        logger.info("Is Card with image sent: %s",
                                    str(send_status), extra=log_param)
                    else:
                        send_status = sendWhatsAppTextMessage(AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, str(
                            get_emojized_message(caption)), str(mobile), preview_url="true")
                        logger.info("Is Card with link sent: %s",
                                    str(send_status), extra=log_param)

        elif len(videos) > 0:
            logger.info("== Inside Videos ==", extra=log_param)
            if 'video_link' in str(videos[i]):
                video_url = youtube_link_formatter(
                    str(videos[i]['video_link']))
                if "youtu.be" in video_url:
                    send_status = sendWhatsAppTextMessage(
                        AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, video_url, str(mobile), preview_url="true")
                else:
                    send_status = sendWhatsAppMediaMessage(AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, "Video", str(
                        video_url), GUPSHUP_MEDIA_CAPTION, GUPSHUP_MEDIA_CAPTION, str(mobile))
                logger.info("Is Video sent: %s", str(
                    send_status), extra=log_param)
            else:
                video_url = youtube_link_formatter(str(videos[i]))
                if "youtu.be" in video_url:
                    send_status = sendWhatsAppTextMessage(
                        AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, video_url, str(mobile), preview_url="true")
                else:
                    send_status = sendWhatsAppMediaMessage(AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, "Video", str(
                        video_url), GUPSHUP_MEDIA_CAPTION, GUPSHUP_MEDIA_CAPTION, str(mobile))
                logger.info("Is Video sent: %s", str(
                    send_status), extra=log_param)

        elif len(images) > 0:
            logger.info("== Inside Images ==", extra=log_param)
            for i in range(len(images)):
                if 'img_url' in images[i] and 'content' in images[i]:
                    logger.info("== Image with caption ==", extra=log_param)
                    send_status = sendWhatsAppMediaMessage(AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, "Image", str(
                        images[i]["img_url"]), str(images[i]['content']), GUPSHUP_MEDIA_CAPTION, str(mobile))
                    logger.info("Is Image sent: %s", str(
                        send_status), extra=log_param)
                else:
                    logger.info("== Image without caption ==")
                    send_status = sendWhatsAppMediaMessage(AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, "Image", str(
                        images[i]), GUPSHUP_MEDIA_CAPTION, GUPSHUP_MEDIA_CAPTION, str(mobile))
                    logger.info("Is Image sent: %s", str(
                        send_status), extra=log_param)

    #   SENDING CHOICES AND RECOMMENDATIONS BOTH:
        if len(choice_str) > 0 and len(recommendation_str) > 0:
            mixed_choice = choice_str+""+recommendation_str
            time.sleep(0.5)
            send_status = sendWhatsAppTextMessage(AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, mixed_choice.replace(
                "\n\n\n", "").replace("$$$", ""), str(mobile), is_unicode_text=True)
            logger.info("Is Mixed Choices sent: %s",
                        str(send_status), extra=log_param)
            choice_str = ""
            recommendation_str = ""

    #   SENDING CHOICES:
        if len(choice_str) > 0:
            if "$$$" in choice_str:
                for bubble in choice_str.split("$$$"):
                    if bubble.strip() == "":
                        continue
                    time.sleep(0.5)
                    send_status = sendWhatsAppTextMessage(
                        AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, bubble, str(mobile), is_unicode_text=True)
                logger.info("Is choices sent: %s", str(
                    send_status), extra=log_param)
            else:
                time.sleep(0.5)
                send_status = sendWhatsAppTextMessage(
                    AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, choice_str, str(mobile), is_unicode_text=True)
                logger.info("Is choices sent: %s", str(
                    send_status), extra=log_param)

    #   SENDING RECOMMENDATIONS:
        if len(recommendation_str) > 0:
            if "$$$" in recommendation_str:
                for bubble in recommendation_str.split("$$$"):
                    if bubble.strip() == "":
                        continue
                    time.sleep(0.5)
                    send_status = sendWhatsAppTextMessage(
                        AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, bubble, str(mobile), is_unicode_text=True)
                    logger.info("Is recommendations sent: %s",
                                str(send_status), extra=log_param)
            else:
                time.sleep(0.5)
                send_status = sendWhatsAppTextMessage(
                    AUTHENTICATION_NUMBER, AUTHENTICATION_KEY, recommendation_str, str(mobile), is_unicode_text=True)
                logger.info("Is recommendations sent: %s",
                            str(send_status), extra=log_param)

        logger.info("REVERSE_WHATSAPP_MESSAGE_DICT: %s", str(
            REVERSE_WHATSAPP_MESSAGE_DICT), extra=log_param)
        save_data(user, json_data={"REVERSE_WHATSAPP_MESSAGE_DICT": REVERSE_WHATSAPP_MESSAGE_DICT},
                  src="None", channel="WhatsApp", bot_id=BOT_ID,  is_cache=True)

        response["status_code"] = 200
        response["status_message"] = "Request processed successfully."
        logger.info("GubShupWhatsAppCallBackURL: %s",
                    str(response), extra=log_param)
        return response
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(E) + str(exc_tb.tb_lineno)
        logger.error("GubShupWhatsAppCallBackURL: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
        return response
