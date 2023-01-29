import datetime


ignore_list = ["what", "where", "who", "whom",
               "how", "when", "why", "not", "about", "no", "you", "your", "yours"]

MAX_MESSAGE_PER_PAGE = 10

# chunk of suggestion limit indicates no of training sentences to be loaded in one chunk
# or the no of suggestions sent in one api call 
CHUNK_OF_SUGGESTION_LIMIT = 5000

INVALID_REQUEST = "<h3>Invalid Request</h3>"
DEFAULT_NO_OF_CLASSES_SELF_LEARNING = 2

DEFAULT_NO_OF_DAYS_WHATSAPP_HISTORY_RECORD_LIST = [10, 25, 50, 100]

BOT_BUILDER_ROLE = "bot_builder"
CUSTOMER_CARE_AGENT_ROLE = "customer_care_agent"

USER_CHOICES = (
    (BOT_BUILDER_ROLE, "bot_builder"),
    (CUSTOMER_CARE_AGENT_ROLE, "customer_care_agent")
)

# Custom Intents for Webpages
AUTO_POPUP = "auto_popup"
FORM_ASSIST = "form_assist"

CUSTOM_INTENTS_CHOICE = (
    (AUTO_POPUP, "auto_popup"),
    (FORM_ASSIST, "form_assist")
)

CUSTOM_INTENTS_FOR_DICT = {
    "auto_popup": AUTO_POPUP,
    "form_assist": FORM_ASSIST
}

EMAIL_FREQ_CHOICES = (
    ("1", "daily"),
    ("2", "weekly"),
    ("3", "monthly")
)

# Custom Intents for Webpages end

ROLES = (
        ("1", "manager"),
        ("2", "agent"),
)

BOT_CREATION_PERMISSION = (
    ("1", "Allowed"),
    ("2", "Not Allowed"),
    ("3", "None")
)

CREATE_INTENT_ACTION = "1"
DELETE_INTENT_ACTION = "2"
MODIFY_INTENT_ACTION = "3"
SHARE_BOT_ACTION = "4"
UNSHARE_BOT_ACTION = "5"
USER_LOGGED_IN = "6"
USER_LOGGED_OUT = "7"
DELETE_BOT_ACTION = "8"
EXPORT_BOT_AS_JSON_ACTION = "9"
IMPORT_BOT_FROM_JSON_ACTION = "10"
EXPORT_BOT_AS_ZIP_ACTION = "11"
IMPORT_BOT_FROM_ZIP_ACTION = "12"
CREATE_BOT_ACTION = "13"
EDIT_PROCESSOR_ACTION = "14"
CREATE_PROCESSOR_ACTION = "15"
FAQ_EXCEL_UPLOADED_ACTION = "16"
CREATE_INTENT_FROM_FAQ_ACTION = "17"
DELETE_PROCESSOR_ACTION = "18"
EXPORT_INTENT_AS_JSON_ACTION = "19"
IMPORT_INTENT_FROM_JSON_ACTION = "20"

AUDIT_TRAIN_ACTIONS = (
    (CREATE_INTENT_ACTION, "Intent created"),
    (DELETE_INTENT_ACTION, "Intent deleted"),
    (MODIFY_INTENT_ACTION, "Intent modified"),
    (SHARE_BOT_ACTION, "Bot Shared"),
    (UNSHARE_BOT_ACTION, "Bot Share Revoked"),
    (USER_LOGGED_IN, "User Logged In"),
    (USER_LOGGED_OUT, "User Logged Out"),
    (DELETE_BOT_ACTION, "Bot deleted"),
    (EXPORT_BOT_AS_JSON_ACTION, "Bot exported as JSON"),
    (IMPORT_BOT_FROM_JSON_ACTION, "Imported bot from JSON"),
    (EXPORT_BOT_AS_ZIP_ACTION, "Bot exported as Zip"),
    (IMPORT_BOT_FROM_ZIP_ACTION, "Imported bot from Zip"),
    (CREATE_BOT_ACTION, "Bot created"),
    (EDIT_PROCESSOR_ACTION, "Processor edited"),
    (CREATE_PROCESSOR_ACTION, "Processor created"),
    (FAQ_EXCEL_UPLOADED_ACTION, "FAQ added using excel"),
    (CREATE_INTENT_FROM_FAQ_ACTION, "Intent added using extracted FAQs"),
    (DELETE_PROCESSOR_ACTION, "Processor Deleted"),
    (EXPORT_INTENT_AS_JSON_ACTION, "Intent exported as JSON"),
    (IMPORT_INTENT_FROM_JSON_ACTION, "Intent imported as JSON"),
)

PASSWORD_RESET_DURATION = [
    ('45', '45 days'),
    ('60', '60 days'),
    ('90', '90 days')
]

AUDIT_TRAIN_ACTION_DICT = {
    CREATE_INTENT_ACTION: "Intent created",
    DELETE_INTENT_ACTION: "Intent deleted",
    MODIFY_INTENT_ACTION: "Intent modified",
    SHARE_BOT_ACTION: "Bot Shared",
    UNSHARE_BOT_ACTION: "Bot Share Revoked",
    USER_LOGGED_IN: "User Logged In",
    USER_LOGGED_OUT: "User Logged Out",
    DELETE_BOT_ACTION: "Bot deleted",
    EXPORT_BOT_AS_JSON_ACTION: "Bot exported as JSON",
    IMPORT_BOT_FROM_JSON_ACTION: "Imported bot from JSON",
    EXPORT_BOT_AS_ZIP_ACTION: "Bot exported as Zip",
    IMPORT_BOT_FROM_ZIP_ACTION: "Imported bot from Zip",
    CREATE_BOT_ACTION: "Bot created",
    EDIT_PROCESSOR_ACTION: "Processor edited",
    CREATE_PROCESSOR_ACTION: "Processor created",
    FAQ_EXCEL_UPLOADED_ACTION: "FAQ added using excel",
    CREATE_INTENT_FROM_FAQ_ACTION: "Intent added using extracted FAQs",
    DELETE_PROCESSOR_ACTION: "Processor deleted",
    EXPORT_INTENT_AS_JSON_ACTION: "Intent exported as JSON",
    IMPORT_INTENT_FROM_JSON_ACTION: "Intent imported as JSON"
}

