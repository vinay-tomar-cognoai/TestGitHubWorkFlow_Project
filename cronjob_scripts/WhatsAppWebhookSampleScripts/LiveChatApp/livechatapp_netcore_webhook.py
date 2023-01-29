from EasyChatApp.utils import *
from LiveChatApp.models import *
from LiveChatApp.utils import get_time, get_miniseconds_datetime
from EasyChatApp.models import *
from django.conf import settings
from EasyChatApp.utils_custom_encryption import CustomEncrypt
import emoji
import time
import json
import sys
import requests
import websocket
from bs4 import BeautifulSoup
from django.utils import timezone as tz

log_param={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'WhatsApp', 'bot_id': '1'}

# ========================== TEXT FORMATTING FUNCTIONS =========================
def youtube_link_formatter(message):
    if "https://www.youtube.com" in message:
        message =  message.replace("embed/","").replace("www.youtube.com","youtu.be")
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
                ul_end_position  = sent.find("</ul>", ul_position)
                list_str = sent[ul_position:ul_end_position+5]
                logger.info("HTML LIST STRING "+str(i+1)+": %s", str(list_str), extra=log_param)
                list_str1 = list_str.replace("<ul>","").replace("</ul>","").replace("<li>","")
                items = list_str1.split("</li>")
                items[-2] = items[-2]+"<br><br>"
                formatted_list_str = ""
                for item in items:
                    if item.strip()!= "":
                        formatted_list_str += "\n\n- "+item.strip()+"\n" 
                sent = sent.replace(list_str,formatted_list_str).replace("<br>","\n")+"\n"
                sent = sent.strip()
                logger.info("---Html list string formatted---", extra=log_param)
        if "<ol>" in sent:
            # print("yes ol")
            for i in range(sent.count("<ol>")): 
                list_strings_dict = {}
                ol_position = sent.find("<ol>", ol_end_position)
                ol_end_position  = sent.find("</ol>", ol_position)
                list_str = sent[ol_position:ol_end_position+5]
                logger.info("HTML LIST STRING "+str(i+1)+": %s", str(list_str), extra=log_param)
                list_str1 = list_str.replace("<li>","").replace("<ol>","").replace("</ol>","")
                items = list_str1.split("</li>")
                items[-2] = items[-2]+"<br><br>"
                formatted_list_str = ""
                for j,item in enumerate(items[:-1]):
                    if item.strip()!= "":
                        formatted_list_str += "\n"+str(j+1)+". "+item.strip()
                sent = sent.replace(list_str,formatted_list_str)
                sent = sent.strip().replace("<br>","\n")
                logger.info("---Html list string formatted---", extra=log_param)            
    except Exception as E:
        logger.error("Failed to format html list string: %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
        # print("Failed to format html list string: %s", str(E))
    return sent    
    
def html_tags_formatter(message):
    tags = {
        "<br>":"\n", "<br/>":"\n", "<br />":"\n",
        "<b>":"*", "</b>":"*",
        "<em>":" _", "</em>":"_ ",
        "<i>":" _", "</i>":"_ ", 
        "<strong>":"*", "</strong>":"*", 
        "<p>":"","</p>":""
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
        message = message.replace("mailto:","").replace("tel:","")
        soup = BeautifulSoup(message, "html.parser")
        for link in soup.findAll('a'):
            href = link.get('href')
            link_name = link.string
            link_element = message[message.find("<a"):message.find("</a>")]+"</a>"
            if link_name.replace("http://","").replace("https://","").strip() == href.replace("http://","").replace("https://","").strip():
                message = message.replace(link_element, href+end)
            else:
                message = message.replace(link_element, link_name+" "+href+end)
    return message

def unicode_formatter(message):
    unicodes = {"&nbsp;":" ", "&#39;":"\'", "&rsquo;":"\'", "&amp;":"&", "&hellip;":"...", "&quot;":"\"", "&rdquo;":"\"", "&ldquo;":"\""}
    for code in unicodes:
        message = message.replace(code, unicodes[code])
    return message    

def get_emojized_message(message):
    return emoji.emojize(message, language='alias')
# ====================== end ===================================================
# Calculate difference b/w datetime objects
def get_time_delta(date_str1, date_str2):
    delta_obj = {"minutes":0.0, "hours":0.0}
    try:
        from datetime import date, datetime
        if "." in date_str1:
            date_str1 = str(date_str1).split(".")[0]
        if "." in date_str2:
            date_str2 = str(date_str2).split(".")[0]
        date_str1 = datetime.strptime(date_str1, "%Y-%m-%d %H:%M:%S")
        date_str2 = datetime.strptime(date_str2, "%Y-%m-%d %H:%M:%S")
        delta = date_str2 - date_str1 # 2nd date is greater
        duration_in_s = delta.total_seconds()
        delta_obj = {
            "seconds":duration_in_s,
            "minutes":round(duration_in_s/60,1), #divmod(duration_in_s, 60)[0],
            "hours":divmod(duration_in_s, 3600)[0],
            "days":divmod(duration_in_s, 86400)[0],
            "years":divmod(duration_in_s, 31536000)[0]
        }
        return delta_obj
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_time_delta: %s at %s", str(E), str(exc_tb.tb_lineno), extra=log_param)
        return delta_obj


#   WHATSAPP SEND TEXT MESSAGE API:
def sendWhatsAppTextMessage(message, phone_number, preview_url=False):
    ''' A function to call send whatsapp text message API.'''
    import requests
    import urllib
    try:
        api_key = "" # Add Netcore API Key Here
        logger.info(message, extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "None"})
        url = "https://waapi.pepipost.com/api/v2/message/"
        headers = {
        'Authorization': 'Bearer '+api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
        }
        payload = {
            "message": [
                {
                    "recipient_whatsapp": phone_number,
                    "recipient_type": "individual",
                    "message_type": "text",
                    "source": "",  # Source provided by Netcore
                    "x-apiheader": "custom_data",
                    "type_text": [
                        {
                            "preview_url": preview_url,
                            "content": message
                        }
                    ]
                }
            ]
        }
        r = requests.request("POST", url, headers=headers, data = json.dumps(payload), timeout=20, verify=False)
        content = json.dumps(r.text)
        logger.info("Send WA Text API Response: %s", str(content), extra=log_param)
        if str(r.status_code) == "200":
            logger.info("Text message sent succesfully", extra=log_param)
            return True
        else:
            logger.error("Failed to Send Text Message.", extra=log_param)
            return False
    except requests.Timeout as rt:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(e) + str(exc_tb.tb_lineno)
        logger.error("sendWhatsAppTextMessage API Timeout error: %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("sendWhatsAppTextMessage ERROR: %s for %s of user-%s", str(e), str(exc_tb.tb_lineno), str(phone_number), extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "None"})
    return False

def get_msg_type(file):
    try:
        file_ext = file.split(".")[-1]
        if file_ext in ["png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"]:
            return "image"
        elif file_ext in ["WEBM", "MPG", "MP2", "MPEG", "MPE", "MPV", "OGG", "MP4", "M4P", "M4V", "AVI", "WMV", "MOV", "QT", "FLV", "SWF", "AVCHD"]:
            return "video"
        else:
            return "document"
    except:
        return "document"


# WHATSAPP SEND MEDIA MESSAGE API:
def sendWhatsAppMediaMessage(media_type, media_url, phone_number, caption = None):
    import requests
    import urllib
    import json
    try:
        api_key = "" # Add Netcore API Key Here        
        logger.info("=== Inside Send WA Media Message API ===", extra=log_param)
        logger.info("Media Type: %s", media_type, extra=log_param)
        if media_type == "document" and caption == None:
            caption = "FileAttachment"
        elif caption == None:
            caption = ""
        url = "https://waapi.pepipost.com/api/v2/message/"
        headers = {
            'Authorization': 'Bearer '+api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            "message": [{
                "recipient_whatsapp": phone_number,
                "message_type": "media",
                "recipient_type": "individual",
                "source": "", # Source provided by Netcore
                "x-apiheader": "custom_data",
                "type_media": [{
                        "attachments": [{
                            "attachment_url": media_url,
                            "attachment_type": media_type,
                            "caption": str(caption)
                        }]
                    }]
            }]
        }
        r = requests.request("POST", url, headers=headers, data = json.dumps(payload), timeout=20, verify=True)
        content = json.dumps(r.text)
        logger.info("Send WA "+media_type.upper()+" API Response: %s", str(content), extra=log_param)
        if str(r.status_code) == "200":
            logger.info(media_type.upper()+" message sent successfully", extra=log_param)
            return True
        else:
            logger.error("Failed to send "+media_type.upper()+" message: %s", extra=log_param)
            return False
    except requests.Timeout as rt:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(e) + str(exc_tb.tb_lineno)
        logger.error("sendWhatsAppMediaMessage Timeout error: %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: sendWhatsAppMediaMessage: %s for %s of user-%s", str(e), str(exc_tb.tb_lineno), str(phone_number), extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "None"})
    return False

def f(x):
    logger.info("Inside wa livechat webhook", extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "None"})
    #  SAMPLE REQUEST PACKET:	
    """
    response = {
    	"session_id":user_session_id,
        "type": (text/file),
        "text_message": (message),
        "path": FILE_PATH,
        "channel": CHANNEL(Web/Whtasapp/Facebook/Alexa/Google),
        "bot_id": BOT_ID
    }
    """
    x = json.loads(x)
    BOT_ID = "1"
    if "bot_id" in x:
        BOT_ID = str(x["bot_id"])
    logger.info("wa livechat request packet: %s", str(x), extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': BOT_ID})
    try:
        user_id = Profile.objects.filter(livechat_session_id=str(x["session_id"]))[0].user_id
        if x["type"] == 'text' and x['path'] == '':
            if "agent_name" in x:
                agent_name = x["agent_name"]
                message = "<b>"+ str(agent_name).strip() +"</b> \n\n"+ x["text_message"]
            else:
                message = x["text_message"]
            message = html_tags_formatter(message)        
            message = unicode_formatter(message)
            message = get_emojized_message(message)       
            logger.info("Agent Message: %s", str(message), extra={'AppName': 'EasyChat', 'user_id': user_id, 'source': "None", 'channel': "None", 'bot_id': BOT_ID})
            sendWhatsAppTextMessage(str(message), user_id)
        else:
            file_path = settings.EASYCHAT_HOST_URL + x["path"]
            logger.info("Agent Attachment: %s", str(file_path), extra={'AppName': 'EasyChat', 'user_id': user_id, 'source': "None", 'channel': "None", 'bot_id': BOT_ID})
            filename = file_path.split("/")[-1]
            message = filename
            msg_type = get_msg_type(filename)
            if x["text_message"] != "":
                message = x["text_message"]
                message = html_tags_formatter(message)        
                message = unicode_formatter(message)
                message = get_emojized_message(message)       
                if msg_type == "document":
                    sendWhatsAppMediaMessage(msg_type, file_path, user_id, message)
                    time.sleep(0.5)
                    sendWhatsAppTextMessage(str(message), user_id)
                else:
                    sendWhatsAppMediaMessage(msg_type, file_path, user_id, message)
            else:
                sendWhatsAppMediaMessage(msg_type, file_path, user_id)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside send_message_to_whatsapp: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': BOT_ID})
        pass
        