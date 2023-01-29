import json
import re
import sys
import logging
import requests
import uuid
import os
import random
import string
from EasyChatApp.constants import *
from EasyChatApp.models import Tree
from EasyChatApp.utils_validation import EasyChatInputValidation
from django.conf import settings
from bs4 import BeautifulSoup

from oauth2client.service_account import ServiceAccountCredentials
from businessmessages import businessmessages_v1_client as bm_client
from businessmessages.businessmessages_v1_messages import (
    BusinessMessagesCarouselCard, BusinessMessagesCardContent, BusinessMessagesContentInfo,
    BusinessMessagesDialAction, BusinessmessagesConversationsMessagesCreateRequest,
    BusinessMessagesOpenUrlAction, BusinessMessagesMedia, BusinessMessagesMessage,
    BusinessMessagesRichCard, BusinessMessagesStandaloneCard,
    BusinessMessagesSuggestion, BusinessMessagesSuggestedAction, BusinessMessagesSuggestedReply,
    BusinessMessagesRepresentative, BusinessMessagesImage, BusinessmessagesConversationsSurveysCreateRequest,
    BusinessMessagesSurvey)
from businesscommunications.businesscommunications_v1_client import (
    BusinesscommunicationsV1
)
from businesscommunications.businesscommunications_v1_messages import (
    Agent,
    BusinessMessagesAgent,
    ConversationStarters,
    ConversationalSetting,
    OfflineMessage,
    PrivacyPolicy,
    WelcomeMessage,
    BusinesscommunicationsBrandsAgentsPatchRequest,
    Suggestion,
    SuggestedReply
)

logger = logging.getLogger(__name__)
log_param = {'AppName': 'EasyChat', 'user_id': 'None',
             'source': 'None', 'channel': 'None', 'bot_id': 'None'}

"""
function remo_html_from_string
input params:
    raw_str: Original string provided by customer

Output Params:
    cleaned_raw_str: After removing html tags
"""


def remo_html_from_string(raw_str):
    try:
        regex_cleaner = re.compile('<.*?>')
        cleaned_raw_str = re.sub(regex_cleaner, '', str(raw_str))
        return cleaned_raw_str.strip()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Inside remo_html_from_string: %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return raw_str.strip()


"""
function send_single_card
input params:
title
description
suggestions: suggestions for card
img url
conversation_id
this function is used to send a single card response
"""


def send_single_card(title, description, suggestions, img_url, conversation_id, bot_representative, service_account_location):
    try:
        fallback_text = ('Something went wrong')

        rich_card = BusinessMessagesRichCard(
            standaloneCard=BusinessMessagesStandaloneCard(
                cardContent=create_single_card_content(title, description, img_url, suggestions)))
        message_obj = BusinessMessagesMessage(
            messageId=str(uuid.uuid4().int),
            representative=bot_representative,
            richCard=rich_card,
            fallback=fallback_text)
        send_message_obj(message_obj, conversation_id,
                         service_account_location)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function send_multiple_cards
input params:
card_contents : list of card_contents
conversation_id
this function is used to send a multipe card response
"""


def send_multiple_cards(card_contents, conversation_id, bot_representative, service_account_location):
    try:
        rich_card = BusinessMessagesRichCard(
            carouselCard=BusinessMessagesCarouselCard(
                cardWidth=BusinessMessagesCarouselCard.CardWidthValueValuesEnum.MEDIUM,
                cardContents=card_contents))
        message_obj = BusinessMessagesMessage(
            messageId=str(uuid.uuid4().int),
            representative=bot_representative,
            richCard=rich_card,
            fallback="Something went wrong")
        send_message_obj(message_obj, conversation_id,
                         service_account_location)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function send_text_message
input params:
message
conversation_id
this function is used to send a text response to a gbm user
"""


def send_text_message(message, conversation_id, bot_representative, service_account_location):
    try:

        message_list = message.split("$$$")

        for message in message_list:

            message_obj = BusinessMessagesMessage(messageId=str(uuid.uuid4().int),
                                                  containsRichText=True,
                                                  representative=bot_representative,
                                                  text=message)
            send_message_obj(message_obj, conversation_id,
                             service_account_location)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function send_image_response