MEDIA_IMAGE = "1"
MEDIA_PPT = "2"
MEDIA_DOC = "3"
MEDIA_XLS = "4"
MEDIA_PDF = "5"
MEDIA_VIDEO = "7"
MEDIA_OTHER = "6"

MEDIA_TYPES = (
    (MEDIA_IMAGE, "image"),
    (MEDIA_PPT, "ppt"),
    (MEDIA_DOC, "docx"),
    (MEDIA_XLS, "xlsx"),
    (MEDIA_PDF, "pdf"),
    (MEDIA_OTHER, "other"),
    (MEDIA_VIDEO, "video")
)

MEDIA_TYPE_DICT = {
    MEDIA_IMAGE: "image",
    MEDIA_PPT: "ppt",
    MEDIA_DOC: "doc",
    MEDIA_XLS: "xlsx",
    MEDIA_PDF: "pdf",
    MEDIA_OTHER: "other",
    MEDIA_VIDEO: "video"
}

EASYCHAT_MEDIA = {
    "images": [],
    "ppts": [],
    "docs": [],
    "pdfs": [],
    "xls": [],
    "other": []
}

DEFAULT_RESPONSE = \
    response = {
        "status_code": "",
        "status_message": "",
        "user_id": "",
        "bot_id": "",
        "response": {
            "cards": [

            ],
            "images": [

            ],
            "videos": [

            ],
            "choices": [

            ],
            "recommendations": [

            ],
            "google_search_results": [

            ],
            "speech_response": {
                "text": ""
            },
            "ssml_response": {
                "text": ""
            },
            "text_response": {
                "text": "",
                "modes": {
                    "is_typable": "true",
                    "is_button": "true",
                    "is_slidable": "false",
                    "is_date": "false",
                    "is_dropdown": "false"
                },
                "modes_param": {
                    "is_slidable": {
                        "max": "",
                        "min": "",
                        "step": ""
                    }
                }
            },
            "is_flow_ended": False,
            "is_authentication_required": False,
            "is_bot_switch": False,
            "is_user_authenticated": False
        }
    }

DEFAULT_WEBHOOK_RESPONSE = {
    "fulfillmentText": "",
    "fulfillmentMessages": [],
    "source": "www.google.com",
    "payload": {
        "google": {
            "expectUserResponse": True,
            "richResponse":
            {
                "items":
                [
                    {
                        "simpleResponse": {
                            "textToSpeech": "There are some network \
                            issues. Please try again later.",
                            "displayText": "There are some network \
                            issues. Please try again later."
                        }
                    },
                ],
            }
        },
        "facebook": {
            "text": "Hello, Facebook!"
        },
        "slack": {
            "text": "Hello, Slack."
        }
    }
}

DEFAULT_WEBHOOK_SYSTEM_INTENT = {
    "systemIntent":
    {
        "intent": "actions.intent.OPTION",
        "data":
        {
            "@type": "type.googleapis.com/google.actions.v2.OptionValueSpec",
            "listSelect":
            {
                "items":
                [

                ]
            }
        }
    }
}

DEFAULT_WEBHOOK_CARD_RESPONSE = {
    "basicCard": {
        "title": "",
        "image": {
            "url": "",
            "accessibilityText": ""
        },
        "buttons": [

        ],
        "imageDisplayOptions": "WHITE"
    }
}

DEFAULT_CAROUSEL_BROWSE = {
    "carouselBrowse":
    {
        "items":
        [

        ]
    }
}

DEFAULT_CAROUSER_SELECT = {
    "carouselSelect": {
        "items": [
            {
                "title": "Math & prime numbers",
                "description": "42 is an abundant number because the \
                sum of its proper divisors 54 is greater",
                "image": {
                    "url": "https://img-d02.moneycontrol.co.in/\
                    news_image_files/2015/356x200/i/\
                    ICICI_Bank_4655_356.jpg",
                    "accessibilityText": "Math & prime numbers"
                }
            }
        ]
    }
}

month_to_num_dict = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

MAX_INTENT_PER_PAGE = 50


ASK_FOR_USER_LOCATION = {
    "fulfillmentText": "",
    "fulfillmentMessages": [],
    "source": "www.google.com",
    "payload": {
        "google": {
            "expectUserResponse": True,
            "systemIntent": {
                "intent": "actions.intent.PERMISSION",
                "data": {
                    "@type": "type.googleapis.com/google.actions.v2.PermissionValueSpec",
                    "optContext": "Raj",
                    "permissions": [
                        "DEVICE_PRECISE_LOCATION"
                    ]
                }
            }
        }
    }
}


BOT_POSITION_CHOICES = (  # ("left", "left"), ("right", "right"),
    ("bottom-right", "bottom-right"),
    ("top-right", "top-right"),
    ("bottom-left", "bottom-left"),
    ("top-left", "top-left"))

POST_PROCESSOR_BASE_PYTHON_CODE = "from EasyChatApp.utils import logger\nimport sys\ndef f(x):\n    json_response = {}\n    json_response['status_code'] = '500'\n    json_response['status_message'] = 'Internal server error.'\n    json_response['child_choice'] = ''\n    json_response['API_REQUEST_PACKET'] = {}\n    json_response['API_RESPONSE_PACKET'] = {}\n    global result_dict\n    json_response['data'] = {}\n    try:\n        #write your code here\n        json_response['status_code'] = '200'\n        json_response['print'] = 'Hello world!'\n        return json_response\n    except Exception as e:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('PostProcessorContent : ' + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        json_response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return json_response"  # noqa: F841

PIPE_PROCESSOR_BASE_PYTHON_CODE = "from EasyChatApp.utils import logger\nimport sys\ndef f(x):\n    json_response = {}\n    json_response['status_code'] = '500'\n    json_response['status_message'] = 'Internal server error.'\n    json_response['recur_flag'] = False\n    json_response['message'] = 'testing'\n    json_response['API_REQUEST_PACKET'] = {}\n    json_response['API_RESPONSE_PACKET'] = {}\n    json_response['data'] = {}\n    global result_dict\n    try:\n        #write your code here\n        json_response['status_code'] = '200'\n        json_response['print'] = 'Hello world!'\n        return json_response\n    except Exception as e:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('PipeProcessorContent : ' + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        json_response['status_code'] = '500'\n        json_response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return json_response"  # noqa: F841

