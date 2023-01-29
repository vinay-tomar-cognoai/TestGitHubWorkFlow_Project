from EasyChatApp.utils_bot import get_translated_text_with_api_status
from EasyChatApp.utils_conversion_analytics import conversion_intent_analytics_translator, create_flow_conversion_analytics_excel, create_intent_conversion_analytics_excel, create_livechat_conversion_analytics_excel, create_dropoff_conversion_analytics_excel, create_whatsapp_block_analytics_excel, create_whatsapp_catalogue_analytics_csv, get_welcome_conversion_analytics_export_file_path, get_traffic_conversion_analytics_export_file_path
from EasyChatApp.utils_execute_query import *
from EasyChatApp.utils_api_analytics import get_combined_device_specific_analytics_list, get_combined_catalogue_analytics_list
from EasyChatApp.email_html_constants import get_email_head_from_email_html_constant
from EasyChatApp.constants_whatsapp_csat_processors import *
import math
from xlwt import Workbook
from zipfile import ZipFile
from django.core.cache import cache

from django.db.models import Sum
import pytz


def get_channel_list(Channel):
    try:
        channel_list = []

        channel_objs = Channel.objects.filter(is_easychat_channel=True)
        for channel_obj in channel_objs:
            channel_list.append(
                {"name": channel_obj.name, "icon": channel_obj.icon})

        return channel_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_channel_list! %s %s",
                     str(e), str(exc_tb.tb_lineno),
                     extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None',
                            'bot_id': 'None'})
        return []


def generate_random_password():
    # maximum length of password needed
    # this can be changed to suit your password length
    MAX_LEN = 12

    # declare arrays of the character that we need in out password
    # Represented as chars to enable easy string concatenation
    DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    LOCASE_CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                         'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                         'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                         'z']

    UPCASE_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                         'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q',
                         'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                         'Z']

    SYMBOLS = ['@', '#', '$']

    # combines all the character arrays above to form one array
    COMBINED_LIST = DIGITS + UPCASE_CHARACTERS + LOCASE_CHARACTERS + SYMBOLS

    # randomly select at least one character from each character set above
    rand_digit = random.choice(DIGITS)
    rand_upper = random.choice(UPCASE_CHARACTERS)
    rand_lower = random.choice(LOCASE_CHARACTERS)
    rand_symbol = random.choice(SYMBOLS)

    # combine the character randomly selected above
    # at this stage, the password contains only 4 characters but
    # we want a 12-character password
    temp_pass = rand_digit + rand_upper + rand_lower + rand_symbol

    # now that we are sure we have at least one character from each
    # set of characters, we fill the rest of
    # the password length by selecting randomly from the combined
    # list of character above.
    for value in range(MAX_LEN - 4):
        temp_pass = temp_pass + random.choice(COMBINED_LIST)
        # convert temporary password into array and shuffle to
        # prevent it from having a consistent pattern
        # where the beginning of the password is predictable

        temp_pass_list = [char for char in temp_pass]
        # temp_pass_list = array.array('d', temp_pass)
        random.shuffle(temp_pass_list)

    # traverse the temporary password array and append the chars
    # to form the password
    password = ""
    for value in temp_pass_list:
        password = password + value

    # print out password
    return password


def generate_query_token():
    query_token_id = EasyChatQueryToken.objects.create()
    return str(query_token_id.token)


"""
function: check_for_expired_credentials
input_params:
    user_obj: User obj 
    SandboxUser: refrence to modal SandboxUser
Returns true if the sandbox user credentials are expired 
"""


def check_for_expired_credentials(user_obj, SandboxUser):
    try:
        sandbox_user_obj = SandboxUser.objects.filter(
            username=user_obj.username)[0]
        if sandbox_user_obj.is_expired:
            return True
        else:
            tz = pytz.timezone(settings.TIME_ZONE)
            current_time = timezone.now().astimezone(tz)
            expiration_date = sandbox_user_obj.will_expire_on.astimezone(tz)
            if current_time > expiration_date:
                sandbox_user_obj.is_expired = True
                sandbox_user_obj.save()
                return True

        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_for_expired_credentials : " + str(e) + str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return False


"""
function: send_whatsapp_endpoint_fail_mail
input_params:
    from_email_id,: email id from which email wil be sent
    from_email_id_password: password of email id from which email wil be sent
    to_emai_id: email id to which email wil be sent
    api_name: name of failed api
    api_request_packet: endpoint request packet
    api_response_packet: endpoint response packet
    bot_obj:

send email
"""


def send_whatsapp_endpoint_fail_mail(api_name, api_request_packet, api_response_packet, bot_obj, to_email_id):
    message = "Request you to connect with the WhatsApp Vendor and look into the issue."
    new_parameters_list = {
        "intent_name": "none",
        "intent_pk": "none",
        "tree_name": "none",
        "tree_id": "none",
        "bot_id": str(bot_obj.id)
    }
    body = return_html_of_mail(
        bot_obj.name, api_name, api_request_packet, api_response_packet, message, new_parameters_list)

    send_email_to_customer_via_awsses(
        to_email_id, "WhatsApp API Error in " + bot_obj.name, body)


"""
function: check_and_send_whatsapp_endpoint_failed_mail
input_params:
    api_name: name of failed api
    api_request_packet: api request packet
    api_response_packet: api response packet
    bot_obj:
    bot_channel_obj:

Checks the time of last send mail for the same API. If time exceeds mail_sender_time_interval, then sends new mail and update mail sent time
"""


def check_and_send_whatsapp_endpoint_failed_mail(api_name, api_request_packet, api_response_packet, bot_obj,
                                                 bot_channel_obj, EasyChatMAil):
    try:
        config = get_developer_console_settings()
        from_email_id = config.email_host_user

        easychat_mail_obj = EasyChatMAil.objects.filter(
            bot=bot_obj, api_name=api_name)
        if easychat_mail_obj:
            easychat_mail_obj = easychat_mail_obj[0]
            import pytz
            tz = pytz.timezone(settings.TIME_ZONE)
            timer_value = bot_channel_obj.mail_sender_time_interval
            last_mail_sent_date = easychat_mail_obj.last_mail_sent_date.astimezone(
                tz)
            current_time = timezone.now().astimezone(tz)

            if (current_time - last_mail_sent_date).total_seconds() > int(timer_value) * 60:
                mail_sent_to_list = json.loads(
                    bot_channel_obj.mail_sent_to_list)["items"]

                for item in mail_sent_to_list:
                    thread = threading.Thread(target=send_whatsapp_endpoint_fail_mail, args=(
                        api_name, api_request_packet, api_response_packet, bot_obj, item), daemon=True)
                    thread.start()
                    logger.info("Threading started...", extra={
                        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None',
                        'bot_id': str(bot_obj.pk)})

                easychat_mail_obj.last_mail_sent_date = timezone.now()
                easychat_mail_obj.mail_sent_from = from_email_id
                easychat_mail_obj.mail_sent_to = json.dumps(
                    {"items": mail_sent_to_list})
                easychat_mail_obj.save()
        else:
            mail_sent_to_list = json.loads(
                bot_channel_obj.mail_sent_to_list)["items"]

            for item in mail_sent_to_list:
                thread = threading.Thread(target=send_whatsapp_endpoint_fail_mail, args=(
                    api_name, api_request_packet, api_response_packet, bot_obj, item), daemon=True)
                thread.start()
                logger.info("Threading started...", extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None',
                    'bot_id': str(bot_obj.pk)})

            EasyChatMAil.objects.create(bot=bot_obj, api_name=api_name, last_mail_sent_date=timezone.now(
            ), mail_sent_from=from_email_id, mail_sent_to=json.dumps({"items": mail_sent_to_list}))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_send_whatsapp_endpoint_failed_mail! %s %s",
                     str(e), str(exc_tb.tb_lineno),
                     extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None',
                            'bot_id': 'None'})


"""
function: apply_filter_api_analytics

input_params:
    selected_bot_obj:
    selected_api_name:
    selected_api_status: Passed/Failed
    datetime_start:
    datetime_end:
output_params:
    Returns the api objects based on filter parameters.
"""


def return_api_objs(selected_bot_obj, selected_api_name, selected_api_status, datetime_start, datetime_end, user_id,
                    APIElapsedTime, logger_extra):
    logger.info('Executing return_api_objs', extra=logger_extra)
    api_objs = []
    try:
        if str(selected_api_name) == "None" or selected_api_name == "All":
            if str(selected_api_status) == "None" or selected_api_status == "All":
                api_objs = APIElapsedTime.objects.filter(bot=selected_bot_obj, created_at__range=[
                    datetime_start, datetime_end]).order_by("-pk")
            else:
                api_objs = APIElapsedTime.objects.filter(bot=selected_bot_obj, api_status=selected_api_status,
                                                         created_at__range=[
                                                             datetime_start, datetime_end]).order_by("-pk")

        else:
            if str(selected_api_status) == "None" or selected_api_status == "All":
                api_objs = APIElapsedTime.objects.filter(bot=selected_bot_obj, api_name=selected_api_name,
                                                         created_at__range=[
                                                             datetime_start, datetime_end]).order_by("-pk")
            else:
                api_objs = APIElapsedTime.objects.filter(bot=selected_bot_obj, api_name=selected_api_name, api_status=selected_api_status, created_at__range=[datetime_start, datetime_end]).order_by("-pk")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error in return api objects for api filter %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra=logger_extra)
    if user_id != "":
        api_objs = api_objs.filter(user__user_id=user_id)
    logger.info('Finished return_api_objs', extra=logger_extra)
    return api_objs


def apply_filter_api_analytics(selected_bot_obj, selected_api_name, selected_api_status, datetime_start, datetime_end,
                               user_id, APIElapsedTime):
    datetime_end = datetime_end + datetime.timedelta(days=1)
    logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                    'source': 'None', 'channel': 'None', 'bot_id': 'None'}
    api_objs = return_api_objs(selected_bot_obj, selected_api_name, selected_api_status,
                               datetime_start, datetime_end, user_id, APIElapsedTime, logger_extra)
    return api_objs


"""
function: apply_custom_filter_api_analytics

input_params:
    selected_bot_obj:
    selected_api_name:
    selected_api_status: Passed/Failed
    datetime_start:
    datetime_end:
output_params:
    Returns the api objects based on filter parameters.
"""


def apply_custom_filter_api_analytics(selected_bot_obj, selected_api_name, selected_api_status, datetime_start,
                                      datetime_end, user_id, APIElapsedTime):
    logger_extra = {'AppName': 'EasyChat', 'user_id': 'None',
                    'source': 'None', 'channel': 'None', 'bot_id': 'None'}
    api_objs = return_api_objs(selected_bot_obj, selected_api_name, selected_api_status,
                               datetime_start, datetime_end, user_id, APIElapsedTime, logger_extra)
    return api_objs


"""
function: get_date_filter_type

input_params:

output_params:
    Used to obtian all options for selecting date as dictionary.
"""


def get_date_filter_type():
    return [{"key": "last_week", "value": "Last Week"}, {"key": "last_month", "value": "Last Month"},
            {"key": "since_go_live", "value": "Since Go Live Date"}, {"key": "custom_date", "value": "Custom Date"}]


"""
function: get_import_option_list

input_params:

output_params:
    Used to obtian all options for importing a bot as dictionary.
"""


def get_import_option_list():
    return [{"key": "0", "value": "Import from JSON"}, {"key": "1", "value": "Import from ZIP"},
            {"key": "2", "value": "Import Multilingual Intents from Excel"}]


"""
function: get_export_option_list

input_params:

output_params:
    Used to obtian all options for exporting a bot as dictionary.
"""


def get_export_option_list():
    return [{"key": "0", "value": "Export as JSON"}, {"key": "1", "value": "Export as ZIP"},
            {"key": "2", "value": "Export FAQs as Excel"}, {"key": "3", "value": "Export as Alexa JSON"},
            {"key": "4", "value": "Export Multilingual Intents As Excel"}]


"""
function: add_changes

input_params:
    change_data: it's a list
    old_data:
    old_data:
    heading:
output_params:
    It adds new entry in change_data(list) if old_data and new_data does not match.
"""


def add_changes(change_data, old_data, new_data, heading):
    if old_data != new_data:
        change_data.append({
            "heading": heading,
            "old_data": old_data,
            "new_data": new_data
        })

    return change_data


"""
function: get_message_list_and_icon_name

input_params:
    sticky_menu_list: list of lists containing intent_pk and icon_name
output_params:
    Returns the list of name of intents and icon_name taking intent pk list a input.
"""


def get_message_list_and_icon_name(sticky_menu_list, Intent):
    message_list = []
    try:
        for sticky in sticky_menu_list:
            pk = sticky[0]
            message = []

            try:
                intent_obj = Intent.objects.get(pk=pk, is_deleted=False)
            except Exception:
                intent_obj = None

            if intent_obj:
                message.append(intent_obj.name)
                message.append(sticky[1])
                message.append(intent_obj.pk)
                message_list.append(message)

    except Exception:
        message_list = []
        logger.warning("No message_list from API Response:", extra={'AppName': 'EasyChat', 'user_id': 'None',
                                                                    'source': 'None', 'channel': 'None',
                                                                    'bot_id': 'None'})
        pass

    return message_list


"""
function: check_access_for_user

input_params:
    user_obj: requesting user object
    bot_pk: for bot specfic query pass pk of bot otherwise None
    access_type: you can pass Full Access, Intent Related, Bot Setting Related, Lead Gen Related, Form Assist Related, Self Learning Related, Analytics Related, EasyDrive Related, EasyDataCollection Related
    type_of_query: type of access check(bot specific oroverall). default is "bot_specific"
output_params:
    Returns True/False depending on whether user have asked access
"""


def check_access_for_user(user_obj, bot_pk, access_type, type_of_query="bot_specific"):
    if type_of_query == "bot_specific":
        bot_pk = int(bot_pk)
        access_params = user_obj.get_bot_related_access_perm(bot_pk)
        if bot_pk in access_params:
            if access_type in access_params[bot_pk] or "Full Access" in access_params[bot_pk]:
                return True
        return False
    else:
        access_array = user_obj.get_overall_access_perm(bot_pk)
        if access_type in access_array or "Full Access" in access_array:
            return True
        return False


"""
function: get_random_captcha_image
It return random captcha image
"""


def get_random_captcha_image():
    files = os.listdir(settings.BASE_DIR +
                       '/EasyChatApp/static/EasyChatApp/captcha_images')
    index = random.randrange(0, len(files))
    return files[index]


"""
function: is_allowed
input params:
    user in the request : user who is trying to access
    allowed_list : type of users which are allowed to access a function
output:
    True : is user type is in allowed list
    False : if not

check whether user with given credentials exist or not
if yes check if he is in allowed list or not
if yes return true
otherwise return false in every case
"""


def is_allowed(request, allowed_list):
    try:
        if request.user.is_authenticated:
            user_obj = User.objects.get(username=request.user.username)
            if user_obj.role in allowed_list:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_allowed: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
        return False


"""
function: is_livechat_access_allowed
input params:
    user in the request : user who is trying to accsess livechat
output:
    True : if user is allowed to access livechat
    False : if not

check whether user with given credentials exist or not
if yes check if user is allowed to access livechat
if yes return true
otherwise return false in every case
"""


def is_livechat_access_allowed(request, BotInfo):
    try:
        if request.user.is_authenticated:
            user_obj = User.objects.get(username=request.user.username)
            livechat_user_obj = LiveChatUser.objects.filter(
                user=user_obj, is_deleted=False)

            if len(livechat_user_obj) > 0 and BotInfo.objects.filter(bot__in=livechat_user_obj[0].bots.filter(is_deleted=False), livechat_provider="cogno_livechat").count():
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_livechat_access_allowed: %s at %s",
                     str(e), str(exc_tb.tb_lineno),
                     extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
    return False


"""
function: is_fusion_access_allowed
input params:
    user in the request : user who is trying to accsess fusion
output:
    True : if user is allowed to access fusion
    False : if not
"""


def is_fusion_access_allowed(request, BotInfo):
    try:
        if request.user.is_authenticated:
            user_obj = User.objects.get(username=request.user.username)
            livechat_user_obj = LiveChatUser.objects.filter(
                user=user_obj, is_deleted=False)

            if len(livechat_user_obj) > 0 and BotInfo.objects.filter(bot__in=livechat_user_obj[0].bots.filter(is_deleted=False), livechat_provider="ameyo_fusion").count():
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_fusion_access_allowed: %s at %s",
                     str(e), str(exc_tb.tb_lineno),
                     extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
    return False


"""
function: is_tms_access_allowed
input params:
    user in the request : user who is trying to accsess TMS
output:
    True : if user is allowed to access TMS
    False : if not

check whether user with given credentials exist or not
if yes check if user is allowed to access TMS
if yes return true
otherwise return false in every case
"""


def is_tms_access_allowed(request, Agent):
    try:
        if request.user.is_authenticated:
            user_obj = User.objects.get(username=request.user.username)
            tms_user_obj = Agent.objects.filter(user=user_obj)
            if tms_user_obj.count() > 0 and tms_user_obj[0].bots.filter(is_deleted=False).count():
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_tms_access_allowed: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
        return False


"""
function: set_user
input params:
    user_id: user_id of the user; value maybe empty string or unique uuid
    message: message of the user
output:
    user: None/user object

it creates new profile object incase of new user and update user pipe
by adding new message.
"""


def is_easyassist_access_allowed(request):
    try:
        if request.user.is_authenticated:
            user_obj = User.objects.get(username=request.user.username)
            if CobrowseAgent.objects.filter(user=user_obj).count() > 0:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_easyassist_access_allowed: %s at %s",
                     str(e), str(exc_tb.tb_lineno),
                     extra={'AppName': 'EasyChat', 'user_id': '', 'source': '', 'channel': '', 'bot_id': ''})
        return False


"""
function: build_error_response
input params:
    e: error string
output:
    return rich json response containg error string
"""


def build_error_response(error_msg):
    response = json.dumps(copy.deepcopy(DEFAULT_RESPONSE))
    response = json.loads(response)
    response["status_code"] = "500"
    response["status_message"] = str(error_msg)
    response["response"]["text_response"]["text"] = str(error_msg)
    return response


"""
function: get_child_tree_objs
input params:
    root_tree_obj: object of root tree
    tree_pk_list: list of child tree objects

output params:
    json_resp: json containing tree_name, tree_pk, subtree information

"""


def get_child_tree_objs(root_tree_obj, tree_pk_list, language_obj):
    try:
        tree_name, lang_tuned_tree_obj = get_multilingual_tree_name(
            root_tree_obj, language_obj)

        child_choices_list = []

        if root_tree_obj.response:
            child_choices = root_tree_obj.response.choices.all()

            for choice in child_choices:
                child_choices_list.append("_".join(choice.value.split(" ")))

        if root_tree_obj.pk in tree_pk_list:
            if root_tree_obj.response is None:
                return {
                    "tree_name": tree_name,
                    "tree_pk": root_tree_obj.pk,
                    "tree_resp": "",
                    "subtree": {
                    },
                    "is_repeat": True,
                    "child_choices_list": child_choices_list
                }
            else:
                sentence = get_multilingual_tree_sentence(
                    root_tree_obj, language_obj, lang_tuned_tree_obj)
                return {
                    "tree_name": tree_name,
                    "tree_pk": root_tree_obj.pk,
                    "tree_resp": sentence,
                    "subtree": {
                    },
                    "is_repeat": True,
                    "child_choices_list": child_choices_list
                }

        json_resp = {}

        json_resp["tree_name"] = tree_name
        json_resp["tree_pk"] = root_tree_obj.pk
        json_resp["child_choices_list"] = child_choices_list
        if root_tree_obj.pk in tree_pk_list:
            json_resp["is_repeat"] = True
        else:
            json_resp["is_repeat"] = False

        tree_pk_list.append(root_tree_obj.pk)
        if (root_tree_obj.post_processor != None):
            json_resp["post_processor"] = root_tree_obj.post_processor.name
        if root_tree_obj.response is None:
            sentence = ""
        else:
            sentence = get_multilingual_tree_sentence(
                root_tree_obj, language_obj, lang_tuned_tree_obj)
        json_resp["tree_resp"] = sentence
        child_tree_objs = root_tree_obj.children.filter(is_deleted=False)

        count = 1
        temp_json = {}
        for child_tree_obj in child_tree_objs:
            temp_json["_".join(child_tree_obj.name.split(" "))] = get_child_tree_objs(
                child_tree_obj, tree_pk_list, language_obj)
            count += 1

        json_resp["subtree"] = temp_json

        return json_resp

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_child_tree_objs: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def delete_form_assist_tag(intent_pk):
    try:
        intent_obj = Intent.objects.filter(
            pk=int(intent_pk), is_deleted=False, is_hidden=False)[0]
        FormAssist.objects.get(intent=intent_obj).delete()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("delete_intent %s in line no %s",
                     str(e), str(exc_tb.tb_lineno),
                     extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None',
                            'bot_id': 'None'})
        pass


"""
function: delete_intent
input params:
    intent_pk: pk of intent object which has to be deleted
    user_obj: active user object
output params:
    returns True or False depending on whether intended intent deleted
        or not
"""


def delete_intent(intent_pk, user_obj):
    try:
        bot_objs = Bot.objects.filter(users__in=[user_obj], is_deleted=False)
        delete_form_assist_tag(intent_pk)
        intent_obj = Intent.objects.filter(
            pk=int(intent_pk), bots__in=bot_objs, is_deleted=False, is_hidden=False)[0]
        intent_obj.disable()
        intent_obj.remove_initial_intent_on_delete()

        # Deleting language tuning objects

        if LanguageTuningBotResponseTable.objects.filter(bot_response=intent_obj.tree.response):
            LanguageTuningBotResponseTable.objects.filter(
                bot_response=intent_obj.tree.response).delete()

        if LanguageTuningTreeTable.objects.filter(tree=intent_obj.tree):
            LanguageTuningTreeTable.objects.filter(
                tree=intent_obj.tree).delete()

        if LanguageTuningIntentTable.objects.filter(intent=intent_obj):
            LanguageTuningIntentTable.objects.filter(
                intent=intent_obj).delete()

        update_welcome_banner_on_intent_delete(intent_obj)

        return True
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("delete_intent %s in line no %s",
                     str(e), str(exc_tb.tb_lineno),
                     extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None',
                            'bot_id': 'None'})
        return False


"""
function: get_tag_mapper_list_for_given_user
input params:
    request: user request data

output_params:
    tag_mapper_objs
"""


def get_tag_mapper_list_for_given_user(request):
    username = request.user.username
    user_obj = User.objects.get(username=username)
    tag_mapper_objs = TagMapper.objects.filter(
        api_tree__users__in=[user_obj]).distinct()
    return tag_mapper_objs


"""
function: get_authentication_objs
output_params:
    auth_obj_list: list of objects of available authtication methods
"""


def get_authentication_objs(bot_objs):
    name_list = []
    auth_objs = Authentication.objects.filter(bot__in=bot_objs).order_by('pk').values()
    auth_obj_list = []

    for auth_obj in auth_objs:
        if auth_obj["name"] not in name_list:
            name_list.append(auth_obj["name"])
            auth_obj_list.append(auth_obj)

    return auth_obj_list


"""
function: get_uat_bots
input_params:
    user_obj: active user object
output_params:
    returns list uat bots objects available for that user object
"""