input params:
file_url :imageurl
conversation_id
this function is used to send a image response to a gbm user

"""


def send_image_response(fileUrl, conversation_id, bot_representative, service_account_location):

    try:
        image = BusinessMessagesImage(
            contentInfo=BusinessMessagesContentInfo(
                altText='image text',
                fileUrl=fileUrl,
                forceRefresh=False
            )
        )
        message_obj = BusinessMessagesMessage(
            messageId=str(uuid.uuid4().int),
            representative=bot_representative,
            image=image,
            fallback="this is fall back text")
        send_message_obj(message_obj, conversation_id,
                         service_account_location)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function send_message_obj
input params:
message_obj
conversation_id
this function  authenticate the credentials and make a send request of the message_obj to buisness messages api
"""


def send_message_obj(message_obj, conversation_id, service_account_location):
    try:

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            service_account_location,
            scopes=['https://www.googleapis.com/auth/businessmessages'])

        client = bm_client.BusinessmessagesV1(credentials=credentials)

        # Create the message request
        create_request = BusinessmessagesConversationsMessagesCreateRequest(
            businessMessagesMessage=message_obj,
            parent='conversations/' + conversation_id)

        bm_client.BusinessmessagesV1.ConversationsMessagesService(
            client=client).Create(request=create_request)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function send_message_with_suggestions
input params:
message
suggestions
conversation_id
this function sends the message with recommendations

"""


def send_message_with_suggestions(message, suggestions, conversation_id, bot_representative, service_account_location):
    try:
        suggestions = suggestions[:13]
        message_list = message.split("$$$")
        for message in message_list:
            message_obj = BusinessMessagesMessage(
                messageId=str(uuid.uuid4().int),
                containsRichText=True,
                representative=bot_representative,
                text=message,
                fallback='Something went wrong"',
                suggestions=suggestions)
            send_message_obj(message_obj, conversation_id,
                             service_account_location)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function create_single_card_content
input params
title
description
img_url
suggestions (optional)
this function is used to create single card content
"""


def create_single_card_content(title, description, img_url, suggestions=[]):
    try:

        return BusinessMessagesCardContent(
            title=title,
            description=description,
            suggestions=suggestions,
            media=BusinessMessagesMedia(
                height=BusinessMessagesMedia.HeightValueValuesEnum.MEDIUM,
                contentInfo=BusinessMessagesContentInfo(
                    fileUrl=img_url,
                    forceRefresh=False
                ))
        )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function
input params
cards : list of card details
this function is used to create card_content list
"""


def create_card_contents(cards):
    card_contents = []
    suggestions = []
    try:

        for card in cards:
            title = card['title']
            description = card['content']
            img_url = card['img_url']
            card_link = card['link']

            if card_link != "":
                suggestions = [
                    BusinessMessagesSuggestion(
                        action=BusinessMessagesSuggestedAction(
                            text='Click Here',
                            postbackData='custom_suggestion_link_click',
                            openUrlAction=BusinessMessagesOpenUrlAction(
                                url=card_link))
                    ),
                ]

            card_contents.append(create_single_card_content(
                title, description, img_url, suggestions))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    return card_contents


"""
function create_recommendation_list
input params
recommendations
this function is used to create sugestions for recommendations
"""


def create_recommendation_list(recommendations):
    suggestions = []
    try:
        for rec in recommendations:
            tree_pk = None
            try:
                if isinstance(rec, dict):
                    if 'tree_pk' in rec:
                        tree_pk = rec['tree_pk']
                    rec = rec['name']
            except:
                pass
            suggestions.append(BusinessMessagesSuggestion(
                reply=BusinessMessagesSuggestedReply(
                    text=format_suggestion_length(rec, tree_pk),
                    postbackData=rec)
            ))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return suggestions


"""
function create_choice_list
input params
choices
this function is used to create suggestions for choices
"""


def create_choice_list(choices):
    suggestions = []
    try:
        for choice in choices:
            if isinstance(choice, dict):
                tree_pk = None
                if 'tree_pk' in choice:
                    tree_pk = choice["tree_pk"]
                suggestions.append(BusinessMessagesSuggestion(
                    reply=BusinessMessagesSuggestedReply(
                        text=format_suggestion_length(choice['value'], tree_pk),
                        postbackData=choice['value'])
                ))

        return suggestions
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return suggestions


"""
function create_language_choice_list
input params
languages
this function is used to create suggestions for language choices
"""


def create_language_choice_list(languages):
    language_choices = []
    try:
        for language in languages:
            language_choices.append(BusinessMessagesSuggestion(
                reply=BusinessMessagesSuggestedReply(
                    text=format_suggestion_length(language['display']),
                    postbackData=language['lang'])
            ))

        return language_choices
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return language_choices


"""
function update_welcome_msg_for_gbm_agent
input params
welcome_message
inital_questions
gmb_agent_id
gmb_brand_id