API_TREE_BASE_PYTHON_CODE = "from EasyChatApp.utils import logger\nimport sys\ndef f():\n    response = {}\n    response['status_code'] = 500\n    response['status_message'] = 'Internal server error.'\n    response['data'] = {}\n    response['cards'] = []\n    response['choices'] = []\n    response['images'] = []\n    response['videos'] = []\n    response['recommendations'] = []\n    response['API_REQUEST_PACKET'] = {}\n    response['API_RESPONSE_PACKET'] = {}\n    response['dynamic_widget_type'] = ''\n    response['modes'] = {}\n    response['modes_param'] = {}\n    global result_dict\n    try:\n        #write your code here\n        response['status_code'] = '200'\n        response['print'] = 'Hello world!'\n        return response\n    except Exception as e:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('ApiTreeContent : ' + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        response['status_code'] = 500\n        response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return response"  # noqa: F841

FIELD_PROCESSOR_BASE_PYTHON_CODE = "from EasyChatApp.utils import logger\nimport sys\ndef f(x):\n    json_response = {}\n    global result_dict\n    json_response['options'] = []\n    json_response['text_field_value'] = ''\n    json_response['range_slider_min_value'] = ''\n    json_response['range_slider_max_value'] = ''\n    json_response['phone_widget_data'] = []\n    try:\n        #write your code here\n        json_response['status_code'] = '200'\n        json_response['print'] = 'Hello world!'\n        return json_response\n    except Exception as e:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('FieldProcessorContent : ' + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        json_response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return json_response"

POST_PROCESSOR_BASE_JAVA_CODE = """import java.util.*;
import org.json.simple.JSONObject;
public class EasyChatConsole {
  public static void main(String[] args){
    String input_x = args[0];
    JSONObject json_response = new JSONObject();
    json_response.put("status_code", "500");
    json_response.put("status_message", "Internal server error.");
    json_response.put("child_choice", "");
    json_response.put("data", new JSONObject());
    json_response.put("API_REQUEST_PACKET", new JSONObject());
    json_response.put("API_RESPONSE_PACKET", new JSONObject());
    try{
        /**write your code here*/
        json_response.put("status_code", "200");
        json_response.put("status_message", "SUCCESS");
        System.out.println(json_response);
    }catch(Exception e){
        json_response.put("status_code", "500");
        json_response.put("status_message", "ERROR :-  "+e.toString());
        System.out.println(json_response);
    }
 }
}"""

PIPE_PROCESSOR_BASE_JAVA_CODE = """import java.util.*;
import org.json.simple.JSONObject;
public class EasyChatConsole {
  public static void main(String[] args){
    String input_x = args[0];
    JSONObject json_response = new JSONObject();
    json_response.put("status_code", "500");
    json_response.put("status_message", "Internal server error.");
    json_response.put("recur_flag", true);
    json_response.put("message","testing");
    json_response.put("data", new JSONObject());
    json_response.put("API_REQUEST_PACKET", new JSONObject());
    json_response.put("API_RESPONSE_PACKET", new JSONObject());
    try{
        /**write your code here*/
        json_response.put("status_code", "200");
        json_response.put("status_message", "SUCCESS");
        System.out.println(json_response);
    }catch(Exception e){
        json_response.put("status_code", "500");
        json_response.put("status_message", "ERROR :-  "+e.toString());
        System.out.println(json_response);
    }
 }
}"""

API_TREE_BASE_JAVA_CODE = """import java.util.*;
import org.json.simple.JSONObject;
public class EasyChatConsole {
  public static void main(String[] args){
    JSONObject json_response = new JSONObject();
    json_response.put("status_code", "500");
    json_response.put("status_message", "Internal server error.");
    json_response.put("data", new JSONObject());
    json_response.put("cards", new ArrayList());
    json_response.put("choices", new ArrayList());
    json_response.put("images", new ArrayList());
    json_response.put("videos", new ArrayList());
    json_response.put("recommendations", new ArrayList());
    json_response.put("API_REQUEST_PACKET", new JSONObject());
    json_response.put("API_RESPONSE_PACKET", new JSONObject());
    try{
        /**write your code here*/
        json_response.put("status_code", "200");
        json_response.put("status_message", "SUCCESS");
        System.out.println(json_response);
    }catch(Exception e){
        json_response.put("status_code", "500");
        json_response.put("status_message", "ERROR :-  "+e.toString());
        System.out.println(json_response);
    }
 }
}"""

API_TREE_BASE_PHP_CODE = """<?php\nfunction f($x){
    $json_response = array(
        "status_code"=>"500",
        "status_message"=>"Internal server error.",
        "data"=> array(),
        "cards"=> array(),
        "choices"=> array(),
        "images"=> array(),
        "videos"=> array(),
        "recommendations"=> array(),
        "API_REQUEST_PACKET"=> array(),
        "API_RESPONSE_PACKET"=> array(),
    );
    try{
        // write your code here
        $json_response["status_code"] = "200";
        $json_response["status_message"] = "SUCCESS";
        return $json_response;
    }catch(Exception $e){
        $json_response["status_code"] = "500";
        $json_response["status_message"] = "Error :- " + strval($e);
        return $json_response;
    }
}
?>
"""

POST_PROCESSOR_BASE_PHP_CODE = """<?php\nfunction f($x){
    $json_response = array(
        "status_code"=>"500",
        "status_message"=>"Internal server error.",
        "child_choice"=> "",
        "data"=> array(),
        "API_REQUEST_PACKET"=> array(),
        "API_RESPONSE_PACKET"=> array(),
    );
    try{
        // write your code here
        $x = trim(preg_replace('/\s+/', ' ', $x));
        $json_response["status_code"] = "200";
        $json_response["status_message"] = "SUCCESS";
        return $json_response;
    }catch(Exception $e){
        $json_response["status_code"] = "500";
        $json_response["status_message"] = "Error :- " + strval($e);
        return $json_response;
    }
}
?>
"""