def get_uat_bots(user_obj):
    logger.info("Get UAT Bots with user object arguement...", extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    if user_obj == 'all':
        return Bot.objects.filter(is_uat=True, is_deleted=False)
    return Bot.objects.filter(users__in=[user_obj], is_uat=True, is_deleted=False)


"""
function: get_form_assist_uat_bots
input_params:
    user_obj: active user object
output_params:
    returns list form assist uat bots objects available for that user object
"""


def get_form_assist_uat_bots(user_obj):
    logger.info("Get UAT Bots with user object arguement...", extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    if user_obj == 'all':
        return Bot.objects.filter(is_uat=True, is_deleted=False, is_form_assist_enabled=True)
    return Bot.objects.filter(users__in=[user_obj], is_uat=True, is_deleted=False, is_form_assist_enabled=True)


"""
function: get_lead_generation_uat_bots
input_params:
    user_obj: active user object
output_params:
    returns list lead generation uat bots objects available for that user object
"""


def get_lead_generation_uat_bots(user_obj):
    if user_obj == 'all':
        return Bot.objects.filter(is_uat=True, is_deleted=False, is_lead_generation_enabled=True)
    logger.info("Get UAT Bots with user object arguement...", extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return Bot.objects.filter(users__in=[user_obj], is_uat=True, is_deleted=False, is_lead_generation_enabled=True)


"""
function: get_production_bots
input_params:
    user_obj: active user object
output_params:
    returns list of all production bot objects associated with user
"""


def get_production_bots(user_obj):
    bot_slug = []

    bots = []
    if user_obj == 'all':
        bots = Bot.objects.filter(is_active=True, is_deleted=False)
    else:
        bots = Bot.objects.filter(
            users__in=[user_obj], is_active=True, is_deleted=False)

    for bot in bots:
        if bot.slug not in bot_slug and bot.slug != None:
            bot_slug.append(bot.slug)

    bot_objs = []

    for slug in bot_slug:
        bot_obj = Bot.objects.filter(
            slug=slug, is_active=True, is_deleted=False).order_by('-pk')[0]
        bot_objs.append(bot_obj)

    return bot_objs


"""
function: get_uat_bots_pk_list
input_params:
    user_obj: active user object
output_params:
    returns list of all production bot object pks associated with user
"""


def get_uat_bots_pk_list(user_obj):
    return list(Bot.objects.filter(users__in=[user_obj], is_uat=True, is_deleted=False).values_list("pk", flat=True))


"""
function: save_audit_trail
input params:
    user_obj: active user object
    action: action done by user [choices are defined in constants.py]
    data: data string
Save audit to database
"""


def save_audit_trail(user_obj, action, data):
    try:
        AuditTrail.objects.create(user=user_obj, action=action, data=data)
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("save_audit_trail %s at %s",
                     str(e), str(exc_tb.tb_lineno),
                     extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None',
                            'bot_id': 'None'})


"""
function: insert_file_into_intent_from_drive
input params:
    bot_response_obj: bot response object to which media to be attached
    easychat_drive_obj_list: media object list

Save bot response object to database after attaching media
"""


def insert_file_into_intent_from_drive(bot_response_obj, easychat_drive_obj_list):
    images = []

    try:

        images = json.loads(bot_response_obj.images)["items"]
        logger.info(images, extra={'AppName': 'EasyChat', 'user_id': 'None',
                                   'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        logger.info(bot_response_obj.images, extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("insert_file_into_intent_from_drive: no image: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    videos = []

    try:

        videos = json.loads(bot_response_obj.videos)["items"]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("insert_file_into_intent_from_drive: no videos: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    cards = []

    try:
        cards = json.loads(bot_response_obj.cards)["items"]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.warning("insert_file_into_intent_from_drive: no cards: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    for easychat_drive_obj in easychat_drive_obj_list:

        # media_url = settings.EASYCHAT_HOST_URL + easychat_drive_obj.media_url
        media_url = easychat_drive_obj.media_url
        if easychat_drive_obj.media_type == MEDIA_IMAGE:
            images.append(media_url)
        elif easychat_drive_obj.media_type == MEDIA_VIDEO:
            videos.append(media_url)
        else:
            cards.append({
                "title": str(easychat_drive_obj.media_name).upper() + " attachment",
                "content": "",
                "link": media_url,
                "img_url": ""
            })

    bot_response_obj.images = json.dumps({
        "items": images
    })

    bot_response_obj.videos = json.dumps({
        "items": videos
    })

    bot_response_obj.cards = json.dumps({
        "items": cards
    })

    bot_response_obj.save()


"""
function: get_all_file_type
Return list of all file type allowed for bot till now
"""


def get_all_file_type():
    logger.info("Into get_all_file_type...", extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    get_all_file = ['image(ex. .jpeg, .png, .jpg)',
                    'word processor(i.e. .doc,.pdf)', 'compressed file(ex. .zip)', 'video file(ex. .mp4)']
    get_all_file_type = []

    for item in get_all_file:
        get_all_file_type.append({
            "is_selected": False,
            "file_type": item
        })
    logger.info("Exit from get_all_file_type...", extra={
        'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return get_all_file_type


"""
function: create_default_intents
input params:
    code: It will create the defaults intents of the newly created bot
    parameter: bot_id(mandatory)
"""


def create_default_intents(bot_id):
    try:
        bot_obj = Bot.objects.get(pk=int(bot_id))
        category = Category.objects.get(name="Others", bot=bot_obj)
        for intent in default_intent_contants:
            name = intent["intent_name"]
            response = intent["response"]
            variations = intent["variation"]
            variations = variations.split(",")
            counter = 0
            data = {}
            for variation in variations:
                data[counter] = variation.strip()
                counter = counter + 1
            response = intent["response"]
            hashed_name = get_hashed_intent_name(name, bot_obj)
            intent_obj = Intent.objects.create(
                name=name, intent_hash=hashed_name, training_data=json.dumps(data), category=category)
            intent_obj.bots.add(bot_obj)
            for channel_obj in Channel.objects.filter(is_easychat_channel=True):
                intent_obj.channels.add(channel_obj)

            modes = ""
            try:
                modes = intent["modes"]
            except Exception:
                pass

            if modes == "":
                bot_response_obj = create_bot_response(response)
                tree_obj = intent_obj.tree
                tree_obj.response = bot_response_obj
                tree_obj.save()
                bot_response_obj.save()
            else:
                bot_response_obj = create_bot_response(response)
                tree_obj = intent_obj.tree
                tree_obj.response = bot_response_obj
                intent_modes = json.loads(bot_response_obj.modes)
                intent_modes.update(modes)
                bot_response_obj.modes = json.dumps(intent_modes)
                bot_response_obj.save()
                tree_obj.save()
                intent_obj.is_hidden = True

            is_small_talk = ""
            try:
                is_small_talk = intent["is_small_talk"]
            except Exception:
                pass

            is_easy_assist_allowed = False
            try:
                is_easy_assist_allowed = intent["is_easy_assist_allowed"]
            except Exception:
                pass

            is_easy_tms_allowed = False
            try:
                is_easy_tms_allowed = intent["is_easy_tms_allowed"]
            except Exception:
                pass

            if is_small_talk == True:
                intent_obj.is_small_talk = True
                # for small talk intents intent level feedback is disabled
                intent_obj.is_feedback_required = False
                intent_obj.is_part_of_suggestion_list = False
                intent_obj.is_livechat_enabled = False
                intent_obj.is_form_assist_enabled = False

            intent_obj.is_easy_tms_allowed = is_easy_tms_allowed
            intent_obj.is_easy_assist_allowed = is_easy_assist_allowed
            intent_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_default_intents: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})


def create_intent_obj(name, response, bot_obj, data, channel_objs, category, modes, other_params, is_hidden):
    try:
        hashed_name = get_hashed_intent_name(name, bot_obj)
        intent_obj = Intent.objects.create(
            name=name, intent_hash=hashed_name, training_data=json.dumps(data), category=category)
        intent_obj.bots.add(bot_obj)
        for channel_obj in channel_objs:
            intent_obj.channels.add(channel_obj)

        if modes == "":
            bot_response_obj = create_bot_response(response)
            tree_obj = intent_obj.tree
            tree_obj.response = bot_response_obj
            tree_obj.save()
            bot_response_obj.save()
        else:
            bot_response_obj = create_bot_response(response)
            tree_obj = intent_obj.tree
            tree_obj.response = bot_response_obj
            intent_modes = json.loads(bot_response_obj.modes)
            intent_modes.update(modes)
            bot_response_obj.modes = json.dumps(intent_modes)
            bot_response_obj.save()
            tree_obj.save()

        intent_obj.is_hidden = is_hidden

        is_small_talk = ""
        if "is_small_talk" in other_params:
            is_small_talk = other_params["is_small_talk"]

        is_easy_assist_allowed = False
        if "is_easy_assist_allowed" in other_params:
            is_easy_assist_allowed = other_params["is_easy_assist_allowed"]

        is_easy_tms_allowed = False
        if "is_easy_tms_allowed" in other_params:
            is_easy_tms_allowed = other_params["is_easy_tms_allowed"]

        is_whatsapp_csat = False
        if "is_whatsapp_csat" in other_params:
            is_whatsapp_csat = other_params["is_whatsapp_csat"]

        if is_small_talk == True:
            intent_obj.is_small_talk = True
            intent_obj.is_part_of_suggestion_list = False
            intent_obj.is_livechat_enabled = False
            intent_obj.is_form_assist_enabled = False

        intent_obj.is_easy_tms_allowed = is_easy_tms_allowed
        intent_obj.is_easy_assist_allowed = is_easy_assist_allowed
        intent_obj.is_whatsapp_csat = is_whatsapp_csat
        intent_obj.save()
        return intent_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_intent_obj: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


def create_bot_response_with_image_file_attach(answer):
    sentence = {
        "items": [
            {
                "text_response": str(answer),
                "speech_response": str(answer),
                "text_reprompt_response": str(answer),
                "speech_reprompt_response": str(answer),
            }
        ]
    }

    cards = {
        "items": [
        ]
    }

    modes = {
        "is_typable": "true",
        "is_button": "true",
        "is_slidable": "false",
        "is_date": "false",
        "is_dropdown": "false",
        "is_attachment_required": "true",
        "is_save_attachment_required": "true"
    }

    modes_param = {
        "is_slidable": [{
            "max": "",
            "min": "",
            "step": "",
            "placeholder": ""
        }],
        "choosen_file_type": "image(ex. .jpeg, .png, .jpg)"
    }

    bot_response_obj = BotResponse.objects.create(
        sentence=json.dumps(sentence),
        cards=json.dumps(cards),
        modes=json.dumps(modes),
        modes_param=json.dumps(modes_param))

    return bot_response_obj


def create_bot_response_with_tms_drop_down(answer, drop_down_choices):
    sentence = {
        "items": [
            {
                "text_response": str(answer),
                "speech_response": str(answer),
                "text_reprompt_response": str(answer),
                "speech_reprompt_response": str(answer),
            }
        ]
    }

    cards = {
        "items": [
        ]
    }

    modes = {
        "is_typable": "true",
        "is_button": "true",
        "is_slidable": "false",
        "is_date": "false",
        "is_dropdown": "true",
        "is_attachment_required": "false",
        "is_save_attachment_required": "false",
        "is_datepicker": "false",
        "is_single_datepicker": "false",
        "is_multi_datepicker": "false",
        "is_timepicker": "false",
        "is_single_timepicker": "false",
        "is_multi_timepicker": "false",
        "is_calender": "false",
        "is_check_box": "false",
        "is_drop_down": "true",
        "is_range_slider": "false",
        "is_radio_button": "false",
        "is_video_recorder_allowed": "false",
        "is_create_form_allowed": "false",
        "is_recommendation_menu": "false",
        "is_tms_cat_dropdown": "true"
    }

    modes_param = {
        "is_slidable": [{
            "max": "",
            "min": "",
            "step": "",
            "placeholder": ""
        }],
        "drop_down_choices": drop_down_choices,
        "choosen_file_type": "none",
    }

    bot_response_obj = BotResponse.objects.create(
        sentence=json.dumps(sentence),
        cards=json.dumps(cards),
        modes=json.dumps(modes),
        modes_param=json.dumps(modes_param))

    return bot_response_obj


def create_and_add_post_proccessor(tree_obj, post_proccesor_name, post_proccesor_function, Processor):
    try:
        post_procceor_obj = Processor.objects.create(
            name=post_proccesor_name, function=post_proccesor_function)
        tree_obj.post_processor = post_procceor_obj
        tree_obj.save()

        return tree_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_and_add_post_proccessor: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return tree_obj


def create_and_add_api_tree(tree_obj, api_tree_name, api_caller, ApiTree):
    try:
        api_tree_obj = ApiTree.objects.create(
            name=api_tree_name, api_caller=api_caller)
        tree_obj.api_tree = api_tree_obj
        tree_obj.save()

        return tree_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_and_add_api_tree: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return tree_obj


def create_and_add_child_with_post_proccesor(parent_tree_obj, child_name, child_response, post_proccesor_name,
                                             post_proccesor_function, Processor, Tree):
    try:
        child_tree = Tree.objects.create(name=child_name)
        bot_response_obj = create_bot_response(child_response)
        child_tree.response = bot_response_obj
        child_tree = create_and_add_post_proccessor(
            child_tree, post_proccesor_name, post_proccesor_function, Processor)
        parent_tree_obj.children.add(child_tree)
        parent_tree_obj.save()
        return child_tree
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_and_add_child_with_post_proccesor: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


def create_and_add_child_with_api_tree(parent_tree_obj, child_name, child_response, api_tree_name, api_caller, ApiTree,
                                       Tree):
    try:
        child_tree = Tree.objects.create(name=child_name)
        bot_response_obj = create_bot_response(child_response)
        child_tree.response = bot_response_obj
        child_tree = create_and_add_api_tree(
            child_tree, api_tree_name, api_caller, ApiTree)
        parent_tree_obj.children.add(child_tree)
        parent_tree_obj.save()
        return child_tree
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_and_add_child_with_api_tree: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


def create_default_tms_flow(bot_id, is_tms_allowed=False):
    try:
        bot_obj = Bot.objects.get(pk=int(bot_id))
        category = Category.objects.get(name="Others", bot=bot_obj)
        modes = ""
        other_params = {
            "is_easy_tms_allowed": True
        }
        is_hidden = True
        if is_tms_allowed == True:
            is_hidden = False
        name = "Raise an issue"
        response = " Please provide your name?"
        variations = ["Raise an issue", "create an issue"]
        counter = 0
        data = {}
        for variation in variations:
            data[counter] = variation
            counter = counter + 1
        channel_objs = Channel.objects.filter(is_easychat_channel=True)

        intent_obj = create_intent_obj(
            name, response, bot_obj, data, channel_objs, category, modes, other_params, is_hidden)
        top_tree_obj = intent_obj.tree

        child_tree = create_and_add_post_proccessor(
            top_tree_obj, "GetUserName", NAME_POST_PROCESSOR_TMS_PYTHON_CODE, Processor)

        child_response = "Kindly provide your valid email id."
        child_tree = create_and_add_child_with_post_proccesor(
            child_tree, "get user email id", child_response, "GetUserEmailId", EMAIL_ID_POST_PROCESSOR_TMS_PYTHON_CODE,
            Processor, Tree)

        child_response = "Kindly provide your valid 10 digit phone number."
        child_tree = create_and_add_child_with_post_proccesor(
            child_tree, "get user Phone no", child_response, "GetUserPhoneNo", PHONE_NO_POST_PROCESSOR_TMS_PYTHON_CODE,
            Processor, Tree)

        child_response = "Select a category that best matches your issue"
        child_tree = create_and_add_child_with_post_proccesor(
            child_tree, "Category", child_response, "GetUserCategory", CATEGORY_NAME_POST_PROCESSOR_TMS_PYTHON_CODE,
            Processor, Tree)
        # as it is a new bot so by default only others category will be thier
        # so adding that in drop down choices
        bot_response_obj = create_bot_response_with_tms_drop_down(
            child_response, ["OTHERS"])
        child_tree.response = bot_response_obj
        create_and_add_api_tree(child_tree, "TMS_CATEGORY_AS_RECOMENDATION_" + str(
            bot_id), API_TREE_FOR_CATEGORY_AS_RECOMMENDATION, ApiTree)
        child_tree.save()
        child_response = "Kindly submit your query. We will surely look into it."
        child_tree = create_and_add_child_with_post_proccesor(
            child_tree, "get user issue", child_response, "GetUSERISSUE", ISSUE_POST_PROCESSOR_TMS_PYTHON_CODE,
            Processor, Tree)
        child_tree.post_processor.is_original_message_required = True
        child_tree.post_processor.save()
        child_response = "Kindly attach a screenshot of your issue (if any).<p>{/upload_image_note/}</p>"
        child_tree = create_and_add_child_with_api_tree(
            child_tree, "Attachment", child_response, "AddAttachment", API_TREE_TMS_ATTACHMENT, ApiTree, Tree)
        bot_response_obj = create_bot_response_with_image_file_attach(
            child_response)
        child_tree.response = bot_response_obj
        child_tree.save()
        child_response = "Thank you <strong>{/full_name/}</strong> for reporting your issue. Your Ticket ID is <strong>{/ticket_id/}</strong>. Kindly save it for further reference. Our customer service agent will contact you shortly."
        child_tree = create_and_add_child_with_api_tree(
            child_tree, "Genrate Ticket", child_response, "GenrateTMSTicket", API_TREE_TMS_CREATE_TICKET, ApiTree, Tree)
        child_tree.is_last_tree = True
        child_tree.save()
        # creating another intent for check ticket status
        name = "Check ticket status"
        response = "Please provide your Ticket Id?"
        variations = ["Check ticket status",
                      "ticket status"]
        counter = 0
        data = {}
        for variation in variations:
            data[counter] = variation
            counter = counter + 1
        channel_objs = Channel.objects.filter(is_easychat_channel=True)

        intent_obj = create_intent_obj(
            name, response, bot_obj, data, channel_objs, category, modes, other_params, is_hidden)
        top_tree_obj = intent_obj.tree
        top_tree_obj = create_and_add_post_proccessor(
            top_tree_obj, "GetUserTicket", TICKETID_POST_PROCESSOR_TMS_PYTHON_CODE, Processor)
        top_post_processor_obj = top_tree_obj.post_processor
        top_post_processor_obj.is_original_message_required = True
        top_post_processor_obj.save(update_fields=["is_original_message_required"])
        
        child_response = "{/ticket_status/}"
        child_tree = create_and_add_child_with_api_tree(top_tree_obj, "TMS Ticket Status", child_response,
                                                        "GetTicketStatus", API_TREE_CHECK_TICKET_STATUS, ApiTree, Tree)

        # If you have any issues regarding this ticket you can reply on it.

        child_tree = create_and_add_post_proccessor(
            child_tree, "Save Customer Message", GET_CUSTOMER_NAME__POST__TMS__CHECK_STATUS_INTENT, Processor)

        # Create and add api tree 4th child
        child_response = "Kindly attach a screenshot (if any)."
        child_tree = create_and_add_child_with_api_tree(
            child_tree, "Attachment", child_response, "AddAttachment", API_TREE_TMS_ATTACHMENT__CHECK_STATUS_INTENT,
            ApiTree, Tree)
        bot_response_obj = create_bot_response_with_image_file_attach(
            child_response)
        child_tree.response = bot_response_obj
        child_tree.save()
        child_response = "Thank You for sharing information with us. We will get back to you shortly."

        # Create and add api tree 5th child
        child_tree = create_and_add_child_with_api_tree(
            child_tree, "Say Thank You", child_response, "CreateCustomerMessageAudit",
            API_TREE_THANK_YOU__CHECK_STATUS_INTENT, ApiTree, Tree)

        child_tree.is_last_tree = True
        child_tree.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_default_tms_flow: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})


"""
function: is_it_livechat_manager
input params:
    username: Username of easychat User object.
Output:
    rteurns True if user is Livechat manager, False otherwise.
"""


def is_it_livechat_manager(username, bot_pk):
    try:
        user_obj = User.objects.get(username=username)
        livechat_user = LiveChatUser.objects.filter(user=user_obj)
        bot_obj = Bot.objects.get(pk=bot_pk)
        if livechat_user.count() > 0 and bot_obj.created_by.username == username:
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_it_livechat_manager: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return False


"""
function: is_it_easysearch_manager
input params:
    username: Username of easychat User object.
Output:
    rteurns True if user is EasySearch manager, False otherwise.
"""


def is_it_easysearch_manager(username):
    try:
        user_obj = User.objects.get(username=username)
        easysearch_user = SearchUser.objects.filter(user=user_obj)
        if easysearch_user.count() > 0:
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_it_easysearch_manager: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return False


"""
function: is_it_easyassist_admin
input params:
    username: Username of easychat User object.
Output:
    rteurns True if user is EasyAssist admin, False otherwise.
"""


def is_it_easyassist_admin(username):
    try:
        user_obj = User.objects.get(username=username)
        cobrowse_agents = CobrowseAgent.objects.filter(user=user_obj)
        if cobrowse_agents.count() > 0 and cobrowse_agents[0].role == "admin":
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_it_easyassist_admin: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return False


"""
function: is_it_easyassist_admin
input params:
    username: Username of easychat User object.
Output:
    rteurns True if user is EasyAssist admin, False otherwise.
"""


def is_it_easytms_admin(username, Agent):
    try:
        user_obj = User.objects.get(username=username)
        agents = Agent.objects.filter(user=user_obj)
        if agents.count() > 0 and agents[0].role == "admin":
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_it_easytms_admin: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return False


"""
function: create_default_livechat_trigger_intent
input params:
    bot_obj: Bot object in which the livechat default intent should be added.
Output:
    rteurns intent object.
If there is already defalt livechat intent then it only mark it is_deleted false otherwise creates new one.
"""


def create_default_livechat_trigger_intent(bot_obj):
    try:
        if bot_obj.livechat_default_intent != None:
            intent_obj = bot_obj.livechat_default_intent
            intent_obj.is_deleted = False
            intent_obj.is_feedback_required = False
            intent_obj.save()
            return intent_obj

        name = "Chat with an expert"

        intent_objs = Intent.objects.filter(
            bots__in=[bot_obj], is_deleted=False).distinct()
        intent_objs = intent_objs.filter(name__iexact=name)
        if intent_objs.count():
            return intent_objs[0]

        response = "Your request has been registered with us. Our expert will chat with you soon."
        variations = "chat with an agent, Chat with an expert"
        variations = variations.split(",")
        counter = 0
        data = {}
        for variation in variations:
            data[counter] = variation
            counter = counter + 1
        hashed_name = get_hashed_intent_name(name, bot_obj)
        intent_obj = Intent.objects.create(
            name=name, intent_hash=hashed_name, training_data=json.dumps(data), is_feedback_required=False)
        intent_obj.bots.add(bot_obj)
        for channel_obj in Channel.objects.filter(is_easychat_channel=True):
            intent_obj.channels.add(channel_obj)
        modes = {"is_typable": "true", "is_button": "true", "is_slidable": "false", "is_date": "false",
                 "is_dropdown": "false", "is_livechat": "true", "is_attachment_required": "false"}

        bot_response_obj = create_bot_response(response)
        tree_obj = intent_obj.tree
        tree_obj.response = bot_response_obj
        intent_modes = json.loads(bot_response_obj.modes)
        intent_modes.update(modes)
        bot_response_obj.modes = json.dumps(intent_modes)
        bot_response_obj.save()
        tree_obj.save()
        intent_obj.save()

        return intent_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_default_livechat_trigger_intent: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})
        return None


"""
function: remove_default_livechat_trigger_intent
input params:
    bot_obj: Bot object from which the livechat default intent should be removed.
Output:
    rteurns none
Mark is_deleted to True of defalt livechat intent
"""


def remove_default_livechat_trigger_intent(bot_obj):
    try:
        if bot_obj.livechat_default_intent != None:
            intent_obj = bot_obj.livechat_default_intent
            intent_obj.is_deleted = True
            intent_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("remove_default_livechat_trigger_intent: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})


"""
function: make_copy_of_tree_obj
input params:
    tree_pk: primary key of tree object
Output:
    returns parent tree object of whole new flow
"""


def make_copy_of_tree_obj(tree_obj, child_list):
    try:

        if tree_obj.is_deleted == True:
            return None

        prev_pk = tree_obj.pk
        response = tree_obj.response
        pre_processor = tree_obj.pre_processor
        post_processor = tree_obj.post_processor
        pipe_processor = tree_obj.pipe_processor
        api_tree = tree_obj.api_tree
        tree_obj.pk = None
        tree_obj.save()

        # dictionary checking original pk
        # and copied pk
        child_list[prev_pk] = tree_obj.pk
        # saving copied processors by
        # appending copied_processors pk
        if pre_processor is not None:
            pre_processor.pk = None
            pre_processor.save()
            pre_processor.name = pre_processor.name + \
                                 "_" + str(pre_processor.pk)
            pre_processor.save()

        if post_processor is not None:
            post_processor.pk = None
            post_processor.save()
            post_processor.name = post_processor.name + \
                                  "_" + str(post_processor.pk)
            post_processor.save()

        if pipe_processor is not None:
            pipe_processor.pk = None
            pipe_processor.save()
            pipe_processor.name = pipe_processor.name + \
                                  "_" + str(pipe_processor.pk)
            pipe_processor.save()

        if api_tree is not None:
            api_tree.pk = None
            api_tree.save()
            api_tree.name = api_tree.name + "_" + str(api_tree.pk)
            api_tree.save()

        if response is not None:
            response.pk = None
            response.save()

        tree_obj.pre_processor = pre_processor
        tree_obj.post_processor = post_processor
        tree_obj.pipe_processor = pipe_processor
        tree_obj.api_tree = api_tree
        tree_obj.response = response
        tree_obj.save()
        reftree_obj = Tree.objects.get(pk=prev_pk)
        child_trees = reftree_obj.children.all()

        if not child_trees.filter(is_deleted=False):
            tree_obj.is_last_tree = True
            tree_obj.save()

        for child_tree in child_trees:
            # checks if recursion is occuring
            if child_tree.pk not in child_list.keys():
                tree_copy = make_copy_of_tree_obj(child_tree, child_list)
            else:
                tree_copy = Tree.objects.get(pk=child_list[child_tree.pk])

            if tree_copy is not None:
                tree_obj.children.add(tree_copy)

        tree_obj.save()
        return tree_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("make_copy_of_tree_obj: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return None


"""
function: manage_default_livechat_intent
input params:
    is_livechat_enabled: True/False
    bot_obj: Bot object in which the livechat default intent should be added/removed.
Output:
    rteurns None just perform the required operation

If is_livechat_enabled True then it go for create_default_livechat_trigger_intent otherwise remove_default_livechat_trigger_intent
"""


def manage_default_livechat_intent(is_livechat_enabled, bot_obj):
    try:
        if is_livechat_enabled:
            bot_obj.livechat_default_intent = create_default_livechat_trigger_intent(
                bot_obj)
            bot_obj.save()
        else:
            remove_default_livechat_trigger_intent(bot_obj)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("manage_default_livechat_intent: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})


"""
function: manage_bot_to_admin_account
input params:
    user: EasyChat user, which should be admin for livechat.
    is_livechat_enabled: True/False
    bot_obj: Bot object in which the livechat default intent should be added/removed.
Output:
    If is_livechat_enabled True then the user will be admin for livechat and this function will add this bot_obj to user's livechat account, otherwise remove bot obj(if already added)
"""


def manage_bot_to_admin_account(user, is_livechat_enabled, bot_obj):
    try:
        if is_livechat_enabled:
            livechat_user = LiveChatUser.objects.get(user=user)
            livechat_user.bots.add(bot_obj)
            livechat_user.save()
        else:
            livechat_user = LiveChatUser.objects.get(user=user)
            livechat_user.bots.remove(bot_obj)
            livechat_user.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("manage_bot_to_admin_account: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})


"""
function: check_and_create_default_livechat_category
input params:
    bot_obj: Bot object in which the livechat default intent should be added/removed.
Output:
    If default livechat category "Others" does not exist then it creates new category object.
"""


def check_and_create_default_livechat_category(bot_obj, user_obj):
    try:
        livechat_user_obj = LiveChatUser.objects.get(user=user_obj)
        if not LiveChatCategory.objects.filter(bot=bot_obj, title="others").count():
            livechat_category = LiveChatCategory.objects.create(
                bot=bot_obj, title="others")
            livechat_user_obj.category.add(livechat_category)
            livechat_user_obj.save()
        else:
            livechat_category = LiveChatCategory.objects.filter(
                bot=bot_obj, title="others")[0]
            livechat_user_obj.category.add(livechat_category)
            livechat_user_obj.save()

        # Creating livechat admin config for the first time
        try:
            livechat_config_obj = LiveChatConfig.objects.get(
                bot=bot_obj)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("Livechat config bot does not exist,creating new config: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            livechat_config_obj = LiveChatConfig.objects.create(
                bot=bot_obj)
            pass

        try:
            livechat_admin_config = LiveChatAdminConfig.objects.get(
                admin=livechat_user_obj, livechat_config__in=[livechat_config_obj])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("LivechatAdmin config bot does not exist, creating new LiveChat admin config: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})
            livechat_admin_config = LiveChatAdminConfig.objects.get(
                admin=livechat_user_obj)
            livechat_admin_config.livechat_config.add(
                livechat_config_obj)
            livechat_admin_config.save()
            pass

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_create_default_livechat_category: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function: send_mail
input_params:
    from_email_id,: email id from which email wil be sent
    to_emai_id: email id to which email wil be sent
    message_as_string: html message
    from_email_id_password: password of from email

send email

"""

# def send_mail(from_email_id, to_emai_id, message_as_string, from_email_id_password):
#     # The actual sending of the e-mail
#     server = smtplib.SMTP('smtp.gmail.com:587')
#     # Credentials (if needed) for sending the mail
#     password = from_email_id_password
#     # Start tls handshaking
#     server.starttls()
#     # Login to server
#     server.login(from_email_id, password)
#     # Send mail
#     server.sendmail(from_email_id, to_emai_id, message_as_string)
#     # Close session
#     server.quit()


"""
function: send_reset_pass_mail
input_params:
    from_email_id,: email id from which email wil be sent
    to_emai_id: email id to which email wil be sent
    message_as_string: html message
    from_email_id_password: password of from email

send email
"""


def send_password_over_email(email, name, password, platform_url):
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
                Dear """ + name + """,
            </p>
            <p>
            Your password to login into EasyChat Console <a href=\"""" + platform_url + """\" target="_blank">""" + platform_url + """</a> for <b>User ID</b> '""" + email + """' is <b>""" + password + """</b>
            </p>

            <p>Kindly connect with us in case of any issue.</p>
            <p>&nbsp;</p>"""

        config = get_developer_console_settings()

        body += config.custom_report_template_signature

        body += """</div></body>"""

        send_email_to_customer_via_awsses(
            email, "EasyChat Console - Access Management", body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("send_password_over_email: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def set_easyassist_intent(bot_obj, is_easy_assist_allowed):
    try:
        intent_objs = Intent.objects.filter(
            bots__in=[bot_obj], is_easy_assist_allowed=True)
        if intent_objs.count() != 0:
            for intent_obj in intent_objs:
                intent_obj.is_hidden = not (is_easy_assist_allowed)
                intent_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("set_easyassist_intent: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})


def set_easytms_intent(bot_obj, is_easy_tms_allowed):
    try:
        intent_objs = Intent.objects.filter(
            bots__in=[bot_obj], is_easy_tms_allowed=True)
        if intent_objs.count() != 0:
            for intent_obj in intent_objs:
                intent_obj.is_hidden = not (is_easy_tms_allowed)
                intent_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("set_easytms_intent: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_obj.pk)})


"""
function: create_flow_with_excel
input_params:
    filepath,: excel file path
    intent_obj: intent object
output:
    create flow using excel
"""


def create_flow_with_excel(filepath, intent_obj):
    import xlrd
    response = {}
    response["status"] = 500
    flow_status_msg = "Something Went Wrong"
    success_status = False
    try:
        validation_obj = EasyChatInputValidation()

        ensure_element_tree(xlrd)

        automated_flow_create_wb = xlrd.open_workbook(filepath)
        excel_flows = automated_flow_create_wb.sheet_by_index(0)
        rows_limit = excel_flows.nrows
        # cols_limit = excel_flows.ncols

        row_index = 1
        flow_status_msg = "Please Check Excel file format: Refer excel format for reference"
        if intent_obj.tree:
            intent_obj.tree.children.clear()
            intent_obj.save()
        tree_id = intent_obj.tree.pk
        is_error_in_trees = False
        while row_index in range(1, rows_limit):
            try:
                logger.info(tree_id, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                child_name = excel_flows.cell_value(row_index, 0)
                child_name = validation_obj.remo_unwanted_security_characters(child_name)
                child_name = validation_obj.sanitize_html(child_name)

                logger.info(child_name, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                if len(child_name) > INTENT_TREE_NAME_CHARACTER_LIMIT:
                    if not is_error_in_trees:
                        flow_status_msg = ""
                    flow_status_msg += "Tree Name Cannot Contain More Than 500 Characters at row {} and column 1<br>".format(
                        row_index)
                    row_index += 1
                    is_error_in_trees = True
                    continue
                parent_obj = Tree.objects.get(
                    pk=int(tree_id), is_deleted=False)
                logger.info(parent_obj, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                new_tree_obj = Tree.objects.create(name=str(child_name))
                logger.info(new_tree_obj, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                text_response = excel_flows.cell_value(row_index, 1)
                text_response = validation_obj.remo_unwanted_security_characters(text_response)
                text_response = validation_obj.sanitize_html(text_response)

                logger.info(text_response, extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                sentence = {
                    "items": [
                        {
                            "text_response": str(text_response),
                            "speech_response": str(text_response),
                            "text_reprompt_response": str(text_response),
                            "speech_reprompt_response": str(text_response),
                        }
                    ]
                }

                cards = {
                    "items": [
                    ]
                }

                modes = {
                    "is_typable": "true",
                    "is_button": "true",
                    "is_slidable": "false",
                    "is_date": "false",
                    "is_dropdown": "false"
                }

                modes_param = {
                    "is_slidable": [{
                        "max": "",
                        "min": "",
                        "step": ""
                    }]
                }

                if new_tree_obj.response == None:
                    bot_response_obj = BotResponse.objects.create(
                        sentence=json.dumps(sentence),
                        cards=json.dumps(cards),
                        modes=json.dumps(modes),
                        modes_param=json.dumps(modes_param))
                else:
                    bot_response_obj = new_tree_obj.response
                new_tree_obj.response = bot_response_obj
                new_tree_obj.save()
                parent_obj.children.add(new_tree_obj)
                parent_obj.save()
                tree_id = new_tree_obj.pk
                row_index += 1
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("ERROR %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                    'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
                row_index += 1
            success_status = True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_flow_with_excel: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        success_status = False
    return success_status, flow_status_msg, is_error_in_trees


def sso_pre_login_check(user_params):
    try:
        email_id = user_params["EmailID"][0]

        if email_id == None:
            return

        if email_id.endswith("@gmail.com"):
            return

        # if not email_id.endswith("@allincall.in"):
        #     return

        # if email_id.endswith("@getcogno.ai"):
        #     email_id = email_id.replace("getcogno.ai", "allincall.in")

        try:
            user_obj = User.objects.get(username=email_id)
            # Provide bot builder access
            user_obj.role = "bot_builder"
            user_obj.status = "1"
            user_obj.save()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("User does not exists %s at %s", str(e), str(exc_tb.tb_lineno), extra={
                'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
            pass

        if email_id.endswith("@getcogno.ai"):

            # Provide EasySearch Access
            if SearchUser.objects.filter(user=user_obj).count() == 0:
                SearchUser.objects.create(user=user_obj)

            # Provide EasyTMS Access
            tms_agent_obj = None
            if Agent.objects.filter(user=user_obj).count() == 0:
                tms_agent_obj = Agent.objects.create(
                    user=user_obj, role="admin")
            else:
                tms_agent_obj = Agent.objects.filter(user=user_obj)[0]

            bot_objs = Bot.objects.filter(users__in=[user_obj])

            for ticket_category in TicketCategory.objects.filter(bot__in=bot_objs):
                tms_agent_obj.ticket_categories.add(ticket_category)

            for bot in bot_objs:
                tms_agent_obj.bots.add(bot)

            tms_agent_obj.save()

            # Provide LiveChat Access
            livechat_agent_obj = None
            if LiveChatUser.objects.filter(user=user_obj).count() == 0:
                livechat_agent_obj = LiveChatUser.objects.create(
                    user=user_obj, status="1")
            else:
                livechat_agent_obj = LiveChatUser.objects.filter(user=user_obj)[
                    0]

            livechat_agent_obj.is_allow_toggle = True

            livechat_agent_obj.save()

            # Provide Cobrowsing Access
            cobrowse_agent = None

            if CobrowseAgent.objects.filter(user=user_obj).count() == 0:
                cobrowse_agent = CobrowseAgent.objects.create(
                    user=user_obj, role="admin")
            else:
                cobrowse_agent = CobrowseAgent.objects.filter(user=user_obj)[0]

            cobrowse_agent.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("sso_pre_login_check: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_approval_mail_for_package_installation(package_manager_obj, email):
    request_user = package_manager_obj.request_user.username
    package = package_manager_obj.package
    bot_name = package_manager_obj.bot.name
    description = package_manager_obj.description
    redirect_url = settings.EASYCHAT_HOST_URL

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
            Dear Team,
        </p>
        <p>
            <b><u>{}</u></b> has requested for installation of new package called <b><u>{}</u></b> for bot <b><u>{}</u></b>.
        </p>
        <p>Reason: <b><u>{}</u></b></p>

        <p>Please visit {} and review the request.</p>

        <p>&nbsp;</p>""".format(request_user, package, bot_name, description, redirect_url)

    config = get_developer_console_settings()

    body += config.custom_report_template_signature

    body += """</div></body>"""

    send_email_to_customer_via_awsses(
        email, "New package installation request @CognoAI", body)


def get_whatsapp_simulator_response(mobile_number, end_point, message, payload):
    timestamp = datetime.datetime.now().replace(tzinfo=timezone.utc).timestamp()
    payload = payload.replace("TIME_STAMP", str(timestamp))
    payload = payload.replace("MOBILE_NUMBER", mobile_number)
    payload = payload.replace("TEXT_MESSAGE", message)
    payload = ast.literal_eval(payload)
    header = {'Content-Type': 'application/json'}
    resp = requests.post(url=end_point, headers=header,
                         data=json.dumps(payload))
    json_response = json.loads(resp.text)

    return json_response["response_packet"]["text_response"]["text"]


def get_request_origin(request):
    try:
        if 'HTTP_ORIGIN' not in request.META:
            origin = request.META.get('HTTP_REFERER')
        else:
            origin = request.META.get('HTTP_ORIGIN')

        origin = urlparse(origin)

        return origin.netloc
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_request_origin %s at %s",
                     str(e), str(exc_tb.tb_lineno))

    return None


"""
function: perform_nlp_benchmarking
input params:
    user_obj: active user object
    bot_obj: bot object which is to be tested
    request: user request data

Performs nlp benchmarking of selected bot and stores result in two excel sheets.
One Excel Sheet stores data for user to download.
The other contains error logs and datetime logs.
"""


def perform_nlp_benchmarking(user_obj, bot_obj, request, path):
    try:
        import xlrd
        # logger.info("perform_nlp_benchmarking started")
        user_query_list = []
        ideal_intent_name_list = []
        identified_intent_name_list = []
        ideal_intent_name_list_external = []
        identified_intent_name_list_external = []
        not_found_intent_list = []
        total_queries_length = 0
        correct_queries_length = 0

        bot_objs = [bot_obj]

        filename = path

        ensure_element_tree(xlrd)

        nlp_benchmarking_wb = xlrd.open_workbook(
            settings.MEDIA_ROOT + path)
        benchmarking_data = nlp_benchmarking_wb.sheet_by_index(0)
        rows_limit = benchmarking_data.nrows

        # Iterating in user uploaded excel
        for index in range(1, rows_limit):
            query = benchmarking_data.cell_value(index, 0)
            ideal_intent_name = benchmarking_data.cell_value(index, 1)

            # Fetch Ideal Intent Object
            try:
                ideal_intent_obj = Intent.objects.get(
                    bots__in=bot_objs, name=ideal_intent_name)

                # Get Original Intent Pk Value
                ideal_intent_pk = ideal_intent_obj.pk

                # Get Identified Intent
                status, identified_intent_obj = get_identified_intent(
                    query, user_obj, bot_objs, ideal_intent_obj.channels.all())

                # Increase total queries length by 1
                total_queries_length += 1

                # If status is true
                if status:
                    # If intent is matched
                    if ideal_intent_pk == identified_intent_obj.pk:
                        # Increase correct queries length by 1
                        correct_queries_length += 1

                    user_query_list.append(query)

                    html = "<a target='_blank' href='/chat/edit-intent/?intent_pk=" + \
                           str(ideal_intent_pk) + "&selected_language=en'>" + \
                           ideal_intent_name + "</a>"

                    ideal_intent_name_list.append(html)
                    ideal_intent_name_list_external.append(ideal_intent_name)

                    identified_intent_name = identified_intent_obj.name

                    html = "<a target='_blank' href='/chat/edit-intent/?intent_pk=" + \
                           str(identified_intent_obj.pk) + "&selected_language=en'>" + \
                           identified_intent_name + "</a>"

                    identified_intent_name_list.append(html)
                    identified_intent_name_list_external.append(
                        identified_intent_name)

                else:

                    user_query_list.append(query)

                    if identified_intent_obj != []:
                        if ideal_intent_obj in identified_intent_obj:
                            correct_queries_length += 1

                    if identified_intent_obj == []:
                        identified_intent_name_list.append("None")
                        identified_intent_name_list_external.append("None")

                    else:

                        identified_intent_name = []
                        identified_intent_name_external = []

                        for identified_intent in identified_intent_obj:
                            intent_name = identified_intent.name
                            html = "<a target='_blank' href='/chat/edit-intent/?intent_pk=" + \
                                   str(identified_intent.pk) + "&selected_language=en'>" + \
                                   intent_name + "</a>"
                            identified_intent_name.append(html)
                            identified_intent_name_external.append(intent_name)
                        identified_intent_name_list.append(
                            "<br> ".join(identified_intent_name))
                        identified_intent_name_list_external.append(
                            ','.join(identified_intent_name_external))

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Error perform_nlp_benchmarking %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

                user_query_list.append(query)
                ideal_intent_name_list.append(ideal_intent_name)
                ideal_intent_name_list_external.append(ideal_intent_name)
                not_found_intent_list.append(ideal_intent_name)

                channels = Channel.objects.filter(is_easychat_channel=True)

                status, identified_intent_obj = get_identified_intent(
                    query, user_obj, bot_objs, channels)

                if status:

                    identified_intent_name = identified_intent_obj.name

                    html = "<a target='_blank' href='/chat/edit-intent/?intent_pk=" + \
                           str(identified_intent_obj.pk) + "&selected_language=en'>" + \
                           identified_intent_name + "</a>"

                    identified_intent_name_list.append(html)
                    identified_intent_name_list_external.append(
                        identified_intent_name)

                else:

                    if identified_intent_obj != []:
                        identified_intent_name = []
                        identified_intent_name_external = []
                        for identified_intent in identified_intent_obj:
                            intent_name = identified_intent.name
                            html = "<a target='_blank' href='/chat/edit-intent/?intent_pk=" + \
                                   str(identified_intent.pk) + "&selected_language=en'>" + \
                                   intent_name + "</a>"
                            identified_intent_name.append(html)
                            identified_intent_name_external.append(intent_name)

                        identified_intent_name_list.append(
                            "<br> ".join(identified_intent_name))
                        identified_intent_name_list_external.append(
                            ','.join(identified_intent_name_external))
                    else:
                        identified_intent_name_list.append("None")
                        identified_intent_name_list_external.append("None")

        from xlwt import Workbook
        import datetime
        nlp_benchmarking_wb = Workbook()
        sheet1 = nlp_benchmarking_wb.add_sheet("NLP Benchmarking Result")
        sheet2 = nlp_benchmarking_wb.add_sheet("NLP Benchmarking Analytics")
        sheet3 = nlp_benchmarking_wb.add_sheet("List of intents not in bot")

        sheet1.write(0, 0, "User Query")
        sheet1.col(0).width = 256 * 40
        sheet1.write(0, 1, "Expected Intent in the Bot")
        sheet1.col(1).width = 256 * 30
        sheet1.write(0, 2, "Identified Intent by the Bot")
        sheet1.col(2).width = 256 * 30

        sheet2.write(0, 0, "Total sentences")
        sheet2.col(0).width = 256 * 30
        sheet2.write(0, 1, "Correct sentences")
        sheet2.col(1).width = 256 * 30
        sheet2.write(0, 2, "Accuracy")
        sheet2.col(2).width = 256 * 30
        sheet2.write(0, 3, "Bot ID")
        sheet2.col(2).width = 256 * 30
        sheet2.write(0, 4, "Bot Name")
        sheet2.col(3).width = 256 * 30
        sheet2.write(0, 5, "Date of Test")
        sheet2.col(4).width = 256 * 30

        sheet3.write(0, 0, "Intents not available in the bot")
        sheet3.col(0).width = 256 * 30

        for index in range(len(user_query_list)):
            sheet1.write(index + 1, 0, user_query_list[index])
            sheet1.write(index + 1, 1, ideal_intent_name_list_external[index])
            sheet1.write(
                index + 1, 2, identified_intent_name_list_external[index])

        sheet2.write(1, 0, str(total_queries_length))
        sheet2.write(1, 1, str(correct_queries_length))
        if total_queries_length == 0:
            sheet2.write(1, 2, "NA")
        else:
            accuracy = round(correct_queries_length *
                             100 / total_queries_length, 2)
            sheet2.write(1, 2, str(accuracy) + '%')
        sheet2.write(1, 3, str(bot_obj.pk))
        sheet2.write(1, 4, str(bot_obj.name))
        sheet2.write(
            1, 5, str(datetime.datetime.now().strftime("%d-%B-%Y %I:%M %p")))

        for index in range(len(not_found_intent_list)):
            sheet3.write(index + 1, 0, not_found_intent_list[index])

        filename_customer = "NLPBenchMarking_Export" + \
                            str(request.user.username).replace(
                                '.', '-') + "_" + str(bot_obj.pk) + ".xls"
        nlp_benchmarking_wb.save(settings.MEDIA_ROOT + filename_customer)

        # logger.info("Excel for customer file has been created Successfully.")
        logger.info("Excel file for customer has been created Successfully.", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        # Writing to excel sheet for internal use

        nlp_benchmarking_wb = Workbook()
        sheet1 = nlp_benchmarking_wb.add_sheet("NLP Benchmarking Result")
        sheet2 = nlp_benchmarking_wb.add_sheet("NLP Benchmarking Analytics")
        sheet3 = nlp_benchmarking_wb.add_sheet("List of intents not in bot")

        sheet1.write(0, 0, "User Query")
        sheet1.write(0, 1, "Expected Intent in the Bot")
        sheet1.write(0, 2, "Identified Intent by the Bot")

        sheet2.write(0, 0, "Total sentences")
        sheet2.write(0, 1, "Correct sentences")
        sheet3.write(0, 2, "Accuracy")
        sheet2.write(0, 3, "Bot ID")
        sheet2.write(0, 4, "Bot Name")
        sheet2.write(0, 5, "Date of Test")
        sheet2.write(0, 6, "Export File path")

        sheet3.write(0, 0, "Intents not available in the bot")

        for index in range(len(user_query_list)):
            sheet1.write(index + 1, 0, user_query_list[index])
            sheet1.write(index + 1, 1, ideal_intent_name_list[index])
            sheet1.write(index + 1, 2, identified_intent_name_list[index])

        sheet2.write(1, 0, str(total_queries_length))
        sheet2.write(1, 1, str(correct_queries_length))
        if total_queries_length == 0:
            sheet2.write(1, 2, "NA")
        else:
            accuracy = round(correct_queries_length *
                             100 / total_queries_length, 2)
            sheet2.write(1, 2, str(accuracy) + '%')
        sheet2.write(1, 3, str(bot_obj.pk))
        sheet2.write(1, 4, str(bot_obj.name))
        sheet2.write(
            1, 5, str(datetime.datetime.now().strftime("%d-%B-%Y %I:%M %p")))

        for index in range(len(not_found_intent_list)):
            sheet3.write(index + 1, 0, not_found_intent_list[index])

        filename = "NLPBenchmarking_" + \
                   str(request.user.username).replace(
                       '.', '-') + "_" + str(bot_obj.pk) + ".xls"

        logger.info(filename, extra={'AppName': 'EasyChat', 'user_id': 'None',
                                     'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        sheet2.write(1, 6, str(str(settings.MEDIA_ROOT).split('/')
                               [-2] + '/' + filename_customer))
        nlp_benchmarking_wb.save(settings.MEDIA_ROOT + filename)
        logger.info("Excel file for internal use has been created Successfully.", extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error get_request_origin %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    cmd = "rm " + settings.MEDIA_ROOT + path
    import os
    os.system(cmd)


def logout_user(user):
    user.is_online = False
    user.save()
    secured_login = SecuredLogin.objects.get(user=user)
    secured_login.failed_attempts = 0
    secured_login.save()

    audit_trail_data = json.dumps({
        "user_id": user.pk
    })
    try:
        livechat_user = LiveChatUser.objects.get(user=user)
        sessions_obj = LiveChatSessionManagement.objects.filter(
            user=livechat_user, session_completed=False)[0]
        if sessions_obj.user.is_online:
            diff = datetime.datetime.now(
                timezone.utc) - sessions_obj.session_ends_at
            sessions_obj.online_time += diff.seconds
            sessions_obj.session_ends_at = timezone.now()
            sessions_obj.session_completed = True
            sessions_obj.is_idle = False
            time_diff = datetime.datetime.now(
                timezone.utc) - sessions_obj.last_idle_time
            sessions_obj.idle_time += time_diff.seconds
            sessions_obj.save()
        else:
            diff = datetime.datetime.now(
                timezone.utc) - sessions_obj.session_ends_at
            sessions_obj.offline_time += diff.seconds
            sessions_obj.session_ends_at = timezone.now()
            sessions_obj.session_completed = True
            if sessions_obj.agent_not_ready.all().count():
                agent_not_ready_obj = sessions_obj.agent_not_ready.all().order_by(
                    '-not_ready_starts_at')[0]
                agent_not_ready_obj.not_ready_ends_at = timezone.now()
                agent_not_ready_obj.save()
            sessions_obj.save()

        livechat_user.is_online = False
        livechat_user.is_session_exp = True
        livechat_user.save()
        save_audit_trail_data("8", livechat_user, LiveChatAuditTrail)
    except Exception:
        pass

    save_audit_trail(user, USER_LOGGED_OUT, audit_trail_data)

    try:
        active_agent = CobrowseAgent.objects.get(
            user=user, is_account_active=True)
        active_agent.is_active = False
        active_agent.is_agent_connected = False
        active_agent.save()
        save_audit_trail_easyassist(active_agent, "2",
                                    "Logout from System", CobrowsingAuditTrail)
    except Exception:
        pass


'''
    Method : delete_user_session
    Input  : UserSession object
    Work   : Delete Session, UserSession object
'''


def delete_user_session(user_session):
    try:
        logger.info("In delete_user_session", extra={'AppName': 'EasyChat', 'user_id': user_session.user.username,
                                                     'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        session_objs = Session.objects.filter(pk=user_session.session_key)
        user_session.delete()
        if session_objs:
            session_objs.delete()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In delete_user_session: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user_session.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
    Method : logout_all
    Input  : username

    Work   : remove all session of user -> username
"""


def logout_all(username):
    try:
        logger.info("In logout_all", extra={'AppName': 'EasyChat', 'user_id': username,
                                            'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        user_session_objs = UserSession.objects.filter(user__username=username)
        is_another_session_exist = user_session_objs.count()
        for user_session_obj in user_session_objs:
            delete_user_session(user_session_obj)

        try:
            if is_another_session_exist:
                user = User.objects.get(username=username)
                logout_user(user)
        except Exception:
            logger.error("User does not exist", extra={
                'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In delete_user_session: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
    Method : is_online
    Input  : username

    Work   : is atleast one UserSession exist then user is active ( return True )
"""


def is_online(username):
    try:
        user_session_objs = UserSession.objects.filter(user__username=username)
        if user_session_objs:
            return True
        else:
            return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In is_online: %s at %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': str(username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return False


'''
    Method : refresh_status_user_session
    Work   : check for perticular user session
             if session last update is greater then max limit ( EASYCHAT_SESSION_AGE )
             then logout user and save audit trails
             delete Session object
             delete UserSession object

'''


def refresh_status_user_session(user_session):
    try:
        total_seconds = int(
            (timezone.now() - user_session.last_update_datetime).total_seconds())
        logger.info("In refresh_status_user_session - %s seconds - %s ", str(total_seconds),
                    str(user_session.session_key), extra={'AppName': 'EasyChat', 'user_id': user_session.user.username,
                                                          'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        if total_seconds > settings.EASYCHAT_SESSION_AGE:
            user = User.objects.get(username=user_session.user.username)
            check_and_expire_livechat_session(user)
            delete_user_session(user_session)
            logout_user(user)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In refresh_status_user_session: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': str(user_session.user.username), 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


'''
    Method : login_activity
    Work   : It is calling after every five seconds by scheduler
             refresh_status_user_session of every UserSession
'''


def login_activity():
    user_session_objs = UserSession.objects.all()

    for user_session_obj in user_session_objs:
        refresh_status_user_session(user_session_obj)


'''
    Method : add_confirmation_and_reset_tree
    input  : parent_tree_obj
             intent_pk
    Work   : It will create confirm and reset tree for parent_tree_obj
'''


def add_confirmation_and_reset_tree(parent_tree_obj, intent_pk):
    def create_confirm_bot_response(response_text):
        sentence_json = {
            "items": [{
                "text_response": "<p>" + response_text + "</p>",
                "speech_response": response_text,
                "hinglish_response": "",
                "text_reprompt_response": "<p>" + response_text + "</p>",
                "speech_reprompt_response": response_text,
                "tooltip_response": ""
            }]
        }
        return json.dumps(sentence_json)

    def reset_pipe_processor(reset_pk):
        name = "reset_pipe_processor_" + str(reset_pk)
        code = '''
from EasyChatApp.utils import logger
import sys
def f(x):
    json_response = {}
    json_response['status_code'] = '500'
    json_response['status_message'] = 'Internal server error.'
    json_response['recur_flag'] = False
    json_response['message'] = 'reset_pipe_processor'
    json_response['API_REQUEST_PACKET'] = {}
    json_response['API_RESPONSE_PACKET'] = {}
    json_response['data'] = {}
    try:
        #write your code here
        json_response['recur_flag'] = True
        json_response['status_code'] = '200'
        json_response['print'] = 'Hello world!'
        return json_response
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error('PipeProcessorContent: %s at %s',str(E), str(exc_tb.tb_lineno))
        json_response['status_code'] = '500'
        json_response['status_message'] = 'ERROR :-  '+str(E)+ ' at line no: ' +str(exc_tb.tb_lineno)
        return json_response
        '''

        processor_obj = Processor.objects.create(name=name, function=code)
        # processor_obj.function = code
        processor_obj.processor_lang = "1"
        processor_obj.save(True)
        return processor_obj

    # Create confirm tree
    confirm_tree_obj = Tree.objects.create(name='Confirm')
    confirm_tree_obj.response = BotResponse.objects.create(
        sentence=create_confirm_bot_response("Thank you"))
    confirm_tree_obj.save()

    # Create Reset tree
    reset_tree_obj = Tree.objects.create(name='Reset')
    reset_tree_obj.response = BotResponse.objects.create()
    reset_tree_obj.pipe_processor = reset_pipe_processor(reset_tree_obj.pk)
    reset_tree_obj.children.add(Tree.objects.get(intent=intent_pk))
    reset_tree_obj.save()

    # Add confirm and reste tree to confirm_reset_parent
    confirm_reset_parent_obj = Tree.objects.create(name='ConfirmReset')
    confirm_reset_parent_obj.children.add(confirm_tree_obj)
    confirm_reset_parent_obj.children.add(reset_tree_obj)
    confirm_reset_parent_obj.response = BotResponse.objects.create(
        sentence=create_confirm_bot_response("Confirm"))
    confirm_reset_parent_obj.accept_keywords = "confirm reset"
    confirm_reset_parent_obj.save()

    parent_tree_obj.children.add(confirm_reset_parent_obj)
    parent_tree_obj.confirmation_reset_tree_pk = confirm_reset_parent_obj.id
    parent_tree_obj.is_confirmation_and_reset_enabled = True
    parent_tree_obj.save()


'''
    Method : remove_confirmation_and_reset_tree
    input  : parent_tree_obj
    Work   : It will remove confirm and reset tree from parent_tree_obj
'''


def remove_confirmation_and_reset_tree(parent_tree_obj):
    confirmation_reset_tree_pk = parent_tree_obj.confirmation_reset_tree_pk
    if confirmation_reset_tree_pk is not None:
        confirmation_reset_tree_obj = Tree.objects.get(
            id=confirmation_reset_tree_pk)

        parent_tree_obj.children.remove(confirmation_reset_tree_obj)
        parent_tree_obj.confirmation_reset_tree_pk = None
        parent_tree_obj.is_confirmation_and_reset_enabled = False
        parent_tree_obj.save()

        # Delete Reset and Confirm subtree
        confirmation_reset_tree_obj.children.all().delete()
        confirmation_reset_tree_obj.delete()
    else:
        parent_tree_obj.is_confirmation_and_reset_enabled = False
        parent_tree_obj.save()


"""
function: mark_livechat_user_online
input params:
    user_obj: EasyChatApp user object

If user is livechat agent, then mark as online
"""


def mark_livechat_user_online(user_obj):
    try:
        livechat_user_obj = LiveChatUser.objects.filter(
            user=user_obj, is_deleted=False)
        if livechat_user_obj.exists():
            livechat_user_obj = livechat_user_obj.first()
            livechat_user_obj.is_online = True
            livechat_user_obj.current_status = "6"
            livechat_user_obj.mark_online()
            time_zone = pytz.timezone(settings.TIME_ZONE)
            livechat_user_obj.last_updated_time = datetime.datetime.now().astimezone(time_zone)
            livechat_user_obj.save(update_fields=['is_online', 'current_status', 'last_updated_time'])
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("mark_livechat_user_online: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_custom_js_file(bot_id):
    try:
        file_path = "EasyChatApp/static/EasyChatApp/js/theme3_" + \
                    str(bot_id) + ".js"
        if os.path.isfile(file_path):
            logger.info("create_custom_js file already exists", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
        else:
            # Saving in main static folder
            theme3_js_file = open(
                settings.BASE_DIR + "/EasyChatApp/static/EasyChatApp/js/theme3.js", "r")

            file_path = "EasyChatApp/static/EasyChatApp/js/theme3_" + \
                        str(bot_id) + ".js"
            write_file = theme3_js_file.read()
            theme3_js_file = open(file_path, "w")
            theme3_js_file.write(write_file)
            theme3_js_file.close()

            # Saving in static folder
            try:
                theme3_js_file = open(
                    settings.BASE_DIR + "/EasyChatApp/static/EasyChatApp/js/theme3.js", "r")
                file_path = "static/EasyChatApp/js/theme3_" + \
                            str(bot_id) + ".js"
                write_file = theme3_js_file.read()
                theme3_js_file = open(file_path, "w")
                theme3_js_file.write(write_file)
                theme3_js_file.close()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("create_custom_js_file: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
                pass

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_custom_js_file: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_custom_css_file(bot_id, theme_name):
    try:
        theme_id = theme_name.split('_')[1]
        file_path = "EasyChatApp/static/EasyChatApp/css/theme" + \
                    str(theme_id) + "_" + str(bot_id) + ".css"
        if os.path.isfile(file_path):
            logger.info("create_custom_css file already exists", extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
        else:
            # Saving in main static folder
            custom_css_file = open(
                settings.BASE_DIR + "/EasyChatApp/static/EasyChatApp/css/theme" + str(theme_id) + ".css", "r")

            file_path = "EasyChatApp/static/EasyChatApp/css/theme" + \
                        str(theme_id) + "_" + str(bot_id) + ".css"
            write_file = custom_css_file.read()
            custom_css_file = open(file_path, "w")
            custom_css_file.write(write_file)
            custom_css_file.close()

            # Saving in static folder
            try:
                custom_css_file = open(
                    settings.BASE_DIR + "/EasyChatApp/static/EasyChatApp/css/theme" + str(theme_id) + ".css", "r")
                file_path = "static/EasyChatApp/css/theme" + \
                            str(theme_id) + "_" + str(bot_id) + ".css"
                write_file = custom_css_file.read()
                custom_css_file = open(file_path, "w")
                custom_css_file.write(write_file)
                custom_css_file.close()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("create_custom_css_file: %s at %s",
                             e, str(exc_tb.tb_lineno),
                             extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None',
                                    'bot_id': 'none'})
                pass

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_custom_css_file: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def send_mail_of_analytics(to_send_in_message, file_url, to_email):
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

        body = body.format(to_send_in_message, file_url)

        for email in to_email.split(","):
            send_email_to_customer_via_awsses(email, to_send_in_message, body)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def get_language_text_for_excel_for_supported_languages(supported_languages):
    language_text = ""
    try:
        language_text = list(
            supported_languages.values_list("name_in_english"))
        language_text = [lang[0] for lang in language_text]
        language_text = ", ".join(language_text)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in get_language_text_for_excel_for_supported_languages  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
    return language_text


def create_and_send_message_analytics(start_date, end_date, channel_value, bot_pk, filter_type_particular, email_id,
                                      category_name, selected_language, supported_languages, to_be_mailed=True, export_request_obj=None):
    try:
        filter_type = str(filter_type_particular)

        datetime_start = start_date
        datetime_end = end_date
        channel_name = channel_value

        uat_bot_obj = Bot.objects.get(
            pk=int(bot_pk), is_deleted=False, is_uat=True)
        # bot_info_obj = BotInfo.objects.get(bot=uat_bot_obj)

        bot_objs = [uat_bot_obj]

        # validation_obj = EasyChatInputValidation()

        if category_name != "All":
            category_obj = Category.objects.get(
                bot=uat_bot_obj, name=category_name)

        # mis_filtered_objs = MISDashboard.objects.filter(bot__in=bot_objs)

        if channel_name == "All" and category_name == "All":
            mis_objects = MISDashboard.objects.filter(
                bot__in=bot_objs, creation_date=datetime.datetime.now().date())
            previous_mis_objects = MessageAnalyticsDaily.objects.filter(
                bot__in=bot_objs)
        elif category_name == "All":
            mis_objects = MISDashboard.objects.filter(
                bot__in=bot_objs, channel_name=channel_name, creation_date=datetime.datetime.now().date())
            previous_mis_objects = MessageAnalyticsDaily.objects.filter(
                bot__in=bot_objs, channel_message=Channel.objects.get(name=channel_name))
            # mis_filtered_objs = mis_filtered_objs.filter(
            #     channel_name=channel_name)
        elif channel_name == "All":
            mis_objects = MISDashboard.objects.filter(
                bot__in=bot_objs, category__name=category_name, creation_date=datetime.datetime.now().date())
            previous_mis_objects = MessageAnalyticsDaily.objects.filter(
                bot__in=bot_objs, category=category_obj)
            # mis_filtered_objs = mis_filtered_objs.filter(
            #     category__name=category_name)
        else:
            mis_objects = MISDashboard.objects.filter(
                bot__in=bot_objs, channel_name=channel_name, category__name=category_name,
                creation_date=datetime.datetime.now().date())
            previous_mis_objects = MessageAnalyticsDaily.objects.filter(
                bot__in=bot_objs, category=category_obj, channel_message=Channel.objects.get(name=channel_name))
            # mis_filtered_objs = mis_filtered_objs.filter(
            #     channel_name=channel_name, category__name=category_name)

        if selected_language.lower() != "all":
            mis_objects = mis_objects.filter(
                selected_language__in=supported_languages)
            previous_mis_objects = previous_mis_objects.filter(
                selected_language__in=supported_languages)
            # mis_filtered_objs = mis_filtered_objs.filter(
            #     selected_language__in=supported_languages)

        previous_mis_objects = previous_mis_objects.filter(date_message_analytics__gte=datetime_start, date_message_analytics__lte=datetime_end)
        mis_objects = mis_objects.filter(creation_date=datetime.datetime.today().date())

        message_analytics_list = []

        if filter_type == "1":
            total_hours_passed = datetime.datetime.today().hour
            avg_msgs = mis_objects.count()
            if total_hours_passed > 0:
                avg_msgs = math.ceil(
                    (avg_msgs / float(total_hours_passed)) * 24.0)
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
                total_intuitive_messages = date_filtered_mis_objects.aggregate(
                    Sum('intuitive_query_count'))['intuitive_query_count__sum']
                total_answered_messages = date_filtered_mis_objects.aggregate(
                    Sum('answered_query_count'))['answered_query_count__sum']
                total_unanswered_messages = date_filtered_mis_objects.aggregate(
                    Sum('unanswered_query_count'))['unanswered_query_count__sum']

                # false_positive_messages = mis_filtered_objs.filter(
                #     creation_date=temp_datetime, flagged_queries_positive_type="1").count()

                if total_messages == None:
                    total_messages = 0

                if total_answered_messages == None:
                    total_answered_messages = 0

                if total_unanswered_messages == None:
                    total_unanswered_messages = 0
                if total_intuitive_messages == None:
                    total_intuitive_messages = 0

                message_analytics_list.append({
                    "label": str(temp_datetime.strftime("%d-%b-%y")),
                    "total_messages": total_messages,
                    "total_answered_messages": total_answered_messages,
                    "total_unanswered_messages": total_unanswered_messages,
                    "predicted_messages_no": total_messages,
                    "total_intuitive_messages": total_intuitive_messages
                    # "false_positive_messages": false_positive_messages
                })

            if datetime_end == datetime.datetime.today().date():
                date_filtered_mis_objects = mis_objects
                total_messages = date_filtered_mis_objects.count()
                total_unanswered_messages = date_filtered_mis_objects.filter(
                    intent_name=None, is_intiuitive_query=False).exclude(message_received="").count()
                total_intuitive_messages = date_filtered_mis_objects.filter(intent_name=None, is_intiuitive_query=True).count()
                total_answered_messages = total_messages - (total_unanswered_messages + total_intuitive_messages)

                # false_positive_messages = date_filtered_mis_objects.filter(
                #     flagged_queries_positive_type="1").count()
                message_analytics_list.append({
                    "label": str((datetime_end).strftime("%d-%b-%y")),
                    "total_messages": total_messages,
                    "total_answered_messages": total_answered_messages,
                    "total_unanswered_messages": total_unanswered_messages,
                    "predicted_messages_no": total_messages,
                    "total_intuitive_messages": total_intuitive_messages
                    # "false_positive_messages": false_positive_messages
                })
                message_analytics_list[-1]["predicted_messages_no"] = avg_msgs

        elif filter_type == "2":

            total_hours_passed = (6 * 24) + datetime.datetime.today().hour

            start_week_date = datetime.datetime.today() - datetime.timedelta(7)

            previous_mis_objects_count = previous_mis_objects.filter(
                date_message_analytics__gte=start_week_date).aggregate(Sum('total_messages_count'))[
                'total_messages_count__sum']

            if previous_mis_objects_count == None:
                previous_mis_objects_count = 0

            avg_msgs = math.ceil(
                ((previous_mis_objects_count + mis_objects.count()) / total_hours_passed) * 7.0 * 24.0) + 1

            no_days = (datetime_end - datetime_start).days
            no_weeks = int(no_days / 7.0) + 1

            for week in range(no_weeks):
                temp_end_datetime = datetime_end - datetime.timedelta(week * 7)
                temp_start_datetime = datetime_end - datetime.timedelta((week + 1) * 7)

                if temp_start_datetime < datetime_start:
                    temp_start_datetime = datetime_start - datetime.timedelta(1)

                date_filtered_mis_objects = previous_mis_objects

                date_filtered_mis_objects = previous_mis_objects.filter(
                    date_message_analytics__gt=temp_start_datetime, date_message_analytics__lte=temp_end_datetime)
                total_messages = date_filtered_mis_objects.aggregate(
                    Sum('total_messages_count'))['total_messages_count__sum']

                total_answered_messages = date_filtered_mis_objects.aggregate(
                    Sum('answered_query_count'))['answered_query_count__sum']
                total_unanswered_messages = date_filtered_mis_objects.aggregate(
                    Sum('unanswered_query_count'))['unanswered_query_count__sum']
                total_intuitive_messages = date_filtered_mis_objects.aggregate(
                    Sum('intuitive_query_count'))['intuitive_query_count__sum']

                # false_positive_messages = mis_filtered_objs.filter(
                #     flagged_queries_positive_type="1", creation_date__gt=temp_start_datetime,
                #     creation_date__lte=temp_end_datetime).count()

                if total_messages == None:
                    total_messages = 0

                if total_answered_messages == None:
                    total_answered_messages = 0

                if total_unanswered_messages == None:
                    total_unanswered_messages = 0
                
                if total_intuitive_messages == None:
                    total_intuitive_messages = 0

                temp_start_datetime_str = (temp_start_datetime + datetime.timedelta(1)).strftime(
                    "%d/%m")
                temp_end_datetime_str = (
                    temp_end_datetime).strftime("%d/%m")
                message_analytics_list.append({
                    "label": str(temp_start_datetime_str + "-" + temp_end_datetime_str),
                    "total_messages": total_messages,
                    "total_answered_messages": total_answered_messages,
                    "total_unanswered_messages": total_unanswered_messages,
                    "predicted_messages_no": total_messages,
                    "total_intuitive_messages": total_intuitive_messages
                    # "false_positive_messages": false_positive_messages
                })

            message_analytics_list = message_analytics_list[::-1]
            if datetime_end == datetime.datetime.today().date():
                date_filtered_mis_objects = mis_objects
                total_messages = date_filtered_mis_objects.count()
                total_unanswered_messages = date_filtered_mis_objects.filter(intent_name=None, is_unidentified_query=True, is_intiuitive_query=False).exclude(message_received="").count()
                total_intuitive_messages = date_filtered_mis_objects.filter(intent_name=None, is_intiuitive_query=True).count()
                total_answered_messages = total_messages - (total_unanswered_messages + total_intuitive_messages)
                message_analytics_list[-1]["total_messages"] = message_analytics_list[-1]["total_messages"] + total_messages
                message_analytics_list[-1]["total_unanswered_messages"] = message_analytics_list[-1]["total_unanswered_messages"] + total_unanswered_messages
                message_analytics_list[-1]["total_intuitive_messages"] = message_analytics_list[-1]["total_intuitive_messages"] + total_intuitive_messages
                message_analytics_list[-1]["total_answered_messages"] = message_analytics_list[-1]["total_answered_messages"] + total_answered_messages
                message_analytics_list[-1]["predicted_messages_no"] = avg_msgs
                # message_analytics_list[-1]["false_positive_messages"] += date_filtered_mis_objects.filter(flagged_queries_positive_type="1").count()

        else:
            month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
                r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days + 1)).keys())

            total_hours_passed = datetime.datetime.today().hour + ((datetime.datetime.today().day - 1) * 24.0)

            start_month_date = datetime.datetime.today(
            ) - datetime.timedelta(datetime.datetime.today().day - 1)
            avg_msgs = math.ceil(((previous_mis_objects.filter(
                date_message_analytics__gte=start_month_date).count() + mis_objects.count()) / total_hours_passed) * 24.0 * datetime.datetime.today().day) + 1

            for month in month_list:
                temp_month = month_to_num_dict[month.split("-")[0]]
                temp_year = int(month.split("-")[1])
                date_filtered_mis_objects = previous_mis_objects.filter(
                    date_message_analytics__month=temp_month, date_message_analytics__year=temp_year)

                total_messages = date_filtered_mis_objects.aggregate(
                    Sum('total_messages_count'))['total_messages_count__sum']

                total_answered_messages = date_filtered_mis_objects.aggregate(
                    Sum('answered_query_count'))['answered_query_count__sum']
                total_unanswered_messages = date_filtered_mis_objects.aggregate(
                    Sum('unanswered_query_count'))['unanswered_query_count__sum']
                total_intuitive_messages = date_filtered_mis_objects.aggregate(
                    Sum('intuitive_query_count'))['intuitive_query_count__sum']

                # false_positive_messages = mis_filtered_objs.filter(
                #     flagged_queries_positive_type="1", creation_date__month=temp_month,
                #     creation_date__year=temp_year).count()

                if total_messages == None:
                    total_messages = 0

                if total_answered_messages == None:
                    total_answered_messages = 0

                if total_unanswered_messages == None:
                    total_unanswered_messages = 0
                
                if total_intuitive_messages == None:
                    total_intuitive_messages = 0

                message_analytics_list.append({
                    "label": month,
                    "total_messages": total_messages,
                    "total_answered_messages": total_answered_messages,
                    "total_unanswered_messages": total_unanswered_messages,
                    "predicted_messages_no": total_messages,
                    "total_intuitive_messages": total_intuitive_messages
                    # "false_positive_messages": false_positive_messages
                })

            if datetime_end == datetime.datetime.today().date():
                message_analytics_list[-1]["predicted_messages_no"] = avg_msgs

                date_filtered_mis_objects = mis_objects
                total_messages = date_filtered_mis_objects.count()
                total_unanswered_messages = date_filtered_mis_objects.filter(
                    intent_name=None, is_unidentified_query=True, is_intiuitive_query=False).exclude(message_received="").count()
                total_intuitive_messages = date_filtered_mis_objects.filter(intent_name=None, is_intiuitive_query=True).count()
                total_answered_messages = total_messages - (total_unanswered_messages + total_intuitive_messages)
                message_analytics_list[-1]["total_messages"] = message_analytics_list[-1]["total_messages"] + total_messages
                message_analytics_list[-1]["total_unanswered_messages"] = message_analytics_list[-1]["total_unanswered_messages"] + total_unanswered_messages
                message_analytics_list[-1]["total_intuitive_messages"] = message_analytics_list[-1]["total_intuitive_messages"] + total_intuitive_messages
                message_analytics_list[-1]["total_answered_messages"] = message_analytics_list[-1]["total_answered_messages"] + total_answered_messages
                message_analytics_list[-1]["predicted_messages_no"] = avg_msgs
                # message_analytics_list[-1]["false_positive_messages"] += date_filtered_mis_objects.filter(flagged_queries_positive_type="1").count()

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Date")
        sheet1.write(0, 1, "Total Messages")
        sheet1.write(0, 2, "Total Answered Messages")
        sheet1.write(0, 3, "Total Unanswered Messages")
        sheet1.write(0, 4, "Total intuitive Messages")
        sheet1.write(0, 5, "Total Predicted Messages")

        curr_col_no = 4
        # if bot_info_obj.enable_flagged_queries_status:
        #     curr_col_no = curr_col_no + 1
        #     sheet1.write(0, curr_col_no, "False Positives")

        if category_name != "All":
            curr_col_no = curr_col_no + 1
            sheet1.write(0, curr_col_no, "Category")

        if selected_language.lower() != "all":
            curr_col_no = curr_col_no + 1
            sheet1.write(0, curr_col_no, "Language")
            language_text = get_language_text_for_excel_for_supported_languages(
                supported_languages)

        row = 1
        for message in message_analytics_list:
            sheet1.write(row, 0, message["label"])
            sheet1.write(row, 1, str(message["total_messages"]))
            sheet1.write(row, 2, str(message["total_answered_messages"]))
            sheet1.write(row, 3, str(message["total_unanswered_messages"]))
            sheet1.write(row, 4, str(message["total_intuitive_messages"]))
            if message["predicted_messages_no"]:
                sheet1.write(row, 5, str(message["predicted_messages_no"]))
            else:
                sheet1.write(row, 5, "0")
            curr_col_no = 5
            # if bot_info_obj.enable_flagged_queries_status:
            #     curr_col_no = curr_col_no + 1
            #     if message["false_positive_messages"] != 0:
            #         sheet1.write(row, curr_col_no, str(
            #             message["false_positive_messages"]))
            #         sheet1.col(curr_col_no).width = 15 * 256
            #     else:
            #         sheet1.write(row, curr_col_no, "-")

            if category_name != "All":
                curr_col_no = curr_col_no + 1
                sheet1.write(row, curr_col_no, category_name)
            if selected_language.lower() != "all":
                curr_col_no = curr_col_no + 1
                sheet1.write(row, curr_col_no, language_text)
            row += 1
        filename_for_mail = 'message_analytics_from_' + \
                            start_date.strftime("%d-%m-%Y") + '_to_' + \
                            end_date.strftime("%d-%m-%Y")
        filename = filename_for_mail + '.xls'

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        test_wb.save(secured_files_path + filename)

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        # #zip_obj = ZipFile(settings.MEDIA_ROOT + "livechat-chat-history/" + "/ChatHistoryTodaysDay.zip", "w")
        # file_path =  "livechat-chat-history/"  + "todays_chat_history" + '.xls'
        # logger.error(file_path , extra={'AppName':'LiveChat'})
        # #zip_obj.write(settings.MEDIA_ROOT + file_path, basename(file_path))
        # #zip_obj.close()
        if export_request_obj:
            export_request_obj.export_file_path = file_url
            export_request_obj.is_completed = True
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])
        if to_be_mailed:
            send_mail_of_analytics('Message Analytics',
                                   file_url, email_id)
        else:
            return file_url
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
        pass


def create_user_analytics(start_date, end_date, channel_value, bot_pk, filter_type_particular, email_id,
                          selected_language, supported_languages, to_be_mailed=True, export_request_obj=None):
    try:
        channel_name = channel_value
        filter_type = str(filter_type_particular)

        datetime_start = start_date
        datetime_end = end_date
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_pk), is_deleted=False, is_uat=True)
        bot_objs = [uat_bot_obj]
        if channel_name == "All":
            mis_objects = MISDashboard.objects.filter(
                bot__in=bot_objs, creation_date=datetime.datetime.now().date())
            previous_mis_objects = UniqueUsers.objects.filter(
                bot__in=bot_objs)
        else:
            mis_objects = MISDashboard.objects.filter(
                bot__in=bot_objs, channel_name=channel_name, creation_date=datetime.datetime.now().date())
            previous_mis_objects = UniqueUsers.objects.filter(
                bot__in=bot_objs, channel=Channel.objects.get(name=channel_name))

        if selected_language.lower() != "all":
            mis_objects = mis_objects.filter(
                selected_language__in=supported_languages)
            previous_mis_objects = previous_mis_objects.filter(
                selected_language__in=supported_languages)

        previous_mis_objects = previous_mis_objects.filter(date__gte=datetime_start, date__lte=datetime_end)

        user_analytics_list = []
        if filter_type == "1":
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

                session_count = date_filtered_mis_objects.aggregate(
                    Sum('session_count'))['session_count__sum']

                session_count = return_zero_if_number_is_none(session_count)

                user_analytics_map = {
                    "label": str(temp_datetime.strftime("%d-%b-%y")),
                    "count": count,
                    "session_count": session_count,
                }

                if channel_name == 'WhatsApp':
                    business_initiated_session_count = date_filtered_mis_objects.aggregate(
                        Sum('business_initiated_session_count'))['business_initiated_session_count__sum']
                    business_initiated_session_count = return_zero_if_number_is_none(
                        business_initiated_session_count)
                    user_analytics_map["business_initiated_session_count"] = business_initiated_session_count
                
                user_analytics_list.append(user_analytics_map)

            if datetime_end.strftime("%d-%b-%y") == datetime.datetime.today().strftime("%d-%b-%y"):
                date_filtered_mis_objects = mis_objects
                total_users = date_filtered_mis_objects.values(
                    "user_id").distinct().count()

                unique_session_objects = date_filtered_mis_objects.values(
                    "session_id").distinct()

                total_sessions = unique_session_objects.count()
                user_analytics_map = {
                    "label": str((datetime_end).strftime("%d-%b-%y")),
                    "count": total_users,
                    "session_count": total_sessions,
                }

                if channel_name == 'WhatsApp':
                    total_business_initiated_sessions = unique_session_objects.filter(
                        is_business_initiated_session=True).count()
                    user_analytics_map["business_initiated_session_count"] = total_business_initiated_sessions

                user_analytics_list.append(user_analytics_map)

        elif filter_type == "2":
            no_days = (datetime_end - datetime_start).days
            no_weeks = int(no_days / 7.0) + 1
            for week in range(no_weeks):
                temp_end_datetime = datetime_end - datetime.timedelta(week * 7)
                temp_start_datetime = datetime_end - datetime.timedelta((week + 1) * 7)

                date_filtered_mis_objects = previous_mis_objects

                date_filtered_mis_objects = previous_mis_objects.filter(
                    date__gt=temp_start_datetime, date__lte=temp_end_datetime)
                total_users = date_filtered_mis_objects.aggregate(
                    Sum('count'))['count__sum']

                if total_users == None:
                    total_users = 0

                total_sessions = date_filtered_mis_objects.aggregate(
                    Sum('session_count'))['session_count__sum']

                if total_sessions == None:
                    total_sessions = 0

                temp_start_datetime_str = (temp_start_datetime + datetime.timedelta(1)).strftime(
                    "%d/%m")
                temp_end_datetime_str = (
                    temp_end_datetime).strftime("%d/%m")
                user_analytics_map = {
                    "label": temp_start_datetime_str + "-" + temp_end_datetime_str,
                    "count": total_users,
                    "session_count": total_sessions,
                }
                if channel_name == 'WhatsApp':
                    business_initiated_session_count = date_filtered_mis_objects.aggregate(
                        Sum('business_initiated_session_count'))['business_initiated_session_count__sum']
                    business_initiated_session_count = return_zero_if_number_is_none(
                        business_initiated_session_count)
                    user_analytics_map["business_initiated_session_count"] = business_initiated_session_count

                user_analytics_list.append(user_analytics_map)

            user_analytics_list = user_analytics_list[::-1]
            if datetime_end.strftime("%d-%b-%y") == datetime.datetime.today().strftime("%d-%b-%y"):
                date_filtered_mis_objects = mis_objects
                total_users = date_filtered_mis_objects.values("user_id").distinct().count()
                user_analytics_list[-1]["count"] = user_analytics_list[-1]["count"] + total_users

                unique_session_objects = date_filtered_mis_objects.values(
                    "session_id").distinct()

                total_sessions = unique_session_objects.count()
                user_analytics_list[-1]["session_count"] = user_analytics_list[-1]["session_count"] + total_sessions
                if channel_name == 'WhatsApp':
                    business_initiated_session_count = unique_session_objects.filter(
                        is_business_initiated_session=True).count()
                    user_analytics_list[-1]["business_initiated_session_count"] = user_analytics_list[-1]["business_initiated_session_count"] + business_initiated_session_count

        else:
            month_list = list(OrderedDict(((datetime_start + datetime.timedelta(_)).strftime(
                r"%b-%Y"), None) for _ in range((datetime_end - datetime_start).days + 1)).keys())
            date_filtered_mis_objects = previous_mis_objects
            for month in month_list:
                temp_month = month_to_num_dict[month.split("-")[0]]
                temp_year = int(month.split("-")[1])
                date_filtered_mis_objects = \
                    previous_mis_objects.filter(date__month=temp_month, date__year=temp_year).aggregate(
                        Sum('count'))['count__sum']

                if date_filtered_mis_objects == None:
                    date_filtered_mis_objects = 0

                total_sessions = previous_mis_objects.filter(date__month=temp_month, date__year=temp_year).aggregate(
                    Sum('session_count'))['session_count__sum']

                total_sessions = return_zero_if_number_is_none(total_sessions)

                user_analytics_map = {
                    "label": month,
                    "count": date_filtered_mis_objects,
                    "session_count": total_sessions,
                }

                if channel_name == 'WhatsApp':
                    business_initiated_session_count = previous_mis_objects.filter(date__month=temp_month, date__year=temp_year).aggregate(
                        Sum('business_initiated_session_count'))['business_initiated_session_count__sum']
                    business_initiated_session_count = return_zero_if_number_is_none(
                        business_initiated_session_count)
                    user_analytics_map["business_initiated_session_count"] = business_initiated_session_count

                user_analytics_list.append(user_analytics_map)

            if datetime_end.month == datetime.datetime.today().month:
                date_filtered_mis_objects = mis_objects
                total_users = date_filtered_mis_objects.values("user_id").distinct().count()
                user_analytics_list[-1]["count"] = user_analytics_list[-1]["count"] + total_users
                unique_session_objects = date_filtered_mis_objects.values(
                    "session_id").distinct()

                total_sessions = unique_session_objects.count()
                user_analytics_list[-1]["session_count"] = user_analytics_list[-1]["session_count"] + total_sessions
                if channel_name == 'WhatsApp':
                    business_initiated_session_count = unique_session_objects.filter(
                        is_business_initiated_session=True).count()
                    user_analytics_list[-1]["business_initiated_session_count"] = user_analytics_list[-1]["business_initiated_session_count"] + business_initiated_session_count

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Date")
        sheet1.write(0, 1, "User Count")
        if channel_name == 'WhatsApp':
            sheet1.write(0, 2, "Customer Initiated Conversation")
            sheet1.write(0, 3, "Business Initiated Conversation")
        else:
            sheet1.write(0, 2, "Unique Session Count")

        if selected_language.lower() != "all":
            language_index = 4 if channel_name == 'WhatsApp' else 3
            sheet1.write(0, language_index, "Language")
            language_text = get_language_text_for_excel_for_supported_languages(
                supported_languages)

        row = 1
        for message in user_analytics_list:
            sheet1.write(row, 0, message["label"])
            sheet1.write(row, 1, message["count"])
            if channel_name == 'WhatsApp':
                customer_initiated_session_count = int(message["session_count"]) - int(message["business_initiated_session_count"])
                sheet1.write(row, 2, customer_initiated_session_count)
                sheet1.write(row, 3, message["business_initiated_session_count"])
            else:
                sheet1.write(row, 2, message["session_count"])
            if selected_language.lower() != "all":
                sheet1.write(row, language_index, language_text)
            row += 1
        filename_for_mail = 'user_analytics_from_' + \
                            start_date.strftime("%d-%m-%Y") + '_to_' + \
                            end_date.strftime("%d-%m-%Y")
        filename = filename_for_mail + '.xls'

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        test_wb.save(secured_files_path + filename)

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.export_file_path = file_url
            export_request_obj.is_completed = True
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            send_mail_of_analytics(
                'User Analytics', file_url, email_id)

        return file_url

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_and_send_device_specific_analytics(start_date, end_date, channel_value, bot_pk, filter_type_particular, email_id,
                                              category_name, selected_language, supported_languages, to_be_mailed=True, export_request_obj=None):
    try:
        filter_type = str(filter_type_particular)
 
        datetime_start = start_date
        datetime_end = end_date
        channel_name = channel_value
        category_obj = None
        
        uat_bot_obj = Bot.objects.filter(
            pk=int(bot_pk), is_deleted=False).first()

        bot_objs = [uat_bot_obj]

        if category_name != "All":
            category_obj = Category.objects.filter(
                bot=uat_bot_obj, name=category_name).first()
        
        mis_objects = return_mis_objects_based_on_category_channel_language(
            datetime.datetime.now().date(), datetime.datetime.now().date(), bot_objs, channel_name, "All", selected_language, supported_languages, MISDashboard, UserSessionHealth)

        previous_mis_objects = return_mis_daily_objects_based_on_filter(
            bot_objs, channel_name, category_name, category_obj, selected_language, supported_languages, MessageAnalyticsDaily)
        
        previous_unique_mis_objects = return_unique_users_objects_based_on_filter(
            bot_objs, channel_name, selected_language, supported_languages, UniqueUsers)

        device_specific_analytics_list, total_days = get_combined_device_specific_analytics_list(
            datetime_start, datetime_end, mis_objects, previous_mis_objects, previous_unique_mis_objects, filter_type, category_name)

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Date")
        sheet1.write(0, 1, "Mobile Users")
        sheet1.write(0, 2, "Desktop Users")
        sheet1.write(0, 3, "Queries asked(Mobile)")
        sheet1.write(0, 4, "Queries asked(Desktop)")
        sheet1.write(0, 5, "Queries answered(Mobile)")
        sheet1.write(0, 6, "Queries answered(Desktop)")
        sheet1.write(0, 7, "Queries intuitive(Mobile)")
        sheet1.write(0, 8, "Queries intuitive(Desktop)")
        sheet1.write(0, 9, "Queries unanswered (Mobile)")
        sheet1.write(0, 10, "Queries unanswered (Desktop)")

        row = 1
        for message in device_specific_analytics_list:
            sheet1.write(row, 0, message["label"])
            sheet1.write(row, 1, str(message["total_users_mobile"]))
            sheet1.write(row, 2, str(message["total_users_desktop"]))
            sheet1.write(row, 3, str(message["total_messages_mobile"]))
            sheet1.write(row, 4, str(message["total_messages_desktop"]))
            sheet1.write(row, 5, str(message["total_answered_messages_mobile"]))
            sheet1.write(row, 6, str(message["total_answered_messages_desktop"]))
            sheet1.write(row, 7, str(message["total_intuitive_messages_mobile"]))
            sheet1.write(row, 8, str(message["total_intuitive_messages_desktop"]))
            sheet1.write(row, 9, str(message["total_unanswered_messages_mobile"]))
            sheet1.write(row, 10, str(message["total_unanswered_messages_desktop"]))
            row += 1

        filename_for_mail = 'device_specific_analytics_from_' + \
                            start_date.strftime("%d-%m-%Y") + '_to_' + \
                            end_date.strftime("%d-%m-%Y")
        filename = filename_for_mail + '.xls'

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        test_wb.save(secured_files_path + filename)

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.export_file_path = file_url
            export_request_obj.is_completed = True
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])
        
        if to_be_mailed:
            send_mail_of_analytics('Device Specific Analytics',
                                   file_url, email_id)
        else:
            return file_url
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
        pass


def create_and_send_combined_whatsapp_analytics(start_date, end_date, channel_value, bot_pk, filter_type_particular, email_id,
                                                to_be_mailed=True, export_request_obj=None):
    try:
        filter_type = str(filter_type_particular)

        datetime_start = start_date
        datetime_end = end_date

        bot_obj = Bot.objects.filter(
            pk=int(bot_pk), is_deleted=False).first()

        combined_catalogue_analytics_list, _ = get_combined_catalogue_analytics_list(
            datetime_start, datetime_end, bot_obj, filter_type)

        filename = 'catalogue_combined_analytics_from_' + \
            start_date.strftime("%d-%m-%Y") + '_to_' + \
            end_date.strftime("%d-%m-%Y") + '.csv'

        secured_files_path = settings.SECURE_MEDIA_ROOT + \
            'EasyChatApp/custom_analytics/' + str(bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        path = '/secured_files/EasyChatApp/custom_analytics/' + \
            str(bot_obj.pk) + '/' + filename

        export_csv_file = open(settings.BASE_DIR + path, 'w+')

        writer = csv.writer(export_csv_file)

        file_headings = ["Date", "Purchased users",
                         "Cart users", "Conversion ratio"]

        writer.writerow(file_headings)

        for catalogue_analytics in combined_catalogue_analytics_list:
            catalogue_analytics["total_conversion_ratio"] = str(
                catalogue_analytics["total_conversion_ratio"]) + "%"
            row_data = [catalogue_analytics["label"], catalogue_analytics["total_purchased_carts"],
                        catalogue_analytics["total_carts"], catalogue_analytics["total_conversion_ratio"]]
            writer.writerow(row_data)

        export_csv_file.close()

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.export_file_path = file_url
            export_request_obj.is_completed = True
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            send_mail_of_analytics('WhatsApp Catalogue Combined Analytics',
                                   file_url, email_id)
        else:
            return file_url
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error create_and_send_combined_whatsapp_analytics %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_frequent_intents_excel(start_date, end_date, reverse, bot_id, channel, email_id, category_name,
                                  selected_language, supported_languages, to_be_mailed=True, dropdown_language="en", export_request_obj=None):
    try:
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_id), is_deleted=False, is_uat=True)
        bot_objs = [uat_bot_obj]
        channel_value = channel
        intent_list = get_intent_frequency(
            bot_objs, MISDashboard, UserSessionHealth, start_date, end_date, channel_value, category_name, selected_language,
            supported_languages)
        filename_for_mail = 'most_frequent_intents_from_' + \
                            start_date.strftime("%d-%m-%Y") + '_to_' + \
                            end_date.strftime("%d-%m-%Y")

        if reverse == True:
            intent_list.reverse()
            filename_for_mail = 'least_frequent_intents_from_' + \
                                start_date.strftime("%d-%m-%Y") + '_to_' + \
                                end_date.strftime("%d-%m-%Y")

        filename = filename_for_mail + '.xls'
        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Intent Name")
        sheet1.write(0, 1, "Frequency")
        curr_col_no = 1
        if category_name != "All":
            curr_col_no = curr_col_no + 1
            sheet1.write(0, curr_col_no, "Category")

        if selected_language.lower() != "all":
            curr_col_no = curr_col_no + 1
            sheet1.write(0, curr_col_no, "Language")
            language_text = get_language_text_for_excel_for_supported_languages(
                supported_languages)

        row = 1

        translate_api_status = True
        intent_list, translate_api_status = conversion_intent_analytics_translator(
            intent_list, dropdown_language, translate_api_status)
        for message in intent_list:
            if translate_api_status:
                sheet1.write(row, 0, message["multilingual_name"])
            else:
                sheet1.write(row, 0, message["intent_name"])
            sheet1.write(row, 1, message["frequency"])
            curr_col_no = 1
            if category_name != "All":
                curr_col_no = curr_col_no + 1
                sheet1.write(row, curr_col_no, category_name)

            if selected_language.lower() != "all":
                curr_col_no = curr_col_no + 1
                sheet1.write(row, curr_col_no, language_text)
            row += 1

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        test_wb.save(secured_files_path + filename)

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.export_file_path = file_url
            export_request_obj.is_completed = True
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            if reverse == True:
                send_mail_of_analytics(
                    'Least Frequent Analytics', file_url, email_id)
            else:
                send_mail_of_analytics(
                    'Most Frequent Analytics', file_url, email_id)
        else:
            return file_url

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def return_intent_with_children_name_pk_occurences(datetime_start, datetime_end, category_name, channel_name, bot_objs,
                                                   selected_language, supported_languages, dropdown_language,
                                                   translate_api_status, search_term=""):
    from EasyChatApp.models import Bot, Intent, MISDashboard
    intent_with_children_name_pk_occurences_english = []
    intent_with_children_name_pk_occurences_multilingual = []
    try:
        if channel_name == "All" and category_name == "All":
            intents_objects_list = Intent.objects.filter(
                is_deleted=False, bots=bot_objs)
        elif category_name == "All":
            intents_objects_list = Intent.objects.filter(is_deleted=False, bots=bot_objs, channels__in=[
                Channel.objects.filter(name=channel_name)[0]])
        elif channel_name == "All":
            intents_objects_list = Intent.objects.filter(
                is_deleted=False, bots=bot_objs, category=Category.objects.get(bot=bot_objs, name=category_name))
        else:
            intents_objects_list = Intent.objects.filter(is_deleted=False, bots=bot_objs, category=Category.objects.get(
                bot=bot_objs, name=category_name), channels__in=[Channel.objects.filter(name=channel_name)[0]])

        for item in intents_objects_list:
            if item.tree.children.filter(is_deleted=False):

                previous_flow_indentified_objs = DailyFlowAnalytics.objects.filter(intent_indentifed=item, current_tree=item.tree, created_time__date__gte=datetime_start, created_time__date__lte=datetime_end)
                if channel_name != "All":
                    previous_flow_indentified_objs = previous_flow_indentified_objs.filter(channel__name=channel_name)

                intent_count = previous_flow_indentified_objs.aggregate(Sum('count'))['count__sum']
                if not intent_count:
                    intent_count = 0

                if datetime_end == datetime.datetime.today().date():
                    today_flow_identified_objs = FlowAnalytics.objects.filter(intent_indentifed=item, current_tree=item.tree, created_time__date=datetime_end)

                    if channel_name != "All":
                        today_flow_identified_objs = today_flow_identified_objs.filter(channel__name=channel_name)

                    intent_count += today_flow_identified_objs.count()

                if intent_count:
                    if translate_api_status:
                        name, translate_api_status = get_multilingual_intent_obj_name(item, dropdown_language, translate_api_status)

                        if search_term.lower() in name.lower():
                            intent_with_children_name_pk_occurences_multilingual.append((name, item.pk, intent_count))

                    if search_term.lower() in item.name.lower():
                        intent_with_children_name_pk_occurences_english.append((item.name, item.pk, intent_count))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("return_intent_with_children_name_pk_occurences  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
    if translate_api_status:
        return intent_with_children_name_pk_occurences_multilingual, translate_api_status
    else:
        return intent_with_children_name_pk_occurences_english, translate_api_status


def create_frequent_intents_wise_chartflow_excel(start_date, end_date, bot_id, channel, email_id, category_name,
                                                 selected_language, supported_languages, to_be_mailed=True,
                                                 dropdown_language="en", export_request_obj=None):
    try:
        datetime_start = start_date
        datetime_end = end_date
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_id), is_deleted=False, is_uat=True)
        translate_api_call_status = True
        intent_with_children_name_pk_occurences, translate_api_call_status = return_intent_with_children_name_pk_occurences(
            datetime_start.date(), datetime_end.date(), category_name, channel, uat_bot_obj, selected_language, supported_languages,
            dropdown_language, translate_api_call_status)
        intent_with_children_name_pk_occurences = list(
            intent_with_children_name_pk_occurences)

        filename_for_mail = 'intent_wise_chartflow_from_' + \
                            start_date.strftime("%d-%m-%Y") + '_to_' + \
                            end_date.strftime("%d-%m-%Y")

        filename = filename_for_mail + '.xls'
        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Intent Name")
        sheet1.write(0, 1, "Frequency")

        curr_col_no = 1
        if category_name != "All":
            curr_col_no = curr_col_no + 1
            sheet1.write(0, curr_col_no, "Category")

        if selected_language.lower() != "all":
            curr_col_no = curr_col_no + 1
            sheet1.write(0, curr_col_no, "Language")
            language_text = get_language_text_for_excel_for_supported_languages(
                supported_languages)

        row = 1
        for message in intent_with_children_name_pk_occurences:
            sheet1.write(row, 0, message[0])
            sheet1.write(row, 1, message[2])
            curr_col_no = 1
            if category_name != "All":
                curr_col_no = curr_col_no + 1
                sheet1.write(row, curr_col_no, category_name)
            if selected_language.lower() != "all":
                curr_col_no = curr_col_no + 1
                sheet1.write(row, curr_col_no, language_text)
            row += 1

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)
        file_path = secured_files_path + filename
        test_wb.save(secured_files_path + filename)

        joined_list = []
        index = 0
        while (start_date + datetime.timedelta(days=index)).strftime("%Y-%m-%d") <= end_date.strftime("%Y-%m-%d"):
            if os.path.isfile(settings.SECURE_MEDIA_ROOT + "EasyChatApp/Botwise-flow-dropoff/" + str(uat_bot_obj.name) + "_" + str(uat_bot_obj.pk) + "/User_dropoff_analytics_of_" + str((start_date + datetime.timedelta(days=index)).strftime("%Y-%m-%d")) + ".csv"):
                joined_list.append(str(settings.SECURE_MEDIA_ROOT + "EasyChatApp/Botwise-flow-dropoff/" + str(uat_bot_obj.name) + "_" + str(uat_bot_obj.pk) + "/User_dropoff_analytics_of_" + str((start_date + datetime.timedelta(days=index)).strftime("%Y-%m-%d")) + ".csv"))
            index += 1

        zip_filename = "Intent-wise ChartFlow " + str(start_date.strftime("%d-%m-%Y")) + " to " + str(end_date.strftime("%d-%m-%Y")) + ".zip"
        zip = ZipFile(secured_files_path + zip_filename, "w")
        zip.write(file_path, os.path.basename(file_path))
        if len(joined_list) > 0:
            df = pd.concat(map(pd.read_csv, joined_list), ignore_index=True)
            dropoff_filepath = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + "user_specific_dropoff_from_" + str(start_date.strftime("%d-%m-%Y")) + "_to_" + str((end_date - timedelta(days=1)).strftime("%d-%m-%Y")) + ".csv"
            df.sort_values([df.columns[1], df.columns[0]],
                            axis=0,
                            ascending=[True, True],
                            inplace=True)
            df.to_csv(dropoff_filepath, index=False)

            zip.write(dropoff_filepath, os.path.basename(dropoff_filepath))

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + zip_filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.export_file_path = file_url
            export_request_obj.is_completed = True
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            send_mail_of_analytics('Intent wise chartflow',
                                   file_url, email_id)
        else:
            return file_url
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_category_excel(start_date, end_date, bot_id, channel, email_id, category_name, selected_language,
                          supported_languages, to_be_mailed=True, dropdown_language="en", export_request_obj=None):
    try:
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_id), is_deleted=False, is_uat=True)
        bot_objs = [uat_bot_obj]
        channel_name = channel

        if channel == 'All' and category_name == 'All':
            mis_objects = MISDashboard.objects.filter(bot__in=bot_objs, creation_date__gte=start_date,
                                                      creation_date__lte=end_date).exclude(
                intent_name="INFLOW-INTENT").exclude(intent_name=None)
        elif category_name == 'All':
            mis_objects = MISDashboard.objects.filter(bot__in=bot_objs, creation_date__gte=start_date,
                                                      creation_date__lte=end_date, channel_name=channel_name).exclude(
                intent_name="INFLOW-INTENT").exclude(intent_name=None)
        elif channel == 'All':
            mis_objects = MISDashboard.objects.filter(bot__in=bot_objs, creation_date__gte=start_date,
                                                      creation_date__lte=end_date,
                                                      category__name=category_name).exclude(
                intent_name="INFLOW-INTENT").exclude(intent_name=None)
        else:
            mis_objects = MISDashboard.objects.filter(bot__in=bot_objs, creation_date__gte=start_date,
                                                      creation_date__lte=end_date, channel_name=channel_name,
                                                      category__name=category_name).exclude(
                intent_name="INFLOW-INTENT").exclude(intent_name=None)

        if selected_language.lower() != "all":
            mis_objects = mis_objects.filter(
                selected_language__in=supported_languages)

        mis_objects = mis_objects.exclude(intent_recognized=None)

        intent_frequency = list(mis_objects.filter(small_talk_intent=False).values(
            "intent_name", "category__name", "intent_recognized").order_by("intent_name").annotate(
            frequency=Count("intent_name")).order_by(
            '-frequency'))

        filename_for_mail = 'most_frequent_intents_category_wise_from_' + \
                            start_date.strftime("%d-%m-%Y") + '_to_' + \
                            end_date.strftime("%d-%m-%Y")

        filename = filename_for_mail + '.xls'

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Intent Name")
        sheet1.write(0, 1, "Category Name")
        sheet1.write(0, 2, "Frequency")
        curr_col_no = 2
        if selected_language.lower() != "all":
            curr_col_no = curr_col_no + 1
            sheet1.write(0, curr_col_no, "Language")
            language_text = get_language_text_for_excel_for_supported_languages(
                supported_languages)

        row = 1
        translate_api_status = True
        intent_frequency, translate_api_status = conversion_intent_analytics_translator(
            intent_frequency, dropdown_language, translate_api_status)

        for message in intent_frequency:
            if translate_api_status:
                sheet1.write(row, 0, message["multilingual_name"])
            else:
                sheet1.write(row, 0, message["intent_name"])
            sheet1.write(row, 1, message["category__name"])
            sheet1.write(row, 2, message["frequency"])
            curr_col_no = 2
            if selected_language.lower() != "all":
                curr_col_no = curr_col_no + 1
                sheet1.write(row, curr_col_no, language_text)
            row += 1

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        test_wb.save(secured_files_path + filename)

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.export_file_path = file_url
            export_request_obj.is_completed = True
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            send_mail_of_analytics(
                'Most Frequent Intent Category Wise', file_url, email_id)
        else:
            return file_url
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_hour_wise_excel(start_date, end_date, bot_id, channel, email_id, category_name, selected_language,
                           supported_languages, interval_type="1", time_format="1", to_be_mailed=True, dropdown_language="en", export_request_obj=None):
    try:
        from EasyChatApp.utils_api_analytics import get_combined_hour_wise_analytics
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_id), is_deleted=False, is_uat=True)
        bot_objs = [uat_bot_obj]

        try:
            date_format = "%Y-%m-%d"
            start_date = datetime.datetime.strptime(
                start_date, date_format).date()
            end_date = datetime.datetime.strptime(end_date, date_format).date()  # noqa: F841
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("startdate and enddate is not in valid format %s at line no %s", str(e), str(exc_tb.tb_lineno), extra={
                         'AppName': 'EasyChat', 'user_id': str(email_id), 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})
            pass

        filename_for_mail = 'Hour_wise_analytics_' + \
                            start_date.strftime("%d-%m-%Y") + '_to_' + \
                            end_date.strftime("%d-%m-%Y")

        filename = filename_for_mail + '.xls'

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Date")
        sheet1.write(0, 1, "Time Interval")
        sheet1.write(0, 2, "No. of Users")
        sheet1.write(0, 3, "No. of Messages")
        row = 1

        if (time_format == "1"):
            time_list = ['12:00am - 01:00am', '01:00am - 02:00am', '02:00am - 03:00am', '03:00am - 04:00am', '04:00am - 05:00am', '05:00am - 06:00am', '06:00am - 07:00am', '07:00am - 08:00am', '08:00am - 09:00am', '09:00am - 10:00am', '10:00am - 11:00am', '11:00am - 12:00pm',
                         '12:00pm - 01:00pm', '01:00pm - 02:00pm', '02:00pm - 03:00pm', '03:00pm - 04:00pm', '04:00pm - 05:00pm', '05:00pm - 06:00pm', '06:00pm - 07:00pm', '07:00pm - 08:00pm', '08:00pm - 09:00pm', '09:00pm - 10:00pm', '10:00pm - 11:00pm', '11:00pm - 12:00am']
            if (interval_type == "2"):
                time_list = ['12:00am - 03:00am', '03:00am - 06:00am', '06:00am - 09:00am', '09:00am - 12:00pm',
                             '12:00pm - 03:00pm', '03:00pm - 06:00pm', '06:00pm - 09:00pm', '09:00pm - 12:00am']
            elif (interval_type == "3"):
                time_list = ['12:00am - 06:00am', '06:00am - 12:00pm',
                             '12:00pm - 06:00pm', '06:00pm - 12:00am']
        else:
            time_list = ['00:00hr - 01:00hr', '01:00hr - 02:00hr', '02:00hr - 03:00hr', '03:00hr - 04:00hr', '04:00hr - 05:00hr', '05:00hr - 06:00hr', '06:00hr - 07:00hr', '07:00hr - 08:00hr', '08:00hr - 09:00hr', '09:00hr - 10:00hr', '10:00hr - 11:00hr', '11:00hr - 12:00hr',
                         '12:00hr - 13:00hr', '13:00hr - 13:00hr', '14:00hr - 15:00hr', '15:00hr - 16:00hr', '16:00hr - 17:00hr', '17:00hr - 18:00hr', '18:00hr - 19:00hr', '19:00hr - 20:00hr', '20:00hr - 21:00hr', '21:00hr - 22:00hr', '22:00hr - 23:00hr', '23:00hr - 24:00hr']
            if (interval_type == "2"):
                time_list = ['00:00hr - 03:00hr', '03:00hr - 06:00hr', '06:00hr - 09:00hr', '09:00hr - 12:00hr',
                             '12:00hr - 15:00hr', '15:00hr - 18:00hr', '18:00hr - 21:00hr', '21:00hr - 24:00hr']
            elif (interval_type == "3"):
                time_list = ['00:00hr - 06:00hr', '06:00hr - 12:00hr',
                             '12:00hr - 18:00hr', '18:00hr - 24:00hr']

        current_date = start_date
        while current_date <= end_date:
            response, status, message = get_combined_hour_wise_analytics(
                {}, bot_objs, current_date, current_date, channel, category_name, selected_language, supported_languages, interval_type, time_format)

            hour_wise_analytics_list = response["hour_wise_analytics_list"]
            total_number_of_messages = hour_wise_analytics_list[0]["total_message_count"]
            total_number_of_users = hour_wise_analytics_list[0]["total_users_count"]

            for number in range(len(total_number_of_messages)):
                sheet1.write(row, 0, current_date.strftime("%d-%m-%Y"))
                sheet1.write(row, 1, time_list[number])
                sheet1.write(row, 2, total_number_of_users[number])
                sheet1.write(row, 3, total_number_of_messages[number])
                row += 1

            current_date += datetime.timedelta(days=1)
            row += 1

        secured_files_path = settings.SECURE_MEDIA_ROOT + \
            'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        test_wb.save(secured_files_path + filename)

        path = '/secured_files/EasyChatApp/custom_analytics/' + \
            str(uat_bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.export_file_path = file_url
            export_request_obj.is_completed = True
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            send_mail_of_analytics(
                'Hour-wise Analytics', file_url, email_id)
        else:
            return file_url
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={
                     'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_unanswered_query_excel(start_date, end_date, bot_id, channel, email_id, selected_language,
                                  supported_languages, to_be_mailed=True, export_request_obj=None):
    try:
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_id), is_deleted=False, is_uat=True)
        bot_objs = [uat_bot_obj]
        channel_value = channel

        if channel_value == 'All':
            unanswered_queries = UnAnsweredQueries.objects.filter(
                bot=bot_objs[0], date__gte=start_date, date__lte=end_date).order_by('-count')
        else:
            unanswered_queries = UnAnsweredQueries.objects.filter(
                channel=Channel.objects.get(name=channel_value), bot=bot_objs[0], date__gte=start_date,
                date__lte=end_date).order_by('-count')

        if selected_language.lower() != "all":
            unanswered_queries = unanswered_queries.filter(
                selected_language__in=supported_languages)

        unanswered_queries = unanswered_queries.exclude(unanswered_message="")

        unanswered_top_hundred_count_tuple = unanswered_queries.values_list("unanswered_message").annotate(total=Sum("count")).order_by("-total")

        filename_for_mail = 'top_unanswered_queries_from_' + \
                            start_date.strftime("%d-%m-%Y") + '_to_' + \
                            end_date.strftime("%d-%m-%Y")

        filename = filename_for_mail + '.xls'

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        sheet1.write(0, 0, "Unanswered Query")
        sheet1.write(0, 1, "Frequency")
        curr_col_no = 1
        if selected_language.lower() != "all":
            curr_col_no = curr_col_no + 1
            sheet1.write(0, curr_col_no, "Language")
            language_text = get_language_text_for_excel_for_supported_languages(
                supported_languages)

        row = 1
        for key, value in unanswered_top_hundred_count_tuple:
            sheet1.write(row, 0, key)
            sheet1.write(row, 1, value)
            curr_col_no = 1
            if selected_language.lower() != "all":
                curr_col_no = curr_col_no + 1
                sheet1.write(row, curr_col_no, language_text)
            row += 1

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        test_wb.save(secured_files_path + filename)

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.export_file_path = file_url
            export_request_obj.is_completed = True
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            send_mail_of_analytics(
                'Top Unanswered Queries', file_url, email_id)
        else:
            return file_url
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_intuitive_query_excel(start_date, end_date, bot_id, channel, email_id, selected_language,
                                 supported_languages, to_be_mailed=True, dropdown_language="en", export_request_obj=None):
    try:
        uat_bot_obj = Bot.objects.get(
            pk=int(bot_id), is_deleted=False, is_uat=True)
        bot_objs = [uat_bot_obj]
        channel_value = channel
        if channel_value == 'All':
            intuitive_queries = IntuitiveQuestions.objects.filter(
                bot=bot_objs[0], date__gte=start_date, date__lte=end_date).order_by('-date')
        else:
            intuitive_queries = IntuitiveQuestions.objects.filter(
                channel=Channel.objects.get(name=channel_value), bot=bot_objs[0], date__gte=start_date,
                date__lte=end_date).order_by('-date')

        if selected_language.lower() != "all":
            intuitive_queries = intuitive_queries.filter(
                selected_language__in=supported_languages)

        filename_for_mail = 'intuitive_questions_from_' + \
                            start_date.strftime("%d-%m-%Y") + '_to_' + \
                            end_date.strftime("%d-%m-%Y")

        filename = filename_for_mail + '.xls'

        test_wb = Workbook()

        sheet1 = test_wb.add_sheet("Sheet1")

        add_intuitive_queries_to_sheet(
            intuitive_queries, sheet1, selected_language, supported_languages, dropdown_language)

        secured_files_path = settings.SECURE_MEDIA_ROOT + 'EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/'
        if not os.path.exists(secured_files_path):
            os.makedirs(secured_files_path)

        test_wb.save(secured_files_path + filename)

        path = '/secured_files/EasyChatApp/custom_analytics/' + str(uat_bot_obj.pk) + '/' + filename

        file_access_management_obj = EasyChatAppFileAccessManagement.objects.create(
            file_path=path, is_analytics_file=True, bot=uat_bot_obj)

        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
            str(file_access_management_obj.key) + '/'

        if export_request_obj:
            export_request_obj.export_file_path = file_url
            export_request_obj.is_completed = True
            export_request_obj.save(update_fields=['is_completed', 'export_file_path'])

        if to_be_mailed:
            send_mail_of_analytics('Intuitive Queries',
                                   file_url, email_id)
        else:
            return file_url
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report intuitive export %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def add_intuitive_queries_to_sheet(intuitive_queries, sheet1, selected_language="All", supported_languages=[], dropdown_language="en"):
    try:
        sheet1.write(0, 0, "Date")
        sheet1.write(0, 1, "User Query")
        sheet1.write(0, 2, "Frequency")
        sheet1.write(0, 3, "Intuitive Queries")
        sheet1.write(0, 4, "Channel Name")

        if selected_language.lower() != "all":
            sheet1.write(0, 5, "Language")
            language_text = get_language_text_for_excel_for_supported_languages(
                supported_languages)
        row = 1
        translate_api_status = True
        for intuitive_query in intuitive_queries:
            string_intents = ""
            for intent in intuitive_query.suggested_intents.all():
                intent_name, translate_api_status = get_multilingual_intent_obj_name(intent, dropdown_language, translate_api_status)
                string_intents = string_intents + intent_name + ", "
            string_intents = string_intents.strip()
            length = len(string_intents) - 1
            string_intents = string_intents[0:length]
            sheet1.write(row, 0, intuitive_query.date.strftime(("%d-%m-%Y")))
            intuitive_message_query, translate_api_status = get_translated_text_with_api_status(intuitive_query.intuitive_message_query, dropdown_language, EasyChatTranslationCache, translate_api_status)
            sheet1.write(row, 1, intuitive_message_query)
            sheet1.write(row, 2, intuitive_query.count)
            sheet1.write(row, 3, string_intents)
            sheet1.write(row, 4, intuitive_query.channel)
            if selected_language.lower() != "all":
                sheet1.write(row, 5, language_text)
            row += 1

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("add_intuitive_queries_to_sheet %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def send_form_data_csv(form_widget_pk, bot_obj, FormWidgetDataCollection, Bot, email_id):
    try:
        form_data_object = FormWidgetDataCollection.objects.filter(
            pk=form_widget_pk, bot=bot_obj).first()
        if not os.path.exists(settings.MEDIA_ROOT + 'form_data_folder'):
            os.makedirs(settings.MEDIA_ROOT + 'form_data_folder')
        fieldnames = ["UserId", "Timestamp"]

        for key, value in json.loads(form_data_object.form_data.replace("'", '"')).items():
            fieldnames.append(key)
        formated_date = form_data_object.date.strftime("%d-%m-%Y")

        with open('files/form_data_folder/' + form_data_object.form_name + '_' + str(form_data_object.pk) + '_' + formated_date + '.csv',
                  mode='w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(fieldnames)

            csv_dict = []
            csv_dict.append(form_data_object.user_id.user_id)
            csv_dict.append(form_data_object.get_datetime())
            for key, value in json.loads(form_data_object.form_data.replace("'", '"')).items():
                if (isinstance(value, list)):
                    if value[0] == 'file_attach':
                        value = settings.EASYCHAT_HOST_URL + value[1]
                    else:
                        value = value[1]
                csv_dict.append(value)
            writer.writerow(csv_dict)

        form_file = form_data_object.form_name + '_' + str(form_data_object.pk) + '_' + formated_date + '.csv'
        # filename = "files/form_data_folder/" + form_file
        access_file_path = 'form_data_folder/' + form_file
        body = """<head>
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
                <a href="{}/{}">click here</a>
                <p>&nbsp;</p>"""

        config = get_developer_console_settings()

        body += config.custom_report_template_signature

        body += """</div></body>"""

        domain = settings.EASYCHAT_HOST_URL
        body = body.format("data of the forms filled by users", domain,
                           "files/" + access_file_path)

        send_email_to_customer_via_awsses(
            email_id, "Data of the forms filled by users", body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error in today report  %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_image_thumbnail(filename):
    thumbnail_file_name = ""

    try:
        original_file = Image.open('secured_files/EasyChatApp/attachment/' + filename)
        original_file.thumbnail((80, 80))
        thumbnail_file_name = filename.split('.')[0] + '_thumbnail.' + filename.split('.')[1]
        original_file.save('secured_files/EasyChatApp/attachment/' + thumbnail_file_name)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_image_thumbnail: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})

    return thumbnail_file_name


def create_video_thumbnail(filename):
    thumbnail_file_name = ""

    try:
        clip = VideoFileClip(settings.SECURE_MEDIA_ROOT +
                             'EasyChatApp/attachment/' + filename)
        duration = clip.duration
        frame_at_second = min(5, duration)
        frame = clip.get_frame(frame_at_second)
        thumbnail = Image.fromarray(frame)

        thumbnail_file_name = filename.split('.')[0] + '_thumbnail.png'

        thumbnail.save(
            'secured_files/EasyChatApp/attachment/' + thumbnail_file_name)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_video_thumbnail: %s at %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
    return thumbnail_file_name


def build_suggestions_and_word_mapper(bot_id, Bot, WordMapper, Channel, Intent, ChunksOfSuggestions):
    try:
        import datetime
        bot_obj = Bot.objects.get(pk=bot_id, is_deleted=False, is_uat=True)

        word_mapper_list = []
        word_mapper_objs = WordMapper.objects.filter(bots__in=[bot_obj])
        for word_mapper in word_mapper_objs:
            word_mapper_list.append({
                "keyword": word_mapper.keyword,
                "similar_words": word_mapper.get_similar_word_list()
            })
        channel_obj = Channel.objects.get(name='Web')
        intent_objs = Intent.objects.filter(bots__in=[bot_obj], is_part_of_suggestion_list=True, is_deleted=False,
                                            is_form_assist_enabled=False, is_hidden=False,
                                            channels__in=[channel_obj]).distinct()
        sentence_list = []
        for intent_obj in intent_objs:
            training_data_dict = json.loads(intent_obj.training_data)
            intent_name = intent_obj.name
            intent_click_count = intent_obj.intent_click_count

            sentence_list.append({
                "key": intent_name,
                "value": intent_name,
                "count": intent_click_count,
                "pk": intent_obj.pk
            })

            for key in training_data_dict:
                training_sentence_lower_str = training_data_dict[key].lower()
                if training_sentence_lower_str not in sentence_list:
                    sentence_list.append({
                        "key": training_sentence_lower_str,
                        "value": intent_name,
                        "count": intent_click_count,
                        "pk": intent_obj.pk
                    })
        for iterator in range(0, len(sentence_list), CHUNK_OF_SUGGESTION_LIMIT):
            ChunksOfSuggestions.objects.create(bot=bot_obj, suggestion_list=json.dumps(sentence_list[iterator:iterator + CHUNK_OF_SUGGESTION_LIMIT]))

        bot_obj.suggestion_list = json.dumps(sentence_list)
        bot_obj.word_mapper_list = json.dumps(word_mapper_list)
        bot_obj.last_bot_updated_datetime = datetime.datetime.now()
        bot_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("build_suggestions_and_word_mapper: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def send_reset_password_mail(email_id, reset_pass_url, user_fullname):
    config = get_developer_console_settings()

    SECONDARY_COLOR = config.secondary_color

    body = '<table><tr style="background:white"><td  style="font-style: normal;font-weight: 500;font-size: 15px;line-height: 35px;letter-spacing: 0.025em;color: #4D4D4D;"><p>Dear ' + user_fullname + \
           ',</p><p>We have recieved a request to reset your password of EasyChat account for your email address.<p>Username: ' + \
           email_id + '</p><p>Please click on the button below to reset a new password</p></td></tr></table>'

    body += '<a href=' + reset_pass_url + ' style="height: 41px;width: 259px;left: 633px;top: 552px;border-radius: 30px;background: #' + SECONDARY_COLOR + \
        ';border-radius: 30px;color: white;text-decoration: none;font-family: Silka;font-style: normal;font-weight: bold;font-size: 14px;line-height: 17px;letter-spacing: 0.025em;color: #FFFFFF;padding: 10px;" target="_blank">Reset Password</a>'

    EMAIL_HEAD = get_email_head_from_email_html_constant()

    body = str(EMAIL_HEAD + body)

    subject = "EasyChat Password Reset"

    body += """</div></body>"""

    body += config.custom_report_template_signature

    send_email_to_customer_via_awsses(email_id, subject, body)


def check_if_reset_password_object_is_expired(reset_pass_obj):
    try:

        config = get_developer_console_settings()

        time_difference = (timezone.now() - reset_pass_obj.last_request_datetime).total_seconds()

        if time_difference > config.reset_password_details_expire_after * 60:
            return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_if_reset_password_object_is_expired: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
    return False


def send_forgot_password_otp_mail(email_id, user_fullname, otp):
    config = get_developer_console_settings()

    body = '<table><tr style="background:white"><td  style="font-style: normal;font-weight: 500;font-size: 15px;line-height: 35px;letter-spacing: 0.025em;color: #4D4D4D;"><p>Dear ' + user_fullname + \
           ',</p><p>We have received a request to reset EasyChat account for your email address.' + \
           '</p><p>Your OTP is {} which is valid for {} mins</p></td></tr></table>'.format(
               otp, config.reset_password_details_expire_after)

    EMAIL_HEAD = get_email_head_from_email_html_constant()

    body = str(EMAIL_HEAD + body)

    subject = "EasyChat Password Reset OTP"

    body += """</div></body>"""

    body += config.custom_report_template_signature

    send_email_to_customer_via_awsses(email_id, subject, body)


def send_login_otp_mail(email_id, user_fullname, otp):
    try:
        config = get_developer_console_settings()

        reciever_name = ""
        user_fullname = user_fullname.strip()
        if(user_fullname != "" or user_fullname):
            reciever_name = user_fullname
        else:
            reciever_name = email_id

        body = '<table>\
            <tr style="background:white">\
                <td  style="font-style: normal;font-weight: 500;font-size: 15px;line-height: 35px;letter-spacing: 0.025em;color: #4D4D4D;">\
                    <p style="font-size: 16px;line-height: 20px;color: #4D4D4D;">Dear ' + reciever_name + ',</p>\
                    <p style="font-size: 14px;line-height: 14px; color: #4D4D4D;">We have received a request to reset Password for your EasyChat account.</p>\
                    <p style="font-size: 14px;color: #7B7A7B;">Your OTP for login is \
                        <span style="font-size: 18px;color: #000000">' + str(otp) + '</span> \
                    which is valid for ' + str(config.authentication_otp_expire_after) + ' minutes.</p>\
                    <div style="color: #2D2D2D;font-size: 14px;line-height: 18px;">' + str(config.custom_report_template_signature) + '</div>\
                </td>\
            </tr>\
        </table>'

        EMAIL_HEAD = get_email_head_from_email_html_constant()

        body = str(EMAIL_HEAD + body)

        subject = "Verify your Login"

        body += """</body>"""

        send_email_to_customer_via_awsses(email_id, subject, body)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("error send_login_otp_mail! %s %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def send_otp_mail(email_ids, subject, content):
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
            """ + str(content) + """
        </p>
        <p>&nbsp;</p>"""

    config = get_developer_console_settings()

    body += config.custom_report_template_signature

    body += """</div></body>"""

    for email_id in email_ids:
        send_email_to_customer_via_awsses(email_id, subject, body)


################################## TMS functions Start####################


def create_an_issue_tms(customer_email_id, user_id, full_name, issue, bot_id, attached_file_path, channel_name,
                        category_name, other_informations):
    try:
        from EasyTMSApp.models import TicketCategory, Ticket, Agent, LeaveCalendar, WorkingCalendar, TicketPriority, \
            TicketStatus, TMSAccessToken, UserNotification
        from EasyChatApp.models import Channel, Bot
        from EasyTMSApp.utils import get_access_token_from_bot, send_notification_to_agent, send_action_info_to_agent, \
            get_agent_name, get_relevant_agent_list, create_user_notification
        name = str(full_name)
        phone_no = str(user_id)
        email = customer_email_id
        ticket_obj = ""
        priority = ""
        category_name = str(category_name).strip()
        category_obj = []
        bot_obj = []
        try:
            access_token_obj = get_access_token_from_bot(
                bot_id, Bot, Agent, TMSAccessToken)
            priority = TicketPriority.objects.get(
                name="LOW", access_token=access_token_obj)
            ticket_status_pending = TicketStatus.objects.get(
                name="PENDING", access_token=access_token_obj)
            ticket_status_unassigned = TicketStatus.objects.get(
                name="UNASSIGNED", access_token=access_token_obj)
            if attached_file_path == None or attached_file_path == "None":
                attached_file_path = ""
            channel = Channel.objects.filter(name=str(channel_name))
            if channel:
                channel = channel[0]
            else:
                channel = None
            try:
                bot_obj = Bot.objects.get(pk=int(bot_id))
                category_obj = TicketCategory.objects.filter(
                    bot=bot_obj, ticket_category=category_name)
                if category_obj.exists():
                    category_obj = category_obj[0]
                else:
                    category_obj = TicketCategory.objects.filter(
                        bot=bot_obj, ticket_category="OTHERS").first()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("Category and Bot not present %s at %s",
                             str(e), str(exc_tb.tb_lineno),
                             extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None',
                                    'bot_id': 'none'})
                pass

            try:
                selected_agent_obj = auto_assign_agent(
                    category_obj, bot_obj, access_token_obj, Agent, Bot, Ticket)
                if (selected_agent_obj != None):
                    ticket_obj = Ticket.objects.create(ticket_status=ticket_status_pending,
                                                       ticket_priority=priority,
                                                       ticket_category=category_obj,
                                                       bot=bot_obj,
                                                       agent=selected_agent_obj,
                                                       customer_name=name,
                                                       bot_channel=channel,
                                                       customer_email_id=email,
                                                       customer_mobile_number=phone_no,
                                                       query_description=issue,
                                                       query_attachment=attached_file_path,
                                                       access_token=access_token_obj,
                                                       )

                    description = "A new ticket is generated and assigned to " + \
                                  selected_agent_obj.user.username
                    # send_notification_to_agent(
                    #     agent_obj, notification_message=notification_message)
                    # send_action_info_to_agent(
                    # agent_obj, action_name="update_ticket_data",
                    # action_info={})

                    agent_objs = get_relevant_agent_list(ticket_obj, Agent)

                    for agent_obj in agent_objs:

                        if agent_obj != selected_agent_obj:
                            create_user_notification(
                                agent_obj, ticket_obj, description, UserNotification)
                            send_action_info_to_agent(agent_obj, action_name="new_ticket_assigned", action_info={
                                "send_notification": True,
                                "notification_message": description,
                                "ticket_id": ticket_obj.ticket_id
                            })
                        elif agent_obj == selected_agent_obj:
                            create_user_notification(
                                agent_obj, ticket_obj, description, UserNotification)
                            notification_message = "Hi, " + \
                                                   get_agent_name(
                                                       agent_obj) + "! A new ticket is assigned to you on Cogno desk."
                            send_action_info_to_agent(agent_obj, action_name="new_ticket_assigned", action_info={
                                "send_notification": True,
                                "notification_message": notification_message,
                                "ticket_id": ticket_obj.ticket_id
                            })
                else:
                    ticket_obj = Ticket.objects.create(ticket_status=ticket_status_unassigned,
                                                       ticket_priority=priority,
                                                       ticket_category=category_obj,
                                                       bot=bot_obj,
                                                       customer_name=name,
                                                       bot_channel=channel,
                                                       customer_email_id=email,
                                                       customer_mobile_number=phone_no,
                                                       query_description=issue,
                                                       query_attachment=attached_file_path,
                                                       access_token=access_token_obj
                                                       )

                    admin_agent = access_token_obj.agent
                    description = "A new ticket is generated."

                    create_user_notification(
                        admin_agent, ticket_obj, description, UserNotification)
                    send_action_info_to_agent(admin_agent, action_name="new_ticket_assigned", action_info={
                        "send_notification": True,
                        "notification_message": description,
                        "ticket_id": ticket_obj.ticket_id
                    })
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                logger.error("create issue: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("create issue: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})

        calendar_obj = LeaveCalendar.objects.filter(
            leave_date_time=date.today())
        if calendar_obj:
            response["status_code"] = 305
        else:
            date_time = timezone.now()
            current_date = date_time.strftime("%Y-%m-%d")
            working_obj = WorkingCalendar.objects.filter(date=current_date)
            current_time = timezone.now().time()
            if working_obj:
                if working_obj[0].start_time < current_time and working_obj[0].end_time > current_time:
                    response["status_code"] = 200
                else:
                    response["status_code"] = 305
            else:
                response["status_code"] = 200

        response["status_message"] = "SUCCESS"
        response["ticket_id"] = str(ticket_obj.ticket_id)
        return response

    except Exception as e:
        logger.error("create issue: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
        response["status_code"] = 500
        response["ticket_id"] = ""

    return response


def check_tms_ticket_status(ticket_id):
    from EasyTMSApp.models import TicketCategory, Ticket, Agent, LeaveCalendar, WorkingCalendar, TicketPriority, \
        TicketStatus, AgentQuery
    from EasyChatApp.models import Channel, Bot
    ticket_status_message = ""
    try:
        ticket_obj = Ticket.objects.get(ticket_id=ticket_id)
        user = ticket_obj.customer_name

        if ticket_obj.ticket_status.name == "REJECTED":
            ticket_status_message = "Hi, " + user + "! your ticket has been declined. Kindly connect with our customer agent in case of issue."
        elif (ticket_obj.ticket_status.name == "UNASSIGNED"):
            ticket_status_message = "Hi, " + user + "! currently no agent is assigned to your issue."
        elif (ticket_obj.ticket_status.name == "RESOLVED"):
            ticket_status_message = "Hi, " + user + "! your issue has been resolved."
        else:
            ticket_status_message = "Hi, " + user + "! The status of your ticket Id " + ticket_id + " is " + ticket_obj.ticket_status.name + "."

        agent_query_obj = AgentQuery.objects.filter(
            ticket=ticket_obj, is_active=True).first()
        if agent_query_obj and agent_query_obj.ticket_audit_trail:
            ticket_status_message = ticket_status_message + "$$$" + agent_query_obj.ticket_audit_trail.description + "$$$" + "Please enter your reply."
            # response["agent_issue_exist"] = True
            response["agent_issue_id"] = agent_query_obj.pk
        else:
            ticket_status_message = ticket_status_message + "$$$" + "If you have any issues regarding this you can reply here."
            # response["agent_issue_exist"] = False
            response["agent_issue_id"] = None

        response["ticket_exist"] = True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check whatsapp ticket status: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
        response["ticket_exist"] = False
        ticket_status_message = "Sorry, no such ticket found. Please check your Ticket ID and try again."

    response["status_code"] = 200
    response["status_message"] = "SUCCESS"
    response["ticket_status_message_response"] = str(ticket_status_message)
    return response


def check_tms_ticket_exists(ticket_id):
    from EasyTMSApp.models import Ticket

    try:
        ticket_obj = Ticket.objects.filter(ticket_id=ticket_id)

        if ticket_obj:
            return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_tms_ticket_exists: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
        return False
    return False


def check_for_tms_intent_and_create_categories(intent_pk, dropdown_choices, TicketCategory):
    response = {}

    try:
        intent_obj = Intent.objects.get(pk=intent_pk)
        if intent_obj.is_easy_tms_allowed:
            create_tms_categories(
                dropdown_choices, intent_obj.bots.all()[0], TicketCategory)
            response['message'] = "Categories Created"
            return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_for_tms_intent_and_create_categories: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})

    response['message'] = "not a tms intent"
    return response


def create_tms_categories(dropdown_choices, bot_obj, TicketCategory, to_update_intent=False):
    try:
        for category in dropdown_choices:
            ticket_obj = TicketCategory.objects.filter(
                bot=bot_obj, ticket_category__iexact=category.strip(), is_deleted=False)
            if ticket_obj.exists() and ticket_obj[0].is_deleted == False:
                continue
            else:
                if ticket_obj.exists():
                    ticket_obj = ticket_obj[0]
                    ticket_obj.is_deleted = False
                    ticket_obj.ticket_category = category
                    ticket_obj.save()
                else:
                    TicketCategory.objects.create(
                        bot=bot_obj, ticket_category=category)
        # marking is deleted true of the objects which are not in the list
        category_objs = TicketCategory.objects.filter(
            bot=bot_obj, is_deleted=False).exclude(ticket_category__in=dropdown_choices)
        for category in category_objs:
            category.is_deleted = True
            category.save()

        if to_update_intent:
            update_dropdown_choices_of_tms_intent(bot_obj, TicketCategory)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_tms_categories: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})


def create_default_csat_flow(bot_id):
    try:
        bot_obj = Bot.objects.get(pk=int(bot_id))
        category = Category.objects.get(name="Others", bot=bot_obj)
        modes = ""
        other_params = {
            "is_easy_tms_allowed": False,
            "is_whatsapp_csat": True,
        }
        is_hidden = False
        name = "Channel feedback flow for bot"
        response = "Please take a second to tell us about your experience with <strong><span translate='no'>{/bot_name/}</span></strong>. Select anyone from the below options"
        variations = [name]
        counter = 0
        data = {}
        for variation in variations:
            data[counter] = variation
            counter = counter + 1
        channel_objs = Channel.objects.filter(name__in=["WhatsApp", "Viber"])

        intent_objs = Intent.objects.filter(
            bots__in=[bot_obj], is_whatsapp_csat=True)
        if intent_objs.count() > 0:
            return

        intent_obj = create_intent_obj(
            name, response, bot_obj, data, channel_objs, category, modes, other_params, is_hidden)
        top_tree_obj = intent_obj.tree
        child_tree = create_and_add_api_tree(
            top_tree_obj, "GetCSATRatingFromUser", CSAT_GET_RATING_PYTHON_CODE_API_TREE, ApiTree)

        child_tree = create_and_add_post_proccessor(
            top_tree_obj, "GetCSATFormChoiceFromUser", CSAT_GET_FORM_CHOICE_POST_PROCESSOR, Processor)

        child_response = "Thankyou for your valuable feedback."
        child_tree = create_and_add_child_with_api_tree(
            top_tree_obj, "Positive Feedback", child_response, "SavePositiveFeedbackAPI",
            CSAT_SAVE_FEEDBACK_WITHOUT_DETAILS_API_TREE, ApiTree, Tree)

        child_response = "Can you help us understand what went wrong?"
        child_tree = create_and_add_child_with_post_proccesor(
            top_tree_obj, "Text Feedback Submit", child_response, "TakeFeedbackTextResponse",
            CSAT_SAVE_FEEDBACK_WITHOUT_DETAILS_POST_PROCESSOR, Processor, Tree)
        child_tree.post_processor.is_original_message_required = True
        child_tree.post_processor.save()

        child_response = "Thankyou for your valuable feedback."
        child_tree = create_and_add_child_with_api_tree(
            child_tree, "Save Final Feedback", child_response, "SaveFinalFeedbackAPI",
            CSAT_SAVE_FEEDBACK_WITHOUT_DETAILS_API_TREE, ApiTree, Tree)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_default_csat_flow: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': str(bot_id)})


def set_tms_bot_admin(user_obj, Agent, bot_obj, TicketCategory):
    agent_obj = Agent.objects.get(user=user_obj)
    agent_obj.bots.add(bot_obj)
    agent_obj.save()

    category_objs = TicketCategory.objects.filter(
        is_deleted=False, bot=bot_obj)
    for category_obj in category_objs:
        agent_obj.ticket_categories.add(category_obj)
    agent_obj.save()


def update_dropdown_choices_of_tms_intent(bot_obj, TicketCategory):
    response = {}
    response['status'] = 500
    try:
        intent_objs = Intent.objects.filter(
            bots__in=[bot_obj], is_easy_tms_allowed=True, is_hidden=False)
        choice_list = TicketCategory.objects.filter(
            bot=bot_obj, is_deleted=False).values_list('ticket_category')
        drop_down_choices_list = [item[0]
                                  for item in choice_list]
        if intent_objs.exists():
            # thier are only 2 intents for a single bot so this loop wont
            # affect much
            for intent_obj in intent_objs:
                tree_obj = intent_obj.tree
                # finding the Tree in which tms cat is enabled so that we can
                # update the categories in drop down choices of
                # bot_response_object
                while tree_obj.children.exists():
                    bot_response_obj = tree_obj.response
                    modes = json.loads(bot_response_obj.modes)
                    if "is_tms_cat_dropdown" in modes and modes["is_tms_cat_dropdown"] == "true":
                        modes_param = json.loads(bot_response_obj.modes_param)
                        modes_param[
                            "drop_down_choices"] = drop_down_choices_list
                        bot_response_obj.modes_param = json.dumps(modes_param)
                        bot_response_obj.save()
                    tree_obj = tree_obj.children.all()[0]
        response['status'] = 200
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_tms_categories: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})
    return response


##################################  TMS END###############################
#######################


"""

This function provides the file access url, it may need authentication or not, depends on is_authentication_required.

"""


def get_secure_file_path(file_path, user_id, bot, is_authentication_required=False, is_analytics_file=False):
    try:
        file_access_object = EasyChatAppFileAccessManagement.objects.create(
            file_path=file_path, is_authentication_required=is_authentication_required, is_analytics_file=is_analytics_file, bot=bot)
        file_key = file_access_object.key
        file_url = settings.EASYCHAT_HOST_URL + '/chat/access-file/' + \
                   str(file_key) + "/?user_id=" + user_id
        return file_url
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_secure_file_path: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})

        return ""


"""

This function checks if word mapper similar words are in correct format

"""


def is_similar_words_format_correct(values_list):
    try:
        if values_list == []:
            return False

        for value in values_list:
            if len(str(value).split()) > 1:
                return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_similar_words_format_correct: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})

        return False

    return True


"""

This function checks if common similar words already exist in word mapper

"""


def is_similar_words_already_exist(values_list, bot_obj, WordMapper):
    try:
        word_mapper_objs = WordMapper.objects.filter(
            bots__in=[bot_obj])

        total_value_list = []
        for word_mapper_obj in word_mapper_objs:
            temp_values_list = [value.strip().lower() for value in str(word_mapper_obj.similar_words).split(",") if value != ""]
            total_value_list += temp_values_list

        common_value_list = list(set(values_list) & set(total_value_list))

        if len(common_value_list) > 0:
            return True

        return False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("is_similar_words_alread_exist: %s at %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'none'})

    return True


def export_easychat_analytics_file(request_data, user_obj, type_of_analytics, start_date, end_date, channel_value, bot_pk, filter_type_particular,
                                   category_name, selected_language, supported_languages, dropdown_language, to_be_mailed=False, email_id="", export_request_obj=None):
    export_file_path = ""
    try:
        if type_of_analytics == "message_analytics":
            export_file_path = create_and_send_message_analytics(
                start_date, end_date, channel_value, bot_pk, filter_type_particular, email_id, category_name,
                selected_language, supported_languages, to_be_mailed, export_request_obj)
        elif type_of_analytics == "user_analytics":
            export_file_path = create_user_analytics(
                start_date, end_date, channel_value, bot_pk, filter_type_particular, email_id, selected_language,
                supported_languages, to_be_mailed, export_request_obj)
        elif type_of_analytics == "most_frequent_intents":
            export_file_path = create_frequent_intents_excel(
                start_date, end_date, False, bot_pk, channel_value, email_id, category_name, selected_language,
                supported_languages, to_be_mailed, dropdown_language, export_request_obj)
        elif type_of_analytics == "least_frequent_intents":
            export_file_path = create_frequent_intents_excel(
                start_date, end_date, True, bot_pk, channel_value, email_id, category_name, selected_language,
                supported_languages, to_be_mailed, dropdown_language, export_request_obj)
        elif type_of_analytics == "intent_wise_chartflow":
            export_file_path = create_frequent_intents_wise_chartflow_excel(
                start_date, end_date, bot_pk, channel_value, email_id, category_name, selected_language,
                supported_languages, to_be_mailed, dropdown_language, export_request_obj)
        elif type_of_analytics == "category_wise_frequent_questions":
            export_file_path = create_category_excel(
                start_date, end_date, bot_pk, channel_value, email_id, category_name, selected_language,
                supported_languages, to_be_mailed, dropdown_language, export_request_obj)
        elif type_of_analytics == "unanswered_questions":
            export_file_path = create_unanswered_query_excel(
                start_date, end_date, bot_pk, channel_value, email_id, selected_language, supported_languages,
                to_be_mailed, export_request_obj)
        elif type_of_analytics == "intuitive_questions":
            export_file_path = create_intuitive_query_excel(
                start_date, end_date, bot_pk, channel_value, email_id, selected_language, supported_languages,
                to_be_mailed, dropdown_language, export_request_obj)
        elif type_of_analytics == "device_specific_analytics":
            export_file_path = create_and_send_device_specific_analytics(
                start_date, end_date, channel_value, bot_pk, filter_type_particular, email_id, category_name,
                selected_language, supported_languages, to_be_mailed, export_request_obj)
        elif type_of_analytics == "hour_wise_analytics":
            interval_type, time_format = filter_type_particular[0], filter_type_particular[1]
            export_file_path = create_hour_wise_excel(
                start_date, end_date, bot_pk, channel_value, email_id, category_name, selected_language, supported_languages, interval_type, time_format,
                to_be_mailed, dropdown_language, export_request_obj)
        elif type_of_analytics == "whatsapp_catalogue_analytics":
            export_file_path = create_and_send_combined_whatsapp_analytics(
                start_date, end_date, channel_value, bot_pk, filter_type_particular, email_id, to_be_mailed, export_request_obj)
        elif type_of_analytics == "most_used_form_assist_intents":
            is_language_filter_applied = True if selected_language.lower() != "all" else False
            export_file_path = export_form_assist_intent(Bot, Intent, FormAssist, FormAssistAnalytics, bot_pk, str(user_obj.username), is_language_filter_applied, supported_languages, dropdown_language, email_id, to_be_mailed, export_request_obj, start_date, end_date)
        elif type_of_analytics == "user_nudge_analytics":
            export_file_path = create_user_nudge_analytics_excel(
                user_obj, bot_pk, channel_value, category_name, start_date, end_date, selected_language,
                supported_languages, email_id, True, export_request_obj)
        if type_of_analytics == "flow_conversion_analytics":
            channel_list = request_data["channel_list"]
            export_file_path = create_flow_conversion_analytics_excel(
                start_date, end_date, channel_list, bot_pk, email_id, to_be_mailed, selected_language, export_request_obj)
        elif type_of_analytics == "intent_conversion_analytics":
            channel_list = request_data["channel_list"]
            export_file_path = create_intent_conversion_analytics_excel(
                start_date, end_date, channel_list, bot_pk, email_id, to_be_mailed, selected_language, export_request_obj)
        elif type_of_analytics == "livechat_conversion_analytics":
            channel_list = request_data["channel_list"]
            export_file_path = create_livechat_conversion_analytics_excel(
                start_date, end_date, channel_list, bot_pk, email_id, to_be_mailed, export_request_obj)
        elif type_of_analytics == "dropoff_conversion_analytics":
            channel_list = request_data["channel_list"]
            export_file_path = create_dropoff_conversion_analytics_excel(start_date, end_date, channel_list, bot_pk,
                                                                         email_id, to_be_mailed, selected_language, export_request_obj)
        elif type_of_analytics == "whatsapp_block_analytics":
            block_type = request_data.get("spam_type", "All")
            export_file_path = create_whatsapp_block_analytics_excel(start_date, end_date, block_type, bot_pk,
                                                                      email_id, to_be_mailed, export_request_obj)
        elif type_of_analytics == "catalogue_conversion_analytics":
            is_catalogue_purchased = request_data.get("is_catalogue_purchased", "all")
            export_file_path = create_whatsapp_catalogue_analytics_csv(start_date, end_date, is_catalogue_purchased, bot_pk,
                                                                       email_id, to_be_mailed, export_request_obj)
        elif type_of_analytics == "welcome_conversion_analytics":
            export_file_path = get_welcome_conversion_analytics_export_file_path(
                start_date, end_date, bot_pk, email_id, selected_language, True, export_request_obj)
        elif type_of_analytics == "traffic_conversion_analytics":
            source_list = request_data.get("source_list", [])
            export_file_path = get_traffic_conversion_analytics_export_file_path(
                start_date, end_date, source_list, bot_pk, email_id, True, export_request_obj)

        return export_file_path
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("export_easychat_analytics_file: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return export_file_path


def start_thread_of_sending_data_via_mail(user_obj, type_of_analytics, start_date, end_date, channel_value, bot_pk,
                                          filter_type_particular, email_id, category_name, selected_language,
                                          supported_languages, dropdown_language, export_request_obj):
    try:
        if type_of_analytics == "message_analytics":
            thread = threading.Thread(target=create_and_send_message_analytics, args=(
                start_date, end_date, channel_value, bot_pk, filter_type_particular, email_id, category_name,
                selected_language, supported_languages, True, export_request_obj,), daemon=True)
            thread.start()
        elif type_of_analytics == "user_analytics":
            thread = threading.Thread(target=create_user_analytics, args=(
                start_date, end_date, channel_value, bot_pk, filter_type_particular, email_id, selected_language,
                supported_languages, True, export_request_obj,), daemon=True)
            thread.start()
        elif type_of_analytics == "most_frequent_intents":
            thread = threading.Thread(target=create_frequent_intents_excel, args=(
                start_date, end_date, False, bot_pk, channel_value, email_id, category_name, selected_language,
                supported_languages, True, dropdown_language, export_request_obj,), daemon=True)
            thread.start()
        elif type_of_analytics == "least_frequent_intents":
            thread = threading.Thread(target=create_frequent_intents_excel, args=(
                start_date, end_date, True, bot_pk, channel_value, email_id, category_name, selected_language,
                supported_languages, True, dropdown_language, export_request_obj,), daemon=True)
            thread.start()
        elif type_of_analytics == "intent_wise_chartflow":
            thread = threading.Thread(target=create_frequent_intents_wise_chartflow_excel, args=(
                start_date, end_date, bot_pk, channel_value, email_id, category_name, selected_language,
                supported_languages, True, dropdown_language, export_request_obj,), daemon=True)
            thread.start()
        elif type_of_analytics == "category_wise_frequent_questions":
            thread = threading.Thread(target=create_category_excel, args=(
                start_date, end_date, bot_pk, channel_value, email_id, category_name, selected_language,
                supported_languages, True, dropdown_language, export_request_obj,), daemon=True)
            thread.start()
        elif type_of_analytics == "unanswered_questions":
            thread = threading.Thread(target=create_unanswered_query_excel, args=(start_date, end_date, bot_pk, channel_value, email_id, selected_language, supported_languages, True, export_request_obj,), daemon=True)
            thread.start()
        elif type_of_analytics == "intuitive_questions":
            thread = threading.Thread(target=create_intuitive_query_excel, args=(start_date, end_date, bot_pk, channel_value, email_id, selected_language, supported_languages, True, dropdown_language, export_request_obj,), daemon=True)
            thread.start()
        elif type_of_analytics == "device_specific_analytics":
            thread = threading.Thread(target=create_and_send_device_specific_analytics, args=(
                start_date, end_date, channel_value, bot_pk, filter_type_particular, email_id, category_name,
                selected_language, supported_languages, True, export_request_obj,), daemon=True)
            thread.start()
        elif type_of_analytics == "hour_wise_analytics":
            interval_type, time_format = filter_type_particular[0], filter_type_particular[1]
            thread = threading.Thread(target=create_hour_wise_excel, args=(
                start_date, end_date, bot_pk, channel_value, email_id, category_name, selected_language, supported_languages, interval_type, time_format,
                True, dropdown_language, export_request_obj,), daemon=True)
            thread.start()
        elif type_of_analytics == "whatsapp_catalogue_analytics":
            thread = threading.Thread(target=create_and_send_combined_whatsapp_analytics, args=(
                start_date, end_date, channel_value, bot_pk, filter_type_particular, email_id, True, export_request_obj,), daemon=True)
            thread.start()
        elif type_of_analytics == "most_used_form_assist_intents":
            is_language_filter_applied = True if selected_language.lower() != "all" else False
            thread = threading.Thread(target=export_form_assist_intent, args=(Bot, Intent, FormAssist, FormAssistAnalytics, bot_pk, str(
                user_obj.username), is_language_filter_applied, supported_languages, dropdown_language, email_id, True, export_request_obj, start_date, end_date), daemon=True)
            thread.start()
        elif type_of_analytics == "user_nudge_analytics":
            thread = threading.Thread(target=create_user_nudge_analytics_excel, args=(user_obj, bot_pk, channel_value, category_name,
                                      start_date, end_date, selected_language, supported_languages, email_id, True, export_request_obj), daemon=True)
            thread.start()
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("start_thread_of_sending_data_via_mail: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def check_for_system_commands(code, Config):
    try:
        config_obj = Config.objects.all()[0]
        system_commands = json.loads(
            config_obj.system_commands.replace("'", '"'))

        for command in system_commands:
            if command in code:
                return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_for_system_commands: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return False


def check_and_parse_channel_messages(welcome_message, failure_message, authentication_message):
    try:
        message_list = [welcome_message, failure_message, authentication_message]
        [welcome_message, failure_message, authentication_message] = list(map(parse_messages, message_list))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_parse_channel_messages: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return welcome_message, failure_message, authentication_message


def parse_messages(message):
    try:
        message = str(BeautifulSoup(
            message, 'html.parser'))
        message = message.strip()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("parse_messages: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return message


def check_channel_status_and_message(welcome_message, failure_message, authentication_message):
    status = 500
    message = ""
    try:
        validation_obj = EasyChatInputValidation()
        welcome_message = validation_obj.remo_html_from_string(welcome_message)
        failure_message = validation_obj.remo_html_from_string(failure_message)
        authentication_message = validation_obj.remo_html_from_string(authentication_message)
        
        if BeautifulSoup(welcome_message).text.strip() == "":
            status = 400
            message = "Welcome message is either empty or invalid"

        if len(welcome_message.strip()) > CHARACTER_LIMIT_LARGE_TEXT:
            status = 400
            message = "Welcome Message is too long."

        if BeautifulSoup(failure_message).text.strip() == "":
            status = 400
            message = "Failure message is either empty or invalid"

        if len(failure_message.strip()) > CHARACTER_LIMIT_LARGE_TEXT:
            status = 400
            message = "Failure message is too long."

        if BeautifulSoup(authentication_message).text.strip() == "":
            status = 400
            message = "Authentication message is either empty or invalid"

        if len(authentication_message.strip()) > CHARACTER_LIMIT_LARGE_TEXT:
            status = 400
            message = "Authentication message is too long."

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_channel_status_and_message: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return status, message


def check_channel_warning_and_block_message(
    query_warning_message_text, query_block_message_text,
    keywords_warning_message_text, keywords_block_message_text
):
    status = 500
    message = ""
    try:
        if BeautifulSoup(query_warning_message_text).text.strip() == "":
            status = 400
            message = "Warning message for user queries is either empty or invalid"

        if len(query_warning_message_text.strip()) > CHARACTER_LIMIT_LARGE_TEXT:
            status = 400
            message = "Warning message for user queries is too long."

        if BeautifulSoup(query_block_message_text).text.strip() == "":
            status = 400
            message = "Blocking message for user queries is either empty or invalid"

        if len(query_block_message_text.strip()) > CHARACTER_LIMIT_LARGE_TEXT:
            status = 400
            message = "Blocking message for user queries is too long."

        if BeautifulSoup(keywords_warning_message_text).text.strip() == "":
            status = 400
            message = "Warning message for spam keywords is either empty or invalid"

        if len(keywords_warning_message_text.strip()) > CHARACTER_LIMIT_LARGE_TEXT:
            status = 400
            message = "Warning message for spam keywords is too long."

        if BeautifulSoup(keywords_block_message_text).text.strip() == "":
            status = 400
            message = "Blocking message for spam keywords is either empty or invalid"

        if len(keywords_block_message_text.strip()) > CHARACTER_LIMIT_LARGE_TEXT:
            status = 400
            message = "Blocking message for spam keywords is too long."

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_channel_warning_and_block_message: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return status, message


def get_multilingual_bot_web_landing_list(bot_web_landing_list, tuned_web_landing_list):
    try:
        final_list = bot_web_landing_list
        for web_landing_data in bot_web_landing_list:
            id = web_landing_data['id']
            for tuned_data in tuned_web_landing_list:
                if tuned_data['id'] == id:
                    web_landing_data['prompt_message'] = tuned_data[
                        'prompt_message']
                    break
        final_list = bot_web_landing_list
        return final_list
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_multilingual_failure_response: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return final_list


def get_multilingual_tree_name(tree_obj, language_obj):
    try:
        intent_obj = get_intent_obj_from_tree_obj(tree_obj)

        if language_obj.lang == "en":
            return tree_obj.name, None
        lang_tuned_tree_obj = LanguageTuningTreeTable.objects.filter(
            language=language_obj, tree=tree_obj)
        if lang_tuned_tree_obj.exists():
            return lang_tuned_tree_obj[0].multilingual_name, lang_tuned_tree_obj[0]

        bot_info_obj = None
        if intent_obj:
            bot_info_obj = BotInfo.objects.filter(bot=intent_obj.bots.first()).first()

        multilingual_name = get_translated_text(
            tree_obj.name, language_obj.lang, EasyChatTranslationCache, bot_info_obj=bot_info_obj)

        return multilingual_name, None
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_multilingual_tree_name: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return tree_obj.name, None


def get_multilingual_tree_sentence(tree_obj, language_obj, lang_tuned_tree_obj):
    try:
        sentence = json.loads(
            tree_obj.response.sentence)["items"][0]["text_response"]

        if language_obj.lang == "en":
            return sentence

        if lang_tuned_tree_obj:
            return lang_tuned_tree_obj.get_response_without_html()

        multilingual_name = get_translated_text(
            sentence, language_obj.lang, EasyChatTranslationCache)

        return multilingual_name
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_multilingual_tree_response: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

        return tree_obj.name


def get_bot_response_activity_update_status(response_obj, sentence, card_list, table_list, eng_lang_obj,
                                            LanguageTuningBotResponseTable):
    activity_update = json.loads(response_obj.activity_update)
    try:
        # if language tuned objects are not thier no need to update activity
        # update
        if not LanguageTuningBotResponseTable.objects.filter(bot_response=response_obj).exclude(
                language=eng_lang_obj).exists():
            return activity_update
        is_text_response_updated, is_speech_response_updated, is_text_reprompt_response_updated, are_cards_updated, is_table_updated = "false", "false", "false", "false", "false"
        response_sentence = json.loads(response_obj.sentence)
        response_sentence = response_sentence["items"][0]
        old_resp = BeautifulSoup(
            response_sentence["text_response"]).text.strip()
        new_resp = BeautifulSoup(sentence["text_response"]).text.strip()
        if old_resp != new_resp:
            is_text_response_updated = "true"
        activity_update["is_text_response_updated"] = is_text_response_updated

        old_resp = BeautifulSoup(
            response_sentence["speech_response"]).text.strip()
        new_resp = BeautifulSoup(sentence["speech_response"]).text.strip()
        if old_resp != new_resp:
            is_speech_response_updated = "true"
        activity_update[
            "is_speech_response_updated"] = is_speech_response_updated

        old_resp = BeautifulSoup(
            response_sentence["text_reprompt_response"]).text.strip()
        new_resp = BeautifulSoup(sentence["reprompt_response"]).text.strip()
        if old_resp != new_resp:
            is_text_reprompt_response_updated = "true"

        activity_update[
            "is_text_reprompt_response_updated"] = is_text_reprompt_response_updated

        response_cards = json.loads(response_obj.cards)["items"]
        if response_cards != card_list:
            are_cards_updated = "true"
        activity_update["are_cards_updated"] = are_cards_updated

        response_table = json.loads(response_obj.table)["items"]
        if response_table != table_list:
            if table_list != "" or response_table != []:
                is_table_updated = "true"
        activity_update["is_table_updated"] = is_table_updated

        return activity_update
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_bot_response_activity_update_status: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return activity_update


def update_intent_activity_status(intent_obj, activity_update, eng_lang_obj, LanguageTuningIntentTable):
    try:
        if LanguageTuningIntentTable.objects.filter(intent=intent_obj).exclude(language=eng_lang_obj).exists():
            activity_update["is_intent_name_updated"] = "true"
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_intent_activity_status: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    

def update_tree_activity_status(tree_obj, activity_update, eng_lang_obj, LanguageTuningTreeTable):
    try:
        if LanguageTuningTreeTable.objects.filter(tree=tree_obj).exclude(language=eng_lang_obj).exists():
            activity_update["is_tree_name_updated"] = "true"
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_tree_activity_status: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def update_english_language_tuned_object(eng_lang_obj, intent_obj, bot_response_obj, intent_name,
                                         LanguageTuningIntentTable):
    try:
        if LanguageTuningIntentTable.objects.filter(language=eng_lang_obj, intent=intent_obj).exists():
            lang_obj = LanguageTuningIntentTable.objects.filter(
                language=eng_lang_obj, intent=intent_obj).first()
            lang_obj.multilingual_name = intent_name
            lang_obj.save()
            lang_bot_resp_obj = LanguageTuningBotResponseTable.objects.filter(
                language=eng_lang_obj, bot_response=bot_response_obj).first()
            lang_bot_resp_obj.sentence = bot_response_obj.sentence
            lang_bot_resp_obj.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("update_english_language_tuned_object: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def get_table_parameters(table_obj):
    table_params = {
        'count_variation': ['daily'],
        'channels': [],
        'message_analytics': [],
        'session_analytics': [],
        'user_analytics': [],
        'livechat_analytics': [],
        'language_analytics': [],
        'language_query_analytics': [],
    }

    try:
        if table_obj:
            table_params = {
                'count_variation': json.loads(table_obj.count_variation),
                'channels': json.loads(table_obj.channels),
                'message_analytics': json.loads(table_obj.message_analytics),
                'session_analytics': json.loads(table_obj.session_analytics),
                'user_analytics': json.loads(table_obj.user_analytics),
                'livechat_analytics': json.loads(table_obj.livechat_analytics),
                'flow_analytics': json.loads(table_obj.flow_completion),
                'intent_analytics': json.loads(table_obj.intent_analytics),
                'traffic_analytics': json.loads(table_obj.traffic_analytics),
                'language_analytics': json.loads(table_obj.language_analytics),
                'language_query_analytics': json.loads(table_obj.language_query_analytics),
            }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_table_parameters: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return table_params


def get_graph_parameters(graph_obj):
    graph_params = {
        'graph_parameters': [],
        'message_analytics_graph': [],
    }

    try:
        if graph_obj:
            graph_params = {
                'graph_parameters': json.loads(graph_obj.graph_parameters),
                'message_analytics_graph': json.loads(graph_obj.message_analytics_graph),
            }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_graph_parameters: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return graph_params


def get_attachment_parameters(attachment_obj):
    attachment_params = {
        'attachments': [],
    }

    try:
        if attachment_obj:
            attachment_params = {
                'attachments': json.loads(attachment_obj.attachments),
            }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_attachment_parameters: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return attachment_params


def get_mailer_profile_data(bot_obj, EasyChatMailerAnalyticsProfile, EasyChatMailerTableParameters):
    try:
        profile_objs = EasyChatMailerAnalyticsProfile.objects.filter(
            bot=bot_obj)

        if not profile_objs:
            create_default_profile(
                bot_obj, EasyChatMailerAnalyticsProfile, EasyChatMailerTableParameters)
            profile_objs = EasyChatMailerAnalyticsProfile.objects.filter(
                bot=bot_obj)

        active_profile_objs = profile_objs.filter(is_deleted=False)

        profile_dict = {}
        if active_profile_objs:
            for profile_obj in active_profile_objs:
                profile_dict[profile_obj.name] = {
                    "id": profile_obj.pk,
                    "name": profile_obj.name,
                    "email_frequency": json.loads(profile_obj.email_frequency),
                    "email_address": json.loads(profile_obj.email_address),
                    "email_subject": profile_obj.email_subject,
                    "bot_accuracy": profile_obj.bot_accuracy_threshold,
                    "is_graph_enabled": profile_obj.is_graph_enabled,
                    "is_table_enabled": profile_obj.is_table_enabled,
                    "is_attachment_enabled": profile_obj.is_attachment_enabled,
                    "table_params": get_table_parameters(profile_obj.table_parameters),
                    "graph_params": get_graph_parameters(profile_obj.graph_parameters),
                    "attachment_params": get_attachment_parameters(profile_obj.attachment_parameters),
                }

        return json.dumps(profile_dict)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_mailer_profile_data: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return json.dumps({})


def create_default_profile(bot_obj, EasyChatMailerAnalyticsProfile, EasyChatMailerTableParameters):
    try:
        profile_obj = EasyChatMailerAnalyticsProfile.objects.create(
            bot=bot_obj,
            name='Profile 1',
            email_frequency=json.dumps([]),
            email_address=json.dumps([]))

        table_obj = EasyChatMailerTableParameters.objects.create(
            profile=profile_obj,
            count_variation=json.dumps(['daily']),
            channels=json.dumps([]),
            message_analytics=json.dumps([]),
            session_analytics=json.dumps([]),
            user_analytics=json.dumps([]),
            livechat_analytics=json.dumps([]),
            flow_completion=json.dumps([]),
            intent_analytics=json.dumps([]),
            traffic_analytics=json.dumps([]), )

        profile_obj.table_parameters = table_obj
        profile_obj.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_default_profile: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def create_mailer_table_object(profile_obj, table_params, EasyChatMailerTableParameters):
    try:
        table_obj = EasyChatMailerTableParameters.objects.create(
            profile=profile_obj,
            count_variation=json.dumps(table_params['count_variation']),
            channels=json.dumps(table_params['channels']),
            message_analytics=json.dumps(table_params['message_analytics']),
            session_analytics=json.dumps(table_params['session_analytics']),
            user_analytics=json.dumps(table_params['user_analytics']),
            livechat_analytics=json.dumps(table_params['livechat_analytics']),
            flow_completion=json.dumps(table_params['flow_analytics']),
            intent_analytics=json.dumps(table_params['intent_analytics']),
            traffic_analytics=json.dumps(table_params['traffic_analytics']),
            language_analytics=json.dumps(table_params['language_analytics']),
            language_query_analytics=json.dumps(table_params['language_query_analytics'])
        )

        return table_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_mailer_table_object: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def create_mailer_graph_object(profile_obj, graph_params, EasyChatMailerGraphParameters):
    try:
        graph_obj = EasyChatMailerGraphParameters.objects.create(
            profile=profile_obj,
            graph_parameters=json.dumps(graph_params['graph_parameters']),
            message_analytics_graph=json.dumps(graph_params['message_analytics_graph']))

        return graph_obj
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_mailer_graph_object: %s %s", str(e), str(exc_tb.tb_lineno), extra={
            'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def create_new_auth_page(detail_obj_id, channel):
    try:
        if channel == "GoogleHome":
            base_html_file = open(
                settings.BASE_DIR + "/EasyChatApp/templates/EasyChatApp/channels/ga_auth.html", "r")
            code = base_html_file.read()
            base_html_file.close()
            file_path = settings.BASE_DIR + \
                        "/EasyChatApp/templates/EasyChatApp/channels/ga_auth_" + \
                        str(detail_obj_id) + ".html"
        elif channel == "Alexa":
            base_html_file = open(
                settings.BASE_DIR + "/EasyChatApp/templates/EasyChatApp/channels/alexa_auth.html", "r")
            file_path = settings.BASE_DIR + \
                        "/EasyChatApp/templates/EasyChatApp/channels/alexa_auth_" + \
                        str(detail_obj_id) + ".html"
            code = base_html_file.read()
            base_html_file.close()

        base_html_file = open(file_path, "w")
        base_html_file.write(code)
        base_html_file.close()
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error create_new_auth_page! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': ''})


def ensure_element_tree(xlrd):
    try:
        xlrd.xlsx.ensure_elementtree_imported(False, None)
        xlrd.xlsx.Element_has_iter = True
    except Exception:
        pass


def update_welcome_banner_on_intent_delete(intent_obj):
    try:
        welcome_banner_objs = WelcomeBanner.objects.filter(intent=intent_obj)
        for welcome_banner_obj in welcome_banner_objs:
            welcome_banner_obj.intent = None
            welcome_banner_obj.save()
    except Exception:
        pass


"""
function: get_identified_intent
input params:
    message: message for automated testing
    user_obj: active user object
    bot_objs: list of bot objects
output params:
    1. True/False: False incase of conflict intent or no intent
    2. intent object list

"""


def get_identified_intent(message, user_obj, bot_objs, channel_objs):
    try:
        stem_words = get_stem_words_of_sentence(
            message, None, None, None, bot_objs)

        intent_objs = Intent.objects.filter(bots__in=bot_objs, is_deleted=False, is_hidden=False, channels__in=channel_objs).distinct()
        intent_tuple_list = []
        max_score = 0

        overall_intent_score_threshold = bot_objs[0].intent_score_threshold

        user_query_stem_words_with_pos_list = get_query_stem_words_with_pos_list(message, bot_objs[0])

        for intent_obj in intent_objs:
            intent_score = intent_obj.get_score(
                stem_words, None, None, None, message, bot_objs[0], user_query_stem_words_with_pos_list)

            if intent_score[0] >= intent_obj.threshold and intent_score[0] >= max_score:
                overall_intent_score = intent_score[0] / (intent_score[0] - intent_score[1])

                if overall_intent_score >= overall_intent_score_threshold:
                    intent_tuple_list.append((intent_score[0], intent_score[1], intent_obj))
                    max_score = intent_score[0]

        intent_tuple_list = sorted(intent_tuple_list, key=lambda element: (element[0], element[1]))
        intent_tuple_list.reverse()

        if len(intent_tuple_list) > 0:
            max_matched_score = intent_tuple_list[0][0]
            not_matched_score = intent_tuple_list[0][1]

            filtered_intent_tuple_list = [(x, intent_obj) for (
                x, y, intent_obj) in intent_tuple_list if x == max_matched_score and y == not_matched_score]

            if len(filtered_intent_tuple_list) == 1:
                return True, filtered_intent_tuple_list[0][1]
            else:
                intent_obj_list = []
                for (score, intent_obj) in filtered_intent_tuple_list:
                    intent_obj_list.append(intent_obj)
                return False, intent_obj_list

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("[NLP]: get_identified_intent %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return False, []


def check_and_return_easychat_session_if_expired(session_id):
    try:
        if session_id == "":
            return session_id

        session_obj = EasyChatSessionIDGenerator.objects.get(token=session_id)

        if session_obj.is_session_expired():
            session_id = ""

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(" check_session_if_expired %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return session_id


def get_session_id_for_current_session(session_id):
    final_session_id = session_id
    is_session_to_be_created = False
    is_previous_session_expired = False
    try:

        if session_id != "":

            session_obj = EasyChatSessionIDGenerator.objects.get(
                token=session_id)

            if session_obj.is_session_expired():
                is_session_to_be_created = True
                is_previous_session_expired = True

        else:
            is_session_to_be_created = True

        if is_session_to_be_created:
            session_obj = EasyChatSessionIDGenerator.objects.create()
            final_session_id = str(session_obj.token)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(" check_and_get_user_id_based_on_session_and_cookies %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return final_session_id, is_previous_session_expired, is_session_to_be_created


def check_and_get_user_id_based_on_session_and_cookies(user_id, is_previous_session_expired):
    final_user_id = user_id
    is_user_session_retained = False

    try:
        if user_id == "":
            return final_user_id, is_user_session_retained

        if is_previous_session_expired:
            final_user_id = ""
        else:
            is_user_session_retained = True

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(" check_and_get_user_id_based_on_session_and_cookies %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return final_user_id, is_user_session_retained


def reseting_user_details(user_id, bot_obj):
    try:

        user = Profile.objects.filter(user_id=user_id, bot=bot_obj)

        if user.exists():
            user = user.first()
        else:
            return
        if user.tree and user.tree.children.all().count():
            generate_flow_dropoff_object(user)
        user.tree = None
        user.user_pipe = ""
        user.save()
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("reseting_user_details %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def check_and_create_time_spent_by_the_user_object(user_id, session_id, bot_id, other_params):
    try:
        time_spent_by_user_objs = TimeSpentByUser.objects.filter(
            user_id=user_id, session_id=session_id)

        if time_spent_by_user_objs.exists():
            return

        bot_web_page = ""
        if "bot_web_page" in other_params:
            bot_web_page = other_params["bot_web_page"]

        web_page_source = ""
        if "web_page_source" in other_params:
            web_page_source = other_params["web_page_source"]

        start_datetime = datetime.datetime.now()

        bot_obj = Bot.objects.get(
            pk=bot_id, is_uat=True, is_deleted=False)

        TimeSpentByUser.objects.create(
            user_id=user_id, session_id=session_id, start_datetime=start_datetime, end_datetime=start_datetime,
            bot=bot_obj, web_page=bot_web_page, web_page_source=web_page_source)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("check_and_create_time_spent_by_the_user_object %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def create_and_set_user_and_session_if_required(session_id, user_id, bot_id, other_params):
    final_user_id = user_id
    try:
        session_id, is_previous_session_expired, _ = get_session_id_for_current_session(
            session_id)

        final_user_id, _ = check_and_get_user_id_based_on_session_and_cookies(
            user_id, is_previous_session_expired)

        user = set_user(final_user_id, "", None, None, bot_id)

        final_user_id = user.user_id

        check_and_create_time_spent_by_the_user_object(
            user_id, session_id, bot_id, other_params)

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("create_and_set_user_and_session_if_required %s in line no %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return session_id, final_user_id


def redirect_to_livechat(request, LiveChatUser, Supervisor, HttpResponseRedirect):
    try:
        livechat_user_obj = LiveChatUser.objects.filter(user=request.user)
        status = livechat_user_obj[0].status

        if Supervisor.objects.filter(managers__in=[request.user]).count():
            return None
        elif status == "2" or livechat_user_obj[0].is_livechat_only_admin:
            return HttpResponseRedirect("/livechat/chat-history")
        elif status == "3" and not livechat_user_obj[0].is_allow_toggle:
            return HttpResponseRedirect("/livechat/")
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("redirect_to_livechat: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return None


def redirect_to_easyassist(request, HttpResponseRedirect):
    try:
        user_obj = User.objects.get(username=request.user.username)
        agent_objs = CobrowseAgent.objects.filter(
            user=user_obj)
        if agent_objs:
            agent_obj = agent_objs[0]
            access_token_obj = agent_obj.get_access_token_obj()
            if access_token_obj and access_token_obj.agent != agent_obj:
                return HttpResponseRedirect("/easy-assist/sales-ai/dashboard")
            else:
                return None
        else:
            return None

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("redirect_to_easyassist: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

        return None


def return_invalid_response(response, response_message, status):
    try:
        response["status"] = status
        response["status_message"] = response_message
        custom_encrypt_obj = CustomEncrypt()
        response = custom_encrypt_obj.encrypt(
            json.dumps(response))
        return response

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("return_invalid_response: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})

        return None


def is_duplicate_intent_exists(intent_name, bot_obj, curr_intent_pk, channel_objs):
    try:
        hashed_name = get_hashed_intent_name(intent_name, bot_obj)
        intent_objs = Intent.objects.filter(
            bots__in=[bot_obj], channels__in=channel_objs, is_deleted=False).distinct()

        intent_objs = intent_objs.filter(intent_hash=hashed_name)

        if intent_objs.count() >= 1:
            is_duplicate = True

            if intent_objs.count() == 1:
                if intent_objs.first().pk == curr_intent_pk:
                    is_duplicate = False

            return is_duplicate

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("return_invalid_response: %s at %s", str(exc), str(
            exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})

    return False


def get_response_sentence_list(json_string):
    data = json.loads(json_string)
    return data["response_sentence_list"]


def remove_custom_html_from_dict_values(data):
    validation_obj = EasyChatInputValidation()
    fields_to_skip = {
        "post_processor_function",
    }
    for fields in data:
        if fields not in fields_to_skip:
            if isinstance(data[fields], str):
                data[fields] = validation_obj.custom_remo_html_tags(data[fields])
            else:
                data[fields] = json.loads(validation_obj.custom_remo_html_tags(json.dumps(data[fields])))
    return data


def get_easychat_theme_obj(theme_selected):
    try:
        if theme_selected == "theme_1":
            try:
                theme_obj = EasyChatTheme.objects.get(
                    name="theme_1", main_page="EasyChatApp/theme1_bot.html", chat_page="EasyChatApp/theme1.html")
            except Exception:
                theme_obj = EasyChatTheme.objects.create(
                    name="theme_1", main_page="EasyChatApp/theme1_bot.html", chat_page="EasyChatApp/theme1.html")
            return theme_obj
        if theme_selected == "theme_2":
            try:
                theme_obj = EasyChatTheme.objects.get(
                    name="theme_2", main_page="EasyChatApp/theme2_bot.html", chat_page="EasyChatApp/theme2.html")
            except Exception:
                theme_obj = EasyChatTheme.objects.create(
                    name="theme_2", main_page="EasyChatApp/theme2_bot.html", chat_page="EasyChatApp/theme2.html")
            return theme_obj
        if theme_selected == "theme_3":
            try:
                theme_obj = EasyChatTheme.objects.get(
                    name="theme_3", main_page="EasyChatApp/theme3_bot.html", chat_page="EasyChatApp/theme3.html")
            except Exception:
                theme_obj = EasyChatTheme.objects.create(
                    name="theme_3", main_page="EasyChatApp/theme3_bot.html", chat_page="EasyChatApp/theme3.html")
            return theme_obj
        if theme_selected == "theme_4":
            try:
                theme_obj = EasyChatTheme.objects.get(
                    name="theme_4", main_page="EasyChatApp/theme4_bot.html", chat_page="EasyChatApp/theme4.html")
            except Exception:
                theme_obj = EasyChatTheme.objects.create(
                    name="theme_4", main_page="EasyChatApp/theme4_bot.html", chat_page="EasyChatApp/theme4.html", theme_image_paths=json.dumps(DEFAULT_THEME_IMAGE_DICT["theme_4"]))
            return theme_obj

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_easychat_theme_obj ! %s %s",
                        str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return None


def is_valid_file_access_request(user, file_management_obj):
    try:
        # If requested file is an EasyChat Analytics File 
        # Un-authenticated users & users not having access to the bot under which file is created
        # Can only access till FILE_ACCESS_MANAGEMENT_EXPIRE_TIME_LIMIT is not exceeded
        # Users with access to that bot can access the file anytime.
        if file_management_obj.is_analytics_file and file_management_obj.is_obj_time_limit_exceeded():
            if not user.is_authenticated or (user.is_authenticated and file_management_obj.bot and user not in file_management_obj.bot.users.all()):
                return False
        return True
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In is_valid_file_access_request ! %s %s",
                        str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return False


def get_intent_obj_from_tree_obj(tree_obj):
    try:
        while True:
            intent_obj = Intent.objects.filter(tree=tree_obj, is_deleted=False).first()
            if intent_obj:
                return intent_obj
            
            tree_objs = Tree.objects.filter(children__in=[tree_obj], is_deleted=False)
            if not tree_objs:
                return None
            tree_obj = tree_objs.first()

    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_intent_obj_from_tree_obj ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return None


def get_parent_tree_obj(tree_obj):
    try:
        intent_obj = Intent.objects.filter(tree=tree_obj, is_deleted=False).first()
        if intent_obj:
            return None

        parent_tree = Tree.objects.filter(children__in=[tree_obj], is_deleted=False).first()
        if tree_obj:
            return parent_tree
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_parent_tree_obj ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return None


def get_dot_replaced_file_name(file_name):
    try:
        splitted_name = os.path.splitext(file_name)
        file_name = str(splitted_name[0]).replace('.', '_')
        file_name = re.sub(r"\s+", '-', file_name)
        file_name = file_name + splitted_name[1]
    except Exception as e:  # noqa: F841
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("In get_dot_replaced_file_name ! %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return file_name


def get_value_from_cache(key, dynamic_prefix):
    try:
        value = cache.get(key + str(dynamic_prefix))
        return value
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_value_from_cache: %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})
        return None


def set_value_to_cache(key, dynamic_prefix, value):
    try:
        cache.set(key + str(dynamic_prefix), value, settings.CACHE_TIME)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("set_value_to_cache: %s %s", str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})


def get_common_utils_file_code(bot_pk):
    try:
        common_utils_code = f"""from EasyChatApp.models import *
from django.core.cache import cache
result_dict = {{}}
try:
    current_bot_id = {bot_pk}
    common_utils_code = cache.get('CommonUtilsFileCode-' + str(current_bot_id))
    if not common_utils_code:
        bot_obj = Bot.objects.get(pk=current_bot_id)
        common_utils_obj = CommonUtilsFile.objects.get(bot=bot_obj)
        common_utils_code = common_utils_obj.code
        cache.set('CommonUtilsFileCode-' + str(current_bot_id), common_utils_code, 3600)

    exec(str(common_utils_code), result_dict)
except Exception as e:
    pass
"""

        return common_utils_code
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("get_common_utils_file_code: %s %s", str(
            e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat'})
        return ""