this function updates the welcome message and conversation starters of the gbm agent

"""


def update_welcome_msg_for_gbm_agent(welcome_message, initial_questions, gmb_agent_id, gmb_brand_id, privacy_policy_url, service_account_location):
    try:
        validation_obj = EasyChatInputValidation()

        welcome_message = validation_obj.remo_html_from_string(welcome_message)
        welcome_message = validation_obj.unicode_formatter(welcome_message)
        scopes = ['https://www.googleapis.com/auth/businesscommunications']
        service_account_file = service_account_location

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            service_account_file, scopes=scopes)

        client = BusinesscommunicationsV1(credentials=credentials)

        agents_service = BusinesscommunicationsV1.BrandsAgentsService(client)

        agent_name = 'brands/' + gmb_brand_id + '/agents/' + gmb_agent_id

        agent = Agent(
            businessMessagesAgent=BusinessMessagesAgent(
                conversationalSettings=BusinessMessagesAgent.ConversationalSettingsValue(
                    additionalProperties=[BusinessMessagesAgent.ConversationalSettingsValue.AdditionalProperty(
                        key='en',
                        value=ConversationalSetting(
                            privacyPolicy=PrivacyPolicy(
                                url=privacy_policy_url),
                            welcomeMessage=WelcomeMessage(
                                text=welcome_message),
                            offlineMessage=OfflineMessage(text=''),
                            conversationStarters=get_conversation_starters(
                                initial_questions)
                        )
                    )
                    ]
                )
            )
        )

        agents_service.Patch(
            BusinesscommunicationsBrandsAgentsPatchRequest(
                agent=agent,
                name=agent_name,
                updateMask='businessMessagesAgent.conversationalSettings.en'
            )
        )
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error update_welcome_msg_for_gbm_agent %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return False


"""
function get_conversation_starters
inpurt params
initial_question
this function converts list of initial questions to list of conversation starters
"""


def get_conversation_starters(initial_questions):
    try:
        conversation_starters = []
        for conv_starter in initial_questions:
            conversation_starters.append(ConversationStarters(
                suggestion=Suggestion(
                    reply=SuggestedReply(text=format_suggestion_length(conv_starter),
                                         postbackData=conv_starter)
                )
            ))
        return conversation_starters

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function format_suggestion_length
input params
suggestion
this function is used to format suggestion length to 25 (max limit for gmb suggestion) of the suggestions which are longer than 25 chars
"""


def format_suggestion_length(suggestion, tree_pk=None):

    try:
        if tree_pk != None and str(Tree.objects.filter(pk=tree_pk).first().short_name) != "":
            suggestion = Tree.objects.filter(pk=tree_pk).first().short_name
        elif len(suggestion) > 25:
            suggestion = suggestion[:22] + "..."

        return suggestion
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error GBMQueryApi %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function send_livechat_attachment
input params:

this function is used to send attachment to gbm customer as a card  with sugestion url as the attached file url

"""


def send_livechat_attachment(title, description, img_url, conversation_id, bot_representative, service_account_location, attached_file_src):
    try:

        suggestions = [BusinessMessagesSuggestion(
            action=BusinessMessagesSuggestedAction(
                text=format_suggestion_length(title),
                postbackData="attachment-Recevied",
                openUrlAction=BusinessMessagesOpenUrlAction(
                    url=attached_file_src
                )
            )
        )]

        send_single_card(title, description, suggestions, img_url,
                         conversation_id, bot_representative, service_account_location)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send livechat attachment %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


"""
function send_gbm_livechat_agent_response
input params:
customer_obj: LiveChatCustomer object