PIPE_PROCESSOR_BASE_PHP_CODE = """<?php\nfunction f($x){
    $json_response = array(
        "status_code"=>"500",
        "status_message"=>"Internal server error.",
        "recur_flag"=> true,
        "message"=> "testing",
        "data"=> array(),
        "API_REQUEST_PACKET"=> array(),
        "API_RESPONSE_PACKET"=> array(),
    );
    try{
        // write your code here
        $x = trim(preg_replace('/\s+/', ' ', $x));
        $json_response["status_code"] = "200";
        $json_response["status_message"] = "SUCCESS";
        return $json_response;
    }catch(Exception $e){
        $json_response["status_code"] = "500";
        $json_response["status_message"] = "Error :- " + strval($e);
        return $json_response;
    }
}
?>
"""

API_TREE_BASE_JS_CODE = """function f(){
    response = {}
    response['status_code'] = 500
    response['status_message'] = 'Internal server error.'
    response['data'] = {}
    response['cards'] = []
    response['choices'] = []
    response['images'] = []
    response['videos'] = []
    response['recommendations'] = []
    response['API_REQUEST_PACKET'] = {}
    response['API_RESPONSE_PACKET'] = {}
    try{
        //write your code here
        response['status_code'] = "200"
        response['print'] = 'Hello world!'
        return response
    }catch(e){
        response['status_code'] = 500
        response['status_message'] = 'ERROR :-  '+e.toString()
        return response
    }
}
"""

POST_PROCESSOR_BASE_JS_CODE = """function f(x){
    json_response = {}
    json_response['status_code'] = '500'
    json_response['status_message'] = 'Internal server error.'
    json_response['child_choice'] = ''
    json_response['data'] = {}
    json_response['API_REQUEST_PACKET'] = {}
    json_response['API_RESPONSE_PACKET'] = {}
    try{
        //write your code here
        json_response['status_code'] = '200'
        json_response['print'] = 'Hello world!'
        json_response['status_message'] = "SUCCESS"
        return json_response
    }catch(e){
        json_response['status_code'] = '500'
        json_response['status_message'] = 'ERROR :-  ' + e.toString()
        return json_response
    }
}
"""

PIPE_PROCESSOR_BASE_JS_CODE = """function f(x){
    json_response = {}
    json_response['status_code'] = '500'
    json_response['status_message'] = 'Internal server error.'
    json_response['recur_flag'] = false
    json_response['message'] = 'testing'
    json_response['data'] = {}
    json_response['API_REQUEST_PACKET'] = {}
    json_response['API_RESPONSE_PACKET'] = {}
    try{
        //write your code here
        json_response['status_code'] = '200'
        json_response['print'] = 'Hello world!'
        json_response['status_message'] = "SUCCESS"
        return json_response
    }catch(e){
        json_response['status_code'] = '500'
        json_response['status_message'] = 'ERROR :-  ' + e.toString()
        return json_response
    }
}
"""
WHATAPP_WEBHOOK_BASE_PYTHON_CODE = """def whatsapp_webhook(request_packet):
    from EasyChatApp.utils import logger
    import sys
    json_response = {}
    json_response["status_code"] = 500
    json_response["status_message"] = "Internal Server Error"
    json_response["mobile_number"] = ""
    try:
        logger.info(request_packet, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        # Write your whatsapp logic here
        json_response["status_code"] = 200
        json_response["status_message"] = "success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("whatsapp_webhook: " +str(e) +" at " + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        status_message = "whatsapp_webhook: " +str(e) +" at " + str(exc_tb.tb_lineno)
        json_response["status_message"] = status_message

    return json_response
"""

WHATAPP_WEBHOOK_EXTRA_FUNCTION_BASE_PYTHON_CODE = """def whatsapp_push_notification(user_mobile_number):
    from EasyChatApp.utils import logger
    import sys
    json_response = {}
    json_response["status_code"] = 500
    json_response["status_message"] = "Internal Server Error"
    try:
        logger.info(request_packet, extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        push_message = 'Thanks for connecting with us, hope we could help you with your queries. If you have a minute, would you like to rate our service on a scale of 0 to 10, 0 for extremely dissatisfied, 10 for Totally Satisfied and would recommend to others.'
        # Write your whatsapp logic here
        json_response["status_code"] = 200
        json_response["status_message"] = "success"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("whatsapp_push_notification: " +str(e) +" at " + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        status_message = "whatsapp_push_notification: " +str(e) +" at " + str(exc_tb.tb_lineno)
        json_response["status_message"] = status_message

    return json_response
"""

POST_PROCESSOR_BASE_PYTHON_CODE_TEST = "from EasyChatApp.utils import logger\nimport sys\ndef f(x):\n    json_response = {}\n    json_response['status_code'] = '500'\n    json_response['status_message'] = 'Internal server error.'\n    json_response['child_choice'] = 'testing'\n    json_response['data'] = {}\n    try:\n        #write your code here\n        json_response['status_code'] = '200'\n        json_response['print'] = 'Hello world!'\n        return json_response\n    except Exception as E:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('PostProcessorContent: %s at %s',str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        json_response['status_code'] = '500'\n        json_response['status_message'] = 'ERROR :-  '+str(E)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return json_response"

POST_PROCESSOR_BASE_PYTHON_CODE_TEST_206 = "from EasyChatApp.utils import logger\nimport sys\ndef f(x):\n    json_response = {}\n    json_response['status_code'] = '500'\n    json_response['status_message'] = 'Internal server error.'\n    json_response['child_choice'] = 'Bye'\n    json_response['data'] = {}\n    try:\n        #write your code here\n        json_response['status_code'] = '206'\n        json_response['print'] = 'Hello world!'\n        return json_response\n    except Exception as E:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('PostProcessorContent: %s at %s',str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        json_response['status_code'] = '500'\n        json_response['status_message'] = 'ERROR :-  '+str(E)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return json_response"

POST_PROCESSOR_BASE_PYTHON_CODE_TEST_308 = "from EasyChatApp.utils import logger\nimport sys\ndef f(x):\n    json_response = {}\n    json_response['status_code'] = '500'\n    json_response['status_message'] = 'Internal server error.'\n    json_response['child_choice'] = 'Bye'\n    json_response['data'] = {}\n    try:\n        #write your code here\n        json_response['status_code'] = '308'\n        json_response['print'] = 'Hello world!'\n        return json_response\n    except Exception as E:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('PostProcessorContent: %s at %s',str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        json_response['status_code'] = '500'\n        json_response['status_message'] = 'ERROR :-  '+str(E)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return json_response"

POST_PROCESSOR_BASE_PYTHON_CODE_TEST_NONE = "from EasyChatApp.utils import logger\nimport sys\ndef f(x):\n    json_response = {}\n    json_response['status_code'] = '500'\n    json_response['status_message'] = 'Internal server error.'\n    json_response['child_choice'] = 'Bye'\n    json_response['data'] = {}\n    try:\n        #write your code here\n        json_response['status_code'] = '500'\n        json_response['print'] = 'Hello world!'\n        return json_response\n    except Exception as E:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('PostProcessorContent: %s at %s',str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        json_response['status_code'] = '500'\n        json_response['status_message'] = 'ERROR :-  '+str(E)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return json_response"

API_TREE_BASE_PYTHON_CODE_TEST = "from EasyChatApp.utils import logger\nimport sys\ndef f():\n    response = {}\n    response['status_code'] = 500\n    response['status_message'] = 'Internal server error.'\n    response['data'] = {}\n    response['cards'] = []\n    response['choices'] = []\n    response['images'] = []\n    response['videos'] = []\n    response['recommendations'] = []\n    response['API_REQUEST_PACKET'] = {}\n    response['API_RESPONSE_PACKET'] = {}\n    try:\n        #write your code here\n        response['status_code'] = '200'\n        response['print'] = 'Hello world!'\n        return response\n    except Exception as E:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('ApiTreeContent: %s at %s',str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        response['status_code'] = 500\n        response['status_message'] = 'ERROR :-  '+str(E)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return response"

API_TREE_BASE_PYTHON_CODE_TEST_1 = "from EasyChatApp.utils import logger\nimport sys\ndef f():\n    response = {}\n    response['status_code'] = 500\n    response['status_message'] = 'Internal server error.'\n    response['data'] = {}\n    response['cards'] = []\n    response['choices'] = []\n    response['images'] = []\n    response['videos'] = []\n    response['recommendations'] = []\n    response['API_REQUEST_PACKET'] = {}\n    response['API_RESPONSE_PACKET'] = {}\n    try:\n        #write your code here\n        response['status_code'] = '500'\n        response['print'] = 'Hello world!'\n        return response\n    except Exception as E:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('ApiTreeContent: %s at %s',str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        response['status_code'] = 500\n        response['status_message'] = 'ERROR :-  '+str(E)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return response"

LANGUAGE_CHOICES = (
    ("1", "Python 3.6"),
    ("2", "Java"),
    ("3", "Php"),
    ("4", "JavaScript"),
)

ALEXA_TRAINING_JSON = {
    "interactionModel": {
        "languageModel": {
            "invocationName": "easychat bot",
            "intents": [
                {
                    "name": "ChatBot",
                    "slots": [
                        {
                            "name": "Intent",
                            "type": "OBFUSCATE_ICICI"
                        }
                    ],
                    "samples": [
                        "{Intent}"
                    ]
                },
                {
                    "name": "AMAZON.StopIntent",
                    "samples": [
                        "stop",
                        "bye bye"
                    ]
                },
                {
                    "name": "AMAZON.CancelIntent",
                    "samples": [
                        "cancel"
                    ]
                },
                {
                    "name": "AMAZON.HelpIntent",
                    "samples": [
                        "how can you help me"
                    ]
                },
                {
                    "name": "AMAZON.NavigateHomeIntent",
                    "samples": []
                }
            ],
            "types": [
                {
                    "name": "OBFUSCATE_ICICI",
                    "values": []
                }
            ]
        }
    }
}

WHATSAPP_REQUEST_PACKET = """
{
    'contacts': [
        {
            'profile': {
                'name': 'Test'
            },
            'wa_id': "MOBILE_NUMBER"
        }
    ],
    'messages': [
        {
            'from': "MOBILE_NUMBER",
            'id': '',
            'text': {
                'body': "TEXT_MESSAGE"
            },
            'timestamp': 'TIME_STAMP',
            'type': 'text'
        }
    ]
}"""

DEFAULT_PAGINATION_METADATA = {
    'total_count': '',
    'start_point': '',
    'end_point': '',
    'page_range': ['', ''],
    'has_next': '',
    'has_previous': '',
    'next_page_number': '',
    'previous_page_number': '',
    'number': '',
    'num_pages': '',
    'has_other_pages': ''
}