this function is used to send Agent respone to to GBM customer

"""


def send_gbm_livechat_agent_response(customer_obj, session_id, message, attached_file_src, data, sender_name, Profile, Bot, GMBDetails):

    response = {}
    response["status"] = 200
    try:

        user_obj = Profile.objects.get(livechat_session_id=session_id)

        if user_obj.livechat_connected == True:

            conversation_id = user_obj.user_id
            selected_bot_obj = Bot.objects.get(
                pk=int(customer_obj.bot.pk), is_deleted=False, is_uat=True)

            gmb_obj = GMBDetails.objects.filter(bot=selected_bot_obj)[0]

            display_name = sender_name

            if display_name == "":
                display_name = gmb_obj.bot_display_name

            display_image_url = gmb_obj.bot_display_image_url
            service_account_location = gmb_obj.gmb_credentials_file_path

            bot_representative = BusinessMessagesRepresentative(
                representativeType=BusinessMessagesRepresentative.RepresentativeTypeValueValuesEnum.BOT,
                displayName=display_name,
                avatarImage=display_image_url)

            if attached_file_src != "":

                if "channel_file_url" in data:

                    attached_file_src = data["channel_file_url"]

                    try:
                        attached_file_src = settings.EASYCHAT_HOST_URL + attached_file_src

                        file_name = attached_file_src.split("/")[-1]

                        if is_image(file_name):
                            send_image_response(
                                attached_file_src, conversation_id, bot_representative, service_account_location)

                        else:
                            img_url = settings.EASYCHAT_HOST_URL + "/static/LiveChatApp/img/gbm_doc.jpg"

                            send_livechat_attachment(
                                file_name, file_name, img_url, conversation_id, bot_representative, service_account_location, attached_file_src)

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        logger.error("send_gbm_livechat_agent_response: %s at %s",
                                     e, str(exc_tb.tb_lineno), extra={'AppName': 'LiveChat'})

            if message != "":
                send_text_message(message, conversation_id,
                                  bot_representative, service_account_location)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error send_gbm_livechat_agent_response %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        response["status"] = 500

    return response


"""     
function save_and_get_gmb_image_src
input params:
img_url : image url 

this function is used to save the image sent by gbm customer in our filesystem and return the path of the image
Note: currently in the image url their is no way to know the Image format so we are saving the images in jpeg format

"""


def save_and_get_gmb_image_src(img_url):
    try:

        req = requests.get(url=img_url)

        if not os.path.exists('files/googlebusinessmessages-attachment'):
            os.makedirs('files/googlebusinessmessages-attachment')

        file_directory = "files/googlebusinessmessages-attachment/"

        file_name = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=16))

        full_path = file_directory + file_name + ".jpeg"

        local_file = open(full_path, 'wb')

        local_file.write(req.content)
        local_file.close()

        full_path = "/files/googlebusinessmessages-attachment/" + file_name + ".jpeg"

        return full_path
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error save_and_get_gmb_image_src %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
        return ""


"""
function is_image
input params:
file_name

this function is used to check wheter the given file is a image or not
"""


def is_image(file_name):

    is_image = False

    try:
        file_ext = file_name.split(".")[-1]

        if file_ext in ["png", "PNG", "JPG", "JPEG", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"]:
            is_image = True

        return is_image

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error is_image %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

    return is_image


def case_insensitive_key(dict, key_to_find):
    key_to_find = key_to_find.lower().strip()
    return [dict[key] for key in dict if key.lower().strip() == key_to_find]


def handle_gbm_survey_and_update_csat(conversation_id, survey_id, surveyQuestionId, questionResponsePostbackData, questionType, questionIndex, totalQuestionCount, bot_obj, channel_obj, Feedback, GBMCSATMapping, GBMSurveyQuestion):
    try:
        csat_mapping_obj = GBMCSATMapping.objects.filter(bot=bot_obj).first()
        questions = csat_mapping_obj.questions.all()
        response_score_mapper = {}
        if questionType == "GOOGLE_STANDARD_QUESTION":
            if questionResponsePostbackData.lower().strip() == "skip_survey":
                return
            if totalQuestionCount == 1:
                if questions.filter(question_id=surveyQuestionId).exists():
                    ques_obj = questions.filter(
                        question_id=surveyQuestionId).first()
                    response_score_mapper = ques_obj.response_score_mapper
                    response_score_mapper = json.loads(response_score_mapper)
                else:
                    # creating default obj in case its not present
                    ques_obj = GBMSurveyQuestion.objects.create(
                        question_id=surveyQuestionId)
                    response_score_mapper = {
                        "yes": 5,
                        "no": 1
                    }
                    ques_obj.response_score_mapper = json.dumps(
                        response_score_mapper)
                    ques_obj.save()
                    csat_mapping_obj.questions.add(ques_obj)
                    csat_mapping_obj.save()
                value = case_insensitive_key(
                    response_score_mapper, questionResponsePostbackData)
                # value is list containg the value for corresponding key if key doesnot exist it return empty list
                if value:
                    rating = int(value[0])
                    Feedback.objects.create(
                        user_id=conversation_id, bot=bot_obj, rating=rating, channel=channel_obj, scale_rating_5=bot_obj.scale_rating_5)

        elif questionType == "PARTNER_CUSTOM_QUESTION":
            if questionResponsePostbackData.lower().strip() == "skip_survey":
                return
            if questions.filter(question_id=surveyQuestionId).exists():
                ques_obj = questions.filter(
                    question_id=surveyQuestionId).first()
                response_score_mapper = ques_obj.response_score_mapper
                response_score_mapper = json.loads(response_score_mapper)
                value = case_insensitive_key(
                    response_score_mapper, questionResponsePostbackData)
                if value:
                    rating = int(value[0])
                    Feedback.objects.create(
                        user_id=conversation_id, bot=bot_obj, rating=rating, channel=channel_obj, scale_rating_5=bot_obj.scale_rating_5)
                else:
                    logger.error("Error handle_gbm_survey_and_update_csat  score mapper not found for " + str(questionResponsePostbackData), extra={
                                 'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

            else:
                logger.error("Error handle_gbm_survey_and_update_csat qustion not added or found for question id " + str(surveyQuestionId), extra={
                             'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Error handle_gbm_survey_and_update_csat %s at %s",
                     str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})


def gbm_text_formatting(message):
    try:
        logger.info("Inside gbm_html_tags_formatter", extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "1"})
        message = message.replace("&nbsp;", "\xa0")
        tags = {
            "*": "\*",
            "[": "\[",
            "]": "\]",
            "(": "\(",
            ")": "\)",
            "<em></em>": "",
            "<strong></strong>": "",
            "</p>": "</p>\n",
            "<b>": "**<b>",
            "</b>": "</b>**",
            "<strong>": "**",
            "</strong>": "**",
            "<i>": "*<i>",
            "</i>": "</i>*",
            "<em>": "*",
            "</em>": "*",
        }

        message = message.replace("<i>", "<em>")
        message = message.replace("</i>", "</em>")
        message = message.replace("<b>", "<strong>")
        message = message.replace("</b>", "</strong>")

        message = BeautifulSoup(message, "html.parser")
        child_soup = message.find_all(['em', 'strong'])
        for tag in child_soup:
            if tag.string == None and len(tag.text) == 0:
                tag.extract()
        
        message = str(message)

        message_list = message.split("</em>")
        if len(message_list) > 1:
            for index, msg in enumerate(message_list):
                if len(msg) - len(msg.rstrip()) > 0:
                    message_list[index] = msg.rstrip() + "</em>" + " " * (len(msg) - len(msg.rstrip()))
                elif index < len(message_list) - 1: 
                    message_list[index] = msg + "</em>"
            message = "".join(message_list)

        message_list = message.split("</strong>")
        if len(message_list) > 1:
            for index, msg in enumerate(message_list):
                if len(msg) - len(msg.rstrip()) > 0:
                    message_list[index] = msg.rstrip() + "</strong>" + " " * (len(msg) - len(msg.rstrip()))
                elif index < len(message_list) - 1: 
                    message_list[index] = msg + "</strong>"
            message = "".join(message_list)

        message_list = message.split("<em>")
        if len(message_list) > 1:
            for index, msg in enumerate(message_list):
                if len(msg) - len(msg.lstrip()) > 0:
                    message_list[index] = " " * (len(msg) - len(msg.lstrip())) + "<em>" + msg.lstrip()
                elif index > 0: 
                    message_list[index] = "<em>" + msg
            message = "".join(message_list)

        message_list = message.split("<strong>")
        if len(message_list) > 1:
            for index, msg in enumerate(message_list):
                if len(msg) - len(msg.lstrip()) > 0:
                    message_list[index] = " " * (len(msg) - len(msg.lstrip())) + "<strong>" + msg.lstrip()
                elif index > 0: 
                    message_list[index] = "<strong>" + msg
            message = "".join(message_list)

        for tag, replacement in tags.items():
            message = message.replace(tag, replacement)

        if "</a>" in message:
            message = message.replace("mailto:", "").replace("tel:", "")
            soup = BeautifulSoup(message, "html.parser")
            for link in soup.findAll('a'):
                href = link.get('href')
                link_name = link.text
                link_element = message[message.find("<a"):message.find("</a>")] + "</a>"
                logger.info("Inside gbm_html_tags_formatter Link Element", extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "1"})

                if link_name.replace("http://", "").replace("https://", "").strip() == href.replace("http://", "").replace("https://", "").strip():
                    message = message.replace(link_element, "[" + "Click here" + "](" + href + ")")
                else:
                    message = message.replace(link_element, "[" + link_name + "](" + href + ")")

        logger.info("Inside gbm_html_tags_formatter Final Output %s", str(message), extra={'AppName': 'EasyChat', 'user_id': "None", 'source': "None", 'channel': "None", 'bot_id': "1"})
    
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Failed to format html string format of gbm: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)

    return str(message)


def html_list_formatter(sent):
    try:
        logger.info("---Html list string found---", extra=log_param)
        ul_end_position = 0
        ol_end_position = 0
        if "<ul>" in sent:
            for itr in range(sent.count("<ul>")):
                ul_position = sent.find("<ul>", ul_end_position)
                ul_end_position = sent.find("</ul>", ul_position)
                list_str = sent[ul_position:ul_end_position]
                logger.info("HTML LIST STRING %s : %s", str(
                    itr + 1), str(list_str), extra=log_param)
                items = list_str.split("</li>")
                if len(items) > 1:
                    formatted_list_str = ""
                    for index, item in enumerate(items):
                        temp_item = item.strip()
                        temp_item = temp_item.replace(" ", "\xa0")
                        if item.strip() != "":
                            if index == 0:
                                formatted_list_str += "•" + temp_item
                            elif index < len(items) - 1:
                                formatted_list_str += "\n•" + temp_item
                    formatted_list_str += "\n"
                    sent = sent.replace(list_str, formatted_list_str)
                    sent = sent.strip()
                    logger.info("---Html list string formatted---",
                                extra=log_param)
        if "<ol>" in sent:
            for itr in range(sent.count("<ol>")):
                ol_position = sent.find("<ol>", ol_end_position)
                ol_end_position = sent.find("</ol>", ol_position)
                list_str = sent[ol_position:ol_end_position]
                logger.info("HTML LIST STRING %s : %s", str(
                    itr + 1), str(list_str), extra=log_param)
                items = list_str.split("</li>")
                if len(items) > 1:
                    formatted_list_str = ""
                    for index, item in enumerate(items[:-1]):
                        if item.strip() != "":
                            temp_item = str(index + 1) + "." + item.strip()
                            temp_item = temp_item.replace(" ", "\xa0")
                            if index == 0:
                                formatted_list_str += temp_item
                            elif index < len(items) - 1:
                                formatted_list_str += "\n" + temp_item
                    formatted_list_str += "\n"
                    sent = sent.replace(list_str, formatted_list_str)
                    sent = sent.strip()
                    logger.info("---Html list string formatted---",
                                extra=log_param)
    except Exception as E:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error("Failed to format gbm html list string: %s at %s",
                     str(E), str(exc_tb.tb_lineno), extra=log_param)
    return sent