LILVECHAT_WHATSAPP_WEBHOOK_SAMPLE = """
from EasyChatApp.utils import *
from LiveChatApp.models import LiveChatCustomer, LiveChatUser
from LiveChatApp.utils import get_time, get_miniseconds_datetime
from EasyChatApp.models import *
from django.conf import settings
from EasyChatApp.utils_custom_encryption import CustomEncrypt
import emoji
import time
import json
import sys
import requests
import threading
import websocket

def get_jwt_token():
        url = "https://apis.rmlconnect.net/auth/v1/login/"
        headers = {
            "Content-Type":"application/json",
            }
        payload = {
            "username":"RMLBot2",
            "password":"Product@123"
        }

        resp = requests.post(url=url, headers=headers,data = json.dumps(payload))
        api_resp = json.loads(resp.text)
        JWT_TOKEN = api_resp["JWTAUTH"]
        return JWT_TOKEN

def sendWhatsAppTextMessage(message, phone_number):
    ''' A function to call send whatsapp text message API.'''
    import requests
    import urllib
    try:
        #       message = urllib.parse.quote(message.encode('utf-8'))
        phone_number = str(phone_number)
        phone_number = phone_number[-10:]
        phone_number = "+91" + str(phone_number)
        JWT_TOKEN = get_jwt_token()
        logger.info(message, extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "None"})
        url="https://apis.rmlconnect.net/wba/v1/messages"
        headers={
            "Authorization": JWT_TOKEN,
            "Content-Type":"application/json"
        }
        payload = {
            "phone": str(phone_number),
            "text": str(message)
        }
        logger.info(message, extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "None"})
        resp=requests.post(url=url,data=json.dumps(payload),headers=headers)
        resp=json.loads(resp.text)
        if str(resp["message"]) == "message received successfully":
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error: sendWhatsAppTextMessage: %s for %s", str(e), str(exc_tb.tb_lineno), str(phone_number), extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "None"})
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
def sendWhatsAppMediaMessage(filename, media_type, media_url, phone_number, caption = None):
    try:
        logger.info("=== Inside Send WA Media Message API ===", extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "None"})
        if media_type == "document" and caption == None:
            caption = "FileAttachment"
        elif caption == None:
            caption = ""
        JWT_TOKEN = get_jwt_token()
        url = "https://apis.rmlconnect.net/wba/v1/messages"
        headers = {
            'Authorization': JWT_TOKEN,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            "phone": "+"+phone_number,
            "media": {
                "type": media_type,
                "url": media_url,
                "file": filename,
                "caption": caption
            }
        }
        resp = requests.request("POST", url, headers=headers, data = json.dumps(payload), timeout=20, verify=True)
        content = json.dumps(resp.text)
        if str(resp.status_code) == "200" or str(resp.status_code) == "202":
            logger.info(media_type.upper()+" message sent successfully", extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "None"})
        else:
            logger.error("Failed to send "+media_type.upper()+" message: %s", extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "None"})
    except requests.Timeout as rt:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        response["status_message"] = str(e) + str(exc_tb.tb_lineno)
        logger.error("SendWhatsAppMediaMessage Timeout error: %s", str(e), str(exc_tb.tb_lineno), extra=log_param)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("SendWhatsAppMediaMessage Failed: %s at %s",
                    str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "None"})
        response["status_message"] = str(e) + str(exc_tb.tb_lineno)

def f(x):
    logger.info("Inside send_message_to_whatsapp", extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "None"})

    # response = {
    #     "user_id": USER_ID(MOBILE),
    #     "type": (text/file),
    #     "text_message": (message),
    #     "path": FILE_PATH,
    #     "channel": CHANNEL(Web/Whtasapp/Facebook/Alexa/Google),
    #     "bot_id": BOT_ID
    # }

    x = json.loads(x)
    try:
        if x["type"] == 'text':
            sendWhatsAppTextMessage(x["text_message"], x["user_id"])
        else:
            file_path = settings.EASYCHAT_HOST_URL + x["path"]
            message = x["text_message"]

            filename = file_path.split("/")[-1]
            msg_type = get_msg_type(filename)
            sendWhatsAppMediaMessage(filename, msg_type, file_path, x["user_id"], message)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside send_message_to_whatsapp: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "None"})
        pass
"""

LILVECHAT_FACEBOOK_WEBHOOK_SAMPLE = """
from django.conf import settings

from EasyChatApp.utils import *
from EasyChatApp.models import *

import sys
import json
import requests
import logging

logger = logging.getLogger(__name__)

def remove_tags(text):
    text = text.replace("<br>", "")
    text = text.replace("<b>", "")
    text = text.replace("</b>", "")
    text = text.replace("<i>", "")
    text = text.replace("</i>", "")
    text = text.replace("  ", " ")
    return text

def send_image(recipient_id, image_url, page_access_token):
    access_token = page_access_token
    params = {
        "access_token": access_token}

    headers = {
        "Content-Type": "application/json"
    }

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": str(image_url),
                    "is_reusable": False
                }
            }
        }
    })
    requests.post("https://graph.facebook.com/v2.6/me/messages",
                  params=params, headers=headers, data=data)

def send_message(recipient_id, message_text, page_access_token):
    access_token = page_access_token
    params = {
        "access_token": access_token}

    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "messaging_type": "RESPONSE",
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    requests.post("https://graph.facebook.com/v6.0/me/messages",
                  params=params, headers=headers, data=data)

def f(x):
    # response = {
    #     "user_id": USER_ID(MOBILE),
    #     "type": (text/file),
    #     "text_message": (message),
    #     "path": FILE_PATH,
    #     "channel": CHANNEL(Web/Whtasapp/Facebook/Alexa/Google),
    #     "bot_id": BOT_ID
    # }

    try:
        x = json.loads(x)
        bot_id = x["bot_id"]
        bot_obj = Bot.objects.get(pk=int(bot_id))
        user_id = x["user_id"]
        text_response = x["text_message"]

        channel_obj = Channel.objects.get(name="Facebook")
        bot_console_obj = BotChannel.objects.get(bot=bot_obj, channel=channel_obj)
        page_access_token = bot_console_obj.verification_token

        if x["type"] == 'text':
            send_message(user_id, text_response, page_access_token)
        else:
            file_path = settings.EASYCHAT_HOST_URL + x["path"]
            send_image(sender, file_path, page_access_token)
            send_message(user_id, text_response, page_access_token)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside send_message_to_facebook: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "Facebook", 'bot_id': "None"})
        pass
"""

STICKY_BUTTON_DISPLAY_CHOICES = (
    ("Button", "Button"),
    ("Menu", "Menu"),
)

ROLES_MIS = (
    ("1", "Marked"),
    ("2", "Not Marked"),
)

CHARACTER_LIMIT_LARGE_TEXT = 500
CHARACTER_LIMIT_MEDIUM_TEXT = 100
CHARACTER_LIMIT_SMALL_TEXT = 25
DEFAULT_NO_OF_DAYS_FOR_DAILY_MAILER_ANALYTICS = 7

ALLOWED_IMAGE_FILE_EXTENTIONS = ["png", "PNG", "JPG", "JPEG",
                                 "jpg", "jpeg", "jpe", "bmp", "gif", "tiff", "exif", "jfif"]

allowed_file_extensions = ALLOWED_IMAGE_FILE_EXTENTIONS + ["webm", "mpg", "mp2",
                                                           "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt", "flv", "swf", "avchd", "pdf", "docs", "docx", "doc", "PDF",
                                                           "zip", "rar", "rpm", "z", "tar.gz", "pkg", "odt", "rtf", "tex", "txt", "wks", "wkp"]

EXPORT_BOT_AS_MULITILINGUAL_EXCEL_INSTRUCTIONS = ["This sheet is to import & export intents and add language translations",
                                                  'Language text can be translated from "IntentTranslation" & "Response Translation" workbook',
                                                  "Keep the first column (English) unchanged",
                                                  "Corresponding translated text will be added to the language columns",
                                                  "Note: Empty fields will automatically get transalted or will not be reflected",
                                                  "Note: On response language translation, removing HTML text may create errors",
                                                  "Note: It is not suggested to add/remove rows when importing",
                                                  'Note: You are not allowed to edit columns Intent/Tree Primary Key columns in "IntentTranslation" workbook',
                                                  'Note: You are not allowed to edit columns Response Primary Key columns in "Response Translation" workbook',
                                                  ]

SIGN_IN_PROCESSOR_BASE_PYTHON_CODE = "from EasyChatApp.utils import logger\nimport sys\ndef f(x):\n    json_response = {}\n    json_response['status_code'] = '500'\n    json_response['status_message'] = 'Internal server error.'\n    global result_dict\n    try:\n        #write your code here\n        json_response['status_code'] = '200'\n        json_response['print'] = 'Hello world!'\n        return json_response\n    except Exception as e:\n        exc_type, exc_obj, exc_tb = sys.exc_info()\n        logger.error('SignInProcessorContent : ' + str(e) + str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})\n        json_response['status_code'] = '500'\n        json_response['status_message'] = 'ERROR :-  '+str(e)+ ' at line no: ' +str(exc_tb.tb_lineno)\n        return json_response"  # noqa: F841

DEFAULT_THEME_IMAGE_DICT = {
    "theme_1": ["/static/EasyChatApp/img/theme_1_0.png", "/static/EasyChatApp/img/theme_1_1.png"],
    "theme_2": ["/static/EasyChatApp/img/theme_2_0.png", "/static/EasyChatApp/img/theme_2_1.png"],
    "theme_3": ["/static/EasyChatApp/img/theme_3_0.png", "/static/EasyChatApp/img/theme_3_1.png"],
    "theme_4": ["/static/EasyChatApp/img/theme_4_0.svg", "/static/EasyChatApp/img/theme_4_1.svg"]
}

EVENT_CHOICES = (
    ("import_bot", "Import Bot"),
    ("build_bot", "Build Bot"),
    ("faq_extraction", "FAQ Extraction"),
    ("sync_products", "Sync Products from Facebook"),
    ("upload_catalogue_products", "Upload Catalogue Products using CSV")
)

DEFAULT_LEAD_TABLE_COL = [
    {
        'name': 'user_query',
        'display_name': ' User Query',
        'selected': "true",
    },
    {
        'name': 'bot_response',
        'display_name': 'Bot Response',
        'selected': "true",
    },
    {
        'name': 'time',
        'display_name': 'Time',
        'selected': "true",
    },
    {
        'name': 'intent_recognized',
        'display_name': 'Intent Recognized',
        'selected': "true",
    },
    {
        'name': 'user_id',
        'display_name': 'User ID',
        'selected': "true",
    },
    {
        'name': 'session_id',
        'display_name': 'Session ID',
        'selected': "true",
    },
    {
        'name': 'channel',
        'display_name': 'Channel',
        'selected': "true",
    },
    {
        'name': 'user_feedback',
        'display_name': 'User Feedback',
        'selected': "true",
    },
    {
        'name': 'intent_feedback',
        'display_name': 'Intent Feedback',
        'selected': "true",
    },
    {
        'name': 'location',
        'display_name': 'Location',
        'selected': "true",
    },
    {
        'name': 'variation_responsible',
        'display_name': 'Variation Responsible',
        'selected': "true",
    },

    {
        'name': 'percentage_match',
        'display_name': 'Percentage Match',
        'selected': "true",
    },
]

WSP_CHOICES = (
    ("1", "Ameyo"),
    ("2", "Gupshup"),
    ("3", "RML"),
    ("4", "ACL"),
    ("5", "Netcore")
)

FLAGGED_QUERY_TYPES = (
    ("1", "False Positive"),
    ("2", "Not False Positive")
)

BOT_DELETED_ERROR_MESSAGE = "Requested bot was deleted"

DEFAULT_VOICE_MODULATION = {
    "selected_tts_provider": "Microsoft",
    "Microsoft": {
        "tts_language": "en-IN",
        "tts_voice": "NeerjaNeural",
        "tts_speaking_style": "general",
        "tts_speaking_speed": 1,
        "tts_pitch": 1,
        "asr_provider": "Google",
        "allow_barge": "false"
    },
    "Google": {
        "tts_language": "en-IN",
        "tts_voice": "Standard-A",
        "tts_speaking_style": "basic",
        "tts_speaking_speed": 1,
        "tts_pitch": 0,
        "asr_provider": "Google",
        "allow_barge": "false"
    },
    "AwsPolly": {
        "tts_language": "en-IN",
        "tts_voice": "Aditi",
        "tts_speaking_style": "standard",
        "tts_speaking_speed": 100,
        "tts_pitch": 0,
        "asr_provider": "Google",
        "allow_barge": "false"
    }
}

WIDGETS_TOGGLE_NAME_MAPPER = {
    "is_range_slider": "range_slider",
    "is_calender": "calendar_picker",
    "is_radio_button": "radio_button",
    "is_check_box": "checkbox",
    "is_drop_down": "drop_down",
    "is_video_recorder_allowed": "video_record",
    "is_attachment_required": "file_attach",
    "is_create_form_allowed": "form"
}

TRAINING_DATA_TYPE_CHOICES = (
    ("1", "Intent Level"),
    ("2", "Tree Level")
)

RATE_LIMIT_FOR_EXTERNAL_API_IN_ONE_MINUTE = 100

EXTERNAL_API_TOKEN_CREATION_LIMIT_PER_MINUTE = 100

AUTH_TOKEN_ACCESS_TYPE_CHOICES = (
    ("1", "Auth Token Generation"),
    ("2", "Analytics Access")
)

EXTERNAL_API_FUNCTION_EXEC_TIME_LIMIT = 20  # In Seconds

DEFAULT_VOICE_BOT_API_KEY = "64d168e44dc4b5d7bbdb475317398a8fa4022d07d01c3aee"

DEFAULT_VOICE_BOT_API_TOKEN = "fff3bfb413deeba7ebb1553b597c9c94881b040731f4b923"

DEFAULT_VOICE_BOT_SUBDOMAIN = "1"

VOICE_BOT_SUBDOMAIN_CHOICES = (
    ("1", "api.in.exotel.com"),
    ("2", "api.exotel.com")
)

DEFAULT_VOICE_BOT_SID = "ameyo1m"

DEFAULT_SILENCE_THRESHOLD = 2

DEFAULT_SILENCE_RESPONSE = "Hey! we could not hear anything from your side, are you still there?"

DEFAULT_SILENCE_TERMINATION_RESPOSNE = "Sorry, we asked a couple of times but did not get any response from your side. Thanks for calling us!"

DEFAULT_LOOP_THRESHOLD = 2

DEFAULT_AGENT_HANDOVER = False

DEFAULT_LOOP_TERMINATION_RESPONSE = "Sorry, it seems that we have detected a loop and reached the retry limit. Thanks for calling us!"

DEFAULT_LOOP_AGENT_HANDOVER_RESPONSE = "Sorry, it seems that we have detected a loop and reached the retry limit. Please wait while we connect you to our assistant shortly."

REPEAT_EVENT_TRAINING_SENTENCES = ["unable to hear you", "Sorry, didn't get you, can you repeat?", "Sorry, didn't get you", "can you repeat?", "did not hear you", "come again", "please come again"]

TREE_LEVEL_VOICE_BOT_CONFIGURATIONS = {"barge_in": False}

DEFAULT_SILENCE_EVENT_TRIGGER_TIMEOUT = 5000

DEFAULT_FALLBACK_RESPONSE = "Apologies, I only understand English and Hindi for now. Thanks for calling us."

ALEXA_DEFAULT_RESPONSE = {
    "authentication": "To use this service, kindly link your account with Cogno AI",
    "recommendation": " You can also ask me queries as follows . ",
    "error": "Sorry, we are unable to process your request due to some internal issue. Kindly try again later.",
    "choice": " Please say ",
    "initial_recommendation": "Please say {} for {} . ",
}

GOOGLE_HOME_DEFAULT_RESPONSE = {
    "initial_recommendation": "Please say {} for {} . ",
}

USER_DROPOFF_CHOICES = (
    ("1", "terminate"),
    ("2", "timeout"),
    ("3", "miscellaneous")
)

FILE_ACCESS_MANAGEMENT_EXPIRE_TIME_LIMIT = 24  # In Hours

LIVECHAT_PROVIDERS = (
    ("cogno_livechat", "Cogno LiveChat"),
    ("ameyo_fusion", "Ameyo Fusion")
)

DEFAULT_LIVECHAT_PROVIDER = "cogno_livechat"

BLOCK_TYPE_CHOICES = (
    ("spam_message", "Spam Message"),
    ("keyword", "Keyword")
)

BLOCK_SPAM_WARNING_THRESOLD_MAX_VALUE = 263
BLOCK_SPAM_BLOCK_THRESOLD_MAX_VALUE = 264
BLOCK_SPAM_BLOCK_MAX_DURATION = 24

CACHE_KEY_EASYCHAT_WHATSAPP_WEBHOOK = "EASYCHAT_WHATSAPP_WEBHOOK_"

INTENT_TREE_NAME_CHARACTER_LIMIT = 500

SELF_SIGNUP_USER_EXPIRATION_TIME = 1  # In Hours

FACEBOOK_GRAPH_BASE_URL = "https://graph.facebook.com/v14.0/"

WHATSAPP_CSAT_FEEDBACK_ID = "00000000-000-0000-0000-000000000000"

INTENT_ICON_CHOICES_INFO = [
    {
        "name": "Initial Questions",
        "value": "1"
    },
    {
        "name": "Failure Recommendations",
        "value": "2"
    },
    {
        "name": "Quick Recommendations",
        "value": "3"
    },
    {
        "name": "Did you mean queries",
        "value": "4"
    },
    {
        "name": "Go Back",
        "value": "5"
    },
    {
        "name": "Do not disturb",
        "value": "6"
    },
    {
        "name": "Suggest LiveChat Intent",
        "value": "7"
    }
]

DEFAULT_INTENT_ICON_CHANNEL_CHOICES_INFO = {
    "web": ["1", "2", "3", "4", "5", "6", "7"],
    "android": ["1", "2", "3", "4", "5", "6", "7"],
    "ios": ["1", "2", "3", "4", "5", "6", "7"]
}

DEFAULT_DO_NOT_TRANSLATE_KEYWORDS = ["SIP", "STP", "NFO", "EMI", "NAV", "ETFS", "NEO", "NCT", "IPO", "API", "KYC", "PAN", "URN", "ATM", "VISA", "FD", "RD", "GST", "VKYC", "UPI", "NEFT", "SWT", "SMS", "OTP"]

OLDER_NEWER_LANGUAGE_CODE_MAPPING = {
    "iw": "he",
    "in": "id",
    "ji": "yi"
}

ANALYTICS_EXPORT_CHOICES = (
    ("combined_global_export", "Combined Analytics Global Export"),
    ("message_analytics", "Message Analytics"),
    ("user_analytics", "User Analytics"),
    ("most_frequent_intents", "Most Frequent Intents"),
    ("intent_wise_chartflow", "Intent Wise ChartFlow"),
    ("category_wise_frequent_questions", "Category Wise Frequent Questions"),
    ("unanswered_questions", "Unanswered Questions"),
    ("intuitive_questions", "Intuitive Questions"),
    ("device_specific_analytics", "Device Specific Analytics"),
    ("hour_wise_analytics", "Hour Wise Analytics"),
    ("whatsapp_catalogue_analytics", "WhatsApp Catalogue Combined Analytics"),
    ("most_used_form_assist_intents", "Most Used Form Assist Intents"),
    ("user_nudge_analytics", "User Nudge Analytics"),
    ("flow_conversion_analytics", "Flow Conversion Analytics"),
    ("intent_conversion_analytics", "Intent Conversion Analytics"),
    ("livechat_conversion_analytics", "LiveChat Conversion Analytics"),
    ("dropoff_conversion_analytics", "DropOff Conversion Analytics"),
    ("whatsapp_block_analytics", "WhatsApp Block Analytics"),
    ("catalogue_conversion_analytics", "WhatsApp Catalogue Conversion Analytics"),
    ("welcome_conversion_analytics", "Welcome Banner Click Rates"),
    ("traffic_conversion_analytics", "Traffic Conversion Analytics")
)
